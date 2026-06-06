"""
CSC module tab for PQ Test Tool.

Provides colorspace conversion controls (BCSH, Algo Type, Precision),
Sat/Hue test panel, and CSC processing logic.
References csc/csc_ui.py and csc/run_csc.py implementations.
"""

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
import PySimpleGUI as sg

from get_csc_coef_hsv import (
    ALGO_RK_HW_CSC,
    ALGO_RK_SW_CSC,
    ALGO_EVIDEO_CSC,
    ALGO_EVIDEO_CSC_PLAN_A,
    ALGO_EVIDEO_CSC_PLAN_B,
    normalize_algo_type,
)
from csc.run_csc import (
    build_bcsh_config_from_dict,
    run_selected_algo,
    get_pixel_depth,
    get_default_bcsh_raw_values,
)

from csc.csc_ui import (
    get_bcsh_norm_value,
    remap_rgb_gain_value_for_algo_switch,
    RGB_GAIN_KEYS,
)

TAB_LABEL = "CSC"

# ------------------------------------------------------------------ #
# Data model                                                         #
# ------------------------------------------------------------------ #

BCSH_KEYS = ["bright", "contrast", "sat", "hue",
             "r_gain", "r_offset", "g_gain", "g_offset", "b_gain", "b_offset"]

BCSH_DEFAULT = {
    "bright": 256, "contrast": 256, "sat": 256, "hue": 256,
    "r_gain": 256, "r_offset": 256,
    "g_gain": 256, "g_offset": 256,
    "b_gain": 256, "b_offset": 256,
}

CHANNEL_SWAP_TYPES = ["None", "V1_SWAP", "V2_Y2R_R2R", "V2_R2Y_R2R", "V2_Y2R_Y2Y"]

PRECISION_VALUES = [0] + list(range(8, 17))

ALGO_TYPE_OPTIONS = [
    ALGO_RK_HW_CSC,
    ALGO_RK_SW_CSC,
    ALGO_EVIDEO_CSC,
    ALGO_EVIDEO_CSC_PLAN_A,
    ALGO_EVIDEO_CSC_PLAN_B,
]

BCSH_NAMES = [
    ("Brightness", "bright", "Contrast:", "contrast"),
    ("Saturation", "sat", "Hue", "hue"),
    ("R Gain", "r_gain", "R Offset", "r_offset"),
    ("G Gain", "g_gain", "G Offset", "g_offset"),
    ("B Gain", "b_gain", "B Offset", "b_offset"),
]


# ------------------------------------------------------------------ #
# Colormap helpers (referenced from csc_ui.py)                       #
# ------------------------------------------------------------------ #

SAT_COLORMAP_SIZE = 416  # effective image area size (px)
SAT_MARGIN = 48          # border margin for axes/labels
_DATA_RANGE_MAX = 128    # max data value, range is [-128, 127] or [-128, 128]
_DATA_SIZE = 256         # total data range size


def _load_font(size):
    """Load a font for colormap axis labels."""
    font_path = Path(__file__).resolve().parents[2] / "data" / "fonts" / "NotoSans-Regular.ttf"
    try:
        from PIL import ImageFont
        return ImageFont.truetype(str(font_path), size)
    except Exception:
        return None


def _data_to_pix(val):
    """Map a float data value in [-128, 128] to pixel coordinate [0, SAT_COLORMAP_SIZE-1]."""
    return int(round((val + _DATA_RANGE_MAX) * SAT_COLORMAP_SIZE / _DATA_SIZE))


def _pix_to_data(pix):
    """Map pixel [0, SIZE-1] to continuous float data value in [-128, 127.5]."""
    return pix * _DATA_SIZE / SAT_COLORMAP_SIZE - _DATA_RANGE_MAX


def _ycbcr2rgb(y, cb, cr):
    """Convert YCbCr to RGB (BT.709), returns 0-255 uint8 arrays."""
    ycbcr = np.stack([np.asarray(y, dtype=np.float32),
                       np.asarray(cb, dtype=np.float32),
                       np.asarray(cr, dtype=np.float32)], axis=-1)
    g_y2r = np.array([[1.0, 0.0, 1.5748], [1.0, -0.187324, -0.468124], [1.0, 1.8556, 0.0]], dtype=np.float32)
    rgb = np.dot(ycbcr.reshape(-1, 3), g_y2r.T).reshape(ycbcr.shape)
    r = np.clip(rgb[..., 0] + 0.5, 0, 255).astype(np.uint8)
    g = np.clip(rgb[..., 1] + 0.5, 0, 255).astype(np.uint8)
    b = np.clip(rgb[..., 2] + 0.5, 0, 255).astype(np.uint8)
    return r, g, b


