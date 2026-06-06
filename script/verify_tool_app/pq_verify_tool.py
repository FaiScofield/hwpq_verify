"""
PQ Verify Tool - Unified module verification framework for ISP pipeline.

Supports multi-module pipeline serialization (CSC -> DCI -> SHP),
real-time parameter adjustment, and live image preview.

Entry point:  python pq_verify_tool.py
"""

import io
import os
import re
import sys

# Ensure the parent script/ package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import PySimpleGUI as sg
from PIL import Image

from csc.run_csc import (
    is_yuv_format,
    is_rgb_format,
    get_pixel_depth,
    get_frame_size,
    read_raw_to_planar,
    write_planar_to_raw,
    FORMAT_NAMES,
)

from verify_tool_app.ui_io import (
    TAB_LABEL as IO_TAB_LABEL,
    FMT_DISPLAY,
    DEFAULT_FMT_DISPLAY,
    CLRSPC_DISPLAY_RGB,
    IMAGE_EXTENSIONS,
    build_controls as build_io_controls,
    handle_io_event,
    update_clrspc_for_fmt,
    read_io_params,
    get_fmt_from_display,
    get_clrspc_from_display,
    _enforce_combo_width,
    IO_CLR_COMBO_SIZE,
)

from verify_tool_app.ui_csc import (
    TAB_LABEL as CSC_TAB_LABEL,
    build_controls as build_csc_controls,
    handle_csc_event,
    read_params as read_csc_params,
    process as process_csc,
    get_right_preview_image as csc_right_preview,
)

from verify_tool_app.ui_dci import (
    TAB_LABEL as DCI_TAB_LABEL,
    build_controls as build_dci_controls,
    handle_dci_event,
    read_params as read_dci_params,
    process as process_dci,
    get_right_preview_image as dci_right_preview,
)

from verify_tool_app.ui_shp import (
    TAB_LABEL as SHP_TAB_LABEL,
    build_controls as build_shp_controls,
    handle_shp_event,
    read_params as read_shp_params,
    process as process_shp,
    get_right_preview_image as shp_right_preview,
)

# ------------------------------------------------------------------ #
# ImageFrame — pipeline data abstraction                             #
# ------------------------------------------------------------------ #

class ImageFrame:
    """Image frame abstraction for pipeline data.

    Encapsulates planar data, format, colorspace, and frame index.
    Internal format convention for pipeline processing:
      8/10-bit RGB -> 0x2 (RGB_Planar) / 0x12 (RGB_Planar_10LSB)
      8/10-bit YUV -> 0x3 (YUV444P_YU24) / 0x13 (YUV444P_10LSB)
    """

    __slots__ = ("data", "fmt", "clrspc", "frame_idx")

    def __init__(self, data: np.ndarray, fmt: int, clrspc: int, frame_idx: int = 0):
        self.data = data          # planar (3, H, W)
        self.fmt = fmt            # format code
        self.clrspc = clrspc      # colorspace code
        self.frame_idx = frame_idx

    # -- properties -------------------------------------------------- #

    @property
    def depth(self) -> int:
        """Pixel bit depth derived from format code."""
        return get_pixel_depth(self.fmt)

    @property
    def is_yuv(self) -> bool:
        return is_yuv_format(self.fmt)

    @property
    def is_rgb(self) -> bool:
        return is_rgb_format(self.fmt)

    @property
    def height(self) -> int:
        return int(self.data.shape[1])

    @property
    def width(self) -> int:
        return int(self.data.shape[2])

    # -- helpers ----------------------------------------------------- #

    def copy(self) -> "ImageFrame":
        """Shallow copy with a deep copy of the data array."""
        return ImageFrame(self.data.copy(), self.fmt, self.clrspc, self.frame_idx)

    def as_tuple(self) -> tuple:
        """Return (data, fmt, clrspc) for backward-compatible module API."""
        return (self.data, self.fmt, self.clrspc)

    def _fmt_for_depth(self, target_10bit: bool) -> int:
        """Pick internal planar format code matching the YUV/RGB domain."""
        if self.is_rgb:
            return 0x12 if target_10bit else 0x2
        else:
            return 0x13 if target_10bit else 0x3

    # -- precision conversion ---------------------------------------- #

    def promote_to_10bit(self):
        """Promote 8-bit data to 10-bit by left-shifting 2 bits.

        Updates data (uint8 -> uint16) and fmt (e.g. 0x2 -> 0x12).
        No-op if already 10-bit.
        """
        if self.depth >= 10:
            return self
        self.data = (self.data.astype(np.uint16) << 2)
        self.fmt = self._fmt_for_depth(target_10bit=True)
        return self

    def demote_to_8bit(self):
        """Demote 10-bit data to 8-bit with rounding (add 2 then >> 2).

        Updates data (uint16 -> uint8) and fmt (e.g. 0x12 -> 0x2).
        No-op if already 8-bit.
        """
        if self.depth <= 8:
            return self
        rounded = (self.data.astype(np.uint32) + 2) >> 2
        self.data = rounded.astype(np.uint8)
        self.fmt = self._fmt_for_depth(target_10bit=False)
        return self


# ------------------------------------------------------------------ #
# Module registry                                                    #
# ------------------------------------------------------------------ #

REGISTERED_MODULES = {}

_PIPELINE_DEFAULT_ORDER = ["csc", "dci", "shp"]
_PIPELINE_DEFAULT_ENABLED = {"csc"}

pipeline_order = list(_PIPELINE_DEFAULT_ORDER)
pipeline_enabled = set(_PIPELINE_DEFAULT_ENABLED)

# Snapshot cache: {tag: ImageFrame}
_SNAPSHOTS: dict[str, ImageFrame] = {}

# Input image cache: ImageFrame read from file
_INPUT_IMAGE: ImageFrame | None = None

# Track last output format to detect changes that require buffer re-creation
_last_out_format: int | None = None
_last_out_frame_size: int = 0


