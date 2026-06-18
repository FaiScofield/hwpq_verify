"""
Preview controller — encapsulates the image preview dock and pixel inspection behavior.
"""

from collections.abc import Callable
import os

import numpy as np
from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QDockWidget, QGraphicsScene, QMainWindow, QMessageBox, QWidget

from script.img_io import ImageFrame, yuv_to_rgb

try:
    from ..ui_gen.io_preview_ui import Ui_PreviewUiWidget
except ImportError:
    from ui_gen.io_preview_ui import Ui_PreviewUiWidget


class PreviewUiWidget(QWidget):
    """Reusable preview widget content for a host dock."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create the preview widget from the generated UI definition."""
        super().__init__(parent)
        self.ui = Ui_PreviewUiWidget()
        self.ui.setupUi(self)


class PreviewUiController(QObject):
    """Controls the preview dock, scenes, pixel readout, and image export."""

    def __init__(
        self,
        preview_widget: PreviewUiWidget,
        parent_window: QMainWindow | None = None,
        output_dir_getter: Callable[[], str] | None = None,
        status_callback: Callable[[str], None] | None = None,
    ) -> None:
        """Bind to a PreviewUiWidget instance and mount it into a dock when possible."""
        super().__init__(parent_window or preview_widget)
        self._win = parent_window
        self.widget = preview_widget
        self.ui = preview_widget.ui
        self._output_dir_getter = output_dir_getter or (lambda: os.getcwd())
        self._status_callback = status_callback or (lambda message: None)
        self._acm_enabled: bool = True
        self._preview_mode: str = "BothInLeft"  # or "SideBySide"

        self.input_frame: ImageFrame | None = None
        self.output_frame: ImageFrame | None = None
        self.input_cache_yuv444: np.ndarray | None = None
        self.output_cache_yuv444: np.ndarray | None = None
        self.input_cache_rgb444: np.ndarray | None = None
        self.output_cache_rgb444: np.ndarray | None = None
        self.input_rgb_from_yuv: np.ndarray | None = None
        self.output_rgb_from_yuv: np.ndarray | None = None
        self.input_qimage: QImage | None = None
        self.output_qimage: QImage | None = None
        self.mouse_pos = (0, 0)
        self.is_pixel_info_frozen = False
        self._preview_scale = 1.0
        self._left_pixmap_item = None
        self._right_pixmap_item = None

        self.scene_left = QGraphicsScene(self)
        self.scene_right = QGraphicsScene(self)
        self.ui.graphicsView_left.setScene(self.scene_left)
        self.ui.graphicsView_right.setScene(self.scene_right)

        self.preview_dock = None
        if self._win is not None:
            self.preview_dock = QDockWidget("Image Preview", self._win)
            self.preview_dock.setObjectName("preview_dock")
            self.preview_dock.setAllowedAreas(Qt.AllDockWidgetAreas)
            self.preview_dock.setFeatures(
                QDockWidget.DockWidgetMovable
                | QDockWidget.DockWidgetFloatable
                | QDockWidget.DockWidgetClosable
            )
            self.preview_dock.setWidget(self.widget)
            self._win.addDockWidget(Qt.BottomDockWidgetArea, self.preview_dock)

        self._connect_signals()
        self._on_preview_scale_changed(self.ui.slider_preview_scale.value())
        self._sync_preview_layout()

    # ------------------------------------------------------------------ #
    # Public interface                                                   #
    # ------------------------------------------------------------------ #

    def set_acm_enabled(self, enabled: bool) -> None:
        """Notify whether ACM processing is active (affects BothInLeft)."""
        if self._acm_enabled != enabled:
            self._acm_enabled = enabled
            self._sync_preview_layout()

    def set_output_dir_getter(self, output_dir_getter: Callable[[], str] | None) -> None:
        """Update the output-directory provider used by save actions."""
        self._output_dir_getter = output_dir_getter or (lambda: os.getcwd())

    def set_input_image(self, frame: ImageFrame | None) -> None:
        """Replace the current input image and refresh."""
        self.input_frame = frame
        self.input_cache_yuv444 = None
        self.input_cache_rgb444 = None
        self.input_rgb_from_yuv = None
        self.input_qimage = None
        self.ui.lineEdit_input_pixel.clear()
        self.ui.lineEdit_position.clear()
        if frame is not None:
            self.input_qimage = self._frame_to_qimage(frame, is_input=True)
        self._sync_preview_layout()
        self._update_display_size_text()

    def set_output_image(self, frame: ImageFrame | None) -> None:
        """Replace the current output image and refresh."""
        self.output_frame = frame
        self.output_cache_yuv444 = None
        self.output_cache_rgb444 = None
        self.output_rgb_from_yuv = None
        self.output_qimage = None
        self.ui.lineEdit_output_pixel.clear()
        if frame is not None:
            self.output_qimage = self._frame_to_qimage(frame, is_input=False)
        self._sync_preview_layout()

    def set_time_cost_ms(self, elapsed_ms: float | None) -> None:
        """Update the displayed processing time."""
        if elapsed_ms is None:
            self.ui.lineEdit_time_cost.clear()
            return
        self.ui.lineEdit_time_cost.setText(f"{elapsed_ms:.2f} ms")

    def handle_key_press(self, event: QEvent) -> bool:
        """Toggle pixel-info freeze with the space key."""
        if event.key() != Qt.Key_Space:
            return False
        self.is_pixel_info_frozen = not self.is_pixel_info_frozen
        status = "Frozen" if self.is_pixel_info_frozen else "Live"
        self._status_callback(f"Pixel info: {status}")
        return True

    # ------------------------------------------------------------------ #
    # Signal wiring                                                      #
    # ------------------------------------------------------------------ #

    def _connect_signals(self) -> None:
        self.ui.pushButton_save_left.clicked.connect(self._on_save_left_image)
        self.ui.pushButton_save_right.clicked.connect(self._on_save_right_image)
        self.ui.slider_preview_scale.valueChanged.connect(self._on_preview_scale_changed)
        if hasattr(self.ui, "comboBox_compare_mode"):
            self.ui.comboBox_compare_mode.currentIndexChanged.connect(self._on_compare_mode_changed)
        if hasattr(self.ui, "comboBox_preview_type"):
            self.ui.comboBox_preview_type.currentTextChanged.connect(self._on_preview_type_changed)
        if hasattr(self.ui, "checkBox_show_input"):
            self.ui.checkBox_show_input.toggled.connect(self._on_show_input_toggled)
        for view in (self.ui.graphicsView_left, self.ui.graphicsView_right):
            view.setMouseTracking(True)
            view.viewport().setMouseTracking(True)
            view.viewport().installEventFilter(self)

    # ------------------------------------------------------------------ #
    # Preview layout                                                     #
    # ------------------------------------------------------------------ #

    def _on_preview_type_changed(self, text: str) -> None:
        self._preview_mode = text
        self._sync_preview_layout()

    def _on_show_input_toggled(self, checked: bool) -> None:
        del checked
        self._sync_preview_layout()

    def _sync_preview_layout(self) -> None:
        """Route input / output QImages to left / right scenes."""
        mode = getattr(self, "_preview_mode", "BothInLeft")

        if mode == "SideBySide":
            self.ui.groupBox_right_preview.setVisible(True)
            self._set_scene_image(self.scene_left, self.input_qimage, "_left_pixmap_item")
            self._set_scene_image(self.scene_right, self.output_qimage, "_right_pixmap_item")
        else:  # BothInLeft
            self.ui.groupBox_right_preview.setVisible(False)
            show_input = bool(getattr(self.ui, "checkBox_show_input", None)
                              and self.ui.checkBox_show_input.isChecked())
            has_output = (self.output_frame is not None and self._acm_enabled)
            has_input = (self.input_frame is not None)

            if has_output and not show_input:
                self._set_scene_image(self.scene_left, self.output_qimage, "_left_pixmap_item")
            elif has_input:
                self._set_scene_image(self.scene_left, self.input_qimage, "_left_pixmap_item")
            else:
                self._set_scene_image(self.scene_left, None, "_left_pixmap_item")
            self._set_scene_image(self.scene_right, None, "_right_pixmap_item")

        self._apply_preview_scale()

    def _set_scene_image(self, scene, qimage, item_attr):
        """Replace a scene's pixmap and store the item reference."""
        scene.clear()
        if qimage is None:
            setattr(self, item_attr, None)
            return
        item = scene.addPixmap(QPixmap.fromImage(qimage))
        setattr(self, item_attr, item)

    # ------------------------------------------------------------------ #
    # Image conversion helpers                                           #
    # ------------------------------------------------------------------ #

    def _frame_to_qimage(self, frame: ImageFrame, is_input: bool) -> QImage:
        """Convert an ImageFrame to a displayable QImage, caching ndarrays."""
        if frame.is_rgb:
            cache = np.stack([frame.pyr, frame.pug, frame.pvb], axis=-1)
            if is_input:
                self.input_cache_rgb444 = cache
            else:
                self.output_cache_rgb444 = cache
            return self._rgb444_to_qimage(cache)
        else:
            cache = frame.as_yuv444_stacked()
            if is_input:
                self.input_cache_yuv444 = cache
            else:
                self.output_cache_yuv444 = cache
            yuv_u8 = self._yuv444_to_u8(cache)
            red, green, blue = yuv_to_rgb(
                yuv_u8[..., 0], yuv_u8[..., 1], yuv_u8[..., 2],
                input_cs=frame.clrspc,
                output_cs=1,
            )
            rgb = np.stack([red, green, blue], axis=-1).astype(np.uint8)
            if is_input:
                self.input_rgb_from_yuv = rgb
            else:
                self.output_rgb_from_yuv = rgb
            return self._rgb444_to_qimage(rgb)

    @staticmethod
    def _yuv444_to_u8(yuv_data: np.ndarray) -> np.ndarray:
        if yuv_data.dtype == np.uint8:
            return yuv_data
        shift = 2
        return np.minimum((yuv_data + 2) >> shift, 255).astype(np.uint8)

    @staticmethod
    def _rgb444_to_qimage(rgb_data: np.ndarray) -> QImage:
        rgb_data = PreviewUiController._yuv444_to_u8(rgb_data)
        height, width = rgb_data.shape[:2]
        return QImage(rgb_data.data, width, height, 3 * width, QImage.Format_RGB888).copy()

    # ------------------------------------------------------------------ #
    # Scale / size                                                       #
    # ------------------------------------------------------------------ #

    def _apply_preview_scale(self) -> None:
        for view in (self.ui.graphicsView_left, self.ui.graphicsView_right):
            view.resetTransform()
            view.scale(self._preview_scale, self._preview_scale)

    def _update_display_size_text(self) -> None:
        if self.input_qimage is None:
            self.ui.lineEdit_display_size.clear()
            return
        src_w = self.input_qimage.width()
        src_h = self.input_qimage.height()
        scale = self._preview_scale
        disp_w = max(1, int(round(src_w * scale)))
        disp_h = max(1, int(round(src_h * scale)))
        self.ui.lineEdit_display_size.setText(f"{disp_w}x{disp_h} ({src_w}x{src_h}x{scale*100:.0f}%)")

    def _on_preview_scale_changed(self, value: int) -> None:
        self.ui.label_scale_value.setText(f"{value}%")
        self._preview_scale = max(1, value) / 100.0
        self._apply_preview_scale()
        self._update_display_size_text()

    def _on_compare_mode_changed(self, index: int) -> None:
        del index

    # ------------------------------------------------------------------ #
    # Mouse tracking / pixel inspection                                  #
    # ------------------------------------------------------------------ #

    def _map_view_pos_to_image(self, view, pixmap_item, qimage, pos):
        if qimage is None or pixmap_item is None:
            return None
        scene_pos = view.mapToScene(pos)
        item_pos = pixmap_item.mapFromScene(scene_pos)
        item_rect = pixmap_item.boundingRect()
        if not item_rect.contains(item_pos):
            return None
        x_pos = int(item_pos.x() * qimage.width() / item_rect.width())
        y_pos = int(item_pos.y() * qimage.height() / item_rect.height())
        if 0 <= x_pos < qimage.width() and 0 <= y_pos < qimage.height():
            return x_pos, y_pos
        return None

    def _on_mouse_move_left(self, pos) -> None:
        """Left preview pixel readout — which image depends on mode."""
        if self.is_pixel_info_frozen:
            return
        qimage = self.scene_left.items()[0].pixmap().toImage() if self.scene_left.items() else None
        if qimage is None or qimage.isNull():
            qimage = self.input_qimage or self.output_qimage
        mapped = self._map_view_pos_to_image(
            self.ui.graphicsView_left, self._left_pixmap_item, qimage, pos)
        if mapped is None:
            return
        x_pos, y_pos = mapped
        self.mouse_pos = (x_pos, y_pos)
        self.ui.lineEdit_position.setText(f"({x_pos}, {y_pos})")

        # Determine which cache to read based on what the left scene shows
        mode = self._preview_mode
        show_input = bool(getattr(self.ui, "checkBox_show_input", None)
                          and self.ui.checkBox_show_input.isChecked())
        is_showing_output = (mode == "BothInLeft"
                             and self.output_frame is not None
                             and self._acm_enabled
                             and not show_input)

        if is_showing_output:
            if self.output_cache_rgb444 is not None:
                r, g, b = self.output_cache_rgb444[y_pos, x_pos]
                self.ui.lineEdit_input_pixel.setText(f"R={r}, G={g}, B={b}")
            elif self.output_cache_yuv444 is not None and self.output_rgb_from_yuv is not None:
                yv, uv, vv = self.output_cache_yuv444[y_pos, x_pos]
                r, g, b = self.output_rgb_from_yuv[y_pos, x_pos]
                self.ui.lineEdit_input_pixel.setText(f"YUV({yv}, {uv}, {vv}) => RGB({r}, {g}, {b})")
        else:
            if self.input_cache_rgb444 is not None:
                r, g, b = self.input_cache_rgb444[y_pos, x_pos]
                self.ui.lineEdit_input_pixel.setText(f"R={r}, G={g}, B={b}")
            elif self.input_cache_yuv444 is not None and self.input_rgb_from_yuv is not None:
                yv, uv, vv = self.input_cache_yuv444[y_pos, x_pos]
                r, g, b = self.input_rgb_from_yuv[y_pos, x_pos]
                self.ui.lineEdit_input_pixel.setText(f"YUV({yv}, {uv}, {vv}) => RGB({r}, {g}, {b})")

    def _on_mouse_move_right(self, pos) -> None:
        """Right preview pixel readout."""
        if self.is_pixel_info_frozen:
            return
        mapped = self._map_view_pos_to_image(
            self.ui.graphicsView_right, self._right_pixmap_item, self.output_qimage, pos)
        if mapped is None:
            return
        x_pos, y_pos = mapped
        if self.output_cache_rgb444 is not None:
            r, g, b = self.output_cache_rgb444[y_pos, x_pos]
            self.ui.lineEdit_output_pixel.setText(f"R={r}, G={g}, B={b}")
        elif self.output_cache_yuv444 is not None and self.output_rgb_from_yuv is not None:
            yv, uv, vv = self.output_cache_yuv444[y_pos, x_pos]
            r, g, b = self.output_rgb_from_yuv[y_pos, x_pos]
            self.ui.lineEdit_output_pixel.setText(f"YUV({yv}, {uv}, {vv}) => RGB({r}, {g}, {b})")

    def eventFilter(self, obj: object, event: QEvent) -> bool:
        if event.type() == QEvent.MouseMove:
            if obj == self.ui.graphicsView_left.viewport():
                self._on_mouse_move_left(event.pos())
            elif obj == self.ui.graphicsView_right.viewport():
                self._on_mouse_move_right(event.pos())
        return super().eventFilter(obj, event)

    # ------------------------------------------------------------------ #
    # Save actions                                                       #
    # ------------------------------------------------------------------ #

    def _save_assets(self, frame: ImageFrame | None, qimage: QImage | None, base_name: str) -> None:
        if frame is None:
            QMessageBox.warning(None, "Warning", "No image data to save")
            return
        output_dir = self._output_dir_getter() or os.getcwd()
        os.makedirs(output_dir, exist_ok=True)
        raw_path = os.path.join(output_dir, f"{base_name}_0x{frame.fmt:x}.yuv")
        frame.copy().to_file(raw_path)
        if qimage is not None:
            png_path = os.path.join(output_dir, f"{base_name}.png")
            if not qimage.save(png_path):
                QMessageBox.warning(None, "Warning", f"Failed to save image: {png_path}")
                self._status_callback(f"Save failed: {png_path}")
                return
            self._status_callback(f"Saved: {raw_path}, {png_path}")
            return
        self._status_callback(f"Saved: {raw_path}")

    def _on_save_left_image(self) -> None:
        mode = self._preview_mode
        if mode == "BothInLeft" and self.output_frame is not None and self._acm_enabled:
            show_input = bool(getattr(self.ui, "checkBox_show_input", None)
                              and self.ui.checkBox_show_input.isChecked())
            if not show_input:
                self._save_assets(self.output_frame, self.output_qimage, "acm_output")
                return
        self._save_assets(self.input_frame, self.input_qimage, "acm_input")

    def _on_save_right_image(self) -> None:
        self._save_assets(self.output_frame, self.output_qimage, "acm_output")
