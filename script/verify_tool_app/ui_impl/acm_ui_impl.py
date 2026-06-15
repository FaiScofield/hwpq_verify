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
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

try:
    from ..ui_gen.acm_ui import Ui_AcmUiWidget
except ImportError:
    from ui_gen.acm_ui import Ui_AcmUiWidget

try:
    from ...script.acm.acm_impl_base import (
        DELTA_Y_MIN, DELTA_Y_MAX,
        DELTA_S_MIN, DELTA_S_MAX,
        DELTA_H_MIN, DELTA_H_MAX,
        GAIN_MIN, GAIN_MAX,
    )
except ImportError:
    from script.acm.acm_impl_base import (
        DELTA_Y_MIN, DELTA_Y_MAX,
        DELTA_S_MIN, DELTA_S_MAX,
        DELTA_H_MIN, DELTA_H_MAX,
        GAIN_MIN, GAIN_MAX,
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
    ) -> None:
        """Create a chart widget with a configurable value range and color."""
        super().__init__(parent)
        self.setMinimumSize(600, 200)
        self.setMaximumSize(1200, 400)
        self.value_range = value_range
        self.curve_color = curve_color
        self.values: list[int] = [0]
        self.padding = 40
        self.sample_positions: list[float] = []
        self.sample_values: list[float] = []
        self.dragging_sample: int | None = None
        self.selected_sample: int | None = None
        self.hover_sample: int | None = None

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

        painter.fillRect(self.rect(), QColor(30, 30, 30))

        # Horizontal grid lines
        painter.setPen(QPen(QColor(60, 60, 60), 1))
        for idx in range(9):
            y_pos = self.padding + chart_height * idx / 8
            painter.drawLine(self.padding, int(y_pos), width - self.padding, int(y_pos))

        # Zero line
        painter.setPen(QPen(QColor(100, 100, 100), 2, Qt.DashLine))
        mid_y = self._value_to_y(0)
        painter.drawLine(self.padding, int(mid_y), width - self.padding, int(mid_y))

        # Curve connecting integer-indexed points
        if n >= 2:
            painter.setPen(QPen(self.curve_color, 2))
            for idx in range(n - 1):
                x1, y1 = self._index_position(idx)
                x2, y2 = self._index_position(idx + 1)
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        # X-axis tick labels every 2 points
        font = painter.font()
        font.setPointSize(9)
        painter.setFont(font)
        painter.setPen(QColor(200, 200, 200))
        if n >= 2:
            for idx in range(0, n, 2):
                x_pos, _ = self._index_position(idx)
                painter.drawLine(int(x_pos), int(height - self.padding),
                                 int(x_pos), int(height - self.padding + 4))
                text_rect = QRect(int(x_pos) - 18, int(height - self.padding + 6), 36, 14)
                painter.drawText(text_rect, Qt.AlignCenter, str(idx))

        # Y-axis range labels
        for value in (255, 192, 128, 64, 0, -64, -128, -192, -255):
            painter.drawText(5, int(self._value_to_y(value) + 4), str(value))

        # Integer-indexed points: small filled circles + value label
        # (even indices above the curve, odd indices below the curve)
        for idx in range(n):
            x_pos, y_pos = self._index_position(idx)
            painter.setBrush(self.curve_color)
            painter.setPen(QPen(self.curve_color.darker(130), 1))
            painter.drawEllipse(int(x_pos) - 3, int(y_pos) - 3, 6, 6)
            if idx % 2 == 0:
                text_rect = QRect(int(x_pos) - 22, int(y_pos) - 22, 44, 14)
            else:
                text_rect = QRect(int(x_pos) - 22, int(y_pos) + 8, 44, 14)
            painter.drawText(text_rect, Qt.AlignCenter, str(int(self.values[idx])))

        # Sample-point overlay: white dashed hollow circles (filled when selected)
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
            # Keep the H-cycle closure pair (first and last sample) in sync.
            # The first and last samples always carry the same value; dragging
            # either one propagates the new value to the other so the LUT is
            # actually updated.
            if self.sample_positions and self.sample_positions[-1] >= len(self.values):
                if self.dragging_sample == 0:
                    self.sample_values[-1] = new_value
                elif self.dragging_sample == len(self.sample_values) - 1:
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
        self._last_input_key: tuple | None = None
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

        # --- Delta chart state ---
        self.full_delta_ybyh = None
        self.full_delta_sbyh = None
        self.full_delta_hbyh = None
        self.ctrl_point_count = self.ui.slider_ctrl_points.value()
        self.interp_method = self.ui.comboBox_interp_method.currentText()
        # Shared sample-point positions across Y/S/H charts (last entry is the
        # H-cycle closure point at len_h whose value mirrors sample_positions[0]).
        self.sample_positions: list[float] = []
        self.sample_values_y: list[float] = []
        self.sample_values_s: list[float] = []
        self.sample_values_h: list[float] = []
        self._suppress_sample_signal = False

        # --- Chart widgets (hosted inside ACM tab) ---
        self.delta_chart_y = SingleCurveChartWidget((DELTA_Y_MIN, DELTA_Y_MAX), QColor(255, 200, 0))
        self.delta_chart_s = SingleCurveChartWidget((DELTA_S_MIN, DELTA_S_MAX), QColor(0, 180, 0))
        self.delta_chart_h = SingleCurveChartWidget((DELTA_H_MIN, DELTA_H_MAX), QColor(0, 100, 255))
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
        self._fix_layout_spacer()  # reposition button_reset_lut_length after spacer
        self._fix_lut_length_order()
        self._init_state()

    def _fix_layout_spacer(self) -> None:
        """Insert a horizontal spacer before the Reset LUT Length button.

        pyside6-uic does not correctly emit spacers in QGridLayout, so we
        remove the button, insert a spacer, then re-add the button at the
        right column with the spacer occupying the gap.
        """
        grid = self.ui.gridLayout_lut_lengths
        btn = self.ui.button_reset_lut_length
        # Remove the button from its default (0,0) spanning 6 cols.
        grid.removeWidget(btn)
        # Insert a horizontal spacer at (2, 0, 1, 4).
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        grid.addItem(spacer, 2, 0, 1, 4)
        # Re-add the button at (2, 4, 1, 2).
        grid.addWidget(btn, 2, 4, 1, 2)

    def _fix_lut_length_order(self) -> None:
        grid = self.ui.gridLayout_lut_lengths
        mappings = [
            (self.ui.slider_len_y, 0, 1),
            (self.ui.spinBox_len_y, 0, 2),
            (self.ui.slider_len_s, 0, 4),
            (self.ui.spinBox_len_s, 0, 5),
            (self.ui.slider_len_h, 1, 1),
            (self.ui.spinBox_len_h, 1, 2),
            (self.ui.slider_len_h2, 1, 4),
            (self.ui.spinBox_len_h2, 1, 5),
        ]
        for widget, _, _ in mappings:
            grid.removeWidget(widget)
        for widget, row, col in mappings:
            grid.addWidget(widget, row, col, 1, 1)

    def _init_state(self) -> None:
        """Perform initial state sync after all widgets are ready."""
        self._apply_default_cordic_for_algo()
        self._on_acm_colorspace_changed()
        self._sync_ctrl_point_slider(self._get_current_acm().len_h)
        self._reload_delta_controls_from_acm()

    def _is_acm_enabled(self) -> bool:
        checkbox = getattr(self.ui, "checkBox_enable_acm", None)
        if checkbox is None:
            return True
        return bool(checkbox.isChecked())

    def _apply_default_cordic_for_algo(self) -> None:
        if not hasattr(self.ui, "checkBox_use_cordic"):
            return
        self.ui.checkBox_use_cordic.setChecked(self.current_algo == "VOP_VP_ACM")

    def _auto_select_colorspace_for_input(self, frame: ImageFrame) -> None:
        if self._colorspace_user_override:
            return
        want_hsv = bool(frame.is_rgb)
        self._suppress_colorspace_signal = True
        try:
            if want_hsv and hasattr(self.ui, "radioButton_colorspace_hsv"):
                self.ui.radioButton_colorspace_hsv.setChecked(True)
            elif hasattr(self.ui, "radioButton_colorspace_yhs"):
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
        if hasattr(ui, "checkBox_enable_acm"):
            ui.checkBox_enable_acm.toggled.connect(self._schedule_auto_run)
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
                DELTA_Y_MIN, DELTA_Y_MAX).astype(np.int16)
            acm.lut_delta_sbyh = np.clip(
                bicubic_resize_array_1d(saved_s, new_len_h),
                DELTA_S_MIN, DELTA_S_MAX).astype(np.int16)
            acm.lut_delta_hbyh = np.clip(
                bicubic_resize_array_1d(saved_h, new_len_h),
                DELTA_H_MIN, DELTA_H_MAX).astype(np.int16)

    # ------------------------------------------------------------------ #
    # Control-point logic                                                #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _normalize_ctrl_point_count(len_h: int, value: int) -> int:
        """Clamp the control-point count to the valid range [4, len_h]."""
        return max(4, min(int(value), int(len_h)))

    def _update_ctrl_point_hint(self, len_h: int) -> None:
        """Refresh the displayed control-point hint text."""
        count = max(1, len(self.sample_positions) - 1)
        step = (len_h - 1) / count
        self.ui.label_delta_hint.setText(f"(len_h: {len_h}, step: {step:.2f})")

    def _compute_sample_positions(self, len_h: int, count: int) -> list[float]:
        """Compute linspace sample positions plus the H-cycle closure point.

        Produces ``count + 1`` positions: ``count`` evenly spaced in
        ``[0, len_h - 1]`` (rounded to 2 decimals) plus one extra point at
        ``len_h`` that closes the H cycle.
        """
        if count < 1:
            return [float(len_h)]
        positions: list[float] = []
        if count == 1:
            positions.append(0.0)
        else:
            for i in range(count):
                pos = (len_h - 1) * i / (count - 1)
                positions.append(round(pos, 2))
        positions.append(round(float(len_h), 2))
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
        # Force H-cycle closure: last sample mirrors first.
        if self.sample_values_y:
            self.sample_values_y[-1] = self.sample_values_y[0]
            self.sample_values_s[-1] = self.sample_values_s[0]
            self.sample_values_h[-1] = self.sample_values_h[0]
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
            if i == n - 2 and positions[i + 1] >= len_h:
                # Last segment ends at the H-cycle closure; only update the
                # integer indices strictly between left_pos and len_h - 1.
                target_max = len_h - 1
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
        self._update_heatmaps()
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
        self._update_heatmaps()
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
            return DELTA_H_MIN, DELTA_H_MAX
        return DELTA_Y_MIN, DELTA_Y_MAX  # "y" and "s" share the same range

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
        self._update_heatmaps()
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

    # Default LUT lengths per algorithm: (len_y, len_s, len_h, len_h2)
    _DEFAULT_LUT_LENGTHS: dict[str, tuple[int, int, int, int]] = {
        "VOP_VP_ACM": (9, 13, 65, 17),
        "SW_ACM": (9, 13, 65, 65),
        "EVIDEO_ACM": (9, 13, 65, 65),
        "SW_ACM_VARIANT": (9, 13, 65, 65),
    }

    def _on_reset_lut_length(self) -> None:
        """Reset all LUT length controls to defaults for the current algorithm."""
        defaults = self._DEFAULT_LUT_LENGTHS.get(self.current_algo, (9, 13, 65, 65))
        self._set_slider_spin_value(
            self.ui.slider_len_y, self.ui.spinBox_len_y, defaults[0])
        self._set_slider_spin_value(
            self.ui.slider_len_s, self.ui.spinBox_len_s, defaults[1])
        # Update len_h controls; constrain len_h2 max before applying.
        self.ui.spinBox_len_h2.setMaximum(defaults[2])
        self.ui.slider_len_h2.setMaximum(defaults[2])
        self._set_slider_spin_value(
            self.ui.slider_len_h, self.ui.spinBox_len_h, defaults[2])
        self._set_slider_spin_value(
            self.ui.slider_len_h2, self.ui.spinBox_len_h2, defaults[3])
        self._apply_lut_lengths()
        self._sync_ctrl_point_slider(defaults[2])
        self._reload_delta_controls_from_acm()
        # Explicitly rebuild sample-point overlay using the updated
        # ctrl_point_count, in case the slider signal was blocked.
        self._recompute_sample_points(
            self._get_current_acm().len_h, self.ctrl_point_count, force=True)
        self._refresh_sample_overlays()
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
                self.heatmap_widgets[key].set_data(data, GAIN_MIN, GAIN_MAX)

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
            if input_is_rgb:
                raise NotImplementedError("TODO: HSV(RGB) ACM path is not implemented yet.")
            yuv444 = input_frame.as_yuv444_stacked()
            yuv_u8 = yuv444 if yuv444.dtype == np.uint8 else ((yuv444 + 2) >> 2).astype(np.uint8)
            r, g, b = yuv_to_rgb(yuv_u8[..., 0], yuv_u8[..., 1], yuv_u8[..., 2], input_cs=input_frame.clrspc, output_cs=1)
            del r, g, b
            raise NotImplementedError("TODO: HSV(RGB) ACM path is not implemented yet.")

        if input_is_rgb:
            r = input_frame.pyr
            g = input_frame.pug
            b = input_frame.pvb
            rgb_input_cs = input_frame.clrspc if input_frame.clrspc in (0, 1) else 1
            y, u, v = rgb_to_yuv(r, g, b, input_cs=rgb_input_cs, output_cs=5)
            input_yuv444 = np.stack([y, u, v], axis=-1)
            input_cs = 5
        else:
            input_yuv444 = input_frame.as_yuv444_stacked()
            input_cs = input_frame.clrspc
        input_depth = input_frame.depth
        self._apply_lut_lengths()
        self._update_acm_gains()
        self._apply_full_delta_to_acm()
        acm = self._get_current_acm()
        start_time = time.time()
        try:
            if input_depth >= 10 and input_yuv444.dtype == np.uint16:
                output = acm.do_acm_u10(
                    input_yuv444,
                    self.ui.checkBox_use_cordic.isChecked(),
                )
            else:
                # Demote to 8-bit if necessary for the u8 pipeline.
                if input_yuv444.dtype != np.uint8:
                    input_yuv444 = (input_yuv444 >> (input_depth - 8)).astype(np.uint8)
                output = acm.do_acm_u8(
                    input_yuv444,
                    self.ui.checkBox_use_cordic.isChecked(),
                )
            elapsed_ms = (time.time() - start_time) * 1000.0
            out_fmt = 0x13 if (input_depth >= 10 and output.dtype == np.uint16) else _PLANAR_YUV_8
            out_frame = ImageFrame(
                output[..., 0], output[..., 1], output[..., 2],
                out_fmt, input_cs,
            )
            self._output_callback(out_frame)
            self._preview_time_callback(elapsed_ms)
            self._update_heatmaps()
            self._status_callback(f"Processing completed in {elapsed_ms:.2f} ms")
        except Exception as exc:
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
        """Switch the active ACM algorithm and refresh the editor state."""
        algo_names = ["VOP_VP_ACM", "SW_ACM", "EVIDEO_ACM", "SW_ACM_VARIANT"]
        self.current_algo = algo_names[index]
        self._apply_default_cordic_for_algo()
        self._refresh_acm_ui_from_current_acm()
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
        """Handle LUT length changes via spinBox or slider (non-h)."""
        del value
        self._apply_lut_lengths()
        self._reload_delta_controls_from_acm()
        self._schedule_auto_run()

    # ------------------------------------------------------------------ #
    # Config persistence                                                 #
    # ------------------------------------------------------------------ #

    def _refresh_acm_ui_from_current_acm(self) -> None:
        """Refresh the ACM widget controls from the active ACM instance."""
        acm = self._get_current_acm()
        self.ui.groupBox_lut_lengths.setEnabled(True)
        self._set_slider_spin_value(self.ui.slider_len_y, self.ui.spinBox_len_y, acm.len_y)
        self._set_slider_spin_value(self.ui.slider_len_s, self.ui.spinBox_len_s, acm.len_s)
        self._set_slider_spin_value(self.ui.slider_len_h, self.ui.spinBox_len_h, acm.len_h)
        # Enforce len_h2 <= len_h before setting its value.
        self.ui.spinBox_len_h2.setMaximum(acm.len_h)
        self.ui.slider_len_h2.setMaximum(acm.len_h)
        self._set_slider_spin_value(self.ui.slider_len_h2, self.ui.spinBox_len_h2, acm.len_h2)
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
