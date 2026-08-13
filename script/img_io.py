"""
Copyright   : Copyright (c) 2026 by Rockchip. All right reserved.
FilePath    : img_io.py
Author      : vance.wu@rock-chips.com
Date        : 2026-06-14
Description : Image I/O, format, colorspace, and resampling utilities.

              Provides shared constants (FORMAT_NAMES, CLRSPC_NAMES, etc.)
              and the ``ImageFrame`` class for pipeline data management.
"""

import os
import re
import sys
import numpy as np
from collections.abc import Callable

# Import canonical BT.601 / BT.709 / BT.2020 matrices.
try:
    from .csc.get_csc_coefs import (
        g_r2y_mat_bt601,
        g_y2r_mat_bt601,
        g_r2y_mat_bt709,
        g_y2r_mat_bt709,
        g_r2y_mat_bt2020,
        g_y2r_mat_bt2020,
    )
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from csc.get_csc_coefs import (
        g_r2y_mat_bt601,
        g_y2r_mat_bt601,
        g_r2y_mat_bt709,
        g_y2r_mat_bt709,
        g_r2y_mat_bt2020,
        g_y2r_mat_bt2020,
    )

# ------------------------------------------------------------------ #
# Shared constants                                                   #
# ------------------------------------------------------------------ #

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
    6: ("bt2020", "L"),
    7: ("bt2020", "F"),
}

FMT_OPTIONS_8BIT = [0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7, 0x8, 0x9, 0xA]
FMT_OPTIONS_10BIT = [0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1A]
FMT_OPTIONS_10PACKED = [0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2A]
FMT_OPTIONS = FMT_OPTIONS_8BIT + FMT_OPTIONS_10BIT + FMT_OPTIONS_10PACKED

CLRSPC_OPTIONS = [0, 1, 2, 3, 4, 5, 6, 7]

STB_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp"}

# Internal pipeline canonical planar formats (always packed-planar)
_PLANAR_RGB_8 = 0x2  # RGB_Planar
_PLANAR_RGB_10 = 0x12  # RGB_Planar_10LSB
_PLANAR_YUV_8 = 0x3  # YUV444P_YU24
_PLANAR_YUV_10 = 0x13  # YUV444P_10LSB

# Limited-range clamping boundaries (8-bit basis; ×4 for 10-bit)
_LIMITED_Y_MIN = 16
_LIMITED_Y_MAX = 235
_LIMITED_UV_MIN = 16
_LIMITED_UV_MAX = 240
_LIMITED_RGB_MIN = 16
_LIMITED_RGB_MAX = 235


# ------------------------------------------------------------------ #
# Utility functions                                                  #
# ------------------------------------------------------------------ #


def is_yuv_format(fmt: int) -> bool:
    """Check if format code represents a YUV format."""
    return (fmt & 0xF) >= 0x3


def is_rgb_format(fmt: int) -> bool:
    """Check if format code represents an RGB format."""
    return (fmt & 0xF) <= 0x2


def get_pixel_depth(fmt: int) -> int:
    """Get pixel bit depth from format code (8 or 10)."""
    return 10 if (fmt & 0xF0) >= 0x10 else 8


def get_bytes_per_element(fmt: int) -> int:
    """Get bytes per pixel element from format code."""
    return 2 if (fmt & 0xF0) >= 0x10 else 1


def get_frame_size(width: int, height: int, fmt: int) -> int:
    """Calculate the expected frame size in bytes."""
    base = fmt & 0xF
    bpe = get_bytes_per_element(fmt)
    if base in (0x0, 0x2, 0x3, 0x5):
        elements = width * height * 3
    elif base == 0x1:
        elements = width * height * 4
    elif base == 0x4:
        elements = width * height * 3
    elif base in (0x6, 0x7):
        elements = width * height * 2
    elif base in (0x8, 0x9):
        elements = width * height * 3 // 2
    elif base == 0xA:
        elements = width * height
    else:
        elements = width * height * 3
    return elements * bpe


def guess_fmt_from_ext(ext: str) -> int | None:
    """Guess a default format code from a file extension.

    Returns a canonical planar format suitable for pipeline processing.
    """
    ext = ext.lower()
    if ext in STB_IMAGE_EXTENSIONS:
        return _PLANAR_RGB_8
    if ext == ".yuv":
        return _PLANAR_YUV_8
    if ext == ".rgb":
        return _PLANAR_RGB_8
    return None


