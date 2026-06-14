"""
ACM tab controller — encapsulates all ACM-related UI behavior and state.
"""

from collections.abc import Callable
import os
import time

import numpy as np
from PySide6.QtCore import QRect, QTimer, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QDockWidget,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

try:
    from ..ui_gen.acm_ui import Ui_AcmUiWidget
except ImportError:
    from ui_gen.acm_ui import Ui_AcmUiWidget


class AcmUiWidget(QWidget):
    """Reusable ACM configuration widget."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create the ACM widget from the generated UI definition."""
        super().__init__(parent)
        self.ui = Ui_AcmUiWidget()
        self.ui.setupUi(self)


class SingleCurveChartWidget(QWidget):
    """Interactive single-curve chart for one H-based delta LUT."""

    dataChanged = Signal(int, list)

    def __init__(
        self,
        value_range: tuple[int, int],
        curve_color: QColor,
        parent: QWidget | None = None,
    ) -> None:
        """Create a chart widget with a configurable value range and color."""
        super().__init__(parent)
        self.setMinimumSize(600, 200)
        self.setMaximumSize(1200, 400)
        self.value_range = value_range
        self.curve_color = curve_color
        self.values = [0, 0, 0, 0]
        self.padding = 40
        self.dragging_point = None
        self.hover_point = None

    def set_num_points(self, count: int) -> None:
        """Resize the control-point list while preserving existing values."""
        if count <= 0:
            return
        if len(self.values) < count:
            self.values.extend([self.values[-1] if self.values else 0] * (count - len(self.values)))
        elif len(self.values) > count:
            self.values = self.values[:count]
        if len(self.values) > 1:
            self.values[-1] = self.values[0]
        self.update()

    def set_values(self, values: list[int] | np.ndarray) -> None:
        """Replace the chart values and repaint."""
        self.values = [int(v) for v in values]
        if len(self.values) > 1:
            self.values[-1] = self.values[0]
        self.update()

    def get_values(self) -> list[int]:
        """Return the chart values with the H-cycle closure applied."""
        if not self.values:
            return []
        result = list(self.values)
        result[-1] = result[0]
        return result

    def _value_to_y(self, value: int | float) -> float:
        """Map a chart value to widget coordinates."""
        value_min, value_max = self.value_range
        chart_height = self.height() - 2 * self.padding
        ratio = (value - value_min) / (value_max - value_min)
        return self.padding + chart_height * (1 - ratio)

    def _point_position(self, index: int) -> tuple[float, float]:
        """Return the widget-space position for a control point."""
        chart_width = self.width() - 2 * self.padding
        x_pos = self.padding
        if len(self.values) > 1:
            x_pos = self.padding + chart_width * index / (len(self.values) - 1)
        y_pos = self._value_to_y(self.values[index])
        return x_pos, y_pos

    def paintEvent(self, event: object) -> None:
        """Paint the chart background, line, and control points."""
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        width = self.width()
        height = self.height()
        chart_width = width - 2 * self.padding
        chart_height = height - 2 * self.padding
        painter.fillRect(self.rect(), QColor(30, 30, 30))
        painter.setPen(QPen(QColor(60, 60, 60), 1))
        for idx in range(9):
            y_pos = self.padding + chart_height * idx / 8
            painter.drawLine(self.padding, int(y_pos), width - self.padding, int(y_pos))
        painter.setPen(QPen(QColor(100, 100, 100), 2, Qt.DashLine))
        mid_y = self._value_to_y(0)
        painter.drawLine(self.padding, int(mid_y), width - self.padding, int(mid_y))
        painter.setPen(QPen(self.curve_color, 2))
        for idx in range(len(self.values) - 1):
            x1, y1 = self._point_position(idx)
            x2, y2 = self._point_position(idx + 1)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
        for idx in range(len(self.values)):
            x_pos, y_pos = self._point_position(idx)
            if idx == self.hover_point or idx == self.dragging_point:
                painter.setBrush(self.curve_color.lighter(150))
                painter.setPen(QPen(Qt.white, 2))
                painter.drawEllipse(int(x_pos) - 6, int(y_pos) - 6, 12, 12)
            else:
                painter.setBrush(self.curve_color)
                painter.setPen(QPen(self.curve_color.darker(130), 1))
                painter.drawEllipse(int(x_pos) - 4, int(y_pos) - 4, 8, 8)
        painter.setPen(QColor(200, 200, 200))
        font = painter.font()
        font.setPointSize(9)
        painter.setFont(font)
        for value in (self.value_range[1], 0, self.value_range[0]):
            painter.drawText(5, int(self._value_to_y(value) + 4), str(value))
        for idx, value in enumerate(self.values):
            x_pos, y_pos = self._point_position(idx)
            text_rect = QRect(int(x_pos) - 24, int(y_pos) - 26, 48, 16)
            painter.drawText(text_rect, Qt.AlignCenter, str(int(value)))

    def mousePressEvent(self, event: object) -> None:
        """Start dragging the nearest control point."""
        if event.button() != Qt.LeftButton:
            return
        point = self._find_nearest_point(event.position().x(), event.position().y())
        if point is not None:
            self.dragging_point = point
            self.update()

    def mouseMoveEvent(self, event: object) -> None:
        """Update hover or dragging state for the chart."""
        x_pos = event.position().x()
        y_pos = event.position().y()
        if self.dragging_point is not None:
            chart_height = self.height() - 2 * self.padding
            ratio = 1 - (y_pos - self.padding) / chart_height
            ratio = max(0.0, min(1.0, ratio))
            value_min, value_max = self.value_range
            self.values[self.dragging_point] = int(value_min + ratio * (value_max - value_min))
            if self.dragging_point in (0, len(self.values) - 1) and len(self.values) > 1:
                paired_index = len(self.values) - 1 if self.dragging_point == 0 else 0
                self.values[paired_index] = self.values[self.dragging_point]
            self.dataChanged.emit(self.dragging_point, self.get_values())
            self.update()
        else:
            hover_point = self._find_nearest_point(x_pos, y_pos)
            if hover_point != self.hover_point:
                self.hover_point = hover_point
                self.update()

    def mouseReleaseEvent(self, event: object) -> None:
        """Stop dragging a control point."""
        if event.button() == Qt.LeftButton:
            self.dragging_point = None
            self.update()

    def _find_nearest_point(self, x_pos: float, y_pos: float) -> int | None:
        """Return the nearest control point index within the hit threshold."""
        threshold = 15
        for idx in range(len(self.values)):
            point_x, point_y = self._point_position(idx)
            distance = ((x_pos - point_x) ** 2 + (y_pos - point_y) ** 2) ** 0.5
            if distance < threshold:
                return idx
        return None