def _register_modules():
    """Explicitly register all available modules."""
    global REGISTERED_MODULES
    REGISTERED_MODULES = {
        "csc": {
            "tag": "csc",
            "label": CSC_TAB_LABEL,
            "build_controls": build_csc_controls,
            "read_params": read_csc_params,
            "process": process_csc,
            "get_right_preview_image": csc_right_preview,
            "handle_event": handle_csc_event,
        },
        "dci": {
            "tag": "dci",
            "label": DCI_TAB_LABEL,
            "build_controls": build_dci_controls,
            "read_params": read_dci_params,
            "process": process_dci,
            "get_right_preview_image": dci_right_preview,
            "handle_event": handle_dci_event,
        },
        "shp": {
            "tag": "shp",
            "label": SHP_TAB_LABEL,
            "build_controls": build_shp_controls,
            "read_params": read_shp_params,
            "process": process_shp,
            "get_right_preview_image": shp_right_preview,
            "handle_event": handle_shp_event,
        },
    }


# ------------------------------------------------------------------ #
# Pipeline UI                                                        #
# ------------------------------------------------------------------ #

def _build_pipeline_bar() -> list:
    """Build the left-side vertical pipeline control bar."""
    rows = []
    for tag in pipeline_order:
        mod = REGISTERED_MODULES[tag]
        enabled = tag in pipeline_enabled
        rows.append([
            sg.Checkbox(
                mod["label"],
                default=enabled,
                key=f"-PIPE-ENABLE-{tag}-",
                enable_events=True,
                size=(3, 1),
            ),
            sg.Button("▲", key=f"-PIPE-UP-{tag}-", size=(1, 1)),
            sg.Button("▼", key=f"-PIPE-DOWN-{tag}-", size=(1, 1)),
        ])
    return [sg.Frame("Pipeline", rows, key="-PIPELINE-FRAME-")]


def _rebuild_pipeline_bar(window: sg.Window):
    """Rebuild pipeline bar after order/enable change: repack row frames vertically."""
    frame_widget = window["-PIPELINE-FRAME-"].Widget
    # ttk.LabelFrame inner content frame is the first child
    row_frame = frame_widget.winfo_children()[0]

    # Map tag -> parent tk frame (the row container)
    row_frames = {}
    for tag in pipeline_order:
        widget = window[f"-PIPE-ENABLE-{tag}-"].Widget
        row_frames[tag] = widget.master

    # Forget all row frames
    for parent in row_frames.values():
        parent.pack_forget()

    # Repack row frames in the updated pipeline_order sequence
    for tag in pipeline_order:
        row_frames[tag].pack(side="top", fill="x")

    # Sync checkbox state
    for tag in pipeline_order:
        window[f"-PIPE-ENABLE-{tag}-"].update(value=tag in pipeline_enabled)


# ------------------------------------------------------------------ #
# Preview layout                                                     #
# ------------------------------------------------------------------ #

PREVIEW_MAX_HEIGHT = 400

# Mouse tracking state
_mouse_pos = None
_pixel_info_frozen = False
_scale_factor = 1.0
_right_scale_factor = 1.0
_current_display_data = None  # (planar, fmt) currently shown in left preview
_right_display_data = None    # (planar, fmt) currently shown in right preview
_right_input_data = None      # (planar, fmt) input data before right-side processing
_right_frozen = False         # independent freeze for right preview
_right_mouse_pos = None
_left_display_size = (0, 0)   # (w, h) of the displayed left preview image in pixels
_last_left_frame_size = (0, 0)  # last Frame size used for re-render throttle


def _build_preview_layout() -> list:
    """Build the Preview layout: Common Info + Left/Right previews + Status."""
    return [
        [sg.HorizontalSeparator()],
        [sg.Frame("Common Info", [
            [
                sg.Text("Display Size", size=(12, 1)),
                sg.Input(
                    "", key="-DISPLAY-SIZE-", size=(48, 1),
                    readonly=True, border_width=0,
                    disabled_readonly_background_color=sg.theme_background_color(),
                    disabled_readonly_text_color=sg.theme_text_color(),
                ),
                sg.Text("Position", size=(12, 1)),
                sg.Input(
                    "", key="-POSITION-INFO-", size=(48, 1),
                    readonly=True, border_width=0,
                    disabled_readonly_background_color=sg.theme_background_color(),
                    disabled_readonly_text_color=sg.theme_text_color(),
                ),
            ],
            [
                sg.Text("Input Pixel", size=(12, 1)),
                sg.Input(
                    "", key="-INPUT-PIXEL-INFO-", size=(48, 1),
                    readonly=True, border_width=0,
                    disabled_readonly_background_color=sg.theme_background_color(),
                    disabled_readonly_text_color=sg.theme_text_color(),
                ),
                sg.Text("Output Pixel", size=(12, 1)),
                sg.Input(
                    "", key="-OUTPUT-PIXEL-INFO-", size=(48, 1),
                    readonly=True, border_width=0,
                    disabled_readonly_background_color=sg.theme_background_color(),
                    disabled_readonly_text_color=sg.theme_text_color(),
                ),
            ],
        ], expand_x=True)],
        [
            sg.Column([
                [
                    sg.Frame("Left Preview", [
                        [sg.Image(key="-LEFT-PREVIEW-", background_color="gray")]
                    ], key="-LEFT-PREVIEW-FRAME-", expand_x=True, expand_y=True),
                ],
            ], expand_x=True, expand_y=True),
            sg.Column([
                [
                    sg.Frame("Right Preview", [
                        [sg.Image(key="-RIGHT-PREVIEW-", background_color="gray")]
                    ], key="-RIGHT-PREVIEW-FRAME-", expand_x=True, expand_y=True),
                ],
            ], expand_x=True, expand_y=True),
            sg.Column([
                [sg.Checkbox("Show Left Input", key="-SHOW-INPUT-", default=False, enable_events=True)],
                [sg.Button("Save Left Image", key="-SAVE-LEFT-IMAGE-")],
                [sg.Checkbox("Show Right Input", key="-SHOW-RIGHT-INPUT-", default=False, enable_events=True)],
                [sg.Button("Save Right Image", key="-SAVE-RIGHT-IMAGE-")],
            ], vertical_alignment="top", pad=(8, 0)),
        ],
        [sg.Input("", key="-STATUS-", text_color="gray", size=(80, 1), readonly=True,
                  border_width=0,
                  disabled_readonly_background_color=sg.theme_background_color(),
                  disabled_readonly_text_color=sg.theme_text_color())],
    ]


