"""
SHP (Sharpen) tab controller — PySide6 迁移试点（对应 PySimpleGUI 版 ui_shp.py）。

2026-09-04 起 UI 扩展为完整的 SharpConfig 编辑器（算法类型 + Peaking / Coring /
Gain Control / Limit Control / Shoot Control 分组 + Band Index）。锐化处理仍经
外部 sharp_full_sim_exe 执行；参数编辑只发 ``paramsChanged`` 信号（不自动重跑——
exe 耗时，由宿主决定何时重跑流水线）。

对象名映射说明（用户手动调整的 ui/shp_ui.ui）：
  - lineEdit_shpExe / btn_browseExe / btn_openDir / btn_saveConfig
  - checkBox_enableShp / comboBox_algoType(SharpFull/Lite/Cutoff)
  - groupBox_peaking: slider_peakingGain(0..1024)+spinBox_peakingGain(0..1023)
      comboBox_BandIndex(8 bands) / pushButton_resetPeaking
  - groupBox_coring(checkable): spinBox_coringZero/Thresh/Ratio (per band)
  - groupBox_gainCtrl(checkable): spinBox_posThresh / spinBox_negThresh
  - groupBox_limitCtrl(checkable): spinBox_limitCtrlPos0/Pos1/BandPos (per band)
  - groupBox_ShootCtrl(checkable): spinBox_filterRadius/DeltaOffset/ShootOver/
      shootUnder/unlimitOver/unlimitUnder + pushButton_resetShootCtrl
"""

from collections.abc import Callable
import os
import subprocess
import tempfile

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QFileDialog, QMainWindow, QWidget

try:
    from ..ui_gen.shp_ui import Ui_ShpUiWidget
except ImportError:
    from ui_gen.shp_ui import Ui_ShpUiWidget

from script.img_io import ImageFrame


class ShpUiWidget(QWidget):
    """Reusable SHP configuration widget."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create the SHP widget from the generated UI definition."""
        super().__init__(parent)
        self.ui = Ui_ShpUiWidget()
        self.ui.setupUi(self)


