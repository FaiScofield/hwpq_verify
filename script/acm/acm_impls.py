"""
Copyright   : Copyright (c) 2026 by Rockchip. All right reserved.
FilePath    : acm_impls.py
Author      : vance.wu@rock-chips.com
Date        : 2026-06-14
Description : Concrete ACM implementation subclasses.

    * AcmImplHwRk       - hardware ACM, 4 LUTs at (9, 13, 65, 17)
    * AcmImplSwRk       - software ACM matching RK semantics, (9, 13, 65, 65)
    * AcmImplSwEvideo   - evideo ACM, (9, 13, 65, 65) with wider delta range
    * AcmImplSwVariant  - any (y, s, h, h2) with h2 <= h
LastEditTime: 2026-06-14
"""

import os
import sys
import argparse
import numpy as np
from typing import Optional

if __package__:
    from .acm_impl_base import (
        AcmImplBase,
        ACM_DELTA_Y_MAX,
        ACM_DELTA_S_MAX,
        ACM_DELTA_H_MAX,
        ACM_HSV_GRAY_THRESHOLD_S,
        linear_resize_array_1d,
        linear_resize_array_2d,
        bicubic_resize_array_1d,
        bicubic_resize_array_2d,
    )
    from ..bcsh.hsv_adjust import rgb_to_hsv, hsv_to_rgb
    from . import cordic
    from .. import utils as utl
else:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    from acm_impl_base import (
        AcmImplBase,
        ACM_DELTA_Y_MAX,
        ACM_DELTA_S_MAX,
        ACM_DELTA_H_MAX,
        ACM_HSV_GRAY_THRESHOLD_S,
        linear_resize_array_1d,
        linear_resize_array_2d,
        bicubic_resize_array_1d,
        bicubic_resize_array_2d,
    )
    from bcsh.hsv_adjust import rgb_to_hsv, hsv_to_rgb
    import cordic
    import utils as utl