# ------------------------------------------------------------------ #
# Image helpers                                                      #
# ------------------------------------------------------------------ #

def _planar_to_rgb_pil(planar: np.ndarray, fmt: int, max_size: int = PREVIEW_MAX_HEIGHT):
    """Convert a 3-plane planar array to a downscaled PIL RGB Image."""
    data = planar.astype(np.float32)
    depth = get_pixel_depth(fmt)

    if is_yuv_format(fmt):
        max_val = float((1 << depth) - 1)
        uv_half = 1 << (depth - 1)
        y = data[0]
        cb = data[1] - uv_half
        cr = data[2] - uv_half
        r = np.clip(y + 1.5748 * cr, 0, max_val)
        g = np.clip(y - 0.187324 * cb - 0.468124 * cr, 0, max_val)
        b = np.clip(y + 1.8556 * cb, 0, max_val)
        rgb = np.stack([r, g, b], axis=0)
    else:
        rgb = data

    if depth > 8:
        # Use integer division instead of >> which fails on float32 arrays
        rgb = (rgb // (1 << (depth - 8)))
    rgb = np.clip(rgb, 0, 255).astype(np.uint8)
    interleaved = np.stack([rgb[0], rgb[1], rgb[2]], axis=-1)
    img = Image.fromarray(interleaved, "RGB")

    if max(img.size) > max_size:
        ratio = max_size / max(img.size)
        new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
        img = img.resize(new_size, Image.LANCZOS if hasattr(Image, "LANCZOS") else Image.Resampling.LANCZOS)

    return img


def _pil_to_bytes(img: Image.Image) -> bytes:
    """Convert PIL Image to PNG bytes for sg.Image."""
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    return bio.getvalue()


def _update_status(window: sg.Window, text: str, color: str = "gray"):
    """Update the status bar with text and color."""
    window["-STATUS-"].update(value=text)
    try:
        window["-STATUS-"].Widget.configure(foreground=color)
    except Exception:
        pass


def _maybe_render_left_on_resize(window: sg.Window, fw: int, fh: int) -> bool:
    """Re-render left preview if frame size changed significantly. Returns True if re-rendered."""
    global _last_left_frame_size
    last_w, last_h = _last_left_frame_size
    if abs(fw - last_w) < 15 and abs(fh - last_h) < 15:
        return False
    _last_left_frame_size = (fw, fh)
    if _current_display_data is not None:
        planar, fmt = _current_display_data
        _update_left_preview(window, planar, fmt)
        return True
    return False


def _update_left_preview(window: sg.Window, planar: np.ndarray, fmt: int, tag: str = ""):
    """Update the left preview area with new image data."""
    global _current_display_data, _scale_factor, _left_display_size
    _current_display_data = (planar, fmt)

    # Scale image to fit available preview area, never exceeding original resolution.
    # _planar_to_rgb_pil compares max_size against max(img_width, img_height),
    # so we clamp to original's max dimension and the frame's min dimension.
    orig_h, orig_w = planar.shape[1], planar.shape[2]
    try:
        frame_h = window["-LEFT-PREVIEW-FRAME-"].Widget.winfo_height()
        frame_w = window["-LEFT-PREVIEW-FRAME-"].Widget.winfo_width()
        if frame_h < 100:
            max_size = max(orig_w, orig_h)
        else:
            max_size = min(frame_h, frame_w, max(orig_w, orig_h))
    except Exception:
        max_size = max(orig_w, orig_h)

    img = _planar_to_rgb_pil(planar, fmt, max_size=max_size)
    w, h = img.size
    orig_h, orig_w = planar.shape[1], planar.shape[2]
    _scale_factor = h / orig_h if orig_h > 0 else 1.0
    _left_display_size = (w, h)
    window["-LEFT-PREVIEW-"].update(data=_pil_to_bytes(img))
    window["-DISPLAY-SIZE-"].update(value=f"{w}x{h} (scale={_scale_factor:.2f})")


def _update_right_preview(window: sg.Window, tag: str, snapshot: tuple, params: dict):
    """Update the right preview with module-specific image.

    The right preview image is height-matched to the left preview for
    consistent visual comparison. Display resolution is used for matching,
    so the displayed heights are always the same regardless of original
    resolutions.
    """
    global _right_display_data, _right_scale_factor, _right_input_data
    mod = REGISTERED_MODULES.get(tag)
    if mod is None:
        window["-RIGHT-PREVIEW-"].update(data=b"")
        _right_display_data = None
        _right_input_data = None
        return
    getter = mod.get("get_right_preview_image")
    if getter is None:
        window["-RIGHT-PREVIEW-"].update(data=b"")
        _right_display_data = None
        _right_input_data = None
        return

    # Store the input snapshot before right-side processing
    if snapshot is not None and isinstance(snapshot, tuple) and len(snapshot) >= 2:
        _right_input_data = (snapshot[0], snapshot[1])
    else:
        _right_input_data = None

    result = getter(snapshot, params)
    if result is not None:
        if isinstance(result, Image.Image):
            img = result
        elif isinstance(result, tuple) and len(result) == 2:
            # DCI returns (mapped_planar, fmt) tuple
            mapped_data, mapped_fmt = result
            img = _planar_to_rgb_pil(mapped_data, mapped_fmt, max_size=99999)
            _right_display_data = (mapped_data, mapped_fmt)
        elif isinstance(result, np.ndarray):
            img = Image.fromarray(result, "RGB") if result.ndim == 3 else Image.fromarray(result, "L").convert("RGB")
        else:
            window["-RIGHT-PREVIEW-"].update(data=b"")
            _right_display_data = None
            return

        # Scale right preview to match left preview display height
        left_disp_h = _left_display_size[1]
        if left_disp_h > 0 and img.size[1] > 0:
            h_ratio = left_disp_h / img.size[1]
            new_w = int(img.size[0] * h_ratio)
            img = img.resize((new_w, left_disp_h), Image.LANCZOS if hasattr(Image, "LANCZOS") else Image.Resampling.LANCZOS)
            _right_scale_factor = h_ratio
        else:
            _right_scale_factor = 1.0

        # Store full planar data for right-preview pixel lookup if not already stored
        if _right_display_data is None:
            _right_display_data = (snapshot[0], snapshot[1]) if snapshot is not None and len(snapshot) >= 2 else None

        window["-RIGHT-PREVIEW-"].update(data=_pil_to_bytes(img))
    else:
        window["-RIGHT-PREVIEW-"].update(data=b"")
        _right_display_data = None


def _get_left_preview_height(window: sg.Window) -> int | None:
    """Get the current displayed height of the left preview image."""
    try:
        data = window["-LEFT-PREVIEW-"].get()
        if data:
            from io import BytesIO
            bio = BytesIO(data)
            img = Image.open(bio)
            return img.size[1]
    except Exception:
        pass
    return None


# ------------------------------------------------------------------ #
# Pipeline execution                                                 #
# ------------------------------------------------------------------ #

def _get_effective_pipeline() -> list:
    """Return ordered list of enabled module tags."""
    return [t for t in pipeline_order if t in pipeline_enabled]


def _invalidate_from(tag: str):
    """Clear snapshots from the given tag onwards."""
    started = False
    for t in pipeline_order:
        if t == tag:
            started = True
        if started:
            _SNAPSHOTS.pop(t, None)


def _parse_color_input(text: str):
    """Parse color input text into a list of 3 integers. Returns None on failure."""
    if not text or not text.strip():
        return None
    text = text.strip().replace(',', ' ')
    parts = text.split()
    nums = []
    for p in parts:
        try:
            nums.append(int(float(p)))
        except ValueError:
            continue
    if len(nums) < 3:
        return None
    return nums[:3]


def _load_input_image(values: dict, window: sg.Window) -> bool:
    """Load input file or generate set-color image into _INPUT_IMAGE cache.

    Returns True on success.  Applies stream-depth promotion to 10-bit if needed.
    """
    global _INPUT_IMAGE
    io_params = read_io_params(values)

    w = io_params["width"]
    h = io_params["height"]
    in_fmt = io_params["in_fmt"]
    in_clrspc = io_params["in_clrspc"]

    stream_depth_str = values.get("-STREAM-DEPTH-", "8bit")
    stream_10bit = (stream_depth_str == "10bit")

    use_set_color = values.get("-USE-SET-COLOR-", False)
    if use_set_color:
        color_vals = _parse_color_input(values.get("-SET-COLOR-INPUT-", ""))
        if color_vals is None:
            _update_status(window, "Invalid set-color input", color="orange")
            return False
        depth = get_pixel_depth(in_fmt)
        max_val = (1 << depth) - 1
        data = np.zeros((3, h, w), dtype=np.uint16 if depth > 8 else np.uint8)
        for i in range(3):
            data[i, :, :] = int(np.clip(color_vals[i], 0, max_val))
        _INPUT_IMAGE = ImageFrame(data, in_fmt, in_clrspc)
        _SNAPSHOTS.clear()
        if stream_10bit:
            _INPUT_IMAGE.promote_to_10bit()
        _update_status(window, f"Set color ({' '.join(str(v) for v in color_vals)}) applied", color="green")
        return True

    input_file = io_params["input_file"]
    if not input_file or not os.path.isfile(input_file):
        _update_status(window, "No input file selected", color="orange")
        return False

    # Handle image files (PNG/JPG/JPEG/BMP) via PIL, treat as RGB888
    ext = os.path.splitext(input_file)[1].lower()
    if ext in IMAGE_EXTENSIONS:
        try:
            from PIL import Image as PILImage
            im = PILImage.open(input_file).convert("RGB")
            w, h = im.size
            arr = np.asarray(im)
            # Convert interleaved RGB (H, W, 3) to planar (3, H, W)
            data = np.stack([arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]], axis=0).astype(np.uint8)
            im.close()
            # Update width/height on UI to match actual image dimensions
            window["-WIDTH-"].update(value=str(w))
            window["-HEIGHT-"].update(value=str(h))
            values["-WIDTH-"] = str(w)
            values["-HEIGHT-"] = str(h)
            _INPUT_IMAGE = ImageFrame(data, 0x0, in_clrspc)
            _SNAPSHOTS.clear()
            if stream_10bit:
                _INPUT_IMAGE.promote_to_10bit()
            _update_status(window, f"Loaded image: {os.path.basename(input_file)} ({w}x{h})", color="green")
            return True
        except Exception as e:
            _update_status(window, f"Image read error: {e}", color="red")
            return False

    expected_size = 0
    try:
        expected_size = get_frame_size(w, h, in_fmt)
    except Exception:
        pass

    actual_size = os.path.getsize(input_file)
    if expected_size > 0 and actual_size < expected_size:
        _update_status(window, "File too small for frame size", color="orange")

    try:
        data = read_raw_to_planar(input_file, w, h, in_fmt)
    except Exception as e:
        _update_status(window, f"Read error: {e}", color="red")
        return False

    _INPUT_IMAGE = ImageFrame(data, in_fmt, in_clrspc)
    _SNAPSHOTS.clear()
    if stream_10bit:
        _INPUT_IMAGE.promote_to_10bit()
    _update_status(window, f"Loaded: {os.path.basename(input_file)}", color="green")
    return True


