"""
Preview controller — encapsulates the image preview dock and pixel inspection behavior.
"""

from collections.abc import Callable
from dataclasses import dataclass
import os

import numpy as np
from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtGui import QColor, QImage, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import (
    QDockWidget,
    QFileDialog,
    QGraphicsPathItem,
    QGraphicsScene,
    QMainWindow,
    QMessageBox,
    QSizePolicy,
    QWidget,
)

from script.img_io import (
    ImageFrame, _csc_range_params, is_limited_range, yuv_to_rgb,
)

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
        self.ui.verticalLayout.setStretch(0, 0)
        self.ui.verticalLayout.setStretch(1, 0)
        self.ui.verticalLayout.setStretch(2, 0)
        self.ui.verticalLayout.setStretch(3, 1)
        self.ui.gridLayout_info.setColumnStretch(0, 0)
        self.ui.gridLayout_info.setColumnStretch(1, 2)
        self.ui.gridLayout_info.setColumnStretch(2, 0)
        self.ui.gridLayout_info.setColumnStretch(3, 2)
        # 第 4/5 列为空（无控件），不设拉伸，避免幽灵空列抢占右侧空间。
        self.ui.gridLayout_info.setColumnStretch(4, 0)
        self.ui.gridLayout_info.setColumnStretch(5, 0)


@dataclass
class PixelSelection:
    """Cache one valid preview pixel for freeze-state reuse and external sync."""

    source_view: str
    x_pos: int
    y_pos: int
    display_role: str


