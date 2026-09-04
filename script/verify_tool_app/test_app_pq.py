"""
PQ Verify Tool (PySide6 pilot) — 链式流水线宿主窗口。
"""

import os
import subprocess
import sys

PQ_APP_VERSION = "v0.1"
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# verify_tool_app 的父目录是 script/；config_def、csc 等以顶层包方式导入
# （config_def/__init__.py 使用 `from config_def...`），故 script 目录需入 path。
SCRIPT_DIR = os.path.dirname(CURRENT_DIR)
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

for _path in (PROJECT_ROOT, SCRIPT_DIR):
    if _path not in sys.path:
        sys.path.insert(0, _path)


def _ensure_generated_ui_modules():
    """Regenerate ui_gen modules when they are missing or older than the source .ui files."""
    ui_pairs = (
        ("ui\\app_mainwindow.ui", "ui_gen\\app_mainwindow.py"),
        ("ui\\preview_ui.ui", "ui_gen\\preview_ui.py"),
        ("ui\\io_ui.ui", "ui_gen\\io_ui.py"),
        ("ui\\shp_ui.ui", "ui_gen\\shp_ui.py"),
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

    print("run auto uic to generate ui_gen modules...")
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
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QApplication, QMainWindow, QScrollArea, QVBoxLayout

from script.img_io import ImageFrame

if __package__:
    from .ui_impl.io_ui_impl import IoUiController, IoUiWidget
    from .ui_impl.shp_ui_impl import ShpUiController, ShpUiWidget
    from .ui_impl.preview_ui_impl import PreviewUiController, PreviewUiWidget
    from .ui_gen.app_mainwindow import Ui_AcmTestAppWindow
else:
    from ui_impl.io_ui_impl import IoUiController, IoUiWidget
    from ui_impl.shp_ui_impl import ShpUiController, ShpUiWidget
    from script.verify_tool_app.ui_impl.preview_ui_impl import PreviewUiController, PreviewUiWidget
    from ui_gen.app_mainwindow import Ui_AcmTestAppWindow


class PqVerifyAppWindow(QMainWindow):
    """Main window host that composes the I/O tab, pipeline stages and preview."""

    def __init__(self):
        super().__init__()
        self.ui = Ui_AcmTestAppWindow()
        self.ui.setupUi(self)
        self.setWindowTitle(f"PQ Verify Tool {PQ_APP_VERSION}")
        self.ui.tabWidget_main.setTabText(
            self.ui.tabWidget_main.indexOf(self.ui.tab_io_host), "I/O")
        self.ui.tabWidget_main.setTabText(
            self.ui.tabWidget_main.indexOf(self.ui.tab_module_host), "SHP")
        self._syncing_preview_action = False
        self._latest_chain_frame: ImageFrame | None = None

        self.io_widget = IoUiWidget(self)
        self.shp_widget = ShpUiWidget(self)
        self.preview_widget = PreviewUiWidget(self)

        self._mount_host_page(self.ui.tab_io_host, self.io_widget, use_scroll_area=True)
        self._mount_host_page(self.ui.tab_module_host, self.shp_widget, use_scroll_area=True)

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
            on_output_changed=self._on_output_config_changed,
            status_callback=self.ui.statusbar.showMessage,
            auto_load_defaults=False,
        )
        self.preview_ctrl.set_output_dir_getter(self.io_ctrl.get_output_dir)
        self.shp_ctrl = ShpUiController(
            self.shp_widget,
            parent_window=self,
            status_callback=self.ui.statusbar.showMessage,
            config_path_getter=self.io_ctrl.get_config_path,
        )
        self.preview_ctrl.set_full_res_output_provider(lambda: self._latest_chain_frame)
        # 链式流水线级（后续 CSC/DCI 依序插入，各暴露 process_frame(frame, io_info)）。
        self._stages = [
            ("SHP", self.shp_ctrl),
        ]

        self._install_run_action()
        self._install_view_menu()
        self.preview_ctrl.preview_dock.visibilityChanged.connect(self._on_preview_dock_visibility_changed)
        # 参数变化不自动重跑（SHP 走外部 exe）：提示用户按 Ctrl+R 重跑。
        self.shp_ctrl.paramsChanged.connect(self._on_params_changed)
        self.io_ctrl.auto_load_defaults()
        self.ui.statusbar.showMessage("Ready")

    # ------------------------------------------------------------------ #
    # Chain orchestration                                                #
    # ------------------------------------------------------------------ #

    def _run_chain(self) -> None:
        """Run the enabled pipeline stages in order over the current input frame."""
        src = self.preview_ctrl.input_frame
        if src is None:
            self.ui.statusbar.showMessage("No input loaded")
            return
        io_info = {
            "out_fmt": self.io_ctrl.get_output_fmt_code(),
            "out_clrspc": self.io_ctrl.get_output_clrspc(),
            "output_dir": self.io_ctrl.get_output_dir(),
            "width": src.width,
            "height": src.height,
        }
        current = src
        for tag, stage in self._stages:
            self.ui.statusbar.showMessage(f"{tag}: processing ...")
            ok, result = stage.process_frame(current, io_info)
            if not ok:
                self.ui.statusbar.showMessage(f"{tag}: {result}")
                return
            current = result
        self._latest_chain_frame = current
        self.preview_ctrl.set_output_image(current)
        self.ui.statusbar.showMessage("Pipeline finished")

    def _on_params_changed(self) -> None:
        """SHP 参数变化：提示手动重跑（避免每次滑动都调外部 exe）。"""
        self.ui.statusbar.showMessage("SHP params changed — press Ctrl+R / Run to re-run")

    def _on_output_config_changed(self) -> None:
        """Output format/colorspace changed: re-run the chain (debounced)."""
        if self.preview_ctrl.input_frame is None:
            return
        self.auto_run_timer.start(300)

    def _install_run_action(self) -> None:
        """Install a Run action (Ctrl+R) to re-run the pipeline manually."""
        run_action = QAction("Run Pipeline", self)
        run_action.setShortcut(QKeySequence("Ctrl+R"))
        run_action.triggered.connect(self._run_chain)
        self.ui.menubar.addAction(run_action)
        toolbar = self.addToolBar("Pipeline")
        toolbar.setObjectName("pq_pipeline_toolbar")
        toolbar.setMovable(False)
        toolbar.addAction(run_action)
        # 输出配置变化后的防抖重跑。
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

    def _install_view_menu(self) -> None:
        """Wire the Preview action to toggle the preview dock visibility."""
        self.ui.actionPreview.toggled.connect(self._on_preview_action_toggled)

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

    def _on_input_loaded(self, frame, status_message):
        """Forward loaded input data to the preview and run the chain."""
        self.preview_ctrl.set_input_image(frame)
        self.preview_ctrl.set_output_image(None)
        self._latest_chain_frame = None
        self.ui.statusbar.showMessage(status_message)
        self._run_chain()

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
