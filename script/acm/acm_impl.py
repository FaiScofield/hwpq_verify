"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : acm_impl.py
Author      : vance.wu@rock-chips.com
Date        : 2025-10-24
Description :
LastEditTime: 2025-12-11
"""

import os
import sys
import json
import cv2
import argparse
import traceback
import numpy as np
import matplotlib.pyplot as plt

import cordic

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

    def do_acm_u8(self, yuv444p_in: np.ndarray, use_cordic: bool = False):
        """input: yuv444 planar in np.uint8, output: yuv444 planar in np.uint8"""
        print("[ACM] doing ACM LUT for u8 image...")

        H, W, _ = yuv444p_in.shape
        ## input is (H, W, 3) in planar order stored as channels-last
        y = yuv444p_in[:, :, 0].astype(np.int32)
        cb = yuv444p_in[:, :, 1].astype(np.int32) - 128
        cr = yuv444p_in[:, :, 2].astype(np.int32) - 128
        if use_cordic:
            h, s, _, _ = cordic.cordic_cbcr2hs(cb, cr, 8, 13, 8, False)
            h_deg = h + 180
        else:
            s = (np.sqrt(cb * cb + cr * cr) + 0.5).astype(np.int32)
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
        if use_cordic:
            h_deg = h + delta_h
            h_deg = np.where(h_deg < 0, h_deg + 360, h_deg)
            h_deg = np.where(h_deg > 360, h_deg - 360, h_deg)
            cb, cr = cordic.cordic_hs2cbcr(h_deg, s, 8, 8, 8, 13, 8)
        else:
            new_rad = h_rad + np.deg2rad(delta_h)
            new_cb = s * np.cos(new_rad)
            new_cr = s * np.sin(new_rad)
            cb = (new_cb + 0.5 * np.sign(new_cb)).astype(np.int32)
            cr = (new_cr + 0.5 * np.sign(new_cr)).astype(np.int32)

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
                len_h2 = data["lutLengthHD"] if "lutLengthHD" in data else 17
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

                ## check if need to transpose the LUT size
                if "lutGainSizeByY_HxW" in data:
                    HxW = data["lutGainSizeByY_HxW"].split("x")
                    HxW = [int(x) for x in HxW]
                    if HxW[0] == len_y or HxW[1] == len_h2:
                        print(f"[ACM] read gain_y LUT size ({HxW[0]}x{HxW[1]}), need to transpose to {len_h2}x{len_y}!")
                        lut_gain_ybyy = lut_gain_ybyy.reshape(len_y, len_h2).T
                        lut_gain_sbyy = lut_gain_sbyy.reshape(len_y, len_h2).T
                        lut_gain_hbyy = lut_gain_hbyy.reshape(len_y, len_h2).T
                    elif HxW[0] != len_h2 or HxW[1] != len_y:
                        print(
                            f"[ACM] gain_y LUT size ({HxW[0]}x{HxW[1]}) not fit to len_h2 x len_y ({len_h2}x{len_y})!"
                        )
                if "lutGainSizeByS_HxW" in data:
                    HxW = data["lutGainSizeByS_HxW"].split("x")
                    HxW = [int(x) for x in HxW]
                    if HxW[0] == len_s or HxW[1] == len_h2:
                        print(f"[ACM] read gain_s LUT size ({HxW[0]}x{HxW[1]}), need to transpose to {len_h2}x{len_s}!")
                        lut_gain_ybys = lut_gain_ybys.reshape(len_s, len_h2).T
                        lut_gain_sbys = lut_gain_sbys.reshape(len_s, len_h2).T
                        lut_gain_hbys = lut_gain_hbys.reshape(len_s, len_h2).T
                    elif HxW[0] != len_h2 or HxW[1] != len_s:
                        print(
                            f"[ACM] gain_s LUT size ({HxW[0]}x{HxW[1]}) not fit to len_h2 x len_y ({len_h2}x{len_s})!"
                        )
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
            "lutLengthHD": self.len_h2,
            "lutStepY": self.step_y,
            "lutStepS": self.step_s,
            "lutStepH": self.step_h,
            "lutStepHD": self.step_h2,
            "lut2dAxis4HD": 0 if self.lut_gain_ybyy.shape[0] == self.len_h2 else 1,
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

    def gen_test_config(self, b_strict: bool = True, random_seed: int = 114514):
        if not self.b_lut_ready:
            return False

        np.random.seed(random_seed)
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

        max_h = self.len_h - 1
        x = np.arange(self.len_h)

        ## generate S/H LUTs strictly for the bug of VOP_ACM, which means:
        ## 1. LUT[0] = LUT[64], make sure the first and last value are the same (h=-180/+180)
        ## 2. LUT[0] = 0, make sure the first delta values are zero (h=-180)
        if b_strict:
            self.lut_delta_ybyh = np.round(np.sin(x / max_h * 2 * np.pi) * 255)  # [-255, 255]
            self.lut_delta_hbyh = np.round(np.sin(x / max_h * 2 * np.pi) * 64)  # [-64, 64]
            self.lut_delta_sbyh = np.round(np.sin(x / max_h * 2 * np.pi) * -255)  # [-255, 255]
            assert self.lut_delta_hbyh[0] == self.lut_delta_hbyh[-1]
            assert self.lut_delta_sbyh[0] == self.lut_delta_sbyh[-1]
            assert self.lut_delta_hbyh[0] == 0 and self.lut_delta_sbyh[0] == 0
        else:
            self.lut_delta_ybyh = np.round(np.arctan((x - self.len_h // 2) * np.pi / max_h) * 255)  # [-255, 255]
            self.lut_delta_hbyh = np.round(np.arctan((x - self.len_h // 2) * np.pi / max_h) * 64)  # [-64, 64]
            self.lut_delta_sbyh = np.round(np.arctan((x - self.len_h // 2) * np.pi / max_h) * -255)  # [-255, 255]
            if self.lut_delta_hbyh[0] != self.lut_delta_hbyh[-1]:
                print(f"WARNING! The first/last element not equal! {self.lut_delta_hbyh[0]}/{self.lut_delta_hbyh[-1]}")
            if self.lut_delta_sbyh[0] != self.lut_delta_sbyh[-1]:
                print(f"WARNING! The first/last element not equal! {self.lut_delta_sbyh[0]}/{self.lut_delta_sbyh[-1]}")
            print(f"y0={self.lut_delta_ybyh[0]}, y32={self.lut_delta_ybyh[32]}, y64={self.lut_delta_ybyh[-1]}")
            print(f"s0={self.lut_delta_sbyh[0]}, s32={self.lut_delta_sbyh[32]}, s64={self.lut_delta_sbyh[-1]}")
            print(f"h0={self.lut_delta_hbyh[0]}, h32={self.lut_delta_hbyh[32]}, h64={self.lut_delta_hbyh[-1]}")

        self.lut_delta_ybyh = self.lut_delta_ybyh.astype(np.int32)
        self.lut_delta_hbyh = self.lut_delta_hbyh.astype(np.int32)
        self.lut_delta_sbyh = self.lut_delta_sbyh.astype(np.int32)
        print(f"[ACM] generated a test config, b_strict={b_strict}, random_seed={random_seed}.")


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

    DEF_OUT_DIR = "V:/hwpq_verify_data/vop_robin_fpga_verify_acm/test_var_lut"
    H = args.height
    W = args.width
    infile = (
        "V:/hwpq_verify_data/vop_robin_fpga_verify_acm/input_1920x1080_yuv444p_601F.yuv"
        if args.input == ""
        else args.input
    )
    outfile = f"{DEF_OUT_DIR}/out_acm_1920x1080_yuv444p_601F.yuv" if args.output == "" else args.output
    cfgfile = "G:/Codes/fpga/fpga_verify/data/vdpp_vop_config_3572.json" if args.config == "" else args.config

    ## test
    data = np.fromfile(infile, np.uint8)
    img = np.zeros((H, W, 3), dtype=np.uint8)
    img[:, :, 0] = data[0 : H * W * 1].reshape(H, W)
    img[:, :, 1] = data[H * W * 1 : H * W * 2].reshape(H, W)
    img[:, :, 2] = data[H * W * 2 : H * W * 3].reshape(H, W)

    acm = AcmImpl()

    if args.config != "":
        ret = acm.load_json(cfgfile, False)
        if not ret:
            print("[ACM] load config failed.")
            exit(ret)
    else:
        acm.set_len(9, 13, 65, 17)
        acm.gen_test_config(False)
        # acm.set_gain(320, 320, 320)

    if args.step:
        acm.set_step(args.step[0], args.step[1], args.step[2], args.step[3])
    elif args.len:
        acm.set_len(args.len[0], args.len[1], args.len[2], args.len[3])
    if args.gain:
        acm.set_gain(args.gain[0], args.gain[1], args.gain[2])

    out = acm.do_acm_u8(img)

    ## write planar Y then Cb then Cr (same layout as input file)
    out.transpose(2, 0, 1).tofile(outfile)  # HWC to CHW
    print(f"[ACM] done. write output file to {outfile}")

    acm.dump_json(f"{DEF_OUT_DIR}/acm_var_config_len_y{acm.len_y}_s{acm.len_s}_h{acm.len_h}_{acm.len_h2}.json")
    acm.dump_lut(DEF_OUT_DIR)
