"""
Copyright   : Copyright (c) 2026 by Rockchip. All right reserved.
FilePath    : csc_ui.py
Author      : vance.wu@rock-chips.com
Date        : 2026-06-03
Description : PySimpleGUI-based UI for interactive CSC image conversion
"""

import io
import os
import re
import sys
from pathlib import Path
import numpy as np
import PySimpleGUI as sg
from PIL import Image, ImageDraw, ImageFont

from get_csc_coefs import (
    CscCoefConfig,
    CscMode,
    ColorSpace,
    get_csc_coefs,
    parse_csc_mode_str,
)
from get_csc_coef_hsv import (
    ALGO_RK_HW_CSC,
    ALGO_RK_SW_CSC,
    ALGO_EVIDEO_CSC,
    ALGO_EVIDEO_CSC_PLAN_A,
    ALGO_EVIDEO_CSC_PLAN_B,
    normalize_algo_type,
    get_evideo_plan_a_steps,
    get_evideo_plan_a_runtime_steps,
    get_evideo_plan_b_steps,
)
from run_csc import (
    FORMAT_NAMES,
    CLRSPC_NAMES,
    CLRSPC_TO_PARAMS,
    FMT_OPTIONS_8BIT,
    FMT_OPTIONS_10BIT,
    CLRSPC_OPTIONS,
    clrspc_to_mode_params,
    build_csc_mode_str,
    is_yuv_format,
    is_rgb_format,
    get_pixel_depth,
    read_raw_to_planar,
    write_planar_to_raw,
    apply_csc,
    build_csc_config,
    build_bcsh_config_from_dict,
    get_default_bcsh_raw_values,
    get_rgb_gain_default_value,
    run_selected_algo,
    _get_default_output_path,
    DEBUG_DUMP_PATH,
)

RGB_GAIN_KEYS = ("r_gain", "g_gain", "b_gain")
UI_BCSH_KEY_TO_CONFIG_KEY = {
    "bright": "brightness",
    "sat": "saturation",
}


