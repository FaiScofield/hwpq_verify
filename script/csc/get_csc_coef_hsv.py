"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : get_csc_coef_hsv.py
Author      : vance.wu@rock-chips.com
Date        : 2026-05-14
Description : HSV-based BCSH implementation
"""

import numpy as np

from get_csc_coefs import get_bcsh_param_pack


def _rgb_to_hsv(rgb):
    """
    Convert RGB to HSV.
    rgb: 2D array of shape (N, 3) with values in [0, 1].
    Returns: 2D array of shape (N, 3) with H in [0, 1], S in [0, 1], V in [0, 1].
    """
    r, g, b = rgb[:, 0], rgb[:, 1], rgb[:, 2]
    max_val = np.maximum(np.maximum(r, g), b)
    min_val = np.minimum(np.minimum(r, g), b)
    delta = max_val - min_val

    h = np.zeros_like(max_val)
    s = np.zeros_like(max_val)
    v = max_val

    mask = delta > 0
    s[mask] = delta[mask] / max_val[mask]

    mask_r = mask & (max_val == r)
    mask_g = mask & (max_val == g)
    mask_b = mask & (max_val == b) & ~(mask_r | mask_g)

    h[mask_r] = ((g[mask_r] - b[mask_r]) / delta[mask_r]) % 6
    h[mask_g] = ((b[mask_g] - r[mask_g]) / delta[mask_g]) + 2
    h[mask_b] = ((r[mask_b] - g[mask_b]) / delta[mask_b]) + 4
    h = h / 6.0

    return np.stack([h, s, v], axis=-1)


def _hsv_to_rgb(hsv):
    """
    Convert HSV to RGB.
    hsv: 2D array of shape (N, 3) with H in [0, 1], S in [0, 1], V in [0, 1].
    Returns: 2D array of shape (N, 3) with values in [0, 1].
    """
    h, s, v = hsv[:, 0], hsv[:, 1], hsv[:, 2]
    h = h * 6.0
    i = np.floor(h).astype(np.int32) % 6
    f = h - np.floor(h)
    p = v * (1 - s)
    q = v * (1 - s * f)
    t = v * (1 - s * (1 - f))

    r = np.zeros_like(v)
    g = np.zeros_like(v)
    b = np.zeros_like(v)

    m0 = i == 0
    r[m0] = v[m0]; g[m0] = t[m0]; b[m0] = p[m0]
    m1 = i == 1
    r[m1] = q[m1]; g[m1] = v[m1]; b[m1] = p[m1]
    m2 = i == 2
    r[m2] = p[m2]; g[m2] = v[m2]; b[m2] = t[m2]
    m3 = i == 3
    r[m3] = p[m3]; g[m3] = q[m3]; b[m3] = v[m3]
    m4 = i == 4
    r[m4] = t[m4]; g[m4] = p[m4]; b[m4] = v[m4]
    m5 = i == 5
    r[m5] = v[m5]; g[m5] = p[m5]; b[m5] = q[m5]

    return np.stack([r, g, b], axis=-1)


def apply_rgb_gain_offset(planar_rgb, bcsh_cfg, pixel_depth, algo_type):
    """
    Apply per-channel RGB gain and offset in normalized RGB space.
    planar_rgb: numpy array (3, H, W) in RGB
    bcsh_cfg: CscBcshConfig object
    pixel_depth: int (8 or 10)
    """
    h, w = planar_rgb.shape[1], planar_rgb.shape[2]
    max_val = (1 << pixel_depth) - 1
    rgb_normalized = planar_rgb.reshape(3, -1).T.astype(np.float64) / max_val
    params = get_bcsh_param_pack(algo_type, bcsh_cfg, pixel_depth)

    rgb_new = rgb_normalized.copy()
    rgb_new *= params["rgb_gains"].astype(np.float64)
    rgb_new += params["rgb_offset_units"].astype(np.float64)
    rgb_new = np.clip(rgb_new, 0.0, 1.0)

    planar_out = (rgb_new.T * max_val)
    planar_out = np.clip(planar_out + 0.5, 0, max_val).astype(planar_rgb.dtype)

    return planar_out.reshape(3, h, w)


def apply_bcsh_hsv(planar_rgb, bcsh_cfg, pixel_depth, algo_type):
    """
    Apply BCSH parameters in HSV color space, then apply RGB gain/offset.
    planar_rgb: numpy array (3, H, W) in RGB
    bcsh_cfg: CscBcshConfig object
    pixel_depth: int (8 or 10)
    """
    h, w = planar_rgb.shape[1], planar_rgb.shape[2]
    max_val = (1 << pixel_depth) - 1
    params = get_bcsh_param_pack(algo_type, bcsh_cfg, pixel_depth)

    rgb_normalized = planar_rgb.reshape(3, -1).T.astype(np.float64) / max_val
    hsv = _rgb_to_hsv(rgb_normalized)

    H = hsv[:, 0]
    S = hsv[:, 1]
    V = hsv[:, 2]

    H = (H + params["hue_turn"]) % 1.0
    S = np.clip(S * params["saturation"], 0.0, 1.0)
    V = np.clip((V - 0.5) * params["contrast"] + 0.5 + params["brightness_unit"], 0.0, 1.0)

    hsv_new = np.stack([H, S, V], axis=-1)
    rgb_new = _hsv_to_rgb(hsv_new)
    rgb_new *= params["rgb_gains"].astype(np.float64)
    rgb_new += params["rgb_offset_units"].astype(np.float64)
    rgb_new = np.clip(rgb_new, 0.0, 1.0)

    planar_out = (rgb_new.T * max_val)
    planar_out = np.clip(planar_out + 0.5, 0, max_val).astype(planar_rgb.dtype)
    return planar_out.reshape(3, h, w)


def apply_bcsh_yuv(planar_yuv, bcsh_cfg, pixel_depth, algo_type):
    """
    Apply BCSH parameters directly in YUV space and ignore RGB gain/offset.
    planar_yuv: numpy array (3, H, W) in YUV
    bcsh_cfg: CscBcshConfig object
    pixel_depth: int (8 or 10)
    """
    h, w = planar_yuv.shape[1], planar_yuv.shape[2]
    max_val = (1 << pixel_depth) - 1
    params = get_bcsh_param_pack(algo_type, bcsh_cfg, pixel_depth)

    yuv_normalized = planar_yuv.reshape(3, -1).T.astype(np.float64) / max_val
    y = yuv_normalized[:, 0]
    u = yuv_normalized[:, 1] - 0.5
    v = yuv_normalized[:, 2] - 0.5

    y = np.clip((y - 0.5) * params["contrast"] + 0.5 + params["brightness_unit"], 0.0, 1.0)
    cos_hue = np.cos(params["hue_rad"])
    sin_hue = np.sin(params["hue_rad"])
    u_new = (u * cos_hue - v * sin_hue) * params["saturation"]
    v_new = (u * sin_hue + v * cos_hue) * params["saturation"]

    yuv_new = np.stack([y, u_new + 0.5, v_new + 0.5], axis=-1)
    yuv_new = np.clip(yuv_new, 0.0, 1.0)

    planar_out = (yuv_new.T * max_val)
    planar_out = np.clip(planar_out + 0.5, 0, max_val).astype(planar_yuv.dtype)
    return planar_out.reshape(3, h, w)