def _run_pipeline(values: dict, window: sg.Window, trigger_tag: str = ""):
    """Execute the pipeline. If trigger_tag is set, only re-run from that module."""
    global _INPUT_IMAGE, _last_out_format, _last_out_frame_size

    io_params = read_io_params(values)

    out_fmt = io_params["out_fmt"]
    out_clrspc = io_params["out_clrspc"]
    width = io_params["width"]
    height = io_params["height"]

    # Read stream depth for promotion / demotion decisions
    stream_depth_str = values.get("-STREAM-DEPTH-", "8bit")
    stream_10bit = (stream_depth_str == "10bit")
    out_fmt_is_8bit = (get_pixel_depth(out_fmt) <= 8)

    # Recalculate output frame size; force full pipeline reset if changed
    out_frame_size = get_frame_size(width, height, out_fmt)
    out_fmt_changed = (_last_out_format is not None and out_fmt != _last_out_format)
    if out_fmt_changed:
        _SNAPSHOTS.clear()
    _last_out_format = out_fmt
    _last_out_frame_size = out_frame_size

    # Determine whether to re-run from trigger_tag or from scratch
    start_tag = trigger_tag if trigger_tag else ""
    if start_tag:
        # Check if upstream snapshot exists
        upstream: ImageFrame | None = _SNAPSHOTS.get(start_tag)
        if upstream is None:
            # Fall back to input
            start_tag = ""
        else:
            # Invalidate downstream if needed
            _invalidate_from(start_tag)

    if not start_tag:
        if out_fmt_changed and _INPUT_IMAGE is not None:
            # Output format changed, input unchanged: skip input reload
            pass
        else:
            _SNAPSHOTS.clear()
            if not _load_input_image(values, window):
                return
        upstream = _INPUT_IMAGE

    effective = _get_effective_pipeline()
    if not effective:
        # No modules enabled, show input (with stream-depth demotion if needed)
        if _INPUT_IMAGE is not None:
            display_frame = _INPUT_IMAGE
            if stream_10bit and out_fmt_is_8bit:
                display_frame = _INPUT_IMAGE.copy()
                display_frame.demote_to_8bit()
            _update_left_preview(window, display_frame.data, display_frame.fmt)
        return

    # Determine start index
    start_idx = 0
    if start_tag:
        try:
            start_idx = effective.index(start_tag)
        except ValueError:
            start_idx = 0
            upstream = _INPUT_IMAGE
            _SNAPSHOTS.clear()
            if not _load_input_image(values, window):
                return
            upstream = _INPUT_IMAGE

    if upstream is None:
        _update_status(window, "No input data", color="orange")
        return

    current_frame = upstream
    output_dir = io_params["output_dir"] or os.path.dirname(io_params["input_file"]) or "."

    for i in range(start_idx, len(effective)):
        tag = effective[i]
        mod = REGISTERED_MODULES.get(tag)
        if mod is None:
            _update_status(window, f"Module '{tag}' not registered", color="orange")
            continue

        snap_key = tag
        if i > 0 and snap_key in _SNAPSHOTS:
            # Use cached upstream result
            current_frame = _SNAPSHOTS[snap_key]
            continue

        params = mod["read_params"](values)

        if tag == "csc":
            ok, result = mod["process"](
                current_frame.data, current_frame.fmt, current_frame.clrspc,
                out_fmt, out_clrspc, params,
            )
            if ok:
                current_frame = ImageFrame(result, out_fmt, out_clrspc)
            else:
                _update_status(window, f"CSC error: {result}", color="red")
                return
        else:
            # DCI/SHP need io_params
            full_io = {
                "width": io_params["width"],
                "height": io_params["height"],
                "frame_idx": io_params["frame_idx"],
                "frame_num": io_params["frame_num"],
                "output_dir": output_dir,
                "config_path": io_params["config_path"],
                "exe_path": values.get("-DCI-EXE-", ""),
                "sharpen_exe": values.get("-SHP-EXE-", ""),
            }
            ok, result, res_fmt, res_clrspc = mod["process"](
                current_frame.data, current_frame.fmt, current_frame.clrspc,
                out_fmt, out_clrspc, params, full_io,
            )
            if ok:
                current_frame = ImageFrame(result, res_fmt, res_clrspc)
            else:
                _update_status(window, f"{tag.upper()} error: {result}", color="red")
                return

        _SNAPSHOTS[tag] = current_frame.copy()

    # Apply stream-depth demotion after last module if output format is 8-bit
    display_frame = current_frame
    if stream_10bit and out_fmt_is_8bit:
        display_frame = current_frame.copy()
        display_frame.demote_to_8bit()

    # Display final output
    final_tag = effective[-1] if effective else ""
    _update_status(window, f"Pipeline OK ({' → '.join(effective)})", color="green")
    _update_left_preview(window, display_frame.data, display_frame.fmt, final_tag)
    _update_right_preview(window, final_tag, display_frame.as_tuple(),
                           REGISTERED_MODULES.get(final_tag, {}).get("read_params", lambda v: {})(values))


