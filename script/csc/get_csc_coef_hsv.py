"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : get_csc_coef_hsv.py
Author      : vance.wu@rock-chips.com
Date        : 2026-05-14
Description : HSV-based BCSH implementation
"""

import numpy as np

ALGO_RK_HW_CSC = "RK HW CSC"
ALGO_RK_SW_CSC = "RK SW CSC"
ALGO_EVIDEO_CSC = "eVideo CSC"
ALGO_EVIDEO_CSC_PLAN_A = "eVideo CSC Plan A"
ALGO_EVIDEO_CSC_PLAN_B = "eVideo CSC Plan B"
ALGO_EVIDEO_CSC_PLAN_C = "eVideo CSC Plan C"
ALGO_RK_CSC = ALGO_RK_HW_CSC
ALGO_EVIDEO_CSC_FIX = ALGO_EVIDEO_CSC_PLAN_A
ALGO_RGB_ON_HSV_ON = ALGO_EVIDEO_CSC_PLAN_B
ALGO_RGB_ON_HSV_OFF = "rgbOnHsv_RgbCfg4YuvOff"
ALGO_RK_CSC_FIX_LEGACY = "RK CSC (fix contrast)"
ALGO_RGB_ON_HSV_LEGACY = "RGB_on_HSV"
ALGO_RK_CSC_LEGACY = "RK CSC"
ALGO_EVIDEO_CSC_FIX_LEGACY = "eVideo CSC fix"
ALGO_RGB_ON_HSV_ON_LEGACY = "rgbOnHsv_RgbCfg4YuvOn"

g_r2y_mat_bt709 = np.array(
    [[0.2126, 0.7152, 0.0722], [-0.114572, -0.385428, 0.5], [0.5, -0.454153, -0.045847]], dtype=np.float32
)
g_y2r_mat_bt709 = np.array([[1, 0, 1.5748], [1, -0.187324, -0.468124], [1, 1.8556, 0]], dtype=np.float32)


def normalize_algo_type(algo_type):
    """
    Normalize legacy algorithm aliases to the current public names.
    """
    if algo_type == ALGO_RK_CSC_LEGACY:
        return ALGO_RK_HW_CSC
    if algo_type == ALGO_RK_CSC_FIX_LEGACY:
        return ALGO_EVIDEO_CSC_PLAN_A
    if algo_type == ALGO_EVIDEO_CSC_FIX_LEGACY:
        return ALGO_EVIDEO_CSC_PLAN_A
    if algo_type in {ALGO_RGB_ON_HSV_LEGACY, ALGO_RGB_ON_HSV_ON_LEGACY, ALGO_RGB_ON_HSV_OFF}:
        return ALGO_EVIDEO_CSC_PLAN_B
    return algo_type


def _make_homogeneous_mat(mat3, ofs3=None):
    """
    Build a 4x4 homogeneous matrix from a 3x3 matrix and optional offset.
    """
    quad = np.eye(4, dtype=np.float32)
    quad[:3, :3] = mat3
    if ofs3 is not None:
        quad[:3, 3] = ofs3
    return quad


def _split_homogeneous_mat(quad):
    """
    Split a 4x4 homogeneous matrix into a 3x3 matrix and a 3x1 offset.
    """
    return quad[:3, :3], quad[:3, 3]


def _make_translation_quad(ofs3):
    """
    Build a pure-translation homogeneous matrix.
    """
    return _make_homogeneous_mat(np.eye(3, dtype=np.float32), ofs3)


def _make_center_scale_quad(scale_mat, center_vec):
    """
    Build a homogeneous transform that scales around a given center.
    """
    return _make_translation_quad(center_vec) @ _make_homogeneous_mat(scale_mat) @ _make_translation_quad(-center_vec)


def _map_centered_unit(raw_value):
    """
    Map a raw slider value [0, 511] to [-1, 1] with 256 as the exact center.
    """
    return float(np.clip((raw_value - 256) / 256.0, -1.0, 1.0))


def get_evideo_bcsh_param_pack(algo_type, bcsh_cfg, pixel_depth):
    """
    Map raw BCSH register values to the eVideo family parameter domain.
    """
    if algo_type not in {ALGO_EVIDEO_CSC, ALGO_EVIDEO_CSC_PLAN_A, ALGO_EVIDEO_CSC_PLAN_B, ALGO_EVIDEO_CSC_PLAN_C}:
        raise ValueError(f"Algorithm '{algo_type}' is not an eVideo family mode")

    max_pixel_val = float((1 << pixel_depth) - 1)
    mid_pixel_val = float(1 << (pixel_depth - 1))
    contrast = bcsh_cfg.contrast / 256.0
    saturation = bcsh_cfg.saturation / 256.0
    hue_deg = _map_centered_unit(bcsh_cfg.hue) * 180.0
    brightness_unit = _map_centered_unit(bcsh_cfg.brightness)
    brightness_pixel = brightness_unit * max_pixel_val
    rgb_offset_units = np.array(
        [
            _map_centered_unit(bcsh_cfg.r_offset),
            _map_centered_unit(bcsh_cfg.g_offset),
            _map_centered_unit(bcsh_cfg.b_offset),
        ],
        dtype=np.float32,
    )
    rgb_offset_pixels = rgb_offset_units * max_pixel_val
    rgb_gains = np.array(
        [
            bcsh_cfg.r_gain / 64.0,
            bcsh_cfg.g_gain / 64.0,
            bcsh_cfg.b_gain / 64.0,
        ],
        dtype=np.float32,
    )
    hue_rad = hue_deg * np.pi / 180.0

    return {
        "algo_type": algo_type,
        "contrast": float(contrast),
        "saturation": float(saturation),
        "hue_deg": float(hue_deg),
        "hue_rad": float(hue_rad),
        "hue_turn": float(hue_deg / 360.0),
        "brightness_unit": float(brightness_unit),
        "brightness_pixel": float(brightness_pixel),
        "rgb_gains": rgb_gains,
        "rgb_offset_units": rgb_offset_units.astype(np.float32),
        "rgb_offset_pixels": rgb_offset_pixels.astype(np.float32),
        "max_pixel_val": float(max_pixel_val),
        "mid_pixel_val": float(mid_pixel_val),
    }


def _get_evideo_bcsh_quads(algo_type, bcsh_cfg, pixel_depth):
    """
    Build reusable homogeneous transforms for the eVideo family.
    """
    params = get_evideo_bcsh_param_pack(algo_type, bcsh_cfg, pixel_depth)
    contrast = params["contrast"]
    saturation = params["saturation"]
    hue_rad = params["hue_rad"]
    cos_hue = np.cos(hue_rad)
    sin_hue = np.sin(hue_rad)
    rgb_gains = params["rgb_gains"]
    rgb_offsets = params["rgb_offset_pixels"]
    brightness = params["brightness_pixel"]
    mid_pixel_val = params["mid_pixel_val"]

    rgb_mat_rgbgains = np.diag(rgb_gains).astype(np.float32)
    rgb_mat_contrast = np.diag([contrast, contrast, contrast]).astype(np.float32)
    yuv_mat_contrast = np.diag([contrast, 1.0, 1.0]).astype(np.float32)
    contrast_center_rgb = np.array([mid_pixel_val, mid_pixel_val, mid_pixel_val], dtype=np.float32)
    contrast_center_yuv = np.array([mid_pixel_val, 0.0, 0.0], dtype=np.float32)
    chroma_center_yuv_raw = np.array([0.0, mid_pixel_val, mid_pixel_val], dtype=np.float32)
    chroma_center_yuv_signed = np.array([0.0, 0.0, 0.0], dtype=np.float32)
    hue_matrix = np.array([[1, 0, 0], [0, cos_hue, -sin_hue], [0, sin_hue, cos_hue]], dtype=np.float32)
    saturation_matrix = np.array([[1, 0, 0], [0, saturation, 0], [0, 0, saturation]], dtype=np.float32)

    quads = {
        "quad_yuv_hue_raw": _make_center_scale_quad(hue_matrix, chroma_center_yuv_raw),
        "quad_yuv_sat_raw": _make_center_scale_quad(saturation_matrix, chroma_center_yuv_raw),
        "quad_yuv_hue_signed": _make_center_scale_quad(hue_matrix, chroma_center_yuv_signed),
        "quad_yuv_sat_signed": _make_center_scale_quad(saturation_matrix, chroma_center_yuv_signed),
        "quad_r2y": _make_homogeneous_mat(g_r2y_mat_bt709, None),
        "quad_y2r": _make_homogeneous_mat(g_y2r_mat_bt709, None),
        "quad_rgb_rgbGains": _make_homogeneous_mat(rgb_mat_rgbgains),
        "quad_rgb_rgbOffsets": _make_translation_quad(rgb_offsets),
        "quad_yuv_bright": _make_translation_quad(np.array([brightness, 0.0, 0.0], dtype=np.float32)),
        "quad_rgb_contrast": _make_center_scale_quad(rgb_mat_contrast, contrast_center_rgb),
        "quad_yuv_contrast": _make_center_scale_quad(yuv_mat_contrast, contrast_center_yuv),
    }
    return params, quads


def _adjust_convert_quad_evideo(config, bcsh_cfg, quad_t):
    """
    Adjust the affine CSC transform with eVideo CSC parameters.
    """
    params, quads = _get_evideo_bcsh_quads(config.algo_type, bcsh_cfg, config.pixel_depth)
    mode = config.csc_mode
    quad_rgb_legacy_contrast = _make_homogeneous_mat(
        np.diag([params["contrast"], params["contrast"], params["contrast"]]).astype(np.float32)
    )
    # RGB 输出路径的亮度同样用像素域偏移，与 YUV 路径保持一致
    quad_rgb_legacy_bright = _make_homogeneous_mat(np.eye(3), np.ones(3) * params["brightness_pixel"]).astype(np.float32)

    if mode.is_input_yuv and mode.is_output_yuv:
        # Y2Y case, rgb_offsets not work here
        quad_out = (
            quads["quad_yuv_bright"]
            @ quad_t
            @ quads["quad_yuv_hue_raw"]
            @ quads["quad_yuv_sat_raw"]
            @ quads["quad_r2y"]
            @ quads["quad_rgb_rgbGains"]
            @ quad_rgb_legacy_contrast
            @ quads["quad_y2r"]
        )
    elif mode.is_input_yuv and not mode.is_output_yuv:
        # Y2R case, all params work here
        quad_out = (
            quad_rgb_legacy_bright
            @ quads["quad_rgb_rgbOffsets"]
            @ quads["quad_rgb_rgbGains"]
            @ quad_rgb_legacy_contrast
            @ quad_t
            @ quads["quad_yuv_hue_raw"]
            @ quads["quad_yuv_sat_raw"]
        )
    elif not mode.is_input_yuv and mode.is_output_yuv:
        # R2Y case, rgb_offsets not work here
        quad_out = (
            quads["quad_yuv_bright"]
            @ quads["quad_yuv_hue_raw"]
            @ quads["quad_yuv_sat_raw"]
            @ quad_t
            @ quads["quad_rgb_rgbGains"]
            @ quad_rgb_legacy_contrast
        )
    else:
        # R2R case, all params work here
        quad_out = (
            quad_rgb_legacy_bright
            @ quads["quad_rgb_rgbOffsets"]
            @ quad_t
            @ quads["quad_rgb_rgbGains"]
            @ quad_rgb_legacy_contrast
            @ quads["quad_y2r"]
            @ quads["quad_yuv_hue_signed"]
            @ quads["quad_yuv_sat_signed"]
            @ quads["quad_r2y"]
        )

    out_mat, out_vec = _split_homogeneous_mat(quad_out)
    return out_mat, out_vec


def _adjust_convert_quad_evideo_plan_a(config, bcsh_cfg, quad_t):
    """
    Adjust the affine CSC transform with the Plan A domain rules.
    """
    _, quads = _get_evideo_bcsh_quads(config.algo_type, bcsh_cfg, config.pixel_depth)
    mode = config.csc_mode

    if mode.is_input_yuv and mode.is_output_yuv: # Y2Y case
        quad_out = (
            quads["quad_yuv_bright"]
            @ quads["quad_yuv_contrast"]
            @ quads["quad_yuv_sat_raw"]
            @ quads["quad_yuv_hue_raw"]
            @ quad_t
        )
    elif mode.is_input_yuv and not mode.is_output_yuv: # Y2R case
        quad_out = (
            quads["quad_rgb_rgbOffsets"]
            @ quads["quad_rgb_rgbGains"]
            @ quad_t
            @ quads["quad_yuv_bright"]
            @ quads["quad_yuv_contrast"]
            @ quads["quad_yuv_sat_raw"]
            @ quads["quad_yuv_hue_raw"]
        )
    elif not mode.is_input_yuv and mode.is_output_yuv: # R2Y case
        quad_out = (
            quads["quad_yuv_bright"]
            @ quads["quad_yuv_contrast"]
            @ quads["quad_yuv_sat_raw"]
            @ quads["quad_yuv_hue_raw"]
            @ quad_t
            @ quads["quad_rgb_rgbOffsets"]
            @ quads["quad_rgb_rgbGains"]
        )
    else: # R2R case
        quad_out = (
            quads["quad_rgb_rgbOffsets"]
            @ quads["quad_rgb_rgbGains"]
            @ quad_t
            @ quads["quad_y2r"]
            @ quads["quad_yuv_bright"]
            @ quads["quad_yuv_contrast"]
            @ quads["quad_yuv_sat_signed"]
            @ quads["quad_yuv_hue_signed"]
            @ quads["quad_r2y"]
        )

    out_mat, out_vec = _split_homogeneous_mat(quad_out)
    return out_mat, out_vec


def _get_fixed_coefs_affine(config, float_mat, float_ofs):
    """
    Quantize a direct affine transform into fixed-point CSC coefficients.
    """
    fix_factor = 2**config.coef_precision
    scaled_mat = float_mat * fix_factor
    scaled_ofs = float_ofs * fix_factor
    fix_mat = (scaled_mat + np.sign(scaled_mat) * 0.5).astype(np.int32)
    fix_ofs = (scaled_ofs + np.sign(scaled_ofs) * 0.5).astype(np.int32)
    if config.platform.lower() == "rk3576":
        rnd_half = 1 << (config.coef_precision - 1)
        fix_ofs = (fix_ofs + rnd_half + (fix_ofs >> 31)) >> config.coef_precision
    return fix_mat, fix_ofs


def get_evideo_csc_coefs(config, bcsh_cfg, base_mat, base_ofs):
    """
    Build CSC coefficients for eVideo CSC and Plan A using the HSV helper module.
    """
    quad_t = _make_homogeneous_mat(base_mat, base_ofs)
    if config.algo_type == ALGO_EVIDEO_CSC:
        final_mat, final_ofs = _adjust_convert_quad_evideo(config, bcsh_cfg, quad_t)
    elif config.algo_type == ALGO_EVIDEO_CSC_PLAN_A:
        final_mat, final_ofs = _adjust_convert_quad_evideo_plan_a(config, bcsh_cfg, quad_t)
    else:
        raise ValueError(f"Algorithm '{config.algo_type}' is not supported by get_evideo_csc_coefs")

    if config.coef_precision > 0:
        return _get_fixed_coefs_affine(config, final_mat, final_ofs)
    return final_mat, final_ofs


def _split_quad_to_step(quad, config):
    """
    Split an optional homogeneous transform into one CSC matrix and offset pair.
    """
    if quad is None:
        return None, None

    step_mat, step_ofs = _split_homogeneous_mat(quad)
    if config.coef_precision > 0:
        return _get_fixed_coefs_affine(config, step_mat, step_ofs)
    return step_mat, step_ofs


def _get_plan_domain_quads(config, bcsh_cfg, base_mat, base_ofs):
    """
    Build reusable domain transforms for the two-step Plan A / Plan B paths.
    """
    _, quads = _get_evideo_bcsh_quads(config.algo_type, bcsh_cfg, config.pixel_depth)
    quad_base = _make_homogeneous_mat(base_mat, base_ofs)
    quad_rgb = quads["quad_rgb_rgbOffsets"] @ quads["quad_rgb_rgbGains"]
    quad_yuv_raw = (
        quads["quad_yuv_bright"]
        @ quads["quad_yuv_contrast"]
        @ quads["quad_yuv_sat_raw"]
        @ quads["quad_yuv_hue_raw"]
    )
    quad_yuv_signed = (
        quads["quad_yuv_bright"]
        @ quads["quad_yuv_contrast"]
        @ quads["quad_yuv_sat_signed"]
        @ quads["quad_yuv_hue_signed"]
    )
    return quads, quad_base, quad_rgb, quad_yuv_raw, quad_yuv_signed


def get_evideo_plan_a_steps(config, bcsh_cfg, base_mat, base_ofs):
    """
    Build the UI-visible YUV/RGB domain transforms for Plan A.
    """
    _, _, quad_rgb, quad_yuv_raw, _ = _get_plan_domain_quads(config, bcsh_cfg, base_mat, base_ofs)
    return _split_quad_to_step(quad_yuv_raw, config), _split_quad_to_step(quad_rgb, config)


def get_evideo_plan_a_runtime_steps(config, bcsh_cfg, base_mat, base_ofs):
    """
    Build the actual apply_csc step list for Plan A.
    """
    quads, quad_base, quad_rgb, quad_yuv_raw, quad_yuv_signed = _get_plan_domain_quads(config, bcsh_cfg, base_mat, base_ofs)
    mode = config.csc_mode

    if mode.is_input_yuv and mode.is_output_yuv:
        # Y2Y 按文档为 One-Step：Q_yuv 直接作用于 YUV，RgbGain/RgbOffset 不生效
        runtime_quads = [quad_yuv_raw @ quad_base]
    elif mode.is_input_yuv and not mode.is_output_yuv:
        runtime_quads = [quad_yuv_raw, quad_rgb @ quad_base]
    elif not mode.is_input_yuv and mode.is_output_yuv:
        runtime_quads = [quad_rgb, quad_yuv_raw @ quad_base]
    else:
        # R2R：Q_rgb 作用于输入 RGB；Q_yuv 作用于输出中间层 YUV，
        # 中间转换 (r2y->Q_yuv->y2r) 合成一步，避免中间层 clip 破坏负色度
        runtime_quads = [quad_rgb, quads["quad_y2r"] @ quad_yuv_signed @ quads["quad_r2y"] @ quad_base]

    return [_split_quad_to_step(quad, config) for quad in runtime_quads]


def get_evideo_plan_b_steps(config, bcsh_cfg, base_mat, base_ofs):
    """
    Build the confirmed two-step homogeneous transforms for Plan B.
    """
    quads, quad_base, quad_rgb, quad_yuv_raw, quad_yuv_signed = _get_plan_domain_quads(
        config, bcsh_cfg, base_mat, base_ofs
    )
    mode = config.csc_mode

    if mode.is_input_yuv and mode.is_output_yuv:
        step1_quad = None
        step2_quad = quad_yuv_raw @ quad_base
    elif mode.is_input_yuv and not mode.is_output_yuv:
        step1_quad = quad_yuv_raw
        step2_quad = quad_rgb @ quad_base
    elif not mode.is_input_yuv and mode.is_output_yuv:
        step1_quad = quad_rgb
        step2_quad = quad_yuv_raw @ quad_base
    else:
        # R2R：Q_yuv 作用于输出中间层 YUV，Q_rgb 作用于输出 RGB；
        # 中间转换 (r2y->Q_yuv->y2r->Q_rgb) 合成一步，避免中间层 clip 破坏负色度
        step1_quad = None
        step2_quad = quad_rgb @ quads["quad_y2r"] @ quad_yuv_signed @ quads["quad_r2y"] @ quad_base

    return _split_quad_to_step(step1_quad, config), _split_quad_to_step(step2_quad, config)


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
    rgb_normalized = planar_rgb.reshape(3, -1).T.astype(np.float32) / max_val
    params = get_evideo_bcsh_param_pack(algo_type, bcsh_cfg, pixel_depth)

    rgb_new = rgb_normalized.copy()
    rgb_new *= params["rgb_gains"].astype(np.float32)
    rgb_new += params["rgb_offset_units"].astype(np.float32)
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
    params = get_evideo_bcsh_param_pack(algo_type, bcsh_cfg, pixel_depth)

    rgb_normalized = planar_rgb.reshape(3, -1).T.astype(np.float32) / max_val
    hsv = _rgb_to_hsv(rgb_normalized)

    H = hsv[:, 0]
    S = hsv[:, 1]
    V = hsv[:, 2]

    H = (H + params["hue_turn"]) % 1.0
    S = np.clip(S * params["saturation"], 0.0, 1.0)
    V = np.clip((V - 0.5) * params["contrast"] + 0.5 + params["brightness_unit"], 0.0, 1.0)

    hsv_new = np.stack([H, S, V], axis=-1)
    rgb_new = _hsv_to_rgb(hsv_new)
    rgb_new *= params["rgb_gains"].astype(np.float32)
    rgb_new += params["rgb_offset_units"].astype(np.float32)
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
    params = get_evideo_bcsh_param_pack(algo_type, bcsh_cfg, pixel_depth)

    yuv_normalized = planar_yuv.reshape(3, -1).T.astype(np.float32) / max_val
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
