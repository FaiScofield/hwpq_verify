"""
DCI (Dynamic Contrast Improvement) tab controller — PySide6.

UI 定义在 ui/dci_ui.ui（Qt Designer，用户手工调整），本模块为代码适配：
  - 顶层：Enable DCI + EXE/Browse/OpenDir/ReadConfig/SaveConfig + Median/Dump。
  - CF 组（checkable）内含三条 Gain spin + “Show Curves” 勾选（Low/Mid/High/CF
    Result）与 Clear 按钮，下方 tabWidget：
      · tab_curve（CF Curves）：显示 cf_dciWgtCoef_low/mid/high 三条系数曲线，
        可叠加显示 CF 处理结果曲线（dump: dci_glb1_cf_lut_frm0.txt，需 output
        目录 + Dump 产物存在）。
      · tab_weight（CF Weights）：显示 cf_dciWeight_low/mid/high 三条权重曲线，
        并叠加输入图像 Y 直方图（由 histogram_provider 提供，可为空）。
    Low/Mid/High 显隐同时作用于两个 tab；Clear 按当前 tab 语义：Curves 页把
    对应系数曲线置为 y=x 斜线，Weights 页置为默认权重 1。
  - HE/BS/WS/CA/CLAHE 组（checkable）提供对应参数，组勾选映射组级 enable。
  处理经外部 DCI exe；Enable 关闭时 process_frame 原帧直通。
"""

from collections.abc import Callable
import os
import subprocess
import tempfile

import numpy as np
from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QCheckBox, QDoubleSpinBox, QFileDialog, QGroupBox, QMainWindow,
    QSpinBox, QVBoxLayout, QWidget,
)

from script.csc.run_csc import read_raw_to_planar
from script.img_io import ImageFrame

try:
    from ..ui_gen.dci_ui import Ui_DciUiWidget
except ImportError:
    from ui_gen.dci_ui import Ui_DciUiWidget

# ------------------------------------------------------------------ #
# Parameter / group tables (object names follow the hand-edited .ui) #
# ------------------------------------------------------------------ #
# (cfg attr, ui object name, is_float)
DCI_PARAM_SPECS = [
    ("cf_gain_low",              "spin_cfGainLow",    False),
    ("cf_gain_mid",              "spin_cfGainMid",    False),
    ("cf_gain_high",             "spin_cfGainHigh",   False),
    ("ctrl_dci_CF_HE_ratio",     "spin_CF_CFHE",      False),
    ("he_split_point",           "spin_HE_SPLIT",     False),
    ("he_overlap",               "spin_HE_OVERLAP",   False),
    ("he_left_clip",             "dspin_HE_LC",       True),
    ("he_right_clip",            "dspin_HE_RC",       True),
    ("bs_set_point",             "spin_BS_SP",        False),
    ("bs_ratio",                 "spin_BS_RATIO",     False),
    ("bs_overlap",               "spin_BS_OVERLAP",   False),
    ("ws_set_point",             "spin_WS_SP",        False),
    ("ws_ratio",                 "spin_WS_RATIO",     False),
    ("ws_overlap",               "spin_WS_OVERLAP",   False),
    ("ca_saturation_w",          "spin_CA_SATW",      False),
    ("ca_adj_luma_coring_zero",  "spin_CA_CORING",    False),
    ("ca_adj_luma_coring_thrd",  "spin_CA_THRESH",    False),
    ("clahe_clip_value",         "dspin_CLAHE_CV",    True),
    ("clahe_local_ratio",        "spin_CLAHE_LR",     False),
    ("clahe_left_alpha",         "dspin_CLAHE_LA",    True),
    ("clahe_left_lumRatio",      "dspin_CLAHE_LLR",   True),
]
# (cfg attr, group box object name) — checkable group = 该组 enable
DCI_GROUP_ENABLE_MAP = [
    ("bs_enable", "groupBox_BS"),
    ("ws_enable", "groupBox_WS"),
    ("ca_enable", "groupBox_CA"),
    ("clahe_en",  "groupBox_CLAHE"),
]

# 曲线相关
_CURVE_KEYS = ("low", "mid", "high")
_CURVE_COLORS = {
    "low": QColor(200, 60, 60), "mid": QColor(0, 160, 60),
    "high": QColor(40, 100, 230), "cfres": QColor(40, 40, 40),
}
_CF_COEF_ARR = {k: f"cf_dciWgtCoef_{k}" for k in _CURVE_KEYS}
_CF_WEIGHT_ARR = {k: f"cf_dciWeight_{k}" for k in _CURVE_KEYS}


