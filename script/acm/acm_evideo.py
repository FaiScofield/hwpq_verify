"""
Copyright   : Copyright (c) 2026 by Rockchip. All right reserved.
FilePath    : acm_evideo.py
Author      : vance.wu@rock-chips.com
Date        : 2026-01-27
Description :
LastEditTime: 2026-01-27
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

g_r2y_mat_bt709 = np.array(
    [[0.2126, 0.7152, 0.0722], [-0.114572, -0.385428, 0.5], [0.5, -0.454153, -0.045847]], dtype=np.float32
)
g_y2r_mat_bt709 = np.array([[1, 0, 1.5748], [1, -0.187324, -0.468124], [1, 1.8556, 0]], dtype=np.float32)

def round_rshift(value, shift: int):
    if shift > 0:
        half = 1 << (shift - 1)
        ret = (np.abs(value) + half) >> shift
        return np.copysign(ret, value).astype(ret.dtype)
    return value << -shift

class AcmEVideo:
    def __init__(self, len_y: int = 9, len_s: int = 13, len_h: int = 65, len_h2: int = 0):
        self.b_lut_ready = False
        self.gain_y = 256  # [0, (256), 1023], 8bit fixed
        self.gain_s = 256  # [0, (256), 1023], 8bit fixed
        self.gain_h = 256  # [0, (256), 1023], 8bit fixed
        self.set_len(len_y, len_s, len_h, len_h2)
        self.rand_seed = -1

    def set_len(self, len_y: int, len_s: int, len_h: int, len_h2: int = 0, kernel: np.ndarray = None):
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
        self.update_lut(kernel)

    def set_gain(self, gain_y: int, gain_s: int, gain_h: int):
        self.gain_y = gain_y
        self.gain_s = gain_s
        self.gain_h = gain_h
        print(f"[ACM] set lut gain: y={self.gain_y}, s={self.gain_s}, h={self.gain_h}")

    def update_lut(self, kernel: np.ndarray = None):
        if not self.b_lut_ready:
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
        delta_y = delta_y * (gain_yy * gain_sy)  # S9*S8*S8 => S23
        delta_s = delta_s * (gain_ys * gain_ss)  # S7*S8*S8 => S21
        delta_h = delta_h * (gain_yh * gain_sh)  # S9*S8*S8 => S23
        delta_y = round_rshift(delta_y, 14)
        delta_s = round_rshift(delta_s, 14)
        delta_h = round_rshift(delta_h, 14)

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

    def load_json(self, filename: str):
        ## check config file validity
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
        lut_delta_ybyh = np.zeros(self.len_h, dtype=np.int16)
        lut_delta_sbyh = np.zeros(self.len_h, dtype=np.int16)
        lut_delta_hbyh = np.zeros(self.len_h, dtype=np.int16)
        lut_gain_ybyy = np.zeros((self.len_h2, self.len_y), dtype=np.int8)
        lut_gain_sbyy = np.zeros((self.len_h2, self.len_y), dtype=np.int8)
        lut_gain_hbyy = np.zeros((self.len_h2, self.len_y), dtype=np.int8)
        lut_gain_ybys = np.zeros((self.len_h2, self.len_s), dtype=np.int8)
        lut_gain_sbys = np.zeros((self.len_h2, self.len_s), dtype=np.int8)
        lut_gain_hbys = np.zeros((self.len_h2, self.len_s), dtype=np.int8)

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

                ## guess lut length
                len_h = data["lutLengthH"] if "lutLengthH" in data else len(lut_delta_ybyh)
                if len(lut_gain_ybyy) == 65 * 9 and len(lut_gain_ybys) == 65 * 13:
                    len_y = 9
                    len_s = 13
                    len_h2 = 65
                else:
                    print("WARNING: unknow len_y/s/h2 !!! use default value.")

                ## check if need to transpose the LUT size
                if lut2dAxis4HD:
                    lut_gain_ybyy = lut_gain_ybyy.reshape(len_y, len_h2).T
                    lut_gain_sbyy = lut_gain_sbyy.reshape(len_y, len_h2).T
                    lut_gain_hbyy = lut_gain_hbyy.reshape(len_y, len_h2).T
                    lut_gain_ybys = lut_gain_ybys.reshape(len_s, len_h2).T
                    lut_gain_sbys = lut_gain_sbys.reshape(len_s, len_h2).T
                    lut_gain_hbys = lut_gain_hbys.reshape(len_s, len_h2).T

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
            "version": f"acm_impl_var_lut_rand_seed_{self.rand_seed}" if self.rand_seed > 0 else "acm_impl_var_lut",
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

        tmp_lut_delta_ybyh = np.random.uniform(-1, 1, 65).reshape(1, 65) * 300
        tmp_lut_delta_hbyh = np.random.uniform(-1, 1, 65).reshape(1, 65) * 100
        tmp_lut_delta_sbyh = np.random.uniform(-1, 1, 65).reshape(1, 65) * 300
        tmp_lut_delta_ybyh = cv2.GaussianBlur(tmp_lut_delta_ybyh, ksize=(5, 1), sigmaX=1.0)
        tmp_lut_delta_hbyh = cv2.GaussianBlur(tmp_lut_delta_hbyh, ksize=(5, 1), sigmaX=1.0)
        tmp_lut_delta_sbyh = cv2.GaussianBlur(tmp_lut_delta_sbyh, ksize=(5, 1), sigmaX=1.0)
        self.lut_delta_ybyh = np.clip(tmp_lut_delta_ybyh.flatten(), -256, 255).astype(np.int16)
        self.lut_delta_hbyh = np.clip(tmp_lut_delta_hbyh.flatten(), -64, 64).astype(np.int16)
        self.lut_delta_sbyh = np.clip(tmp_lut_delta_sbyh.flatten(), -256, 255).astype(np.int16)

        ## generate S/H LUTs strictly for the bug of VOP_ACM, which means:
        ## 1. LUT[0] = LUT[64], make sure the first and last value are the same (h=-180/+180)
        ## 2. LUT[0] = 0, make sure the first delta values are zero (h=-180)
        if b_strict:
            self.lut_delta_ybyh[-1] = self.lut_delta_ybyh[0]
            self.lut_delta_hbyh[-1] = self.lut_delta_hbyh[0] = 0
            self.lut_delta_sbyh[-1] = self.lut_delta_sbyh[0] = 0

        self.rand_seed = random_seed
        print(f"[ACM] generated a test config, b_strict={b_strict}, random_seed={random_seed}.")


def main():
    ## arg parser
    parser = argparse.ArgumentParser(exit_on_error=False)
    parser.add_argument("-i", "--input", default="", type=str, help="输入图像文件, yuv444p格式")
    parser.add_argument("-o", "--output", default="", type=str, help="输出图像文件")
    parser.add_argument("-c", "--config", default="", type=str, help=".json配置文件")
    parser.add_argument("-w", "--width", default=1920, type=int, help="图像宽度，默认: 1920")
    parser.add_argument("-g", "--height", default=1080, type=int, help="图像高度，默认: 1080")
    parser.add_argument("-G", "--gain", type=int, nargs='+', help="LUT gain 数组, 4个元素")
    parser.add_argument("-C", "--color", type=int, nargs='+', help="传入R/G/B数值测试结果")
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

    acm = AcmEVideo()

    if args.config != "":
        ret = acm.load_json(cfgfile)
        if not ret:
            print("[ACM] load config failed.")
            exit(ret)

    if args.gain:
        acm.set_gain(args.gain[0], args.gain[1], args.gain[2])

    if args.color:
        if len(args.color) > 3:
            args.color = args.color[:3]
        elif len(args.color) > 0 and len(args.color) < 3:
            args.color = np.append(args.color, np.zeros(3 - len(args.color), dtype=np.int32))

        yuv = g_r2y_mat_bt709 @ np.array(args.color) + np.array([0, 128, 128])
        yuv = np.clip(yuv + 0.5, 0, 255).astype(np.int32)
        ycbcr = yuv - np.array([0, 128, 128])
        h, s, _, _ = cordic.cordic_cbcr2hs(ycbcr[1], ycbcr[2], 8, 13, 8, False)
        ysh = np.array([yuv[0], s, h]).astype(int)
        print(f"[ACM] color={args.color} -> yuv={yuv} -> ycbcr={ycbcr} -> ysh={ysh} unit of h: deg")
        exit(0)

    out = acm.do_acm_u8(img)

    ## write planar Y then Cb then Cr (same layout as input file)
    out.transpose(2, 0, 1).tofile(outfile)  # HWC to CHW
    print(f"[ACM] done. write output file to {outfile}")

    acm.dump_json(f"{DEF_OUT_DIR}/acm_var_config_len_y{acm.len_y}_s{acm.len_s}_h{acm.len_h}_{acm.len_h2}.json")
    acm.dump_lut(DEF_OUT_DIR)


if __name__ == '__main__':
    main()