class PreviewUiController(QObject):
    """Controls the preview dock, scenes, pixel readout, and image export."""

    def __init__(
        self,
        preview_widget: PreviewUiWidget,
        parent_window: QMainWindow | None = None,
        output_dir_getter: Callable[[], str] | None = None,
        status_callback: Callable[[str], None] | None = None,
        pixel_selection_callback: Callable[[dict | None], None] | None = None,
        colorspace_getter: Callable[[], str] | None = None,
        pixel_readout_provider: Callable[[int, int, str], str] | None = None,
    ) -> None:
        """Bind to a PreviewUiWidget instance and mount it into a dock when possible."""
        super().__init__(parent_window or preview_widget)
        self._win = parent_window
        self.widget = preview_widget
        self.ui = preview_widget.ui
        self._output_dir_getter = output_dir_getter or (lambda: os.getcwd())
        self._status_callback = status_callback or (lambda message: None)
        self._pixel_selection_callback = pixel_selection_callback or (lambda selection: None)
        self._colorspace_getter = colorspace_getter or (lambda: "RGB(HSV)")
        self._pixel_readout_provider = pixel_readout_provider or (lambda x, y, role: "")
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
        self._last_pixel_selection: PixelSelection | None = None
        self._preview_scale = 1.0
        self._full_res_output_provider: Callable[[], ImageFrame | None] | None = None
        self._left_pixmap_item = None
        self._right_pixmap_item = None
        self._frozen_marker_item: QGraphicsPathItem | None = None

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
            self.preview_dock.setMinimumSize(360, 320)
            self._win.addDockWidget(Qt.BottomDockWidgetArea, self.preview_dock)
            self._win.resizeDocks([self.preview_dock], [400], Qt.Vertical)

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

    def set_full_res_output_provider(
        self, provider: Callable[[], ImageFrame | None] | None,
    ) -> None:
        """Set a provider returning a full-resolution output frame for saving.

        When the preview pass ran at a downsampled resolution, this provider
        recomputes the output at the source resolution so saved files stay
        exact.
        """
        self._full_res_output_provider = provider

    def get_work_size(self, src_w: int, src_h: int) -> tuple[int, int]:
        """Return the preview processing resolution: min(source, preview size).

        The preview display is ``source x preview_scale``; processing at this
        (or smaller) resolution keeps the preview responsive while staying
        pixel-identical whenever the source is no larger than the preview size.
        """
        scale = self._preview_scale
        if scale >= 1.0:
            return src_w, src_h
        return max(1, int(round(src_w * scale))), max(1, int(round(src_h * scale)))

    def set_pixel_selection_callback(
        self,
        pixel_selection_callback: Callable[[dict | None], None] | None,
    ) -> None:
        """Update the host callback used to sync frozen pixel selections."""
        self._pixel_selection_callback = pixel_selection_callback or (lambda selection: None)

    def set_input_image(self, frame: ImageFrame | None) -> None:
        """Replace the current input image and refresh."""
        self.input_frame = frame
        self.input_cache_yuv444 = None
        self.input_cache_rgb444 = None
        self.input_rgb_from_yuv = None
        self.input_qimage = None
        self.ui.lineEdit_input_pixel.clear()
        self.ui.lineEdit_position.clear()
        self._clear_pixel_selection(notify=True)
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
        if frame is not None:
            self.output_qimage = self._frame_to_qimage(frame, is_input=False)
        self._sync_preview_layout()
        self._restore_frozen_pixel_readout()

    def handle_key_press(self, event: QEvent) -> bool:
        """Toggle pixel-info freeze with the space key."""
        if event.key() != Qt.Key_Space:
            return False
        self.is_pixel_info_frozen = not self.is_pixel_info_frozen
        if self.is_pixel_info_frozen:
            if self._last_pixel_selection is not None:
                self._set_position_text(self._last_pixel_selection.x_pos, self._last_pixel_selection.y_pos)
            # 先用本地缓存填充（总是可用），再让 HSV 侧补充更丰富的格式。
            self._restore_frozen_pixel_readout()
            self._emit_pixel_selection()
        else:
            self._set_position_text(*self.mouse_pos)
            self._clear_pixel_selection(notify=True)
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
        if hasattr(self.ui, "radioButton_preview_bothInLeft"):
            self.ui.radioButton_preview_bothInLeft.toggled.connect(self._on_preview_type_toggled)
        if hasattr(self.ui, "radioButton_preview_sideBySide"):
            self.ui.radioButton_preview_sideBySide.toggled.connect(self._on_preview_type_toggled)
        if hasattr(self.ui, "checkBox_show_input"):
            self.ui.checkBox_show_input.toggled.connect(self._on_show_input_toggled)
        for view in (self.ui.graphicsView_left, self.ui.graphicsView_right):
            view.setMouseTracking(True)
            view.viewport().setMouseTracking(True)
            view.viewport().installEventFilter(self)

    # ------------------------------------------------------------------ #
    # Preview layout                                                     #
    # ------------------------------------------------------------------ #

    def _on_preview_type_toggled(self, checked: bool) -> None:
        """Update the preview layout when a preview-type radio is selected."""
        if not checked:
            return
        side_by_side = bool(getattr(self.ui, "radioButton_preview_sideBySide", None)
                             and self.ui.radioButton_preview_sideBySide.isChecked())
        self._preview_mode = "SideBySide" if side_by_side else "BothInLeft"
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
        self._update_frozen_marker()

    def _set_scene_image(self, scene, qimage, item_attr):
        """Replace a scene's pixmap and store the item reference."""
        scene.clear()
        # scene.clear() 会删除冻结像素 marker 的 C++ 对象，Python 引用立即失效。
        self._frozen_marker_item = None
        if qimage is None:
            setattr(self, item_attr, None)
            return
        item = scene.addPixmap(QPixmap.fromImage(qimage))
        setattr(self, item_attr, item)

    # ------------------------------------------------------------------ #
    # Image conversion helpers                                           #
    # ------------------------------------------------------------------ #

    def _frame_to_qimage(self, frame: ImageFrame, is_input: bool) -> QImage:
        """Convert an ImageFrame to a displayable QImage, caching ndarrays.

        预览恒转 full-range RGB：任何 limited RGB 帧（输入/输出）都展开 full。
        """
        if frame.is_rgb:
            if frame.clrspc == 0:
                # limited RGB（8bit [16,235] / 10bit [64,940]）：展开 full 再显示。
                max_val = (1 << frame.depth) - 1
                rp = _csc_range_params(frame.depth)
                lo = rp["yr_lo_l"]
                scale = max_val / (rp["yr_hi_l"] - lo)
                r = np.clip(np.rint((frame.pyr.astype(np.float32) - lo) * scale),
                            0, max_val).astype(frame.pyr.dtype)
                g = np.clip(np.rint((frame.pug.astype(np.float32) - lo) * scale),
                            0, max_val).astype(frame.pug.dtype)
                b = np.clip(np.rint((frame.pvb.astype(np.float32) - lo) * scale),
                            0, max_val).astype(frame.pvb.dtype)
                cache = np.stack([r, g, b], axis=-1)
            else:
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
        # QImage 需要 C-contiguous 缓冲（升采样/子采样路径可能产生非连续数组）。
        rgb_data = np.ascontiguousarray(rgb_data)
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

    def _clear_pixel_selection(self, notify: bool) -> None:
        """Reset the cached pixel selection and optionally clear external state."""
        self._last_pixel_selection = None
        self.is_pixel_info_frozen = False
        if notify:
            self._pixel_selection_callback(None)
        self._update_frozen_marker()

    def _emit_pixel_selection(self) -> None:
        """Forward the frozen pixel location to the host callback."""
        if self._last_pixel_selection is None:
            self._pixel_selection_callback(None)
            return
        self._pixel_selection_callback(
            {
                "source_view": self._last_pixel_selection.source_view,
                "x": self._last_pixel_selection.x_pos,
                "y": self._last_pixel_selection.y_pos,
                "display_role": self._last_pixel_selection.display_role,
                "frozen": self.is_pixel_info_frozen,
            }
        )
        self._update_frozen_marker()

    def _update_frozen_marker(self) -> None:
        """Draw a crosshair on the preview scene at the frozen pixel.

        The marker is black or white so it stays visible on any background:
        white when the pixel luma is dark (Y < 128), black when bright
        (Y >= 128).  It lives in scene coordinates (image pixel units); the
        view transform handles display scaling.  It is re-added whenever a
        scene is refreshed (``_set_scene_image`` clears the scene).
        """
        if self._frozen_marker_item is not None:
            try:
                scene = self._frozen_marker_item.scene()
            except RuntimeError:
                scene = None   # C++ 对象已被 scene.clear() 删除
            if scene is not None:
                scene.removeItem(self._frozen_marker_item)
            self._frozen_marker_item = None
        if not self.is_pixel_info_frozen or self._last_pixel_selection is None:
            return
        sel = self._last_pixel_selection
        if sel.source_view == "right" and self._right_pixmap_item is not None:
            item = self._right_pixmap_item
        else:
            item = self._left_pixmap_item
        try:
            if item is None or item.scene() is None:
                return
            luma = self._pixel_luma(sel)
            if luma is None:
                color = QColor(255, 0, 0)   # fallback when the pixel is unavailable
            else:
                color = QColor(255, 255, 255) if luma < 128 else QColor(0, 0, 0)
            half = 8
            path = QPainterPath()
            path.moveTo(sel.x_pos - half, sel.y_pos)
            path.lineTo(sel.x_pos + half, sel.y_pos)
            path.moveTo(sel.x_pos, sel.y_pos - half)
            path.lineTo(sel.x_pos, sel.y_pos + half)
            marker = QGraphicsPathItem(path)
            marker.setPen(QPen(color, 2))
            item.scene().addItem(marker)
            self._frozen_marker_item = marker
        except RuntimeError:
            # item 的 C++ 对象可能已被 scene 刷新删除；放弃本次绘制。
            self._frozen_marker_item = None

    def _pixel_luma(self, sel) -> int | None:
        """Return the luma (Y) of the frozen pixel as 8-bit 0..255.

        Uses the source Y plane when available (YUV frames, 10-bit converted
        to 8-bit), otherwise the BT.601 luma computed from the displayed RGB.
        """
        if sel.display_role == "output":
            yuv_cache = self.output_cache_yuv444
            rgb_cache = self.output_cache_rgb444
        else:
            yuv_cache = self.input_cache_yuv444
            rgb_cache = self.input_cache_rgb444
        try:
            if yuv_cache is not None:
                y = int(yuv_cache[sel.y_pos, sel.x_pos, 0])
                if yuv_cache.dtype != np.uint8:
                    y = min((y + 2) >> 2, 255)
                return y
            if rgb_cache is not None:
                r, g, b = rgb_cache[sel.y_pos, sel.x_pos]
                return int(0.299 * int(r) + 0.587 * int(g) + 0.114 * int(b) + 0.5)
        except (IndexError, TypeError):
            pass
        return None

    def _update_pixel_selection(
        self,
        source_view: str,
        x_pos: int,
        y_pos: int,
        display_role: str,
    ) -> None:
        """Cache the latest valid preview pixel for freeze-state reuse."""
        self._last_pixel_selection = PixelSelection(
            source_view=source_view,
            x_pos=x_pos,
            y_pos=y_pos,
            display_role=display_role,
        )
        self.mouse_pos = (x_pos, y_pos)
        self._set_position_text(x_pos, y_pos)

    def _set_position_text(self, x_pos: int, y_pos: int) -> None:
        """Render the current pixel position together with the freeze state."""
        state = "Frozen" if self.is_pixel_info_frozen else "Live"
        self.ui.lineEdit_position.setText(f"({x_pos}, {y_pos}) [{state}]")

    def set_colorspace_getter(self, getter: Callable[[], str] | None) -> None:
        """Set the callback returning the active colorspace text (compat no-op).

        读数已委托给 HSV 处理缓存，此处仅保留兼容入口。
        """
        self._colorspace_getter = getter or (lambda: "RGB(HSV)")

    def _fill_readout(self, x_pos: int, y_pos: int) -> None:
        """Fill both pixel readout fields from the HSV processing readout provider.

        读数显示步骤 1️⃣~6️⃣ 的处理结果（视 clip 选项钳位/未钳位，可超 [0,1]）。
        """
        self.ui.lineEdit_input_pixel.setText(
            self._pixel_readout_provider(x_pos, y_pos, "input"))
        self.ui.lineEdit_output_pixel.setText(
            self._pixel_readout_provider(x_pos, y_pos, "output"))

    def _restore_frozen_pixel_readout(self) -> None:
        """Re-fill pixel readout fields from current caches after a frame update."""
        if not self.is_pixel_info_frozen or self._last_pixel_selection is None:
            return
        x, y = self._last_pixel_selection.x_pos, self._last_pixel_selection.y_pos
        self._fill_readout(x, y)

    def _handle_view_leave(self) -> None:
        """Clear live pixel text when the cursor leaves a preview viewport."""
        if self.is_pixel_info_frozen:
            return
        self.ui.lineEdit_position.clear()
        self.ui.lineEdit_input_pixel.clear()
        self.ui.lineEdit_output_pixel.clear()
        self._last_pixel_selection = None

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
        mode = self._preview_mode
        show_input = bool(getattr(self.ui, "checkBox_show_input", None)
                         and self.ui.checkBox_show_input.isChecked())
        is_showing_output = (mode == "BothInLeft"
                             and self.output_frame is not None
                             and self._acm_enabled
                             and not show_input)
        mapped = self._map_view_pos_to_image(
            self.ui.graphicsView_left, self._left_pixmap_item, qimage, pos)
        if mapped is None:
            return
        x_pos, y_pos = mapped
        self._update_pixel_selection(
            source_view="left",
            x_pos=x_pos,
            y_pos=y_pos,
            display_role="output" if is_showing_output else "input",
        )

        # Always fill both input and output pixel readouts.
        self._fill_readout(x_pos, y_pos)

    def _on_mouse_move_right(self, pos) -> None:
        """Right preview pixel readout."""
        if self.is_pixel_info_frozen:
            return
        mapped = self._map_view_pos_to_image(
            self.ui.graphicsView_right, self._right_pixmap_item, self.output_qimage, pos)
        if mapped is None:
            return
        x_pos, y_pos = mapped
        self._update_pixel_selection(
            source_view="right",
            x_pos=x_pos,
            y_pos=y_pos,
            display_role="output",
        )
        # Always fill both input and output pixel readouts.
        self._fill_readout(x_pos, y_pos)

    def eventFilter(self, obj: object, event: QEvent) -> bool:
        if event.type() == QEvent.MouseMove:
            if obj == self.ui.graphicsView_left.viewport():
                self._on_mouse_move_left(event.pos())
            elif obj == self.ui.graphicsView_right.viewport():
                self._on_mouse_move_right(event.pos())
        elif event.type() == QEvent.Leave:
            if obj in (self.ui.graphicsView_left.viewport(), self.ui.graphicsView_right.viewport()):
                self._handle_view_leave()
        return super().eventFilter(obj, event)

    # ------------------------------------------------------------------ #
    # Save actions                                                       #
    # ------------------------------------------------------------------ #

    def _ask_save_target(self, default_name: str, frame: ImageFrame | None):
        """Open a save dialog; return (base_path, chosen_ext) or None.

        默认后缀按帧格式决定：YUV 系列为 .yuv、RGB 系列为 .rgb。
        chosen_ext 为用户选择的扩展名（小写）：.yuv/.rgb/.png/.jpg/.bmp，
        未输入扩展名时为 ""。base_path 为去掉扩展名后的路径。
        取消时返回 None。
        """
        raw_ext = ".yuv" if (frame is not None and frame.is_yuv) else ".rgb"
        output_dir = self._output_dir_getter() or os.getcwd()
        os.makedirs(output_dir, exist_ok=True)
        suggested = os.path.join(output_dir, f"{default_name}{raw_ext}")
        path, _ = QFileDialog.getSaveFileName(
            self._win, "Save Image", suggested,
            "Raw (*.yuv *.rgb);;PNG (*.png);;JPEG (*.jpg);;BMP (*.bmp);;All files (*)")
        if not path:
            return None
        lower = path.lower()
        chosen = ""
        for ext in (".yuv", ".rgb", ".png", ".jpg", ".jpeg", ".bmp"):
            if lower.endswith(ext):
                chosen = ".jpg" if ext == ".jpeg" else ext
                path = path[:-len(ext)]
                break
        return path, chosen

    def _save_assets(
        self, frame: ImageFrame | None, qimage: QImage | None, base_path: str,
        chosen_ext: str = "", apply_output_f2l: bool = False,
    ) -> None:
        """Save a frame as raw data or as an image.

        ``base_path``: full output path without extension.
        ``chosen_ext``: 用户选择的扩展名（小写）。为 .png/.jpg/.bmp 时仅保存
        显示图像到 ``<base_path><chosen_ext>``；为 .yuv/.rgb 或未输扩展名时
        按帧格式保存 raw 数据到 ``<base_path>_0x{fmt}<raw_ext>``
        （YUV 系列 .yuv / RGB 系列 .rgb），不再附带 PNG 预览。

        ``apply_output_f2l``: when True the frame carries full-range RGB data
        (HSV pipeline output) while its target colorspace is limited — the raw
        data is converted full->limited before writing so the saved file
        matches the colorspace.
        """
        if frame is None:
            QMessageBox.warning(None, "Warning", "No image data to save")
            return
        out_dir = os.path.dirname(base_path) or os.getcwd()
        os.makedirs(out_dir, exist_ok=True)

        # 仅保存图像（png/jpg/bmp）：用显示图，不做 raw 导出。
        if chosen_ext in (".png", ".jpg", ".bmp"):
            if qimage is None:
                QMessageBox.warning(None, "Warning", "No image data to save")
                return
            img_path = f"{base_path}{chosen_ext}"
            if not qimage.save(img_path):
                QMessageBox.warning(None, "Warning", f"Failed to save image: {img_path}")
                self._status_callback(f"Save failed: {img_path}")
                return
            self._status_callback(f"Saved: {img_path}")
            return

        # raw 导出：后缀按帧格式（YUV=.yuv / RGB=.rgb），不附带 PNG 预览。
        raw_ext = ".yuv" if frame.is_yuv else ".rgb"
        raw_path = f"{base_path}_0x{frame.fmt:x}{raw_ext}"
        frame = frame.copy()
        if apply_output_f2l and frame.is_rgb and is_limited_range(frame.clrspc):
            # full -> limited RGB（8bit [16,235] / 10bit [64,940]）。
            max_val = (1 << frame.depth) - 1
            rp = _csc_range_params(frame.depth)
            lo = rp["yr_lo_l"]
            scale = (rp["yr_hi_l"] - lo) / max_val
            r = np.clip(np.rint(frame.pyr.astype(np.float32) * scale + lo),
                        0, max_val).astype(frame.pyr.dtype)
            g = np.clip(np.rint(frame.pug.astype(np.float32) * scale + lo),
                        0, max_val).astype(frame.pug.dtype)
            b = np.clip(np.rint(frame.pvb.astype(np.float32) * scale + lo),
                        0, max_val).astype(frame.pvb.dtype)
            frame = ImageFrame(r, g, b, frame.fmt, frame.clrspc)
        frame.to_file(raw_path)
        self._status_callback(f"Saved: {raw_path}")

    def _get_output_for_save(self) -> ImageFrame | None:
        """Return the output frame to save.

        Uses the full-resolution provider when available (recomputes at source
        resolution if the preview pass was downsampled), falling back to the
        cached preview output frame.
        """
        if self._full_res_output_provider is not None:
            full = self._full_res_output_provider()
            if full is not None:
                return full
        return self.output_frame

    def _save_output_image(self, base_path: str, chosen_ext: str = "") -> None:
        """Save the output as raw (or image-only) at full resolution when possible.

        输出帧（步骤 6️⃣）已按所选输出 format/cs 正确编码，无需再做 f2l；
        预览 QImage 转换使用副本，避免 as_yuv444_stacked 原地升采样破坏原始数据。
        """
        frame = self._get_output_for_save()
        qimage = self.output_qimage
        if frame is not None and frame is not self.output_frame:
            qimage = self._frame_to_qimage(frame.copy(), is_input=False)
        self._save_assets(frame, qimage, base_path, chosen_ext)

    def _on_save_left_image(self) -> None:
        mode = self._preview_mode
        if mode == "BothInLeft" and self.output_frame is not None and self._acm_enabled:
            show_input = bool(getattr(self.ui, "checkBox_show_input", None)
                              and self.ui.checkBox_show_input.isChecked())
            if not show_input:
                target = self._ask_save_target("output_img", self._get_output_for_save())
                if target is not None:
                    self._save_output_image(*target)
                return
        target = self._ask_save_target("input_img", self.input_frame)
        if target is not None:
            self._save_assets(self.input_frame, self.input_qimage, *target)

    def _on_save_right_image(self) -> None:
        target = self._ask_save_target("output_img", self._get_output_for_save())
        if target is not None:
            self._save_output_image(*target)
