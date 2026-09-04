"""
PQ Verify Tool (PySide6 pilot) — 链式流水线宿主窗口。
"""

import logging
import os
import subprocess
import sys
import time

PQ_APP_VERSION = "v0.1"
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# verify_tool_app 的父目录是 script/；config_def、csc 等以顶层包方式导入
# （config_def/__init__.py 使用 `from config_def...`），故 script 目录需入 path。
SCRIPT_DIR = os.path.dirname(CURRENT_DIR)
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

for _path in (PROJECT_ROOT, SCRIPT_DIR):
    if _path not in sys.path:
        sys.path.insert(0, _path)

# 默认日志文件（Help -> App Log 菜单直接打开它）。
DEFAULT_LOG_FILE = os.path.join(PROJECT_ROOT, "output", "pq_verify_tool.log")


def _git_short_hash() -> str:
    """Return the repository HEAD short hash (or 'unknown')."""
    try:
        result = subprocess.run(
            ["git", "-C", PROJECT_ROOT, "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5)
        return result.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def _build_date_str() -> str:
    """Return the source-file modification time as the build date."""
    try:
        import datetime
        stamp = os.path.getmtime(os.path.abspath(__file__))
        return datetime.datetime.fromtimestamp(stamp).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return "unknown"


GIT_SHORT_HASH = _git_short_hash()
BUILD_DATE = _build_date_str()

# 复用 script/utils.py 的 setup_logger（不再自定义 _setup_logging）：
# utils 顶部 basicConfig 已给 root 配好控制台 handler（g_plain_formatter 格式），
# 这里把 root level 置为 INFO 并挂上默认日志文件；各模块 logger propagate 到 root。
from script.utils import setup_logger

setup_logger(name=None, output=DEFAULT_LOG_FILE, loglevel="DEBUG")


logger = logging.getLogger(__name__)


def _ensure_generated_ui_modules():
    """Regenerate ui_gen modules when they are missing or older than the source .ui files."""
    ui_pairs = (
        ("ui\\app_mainwindow.ui", "ui_gen\\app_mainwindow.py"),
        ("ui\\preview_ui.ui", "ui_gen\\preview_ui.py"),
        ("ui\\io_ui.ui", "ui_gen\\io_ui.py"),
        ("ui\\acm_ui.ui", "ui_gen\\acm_ui.py"),
        ("ui\\bcsh_ui.ui", "ui_gen\\bcsh_ui.py"),
        ("ui\\shp_ui.ui", "ui_gen\\shp_ui.py"),
        ("ui\\csc_ui.ui", "ui_gen\\csc_ui.py"),
        ("ui\\dci_ui.ui", "ui_gen\\dci_ui.py"),
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

    logger.info("run auto uic to generate ui_gen modules...")
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

from PySide6.QtCore import QSignalBlocker, Qt, QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QScrollArea, QVBoxLayout, QWidget

from script.img_io import ImageFrame

if __package__:
    from .ui_impl.io_ui_impl import IoUiController, IoUiWidget
    from .ui_impl.csc_ui_impl import CscUiController, CscUiWidget
    from .ui_impl.bcsh_ui_impl import HsvUiController, HsvUiWidget
    from .ui_impl.acm_ui_impl import AcmUiController, AcmUiWidget
    from .ui_impl.dci_ui_impl import DciUiController, DciUiWidget
    from .ui_impl.shp_ui_impl import ShpUiController, ShpUiWidget
    from .ui_impl.preview_ui_impl import PreviewUiController, PreviewUiWidget
    from .ui_gen.app_mainwindow import Ui_TestAppWindow
else:
    from ui_impl.io_ui_impl import IoUiController, IoUiWidget
    from ui_impl.csc_ui_impl import CscUiController, CscUiWidget
    from ui_impl.bcsh_ui_impl import HsvUiController, HsvUiWidget
    from ui_impl.acm_ui_impl import AcmUiController, AcmUiWidget
    from ui_impl.dci_ui_impl import DciUiController, DciUiWidget
    from ui_impl.shp_ui_impl import ShpUiController, ShpUiWidget
    from script.verify_tool_app.ui_impl.preview_ui_impl import PreviewUiController, PreviewUiWidget
    from ui_gen.app_mainwindow import Ui_TestAppWindow


class PqVerifyAppWindow(QMainWindow):
    """Main window host that composes the I/O tab, pipeline stages and preview."""

    def __init__(self):
        super().__init__()
        self.ui = Ui_TestAppWindow()
        self.ui.setupUi(self)
        self.setWindowTitle(f"PQ Verify Tool {PQ_APP_VERSION}")
        # tab 顺序：I/O, CSC, BCSH, ACM, DCI, SHP。
        self.ui.tabWidget_main.setTabText(
            self.ui.tabWidget_main.indexOf(self.ui.tab_io_host), "I/O")
        self.ui.tabWidget_main.setTabText(
            self.ui.tabWidget_main.indexOf(self.ui.tab_module_host), "SHP")
        self._syncing_preview_action = False
        self._latest_chain_frame: ImageFrame | None = None

        self.io_widget = IoUiWidget(self)
        self.csc_widget = CscUiWidget(self)
        self.bcsh_widget = HsvUiWidget(self)
        self.acm_widget = AcmUiWidget(self)
        self.dci_widget = DciUiWidget(self)
        self.shp_widget = ShpUiWidget(self)
        self.preview_widget = PreviewUiWidget(self)

        # SHP 复用 module_host tab（末尾）；CSC/BCSH/ACM/DCI 新建 tab 依次插入。
        self._mount_host_page(self.ui.tab_io_host, self.io_widget, use_scroll_area=True)
        self._mount_host_page(self.ui.tab_module_host, self.shp_widget, use_scroll_area=True)
        self._insert_module_tab("CSC", self.csc_widget, index=1)
        self._insert_module_tab("BCSH", self.bcsh_widget, index=2)
        self._insert_module_tab("ACM", self.acm_widget, index=3)
        self._insert_module_tab("DCI", self.dci_widget, index=4)

        self.preview_ctrl = PreviewUiController(
            self.preview_widget,
            parent_window=self,
            status_callback=self.ui.statusbar.showMessage,
            pixel_readout_provider=self._pixel_readout,
        )
        self.io_ctrl = IoUiController(
            self.io_widget,
            parent_window=self,
            on_input_loaded=self._on_input_loaded,
            on_load_config=lambda path: self.acm_ctrl.load_current_config(path),
            on_output_changed=self._on_output_config_changed,
            status_callback=self.ui.statusbar.showMessage,
            auto_load_defaults=False,
        )
        self.preview_ctrl.set_output_dir_getter(self.io_ctrl.get_output_dir)
        # 链式宿主：模块不再自行处理/展示预览，交由宿主按 pipeline 顺序串行
        # process_frame。BCSH/ACM 仍注入 input_provider/work_size_provider 让其
        # UI 联动与防抖逻辑正常，但其内部 _do_auto_run 与宿主整链重跑冲突，
        # 故在下方断开其防抖定时器并改由宿主接管（编辑 -> 整链重跑）。
        self.csc_ctrl = CscUiController(
            self.csc_widget,
            parent_window=self,
            status_callback=self.ui.statusbar.showMessage,
            config_path_getter=self.io_ctrl.get_config_path,
        )
        self.bcsh_ctrl = HsvUiController(
            self.bcsh_widget,
            parent_window=self,
            input_provider=lambda: self.preview_ctrl.input_frame,
            output_callback=lambda frame: None,
            status_callback=self.ui.statusbar.showMessage,
            work_size_provider=self.preview_ctrl.get_work_size,
            output_fmt_provider=self.io_ctrl.get_output_fmt_code,
            output_clrspc_provider=self.io_ctrl.get_output_clrspc,
        )
        self.acm_ctrl = AcmUiController(
            self.acm_widget,
            parent_window=self,
            input_provider=lambda: self.preview_ctrl.input_frame,
            output_callback=lambda frame: None,
            status_callback=self.ui.statusbar.showMessage,
            config_path_getter=self.io_ctrl.get_config_path,
            config_path_setter=self.io_ctrl.set_config_path,
            work_size_provider=self.preview_ctrl.get_work_size,
            output_fmt_provider=self.io_ctrl.get_output_fmt_code,
            output_clrspc_provider=self.io_ctrl.get_output_clrspc,
        )
        self.dci_ctrl = DciUiController(
            self.dci_widget,
            parent_window=self,
            status_callback=self.ui.statusbar.showMessage,
            config_path_getter=self.io_ctrl.get_config_path,
            output_dir_getter=self.io_ctrl.get_output_dir,
            histogram_provider=self._dci_histogram,
        )
        self.shp_ctrl = ShpUiController(
            self.shp_widget,
            parent_window=self,
            status_callback=self.ui.statusbar.showMessage,
            config_path_getter=self.io_ctrl.get_config_path,
        )
        self.preview_ctrl.set_full_res_output_provider(lambda: self._latest_chain_frame)

        # 串行链级注册表 + 各模块 "Enable xxx" 总开关（与 pipeline 勾选联动）。
        self._stage_controllers: dict = {
            "csc": self.csc_ctrl, "bcsh": self.bcsh_ctrl,
            "acm": self.acm_ctrl, "dci": self.dci_ctrl, "shp": self.shp_ctrl,
        }
        self._stage_labels = {"csc": "CSC", "bcsh": "BCSH", "acm": "ACM",
                              "dci": "DCI", "shp": "SHP"}
        self._stage_enable_boxes = {
            "csc": self.csc_ctrl.ui.checkBox_enableCsc,
            "bcsh": self.bcsh_ctrl.ui.checkBox_enableHsvAdj,
            "acm": self.acm_ctrl.ui.checkBox_enable_acm,
            "dci": self.dci_ctrl.ui.checkBox_enableDci,
            "shp": self.shp_ctrl.ui.checkBox_enableShp,
        }
        # pipeline 勾选默认全不选中 -> 各模块 Enable 总开关也置为未勾选。
        for tag, box in self._stage_enable_boxes.items():
            box.setChecked(False)
            box.toggled.connect(
                lambda checked, t=tag: self._on_module_enable_changed(t, checked))
        self.io_ctrl.configure_pipeline(
            [("csc", "CSC"), ("bcsh", "BCSH"), ("acm", "ACM"),
             ("dci", "DCI"), ("shp", "SHP")])
        self.io_ctrl.set_pipeline_visible(True)
        self.io_ctrl.set_pipeline_changed_callback(self._on_pipeline_changed)

        self._init_auto_run_timer()
        self._install_view_menu()
        self._install_help_actions()
        self.preview_ctrl.preview_dock.visibilityChanged.connect(
            self._on_preview_dock_visibility_changed)
        # 接管 BCSH/ACM 内部防抖定时器：其 UI 编辑触发的自动运行改由宿主整链
        # 重跑（断开其 _do_auto_run，改连 _schedule_chain_run）。
        for ctrl in (self.bcsh_ctrl, self.acm_ctrl):
            ctrl.auto_run_timer.timeout.disconnect()
            ctrl.auto_run_timer.timeout.connect(self._schedule_chain_run)
        # 模块参数/使能变化：防抖整链自动重跑（状态栏显示 Running 进度）。
        for ctrl in (self.csc_ctrl, self.dci_ctrl, self.shp_ctrl):
            ctrl.paramsChanged.connect(self._on_params_changed)
        self.io_ctrl.auto_load_defaults()
        self.ui.tabWidget_main.setCurrentIndex(0)
        self.ui.statusbar.showMessage("Ready")

    # ------------------------------------------------------------------ #
    # Chain orchestration                                                #
    # ------------------------------------------------------------------ #

    def _run_chain(self) -> None:
        """Run the enabled pipeline stages serially over the current input frame.

        前一模块的输出作为下一模块的输入（串行数据链）；顺序与启用集合由
        I/O 页 groupBox_pipeline 控制（io_ctrl.get_pipeline_enabled()）。
        状态栏显示正在运行的模块（如 "Running BCSH... 1/3"）。
        """
        src = self.preview_ctrl.input_frame
        if src is None:
            self.ui.statusbar.showMessage("No input loaded")
            return
        start_time = time.perf_counter()
        io_info = {
            "out_fmt": self.io_ctrl.get_output_fmt_code(),
            "out_clrspc": self.io_ctrl.get_output_clrspc(),
            "output_dir": self.io_ctrl.get_output_dir(),
            "width": src.width,
            "height": src.height,
        }
        tags = self.io_ctrl.get_pipeline_enabled()
        if not tags:
            # 无启用模块：输入直通为最终输出。
            self._latest_chain_frame = src
            self.preview_ctrl.set_output_image(src)
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            self.ui.statusbar.showMessage(
                f"No pipeline stage enabled - pass-through ({elapsed_ms:.1f} ms)")
            return
        current = src
        total = len(tags)
        for index, tag in enumerate(tags, start=1):
            stage = self._stage_controllers[tag]
            label = self._stage_labels.get(tag, tag)
            self.ui.statusbar.showMessage(f"Running {label}... {index}/{total}")
            ok, result = stage.process_frame(current, io_info)
            if not ok:
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                self.ui.statusbar.showMessage(
                    f"{label} failed: {result} ({elapsed_ms:.1f} ms)")
                return
            current = result
        self._latest_chain_frame = current
        self.preview_ctrl.set_output_image(current)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        self.ui.statusbar.showMessage(
            f"Pipeline finished ({total} stage{'s' if total > 1 else ''}) in {elapsed_ms:.1f} ms")

    def _on_params_changed(self) -> None:
        """Module params changed: re-run the whole chain (debounced)."""
        self.ui.statusbar.showMessage("Params changed - re-running pipeline...")
        self._schedule_chain_run()

    def _on_output_config_changed(self) -> None:
        """Output format/colorspace changed: re-run the chain (debounced)."""
        self._schedule_chain_run()

    def _init_auto_run_timer(self) -> None:
        """Create the debounced chain re-run timer used by automatic re-runs.

        所有参数/输入/输出/pipeline 变化都经 _schedule_chain_run() 触发该
        300ms 单发定时器 -> _run_chain()，无需手动 Run 入口。
        """
        self.auto_run_timer = QTimer(self)
        self.auto_run_timer.setSingleShot(True)
        self.auto_run_timer.timeout.connect(self._run_chain)

    # ------------------------------------------------------------------ #
    # Preview readout & view menu (reused from the PySide6 test apps)    #
    # ------------------------------------------------------------------ #

    def _pixel_readout(self, x_pos: int, y_pos: int, role: str) -> str:
        """Show the native pixel value of the input / chain-output frame."""
        if role == "input":
            frame = self.preview_ctrl.input_frame
        else:
            frame = self._latest_chain_frame
        if frame is None:
            return ""
        try:
            tag = "RGB" if frame.is_rgb else "YUV"
            return "{}({}, {}, {})".format(
                tag, int(frame.pyr[y_pos, x_pos]),
                int(frame.pug[y_pos, x_pos]), int(frame.pvb[y_pos, x_pos]))
        except (IndexError, TypeError):
            return ""

    def _dci_histogram(self):
        """Compute the input Y-plane histogram for the DCI weight tab (or None)."""
        frame = self.preview_ctrl.input_frame
        if frame is None:
            return None
        try:
            import numpy as np
            plane = frame.pyr.ravel()
            depth = 1024 if frame.depth >= 10 else 256
            hist, _ = np.histogram(plane, bins=64, range=(0, depth))
            return hist.astype(np.float64)
        except Exception:
            return None

    def _install_view_menu(self) -> None:
        """Wire the Preview action to toggle the preview dock visibility."""
        self.ui.actionPreview.toggled.connect(self._on_preview_action_toggled)

    def _install_help_actions(self) -> None:
        """Wire the Help-menu actions (About / App Log)."""
        if hasattr(self.ui, "actionAbout_This_App"):
            self.ui.actionAbout_This_App.triggered.connect(self._on_about)
        if hasattr(self.ui, "actionAPP_LOG"):
            self.ui.actionAPP_LOG.triggered.connect(self._on_open_log)

    def _on_about(self) -> None:
        """Show the About dialog (version / git hash / build date)."""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.about(
            self, "About PQ Verify Tool",
            f"<b>PQ Verify Tool</b> {PQ_APP_VERSION}<br/><br/>"
            f"Git commit: {GIT_SHORT_HASH}<br/>"
            f"Compiled date: {BUILD_DATE}")

    def _on_open_log(self) -> None:
        """Open the default log file with the system handler."""
        if os.path.isfile(DEFAULT_LOG_FILE):
            os.startfile(DEFAULT_LOG_FILE)
        else:
            self.ui.statusbar.showMessage(f"Log file not found: {DEFAULT_LOG_FILE}")

    def _on_preview_action_toggled(self, checked: bool) -> None:
        """Show or hide the preview dock."""
        if self._syncing_preview_action:
            return
        dock = self.preview_ctrl.preview_dock
        if dock is None:
            return
        dock.setVisible(checked)
        if checked and not self.dockWidgetArea(dock):
            self.addDockWidget(Qt.BottomDockWidgetArea, dock)

    def _on_preview_dock_visibility_changed(self, visible: bool) -> None:
        """Sync the View action without recursively toggling the dock."""
        if self.ui.actionPreview.isChecked() == visible:
            return
        self._syncing_preview_action = True
        blocker = QSignalBlocker(self.ui.actionPreview)
        self.ui.actionPreview.setChecked(visible)
        del blocker
        self._syncing_preview_action = False

    def _mount_host_page(self, host_page, child_widget, use_scroll_area: bool = False):
        """Mount a reusable child widget into a host tab page."""
        layout = QVBoxLayout(host_page)
        layout.setContentsMargins(0, 0, 0, 0)
        if use_scroll_area:
            scroll_area = QScrollArea(host_page)
            scroll_area.setWidgetResizable(True)
            scroll_area.setFrameShape(QScrollArea.NoFrame)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll_area.setWidget(child_widget)
            layout.addWidget(scroll_area)
            return
        layout.addWidget(child_widget)

    def _insert_module_tab(self, title: str, child_widget, index: int) -> QWidget:
        """Insert a new module tab page at index and mount the child widget."""
        page = QWidget(self)
        self.ui.tabWidget_main.insertTab(index, page, title)
        self._mount_host_page(page, child_widget, use_scroll_area=True)
        return page

    def _schedule_chain_run(self, *_args) -> None:
        """Debounced full-chain re-run after module/pipeline changes."""
        if self.preview_ctrl.input_frame is None:
            return
        self.auto_run_timer.start(300)

    def _on_pipeline_changed(self) -> None:
        """Pipeline 勾选/顺序变化：同步各模块 Enable 总开关并重跑链。"""
        enabled = set(self.io_ctrl.get_pipeline_enabled())
        for tag, box in self._stage_enable_boxes.items():
            target = tag in enabled
            if box.isChecked() != target:
                box.setChecked(target)
        self.ui.statusbar.showMessage("Pipeline changed - re-running...")
        self._schedule_chain_run()

    def _on_module_enable_changed(self, tag: str, checked: bool) -> None:
        """模块 Enable 总开关切换：同步 pipeline 勾选并重跑链。"""
        self.io_ctrl.set_pipeline_stage_enabled(tag, checked)
        self._schedule_chain_run()

    def _on_input_loaded(self, frame, status_message):
        """Forward loaded input data to the preview and run the chain."""
        self.preview_ctrl.set_input_image(frame)
        self.preview_ctrl.set_output_image(None)
        self._latest_chain_frame = None
        self.ui.statusbar.showMessage(status_message)
        # 新输入：让 ACM 为新输入自动选择 colorspace；随后统一调度整链重跑。
        # （模块内部 request 只走其防抖定时器，而定时器已被宿主接管 -> 整链重跑）
        self.bcsh_ctrl.request_auto_run()
        self.acm_ctrl.request_auto_run()
        self._schedule_chain_run()

    def keyPressEvent(self, event):
        """Delegate preview hotkeys before falling back to the base window handler."""
        if self.preview_ctrl.handle_key_press(event):
            return
        super().keyPressEvent(event)


def main():
    """Launch the PQ Verify Tool host window."""
    app = QApplication(sys.argv)
    window = PqVerifyAppWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