def _rgb2hsv(r, g, b):
    """Convert RGB (0-255) to HSV, returns h(0-360), s(0-1), v(0-1)."""
    r = np.asarray(r, dtype=np.float32) / 255.0
    g = np.asarray(g, dtype=np.float32) / 255.0
    b = np.asarray(b, dtype=np.float32) / 255.0
    maxc = np.maximum(np.maximum(r, g), b)
    minc = np.minimum(np.minimum(r, g), b)
    delta = maxc - minc
    h = np.zeros_like(maxc)
    cond = delta != 0
    rc = np.where(cond, (maxc - r) / delta, 0)
    gc = np.where(cond, (maxc - g) / delta, 0)
    bc = np.where(cond, (maxc - b) / delta, 0)
    h = np.where(cond & (maxc == r), bc - gc, h)
    h = np.where(cond & (maxc == g), 2.0 + rc - bc, h)
    h = np.where(cond & (maxc == b), 4.0 + gc - rc, h)
    h = (h / 6.0) % 1.0 * 360.0
    s = np.where(maxc != 0, delta / maxc, 0.0)
    v = maxc
    return h, s, v


def _hsv2rgb(h, s, v):
    """Convert HSV to RGB, returns 0-255 uint8 arrays."""
    h = np.asarray(h, dtype=np.float32) % 360
    s = np.asarray(s, dtype=np.float32)
    v = np.asarray(v, dtype=np.float32)
    c = v * s
    x = c * (1 - np.abs((h / 60) % 2 - 1))
    m = v - c
    r = np.zeros_like(h)
    g = np.zeros_like(h)
    b = np.zeros_like(h)
    for lo, hi, rc, gc, bc in [(0, 60, c, x, 0), (60, 120, x, c, 0), (120, 180, 0, c, x),
                                (180, 240, 0, x, c), (240, 300, x, 0, c), (300, 360, c, 0, x)]:
        mask = (h >= lo) & (h < hi)
        r[mask] = rc[mask] if isinstance(rc, np.ndarray) else rc
        g[mask] = gc[mask] if isinstance(gc, np.ndarray) else gc
        b[mask] = bc[mask] if isinstance(bc, np.ndarray) else bc
    r = np.clip((r + m) * 255 + 0.5, 0, 255).astype(np.uint8)
    g = np.clip((g + m) * 255 + 0.5, 0, 255).astype(np.uint8)
    b = np.clip((b + m) * 255 + 0.5, 0, 255).astype(np.uint8)
    return r, g, b


def _build_colormap_yuv(luma_val):
    """Build YCbCr->RGB colormap for a fixed luma value. Returns PIL Image."""
    w, h_img = SAT_COLORMAP_SIZE, SAT_COLORMAP_SIZE
    cb_grid = _pix_to_data(np.tile(np.arange(w, dtype=np.float32), (h_img, 1)))
    cr_grid = _pix_to_data(np.tile(np.arange(h_img - 1, -1, -1, dtype=np.float32).reshape(-1, 1), (1, w)))
    y = np.full((h_img, w), float(luma_val), dtype=np.float32)
    r, g, b = _ycbcr2rgb(y, cb_grid, cr_grid)
    return Image.fromarray(np.stack([r, g, b], axis=-1), 'RGB')


def _build_colormap_rgb(value_val):
    """Build HSV->RGB colormap for a fixed V value. Returns PIL Image."""
    w, h_img = SAT_COLORMAP_SIZE, SAT_COLORMAP_SIZE
    pix_x = np.tile(np.arange(w, dtype=np.float32), (h_img, 1))
    pix_y = np.tile(np.arange(h_img - 1, -1, -1, dtype=np.float32).reshape(-1, 1), (1, w))
    cx = _pix_to_data(pix_x) / _DATA_RANGE_MAX
    cy = _pix_to_data(pix_y) / _DATA_RANGE_MAX
    h = (np.arctan2(cy, cx) * 180.0 / np.pi + 360.0) % 360.0
    s = np.sqrt(cx ** 2 + cy ** 2)
    v = np.full((h_img, w), float(value_val) / 255.0, dtype=np.float32)
    r, g, b = _hsv2rgb(h, s, v)
    mask = s > 1.0
    r[mask], g[mask], b[mask] = 220, 220, 220
    return Image.fromarray(np.stack([r, g, b], axis=-1), 'RGB')