def _handle_mouse_motion(window: sg.Window, values: dict, event: str):
    """Handle mouse motion over left preview to update pixel info."""
    global _pixel_info_frozen, _mouse_pos

    if _pixel_info_frozen:
        return

    try:
        e = window["-LEFT-PREVIEW-"].user_bind_event
        widget_x, widget_y = e.x, e.y
    except Exception:
        return

    if _scale_factor <= 0:
        return
    orig_x = int(widget_x / _scale_factor)
    orig_y = int(widget_y / _scale_factor)
    _mouse_pos = (orig_x, orig_y)

    # Get input pixel
    input_str = "(----, ----, ----)"
    if _INPUT_IMAGE is not None:
        in_planar = _INPUT_IMAGE.data
        in_fmt = _INPUT_IMAGE.fmt
        in_h, in_w = in_planar.shape[1], in_planar.shape[2]
        if 0 <= orig_x < in_w and 0 <= orig_y < in_h:
            p0 = in_planar[0, orig_y, orig_x]
            p1 = in_planar[1, orig_y, orig_x]
            p2 = in_planar[2, orig_y, orig_x]
            fmt_label = "yuv" if is_yuv_format(in_fmt) else "rgb"
            input_str = f"{fmt_label}: ({p0:4d}, {p1:4d}, {p2:4d})"

    # Get output pixel
    output_str = "(----, ----, ----)"
    if _current_display_data is not None:
        out_planar, _ = _current_display_data
        out_h, out_w = out_planar.shape[1], out_planar.shape[2]
        if 0 <= orig_x < out_w and 0 <= orig_y < out_h:
            p0 = out_planar[0, orig_y, orig_x]
            p1 = out_planar[1, orig_y, orig_x]
            p2 = out_planar[2, orig_y, orig_x]
            # Use I/O output format for the label, not the displayed data format
            io_out_fmt = get_fmt_from_display(values.get("-OUT-FMT-", DEFAULT_FMT_DISPLAY))
            fmt_label = "yuv" if is_yuv_format(io_out_fmt) else "rgb"
            output_str = f"{fmt_label}: ({p0:4d}, {p1:4d}, {p2:4d})"

    freeze_status = "[Frozen]" if _pixel_info_frozen else "[Space to freeze]"
    window["-POSITION-INFO-"].update(f"({orig_x:4d},{orig_y:4d}) {freeze_status}")
    window["-INPUT-PIXEL-INFO-"].update(input_str)
    window["-OUTPUT-PIXEL-INFO-"].update(output_str)


