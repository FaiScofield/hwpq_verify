"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : get_csc_coefs.py
Author      : vance.wu@rock-chips.com
Date        : 2025-08-27
Description :
LastEditTime: 2025-09-11
"""

import argparse
import numpy as np
from enum import Enum
from typing import Optional

# from utils import enum_with_index


# @enum_with_index
class ColorSpace(Enum):
    BT601 = 0
    BT709 = 1
    BT2020 = 2

    @classmethod
    def from_index(cls, index: int):
        members = list(cls)
        if 0 <= index < len(members):
            return members[index]
        raise ValueError(f"Index {index} out of range (0-{len(members)-1})")


class CscMode:
    def __init__(self, color_i=1, color_o=1, is_yuv_i=0, is_yuv_o=1, is_full_i=1, is_full_o=1):
        self.input_color_encoding = color_i
        self.output_color_encoding = color_o
        self.is_input_yuv = is_yuv_i
        self.is_output_yuv = is_yuv_o
        self.is_input_full_range = is_full_i
        self.is_output_full_range = is_full_o


class CscCoefConfig:
    csc_mode = CscMode()
    pixel_depth = 10
    coef_precision = 0
    tune_fix_coefs = 0  # 0-no tuning, >0 means a diagonal ratio (float), no need to set this value
    platform = "rk3572"
    algo_type = "RK HW CSC"  # "RK HW CSC", "RK SW CSC"


class CscBcshConfig:
    hue = 256  # range: [0, 511], default: 256
    saturation = 256  # range: [0, 511], default: 256
    contrast = 256  # range: [0, 511], default: 256
    brightness = 256  # range: [0, 511], default: 256
    r_gain = 256  # range: [0, 511], default: 256
    g_gain = 256  # range: [0, 511], default: 256
    b_gain = 256  # range: [0, 511], default: 256
    r_offset = 256  # range: [0, 511], default: 256
    g_offset = 256  # range: [0, 511], default: 256
    b_offset = 256  # range: [0, 511], default: 256


## matrixs from Rec ITU-R BT.601-7 / BT.709-6 / BT.2020-2
g_identity_mat = np.eye(3, dtype=np.float32)
g_r2y_mat_bt601 = np.array(
    [[0.299, 0.587, 0.114], [-0.168736, -0.331264, 0.5], [0.5, -0.418688, -0.081312]], dtype=np.float32
)
g_y2r_mat_bt601 = np.array([[1, 0, 1.402], [1, -0.344136, -0.714136], [1, 1.772, 0]], dtype=np.float32)
g_r2y_mat_bt709 = np.array(
    [[0.2126, 0.7152, 0.0722], [-0.114572, -0.385428, 0.5], [0.5, -0.454153, -0.045847]], dtype=np.float32
)
g_y2r_mat_bt709 = np.array([[1, 0, 1.5748], [1, -0.187324, -0.468124], [1, 1.8556, 0]], dtype=np.float32)
g_r2y_mat_bt2020 = np.array(
    [[0.2627, 0.678, 0.0593], [-0.13963, -0.36037, 0.5], [0.5, -0.459786, -0.040214]], dtype=np.float32
)
g_y2r_mat_bt2020 = np.array([[1, 0, 1.4746], [1, -0.164553, -0.571353], [1, 1.8814, 0]], dtype=np.float32)

g_supported_standard_convert_modes = {
    "rgbl_to_rgbf": CscMode(ColorSpace.BT709, ColorSpace.BT709, 0, 0, 0, 1),
    "rgbl_to_601l": CscMode(ColorSpace.BT601, ColorSpace.BT601, 0, 1, 0, 0),
    "rgbl_to_601f": CscMode(ColorSpace.BT601, ColorSpace.BT601, 0, 1, 0, 1),
    "rgbl_to_709l": CscMode(ColorSpace.BT709, ColorSpace.BT709, 0, 1, 0, 0),
    "rgbl_to_709f": CscMode(ColorSpace.BT709, ColorSpace.BT709, 0, 1, 0, 1),
    "rgbl_to_2020l": CscMode(ColorSpace.BT2020, ColorSpace.BT2020, 0, 1, 0, 0),
    "rgbl_to_2020f": CscMode(ColorSpace.BT2020, ColorSpace.BT2020, 0, 1, 0, 1),
    "rgbf_to_rgbl": CscMode(ColorSpace.BT709, ColorSpace.BT709, 0, 0, 1, 0),
    "rgbf_to_601l": CscMode(ColorSpace.BT601, ColorSpace.BT601, 0, 1, 1, 0),
    "rgbf_to_601f": CscMode(ColorSpace.BT601, ColorSpace.BT601, 0, 1, 1, 1),
    "rgbf_to_709l": CscMode(ColorSpace.BT709, ColorSpace.BT709, 0, 1, 1, 0),
    "rgbf_to_709f": CscMode(ColorSpace.BT709, ColorSpace.BT709, 0, 1, 1, 1),
    "rgbf_to_2020l": CscMode(ColorSpace.BT2020, ColorSpace.BT2020, 0, 1, 1, 0),
    "rgbf_to_2020f": CscMode(ColorSpace.BT2020, ColorSpace.BT2020, 0, 1, 1, 1),
    "601l_to_rgbl": CscMode(ColorSpace.BT601, ColorSpace.BT601, 1, 0, 0, 0),
    "601l_to_rgbf": CscMode(ColorSpace.BT601, ColorSpace.BT601, 1, 0, 0, 1),
    "601l_to_601f": CscMode(ColorSpace.BT601, ColorSpace.BT601, 1, 1, 0, 1),
    "601l_to_709l": CscMode(ColorSpace.BT601, ColorSpace.BT709, 1, 1, 0, 0),
    "601l_to_709f": CscMode(ColorSpace.BT601, ColorSpace.BT709, 1, 1, 0, 1),
    "601f_to_rgbl": CscMode(ColorSpace.BT601, ColorSpace.BT601, 1, 0, 1, 0),
    "601f_to_rgbf": CscMode(ColorSpace.BT601, ColorSpace.BT601, 1, 0, 1, 1),
    "601f_to_601l": CscMode(ColorSpace.BT601, ColorSpace.BT601, 1, 1, 1, 0),
    "601f_to_709l": CscMode(ColorSpace.BT601, ColorSpace.BT709, 1, 1, 1, 0),
    "601f_to_709f": CscMode(ColorSpace.BT601, ColorSpace.BT709, 1, 1, 1, 1),
    "709l_to_rgbl": CscMode(ColorSpace.BT709, ColorSpace.BT709, 1, 0, 0, 0),
    "709l_to_rgbf": CscMode(ColorSpace.BT709, ColorSpace.BT709, 1, 0, 0, 1),
    "709l_to_601l": CscMode(ColorSpace.BT709, ColorSpace.BT601, 1, 1, 0, 0),
    "709l_to_601f": CscMode(ColorSpace.BT709, ColorSpace.BT601, 1, 1, 0, 1),
    "709l_to_709f": CscMode(ColorSpace.BT709, ColorSpace.BT709, 1, 1, 0, 1),
    "709f_to_rgbl": CscMode(ColorSpace.BT709, ColorSpace.BT709, 1, 0, 1, 0),
    "709f_to_rgbf": CscMode(ColorSpace.BT709, ColorSpace.BT709, 1, 0, 1, 1),
    "709f_to_601l": CscMode(ColorSpace.BT709, ColorSpace.BT601, 1, 1, 1, 0),
    "709f_to_601f": CscMode(ColorSpace.BT709, ColorSpace.BT601, 1, 1, 1, 1),
    "709f_to_709l": CscMode(ColorSpace.BT709, ColorSpace.BT709, 1, 1, 1, 0),
    "2020l_to_rgbl": CscMode(ColorSpace.BT2020, ColorSpace.BT2020, 1, 0, 0, 0),
    "2020l_to_rgbf": CscMode(ColorSpace.BT2020, ColorSpace.BT2020, 1, 0, 0, 1),
    "2020l_to_2020f": CscMode(ColorSpace.BT2020, ColorSpace.BT2020, 1, 1, 0, 1),
    "2020f_to_rgbl": CscMode(ColorSpace.BT2020, ColorSpace.BT2020, 1, 0, 1, 0),
    "2020f_to_rgbf": CscMode(ColorSpace.BT2020, ColorSpace.BT2020, 1, 0, 1, 1),
    "2020f_to_2020l": CscMode(ColorSpace.BT2020, ColorSpace.BT2020, 1, 1, 1, 0),
    "identity_mode": CscMode(ColorSpace.BT709, ColorSpace.BT709, 0, 0, 1, 1),
}


def get_range_convert_mat(mode: CscMode, pixel_depth: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    range_mat_i = np.eye(3, dtype=np.float32)
    range_mat_o = np.eye(3, dtype=np.float32)
    offset_vec_i = np.zeros(3, dtype=np.float32)
    offset_vec_o = np.zeros(3, dtype=np.float32)

    ratio_gain = 1 << (pixel_depth - 8)
    ratio_denorm = (1 << pixel_depth) - 1

    ## get matrix and vector for input
    ratio_y = 1.0
    ratio_c = 1.0
    offset_y = 0 if mode.is_input_full_range else 16
    offset_c = 128 if mode.is_input_yuv else offset_y
    if not mode.is_input_full_range:
        ratio_y = (235 - 16) * ratio_gain / ratio_denorm
        ratio_c = (240 - 16) * ratio_gain / ratio_denorm if mode.is_input_yuv else ratio_y
        ratio_y = 1.0 / ratio_y
        ratio_c = 1.0 / ratio_c

    range_mat_i[0, 0] = ratio_y
    range_mat_i[1, 1] = ratio_c
    range_mat_i[2, 2] = range_mat_i[1, 1]
    offset_vec_i[0] = -offset_y * ratio_gain
    offset_vec_i[1] = -offset_c * ratio_gain
    offset_vec_i[2] = -offset_c * ratio_gain

    ## get matrix and vector for output
    ratio_y = 1
    ratio_c = 1
    offset_y = 0 if mode.is_output_full_range else 16
    offset_c = 128 if mode.is_output_yuv else offset_y
    if not mode.is_output_full_range:
        ratio_y = (235 - 16) * ratio_gain / ratio_denorm
        ratio_c = (240 - 16) * ratio_gain / ratio_denorm if mode.is_output_yuv else ratio_y
    range_mat_o[0, 0] = ratio_y
    range_mat_o[1, 1] = ratio_c
    range_mat_o[2, 2] = range_mat_o[1, 1]
    offset_vec_o[0] = offset_y * ratio_gain
    offset_vec_o[1] = offset_c * ratio_gain
    offset_vec_o[2] = offset_c * ratio_gain
    return range_mat_i, range_mat_o, offset_vec_i, offset_vec_o


def get_space_convert_mat(mode: CscMode) -> Optional[np.ndarray]:
    ## R2R case
    if mode.is_input_yuv == 0 and mode.is_output_yuv == 0:
        return g_identity_mat

    ## R2Y case
    if mode.is_input_yuv == 0 and mode.is_output_yuv == 1:
        if mode.output_color_encoding == ColorSpace.BT601:
            return g_r2y_mat_bt601
        if mode.output_color_encoding == ColorSpace.BT2020:
            return g_r2y_mat_bt2020
        return g_r2y_mat_bt709

    ## Y2R case
    if mode.is_input_yuv == 1 and mode.is_output_yuv == 0:
        if mode.input_color_encoding == ColorSpace.BT601:
            return g_y2r_mat_bt601
        if mode.input_color_encoding == ColorSpace.BT2020:
            return g_y2r_mat_bt2020
        return g_y2r_mat_bt709

    ## Y2Y case with same colorspace
    if mode.input_color_encoding == mode.output_color_encoding:
        return g_identity_mat

    ## Y2Y case with different colorspace
    if (
        mode.input_color_encoding in [ColorSpace.BT601, ColorSpace.BT709]
        and mode.output_color_encoding == ColorSpace.BT2020
    ):
        return None
    if (
        mode.output_color_encoding in [ColorSpace.BT601, ColorSpace.BT709]
        and mode.input_color_encoding == ColorSpace.BT2020
    ):
        return None
    if mode.input_color_encoding == ColorSpace.BT601:
        mat_y2r = g_y2r_mat_bt601
    elif mode.input_color_encoding == ColorSpace.BT2020:
        mat_y2r = g_r2y_mat_bt2020
    else:
        mat_y2r = g_y2r_mat_bt709
    if mode.output_color_encoding == ColorSpace.BT601:
        mat_r2y = g_r2y_mat_bt601
    elif mode.output_color_encoding == ColorSpace.BT2020:
        mat_r2y = g_r2y_mat_bt2020
    else:
        mat_r2y = g_r2y_mat_bt709
    return mat_r2y @ mat_y2r


def adjust_convert_mat(
    config: CscCoefConfig, bcsh_cfg: CscBcshConfig, out_mat: np.ndarray, out_vec: np.ndarray
) -> tuple[np.ndarray, np.ndarray, float]:
    ## get BCSH parameters
    contrast = bcsh_cfg.contrast / 256.0  # [0, 511] -> [0, 2)
    saturation = bcsh_cfg.saturation / 256.0  # [0, 511] -> [0, 2)
    r_gain = bcsh_cfg.r_gain / 256.0  # [0, 511] -> [0, 2)
    g_gain = bcsh_cfg.g_gain / 256.0  # [0, 511] -> [0, 2)
    b_gain = bcsh_cfg.b_gain / 256.0  # [0, 511] -> [0, 2)
    hue_rad = (bcsh_cfg.hue - 256) * 30 / 256.0 * np.pi / 180.0  # [0, 511] -> [-pi/6, pi/6]
    cos_hue = np.cos(hue_rad)
    sin_hue = np.sin(hue_rad)
    r_offset = bcsh_cfg.r_offset - 256
    g_offset = bcsh_cfg.g_offset - 256
    b_offset = bcsh_cfg.b_offset - 256
    brightness = bcsh_cfg.brightness - 256
    offset_shift_bits = 3 - (config.pixel_depth - 8)
    if offset_shift_bits >= 0:
        r_offset >>= offset_shift_bits
        g_offset >>= offset_shift_bits
        b_offset >>= offset_shift_bits
    else:
        r_offset <<= -offset_shift_bits
        g_offset <<= -offset_shift_bits
        b_offset <<= -offset_shift_bits
    if config.pixel_depth <= 10:
        brightness >>= 10 - config.pixel_depth
    else:
        brightness <<= config.pixel_depth - 10

    gain_matrix = np.array([[r_gain, 0, 0], [0, g_gain, 0], [0, 0, b_gain]], dtype=np.float32)
    contrast_matrix = np.array([[contrast, 0, 0], [0, contrast, 0], [0, 0, contrast]], dtype=np.float32)
    hue_matrix = np.array([[1, 0, 0], [0, cos_hue, -sin_hue], [0, sin_hue, cos_hue]], dtype=np.float32)
    saturation_matrix = np.array([[1, 0, 0], [0, saturation, 0], [0, 0, saturation]], dtype=np.float32)
    b_diagonal_m0 = hue_rad == 0 and saturation == 1
    b_diagonal_m1 = r_gain == g_gain and g_gain == b_gain
    m_yuv = hue_matrix @ saturation_matrix
    m_rgb = gain_matrix @ contrast_matrix
    mode = config.csc_mode

    ## Y2Y: output = T * M0 * N_r2y * M1 * N_y2r
    if mode.is_input_yuv and mode.is_output_yuv:
        out_mat = out_mat @ m_yuv @ g_r2y_mat_bt709 @ m_rgb @ g_y2r_mat_bt709
        out_vec[0] += brightness
    ## Y2R: output = M1 * T * M0
    elif mode.is_input_yuv and not mode.is_output_yuv:
        out_mat = m_rgb @ out_mat @ m_yuv
        out_vec[0] += brightness + r_offset
        out_vec[1] += brightness + g_offset
        out_vec[2] += brightness + b_offset
    ## R2Y: output = M0 * T * M1
    elif not mode.is_input_yuv and mode.is_output_yuv:
        out_mat = m_yuv @ out_mat @ m_rgb
        out_vec[0] += brightness
    ## R2R: output = T * M1 * N_y2r * M0 * N_r2y
    else:
        out_mat = out_mat @ m_rgb @ g_y2r_mat_bt709 @ m_yuv @ g_r2y_mat_bt709
        out_vec[0] += brightness + r_offset
        out_vec[1] += brightness + g_offset
        out_vec[2] += brightness + b_offset

    ## count diagonal ratio for later fixed-point calcuation
    if b_diagonal_m0 and b_diagonal_m1:
        diagonal_ratio = r_gain * contrast * saturation
    else:
        diagonal_ratio = 0.0

    return out_mat, out_vec, diagonal_ratio


def _compose_transforms(*transforms):
    """
    Compose a sequence of (mat, ofs) transforms where the first tuple is applied first to the pixel.
    Each transform is a tuple (mat3x3, ofs3x1).
    """
    mat = np.eye(3, dtype=np.float32)
    ofs = np.zeros(3, dtype=np.float32)
    for t_mat, t_ofs in transforms:
        ofs = t_mat @ ofs + t_ofs
        mat = t_mat @ mat
    return mat, ofs


def adjust_convert_mat_evideo(config, bcsh_cfg, out_mat, out_vec):
    """
    Adjust the non-homogeneous CSC matrix with eVideo BCSH parameters.
    Uses the same direct matrix-manipulation approach as adjust_convert_mat,
    but with eVideo parameter mapping ranges.
    """
    from get_csc_coef_hsv import get_evideo_bcsh_param_pack

    params = get_evideo_bcsh_param_pack(config.algo_type, bcsh_cfg, config.pixel_depth)
    contrast = params["contrast"]
    saturation = params["saturation"]
    hue_rad = params["hue_rad"]
    cos_hue = np.cos(hue_rad)
    sin_hue = np.sin(hue_rad)
    rgb_gains = params["rgb_gains"]
    rgb_offsets = params["rgb_offset_pixels"]
    brightness = params["brightness_pixel"]
    brightness_unit = params["brightness_unit"]
    mid_pixel_val = params["mid_pixel_val"]

    zero3 = np.zeros(3, dtype=np.float32)
    ident = np.eye(3, dtype=np.float32)

    # Build BCSH matrices matching the quad version
    gain_matrix = np.diag(rgb_gains).astype(np.float32)
    contrast_matrix = np.diag([contrast, contrast, contrast]).astype(np.float32)
    hue_matrix = np.array([[1, 0, 0], [0, cos_hue, -sin_hue], [0, sin_hue, cos_hue]], dtype=np.float32)
    saturation_matrix = np.array([[1, 0, 0], [0, saturation, 0], [0, 0, saturation]], dtype=np.float32)
    chroma_center_raw = np.array([0.0, mid_pixel_val, mid_pixel_val], dtype=np.float32)

    # Build transform tuples matching the homogeneous quad versions
    tf_contrast = (contrast_matrix, zero3)  # legacy eVideo contrast: no center
    tf_rgbGains = (gain_matrix, zero3)
    tf_rgbOffsets = (ident, rgb_offsets)
    tf_bright_yuv = (ident, np.array([brightness, 0.0, 0.0], dtype=np.float32))
    tf_bright_rgb = (ident, np.full(3, brightness_unit, dtype=np.float32))

    # Center-scaled around chroma_center_raw (unsigned YUV)
    sat_raw_ofs = chroma_center_raw - saturation_matrix @ chroma_center_raw
    hue_raw_ofs = chroma_center_raw - hue_matrix @ chroma_center_raw
    tf_sat_raw = (saturation_matrix, sat_raw_ofs)
    tf_hue_raw = (hue_matrix, hue_raw_ofs)

    # Signed (center at [0, 0, 0], no offset needed)
    tf_sat_signed = (saturation_matrix, zero3)
    tf_hue_signed = (hue_matrix, zero3)

    tf_r2y = (g_r2y_mat_bt709, zero3)
    tf_y2r = (g_y2r_mat_bt709, zero3)

    base_tf = (out_mat, out_vec)

    mode = config.csc_mode

    if mode.is_input_yuv and mode.is_output_yuv:
        # Y2Y: bright_yuv @ base @ hue_raw @ sat_raw @ r2y @ rgbGains @ contrast @ y2r
        final_mat, final_ofs = _compose_transforms(
            tf_y2r, tf_contrast, tf_rgbGains, tf_r2y, tf_sat_raw, tf_hue_raw, base_tf, tf_bright_yuv
        )
    elif mode.is_input_yuv and not mode.is_output_yuv:
        # Y2R: bright_rgb @ rgbOffsets @ rgbGains @ contrast @ base @ hue_raw @ sat_raw
        final_mat, final_ofs = _compose_transforms(
            tf_sat_raw, tf_hue_raw, base_tf, tf_contrast, tf_rgbGains, tf_rgbOffsets, tf_bright_rgb
        )
    elif not mode.is_input_yuv and mode.is_output_yuv:
        # R2Y: bright_yuv @ hue_raw @ sat_raw @ base @ rgbGains @ contrast
        final_mat, final_ofs = _compose_transforms(
            tf_contrast, tf_rgbGains, base_tf, tf_sat_raw, tf_hue_raw, tf_bright_yuv
        )
    else:
        # R2R: bright_rgb @ rgbOffsets @ base @ rgbGains @ contrast @ y2r @ hue_signed @ sat_signed @ r2y
        final_mat, final_ofs = _compose_transforms(
            tf_r2y, tf_sat_signed, tf_hue_signed, tf_y2r, tf_contrast, tf_rgbGains,
            base_tf, tf_rgbOffsets, tf_bright_rgb
        )

    # Compute diagonal ratio for later fixed-point fine-tuning
    b_diagonal_m0 = hue_rad == 0.0 and saturation == 1.0
    b_diagonal_m1 = abs(rgb_gains[0] - rgb_gains[1]) < 1e-6 and abs(rgb_gains[1] - rgb_gains[2]) < 1e-6
    if b_diagonal_m0 and b_diagonal_m1:
        diagonal_ratio = rgb_gains[0] * contrast * saturation
    else:
        diagonal_ratio = 0.0

    return final_mat, final_ofs, diagonal_ratio


def get_fixed_coefs_mat(
    config: CscCoefConfig, float_mat: np.ndarray, range_ofs_i: np.ndarray, range_ofs_o: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    pixel_depth = config.pixel_depth
    fix_factor = 2**config.coef_precision
    max_pixel_val = 2**pixel_depth - 1
    float_mat *= fix_factor
    fix_mat = (float_mat + np.sign(float_mat) * 0.5).astype(np.int32)

    ## fine-tuning for fixed matrix (only R2Y & Y2R case)
    if config.tune_fix_coefs > 0:
        mode = config.csc_mode
        ratio_y = (219 << (pixel_depth - 8)) / max_pixel_val
        target_denorms = np.zeros(3, dtype=np.int32)
        if mode.is_input_full_range and not mode.is_output_full_range:  # F2L
            target_denorms[0] = np.int32(fix_factor * ratio_y * config.tune_fix_coefs + 0.5)
        elif not mode.is_input_full_range and mode.is_output_full_range:  # L2F
            target_denorms[0] = np.int32(fix_factor / ratio_y * config.tune_fix_coefs + 0.5)
        else:
            target_denorms[0] = np.int32(fix_factor * config.tune_fix_coefs + 0.5)

        org_fix_mat = fix_mat.copy()
        if not mode.is_input_yuv and mode.is_output_yuv:  # R2Y
            target_denorms[1] = target_denorms[2] = 0
            denorms = np.sum(fix_mat, axis=1)

            for i in range(3):
                if denorms[i] != target_denorms[i]:
                    # fix_mat = solveLSE4Luma(fix_mat[i, :], mat_flt[i, :], target_denorms[i] - denorms[i])
                    delta = target_denorms[i] - denorms[i]
                    j = np.argmin(np.abs(fix_mat[i, :] + delta - float_mat[i, :]))
                    fix_mat[i, j] += delta
                    print(
                        f"NOTE: denorms[{i}] = {denorms[i]} != {target_denorms[i]}. Update coef[{i}][{j}]: {org_fix_mat[i,j]} => {fix_mat[i,j]}"
                    )
        elif mode.is_input_yuv and not mode.is_output_yuv:  # Y2R
            if fix_mat[0, 0] != target_denorms[0]:
                print(f"NOTE: Update coef[0,0] = {fix_mat[0, 0]} => {target_denorms[0]}, since RY2 case!")
                fix_mat[0, 0] = target_denorms[0]
            if fix_mat[1, 0] != target_denorms[0]:
                print(f"NOTE: Update coef[1,0] = {fix_mat[1, 0]} => {target_denorms[0]}, since RY2 case!")
                fix_mat[1, 0] = target_denorms[0]
            if fix_mat[2, 0] != target_denorms[0]:
                print(f"NOTE: Update coef[2,0] = {fix_mat[2, 0]} => {target_denorms[0]}, since RY2 case!")
                fix_mat[2, 0] = target_denorms[0]
            if fix_mat[0, 1] != 0:
                print(f"NOTE: Update coef[0,1] = {fix_mat[0, 1]} => 0, since RY2 case!")
                fix_mat[0, 1] = 0
            if fix_mat[2, 2] != 0:
                print(f"NOTE: Update coef[1,0] = {fix_mat[2, 2]} => 0, since RY2 case!")
                fix_mat[2, 2] = 0

    ## get fixed offset
    fix_ofs = (fix_factor * range_ofs_o + fix_mat @ range_ofs_i).astype(np.int32)
    return fix_mat, fix_ofs


def get_csc_coefs(config: CscCoefConfig, bcsh_cfg: Optional[CscBcshConfig]) -> tuple[np.ndarray, np.ndarray]:
    ## get convert mat & vec first
    range_mat_i, range_mat_o, range_ofs_i, range_ofs_o = get_range_convert_mat(config.csc_mode, config.pixel_depth)
    color_convert_mat = get_space_convert_mat(config.csc_mode)
    final_mat = range_mat_o @ color_convert_mat @ range_mat_i
    final_ofs = range_ofs_o + final_mat @ range_ofs_i

    ## adjust final_mat with bsch configs
    if bcsh_cfg is not None:
        if config.algo_type in {"RK HW CSC", "RK SW CSC"}:
            final_mat, range_ofs_o, diagonal_ratio = adjust_convert_mat(config, bcsh_cfg, final_mat, range_ofs_o)
            final_ofs = range_ofs_o + final_mat @ range_ofs_i
        elif config.algo_type == "eVideo CSC":
            final_mat, final_ofs, diagonal_ratio = adjust_convert_mat_evideo(config, bcsh_cfg, final_mat, final_ofs)
            # Recover effective range_ofs_o so get_fixed_coefs_mat uses BCSH-corrected offset
            range_ofs_o = final_ofs - final_mat @ range_ofs_i
        else:
            raise ValueError(f"Algorithm '{config.algo_type}' is not implemented in get_csc_coefs.py")
        if config.tune_fix_coefs:
            config.tune_fix_coefs = diagonal_ratio  # >0 means the BCSH matrixes are diagonal

    ## get fixed mat, dtype=np.int32
    if config.coef_precision > 0:
        csc_coefs, csc_offset = get_fixed_coefs_mat(config, final_mat, range_ofs_i, range_ofs_o)
        if config.platform.lower() == "rk3576":
            rnd_half = 1 << (config.coef_precision - 1)
            csc_offset = (csc_offset + rnd_half + (csc_offset >> 31)) >> config.coef_precision
    else:
        csc_coefs = final_mat
        csc_offset = final_ofs

    return csc_coefs, csc_offset


def parse_csc_mode_str(csc_mode_str) -> Optional[CscMode]:
    ## csc_mode_str: 709l_to_rgbl
    substrs = csc_mode_str.split("_to_")
    if len(substrs) != 2:
        print(f"Error: invalid csc mode string: {csc_mode_str}. use 'xxxf/l_to_xxxf/l' format ...")
        return None

    color_space_i = substrs[0].lower()
    color_space_o = substrs[1].lower()
    range_i = color_space_i[-1].upper()
    range_o = color_space_o[-1].upper()
    if range_i not in ["L", "F"] or range_o not in ["L", "F"]:
        print(f"Error: invalid csc mode string: {csc_mode_str}. use 'xxxf/l_to_xxxf/l' format ...")
        return None

    color_space_i = color_space_i[0:-1]
    color_space_o = color_space_o[0:-1]
    if color_space_i.startswith("601") or color_space_i.startswith("709") or color_space_i.startswith("2020"):
        color_space_i = "bt" + color_space_i
    if color_space_o.startswith("601") or color_space_o.startswith("709") or color_space_o.startswith("2020"):
        color_space_o = "bt" + color_space_o
    supported_colorspaces = ["rgb", "bt601", "bt709", "bt2020"]
    if color_space_i not in supported_colorspaces or color_space_o not in supported_colorspaces:
        print(
            f"Error: invalid csc mode string: {csc_mode_str}. input({color_space_i}) or output({color_space_o}) color space is not supported!"
        )
        return None

    mode = CscMode()
    mode.is_input_yuv = color_space_i.startswith("bt")
    mode.is_output_yuv = color_space_o.startswith("bt")
    mode.is_input_full_range = range_i == "F"
    mode.is_output_full_range = range_o == "F"
    if color_space_i == "rgb":
        color_space_i = color_space_o if color_space_o != "rgb" else "bt709"
    if color_space_o == "rgb":
        color_space_o = color_space_i if color_space_i != "rgb" else "bt709"
    mode.input_color_encoding = ColorSpace[color_space_i.upper()]
    mode.output_color_encoding = ColorSpace[color_space_o.upper()]

    return mode


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--print_all", action="store_true", help="print all csc mode coefs")
    parser.add_argument("-c", "--fix_check", action="store_true", help="check and do fine tuning for the fixed coefs")
    parser.add_argument(
        "-o",
        "--out_file",
        type=str,
        default="",
        help="dump all csc coefs for all supported modes to a file when '-a' is set",
    )
    parser.add_argument(
        "-p", "--platform", type=str, default="RK3572", help="the RK soc platform name, like: rk3572/rk3576/rk3538"
    )
    parser.add_argument(
        "-M", "--mode", type=str, default="", help="a single csc mode string, like: '601f_to_rgbl/rgbf_to_2020f' ...)"
    )
    parser.add_argument("-P", "--precision", type=int, default=10, help="the fixed coef precision bits 0 or [8, 16]")
    parser.add_argument("-D", "--depth", type=int, default=10, help="the pixel depth bits [8, 16]")
    parser.add_argument("-r", "--reg_type", type=int, default=0, help="dump register values, type range: [0, 2]")
    parser.add_argument("-C", "--color", type=float, nargs=3, help="do color conversion with out coefs")
    parser.print_usage()
    args, _ = parser.parse_known_args()

    depth = args.depth
    if depth not in range(8, 17):
        print(f"Error: pixel_depth({depth}) should be in range [8, 16]!")
        exit(-1)
    precision = args.precision
    if precision not in range(8, 17) and precision != 0:
        print(f"Error: precision bits({precision}) should be in range [8, 16]!")
        exit(-1)
    if precision > 0 and precision < depth:
        print(f"Warning: precision bits({precision}) better >= pixel_depth({depth})!")
    reg_type = args.reg_type
    if reg_type not in range(3):
        print(f"Warning: reg_type({reg_type}) should be in range [0, 2]! ignore this option.")
        reg_type = 0

    if args.mode:
        mode_str = args.mode.lower()
    else:
        mode_str = "print_all"
        args.print_all = True
    out_file = args.out_file if args.out_file else f"csc_coefs_%dbit-%dbit_from_py.txt" % (depth, precision)
    print(f" - get pixel_bits: {depth}, coefs_bits: {precision}, fix_check: {args.fix_check}")
    print(f" - get csc_mode: {mode_str}")

    ## create a CscConfig object
    csc_config = CscCoefConfig()
    csc_config.pixel_depth = depth
    csc_config.coef_precision = precision
    csc_config.tune_fix_coefs = args.fix_check
    csc_config.platform = args.platform.lower()  # RK3576/RK3572/RK3538

    bcsh = CscBcshConfig()
    # bcsh.hue = 256
    # bcsh.saturation = 299
    # bcsh.contrast = 311
    # bcsh.brightness = 212
    # bcsh.r_gain = 288
    # bcsh.g_gain = 288
    # bcsh.b_gain = 288
    # bcsh.r_offset = 253
    # bcsh.g_offset = 251
    # bcsh.b_offset = 249

    np.set_printoptions(linewidth=120)
    float_fmt = {'float_kind': lambda x: f"{x:.6f}"}  # fsor float data format-string
    if args.print_all:
        print(f" - get out_file: {out_file}")
        count = 0
        fp = open(out_file, "w")
        for mode_str in g_supported_standard_convert_modes:
            csc_config.csc_mode = g_supported_standard_convert_modes[mode_str]
            mat, offset = get_csc_coefs(csc_config, bcsh)
            if mat is not None:
                print(f"CSC mode: {mode_str.upper()}:")
                print(f"\t- matrix: {np.array2string(mat.flatten(), separator=', ', formatter=float_fmt)}")
                print(f"\t- offset: {np.array2string(offset.flatten(), separator=', ', formatter=float_fmt)}")
                fp.write(f"CSC mode: {mode_str.upper()}:\n")
                fp.write(f"\t- matrix: {np.array2string(mat.flatten(), separator=', ', formatter=float_fmt)}\n")
                fp.write(f"\t- offset: {np.array2string(offset.flatten(), separator=', ', formatter=float_fmt)}\n")
                count += 1
            else:
                print(f"invalid csc mode: {mode_str.upper()}!")
        fp.close()
        print(f"write {count} group of csc coefs to: {out_file}")
    else:
        csc_config.csc_mode = parse_csc_mode_str(mode_str)

        mat, offset = get_csc_coefs(csc_config, bcsh)
        if mat is not None:
            print(f"CSC mode: {mode_str.upper()}:")
            print(f"\t- matrix: {np.array2string(mat.flatten(), separator=', ', formatter=float_fmt)}")
            print(f"\t- offset: {np.array2string(offset.flatten(), separator=', ', formatter=float_fmt)}")
            if precision > 0 and reg_type > 0:
                regs = [0] * 8
                if reg_type == 2:
                    regs[0] = 0x1 | (0x1 << 1) | ((mat[0, 0] & 0xFFFF) << 16)
                    regs[1] = (mat[0, 1] & 0xFFFF) | ((mat[0, 2] & 0xFFFF) << 16)
                    regs[2] = (mat[1, 0] & 0xFFFF) | ((mat[1, 1] & 0xFFFF) << 16)
                    regs[3] = (mat[1, 2] & 0xFFFF) | ((mat[2, 0] & 0xFFFF) << 16)
                    regs[4] = (mat[2, 1] & 0xFFFF) | ((mat[2, 2] & 0xFFFF) << 16)
                else:
                    regs[0] = (mat[0, 0] & 0xFFFF) | ((mat[0, 1] & 0xFFFF) << 16)
                    regs[1] = (mat[0, 2] & 0xFFFF) | ((mat[1, 0] & 0xFFFF) << 16)
                    regs[2] = (mat[1, 1] & 0xFFFF) | ((mat[1, 2] & 0xFFFF) << 16)
                    regs[3] = (mat[2, 0] & 0xFFFF) | ((mat[2, 1] & 0xFFFF) << 16)
                    regs[4] = mat[2, 2] & 0xFFFF
                regs[5] = offset[0].astype(np.uint32)
                regs[6] = offset[1].astype(np.uint32)
                regs[7] = offset[2].astype(np.uint32)
                print("\t- reg[0:4]: 0x%08X 0x%08X 0x%08X 0x%08X" % (regs[0], regs[1], regs[2], regs[3]))
                print("\t- reg[4:8]: 0x%08X 0x%08X 0x%08X 0x%08X" % (regs[4], regs[5], regs[6], regs[7]))
        else:
            print(f"invalid csc mode: {mode_str.upper()}!")
            exit(-1)

        if args.color is not None:
            out_color = mat @ args.color + offset
            if precision > 0:
                out_color = (out_color.astype(np.int32) + (1 << (precision - 1))) >> precision
                out_color = np.clip(out_color, 0, 2**depth - 1)

            # 格式化 numpy 数组，保留 6 位小数
            def format_array(arr):
                return '[' + ', '.join(f'{x:.4f}' for x in arr) + ']'

            print(f"do conversion: {format_array(args.color)} -> {format_array(out_color)}")
