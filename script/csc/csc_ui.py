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
    g_r2y_mat_bt709,
    g_y2r_mat_bt709
)
from get_csc_coef_hsv import (
    ALGO_RK_HW_CSC,
    ALGO_RK_SW_CSC,
    ALGO_EVIDEO_CSC,
    ALGO_EVIDEO_CSC_PLAN_A,
    ALGO_EVIDEO_CSC_PLAN_B,
    ALGO_EVIDEO_CSC_PLAN_C,
    normalize_algo_type,
    get_evideo_plan_a_steps,
    get_evideo_plan_a_runtime_steps,
    get_evideo_plan_b_steps,
    rgb_to_hsv,
    hsv_to_rgb,
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
    is_image_file,
    read_image_to_planar,
    read_raw_to_planar,
    write_planar_to_raw,
    apply_csc,
    build_csc_config,
    convert_planar,
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

# VOP channel swap modes exposed in the BCSH Config tab.
CHANNEL_SWAP_TYPES = ["None", "V1_SWAP", "V2_Y2R_R2R", "V2_R2Y_R2R", "V2_Y2R_Y2Y", "V2_R2Y_Y2Y"]


def _apply_step2_channel_swap_display(channel_swap, step2_coefs, step2_offset, input_is_yuv, output_is_yuv):
    """将 VOP channel swap 通道置换作用到 step2 系数上，用于 UI 显示。

    置换规则与内核 rockchip_swap_color_channel() 保持一致：
    - swap_mat = [[0,0,1],[1,0,0],[0,1,0]]（RGB->BRG / YUV->VYU），inv 为其逆
    - V1_SWAP: 输入 RGB 时后乘 swap_mat，输出 YUV 时前乘 swap_mat
    - V2_Y2R_R2R: 后乘 swap_mat；V2_R2Y_R2R: 前乘 inv_swap_mat
    - V2_Y2R_Y2Y: 前乘 swap_mat；V2_R2Y_Y2Y: 后乘 inv_swap_mat
    """
    if channel_swap == 'None' or step2_coefs is None:
        return step2_coefs, step2_offset

    swap_mat = np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0]], dtype=step2_coefs.dtype)
    inv_swap_mat = np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]], dtype=step2_coefs.dtype)

    coefs = step2_coefs
    offset = step2_offset

    if channel_swap == 'V1_SWAP':
        if not input_is_yuv:
            coefs = coefs @ swap_mat
        if output_is_yuv:
            coefs = swap_mat @ coefs
            if offset is not None:
                offset = swap_mat @ offset
    elif channel_swap == 'V2_Y2R_R2R':
        coefs = coefs @ swap_mat
    elif channel_swap == 'V2_R2Y_R2R':
        coefs = inv_swap_mat @ coefs
        if offset is not None:
            offset = inv_swap_mat @ offset
    elif channel_swap == 'V2_Y2R_Y2Y':
        coefs = swap_mat @ coefs
        if offset is not None:
            offset = swap_mat @ offset
    elif channel_swap == 'V2_R2Y_Y2Y':
        coefs = coefs @ inv_swap_mat

    return coefs, offset


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
    evideo_algos = {ALGO_EVIDEO_CSC, ALGO_EVIDEO_CSC_PLAN_A, ALGO_EVIDEO_CSC_PLAN_B, ALGO_EVIDEO_CSC_PLAN_C}
    is_evideo = algo_type in evideo_algos

    if param_key in ("r_gain", "g_gain", "b_gain"):
        if is_evideo:
            norm = raw_value / 64.0
        else:
            norm = raw_value / 256.0
        return f"{norm: 4.2f}"
    elif param_key in ("r_offset", "g_offset", "b_offset"):
        if is_evideo:
            norm = (raw_value - 256) / 256.0
        else:
            norm = (raw_value - 256) / 2048.0
        return f"{norm: 4.2f}"
    elif param_key == "bright":
        if is_evideo:
            norm = (raw_value - 256) / 256.0
        else:
            norm = (raw_value - 256) / 1024.0
        return f"{norm: 4.2f}"
    elif param_key == "contrast":
        norm = raw_value / 256.0
        return f"{norm: 4.2f}"
    elif param_key == "sat":
        norm = raw_value / 256.0
        return f"{norm: 4.2f}"
    elif param_key == "hue":
        if is_evideo:
            norm = (raw_value - 256) * 180.0 / 256.0
        else:
            norm = (raw_value - 256) * 30.0 / 256.0
        return f"{norm: 4.2f}"
    return ""


def remap_rgb_gain_value_for_algo_switch(value, old_algo_type, new_algo_type):
    """Remap raw RGB gain when switching between RK-family and eVideo CSC."""
    if old_algo_type == new_algo_type:
        return int(value)

    remapped = float(value)
    rk_algo_types = {ALGO_RK_HW_CSC, ALGO_RK_SW_CSC}
    evideo_algo_types = {ALGO_EVIDEO_CSC, ALGO_EVIDEO_CSC_PLAN_A, ALGO_EVIDEO_CSC_PLAN_B, ALGO_EVIDEO_CSC_PLAN_C}
    if old_algo_type in rk_algo_types and new_algo_type in evideo_algo_types:
        remapped /= 4.0
    elif old_algo_type in evideo_algo_types and new_algo_type in rk_algo_types:
        remapped *= 4.0

    return int(np.clip(round(remapped), 0, 511))


# ---- Colormap conversion helpers ----

def _ycbcr2rgb(y, cb, cr, clip=True):
    """Apply the BT.709 YCbCr->RGB matrix.  When clip is True (default), round to
    nearest integer and clip to [0, 255], returning uint8 arrays (R, G, B).
    When clip is False, skip the clip+uint8 conversion and return float32
    arrays with the raw mathematical values (may be negative or > 255); this
    lets callers detect out-of-gamut pixels before display (e.g. colormap
    builders that want to mark clipped regions)."""
    ycbcr = np.stack([np.asarray(y, dtype=np.float32),
                       np.asarray(cb, dtype=np.float32),
                       np.asarray(cr, dtype=np.float32)], axis=-1)
    rgb = np.dot(ycbcr.reshape(-1, 3), g_y2r_mat_bt709.T).reshape(ycbcr.shape)
    if clip:
        r = np.clip(rgb[..., 0] + 0.5, 0, 255).astype(np.uint8)
        g = np.clip(rgb[..., 1] + 0.5, 0, 255).astype(np.uint8)
        b = np.clip(rgb[..., 2] + 0.5, 0, 255).astype(np.uint8)
        return r, g, b
    return rgb[..., 0], rgb[..., 1], rgb[..., 2]


def _rgb2ycbcr(r, g, b):
    """Convert RGB (0-255) to YCbCr (BT.709), returns Y, Cb, Cr as float32 arrays (0-255)."""
    rgb = np.stack([np.asarray(r, dtype=np.float32),
                    np.asarray(g, dtype=np.float32),
                    np.asarray(b, dtype=np.float32)], axis=-1)
    ycbcr = np.dot(rgb.reshape(-1, 3), g_r2y_mat_bt709.T).reshape(rgb.shape)
    y = ycbcr[..., 0]
    cb = ycbcr[..., 1] + 128.0
    cr = ycbcr[..., 2] + 128.0
    return y, cb, cr


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
    rc = np.divide(maxc - r, delta, out=np.zeros_like(maxc), where=cond)
    gc = np.divide(maxc - g, delta, out=np.zeros_like(maxc), where=cond)
    bc = np.divide(maxc - b, delta, out=np.zeros_like(maxc), where=cond)
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


SAT_HS_TYPES = ["HSV", "HSL", "HSI", "HSY"]
SAT_COLORSPACE_OPTIONS = ["YCbCr", "HSV", "YCbCr=>HSV", "HSV=>YCbCr"]
_HSY_LUMA_WEIGHTS = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)


def _normalize_hs_type(hs_type):
    """Normalize HS-family names to the supported tokens."""
    hs_text = str(hs_type).upper()
    return hs_text if hs_text in SAT_HS_TYPES else "HSV"


def _get_hs_space_label(hs_type):
    """Return the third-component label for the selected HS-family space."""
    hs_space = _normalize_hs_type(hs_type)
    return {"HSV": "V", "HSL": "L", "HSI": "I", "HSY": "Y"}[hs_space]


def _rgb2hsl(r, g, b):
    """Convert RGB (0-255) to HSL, returns h(0-360), s(0-1), l(0-1)."""
    r_n = np.asarray(r, dtype=np.float32) / 255.0
    g_n = np.asarray(g, dtype=np.float32) / 255.0
    b_n = np.asarray(b, dtype=np.float32) / 255.0
    maxc = np.maximum(np.maximum(r_n, g_n), b_n)
    minc = np.minimum(np.minimum(r_n, g_n), b_n)
    delta = maxc - minc
    h = np.zeros_like(maxc)
    cond = delta > 1e-6
    rc = np.divide(maxc - r_n, delta, out=np.zeros_like(maxc), where=cond)
    gc = np.divide(maxc - g_n, delta, out=np.zeros_like(maxc), where=cond)
    bc = np.divide(maxc - b_n, delta, out=np.zeros_like(maxc), where=cond)
    h = np.where(cond & (maxc == r_n), bc - gc, h)
    h = np.where(cond & (maxc == g_n), 2.0 + rc - bc, h)
    h = np.where(cond & (maxc == b_n), 4.0 + gc - rc, h)
    h = (h / 6.0) % 1.0 * 360.0
    l = (maxc + minc) * 0.5
    denom = 1.0 - np.abs(2.0 * l - 1.0)
    valid = cond & (denom > 1e-6)
    s = np.divide(delta, denom, out=np.zeros_like(delta), where=valid)
    return h, s, l


def _hsl2rgb(h, s, l):
    """Convert HSL to RGB, returns 0-255 uint8 arrays."""
    h = np.asarray(h, dtype=np.float32) % 360.0
    s = np.asarray(s, dtype=np.float32)
    l = np.asarray(l, dtype=np.float32)
    c = (1.0 - np.abs(2.0 * l - 1.0)) * s
    x = c * (1.0 - np.abs((h / 60.0) % 2.0 - 1.0))
    m = l - c * 0.5
    r = np.zeros_like(h)
    g = np.zeros_like(h)
    b = np.zeros_like(h)
    for lo, hi, rc, gc, bc in [(0, 60, c, x, 0), (60, 120, x, c, 0), (120, 180, 0, c, x),
                                (180, 240, 0, x, c), (240, 300, x, 0, c), (300, 360, c, 0, x)]:
        mask = (h >= lo) & (h < hi)
        r[mask] = rc[mask] if isinstance(rc, np.ndarray) else rc
        g[mask] = gc[mask] if isinstance(gc, np.ndarray) else gc
        b[mask] = bc[mask] if isinstance(bc, np.ndarray) else bc
    r = np.clip((r + m) * 255.0 + 0.5, 0, 255).astype(np.uint8)
    g = np.clip((g + m) * 255.0 + 0.5, 0, 255).astype(np.uint8)
    b = np.clip((b + m) * 255.0 + 0.5, 0, 255).astype(np.uint8)
    return r, g, b


def _rgb2hsi(r, g, b):
    """Convert RGB (0-255) to HSI, returns h(0-360), s(0-1), i(0-1)."""
    r_n = np.asarray(r, dtype=np.float32) / 255.0
    g_n = np.asarray(g, dtype=np.float32) / 255.0
    b_n = np.asarray(b, dtype=np.float32) / 255.0
    intensity = (r_n + g_n + b_n) / 3.0
    minc = np.minimum(np.minimum(r_n, g_n), b_n)
    sum_rgb = r_n + g_n + b_n
    sat = np.where(sum_rgb > 1e-6, 1.0 - 3.0 * minc / sum_rgb, 0.0)
    num = 0.5 * ((r_n - g_n) + (r_n - b_n))
    den = np.sqrt((r_n - g_n) ** 2 + (r_n - b_n) * (g_n - b_n))
    cos_theta = np.divide(num, den, out=np.ones_like(num), where=den > 1e-6)
    theta = np.degrees(np.arccos(np.clip(cos_theta, -1.0, 1.0)))
    hue = np.where(b_n <= g_n, theta, 360.0 - theta)
    hue = np.where(den > 1e-6, hue, 0.0)
    return hue, np.clip(sat, 0.0, 1.0), np.clip(intensity, 0.0, 1.0)


def _hsi2rgb(h, s, i):
    """Convert HSI to RGB, returns 0-255 uint8 arrays."""
    h = np.asarray(h, dtype=np.float32) % 360.0
    s = np.clip(np.asarray(s, dtype=np.float32), 0.0, 1.0)
    intensity = np.clip(np.asarray(i, dtype=np.float32), 0.0, 1.0)
    h_prime = h / 60.0
    z = 1.0 - np.abs(np.mod(h_prime, 2.0) - 1.0)
    c = np.divide(3.0 * intensity * s, 1.0 + z, out=np.zeros_like(h, dtype=np.float32), where=(1.0 + z) > 1e-6)
    x = c * z
    m = intensity * (1 - s)
    r = np.zeros_like(h, dtype=np.float32)
    g = np.zeros_like(h, dtype=np.float32)
    b = np.zeros_like(h, dtype=np.float32)

    for lo, hi, rc, gc, bc in [
        (0.0, 1.0, c, x, 0.0),
        (1.0, 2.0, x, c, 0.0),
        (2.0, 3.0, 0.0, c, x),
        (3.0, 4.0, 0.0, x, c),
        (4.0, 5.0, x, 0.0, c),
        (5.0, 6.0, c, 0.0, x),
    ]:
        mask = (h_prime >= lo) & (h_prime < hi)
        r[mask] = rc[mask] if isinstance(rc, np.ndarray) else rc
        g[mask] = gc[mask] if isinstance(gc, np.ndarray) else gc
        b[mask] = bc[mask] if isinstance(bc, np.ndarray) else bc

    r += m
    g += m
    b += m

    r = np.clip(r * 255.0 + 0.5, 0, 255).astype(np.uint8)
    g = np.clip(g * 255.0 + 0.5, 0, 255).astype(np.uint8)
    b = np.clip(b * 255.0 + 0.5, 0, 255).astype(np.uint8)
    return r, g, b


def _hsy_hue_basis(h):
    """Return the unit-chroma RGB sector basis for an HSY hue."""
    hue = np.asarray(h, dtype=np.float32) % 360.0
    h_prime = hue / 60.0
    z = 1.0 - np.abs(np.mod(h_prime, 2.0) - 1.0)
    r = np.zeros_like(hue, dtype=np.float32)
    g = np.zeros_like(hue, dtype=np.float32)
    b = np.zeros_like(hue, dtype=np.float32)
    for lo, hi, rc, gc, bc in [
        (0.0, 1.0, 1.0, z, 0.0),
        (1.0, 2.0, z, 1.0, 0.0),
        (2.0, 3.0, 0.0, 1.0, z),
        (3.0, 4.0, 0.0, z, 1.0),
        (4.0, 5.0, z, 0.0, 1.0),
        (5.0, 6.0, 1.0, 0.0, z),
    ]:
        mask = (h_prime >= lo) & (h_prime < hi)
        r[mask] = rc[mask] if isinstance(rc, np.ndarray) else rc
        g[mask] = gc[mask] if isinstance(gc, np.ndarray) else gc
        b[mask] = bc[mask] if isinstance(bc, np.ndarray) else bc
    return np.stack([r, g, b], axis=-1)


def _hsy_chroma_limit(hue, lum):
    """Return the maximum HSY chroma allowed by the fixed BT.709 luma."""
    basis = _hsy_hue_basis(hue)
    basis_luma = np.sum(basis * _HSY_LUMA_WEIGHTS, axis=-1)
    lower = np.divide(lum, basis_luma, out=np.zeros_like(lum), where=basis_luma > 1e-6)
    upper = np.divide(1.0 - lum, 1.0 - basis_luma, out=np.zeros_like(lum), where=(1.0 - basis_luma) > 1e-6)
    return np.where(lum <= basis_luma, lower, upper)


def _hsy_full_sat_rgb(h, y):
    """Return the full-saturation RGB endpoint for the custom HSY model."""
    hue = np.asarray(h, dtype=np.float32) % 360.0
    lum = np.clip(np.asarray(y, dtype=np.float32), 0.0, 1.0)
    h_prime = hue / 60.0
    z = 1.0 - np.abs(np.mod(h_prime, 2.0) - 1.0)
    chroma = _hsy_chroma_limit(hue, lum)
    x = chroma * z
    r1 = np.zeros_like(hue, dtype=np.float32)
    g1 = np.zeros_like(hue, dtype=np.float32)
    b1 = np.zeros_like(hue, dtype=np.float32)
    for lo, hi, rc, gc, bc in [
        (0.0, 1.0, chroma, x, 0.0),
        (1.0, 2.0, x, chroma, 0.0),
        (2.0, 3.0, 0.0, chroma, x),
        (3.0, 4.0, 0.0, x, chroma),
        (4.0, 5.0, x, 0.0, chroma),
        (5.0, 6.0, chroma, 0.0, x),
    ]:
        mask = (h_prime >= lo) & (h_prime < hi)
        r1[mask] = rc[mask] if isinstance(rc, np.ndarray) else rc
        g1[mask] = gc[mask] if isinstance(gc, np.ndarray) else gc
        b1[mask] = bc[mask] if isinstance(bc, np.ndarray) else bc
    rgb1 = np.stack([r1, g1, b1], axis=-1)
    m = lum - np.sum(rgb1 * _HSY_LUMA_WEIGHTS, axis=-1)
    return np.clip(rgb1 + m[..., None], 0.0, 1.0)


