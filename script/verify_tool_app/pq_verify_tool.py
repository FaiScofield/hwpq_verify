"""
PQ Verify Tool - Unified module verification framework for ISP pipeline.

Supports multi-module pipeline serialization (CSC -> DCI -> SHP),
real-time parameter adjustment, and live image preview.

Entry point:  python pq_verify_tool.py
"""

import argparse
import io
import os
import re
import sys

# Ensure the parent script/ package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import PySimpleGUI as sg
from PIL import Image

LOGTAG = "PQTool"

from csc.run_csc import (
    is_yuv_format,
    is_rgb_format,
    get_pixel_depth,
    get_frame_size,
    read_raw_to_planar,
    write_planar_to_raw,
    FORMAT_NAMES,
    build_bcsh_config_from_dict,
    run_selected_algo,
)

from csc.get_csc_coef_hsv import (
    ALGO_RK_HW_CSC,
    normalize_algo_type,
)

from verify_tool_app.ui_io import (
    TAB_LABEL as IO_TAB_LABEL,
    FMT_DISPLAY,
    DEFAULT_FMT_DISPLAY,
    CLRSPC_DISPLAY_RGB,
    STB_IMAGE_EXTENSIONS,
    build_controls as build_io_controls,
    init_module as init_io_module,
    handle_io_event,
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
    right_preview_mouse_motion as csc_right_preview_mouse_motion,
    CSC_SUPPORT_IO_FORMATS,
)

from verify_tool_app.ui_dci import (
    TAB_LABEL as DCI_TAB_LABEL,
    build_controls as build_dci_controls,
    handle_dci_event,
    read_params as read_dci_params,
    process as process_dci,
    get_right_preview_image as dci_right_preview,
    DCI_SUPPORT_IO_FORMATS,
)

from verify_tool_app.ui_shp import (
    TAB_LABEL as SHP_TAB_LABEL,
    build_controls as build_shp_controls,
    handle_shp_event,
    read_params as read_shp_params,
    process as process_shp,
    get_right_preview_image as shp_right_preview,
    SHP_SUPPORT_IO_FORMATS,
)

from verify_tool_app.ui_helpers import (
    STATUS_ERROR, STATUS_OK, STATUS_WARNING,
    LINE, update_status,
)

# ------------------------------------------------------------------ #
# ImageFrame — pipeline data abstraction                             #
# ------------------------------------------------------------------ #

class ImageFrame:
    """Image frame abstraction for pipeline data.

    Encapsulates planar channels (pyr/pug/pvb), format, colorspace, and frame index.
    The three channels may have different resolutions for subsampled YUV formats:
      - YUV422P: pyr (H,W), pug (H,W/2), pvb (H,W/2)
      - YUV420P: pyr (H,W), pug (H/2,W/2), pvb (H/2,W/2)
    Internal format convention for pipeline processing:
      8/10-bit RGB    -> 0x2 (RGB_Planar)   / 0x12 (RGB_Planar_10LSB)
      8/10-bit YUV444 -> 0x3 (YUV444P_YU24) / 0x13 (YUV444P_10LSB)
      8/10-bit YUV422 -> 0x6 (YUV422P_YU16) / 0x16 (YUV422P_10LSB)
      8/10-bit YUV420 -> 0x8 (YUV420P_YU12) / 0x18 (YUV420P_10LSB)
    """

    __slots__ = ("pyr", "pug", "pvb", "fmt", "clrspc", "frame_idx")

    def __init__(self, pyr: np.ndarray, pug: np.ndarray, pvb: np.ndarray,
                 fmt: int, clrspc: int, frame_idx: int = 0):
        self.pyr = pyr          # Y or R channel (H, W)
        self.pug = pug          # U or G channel (H_uv, W_uv)
        self.pvb = pvb          # V or B channel (H_uv, W_uv)
        self.fmt = fmt          # format code: 0x2/0x3/0x6/0x8(+0x10)
        self.clrspc = clrspc    # colorspace code
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
        return int(self.pyr.shape[0])

    @property
    def width(self) -> int:
        return int(self.pyr.shape[1])

    @property
    def uv_height(self) -> int:
        """UV plane height (may differ from Y for YUV420)."""
        return int(self.pug.shape[0])

    @property
    def uv_width(self) -> int:
        """UV plane width (may differ from Y for YUV422/420)."""
        return int(self.pug.shape[1])

    # -- helpers ----------------------------------------------------- #

    def copy(self) -> "ImageFrame":
        """Shallow copy with a deep copy of the data arrays."""
        return ImageFrame(
            self.pyr.copy(), self.pug.copy(), self.pvb.copy(),
            self.fmt, self.clrspc, self.frame_idx,
        )

    def planar_data(self) -> np.ndarray:
        """Stack the three channels into a single (3, H, W) array.

        Requires all three channels to have the same spatial dimensions.
        Use for backwards-compatibility with legacy APIs.
        """
        return np.stack([self.pyr, self.pug, self.pvb], axis=0)

    def as_tuple(self) -> tuple:
        """Return (data, fmt, clrspc) for backward-compatible module API.

        WARNING: stacks channels — only valid when all channels share
        the same resolution (RGB, YUV444, or already upsampled).
        """
        return (self.planar_data(), self.fmt, self.clrspc)

    def _fmt_for_depth(self, target_10bit: bool) -> int:
        """Pick internal planar format code matching the YUV/RGB domain."""
        if self.is_rgb:
            return 0x12 if target_10bit else 0x2
        else:
            return 0x13 if target_10bit else 0x3

    # -- precision conversion ---------------------------------------- #

    def promote_to_10bit(self):
        """Promote 8-bit data to 10-bit by left-shifting 2 bits.

        Updates all three channels (uint8 -> uint16) and fmt (e.g. 0x2 -> 0x12).
        No-op if already 10-bit.
        """
        if self.depth >= 10:
            return self
        self.pyr = (self.pyr.astype(np.uint16) << 2)
        self.pug = (self.pug.astype(np.uint16) << 2)
        self.pvb = (self.pvb.astype(np.uint16) << 2)
        self.fmt |= 0x10 # change to 10-bit format
        return self

    def demote_to_8bit(self):
        """Demote 10-bit data to 8-bit with rounding (add 2 then >> 2).

        Updates all three channels (uint16 -> uint8) and fmt (e.g. 0x12 -> 0x2).
        No-op if already 8-bit.
        """
        if self.depth <= 8:
            return self
        for attr in ("pyr", "pug", "pvb"):
            ch = getattr(self, attr)
            rounded = (ch.astype(np.uint32) + 2) >> 2
            setattr(self, attr, np.clip(rounded, 0, 255).astype(np.uint8))
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

