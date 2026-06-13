"""
I/O tab controller — encapsulates all IO-related behavior for reuse.
"""

from collections.abc import Callable
import os
import re

import numpy as np
from PIL import Image
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox, QWidget

from script.csc.run_csc import (
    CLRSPC_NAMES,
    CLRSPC_OPTIONS,
    FORMAT_NAMES,
    FMT_OPTIONS,
    get_frame_size,
    is_yuv_format,
    read_raw_to_planar,
)

try:
    from ..ui_gen.io_ui import Ui_IoUiWidget
except ImportError:
    from ui_gen.io_ui import Ui_IoUiWidget


class IoUiWidget(QWidget):
    """Reusable I/O configuration widget."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create the I/O widget from the generated UI definition."""
        super().__init__(parent)
        self.ui = Ui_IoUiWidget()
        self.ui.setupUi(self)


class IoUiController:
    """Controls the I/O tab: init combos, handle signals, and load input data."""

    # ------------------------------------------------------------------ #
    # Initialization                                                     #
    # ------------------------------------------------------------------ #

    def __init__(
        self,
        io_widget: IoUiWidget,
        parent_window: QMainWindow | None = None,
        on_input_loaded: Callable[[np.ndarray, str], None] | None = None,
        on_load_config: Callable[[str], None] | None = None,
        status_callback: Callable[[str], None] | None = None,
    ) -> None:
        """Bind to an IoUiWidget instance and explicit host callbacks.

        Args:
            io_widget: An IoUiWidget whose ``.ui`` provides the I/O controls.
            parent_window: Optional host window kept only for dialog parenting.
            on_input_loaded: Optional callback receiving ``(input_yuv444, status_message)``.
            on_load_config: Optional callback receiving a config path.
            status_callback: Optional callback receiving a status-bar message.
        """
        self._win = parent_window
        self.widget = io_widget
        self.ui = io_widget.ui
        self._on_input_loaded = on_input_loaded
        self._load_config_callback = on_load_config
        self._status_callback = status_callback
        self._init_ui()
        self._connect_signals()

    def _init_ui(self) -> None:
        """Populate format/colorspace combo boxes with default selections."""
        fmt_display = [f"0x{fmt:x} - {FORMAT_NAMES.get(fmt, 'Unknown')}" for fmt in FMT_OPTIONS]
        self.ui.comboBox_input_format.addItems(fmt_display)
        self.ui.comboBox_output_format.addItems(fmt_display)

        clrspc_display = [f"{clr} - {CLRSPC_NAMES[clr]}" for clr in CLRSPC_OPTIONS]
        clrspc_rgb = [item for item in clrspc_display if int(item.split(" ")[0]) in (0, 1)]
        clrspc_yuv = [item for item in clrspc_display if int(item.split(" ")[0]) in range(2, 8)]
        self.ui.comboBox_input_colorspace.addItems(clrspc_rgb)
        self.ui.comboBox_output_colorspace.addItems(clrspc_rgb)

        default_yuv_fmt = next((item for item in fmt_display if item.startswith("0x3 ")), "")
        if default_yuv_fmt:
            self.ui.comboBox_input_format.setCurrentText(default_yuv_fmt)
            self.ui.comboBox_output_format.setCurrentText(default_yuv_fmt)
        if clrspc_yuv:
            default_yuv_clrspc = clrspc_yuv[3] if len(clrspc_yuv) > 3 else clrspc_yuv[-1]
            self.ui.comboBox_input_colorspace.clear()
            self.ui.comboBox_input_colorspace.addItems(clrspc_yuv)
            self.ui.comboBox_output_colorspace.clear()
            self.ui.comboBox_output_colorspace.addItems(clrspc_yuv)
            self.ui.comboBox_input_colorspace.setCurrentText(default_yuv_clrspc)
            self.ui.comboBox_output_colorspace.setCurrentText(default_yuv_clrspc)

    def _connect_signals(self) -> None:
        """Wire I/O widget signals to internal handlers."""
        self.ui.pushButton_browse_input.clicked.connect(self._on_browse_input)
        self.ui.pushButton_reload.clicked.connect(self._on_reload_input)
        self.ui.pushButton_browse_output.clicked.connect(self._on_browse_output)
        self.ui.pushButton_open_output.clicked.connect(self._on_open_output_dir)
        self.ui.pushButton_browse_config.clicked.connect(self._on_browse_config)
        self.ui.pushButton_load_config.clicked.connect(self._on_load_config)
        self.ui.comboBox_input_format.currentIndexChanged.connect(self._on_input_format_changed)
        self.ui.checkBox_set_color.toggled.connect(self._on_set_color_toggled)

    # ------------------------------------------------------------------ #
    # Public queries                                                     #
    # ------------------------------------------------------------------ #

    def get_input_fmt_code(self) -> int:
        """Return the currently selected input format integer code."""
        fmt_str = self.ui.comboBox_input_format.currentText()
        return int(fmt_str.split(" ")[0], 16) if fmt_str else 0

    def get_input_clrspc(self) -> int:
        """Return the currently selected input colorspace integer code."""
        clr_str = self.ui.comboBox_input_colorspace.currentText()
        return int(clr_str.split(" ")[0]) if clr_str else 0

    # ------------------------------------------------------------------ #
    # Signal handlers                                                    #
    # ------------------------------------------------------------------ #

    def _on_browse_input(self) -> None:
        """Browse for an input file and load it into memory."""
        path, _ = QFileDialog.getOpenFileName(
            None,
            "Select Input File",
            "",
            "All Files (*.*);;YUV Files (*.yuv);;RGB Files (*.rgb);;Image Files (*.png *.jpg *.bmp)",
        )
        if path:
            self.ui.lineEdit_input_file.setText(path)
            self._guess_input_params(path)
            self._recalc_frame_num()
            self._load_input_image()

    def _on_reload_input(self) -> None:
        """Reload the current input file with the latest I/O settings."""
        self.ui.checkBox_set_color.setChecked(False)
        path = self.ui.lineEdit_input_file.text()
        if path:
            self._guess_input_params(path)
            self._recalc_frame_num()
            self._load_input_image()

    def _on_browse_output(self) -> None:
        """Browse for an output directory."""
        path = QFileDialog.getExistingDirectory(None, "Select Output Directory")
        if path:
            self.ui.lineEdit_output_dir.setText(path)

    def _on_open_output_dir(self) -> None:
        """Open the configured output directory."""
        path = self.ui.lineEdit_output_dir.text()
        if path and os.path.isdir(path):
            os.startfile(path)

    def _on_browse_config(self) -> None:
        """Browse for an ACM config file."""
        path, _ = QFileDialog.getOpenFileName(None, "Select Config File", "", "JSON Files (*.json)")
        if path:
            self.ui.lineEdit_config_file.setText(path)

    def _on_load_config(self) -> None:
        """Load the ACM config into the current ACM instance."""
        if self._load_config_callback is not None:
            self._load_config_callback(self.ui.lineEdit_config_file.text())

    def _on_input_format_changed(self, index: int) -> None:
        """Update colorspace choices after the input format changes."""
        del index
        fmt_str = self.ui.comboBox_input_format.currentText()
        if not fmt_str:
            return
        fmt_code = int(fmt_str.split(" ")[0], 16)
        clrspc_display = [f"{clr} - {CLRSPC_NAMES[clr]}" for clr in CLRSPC_OPTIONS]
        if (fmt_code & 0xF) <= 0x2:
            options = [item for item in clrspc_display if int(item.split(" ")[0]) in (0, 1)]
        else:
            options = [item for item in clrspc_display if int(item.split(" ")[0]) in range(2, 8)]
        current_text = self.ui.comboBox_input_colorspace.currentText()
        self.ui.comboBox_input_colorspace.clear()
        self.ui.comboBox_input_colorspace.addItems(options)
        idx = options.index(current_text) if current_text in options else -1
        self.ui.comboBox_input_colorspace.setCurrentIndex(max(0, idx))

    def _on_set_color_toggled(self, enabled: bool) -> None:
        """Toggle the explicit-color input edit."""
        self.ui.lineEdit_set_color.setEnabled(enabled)

    # ------------------------------------------------------------------ #
    # File helpers                                                       #
    # ------------------------------------------------------------------ #

    def _guess_input_params(self, filepath: str) -> None:
        """Guess format and resolution from the selected input file name."""
        basename = os.path.basename(filepath).lower()
        ext = os.path.splitext(basename)[1]
        fmt_display = [f"0x{fmt:x} - {FORMAT_NAMES.get(fmt, 'Unknown')}" for fmt in FMT_OPTIONS]

        if ext in (".png", ".jpg", ".jpeg", ".bmp"):
            rgb_fmt = next((item for item in fmt_display if item.startswith("0x0 ")), None)
            if rgb_fmt:
                self.ui.comboBox_input_format.setCurrentText(rgb_fmt)
            try:
                with Image.open(filepath) as image:
                    width, height = image.size
                self.ui.spinBox_width.setValue(width)
                self.ui.spinBox_height.setValue(height)
            except Exception:
                pass
        elif ext == ".yuv":
            yuv_fmt = next((item for item in fmt_display if item.startswith("0x3 ")), None)
            if yuv_fmt:
                self.ui.comboBox_input_format.setCurrentText(yuv_fmt)
        elif ext == ".rgb":
            rgb_fmt = next((item for item in fmt_display if item.startswith("0x0 ")), None)
            if rgb_fmt:
                self.ui.comboBox_input_format.setCurrentText(rgb_fmt)

        match = re.search(r"(\d+)x(\d+)", basename)
        if match:
            self.ui.spinBox_width.setValue(int(match.group(1)))
            self.ui.spinBox_height.setValue(int(match.group(2)))

    def _recalc_frame_num(self) -> None:
        """Recalculate frame count from the selected file and format."""
        input_file = self.ui.lineEdit_input_file.text()
        if not input_file or not os.path.isfile(input_file):
            return

        ext = os.path.splitext(input_file)[1].lower()
        if ext in (".png", ".jpg", ".jpeg", ".bmp"):
            self.ui.spinBox_frame_num.setValue(1)
            return

        fmt_str = self.ui.comboBox_input_format.currentText()
        if not fmt_str:
            return
        fmt_code = int(fmt_str.split(" ")[0], 16)
        width = self.ui.spinBox_width.value()
        height = self.ui.spinBox_height.value()
        frame_size = get_frame_size(width, height, fmt_code)
        actual_size = os.path.getsize(input_file)
        frame_num = max(1, actual_size // frame_size) if frame_size > 0 else 1
        self.ui.spinBox_frame_num.setValue(frame_num)

    # ------------------------------------------------------------------ #
    # Image loading                                                      #
    # ------------------------------------------------------------------ #

    def get_output_dir(self) -> str:
        """Return the currently configured output directory."""
        return self.ui.lineEdit_output_dir.text()

    def get_config_path(self) -> str:
        """Return the currently configured ACM config path."""
        return self.ui.lineEdit_config_file.text()

    def set_config_path(self, path: str) -> None:
        """Update the visible ACM config path."""
        self.ui.lineEdit_config_file.setText(path)

    def _emit_input_loaded(self, input_yuv444: np.ndarray, status_message: str) -> None:
        """Publish a successfully loaded input image to the host."""
        if self._on_input_loaded is not None:
            self._on_input_loaded(input_yuv444, status_message)
        elif self._status_callback is not None:
            self._status_callback(status_message)

    def _load_input_image(self) -> None:
        """Load input data into a YUV444 buffer and notify parent."""
        input_file = self.ui.lineEdit_input_file.text()
        use_set_color = self.ui.checkBox_set_color.isChecked()

        if use_set_color:
            color_str = self.ui.lineEdit_set_color.text()
            try:
                red, green, blue = map(int, color_str.split())
                width = self.ui.spinBox_width.value()
                height = self.ui.spinBox_height.value()
                y_data = np.full((height, width), red * 0.299 + green * 0.587 + blue * 0.114, dtype=np.uint8)
                cb_data = np.full((height, width), 128 - red * 0.114 - green * 0.385 + blue * 0.5, dtype=np.uint8)
                cr_data = np.full((height, width), 128 + red * 0.5 - green * 0.454 - blue * 0.046, dtype=np.uint8)
                input_yuv444 = np.stack([y_data, cb_data, cr_data], axis=-1)
                self._emit_input_loaded(input_yuv444, f"Input generated: {width}x{height}")
            except Exception:
                QMessageBox.warning(None, "Warning", "Invalid color format. Use 'R G B'")
            return

        if not input_file or not os.path.isfile(input_file):
            return

        fmt_str = self.ui.comboBox_input_format.currentText()
        if not fmt_str:
            return
        fmt_code = int(fmt_str.split(" ")[0], 16)
        width = self.ui.spinBox_width.value()
        height = self.ui.spinBox_height.value()
        try:
            data, _ = read_raw_to_planar(input_file, width, height, fmt_code, repeat_to_444=True)
            input_yuv444 = self._convert_to_yuv444(data, fmt_code)
            self._emit_input_loaded(input_yuv444, f"Input loaded: {width}x{height}")
        except Exception as exc:
            QMessageBox.critical(None, "Error", f"Failed to load image: {exc}")

    def _convert_to_yuv444(self, data: tuple[np.ndarray, ...], fmt_code: int) -> np.ndarray:
        """Convert raw planar input data to channels-last YUV444."""
        if is_yuv_format(fmt_code):
            y_data = data[0]
            u_data = data[1]
            v_data = data[2]
            if u_data.shape[1] != y_data.shape[1]:
                u_data = np.repeat(u_data, 2, axis=1)
                v_data = np.repeat(v_data, 2, axis=1)
            if u_data.shape[0] != y_data.shape[0]:
                u_data = np.repeat(u_data, 2, axis=0)
                v_data = np.repeat(v_data, 2, axis=0)
            return np.stack([y_data, u_data, v_data], axis=-1)

        red = data[0].astype(np.float32)
        green = data[1].astype(np.float32)
        blue = data[2].astype(np.float32)
        y_data = (0.2126 * red + 0.7152 * green + 0.0722 * blue + 0.5).astype(np.uint8)
        cb_data = (-0.1146 * red - 0.3854 * green + 0.5 * blue + 128 + 0.5).astype(np.uint8)
        cr_data = (0.5 * red - 0.4542 * green - 0.0458 * blue + 128 + 0.5).astype(np.uint8)
        return np.stack([y_data, cb_data, cr_data], axis=-1)
