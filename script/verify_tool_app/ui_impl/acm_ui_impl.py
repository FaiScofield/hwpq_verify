"""
ACM tab controller — encapsulates all ACM-related UI behavior and state.
"""

from collections.abc import Callable
import os
import time

import numpy as np
from PySide6.QtCore import QRect, QTimer, Qt, Signal
from PySide6.QtGui import QColor, QGuiApplication, QImage, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

try:
    from ..ui_gen.acm_ui import Ui_AcmUiWidget
except ImportError:
    from ui_gen.acm_ui import Ui_AcmUiWidget

try:
    from ...script.acm import cordic
except ImportError:
    from script.acm import cordic

try:
    from ...script.acm.acm_impl_base import (
        DELTA_Y_MIN, DELTA_Y_MAX,
        DELTA_S_MIN, DELTA_S_MAX,
        DELTA_H_MIN, DELTA_H_MAX,
        GAIN_MIN, GAIN_MAX,
    )
except ImportError:
    from script.acm.acm_impl_base import (
        ACM_DELTA_Y_MIN, ACM_DELTA_Y_MAX,
        ACM_DELTA_S_MIN, ACM_DELTA_S_MAX,
        ACM_DELTA_H_MIN, ACM_DELTA_H_MAX,
        ACM_GAIN_MIN, ACM_GAIN_MAX,
    )

try:
    from ...script.img_io import ImageFrame, _PLANAR_YUV_8, rgb_to_yuv, yuv_to_rgb
except ImportError:
    from script.img_io import ImageFrame, _PLANAR_YUV_8, rgb_to_yuv, yuv_to_rgb


class AcmUiWidget(QWidget):
    """Reusable ACM configuration widget."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create the ACM widget from the generated UI definition."""
        super().__init__(parent)
        self.ui = Ui_AcmUiWidget()
        self.ui.setupUi(self)


class LutImageWindow(QWidget):
    """Standalone non-modal window for displaying the LUT overview image."""

    def __init__(self, on_close: Callable[[], None], parent: QWidget | None = None) -> None:
        """Create a top-level window with a stretch-filled image label."""
        super().__init__(parent, Qt.Window)
        self._on_close = on_close
        self.setWindowTitle("LUT Visualization")
        self.resize(960, 540)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(100, 80)
        self.image_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.image_label.setScaledContents(True)
        self.image_label.setText("No LUT")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.image_label)

    def closeEvent(self, event: object) -> None:
        """Notify the controller when the window is manually closed."""
        if self._on_close is not None:
            self._on_close()
        super().closeEvent(event)


