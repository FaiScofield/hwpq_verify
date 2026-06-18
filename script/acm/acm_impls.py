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
        ACM_DELTA_Y_MAX, ACM_DELTA_S_MAX, ACM_DELTA_H_MAX,
        linear_resize_array_1d,
        linear_resize_array_2d,
        bicubic_resize_array_1d,
        bicubic_resize_array_2d,
    )
    from . import cordic
    from .. import utils as utl
else:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    from acm_impl_base import (
        AcmImplBase,
        ACM_DELTA_Y_MAX, ACM_DELTA_S_MAX, ACM_DELTA_H_MAX,
        linear_resize_array_1d,
        linear_resize_array_2d,
        bicubic_resize_array_1d,
        bicubic_resize_array_2d,
    )
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

        H_img, W_img, _ = planar_data.shape
        is_u8 = (depth == 8)

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

        # ---- shorthand ----
        delta_lut = (
            self.lut_delta_ybyh.astype(np.int32),
            self.lut_delta_hbyh.astype(np.int32),
            self.lut_delta_sbyh.astype(np.int32),
        )
        gain_lut_hy = (
            self.lut_gain_ybyy.astype(np.int32).T,
            self.lut_gain_hbyy.astype(np.int32).T,
            self.lut_gain_sbyy.astype(np.int32).T,
        )
        gain_lut_hs = (
            self.lut_gain_ybys.astype(np.int32).T,
            self.lut_gain_hbys.astype(np.int32).T,
            self.lut_gain_sbys.astype(np.int32).T,
        )

        # ---- 1. Extract planar channels ----
        Y = planar_data[:, :, 0].astype(np.int32)
        U = planar_data[:, :, 1].astype(np.int32)
        V = planar_data[:, :, 2].astype(np.int32)
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
        wy_hy = _sample_4pt(gain_lut_hy[0], idxHD0, idxHD1, idxY0, idxY1,
                            wgtYH00, wgtYH01, wgtYH10, wgtYH11, wgtFixBitYH)
        wh_hy = _sample_4pt(gain_lut_hy[1], idxHD0, idxHD1, idxY0, idxY1,
                            wgtYH00, wgtYH01, wgtYH10, wgtYH11, wgtFixBitYH)
        ws_hy = _sample_4pt(gain_lut_hy[2], idxHD0, idxHD1, idxY0, idxY1,
                            wgtYH00, wgtYH01, wgtYH10, wgtYH11, wgtFixBitYH)
        wy_hs = _sample_4pt(gain_lut_hs[0], idxHD0, idxHD1, idxS0, idxS1,
                            wgtSH00, wgtSH01, wgtSH10, wgtSH11, wgtFixBitSH)
        wh_hs = _sample_4pt(gain_lut_hs[1], idxHD0, idxHD1, idxS0, idxS1,
                            wgtSH00, wgtSH01, wgtSH10, wgtSH11, wgtFixBitSH)
        ws_hs = _sample_4pt(gain_lut_hs[2], idxHD0, idxHD1, idxS0, idxS1,
                            wgtSH00, wgtSH01, wgtSH10, wgtSH11, wgtFixBitSH)

        # ---- 11. Dual-gain delta chain ----
        Ydel0 = dy * wy_hy
        Hdel0 = dh * wh_hy
        Sdel0 = ds * ws_hy
        Ydel1 = SHIFT_ROUND_S32(Ydel0, 9)
        Hdel1 = SHIFT_ROUND_S32(Hdel0, 9)
        Sdel1 = SHIFT_ROUND_S32(Sdel0, 9)

        Ydel2 = Ydel1 * wy_hs
        Hdel2 = Hdel1 * wh_hs
        Sdel2 = Sdel1 * ws_hs
        Ydel3 = SHIFT_ROUND_S32(Ydel2, 11)
        Hdel3 = SHIFT_ROUND_S32(Hdel2, 3)
        Sdel3 = SHIFT_ROUND_S32(Sdel2, 11 - RKVOP_PQ_ACM_CORDIC_S_BITS)

        # ---- 12. Zero delta when S == 0 ----
        Ydel = Ydel3
        Hdel = np.where(S == 0, 0, Hdel3)
        Sdel = np.where(S == 0, 0, Sdel3)

        # ---- 13. Apply result to Y / S / H ----
        YO = np.clip(Y + Ydel, 0, YUV_maxvalue)
        SO = np.clip(S + Sdel, 0, S_maxvalue << RKVOP_PQ_ACM_CORDIC_S_BITS)

        HO = H + Hdel
        pi_flag = (HO < -RKVOP_PQ_ACM_TANTABFIXTMP).astype(np.int32) - \
                  (HO >  RKVOP_PQ_ACM_TANTABFIXTMP).astype(np.int32)
        HO = HO + pi_flag * (2 * RKVOP_PQ_ACM_TANTABFIXTMP)

        # ---- 14. CORDIC: H/S → CB/CR → U/V ----
        CB, CR = cordic.cordic_hs2cbcr(HO, SO, 16,
                                        depth + RKVOP_PQ_ACM_CORDIC_S_BITS,
                                        depth, 13,
                                        6 - RKVOP_PQ_ACM_CORDIC_S_BITS)
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
        print("[ACM] created AcmImplSwVariant.")

    def do_acm_u8(self, planar_data, isRgb=False, use_cordic=None):
        if isRgb:
            return super().do_acm_u8(planar_data, isRgb=True)
        if use_cordic is None:
            use_cordic = self.use_cordic
        y = planar_data[0, :, :].astype(np.int32)
        cb = planar_data[1, :, :].astype(np.int32) - 128
        cr = planar_data[2, :, :].astype(np.int32) - 128
        s, h_deg, h_rad = self._cbcr_to_hs(cb, cr, depth_uv=8, use_cordic=use_cordic)
        return self._do_acm_yuv_variant(
            y, cb, cr, s, h_deg, h_rad, depth_uv=8, y_range=256, cbcr_center=128, use_cordic=use_cordic)

    def do_acm_u10(self, planar_data, isRgb=False, use_cordic=None):
        if isRgb:
            return super().do_acm_u10(planar_data, isRgb=True)
        if use_cordic is None:
            use_cordic = self.use_cordic
        y = planar_data[0, :, :].astype(np.int32)
        cb = planar_data[1, :, :].astype(np.int32) - 512
        cr = planar_data[2, :, :].astype(np.int32) - 512
        s, h_deg, h_rad = self._cbcr_to_hs(cb, cr, depth_uv=10, use_cordic=use_cordic)
        return self._do_acm_yuv_variant(
            y, cb, cr, s, h_deg, h_rad, depth_uv=10, y_range=1024, cbcr_center=512, use_cordic=use_cordic)

    def _do_acm_yuv_variant(self, y, cb, cr, s, h_deg, h_rad,
                            depth_uv, y_range, cbcr_center, use_cordic):
        """Variant ACM pipeline: gains applied late, delta_s multiplicative."""
        import cv2

        y_max = float(y_range - 1)
        s_max = 181.0 if depth_uv == 8 else 724.0
        h_max = 360.0
        dr_y, dr_s, dr_h = self.delta_range

        # ---- 1. Normalise inputs to [0, 1] ----
        y_f = y.astype(np.float32) / y_max
        s_f = s.astype(np.float32) / s_max
        h_f = ((h_deg + 180) % 360).astype(np.float32) / h_max

        # ---- 2. Normalise LUT tables (NO gain here — applied later) ----
        lut_dy = self.lut_delta_ybyh.astype(np.float32) / ACM_DELTA_Y_MAX * dr_y
        lut_ds = self.lut_delta_sbyh.astype(np.float32) / ACM_DELTA_S_MAX * dr_s
        lut_dh = self.lut_delta_hbyh.astype(np.float32) / ACM_DELTA_H_MAX * dr_h

        lut_g_yy = self.lut_gain_ybyy.astype(np.float32) / 127.0
        lut_g_ys = self.lut_gain_sbyy.astype(np.float32) / 127.0
        lut_g_yh = self.lut_gain_hbyy.astype(np.float32) / 127.0
        lut_g_sy = self.lut_gain_ybys.astype(np.float32) / 127.0
        lut_g_ss = self.lut_gain_sbys.astype(np.float32) / 127.0
        lut_g_sh = self.lut_gain_hbys.astype(np.float32) / 127.0

        # ---- 3. Compute remap indices ----
        idx_y = y_f * (self.len_y - 1)
        idx_s = s_f * (self.len_s - 1)
        idx_h = h_f * (self.len_h - 1)
        idx_hd = h_f * (self.len_hd - 1)
        idx_zeros = np.zeros_like(idx_h)

        # ---- 4. Sample delta tables ----
        delta_y = cv2.remap(lut_dy, idx_h, idx_zeros,
                            interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        delta_s = cv2.remap(lut_ds, idx_h, idx_zeros,
                            interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        delta_h = cv2.remap(lut_dh, idx_h, idx_zeros,
                            interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)

        # ---- 5. Sample gain tables ----
        gain_yy = cv2.remap(lut_g_yy, idx_y, idx_hd,
                            interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        gain_ys = cv2.remap(lut_g_ys, idx_y, idx_hd,
                            interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        gain_yh = cv2.remap(lut_g_yh, idx_y, idx_hd,
                            interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        gain_sy = cv2.remap(lut_g_sy, idx_s, idx_hd,
                            interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        gain_ss = cv2.remap(lut_g_ss, idx_s, idx_hd,
                            interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        gain_sh = cv2.remap(lut_g_sh, idx_s, idx_hd,
                            interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)

        # ---- 6. Combine deltas (apply global gains HERE instead of upfront) ----
        g_y = self.gain_y / 256.0
        g_s = self.gain_s / 256.0
        g_h = self.gain_h / 256.0
        delta_y = np.clip(delta_y * gain_yy * gain_sy * g_y, -dr_y, dr_y)
        delta_s = np.clip(delta_s * gain_ys * gain_ss * g_s, -dr_s, dr_s)
        delta_h = np.clip(delta_h * gain_yh * gain_sh * g_h, -dr_h, dr_h)

        # ---- 7. Apply to normalised values ----
        y_f = np.clip(y_f + delta_y, 0, 1.0)
        s_f = np.maximum(s_f * (1.0 + delta_s), 0.0)  # multiplicative delta_s

        # ---- 8. Convert back to integer pixel domain ----
        y_out = y_f * y_max
        s_pix = s_f * s_max

        if use_cordic:
            h_deg_new = (h_deg + delta_h) % 360.0
            h_deg_new = np.where(h_deg_new < 0, h_deg_new + 360.0, h_deg_new)
            cb, cr = cordic.cordic_hs2cbcr(h_deg_new, s_pix.astype(np.int32), 8, depth_uv, depth_uv, 13, 8)
        else:
            new_rad = h_rad + np.deg2rad(delta_h)
            new_cb = s_pix * np.cos(new_rad)
            new_cr = s_pix * np.sin(new_rad)
            cb = (new_cb + 0.5 * np.sign(new_cb)).astype(np.int32)
            cr = (new_cr + 0.5 * np.sign(new_cr)).astype(np.int32)

        out_dtype = np.uint8 if depth_uv == 8 else np.uint16
        y_clip = y_range - 1

        # ---- 9. Final clip ----
        y_out_f = y_out.astype(np.float64)
        cb_out_f = (cb + cbcr_center).astype(np.float64)
        cr_out_f = (cr + cbcr_center).astype(np.float64)

        if self.clip_type in ("soft_clip", "const_hue"):
            r_f, g_f, b_f = self._yuv_to_rgb_float(
                y_out_f, cb_out_f, cr_out_f, float(cbcr_center), float(y_max + 1))
            if self.clip_type == "soft_clip":
                r_f, g_f, b_f = self._clip_soft_rgb(r_f, g_f, b_f)
            else:
                r_f, g_f, b_f = self._clip_const_hue_rgb(r_f, g_f, b_f)
            y_out_f, cb_out_f, cr_out_f = self._rgb_to_yuv_float(
                r_f, g_f, b_f, float(cbcr_center), float(y_max + 1))

        yuv444p_out = np.empty((3, y.shape[0], y.shape[1]), dtype=out_dtype)
        yuv444p_out[0, :, :] = np.clip(y_out_f, 0, y_clip).astype(out_dtype)
        yuv444p_out[1, :, :] = np.clip(cb_out_f, 0, y_clip).astype(out_dtype)
        yuv444p_out[2, :, :] = np.clip(cr_out_f, 0, y_clip).astype(out_dtype)
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
            source_acm._default_lut_gain_ybyy, source_acm._default_len_hd, source_acm._default_len_y, kernel
        )
        self._default_lut_gain_sbyy = bicubic_resize_array_2d(
            source_acm._default_lut_gain_sbyy, source_acm._default_len_hd, source_acm._default_len_y, kernel
        )
        self._default_lut_gain_hbyy = bicubic_resize_array_2d(
            source_acm._default_lut_gain_hbyy, source_acm._default_len_hd, source_acm._default_len_y, kernel
        )

        # 2D gain LUTs (S axis)
        self._default_lut_gain_ybys = bicubic_resize_array_2d(
            source_acm._default_lut_gain_ybys, source_acm._default_len_hd, source_acm._default_len_s, kernel
        )
        self._default_lut_gain_sbys = bicubic_resize_array_2d(
            source_acm._default_lut_gain_sbys, source_acm._default_len_hd, source_acm._default_len_s, kernel
        )
        self._default_lut_gain_hbys = bicubic_resize_array_2d(
            source_acm._default_lut_gain_hbys, source_acm._default_len_hd, source_acm._default_len_s, kernel
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
        self.is_lut4rgb = source_acm.is_lut4rgb
        self.clip_type = source_acm.clip_type
        self.rand_seed = source_acm.rand_seed

        # Propagate default -> current
        self._resample_default_to_current(method="bicubic")
        self.b_lut_ready = True
        print("[ACM] Interpolation completed successfully.")
        return True


# ---------------------------------------------------------------------------
# private helper for AcmImplSwVariant.interpolate_from
# ---------------------------------------------------------------------------
def _resize_2d_lut(
    src_lut: np.ndarray, src_h2: int, src_dim: int, dst_h2: int, dst_dim: int, kernel: np.ndarray
) -> np.ndarray:
    """Resize a 2D LUT from (src_h2, src_dim) to (dst_h2, dst_dim) in two passes."""
    if src_lut.shape == (dst_h2, dst_dim):
        return src_lut.copy()

    if src_h2 != dst_h2:
        tmp = np.zeros((dst_h2, src_dim), dtype=src_lut.dtype)
        for i in range(src_dim):
            tmp[:, i] = linear_resize_array_1d(src_lut[:, i], dst_h2)
    else:
        tmp = src_lut.copy()

    if src_dim != dst_dim:
        result = np.zeros((dst_h2, dst_dim), dtype=src_lut.dtype)
        for i in range(dst_h2):
            result[i, :] = linear_resize_array_1d(tmp[i, :], dst_dim)
        return result
    return tmp


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
        "G:/Codes/gerrit_projects/hwpq_verify/data/vdpp_vop_config_3576.json" if args.config == "" else args.config
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
    acm.dump_lut(DEF_OUT_DIR)
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
