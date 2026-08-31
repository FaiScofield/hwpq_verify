"""
HSV tab controller — encapsulates all HSV-related UI behavior and state.

调整语义（对应 script/bcsh/hsv_adjust.py）：
  B：Contrast 乘性 + delta_b（加性/乘性由 comboBox_modeB 选择），
     增益参考点由 comboBox_modeC 选择：GainAtMid（v=0.5 中点）/ GainAtZero
     （过 v=0 原点）/ GainAtBoth（按 gc<1 或 >1 自动选择）/ TanSlant
     （c∈[-1,1]，增益=tan((c+1)π/4)）/ FastStone（仅 RGB 域，C∈[-1,1]，
     归一化到 [-100,100] 做逐通道 Levels 拉伸 out=clip(k·in+b)）
     modeB: ModeAdd 加性偏移 / ModeMul 乘性增益 / NegMulPosRat（δV∈[-1,1]：
     负值乘性压缩、正值按进度向白靠拢，极值纯黑/纯白）
  S：comboBox_modeS 切换加性/乘性  s'=clip(s+ds) / s'=clip(s*ds)；
     RGB 域禁用 ModeS，恒为 scale 灰阶混合 out=scale*in+(1-scale)*gray(in)
  H：comboBox_goalH 选择目标——SameOffset 恒为加性偏移（默认）；SameTarget 向指定
     目标色调旋转（激活 Same Hue Goal 行控件）；comboBox_modeH 选择生效方式——
     ModeAdd 加性色相平移（所有域；RGB 域即 FastStone 兼容的六边形 HSV 加法）；
     RotateOnGray（绕灰轴）仅 RGB 域
指定色调（groupBox_setHueRange 勾选）：仅色调落在 [hs, he] 附近的像素被处理，
通过 Tail（向内）/ Pad（向外）的 alpha blending 过渡。

comboBox_adjustField 选择处理域（8 选项）：
  HSV/HSI/HSL/HCY/HSP/Lch/RGB（RGB 系）：full-range RGB <-> 对应域，域内 BCSH 调整。
     Lch 为 sRGB D65 -> CIELAB 柱坐标，s=C/Cmax 归一化、l=L/100 归一化。
     HCY 为 Hue/Chroma/Luma（Rec.601 luma，六边形色相），c/y 归一化 [0,1]，
     同 Y 亮度一致。
     HSP 为 Hue/Saturation/Perceived brightness（感知亮度 sqrt(ΣW·c²)，
     与 HSV 相同的饱和度），s/p 归一化 [0,1]，同 P 亮度一致。
     RGB 为直接 RGB 域处理：C/V 三通道一致、S 灰阶混合、H 灰色轴旋转。
  YCbCr（YUV 系）：处理域为 yuv444p full-range，uv 去中心 0.5 得 YCbCr；
     Y 通道调 B/C，Cb(x)/Cr(y) 极坐标系调 H(角度)/S(极径)。
统一流水线（1️⃣~6️⃣）：1️⃣ 原始输入直读 -> 2️⃣ 输入 CSC 到处理域（y2rClipType
  决定 YUV->RGB 转换的钳位：HardClip 硬钳 / SoftClip 色相保持软钳 / ConstHue
  恒定色相等比缩放；RGB 输入 limited->full 展开直接硬钳）-> 3️⃣ 域转换（有钳位）
  -> 4️⃣ BCSH 调整 -> 5️⃣ 回 full-range RGB/YUV（y2yClipType 统一色域处理策略：
  HardClip YUV 硬钳 / ClipChroma 保 Y、沿色相缩色度 / ScaleChromaPix 按像素边界
  归一化 S（域内免钳）/ ScaleChromaSec 按全局最大归一化（越界走 HardClip）/
  CompLumaOnly 保色度调亮度 / CompLumaFirst 调亮度优先、不足缩色度兜底）
  -> 6️⃣ 输出 CSC 到输出格式/色彩空间（YUV 输出直接编码，不经 RGB；必钳）。
"""

from collections.abc import Callable
from dataclasses import dataclass
import time

import numpy as np
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QLineEdit, QMainWindow, QWidget

from script.bcsh.hsv_adjust import (
    adjust_hsv, adjust_rgb, rgb_to_hsv, hsv_to_rgb,
    rgb_to_hsi, hsi_to_rgb, rgb_to_hsl, hsl_to_rgb,
    rgb_to_lch, lch_to_rgb, rgb_to_hcy, hcy_to_rgb,
    rgb_to_hsp, hsp_to_rgb,
)
from script.img_io import (
    ImageFrame, _csc_range_params, _get_csc_matrices, is_limited_range,
    is_rgb_format, rgb_to_yuv,
    _PLANAR_RGB_8, _PLANAR_RGB_10, _PLANAR_YUV_8, _PLANAR_YUV_10,
)

try:
    from ..params_config import SLIDER_SCALE, load_params, param_entry
except ImportError:
    from params_config import SLIDER_SCALE, load_params, param_entry

try:
    from ..ui_gen.hsv_ui import Ui_HsvUiWidget
except ImportError:
    from ui_gen.hsv_ui import Ui_HsvUiWidget


def _bt_chroma_max(cs: int) -> float:
    """某色彩空间一次/二次色最大色度极径（YCbCr 极坐标 S 归一化因子）。"""
    r2y, _ = _get_csc_matrices(cs)
    primaries = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1], # RGBYCM
                          [1, 1, 0], [0, 1, 1], [1, 0, 1]], dtype=np.float32)
    pts = primaries @ r2y[1:, :].T                      # (6, 2): (Cb, Cr)
    return float(np.max(np.sqrt(np.sum(pts ** 2, axis=1))))


def _build_hue_sync_lut(cs: int, n: int = 4096) -> tuple[np.ndarray, np.ndarray]:
    """构建 HSV 色相 -> YCbCr 极角（去 360° 环绕、单调）LUT，供双向同步换算。

    HSV 色相按六边形等角分布；YCbCr 极角是 Cb/Cr 平面真实角度，两者相差一个
    非恒定偏移（随矩阵族变化）。该 LUT 使两者可精确互转（往返 0.000°）。
    """
    r2y, _ = _get_csc_matrices(cs)
    hsv = np.linspace(0.0, 360.0, n, endpoint=False)
    rgb = hsv_to_rgb(np.stack([hsv, np.ones(n), np.ones(n)], axis=-1))
    chroma = rgb @ r2y[1:, :].T                            # (n, 2): (Cb, Cr)
    ycbcr = (np.degrees(np.arctan2(chroma[:, 1], chroma[:, 0])) + 360.0) % 360.0
    ycbcr_unwrap = np.unwrap(np.radians(ycbcr)) * 180.0 / np.pi
    return hsv, ycbcr_unwrap


# YUV 处理域按矩阵族（BT.601/709/2020 代表代码 2/4/6）参数化的色相同步 LUT 与色度归一化因子。
_HUE_LUTS = {2: _build_hue_sync_lut(2), 4: _build_hue_sync_lut(4), 6: _build_hue_sync_lut(6)}
_CHROMA_MAX = {2: _bt_chroma_max(2), 4: _bt_chroma_max(4), 6: _bt_chroma_max(6)} # BY=0.5021, RC=0.5130, GM=0.5957

# 处理域数据钳位策略（档位由 .ui 定义；见 comboBox_y2rClipType / comboBox_y2yClipType）：
#   y2rClipType（YUV->RGB 转换钳位）：HardClip 逐通道硬钳 / SoftClip 色相保持
#     软钳（zentone soft_clip）/ ConstHue 恒定色相等比例缩放（负值先钳 0）。
#   y2yClipType（YCbCr 处理域统一色域处理策略，仅 YCbCr field 启用）：
#     HardClip YUV 范围硬钳 / ClipChroma 保 Y、沿色相缩色度到 r_max(Y,θ) /
#     ScaleChromaPix 按该像素边界半径 r_max(Y,θ) 归一化 S（S∈[0,1] 域内免钳，
#     Y/S/H 解耦）/ ScaleChromaSec 按全局最大 _CHROMA_MAX 归一化（不保证域内，
#     越界像素按 HardClip 兜底）/ CompLumaOnly 保色度、调 Y 拉回域内 /
#     CompLumaFirst 调 Y 优先、Y 单独不够时缩色度到 r* 并顶 Y 到 Y* 兜底。


# RGB 系处理域（Adjust Field != YCbCr）的域转换函数表。
# Lch：sRGB D65 -> Lab 柱坐标，s=C/Cmax 归一化、l=L/100 归一化。
# HCY：Hue/Chroma/Luma，Rec.601 luma，六边形色相；c/y 归一化 [0,1]。
# HSP：Hue/Saturation/Perceived brightness，感知亮度 sqrt(ΣW·c²) + HSV 饱和度；s/p 归一化 [0,1]。
# RGB：直接 RGB 域，to/from 均为恒等（钳位 [0,1]）。
def _rgb_domain_to(rgb):
    """RGB 处理域 to_domain：恒等返回三通道（域内钳位 [0,1]）。"""
    rgb = np.clip(np.asarray(rgb, dtype=np.float32), 0.0, 1.0)
    return rgb[..., 0], rgb[..., 1], rgb[..., 2]


def _rgb_domain_from(dom):
    """RGB 处理域 from_domain：恒等（钳位 [0,1]）。"""
    return np.clip(np.asarray(dom, dtype=np.float32), 0.0, 1.0)


_DOMAIN_CONVERTERS = {
    "HSV": (rgb_to_hsv, hsv_to_rgb),
    "HSI": (rgb_to_hsi, hsi_to_rgb),
    "HSL": (rgb_to_hsl, hsl_to_rgb),
    "HCY": (rgb_to_hcy, hcy_to_rgb),
    "HSP": (rgb_to_hsp, hsp_to_rgb),
    "Lch": (rgb_to_lch, lch_to_rgb),
    "RGB": (_rgb_domain_to, _rgb_domain_from),
}


