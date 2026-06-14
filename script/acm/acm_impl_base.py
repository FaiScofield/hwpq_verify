"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : acm_impl_base.py
Author      : vance.wu@rock-chips.com
Date        : 2026-06-14
Description : Base class for ACM implementation, providing LUT management,
              YUV<=>YHS conversion (trig or cordic), and ACM processing for
              8bit / 10bit YUV444 planar images.
LastEditTime: 2026-06-14
"""

import os
import sys
import json
import cv2
import argparse
import traceback
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
def round_rshift(value, shift: int):
    if shift > 0:
        half = 1 << (shift - 1)
        ret = (np.abs(value) + half) >> shift
        return np.copysign(ret, value).astype(ret.dtype)
    return value << -shift


def gaussian_down_sample(arr: np.ndarray, out_size, kernel: np.ndarray = None):
    # use default 5x5 kernel if not set
    if kernel is None:
        kernel = np.array([1, 4, 6, 4, 1], dtype=np.float32)
        kernel = np.outer(kernel, kernel)
        kernel = kernel / kernel.sum()

    H, W = arr.shape
    out_rows, out_cols = out_size
    kh, kw = kernel.shape

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
            kernel_sum = 0.0

            for ky in range(kh):
                src_y = (start_y + ky + H) % H  # cyclic along H
                for kx in range(kw):
                    src_x = np.clip(start_x + kx, 0, W - 1)  # replicate along W
                    conv_sum += arr[src_y, src_x] * kernel[ky, kx]
                    kernel_sum += kernel[ky, kx]

            if kernel_sum > 0:
                dst[y, x] = conv_sum / kernel_sum
            else:
                dst[y, x] = 0

    return dst


def linear_resize_array_1d(arr: np.ndarray, new_length: int):
    if len(arr) == 0:
        raise ValueError("Empty 1D array input!")

    if new_length == len(arr):
        return np.array(arr)

    x_old = np.linspace(0, 1, len(arr))
    x_new = np.linspace(0, 1, new_length)
    new_arr = np.interp(x_new, x_old, arr)

    return new_arr


def linear_resize_array_2d(mat: np.ndarray, new_rows: int, new_cols: int, kernel: np.ndarray = None):
    if mat.size == 0 or mat.shape[0] == 0 or mat.shape[1] == 0:
        raise ValueError("Invalid 2D array input!")

    old_rows, old_cols = mat.shape
    if old_rows == new_rows and old_cols == new_cols:
        return mat.copy()

    if new_cols * new_rows > old_rows * old_cols:
        # scale up, use bilinear interpolation
        new_mat = cv2.resize(mat.astype(np.float32), (new_cols, new_rows), interpolation=cv2.INTER_LINEAR)
    else:
        # scale down
        if kernel is not None:
            # use custom filter kernel
            new_mat = gaussian_down_sample(mat.astype(np.float32), (new_rows, new_cols), kernel)
        else:
            # use AREA interpolation (ONLY support uint8, uint16, float32)
            new_mat = cv2.resize(mat.astype(np.float32), (new_cols, new_rows), interpolation=cv2.INTER_AREA)

    return new_mat.astype(mat.dtype)


def bicubic_resize_array_1d(arr: np.ndarray, new_length: int):
    """Bicubic resize for 1D array, goes through 2D path of cv2.resize."""
    if len(arr) == 0:
        raise ValueError("Empty 1D array input!")
    if new_length == len(arr):
        return np.array(arr)
    if new_length == 1:
        return np.array([arr[0]], dtype=arr.dtype)
    mat = arr.reshape(1, -1).astype(np.float32)
    new_mat = cv2.resize(mat, (new_length, 1), interpolation=cv2.INTER_CUBIC)
    return new_mat.reshape(-1).astype(arr.dtype)


def bicubic_resize_array_2d(mat: np.ndarray, new_rows: int, new_cols: int, kernel: np.ndarray = None):
    """Bicubic resize for 2D array. The ``kernel`` argument is accepted for API
    parity with :func:`linear_resize_array_2d` but is not used (cv2 bicubic
    interpolation is not a separable filter).
    """
    if mat.size == 0 or mat.shape[0] == 0 or mat.shape[1] == 0:
        raise ValueError("Invalid 2D array input!")
    old_rows, old_cols = mat.shape
    if old_rows == new_rows and old_cols == new_cols:
        return mat.copy()
    new_mat = cv2.resize(mat.astype(np.float32), (new_cols, new_rows), interpolation=cv2.INTER_CUBIC)
    return new_mat.astype(mat.dtype)


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

# default (canonical) length range — used during construction / load_json
LEN_Y_DEFAULT_MIN = 2
LEN_Y_DEFAULT_MAX = 256   # 255 + 1
LEN_S_DEFAULT_MIN = 2
LEN_S_DEFAULT_MAX = 182   # 181 + 1
LEN_H_DEFAULT_MIN = 2
LEN_H_DEFAULT_MAX = 361   # 360 + 1

# current (runtime / UI) length range — used by set_len
LEN_Y_MIN = 4
LEN_Y_MAX = 128           # 127 + 1
LEN_S_MIN = 4
LEN_S_MAX = 91            # 90 + 1
LEN_H_MIN = 5             # 4 + 1
LEN_H_MAX = 361           # 360 + 1
LEN_H2_MIN = 4

# ---------------------------------------------------------------------------
# LUT value ranges
# ---------------------------------------------------------------------------

# signed delta ranges (semantic; stored as int16)
DELTA_Y_MIN = -255
DELTA_Y_MAX = 255
DELTA_S_MIN = -255
DELTA_S_MAX = 255
DELTA_H_MIN = -64
DELTA_H_MAX = 64

# 2D gain values (stored as int8)
GAIN_MIN = -128
GAIN_MAX = 127

# full data ranges used for LUT index mapping
Y_FULL_RANGE = 255
S_FULL_RANGE = 181
H_FULL_RANGE = 360


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

    # LUT numeric ranges shared by load/dump & runtime computation
    _DELTA_Y_RANGE = DELTA_Y_MAX - DELTA_Y_MIN + 1  # 256, [-255, 255]
    _DELTA_S_RANGE = DELTA_S_MAX - DELTA_S_MIN + 1  # 256, [-255, 255]
    _DELTA_H_RANGE = DELTA_H_MAX - DELTA_H_MIN + 1  # 64, [-64, 64] degrees
    _GAIN_RANGE = 128  # LUT stores int8 in [-128, 127]; half-range for scaling
    # delta scaling factors per mode
    _DELTA_MODE_SCALE = {
        "rk": {"y": 0.25, "s": 0.25, "h": 1.0},
        "evideo": {"y": 1.0, "s": 1.0, "h": 1.0},
    }

    def __init__(self, len_y: int = 9, len_s: int = 13, len_h: int = 65, len_h2: int = 0,
                 delta_mode: str = "rk", yuv_method: str = "trig"):
        # --- mode / method ---
        assert delta_mode in self._DELTA_MODE_SCALE, f"unknown delta_mode: {delta_mode}"
        assert yuv_method in ("trig", "cordic"), f"unknown yuv_method: {yuv_method}"
        self.delta_mode = delta_mode
        self.yuv_method = yuv_method

        # --- gains ---
        self.gain_y = 256  # [0, (256), 1023], 8bit fixed
        self.gain_s = 256
        self.gain_h = 256

        self.rand_seed = -1
        self.b_lut_ready = False

        # --- default length config (canonical) ---
        self._default_len_y = utl.clamp(len_y, LEN_Y_DEFAULT_MIN, LEN_Y_DEFAULT_MAX)
        self._default_len_s = utl.clamp(len_s, LEN_S_DEFAULT_MIN, LEN_S_DEFAULT_MAX)
        self._default_len_h = utl.clamp(len_h, LEN_H_DEFAULT_MIN, LEN_H_DEFAULT_MAX)
        self._default_len_h2 = (self._default_len_h if len_h2 <= 0
                                else utl.clamp(len_h2, LEN_H_DEFAULT_MIN, self._default_len_h))
        self._default_step_y = Y_FULL_RANGE / (self._default_len_y - 1)
        self._default_step_s = S_FULL_RANGE / (self._default_len_s - 1)
        self._default_step_h = H_FULL_RANGE / (self._default_len_h - 1)
        self._default_step_h2 = H_FULL_RANGE / (self._default_len_h2 - 1)

        # --- current length config (runtime, may be resampled) ---
        self._init_current_len()

        # --- LUT sets (default + current) ---
        self._init_default_luts()
        self._init_current_luts()

        self._print_len("default", self._default_len_y, self._default_len_s,
                        self._default_len_h, self._default_len_h2)
        self._print_len("current", self.len_y, self.len_s, self.len_h, self.len_h2)
        print(f"[ACM] delta_mode={self.delta_mode}, yuv_method={self.yuv_method}")

    # ------------------------------------------------------------------
    # length / LUT init helpers
    # ------------------------------------------------------------------
    def _init_current_len(self):
        self.len_y = self._default_len_y
        self.len_s = self._default_len_s
        self.len_h = self._default_len_h
        self.len_h2 = self._default_len_h2
        self.step_y = self._default_step_y
        self.step_s = self._default_step_s
        self.step_h = self._default_step_h
        self.step_h2 = self._default_step_h2

    def _init_default_luts(self):
        self._default_lut_delta_ybyh = np.zeros(self._default_len_h, dtype=np.int16)
        self._default_lut_delta_sbyh = np.zeros(self._default_len_h, dtype=np.int16)
        self._default_lut_delta_hbyh = np.zeros(self._default_len_h, dtype=np.int16)
        for name in LUT_2D_Y_NAMES:
            setattr(self, f"_default_{name}",
                    np.zeros((self._default_len_h2, self._default_len_y), dtype=np.int8))
        for name in LUT_2D_S_NAMES:
            setattr(self, f"_default_{name}",
                    np.zeros((self._default_len_h2, self._default_len_s), dtype=np.int8))

    def _init_current_luts(self):
        self.lut_delta_ybyh = self._default_lut_delta_ybyh.copy()
        self.lut_delta_sbyh = self._default_lut_delta_sbyh.copy()
        self.lut_delta_hbyh = self._default_lut_delta_hbyh.copy()
        for name in LUT_2D_Y_NAMES:
            setattr(self, f"lut_{name}",
                    getattr(self, f"_default_{name}").copy())
        for name in LUT_2D_S_NAMES:
            setattr(self, f"lut_{name}",
                    getattr(self, f"_default_{name}").copy())
        self.b_lut_ready = True

    @staticmethod
    def _print_len(tag, y, s, h, h2):
        print(f"[ACM] {tag} lut len: y={y}, s={s}, h={h}, h2={h2}")

    # ------------------------------------------------------------------
    # public configuration setters
    # ------------------------------------------------------------------
    def set_len(self, len_y: int, len_s: int, len_h: int, len_h2: int = 0,
                kernel: np.ndarray = None):
        """Change current LUT length. Resamples from default set using bicubic."""
        self.len_y = utl.clamp(len_y, LEN_Y_MIN, LEN_Y_MAX)
        self.len_s = utl.clamp(len_s, LEN_S_MIN, LEN_S_MAX)
        self.len_h = utl.clamp(len_h, LEN_H_MIN, LEN_H_MAX)
        self.len_h2 = (self.len_h if len_h2 <= 0
                       else utl.clamp(len_h2, LEN_H2_MIN, self.len_h))
        self.step_y = Y_FULL_RANGE / (self.len_y - 1)
        self.step_s = S_FULL_RANGE / (self.len_s - 1)
        self.step_h = H_FULL_RANGE / (self.len_h - 1)
        self.step_h2 = H_FULL_RANGE / (self.len_h2 - 1)
        print(f"[ACM] set current lut len: y={self.len_y}, s={self.len_s}, "
              f"h={self.len_h}, h2={self.len_h2}")
        self._resample_default_to_current(kernel, method="bicubic")

    def set_step(self, step_y: float, step_s: float, step_h: float, step_h2: float = 0.0,
                 kernel: np.ndarray = None):
        self.step_y = utl.clamp(step_y, 2.0, Y_FULL_RANGE / (LEN_Y_MIN - 1))
        self.step_s = utl.clamp(step_s, 2.0, S_FULL_RANGE / (LEN_S_MIN - 1))
        self.step_h = utl.clamp(step_h, 2.0, H_FULL_RANGE / (LEN_H_MIN - 1))
        self.step_h2 = self.step_h if step_h2 <= 0.0 else min(
            H_FULL_RANGE / (LEN_H_MIN - 1), max(step_h2, step_h))
        self.len_y = round(Y_FULL_RANGE / self.step_y) + 1
        self.len_s = round(S_FULL_RANGE / self.step_s) + 1
        self.len_h = round(H_FULL_RANGE / self.step_h) + 1
        self.len_h2 = round(H_FULL_RANGE / self.step_h2) + 1
        print(f"[ACM] set current lut step: y={self.step_y:.4f}, s={self.step_s:.4f}, "
              f"h={self.step_h:.4f}, h2={self.step_h2:.4f}")
        self._resample_default_to_current(kernel, method="bicubic")

    def set_gain(self, gain_y: int, gain_s: int, gain_h: int):
        self.gain_y = gain_y
        self.gain_s = gain_s
        self.gain_h = gain_h
        print(f"[ACM] set lut gain: y={self.gain_y}, s={self.gain_s}, h={self.gain_h}")

    def set_delta_mode(self, mode: str):
        """Switch delta mapping mode ("rk" or "evideo")."""
        if mode not in self._DELTA_MODE_SCALE:
            raise ValueError(f"unknown delta_mode: {mode}, expect one of {list(self._DELTA_MODE_SCALE)}")
        self.delta_mode = mode
        print(f"[ACM] set delta_mode: {self.delta_mode}")

    def set_yuv_method(self, method: str):
        """Switch YUV<=>YHS conversion method ("trig" or "cordic")."""
        if method not in ("trig", "cordic"):
            raise ValueError(f"unknown yuv_method: {method}, expect 'trig' or 'cordic'")
        self.yuv_method = method
        print(f"[ACM] set yuv_method: {self.yuv_method}")

    # ------------------------------------------------------------------
    # resampling between default <-> current
    # ------------------------------------------------------------------
    def _resample_default_to_current(self, kernel: np.ndarray = None, method: str = "bicubic"):
        """Resample default LUTs into the current length config."""
        resample_1d = bicubic_resize_array_1d if method == "bicubic" else linear_resize_array_1d
        resample_2d = bicubic_resize_array_2d if method == "bicubic" else linear_resize_array_2d

        if self._default_lut_delta_ybyh.shape[0] != self.len_h:
            self.lut_delta_ybyh = np.clip(resample_1d(
                self._default_lut_delta_ybyh, self.len_h),
                DELTA_Y_MIN, DELTA_Y_MAX).astype(np.int16)
            self.lut_delta_sbyh = np.clip(resample_1d(
                self._default_lut_delta_sbyh, self.len_h),
                DELTA_S_MIN, DELTA_S_MAX).astype(np.int16)
            self.lut_delta_hbyh = np.clip(resample_1d(
                self._default_lut_delta_hbyh, self.len_h),
                DELTA_H_MIN, DELTA_H_MAX).astype(np.int16)
            print(f"[ACM] resample delta LUT: {self._default_len_h} => {self.len_h} ({method})")

        for name in LUT_2D_Y_NAMES:
            default_lut = getattr(self, f"_default_{name}")
            if default_lut.shape != (self.len_h2, self.len_y):
                new_lut = resample_2d(default_lut, self.len_h2, self.len_y, kernel)
                setattr(self, f"lut_{name}", new_lut)
                print(f"[ACM] resample {name}: {default_lut.shape} => {new_lut.shape} ({method})")
        for name in LUT_2D_S_NAMES:
            default_lut = getattr(self, f"_default_{name}")
            if default_lut.shape != (self.len_h2, self.len_s):
                new_lut = resample_2d(default_lut, self.len_h2, self.len_s, kernel)
                setattr(self, f"lut_{name}", new_lut)
                print(f"[ACM] resample {name}: {default_lut.shape} => {new_lut.shape} ({method})")

    def sync_to_default(self):
        """Resample current LUTs back to the default length config.

        Useful when the user has edited the current LUTs in-place at a custom
        resolution and wants to promote those changes to the default set.
        Uses bicubic interpolation to preserve the shape of edits.
        """
        # 1D delta LUTs
        if self._default_lut_delta_ybyh.shape[0] != self.lut_delta_ybyh.shape[0]:
            self._default_lut_delta_ybyh = np.clip(bicubic_resize_array_1d(
                self.lut_delta_ybyh, self._default_len_h),
                DELTA_Y_MIN, DELTA_Y_MAX).astype(np.int16)
            self._default_lut_delta_sbyh = np.clip(bicubic_resize_array_1d(
                self.lut_delta_sbyh, self._default_len_h),
                DELTA_S_MIN, DELTA_S_MAX).astype(np.int16)
            self._default_lut_delta_hbyh = np.clip(bicubic_resize_array_1d(
                self.lut_delta_hbyh, self._default_len_h),
                DELTA_H_MIN, DELTA_H_MAX).astype(np.int16)
            print(f"[ACM] sync delta LUT to default: {self.lut_delta_ybyh.shape[0]} "
                  f"=> {self._default_len_h}")
        else:
            self._default_lut_delta_ybyh = self.lut_delta_ybyh.copy()
            self._default_lut_sbyh = self.lut_delta_sbyh.copy()
            self._default_lut_hbyh = self.lut_delta_hbyh.copy()

        # 2D gain LUTs
        for name in LUT_2D_Y_NAMES:
            current = getattr(self, f"lut_{name}")
            default_lut = getattr(self, f"_default_{name}")
            if current.shape != default_lut.shape:
                setattr(self, f"_default_{name}",
                        bicubic_resize_array_2d(current, default_lut.shape[0], default_lut.shape[1]))
        for name in LUT_2D_S_NAMES:
            current = getattr(self, f"lut_{name}")
            default_lut = getattr(self, f"_default_{name}")
            if current.shape != default_lut.shape:
                setattr(self, f"_default_{name}",
                        bicubic_resize_array_2d(current, default_lut.shape[0], default_lut.shape[1]))

    # ------------------------------------------------------------------
    # YUV <-> YHS conversion helpers
    # ------------------------------------------------------------------
    def _cbcr_to_hs(self, cb, cr, depth_uv: int, use_cordic: bool):
        """Convert signed Cb/Cr to H (deg in [0, 360)), S and H (rad in [-pi, pi]).

        When use_cordic is True, h_rad is None (cordic path uses h_deg directly).
        """
        if use_cordic:
            h, s, _, _ = cordic.cordic_cbcr2hs(cb, cr, depth_uv, 13, 8, False)
            h_deg = h + 180
            return s, h_deg, None
        s = (np.sqrt(cb * cb + cr * cr) + 0.5).astype(np.int32)
        h_rad = np.arctan2(cr, cb)  # [-pi, pi]
        h_deg = (np.rad2deg(h_rad) + 180 + 0.5).astype(np.int32)  # [0, 360]
        return s, h_deg, h_rad

    def _use_cordic(self) -> bool:
        return self.yuv_method == "cordic"

    # ------------------------------------------------------------------
    # ACM processing
    # ------------------------------------------------------------------
    def do_acm_u8(self, yuv444p_in: np.ndarray, use_cordic: bool = None):
        """Apply ACM to an 8bit YUV444p image. Returns YUV444p uint8."""
        print("[ACM] doing ACM LUT for u8 image...")
        if use_cordic is None:
            use_cordic = self._use_cordic()

        H, W, _ = yuv444p_in.shape
        y = yuv444p_in[:, :, 0].astype(np.int32)
        cb = yuv444p_in[:, :, 1].astype(np.int32) - 128
        cr = yuv444p_in[:, :, 2].astype(np.int32) - 128
        s, h_deg, h_rad = self._cbcr_to_hs(cb, cr, depth_uv=8, use_cordic=use_cordic)

        yuv444p_out = self._do_acm(y, cb, cr, s, h_deg, h_rad,
                                   depth_uv=8, y_range=256, cbcr_center=128,
                                   use_cordic=use_cordic)
        print("[ACM] do ACM LUT for u8 image done.")
        return yuv444p_out

    def do_acm_u10(self, yuv444p_in: np.ndarray, use_cordic: bool = None):
        """Apply ACM to a 10bit YUV444p image. Returns YUV444p uint16.

        10bit convention: full range [0, 1023], Cb/Cr center 512, S range
        [0, 724].  Delta ranges are kept identical to the 8bit path (S23
        bit-width), the final Y/Cb/Cr are clipped to the 10bit range so the
        result is equivalent to running on 8bit data and shifting by 2.
        """
        print("[ACM] doing ACM LUT for u10 image...")
        if use_cordic is None:
            use_cordic = self._use_cordic()

        assert yuv444p_in.dtype == np.uint16, "do_acm_u10 expects uint16 input"
        H, W, _ = yuv444p_in.shape
        y = yuv444p_in[:, :, 0].astype(np.int32)
        cb = yuv444p_in[:, :, 1].astype(np.int32) - 512
        cr = yuv444p_in[:, :, 2].astype(np.int32) - 512
        s, h_deg, h_rad = self._cbcr_to_hs(cb, cr, depth_uv=10, use_cordic=use_cordic)

        yuv444p_out = self._do_acm(y, cb, cr, s, h_deg, h_rad,
                                   depth_uv=10, y_range=1024, cbcr_center=512,
                                   use_cordic=use_cordic)
        print("[ACM] do ACM LUT for u10 image done.")
        return yuv444p_out

    def _do_acm(self, y, cb, cr, s, h_deg, h_rad, depth_uv, y_range, cbcr_center, use_cordic):
        # depth-dependent full-scale ranges
        # u8:  Y in [0,255], S in [0,181];  u10: Y in [0,1023], S in [0,724]
        y_max = float(y_range - 1)
        s_max = 181.0 if depth_uv == 8 else 724.0

        # mode-dependent scale (delta_y *= 0.25 for rk mode, *1.0 for evideo)
        scl = self._DELTA_MODE_SCALE[self.delta_mode]

        local_lut_delta_ybyh = round_rshift(self.lut_delta_ybyh.astype(np.int32) * self.gain_y, 8)
        local_lut_delta_sbyh = round_rshift(self.lut_delta_sbyh.astype(np.int32) * self.gain_s, 8)
        local_lut_delta_hbyh = round_rshift(self.lut_delta_hbyh.astype(np.int32) * self.gain_h, 8)
        local_lut_delta_ybyh = np.clip(local_lut_delta_ybyh, DELTA_Y_MIN, DELTA_Y_MAX)
        local_lut_delta_sbyh = np.clip(local_lut_delta_sbyh, DELTA_S_MIN, DELTA_S_MAX)
        local_lut_delta_hbyh = np.clip(local_lut_delta_hbyh, DELTA_H_MIN, DELTA_H_MAX)

        idx_y = y.astype(np.float32) / (y_max / (self.len_y - 1)) if self.len_y > 1 else np.zeros_like(y, dtype=np.float32)
        idx_s = s.astype(np.float32) / (s_max / (self.len_s - 1)) if self.len_s > 1 else np.zeros_like(s, dtype=np.float32)
        idx_h = h_deg.astype(np.float32) / self.step_h
        idx_h2 = h_deg.astype(np.float32) / self.step_h2

        # NOTE: cv2.remap does not support int32 for bilinear interpolation
        idx_zeros = np.zeros_like(idx_h)
        delta_y = cv2.remap(
            local_lut_delta_ybyh.astype(np.float32) * scl["y"],
            idx_h, idx_zeros,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE)
        delta_s = cv2.remap(
            local_lut_delta_sbyh.astype(np.float32) * scl["s"] / 255.0 * s_max,
            idx_h, idx_zeros,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE)
        delta_h = cv2.remap(
            local_lut_delta_hbyh.astype(np.float32) * scl["h"],
            idx_h, idx_zeros,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE)
        gain_yy = cv2.remap(self.lut_gain_ybyy.astype(np.float32),
                            idx_y, idx_h2, interpolation=cv2.INTER_LINEAR,
                            borderMode=cv2.BORDER_REPLICATE)
        gain_ys = cv2.remap(self.lut_gain_sbyy.astype(np.float32),
                            idx_y, idx_h2, interpolation=cv2.INTER_LINEAR,
                            borderMode=cv2.BORDER_REPLICATE)
        gain_yh = cv2.remap(self.lut_gain_hbyy.astype(np.float32),
                            idx_y, idx_h2, interpolation=cv2.INTER_LINEAR,
                            borderMode=cv2.BORDER_REPLICATE)
        gain_sy = cv2.remap(self.lut_gain_ybys.astype(np.float32),
                            idx_s, idx_h2, interpolation=cv2.INTER_LINEAR,
                            borderMode=cv2.BORDER_REPLICATE)
        gain_ss = cv2.remap(self.lut_gain_sbys.astype(np.float32),
                            idx_s, idx_h2, interpolation=cv2.INTER_LINEAR,
                            borderMode=cv2.BORDER_REPLICATE)
        gain_sh = cv2.remap(self.lut_gain_hbys.astype(np.float32),
                            idx_s, idx_h2, interpolation=cv2.INTER_LINEAR,
                            borderMode=cv2.BORDER_REPLICATE)

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

    # ------------------------------------------------------------------
    # load_json / dump_json
    # ------------------------------------------------------------------
    def load_json(self, filename: str):
        if not os.path.exists(filename):
            print(f"[ACM] config file '{filename}' doesn't exist!")
            return False
        if not filename.endswith(".json"):
            print(f"[ACM] config file '{filename}' is not a json file!")
            return False

        len_y = 9
        len_s = 13
        len_h = 65
        len_h2 = 65
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

                ## guess lut length from the file
                len_h = data["lutLengthH"] if "lutLengthH" in data else len(lut_delta_ybyh)
                if len(lut_gain_ybyy) == 65 * 9 and len(lut_gain_ybys) == 65 * 13:
                    len_y, len_s, len_h2 = 9, 13, 65
                elif len(lut_gain_ybyy) == 17 * 9 and len(lut_gain_ybys) == 17 * 13:
                    len_y, len_s, len_h2 = 9, 13, 17
                elif all(k in data for k in ("lutLengthY", "lutLengthS", "lutLengthHD")):
                    len_y = data["lutLengthY"]
                    len_s = data["lutLengthS"]
                    len_h2 = data["lutLengthHD"]
                else:
                    print("WARNING: unknown len_y/s/h2 !!! use default value.")

                if lut2dAxis4HD:
                    lut_gain_ybyy = lut_gain_ybyy.reshape(len_y, len_h2).T
                    lut_gain_sbyy = lut_gain_sbyy.reshape(len_y, len_h2).T
                    lut_gain_hbyy = lut_gain_hbyy.reshape(len_y, len_h2).T
                    lut_gain_ybys = lut_gain_ybys.reshape(len_s, len_h2).T
                    lut_gain_sbys = lut_gain_sbys.reshape(len_s, len_h2).T
                    lut_gain_hbys = lut_gain_hbys.reshape(len_s, len_h2).T
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)[-1]
            print(f"[ACM] load config '{filename}' failed in "
                  f"'{os.path.basename(tb.filename)}'-{tb.lineno}: {e}")

        ## shape validations
        if len(lut_delta_ybyh) != len_h:
            raise ValueError(f"length of lut_delta_ybyh({len(lut_delta_ybyh)}) != len_h({len_h})!")
        if len(lut_delta_sbyh) != len_h:
            raise ValueError(f"length of lut_delta_sbyh({len(lut_delta_sbyh)}) != len_h({len_h})!")
        if len(lut_delta_hbyh) != len_h:
            raise ValueError(f"length of lut_delta_hbyh({len(lut_delta_hbyh)}) != len_h({len_h})!")
        if len(lut_gain_ybyy) != len_h2 * len_y:
            raise ValueError(f"length of lut_gain_ybyy({len(lut_gain_ybyy)}) != len_h2({len_h2}) x len_y({len_y})!")
        if len(lut_gain_sbyy) != len_h2 * len_y:
            raise ValueError(f"length of lut_gain_sbyy({len(lut_gain_sbyy)}) != len_h2({len_h2}) x len_y({len_y})!")
        if len(lut_gain_hbyy) != len_h2 * len_y:
            raise ValueError(f"length of lut_gain_hbyy({len(lut_gain_hbyy)}) != len_h2({len_h2}) x len_y({len_y})!")
        if len(lut_gain_ybys) != len_h2 * len_s:
            raise ValueError(f"length of lut_gain_ybys({len(lut_gain_ybys)}) != len_h2({len_h2}) x len_s({len_s})!")
        if len(lut_gain_sbys) != len_h2 * len_s:
            raise ValueError(f"length of lut_gain_sbys({len(lut_gain_sbys)}) != len_h2({len_h2}) x len_s({len_s})!")
        if len(lut_gain_hbys) != len_h2 * len_s:
            raise ValueError(f"length of lut_gain_hbys({len(lut_gain_hbys)}) != len_h2({len_h2}) x len_s({len_s})!")

        lut_gain_ybyy = lut_gain_ybyy.reshape(len_h2, len_y)
        lut_gain_sbyy = lut_gain_sbyy.reshape(len_h2, len_y)
        lut_gain_hbyy = lut_gain_hbyy.reshape(len_h2, len_y)
        lut_gain_ybys = lut_gain_ybys.reshape(len_h2, len_s)
        lut_gain_sbys = lut_gain_sbys.reshape(len_h2, len_s)
        lut_gain_hbys = lut_gain_hbys.reshape(len_h2, len_s)

        ## resample the loaded LUTs to the default length (if they differ)
        target_h = self._default_len_h
        target_h2 = self._default_len_h2
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
        self._default_lut_delta_ybyh = np.clip(lut_delta_ybyh, DELTA_Y_MIN, DELTA_Y_MAX).astype(np.int16)
        self._default_lut_delta_sbyh = np.clip(lut_delta_sbyh, DELTA_S_MIN, DELTA_S_MAX).astype(np.int16)
        self._default_lut_delta_hbyh = np.clip(lut_delta_hbyh, DELTA_H_MIN, DELTA_H_MAX).astype(np.int16)
        self._default_lut_gain_ybyy = np.clip(lut_gain_ybyy, GAIN_MIN, GAIN_MAX).astype(np.int8)
        self._default_lut_gain_sbyy = np.clip(lut_gain_sbyy, GAIN_MIN, GAIN_MAX).astype(np.int8)
        self._default_lut_gain_hbyy = np.clip(lut_gain_hbyy, GAIN_MIN, GAIN_MAX).astype(np.int8)
        self._default_lut_gain_ybys = np.clip(lut_gain_ybys, GAIN_MIN, GAIN_MAX).astype(np.int8)
        self._default_lut_gain_sbys = np.clip(lut_gain_sbys, GAIN_MIN, GAIN_MAX).astype(np.int8)
        self._default_lut_gain_hbys = np.clip(lut_gain_hbys, GAIN_MIN, GAIN_MAX).astype(np.int8)

        self._resample_default_to_current(method="bicubic")
        self.b_lut_ready = True
        print("[ACM] load config done.")
        return True

    def dump_json(self, filename: str = ""):
        data = {
            "version": (f"acm_impl_var_lut_rand_seed_{self.rand_seed}"
                        if self.rand_seed > 0 else "acm_impl_var_lut"),
            "acmEnable": 1,
            "acmTableDeltaYbyH": utl.NoIndent(self._default_lut_delta_ybyh.flatten().tolist()),
            "acmTableDeltaHbyH": utl.NoIndent(self._default_lut_delta_hbyh.flatten().tolist()),
            "acmTableDeltaSbyH": utl.NoIndent(self._default_lut_delta_sbyh.flatten().tolist()),
            "acmTableGainYbyY": utl.NoIndent(self._default_lut_gain_ybyy.flatten().tolist()),
            "acmTableGainHbyY": utl.NoIndent(self._default_lut_gain_hbyy.flatten().tolist()),
            "acmTableGainSbyY": utl.NoIndent(self._default_lut_gain_sbyy.flatten().tolist()),
            "acmTableGainYbyS": utl.NoIndent(self._default_lut_gain_ybys.flatten().tolist()),
            "acmTableGainHbyS": utl.NoIndent(self._default_lut_gain_sbys.flatten().tolist()),
            "acmTableGainSbyS": utl.NoIndent(self._default_lut_gain_hbys.flatten().tolist()),
            "lumGain": self.gain_y,
            "hueGain": self.gain_h,
            "satGain": self.gain_s,
            "lutLengthY": self._default_len_y,
            "lutLengthS": self._default_len_s,
            "lutLengthH": self._default_len_h,
            "lutLengthHD": self._default_len_h2,
            "lutStepY": self._default_step_y,
            "lutStepS": self._default_step_s,
            "lutStepH": self._default_step_h,
            "lutStepHD": self._default_step_h2,
            "lut2dAxis4HD": (0 if self._default_lut_gain_ybyy.shape[0] == self._default_len_h2 else 1),
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

    def dump_lut(self, dir: str):
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

        plt.imsave(f"{dir}/lut_gain_ybyy_{self.len_h2}x{self.len_y}.png", self.lut_gain_ybyy, cmap='gray')
        plt.imsave(f"{dir}/lut_gain_sbyy_{self.len_h2}x{self.len_y}.png", self.lut_gain_sbyy, cmap='gray')
        plt.imsave(f"{dir}/lut_gain_hbyy_{self.len_h2}x{self.len_y}.png", self.lut_gain_hbyy, cmap='gray')
        plt.imsave(f"{dir}/lut_gain_ybys_{self.len_h2}x{self.len_s}.png", self.lut_gain_ybys, cmap='gray')
        plt.imsave(f"{dir}/lut_gain_sbys_{self.len_h2}x{self.len_s}.png", self.lut_gain_sbys, cmap='gray')
        plt.imsave(f"{dir}/lut_gain_hbys_{self.len_h2}x{self.len_s}.png", self.lut_gain_hbys, cmap='gray')

        plt.close()
        print(f"[ACM] dump LUT images to {dir}.")

    def gen_test_config(self, b_strict: bool = True, random_seed: int = 114514):
        if not self.b_lut_ready:
            return False

        np.random.seed(random_seed)
        tmp_lut_gain_ybyy = np.random.normal(0.0, 64.0, size=(self._default_len_h2, self._default_len_y)) * 16
        tmp_lut_gain_sbyy = np.random.normal(0.0, 64.0, size=(self._default_len_h2, self._default_len_y)) * 16
        tmp_lut_gain_hbyy = np.random.normal(0.0, 64.0, size=(self._default_len_h2, self._default_len_y)) * 16
        tmp_lut_gain_ybys = np.random.normal(0.0, 64.0, size=(self._default_len_h2, self._default_len_s)) * 16
        tmp_lut_gain_sbys = np.random.normal(0.0, 64.0, size=(self._default_len_h2, self._default_len_s)) * 16
        tmp_lut_gain_hbys = np.random.normal(0.0, 64.0, size=(self._default_len_h2, self._default_len_s)) * 16
        tmp_lut_gain_ybyy = cv2.GaussianBlur(tmp_lut_gain_ybyy, ksize=(0, 0), sigmaX=3.0, sigmaY=3.0)
        tmp_lut_gain_sbyy = cv2.GaussianBlur(tmp_lut_gain_sbyy, ksize=(0, 0), sigmaX=3.0, sigmaY=3.0)
        tmp_lut_gain_hbyy = cv2.GaussianBlur(tmp_lut_gain_hbyy, ksize=(0, 0), sigmaX=3.0, sigmaY=3.0)
        tmp_lut_gain_ybys = cv2.GaussianBlur(tmp_lut_gain_ybys, ksize=(0, 0), sigmaX=3.0, sigmaY=3.0)
        tmp_lut_gain_sbys = cv2.GaussianBlur(tmp_lut_gain_sbys, ksize=(0, 0), sigmaX=3.0, sigmaY=3.0)
        tmp_lut_gain_hbys = cv2.GaussianBlur(tmp_lut_gain_hbys, ksize=(0, 0), sigmaX=3.0, sigmaY=3.0)
        self._default_lut_gain_ybyy = np.clip(tmp_lut_gain_ybyy, GAIN_MIN, GAIN_MAX).astype(np.int8)
        self._default_lut_gain_sbyy = np.clip(tmp_lut_gain_sbyy, GAIN_MIN, GAIN_MAX).astype(np.int8)
        self._default_lut_gain_hbyy = np.clip(tmp_lut_gain_hbyy, GAIN_MIN, GAIN_MAX).astype(np.int8)
        self._default_lut_gain_ybys = np.clip(tmp_lut_gain_ybys, GAIN_MIN, GAIN_MAX).astype(np.int8)
        self._default_lut_gain_sbys = np.clip(tmp_lut_gain_sbys, GAIN_MIN, GAIN_MAX).astype(np.int8)
        self._default_lut_gain_hbys = np.clip(tmp_lut_gain_hbys, GAIN_MIN, GAIN_MAX).astype(np.int8)

        tmp_lut_delta_ybyh = np.random.uniform(-1, 1, self._default_len_h).reshape(1, -1) * 300
        tmp_lut_delta_hbyh = np.random.uniform(-1, 1, self._default_len_h).reshape(1, -1) * 100
        tmp_lut_delta_sbyh = np.random.uniform(-1, 1, self._default_len_h).reshape(1, -1) * 300
        tmp_lut_delta_ybyh = cv2.GaussianBlur(tmp_lut_delta_ybyh, ksize=(5, 1), sigmaX=1.0)
        tmp_lut_delta_hbyh = cv2.GaussianBlur(tmp_lut_delta_hbyh, ksize=(5, 1), sigmaX=1.0)
        tmp_lut_delta_sbyh = cv2.GaussianBlur(tmp_lut_delta_sbyh, ksize=(5, 1), sigmaX=1.0)
        self._default_lut_delta_ybyh = np.clip(tmp_lut_delta_ybyh.flatten(), DELTA_Y_MIN, DELTA_Y_MAX).astype(np.int16)
        self._default_lut_delta_hbyh = np.clip(tmp_lut_delta_hbyh.flatten(), DELTA_H_MIN, DELTA_H_MAX).astype(np.int16)
        self._default_lut_delta_sbyh = np.clip(tmp_lut_delta_sbyh.flatten(), DELTA_S_MIN, DELTA_S_MAX).astype(np.int16)

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
