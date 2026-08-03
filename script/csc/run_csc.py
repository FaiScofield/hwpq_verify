#!/usr/bin/env python3
"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : run_csc.py
Author      : vance.wu@rock-chips.com
Date        : 2026-05-14
Description : CSC image conversion tool with optional UI
"""

import argparse
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from get_csc_coefs import (
    CscCoefConfig,
    CscBcshConfig,
    CscMode,
    get_csc_coefs,
    parse_csc_mode_str,
    ColorSpace,
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
    apply_bcsh_hsv,
)

DEBUG_DUMP_PATH = "D:/RkDefaultDumpData/"

FORMAT_NAMES = {
    0x0: "RGB888",
    0x1: "RGBA8888",
    0x2: "RGB_Planar",
    0x3: "YUV444P_YU24",
    0x4: "YUV444SP_NV24",
    0x5: "YUV444I_VU24",
    0x6: "YUV422P_YU16",
    0x7: "YUV422SP_NV16",
    0x8: "YUV420P_YU12",
    0x9: "YUV420SP_NV12",
    0xA: "YUV400_Gray",
    0x10: "RGB_10LSB",
    0x11: "RGBA_10LSB",
    0x12: "RGB_Planar_10LSB",
    0x13: "YUV444P_10LSB",
    0x14: "YUV444SP_10LSB",
    0x15: "YUV444I_10LSB",
    0x16: "YUV422P_10LSB",
    0x17: "YUV422SP_10LSB",
    0x18: "YUV420P_10LSB",
    0x19: "YUV420SP_10LSB",
    0x1A: "YUV400_10LSB",
    0x20: "RGB_10Packed",
    0x21: "RGBA_1010102",
    0x22: "RGB_Planar_10Packed",
    0x23: "YUV444P_10Packed",
    0x24: "YUV444SP_10Packed_NV30",
    0x25: "YUV444I_10Packed",
    0x26: "YUV422P_10Packed",
    0x27: "YUV422SP_10Packed_NV20",
    0x28: "YUV420P_10Packed",
    0x29: "YUV420SP_10Packed_NV15",
    0x2A: "YUV400_10Packed",
}

CLRSPC_NAMES = {
    0: "RGB_Limited",
    1: "RGB_Full",
    2: "BT601_Limited",
    3: "BT601_Full",
    4: "BT709_Limited",
    5: "BT709_Full",
    6: "BT2020_Limited",
    7: "BT2020_Full",
}

CLRSPC_TO_PARAMS = {
    0: ("rgb", "L"),
    1: ("rgb", "F"),
    2: ("bt601", "L"),
    3: ("bt601", "F"),
    4: ("bt709", "L"),
    5: ("bt709", "F"),
    8: ("bt2020", "L"),
    9: ("bt2020", "F"),
}

CLRSPC_OPTIONS = [0, 1, 2, 3, 4, 5, 6, 7]

FMT_OPTIONS_8BIT = [0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7, 0x8, 0x9, 0xA]
FMT_OPTIONS_10BIT = [0x10, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1A]
FMT_OPTIONS = FMT_OPTIONS_8BIT + FMT_OPTIONS_10BIT


def clrspc_to_mode_params(clrspc):
    """Convert clrspc integer to (color_space_name, range_flag) tuple"""
    if clrspc not in CLRSPC_TO_PARAMS:
        raise ValueError(f"Unsupported colorspace: {clrspc}, supported: {list(CLRSPC_TO_PARAMS.keys())}")
    return CLRSPC_TO_PARAMS[clrspc]


def build_csc_mode_str(input_clrspc, output_clrspc):
    """Build a CSC mode string from input and output colorspace integers"""
    ics, irange = clrspc_to_mode_params(input_clrspc)
    ocs, orange = clrspc_to_mode_params(output_clrspc)
    mode_str = f"{ics}{irange.lower()}_to_{ocs}{orange.lower()}"
    return mode_str


def is_yuv_format(fmt):
    """Check if format code represents a YUV format"""
    base = fmt & 0xF
    return base >= 0x3


def is_rgb_format(fmt):
    """Check if format code represents an RGB format"""
    base = fmt & 0xF
    return base <= 0x2


def get_pixel_depth(fmt):
    """Get pixel bit depth from format code"""
    modifier = fmt & 0xF0
    if modifier >= 0x10:
        return 10
    return 8


def get_bytes_per_element(fmt):
    """Get bytes per pixel element from format code"""
    modifier = fmt & 0xF0
    if modifier >= 0x10:
        return 2
    return 1


def _resample_yuv422(channel, target_w):
    """Resample a channel to target width by duplicating each column"""
    h, w = channel.shape
    if w == target_w:
        return channel
    ratio = target_w // w
    return np.repeat(channel, ratio, axis=1)


def _resample_yuv420(channel, target_h, target_w):
    """Resample a channel to target height and width by duplicating"""
    h, w = channel.shape
    if h == target_h and w == target_w:
        return channel
    h_ratio = target_h // h
    w_ratio = target_w // w
    result = np.repeat(channel, h_ratio, axis=0)
    result = np.repeat(result, w_ratio, axis=1)
    return result


def get_frame_size(width, height, fmt):
    """Calculate the expected frame size in bytes based on resolution and format"""
    base = fmt & 0xF
    bpe = get_bytes_per_element(fmt)

    # Base number of elements (pixels)
    if base == 0x0 or base == 0x2 or base == 0x3 or base == 0x5: # RGB888, RGB_Planar, YUV444P, YUV444I
        elements = width * height * 3
    elif base == 0x1: # RGBA8888
        elements = width * height * 4
    elif base == 0x4: # YUV444SP
        elements = width * height * 3
    elif base == 0x6 or base == 0x7: # YUV422P, YUV422SP
        elements = width * height * 2
    elif base == 0x8 or base == 0x9: # YUV420P, YUV420SP
        elements = width * height * 3 // 2
    elif base == 0xA: # YUV400_Gray
        elements = width * height
    else:
        elements = width * height * 3

    return elements * bpe


def read_raw_to_planar(filepath, width, height, fmt, repeat_to_444=False):
    """Read raw image file and return planar data.

    When repeat_to_444 is True (default), returns a 3D numpy array (3, H, W).
    When repeat_to_444 is False and the format is YUV422/YUV420, returns a list
    of three 2D arrays with per-channel native resolutions.
    """
    base_fmt = fmt & 0xF
    bpe = get_bytes_per_element(fmt)
    dtype = np.uint16 if bpe == 2 else np.uint8
    depth = get_pixel_depth(fmt)

    raw = np.fromfile(filepath, dtype=dtype)
    max_val = (1 << depth) - 1

    if base_fmt == 0x0:
        rgb = raw[: height * width * 3].reshape(height, width, 3)
        planar = np.zeros((3, height, width), dtype=dtype)
        planar[0] = rgb[:, :, 0]
        planar[1] = rgb[:, :, 1]
        planar[2] = rgb[:, :, 2]
        fmt = 0x2
    elif base_fmt == 0x1:
        rgba = raw[: height * width * 4].reshape(height, width, 4)
        planar = np.zeros((3, height, width), dtype=dtype)
        planar[0] = rgba[:, :, 0]
        planar[1] = rgba[:, :, 1]
        planar[2] = rgba[:, :, 2]
        fmt = 0x2
    elif base_fmt == 0x2:
        planar = raw[: 3 * height * width].reshape(3, height, width)
        fmt = 0x2
    elif base_fmt == 0x3:
        planar = raw[: 3 * height * width].reshape(3, height, width)
        fmt = 0x3
    elif base_fmt == 0x4:
        y_size = height * width
        y = raw[:y_size].reshape(height, width)
        uv = raw[y_size : y_size + y_size * 2].reshape(height, width, 2)
        planar = np.zeros((3, height, width), dtype=dtype)
        planar[0] = y
        planar[1] = uv[:, :, 0]
        planar[2] = uv[:, :, 1]
        fmt = 0x3
    elif base_fmt == 0x5:
        vuy = raw[: height * width * 3].reshape(height, width, 3)
        planar = np.zeros((3, height, width), dtype=dtype)
        planar[0] = vuy[:, :, 2]
        planar[1] = vuy[:, :, 1]
        planar[2] = vuy[:, :, 0]
        fmt = 0x3
    elif base_fmt == 0x6:
        y_size = height * width
        uv_size = height * (width // 2)
        y = raw[:y_size].reshape(height, width)
        u = raw[y_size : y_size + uv_size].reshape(height, width // 2)
        v = raw[y_size + uv_size : y_size + 2 * uv_size].reshape(height, width // 2)
        if repeat_to_444:
            planar = np.zeros((3, height, width), dtype=dtype)
            planar[0] = y
            planar[1] = _resample_yuv422(u, width)
            planar[2] = _resample_yuv422(v, width)
        else:
            planar = [y, u, v]
        fmt = 0x3 if repeat_to_444 else 0x6
    elif base_fmt == 0x7:
        y_size = height * width
        y = raw[:y_size].reshape(height, width)
        uv = raw[y_size : y_size + y_size].reshape(height, width // 2, 2)
        if repeat_to_444:
            planar = np.zeros((3, height, width), dtype=dtype)
            planar[0] = y
            planar[1] = _resample_yuv422(uv[:, :, 0], width)
            planar[2] = _resample_yuv422(uv[:, :, 1], width)
        else:
            planar = [y, uv[:, :, 0], uv[:, :, 1]]
        fmt = 0x3 if repeat_to_444 else 0x6
    elif base_fmt == 0x8:
        y_size = height * width
        uv_size = (height // 2) * (width // 2)
        y = raw[:y_size].reshape(height, width)
        u = raw[y_size : y_size + uv_size].reshape(height // 2, width // 2)
        v = raw[y_size + uv_size : y_size + 2 * uv_size].reshape(height // 2, width // 2)
        if repeat_to_444:
            planar = np.zeros((3, height, width), dtype=dtype)
            planar[0] = y
            planar[1] = _resample_yuv420(u, height, width)
            planar[2] = _resample_yuv420(v, height, width)
        else:
            planar = [y, u, v]
        fmt = 0x3 if repeat_to_444 else 0x8
    elif base_fmt == 0x9:
        y_size = height * width
        y = raw[:y_size].reshape(height, width)
        uv = raw[y_size : y_size + (height // 2) * width].reshape(height // 2, width // 2, 2)
        if repeat_to_444:
            planar = np.zeros((3, height, width), dtype=dtype)
            planar[0] = y
            planar[1] = _resample_yuv420(uv[:, :, 0], height, width)
            planar[2] = _resample_yuv420(uv[:, :, 1], height, width)
        else:
            planar = [y, uv[:, :, 0], uv[:, :, 1]]
        fmt = 0x3 if repeat_to_444 else 0x8
    elif base_fmt == 0xA:
        planar = np.zeros((3, height, width), dtype=dtype)
        y = raw[: height * width].reshape(height, width)
        planar[0] = y
        planar[1] = max_val if is_yuv_format(fmt) else 0
        planar[2] = planar[1].copy()
        fmt = 0xA
    else:
        raise ValueError(f"Unsupported base format: 0x{base_fmt:X}")

    if bpe == 2:
        if isinstance(planar, list):
            planar = [ch.astype(np.uint16) for ch in planar]
        else:
            planar = planar.astype(np.uint16)
        fmt += 0x10

    return planar, fmt


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp"}


def is_image_file(filepath):
    """按扩展名判断是否为受支持的图片文件（PNG/JPEG/BMP）。"""
    return os.path.splitext(filepath)[1].lower() in IMAGE_EXTENSIONS


def read_image_to_planar(filepath):
    """解码 PNG/JPEG/BMP 图片为 planar RGB 数据。

    返回 (planar, width, height)，其中 planar 为 uint8 数组 (3, H, W)，
    通道顺序为 R/G/B。
    """
    from PIL import Image

    with Image.open(filepath) as img:
        rgb = img.convert("RGB")
        width, height = rgb.size
        arr = np.asarray(rgb, dtype=np.uint8)

    planar = np.zeros((3, height, width), dtype=np.uint8)
    planar[0] = arr[:, :, 0]
    planar[1] = arr[:, :, 1]
    planar[2] = arr[:, :, 2]
    return planar, width, height


def write_planar_to_raw(planar, filepath, width, height, fmt):
    """Write planar numpy array (3, H, W) to raw file in specified format"""
    base = fmt & 0xF
    bpe = get_bytes_per_element(fmt)
    dtype = planar.dtype

    if base == 0x0:
        out = np.stack([planar[0], planar[1], planar[2]], axis=-1).ravel()
    elif base == 0x1:
        alpha = np.full((height, width), 255, dtype=dtype)
        out = np.stack([planar[0], planar[1], planar[2], alpha], axis=-1).ravel()
    elif base == 0x2:
        out = planar.ravel()
    elif base == 0x3:
        out = planar.ravel()
    elif base == 0x4:
        uv = np.stack([planar[1], planar[2]], axis=-1).ravel()
        out = np.concatenate([planar[0].ravel(), uv])
    elif base == 0x5:
        vuy = np.stack([planar[2], planar[1], planar[0]], axis=-1).ravel()
        out = vuy
    elif base == 0x6:
        y_out = planar[0].ravel()
        u_out = planar[1][:, 0::2].ravel()
        v_out = planar[2][:, 0::2].ravel()
        out = np.concatenate([y_out, u_out, v_out])
    elif base == 0x7:
        y_out = planar[0].ravel()
        uv_ch = np.stack([planar[1][:, 0::2], planar[2][:, 0::2]], axis=-1).ravel()
        out = np.concatenate([y_out, uv_ch])
    elif base == 0x8:
        y_out = planar[0].ravel()
        u_out = planar[1][0::2, 0::2].ravel()
        v_out = planar[2][0::2, 0::2].ravel()
        out = np.concatenate([y_out, u_out, v_out])
    elif base == 0x9:
        y_out = planar[0].ravel()
        uv_ch = np.stack([planar[1][0::2, 0::2], planar[2][0::2, 0::2]], axis=-1).ravel()
        out = np.concatenate([y_out, uv_ch])
    elif base == 0xA:
        out = planar[0].ravel()
    else:
        raise ValueError(f"Unsupported base format: 0x{base:X}")

    out.tofile(filepath)


def _get_dump_fmt(is_rgb_domain, pixel_depth):
    """Return a dump format code that matches the intermediate domain and bit depth."""
    if is_rgb_domain:
        return 0x12 if pixel_depth > 8 else 0x2
    return 0x13 if pixel_depth > 8 else 0x3


def _dump_step_planar(planar, step_name, is_rgb_domain, pixel_depth):
    """Dump one intermediate planar image to the debug dump directory."""
    os.makedirs(DEBUG_DUMP_PATH, exist_ok=True)
    height, width = planar.shape[1], planar.shape[2]
    dump_fmt = _get_dump_fmt(is_rgb_domain, pixel_depth)
    exten = "rgb" if is_rgb_domain else "yuv"
    dump_path = os.path.join(DEBUG_DUMP_PATH, f"{step_name}_{width}x{height}.{exten}")
    write_planar_to_raw(planar, dump_path, width, height, dump_fmt)
    print(f"Dumped file: {dump_path}")


def _get_step_output_domains(algo_type, input_is_rgb, output_is_rgb):
    """Return the output domains for step1 and step2."""
    if algo_type == ALGO_EVIDEO_CSC_PLAN_A:
        if not input_is_rgb and not output_is_rgb:
            return True, False
        if not input_is_rgb and output_is_rgb:
            return False, True
        if input_is_rgb and not output_is_rgb:
            return True, False
        return False, True

    if algo_type == ALGO_EVIDEO_CSC_PLAN_B:
        if not input_is_rgb and not output_is_rgb:
            return None, False
        if not input_is_rgb and output_is_rgb:
            return False, True
        if input_is_rgb and not output_is_rgb:
            return True, False
        return None, True

    return None, output_is_rgb


def apply_csc(planar_in, csc_coefs, csc_offset, coef_precision, pixel_depth):
    """Apply CSC transformation to planar image, return output planar (3, H, W)"""
    h, w = planar_in.shape[1], planar_in.shape[2]

    if coef_precision > 0:
        assert(csc_coefs.dtype == np.int32 and csc_offset.dtype == np.int32)
        pixels = planar_in.reshape(3, -1).astype(np.int32)
        out = csc_coefs @ pixels + csc_offset.reshape(3, 1)
        rnd = 1 << (coef_precision - 1)
        out = (out + rnd) >> coef_precision
    else:
        pixels = planar_in.reshape(3, -1).astype(np.float32)
        out = csc_coefs.astype(np.float32) @ pixels + csc_offset.reshape(3, 1).astype(np.float32)

    max_val = (1 << pixel_depth) - 1
    out = np.clip(out, 0, max_val).astype(planar_in.dtype)
    return out.reshape(3, h, w)


def build_csc_config(pixel_depth, coef_precision, algo_type, input_clrspc, output_clrspc):
    """Build a CSC config object for a single conversion step."""
    csc_config = CscCoefConfig()
    csc_config.pixel_depth = pixel_depth
    csc_config.coef_precision = coef_precision
    csc_config.algo_type = normalize_algo_type(algo_type)
    mode_str = build_csc_mode_str(input_clrspc, output_clrspc)
    csc_config.csc_mode = parse_csc_mode_str(mode_str)
    return csc_config


def is_rgb_on_hsv_algo_type(algo_type):
    """Check whether the algorithm is one of the RGB-on-HSV runtime modes."""
    return algo_type in {ALGO_EVIDEO_CSC_PLAN_B, ALGO_EVIDEO_CSC_PLAN_C}


def get_rgb_gain_default_value(algo_type):
    """Return the default raw RGB gain value for the selected algorithm."""
    evideo_algo_types = {ALGO_EVIDEO_CSC, ALGO_EVIDEO_CSC_PLAN_A, ALGO_EVIDEO_CSC_PLAN_B, ALGO_EVIDEO_CSC_PLAN_C}
    return 64 if algo_type in evideo_algo_types else 256


def get_default_bcsh_raw_values(algo_type):
    """Return default raw BCSH values for the selected algorithm."""
    rgb_gain_default = get_rgb_gain_default_value(algo_type)
    return {
        "hue": 256,
        "saturation": 256,
        "contrast": 256,
        "brightness": 256,
        "r_gain": rgb_gain_default,
        "g_gain": rgb_gain_default,
        "b_gain": rgb_gain_default,
        "r_offset": 256,
        "g_offset": 256,
        "b_offset": 256,
    }


def build_bcsh_config_from_dict(raw_values, algo_type=ALGO_RK_HW_CSC):
    """Build a BCSH config from raw values and algorithm-specific defaults."""
    bcsh = CscBcshConfig()
    for key, value in get_default_bcsh_raw_values(algo_type).items():
        setattr(bcsh, key, int(value))
    for key, value in raw_values.items():
        if value is not None:
            setattr(bcsh, key, int(value))
    return bcsh


def clone_bcsh_config(bcsh):
    """Create a shallow copy of a BCSH config object."""
    cloned = CscBcshConfig()
    for key in ("hue", "saturation", "contrast", "brightness", "r_gain", "g_gain", "b_gain", "r_offset", "g_offset", "b_offset"):
        setattr(cloned, key, int(getattr(bcsh, key)))
    return cloned


def clear_bcsh_rgb_gains(bcsh):
    """Return a BCSH config with RGB gains reset to the RK neutral value."""
    cleared = clone_bcsh_config(bcsh)
    cleared.r_gain = 256
    cleared.g_gain = 256
    cleared.b_gain = 256
    return cleared


def apply_rk_rgb_gain(planar_rgb, bcsh_cfg, pixel_depth, algo_type):
    """Apply RK-family RGB gain only in RGB space without applying RGB offsets."""
    h, w = planar_rgb.shape[1], planar_rgb.shape[2]
    max_val = (1 << pixel_depth) - 1
    rgb_normalized = planar_rgb.reshape(3, -1).T.astype(np.float32) / max_val
    algo_type = normalize_algo_type(algo_type)
    if algo_type not in {ALGO_RK_HW_CSC, ALGO_RK_SW_CSC}:
        raise ValueError(f"Algorithm '{algo_type}' is not an RK family mode")

    rgb_gains = np.array(
        [
            bcsh_cfg.r_gain / 256.0,
            bcsh_cfg.g_gain / 256.0,
            bcsh_cfg.b_gain / 256.0,
        ],
        dtype=np.float32,
    )

    rgb_new = rgb_normalized * rgb_gains
    rgb_new = np.clip(rgb_new, 0.0, 1.0)

    planar_out = (rgb_new.T * max_val)
    planar_out = np.clip(planar_out + 0.5, 0, max_val).astype(planar_rgb.dtype)
    return planar_out.reshape(3, h, w)


def get_runtime_coef_precision(algo_type, coef_precision):
    """Return the effective coefficient precision used at runtime."""
    if algo_type == ALGO_RK_SW_CSC:
        return 10
    return coef_precision


def convert_planar(planar_in, input_clrspc, output_clrspc, coef_precision, pixel_depth):
    """Convert planar data between two colorspaces using the matrix CSC path only."""
    csc_config = build_csc_config(pixel_depth, coef_precision, ALGO_RK_HW_CSC, input_clrspc, output_clrspc)
    coefs, offset = get_csc_coefs(csc_config, None)
    planar_out = apply_csc(planar_in, coefs, offset, coef_precision, pixel_depth)
    return planar_out, coefs, offset


def run_selected_algo(planar_in, bcsh, pixel_depth, coef_precision, algo_type, input_clrspc, output_clrspc, input_fmt, output_fmt, dump_enabled=False):
    """Run the selected CSC/BCSH algorithm and return output plus up to two CSC steps."""
    runtime_coef_precision = get_runtime_coef_precision(algo_type, coef_precision)
    csc_config = build_csc_config(pixel_depth, runtime_coef_precision, algo_type, input_clrspc, output_clrspc)
    input_is_rgb = is_rgb_format(input_fmt)
    output_is_rgb = is_rgb_format(output_fmt)
    step1_is_rgb, step2_is_rgb = _get_step_output_domains(algo_type, input_is_rgb, output_is_rgb)
    direct_csc_algos = {ALGO_RK_HW_CSC, ALGO_RK_SW_CSC, ALGO_EVIDEO_CSC}

    if algo_type in direct_csc_algos:
        planar_in_proc = planar_in
        bcsh_for_csc = bcsh
        step1_coefs = None
        step1_offset = None

        # SWPQ CSC R2Y case: pull RgbGain out as a separate step1 CSC to avoid color cast
        if algo_type == ALGO_RK_SW_CSC and input_is_rgb and not output_is_rgb:
            fix_factor = 1 << runtime_coef_precision
            step1_coefs = np.diag([
                bcsh.r_gain * (fix_factor // 256),
                bcsh.g_gain * (fix_factor // 256),
                bcsh.b_gain * (fix_factor // 256),
            ]).astype(np.int32)
            step1_offset = np.zeros(3, dtype=np.int32)
            planar_in_proc = apply_csc(planar_in, step1_coefs, step1_offset, runtime_coef_precision, pixel_depth)
            step1_is_rgb = True
            bcsh_for_csc = clear_bcsh_rgb_gains(bcsh)
            if dump_enabled:
                _dump_step_planar(planar_in_proc, "step1", True, pixel_depth)

        coefs, offset = get_csc_coefs(csc_config, bcsh_for_csc)
        planar_out = apply_csc(planar_in_proc, coefs, offset, runtime_coef_precision, pixel_depth)
        if dump_enabled:
            _dump_step_planar(planar_out, "step2", step2_is_rgb, pixel_depth)
        return planar_out, step1_coefs, step1_offset, coefs, offset

    base_config = build_csc_config(pixel_depth, 0, ALGO_RK_HW_CSC, input_clrspc, output_clrspc)
    base_mat, base_ofs = get_csc_coefs(base_config, None)

    if algo_type == ALGO_EVIDEO_CSC_PLAN_A:
        (step1_coefs, step1_offset), (step2_coefs, step2_offset) = get_evideo_plan_a_steps(
            csc_config, bcsh, base_mat, base_ofs
        )
        runtime_steps = get_evideo_plan_a_runtime_steps(csc_config, bcsh, base_mat, base_ofs)
        if not input_is_rgb and not output_is_rgb:
            # Y2Y 为 One-Step，仅 YUV 域
            runtime_domains = [False]
        elif not input_is_rgb and output_is_rgb:
            runtime_domains = [False, True]
        elif input_is_rgb and not output_is_rgb:
            runtime_domains = [True, False]
        else:
            # R2R：输入 RGB -> 输出 RGB（中间 YUV 已合成，无中间 clip）
            runtime_domains = [True, True]

        planar_out = planar_in
        for step_index, ((runtime_coefs, runtime_offset), is_rgb_domain) in enumerate(zip(runtime_steps, runtime_domains), start=1):
            planar_out = apply_csc(planar_out, runtime_coefs, runtime_offset, runtime_coef_precision, pixel_depth)
            if dump_enabled:
                _dump_step_planar(planar_out, f"step{step_index}", is_rgb_domain, pixel_depth)
        return planar_out, step1_coefs, step1_offset, step2_coefs, step2_offset

    if algo_type == ALGO_EVIDEO_CSC_PLAN_B:
        (step1_coefs, step1_offset), (step2_coefs, step2_offset) = get_evideo_plan_b_steps(
            csc_config, bcsh, base_mat, base_ofs
        )
        planar_mid = planar_in
        if step1_coefs is not None:
            planar_mid = apply_csc(planar_in, step1_coefs, step1_offset, runtime_coef_precision, pixel_depth)
            if dump_enabled:
                _dump_step_planar(planar_mid, "step1", step1_is_rgb, pixel_depth)
        planar_out = apply_csc(planar_mid, step2_coefs, step2_offset, runtime_coef_precision, pixel_depth)
        if dump_enabled:
            _dump_step_planar(planar_out, "step2", step2_is_rgb, pixel_depth)
        return planar_out, step1_coefs, step1_offset, step2_coefs, step2_offset

    if algo_type == ALGO_EVIDEO_CSC_PLAN_C:
        # Plan C：输入统一转到 RGB，再进入 HSV 域调色，调色完成后转回输出色域。
        # 调色路径为非线性的 HSV 域操作（apply_bcsh_hsv），不使用矩阵固定点量化。
        if input_is_rgb:
            rgb_planar = planar_in
        else:
            rgb_planar, _, _ = convert_planar(planar_in, input_clrspc, 1, 0, pixel_depth)
            if dump_enabled:
                _dump_step_planar(rgb_planar, "step1_y2r", True, pixel_depth)
        rgb_planar = apply_bcsh_hsv(rgb_planar, bcsh, pixel_depth, algo_type)
        if dump_enabled:
            _dump_step_planar(rgb_planar, "step2_hsv", True, pixel_depth)
        if output_is_rgb:
            planar_out = rgb_planar
        else:
            planar_out, _, _ = convert_planar(rgb_planar, 1, output_clrspc, 0, pixel_depth)
            if dump_enabled:
                _dump_step_planar(planar_out, "step3_r2y", False, pixel_depth)
        return planar_out, None, None, None, None

    raise ValueError(f"Unsupported algorithm type: {algo_type}")


def _get_default_output_path(input_path):
    """Generate default output path: dirname(input)/custom_output_basename"""
    dirname = os.path.dirname(input_path)
    basename = os.path.splitext(os.path.basename(input_path))[0]
    if not dirname:
        dirname = "."
    return os.path.join(dirname, f"{basename}_csc_output.raw")


def run_cli(args):
    """Run CSC conversion in command-line mode"""
    if not args.input:
        print("Error: input file (-i/--input) is required in CLI mode")
        sys.exit(-1)

    input_file = args.input
    width = args.width
    height = args.height
    input_fmt = args.format
    input_clrspc = args.clrspc
    output_fmt = args.outfmt
    output_clrspc = args.outclr
    coef_precision = args.precision
    pixel_depth = args.depth

    if output_fmt is None:
        output_fmt = (input_fmt & 0xF) + 0x10
    if output_clrspc is None:
        output_clrspc = input_clrspc

    output_file = args.output
    if output_file is None:
        output_file = _get_default_output_path(input_file)

    if not os.path.isfile(input_file):
        print(f"Error: input file not found: {input_file}")
        sys.exit(-1)

    print(f"Input:  {input_file} ({FORMAT_NAMES.get(input_fmt, f'0x{input_fmt:X}')}, "
          f"{CLRSPC_NAMES.get(input_clrspc, str(input_clrspc))}, {width}x{height})")
    print(f"Output: {output_file} ({FORMAT_NAMES.get(output_fmt, f'0x{output_fmt:X}')}, "
          f"{CLRSPC_NAMES.get(output_clrspc, str(output_clrspc))}, {width}x{height})")
    print(f"CSC config: precision={coef_precision}, depth={pixel_depth}")

    mode_str = build_csc_mode_str(input_clrspc, output_clrspc)
    print(f"CSC mode: {mode_str}")

    planar_in, input_fmt = read_raw_to_planar(input_file, width, height, input_fmt)

    csc_config = CscCoefConfig()
    csc_config.csc_mode = parse_csc_mode_str(mode_str)
    csc_config.pixel_depth = pixel_depth
    csc_config.coef_precision = coef_precision
    csc_config.platform = "rk3576"
    csc_config.algo_type = args.algo_type

    bcsh = build_bcsh_config_from_dict(
        {
            "hue": args.hue,
            "saturation": args.saturation,
            "contrast": args.contrast,
            "brightness": args.brightness,
            "r_gain": args.r_gain,
            "g_gain": args.g_gain,
            "b_gain": args.b_gain,
            "r_offset": args.r_offset,
            "g_offset": args.g_offset,
            "b_offset": args.b_offset,
        },
        args.algo_type,
    )

    planar_out, step1_coefs, step1_offset, step2_coefs, step2_offset = run_selected_algo(
        planar_in, bcsh, pixel_depth, coef_precision, args.algo_type, input_clrspc, output_clrspc, input_fmt, output_fmt, args.dump
    )

    print(f"Step1 CSC matrix:\n{step1_coefs}")
    print(f"Step1 CSC offset: {step1_offset}")
    print(f"Step2 CSC matrix:\n{step2_coefs}")
    print(f"Step2 CSC offset: {step2_offset}")
    write_planar_to_raw(planar_out, output_file, width, height, output_fmt)
    print(f"Conversion done, output written to: {output_file}")


def run_point(args):
    """Run CSC conversion for a single pixel point, output to console."""
    if args.rgb is not None:
        input_is_rgb = True
        input_vals = args.rgb
        input_clrspc = args.clrspc if args.clrspc else 1
        domain_label = "RGB"
    else:
        input_is_rgb = False
        input_vals = args.yuv
        input_clrspc = args.clrspc if args.clrspc else 5
        domain_label = "YUV"

    if len(input_vals) != 3:
        print("Error: --rgb/--yuv requires exactly 3 values")
        sys.exit(-1)

    pixel_depth = args.depth
    coef_precision = args.precision
    output_clrspc = args.outclr if args.outclr else input_clrspc

    if pixel_depth > 8:
        input_fmt = 0x12 if input_is_rgb else 0x13
    else:
        input_fmt = 0x0 if input_is_rgb else 0x3

    output_is_rgb = True if output_clrspc <= 1 else False
    if pixel_depth > 8:
        output_fmt = 0x12 if output_is_rgb else 0x13
    else:
        output_fmt = 0x0 if output_is_rgb else 0x3

    max_val = (1 << pixel_depth) - 1
    planar_in = np.zeros((3, 1, 1), dtype=np.uint16 if pixel_depth > 8 else np.uint8)
    for i in range(3):
        planar_in[i, 0, 0] = int(np.clip(input_vals[i], 0, max_val))

    bcsh = build_bcsh_config_from_dict(
        {
            "hue": args.hue,
            "saturation": args.saturation,
            "contrast": args.contrast,
            "brightness": args.brightness,
            "r_gain": args.r_gain,
            "g_gain": args.g_gain,
            "b_gain": args.b_gain,
            "r_offset": args.r_offset,
            "g_offset": args.g_offset,
            "b_offset": args.b_offset,
        },
        args.algo_type,
    )

    planar_out, step1_coefs, step1_offset, step2_coefs, step2_offset = run_selected_algo(
        planar_in, bcsh, pixel_depth, coef_precision, args.algo_type,
        input_clrspc, output_clrspc, input_fmt, output_fmt
    )

    out_vals = [int(planar_out[i, 0, 0]) for i in range(3)]

    print(f"Input  ({domain_label}): ({input_vals[0]:3d}, {input_vals[1]:3d}, {input_vals[2]:3d}) {CLRSPC_NAMES.get(input_clrspc, str(input_clrspc))}")
    output_domain_label = "RGB" if output_is_rgb else "YUV"
    print(f"Output ({output_domain_label}): ({out_vals[0]:3d}, {out_vals[1]:3d}, {out_vals[2]:3d}) {CLRSPC_NAMES.get(output_clrspc, str(output_clrspc))}")
    print("\n===========================")
    print(f"CSC mode: {build_csc_mode_str(input_clrspc, output_clrspc)}, depth: {pixel_depth}, precision: {coef_precision}")
    if step1_coefs is not None:
        print(f"Pre step CSC matrix:\n{step1_coefs} \noffset: {step1_offset}")
    print(f"Post step CSC matrix:\n{step2_coefs} \noffset: {step2_offset.T}")


def main():
    parser = argparse.ArgumentParser(description="CSC image conversion tool, three modes: --ui / -i/-o / --rgb/--yuv")
    parser.add_argument("--ui", action="store_true", help="open UI interface for interactive CSC conversion")

    parser.add_argument("-i", "--input", type=str, default=None, help="input filename")
    parser.add_argument("-w", "--width", type=int, default=1920, help="input image width, default: 1920")
    parser.add_argument("-g", "--height", type=int, default=1080, help="input image height, default: 1080")
    parser.add_argument("-f", "--format", type=lambda x: int(x, 0), default=0x0,
                        help="input image format, default: 0x0, support: "
                             "rgb(0)[a(1)|planar(2)]; "
                             "yuv[444p(3)|444sp(4)|444i(5)|422p(6)|422sp(7)|420p(8)|420sp(9)|400(a)]"
                             "(+0x10 for 10bit unpacked(LSB); +0x20 for 10bit packed)")
    parser.add_argument("-r", "--clrspc", type=int, default=None,
                        help="input image colorspace, default: 1-RGBF/5-709F, "
                             "support: {0/1(RGBL/F), 2/3(601L/F), 4/5(709L/F), 6/7(2020L/F)}")
    parser.add_argument("-o", "--output", type=str, default=None,
                        help="output filename, default: 'dirname(input)/custom_output_basename'")
    parser.add_argument("-F", "--outfmt", type=lambda x: int(x, 0), default=None,
                        help="output image format, default: mod('format',16)+0x10")
    parser.add_argument("-R", "--outclr", type=int, default=None,
                        help="output image colorspace, default: same to 'clrspc'")
    parser.add_argument("-P", "--precision", type=int, default=10,
                        help="the fixed coef precision bits 0 or [8, 16]")
    parser.add_argument("-D", "--depth", type=int, default=10,
                        help="the pixel depth bits [8, 16]")
    parser.add_argument("--dump", action="store_true",
                        help=f"dump step1/step2 apply_csc results to '{DEBUG_DUMP_PATH}'")

    parser.add_argument("--rgb", type=int, nargs=3, default=None, metavar=("R", "G", "B"),
                        help="input RGB pixel values (3 numbers)")
    parser.add_argument("--yuv", type=int, nargs=3, default=None, metavar=("Y", "U", "V"),
                        help="input YUV pixel values (3 numbers)")

    parser.add_argument("--hue", type=int, default=None, help="BCSH hue [0, 511], default: 256")
    parser.add_argument("--saturation", type=int, default=None, help="BCSH saturation [0, 511], default: 256")
    parser.add_argument("--contrast", type=int, default=None, help="BCSH contrast [0, 511], default: 256")
    parser.add_argument("--brightness", type=int, default=None, help="BCSH brightness [0, 511], default: 256")
    parser.add_argument("--r_gain", type=int, default=None, help="BCSH R gain [0, 511], default: 256")
    parser.add_argument("--g_gain", type=int, default=None, help="BCSH G gain [0, 511], default: 256")
    parser.add_argument("--b_gain", type=int, default=None, help="BCSH B gain [0, 511], default: 256")
    parser.add_argument("--r_offset", type=int, default=None, help="BCSH R offset [0, 511], default: 256")
    parser.add_argument("--g_offset", type=int, default=None, help="BCSH G offset [0, 511], default: 256")
    parser.add_argument("--b_offset", type=int, default=None, help="BCSH B offset [0, 511], default: 256")
    parser.add_argument("-t", "--algo-type", type=str, default=ALGO_RK_HW_CSC,
                        help=f"BCSH algorithm type: '{ALGO_RK_HW_CSC}', '{ALGO_RK_SW_CSC}', "
                             f"'{ALGO_EVIDEO_CSC}', '{ALGO_EVIDEO_CSC_PLAN_A}', "
                             f"'{ALGO_EVIDEO_CSC_PLAN_B}', '{ALGO_EVIDEO_CSC_PLAN_C}'")

    args, _ = parser.parse_known_args()

    if args.depth not in [8, 10]:
        print(f"Error: pixel_depth({args.depth}) should be 8 or 10!")
        sys.exit(-1)
    if args.precision not in range(8, 17) and args.precision != 0:
        print(f"Error: coef_precision({args.precision}) should be 0 or [8, 16]!")
        sys.exit(-1)

    if args.ui:
        from csc_ui import open_csc_ui
        open_csc_ui(args)
    elif args.rgb is not None or args.yuv is not None:
        run_point(args)
    else:
        run_cli(args)


if __name__ == "__main__":
    main()