def _rgb2hsy(r, g, b):
    """Convert RGB (0-255) to the custom HSY space used by the UI."""
    hue, _, _ = _rgb2hsv(r, g, b)
    rgb = np.stack([np.asarray(r, dtype=np.float32),
                    np.asarray(g, dtype=np.float32),
                    np.asarray(b, dtype=np.float32)], axis=-1) / 255.0
    lum = np.sum(rgb * _HSY_LUMA_WEIGHTS, axis=-1)
    gray = np.repeat(lum[..., None], 3, axis=-1)
    boundary = _hsy_full_sat_rgb(hue, lum)
    delta_boundary = boundary - gray
    delta_rgb = rgb - gray
    max_axis = np.argmax(np.abs(delta_boundary), axis=-1)
    boundary_axis = np.take_along_axis(delta_boundary, max_axis[..., None], axis=-1)[..., 0]
    rgb_axis = np.take_along_axis(delta_rgb, max_axis[..., None], axis=-1)[..., 0]
    sat = np.where(np.abs(boundary_axis) > 1e-6, rgb_axis / boundary_axis, 0.0)
    return hue, np.clip(sat, 0.0, 1.0), np.clip(lum, 0.0, 1.0)


def _hsy2rgb(h, s, y):
    """Convert the custom HSY space to RGB, returns 0-255 uint8 arrays."""
    hue = np.asarray(h, dtype=np.float32) % 360.0
    sat = np.clip(np.asarray(s, dtype=np.float32), 0.0, 1.0)
    lum = np.clip(np.asarray(y, dtype=np.float32), 0.0, 1.0)
    h_prime = hue / 60.0
    z = 1.0 - np.abs(np.mod(h_prime, 2.0) - 1.0)
    chroma = sat * _hsy_chroma_limit(hue, lum)
    x = chroma * z
    r1 = np.zeros_like(hue, dtype=np.float32)
    g1 = np.zeros_like(hue, dtype=np.float32)
    b1 = np.zeros_like(hue, dtype=np.float32)
    for lo, hi, rc, gc, bc in [
        (0.0, 1.0, chroma, x, 0.0),
        (1.0, 2.0, x, chroma, 0.0),
        (2.0, 3.0, 0.0, chroma, x),
        (3.0, 4.0, 0.0, x, chroma),
        (4.0, 5.0, x, 0.0, chroma),
        (5.0, 6.0, chroma, 0.0, x),
    ]:
        mask = (h_prime >= lo) & (h_prime < hi)
        r1[mask] = rc[mask] if isinstance(rc, np.ndarray) else rc
        g1[mask] = gc[mask] if isinstance(gc, np.ndarray) else gc
        b1[mask] = bc[mask] if isinstance(bc, np.ndarray) else bc
    rgb1 = np.stack([r1, g1, b1], axis=-1)
    m = lum - np.sum(rgb1 * _HSY_LUMA_WEIGHTS, axis=-1)
    rgb = np.clip(rgb1 + m[..., None], 0.0, 1.0)
    return (np.clip(rgb[..., 0] * 255.0 + 0.5, 0, 255).astype(np.uint8),
            np.clip(rgb[..., 1] * 255.0 + 0.5, 0, 255).astype(np.uint8),
            np.clip(rgb[..., 2] * 255.0 + 0.5, 0, 255).astype(np.uint8))


def _rgb_to_hs_space(hs_type, r, g, b):
    """Convert RGB bytes to the selected HS-family space."""
    hs_space = _normalize_hs_type(hs_type)
    if hs_space == "HSL":
        return _rgb2hsl(r, g, b)
    if hs_space == "HSI":
        return _rgb2hsi(r, g, b)
    if hs_space == "HSY":
        return _rgb2hsy(r, g, b)
    return _rgb2hsv(r, g, b)


def _hs_space_to_rgb(hs_type, h, s, third):
    """Convert the selected HS-family space to RGB bytes."""
    hs_space = _normalize_hs_type(hs_type)
    if hs_space == "HSL":
        return _hsl2rgb(h, s, third)
    if hs_space == "HSI":
        return _hsi2rgb(h, s, third)
    if hs_space == "HSY":
        return _hsy2rgb(h, s, third)
    return _hsv2rgb(h, s, third)


SAT_COLORMAP_SIZE = 416  # effective image area size (px)
SAT_MARGIN = 48          # border margin for axes/labels
_DATA_RANGE_MAX = 128    # max data value, range is [-128, 127] or [-128, 128]
_DATA_SIZE = 256         # total data range size (max - min + 1 for ticks)
RGB_COLORMAP_MODE_CIRCLE = 'circle'
RGB_COLORMAP_MODE_HEX = 'hex'


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


def _normalize_rgb_colormap_mode(mode):
    """Normalize RGB colormap mode names to the internal circle/hex tokens."""
    return RGB_COLORMAP_MODE_HEX if str(mode).lower() == RGB_COLORMAP_MODE_HEX else RGB_COLORMAP_MODE_CIRCLE


def _rgb_colormap_boundary_radius(hue_deg, map_mode=RGB_COLORMAP_MODE_CIRCLE):
    """Return the normalized boundary radius for a hue direction in the RGB map plane."""
    hue = np.asarray(hue_deg, dtype=np.float32)
    mode = _normalize_rgb_colormap_mode(map_mode)
    if mode == RGB_COLORMAP_MODE_CIRCLE:
        return np.ones_like(hue, dtype=np.float32)
    sector = np.mod(hue, 60.0)
    angle = np.radians(sector - 30.0)
    cos_term = np.maximum(np.cos(angle), 1e-6)
    return np.float32(np.cos(np.radians(30.0))) / cos_term


def _rgb_hsv_to_colormap_coords(hue_deg, sat_val, map_mode=RGB_COLORMAP_MODE_CIRCLE):
    """Map HSV hue/saturation to normalized RGB colormap plane coordinates."""
    hue = np.asarray(hue_deg, dtype=np.float32)
    sat = np.asarray(sat_val, dtype=np.float32)
    radius = sat * _rgb_colormap_boundary_radius(hue, map_mode)
    rad = np.radians(hue)
    return radius * np.cos(rad), radius * np.sin(rad)


def _rgb_colormap_coords_to_hsv(norm_x, norm_y, map_mode=RGB_COLORMAP_MODE_CIRCLE):
    """Map normalized RGB colormap plane coordinates back to HSV hue/saturation."""
    x = np.asarray(norm_x, dtype=np.float32)
    y = np.asarray(norm_y, dtype=np.float32)
    hue = (np.arctan2(y, x) * 180.0 / np.pi + 360.0) % 360.0
    radius = np.sqrt(x ** 2 + y ** 2)
    boundary = _rgb_colormap_boundary_radius(hue, map_mode)
    sat = np.where(boundary > 1e-6, radius / boundary, 0.0)
    return hue, np.maximum(sat, 0.0)


def _rgb_colormap_labels(map_mode):
    """Return title suffix and axis labels for the current RGB colormap geometry."""
    mode = _normalize_rgb_colormap_mode(map_mode)
    if mode == RGB_COLORMAP_MODE_HEX:
        return 'Hex Boundary', 'Hex X', 'Hex Y'
    return 'Circle', 'S*cos(H)', 'S*sin(H)'


def _get_hs_space_title(hs_type):
    """Return the colormap title prefix for the selected HS-family space."""
    hs_space = _normalize_hs_type(hs_type)
    return f"{hs_space}->RGB"


def _build_colormap_yuv(luma_val, mark_clip_pixel=False):
    """Build YCbCr->RGB colormap for a fixed luma value. Returns PIL Image."""
    w, h_img = SAT_COLORMAP_SIZE, SAT_COLORMAP_SIZE
    # Map pixel coords to data range [-128, 127]
    cb_grid = _pix_to_data(np.tile(np.arange(w, dtype=np.float32), (h_img, 1)))
    cr_grid = _pix_to_data(np.tile(np.arange(h_img - 1, -1, -1, dtype=np.float32).reshape(-1, 1), (1, w)))
    y = np.full((h_img, w), float(luma_val), dtype=np.float32)
    if mark_clip_pixel:
        # Use the unclipped matrix output so we can detect out-of-gamut pixels.
        r_raw, g_raw, b_raw = _ycbcr2rgb(y, cb_grid, cr_grid, clip=False)
        # Out-of-gamut: any channel < 0 or > 255 (matching _ycbcr2rgb's clip range).
        clip_mask = (r_raw < 0) | (r_raw > 255) | (g_raw < 0) | (g_raw > 255) | (b_raw < 0) | (b_raw > 255)
        # "Inner edge" of the clip region: clip pixels that have at least one
        # 4-connected non-clip neighbor.  Pad with True (treated as "in gamut")
        # so edge-of-image clip pixels whose in-image neighbors are all clip are
        # NOT marked as boundary.  Out-of-image pixels are not real neighbors.
        padded = np.pad(clip_mask, 1, mode='constant', constant_values=True)
        n_up    = padded[:-2, 1:-1]
        n_down  = padded[2:,   1:-1]
        n_left  = padded[1:-1, :-2]
        n_right = padded[1:-1, 2:]
        all_nbrs_clip = n_up & n_down & n_left & n_right
        boundary = clip_mask & ~all_nbrs_clip
        # Mark boundary pixels gray; non-boundary pixels (including those inside
        # the clip region) keep their natural rounded-and-clipped color so the
        # underlying tone is still visible inside the out-of-gamut area.
        gray = 128.0
        r_disp = np.where(boundary, gray, np.clip(r_raw + 0.5, 0, 255))
        g_disp = np.where(boundary, gray, np.clip(g_raw + 0.5, 0, 255))
        b_disp = np.where(boundary, gray, np.clip(b_raw + 0.5, 0, 255))
        return Image.fromarray(np.stack([r_disp, g_disp, b_disp], axis=-1).astype(np.uint8), 'RGB')
    r, g, b = _ycbcr2rgb(y, cb_grid, cr_grid)
    return Image.fromarray(np.stack([r, g, b], axis=-1), 'RGB')


def _build_colormap_rgb(value_val, map_mode=RGB_COLORMAP_MODE_CIRCLE, hs_type="HSV"):
    """Build an HS-family->RGB colormap for a fixed third component using circle or hex geometry."""
    w, h_img = SAT_COLORMAP_SIZE, SAT_COLORMAP_SIZE
    # Map pixel coords to [-128, 127] range, then to normalized [-1, 1]
    pix_x = np.tile(np.arange(w, dtype=np.float32), (h_img, 1))
    pix_y = np.tile(np.arange(h_img - 1, -1, -1, dtype=np.float32).reshape(-1, 1), (1, w))
    cx = _pix_to_data(pix_x) / _DATA_RANGE_MAX
    cy = _pix_to_data(pix_y) / _DATA_RANGE_MAX
    h, s = _rgb_colormap_coords_to_hsv(cx, cy, map_mode)
    third = np.full((h_img, w), float(value_val) / 255.0, dtype=np.float32)
    r, g, b = _hs_space_to_rgb(hs_type, h, s, third)
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
    tick_data_vals = [-128, -96, -64, -32, 0, 32, 64, 96, 128]  # match data range [-128, 127]
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


def _is_pysimplegui_63():
    """Return True when the running PySimpleGUI is version 6.3.x.

    Version 6.3 has a bug where the SystemDefault theme uses the magic sentinel
    COLOR_SYSTEM_DEFAULT('1234567890') directly as a color name, which crashes
    with TclError: unknown color name "1234567890" on the first Input.update().
    """
    try:
        parts = [int(p) for p in str(sg.version).split('.')]
    except (ValueError, AttributeError):
        return False
    return len(parts) >= 2 and parts[0] == 6 and parts[1] == 3


