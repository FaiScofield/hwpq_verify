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

        self.input_frame: ImageFrame | None = None
        self.output_frame: ImageFrame | None = None
        self.input_cache_yuv444: np.ndarray | None = None  # cached stacked array for pixel inspection
        self.output_cache_yuv444: np.ndarray | None = None  # cached stacked array for pixel inspection
        self.input_cache_rgb444: np.ndarray | None = None  # cached stacked array for pixel inspection
        self.output_cache_rgb444: np.ndarray | None = None  # cached stacked array for pixel inspection
        self.input_rgb_from_yuv: np.ndarray | None = None
        self.output_rgb_from_yuv: np.ndarray | None = None
        self.input_qimage = None
        self.output_qimage = None
        self.mouse_pos = (0, 0)
        self.is_pixel_info_frozen = False
        self._preview_scale = 1.0
        self._input_pixmap_item = None
        self._output_pixmap_item = None

        self.scene_input = QGraphicsScene(self)
        self.scene_output = QGraphicsScene(self)
        self.ui.graphicsView_input.setScene(self.scene_input)
        self.ui.graphicsView_output.setScene(self.scene_output)

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

    def _connect_signals(self) -> None:
        """Wire preview widget signals and install viewport event filters."""
        self.ui.pushButton_save_left.clicked.connect(self._on_save_left_image)
        self.ui.pushButton_save_right.clicked.connect(self._on_save_right_image)
        self.ui.slider_preview_scale.valueChanged.connect(self._on_preview_scale_changed)
        if hasattr(self.ui, "comboBox_compare_mode"):
            self.ui.comboBox_compare_mode.currentIndexChanged.connect(self._on_compare_mode_changed)
        self.ui.graphicsView_input.setMouseTracking(True)
        self.ui.graphicsView_output.setMouseTracking(True)
        self.ui.graphicsView_input.viewport().setMouseTracking(True)
        self.ui.graphicsView_output.viewport().setMouseTracking(True)
        self.ui.graphicsView_input.viewport().installEventFilter(self)
        self.ui.graphicsView_output.viewport().installEventFilter(self)

    def set_output_dir_getter(self, output_dir_getter: Callable[[], str] | None) -> None:
        """Update the output-directory provider used by save actions."""
        self._output_dir_getter = output_dir_getter or (lambda: os.getcwd())

    def set_input_image(self, frame: ImageFrame | None) -> None:
        """Replace the current input image and refresh the left preview."""
        self.input_frame = frame
        self.input_cache_yuv444 = None
        self.input_cache_rgb444 = None
        self.input_rgb_from_yuv = None
        self._update_input_preview()

    def set_output_image(self, frame: ImageFrame | None) -> None:
        """Replace the current output image and refresh the right preview."""
        self.output_frame = frame
        self.output_cache_yuv444 = None
        self.output_cache_rgb444 = None
        self.output_rgb_from_yuv = None
        self._update_output_preview()

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

    @staticmethod
    def _yuv444_to_u8(yuv_data: np.ndarray) -> np.ndarray:
        """Ensure YUV444 ndarray is uint8 for QImage conversion."""
        if yuv_data.dtype == np.uint8:
            return yuv_data
        depth = 8 if yuv_data.dtype == np.uint8 else 10
        shift = max(0, depth - 8) # 2
        yuv_u8 = np.minimum((yuv_data + 2) >> shift, 255)
        return yuv_u8.astype(np.uint8)

    @staticmethod
    def _yuv444_to_qimage(yuv_data: np.ndarray, input_cs: int = 5) -> QImage:
        """Convert channels-last YUV444 data to a displayable QImage.

        Always renders as full-range RGB regardless of the source range.
        """
        yuv_data = PreviewUiController._yuv444_to_u8(yuv_data)
        height, width = yuv_data.shape[:2]
        y, u, v = yuv_data[..., 0], yuv_data[..., 1], yuv_data[..., 2]
        red, green, blue = yuv_to_rgb(y, u, v, input_cs=input_cs, output_cs=1)
        rgb = np.stack([red, green, blue], axis=-1)
        return QImage(rgb.data, width, height, 3 * width, QImage.Format_RGB888).copy()

    @staticmethod
    def _rgb444_to_qimage(rgb_data: np.ndarray) -> QImage:
        rgb_data = PreviewUiController._yuv444_to_u8(rgb_data)
        height, width = rgb_data.shape[:2]
        return QImage(rgb_data.data, width, height, 3 * width, QImage.Format_RGB888).copy()

    @staticmethod
    def _update_scene(scene: QGraphicsScene, qimage: QImage | None):
        """Replace the scene pixmap and return the new item (if any)."""
        scene.clear()
        if qimage is None:
            return None
        return scene.addPixmap(QPixmap.fromImage(qimage))

    def _apply_preview_scale(self) -> None:
        for view in (self.ui.graphicsView_input, self.ui.graphicsView_output):
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
        self.ui.lineEdit_display_size.setText(f"{disp_w}x{disp_h} ({src_w}x{src_h}x{scale:.2f})")

    def _update_input_preview(self) -> None:
        """Refresh the input preview scene from the current input image."""
        self.input_qimage = None
        self.ui.lineEdit_input_pixel.clear()
        self.ui.lineEdit_position.clear()
        if self.input_frame is not None:
            if self.input_frame.is_rgb:
                self.input_cache_rgb444 = np.stack([self.input_frame.pyr, self.input_frame.pug, self.input_frame.pvb], axis=-1)
                self.input_qimage = self._rgb444_to_qimage(self.input_cache_rgb444)
            else:
                self.input_cache_yuv444 = self.input_frame.as_yuv444_stacked()
                yuv_u8 = self._yuv444_to_u8(self.input_cache_yuv444)
                red, green, blue = yuv_to_rgb(
                    yuv_u8[..., 0], yuv_u8[..., 1], yuv_u8[..., 2],
                    input_cs=self.input_frame.clrspc,
                    output_cs=1,
                )
                self.input_rgb_from_yuv = np.stack([red, green, blue], axis=-1).astype(np.uint8)
                self.input_qimage = self._rgb444_to_qimage(self.input_rgb_from_yuv)
        else:
            self.input_cache_yuv444 = None
            self.input_cache_rgb444 = None
            self.input_rgb_from_yuv = None
        self._input_pixmap_item = self._update_scene(self.scene_input, self.input_qimage)
        self._apply_preview_scale()
        self._update_display_size_text()

    def _update_output_preview(self) -> None:
        """Refresh the output preview scene from the current output image."""
        self.output_qimage = None
        self.ui.lineEdit_output_pixel.clear()
        if self.output_frame is not None:
            if self.output_frame.is_rgb:
                self.output_cache_rgb444 = np.stack([self.output_frame.pyr, self.output_frame.pug, self.output_frame.pvb], axis=-1)
                self.output_qimage = self._rgb444_to_qimage(self.output_cache_rgb444)
            else:
                self.output_cache_yuv444 = self.output_frame.as_yuv444_stacked()
                yuv_u8 = self._yuv444_to_u8(self.output_cache_yuv444)
                red, green, blue = yuv_to_rgb(
                    yuv_u8[..., 0], yuv_u8[..., 1], yuv_u8[..., 2],
                    input_cs=self.output_frame.clrspc,
                    output_cs=1,
                )
                self.output_rgb_from_yuv = np.stack([red, green, blue], axis=-1).astype(np.uint8)
                self.output_qimage = self._rgb444_to_qimage(self.output_rgb_from_yuv)
        else:
            self.output_cache_yuv444 = None
            self.output_cache_rgb444 = None
            self.output_rgb_from_yuv = None
        self._output_pixmap_item = self._update_scene(self.scene_output, self.output_qimage)
        self._apply_preview_scale()

    def _map_view_pos_to_image(
        self,
        view: object,
        pixmap_item: object,
        qimage: QImage | None,
        pos: object,
    ) -> tuple[int, int] | None:
        """Map a viewport position to image-space coordinates when possible."""
        if qimage is None:
            return None
        if pixmap_item is None:
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

    def _on_mouse_move_input(self, pos: object) -> None:
        """Update the input pixel readout from the left preview viewport."""
        if self.is_pixel_info_frozen:
            return
        mapped_pos = self._map_view_pos_to_image(
            self.ui.graphicsView_input,
            self._input_pixmap_item,
            self.input_qimage,
            pos,
        )
        if mapped_pos is None:
            return
        x_pos, y_pos = mapped_pos
        self.mouse_pos = (x_pos, y_pos)
        self.ui.lineEdit_position.setText(f"({x_pos}, {y_pos})")
        if self.input_cache_rgb444 is not None:
            r_val = self.input_cache_rgb444[y_pos, x_pos, 0]
            g_val = self.input_cache_rgb444[y_pos, x_pos, 1]
            b_val = self.input_cache_rgb444[y_pos, x_pos, 2]
            self.ui.lineEdit_input_pixel.setText(f"R={r_val}, G={g_val}, B={b_val}")
        elif self.input_cache_yuv444 is not None and self.input_rgb_from_yuv is not None:
            y_val = self.input_cache_yuv444[y_pos, x_pos, 0]
            u_val = self.input_cache_yuv444[y_pos, x_pos, 1]
            v_val = self.input_cache_yuv444[y_pos, x_pos, 2]
            r_val = self.input_rgb_from_yuv[y_pos, x_pos, 0]
            g_val = self.input_rgb_from_yuv[y_pos, x_pos, 1]
            b_val = self.input_rgb_from_yuv[y_pos, x_pos, 2]
            self.ui.lineEdit_input_pixel.setText(f"YUV({y_val}, {u_val}, {v_val}) => RGB({r_val}, {g_val}, {b_val})")

    def _on_mouse_move_output(self, pos: object) -> None:
        """Update the output pixel readout from the right preview viewport."""
        if self.is_pixel_info_frozen:
            return
        mapped_pos = self._map_view_pos_to_image(
            self.ui.graphicsView_output,
            self._output_pixmap_item,
            self.output_qimage,
            pos,
        )
        if mapped_pos is None:
            return
        x_pos, y_pos = mapped_pos
        if self.output_cache_rgb444 is not None:
            r_val = self.output_cache_rgb444[y_pos, x_pos, 0]
            g_val = self.output_cache_rgb444[y_pos, x_pos, 1]
            b_val = self.output_cache_rgb444[y_pos, x_pos, 2]
            self.ui.lineEdit_output_pixel.setText(f"R={r_val}, G={g_val}, B={b_val}")
        elif self.output_cache_yuv444 is not None and self.output_rgb_from_yuv is not None:
            y_val = self.output_cache_yuv444[y_pos, x_pos, 0]
            u_val = self.output_cache_yuv444[y_pos, x_pos, 1]
            v_val = self.output_cache_yuv444[y_pos, x_pos, 2]
            r_val = self.output_rgb_from_yuv[y_pos, x_pos, 0]
            g_val = self.output_rgb_from_yuv[y_pos, x_pos, 1]
            b_val = self.output_rgb_from_yuv[y_pos, x_pos, 2]
            self.ui.lineEdit_output_pixel.setText(f"YUV({y_val}, {u_val}, {v_val}) => RGB({r_val}, {g_val}, {b_val})")

    def _on_preview_scale_changed(self, value: int) -> None:
        """Update the scale label for the preview area."""
        self.ui.label_scale_value.setText(f"{value}%")
        self._preview_scale = max(1, value) / 100.0
        self._apply_preview_scale()
        self._update_display_size_text()

    def _on_compare_mode_changed(self, index: int) -> None:
        """Handle compare-mode changes for later preview enhancements."""
        del index

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
        """Save the currently displayed left-side input image."""
        self._save_assets(self.input_frame, self.input_qimage, "acm_input")

    def _on_save_right_image(self) -> None:
        """Save the currently displayed right-side output image."""
        self._save_assets(self.output_frame, self.output_qimage, "acm_output")

    def eventFilter(self, obj: object, event: QEvent) -> bool:
        """Track mouse movement over the preview graphics views."""
        if event.type() == QEvent.MouseMove:
            input_viewport = self.ui.graphicsView_input.viewport()
            output_viewport = self.ui.graphicsView_output.viewport()
            if obj == input_viewport:
                self._on_mouse_move_input(event.pos())
            elif obj == output_viewport:
                self._on_mouse_move_output(event.pos())
        return super().eventFilter(obj, event)
