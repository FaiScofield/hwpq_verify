"""
I/O tab controller — encapsulates all IO-related behavior for reuse.
"""

from collections.abc import Callable
import os
import re

from PIL import Image
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox, QWidget

from script.csc.run_csc import (
    CLRSPC_NAMES,
    CLRSPC_OPTIONS,
    FORMAT_NAMES,
    FMT_OPTIONS,
    get_frame_size,
)
from script.img_io import (
    ImageFrame, STB_IMAGE_EXTENSIONS, guess_fmt_from_ext,
    is_limited_range, is_yuv_format, get_pixel_depth,
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
        on_input_loaded: Callable[[object, str], None] | None = None,
        on_load_config: Callable[[str], None] | None = None,
        status_callback: Callable[[str], None] | None = None,
        auto_load_defaults: bool = True,
    ) -> None:
        """Bind to an IoUiWidget instance and explicit host callbacks.

        Args:
            io_widget: An IoUiWidget whose ``.ui`` provides the I/O controls.
            parent_window: Optional host window kept only for dialog parenting.
            on_input_loaded: Optional callback receiving ``(input_yuv444, status_message)``.
            on_load_config: Optional callback receiving a config path.
            status_callback: Optional callback receiving a status-bar message.
            auto_load_defaults: Whether to auto-load the default input/config during init.
        """
        self._win = parent_window
        self.widget = io_widget
        self.ui = io_widget.ui
        self._on_input_loaded = on_input_loaded
        self._load_config_callback = on_load_config
        self._status_callback = status_callback
        self._input_loaded = False
        self._init_ui()
        self._connect_signals()
        if auto_load_defaults:
            self._auto_load_defaults()

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

        self.ui.comboBox_output_format.setEnabled(False)
        self.ui.comboBox_output_colorspace.setEnabled(False)

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
        self.ui.lineEdit_set_color.returnPressed.connect(self._on_set_color_return_pressed)

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
            # Only re-guess format if no input has been loaded yet.
            if not self._input_loaded:
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
        """Update colorspace choices, reload input, and re-run pipeline."""
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
        self._recalc_frame_num()
        self._load_input_image()

    # ------------------------------------------------------------------ #
    # Auto-load defaults on startup                                       #
    # ------------------------------------------------------------------ #

    def _auto_load_defaults(self) -> None:
        """Auto-load the input image and config file if defaults are valid."""
        input_path = self.ui.lineEdit_input_file.text().strip()
        config_path = self.ui.lineEdit_config_file.text().strip()

        input_loaded = False
        if input_path and os.path.isfile(input_path):
            self._on_reload_input()
            input_loaded = True

        config_loaded = False
        if config_path and os.path.isfile(config_path) and self._load_config_callback:
            self._load_config_callback(config_path)
            config_loaded = True

        if self._status_callback:
            if input_loaded and config_loaded:
                self._status_callback("Auto-loaded input image and config.")
            elif input_loaded:
                self._status_callback("Auto-loaded input image.")

    def auto_load_defaults(self) -> None:
        """Public wrapper used by the host after all dependent controllers exist."""
        self._auto_load_defaults()

    def _on_set_color_toggled(self, enabled: bool) -> None:
        """Toggle the explicit-color input edit and reload."""
        self.ui.lineEdit_set_color.setEnabled(enabled)
        if enabled:
            # Clear any previous success style so the user starts fresh
            self.ui.lineEdit_set_color.setStyleSheet("")
        self._load_input_image()

    def _guess_input_params(self, filepath: str) -> None:
        """Guess format and resolution from the selected input file name."""
        basename = os.path.basename(filepath).lower()
        ext = os.path.splitext(basename)[1]
        fmt_display = [f"0x{fmt:x} - {FORMAT_NAMES.get(fmt, 'Unknown')}" for fmt in FMT_OPTIONS]

        if ext in STB_IMAGE_EXTENSIONS:
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
        if ext in STB_IMAGE_EXTENSIONS:
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

    def _emit_input_loaded(self, frame: ImageFrame, status_message: str) -> None:
        """Publish a successfully loaded input image to the host."""
        if self._on_input_loaded is not None:
            self._on_input_loaded(frame, status_message)
        elif self._status_callback is not None:
            self._status_callback(status_message)

    def _load_set_color_input(self) -> None:
        """Build a solid-colour ImageFrame from the set-color fields.

        The three channel values are parsed as RGB or YUV depending on the
        selected input format.  Limited-range colorspaces clamp the 8-bit
        values to the spec-defined ranges before scaling to 10-bit.
        """
        color_str = self.ui.lineEdit_set_color.text().strip()
        parsed = self._parse_color_text(color_str)
        if parsed is None:
            QMessageBox.warning(None, "Warning", "Invalid color format. Use three numbers separated by spaces or commas (e.g. 128,128,128 or 128 128 128)")
            self.ui.lineEdit_set_color.setStyleSheet("")
            return
        c1, c2, c3 = parsed
        self.ui.lineEdit_set_color.setStyleSheet("color: #22dd22;")
        fmt_str = self.ui.comboBox_input_format.currentText()
        if not fmt_str:
            return
        fmt_code = int(fmt_str.split(" ")[0], 16)
        clrspc = self.get_input_clrspc()
        depth = get_pixel_depth(fmt_code)
        limited = is_limited_range(clrspc)
        width = self.ui.spinBox_width.value()
        height = self.ui.spinBox_height.value()

        # Clamp 8-bit base values when using limited range.
        if limited and is_yuv_format(fmt_code):
            # Y ∈ [16, 235], U/V ∈ [16, 240]
            c1 = max(16, min(235, c1))
            c2 = max(16, min(240, c2))
            c3 = max(16, min(240, c3))
        elif limited:
            # RGB ∈ [16, 235]
            c1 = max(16, min(235, c1))
            c2 = max(16, min(235, c2))
            c3 = max(16, min(235, c3))

        channel_label = "YUV" if is_yuv_format(fmt_code) else "RGB"
        if is_yuv_format(fmt_code):
            frame = ImageFrame.from_solid_yuv(
                width, height, c1, c2, c3, clrspc, depth,
            )
        else:
            frame = ImageFrame.from_solid_color(
                width, height, c1, c2, c3, clrspc, depth,
            )
        self._emit_input_loaded(
            frame,
            f"Input generated ({channel_label} {c1}, {c2}, {c3}) "
            f"{'limited' if limited else 'full'} range, {depth}-bit, "
            f"size: {width}x{height}",
        )

    def _on_set_color_return_pressed(self) -> None:
        """Parse the set-color text when Enter is pressed.

        On success the text colour turns green; on failure a warning is shown
        and the colour stays unchanged.
        """
        color_str = self.ui.lineEdit_set_color.text().strip()
        parsed = self._parse_color_text(color_str)
        if parsed is None:
            QMessageBox.warning(
                None, "Warning",
                "Invalid color format. Use three numbers separated by spaces or commas (e.g. 128,128,128 or 128 128 128)",
            )
            return
        self.ui.lineEdit_set_color.setStyleSheet("color: #22dd22;")
        self._load_input_image()

    @staticmethod
    def _parse_color_text(text: str) -> tuple[int, int, int] | None:
        """Parse 'C1 C2 C3' or 'C1,C2,C3' into three ints. Returns None on failure."""
        parts = re.split(r'[,\s]+', text.strip())
        parts = [p for p in parts if p]
        if len(parts) != 3:
            return None
        try:
            return tuple(map(int, parts))
        except ValueError:
            return None

    def _load_input_image(self) -> None:
        """Load input data as an ImageFrame and notify parent."""
        input_file = self.ui.lineEdit_input_file.text()
        use_set_color = self.ui.checkBox_set_color.isChecked()

        if use_set_color:
            self._load_set_color_input()
            return

        if not input_file or not os.path.isfile(input_file):
            return

        fmt_str = self.ui.comboBox_input_format.currentText()
        if not fmt_str:
            return
        fmt_code = int(fmt_str.split(" ")[0], 16)
        width = self.ui.spinBox_width.value()
        height = self.ui.spinBox_height.value()
        frame_idx = self.ui.spinBox_frame_idx.value()
        clrspc = self.get_input_clrspc()

        try:
            ext = os.path.splitext(input_file)[1].lower()
            if ext in STB_IMAGE_EXTENSIONS:
                frame = ImageFrame.from_image(input_file, clrspc)
            else:
                frame = ImageFrame.from_file(
                    input_file, width, height, fmt_code, clrspc, frame_idx,
                )
            self._emit_input_loaded(
                frame, f"Input loaded: {frame.width}x{frame.height}, idx={frame_idx}")
            self._input_loaded = True
        except Exception as exc:
            QMessageBox.critical(None, "Error", f"Failed to load image: {exc}")
