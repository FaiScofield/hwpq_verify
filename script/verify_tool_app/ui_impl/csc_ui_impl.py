"""
CSC (Colorspace Conversion + BCSH) tab controller — PySide6.

UI 定义在 ui/csc_ui.ui（Qt Designer），由 uic 生成 ui_gen/csc_ui.py
（Ui_CscUiWidget）；控制器保持与 PySimpleGUI 版 ui_csc.py 相同的语义
（忽略 "Sat/Hue Test" 部分）：
  - 顶层：Enable CSC 总开关 + Algo Type / Precision / Channel Swap + Reset/Save。
  - BCSH 参数表：Brightness/Contrast/Sat/Hue + RGB Gain/Offset（0..511，256 中性）
    每项 slider + spin + 归一化显示（随算法切换 remap RGB gain）。
  - 底部：CSC Coef Info（步骤1/2 系数与偏移，随最近一次运行更新）。
处理经 script/csc/run_csc.run_selected_algo 完成，符合链式宿主
``process_frame(frame, io_info)`` 契约；Enable 关闭时原帧直通。
"""

from collections.abc import Callable
import logging
import os

import numpy as np
from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtGui import QFontMetrics
from PySide6.QtWidgets import (
    QCheckBox, QFileDialog, QHeaderView, QMainWindow, QTableWidget,
    QTableWidgetItem, QWidget,
)

from script.csc import run_csc as _run_csc  # noqa: F401  (自插入 script/csc 到 sys.path)
from script.csc.csc_ui import (
    RGB_GAIN_KEYS, get_bcsh_norm_value, remap_rgb_gain_value_for_algo_switch,
)
from script.csc.run_csc import (
    CLRSPC_NAMES, CLRSPC_OPTIONS,
    _get_step_output_domains, build_bcsh_config_from_dict,
    get_default_bcsh_raw_values, get_pixel_depth, get_runtime_coef_precision,
    is_rgb_format, run_selected_algo,
)
from script.img_io import ImageFrame

try:
    from ..ui_gen.csc_ui import Ui_CscUiWidget
except ImportError:
    from ui_gen.csc_ui import Ui_CscUiWidget

try:
    from ..config_actions import (
        ask_reload, ask_save_mode, build_own_root, config_section_key,
        pick_save_as_path, write_config_section,
    )
except ImportError:
    from script.verify_tool_app.ui_impl.com_impl import (
        ask_reload, ask_save_mode, build_own_root, config_section_key,
        pick_save_as_path, write_config_section,
    )

logger = logging.getLogger(__name__)

# BCSH 参数键（与 ui/csc_ui.ui 中 slider_<key>/spin_<key>/norm_<key> 对应）
BCSH_KEYS = ("bright", "contrast", "sat", "hue",
             "r_gain", "r_offset", "g_gain", "g_offset", "b_gain", "b_offset")

# CscConfig 属性映射（保存配置用）
_CSC_UI_KEY_TO_ATTR = {
    "bright": "cscBrightness", "contrast": "cscContrast", "sat": "cscSaturation",
    "hue": "cscHue", "r_gain": "cscRGain", "r_offset": "cscROffset",
    "g_gain": "cscGGain", "g_offset": "cscGOffset",
    "b_gain": "cscBGain", "b_offset": "cscBOffset",
}

# 色彩空间码 -> CSC mode 字符串片段（如 4 -> "709L"），用于 "709L_to_RGBF" 显示。
_CLRSPC_MODE_TAGS = {
    0: "RGBL", 1: "RGBF",
    2: "601L", 3: "601F",
    4: "709L", 5: "709F",
    6: "2020L", 7: "2020F",
}


def build_csc_mode_display(input_clrspc: int, output_clrspc: int) -> str:
    """把输入/输出色彩空间码格式化为可读的基础 CSC mode（如 709L_to_RGBF）。"""
    in_tag = _CLRSPC_MODE_TAGS.get(int(input_clrspc))
    out_tag = _CLRSPC_MODE_TAGS.get(int(output_clrspc))
    if in_tag is None or out_tag is None:
        return "Unknown"
    return f"{in_tag}_to_{out_tag}"