def _handle_right_mouse_motion(window: sg.Window, values: dict, event: str):
    """Handle mouse motion over right preview to update pixel info."""
    global _right_frozen, _right_mouse_pos

    if _right_frozen:
        return

    try:
        e = window["-RIGHT-PREVIEW-"].user_bind_event
        widget_x, widget_y = e.x, e.y
    except Exception:
        return

    if _right_scale_factor <= 0:
        return
    orig_x = int(widget_x / _right_scale_factor)
    orig_y = int(widget_y / _right_scale_factor)
    _right_mouse_pos = (orig_x, orig_y)

    # Get input pixel from input image
    input_str = "(----, ----, ----)"
    if _INPUT_IMAGE is not None:
        in_planar = _INPUT_IMAGE.data
        in_fmt = _INPUT_IMAGE.fmt
        in_h, in_w = in_planar.shape[1], in_planar.shape[2]
        if 0 <= orig_x < in_w and 0 <= orig_y < in_h:
            p0 = in_planar[0, orig_y, orig_x]
            p1 = in_planar[1, orig_y, orig_x]
            p2 = in_planar[2, orig_y, orig_x]
            fmt_label = "yuv" if is_yuv_format(in_fmt) else "rgb"
            input_str = f"{fmt_label}: ({p0:4d}, {p1:4d}, {p2:4d})"

    # Get output pixel from right display data
    output_str = "(----, ----, ----)"
    if _right_display_data is not None:
        out_planar, out_fmt = _right_display_data
        out_h, out_w = out_planar.shape[1], out_planar.shape[2]
        if 0 <= orig_x < out_w and 0 <= orig_y < out_h:
            p0 = out_planar[0, orig_y, orig_x]
            p1 = out_planar[1, orig_y, orig_x]
            p2 = out_planar[2, orig_y, orig_x]
            fmt_label = "yuv" if is_yuv_format(out_fmt) else "rgb"
            output_str = f"{fmt_label}: ({p0:4d}, {p1:4d}, {p2:4d})"

    # Get display size
    display_str = ""
    if _right_display_data is not None:
        rhs, rws = _right_display_data[0].shape[1], _right_display_data[0].shape[2]
        display_str = f"{rws}x{rhs} (scale={_right_scale_factor:.2f})"
    if not display_str and _current_display_data is not None:
        lh, lw = _current_display_data[0].shape[1], _current_display_data[0].shape[2]
        display_str = f"{lw}x{lh} (scale={_scale_factor:.2f})"

    freeze_status = "[Frozen]" if _right_frozen else "[Space to freeze]"
    window["-POSITION-INFO-"].update(f"({orig_x:4d},{orig_y:4d}) {freeze_status}")
    window["-INPUT-PIXEL-INFO-"].update(input_str)
    window["-OUTPUT-PIXEL-INFO-"].update(output_str)
    if display_str:
        window["-DISPLAY-SIZE-"].update(value=display_str)


def _clear_pixel_info(window: sg.Window):
    """Clear pixel info display unless either preview is frozen."""
    if _pixel_info_frozen or _right_frozen:
        return
    window["-POSITION-INFO-"].update("")
    window["-INPUT-PIXEL-INFO-"].update("(hover over image)")
    window["-OUTPUT-PIXEL-INFO-"].update("")


def _refresh_right_preview_only(window: sg.Window, values: dict):
    """Refresh only the right preview using the current pipeline output snapshot.

    Used when DCI COMBO MEDIAN changes to avoid re-running the full pipeline.
    """
    effective = _get_effective_pipeline()
    if not effective:
        return
    last_tag = effective[-1]
    snap = _SNAPSHOTS.get(last_tag) or _INPUT_IMAGE
    if snap is None:
        return
    mod = REGISTERED_MODULES.get(last_tag)
    if mod is None:
        return
    params = mod.get("read_params", lambda v: {})(values)
    _update_right_preview(window, last_tag, snap.as_tuple(), params)


def _save_image(values: dict, window: sg.Window, display_data):
    """Save the given display data (planar, fmt) to file."""
    if display_data is None:
        _update_status(window, "No image to save", color="orange")
        return

    file_path = sg.popup_get_file(
        "Save Image", save_as=True,
        file_types=(("PNG", "*.png"), ("BMP", "*.bmp"), ("RAW YUV", "*.yuv"), ("RAW RGB", "*.rgb")),
    )
    if not file_path:
        return

    planar, fmt = display_data
    ext = os.path.splitext(file_path)[1].lower()

    try:
        if ext in (".png", ".bmp"):
            img = _planar_to_rgb_pil(planar, fmt, max_size=99999)
            img.save(file_path)
        elif ext in (".yuv", ".rgb"):
            width = int(values.get("-WIDTH-", "1920"))
            height = int(values.get("-HEIGHT-", "1080"))
            write_planar_to_raw(planar, file_path, width, height, fmt)
        else:
            _update_status(window, f"Unsupported format: {ext}", color="orange")
            return
        _update_status(window, f"Saved: {file_path}", color="green")
    except Exception as e:
        _update_status(window, f"Save error: {e}", color="red")


