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
    read_raw_to_planar,
    write_planar_to_raw,
    FORMAT_NAMES,
)

from verify_tool_app.ui_io import (
    TAB_LABEL as IO_TAB_LABEL,
    FMT_DISPLAY,
    DEFAULT_FMT_DISPLAY,
    CLRSPC_DISPLAY_RGB,
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
# Module registry                                                    #
# ------------------------------------------------------------------ #

REGISTERED_MODULES = {}

_PIPELINE_DEFAULT_ORDER = ["csc", "dci", "shp"]
_PIPELINE_DEFAULT_ENABLED = {"csc"}

pipeline_order = list(_PIPELINE_DEFAULT_ORDER)
pipeline_enabled = set(_PIPELINE_DEFAULT_ENABLED)

# Snapshot cache: {tag: (data: np.ndarray, fmt: int, clrspc: int)}
_SNAPSHOTS: dict[str, tuple] = {}

# Input image cache: (data_planar, fmt, clrspc) read from file
_INPUT_IMAGE: tuple | None = None


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
    """Build the top pipeline control bar."""
    row = []
    for tag in pipeline_order:
        mod = REGISTERED_MODULES[tag]
        enabled = tag in pipeline_enabled
        row.extend([
            sg.Checkbox(
                mod["label"],
                default=enabled,
                key=f"-PIPE-ENABLE-{tag}-",
                enable_events=True,
            ),
            sg.Button("◀", key=f"-PIPE-LEFT-{tag}-", size=(2, 1)),
            sg.Button("▶", key=f"-PIPE-RIGHT-{tag}-", size=(2, 1)),
            sg.Text("  "),
        ])
    return [sg.Frame("Pipeline", [row], expand_x=True)]


def _rebuild_pipeline_bar(window: sg.Window):
    """Rebuild pipeline bar after order/enable change. Simpler: just update checkboxes."""
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
_right_frozen = False         # independent freeze for right preview
_right_mouse_pos = None


def _build_preview_layout() -> list:
    """Build the Preview layout: Common Info + Left/Right previews + Status."""
    return [
        [sg.HorizontalSeparator()],
        [sg.Frame("Common Info", [
            [
                sg.Text("Display Size:", size=(12, 1)),
                sg.Input(
                    "", key="-DISPLAY-SIZE-", size=(48, 1),
                    readonly=True, border_width=0,
                    disabled_readonly_background_color=sg.theme_background_color(),
                    disabled_readonly_text_color=sg.theme_text_color(),
                ),
                sg.Text("Position:", size=(12, 1)),
                sg.Input(
                    "", key="-POSITION-INFO-", size=(48, 1),
                    readonly=True, border_width=0,
                    disabled_readonly_background_color=sg.theme_background_color(),
                    disabled_readonly_text_color=sg.theme_text_color(),
                ),
            ],
            [
                sg.Text("Input Pixel:", size=(12, 1)),
                sg.Input(
                    "", key="-INPUT-PIXEL-INFO-", size=(48, 1),
                    readonly=True, border_width=0,
                    disabled_readonly_background_color=sg.theme_background_color(),
                    disabled_readonly_text_color=sg.theme_text_color(),
                ),
                sg.Text("Output Pixel:", size=(12, 1)),
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
                [
                    sg.Checkbox("Show Input", key="-SHOW-INPUT-", default=False, enable_events=True),
                    sg.Push(),
                    sg.Button("Save Image", key="-SAVE-IMAGE-"),
                ],
            ], expand_x=True, expand_y=True),
            sg.Column([
                [
                    sg.Frame("Right Preview", [
                        [sg.Image(key="-RIGHT-PREVIEW-", background_color="gray")]
                    ], key="-RIGHT-PREVIEW-FRAME-", expand_x=True, expand_y=True),
                ],
            ], expand_y=True),
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
        y = data[0]
        cb = data[1] - (max_val / 2)
        cr = data[2] - (max_val / 2)
        r = np.clip(y + 1.5748 * cr, 0, max_val)
        g = np.clip(y - 0.187324 * cb - 0.468124 * cr, 0, max_val)
        b = np.clip(y + 1.8556 * cb, 0, max_val)
        rgb = np.stack([r, g, b], axis=0)
    else:
        rgb = data

    if depth > 8:
        rgb = (rgb >> (depth - 8))
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


def _update_left_preview(window: sg.Window, planar: np.ndarray, fmt: int, tag: str = ""):
    """Update the left preview area with new image data."""
    global _current_display_data, _scale_factor
    _current_display_data = (planar, fmt)
    img = _planar_to_rgb_pil(planar, fmt)
    w, h = img.size
    orig_h = planar.shape[1]
    _scale_factor = h / orig_h if orig_h > 0 else 1.0
    window["-LEFT-PREVIEW-"].update(data=_pil_to_bytes(img))
    window["-DISPLAY-SIZE-"].update(value=f"{w}x{h} (scale: {_scale_factor:.2f})")


def _update_right_preview(window: sg.Window, tag: str, snapshot: tuple, params: dict):
    """Update the right preview with module-specific image.

    The right preview image is height-matched to the left preview for
    consistent visual comparison.
    """
    global _right_display_data, _right_scale_factor
    mod = REGISTERED_MODULES.get(tag)
    if mod is None:
        window["-RIGHT-PREVIEW-"].update(data=b"")
        _right_display_data = None
        return
    getter = mod.get("get_right_preview_image")
    if getter is None:
        window["-RIGHT-PREVIEW-"].update(data=b"")
        _right_display_data = None
        return
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

        # Scale right preview to match left preview height
        left_img_h = _get_left_preview_height(window)
        if left_img_h is not None and left_img_h > 0:
            h_ratio = left_img_h / img.size[1]
            new_w = int(img.size[0] * h_ratio)
            img = img.resize((new_w, left_img_h), Image.LANCZOS if hasattr(Image, "LANCZOS") else Image.Resampling.LANCZOS)
            _right_scale_factor = h_ratio
        else:
            _right_scale_factor = 1.0

        # Store full planar data for right-preview pixel lookup if not already stored
        if _right_display_data is None and snapshot is not None and isinstance(snapshot, tuple) and len(snapshot) >= 2:
            _right_display_data = (snapshot[0], snapshot[1])

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
    """Load input file or generate set-color image into _INPUT_IMAGE cache. Returns True on success."""
    global _INPUT_IMAGE
    io_params = read_io_params(values)

    w = io_params["width"]
    h = io_params["height"]
    in_fmt = io_params["in_fmt"]
    in_clrspc = io_params["in_clrspc"]

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
        _INPUT_IMAGE = (data, in_fmt, in_clrspc)
        _SNAPSHOTS.clear()
        _update_status(window, f"Set color ({' '.join(str(v) for v in color_vals)}) applied", color="green")
        return True

    input_file = io_params["input_file"]
    if not input_file or not os.path.isfile(input_file):
        _update_status(window, "No input file selected", color="orange")
        return False

    expected_size = 0
    try:
        from csc.run_csc import get_frame_size
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

    _INPUT_IMAGE = (data, in_fmt, in_clrspc)
    _SNAPSHOTS.clear()
    _update_status(window, f"Loaded: {os.path.basename(input_file)}", color="green")
    return True


def _run_pipeline(values: dict, window: sg.Window, trigger_tag: str = ""):
    """Execute the pipeline. If trigger_tag is set, only re-run from that module."""
    global _INPUT_IMAGE

    io_params = read_io_params(values)

    # Determine whether to re-run from trigger_tag or from scratch
    start_tag = trigger_tag if trigger_tag else ""
    if start_tag:
        # Check if upstream snapshot exists
        upstream = _SNAPSHOTS.get(start_tag)
        if upstream is None:
            # Fall back to input
            start_tag = ""
        else:
            # Invalidate downstream if needed
            _invalidate_from(start_tag)

    if not start_tag:
        _SNAPSHOTS.clear()
        if not _load_input_image(values, window):
            return
        upstream = _INPUT_IMAGE

    effective = _get_effective_pipeline()
    if not effective:
        # No modules enabled, show input
        if _INPUT_IMAGE:
            _update_left_preview(window, _INPUT_IMAGE[0], _INPUT_IMAGE[1])
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

    current_data, current_fmt, current_clrspc = upstream
    out_fmt = io_params["out_fmt"]
    out_clrspc = io_params["out_clrspc"]
    output_dir = io_params["output_dir"] or os.path.dirname(io_params["input_file"]) or "."

    for i in range(start_idx, len(effective)):
        tag = effective[i]
        mod = REGISTERED_MODULES.get(tag)
        if mod is None:
            continue

        snap_key = tag
        if i > 0 and snap_key in _SNAPSHOTS:
            # Use cached upstream result
            current_data, current_fmt, current_clrspc = _SNAPSHOTS[snap_key]
            continue

        params = mod["read_params"](values)

        if tag == "csc":
            ok, result = mod["process"](
                current_data, current_fmt, current_clrspc,
                out_fmt, out_clrspc, params,
            )
            if ok:
                current_data = result
                current_fmt = out_fmt
                current_clrspc = out_clrspc
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
                current_data, current_fmt, current_clrspc,
                out_fmt, out_clrspc, params, full_io,
            )
            if ok:
                current_data = result
                current_fmt = res_fmt
                current_clrspc = res_clrspc
            else:
                _update_status(window, f"{tag.upper()} error: {result}", color="red")
                return

        _SNAPSHOTS[tag] = (current_data.copy(), current_fmt, current_clrspc)

    # Display final output
    final_tag = effective[-1] if effective else ""
    _update_status(window, f"Pipeline OK ({' → '.join(effective)})", color="green")
    _update_left_preview(window, current_data, current_fmt, final_tag)
    _update_right_preview(window, final_tag, (current_data, current_fmt, current_clrspc),
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
        in_planar, in_fmt, _ = _INPUT_IMAGE
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
        in_planar, in_fmt, _ = _INPUT_IMAGE
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
        display_str = f"{rws}x{rhs} (R-scale: {_right_scale_factor:.2f})"
    if not display_str and _current_display_data is not None:
        lhs, lws = _current_display_data[0].shape[1], _current_display_data[0].shape[2]
        display_str = f"{lws}x{lhs} (scale: {_scale_factor:.2f})"

    freeze_status = "[Frozen]" if _right_frozen else "[Space to freeze]"
    window["-POSITION-INFO-"].update(f"({orig_x:4d},{orig_y:4d}) R {freeze_status}")
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
    _update_right_preview(window, last_tag, snap, params)


def _save_current_image(values: dict, window: sg.Window):
    """Save the currently displayed left preview image to file."""
    if _current_display_data is None:
        _update_status(window, "No image to save", color="orange")
        return

    file_path = sg.popup_get_file(
        "Save Image", save_as=True,
        file_types=(("PNG", "*.png"), ("BMP", "*.bmp"), ("RAW YUV", "*.yuv"), ("RAW RGB", "*.rgb")),
    )
    if not file_path:
        return

    planar, fmt = _current_display_data
    ext = os.path.splitext(file_path)[1].lower()

    try:
        if ext in (".png", ".bmp"):
            img = _planar_to_rgb_pil(planar, fmt, max_size=99999)
            img.save(file_path)
        elif ext in (".yuv", ".rgb"):
            write_planar_to_raw(planar, file_path)
        else:
            _update_status(window, f"Unsupported format: {ext}", color="orange")
            return
        _update_status(window, f"Saved: {file_path}", color="green")
    except Exception as e:
        _update_status(window, f"Save error: {e}", color="red")


# ------------------------------------------------------------------ #
# Main                                                               #
# ------------------------------------------------------------------ #

def main():
    """Main entry point for PQ Verify Tool."""
    global _pixel_info_frozen, _mouse_pos, _scale_factor, _current_display_data, _right_scale_factor, _right_display_data, _right_frozen
    global _INPUT_IMAGE, pipeline_order, pipeline_enabled, _SNAPSHOTS

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
        _build_pipeline_bar(),
        [tab_group],
        *_build_preview_layout(),
    ]

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

        if event.startswith("-PIPE-LEFT-"):
            tag = event.replace("-PIPE-LEFT-", "").rstrip("-")
            idx = pipeline_order.index(tag)
            if idx > 0:
                pipeline_order[idx], pipeline_order[idx - 1] = \
                    pipeline_order[idx - 1], pipeline_order[idx]
                _rebuild_pipeline_bar(window)
                _SNAPSHOTS.clear()
                _run_pipeline(values, window)
            continue

        if event.startswith("-PIPE-RIGHT-"):
            tag = event.replace("-PIPE-RIGHT-", "").rstrip("-")
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

        # Space to freeze/unfreeze pixel info
        if event in (" ", "-LEFT-PREVIEW-SPACE-"):
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

        # Show Input checkbox
        if event == "-SHOW-INPUT-":
            if values["-SHOW-INPUT-"] and _INPUT_IMAGE is not None:
                _update_left_preview(window, _INPUT_IMAGE[0], _INPUT_IMAGE[1], "input")
            else:
                # Show last output
                effective = _get_effective_pipeline()
                if effective:
                    last = effective[-1]
                    snap = _SNAPSHOTS.get(last) or _INPUT_IMAGE
                    if snap:
                        _update_left_preview(window, snap[0], snap[1], last)
            continue

        # Save Image
        if event == "-SAVE-IMAGE-":
            _save_current_image(values, window)
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
    """Bind keyboard focus on slider widgets for DCI/SHP."""
    slider_keys = [
        "-CFHE-SLIDER-", "-BS-SLIDER-", "-WS-SLIDER-",
        "-CLAHE-R-SLIDER-", "-CLAHE-C-SLIDER-",
        "-SHP-PEAKING-GAIN-SLIDER-", "-SHP-CORING-THRESHOLD-SLIDER-",
        "-SHP-SHOOT-OVER-SLIDER-", "-SHP-SHOOT-UNDER-SLIDER-",
    ]
    for key in slider_keys:
        try:
            tk_widget = window[key].Widget
            tk_widget.bind("<Button-1>", lambda e, k=key: window[k].Widget.focus_set())
        except Exception:
            pass


if __name__ == "__main__":
    main()