def _resolve_exe_path(path: str) -> str:
    """Resolve a relative path against the project root; '' stays ''."""
    if not path:
        return ""
    if os.path.isabs(path):
        return path
    root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))))
    return os.path.join(root, path)


class DciChartWidget(QWidget):
    """Multi-curve chart with optional histogram bars behind the curves.

    - ``set_series([(name, QColor, values), ...])`` draws several polylines.
    - ``set_histogram(np.ndarray | None)`` draws translucent vertical bars.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumSize(420, 240)
        self.padding = 8
        self._series: list[tuple[str, QColor, list[float]]] = []
        self._hist: np.ndarray | None = None
        self._x_labels = None

    # ------------------------------------------------------------------ #
    def clear(self) -> None:
        self._series = []
        self._hist = None
        self.update()

    def set_series(self, series: list[tuple[str, QColor, list | np.ndarray]]) -> None:
        self._series = [
            (name, color, [float(v) for v in values])
            for name, color, values in series if len(values) > 0
        ]
        self.update()

    def set_histogram(self, hist: np.ndarray | None) -> None:
        self._hist = None if hist is None else np.asarray(hist, dtype=np.float64)
        self.update()

    def set_x_labels(self, labels: list[str] | None) -> None:
        self._x_labels = labels
        self.update()

    # ------------------------------------------------------------------ #
    def _v_range(self):
        vals = [v for _n, _c, vs in self._series for v in vs]
        lo = min(vals) if vals else 0.0
        hi = max(vals) if vals else 1.0
        if hi - lo < 1e-6:
            hi = lo + 1.0
        pad = (hi - lo) * 0.08
        return lo - pad, hi + pad

    def _to_y(self, value: float) -> float:
        lo, hi = self._v_range()
        h = self.height() - 2 * self.padding
        return self.padding + h * (1 - (value - lo) / (hi - lo))

    def _to_x(self, index: float, count: int) -> float:
        w = self.width() - 2 * self.padding
        return self.padding + w * index / max(1, count - 1)

    def paintEvent(self, event) -> None:
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(255, 255, 255))
        w, h = self.width(), self.height()
        lo, hi = self._v_range()

        # horizontal grid
        painter.setPen(QPen(QColor(210, 210, 210), 1, Qt.PenStyle.DashLine))
        for frac in (0.25, 0.5, 0.75):
            y = self._to_y(lo + (hi - lo) * (1 - frac))
            painter.drawLine(self.padding, int(y), w - self.padding, int(y))

        # histogram bars (translucent, scaled to its own max over the chart height)
        if self._hist is not None and self._hist.size > 0:
            hmax = float(self._hist.max()) or 1.0
            n = self._hist.size
            bw = max(1.0, (w - 2 * self.padding) / n)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(120, 120, 120, 70))
            for i in range(n):
                bh = (self.height() - 2 * self.padding) * (self._hist[i] / hmax)
                x0 = self._to_x(i + 0.5, n)
                painter.drawRect(int(x0), int(self.height() - self.padding - bh),
                                 max(1, int(bw * 0.7)), int(bh))

        # curves
        for name, color, values in self._series:
            pen = QPen(color, 2)
            if name == "CF Result":
                pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(pen)
            n = len(values)
            prev = None
            for i in range(n):
                pt = (self._to_x(i, n), self._to_y(values[i]))
                if prev is not None:
                    painter.drawLine(int(prev[0]), int(prev[1]),
                                     int(pt[0]), int(pt[1]))
                prev = pt

        # legend
        if self._series:
            x = self.padding + 4
            y = self.padding + 10
            for name, color, _vs in self._series:
                painter.setPen(QPen(color, 2))
                painter.drawLine(int(x), int(y - 5), int(x + 26), int(y - 5))
                painter.setPen(QColor(0, 0, 0))
                painter.drawText(int(x + 30), int(y), name)
                y += 16


class DciUiWidget(QWidget):
    """Reusable DCI configuration widget (loads ui_gen/dci_ui.Ui_DciUiWidget)."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Load the generated DCI UI and mount the chart widgets into the tabs."""
        super().__init__(parent)
        self.ui = Ui_DciUiWidget()
        self.ui.setupUi(self)
        # 参数控件映射（cfg attr -> 控件），仅登记 .ui 中实际存在的
        self.ui.param_controls: dict[str, QWidget] = {}
        for attr, obj_name, _is_float in DCI_PARAM_SPECS:
            if hasattr(self.ui, obj_name):
                self.ui.param_controls[attr] = getattr(self.ui, obj_name)
        # 组级 enable（checkable group box）
        self.ui.group_enables: dict[str, QGroupBox] = {}
        for _attr, box_name in DCI_GROUP_ENABLE_MAP:
            if hasattr(self.ui, box_name):
                self.ui.group_enables[box_name] = getattr(self.ui, box_name)
        # 曲线 tab 内挂图表
        self.ui.curve_chart = DciChartWidget(self)
        lay_c = QVBoxLayout(self.ui.tab_curve)
        lay_c.setContentsMargins(2, 2, 2, 2)
        lay_c.addWidget(self.ui.curve_chart)
        self.ui.weight_chart = DciChartWidget(self)
        lay_w = QVBoxLayout(self.ui.tab_weight)
        lay_w.setContentsMargins(2, 2, 2, 2)
        lay_w.addWidget(self.ui.weight_chart)


