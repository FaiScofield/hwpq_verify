"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : acm_impl_base.py
Author      : vance.wu@rock-chips.com
Date        : 2026-06-14
Description : Base class for ACM implementation, providing LUT management,
              YUV<=>YHS conversion (trig or cordic), and ACM processing for
              8bit / 10bit YUV444 planar images.
LastEditTime: 2026-06-25
"""

import os
import sys
import json
import cv2
import argparse
import traceback
import warnings
from typing import Optional, Tuple
import numpy as np
import matplotlib.pyplot as plt

if __package__:
    from . import cordic
    from .. import utils as utl
    from ..csc.get_csc_coefs import g_y2r_mat_bt709, g_r2y_mat_bt709
else:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    import cordic
    import utils as utl
    from csc.get_csc_coefs import g_y2r_mat_bt709, g_r2y_mat_bt709


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------
# Default 5x5 separable low-pass kernel, normalised to sum 1.
_DEFAULT_GAUSSIAN_KERNEL_1D = np.array([1, 4, 6, 4, 1], dtype=np.float32)
_DEFAULT_GAUSSIAN_KERNEL = np.outer(_DEFAULT_GAUSSIAN_KERNEL_1D, _DEFAULT_GAUSSIAN_KERNEL_1D)
_DEFAULT_GAUSSIAN_KERNEL /= _DEFAULT_GAUSSIAN_KERNEL.sum()

_BT709_TRIANGLE_REGION_PEAKS = np.array(
    [
        # (s, y)
        [0.96, 96.0 / 255.0],  # M
        [0.94, 123.0 / 255.0],  # R
        [0.91, 163.0 / 255.0],  # Y
        [0.96, 158.0 / 255.0],  # G
        [0.94, 131.0 / 255.0],  # C
        [0.91, 91.0 / 255.0],  # B
    ],
    dtype=np.float32,
)
_BT709_TRIANGLE_REGION_CENTERS_DEG = np.array([25, 85, 145, 205, 265, 325], dtype=np.float32)


def _clip_cast(arr_float: np.ndarray, target_dtype: np.dtype) -> np.ndarray:
    """Cast a float array to ``target_dtype`` while clipping to the dtype's
    representable range. Prevents wrap-around for unsigned / narrow integer
    types when interpolation pushes values outside the original range."""
    if np.issubdtype(target_dtype, np.integer):
        info = np.iinfo(target_dtype)
        arr_float = np.clip(arr_float, info.min, info.max)
    return arr_float.astype(target_dtype)


def round_rshift(value: np.ndarray, shift: int) -> np.ndarray:
    """Rounded arithmetic right shift (positive ``shift``) or plain left shift
    (negative ``shift``). Narrow integer inputs are promoted to ``int32``
    internally to avoid overflow in ``abs(value) + half``."""
    if shift == 0:
        return value.copy()
    if shift > 0:
        half = 1 << (shift - 1)
        # promote narrow integer types to avoid abs() + half overflowing in-place
        if np.issubdtype(value.dtype, np.integer) and value.dtype.itemsize < 4:
            promoted = value.astype(np.int32)
        else:
            promoted = value
        ret = (np.abs(promoted) + half) >> shift
        return np.copysign(ret, promoted).astype(value.dtype)
    return value << -shift


def gaussian_down_sample(
    arr: np.ndarray, out_size: Tuple[int, int], kernel: np.ndarray = None, cyclic_y: bool = True
) -> np.ndarray:
    """Downsample ``arr`` to ``out_size`` using a custom (or default 5x5) low-pass
    kernel. The X axis is always padded with edge replication. The Y axis is
    padded cyclically when ``cyclic_y`` is True (default) and with edge
    replication otherwise."""
    # use default 5x5 kernel if not set
    if kernel is None:
        kernel = _DEFAULT_GAUSSIAN_KERNEL

    if arr.ndim != 2:
        raise ValueError("gaussian_down_sample expects a 2D array.")
    H, W = arr.shape
    out_rows, out_cols = out_size
    if out_rows <= 0 or out_cols <= 0:
        raise ValueError("out_size must contain positive dimensions.")
    kh, kw = kernel.shape
    if kh % 2 == 0 or kw % 2 == 0:
        raise ValueError("Kernel size must be odd for centered sampling.")

    # scale factor
    scale_h = H / out_rows
    scale_w = W / out_cols

    dst = np.zeros((out_rows, out_cols), dtype=np.float32)

    # do downsample
    for y in range(out_rows):
        center_y = (y + 0.5) * scale_h - 0.5
        start_y = int(np.floor(center_y - kh // 2))

        for x in range(out_cols):
            center_x = (x + 0.5) * scale_w - 0.5
            start_x = int(np.floor(center_x - kw // 2))

            # apply filter
            conv_sum = 0.0
            for ky in range(kh):
                if cyclic_y:
                    src_y = (start_y + ky + H) % H
                else:
                    src_y = np.clip(start_y + ky, 0, H - 1)
                for kx in range(kw):
                    src_x = np.clip(start_x + kx, 0, W - 1)  # replicate along width
                    conv_sum += arr[src_y, src_x] * kernel[ky, kx]

            # ``kernel.sum()`` is invariant of the padding mode used here:
            # cyclic wraps weights without dropping them, replicate only reuses
            # weights at the border instead of dropping them.
            kernel_sum = float(kernel.sum())
            if kernel_sum > 0:
                dst[y, x] = conv_sum / kernel_sum
            else:
                dst[y, x] = 0

    return dst


def linear_resize_array_1d(arr: np.ndarray, new_length: int) -> np.ndarray:
    """Linear-interpolation resize for 1D arrays. Delegates to the 2D path so
    interpolation rules and dtype handling stay in a single place."""
    if arr.size == 0:
        raise ValueError("Empty 1D array input!")
    if new_length <= 0:
        raise ValueError("new_length must be positive.")
    new_mat = linear_resize_array_2d(arr.reshape(1, -1), 1, new_length)
    return new_mat.reshape(-1)


def linear_resize_array_2d(mat: np.ndarray, new_rows: int, new_cols: int, kernel: np.ndarray = None) -> np.ndarray:
    """Resize a 2D array. Scale-up uses bilinear, scale-down uses either the
    provided custom ``kernel`` or OpenCV's area interpolation. Integer-typed
    outputs are clipped to the dtype range to avoid wrap-around."""
    if mat.size == 0 or mat.shape[0] == 0 or mat.shape[1] == 0:
        raise ValueError("Invalid 2D array input!")
    if new_rows <= 0 or new_cols <= 0:
        raise ValueError("new_rows and new_cols must be positive.")

    old_rows, old_cols = mat.shape
    if old_rows == new_rows and old_cols == new_cols:
        return mat.copy()

    src = mat.astype(np.float32)
    if new_cols * new_rows > old_rows * old_cols:
        # scale up, use bilinear interpolation
        new_mat = cv2.resize(src, (new_cols, new_rows), interpolation=cv2.INTER_LINEAR)
    elif kernel is not None:
        # use custom filter kernel for scale-down
        new_mat = gaussian_down_sample(src, (new_rows, new_cols), kernel)
    else:
        # use AREA interpolation (ONLY support uint8, uint16, float32)
        new_mat = cv2.resize(src, (new_cols, new_rows), interpolation=cv2.INTER_AREA)

    return _clip_cast(new_mat, mat.dtype)


def bicubic_resize_array_1d(arr: np.ndarray, new_length: int) -> np.ndarray:
    """Bicubic resize for 1D array, goes through 2D path."""
    if arr.size == 0:
        raise ValueError("Empty 1D array input!")
    if new_length <= 0:
        raise ValueError("new_length must be positive.")
    new_mat = bicubic_resize_array_2d(arr.reshape(1, -1), 1, new_length)
    return new_mat.reshape(-1)


def bicubic_resize_array_2d(mat: np.ndarray, new_rows: int, new_cols: int, kernel: np.ndarray = None) -> np.ndarray:
    """Resize a 2D array. Scale-up uses bicubic; scale-down uses either the
    provided custom ``kernel`` or OpenCV's area interpolation (bicubic causes
    aliasing when reducing resolution). Integer-typed outputs are clipped to
    the dtype range to avoid wrap-around. A non-None ``kernel`` is ignored
    during scale-up (a warning is emitted)."""
    if mat.size == 0 or mat.shape[0] == 0 or mat.shape[1] == 0:
        raise ValueError("Invalid 2D array input!")
    if new_rows <= 0 or new_cols <= 0:
        raise ValueError("new_rows and new_cols must be positive.")

    old_rows, old_cols = mat.shape
    if old_rows == new_rows and old_cols == new_cols:
        return mat.copy()

    src = mat.astype(np.float32)
    if new_cols * new_rows > old_rows * old_cols:  # scale up
        if kernel is not None:
            warnings.warn("bicubic_resize_array_2d: kernel is ignored for scale-up.", stacklevel=2)
        new_mat = cv2.resize(src, (new_cols, new_rows), interpolation=cv2.INTER_CUBIC)
    elif kernel is not None:  # scale down
        new_mat = gaussian_down_sample(src, (new_rows, new_cols), kernel)
    else:
        new_mat = cv2.resize(src, (new_cols, new_rows), interpolation=cv2.INTER_AREA)

    return _clip_cast(new_mat, mat.dtype)


# ---------------------------------------------------------------------------
# LUT slot names (kept in sync between default and current sets)
# ---------------------------------------------------------------------------
LUT_1D_NAMES = ("delta_ybyh", "delta_sbyh", "delta_hbyh")
LUT_2D_Y_NAMES = ("gain_ybyy", "gain_sbyy", "gain_hbyy")  # 2D LUTs along Y axis
LUT_2D_S_NAMES = ("gain_ybys", "gain_sbys", "gain_hbys")  # 2D LUTs along S axis
LUT_2D_NAMES = LUT_2D_Y_NAMES + LUT_2D_S_NAMES


# ---------------------------------------------------------------------------
# LUT length boundaries
# ---------------------------------------------------------------------------
ACM_LEN_Y_MIN = 3
ACM_LEN_Y_MAX = 256
ACM_LEN_S_MIN = 3
ACM_LEN_S_MAX = 182
ACM_LEN_H_MIN = 3
ACM_LEN_H_MAX = 360
ACM_LEN_HD_MIN = 3

# ---------------------------------------------------------------------------
# LUT value ranges
# ---------------------------------------------------------------------------
ACM_DELTA_Y_MIN = -255
ACM_DELTA_Y_MAX = 255
ACM_DELTA_S_MIN = -255
ACM_DELTA_S_MAX = 255
ACM_DELTA_H_MIN = -64
ACM_DELTA_H_MAX = 64

# 2D gain values (stored as int8)
ACM_GAIN_MIN = -128
ACM_GAIN_MAX = 127

# HSV path thresholds (mirror pq_acm.cl)
ACM_HSV_GRAY_THRESHOLD_S = 0.02  # ~5/255, treat as gray when saturation is below this
ACM_HSV_EPSILON_S = 1.0 / 1023.0  # used to avoid div-by-zero / false-color in H/S

# full data ranges used for LUT index mapping
ACM_Y_FULL_RANGE = 255
ACM_S_FULL_RANGE = 181
ACM_H_FULL_RANGE = 360


# ---------------------------------------------------------------------------
# AcmImplBase
# ---------------------------------------------------------------------------
class AcmImplBase:
    """Base class for ACM implementations.

    Maintains two sets of LUT length configuration and two sets of LUT data:
      * default: configured at construction time, treated as the canonical
        resolution.  ``load_json`` / ``gen_test_config`` / ``dump_json`` all
        operate on this set.
      * current: runtime resolution used by ``do_acm_*``.  Derived from the
        default set via resampling whenever ``set_len`` is called.

    Also supports runtime switching of:
      * delta_range: 3-tuple (y:float, s:float, h:int) -- max absolute delta
        per channel. h is in degrees; converted to radians in do_acm.
      * YUV <-> YHS conversion method (trig or cordic)
      * clip strategy for out-of-range pixel handling
    """

    # valid clip strategies
    _CLIP_TYPES = ("easy_clip", "radial_clip", "luma_clip")

    def __init__(
        self,
        len_y: int = 9,
        len_s: int = 13,
        len_h: int = 65,
        len_hd: int = 0,
        delta_range: Tuple[float, float, int] = (0.25, 0.25, 64),
        use_cordic: bool = False,
        is_lut4rgb: bool = False,
        clip_type: str = "easy_clip",
    ):
        # --- mode / method ---
        if isinstance(delta_range, (int, float)):
            delta_range = (float(delta_range), float(delta_range), 64)
        assert len(delta_range) == 3, f"delta_range must be a 3-tuple (y, s, h), got {delta_range}"
        dy, ds, dh = delta_range
        assert dy > 0 and ds > 0 and dh > 0, f"delta_range elements must be > 0, got {delta_range}"
        assert isinstance(dh, int), f"delta_range.h must be int (degrees), got {type(dh)}"
        assert clip_type in self._CLIP_TYPES, f"unknown clip_type: {clip_type}"
        self.delta_range = (float(dy), float(ds), int(dh))
        self.use_cordic = use_cordic
        self.is_lut4rgb = is_lut4rgb
        self.clip_type = clip_type
        self.ignore_gain_luts = False

        # --- gains ---
        self.gain_y = 256  # [0, (256), 1023], 8bit fixed
        self.gain_s = 256
        self.gain_h = 256
        self.offset_wr = 256
        self.offset_wg = 256
        self.offset_wb = 256

        self.rand_seed = -1
        self.b_lut_ready = False

        self._init_lens(len_y, len_s, len_h, len_hd)
        self._init_luts()

        self._print_len("default", self._default_len_y, self._default_len_s, self._default_len_h, self._default_len_hd)
        self._print_len("current", self.len_y, self.len_s, self.len_h, self.len_hd)
        print(
            f"[ACM] delta_range: (y={self.delta_range[0]}, s={self.delta_range[1]}, h={self.delta_range[2]}), "
            f"use_cordic: {self.use_cordic}, clip_type: {self.clip_type}"
        )

    # ------------------------------------------------------------------
    # length / LUT init helpers
    # ------------------------------------------------------------------
    def _init_lens(self, len_y: int, len_s: int, len_h: int, len_hd: int = 0) -> None:
        # --- default length config (canonical) ---
        self._default_len_y = utl.clamp(len_y, ACM_LEN_Y_MIN, ACM_LEN_Y_MAX)
        self._default_len_s = utl.clamp(len_s, ACM_LEN_S_MIN, ACM_LEN_S_MAX)
        self._default_len_h = utl.clamp(len_h, ACM_LEN_H_MIN, ACM_LEN_H_MAX)
        self._default_len_hd = (
            self._default_len_h if len_hd <= 0 else utl.clamp(len_hd, ACM_LEN_H_MIN, self._default_len_h)
        )

        # --- current length config (runtime, may be resampled) ---
        self.len_y = self._default_len_y
        self.len_s = self._default_len_s
        self.len_h = self._default_len_h
        self.len_hd = self._default_len_hd

    def _init_luts(self) -> None:
        self._default_lut_delta_ybyh = np.zeros(self._default_len_h, dtype=np.int16)
        self._default_lut_delta_sbyh = np.zeros(self._default_len_h, dtype=np.int16)
        self._default_lut_delta_hbyh = np.zeros(self._default_len_h, dtype=np.int16)
        self.lut_delta_ybyh = self._default_lut_delta_ybyh.copy()
        self.lut_delta_sbyh = self._default_lut_delta_sbyh.copy()
        self.lut_delta_hbyh = self._default_lut_delta_hbyh.copy()

        for name in LUT_2D_Y_NAMES:
            setattr(
                self, f"_default_lut_{name}", np.ones((self._default_len_y, self._default_len_hd), dtype=np.int8) * 127
            )
            setattr(self, f"lut_{name}", getattr(self, f"_default_lut_{name}").copy())
        for name in LUT_2D_S_NAMES:
            setattr(
                self, f"_default_lut_{name}", np.ones((self._default_len_s, self._default_len_hd), dtype=np.int8) * 127
            )
            setattr(self, f"lut_{name}", getattr(self, f"_default_lut_{name}").copy())
        self.b_lut_ready = True

    @staticmethod
    def _print_len(tag: str, y: int, s: int, h: int, hd: int) -> None:
        print(f"[ACM] {tag} lut len: y={y}, s={s}, h={h}, hd={hd}")

    # ------------------------------------------------------------------
    # public configuration setters
    # ------------------------------------------------------------------
    def set_len(self, len_y: int, len_s: int, len_h: int, len_hd: int = 0, kernel: np.ndarray = None) -> None:
        """Change current LUT length. Resamples from default set using bicubic."""
        self.len_y = utl.clamp(len_y, ACM_LEN_Y_MIN, ACM_LEN_Y_MAX)
        self.len_s = utl.clamp(len_s, ACM_LEN_S_MIN, ACM_LEN_S_MAX)
        self.len_h = utl.clamp(len_h, ACM_LEN_H_MIN, ACM_LEN_H_MAX)
        self.len_hd = self.len_h if len_hd <= 0 else utl.clamp(len_hd, ACM_LEN_HD_MIN, self.len_h)

        print(f"[ACM] set current lut len: y={self.len_y}, s={self.len_s}, h={self.len_h}, hd={self.len_hd}")
        self._resample_default_to_current(kernel, method="bicubic")

    def set_step(
        self, step_y: float, step_s: float, step_h: float, step_h2: float = 0.0, kernel: np.ndarray = None
    ) -> None:
        step_y = utl.clamp(step_y, 1.0, ACM_Y_FULL_RANGE / (ACM_LEN_Y_MIN - 1))
        step_s = utl.clamp(step_s, 1.0, ACM_S_FULL_RANGE / (ACM_LEN_S_MIN - 1))
        step_h = utl.clamp(step_h, 1.0, ACM_H_FULL_RANGE / (ACM_LEN_H_MIN - 1))
        step_hd = step_h if step_h2 <= 0.0 else min(ACM_H_FULL_RANGE / (ACM_LEN_H_MIN - 1), max(step_h2, step_h))
        self.len_y = round(ACM_Y_FULL_RANGE / step_y) + 1
        self.len_s = round(ACM_S_FULL_RANGE / step_s) + 1
        self.len_h = round(ACM_H_FULL_RANGE / step_h) + 1
        self.len_hd = round(ACM_H_FULL_RANGE / step_hd) + 1
        print(f"[ACM] set current lut step: y={step_y:.2f}, s={step_s:.2f}, h={step_h:. f}, hd={step_hd:.4f}")
        self._print_len("current", self.len_y, self.len_s, self.len_h, self.len_hd)
        self._resample_default_to_current(kernel, method="bicubic")

    def set_global_gains(self, gain_y: int, gain_s: int, gain_h: int) -> None:
        self.gain_y = gain_y
        self.gain_s = gain_s
        self.gain_h = gain_h
        print(f"[ACM] set global gains: y={self.gain_y}, s={self.gain_s}, h={self.gain_h}")

    def set_wrgb_offset(self, wr_offset: int, wg_offset: int, wb_offset: int) -> None:
        self.offset_wr = wr_offset
        self.offset_wg = wg_offset
        self.offset_wb = wb_offset
        print(f"[ACM] set wrgb offset: wr={self.offset_wr}, wg={self.offset_wg}, wb={self.offset_wb}")

    def set_delta_range(self, value) -> None:
        """Set the max absolute delta tuple (y:float, s:float, h:int).

        Accepts a single float (applied to y and s, h defaults to 64)
        or a 3-tuple (y, s, h). h is in degrees.
        """
        if isinstance(value, (int, float)):
            value = (float(value), float(value), 64)
        dy, ds, dh = value
        if dy <= 0 or ds <= 0 or dh <= 0:
            raise ValueError(f"delta_range elements must be > 0, got {value}")
        if not isinstance(dh, int):
            raise ValueError(f"delta_range.h must be int (degrees), got {type(dh)}")
        self.delta_range = (float(dy), float(ds), int(dh))
        print(f"[ACM] set delta_range: (y={self.delta_range[0]}, s={self.delta_range[1]}, h={self.delta_range[2]})")

    def set_use_cordic(self, value: bool) -> None:
        """Switch YUV<=>YHS conversion between trig (False) and cordic (True)."""
        self.use_cordic = value
        print(f"[ACM] set use_cordic: {self.use_cordic}")

    # ------------------------------------------------------------------
    # resampling between default <-> current
    # ------------------------------------------------------------------
    def _resample_default_to_current(self, kernel: np.ndarray = None, method: str = "bicubic") -> None:
        """Resample default LUTs into the current length config."""
        resample_1d = bicubic_resize_array_1d if method == "bicubic" else linear_resize_array_1d
        resample_2d = bicubic_resize_array_2d if method == "bicubic" else linear_resize_array_2d

        if self._default_lut_delta_ybyh.shape[0] != self.len_h:
            self.lut_delta_ybyh = np.clip(
                resample_1d(self._default_lut_delta_ybyh, self.len_h), ACM_DELTA_Y_MIN, ACM_DELTA_Y_MAX
            ).astype(np.int16)
            self.lut_delta_sbyh = np.clip(
                resample_1d(self._default_lut_delta_sbyh, self.len_h), ACM_DELTA_S_MIN, ACM_DELTA_S_MAX
            ).astype(np.int16)
            self.lut_delta_hbyh = np.clip(
                resample_1d(self._default_lut_delta_hbyh, self.len_h), ACM_DELTA_H_MIN, ACM_DELTA_H_MAX
            ).astype(np.int16)
            print(f"[ACM] resample delta LUT: {self._default_len_h} => {self.len_h} ({method})")
        else:
            self.lut_delta_ybyh = self._default_lut_delta_ybyh.copy()
            self.lut_delta_sbyh = self._default_lut_delta_sbyh.copy()
            self.lut_delta_hbyh = self._default_lut_delta_hbyh.copy()

        for name in LUT_2D_Y_NAMES:
            default_lut = getattr(self, f"_default_lut_{name}")
            if default_lut.shape != (self.len_y, self.len_hd):
                new_lut = resample_2d(default_lut, self.len_y, self.len_hd, kernel)
                setattr(self, f"lut_{name}", new_lut)
                print(f"[ACM] resample {name}: {default_lut.shape} => {new_lut.shape} ({method})")
            else:
                setattr(self, f"lut_{name}", default_lut.copy())
        for name in LUT_2D_S_NAMES:
            default_lut = getattr(self, f"_default_lut_{name}")
            if default_lut.shape != (self.len_s, self.len_hd):
                new_lut = resample_2d(default_lut, self.len_s, self.len_hd, kernel)
                setattr(self, f"lut_{name}", new_lut)
                print(f"[ACM] resample {name}: {default_lut.shape} => {new_lut.shape} ({method})")
            else:
                setattr(self, f"lut_{name}", default_lut.copy())

    def sync_to_default(self) -> None:
        """Resample current LUTs back to the default length config.

        Useful when the user has edited the current LUTs in-place at a custom
        resolution and wants to promote those changes to the default set.
        Uses bicubic interpolation to preserve the shape of edits.
        """
        # 1D delta LUTs
        if self._default_lut_delta_ybyh.shape[0] != self.lut_delta_ybyh.shape[0]:
            self._default_lut_delta_ybyh = np.clip(
                bicubic_resize_array_1d(self.lut_delta_ybyh, self._default_len_h), ACM_DELTA_Y_MIN, ACM_DELTA_Y_MAX
            ).astype(np.int16)
            self._default_lut_delta_sbyh = np.clip(
                bicubic_resize_array_1d(self.lut_delta_sbyh, self._default_len_h), ACM_DELTA_S_MIN, ACM_DELTA_S_MAX
            ).astype(np.int16)
            self._default_lut_delta_hbyh = np.clip(
                bicubic_resize_array_1d(self.lut_delta_hbyh, self._default_len_h), ACM_DELTA_H_MIN, ACM_DELTA_H_MAX
            ).astype(np.int16)
            print(f"[ACM] sync delta LUT to default: {self.lut_delta_ybyh.shape[0]} " f"=> {self._default_len_h}")
        else:
            self._default_lut_delta_ybyh = self.lut_delta_ybyh.copy()
            self._default_lut_delta_sbyh = self.lut_delta_sbyh.copy()
            self._default_lut_delta_hbyh = self.lut_delta_hbyh.copy()

        # 2D gain LUTs
        for name in LUT_2D_Y_NAMES:
            current = getattr(self, f"lut_{name}")
            default_lut = getattr(self, f"_default_lut_{name}")
            if current.shape != default_lut.shape:
                setattr(
                    self,
                    f"_default_lut_{name}",
                    bicubic_resize_array_2d(current, default_lut.shape[0], default_lut.shape[1]),
                )
            else:
                setattr(self, f"_default_lut_{name}", current.copy())
        for name in LUT_2D_S_NAMES:
            current = getattr(self, f"lut_{name}")
            default_lut = getattr(self, f"_default_lut_{name}")
            if current.shape != default_lut.shape:
                setattr(
                    self,
                    f"_default_lut_{name}",
                    bicubic_resize_array_2d(current, default_lut.shape[0], default_lut.shape[1]),
                )
            else:
                setattr(self, f"_default_lut_{name}", current.copy())

    # ------------------------------------------------------------------
    # ACM processing
    # ------------------------------------------------------------------
    def do_acm_u8(self, planar_data: np.ndarray, isRgb: bool = False, use_cordic: Optional[bool] = None) -> np.ndarray:
        """Apply ACM to an 8bit YUV444p image. Returns YUV444p uint8."""
        print(f"[ACM] doing ACM LUT for u8 {'rgb' if isRgb else 'yuv'} image...")
        if use_cordic is None:
            use_cordic = self.use_cordic

        if isRgb and self.is_lut4rgb:
            data_out = self._do_acm_rgb(planar_data, range=256)
        else:
            data_out = self._do_acm_yuv(planar_data, depth=8, use_cordic=use_cordic)
        print(f"[ACM] do ACM LUT for u8 {'rgb' if isRgb else 'yuv'} image done.")
        return data_out

    def do_acm_u10(self, planar_data: np.ndarray, isRgb: bool = False, use_cordic: Optional[bool] = None) -> np.ndarray:
        """Apply ACM to a 10bit YUV444p image. Returns YUV444p uint16.

        10bit convention: full range [0, 1023], Cb/Cr center 512, S range
        [0, 724].  The LUT is stored in the 8bit reference domain; ``_do_acm``
        re-scales delta_y by ``y_max / Y_FULL_RANGE`` and delta_s by
        ``s_max / S_FULL_RANGE`` so that the LUT entry semantics carry over
        consistently across bit depths (1x LUT value = 1x of the current
        input range, then multiplied by ``scl`` from the delta mode).
        """
        print(f"[ACM] doing ACM LUT for u10 {'rgb' if isRgb else 'yuv'} image...")
        assert planar_data.dtype == np.uint16, "do_acm_u10 expects uint16 input"
        if use_cordic is None:
            use_cordic = self.use_cordic

        if isRgb and self.is_lut4rgb:
            data_out = self._do_acm_rgb(planar_data, range=1024)
        else:
            data_out = self._do_acm_yuv(planar_data, depth=10, use_cordic=use_cordic)
        print(f"[ACM] do ACM LUT for u10 {'rgb' if isRgb else 'yuv'} image done.")
        return data_out

    def _do_acm_yuv(self, planar_data: np.ndarray, depth: int, use_cordic: bool) -> np.ndarray:  # 8/10
        """Core ACM LUT pipeline (YUV path).

        All computation is performed in normalised float:
          * y_f, s_f, h_f  in [0, 1]  (h_f maps linearly 0→0°, 1→360°)
        LUT tables are pre-converted to normalised float with gain and
        delta_range applied, so the remap outputs are directly usable as
        additive deltas (fraction of full-scale for Y/S, degrees for H).
        """
        if depth == 10:
            y_max = 1023
            cbcr_center = 512
            s_max = 724 if self.clip_type == 'easy_clip' else 511
        else:
            y_max = 255
            cbcr_center = 128
            s_max = 181 if self.clip_type == 'easy_clip' else 127

        # ---- 1. do yuv2yhs ----
        y = planar_data[0].astype(np.int32)  # [0,255]/[0,1023]
        cb = planar_data[1].astype(np.int32) - cbcr_center  # [-128,127]/[-512,511]
        cr = planar_data[2].astype(np.int32) - cbcr_center  # [-128,127]/[-512,511]

        if use_cordic:
            h_deg, s, _, _ = cordic.cordic_cbcr2hs(cb, cr, depth, 13, 6, False)  # h:[-180, 180], s:[0,181]/[0,724]
            h_rad = np.deg2rad(h_deg)  # [-pi, pi]
        else:
            s = np.rint(np.sqrt(cb * cb + cr * cr)).astype(np.int32)  # [0,181]/[0,724]
            h_rad = np.arctan2(cr, cb)  # [-pi, pi]
            h_deg = np.rint(np.rad2deg(h_rad)).astype(np.int32)  # [-180, 180]

        # ---- 2. Normalise LUT tables (apply gain & delta_range upfront) ----
        g_y = self.gain_y / 256.0
        g_s = self.gain_s / 256.0
        g_h = self.gain_h / 256.0
        dr_y, dr_s, dr_h = self.delta_range  # (0.25, 0.25, 64) or (1.0, 1.0, 64)
        lut_dy = np.clip(self.lut_delta_ybyh.astype(np.float32) / ACM_DELTA_Y_MAX * g_y * dr_y, -dr_y, dr_y)
        lut_ds = np.clip(self.lut_delta_sbyh.astype(np.float32) / ACM_DELTA_S_MAX * g_s * dr_s, -dr_s, dr_s)
        lut_dh = np.clip(self.lut_delta_hbyh.astype(np.float32) / ACM_DELTA_H_MAX * g_h * dr_h, -dr_h, dr_h)
        lut_gy_y = np.clip(self.lut_gain_ybyy.astype(np.float32) / 127.0, -1.0, 1.0)
        lut_gs_y = np.clip(self.lut_gain_sbyy.astype(np.float32) / 127.0, -1.0, 1.0)
        lut_gh_y = np.clip(self.lut_gain_hbyy.astype(np.float32) / 127.0, -1.0, 1.0)
        lut_gy_s = np.clip(self.lut_gain_ybys.astype(np.float32) / 127.0, -1.0, 1.0)
        lut_gs_s = np.clip(self.lut_gain_sbys.astype(np.float32) / 127.0, -1.0, 1.0)
        lut_gh_s = np.clip(self.lut_gain_hbys.astype(np.float32) / 127.0, -1.0, 1.0)

        # ---- 3. Compute remap indices ----
        y_f = y.astype(np.float32) / y_max
        s_f = np.minimum(s.astype(np.float32) / s_max, 1.0)
        h_f = ((h_rad + np.pi) / (2.0 * np.pi)).astype(np.float32)
        idx_y = y_f * (self.len_y - 1)
        idx_s = s_f * (self.len_s - 1)
        idx_h = h_f * (self.len_h - 1)
        idx_hd = h_f * (self.len_hd - 1)
        idx_zeros = np.zeros_like(idx_h)

        # ---- 4. Sample delta tables (1D, indexed by H) → additive deltas ----
        lut_dy = lut_dy.reshape(1, -1) # need to reshape to (1, len_h) for cv2.remap
        lut_ds = lut_ds.reshape(1, -1)
        lut_dh = lut_dh.reshape(1, -1)
        delta_y = cv2.remap(lut_dy, idx_h, idx_zeros, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        delta_s = cv2.remap(lut_ds, idx_h, idx_zeros, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        delta_h = cv2.remap(
            lut_dh, idx_h, idx_zeros, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE
        )  # [-64, 64]

        # ---- 5. Sample gain tables (2D, indexed by (Y/S, HD)) ----
        if self.ignore_gain_luts:
            gain_yy = np.ones_like(delta_y, dtype=np.float32)
            gain_sy = np.ones_like(delta_s, dtype=np.float32)
            gain_hy = np.ones_like(delta_h, dtype=np.float32)
            gain_ys = np.ones_like(delta_y, dtype=np.float32)
            gain_ss = np.ones_like(delta_s, dtype=np.float32)
            gain_hs = np.ones_like(delta_h, dtype=np.float32)
        else:
            gain_yy = cv2.remap(
                lut_gy_y, idx_hd, idx_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE
            )
            gain_sy = cv2.remap(
                lut_gs_y, idx_hd, idx_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE
            )
            gain_hy = cv2.remap(
                lut_gh_y, idx_hd, idx_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE
            )
            gain_ys = cv2.remap(
                lut_gy_s, idx_hd, idx_s, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE
            )
            gain_ss = cv2.remap(
                lut_gs_s, idx_hd, idx_s, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE
            )
            gain_hs = cv2.remap(
                lut_gh_s, idx_hd, idx_s, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE
            )


        # ---- 5b. Save raw intermediate values for UI inspection ----
        self._last_delta_y_raw = delta_y.copy()
        self._last_delta_s_raw = delta_s.copy()
        self._last_delta_h_raw = delta_h.copy()
        self._last_gain_yy = gain_yy.copy()
        self._last_gain_ys = gain_ys.copy()
        self._last_gain_sy = gain_sy.copy()
        self._last_gain_ss = gain_ss.copy()
        self._last_gain_hy = gain_hy.copy()
        self._last_gain_hs = gain_hs.copy()
        self._last_intermediate_shape = delta_y.shape

        # ---- 6. Combine deltas (all in normalised float) ----
        delta_y = delta_y * gain_yy * gain_ys  # [-dr_y, dr_y]
        delta_s = delta_s * gain_sy * gain_ss  # [-dr_s, dr_s]
        delta_h = delta_h * gain_hy * gain_hs  # [-dr_h, dr_h]
        delta_s = np.where(s_f < 1.0/s_max, 0.0, delta_s)
        delta_h = np.where(s_f < 1.0/s_max, 0.0, delta_h)
        self._final_delta_y = delta_y.copy()
        self._final_delta_s = delta_s.copy()
        self._final_delta_h = delta_h.copy()

        # ---- 7. Apply to normalised values ----
        h_deg_new = np.mod(h_deg + delta_h, 360.0) # [0, 360]
        if self.clip_type == "luma_clip":
            y_new = np.clip(y_f + delta_y, 0.0, 1.0)
            s_new, s_max_old, s_max_new = self._sat_adjust_triangle(y_f, h_deg, s_f, y_new, h_deg_new)
            s_f = np.clip(s_new + delta_s * s_max_new, 0.0, s_max_new)
            y_f = y_new
        else:
            y_f = np.clip(y_f + delta_y, 0.0, 1.0)
            s_f = np.clip(s_f + delta_s, 0.0, 1.0)

        # ---- 8. Convert back to integer pixel domain ----
        s_pix_f = s_f * s_max
        if use_cordic:
            s_pix = np.rint(s_pix_f).astype(np.int32)
            cb, cr = cordic.cordic_hs2cbcr(h_deg_new, s_pix, 8, depth, depth, 13, 6)
        else:
            new_rad = np.deg2rad(h_deg_new)
            new_cb = s_pix_f * np.cos(new_rad)
            new_cr = s_pix_f * np.sin(new_rad)
            cb = np.rint(new_cb).astype(np.int32)
            cr = np.rint(new_cr).astype(np.int32)

        # ---- 9. Final clip ----
        y_out = np.rint(y_f * y_max).astype(np.int32)

        out_dtype = np.uint8 if depth == 8 else np.uint16
        yuv444p_out = np.empty((3, y.shape[0], y.shape[1]), dtype=out_dtype)
        yuv444p_out[0, :, :] = np.clip(y_out, 0, y_max).astype(out_dtype)
        yuv444p_out[1, :, :] = np.clip(cb + cbcr_center, 0, y_max).astype(out_dtype)
        yuv444p_out[2, :, :] = np.clip(cr + cbcr_center, 0, y_max).astype(out_dtype)
        return yuv444p_out  # [C, H, W] planar

    def _do_acm_rgb(self, planar_data: np.ndarray, range: int) -> np.ndarray:
        """Apply ACM via the HSV path on a full-range RGB image.

        Mirrors ``clkernel_lut4rgb_img2img_2x2`` + ``getFinalDeltaRgb`` in
        ``pq_acm.cl``.  Input is expected in the full-range domain
        ([0, range-1]); limited-range handling is the caller's responsibility
        since the current Python pipeline does not pass that flag here.

        For pixels whose saturation is below ``GRAY_THRESHOLD_S`` the LUT is
        bypassed: the configured RGB offset is applied directly and that
        pixel is taken as the final result.
        """
        y_max = float(range - 1)
        h_max = 360.0

        # ---- 1. Normalize to full-range [0, 1] ----
        rgb_f = planar_data.astype(np.float32) / y_max
        r = rgb_f[:, :, 0]
        g = rgb_f[:, :, 1]
        b = rgb_f[:, :, 2]
        v = np.max(rgb_f, axis=2)
        m = np.min(rgb_f, axis=2)
        delta_val = v - m

        # ---- 2. Gray mask: bypass LUT, apply RGB offset directly ----
        is_gray = delta_val < ACM_HSV_GRAY_THRESHOLD_S
        # Map stored offset (centered at 256, span 256) to CL's [-0.5, +0.5] domain.
        rgb_offset = np.array(
            [(self.offset_wr - 256) / 512.0, (self.offset_wg - 256) / 512.0, (self.offset_wb - 256) / 512.0],
            dtype=np.float32,
        )
        r_gray = np.clip(r + rgb_offset[0], 0.0, 1.0)
        g_gray = np.clip(g + rgb_offset[1], 0.0, 1.0)
        b_gray = np.clip(b + rgb_offset[2], 0.0, 1.0)

        # ---- 3. Compute hue for non-gray pixels ----
        # Use argmax to identify the dominant channel robustly under float math.
        max_idx = np.argmax(rgb_f, axis=2)
        delta_safe = np.where(delta_val > 0, delta_val, 1.0)
        cond_r = (max_idx == 0) & (delta_val > 0)
        cond_g = (max_idx == 1) & (delta_val > 0)
        cond_b = (max_idx == 2) & (delta_val > 0)
        h = np.zeros_like(v)
        h = np.where(cond_r, (g - b) / delta_safe, h)
        h = np.where(cond_g, (b - r) / delta_safe + 2.0, h)
        h = np.where(cond_b, (r - g) / delta_safe + 4.0, h)
        h *= 60.0
        h = np.where(h < 0.0, h + 360.0, h)
        h = np.where(is_gray, 0.0, h)
        s = np.where(v > 0.0, delta_val / np.maximum(v, ACM_HSV_EPSILON_S), 0.0)
        s = np.where(is_gray, 0.0, s)

        # ---- 4. Normalise LUT tables (apply gain & delta_range upfront) ----
        g_y = self.gain_y / 256.0
        g_s = self.gain_s / 256.0
        g_h = self.gain_h / 256.0
        dr_y, dr_s, dr_h = self.delta_range
        lut_dy = self.lut_delta_ybyh.astype(np.float32) / ACM_Y_FULL_RANGE * g_y * dr_y
        lut_ds = self.lut_delta_sbyh.astype(np.float32) / ACM_Y_FULL_RANGE * g_s * dr_s
        lut_dh = self.lut_delta_hbyh.astype(np.float32) / float(ACM_DELTA_H_MAX) * g_h * dr_h

        lut_g_yy = self.lut_gain_ybyy.astype(np.float32) / 127.0
        lut_g_ys = self.lut_gain_sbyy.astype(np.float32) / 127.0
        lut_g_yh = self.lut_gain_hbyy.astype(np.float32) / 127.0
        lut_g_sy = self.lut_gain_ybys.astype(np.float32) / 127.0
        lut_g_ss = self.lut_gain_sbys.astype(np.float32) / 127.0
        lut_g_sh = self.lut_gain_hbys.astype(np.float32) / 127.0

        # ---- 5. Compute LUT indices ----
        hp_deg = np.mod(h + 180.0, 360.0)
        idx_v = v * (self.len_y - 1)
        idx_s = s * (self.len_s - 1)
        idx_hp = hp_deg / h_max * (self.len_hd - 1)
        idx_zeros = np.zeros_like(idx_v)

        # ---- 6. Sample delta tables (1D LUTs indexed by H) ----
        lut_dy = lut_dy.reshape(1, -1) # need to reshape to (1, len_h) for cv2.remap
        lut_ds = lut_ds.reshape(1, -1)
        lut_dh = lut_dh.reshape(1, -1)
        delta_y = cv2.remap(lut_dy, idx_hp, idx_zeros, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        delta_s = cv2.remap(lut_ds, idx_hp, idx_zeros, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        delta_h = cv2.remap(lut_dh, idx_hp, idx_zeros, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)

        # ---- 7. Sample gain tables (2D LUTs indexed by (V,H) and (S,H)) ----
        if self.ignore_gain_luts:
            gain_yy = np.ones_like(delta_y, dtype=np.float32)
            gain_ys = np.ones_like(delta_s, dtype=np.float32)
            gain_yh = np.ones_like(delta_h, dtype=np.float32)
            gain_sy = np.ones_like(delta_y, dtype=np.float32)
            gain_ss = np.ones_like(delta_s, dtype=np.float32)
            gain_sh = np.ones_like(delta_h, dtype=np.float32)
        else:
            gain_yy = cv2.remap(
                lut_g_yy, idx_hp, idx_v, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE
            )
            gain_ys = cv2.remap(
                lut_g_ys, idx_hp, idx_v, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE
            )
            gain_yh = cv2.remap(
                lut_g_yh, idx_hp, idx_v, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE
            )
            gain_sy = cv2.remap(
                lut_g_sy, idx_hp, idx_s, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE
            )
            gain_ss = cv2.remap(
                lut_g_ss, idx_hp, idx_s, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE
            )
            gain_sh = cv2.remap(
                lut_g_sh, idx_hp, idx_s, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE
            )

        # ---- 8. Combine deltas ----
        delta_y = delta_y * gain_yy * gain_sy
        delta_s = delta_s * gain_ys * gain_ss
        delta_h = delta_h * gain_yh * gain_sh

        # ---- 9. Apply deltas to V, S, H ----
        v_new = np.clip(v + delta_y, 0.0, 1.0)
        s_new = np.clip(s + delta_s, 0.0, 1.0)
        h_new = np.mod(h + delta_h, 360.0)
        h_new = np.where(h_new < 0.0, h_new + 360.0, h_new)

        # ---- 10. HSV -> RGB for non-gray pixels ----
        hsv_new = np.stack([h_new, s_new, v_new], axis=2)
        rgb_new = cv2.cvtColor(hsv_new, cv2.COLOR_HSV2RGB)

        # ---- 11. Merge gray / non-gray paths ----
        r_out = np.where(is_gray, r_gray, rgb_new[:, :, 0])
        g_out = np.where(is_gray, g_gray, rgb_new[:, :, 1])
        b_out = np.where(is_gray, b_gray, rgb_new[:, :, 2])

        # ---- 13. Cast back to integer with full-range clipping ----
        rgb_out = np.empty_like(planar_data)
        rgb_out[:, :, 0] = np.clip(r_out * y_max, 0.0, y_max).astype(planar_data.dtype)
        rgb_out[:, :, 1] = np.clip(g_out * y_max, 0.0, y_max).astype(planar_data.dtype)
        rgb_out[:, :, 2] = np.clip(b_out * y_max, 0.0, y_max).astype(planar_data.dtype)
        return rgb_out.transpose(2, 0, 1)  # [C, H, W] planar

    def _calc_bt709_triangle_slopes(self, h_deg: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Blend the six BT709 region triangles and return lower/upper edge slopes."""
        h_norm = np.mod(h_deg.astype(np.float32), 360.0)
        h_ext = np.where(h_norm < _BT709_TRIANGLE_REGION_CENTERS_DEG[0], h_norm + 360.0, h_norm)
        idx = np.searchsorted(_BT709_TRIANGLE_REGION_CENTERS_DEG, h_ext, side="right") % 6
        center_pts = _BT709_TRIANGLE_REGION_PEAKS[idx]  # (s,y)
        # (s,y) -> (y,s)
        lower = center_pts[:, :, 0] / center_pts[:, :, 1]
        upper = center_pts[:, :, 0] / (1.0 - center_pts[:, :, 1])
        th = center_pts[:, : ,1]

        return lower.astype(np.float32), upper.astype(np.float32), th

    def _triangle_s_max_bt709(self, y_f: np.ndarray, h_deg: np.ndarray) -> np.ndarray:
        """Compute the BT709 luma-clip saturation limit for one Y/H slice."""
        y_clamped = np.clip(y_f.astype(np.float32), 0.0, 1.0)
        lower_slopes, upper_slopes, ths = self._calc_bt709_triangle_slopes(h_deg)
        s_max_lower = y_clamped * lower_slopes
        s_max_upper = (1.0 - y_clamped) * upper_slopes
        s_max = np.where(y_clamped <= ths, s_max_lower, s_max_upper)

        return s_max

    def _sat_adjust_triangle(
        self,
        y_f_old: np.ndarray,  # [0, 1]
        h_deg_old: np.ndarray,  # [0, 360]
        s_f_old: np.ndarray,  # [0, 1]
        y_f_new: np.ndarray,  # [0, 1]
        h_deg_new: np.ndarray,  # [0, 360]
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Project saturation between BT709 hue-weighted luma triangles."""
        s_max_old = self._triangle_s_max_bt709(y_f_old, h_deg_old)
        s_max_new = self._triangle_s_max_bt709(y_f_new, h_deg_new)
        s_f_old = np.minimum(s_f_old.astype(np.float32), s_max_old)
        with np.errstate(divide='ignore', invalid='ignore'):
            scale = np.divide(s_max_new, s_max_old, out=np.zeros_like(s_max_new, dtype=np.float32), where=s_max_old > 0)
        s_f_new = s_f_old * scale
        return s_f_new, s_max_old, s_max_new

    # ------------------------------------------------------------------
    # load_json / dump_json
    # ------------------------------------------------------------------
    def load_json(self, filename: str) -> bool:
        if not os.path.exists(filename):
            print(f"[ACM] config file '{filename}' doesn't exist!")
            return False
        if not filename.endswith(".json"):
            print(f"[ACM] config file '{filename}' is not a json file!")
            return False

        len_y = 9
        len_s = 13
        len_h = 65
        len_hd = 65
        lut2dAxis4HD = 1

        ## read json config
        try:
            with open(filename, "r") as f:
                print(f"[ACM] loading config from file: {filename} ...")
                data = json.load(f)
                if "pq_tuning_param" in data:
                    data = data["pq_tuning_param"]
                if "acm" in data:
                    data = data["acm"]

                lut_delta_ybyh = np.array(data["acmTableDeltaYbyH"], dtype=np.int16)
                lut_delta_sbyh = np.array(data["acmTableDeltaSbyH"], dtype=np.int16)
                lut_delta_hbyh = np.array(data["acmTableDeltaHbyH"], dtype=np.int16)
                lut_gain_ybyy = np.array(data["acmTableGainYbyY"], dtype=np.int8)
                lut_gain_sbyy = np.array(data["acmTableGainSbyY"], dtype=np.int8)
                lut_gain_hbyy = np.array(data["acmTableGainHbyY"], dtype=np.int8)
                lut_gain_ybys = np.array(data["acmTableGainYbyS"], dtype=np.int8)
                lut_gain_sbys = np.array(data["acmTableGainSbyS"], dtype=np.int8)
                lut_gain_hbys = np.array(data["acmTableGainHbyS"], dtype=np.int8)

                lut2dAxis4HD = data["lut2dAxis4HD"] if "lut2dAxis4HD" in data else 1

                self.gain_y = data["lumGain"] if "lumGain" in data else 256
                self.gain_s = data["satGain"] if "satGain" in data else 256
                self.gain_h = data["hueGain"] if "hueGain" in data else 256
                self.offset_wb = data["wbOffset"] if "wbOffset" in data else 256
                self.offset_wg = data["wgOffset"] if "wgOffset" in data else 256
                self.offset_wr = data["wrOffset"] if "wrOffset" in data else 256
                self.is_lut4rgb = bool(data["isLut4Rgb"]) if "isLut4Rgb" in data else False

                ## guess lut length from the file
                len_h = data["lutLengthH"] if "lutLengthH" in data else len(lut_delta_ybyh)
                if len(lut_gain_ybyy) == 65 * 9 and len(lut_gain_ybys) == 65 * 13:
                    len_y, len_s, len_hd = 9, 13, 65
                elif len(lut_gain_ybyy) == 17 * 9 and len(lut_gain_ybys) == 17 * 13:
                    len_y, len_s, len_hd = 9, 13, 17
                elif all(k in data for k in ("lutLengthY", "lutLengthS", "lutLengthHD")):
                    len_y = data["lutLengthY"]
                    len_s = data["lutLengthS"]
                    len_hd = data["lutLengthHD"]
                else:
                    print("WARNING: unknown len_y/s/hd !!! use default value.")

                if lut2dAxis4HD:
                    lut_gain_ybyy = lut_gain_ybyy.reshape(len_y, len_hd)
                    lut_gain_sbyy = lut_gain_sbyy.reshape(len_y, len_hd)
                    lut_gain_hbyy = lut_gain_hbyy.reshape(len_y, len_hd)
                    lut_gain_ybys = lut_gain_ybys.reshape(len_s, len_hd)
                    lut_gain_sbys = lut_gain_sbys.reshape(len_s, len_hd)
                    lut_gain_hbys = lut_gain_hbys.reshape(len_s, len_hd)
                else:
                    print(
                        f"[ACM] gain luts reshape to {len_y}/{len_s}(W) x {len_hd}(H) since lut2dAxis4HD={lut2dAxis4HD}"
                    )
                    lut_gain_ybyy = lut_gain_ybyy.reshape(len_hd, len_y).T
                    lut_gain_sbyy = lut_gain_sbyy.reshape(len_hd, len_y).T
                    lut_gain_hbyy = lut_gain_hbyy.reshape(len_hd, len_y).T
                    lut_gain_ybys = lut_gain_ybys.reshape(len_hd, len_s).T
                    lut_gain_sbys = lut_gain_sbys.reshape(len_hd, len_s).T
                    lut_gain_hbys = lut_gain_hbys.reshape(len_hd, len_s).T

        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)[-1]
            print(f"[ACM] load config '{filename}' failed in " f"'{os.path.basename(tb.filename)}'-{tb.lineno}: {e}")
            return False

        ## shape validations
        if len(lut_delta_ybyh) != len_h:
            raise ValueError(f"length of lut_delta_ybyh({len(lut_delta_ybyh)}) != len_h({len_h})!")
        if len(lut_delta_sbyh) != len_h:
            raise ValueError(f"length of lut_delta_sbyh({len(lut_delta_sbyh)}) != len_h({len_h})!")
        if len(lut_delta_hbyh) != len_h:
            raise ValueError(f"length of lut_delta_hbyh({len(lut_delta_hbyh)}) != len_h({len_h})!")
        if lut_gain_ybyy.shape != (len_y, len_hd):
            raise ValueError(f"shape of lut_gain_ybyy{lut_gain_ybyy.shape} != ({len_y}, {len_hd})!")
        if lut_gain_sbyy.shape != (len_y, len_hd):
            raise ValueError(f"shape of lut_gain_sbyy{lut_gain_sbyy.shape} != ({len_y}, {len_hd})!")
        if lut_gain_hbyy.shape != (len_y, len_hd):
            raise ValueError(f"shape of lut_gain_hbyy{lut_gain_hbyy.shape} != ({len_y}, {len_hd})!")
        if lut_gain_ybys.shape != (len_s, len_hd):
            raise ValueError(f"shape of lut_gain_ybys{lut_gain_ybys.shape} != ({len_s}, {len_hd})!")
        if lut_gain_sbys.shape != (len_s, len_hd):
            raise ValueError(f"shape of lut_gain_sbys{lut_gain_sbys.shape} != ({len_s}, {len_hd})!")
        if lut_gain_hbys.shape != (len_s, len_hd):
            raise ValueError(f"shape of lut_gain_hbys{lut_gain_hbys.shape} != ({len_s}, {len_hd})!")

        lut_gain_ybyy = lut_gain_ybyy.reshape(len_y, len_hd)
        lut_gain_sbyy = lut_gain_sbyy.reshape(len_y, len_hd)
        lut_gain_hbyy = lut_gain_hbyy.reshape(len_y, len_hd)
        lut_gain_ybys = lut_gain_ybys.reshape(len_s, len_hd)
        lut_gain_sbys = lut_gain_sbys.reshape(len_s, len_hd)
        lut_gain_hbys = lut_gain_hbys.reshape(len_s, len_hd)

        ## resample the loaded LUTs to the default length (if they differ)
        target_h = self._default_len_h
        target_hd = self._default_len_hd
        target_y = self._default_len_y
        target_s = self._default_len_s

        if len_h != target_h:
            print(f"[ACM] resample loaded delta LUT: {len_h} => {target_h} (linear)")
            lut_delta_ybyh = linear_resize_array_1d(lut_delta_ybyh, target_h)
            lut_delta_sbyh = linear_resize_array_1d(lut_delta_sbyh, target_h)
            lut_delta_hbyh = linear_resize_array_1d(lut_delta_hbyh, target_h)

        if lut_gain_ybyy.shape != (target_y, target_hd):
            print(f"[ACM] resample loaded gain_ybyy: {lut_gain_ybyy.shape} => ({target_y}, {target_hd}) (bilinear)")
            lut_gain_ybyy = linear_resize_array_2d(lut_gain_ybyy, target_y, target_hd)
            lut_gain_sbyy = linear_resize_array_2d(lut_gain_sbyy, target_y, target_hd)
            lut_gain_hbyy = linear_resize_array_2d(lut_gain_hbyy, target_y, target_hd)
        if lut_gain_ybys.shape != (target_s, target_hd):
            print(f"[ACM] resample loaded gain_ybys: {lut_gain_ybys.shape} => ({target_s}, {target_hd}) (bilinear)")
            lut_gain_ybys = linear_resize_array_2d(lut_gain_ybys, target_s, target_hd)
            lut_gain_sbys = linear_resize_array_2d(lut_gain_sbys, target_s, target_hd)
            lut_gain_hbys = linear_resize_array_2d(lut_gain_hbys, target_s, target_hd)

        ## write into default set, then propagate to current set (uses bicubic)
        self._default_lut_delta_ybyh = np.clip(lut_delta_ybyh, ACM_DELTA_Y_MIN, ACM_DELTA_Y_MAX).astype(np.int16)
        self._default_lut_delta_sbyh = np.clip(lut_delta_sbyh, ACM_DELTA_S_MIN, ACM_DELTA_S_MAX).astype(np.int16)
        self._default_lut_delta_hbyh = np.clip(lut_delta_hbyh, ACM_DELTA_H_MIN, ACM_DELTA_H_MAX).astype(np.int16)
        self._default_lut_gain_ybyy = np.clip(lut_gain_ybyy, ACM_GAIN_MIN, ACM_GAIN_MAX).astype(np.int8)
        self._default_lut_gain_sbyy = np.clip(lut_gain_sbyy, ACM_GAIN_MIN, ACM_GAIN_MAX).astype(np.int8)
        self._default_lut_gain_hbyy = np.clip(lut_gain_hbyy, ACM_GAIN_MIN, ACM_GAIN_MAX).astype(np.int8)
        self._default_lut_gain_ybys = np.clip(lut_gain_ybys, ACM_GAIN_MIN, ACM_GAIN_MAX).astype(np.int8)
        self._default_lut_gain_sbys = np.clip(lut_gain_sbys, ACM_GAIN_MIN, ACM_GAIN_MAX).astype(np.int8)
        self._default_lut_gain_hbys = np.clip(lut_gain_hbys, ACM_GAIN_MIN, ACM_GAIN_MAX).astype(np.int8)

        self._resample_default_to_current(method="bicubic")
        self.b_lut_ready = True
        print("[ACM] load config done.")
        return True

    def dump_json(self, filename: str = "") -> bool:
        data = {
            "version": (f"acm_impl_var_lut_rand_seed_{self.rand_seed}" if self.rand_seed > 0 else "acm_impl_var_lut"),
            "acmEnable": 1,
            "isLut4Rgb": int(self.is_lut4rgb),
            "lutLengthY": self._default_len_y,
            "lutLengthS": self._default_len_s,
            "lutLengthH": self._default_len_h,
            "lutLengthHD": self._default_len_hd,
            "lut2dAxis4HD": 1,
            "wrOffset": self.offset_wr,
            "wgOffset": self.offset_wg,
            "wbOffset": self.offset_wb,
            "lumGain": self.gain_y,
            "hueGain": self.gain_h,
            "satGain": self.gain_s,
            "acmTableDeltaYbyH": utl.NoIndent(self._default_lut_delta_ybyh.flatten().tolist()),
            "acmTableDeltaHbyH": utl.NoIndent(self._default_lut_delta_hbyh.flatten().tolist()),
            "acmTableDeltaSbyH": utl.NoIndent(self._default_lut_delta_sbyh.flatten().tolist()),
            "acmTableGainYbyY": utl.NoIndent(self._default_lut_gain_ybyy.flatten().tolist()),
            "acmTableGainHbyY": utl.NoIndent(self._default_lut_gain_hbyy.flatten().tolist()),
            "acmTableGainSbyY": utl.NoIndent(self._default_lut_gain_sbyy.flatten().tolist()),
            "acmTableGainYbyS": utl.NoIndent(self._default_lut_gain_ybys.flatten().tolist()),
            "acmTableGainHbyS": utl.NoIndent(self._default_lut_gain_hbys.flatten().tolist()),
            "acmTableGainSbyS": utl.NoIndent(self._default_lut_gain_sbys.flatten().tolist()),
        }

        nest_data = {"pq_tuning_param": {"acm": data}}
        json_data = json.dumps(nest_data, indent=4, ensure_ascii=False, cls=utl.CompactArrayEncoder)

        if filename == "":
            print(f"[ACM] Config parameters shown below:")
            print(json_data)
        else:
            with open(filename, "w") as f:
                f.write(json_data)
                print(f"[ACM] Config parameters saved to file '{filename}'")
                return True


    def get_pixel_intermediates(self, x: int, y: int) -> dict | None:
        """Return raw intermediate delta/gain values for a specific pixel.

        Returns a dict with keys delta_y, delta_s, delta_h, gain_yy, gain_ys,
        gain_sy, gain_ss, gain_hy, gain_hs, or None if no intermediate data
        has been stored yet (i.e. no image has been processed).
        """
        if not hasattr(self, "_last_intermediate_shape"):
            return None
        h, w = self._last_intermediate_shape
        if y < 0 or y >= h or x < 0 or x >= w:
            return None
        return {
            "delta_y": float(self._last_delta_y_raw[y, x]),
            "delta_s": float(self._last_delta_s_raw[y, x]),
            "delta_h": float(self._last_delta_h_raw[y, x]),
            "gain_yy": float(self._last_gain_yy[y, x]),
            "gain_ys": float(self._last_gain_ys[y, x]),
            "gain_sy": float(self._last_gain_sy[y, x]),
            "gain_ss": float(self._last_gain_ss[y, x]),
            "gain_hy": float(self._last_gain_hy[y, x]),
            "gain_hs": float(self._last_gain_hs[y, x]),
        }
    def dump_luts(self, dir: str = "", return_image: bool = False) -> np.ndarray | None:
        """Dump all LUT tables into a single figure and optionally return the image.

        All rows: 9 heatmaps (3 delta strips + 6 gain LUTs) in a 3×3 grid.
        Small LUTs are rendered with nearest-neighbour interpolation for clarity.
        """
        from matplotlib.gridspec import GridSpec

        ny, ns, nh, nhd = self.len_y, self.len_s, self.len_h, self.len_hd

        fig = plt.figure(figsize=(16, 10))
        gs = GridSpec(3, 3, figure=fig, height_ratios=[1.5, 1, 1], hspace=0.45, wspace=0.35)

        # ---- Row 0: Delta curves ----
        ax_delta = fig.add_subplot(gs[0, :])
        x = np.arange(nh)
        ax_delta.plot(x, self.lut_delta_ybyh, color="red", linewidth=1.5, label="delta_ybyh")
        ax_delta.plot(x, self.lut_delta_sbyh, color="blue", linewidth=1.5, label="delta_sbyh")
        ax_delta.plot(x, self.lut_delta_hbyh, color="green", linewidth=1.5, label="delta_hbyh")
        ax_delta.axhline(0, color="gray", linestyle=":", linewidth=0.8)
        ax_delta.legend(loc="upper right")
        ax_delta.set_title(f'ACM Delta LUT by H  (len_h={nh})')
        ax_delta.set_xlabel("H index")
        ax_delta.set_ylabel("Delta value")
        ax_delta.grid(True, linestyle=":", alpha=0.5)

        # ---- Rows 1-2: Gain heatmaps ----
        gain_specs = [
            # row, col, data, title, shape_str, y_label
            (1, 0, self.lut_gain_ybyy, "GainY by Y", f"{nhd}x{ny}", "Y index"),
            (1, 1, self.lut_gain_sbyy, "GainS by Y", f"{nhd}x{ny}", "Y index"),
            (1, 2, self.lut_gain_hbyy, "GainH by Y", f"{nhd}x{ny}", "Y index"),
            (2, 0, self.lut_gain_ybys, "GainY by S", f"{nhd}x{ns}", "S index"),
            (2, 1, self.lut_gain_sbys, "GainS by S", f"{nhd}x{ns}", "S index"),
            (2, 2, self.lut_gain_hbys, "GainH by S", f"{nhd}x{ns}", "S index"),
        ]
        for row, col, data, title, shape_str, y_label in gain_specs:
            ax = fig.add_subplot(gs[row, col])
            h, w = data.shape
            step_y = (h + 3) // 4
            step_x = (w + 7) // 8
            # Use nearest-neighbour for tiny LUTs; keep aspect auto so they
            # fill the subplot area regardless of native pixel count.
            interpolation = "nearest" if max(h, w) < 50 else "bilinear"
            im = ax.imshow(
                data, cmap="RdBu_r", vmin=-128, vmax=127, aspect="auto", origin="lower", interpolation=interpolation
            )
            ax.set_title(f"{title}  [{shape_str}]")
            ax.set_xlabel("H index")
            ax.set_ylabel(y_label)
            ax.set_xticks(np.arange(0, w, step_x, dtype=int))
            ax.set_yticks(np.arange(0, h, step_y, dtype=int))
            plt.colorbar(im, ax=ax, shrink=0.82)

        fig.suptitle(f"ACM LUT Overview", fontsize=14, fontweight="bold")

        image = None
        if return_image:
            fig.canvas.draw()
            image = np.asarray(fig.canvas.buffer_rgba()).copy()

        if dir:
            out_path = f"{dir}/lut_all.png"
            plt.savefig(out_path, dpi=200, bbox_inches="tight")
            print(f"[ACM] dump LUT overview to {out_path}.")
        plt.close(fig)
        return image

    def dump_lut_results(self, return_image: bool = False) -> object:
        """Dump per-pixel LUT lookup results as 12 heatmaps in a 4x3 grid.

        Shows the 12 intermediate arrays (3 raw deltas + 3 final deltas + 6 gains)
        from the last ACM processing run at full image resolution.
        """
        if not hasattr(self, "_last_intermediate_shape"):
            print("[LUT Result] dump_lut_results: no _last_intermediate_shape")
            return None
        print(f"[LUT Result] dump_lut_results: shape={self._last_intermediate_shape}")
        from matplotlib.gridspec import GridSpec

        fig = plt.figure(figsize=(16, 14))
        gs = GridSpec(4, 3, figure=fig, hspace=0.45, wspace=0.35)

        specs = [
            # row, col, attr, title, cmap, vmax
            (0, 0, "_last_delta_y_raw", "DeltaY (raw)", "RdBu_r", 1.0),
            (0, 1, "_last_delta_s_raw", "DeltaS (raw)", "RdBu_r", 1.0),
            (0, 2, "_last_delta_h_raw", "DeltaH (raw)", "RdBu_r", 64.0),
            (1, 0, "_final_delta_y", "DeltaY (final)", "RdBu_r", 1.0),
            (1, 1, "_final_delta_s", "DeltaS (final)", "RdBu_r", 1.0),
            (1, 2, "_final_delta_h", "DeltaH (final)", "RdBu_r", 64.0),
            (2, 0, "_last_gain_yy", "GainY by Y", "RdBu_r", 1.0),
            (2, 1, "_last_gain_sy", "GainS by Y", "RdBu_r", 1.0),
            (2, 2, "_last_gain_hy", "GainH by Y", "RdBu_r", 1.0),
            (3, 0, "_last_gain_ys", "GainY by S", "RdBu_r", 1.0),
            (3, 1, "_last_gain_ss", "GainS by S", "RdBu_r", 1.0),
            (3, 2, "_last_gain_hs", "GainH by S", "RdBu_r", 1.0),
        ]
        for row, col, attr, title, cmap, vmax in specs:
            data = getattr(self, attr, None)
            if data is None:
                continue
            ax = fig.add_subplot(gs[row, col])
            # vmax = np.percentile(np.abs(data), 99) if data.size > 0 else 1.0
            # vmax = max(vmax, 0.01)
            h, w = data.shape
            im = ax.imshow(data, cmap=cmap, vmin=-vmax, vmax=vmax,
                          aspect="auto", origin="lower",
                          interpolation="bilinear" if max(h, w) > 256 else "nearest")
            ax.set_title(f"{title}  [{w}x{h}]", fontsize=12)
            ax.set_xlabel("X pixel")
            ax.set_ylabel("Y pixel")
            plt.colorbar(im, ax=ax, shrink=0.82)

        fig.suptitle("ACM Per-Pixel LUT Lookup Results", fontsize=14, fontweight="bold")

        image = None
        if return_image:
            fig.canvas.draw()
            image = np.asarray(fig.canvas.buffer_rgba()).copy()
        plt.close(fig)
        return image

    def gen_test_config(self, b_strict: bool = True, random_seed: int = 114514) -> bool:
        if not self.b_lut_ready:
            return False

        np.random.seed(random_seed)
        tmp_lut_gain_ybyy = np.random.normal(0.0, 64.0, size=(self._default_len_y, self._default_len_hd)) * 16
        tmp_lut_gain_sbyy = np.random.normal(0.0, 64.0, size=(self._default_len_y, self._default_len_hd)) * 16
        tmp_lut_gain_hbyy = np.random.normal(0.0, 64.0, size=(self._default_len_y, self._default_len_hd)) * 16
        tmp_lut_gain_ybys = np.random.normal(0.0, 64.0, size=(self._default_len_s, self._default_len_hd)) * 16
        tmp_lut_gain_sbys = np.random.normal(0.0, 64.0, size=(self._default_len_s, self._default_len_hd)) * 16
        tmp_lut_gain_hbys = np.random.normal(0.0, 64.0, size=(self._default_len_s, self._default_len_hd)) * 16
        tmp_lut_gain_ybyy = cv2.GaussianBlur(tmp_lut_gain_ybyy, ksize=(0, 0), sigmaX=3.0, sigmaY=3.0)
        tmp_lut_gain_sbyy = cv2.GaussianBlur(tmp_lut_gain_sbyy, ksize=(0, 0), sigmaX=3.0, sigmaY=3.0)
        tmp_lut_gain_hbyy = cv2.GaussianBlur(tmp_lut_gain_hbyy, ksize=(0, 0), sigmaX=3.0, sigmaY=3.0)
        tmp_lut_gain_ybys = cv2.GaussianBlur(tmp_lut_gain_ybys, ksize=(0, 0), sigmaX=3.0, sigmaY=3.0)
        tmp_lut_gain_sbys = cv2.GaussianBlur(tmp_lut_gain_sbys, ksize=(0, 0), sigmaX=3.0, sigmaY=3.0)
        tmp_lut_gain_hbys = cv2.GaussianBlur(tmp_lut_gain_hbys, ksize=(0, 0), sigmaX=3.0, sigmaY=3.0)
        self._default_lut_gain_ybyy = np.clip(tmp_lut_gain_ybyy, ACM_GAIN_MIN, ACM_GAIN_MAX).astype(np.int8)
        self._default_lut_gain_sbyy = np.clip(tmp_lut_gain_sbyy, ACM_GAIN_MIN, ACM_GAIN_MAX).astype(np.int8)
        self._default_lut_gain_hbyy = np.clip(tmp_lut_gain_hbyy, ACM_GAIN_MIN, ACM_GAIN_MAX).astype(np.int8)
        self._default_lut_gain_ybys = np.clip(tmp_lut_gain_ybys, ACM_GAIN_MIN, ACM_GAIN_MAX).astype(np.int8)
        self._default_lut_gain_sbys = np.clip(tmp_lut_gain_sbys, ACM_GAIN_MIN, ACM_GAIN_MAX).astype(np.int8)
        self._default_lut_gain_hbys = np.clip(tmp_lut_gain_hbys, ACM_GAIN_MIN, ACM_GAIN_MAX).astype(np.int8)

        tmp_lut_delta_ybyh = np.random.uniform(-1, 1, self._default_len_h).reshape(1, -1) * 300
        tmp_lut_delta_hbyh = np.random.uniform(-1, 1, self._default_len_h).reshape(1, -1) * 100
        tmp_lut_delta_sbyh = np.random.uniform(-1, 1, self._default_len_h).reshape(1, -1) * 300
        tmp_lut_delta_ybyh = cv2.GaussianBlur(tmp_lut_delta_ybyh, ksize=(5, 1), sigmaX=1.0)
        tmp_lut_delta_hbyh = cv2.GaussianBlur(tmp_lut_delta_hbyh, ksize=(5, 1), sigmaX=1.0)
        tmp_lut_delta_sbyh = cv2.GaussianBlur(tmp_lut_delta_sbyh, ksize=(5, 1), sigmaX=1.0)
        self._default_lut_delta_ybyh = np.clip(tmp_lut_delta_ybyh.flatten(), ACM_DELTA_Y_MIN, ACM_DELTA_Y_MAX).astype(
            np.int16
        )
        self._default_lut_delta_hbyh = np.clip(tmp_lut_delta_hbyh.flatten(), ACM_DELTA_H_MIN, ACM_DELTA_H_MAX).astype(
            np.int16
        )
        self._default_lut_delta_sbyh = np.clip(tmp_lut_delta_sbyh.flatten(), ACM_DELTA_S_MIN, ACM_DELTA_S_MAX).astype(
            np.int16
        )

        ## generate S/H LUTs strictly for the bug of VOP_ACM, which means:
        ## 1. LUT[0] = LUT[64], make sure the first and last value are the same (h=-180/+180)
        ## 2. LUT[0] = 0, make sure the first delta values are zero (h=-180)
        if b_strict and self._default_len_h > 1:
            self._default_lut_delta_ybyh[-1] = self._default_lut_delta_ybyh[0]
            self._default_lut_delta_hbyh[-1] = self._default_lut_delta_hbyh[0] = 0
            self._default_lut_delta_sbyh[-1] = self._default_lut_delta_sbyh[0] = 0

        self.rand_seed = random_seed
        self._resample_default_to_current()
        print(f"[ACM] generated a test config, b_strict={b_strict}, random_seed={random_seed}.")
