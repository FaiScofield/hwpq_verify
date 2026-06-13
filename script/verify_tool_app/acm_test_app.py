"""
Copyright   : Copyright (c) 2026 by Rockchip. All right reserved.
FilePath    : acm_test_app.py
Author      : vance.wu@rock-chips.com
Date        : 2026-06-13
Description : ACM test application host window with reusable widget composition
"""

import os
import re
import subprocess
import sys
import time

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def _ensure_generated_ui_modules():
    """Regenerate ui_gen modules when they are missing or older than the source .ui files."""
    ui_pairs = (
        ("ui\\acm_test_app.ui", "ui_gen\\acm_test_app_ui.py"),
        ("ui\\acm_ui.ui", "ui_gen\\acm_ui.py"),
        ("ui\\io_preview_ui.ui", "ui_gen\\io_preview_ui.py"),
        ("ui\\io_ui.ui", "ui_gen\\io_ui.py"),
    )
    needs_regen = False
    for src_rel, gen_rel in ui_pairs:
        src_path = os.path.join(CURRENT_DIR, src_rel)
        gen_path = os.path.join(CURRENT_DIR, gen_rel)
        if not os.path.exists(gen_path) or os.path.getmtime(gen_path) < os.path.getmtime(src_path):
            needs_regen = True
            break

    if not needs_regen:
        return

    cmd_path = os.path.join(CURRENT_DIR, "uic.cmd")
    if not os.path.isfile(cmd_path):
        raise RuntimeError(f"Missing UI generator script: {cmd_path}")

    result = subprocess.run(
        ["cmd", "/c", cmd_path],
        cwd=CURRENT_DIR,
        capture_output=True,
        text=True,
        shell=False,
    )
    if result.returncode != 0:
        output = "\n".join(part for part in (result.stdout.strip(), result.stderr.strip()) if part).strip()
        raise RuntimeError(f"Failed to generate UI files via uic.cmd\n{output}")


_ensure_generated_ui_modules()

import numpy as np
from PIL import Image
from PySide6.QtCore import QEvent, QRect, QTimer, Qt, Signal
from PySide6.QtGui import QColor, QImage, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QDockWidget,
    QFileDialog,
    QGraphicsScene,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from script.acm.acm_evideo import AcmEVideo
from script.acm.acm_impl import AcmImpl
from script.acm.acm_impl_variant import AcmImplVariant
from script.csc.run_csc import (
    CLRSPC_NAMES,
    CLRSPC_OPTIONS,
    FORMAT_NAMES,
    FMT_OPTIONS,
    get_frame_size,
    is_yuv_format,
    read_raw_to_planar,
)

if __package__:
    from .ui_gen.acm_test_app_ui import Ui_AcmTestAppWindow
    from .ui_gen.acm_ui import Ui_AcmUiWidget
    from .ui_gen.io_preview_ui import Ui_PreviewUiWidget
    from .ui_gen.io_ui import Ui_IoUiWidget
else:
    from ui_gen.acm_test_app_ui import Ui_AcmTestAppWindow
    from ui_gen.acm_ui import Ui_AcmUiWidget
    from ui_gen.io_preview_ui import Ui_PreviewUiWidget
    from ui_gen.io_ui import Ui_IoUiWidget


class IoUiWidget(QWidget):
    """Reusable I/O configuration widget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_IoUiWidget()
        self.ui.setupUi(self)


class AcmUiWidget(QWidget):
    """Reusable ACM configuration widget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_AcmUiWidget()
        self.ui.setupUi(self)


