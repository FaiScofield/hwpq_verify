"""
HSV tab controller — encapsulates all HSV-related UI behavior and state.

调整语义（对应 script/bcsh/hsv_adjust.py）：
  V：Contrast 乘性 + delta_v 加性，增益参考点由 comboBox_modeC 选择：
     GainAtMidPoint（过 v=0.5 中点）/ GainAtZeroPoint（过 v=0 原点）/ GainAtBothZeroAndMid
  S：mode 切换加性/乘性            s'=clip(s+ds) 或 s'=clip(s*ds)
  H：始终加性（或 Same Hue Goal 向指定色调旋转）
指定色调（groupBox_setHueRange 勾选）：仅色调落在 [hs, he] 附近的像素被处理，
通过 Tail（向内）/ Pad（向外）的 alpha blending 过渡。
"""

from collections.abc import Callable
import time

import numpy as np
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QLineEdit, QMainWindow, QWidget

from script.bcsh.hsv_adjust import adjust_hsv, rgb_to_hsv, hsv_to_rgb
from script.img_io import (
    ImageFrame, _csc_range_params, is_limited_range, yuv_to_rgb,
    _PLANAR_RGB_8, _PLANAR_RGB_10,
)

try:
    from ..ui_gen.hsv_ui import Ui_HsvUiWidget
except ImportError:
    from ui_gen.hsv_ui import Ui_HsvUiWidget


class HsvUiWidget(QWidget):
    """Reusable HSV configuration widget."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create the HSV widget from the generated UI definition."""
        super().__init__(parent)
        self.ui = Ui_HsvUiWidget()
        self.ui.setupUi(self)