# ---------------------------------------------------------------------------
# AcmImplHwRk
# ---------------------------------------------------------------------------
class AcmImplHwRk(AcmImplBase):
    """ACM implementation for RK VOP hardware. len_h2 = 17."""

    def __init__(
        self,
        len_y: int = 9,
        len_s: int = 13,
        len_h: int = 65,
        len_h2: int = 17,
        delta_range: tuple = (0.25, 0.25, 64),
        use_cordic: bool = True,
    ):
        super().__init__(
            len_y=len_y, len_s=len_s, len_h=len_h, len_hd=len_h2, delta_range=delta_range, use_cordic=use_cordic
        )
        self.name = "AcmImplHwRk"
        print("[ACM] created AcmImplHwRk.")

    ## override
    def do_acm_u8(self, planar_data: np.ndarray, isRgb: bool = False, use_cordic: Optional[bool] = None) -> np.ndarray:
        """Hardware ACM on 8-bit YUV444p — replicates rkvop_pq_acm::process2()."""
        if isRgb:
            return super().do_acm_u8(planar_data, isRgb=True)
        return self._do_acm_hw(planar_data, 8)

    def do_acm_u10(self, planar_data: np.ndarray, isRgb: bool = False, use_cordic: Optional[bool] = None) -> np.ndarray:
        """Hardware ACM on 10-bit YUV444p — replicates rkvop_pq_acm::process2()."""
        if isRgb:
            return super().do_acm_u10(planar_data, isRgb=True)
        return self._do_acm_hw(planar_data, 10)

    def _do_acm_hw(self, planar_data: np.ndarray, depth: int) -> np.ndarray:
        """Replicate rkvop_pq_acm::process2() fixed‑point ACM pipeline.

        Uses depth‑specific acm_fix_coef (8‑bit: dc_UV=128/Ymax=255/Smax=181;
        10‑bit: dc_UV=512/Ymax=1023/Smax=724).  No bit‑depth promotion is
        applied — values stay in their native range, matching the C++ behaviour.
        """

        # ---- C++ macro replicas ----
        def SHIFT_ROUND_S32(x, n):
            return np.right_shift(x + (1 << (n - 1)) + np.right_shift(x, 31), n)

        _, H_img, W_img = planar_data.shape
        is_u8 = depth == 8

        # ---- acm_fix_coef (acm_8bit / acm_10bit) ----
        dc_UV = 128 if is_u8 else 512
        YUV_maxvalue = 255 if is_u8 else 1023
        S_maxvalue = 181 if is_u8 else 724

        # ---- bit-width constants ----
        ACM_FIX_BIT_WEIGHT_Y = 7
        ACM_FIX_BIT_WEIGHT_S = 7
        ACM_FIX_BIT_WEIGHT_H = 7
        ACM_FIX_BIT_WEIGHT_HD = 7
        ACM_FIX_BIT_WEIGHT_KEEP = 2
        RKVOP_PQ_ACM_CORDIC_S_BITS = 3
        RKVOP_PQ_ACM_TANTABFIXTMP = 46080

        delta_lut = (
            self.lut_delta_ybyh.astype(np.int32),
            self.lut_delta_hbyh.astype(np.int32),
            self.lut_delta_sbyh.astype(np.int32),
        )
        # Keep gain LUTs in the unified (Y/S, HD) layout used by the sampler.
        gain_lut_hy = (
            self.lut_gain_ybyy.astype(np.int32),
            self.lut_gain_hbyy.astype(np.int32),
            self.lut_gain_sbyy.astype(np.int32),
        )
        gain_lut_hs = (
            self.lut_gain_ybys.astype(np.int32),
            self.lut_gain_hbys.astype(np.int32),
            self.lut_gain_sbys.astype(np.int32),
        )

        # ---- 1. Extract planar channels ----
        Y = planar_data[0].astype(np.int32)
        U = planar_data[1].astype(np.int32)
        V = planar_data[2].astype(np.int32)
        CB = U - dc_UV
        CR = V - dc_UV

        # ---- 2. CORDIC: CB/CR → H/S ----
        H, S, _, _ = cordic.cordic_cbcr2hs(CB, CR, depth, 13, 6, RKVOP_PQ_ACM_CORDIC_S_BITS)
        HP = np.right_shift(H + RKVOP_PQ_ACM_TANTABFIXTMP, 6)

        # ---- 3. H index / weight ----
        shiftH = 17 - 6 - ACM_FIX_BIT_WEIGHT_H
        if shiftH > 0:
            H_idx_wgt = np.right_shift(HP * 91 + (1 << (shiftH - 1)), shiftH)
        else:
            H_idx_wgt = HP * 91
        idxH0 = np.right_shift(H_idx_wgt, ACM_FIX_BIT_WEIGHT_H)
        idxH1 = np.minimum(idxH0 + 1, 64)
        wgtH1 = H_idx_wgt & ((1 << ACM_FIX_BIT_WEIGHT_H) - 1)
        wgtH0 = (1 << ACM_FIX_BIT_WEIGHT_H) - wgtH1

        # ---- 4. HD index / weight (len_hd=17) ----
        if self.len_hd == self.len_h:
            idxHD0, idxHD1 = idxH0, idxH1
            wgtHD1, wgtHD0 = wgtH1, wgtH0
        else:
            shiftHD = 17 - 4 - ACM_FIX_BIT_WEIGHT_HD
            if shiftHD > 0:
                HD_idx_wgt = np.right_shift(HP * 91 + (1 << (shiftHD - 1)), shiftHD)
            else:
                HD_idx_wgt = HP * 91
            idxHD0 = np.right_shift(HD_idx_wgt, ACM_FIX_BIT_WEIGHT_HD)
            idxHD1 = np.minimum(idxHD0 + 1, 16)
            wgtHD1 = HD_idx_wgt & ((1 << ACM_FIX_BIT_WEIGHT_HD) - 1)
            wgtHD0 = (1 << ACM_FIX_BIT_WEIGHT_HD) - wgtHD1

        # ---- 5. Y index / weight ----
        idxY0 = np.right_shift(Y, ACM_FIX_BIT_WEIGHT_Y)
        idxY1 = np.minimum(idxY0 + 1, 8)
        wgtY1 = np.bitwise_and(Y, (1 << ACM_FIX_BIT_WEIGHT_Y) - 1)
        wgtY0 = (1 << ACM_FIX_BIT_WEIGHT_Y) - wgtY1

        # ---- 6. S index / weight ----
        shiftS = 17 - 4 - ACM_FIX_BIT_WEIGHT_S
        if shiftS > 0:
            S_idx_wgt = np.right_shift(S * 17 + (1 << (shiftS - 1)), shiftS)
        else:
            S_idx_wgt = S * 17
        idxS0 = np.right_shift(S_idx_wgt, ACM_FIX_BIT_WEIGHT_S)
        idxS1 = np.minimum(idxS0 + 1, 12)
        wgtS1 = S_idx_wgt & ((1 << ACM_FIX_BIT_WEIGHT_S) - 1)
        wgtS0 = (1 << ACM_FIX_BIT_WEIGHT_S) - wgtS1

        # ---- 7. Pre-compute bilinear weights ----
        wgtFixBitYH = ACM_FIX_BIT_WEIGHT_Y + ACM_FIX_BIT_WEIGHT_HD
        wgtYH00 = wgtY0 * wgtHD0
        wgtYH01 = wgtY0 * wgtHD1
        wgtYH10 = wgtY1 * wgtHD0
        wgtYH11 = wgtY1 * wgtHD1

        wgtFixBitSH = ACM_FIX_BIT_WEIGHT_S + ACM_FIX_BIT_WEIGHT_HD
        wgtSH00 = wgtS0 * wgtHD0
        wgtSH01 = wgtS0 * wgtHD1
        wgtSH10 = wgtS1 * wgtHD0
        wgtSH11 = wgtS1 * wgtHD1

        # ---- helper: 4‑point bilinear lookup ----
        def _sample_4pt(lut, iH0, iH1, iV0, iV1, w00, w01, w10, w11, wgtFixBits):
            tl = lut[iV0, iH0] * w00
            tr = lut[iV0, iH1] * w01
            bl = lut[iV1, iH0] * w10
            br = lut[iV1, iH1] * w11
            return SHIFT_ROUND_S32(tl + tr + bl + br, wgtFixBits - ACM_FIX_BIT_WEIGHT_KEEP)

        # ---- 8. 1D delta lookup ----
        def _delta_1d(lut_1d, idx0, idx1, w0, w1):
            d0 = lut_1d[idx0] * w0
            d1 = lut_1d[idx1] * w1
            return SHIFT_ROUND_S32(d0 + d1, ACM_FIX_BIT_WEIGHT_H - ACM_FIX_BIT_WEIGHT_KEEP)

        dy = _delta_1d(delta_lut[0], idxH0, idxH1, wgtH0, wgtH1)
        dh = _delta_1d(delta_lut[1], idxH0, idxH1, wgtH0, wgtH1)
        ds = _delta_1d(delta_lut[2], idxH0, idxH1, wgtH0, wgtH1)

        # ---- 9. Apply global gain to delta ----
        dy = SHIFT_ROUND_S32(dy.astype(np.int64) * self.gain_y, 8).astype(np.int32)
        dh = SHIFT_ROUND_S32(dh.astype(np.int64) * self.gain_h, 8).astype(np.int32)
        ds = SHIFT_ROUND_S32(ds.astype(np.int64) * self.gain_s, 8).astype(np.int32)
        dy = np.clip(dy, -1023, 1023)
        dh = np.clip(dh, -255, 255)
        ds = np.clip(ds, -1023, 1023)

        # ---- 10. 2D gain lookups ----
        if self.ignore_gain_luts:
            wy_hy = np.full_like(dy, 128 << ACM_FIX_BIT_WEIGHT_KEEP, dtype=np.int32)
            wh_hy = np.full_like(dh, 128 << ACM_FIX_BIT_WEIGHT_KEEP, dtype=np.int32)
            ws_hy = np.full_like(ds, 128 << ACM_FIX_BIT_WEIGHT_KEEP, dtype=np.int32)
            wy_hs = np.full_like(dy, 128 << ACM_FIX_BIT_WEIGHT_KEEP, dtype=np.int32)
            wh_hs = np.full_like(dh, 128 << ACM_FIX_BIT_WEIGHT_KEEP, dtype=np.int32)
            ws_hs = np.full_like(ds, 128 << ACM_FIX_BIT_WEIGHT_KEEP, dtype=np.int32)
        else:
            wy_hy = _sample_4pt(
                gain_lut_hy[0], idxHD0, idxHD1, idxY0, idxY1, wgtYH00, wgtYH01, wgtYH10, wgtYH11, wgtFixBitYH
            )
            wh_hy = _sample_4pt(
                gain_lut_hy[1], idxHD0, idxHD1, idxY0, idxY1, wgtYH00, wgtYH01, wgtYH10, wgtYH11, wgtFixBitYH
            )
            ws_hy = _sample_4pt(
                gain_lut_hy[2], idxHD0, idxHD1, idxY0, idxY1, wgtYH00, wgtYH01, wgtYH10, wgtYH11, wgtFixBitYH
            )
            wy_hs = _sample_4pt(
                gain_lut_hs[0], idxHD0, idxHD1, idxS0, idxS1, wgtSH00, wgtSH01, wgtSH10, wgtSH11, wgtFixBitSH
            )
            wh_hs = _sample_4pt(
                gain_lut_hs[1], idxHD0, idxHD1, idxS0, idxS1, wgtSH00, wgtSH01, wgtSH10, wgtSH11, wgtFixBitSH
            )
            ws_hs = _sample_4pt(
                gain_lut_hs[2], idxHD0, idxHD1, idxS0, idxS1, wgtSH00, wgtSH01, wgtSH10, wgtSH11, wgtFixBitSH
            )

        # ---- 10b. Save raw intermediate values for UI inspection ----
        # Normalise HW fixed-point values to match _do_acm_yuv semantics.
        # delta_y/s: HW range [-1023,1023] -> normalised [-0.25, 0.25]
        # delta_h:   HW range [-255, 255]  -> normalised [-64, 64]
        # gain_*:    HW range (unity=512)  -> normalised [-1, 1]
        self._last_delta_y_raw = dy.astype(np.float32) / 4095.0
        self._last_delta_s_raw = ds.astype(np.float32) / 4095.0
        self._last_delta_h_raw = dh.astype(np.float32) / 4.0
        self._last_gain_yy = wy_hy.astype(np.float32) / 511.0
        self._last_gain_ys = wy_hs.astype(np.float32) / 511.0
        self._last_gain_sy = ws_hy.astype(np.float32) / 511.0
        self._last_gain_ss = ws_hs.astype(np.float32) / 511.0
        self._last_gain_hy = wh_hy.astype(np.float32) / 511.0
        self._last_gain_hs = wh_hs.astype(np.float32) / 511.0
        self._last_intermediate_shape = dy.shape
        # ---- 11. Dual-gain delta chain ----
        Ydel0 = dy * wy_hy # S9*S8.2
        Hdel0 = dh * wh_hy
        Sdel0 = ds * ws_hy
        Ydel1 = SHIFT_ROUND_S32(Ydel0, 9) # S8.2
        Hdel1 = SHIFT_ROUND_S32(Hdel0, 9)
        Sdel1 = SHIFT_ROUND_S32(Sdel0, 9)

        Ydel2 = Ydel1 * wy_hs #S8.2*S8.2
        Hdel2 = Hdel1 * wh_hs
        Sdel2 = Sdel1 * ws_hs
        Ydel3 = SHIFT_ROUND_S32(Ydel2, 11) # S9
        Hdel3 = SHIFT_ROUND_S32(Hdel2, 3)
        Sdel3 = SHIFT_ROUND_S32(Sdel2, 11 - RKVOP_PQ_ACM_CORDIC_S_BITS) # S9.3

        # ---- 12. Zero delta when S == 0 ----
        # 1/4 scale for 8-bit (10-bit delta domain)
        Ydel = SHIFT_ROUND_S32(Ydel3, 2) if is_u8 else Ydel3
        Sdel = SHIFT_ROUND_S32(Sdel3, 2) if is_u8 else Sdel3
        Sdel = np.where(S == 0, 0, Sdel)
        Hdel = np.where(S == 0, 0, Hdel3)

        # ---- 13. Apply result to Y / S / H ----
        YO = np.clip(Y + Ydel, 0, YUV_maxvalue)
        SO = np.clip(S + Sdel, 0, S_maxvalue << RKVOP_PQ_ACM_CORDIC_S_BITS)

        HO = H + Hdel
        pi_flag = (HO < -RKVOP_PQ_ACM_TANTABFIXTMP).astype(np.int32) - (HO > RKVOP_PQ_ACM_TANTABFIXTMP).astype(np.int32)
        HO = HO + pi_flag * (2 * RKVOP_PQ_ACM_TANTABFIXTMP)

        # ---- 14. CORDIC: H/S → CB/CR → U/V ----
        CB, CR = cordic.cordic_hs2cbcr(
            HO, SO, 16, depth + RKVOP_PQ_ACM_CORDIC_S_BITS, depth, 13, 6 - RKVOP_PQ_ACM_CORDIC_S_BITS
        )
        UO = np.clip(CB + dc_UV, 0, YUV_maxvalue)
        VO = np.clip(CR + dc_UV, 0, YUV_maxvalue)

        # ---- 15. Pack planar output ----
        out = np.empty((3, H_img, W_img), dtype=np.uint8 if is_u8 else np.uint16)
        out[0] = YO.astype(out.dtype)
        out[1] = UO.astype(out.dtype)
        out[2] = VO.astype(out.dtype)
        return out


