"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : acm_impl_base.py
Author      : vance.wu@rock-chips.com
Date        : 2026-06-14
Description : Base class for ACM implementation, providing LUT management,
              YUV<=>YHS conversion (trig or cordic), and ACM processing for
              8bit / 10bit YUV444 planar images.
LastEditTime: 2026-06-15
"""

import os
import sys
import json
import cv2
import argparse
import traceback
import warnings
from typing import Tuple
import numpy as np
import matplotlib.pyplot as plt

if __package__:
    from . import cordic
    from .. import utils as utl
else:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    import cordic
    import utils as utl


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
ACM_HSV_GRAY_THRESHOLD_S = 0.02     # ~5/255, treat as gray when saturation is below this
ACM_HSV_EPSILON_S = 1.0 / 1023.0    # used to avoid div-by-zero / false-color in H/S

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
      * delta mapping mode ("rk" with [-1/4, 1/4] Y/S scale, or
        "evideo" with [-1, 1] Y/S scale; H always [-64, 64] deg)
      * YUV <-> YHS conversion method ("trig" by default, or "cordic")
    """

    # delta scaling factors per mode
    _DELTA_MODE_SCALE = {"rk": {"y": 0.25, "s": 0.25, "h": 1.0}, "evideo": {"y": 1.0, "s": 1.0, "h": 1.0}}
    _CVT_METHODS = ("trig", "cordic", "hsv")

    def __init__(
        self,
        len_y: int = 9,
        len_s: int = 13,
        len_h: int = 65,
        len_hd: int = 0,
        delta_mode: str = "rk",
        cvt_method: str = "trig",
    ):
        # --- mode / method ---
        assert delta_mode in self._DELTA_MODE_SCALE, f"unknown delta_mode: {delta_mode}"
        assert cvt_method in self._CVT_METHODS, f"unknown cvt_method: {cvt_method}"
        self.delta_mode = delta_mode
        self.cvt_method = cvt_method

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
        print(f"[ACM] delta_mode={self.delta_mode}, cvt_method={self.cvt_method}")

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
            setattr(self, f"_default_{name}", np.ones((self._default_len_hd, self._default_len_y), dtype=np.int8) * 127)
            setattr(self, f"lut_{name}", getattr(self, f"_default_{name}").copy())
        for name in LUT_2D_S_NAMES:
            setattr(self, f"_default_{name}", np.ones((self._default_len_hd, self._default_len_s), dtype=np.int8) * 127)
            setattr(self, f"lut_{name}", getattr(self, f"_default_{name}").copy())
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

    def set_delta_mode(self, mode: str) -> None:
        """Switch delta mapping mode ("rk" or "evideo")."""
        if mode not in self._DELTA_MODE_SCALE:
            raise ValueError(f"unknown delta_mode: {mode}, expect one of {list(self._DELTA_MODE_SCALE)}")
        self.delta_mode = mode
        print(f"[ACM] set delta_mode: {self.delta_mode}")

    def set_cvt_method(self, method: str) -> None:
        """Switch YUV<=>YHS conversion method ("trig" or "cordic")."""
        if method not in self._CVT_METHODS:
            raise ValueError(f"unknown cvt_method: {method}, expect 'trig'/'cordic'/'hsv'")
        self.cvt_method = method
        self.isLut4Rgb = 1 if method == "hsv" else 0
        print(f"[ACM] set cvt_method: {self.cvt_method}")

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

        for name in LUT_2D_Y_NAMES:
            default_lut = getattr(self, f"_default_{name}")
            if default_lut.shape != (self.len_hd, self.len_y):
                new_lut = resample_2d(default_lut, self.len_hd, self.len_y, kernel)
                setattr(self, f"lut_{name}", new_lut)
                print(f"[ACM] resample {name}: {default_lut.shape} => {new_lut.shape} ({method})")
        for name in LUT_2D_S_NAMES:
            default_lut = getattr(self, f"_default_{name}")
            if default_lut.shape != (self.len_hd, self.len_s):
                new_lut = resample_2d(default_lut, self.len_hd, self.len_s, kernel)
                setattr(self, f"lut_{name}", new_lut)
                print(f"[ACM] resample {name}: {default_lut.shape} => {new_lut.shape} ({method})")

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
            default_lut = getattr(self, f"_default_{name}")
            if current.shape != default_lut.shape:
                setattr(
                    self,
                    f"_default_{name}",
                    bicubic_resize_array_2d(current, default_lut.shape[0], default_lut.shape[1]),
                )
        for name in LUT_2D_S_NAMES:
            current = getattr(self, f"lut_{name}")
            default_lut = getattr(self, f"_default_{name}")
            if current.shape != default_lut.shape:
                setattr(
                    self,
                    f"_default_{name}",
                    bicubic_resize_array_2d(current, default_lut.shape[0], default_lut.shape[1]),
                )

    # ------------------------------------------------------------------
    # YUV <-> YHS conversion helpers
    # ------------------------------------------------------------------
    def _cbcr_to_hs(
        self, cb: np.ndarray, cr: np.ndarray, depth_uv: int, use_cordic: bool
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Convert signed Cb/Cr to H (deg in [0, 360)), S and H (rad in [-pi, pi]).

        When use_cordic is True, h_rad is None (cordic path uses h_deg directly).
        """
        if use_cordic:
            h, s, _, _ = cordic.cordic_cbcr2hs(cb, cr, depth_uv, 13, 8, False)
            h_deg = (h + 180) % 360
            return s, h_deg, None
        s = (np.sqrt(cb * cb + cr * cr) + 0.5).astype(np.int32)
        h_rad = np.arctan2(cr, cb)  # [-pi, pi]
        h_deg = (np.rad2deg(h_rad) + 180 + 0.5).astype(np.int32)  # [0, 360]
        return s, h_deg, h_rad

    def _use_cordic(self) -> bool:
        return self.cvt_method == "cordic"

    # ------------------------------------------------------------------
    # ACM processing
    # ------------------------------------------------------------------
    def do_acm_u8(self, planar_data: np.ndarray, isRgb: bool = False, use_cordic: Optional[bool] = None) -> np.ndarray:
        """Apply ACM to an 8bit YUV444p image. Returns YUV444p uint8."""
        print(f"[ACM] doing ACM LUT for u8 {'rgb' if isRgb else 'yuv'} image...")
        if use_cordic is None:
            use_cordic = self._use_cordic()

        if isRgb and self.cvt_method == "hsv":
            data_out = self._do_acm_rgb(planar_data, range=256)
            return data_out

        y = planar_data[:, :, 0].astype(np.int32)
        cb = planar_data[:, :, 1].astype(np.int32) - 128
        cr = planar_data[:, :, 2].astype(np.int32) - 128
        s, h_deg, h_rad = self._cbcr_to_hs(cb, cr, depth_uv=8, use_cordic=use_cordic)

        yuv444p_out = self._do_acm_yuv(
            y, cb, cr, s, h_deg, h_rad, depth_uv=8, y_range=256, cbcr_center=128, use_cordic=use_cordic
        )
        print(f"[ACM] do ACM LUT for u8 {'rgb' if isRgb else 'yuv'} image done.")
        return yuv444p_out

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
            use_cordic = self._use_cordic()

        if isRgb and self.cvt_method == "hsv":
            data_out = self._do_acm_rgb(planar_data, range=1024)
            return data_out

        y = planar_data[:, :, 0].astype(np.int32)
        cb = planar_data[:, :, 1].astype(np.int32) - 512
        cr = planar_data[:, :, 2].astype(np.int32) - 512
        s, h_deg, h_rad = self._cbcr_to_hs(cb, cr, depth_uv=10, use_cordic=use_cordic)

        yuv444p_out = self._do_acm_yuv(
            y, cb, cr, s, h_deg, h_rad, depth_uv=10, y_range=1024, cbcr_center=512, use_cordic=use_cordic
        )
        print(f"[ACM] do ACM LUT for u10 {'rgb' if isRgb else 'yuv'} image done.")
        return yuv444p_out

    def _do_acm_yuv(
        self,
        y: np.ndarray,
        cb: np.ndarray,
        cr: np.ndarray,
        s: np.ndarray,
        h_deg: np.ndarray,
        h_rad: np.ndarray,
        depth_uv: int,
        y_range: int,
        cbcr_center: int,
        use_cordic: bool,
    ) -> np.ndarray:
        # depth-dependent full-scale ranges
        # u8:  Y in [0,255], S in [0,181];  u10: Y in [0,1023], S in [0,724]
        y_max = float(y_range - 1)
        s_max = 181.0 if depth_uv == 8 else 724.0
        h_max = 360

        # mode-dependent scale (delta_y *= 0.25 for rk mode, *1.0 for evideo)
        scl = self._DELTA_MODE_SCALE[self.delta_mode]

        # SW method: apply global gains to delta tables first. I don't think it's a good idea.
        local_lut_delta_ybyh = round_rshift(self.lut_delta_ybyh.astype(np.int32) * self.gain_y, 8)
        local_lut_delta_sbyh = round_rshift(self.lut_delta_sbyh.astype(np.int32) * self.gain_s, 8)
        local_lut_delta_hbyh = round_rshift(self.lut_delta_hbyh.astype(np.int32) * self.gain_h, 8)
        local_lut_delta_ybyh = np.clip(local_lut_delta_ybyh, ACM_DELTA_Y_MIN, ACM_DELTA_Y_MAX)
        local_lut_delta_sbyh = np.clip(local_lut_delta_sbyh, ACM_DELTA_S_MIN, ACM_DELTA_S_MAX)
        local_lut_delta_hbyh = np.clip(local_lut_delta_hbyh, ACM_DELTA_H_MIN, ACM_DELTA_H_MAX)

        idx_y = y.astype(np.float32) / y_max * (self.len_y - 1)
        idx_s = s.astype(np.float32) / s_max * (self.len_s - 1)
        idx_h = h_deg.astype(np.float32) / h_max * (self.len_h - 1)
        idx_hd = h_deg.astype(np.float32) / h_max * (self.len_hd - 1)

        # NOTE: cv2.remap does not support int32 for bilinear interpolation.
        # The LUT values are stored in the 8bit reference domain: delta_y in
        # [-Y_FULL_RANGE, Y_FULL_RANGE] and delta_s in [-S_FULL_RANGE,
        # S_FULL_RANGE]. We interpret the LUT as a ratio relative to the 8bit
        # input range and re-scale by the current bit depth's y_max / s_max so
        # that "1x LUT value" == "1x of the current input range". Combined
        # with ``scl`` this yields:
        #   * rk    + 8bit:  delta_y in [-Y_FULL_RANGE/4,  Y_FULL_RANGE/4]
        #                    delta_s in [-S_FULL_RANGE/4,  S_FULL_RANGE/4]
        #   * rk    + 10bit: delta_y in [-y_max_10bit/4,   y_max_10bit/4]
        #                    delta_s in [-s_max_10bit/4,   s_max_10bit/4]
        #   * evideo+ 8bit:  delta_y in [-Y_FULL_RANGE,   Y_FULL_RANGE]
        #                    delta_s in [-S_FULL_RANGE,   S_FULL_RANGE]
        #   * evideo+ 10bit: delta_y in [-y_max_10bit,    y_max_10bit]
        #                    delta_s in [-s_max_10bit,    s_max_10bit]
        idx_zeros = np.zeros_like(idx_h)
        delta_y = cv2.remap(
            local_lut_delta_ybyh.astype(np.float32) * scl["y"] * y_max / ACM_Y_FULL_RANGE,
            idx_h,
            idx_zeros,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE,
        )
        delta_s = cv2.remap(
            local_lut_delta_sbyh.astype(np.float32) * scl["s"] * s_max / ACM_S_FULL_RANGE,
            idx_h,
            idx_zeros,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE,
        )
        delta_h = cv2.remap(
            local_lut_delta_hbyh.astype(np.float32) * scl["h"],
            idx_h,
            idx_zeros,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE,
        )
        gain_yy = cv2.remap(
            self.lut_gain_ybyy.astype(np.float32),
            idx_y,
            idx_hd,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE,
        )
        gain_ys = cv2.remap(
            self.lut_gain_sbyy.astype(np.float32),
            idx_y,
            idx_hd,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE,
        )
        gain_yh = cv2.remap(
            self.lut_gain_hbyy.astype(np.float32),
            idx_y,
            idx_hd,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE,
        )
        gain_sy = cv2.remap(
            self.lut_gain_ybys.astype(np.float32),
            idx_s,
            idx_hd,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE,
        )
        gain_ss = cv2.remap(
            self.lut_gain_sbys.astype(np.float32),
            idx_s,
            idx_hd,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE,
        )
        gain_sh = cv2.remap(
            self.lut_gain_hbys.astype(np.float32),
            idx_s,
            idx_hd,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE,
        )

        delta_y = (delta_y + np.sign(delta_y) * 0.5).astype(np.int32)
        delta_s = (delta_s + np.sign(delta_s) * 0.5).astype(np.int32)
        delta_h = (delta_h + np.sign(delta_h) * 0.5).astype(np.int32)
        gain_yy = (gain_yy + np.sign(gain_yy) * 0.5).astype(np.int32)
        gain_ys = (gain_ys + np.sign(gain_ys) * 0.5).astype(np.int32)
        gain_yh = (gain_yh + np.sign(gain_yh) * 0.5).astype(np.int32)
        gain_sy = (gain_sy + np.sign(gain_sy) * 0.5).astype(np.int32)
        gain_ss = (gain_ss + np.sign(gain_ss) * 0.5).astype(np.int32)
        gain_sh = (gain_sh + np.sign(gain_sh) * 0.5).astype(np.int32)
        delta_y = delta_y * (gain_yy * gain_sy)  # S9*S8*S8 => S23
        delta_s = delta_s * (gain_ys * gain_ss)  # S7*S8*S8 => S21
        delta_h = delta_h * (gain_yh * gain_sh)  # S9*S8*S8 => S23
        delta_y = round_rshift(delta_y, 14)
        delta_s = round_rshift(delta_s, 14)
        delta_h = round_rshift(delta_h, 14)

        y += delta_y
        s += delta_s

        if use_cordic:
            h_deg = h_deg + delta_h
            h_deg = np.where(h_deg < 0, h_deg + 360, h_deg)
            h_deg = np.where(h_deg > 360, h_deg - 360, h_deg)
            cb, cr = cordic.cordic_hs2cbcr(h_deg, s, 8, depth_uv, depth_uv, 13, 8)
        else:
            new_rad = h_rad + np.deg2rad(delta_h)
            new_cb = s * np.cos(new_rad)
            new_cr = s * np.sin(new_rad)
            cb = (new_cb + 0.5 * np.sign(new_cb)).astype(np.int32)
            cr = (new_cr + 0.5 * np.sign(new_cr)).astype(np.int32)

        out_dtype = np.uint8 if depth_uv == 8 else np.uint16
        yuv444p_out = np.zeros((y.shape[0], y.shape[1], 3), dtype=out_dtype)
        y_clip = y_range - 1
        yuv444p_out[:, :, 0] = np.clip(y, 0, y_clip).astype(out_dtype)
        yuv444p_out[:, :, 1] = np.clip(cb + cbcr_center, 0, y_clip).astype(out_dtype)
        yuv444p_out[:, :, 2] = np.clip(cr + cbcr_center, 0, y_clip).astype(out_dtype)
        return yuv444p_out

    def _do_acm_rgb(
        self,
        planar_data: np.ndarray,
        range: int,
    ) -> np.ndarray:
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
        r = rgb_f[0]
        g = rgb_f[1]
        b = rgb_f[2]
        v = np.max(rgb_f, axis=2)
        m = np.min(rgb_f, axis=2)
        delta_val = v - m

        # ---- 2. Gray mask: bypass LUT, apply RGB offset directly ----
        is_gray = delta_val < ACM_HSV_GRAY_THRESHOLD_S
        # Map stored offset (centered at 256, span 256) to CL's [-0.5, +0.5] domain.
        rgb_offset = np.array(
            [
                (self.offset_wr - 256) / 512.0,
                (self.offset_wg - 256) / 512.0,
                (self.offset_wb - 256) / 512.0,
            ],
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

        # ---- 4. Apply global gains to delta tables (mirrors CL host side) ----
        local_lut_delta_ybyh = round_rshift(self.lut_delta_ybyh.astype(np.int32) * self.gain_y, 8)
        local_lut_delta_sbyh = round_rshift(self.lut_delta_sbyh.astype(np.int32) * self.gain_s, 8)
        local_lut_delta_hbyh = round_rshift(self.lut_delta_hbyh.astype(np.int32) * self.gain_h, 8)
        local_lut_delta_ybyh = np.clip(local_lut_delta_ybyh, ACM_DELTA_Y_MIN, ACM_DELTA_Y_MAX)
        local_lut_delta_sbyh = np.clip(local_lut_delta_sbyh, ACM_DELTA_S_MIN, ACM_DELTA_S_MAX)
        local_lut_delta_hbyh = np.clip(local_lut_delta_hbyh, ACM_DELTA_H_MIN, ACM_DELTA_H_MAX)

        # ---- 5. Compute LUT indices ----
        # CL: idxY = v*8+0.5, idxS = s*12+0.5, idxH = hp*64/360+0.5 (with pixel-center +0.5)
        # Python's cv2.remap uses the same pixel-center convention without an
        # explicit +0.5, so the equivalent index is value*(len-1)/full_range.
        hp_deg = np.mod(h + 180.0, 360.0)
        idx_v = v * (self.len_y - 1)
        idx_s = s * (self.len_s - 1)
        idx_hp = hp_deg / h_max * (self.len_hd - 1)
        idx_zeros = np.zeros_like(idx_v)

        # ---- 6. Sample delta tables (1D LUTs indexed by H) ----
        # CL interpretation: int16/255 = fraction in [-1, +1]; delta_h is in degrees [-64, +64].
        delta_y = cv2.remap(
            local_lut_delta_ybyh.astype(np.float32) / ACM_Y_FULL_RANGE,
            idx_hp, idx_zeros,
            interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE,
        )
        delta_s = cv2.remap(
            local_lut_delta_sbyh.astype(np.float32) / ACM_Y_FULL_RANGE,
            idx_hp, idx_zeros,
            interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE,
        )
        delta_h = cv2.remap(
            local_lut_delta_hbyh.astype(np.float32),
            idx_hp, idx_zeros,
            interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE,
        )

        # ---- 7. Sample gain tables (2D LUTs indexed by (V,H) and (S,H)) ----
        # CL interpretation: int8/128 = fraction in [-1, +1].
        gain_yy = cv2.remap(
            self.lut_gain_ybyy.astype(np.float32) / 128.0, idx_v, idx_hp,
            interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE,
        )
        gain_ys = cv2.remap(
            self.lut_gain_sbyy.astype(np.float32) / 128.0, idx_v, idx_hp,
            interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE,
        )
        gain_yh = cv2.remap(
            self.lut_gain_hbyy.astype(np.float32) / 128.0, idx_v, idx_hp,
            interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE,
        )
        gain_sy = cv2.remap(
            self.lut_gain_ybys.astype(np.float32) / 128.0, idx_s, idx_hp,
            interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE,
        )
        gain_ss = cv2.remap(
            self.lut_gain_sbys.astype(np.float32) / 128.0, idx_s, idx_hp,
            interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE,
        )
        gain_sh = cv2.remap(
            self.lut_gain_hbys.astype(np.float32) / 128.0, idx_s, idx_hp,
            interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE,
        )

        # ---- 8. Combine deltas (CL: delta *= gaina * gainb; no (0.25, 0.25, 1, 1) factor) ----
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

        # ---- 12. Cast back to integer with full-range clipping ----
        rgb_out = np.empty_like(planar_data)
        rgb_out[:, :, 0] = np.clip(r_out * y_max, 0.0, y_max).astype(planar_data.dtype)
        rgb_out[:, :, 1] = np.clip(g_out * y_max, 0.0, y_max).astype(planar_data.dtype)
        rgb_out[:, :, 2] = np.clip(b_out * y_max, 0.0, y_max).astype(planar_data.dtype)
        return rgb_out

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
                data = json.load(f)
                if "pq_tuning_param" in data:
                    print("[ACM] loading config from pq_tuning_param ...")
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
                self.isLut4Rgb = data["isLut4Rgb"] if "isLut4Rgb" in data else 0

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
        if len(lut_gain_ybyy) != len_hd * len_y:
            raise ValueError(f"length of lut_gain_ybyy({len(lut_gain_ybyy)}) != len_hd({len_hd}) x len_y({len_y})!")
        if len(lut_gain_sbyy) != len_hd * len_y:
            raise ValueError(f"length of lut_gain_sbyy({len(lut_gain_sbyy)}) != len_hd({len_hd}) x len_y({len_y})!")
        if len(lut_gain_hbyy) != len_hd * len_y:
            raise ValueError(f"length of lut_gain_hbyy({len(lut_gain_hbyy)}) != len_hd({len_hd}) x len_y({len_y})!")
        if len(lut_gain_ybys) != len_hd * len_s:
            raise ValueError(f"length of lut_gain_ybys({len(lut_gain_ybys)}) != len_hd({len_hd}) x len_s({len_s})!")
        if len(lut_gain_sbys) != len_hd * len_s:
            raise ValueError(f"length of lut_gain_sbys({len(lut_gain_sbys)}) != len_hd({len_hd}) x len_s({len_s})!")
        if len(lut_gain_hbys) != len_hd * len_s:
            raise ValueError(f"length of lut_gain_hbys({len(lut_gain_hbys)}) != len_hd({len_hd}) x len_s({len_s})!")

        lut_gain_ybyy = lut_gain_ybyy.reshape(len_hd, len_y)
        lut_gain_sbyy = lut_gain_sbyy.reshape(len_hd, len_y)
        lut_gain_hbyy = lut_gain_hbyy.reshape(len_hd, len_y)
        lut_gain_ybys = lut_gain_ybys.reshape(len_hd, len_s)
        lut_gain_sbys = lut_gain_sbys.reshape(len_hd, len_s)
        lut_gain_hbys = lut_gain_hbys.reshape(len_hd, len_s)

        ## resample the loaded LUTs to the default length (if they differ)
        target_h = self._default_len_h
        target_h2 = self._default_len_hd
        target_y = self._default_len_y
        target_s = self._default_len_s

        if len_h != target_h:
            print(f"[ACM] resample loaded delta LUT: {len_h} => {target_h} (linear)")
            lut_delta_ybyh = linear_resize_array_1d(lut_delta_ybyh, target_h)
            lut_delta_sbyh = linear_resize_array_1d(lut_delta_sbyh, target_h)
            lut_delta_hbyh = linear_resize_array_1d(lut_delta_hbyh, target_h)

        if lut_gain_ybyy.shape != (target_h2, target_y):
            print(f"[ACM] resample loaded gain_ybyy: {lut_gain_ybyy.shape} => ({target_h2}, {target_y}) (linear)")
            lut_gain_ybyy = linear_resize_array_2d(lut_gain_ybyy, target_h2, target_y)
            lut_gain_sbyy = linear_resize_array_2d(lut_gain_sbyy, target_h2, target_y)
            lut_gain_hbyy = linear_resize_array_2d(lut_gain_hbyy, target_h2, target_y)
        if lut_gain_ybys.shape != (target_h2, target_s):
            print(f"[ACM] resample loaded gain_ybys: {lut_gain_ybys.shape} => ({target_h2}, {target_s}) (linear)")
            lut_gain_ybys = linear_resize_array_2d(lut_gain_ybys, target_h2, target_s)
            lut_gain_sbys = linear_resize_array_2d(lut_gain_sbys, target_h2, target_s)
            lut_gain_hbys = linear_resize_array_2d(lut_gain_hbys, target_h2, target_s)

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
            "isLut4Rgb": 1 if self.cvt_method == "hsv" else 0,
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

    def dump_lut(self, dir: str) -> None:
        ## plot delta LUT (use the current set, which reflects runtime edits)
        x = np.arange(self.len_h)

        plt.figure(figsize=(8, 6))
        plt.plot(x, self.lut_delta_ybyh, label="delta_ybyh", color="red", linewidth=1.5)
        plt.plot(x, self.lut_delta_sbyh, label="delta_sbyh", color="blue", linewidth=1.5)
        plt.plot(x, self.lut_delta_hbyh, label="delta_hbyh", color="green", linewidth=1.5)
        plt.legend()
        plt.title("ACM Delta LUT YSH by H")
        plt.xlabel("Hue")
        plt.ylabel("Delta Y/S/H")
        plt.grid(True, linestyle=":", alpha=0.7)
        plt.savefig(f"{dir}/lut_delta_yshbyh_x{self.len_h}.png", dpi=600, bbox_inches="tight")

        plt.imsave(f"{dir}/lut_gain_ybyy_{self.len_hd}x{self.len_y}.png", self.lut_gain_ybyy, cmap='gray')
        plt.imsave(f"{dir}/lut_gain_sbyy_{self.len_hd}x{self.len_y}.png", self.lut_gain_sbyy, cmap='gray')
        plt.imsave(f"{dir}/lut_gain_hbyy_{self.len_hd}x{self.len_y}.png", self.lut_gain_hbyy, cmap='gray')
        plt.imsave(f"{dir}/lut_gain_ybys_{self.len_hd}x{self.len_s}.png", self.lut_gain_ybys, cmap='gray')
        plt.imsave(f"{dir}/lut_gain_sbys_{self.len_hd}x{self.len_s}.png", self.lut_gain_sbys, cmap='gray')
        plt.imsave(f"{dir}/lut_gain_hbys_{self.len_hd}x{self.len_s}.png", self.lut_gain_hbys, cmap='gray')

        plt.close()
        print(f"[ACM] dump LUT images to {dir}.")

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