_MIN_PREVIEW_SIZE = 300


def _register_modules(modules=None):
    """Register selected modules.

    Args:
        modules: Iterable of module tags to register. If None, registers all.
    """
    global REGISTERED_MODULES, pipeline_order, pipeline_enabled
    all_modules = {
        "csc": {
            "tag": "csc",
            "label": CSC_TAB_LABEL,
            "build_controls": build_csc_controls,
            "read_params": read_csc_params,
            "process": process_csc,
            "get_right_preview_image": csc_right_preview,
            "right_preview_mouse_motion": csc_right_preview_mouse_motion,
            "handle_event": handle_csc_event,
            "init": lambda w: _init_module(w, "csc"),
            "supported_formats": CSC_SUPPORT_IO_FORMATS,
        },
        "dci": {
            "tag": "dci",
            "label": DCI_TAB_LABEL,
            "build_controls": build_dci_controls,
            "read_params": read_dci_params,
            "process": process_dci,
            "get_right_preview_image": dci_right_preview,
            "right_preview_mouse_motion": None,
            "handle_event": handle_dci_event,
            "init": lambda w: _init_module(w, "dci"),
            "supported_formats": DCI_SUPPORT_IO_FORMATS,
        },
        "shp": {
            "tag": "shp",
            "label": SHP_TAB_LABEL,
            "build_controls": build_shp_controls,
            "read_params": read_shp_params,
            "process": process_shp,
            "get_right_preview_image": shp_right_preview,
            "right_preview_mouse_motion": None,
            "handle_event": handle_shp_event,
            "init": lambda w: _init_module(w, "shp"),
            "supported_formats": SHP_SUPPORT_IO_FORMATS,
        },
    }

    if modules is not None:
        selected = set(modules)
        REGISTERED_MODULES = {tag: all_modules[tag] for tag in selected if tag in all_modules}
        pipeline_order = [tag for tag in pipeline_order if tag in selected]
        pipeline_enabled = {tag for tag in pipeline_enabled if tag in selected}
    else:
        REGISTERED_MODULES = dict(all_modules)


# ------------------------------------------------------------------ #
# Pipeline UI                                                        #
# ------------------------------------------------------------------ #

def _build_pipeline_bar() -> list:
    """Build the left-side vertical pipeline control bar."""
    tip_map = {
        "csc": "CSC: 色彩空间转换与BCSH校色",
        "dci": "DCI: 动态对比度增强",
        "shp": "SHP: 锐化处理",
    }
    rows = []
    for tag in pipeline_order:
        mod = REGISTERED_MODULES[tag]
        enabled = tag in pipeline_enabled
        row = [
            sg.Checkbox(
                mod["label"],
                default=enabled,
                key=f"-PIPE-ENABLE-{tag}-",
                enable_events=True,
                size=(4, 1),
                tooltip=tip_map.get(tag, f"启用/禁用 {mod['label']} 处理模块"),
            ),
        ]
        # CSC is always first, no position adjustment needed
        if tag != "csc":
            row.extend([
                sg.Button("▲", key=f"-PIPE-UP-{tag}-", size=(2, 1),
                          tooltip="上移此模块（调整Pipeline执行顺序）"),
                sg.Button("▼", key=f"-PIPE-DOWN-{tag}-", size=(2, 1),
                          tooltip="下移此模块（调整Pipeline执行顺序）"),
            ])
        rows.append(row)
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

    # Update stream format state based on module count
    _update_stream_format_state(window)


def _update_stream_format_state(window: sg.Window):
    """Enable/disable stream format control based on pipeline module count.

    Single-module pipeline: disable + clear (stream format is ignored).
    Multi-module pipeline: enable + set default if empty.
    """
    effective = _get_effective_pipeline()
    if len(effective) <= 1:
        window["-STREAM-FORMAT-"].update(value="", disabled=True)
    else:
        current = window["-STREAM-FORMAT-"].get()
        if not current:
            default = next(f for f in FMT_DISPLAY if f.startswith("0x13 "))
            window["-STREAM-FORMAT-"].update(value=default)
        window["-STREAM-FORMAT-"].update(disabled=False)


# ------------------------------------------------------------------ #
# Preview layout                                                     #
# ------------------------------------------------------------------ #

PREVIEW_MAX_HEIGHT = 400

