"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : acm_impl.py
Author      : vance.wu@rock-chips.com
Date        : 2025-10-24
Description :
LastEditTime: 2025-10-24
"""

import os
import json
import cv2
import traceback
import numpy as np
# from utils import *

PI = 3.1415926

def clamp(value, min_value, max_value):
    return min(max(value, min_value), max_value)

def sample1d_linear(arr: np.ndarray, idx: float):
    # arr: (N, C) or (N,) ; idx: float
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
    x = clamp(x, 0.0, W - 1.0)
    y = clamp(y, 0.0, H - 1.0)
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
    return new_arr


def linear_resize_array_2d(mat: np.ndarray, new_rows: int, new_cols: int):
    if not mat or len(mat) == 0 or len(mat[0]) == 0:
        raise ValueError("Invalid 2D array input!")

    old_rows, old_cols = mat.shape
    if old_rows == new_rows and old_cols == new_cols:
        return mat.copy()

    new_mat = cv2.resize(mat, (new_cols, new_rows), interpolation=cv2.INTER_LINEAR_EXACT)
    return new_mat


class AcmImpl:
    def __init__(self, len_y: int = 9, len_s: int = 13, len_h: int = 65, len_h2: int = 0):
        self.b_lut_ready = False
        self.gain_y = 256
        self.gain_s = 256
        self.gain_h = 256
        self.set_len(len_y, len_s, len_h, len_h2)

    def set_len(self, len_y: int, len_s: int, len_h: int, len_h2: int = 0):
        self.len_y = clamp(len_y, 2, 256)
        self.len_s = clamp(len_s, 2, 181)
        self.len_h = clamp(len_h, 2, 361)
        self.len_h2 = self.len_h if len_h2 <= 0 else clamp(len_h2, 2, self.len_h)
        self.step_y = 255.0 / (self.len_y - 1)
        self.step_s = 180.0 / (self.len_s - 1)
        self.step_h = 360.0 / (self.len_h - 1)
        self.step_h2 = 360.0 / (self.len_h2 - 1)
        self.update_lut()

    def set_step(self, step_y: float, step_s: float, step_h: float, step_h2: float = 0.0):
        len_y = round(255.0 / max(step_y, 1))
        len_s = round(180.0 / max(step_s, 1))
        len_h = round(360.0 / max(step_h, 1))
        len_h2 = len_h if step_h2 <= 0.0 else round(360.0 / max(1, max(step_h2, step_h)))
        self.set_len(len_y, len_s, len_h, len_h2)

    def set_gain(self, gain_y: int, gain_s: int, gain_h: int):
        self.gain_y = gain_y
        self.gain_s = gain_s
        self.gain_h = gain_h

    def update_lut(self):
        if self.b_lut_ready:
            if len(self.lut_delta_ybyh) != self.len_h:
                lut_delta_ybyh = linear_resize_array_1d(self.lut_delta_ybyh, self.len_h)
                lut_delta_sbyh = linear_resize_array_1d(self.lut_delta_sbyh, self.len_h)
                lut_delta_hbyh = linear_resize_array_1d(self.lut_delta_hbyh, self.len_h)
                print(f"[ACM] update delta LUT size: {len(self.lut_delta_ybyh)} => {self.len_h}")

            if lut_gain_ybyy.shape[0] != self.len_h2:
                lut_gain_ybyy = linear_resize_array_2d(self.lut_gain_ybyy, self.len_h2, self.len_y)
                lut_gain_sbyy = linear_resize_array_2d(self.lut_gain_sbyy, self.len_h2, self.len_y)
                lut_gain_hbyy = linear_resize_array_2d(self.lut_gain_hbyy, self.len_h2, self.len_y)
                lut_gain_ybys = linear_resize_array_2d(self.lut_gain_ybys, self.len_h2, self.len_s)
                lut_gain_sbys = linear_resize_array_2d(self.lut_gain_sbys, self.len_h2, self.len_s)
                lut_gain_hbys = linear_resize_array_2d(self.lut_gain_hbys, self.len_h2, self.len_s)
                print(
                    f"[ACM] update gain_y LUT size: {lut_gain_ybyy.shape[0]}x{lut_gain_ybyy.shape[1]} => {self.len_h2}x{self.len_y}"
                )
                print(
                    f"[ACM] update gain_s LUT size: {lut_gain_ybyy.shape[0]}x{lut_gain_ybyy.shape[1]} => {self.len_h2}x{self.len_s}"
                )
            else:
                if lut_gain_ybyy.shape[1] != self.len_y:
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
                if lut_gain_ybys.shape[1] != self.len_s:
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
        else:
            lut_delta_ybyh = np.zeros(self.len_h, dtype=np.int16)
            lut_delta_sbyh = np.zeros(self.len_h, dtype=np.int16)
            lut_delta_hbyh = np.zeros(self.len_h, dtype=np.int16)
            lut_gain_ybyy = np.zeros((self.len_h2, self.len_y), dtype=np.int8)
            lut_gain_sbyy = np.zeros((self.len_h2, self.len_y), dtype=np.int8)
            lut_gain_hbyy = np.zeros((self.len_h2, self.len_y), dtype=np.int8)
            lut_gain_ybys = np.zeros((self.len_h2, self.len_s), dtype=np.int8)
            lut_gain_sbys = np.zeros((self.len_h2, self.len_s), dtype=np.int8)
            lut_gain_hbys = np.zeros((self.len_h2, self.len_s), dtype=np.int8)

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

    def do_acm_u8(self, yuv444p_in: np.ndarray):
        """input: yuv444 planar in np.uint8, output: yuv444 planar in np.uint8"""
        print("[ACM] doing ACM LUT for u8 image...")
        H, W, _ = yuv444p_in.shape
        # input is (H, W, 3) in planar order stored as channels-last
        y = yuv444p_in[:, :, 0].astype(np.int32)
        cb = yuv444p_in[:, :, 1].astype(np.int32) - 128
        cr = yuv444p_in[:, :, 2].astype(np.int32) - 128
        s = (np.sqrt(cb * cb + cr * cr) + 0.5).astype(np.int32)  # TODO: use cordic
        h_rad = np.arctan2(cr, cb)  # [-pi, pi]
        h_deg = (np.rad2deg(h_rad) + 180 + 0.5).astype(np.int32)  # [0, 2*pi]

        for i in range(H):
            for j in range(W):
                idx_y = float(y[i, j] / self.step_y)
                idx_s = float(s[i, j] / self.step_s)
                idx_h = float(h_deg[i, j] / self.step_h)
                idx_h2 = float(h_deg[i, j] / self.step_h2)

                delta_y = int(sample1d_linear(self.lut_delta_ybyh, idx_h))
                delta_s = int(sample1d_linear(self.lut_delta_sbyh, idx_h))
                delta_h = int(sample1d_linear(self.lut_delta_hbyh, idx_h))
                gain_yy = int(sample2d_linear(self.lut_gain_ybyy, idx_y, idx_h2))
                gain_ys = int(sample2d_linear(self.lut_gain_sbyy, idx_y, idx_h2))
                gain_yh = int(sample2d_linear(self.lut_gain_hbyy, idx_y, idx_h2))
                gain_sy = int(sample2d_linear(self.lut_gain_ybys, idx_s, idx_h2))
                gain_ss = int(sample2d_linear(self.lut_gain_sbys, idx_s, idx_h2))
                gain_sh = int(sample2d_linear(self.lut_gain_hbys, idx_s, idx_h2))

                delta_y = delta_y * (gain_yy * gain_sy) * self.gain_y
                delta_s = delta_s * (gain_ys * gain_ss) * self.gain_s
                delta_h = delta_h * (gain_yh * gain_sh) * self.gain_h
                delta_y = int(delta_y + np.sign(delta_y) * (1 << 21)) >> 22
                delta_s = int(delta_s + np.sign(delta_s) * (1 << 21)) >> 22
                delta_h = int(delta_h + np.sign(delta_h) * (1 << 21)) >> 22

                # YSH -> YUV (full-range)
                y[i, j] += delta_y
                s[i, j] += delta_s
                new_rad = h_rad[i, j] + np.deg2rad(delta_h)
                new_cb = s[i, j] * np.cos(new_rad)
                new_cr = s[i, j] * np.sin(new_rad)
                cb[i, j] = int(new_cb + 0.5 * np.sign(new_cb))
                cr[i, j] = int(new_cr + 0.5 * np.sign(new_cr))

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
            self.step_s = 180.0 / (self.len_s - 1)
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
        print("[ACM] load config done.")
        return True


if __name__ == '__main__':
    # test
    H = 1080
    W = 1920
    infile = "V:/hwpq_verify_data/vop_robin_fpga_verify_acm/input_1920x1080_yuv444p_601F.yuv"
    data = np.fromfile(infile, np.uint8)
    img = np.zeros((H, W, 3), dtype=np.uint8)
    img[:, :, 0] = data[0:H*W*1].reshape(H, W)
    img[:, :, 1] = data[H*W*1:H*W*2].reshape(H, W)
    img[:, :, 2] = data[H*W*2:H*W*3].reshape(H, W)

    acm = AcmImpl()
    acm.load_json("G:/Codes/fpga/fpga_verify/data/vdpp_vop_config_3572.json", False)

    out = acm.do_acm_u8(img)

    # write planar Y then Cb then Cr (same layout as input file)
    # HWC to CHW
    outfile = "V:/hwpq_verify_data/vop_robin_fpga_verify_acm/out_acm_1920x1080_yuv444p_601F.yuv"
    out.transpose(2,0,1).tofile(outfile)
    print(f"[ACM] done. write output file to {outfile}")
