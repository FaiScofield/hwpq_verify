"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : get_csc_coefs.py
Author      : vance.wu@rock-chips.com
Date        : 2025-08-27
Description :
LastEditTime: 2025-09-09
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
    platform = "RK3572"


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
) -> tuple[np.ndarray, np.ndarray, bool]:
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
    offset_shift_bits = 3 - (config.pixel_depth - 8)  # [1, 3]
    if offset_shift_bits >= 0:
        r_offset >>= offset_shift_bits  # [-32, 32) for U8
        g_offset >>= offset_shift_bits
        b_offset >>= offset_shift_bits
    else:
        r_offset <<= -offset_shift_bits
        g_offset <<= -offset_shift_bits
        b_offset <<= -offset_shift_bits
    if config.pixel_depth <= 10:
        brightness >>= 10 - config.pixel_depth  # [-64, 64) for U8
    else:
        brightness <<= config.pixel_depth - 10  # [-256, 256) for U10

    gain_matrix = np.array([[r_gain, 0, 0], [0, g_gain, 0], [0, 0, b_gain]], dtype=np.float32)
    contrast_matrix = np.array([[contrast, 0, 0], [0, contrast, 0], [0, 0, contrast]], dtype=np.float32)
    hue_matrix = np.array([[1, 0, 0], [0, cos_hue, sin_hue], [0, -sin_hue, cos_hue]], dtype=np.float32)
    saturation_matrix = np.array([[saturation, 0, 0], [0, saturation, 0], [0, 0, saturation]], dtype=np.float32)
    b_diagonal_m0 = hue_rad == 0
    b_diagonal_m1 = r_gain == g_gain and g_gain == b_gain

    ## M0 = hue_matrix * saturation_matrix, which is applied on YUV space. It will be a DIAGONAL matrix ONLY if the hue_matrix is identity
    ## M1 = gain_matrix * contrast_matrix, which is applied on RGB space. It will be a DIAGONAL matrix ONLY if the gain_matrix is identity
    M0 = hue_matrix @ saturation_matrix
    M1 = gain_matrix @ contrast_matrix
    r2y_matrix = g_r2y_mat_bt709
    y2r_matrix = g_y2r_mat_bt709
    mode = config.csc_mode

    ## Y2Y: output = T * M0 * N_r2y * M1 * N_y2r
    if mode.is_input_yuv and mode.is_output_yuv:
        out_mat = out_mat @ M0 @ r2y_matrix @ M1 @ y2r_matrix
        out_vec[0] += brightness
    ## Y2R: output = M1 * T * M0
    elif mode.is_input_yuv and not mode.is_output_yuv:
        out_mat = M1 @ out_mat @ M0
        out_vec[0] += brightness + r_offset
        out_vec[1] += brightness + g_offset
        out_vec[2] += brightness + b_offset
    ## R2Y: output = M0 * T * M1
    elif not mode.is_input_yuv and mode.is_output_yuv:
        out_mat = M0 @ out_mat @ M1
        out_vec[0] += brightness
    ## R2R: output = T * M1 * N_y2r * M0 * N_r2y
    else:
        out_mat = out_mat @ M1 @ y2r_matrix @ M0 @ r2y_matrix
        out_vec[0] += brightness + r_offset
        out_vec[1] += brightness + g_offset
        out_vec[2] += brightness + b_offset

    ## count diagonal ratio for later fixed-point calcuation
    if hue_rad == 0 and r_gain == g_gain and g_gain == b_gain:
        diagonal_ratio = r_gain * contrast * saturation
    else:
        diagonal_ratio = 0

    return out_mat, out_vec, diagonal_ratio


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

    ## adjust final_mat with bsch configs
    if bcsh_cfg is not None:
        final_mat, range_ofs_o, diagonal_ratio = adjust_convert_mat(config, bcsh_cfg, final_mat, range_ofs_o)
        config.tune_fix_coefs = diagonal_ratio  # >0 means diagonal BCSH matrix

    ## get fixed mat, dtype=np.int32
    if config.coef_precision > 0:
        csc_coefs, csc_offset = get_fixed_coefs_mat(config, final_mat, range_ofs_i, range_ofs_o)
        if config.platform.upper() == "RK3576":
            rnd_half = 1 << (config.precision - 1)
            csc_offset = (csc_offset + rnd_half + (csc_offset >> 31)) >> config.precision
    else:
        csc_coefs = final_mat
        csc_offset = range_ofs_o + final_mat @ range_ofs_i

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
        "-m", "--mode", type=str, default="", help="a single csc mode string, like: '601f_to_rgbl/rgbf_to_2020f' ...)"
    )
    parser.add_argument("-p", "--precision", type=int, default=10, help="the fixed coef precision bits 0 or [8, 16]")
    parser.add_argument("-d", "--depth", type=int, default=10, help="the pixel depth bits [8, 16]")
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
        else:
            print(f"invalid csc mode: {mode_str.upper()}!")