class ShpUiController(QObject):
    """Controls the SHP tab: sharpen params + external-exe processing.

    与 ui_shp.py（PySimpleGUI 版）保持相同语义：锐化处理经外部
    sharp_full_sim_exe 可执行文件完成；控件参数变化只发 ``paramsChanged``
    信号（不自动重跑——exe 调用耗时，由宿主决定何时重跑流水线）。
    """

    paramsChanged = Signal()

    # 与 SharpConfig s_peaking 的 8-band 数组一一对应（Band_Hor0..Usm）。
    _BAND_NAMES = ("Band_Hor0", "Band_Hor1", "Band_Hor2",
                   "Band_Ver0", "Band_Ver1", "Band_Dia0", "Band_Dia1", "Band_Usm")

    # Peaking Gain：slider 量程 [0,1024]，spin 量程 [0,1023]，同步时按 spin 上限钳位。
    _GAIN_SPIN_MAX = 1023

    def __init__(
        self,
        shp_widget: ShpUiWidget,
        parent_window: QMainWindow | None = None,
        status_callback: Callable[[str], None] | None = None,
        config_path_getter: Callable[[], str] | None = None,
    ) -> None:
        """Bind to a ShpUiWidget instance and explicit host callbacks.

        Args:
            shp_widget: A ShpUiWidget whose ``.ui`` provides the SHP controls.
            parent_window: Optional host window kept for QObject parenting.
            status_callback: Optional callback receiving status-bar text.
            config_path_getter: Optional callback returning the I/O config path.
        """
        super().__init__(parent_window or shp_widget)
        self._win = parent_window
        self.widget = shp_widget
        self.ui = shp_widget.ui
        self._status_callback = status_callback or (lambda message: None)
        self._config_path_getter = config_path_getter or (lambda: "")
        self._connect_signals()

    # ------------------------------------------------------------------ #
    # Band index helper                                                  #
    # ------------------------------------------------------------------ #

    def _band_index(self) -> int:
        """Return the selected band index [0, 7] from comboBox_BandIndex."""
        return max(0, min(self.ui.comboBox_BandIndex.currentIndex(), len(self._BAND_NAMES) - 1))

    # ------------------------------------------------------------------ #
    # Public param accessors / module protocol                           #
    # ------------------------------------------------------------------ #

    def get_params(self) -> dict:
        """Read the current SHP parameters from the UI controls."""
        ui = self.ui
        return {
            # module / exe / config
            "sharpen_exe": ui.lineEdit_shpExe.text().strip(),
            "enable": ui.checkBox_enableShp.isChecked(),
            "algo_type": ui.comboBox_algoType.currentText(),
            # peaking
            "peaking_gain": ui.spinBox_peakingGain.value(),
            "band_index": self._band_index(),
            # coring (per band)
            "coring_enable": ui.groupBox_coring.isChecked(),
            "coring_zero": ui.spinBox_coringZero.value(),
            "coring_threshold": ui.spinBox_coringThresh.value(),
            "coring_ratio": ui.spinBox_coringRatio.value(),
            # gain control
            "gain_ctrl_enable": ui.groupBox_gainCtrl.isChecked(),
            "gain_pos_thresh": ui.spinBox_posThresh.value(),
            "gain_neg_thresh": ui.spinBox_negThresh.value(),
            # limit control (per band)
            "limit_ctrl_enable": ui.groupBox_limitCtrl.isChecked(),
            "limit_pos0": ui.spinBox_limitCtrlPos0.value(),
            "limit_pos1": ui.spinBox_limitCtrlPos1.value(),
            "limit_band_pos": ui.spinBox_limitCtrlBandPos.value(),
            # shoot control
            "shoot_ctrl_enable": ui.groupBox_ShootCtrl.isChecked(),
            "filter_radius": ui.spinBox_filterRadius.value(),
            "delta_offset": ui.spinBox_deltaOffset.value(),
            "shoot_over": ui.spinBox_shootOver.value(),
            "shoot_under": ui.spinBox_shootUnder.value(),
            "shoot_over_unlimit": ui.spinBox_unlimitOver.value(),
            "shoot_under_unlimit": ui.spinBox_unlimitUnder.value(),
        }

    def process_frame(self, src_frame: ImageFrame, io_info: dict) -> tuple:
        """Run SHP processing via the external sharpen exe (mirrors ui_shp.process).

        Args:
            src_frame: yuv444p ImageFrame with the input data.
            io_info: dict with out_fmt / out_clrspc / output_dir / width / height.

        Returns:
            (ok: bool, dst_frame: ImageFrame | str)
        """
        try:
            params = self.get_params()
            sharpen_exe = params["sharpen_exe"]
            if not sharpen_exe or not os.path.isfile(sharpen_exe):
                return False, "Sharpen exe not found"

            input_fmt = src_frame.fmt
            output_fmt = io_info.get("out_fmt", input_fmt)
            output_clrspc = io_info.get("out_clrspc", src_frame.clrspc)
            output_dir = io_info.get("output_dir") or tempfile.gettempdir()
            width = io_info.get("width") or src_frame.width
            height = io_info.get("height") or src_frame.height

            # Write input channels raw (Y then U then V, each at native resolution)
            input_tmp = os.path.join(output_dir, f"_shp_input_{width}x{height}_fmt{input_fmt:#x}.yuv")
            with open(input_tmp, "wb") as f:
                src_frame.pyr.tofile(f)
                src_frame.pug.tofile(f)
                src_frame.pvb.tofile(f)

            output_file = os.path.join(output_dir, f"shp_output_{width}x{height}_fmt{output_fmt:#x}.yuv")

            cmd = [
                sharpen_exe,
                "--input", input_tmp,
                "--output", output_file,
                "--width", str(width),
                "--height", str(height),
                "--format", str(input_fmt),
            ]
            if params["enable"]:
                cmd.extend(["--peaking-gain", str(params["peaking_gain"])])
                cmd.extend(["--coring-threshold", str(params["coring_threshold"])])
                cmd.extend(["--shoot-over", str(params["shoot_over"])])
                cmd.extend(["--shoot-under", str(params["shoot_under"])])

            result = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                return False, f"Sharpen failed: {result.stderr[:200]}"
            if not os.path.isfile(output_file):
                return False, "Sharpen output file not created"

            from script.csc.run_csc import read_raw_to_planar
            output_data, _ = read_raw_to_planar(output_file, width, height, output_fmt)
            dst_frame = ImageFrame(output_data[0], output_data[1], output_data[2],
                                   output_fmt, output_clrspc)
            return True, dst_frame
        except subprocess.TimeoutExpired:
            return False, "Sharpen timeout"
        except Exception as exc:
            return False, str(exc)

    # ------------------------------------------------------------------ #
    # SharpConfig load / save                                            #
    # ------------------------------------------------------------------ #

    def _new_cfg(self):
        """Create a fresh SharpConfig (domain defaults)."""
        from script.config_def.module_config_sharp import SharpConfig
        return SharpConfig()

    def load_config(self, config_path: str | None = None) -> tuple:
        """Load a SharpConfig json file into the UI controls.

        Returns (ok, message). Band Index 选中哪个 band，就把该 band 的
        Coring/Limit 数组值写入对应控件。
        """
        cfg_path = config_path or self._config_path_getter()
        if not cfg_path or not os.path.isfile(cfg_path):
            return False, "No valid config file path specified"
        try:
            cfg = self._new_cfg()
            if not cfg.load(cfg_path):
                return False, f"Failed to load config: {cfg_path}"
            self._apply_cfg_to_ui(cfg)
            return True, f"Config loaded: {cfg_path}"
        except Exception as exc:
            return False, str(exc)

    def _apply_cfg_to_ui(self, cfg) -> None:
        """Write SharpConfig fields into the UI controls (per current band)."""
        ui = self.ui
        band = self._band_index()
        peaking = cfg.s_peaking

        ui.checkBox_enableShp.setChecked(bool(cfg.i_EnabledSharpen))
        # Peaking Gain：cfg 值可能超过 spin 上限（1023），setValue 会自动钳位。
        ui.spinBox_peakingGain.setValue(int(peaking.i_peakingGain))
        ui.slider_peakingGain.setValue(int(peaking.i_peakingGain))

        # Coring（当前 band）
        ui.groupBox_coring.setChecked(bool(cfg.s_sharp_en_ctrl.i_peaking_coring_en))
        ui.spinBox_coringZero.setValue(int(peaking.t_CoringZero[band]))
        ui.spinBox_coringThresh.setValue(int(peaking.t_CoringThreshold[band]))
        ui.spinBox_coringRatio.setValue(int(peaking.t_CoringRatio[band]))

        # Gain Control（映射不确定：pos/negThresh 具体字段待确认，先只同步使能）
        ui.groupBox_gainCtrl.setChecked(bool(cfg.s_sharp_en_ctrl.i_peaking_gain_en))

        # Limit Control（当前 band）
        ui.groupBox_limitCtrl.setChecked(bool(cfg.s_sharp_en_ctrl.i_peaking_limit_ctrl_en))
        ui.spinBox_limitCtrlPos0.setValue(int(peaking.t_LimitPos0[band]))
        ui.spinBox_limitCtrlPos1.setValue(int(peaking.t_LimitPos1[band]))
        ui.spinBox_limitCtrlBandPos.setValue(int(peaking.t_LimitboundPos[band]))

        # Shoot Control
        ui.groupBox_ShootCtrl.setChecked(bool(cfg.s_sharp_en_ctrl.i_shoot_ctrl_en))
        shoot = cfg.s_shootCtrl
        ui.spinBox_filterRadius.setValue(int(shoot.i_FilterRadius))
        ui.spinBox_deltaOffset.setValue(int(shoot.i_Delta_offset))
        ui.spinBox_shootOver.setValue(int(shoot.i_Alpha_over))
        ui.spinBox_shootUnder.setValue(int(shoot.i_Alpha_under))
        ui.spinBox_unlimitOver.setValue(int(shoot.i_Alpha_over_unlimit))
        ui.spinBox_unlimitUnder.setValue(int(shoot.i_Alpha_under_unlimit))

    def save_config(self, config_path: str | None = None) -> tuple:
        """Save the UI params onto a SharpConfig json file.

        Returns (ok, message). ``config_path`` 缺省时取 I/O 的 config path。
        """
        cfg_path = config_path or self._config_path_getter()
        if not cfg_path:
            return False, "No config file path specified"
        try:
            cfg = self._new_cfg()
            if os.path.isfile(cfg_path):
                cfg.load(cfg_path)      # 已有配置先加载，只覆盖 UI 涉及的字段
            self._apply_ui_to_cfg(cfg)
            cfg.dump(cfg_path)
            return True, f"Config saved to {cfg_path}"
        except Exception as exc:
            return False, str(exc)

    def _apply_ui_to_cfg(self, cfg) -> None:
        """Write UI controls into SharpConfig fields (per current band)."""
        ui = self.ui
        band = self._band_index()
        peaking = cfg.s_peaking

        cfg.i_EnabledSharpen = 1 if ui.checkBox_enableShp.isChecked() else 0
        cfg.s_sharp_en_ctrl.i_peaking_en = 1 if ui.checkBox_enableShp.isChecked() else 0

        peaking.i_peakingGain = ui.spinBox_peakingGain.value()

        # Coring（当前 band）
        cfg.s_sharp_en_ctrl.i_peaking_coring_en = 1 if ui.groupBox_coring.isChecked() else 0
        peaking.t_CoringZero[band] = ui.spinBox_coringZero.value()
        peaking.t_CoringThreshold[band] = ui.spinBox_coringThresh.value()
        peaking.t_CoringRatio[band] = ui.spinBox_coringRatio.value()

        # Gain Control（映射不确定：pos/negThresh 具体字段待确认，先只同步使能）
        cfg.s_sharp_en_ctrl.i_peaking_gain_en = 1 if ui.groupBox_gainCtrl.isChecked() else 0

        # Limit Control（当前 band）
        cfg.s_sharp_en_ctrl.i_peaking_limit_ctrl_en = 1 if ui.groupBox_limitCtrl.isChecked() else 0
        peaking.t_LimitPos0[band] = ui.spinBox_limitCtrlPos0.value()
        peaking.t_LimitPos1[band] = ui.spinBox_limitCtrlPos1.value()
        peaking.t_LimitboundPos[band] = ui.spinBox_limitCtrlBandPos.value()

        # Shoot Control
        cfg.s_sharp_en_ctrl.i_shoot_ctrl_en = 1 if ui.groupBox_ShootCtrl.isChecked() else 0
        shoot = cfg.s_shootCtrl
        shoot.i_FilterRadius = ui.spinBox_filterRadius.value()
        shoot.i_Delta_offset = ui.spinBox_deltaOffset.value()
        shoot.i_Alpha_over = ui.spinBox_shootOver.value()
        shoot.i_Alpha_under = ui.spinBox_shootUnder.value()
        shoot.i_Alpha_over_unlimit = ui.spinBox_unlimitOver.value()
        shoot.i_Alpha_under_unlimit = ui.spinBox_unlimitUnder.value()

    # ------------------------------------------------------------------ #
    # Reset helpers                                                      #
    # ------------------------------------------------------------------ #

    def _on_reset_peaking(self) -> None:
        """Reset the peaking group to fresh SharpConfig defaults."""
        try:
            cfg = self._new_cfg()
            ui = self.ui
            ui.spinBox_peakingGain.setValue(int(cfg.s_peaking.i_peakingGain))
            ui.slider_peakingGain.setValue(int(cfg.s_peaking.i_peakingGain))
            ui.comboBox_BandIndex.setCurrentIndex(0)
        except Exception as exc:
            self._status_callback(f"Reset peaking failed: {exc}")
        self.paramsChanged.emit()

    def _on_reset_shoot_ctrl(self) -> None:
        """Reset the shoot-control group to fresh SharpConfig defaults."""
        try:
            cfg = self._new_cfg()
            shoot = cfg.s_shootCtrl
            ui = self.ui
            ui.spinBox_filterRadius.setValue(int(shoot.i_FilterRadius))
            ui.spinBox_deltaOffset.setValue(int(shoot.i_Delta_offset))
            ui.spinBox_shootOver.setValue(int(shoot.i_Alpha_over))
            ui.spinBox_shootUnder.setValue(int(shoot.i_Alpha_under))
            ui.spinBox_unlimitOver.setValue(int(shoot.i_Alpha_over_unlimit))
            ui.spinBox_unlimitUnder.setValue(int(shoot.i_Alpha_under_unlimit))
        except Exception as exc:
            self._status_callback(f"Reset shoot failed: {exc}")
        self.paramsChanged.emit()

    # ------------------------------------------------------------------ #
    # Signal wiring                                                      #
    # ------------------------------------------------------------------ #

    def _connect_signals(self) -> None:
        """Wire SHP widget signals to internal handlers."""
        ui = self.ui

        # Peaking Gain slider <-> spin（slider 上限 1024 > spin 上限 1023）
        ui.slider_peakingGain.valueChanged.connect(self._on_gain_slider_changed)
        ui.spinBox_peakingGain.valueChanged.connect(self._on_gain_spin_changed)

        # 分组/使能开关与全部参数控件 -> paramsChanged
        ui.checkBox_enableShp.toggled.connect(self._on_param_changed)
        ui.comboBox_algoType.currentIndexChanged.connect(self._on_param_changed)
        ui.comboBox_BandIndex.currentIndexChanged.connect(self._on_param_changed)
        for box in (ui.groupBox_coring, ui.groupBox_gainCtrl,
                    ui.groupBox_limitCtrl, ui.groupBox_ShootCtrl):
            box.toggled.connect(self._on_param_changed)
        for spin in (
            ui.spinBox_coringZero, ui.spinBox_coringThresh, ui.spinBox_coringRatio,
            ui.spinBox_posThresh, ui.spinBox_negThresh,
            ui.spinBox_limitCtrlPos0, ui.spinBox_limitCtrlPos1, ui.spinBox_limitCtrlBandPos,
            ui.spinBox_filterRadius, ui.spinBox_deltaOffset,
            ui.spinBox_shootOver, ui.spinBox_shootUnder,
            ui.spinBox_unlimitOver, ui.spinBox_unlimitUnder,
        ):
            spin.valueChanged.connect(self._on_param_changed)

        # 按钮
        ui.lineEdit_shpExe.editingFinished.connect(self._on_param_changed)
        ui.btn_browseExe.clicked.connect(self._on_browse_exe)
        ui.btn_openDir.clicked.connect(self._on_open_exe_dir)
        ui.btn_saveConfig.clicked.connect(self._on_save_config)
        ui.pushButton_resetPeaking.clicked.connect(self._on_reset_peaking)
        ui.pushButton_resetShootCtrl.clicked.connect(self._on_reset_shoot_ctrl)

    # ------------------------------------------------------------------ #
    # Signal handlers                                                    #
    # ------------------------------------------------------------------ #

    def _on_gain_slider_changed(self, value: int) -> None:
        """Sync the peaking-gain spin box from the slider (clamp to spin max)."""
        self.ui.spinBox_peakingGain.setValue(min(int(value), self.ui.spinBox_peakingGain.maximum()))
        self.paramsChanged.emit()

    def _on_gain_spin_changed(self, value: int) -> None:
        """Sync the peaking-gain slider from the spin box."""
        self.ui.slider_peakingGain.setValue(int(value))
        self.paramsChanged.emit()

    def _on_param_changed(self, *_args) -> None:
        """Emit the params-changed signal (no auto re-run; host decides)."""
        self.paramsChanged.emit()

    def _on_browse_exe(self) -> None:
        """Browse for the sharpen executable."""
        current = self.ui.lineEdit_shpExe.text().strip()
        start_dir = os.path.dirname(current) if current else os.getcwd()
        path, _ = QFileDialog.getOpenFileName(
            None, "Select Sharpen Exe", start_dir,
            "Executable (*.exe);;All Files (*)")
        if path:
            self.ui.lineEdit_shpExe.setText(path)
            self._on_param_changed()

    def _on_open_exe_dir(self) -> None:
        """Open the sharpen-exe directory in the file explorer."""
        exe_path = self.ui.lineEdit_shpExe.text().strip()
        exe_dir = os.path.dirname(exe_path) if exe_path else ""
        if not exe_dir or not os.path.isdir(exe_dir):
            self._status_callback("Sharpen exe directory not found")
            return
        os.startfile(exe_dir)

    def _on_save_config(self) -> None:
        """Save the current SHP configuration to the I/O config path."""
        ok, message = self.save_config()
        self._status_callback(message)