def _update_right_preview_with_snapshot(window: sg.Window, planar: np.ndarray, fmt: int):
    """Update right preview directly with the given planar data (for Show Right Input)."""
    global _right_display_data, _right_scale_factor
    _right_display_data = (planar, fmt)
    img = _planar_to_rgb_pil(planar, fmt, max_size=99999)
    # Match left preview display height
    left_disp_h = _left_display_size[1]
    if left_disp_h > 0 and img.size[1] > 0:
        h_ratio = left_disp_h / img.size[1]
        new_w = int(img.size[0] * h_ratio)
        img = img.resize((new_w, left_disp_h), Image.LANCZOS if hasattr(Image, "LANCZOS") else Image.Resampling.LANCZOS)
        _right_scale_factor = h_ratio
    else:
        _right_scale_factor = 1.0
    window["-RIGHT-PREVIEW-"].update(data=_pil_to_bytes(img))


# ------------------------------------------------------------------ #
# Main                                                               #
# ------------------------------------------------------------------ #

def main():
    """Main entry point for PQ Verify Tool."""
    global _pixel_info_frozen, _mouse_pos, _scale_factor, _current_display_data, _right_scale_factor, _right_display_data, _right_input_data, _right_frozen
    global _left_display_size, _INPUT_IMAGE, _last_out_format, _last_out_frame_size, pipeline_order, pipeline_enabled, _SNAPSHOTS

    _register_modules()

    sg.theme("SystemDefault")

    # Build tab layout
    tab_group = sg.TabGroup([[
        sg.Tab(IO_TAB_LABEL, build_io_controls()),
        sg.Tab(CSC_TAB_LABEL, build_csc_controls()),
        sg.Tab(DCI_TAB_LABEL, build_dci_controls()),
        sg.Tab(SHP_TAB_LABEL, build_shp_controls()),
    ]], expand_x=True, key="-TAB-GROUP-")

    # Build full layout
    layout = [
        [
            tab_group,
            sg.Column([
                _build_pipeline_bar(),
                [sg.Checkbox("dump", key="-DUMP-", default=False)],
            ], vertical_alignment="top"),
        ],
        *_build_preview_layout(),
    ]
    # rows.append([sg.Checkbox("dump", key="-DUMP-", default=False)])

    window = sg.Window(
        "PQ Verify Tool v0.2",
        layout,
        resizable=True,
        finalize=True,
        return_keyboard_events=True,
        size=(1300, 900),
    )

    # Bind mouse events for pixel info
    window["-LEFT-PREVIEW-"].bind("<Motion>", "+MOTION")
    window["-LEFT-PREVIEW-"].bind("<Enter>", "+ENTER")
    window["-LEFT-PREVIEW-"].bind("<Leave>", "+LEAVE")

    # Bind keyboard events on left preview for pixel freeze
    window["-LEFT-PREVIEW-"].Widget.bind("<space>", lambda e: window.write_event_value("-LEFT-PREVIEW-SPACE-", None))
    window["-LEFT-PREVIEW-"].Widget.focus_set()

    # Bind mouse events on right preview
    window["-RIGHT-PREVIEW-"].bind("<Motion>", "+MOTION")
    window["-RIGHT-PREVIEW-"].bind("<Enter>", "+ENTER")
    window["-RIGHT-PREVIEW-"].bind("<Leave>", "+LEAVE")
    window["-RIGHT-PREVIEW-"].Widget.bind("<space>", lambda e: window.write_event_value("-RIGHT-PREVIEW-SPACE-", None))

    # Bind <Configure> on preview FRAMES (not Image, which doesn't expand)
    def _on_left_frame_resize(e):
        w = e.width
        h = e.height
        if w > 1 and h > 1:
            window.write_event_value("-LEFT-PREVIEW-RESIZE-", (w, h))
    window["-LEFT-PREVIEW-FRAME-"].Widget.bind("<Configure>", _on_left_frame_resize)

    # Bind slider keyboard for DCI/SHP
    _bind_sliders(window)

    # Initial colorspace sync
    _init_clrspc_sync(window)

    # Initial BCSH norm labels
    _init_bcsh_norm(window)

    # Event loop
    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            break

        # Pipeline bar events
        if event.startswith("-PIPE-ENABLE-"):
            tag = event.replace("-PIPE-ENABLE-", "").rstrip("-")
            if values[event]:
                pipeline_enabled.add(tag)
            else:
                pipeline_enabled.discard(tag)
            _run_pipeline(values, window)
            continue

        if event.startswith("-PIPE-UP-"):
            tag = event.replace("-PIPE-UP-", "").rstrip("-")
            idx = pipeline_order.index(tag)
            if idx > 0:
                pipeline_order[idx], pipeline_order[idx - 1] = \
                    pipeline_order[idx - 1], pipeline_order[idx]
                _rebuild_pipeline_bar(window)
                _SNAPSHOTS.clear()
                _run_pipeline(values, window)
            continue

        if event.startswith("-PIPE-DOWN-"):
            tag = event.replace("-PIPE-DOWN-", "").rstrip("-")
            idx = pipeline_order.index(tag)
            if idx < len(pipeline_order) - 1:
                pipeline_order[idx], pipeline_order[idx + 1] = \
                    pipeline_order[idx + 1], pipeline_order[idx]
                _rebuild_pipeline_bar(window)
                _SNAPSHOTS.clear()
                _run_pipeline(values, window)
            continue

        # Mouse pixel info - left preview
        if event == "-LEFT-PREVIEW-+MOTION":
            _handle_mouse_motion(window, values, event)
            continue

        if event == "-LEFT-PREVIEW-+LEAVE":
            if not _pixel_info_frozen:
                _clear_pixel_info(window)
            continue

        # Mouse pixel info - right preview
        if event == "-RIGHT-PREVIEW-+MOTION":
            _handle_right_mouse_motion(window, values, event)
            continue

        if event == "-RIGHT-PREVIEW-+LEAVE":
            if not _right_frozen:
                _clear_pixel_info(window)
            continue

        # Re-render left preview on frame resize (throttled by 15px)
        if event == "-LEFT-PREVIEW-RESIZE-":
            fw, fh = values[event]
            if _maybe_render_left_on_resize(window, fw, fh):
                pass  # printed inside _maybe_render_left_on_resize
            print(f"[resize] Left preview frame: {fw}x{fh}")
            continue

        # Space to freeze/unfreeze pixel info — independent per preview
        if event == "-LEFT-PREVIEW-SPACE-":
            _pixel_info_frozen = not _pixel_info_frozen
            status = "[Frozen]" if _pixel_info_frozen else "[Unfrozen]"
            pos = window["-POSITION-INFO-"].get()
            if _pixel_info_frozen:
                window["-POSITION-INFO-"].update(pos.replace("[Space to freeze]", status))
            else:
                window["-POSITION-INFO-"].update(pos.replace("[Frozen]", status))
            continue

        if event == "-RIGHT-PREVIEW-SPACE-":
            _right_frozen = not _right_frozen
            status = "[Frozen]" if _right_frozen else "[Unfrozen]"
            pos = window["-POSITION-INFO-"].get()
            if _right_frozen:
                window["-POSITION-INFO-"].update(pos.replace("[Space to freeze]", status))
            else:
                window["-POSITION-INFO-"].update(pos.replace("[Frozen]", status))
            continue

        # Show Left Input checkbox
        if event == "-SHOW-INPUT-":
            if values["-SHOW-INPUT-"] and _INPUT_IMAGE is not None:
                _update_left_preview(window, _INPUT_IMAGE.data, _INPUT_IMAGE.fmt, "input")
            else:
                # Show last output
                effective = _get_effective_pipeline()
                if effective:
                    last = effective[-1]
                    snap = _SNAPSHOTS.get(last) or _INPUT_IMAGE
                    if snap:
                        _update_left_preview(window, snap.data, snap.fmt, last)
            continue

        # Show Right Input checkbox
        if event == "-SHOW-RIGHT-INPUT-":
            if values["-SHOW-RIGHT-INPUT-"] and _right_input_data is not None:
                _update_right_preview_with_snapshot(window, _right_input_data[0], _right_input_data[1])
            else:
                # Refresh right preview from pipeline
                _refresh_right_preview_only(window, values)
            continue

        # Save Left Image
        if event == "-SAVE-LEFT-IMAGE-":
            _save_image(values, window, _current_display_data)
            continue

        # Save Right Image
        if event == "-SAVE-RIGHT-IMAGE-":
            _save_image(values, window, _right_display_data)
            continue

        # Stream depth changed — reload input and re-run pipeline
        if event == "-STREAM-DEPTH-":
            _SNAPSHOTS.clear()
            _run_pipeline(values, window)
            continue

        # IO events
        if handle_io_event(event, values, window):
            if not event.startswith("-OPEN-DIR-"):
                _run_pipeline(values, window)
            continue

        # CSC events
        if handle_csc_event(event, values, window):
            if event not in ("-SAT-SET-COLOR-",):
                _run_pipeline(values, window, trigger_tag="csc")
            continue

        # DCI events
        if handle_dci_event(event, values, window):
            # UI-only events: don't trigger pipeline re-run
            if event not in ("-DCI-OPEN-EXE-DIR-", "-DCI-OPEN-AUDIT-DIR-", "-DCI-AUDIT-DIR-"):
                if not event.endswith("-RESET-"):
                    _run_pipeline(values, window, trigger_tag="dci")
            # Refresh right preview for COMBO MEDIAN or audit dir changes
            if event in ("-DCI-COMBO-MEDIAN-", "-DCI-AUDIT-DIR-"):
                _refresh_right_preview_only(window, values)
            continue

        # SHP events
        if handle_shp_event(event, values, window):
            _run_pipeline(values, window, trigger_tag="shp")
            continue

    window.close()


