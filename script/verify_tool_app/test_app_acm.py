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

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def _ensure_generated_ui_modules():
    """Regenerate ui_gen modules when they are missing or older than the source .ui files."""
    ui_pairs = (
        ("ui\\acm_test_app_mainwindow.ui", "ui_gen\\acm_test_app_mainwindow.py"),
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

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout

from ui_impl.io_ui_impl import IoUiController, IoUiWidget
from ui_impl.acm_ui_impl import AcmUiController, AcmUiWidget
from ui_impl.io_preview_ui_impl import PreviewUiController, PreviewUiWidget

if __package__:
    from .ui_gen.acm_test_app_mainwindow import Ui_AcmTestAppWindow
else:
    from ui_gen.acm_test_app_mainwindow import Ui_AcmTestAppWindow


class AcmTestAppWindow(QMainWindow):
    """Main window host that composes the ACM UI widgets."""

    def __init__(self):
        super().__init__()
        self.ui = Ui_AcmTestAppWindow()
        self.ui.setupUi(self)

        self.io_widget = IoUiWidget(self)
        self.acm_widget = AcmUiWidget(self)
        self.preview_widget = PreviewUiWidget(self)

        self._mount_host_page(self.ui.tab_io_host, self.io_widget)
        self._mount_host_page(self.ui.tab_acm_host, self.acm_widget)

        self.preview_ctrl = PreviewUiController(
            self.preview_widget,
            parent_window=self,
            status_callback=self.ui.statusbar.showMessage,
        )
        self.io_ctrl = IoUiController(
            self.io_widget,
            parent_window=self,
            on_input_loaded=self._on_input_loaded,
            on_load_config=lambda path: self.acm_ctrl.load_current_config(path),
            status_callback=self.ui.statusbar.showMessage,
        )
        self.preview_ctrl.set_output_dir_getter(self.io_ctrl.get_output_dir)
        self.acm_ctrl = AcmUiController(
            self.acm_widget,
            parent_window=self,
            input_provider=lambda: self.preview_ctrl.input_frame,
            output_callback=self.preview_ctrl.set_output_image,
            preview_time_callback=self.preview_ctrl.set_time_cost_ms,
            status_callback=self.ui.statusbar.showMessage,
            config_path_getter=self.io_ctrl.get_config_path,
            config_path_setter=self.io_ctrl.set_config_path,
            dock_host=self,
        )
        self._install_view_menu()
        self.ui.statusbar.showMessage("Ready")

    def _install_view_menu(self) -> None:
        """Attach a View menu with a 'Show Preview' action to the menu bar.

        Allows re-displaying the preview dock after it has been closed.
        """
        view_menu = self.ui.menuView
        view_menu.clear()
        show_preview_action = QAction("Show Preview", self)
        show_preview_action.setShortcut(QKeySequence("Ctrl+P"))
        show_preview_action.triggered.connect(self._show_preview_dock)
        view_menu.addAction(show_preview_action)

    def _show_preview_dock(self) -> None:
        """Re-display the preview dock widget when the user requests it."""
        if self.preview_ctrl.preview_dock is None:
            return
        dock = self.preview_ctrl.preview_dock
        dock.setVisible(True)
        dock.show()
        dock.raise_()
        # Re-add to the same bottom dock area if Qt dropped it.
        if not self.dockWidgetArea(dock):
            self.addDockWidget(Qt.BottomDockWidgetArea, dock)

    def _mount_host_page(self, host_page, child_widget):
        """Mount a reusable child widget into a host tab page."""
        layout = QVBoxLayout(host_page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(child_widget)

    def _on_input_loaded(self, frame, status_message):
        """Forward loaded input data to the preview and ACM controllers."""
        self.preview_ctrl.set_input_image(frame)
        self.preview_ctrl.set_output_image(None)
        self.preview_ctrl.set_time_cost_ms(None)
        self.ui.statusbar.showMessage(status_message)
        self.acm_ctrl.request_auto_run()

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