# Mouse tracking state
_mouse_pos = None
_pixel_info_frozen = False
_scale_factor = 1.0
_right_scale_factor = 1.0
_OUTPUT_IMAGE: ImageFrame | None = None  # last pipeline output frame shown in left preview
_right_display_data = None    # (planar, fmt) currently shown in right preview
_right_input_data = None      # (planar, fmt) input data before right-side processing
_right_frozen = False         # independent freeze for right preview
_right_mouse_pos = None
_right_preview_tag: str = ""  # which module's right preview is currently shown
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
                    tooltip="当前左预览图像在窗口中的显示尺寸（宽×高）",
                ),
                sg.Text("Position", size=(12, 1)),
                sg.Input(
                    "", key="-POSITION-INFO-", size=(48, 1),
                    readonly=True, border_width=0,
                    disabled_readonly_background_color=sg.theme_background_color(),
                    disabled_readonly_text_color=sg.theme_text_color(),
                    tooltip="鼠标所在像素坐标及像素值信息；按空格键可冻结/解冻",
                ),
            ],
            [
                sg.Text("Input Pixel", size=(12, 1)),
                sg.Input(
                    "", key="-INPUT-PIXEL-INFO-", size=(48, 1),
                    readonly=True, border_width=0,
                    disabled_readonly_background_color=sg.theme_background_color(),
                    disabled_readonly_text_color=sg.theme_text_color(),
                    tooltip="输入图像在鼠标位置(R,G,B)像素值",
                ),
                sg.Text("Output Pixel", size=(12, 1)),
                sg.Input(
                    "", key="-OUTPUT-PIXEL-INFO-", size=(48, 1),
                    readonly=True, border_width=0,
                    disabled_readonly_background_color=sg.theme_background_color(),
                    disabled_readonly_text_color=sg.theme_text_color(),
                    tooltip="处理输出图像在鼠标位置的(R,G,B)像素值",
                ),
            ],
        ], expand_x=True)],
        [
            sg.Column([
                [
                    sg.Frame("Left Preview", [
                        [sg.Image(key="-LEFT-PREVIEW-", background_color="gray",
                                  tooltip="左预览区：显示Pipeline处理输出图像；鼠标悬停查看像素值，按空格冻结")]
                    ], key="-LEFT-PREVIEW-FRAME-", expand_x=True, expand_y=True),
                ],
            ], expand_x=True, expand_y=True),
            sg.Column([
                [
                    sg.Frame("Right Preview", [
                        [sg.Image(key="-RIGHT-PREVIEW-", background_color="gray",
                                  tooltip="右预览区：显示当前模块辅助分析图（CSC饱和度/色相图 或 DCI曲线图）；按空格冻结")]
                    ], key="-RIGHT-PREVIEW-FRAME-", expand_x=True, expand_y=True),
                ],
            ], expand_x=True, expand_y=True),
            sg.Column([
                [sg.Checkbox("Show Left Input", key="-SHOW-INPUT-", default=False,
                             enable_events=True,
                             tooltip="勾选后在左预览区显示原始输入图像")],
                [sg.Button("Save Left Image", key="-SAVE-LEFT-IMAGE-",
                           tooltip="保存左预览区图像到文件")],
                [sg.Checkbox("Show Right Input", key="-SHOW-RIGHT-INPUT-", default=False,
                             enable_events=True,
                             tooltip="勾选后在右预览区显示原始输入图像")],
                [sg.Button("Save Right Image", key="-SAVE-RIGHT-IMAGE-",
                           tooltip="保存右预览区图像到文件")],
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

def _planar_to_rgb_pil(frame: ImageFrame, max_size: int = PREVIEW_MAX_HEIGHT):
    """Convert an ImageFrame to a downscaled PIL RGB Image.

    For subsampled YUV formats, UV channels are upsampled to Y resolution.
    """
    fmt = frame.fmt
    depth = get_pixel_depth(fmt)
    pyr = frame.pyr.astype(np.float32)
    pug = frame.pug.astype(np.float32)
    pvb = frame.pvb.astype(np.float32)

    # Upsample UV channels to Y resolution if needed (YUV422/420)
    if is_yuv_format(fmt):
        y_h, y_w = frame.height, frame.width
        uv_h, uv_w = frame.uv_height, frame.uv_width
        if uv_h != y_h or uv_w != y_w:
            if uv_w != y_w:
                # Horizontal upsampling for YUV422
                pug = np.repeat(pug, y_w // uv_w, axis=1)
                pvb = np.repeat(pvb, y_w // uv_w, axis=1)
            if uv_h != y_h:
                # Vertical upsampling for YUV420
                pug = np.repeat(pug, y_h // uv_h, axis=0)
                pvb = np.repeat(pvb, y_h // uv_h, axis=0)

    if is_yuv_format(fmt):
        max_val = float((1 << depth) - 1)
        uv_half = 1 << (depth - 1)
        y = pyr
        cb = pug - uv_half
        cr = pvb - uv_half
        r = np.clip(y + 1.5748 * cr, 0, max_val)
        g = np.clip(y - 0.187324 * cb - 0.468124 * cr, 0, max_val)
        b = np.clip(y + 1.8556 * cb, 0, max_val)
        rgb = np.stack([r, g, b], axis=0)
    else:
        rgb = np.stack([pyr, pug, pvb], axis=0)

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


def _maybe_render_left_on_resize(window: sg.Window, fw: int, fh: int) -> bool:
    """Re-render left preview if frame size changed significantly. Returns True if re-rendered."""
    global _last_left_frame_size, _left_display_size
    last_w, last_h = _last_left_frame_size
    if abs(fw - last_w) < 15 and abs(fh - last_h) < 15:
        return False
    _last_left_frame_size = (fw, fh)
    if _OUTPUT_IMAGE is not None:
        # Avoid re-render cycle: if displayed image already fills at least
        # one dimension of the new frame size, layout is settling; skip.
        disp_w, disp_h = _left_display_size
        if disp_w > 0 and disp_h > 0:
            if abs(disp_w - fw) <= 15 or abs(disp_h - fh) <= 15:
                return False
        _update_left_preview(window, _OUTPUT_IMAGE, frame_w=fw, frame_h=fh)
        return True
    return False


def _update_left_preview(window: sg.Window, frame: ImageFrame, tag: str = "",
                         frame_w: int = None, frame_h: int = None):
    """Update the left preview area with new image data.

    Args:
        frame_w, frame_h: Pre-queried frame dimensions (from resize event).
            If None, queried via winfo.
    """
    global _OUTPUT_IMAGE, _scale_factor, _left_display_size, _last_left_frame_size
    _OUTPUT_IMAGE = frame

    orig_h, orig_w = frame.height, frame.width
    try:
        # Use cached frame dimensions when not explicitly provided to avoid
        # layout feedback loop when toggling between images of different AR.
        fh = frame_h if frame_h is not None else _last_left_frame_size[1]
        fw = frame_w if frame_w is not None else _last_left_frame_size[0]
        if fh <= 0 or fw <= 0:
            fh = window["-LEFT-PREVIEW-FRAME-"].Widget.winfo_height()
            fw = window["-LEFT-PREVIEW-FRAME-"].Widget.winfo_width()
            _last_left_frame_size = (fw, fh) if fw > 0 and fh > 0 else _last_left_frame_size
        if max(fh, fw) <= _MIN_PREVIEW_SIZE:
            max_size = _MIN_PREVIEW_SIZE
        else:
            # Constrain image to fit within both frame dimensions to prevent resize cascade
            w_ratio = fw / orig_w if orig_w > 0 else 1.0
            h_ratio = fh / orig_h if orig_h > 0 else 1.0
            ratio = min(w_ratio, h_ratio)
            max_size = int(ratio * max(orig_w, orig_h))
            max_size = max(max_size, _MIN_PREVIEW_SIZE) if _MIN_PREVIEW_SIZE > 0 else max_size
    except Exception:
        max_size = max(orig_w, orig_h)

    img = _planar_to_rgb_pil(frame, max_size)
    w, h = img.size
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
    global _right_display_data, _right_scale_factor, _right_input_data, _right_preview_tag
    _right_preview_tag = tag
    mod = REGISTERED_MODULES.get(tag)
    if mod is None:
        window["-RIGHT-PREVIEW-"].update(data=b"")
        _right_display_data = None
        _right_input_data = None
        _right_preview_tag = ""
        return
    getter = mod.get("get_right_preview_image")
    if getter is None:
        window["-RIGHT-PREVIEW-"].update(data=b"")
        _right_display_data = None
        _right_input_data = None
        _right_preview_tag = ""
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
            tmp_frame = ImageFrame(mapped_data[0], mapped_data[1], mapped_data[2],
                                   mapped_fmt, 0)
            img = _planar_to_rgb_pil(tmp_frame, max_size=99999)
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
    stream_fmt_str = values.get("-STREAM-FORMAT-", "")
    stream_fmt = get_fmt_from_display(stream_fmt_str) if stream_fmt_str else 0x13
    stream_10bit = (get_pixel_depth(stream_fmt) == 10)
    use_set_color = values.get("-USE-SET-COLOR-", False)

    if use_set_color:
        color_vals = _parse_color_input(values.get("-SET-COLOR-INPUT-", ""))
        if color_vals is None:
            update_status(window, LOGTAG, LINE(), "Invalid set-color input", level=STATUS_WARNING)
            return False
        depth = get_pixel_depth(in_fmt)
        max_val = (1 << depth) - 1
        dtype = np.uint16 if depth > 8 else np.uint8

        # Compute UV resolution for subsampled YUV formats
        if is_yuv_format(in_fmt):
            base = in_fmt & 0xF
            if base in (0x6, 0x7):
                uv_h, uv_w = h, w // 2      # YUV422
            elif base in (0x8, 0x9):
                uv_h, uv_w = h // 2, w // 2  # YUV420
            else:
                uv_h, uv_w = h, w            # YUV444
        else:
            uv_h, uv_w = h, w                # RGB

        pyr = np.full((h, w), int(np.clip(color_vals[0], 0, max_val)), dtype=dtype)
        pug = np.full((uv_h, uv_w), int(np.clip(color_vals[1], 0, max_val)), dtype=dtype)
        pvb = np.full((uv_h, uv_w), int(np.clip(color_vals[2], 0, max_val)), dtype=dtype)
        _INPUT_IMAGE = ImageFrame(pyr, pug, pvb, in_fmt, in_clrspc)
        _SNAPSHOTS.clear()
        if stream_10bit:
            _INPUT_IMAGE.promote_to_10bit()
        update_status(window, LOGTAG, LINE(), f"Set color ({' '.join(str(v) for v in color_vals)}) applied", level=STATUS_OK)
        return True

    # Read input files
    input_file = io_params["input_file"]
    if not input_file or not os.path.isfile(input_file):
        update_status(window, LOGTAG, LINE(), "No input file selected", level=STATUS_WARNING)
        return False

    # Handle image files (PNG/JPG/JPEG/BMP) via PIL, treat as RGB888
    ext = os.path.splitext(input_file)[1].lower()
    if ext in STB_IMAGE_EXTENSIONS:
        try:
            from PIL import Image as PILImage
            im = PILImage.open(input_file).convert("RGB")
            w, h = im.size
            arr = np.asarray(im)
            # Convert interleaved RGB (H, W, 3) to three planar channels
            pyr = arr[:, :, 0].astype(np.uint8)
            pug = arr[:, :, 1].astype(np.uint8)
            pvb = arr[:, :, 2].astype(np.uint8)
            im.close()
            # Update width/height on UI to match actual image dimensions
            window["-WIDTH-"].update(value=str(w))
            window["-HEIGHT-"].update(value=str(h))
            values["-WIDTH-"] = str(w)
            values["-HEIGHT-"] = str(h)
            _INPUT_IMAGE = ImageFrame(pyr, pug, pvb, 0x0, in_clrspc)
            _SNAPSHOTS.clear()
            if stream_10bit:
                _INPUT_IMAGE.promote_to_10bit()
            update_status(window, LOGTAG, LINE(), f"Loaded image: {os.path.basename(input_file)} ({w}x{h})", level=STATUS_OK)
            return True
        except Exception as e:
            update_status(window, LOGTAG, LINE(), f"Image read error: {e}", level=STATUS_ERROR)
            return False

    expected_size = 0
    try:
        expected_size = get_frame_size(w, h, in_fmt)
    except Exception:
        pass

    actual_size = os.path.getsize(input_file)
    if expected_size > 0 and actual_size < expected_size:
        update_status(window, LOGTAG, LINE(), "File too small for frame size", level=STATUS_WARNING)

    try:
        data, in_fmt = read_raw_to_planar(input_file, w, h, in_fmt, repeat_to_444=False)
    except Exception as e:
        update_status(window, LOGTAG, LINE(), f"Read error: {e}", level=STATUS_ERROR)
        return False

    _INPUT_IMAGE = ImageFrame(data[0], data[1], data[2], in_fmt, in_clrspc)
    _SNAPSHOTS.clear()
    if stream_10bit:
        _INPUT_IMAGE.promote_to_10bit()
    update_status(window, LOGTAG, LINE(), f"Loaded: {os.path.basename(input_file)}", level=STATUS_OK)
    return True


def _get_stream_clrspc(stream_fmt, in_fmt, in_clrspc, out_fmt, out_clrspc):
    """Determine colorspace for the stream format carrier.

    - RGB stream formats → always RGB_Full (1).
    - YUV stream formats:
      1. If input is YUV → Full-range variant of input colorspace.
      2. Else if output is YUV → Full-range variant of output colorspace.
      3. Otherwise → BT709_Full (5).
    """
    if is_rgb_format(stream_fmt):
        return 1  # RGB_Full
    # YUV stream format
    if is_yuv_format(in_fmt):
        # Full-range variant: Limited is even, Full is odd (Limited+1)
        return in_clrspc + 1 if in_clrspc % 2 == 0 else in_clrspc
    if is_yuv_format(out_fmt):
        return out_clrspc + 1 if out_clrspc % 2 == 0 else out_clrspc
    return 5  # BT709_Full


def _run_pipeline(window_elements: dict, window: sg.Window, trigger_tag: str = ""):
    """Execute the pipeline. If trigger_tag is set, only re-run from that module."""
    global _INPUT_IMAGE, _last_out_format, _last_out_frame_size

    io_params = read_io_params(window_elements)

    out_fmt = io_params["out_fmt"]
    out_clrspc = io_params["out_clrspc"]
    width = io_params["width"]
    height = io_params["height"]

    # Read stream format for multi-module pipeline carrier
    stream_fmt_str = window_elements.get("-STREAM-FORMAT-", "")
    stream_fmt = get_fmt_from_display(stream_fmt_str) if stream_fmt_str else 0x13
    stream_10bit = (get_pixel_depth(stream_fmt) == 10)
    stream_clrspc = _get_stream_clrspc(
        stream_fmt, io_params["in_fmt"], io_params["in_clrspc"], out_fmt, out_clrspc)

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
            if not _load_input_image(window_elements, window):
                return
        upstream = _INPUT_IMAGE

    effective = _get_effective_pipeline()
    if not effective:
        # No modules enabled, show input as-is
        if _INPUT_IMAGE is not None:
            _update_left_preview(window, _INPUT_IMAGE)
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
            if not _load_input_image(window_elements, window):
                return
            upstream = _INPUT_IMAGE

    if upstream is None:
        update_status(window, LOGTAG, LINE(), "No input data", level=STATUS_WARNING)
        return

    current_frame = upstream
    output_dir = io_params["output_dir"] or os.path.dirname(io_params["input_file"]) or "."

    # For multi-module pipeline, convert input to stream format via CSC
    # Skip if CSC is already the first module (user intends CSC to handle it)
    if len(effective) >= 2 and current_frame.fmt != stream_fmt and effective[0] != "csc":
        try:
            orig_fmt = current_frame.fmt
            in_depth = get_pixel_depth(current_frame.fmt)
            s_depth = get_pixel_depth(stream_fmt)
            pixel_depth = max(in_depth, s_depth)
            algo_type = normalize_algo_type(ALGO_RK_HW_CSC)
            bcsh_config = build_bcsh_config_from_dict({
                "brightness": 256, "contrast": 256,
                "saturation": 256, "hue": 256,
                "r_gain": 256, "r_offset": 256,
                "g_gain": 256, "g_offset": 256,
                "b_gain": 256, "b_offset": 256,
            }, algo_type)
            input_data = np.stack([current_frame.pyr, current_frame.pug, current_frame.pvb], axis=0)
            output_data, _, _, _, _ = run_selected_algo(
                input_data, bcsh_config, pixel_depth, 10,
                algo_type, current_frame.clrspc, stream_clrspc,
                current_frame.fmt, stream_fmt,
            )
            current_frame = ImageFrame(output_data[0], output_data[1], output_data[2],
                                      stream_fmt, stream_clrspc)
            update_status(window, LOGTAG, LINE(),
                f"Stream-fmt converted: 0x{orig_fmt:x} → 0x{stream_fmt:x}", level=STATUS_OK)
        except Exception as e:
            update_status(window, LOGTAG, LINE(),
                f"Stream-fmt conversion failed: {e}", level=STATUS_ERROR)
            return

    for i in range(start_idx, len(effective)):
        tag = effective[i]
        mod = REGISTERED_MODULES.get(tag)
        if mod is None:
            update_status(window, LOGTAG, LINE(), f"Module '{tag}' not registered", level=STATUS_WARNING)
            continue

        snap_key = tag
        if i > 0 and snap_key in _SNAPSHOTS:
            # Use cached upstream result
            current_frame = _SNAPSHOTS[snap_key]
            continue

        # Validate input format and determine per-module output
        supported_formats = mod.get("supported_formats", {})
        cur_fmt = current_frame.fmt
        if cur_fmt not in supported_formats:
            update_status(window, LOGTAG, LINE(),
                f"{tag}: unsupported input format 0x{cur_fmt:x}", level=STATUS_ERROR)
            return
        supported_outputs = supported_formats[cur_fmt]

        is_last = (i == len(effective) - 1)
        if len(effective) >= 2:
            # Multi-module pipeline: all modules output stream_fmt
            # Final format conversion is handled post-loop via CSC
            if stream_fmt not in supported_outputs:
                update_status(window, LOGTAG, LINE(),
                    f"{tag}: stream-fmt 0x{stream_fmt:x} not in supported outputs "
                    f"(supports: {[f'0x{f:x}' for f in supported_outputs]})",
                    level=STATUS_ERROR)
                return
            module_out_fmt = stream_fmt
            module_out_clrspc = stream_clrspc
        else:
            # Single-module pipeline: use I/O tab's output format directly
            module_out_fmt = out_fmt
            module_out_clrspc = out_clrspc
            if module_out_fmt not in supported_outputs:
                update_status(window, LOGTAG, LINE(),
                    f"I/O output 0x{module_out_fmt:x} not supported "
                    f"(supports: {[f'0x{f:x}' for f in supported_outputs]})",
                    level=STATUS_ERROR)
                return

        io_info = {
            "out_fmt": module_out_fmt,
            "out_clrspc": module_out_clrspc,
            "width": io_params["width"],
            "height": io_params["height"],
            "frame_idx": io_params["frame_idx"],
            "frame_num": io_params["frame_num"],
            "output_dir": output_dir,
            "config_path": io_params["config_path"],
            "elements": window_elements,
            "window": window,
        }

        ok, result = mod["process"](current_frame, io_info)
        if ok:
            current_frame = result  # result is an ImageFrame
        else:
            update_status(window, LOGTAG, LINE(), f"{tag.upper()} error: {result}", level=STATUS_ERROR)
            return

        _SNAPSHOTS[tag] = current_frame.copy()

    # Post-loop: for multi-module pipeline, convert to I/O tab's output format if different
    if len(effective) >= 2 and current_frame.fmt != out_fmt:
        try:
            orig_fmt = current_frame.fmt
            in_depth = get_pixel_depth(current_frame.fmt)
            o_depth = get_pixel_depth(out_fmt)
            pixel_depth = max(in_depth, o_depth)
            algo_type = normalize_algo_type(ALGO_RK_HW_CSC)
            bcsh_config = build_bcsh_config_from_dict({
                "brightness": 256, "contrast": 256,
                "saturation": 256, "hue": 256,
                "r_gain": 256, "r_offset": 256,
                "g_gain": 256, "g_offset": 256,
                "b_gain": 256, "b_offset": 256,
            }, algo_type)
            input_data = np.stack([current_frame.pyr, current_frame.pug, current_frame.pvb], axis=0)
            output_data, _, _, _, _ = run_selected_algo(
                input_data, bcsh_config, pixel_depth, 10,
                algo_type, current_frame.clrspc, out_clrspc,
                current_frame.fmt, out_fmt,
            )
            current_frame = ImageFrame(output_data[0], output_data[1], output_data[2],
                                      out_fmt, out_clrspc)
            update_status(window, LOGTAG, LINE(),
                f"Output-fmt converted: 0x{orig_fmt:x} → 0x{out_fmt:x}", level=STATUS_OK)
        except Exception as e:
            update_status(window, LOGTAG, LINE(),
                f"Output-fmt conversion failed: {e}", level=STATUS_ERROR)
            return

    # Display final output
    final_tag = effective[-1] if effective else ""
    update_status(window, LOGTAG, LINE(), f"Pipeline OK ({' → '.join(effective)})", level=STATUS_OK)
    _update_left_preview(window, current_frame, final_tag)
    _update_right_preview(window, final_tag, current_frame.as_tuple(),
                          REGISTERED_MODULES.get(final_tag, {}).get("read_params", lambda v: {})(window_elements))


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
        in_fmt = _INPUT_IMAGE.fmt
        in_h, in_w = _INPUT_IMAGE.height, _INPUT_IMAGE.width
        uv_h, uv_w = _INPUT_IMAGE.uv_height, _INPUT_IMAGE.uv_width
        if 0 <= orig_x < in_w and 0 <= orig_y < in_h:
            p0 = _INPUT_IMAGE.pyr[orig_y, orig_x]
            # Handle subsampled UV coordinates for YUV422/420
            uv_x = orig_x * uv_w // in_w if uv_w != in_w else orig_x
            uv_y = orig_y * uv_h // in_h if uv_h != in_h else orig_y
            p1 = _INPUT_IMAGE.pug[uv_y, uv_x]
            p2 = _INPUT_IMAGE.pvb[uv_y, uv_x]
            fmt_label = "yuv" if is_yuv_format(in_fmt) else "rgb"
            input_str = f"{fmt_label}-{in_fmt:#x}: ({p0:4d}, {p1:4d}, {p2:4d})"

    # Get output pixel
    output_str = "(----, ----, ----)"
    if _OUTPUT_IMAGE is not None:
        out_fmt = _OUTPUT_IMAGE.fmt
        out_h, out_w = _OUTPUT_IMAGE.height, _OUTPUT_IMAGE.width
        uv_h, uv_w = _OUTPUT_IMAGE.uv_height, _OUTPUT_IMAGE.uv_width
        if 0 <= orig_x < out_w and 0 <= orig_y < out_h:
            p0 = _OUTPUT_IMAGE.pyr[orig_y, orig_x]
            uv_x = orig_x * uv_w // out_w if uv_w != out_w else orig_x
            uv_y = orig_y * uv_h // out_h if uv_h != out_h else orig_y
            p1 = _OUTPUT_IMAGE.pug[uv_y, uv_x]
            p2 = _OUTPUT_IMAGE.pvb[uv_y, uv_x]
            # Use I/O output format for the label, not the displayed data format
            io_out_fmt = get_fmt_from_display(values.get("-OUT-FMT-", DEFAULT_FMT_DISPLAY))
            fmt_label = "yuv" if is_yuv_format(io_out_fmt) else "rgb"
            output_str = f"{fmt_label}-{io_out_fmt:#x}: ({p0:4d}, {p1:4d}, {p2:4d})"

    freeze_status = "[Frozen]" if _pixel_info_frozen else "[Space to freeze]"
    window["-POSITION-INFO-"].update(f"({orig_x:4d},{orig_y:4d}) {freeze_status}")
    window["-INPUT-PIXEL-INFO-"].update(input_str)
    window["-OUTPUT-PIXEL-INFO-"].update(output_str)


def _handle_right_mouse_motion(window: sg.Window, values: dict, event: str):
    """Handle mouse motion over right preview to update pixel info.

    If the current right-preview module provides right_preview_mouse_motion,
    delegates to it with image-center coordinates (0,0 = center, right/up positive).
    Otherwise falls back to default pixel inspector.
    """
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

    # Delegate to module-specific handler if available
    if _right_preview_tag:
        mod = REGISTERED_MODULES.get(_right_preview_tag)
        if mod is not None:
            handler = mod.get("right_preview_mouse_motion")
            if handler is not None:
                # Compute image-center coordinates (0,0=center, right/up positive)
                rdh = _right_display_data
                if rdh is not None:
                    img_h, img_w = rdh[0].shape[1], rdh[0].shape[2]
                    cx = orig_x - img_w // 2
                    cy = img_h // 2 - orig_y
                    handler(cx, cy, window, values)
                return

    # Default pixel inspector fallback
    # Get input pixel from input image
    input_str = "(----, ----, ----)"
    if _INPUT_IMAGE is not None:
        in_fmt = _INPUT_IMAGE.fmt
        in_h, in_w = _INPUT_IMAGE.height, _INPUT_IMAGE.width
        uv_h, uv_w = _INPUT_IMAGE.uv_height, _INPUT_IMAGE.uv_width
        if 0 <= orig_x < in_w and 0 <= orig_y < in_h:
            p0 = _INPUT_IMAGE.pyr[orig_y, orig_x]
            uv_x = orig_x * uv_w // in_w if uv_w != in_w else orig_x
            uv_y = orig_y * uv_h // in_h if uv_h != in_h else orig_y
            p1 = _INPUT_IMAGE.pug[uv_y, uv_x]
            p2 = _INPUT_IMAGE.pvb[uv_y, uv_x]
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
    if not display_str and _OUTPUT_IMAGE is not None:
        lh, lw = _OUTPUT_IMAGE.height, _OUTPUT_IMAGE.width
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
    window["-POSITION-INFO-"].update("(hover over image)")
    window["-INPUT-PIXEL-INFO-"].update("")
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


def _save_image(values: dict, window: sg.Window, frame: ImageFrame | None):
    """Save the given ImageFrame to file."""
    if frame is None:
        update_status(window, LOGTAG, LINE(), "No image to save", level=STATUS_WARNING)
        return

    file_path = sg.popup_get_file(
        "Save Image", save_as=True,
        file_types=(("PNG", "*.png"), ("BMP", "*.bmp"), ("RAW YUV", "*.yuv"), ("RAW RGB", "*.rgb")),
    )
    if not file_path:
        return

    ext = os.path.splitext(file_path)[1].lower()

    try:
        if ext in (".png", ".bmp"):
            img = _planar_to_rgb_pil(frame, max_size=99999)
            img.save(file_path)
        elif ext in (".yuv", ".rgb"):
            width = int(values.get("-WIDTH-", "1920"))
            height = int(values.get("-HEIGHT-", "1080"))
            planar = frame.planar_data()
            write_planar_to_raw(planar, file_path, width, height, frame.fmt)
        else:
            update_status(window, LOGTAG, LINE(), f"Unsupported format: {ext}", level=STATUS_WARNING)
            return
        update_status(window, LOGTAG, LINE(), f"Saved: {file_path}", level=STATUS_OK)
    except Exception as e:
        update_status(window, LOGTAG, LINE(), f"Save error: {e}", level=STATUS_ERROR)


def _update_right_preview_with_snapshot(window: sg.Window, frame: ImageFrame):
    """Update right preview directly with the given ImageFrame (for Show Right Input)."""
    global _right_display_data, _right_scale_factor
    _right_display_data = (frame.planar_data(), frame.fmt)
    img = _planar_to_rgb_pil(frame, max_size=99999)
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
    global _pixel_info_frozen, _mouse_pos, _scale_factor, _OUTPUT_IMAGE, _right_scale_factor, _right_display_data, _right_input_data, _right_frozen
    global _left_display_size, _INPUT_IMAGE, _last_out_format, _last_out_frame_size, pipeline_order, pipeline_enabled, _SNAPSHOTS

    # Parse command-line arguments for module selection
    parser = argparse.ArgumentParser(description="PQ Verify Tool - ISP Pipeline Verification")
    parser.add_argument("--all", action="store_true", help="register all modules")
    parser.add_argument("--csc", action="store_true", help="register CSC module")
    parser.add_argument("--dci", action="store_true", help="register DCI module")
    parser.add_argument("--shp", action="store_true", help="register SHP module")
    parser.add_argument("--disable-pipeline", action="store_true", help="hide pipeline bar and dump checkbox")
    args = parser.parse_args()

    # Determine which modules to register
    if args.all:
        _register_modules()  # register all
    elif any([args.csc, args.dci, args.shp]):
        selected = []
        if args.csc:
            selected.append("csc")
        if args.dci:
            selected.append("dci")
        if args.shp:
            selected.append("shp")
        _register_modules(selected)
    else:
        _register_modules()  # default: register all

    sg.theme("SystemDefault")

    # Build tab layout dynamically based on registered modules
    tabs = [sg.Tab(IO_TAB_LABEL, build_io_controls())]
    for tag in pipeline_order:
        mod = REGISTERED_MODULES[tag]
        tabs.append(sg.Tab(mod["label"], mod["build_controls"]()))
    tab_group = sg.TabGroup([tabs], expand_x=True, key="-TAB-GROUP-")

    # Build full layout
    if args.disable_pipeline:
        layout = [
            [tab_group],
            *_build_preview_layout(),
        ]
    else:
        layout = [
            [
                sg.Column([
                    _build_pipeline_bar(),
                    [sg.Checkbox("dump", key="-DUMP-", default=False,
                                 tooltip="保存各模块处理结果到输出目录")],
                ], vertical_alignment="top"),
                tab_group,
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
        print_event_values=False,
        size=(1300, 900),
    )
    # focus window when opened
    window.TKroot.attributes('-topmost', True)
    window.TKroot.lift()
    window.TKroot.focus_force()
    window.TKroot.after(100, lambda: window.TKroot.attributes('-topmost', False))

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

    # Initialize registered modules (bind events + norm labels)
    init_io_module(window)
    for tag in pipeline_order:
        REGISTERED_MODULES[tag]["init"](window)

    # Initialize stream format UI state based on current pipeline
    _update_stream_format_state(window)

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
            _update_stream_format_state(window)
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
                _update_left_preview(window, _INPUT_IMAGE, "input")
            else:
                # Show last output
                effective = _get_effective_pipeline()
                if effective:
                    last = effective[-1]
                    snap = _SNAPSHOTS.get(last) or _INPUT_IMAGE
                    if snap:
                        _update_left_preview(window, snap, last)
            continue

        # Show Right Input checkbox
        if event == "-SHOW-RIGHT-INPUT-":
            if values["-SHOW-RIGHT-INPUT-"] and _right_input_data is not None:
                r_data, r_fmt = _right_input_data
                if r_data is not None:
                    tmp_frame = ImageFrame(r_data[0], r_data[1], r_data[2], r_fmt, 0)
                    _update_right_preview_with_snapshot(window, tmp_frame)
            else:
                # Refresh right preview from pipeline
                _refresh_right_preview_only(window, values)
            continue

        # Save Left Image
        if event == "-SAVE-LEFT-IMAGE-":
            _save_image(values, window, _OUTPUT_IMAGE)
            continue

        # Save Right Image
        if event == "-SAVE-RIGHT-IMAGE-":
            if _right_display_data is not None:
                r_data, r_fmt = _right_display_data
                tmp_frame = ImageFrame(r_data[0], r_data[1], r_data[2], r_fmt, 0)
                _save_image(values, window, tmp_frame)
            continue

        # Stream format changed — reload input and re-run pipeline
        if event == "-STREAM-FORMAT-":
            _SNAPSHOTS.clear()
            _run_pipeline(values, window)
            continue

        # Load DCI config to UI when config path changes via FileBrowse
        if event == "-BROWSE-CONFIG-":
            from verify_tool_app.ui_dci import _load_dci_config_to_ui
            config_path = values.get("-CONFIG-PATH-", "").strip()
            if config_path:
                _load_dci_config_to_ui(window, values, config_path)

        # IO events
        if handle_io_event(event, values, window):
            if not event.startswith("-OPEN-DIR-"):
                _run_pipeline(values, window)
            continue

        # CSC events
        if handle_csc_event(event, values, window):
            if event not in ("-SAT-SET-COLOR-", "-CSC-SAVE-CFG-"):
                _run_pipeline(values, window, trigger_tag="csc")
            continue

        # DCI events
        if handle_dci_event(event, values, window):
            # UI-only events: don't trigger pipeline re-run
            if event not in ("-DCI-OPEN-EXE-DIR-", "-DCI-OPEN-AUDIT-DIR-", "-DCI-AUDIT-DIR-", "-DCI-SAVE-CFG-"):
                if not event.endswith("-RESET-"):
                    _run_pipeline(values, window, trigger_tag="dci")
            # Refresh right preview for COMBO MEDIAN or audit dir changes
            if event in ("-DCI-COMBO-MEDIAN-", "-DCI-AUDIT-DIR-"):
                _refresh_right_preview_only(window, values)
            continue

        # SHP events
        if handle_shp_event(event, values, window):
            if event != "-SHP-SAVE-CFG-":
                _run_pipeline(values, window, trigger_tag="shp")
            continue

    window.close()


def _init_module(window: sg.Window, tag: str):
    """Initialize a registered module: bind keyboard events and sync norm labels."""
    from verify_tool_app.ui_helpers import sync_all_norms

    if tag == "csc":
        from verify_tool_app.ui_csc import bind_keyboard_events, CSC_SLIDER_SPIN_PAIRS
        bind_keyboard_events(window)
        sync_all_norms(window, {}, CSC_SLIDER_SPIN_PAIRS)
    elif tag == "dci":
        from verify_tool_app.ui_dci import bind_keyboard_events, DCI_SLIDER_SPIN_PAIRS, _load_dci_config_to_ui
        bind_keyboard_events(window)
        sync_all_norms(window, {}, DCI_SLIDER_SPIN_PAIRS)
        # Load DCI config from default config path on initialization
        config_path = window["-CONFIG-PATH-"].get().strip()
        if config_path:
            _load_dci_config_to_ui(window, {}, config_path)
    elif tag == "shp":
        from verify_tool_app.ui_shp import bind_keyboard_events, SHP_SLIDER_SPIN_PAIRS
        bind_keyboard_events(window)
        sync_all_norms(window, {}, SHP_SLIDER_SPIN_PAIRS)


if __name__ == "__main__":
    main()