def _init_clrspc_sync(window: sg.Window):
    """Sync initial colorspace combos to match default format on startup."""
    from verify_tool_app.ui_io import DEFAULT_FMT_DISPLAY
    update_clrspc_for_fmt(window, {}, "-IN-CLR-", DEFAULT_FMT_DISPLAY)
    update_clrspc_for_fmt(window, {}, "-OUT-CLR-", DEFAULT_FMT_DISPLAY)


def _init_bcsh_norm(window: sg.Window):
    """Initialize BCSH norm labels to default values on startup."""
    from csc.csc_ui import get_bcsh_norm_value
    from csc.run_csc import get_default_bcsh_raw_values
    from verify_tool_app.ui_csc import BCSH_NAMES, ALGO_RK_HW_CSC
    algo_type = ALGO_RK_HW_CSC
    defaults = get_default_bcsh_raw_values(algo_type)
    key_name_map = {
        "bright": "brightness", "contrast": "contrast",
        "sat": "saturation", "hue": "hue",
        "r_gain": "r_gain", "r_offset": "r_offset",
        "g_gain": "g_gain", "g_offset": "g_offset",
        "b_gain": "b_gain", "b_offset": "b_offset",
    }
    for _, k1, _, k2 in BCSH_NAMES:
        for k in (k1, k2):
            config_key = key_name_map.get(k, k)
            default_val = defaults.get(config_key, 256)
            norm = get_bcsh_norm_value(k, default_val, algo_type)
            window[f"-BCSH-{k}-NORM-"].update(value=norm)


def _bind_sliders(window: sg.Window):
    """Bind keyboard events on all module slider/spin widgets."""
    from verify_tool_app.ui_csc import bind_keyboard_events as bind_csc
    from verify_tool_app.ui_dci import bind_keyboard_events as bind_dci
    from verify_tool_app.ui_shp import bind_keyboard_events as bind_shp

    bind_csc(window)
    bind_dci(window)
    bind_shp(window)


if __name__ == "__main__":
    main()
