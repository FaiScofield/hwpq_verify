"""
ACM tab controller — encapsulates all ACM-related UI behavior and state.
"""

from collections.abc import Callable
from dataclasses import dataclass
import os
import time

import numpy as np
from PySide6.QtCore import QRect, QTimer, Qt, Signal
from PySide6.QtGui import QColor, QGuiApplication, QImage, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QLineEdit,
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
    from ...script.img_io import (
        ImageFrame, _PLANAR_YUV_8, _PLANAR_YUV_10, _PLANAR_RGB_8, _PLANAR_RGB_10,
        _csc_range_params, _get_csc_matrices, is_limited_range, is_rgb_format,
        rgb_to_yuv, yuv_to_rgb,
    )
except ImportError:
    from script.img_io import (
        ImageFrame, _PLANAR_YUV_8, _PLANAR_YUV_10, _PLANAR_RGB_8, _PLANAR_RGB_10,
        _csc_range_params, _get_csc_matrices, is_limited_range, is_rgb_format,
        rgb_to_yuv, yuv_to_rgb,
    )


@dataclass
class AcmPixelReadoutCache:
    """ACM 处理读数缓存（全分辨率，float full-range / 原生整数）。

    输入侧：in_native(1️⃣) / in_full_yuv·in_full_rgb(2️⃣, 视处理域) / in_domain(3️⃣)。
    输出侧：out_native(6️⃣) / out_full_yuv·out_full_rgb(5️⃣) / out_domain(4️⃣)。
    域值 in/out_domain 为 (name, h, s, y)：
      YHS 处理域：h=YCbCr 极角度 [-180,180]，s=原始极径，y=Y 原生尺度。
      HSV 处理域：h=六边形色相度 [0,360)，s=S∈[0,1]，y=V∈[0,1]。
    """

    in_native: tuple                       # (kind, (planes), depth)，kind='rgb'/'yuv'
    in_full_yuv: np.ndarray | None         # (H,W,3) float (Y, cb, cr)（YHS 处理域）
    in_full_rgb: np.ndarray | None         # (H,W,3) float full-range RGB（HSV 处理域）
    in_yuv_cs: int
    in_domain: tuple                       # (name, h, s, y)
    out_native: tuple
    out_full_yuv: np.ndarray | None
    out_full_rgb: np.ndarray | None
    out_yuv_cs: int
    out_domain: tuple


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
        input_label: str | None = None,
        output_label: str | None = None,
    ) -> None:
        """Set H-axis reference markers and input/output value markers.

        Args:
            h_index_in:   input H index  → black dashed line + black × marker.
            h_index_out:  output H index → white dashed line + white × marker.
            input_value:  chart-space Y value for the input marker (black ×).
            output_value: chart-space Y value for the output marker (white ×).
            input_label:  optional text label drawn next to the input marker.
            output_label: optional text label drawn next to the output marker.
        """
        self.reference_h_index = h_index_in
        self.reference_h_index_out = h_index_out
        self.input_value = input_value
        self.output_value = output_value
        self.input_label = input_label
        self.output_label = output_label
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
            if self.input_label is not None:
                painter.setPen(QPen(QColor(0, 0, 0), 1))
                font_small = painter.font()
                font_small.setPointSize(8)
                painter.setFont(font_small)
                painter.drawText(int(ref_x) + marker_size + 4, int(y_marker) + marker_size + 12,
                                 self.input_label)
        if ref_x_out is not None and self.output_value is not None:
            y_marker = self._value_to_y(self.output_value)
            painter.setPen(QPen(QColor(255, 255, 255), 2))  # white
            painter.drawLine(int(ref_x_out) - marker_size, int(y_marker) - marker_size,
                             int(ref_x_out) + marker_size, int(y_marker) + marker_size)
            painter.drawLine(int(ref_x_out) + marker_size, int(y_marker) - marker_size,
                             int(ref_x_out) - marker_size, int(y_marker) + marker_size)
            if self.output_label is not None:
                painter.setPen(QPen(QColor(255, 255, 255), 1))
                font_small = painter.font()
                font_small.setPointSize(8)
                painter.setFont(font_small)
                painter.drawText(int(ref_x_out) + marker_size + 4, int(y_marker) - marker_size - 4,
                                 self.output_label)

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
        "HW_VOP (9,13,65,17)",
        "SW_RK (9,13,65,65)",
        "SW_Sonnoc (9,13,65,65)",
        "ACM_LITE (custom)",
    )
    _HW_ALGO_KEY = "VOP_VP_ACM"
    # 支持 RGB/HSV 处理路径的算法（do_acm 尊重 isRgb：SW_RK/SW_Sonnoc 走基类
    # _do_acm_rgb，ACM_LITE 走自身 _do_acm_rgb_variant；HW_VOP 恒走 YUV）。
    _RGB_PATH_ALGOS: tuple[str, ...] = ("SW_ACM", "EVIDEO_ACM", "SW_ACM_VARIANT")

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
        work_size_provider: Callable[[int, int], tuple[int, int]] | None = None,
        input_pixel_edit: QLineEdit | None = None,
        output_pixel_edit: QLineEdit | None = None,
        output_fmt_provider: Callable[[], int] | None = None,
        output_clrspc_provider: Callable[[], int] | None = None,
        dock_host: QMainWindow | None = None,
    ) -> None:
        """Bind to an AcmUiWidget instance and explicit host callbacks.

        Args:
            acm_widget: An AcmUiWidget whose ``.ui`` provides ACM controls.
            parent_window: Optional host window kept for QObject parenting.
            input_provider: Optional callback returning the current input frame.
            output_callback: Optional callback receiving the processed preview frame.
            preview_time_callback: Optional callback receiving elapsed milliseconds.
            status_callback: Optional callback receiving status-bar text.
            config_path_getter: Optional callback returning the current config path string.
            config_path_setter: Optional callback receiving a config path string.
            work_size_provider: Optional callback returning the processing size
                (w, h) for a source size (w, h) — used to downsample the preview
                pass for responsiveness.
            input_pixel_edit / output_pixel_edit: preview readout QLineEdits that
                show the frozen pixel's native/full-range/domain values.
            output_fmt_provider / output_clrspc_provider: output format / colorspace
                from the I/O controller (used by step 6️⃣).
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
        self._work_size_provider = work_size_provider
        self._input_pixel_edit = input_pixel_edit
        self._output_pixel_edit = output_pixel_edit
        self._output_fmt_provider = output_fmt_provider
        self._output_clrspc_provider = output_clrspc_provider
        self._last_input_key: tuple | None = None
        self._latest_output_frame: ImageFrame | None = None
        self._latest_preview_frame: ImageFrame | None = None
        self._last_readout: AcmPixelReadoutCache | None = None
        self._work_size: tuple[int, int] | None = None
        self._input_is_rgb = True
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
        self.lut_result_window: LutImageWindow | None = None

        # --- Auto-run debounce timer ---
        self.auto_run_timer = QTimer(self.widget)
        self.auto_run_timer.setSingleShot(True)
        self.auto_run_timer.timeout.connect(self._do_auto_run)

        self._connect_signals()
        self._init_state()

    def _init_state(self) -> None:
        """Perform initial state sync after all widgets are ready."""
        if hasattr(self.ui, "radioButton_colorspace_hsv"):
            self.ui.radioButton_colorspace_hsv.setToolTip(
                "HSV mode binds isLut4Rgb=1 (RGB/HSV LUT path); loading a config "
                "with isLut4Rgb reflects back to this selection. HW_VOP is YUV-only."
            )
        self._sync_clip_type_ui_state()
        self._on_acm_colorspace_changed()
        self._sync_ctrl_point_slider(self._get_current_acm().len_h)
        self._reload_delta_controls_from_acm()
        self._on_lut_visualization_toggled(bool(self.ui.checkBox_lut_config.isChecked()))

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
        ui.checkBox_lut_config.toggled.connect(self._on_lut_visualization_toggled)
        ui.checkBox_lut_result.toggled.connect(self._on_lut_result_toggled)
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
            tooltip = "clip_type is only supported by software ACM paths; HW_VOP ignores this setting."
        self.ui.comboBox_clip_type.setEnabled(is_supported)
        self.ui.comboBox_clip_type.setToolTip(tooltip)
        if hasattr(self.ui, "label_clip_type"):
            self.ui.label_clip_type.setEnabled(is_supported)
            self.ui.label_clip_type.setToolTip(tooltip)

    def _sync_algo_options_enabled(self) -> None:
        """Enable algorithm options based on the ACM colorspace selection.

        All algorithms are available under YHS; only the last two software
        paths (SW_Sonnoc / ACM_LITE) are available under HSV. If the current
        selection is not allowed under HSV, fall back to the first allowed one.
        """
        combo = self.ui.comboBox_algo_type
        is_hsv = self.ui.radioButton_colorspace_hsv.isChecked()
        for index in range(combo.count()):
            combo.model().item(index).setEnabled(not is_hsv or index >= 2)
        if is_hsv and combo.currentIndex() < 2:
            combo.setCurrentIndex(2)

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
        """Convert hue to the current ACM H index.

        YHS 处理域：H 为 YCbCr 极角 [-180, 180]；HSV 处理域：H 为六边形色相
        [0, 360)。两者都线性映射到 [0, len_h-1]。
        """
        acm = self._get_current_acm()
        if self._is_hsv_colorspace():
            h_f = (float(h_deg) % 360.0) / 360.0
        else:
            h_f = (float(h_deg) + 180.0) / 360.0
        return float(h_f * (acm.len_h - 1))

    def update_preview_h_marker(self, x_pos: int, y_pos: int) -> None:
        """Compute the ACM H-domain markers for one pixel and update all charts.

        Reads the input/output domain values from the last processing readout
        cache (步骤 3️⃣/4️⃣)，then places black × markers on the H_in line and
        white × markers on the H_out line for the delta_y and delta_s charts.
        """
        # Cache frozen pixel coordinates so markers can be refreshed after processing.
        self._frozen_pixel_x = x_pos
        self._frozen_pixel_y = y_pos

        rc = self._last_readout
        if rc is None:
            self.clear_preview_h_marker()
            return
        _, h_in_arr, s_in_arr, y_in_arr = rc.in_domain
        if y_pos < 0 or x_pos < 0 or y_pos >= s_in_arr.shape[0] or x_pos >= s_in_arr.shape[1]:
            self.clear_preview_h_marker()
            return

        # Determine depth / s_max for chart normalisation.
        in_depth = 10 if rc.in_native[2] >= 10 else 8
        clip_type = getattr(self._get_current_acm(), 'clip_type', 'easy_clip')
        if in_depth >= 10:
            s_max = 511 if clip_type in ('radial_clip', 'luma_clip') else 724
        else:
            s_max = 127 if clip_type in ('radial_clip', 'luma_clip') else 181

        # Input pixel domain values
        h_idx_in = self._h_deg_to_index(float(h_in_arr[y_pos, x_pos]))
        # Output pixel domain values
        _, h_out_arr, s_out_arr, y_out_arr = rc.out_domain
        h_idx_out = self._h_deg_to_index(float(h_out_arr[y_pos, x_pos]))

        if self._is_hsv_colorspace():
            # HSV 处理域：S/V ∈ [0,1]，映射到 [0,255] 显示。
            y_in_norm = float(y_in_arr[y_pos, x_pos]) * 255.0
            s_in_norm = float(s_in_arr[y_pos, x_pos]) * 255.0
            y_out_norm = float(y_out_arr[y_pos, x_pos]) * 255.0
            s_out_norm = float(s_out_arr[y_pos, x_pos]) * 255.0
        else:
            y_in_norm, s_in_norm = self._norm_ys_to_chart(
                float(y_in_arr[y_pos, x_pos]), float(s_in_arr[y_pos, x_pos]), in_depth, s_max)
            y_out_norm, s_out_norm = self._norm_ys_to_chart(
                float(y_out_arr[y_pos, x_pos]), float(s_out_arr[y_pos, x_pos]), in_depth, s_max)

        # Update charts
        # --- fetch intermediate ACM delta/gain values for annotation ---
        intermediates = self._get_current_acm().get_pixel_intermediates(x_pos, y_pos)
        if intermediates is not None:
            dy = intermediates['delta_y']
            ds = intermediates['delta_s']
            dh = intermediates['delta_h']
            gyy = intermediates['gain_yy']
            gys = intermediates['gain_ys']
            gsy = intermediates['gain_sy']
            gss = intermediates['gain_ss']
            ghy = intermediates['gain_hy']
            ghs = intermediates['gain_hs']
            # Per-channel labels: each chart only shows its own delta/gain values.
            y_in  = f'orig_dY={dy:.2f}, final_dY={dy*gyy*gys:.3f}'
            y_out = f'gain_yy={gyy:.3f}, gain_ys={gys:.3f}'
            s_in  = f'orig_dS={ds:.2f}, final_dS={ds*gsy*gss:.3f}'
            s_out = f'gain_sy={gsy:.3f}, gain_ss={gss:.3f}'
            h_in  = f'orig_dH={dh:.2f}, final_dH={dh*ghy*ghs:.3f}'
            h_out = f'gain_hy={ghy:.3f}, gain_hs={ghs:.3f}'
        else:
            y_in = y_out = s_in = s_out = h_in = h_out = None
        self.delta_chart_y.set_h_markers(h_idx_in, h_idx_out, y_in_norm, y_out_norm,
                                         input_label=y_in, output_label=y_out)
        self.delta_chart_s.set_h_markers(h_idx_in, h_idx_out, s_in_norm, s_out_norm,
                                         input_label=s_in, output_label=s_out)
        self.delta_chart_h.set_h_markers(h_idx_in, h_idx_out, None, None,
                                         input_label=h_in, output_label=h_out)
        self._refresh_frozen_readout()

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

    # ------------------------------------------------------------------ #
    # Lut Result window                                                 #
    # ------------------------------------------------------------------ #

    def _ensure_lut_result_window(self) -> LutImageWindow:
        """Create the standalone LUT result visualization window on first use."""
        if self.lut_result_window is None:
            self.lut_result_window = LutImageWindow(self._on_lut_result_closed)
            self.lut_result_window.setWindowTitle("LUT Result")
            host_frame = self._win.frameGeometry()
            screen = self._win.screen() or QGuiApplication.primaryScreen()
            available = screen.availableGeometry() if screen is not None else host_frame
            margin = 12
            ww = self.lut_result_window.frameGeometry().width()
            wh = self.lut_result_window.frameGeometry().height()
            rx = host_frame.right() + margin
            lx = host_frame.left() - margin - ww
            tx = rx if rx + ww <= available.right() else max(available.left(), lx)
            ty = min(max(host_frame.top(), available.top()), available.bottom() - wh)
            self.lut_result_window.move(tx + 400, ty + 200)
        return self.lut_result_window

    def _on_lut_result_closed(self) -> None:
        """Keep the View Lut Result checkbox in sync when the window is closed manually."""
        if hasattr(self.ui, "checkBox_lut_result") and self.ui.checkBox_lut_result.isChecked():
            self.ui.checkBox_lut_result.blockSignals(True)
            self.ui.checkBox_lut_result.setChecked(False)
            self.ui.checkBox_lut_result.blockSignals(False)

    def _update_lut_result(self) -> None:
        """Refresh the LUT result image when the result window is visible."""
        if self.lut_result_window is None or not self.lut_result_window.isVisible():
            return
        acm = self._get_current_acm()
        if not hasattr(acm, "_last_intermediate_shape"):
            self.lut_result_window.image_label.clear()
            self.lut_result_window.image_label.setText("No result data")
            return
        pixmap = self._lut_image_to_pixmap(acm.dump_lut_results(return_image=True))
        if pixmap is None:
            self.lut_result_window.image_label.clear()
            self.lut_result_window.image_label.setText("No result data")
            return
        self.lut_result_window.image_label.setText("")
        self.lut_result_window.image_label.setPixmap(pixmap)

    def _on_lut_result_toggled(self, checked: bool) -> None:
        """Show or close the standalone LUT result window."""
        if checked:
            window = self._ensure_lut_result_window()
            window.show()
            window.raise_()
            window.activateWindow()
            frame = self._input_provider()
            if frame is None:
                window.image_label.clear()
                window.image_label.setText("No input loaded")
            elif not self._is_acm_enabled():
                window.image_label.clear()
                window.image_label.setText("ACM is disabled")
            else:
                acm = self._get_current_acm()
                if not hasattr(acm, "_last_intermediate_shape"):
                    window.image_label.setText("Acquiring result...")
                    self._schedule_auto_run()
                else:
                    self._update_lut_result()
        elif self.lut_result_window is not None and self.lut_result_window.isVisible():
            self.lut_result_window.close()

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
        if self.ui.checkBox_lut_config.isChecked():
            self.ui.checkBox_lut_config.blockSignals(True)
            self.ui.checkBox_lut_config.setChecked(False)
            self.ui.checkBox_lut_config.blockSignals(False)

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
        """Run ACM processing at the preview work resolution and refresh.

        统一流水线（步骤 1️⃣~6️⃣）：YHS → yuv full-range 处理域；HSV → RGB
        full-range 处理域。预览显示步骤 5️⃣ 的处理域结果（full-range RGB 帧）。
        """
        input_frame = self._input_provider()
        if input_frame is None:
            return
        if not self._is_acm_enabled():
            self._status_callback("ACM disabled")
            return
        self._update_acm_gains()
        self._update_acm_offsets()
        self._update_ignore_gain_luts()
        self._apply_delta_range_to_acm()
        self._apply_full_delta_to_acm()
        start_time = time.time()
        try:
            src_w, src_h = input_frame.width, input_frame.height
            work_w, work_h = self._resolve_work_size(src_w, src_h)
            self._work_size = (work_w, work_h)
            out_frame, preview_frame = self._process_frame(input_frame, (work_w, work_h))
            self._latest_output_frame = out_frame
            self._latest_preview_frame = preview_frame
            # 预览显示步骤 5️⃣ 的处理域结果（full-range RGB 帧）。
            self._output_callback(preview_frame)
            elapsed_ms = (time.time() - start_time) * 1000.0
            self._refresh_frozen_readout()
            if self._frozen_pixel_x is not None and self._frozen_pixel_y is not None:
                self.update_preview_h_marker(self._frozen_pixel_x, self._frozen_pixel_y)
            self._update_lut_result()
            self._preview_time_callback(elapsed_ms)
            self._status_callback(f"Processing completed in {elapsed_ms:.2f} ms")
        except Exception as exc:
            print("ACM processing failed:", exc)
            self._status_callback(f"Processing failed: {exc}")

    def get_full_res_output(self) -> ImageFrame | None:
        """Return a full-resolution output frame（步骤 6️⃣）for saving.

        若最近一次预览处理已在源分辨率进行，直接复用缓存帧；否则按源分辨率
        重算一次。返回前按所选输出 format 转换（子采样/打包），保证保存的
        文件与所选格式一致。
        """
        input_frame = self._input_provider()
        if input_frame is None:
            return None
        src_w, src_h = input_frame.width, input_frame.height
        if self._work_size == (src_w, src_h) and self._latest_output_frame is not None:
            out_444 = self._latest_output_frame
        else:
            out_444, _preview = self._process_frame(input_frame)
            self._latest_output_frame = out_444
            self._work_size = (src_w, src_h)
        return self._apply_output_format(out_444, self._output_fmt_code())

    def _resolve_work_size(self, src_w: int, src_h: int) -> tuple[int, int]:
        """Return the processing resolution: min(source, preview target)."""
        if self._work_size_provider is not None:
            return self._work_size_provider(src_w, src_h)
        return src_w, src_h

    # ------------------------------------------------------------------ #
    # 统一流水线（步骤 1️⃣~6️⃣）                                            #
    # ------------------------------------------------------------------ #

    def _is_hsv_colorspace(self) -> bool:
        """True when the ACM colorspace is HSV（RGB 处理域）。"""
        return bool(self.ui.radioButton_colorspace_hsv.isChecked())

    def _apply_lut4rgb_binding(self) -> None:
        """将 is_lut4rgb 与 colorspace_hsv 绑定。

        colorspace_hsv=ON → is_lut4rgb=True（RGB/HSV 处理域，do_acm(isRgb=True)
        路由到 _do_acm_rgb）；colorspace_yhs=ON → is_lut4rgb=False（YUV 处理域）。
        colorspace 单选是 is_lut4rgb 的唯一权威；配置文件的 isLut4Rgb 字段
        加载后仍会被本绑定覆盖。
        """
        is_hsv = bool(self.ui.radioButton_colorspace_hsv.isChecked())
        for acm in self.acm_instances.values():
            acm.is_lut4rgb = is_hsv

    def _process_frame(
        self, frame: ImageFrame, work_wh: tuple[int, int] | None = None,
    ) -> tuple[ImageFrame, ImageFrame]:
        """统一流水线处理一帧（可选降采样）→ (输出帧 6️⃣, 预览帧 5️⃣)。

        按 colorspace 分派：YHS → yuv444p full-range 处理域；HSV → full-range
        RGB 处理域。降采样处理完成后升采样回源分辨率，保证预览/读数与输入
        对齐（预览显示逻辑无需感知降采样）。
        """
        src_w, src_h = frame.width, frame.height
        work_frame = frame
        if work_wh is not None and (work_wh[0] < src_w or work_wh[1] < src_h):
            work_frame = self._downsample_frame(frame, work_wh[0], work_wh[1])

        if self._is_hsv_colorspace():
            out_frame, preview_frame, readout = self._process_frame_hsv(work_frame)
        else:
            out_frame, preview_frame, readout = self._process_frame_yhs(work_frame)

        if work_frame is not frame:
            out_frame = self._upsample_frame(out_frame, src_h, src_w)
            preview_frame = self._upsample_frame(preview_frame, src_h, src_w)
            readout = self._upsample_readout(readout, src_h, src_w)

        self._last_readout = readout
        self._input_is_rgb = frame.is_rgb
        return out_frame, preview_frame

    @staticmethod
    def _upsample_readout(readout: "AcmPixelReadoutCache", out_h: int, out_w: int) -> "AcmPixelReadoutCache":
        """最近邻把读数缓存的各 (H,W) 数组升采样到 (out_h, out_w)。"""
        def _up_native(native):
            kind, planes, depth = native
            planar = np.stack(planes, axis=0)
            up = AcmUiController._upsample_planar(planar, out_h, out_w)
            return (kind, (up[0], up[1], up[2]), depth)

        def _up_arr(arr):
            if arr is None:
                return None
            return AcmUiController._upsample_planar(
                arr.transpose(2, 0, 1), out_h, out_w).transpose(1, 2, 0)

        def _up_dom(dom):
            name, h, s, y = dom
            up2d = lambda a: AcmUiController._upsample_planar(a[None, ...], out_h, out_w)[0]
            return (name, up2d(h), up2d(s), up2d(y))

        return AcmPixelReadoutCache(
            in_native=_up_native(readout.in_native),
            in_full_yuv=_up_arr(readout.in_full_yuv),
            in_full_rgb=_up_arr(readout.in_full_rgb),
            in_yuv_cs=readout.in_yuv_cs,
            in_domain=_up_dom(readout.in_domain),
            out_native=_up_native(readout.out_native),
            out_full_yuv=_up_arr(readout.out_full_yuv),
            out_full_rgb=_up_arr(readout.out_full_rgb),
            out_yuv_cs=readout.out_yuv_cs,
            out_domain=_up_dom(readout.out_domain),
        )

    def _process_frame_yhs(
        self, work_frame: ImageFrame,
    ) -> tuple[ImageFrame, ImageFrame, AcmPixelReadoutCache]:
        """YHS 处理：步骤 1️⃣~6️⃣。处理域 = yuv444p full-range。

        输入 RGB 用 BT.709 系数转 YUV；输入 YUV 保持输入矩阵（limited→full
        展开）。量化到 full-range 整数 YUV444 后交给 ACM do_acm（步骤 3️⃣/4️⃣
        的 YUV→YHS 转换与 LUT 应用在算法内部完成），输出回 full-range float
        后按输出格式/色彩空间编码（步骤 6️⃣）。
        Returns (输出帧 6️⃣, 预览帧 5️⃣, 读数缓存).
        """
        depth = work_frame.depth
        input_is_rgb = work_frame.is_rgb
        max_val = (1 << depth) - 1
        rp = _csc_range_params(depth)
        uv_center = rp["uv_center"]

        # ---- 1️⃣ 原始输入 ----
        in_native = self._native_planes(work_frame)

        # ---- 2️⃣ 输入 CSC -> yuv full-range（YHS 处理域） ----
        if input_is_rgb:
            proc_cs = 5                                          # BT.709
            rgb = self._rgb_full_from_frame(work_frame)
            r2y, _ = _get_csc_matrices(proc_cs)
            yuv = rgb @ r2y.T                                    # (Y, cb, cr)
        else:
            proc_cs = work_frame.clrspc if work_frame.clrspc in (2, 3, 4, 5, 6, 7) else 5
            yuv = self._yuv_full_from_frame(work_frame)
        yuv_in = yuv.copy()

        # ---- 量化到 full-range 整数 YUV444，供 ACM do_acm（步骤 4️⃣） ----
        dtype = np.uint16 if depth >= 10 else np.uint8
        y_u = np.clip(np.rint(yuv[..., 0] * max_val), 0, max_val).astype(dtype)
        u_u = np.clip(np.rint(yuv[..., 1] * max_val + uv_center), 0, max_val).astype(dtype)
        v_u = np.clip(np.rint(yuv[..., 2] * max_val + uv_center), 0, max_val).astype(dtype)
        input_planar = np.stack([y_u, u_u, v_u], axis=0)         # [C,H,W]

        # ---- 4️⃣ ACM 处理（YUV 路径） ----
        acm = self._get_current_acm()
        if depth >= 10:
            output = acm.do_acm_u10(input_planar)
        else:
            output = acm.do_acm_u8(input_planar)

        # ---- 5️⃣ 回 yuv full-range float ----
        y_5 = output[0].astype(np.float32) / max_val
        cb_5 = (output[1].astype(np.float32) - uv_center) / max_val
        cr_5 = (output[2].astype(np.float32) - uv_center) / max_val
        yuv_5 = np.stack([y_5, cb_5, cr_5], axis=-1)

        # ---- 域值（YHS：Y 原生尺度 / H 极角 / S 原始极径，H ∈ [-180, 180]） ----
        s_5 = np.sqrt(cb_5 * cb_5 + cr_5 * cr_5) * max_val
        h_5 = np.degrees(np.arctan2(cr_5, cb_5))
        y_5_dom = y_5 * max_val
        cb_i, cr_i = yuv_in[..., 1], yuv_in[..., 2]
        s_in = np.sqrt(cb_i * cb_i + cr_i * cr_i) * max_val
        h_in = np.degrees(np.arctan2(cr_i, cb_i))
        y_in_dom = yuv_in[..., 0] * max_val

        # ---- 预览帧（步骤 5️⃣，YUV -> RGB 显示帧） ----
        preview_frame = self._yuv_to_preview_frame(yuv_5, proc_cs, depth)

        # ---- 6️⃣ 输出 CSC（必钳位，444 平面帧；格式转换在保存时进行） ----
        out_frame = self._to_output_frame_yuv(yuv_5, proc_cs, depth)
        out_native = self._native_planes(out_frame)

        readout = AcmPixelReadoutCache(
            in_native=in_native,
            in_full_yuv=yuv_in, in_full_rgb=None, in_yuv_cs=proc_cs,
            in_domain=("YHS", h_in, s_in, y_in_dom),
            out_native=out_native,
            out_full_yuv=yuv_5, out_full_rgb=None, out_yuv_cs=proc_cs,
            out_domain=("YHS", h_5, s_5, y_5_dom),
        )
        return out_frame, preview_frame, readout

    def _process_frame_hsv(
        self, work_frame: ImageFrame,
    ) -> tuple[ImageFrame, ImageFrame, AcmPixelReadoutCache]:
        """HSV 处理：步骤 1️⃣~6️⃣。处理域 = full-range RGB。

        输入 RGB limited→full 展开（直接硬钳）；输入 YUV 经输入矩阵转 RGB。
        量化到 full-range 整数 RGB [H,W,3] 后交给 ACM do_acm(isRgb=True)
        （步骤 3️⃣/4️⃣ 的 RGB→HSV 转换与 LUT 应用在算法内部完成，需
        is_lut4rgb），输出回 full-range float 后按输出格式/色彩空间编码。
        Returns (输出帧 6️⃣, 预览帧 5️⃣, 读数缓存).
        """
        depth = work_frame.depth
        input_is_rgb = work_frame.is_rgb
        max_val = (1 << depth) - 1

        # ---- 1️⃣ 原始输入 ----
        in_native = self._native_planes(work_frame)

        # ---- 2️⃣ 输入 CSC -> full-range RGB（HSV 处理域） ----
        if input_is_rgb:
            rgb_2 = np.clip(self._rgb_full_from_frame(work_frame), 0.0, 1.0)
        else:
            rgb_2 = np.clip(self._yuv_to_rgb_full_float(work_frame), 0.0, 1.0)

        # ---- 量化到 full-range 整数 RGB [H,W,3]，供 ACM do_acm(isRgb=True) ----
        rgb_u = np.clip(np.rint(rgb_2 * max_val), 0, max_val).astype(
            np.uint16 if depth >= 10 else np.uint8)              # [H,W,3]

        # ---- 4️⃣ ACM 处理（RGB/HSV 路径） ----
        # is_lut4rgb 已与 colorspace_hsv 绑定（HSV=ON 恒为 True），do_acm(isRgb=True)
        # 对走基类 do_acm 的算法（SW_RK/SW_Sonnoc）路由到 _do_acm_rgb。
        # HW_VOP/ACM_LITE 的 do_acm 忽略 isRgb 恒走 YUV（HWC RGB 会被误读成
        # CHW YUV 产生错误结果），故在此给出明确提示。
        acm = self._get_current_acm()
        self._apply_lut4rgb_binding()
        if self.current_algo not in self._RGB_PATH_ALGOS:
            raise RuntimeError(
                f"{self.current_algo} does not support the HSV/RGB processing "
                "path (its do_acm always runs the YUV path); "
                "please use SW_RK or SW_Sonnoc.")
        if depth >= 10:
            output = acm.do_acm_u10(rgb_u, isRgb=True)           # -> [C,H,W]
        else:
            output = acm.do_acm_u8(rgb_u, isRgb=True)            # -> [C,H,W]

        # ---- 5️⃣ 回 full-range RGB float [H,W,3] ----
        rgb_5 = np.stack([output[0], output[1], output[2]], axis=-1).astype(np.float32) / max_val

        # ---- 域值（HSV：H 色相 / S / V） ----
        v_5 = np.max(rgb_5, axis=-1)
        m_5 = np.min(rgb_5, axis=-1)
        delta_5 = v_5 - m_5
        s_5 = np.where(v_5 > 0.0, np.divide(delta_5, np.maximum(v_5, 1e-6)), 0.0)
        h_5 = self._rgb_to_hue_deg(rgb_5, v_5, m_5, delta_5)
        v_in = np.max(rgb_2, axis=-1)
        m_in = np.min(rgb_2, axis=-1)
        delta_in = v_in - m_in
        s_in = np.where(v_in > 0.0, np.divide(delta_in, np.maximum(v_in, 1e-6)), 0.0)
        h_in = self._rgb_to_hue_deg(rgb_2, v_in, m_in, delta_in)

        # ---- 预览帧（步骤 5️⃣，full-range RGB 显示帧） ----
        preview_frame = self._rgb_full_to_frame(rgb_5, depth)

        # ---- 6️⃣ 输出 CSC（必钳位，444 平面帧；格式转换在保存时进行） ----
        out_frame = self._to_output_frame_rgb(rgb_5, depth)
        out_native = self._native_planes(out_frame)

        readout = AcmPixelReadoutCache(
            in_native=in_native,
            in_full_yuv=None, in_full_rgb=rgb_2, in_yuv_cs=5,
            in_domain=("HSV", h_in, s_in, v_in),
            out_native=out_native,
            out_full_yuv=None, out_full_rgb=rgb_5, out_yuv_cs=5,
            out_domain=("HSV", h_5, s_5, v_5),
        )
        return out_frame, preview_frame, readout

    @staticmethod
    def _rgb_to_hue_deg(rgb, v, m, delta) -> np.ndarray:
        """full-range RGB -> 六边形 HSV 色相度 [0, 360)（灰阶为 0）。"""
        r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
        delta_safe = np.where(delta > 0, delta, 1.0)
        h = np.where(delta > 0,
                     np.where(v == r, (g - b) / delta_safe,
                     np.where(v == g, (b - r) / delta_safe + 2.0,
                                        (r - g) / delta_safe + 4.0)), 0.0)
        return np.mod(h * 60.0, 360.0)

    # ------------------------------------------------------------------ #
    # Frozen pixel readout（预览像素显示，参考 bcsh_ui_impl）               #
    # ------------------------------------------------------------------ #

    def _refresh_frozen_readout(self) -> None:
        """Write the pixel readout chain of the frozen pixel into the preview readouts."""
        if self._frozen_pixel_x is None or self._frozen_pixel_y is None:
            return
        x_pos, y_pos = self._frozen_pixel_x, self._frozen_pixel_y
        if self._input_pixel_edit is not None:
            self._input_pixel_edit.setText(self.readout_text(x_pos, y_pos, "input"))
        if self._output_pixel_edit is not None:
            self._output_pixel_edit.setText(self.readout_text(x_pos, y_pos, "output"))

    def readout_text(self, x_pos: int, y_pos: int, role: str) -> str:
        """按当前处理域拼装 (x,y) 像素读数；role='input'/'output'。

        输入侧：native(1️⃣), 处理域 full(2️⃣), 域值(3️⃣)
        输出侧：native(6️⃣), 处理域 full(5️⃣), 域值(4️⃣)
        """
        if self._last_readout is None:
            return ""
        rc = self._last_readout
        if role == "input":
            native = rc.in_native
            full = rc.in_full_yuv if rc.in_full_yuv is not None else rc.in_full_rgb
            full_kind = 'yuv' if rc.in_full_yuv is not None else 'rgb'
            dom = rc.in_domain
        else:
            native = rc.out_native
            full = rc.out_full_yuv if rc.out_full_yuv is not None else rc.out_full_rgb
            full_kind = 'yuv' if rc.out_full_yuv is not None else 'rgb'
            dom = rc.out_domain
        return self._format_chain(native, full, full_kind, dom, x_pos, y_pos)

    @staticmethod
    def _format_chain(native, full, full_kind: str, dom, x_pos: int, y_pos: int) -> str:
        """拼装 `原生(整数), YUVF/RGBF(整数), 域(H/S/Y 浮点)` 读数链。

        YUVF 按帧位深缩放为整数显示（U=cb+0.5、V=cr+0.5 去中心）。域值：
        YHS 显示 YHS(Y, H, S)（Y 原生尺度 / H 度 / S 原始极径）；
        HSV 显示 HSV(H, S, V)（H 度 / S / V）。
        """
        kind, (p0, p1, p2), depth = native
        if y_pos < 0 or x_pos < 0 or y_pos >= p0.shape[0] or x_pos >= p0.shape[1]:
            return ""
        max_val = (1 << depth) - 1
        parts = ["{}({}, {}, {})".format(
            'RGB' if kind == 'rgb' else 'YUV',
            int(p0[y_pos, x_pos]), int(p1[y_pos, x_pos]), int(p2[y_pos, x_pos]))]
        if full is not None:
            f0 = float(full[y_pos, x_pos, 0]) * max_val
            f1 = float(full[y_pos, x_pos, 1]) * max_val
            f2 = float(full[y_pos, x_pos, 2]) * max_val
            if full_kind == 'yuv':
                f1 += 128/255 * max_val   # cb -> U
                f2 += 128/255 * max_val   # cr -> V
            parts.append("{}({}, {}, {})".format(
                'YUVF' if full_kind == 'yuv' else 'RGBF',
                int(round(f0)), int(round(f1)), int(round(f2))))
        name, dh, ds, dx = dom
        if name == "HSV":
            parts.append("HSV({:.1f}, {:.3f}, {:.3f})".format(
                float(dh[y_pos, x_pos]), float(ds[y_pos, x_pos]), float(dx[y_pos, x_pos])))
        else:  # YHS：Y/S 为原生尺度，H 为度
            parts.append("YHS({:.1f}, {:.1f}, {:.1f})".format(
                float(dx[y_pos, x_pos]), float(dh[y_pos, x_pos]), float(ds[y_pos, x_pos])))
        return ", ".join(parts)

    # ------------------------------------------------------------------ #
    # 统一流水线辅助（步骤 2️⃣/5️⃣/6️⃣ 的 CSC 与帧封装）                    #
    # ------------------------------------------------------------------ #

    def _output_fmt_code(self) -> int:
        """所选输出格式代码（io_ui 提供；默认 YUV444P）。"""
        if self._output_fmt_provider is not None:
            return self._output_fmt_provider()
        return _PLANAR_YUV_8

    def _output_clrspc(self) -> int:
        """所选输出色彩空间代码（io_ui 提供；默认 BT.709 full）。"""
        if self._output_clrspc_provider is not None:
            return self._output_clrspc_provider()
        return 5

    @staticmethod
    def _native_planes(frame: ImageFrame) -> tuple:
        """步骤 1️⃣/6️⃣ 原始（native 量化）数据：(kind, (p0,p1,p2), depth)。"""
        kind = 'rgb' if frame.is_rgb else 'yuv'
        return (kind, (frame.pyr, frame.pug, frame.pvb), frame.depth)

    @staticmethod
    def _rgb_full_from_frame(frame: ImageFrame) -> np.ndarray:
        """RGB 帧 -> full-range RGB float (H,W,3)；limited 展开 full。"""
        depth = frame.depth
        max_val = (1 << depth) - 1
        r, g, b = (frame.pyr.astype(np.float32), frame.pug.astype(np.float32),
                   frame.pvb.astype(np.float32))
        if frame.clrspc == 0:  # limited RGB -> full 展开
            rp = _csc_range_params(depth)
            lo = rp["yr_lo_l"]
            scale = max_val / (rp["yr_hi_l"] - lo)
            r = (r - lo) * scale
            g = (g - lo) * scale
            b = (b - lo) * scale
        return np.stack([r, g, b], axis=-1) / max_val

    @staticmethod
    def _yuv_to_rgb_full_float(frame: ImageFrame) -> np.ndarray:
        """YUV 帧 -> full-range RGB float (H,W,3)；用输入矩阵，不钳位（可越界）。"""
        depth = frame.depth
        max_val = (1 << depth) - 1
        input_cs = frame.clrspc if frame.clrspc in (2, 3, 4, 5, 6, 7) else 5
        rp = _csc_range_params(depth)
        uv_center = rp["uv_center"]
        y = frame.pyr.astype(np.float32)
        u = frame.pug.astype(np.float32)
        v = frame.pvb.astype(np.float32)
        if is_limited_range(input_cs):
            scale_y = max_val / (rp["yr_hi_l"] - rp["yr_lo_l"])
            scale_c = max_val / (rp["uv_hi_l"] - rp["uv_lo_l"])
            y_f = (y - rp["yr_lo_l"]) * scale_y / max_val
            u_f = (u - uv_center) * scale_c / max_val
            v_f = (v - uv_center) * scale_c / max_val
        else:
            y_f = y / max_val
            u_f = (u - uv_center) / max_val
            v_f = (v - uv_center) / max_val
        _, y2r = _get_csc_matrices(input_cs)
        return np.stack([y_f, u_f, v_f], axis=-1) @ y2r.T

    @staticmethod
    def _yuv_full_from_frame(frame: ImageFrame) -> np.ndarray:
        """YUV 帧 -> full-range 归一化 (Y, cb, cr) (H,W,3)；保持输入矩阵、去中心。"""
        depth = frame.depth
        max_val = (1 << depth) - 1
        rp = _csc_range_params(depth)
        uv_center = rp["uv_center"]
        y = frame.pyr.astype(np.float32)
        u = frame.pug.astype(np.float32)
        v = frame.pvb.astype(np.float32)
        if is_limited_range(frame.clrspc):
            scale_y = max_val / (rp["yr_hi_l"] - rp["yr_lo_l"])
            scale_c = max_val / (rp["uv_hi_l"] - rp["uv_lo_l"])
            y_f = (y - rp["yr_lo_l"]) * scale_y / max_val
            cb = (u - uv_center) * scale_c / max_val
            cr = (v - uv_center) * scale_c / max_val
        else:
            y_f = y / max_val
            cb = (u - uv_center) / max_val
            cr = (v - uv_center) / max_val
        return np.stack([y_f, cb, cr], axis=-1)

    @staticmethod
    def _rgb_full_to_frame(rgb_norm: np.ndarray, depth: int) -> ImageFrame:
        """full-range RGB float -> RGB planar 帧（clrspc=1 full，必钳位量化）。"""
        max_val = (1 << depth) - 1
        rgb = np.clip(np.rint(rgb_norm * max_val), 0, max_val)
        planar = rgb.transpose(2, 0, 1)
        dtype = np.uint16 if depth >= 10 else np.uint8
        out_fmt = _PLANAR_RGB_10 if depth >= 10 else _PLANAR_RGB_8
        return ImageFrame(planar[0].astype(dtype), planar[1].astype(dtype),
                          planar[2].astype(dtype), out_fmt, 1)

    @staticmethod
    def _yuv_norm_to_output_frame(yuv_norm: np.ndarray, depth: int, cs: int) -> ImageFrame:
        """归一化 (Y, cb, cr) -> yuv444p 输出帧（按 cs 编码 full/limited，必钳位量化）。

        YCbCr 处理域的直接输出编码（步骤 6️⃣，不经过 RGB）；cs 为输出色彩空间。
        """
        max_val = (1 << depth) - 1
        rp = _csc_range_params(depth)
        uv_center = rp["uv_center"]
        if is_limited_range(cs):
            sy = (rp["yr_hi_l"] - rp["yr_lo_l"]) / max_val
            sc = (rp["uv_hi_l"] - rp["uv_lo_l"]) / max_val
            y = np.clip(np.rint(yuv_norm[..., 0] * max_val * sy + rp["yr_lo_l"]), 0, max_val)
            u = np.clip(np.rint(yuv_norm[..., 1] * max_val * sc + uv_center), 0, max_val)
            v = np.clip(np.rint(yuv_norm[..., 2] * max_val * sc + uv_center), 0, max_val)
            clrspc = cs
        else:
            y = np.clip(np.rint(yuv_norm[..., 0] * max_val), 0, max_val)
            u = np.clip(np.rint(yuv_norm[..., 1] * max_val + uv_center), 0, max_val)
            v = np.clip(np.rint(yuv_norm[..., 2] * max_val + uv_center), 0, max_val)
            clrspc = (cs | 1) if cs in (2, 3, 4, 5, 6, 7) else 5    # limited -> full 同族
        dtype = np.uint16 if depth >= 10 else np.uint8
        out_fmt = _PLANAR_YUV_10 if depth >= 10 else _PLANAR_YUV_8
        return ImageFrame(y.astype(dtype), u.astype(dtype), v.astype(dtype), out_fmt, clrspc)

    @staticmethod
    def _rgb_float_to_uint(rgb_norm: np.ndarray, depth: int) -> np.ndarray:
        """full-range RGB float -> uint 量化（钳位 [0,1]，按 depth）。"""
        max_val = (1 << depth) - 1
        q = np.clip(np.rint(rgb_norm * max_val), 0, max_val)
        dtype = np.uint16 if depth >= 10 else np.uint8
        return q.astype(dtype)

    @staticmethod
    def _encode_rgb_frame(rgb_norm: np.ndarray, depth: int, out_cs: int) -> ImageFrame:
        """full-range RGB float -> 输出 RGB 444 平面帧（按 out_cs 编码，必钳位）。"""
        max_val = (1 << depth) - 1
        if out_cs == 0:  # limited RGB
            rp = _csc_range_params(depth)
            lo = rp["yr_lo_l"]
            scale = (rp["yr_hi_l"] - lo) / max_val
            r = np.clip(np.rint(rgb_norm[..., 0] * max_val * scale + lo), 0, max_val)
            g = np.clip(np.rint(rgb_norm[..., 1] * max_val * scale + lo), 0, max_val)
            b = np.clip(np.rint(rgb_norm[..., 2] * max_val * scale + lo), 0, max_val)
        else:  # full RGB
            r = np.clip(np.rint(rgb_norm[..., 0] * max_val), 0, max_val)
            g = np.clip(np.rint(rgb_norm[..., 1] * max_val), 0, max_val)
            b = np.clip(np.rint(rgb_norm[..., 2] * max_val), 0, max_val)
        dtype = np.uint16 if depth >= 10 else np.uint8
        fmt = _PLANAR_RGB_10 if depth >= 10 else _PLANAR_RGB_8
        return ImageFrame(r.astype(dtype), g.astype(dtype), b.astype(dtype), fmt, out_cs)

    @staticmethod
    def _apply_output_format(frame: ImageFrame, fmt: int) -> ImageFrame:
        """把 planar 输出帧转到所选输出格式（子采样/深度；交错在写出时进行）。"""
        if frame.fmt == fmt:
            return frame
        return frame.copy().to_format(fmt)

    def _to_output_frame_rgb(self, rgb_norm: np.ndarray, depth: int) -> ImageFrame:
        """步骤 6️⃣（HSV/RGB 系）：full-range RGB -> 444 平面输出帧（必钳位）。"""
        out_cs = self._output_clrspc()
        out_fmt = self._output_fmt_code()
        if is_rgb_format(out_fmt):
            return self._encode_rgb_frame(rgb_norm, depth, out_cs)
        # YUV 输出：RGB uint -> YUV（out_cs 编码，rgb_to_yuv 内部钳位量化）
        rgb_u = self._rgb_float_to_uint(rgb_norm, depth)
        y, u, v = rgb_to_yuv(rgb_u[..., 0], rgb_u[..., 1], rgb_u[..., 2],
                             input_cs=1, output_cs=out_cs)
        fmt = _PLANAR_YUV_10 if depth >= 10 else _PLANAR_YUV_8
        return ImageFrame(y, u, v, fmt, out_cs)

    def _to_output_frame_yuv(self, yuv_norm: np.ndarray, proc_cs: int, depth: int) -> ImageFrame:
        """步骤 6️⃣（YHS 系）：处理域 yuv（proc_cs full）-> 444 平面输出帧（必钳位）。

        YUV 输出直接编码处理域 YUV（步骤 5️⃣ 已完成色域处理）；仅 RGB 输出仍
        需 full-RGB 桥（y2r -> rgb 钳位 -> 输出编码）。
        """
        out_cs = self._output_clrspc()
        out_fmt = self._output_fmt_code()
        if not is_rgb_format(out_fmt):
            return self._yuv_norm_to_output_frame(yuv_norm, depth, out_cs)
        _, y2r = _get_csc_matrices(proc_cs)
        rgb = np.clip(yuv_norm @ y2r.T, 0.0, 1.0)
        return self._encode_rgb_frame(rgb, depth, out_cs)

    def _yuv_to_preview_frame(self, yuv_norm, proc_cs, depth) -> ImageFrame:
        """输出 YUV 帧 -> 预览显示帧（YHS 域）：YUV->RGB 硬钳显示。"""
        _, y2r = _get_csc_matrices(proc_cs)
        rgb = np.clip(yuv_norm @ y2r.T, 0.0, 1.0)
        return self._rgb_full_to_frame(rgb, depth)

    @staticmethod
    def _upsample_frame(frame: ImageFrame, out_h: int, out_w: int) -> ImageFrame:
        """最近邻把 444 帧（RGB 或 YUV444p）升采样到 (out_h, out_w)。"""
        planar = np.stack([frame.pyr, frame.pug, frame.pvb], axis=0)
        up = AcmUiController._upsample_planar(planar, out_h, out_w)
        return ImageFrame(up[0], up[1], up[2], frame.fmt, frame.clrspc)

    @staticmethod
    def _downsample_frame(frame: ImageFrame, work_w: int, work_h: int) -> ImageFrame:
        """最近邻降采样到目标尺寸，保持 YUV 子采样比例。"""
        if frame.width <= work_w and frame.height <= work_h:
            return frame
        work_w, work_h = max(1, work_w), max(1, work_h)

        def _sample(plane, tw, th):
            h, w = plane.shape
            if h <= th and w <= tw:
                return plane
            yi = np.minimum((np.arange(th) * h / max(1, th)).astype(int), h - 1)
            xi = np.minimum((np.arange(tw) * w / max(1, tw)).astype(int), w - 1)
            return plane[yi][:, xi]

        uv_scale_h = frame.pug.shape[0] / max(1, frame.height)
        uv_scale_w = frame.pug.shape[1] / max(1, frame.width)
        pyr = _sample(frame.pyr, work_w, work_h)
        pug = _sample(frame.pug, max(1, int(round(work_w * uv_scale_w))),
                      max(1, int(round(work_h * uv_scale_h))))
        pvb = _sample(frame.pvb, max(1, int(round(work_w * uv_scale_w))),
                      max(1, int(round(work_h * uv_scale_h))))
        return ImageFrame(pyr, pug, pvb, frame.fmt, frame.clrspc)

    @staticmethod
    def _upsample_planar(planar: np.ndarray, out_h: int, out_w: int) -> np.ndarray:
        """最近邻把 (3, H, W) 平面放大到 (3, out_h, out_w)。"""
        h, w = planar.shape[1], planar.shape[2]
        if h == out_h and w == out_w:
            return planar
        yi = np.minimum((np.arange(out_h) * h / max(1, out_h)).astype(int), h - 1)
        xi = np.minimum((np.arange(out_w) * w / max(1, out_w)).astype(int), w - 1)
        return planar[:, yi][:, :, xi]

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
        self._sync_algo_options_enabled()
        self._apply_lut4rgb_binding()
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
        # 保留 RGB/HSV LUT 能力（HSV 处理域依赖 is_lut4rgb）。
        new_acm.is_lut4rgb = old_acm.is_lut4rgb
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
            # 先把配置同步到 UI/LUT 编辑器，再让 colorspace 单选跟随配置：
            # isLut4Rgb 是配置声明的默认处理域（=1 -> HSV，=0 -> YHS），
            # setChecked 会触发绑定使全实例 is_lut4rgb 与单选一致。
            self._refresh_acm_ui_from_current_acm()
            wants_hsv = bool(getattr(self._get_current_acm(), "is_lut4rgb", False))
            if wants_hsv:
                self.ui.radioButton_colorspace_hsv.setChecked(True)
            else:
                self.ui.radioButton_colorspace_yhs.setChecked(True)
            self._config_path_setter(path)
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