class CscUiWidget(QWidget):
    """Reusable CSC configuration widget (loads ui_gen/csc_ui.Ui_CscUiWidget)."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Load the generated CSC UI and build the BCSH key->control maps."""
        super().__init__(parent)
        self.ui = Ui_CscUiWidget()
        self.ui.setupUi(self)
        self.ui.comboBox_precision.setCurrentText("10")
        # BCSH 键 -> 控件映射（BCSH_KEYS 与 .ui 中的命名一致）
        self.ui.sliders = {k: getattr(self.ui, f"slider_{k}") for k in BCSH_KEYS}
        self.ui.spins = {k: getattr(self.ui, f"spin_{k}") for k in BCSH_KEYS}
        self.ui.norms = {k: getattr(self.ui, f"norm_{k}") for k in BCSH_KEYS}
        self._lock_norm_label_widths()

    def _lock_norm_label_widths(self) -> None:
        """固定 norm_* 读数标签宽度，避免数值长度变化时抖动并推动网格列宽。

        归一化文本长度随数值变化（如 "2.00" / "-1.00" / "-180.00"），标签若按
        内容自适应，会在滑动 slider 时不断改变自身宽度、连带改变 bcshGrid 列宽。
        这里按"所有算法 x 取值极值"量取最宽文本，再对每个标签 setFixedWidth。
        """
        algos = [self.ui.comboBox_algoType.itemText(i)
                 for i in range(self.ui.comboBox_algoType.count())]
        metrics = QFontMetrics(self.ui.norms[BCSH_KEYS[0]].font())
        widest = 0
        for key in BCSH_KEYS:
            slider = self.ui.sliders[key]
            for algo in algos:
                # 取极值（含中性 256）：绝对值最大处文本最长
                for raw in (slider.minimum(), slider.maximum(), 256):
                    text = get_bcsh_norm_value(key, raw, algo)
                    widest = max(widest, metrics.horizontalAdvance(text))
        width = widest + 4   # 余量：不同字体 hinting 下避免裁字
        for key in BCSH_KEYS:
            self.ui.norms[key].setFixedWidth(width)