class HsvUiController:
    """Controls the HSV tab: V/S/H adjustment and specified-hue processing."""

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

        self._latest_output_frame: ImageFrame | None = None
        self._frozen_pixel: tuple[int, int] | None = None
        self._last_input_rgb = None
        self._last_output_rgb = None
        self._s_mode = True           # False=add, True=mul（S 通道模式，.ui 默认 Mul）
        self._work_size: tuple[int, int] | None = None   # 最近一次预览处理的分辨率

        # --- Auto-run debounce timer ---
        self.auto_run_timer = QTimer(self.widget)
        self.auto_run_timer.setSingleShot(True)
        self.auto_run_timer.timeout.connect(self._do_auto_run)

        self._connect_signals()
        self._init_state()

    def _init_state(self) -> None:
        """Perform initial state sync after all widgets are ready."""
        # .ui 默认 Multiplicative：同步 S 模式内部状态并应用其控件范围/中性值。
        self._s_mode = self.ui.radioButton_modeMul.isChecked()
        self._apply_s_mode_ui(self._s_mode)
        self._update_hue_limits()
        self._on_same_hue_goal_toggled(self.ui.checkBox_sameHueGoal.isChecked())
        # A checkable QGroupBox defaults to checked=True; the specified-hue
        # adjustment must be OFF by default so the whole image is processed.
        self.ui.groupBox_setHueRange.setChecked(False)

    # ------------------------------------------------------------------ #
    # Public accessors                                                   #
    # ------------------------------------------------------------------ #

    def request_auto_run(self) -> None:
        """Public helper that schedules HSV processing with the current input."""
        self._schedule_auto_run()

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
        ui.radioButton_modeAdd.toggled.connect(self._on_mode_changed)
        ui.radioButton_modeMul.toggled.connect(self._on_mode_changed)
        ui.comboBox_modeC.currentIndexChanged.connect(self._schedule_auto_run)
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
        ui.checkBox_sameHueGoal.toggled.connect(self._on_same_hue_goal_toggled)
        # Mapped slider-spin pairs (scale maps slider int to spin value).
        self._connect_mapped_slider_spin(ui.slider_gainC, ui.spinBox_gainC, 100.0)
        self._connect_mapped_slider_spin(ui.slider_deltaV, ui.spinBox_deltaV, 100.0)
        self._connect_mapped_slider_spin(ui.slider_deltaS, ui.spinBox_deltaS, 100.0)
        self._connect_mapped_slider_spin(ui.slider_deltaH, ui.spinBox_deltaH, 1.0)
        self._connect_mapped_slider_spin(ui.slider_sameHueGoal, ui.spinBox_sameHueGoal, 1.0)
        # Schedule auto-run on every adjust value change.
        for slider, spin in ((ui.slider_gainC, ui.spinBox_gainC),
                             (ui.slider_deltaV, ui.spinBox_deltaV),
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

    def _apply_s_mode_ui(self, is_mul: bool) -> None:
        """Set spin/slider ranges and the label for the S mode (no value remap)."""
        if is_mul:
            self.ui.spinBox_deltaS.setRange(0.0, 4.0)
            self.ui.spinBox_deltaS.setSingleStep(0.02)
            self.ui.slider_deltaS.setRange(0, 400)
            self.ui.label_deltaS.setText("Gain S")
        else:
            self.ui.spinBox_deltaS.setRange(-1.0, 1.0)
            self.ui.spinBox_deltaS.setSingleStep(0.01)
            self.ui.slider_deltaS.setRange(-100, 100)
            self.ui.label_deltaS.setText("Delta S")

    def _on_mode_changed(self, *_args) -> None:
        """Switch the saturation adjustment between additive and multiplicative.

        Only the S channel is affected: the deltaS spin/slider range and its
        neutral (default) value change with the mode (add: 0.0, mul: 1.0).
        The V/H/Contrast controls keep their values.  Initial state and
        redundant toggled signals are no-ops.
        """
        del _args
        is_mul = self.ui.radioButton_modeMul.isChecked()
        if is_mul == self._s_mode:
            return
        neutral = 1.0 if is_mul else 0.0
        self._apply_s_mode_ui(is_mul)
        self._set_spin_value(self.ui.spinBox_deltaS, neutral)
        self._set_slider_value(self.ui.slider_deltaS, int(round(neutral * 100)))
        self._s_mode = is_mul
        self._schedule_auto_run()

    def _on_reset_c(self) -> None:
        """Reset the Contrast gain to neutral (1.0)."""
        self._reset_mapped(self.ui.slider_gainC, self.ui.spinBox_gainC, 1.0, 100.0)

    def _on_reset_v(self) -> None:
        """Reset the Delta V to neutral (0.0)."""
        self._reset_mapped(self.ui.slider_deltaV, self.ui.spinBox_deltaV, 0.0, 100.0)

    def _on_reset_s(self) -> None:
        """Reset the S value to its mode neutral (0.0 add / 1.0 mul)."""
        neutral = 1.0 if self.ui.radioButton_modeMul.isChecked() else 0.0
        self._reset_mapped(self.ui.slider_deltaS, self.ui.spinBox_deltaS, neutral, 100.0)

    def _on_reset_h(self) -> None:
        """Reset the Delta H to neutral (0 deg)."""
        self._reset_mapped(self.ui.slider_deltaH, self.ui.spinBox_deltaH, 0, 1.0)

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
        for spin in (self.ui.spinBox_hueStartTail, self.ui.spinBox_hueEndTail,
                     self.ui.spinBox_hueStartPad, self.ui.spinBox_hueEndPad):
            spin.setMaximum(max_side)

    def _on_same_hue_goal_toggled(self, checked: bool) -> None:
        """Enable the same-hue-goal target controls and re-run."""
        self.ui.spinBox_sameHueGoal.setEnabled(checked)
        self.ui.slider_sameHueGoal.setEnabled(checked)
        self._schedule_auto_run()

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
            self._status_callback("HSV adjust disabled")
            return
        start_time = time.time()
        try:
            src_w, src_h = input_frame.width, input_frame.height
            work_w, work_h = self._resolve_work_size(src_w, src_h)
            self._work_size = (work_w, work_h)
            out_frame = self._process_frame(input_frame, (work_w, work_h))
            self._output_callback(out_frame)
            self._latest_output_frame = out_frame
            elapsed_ms = (time.time() - start_time) * 1000.0
            self._refresh_frozen_readout()
            self._status_callback(f"Processing completed in {elapsed_ms:.2f} ms")
            if self._time_cost_callback is not None:
                self._time_cost_callback(elapsed_ms)
        except Exception as exc:
            print("HSV processing failed:", exc)
            self._status_callback(f"Processing failed: {exc}")

    def get_full_res_output(self) -> ImageFrame | None:
        """Return a full-resolution output frame for saving.

        若最近一次预览处理已在源分辨率进行（源 <= 预览目标），直接复用
        缓存帧；否则按源分辨率重算一次，保证保存的文件为精确结果。
        """
        input_frame = self._input_provider()
        if input_frame is None:
            return None
        src_w, src_h = input_frame.width, input_frame.height
        if self._work_size == (src_w, src_h) and self._latest_output_frame is not None:
            return self._latest_output_frame
        out_frame = self._process_frame(input_frame)
        self._latest_output_frame = out_frame
        self._work_size = (src_w, src_h)
        return out_frame

    def _resolve_work_size(self, src_w: int, src_h: int) -> tuple[int, int]:
        """Return the processing resolution: min(source, preview target)."""
        if self._work_size_provider is not None:
            return self._work_size_provider(src_w, src_h)
        return src_w, src_h

    def _process_frame(
        self, frame: ImageFrame, work_wh: tuple[int, int] | None = None,
    ) -> ImageFrame:
        """Process one frame (optionally downsampled) and return an RGB frame.

        处理分辨率取 min(源分辨率, work_wh)；降采样处理完成后升采样回源
        分辨率，保证预览显示与输入对齐（预览显示逻辑无需感知降采样）。
        """
        src_w, src_h = frame.width, frame.height
        work_frame = frame
        if work_wh is not None and (work_wh[0] < src_w or work_wh[1] < src_h):
            work_frame = self._downsample_frame(frame, work_wh[0], work_wh[1])

        r, g, b, depth = self._frame_to_rgb_planar(work_frame)
        max_val = (1 << depth) - 1
        rgb_planar = np.stack([r, g, b], axis=0).astype(np.float32)   # (3, H, W)
        rgb_norm = rgb_planar.transpose(1, 2, 0) / max_val            # (H, W, 3)
        hsv = np.stack(rgb_to_hsv(rgb_norm), axis=-1)                 # (H, W, 3)
        h_deg = hsv[..., 0]

        # Fully-adjusted HSV -> RGB.
        adj_hsv = self._compute_adjusted_hsv(hsv, h_deg)
        rgb_adj = hsv_to_rgb(adj_hsv)                                 # (H, W, 3)

        # Specified-hue blend weight (1.0 = full image).
        if self.ui.groupBox_setHueRange.isChecked():
            w = self._hue_blend_weights(
                h_deg,
                self.ui.spinBox_hueStart.value(),
                self.ui.spinBox_hueEnd.value(),
                self.ui.spinBox_hueStartTail.value(),
                self.ui.spinBox_hueEndTail.value(),
                self.ui.spinBox_hueStartPad.value(),
                self.ui.spinBox_hueEndPad.value(),
            )
        else:
            w = np.ones_like(h_deg, dtype=np.float32)

        # Blend in RGB space (avoids angular H interpolation artifacts).
        rgb_out = rgb_norm * (1.0 - w[..., None]) + rgb_adj * w[..., None]
        rgb_out = np.clip(rgb_out, 0.0, 1.0)
        out = (rgb_out * max_val + 0.5).astype(r.dtype)
        out_planar = out.transpose(2, 0, 1)                           # (3, H, W)
        out_fmt = _PLANAR_RGB_10 if depth >= 10 else _PLANAR_RGB_8
        # HSV 输出始终为 full-range RGB；目标色彩空间跟随输入
        # (limited -> RGB_Limited(0)，full -> RGB_Full(1))，保存时按需 f2l。
        out_clrspc = 0 if is_limited_range(frame.clrspc) else 1

        # 降采样处理时升采样回源分辨率，保证预览/像素读数与输入对齐。
        if work_frame is not frame:
            out_planar = self._upsample_planar(out_planar, src_h, src_w)
        out_frame = ImageFrame(out_planar[0], out_planar[1], out_planar[2], out_fmt, out_clrspc)

        # Cache source-resolution RGB planes for the frozen-pixel readout.
        if work_frame is not frame:
            in_planar = self._upsample_planar(
                np.stack([r, g, b], axis=0), src_h, src_w)
            self._last_input_rgb = (in_planar[0], in_planar[1], in_planar[2], depth)
        else:
            self._last_input_rgb = (r, g, b, depth)
        self._last_output_rgb = (out_planar[0], out_planar[1], out_planar[2], depth)
        return out_frame

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

    def _frame_to_rgb_planar(self, frame: ImageFrame) -> tuple[np.ndarray, np.ndarray, np.ndarray, int]:
        """Return (r, g, b, depth) full-range RGB planar (H, W) arrays."""
        depth = frame.depth
        max_val = (1 << depth) - 1
        if frame.is_rgb:
            r, g, b = frame.pyr, frame.pug, frame.pvb
            if frame.clrspc == 0:  # limited RGB -> expand to full (depth-aware)
                # 8bit [16,235] / 10bit [64,940]
                rp = _csc_range_params(depth)
                lo = rp["yr_lo_l"]
                scale = max_val / (rp["yr_hi_l"] - lo)
                r = np.clip(np.rint((r.astype(np.float32) - lo) * scale), 0, max_val).astype(r.dtype)
                g = np.clip(np.rint((g.astype(np.float32) - lo) * scale), 0, max_val).astype(g.dtype)
                b = np.clip(np.rint((b.astype(np.float32) - lo) * scale), 0, max_val).astype(b.dtype)
        else:
            input_cs = frame.clrspc if frame.clrspc in (2, 3, 4, 5, 6, 7) else 5
            r, g, b = yuv_to_rgb(frame.pyr, frame.pug, frame.pvb, input_cs=input_cs, output_cs=1)
        return r, g, b, depth

    def _mode_c_code(self) -> str:
        """Map comboBox_modeC text to adjust_hsv mode_c ('mid'/'zero'/'both')."""
        text = self.ui.comboBox_modeC.currentText()
        return {'GainAtMidPoint': 'mid',
                'GainAtZeroPoint': 'zero',
                'GainAtBothZeroAndMid': 'both'}.get(text, 'mid')

    def _compute_adjusted_hsv(
        self, hsv: np.ndarray, h_deg: np.ndarray,
    ) -> np.ndarray:
        """Compute the fully-adjusted HSV array from the current controls."""
        dv = float(self.ui.spinBox_deltaV.value())
        gc = float(self.ui.spinBox_gainC.value())
        ds = float(self.ui.spinBox_deltaS.value())
        dh_deg = float(self.ui.spinBox_deltaH.value())
        mode = 'mul' if self.ui.radioButton_modeMul.isChecked() else 'add'
        # S Tolerance：控件已是归一化浮点 [0, 0.1]，直接传给 adjust_hsv。
        tolerance_s = float(self.ui.spinBox_toleranceS.value())
        adj_hsv = adjust_hsv(hsv, delta_v=dv, delta_s=ds, delta_h=dh_deg / 360.0,
                             gain_c=gc, mode=mode, tolerance_s=tolerance_s,
                             mode_c=self._mode_c_code())
        if self.ui.checkBox_sameHueGoal.isChecked():
            target = float(self.ui.spinBox_sameHueGoal.value())
            progress = float(np.clip(dh_deg / 180.0, -1.0, 1.0))
            arc = ((target - h_deg + 180.0) % 360.0) - 180.0   # shortest signed arc
            h_adj = (h_deg + np.abs(progress) * arc) % 360.0
            adj_hsv = np.stack([h_adj, adj_hsv[..., 1], adj_hsv[..., 2]], axis=-1)
        return adj_hsv

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
        """Write RGB+HSV values of the frozen pixel into the preview readouts.

        仅当本地 RGB 缓存存在时覆盖对应输入/输出框；缓存缺失（例如
        enableHsvAdj 关闭、尚未处理过）时保留 preview 已填充的值。
        """
        if self._frozen_pixel is None:
            return
        x_pos, y_pos = self._frozen_pixel
        if self._last_input_rgb is not None and self._input_pixel_edit is not None:
            self._input_pixel_edit.setText(
                self._pixel_hsv_text(self._last_input_rgb, x_pos, y_pos))
        if self._last_output_rgb is not None and self._output_pixel_edit is not None:
            self._output_pixel_edit.setText(
                self._pixel_hsv_text(self._last_output_rgb, x_pos, y_pos))

    @staticmethod
    def _pixel_hsv_text(rgb_cache, x_pos: int, y_pos: int) -> str:
        """Format one pixel as 'RGB(...) HSV(...)' from a (r, g, b, depth) cache."""
        if rgb_cache is None:
            return ""
        r, g, b, depth = rgb_cache
        if y_pos < 0 or x_pos < 0 or y_pos >= r.shape[0] or x_pos >= r.shape[1]:
            return ""
        rv = int(r[y_pos, x_pos])
        gv = int(g[y_pos, x_pos])
        bv = int(b[y_pos, x_pos])
        max_val = (1 << depth) - 1
        h, s, v = rgb_to_hsv(np.array([rv, gv, bv], dtype=np.float32) / max_val)
        return f"RGB({rv}, {gv}, {bv}) HSV({float(h):.1f}, {float(s):.3f}, {float(v):.3f})"