class HeatmapWidget(QWidget):
    """Simple heatmap widget for ACM LUT visualization."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create an empty heatmap widget."""
        super().__init__(parent)
        self.setMinimumSize(160, 120)
        self.data = None
        self.value_min = -128
        self.value_max = 127

    def set_data(self, data: np.ndarray | None, value_min: int = -128, value_max: int = 127) -> None:
        """Update the heatmap data and repaint."""
        self.data = None if data is None else np.array(data, copy=True)
        self.value_min = value_min
        self.value_max = value_max
        self.update()

    def paintEvent(self, event: object) -> None:
        """Paint the heatmap or a placeholder background."""
        del event
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(30, 30, 30))
        if self.data is None or self.data.size == 0:
            painter.setPen(QColor(180, 180, 180))
            painter.drawText(self.rect(), Qt.AlignCenter, "No LUT")
            return
        rows, cols = self.data.shape
        cell_w = self.width() / max(cols, 1)
        cell_h = self.height() / max(rows, 1)
        for row in range(rows):
            for col in range(cols):
                raw_value = int(self.data[row, col])
                display_value = min(abs(raw_value) * 2, 255)
                norm = max(0.0, min(1.0, display_value / 255.0))
                if raw_value < 0:
                    color = QColor(
                        int(30 + 70 * norm),
                        int(70 + 110 * norm),
                        int(110 + 145 * norm),
                    )
                else:
                    gray = int(40 + 190 * norm)
                    color = QColor(gray, gray, gray)
                painter.fillRect(
                    int(col * cell_w),
                    int(row * cell_h),
                    max(1, int(cell_w + 1)),
                    max(1, int(cell_h + 1)),
                    color,
                )