# ---------------------------------------------------------------------------
# AcmImplSwRk
# ---------------------------------------------------------------------------
class AcmImplSwRk(AcmImplBase):
    """ACM implementation matching RK software semantics. len_h2 = 65."""

    def __init__(
        self,
        len_y: int = 9,
        len_s: int = 13,
        len_h: int = 65,
        len_h2: int = 65,
        delta_range: tuple = (0.25, 0.25, 64),
        use_cordic: bool = False,
    ):
        super().__init__(
            len_y=len_y, len_s=len_s, len_h=len_h, len_hd=len_h2, delta_range=delta_range, use_cordic=use_cordic
        )
        self.name = "AcmImplSwRk"
        print("[ACM] created AcmImplSwRk.")


# ---------------------------------------------------------------------------
# AcmImplSwEvideo
# ---------------------------------------------------------------------------
class AcmImplSwEvideo(AcmImplBase):
    """EVideo-style ACM with wider delta mapping range.

    Default delta_range is (1.0, 1.0, 64) (delta_y/s in [-1, 1] of full range, h in [-64, 64] deg).
    Can be switched to 0.25 via set_delta_range(0.25) to match the rk semantics.
    """

    def __init__(
        self,
        len_y: int = 9,
        len_s: int = 13,
        len_h: int = 65,
        len_h2: int = 65,
        delta_range: tuple = (1.0, 1.0, 64),
        use_cordic: bool = False,
    ):
        super().__init__(
            len_y=len_y, len_s=len_s, len_h=len_h, len_hd=len_h2, delta_range=delta_range, use_cordic=use_cordic
        )
        self.name = "AcmImplSwEvideo"
        print("[ACM] created AcmImplSwEvideo.")