class CscUiController(QObject):
    """Controls the CSC tab: BCSH params + run_selected_algo chain stage."""

    paramsChanged = Signal()

    def __init__(
        self,
        csc_widget: CscUiWidget,
        parent_window: QMainWindow | None = None,
        status_callback: Callable[[str], None] | None = None,
        config_path_getter: Callable[[], str] | None = None,
    ) -> None:
        """Bind to a CscUiWidget and explicit host callbacks."""
        super().__init__(parent_window or csc_widget)
        self.widget = csc_widget
        self.ui = csc_widget.ui
        self._win = parent_window
        self._status_callback = status_callback or (lambda message: None)
        self._config_path_getter = config_path_getter or (lambda: "")
        self._prev_algo = self.get_algo_type()
        self._mid_output_locked = False
        self._last_input_clrspc = -1   # 进入 CSC 的帧色彩空间，未知时为 -1
        self._init_mid_output_controls()
        self._setup_coef_tables()
        self._sync_norms()
        self._connect_signals()

    # ------------------------------------------------------------------ #
    # Public helpers / module protocol                                   #
    # ------------------------------------------------------------------ #

    @property
    def enable_checkbox(self) -> QCheckBox:
        """模块总开关（流水线勾选联动对象）。"""
        return self.ui.checkBox_enableCsc

    def get_algo_type(self) -> str:
        """Return the currently selected algorithm type string."""
        return self.ui.comboBox_algoType.currentText()

    def get_params(self) -> dict:
        """Read BCSH raw params + algo/precision/channel-swap from the UI."""
        params: dict = {}
        for key in BCSH_KEYS:
            params[key] = int(self.ui.sliders[key].value())
        params["algo_type"] = self.get_algo_type()
        try:
            params["precision"] = int(self.ui.comboBox_precision.currentText())
        except ValueError:
            params["precision"] = 10
        params["channel_swap"] = self.ui.cmbox_channelSwap.currentText()
        params["enable"] = bool(self.ui.checkBox_enableCsc.isChecked())
        return params

    def process_frame(self, src_frame: ImageFrame, io_info: dict) -> tuple:
        """链式流水线适配：以 src_frame 为输入按当前 CSC/BCSH 参数处理。

        Enable 关闭 -> 原帧直通。输出格式/色彩空间取 Mid 输出行（末级时该行由
        宿主同步为 I/O 页输出），返回 (ok, dst_frame | 错误消息)，并更新底部
        Coef Info 与基础 mode 显示。
        """
        try:
            input_fmt = src_frame.fmt
            input_clrspc = src_frame.clrspc
            # Mid 输出行即本级的输出格式/色彩空间；CSC 为流水线末级时该行已被
            # 宿主禁用并同步为 I/O 页输出（见 set_mid_output_locked），故统一读该
            # 行，仅在选项未初始化时回退到 io_info 的目标输出。
            mid_fmt = self.get_mid_fmt_code()
            mid_clrspc = self.get_mid_clrspc()
            output_fmt = (int(io_info.get("out_fmt", input_fmt))
                          if mid_fmt is None else mid_fmt)
            output_clrspc = (int(io_info.get("out_clrspc", input_clrspc))
                             if mid_clrspc is None else mid_clrspc)
            # 基础 mode 显示跟随实际输入色彩空间。
            self._last_input_clrspc = input_clrspc
            self._update_base_type_info()
            if not self.ui.checkBox_enableCsc.isChecked():
                return True, src_frame
            params = self.get_params()
            pixel_depth = max(get_pixel_depth(input_fmt),
                              get_pixel_depth(output_fmt))
            algo_type = params["algo_type"]
            bcsh_config = build_bcsh_config_from_dict({
                "brightness": params["bright"],
                "contrast": params["contrast"],
                "saturation": params["sat"],
                "hue": params["hue"],
                "r_gain": params["r_gain"], "r_offset": params["r_offset"],
                "g_gain": params["g_gain"], "g_offset": params["g_offset"],
                "b_gain": params["b_gain"], "b_offset": params["b_offset"],
            }, algo_type)
            planar_in = np.stack([src_frame.pyr, src_frame.pug,
                                  src_frame.pvb], axis=0)
            output_data, s1c, s1o, s2c, s2o = run_selected_algo(
                planar_in, bcsh_config, pixel_depth, params["precision"],
                algo_type, input_clrspc, output_clrspc,
                input_fmt, output_fmt,
            )
            dst = ImageFrame(output_data[0], output_data[1], output_data[2],
                             output_fmt, output_clrspc)
            # 各步骤输入/输出域（决定矩阵行/列通道标签）。
            input_is_rgb = is_rgb_format(input_fmt)
            output_is_rgb = is_rgb_format(output_fmt)
            step1_out_rgb, step2_out_rgb = _get_step_output_domains(
                algo_type, input_is_rgb, output_is_rgb)
            if step1_out_rgb is None and s1c is not None:
                # RK_SW R2Y 特例：step1 是 RGB 域的对角 Gain 矩阵。
                step1_out_rgb = True
            if step2_out_rgb is None:
                step2_out_rgb = output_is_rgb
            step2_in_rgb = (step1_out_rgb if s1c is not None
                            else input_is_rgb)
            runtime_precision = get_runtime_coef_precision(
                algo_type, params["precision"])
            self._update_coef_info(
                s1c, s1o, input_is_rgb, bool(step1_out_rgb),
                runtime_precision)
            self._update_coef_info(
                s2c, s2o, bool(step2_in_rgb), bool(step2_out_rgb),
                runtime_precision, table_index=1)
            return True, dst
        except Exception as exc:
            logger.warning("CSC process failed: %s", exc)
            return False, str(exc)

    # ------------------------------------------------------------------ #
    # Mid output row (cmbox_midFmt / cmbox_midClrspc)                    #
    # ------------------------------------------------------------------ #
    #
    # 该行描述 CSC 作为流水线中间级时的输出格式/色彩空间：CSC 不是末级时由用户
    # 选择；CSC 是末级时被禁用并跟随 I/O 页的输出格式/色彩空间（宿主
    # test_app_pq 通过 set_mid_output_locked() 同步）。Mid Colorspace 选项随
    # Mid Format 的域（RGB / YUV）变化，显示格式与 I/O 页输入色彩空间一致。

    def _init_mid_output_controls(self) -> None:
        """初始化 Mid Colorspace 选项（Mid Format 选项固定在 .ui 中）。"""
        self._refresh_mid_clrspc_options(keep_current=False)

    def get_mid_fmt_code(self) -> int | None:
        """返回 Mid Format 的格式码；未选择时返回 None。"""
        text = self.ui.cmbox_midFmt.currentText()
        return int(text.split("-")[0], 16) if text else None

    def get_mid_clrspc(self) -> int | None:
        """返回 Mid Colorspace 的色彩空间码；未选择时返回 None。"""
        text = self.ui.cmbox_midClrspc.currentText()
        return int(text.split("-")[0]) if text else None

    @staticmethod
    def _find_clrspc_item(combo, code: int) -> str:
        """在 combo 中按色彩空间码查找显示项文本（找不到返回空串）。"""
        for i in range(combo.count()):
            try:
                if int(combo.itemText(i).split("-")[0].strip()) == code:
                    return combo.itemText(i)
            except ValueError:
                continue
        return ""

    def _refresh_mid_clrspc_options(self, keep_current: bool = True) -> None:
        """按 Mid Format 的域重建 Mid Colorspace 选项。

        RGB 格式 -> {RGB_Limited, RGB_Full}（0/1）；YUV 格式 -> BT601/709/2020
        x L/F（2..7）。当前值仍合法时保留，否则落到该域默认全量程
        （RGB->1 RGB_Full，YUV->5 BT709_Full）。
        """
        ui = self.ui
        fmt_code = self.get_mid_fmt_code()
        is_rgb = is_rgb_format(fmt_code) if fmt_code is not None else True
        clrspc_display = [f"{clr}-{CLRSPC_NAMES[clr]}" for clr in CLRSPC_OPTIONS]
        items = ([item for item in clrspc_display
                  if int(item.split("-")[0]) in (0, 1)] if is_rgb else
                 [item for item in clrspc_display
                  if int(item.split("-")[0]) in range(2, 8)])
        if not items:
            return
        current = ui.cmbox_midClrspc.currentText()
        ui.cmbox_midClrspc.blockSignals(True)
        ui.cmbox_midClrspc.clear()
        ui.cmbox_midClrspc.addItems(items)
        if keep_current and current in items:
            ui.cmbox_midClrspc.setCurrentText(current)
        else:
            default = 1 if is_rgb else 5
            ui.cmbox_midClrspc.setCurrentText(
                self._find_clrspc_item(ui.cmbox_midClrspc, default) or items[0])
        ui.cmbox_midClrspc.blockSignals(False)

    def _select_mid_fmt(self, fmt_code: int | None) -> None:
        """在 Mid Format 中选中与给定格式码最匹配的项（先同码，再同域同深度）。

        Mid Format 选项（.ui）只覆盖常见的平面 RGB/YUV444 格式，I/O 页输出可能
        是其它格式（如 NV12），此时退化为同域、同深度的首个选项。
        """
        combo = self.ui.cmbox_midFmt
        if fmt_code is None or combo.count() == 0:
            return
        item = next((combo.itemText(i) for i in range(combo.count())
                     if combo.itemText(i).startswith(f"0x{fmt_code:x}-")), "")
        if not item:
            want_rgb = is_rgb_format(fmt_code)
            want_10bit = get_pixel_depth(fmt_code) >= 10
            same_domain = [combo.itemText(i) for i in range(combo.count())
                           if is_rgb_format(int(combo.itemText(i).split("-")[0], 16))
                           == want_rgb]
            same_depth = [text for text in same_domain
                          if (get_pixel_depth(int(text.split("-")[0], 16)) >= 10)
                          == want_10bit]
            item = (same_depth or same_domain or [combo.itemText(0)])[0]
        combo.blockSignals(True)
        combo.setCurrentText(item)
        combo.blockSignals(False)

    def _select_mid_clrspc(self, clrspc: int | None) -> None:
        """在 Mid Colorspace 中选中给定色彩空间码（不存在则保持原值）。"""
        combo = self.ui.cmbox_midClrspc
        if clrspc is None:
            return
        item = self._find_clrspc_item(combo, clrspc)
        if not item:
            return
        combo.blockSignals(True)
        combo.setCurrentText(item)
        combo.blockSignals(False)

    def set_mid_output_locked(
        self, locked: bool, out_fmt: int | None = None,
        out_clrspc: int | None = None,
    ) -> None:
        """设置 Mid 输出行状态（宿主按 CSC 是否为流水线末级调用）。

        locked=True（CSC 为末级）：禁用两个下拉，并把值同步为 I/O 页的输出
        格式/色彩空间；locked=False（CSC 非末级）：使能该行，由用户选择中间输出。
        """
        self._mid_output_locked = bool(locked)
        if locked:
            self._select_mid_fmt(out_fmt)
            self._refresh_mid_clrspc_options(keep_current=False)
            self._select_mid_clrspc(out_clrspc)
        self.ui.cmbox_midFmt.setEnabled(not locked)
        self.ui.cmbox_midClrspc.setEnabled(not locked)
        self._update_base_type_info()

    def _on_mid_fmt_changed(self, *_args) -> None:
        """Mid Format 变化：按新的域重建 Mid Colorspace 选项并重跑链。"""
        self._refresh_mid_clrspc_options()
        self._update_base_type_info()
        self.paramsChanged.emit()

    def _on_mid_clrspc_changed(self, *_args) -> None:
        """Mid Colorspace 变化：刷新基础 mode 显示并重跑链。"""
        self._update_base_type_info()
        self.paramsChanged.emit()

    def get_base_type_str(self) -> str:
        """返回基础 CSC mode 字符串（进入 CSC 的输入色彩空间 -> Mid 输出色彩空间）。"""
        in_clrspc = self._last_input_clrspc
        out_clrspc = self.get_mid_clrspc()
        if in_clrspc < 0 or out_clrspc is None:
            return "Unknown"
        return build_csc_mode_display(in_clrspc, out_clrspc)

    def _update_base_type_info(self) -> None:
        """刷新 label_baseTypeInfo：显示基础 CSC mode（如 709L_to_RGBF）。"""
        self.ui.label_baseTypeInfo.setText(
            f"CSC Base Type: {self.get_base_type_str()}")

    # ------------------------------------------------------------------ #
    # Coef tables (table_coefStep1 / table_coefStep2)                    #
    # ------------------------------------------------------------------ #
    #
    # 每个表格以矩阵方程形式显示一步 CSC：
    #     [out] = [m00 m01 m02] * [in] + [v]
    # 每个表格分两段：Fixed Coef（定点整数）与 Floating Coef（/= 2^precision），
    # 行/列通道标签按该步骤实际输入/输出域（RGB -> R/G/B，YUV -> Y/U/V）。

    _COEF_TABLES = ("table_coefStep1", "table_coefStep2")

    def _setup_coef_tables(self) -> None:
        """配置两个系数表格：9 行（两段 x 3 行 + 段标题/分隔），9 列。"""
        for name in self._COEF_TABLES:
            table: QTableWidget = getattr(self.ui, name)
            table.setColumnCount(9)
            table.setRowCount(9)
            table.setHorizontalHeaderLabels([""] * 9)
            table.verticalHeader().setVisible(False)
            table.horizontalHeader().setVisible(False)
            table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
            header = table.horizontalHeader()
            for col in range(9):
                header.setSectionResizeMode(
                    col, QHeaderView.ResizeMode.ResizeToContents)
            self._clear_coef_table(table)

    def _clear_coef_table(self, table: QTableWidget) -> None:
        """把一个系数表格填为占位文本。"""
        self._fill_coef_table(table, None, None, True, True, 0)

    def _update_coef_info(
        self, mat, offset, in_is_rgb: bool, out_is_rgb: bool,
        precision: int, table_index: int = 0,
    ) -> None:
        """把一步 CSC 的系数/偏移写入 table_coefStep1/2。"""
        table: QTableWidget = getattr(self.ui, self._COEF_TABLES[table_index])
        self._fill_coef_table(table, mat, offset, in_is_rgb, out_is_rgb,
                              precision)

    def _fill_coef_table(
        self, table: QTableWidget, mat, offset,
        in_is_rgb: bool, out_is_rgb: bool, precision: int,
    ) -> None:
        """填充单个表格：Fixed 段（3 行）+ 空行 + Floating 段（3 行）。"""
        table.clearContents()
        # clearContents() 不会移除 span：上一轮 N/A 占位设的 3x9 合并单元格会残留，
        # 使随后写入的真实系数单元格被 span 遮住（整表看起来空的），故先重置 span。
        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                if table.rowSpan(row, col) > 1 or table.columnSpan(row, col) > 1:
                    table.setSpan(row, col, 1, 1)
        out_labels = ("R", "G", "B") if out_is_rgb else ("Y", "U", "V")
        in_labels = ("R", "G", "B") if in_is_rgb else ("Y", "U", "V")
        scale = 1 << precision if precision > 0 else 1.0
        has_data = mat is not None and offset is not None

        def _set(row, col, text, bold=False):
            item = QTableWidgetItem(text)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if bold:
                font = item.font()
                font.setBold(True)
                item.setFont(font)
            table.setItem(row, col, item)

        def _coef_text(value, is_fixed: bool) -> str:
            try:
                v = float(value)
            except (TypeError, ValueError):
                return "N/A"
            if is_fixed and isinstance(value, (int, np.integer)):
                return str(int(v))
            if precision > 0:
                return f"{v / scale:.4f}"
            return f"{v:.4f}"

        def _draw_block(start_row: int, title: str, is_fixed: bool) -> None:
            _set(start_row, 0, title, bold=True)
            table.setSpan(start_row, 0, 1, 9)
            if not has_data:
                _set(start_row + 1, 0, "N/A")
                table.setSpan(start_row + 1, 0, 3, 9)
                return
            for i in range(3):
                row = start_row + 1 + i
                m = mat[i]
                _set(row, 0, out_labels[i], bold=True)
                _set(row, 1, "=")
                for j in range(3):
                    _set(row, 2 + j, _coef_text(m[j], is_fixed))
                _set(row, 5, "*")
                _set(row, 6, in_labels[i], bold=True)
                _set(row, 7, "+")
                _set(row, 8, _coef_text(offset[i], is_fixed))

        _draw_block(0, "Fixed Coef", is_fixed=True)
        # 第 4 行作为两段之间的空白分隔。
        _draw_block(5, "Floating Coef", is_fixed=False)

    def _sync_norms(self) -> None:
        """Refresh all normalized BCSH display labels for the current algo."""
        algo_type = self.get_algo_type()
        for key in BCSH_KEYS:
            norm_val = get_bcsh_norm_value(
                key, int(self.ui.sliders[key].value()), algo_type)
            self.ui.norms[key].setText(norm_val)


    # ------------------------------------------------------------------ #
    # Signal wiring / handlers                                           #
    # ------------------------------------------------------------------ #

    def _connect_signals(self) -> None:
        ui = self.ui
        ui.checkBox_enableCsc.toggled.connect(self._on_param_changed)
        ui.comboBox_precision.currentIndexChanged.connect(self._on_param_changed)
        ui.cmbox_channelSwap.currentIndexChanged.connect(self._on_param_changed)
        ui.comboBox_algoType.currentIndexChanged.connect(self._on_algo_changed)
        ui.cmbox_midFmt.currentIndexChanged.connect(self._on_mid_fmt_changed)
        ui.cmbox_midClrspc.currentIndexChanged.connect(self._on_mid_clrspc_changed)
        for key in BCSH_KEYS:
            ui.sliders[key].valueChanged.connect(
                lambda _v, k=key: self._on_slider_changed(k))
            ui.spins[key].valueChanged.connect(
                lambda v, k=key: self._on_spin_changed(k, v))
        ui.btn_resetBcsh.clicked.connect(self._on_reset)
        ui.btn_saveCfg.clicked.connect(self._on_save_config)
        ui.btn_readCfg.clicked.connect(self._on_read_config)

    def _on_slider_changed(self, key: str) -> None:
        """Slider -> spin + norm sync."""
        value = int(self.ui.sliders[key].value())
        spin = self.ui.spins[key]
        if spin.value() != value:
            spin.blockSignals(True)
            spin.setValue(value)
            spin.blockSignals(False)
        self._sync_norms()
        self.paramsChanged.emit()

    def _on_spin_changed(self, key: str, value: int) -> None:
        """Spin -> slider + norm sync."""
        slider = self.ui.sliders[key]
        if slider.value() != value:
            slider.blockSignals(True)
            slider.setValue(value)
            slider.blockSignals(False)
        self._sync_norms()
        self.paramsChanged.emit()

    def _on_algo_changed(self, *_args) -> None:
        """Algo switch: remap RGB gains between RK/eVideo families, refresh norms."""
        ui = self.ui
        new_algo = self.get_algo_type()
        old_algo = self._prev_algo
        if new_algo != old_algo:
            for gain_key in RGB_GAIN_KEYS:
                slider = ui.sliders[gain_key]
                remapped = remap_rgb_gain_value_for_algo_switch(
                    int(slider.value()), old_algo, new_algo)
                spin = ui.spins[gain_key]
                slider.blockSignals(True)
                spin.blockSignals(True)
                slider.setValue(remapped)
                spin.setValue(remapped)
                slider.blockSignals(False)
                spin.blockSignals(False)
        self._prev_algo = new_algo
        self._sync_norms()
        self.paramsChanged.emit()

    def _on_reset(self) -> None:
        """Reset all BCSH params to the current algorithm's defaults."""
        defaults = get_default_bcsh_raw_values(self.get_algo_type())
        key_map = {
            "brightness": "bright", "contrast": "contrast",
            "saturation": "sat", "hue": "hue",
            "r_gain": "r_gain", "r_offset": "r_offset",
            "g_gain": "g_gain", "g_offset": "g_offset",
            "b_gain": "b_gain", "b_offset": "b_offset",
        }
        for config_key, ui_key in key_map.items():
            default_val = int(defaults.get(config_key, 256))
            self.ui.sliders[ui_key].blockSignals(True)
            self.ui.spins[ui_key].blockSignals(True)
            self.ui.sliders[ui_key].setValue(default_val)
            self.ui.spins[ui_key].setValue(default_val)
            self.ui.sliders[ui_key].blockSignals(False)
            self.ui.spins[ui_key].blockSignals(False)
        self._sync_norms()
        self._status_callback(f"CSC BCSH reset to {self.get_algo_type()} defaults")
        self.paramsChanged.emit()

    def _dump_config_to(self, path: str) -> None:
        """Write the current CSC/BCSH UI params to ``path`` as a full config file."""
        from config_def.module_config_csc import CscConfig
        cfg = CscConfig()
        for ui_key, attr in _CSC_UI_KEY_TO_ATTR.items():
            setattr(cfg, attr, int(self.ui.sliders[ui_key].value()))
        import script.csc.get_csc_coefs as csc_core
        for index, key in enumerate(csc_core.g_supported_standard_convert_modes.keys()):
            if csc_core.g_supported_standard_convert_modes[key] == self.get_algo_type():
                cfg.cscConvertMode = index
                break
        try:
            cfg.cscCoefPrecision = int(self.ui.comboBox_precision.currentText())
        except ValueError:
            cfg.cscCoefPrecision = 10
        cfg.update_csc_coefs()
        cfg.dump(path)

    def _on_save_config(self) -> None:
        """Save CSC config: Yes=直接更新 I/O Config File / No=另存 / Cancel=取消。"""
        mode = ask_save_mode("CSC")
        if mode == "cancel":
            return
        if mode == "overwrite":
            target = self._config_path_getter()
            if not target:
                self._status_callback("I/O page has no config file path set")
                return
        else:
            target = pick_save_as_path(
                self._config_path_getter(), "Save CSC Config As")
            if not target:
                return
        own_root = build_own_root(self._dump_config_to)
        if own_root is None:
            self._status_callback("CSC save config failed")
            return
        if write_config_section(own_root, config_section_key("CSC"), target):
            self._status_callback(f"CSC config saved to {target}")
        else:
            self._status_callback(f"CSC save config failed: {target}")

    def _on_read_config(self) -> None:
        """Reload the CSC config from the I/O Config File and apply to the UI."""
        if not ask_reload("CSC"):
            return
        path = self._config_path_getter()
        if not path or not os.path.isfile(path):
            self._status_callback(f"No config file to reload: {path}")
            return
        try:
            from config_def.module_config_csc import CscConfig
            cfg = CscConfig()
            if not cfg.load(path):
                self._status_callback(f"Failed to read CSC config: {path}")
                return
            ui = self.ui
            # 先写 BCSH 原始值（屏蔽信号，避免被算法 remap 干扰）
            for w in (ui.sliders, ui.spins):
                for key in BCSH_KEYS:
                    w[key].blockSignals(True)
            attr_map = {
                "bright": "cscBrightness", "contrast": "cscContrast",
                "sat": "cscSaturation", "hue": "cscHue",
                "r_gain": "cscRGain", "r_offset": "cscROffset",
                "g_gain": "cscGGain", "g_offset": "cscGOffset",
                "b_gain": "cscBGain", "b_offset": "cscBOffset",
            }
            for key, attr in attr_map.items():
                val = int(getattr(cfg, attr, 256))
                ui.sliders[key].setValue(val)
                ui.spins[key].setValue(val)
            for w in (ui.sliders, ui.spins):
                for key in BCSH_KEYS:
                    w[key].blockSignals(False)
            # 算法/精度
            import script.csc.get_csc_coefs as csc_core
            algo = csc_core.g_supported_standard_convert_modes.get(
                int(getattr(cfg, "cscConvertMode", 0)), self.get_algo_type())
            ui.comboBox_algoType.setCurrentText(algo)
            try:
                ui.comboBox_precision.setCurrentText(
                    str(int(getattr(cfg, "cscCoefPrecision", 10))))
            except Exception:
                pass
            self._prev_algo = self.get_algo_type()
            self._update_base_type_info()
            self._sync_norms()
            self._status_callback(f"CSC config reloaded: {path}")
            self.paramsChanged.emit()
        except Exception as exc:
            logger.warning("CSC read config failed: %s", exc)
            self._status_callback(f"CSC read config failed: {exc}")

    def _on_param_changed(self, *_args) -> None:
        """Emit params-changed (host decides rerun)."""
        self.paramsChanged.emit()