class AcmUiController:
    """Controls the ACM tab: algorithm selection, delta editing, heatmaps, and LUT viz."""

    # ------------------------------------------------------------------ #
    # Initialization                                                     #
    # ------------------------------------------------------------------ #

    def __init__(
        self,
        acm_widget: AcmUiWidget,
        parent_window: QMainWindow | None = None,
        input_provider: Callable[[], np.ndarray | None] | None = None,
        output_callback: Callable[[np.ndarray], None] | None = None,
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
            dock_host: Optional QMainWindow used to host the LUT visualization dock.
        """
        self._win = parent_window
        self._dock_host = dock_host or parent_window
        self.widget = acm_widget
        self.ui = acm_widget.ui
        self._input_provider = input_provider or (lambda: None)
        self._output_callback = output_callback or (lambda output: None)
        self._preview_time_callback = preview_time_callback or (lambda elapsed_ms: None)
        self._status_callback = status_callback or (lambda message: None)
        self._config_path_getter = config_path_getter or (lambda: "")
        self._config_path_setter = config_path_setter or (lambda path: None)

        # --- ACM algorithm instances ---
        from script.acm.acm_impls import AcmImplHwRk, AcmImplSwRk, AcmImplSwEvideo, AcmImplSwVariant

        self.acm_instances = {
            "VOP_VP_ACM": AcmImplHwRk(),
            "SW_ACM": AcmImplSwRk(),
            "EVIDEO_ACM": AcmImplSwEvideo(),
            "SW_ACM_VARIANT": AcmImplSwVariant(),
        }
        self.current_algo = "VOP_VP_ACM"

        # --- Delta chart state ---
        self.full_delta_ybyh = None
        self.full_delta_sbyh = None
        self.full_delta_hbyh = None
        self.ctrl_point_count = self.ui.slider_ctrl_points.value()
        self.interp_method = self.ui.comboBox_interp_method.currentText()

        # --- Chart widgets (hosted inside ACM tab) ---
        self.delta_chart_y = SingleCurveChartWidget((-255, 255), QColor(255, 200, 0))
        self.delta_chart_s = SingleCurveChartWidget((-255, 255), QColor(0, 180, 0))
        self.delta_chart_h = SingleCurveChartWidget((-64, 64), QColor(0, 100, 255))
        for host, chart in (
            (self.ui.widget_delta_y_host, self.delta_chart_y),
            (self.ui.widget_delta_s_host, self.delta_chart_s),
            (self.ui.widget_delta_h_host, self.delta_chart_h),
        ):
            layout = QVBoxLayout(host)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(chart)

        # --- Heatmap widgets ---
        self.heatmap_widgets = {}
        for key, host in (
            ("gain_ybyy", self.ui.widget_gain_ybyy_host),
            ("gain_sbyy", self.ui.widget_gain_sbyy_host),
            ("gain_hbyy", self.ui.widget_gain_hbyy_host),
            ("gain_ybys", self.ui.widget_gain_ybys_host),
            ("gain_sbys", self.ui.widget_gain_sbys_host),
            ("gain_hbys", self.ui.widget_gain_hbys_host),
        ):
            heatmap = HeatmapWidget()
            layout = QVBoxLayout(host)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(heatmap)
            self.heatmap_widgets[key] = heatmap

        # --- Auto-run debounce timer ---
        self.auto_run_timer = QTimer(self.widget)
        self.auto_run_timer.setSingleShot(True)
        self.auto_run_timer.timeout.connect(self._do_auto_run)

        # --- LUT dock (lazy) ---
        self.lut_dock = None
        self._lut_gb_original_layout = None

        # Hide LUT Visualization groupBox by default
        self.ui.groupBox_lut_visualization.setVisible(False)

        self._connect_signals()
        self._init_state()

    def _init_state(self) -> None:
        """Perform initial state sync after all widgets are ready."""
        self._on_acm_colorspace_changed()
        self._sync_ctrl_point_slider(self._get_current_acm().len_h)
        self._reload_delta_controls_from_acm()

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
        ui.checkBox_lut_visualization.toggled.connect(self._on_lut_visualization_toggled)
        ui.spinBox_len_h.valueChanged.connect(self._on_len_h_changed)
        ui.spinBox_len_y.valueChanged.connect(self._on_variant_lengths_changed)
        ui.spinBox_len_s.valueChanged.connect(self._on_variant_lengths_changed)
        ui.spinBox_len_h2.valueChanged.connect(self._on_variant_lengths_changed)
        ui.button_reset_delta_y.clicked.connect(lambda: self._reset_delta_curve("y"))
        ui.button_reset_delta_s.clicked.connect(lambda: self._reset_delta_curve("s"))
        ui.button_reset_delta_h.clicked.connect(lambda: self._reset_delta_curve("h"))
        ui.pushButton_read_config.clicked.connect(self._on_read_config)
        ui.pushButton_save_config.clicked.connect(self._on_save_config)
        self._connect_slider_spin(ui.slider_gain_y, ui.spinBox_gain_y)
        self._connect_slider_spin(ui.slider_gain_s, ui.spinBox_gain_s)
        self._connect_slider_spin(ui.slider_gain_h, ui.spinBox_gain_h)
        self._connect_slider_spin(ui.slider_offset_wr, ui.spinBox_offset_wr)
        self._connect_slider_spin(ui.slider_offset_wg, ui.spinBox_offset_wg)
        self._connect_slider_spin(ui.slider_offset_wb, ui.spinBox_offset_wb)
        ui.slider_gain_y.valueChanged.connect(self._schedule_auto_run)
        ui.slider_gain_s.valueChanged.connect(self._schedule_auto_run)
        ui.slider_gain_h.valueChanged.connect(self._schedule_auto_run)
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

    def _apply_variant_lengths(self) -> None:
        """Apply custom LUT lengths when the variant ACM is active."""
        if self.current_algo != "SW_ACM_VARIANT":
            return
        variant_acm = self._get_current_acm()
        variant_acm.set_len_variant(
            self.ui.spinBox_len_y.value(),
            self.ui.spinBox_len_s.value(),
            self.ui.spinBox_len_h.value(),
            self.ui.spinBox_len_h2.value(),
        )

    # ------------------------------------------------------------------ #
    # Control-point logic                                                #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _normalize_ctrl_point_count(len_h: int, value: int) -> int:
        """Clamp the control-point count to the valid even range."""
        max_even = len_h if len_h % 2 == 0 else len_h - 1
        max_even = max(4, max_even)
        value = max(4, min(value, max_even))
        if value % 2 != 0:
            value -= 1
        return max(4, value)

    def _update_ctrl_point_hint(self, len_h: int) -> None:
        """Refresh the displayed control-point hint text."""
        step = (len_h - 1) / max(1, self.ctrl_point_count - 1)
        self.ui.label_delta_hint.setText(f"(len_h = {len_h}, step = {step:.1f})")

    def _get_ctrl_positions(self, len_h: int) -> np.ndarray:
        """Return the H positions corresponding to the current control points."""
        return np.linspace(0.0, len_h - 1, self.ctrl_point_count)

    def _sync_ctrl_point_slider(self, len_h: int) -> None:
        """Update the control-point slider bounds for the current len_h."""
        max_even = self._normalize_ctrl_point_count(len_h, len_h)
        new_value = self._normalize_ctrl_point_count(len_h, self.ctrl_point_count)
        self.ctrl_point_count = new_value
        self.ui.slider_ctrl_points.blockSignals(True)
        self.ui.slider_ctrl_points.setRange(4, max_even)
        self.ui.slider_ctrl_points.setSingleStep(2)
        self.ui.slider_ctrl_points.setPageStep(2)
        self.ui.slider_ctrl_points.setValue(new_value)
        self.ui.slider_ctrl_points.blockSignals(False)
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
        self._resample_full_to_ctrl()

    def _resample_full_to_ctrl(self) -> None:
        """Resample the current full LUTs down to the editable control points."""
        point_count = self.ctrl_point_count
        for chart in (self.delta_chart_y, self.delta_chart_s, self.delta_chart_h):
            chart.set_num_points(point_count)
        if self.full_delta_ybyh is None:
            zero_values = [0] * point_count
            self.delta_chart_y.set_values(zero_values)
            self.delta_chart_s.set_values(zero_values)
            self.delta_chart_h.set_values(zero_values)
            return
        x_src = np.arange(len(self.full_delta_ybyh), dtype=np.float32)
        x_dst = self._get_ctrl_positions(len(self.full_delta_ybyh))
        self.delta_chart_y.set_values(np.interp(x_dst, x_src, self.full_delta_ybyh))
        self.delta_chart_s.set_values(np.interp(x_dst, x_src, self.full_delta_sbyh))
        self.delta_chart_h.set_values(np.interp(x_dst, x_src, self.full_delta_hbyh))

    def _interpolate_segment(
        self,
        x_points: list[float] | np.ndarray,
        y_points: list[float] | np.ndarray,
        x_targets: list[float] | np.ndarray,
    ) -> np.ndarray:
        """Interpolate a local segment using the selected interpolation method."""
        x_points = np.array(x_points, dtype=np.float32)
        y_points = np.array(y_points, dtype=np.float32)
        x_targets = np.array(x_targets, dtype=np.float32)
        if x_targets.size == 0:
            return np.array([], dtype=np.float32)
        if self.interp_method == "Linear" or len(x_points) < 3:
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

    def _apply_local_curve_change(self, curve_key: str, changed_index: int) -> None:
        """Apply a local control-point edit back to the corresponding full LUT array."""
        full_lut = getattr(self, f"full_delta_{curve_key}byh")
        if full_lut is None:
            return
        chart = getattr(self, f"delta_chart_{curve_key}")
        ctrl_values = np.array(chart.get_values(), dtype=np.float32)
        len_h = len(full_lut)
        ctrl_x = self._get_ctrl_positions(len_h)
        point_count = len(ctrl_values)
        if point_count < 2:
            return

        if changed_index in (0, point_count - 1):
            ctrl_values[0] = ctrl_values[-1] = ctrl_values[0]
            right_index = 1
            left_index = point_count - 2
            right_targets = np.arange(1, int(np.floor(ctrl_x[right_index])), dtype=np.int32)
            left_targets = np.arange(int(np.ceil(ctrl_x[left_index])) + 1, len_h - 1, dtype=np.int32)
            if left_targets.size:
                left_values = self._interpolate_segment(
                    [ctrl_x[left_index], len_h - 1],
                    [ctrl_values[left_index], ctrl_values[0]],
                    left_targets,
                )
                full_lut[left_targets] = np.rint(left_values).astype(np.int16)
            if right_targets.size:
                right_values = self._interpolate_segment(
                    [0, ctrl_x[right_index]],
                    [ctrl_values[0], ctrl_values[right_index]],
                    right_targets,
                )
                full_lut[right_targets] = np.rint(right_values).astype(np.int16)
            endpoint_value = np.int16(round(ctrl_values[0]))
            full_lut[0] = endpoint_value
            full_lut[-1] = endpoint_value
            return

        left_index = changed_index - 1
        right_index = changed_index + 1
        target_indices = np.arange(
            int(np.ceil(ctrl_x[left_index])) + 1,
            int(np.floor(ctrl_x[right_index])),
            dtype=np.int32,
        )
        if target_indices.size:
            segment_values = self._interpolate_segment(
                [ctrl_x[left_index], ctrl_x[changed_index], ctrl_x[right_index]],
                [ctrl_values[left_index], ctrl_values[changed_index], ctrl_values[right_index]],
                target_indices,
            )
            full_lut[target_indices] = np.rint(segment_values).astype(np.int16)
        changed_full_index = int(round(ctrl_x[changed_index]))
        changed_full_index = max(0, min(len_h - 1, changed_full_index))
        full_lut[changed_full_index] = np.int16(round(ctrl_values[changed_index]))

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
        getattr(self, f"delta_chart_{curve_key}").set_values([0] * self.ctrl_point_count)
        self._apply_full_delta_to_acm()
        self._update_heatmaps()
        self._schedule_auto_run()

    # ------------------------------------------------------------------ #
    # Heatmap refresh                                                    #
    # ------------------------------------------------------------------ #

    def _update_heatmaps(self) -> None:
        """Refresh the mounted LUT heatmap widgets."""
        acm = self._get_current_acm()
        if not getattr(acm, "b_lut_ready", False):
            return
        lut_map = {
            "gain_ybyy": acm.lut_gain_ybyy,
            "gain_sbyy": acm.lut_gain_sbyy,
            "gain_hbyy": acm.lut_gain_hbyy,
            "gain_ybys": acm.lut_gain_ybys,
            "gain_sbys": acm.lut_gain_sbys,
            "gain_hbys": acm.lut_gain_hbys,
        }
        for key, data in lut_map.items():
            if key in self.heatmap_widgets:
                self.heatmap_widgets[key].set_data(data, -128, 127)

    # ------------------------------------------------------------------ #
    # ACM processing                                                     #
    # ------------------------------------------------------------------ #

    def _update_acm_gains(self) -> None:
        """Write the current gain controls back to the active ACM instance."""
        self._get_current_acm().set_gain(
            self.ui.spinBox_gain_y.value(),
            self.ui.spinBox_gain_s.value(),
            self.ui.spinBox_gain_h.value(),
        )

    def _schedule_auto_run(self) -> None:
        """Debounce ACM processing after UI edits."""
        if self._input_provider() is None:
            return
        self.auto_run_timer.start(300)

    def _do_auto_run(self) -> None:
        """Run ACM processing and notify parent to refresh output preview."""
        input_data = self._input_provider()
        if input_data is None:
            return
        self._apply_variant_lengths()
        self._update_acm_gains()
        self._apply_full_delta_to_acm()
        acm = self._get_current_acm()
        start_time = time.time()
        try:
            output = acm.do_acm_u8(
                input_data,
                self.ui.checkBox_use_cordic.isChecked(),
            )
            elapsed_ms = (time.time() - start_time) * 1000.0
            self._output_callback(output)
            self._preview_time_callback(elapsed_ms)
            self._update_heatmaps()
            self._status_callback(f"Processing completed in {elapsed_ms:.2f} ms")
        except Exception as exc:
            self._status_callback(f"Processing failed: {exc}")

    # ------------------------------------------------------------------ #
    # UI signal handlers                                                 #
    # ------------------------------------------------------------------ #

    def _on_ctrl_points_changed(self, value: int) -> None:
        """Handle control-point count changes from the ACM widget."""
        normalized_value = self._normalize_ctrl_point_count(self._get_current_acm().len_h, value)
        if normalized_value != value:
            self.ui.slider_ctrl_points.blockSignals(True)
            self.ui.slider_ctrl_points.setValue(normalized_value)
            self.ui.slider_ctrl_points.blockSignals(False)
        self.ctrl_point_count = normalized_value
        self.ui.label_ctrl_points_value.setText(str(normalized_value))
        self._update_ctrl_point_hint(self._get_current_acm().len_h)
        self._resample_full_to_ctrl()

    def _on_interp_method_changed(self, text: str) -> None:
        """Handle interpolation-method changes."""
        self.interp_method = text

    def _on_delta_chart_changed(self, curve_key: str, changed_index: int, values: list[int]) -> None:
        """Handle edits from any delta chart widget."""
        del values
        self._apply_local_curve_change(curve_key, changed_index)
        self._apply_full_delta_to_acm()
        self._schedule_auto_run()

    def _on_acm_colorspace_changed(self, checked: bool = False) -> None:
        """Toggle RGB offset controls when the ACM colorspace selection changes."""
        del checked
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

    def _on_algo_changed(self, index: int) -> None:
        """Switch the active ACM algorithm and refresh the editor state."""
        algo_names = ["VOP_VP_ACM", "SW_ACM", "EVIDEO_ACM", "SW_ACM_VARIANT"]
        self.current_algo = algo_names[index]
        self._refresh_acm_ui_from_current_acm()
        self._schedule_auto_run()

    def _on_len_h_changed(self, value: int) -> None:
        """Refresh the delta editor after the variant len_h value changes."""
        if self.current_algo != "SW_ACM_VARIANT":
            return
        self._apply_variant_lengths()
        self._sync_ctrl_point_slider(value)
        self._reload_delta_controls_from_acm()
        self._schedule_auto_run()

    def _on_variant_lengths_changed(self, value: int) -> None:
        """Handle non-h variant length changes."""
        del value
        if self.current_algo != "SW_ACM_VARIANT":
            return
        self._apply_variant_lengths()
        self._schedule_auto_run()

    # ------------------------------------------------------------------ #
    # Config persistence                                                 #
    # ------------------------------------------------------------------ #

    def _refresh_acm_ui_from_current_acm(self) -> None:
        """Refresh the ACM widget controls from the active ACM instance."""
        acm = self._get_current_acm()
        is_variant = self.current_algo == "SW_ACM_VARIANT"
        self.ui.groupBox_lut_lengths.setEnabled(is_variant)
        self._set_spinbox_value(self.ui.spinBox_len_y, acm.len_y)
        self._set_spinbox_value(self.ui.spinBox_len_s, acm.len_s)
        self._set_spinbox_value(self.ui.spinBox_len_h, acm.len_h)
        self._set_spinbox_value(self.ui.spinBox_len_h2, acm.len_h2)
        self._set_slider_spin_value(self.ui.slider_gain_y, self.ui.spinBox_gain_y, acm.gain_y)
        self._set_slider_spin_value(self.ui.slider_gain_s, self.ui.spinBox_gain_s, acm.gain_s)
        self._set_slider_spin_value(self.ui.slider_gain_h, self.ui.spinBox_gain_h, acm.gain_h)
        self._sync_ctrl_point_slider(acm.len_h)
        self._reload_delta_controls_from_acm()
        self._update_heatmaps()

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
            acm.dump_json(path)
            self._status_callback(f"Config saved: {path}")

    def _on_read_config(self) -> None:
        """Browse and load an ACM configuration from the ACM editor tab."""
        current_path = self._config_path_getter()
        start_dir = os.path.dirname(current_path) if current_path else ""
        path, _ = QFileDialog.getOpenFileName(None, "Read Config", start_dir, "JSON Files (*.json)")
        if path:
            self.load_current_config(path)

    # ------------------------------------------------------------------ #
    # LUT Visualization dock                                             #
    # ------------------------------------------------------------------ #

    def _on_lut_visualization_toggled(self, checked: bool):
        """Detach or re-attach groupBox_lut_visualization to a standalone dock."""
        if self._dock_host is None:
            return
        gb = self.ui.groupBox_lut_visualization

        if checked:
            gb.setVisible(False)
            self._lut_gb_original_layout = gb.parent().layout()
            self.lut_dock = QDockWidget("LUT Visualization", self._dock_host)
            self.lut_dock.setObjectName("lut_visualization_dock")
            self.lut_dock.setAllowedAreas(Qt.AllDockWidgetAreas)
            self.lut_dock.setFeatures(
                QDockWidget.DockWidgetMovable
                | QDockWidget.DockWidgetFloatable
                | QDockWidget.DockWidgetClosable
            )
            if self._lut_gb_original_layout:
                self._lut_gb_original_layout.removeWidget(gb)
            gb.setParent(self.lut_dock)
            self.lut_dock.setWidget(gb)
            gb.setVisible(True)
            self._dock_host.addDockWidget(Qt.RightDockWidgetArea, self.lut_dock)
            self.lut_dock.setVisible(True)
            self.lut_dock.visibilityChanged.connect(self._on_lut_dock_visibility_changed)
        else:
            if self.lut_dock is not None:
                gb.setVisible(False)
                self.lut_dock.setWidget(None)
                gb.setParent(self.widget)
                if self._lut_gb_original_layout is not None:
                    self._lut_gb_original_layout.addWidget(gb)
                gb.setVisible(False)
                self._dock_host.removeDockWidget(self.lut_dock)
                self.lut_dock.deleteLater()
                self.lut_dock = None

    def _on_lut_dock_visibility_changed(self, visible: bool):
        """Sync the LUT Visualization checkbox when the dock is closed by the user."""
        if not visible:
            if self.ui.checkBox_lut_visualization.isChecked():
                self.ui.checkBox_lut_visualization.setChecked(False)