def _load_ui_font(size):
    """Load the UI font from the packaged bundle or repository data directory."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        font_path = Path(sys._MEIPASS) / "assets" / "fonts" / "NotoSans-Regular.ttf"
    else:
        font_path = Path(__file__).resolve().parents[2] / "data" / "fonts" / "NotoSans-Regular.ttf"
    try:
        return ImageFont.truetype(str(font_path), size)
    except Exception:
        return ImageFont.load_default()


def ui_bcsh_key_to_config_key(ui_key):
    """Convert a UI BCSH key to the matching config field name."""
    return UI_BCSH_KEY_TO_CONFIG_KEY.get(ui_key, ui_key)


def get_bcsh_spin_key(slider_key):
    """Return the paired spinbox key for a BCSH slider key."""
    if not slider_key.startswith("-BCSH-") or not slider_key.endswith("-"):
        raise ValueError(f"Invalid BCSH slider key: {slider_key}")
    return slider_key[:-1] + "-SPIN-"


def normalize_bcsh_spin_value(raw_value, fallback_value):
    """Normalize a spinbox commit to an in-range integer."""
    try:
        value = int(str(raw_value).strip())
    except (TypeError, ValueError):
        return int(fallback_value)
    return max(0, min(511, value))


def step_bcsh_value(current_value, delta):
    """Step a BCSH value by delta while clamping to the valid range."""
    return max(0, min(511, int(current_value) + int(delta)))


def get_bcsh_norm_value(param_key, raw_value, algo_type):
    """
    Compute the normalized display value for a BCSH parameter.
    Returns a formatted string according to the algorithm's mapping range.
    """
    evideo_algos = {ALGO_EVIDEO_CSC, ALGO_EVIDEO_CSC_PLAN_A, ALGO_EVIDEO_CSC_PLAN_B}
    is_evideo = algo_type in evideo_algos

    if param_key in ("r_gain", "g_gain", "b_gain"):
        if is_evideo:
            norm = raw_value / 64.0
        else:
            norm = raw_value / 256.0
        return f"{norm:.2f}"
    elif param_key in ("r_offset", "g_offset", "b_offset"):
        if is_evideo:
            norm = (raw_value - 256) / 256.0
        else:
            norm = (raw_value - 256) / 2048.0
        return f"{norm:.2f}"
    elif param_key == "bright":
        if is_evideo:
            norm = (raw_value - 256) / 256.0
        else:
            norm = (raw_value - 256) / 1024.0
        return f"{norm:.2f}"
    elif param_key == "contrast":
        norm = raw_value / 256.0
        return f"{norm:.2f}"
    elif param_key == "sat":
        norm = raw_value / 256.0
        return f"{norm:.2f}"
    elif param_key == "hue":
        if is_evideo:
            norm = (raw_value - 256) * 180.0 / 256.0
        else:
            norm = (raw_value - 256) * 30.0 / 256.0
        return f"{norm:.2f}"
    return ""


def remap_rgb_gain_value_for_algo_switch(value, old_algo_type, new_algo_type):
    """Remap raw RGB gain when switching between RK-family and eVideo CSC."""
    if old_algo_type == new_algo_type:
        return int(value)

    remapped = float(value)
    rk_algo_types = {ALGO_RK_HW_CSC, ALGO_RK_SW_CSC}
    evideo_algo_types = {ALGO_EVIDEO_CSC, ALGO_EVIDEO_CSC_PLAN_A, ALGO_EVIDEO_CSC_PLAN_B}
    if old_algo_type in rk_algo_types and new_algo_type in evideo_algo_types:
        remapped /= 4.0
    elif old_algo_type in evideo_algo_types and new_algo_type in rk_algo_types:
        remapped *= 4.0

    return int(np.clip(round(remapped), 0, 511))


# ---- Colormap conversion helpers ----

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


SAT_COLORMAP_SIZE = 416  # effective image area size (px)
SAT_MARGIN = 48          # border margin for axes/labels
_DATA_RANGE_MAX = 128    # max data value, range is [-128, 127] or [-128, 128]
_DATA_SIZE = 256         # total data range size (max - min + 1 for ticks)


def _data_to_pix(val):
    """Map a float data value in [-128, 128] to pixel coordinate [0, SAT_COLORMAP_SIZE-1].
    Uses exact integer scaling: each of the 256 data values occupies SIZE/256 pixels."""
    return int(round((val + _DATA_RANGE_MAX) * SAT_COLORMAP_SIZE / _DATA_SIZE))


def _pix_to_data(pix):
    """Map pixel [0, SIZE-1] to continuous float data value in [-128, 127.5].
    Used for color generation (colormap pixel→data→RGB conversion)."""
    return pix * _DATA_SIZE / SAT_COLORMAP_SIZE - _DATA_RANGE_MAX


def _pix_to_data_int(pix):
    """Map pixel [0, SIZE-1] to discrete integer data value in [-128, 127].
    Uses floor: each group of ceil(SIZE/256) pixels maps to one integer data value."""
    return int(pix * _DATA_SIZE / SAT_COLORMAP_SIZE) - _DATA_RANGE_MAX


def _build_colormap_yuv(luma_val):
    """Build YCbCr->RGB colormap for a fixed luma value. Returns PIL Image."""
    w, h_img = SAT_COLORMAP_SIZE, SAT_COLORMAP_SIZE
    # Map pixel coords to data range [-128, 127]
    cb_grid = _pix_to_data(np.tile(np.arange(w, dtype=np.float32), (h_img, 1)))
    cr_grid = _pix_to_data(np.tile(np.arange(h_img - 1, -1, -1, dtype=np.float32).reshape(-1, 1), (1, w)))
    y = np.full((h_img, w), float(luma_val), dtype=np.float32)
    r, g, b = _ycbcr2rgb(y, cb_grid, cr_grid)
    return Image.fromarray(np.stack([r, g, b], axis=-1), 'RGB')


def _build_colormap_rgb(value_val):
    """Build HSV->RGB colormap for a fixed V value. Returns PIL Image."""
    w, h_img = SAT_COLORMAP_SIZE, SAT_COLORMAP_SIZE
    # Map pixel coords to [-128, 127] range, then to normalized [-1, 1]
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
    font = _load_ui_font(16)
    axis_color = (0, 0, 0)
    tick_color = (64, 64, 64)
    # Origin at center of effective area (Cb=0, Cr=0)
    cx0 = _data_to_pix(0)    # pixel offset within effective area for Cb=0
    cy0 = _data_to_pix(0)    # pixel offset from top for Cr=0 (= SIZE-1 - _data_to_pix(0) for symmetry)
    x0 = margin + cx0
    y0 = margin + (SAT_COLORMAP_SIZE - 1) - cy0
    # X axis (horizontal through Cr=0)
    draw.line([(margin, y0), (total_w - margin, y0)], fill=axis_color, width=2)
    # Y axis (vertical through Cb=0)
    draw.line([(x0, margin), (x0, total_h - margin)], fill=axis_color, width=2)
    # Ticks
    tick_data_vals = [-128, -96, -64, -32, 0, 32, 64, 96]  # match data range [-128, 127]
    for dv in tick_data_vals:
        # X tick: Cb=dv at pixel _data_to_pix(dv) from left
        x = margin + _data_to_pix(dv)
        draw.line([(x, y0 - 4), (x, y0 + 4)], fill=tick_color, width=1)
        if font and dv != 0:
            draw.text((x + 3, y0 + 5), str(dv), fill=tick_color, font=font)
        # Y tick: Cr=dv at pixel SAT_COLORMAP_SIZE-1-_data_to_pix(dv) from top
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


def open_csc_ui(args=None):
    """Open PySimpleGUI UI for interactive CSC conversion"""
    sg.theme('SystemDefault')

    fmt_options = FMT_OPTIONS_8BIT + FMT_OPTIONS_10BIT
    fmt_display = [f"0x{f:X} - {FORMAT_NAMES.get(f, 'Unknown')}" for f in fmt_options]
    clrspc_display_all = [f"{c} - {CLRSPC_NAMES[c]}" for c in CLRSPC_OPTIONS]
    clrspc_rgb = [s for s in clrspc_display_all if int(s.split(" ")[0]) in (0, 1)]
    clrspc_yuv = [s for s in clrspc_display_all if int(s.split(" ")[0]) in range(2, 8)]
    precision_values = [0] + list(range(8, 17))
    fmt_combo_width = 28
    clrspc_combo_width = 22

    def get_fmt_from_display(display_str):
        return int(display_str.split(" ")[0], 16)

    def get_clrspc_from_display(display_str):
        return int(display_str.split(" ")[0])

    def _update_fmt_for_clrspc(window, values, fmts, iclr):
        """Auto-select input format based on colorspace when Set Color is active."""
        iclr_int = int(iclr)
        if iclr_int in (0, 1):
            # RGB full/limited -> RGB888 (0x0)
            target_fmt = next((f for f in fmts if f.startswith('0x0 ')), None)
        else:
            # YUV -> YU24 (0x3)
            target_fmt = next((f for f in fmts if f.startswith('0x3 ')), None)
        if target_fmt:
            window['-IN-FMT-'].update(value=target_fmt)
            values['-IN-FMT-'] = target_fmt

    def _enforce_combo_width(window, key, width_chars):
        """Keep combo widget width stable after runtime value list updates."""
        widget = window[key].Widget
        try:
            widget.configure(width=width_chars)
        except Exception:
            pass

    def _update_clrspc_for_fmt(window, values, clrspc_key, fmt_str, default_clrspc=None):
        """Update a colorspace combo options to match the selected format domain."""
        fmt_code = int(fmt_str.split(" ")[0], 16)
        base = fmt_code & 0xF
        if base <= 0x2:
            options = clrspc_rgb
            default = default_clrspc or clrspc_rgb[1]  # RGB_Full
        else:
            options = clrspc_yuv
            default = default_clrspc or clrspc_yuv[3]  # BT709_Full
        window[clrspc_key].update(values=options)
        _enforce_combo_width(window, clrspc_key, clrspc_combo_width)
        # Reset to default if current value is not in the new options
        current_val = values.get(clrspc_key, '')
        if current_val not in options:
            window[clrspc_key].update(value=default)
            values[clrspc_key] = default
        else:
            window[clrspc_key].update(value=current_val)

    def _sync_clrspc_controls(window, values):
        """Bind input/output colorspace controls to the current format domain."""
        _update_clrspc_for_fmt(window, values, '-IN-CLR-', values['-IN-FMT-'])
        _update_clrspc_for_fmt(window, values, '-OUT-CLR-', values['-OUT-FMT-'])

    bcsh_names = [
        ('Brightness:', 'bright', 'Contrast:', 'contrast'),
        ('Saturation:', 'sat', 'Hue:', 'hue'),
        ('R Gain:', 'r_gain', 'R Offset:', 'r_offset'),
        ('G Gain:', 'g_gain', 'G Offset:', 'g_offset'),
        ('B Gain:', 'b_gain', 'B Offset:', 'b_offset'),
    ]

    bcsh_layout = []
    for n1, k1, n2, k2 in bcsh_names:
        bcsh_layout.append([
            sg.Text(n1, size=(10, 1)),
            sg.Slider(range=(0, 511), default_value=256, orientation='h',
                      size=(20, 15), key=f'-BCSH-{k1}-', enable_events=True, disable_number_display=True),
            sg.Spin([str(i) for i in range(512)], initial_value='256', key=f'-BCSH-{k1}-SPIN-', size=(5, 1)),
            sg.Text('', size=(8, 1), key=f'-BCSH-{k1}-NORM-', justification='left'),
            sg.Text(n2, size=(10, 1)),
            sg.Slider(range=(0, 511), default_value=256, orientation='h',
                      size=(20, 15), key=f'-BCSH-{k2}-', enable_events=True, disable_number_display=True),
            sg.Spin([str(i) for i in range(512)], initial_value='256', key=f'-BCSH-{k2}-SPIN-', size=(5, 1)),
            sg.Text('', size=(8, 1), key=f'-BCSH-{k2}-NORM-', justification='left'),
        ])

    algo_type_options = [
        ALGO_RK_HW_CSC,
        ALGO_RK_SW_CSC,
        ALGO_EVIDEO_CSC,
        ALGO_EVIDEO_CSC_PLAN_A,
        ALGO_EVIDEO_CSC_PLAN_B,
    ]
    bcsh_tab_layout = [
        *bcsh_layout,
        [sg.Text('Algo Type:', size=(8, 1)),
         sg.Combo(algo_type_options, default_value=ALGO_RK_HW_CSC, key='-BCSH-ALGO-TYPE-',
                  readonly=True, size=(22, 1), enable_events=True),
         sg.Push(),
         sg.Button('Reset BCSH', key='-RESET-BCSH-')]
    ]

    preview_resize_threshold = 24

    sathue_tab_layout = [
        [sg.Text('Input Colorspace:', size=(14, 1)),
         sg.Combo(['YUV', 'RGB'], default_value='YUV', key='-SAT-CLRSPC-',
                  readonly=True, size=(6, 1), enable_events=True),
         sg.Text('Input Depth:', size=(10, 1)),
         sg.Text('8bit', key='-SAT-DEPTH-', size=(5, 1)),
         sg.Push(),
         sg.Checkbox('Show Color Map', key='-SAT-SHOW-MAP-', default=False, enable_events=True)],
        [sg.Checkbox('Set Color', key='-SAT-SET-COLOR-', default=False, enable_events=True),
         sg.Input('', key='-SAT-COLOR-INPUT-', size=(28, 1), enable_events=False,
                  disabled=True, disabled_readonly_background_color=sg.theme_background_color())],
        [sg.Text('Luma/Value:', size=(14, 1)),
         sg.Slider(range=(0, 255), default_value=204, orientation='h',
                   size=(20, 15), key='-SAT-LUMA-', enable_events=True, disable_number_display=True),
         sg.Spin([str(i) for i in range(256)], initial_value='204', key='-SAT-LUMA-SPIN-', size=(5, 1))],
        [sg.Text('Hue:', size=(14, 1)),
         sg.Slider(range=(-180, 180), default_value=0, resolution=1, orientation='h',
                   size=(20, 15), key='-SAT-HUE-', enable_events=True, disable_number_display=True),
         sg.Spin([str(i) for i in range(-180, 181)], initial_value='0', key='-SAT-HUE-SPIN-', size=(5, 1)),
         sg.Button('Reset', key='-SAT-HUE-RESET-', size=(5, 1))],
        [sg.Text('Saturation:', size=(14, 1)),
         sg.Slider(range=(0, 360), default_value=180, resolution=1, orientation='h',
                   size=(20, 15), key='-SAT-SAT-', enable_events=True, disable_number_display=True),
         sg.Spin([f"{i/180:.2f}" for i in range(361)], initial_value='1.00', key='-SAT-SAT-SPIN-', size=(5, 1)),
         sg.Button('Reset', key='-SAT-SAT-RESET-', size=(5, 1))],
    ]

    input_output_layout = [
        [sg.Text('Input File:', size=(12, 1)),
         sg.Input(key='-INPUT-FILE-', size=(52, 1), enable_events=True, readonly=True),
         sg.FileBrowse('Browse...')],
        [sg.Text('Width:', size=(6, 1)), sg.Input('1920', key='-WIDTH-', size=(8, 1), enable_events=True),
         sg.Text('Height:', size=(6, 1)), sg.Input('1080', key='-HEIGHT-', size=(8, 1), enable_events=True),
         sg.Checkbox('Set Color', key='-SET-COLOR-', default=False, enable_events=True),
         sg.Input('128 128 128', key='-COLOR-INPUT-', size=(28, 1), enable_events=False,
                  disabled=True, disabled_readonly_background_color=sg.theme_background_color())],
        [sg.Text('Input Format:', size=(12, 1)),
         sg.Combo(fmt_display, default_value=fmt_display[0], key='-IN-FMT-',
                  readonly=True, size=(fmt_combo_width, 1), enable_events=True),
         sg.Text('Input Colorspace:', size=(14, 1)),
         sg.Combo(clrspc_rgb, default_value=clrspc_rgb[1], key='-IN-CLR-',
                  readonly=True, size=(clrspc_combo_width, 1), enable_events=True)],
        [sg.Text('Output Format:', size=(12, 1)),
         sg.Combo(fmt_display, default_value=fmt_display[0], key='-OUT-FMT-',
                  readonly=True, size=(fmt_combo_width, 1), enable_events=True),
         sg.Text('Output Colorspace:', size=(14, 1)),
         sg.Combo(clrspc_rgb, default_value=clrspc_rgb[1], key='-OUT-CLR-',
                  readonly=True, size=(clrspc_combo_width, 1), enable_events=True)],
        [sg.Text('Precision (0=float):', size=(16, 1)),
         sg.Combo([str(v) for v in precision_values], default_value='10',
                  key='-PRECISION-', readonly=True, size=(6, 1), enable_events=True),
         sg.Text('Auto Pixel Depth:', size=(14, 1)),
         sg.Text('8', key='-DISP-DEPTH-', size=(4, 1), font=('_', 10, 'bold'))]
    ]

    layout = [
        [sg.Column([
            [sg.TabGroup([
                [sg.Tab('I/O Config', input_output_layout),
                 sg.Tab('BCSH Config', bcsh_tab_layout),
                 sg.Tab('Sat/Hue Test', sathue_tab_layout)]
            ], key='-TABS-')]
        ]),
        sg.Column([
             [sg.Button('Save Output', key='-SAVE-OUT-', size=(12, 2))],
             [sg.Radio('Show Input', 'RADIO1', key='-SHOW-IN-', enable_events=True, size=(12, 1))],
             [sg.Radio('Show Output', 'RADIO1', default=True, key='-SHOW-OUT-', enable_events=True, size=(12, 1))],
             [sg.Checkbox('dump', key='-DUMP-', default=False, enable_events=True, size=(12, 1))]
         ], element_justification='l', vertical_alignment='top', pad=(10, 30))],
        [sg.HorizontalSeparator()],
        [sg.Frame('Preview Info', [
            [
                sg.Text('Display Size:', size=(12, 1)),
                sg.Input('', key='-DISPLAY-SIZE-', size=(48, 1), readonly=True, border_width=0,
                         disabled_readonly_background_color=sg.theme_background_color(), disabled_readonly_text_color=sg.theme_text_color()),
                sg.Text('Position:', size=(10, 1)),
                sg.Input('', key='-POSITION-INFO-', size=(48, 1), readonly=True, border_width=0,
                         disabled_readonly_background_color=sg.theme_background_color(), disabled_readonly_text_color=sg.theme_text_color()),
            ],
            [
                sg.Text('Input Pixel:', size=(12, 1)),
                sg.Input('', key='-INPUT-PIXEL-INFO-', size=(48, 1), readonly=True, border_width=0,
                         disabled_readonly_background_color=sg.theme_background_color(), disabled_readonly_text_color=sg.theme_text_color()),
                sg.Text('Output Pixel:', size=(10, 1)),
                sg.Input('', key='-OUTPUT-PIXEL-INFO-', size=(48, 1), readonly=True, border_width=0,
                         disabled_readonly_background_color=sg.theme_background_color(), disabled_readonly_text_color=sg.theme_text_color()),
            ],
        ], expand_x=True)],
        [sg.Frame('CSC Steps', [
            [
                sg.Text('Step1 Coefs:', size=(12, 1)),
                sg.Multiline('', size=(58, 1), key='-STEP1-COEFS-', disabled=True, no_scrollbar=True),
                sg.Text('Step1 Offset:', size=(12, 1)),
                sg.Multiline('', size=(28, 1), key='-STEP1-OFFSET-', disabled=True, no_scrollbar=True),
            ],
            [
                sg.Text('Step2 Coefs:', size=(12, 1)),
                sg.Multiline('', size=(58, 1), key='-STEP2-COEFS-', disabled=True, no_scrollbar=True),
                sg.Text('Step2 Offset:', size=(12, 1)),
                sg.Multiline('', size=(28, 1), key='-STEP2-OFFSET-', disabled=True, no_scrollbar=True),
            ],
        ], expand_x=True)],
        [sg.Column([
            [sg.Frame('Image Preview', [[sg.Image(key='-IMAGE-', background_color='gray')]],
                      key='-MAIN-PREVIEW-FRAME-', expand_x=True, expand_y=True)]
        ], key='-MAIN-IMAGE-COL-', expand_x=True, expand_y=True, element_justification='center', vertical_alignment='top'),
         sg.Column([
             [sg.Frame('Sat/Hue Preview', [[sg.Image(key='-SAT-IMAGE-', background_color='gray')]],
                       key='-SAT-PREVIEW-FRAME-', expand_x=True, expand_y=True)]
         ], key='-SAT-IMAGE-COL-', expand_y=True, element_justification='center', vertical_alignment='top', pad=((10, 0), 0), visible=False)]
    ]

    window = sg.Window('CSC Test Tool v1.0', layout, resizable=True, finalize=True, return_keyboard_events=True)
    window.TKroot.attributes('-topmost', True)
    window.TKroot.lift()
    window.TKroot.focus_force()
    window.TKroot.after(100, lambda: window.TKroot.attributes('-topmost', False))

    window.bind('<Configure>', '-WINDOW-RESIZE-')
    _sync_clrspc_controls(window, {
        '-IN-FMT-': window['-IN-FMT-'].get(),
        '-IN-CLR-': window['-IN-CLR-'].get(),
        '-OUT-FMT-': window['-OUT-FMT-'].get(),
        '-OUT-CLR-': window['-OUT-CLR-'].get(),
    })
    _enforce_combo_width(window, '-IN-FMT-', fmt_combo_width)
    _enforce_combo_width(window, '-OUT-FMT-', fmt_combo_width)

    window['-IMAGE-'].bind('<Motion>', '+MOTION')
    window['-IMAGE-'].bind('<Enter>', '+ENTER')
    window['-IMAGE-'].bind('<Leave>', '+LEAVE')
    window['-SAT-IMAGE-'].bind('<Motion>', '+MOTION')
    window['-SAT-IMAGE-'].bind('<Enter>', '+ENTER')
    window['-SAT-IMAGE-'].bind('<Leave>', '+LEAVE')
    window['-COLOR-INPUT-'].bind('<Return>', '+ENTER')
    window['-COLOR-INPUT-'].bind('<KP_Enter>', '+ENTER')
    window['-SAT-COLOR-INPUT-'].bind('<Return>', '+ENTER')
    window['-SAT-COLOR-INPUT-'].bind('<KP_Enter>', '+ENTER')

    current_planar_in = None
    current_planar_out = None
    current_output_pixel_depth = 10
    current_input_pixel_depth = 10
    current_output_is_yuv = False
    current_input_is_yuv = False
    current_output_full_range = True
    current_input_full_range = True
    current_output_color = ColorSpace.BT709
    current_input_color = ColorSpace.BT709
    current_step1_coefs = None
    current_step1_offset = None
    current_step2_coefs = None
    current_step2_offset = None
    current_scale_factor = 1.0
    current_mouse_pos = None
    is_pixel_info_frozen = False
    is_mouse_in_image = False
    current_algo_type = ALGO_RK_HW_CSC
    sat_preview_visible = False
    last_main_preview_size = (0, 0)
    last_sat_preview_size = (0, 0)
    current_main_display_size = (400, 400)

    # Sat/Hue Test state
    sathue_colorspace = 'YUV'
    sathue_luma_val = 204
    sathue_hue_val = 0
    sathue_sat_val = 1.0
    sathue_img_eff = None       # effective colormap PIL Image (without axes)
    sathue_img_full = None      # full image with axes, margin
    sathue_margin = SAT_MARGIN
    sathue_locked = False
    sathue_locked_pix = None    # (img_x, img_y) in effective coords
    sathue_locked_input = None  # (c1, c2, c3) input values at lock point
    sathue_mouse_pos = None
    sathue_display_scale = 1.0  # scale ratio applied to full_img for display
    sathue_render_after_id = None  # tkinter after id for deferred render
    is_mouse_in_sathue = False
    sathue_set_color_enabled = False
    planar_in_full = None
    current_input_file_params = None  # (input_file, w, h, ifmt)

    def parse_color_input(text):
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
            sg.popup_error(f"Need 3 integer values, got {len(nums)}. Input: '{text}'")
            return None
        return nums[:3]

    def update_sathue_map(preserve_display_size=False):
        """Regenerate the Sat/Hue colormap image and update the widget."""
        nonlocal sathue_img_eff, sathue_img_full, sathue_margin
        nonlocal sathue_display_scale
        if sathue_colorspace == 'YUV':
            img_eff = _build_colormap_yuv(sathue_luma_val)
            title = f"YCbCr->RGB  (Y={sathue_luma_val})"
            xlabel, ylabel = "Cb", "Cr"
        else:
            img_eff = _build_colormap_rgb(sathue_luma_val)
            title = f"HSV->RGB  (V={sathue_luma_val})"
            xlabel, ylabel = "S*cos(H)", "S*sin(H)"
        sathue_img_eff = img_eff.copy()

        # Draw locked-point circles
        img_verbose = img_eff.copy()
        draw_verbose = ImageDraw.Draw(img_verbose)

        if sathue_locked and sathue_locked_pix is not None:
            lx, ly = sathue_locked_pix
            # Black circle at locked position (thick)
            r = 5
            for _ in range(2):
                draw_verbose.ellipse([lx - r, ly - r, lx + r, ly + r], outline=(0, 0, 0))
                r -= 1
            # White circle at transformed position (thick)
            out_pos = _compute_sathue_output_pos()
            if out_pos is not None:
                tx, ty = out_pos
                r = 5
                for _ in range(2):
                    draw_verbose.ellipse([tx - r, ty - r, tx + r, ty + r], outline=(255, 255, 255))
                    r -= 1

            # Update locked pixel display
            _update_sathue_lock_display()

        full_img, margin = _build_colormap_with_axis(img_verbose, title, xlabel, ylabel)
        sathue_img_full = full_img
        sathue_margin = margin
        if preserve_display_size:
            _update_sathue_image_content()
        else:
            _render_sathue_display()

    def _preview_size_changed_enough(last_size, new_size):
        """Return whether preview size changed enough to justify a redraw."""
        return any(abs(new_size[idx] - last_size[idx]) >= preview_resize_threshold for idx in range(2))

    def _get_preview_widget_size(key):
        """Return widget size as a (width, height) tuple."""
        widget = window[key].Widget
        return max(widget.winfo_width(), 0), max(widget.winfo_height(), 0)

    def _set_sat_preview_visible(visible):
        """Show or hide the right-side Sat/Hue preview column."""
        nonlocal sat_preview_visible, last_sat_preview_size
        sat_preview_visible = bool(visible)
        window['-SAT-IMAGE-COL-'].update(visible=sat_preview_visible)
        if not sat_preview_visible:
            window['-SAT-IMAGE-'].update(data=b'')
            last_sat_preview_size = (0, 0)

    def _set_sathue_color_lock(pixel_vals):
        """Apply a typed color to Sat/Hue Test and lock both input/output markers."""
        nonlocal sathue_locked, sathue_locked_pix, sathue_locked_input, sathue_luma_val
        if sathue_colorspace == 'YUV':
            y_val = int(np.clip(pixel_vals[0], 0, 255))
            u_val = int(np.clip(pixel_vals[1], 0, 255))
            v_val = int(np.clip(pixel_vals[2], 0, 255))
            cb = u_val - 128
            cr = v_val - 128
            sathue_luma_val = y_val
            window['-SAT-LUMA-'].update(value=y_val)
            window['-SAT-LUMA-SPIN-'].update(value=str(y_val))
            lock_x = _data_to_pix(cb)
            lock_y = SAT_COLORMAP_SIZE - 1 - _data_to_pix(cr)
            sathue_locked_input = (y_val, cb, cr)
        else:
            r_val = int(np.clip(pixel_vals[0], 0, 255))
            g_val = int(np.clip(pixel_vals[1], 0, 255))
            b_val = int(np.clip(pixel_vals[2], 0, 255))
            hue_arr, sat_arr, val_arr = _rgb2hsv(np.array([r_val]), np.array([g_val]), np.array([b_val]))
            hue = float(hue_arr[0])
            sat = float(sat_arr[0])
            val = float(val_arr[0])
            value_byte = int(np.clip(round(val * 255.0), 0, 255))
            sathue_luma_val = value_byte
            window['-SAT-LUMA-'].update(value=value_byte)
            window['-SAT-LUMA-SPIN-'].update(value=str(value_byte))
            lock_x = _data_to_pix(sat * _DATA_RANGE_MAX * np.cos(np.radians(hue)))
            lock_y = SAT_COLORMAP_SIZE - 1 - _data_to_pix(sat * _DATA_RANGE_MAX * np.sin(np.radians(hue)))
            sathue_locked_input = (hue, sat, val)

        lock_x = int(np.clip(lock_x, 0, SAT_COLORMAP_SIZE - 1))
        lock_y = int(np.clip(lock_y, 0, SAT_COLORMAP_SIZE - 1))
        sathue_locked = True
        sathue_locked_pix = (lock_x, lock_y)
        update_sathue_map(preserve_display_size=False)

    def _clear_sathue_color_lock():
        """Disable the forced Sat/Hue color lock and restore hover mode."""
        nonlocal sathue_locked, sathue_locked_pix, sathue_locked_input
        sathue_locked = False
        sathue_locked_pix = None
        sathue_locked_input = None
        update_sathue_map(preserve_display_size=True)

    def _render_sathue_display():
        """Scale the full colormap image to fit the widget and display it."""
        nonlocal sathue_display_scale, sathue_render_after_id
        sathue_render_after_id = None
        if sathue_img_full is None or not sat_preview_visible:
            return
        img_w, img_h = sathue_img_full.size
        col_widget = window['-SAT-IMAGE-COL-'].Widget
        preferred_side = current_main_display_size[1] if current_main_display_size[1] > 0 else 400
        max_side = max(preferred_side, 1)
        scale_ratio = min(2.0, max_side / img_w, max_side / img_h)
        sathue_display_scale = scale_ratio
        display_w = int(round(img_w * scale_ratio))
        display_h = int(round(img_h * scale_ratio))
        display_img = sathue_img_full.resize((display_w, display_h),
            Image.LANCZOS if hasattr(Image, 'LANCZOS') else Image.Resampling.LANCZOS)
        bio = io.BytesIO()
        display_img.save(bio, format='PNG')
        window['-SAT-IMAGE-'].update(data=bio.getvalue(), size=(display_w, display_h))

    def _update_sathue_image_content():
        """Refresh only the Sat/Hue preview image content while keeping its display size fixed."""
        if sathue_img_full is None or not sat_preview_visible:
            return
        display_w = max(int(round(sathue_img_full.size[0] * sathue_display_scale)), 1)
        display_h = max(int(round(sathue_img_full.size[1] * sathue_display_scale)), 1)
        display_img = sathue_img_full.resize((display_w, display_h),
            Image.LANCZOS if hasattr(Image, 'LANCZOS') else Image.Resampling.LANCZOS)
        bio = io.BytesIO()
        display_img.save(bio, format='PNG')
        window['-SAT-IMAGE-'].update(data=bio.getvalue())

    def _compute_sathue_output_pos():
        """Compute the output pixel coordinate after Hue/Saturation transform on locked input.
        Returns (pix_x, pix_y) in effective coords, or None if out of range."""
        if sathue_locked_input is None:
            return None
        c1, c2, c3 = sathue_locked_input
        hue_deg = sathue_hue_val
        sat_scale = sathue_sat_val
        if sathue_colorspace == 'YUV':
            cb = c2
            cr = c3
            h_rad = np.radians(hue_deg)
            cb2 = sat_scale * (cb * np.cos(h_rad) - cr * np.sin(h_rad))
            cr2 = sat_scale * (cb * np.sin(h_rad) + cr * np.cos(h_rad))
            cb2 = np.clip(cb2, -128, 127)
            cr2 = np.clip(cr2, -128, 127)
            tx = _data_to_pix(cb2)
            ty = _data_to_pix(-cr2)
        else:
            h = c1
            s = float(c2)
            h2 = (h + hue_deg) % 360
            s2 = np.clip(s * sat_scale, 0.0, 1.0)
            sx = _data_to_pix(s2 * _DATA_RANGE_MAX * np.cos(np.radians(h2)))
            sy = _data_to_pix(-s2 * _DATA_RANGE_MAX * np.sin(np.radians(h2)))
            tx, ty = sx, sy
        if 0 <= tx < SAT_COLORMAP_SIZE and 0 <= ty < SAT_COLORMAP_SIZE:
            return tx, ty
        return None

    def _get_sathue_input_at(pix_x, pix_y):
        """Get the (c1, c2, c3) input values at pixel in effective coords."""
        if sathue_colorspace == 'YUV':
            Y = sathue_luma_val
            Cb = _pix_to_data_int(pix_x)
            Cr = _pix_to_data_int(SAT_COLORMAP_SIZE - 1 - pix_y)
            return (Y, Cb, Cr)
        else:
            cx = _pix_to_data(pix_x) / _DATA_RANGE_MAX
            cy = _pix_to_data(SAT_COLORMAP_SIZE - 1 - pix_y) / _DATA_RANGE_MAX
            H = (np.arctan2(cy, cx) * 180.0 / np.pi + 360.0) % 360.0
            S = np.sqrt(cx ** 2 + cy ** 2)
            V = sathue_luma_val / 255.0
            return (H, max(S, 0.0), V)

    def _format_sathue_input_str(invals):
        """Format input pixel info string per the display template."""
        if sathue_colorspace == 'YUV':
            y_val, cb, cr = int(round(invals[0])), int(round(invals[1])), int(round(invals[2]))
            return f"YCbCr({y_val:3d}, {cb:3d}, {cr:3d}) <=> YUV({y_val:3d}, {cb+128:3d}, {cr+128:3d})"
        else:
            h_val, s_val, v_val = invals
            r, g, b = _hsv2rgb(np.array([h_val]), np.array([s_val]), np.array([v_val]))
            return f"HSV({h_val:3.1f}, {s_val:3.2f}, {v_val:3.2f}) <=> RGB({r[0]:3d}, {g[0]:3d}, {b[0]:3d})"

    def _format_sathue_output_str(outvals):
        """Format output pixel info string per the display template."""
        if sathue_colorspace == 'YUV':
            y_val, cb, cr = int(round(outvals[0])), int(round(outvals[1])), int(round(outvals[2]))
            return f"YCbCr({y_val:3d}, {cb:3d}, {cr:3d}) <=> YUV({y_val:3d}, {cb+128:3d}, {cr+128:3d})"
        else:
            r, g, b = outvals
            h_val, s_val, v_val = _rgb2hsv(np.array([r]), np.array([g]), np.array([b]))
            return f"HSV({h_val[0]:3.1f}, {s_val[0]:3.2f}, {v_val[0]:3.2f}) <=> RGB({r:3d}, {g:3d}, {b:3d})"

    def _get_sathue_output_at(pix_x, pix_y):
        """Get the output values at pixel in effective coords.
        YUV mode: returns (Y, Cb, Cr). RGB mode: returns (R, G, B) 0-255.
        Returns None if outside valid area."""
        if not (0 <= pix_x < SAT_COLORMAP_SIZE and 0 <= pix_y < SAT_COLORMAP_SIZE):
            return None
        if sathue_img_eff is None:
            return None
        # For HSV mode, outside circle is invalid
        if sathue_colorspace == 'RGB':
            cx = _pix_to_data(pix_x) / _DATA_RANGE_MAX
            cy = _pix_to_data(SAT_COLORMAP_SIZE - 1 - pix_y) / _DATA_RANGE_MAX
            if cx ** 2 + cy ** 2 > 1.0:
                return None
        px = sathue_img_eff.getpixel((pix_x, pix_y))
        r, g, b = px[0], px[1], px[2]
        if sathue_colorspace == 'YUV':
            # Convert RGB back to YCbCr
            r_f = np.float32(r)
            g_f = np.float32(g)
            b_f = np.float32(b)
            Y  = int(round(0.2126 * r_f + 0.7152 * g_f + 0.0722 * b_f))
            Cb = int(round(-0.114572 * r_f - 0.385428 * g_f + 0.5 * b_f))
            Cr = int(round(0.5 * r_f - 0.454153 * g_f - 0.045847 * b_f))
            return (np.clip(Y, 0, 255), np.clip(Cb, -128, 127), np.clip(Cr, -128, 127))
        return (r, g, b)

    def _format_sathue_pos_str(pix_x, pix_y, frozen=False):
        """Format position as (x-center, y-center) in effective coordinate space."""
        cx = _pix_to_data_int(pix_x)
        cy = _pix_to_data_int(SAT_COLORMAP_SIZE - 1 - pix_y)
        if not frozen:
            return f"({cx:4d},{cy:4d}) [Press Space to freeze this color]"
        return f"({cx:4d},{cy:4d}) [Frozen]"

    def _update_sathue_lock_display():
        """Update the input/output pixel text when a pixel is locked."""
        if not sathue_locked or sathue_locked_pix is None or sathue_locked_input is None:
            return
        lx, ly = sathue_locked_pix
        window['-INPUT-PIXEL-INFO-'].update(f"{_format_sathue_input_str(sathue_locked_input)}")
        # Compute transformed output
        out_pos = _compute_sathue_output_pos()
        if out_pos is not None:
            out_px = _get_sathue_output_at(*out_pos)
            if out_px is not None:
                window['-OUTPUT-PIXEL-INFO-'].update(f"{_format_sathue_output_str(out_px)}")
                window['-POSITION-INFO-'].update(_format_sathue_pos_str(lx, ly, frozen=True))
            else:
                window['-OUTPUT-PIXEL-INFO-'].update('(outside valid area)')
        else:
            window['-OUTPUT-PIXEL-INFO-'].update('(outside valid area)')

    def do_conversion(planar_in, values, depth, precision, algo_type, iclr, oclr, ifmt, ofmt, dump_enabled=False):
        bcsh = build_bcsh_config_from_dict(
            {
                'hue': values['-BCSH-hue-'],
                'saturation': values['-BCSH-sat-'],
                'contrast': values['-BCSH-contrast-'],
                'brightness': values['-BCSH-bright-'],
                'r_gain': values['-BCSH-r_gain-'],
                'g_gain': values['-BCSH-g_gain-'],
                'b_gain': values['-BCSH-b_gain-'],
                'r_offset': values['-BCSH-r_offset-'],
                'g_offset': values['-BCSH-g_offset-'],
                'b_offset': values['-BCSH-b_offset-'],
            },
            algo_type,
        )
        return run_selected_algo(planar_in, bcsh, depth, precision, algo_type, iclr, oclr, ifmt, ofmt, dump_enabled)

    def update_bcsh_norm_labels(window, values, algo_type):
        """Update all BCSH normalized value labels based on current slider values and algo type."""
        for _, k1, _, k2 in bcsh_names:
            for k in (k1, k2):
                raw_val = int(values[f'-BCSH-{k}-'])
                norm_str = get_bcsh_norm_value(k, raw_val, algo_type)
                window[f'-BCSH-{k}-NORM-'].update(norm_str)

    def set_bcsh_pair_value(window, values, slider_key, committed_value):
        """Synchronize one BCSH slider and its paired spinbox."""
        spin_key = get_bcsh_spin_key(slider_key)
        committed_value = int(committed_value)
        window[slider_key].update(value=committed_value)
        window[spin_key].update(value=str(committed_value))
        values[slider_key] = committed_value
        values[spin_key] = str(committed_value)

    def commit_bcsh_spin_value(window, values, spin_key):
        """Commit an edited BCSH spinbox value back to the paired slider."""
        slider_key = spin_key.replace("-SPIN-", "-")
        fallback_value = int(values[slider_key])
        committed_value = normalize_bcsh_spin_value(values.get(spin_key), fallback_value)
        set_bcsh_pair_value(window, values, slider_key, committed_value)
        return committed_value

    def emit_bcsh_ui_event(event_key, stop_default=False):
        """Build a Tk callback that forwards a custom UI event to the window."""
        def _handler(event=None):
            window.write_event_value(event_key, None)
            if stop_default:
                return "break"
            return None

        return _handler

    def update_rgb_gain_controls_for_algo_switch(window, values, old_algo_type, new_algo_type):
        """Update RGB gain sliders when switching between RK-family and eVideo CSC."""
        for gain_key in RGB_GAIN_KEYS:
            slider_key = f'-BCSH-{gain_key}-'
            current_value = int(values[slider_key])
            remapped_value = remap_rgb_gain_value_for_algo_switch(current_value, old_algo_type, new_algo_type)
            set_bcsh_pair_value(window, values, slider_key, remapped_value)

    def update_pixel_info(window, orig_x, orig_y):
        nonlocal current_planar_in, current_planar_out
        nonlocal current_input_is_yuv, current_output_is_yuv
        nonlocal current_scale_factor

        if current_planar_in is not None:
            # Map original coordinates to downsampled array coordinates
            ds_x = int(orig_x * current_scale_factor)
            ds_y = int(orig_y * current_scale_factor)

            h, w = current_planar_in.shape[1], current_planar_in.shape[2]

            if 0 <= ds_x < w and 0 <= ds_y < h:
                in_p0 = current_planar_in[0, ds_y, ds_x]
                in_p1 = current_planar_in[1, ds_y, ds_x]
                in_p2 = current_planar_in[2, ds_y, ds_x]
                in_str = f"({in_p0:4d}, {in_p1:4d}, {in_p2:4d})"
            else:
                in_str = "(----, ----, ----)"

            out_str = "(----, ----, ----)"
            if current_planar_out is not None:
                out_h, out_w = current_planar_out.shape[1], current_planar_out.shape[2]
                if 0 <= ds_x < out_w and 0 <= ds_y < out_h:
                    out_p0 = current_planar_out[0, ds_y, ds_x]
                    out_p1 = current_planar_out[1, ds_y, ds_x]
                    out_p2 = current_planar_out[2, ds_y, ds_x]
                    out_str = f"({out_p0:4d}, {out_p1:4d}, {out_p2:4d})"

            in_format = "yuv" if current_input_is_yuv else "rgb"
            out_format = "yuv" if current_output_is_yuv else "rgb"

            freeze_status = "[Frozen]" if is_pixel_info_frozen else "[Press Space to feeze this pixel]"
            window['-POSITION-INFO-'].update(f"({orig_x:4d},{orig_y:4d}) {freeze_status}")
            window['-INPUT-PIXEL-INFO-'].update(f"{in_format}: {in_str}")
            window['-OUTPUT-PIXEL-INFO-'].update(f"{out_format}: {out_str}")

    for _, k1, _, k2 in bcsh_names:
        for bcsh_key in (k1, k2):
            slider_key = f'-BCSH-{bcsh_key}-'
            spin_key = get_bcsh_spin_key(slider_key)
            window[spin_key].bind('<Return>', '+ENTER')
            window[spin_key].bind('<KP_Enter>', '+ENTER')
            window[spin_key].Widget.configure(command=emit_bcsh_ui_event(f'{spin_key}+STEP'))
            slider_widget = window[slider_key].Widget
            slider_widget.configure(takefocus=1)
            slider_widget.bind('<Button-1>', lambda event, widget=slider_widget: widget.focus_set(), add='+')
            slider_widget.bind('<Left>', emit_bcsh_ui_event(f'{slider_key}+LEFT', stop_default=True))
            slider_widget.bind('<Right>', emit_bcsh_ui_event(f'{slider_key}+RIGHT', stop_default=True))

    # Sat/Hue spin bindings
    for spin_key in ('-SAT-LUMA-SPIN-', '-SAT-HUE-SPIN-', '-SAT-SAT-SPIN-'):
        window[spin_key].bind('<Return>', '+ENTER')
        window[spin_key].bind('<KP_Enter>', '+ENTER')
        window[spin_key].Widget.configure(command=emit_bcsh_ui_event(f'{spin_key}+STEP'))

    # Sat/Hue slider left/right key bindings
    for slider_key in ('-SAT-LUMA-', '-SAT-HUE-', '-SAT-SAT-'):
        sw = window[slider_key].Widget
        sw.configure(takefocus=1)
        sw.bind('<Button-1>', lambda event, widget=sw: widget.focus_set(), add='+')
        sw.bind('<Left>', emit_bcsh_ui_event(f'{slider_key}+LEFT', stop_default=True))
        sw.bind('<Right>', emit_bcsh_ui_event(f'{slider_key}+RIGHT', stop_default=True))

    def update_multiline_readonly(window, key, value):
        widget = window[key].Widget
        widget.configure(state='normal')
        window[key].update(value=value)

    def trigger_convert(values, update_display=True, preserve_preview_size=False):
        nonlocal current_planar_in, current_planar_out
        nonlocal current_output_pixel_depth, current_input_pixel_depth
        nonlocal current_output_is_yuv, current_input_is_yuv
        nonlocal current_output_full_range, current_input_full_range
        nonlocal current_output_color, current_input_color
        nonlocal current_step1_coefs, current_step1_offset
        nonlocal current_step2_coefs, current_step2_offset
        nonlocal planar_in_full, current_input_file_params
        nonlocal current_scale_factor

        def get_preview_sampling_size(src_w, src_h, min_display_w, min_display_h):
            """Return the preview sampling size while optionally preserving the current display size."""
            if preserve_preview_size and current_planar_in is not None:
                prev_h, prev_w = current_planar_in.shape[1], current_planar_in.shape[2]
                if prev_w > 0 and prev_h > 0:
                    return min(prev_w, src_w), min(prev_h, src_h)

            col_widget = window['-MAIN-IMAGE-COL-'].Widget
            max_display_w = max(col_widget.winfo_width() - 20, min_display_w)
            max_display_h = max(col_widget.winfo_height() - 20, min_display_h)
            scale_factor = min(max_display_w / src_w, max_display_h / src_h, 1.0)
            disp_w = max(int(src_w * scale_factor), 1)
            disp_h = max(int(src_h * scale_factor), 1)
            return disp_w, disp_h

        set_color = values.get('-SET-COLOR-', False)

        if set_color:
            # Use the parsed color as a flat input image
            color_vals = parse_color_input(values.get('-COLOR-INPUT-', ''))
            if color_vals is None:
                return

            try:
                w = int(values['-WIDTH-']) if values['-WIDTH-'] else 256
                h = int(values['-HEIGHT-']) if values['-HEIGHT-'] else 256
                if w <= 0:
                    w = 256
                if h <= 0:
                    h = 256
                ifmt = get_fmt_from_display(values['-IN-FMT-'])
                iclr = get_clrspc_from_display(values['-IN-CLR-'])
                ofmt = get_fmt_from_display(values['-OUT-FMT-'])
                oclr = get_clrspc_from_display(values['-OUT-CLR-'])
                precision = int(values['-PRECISION-'])

                in_depth = get_pixel_depth(ifmt)
                out_depth = get_pixel_depth(ofmt)
                depth = max(in_depth, out_depth)

                window['-DISP-DEPTH-'].update(str(depth))
            except (ValueError, IndexError):
                return

            if h <= 0 or w <= 0:
                return

            # Build flat planar from color values
            max_val = (1 << depth) - 1
            planar_in_full = np.zeros((3, h, w), dtype=np.uint16 if depth > 8 else np.uint8)
            for i in range(3):
                planar_in_full[i, :, :] = int(np.clip(color_vals[i], 0, max_val))
            current_input_file_params = None

            # Downsample for display while preserving aspect ratio
            disp_w, disp_h = get_preview_sampling_size(w, h, 400, 400)
            scale_factor = min(disp_w / w, disp_h / h, 1.0)
            current_scale_factor = scale_factor
            if disp_w != w or disp_h != h:
                y_indices = np.linspace(0, h - 1, disp_h).astype(int)
                x_indices = np.linspace(0, w - 1, disp_w).astype(int)
                planar_in = planar_in_full[:, y_indices[:, None], x_indices]
            else:
                planar_in = planar_in_full

            algo_type = values.get('-BCSH-ALGO-TYPE-', ALGO_RK_HW_CSC)

            planar_out, step1_coefs, step1_offset, step2_coefs, step2_offset = do_conversion(
                planar_in, values, depth, precision, algo_type, iclr, oclr, ifmt, ofmt, False
            )

            current_planar_in = planar_in
            current_planar_out = planar_out
            current_step1_coefs = step1_coefs
            current_step1_offset = step1_offset
            current_step2_coefs = step2_coefs
            current_step2_offset = step2_offset
            current_output_pixel_depth = out_depth
            current_input_pixel_depth = in_depth
            current_output_is_yuv = is_yuv_format(ofmt)
            current_input_is_yuv = is_yuv_format(ifmt)

            _, orange = clrspc_to_mode_params(oclr)
            current_output_full_range = (orange == "F")
            ocs, _ = clrspc_to_mode_params(oclr)
            current_output_color = ColorSpace[ocs.upper()] if ocs.startswith("bt") else ColorSpace.BT709

            _, irange = clrspc_to_mode_params(iclr)
            current_input_full_range = (irange == "F")
            ics, _ = clrspc_to_mode_params(iclr)
            current_input_color = ColorSpace[ics.upper()] if ics.startswith("bt") else ColorSpace.BT709

            if update_display:
                display_result(window, values)
            return

        input_file = values['-INPUT-FILE-']
        if not input_file or not os.path.isfile(input_file):
            return

        try:
            w = int(values['-WIDTH-'])
            h = int(values['-HEIGHT-'])
            ifmt = get_fmt_from_display(values['-IN-FMT-'])
            iclr = get_clrspc_from_display(values['-IN-CLR-'])
            ofmt = get_fmt_from_display(values['-OUT-FMT-'])
            oclr = get_clrspc_from_display(values['-OUT-CLR-'])
            precision = int(values['-PRECISION-'])

            in_depth = get_pixel_depth(ifmt)
            out_depth = get_pixel_depth(ofmt)
            depth = max(in_depth, out_depth)

            # Update the displayed pixel depth on UI
            window['-DISP-DEPTH-'].update(str(depth))
        except (ValueError, IndexError):
            return

        if h <= 0 or w <= 0:
            return

        from run_csc import get_frame_size

        expected_size = get_frame_size(w, h, ifmt)
        actual_size = os.path.getsize(input_file)
        if actual_size < expected_size:
            current_main_display_size = (400, 400)
            window['-DISPLAY-SIZE-'].update(value=f"Error: file too small ({actual_size} < {expected_size})")
            window['-POSITION-INFO-'].update(value='')
            window['-INPUT-PIXEL-INFO-'].update(value='')
            window['-OUTPUT-PIXEL-INFO-'].update(value='')
            window['-IMAGE-'].update(data=b'', size=current_main_display_size)
            return

        try:
            file_params = (input_file, w, h, ifmt)
            if planar_in_full is None or current_input_file_params != file_params:
                planar_in_full = read_raw_to_planar(input_file, w, h, ifmt)
                current_input_file_params = file_params

            # Calculate downsampling factors
            disp_w, disp_h = get_preview_sampling_size(w, h, 640, 360)
            scale_factor = min(disp_w / w, disp_h / h, 1.0)
            current_scale_factor = scale_factor

            # Downsample the full resolution input
            y_indices = np.linspace(0, h - 1, disp_h).astype(int)
            x_indices = np.linspace(0, w - 1, disp_w).astype(int)
            planar_in = planar_in_full[:, y_indices[:, None], x_indices]

            algo_type = values.get('-BCSH-ALGO-TYPE-', ALGO_RK_HW_CSC)

            planar_out, step1_coefs, step1_offset, step2_coefs, step2_offset = do_conversion(
                planar_in, values, depth, precision, algo_type, iclr, oclr, ifmt, ofmt, False
            )

            if values.get('-DUMP-', False):
                do_conversion(planar_in_full, values, depth, precision, algo_type, iclr, oclr, ifmt, ofmt, True)

            current_planar_in = planar_in
            current_planar_out = planar_out
            current_step1_coefs = step1_coefs
            current_step1_offset = step1_offset
            current_step2_coefs = step2_coefs
            current_step2_offset = step2_offset
            current_output_pixel_depth = out_depth
            current_input_pixel_depth = in_depth
            current_output_is_yuv = is_yuv_format(ofmt)
            current_input_is_yuv = is_yuv_format(ifmt)

            _, orange = clrspc_to_mode_params(oclr)
            current_output_full_range = (orange == "F")
            ocs, _ = clrspc_to_mode_params(oclr)
            if ocs.startswith("bt"):
                current_output_color = ColorSpace[ocs.upper()]
            else:
                current_output_color = ColorSpace.BT709

            _, irange = clrspc_to_mode_params(iclr)
            current_input_full_range = (irange == "F")
            ics, _ = clrspc_to_mode_params(iclr)
            if ics.startswith("bt"):
                current_input_color = ColorSpace[ics.upper()]
            else:
                current_input_color = ColorSpace.BT709

            if update_display:
                display_result(window, values)
                if current_mouse_pos is not None:
                    update_pixel_info(window, current_mouse_pos[0], current_mouse_pos[1])
        except Exception as e:
            current_main_display_size = (400, 400)
            window['-DISPLAY-SIZE-'].update(value=f"Error: {e}")
            window['-POSITION-INFO-'].update(value='')
            window['-INPUT-PIXEL-INFO-'].update(value='')
            window['-OUTPUT-PIXEL-INFO-'].update(value='')
            window['-IMAGE-'].update(data=b'', size=current_main_display_size)

    def display_result(window, values):
        nonlocal current_planar_in, current_planar_out
        nonlocal current_step1_coefs, current_step1_offset
        nonlocal current_step2_coefs, current_step2_offset
        nonlocal current_scale_factor
        nonlocal current_main_display_size

        show_output = values.get('-SHOW-OUT-', False)
        old_main_display_size = current_main_display_size

        target_planar = current_planar_out if show_output else current_planar_in
        if target_planar is None:
            current_main_display_size = (400, 400)
            window['-DISPLAY-SIZE-'].update(value="No conversion result")
            window['-POSITION-INFO-'].update(value='')
            window['-INPUT-PIXEL-INFO-'].update(value='')
            window['-OUTPUT-PIXEL-INFO-'].update(value='')
            update_multiline_readonly(window, '-STEP1-COEFS-', 'None')
            update_multiline_readonly(window, '-STEP1-OFFSET-', 'None')
            update_multiline_readonly(window, '-STEP2-COEFS-', 'None')
            update_multiline_readonly(window, '-STEP2-OFFSET-', 'None')
            window['-IMAGE-'].update(data=b'', size=current_main_display_size)
            return

        target_is_yuv = current_output_is_yuv if show_output else current_input_is_yuv
        target_pixel_depth = current_output_pixel_depth if show_output else current_input_pixel_depth
        target_full_range = current_output_full_range if show_output else current_input_full_range
        target_color = current_output_color if show_output else current_input_color

        try:
            if target_is_yuv:
                y2r_config = CscCoefConfig()
                y2r_config.pixel_depth = target_pixel_depth
                y2r_config.coef_precision = 0
                y2r_mode = CscMode()
                y2r_mode.is_input_yuv = True
                y2r_mode.is_output_yuv = False
                y2r_mode.is_input_full_range = target_full_range
                y2r_mode.is_output_full_range = True
                y2r_mode.input_color_encoding = target_color
                y2r_mode.output_color_encoding = ColorSpace.BT709
                y2r_config.csc_mode = y2r_mode

                y2r_coefs, y2r_offset = get_csc_coefs(y2r_config, None)
                rgb_planar = apply_csc(target_planar, y2r_coefs, y2r_offset, 0, target_pixel_depth)
            else:
                rgb_planar = target_planar.copy()
                max_val = (1 << target_pixel_depth) - 1
                rgb_planar = np.clip(rgb_planar, 0, max_val)

            h, w = rgb_planar.shape[1], rgb_planar.shape[2]
            if target_pixel_depth > 8:
                rgb_8bit = (rgb_planar >> (target_pixel_depth - 8)).astype(np.uint8)
            else:
                rgb_8bit = rgb_planar.astype(np.uint8)

            rgb_interleaved = np.stack([rgb_8bit[0], rgb_8bit[1], rgb_8bit[2]], axis=-1)

            # target_planar is already downsampled to disp_w x disp_h
            img = Image.fromarray(rgb_interleaved, 'RGB')

            bio = io.BytesIO()
            img.save(bio, format='PNG')
            window['-IMAGE-'].update(data=bio.getvalue(), size=(w, h))
            current_main_display_size = (w, h)
            if sat_preview_visible and current_main_display_size != old_main_display_size:
                _render_sathue_display()

            iclr_disp = values['-IN-CLR-']
            oclr_disp = values['-OUT-CLR-']
            mode_desc = build_csc_mode_str(
                get_clrspc_from_display(iclr_disp),
                get_clrspc_from_display(oclr_disp),
            )
            step1_coef_str = str(current_step1_coefs).replace('\n', ' ') if current_step1_coefs is not None else "None"
            step1_offset_str = str(current_step1_offset) if current_step1_offset is not None else "None"
            step2_coef_str = str(current_step2_coefs).replace('\n', ' ') if current_step2_coefs is not None else "None"
            step2_offset_str = str(current_step2_offset) if current_step2_offset is not None else "None"
            window['-DISPLAY-SIZE-'].update(value=f"{w}x{h} ({mode_desc})")
            update_multiline_readonly(window, '-STEP1-COEFS-', step1_coef_str)
            update_multiline_readonly(window, '-STEP1-OFFSET-', step1_offset_str)
            update_multiline_readonly(window, '-STEP2-COEFS-', step2_coef_str)
            update_multiline_readonly(window, '-STEP2-OFFSET-', step2_offset_str)
        except Exception as e:
            window['-DISPLAY-SIZE-'].update(value=f"Display error: {e}")

    bcsh_keys = {f'-BCSH-{k}-' for _, k, _, _ in bcsh_names}.union({f'-BCSH-{k}-' for _, _, _, k in bcsh_names})
    bcsh_spin_keys = {get_bcsh_spin_key(key) for key in bcsh_keys}
    convert_keys = {'-IN-FMT-', '-OUT-FMT-', '-IN-CLR-', '-OUT-CLR-',
                    '-PRECISION-', '-WIDTH-', '-HEIGHT-', '-BCSH-ALGO-TYPE-'}
    convert_keys.add('-DUMP-')

    last_window_size = window.size

    # Initialize normalized value labels with default values
    default_bcsh_vals = {f'-BCSH-{k}-': 256 for _, k1, _, k2 in bcsh_names for k in (k1, k2)}
    update_bcsh_norm_labels(window, default_bcsh_vals, ALGO_RK_HW_CSC)
    update_sathue_map()
    _set_sat_preview_visible(False)

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, None):
            break

        if event == '-WINDOW-RESIZE-':
            main_preview_size = _get_preview_widget_size('-MAIN-IMAGE-COL-')
            sat_preview_size = _get_preview_widget_size('-SAT-IMAGE-COL-') if sat_preview_visible else (0, 0)
            main_changed = _preview_size_changed_enough(last_main_preview_size, main_preview_size)
            sat_changed = sat_preview_visible and _preview_size_changed_enough(last_sat_preview_size, sat_preview_size)
            if main_changed:
                last_main_preview_size = main_preview_size
            if sat_changed:
                last_sat_preview_size = sat_preview_size

            if sat_changed:
                if sathue_render_after_id is not None:
                    window.TKroot.after_cancel(sathue_render_after_id)
                sathue_render_after_id = window.TKroot.after(50, _render_sathue_display)

            if last_window_size != window.size:
                last_window_size = window.size
                if main_changed and current_planar_in is not None:
                    window.perform_long_operation(lambda: None, '-REDRAW-IMAGE-')
            continue
        elif event == '-REDRAW-IMAGE-':
            trigger_convert(values)
            continue
        elif event == '-SET-COLOR-':
            set_color = values.get('-SET-COLOR-', False)
            if set_color:
                window['-COLOR-INPUT-'].update(disabled=False)
            else:
                window['-COLOR-INPUT-'].update(disabled=True)
            trigger_convert(values)
            continue

        event_key, _, event_suffix = event.rpartition('+')

        if event in bcsh_keys:
            set_bcsh_pair_value(window, values, event, int(values[event]))
            update_bcsh_norm_labels(window, values, current_algo_type)
            trigger_convert(values, preserve_preview_size=True)
        elif event_key in bcsh_spin_keys and event_suffix == 'STEP':
            commit_bcsh_spin_value(window, values, event_key)
            update_bcsh_norm_labels(window, values, current_algo_type)
            trigger_convert(values, preserve_preview_size=True)
        elif event_key in bcsh_spin_keys and event_suffix == 'ENTER':
            commit_bcsh_spin_value(window, values, event_key)
            update_bcsh_norm_labels(window, values, current_algo_type)
            trigger_convert(values, preserve_preview_size=True)
        elif event_key in bcsh_keys and event_suffix in {'LEFT', 'RIGHT'}:
            delta = -1 if event_suffix == 'LEFT' else 1
            stepped_value = step_bcsh_value(values[event_key], delta)
            set_bcsh_pair_value(window, values, event_key, stepped_value)
            update_bcsh_norm_labels(window, values, current_algo_type)
            trigger_convert(values, preserve_preview_size=True)
        elif event == '-BCSH-ALGO-TYPE-':
            new_algo_type = values.get('-BCSH-ALGO-TYPE-', ALGO_RK_HW_CSC)
            update_rgb_gain_controls_for_algo_switch(window, values, current_algo_type, new_algo_type)
            current_algo_type = new_algo_type
            update_bcsh_norm_labels(window, values, current_algo_type)
            print(f"algo_type switch to: {new_algo_type}")
            trigger_convert(values, preserve_preview_size=True)
        elif event == '-RESET-BCSH-':
            algo_type = values.get('-BCSH-ALGO-TYPE-', ALGO_RK_HW_CSC)
            default_values = get_default_bcsh_raw_values(algo_type)
            for _, k1, _, k2 in bcsh_names:
                value1 = default_values[ui_bcsh_key_to_config_key(k1)]
                value2 = default_values[ui_bcsh_key_to_config_key(k2)]
                set_bcsh_pair_value(window, values, f'-BCSH-{k1}-', value1)
                set_bcsh_pair_value(window, values, f'-BCSH-{k2}-', value2)
            update_bcsh_norm_labels(window, values, algo_type)
            trigger_convert(values, preserve_preview_size=True)
        elif event == '-SAVE-OUT-':
            try:
                input_file = values['-INPUT-FILE-']
                w = int(values['-WIDTH-'])
                h = int(values['-HEIGHT-'])
                ifmt = get_fmt_from_display(values['-IN-FMT-'])
                iclr = get_clrspc_from_display(values['-IN-CLR-'])
                ofmt = get_fmt_from_display(values['-OUT-FMT-'])
                oclr = get_clrspc_from_display(values['-OUT-CLR-'])
                precision = int(values['-PRECISION-'])
                if not input_file or not os.path.isfile(input_file):
                    sg.popup_error("Please select a valid input file first!")
                    continue

                if current_planar_out is None or planar_in_full is None:
                    sg.popup_error("No output image generated yet. Check parameters.")
                    continue

                default_output = _get_default_output_path(input_file)
                save_path = sg.popup_get_file('Save output image as', save_as=True, default_path=default_output)
                if save_path:
                    # Calculate full resolution output
                    algo_type = values.get('-BCSH-ALGO-TYPE-', ALGO_RK_HW_CSC)
                    in_depth = get_pixel_depth(ifmt)
                    out_depth = get_pixel_depth(ofmt)
                    depth = max(in_depth, out_depth)

                    full_planar_out, _, _, _, _ = do_conversion(
                        planar_in_full, values, depth, precision, algo_type, iclr, oclr, ifmt, ofmt
                    )

                    write_planar_to_raw(full_planar_out, save_path, w, h, ofmt)
                    sg.popup(f"Saved successfully to:\n{save_path}", title="Success")
            except Exception as e:
                sg.popup_error(f"Failed to save output:\n{e}")
        elif event == '-COLOR-INPUT-+ENTER':
            trigger_convert(values)
        elif event == '-IN-CLR-' and values.get('-SET-COLOR-', False):
            _update_fmt_for_clrspc(window, values, fmt_display, get_clrspc_from_display(values['-IN-CLR-']))
            _update_clrspc_for_fmt(window, values, '-IN-CLR-', values['-IN-FMT-'])
            trigger_convert(values)
        elif event == '-IN-FMT-':
            fmt_base = get_fmt_from_display(values['-IN-FMT-']) & 0xF
            default_clrspc = clrspc_rgb[1] if fmt_base <= 0x2 else clrspc_yuv[3]
            _update_clrspc_for_fmt(window, values, '-IN-CLR-', values['-IN-FMT-'], default_clrspc)
            trigger_convert(values)
        elif event == '-OUT-FMT-':
            _update_clrspc_for_fmt(window, values, '-OUT-CLR-', values['-OUT-FMT-'])
            trigger_convert(values)
        elif event == '-SAT-SHOW-MAP-':
            _set_sat_preview_visible(values.get('-SAT-SHOW-MAP-', False))
            main_preview_size = _get_preview_widget_size('-MAIN-IMAGE-COL-')
            last_main_preview_size = main_preview_size
            if current_planar_in is not None:
                window.perform_long_operation(lambda: None, '-REDRAW-IMAGE-')
            if sat_preview_visible:
                window.TKroot.after(50, _render_sathue_display)
        elif event == '-SAT-SET-COLOR-':
            sathue_set_color_enabled = values.get('-SAT-SET-COLOR-', False)
            window['-SAT-COLOR-INPUT-'].update(disabled=not sathue_set_color_enabled)
            if sathue_set_color_enabled:
                color_vals = parse_color_input(values.get('-SAT-COLOR-INPUT-', ''))
                if color_vals is not None:
                    _set_sathue_color_lock(color_vals)
            else:
                _clear_sathue_color_lock()
        elif event == '-SAT-CLRSPC-':
            sathue_colorspace = values['-SAT-CLRSPC-']
            if sathue_set_color_enabled:
                color_vals = parse_color_input(values.get('-SAT-COLOR-INPUT-', ''))
                if color_vals is not None:
                    _set_sathue_color_lock(color_vals)
                    continue
            if sathue_locked and sathue_locked_pix is not None:
                sathue_locked_input = _get_sathue_input_at(*sathue_locked_pix)
            update_sathue_map()
        elif event == '-SAT-LUMA-':
            sathue_luma_val = int(values['-SAT-LUMA-'])
            window['-SAT-LUMA-SPIN-'].update(value=str(sathue_luma_val))
            if sathue_locked and not sathue_set_color_enabled:
                sathue_locked_input = _get_sathue_input_at(*sathue_locked_pix)
            update_sathue_map(preserve_display_size=True)
        elif event == '-SAT-HUE-':
            sathue_hue_val = int(values['-SAT-HUE-'])
            window['-SAT-HUE-SPIN-'].update(value=str(sathue_hue_val))
            update_sathue_map(preserve_display_size=True)
        elif event == '-SAT-SAT-':
            sathue_sat_val = int(values['-SAT-SAT-']) / 180.0
            window['-SAT-SAT-SPIN-'].update(value=f"{sathue_sat_val:.2f}")
            update_sathue_map(preserve_display_size=True)
        elif event_key.startswith('-SAT-') and event_key.endswith('-SPIN-') and event_suffix == 'STEP':
            slider_key = event_key.replace('-SPIN-', '-')
            if event_key == '-SAT-LUMA-SPIN-':
                v = int(values[event_key])
                v = max(0, min(255, v))
                sathue_luma_val = v
                window[slider_key].update(value=v)
            elif event_key == '-SAT-HUE-SPIN-':
                v = int(values[event_key])
                v = max(-180, min(180, v))
                sathue_hue_val = v
                window[slider_key].update(value=v)
            else:
                try:
                    v = float(values[event_key])
                    v = max(0.0, min(2.0, v))
                except ValueError:
                    v = sathue_sat_val
                sathue_sat_val = v
                window[slider_key].update(value=int(round(v * 180)))
            update_sathue_map(preserve_display_size=True)
        elif event_key.startswith('-SAT-') and event_key.endswith('-SPIN-') and event_suffix == 'ENTER':
            slider_key = event_key.replace('-SPIN-', '-')
            if event_key == '-SAT-LUMA-SPIN-':
                try:
                    v = int(values[event_key])
                    v = max(0, min(255, v))
                except ValueError:
                    v = sathue_luma_val
                sathue_luma_val = v
                window[slider_key].update(value=v)
                window[event_key].update(value=str(v))
                if sathue_locked:
                    sathue_locked_input = _get_sathue_input_at(*sathue_locked_pix)
            elif event_key == '-SAT-HUE-SPIN-':
                try:
                    v = int(values[event_key])
                    v = max(-180, min(180, v))
                except ValueError:
                    v = sathue_hue_val
                sathue_hue_val = v
                window[slider_key].update(value=v)
                window[event_key].update(value=str(v))
            else:
                try:
                    v = float(values[event_key])
                    v = max(0.0, min(2.0, v))
                except ValueError:
                    v = sathue_sat_val
                sathue_sat_val = v
                window[slider_key].update(value=int(round(v * 180)))
                window[event_key].update(value=f"{v:.2f}")
            update_sathue_map(preserve_display_size=True)
        elif event == '-SAT-HUE-RESET-':
            sathue_hue_val = 0
            window['-SAT-HUE-'].update(value=0)
            window['-SAT-HUE-SPIN-'].update(value='0')
            update_sathue_map(preserve_display_size=True)
        elif event == '-SAT-SAT-RESET-':
            sathue_sat_val = 1.0
            window['-SAT-SAT-'].update(value=180)
            window['-SAT-SAT-SPIN-'].update(value='1.00')
            update_sathue_map(preserve_display_size=True)
        elif event == '-SAT-COLOR-INPUT-+ENTER':
            if sathue_set_color_enabled:
                color_vals = parse_color_input(values.get('-SAT-COLOR-INPUT-', ''))
                if color_vals is not None:
                    _set_sathue_color_lock(color_vals)
        elif event_key.startswith('-SAT-') and event_key.endswith('-') and event_suffix in {'LEFT', 'RIGHT'}:
            delta = -1 if event_suffix == 'LEFT' else 1
            cur = int(values[event_key])
            if event_key == '-SAT-LUMA-':
                cur = max(0, min(255, cur + delta))
                sathue_luma_val = cur
                window['-SAT-LUMA-SPIN-'].update(value=str(cur))
                window[event_key].update(value=cur)
                if sathue_locked and not sathue_set_color_enabled:
                    sathue_locked_input = _get_sathue_input_at(*sathue_locked_pix)
            elif event_key == '-SAT-HUE-':
                cur = max(-180, min(180, cur + delta))
                sathue_hue_val = cur
                window['-SAT-HUE-SPIN-'].update(value=str(cur))
                window[event_key].update(value=cur)
            elif event_key == '-SAT-SAT-':
                new_val = sathue_sat_val + delta / 180.0
                new_val = max(0.0, min(2.0, new_val))
                sathue_sat_val = new_val
                sv = int(round(new_val * 180))
                window[event_key].update(value=sv)
                window['-SAT-SAT-SPIN-'].update(value=f"{new_val:.2f}")
            update_sathue_map(preserve_display_size=True)
        elif event in convert_keys:
            trigger_convert(values)
        elif event in ['-SHOW-IN-', '-SHOW-OUT-']:
            display_result(window, values)
        elif event == '-INPUT-FILE-':
            if values['-INPUT-FILE-'] and os.path.isfile(values['-INPUT-FILE-']):
                filepath = values['-INPUT-FILE-']
                basename = os.path.basename(filepath).lower()
                ext = os.path.splitext(basename)[1]

                # 1. Guess by extension
                if ext == '.yuv':
                    # YUV420SP_NV12 is 0x9, BT709_Full is 5
                    yuv_fmt = next((f for f in fmt_display if f.startswith('0x9 ')), None)
                    if yuv_fmt:
                        window['-IN-FMT-'].update(value=yuv_fmt)
                        values['-IN-FMT-'] = yuv_fmt
                    if yuv_fmt:
                        _update_clrspc_for_fmt(window, values, '-IN-CLR-', yuv_fmt, clrspc_yuv[3])
                elif ext == '.rgb':
                    # RGB888 is 0x0, RGB_Full is 1
                    rgb_fmt = next((f for f in fmt_display if f.startswith('0x0 ')), None)
                    if rgb_fmt:
                        window['-IN-FMT-'].update(value=rgb_fmt)
                        values['-IN-FMT-'] = rgb_fmt
                    if rgb_fmt:
                        _update_clrspc_for_fmt(window, values, '-IN-CLR-', rgb_fmt, clrspc_rgb[1])

                # 2. Guess by resolution in basename
                m_res = re.search(r'(\d+)x(\d+)', basename)
                if m_res:
                    w_str, h_str = m_res.group(1), m_res.group(2)
                    window['-WIDTH-'].update(value=w_str)
                    values['-WIDTH-'] = w_str
                    window['-HEIGHT-'].update(value=h_str)
                    values['-HEIGHT-'] = h_str

                trigger_convert(values)
        elif event == '-IMAGE-+ENTER':
            is_mouse_in_image = True
            is_mouse_in_sathue = False
            if is_pixel_info_frozen and current_mouse_pos is not None:
                update_pixel_info(window, current_mouse_pos[0], current_mouse_pos[1])
        elif event == '-IMAGE-+LEAVE':
            is_mouse_in_image = False
        elif event == '-SAT-IMAGE-+ENTER':
            is_mouse_in_sathue = True
            is_mouse_in_image = False
            if sathue_locked:
                _update_sathue_lock_display()
        elif event == '-SAT-IMAGE-+LEAVE':
            is_mouse_in_sathue = False
            if is_mouse_in_image and is_pixel_info_frozen and current_mouse_pos is not None:
                update_pixel_info(window, current_mouse_pos[0], current_mouse_pos[1])
            elif not sathue_locked:
                window['-INPUT-PIXEL-INFO-'].update('(hover over image)')
                window['-OUTPUT-PIXEL-INFO-'].update('')
                window['-POSITION-INFO-'].update('')
        elif event == '-IMAGE-+MOTION':
            if current_planar_in is not None and not is_pixel_info_frozen:
                e = window['-IMAGE-'].user_bind_event
                # tkinter event coordinates are relative to the widget
                widget_x, widget_y = e.x, e.y

                # Image widget padding/border is small but we use coordinates directly
                # Map to original image coordinates using current_scale_factor
                orig_x = int(widget_x / current_scale_factor)
                orig_y = int(widget_y / current_scale_factor)

                current_mouse_pos = (orig_x, orig_y)
                update_pixel_info(window, orig_x, orig_y)
        elif event == '-SAT-IMAGE-+MOTION':
            if sathue_locked:
                _update_sathue_lock_display()
            elif sathue_img_full is not None:
                e = window['-SAT-IMAGE-'].user_bind_event
                wx, wy = e.x, e.y
                eff_x = int(wx / sathue_display_scale) - sathue_margin
                eff_y = int(wy / sathue_display_scale) - sathue_margin
                if 0 <= eff_x < SAT_COLORMAP_SIZE and 0 <= eff_y < SAT_COLORMAP_SIZE:
                    invals = _get_sathue_input_at(eff_x, eff_y)
                    outpx = _get_sathue_output_at(eff_x, eff_y)
                    window['-INPUT-PIXEL-INFO-'].update(f"{_format_sathue_input_str(invals)}")
                    window['-POSITION-INFO-'].update(_format_sathue_pos_str(eff_x, eff_y, frozen=False))
                    if outpx is not None:
                        window['-OUTPUT-PIXEL-INFO-'].update(f"{_format_sathue_output_str(outpx)}")
                    else:
                        window['-OUTPUT-PIXEL-INFO-'].update('(outside valid area)')
                    sathue_mouse_pos = (eff_x, eff_y)

        elif event == ' ':  # Space key
            if is_mouse_in_sathue and sathue_mouse_pos is not None:
                if sathue_set_color_enabled:
                    continue
                if sathue_locked:
                    # Unlock
                    sathue_locked = False
                    sathue_locked_pix = None
                    sathue_locked_input = None
                    # Restore hover display after unlocking
                    if sathue_mouse_pos is not None:
                        invals = _get_sathue_input_at(*sathue_mouse_pos)
                        outpx = _get_sathue_output_at(*sathue_mouse_pos)
                        window['-INPUT-PIXEL-INFO-'].update(f"{_format_sathue_input_str(invals)}")
                        window['-POSITION-INFO-'].update(_format_sathue_pos_str(*sathue_mouse_pos, frozen=False))
                        if outpx:
                            window['-OUTPUT-PIXEL-INFO-'].update(f"{_format_sathue_output_str(outpx)}")
                        else:
                            window['-OUTPUT-PIXEL-INFO-'].update('(outside valid area)')
                else:
                    # Lock
                    sathue_locked = True
                    sathue_locked_pix = sathue_mouse_pos
                    sathue_locked_input = _get_sathue_input_at(*sathue_mouse_pos)
                update_sathue_map()
            elif is_mouse_in_image:
                is_pixel_info_frozen = not is_pixel_info_frozen
                if current_mouse_pos is not None:
                    update_pixel_info(window, current_mouse_pos[0], current_mouse_pos[1])

    window.close()
