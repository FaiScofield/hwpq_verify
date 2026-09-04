"""
I/O tab controller — encapsulates all IO-related behavior for reuse.
"""

from collections.abc import Callable
import os
import re

import numpy as np
from PIL import Image
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox, QWidget

from script.csc.run_csc import (
    CLRSPC_NAMES,
    CLRSPC_OPTIONS,
    FORMAT_NAMES,
    FMT_OPTIONS,
    get_frame_size,
)
from script.bcsh.hsv_adjust import hsv_to_rgb
from script.img_io import (
    ImageFrame, STB_IMAGE_EXTENSIONS, guess_fmt_from_ext,
    is_limited_range, is_rgb_format, is_yuv_format, get_pixel_depth,
    _PLANAR_RGB_8,
)

try:
    from ..ui_gen.io_ui import Ui_IoUiWidget
except ImportError:
    from ui_gen.io_ui import Ui_IoUiWidget


# ------------------------------------------------------------------ #
# Synthetic test pattern generation                                  #
# ------------------------------------------------------------------ #

def build_test_pattern_rgb(
    kind: str, width: int, height: int, value_v: float = 1.0,
    value_h: float = 0.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generate a synthetic RGB planar test image.

    Returns (R, G, B) uint8 arrays of shape (height, width), full-range RGB.
    kind: "Rainbow Hue Circle" / "Rainbow Hue Ramp" / "HSV Patches dV" /
          "HSV Patches dS" / "Saturation Ramp" / "Value Ramp" / "Gray Ramp".
    value_v: normalized V in [0, 1] used by the patterns with a fixed V
             (Rainbow Hue Circle / Rainbow Hue Ramp / Saturation Ramp /
              HSV Patches dS); ignored by the others.
    value_h: hue in degrees [0, 360) used by Saturation Ramp / Value Ramp.
    """
    if width <= 0 or height <= 0:
        raise ValueError(f"Invalid size: {width}x{height}")
    if not 0.0 <= value_v <= 1.0:
        raise ValueError(f"Invalid V value: {value_v}")
    if not 0.0 <= value_h < 360.0:
        raise ValueError(f"Invalid H value: {value_h}")
    xx = np.linspace(0.0, 1.0, width, dtype=np.float32)      # column position [0,1]
    yy = np.linspace(0.0, 1.0, height, dtype=np.float32)     # row position [0,1]
    if kind == "Rainbow Hue Circle":
        # Circular HSV colour wheel: hue = angle, saturation = radius,
        # value = value_v inside the inscribed circle, white outside.
        # 注意：图像坐标 y 轴向下，直接 atan2(dy,dx) 会让色相在屏幕上顺时针
        # 增大（0° 红 -> 右上 300° 品红）。取反角度使色相按标准色环逆时针
        # 增大：右=0° 红，右上=60° 黄，上=90° 黄绿，左=180° 青……
        cx = (width - 1) * 0.5
        cy = (height - 1) * 0.5
        y_idx, x_idx = np.mgrid[0:height, 0:width].astype(np.float64)
        radius = np.sqrt((x_idx - cx) ** 2 + (y_idx - cy) ** 2)
        max_r = max(1.0, min(width, height) / 2.0)
        h = (360.0 - np.degrees(np.arctan2(y_idx - cy, x_idx - cx))) % 360.0
        s = np.clip(radius / max_r, 0.0, 1.0)
        v = np.full((height, width), value_v, dtype=np.float32)
        outside = radius > max_r
        s[outside] = 0.0   # white background outside the circle
        v[outside] = 1.0
    elif kind == "Rainbow Hue Ramp":
        h = np.tile(xx * 360.0, (height, 1))
        s = np.ones((height, width), dtype=np.float32)
        v = np.full((height, width), value_v, dtype=np.float32)
    elif kind == "HSV Patches dV":
        # 色相×明度色块：12 列色相，6 行明度，V 从上到下 1→0（S 恒 1）。
        n_hue = 12
        n_val = 6
        hue_cols = (np.floor(xx * n_hue) / n_hue * 360.0).astype(np.float32)              # (width,)
        val_rows = (1.0 - np.floor(yy * n_val) / max(1, n_val - 1)).astype(np.float32)    # (height,)
        h = np.tile(hue_cols, (height, 1))
        v = np.tile(val_rows[:, None], (1, width))
        s = np.ones((height, width), dtype=np.float32)
    elif kind == "HSV Patches dS":
        # 色相×饱和度色块：12 列色相，6 行饱和度，S 从上到下 1→0（V 固定为 value_v）。
        n_hue = 12
        n_val = 6
        hue_cols = (np.floor(xx * n_hue) / n_hue * 360.0).astype(np.float32)              # (width,)
        sat_rows = (1.0 - np.floor(yy * n_val) / max(1, n_val - 1)).astype(np.float32)    # (height,)
        h = np.tile(hue_cols, (height, 1))
        s = np.tile(sat_rows[:, None], (1, width))
        v = np.full((height, width), value_v, dtype=np.float32)
    elif kind == "Saturation Ramp":
        h = np.full((height, width), value_h, dtype=np.float32)
        s = np.tile(xx, (height, 1))
        v = np.full((height, width), value_v, dtype=np.float32)
    elif kind == "Value Ramp":
        h = np.full((height, width), value_h, dtype=np.float32)
        s = np.ones((height, width), dtype=np.float32)
        v = np.tile(xx, (height, 1))
    elif kind == "Gray Ramp":
        g = (np.tile(xx, (height, 1)) * 255.0 + 0.5).astype(np.uint8)
        return (g.copy(), g.copy(), g.copy())
    else:
        raise ValueError(f"Unknown test pattern: {kind!r}")
    hsv = np.stack([h, s, v], axis=-1)
    rgb = np.clip(hsv_to_rgb(hsv), 0.0, 1.0)
    rgb_u8 = (rgb * 255.0 + 0.5).astype(np.uint8)
    return rgb_u8[..., 0], rgb_u8[..., 1], rgb_u8[..., 2]


# Suffix token (after '_', case-insensitive) -> format code for .yuv file names.
_YUV_SUFFIX_FMT = {
    "yu24": 0x3,   # YUV444P_YU24
    "nv24": 0x4,   # YUV444SP_NV24
    "vu24": 0x5,   # YUV444I_VU24
    "yu16": 0x6,   # YUV422P_YU16
    "nv16": 0x7,   # YUV422SP_NV16
    "yu12": 0x8,   # YUV420P_YU12
    "nv12": 0x9,   # YUV420SP_NV12
    "gray": 0xA,   # YUV400_Gray
}

_RGB_SUFFIX_FMT = {
    "rgba": 0x1,
    "bgra": 0x1,
    "argb": 0x1,
    "abgr": 0x1,
    "rgb": 0x0,
    "bgr": 0x0,
}


class IoUiWidget(QWidget):
    """Reusable I/O configuration widget."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create the I/O widget from the generated UI definition."""
        super().__init__(parent)
        self.ui = Ui_IoUiWidget()
        self.ui.setupUi(self)


class IoUiController:
    """Controls the I/O tab: init combos, handle signals, and load input data."""

    # ------------------------------------------------------------------ #
    # Initialization                                                     #
    # ------------------------------------------------------------------ #

    def __init__(
        self,
        io_widget: IoUiWidget,
        parent_window: QMainWindow | None = None,
        on_input_loaded: Callable[[object, str], None] | None = None,
        on_load_config: Callable[[str], None] | None = None,
        on_output_changed: Callable[[], None] | None = None,
        status_callback: Callable[[str], None] | None = None,
        auto_load_defaults: bool = True,
    ) -> None:
        """Bind to an IoUiWidget instance and explicit host callbacks.

        Args:
            io_widget: An IoUiWidget whose ``.ui`` provides the I/O controls.
            parent_window: Optional host window kept only for dialog parenting.
            on_input_loaded: Optional callback receiving ``(input_yuv444, status_message)``.
            on_load_config: Optional callback receiving a config path.
            status_callback: Optional callback receiving a status-bar message.
            auto_load_defaults: Whether to auto-load the default input/config during init.
        """
        self._win = parent_window
        self.widget = io_widget
        self.ui = io_widget.ui
        self._on_input_loaded = on_input_loaded
        self._load_config_callback = on_load_config
        self._on_output_changed = on_output_changed
        self._status_callback = status_callback
        self._input_loaded = False
        # 参数猜测级联（格式/色彩空间/帧号变化触发重载）期间抑制装载失败弹窗。
        self._suppress_load_errors = False
        self._init_ui()
        self._connect_signals()
        self._update_swap_controls()
        if auto_load_defaults:
            self._auto_load_defaults()

    def _init_ui(self) -> None:
        """Populate format/colorspace combo boxes with default selections."""
        fmt_display = [f"0x{fmt:x}-{FORMAT_NAMES.get(fmt, 'Unknown')}" for fmt in FMT_OPTIONS]
        self.ui.comboBox_input_format.addItems(fmt_display)
        self.ui.comboBox_output_format.addItems(fmt_display)

        clrspc_display = [f"{clr}-{CLRSPC_NAMES[clr]}" for clr in CLRSPC_OPTIONS]
        clrspc_rgb = [item for item in clrspc_display if int(item.split("-")[0]) in (0, 1)]
        clrspc_yuv = [item for item in clrspc_display if int(item.split("-")[0]) in range(2, 8)]
        self.ui.comboBox_input_colorspace.addItems(clrspc_rgb)
        self.ui.comboBox_output_colorspace.addItems(clrspc_rgb)

        default_yuv_fmt = next((item for item in fmt_display if item.startswith("0x3-")), "")
        if default_yuv_fmt:
            self.ui.comboBox_input_format.setCurrentText(default_yuv_fmt)
            self.ui.comboBox_output_format.setCurrentText(default_yuv_fmt)
        if clrspc_yuv:
            default_yuv_clrspc = clrspc_yuv[3] if len(clrspc_yuv) > 3 else clrspc_yuv[-1]
            self.ui.comboBox_input_colorspace.clear()
            self.ui.comboBox_input_colorspace.addItems(clrspc_yuv)
            self.ui.comboBox_output_colorspace.clear()
            self.ui.comboBox_output_colorspace.addItems(clrspc_yuv)
            self.ui.comboBox_input_colorspace.setCurrentText(default_yuv_clrspc)
            self.ui.comboBox_output_colorspace.setCurrentText(default_yuv_clrspc)

        # 输出 format/colorspace 由用户选择（不再跟随输入）；按输入家族限制刷新 colorspace 选项。
        self.ui.comboBox_output_format.setEnabled(True)
        self.ui.comboBox_output_colorspace.setEnabled(True)
        self._refresh_output_colorspace_options()
        # Test-pattern controls are active only when the test-pattern radio is checked.
        self.ui.comboBox_useTestPattern.setEnabled(False)
        self.ui.label_valueV.setEnabled(False)
        self.ui.spinBox_valueV.setEnabled(False)
        self.ui.spinBox_valueH.setEnabled(False)
        # Remember per-domain colorspace choices (restored when the format
        # switches between the RGB and YUV domains). 默认 RGB->1 全量程、YUV->5 BT.709 full。
        self._last_clrspc_rgb = 1
        clr_str = self.ui.comboBox_input_colorspace.currentText()
        self._last_clrspc_yuv = int(clr_str.split("-")[0]) if clr_str else 5

    def _connect_signals(self) -> None:
        """Wire I/O widget signals to internal handlers."""
        self.ui.pushButton_browse_input.clicked.connect(self._on_browse_input)
        self.ui.pushButton_reload.clicked.connect(self._on_reload_input)
        self.ui.pushButton_browse_output.clicked.connect(self._on_browse_output)
        self.ui.pushButton_open_output.clicked.connect(self._on_open_output_dir)
        self.ui.pushButton_browse_config.clicked.connect(self._on_browse_config)
        self.ui.pushButton_load_config.clicked.connect(self._on_load_config)
        self.ui.comboBox_input_format.currentIndexChanged.connect(self._on_input_format_changed)
        self.ui.comboBox_input_colorspace.currentIndexChanged.connect(self._on_input_colorspace_changed)
        self.ui.comboBox_output_format.currentIndexChanged.connect(self._on_output_format_changed)
        self.ui.comboBox_output_colorspace.currentIndexChanged.connect(self._on_output_colorspace_changed)
        self.ui.radioButton_useSecColor.toggled.connect(self._on_set_color_toggled)
        self.ui.lineEdit_setColor.returnPressed.connect(self._on_set_color_return_pressed)
        self.ui.radioButton_useTestPattern.toggled.connect(self._on_use_test_pattern_toggled)
        self.ui.radioButton_useInputFile.toggled.connect(self._on_use_input_file_toggled)
        self.ui.comboBox_useTestPattern.currentIndexChanged.connect(self._on_test_pattern_combo_changed)
        self.ui.spinBox_valueV.valueChanged.connect(self._on_test_pattern_value_changed)
        self.ui.spinBox_valueH.valueChanged.connect(self._on_test_pattern_value_changed)
        self.ui.spinBox_width.valueChanged.connect(self._on_input_size_changed)
        self.ui.spinBox_height.valueChanged.connect(self._on_input_size_changed)
        self.ui.spinBox_frame_idx.valueChanged.connect(self._on_frame_idx_changed)
        self.ui.checkBox_swapRB.toggled.connect(self._on_swap_toggled)
        self.ui.checkBox_swapUV.toggled.connect(self._on_swap_toggled)

    # ------------------------------------------------------------------ #
    # Public queries                                                     #
    # ------------------------------------------------------------------ #

    def get_input_fmt_code(self) -> int:
        """Return the currently selected input format integer code."""
        fmt_str = self.ui.comboBox_input_format.currentText()
        return int(fmt_str.split("-")[0], 16) if fmt_str else 0

    def get_input_clrspc(self) -> int:
        """Return the currently selected input colorspace integer code."""
        clr_str = self.ui.comboBox_input_colorspace.currentText()
        return int(clr_str.split("-")[0]) if clr_str else 0

    def get_output_fmt_code(self) -> int:
        """Return the currently selected output format integer code."""
        fmt_str = self.ui.comboBox_output_format.currentText()
        return int(fmt_str.split("-")[0], 16) if fmt_str else 0x3

    def get_output_clrspc(self) -> int:
        """Return the currently selected output colorspace integer code."""
        clr_str = self.ui.comboBox_output_colorspace.currentText()
        return int(clr_str.split("-")[0]) if clr_str else 5

    def _allowed_output_clrspcs(self) -> list[int]:
        """按输出 format 域与输入 YUV 家族限制输出 colorspace 选项。

        - 输出 RGB -> {RGB_Limited, RGB_Full}（0/1）
        - 输出 YUV + 输入 RGB -> {BT601/709/2020 × L/F}（2..7）
        - 输出 YUV + 输入 YUV 601/709 -> {BT601, BT709}（2..5，不允许与 2020 互转）
        - 输出 YUV + 输入 YUV 2020 -> {BT2020}（6/7）
        """
        if is_rgb_format(self.get_output_fmt_code()):
            return [0, 1]
        in_fmt = self.get_input_fmt_code()
        if is_rgb_format(in_fmt):
            return list(range(2, 8))
        if self.get_input_clrspc() in (6, 7):
            return [6, 7]
        return [2, 3, 4, 5]

    def _refresh_output_colorspace_options(self, keep_current: bool = True) -> None:
        """重建输出 colorspace 选项；当前值仍合法时保留，否则按输出 format 域
        落到默认全量程（RGB->1 RGB_Full，YUV->5 BT.709 full；5 不可用时如输入
        2020 回落到 7 或列表首个）。

        显示格式与 ``_on_input_format_changed`` 一致（``"{clr}-{name}"``）。
        """
        clrspc_display = [f"{clr}-{CLRSPC_NAMES[clr]}" for clr in self._allowed_output_clrspcs()]
        current = self.ui.comboBox_output_colorspace.currentText()
        self.ui.comboBox_output_colorspace.clear()
        self.ui.comboBox_output_colorspace.addItems(clrspc_display)
        if keep_current and current in clrspc_display:
            self.ui.comboBox_output_colorspace.setCurrentText(current)
            return
        default = 1 if is_rgb_format(self.get_output_fmt_code()) else 5
        item = self._find_clrspc_item(self.ui.comboBox_output_colorspace, default)
        if not item:
            item = self._find_clrspc_item(self.ui.comboBox_output_colorspace, default + 2)
        if not item:
            item = clrspc_display[0]
        self.ui.comboBox_output_colorspace.setCurrentText(item)

    @staticmethod
    def _find_clrspc_item(combo, code: int) -> str:
        """在 combo 中按 colorspace 代码查找显示项文本（兼容有无空格格式）。"""
        for i in range(combo.count()):
            item = combo.itemText(i)
            try:
                if int(item.split("-")[0].strip()) == code:
                    return item
            except ValueError:
                continue
        return ""

    # ------------------------------------------------------------------ #
    # Signal handlers                                                    #
    # ------------------------------------------------------------------ #

    def _on_browse_input(self) -> None:
        """Browse for an input file and load it into memory."""
        path, _ = QFileDialog.getOpenFileName(
            None,
            "Select Input File",
            "",
            "All Files (*.*);;YUV Files (*.yuv);;RGB Files (*.rgb);;Image Files (*.png *.jpg *.bmp)",
        )
        if path:
            self.ui.lineEdit_input_file.setText(path)
            was_checked = self.ui.radioButton_useInputFile.isChecked()
            self.ui.radioButton_useInputFile.setChecked(True)
            if not was_checked:
                # 单选按钮切换已触发 _on_use_input_file_toggled -> _on_reload_input
                # （内部已完成猜测+装载），避免重复装载/重复弹窗。
                return
            # 已处于文件模式：参数猜测期间抑制中间失败弹窗，只保留最终一次。
            self._suppress_load_errors = True
            try:
                self._guess_input_params(path)
                self._recalc_frame_num()
            finally:
                self._suppress_load_errors = False
            self._load_input_image()

    def _on_reload_input(self) -> None:
        """Reload the current input file, re-guessing format/resolution."""
        self.ui.radioButton_useInputFile.setChecked(True)
        path = self.ui.lineEdit_input_file.text()
        if path:
            # 参数猜测会触发格式/色彩空间/帧号信号导致的中间重载，失败弹窗统一
            # 抑制，只在最终装载时报一次错。
            self._suppress_load_errors = True
            try:
                self._guess_input_params(path)
                self._recalc_frame_num()
            finally:
                self._suppress_load_errors = False
            self._load_input_image()

    def _on_browse_output(self) -> None:
        """Browse for an output directory."""
        path = QFileDialog.getExistingDirectory(None, "Select Output Directory")
        if path:
            self.ui.lineEdit_output_dir.setText(path)

    def _on_open_output_dir(self) -> None:
        """Open the configured output directory."""
        path = self.ui.lineEdit_output_dir.text()
        if path and os.path.isdir(path):
            os.startfile(path)

    def _on_browse_config(self) -> None:
        """Browse for an ACM config file."""
        path, _ = QFileDialog.getOpenFileName(None, "Select Config File", "", "JSON Files (*.json)")
        if path:
            self.ui.lineEdit_config_file.setText(path)

    def _on_load_config(self) -> None:
        """Load the ACM config into the current ACM instance."""
        if self._load_config_callback is not None:
            self._load_config_callback(self.ui.lineEdit_config_file.text())

    def _on_input_format_changed(self, index: int) -> None:
        """Update colorspace choices, reload input, and re-run pipeline."""
        del index
        fmt_str = self.ui.comboBox_input_format.currentText()
        if not fmt_str:
            return
        fmt_code = int(fmt_str.split("-")[0], 16)
        clrspc_display = [f"{clr}-{CLRSPC_NAMES[clr]}" for clr in CLRSPC_OPTIONS]
        is_rgb = (fmt_code & 0xF) <= 0x2
        if is_rgb:
            options = [item for item in clrspc_display if int(item.split("-")[0]) in (0, 1)]
        else:
            options = [item for item in clrspc_display if int(item.split("-")[0]) in range(2, 8)]
        # Remember the current domain selection before rebuilding the list.
        current_text = self.ui.comboBox_input_colorspace.currentText()
        if current_text:
            cur_clr = int(current_text.split("-")[0])
            if cur_clr in (0, 1):
                self._last_clrspc_rgb = cur_clr
            else:
                self._last_clrspc_yuv = cur_clr
        # Keep the current colorspace if still valid; otherwise restore the
        # remembered one for the new domain, falling back to the first option.
        if current_text in options:
            idx = options.index(current_text)
        else:
            fallback = self._last_clrspc_yuv if not is_rgb else self._last_clrspc_rgb
            fallback_item = next((it for it in options if it.startswith(f"{fallback}-")), "")
            idx = options.index(fallback_item) if fallback_item else 0
        # 重建色彩空间选项期间阻断信号，避免 _on_input_colorspace_changed 再次触发
        # 重载（一次格式改动只装载/报错一次）；输出 cs 刷新与本函数末尾的装载覆盖之。
        self.ui.comboBox_input_colorspace.blockSignals(True)
        self.ui.comboBox_input_colorspace.clear()
        self.ui.comboBox_input_colorspace.addItems(options)
        self.ui.comboBox_input_colorspace.setCurrentIndex(idx)
        self.ui.comboBox_input_colorspace.blockSignals(False)
        # 输出 format 独立于输入；仅按输入 YUV 家族限制刷新输出 colorspace 选项。
        self._refresh_output_colorspace_options()
        self._update_swap_controls()
        self._recalc_frame_num()
        self._load_input_image()

    def _on_input_colorspace_changed(self, index: int) -> None:
        """Reload the input since reading uses the selected colorspace, and
        refresh the output colorspace options (YUV family restriction)."""
        del index
        self._refresh_output_colorspace_options()
        self._load_input_image()

    def _on_output_format_changed(self, index: int) -> None:
        """Output format changed: refresh colorspace options and re-run pipeline."""
        del index
        self._refresh_output_colorspace_options()
        if self._on_output_changed is not None:
            self._on_output_changed()

    def _on_output_colorspace_changed(self, index: int) -> None:
        """Output colorspace changed: re-run pipeline."""
        del index
        if self._on_output_changed is not None:
            self._on_output_changed()

    # ------------------------------------------------------------------ #
    # Input channel swap (R/B for RGB, U/V for YUV)                      #
    # ------------------------------------------------------------------ #

    def _update_swap_controls(self) -> None:
        """Enable the matching swap checkbox for file input.

        Swap R/B is offered for RGB formats, Swap U/V for YUV formats; both
        are disabled when the input source is not a file (test pattern or
        solid colour).
        """
        is_file = self.ui.radioButton_useInputFile.isChecked()
        fmt_str = self.ui.comboBox_input_format.currentText()
        fmt_code = int(fmt_str.split("-")[0], 16) if fmt_str else 0
        is_rgb = is_rgb_format(fmt_code)

        if not is_file:
            self.ui.checkBox_swapRB.setEnabled(False)
            self.ui.checkBox_swapUV.setEnabled(False)
            return
        if is_rgb:
            self.ui.checkBox_swapRB.setEnabled(True)
            self.ui.checkBox_swapUV.setEnabled(False)
            # Uncheck the irrelevant checkbox without triggering a reload.
            self.ui.checkBox_swapUV.blockSignals(True)
            self.ui.checkBox_swapUV.setChecked(False)
            self.ui.checkBox_swapUV.blockSignals(False)
        else:
            self.ui.checkBox_swapRB.setEnabled(False)
            self.ui.checkBox_swapUV.setEnabled(True)
            self.ui.checkBox_swapRB.blockSignals(True)
            self.ui.checkBox_swapRB.setChecked(False)
            self.ui.checkBox_swapRB.blockSignals(False)

    def _on_swap_toggled(self, checked: bool) -> None:
        """Reload the file input so the new channel order takes effect."""
        del checked
        if self.ui.radioButton_useInputFile.isChecked():
            self._load_input_image()

    def _apply_swap(self, frame: ImageFrame) -> ImageFrame:
        """Swap input channels according to the active swap checkbox.

        R/B are swapped for RGB frames, U/V for YUV frames. Operates in place
        and returns the same frame.
        """
        if self.ui.checkBox_swapRB.isChecked() and frame.is_rgb:
            frame.pyr, frame.pvb = frame.pvb, frame.pyr
        elif self.ui.checkBox_swapUV.isChecked() and frame.is_yuv:
            frame.pug, frame.pvb = frame.pvb, frame.pug
        return frame

    def _on_test_pattern_combo_changed(self, index: int) -> None:
        """Auto-generate the selected test pattern when the combo changes."""
        del index
        self._on_generate_test_pattern()

    def _on_test_pattern_value_changed(self, value: int) -> None:
        """Regenerate the test pattern when the H/V value changes."""
        del value
        self._on_generate_test_pattern()

    def _on_input_size_changed(self, value: int) -> None:
        """Regenerate the current input when the width/height changes.

        Test patterns are re-rendered at the new resolution; the specified
        color is rebuilt as a solid frame of the new size.  File mode is left
        untouched (resolution is a load parameter there, applied via Reload).
        """
        del value
        if self.ui.radioButton_useTestPattern.isChecked():
            self._on_generate_test_pattern()
        elif self.ui.radioButton_useSecColor.isChecked():
            self._load_set_color_input()

    def _on_frame_idx_changed(self, value: int) -> None:
        """Reload the file input at the newly selected frame index."""
        del value
        if self.ui.radioButton_useInputFile.isChecked():
            self._load_input_image()

    def _on_use_test_pattern_toggled(self, enabled: bool) -> None:
        """Enable the test-pattern controls and load the selected pattern as input."""
        self.ui.comboBox_useTestPattern.setEnabled(enabled)
        self.ui.label_valueV.setEnabled(enabled)
        self.ui.label_valueH.setEnabled(enabled)
        self.ui.spinBox_valueV.setEnabled(enabled)
        self.ui.spinBox_valueH.setEnabled(enabled)
        self._update_swap_controls()
        if not enabled:
            return   # exclusive group: the newly-checked radio performs the load
        # Test patterns are full-range RGB: force input format 0x0 / colorspace 0x1.
        # If the format changed, the format-change handler already regenerated.
        if not self._set_test_pattern_input_fmt():
            # The combo always holds a valid pattern (no "None" entry); generate it.
            self._on_generate_test_pattern()

    def _set_test_pattern_input_fmt(self) -> bool:
        """Force the input format to 0x0 (RGB888) and colorspace to 0x1 (RGB_Full).

        Returns True when the format combo actually changed (the format-change
        handler then already regenerated the pattern); False otherwise.
        """
        fmt_items = [self.ui.comboBox_input_format.itemText(i)
                     for i in range(self.ui.comboBox_input_format.count())]
        fmt_item = next((it for it in fmt_items if it.startswith("0x0-")), "")
        changed = False
        if fmt_item and self.ui.comboBox_input_format.currentText() != fmt_item:
            self.ui.comboBox_input_format.setCurrentText(fmt_item)
            changed = True
        clrspc_item = self._find_clrspc_item(self.ui.comboBox_input_colorspace, 1)
        if clrspc_item:
            self.ui.comboBox_input_colorspace.setCurrentText(clrspc_item)
        return changed

    def _on_use_input_file_toggled(self, enabled: bool) -> None:
        """Update the swap controls, and reload the file input (re-guess
        format/resolution) when the file-source radio is selected."""
        self._update_swap_controls()
        if enabled:
            self._on_reload_input()

    def _on_generate_test_pattern(self) -> None:
        """Generate the selected synthetic test pattern at the current resolution."""
        if not self.ui.radioButton_useTestPattern.isChecked():
            return
        kind = self.ui.comboBox_useTestPattern.currentText()
        if not kind:
            return
        width = self.ui.spinBox_width.value()
        height = self.ui.spinBox_height.value()
        value_v = self.ui.spinBox_valueV.value() / 255.0
        value_h = self.ui.spinBox_valueH.value()
        try:
            r, g, b = build_test_pattern_rgb(kind, width, height, value_v, value_h)
        except Exception as exc:
            QMessageBox.critical(None, "Error", f"Failed to generate test pattern: {exc}")
            return
        frame = ImageFrame(r, g, b, _PLANAR_RGB_8, 1)
        self._emit_input_loaded(
            frame, f"Test pattern generated: {kind}, V={self.ui.spinBox_valueV.value()}, H={value_h}, size: {width}x{height}")

    # ------------------------------------------------------------------ #
    # Auto-load defaults on startup                                       #
    # ------------------------------------------------------------------ #

    def _auto_load_defaults(self) -> None:
        """Auto-load the input image and config file if defaults are valid."""
        input_path = self.ui.lineEdit_input_file.text().strip()
        config_path = self.ui.lineEdit_config_file.text().strip()

        input_loaded = False
        if input_path and os.path.isfile(input_path):
            self._on_reload_input()
            input_loaded = True

        config_loaded = False
        if config_path and os.path.isfile(config_path) and self._load_config_callback:
            self._load_config_callback(config_path)
            config_loaded = True

        if self._status_callback:
            if input_loaded and config_loaded:
                self._status_callback("Auto-loaded input image and config.")
            elif input_loaded:
                self._status_callback("Auto-loaded input image.")

    def auto_load_defaults(self) -> None:
        """Public wrapper used by the host after all dependent controllers exist."""
        self._auto_load_defaults()

    def _on_set_color_toggled(self, enabled: bool) -> None:
        """Enable/disable the explicit-color edit; the newly-checked source
        radio's own handler performs the load."""
        self.ui.lineEdit_setColor.setEnabled(enabled)
        self._update_swap_controls()
        if not enabled:
            return
        # Clear any previous error style so the user starts fresh
        self.ui.lineEdit_setColor.setStyleSheet("")
        self._load_input_image()

    def _guess_input_params(self, filepath: str) -> None:
        """Guess format and resolution from the selected input file name.

        Resolution is guessed before the format so that the format-change
        handler (which reloads the input) never runs with stale width/height.
        """
        basename = os.path.basename(filepath).lower()
        ext = os.path.splitext(basename)[-1]

        # --- Resolution first ---
        if ext in STB_IMAGE_EXTENSIONS:
            try:
                with Image.open(filepath) as image:
                    width, height = image.size
                self.ui.spinBox_width.setValue(width)
                self.ui.spinBox_height.setValue(height)
            except Exception:
                pass
        match = re.search(r"(\d+)x(\d+)", basename)
        if match:
            self.ui.spinBox_width.setValue(int(match.group(1)))
            self.ui.spinBox_height.setValue(int(match.group(2)))

        # --- Format after ---
        fmt_display = [f"0x{fmt:x}-{FORMAT_NAMES.get(fmt, 'Unknown')}" for fmt in FMT_OPTIONS]
        if ext in STB_IMAGE_EXTENSIONS:
            fmt_code = 0x0
        elif ext == ".yuv":
            fmt_code = next(
                (code for token, code in _YUV_SUFFIX_FMT.items()
                 if f"_{token}" in basename),
                0x3,   # default YUV444P_YU24 when no token matches
            )
        elif ext == ".rgb":
            fmt_code = 0x1 if "_rgba" in basename else 0x0
            fmt_code = next(
                (code for token, code in _RGB_SUFFIX_FMT.items()
                    if f"_{token}" in basename),
                0x0,   # default RGB888 when no token matches
            )
        else:
            # raw .bin：先匹配 YUV token，再匹配 RGB token，默认 RGB888(0x0)。
            fmt_code = next(
                (code for token, code in _YUV_SUFFIX_FMT.items()
                 if f"_{token}" in basename),
                next(
                    (code for token, code in _RGB_SUFFIX_FMT.items()
                     if f"_{token}" in basename),
                    0x0,
                ),
            )

        # 猜测格式后的默认色彩空间：RGB -> RGB_Full(1)，YUV -> BT709_Full(5)。
        default_cs = 1 if is_rgb_format(fmt_code) else 5

        fmt_item = next(
            (item for item in fmt_display if item.startswith(f"0x{fmt_code:x}")), None)
        if fmt_item:
            self.ui.comboBox_input_format.setCurrentText(fmt_item)

        # 输入色彩空间默认 1（RGB）/ 5（YUV）。
        in_item = self._find_clrspc_item(self.ui.comboBox_input_colorspace, default_cs)
        if in_item:
            self.ui.comboBox_input_colorspace.setCurrentText(in_item)

        # 猜测格式后，输出格式/色彩空间默认跟随输入（用户之后仍可手动修改）。
        # 先同步输出 format（触发输出 cs 选项按新域/家族刷新），再按代码匹配设置输出 cs。
        self.ui.comboBox_output_format.setCurrentText(self.ui.comboBox_input_format.currentText())
        self._refresh_output_colorspace_options()
        out_item = self._find_clrspc_item(self.ui.comboBox_output_colorspace, default_cs)
        if out_item:
            self.ui.comboBox_output_colorspace.setCurrentText(out_item)

    def _recalc_frame_num(self) -> None:
        """Recalculate frame count from the selected file and format."""
        input_file = self.ui.lineEdit_input_file.text()
        if not input_file or not os.path.isfile(input_file):
            return

        ext = os.path.splitext(input_file)[1].lower()
        if ext in STB_IMAGE_EXTENSIONS:
            self.ui.spinBox_frame_num.setValue(1)
            self.ui.spinBox_frame_idx.setMaximum(0)
            return

        fmt_str = self.ui.comboBox_input_format.currentText()
        if not fmt_str:
            return
        fmt_code = int(fmt_str.split("-")[0], 16)
        width = self.ui.spinBox_width.value()
        height = self.ui.spinBox_height.value()
        frame_size = get_frame_size(width, height, fmt_code)
        actual_size = os.path.getsize(input_file)
        frame_num = max(1, actual_size // frame_size) if frame_size > 0 else 1
        self.ui.spinBox_frame_num.setValue(frame_num)
        # Frame index is 0-based: valid range is [0, frame_num - 1].
        self.ui.spinBox_frame_idx.setMaximum(max(0, frame_num - 1))

    # ------------------------------------------------------------------ #
    # Image loading                                                      #
    # ------------------------------------------------------------------ #

    def get_output_dir(self) -> str:
        """Return the currently configured output directory."""
        return self.ui.lineEdit_output_dir.text()

    def get_config_path(self) -> str:
        """Return the currently configured ACM config path."""
        return self.ui.lineEdit_config_file.text()

    def set_config_path(self, path: str) -> None:
        """Update the visible ACM config path."""
        self.ui.lineEdit_config_file.setText(path)

    def _emit_input_loaded(self, frame: ImageFrame, status_message: str) -> None:
        """Publish a successfully loaded input image to the host."""
        if self._on_input_loaded is not None:
            self._on_input_loaded(frame, status_message)
        elif self._status_callback is not None:
            self._status_callback(status_message)

    def _load_set_color_input(self) -> None:
        """Build a solid-colour ImageFrame from the set-color fields.

        The three channel values are interpreted at the selected format's bit
        depth (0..255 for 8-bit, 0..1023 for 10-bit) and as RGB or YUV
        depending on the input format.  Out-of-range values are rejected with
        a warning (text turns red; the user re-enters or switches source)
        instead of being clamped.  Limited-range colorspaces clamp valid
        values to the spec-defined ranges.
        """
        color_str = self.ui.lineEdit_setColor.text().strip()
        parsed = self._parse_color_text(color_str)
        if parsed is None:
            QMessageBox.warning(None, "Warning", "Invalid color format. Use three numbers separated by spaces or commas (e.g. 128,128,128 or 128 128 128)")
            self.ui.lineEdit_setColor.setStyleSheet("color: #ff0000;")
            return
        c1, c2, c3 = parsed
        fmt_str = self.ui.comboBox_input_format.currentText()
        if not fmt_str:
            return
        fmt_code = int(fmt_str.split("-")[0], 16)
        clrspc = self.get_input_clrspc()
        depth = get_pixel_depth(fmt_code)
        limited = is_limited_range(clrspc)
        width = self.ui.spinBox_width.value()
        height = self.ui.spinBox_height.value()

        # Reject values outside the format's bit-depth range (no silent clamp).
        max_val = 1023 if depth >= 10 else 255
        if any(v < 0 or v > max_val for v in (c1, c2, c3)):
            self.ui.lineEdit_setColor.setStyleSheet("color: #ff0000;")
            QMessageBox.warning(
                None, "Warning",
                f"Value out of range for {depth}-bit input. Use values in [0, {max_val}].",
            )
            return

        # Clamp valid values to the limited-range window (depth-scaled).
        if limited:
            if depth >= 10:
                lo_y, hi_y, hi_uv = 64, 940, 960
            else:
                lo_y, hi_y, hi_uv = 16, 235, 240
            if is_yuv_format(fmt_code):
                # Y: [lo_y, hi_y], U/V: [lo_y, hi_uv]
                c1 = max(lo_y, min(hi_y, c1))
                c2 = max(lo_y, min(hi_uv, c2))
                c3 = max(lo_y, min(hi_uv, c3))
            else:
                # RGB: [lo_y, hi_y]
                c1 = max(lo_y, min(hi_y, c1))
                c2 = max(lo_y, min(hi_y, c2))
                c3 = max(lo_y, min(hi_y, c3))

        channel_label = "YUV" if is_yuv_format(fmt_code) else "RGB"
        if is_yuv_format(fmt_code):
            frame = ImageFrame.from_solid_yuv(
                width, height, c1, c2, c3, clrspc, depth,
            )
        else:
            frame = ImageFrame.from_solid_color(
                width, height, c1, c2, c3, clrspc, depth,
            )
        self.ui.lineEdit_setColor.setStyleSheet("")
        self._emit_input_loaded(
            frame,
            f"Input generated ({channel_label} {c1}, {c2}, {c3}) "
            f"{'limited' if limited else 'full'} range, {depth}-bit, "
            f"size: {width}x{height}",
        )

    def _on_set_color_return_pressed(self) -> None:
        """Parse the set-color text when Enter is pressed.

        On success the text colour stays default; on failure the text turns
        red and a warning is shown.
        """
        color_str = self.ui.lineEdit_setColor.text().strip()
        parsed = self._parse_color_text(color_str)
        if parsed is None:
            QMessageBox.warning(
                None, "Warning",
                "Invalid color format. Use three numbers separated by spaces or commas (e.g. 128,128,128 or 128 128 128)",
            )
            self.ui.lineEdit_setColor.setStyleSheet("color: #ff0000;")
            return
        self.ui.lineEdit_setColor.setStyleSheet("")
        self._load_input_image()

    @staticmethod
    def _parse_color_text(text: str) -> tuple[int, int, int] | None:
        """Parse 'C1 C2 C3' or 'C1,C2,C3' into three ints. Returns None on failure."""
        parts = re.split(r'[,\s]+', text.strip())
        parts = [p for p in parts if p]
        if len(parts) != 3:
            return None
        try:
            return tuple(map(int, parts))
        except ValueError:
            return None

    def _load_input_image(self) -> None:
        """Load input data as an ImageFrame and notify parent."""
        input_file = self.ui.lineEdit_input_file.text()

        if self.ui.radioButton_useSecColor.isChecked():
            self._load_set_color_input()
            return
        if self.ui.radioButton_useTestPattern.isChecked():
            self._on_generate_test_pattern()
            return

        if not input_file or not os.path.isfile(input_file):
            return

        fmt_str = self.ui.comboBox_input_format.currentText()
        if not fmt_str:
            return
        fmt_code = int(fmt_str.split("-")[0], 16)
        width = self.ui.spinBox_width.value()
        height = self.ui.spinBox_height.value()
        frame_idx = self.ui.spinBox_frame_idx.value()
        clrspc = self.get_input_clrspc()

        try:
            ext = os.path.splitext(input_file)[1].lower()
            if ext in STB_IMAGE_EXTENSIONS:
                frame = ImageFrame.from_image(input_file, clrspc)
            else:
                frame = ImageFrame.from_file(
                    input_file, width, height, fmt_code, clrspc, frame_idx,
                )
            frame = self._apply_swap(frame)
            self._emit_input_loaded(
                frame, f"Input loaded: {frame.width}x{frame.height}, idx={frame_idx}")
            self._input_loaded = True
        except Exception as exc:
            if self._suppress_load_errors:
                return
            QMessageBox.critical(None, "Error", f"Failed to load image: {exc}")