@dataclass
class PixelReadoutCache:
    """一次处理的像素读数缓存（全分辨率，源位深 float/原生）。

    输入侧：in_native(1️⃣) / in_full_rgb·in_full_yuv(2️⃣, 视 clip 钳位/未钳位) / in_domain(3️⃣)。
    输出侧：out_native(6️⃣) / out_full_rgb·out_full_yuv(5️⃣, 视 clip) / out_domain(4️⃣)。
    """

    in_native: tuple                       # (kind, (planes), depth)，kind='rgb'/'yuv'
    in_full_rgb: np.ndarray | None         # (H,W,3) float full-range RGB（RGB 系处理域）
    in_full_yuv: np.ndarray | None         # (H,W,3) float (Y, cb, cr)（YCbCr 处理域）
    in_yuv_cs: int                         # in_full_yuv 的 colorspace 代码
    in_domain: tuple                       # (name, h, s, x) 步骤 3️⃣
    out_native: tuple                      # 输出帧 6️⃣ 的原生值 (kind, (planes), depth)
    out_full_rgb: np.ndarray | None        # (H,W,3) 步骤 5️⃣ RGBF
    out_full_yuv: np.ndarray | None        # (H,W,3) 步骤 5️⃣ YUVF
    out_yuv_cs: int                        # out_full_yuv 的 colorspace 代码
    out_domain: tuple                      # (name, h, s, x) 步骤 4️⃣


def _cs_family(cs: int) -> int:
    """Colorspace 代码 -> 矩阵族代表代码（601->2，709->4，2020->6）。"""
    return {0: 1, 1: 1, 2: 2, 3: 2, 4: 4, 5: 4, 6: 6, 7: 6}.get(cs, 4)


def hue_hsv_to_ycbcr(h, cs: int = 4) -> np.ndarray:
    """HSV 色相 -> YCbCr 极角（[0,360)）。按色彩空间矩阵；支持标量或数组。"""
    hsv, ycbcr = _HUE_LUTS[_cs_family(cs)]
    return np.interp(np.asarray(h, dtype=np.float64), hsv, ycbcr) % 360.0


def hue_ycbcr_to_hsv(h, cs: int = 4) -> np.ndarray:
    """YCbCr 极角 -> HSV 色相（[0,360)）。按色彩空间矩阵；处理 <起点 的环绕段。"""
    hsv, ycbcr = _HUE_LUTS[_cs_family(cs)]
    x = np.asarray(h, dtype=np.float64) % 360.0
    start = float(ycbcr[0])
    x = np.where(x < start, x + 360.0, x)                # [0,起点) 段 +360 对齐到单调区间
    return np.interp(x, ycbcr, hsv) % 360.0


class HsvUiWidget(QWidget):
    """Reusable HSV configuration widget."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create the HSV widget from the generated UI definition."""
        super().__init__(parent)
        self.ui = Ui_HsvUiWidget()
        self.ui.setupUi(self)