# ---------------------------------------------------------------------------
# AcmImplSwVariant
# ---------------------------------------------------------------------------
class AcmImplSwVariant(AcmImplBase):
    """ACM with arbitrary LUT lengths (only constraint: len_h2 <= len_h).

    The 4 len arguments can be changed at runtime via set_len / set_step.
    The current LUT is always re-sampled (bicubic) from the default LUT
    when the length changes; call sync_to_default() to push runtime edits
    back into the default set (bicubic).
    """

    def __init__(
        self,
        len_y: int = 9,
        len_s: int = 13,
        len_h: int = 65,
        len_h2: int = 65,
        delta_range: tuple = (1.0, 1.0, 64),
        use_cordic: bool = False,
    ):
        super().__init__(
            len_y=len_y, len_s=len_s, len_h=len_h, len_hd=len_h2, delta_range=delta_range, use_cordic=use_cordic
        )
        self.name = "AcmImplSwVariant"
        print("[ACM] created AcmImplSwVariant.")

    def do_acm_u8(self, planar_data: np.ndarray, isRgb=False, use_cordic=None):
        if isRgb:
            return self._do_acm_rgb_variant(planar_data, rng=256)
        if use_cordic is None:
            use_cordic = self.use_cordic
        return self._do_acm_yuv_variant(planar_data, depth=8, use_cordic=use_cordic)

    def do_acm_u10(self, planar_data: np.ndarray, isRgb=False, use_cordic=None):
        if isRgb:
            return self._do_acm_rgb_variant(planar_data, rng=1024)
        if use_cordic is None:
            use_cordic = self.use_cordic
        return self._do_acm_yuv_variant(planar_data, depth=10, use_cordic=use_cordic)

    def _do_acm_rgb_variant(self, planar_data: np.ndarray, rng: int) -> np.ndarray:
        """Variant ACM on full-range RGB via the HSV path（RGB/HSV 处理域）。

        与 :meth:`_do_acm_yuv_variant` 语义一致：gain 后置（不在 LUT 归一化时
        乘入）、delta_s 乘性（LUT 归一化到 [0,2]，S'=S·delta_s）、delta_y/h
        按 delta_range 钳位；域转换用 hsv_adjust.py 的 rgb_to_hsv / hsv_to_rgb
        （六边形 HSV，与 BCSH 工具一致的参考实现）。灰阶像素旁路 LUT，直接
        施加 RGB offset（wr/wg/wb，256 为中性）。
        输入 [H,W,3] full-range 整数；返回 [C,H,W]。
        """
        import cv2
        y_max = float(rng - 1)
        dr_y, _dr_s, dr_h = self.delta_range  # delta_s 为乘性，不使用 dr_s 缩放

        # ---- 1. normalize [0,1] ----
        rgb_f = planar_data.astype(np.float32) / y_max
        r = rgb_f[..., 0]
        g = rgb_f[..., 1]
        b = rgb_f[..., 2]
        v0 = np.max(rgb_f, axis=-1)
        m0 = np.min(rgb_f, axis=-1)
        delta_val = v0 - m0

        # ---- 2. gray bypass：LUT 旁路，直接施加 RGB offset ----
        is_gray = delta_val < ACM_HSV_GRAY_THRESHOLD_S
        rgb_offset = np.array(
            [(self.offset_wr - 256) / 512.0,
             (self.offset_wg - 256) / 512.0,
             (self.offset_wb - 256) / 512.0], dtype=np.float32)
        rgb_gray = np.clip(rgb_f + rgb_offset[None, None, :], 0.0, 1.0)

        # ---- 3. RGB -> HSV（hsv_adjust 六边形 HSV：h∈[0,360), s/v∈[0,1]） ----
        h, s, v = rgb_to_hsv(rgb_f)          # h/s/v 均为 (H,W)
        h = np.where(is_gray, 0.0, h)
        s = np.where(is_gray, 0.0, s)

        # ---- 4. 归一化 LUT（gain 后置；delta_s 乘性） ----
        lut_dy = np.clip(self.lut_delta_ybyh.astype(np.float32) / ACM_DELTA_Y_MAX * dr_y, -dr_y, dr_y)
        lut_ds = np.clip(self.lut_delta_sbyh.astype(np.float32) / ACM_DELTA_S_MAX + 1.0, 0.0, 2.0)
        lut_dh = np.clip(self.lut_delta_hbyh.astype(np.float32) / ACM_DELTA_H_MAX * dr_h, -dr_h, dr_h)
        lut_gy_y = self.lut_gain_ybyy.astype(np.float32) / 127.0
        lut_gs_y = self.lut_gain_sbyy.astype(np.float32) / 127.0
        lut_gh_y = self.lut_gain_hbyy.astype(np.float32) / 127.0
        lut_gy_s = self.lut_gain_ybys.astype(np.float32) / 127.0
        lut_gs_s = self.lut_gain_sbys.astype(np.float32) / 127.0
        lut_gh_s = self.lut_gain_hbys.astype(np.float32) / 127.0

        # ---- 5. LUT 索引：h 用 hp=(h+180)%360 对齐 YUV 域 LUT 的 H 轴 ----
        hp_deg = np.mod(h + 180.0, 360.0)
        idx_h = (hp_deg / 360.0 * (self.len_h - 1)).astype(np.float32)      # delta 1D（len_h）
        idx_hd = (hp_deg / 360.0 * (self.len_hd - 1)).astype(np.float32)    # gain 2D 第二轴（len_hd）
        idx_v = (v * (self.len_y - 1)).astype(np.float32)
        idx_s = (s * (self.len_s - 1)).astype(np.float32)
        idx_zeros = np.zeros_like(idx_h)

        # ---- 6. 采样 delta 表（1D，按 H） ----
        _kw = dict(interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        delta_y = cv2.remap(lut_dy.reshape(1, -1), idx_h, idx_zeros, **_kw)
        delta_s = cv2.remap(lut_ds.reshape(1, -1), idx_h, idx_zeros, **_kw)
        delta_h = cv2.remap(lut_dh.reshape(1, -1), idx_h, idx_zeros, **_kw)

        # ---- 7. 采样 gain 表（2D，按 (V/S, HD)） ----
        if self.ignore_gain_luts:
            gain_yy = np.ones_like(delta_y, dtype=np.float32)
            gain_ys = np.ones_like(delta_y, dtype=np.float32)
            gain_hy = np.ones_like(delta_y, dtype=np.float32)
            gain_sy = np.ones_like(delta_y, dtype=np.float32)
            gain_ss = np.ones_like(delta_y, dtype=np.float32)
            gain_hs = np.ones_like(delta_y, dtype=np.float32)
        else:
            gain_yy = cv2.remap(lut_gy_y, idx_hd, idx_v, **_kw)   # ybyy 按 (V, HD)
            gain_ys = cv2.remap(lut_gs_y, idx_hd, idx_v, **_kw)   # sbyy 按 (V, HD)
            gain_hy = cv2.remap(lut_gh_y, idx_hd, idx_v, **_kw)   # hbyy 按 (V, HD)
            gain_sy = cv2.remap(lut_gy_s, idx_hd, idx_s, **_kw)   # ybys 按 (S, HD)
            gain_ss = cv2.remap(lut_gs_s, idx_hd, idx_s, **_kw)   # sbys 按 (S, HD)
            gain_hs = cv2.remap(lut_gh_s, idx_hd, idx_s, **_kw)   # hbys 按 (S, HD)

        # ---- 8. 中间值缓存（UI 标注 get_pixel_intermediates） ----
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

        # ---- 9. 合并 delta（gain 后置） ----
        g_y = self.gain_y / 256.0
        g_s = self.gain_s / 256.0
        g_h = self.gain_h / 256.0
        delta_y = np.clip(delta_y * gain_yy * gain_ys * g_y, -dr_y, dr_y)
        delta_s = np.clip(delta_s * gain_sy * gain_ss * g_s, 0.0, 2.0)
        delta_h = np.clip(delta_h * gain_hy * gain_hs * g_h, -dr_h, dr_h)

        # ---- 10. 应用到 HSV ----
        h_new = np.mod(h + delta_h, 360.0)
        s_new = np.clip(s * delta_s, 0.0, 1.0)
        v_new = np.clip(v + delta_y, 0.0, 1.0)

        # ---- 11. HSV -> RGB（hsv_adjust 纯 numpy） ----
        rgb_new = hsv_to_rgb(np.stack([h_new, s_new, v_new], axis=-1))

        # ---- 12. 灰阶合并 ----
        rgb_out_f = np.where(is_gray[..., None], rgb_gray, rgb_new)

        # ---- 13. 量化回整数 [C,H,W] ----
        rgb_q = np.clip(np.rint(rgb_out_f * y_max), 0.0, y_max)
        dtype = np.uint16 if rng > 256 else np.uint8
        rgb_out = np.empty((3, rgb_f.shape[0], rgb_f.shape[1]), dtype=dtype)
        for ch in range(3):
            rgb_out[ch] = rgb_q[..., ch].astype(dtype)
        return rgb_out

    def _do_acm_yuv_variant(self, planar_data: np.ndarray, depth: int, use_cordic: bool):
        """Variant ACM pipeline: gains applied late, delta_s multiplicative."""
        import cv2

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
            s = np.rint(np.sqrt(cb * cb + cr * cr)).astype(np.int32) # [0,181]/[0,724]
            h_rad = np.arctan2(cr, cb)  # [-pi, pi]
            h_deg = np.rint(np.rad2deg(h_rad)).astype(np.int32)  # [-180, 180]

        # ---- 2. Normalise LUT tables (apply gain & delta_range upfront) ----
        dr_y, _, dr_h = self.delta_range  # (0.25, 0.25, 64) or (1.0, 1.0, 64)
        lut_dy = np.clip(self.lut_delta_ybyh.astype(np.float32) / ACM_DELTA_Y_MAX * dr_y, -dr_y, dr_y)
        lut_ds = np.clip(self.lut_delta_sbyh.astype(np.float32) / ACM_DELTA_S_MAX + 1.0, 0, 2.0) # [0, 2]
        lut_dh = np.clip(self.lut_delta_hbyh.astype(np.float32) / ACM_DELTA_H_MAX * dr_h, -dr_h, dr_h)
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
            gain_ys = np.ones_like(delta_s, dtype=np.float32)
            gain_hy = np.ones_like(delta_h, dtype=np.float32)
            gain_sy = np.ones_like(delta_y, dtype=np.float32)
            gain_ss = np.ones_like(delta_s, dtype=np.float32)
            gain_hs = np.ones_like(delta_h, dtype=np.float32)
        else:
            gain_yy = cv2.remap(lut_gy_y, idx_hd, idx_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
            gain_ys = cv2.remap(lut_gs_y, idx_hd, idx_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
            gain_hy = cv2.remap(lut_gh_y, idx_hd, idx_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
            gain_sy = cv2.remap(lut_gy_s, idx_hd, idx_s, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
            gain_ss = cv2.remap(lut_gs_s, idx_hd, idx_s, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
            gain_hs = cv2.remap(lut_gh_s, idx_hd, idx_s, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


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
        # ---- 6. Combine deltas (apply global gains HERE instead of upfront) ----
        g_y = self.gain_y / 256.0
        g_s = self.gain_s / 256.0
        g_h = self.gain_h / 256.0
        delta_y = np.clip(delta_y * gain_yy * gain_ys * g_y, -dr_y, dr_y)
        delta_s = np.clip(delta_s * gain_sy * gain_ss * g_s, 0, 2)  # [0, 2]
        delta_h = np.clip(delta_h * gain_hy * gain_hs * g_h, -dr_h, dr_h)

        # ---- 7. Apply to normalised values ----
        h_deg_new = np.mod(h_deg + delta_h, 360.0) # [0, 360]
        if self.clip_type == "luma_clip":
            y_new = np.clip(y_f + delta_y, 0.0, 1.0)
            h_deg_new = np.mod(h_deg + delta_h, 360.0)
            s_new, s_max_old, s_max_new = self._sat_adjust_triangle(y_f, h_deg, s_f, y_new, h_deg_new)
            s_f = np.clip(s_new * delta_s, 0.0, s_max_new)
            y_f = y_new
        else:
            y_f = np.clip(y_f + delta_y, 0.0, 1.0)
            s_f = np.clip(s_f * delta_s, 0.0, 1.0)

        # ---- 8. Convert back to integer pixel domain ----
        h_deg_new = np.mod(h_deg + delta_h, 360.0)
        h_deg_new = np.where(h_deg_new < 0, h_deg_new + 360.0, h_deg_new)
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
        return yuv444p_out

    # ------------------------------------------------------------------
    # extra helper
    def interpolate_from(self, source_acm: AcmImplBase, kernel: np.ndarray = None) -> bool:
        """Interpolate LUT data from another ACM instance.

        Resamples all 9 LUT tables from source_acm to match self's dimensions.
        Both default and current sets are populated.
        """
        if not source_acm.b_lut_ready:
            print("[ACM] Source ACM LUT is not ready!")
            return False

        print(
            f"[ACM] Interpolating LUTs from source: "
            f"y={source_acm.len_y}x{self.len_y}, s={source_acm.len_s}x{self.len_s}, "
            f"h={source_acm.len_h}x{self.len_h}, h2={source_acm.len_hd}x{self.len_hd}"
        )

        # 1D delta LUTs
        if source_acm.len_h != self._default_len_h:
            self._default_lut_delta_ybyh = linear_resize_array_1d(
                source_acm._default_lut_delta_ybyh, self._default_len_h
            )
            self._default_lut_delta_sbyh = linear_resize_array_1d(
                source_acm._default_lut_delta_sbyh, self._default_len_h
            )
            self._default_lut_delta_hbyh = linear_resize_array_1d(
                source_acm._default_lut_delta_hbyh, self._default_len_h
            )
            print(f"[ACM] Updated delta LUT size: {source_acm.len_h} => {self._default_len_h}")
        else:
            self._default_lut_delta_ybyh = source_acm._default_lut_delta_ybyh.copy()
            self._default_lut_delta_sbyh = source_acm._default_lut_delta_sbyh.copy()
            self._default_lut_delta_hbyh = source_acm._default_lut_delta_hbyh.copy()

        # 2D gain LUTs (Y axis)
        self._default_lut_gain_ybyy = bicubic_resize_array_2d(
            source_acm._default_lut_gain_ybyy, self._default_len_y, self._default_len_hd, kernel
        )
        self._default_lut_gain_sbyy = bicubic_resize_array_2d(
            source_acm._default_lut_gain_sbyy, self._default_len_y, self._default_len_hd, kernel
        )
        self._default_lut_gain_hbyy = bicubic_resize_array_2d(
            source_acm._default_lut_gain_hbyy, self._default_len_y, self._default_len_hd, kernel
        )

        # 2D gain LUTs (S axis)
        self._default_lut_gain_ybys = bicubic_resize_array_2d(
            source_acm._default_lut_gain_ybys, self._default_len_s, self._default_len_hd, kernel
        )
        self._default_lut_gain_sbys = bicubic_resize_array_2d(
            source_acm._default_lut_gain_sbys, self._default_len_s, self._default_len_hd, kernel
        )
        self._default_lut_gain_hbys = bicubic_resize_array_2d(
            source_acm._default_lut_gain_hbys, self._default_len_s, self._default_len_hd, kernel
        )

        # Copy gains
        self.gain_y = source_acm.gain_y
        self.gain_s = source_acm.gain_s
        self.gain_h = source_acm.gain_h
        self.offset_wr = source_acm.offset_wr
        self.offset_wg = source_acm.offset_wg
        self.offset_wb = source_acm.offset_wb
        self.is_lut4rgb = source_acm.is_lut4rgb
        self.delta_range = source_acm.delta_range
        self.use_cordic = source_acm.use_cordic
        self.clip_type = source_acm.clip_type
        self.rand_seed = source_acm.rand_seed

        # Propagate default -> current
        self._resample_default_to_current(method="bicubic")
        self.b_lut_ready = True
        print("[ACM] Interpolation completed successfully.")
        return True


# ---------------------------------------------------------------------------
# CLI entry
# ---------------------------------------------------------------------------
def main() -> None:
    """Command-line entry for ACM LUT verify / dump.

    Reads a YUV444 planar image, loads (or generates) a LUT, applies ACM
    and writes the result back as a planar YUV file, then dumps the
    effective config and LUT preview.
    """
    parser = argparse.ArgumentParser(exit_on_error=False)
    parser.add_argument("-i", "--input", default="", type=str, help="输入图像文件，yuv444p格式")
    parser.add_argument("-o", "--output", default="", type=str, help="输出图像文件")
    parser.add_argument("-c", "--config", default="", type=str, help=".json 配置文件")
    parser.add_argument("-w", "--width", default=1920, type=int, help="图像宽度, 默认 1920")
    parser.add_argument("-g", "--height", default=1080, type=int, help="图像高度, 默认 1080")
    parser.add_argument("-s", "--step", type=float, nargs='+', help="LUT step 数组, 4 个元素")
    parser.add_argument("-l", "--len", type=int, nargs='+', help="LUT len 数组, 4 个元素")
    parser.add_argument("-G", "--gain", type=int, nargs='+', help="LUT gain 数组, 3 个元素")
    parser.add_argument("-n", "--iter_num", default=13, type=int, help="Cordic 迭代次数, 默认: 13")
    parser.add_argument("-b", "--increase_bits", default=3, type=int, help="Cordic S 定点提示精度, 默认: 3")
    parser.add_argument("-uv", "--uv", type=int, nargs='+', help="传入U/V数值测试Cordic结果")
    parser.add_argument("-hs", "--hs", type=int, nargs='+', help="传入H/S数值测试Cordic结果")
    parser.add_argument("-t", "--type", default=0, type=int, help="算法类型")
    args, _ = parser.parse_known_args()

    # DEF_OUT_DIR = "V:/hwpq_verify_data/vop_robin_fpga_verify_acm/test_var_lut"
    DEF_OUT_DIR = "D:/RkDefaultDumpData"
    H = args.height
    W = args.width
    infile = (
        "V:/hwpq_verify_data/vop_robin_fpga_verify_acm/input_1920x1080_yuv444p_601F.yuv"
        if args.input == ""
        else args.input
    )
    outfile = f"{DEF_OUT_DIR}/out_acm_1920x1080_yuv444p_601F.yuv" if args.output == "" else args.output
    cfgfile = (
        "G:/Codes/gerrit_projects/hwpq_verify/data/tmp_acm_config.json" if args.config == "" else args.config
    )

    ## read YUV444 planar (Y | Cb | Cr)
    data = np.fromfile(infile, np.uint8)
    img = np.zeros((3, H, W), dtype=np.uint8)
    img[0, :, :] = data[0 : H * W * 1].reshape(H, W)
    img[1, :, :] = data[H * W * 1 : H * W * 2].reshape(H, W)
    img[2, :, :] = data[H * W * 2 : H * W * 3].reshape(H, W)

    if args.type == 1:
        acm = AcmImplSwRk()
    elif args.type == 2:
        acm = AcmImplSwEvideo()
    elif args.type == 3:
        acm = AcmImplSwVariant()
    else:
        acm = AcmImplHwRk()

    if cfgfile != "":
        ret = acm.load_json(cfgfile)
        if not ret:
            print("[ACM] load config failed.")
            exit(ret)
    else:
        acm.set_len(9, 13, 65, 17)
        acm.gen_test_config(False)

    if args.step:
        acm.set_step(args.step[0], args.step[1], args.step[2], args.step[3])
    elif args.len:
        acm.set_len(args.len[0], args.len[1], args.len[2], args.len[3])
    if args.gain:
        acm.set_global_gains(args.gain[0], args.gain[1], args.gain[2])

    out = acm.do_acm_u8(img)

    ## write planar Y then Cb then Cr (same layout as input file)
    out.tofile(outfile)  # shape is already [C,H,W] (planar)
    print(f"[ACM] done. write output file to {outfile}")

    acm.dump_json(f"{DEF_OUT_DIR}/acm_var_config_len_y{acm.len_y}_s{acm.len_s}" f"_h{acm.len_h}_{acm.len_hd}.json")
    acm.dump_luts(DEF_OUT_DIR)
    utl.run_cmd(f"cp {infile} {DEF_OUT_DIR}")


if __name__ == '__main__':
    main()

    # b_strict = True
    # seed = 114517
    # acm = AcmImplSwRk(9, 13, 65, 65)
    # acm.gen_test_config(b_strict, seed)

    # kernel = np.array([1, 4, 6, 4, 1])
    # kernel = np.outer(kernel, kernel)
    # kernel = kernel / kernel.sum()
    # print("kernel: \n", kernel)

    # acm.set_len(9, 13, 65, 17, kernel)
    # if b_strict:
    #     acm.dump_json(
    #         f"acm_var_config_len_y{acm.len_y}_s{acm.len_s}_h{acm.len_h}"
    #         f"_hd{acm.len_hd}_strict_rand{seed}_kernel.json"
    #     )
    # else:
    #     acm.dump_json(f"acm_var_config_len_y{acm.len_y}_s{acm.len_s}_h{acm.len_h}" f"_hd{acm.len_hd}_rand{seed}.json")
