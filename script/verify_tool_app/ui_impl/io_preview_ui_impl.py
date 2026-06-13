"""
Preview controller — encapsulates the image preview dock and pixel inspection behavior.
"""

from collections.abc import Callable
import os

import numpy as np
from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QDockWidget, QGraphicsScene, QMainWindow, QMessageBox, QWidget

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

        self.input_yuv444 = None
        self.output_yuv444 = None
        self.input_qimage = None
        self.output_qimage = None
        self.mouse_pos = (0, 0)
        self.is_pixel_info_frozen = False

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
        self.ui.graphicsView_input.viewport().installEventFilter(self)
        self.ui.graphicsView_output.viewport().installEventFilter(self)

    def set_output_dir_getter(self, output_dir_getter: Callable[[], str] | None) -> None:
        """Update the output-directory provider used by save actions."""
        self._output_dir_getter = output_dir_getter or (lambda: os.getcwd())

    def set_input_image(self, yuv444: np.ndarray | None) -> None:
        """Replace the current input image and refresh the left preview."""
        self.input_yuv444 = None if yuv444 is None else np.array(yuv444, copy=True)
        self._update_input_preview()

    def set_output_image(self, yuv444: np.ndarray | None) -> None:
        """Replace the current output image and refresh the right preview."""
        self.output_yuv444 = None if yuv444 is None else np.array(yuv444, copy=True)
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
    def _yuv444_to_qimage(yuv_data: np.ndarray) -> QImage:
        """Convert channels-last YUV444 data to a displayable QImage."""
        height, width = yuv_data.shape[:2]
        y_data = yuv_data[..., 0].astype(np.float32)
        cb_data = yuv_data[..., 1].astype(np.float32) - 128.0
        cr_data = yuv_data[..., 2].astype(np.float32) - 128.0
        red = y_data + 1.5748 * cr_data
        green = y_data - 0.1873 * cb_data - 0.4681 * cr_data
        blue = y_data + 1.8556 * cb_data
        rgb = np.stack([red, green, blue], axis=-1)
        rgb = np.clip(rgb, 0, 255).astype(np.uint8)
        return QImage(rgb.data, width, height, 3 * width, QImage.Format_RGB888).copy()

    @staticmethod
    def _update_scene(scene: QGraphicsScene, view: object, qimage: QImage | None) -> None:
        """Replace the scene pixmap and fit it into the target view."""
        scene.clear()
        if qimage is None:
            return
        scene.addPixmap(QPixmap.fromImage(qimage))
        if scene.items():
            view.fitInView(scene.items()[0], Qt.KeepAspectRatio)

    def _update_input_preview(self) -> None:
        """Refresh the input preview scene from the current input image."""
        self.input_qimage = None
        self.ui.lineEdit_input_pixel.clear()
        self.ui.lineEdit_position.clear()
        if self.input_yuv444 is not None:
            self.input_qimage = self._yuv444_to_qimage(self.input_yuv444)
        self._update_scene(self.scene_input, self.ui.graphicsView_input, self.input_qimage)
        if self.input_qimage is None:
            self.ui.lineEdit_display_size.clear()
            return
        self.ui.lineEdit_display_size.setText(f"{self.input_qimage.width()}x{self.input_qimage.height()}")

    def _update_output_preview(self) -> None:
        """Refresh the output preview scene from the current output image."""
        self.output_qimage = None
        self.ui.lineEdit_output_pixel.clear()
        if self.output_yuv444 is not None:
            self.output_qimage = self._yuv444_to_qimage(self.output_yuv444)
        self._update_scene(self.scene_output, self.ui.graphicsView_output, self.output_qimage)

    def _map_view_pos_to_image(
        self,
        scene: QGraphicsScene,
        view: object,
        qimage: QImage | None,
        pos: object,
    ) -> tuple[int, int] | None:
        """Map a viewport position to image-space coordinates when possible."""
        if qimage is None:
            return None
        item = scene.itemAt(pos, view.transform())
        if item is None:
            return None
        scene_pos = view.mapToScene(pos)
        item_rect = item.boundingRect()
        if not item_rect.contains(scene_pos):
            return None
        x_pos = int(scene_pos.x() * qimage.width() / item_rect.width())
        y_pos = int(scene_pos.y() * qimage.height() / item_rect.height())
        if 0 <= x_pos < qimage.width() and 0 <= y_pos < qimage.height():
            return x_pos, y_pos
        return None

    def _on_mouse_move_input(self, pos: object) -> None:
        """Update the input pixel readout from the left preview viewport."""
        if self.input_yuv444 is None or self.is_pixel_info_frozen:
            return
        mapped_pos = self._map_view_pos_to_image(
            self.scene_input,
            self.ui.graphicsView_input,
            self.input_qimage,
            pos,
        )
        if mapped_pos is None:
            return
        x_pos, y_pos = mapped_pos
        self.mouse_pos = (x_pos, y_pos)
        self.ui.lineEdit_position.setText(f"({x_pos}, {y_pos})")
        y_val = self.input_yuv444[y_pos, x_pos, 0]
        cb_val = self.input_yuv444[y_pos, x_pos, 1]
        cr_val = self.input_yuv444[y_pos, x_pos, 2]
        self.ui.lineEdit_input_pixel.setText(f"Y={y_val}, Cb={cb_val}, Cr={cr_val}")

    def _on_mouse_move_output(self, pos: object) -> None:
        """Update the output pixel readout from the right preview viewport."""
        if self.output_yuv444 is None or self.is_pixel_info_frozen:
            return
        mapped_pos = self._map_view_pos_to_image(
            self.scene_output,
            self.ui.graphicsView_output,
            self.output_qimage,
            pos,
        )
        if mapped_pos is None:
            return
        x_pos, y_pos = mapped_pos
        y_val = self.output_yuv444[y_pos, x_pos, 0]
        cb_val = self.output_yuv444[y_pos, x_pos, 1]
        cr_val = self.output_yuv444[y_pos, x_pos, 2]
        self.ui.lineEdit_output_pixel.setText(f"Y={y_val}, Cb={cb_val}, Cr={cr_val}")

    def _on_preview_scale_changed(self, value: int) -> None:
        """Update the scale label for the preview area."""
        self.ui.label_scale_value.setText(f"{value}%")

    def _on_compare_mode_changed(self, index: int) -> None:
        """Handle compare-mode changes for later preview enhancements."""
        del index

    def _save_qimage(self, qimage: QImage | None, default_name: str) -> None:
        """Persist a QImage to the configured output directory."""
        if qimage is None:
            QMessageBox.warning(None, "Warning", f"No {default_name.split('_')[1].split('.')[0]} image to save")
            return
        output_dir = self._output_dir_getter() or os.getcwd()
        path = os.path.join(output_dir, default_name)
        qimage.save(path)
        self._status_callback(f"Saved: {path}")

    def _on_save_left_image(self) -> None:
        """Save the currently displayed left-side input image."""
        self._save_qimage(self.input_qimage, "acm_input.png")

    def _on_save_right_image(self) -> None:
        """Save the currently displayed right-side output image."""
        self._save_qimage(self.output_qimage, "acm_output.png")

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