class DciUiController(QObject):
    """Controls the DCI tab: params + curve/weight charts + exe chain stage."""

    paramsChanged = Signal()

    def __init__(
        self,
        dci_widget: DciUiWidget,
        parent_window: QMainWindow | None = None,
        status_callback: Callable[[str], None] | None = None,
        config_path_getter: Callable[[], str] | None = None,
        output_dir_getter: Callable[[], str] | None = None,
        histogram_provider: Callable[[], np.ndarray | None] | None = None,
    ) -> None:
        super().__init__(parent_window or dci_widget)
        self.widget = dci_widget
        self.ui = dci_widget.ui
        self._win = parent_window
        self._status_callback = status_callback or (lambda message: None)
        self._config_path_getter = config_path_getter or (lambda: "")
        self._output_dir_getter = output_dir_getter or (lambda: "")
        self._histogram_provider = histogram_provider
        # 工作配置（承载 cf 系数/权重数组等非 spin 字段）
        from config_def.module_config_dci import DciUserConfig
        self._cfg = DciUserConfig()
        self._connect_signals()
        self._refresh_curve_charts()

    # ------------------------------------------------------------------ #
    # Public helpers / module protocol                                   #
    # ------------------------------------------------------------------ #

    @property
    def enable_checkbox(self) -> QCheckBox:
        return self.ui.checkBox_enableDci

    def get_value(self, attr: str) -> float:
        ctrl = self.ui.param_controls.get(attr)
        if ctrl is None:
            return 0.0
        return float(ctrl.value())

    def set_value(self, attr: str, value: float) -> None:
        ctrl = self.ui.param_controls.get(attr)
        if ctrl is None:
            return
        ctrl.blockSignals(True)
        try:
            if isinstance(ctrl, QSpinBox):
                ctrl.setValue(int(value))
            else:
                ctrl.setValue(float(value))  # QDoubleSpinBox
        finally:
            ctrl.blockSignals(False)

    def write_config(self, cfg) -> None:
        for attr, _obj, _fl in DCI_PARAM_SPECS:
            if attr in self.ui.param_controls:
                setattr(cfg, attr, self.get_value(attr))
        for attr, box_name in DCI_GROUP_ENABLE_MAP:
            box = self.ui.group_enables.get(box_name)
            if box is not None:
                setattr(cfg, attr, 1 if box.isChecked() else 0)
        # 保留曲线数组（自 _cfg 工作配置）
        for k in _CURVE_KEYS:
            setattr(cfg, _CF_COEF_ARR[k],
                    np.asarray(getattr(self._cfg, _CF_COEF_ARR[k]), dtype=np.uint16))
            setattr(cfg, _CF_WEIGHT_ARR[k],
                    np.asarray(getattr(self._cfg, _CF_WEIGHT_ARR[k]), dtype=np.uint16))

    def load_config_into_ui(self, cfg) -> None:
        for attr, _obj, _fl in DCI_PARAM_SPECS:
            if attr in self.ui.param_controls:
                self.set_value(attr, float(getattr(cfg, attr, 0)))
        for attr, box_name in DCI_GROUP_ENABLE_MAP:
            box = self.ui.group_enables.get(box_name)
            if box is not None:
                box.setChecked(bool(getattr(cfg, attr, False)))
        self._cfg = cfg
        self._refresh_curve_charts()

    def process_frame(self, src_frame: ImageFrame, io_info: dict) -> tuple:
        try:
            if not self.ui.checkBox_enableDci.isChecked():
                return True, src_frame
            input_fmt = src_frame.fmt
            input_clrspc = src_frame.clrspc
            output_fmt = int(io_info.get("out_fmt", input_fmt))
            output_clrspc = int(io_info.get("out_clrspc", input_clrspc))
            width = io_info.get("width") or src_frame.width
            height = io_info.get("height") or src_frame.height
            output_dir = io_info.get("output_dir") or tempfile.gettempdir()
            exe_path = _resolve_exe_path(self.ui.lineEdit_exe.text().strip())
            if not exe_path or not os.path.isfile(exe_path):
                return False, "DCI runner exe not found"
            input_tmp = os.path.join(
                output_dir, f"_dci_input_{width}x{height}_fmt{input_fmt:#x}.yuv")
            with open(input_tmp, "wb") as f:
                src_frame.pyr.tofile(f)
                src_frame.pug.tofile(f)
                src_frame.pvb.tofile(f)
            output_file = os.path.join(
                output_dir, f"dci_output_{width}x{height}_fmt{output_fmt:#x}.yuv")
            from config_def.module_config_dci import DciUserConfig
            local_cfg = os.path.join(output_dir, "_dci_config.json")
            cfg = DciUserConfig()
            try:
                if os.path.isfile(local_cfg):
                    cfg.load(local_cfg)
            except Exception:
                pass
            self.write_config(cfg)
            cfg.dump(local_cfg)
            cmd = [
                exe_path, "-i", input_tmp, "-w", str(width), "-g", str(height),
                "-f", f"{input_fmt:#x}", "-r", str(input_clrspc),
                "-F", f"{output_fmt:#x}", "-R", str(output_clrspc),
                "-o", output_file, "-c", local_cfg, "-m", "0",
            ]
            if self.ui.checkBox_dump.isChecked():
                cmd += ["--dump", "0xff"]
            result = subprocess.run(cmd, check=False, capture_output=True,
                                    text=True, timeout=120)
            if result.returncode != 0:
                return False, f"DCI runner failed: {result.stderr[:200]}"
            if not os.path.isfile(output_file):
                return False, "DCI output file not created"
            data, _ = read_raw_to_planar(output_file, width, height, output_fmt)
            dst = ImageFrame(data[0], data[1], data[2], output_fmt, output_clrspc)
            self._load_cf_result_curve()
            return True, dst
        except subprocess.TimeoutExpired:
            return False, "DCI runner timeout"
        except Exception as exc:
            return False, str(exc)

    # ------------------------------------------------------------------ #
    # Curve / weight charts                                              #
    # ------------------------------------------------------------------ #

    def _refresh_curve_charts(self) -> None:
        """Refresh both tabs from the working cfg + visibility toggles."""
        show = {k: self.ui.ckbox_showLow.isChecked() for k in ("low",)}
        show = {
            "low": self.ui.ckbox_showLow.isChecked(),
            "mid": self.ui.ckbox_showMid.isChecked(),
            "high": self.ui.ckbox_showHigh.isChecked(),
        }
        # tab_curve: cf_dciWgtCoef_* (33)
        coef_series = [
            (f"{k.capitalize()}", _CURVE_COLORS[k],
             np.asarray(getattr(self._cfg, _CF_COEF_ARR[k]), dtype=np.float64))
            for k in _CURVE_KEYS if show[k]
        ]
        if self.ui.ckbox_showCfRes.isChecked() and getattr(self, "_cf_res_curve", None) is not None:
            coef_series.append(("CF Result", _CURVE_COLORS["cfres"], self._cf_res_curve))
        self.ui.curve_chart.set_series(coef_series)
        # tab_weight: cf_dciWeight_* (32) + histogram
        weight_series = [
            (f"{k.capitalize()} W", _CURVE_COLORS[k],
             np.asarray(getattr(self._cfg, _CF_WEIGHT_ARR[k]), dtype=np.float64))
            for k in _CURVE_KEYS if show[k]
        ]
        self.ui.weight_chart.set_series(weight_series)
        hist = None
        if self._histogram_provider is not None:
            try:
                hist = self._histogram_provider()
            except Exception:
                hist = None
        self.ui.weight_chart.set_histogram(hist)

    def _load_cf_result_curve(self) -> None:
        """Read the CF result curve from the dump file, if present."""
        self._cf_res_curve = None
        dump_dir = self._output_dir_getter() or ""
        if not dump_dir:
            return
        try:
            from script.dci import draw_global_lut as dgl
            path = os.path.join(dump_dir, "dci_glb1_cf_lut_frm0.txt")
            if not os.path.isfile(path):
                return
            _lx, ly = dgl.parse_global_lut_file(path)
            if ly is not None:
                self._cf_res_curve = [float(v) for v in ly]
        except Exception:
            self._cf_res_curve = None
        self._refresh_curve_charts()

    def _on_show_toggled(self) -> None:
        self._refresh_curve_charts()
        self.paramsChanged.emit()

    def _on_clear(self, key: str) -> None:
        """Clear one Low/Mid/High curve; semantics depend on the active tab."""
        if self.ui.tabWidget.currentIndex() == 0:  # tab_curve -> y=x 斜线
            arr = getattr(self._cfg, _CF_COEF_ARR[key])
            n = len(arr)
            arr[:] = np.arange(n, dtype=arr.dtype)
        else:  # tab_weight -> 默认权重 1
            arr = getattr(self._cfg, _CF_WEIGHT_ARR[key])
            arr[:] = 1
        self._status_callback(f"Cleared {key} curve (tab: "
                              + ("Curves" if self.ui.tabWidget.currentIndex() == 0 else "Weights")
                              + ")")
        self._refresh_curve_charts()
        self.paramsChanged.emit()

    # ------------------------------------------------------------------ #
    # Config persistence (buttons)                                       #
    # ------------------------------------------------------------------ #

    def _on_save_config(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            None, "Save DCI Config As", "", "JSON Files (*.json)")
        if not path:
            return
        try:
            from config_def.module_config_dci import DciUserConfig
            cfg = DciUserConfig()
            self.write_config(cfg)
            cfg.dump(path)
            self._status_callback(f"DCI config saved to {path}")
        except Exception as exc:
            self._status_callback(f"DCI save config failed: {exc}")

    def _on_read_config(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            None, "Read DCI Config", "", "JSON Files (*.json)")
        if not path:
            return
        try:
            from config_def.module_config_dci import DciUserConfig
            cfg = DciUserConfig()
            if not cfg.load(path):
                self._status_callback(f"Failed to read DCI config: {path}")
                return
            self.load_config_into_ui(cfg)
            self._status_callback(f"DCI config read: {path}")
            self.paramsChanged.emit()
        except Exception as exc:
            self._status_callback(f"DCI read config failed: {exc}")

    def _on_browse_exe(self) -> None:
        current = self.ui.lineEdit_exe.text().strip()
        start = os.path.dirname(_resolve_exe_path(current)) if current else ""
        path, _ = QFileDialog.getOpenFileName(
            None, "Select DCI Exe", start or os.getcwd(),
            "Executable (*.exe);;All Files (*)")
        if path:
            self.ui.lineEdit_exe.setText(path)
            self.paramsChanged.emit()

    def _on_open_exe_dir(self) -> None:
        exe_path = _resolve_exe_path(self.ui.lineEdit_exe.text().strip())
        target = os.path.dirname(exe_path) if os.path.isfile(exe_path) else exe_path
        if target and os.path.isdir(target):
            try:
                os.startfile(target)
            except Exception:
                pass
        else:
            self._status_callback("DCI exe directory not found")

    # ------------------------------------------------------------------ #
    # Signals                                                            #
    # ------------------------------------------------------------------ #

    def _connect_signals(self) -> None:
        ui = self.ui
        ui.checkBox_enableDci.toggled.connect(self._on_param_changed)
        ui.lineEdit_exe.editingFinished.connect(self._on_param_changed)
        ui.comboBox_median.currentIndexChanged.connect(self._on_param_changed)
        ui.checkBox_dump.toggled.connect(self._on_param_changed)
        ui.btn_browseExe.clicked.connect(self._on_browse_exe)
        ui.btn_openDir.clicked.connect(self._on_open_exe_dir)
        ui.btn_saveConfig.clicked.connect(self._on_save_config)
        if hasattr(ui, "btn_readConfig"):
            ui.btn_readConfig.clicked.connect(self._on_read_config)
        for attr, ctrl in ui.param_controls.items():
            ctrl.valueChanged.connect(self._on_param_changed)
        for box in ui.group_enables.values():
            box.toggled.connect(self._on_param_changed)
        for cb in (ui.ckbox_showLow, ui.ckbox_showMid, ui.ckbox_showHigh,
                   ui.ckbox_showCfRes):
            cb.toggled.connect(self._on_show_toggled)
        ui.btn_clearLow.clicked.connect(lambda: self._on_clear("low"))
        ui.btn_clearMid.clicked.connect(lambda: self._on_clear("mid"))
        ui.btn_clearHigh.clicked.connect(lambda: self._on_clear("high"))

    def _on_param_changed(self, *_args) -> None:
        self.paramsChanged.emit()
