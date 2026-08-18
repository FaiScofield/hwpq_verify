"""
Copyright   : Copyright (c) 2026 by Rockchip. All right reserved.
FilePath    : test_app_hsv.py
Author      : vance.wu@rock-chips.com
Date        : 2026-08-13
Description : HSV test application host window with reusable widget composition
"""

import os
import subprocess
import sys

HSV_APP_VERSION = "v2.0"
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def _ensure_generated_ui_modules():
    """Regenerate ui_gen modules when they are missing or older than the source .ui files.

    PyInstaller 打包后跳过：ui_gen 模块已内置于可执行文件中，
    运行时不存在 .ui 源文件与 uic.cmd。
    """
    if getattr(sys, "frozen", False):
        return
    ui_pairs = (
        ("ui\\module_app_mainwindow.ui", "ui_gen\\module_app_mainwindow.py"),
        ("ui\\io_preview_ui.ui", "ui_gen\\io_preview_ui.py"),
        ("ui\\io_ui.ui", "ui_gen\\io_ui.py"),
        ("ui\\hsv_ui.ui", "ui_gen\\hsv_ui.py"),
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

from PySide6.QtCore import QSignalBlocker, Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QScrollArea, QVBoxLayout

if __package__:
    from .ui_impl.io_ui_impl import IoUiController, IoUiWidget
    from .ui_impl.hsv_ui_impl import HsvUiController, HsvUiWidget
    from .ui_impl.io_preview_ui_impl import PreviewUiController, PreviewUiWidget
    from .ui_gen.module_app_mainwindow import Ui_AcmTestAppWindow
else:
    from ui_impl.io_ui_impl import IoUiController, IoUiWidget
    from ui_impl.hsv_ui_impl import HsvUiController, HsvUiWidget
    from ui_impl.io_preview_ui_impl import PreviewUiController, PreviewUiWidget
    from ui_gen.module_app_mainwindow import Ui_AcmTestAppWindow


class HsvTestAppWindow(QMainWindow):
    """Main window host that composes the HSV UI widgets."""

    def __init__(self):
        super().__init__()
        self.ui = Ui_AcmTestAppWindow()
        self.ui.setupUi(self)
        self.setWindowTitle(f"HSV Test App {HSV_APP_VERSION}")
        # The host window .ui is shared across apps; set the HSV tab label here.
        self.ui.tabWidget_main.setTabText(
            self.ui.tabWidget_main.indexOf(self.ui.tab_module_host), "BCSH Config")
        self._syncing_preview_action = False

        self.io_widget = IoUiWidget(self)
        self.hsv_widget = HsvUiWidget(self)
        self.preview_widget = PreviewUiWidget(self)

        self._mount_host_page(self.ui.tab_io_host, self.io_widget, use_scroll_area=True)
        self._mount_host_page(self.ui.tab_module_host, self.hsv_widget, use_scroll_area=True)
        # 本程序不使用配置文件，隐藏 I/O 页的配置文件行（共享 UI 中未被用到的部分）。
        for _w in (self.io_widget.ui.label_config_file,
                   self.io_widget.ui.lineEdit_config_file,
                   self.io_widget.ui.pushButton_browse_config,
                   self.io_widget.ui.pushButton_load_config):
            _w.setVisible(False)

        self.preview_ctrl = PreviewUiController(
            self.preview_widget,
            parent_window=self,
            status_callback=self.ui.statusbar.showMessage,
        )
        self.io_ctrl = IoUiController(
            self.io_widget,
            parent_window=self,
            on_input_loaded=self._on_input_loaded,
            status_callback=self.ui.statusbar.showMessage,
            auto_load_defaults=False,
        )
        self.preview_ctrl.set_output_dir_getter(self.io_ctrl.get_output_dir)
        self.hsv_ctrl = HsvUiController(
            self.hsv_widget,
            parent_window=self,
            input_provider=lambda: self.preview_ctrl.input_frame,
            output_callback=self.preview_ctrl.set_output_image,
            status_callback=self.ui.statusbar.showMessage,
            work_size_provider=self.preview_ctrl.get_work_size,
            input_pixel_edit=self.preview_widget.ui.lineEdit_input_pixel,
            output_pixel_edit=self.preview_widget.ui.lineEdit_output_pixel,
        )
        self.preview_ctrl.set_full_res_output_provider(self.hsv_ctrl.get_full_res_output)
        self.preview_ctrl.set_pixel_selection_callback(self.hsv_ctrl.on_preview_pixel_selection)
        # 让预览实时像素读数跟随 BCSH 处理域（RGB(HSV)/YUV(YCbCr)）。
        self.preview_ctrl.set_colorspace_getter(
            lambda: self.hsv_ctrl.ui.comboBox_colorspace.currentText())
        self._install_view_menu()
        # Propagate HSV enabled state to preview for BothInLeft mode.
        self.hsv_ctrl.ui.checkBox_enableHsvAdj.toggled.connect(self.preview_ctrl.set_acm_enabled)
        self.preview_ctrl.set_acm_enabled(self.hsv_ctrl.ui.checkBox_enableHsvAdj.isChecked())
        # Keep actionPreview checked state in sync with dock visibility without re-entering toggle logic.
        self.preview_ctrl.preview_dock.visibilityChanged.connect(self._on_preview_dock_visibility_changed)
        self.io_ctrl.auto_load_defaults()
        self.ui.statusbar.showMessage("Ready")

    def _install_view_menu(self) -> None:
        """Wire the Preview action to toggle the preview dock visibility.

        The action is defined in module_app_mainwindow.ui as checkable /
        checked-by-default.  Toggling it shows or hides the preview dock.
        """
        action = self.ui.actionPreview
        action.toggled.connect(self._on_preview_action_toggled)

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
        """Forward loaded input data to the preview and HSV controllers."""
        self.preview_ctrl.set_input_image(frame)
        self.preview_ctrl.set_output_image(None)
        self.ui.statusbar.showMessage(status_message)
        self.hsv_ctrl.request_auto_run()

    def keyPressEvent(self, event):
        """Delegate preview hotkeys before falling back to the base window handler."""
        if self.preview_ctrl.handle_key_press(event):
            return
        super().keyPressEvent(event)


def main():
    """Launch the HSV test application host window."""
    app = QApplication(sys.argv)
    window = HsvTestAppWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