def open_csc_ui(args=None):
    """Open PySimpleGUI UI for interactive CSC conversion"""
    # PySimpleGUI 6.3 的 SystemDefault 主题有 bug: 把魔法哨兵
    # COLOR_SYSTEM_DEFAULT('1234567890') 直接用作颜色名, 在 Input.update 时会触发
    # TclError: unknown color name "1234567890" 崩溃。因此仅在 6.3 版本改用
    # LightGrey1 (白底/浅灰输入框/黑字, 观感接近 SystemDefault), 其他版本保持默认。
    if _is_pysimplegui_63():
        sg.theme('LightGrey1')
    else:
        sg.theme('SystemDefault')

    fmt_options = FMT_OPTIONS_8BIT + FMT_OPTIONS_10BIT
    fmt_display = [f"0x{f:x} - {FORMAT_NAMES.get(f, 'Unknown')}" for f in fmt_options]
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
        ALGO_EVIDEO_CSC_PLAN_C,
    ]
    bcsh_tab_layout = [
        [sg.Text('Algo Type:', size=(8, 1)),
         sg.Combo(algo_type_options, default_value=ALGO_RK_HW_CSC, key='-BCSH-ALGO-TYPE-',
                  readonly=True, size=(20, 1), enable_events=True),
         sg.Text('Precision (0=float):', size=(14, 1)),
         sg.Combo([str(v) for v in precision_values], default_value='10',
                  key='-PRECISION-', readonly=True, size=(6, 1), enable_events=True),
         sg.Text('Channel Swap (VOP):', size=(16, 1)),
         sg.Combo(CHANNEL_SWAP_TYPES, default_value='None', key='-CHANNEL-SWAP-',
                  readonly=True, size=(12, 1), enable_events=True),
         sg.Button('Reset BCSH', key='-RESET-BCSH-', pad=(0, 0), border_width=0)],
        *bcsh_layout,
    ]

    preview_resize_threshold = 24

    sathue_tab_layout = [
        [sg.Text('Input Colorspace:', size=(14, 1)),
         sg.Combo(SAT_COLORSPACE_OPTIONS, default_value='YCbCr', key='-SAT-CLRSPC-',
                  readonly=True, size=(14, 1), enable_events=True),
         sg.Text('HSV Type:', size=(9, 1)),
         sg.Combo(SAT_HS_TYPES, default_value='HSV', key='-SAT-HS-TYPE-',
                  readonly=True, size=(6, 1), enable_events=True),
         sg.Text('RGB Map:', size=(8, 1)),
         sg.Combo(['Circle', 'Hex'], default_value='Circle', key='-SAT-RGB-MAP-',
                  readonly=True, size=(8, 1), enable_events=True),
         sg.Text('Input Depth:', size=(8, 1)),
         sg.Text('8bit', key='-SAT-DEPTH-', size=(5, 1))],
        [sg.Checkbox('Show Color Map', key='-SAT-SHOW-MAP-', default=False, enable_events=True),
         sg.Checkbox('Set Luma/Value', key='-SAT-LUMA-', default=True, enable_events=True),
         sg.Slider(range=(0, 255), default_value=204, orientation='h',
                   size=(14, 15), key='-SAT-LUMA-SLIDER-', enable_events=True, disable_number_display=True),
         sg.Spin([str(i) for i in range(256)], initial_value='204', key='-SAT-LUMA-SPIN-', size=(5, 1)),
         sg.Checkbox('or Set Color', key='-SAT-SET-COLOR-', default=False, enable_events=True),
         sg.Input('', key='-SAT-COLOR-INPUT-', size=(22, 1), enable_events=False,
                  disabled=True, disabled_readonly_background_color=sg.theme_background_color())],
        [sg.Checkbox('Adjust Target Color Range', key='-SAT-TARGET-ENABLE-', default=False, enable_events=True)],
        [sg.Column([
            [sg.Frame('H/S/V Adjust Parameters', [
                [sg.Text('Delta Luma:', size=(14, 1)),
                 sg.Slider(range=(-255, 255), default_value=0, resolution=1, orientation='h',
                           size=(20, 15), key='-SAT-DELTA-LUMA-', enable_events=True, disable_number_display=True),
                 sg.Spin([str(i) for i in range(-255, 256)], initial_value='0', key='-SAT-DELTA-LUMA-SPIN-', size=(5, 1)),
                 sg.Button('Reset', key='-SAT-DELTA-LUMA-RESET-', size=(5, 1), pad=(0, 0), border_width=0)],
                [sg.Text('Delta Hue:', size=(14, 1)),
                 sg.Slider(range=(-180, 180), default_value=0, resolution=1, orientation='h',
                           size=(20, 15), key='-SAT-HUE-', enable_events=True, disable_number_display=True),
                 sg.Spin([str(i) for i in range(-180, 181)], initial_value='0', key='-SAT-HUE-SPIN-', size=(5, 1)),
                 sg.Button('Reset', key='-SAT-HUE-RESET-', size=(5, 1), pad=(0, 0), border_width=0)],
                [sg.Text('Gain Sat:', size=(14, 1)),
                 sg.Slider(range=(0, 360), default_value=180, resolution=1, orientation='h',
                           size=(20, 15), key='-SAT-SAT-', enable_events=True, disable_number_display=True),
                 sg.Spin([f"{i/180:.2f}" for i in range(361)], initial_value='1.00', key='-SAT-SAT-SPIN-', size=(5, 1)),
                 sg.Button('Reset', key='-SAT-SAT-RESET-', size=(5, 1), pad=(0, 0), border_width=0)],
            ], expand_x=True)],
        ], vertical_alignment='top'),
         sg.Column([
             [sg.Frame('Target Color Range Settings', [
                 [sg.Checkbox('Fix Target Hue', key='-SAT-FIX-HUE-ENABLE-', default=False, enable_events=True),
                  sg.Slider(range=(0, 360), default_value=0, resolution=1, orientation='h',
                            size=(13, 15), key='-SAT-FIX-HUE-', enable_events=True, disable_number_display=True),
                  sg.Spin([str(i) for i in range(361)], initial_value='0', key='-SAT-FIX-HUE-SPIN-', size=(5, 1))],
                 [sg.Text('Start Hue:', size=(8, 1)),
                  sg.Spin([str(i) for i in range(361)], initial_value='0', key='-SAT-TARGET-HS-SPIN-', size=(5, 1)),
                  sg.Text('Start Tail:', size=(10, 1)),
                  sg.Spin([str(i) for i in range(61)], initial_value='0', key='-SAT-TARGET-HST-SPIN-', size=(5, 1)),
                  sg.Text('Start Padding:', size=(12, 1)),
                  sg.Spin([str(i) for i in range(61)], initial_value='0', key='-SAT-TARGET-HSP-SPIN-', size=(5, 1))],
                 [sg.Text('End Hue:', size=(8, 1)),
                  sg.Spin([str(i) for i in range(361)], initial_value='360', key='-SAT-TARGET-HE-SPIN-', size=(5, 1)),
                  sg.Text('End Tail:', size=(10, 1)),
                  sg.Spin([str(i) for i in range(61)], initial_value='0', key='-SAT-TARGET-HET-SPIN-', size=(5, 1)),
                  sg.Text('End Padding:', size=(12, 1)),
                  sg.Spin([str(i) for i in range(61)], initial_value='0', key='-SAT-TARGET-HEP-SPIN-', size=(5, 1))],
             ], expand_x=True)],
         ], vertical_alignment='top', pad=(10, 0))],
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
        [sg.Text('Auto Pixel Depth:', size=(14, 1)),
         sg.Text('8', key='-DISP-DEPTH-', size=(4, 1), font=('_', 10, 'bold'))],
        [sg.Text('Display Scale:', size=(14, 1)),
         sg.Slider(range=(0.01, 2.0), default_value=0.4, resolution=0.05, orientation='h',
                   size=(20, 15), key='-DISP-SCALE-', enable_events=True, disable_number_display=True),
         sg.Spin([f"{i/20:.2f}" for i in range(2, 41)], initial_value='0.40', key='-DISP-SCALE-SPIN-', size=(5, 1))]
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
             [sg.Button('Save Output', key='-SAVE-OUT-', size=(12, 2), pad=(0, 0), border_width=0)],
             [sg.Radio('Show Input', 'RADIO1', key='-SHOW-IN-', enable_events=True, size=(12, 1))],
             [sg.Radio('Show Output', 'RADIO1', default=True, key='-SHOW-OUT-', enable_events=True, size=(12, 1))],
             [sg.Checkbox('dump', key='-DUMP-', default=False, enable_events=True, size=(12, 1))]
         ], element_justification='l', vertical_alignment='top', pad=(10, 30))],
        [sg.HorizontalSeparator()],
        [sg.Frame('Preview Info', [
            [
                sg.Text('Display Size:', size=(10, 1)),
                sg.Input('', key='-DISPLAY-SIZE-', size=(60, 1), readonly=True, border_width=0,
                         disabled_readonly_background_color=sg.theme_background_color(), disabled_readonly_text_color=sg.theme_text_color()),
                sg.Text('Position:', size=(10, 1)),
                sg.Input('', key='-POSITION-INFO-', size=(60, 1), readonly=True, border_width=0,
                         disabled_readonly_background_color=sg.theme_background_color(), disabled_readonly_text_color=sg.theme_text_color()),
            ],
            [
                sg.Text('Input Pixel:', size=(10, 1)),
                sg.Input('', key='-INPUT-PIXEL-INFO-', size=(60, 1), readonly=True, border_width=0,
                         disabled_readonly_background_color=sg.theme_background_color(), disabled_readonly_text_color=sg.theme_text_color()),
                sg.Text('Output Pixel:', size=(10, 1)),
                sg.Input('', key='-OUTPUT-PIXEL-INFO-', size=(60, 1), readonly=True, border_width=0,
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

    window = sg.Window('CSC Test Tool v1.2', layout, resizable=True, finalize=True, return_keyboard_events=True)
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
    current_display_scale = 0.4   # Display Scale: preview size = input_size * this
    display_scale_src = None      # input identity for which Display Scale was auto-initialized

    # Sat/Hue Test state
    sathue_colorspace = 'YUV'  # legacy single-mode colorspace; mirrored to *_colorspace in single mode
    sathue_mode = 'single'  # 'single' = right colormap only; 'dual' = left+right colormaps (YUV=>RGB / RGB=>YUV)
    sathue_left_colorspace = 'YUV'
    sathue_right_colorspace = 'YUV'
    sathue_hs_type = 'HSV'
    sathue_rgb_map_mode = RGB_COLORMAP_MODE_CIRCLE
    sathue_luma_val = 204
    sathue_hue_val = 0
    sathue_sat_val = 1.0
    # Target-color-range selective adjustment (Sat/Hue tab).
    sathue_delta_luma_val = 0      # Delta Luma [-255, 255], added to V (normalized /255)
    sathue_target_enabled = False  # Adjust Target Color Range checkbox
    sathue_target_hs = 0           # Start Hue [0, 360]
    sathue_target_he = 360         # End Hue [0, 360]
    sathue_target_hst = 0          # Start Tail [0, 60]
    sathue_target_het = 0          # End Tail [0, 60]
    sathue_target_hsp = 0          # Start Padding [0, 60]
    sathue_target_hep = 0          # End Padding [0, 60]
    sathue_gray_thrd = 0.01        # Fixed gray threshold: pixels with S below this are treated as gray and untouched
    sathue_fix_hue_enabled = False # Fix Target Hue checkbox
    sathue_fix_hue_val = 0         # TargHue [0, 360]
    sathue_img_eff = None       # effective colormap PIL Image (without axes); single-mode only
    sathue_img_full = None      # full image with axes, margin; single-mode only
    sathue_left_img_eff = None
    sathue_left_img_full = None
    sathue_right_img_eff = None
    sathue_right_img_full = None
    sathue_margin = SAT_MARGIN
    sathue_locked = False
    sathue_locked_pix = None    # (img_x, img_y) in effective coords (single-mode)
    sathue_locked_input = None  # (c1, c2, c3) input values at lock point (single-mode)
    sathue_left_locked = False
    sathue_left_locked_pix = None
    sathue_left_locked_input = None
    sathue_right_locked_pix = None
    sathue_right_locked_input = None
    # Mirrors the -SHOW-IN-/OUT- radio state; in dual + frozen + YUV=>RGB mode it
    # also drives which YUV pixel (input vs. hue/sat-transformed output) feeds
    # the right RGB colormap's V value and the right-side marker style.
    sathue_show_output = True
    sathue_mouse_pos = None
    sathue_left_display_scale = 1.0
    sathue_right_display_scale = 1.0
    sathue_display_scale = 1.0  # scale ratio applied to full_img for display (single-mode)
    sathue_render_after_id = None  # tkinter after id for deferred render
    is_mouse_in_sathue = False
    is_mouse_in_sathue_left = False
    sathue_set_color_enabled = False
    sathue_left_mouse_pos = None
    sathue_left_render_after_id = None
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

    def _get_rgb_display_meta():
        """Return the active HS-family title and third-component label."""
        return _get_hs_space_title(sathue_hs_type), _get_hs_space_label(sathue_hs_type)

    def _convert_rgb_input_between_hs_types(input_vals, from_hs_type, to_hs_type):
        """Convert a stored RGB-side HS tuple between two HS-family spaces."""
        if input_vals is None:
            return None
        r_val, g_val, b_val = _hs_space_to_rgb(from_hs_type, input_vals[0], input_vals[1], input_vals[2])
        r_arr = np.asarray(r_val, dtype=np.uint8).reshape(-1)
        g_arr = np.asarray(g_val, dtype=np.uint8).reshape(-1)
        b_arr = np.asarray(b_val, dtype=np.uint8).reshape(-1)
        h_new, s_new, t_new = _rgb_to_hs_space(to_hs_type, r_arr, g_arr, b_arr)
        return float(h_new[0]), float(s_new[0]), float(t_new[0])

    def _remap_rgb_inputs_for_hs_type_change(old_hs_type, new_hs_type):
        """Keep frozen RGB-side markers on the same color when the HS-family changes."""
        nonlocal sathue_locked_input, sathue_left_locked_input, sathue_right_locked_input
        if old_hs_type == new_hs_type:
            return
        if sathue_mode == 'single':
            if sathue_colorspace == 'RGB' and sathue_locked_input is not None:
                sathue_locked_input = _convert_rgb_input_between_hs_types(sathue_locked_input, old_hs_type, new_hs_type)
        else:
            if sathue_left_colorspace == 'RGB' and sathue_left_locked_input is not None:
                sathue_left_locked_input = _convert_rgb_input_between_hs_types(sathue_left_locked_input, old_hs_type, new_hs_type)
            if sathue_right_colorspace == 'RGB' and sathue_right_locked_input is not None:
                sathue_right_locked_input = _convert_rgb_input_between_hs_types(sathue_right_locked_input, old_hs_type, new_hs_type)
            if sathue_locked and sathue_left_locked_input is not None:
                sathue_locked_input = sathue_left_locked_input

    def update_sathue_map(preserve_display_size=False):
        """Regenerate the Sat/Hue colormap image(s) and update the widget(s).
        Single mode: only -SAT-IMAGE- is updated. Dual mode: -LEFT-PREVIEW- and -SAT-IMAGE-
        are both updated with their respective colormaps."""
        nonlocal sathue_img_eff, sathue_img_full, sathue_margin
        nonlocal sathue_display_scale
        nonlocal sathue_left_img_eff, sathue_left_img_full
        nonlocal sathue_right_img_eff, sathue_right_img_full
        rgb_title_suffix, rgb_xlabel, rgb_ylabel = _rgb_colormap_labels(sathue_rgb_map_mode)
        hs_title, hs_third_label = _get_rgb_display_meta()

        if sathue_mode == 'single':
            if sathue_colorspace == 'YUV':
                img_eff = _build_colormap_yuv(sathue_luma_val, mark_clip_pixel=True)
                title = f"YCbCr->RGB  (Y={sathue_luma_val})"
                xlabel, ylabel = "Cb", "Cr"
            else:
                img_eff = _build_colormap_rgb(sathue_luma_val, sathue_rgb_map_mode, sathue_hs_type)
                title = f"{hs_title} [{rgb_title_suffix}]  ({hs_third_label}={sathue_luma_val})"
                xlabel, ylabel = rgb_xlabel, rgb_ylabel
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
        else:
            # Dual mode: regenerate left and right colormaps independently.
            # Luma sources:
            #   - No frozen pixel: both sides use sathue_luma_val (the -SAT-LUMA- control).
            #   - Left frozen: left side uses the frozen pixel's own Luma/Value; right side
            #     uses the Luma/Value derived from the left frozen pixel converted to the
            #     right colorspace. The -SAT-LUMA- control no longer drives the right side.
            # In dual + frozen mode, when the right cs differs from the left
            # cs (i.e. YUV=>RGB or RGB=>YUV), the right luma is sourced from
            # either the left *output* pixel (Show Output) or the left
            # *input* pixel (Show Input), per sathue_show_output.
            dual_use_output = ((sathue_left_colorspace == 'YUV'
                                and sathue_right_colorspace == 'RGB')
                               or (sathue_left_colorspace == 'RGB'
                                   and sathue_right_colorspace == 'YUV')) \
                              and sathue_show_output
            left_luma, right_luma = _resolve_dual_luma(use_output=dual_use_output)

            # Left colormap.
            if sathue_left_colorspace == 'YUV':
                left_eff = _build_colormap_yuv(left_luma, mark_clip_pixel=True)
                left_title = f"YCbCr->RGB  (Y={left_luma})"
                left_xl, left_yl = "Cb", "Cr"
            else:
                left_eff = _build_colormap_rgb(left_luma, sathue_rgb_map_mode, sathue_hs_type)
                left_title = f"{hs_title} [{rgb_title_suffix}]  ({hs_third_label}={left_luma})"
                left_xl, left_yl = rgb_xlabel, rgb_ylabel
            sathue_left_img_eff = left_eff.copy()
            left_verbose = left_eff.copy()
            left_draw = ImageDraw.Draw(left_verbose)
            if sathue_left_locked and sathue_left_locked_pix is not None:
                _draw_locked_markers(left_draw, sathue_left_locked_pix,
                                     sathue_left_locked_input, cs=sathue_left_colorspace)
                _update_dual_lock_display()
            sathue_left_img_full, _ = _build_colormap_with_axis(left_verbose, left_title, left_xl, left_yl)

            # Right colormap.
            if sathue_right_colorspace == 'YUV':
                right_eff = _build_colormap_yuv(right_luma, mark_clip_pixel=True)
                right_title = f"YCbCr->RGB  (Y={right_luma})"
                right_xl, right_yl = "Cb", "Cr"
            else:
                right_eff = _build_colormap_rgb(right_luma, sathue_rgb_map_mode, sathue_hs_type)
                right_title = f"{hs_title} [{rgb_title_suffix}]  ({hs_third_label}={right_luma})"
                right_xl, right_yl = rgb_xlabel, rgb_ylabel
            sathue_right_img_eff = right_eff.copy()
            right_verbose = right_eff.copy()
            right_draw = ImageDraw.Draw(right_verbose)
            if sathue_right_locked_pix is not None and sathue_right_locked_input is not None:
                if sathue_left_colorspace != sathue_right_colorspace:
                    # In dual + frozen + cross-cs mode (YUV=>RGB or RGB=>YUV)
                    # the two markers on the right colormap mirror the two
                    # frozen pixel *values* shown in the Input/Output Pixel
                    # text fields:
                    #   - black marker  = the left input pixel projected to
                    #                    the right colormap (the "Input
                    #                    Pixel" numeric value).
                    #   - white marker  = the left output pixel projected
                    #                    to the right colormap (the
                    #                    "Output Pixel" numeric value).
                    # The -SHOW-OUT- radio only changes the colormap's
                    # Luma/Value and flips the solid/dash style of the two
                    # markers so the user can tell which one is the live
                    # reference:
                    #   Show Output : black (input) = dashed, white (output) = solid
                    #   Show Input  : black (input) = solid,  white (output) = dashed
                    # The marker positions themselves never change with the
                    # Show IO radio because they always point to the same
                    # left input / left output pixel, regardless of the
                    # Luma/Value used to render the colormap background.
                    in_pix = sathue_right_locked_pix
                    right_out_data = _compute_dual_right_data_pos()
                    if right_out_data is not None:
                        ox, oy = right_out_data
                        out_pix = (_data_to_pix(ox),
                                   SAT_COLORMAP_SIZE - 1 - _data_to_pix(oy))
                    else:
                        out_pix = None
                    solid_input = not sathue_show_output
                    solid_output = sathue_show_output
                    if solid_input:
                        r = 5
                        for _ in range(2):
                            right_draw.ellipse(
                                [in_pix[0] - r, in_pix[1] - r,
                                 in_pix[0] + r, in_pix[1] + r],
                                outline=(0, 0, 0))
                            r -= 1
                    else:
                        _draw_dashed_circle(right_draw, in_pix[0], in_pix[1], 5,
                                            outline=(0, 0, 0))
                    if out_pix is not None:
                        if solid_output:
                            r = 5
                            for _ in range(2):
                                right_draw.ellipse(
                                    [out_pix[0] - r, out_pix[1] - r,
                                     out_pix[0] + r, out_pix[1] + r],
                                    outline=(255, 255, 255))
                                r -= 1
                        else:
                            _draw_dashed_circle(right_draw, out_pix[0], out_pix[1], 5,
                                                outline=(255, 255, 255))
                else:
                    _draw_locked_markers(right_draw, sathue_right_locked_pix,
                                         sathue_right_locked_input, cs=sathue_right_colorspace)
            sathue_right_img_full, sathue_margin = _build_colormap_with_axis(
                right_verbose, right_title, right_xl, right_yl)

            # Push to -IMAGE- and -SAT-IMAGE-.
            _render_dual_main_previews(preserve=preserve_display_size)

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

    def _set_sathue_color_lock(pixel_vals, cs=None):
        """Apply a typed color to Sat/Hue Test and lock both input/output markers.
        Pass cs explicitly in dual mode (typically sathue_left_colorspace);
        otherwise falls back to sathue_colorspace."""
        if cs is None:
            cs = sathue_colorspace
        nonlocal sathue_locked, sathue_locked_pix, sathue_locked_input, sathue_luma_val
        if cs == 'YUV':
            y_val = int(np.clip(pixel_vals[0], 0, 255))
            u_val = int(np.clip(pixel_vals[1], 0, 255))
            v_val = int(np.clip(pixel_vals[2], 0, 255))
            cb = u_val - 128
            cr = v_val - 128
            sathue_luma_val = y_val
            window['-SAT-LUMA-SLIDER-'].update(value=y_val)
            window['-SAT-LUMA-SPIN-'].update(value=str(y_val))
            lock_x = _data_to_pix(cb)
            lock_y = SAT_COLORMAP_SIZE - 1 - _data_to_pix(cr)
            sathue_locked_input = (y_val, cb, cr)
        else:
            r_val = int(np.clip(pixel_vals[0], 0, 255))
            g_val = int(np.clip(pixel_vals[1], 0, 255))
            b_val = int(np.clip(pixel_vals[2], 0, 255))
            hue_arr, sat_arr, third_arr = _rgb_to_hs_space(sathue_hs_type, np.array([r_val]), np.array([g_val]), np.array([b_val]))
            hue = float(hue_arr[0])
            sat = float(sat_arr[0])
            third = float(third_arr[0])
            third_byte = int(np.clip(round(third * 255.0), 0, 255))
            sathue_luma_val = third_byte
            window['-SAT-LUMA-SLIDER-'].update(value=third_byte)
            window['-SAT-LUMA-SPIN-'].update(value=str(third_byte))
            sathue_locked_input = (hue, sat, third)
            lock_x, lock_y = _input_to_lock_pix(sathue_locked_input, cs='RGB')

        lock_x = int(np.clip(lock_x, 0, SAT_COLORMAP_SIZE - 1))
        lock_y = int(np.clip(lock_y, 0, SAT_COLORMAP_SIZE - 1))
        sathue_locked = True
        sathue_locked_pix = (lock_x, lock_y)
        update_sathue_map(preserve_display_size=False)

    def _set_sathue_dual_color_lock(pixel_vals):
        """Lock a typed color in dual mode: left colormap gets the parsed pixel, right colormap
        receives the converted (other colorspace) equivalent at the same screen coords."""
        nonlocal sathue_left_locked, sathue_left_locked_pix, sathue_left_locked_input
        nonlocal sathue_right_locked_pix, sathue_right_locked_input
        nonlocal sathue_luma_val
        # Lock on the left side using the left colorspace.
        _set_sathue_color_lock(list(pixel_vals), cs=sathue_left_colorspace)
        sathue_left_locked = True
        sathue_left_locked_pix = sathue_locked_pix
        sathue_left_locked_input = sathue_locked_input
        # Compute the equivalent in the right colorspace.
        if sathue_left_colorspace == 'YUV' and sathue_right_colorspace == 'RGB':
            right_input = _yuv_to_rgb_input(sathue_left_locked_input)
        elif sathue_left_colorspace == 'RGB' and sathue_right_colorspace == 'YUV':
            right_input = _rgb_to_yuv_input(sathue_left_locked_input)
        else:
            right_input = sathue_left_locked_input
        right_x, right_y = _input_to_lock_pix(right_input, cs=sathue_right_colorspace)
        sathue_right_locked_pix = (right_x, right_y)
        sathue_right_locked_input = right_input
        update_sathue_map(preserve_display_size=False)

    def _clear_sathue_dual_color_lock():
        """Clear all locks in dual mode."""
        nonlocal sathue_left_locked, sathue_left_locked_pix, sathue_left_locked_input
        nonlocal sathue_right_locked_pix, sathue_right_locked_input
        nonlocal sathue_locked, sathue_locked_pix, sathue_locked_input
        sathue_left_locked = False
        sathue_left_locked_pix = None
        sathue_left_locked_input = None
        sathue_right_locked_pix = None
        sathue_right_locked_input = None
        sathue_locked = False
        sathue_locked_pix = None
        sathue_locked_input = None
        update_sathue_map(preserve_display_size=True)

    def _input_to_lock_pix(input_vals, cs):
        """Convert an (input) tuple to (pix_x, pix_y) for the given colorspace."""
        if cs == 'YUV':
            _, cb, cr = input_vals
            return _data_to_pix(cb), SAT_COLORMAP_SIZE - 1 - _data_to_pix(cr)
        else:
            hue, sat, val = input_vals
            norm_x, norm_y = _rgb_hsv_to_colormap_coords(hue, sat, sathue_rgb_map_mode)
            x = _data_to_pix(norm_x * _DATA_RANGE_MAX)
            y = SAT_COLORMAP_SIZE - 1 - _data_to_pix(norm_y * _DATA_RANGE_MAX)
            return x, y

    def _refresh_rgb_lock_pixels():
        """Refresh lock marker coordinates after the RGB colormap geometry changes."""
        nonlocal sathue_locked_pix, sathue_left_locked_pix, sathue_right_locked_pix
        if sathue_locked and sathue_locked_input is not None and sathue_mode == 'single' and sathue_colorspace == 'RGB':
            sathue_locked_pix = _input_to_lock_pix(sathue_locked_input, cs='RGB')
        if sathue_left_locked and sathue_left_locked_input is not None and sathue_left_colorspace == 'RGB':
            sathue_left_locked_pix = _input_to_lock_pix(sathue_left_locked_input, cs='RGB')
            if sathue_locked:
                sathue_locked_pix = sathue_left_locked_pix
        if sathue_right_locked_input is not None and sathue_right_colorspace == 'RGB':
            sathue_right_locked_pix = _input_to_lock_pix(sathue_right_locked_input, cs='RGB')

    def _yuv_to_rgb_input(yuv_input):
        """Convert YUV input tuple (Y, Cb, Cr) to the active RGB-side HS tuple."""
        _, cb, cr = yuv_input
        y_byte = int(np.clip(round(float(yuv_input[0])), 0, 255))
        # _ycbcr2rgb is the BT.709 data-domain matrix; pass Cb/Cr directly without +128.
        r, g, b = _ycbcr2rgb(np.array([y_byte]), np.array([cb]), np.array([cr]))
        h_arr, s_arr, third_arr = _rgb_to_hs_space(sathue_hs_type, np.array([r[0]]), np.array([g[0]]), np.array([b[0]]))
        return (float(h_arr[0]), float(s_arr[0]), float(third_arr[0]))

    def _rgb_to_yuv_input(rgb_input):
        """Convert the active RGB-side HS tuple to YUV input tuple (Y, Cb, Cr)."""
        h, s, third = rgb_input
        r_arr, g_arr, b_arr = _hs_space_to_rgb(sathue_hs_type, np.array([h]), np.array([s]), np.array([third]))
        y_arr, cb_arr, cr_arr = _rgb2ycbcr(np.array([r_arr[0]]), np.array([g_arr[0]]), np.array([b_arr[0]]))
        return (float(y_arr[0]), float(cb_arr[0]) - 128.0, float(cr_arr[0]) - 128.0)

    def _get_luma_from_input(input_vals, cs):
        """Extract the Luma/Value byte (0..255) from a sat/hue input tuple in the given cs."""
        if cs == 'YUV':
            y = float(input_vals[0])
        else:
            y = float(input_vals[2]) * 255.0
        return int(np.clip(round(y), 0, 255))

    def _resolve_dual_luma(use_output=False):
        """Return (left_luma, right_luma) for dual mode.
        When left side has a frozen pixel, left luma comes from the frozen pixel itself
        and right luma comes from the left frozen pixel converted to the right cs.
        Otherwise both sides share sathue_luma_val.

        use_output (meaningful in dual + frozen mode whenever the right cs
        differs from the left cs): when True, the right luma is derived from
        the left *output* pixel (one application of hue/sat) instead of from
        the left input pixel.  This mirrors the -SHOW-OUT- radio state and
        applies symmetrically to both YUV=>RGB and RGB=>YUV directions:
          YUV=>RGB:  right_luma = V(_yuv_to_rgb_input(apply_hue_sat_yuv(left_in)))
          RGB=>YUV:  right_luma = Y(_rgb_to_yuv_input(apply_hue_sat_hsv(left_in)))"""
        if sathue_left_locked and sathue_left_locked_input is not None:
            left_luma = _get_luma_from_input(sathue_left_locked_input, sathue_left_colorspace)
            if sathue_left_colorspace == sathue_right_colorspace:
                right_luma = left_luma
            elif sathue_left_colorspace == 'YUV' and sathue_right_colorspace == 'RGB':
                if use_output:
                    out_yuv = _apply_hue_sat_yuv(sathue_left_locked_input)
                    converted = _yuv_to_rgb_input(out_yuv)
                else:
                    converted = _yuv_to_rgb_input(sathue_left_locked_input)
                right_luma = _get_luma_from_input(converted, 'RGB')
            else:
                # RGB=>YUV
                if use_output:
                    h2, s2, third2 = _apply_hue_sat_hs(sathue_left_locked_input)
                    converted = _rgb_to_yuv_input((h2, s2, third2))
                else:
                    converted = _rgb_to_yuv_input(sathue_left_locked_input)
                right_luma = _get_luma_from_input(converted, 'YUV')
            return left_luma, right_luma
        return sathue_luma_val, sathue_luma_val

    def _clear_sathue_color_lock():
        """Disable the forced Sat/Hue color lock and restore hover mode."""
        nonlocal sathue_locked, sathue_locked_pix, sathue_locked_input
        sathue_locked = False
        sathue_locked_pix = None
        sathue_locked_input = None
        update_sathue_map(preserve_display_size=True)

    def _update_dual_frozen_left_luma(new_luma):
        """Update the left frozen pixel's luma component (Y for YUV, V for RGB/HSV)
        to new_luma (0..255 byte) in dual + frozen mode, and refresh the mirrored
        right-side locked pixel accordingly.  No-op outside dual + frozen mode."""
        nonlocal sathue_left_locked, sathue_left_locked_pix, sathue_left_locked_input
        nonlocal sathue_right_locked_pix, sathue_right_locked_input
        nonlocal sathue_locked, sathue_locked_pix, sathue_locked_input
        if sathue_mode != 'dual' or not sathue_left_locked or sathue_left_locked_input is None:
            return
        if sathue_left_colorspace == 'YUV':
            _, cb, cr = sathue_left_locked_input
            sathue_left_locked_input = (float(new_luma), cb, cr)
        else:
            h, s, _v = sathue_left_locked_input
            sathue_left_locked_input = (h, s, new_luma / 255.0)
        # Keep the single-mode globals in sync with the left side.
        sathue_locked = True
        sathue_locked_pix = sathue_left_locked_pix
        sathue_locked_input = sathue_left_locked_input
        # Recompute the mirrored right-side locked input and pixel coords.
        if sathue_left_colorspace == 'YUV' and sathue_right_colorspace == 'RGB':
            right_input = _yuv_to_rgb_input(sathue_left_locked_input)
        elif sathue_left_colorspace == 'RGB' and sathue_right_colorspace == 'YUV':
            right_input = _rgb_to_yuv_input(sathue_left_locked_input)
        else:
            right_input = sathue_left_locked_input
        sathue_right_locked_input = right_input
        rx, ry = _input_to_lock_pix(right_input, cs=sathue_right_colorspace)
        rx = int(np.clip(rx, 0, SAT_COLORMAP_SIZE - 1))
        ry = int(np.clip(ry, 0, SAT_COLORMAP_SIZE - 1))
        sathue_right_locked_pix = (rx, ry)

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

    def _refresh_sathue_display():
        """Unified entry point that routes to the right renderer based on sathue_mode.
        Single mode -> -SAT-IMAGE- only. Dual mode -> -LEFT-PREVIEW- + -SAT-IMAGE-."""
        if sathue_mode == 'dual':
            _render_dual_main_previews(preserve=False)
        else:
            _render_sathue_display()

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

    def _draw_dashed_circle(draw, cx, cy, r, outline, segments=16, dash_ratio=0.5, width=1):
        """Draw a dashed circle on the given ImageDraw context.
        PIL's ImageDraw.ellipse has no dash support, so approximate it by drawing
        `segments` short arc segments evenly spaced around the circle and only
        stroking the first `dash_ratio` of each segment."""
        import math
        if r <= 0 or segments <= 0:
            return
        angle_step = 2.0 * math.pi / segments
        on_segments = max(int(round(segments * dash_ratio)), 1)
        for i in range(0, segments, 2):
            start_angle = (i + 0) * angle_step - math.pi / 2.0
            for k in range(on_segments):
                a1 = (i + k) * angle_step - math.pi / 2.0
                a2 = (i + k + 1) * angle_step - math.pi / 2.0
                x1 = cx + r * math.cos(a1)
                y1 = cy + r * math.sin(a1)
                x2 = cx + r * math.cos(a2)
                y2 = cy + r * math.sin(a2)
                draw.line([x1, y1, x2, y2], fill=outline, width=width)

    def _draw_locked_markers(draw, locked_pix, locked_input, cs,
                             solid_input=True, solid_output=True):
        """Draw the input (black) and output (white) marker rings on the given draw context.

        solid_input/solid_output:
          True  -> solid double-ring (current default look).
          False -> single dashed ring, so the user can visually distinguish
                  "this is the live input/output" from "this is the cross-mode
                  reference point"."""
        if locked_pix is None or locked_input is None:
            return
        lx, ly = locked_pix
        if solid_input:
            r = 5
            for _ in range(2):
                draw.ellipse([lx - r, ly - r, lx + r, ly + r], outline=(0, 0, 0))
                r -= 1
        else:
            _draw_dashed_circle(draw, lx, ly, 5, outline=(0, 0, 0))
        out_pos = _compute_sathue_output_pos_for(cs, locked_input)
        if out_pos is not None:
            tx, ty = out_pos
            if solid_output:
                r = 5
                for _ in range(2):
                    draw.ellipse([tx - r, ty - r, tx + r, ty + r], outline=(255, 255, 255))
                    r -= 1
            else:
                _draw_dashed_circle(draw, tx, ty, 5, outline=(255, 255, 255))

    def _compute_sathue_output_pos_for(cs, locked_input):
        """Compute the output pixel coordinate for a given (cs, locked_input) tuple.
        Mirrors _compute_sathue_output_pos but decoupled from global sathue_locked_input."""
        if locked_input is None:
            return None
        c1, c2, c3 = locked_input
        hue_deg = sathue_hue_val
        sat_scale = sathue_sat_val
        if cs == 'YUV':
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
            norm_x, norm_y = _rgb_hsv_to_colormap_coords(h2, s2, sathue_rgb_map_mode)
            sx = _data_to_pix(norm_x * _DATA_RANGE_MAX)
            sy = _data_to_pix(-norm_y * _DATA_RANGE_MAX)
            tx, ty = sx, sy
            tx, ty = sx, sy
        if 0 <= tx < SAT_COLORMAP_SIZE and 0 <= ty < SAT_COLORMAP_SIZE:
            return tx, ty
        return None

    def _render_dual_main_previews(preserve=False):
        """Render the dual colormaps into -LEFT-PREVIEW- and -SAT-IMAGE- with matched sizing."""
        nonlocal sathue_left_display_scale, sathue_right_display_scale
        if sathue_left_img_full is None or sathue_right_img_full is None:
            return
        if not preserve:
            preferred_side = current_main_display_size[1] if current_main_display_size[1] > 0 else 400
            max_side = max(preferred_side, 1)
            liw, lih = sathue_left_img_full.size
            riw, rih = sathue_right_img_full.size
            left_ratio = min(2.0, max_side / liw, max_side / lih)
            right_ratio = min(2.0, max_side / riw, max_side / rih)
            # Keep both sides at the same display scale to keep them aligned.
            scale_ratio = min(left_ratio, right_ratio)
            sathue_left_display_scale = scale_ratio
            sathue_right_display_scale = scale_ratio
            left_disp = sathue_left_img_full.resize(
                (int(round(liw * scale_ratio)), int(round(lih * scale_ratio))),
                Image.LANCZOS if hasattr(Image, 'LANCZOS') else Image.Resampling.LANCZOS)
            bio = io.BytesIO()
            left_disp.save(bio, format='PNG')
            window['-IMAGE-'].update(data=bio.getvalue(),
                                     size=(int(round(liw * scale_ratio)),
                                           int(round(lih * scale_ratio))))
        else:
            # Preserve previous scale but refresh content.
            liw, lih = sathue_left_img_full.size
            left_disp = sathue_left_img_full.resize(
                (max(int(round(liw * sathue_left_display_scale)), 1),
                 max(int(round(lih * sathue_left_display_scale)), 1)),
                Image.LANCZOS if hasattr(Image, 'LANCZOS') else Image.Resampling.LANCZOS)
            bio = io.BytesIO()
            left_disp.save(bio, format='PNG')
            window['-IMAGE-'].update(data=bio.getvalue())

        # Right side respects the -SAT-IMAGE-COL- visibility toggle.
        if sat_preview_visible:
            riw, rih = sathue_right_img_full.size
            right_disp = sathue_right_img_full.resize(
                (max(int(round(riw * sathue_right_display_scale)), 1),
                 max(int(round(rih * sathue_right_display_scale)), 1)),
                Image.LANCZOS if hasattr(Image, 'LANCZOS') else Image.Resampling.LANCZOS)
            bio = io.BytesIO()
            right_disp.save(bio, format='PNG')
            if not preserve:
                window['-SAT-IMAGE-'].update(data=bio.getvalue(),
                                             size=(max(int(round(riw * sathue_right_display_scale)), 1),
                                                   max(int(round(rih * sathue_right_display_scale)), 1)))
            else:
                window['-SAT-IMAGE-'].update(data=bio.getvalue())

    def _update_dual_lock_display():
        """Update INPUT/OUTPUT/POSITION text for dual mode (right colormap is the
        source-of-truth lock for the Output line; left colormap is the source-of-truth
        for the Input line and the Display Size "start" coordinate)."""
        if not sathue_left_locked or sathue_left_locked_pix is None or sathue_left_locked_input is None:
            return
        lx, ly = sathue_left_locked_pix
        out_pos = _compute_sathue_output_pos(cs=sathue_left_colorspace, invals=sathue_left_locked_input)
        window['-INPUT-PIXEL-INFO-'].update(
            _format_dual_input_str(sathue_left_colorspace, sathue_left_locked_input, out_pos, True))
        window['-OUTPUT-PIXEL-INFO-'].update(
            _format_dual_output_str(sathue_left_colorspace, sathue_left_locked_input, out_pos, True))
        # Position: dual mode shows the right colormap trajectory.
        # "(xs, ys) -> (xe, ye) [Frozen]"  where (xs, ys) is the frozen pixel on
        # the right colormap and (xe, ye) is the hue/sat-transformed output pixel
        # projected onto the right colormap (the right colormap may be in a different
        # colorspace than the left one).
        xl = _pix_to_data_int(lx)
        yl = _pix_to_data_int(SAT_COLORMAP_SIZE - 1 - ly)
        right_start = _compute_dual_right_frozen_data_pos()
        # The "right end" pixel position is the right-side *output* pixel
        # projected onto the right colormap.  It is always the left *output*
        # YUV pixel (one application of hue/sat) projected to the right
        # colormap, regardless of the -SHOW-IN-/OUT- radio.  This mirrors the
        # "Output Pixel" text in the UI, which is also the left output YUV
        # pixel.  The Show IO radio only changes the colormap's V value and
        # the marker style (solid/dash), not the marker position.
        right_end = _compute_dual_right_data_pos()
        if right_start is None or right_end is None:
            pos_text = "( n/a,  n/a) -> ( n/a,  n/a) [Frozen]"
        else:
            xs, ys = right_start
            xe, ye = right_end
            pos_text = f"({int(round(xs)):4d},{int(round(ys)):4d}) -> ({int(round(xe)):4d},{int(round(ye)):4d}) [Frozen]"
        window['-POSITION-INFO-'].update(pos_text)
        # Display Size in dual + frozen: show the left colormap trajectory
        # "(xs, ys) -> (xe, ye) [Frozen]" where (xs, ys) is the left colormap frozen
        # pixel and (xe, ye) is the left colormap pixel after one application of
        # hue/sat.  When not frozen, fall back to the default W x H display.
        left_end = _compute_dual_left_end_data_pos()
        if left_end is None:
            disp_size_text = f"({xl:4d},{yl:4d}) -> ( n/a,  n/a) [Frozen]"
        else:
            xe2, ye2 = left_end
            disp_size_text = f"({xl:4d},{yl:4d}) -> ({int(round(xe2)):4d},{int(round(ye2)):4d}) [Frozen]"
        window['-DISPLAY-SIZE-'].update(value=disp_size_text)

    def _compute_dual_right_data_pos():
        """Return (x_data, y_data) of the right-side *output* pixel projected onto
        the right colormap (in data coords, the same convention as the left side
        uses).  Returns None if the result is outside the valid [-128, 128) data
        range.  This is the position of the white output marker on the right
        colormap; the "Output Pixel" text in the UI is the numeric value of the
        same pixel, so the marker must always mirror that pixel.
        YUV=>RGB:  invals (YUV) -> apply hue/sat once (left output YUV) -> RGB
                   bytes -> HSV -> (h, s, v) -> HSV colormap (x, y).
        RGB=>YUV:  invals (HSV) -> apply hue/sat once -> RGB -> YUV -> YUV
                   colormap (Cb, Cr)."""
        invals = sathue_left_locked_input
        if invals is None:
            return None
        if sathue_left_colorspace == 'YUV' and sathue_right_colorspace == 'RGB':
            out_yuv = _apply_hue_sat_yuv(invals)
            r, g, b = _yuv_tuple_to_rgb_bytes(out_yuv)
            h_arr, s_arr, _third_arr = _rgb_to_hs_space(sathue_hs_type, np.array([r]), np.array([g]), np.array([b]))
            h, s = float(h_arr[0]), float(s_arr[0])
            norm_x, norm_y = _rgb_hsv_to_colormap_coords(h, s, sathue_rgb_map_mode)
            cx = norm_x * _DATA_RANGE_MAX
            cy = norm_y * _DATA_RANGE_MAX
        elif sathue_left_colorspace == 'RGB' and sathue_right_colorspace == 'YUV':
            h2, s2, third2 = _apply_hue_sat_hs(invals)
            out_yuv_data = _rgb_to_yuv_input((h2, s2, third2))
            cx = float(out_yuv_data[1])
            cy = float(out_yuv_data[2])
        else:
            return None
        if -128.0 <= cx < 128.0 and -128.0 <= cy < 128.0:
            return cx, cy
        return None

    def _compute_dual_right_frozen_data_pos():
        """Return (x_data, y_data) of the right-colormap frozen pixel (the source
        of the dual-mode Output line) projected onto the right colormap.

        YUV=>RGB: sathue_right_locked_input is (H, S, V) -> HSV colormap (x, y).
        RGB=>YUV: sathue_right_locked_input is (Y, Cb_signed, Cr_signed) -> YUV colormap (Cb, Cr)."""
        right_invals = sathue_right_locked_input
        if right_invals is None:
            return None
        if sathue_left_colorspace == 'YUV' and sathue_right_colorspace == 'RGB':
            h, s, _third = right_invals
            norm_x, norm_y = _rgb_hsv_to_colormap_coords(h, s, sathue_rgb_map_mode)
            cx = norm_x * _DATA_RANGE_MAX
            cy = norm_y * _DATA_RANGE_MAX
        elif sathue_left_colorspace == 'RGB' and sathue_right_colorspace == 'YUV':
            cx = float(right_invals[1])
            cy = float(right_invals[2])
        else:
            return None
        if -128.0 <= cx < 128.0 and -128.0 <= cy < 128.0:
            return cx, cy
        return None

    def _compute_dual_left_end_data_pos():
        """Return (x_data, y_data) of the left-colormap frozen pixel after one
        application of hue/sat, still on the left colormap.  Used for the
        "Display Size" trajectory "(xs, ys) -> (xe, ye) [Frozen]" in dual mode.

        YUV=>RGB (left=YUV): invals (Y, Cb, Cr) -> apply YUV hue/sat -> (Cb, Cr).
        RGB=>YUV (left=HSV): invals (H, S, V) -> apply HSV hue/sat -> HSV colormap (x, y)."""
        invals = sathue_left_locked_input
        if invals is None:
            return None
        if sathue_left_colorspace == 'YUV':
            y, cb2, cr2 = _apply_hue_sat_yuv(invals)
            cx, cy = float(cb2), float(cr2)
        elif sathue_left_colorspace == 'RGB':
            h2, s2, _third2 = _apply_hue_sat_hs(invals)
            norm_x, norm_y = _rgb_hsv_to_colormap_coords(h2, s2, sathue_rgb_map_mode)
            cx = norm_x * _DATA_RANGE_MAX
            cy = norm_y * _DATA_RANGE_MAX
        else:
            return None
        if -128.0 <= cx < 128.0 and -128.0 <= cy < 128.0:
            return cx, cy
        return None

    def _compute_sathue_output_pos(cs=None, invals=None):
        """Compute the output pixel coordinate after Hue/Saturation transform.
        When invals is provided it is used directly (hover case); otherwise the
        currently locked input (sathue_locked_input) is used.
        Returns (pix_x, pix_y) in effective coords, or None if out of range.
        Pass cs explicitly in dual mode; otherwise falls back to sathue_colorspace."""
        if cs is None:
            cs = sathue_colorspace
        if invals is None:
            if sathue_locked_input is None:
                return None
            invals = sathue_locked_input
        c1, c2, c3 = invals
        hue_deg = sathue_hue_val
        sat_scale = sathue_sat_val
        if cs == 'YUV':
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

    def _get_sathue_input_at(pix_x, pix_y, cs=None):
        """Get the (c1, c2, c3) input values at pixel in effective coords.
        Pass cs explicitly in dual mode; otherwise falls back to sathue_colorspace.
        In dual mode the Luma/Value used here matches the Luma/Value the colormap was
        rendered with (i.e. resolved via _resolve_dual_luma for that side)."""
        if cs is None:
            cs = sathue_colorspace
        # In dual mode pick the effective Luma/Value that this side's colormap was
        # rendered with, so the resulting (Y, Cb, Cr) / (H, S, V) tuple is consistent
        # with the pixels the user is hovering on.
        if sathue_mode == 'dual':
            left_luma, right_luma = _resolve_dual_luma()
            if cs == sathue_left_colorspace:
                eff_luma = left_luma
            elif cs == sathue_right_colorspace:
                eff_luma = right_luma
            else:
                eff_luma = sathue_luma_val
        else:
            eff_luma = sathue_luma_val
        if cs == 'YUV':
            Cb = _pix_to_data_int(pix_x)
            Cr = _pix_to_data_int(SAT_COLORMAP_SIZE - 1 - pix_y)
            return (eff_luma, Cb, Cr)
        else:
            cx = _pix_to_data(pix_x) / _DATA_RANGE_MAX
            cy = _pix_to_data(SAT_COLORMAP_SIZE - 1 - pix_y) / _DATA_RANGE_MAX
            H, S = _rgb_colormap_coords_to_hsv(cx, cy, sathue_rgb_map_mode)
            return (H, max(S, 0.0), eff_luma / 255.0)

    def _format_sathue_input_str(invals, cs=None):
        """Format input pixel info string per the display template.
        Pass cs explicitly in dual mode; otherwise falls back to sathue_colorspace."""
        if cs is None:
            cs = sathue_colorspace
        if cs == 'YUV':
            y_val, cb, cr = int(round(invals[0])), int(round(invals[1])), int(round(invals[2]))
            return f"YCbCr({y_val:3d}, {cb:3d}, {cr:3d}) <=> YUV({y_val:3d}, {cb+128:3d}, {cr+128:3d})"
        else:
            h_val, s_val, third_val = invals
            r, g, b = _hs_space_to_rgb(sathue_hs_type, np.array([h_val]), np.array([s_val]), np.array([third_val]))
            return f"{sathue_hs_type}({h_val:3.1f}, {s_val:3.2f}, {third_val:3.2f}) <=> RGB({r[0]:3d}, {g[0]:3d}, {b[0]:3d})"

    def _format_sathue_output_str(outvals, cs=None):
        """Format output pixel info string per the display template.
        Pass cs explicitly in dual mode; otherwise falls back to sathue_colorspace."""
        if cs is None:
            cs = sathue_colorspace
        if cs == 'YUV':
            y_val, cb, cr = int(round(outvals[0])), int(round(outvals[1])), int(round(outvals[2]))
            return f"YCbCr({y_val:3d}, {cb:3d}, {cr:3d}) <=> YUV({y_val:3d}, {cb+128:3d}, {cr+128:3d})"
        else:
            r, g, b = outvals
            h_val, s_val, third_val = _rgb_to_hs_space(sathue_hs_type, np.array([r]), np.array([g]), np.array([b]))
            return f"{sathue_hs_type}({h_val[0]:3.1f}, {s_val[0]:3.2f}, {third_val[0]:3.2f}) <=> RGB({r:3d}, {g:3d}, {b:3d})"

    def _yuv_tuple_to_rgb_bytes(yuv_input):
        """Return (R, G, B) 0-255 ints for a YUV data-domain tuple
        (Y, Cb_signed, Cr_signed) in [-128, 127].  The internal _ycbcr2rgb matrix
        is built for that data domain, so the Cb/Cr must NOT be shifted by +128 here."""
        y = float(yuv_input[0])
        cb = float(yuv_input[1])
        cr = float(yuv_input[2])
        r, g, b = _ycbcr2rgb(np.array([y]), np.array([cb]), np.array([cr]))
        return int(np.clip(r[0], 0, 255)), int(np.clip(g[0], 0, 255)), int(np.clip(b[0], 0, 255))

    def _hs_tuple_to_rgb_bytes(hs_input):
        """Return (R, G, B) 0-255 ints for the active HS-family tuple."""
        h, s, third = hs_input
        r_arr, g_arr, b_arr = _hs_space_to_rgb(sathue_hs_type, np.array([h]), np.array([s]), np.array([third]))
        return int(r_arr[0]), int(g_arr[0]), int(b_arr[0])

    def _yuv_data_to_pixel_yuv(yuv_input):
        """Return (Y, Cb_pix, Cr_pix) ints in pixel domain [0,255] for a YUV data tuple
        (Y, Cb_signed, Cr_signed) in [-128, 127].  Y is unchanged; Cb/Cr get +128 offset."""
        y_byte = int(np.clip(round(float(yuv_input[0])), 0, 255))
        cb_byte = int(np.clip(round(float(yuv_input[1])) + 128.0, 0, 255))
        cr_byte = int(np.clip(round(float(yuv_input[2])) + 128.0, 0, 255))
        return y_byte, cb_byte, cr_byte

    def _apply_hue_sat_yuv(yuv_input):
        """Apply the current sathue hue/sat transform to a YUV data-domain tuple
        (Y, Cb_signed, Cr_signed).  Returns (Y, cb2, cr2) still in the data domain."""
        y = float(yuv_input[0])
        cb = float(yuv_input[1])
        cr = float(yuv_input[2])
        h_rad = np.radians(sathue_hue_val)
        sat_scale = sathue_sat_val
        cb2 = np.clip(sat_scale * (cb * np.cos(h_rad) - cr * np.sin(h_rad)), -128.0, 127.0)
        cr2 = np.clip(sat_scale * (cb * np.sin(h_rad) + cr * np.cos(h_rad)), -128.0, 127.0)
        return y, cb2, cr2

    def _apply_hue_sat_hs(hs_input):
        """Apply the current sathue hue/sat transform to an HS-family tuple."""
        h, s, third = hs_input
        h2 = (float(h) + sathue_hue_val) % 360.0
        s2 = float(np.clip(s * sathue_sat_val, 0.0, 1.0))
        third2 = float(third)
        return h2, s2, third2

    def _apply_target_color_range(planar_rgb, pixel_depth, delta_hue, delta_sat, delta_luma, hs, he, gray_thrd=0.0, fix_hue_enabled=False, targ_hue=0.0, hst=0.0, het=0.0, hsp=0.0, hep=0.0):
        """Selectively adjust colors whose hue lies inside the target range [hs, he].

        When hs > he the range wraps around: [hs, 360] U [0, he].  Only pixels
        inside the range are modified, in HSV space:
          H' = (H + delta_hue) % 360            (default)
          S' = clip(S * delta_sat, 0, 1)
          V' = clip(V + delta_luma / 255, 0, 1)
        Pixels with saturation below gray_thrd are treated as gray (black/gray/
        white) and are left untouched regardless of hue.

        Each range edge fades over a larger interval made of a Tail (outside the
        nominal range) plus a Padding (inside the range):
          start edge: [hs - hst, hs + hsp]   (Tail below hs, Padding above hs)
          end edge:   [he - hep, he + het]   (Padding below he, Tail above he)
        (mod 360).  The transition mode depends on how many segments are set:
          - both Tail and Padding > 0: two-segment ramp meeting at the edge with
            alpha = 0.5, so each segment has its own ramp rate:
              start: Tail [hs - hst, hs] 0 -> 0.5, Padding [hs, hs + hsp] 0.5 -> 1
              end:   Padding [he - hep, he] 1 -> 0.5, Tail [he, he + het] 0.5 -> 0
          - only one of them > 0: single-segment linear ramp over that zone
            (0 -> 1 at start, 1 -> 0 at end)
          - neither: no transition (hard edge).
        The fully-adjusted result is alpha-blended with the input pixel inside
        the zone; the middle of the range keeps the full result.  The zones are
        extended by the hue tolerance (eps) so alpha reaches 0 exactly at the
        in-range boundary, keeping the transition continuous even with 8-bit hue
        quantization.

        When fix_hue_enabled, Delta Hue is treated as a percentage (clamped to
        [-100, 100]): all in-range pixels rotate toward +targ_hue (positive
        direction) or -targ_hue (negative direction), with the rotation progress
        equal to |delta_hue|%; at 100% every in-range pixel's H equals the target.
        planar_rgb: (3, H, W) full-range RGB planar in the input pixel depth.
        Returns a new planar of the same shape/dtype; out-of-range and low-
        saturation pixels are left unchanged."""
        h, w = planar_rgb.shape[1], planar_rgb.shape[2]
        max_val = (1 << pixel_depth) - 1
        rgb_norm = planar_rgb.reshape(3, -1).T.astype(np.float32) / max_val
        hsv = rgb_to_hsv(rgb_norm)                      # H in [0, 1] (fraction of 360)
        h_deg = hsv[:, 0] * 360.0

        # Small tolerance (deg) to absorb hue quantization at the range edges:
        # in 8-bit the color nearest to hue=330 computes to 329.9 (and 30 to
        # 30.1), so an exact >= hs / <= he test would wrongly exclude them.
        eps = 0.5
        hst = float(hst)
        hsp = float(hsp)
        het = float(het)
        hep = float(hep)
        # The in-range set extends past the nominal [hs, he] by the Tail amounts
        # (hst below hs / het above he) plus the hue tolerance, so the Tail fade
        # actually blends those out-of-range pixels and alpha reaches 0 exactly
        # at the in_range boundary.
        if hs <= he:
            in_range = (h_deg >= hs - hst - eps) & (h_deg <= he + het + eps)
        else:
            in_range = (h_deg >= hs - hst - eps) | (h_deg <= he + het + eps)

        # Soft transition alpha.  Each edge fades over its Tail/Padding zone,
        # with the transition mode depending on how many segments are present:
        #   - both Tail and Padding (> 0): two-segment ramp meeting at the edge
        #     with alpha = 0.5 (each segment has its own rate):
        #       start: Tail [hs-hst-eps, hs] 0 -> 0.5, Padding [hs, hs+hsp] 0.5 -> 1
        #       end:   Padding [he-hep, he] 1 -> 0.5, Tail [he, he+het+eps] 0.5 -> 0
        #   - only one of them (> 0): single-segment linear ramp over that zone:
        #       start Tail-only [hs-hst-eps, hs] 0 -> 1, Padding-only [hs-eps, hs+hsp] 0 -> 1
        #       end   Tail-only [he, he+het+eps] 1 -> 0, Padding-only [he-hep, he+eps] 1 -> 0
        #   - neither: no transition (hard edge).
        # The extra eps on the Tail/edge side keeps the quantization edge part
        # of the fade instead of a hard seam.
        alpha = np.ones_like(h_deg)
        if hst > 0.0 and hsp > 0.0:
            tail_len = hst + eps
            d_tail = (h_deg - (float(hs) - tail_len)) % 360.0
            zs1 = d_tail <= tail_len
            alpha[zs1] = np.minimum(alpha[zs1], np.clip(d_tail[zs1] / tail_len * 0.5, 0.0, 0.5))
            d_pad = (h_deg - float(hs)) % 360.0
            zs2 = d_pad <= hsp
            alpha[zs2] = np.minimum(alpha[zs2], np.clip(0.5 + d_pad[zs2] / hsp * 0.5, 0.5, 1.0))
        elif hst > 0.0:
            # Tail-only: single ramp [hs-hst-eps, hs], alpha 0 -> 1.
            tail_len = hst + eps
            d_tail = (h_deg - (float(hs) - tail_len)) % 360.0
            zs = d_tail <= tail_len
            alpha[zs] = np.minimum(alpha[zs], np.clip(d_tail[zs] / tail_len, 0.0, 1.0))
        elif hsp > 0.0:
            # Padding-only: single ramp [hs-eps, hs+hsp], alpha 0 -> 1.
            start_len = hsp + eps
            d_pad = (h_deg - (float(hs) - eps)) % 360.0
            zs = d_pad <= start_len
            alpha[zs] = np.minimum(alpha[zs], np.clip(d_pad[zs] / start_len, 0.0, 1.0))
        if het > 0.0 and hep > 0.0:
            d_pad_end = (h_deg - (float(he) - hep)) % 360.0
            ze1 = d_pad_end <= hep
            alpha[ze1] = np.minimum(alpha[ze1], np.clip(1.0 - d_pad_end[ze1] / hep * 0.5, 0.5, 1.0))
            # The end Tail spans [he, he+het+eps] so alpha reaches 0 exactly
            # at the in_range edge (he+het+eps) instead of at he.  The band h in
            # (he, he+het+eps] is still considered in-range (8-bit hue
            # quantization can land there), so keeping alpha at 1 there left a
            # residual full-adjustment strip that showed up as red specks
            # breaking the overlay continuity.
            tail_len_end = het + eps
            d_tail_end = (h_deg - float(he)) % 360.0
            ze2 = d_tail_end <= tail_len_end
            alpha[ze2] = np.minimum(alpha[ze2], np.clip(0.5 - d_tail_end[ze2] / tail_len_end * 0.5, 0.0, 0.5))
        elif het > 0.0:
            # End Tail-only: single ramp [he, he+het+eps], alpha 1 -> 0.
            tail_len_end = het + eps
            d_tail_end = (h_deg - float(he)) % 360.0
            ze = d_tail_end <= tail_len_end
            alpha[ze] = np.minimum(alpha[ze], np.clip(1.0 - d_tail_end[ze] / tail_len_end, 0.0, 1.0))
        elif hep > 0.0:
            # End Padding-only: single ramp [he-hep, he+eps], alpha 1 -> 0.
            end_len = hep + eps
            d_pad_end = (h_deg - (float(he) - hep)) % 360.0
            ze = d_pad_end <= end_len
            alpha[ze] = np.minimum(alpha[ze], np.clip(1.0 - d_pad_end[ze] / end_len, 0.0, 1.0))
        # Black/gray/white pixels (saturation below the threshold) must not change.
        if gray_thrd and gray_thrd > 0.0:
            in_range = in_range & (hsv[:, 1] >= gray_thrd)

        # Compute the fully adjusted HSV for every pixel.
        hsv_adj = hsv.copy()
        if fix_hue_enabled:
            # Delta Hue is a percentage in [-100, 100]; the sign picks the
            # rotation direction (+targ_hue / -targ_hue) and the magnitude is
            # the progress toward that target hue.
            progress = np.clip(float(delta_hue), -100.0, 100.0) / 100.0
            target = float(targ_hue) if progress >= 0.0 else float((-targ_hue) % 360.0)
            arc = ((target - h_deg + 180.0) % 360.0) - 180.0   # shortest signed arc
            h_adj = (h_deg + abs(progress) * arc) % 360.0
        else:
            h_adj = (h_deg + delta_hue) % 360.0
        hsv_adj[:, 0] = h_adj / 360.0
        hsv_adj[:, 1] = np.clip(hsv[:, 1] * delta_sat, 0.0, 1.0)
        hsv_adj[:, 2] = np.clip(hsv[:, 2] + delta_luma / 255.0, 0.0, 1.0)

        rgb_out = rgb_norm.copy()
        rgb_adj = hsv_to_rgb(hsv_adj)
        # In-range pixels: alpha-blend the adjusted result with the input.
        # The overlay zones fade (alpha < 1) near the edges; the core keeps
        # alpha = 1, i.e. the full adjustment.
        rgb_out[in_range] = (alpha[in_range, None] * rgb_adj[in_range]
                             + (1.0 - alpha[in_range, None]) * rgb_out[in_range])

        planar_out = np.clip(rgb_out.T * max_val + 0.5, 0, max_val).astype(planar_rgb.dtype)
        return planar_out.reshape(3, h, w)

    def _render_target_color_preview(window, values):
        """Render the target-color-range selective adjustment into -IMAGE-.

        Only called when sathue_target_enabled and current_planar_in is not None.
        - Show Output: input -> RGB -> HSV -> selective adjust -> RGB -> output
          colorspace -> -IMAGE-.  Independent of the CSC pipeline (coefs show None).
        - Show Input:  the raw input image is displayed."""
        nonlocal current_main_display_size
        show_output = values.get('-SHOW-OUT-', False)

        if show_output:
            depth = current_input_pixel_depth
            # 1) Input -> RGB full range.
            if current_input_is_yuv:
                y2r_config = CscCoefConfig()
                y2r_config.pixel_depth = depth
                y2r_config.coef_precision = 0
                y2r_mode = CscMode()
                y2r_mode.is_input_yuv = True
                y2r_mode.is_output_yuv = False
                y2r_mode.is_input_full_range = current_input_full_range
                y2r_mode.is_output_full_range = True
                y2r_mode.input_color_encoding = current_input_color
                y2r_mode.output_color_encoding = ColorSpace.BT709
                y2r_config.csc_mode = y2r_mode
                y2r_coefs, y2r_offset = get_csc_coefs(y2r_config, None)
                rgb_planar = apply_csc(current_planar_in, y2r_coefs, y2r_offset, 0, depth)
            else:
                max_val = (1 << depth) - 1
                rgb_planar = np.clip(current_planar_in, 0, max_val).astype(
                    np.uint16 if depth > 8 else np.uint8)
            # 2) Selective HSV adjustment.
            rgb_planar = _apply_target_color_range(
                rgb_planar, depth,
                sathue_hue_val, sathue_sat_val, sathue_delta_luma_val,
                sathue_target_hs, sathue_target_he,
                sathue_gray_thrd,
                sathue_fix_hue_enabled,
                sathue_fix_hue_val,
                sathue_target_hst,
                sathue_target_het,
                sathue_target_hsp,
                sathue_target_hep,
            )
            # 3) Back to the output colorspace (RGB_Full -> oclr).
            out_clr = get_clrspc_from_display(values['-OUT-CLR-'])
            display_planar = convert_planar(rgb_planar, 1, out_clr, 0, depth)[0]
            target_is_yuv = is_yuv_format(get_fmt_from_display(values['-OUT-FMT-']))
            target_pixel_depth = depth
            _, orange = clrspc_to_mode_params(out_clr)
            target_full_range = (orange == "F")
            ocs, _ = clrspc_to_mode_params(out_clr)
            target_color = ColorSpace[ocs.upper()] if ocs.startswith("bt") else ColorSpace.BT709
        else:
            display_planar = current_planar_in
            target_is_yuv = current_input_is_yuv
            target_pixel_depth = current_input_pixel_depth
            target_full_range = current_input_full_range
            target_color = current_input_color

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
                rgb_planar = apply_csc(display_planar, y2r_coefs, y2r_offset, 0, target_pixel_depth)
            else:
                rgb_planar = display_planar.copy()
                max_val = (1 << target_pixel_depth) - 1
                rgb_planar = np.clip(rgb_planar, 0, max_val)

            h, w = rgb_planar.shape[1], rgb_planar.shape[2]
            if target_pixel_depth > 8:
                rgb_8bit = (rgb_planar >> (target_pixel_depth - 8)).astype(np.uint8)
            else:
                rgb_8bit = rgb_planar.astype(np.uint8)
            rgb_interleaved = np.stack([rgb_8bit[0], rgb_8bit[1], rgb_8bit[2]], axis=-1)
            img = Image.fromarray(rgb_interleaved, 'RGB')
            bio = io.BytesIO()
            img.save(bio, format='PNG')
            # In dual mode, -IMAGE- is owned by the left colormap renderer.
            if sathue_mode != 'dual':
                window['-IMAGE-'].update(data=bio.getvalue(), size=(w, h))
            current_main_display_size = (w, h)
            mode_desc = build_csc_mode_str(
                get_clrspc_from_display(values['-IN-CLR-']),
                get_clrspc_from_display(values['-OUT-CLR-']),
            )
            window['-DISPLAY-SIZE-'].update(value=f"{w}x{h} ({mode_desc})")
            # The adjusted image is not produced by the CSC pipeline.
            update_multiline_readonly(window, '-STEP1-COEFS-', 'None')
            update_multiline_readonly(window, '-STEP1-OFFSET-', 'None')
            update_multiline_readonly(window, '-STEP2-COEFS-', 'None')
            update_multiline_readonly(window, '-STEP2-OFFSET-', 'None')
        except Exception as e:
            window['-DISPLAY-SIZE-'].update(value=f"Display error: {e}")

    def _format_dual_input_str(input_cs, input_vals, out_pos, frozen):
        """Format the dual-mode Input Pixel line.  All printed Y/Cb/Cr values are in
        the pixel domain [0, 255]; all printed R/G/B values are 0-255 bytes.

        With frozen pixel:
          YUV=>RGB : "YUV(yi,ui,vi) / RGB(ri,gi,bi)"        (left-input only)
          RGB=>YUV : "RGB(ri,gi,bi) / YUV(yi,ui,vi)"        (left-input only)

          Without frozen pixel (hover-only):
          YUV=>RGB : "YCbCr(y,cb,cr) => YUV(y,u,v)"
          RGB=>YUV : "HSV(h, s, v) => RGB(r,g,b)"

        Lowercase letters inside parentheses are the per-channel pixel values."""
        if input_cs == 'YUV':
            y_pix, cb_pix, cr_pix = _yuv_data_to_pixel_yuv(input_vals)
            ri, gi, bi = _yuv_tuple_to_rgb_bytes(input_vals)
        else:
            ri, gi, bi = _hs_tuple_to_rgb_bytes(input_vals)
            yuv_data = _rgb_to_yuv_input(input_vals)
            y_pix, cb_pix, cr_pix = _yuv_data_to_pixel_yuv(yuv_data)

        if not frozen:
            if input_cs == 'YUV':
                return f"YCbCr({y_pix:3d},{cb_pix:3d},{cr_pix:3d}) => YUV({y_pix:3d},{input_vals[1] + 128:3d},{input_vals[2] + 128:3d})"
            return f"{sathue_hs_type}({input_vals[0]:3.1f}, {input_vals[1]:3.2f}, {input_vals[2]:3.2f}) => RGB({ri:3d},{gi:3d},{bi:3d})"

        # Frozen branch: show only the *input* pixel (left side) - the
        # corresponding *output* pixel is reported on the "Output Pixel"
        # line.  YUV is the primary on the left in YUV=>RGB, RGB is the
        # primary on the left in RGB=>YUV.
        if input_cs == 'YUV':
            return f"YUV({y_pix:3d},{cb_pix:3d},{cr_pix:3d})/RGB({ri:3d},{gi:3d},{bi:3d})"
        return f"RGB({ri:3d},{gi:3d},{bi:3d})/YUV({y_pix:3d},{cb_pix:3d},{cr_pix:3d})"

    def _format_dual_output_str(input_cs, input_vals, out_pos, frozen):
        """Format the dual-mode Output Pixel line.  All printed Y/Cb/Cr values are
        in the pixel domain [0, 255]; all printed R/G/B values are 0-255 bytes.

        In dual + frozen mode the right-side input/output pixel are no longer
        independent: the right output is the left *output* projected onto the
        right colormap.  The "Output Pixel" line therefore reports the
        transformed value of the same left pixel that the "Input Pixel" line
        reports, but with one application of the hue/sat slider.
          YUV=>RGB : "YUV(yo,uo,vo)/RGB(ro,go,bo)"
          RGB=>YUV : "RGB(ro,go,bo)/YUV(yo,uo,vo)"
        Without frozen pixel: returns an empty string (caller clears the field)."""
        if not frozen:
            return ''
        # Compute the transformed (output) pixel directly from input_vals via
        # the hue/sat formula, NOT from the colormap (which is the un-transformed
        # reference).
        if input_cs == 'YUV':
            out_yuv_data = _apply_hue_sat_yuv(input_vals)
        else:
            h2, s2, third2 = _apply_hue_sat_hs(input_vals)
            out_yuv_data = _rgb_to_yuv_input((h2, s2, third2))
        yo_pix, uo_pix, vo_pix = _yuv_data_to_pixel_yuv(out_yuv_data)
        ro, go, bo = _yuv_tuple_to_rgb_bytes(out_yuv_data)
        if input_cs == 'YUV':
            return f"YUV({yo_pix:3d},{uo_pix:3d},{vo_pix:3d})/RGB({ro:3d},{go:3d},{bo:3d})"
        return f"RGB({ro:3d},{go:3d},{bo:3d})/YUV({yo_pix:3d},{uo_pix:3d},{vo_pix:3d})"

    def _get_sathue_output_at(pix_x, pix_y, cs=None, img_eff=None):
        """Get the output values at pixel in effective coords.
        YUV mode: returns (Y, Cb, Cr). RGB mode: returns (R, G, B) 0-255.
        Returns None if outside valid area.
        Pass cs / img_eff explicitly in dual mode; otherwise fall back to single-mode state."""
        if cs is None:
            cs = sathue_colorspace
        if img_eff is None:
            img_eff = sathue_img_eff
        if not (0 <= pix_x < SAT_COLORMAP_SIZE and 0 <= pix_y < SAT_COLORMAP_SIZE):
            return None
        if img_eff is None:
            return None
        # For HSV mode, outside circle is invalid
        if cs == 'RGB':
            cx = _pix_to_data(pix_x) / _DATA_RANGE_MAX
            cy = _pix_to_data(SAT_COLORMAP_SIZE - 1 - pix_y) / _DATA_RANGE_MAX
            _, sat = _rgb_colormap_coords_to_hsv(cx, cy, sathue_rgb_map_mode)
            if sat > 1.0:
                return None
        px = img_eff.getpixel((pix_x, pix_y))
        r, g, b = px[0], px[1], px[2]
        if cs == 'YUV':
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

    def update_channel_swap_control(window, values, algo_type):
        """Enable channel swap only for RK HW CSC and reset it otherwise."""
        enabled = (algo_type == ALGO_RK_HW_CSC)
        if not enabled:
            window['-CHANNEL-SWAP-'].update(value='None', disabled=True)
            values['-CHANNEL-SWAP-'] = 'None'
        else:
            current_value = values.get('-CHANNEL-SWAP-', 'None')
            if current_value not in CHANNEL_SWAP_TYPES:
                current_value = 'None'
            window['-CHANNEL-SWAP-'].update(value=current_value, disabled=False)
            values['-CHANNEL-SWAP-'] = current_value

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
    for spin_key in ('-SAT-LUMA-SPIN-', '-SAT-HUE-SPIN-', '-SAT-SAT-SPIN-',
                     '-SAT-DELTA-LUMA-SPIN-', '-SAT-TARGET-HS-SPIN-', '-SAT-TARGET-HE-SPIN-',
                     '-SAT-TARGET-HST-SPIN-', '-SAT-TARGET-HET-SPIN-',
                     '-SAT-TARGET-HSP-SPIN-', '-SAT-TARGET-HEP-SPIN-',
                     '-SAT-FIX-HUE-SPIN-'):
        window[spin_key].bind('<Return>', '+ENTER')
        window[spin_key].bind('<KP_Enter>', '+ENTER')
        window[spin_key].Widget.configure(command=emit_bcsh_ui_event(f'{spin_key}+STEP'))

    # Sat/Hue slider left/right key bindings
    for slider_key in ('-SAT-LUMA-SLIDER-', '-SAT-HUE-', '-SAT-SAT-',
                       '-SAT-DELTA-LUMA-',
                       '-SAT-FIX-HUE-'):
        sw = window[slider_key].Widget
        sw.configure(takefocus=1)
        sw.bind('<Button-1>', lambda event, widget=sw: widget.focus_set(), add='+')
        sw.bind('<Left>', emit_bcsh_ui_event(f'{slider_key}+LEFT', stop_default=True))
        sw.bind('<Right>', emit_bcsh_ui_event(f'{slider_key}+RIGHT', stop_default=True))

    # Display Scale (I/O Config) spin/slider key bindings
    window['-DISP-SCALE-SPIN-'].bind('<Return>', '+ENTER')
    window['-DISP-SCALE-SPIN-'].bind('<KP_Enter>', '+ENTER')
    window['-DISP-SCALE-SPIN-'].Widget.configure(command=emit_bcsh_ui_event('-DISP-SCALE-SPIN-+STEP'))
    ds_widget = window['-DISP-SCALE-'].Widget
    ds_widget.configure(takefocus=1)
    ds_widget.bind('<Button-1>', lambda event, widget=ds_widget: widget.focus_set(), add='+')
    ds_widget.bind('<Left>', emit_bcsh_ui_event('-DISP-SCALE-+LEFT', stop_default=True))
    ds_widget.bind('<Right>', emit_bcsh_ui_event('-DISP-SCALE-+RIGHT', stop_default=True))

    def update_multiline_readonly(window, key, value):
        widget = window[key].Widget
        widget.configure(state='normal')
        window[key].update(value=value)

    def _init_display_scale_for(window, values, w):
        """Auto-set the Display Scale so the preview is ~400px wide (clamped to [0.1, 2.0])."""
        nonlocal current_display_scale
        init_scale = max(0.1, min(2.0, 400.0 / w))
        init_scale = round(init_scale / 0.05) * 0.05
        current_display_scale = init_scale
        window['-DISP-SCALE-'].update(value=init_scale)
        window['-DISP-SCALE-SPIN-'].update(value=f"{init_scale:.2f}")
        values['-DISP-SCALE-'] = init_scale

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
        nonlocal current_display_scale, display_scale_src

        def get_preview_sampling_size(src_w, src_h, min_display_w, min_display_h):
            """Return the preview sampling size for the current Display Scale."""
            if preserve_preview_size and current_planar_in is not None:
                prev_h, prev_w = current_planar_in.shape[1], current_planar_in.shape[2]
                if prev_w > 0 and prev_h > 0:
                    return min(prev_w, src_w), min(prev_h, src_h)

            disp_w = max(int(round(src_w * current_display_scale)), 1)
            disp_h = max(int(round(src_h * current_display_scale)), 1)
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

            # Auto-init the Display Scale for a new input size (preview ~400px wide).
            color_src = ('color', w, h)
            if display_scale_src != color_src:
                _init_display_scale_for(window, values, w)
                display_scale_src = color_src

            # Build flat planar from color values
            max_val = (1 << depth) - 1
            planar_in_full = np.zeros((3, h, w), dtype=np.uint16 if depth > 8 else np.uint8)
            for i in range(3):
                planar_in_full[i, :, :] = int(np.clip(color_vals[i], 0, max_val))
            current_input_file_params = None

            # Downsample to the Display Scale size
            disp_w, disp_h = get_preview_sampling_size(w, h, 400, 400)
            scale_factor = disp_w / float(w)
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
                display_result(window, values, preserve_preview_size)
            return

        input_file = values['-INPUT-FILE-']
        if not input_file or not os.path.isfile(input_file):
            return

        is_image = is_image_file(input_file)

        try:
            if is_image:
                # 图片文件（PNG/JPEG/BMP）：直接解码为 RGB planar，分辨率取图像实际尺寸
                decoded_planar, img_w, img_h = read_image_to_planar(input_file)
                planar_in_full = decoded_planar
                w, h = int(img_w), int(img_h)
                ifmt = 0x0  # RGB888：解码后的像素为 RGB
                iclr = 1    # RGB_Full：PIL 解码为全范围 RGB
                current_input_file_params = (input_file, w, h, ifmt)

                # 自动更新界面上的分辨率
                window['-WIDTH-'].update(value=str(w))
                values['-WIDTH-'] = str(w)
                window['-HEIGHT-'].update(value=str(h))
                values['-HEIGHT-'] = str(h)
                # 输入格式/色彩空间固定为 RGB888 + RGB_Full
                rgb_fmt = next((f for f in fmt_display if f.startswith('0x0 ')), None)
                if rgb_fmt:
                    window['-IN-FMT-'].update(value=rgb_fmt)
                    values['-IN-FMT-'] = rgb_fmt
                window['-IN-CLR-'].update(value=clrspc_rgb[1])
                values['-IN-CLR-'] = clrspc_rgb[1]
            else:
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
        except (ValueError, IndexError, OSError):
            return

        if h <= 0 or w <= 0:
            return

        if not is_image:
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
            # Auto-init the Display Scale when a new input image is loaded.
            if display_scale_src != file_params:
                _init_display_scale_for(window, values, w)
                display_scale_src = file_params
            if planar_in_full is None or current_input_file_params != file_params:
                if is_image:
                    # 缓存失效时重新解码图片
                    planar_in_full, _, _ = read_image_to_planar(input_file)
                else:
                    planar_in_full, _ = read_raw_to_planar(input_file, w, h, ifmt)
                current_input_file_params = file_params

            # Downsample to the Display Scale size
            disp_w, disp_h = get_preview_sampling_size(w, h, 640, 360)
            scale_factor = disp_w / float(w)
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
                display_result(window, values, preserve_preview_size)
                if current_mouse_pos is not None:
                    update_pixel_info(window, current_mouse_pos[0], current_mouse_pos[1])
        except Exception as e:
            current_main_display_size = (400, 400)
            window['-DISPLAY-SIZE-'].update(value=f"Error: {e}")
            window['-POSITION-INFO-'].update(value='')
            window['-INPUT-PIXEL-INFO-'].update(value='')
            window['-OUTPUT-PIXEL-INFO-'].update(value='')
            window['-IMAGE-'].update(data=b'', size=current_main_display_size)

    def display_result(window, values, preserve_preview_size=False):
        nonlocal current_planar_in, current_planar_out
        nonlocal current_step1_coefs, current_step1_offset
        nonlocal current_step2_coefs, current_step2_offset
        nonlocal current_scale_factor
        nonlocal current_main_display_size

        # When the target-color-range adjustment is active the main image is
        # produced by the independent selective-adjustment path (input -> RGB ->
        # HSV -> adjust -> output colorspace), NOT by the CSC pipeline.
        if sathue_target_enabled and current_planar_in is not None:
            _render_target_color_preview(window, values)
            return

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
            # In dual mode, -IMAGE- is owned by the left colormap renderer; don't overwrite it.
            if sathue_mode != 'dual':
                window['-IMAGE-'].update(data=bio.getvalue(), size=(w, h))
            current_main_display_size = (w, h)
            if sat_preview_visible and current_main_display_size != old_main_display_size:
                # In dual mode, -SAT-IMAGE- is owned by the dual colormap renderer
                # (sathue_right_img_full / HSV or YUV colormap), so we must NOT
                # re-render sathue_img_full (the stale single-mode colormap) here.
                if sathue_mode == 'dual':
                    _render_dual_main_previews(preserve=preserve_preview_size)
                else:
                    _render_sathue_display()

            iclr_disp = values['-IN-CLR-']
            oclr_disp = values['-OUT-CLR-']
            mode_desc = build_csc_mode_str(
                get_clrspc_from_display(iclr_disp),
                get_clrspc_from_display(oclr_disp),
            )
            step1_coef_str = str(current_step1_coefs).replace('\n', ' ') if current_step1_coefs is not None else "None"
            step1_offset_str = str(current_step1_offset) if current_step1_offset is not None else "None"
            step2_coefs_disp, step2_offset_disp = _apply_step2_channel_swap_display(
                values.get('-CHANNEL-SWAP-', 'None'),
                current_step2_coefs,
                current_step2_offset,
                current_input_is_yuv,
                current_output_is_yuv,
            )
            step2_coef_str = str(step2_coefs_disp).replace('\n', ' ') if step2_coefs_disp is not None else "None"
            step2_offset_str = str(step2_offset_disp) if step2_offset_disp is not None else "None"
            window['-DISPLAY-SIZE-'].update(value=f"{w}x{h} ({mode_desc})")
            # In dual mode the "Display Size" field is repurposed to show the
            # left-colormap trajectory "(xs, ys) -> (xe, ye) [Frozen]"; that
            # update is owned by _update_dual_lock_display, so leave the
            # default W x H text in place only when no frozen pixel is active.
            if sathue_mode == 'dual' and sathue_left_locked:
                _update_dual_lock_display()
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
    update_channel_swap_control(window, {'-CHANNEL-SWAP-': 'None'}, ALGO_RK_HW_CSC)
    update_sathue_map()
    _set_sat_preview_visible(False)

    # Start with the target-color-range controls disabled until Enable is checked.
    window['-SAT-TARGET-HS-SPIN-'].update(disabled=True)
    window['-SAT-TARGET-HE-SPIN-'].update(disabled=True)
    window['-SAT-TARGET-HST-SPIN-'].update(disabled=True)
    window['-SAT-TARGET-HET-SPIN-'].update(disabled=True)
    window['-SAT-TARGET-HSP-SPIN-'].update(disabled=True)
    window['-SAT-TARGET-HEP-SPIN-'].update(disabled=True)
    # Fix Target Hue value controls are disabled until its checkbox is checked.
    window['-SAT-FIX-HUE-'].update(disabled=True)
    window['-SAT-FIX-HUE-SPIN-'].update(disabled=True)

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
                sathue_render_after_id = None
                # Route the redraw to the correct renderer: in dual mode the right
                # colormap is sathue_right_img_full (NOT the stale sathue_img_full from
                # any prior single-mode render), so we must use the dual renderer
                # here, otherwise the right pane falls back to the stale YUV/HSV
                # colormap from single mode after a window resize.
                if sathue_mode == 'dual':
                    _render_dual_main_previews(preserve=False)
                else:
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
            update_channel_swap_control(window, values, current_algo_type)
            print(f"algo_type switch to: {new_algo_type}")
            trigger_convert(values, preserve_preview_size=True)
        elif event == '-CHANNEL-SWAP-':
            display_result(window, values)
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
        elif event == '-DISP-SCALE-':
            current_display_scale = round(float(values['-DISP-SCALE-']) / 0.05) * 0.05
            window['-DISP-SCALE-SPIN-'].update(value=f"{current_display_scale:.2f}")
            trigger_convert(values)
        elif event_key == '-DISP-SCALE-SPIN-' and event_suffix in {'STEP', 'ENTER'}:
            try:
                v = float(values.get('-DISP-SCALE-SPIN-', current_display_scale))
            except (TypeError, ValueError):
                v = current_display_scale
            current_display_scale = round(max(0.1, min(2.0, v)) / 0.05) * 0.05
            window['-DISP-SCALE-'].update(value=current_display_scale)
            window['-DISP-SCALE-SPIN-'].update(value=f"{current_display_scale:.2f}")
            trigger_convert(values)
        elif event_key == '-DISP-SCALE-' and event_suffix in {'LEFT', 'RIGHT'}:
            delta = -0.05 if event_suffix == 'LEFT' else 0.05
            current_display_scale = round(max(0.1, min(2.0, current_display_scale + delta)) / 0.05) * 0.05
            window['-DISP-SCALE-'].update(value=current_display_scale)
            window['-DISP-SCALE-SPIN-'].update(value=f"{current_display_scale:.2f}")
            trigger_convert(values)
        elif event == '-SAT-SHOW-MAP-':
            show_map = values.get('-SAT-SHOW-MAP-', False)
            # Mutual exclusion with Adjust Target Color Range: showing the color map
            # conflicts with the target-color-range preview on the main image.
            if show_map:
                window['-SAT-TARGET-ENABLE-'].update(value=False)
                values['-SAT-TARGET-ENABLE-'] = False
                sathue_target_enabled = False
                window['-SAT-TARGET-HS-SPIN-'].update(disabled=True)
                window['-SAT-TARGET-HE-SPIN-'].update(disabled=True)
                window['-SAT-TARGET-HST-SPIN-'].update(disabled=True)
                window['-SAT-TARGET-HET-SPIN-'].update(disabled=True)
                window['-SAT-TARGET-HSP-SPIN-'].update(disabled=True)
                window['-SAT-TARGET-HEP-SPIN-'].update(disabled=True)
            _set_sat_preview_visible(show_map)
            main_preview_size = _get_preview_widget_size('-MAIN-IMAGE-COL-')
            last_main_preview_size = main_preview_size
            # Do NOT trigger -REDRAW-IMAGE- here. trigger_convert -> display_result
            # would overwrite -IMAGE- with the input/output planar, which clobbers
            # the left-side colormap in dual mode. Show Color Map only toggles the
            # sat preview visibility and the colormap renderers below handle the rest.
            if sat_preview_visible:
                # Re-render the colormap(s) according to the current mode.
                # In dual mode, regenerating the colormaps also re-applies the freeze markers.
                if sathue_mode == 'dual':
                    update_sathue_map(preserve_display_size=False)
                else:
                    window.TKroot.after(50, _render_sathue_display)
        elif event == '-SAT-SET-COLOR-':
            sathue_set_color_enabled = values.get('-SAT-SET-COLOR-', False)
            # Mutual exclusion with Set Luma/Value (-SAT-LUMA-).
            if sathue_set_color_enabled:
                window['-SAT-LUMA-'].update(value=False)
                values['-SAT-LUMA-'] = False
                window['-SAT-LUMA-SLIDER-'].update(disabled=True)
                window['-SAT-LUMA-SPIN-'].update(disabled=True)
            else:
                luma_checked = values.get('-SAT-LUMA-', True)
                window['-SAT-LUMA-SLIDER-'].update(disabled=not luma_checked)
                window['-SAT-LUMA-SPIN-'].update(disabled=not luma_checked)
            window['-SAT-COLOR-INPUT-'].update(disabled=not sathue_set_color_enabled)
            if sathue_set_color_enabled:
                color_vals = parse_color_input(values.get('-SAT-COLOR-INPUT-', ''))
                if color_vals is not None:
                    if sathue_mode == 'dual':
                        _set_sathue_dual_color_lock(color_vals)
                    else:
                        _set_sathue_color_lock(color_vals)
            else:
                if sathue_mode == 'dual':
                    _clear_sathue_dual_color_lock()
                else:
                    _clear_sathue_color_lock()
        elif event == '-SAT-CLRSPC-':
            new_cs = values['-SAT-CLRSPC-']
            if new_cs in ('YCbCr=>HSV', 'HSV=>YCbCr'):
                # Enter dual mode. The actual dual-colormap rendering only happens once
                # -SAT-SHOW-MAP- is enabled (see _refresh_sathue_display).
                sathue_mode = 'dual'
                sathue_left_colorspace = 'YUV' if new_cs == 'YCbCr=>HSV' else 'RGB'
                sathue_right_colorspace = 'RGB' if new_cs == 'YCbCr=>HSV' else 'YUV'
                # Reset all frozen markers.
                sathue_locked = False
                sathue_locked_pix = None
                sathue_locked_input = None
                sathue_left_locked = False
                sathue_left_locked_pix = None
                sathue_left_locked_input = None
                sathue_right_locked_pix = None
                sathue_right_locked_input = None
                # Only render the dual colormaps if the user has already enabled Show Color Map.
                if sat_preview_visible:
                    update_sathue_map(preserve_display_size=False)
                else:
                    # Clear any stale single-mode colormap so the right pane is empty.
                    window['-SAT-IMAGE-'].update(data=b'', size=(1, 1))
                # Clear input/output text in case they show old values.
                window['-INPUT-PIXEL-INFO-'].update('')
                window['-OUTPUT-PIXEL-INFO-'].update('')
                window['-POSITION-INFO-'].update('')
            else:
                # Single mode.
                sathue_mode = 'single'
                sathue_colorspace = 'YUV' if new_cs == 'YCbCr' else 'RGB'
                # Reset all frozen markers.
                sathue_locked = False
                sathue_locked_pix = None
                sathue_locked_input = None
                sathue_left_locked = False
                sathue_left_locked_pix = None
                sathue_left_locked_input = None
                sathue_right_locked_pix = None
                sathue_right_locked_input = None
                if sathue_set_color_enabled:
                    color_vals = parse_color_input(values.get('-SAT-COLOR-INPUT-', ''))
                    if color_vals is not None:
                        _set_sathue_color_lock(color_vals)
                        continue
                if sathue_locked and sathue_locked_pix is not None:
                    sathue_locked_input = _get_sathue_input_at(*sathue_locked_pix)
                update_sathue_map()
        elif event == '-SAT-HS-TYPE-':
            old_hs_type = sathue_hs_type
            sathue_hs_type = _normalize_hs_type(values.get('-SAT-HS-TYPE-', 'HSV'))
            _remap_rgb_inputs_for_hs_type_change(old_hs_type, sathue_hs_type)
            _refresh_rgb_lock_pixels()
            if sat_preview_visible:
                update_sathue_map(preserve_display_size=True)
        elif event == '-SAT-RGB-MAP-':
            sathue_rgb_map_mode = RGB_COLORMAP_MODE_HEX if values.get('-SAT-RGB-MAP-') == 'Hex' else RGB_COLORMAP_MODE_CIRCLE
            _refresh_rgb_lock_pixels()
            if sat_preview_visible:
                update_sathue_map(preserve_display_size=True)
        elif event == '-SAT-LUMA-':
            # Set Luma/Value checkbox: mutually exclusive with -SAT-SET-COLOR-.
            luma_enabled = values.get('-SAT-LUMA-', True)
            if luma_enabled:
                window['-SAT-SET-COLOR-'].update(value=False)
                values['-SAT-SET-COLOR-'] = False
                sathue_set_color_enabled = False
                window['-SAT-COLOR-INPUT-'].update(disabled=True)
                if sathue_mode == 'dual':
                    _clear_sathue_dual_color_lock()
                else:
                    _clear_sathue_color_lock()
            window['-SAT-LUMA-SLIDER-'].update(disabled=not luma_enabled)
            window['-SAT-LUMA-SPIN-'].update(disabled=not luma_enabled)
            update_sathue_map(preserve_display_size=True)
        elif event == '-SAT-LUMA-SLIDER-':
            sathue_luma_val = int(values['-SAT-LUMA-SLIDER-'])
            window['-SAT-LUMA-SPIN-'].update(value=str(sathue_luma_val))
            if sathue_mode == 'dual' and sathue_left_locked and not sathue_set_color_enabled:
                # In dual + frozen mode the luma slider drives the left frozen pixel's
                # luma (Y for YUV, V for RGB/HSV); the right side is re-mirrored.
                _update_dual_frozen_left_luma(sathue_luma_val)
            elif sathue_locked and not sathue_set_color_enabled:
                sathue_locked_input = _get_sathue_input_at(*sathue_locked_pix)
            update_sathue_map(preserve_display_size=True)
        elif event == '-SAT-HUE-':
            sathue_hue_val = int(values['-SAT-HUE-'])
            window['-SAT-HUE-SPIN-'].update(value=str(sathue_hue_val))
            update_sathue_map(preserve_display_size=True)
            if sathue_target_enabled and current_planar_in is not None:
                display_result(window, values)
        elif event == '-SAT-SAT-':
            sathue_sat_val = int(values['-SAT-SAT-']) / 180.0
            window['-SAT-SAT-SPIN-'].update(value=f"{sathue_sat_val:.2f}")
            update_sathue_map(preserve_display_size=True)
            if sathue_target_enabled and current_planar_in is not None:
                display_result(window, values)
        elif event == '-SAT-TARGET-ENABLE-':
            sathue_target_enabled = values.get('-SAT-TARGET-ENABLE-', False)
            # Mutual exclusion with Show Color Map: the target-color-range preview
            # renders on the main image, so hide the Sat/Hue colormap when active.
            if sathue_target_enabled:
                window['-SAT-SHOW-MAP-'].update(value=False)
                values['-SAT-SHOW-MAP-'] = False
                _set_sat_preview_visible(False)
            window['-SAT-TARGET-HS-SPIN-'].update(disabled=not sathue_target_enabled)
            window['-SAT-TARGET-HE-SPIN-'].update(disabled=not sathue_target_enabled)
            window['-SAT-TARGET-HST-SPIN-'].update(disabled=not sathue_target_enabled)
            window['-SAT-TARGET-HET-SPIN-'].update(disabled=not sathue_target_enabled)
            window['-SAT-TARGET-HSP-SPIN-'].update(disabled=not sathue_target_enabled)
            window['-SAT-TARGET-HEP-SPIN-'].update(disabled=not sathue_target_enabled)
            if current_planar_in is not None:
                display_result(window, values)
        elif event == '-SAT-FIX-HUE-ENABLE-':
            sathue_fix_hue_enabled = values.get('-SAT-FIX-HUE-ENABLE-', False)
            window['-SAT-FIX-HUE-'].update(disabled=not sathue_fix_hue_enabled)
            window['-SAT-FIX-HUE-SPIN-'].update(disabled=not sathue_fix_hue_enabled)
            if sathue_target_enabled and current_planar_in is not None:
                display_result(window, values)
        elif event == '-SAT-FIX-HUE-':
            sathue_fix_hue_val = int(values['-SAT-FIX-HUE-'])
            window['-SAT-FIX-HUE-SPIN-'].update(value=str(sathue_fix_hue_val))
            if sathue_target_enabled and current_planar_in is not None:
                display_result(window, values)
        elif event == '-SAT-DELTA-LUMA-':
            sathue_delta_luma_val = int(values['-SAT-DELTA-LUMA-'])
            window['-SAT-DELTA-LUMA-SPIN-'].update(value=str(sathue_delta_luma_val))
            if sathue_target_enabled and current_planar_in is not None:
                display_result(window, values)
        elif event == '-SAT-DELTA-LUMA-RESET-':
            sathue_delta_luma_val = 0
            window['-SAT-DELTA-LUMA-'].update(value=0)
            window['-SAT-DELTA-LUMA-SPIN-'].update(value='0')
            if sathue_target_enabled and current_planar_in is not None:
                display_result(window, values)
        elif event_key in ('-SAT-TARGET-HS-SPIN-', '-SAT-TARGET-HE-SPIN-',
                           '-SAT-TARGET-HST-SPIN-', '-SAT-TARGET-HET-SPIN-',
                           '-SAT-TARGET-HSP-SPIN-', '-SAT-TARGET-HEP-SPIN-') and event_suffix in {'STEP', 'ENTER'}:
            # Start/End Hue (HS/HE), their Tail values (HST/HET) and Padding
            # values (HSP/HEP).  The HS/HE sliders were removed, so these spins
            # are the only input.
            if event_key == '-SAT-TARGET-HS-SPIN-':
                try:
                    v = int(values.get(event_key, sathue_target_hs))
                    v = max(0, min(360, v))
                except (TypeError, ValueError):
                    v = sathue_target_hs
                sathue_target_hs = v
            elif event_key == '-SAT-TARGET-HE-SPIN-':
                try:
                    v = int(values.get(event_key, sathue_target_he))
                    v = max(0, min(360, v))
                except (TypeError, ValueError):
                    v = sathue_target_he
                sathue_target_he = v
            elif event_key == '-SAT-TARGET-HST-SPIN-':
                try:
                    v = int(values.get(event_key, sathue_target_hst))
                    v = max(0, min(60, v))
                except (TypeError, ValueError):
                    v = sathue_target_hst
                sathue_target_hst = v
            elif event_key == '-SAT-TARGET-HET-SPIN-':
                try:
                    v = int(values.get(event_key, sathue_target_het))
                    v = max(0, min(60, v))
                except (TypeError, ValueError):
                    v = sathue_target_het
                sathue_target_het = v
            elif event_key == '-SAT-TARGET-HSP-SPIN-':
                try:
                    v = int(values.get(event_key, sathue_target_hsp))
                    v = max(0, min(60, v))
                except (TypeError, ValueError):
                    v = sathue_target_hsp
                sathue_target_hsp = v
            else:
                try:
                    v = int(values.get(event_key, sathue_target_hep))
                    v = max(0, min(60, v))
                except (TypeError, ValueError):
                    v = sathue_target_hep
                sathue_target_hep = v
            window[event_key].update(value=str(v))
            if sathue_target_enabled and current_planar_in is not None:
                display_result(window, values)
        elif event_key == '-SAT-FIX-HUE-SPIN-' and event_suffix in {'STEP', 'ENTER'}:
            try:
                v = int(values.get('-SAT-FIX-HUE-SPIN-', sathue_fix_hue_val))
                v = max(0, min(360, v))
            except (TypeError, ValueError):
                v = sathue_fix_hue_val
            sathue_fix_hue_val = v
            window['-SAT-FIX-HUE-'].update(value=v)
            window['-SAT-FIX-HUE-SPIN-'].update(value=str(v))
            if sathue_target_enabled and current_planar_in is not None:
                display_result(window, values)
        elif event_key.startswith('-SAT-') and event_key.endswith('-SPIN-') and event_suffix == 'STEP':
            slider_key = event_key.replace('-SPIN-', '-')
            if event_key == '-SAT-LUMA-SPIN-':
                v = int(values[event_key])
                v = max(0, min(255, v))
                sathue_luma_val = v
                window['-SAT-LUMA-SLIDER-'].update(value=v)
                if sathue_mode == 'dual' and sathue_left_locked and not sathue_set_color_enabled:
                    _update_dual_frozen_left_luma(sathue_luma_val)
                elif sathue_locked and not sathue_set_color_enabled:
                    sathue_locked_input = _get_sathue_input_at(*sathue_locked_pix)
            elif event_key == '-SAT-HUE-SPIN-':
                v = int(values[event_key])
                v = max(-180, min(180, v))
                sathue_hue_val = v
                window[slider_key].update(value=v)
            elif event_key == '-SAT-DELTA-LUMA-SPIN-':
                try:
                    v = int(values[event_key])
                    v = max(-255, min(255, v))
                except ValueError:
                    v = sathue_delta_luma_val
                sathue_delta_luma_val = v
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
            if sathue_target_enabled and current_planar_in is not None:
                display_result(window, values)
        elif event_key.startswith('-SAT-') and event_key.endswith('-SPIN-') and event_suffix == 'ENTER':
            slider_key = event_key.replace('-SPIN-', '-')
            if event_key == '-SAT-LUMA-SPIN-':
                try:
                    v = int(values[event_key])
                    v = max(0, min(255, v))
                except ValueError:
                    v = sathue_luma_val
                sathue_luma_val = v
                window['-SAT-LUMA-SLIDER-'].update(value=v)
                window[event_key].update(value=str(v))
                if sathue_mode == 'dual' and sathue_left_locked and not sathue_set_color_enabled:
                    _update_dual_frozen_left_luma(sathue_luma_val)
                elif sathue_locked:
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
            elif event_key == '-SAT-DELTA-LUMA-SPIN-':
                try:
                    v = int(values[event_key])
                    v = max(-255, min(255, v))
                except ValueError:
                    v = sathue_delta_luma_val
                sathue_delta_luma_val = v
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
            if sathue_target_enabled and current_planar_in is not None:
                display_result(window, values)
        elif event == '-SAT-HUE-RESET-':
            sathue_hue_val = 0
            window['-SAT-HUE-'].update(value=0)
            window['-SAT-HUE-SPIN-'].update(value='0')
            update_sathue_map(preserve_display_size=True)
            if sathue_target_enabled and current_planar_in is not None:
                display_result(window, values)
        elif event == '-SAT-SAT-RESET-':
            sathue_sat_val = 1.0
            window['-SAT-SAT-'].update(value=180)
            window['-SAT-SAT-SPIN-'].update(value='1.00')
            update_sathue_map(preserve_display_size=True)
            if sathue_target_enabled and current_planar_in is not None:
                display_result(window, values)
        elif event == '-SAT-COLOR-INPUT-+ENTER':
            if sathue_set_color_enabled:
                color_vals = parse_color_input(values.get('-SAT-COLOR-INPUT-', ''))
                if color_vals is not None:
                    if sathue_mode == 'dual':
                        _set_sathue_dual_color_lock(color_vals)
                    else:
                        _set_sathue_color_lock(color_vals)
        elif event_key.startswith('-SAT-') and event_key.endswith('-') and event_suffix in {'LEFT', 'RIGHT'}:
            delta = -1 if event_suffix == 'LEFT' else 1
            cur = int(values[event_key])
            if event_key == '-SAT-LUMA-SLIDER-':
                cur = max(0, min(255, cur + delta))
                sathue_luma_val = cur
                window['-SAT-LUMA-SPIN-'].update(value=str(cur))
                window[event_key].update(value=cur)
                if sathue_mode == 'dual' and sathue_left_locked and not sathue_set_color_enabled:
                    _update_dual_frozen_left_luma(sathue_luma_val)
                elif sathue_locked and not sathue_set_color_enabled:
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
            elif event_key == '-SAT-DELTA-LUMA-':
                cur = max(-255, min(255, cur + delta))
                sathue_delta_luma_val = cur
                window['-SAT-DELTA-LUMA-SPIN-'].update(value=str(cur))
                window[event_key].update(value=cur)
            elif event_key == '-SAT-FIX-HUE-':
                cur = max(0, min(360, cur + delta))
                sathue_fix_hue_val = cur
                window['-SAT-FIX-HUE-SPIN-'].update(value=str(cur))
                window[event_key].update(value=cur)
            update_sathue_map(preserve_display_size=True)
            if sathue_target_enabled and current_planar_in is not None:
                display_result(window, values)
        elif event in convert_keys:
            trigger_convert(values)
        elif event in ['-SHOW-IN-', '-SHOW-OUT-']:
            display_result(window, values)
            # In dual + frozen + YUV=>RGB mode the -SHOW-IN-/OUT- radio also
            # drives the right RGB colormap (V value + output marker position)
            # and flips the input/output marker styles, so we must re-render
            # the Sat/Hue map and refresh the lock display when the user
            # toggles it.  In all other dual modes this is a no-op because
            # dual_use_output stays False.
            sathue_show_output = bool(values.get('-SHOW-OUT-', False))
            if sathue_mode == 'dual' and sathue_left_locked and sathue_left_locked_input is not None:
                update_sathue_map(preserve_display_size=True)
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
                elif ext in ('.png', '.jpg', '.jpeg', '.bmp'):
                    # 图片文件按 RGB888 + RGB_Full 处理；分辨率在 trigger_convert 中解码后自动更新
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
            if sathue_mode == 'dual':
                is_mouse_in_sathue_left = True
                is_mouse_in_image = False
                is_mouse_in_sathue = False
                if sathue_left_locked:
                    _update_dual_lock_display()
            else:
                is_mouse_in_image = True
                is_mouse_in_sathue_left = False
                if is_pixel_info_frozen and current_mouse_pos is not None:
                    update_pixel_info(window, current_mouse_pos[0], current_mouse_pos[1])
        elif event == '-IMAGE-+LEAVE':
            if sathue_mode == 'dual':
                is_mouse_in_sathue_left = False
                if not sathue_left_locked:
                    window['-INPUT-PIXEL-INFO-'].update('(hover over image)')
                    window['-OUTPUT-PIXEL-INFO-'].update('')
                    window['-POSITION-INFO-'].update('')
            else:
                is_mouse_in_image = False
                is_mouse_in_sathue_left = False
        elif event == '-SAT-IMAGE-+ENTER':
            is_mouse_in_sathue = True
            is_mouse_in_image = False
            is_mouse_in_sathue_left = False
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
            if sathue_mode == 'dual':
                # Dual mode: -IMAGE- displays the left colormap; route to sathue hover.
                if sathue_left_locked:
                    _update_dual_lock_display()
                elif sathue_left_img_full is not None:
                    e = window['-IMAGE-'].user_bind_event
                    wx, wy = e.x, e.y
                    eff_x = int(wx / sathue_left_display_scale) - sathue_margin
                    eff_y = int(wy / sathue_left_display_scale) - sathue_margin
                    if 0 <= eff_x < SAT_COLORMAP_SIZE and 0 <= eff_y < SAT_COLORMAP_SIZE:
                        invals = _get_sathue_input_at(eff_x, eff_y, cs=sathue_left_colorspace)
                        out_pos = _compute_sathue_output_pos(cs=sathue_left_colorspace, invals=invals)
                        window['-INPUT-PIXEL-INFO-'].update(
                            _format_dual_input_str(sathue_left_colorspace, invals, out_pos, sathue_left_locked))
                        window['-OUTPUT-PIXEL-INFO-'].update(
                            _format_dual_output_str(sathue_left_colorspace, invals, out_pos, sathue_left_locked))
                        window['-POSITION-INFO-'].update(
                            _format_sathue_pos_str(eff_x, eff_y, frozen=False))
                        sathue_left_mouse_pos = (eff_x, eff_y)
            elif current_planar_in is not None and not is_pixel_info_frozen:
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
            if sathue_mode == 'dual':
                # Dual mode: -SAT-IMAGE- displays the right colormap; route to sathue hover.
                if sathue_left_locked:
                    _update_dual_lock_display()
                elif sathue_right_img_full is not None:
                    e = window['-SAT-IMAGE-'].user_bind_event
                    wx, wy = e.x, e.y
                    eff_x = int(wx / sathue_right_display_scale) - sathue_margin
                    eff_y = int(wy / sathue_right_display_scale) - sathue_margin
                    if 0 <= eff_x < SAT_COLORMAP_SIZE and 0 <= eff_y < SAT_COLORMAP_SIZE:
                        invals = _get_sathue_input_at(eff_x, eff_y, cs=sathue_right_colorspace)
                        out_pos = _compute_sathue_output_pos(cs=sathue_right_colorspace, invals=invals)
                        window['-INPUT-PIXEL-INFO-'].update(
                            _format_dual_input_str(sathue_right_colorspace, invals, out_pos, sathue_left_locked))
                        window['-OUTPUT-PIXEL-INFO-'].update(
                            _format_dual_output_str(sathue_right_colorspace, invals, out_pos, sathue_left_locked))
                        window['-POSITION-INFO-'].update(
                            _format_sathue_pos_str(eff_x, eff_y, frozen=False))
                        sathue_mouse_pos = (eff_x, eff_y)
            elif sathue_locked:
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
            if sathue_mode == 'dual':
                if sathue_set_color_enabled:
                    continue
                # Dual mode: left is the source-of-truth trigger.
                if is_mouse_in_sathue_left and sathue_left_mouse_pos is not None:
                    if sathue_left_locked:
                        # Unlock both sides.
                        sathue_left_locked = False
                        sathue_left_locked_pix = None
                        sathue_left_locked_input = None
                        sathue_right_locked_pix = None
                        sathue_right_locked_input = None
                        sathue_locked = False
                        sathue_locked_pix = None
                        sathue_locked_input = None
                        # Restore hover display using left colorspace.
                        if sathue_left_mouse_pos is not None:
                            invals = _get_sathue_input_at(*sathue_left_mouse_pos, cs=sathue_left_colorspace)
                            out_pos = _compute_sathue_output_pos(cs=sathue_left_colorspace, invals=invals)
                            window['-INPUT-PIXEL-INFO-'].update(
                                _format_dual_input_str(sathue_left_colorspace, invals, out_pos, sathue_left_locked))
                            window['-OUTPUT-PIXEL-INFO-'].update(
                                _format_dual_output_str(sathue_left_colorspace, invals, out_pos, sathue_left_locked))
                            window['-POSITION-INFO-'].update(
                                _format_sathue_pos_str(*sathue_left_mouse_pos, frozen=False))
                    else:
                        # Lock left, mirror to right.
                        eff_x, eff_y = sathue_left_mouse_pos
                        sathue_left_locked = True
                        sathue_left_locked_pix = (eff_x, eff_y)
                        sathue_left_locked_input = _get_sathue_input_at(eff_x, eff_y, cs=sathue_left_colorspace)
                        # Also keep the single-mode globals in sync so single-mode code paths work.
                        sathue_locked = True
                        sathue_locked_pix = (eff_x, eff_y)
                        sathue_locked_input = sathue_left_locked_input
                        # Compute mirrored input on the right colorspace and convert to (pix_x, pix_y).
                        if sathue_left_colorspace == 'YUV' and sathue_right_colorspace == 'RGB':
                            right_input = _yuv_to_rgb_input(sathue_left_locked_input)
                        elif sathue_left_colorspace == 'RGB' and sathue_right_colorspace == 'YUV':
                            right_input = _rgb_to_yuv_input(sathue_left_locked_input)
                        else:
                            right_input = sathue_left_locked_input
                        rx, ry = _input_to_lock_pix(right_input, cs=sathue_right_colorspace)
                        rx = int(np.clip(rx, 0, SAT_COLORMAP_SIZE - 1))
                        ry = int(np.clip(ry, 0, SAT_COLORMAP_SIZE - 1))
                        sathue_right_locked_pix = (rx, ry)
                        sathue_right_locked_input = right_input
                    update_sathue_map(preserve_display_size=False)
                    continue
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