def _build_colormap_with_axis(img_eff, title, xlabel, ylabel):
    """Add margin and axes to a colormap PIL Image. Returns (padded_img, margin_size)."""
    margin = SAT_MARGIN
    w, h_img = img_eff.size
    total_w, total_h = w + 2 * margin, h_img + 2 * margin
    padded = Image.new('RGB', (total_w, total_h), (255, 255, 255))
    padded.paste(img_eff, (margin, margin))
    draw = ImageDraw.Draw(padded)
    font = _load_font(16)
    axis_color = (0, 0, 0)
    tick_color = (64, 64, 64)
    # Origin at center of effective area
    cx0 = _data_to_pix(0)
    cy0 = _data_to_pix(0)
    x0 = margin + cx0
    y0 = margin + (SAT_COLORMAP_SIZE - 1) - cy0
    # Axes
    draw.line([(margin, y0), (total_w - margin, y0)], fill=axis_color, width=2)
    draw.line([(x0, margin), (x0, total_h - margin)], fill=axis_color, width=2)
    # Ticks
    tick_data_vals = [-128, -96, -64, -32, 0, 32, 64, 96]
    for dv in tick_data_vals:
        x = margin + _data_to_pix(dv)
        draw.line([(x, y0 - 4), (x, y0 + 4)], fill=tick_color, width=1)
        if font and dv != 0:
            draw.text((x + 3, y0 + 5), str(dv), fill=tick_color, font=font)
        y = margin + (SAT_COLORMAP_SIZE - 1) - _data_to_pix(dv)
        draw.line([(x0 - 4, y), (x0 + 4, y)], fill=tick_color, width=1)
        if font and dv != 0:
            draw.text((x0 - 30, y - 8), str(dv), fill=tick_color, font=font)
    # Labels
    if font:
        draw.text((total_w - margin + 8, y0 - 10), xlabel, fill=axis_color, font=font)
        draw.text((x0 + 5, margin - 22), ylabel, fill=axis_color, font=font)
        bbox = draw.textbbox((0, 0), title, font=font)
        tw = bbox[2] - bbox[0]
        draw.text((total_w // 2 - tw // 2, 4), title, fill=axis_color, font=font)
    return padded, margin


# ------------------------------------------------------------------ #
# Layout                                                             #
# ------------------------------------------------------------------ #

def _build_bcsh_layout() -> list:
    """Build the BCSH parameter control rows."""
    rows = []
    for n1, k1, n2, k2 in BCSH_NAMES:
        rows.append([
            sg.Text(n1, size=(10, 1)),
            sg.Slider(
                range=(0, 511), default_value=256, orientation="h",
                size=(15, 15), key=f"-BCSH-{k1}-", enable_events=True,
                disable_number_display=True,
            ),
            sg.Spin(
                [str(i) for i in range(512)], initial_value="256",
                key=f"-BCSH-{k1}-SPIN-", size=(5, 1),
            ),
            sg.Text("", size=(8, 1), key=f"-BCSH-{k1}-NORM-", justification="left"),
            sg.Text(n2, size=(10, 1)),
            sg.Slider(
                range=(0, 511), default_value=256, orientation="h",
                size=(15, 15), key=f"-BCSH-{k2}-", enable_events=True,
                disable_number_display=True,
            ),
            sg.Spin(
                [str(i) for i in range(512)], initial_value="256",
                key=f"-BCSH-{k2}-SPIN-", size=(5, 1),
            ),
            sg.Text("", size=(8, 1), key=f"-BCSH-{k2}-NORM-", justification="left"),
        ])
    return rows


def _build_sathue_frame() -> list:
    """Build the Sat/Hue test Frame layout."""
    return [
        [
            sg.Frame(
                "Sat/Hue Test",
                [
                    [
                        sg.Checkbox(
                            "Show Color Map", key="-SAT-SHOW-MAP-", size=(12, 1), default=False, enable_events=True
                        ),
                        sg.Combo(
                            ["YUV", "RGB"],
                            default_value="YUV",
                            key="-SAT-CLRSPC-",
                            readonly=True,
                            size=(12, 1),
                            enable_events=True,
                        ),
                    ],
                    [
                        sg.Checkbox(
                            "Set Src Color", key="-SAT-SET-COLOR-", size=(12, 1), default=False, enable_events=True
                        ),
                        sg.Input(
                            "",
                            key="-SAT-COLOR-INPUT-",
                            size=(12, 1),
                            disabled=True,
                            disabled_readonly_background_color=sg.theme_background_color(),
                        ),
                    ],
                    [
                        sg.Text("Luma/Value:", size=(10, 1)),
                        sg.Slider(
                            range=(0, 255),
                            default_value=204,
                            orientation="h",
                            size=(10, 15),
                            key="-SAT-LUMA-",
                            enable_events=True,
                            disable_number_display=True,
                        ),
                        sg.Spin([str(i) for i in range(256)], initial_value="204", key="-SAT-LUMA-SPIN-", size=(5, 1)),
                    ],
                ],
                expand_x=True,
            )
        ]
    ]


def _build_coef_info_layout() -> list:
    """Build the CSC Coef Info display section."""
    return [
        [sg.Frame("CSC Coef Info", [
            [
                sg.Text("Step1 Coefs", size=(12, 1)),
                sg.Multiline("", size=(50, 1), key="-STEP1-COEFS-", disabled=True, no_scrollbar=True),
                sg.Text("Step1 Offset", size=(12, 1)),
                sg.Multiline("", size=(25, 1), key="-STEP1-OFFSET-", disabled=True, no_scrollbar=True),
            ],
            [
                sg.Text("Step2 Coefs", size=(12, 1)),
                sg.Multiline("", size=(50, 1), key="-STEP2-COEFS-", disabled=True, no_scrollbar=True),
                sg.Text("Step2 Offset", size=(12, 1)),
                sg.Multiline("", size=(25, 1), key="-STEP2-OFFSET-", disabled=True, no_scrollbar=True),
            ],
        ])],
    ]


def build_controls() -> list:
    """Build the CSC module tab layout.

    Left column: CSC Config Frame (Algo Type + BCSH sliders).
    Right column: Sat/Hue Test Frame.
    Below both: CSC Coef Info.
    """
    csc_config_rows = [
        [
            sg.Text("Algo Type"),
            sg.Combo(
                ALGO_TYPE_OPTIONS, default_value=ALGO_RK_HW_CSC,
                key="-BCSH-ALGO-TYPE-", readonly=True,
                enable_events=True,
            ),
            sg.Text("Precision"),
            sg.Combo(
                [str(v) for v in PRECISION_VALUES], default_value="10",
                key="-PRECISION-", readonly=True,
                enable_events=True,
            ),
            sg.Text("Channel Swap (VOP)"),
            sg.Combo(
                CHANNEL_SWAP_TYPES, default_value="None",
                key="-CHANNEL-SWAP-", readonly=True,
                enable_events=True,
            ),
            sg.Button("Reset BCSH", key="-RESET-BCSH-"),
        ],
    ]
    csc_config_rows.extend(_build_bcsh_layout())

    layout = [
        [
            sg.Column([
                [sg.Frame("CSC Config", csc_config_rows, expand_x=True, expand_y=True)]
            ], expand_x=True, expand_y=True, vertical_alignment="top"),
            sg.Column(
                _build_sathue_frame(),
                expand_y=True,
                vertical_alignment="top",
            ),
        ],
    ]
    layout.extend(_build_coef_info_layout())
    return layout


# ------------------------------------------------------------------ #
# Event handling                                                     #
# ------------------------------------------------------------------ #

def handle_csc_event(event: str, values: dict, window: sg.Window) -> bool:
    """Handle CSC-specific events. Returns True if consumed."""
    # -- Keyboard suffix events (bind_keyboard_events) - step before exact match --
    if "+" in event:
        event_key, _, event_suffix = event.rpartition("+")

        # BCSH spin +STEP / +ENTER: commit spin → slider
        if event_key.endswith("-SPIN-") and event_suffix in ("STEP", "ENTER"):
            _commit_bcsh_spin_to_slider(window, values, event_key)
            return True

        # BCSH slider +LEFT / +RIGHT: step by ±1
        if event_suffix in ("LEFT", "RIGHT") and not event_key.endswith("-SPIN-"):
            delta = -1 if event_suffix == "LEFT" else 1
            _step_bcsh_slider(window, values, event_key, delta)
            return True

        # SAT-LUMA spin +STEP / +ENTER
        if event_key == "-SAT-LUMA-SPIN-" and event_suffix in ("STEP", "ENTER"):
            _sync_sathue_slider_spin(window, values, "LUMA", 0, 255, int)
            return True

        # SAT-LUMA slider +LEFT / +RIGHT
        if event_key == "-SAT-LUMA-" and event_suffix in ("LEFT", "RIGHT"):
            delta = -1 if event_suffix == "LEFT" else 1
            cur = int(values.get("-SAT-LUMA-", 0))
            val = max(0, min(255, cur + delta))
            window["-SAT-LUMA-"].update(value=val)
            window["-SAT-LUMA-SPIN-"].update(value=str(val))
            return True

    # BCSH slider/spin sync
    for _, k1, _, k2 in BCSH_NAMES:
        for k in (k1, k2):
            slider_key = f"-BCSH-{k}-"
            spin_key = f"-BCSH-{k}-SPIN-"
            if event == slider_key:
                _sync_bcsh_slider(window, values, k)
                return True
            if event == spin_key:
                _sync_bcsh_spin(window, values, k)
                return True

    if event == "-RESET-BCSH-":
        _reset_bcsh(window, values)
        return True

    # Algo type switch with RGB gain remap
    if event == "-BCSH-ALGO-TYPE-":
        _handle_algo_type_switch(window, values)
        return True

    # Sat/Hue events
    if event == "-SAT-SET-COLOR-":
        enabled = values["-SAT-SET-COLOR-"]
        window["-SAT-COLOR-INPUT-"].update(disabled=not enabled)
        return True

    if event == "-SAT-SHOW-MAP-":
        return True

    if event == "-SAT-CLRSPC-":
        return True

    if event in ("-SAT-LUMA-", "-SAT-LUMA-SPIN-"):
        _sync_sathue_slider_spin(window, values, "LUMA", 0, 255, int)
        return True

    return False


# Track algo type for RGB gain remap
_current_algo_type = ALGO_RK_HW_CSC


def _handle_algo_type_switch(window: sg.Window, values: dict):
    """Handle algo type switch and remap RGB gain values."""
    global _current_algo_type
    new_algo_type = values.get("-BCSH-ALGO-TYPE-", ALGO_RK_HW_CSC)
    old_algo_type = _current_algo_type
    for gain_key in RGB_GAIN_KEYS:
        slider_key = f"-BCSH-{gain_key}-"
        current_value = int(values[slider_key])
        remapped = remap_rgb_gain_value_for_algo_switch(current_value, old_algo_type, new_algo_type)
        window[slider_key].update(value=remapped)
        window[f"-BCSH-{gain_key}-SPIN-"].update(value=str(remapped))
        norm = get_bcsh_norm_value(gain_key, remapped, new_algo_type)
        window[f"-BCSH-{gain_key}-NORM-"].update(value=norm)
        values[slider_key] = remapped
        values[f"-BCSH-{gain_key}-SPIN-"] = str(remapped)
    # Update all norm labels for the new algo type
    for _, k1, _, k2 in BCSH_NAMES:
        for k in (k1, k2):
            raw_val = int(values[f"-BCSH-{k}-"])
            norm = get_bcsh_norm_value(k, raw_val, new_algo_type)
            window[f"-BCSH-{k}-NORM-"].update(value=norm)
    _current_algo_type = new_algo_type


def _sync_bcsh_slider(window: sg.Window, values: dict, key: str):
    """Sync Spin to Slider value on BCSH Slider change."""
    val = int(values[f"-BCSH-{key}-"])
    window[f"-BCSH-{key}-SPIN-"].update(value=str(val))
    algo_type = values.get("-BCSH-ALGO-TYPE-", ALGO_RK_HW_CSC)
    norm = get_bcsh_norm_value(key, val, algo_type)
    window[f"-BCSH-{key}-NORM-"].update(value=norm)


def _sync_bcsh_spin(window: sg.Window, values: dict, key: str):
    """Sync Slider to Spin value on BCSH Spin change."""
    try:
        val = int(values[f"-BCSH-{key}-SPIN-"])
    except ValueError:
        return
    val = max(0, min(511, val))
    window[f"-BCSH-{key}-"].update(value=val)
    algo_type = values.get("-BCSH-ALGO-TYPE-", ALGO_RK_HW_CSC)
    norm = get_bcsh_norm_value(key, val, algo_type)
    window[f"-BCSH-{key}-NORM-"].update(value=norm)


def _sync_sathue_slider_spin(window: sg.Window, values: dict, suffix: str,
                              min_val: int, max_val: int, spin_fmt):
    """Sync Sat/Hue Slider and Spin bidirectionally."""
    slider_key = f"-SAT-{suffix}-"
    spin_key = f"-SAT-{suffix}-SPIN-"
    slider_val = int(values[slider_key])
    spin_val = values[spin_key]

    if values.get(slider_key) is not None:
        window[spin_key].update(value=str(spin_fmt(slider_val)))
    try:
        sv = int(spin_val)
        sv = max(min_val, min(max_val, sv))
        window[slider_key].update(value=sv)
    except (ValueError, TypeError):
        pass


def _reset_bcsh(window: sg.Window, values: dict = None):
    """Reset all BCSH controls to algorithm-specific defaults."""
    algo_type = values.get("-BCSH-ALGO-TYPE-", ALGO_RK_HW_CSC) if values else ALGO_RK_HW_CSC
    defaults = get_default_bcsh_raw_values(algo_type)
    key_map = {
        "brightness": "bright", "contrast": "contrast",
        "saturation": "sat", "hue": "hue",
        "r_gain": "r_gain", "r_offset": "r_offset",
        "g_gain": "g_gain", "g_offset": "g_offset",
        "b_gain": "b_gain", "b_offset": "b_offset",
    }
    for config_key, ui_key in key_map.items():
        default_val = defaults.get(config_key, 256)
        window[f"-BCSH-{ui_key}-"].update(value=default_val)
        window[f"-BCSH-{ui_key}-SPIN-"].update(value=str(default_val))
        norm = get_bcsh_norm_value(ui_key, default_val, algo_type)
        window[f"-BCSH-{ui_key}-NORM-"].update(value=norm)


# ------------------------------------------------------------------ #
# Module protocol                                                    #
# ------------------------------------------------------------------ #

def read_params(values: dict) -> dict:
    """Extract CSC module parameters from window values."""
    params = {}
    for _, k1, _, k2 in BCSH_NAMES:
        for k in (k1, k2):
            try:
                params[k] = int(values.get(f"-BCSH-{k}-SPIN-", "256"))
            except ValueError:
                params[k] = BCSH_DEFAULT.get(k, 256)
    params["algo_type"] = values.get("-BCSH-ALGO-TYPE-", ALGO_RK_HW_CSC)
    try:
        params["precision"] = int(values.get("-PRECISION-", "10"))
    except ValueError:
        params["precision"] = 10

    # Sat/Hue params (hue/sat from BCSH)
    params["sat_luma"] = int(values.get("-SAT-LUMA-", "204"))
    params["sat_show_map"] = values.get("-SAT-SHOW-MAP-", False)
    params["bcsh_hue"] = params.get("hue", 256)
    params["bcsh_sat"] = params.get("sat", 256)
    params["sat_clrspc"] = values.get("-SAT-CLRSPC-", "Input Colorspace")

    return params


def process(input_data: np.ndarray, input_fmt: int, input_clrspc: int,
            output_fmt: int, output_clrspc: int, params: dict):
    """Run CSC processing.

    Args:
        input_data: Input planar numpy array (3, H, W).
        input_fmt: Input pixel format code.
        input_clrspc: Input colorspace code.
        output_fmt: Output pixel format code.
        output_clrspc: Output colorspace code.
        params: CSC module parameters from read_params().

    Returns:
        (ok: bool, output_data: np.ndarray | str)
        On success: (True, output_planar)
        On failure: (False, error_message)
    """
    try:
        in_depth = get_pixel_depth(input_fmt)
        out_depth = get_pixel_depth(output_fmt)
        pixel_depth = max(in_depth, out_depth)

        algo_type = normalize_algo_type(params.get("algo_type", ALGO_RK_HW_CSC))
        precision = params.get("precision", 10)

        bcsh_config = build_bcsh_config_from_dict({
            "brightness": params.get("bright", 256),
            "contrast": params.get("contrast", 256),
            "saturation": params.get("sat", 256),
            "hue": params.get("hue", 256),
            "r_gain": params.get("r_gain", 256),
            "r_offset": params.get("r_offset", 256),
            "g_gain": params.get("g_gain", 256),
            "g_offset": params.get("g_offset", 256),
            "b_gain": params.get("b_gain", 256),
            "b_offset": params.get("b_offset", 256),
        }, algo_type)

        output_data, step1_coefs, step1_offset, step2_coefs, step2_offset = run_selected_algo(
            input_data, bcsh_config, pixel_depth, precision,
            algo_type, input_clrspc, output_clrspc,
            input_fmt, output_fmt,
        )

        return True, output_data
    except Exception as e:
        return False, str(e)


def get_right_preview_image(snapshot, params: dict):
    """Return Sat/Hue color map for right preview, or None if disabled."""
    if not params.get("sat_show_map", False):
        return None

    clrspc = params.get("sat_clrspc", "Input Colorspace")
    luma = params.get("sat_luma", 204)

    if clrspc == "RGB":
        img_eff = _build_colormap_rgb(luma)
        title = f"HSV->RGB  (V={luma})"
        xlabel, ylabel = "S*cos(H)", "S*sin(H)"
    else:
        # Default: YUV mode (also for "Input Colorspace")
        img_eff = _build_colormap_yuv(luma)
        title = f"YCbCr->RGB  (Y={luma})"
        xlabel, ylabel = "Cb", "Cr"

    full_img, _ = _build_colormap_with_axis(img_eff, title, xlabel, ylabel)
    return np.array(full_img)


# ------------------------------------------------------------------ #
# Keyboard bindings                                                  #
# ------------------------------------------------------------------ #

def _commit_bcsh_spin_to_slider(window: sg.Window, values: dict, spin_key: str):
    """For BCSH spin +STEP / +ENTER: commit spin value to slider and update norm."""
    try:
        val = int(values.get(spin_key, "256"))
    except (ValueError, TypeError):
        return
    val = max(0, min(511, val))
    slider_key = spin_key.replace("-SPIN-", "-")
    window[slider_key].update(value=val)


def _step_bcsh_slider(window: sg.Window, values: dict, slider_key: str, delta: int):
    """For BCSH slider +LEFT / +RIGHT: step the slider value by delta."""
    cur = int(values.get(slider_key, 256))
    val = max(0, min(511, cur + delta))
    spin_key = slider_key[:-1] + "-SPIN-"
    window[slider_key].update(value=val)
    window[spin_key].update(value=str(val))


def bind_keyboard_events(window: sg.Window):
    """Bind keyboard events (arrows, Enter, step) on all CSC sliders and spins."""
    for _, k1, _, k2 in BCSH_NAMES:
        for bcsh_key in (k1, k2):
            slider_key = f"-BCSH-{bcsh_key}-"
            spin_key = f"-BCSH-{bcsh_key}-SPIN-"
            # Spin: Return / KP_Enter to commit, command for step
            try:
                window[spin_key].bind("<Return>", "+ENTER")
                window[spin_key].bind("<KP_Enter>", "+ENTER")
                window[spin_key].Widget.configure(
                    command=lambda wk=window, sk=spin_key: wk.write_event_value(f"{sk}+STEP", None)
                )
            except Exception:
                pass
            # Slider: Left/Right arrow to step, Button-1 to focus
            try:
                sw = window[slider_key].Widget
                sw.configure(takefocus=1)
                sw.bind("<Button-1>", lambda e, w=sw: w.focus_set(), add="+")
                sw.bind("<Left>", lambda e, wk=window, sk=slider_key: wk.write_event_value(f"{sk}+LEFT", None))
                sw.bind("<Right>", lambda e, wk=window, sk=slider_key: wk.write_event_value(f"{sk}+RIGHT", None))
            except Exception:
                pass

    # SAT-LUMA spin
    try:
        window["-SAT-LUMA-SPIN-"].bind("<Return>", "+ENTER")
        window["-SAT-LUMA-SPIN-"].bind("<KP_Enter>", "+ENTER")
        window["-SAT-LUMA-SPIN-"].Widget.configure(
            command=lambda wk=window: wk.write_event_value("-SAT-LUMA-SPIN-+STEP", None)
        )
    except Exception:
        pass

    # SAT-LUMA slider
    try:
        sw = window["-SAT-LUMA-"].Widget
        sw.configure(takefocus=1)
        sw.bind("<Button-1>", lambda e, w=sw: w.focus_set(), add="+")
        sw.bind("<Left>", lambda e, wk=window: wk.write_event_value("-SAT-LUMA-+LEFT", None))
        sw.bind("<Right>", lambda e, wk=window: wk.write_event_value("-SAT-LUMA-+RIGHT", None))
    except Exception:
        pass