class HsvUiController:
    """Controls the HSV tab: V/S/H adjustment and specified-hue processing."""

    # comboBox_modeS 两类互斥选项：圆柱色域 S 模式 / RGB 域灰阶混合（MixGray）。
    _MODE_S_RGB = ("MixGray_BT709", "MixGray_BT601")
    # comboBox_modeH 的 Rotate 系列（仅 RGB 处理域可选）。
    _MODE_H_ROTATE = ("RotateOnGray",)
    # comboBox_modeC 的 FastStone（仅 RGB 处理域可选）。
    _MODE_C_RGB = ("FastStone",)

    # ------------------------------------------------------------------ #
    # Initialization                                                     #
    # ------------------------------------------------------------------ #

    def __init__(
        self,
        hsv_widget: HsvUiWidget,
        parent_window: QMainWindow | None = None,
        input_provider: Callable[[], ImageFrame | None] | None = None,
        output_callback: Callable[[ImageFrame], None] | None = None,
        status_callback: Callable[[str], None] | None = None,
        time_cost_callback: Callable[[float], None] | None = None,
        work_size_provider: Callable[[int, int], tuple[int, int]] | None = None,
        input_pixel_edit: QLineEdit | None = None,
        output_pixel_edit: QLineEdit | None = None,
        params: dict | None = None,
        output_fmt_provider: Callable[[], int] | None = None,
        output_clrspc_provider: Callable[[], int] | None = None,
    ) -> None:
        """Bind to an HsvUiWidget instance and explicit host callbacks.

        Args:
            hsv_widget: An HsvUiWidget whose ``.ui`` provides the HSV controls.
            parent_window: Optional host window kept for dialog parenting.
            input_provider: Optional callback returning the current input frame.
            output_callback: Optional callback receiving the processed output frame.
            status_callback: Optional callback receiving status-bar text.
            time_cost_callback: Optional callback receiving the processing time in ms.
            work_size_provider: Optional callback returning the processing size
                (w, h) for a source size (w, h) — used to downsample the preview
                pass for responsiveness.
            input_pixel_edit / output_pixel_edit: preview readout QLineEdits that
                show the frozen pixel's RGB+HSV values (input / output).
        """
        self._win = parent_window
        self.widget = hsv_widget
        self.ui = hsv_widget.ui
        self._input_provider = input_provider or (lambda: None)
        self._output_callback = output_callback or (lambda output: None)
        self._status_callback = status_callback or (lambda message: None)
        self._time_cost_callback = time_cost_callback
        self._work_size_provider = work_size_provider
        self._input_pixel_edit = input_pixel_edit
        self._output_pixel_edit = output_pixel_edit
        self._output_fmt_provider = output_fmt_provider
        self._output_clrspc_provider = output_clrspc_provider

        # B/C/S/H 取值范围/步长配置（JSON 可覆盖；注入便于测试）。
        if params is None:
            params, _loaded = load_params()
        self._params = params

        self._latest_output_frame: ImageFrame | None = None
        self._latest_preview_frame: ImageFrame | None = None
        self._last_readout: PixelReadoutCache | None = None
        self._frozen_pixel: tuple[int, int] | None = None
        self._input_is_rgb = True     # 源输入帧是否为 RGB（决定像素读数链路前缀）
        self._s_mode = 'mul'          # 'add'/'mul'（S 通道模式，.ui 默认 Mul）
        self._b_mode = 'add'          # 'add'/'mul'（B 通道模式，.ui 默认 Add）
        self._work_size: tuple[int, int] | None = None   # 最近一次预览处理的分辨率

        # --- Auto-run debounce timer ---
        self.auto_run_timer = QTimer(self.widget)
        self.auto_run_timer.setSingleShot(True)
        self.auto_run_timer.timeout.connect(self._do_auto_run)

        self._connect_signals()
        self._init_state()

    def _init_state(self) -> None:
        """Perform initial state sync after all widgets are ready."""
        # .ui 默认 S=Multiplicative、V=Additive：同步各通道模式内部状态并
        # 应用其控件范围/中性值。
        self._s_mode = self._s_mode_code()
        self._b_mode = self._b_mode_code()
        self._apply_c_ui()
        self._apply_s_mode_ui(self._s_mode)
        self._apply_b_mode_ui(self._b_mode)
        self._update_hue_limits()
        self._on_h_mode_changed()
        # A checkable QGroupBox defaults to checked=True; the specified-hue
        # adjustment must be OFF by default so the whole image is processed.
        self.ui.groupBox_setHueRange.setChecked(False)
        # 钳位/归一化下拉使能随处理域与输入格式更新。
        self._update_clip_enables()
        # comboBox_modeS 的 MixGray 项仅在 RGB 处理域可选。
        self._set_mode_s_items_enabled(self._adjust_field() == "RGB")
        # comboBox_modeH 的 Rotate 系列仅在 RGB 处理域可选。
        self._set_mode_h_items_enabled(self._adjust_field() == "RGB")

    # ------------------------------------------------------------------ #
    # Public accessors                                                   #
    # ------------------------------------------------------------------ #

    def request_auto_run(self) -> None:
        """Public helper that schedules HSV processing with the current input."""
        self._schedule_auto_run()

    @property
    def params(self) -> dict:
        """Current B/C/S/H range config (used by the preferences dialog)."""
        return self._params

    def apply_params(self, params: dict) -> None:
        """Replace the range config and re-apply all control ranges/steps."""
        self._params = params
        self._b_mode = self._b_mode_code()
        self._s_mode = self._s_mode_code()
        self._apply_c_ui()
        self._apply_b_mode_ui(self._b_mode)
        self._apply_s_mode_ui(self._s_mode)
        self._on_h_mode_changed()
        self._schedule_auto_run()

    def _entry(self, channel: str, mode: str | None = None) -> dict:
        """当前配置中某通道/模式的 {min,max,step,default}。"""
        return param_entry(self._params, channel, mode)

    def on_preview_pixel_selection(self, selection: dict | None) -> None:
        """Host callback from the preview's frozen-pixel selection signal."""
        if not selection or not selection.get("frozen", False):
            self._frozen_pixel = None
            return
        self._frozen_pixel = (int(selection.get("x", 0)), int(selection.get("y", 0)))
        self._refresh_frozen_readout()

    # ------------------------------------------------------------------ #
    # Signal wiring                                                      #
    # ------------------------------------------------------------------ #

    def _connect_signals(self) -> None:
        """Wire HSV widget signals to internal handlers."""
        ui = self.ui
        ui.checkBox_enableHsvAdj.toggled.connect(self._schedule_auto_run)
        ui.comboBox_adjustField.currentIndexChanged.connect(self._on_adjust_field_changed)
        ui.comboBox_y2rClipType.currentIndexChanged.connect(self._schedule_auto_run)
        ui.comboBox_y2yClipType.currentIndexChanged.connect(self._on_y2y_clip_changed)
        ui.comboBox_modeB.currentIndexChanged.connect(self._on_b_mode_changed)
        ui.comboBox_modeS.currentIndexChanged.connect(self._on_s_mode_changed)
        ui.comboBox_goalH.currentIndexChanged.connect(self._on_h_mode_changed)
        ui.comboBox_modeH.currentIndexChanged.connect(self._on_h_apply_changed)
        ui.comboBox_modeC.currentIndexChanged.connect(self._on_c_mode_changed)
        ui.pushButton_resetC.clicked.connect(self._on_reset_c)
        ui.pushButton_resetV.clicked.connect(self._on_reset_v)
        ui.pushButton_resetS.clicked.connect(self._on_reset_s)
        ui.pushButton_resetH.clicked.connect(self._on_reset_h)
        ui.groupBox_setHueRange.toggled.connect(self._schedule_auto_run)
        ui.spinBox_hueStart.valueChanged.connect(self._on_hue_range_changed)
        ui.spinBox_hueEnd.valueChanged.connect(self._on_hue_range_changed)
        for spin in (ui.spinBox_hueStartTail, ui.spinBox_hueEndTail,
                     ui.spinBox_hueStartPad, ui.spinBox_hueEndPad):
            spin.valueChanged.connect(self._schedule_auto_run)
        ui.spinBox_toleranceS.valueChanged.connect(self._schedule_auto_run)
        # Mapped slider-spin pairs (scale maps slider int to spin value).
        self._connect_mapped_slider_spin(ui.slider_gainC, ui.spinBox_gainC, 100.0)
        self._connect_mapped_slider_spin(ui.slider_deltaB, ui.spinBox_deltaB, 100.0)
        self._connect_mapped_slider_spin(ui.slider_deltaS, ui.spinBox_deltaS, 100.0)
        self._connect_mapped_slider_spin(ui.slider_deltaH, ui.spinBox_deltaH, 1.0)
        self._connect_mapped_slider_spin(ui.slider_sameHueGoal, ui.spinBox_sameHueGoal, 1.0)
        # Schedule auto-run on every adjust value change.
        for slider, spin in ((ui.slider_gainC, ui.spinBox_gainC),
                             (ui.slider_deltaB, ui.spinBox_deltaB),
                             (ui.slider_deltaS, ui.spinBox_deltaS),
                             (ui.slider_deltaH, ui.spinBox_deltaH),
                             (ui.slider_sameHueGoal, ui.spinBox_sameHueGoal)):
            slider.valueChanged.connect(self._schedule_auto_run)
            spin.valueChanged.connect(self._schedule_auto_run)

    # ------------------------------------------------------------------ #
    # Slider-spin helpers                                                #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _set_spin_value(spin: object, value: float) -> None:
        """Set a spin box value without emitting change notifications."""
        spin.blockSignals(True)
        spin.setValue(value)
        spin.blockSignals(False)

    @staticmethod
    def _set_slider_value(slider: object, value: int) -> None:
        """Set a slider value without emitting change notifications."""
        slider.blockSignals(True)
        slider.setValue(value)
        slider.blockSignals(False)

    @staticmethod
    def _set_combo_text(combo: object, text: str) -> None:
        """Set the combo box current item by text without emitting signals."""
        combo.blockSignals(True)
        idx = combo.findText(text)
        if idx >= 0:
            combo.setCurrentIndex(idx)
        combo.blockSignals(False)

    def _set_mode_s_items_enabled(self, rgb_only: bool) -> None:
        """按处理域启用/禁用 comboBox_modeS 的选项：RGB 域只留 MixGray（灰阶混合），
        圆柱色域只留 ModeAdd/ModeMul。"""
        combo = self.ui.comboBox_modeS
        for i in range(combo.count()):
            combo.model().item(i).setEnabled(
                (combo.itemText(i) in self._MODE_S_RGB) == rgb_only)

    def _set_mode_h_items_enabled(self, rgb_only: bool) -> None:
        """按处理域启用/禁用 comboBox_modeH 的选项：RotateOnGray 仅 RGB 域可选；
        ModeAdd 始终可用。"""
        combo = self.ui.comboBox_modeH
        for i in range(combo.count()):
            combo.model().item(i).setEnabled(
                combo.itemText(i) not in self._MODE_H_ROTATE or rgb_only)

    def _set_mode_c_items_enabled(self, rgb_only: bool) -> None:
        """按处理域启用/禁用 comboBox_modeC 的 FastStone：仅 RGB 域可选；其余模式始终可用。"""
        combo = self.ui.comboBox_modeC
        for i in range(combo.count()):
            combo.model().item(i).setEnabled(
                combo.itemText(i) not in self._MODE_C_RGB or rgb_only)

    def _h_mode_code(self) -> str:
        """Map comboBox_modeH text to H apply-mode code ('add'/'rotategray')."""
        text = self.ui.comboBox_modeH.currentText()
        return {'ModeAdd': 'add',
                'RotateOnGray': 'rotategray'}.get(text, 'add')

    def _s_entry_mode(self, code: str) -> str:
        """S 模式配置条目键：MixGray 系（mixgray / mixgray_bt709 / mixgray_bt601）
        用独立 'mixgray' 量程/中性值；add/mul 用各自条目。"""
        if code in ('add', 'mul'):
            return code
        if code in ('mixgray', 'mixgray_bt709', 'mixgray_bt601'):
            return 'mixgray'
        return 'mul'

    def _reset_mapped(self, slider: object, spin: object, value: float, scale: float) -> None:
        """Reset a mapped slider-spin pair to ``value`` and re-run."""
        self._set_spin_value(spin, value)
        self._set_slider_value(slider, int(round(value * scale)))
        self._schedule_auto_run()

    def _connect_mapped_slider_spin(self, slider: object, spin: object, scale: float) -> None:
        """Synchronize a slider and spin box bidirectionally (spin = slider / scale)."""
        slider.valueChanged.connect(lambda v: self._set_spin_value(spin, v / scale))
        spin.valueChanged.connect(lambda v: self._set_slider_value(slider, int(round(v * scale))))

    # ------------------------------------------------------------------ #
    # UI signal handlers                                                 #
    # ------------------------------------------------------------------ #

    def _c_entry_mode(self) -> str:
        """C 通道配置条目键：TanSlant 用 'tanslant'、FastStone 用 'faststone'，其余增益模式用 'gain'。"""
        code = self._mode_c_code()
        return code if code in ('tanslant', 'faststone') else 'gain'

    def _apply_c_ui(self, keep_value: bool = False) -> None:
        """按配置设置 Contrast 量程/步长；默认置为配置默认值，keep_value 时保留当前值（clip 到新量程）。"""
        entry = self._entry('Contrast', self._c_entry_mode())
        scale = SLIDER_SCALE['Contrast']
        self.ui.spinBox_gainC.setRange(entry["min"], entry["max"])
        self.ui.spinBox_gainC.setSingleStep(entry["step"])
        self.ui.slider_gainC.setRange(int(round(entry["min"] * scale)),
                                      int(round(entry["max"] * scale)))
        if keep_value:
            value = min(max(self.ui.spinBox_gainC.value(), entry["min"]), entry["max"])
        else:
            value = entry["default"]
        self._set_spin_value(self.ui.spinBox_gainC, value)
        self._set_slider_value(self.ui.slider_gainC, int(round(value * scale)))

    def _s_mode_code(self) -> str:
        """Map comboBox_modeS text to S mode code
        ('add'/'mul'/'mixgray_bt709'/'mixgray_bt601')."""
        text = self.ui.comboBox_modeS.currentText()
        return {'ModeAdd': 'add',
                'ModeMul': 'mul',
                'MixGray_BT709': 'mixgray_bt709',
                'MixGray_BT601': 'mixgray_bt601'}.get(text, 'mul')

    def _apply_s_mode_ui(self, mode: str, keep_value: bool = False) -> None:
        """按配置设置 S 通道量程/步长；默认置为配置默认值，keep_value 时保留当前值（clip 到新量程）。
        MixGray 用独立 'mixgray' 量程/中性值配置。"""
        entry = self._entry('Saturation', self._s_entry_mode(mode))
        scale = SLIDER_SCALE['Saturation']
        self.ui.spinBox_deltaS.setRange(entry["min"], entry["max"])
        self.ui.spinBox_deltaS.setSingleStep(entry["step"])
        self.ui.slider_deltaS.setRange(int(round(entry["min"] * scale)),
                                       int(round(entry["max"] * scale)))
        if keep_value:
            value = min(max(self.ui.spinBox_deltaS.value(), entry["min"]), entry["max"])
        else:
            value = entry["default"]
        self._set_spin_value(self.ui.spinBox_deltaS, value)
        self._set_slider_value(self.ui.slider_deltaS, int(round(value * scale)))

    def _b_mode_code(self) -> str:
        """Map comboBox_modeB text to adjust_hsv mode_b code
        ('add'/'mul'/'negmulposrat')."""
        text = self.ui.comboBox_modeB.currentText()
        return {'ModeAdd': 'add',
                'ModeMul': 'mul',
                'NegMulPosRat': 'negmulposrat'}.get(text, 'add')

    def _b_entry_mode(self, code: str) -> str:
        """B 模式配置条目键：add/mul/negmulposrat 各自条目。"""
        return code

    def _apply_b_mode_ui(self, mode: str, keep_value: bool = False) -> None:
        """按配置设置 B 通道量程/步长；默认置为配置默认值，keep_value 时保留当前值（clip 到新量程）。"""
        entry = self._entry('Brightness', self._b_entry_mode(mode))
        scale = SLIDER_SCALE['Brightness']
        self.ui.spinBox_deltaB.setRange(entry["min"], entry["max"])
        self.ui.spinBox_deltaB.setSingleStep(entry["step"])
        self.ui.slider_deltaB.setRange(int(round(entry["min"] * scale)),
                                       int(round(entry["max"] * scale)))
        if keep_value:
            value = min(max(self.ui.spinBox_deltaB.value(), entry["min"]), entry["max"])
        else:
            value = entry["default"]
        self._set_spin_value(self.ui.spinBox_deltaB, value)
        self._set_slider_value(self.ui.slider_deltaB, int(round(value * scale)))

    def _on_c_mode_changed(self, *_args) -> None:
        """Contrast 模式切换：量程随模式变化；保留当前值（clip 到新量程），不重置默认。"""
        del _args
        self._apply_c_ui(keep_value=True)
        self._schedule_auto_run()

    def _on_adjust_field_changed(self, *_args) -> None:
        """adjustField 切换：RGB 域只允许 MixGray_BT709/BT601（灰阶混合），
        圆柱色域只允许 ModeAdd/ModeMul；modeC 的 FastStone 仅 RGB 域。"""
        del _args
        is_rgb = self._adjust_field() == "RGB"
        self._set_mode_s_items_enabled(is_rgb)
        self._set_mode_h_items_enabled(is_rgb)
        self._set_mode_c_items_enabled(is_rgb)
        code = self._s_mode_code()
        if is_rgb:
            if code not in ('mixgray_bt709', 'mixgray_bt601'):
                self._set_combo_text(self.ui.comboBox_modeS, 'MixGray_BT709')
            self._apply_s_mode_ui('mixgray')      # scale 语义（mixgray 量程/中性）
        else:
            if code in ('mixgray_bt709', 'mixgray_bt601'):
                self._set_combo_text(self.ui.comboBox_modeS, 'ModeMul')
            self._apply_s_mode_ui(self._s_mode_code())
        # modeH：Rotate 系列仅 RGB 域；跨域无效项回落 ModeAdd。
        h_code = self._h_mode_code()
        field = self._adjust_field()
        if not (h_code == 'add' or (field == "RGB" and h_code == 'rotategray')):
            self._set_combo_text(self.ui.comboBox_modeH, 'ModeAdd')
        # modeC：非 RGB 域禁用 FastStone（回落 GainAtMid）；RGB 域全部可选。
        if not is_rgb and self._mode_c_code() == 'faststone':
            self._set_combo_text(self.ui.comboBox_modeC, 'GainAtMid')
        # 钳位下拉使能随处理域与输入格式更新。
        self._update_clip_enables()
        self._schedule_auto_run()

    def _on_y2y_clip_changed(self, *_args) -> None:
        """y2yClipType 切换：仅重跑。"""
        del _args
        self._schedule_auto_run()

    def _on_b_mode_changed(self, *_args) -> None:
        """B 通道模式切换：量程随模式变化；保留当前值（clip 到新量程），不重置默认。

        The deltaB spin/slider range changes with the mode (add: [-1, 1],
        mul: [0, 4], negmulposrat: [-1, 1]); the current value is kept and
        clipped to the new range instead of resetting to the mode default.
        Initial state and redundant signals are no-ops.
        """
        del _args
        code = self._b_mode_code()
        if code == self._b_mode:
            return
        self._apply_b_mode_ui(code, keep_value=True)
        self._b_mode = code
        self._schedule_auto_run()

    def _on_s_mode_changed(self, *_args) -> None:
        """S 通道模式切换（add/mul）：量程随模式变化；保留当前值（clip 到新量程）。

        Only the S channel is affected: the deltaS spin/slider range changes
        with the mode (add: [-1, 1], mul: [0, 4]); the
        current value is kept and clipped to the new range.  The V/H/Contrast
        controls keep their values.  Initial state and redundant signals are
        no-ops.
        """
        del _args
        code = self._s_mode_code()
        if code == self._s_mode:
            return
        self._apply_s_mode_ui(code, keep_value=True)
        self._s_mode = code
        self._schedule_auto_run()

    def _on_h_mode_changed(self, *_args) -> None:
        """H 目标（comboBox_goalH）：SameOffset 恒为加性偏移（默认）；SameTarget 激活
        Same Hue Goal 行，且 Delta H 范围改为 [0,100]（表示向目标色相旋转的进度）。"""
        del _args
        same_target = self.ui.comboBox_goalH.currentIndex() == 1
        self._apply_same_hue_goal_enable(same_target)
        entry = self._entry('Hue', 'same_target' if same_target else 'same_offset')
        scale = SLIDER_SCALE['Hue']
        self.ui.spinBox_deltaH.setRange(int(round(entry["min"])), int(round(entry["max"])))
        self.ui.spinBox_deltaH.setSingleStep(int(round(entry["step"])))
        self.ui.slider_deltaH.setRange(int(round(entry["min"] * scale)),
                                       int(round(entry["max"] * scale)))
        # 切换模式时不重置默认，保留当前值（clip 到新量程）。
        value = int(min(max(self.ui.spinBox_deltaH.value(), entry["min"]), entry["max"]))
        self._set_spin_value(self.ui.spinBox_deltaH, value)
        self._set_slider_value(self.ui.slider_deltaH, int(round(value * scale)))
        self._schedule_auto_run()

    def _on_h_apply_changed(self, *_args) -> None:
        """H 生效方式（comboBox_modeH）切换：仅重跑；Rotate 系列仅在 RGB 域可选。"""
        del _args
        self._schedule_auto_run()

    def _on_reset_c(self) -> None:
        """Reset the Contrast gain to its configured neutral value."""
        self._reset_mapped(self.ui.slider_gainC, self.ui.spinBox_gainC,
                           self._entry('Contrast', self._c_entry_mode())["default"], SLIDER_SCALE['Contrast'])

    def _on_reset_v(self) -> None:
        """Reset the V value to its mode neutral from the config."""
        neutral = self._entry('Brightness', self._b_entry_mode(self._b_mode_code()))["default"]
        self._reset_mapped(self.ui.slider_deltaB, self.ui.spinBox_deltaB,
                           neutral, SLIDER_SCALE['Brightness'])

    def _on_reset_s(self) -> None:
        """Reset the S value to its mode neutral from the config."""
        neutral = self._entry('Saturation', self._s_entry_mode(self._s_mode_code()))["default"]
        self._reset_mapped(self.ui.slider_deltaS, self.ui.spinBox_deltaS,
                           neutral, SLIDER_SCALE['Saturation'])

    def _on_reset_h(self) -> None:
        """Reset the Delta H to its mode neutral from the config."""
        same_target = self.ui.comboBox_goalH.currentIndex() == 1
        entry = self._entry('Hue', 'same_target' if same_target else 'same_offset')
        neutral = int(round(entry["default"]))
        self._reset_mapped(self.ui.slider_deltaH, self.ui.spinBox_deltaH, neutral, 1.0)

    def _on_hue_range_changed(self, _value: int | None = None) -> None:
        """Clamp tail/pad spin maxima to hr/2 and re-run."""
        del _value
        self._update_hue_limits()
        self._schedule_auto_run()

    def _update_hue_limits(self) -> None:
        """Set tail/pad spin maxima to hr/2 (hr = he - hs, wrap-aware)."""
        hs = self.ui.spinBox_hueStart.value()
        he = self.ui.spinBox_hueEnd.value()
        hr = (he - hs + 360) % 360
        if hr == 0:
            hr = 360
        max_side = int(hr // 2)
        for spin in (self.ui.spinBox_hueStartTail, self.ui.spinBox_hueEndTail):
            spin.setMaximum(max_side)

    def _apply_same_hue_goal_enable(self, active: bool) -> None:
        """按 H 目标（comboBox_goalH）使能/禁用目标色相滑块与数字框。

        ``active`` 表示 comboBox_goalH 是否选中 SameTarget；Same Hue Goal 已改为
        静态 label，仅 SameTarget 下目标色相控件可用。
        """
        self.ui.slider_sameHueGoal.setEnabled(active)
        self.ui.spinBox_sameHueGoal.setEnabled(active)

    # ------------------------------------------------------------------ #
    # HSV processing                                                     #
    # ------------------------------------------------------------------ #

    def _schedule_auto_run(self) -> None:
        """Debounce HSV processing after UI edits."""
        if self._input_provider() is None:
            return
        if not self.ui.checkBox_enableHsvAdj.isChecked():
            return
        self.auto_run_timer.start(300)

    def _do_auto_run(self) -> None:
        """Run HSV processing at the preview work resolution and refresh."""
        input_frame = self._input_provider()
        if input_frame is None:
            return
        if not self.ui.checkBox_enableHsvAdj.isChecked():
            self._status_callback("BCSH adjust disabled")
            return
        start_time = time.time()
        try:
            src_w, src_h = input_frame.width, input_frame.height
            work_w, work_h = self._resolve_work_size(src_w, src_h)
            self._work_size = (work_w, work_h)
            out_frame, preview_frame = self._process_frame(input_frame, (work_w, work_h))
            self._latest_output_frame = out_frame
            self._latest_preview_frame = preview_frame
            # 预览显示步骤 5️⃣ 的处理域结果（full-range RGB / yuv444p full）。
            self._output_callback(preview_frame)
            elapsed_ms = (time.time() - start_time) * 1000.0
            self._refresh_frozen_readout()
            self._status_callback(f"Processing completed in {elapsed_ms:.2f} ms")
            if self._time_cost_callback is not None:
                self._time_cost_callback(elapsed_ms)
        except Exception as exc:
            print("HSV processing failed:", exc)
            self._status_callback(f"Processing failed: {exc}")

    def get_full_res_output(self) -> ImageFrame | None:
        """Return a full-resolution output frame（步骤 6️⃣）for saving.

        若最近一次预览处理已在源分辨率进行（源 <= 预览目标），直接复用
        缓存帧；否则按源分辨率重算一次。返回前按所选输出 format 转换
        （子采样/打包），保证保存的文件与所选格式一致。
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

    def _process_frame(
        self, frame: ImageFrame, work_wh: tuple[int, int] | None = None,
    ) -> tuple[ImageFrame, ImageFrame]:
        """Process one frame (optionally downsampled).

        处理分辨率取 min(源分辨率, work_wh)；降采样处理完成后升采样回源
        分辨率，保证预览显示与输入对齐（预览显示逻辑无需感知降采样）。
        返回 (输出帧 6️⃣, 预览帧 5️⃣)；按 adjustField 分派到 RGB 系或 YCbCr 系处理。
        """
        src_w, src_h = frame.width, frame.height
        work_frame = frame
        if work_wh is not None and (work_wh[0] < src_w or work_wh[1] < src_h):
            work_frame = self._downsample_frame(frame, work_wh[0], work_wh[1])

        if self._is_yuv_colorspace():
            out_frame, preview_frame, readout = self._process_frame_yuv(work_frame)
        else:
            out_frame, preview_frame, readout = self._process_frame_rgb(work_frame)

        # 降采样处理时升采样回源分辨率，保证预览/像素读数与输入对齐。
        if work_frame is not frame:
            out_frame = self._upsample_frame(out_frame, src_h, src_w)
            preview_frame = self._upsample_frame(preview_frame, src_h, src_w)
            readout = self._upsample_readout(readout, src_h, src_w)

        self._last_readout = readout
        self._input_is_rgb = frame.is_rgb
        self._update_clip_enables()      # 输入格式变化可能影响 y2rClipType 使能
        return out_frame, preview_frame

    @staticmethod
    def _upsample_readout(readout: "PixelReadoutCache", out_h: int, out_w: int) -> "PixelReadoutCache":
        """最近邻把读数缓存的各 (H,W) 数组升采样到 (out_h, out_w)。"""
        def _up_native(native):
            kind, planes, depth = native
            planar = np.stack(planes, axis=0)
            up = HsvUiController._upsample_planar(planar, out_h, out_w)
            return (kind, (up[0], up[1], up[2]), depth)

        def _up_arr(arr):
            if arr is None:
                return None
            return HsvUiController._upsample_planar(
                arr.transpose(2, 0, 1), out_h, out_w).transpose(1, 2, 0)

        def _up_dom(dom):
            name, h, s, x = dom
            up2d = lambda a: HsvUiController._upsample_planar(a[None, ...], out_h, out_w)[0]
            return (name, up2d(h), up2d(s), up2d(x))

        return PixelReadoutCache(
            in_native=_up_native(readout.in_native),
            in_full_rgb=_up_arr(readout.in_full_rgb),
            in_full_yuv=_up_arr(readout.in_full_yuv),
            in_yuv_cs=readout.in_yuv_cs,
            in_domain=_up_dom(readout.in_domain),
            out_native=_up_native(readout.out_native),
            out_full_rgb=_up_arr(readout.out_full_rgb),
            out_full_yuv=_up_arr(readout.out_full_yuv),
            out_yuv_cs=readout.out_yuv_cs,
            out_domain=_up_dom(readout.out_domain),
        )

    def _is_yuv_colorspace(self) -> bool:
        """True when the BCSH processing domain is YCbCr."""
        return self.ui.comboBox_adjustField.currentText() == "YCbCr"

    def _hue_blend_weights_for(self, hue_deg: np.ndarray) -> np.ndarray:
        """Return per-pixel blend weight from the specified-hue group box."""
        if self.ui.groupBox_setHueRange.isChecked():
            return self._hue_blend_weights(
                hue_deg,
                self.ui.spinBox_hueStart.value(),
                self.ui.spinBox_hueEnd.value(),
                self.ui.spinBox_hueStartTail.value(),
                self.ui.spinBox_hueEndTail.value(),
                self.ui.spinBox_hueStartPad.value(),
                self.ui.spinBox_hueEndPad.value(),
            )
        return np.ones_like(hue_deg, dtype=np.float32)

    def _process_frame_rgb(
        self, work_frame: ImageFrame,
    ) -> tuple[ImageFrame, ImageFrame, PixelReadoutCache]:
        """RGB 系（HSV/HSI/HSL/HCY/HSP/Lch/RGB）处理：步骤 1️⃣~6️⃣。

        处理域 = full-range RGB。输入 rgb/yuv 两分支（用例 1/3）。
        RGB 域直接处理（无域转换）；其余先转域再 BCSH 调整。
        Returns (输出帧 6️⃣, 预览帧 5️⃣, 读数缓存).
        """
        depth = work_frame.depth
        input_is_rgb = work_frame.is_rgb
        field = self._adjust_field()
        to_domain, from_domain = _DOMAIN_CONVERTERS[field]

        # ---- 1️⃣ 原始输入 ----
        in_native = self._native_planes(work_frame)

        # ---- 2️⃣ 输入 CSC -> full-range RGB（y2rClipType 决定 YUV->RGB 的钳位方式） ----
        if input_is_rgb:
            # RGB 输入 limited->full 展开：直接硬钳，不依赖 y2rClipType。
            rgb_2 = np.clip(self._rgb_full_from_frame(work_frame), 0.0, 1.0)
        else:
            rgb_2 = self._clip_rgb(
                self._yuv_to_rgb_full_float(work_frame), self._y2r_clip_type())

        # ---- 3️⃣ 域转换（有钳位） ----
        domain = np.stack(to_domain(rgb_2), axis=-1)           # (H,W,3)
        if field == "RGB":
            # RGB 域：无域转换，直接用 HSV 色相做指定色相/SameTarget 决策
            h_deg = rgb_to_hsv(rgb_2)[0]
        else:
            h_deg = domain[..., 0]

        # ---- 4️⃣ BCSH 调整 ----
        if field == "RGB":
            adj = self._compute_adjusted_rgb(rgb_2, h_deg)
        else:
            adj = self._compute_adjusted_hsv(domain, h_deg)

        # ---- 5️⃣ 回 full-range RGB（域往返本身有钳位 -> 恒 [0,1]） ----
        rgb_5 = from_domain(adj)
        w = self._hue_blend_weights_for(h_deg)
        rgb_5 = rgb_2 * (1.0 - w[..., None]) + rgb_5 * w[..., None]
        rgb_5 = np.clip(rgb_5, 0.0, 1.0)

        # ---- 预览帧（步骤 5️⃣，full-range RGB，存储必钳位） ----
        preview_frame = self._rgb_full_to_frame(rgb_5, depth)

        # ---- 6️⃣ 输出 CSC（必钳位，444 平面帧；格式转换在保存时按全分辨率进行） ----
        out_frame = self._to_output_frame_rgb(rgb_5, depth)
        out_native = self._native_planes(out_frame)

        readout = PixelReadoutCache(
            in_native=in_native,
            in_full_rgb=rgb_2, in_full_yuv=None, in_yuv_cs=5,
            in_domain=(field, domain[..., 0], domain[..., 1], domain[..., 2]),
            out_native=out_native,
            out_full_rgb=rgb_5, out_full_yuv=None, out_yuv_cs=5,
            out_domain=(field, adj[..., 0], adj[..., 1], adj[..., 2]),
        )
        return out_frame, preview_frame, readout

    def _process_frame_yuv(
        self, work_frame: ImageFrame,
    ) -> tuple[ImageFrame, ImageFrame, PixelReadoutCache]:
        """YCbCr 处理：步骤 1️⃣~6️⃣。

        处理域 = yuv444p full-range（归一化 (Y, cb, cr)，cb/cr 去中心）。
        输入 rgb 用 BT.709 系数（用例 2）；输入 yuv 保持输入矩阵（用例 4）。
        Returns (输出帧 6️⃣, 预览帧 5️⃣, 读数缓存).
        """
        depth = work_frame.depth
        input_is_rgb = work_frame.is_rgb
        y2y_policy = self._y2y_clip_type()

        in_native = self._native_planes(work_frame)

        # ---- 2️⃣ 输入 CSC -> yuv full-range（输入 YUV 不做钳位） ----
        if input_is_rgb:
            proc_cs = 5                                          # BT.709
            rgb = self._rgb_full_from_frame(work_frame)
            r2y, _ = _get_csc_matrices(proc_cs)
            yuv = rgb @ r2y.T                                    # (Y, cb, cr)
        else:
            proc_cs = work_frame.clrspc if work_frame.clrspc in (2, 3, 4, 5, 6, 7) else 5
            yuv = self._yuv_full_from_frame(work_frame)          # 保持输入矩阵
        y_n, cb, cr = yuv[..., 0], yuv[..., 1], yuv[..., 2]
        # 读数用的步骤 2️⃣ 值：输入 YUV 保持原样（RGB 数据钳位由 y2rClipType
        # 在 RGB 系处理路径负责；此处处理域即 YUV，不做输入钳位）。
        yuv_in = np.stack([y_n, cb, cr], axis=-1)

        # ---- 3️⃣ YCbCr H/S（极坐标，按 y2yClipType 的 S 语义归一化） ----
        radius = np.sqrt(cb * cb + cr * cr)
        if y2y_policy == 'scalechromapix':
            # ScaleChromaPix：S = r/r_max(Y,θ) 按该像素色域边界半径归一化，S∈[0,1]
            # 保证落在 RGB 色域内（Y/S/H 解耦，任意调整不越界、色相不变）。
            s_norm = self._gamut_s_norm(y_n, cb, cr, proc_cs)
        elif y2y_policy == 'scalechromasec':
            # ScaleChromaSec：S = r/_CHROMA_MAX（全局最大边界半径归一化，绝对比例）；
            # 不保证落在色域内（该 (Y,θ) 边界可能远小于全局最大，越界像素按 HardClip）。
            s_norm = np.clip(radius / _CHROMA_MAX[_cs_family(proc_cs)], 0.0, 1.0)
        else:
            # 其余策略：S 按绝对极径长度计算，不归一化。
            s_norm = radius
        angle = (np.degrees(np.arctan2(cr, cb)) + 360.0) % 360.0
        hue_sync = hue_ycbcr_to_hsv(angle, proc_cs)

        # ---- 4️⃣ BCSH 调整：H 直接作用于 YCbCr 极角（dh 即极角旋转），
        #      h' 同步色相仅作读数显示，不再经 HSV 色相中转。 ----
        yhs = np.stack([angle, s_norm, y_n], axis=-1)
        adj = self._compute_adjusted_hsv(yhs, angle, proc_cs=proc_cs)
        angle_a, s_a, y_a = adj[..., 0], adj[..., 1], adj[..., 2]
        hue_sync_a = hue_ycbcr_to_hsv(angle_a, proc_cs)

        # ---- 5️⃣ 回 yuv full-range（y2yClipType 决定重建与色域处理方式） ----
        w = self._hue_blend_weights_for(hue_sync)
        if y2y_policy == 'scalechromapix':
            # ScaleChromaPix 重建：r' = S'·r_max(Y',θ')，天然在调整后的色域内。
            r_max_a = self._gamut_r_max(
                y_a, np.cos(np.radians(angle_a)), np.sin(np.radians(angle_a)), proc_cs)
            radius_a = s_a * r_max_a
        elif y2y_policy == 'scalechromasec':
            # ScaleChromaSec 重建：r' = S'·_CHROMA_MAX（全局最大边界半径）。
            radius_a = s_a * _CHROMA_MAX[_cs_family(proc_cs)]
        else:
            radius_a = s_a                     # 绝对极径，不归一化
        cb_a = radius_a * np.cos(np.radians(angle_a))
        cr_a = radius_a * np.sin(np.radians(angle_a))
        cb_5 = cb * (1.0 - w) + cb_a * w
        cr_5 = cr * (1.0 - w) + cr_a * w
        y_5 = y_n * (1.0 - w) + y_a * w
        yuv_5_raw = np.stack([y_5, cb_5, cr_5], axis=-1)
        yuv_5_disp = self._apply_y2y_strategy(yuv_5_raw, proc_cs)

        # ---- 预览帧（步骤 5️⃣，输出 YUV 帧 -> RGB 显示，按 y2rClipType 钳位） ----
        preview_frame = self._yuv_to_preview_frame(yuv_5_disp, proc_cs, depth)

        # ---- 6️⃣ 输出 CSC（必钳位，444 平面帧；格式转换在保存时按全分辨率进行） ----
        out_frame = self._to_output_frame_yuv(yuv_5_disp, proc_cs, depth)
        out_native = self._native_planes(out_frame)

        # 读数域值：按实际输出极径更新 S（H/Y 不变）。
        radius_out = np.sqrt(yuv_5_disp[..., 1] ** 2 + yuv_5_disp[..., 2] ** 2)
        if y2y_policy == 'scalechromapix':
            s_out = self._gamut_s_norm(
                yuv_5_disp[..., 0], yuv_5_disp[..., 1], yuv_5_disp[..., 2], proc_cs)
        elif y2y_policy == 'scalechromasec':
            s_out = np.clip(radius_out / _CHROMA_MAX[_cs_family(proc_cs)], 0.0, 1.0)
        else:
            s_out = radius_out

        readout = PixelReadoutCache(
            in_native=in_native,
            in_full_rgb=None, in_full_yuv=yuv_in, in_yuv_cs=proc_cs,
            # H/H'SY：h 槽为 (...,2) [YCbCr 极角, HSV 同步色相]，显示为 h/h'。
            in_domain=("H/H'SY", np.stack([angle, hue_sync], axis=-1), s_norm, y_n),
            out_native=out_native,
            out_full_rgb=None, out_full_yuv=yuv_5_disp, out_yuv_cs=proc_cs,
            out_domain=("H/H'SY", np.stack([angle_a, hue_sync_a], axis=-1), s_out, y_a),
        )
        return out_frame, preview_frame, readout

    def _comp_luma(self, y, cb, cr, policy, cs) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """y2yClipType=CompLumaOnly/CompLumaFirst（YCbCr 域）：色域补偿（保极角）。

        输入为步骤 5️⃣ 混合后的 (y, cb, cr)，返回补偿后的 (y', cb', cr')。
        CompLumaOnly（保 S 调 Y）：色度不变，按 Y2R 通道钳位量补 ΔY=缺量-超量
        （只补回实际被钳掉的部分，不直接顶到可行区间边界）。
        CompLumaFirst（Y 优先、S 兜底）：先只调 Y——把 Y 钳到该 (极角, 极径)
        下的可行区间 [Y_lo, Y_hi]（Y_lo=max_i(-k_i)，Y_hi=min_i(1-k_i)，可行时与
        CompLumaOnly 一致）；若极径超过该 (极角,Y) 可承载上限（Y_lo>Y_hi，Y 单独
        调不够），再把色度极径缩到恰好可解的最大值 r*=1/(A+B)（A=max_i(-k_i)，
        B=max_i(k_i)，均含极径），Y 顶到唯一可行值 Y*=A/(A+B)，结果落在色域边界
        （max=1、min=0，全饱和），色相严格保持、无残留越界。
        """
        _, y2r = _get_csc_matrices(cs)
        k = (y2r[:, 1, None, None] * cb[None, ...]
             + y2r[:, 2, None, None] * cr[None, ...])                 # (3,H,W) Y 系数
        if policy == 'complumaonly':
            rgb_probe = y[None, ...] + k                              # 未钳位 RGB (3,H,W)
            clip_neg = np.maximum(0.0, -np.minimum.reduce(rgb_probe, axis=0))
            clip_pos = np.maximum(0.0, np.maximum.reduce(rgb_probe, axis=0) - 1.0)
            dy = clip_neg - clip_pos
            return np.clip(y + dy, 0.0, 1.0), cb, cr
        # complumafirst：Y 优先、S 兜底：先只调 Y（可行区间 [Y_lo, Y_hi]）；不可行时
        # 缩色度到 r*=r/(A+B)（scale=1/(A+B)，A/B 含极径）并把 Y 顶到
        # Y*=A/(A+B)，落在色域边界（max=1、min=0），色相严格保持。
        y_lo = np.maximum.reduce(-k, axis=0)
        y_hi = np.minimum.reduce(1.0 - k, axis=0)
        feasible = y_lo <= y_hi
        y_out = np.clip(np.clip(y, y_lo, y_hi), 0.0, 1.0)
        a = np.maximum.reduce(-k, axis=0)          # = r·A_unit
        b = np.maximum.reduce(k, axis=0)           # = r·B_unit
        denom = a + b                              # = r·(A_unit+B_unit)
        scale = np.divide(1.0, denom, out=np.ones_like(denom), where=denom > 0.0)
        y_star = np.divide(a, denom, out=np.zeros_like(a), where=denom > 0.0)
        cb_out = np.where(feasible, cb, cb * scale)
        cr_out = np.where(feasible, cr, cr * scale)
        y_out = np.where(feasible, y_out, y_star)
        return y_out, cb_out, cr_out

    def _apply_y2y_strategy(self, yuv_norm, proc_cs) -> np.ndarray:
        """步骤 5️⃣：按 y2yClipType 统一色域处理策略处理 YCbCr 数据。

        - clipchroma：保 Y、沿色相把极径缩到 r_max(Y,θ)（降饱和保色相）。
        - complumaonly / complumafirst：调 Y（不足时缩色度）拉回域内，保极角。
        - hardclip / scalechromapix（域内免钳）/ scalechromasec（越界走硬钳）：
          统一按 YUV 范围硬钳兜底（scalechromapix 重建已域内，硬钳恒等）。
        """
        yuv = np.asarray(yuv_norm, dtype=np.float32)
        policy = self._y2y_clip_type()
        if policy == 'clipchroma':
            return self._gamut_clip_chroma(yuv, proc_cs)
        if policy in ('complumaonly', 'complumafirst'):
            y, cb, cr = yuv[..., 0], yuv[..., 1], yuv[..., 2]
            y, cb, cr = self._comp_luma(y, cb, cr, policy, proc_cs)
            return np.stack([y, cb, cr], axis=-1)
        # hardclip / scalechromapix / scalechromasec：YUV 范围硬钳。
        y_c = np.clip(yuv[..., 0], 0.0, 1.0)
        cb_c = np.clip(yuv[..., 1], -0.5, 0.5)
        cr_c = np.clip(yuv[..., 2], -0.5, 0.5)
        return np.stack([y_c, cb_c, cr_c], axis=-1)

    def _yuv_to_preview_frame(self, yuv_norm, proc_cs, depth) -> ImageFrame:
        """输出 YUV 帧 -> 预览显示帧（YCbCr 域）：YUV->RGB 按 y2rClipType 钳位
        （HardClip 硬钳 / SoftClip 软钳 / ConstHue 等比钳）。"""
        _, y2r = _get_csc_matrices(proc_cs)
        rgb = self._clip_rgb(yuv_norm @ y2r.T, self._y2r_clip_type())
        return self._rgb_full_to_frame(rgb, depth)

    # ------------------------------------------------------------------ #
    # 统一流水线辅助（步骤 2️⃣/5️⃣/6️⃣ 的 CSC 与帧封装）                    #
    # ------------------------------------------------------------------ #

    def _adjust_field(self) -> str:
        """当前处理色域名（HSV/HSI/HSL/HCY/HSP/Lch/RGB/YCbCr）。"""
        return self.ui.comboBox_adjustField.currentText()

    def _update_clip_enables(self) -> None:
        """按处理域与输入格式更新钳位控件使能：
        - comboBox_y2yClipType：仅 YCbCr 处理域启用。
        - comboBox_y2rClipType：存在 YUV->RGB（y2r）节点时启用——YCbCr 处理域
          （预览 y2r 恒存在，输出 RGB 桥亦然）或 输入为 YUV 且非 YCbCr
          （输入 y2r 节点）。
        """
        is_ycbcr = self._adjust_field() == "YCbCr"
        self.ui.comboBox_y2yClipType.setEnabled(is_ycbcr)
        frame = self._input_provider()
        input_is_yuv = frame is not None and not frame.is_rgb
        self.ui.comboBox_y2rClipType.setEnabled(is_ycbcr or input_is_yuv)

    def _y2r_clip_type(self) -> str:
        """y2rClipType 钳位方式：'hard'/'soft'/'consthue'（YUV->RGB 转换）。"""
        text = self.ui.comboBox_y2rClipType.currentText()
        return {'HardClip': 'hard',
                'SoftClip': 'soft',
                'ConstHue': 'consthue'}.get(text, 'hard')

    def _y2y_clip_type(self) -> str:
        """y2yClipType 色域处理策略：
        'hardclip'/'clipchroma'/'scalechromapix'/'scalechromasec'/
        'complumaonly'/'complumafirst'（YCbCr 处理域步骤 3️⃣/5️⃣）。"""
        text = self.ui.comboBox_y2yClipType.currentText()
        return {'HardClip': 'hardclip',
                'ClipChroma': 'clipchroma',
                'ScaleChromaPix': 'scalechromapix',
                'ScaleChromaSec': 'scalechromasec',
                'CompLumaOnly': 'complumaonly',
                'CompLumaFirst': 'complumafirst'}.get(text, 'hardclip')

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
    def _yuv_norm_to_frame(yuv_norm: np.ndarray, depth: int, cs: int) -> ImageFrame:
        """归一化 (Y, cb, cr) -> yuv444p full-range 帧（必钳位量化）。"""
        max_val = (1 << depth) - 1
        rp = _csc_range_params(depth)
        uv_center = rp["uv_center"]
        y = np.clip(np.rint(yuv_norm[..., 0] * max_val), 0, max_val)
        u = np.clip(np.rint(yuv_norm[..., 1] * max_val + uv_center), 0, max_val)
        v = np.clip(np.rint(yuv_norm[..., 2] * max_val + uv_center), 0, max_val)
        dtype = np.uint16 if depth >= 10 else np.uint8
        out_fmt = _PLANAR_YUV_10 if depth >= 10 else _PLANAR_YUV_8
        clrspc = (cs | 1) if cs in (2, 3, 4, 5, 6, 7) else 5    # limited -> full 同族
        return ImageFrame(y.astype(dtype), u.astype(dtype), v.astype(dtype), out_fmt, clrspc)

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
        """步骤 6️⃣（RGB 系）：full-range RGB -> 444 平面输出帧（必钳位）。"""
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

    @staticmethod
    def _clip_rgb(rgb_norm: np.ndarray, mode: str) -> np.ndarray:
        """按 mode 把 full-range RGB 钳到 [0,1]（步骤 2️⃣）：
        'hard' 逐通道硬钳；'soft' zentone 色相保持软钳；'consthue' 恒定色相
        等比例缩放（负值先钳 0）。"""
        arr = np.asarray(rgb_norm, dtype=np.float32)
        if mode == 'soft':
            return HsvUiController._rgb_soft_clip(arr)
        if mode == 'consthue':
            return HsvUiController._rgb_const_hue_clip(arr)
        return np.clip(arr, 0.0, 1.0)

    @staticmethod
    def _rgb_soft_clip(rgb: np.ndarray) -> np.ndarray:
        """zentone soft_clip：色相保持软钳（参考
        https://docs.rs/zentone/latest/zentone/gamut/fn.soft_clip.html）。

        负值先钳 0；max<=1 直接返回（钳负值后）；否则排序 (hi, mid, lo)：hi 钳
        到 1，mid 按 (mid-lo)/(hi-lo) 比例在 [min(lo,1), min(hi,1)] 间线性插值，
        保持通道比例（色相不变）；全部相等时映射到 min(hi,1)。
        """
        arr = np.asarray(rgb, dtype=np.float32)
        r = np.maximum(arr[..., 0], 0.0)
        g = np.maximum(arr[..., 1], 0.0)
        b = np.maximum(arr[..., 2], 0.0)
        mx = np.maximum(np.maximum(r, g), b)
        mn = np.minimum(np.minimum(r, g), b)
        mid = r + g + b - mx - mn
        hi_c = np.minimum(mx, 1.0)
        lo_c = np.minimum(mn, 1.0)
        denom = mx - mn
        safe = denom > 0.0
        t = np.divide(mid - mn, denom, out=np.zeros_like(mn), where=safe)
        mid_c = np.where(safe, lo_c + (hi_c - lo_c) * t, hi_c)
        out = np.empty_like(arr)
        out[..., 0] = np.where(r == mx, hi_c, np.where(r == mn, lo_c, mid_c))
        out[..., 1] = np.where(g == mx, hi_c, np.where(g == mn, lo_c, mid_c))
        out[..., 2] = np.where(b == mx, hi_c, np.where(b == mn, lo_c, mid_c))
        return out

    @staticmethod
    def _rgb_const_hue_clip(rgb: np.ndarray) -> np.ndarray:
        """恒定色相钳位：负值先钳 0，再按同一比例缩放使最大通道=1（通道比例
        不变 -> 色相不变；max<=1 时恒等）。"""
        arr = np.asarray(rgb, dtype=np.float32)
        rgb_c = np.maximum(arr, 0.0)
        mx = np.max(rgb_c, axis=-1)
        scale = np.minimum(
            1.0, np.divide(1.0, mx, out=np.ones_like(mx), where=mx > 0.0))
        return rgb_c * scale[..., None]

    @staticmethod
    def _gamut_clip_chroma(yuv_norm: np.ndarray, cs: int,
                           soft_knee: float = 0.0) -> np.ndarray:
        """沿恒定色相压缩色度，使 (Y, cb, cr) 落回 RGB 色域。

        保持 Y 与 YCbCr 极角不变，只把色度极径缩到该 (极角, Y) 下的色域边界半径 r_max：
          channel_i(Y, cb, cr) = Y + k_i*r,  k_i = a_i*cosθ + b_i*sinθ
          r_max = min( min_{k>0}(1-Y)/k, min_{k<0}(-Y)/k )
        soft_knee>0 时用软拐角：保留 [0, knee*r_max] 不变，其后 C¹ 连续平滑
        收敛到 r_max（避免整图在色域边界出现硬切色带）。
        """
        yuv = np.asarray(yuv_norm, dtype=np.float32)
        y = np.clip(yuv[..., 0], 0.0, 1.0)
        cb, cr = yuv[..., 1], yuv[..., 2]
        r = np.sqrt(cb * cb + cr * cr)
        _, y2r = _get_csc_matrices(cs)
        a = y2r[:, 1]                                # (3,) R,G,B 对 Cb 系数
        b = y2r[:, 2]                                # (3,) R,G,B 对 Cr 系数
        cos_t = np.divide(cb, r, out=np.zeros_like(cb), where=r > 0)
        sin_t = np.divide(cr, r, out=np.zeros_like(cr), where=r > 0)
        k = (a[:, None, None] * cos_t[None, ...]
             + b[:, None, None] * sin_t[None, ...])  # (3, ...)
        up = np.divide(1.0 - y, k, out=np.full_like(k, np.inf), where=k > 0)
        lo = np.divide(-y, k, out=np.full_like(k, np.inf), where=k < 0)
        r_max = np.minimum(np.minimum(up, lo).min(axis=0), 1.0)   # (...,)
        r_max = np.maximum(r_max, 0.0)
        scale = np.minimum(
            np.divide(r_max, r, out=np.ones_like(r), where=r > 0), 1.0)
        if soft_knee > 0.0:
            r_soft = soft_knee * r_max
            t = np.maximum(r - r_soft, 0.0) / np.maximum(r_max - r_soft, 1e-6)
            r_new = r_soft + (r_max - r_soft) * (t / (1.0 + t))
            scale = np.divide(r_new, r, out=np.ones_like(r), where=r > 0)
        return np.stack([y, cb * scale, cr * scale], axis=-1)

    @staticmethod
    def _gamut_r_max(y, cb, cr, cs) -> np.ndarray:
        """(Y, cb, cr) 所在极角下的 RGB 色域边界极径 r_max(Y,θ)。

        cb/cr 只提供方向（模长无关，传单位方向亦可）；灰阶 r=0 时返回 1.0
        （此时 S 取 0 即可，任意 r_max 都成立）。Y 超出 [0,1] 时 r_max 钳到 0。
        """
        y = np.asarray(y, dtype=np.float32)
        cb = np.asarray(cb, dtype=np.float32)
        cr = np.asarray(cr, dtype=np.float32)
        r = np.sqrt(cb * cb + cr * cr)
        _, y2r = _get_csc_matrices(cs)
        cos_t = np.divide(cb, r, out=np.zeros_like(cb), where=r > 0)
        sin_t = np.divide(cr, r, out=np.zeros_like(cr), where=r > 0)
        k = (y2r[:, 1, None, None] * cos_t[None, ...]
             + y2r[:, 2, None, None] * sin_t[None, ...])             # (3, H, W)
        up = np.divide(1.0 - y, k, out=np.full_like(k, np.inf), where=k > 0)
        lo = np.divide(-y, k, out=np.full_like(k, np.inf), where=k < 0)
        r_max = np.minimum(np.minimum(up, lo).min(axis=0), 1.0)
        return np.maximum(r_max, 0.0)

    @staticmethod
    def _gamut_s_norm(y, cb, cr, cs) -> np.ndarray:
        """NormByPix 色域归一化 S = r / r_max(Y,θ) ∈ [0,1]（灰阶为 0）。"""
        r = np.sqrt(cb * cb + cr * cr)
        r_max = HsvUiController._gamut_r_max(y, cb, cr, cs)
        return np.clip(
            np.divide(r, r_max, out=np.zeros_like(r), where=r_max > 0), 0.0, 1.0)

    def _to_output_frame_yuv(self, yuv_norm: np.ndarray, proc_cs: int, depth: int) -> ImageFrame:
        """步骤 6️⃣（YCbCr 系）：处理域 yuv（proc_cs full）-> 444 平面输出帧（必钳位）。

        YUV 输出直接编码处理域 YUV（色域策略已在步骤 5️⃣ 完成，不再经 RGB 桥）；
        仅 RGB 输出仍需 full-RGB 桥（y2r -> rgb 钳位 -> 输出编码）。系数与
        script/csc/get_csc_coefs.py 一致；跨族（601/709 <-> 2020）由 UI 限制保证不出现。
        """
        out_cs = self._output_clrspc()
        out_fmt = self._output_fmt_code()
        if not is_rgb_format(out_fmt):
            return self._yuv_norm_to_output_frame(yuv_norm, depth, out_cs)
        _, y2r = _get_csc_matrices(proc_cs)
        # YCbCr 处理域转输出 RGB 时应用 y2rClipType（YUV->RGB 转换钳位）。
        rgb = self._clip_rgb(yuv_norm @ y2r.T, self._y2r_clip_type())
        return self._encode_rgb_frame(rgb, depth, out_cs)

    @staticmethod
    def _upsample_frame(frame: ImageFrame, out_h: int, out_w: int) -> ImageFrame:
        """最近邻把 444 帧（RGB 或 YUV444p）升采样到 (out_h, out_w)。"""
        planar = np.stack([frame.pyr, frame.pug, frame.pvb], axis=0)
        up = HsvUiController._upsample_planar(planar, out_h, out_w)
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

    def _mode_c_code(self) -> str:
        """Map comboBox_modeC text to adjust_hsv mode_c
        ('mid'/'zero'/'both'/'tanslant'/'faststone')."""
        text = self.ui.comboBox_modeC.currentText()
        return {'GainAtMid': 'mid',
                'GainAtZero': 'zero',
                'GainAtBoth': 'both',
                'TanSlant': 'tanslant',
                'FastStone': 'faststone'}.get(text, 'mid')

    def _compute_adjusted_hsv(
        self, hsv: np.ndarray, h_deg: np.ndarray, proc_cs: int | None = None,
    ) -> np.ndarray:
        """Compute the fully-adjusted HSV array from the current controls.

        ``proc_cs`` 为 YCbCr 处理域矩阵代码时，h 通道为 YCbCr 极角（dh 直接旋转
        极角）；SameTarget 的目标色相按 HSV 色相输入并换算到极角。None 时为
        HSV 色相域（RGB 系处理域，默认）。
        """
        db = float(self.ui.spinBox_deltaB.value())
        gc = float(self.ui.spinBox_gainC.value())
        ds = float(self.ui.spinBox_deltaS.value())
        dh_deg = float(self.ui.spinBox_deltaH.value())
        mode = self._s_mode_code()
        mode_b = self._b_mode_code()
        # S Tolerance：控件已是归一化浮点 [0, 0.1]，直接传给 adjust_hsv。
        tolerance_s = float(self.ui.spinBox_toleranceS.value())
        same_target = self.ui.comboBox_goalH.currentIndex() == 1
        # SameTarget 下 Delta H 表示向目标旋转的进度，不作为加性偏移传入 adjust_hsv。
        adj_hsv = adjust_hsv(hsv, delta_b=db, delta_s=ds,
                             delta_h=0.0 if same_target else dh_deg / 360.0,
                             gain_c=gc, mode=mode, tolerance_s=tolerance_s,
                             mode_c=self._mode_c_code(), mode_b=mode_b)
        if same_target:
            target = float(self.ui.spinBox_sameHueGoal.value())
            if proc_cs is not None:
                # YCbCr 域：目标按 HSV 色相输入，换算到 YCbCr 极角再算弧长。
                target = float(hue_hsv_to_ycbcr(np.asarray(target), proc_cs))
            # Delta H 范围 [0,100]：表示向目标色相旋转的进度（0=不旋转，100=完全到位）。
            progress = float(np.clip(dh_deg / 100.0, 0.0, 1.0))
            arc = ((target - h_deg + 180.0) % 360.0) - 180.0   # shortest signed arc
            h_adj = (h_deg + progress * arc) % 360.0
            adj_hsv = np.stack([h_adj, adj_hsv[..., 1], adj_hsv[..., 2]], axis=-1)
        return adj_hsv

    def _compute_adjusted_rgb(
        self, rgb: np.ndarray, h_deg: np.ndarray,
    ) -> np.ndarray:
        """RGB 域 BCSH 调整：C/V 逐通道、S 灰阶混合（MixGray_BT709/BT601）、
        H 按 modeH 生效（ModeAdd 六边形加法 / RotateOnGray 灰轴）。

        SameOffset：angle=dh；SameTarget：angle=progress*shortest_arc（逐像素，
        用 HSV 色相 h_deg 计算弧长）。
        """
        db = float(self.ui.spinBox_deltaB.value())
        gc = float(self.ui.spinBox_gainC.value())
        ds = float(self.ui.spinBox_deltaS.value())
        dh_deg = float(self.ui.spinBox_deltaH.value())
        same_target = self.ui.comboBox_goalH.currentIndex() == 1
        if same_target:
            target = float(self.ui.spinBox_sameHueGoal.value())
            progress = float(np.clip(dh_deg / 100.0, 0.0, 1.0))
            arc = ((target - h_deg + 180.0) % 360.0) - 180.0   # shortest signed arc
            angle = progress * arc
        else:
            angle = dh_deg
        s_code = self._s_mode_code()
        gray_coef = 'bt601' if s_code == 'mixgray_bt601' else 'bt709'
        return adjust_rgb(rgb, delta_b=db, delta_s=ds, gain_c=gc,
                          tolerance_s=float(self.ui.spinBox_toleranceS.value()),
                          mode_c=self._mode_c_code(), mode_b=self._b_mode_code(),
                          angle_deg=angle, gray_coef=gray_coef,
                          h_mode=self._h_mode_code())

    @staticmethod
    def _hue_blend_weights(hue_deg, hs, he, st, et, sp, ep):
        """Compute per-pixel blend weight for the specified-hue adjustment.

        Returns w in [0, 1] for each hue in ``hue_deg`` (deg, [0, 360)).
        hs/he: nominal range (may wrap). st/et: start/end Tail lengths.
        sp/ep: start/end Pad lengths.
        Processed zone = [hs - sp, he + ep] (wrap-aware):
          start: Pad [hs-sp, hs] + Tail [hs, hs+st]
          end:   Tail [he-et, he] + Pad [he, he+ep]
          core:  [hs+st, he-et]  (w = 1)
        Transition weights:
          - tail and pad both set: pad 0 -> 0.5, tail 0.5 -> 1 (start);
                                 tail 1 -> 0.5, pad 0.5 -> 0 (end)
          - only one side set: linear 0 -> 1 (start) / 1 -> 0 (end)
        """
        h = np.asarray(hue_deg, dtype=np.float32)
        sp = float(sp)
        st = float(st)
        et = float(et)
        ep = float(ep)
        use_tail = (st > 0.0) or (et > 0.0)
        use_pad = (sp > 0.0) or (ep > 0.0)
        if not use_tail and not use_pad:
            # Hard range only: w = 1 inside [hs, he] (wrap-aware), else 0.
            hs_f = float(hs)
            he_f = float(he)
            if hs_f <= he_f:
                return np.where((h >= hs_f) & (h <= he_f), 1.0, 0.0).astype(np.float32)
            return np.where((h >= hs_f) | (h <= he_f), 1.0, 0.0).astype(np.float32)
        hsp = float(hs) - sp
        span = ((float(he) + ep) - hsp) % 360.0          # processed zone length (forward)
        d = (h - hsp) % 360.0
        w = np.zeros_like(d, dtype=np.float32)
        core_start = sp + st
        core_end = span - (ep + et)
        combined = use_tail and use_pad
        # Start ramp over [0, core_start].
        if core_start > 0.0:
            if combined:
                if sp > 0.0:
                    m1 = d <= sp
                    w[m1] = np.clip(d[m1] / sp * 0.5, 0.0, 0.5)
                if st > 0.0:
                    m2 = (d > sp) & (d <= core_start)
                    w[m2] = 0.5 + np.clip((d[m2] - sp) / st * 0.5, 0.0, 0.5)
            else:
                m = d <= core_start
                w[m] = np.clip(d[m] / core_start, 0.0, 1.0)
        # Core (full adjustment).
        if core_end > core_start:
            w[(d > core_start) & (d < core_end)] = 1.0
        # End ramp over [core_end, span].
        if span > core_end:
            if combined:
                if et > 0.0:
                    m3 = (d >= core_end) & (d <= core_end + et)
                    w[m3] = 1.0 - np.clip((d[m3] - core_end) / et * 0.5, 0.0, 0.5)
                if ep > 0.0:
                    m4 = (d > core_end + et) & (d <= span)
                    w[m4] = 0.5 - np.clip((d[m4] - core_end - et) / ep * 0.5, 0.0, 0.5)
            else:
                m = (d >= core_end) & (d <= span)
                w[m] = 1.0 - np.clip((d[m] - core_end) / (span - core_end), 0.0, 1.0)
        return np.clip(w, 0.0, 1.0)

    # ------------------------------------------------------------------ #
    # Frozen pixel readout                                               #
    # ------------------------------------------------------------------ #

    def _refresh_frozen_readout(self) -> None:
        """Write the pixel readout chain of the frozen pixel into the preview readouts."""
        if self._frozen_pixel is None:
            return
        x_pos, y_pos = self._frozen_pixel
        if self._input_pixel_edit is not None:
            self._input_pixel_edit.setText(self.readout_text(x_pos, y_pos, "input"))
        if self._output_pixel_edit is not None:
            self._output_pixel_edit.setText(self.readout_text(x_pos, y_pos, "output"))

    def readout_text(self, x_pos: int, y_pos: int, role: str) -> str:
        """按当前用例拼装 (x,y) 像素读数；role='input'/'output'。

        输入侧：native(1️⃣), 处理域 full(2️⃣), 域值(3️⃣)
        输出侧：native(6️⃣), 处理域 full(5️⃣), 域值(4️⃣)
        视 clip 选项显示钳位或未钳位值（归一化值可超出 [0,1]、出现负值）。
        """
        if self._last_readout is None:
            return ""
        rc = self._last_readout
        if role == "input":
            native = rc.in_native
            full = rc.in_full_rgb if rc.in_full_rgb is not None else rc.in_full_yuv
            full_kind = 'rgb' if rc.in_full_rgb is not None else 'yuv'
            dom = rc.in_domain
        else:
            native = rc.out_native
            full = rc.out_full_rgb if rc.out_full_rgb is not None else rc.out_full_yuv
            full_kind = 'rgb' if rc.out_full_rgb is not None else 'yuv'
            dom = rc.out_domain
        return self._format_chain(native, full, full_kind, dom, x_pos, y_pos)

    @staticmethod
    def _format_chain(native, full, full_kind: str, dom, x_pos: int, y_pos: int) -> str:
        """拼装 `原生(整数), RGBF/YUVF(整数), 域(H,S,X 浮点)` 读数链。

        RGBF/YUVF 按帧位深缩放为整数显示（YUVF 先转 YUV [0,1]：U=cb+0.5、
        V=cr+0.5）。域值为直接颜色空间（RGB/YUV，归一化 [0,1]）时同样按位深
        缩放为整数；圆柱色域（H/H'SY/HSV/HSI/HSL/HCY/HSP/Lch）按浮点显示；
        H/H'SY 的 h 槽为 [YCbCr 极角, HSV 同步色相]，显示为 h/h'。
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
                'RGBF' if full_kind == 'rgb' else 'YUVF',
                int(round(f0)), int(round(f1)), int(round(f2))))
        name, dh, ds, dx = dom
        if name in ("RGB", "YUV"):
            # 直接颜色空间域（归一化 [0,1]）：按帧位深缩放为整数显示
            parts.append("{}({}, {}, {})".format(
                name,
                int(round(float(dh[y_pos, x_pos]) * max_val)),
                int(round(float(ds[y_pos, x_pos]) * max_val)),
                int(round(float(dx[y_pos, x_pos]) * max_val))))
        elif name == "H/H'SY":
            # YCbCr 极坐标域：h 槽为 (...,2) [YCbCr 极角, HSV 同步色相]。
            h_polar = float(dh[y_pos, x_pos, 0])
            h_sync = float(dh[y_pos, x_pos, 1])
            parts.append("{}({:.1f}/{:.1f}, {:.3f}, {:.3f})".format(
                name, h_polar, h_sync,
                float(ds[y_pos, x_pos]), float(dx[y_pos, x_pos])))
        else:
            parts.append("{}({:.1f}, {:.3f}, {:.3f})".format(
                name, float(dh[y_pos, x_pos]), float(ds[y_pos, x_pos]),
                float(dx[y_pos, x_pos])))
        return ", ".join(parts)
