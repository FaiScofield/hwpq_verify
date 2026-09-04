"""
Copyright   : Copyright (c) 2026 by Rockchip. All right reserved.
FilePath    : acm_test_app.py
Author      : vance.wu@rock-chips.com
Date        : 2026-06-13
Description : ACM test application host window with reusable widget composition
"""

import os
import subprocess
import sys

ACM_APP_VERSION = "v1.1"
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def _ensure_generated_ui_modules():
    """Regenerate ui_gen modules when they are missing or older than the source .ui files."""
    ui_pairs = (
        ("ui\\module_app_mainwindow.ui", "ui_gen\\module_app_mainwindow.py"),
        ("ui\\acm_ui.ui", "ui_gen\\acm_ui.py"),
        ("ui\\io_preview_ui.ui", "ui_gen\\io_preview_ui.py"),
        ("ui\\io_ui.ui", "ui_gen\\io_ui.py"),
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
    from .ui_impl.acm_ui_impl import AcmUiController, AcmUiWidget
    from .ui_impl.io_preview_ui_impl import PreviewUiController, PreviewUiWidget
    from .ui_gen.module_app_mainwindow import Ui_AcmTestAppWindow
else:
    from ui_impl.io_ui_impl import IoUiController, IoUiWidget
    from ui_impl.acm_ui_impl import AcmUiController, AcmUiWidget
    from ui_impl.io_preview_ui_impl import PreviewUiController, PreviewUiWidget
    from ui_gen.module_app_mainwindow import Ui_AcmTestAppWindow


class AcmTestAppWindow(QMainWindow):
    """Main window host that composes the ACM UI widgets."""

    def __init__(self):
        super().__init__()
        self.ui = Ui_AcmTestAppWindow()
        self.ui.setupUi(self)
        self.setWindowTitle(f"ACM Test App {ACM_APP_VERSION}")
        # The host window .ui is shared across apps; set the ACM tab label here.
        self.ui.tabWidget_main.setTabText(
            self.ui.tabWidget_main.indexOf(self.ui.tab_module_host), "ACM Config")
        self._syncing_preview_action = False

        self.io_widget = IoUiWidget(self)
        self.acm_widget = AcmUiWidget(self)
        self.preview_widget = PreviewUiWidget(self)

        self._mount_host_page(self.ui.tab_io_host, self.io_widget, use_scroll_area=True)
        self._mount_host_page(self.ui.tab_module_host, self.acm_widget, use_scroll_area=True)

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
        self.acm_ctrl = AcmUiController(
            self.acm_widget,
            parent_window=self,
            input_provider=lambda: self.preview_ctrl.input_frame,
            output_callback=self.preview_ctrl.set_output_image,
            status_callback=self.ui.statusbar.showMessage,
            config_path_getter=self.io_ctrl.get_config_path,
            config_path_setter=self.io_ctrl.set_config_path,
            work_size_provider=self.preview_ctrl.get_work_size,
            input_pixel_edit=self.preview_widget.ui.lineEdit_input_pixel,
            output_pixel_edit=self.preview_widget.ui.lineEdit_output_pixel,
            output_fmt_provider=self.io_ctrl.get_output_fmt_code,
            output_clrspc_provider=self.io_ctrl.get_output_clrspc,
            dock_host=self,
        )
        self.preview_ctrl.set_full_res_output_provider(self.acm_ctrl.get_full_res_output)
        self.preview_ctrl.set_pixel_selection_callback(self._on_preview_pixel_selection_changed)
        self._install_view_menu()
        # Propagate ACM enabled state to preview for BothInLeft mode.
        self.acm_ctrl.ui.checkBox_enable_acm.toggled.connect(self.preview_ctrl.set_acm_enabled)
        self.preview_ctrl.set_acm_enabled(self.acm_ctrl.ui.checkBox_enable_acm.isChecked())
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

    def _pixel_readout(self, x_pos: int, y_pos: int, role: str) -> str:
        """Delegate preview pixel readout to the ACM processing caches (步骤 1~6)."""
        return self.acm_ctrl.readout_text(x_pos, y_pos, role)

    def _on_output_config_changed(self) -> None:
        """Re-run ACM processing when the output format/colorspace changes."""
        self.acm_ctrl.request_auto_run()

    def _on_input_loaded(self, frame, status_message):
        """Forward loaded input data to the preview and ACM controllers."""
        self.preview_ctrl.set_input_image(frame)
        self.preview_ctrl.set_output_image(None)
        self.acm_ctrl.clear_preview_h_marker()
        self.ui.statusbar.showMessage(status_message)
        self.acm_ctrl.request_auto_run()

    def _on_preview_pixel_selection_changed(self, selection: dict | None) -> None:
        """Bridge preview freeze state into the ACM H-axis marker overlay."""
        if not selection or not selection.get("frozen", False):
            self.acm_ctrl.clear_preview_h_marker()
            return
        self.acm_ctrl.update_preview_h_marker(selection["x"], selection["y"])

    def keyPressEvent(self, event):
        """Delegate preview hotkeys before falling back to the base window handler."""
        if self.preview_ctrl.handle_key_press(event):
            return
        super().keyPressEvent(event)


def main():
    """Launch the ACM test application host window."""
    app = QApplication(sys.argv)
    window = AcmTestAppWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