class PreviewUiWidget(QWidget):
    """Reusable preview widget content for a host dock."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_PreviewUiWidget()
        self.ui.setupUi(self)


class SingleCurveChartWidget(QWidget):
    """Interactive single-curve chart for one H-based delta LUT."""

    dataChanged = Signal(int, list)

    def __init__(self, value_range, curve_color, parent=None):
        super().__init__(parent)
        self.setMinimumSize(600, 200)
        self.setMaximumSize(1200, 400)
        self.value_range = value_range
        self.curve_color = curve_color
        self.values = [0, 0, 0, 0]
        self.padding = 40
        self.dragging_point = None
        self.hover_point = None

    def set_num_points(self, count):
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

    def set_values(self, values):
        """Replace the chart values and repaint."""
        self.values = [int(v) for v in values]
        if len(self.values) > 1:
            self.values[-1] = self.values[0]
        self.update()

    def get_values(self):
        """Return the chart values with the H-cycle closure applied."""
        if not self.values:
            return []
        result = list(self.values)
        result[-1] = result[0]
        return result

    def _value_to_y(self, value):
        """Map a chart value to widget coordinates."""
        value_min, value_max = self.value_range
        chart_height = self.height() - 2 * self.padding
        ratio = (value - value_min) / (value_max - value_min)
        return self.padding + chart_height * (1 - ratio)

    def _point_position(self, index):
        """Return the widget-space position for a control point."""
        chart_width = self.width() - 2 * self.padding
        x_pos = self.padding
        if len(self.values) > 1:
            x_pos = self.padding + chart_width * index / (len(self.values) - 1)
        y_pos = self._value_to_y(self.values[index])
        return x_pos, y_pos

    def paintEvent(self, event):
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

    def mousePressEvent(self, event):
        """Start dragging the nearest control point."""
        if event.button() != Qt.LeftButton:
            return
        point = self._find_nearest_point(event.position().x(), event.position().y())
        if point is not None:
            self.dragging_point = point
            self.update()

    def mouseMoveEvent(self, event):
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

    def mouseReleaseEvent(self, event):
        """Stop dragging a control point."""
        if event.button() == Qt.LeftButton:
            self.dragging_point = None
            self.update()

    def _find_nearest_point(self, x_pos, y_pos):
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

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(160, 120)
        self.data = None
        self.value_min = -128
        self.value_max = 127

    def set_data(self, data, value_min=-128, value_max=127):
        """Update the heatmap data and repaint."""
        self.data = None if data is None else np.array(data, copy=True)
        self.value_min = value_min
        self.value_max = value_max
        self.update()

    def paintEvent(self, event):
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


class AcmTestAppWindow(QMainWindow):
    """Main window host that composes the ACM UI widgets."""

    def __init__(self):
        super().__init__()
        self.ui = Ui_AcmTestAppWindow()
        self.ui.setupUi(self)

        self.io_widget = IoUiWidget(self)
        self.acm_widget = AcmUiWidget(self)
        self.preview_widget = PreviewUiWidget(self)

        for host_page, child_widget in (
            (self.ui.tab_io_host, self.io_widget),
            (self.ui.tab_acm_host, self.acm_widget),
        ):
            layout = QVBoxLayout(host_page)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(child_widget)

        self.preview_dock = QDockWidget("Image Preview", self)
        self.preview_dock.setObjectName("preview_dock")
        self.preview_dock.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.preview_dock.setFeatures(
            QDockWidget.DockWidgetMovable
            | QDockWidget.DockWidgetFloatable
            | QDockWidget.DockWidgetClosable
        )
        self.preview_dock.setWidget(self.preview_widget)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.preview_dock)

        self.lut_dock = None
        self._lut_gb_original_layout = None

        self.current_algo = "VOP_VP_ACM"
        self.acm_instances = {
            "VOP_VP_ACM": AcmImpl(9, 13, 65, 17),
            "SW_ACM": AcmImpl(9, 13, 65, 65),
            "EVIDEO_ACM": AcmEVideo(9, 13, 65, 65),
            "SW_ACM_VARIANT": AcmImplVariant(9, 13, 65, 65),
        }
        self.input_yuv444 = None
        self.output_yuv444 = None
        self.input_qimage = None
        self.output_qimage = None
        self.mouse_pos = (0, 0)
        self.is_pixel_info_frozen = False
        self.scene_input = QGraphicsScene(self)
        self.scene_output = QGraphicsScene(self)
        self.preview_widget.ui.graphicsView_input.setScene(self.scene_input)
        self.preview_widget.ui.graphicsView_output.setScene(self.scene_output)
        self.auto_run_timer = QTimer(self)
        self.auto_run_timer.setSingleShot(True)
        self.auto_run_timer.timeout.connect(self._do_auto_run)
        self.ctrl_point_count = self.acm_widget.ui.slider_ctrl_points.value()
        self.interp_method = self.acm_widget.ui.comboBox_interp_method.currentText()
        self.full_delta_ybyh = None
        self.full_delta_sbyh = None
        self.full_delta_hbyh = None

        self.delta_chart_y = SingleCurveChartWidget((-255, 255), QColor(255, 200, 0), self)
        self.delta_chart_s = SingleCurveChartWidget((-255, 255), QColor(0, 180, 0), self)
        self.delta_chart_h = SingleCurveChartWidget((-64, 64), QColor(0, 100, 255), self)
        for host, chart in (
            (self.acm_widget.ui.widget_delta_y_host, self.delta_chart_y),
            (self.acm_widget.ui.widget_delta_s_host, self.delta_chart_s),
            (self.acm_widget.ui.widget_delta_h_host, self.delta_chart_h),
        ):
            layout = QVBoxLayout(host)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(chart)
        self.heatmap_widgets = {}
        for key, host in (
            ("gain_ybyy", self.acm_widget.ui.widget_gain_ybyy_host),
            ("gain_sbyy", self.acm_widget.ui.widget_gain_sbyy_host),
            ("gain_hbyy", self.acm_widget.ui.widget_gain_hbyy_host),
            ("gain_ybys", self.acm_widget.ui.widget_gain_ybys_host),
            ("gain_sbys", self.acm_widget.ui.widget_gain_sbys_host),
            ("gain_hbys", self.acm_widget.ui.widget_gain_hbys_host),
        ):
            heatmap = HeatmapWidget(self)
            layout = QVBoxLayout(host)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(heatmap)
            self.heatmap_widgets[key] = heatmap

        self._init_io_ui()
        self._connect_io_signals()
        self._connect_preview_signals()
        self._connect_acm_signals()
        self._on_acm_colorspace_changed()
        self._sync_ctrl_point_slider(self._get_current_acm().len_h)
        self._reload_delta_controls_from_acm()
        # Hide LUT Visualization groupBox by default (shown via checkbox)
        self.acm_widget.ui.groupBox_lut_visualization.setVisible(False)
        self.ui.statusbar.showMessage("Ready")

    def _init_io_ui(self):
        """Initialize the reusable I/O widget controls."""
        io_ui = self.io_widget.ui
        fmt_display = [f"0x{fmt:x} - {FORMAT_NAMES.get(fmt, 'Unknown')}" for fmt in FMT_OPTIONS]
        io_ui.comboBox_input_format.addItems(fmt_display)
        io_ui.comboBox_output_format.addItems(fmt_display)

        clrspc_display = [f"{clr} - {CLRSPC_NAMES[clr]}" for clr in CLRSPC_OPTIONS]
        clrspc_rgb = [item for item in clrspc_display if int(item.split(" ")[0]) in (0, 1)]
        clrspc_yuv = [item for item in clrspc_display if int(item.split(" ")[0]) in range(2, 8)]
        io_ui.comboBox_input_colorspace.addItems(clrspc_rgb)
        io_ui.comboBox_output_colorspace.addItems(clrspc_rgb)

        default_yuv_fmt = next((item for item in fmt_display if item.startswith("0x3 ")), "")
        if default_yuv_fmt:
            io_ui.comboBox_input_format.setCurrentText(default_yuv_fmt)
            io_ui.comboBox_output_format.setCurrentText(default_yuv_fmt)
        if clrspc_yuv:
            default_yuv_clrspc = clrspc_yuv[3] if len(clrspc_yuv) > 3 else clrspc_yuv[-1]
            io_ui.comboBox_input_colorspace.clear()
            io_ui.comboBox_input_colorspace.addItems(clrspc_yuv)
            io_ui.comboBox_output_colorspace.clear()
            io_ui.comboBox_output_colorspace.addItems(clrspc_yuv)
            io_ui.comboBox_input_colorspace.setCurrentText(default_yuv_clrspc)
            io_ui.comboBox_output_colorspace.setCurrentText(default_yuv_clrspc)

    def _connect_io_signals(self):
        """Connect the reusable I/O widget signals."""
        io_ui = self.io_widget.ui
        io_ui.pushButton_browse_input.clicked.connect(self._on_browse_input)
        io_ui.pushButton_reload.clicked.connect(self._on_reload_input)
        io_ui.pushButton_browse_output.clicked.connect(self._on_browse_output)
        io_ui.pushButton_open_output.clicked.connect(self._on_open_output_dir)
        io_ui.pushButton_browse_config.clicked.connect(self._on_browse_config)
        io_ui.pushButton_load_config.clicked.connect(self._on_load_config)
        io_ui.comboBox_input_format.currentIndexChanged.connect(self._on_input_format_changed)
        io_ui.checkBox_set_color.toggled.connect(self._on_set_color_toggled)

    def _connect_preview_signals(self):
        """Connect the preview widget signals."""
        preview_ui = self.preview_widget.ui
        preview_ui.pushButton_save_left.clicked.connect(self._on_save_left_image)
        preview_ui.pushButton_save_right.clicked.connect(self._on_save_right_image)
        preview_ui.slider_preview_scale.valueChanged.connect(self._on_preview_scale_changed)
        if hasattr(preview_ui, "comboBox_compare_mode"):
            preview_ui.comboBox_compare_mode.currentIndexChanged.connect(self._on_compare_mode_changed)
        preview_ui.graphicsView_input.viewport().installEventFilter(self)
        preview_ui.graphicsView_output.viewport().installEventFilter(self)

    def _connect_acm_signals(self):
        """Connect the ACM widget controls related to delta editing."""
        acm_ui = self.acm_widget.ui
        acm_ui.slider_ctrl_points.valueChanged.connect(self._on_ctrl_points_changed)
        acm_ui.comboBox_interp_method.currentTextChanged.connect(self._on_interp_method_changed)
        acm_ui.comboBox_algo_type.currentIndexChanged.connect(self._on_algo_changed)
        acm_ui.checkBox_lut_visualization.toggled.connect(self._on_lut_visualization_toggled)
        acm_ui.spinBox_len_h.valueChanged.connect(self._on_len_h_changed)
        acm_ui.spinBox_len_y.valueChanged.connect(self._on_variant_lengths_changed)
        acm_ui.spinBox_len_s.valueChanged.connect(self._on_variant_lengths_changed)
        acm_ui.spinBox_len_h2.valueChanged.connect(self._on_variant_lengths_changed)
        acm_ui.button_reset_delta_y.clicked.connect(lambda: self._reset_delta_curve("y"))
        acm_ui.button_reset_delta_s.clicked.connect(lambda: self._reset_delta_curve("s"))
        acm_ui.button_reset_delta_h.clicked.connect(lambda: self._reset_delta_curve("h"))
        acm_ui.pushButton_read_config.clicked.connect(self._on_read_config)
        acm_ui.pushButton_save_config.clicked.connect(self._on_save_config)
        self._connect_slider_spin(acm_ui.slider_gain_y, acm_ui.spinBox_gain_y)
        self._connect_slider_spin(acm_ui.slider_gain_s, acm_ui.spinBox_gain_s)
        self._connect_slider_spin(acm_ui.slider_gain_h, acm_ui.spinBox_gain_h)
        self._connect_slider_spin(acm_ui.slider_offset_wr, acm_ui.spinBox_offset_wr)
        self._connect_slider_spin(acm_ui.slider_offset_wg, acm_ui.spinBox_offset_wg)
        self._connect_slider_spin(acm_ui.slider_offset_wb, acm_ui.spinBox_offset_wb)
        acm_ui.slider_gain_y.valueChanged.connect(self._schedule_auto_run)
        acm_ui.slider_gain_s.valueChanged.connect(self._schedule_auto_run)
        acm_ui.slider_gain_h.valueChanged.connect(self._schedule_auto_run)
        acm_ui.radioButton_colorspace_yhs.toggled.connect(self._on_acm_colorspace_changed)
        acm_ui.radioButton_colorspace_hsv.toggled.connect(self._on_acm_colorspace_changed)
        self.delta_chart_y.dataChanged.connect(self._on_delta_chart_changed)
        self.delta_chart_s.dataChanged.connect(self._on_delta_chart_changed)
        self.delta_chart_h.dataChanged.connect(self._on_delta_chart_changed)

    def _get_current_acm(self):
        """Return the current ACM implementation instance."""
        return self.acm_instances[self.current_algo]

    def _on_lut_visualization_toggled(self, checked: bool):
        """Detach or re-attach groupBox_lut_visualization to a standalone dock."""
        acm_ui = self.acm_widget.ui
        gb = acm_ui.groupBox_lut_visualization

        if checked:
            gb.setVisible(False)
            self._lut_gb_original_layout = gb.parent().layout()
            self.lut_dock = QDockWidget("LUT Visualization", self)
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
            self.addDockWidget(Qt.RightDockWidgetArea, self.lut_dock)
            self.lut_dock.setVisible(True)
            # Sync checkbox when dock is closed via title-bar X button
            self.lut_dock.visibilityChanged.connect(self._on_lut_dock_visibility_changed)
        else:
            if self.lut_dock is not None:
                gb.setVisible(False)
                self.lut_dock.setWidget(None)  # detach widget before reparenting
                gb.setParent(self.acm_widget)
                if self._lut_gb_original_layout is not None:
                    self._lut_gb_original_layout.addWidget(gb)
                gb.setVisible(False)  # stay hidden in tab when unchecked
                self.removeDockWidget(self.lut_dock)
                self.lut_dock.deleteLater()
                self.lut_dock = None

    def _on_lut_dock_visibility_changed(self, visible: bool):
        """Sync the LUT Visualization checkbox when the dock is closed by the user."""
        if not visible:
            # Programmatic toggle will already have unset the checkbox;
            # only sync when the user closed the dock via the title-bar X button.
            if self.acm_widget.ui.checkBox_lut_visualization.isChecked():
                self.acm_widget.ui.checkBox_lut_visualization.setChecked(False)

    def _connect_slider_spin(self, slider, spinbox):
        """Synchronize a slider and spin box bidirectionally."""
        slider.valueChanged.connect(spinbox.setValue)
        spinbox.valueChanged.connect(slider.setValue)

    def _normalize_ctrl_point_count(self, len_h, value):
        """Clamp the control-point count to the valid even range."""
        max_even = len_h if len_h % 2 == 0 else len_h - 1
        max_even = max(4, max_even)
        value = max(4, min(value, max_even))
        if value % 2 != 0:
            value -= 1
        return max(4, value)

    def _update_ctrl_point_hint(self, len_h):
        """Refresh the displayed control-point hint text."""
        step = (len_h - 1) / max(1, self.ctrl_point_count - 1)
        self.acm_widget.ui.label_delta_hint.setText(f"(len_h = {len_h}, step = {step:.1f})")

    def _get_ctrl_positions(self, len_h):
        """Return the H positions corresponding to the current control points."""
        return np.linspace(0.0, len_h - 1, self.ctrl_point_count)

    def _set_spinbox_value(self, spinbox, value):
        """Set a spin box value without emitting change notifications."""
        spinbox.blockSignals(True)
        spinbox.setValue(value)
        spinbox.blockSignals(False)

    def _set_slider_spin_value(self, slider, spinbox, value):
        """Set a linked slider and spin box pair without signal feedback."""
        slider.blockSignals(True)
        spinbox.blockSignals(True)
        slider.setValue(value)
        spinbox.setValue(value)
        slider.blockSignals(False)
        spinbox.blockSignals(False)

    def _set_rgb_offset_controls_enabled(self, enabled):
        """Enable the RGB offset controls only for the HSV colorspace mode."""
        acm_ui = self.acm_widget.ui
        for widget in (
            acm_ui.label_offset_wr,
            acm_ui.slider_offset_wr,
            acm_ui.spinBox_offset_wr,
            acm_ui.label_offset_wg,
            acm_ui.slider_offset_wg,
            acm_ui.spinBox_offset_wg,
            acm_ui.label_offset_wb,
            acm_ui.slider_offset_wb,
            acm_ui.spinBox_offset_wb,
        ):
            widget.setEnabled(enabled)

    def _refresh_acm_ui_from_current_acm(self):
        """Refresh the ACM widget controls from the active ACM instance."""
        acm = self._get_current_acm()
        acm_ui = self.acm_widget.ui
        is_variant = self.current_algo == "SW_ACM_VARIANT"
        acm_ui.groupBox_lut_lengths.setEnabled(is_variant)
        self._set_spinbox_value(acm_ui.spinBox_len_y, acm.len_y)
        self._set_spinbox_value(acm_ui.spinBox_len_s, acm.len_s)
        self._set_spinbox_value(acm_ui.spinBox_len_h, acm.len_h)
        self._set_spinbox_value(acm_ui.spinBox_len_h2, acm.len_h2)
        self._set_slider_spin_value(acm_ui.slider_gain_y, acm_ui.spinBox_gain_y, acm.gain_y)
        self._set_slider_spin_value(acm_ui.slider_gain_s, acm_ui.spinBox_gain_s, acm.gain_s)
        self._set_slider_spin_value(acm_ui.slider_gain_h, acm_ui.spinBox_gain_h, acm.gain_h)
        self._sync_ctrl_point_slider(acm.len_h)
        self._reload_delta_controls_from_acm()
        self._update_heatmaps()

    def _load_current_config(self, path):
        """Load a JSON config into the active ACM instance and refresh the UI."""
        if not path or not os.path.isfile(path):
            QMessageBox.warning(self, "Warning", "Please select a valid config file")
            return False

        try:
            self._get_current_acm().load_json(path)
            self.io_widget.ui.lineEdit_config_file.setText(path)
            self._refresh_acm_ui_from_current_acm()
            self._schedule_auto_run()
            self.ui.statusbar.showMessage(f"Config loaded: {path}")
            return True
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Failed to load config: {exc}")
            return False

    def _sync_ctrl_point_slider(self, len_h):
        """Update the control-point slider bounds for the current len_h."""
        max_even = self._normalize_ctrl_point_count(len_h, len_h)
        new_value = self._normalize_ctrl_point_count(len_h, self.ctrl_point_count)
        self.ctrl_point_count = new_value
        acm_ui = self.acm_widget.ui
        acm_ui.slider_ctrl_points.blockSignals(True)
        acm_ui.slider_ctrl_points.setRange(4, max_even)
        acm_ui.slider_ctrl_points.setSingleStep(2)
        acm_ui.slider_ctrl_points.setPageStep(2)
        acm_ui.slider_ctrl_points.setValue(new_value)
        acm_ui.slider_ctrl_points.blockSignals(False)
        acm_ui.label_ctrl_points_value.setText(str(new_value))
        self._update_ctrl_point_hint(len_h)

    def _reload_delta_controls_from_acm(self):
        """Reload the chart data from the current ACM LUT tables."""
        acm = self._get_current_acm()
        self.full_delta_ybyh = np.array(acm.lut_delta_ybyh, dtype=np.int16)
        self.full_delta_sbyh = np.array(acm.lut_delta_sbyh, dtype=np.int16)
        self.full_delta_hbyh = np.array(acm.lut_delta_hbyh, dtype=np.int16)
        self._resample_full_to_ctrl()

    def _resample_full_to_ctrl(self):
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

    def _interpolate_segment(self, x_points, y_points, x_targets):
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

    def _apply_local_curve_change(self, curve_key, changed_index):
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

    def _apply_full_delta_to_acm(self):
        """Write the rebuilt full LUT arrays back to the current ACM instance."""
        if self.full_delta_ybyh is None:
            return
        acm = self._get_current_acm()
        acm.lut_delta_ybyh[:] = self.full_delta_ybyh
        acm.lut_delta_sbyh[:] = self.full_delta_sbyh
        acm.lut_delta_hbyh[:] = self.full_delta_hbyh

    def _on_ctrl_points_changed(self, value):
        """Handle control-point count changes from the ACM widget."""
        normalized_value = self._normalize_ctrl_point_count(self._get_current_acm().len_h, value)
        if normalized_value != value:
            self.acm_widget.ui.slider_ctrl_points.blockSignals(True)
            self.acm_widget.ui.slider_ctrl_points.setValue(normalized_value)
            self.acm_widget.ui.slider_ctrl_points.blockSignals(False)
        self.ctrl_point_count = normalized_value
        self.acm_widget.ui.label_ctrl_points_value.setText(str(normalized_value))
        self._update_ctrl_point_hint(self._get_current_acm().len_h)
        self._resample_full_to_ctrl()

    def _on_interp_method_changed(self, text):
        """Handle interpolation-method changes."""
        self.interp_method = text

    def _on_delta_chart_changed(self, changed_index, values):
        """Handle edits from any delta chart widget."""
        del values
        sender = self.sender()
        if sender == self.delta_chart_y:
            curve_key = "y"
        elif sender == self.delta_chart_s:
            curve_key = "s"
        else:
            curve_key = "h"
        self._apply_local_curve_change(curve_key, changed_index)
        self._apply_full_delta_to_acm()
        self._schedule_auto_run()

    def _reset_delta_curve(self, curve_key):
        """Reset one delta curve and its backing LUT to all zeros."""
        full_lut = getattr(self, f"full_delta_{curve_key}byh")
        if full_lut is None:
            return
        full_lut[:] = 0
        getattr(self, f"delta_chart_{curve_key}").set_values([0] * self.ctrl_point_count)
        self._apply_full_delta_to_acm()
        self._update_heatmaps()
        self._schedule_auto_run()

    def _update_acm_gains(self):
        """Write the current gain controls back to the active ACM instance."""
        acm_ui = self.acm_widget.ui
        self._get_current_acm().set_gain(
            acm_ui.spinBox_gain_y.value(),
            acm_ui.spinBox_gain_s.value(),
            acm_ui.spinBox_gain_h.value(),
        )

    def _on_acm_colorspace_changed(self, checked=False):
        """Toggle RGB offset controls when the ACM colorspace selection changes."""
        del checked
        self._set_rgb_offset_controls_enabled(self.acm_widget.ui.radioButton_colorspace_hsv.isChecked())

    def _schedule_auto_run(self):
        """Debounce ACM processing after UI edits."""
        if self.input_yuv444 is None:
            return
        self.auto_run_timer.start(300)

    def _apply_variant_lengths(self):
        """Apply custom LUT lengths when the variant ACM is active."""
        if self.current_algo != "SW_ACM_VARIANT":
            return
        acm_ui = self.acm_widget.ui
        variant_acm = self._get_current_acm()
        variant_acm.set_len_variant(
            acm_ui.spinBox_len_y.value(),
            acm_ui.spinBox_len_s.value(),
            acm_ui.spinBox_len_h.value(),
            acm_ui.spinBox_len_h2.value(),
        )

    def _do_auto_run(self):
        """Run ACM processing and refresh the output preview."""
        if self.input_yuv444 is None:
            return
        self._apply_variant_lengths()
        self._update_acm_gains()
        self._apply_full_delta_to_acm()
        acm = self._get_current_acm()
        start_time = time.time()
        try:
            self.output_yuv444 = acm.do_acm_u8(
                self.input_yuv444,
                self.acm_widget.ui.checkBox_use_cordic.isChecked(),
            )
            elapsed_ms = (time.time() - start_time) * 1000.0
            self.preview_widget.ui.lineEdit_time_cost.setText(f"{elapsed_ms:.2f} ms")
            self._update_output_preview()
            self._update_heatmaps()
            self.ui.statusbar.showMessage(f"Processing completed in {elapsed_ms:.2f} ms")
        except Exception as exc:
            self.ui.statusbar.showMessage(f"Processing failed: {exc}")

    def _on_algo_changed(self, index):
        """Switch the active ACM algorithm and refresh the editor state."""
        algo_names = ["VOP_VP_ACM", "SW_ACM", "EVIDEO_ACM", "SW_ACM_VARIANT"]
        self.current_algo = algo_names[index]
        self._refresh_acm_ui_from_current_acm()
        self._schedule_auto_run()

    def _on_len_h_changed(self, value):
        """Refresh the delta editor after the variant len_h value changes."""
        if self.current_algo != "SW_ACM_VARIANT":
            return
        self._apply_variant_lengths()
        self._sync_ctrl_point_slider(value)
        self._reload_delta_controls_from_acm()
        self._schedule_auto_run()

    def _on_variant_lengths_changed(self, value):
        """Handle non-h variant length changes."""
        del value
        if self.current_algo != "SW_ACM_VARIANT":
            return
        self._apply_variant_lengths()
        self._schedule_auto_run()

    def _update_heatmaps(self):
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

    def _on_save_config(self):
        """Save the current ACM configuration to a JSON file."""
        acm = self._get_current_acm()
        if not acm.b_lut_ready:
            QMessageBox.warning(self, "Warning", "No LUT data to save")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save Config", "", "JSON Files (*.json)")
        if path:
            if not path.endswith(".json"):
                path += ".json"
            acm.dump_json(path)
            self.ui.statusbar.showMessage(f"Config saved: {path}")

    def _on_read_config(self):
        """Browse and load an ACM configuration from the ACM editor tab."""
        current_path = self.io_widget.ui.lineEdit_config_file.text()
        start_dir = os.path.dirname(current_path) if current_path else ""
        path, _ = QFileDialog.getOpenFileName(self, "Read Config", start_dir, "JSON Files (*.json)")
        if path:
            self._load_current_config(path)

    def _on_browse_input(self):
        """Browse for an input file and load it into memory."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Input File",
            "",
            "All Files (*.*);;YUV Files (*.yuv);;RGB Files (*.rgb);;Image Files (*.png *.jpg *.bmp)",
        )
        if path:
            self.io_widget.ui.lineEdit_input_file.setText(path)
            self._guess_input_params(path)
            self._recalc_frame_num()
            self._load_input_image()

    def _on_reload_input(self):
        """Reload the current input file with the latest I/O settings."""
        io_ui = self.io_widget.ui
        io_ui.checkBox_set_color.setChecked(False)
        path = io_ui.lineEdit_input_file.text()
        if path:
            self._guess_input_params(path)
            self._recalc_frame_num()
            self._load_input_image()

    def _on_browse_output(self):
        """Browse for an output directory."""
        path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if path:
            self.io_widget.ui.lineEdit_output_dir.setText(path)

    def _on_open_output_dir(self):
        """Open the configured output directory."""
        path = self.io_widget.ui.lineEdit_output_dir.text()
        if path and os.path.isdir(path):
            os.startfile(path)

    def _on_browse_config(self):
        """Browse for an ACM config file."""
        path, _ = QFileDialog.getOpenFileName(self, "Select Config File", "", "JSON Files (*.json)")
        if path:
            self.io_widget.ui.lineEdit_config_file.setText(path)

    def _on_load_config(self):
        """Load the ACM config into the current ACM instance."""
        self._load_current_config(self.io_widget.ui.lineEdit_config_file.text())

    def _on_input_format_changed(self, index):
        """Update colorspace choices after the input format changes."""
        del index
        io_ui = self.io_widget.ui
        fmt_str = io_ui.comboBox_input_format.currentText()
        if not fmt_str:
            return
        fmt_code = int(fmt_str.split(" ")[0], 16)
        clrspc_display = [f"{clr} - {CLRSPC_NAMES[clr]}" for clr in CLRSPC_OPTIONS]
        if (fmt_code & 0xF) <= 0x2:
            options = [item for item in clrspc_display if int(item.split(" ")[0]) in (0, 1)]
        else:
            options = [item for item in clrspc_display if int(item.split(" ")[0]) in range(2, 8)]
        current_text = io_ui.comboBox_input_colorspace.currentText()
        io_ui.comboBox_input_colorspace.clear()
        io_ui.comboBox_input_colorspace.addItems(options)
        idx = options.index(current_text) if current_text in options else -1
        io_ui.comboBox_input_colorspace.setCurrentIndex(max(0, idx))

    def _on_set_color_toggled(self, enabled):
        """Toggle the explicit-color input edit."""
        self.io_widget.ui.lineEdit_set_color.setEnabled(enabled)

    def _guess_input_params(self, filepath):
        """Guess format and resolution from the selected input file name."""
        io_ui = self.io_widget.ui
        basename = os.path.basename(filepath).lower()
        ext = os.path.splitext(basename)[1]
        fmt_display = [f"0x{fmt:x} - {FORMAT_NAMES.get(fmt, 'Unknown')}" for fmt in FMT_OPTIONS]

        if ext in (".png", ".jpg", ".jpeg", ".bmp"):
            rgb_fmt = next((item for item in fmt_display if item.startswith("0x0 ")), None)
            if rgb_fmt:
                io_ui.comboBox_input_format.setCurrentText(rgb_fmt)
            try:
                with Image.open(filepath) as image:
                    width, height = image.size
                io_ui.spinBox_width.setValue(width)
                io_ui.spinBox_height.setValue(height)
            except Exception:
                pass
        elif ext == ".yuv":
            yuv_fmt = next((item for item in fmt_display if item.startswith("0x3 ")), None)
            if yuv_fmt:
                io_ui.comboBox_input_format.setCurrentText(yuv_fmt)
        elif ext == ".rgb":
            rgb_fmt = next((item for item in fmt_display if item.startswith("0x0 ")), None)
            if rgb_fmt:
                io_ui.comboBox_input_format.setCurrentText(rgb_fmt)

        match = re.search(r"(\d+)x(\d+)", basename)
        if match:
            io_ui.spinBox_width.setValue(int(match.group(1)))
            io_ui.spinBox_height.setValue(int(match.group(2)))

    def _recalc_frame_num(self):
        """Recalculate frame count from the selected file and format."""
        io_ui = self.io_widget.ui
        input_file = io_ui.lineEdit_input_file.text()
        if not input_file or not os.path.isfile(input_file):
            return

        ext = os.path.splitext(input_file)[1].lower()
        if ext in (".png", ".jpg", ".jpeg", ".bmp"):
            io_ui.spinBox_frame_num.setValue(1)
            return

        fmt_str = io_ui.comboBox_input_format.currentText()
        if not fmt_str:
            return
        fmt_code = int(fmt_str.split(" ")[0], 16)
        width = io_ui.spinBox_width.value()
        height = io_ui.spinBox_height.value()
        frame_size = get_frame_size(width, height, fmt_code)
        actual_size = os.path.getsize(input_file)
        frame_num = max(1, actual_size // frame_size) if frame_size > 0 else 1
        io_ui.spinBox_frame_num.setValue(frame_num)

    def _load_input_image(self):
        """Load input data into a YUV444 buffer for later preview and ACM use."""
        io_ui = self.io_widget.ui
        input_file = io_ui.lineEdit_input_file.text()
        use_set_color = io_ui.checkBox_set_color.isChecked()

        if use_set_color:
            color_str = io_ui.lineEdit_set_color.text()
            try:
                red, green, blue = map(int, color_str.split())
                width = io_ui.spinBox_width.value()
                height = io_ui.spinBox_height.value()
                y_data = np.full((height, width), red * 0.299 + green * 0.587 + blue * 0.114, dtype=np.uint8)
                cb_data = np.full((height, width), 128 - red * 0.114 - green * 0.385 + blue * 0.5, dtype=np.uint8)
                cr_data = np.full((height, width), 128 + red * 0.5 - green * 0.454 - blue * 0.046, dtype=np.uint8)
                self.input_yuv444 = np.stack([y_data, cb_data, cr_data], axis=-1)
                self._update_input_preview()
                self.ui.statusbar.showMessage(f"Input generated: {width}x{height}")
            except Exception:
                QMessageBox.warning(self, "Warning", "Invalid color format. Use 'R G B'")
            return

        if not input_file or not os.path.isfile(input_file):
            return

        fmt_str = io_ui.comboBox_input_format.currentText()
        if not fmt_str:
            return
        fmt_code = int(fmt_str.split(" ")[0], 16)
        width = io_ui.spinBox_width.value()
        height = io_ui.spinBox_height.value()
        try:
            data, _ = read_raw_to_planar(input_file, width, height, fmt_code, repeat_to_444=True)
            self.input_yuv444 = self._convert_to_yuv444(data, fmt_code)
            self._update_input_preview()
            self.ui.statusbar.showMessage(f"Input loaded: {width}x{height}")
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Failed to load image: {exc}")

    def _convert_to_yuv444(self, data, fmt_code):
        """Convert raw planar input data to channels-last YUV444."""
        if is_yuv_format(fmt_code):
            y_data = data[0]
            u_data = data[1]
            v_data = data[2]
            if u_data.shape[1] != y_data.shape[1]:
                u_data = np.repeat(u_data, 2, axis=1)
                v_data = np.repeat(v_data, 2, axis=1)
            if u_data.shape[0] != y_data.shape[0]:
                u_data = np.repeat(u_data, 2, axis=0)
                v_data = np.repeat(v_data, 2, axis=0)
            return np.stack([y_data, u_data, v_data], axis=-1)

        red = data[0].astype(np.float32)
        green = data[1].astype(np.float32)
        blue = data[2].astype(np.float32)
        y_data = (0.2126 * red + 0.7152 * green + 0.0722 * blue + 0.5).astype(np.uint8)
        cb_data = (-0.1146 * red - 0.3854 * green + 0.5 * blue + 128 + 0.5).astype(np.uint8)
        cr_data = (0.5 * red - 0.4542 * green - 0.0458 * blue + 128 + 0.5).astype(np.uint8)
        return np.stack([y_data, cb_data, cr_data], axis=-1)

    def _yuv444_to_qimage(self, yuv_data):
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

    def _update_input_preview(self):
        """Refresh the input preview scene from the loaded input image."""
        if self.input_yuv444 is None:
            return
        preview_ui = self.preview_widget.ui
        self.input_qimage = self._yuv444_to_qimage(self.input_yuv444)
        self.scene_input.clear()
        self.scene_input.addPixmap(QPixmap.fromImage(self.input_qimage))
        if self.scene_input.items():
            preview_ui.graphicsView_input.fitInView(self.scene_input.items()[0], Qt.KeepAspectRatio)
        preview_ui.lineEdit_display_size.setText(
            f"{self.input_qimage.width()}x{self.input_qimage.height()}"
        )

    def _update_output_preview(self):
        """Refresh the output preview scene from the processed output image."""
        if self.output_yuv444 is None:
            return
        self.output_qimage = self._yuv444_to_qimage(self.output_yuv444)
        self.scene_output.clear()
        self.scene_output.addPixmap(QPixmap.fromImage(self.output_qimage))
        if self.scene_output.items():
            self.preview_widget.ui.graphicsView_output.fitInView(
                self.scene_output.items()[0], Qt.KeepAspectRatio
            )

    def _on_preview_scale_changed(self, value):
        """Update the scale label for the preview area."""
        self.preview_widget.ui.label_scale_value.setText(f"{value}%")

    def _on_compare_mode_changed(self, index):
        """Handle compare-mode changes for later preview enhancements."""
        del index

    def _on_mouse_move_input(self, pos):
        """Update the input preview pixel readout from the mouse position."""
        if self.input_qimage is None or self.is_pixel_info_frozen:
            return
        item = self.scene_input.itemAt(pos, self.preview_widget.ui.graphicsView_input.transform())
        if item is None:
            return
        scene_pos = self.preview_widget.ui.graphicsView_input.mapToScene(pos)
        item_rect = item.boundingRect()
        if not item_rect.contains(scene_pos):
            return
        x_pos = int(scene_pos.x() * self.input_qimage.width() / item_rect.width())
        y_pos = int(scene_pos.y() * self.input_qimage.height() / item_rect.height())
        if 0 <= x_pos < self.input_qimage.width() and 0 <= y_pos < self.input_qimage.height():
            self.mouse_pos = (x_pos, y_pos)
            self.preview_widget.ui.lineEdit_position.setText(f"({x_pos}, {y_pos})")
            y_val = self.input_yuv444[y_pos, x_pos, 0]
            cb_val = self.input_yuv444[y_pos, x_pos, 1]
            cr_val = self.input_yuv444[y_pos, x_pos, 2]
            self.preview_widget.ui.lineEdit_input_pixel.setText(
                f"Y={y_val}, Cb={cb_val}, Cr={cr_val}"
            )

    def _on_mouse_move_output(self, pos):
        """Update the output preview pixel readout from the mouse position."""
        if self.output_qimage is None or self.is_pixel_info_frozen:
            return
        item = self.scene_output.itemAt(pos, self.preview_widget.ui.graphicsView_output.transform())
        if item is None:
            return
        scene_pos = self.preview_widget.ui.graphicsView_output.mapToScene(pos)
        item_rect = item.boundingRect()
        if not item_rect.contains(scene_pos):
            return
        x_pos = int(scene_pos.x() * self.output_qimage.width() / item_rect.width())
        y_pos = int(scene_pos.y() * self.output_qimage.height() / item_rect.height())
        if 0 <= x_pos < self.output_qimage.width() and 0 <= y_pos < self.output_qimage.height():
            y_val = self.output_yuv444[y_pos, x_pos, 0]
            cb_val = self.output_yuv444[y_pos, x_pos, 1]
            cr_val = self.output_yuv444[y_pos, x_pos, 2]
            self.preview_widget.ui.lineEdit_output_pixel.setText(
                f"Y={y_val}, Cb={cb_val}, Cr={cr_val}"
            )

    def _on_save_left_image(self):
        """Save the currently displayed left-side input image."""
        if self.input_qimage is None:
            QMessageBox.warning(self, "Warning", "No input image to save")
            return
        output_dir = self.io_widget.ui.lineEdit_output_dir.text() or os.getcwd()
        path = os.path.join(output_dir, "acm_input.png")
        self.input_qimage.save(path)
        self.ui.statusbar.showMessage(f"Saved: {path}")

    def _on_save_right_image(self):
        """Save the currently displayed right-side output image."""
        if self.output_qimage is None:
            QMessageBox.warning(self, "Warning", "No output image to save")
            return
        output_dir = self.io_widget.ui.lineEdit_output_dir.text() or os.getcwd()
        path = os.path.join(output_dir, "acm_output.png")
        self.output_qimage.save(path)
        self.ui.statusbar.showMessage(f"Saved: {path}")

    def eventFilter(self, obj, event):
        """Track mouse movement over the preview graphics views."""
        preview_ui = self.preview_widget.ui
        if event.type() == QEvent.MouseMove:
            if obj == preview_ui.graphicsView_input.viewport():
                self._on_mouse_move_input(event.pos())
            elif obj == preview_ui.graphicsView_output.viewport():
                self._on_mouse_move_output(event.pos())
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event):
        """Toggle pixel-info freeze with the space key."""
        if event.key() == Qt.Key_Space:
            self.is_pixel_info_frozen = not self.is_pixel_info_frozen
            status = "Frozen" if self.is_pixel_info_frozen else "Live"
            self.ui.statusbar.showMessage(f"Pixel info: {status}")
        super().keyPressEvent(event)


def main():
    """Launch the ACM test application host window."""
    app = QApplication(sys.argv)
    window = AcmTestAppWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