def guess_resolution_from_name(filepath: str) -> tuple[int, int] | None:
    """Extract resolution from a filename pattern like 'foo_1920x1080.yuv'."""
    match = re.search(r"(\d+)x(\d+)", os.path.basename(filepath))
    if match:
        return int(match.group(1)), int(match.group(2))
    return None


def is_limited_range(clrspc: int) -> bool:
    """Return True when the colorspace code corresponds to limited range."""
    return (clrspc % 2) == 0


# ------------------------------------------------------------------ #
# Chroma resampling helpers                                          #
# ------------------------------------------------------------------ #


def _repeat_columns(channel: np.ndarray, target_w: int) -> np.ndarray:
    """Duplicate each column to reach target_w (nearest-neighbour expand)."""
    h, w = channel.shape
    if w == target_w:
        return channel
    return np.repeat(channel, target_w // w, axis=1)


def _repeat_rows_cols(channel: np.ndarray, target_h: int, target_w: int) -> np.ndarray:
    """Duplicate rows and columns to reach (target_h, target_w)."""
    h, w = channel.shape
    if h == target_h and w == target_w:
        return channel
    result = np.repeat(channel, target_h // h, axis=0)
    if target_w != w:
        result = np.repeat(result, target_w // w, axis=1)
    return result


def _subsample_columns(channel: np.ndarray, target_w: int) -> np.ndarray:
    """Subsample columns by taking every Nth column (nearest-neighbour shrink)."""
    h, w = channel.shape
    if w == target_w:
        return channel
    step = w // target_w
    return channel[:, ::step]


def _subsample_rows_cols(channel: np.ndarray, target_h: int, target_w: int) -> np.ndarray:
    """Subsample rows and columns by taking every Nth (nearest-neighbour shrink)."""
    h, w = channel.shape
    if h == target_h and w == target_w:
        return channel
    h_step = h // target_h
    w_step = w // target_w
    return channel[::h_step, ::w_step]


# ------------------------------------------------------------------ #
# Subsampling helpers (used by the generic CSC functions)            #
# ------------------------------------------------------------------ #


def _is_422(fmt: int) -> bool:
    """True if the format is a 4:2:2 YUV format."""
    return (fmt & 0xF) in (0x6, 0x7)


def _is_420(fmt: int) -> bool:
    """True if the format is a 4:2:0 YUV format."""
    return (fmt & 0xF) in (0x8, 0x9)


def _upsample_chroma_422(u: np.ndarray, v: np.ndarray, target_w: int) -> tuple[np.ndarray, np.ndarray]:
    """Horizontally upsample 4:2:2 chroma planes to full width."""
    return _repeat_columns(u, target_w), _repeat_columns(v, target_w)


def _upsample_chroma_420(u: np.ndarray, v: np.ndarray, target_h: int, target_w: int) -> tuple[np.ndarray, np.ndarray]:
    """Upsample 4:2:0 chroma planes to full resolution."""
    u_up = _repeat_rows_cols(u, target_h, target_w)
    v_up = _repeat_rows_cols(v, target_h, target_w)
    return u_up, v_up


def _subsample_chroma_422(u: np.ndarray, v: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Horizontally subsample chroma from 444 to 422."""
    return _subsample_columns(u, u.shape[1] // 2), _subsample_columns(v, v.shape[1] // 2)


def _subsample_chroma_420(u: np.ndarray, v: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Subsample chroma from 444 to 420."""
    return (
        _subsample_rows_cols(u, u.shape[0] // 2, u.shape[1] // 2),
        _subsample_rows_cols(v, v.shape[0] // 2, v.shape[1] // 2),
    )


# ------------------------------------------------------------------ #
# Colorspace conversion (BT.601 / BT.709 / BT.2020)                  #
# ------------------------------------------------------------------ #

# Map colorspace code → (rgb→yuv, yuv→rgb) matrix pair.
# colorspace: 2/3→BT601, 4/5→BT709, 6/7→BT2020 (even=L, odd=F).
_CSC_MATRIX_MAP: dict[int, tuple[np.ndarray, np.ndarray]] = {
    2: (g_r2y_mat_bt601, g_y2r_mat_bt601),
    3: (g_r2y_mat_bt601, g_y2r_mat_bt601),
    4: (g_r2y_mat_bt709, g_y2r_mat_bt709),
    5: (g_r2y_mat_bt709, g_y2r_mat_bt709),
    6: (g_r2y_mat_bt2020, g_y2r_mat_bt2020),
    7: (g_r2y_mat_bt2020, g_y2r_mat_bt2020),
}


def _get_csc_matrices(colorspace: int) -> tuple[np.ndarray, np.ndarray]:
    """Return (r2y, y2r) matrices for a colorspace code.  Falls back to BT.709."""
    return _CSC_MATRIX_MAP.get(colorspace, (g_r2y_mat_bt709, g_y2r_mat_bt709))


def _csc_range_params(depth: int) -> dict:
    """Return depth-dependent range constants for 8- or 10-bit data.

    Dict keys:
      yr_center, uv_center — full-range shift for signed Cb/Cr (128 or 512)
      yr_lo_l, yr_hi_l — limited  Y/R/G/B bounds (16/235 or 64/940)
      uv_lo_l, uv_hi_l — limited  U/V     bounds (16/240 or 64/960)
      yruv_lo_f, yruv_hi_f — full  Y/U/V/R/G/B bounds (0/255 or 0/1023)
    """
    if depth == 8:
        scale = 1
        yr_center = 128
    elif depth == 10:
        scale = 4
        yr_center = 512
    else:
        raise ValueError(f"Invalid depth: {depth}")
    return {
        "yr_center": yr_center,
        "uv_center": yr_center,
        "yr_lo_l": 16 * scale,
        "yr_hi_l": 235 * scale,
        "uv_lo_l": 16 * scale,
        "uv_hi_l": 240 * scale,
        "yruv_lo_f": 0,
        "yruv_hi_f": (1 << depth) - 1,
    }


def yuv_to_rgb(
    y: np.ndarray, u: np.ndarray, v: np.ndarray, input_cs: int = 5, output_cs: int = 1
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Convert YUV planar channels to RGB planar channels with full/limited range handling.

    Supports 8-bit (uint8) and 10-bit (uint16), any YUV colorspace at the
    input and any RGB range at the output (same depth).

    Chroma auto-upsampling: if U/V resolution differs from Y, the function
    automatically detects 4:2:2 (half width) or 4:2:0 (half width & height)
    and upsamples to 4:4:4 before conversion.

    ``input_cs``: YUV colorspace (2/3→BT601, 4/5→BT709, 6/7→BT2020).
    ``output_cs``: RGB range (0→limited, 1→full).
    Returns (R, G, B) ndarrays — always separate planar channels, same dtype as y.
    """
    depth = 10 if y.dtype == np.uint16 else 8
    input_limited = is_limited_range(input_cs)
    rp = _csc_range_params(depth)
    _, y2r = _get_csc_matrices(input_cs)

    limit_lo_y = rp["yr_lo_l"]
    limit_hi_y = rp["yr_hi_l"]
    limit_lo_c = rp["uv_lo_l"]
    limit_hi_c = rp["uv_hi_l"]
    uv_center = rp["uv_center"]
    full_hi = rp["yruv_hi_f"]
    full_lo = rp["yruv_lo_f"]

    # Step 0 — chroma upsampling to 444 if needed (auto-detect from U/V shape)
    y_h, y_w = y.shape
    u_h, u_w = u.shape
    if u_h != y_h and u_w != y_w:
        u, v = _upsample_chroma_420(u, v, y_h, y_w)
    elif u_w != y_w:
        u, v = _upsample_chroma_422(u, v, y_w)

    y_f = y.astype(np.float32)
    u_f = u.astype(np.float32)
    v_f = v.astype(np.float32)

    # Step 1 — undo input range encoding → normalized full-range
    u_f = u_f - uv_center
    v_f = v_f - uv_center
    if input_limited:
        scale_y = full_hi / (limit_hi_y - limit_lo_y)
        scale_c = full_hi / (limit_hi_c - limit_lo_c)
        y_f = np.clip((y_f - limit_lo_y) * scale_y, full_lo, full_hi)
        u_f = np.clip(u_f * scale_c, full_lo, full_hi)
        v_f = np.clip(v_f * scale_c, full_lo, full_hi)

    # Step 2 — core y2r matrix
    stacked = np.stack([y_f, u_f, v_f], axis=-1)
    rgb = stacked @ y2r.T

    # Step 3 — apply output range encoding
    if output_cs == 0:  # limited RGB
        rgb = rgb * ((limit_hi_y - limit_lo_y) / full_hi) + limit_lo_y
        lo, hi = limit_lo_y, limit_hi_y
    else:
        lo, hi = full_lo, full_hi

    dtype_out = y.dtype if y.dtype in (np.uint8, np.uint16) else np.uint8
    r = np.clip(np.rint(rgb[..., 0]), lo, hi).astype(dtype_out)
    g = np.clip(np.rint(rgb[..., 1]), lo, hi).astype(dtype_out)
    b = np.clip(np.rint(rgb[..., 2]), lo, hi).astype(dtype_out)
    return r, g, b


def rgb_to_yuv(
    r: np.ndarray, g: np.ndarray, b: np.ndarray, input_cs: int = 1, output_cs: int = 5
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Convert RGB planar channels to YUV planar channels with full/limited range handling.

    Supports 8-bit (uint8) and 10-bit (uint16), any RGB range at the
    input and any YUV colorspace at the output (same depth).
    Always outputs 4:4:4 planar YUV.

    ``input_cs``: RGB range (0→limited, 1→full).
    ``output_cs``: YUV colorspace (2/3→BT601, 4/5→BT709, 6/7→BT2020).
    Returns (Y, U, V) ndarrays — always 4:4:4 planar, same dtype as r.
    """
    depth = 10 if r.dtype == np.uint16 else 8
    rp = _csc_range_params(depth)
    r2y, _ = _get_csc_matrices(output_cs)
    output_limited = is_limited_range(output_cs)

    _yr_lo = rp["yr_lo_l"]
    _yr_hi = rp["yr_hi_l"]
    _uv_lo = rp["uv_lo_l"]
    _uv_hi = rp["uv_hi_l"]
    _uv_ctr = rp["uv_center"]
    _fr_hi = rp["yruv_hi_f"]

    # Step 1 — undo input range encoding → normalized full-range
    if input_cs == 0:  # limited RGB input
        rgb_scale = _fr_hi / (_yr_hi - _yr_lo)
        r_f = (r.astype(np.float32) - _yr_lo) * rgb_scale
        g_f = (g.astype(np.float32) - _yr_lo) * rgb_scale
        b_f = (b.astype(np.float32) - _yr_lo) * rgb_scale
    else:
        r_f = r.astype(np.float32)
        g_f = g.astype(np.float32)
        b_f = b.astype(np.float32)

    # Step 2 — core r2y matrix
    stacked = np.stack([r_f, g_f, b_f], axis=-1)
    yuv = stacked @ r2y.T

    # Step 3 — apply output range encoding
    if output_limited:
        yuv[..., 0] = yuv[..., 0] * ((_yr_hi - _yr_lo) / _fr_hi) + _yr_lo
        uv_scale = (_uv_hi - _uv_lo) / _fr_hi
        uv_bias = _uv_ctr + _uv_lo
        yuv[..., 1] = yuv[..., 1] * uv_scale + uv_bias
        yuv[..., 2] = yuv[..., 2] * uv_scale + uv_bias
        y_lo, y_hi = _yr_lo, _yr_hi
        uv_lo, uv_hi = _uv_lo, _uv_hi
    else:
        yuv[..., 1] += _uv_ctr
        yuv[..., 2] += _uv_ctr
        y_lo = y_hi = uv_lo = uv_hi = 0  # use full-range clip below
        y_hi = _fr_hi
        uv_hi = _fr_hi

    dtype_out = r.dtype if r.dtype in (np.uint8, np.uint16) else np.uint8
    y_out = np.clip(np.rint(yuv[..., 0]), y_lo, y_hi).astype(dtype_out)
    u_out = np.clip(np.rint(yuv[..., 1]), uv_lo, uv_hi).astype(dtype_out)
    v_out = np.clip(np.rint(yuv[..., 2]), uv_lo, uv_hi).astype(dtype_out)
    return y_out, u_out, v_out


# ------------------------------------------------------------------ #
# ImageFrame                                                         #
# ------------------------------------------------------------------ #


class ImageFrame:
    """Encapsulates planar image data with format and colorspace metadata.

    Internally stores three planar channels (pyr/pug/pvb) as 2D numpy arrays.
    The channels may have different resolutions for subsampled YUV formats:
      - YUV422: pyr (H,W), pug (H,W/2), pvb (H,W/2)
      - YUV420: pyr (H,W), pug (H/2,W/2), pvb (H/2,W/2)

    Pipeline processing uses canonical planar formats internally:
      - 8/10-bit YUV444 → 0x3 / 0x13 (YUV444P)
      - 8/10-bit YUV422 → 0x6 / 0x16 (YUV422P)
      - 8/10-bit YUV420 → 0x8 / 0x18 (YUV420P)
    """

    __slots__ = ("pyr", "pug", "pvb", "fmt", "clrspc", "frame_idx")

    # ------------------------------------------------------------------ #
    # Construction                                                       #
    # ------------------------------------------------------------------ #

    def __init__(
        self, pyr: np.ndarray, pug: np.ndarray, pvb: np.ndarray, fmt: int, clrspc: int = 5, frame_idx: int = 0
    ) -> None:
        self.pyr = pyr  # Y or R channel (H, W)
        self.pug = pug  # U or G channel (H_uv, W_uv)
        self.pvb = pvb  # V or B channel (H_uv, W_uv)
        self.fmt = fmt  # format code
        self.clrspc = clrspc  # colorspace code
        self.frame_idx = frame_idx

    @classmethod
    def from_file(
        cls, filepath: str, width: int, height: int, fmt: int, clrspc: int = 5, frame_idx: int = 0
    ) -> "ImageFrame":
        """Read a single frame from a raw image file.

        Supports YUV and RGB raw formats. Non-planar formats (interleaved,
        semi-planar, packed) are converted to planar during read.
        YUV422/420 chroma planes are kept at native subsampled resolution.
        """
        base = fmt & 0xF
        depth = get_pixel_depth(fmt)
        bpe = get_bytes_per_element(fmt)
        dtype = np.uint16 if bpe == 2 else np.uint8

        raw = np.fromfile(filepath, dtype=dtype)
        frame_size = get_frame_size(width, height, fmt)
        offset = frame_idx * frame_size

        if base == 0x0:  # RGB888 / RGB_10LSB
            rgb = raw[offset : offset + height * width * 3].reshape(height, width, 3)
            out_fmt = _PLANAR_RGB_10 if depth >= 10 else _PLANAR_RGB_8
            return cls(rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2], out_fmt, clrspc)
        elif base == 0x1:  # RGBA8888 / RGBA_10LSB
            rgba = raw[offset : offset + height * width * 4].reshape(height, width, 4)
            out_fmt = _PLANAR_RGB_10 if depth >= 10 else _PLANAR_RGB_8
            return cls(rgba[:, :, 0], rgba[:, :, 1], rgba[:, :, 2], out_fmt, clrspc)
        elif base == 0x2:  # RGB_Planar / RGB_Planar_10LSB
            planar = raw[offset : offset + 3 * height * width].reshape(3, height, width)
            out_fmt = _PLANAR_RGB_10 if depth >= 10 else _PLANAR_RGB_8
            return cls(planar[0], planar[1], planar[2], out_fmt, clrspc)
        elif base == 0x3:  # YUV444P / YUV444P_10LSB
            planar = raw[offset : offset + 3 * height * width].reshape(3, height, width)
            out_fmt = _PLANAR_YUV_10 if depth >= 10 else _PLANAR_YUV_8
            return cls(planar[0], planar[1], planar[2], out_fmt, clrspc)
        elif base == 0x4:  # YUV444SP NV24 / YUV444SP_10LSB
            y_size = height * width
            y = raw[offset : offset + y_size].reshape(height, width)
            uv = raw[offset + y_size : offset + y_size + y_size * 2].reshape(height, width, 2)
            out_fmt = _PLANAR_YUV_10 if depth >= 10 else _PLANAR_YUV_8
            return cls(y, uv[:, :, 0], uv[:, :, 1], out_fmt, clrspc)
        elif base == 0x5:  # YUV444I VU24 / YUV444I_10LSB
            vuy = raw[offset : offset + height * width * 3].reshape(height, width, 3)
            out_fmt = _PLANAR_YUV_10 if depth >= 10 else _PLANAR_YUV_8
            return cls(vuy[:, :, 2], vuy[:, :, 1], vuy[:, :, 0], out_fmt, clrspc)
        elif base == 0x6:  # YUV422P / YUV422P_10LSB
            y_size = height * width
            uv_size = height * (width // 2)
            y = raw[offset : offset + y_size].reshape(height, width)
            u = raw[offset + y_size : offset + y_size + uv_size].reshape(height, width // 2)
            v = raw[offset + y_size + uv_size : offset + y_size + 2 * uv_size].reshape(height, width // 2)
            frame = cls(y, u, v, fmt, clrspc)
            frame.to_yuv444()
            return frame
        elif base == 0x7:  # YUV422SP NV16 / YUV422SP_10LSB
            y_size = height * width
            y = raw[offset : offset + y_size].reshape(height, width)
            uv = raw[offset + y_size : offset + y_size + y_size].reshape(height, width // 2, 2)
            frame = cls(y, uv[:, :, 0], uv[:, :, 1], fmt, clrspc)
            frame.to_yuv444()
            return frame
        elif base == 0x8:  # YUV420P / YUV420P_10LSB
            y_size = height * width
            uv_size = (height // 2) * (width // 2)
            y = raw[offset : offset + y_size].reshape(height, width)
            u = raw[offset + y_size : offset + y_size + uv_size].reshape(height // 2, width // 2)
            v = raw[offset + y_size + uv_size : offset + y_size + 2 * uv_size].reshape(height // 2, width // 2)
            frame = cls(y, u, v, fmt, clrspc)
            frame.to_yuv444()
            return frame
        elif base == 0x9:  # YUV420SP NV12 / YUV420SP_10LSB
            y_size = height * width
            y = raw[offset : offset + y_size].reshape(height, width)
            uv = raw[offset + y_size : offset + y_size + (height // 2) * width].reshape(height // 2, width // 2, 2)
            frame = cls(y, uv[:, :, 0], uv[:, :, 1], fmt, clrspc)
            frame.to_yuv444()
            return frame
        elif base == 0xA:  # YUV400 Gray / YUV400_10LSB
            y = raw[offset : offset + height * width].reshape(height, width)
            uv = np.full_like(y, 128, dtype=dtype)
            out_fmt = _PLANAR_YUV_10 if depth >= 10 else _PLANAR_YUV_8
            return cls(y, uv, uv, out_fmt, clrspc)
        else:
            raise ValueError(f"Unsupported base format: 0x{base:X}")

    @classmethod
    def from_image(cls, filepath: str, clrspc: int = 5) -> "ImageFrame":
        """Read a PNG/JPG/BMP file and return as planar RGB."""
        try:
            from PIL import Image as PILImage
        except ImportError:
            raise ImportError("Pillow is required to read image files.")
        img = PILImage.open(filepath).convert("RGB")
        data = np.array(img, dtype=np.uint8)
        r, g, b = data[:, :, 0], data[:, :, 1], data[:, :, 2]
        return cls(r, g, b, _PLANAR_RGB_8, clrspc)

    @classmethod
    def from_rgb_channels(
        cls, r: np.ndarray, g: np.ndarray, b: np.ndarray, clrspc: int = 5, depth: int = 8
    ) -> "ImageFrame":
        """Build a YUV444 ImageFrame from separate R/G/B channels.

        ``depth`` controls the output format tag (8→0x3, 10→0x13).
        The caller is responsible for providing correctly-scaled input arrays.
        """
        y, u, v = rgb_to_yuv(r, g, b, input_cs=1, output_cs=clrspc)
        out_fmt = _PLANAR_YUV_10 if depth >= 10 else _PLANAR_YUV_8
        return cls(y, u, v, out_fmt, clrspc)

    @classmethod
    def from_solid_color(
        cls, width: int, height: int, red: int, green: int, blue: int, clrspc: int = 5, depth: int = 8
    ) -> "ImageFrame":
        """Create a solid YUV444 ImageFrame from R/G/B values.

        Values are interpreted at the format's bit depth (0..255 for 8-bit,
        0..1023 for 10-bit) and stored directly without scaling.
        Limited-range clamping is applied when ``is_limited_range(clrspc)``.
        """
        d = np.uint16 if depth >= 10 else np.uint8
        r = np.full((height, width), red, dtype=d)
        g = np.full((height, width), green, dtype=d)
        b = np.full((height, width), blue, dtype=d)
        return cls.from_rgb_channels(r, g, b, clrspc, depth)

    @classmethod
    def from_solid_yuv(
        cls, width: int, height: int, y_val: int, u_val: int, v_val: int, clrspc: int = 5, depth: int = 8
    ) -> "ImageFrame":
        """Create a solid YUV444 ImageFrame from Y/U/V values.

        Values are interpreted at the format's bit depth (0..255 for 8-bit,
        0..1023 for 10-bit) and stored directly without scaling.
        Limited-range clamping is applied when ``is_limited_range(clrspc)``.
        """
        d = np.uint16 if depth >= 10 else np.uint8
        out_fmt = _PLANAR_YUV_10 if depth >= 10 else _PLANAR_YUV_8
        y = np.full((height, width), y_val, dtype=d)
        u = np.full((height, width), u_val, dtype=d)
        v = np.full((height, width), v_val, dtype=d)
        return cls(y, u, v, out_fmt, clrspc)

    # ------------------------------------------------------------------ #
    # Properties                                                         #
    # ------------------------------------------------------------------ #

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

    @property
    def is_444(self) -> bool:
        """True when chroma planes share Y resolution (YUV444 or RGB)."""
        return self.pug.shape == self.pyr.shape

    # ------------------------------------------------------------------ #
    # Copy                                                               #
    # ------------------------------------------------------------------ #

    def copy(self) -> "ImageFrame":
        """Deep copy (data arrays are copied)."""
        return ImageFrame(self.pyr.copy(), self.pug.copy(), self.pvb.copy(), self.fmt, self.clrspc, self.frame_idx)

    # ------------------------------------------------------------------ #
    # Precision conversion                                               #
    # ------------------------------------------------------------------ #

    def _pick_planar_fmt(self, target_10bit: bool) -> int:
        """Pick internal planar format code matching the YUV/RGB domain."""
        if self.is_rgb:
            return _PLANAR_RGB_10 if target_10bit else _PLANAR_RGB_8
        else:
            return _PLANAR_YUV_10 if target_10bit else _PLANAR_YUV_8

    def promote_to_10bit(self) -> "ImageFrame":
        """Promote 8-bit data to 10-bit by left-shifting 2 bits.

        No-op if already 10-bit. Returns self for chaining.
        """
        if self.depth >= 10:
            return self
        self.pyr = self.pyr.astype(np.uint16) << 2
        self.pug = self.pug.astype(np.uint16) << 2
        self.pvb = self.pvb.astype(np.uint16) << 2
        self.fmt = self._pick_planar_fmt(target_10bit=True)
        return self

    def demote_to_8bit(self) -> "ImageFrame":
        """Demote 10-bit data to 8-bit with rounding (add 2 then >> 2).

        No-op if already 8-bit. Returns self for chaining.
        """
        if self.depth <= 8:
            return self
        for attr in ("pyr", "pug", "pvb"):
            ch = getattr(self, attr)
            rounded = (ch.astype(np.uint32) + 2) >> 2
            setattr(self, attr, np.clip(rounded, 0, 255).astype(np.uint8))
        self.fmt = self._pick_planar_fmt(target_10bit=False)
        return self

    # ------------------------------------------------------------------ #
    # Write                                                              #
    # ------------------------------------------------------------------ #

    def to_file(self, filepath: str) -> None:
        """Write the frame to a raw file. Appends to existing files.

        Requires the frame to be in YUV444 planar format.
        """
        if not self.is_444:
            raise ValueError("to_file currently only supports YUV444 planar frames.")
        raw = np.stack([self.pyr, self.pug, self.pvb], axis=0).ravel()
        raw.astype(self.pyr.dtype).tofile(filepath)

    # ------------------------------------------------------------------ #
    # Chroma upsampling / downsampling                                   #
    # ------------------------------------------------------------------ #

    def to_yuv444(self) -> "ImageFrame":
        """Upsample chroma planes to Y resolution (nearest-neighbour).

        RGB frames are returned unchanged. No-op if already 444.
        """
        if self.is_rgb or self.is_444:
            return self
        h_y, w_y = self.pyr.shape
        u_up = _repeat_rows_cols(self.pug, h_y, w_y)
        v_up = _repeat_rows_cols(self.pvb, h_y, w_y)
        self.pug = u_up
        self.pvb = v_up
        self.fmt = self._pick_planar_fmt(target_10bit=self.depth >= 10)
        return self

    def to_yuv422(self) -> "ImageFrame":
        """Subsample chroma horizontally to YUV422."""
        if not self.is_yuv:
            raise ValueError("Chroma subsampling requires YUV input.")
        h_y, w_y = self.pyr.shape
        if self.pug.shape[1] == w_y // 2 and self.pug.shape[0] == h_y:
            return self  # already 422
        u_sub = _subsample_columns(self.pug, w_y // 2)
        v_sub = _subsample_columns(self.pvb, w_y // 2)
        self.pug = u_sub
        self.pvb = v_sub
        self.fmt = 0x16 if self.depth >= 10 else 0x6
        return self

    def to_yuv420(self) -> "ImageFrame":
        """Subsample chroma horizontally and vertically to YUV420."""
        if not self.is_yuv:
            raise ValueError("Chroma subsampling requires YUV input.")
        h_y, w_y = self.pyr.shape
        if self.pug.shape[1] == w_y // 2 and self.pug.shape[0] == h_y // 2:
            return self  # already 420
        u_sub = _subsample_rows_cols(self.pug, h_y // 2, w_y // 2)
        v_sub = _subsample_rows_cols(self.pvb, h_y // 2, w_y // 2)
        self.pug = u_sub
        self.pvb = v_sub
        self.fmt = 0x18 if self.depth >= 10 else 0x8
        return self

    # ------------------------------------------------------------------ #
    # Colorspace conversion                                              #
    # ------------------------------------------------------------------ #

    def to_rgb(self) -> "ImageFrame":
        """Convert YUV to RGB in-place.

        Requires YUV444 layout (call ``to_yuv444()`` first if needed).
        Returns self for chaining.
        """
        if self.is_rgb:
            return self
        if not self.is_444:
            self.to_yuv444()
        r, g, b = yuv_to_rgb(
            self.pyr, self.pug, self.pvb, input_cs=self.clrspc, output_cs=0 if is_limited_range(self.clrspc) else 1
        )
        self.pyr = r
        self.pug = g
        self.pvb = b
        self.fmt = self._pick_planar_fmt(target_10bit=self.depth >= 10)
        self.clrspc = 0 if is_limited_range(self.clrspc) else 1  # YUV range → RGB range
        return self

    def to_yuv(self, target_clrspc: int = 5) -> "ImageFrame":
        """Convert RGB to YUV in-place.

        Returns self for chaining.
        """
        if self.is_yuv:
            if self.clrspc != target_clrspc:
                self.clrspc = target_clrspc
            return self
        y, u, v = rgb_to_yuv(self.pyr, self.pug, self.pvb, input_cs=self.clrspc, output_cs=target_clrspc)
        self.pyr = y
        self.pug = u
        self.pvb = v
        self.fmt = self._pick_planar_fmt(target_10bit=self.depth >= 10)
        self.clrspc = target_clrspc
        return self

    # ------------------------------------------------------------------ #
    # Scaling / resize                                                   #
    # ------------------------------------------------------------------ #

    def resize(self, new_width: int, new_height: int) -> "ImageFrame":
        """Resize the frame using bilinear interpolation.

        Works on YUV444 or RGB planar data. Chroma planes are also resized
        proportionally for subsampled formats.
        Returns self for chaining.
        """
        try:
            import cv2
        except ImportError:
            raise ImportError("OpenCV is required for resize.")

        scale_w = new_width / self.width
        scale_h = new_height / self.height

        self.pyr = cv2.resize(
            self.pyr.astype(np.float32), (new_width, new_height), interpolation=cv2.INTER_LINEAR
        ).astype(self.pyr.dtype)

        new_uv_w = int(self.uv_width * scale_w)
        new_uv_h = int(self.uv_height * scale_h)
        self.pug = cv2.resize(self.pug.astype(np.float32), (new_uv_w, new_uv_h), interpolation=cv2.INTER_LINEAR).astype(
            self.pug.dtype
        )
        self.pvb = cv2.resize(self.pvb.astype(np.float32), (new_uv_w, new_uv_h), interpolation=cv2.INTER_LINEAR).astype(
            self.pvb.dtype
        )
        return self

    # ------------------------------------------------------------------ #
    # Channel-stacked export (backward compatibility)                    #
    # ------------------------------------------------------------------ #

    def as_yuv444_stacked(self) -> np.ndarray:
        """Convert to YUV444 and return as channels-last (H, W, 3) ndarray.

        Keeps the frame's native bit depth — call ``demote_to_8bit()`` first
        if an 8-bit buffer is required.
        """
        if not self.is_yuv:
            self.to_yuv()
        if not self.is_444:
            self.to_yuv444()
        return np.stack([self.pyr, self.pug, self.pvb], axis=-1)

    def as_planar(self) -> np.ndarray:
        """Stack channels into (3, H, W) planar array.

        Requires all channels to share resolution (YUV444 or RGB).
        """
        if not self.is_444:
            self.to_yuv444()
        return np.stack([self.pyr, self.pug, self.pvb], axis=0)

    def as_tuple(self) -> tuple:
        """Return (planar, fmt, clrspc) for backward-compatible module API.

        WARNING: stacks channels — only valid when all channels share
        the same resolution (RGB, YUV444, or already upsampled).
        """
        return (self.as_planar(), self.fmt, self.clrspc)

    # ------------------------------------------------------------------ #
    # Display helpers                                                    #
    # ------------------------------------------------------------------ #

    @staticmethod
    def fmt_to_display(fmt: int) -> str:
        """Format code → display string (e.g. '0x3 - YUV444P_YU24')."""
        return f"0x{fmt:x} - {FORMAT_NAMES.get(fmt, 'Unknown')}"

    @staticmethod
    def clrspc_to_display(clrspc: int) -> str:
        """Colorspace code → display string (e.g. '5 - BT709_Full')."""
        return f"{clrspc} - {CLRSPC_NAMES.get(clrspc, 'Unknown')}"

    def __repr__(self) -> str:
        return (
            f"ImageFrame({self.width}x{self.height}, "
            f"{self.fmt_to_display(self.fmt)}, "
            f"{self.clrspc_to_display(self.clrspc)}, "
            f"idx={self.frame_idx})"
        )
