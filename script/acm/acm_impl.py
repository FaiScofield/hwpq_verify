"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : acm_impl.py
Author      : vance.wu@rock-chips.com
Date        : 2025-10-24
Description :
LastEditTime: 2025-11-25
"""

from ast import Not
import os
import sys
import json
import cv2
import argparse
import traceback
from matplotlib.pylab import f
import numpy as np
import matplotlib.pyplot as plt

# from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import utils as utl


def round_rshift(value, shift: int):
    if shift > 0:
        half = 1 << (shift - 1)
        ret = (np.abs(value) + half) >> shift
        return np.copysign(ret, value).astype(ret.dtype)
    return value << -shift


def sample1d_linear(arr: np.ndarray, idx: float):
    # arr: (N, C) or (N,)  idx: float
    n = arr.shape[0]
    if n == 0:
        raise ValueError("Empty 1D table")
    # clamp index to edge
    if idx <= 0:
        return arr[0]
    if idx >= n - 1:
        return arr[-1]

    i0 = int(np.floor(idx))
    i1 = min(i0 + 1, n - 1)
    w1 = idx - i0
    val = arr[i0] * (1.0 - w1) + arr[i1] * w1
    return int(val + 0.5 * np.sign(val))  # rount to nearest integer


def sample2d_linear(arr: np.ndarray, x: float, y: float):
    H, W = arr.shape

    # clamp coords
    x = utl.clamp(x, 0.0, W - 1.0)
    y = utl.clamp(y, 0.0, H - 1.0)
    x0 = int(np.floor(x))
    x1 = min(x0 + 1, W - 1)
    y0 = int(np.floor(y))
    y1 = min(y0 + 1, H - 1)
    wx = x - x0
    wy = y - y0
    v00 = float(arr[y0, x0])
    v10 = float(arr[y0, x1])
    v01 = float(arr[y1, x0])
    v11 = float(arr[y1, x1])
    top = v00 * (1.0 - wx) + v10 * wx
    bot = v01 * (1.0 - wx) + v11 * wx
    val = top * (1.0 - wy) + bot * wy
    return int(val + 0.5 * np.sign(val))  # rount to nearest integer


def linear_resize_array_1d(arr: np.ndarray, new_length: int):
    if len(arr) == 0:
        raise ValueError("Empty 1D array input!")

    if new_length == len(arr):
        return np.array(arr)

    x_old = np.linspace(0, 1, len(arr))
    x_new = np.linspace(0, 1, new_length)
    new_arr = np.interp(x_new, x_old, arr)

    # dir = "V:/hwpq_verify_data/vop_robin_fpga_verify_acm/test_var_lut/"
    # (arr + 64).astype(np.uint8).tofile(f"{dir}/old_lut_before_scaling_x{len(arr)}.yuv")
    # (new_arr + 64).astype(np.uint8).tofile(f"{dir}/new_lut_after_scaling_x{new_length}.yuv")

    return new_arr


def linear_resize_array_2d(mat: np.ndarray, new_rows: int, new_cols: int):
    if mat.size == 0 or mat.shape[0] == 0 or mat.shape[1] == 0:
        raise ValueError("Invalid 2D array input!")

    old_rows, old_cols = mat.shape
    if old_rows == new_rows and old_cols == new_cols:
        return mat.copy()

    # dir = "V:/hwpq_verify_data/vop_robin_fpga_verify_acm/test_var_lut/"
    # plt.imsave(f"{dir}/old_mat_before_scaling_{old_rows}x{old_cols}.png", mat, cmap='gray')

    if new_cols * new_rows > old_rows * old_cols:
        # scale up, use bilinear interpolation
        new_mat = cv2.resize(mat.astype(np.float32), (new_cols, new_rows), interpolation=cv2.INTER_LINEAR)
    else:
        # scale down, use AREA interpolation (ONLY support uint8, uint16, float32)
        new_mat = cv2.resize(mat.astype(np.float32), (new_cols, new_rows), interpolation=cv2.INTER_AREA)

    # plt.imsave(f"{dir}/new_mat_after_scaling_{new_rows}x{new_cols}.png", new_mat.astype(mat.dtype), cmap='gray')

    return new_mat.astype(mat.dtype)


CORDIC_FIX_BITS = 0
## u14 max, 8bit fixed: angle [45, 26.565, 14.036, ..., 0.006994, 0.003497] * 256
CORDIC_ATAN_LUT_FIX8 = [11520, 6801, 3593, 1824, 916, 458, 229, 115, 57, 29, 14, 7, 4, 2, 1]
CORDIC_COEF_K_FIX10 = 622  # 10bit fixed: 0.607252935 * 1024, (from K4 to K15 are all the same)
CORDIC_MAX_ITER_NUM = 15
CORDIC_DEG180_FIX8 = 180 << 8


def cordic_cbcr2hs(cb, cr, depth: int, iter_num: int = 13, increase_bits_for_s: int = 0):
    """
    depth: 8 or 10
    input cb range: [-128, 127] in S8 / [-512, 511] in S10
    input cr range: [-128, 127] in S8 / [-512, 511] in S10
    output h range: [-180, 180] in S8 / [-360, 360] in S10, add more 8bit fixed
    output s range: [  0,  181] in U8 / [   0, 724] in U10, add more 'increase_bits_for_s' fixed
    """
    assert depth >= 8

    ## at leat 7 times iterations make sure the error of the output angle is less than 1 degree
    iter_num = utl.clamp(iter_num, 7, 15)

    ## the depth of x & y should be > iter_num, otherwise, the remain (depth - iter_num) iterations will be useless!
    increase_bits_for_s = utl.clamp(increase_bits_for_s, 0, 8)
    if increase_bits_for_s + 8 <= iter_num:
        print(
            f"Warning: increase_bits_for_s({increase_bits_for_s}) + depth(8) <= iter_num({iter_num}), some iterations will be useless!"
        )
    fix_bits = increase_bits_for_s + 10

    ## swap to the first coordinate quadrant
    x = abs(cb) << increase_bits_for_s  # s20
    y = abs(cr) << increase_bits_for_s  # s20
    z = 0  # [0, 90] << 8

    mx = 0
    my = 0
    mz = 0

    ## cordic iteration
    for i in range(iter_num):
        d = (y < 0) * 2 - 1  # +y => -1 -y => +1
        xp = x - d * (y >> i)
        yp = y + d * (x >> i)
        zp = z - d * CORDIC_ATAN_LUT_FIX8[i]
        x = xp
        y = yp
        z = zp

        # mx = max(mx, abs(x))
        # my = max(my, abs(y))
        # mz = max(mz, abs(z))

    s = (CORDIC_COEF_K_FIX10 * x + (1 << fix_bits - 1)) >> fix_bits  # x=s/K, K=0.607252935
    if type(cb) == np.ndarray:
        h = np.where(s == 0, np.zeros_like(cb), np.maximum(z, 0))
    else:
        h = 0 if s == 0 else np.maximum(z, 0)  # z might be a little negative after cordic iteration

    '''
      return H value to four quadrants by input sign of UV
        | quadrant | x_y_in       | h_out   | s_out |
        | -------- | ------------ | ------- | ----- |
        |    1     | x0=+x, y0=+y | +z      | Kx    |
        |    2     | x0=-x, y0=+y | -(z-pi) | Kx    |
        |    3     | x0=-x, y0=-y | +(z-pi) | Kx    |
        |    4     | x0=+x, y0=-y | -z      | Kx    |
    '''
    cb_mask = cb >= 0
    cr_mask = cr >= 0
    cb_mask_pi = cb < 0  # +cb => 0, -cb => 1
    cb_mask_H = 2 * cb_mask - 1  # +cb => 1, -cb => -1
    cr_mask_H = 2 * cr_mask - 1  # +cr => 1, -cr => -1
    h = (CORDIC_DEG180_FIX8 * cb_mask_pi + h * cb_mask_H) * cr_mask_H

    # ofs = np.sign(h)
    h = (h + 128 + np.sign(h)) >> 8  # 8bit fixed

    return h, s, mx, my, mz


def cordic_hs2cbcr(h, s, depth: int, iter_num: int = 13, increase_bits_for_s: int = 3):
    """
    depth: 8 or 10
    input   h range: [- 90,  90] in S8 / [-360, 360] in S10
    input   s range: [  0,  181] in U8 / [   0, 724] in U10
    output cb range: [-128, 127] in S8 / [-512, 511] in S10
    output cr range: [-128, 127] in S8 / [-512, 511] in S10
    """
    assert depth >= 8

    ## at leat 7 times iterations make sure the error of the output angle is less than 1 degree
    iter_num = utl.clamp(iter_num, 7, 15)

    ## the depth of x & y should be > iter_num, otherwise, the remain (depth - iter_num) iterations will be useless!
    increase_bits_for_s = utl.clamp(increase_bits_for_s, 0, 8)
    fix_bits = increase_bits_for_s + 10
    if increase_bits_for_s + 8 <= iter_num:
        print(
            f"Warning: increase_bits_for_s({increase_bits_for_s}) + depth(8) <= iter_num({iter_num}), some iterations will be useless!"
        )

    ## change H to the first/fourth quadrant
    H_flag = ((h >= -90) & (h <= 90)) * 2 - 1  # 1: q1/q4; -1: q2/q3
    H_cordicPiFlag = np.int32(h > 90) - np.int32(h < -90)  # 0: q1/q4; 1: q2; -1: q3
    h0 = H_cordicPiFlag * 180 + H_flag * h

    x = s << increase_bits_for_s
    y = 0
    z = h0 << 8

    ## cordic iteration
    for i in range(iter_num):
        d = (z > 0) * 2 - 1
        xp = x - d * (y >> i)
        yp = y + d * (x >> i)
        zp = z - d * CORDIC_ATAN_LUT_FIX8[i]
        x = xp
        y = yp
        z = zp

    # out_0 = int32(floor((k * floor((double(x) + 32*fix)/(64*fix)) + 512) / 1024))
    # out_1 = int32(floor((k * floor((double(y) + 32*fix)/(64*fix)) + 512) / 1024))
    cb = (CORDIC_COEF_K_FIX10 * x + (1 << fix_bits - 1)) >> fix_bits
    cr = (CORDIC_COEF_K_FIX10 * y + (1 << fix_bits - 1)) >> fix_bits

    ## get the sign of U by the H value
    cb = cb * H_flag

    return cb, cr


class AcmImpl:
    def __init__(self, len_y: int = 9, len_s: int = 13, len_h: int = 65, len_h2: int = 0):
        self.b_lut_ready = False
        self.gain_y = 256  # [0, (256), 1023], 8bit fixed
        self.gain_s = 256  # [0, (256), 1023], 8bit fixed
        self.gain_h = 256  # [0, (256), 1023], 8bit fixed
        self.set_len(len_y, len_s, len_h, len_h2)

    def set_len(self, len_y: int, len_s: int, len_h: int, len_h2: int = 0):
        self.len_y = utl.clamp(len_y, 2, 255 + 1)
        self.len_s = utl.clamp(len_s, 2, 181 + 1)
        self.len_h = utl.clamp(len_h, 2, 360 + 1)
        self.len_h2 = self.len_h if len_h2 <= 0 else utl.clamp(len_h2, 2, self.len_h)
        self.step_y = 255.0 / (self.len_y - 1)  # step in range [0, 255]
        self.step_s = 181.0 / (self.len_s - 1)  # step in range [0, 181]
        self.step_h = 360.0 / (self.len_h - 1)  # step in range [0, 360]
        self.step_h2 = 360.0 / (self.len_h2 - 1)  # step in range [0, 360]
        print(f"[ACM] set lut len: y={self.len_y}, s={self.len_s}, h={self.len_h}, h2={self.len_h2}")
        print(
            f"[ACM] update lut step: y={self.step_y:.4f}, s={self.step_s:.4f}, h={self.step_h:.4f}, h2={self.step_h2:.4f}"
        )
        self.update_lut()

    def set_step(self, step_y: float, step_s: float, step_h: float, step_h2: float = 0.0):
        self.step_y = utl.clamp(step_y, 1.0, 255.0)
        self.step_s = utl.clamp(step_s, 1.0, 181.0)
        self.step_h = utl.clamp(step_h, 1.0, 360.0)
        self.step_h2 = self.step_h if step_h2 <= 0.0 else min(360.0, max(step_h2, step_h))
        self.len_y = round(255.0 / step_y) + 1
        self.len_s = round(181.0 / step_s) + 1
        self.len_h = round(360.0 / step_h) + 1
        self.len_h2 = round(360.0 / step_h2) + 1
        print(
            f"[ACM] set lut step: y={self.step_y:.4f}, s={self.step_s:.4f}, h={self.step_h:.4f}, h2={self.step_h2:.4f}"
        )
        print(f"[ACM] update lut len: y={self.len_y}, s={self.len_s}, h={self.len_h}, h2={self.len_h2}")
        self.update_lut()

    def set_gain(self, gain_y: int, gain_s: int, gain_h: int):
        self.gain_y = gain_y
        self.gain_s = gain_s
        self.gain_h = gain_h
        print(f"[ACM] set lut gain: y={self.gain_y}, s={self.gain_s}, h={self.gain_h}")

    def update_lut(self):
        dir = "V:/hwpq_verify_data/vop_robin_fpga_verify_acm/test_var_lut/"
        if self.b_lut_ready:
            if len(self.lut_delta_ybyh) != self.len_h:
                print(f"[ACM] update delta LUT size: {len(self.lut_delta_ybyh)} => {self.len_h}")
                self.lut_delta_ybyh = linear_resize_array_1d(self.lut_delta_ybyh, self.len_h)
                self.lut_delta_sbyh = linear_resize_array_1d(self.lut_delta_sbyh, self.len_h)
                self.lut_delta_hbyh = linear_resize_array_1d(self.lut_delta_hbyh, self.len_h)

            if self.lut_gain_ybyy.shape[0] != self.len_h2:
                print(
                    f"[ACM] update gain_y LUT size: {self.lut_gain_ybyy.shape[0]}x{self.lut_gain_ybyy.shape[1]} => {self.len_h2}x{self.len_y}"
                )
                print(
                    f"[ACM] update gain_s LUT size: {self.lut_gain_ybys.shape[0]}x{self.lut_gain_ybys.shape[1]} => {self.len_h2}x{self.len_s}"
                )

                self.lut_gain_ybyy = linear_resize_array_2d(self.lut_gain_ybyy, self.len_h2, self.len_y)
                self.lut_gain_sbyy = linear_resize_array_2d(self.lut_gain_sbyy, self.len_h2, self.len_y)
                self.lut_gain_hbyy = linear_resize_array_2d(self.lut_gain_hbyy, self.len_h2, self.len_y)
                self.lut_gain_ybys = linear_resize_array_2d(self.lut_gain_ybys, self.len_h2, self.len_s)
                self.lut_gain_sbys = linear_resize_array_2d(self.lut_gain_sbys, self.len_h2, self.len_s)
                self.lut_gain_hbys = linear_resize_array_2d(self.lut_gain_hbys, self.len_h2, self.len_s)
            else:
                if self.lut_gain_ybyy.shape[1] != self.len_y:
                    lut_gain_ybyy = np.zeros((self.len_h2, self.len_y), dtype=np.float32)
                    lut_gain_sbyy = np.zeros((self.len_h2, self.len_y), dtype=np.float32)
                    lut_gain_hbyy = np.zeros((self.len_h2, self.len_y), dtype=np.float32)
                    for h2 in range(self.len_h2):
                        lut_gain_ybyy[h2] = linear_resize_array_1d(self.lut_gain_ybyy[h2], self.len_y)
                        lut_gain_sbyy[h2] = linear_resize_array_1d(self.lut_gain_sbyy[h2], self.len_y)
                        lut_gain_hbyy[h2] = linear_resize_array_1d(self.lut_gain_hbyy[h2], self.len_y)
                    print(
                        f"[ACM] update gain_y LUT size: {lut_gain_ybyy.shape[0]}x{lut_gain_ybyy.shape[1]} => {self.len_h2}x{self.len_y}"
                    )
                    self.lut_gain_ybyy = lut_gain_ybyy
                    self.lut_gain_sbyy = lut_gain_sbyy
                    self.lut_gain_hbyy = lut_gain_hbyy

                if self.lut_gain_ybys.shape[1] != self.len_s:
                    lut_gain_ybys = np.zeros((self.len_h2, self.len_s), dtype=np.float32)
                    lut_gain_sbys = np.zeros((self.len_h2, self.len_s), dtype=np.float32)
                    lut_gain_hbys = np.zeros((self.len_h2, self.len_s), dtype=np.float32)
                    for h2 in range(self.len_h2):
                        lut_gain_ybys[h2] = linear_resize_array_1d(self.lut_gain_ybys[h2], self.len_s)
                        lut_gain_sbys[h2] = linear_resize_array_1d(self.lut_gain_sbys[h2], self.len_s)
                        lut_gain_hbys[h2] = linear_resize_array_1d(self.lut_gain_hbys[h2], self.len_s)
                    print(
                        f"[ACM] update gain_s LUT size: {lut_gain_ybyy.shape[0]}x{lut_gain_ybyy.shape[1]} => {self.len_h2}x{self.len_s}"
                    )
                    self.lut_gain_ybys = lut_gain_ybys
                    self.lut_gain_sbys = lut_gain_sbys
                    self.lut_gain_hbys = lut_gain_hbys
        else:
            self.lut_delta_ybyh = np.zeros(self.len_h, dtype=np.int16)
            self.lut_delta_sbyh = np.zeros(self.len_h, dtype=np.int16)
            self.lut_delta_hbyh = np.zeros(self.len_h, dtype=np.int16)
            self.lut_gain_ybyy = np.zeros((self.len_h2, self.len_y), dtype=np.int8)
            self.lut_gain_sbyy = np.zeros((self.len_h2, self.len_y), dtype=np.int8)
            self.lut_gain_hbyy = np.zeros((self.len_h2, self.len_y), dtype=np.int8)
            self.lut_gain_ybys = np.zeros((self.len_h2, self.len_s), dtype=np.int8)
            self.lut_gain_sbys = np.zeros((self.len_h2, self.len_s), dtype=np.int8)
            self.lut_gain_hbys = np.zeros((self.len_h2, self.len_s), dtype=np.int8)

        self.b_lut_ready = True

    def do_acm_u8(self, yuv444p_in: np.ndarray):
        """input: yuv444 planar in np.uint8, output: yuv444 planar in np.uint8"""
        print("[ACM] doing ACM LUT for u8 image...")

        H, W, _ = yuv444p_in.shape
        ## input is (H, W, 3) in planar order stored as channels-last
        y = yuv444p_in[:, :, 0].astype(np.int32)
        cb = yuv444p_in[:, :, 1].astype(np.int32) - 128
        cr = yuv444p_in[:, :, 2].astype(np.int32) - 128
        s = (np.sqrt(cb * cb + cr * cr) + 0.5).astype(np.int32)  # TODO: use cordic
        h_rad = np.arctan2(cr, cb)  # [-pi, pi]
        h_deg = (np.rad2deg(h_rad) + 180 + 0.5).astype(np.int32)  # [0, 360]

        local_lut_delta_ybyh = round_rshift(self.lut_delta_ybyh.astype(np.int32) * self.gain_y, 8)
        local_lut_delta_sbyh = round_rshift(self.lut_delta_sbyh.astype(np.int32) * self.gain_s, 8)
        local_lut_delta_hbyh = round_rshift(self.lut_delta_hbyh.astype(np.int32) * self.gain_h, 8)
        local_lut_delta_ybyh = np.clip(local_lut_delta_ybyh, -255, 255)
        local_lut_delta_sbyh = np.clip(local_lut_delta_sbyh, -255, 255)
        local_lut_delta_hbyh = np.clip(local_lut_delta_hbyh, -64, 64)

        ## get index
        idx_y = y.astype(np.float32) / self.step_y
        idx_s = s.astype(np.float32) / self.step_s
        idx_h = h_deg.astype(np.float32) / self.step_h
        idx_h2 = h_deg.astype(np.float32) / self.step_h2

        ## lut,
        # NOTE: cv2.remap 不支持 int32 类型做双线性插值，不支持 INTER_LINEAR_EXACT
        idx_zeros = np.zeros_like(idx_h)
        delta_y = cv2.remap(
            local_lut_delta_ybyh.astype(np.float32),
            idx_h,
            idx_zeros,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE,
        )  # [-255, 255]
        delta_s = cv2.remap(
            local_lut_delta_sbyh.astype(np.float32) / 255.0 * 181.0,  # range 255 -> 181
            idx_h,
            idx_zeros,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE,
        )  # [-255, 255]
        delta_h = cv2.remap(
            local_lut_delta_hbyh.astype(np.float32),
            idx_h,
            idx_zeros,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE,
        )  # [-64, 64]
        gain_yy = cv2.remap(
            self.lut_gain_ybyy.astype(np.float32),
            idx_y,
            idx_h2,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE,
        )  # [-127, 127]
        gain_ys = cv2.remap(
            self.lut_gain_sbyy.astype(np.float32),
            idx_y,
            idx_h2,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE,
        )  # [-127, 127]
        gain_yh = cv2.remap(
            self.lut_gain_hbyy.astype(np.float32),
            idx_y,
            idx_h2,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE,
        )  # [-127, 127]
        gain_sy = cv2.remap(
            self.lut_gain_ybys.astype(np.float32),
            idx_s,
            idx_h2,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE,
        )  # [-127, 127]
        gain_ss = cv2.remap(
            self.lut_gain_sbys.astype(np.float32),
            idx_s,
            idx_h2,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE,
        )  # [-127, 127]
        gain_sh = cv2.remap(
            self.lut_gain_hbys.astype(np.float32),
            idx_s,
            idx_h2,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE,
        )  # [-127, 127]

        delta_y = (delta_y + np.sign(delta_y) * 0.5).astype(np.int32)
        delta_s = (delta_s + np.sign(delta_s) * 0.5).astype(np.int32)
        delta_h = (delta_h + np.sign(delta_h) * 0.5).astype(np.int32)
        gain_yy = (gain_yy + np.sign(gain_yy) * 0.5).astype(np.int32)
        gain_ys = (gain_ys + np.sign(gain_ys) * 0.5).astype(np.int32)
        gain_yh = (gain_yh + np.sign(gain_yh) * 0.5).astype(np.int32)
        gain_sy = (gain_sy + np.sign(gain_sy) * 0.5).astype(np.int32)
        gain_ss = (gain_ss + np.sign(gain_ss) * 0.5).astype(np.int32)
        gain_sh = (gain_sh + np.sign(gain_sh) * 0.5).astype(np.int32)
        delta_y = delta_y * (gain_yy * gain_sy)
        delta_s = delta_s * (gain_ys * gain_ss)
        delta_h = delta_h * (gain_yh * gain_sh)
        delta_y = round_rshift(delta_y, 14 + 2)
        delta_s = round_rshift(delta_s, 14 + 2)
        delta_h = round_rshift(delta_h, 14 + 2)

        # YSH -> YUV (full-range)
        y += delta_y
        s += delta_s
        # y = np.clip(y + delta_y, 0, 255)
        # s = np.clip(s + delta_s, 0, 181)
        new_rad = h_rad + np.deg2rad(delta_h)
        new_cb = s * np.cos(new_rad)
        new_cr = s * np.sin(new_rad)
        cb = (new_cb + 0.5 * np.sign(new_cb)).astype(np.int32)
        cr = (new_cr + 0.5 * np.sign(new_cr)).astype(np.int32)

        # for i in range(H):
        #     for j in range(W):
        #         idx_y = float(y[i, j] / self.step_y)
        #         idx_s = float(s[i, j] / self.step_s)
        #         idx_h = float(h_deg[i, j] / self.step_h)
        #         idx_h2 = float(h_deg[i, j] / self.step_h2)

        #         delta_y = sample1d_linear(local_lut_delta_ybyh, idx_h)  # [-255, 255]
        #         delta_s = sample1d_linear(local_lut_delta_sbyh, idx_h)  # [-255, 255]
        #         delta_h = sample1d_linear(local_lut_delta_hbyh, idx_h)  # [-64, 64]
        #         gain_yy = sample2d_linear(self.lut_gain_ybyy, idx_y, idx_h2)  # [-127, 127]
        #         gain_ys = sample2d_linear(self.lut_gain_sbyy, idx_y, idx_h2)  # [-127, 127]
        #         gain_yh = sample2d_linear(self.lut_gain_hbyy, idx_y, idx_h2)  # [-127, 127]
        #         gain_sy = sample2d_linear(self.lut_gain_ybys, idx_s, idx_h2)  # [-127, 127]
        #         gain_ss = sample2d_linear(self.lut_gain_sbys, idx_s, idx_h2)  # [-127, 127]
        #         gain_sh = sample2d_linear(self.lut_gain_hbys, idx_s, idx_h2)  # [-127, 127]

        #         delta_y = delta_y * (gain_yy * gain_sy)
        #         delta_s = delta_s * (gain_ys * gain_ss)
        #         delta_h = delta_h * (gain_yh * gain_sh)
        #         delta_y = round_rshift(delta_y, 14)
        #         delta_s = round_rshift(delta_s, 14)
        #         delta_h = round_rshift(delta_h, 14)

        #         # YSH -> YUV (full-range)
        #         y[i, j] = utl.clamp(y[i, j] + delta_y, 0, 255)
        #         s[i, j] = utl.clamp(s[i, j] + delta_s, 0, 181)
        #         new_rad = h_rad[i, j] + np.deg2rad(delta_h)
        #         new_cb = s[i, j] * np.cos(new_rad)
        #         new_cr = s[i, j] * np.sin(new_rad)
        #         cb[i, j] = int(new_cb + 0.5 * np.sign(new_cb))
        #         cr[i, j] = int(new_cr + 0.5 * np.sign(new_cr))

        # create output as (H, W, 3) channels-last
        yuv444p_out = np.zeros((H, W, 3), dtype=np.uint8)
        yuv444p_out[:, :, 0] = np.clip(y, 0, 255).astype(np.uint8)
        yuv444p_out[:, :, 1] = np.clip(cb + 128, 0, 255).astype(np.uint8)
        yuv444p_out[:, :, 2] = np.clip(cr + 128, 0, 255).astype(np.uint8)
        print("[ACM] do ACM LUT for u8 image done.")
        return yuv444p_out

    def load_json(self, filename: str, b_resample: bool = False):
        ## check config file validity
        if not os.path.exists(filename):
            print(f"[ACM] config file '{filename}' doesn't exist!")
            return False
        if not filename.endswith(".json"):
            print(f"[ACM] config file '{filename}' is not a json file!")
            return False

        ## read json config
        try:
            with open(filename, "r") as f:
                data = json.load(f)
                if "pq_tuning_param" in data:
                    print("[ACM] loading config from pq_tuning_param.acm ...")
                    data = data["pq_tuning_param"]["acm"]
                len_y = data["lutLengthY"] if "lutLengthY" in data else 9
                len_s = data["lutLengthS"] if "lutLengthS" in data else 13
                len_h = data["lutLengthH"] if "lutLengthH" in data else 65
                len_h2 = data["lutLengthH2"] if "lutLengthH2" in data else 17
                lut_delta_ybyh = np.array(data["acmTableDeltaYbyH"], dtype=np.int16)
                lut_delta_sbyh = np.array(data["acmTableDeltaSbyH"], dtype=np.int16)
                lut_delta_hbyh = np.array(data["acmTableDeltaHbyH"], dtype=np.int16)
                lut_gain_ybyy = np.array(data["acmTableGainYbyY"], dtype=np.int8)
                lut_gain_sbyy = np.array(data["acmTableGainSbyY"], dtype=np.int8)
                lut_gain_hbyy = np.array(data["acmTableGainHbyY"], dtype=np.int8)
                lut_gain_ybys = np.array(data["acmTableGainYbyS"], dtype=np.int8)
                lut_gain_sbys = np.array(data["acmTableGainSbyS"], dtype=np.int8)
                lut_gain_hbys = np.array(data["acmTableGainHbyS"], dtype=np.int8)
                self.gain_y = data["lumGain"] if "lumGain" in data else 256
                self.gain_s = data["satGain"] if "satGain" in data else 256
                self.gain_h = data["hueGain"] if "hueGain" in data else 256
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)[-1]  # get last erro stack
            print(f"[ACM] load config '{filename}' failed in '{os.path.basename(tb.filename)}'-{tb.lineno}: {e}")

        ## check config data validity
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

        ## resample if needed
        if b_resample:
            if len_h != self.len_h:
                lut_delta_ybyh = linear_resize_array_1d(lut_delta_ybyh, self.len_h)
                lut_delta_sbyh = linear_resize_array_1d(lut_delta_sbyh, self.len_h)
                lut_delta_hbyh = linear_resize_array_1d(lut_delta_hbyh, self.len_h)
                print(f"[ACM] update delta LUT size: {len_h} => {self.len_h}")
            if len_h2 != self.len_h2 or lut_gain_ybyy.shape[1] != self.len_y:
                print(
                    f"[ACM] update gain_y LUT size: {lut_gain_ybyy.shape[0]}x{lut_gain_ybyy.shape[1]} => {self.len_h2}x{self.len_y}"
                )
                lut_gain_ybyy = linear_resize_array_2d(lut_gain_ybyy, self.len_h2, self.len_y)
                lut_gain_sbyy = linear_resize_array_2d(lut_gain_sbyy, self.len_h2, self.len_y)
                lut_gain_hbyy = linear_resize_array_2d(lut_gain_hbyy, self.len_h2, self.len_y)
            if len_h2 != self.len_h2 or lut_gain_ybys.shape[1] != self.len_s:
                print(
                    f"[ACM] update gain_s LUT size: {lut_gain_ybyy.shape[0]}x{lut_gain_ybyy.shape[1]} => {self.len_h2}x{self.len_s}"
                )
                lut_gain_ybys = linear_resize_array_2d(lut_gain_ybys, self.len_h2, self.len_s)
                lut_gain_sbys = linear_resize_array_2d(lut_gain_sbys, self.len_h2, self.len_s)
                lut_gain_hbys = linear_resize_array_2d(lut_gain_hbys, self.len_h2, self.len_s)
        else:
            self.len_y = len_y
            self.len_s = len_s
            self.len_h = len_h
            self.len_h2 = len_h2
            self.step_y = 255.0 / (self.len_y - 1)
            self.step_s = 181.0 / (self.len_s - 1)
            self.step_h = 360.0 / (self.len_h - 1)
            self.step_h2 = 360.0 / (self.len_h2 - 1)

        ## update LUTs
        self.lut_delta_ybyh = lut_delta_ybyh
        self.lut_delta_sbyh = lut_delta_sbyh
        self.lut_delta_hbyh = lut_delta_hbyh
        self.lut_gain_ybyy = lut_gain_ybyy
        self.lut_gain_sbyy = lut_gain_sbyy
        self.lut_gain_hbyy = lut_gain_hbyy
        self.lut_gain_ybys = lut_gain_ybys
        self.lut_gain_sbys = lut_gain_sbys
        self.lut_gain_hbys = lut_gain_hbys

        self.b_lut_ready = True
        print("[ACM] load config done.")
        return True

    def dump_json(self, filename: str = ""):
        ## write to json config
        data = {
            "version": "acm_impl_var_lut",
            "acmEnable": 1,
            ## keep list data in one line by using NoIndent & CompactArrayEncoder
            "acmTableDeltaYbyH": utl.NoIndent(self.lut_delta_ybyh.flatten().tolist()),
            "acmTableDeltaHbyH": utl.NoIndent(self.lut_delta_hbyh.flatten().tolist()),
            "acmTableDeltaSbyH": utl.NoIndent(self.lut_delta_sbyh.flatten().tolist()),
            "acmTableGainYbyY": utl.NoIndent(self.lut_gain_ybyy.flatten().tolist()),
            "acmTableGainHbyY": utl.NoIndent(self.lut_gain_hbyy.flatten().tolist()),
            "acmTableGainSbyY": utl.NoIndent(self.lut_gain_sbyy.flatten().tolist()),
            "acmTableGainYbyS": utl.NoIndent(self.lut_gain_ybys.flatten().tolist()),
            "acmTableGainHbyS": utl.NoIndent(self.lut_gain_sbys.flatten().tolist()),
            "acmTableGainSbyS": utl.NoIndent(self.lut_gain_hbys.flatten().tolist()),
            "lumGain": self.gain_y,
            "hueGain": self.gain_h,
            "satGain": self.gain_s,
            "lutLengthY": self.len_y,
            "lutLengthS": self.len_s,
            "lutLengthH": self.len_h,
            "lutLengthH2": self.len_h2,
            "lutStepY": self.step_y,
            "lutStepS": self.step_s,
            "lutStepH": self.step_h,
            "lutStepH2": self.step_h2,
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
        ## plot delta LUT & save to file
        x = np.arange(self.len_h)

        plt.figure(figsize=(8, 6))  # 可选：设置图像大小（英寸）
        plt.plot(x, self.lut_delta_ybyh, label="delta_ybyh", color="red", linewidth=1.5)
        plt.plot(x, self.lut_delta_sbyh, label="delta_sbyh", color="blue", linewidth=1.5)
        plt.plot(x, self.lut_delta_hbyh, label="delta_hbyh", color="green", linewidth=1.5)
        plt.legend()
        plt.title("ACM Delta LUT YSH by H")
        plt.xlabel("Hue")
        plt.ylabel("Delta Y/S/H")
        plt.grid(True, linestyle=":", alpha=0.7)
        plt.savefig(f"{dir}/lut_delta_yshbyh_x{self.len_h}.png", dpi=600, bbox_inches="tight")
        # plt.show()

        plt.imsave(f"{dir}/lut_gain_ybyy_{self.len_h2}x{self.len_y}.png", self.lut_gain_ybyy, cmap='gray')
        plt.imsave(f"{dir}/lut_gain_sbyy_{self.len_h2}x{self.len_y}.png", self.lut_gain_sbyy, cmap='gray')
        plt.imsave(f"{dir}/lut_gain_hbyy_{self.len_h2}x{self.len_y}.png", self.lut_gain_hbyy, cmap='gray')
        plt.imsave(f"{dir}/lut_gain_ybys_{self.len_h2}x{self.len_s}.png", self.lut_gain_ybys, cmap='gray')
        plt.imsave(f"{dir}/lut_gain_sbys_{self.len_h2}x{self.len_s}.png", self.lut_gain_sbys, cmap='gray')
        plt.imsave(f"{dir}/lut_gain_hbys_{self.len_h2}x{self.len_s}.png", self.lut_gain_hbys, cmap='gray')

        plt.close()
        print(f"[ACM] dump LUT images to {dir}.")

    def gen_test_config(self):
        if not self.b_lut_ready:
            return False

        np.random.seed(114514)
        tmp_lut_gain_ybyy = np.random.normal(0.0, 64.0, size=(self.len_h2, self.len_y)) * 16
        tmp_lut_gain_sbyy = np.random.normal(0.0, 64.0, size=(self.len_h2, self.len_y)) * 16
        tmp_lut_gain_hbyy = np.random.normal(0.0, 64.0, size=(self.len_h2, self.len_y)) * 16
        tmp_lut_gain_ybys = np.random.normal(0.0, 64.0, size=(self.len_h2, self.len_s)) * 16
        tmp_lut_gain_sbys = np.random.normal(0.0, 64.0, size=(self.len_h2, self.len_s)) * 16
        tmp_lut_gain_hbys = np.random.normal(0.0, 64.0, size=(self.len_h2, self.len_s)) * 16
        tmp_lut_gain_ybyy = cv2.GaussianBlur(tmp_lut_gain_ybyy, ksize=(0, 0), sigmaX=3.0, sigmaY=3.0)
        tmp_lut_gain_sbyy = cv2.GaussianBlur(tmp_lut_gain_sbyy, ksize=(0, 0), sigmaX=3.0, sigmaY=3.0)
        tmp_lut_gain_hbyy = cv2.GaussianBlur(tmp_lut_gain_hbyy, ksize=(0, 0), sigmaX=3.0, sigmaY=3.0)
        tmp_lut_gain_ybys = cv2.GaussianBlur(tmp_lut_gain_ybys, ksize=(0, 0), sigmaX=3.0, sigmaY=3.0)
        tmp_lut_gain_sbys = cv2.GaussianBlur(tmp_lut_gain_sbys, ksize=(0, 0), sigmaX=3.0, sigmaY=3.0)
        tmp_lut_gain_hbys = cv2.GaussianBlur(tmp_lut_gain_hbys, ksize=(0, 0), sigmaX=3.0, sigmaY=3.0)
        self.lut_gain_ybyy = np.clip(tmp_lut_gain_ybyy, -128, 127).astype(np.int8)
        self.lut_gain_sbyy = np.clip(tmp_lut_gain_sbyy, -128, 127).astype(np.int8)
        self.lut_gain_hbyy = np.clip(tmp_lut_gain_hbyy, -128, 127).astype(np.int8)
        self.lut_gain_ybys = np.clip(tmp_lut_gain_ybys, -128, 127).astype(np.int8)
        self.lut_gain_sbys = np.clip(tmp_lut_gain_sbys, -128, 127).astype(np.int8)
        self.lut_gain_hbys = np.clip(tmp_lut_gain_hbys, -128, 127).astype(np.int8)

        for h in range(self.len_h):
            self.lut_delta_ybyh[h] = np.round(np.cos(h / self.len_h * 2 * np.pi) * 64)  # [-64, 64]
            self.lut_delta_sbyh[h] = np.round(np.sin(h / self.len_h * 2 * np.pi) * 64)  # [-64, 64]
            self.lut_delta_hbyh[h] = np.round(
                np.arctan((h - self.len_h / 2) * 2 / self.len_h) / np.pi * 90
            )  # [-22, 22] deg
            # self.lut_delta_ybyh[h] = np.round(np.cos(h / self.len_h * 2 * np.pi) * 128)  # [-255, 255]
            # self.lut_delta_sbyh[h] = np.round(np.sin(h / self.len_h * 2 * np.pi) * 180)  # [-180, 180]


if __name__ == '__main__':
    ## arg parser
    parser = argparse.ArgumentParser(exit_on_error=False)
    parser.add_argument("-i", "--input", default="", type=str, help="输入图像文件, yuv444p格式")
    parser.add_argument("-o", "--output", default="", type=str, help="输出图像文件")
    parser.add_argument("-c", "--config", default="", type=str, help=".json配置文件")
    parser.add_argument("-w", "--width", default=1920, type=int, help="图像宽度，默认: 1920")
    parser.add_argument("-g", "--height", default=1080, type=int, help="图像高度，默认: 1080")
    parser.add_argument("-s", "--step", type=float, nargs='+', help="LUT step 数组, 4个元素")
    parser.add_argument("-l", "--len", type=int, nargs='+', help="LUT len 数组, 4个元素")
    parser.add_argument("-G", "--gain", type=int, nargs='+', help="LUT gain 数组, 4个元素")
    parser.add_argument("-n", "--iter_num", default=13, type=int, help="Cordic迭代次数, 默认: 13")
    parser.add_argument("-b", "--increase_bits", default=3, type=int, help="Cordic S定点提示精度, 默认: 3")
    parser.add_argument("-uv", "--uv", type=int, nargs='+', help="传入U/V数值测试Cordic结果")
    parser.add_argument("-hs", "--hs", type=int, nargs='+', help="传入H/S数值测试Cordic结果")
    args, _ = parser.parse_known_args()

    # DEF_OUT_DIR = "V:/hwpq_verify_data/vop_robin_fpga_verify_acm/test_var_lut"
    # H = args.height
    # W = args.width
    # infile = (
    #     "V:/hwpq_verify_data/vop_robin_fpga_verify_acm/input_1920x1080_yuv444p_601F.yuv"
    #     if args.input == ""
    #     else args.input
    # )
    # outfile = f"{DEF_OUT_DIR}/out_acm_1920x1080_yuv444p_601F.yuv" if args.output == "" else args.output
    # cfgfile = "G:/Codes/fpga/fpga_verify/data/vdpp_vop_config_3572.json" if args.config == "" else args.config

    # ## test
    # data = np.fromfile(infile, np.uint8)
    # img = np.zeros((H, W, 3), dtype=np.uint8)
    # img[:, :, 0] = data[0 : H * W * 1].reshape(H, W)
    # img[:, :, 1] = data[H * W * 1 : H * W * 2].reshape(H, W)
    # img[:, :, 2] = data[H * W * 2 : H * W * 3].reshape(H, W)

    # acm = AcmImpl()

    # if args.config != "":
    #     ret = acm.load_json(cfgfile, False)
    #     if not ret:
    #         print("[ACM] load config failed.")
    #         exit(ret)
    # else:
    #     acm.gen_test_config()
    #     # acm.set_len(9, 13, 65, 17)
    #     acm.set_gain(320, 320, 320)

    # if args.step:
    #     acm.set_step(args.step[0], args.step[1], args.step[2], args.step[3])
    # elif args.len:
    #     acm.set_len(args.len[0], args.len[1], args.len[2], args.len[3])
    # if args.gain:
    #     acm.set_gain(args.gain[0], args.gain[1], args.gain[2])

    # out = acm.do_acm_u8(img)

    # ## write planar Y then Cb then Cr (same layout as input file)
    # out.transpose(2, 0, 1).tofile(outfile)  # HWC to CHW
    # print(f"[ACM] done. write output file to {outfile}")

    # acm.dump_json(f"{DEF_OUT_DIR}/acm_var_config_len_y{acm.len_y}_s{acm.len_s}_h{acm.len_h}_{acm.len_h2}.json")
    # acm.dump_lut(DEF_OUT_DIR)

    def test_cordic_cbcr2hs_u8(iter_num, increase_bits, uv):
        if (uv is not None) and len(uv) >= 2:
            u, v = uv[0], uv[1]
        else:
            u, v = np.indices((256, 256))
        dh = np.zeros_like(u)
        ds = np.zeros_like(u)

        cb, cr = u - 128, v - 128
        res = cordic_cbcr2hs(cb, cr, 8, iter_num, increase_bits)
        h = res[0]
        s = res[1]  # if increase_bits == 0 else res[1] + (1 << (increase_bits - 1)) >> increase_bits

        hp = np.degrees(np.arctan2(cr, cb))  # [-180, +180]
        sp = np.sqrt(cb**2 + cr**2)  # [0, 181]
        hp = (hp + 0.5 * np.sign(hp)).astype(np.int32)
        sp = (sp + 0.5).astype(np.int32)

        dh = hp - h
        ds = sp - s

        if type(u) != np.ndarray:
            print(f"input  u={u}, v={v} => cb={cb}, cr={cr}")
            print(f"output h={h}, s={s} / hp={hp}, sp={sp}")
        else:
            # (h/180*127).astype(np.int8).tofile(f"out_h_256x256_iter{iter_num}_incbits{increase_bits}_yuv400.yuv")
            # s.astype(np.uint8).tofile(f"out_s_256x256_iter{iter_num}_incbits{increase_bits}_yuv400.yuv")
            # (hp/180*127).astype(np.int8).tofile(f"out_hp_256x256_iter{iter_num}_incbits{increase_bits}_yuv400.yuv")
            # sp.astype(np.uint8).tofile(f"out_sp_256x256_iter{iter_num}_incbits{increase_bits}_yuv400.yuv")
            # dh.astype(np.int8).tofile(f"diff_h_256x256_iter{iter_num}_incbits{increase_bits}_yuv400.yuv")
            # ds.astype(np.int8).tofile(f"diff_s_256x256_iter{iter_num}_incbits{increase_bits}_yuv400.yuv")
            print(f"Max absolute error: dh={np.max(np.abs(dh))}, ds={np.max(np.abs(ds))}")
        print(
            f"sum error for 8bit uv->hs: eh={abs(dh).sum()}, es={abs(ds).sum()} (iter={iter_num}, inc_bits={increase_bits})"
        )

    test_cordic_cbcr2hs_u8(args.iter_num, args.increase_bits, args.uv if args.uv else None)

    def test_cordic_hs2cbcr_u8(iter_num, increase_bits, hs):
        if (hs is not None) and len(hs) >= 2:
            h, s = hs[0], hs[1]
        else:
            h = np.full((361, 182), np.arange(-180, 181).reshape(-1, 1))
            _, s = np.indices((361, 182))
        du = np.zeros_like(h)
        dv = np.zeros_like(h)

        res = cordic_hs2cbcr(h, s, 8, iter_num, increase_bits)
        u = np.clip(res[0] + 128, 0, 255)
        v = np.clip(res[1] + 128, 0, 255)

        up = np.clip(s * np.cos(np.radians(h)) + 128, 0, 255)
        vp = np.clip(s * np.sin(np.radians(h)) + 128, 0, 255)
        up = (up + 0.5).astype(np.int32)
        vp = (vp + 0.5).astype(np.int32)

        du = up - u
        dv = vp - v

        if type(h) != np.ndarray:
            print(f"input  h={h}, s={s}")
            print(f"output u={u}, v={v} / up={up}, vp={vp}")
        else:
            # u.astype(np.uint8).tofile(f"out_u_182x361_iter{iter_num}_incbits{increase_bits}_yuv400.yuv")
            # v.astype(np.uint8).tofile(f"out_v_182x361_iter{iter_num}_incbits{increase_bits}_yuv400.yuv")
            # up.astype(np.uint8).tofile(f"out_up_182x361_iter{iter_num}_incbits{increase_bits}_yuv400.yuv")
            # vp.astype(np.uint8).tofile(f"out_vp_182x361_iter{iter_num}_incbits{increase_bits}_yuv400.yuv")
            # du.astype(np.int8).tofile(f"diff_u_182x361_iter{iter_num}_incbits{increase_bits}_yuv400.yuv")
            # dv.astype(np.int8).tofile(f"diff_v_182x361_iter{iter_num}_incbits{increase_bits}_yuv400.yuv")
            print(f"Max absolute error: du={np.max(np.abs(du))}, dv={np.max(np.abs(dv))}")
        print(
            f"sum error for 8bit hs->uv: eu={abs(du).sum()}, ev={abs(dv).sum()} (iter={iter_num}, inc_bits={increase_bits})"
        )

    test_cordic_hs2cbcr_u8(args.iter_num, args.increase_bits, args.hs if args.hs else None)
