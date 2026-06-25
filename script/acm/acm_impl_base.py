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
                self, f"_default_lut_{name}", np.ones((self._default_len_hd, self._default_len_y), dtype=np.int8) * 127
            )
            setattr(self, f"lut_{name}", getattr(self, f"_default_lut_{name}").copy())
        for name in LUT_2D_S_NAMES:
            setattr(
                self, f"_default_lut_{name}", np.ones((self._default_len_hd, self._default_len_s), dtype=np.int8) * 127
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
            if default_lut.shape != (self.len_hd, self.len_y):
                new_lut = resample_2d(default_lut, self.len_hd, self.len_y, kernel)
                setattr(self, f"lut_{name}", new_lut)
                print(f"[ACM] resample {name}: {default_lut.shape} => {new_lut.shape} ({method})")
            else:
                setattr(self, f"lut_{name}", default_lut.copy())
        for name in LUT_2D_S_NAMES:
            default_lut = getattr(self, f"_default_lut_{name}")
            if default_lut.shape != (self.len_hd, self.len_s):
                new_lut = resample_2d(default_lut, self.len_hd, self.len_s, kernel)
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
            self._default_lut_sbyh = self.lut_delta_sbyh.copy()
            self._default_lut_hbyh = self.lut_delta_hbyh.copy()

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
            s_max = 511 if self.clip_type == 'radial_clip' else 724
        else:
            y_max = 255
            cbcr_center = 128
            s_max = 127 if self.clip_type == 'radial_clip' else 181

        # ---- 1. do yuv2yhs ----
        y = planar_data[0].astype(np.int32)  # [0,255]/[0,1023]
        cb = planar_data[1].astype(np.int32) - cbcr_center  # [-128,127]/[-512,511]
        cr = planar_data[2].astype(np.int32) - cbcr_center  # [-128,127]/[-512,511]

        if use_cordic:
            h_deg, s, _, _ = cordic.cordic_cbcr2hs(cb, cr, depth, 13, 6, False)  # h:[-180, 180], s:[0,181]/[0,724]
            h_rad = np.deg2rad(h_deg)  # [-pi, pi]
        else:
            s = (np.sqrt(cb * cb + cr * cr) + 0.5).astype(np.int32) # [0,181]/[0,724]
            h_rad = np.arctan2(cr, cb)  # [-pi, pi]
            h_deg = np.rad2deg(h_rad).astype(np.int32)  # [-180, 180]

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
        h_f = (h_deg.astype(np.float32) + 180.0) / 360.0
        idx_y = y_f * (self.len_y - 1)
        idx_s = s_f * (self.len_s - 1)
        idx_h = h_f * (self.len_h - 1)
        idx_hd = h_f * (self.len_hd - 1)
        idx_zeros = np.zeros_like(idx_h)

        # ---- 4. Sample delta tables (1D, indexed by H) → additive deltas ----
        delta_y = cv2.remap(lut_dy, idx_h, idx_zeros, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        delta_s = cv2.remap(lut_ds, idx_h, idx_zeros, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        delta_h = cv2.remap(
            lut_dh, idx_h, idx_zeros, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE
        )  # [-64, 64]

        # ---- 5. Sample gain tables (2D, indexed by (Y/S, HD)) ----
        gain_yy = cv2.remap(lut_gy_y, idx_y, idx_hd, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        gain_sy = cv2.remap(lut_gs_y, idx_y, idx_hd, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        gain_hy = cv2.remap(lut_gh_y, idx_y, idx_hd, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        gain_ys = cv2.remap(lut_gy_s, idx_s, idx_hd, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        gain_ss = cv2.remap(lut_gs_s, idx_s, idx_hd, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        gain_hs = cv2.remap(lut_gh_s, idx_s, idx_hd, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)

        # ---- 6. Combine deltas (all in normalised float) ----
        delta_y = delta_y * gain_yy * gain_ys # [-dr_y, dr_y]
        delta_s = delta_s * gain_sy * gain_ss # [-dr_s, dr_s]
        delta_h = delta_h * gain_hy * gain_hs # [-dr_h, dr_h]

        # ---- 7. Apply to normalised values ----
        if self.clip_type == "luma_clip":
            y_new = np.clip(y_f + delta_y, 0.0, 1.0)
            s_new, s_max_old, s_max_new = self._sat_adjust_triangle(y_f, y_new, s_f)
            s_f = np.clip(s_new + delta_s * s_max_new, 0.0, s_max_new)
            y_f = y_new
        else:
            y_f = np.clip(y_f + delta_y, 0.0, 1.0)
            s_f = np.clip(s_f + delta_s, 0.0, 1.0)

        # ---- 8. Convert back to integer pixel domain ----
        h_deg_new = np.mod(h_deg + delta_h, 360.0)
        h_deg_new = np.where(h_deg_new < 0, h_deg_new + 360.0, h_deg_new)
        s_pix_f = s_f * s_max
        if use_cordic:
            s_pix = (s_pix_f + 0.5).astype(np.int32)
            cb, cr = cordic.cordic_hs2cbcr(h_deg_new, s_pix, 8, depth, depth, 13, 6)
        else:
            new_rad = np.deg2rad(h_deg_new)
            new_cb = s_pix_f * np.cos(new_rad)
            new_cr = s_pix_f * np.sin(new_rad)
            cb = (new_cb + np.sign(new_cb) * 0.5).astype(np.int32)
            cr = (new_cr + np.sign(new_cr) * 0.5).astype(np.int32)

        # ---- 9. Final clip ----
        y_out = (y_f * y_max + 0.5).astype(np.int32)

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
        delta_y = cv2.remap(lut_dy, idx_hp, idx_zeros, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        delta_s = cv2.remap(lut_ds, idx_hp, idx_zeros, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        delta_h = cv2.remap(lut_dh, idx_hp, idx_zeros, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)

        # ---- 7. Sample gain tables (2D LUTs indexed by (V,H) and (S,H)) ----
        gain_yy = cv2.remap(lut_g_yy, idx_v, idx_hp, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        gain_ys = cv2.remap(lut_g_ys, idx_v, idx_hp, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        gain_yh = cv2.remap(lut_g_yh, idx_v, idx_hp, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        gain_sy = cv2.remap(lut_g_sy, idx_s, idx_hp, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        gain_ss = cv2.remap(lut_g_ss, idx_s, idx_hp, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        gain_sh = cv2.remap(lut_g_sh, idx_s, idx_hp, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)

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

    def _sat_adjust_triangle(self, y_f_old: np.ndarray, y_f_new: np.ndarray, s_f_old: np.ndarray) -> tuple:
        """
        Apply triangle saturation adjustment to s_f.
        """
        # corner point: (s=94, 127)
        # k = 0.94 / 0.5
        # s_max = 0.94 * np.ones_like(s_f, dtype=np.float32)
        # s_max = np.where(y_f <= 0.5, y_f * k, s_max)
        # s_max = np.where(y_f > 0.5, (1 - y_f) * k, s_max)

        max_s_lut_by_y = np.array([
            0,   2,   4,   6,   8,   9,  11,  13,  15,  17,  19,  21,  23,
            25,  26,  28,  30,  32,  34,  36,  38,  40,  42,  43,  45,  47,
            49,  51,  53,  55,  57,  59,  60,  62,  64,  66,  68,  70,  72,
            74,  75,  77,  79,  81,  83,  85,  87,  89,  91,  92,  94,  96,
            98, 100, 102, 104, 106, 108, 109, 111, 113, 115, 117, 119, 121,
            123, 125, 126, 128, 130, 132, 134, 136, 138, 140, 142, 143, 145,
            147, 149, 151, 153, 155, 157, 159, 160, 162, 164, 166, 168, 170,
            172, 174, 176, 177, 179, 181, 183, 185, 187, 189, 191, 193, 194,
            196, 198, 200, 202, 204, 206, 208, 209, 211, 213, 215, 217, 219,
            221, 223, 225, 226, 228, 230, 232, 234, 236, 238, 240, 240, 238,
            236, 234, 232, 230, 228, 226, 225, 223, 221, 219, 217, 215, 213,
            211, 209, 208, 206, 204, 202, 200, 198, 196, 194, 193, 191, 189,
            187, 185, 183, 181, 179, 177, 176, 174, 172, 170, 168, 166, 164,
            162, 160, 159, 157, 155, 153, 151, 149, 147, 145, 143, 142, 140,
            138, 136, 134, 132, 130, 128, 126, 125, 123, 121, 119, 117, 115,
            113, 111, 109, 108, 106, 104, 102, 100,  98,  96,  94,  92,  91,
            89,  87,  85,  83,  81,  79,  77,  75,  74,  72,  70,  68,  66,
            64,  62,  60,  59,  57,  55,  53,  51,  49,  47,  45,  43,  42,
            40,  38,  36,  34,  32,  30,  28,  26,  25,  23,  21,  19,  17,
            15,  13,  11,   9,   8,   6,   4,   2,   0], dtype=np.float32) / 256.0

        y_range = np.linspace(0, 1.0, 256)
        s_max_old = np.interp(y_f_old, y_range, max_s_lut_by_y, 0, 240)
        s_max_new = np.interp(y_f_new, y_range, max_s_lut_by_y, 0, 240)
        s_f_old = np.minimum(s_f_old, s_max_old)
        s_f_new = s_f_old * s_max_new / s_max_old
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
        lut2dAxis4HD = 0

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

                lut2dAxis4HD = data["lut2dAxis4HD"] if "lut2dAxis4HD" in data else 0

                self.gain_y = data["lumGain"] if "lumGain" in data else 256
                self.gain_s = data["satGain"] if "satGain" in data else 256
                self.gain_h = data["hueGain"] if "hueGain" in data else 256
                self.offset_wb = data["wbOffset"] if "wbOffset" in data else 0
                self.offset_wg = data["wgOffset"] if "wgOffset" in data else 0
                self.offset_wr = data["wrOffset"] if "wrOffset" in data else 0
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
                    print(
                        f"[ACM] gain luts reshape to {len_hd}(H) x {len_y}/{len_s}(W) since lut2dAxis4HD={lut2dAxis4HD}"
                    )
                    lut_gain_ybyy = lut_gain_ybyy.reshape(len_y, len_hd).T
                    lut_gain_sbyy = lut_gain_sbyy.reshape(len_y, len_hd).T
                    lut_gain_hbyy = lut_gain_hbyy.reshape(len_y, len_hd).T
                    lut_gain_ybys = lut_gain_ybys.reshape(len_s, len_hd).T
                    lut_gain_sbys = lut_gain_sbys.reshape(len_s, len_hd).T
                    lut_gain_hbys = lut_gain_hbys.reshape(len_s, len_hd).T

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
        if lut_gain_ybyy.shape[0] * lut_gain_ybyy.shape[1] != len_hd * len_y:
            raise ValueError(
                f"size of lut_gain_ybyy({lut_gain_ybyy.shape[0]} x {lut_gain_ybyy.shape[1]}) != len_hd({len_hd}) x len_y({len_y})!"
            )
        if lut_gain_sbyy.shape[0] * lut_gain_sbyy.shape[1] != len_hd * len_y:
            raise ValueError(
                f"size of lut_gain_sbyy({lut_gain_sbyy.shape[0]} x {lut_gain_sbyy.shape[1]}) != len_hd({len_hd}) x len_y({len_y})!"
            )
        if lut_gain_hbyy.shape[0] * lut_gain_hbyy.shape[1] != len_hd * len_y:
            raise ValueError(
                f"size of lut_gain_hbyy({lut_gain_hbyy.shape[0]} x {lut_gain_hbyy.shape[1]}) != len_hd({len_hd}) x len_y({len_y})!"
            )
        if lut_gain_ybys.shape[0] * lut_gain_ybys.shape[1] != len_hd * len_s:
            raise ValueError(
                f"size of lut_gain_ybys({lut_gain_ybys.shape[0]} x {lut_gain_ybys.shape[1]}) != len_hd({len_hd}) x len_s({len_s})!"
            )
        if lut_gain_sbys.shape[0] * lut_gain_sbys.shape[1] != len_hd * len_s:
            raise ValueError(
                f"size of lut_gain_sbys({lut_gain_sbys.shape[0]} x {lut_gain_sbys.shape[1]}) != len_hd({len_hd}) x len_s({len_s})!"
            )
        if lut_gain_hbys.shape[0] * lut_gain_hbys.shape[1] != len_hd * len_s:
            raise ValueError(
                f"size of lut_gain_hbys({lut_gain_hbys.shape[0]} x {lut_gain_hbys.shape[1]}) != len_hd({len_hd}) x len_s({len_s})!"
            )

        lut_gain_ybyy = lut_gain_ybyy.reshape(len_hd, len_y)
        lut_gain_sbyy = lut_gain_sbyy.reshape(len_hd, len_y)
        lut_gain_hbyy = lut_gain_hbyy.reshape(len_hd, len_y)
        lut_gain_ybys = lut_gain_ybys.reshape(len_hd, len_s)
        lut_gain_sbys = lut_gain_sbys.reshape(len_hd, len_s)
        lut_gain_hbys = lut_gain_hbys.reshape(len_hd, len_s)

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

        if lut_gain_ybyy.shape != (target_hd, target_y):
            print(f"[ACM] resample loaded gain_ybyy: {lut_gain_ybyy.shape} => ({target_hd}, {target_y}) (bilinear)")
            lut_gain_ybyy = linear_resize_array_2d(lut_gain_ybyy, target_hd, target_y)
            lut_gain_sbyy = linear_resize_array_2d(lut_gain_sbyy, target_hd, target_y)
            lut_gain_hbyy = linear_resize_array_2d(lut_gain_hbyy, target_hd, target_y)
        if lut_gain_ybys.shape != (target_hd, target_s):
            print(f"[ACM] resample loaded gain_ybys: {lut_gain_ybys.shape} => ({target_hd}, {target_s}) (bilinear)")
            lut_gain_ybys = linear_resize_array_2d(lut_gain_ybys, target_hd, target_s)
            lut_gain_sbys = linear_resize_array_2d(lut_gain_sbys, target_hd, target_s)
            lut_gain_hbys = linear_resize_array_2d(lut_gain_hbys, target_hd, target_s)

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
            "isLut4Rgb": 1 if self.is_lut4rgb else 0,
            "lutLengthY": self._default_len_y,
            "lutLengthS": self._default_len_s,
            "lutLengthH": self._default_len_h,
            "lutLengthHD": self._default_len_hd,
            "lut2dAxis4HD": (0 if self._default_lut_gain_ybyy.shape[0] == self._default_len_hd else 1),
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
            "acmTableGainHbyS": utl.NoIndent(self._default_lut_gain_sbys.flatten().tolist()),
            "acmTableGainSbyS": utl.NoIndent(self._default_lut_gain_hbys.flatten().tolist()),
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

    def dump_luts(self, dir: str = "", return_image: bool = False) -> np.ndarray | None:
        """Dump all LUT tables into a single figure and optionally return the image.

        Top row:  3 delta curves (Y/S/H vs H)
        Rows 2-3: 6 gain heatmaps (3×Y axis + 3×S axis)
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
        ax_delta.set_title(f"ACM Delta LUT by H  (len_h={nh})")
        ax_delta.set_xlabel("H index")
        ax_delta.set_ylabel("Delta value")
        ax_delta.grid(True, linestyle=":", alpha=0.5)

        # ---- Rows 1-2: Gain heatmaps ----
        gain_specs = [
            (1, 0, self.lut_gain_ybyy, "Gain Y by Y", f"{nhd}×{ny}"),
            (1, 1, self.lut_gain_sbyy, "Gain S by Y", f"{nhd}×{ny}"),
            (1, 2, self.lut_gain_hbyy, "Gain H by Y", f"{nhd}×{ny}"),
            (2, 0, self.lut_gain_ybys, "Gain Y by S", f"{nhd}×{ns}"),
            (2, 1, self.lut_gain_sbys, "Gain S by S", f"{nhd}×{ns}"),
            (2, 2, self.lut_gain_hbys, "Gain H by S", f"{nhd}×{ns}"),
        ]
        for row, col, data, title, shape_str in gain_specs:
            ax = fig.add_subplot(gs[row, col])
            h, w = data.shape
            # Use nearest-neighbour for tiny LUTs; keep aspect auto so they
            # fill the subplot area regardless of native pixel count.
            interpolation = "nearest" if max(h, w) < 50 else "bilinear"
            im = ax.imshow(
                data, cmap="RdBu_r", vmin=-128, vmax=127, aspect="auto", origin="lower", interpolation=interpolation
            )
            ax.set_title(f"{title}  [{shape_str}]")
            ax.set_xlabel("Y/S index")
            ax.set_ylabel("H index")
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

    def gen_test_config(self, b_strict: bool = True, random_seed: int = 114514) -> bool:
        if not self.b_lut_ready:
            return False

        np.random.seed(random_seed)
        tmp_lut_gain_ybyy = np.random.normal(0.0, 64.0, size=(self._default_len_hd, self._default_len_y)) * 16
        tmp_lut_gain_sbyy = np.random.normal(0.0, 64.0, size=(self._default_len_hd, self._default_len_y)) * 16
        tmp_lut_gain_hbyy = np.random.normal(0.0, 64.0, size=(self._default_len_hd, self._default_len_y)) * 16
        tmp_lut_gain_ybys = np.random.normal(0.0, 64.0, size=(self._default_len_hd, self._default_len_s)) * 16
        tmp_lut_gain_sbys = np.random.normal(0.0, 64.0, size=(self._default_len_hd, self._default_len_s)) * 16
        tmp_lut_gain_hbys = np.random.normal(0.0, 64.0, size=(self._default_len_hd, self._default_len_s)) * 16
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