class SingleCurveChartWidget(QWidget):
    """Interactive single-curve chart for one H-based delta LUT.

    The widget always owns ``values`` whose length equals ``len_h`` (one entry
    per integer H index). On top of that it overlays a smaller set of
    ``sample_points`` (positions and values) that act as editable control
    points; moving a sample point triggers re-interpolation of the underlying
    integer-indexed values between neighbouring sample points.
    """

    dataChanged = Signal(int, list)
    samplePointChanged = Signal(int, list)

    def __init__(
        self,
        value_range: tuple[int, int],
        curve_color: QColor,
        parent: QWidget | None = None,
        bg_image_path: str = "",
    ) -> None:
        """Create a chart widget with a configurable value range and color.

        Args:
            bg_image_path: optional background image (BMP) painted before data.
        """
        super().__init__(parent)
        self.setMinimumSize(600, 400)
        self.setMaximumSize(1200, 800)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.value_range = value_range
        self.curve_color = curve_color
        self.values: list[int] = [0]
        self.padding = 40
        self.sample_positions: list[float] = []
        self.sample_values: list[float] = []
        self.dragging_sample: int | None = None
        self.selected_sample: int | None = None
        self.hover_sample: int | None = None
        self.reference_h_index: float | None = None
        self.reference_h_index_out: float | None = None
        self.input_value: float | None = None
        self.output_value: float | None = None
        self._bg_pixmap: QPixmap | None = None
        if bg_image_path and os.path.isfile(bg_image_path):
            self._bg_pixmap = QPixmap(bg_image_path)

    def set_num_points(self, count: int) -> None:
        """No-op kept for API compatibility.

        ``values`` length is now driven by the controller via :meth:`set_values`
        and is always equal to ``len_h``. The argument is ignored.
        """
        del count

    def set_values(self, values: list[int] | np.ndarray) -> None:
        """Replace the underlying integer-indexed LUT values and repaint."""
        self.values = [int(v) for v in values]
        self.update()

    def get_values(self) -> list[int]:
        """Return the integer-indexed LUT values."""
        return list(self.values)

    def set_sample_points(
        self,
        positions: list[float] | np.ndarray,
        values: list[float] | np.ndarray,
    ) -> None:
        """Update the sample-point overlay (positions and values)."""
        self.sample_positions = [float(p) for p in positions]
        self.sample_values = [float(v) for v in values]
        if self.selected_sample is not None and self.selected_sample >= len(self.sample_positions):
            self.selected_sample = None
        if self.dragging_sample is not None and self.dragging_sample >= len(self.sample_positions):
            self.dragging_sample = None
        self.update()

    def set_selected_sample(self, index: int | None) -> None:
        """Mark a sample point as selected (changes its render color)."""
        self.selected_sample = index
        self.update()

    def set_reference_h_index(self, h_index: float | None) -> None:
        """Update the input H-axis reference marker (backward compat)."""
        self.set_h_markers(h_index, None, None, None)

    def set_h_markers(
        self,
        h_index_in: float | None,
        h_index_out: float | None,
        input_value: float | None,
        output_value: float | None,
    ) -> None:
        """Set H-axis reference markers and input/output value markers.

        Args:
            h_index_in:  input H index  → black dashed line + black × marker.
            h_index_out: output H index → white dashed line + white × marker.
            input_value:  chart-space Y value for the input marker (black ×).
            output_value: chart-space Y value for the output marker (white ×).
        """
        self.reference_h_index = h_index_in
        self.reference_h_index_out = h_index_out
        self.input_value = input_value
        self.output_value = output_value
        self.update()

    def _value_to_y(self, value: int | float) -> float:
        """Map a chart value to widget coordinates."""
        value_min, value_max = self.value_range
        chart_height = self.height() - 2 * self.padding
        ratio = (value - value_min) / (value_max - value_min)
        return self.padding + chart_height * (1 - ratio)

    def _index_position(self, index: int) -> tuple[float, float]:
        """Return the widget-space position for an integer-indexed point."""
        chart_width = self.width() - 2 * self.padding
        n = len(self.values)
        x_pos = self.padding
        if n > 1:
            x_pos = self.padding + chart_width * index / (n - 1)
        y_pos = self._value_to_y(self.values[index] if 0 <= index < n else 0)
        return x_pos, y_pos

    def _sample_position(self, index: int) -> tuple[float, float]:
        """Return the widget-space position for a sample point."""
        chart_width = self.width() - 2 * self.padding
        n = len(self.values)
        x_pos = self.padding
        if n > 1 and 0 <= index < len(self.sample_positions):
            ratio = self.sample_positions[index] / (n - 1)
            x_pos = self.padding + chart_width * max(0.0, min(1.0, ratio))
        y_value = self.sample_values[index] if 0 <= index < len(self.sample_values) else 0.0
        return x_pos, self._value_to_y(y_value)

    def _reference_x_position(self) -> float | None:
        """Map the input H index to the widget x position."""
        if self.reference_h_index is None or len(self.values) <= 1:
            return None
        chart_width = self.width() - 2 * self.padding
        ratio = self.reference_h_index / max(1, len(self.values) - 1)
        ratio = max(0.0, min(1.0, ratio))
        return self.padding + chart_width * ratio

    def _reference_x_position_out(self) -> float | None:
        """Map the output H index to the widget x position."""
        if self.reference_h_index_out is None or len(self.values) <= 1:
            return None
        chart_width = self.width() - 2 * self.padding
        ratio = self.reference_h_index_out / max(1, len(self.values) - 1)
        ratio = max(0.0, min(1.0, ratio))
        return self.padding + chart_width * ratio

    def paintEvent(self, event: object) -> None:
        """Paint the chart background, integer-indexed points and sample points."""
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        width = self.width()
        height = self.height()
        chart_width = width - 2 * self.padding
        chart_height = height - 2 * self.padding
        n = len(self.values)
        chart_rect = QRect(self.padding, self.padding, int(chart_width), int(chart_height))

        painter.fillRect(self.rect(), QColor(255, 255, 255))
        # painter.fillRect(chart_rect, QColor(255, 255, 255))

        # Background image (scaled to chart area, placed behind grid)
        if self._bg_pixmap is not None:
            bg = self._bg_pixmap.scaled(
                chart_rect.width(), chart_rect.height(),
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            painter.drawPixmap(chart_rect.topLeft(), bg)

        # Horizontal grid lines (light gray dashed)
        painter.setPen(QPen(QColor(140, 140, 140), 0.5, Qt.DashLine))
        for idx in range(9):
            y_pos = self.padding + chart_height * idx / 8
            painter.drawLine(self.padding, int(y_pos), width - self.padding, int(y_pos))

        # Zero line
        painter.setPen(QPen(QColor(100, 100, 100), 2, Qt.DashLine))
        mid_y = self._value_to_y(0)
        painter.drawLine(self.padding, int(mid_y), width - self.padding, int(mid_y))

        # H_in reference line (dark dashed)
        ref_x = self._reference_x_position()
        if ref_x is not None:
            painter.setPen(QPen(QColor(60, 60, 60), 1, Qt.DashLine))
            painter.drawLine(int(ref_x), self.padding, int(ref_x), height - self.padding)

        # H_out reference line (white dashed)
        ref_x_out = self._reference_x_position_out()
        if ref_x_out is not None:
            painter.setPen(QPen(QColor(200, 200, 200), 1, Qt.DashLine))
            painter.drawLine(int(ref_x_out), self.padding, int(ref_x_out), height - self.padding)

        # Input / output value markers (×)
        marker_size = 4
        if ref_x is not None and self.input_value is not None:
            y_marker = self._value_to_y(self.input_value)
            painter.setPen(QPen(QColor(0, 0, 0), 2))  # black
            painter.drawLine(int(ref_x) - marker_size, int(y_marker) - marker_size,
                             int(ref_x) + marker_size, int(y_marker) + marker_size)
            painter.drawLine(int(ref_x) + marker_size, int(y_marker) - marker_size,
                             int(ref_x) - marker_size, int(y_marker) + marker_size)
        if ref_x_out is not None and self.output_value is not None:
            y_marker = self._value_to_y(self.output_value)
            painter.setPen(QPen(QColor(255, 255, 255), 2))  # white
            painter.drawLine(int(ref_x_out) - marker_size, int(y_marker) - marker_size,
                             int(ref_x_out) + marker_size, int(y_marker) + marker_size)
            painter.drawLine(int(ref_x_out) + marker_size, int(y_marker) - marker_size,
                             int(ref_x_out) - marker_size, int(y_marker) + marker_size)

        # Curve connecting integer-indexed points (black solid)
        if n >= 2:
            painter.setPen(QPen(QColor(0, 0, 0), 1))
            for idx in range(n - 1):
                x1, y1 = self._index_position(idx)
                x2, y2 = self._index_position(idx + 1)
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        # X-axis tick labels every 2 points
        font = painter.font()
        font.setPointSize(9)
        painter.setFont(font)
        painter.setPen(QColor(40, 40, 40))
        if n >= 2:
            for idx in range(0, n, 2):
                x_pos, _ = self._index_position(idx)
                painter.drawLine(int(x_pos), int(height - self.padding),
                                 int(x_pos), int(height - self.padding + 4))
                text_rect = self._clamp_text_rect(QRect(int(x_pos) - 18, int(height - self.padding + 6), 36, 14))
                painter.drawText(text_rect, Qt.AlignCenter, str(idx))

        # Y-axis range labels
        for value in (255, 192, 128, 64, 0, -64, -128, -192, -255):
            painter.drawText(5, int(self._value_to_y(value) + 4), str(value))

        # Integer-indexed points: small filled circles + value label
        # (even indices above the curve, odd indices below the curve)
        for idx in range(n):
            x_pos, y_pos = self._index_position(idx)
            painter.setBrush(QColor(0, 0, 0))
            painter.setPen(QPen(QColor(0, 0, 0), 1))
            painter.drawEllipse(int(x_pos) - 2, int(y_pos) - 2, 4, 4)
            if idx % 2 == 0:
                text_rect = QRect(int(x_pos) - 22, int(y_pos) - 22, 44, 14)
            else:
                text_rect = QRect(int(x_pos) - 22, int(y_pos) + 8, 44, 14)
            text_rect = self._clamp_text_rect(text_rect)
            painter.drawText(text_rect, Qt.AlignCenter, str(int(self.values[idx])))

        # Sample-point overlay: white dashed hollow circles (filled when selected).
        sample_radius = 4
        sample_diameter = sample_radius * 2
        for s_idx in range(len(self.sample_positions)):
            x_pos, y_pos = self._sample_position(s_idx)
            is_active = (
                s_idx == self.selected_sample
                or s_idx == self.dragging_sample
                or s_idx == self.hover_sample
            )
            if is_active:
                # Selected/hover/dragging: solid filled white circle
                painter.setBrush(Qt.white)
                painter.setPen(QPen(Qt.white, 2))
            else:
                # Idle: white dashed hollow circle
                painter.setBrush(QColor(0, 0, 0, 0))
                painter.setPen(QPen(Qt.white, 2, Qt.DashLine))
            painter.drawEllipse(
                int(x_pos) - sample_radius,
                int(y_pos) - sample_radius,
                sample_diameter,
                sample_diameter,
            )

    def _clamp_text_rect(self, rect: QRect) -> QRect:
        """Clamp annotation rectangles to the widget bounds so edge labels stay visible."""
        x_pos = max(0, min(rect.x(), self.width() - rect.width()))
        y_pos = max(0, min(rect.y(), self.height() - rect.height()))
        return QRect(x_pos, y_pos, rect.width(), rect.height())

    def mousePressEvent(self, event: object) -> None:
        """Select or start dragging the nearest sample point."""
        if event.button() != Qt.LeftButton:
            return
        sample = self._find_nearest_sample(event.position().x(), event.position().y())
        if sample is None:
            return
        self.selected_sample = sample
        self.dragging_sample = sample
        self.update()

    def mouseMoveEvent(self, event: object) -> None:
        """Update the dragged sample point or the hover state."""
        x_pos = event.position().x()
        y_pos = event.position().y()
        if self.dragging_sample is not None:
            chart_height = self.height() - 2 * self.padding
            ratio = 1 - (y_pos - self.padding) / chart_height
            ratio = max(0.0, min(1.0, ratio))
            value_min, value_max = self.value_range
            new_value = int(round(value_min + ratio * (value_max - value_min)))
            self.sample_values[self.dragging_sample] = new_value
            # H-cycle closure: sample 0 and sample n-1 share the same value.
            n_vals = len(self.sample_values)
            if n_vals > 1:
                if self.dragging_sample == 0:
                    self.sample_values[n_vals - 1] = new_value
                elif self.dragging_sample == n_vals - 1:
                    self.sample_values[0] = new_value
            self.samplePointChanged.emit(self.dragging_sample, list(self.sample_values))
            self.update()
            return
        hover = self._find_nearest_sample(x_pos, y_pos)
        if hover != self.hover_sample:
            self.hover_sample = hover
            self.update()

    def mouseReleaseEvent(self, event: object) -> None:
        """Stop dragging a sample point."""
        if event.button() == Qt.LeftButton:
            self.dragging_sample = None
            self.update()

    def _find_nearest_sample(self, x_pos: float, y_pos: float) -> int | None:
        """Return the nearest sample-point index within the hit threshold."""
        threshold = 10
        best_index: int | None = None
        best_distance = threshold
        for s_idx in range(len(self.sample_positions)):
            point_x, point_y = self._sample_position(s_idx)
            distance = ((x_pos - point_x) ** 2 + (y_pos - point_y) ** 2) ** 0.5
            if distance < best_distance:
                best_distance = distance
                best_index = s_idx
        return best_index


class AcmUiController:
    """Controls the ACM tab: algorithm selection, delta editing, and LUT visualization."""

    _SUPPORTED_CLIP_TYPES: tuple[str, ...] = ("easy_clip", "radial_clip", "luma_clip")
    _ALGO_KEYS: tuple[str, ...] = ("VOP_VP_ACM", "SW_ACM", "EVIDEO_ACM", "SW_ACM_VARIANT")
    _ALGO_DISPLAY_TEXTS: tuple[str, ...] = (
        "HW_ACM(VOP) (9,13,65,17)",
        "SW_ACM (9,13,65,65)",
        "EVIDEO_ACM (9,13,65,65)",
        "SW_ACM_VARIANT (custom)",
    )
    _HW_ALGO_KEY = "VOP_VP_ACM"

    # ------------------------------------------------------------------ #
    # Initialization                                                     #
    # ------------------------------------------------------------------ #

    def __init__(
        self,
        acm_widget: AcmUiWidget,
        parent_window: QMainWindow | None = None,
        input_provider: Callable[[], ImageFrame | None] | None = None,
        output_callback: Callable[['ImageFrame'], None] | None = None,
        preview_time_callback: Callable[[float], None] | None = None,
        status_callback: Callable[[str], None] | None = None,
        config_path_getter: Callable[[], str] | None = None,
        config_path_setter: Callable[[str], None] | None = None,
        dock_host: QMainWindow | None = None,
    ) -> None:
        """Bind to an AcmUiWidget instance and explicit host callbacks.

        Args:
            acm_widget: An AcmUiWidget whose ``.ui`` provides ACM controls.
            parent_window: Optional host window kept for QObject parenting.
            input_provider: Optional callback returning the current input YUV444 buffer.
            output_callback: Optional callback receiving the processed output YUV444.
            preview_time_callback: Optional callback receiving elapsed milliseconds.
            status_callback: Optional callback receiving status-bar text.
            config_path_getter: Optional callback returning the current config path string.
            config_path_setter: Optional callback receiving a config path string.
            dock_host: Unused legacy parameter kept for compatibility.
        """
        del dock_host
        self._win = parent_window
        self.widget = acm_widget
        self.ui = acm_widget.ui
        self._input_provider = input_provider or (lambda: None)
        self._output_callback = output_callback or (lambda output: None)
        self._preview_time_callback = preview_time_callback or (lambda elapsed_ms: None)
        self._status_callback = status_callback or (lambda message: None)
        self._config_path_getter = config_path_getter or (lambda: "")
        self._config_path_setter = config_path_setter or (lambda path: None)
        self._last_input_key: tuple | None = None
        self._latest_output_frame: ImageFrame | None = None
        self._frozen_pixel_x: int | None = None
        self._frozen_pixel_y: int | None = None
        self._colorspace_user_override = False
        self._suppress_colorspace_signal = False

        # --- ACM algorithm instances ---
        from script.acm.acm_impls import AcmImplHwRk, AcmImplSwRk, AcmImplSwEvideo, AcmImplSwVariant

        self.acm_instances = {
            "VOP_VP_ACM": AcmImplHwRk(),
            "SW_ACM": AcmImplSwRk(),
            "EVIDEO_ACM": AcmImplSwEvideo(),
            "SW_ACM_VARIANT": AcmImplSwVariant(),
        }
        self.current_algo = "VOP_VP_ACM"
        self._apply_algo_display_names()

        # --- Delta chart state ---
        self.full_delta_ybyh = None
        self.full_delta_sbyh = None
        self.full_delta_hbyh = None
        self.ctrl_point_count = self.ui.slider_ctrl_points.value()
        self.interp_method = self.ui.comboBox_interp_method.currentText()
        # Shared sample-point positions across Y/S/H charts.
        self.sample_positions: list[float] = []
        self.sample_values_y: list[float] = []
        self.sample_values_s: list[float] = []
        self.sample_values_h: list[float] = []
        self._suppress_sample_signal = False

        # --- Chart widgets (hosted inside ACM tab) ---
        _res_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resource")
        self.delta_chart_y = SingleCurveChartWidget(
            (ACM_DELTA_Y_MIN, ACM_DELTA_Y_MAX), QColor(255, 200, 0),
            bg_image_path=os.path.join(_res_dir, "Y_deltaImg.bmp"))
        self.delta_chart_s = SingleCurveChartWidget(
            (ACM_DELTA_S_MIN, ACM_DELTA_S_MAX), QColor(0, 180, 0),
            bg_image_path=os.path.join(_res_dir, "S_deltaImg.bmp"))
        self.delta_chart_h = SingleCurveChartWidget(
            (ACM_DELTA_H_MIN, ACM_DELTA_H_MAX), QColor(0, 100, 255),
            bg_image_path=os.path.join(_res_dir, "H_deltaImg.bmp"))
        for host, chart in (
            (self.ui.widget_delta_y_host, self.delta_chart_y),
            (self.ui.widget_delta_s_host, self.delta_chart_s),
            (self.ui.widget_delta_h_host, self.delta_chart_h),
        ):
            layout = QVBoxLayout(host)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(chart)

        # --- LUT overview window ---
        self.lut_image_window: LutImageWindow | None = None

        # --- Auto-run debounce timer ---
        self.auto_run_timer = QTimer(self.widget)
        self.auto_run_timer.setSingleShot(True)
        self.auto_run_timer.timeout.connect(self._do_auto_run)

        self._connect_signals()
        self._init_state()

    def _init_state(self) -> None:
        """Perform initial state sync after all widgets are ready."""
        if hasattr(self.ui, "radioButton_colorspace_hsv"):
            self.ui.radioButton_colorspace_hsv.setEnabled(False)
            self.ui.radioButton_colorspace_hsv.setToolTip(
                "HSV ACM path is not implemented yet. Please use YHS."
            )
        self._sync_clip_type_ui_state()
        self._on_acm_colorspace_changed()
        self._sync_ctrl_point_slider(self._get_current_acm().len_h)
        self._reload_delta_controls_from_acm()
        self._on_lut_visualization_toggled(bool(self.ui.checkBox_lut_visualization.isChecked()))

    def _is_acm_enabled(self) -> bool:
        checkbox = getattr(self.ui, "checkBox_enable_acm", None)
        if checkbox is None:
            return True
        return bool(checkbox.isChecked())

    def _auto_select_colorspace_for_input(self, frame: ImageFrame) -> None:
        """Auto-select the currently supported ACM colorspace for the input frame."""
        if self._colorspace_user_override:
            return
        self._suppress_colorspace_signal = True
        try:
            del frame
            if hasattr(self.ui, "radioButton_colorspace_yhs"):
                self.ui.radioButton_colorspace_yhs.setChecked(True)
        finally:
            self._suppress_colorspace_signal = False

    # ------------------------------------------------------------------ #
    # Public accessors                                                   #
    # ------------------------------------------------------------------ #

    def request_auto_run(self) -> None:
        """Public helper that schedules ACM processing with the current input image."""
        self._schedule_auto_run()

    # ------------------------------------------------------------------ #
    # Signal wiring                                                      #
    # ------------------------------------------------------------------ #

    def _connect_signals(self) -> None:
        """Wire ACM widget signals to internal handlers."""
        ui = self.ui
        ui.slider_ctrl_points.valueChanged.connect(self._on_ctrl_points_changed)
        ui.comboBox_interp_method.currentTextChanged.connect(self._on_interp_method_changed)
        ui.comboBox_algo_type.currentIndexChanged.connect(self._on_algo_changed)
        ui.groupBox_lut_lengths.toggled.connect(self._on_lut_lengths_group_toggled)
        if hasattr(ui, "checkBox_enable_acm"):
            ui.checkBox_enable_acm.toggled.connect(self._schedule_auto_run)
        if hasattr(ui, "checkBox_ignore_gain_luts"):
            ui.checkBox_ignore_gain_luts.toggled.connect(self._on_ignore_gain_luts_toggled)
        ui.checkBox_lut_visualization.toggled.connect(self._on_lut_visualization_toggled)
        ui.spinBox_len_h.valueChanged.connect(self._on_len_h_changed)
        ui.spinBox_len_y.valueChanged.connect(self._on_lut_lengths_changed)
        ui.spinBox_len_s.valueChanged.connect(self._on_lut_lengths_changed)
        ui.spinBox_len_h2.valueChanged.connect(self._on_lut_lengths_changed)
        self._connect_slider_spin(ui.slider_len_y, ui.spinBox_len_y)
        self._connect_slider_spin(ui.slider_len_s, ui.spinBox_len_s)
        self._connect_slider_spin(ui.slider_len_h, ui.spinBox_len_h)
        self._connect_slider_spin(ui.slider_len_h2, ui.spinBox_len_h2)
        ui.slider_len_h.valueChanged.connect(self._on_len_h_changed)
        ui.slider_len_y.valueChanged.connect(self._on_lut_lengths_changed)
        ui.slider_len_s.valueChanged.connect(self._on_lut_lengths_changed)
        ui.slider_len_h2.valueChanged.connect(self._on_lut_lengths_changed)
        ui.button_reset_curr.clicked.connect(self._on_reset_curr)
        ui.button_smooth_curr.clicked.connect(self._on_smooth_curr)
        ui.button_reset_all.clicked.connect(self._on_reset_all)
        ui.button_smooth_all.clicked.connect(self._on_smooth_all)
        ui.button_reset_gain.clicked.connect(self._on_reset_gain)
        ui.button_reset_offset.clicked.connect(self._on_reset_offset)
        ui.pushButton_read_config.clicked.connect(self._on_read_config)
        ui.pushButton_save_config.clicked.connect(self._on_save_config)
        ui.button_reset_lut_length.clicked.connect(self._on_reset_lut_length)
        self._connect_slider_spin(ui.slider_gain_y, ui.spinBox_gain_y)
        self._connect_slider_spin(ui.slider_gain_s, ui.spinBox_gain_s)
        self._connect_slider_spin(ui.slider_gain_h, ui.spinBox_gain_h)
        self._connect_slider_spin(ui.slider_offset_wr, ui.spinBox_offset_wr)
        self._connect_slider_spin(ui.slider_offset_wg, ui.spinBox_offset_wg)
        self._connect_slider_spin(ui.slider_offset_wb, ui.spinBox_offset_wb)
        ui.slider_gain_y.valueChanged.connect(self._schedule_auto_run)
        ui.slider_gain_s.valueChanged.connect(self._schedule_auto_run)
        ui.slider_gain_h.valueChanged.connect(self._schedule_auto_run)
        ui.slider_offset_wr.valueChanged.connect(self._schedule_auto_run)
        ui.slider_offset_wg.valueChanged.connect(self._schedule_auto_run)
        ui.slider_offset_wb.valueChanged.connect(self._schedule_auto_run)
        # Max Delta controls
        ui.button_reset_max_delta.clicked.connect(self._on_reset_max_delta)
        ui.comboBox_clip_type.currentTextChanged.connect(self._on_clip_type_changed)
        ui.slider_max_delta_y.valueChanged.connect(
            lambda v: ui.spinBox_max_delta_y.setValue(v / 100.0))
        ui.spinBox_max_delta_y.valueChanged.connect(
            lambda v: ui.slider_max_delta_y.setValue(int(v * 100 + 0.5)))
        ui.slider_max_delta_s.valueChanged.connect(
            lambda v: ui.spinBox_max_delta_s.setValue(v / 100.0))
        ui.spinBox_max_delta_s.valueChanged.connect(
            lambda v: ui.slider_max_delta_s.setValue(int(v * 100 + 0.5)))
        self._connect_slider_spin(ui.slider_max_delta_h, ui.spinBox_max_delta_h)
        ui.slider_max_delta_y.valueChanged.connect(self._schedule_auto_run)
        ui.slider_max_delta_s.valueChanged.connect(self._schedule_auto_run)
        ui.slider_max_delta_h.valueChanged.connect(self._schedule_auto_run)
        ui.radioButton_colorspace_yhs.toggled.connect(self._on_acm_colorspace_changed)
        ui.radioButton_colorspace_hsv.toggled.connect(self._on_acm_colorspace_changed)
        self.delta_chart_y.dataChanged.connect(
            lambda changed_index, values: self._on_delta_chart_changed("y", changed_index, values)
        )
        self.delta_chart_s.dataChanged.connect(
            lambda changed_index, values: self._on_delta_chart_changed("s", changed_index, values)
        )
        self.delta_chart_h.dataChanged.connect(
            lambda changed_index, values: self._on_delta_chart_changed("h", changed_index, values)
        )
        self.delta_chart_y.samplePointChanged.connect(
            lambda idx, values: self._on_sample_point_changed("y", idx, values)
        )
        self.delta_chart_s.samplePointChanged.connect(
            lambda idx, values: self._on_sample_point_changed("s", idx, values)
        )
        self.delta_chart_h.samplePointChanged.connect(
            lambda idx, values: self._on_sample_point_changed("h", idx, values)
        )

    # ------------------------------------------------------------------ #
    # Slider-spin helpers                                                #
    # ------------------------------------------------------------------ #

    def _connect_slider_spin(self, slider: object, spinbox: object) -> None:
        """Synchronize a slider and spin box bidirectionally."""
        slider.valueChanged.connect(spinbox.setValue)
        spinbox.valueChanged.connect(slider.setValue)

    @staticmethod
    def _set_spinbox_value(spinbox: object, value: int) -> None:
        """Set a spin box value without emitting change notifications."""
        spinbox.blockSignals(True)
        spinbox.setValue(value)
        spinbox.blockSignals(False)

    @staticmethod
    def _set_slider_spin_value(slider: object, spinbox: object, value: int) -> None:
        """Set a linked slider and spin box pair without signal feedback."""
        slider.blockSignals(True)
        spinbox.blockSignals(True)
        slider.setValue(value)
        spinbox.setValue(value)
        slider.blockSignals(False)
        spinbox.blockSignals(False)

    # ------------------------------------------------------------------ #
    # ACM instance helpers                                               #
    # ------------------------------------------------------------------ #

    def _get_current_acm(self) -> object:
        """Return the current ACM implementation instance."""
        return self.acm_instances[self.current_algo]

    def _apply_algo_display_names(self) -> None:
        """Refresh the visible algorithm names shown by the combo box."""
        combo = self.ui.comboBox_algo_type
        for index, text in enumerate(self._ALGO_DISPLAY_TEXTS):
            if index < combo.count():
                combo.setItemText(index, text)

    def _sync_clip_type_ui_state(self) -> None:
        """Enable clip-type controls only for algorithms that actually consume them."""
        is_supported = self.current_algo != self._HW_ALGO_KEY
        tooltip = ""
        if not is_supported:
            tooltip = "clip_type is only supported by software ACM paths; HW_ACM(VOP) ignores this setting."
        self.ui.comboBox_clip_type.setEnabled(is_supported)
        self.ui.comboBox_clip_type.setToolTip(tooltip)
        if hasattr(self.ui, "label_clip_type"):
            self.ui.label_clip_type.setEnabled(is_supported)
            self.ui.label_clip_type.setToolTip(tooltip)

    def clear_preview_h_marker(self) -> None:
        """Remove all preview-linked H markers and value markers from all delta charts."""
        self._frozen_pixel_x = None
        self._frozen_pixel_y = None
        for chart in (self.delta_chart_y, self.delta_chart_s, self.delta_chart_h):
            chart.set_h_markers(None, None, None, None)

    def _get_pixel_yhs(
        self, frame: ImageFrame, x_pos: int, y_pos: int
    ) -> tuple[float, float, float] | None:
        """Extract (Y_val, S_val, H_deg) from a single pixel in a frame.

        Y_val  in [0, 255] or [0, 1023] depending on depth.
        S_val  in [0, s_max_raw] (raw saturation, not normalised).
        H_deg  in [-180, 180].
        """
        if x_pos < 0 or y_pos < 0 or y_pos >= frame.pyr.shape[0] or x_pos >= frame.pyr.shape[1]:
            return None
        if frame.is_rgb:
            r = frame.pyr[y_pos:y_pos + 1, x_pos:x_pos + 1]
            g = frame.pug[y_pos:y_pos + 1, x_pos:x_pos + 1]
            b = frame.pvb[y_pos:y_pos + 1, x_pos:x_pos + 1]
            y_arr, u_arr, v_arr = rgb_to_yuv(
                r, g, b,
                input_cs=frame.clrspc if frame.clrspc in (0, 1) else 1,
                output_cs=5,
            )
            yuv_dtype = y_arr.dtype
            y_val = float(y_arr[0, 0])
            cb = int(u_arr[0, 0])
            cr = int(v_arr[0, 0])
        else:
            yuv = frame.as_yuv444_stacked()[y_pos:y_pos + 1, x_pos:x_pos + 1, :]
            yuv_dtype = yuv.dtype
            y_val = float(yuv[0, 0, 0])
            cb = int(yuv[0, 0, 1])
            cr = int(yuv[0, 0, 2])

        depth = 10 if yuv_dtype == np.uint16 else 8
        cbcr_center = 512 if depth == 10 else 128
        cb -= cbcr_center
        cr -= cbcr_center

        acm = self._get_current_acm()
        if getattr(acm, "use_cordic", False):
            h_deg_arr, s_arr, _, _ = cordic.cordic_cbcr2hs(
                np.array([[cb]], dtype=np.int32), np.array([[cr]], dtype=np.int32),
                depth, 13, 6, False)
            h_deg = float(h_deg_arr[0, 0])
            s_val = float(s_arr[0, 0])
        else:
            s_val = float(int(np.sqrt(cb * cb + cr * cr) + 0.5))  # match pipeline rounding
            h_deg = float(np.rad2deg(np.arctan2(cr, cb)).astype(np.int32))  # match pipeline truncation
        return y_val, s_val, h_deg

    @staticmethod
    def _norm_ys_to_chart(y_val: float, s_val: float, depth: int, s_max: int) -> tuple[float, float]:
        """Normalise raw Y and S values to the chart display range [0, 255].

        Y: 8-bit values pass through; 10-bit values are scaled down.
        S: scaled from [0, s_max] to [0, 255] using ``s_max`` from the
            active ACM pipeline.
        """
        if depth >= 10:
            y_norm = y_val / 1023.0 * 255.0
        else:
            y_norm = float(y_val)
        s_norm = min(s_val / max(float(s_max), 1.0), 1.0) * 255.0
        return y_norm, s_norm

    def _h_deg_to_index(self, h_deg: float) -> float:
        """Convert hue in degrees [-180, 180] to the current ACM H index."""
        acm = self._get_current_acm()
        h_f = (h_deg + 180.0) / 360.0
        return float(h_f * (acm.len_h - 1))

    def update_preview_h_marker(self, x_pos: int, y_pos: int) -> None:
        """Compute the ACM H-domain markers for one pixel and update all charts.

        Reads the raw pixel from the input frame and the processed pixel from
        the latest output frame, then places black × markers on the H_in line
        and white × markers on the H_out line for the delta_y and delta_s charts.
        """
        # Cache frozen pixel coordinates so markers can be refreshed after processing.
        self._frozen_pixel_x = x_pos
        self._frozen_pixel_y = y_pos

        in_frame = self._input_provider()
        out_frame = self._latest_output_frame
        if in_frame is None:
            self.clear_preview_h_marker()
            return

        # Determine depth / s_max once from the input frame.
        in_depth = 10 if in_frame.pyr.dtype == np.uint16 else 8
        clip_type = getattr(self._get_current_acm(), 'clip_type', 'easy_clip')
        if in_depth >= 10:
            s_max = 511 if clip_type in ('radial_clip', 'luma_clip') else 724
        else:
            s_max = 127 if clip_type in ('radial_clip', 'luma_clip') else 181

        # Input pixel
        in_ysh = self._get_pixel_yhs(in_frame, x_pos, y_pos)
        if in_ysh is None:
            self.clear_preview_h_marker()
            return
        y_in, s_in, h_in = in_ysh
        h_idx_in = self._h_deg_to_index(h_in)
        y_in_norm, s_in_norm = self._norm_ys_to_chart(y_in, s_in, in_depth, s_max)

        # Output pixel (if available)
        if out_frame is not None:
            out_ysh = self._get_pixel_yhs(out_frame, x_pos, y_pos)
            if out_ysh is not None:
                y_out, s_out, h_out = out_ysh
                h_idx_out = self._h_deg_to_index(h_out)
                y_out_norm, s_out_norm = self._norm_ys_to_chart(y_out, s_out, in_depth, s_max)
            else:
                h_idx_out, y_out_norm, s_out_norm = None, None, None
        else:
            h_idx_out, y_out_norm, s_out_norm = None, None, None

        # Update charts
        self.delta_chart_y.set_h_markers(h_idx_in, h_idx_out, y_in_norm, y_out_norm)
        self.delta_chart_s.set_h_markers(h_idx_in, h_idx_out, s_in_norm, s_out_norm)
        self.delta_chart_h.set_h_markers(h_idx_in, h_idx_out, None, None)

    def _apply_lut_lengths(self) -> None:
        """Apply the current spinBox LUT lengths to the active ACM instance.

        Instead of going through the default-length intermediate (which doubles
        bicubic resampling error and causes values to drift toward zero when
        shrinking), we snapshot the current LUT, let ``set_len`` configure the
        new lengths, then directly resize the snapshot to the new length in
        a single step.
        """
        acm = self._get_current_acm()
        from script.acm.acm_impl_base import bicubic_resize_array_1d

        # Snapshot current 1D delta LUTs before the length change.
        saved_y = np.copy(acm.lut_delta_ybyh)
        saved_s = np.copy(acm.lut_delta_sbyh)
        saved_h = np.copy(acm.lut_delta_hbyh)
        old_len_h = saved_y.size

        new_len_y = self.ui.spinBox_len_y.value()
        new_len_s = self.ui.spinBox_len_s.value()
        new_len_h = self.ui.spinBox_len_h.value()
        new_len_h2 = self.ui.spinBox_len_h2.value()

        # Persist current edits to the default set (needed for algorithm
        # switches and config saves), then apply the new length config.
        acm.sync_to_default()
        acm.set_len(new_len_y, new_len_s, new_len_h, new_len_h2)

        # Replace the default→current resample result with a direct
        # old→new resize to avoid the default-length bottleneck.
        if old_len_h > 0 and old_len_h != new_len_h:
            acm.lut_delta_ybyh = np.clip(
                bicubic_resize_array_1d(saved_y, new_len_h),
                ACM_DELTA_Y_MIN, ACM_DELTA_Y_MAX).astype(np.int16)
            acm.lut_delta_sbyh = np.clip(
                bicubic_resize_array_1d(saved_s, new_len_h),
                ACM_DELTA_S_MIN, ACM_DELTA_S_MAX).astype(np.int16)
            acm.lut_delta_hbyh = np.clip(
                bicubic_resize_array_1d(saved_h, new_len_h),
                ACM_DELTA_H_MIN, ACM_DELTA_H_MAX).astype(np.int16)

    # ------------------------------------------------------------------ #
    # Control-point logic                                                #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _normalize_ctrl_point_count(len_h: int, value: int) -> int:
        """Clamp the control-point count to the valid range [4, len_h]."""
        return max(4, min(int(value), int(len_h)))

    def _update_ctrl_point_hint(self, len_h: int) -> None:
        """Refresh the displayed control-point hint text."""
        count = max(1, len(self.sample_positions))
        step = (len_h - 1) / max(1, count - 1) if count > 1 else 0.0
        self.ui.label_delta_hint.setText(f"(len_h: {len_h}, step: {step:.2f})")

    def _compute_sample_positions(self, len_h: int, count: int) -> list[float]:
        """Compute evenly spaced sample positions in [0, len_h - 1].

        Returns exactly ``count`` positions, with the first at 0 and the
        last at ``len_h - 1``.  H‑cycle closure is handled by mirroring the
        value of sample 0 to sample ``count - 1`` at the data level, not by
        adding an extra visual point.
        """
        if count < 2:
            return [0.0]
        positions: list[float] = []
        for i in range(count):
            pos = (len_h - 1) * i / (count - 1)
            positions.append(round(pos, 2))
        return positions

    def _sync_ctrl_point_slider(self, len_h: int) -> None:
        """Update the control-point slider bounds for the current len_h."""
        max_value = max(4, int(len_h))
        default_value = max(4, min(max_value, int(len_h) // 4))
        new_value = self._normalize_ctrl_point_count(len_h, default_value)
        self.ui.slider_ctrl_points.blockSignals(True)
        self.ui.slider_ctrl_points.setRange(4, max_value)
        self.ui.slider_ctrl_points.setSingleStep(1)
        self.ui.slider_ctrl_points.setPageStep(1)
        self.ui.slider_ctrl_points.setValue(new_value)
        self.ui.slider_ctrl_points.blockSignals(False)
        self.ctrl_point_count = new_value
        self.ui.label_ctrl_points_value.setText(str(new_value))
        self._update_ctrl_point_hint(len_h)

    # ------------------------------------------------------------------ #
    # Delta LUT management                                               #
    # ------------------------------------------------------------------ #

    def _reload_delta_controls_from_acm(self) -> None:
        """Reload the chart data from the current ACM LUT tables."""
        acm = self._get_current_acm()
        self.full_delta_ybyh = np.array(acm.lut_delta_ybyh, dtype=np.int16)
        self.full_delta_sbyh = np.array(acm.lut_delta_sbyh, dtype=np.int16)
        self.full_delta_hbyh = np.array(acm.lut_delta_hbyh, dtype=np.int16)
        len_h = len(self.full_delta_ybyh)
        self.delta_chart_y.set_values(self.full_delta_ybyh)
        self.delta_chart_s.set_values(self.full_delta_sbyh)
        self.delta_chart_h.set_values(self.full_delta_hbyh)
        self._recompute_sample_points(len_h, self.ctrl_point_count, force=True)
        self._refresh_sample_overlays()
        self._update_lut_visualization()

    def _recompute_sample_points(self, len_h: int, count: int, force: bool = False) -> None:
        """Recompute sample-point positions and refresh the overlay on each chart.

        When ``force`` is True the sample values are resampled from the current
        integer-indexed LUT. Otherwise the previously stored sample values are
        kept so that adjusting the slider does not destroy the user's edits.
        """
        positions = self._compute_sample_positions(len_h, count)
        prev_values = (
            list(self.sample_values_y),
            list(self.sample_values_s),
            list(self.sample_values_h),
        )
        self.sample_positions = positions
        if force or not self.sample_values_y or len(self.sample_values_y) != len(positions):
            self.sample_values_y = self._resample_sample_values(
                self.full_delta_ybyh, positions
            )
            self.sample_values_s = self._resample_sample_values(
                self.full_delta_sbyh, positions
            )
            self.sample_values_h = self._resample_sample_values(
                self.full_delta_hbyh, positions
            )
        else:
            self.sample_values_y = self._resize_sample_values(prev_values[0], len(positions))
            self.sample_values_s = self._resize_sample_values(prev_values[1], len(positions))
            self.sample_values_h = self._resize_sample_values(prev_values[2], len(positions))
        self._refresh_sample_overlays()

    @staticmethod
    def _resample_sample_values(full_lut: np.ndarray | None, positions: list[float]) -> list[float]:
        """Resample the integer-indexed LUT at the given sample positions."""
        if full_lut is None or len(full_lut) == 0 or not positions:
            return [0.0] * len(positions)
        x_src = np.arange(len(full_lut), dtype=np.float32)
        return [float(v) for v in np.interp(positions, x_src, full_lut.astype(np.float32))]

    @staticmethod
    def _resize_sample_values(values: list[float], new_size: int) -> list[float]:
        """Resize a sample-value list, padding/truncating while keeping first/last paired."""
        if new_size <= 0:
            return []
        if not values:
            return [0.0] * new_size
        if len(values) == new_size:
            return list(values)
        if new_size == 1:
            return [values[0]]
        x_src = np.linspace(0.0, 1.0, len(values))
        x_dst = np.linspace(0.0, 1.0, new_size)
        return [float(v) for v in np.interp(x_dst, x_src, values)]

    def _refresh_sample_overlays(self) -> None:
        """Push current sample-point positions/values to all three chart widgets."""
        self._suppress_sample_signal = True
        try:
            self.delta_chart_y.set_sample_points(self.sample_positions, self.sample_values_y)
            self.delta_chart_s.set_sample_points(self.sample_positions, self.sample_values_s)
            self.delta_chart_h.set_sample_points(self.sample_positions, self.sample_values_h)
        finally:
            self._suppress_sample_signal = False

    def _interpolate_segment(
        self,
        x_points: list[float] | np.ndarray,
        y_points: list[float] | np.ndarray,
        x_targets: list[float] | np.ndarray,
    ) -> np.ndarray:
        """Interpolate a local segment using the selected interpolation method.

        Only ``Linear``/``Cubic``/``B-Spline`` are true interpolators; the
        filter-style options (``Poly-13``/``Savitzky-Golay``) fall
        back to linear interpolation here since they are not meaningful on
        three control points.
        """
        x_points = np.array(x_points, dtype=np.float32)
        y_points = np.array(y_points, dtype=np.float32)
        x_targets = np.array(x_targets, dtype=np.float32)
        if x_targets.size == 0:
            return np.array([], dtype=np.float32)
        if self.interp_method in ("Linear", "Poly-13", "Savitzky-Golay") or len(x_points) < 3:
            return np.interp(x_targets, x_points, y_points)
        try:
            from scipy.interpolate import interp1d, make_interp_spline

            if self.interp_method == "B-Spline":
                spline = make_interp_spline(x_points, y_points, k=min(3, len(x_points) - 1))
                return spline(x_targets)
            kind = "cubic" if len(x_points) >= 4 else "quadratic"
            return interp1d(x_points, y_points, kind=kind)(x_targets)
        except Exception:
            return np.interp(x_targets, x_points, y_points)

    def _apply_sample_point_change(
        self,
        curve_key: str,
        changed_idx: int | None = None,
    ) -> None:
        """Regenerate the integer-indexed LUT values affected by a sample edit.

        When ``changed_idx`` is given, only the segments adjacent to that
        sample point (its left and right neighbour segments) are
        re-interpolated; the rest of the LUT is left untouched. When
        ``changed_idx`` is ``None``, the full LUT is rebuilt (used by the
        ``smooth`` action).

        The H-cycle closure pair (sample 0 and the last sample, whose value
        mirrors sample 0) is handled by treating changes to either end as
        changes to both endpoints.
        """
        full_lut = getattr(self, f"full_delta_{curve_key}byh")
        if full_lut is None or len(self.sample_positions) < 2:
            return
        sample_values = getattr(self, f"sample_values_{curve_key}")
        if len(sample_values) != len(self.sample_positions):
            return
        len_h = len(full_lut)
        positions = self.sample_positions
        n = len(positions)
        # Map each sample to its nearest integer H index so the curve honors
        # the control point value at the closest grid index.
        nearest_indices = [
            int(round(min(max(float(p), 0.0), float(len_h - 1))))
            for p in positions
        ]
        # Decide which segments to re-interpolate and which samples need to
        # be synced to the LUT's nearest integer index.
        if changed_idx is None or not (0 <= changed_idx < n):
            segments_to_update = set(range(n - 1))
            samples_to_update = set(range(n))
        else:
            samples_to_update = {changed_idx}
            if changed_idx == 0 or changed_idx == n - 1:
                # The H-cycle closure pair shares a value, so editing either
                # end affects the other and both its surrounding segments.
                samples_to_update.update({0, n - 1})
            segments_to_update = set()
            for s in samples_to_update:
                if 0 < s:
                    segments_to_update.add(s - 1)
                if s < n - 1:
                    segments_to_update.add(s)
        for i in sorted(segments_to_update):
            target_min = nearest_indices[i]
            target_max = nearest_indices[i + 1]
            if i == 0:
                target_min = max(target_min, 1)  # preserve endpoint at index 0
            if target_max <= target_min:
                continue
            target_indices = np.arange(target_min, target_max, dtype=np.int32)
            # Build the window of sample indices to feed to the interpolator.
            # Cubic / B-Spline need at least 4 points; expand outward from
            # [i-1, i+1] until we have enough or hit boundaries.
            if self.interp_method in ("Cubic", "B-Spline"):
                start_idx = max(0, i - 1) if i > 0 else 0
                end_idx = min(i + 1, n - 1)
                while end_idx - start_idx + 1 < 4:
                    if start_idx > 0:
                        start_idx -= 1
                    if end_idx < n - 1 and end_idx - start_idx + 1 < 4:
                        end_idx += 1
                    if start_idx == 0 and end_idx == n - 1:
                        break
            elif i == 0:
                start_idx, end_idx = 0, 1
            else:
                start_idx, end_idx = i - 1, i + 1
            x_pts = positions[start_idx:end_idx + 1]
            y_pts = sample_values[start_idx:end_idx + 1]
            segment_values = self._interpolate_segment(x_pts, y_pts, target_indices)
            full_lut[target_indices] = np.rint(segment_values).astype(np.int16)
        # Force the integer index nearest to each changed sample point to
        # mirror that sample's value, so dragging a sample point is always
        # reflected in the closest integer-indexed point.
        for s_idx in samples_to_update:
            full_lut[nearest_indices[s_idx]] = int(round(sample_values[s_idx]))
        # Force H-cycle closure on endpoints.
        endpoint_value = int(round(sample_values[0]))
        full_lut[0] = endpoint_value
        full_lut[-1] = endpoint_value
        getattr(self, f"delta_chart_{curve_key}").set_values(full_lut)

    def _on_sample_point_changed(self, curve_key: str, idx: int, sample_values: list) -> None:
        """React to a sample point being edited in one of the charts.

        The chart widget already keeps the H-cycle closure pair (first and
        last sample) in sync, so we only need to persist the new values and
        rebuild the affected segments of the integer-indexed LUT. The
        ``idx`` is forwarded to limit the rebuild scope to the changed
        sample's neighbour segments.
        """
        if self._suppress_sample_signal:
            return
        setattr(self, f"sample_values_{curve_key}", [float(v) for v in sample_values])
        self._apply_sample_point_change(curve_key, changed_idx=idx)
        self._apply_full_delta_to_acm()
        self._update_lut_visualization()
        self._schedule_auto_run()

    def _apply_full_delta_to_acm(self) -> None:
        """Write the rebuilt full LUT arrays back to the current ACM instance."""
        if self.full_delta_ybyh is None:
            return
        acm = self._get_current_acm()
        acm.lut_delta_ybyh[:] = self.full_delta_ybyh
        acm.lut_delta_sbyh[:] = self.full_delta_sbyh
        acm.lut_delta_hbyh[:] = self.full_delta_hbyh

    def _reset_delta_curve(self, curve_key: str) -> None:
        """Reset one delta curve and its backing LUT to all zeros."""
        full_lut = getattr(self, f"full_delta_{curve_key}byh")
        if full_lut is None:
            return
        full_lut[:] = 0
        getattr(self, f"delta_chart_{curve_key}").set_values([0] * len(full_lut))
        sample_attr = f"sample_values_{curve_key}"
        if getattr(self, sample_attr):
            values = getattr(self, sample_attr)
            for i in range(len(values)):
                values[i] = 0.0
            self._refresh_sample_overlays()
        self._apply_full_delta_to_acm()
        self._update_lut_visualization()
        self._schedule_auto_run()

    @staticmethod
    def _smooth_curve(values: np.ndarray, method: str) -> np.ndarray:
        """Apply a smoothing/fitting method selected from the interpolation combo.

        Supported methods:
          - ``"Poly-13"``: global least-squares polynomial fit
            evaluated back at integer H indices.
          - ``"Savitzky-Golay"``: local polynomial regression filter (window
            length auto-sized to data length). Preserves peaks and valleys
            better than global polynomial fitting.
        """
        if values.size == 0:
            return values.copy()
        if method == "Savitzky-Golay":
            try:
                from scipy.signal import savgol_filter
            except Exception:
                # Fall back to Poly-13 if SciPy is unavailable.
                method = "Poly-13"
            else:
                # Window length must be odd and <= values.size; pick a sensible
                # default that adapts to short curves.
                win = min(11, values.size)
                if win % 2 == 0:
                    win -= 1
                win = max(win, 3)
                poly = min(3, win - 1)
                smoothed = savgol_filter(
                    values.astype(np.float32),
                    window_length=win,
                    polyorder=poly,
                )
                return np.rint(smoothed).astype(values.dtype)
        degree = 13
        if values.size <= degree + 1:
            return values.copy()
        x = np.arange(values.size, dtype=np.float32)
        coeffs = np.polyfit(x, values.astype(np.float32), degree)
        smoothed = np.polyval(coeffs, x)
        return np.rint(smoothed).astype(values.dtype)

    @staticmethod
    def _delta_clip_range(curve_key: str) -> tuple[int, int]:
        """Return the valid (low, high) clip range for a delta curve."""
        if curve_key == "h":
            return ACM_DELTA_H_MIN, ACM_DELTA_H_MAX
        return ACM_DELTA_Y_MIN, ACM_DELTA_Y_MAX  # "y" and "s" share the same range

    def _smooth_delta_curve(self, curve_key: str) -> None:
        """Apply the comboBox-selected smoothing/fitting to a delta curve.

        ``Linear`` / ``Cubic`` / ``B-Spline`` re-apply the current sample (q)
        values to regenerate the integer-indexed LUT using the chosen
        interpolation method.

        ``Poly-13`` fits a polynomial to the (p, q) sample points
        and evaluate it at every integer H index to produce the smoothed full
        LUT; the sample q values are then resampled from the smoothed curve.

        ``Savitzky-Golay`` applies the SG filter directly to the dense LUT
        and resamples the q values from the filtered curve (SG requires dense
        input and cannot work only on the sparse q set).
        """
        full_lut = getattr(self, f"full_delta_{curve_key}byh")
        if full_lut is None:
            return
        sample_attr = f"sample_values_{curve_key}"
        sample_values = getattr(self, sample_attr, None)
        if self.interp_method in ("Linear", "Cubic", "B-Spline"):
            # Re-apply the current sample values to regenerate the LUT using
            # the chosen interpolation method; sample values stay as-is.
            self._apply_sample_point_change(curve_key)
        elif self.interp_method == "Poly-13":
            # Fit polynomial to the sparse (p, q) sample points and evaluate
            # at every integer H index to produce the smoothed full LUT.
            positions = self.sample_positions
            x = np.array(positions, dtype=np.float32)
            y = np.array(sample_values, dtype=np.float32)
            degree = min(13, len(x) - 1)  # cap to avoid overfitting
            coeffs = np.polyfit(x, y, degree)
            x_full = np.arange(len(full_lut), dtype=np.float32)
            smoothed = np.polyval(coeffs, x_full)
            delta_lo, delta_hi = self._delta_clip_range(curve_key)
            full_lut[:] = np.clip(np.rint(smoothed), delta_lo, delta_hi).astype(np.int16)
            # Resample q values from the smoothed curve.
            if sample_values is not None and positions:
                for i, pos in enumerate(positions):
                    idx = int(round(min(max(pos, 0.0), float(len(smoothed) - 1))))
                    sample_values[i] = float(smoothed[idx])
                sample_values[-1] = sample_values[0]
                self._refresh_sample_overlays()
        else:  # Savitzky-Golay
            smoothed = self._smooth_curve(full_lut, self.interp_method)
            delta_lo, delta_hi = self._delta_clip_range(curve_key)
            full_lut[:] = np.clip(smoothed, delta_lo, delta_hi).astype(np.int16)
            if sample_values is not None and self.sample_positions:
                for i, pos in enumerate(self.sample_positions):
                    idx = int(round(min(max(pos, 0.0), float(len(smoothed) - 1))))
                    sample_values[i] = float(smoothed[idx])
                # Keep the H-cycle closure pair in sync.
                sample_values[-1] = sample_values[0]
                self._refresh_sample_overlays()
        getattr(self, f"delta_chart_{curve_key}").set_values(full_lut)
        self._apply_full_delta_to_acm()
        self._update_lut_visualization()
        self._schedule_auto_run()

    def _current_curve_key(self) -> str:
        """Return ``"y"``, ``"s"`` or ``"h"`` based on the active delta tab."""
        index = self.ui.tabWidget_delta.currentIndex()
        return ("y", "s", "h")[index] if 0 <= index < 3 else "y"

    def _on_reset_curr(self) -> None:
        """Reset the delta curve of the active tab."""
        self._reset_delta_curve(self._current_curve_key())

    def _on_smooth_curr(self) -> None:
        """Polynomial-smooth the delta curve of the active tab."""
        self._smooth_delta_curve(self._current_curve_key())

    def _on_reset_all(self) -> None:
        """Reset the delta curves of all three tabs."""
        for key in ("y", "s", "h"):
            self._reset_delta_curve(key)

    def _on_smooth_all(self) -> None:
        """Polynomial-smooth the delta curves of all three tabs."""
        for key in ("y", "s", "h"):
            self._smooth_delta_curve(key)

    def _on_reset_gain(self) -> None:
        """Reset all Y/S/H gain spinboxes to their default value (256)."""
        for spinbox in (
            self.ui.spinBox_gain_y,
            self.ui.spinBox_gain_s,
            self.ui.spinBox_gain_h,
        ):
            spinbox.setValue(256)

    def _on_reset_offset(self) -> None:
        """Reset all WR/WG/WB offset spinboxes to their default value (256)."""
        for spinbox in (
            self.ui.spinBox_offset_wr,
            self.ui.spinBox_offset_wg,
            self.ui.spinBox_offset_wb,
        ):
            spinbox.setValue(256)
        self._schedule_auto_run()

    # Default LUT lengths per algorithm: (len_y, len_s, len_h, len_h2)
    _DEFAULT_LUT_LENGTHS: dict[str, tuple[int, int, int, int]] = {
        "VOP_VP_ACM": (9, 13, 65, 17),
        "SW_ACM": (9, 13, 65, 65),
        "EVIDEO_ACM": (9, 13, 65, 65),
        "SW_ACM_VARIANT": (9, 13, 65, 65),
    }

    @classmethod
    def _get_default_lut_lengths(cls, algo_name: str) -> tuple[int, int, int, int]:
        """Return the default LUT lengths for a specific ACM algorithm."""
        return cls._DEFAULT_LUT_LENGTHS.get(algo_name, (9, 13, 65, 65))

    def _get_ui_lut_lengths(self) -> tuple[int, int, int, int]:
        """Read the current LUT lengths from the UI controls."""
        return (
            self.ui.spinBox_len_y.value(),
            self.ui.spinBox_len_s.value(),
            self.ui.spinBox_len_h.value(),
            self.ui.spinBox_len_h2.value(),
        )

    def _set_ui_lut_lengths(self, lengths: tuple[int, int, int, int]) -> None:
        """Update all LUT length controls without emitting change notifications."""
        len_y, len_s, len_h, len_h2 = lengths
        self.ui.spinBox_len_h2.setMaximum(len_h)
        self.ui.slider_len_h2.setMaximum(len_h)
        self._set_slider_spin_value(self.ui.slider_len_y, self.ui.spinBox_len_y, len_y)
        self._set_slider_spin_value(self.ui.slider_len_s, self.ui.spinBox_len_s, len_s)
        self._set_slider_spin_value(self.ui.slider_len_h, self.ui.spinBox_len_h, len_h)
        self._set_slider_spin_value(self.ui.slider_len_h2, self.ui.spinBox_len_h2, len_h2)

    def _resolve_target_lut_lengths(self, algo_name: str) -> tuple[int, int, int, int]:
        """Resolve the target LUT lengths based on the group-box checked state."""
        if self.ui.groupBox_lut_lengths.isChecked():
            return self._get_ui_lut_lengths()
        return self._get_default_lut_lengths(algo_name)

    def _resize_delta_arrays_for_len_h(
        self, len_h: int
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray] | None:
        """Resize cached delta arrays to a target ``len_h`` for algorithm switches."""
        if self.full_delta_ybyh is None:
            return None

        if len(self.full_delta_ybyh) == len_h:
            return (
                np.array(self.full_delta_ybyh, dtype=np.int16),
                np.array(self.full_delta_sbyh, dtype=np.int16),
                np.array(self.full_delta_hbyh, dtype=np.int16),
            )

        from script.acm.acm_impl_base import bicubic_resize_array_1d

        return (
            np.clip(
                bicubic_resize_array_1d(self.full_delta_ybyh, len_h),
                ACM_DELTA_Y_MIN,
                ACM_DELTA_Y_MAX,
            ).astype(np.int16),
            np.clip(
                bicubic_resize_array_1d(self.full_delta_sbyh, len_h),
                ACM_DELTA_S_MIN,
                ACM_DELTA_S_MAX,
            ).astype(np.int16),
            np.clip(
                bicubic_resize_array_1d(self.full_delta_hbyh, len_h),
                ACM_DELTA_H_MIN,
                ACM_DELTA_H_MAX,
            ).astype(np.int16),
        )

    def _on_reset_lut_length(self) -> None:
        """Reset all LUT length controls to defaults for the current algorithm."""
        defaults = self._get_default_lut_lengths(self.current_algo)
        self._set_ui_lut_lengths(defaults)
        self._apply_lut_lengths()
        self._sync_ctrl_point_slider(defaults[2])
        self._reload_delta_controls_from_acm()
        # Explicitly rebuild sample-point overlay using the updated
        # ctrl_point_count, in case the slider signal was blocked.
        self._recompute_sample_points(
            self._get_current_acm().len_h, self.ctrl_point_count, force=True)
        self._refresh_sample_overlays()
        self._schedule_auto_run()

    def _on_reset_max_delta(self) -> None:
        """Reset max delta controls to defaults (0.25, 0.25, 64)."""
        self._set_slider_spin_value(
            self.ui.slider_max_delta_y, self.ui.spinBox_max_delta_y, 25)
        self.ui.spinBox_max_delta_y.setValue(0.25)
        self._set_slider_spin_value(
            self.ui.slider_max_delta_s, self.ui.spinBox_max_delta_s, 25)
        self.ui.spinBox_max_delta_s.setValue(0.25)
        self._set_slider_spin_value(
            self.ui.slider_max_delta_h, self.ui.spinBox_max_delta_h, 64)
        self._schedule_auto_run()

    def _on_clip_type_changed(self, text: str) -> None:
        """Apply clip_type change to ACM instance."""
        clip_type = text if text in self._SUPPORTED_CLIP_TYPES else "easy_clip"
        self._get_current_acm().clip_type = clip_type
        self._schedule_auto_run()

    # ------------------------------------------------------------------ #
    # LUT visualization                                                  #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _lut_image_to_pixmap(image: np.ndarray | None) -> QPixmap | None:
        """Convert an RGBA/RGB numpy image from ``dump_luts`` to a pixmap."""
        if image is None or image.size == 0:
            return None
        if image.ndim != 3 or image.shape[2] not in (3, 4):
            return None
        h, w, channels = image.shape
        image = np.ascontiguousarray(image)
        fmt = QImage.Format_RGBA8888 if channels == 4 else QImage.Format_RGB888
        qimage = QImage(image.data, w, h, image.strides[0], fmt).copy()
        return QPixmap.fromImage(qimage)

    def _ensure_lut_image_window(self) -> LutImageWindow:
        """Create the standalone LUT visualization window on first use."""
        if self.lut_image_window is None:
            self.lut_image_window = LutImageWindow(self._on_lut_window_closed)
            host_frame = self._win.frameGeometry()
            screen = self._win.screen() or QGuiApplication.primaryScreen()
            available = screen.availableGeometry() if screen is not None else host_frame
            margin = 12
            window_width = self.lut_image_window.frameGeometry().width()
            window_height = self.lut_image_window.frameGeometry().height()

            right_x = host_frame.right() + margin
            left_x = host_frame.left() - margin - window_width
            if right_x + window_width <= available.right():
                target_x = right_x
            else:
                target_x = max(available.left(), left_x)

            target_y = min(max(host_frame.top(), available.top()), available.bottom() - window_height)
            self.lut_image_window.move(target_x, target_y)
        return self.lut_image_window

    def _on_lut_window_closed(self) -> None:
        """Keep the LUT visualization checkbox in sync when the window is closed manually."""
        if self.ui.checkBox_lut_visualization.isChecked():
            self.ui.checkBox_lut_visualization.blockSignals(True)
            self.ui.checkBox_lut_visualization.setChecked(False)
            self.ui.checkBox_lut_visualization.blockSignals(False)

    def _update_lut_visualization(self) -> None:
        """Refresh the LUT overview image when the standalone window is visible."""
        if self.lut_image_window is None or not self.lut_image_window.isVisible():
            return
        acm = self._get_current_acm()
        if not getattr(acm, "b_lut_ready", False):
            self.lut_image_window.image_label.clear()
            self.lut_image_window.image_label.setText("No LUT")
            return
        pixmap = self._lut_image_to_pixmap(acm.dump_luts(return_image=True))
        if pixmap is None:
            self.lut_image_window.image_label.clear()
            self.lut_image_window.image_label.setText("No LUT")
            return
        self.lut_image_window.image_label.setText("")
        self.lut_image_window.image_label.setPixmap(pixmap)

    # ------------------------------------------------------------------ #
    # ACM processing                                                     #
    # ------------------------------------------------------------------ #

    def _update_acm_gains(self) -> None:
        """Write the current gain controls back to the active ACM instance."""
        self._get_current_acm().gain_y = self.ui.spinBox_gain_y.value()
        self._get_current_acm().gain_s = self.ui.spinBox_gain_s.value()
        self._get_current_acm().gain_h = self.ui.spinBox_gain_h.value()

    def _update_acm_offsets(self) -> None:
        """Write the current WR/WG/WB offset controls back to the active ACM instance."""
        self._get_current_acm().offset_wr = self.ui.spinBox_offset_wr.value()
        self._get_current_acm().offset_wg = self.ui.spinBox_offset_wg.value()
        self._get_current_acm().offset_wb = self.ui.spinBox_offset_wb.value()

    def _update_ignore_gain_luts(self) -> None:
        """Write the current ignore-gain-LUTs checkbox state to the active ACM instance."""
        if hasattr(self.ui, "checkBox_ignore_gain_luts"):
            self._get_current_acm().ignore_gain_luts = bool(self.ui.checkBox_ignore_gain_luts.isChecked())

    def _apply_delta_range_to_acm(self) -> None:
        """Write the current max delta controls back to the active ACM instance."""
        dy = self.ui.spinBox_max_delta_y.value()
        ds = self.ui.spinBox_max_delta_s.value()
        dh = self.ui.spinBox_max_delta_h.value()
        self._get_current_acm().delta_range = (float(dy), float(ds), int(dh))

    def _schedule_auto_run(self) -> None:
        """Debounce ACM processing after UI edits."""
        input_frame = self._input_provider()
        if input_frame is None:
            return
        key = (input_frame.fmt, input_frame.clrspc, input_frame.width, input_frame.height, input_frame.frame_idx)
        if key != self._last_input_key:
            self._last_input_key = key
            self._colorspace_user_override = False
            self._auto_select_colorspace_for_input(input_frame)
        if not self._is_acm_enabled():
            return
        self.auto_run_timer.start(300)

    def _do_auto_run(self) -> None:
        """Run ACM processing and notify parent to refresh output preview."""
        input_frame = self._input_provider()
        if input_frame is None:
            return
        if not self._is_acm_enabled():
            self._status_callback("ACM disabled")
            return

        want_hsv = bool(self.ui.radioButton_colorspace_hsv.isChecked())
        input_is_rgb = bool(input_frame.is_rgb)

        if want_hsv:
            del input_is_rgb
            self._status_callback("HSV ACM path is not implemented yet. Please use YHS.")
            return

        if input_is_rgb:
            y, u, v = rgb_to_yuv(input_frame.pyr, input_frame.pug, input_frame.pvb,
                                 input_cs=input_frame.clrspc if input_frame.clrspc in (0, 1) else 1,
                                 output_cs=5)
            input_planar = np.stack([y, u, v], axis=0)  # [C, H, W]
            input_cs = 5
        else:
            input_planar = np.stack([input_frame.pyr, input_frame.pug, input_frame.pvb], axis=0)
            input_cs = input_frame.clrspc
        input_depth = input_frame.depth
        self._update_acm_gains()
        self._update_acm_offsets()
        self._update_ignore_gain_luts()
        self._apply_delta_range_to_acm()
        self._apply_full_delta_to_acm()
        acm = self._get_current_acm()
        start_time = time.time()
        try:
            if input_depth >= 10 and input_planar.dtype == np.uint16:
                output = acm.do_acm_u10(input_planar)
            else:
                if input_planar.dtype != np.uint8:
                    input_planar = ((input_planar + 2) >> 2).astype(np.uint8)
                output = acm.do_acm_u8(input_planar)
            elapsed_ms = (time.time() - start_time) * 1000.0
            out_fmt = 0x13 if (input_depth >= 10 and output.dtype == np.uint16) else _PLANAR_YUV_8
            out_frame = ImageFrame(
                output[0], output[1], output[2],  # planar [C,H,W]
                out_fmt, input_cs,
            )
            self._output_callback(out_frame)
            self._latest_output_frame = out_frame
            if self._frozen_pixel_x is not None and self._frozen_pixel_y is not None:
                self.update_preview_h_marker(self._frozen_pixel_x, self._frozen_pixel_y)
            self._preview_time_callback(elapsed_ms)
            self._status_callback(f"Processing completed in {elapsed_ms:.2f} ms")
        except Exception as exc:
            print("processing failed:", exc)
            self._status_callback(f"Processing failed: {exc}")

    # ------------------------------------------------------------------ #
    # UI signal handlers                                                 #
    # ------------------------------------------------------------------ #

    def _on_ctrl_points_changed(self, value: int) -> None:
        """Handle sample-point count changes from the ACM widget.

        The chart's ``values`` array stays at ``len_h``; only the positions of
        the floating-point sample points are recomputed. Existing sample
        values are rescaled to the new position grid so the user's edits are
        not destroyed.
        """
        len_h = self._get_current_acm().len_h
        normalized_value = self._normalize_ctrl_point_count(len_h, value)
        if normalized_value != value:
            self.ui.slider_ctrl_points.blockSignals(True)
            self.ui.slider_ctrl_points.setValue(normalized_value)
            self.ui.slider_ctrl_points.blockSignals(False)
        self.ctrl_point_count = normalized_value
        self.ui.label_ctrl_points_value.setText(str(normalized_value))
        self._recompute_sample_points(len_h, normalized_value, force=False)
        self._update_ctrl_point_hint(len_h)

    def _on_interp_method_changed(self, text: str) -> None:
        """Handle interpolation-method changes."""
        self.interp_method = text

    def _on_delta_chart_changed(self, curve_key: str, changed_index: int, values: list[int]) -> None:
        """Forward legacy ``dataChanged`` events to the sample-point handler."""
        del changed_index, values
        # Integer-indexed points are no longer user-editable; this signal is
        # currently unused but kept for API compatibility.

    def _on_acm_colorspace_changed(self, checked: bool = False) -> None:
        """Toggle RGB offset controls when the ACM colorspace selection changes."""
        del checked
        if not self._suppress_colorspace_signal:
            self._colorspace_user_override = True
        is_hsv = self.ui.radioButton_colorspace_hsv.isChecked()
        for widget in (
            self.ui.label_offset_wr,
            self.ui.slider_offset_wr,
            self.ui.spinBox_offset_wr,
            self.ui.label_offset_wg,
            self.ui.slider_offset_wg,
            self.ui.spinBox_offset_wg,
            self.ui.label_offset_wb,
            self.ui.slider_offset_wb,
            self.ui.spinBox_offset_wb,
        ):
            widget.setEnabled(is_hsv)
        self._schedule_auto_run()

    def _on_algo_changed(self, index: int) -> None:
        """Switch the active ACM algorithm, preserving current LUT data.

        The current LUT data (9 tables) and LUT lengths from UI spinboxes
        are written into the new instance before switching, so delta charts
        stay unchanged and the new instance picks up the current edits.
        """
        new_algo = self._ALGO_KEYS[index]
        if new_algo == self.current_algo:
            return

        # Snapshot current UI state before switching
        old_acm = self._get_current_acm()
        target_len = self._resolve_target_lut_lengths(new_algo)
        resized_deltas = self._resize_delta_arrays_for_len_h(target_len[2])

        # Switch to new instance
        self.current_algo = new_algo
        new_acm = self._get_current_acm()
        self._set_ui_lut_lengths(target_len)

        # Apply target lengths to the new instance.
        if target_len != (new_acm.len_y, new_acm.len_s, new_acm.len_h, new_acm.len_hd):
            new_acm.set_len(*target_len)

        # Copy current delta chart data into the new instance, resizing when
        # the target algorithm uses a different len_h.
        if resized_deltas is not None:
            new_acm.lut_delta_ybyh[:] = resized_deltas[0]
            new_acm.lut_delta_sbyh[:] = resized_deltas[1]
            new_acm.lut_delta_hbyh[:] = resized_deltas[2]

        # Copy gain LUTs from old to new (resize if needed)
        for name_2d in ('ybyy', 'sbyy', 'hbyy', 'ybys', 'sbys', 'hbys'):
            src = getattr(old_acm, f'lut_gain_{name_2d}')
            dst = getattr(new_acm, f'lut_gain_{name_2d}')
            if src.shape == dst.shape:
                dst[:] = src
            else:
                from script.acm.acm_impl_base import bicubic_resize_array_2d
                resampled = bicubic_resize_array_2d(src, dst.shape[0], dst.shape[1])
                dst[:] = resampled
                print(f"[ACM] resampled gain_{name_2d}: {src.shape} => {dst.shape}")
        # Sync active tables back to default tables, so the gain data survives
        # future LUT length changes (set_len / set_step).
        new_acm.sync_to_default()

        # Copy misc state
        new_acm.gain_y = old_acm.gain_y
        new_acm.gain_s = old_acm.gain_s
        new_acm.gain_h = old_acm.gain_h
        new_acm.offset_wr = old_acm.offset_wr
        new_acm.offset_wg = old_acm.offset_wg
        new_acm.offset_wb = old_acm.offset_wb
        new_acm.ignore_gain_luts = old_acm.ignore_gain_luts
        # new_acm.delta_range = old_acm.delta_range
        new_acm.clip_type = old_acm.clip_type if old_acm.clip_type in self._SUPPORTED_CLIP_TYPES else "easy_clip"

        # Refresh UI controls while keeping the in-memory delta editor state.
        self._refresh_acm_ui_controls()
        if resized_deltas is not None:
            self.full_delta_ybyh = np.array(resized_deltas[0], dtype=np.int16)
            self.full_delta_sbyh = np.array(resized_deltas[1], dtype=np.int16)
            self.full_delta_hbyh = np.array(resized_deltas[2], dtype=np.int16)
            self.delta_chart_y.set_values(self.full_delta_ybyh)
            self.delta_chart_s.set_values(self.full_delta_sbyh)
            self.delta_chart_h.set_values(self.full_delta_hbyh)
            self._recompute_sample_points(target_len[2], self.ctrl_point_count, force=False)
            self._refresh_sample_overlays()
        self._update_lut_visualization()
        self._schedule_auto_run()

    def _on_lut_lengths_group_toggled(self, checked: bool) -> None:
        """Synchronize LUT lengths when the override group checked state changes."""
        del checked
        target_lengths = self._resolve_target_lut_lengths(self.current_algo)
        self._set_ui_lut_lengths(target_lengths)
        self._apply_lut_lengths()
        self._sync_ctrl_point_slider(target_lengths[2])
        self._reload_delta_controls_from_acm()
        self._schedule_auto_run()

    def _on_len_h_changed(self, value: int) -> None:
        """Refresh the delta editor after len_h changes."""
        # Clamp len_h2 max so it cannot exceed len_h.
        self.ui.spinBox_len_h2.setMaximum(value)
        self.ui.slider_len_h2.setMaximum(value)
        self._apply_lut_lengths()
        self._sync_ctrl_point_slider(value)
        self._reload_delta_controls_from_acm()
        self._schedule_auto_run()

    def _on_lut_lengths_changed(self, value: int) -> None:
        """Handle LUT length changes for Y / S / HD (non-H) sliders.

        Only the 2D gain tables are affected by Y/S/HD length changes —
        the 1D delta LUTs are left untouched so the chart stays stable.
        """
        del value
        self._apply_lut_lengths()
        self._update_lut_visualization()
        self._schedule_auto_run()

    def _on_ignore_gain_luts_toggled(self, checked: bool) -> None:
        """Toggle whether the active ACM instance ignores the six 2D gain LUTs."""
        self._get_current_acm().ignore_gain_luts = bool(checked)
        self._schedule_auto_run()

    # ------------------------------------------------------------------ #
    # Config persistence                                                 #
    # ------------------------------------------------------------------ #

    def _refresh_acm_ui_from_current_acm(self) -> None:
        """Refresh the ACM widget controls from the active ACM instance.

        This reloads delta chart data from the instance — use
        :meth:`_refresh_acm_ui_controls` for algorithm switches where
        chart data should be preserved.
        """
        self._refresh_acm_ui_controls()
        self._reload_delta_controls_from_acm()

    def _refresh_acm_ui_controls(self) -> None:
        """Refresh UI spinboxes/combos from the active ACM instance,
        without touching delta chart data.
        """
        acm = self._get_current_acm()
        self.ui.groupBox_lut_lengths.setEnabled(True)
        self._set_slider_spin_value(self.ui.slider_len_y, self.ui.spinBox_len_y, acm.len_y)
        self._set_slider_spin_value(self.ui.slider_len_s, self.ui.spinBox_len_s, acm.len_s)
        self._set_slider_spin_value(self.ui.slider_len_h, self.ui.spinBox_len_h, acm.len_h)
        self.ui.spinBox_len_h2.setMaximum(acm.len_h)
        self.ui.slider_len_h2.setMaximum(acm.len_h)
        self._set_slider_spin_value(self.ui.slider_len_h2, self.ui.spinBox_len_h2, acm.len_hd)
        self._set_slider_spin_value(self.ui.slider_gain_y, self.ui.spinBox_gain_y, acm.gain_y)
        self._set_slider_spin_value(self.ui.slider_gain_s, self.ui.spinBox_gain_s, acm.gain_s)
        self._set_slider_spin_value(self.ui.slider_gain_h, self.ui.spinBox_gain_h, acm.gain_h)
        if hasattr(self.ui, "checkBox_ignore_gain_luts"):
            self.ui.checkBox_ignore_gain_luts.blockSignals(True)
            self.ui.checkBox_ignore_gain_luts.setChecked(bool(getattr(acm, "ignore_gain_luts", False)))
            self.ui.checkBox_ignore_gain_luts.blockSignals(False)
        self._set_slider_spin_value(self.ui.slider_offset_wr, self.ui.spinBox_offset_wr, acm.offset_wr)
        self._set_slider_spin_value(self.ui.slider_offset_wg, self.ui.spinBox_offset_wg, acm.offset_wg)
        self._set_slider_spin_value(self.ui.slider_offset_wb, self.ui.spinBox_offset_wb, acm.offset_wb)
        dr = getattr(acm, 'delta_range', (0.25, 0.25, 64))
        self.ui.spinBox_max_delta_y.setValue(dr[0])
        self.ui.spinBox_max_delta_s.setValue(dr[1])
        self.ui.spinBox_max_delta_h.setValue(dr[2])
        ct = getattr(acm, 'clip_type', 'easy_clip')
        if ct not in self._SUPPORTED_CLIP_TYPES:
            ct = "easy_clip"
            acm.clip_type = ct
        idx = self.ui.comboBox_clip_type.findText(ct)
        if idx >= 0:
            self.ui.comboBox_clip_type.setCurrentIndex(idx)
        self._sync_clip_type_ui_state()
        self._sync_ctrl_point_slider(acm.len_h)
        self._update_lut_visualization()

    def load_current_config(self, path: str) -> bool:
        """Load a JSON config into the active ACM instance and refresh the UI."""
        if not path or not os.path.isfile(path):
            QMessageBox.warning(None, "Warning", "Please select a valid config file")
            return False

        try:
            self._get_current_acm().load_json(path)
            self._config_path_setter(path)
            self._refresh_acm_ui_from_current_acm()
            self._schedule_auto_run()
            self._status_callback(f"Config loaded: {path}")
            return True
        except Exception as exc:
            QMessageBox.critical(None, "Error", f"Failed to load config: {exc}")
            return False

    def _on_save_config(self) -> None:
        """Save the current ACM configuration to a JSON file."""
        acm = self._get_current_acm()
        if not acm.b_lut_ready:
            QMessageBox.warning(None, "Warning", "No LUT data to save")
            return
        path, _ = QFileDialog.getSaveFileName(None, "Save Config", "", "JSON Files (*.json)")
        if path:
            if not path.endswith(".json"):
                path += ".json"
            acm.sync_to_default()
            acm.dump_json(path)
            self._status_callback(f"Config saved: {path}")

    def _on_read_config(self) -> None:
        """Browse and load an ACM configuration from the ACM editor tab."""
        current_path = self._config_path_getter()
        start_dir = os.path.dirname(current_path) if current_path else ""
        path, _ = QFileDialog.getOpenFileName(None, "Read Config", start_dir, "JSON Files (*.json)")
        if path:
            self.load_current_config(path)

    def _on_lut_visualization_toggled(self, checked: bool) -> None:
        """Show or close the standalone LUT overview window."""
        if checked:
            window = self._ensure_lut_image_window()
            window.show()
            window.raise_()
            window.activateWindow()
            self._update_lut_visualization()
        elif self.lut_image_window is not None and self.lut_image_window.isVisible():
            self.lut_image_window.close()
