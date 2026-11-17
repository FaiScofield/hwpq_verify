"""
Copyright   : Copyright (c) 2026 by Rockchip. All right reserved.
FilePath    : acm_impls.py
Author      : vance.wu@rock-chips.com
Date        : 2026-06-14
Description : Concrete ACM implementation subclasses.

    * AcmImplHwRk       - hardware ACM, 4 LUTs at (9, 13, 65, 17)
    * AcmImplHwRkLite   - ACM_LITE HSV, coarse/fine hue partition (default 12+20 intervals)
    * AcmImplSwRk       - software ACM matching RK semantics, (9, 13, 65, 65)
    * AcmImplSwEvideo   - evideo ACM, (9, 13, 65, 65) with wider delta range
    * AcmImplSwVariant  - any (y, s, h, h2) with h2 <= h
LastEditTime: 2026-06-14
"""

import os
import sys
import json
import argparse
import numpy as np
from typing import Optional

if __package__:
    from .acm_impl_base import (
        AcmImplBase,
        ACM_DELTA_Y_MIN,
        ACM_DELTA_Y_MAX,
        ACM_DELTA_S_MIN,
        ACM_DELTA_S_MAX,
        ACM_DELTA_H_MIN,
        ACM_DELTA_H_MAX,
        ACM_LEN_H_MAX,
        ACM_LEN_H_MIN,
        ACM_HSV_GRAY_THRESHOLD_S,
        linear_resize_array_1d,
        linear_resize_array_2d,
        bicubic_resize_array_1d,
        bicubic_resize_array_2d,
    )
    from ..bcsh.hsv_adjust import rgb_to_hsv, hsv_to_rgb
    from ..csc.get_csc_coefs import g_y2r_mat_bt709, g_r2y_mat_bt709
    from . import cordic
    from .. import utils as utl
else:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    from acm_impl_base import (
        AcmImplBase,
        ACM_DELTA_Y_MIN,
        ACM_DELTA_Y_MAX,
        ACM_DELTA_S_MIN,
        ACM_DELTA_S_MAX,
        ACM_DELTA_H_MIN,
        ACM_DELTA_H_MAX,
        ACM_LEN_H_MAX,
        ACM_LEN_H_MIN,
        ACM_HSV_GRAY_THRESHOLD_S,
        linear_resize_array_1d,
        linear_resize_array_2d,
        bicubic_resize_array_1d,
        bicubic_resize_array_2d,
    )
    from bcsh.hsv_adjust import rgb_to_hsv, hsv_to_rgb
    from csc.get_csc_coefs import g_y2r_mat_bt709, g_r2y_mat_bt709
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
# AcmImplHwRkLite
# ---------------------------------------------------------------------------
class AcmImplHwRkLite(AcmImplBase):
    """RK ACM_LITE HSV color adjustment with a coarse/fine hue partition.

    Processing domain is RGB/HSV: YUV input is converted to RGB first (its
    out-of-gamut handling follows ``clip_type``), then to HSV for H/V/S
    adjustment, and converted back to YUV at the end. The 1D delta LUTs
    (dH/dS/dV by H) use a two-segment hue partition:

      * fine segment   [0, 60) with ``n_fine`` intervals
      * coarse segment [60, 360) with ``n_coarse`` intervals

    The table is point based: index 0 is 0 deg and the last point duplicates
    360 deg (= 0 deg), so hardware can interpolate the closing segment
    without address wrapping. ``len_h = n_fine + n_coarse + 1``.

    The 2D gain LUTs keep the legacy 17-point hue axis (``len_hd``) and are
    sampled uniformly starting from 0 deg. ``GainV_byV``, ``GainS_byV``,
    ``GainS_byS`` and ``GainV_byS`` are all sampled; ``GainH_byV`` and
    ``GainH_byS`` are ignored (their tables stay at the identity value for
    config compatibility).

    Global gains are applied at the last stage and are not clamped after
    application; the register range [0, 1023] maps to [0, 4] with 256 = 1.0x.

    Gain tables use the same convention as the legacy paths,
    ``gain = raw / 127`` (raw 127 = 1.0x), so gain data can be copied between
    algorithms without any neutral-value conversion. Gain tables scale the
    delta increments, so a zero delta table always leaves the image unchanged.
    """

    HUE_START_DEG = 0.0
    HUE_FINE_SPAN_DEG = 60.0
    HUE_COARSE_SPAN_DEG = 300.0

    # Raw full-scale code ranges of the Lite delta tables. The normalisation
    # denominator is ``RAW_RANGE / delta_range``, so one raw code maps to
    # ``delta_range / RAW_RANGE`` in physical units. With the default
    # delta_range this yields 1 deg per raw for H, 1/1023 for Y and 1/63 for
    # the multiplicative S gain.
    DELTA_H_RAW_RANGE = 63.0
    DELTA_Y_RAW_RANGE = 127.0
    DELTA_S_RAW_RANGE = 63.0

    # 2D gain table names kept by the base class; the Lite path samples the
    # first four and leaves the deleted ones untouched.
    LITE_GAIN_LUTS = ("gain_ybyy", "gain_sbyy", "gain_sbys", "gain_ybys")
    REMOVED_GAIN_LUTS = ("gain_hbyy", "gain_hbys")

    def __init__(
        self,
        len_y: int = 9,
        len_s: int = 8,
        n_coarse: int = 20,
        n_fine: int = 12,
        len_h2: int = 17,
        delta_range: tuple = (0.124, 1.0, 63),
        use_cordic: bool = True,
        limited_range: bool = False,
        chroma_protect: float = ACM_HSV_GRAY_THRESHOLD_S,
    ):
        n_coarse = int(n_coarse)
        n_fine = int(n_fine)
        # Point-based table: the last point duplicates 360 deg (0 deg).
        len_h = n_coarse + n_fine + 1
        if n_coarse < 1 or n_fine < 1:
            raise ValueError(f"n_coarse/n_fine must be >= 1, got ({n_coarse}, {n_fine})")
        if not (ACM_LEN_H_MIN <= len_h <= ACM_LEN_H_MAX):
            raise ValueError(f"n_coarse + n_fine + 1 must be in [{ACM_LEN_H_MIN}, {ACM_LEN_H_MAX}], got {len_h}")
        if int(len_h2) > 0 and len_h < int(len_h2):
            raise ValueError(f"len_h ({len_h}) must be >= len_hd ({len_h2})")

        super().__init__(
            len_y=len_y,
            len_s=len_s,
            len_h=len_h,
            len_hd=len_h2,
            delta_range=delta_range,
            use_cordic=use_cordic,
        )
        self.name = "AcmImplHwRkLite"
        self.n_coarse = n_coarse
        self.n_fine = n_fine
        self.is_lut4rgb = True
        self.limited_range = bool(limited_range)
        self.chroma_protect = float(np.clip(chroma_protect, 0.0, 1.0))
        self._init_lite_gain_luts()
        print(
            f"[ACM] created AcmImplHwRkLite: fine={n_fine}, coarse={n_coarse}, "
            f"len_h={len_h}, gain hue axis={self.len_hd}, clip type={self.clip_type}"
        )

    # ------------------------------------------------------------------
    # Lite configuration helpers
    # ------------------------------------------------------------------
    def _init_lite_gain_luts(self) -> None:
        """Reset Lite gain LUTs to the identity gain value.

        Lite uses the same ``gain = raw / 127`` convention as the legacy
        paths, so 127 means 1.0x. The tables are set explicitly here to keep
        the Lite identity independent of the base-class defaults.
        """
        for name in self.LITE_GAIN_LUTS + self.REMOVED_GAIN_LUTS:
            for attr in (f"lut_{name}", f"_default_lut_{name}"):
                if hasattr(self, attr):
                    getattr(self, attr)[...] = 127

    def set_hue_partition(self, n_coarse: int, n_fine: int, kernel: np.ndarray = None) -> None:
        """Change the coarse/fine hue partition with hue-aware resampling.

        ``n_coarse`` / ``n_fine`` count intervals over [60, 360) and [0, 60)
        respectively. The table is point based, so ``len_h = n_coarse +
        n_fine + 1`` and the last point duplicates 360 deg. The current 1D
        delta LUTs are resampled by hue angle (not by array index) so that
        switching between partitions preserves the tuning curve. The resampled
        tables also become the new default set, so later ``set_len`` calls use
        the new partition as the canonical reference.
        """
        n_coarse = int(n_coarse)
        n_fine = int(n_fine)
        if n_coarse < 1 or n_fine < 1:
            raise ValueError(f"n_coarse/n_fine must be >= 1, got ({n_coarse}, {n_fine})")
        total = n_coarse + n_fine + 1
        if not (ACM_LEN_H_MIN <= total <= ACM_LEN_H_MAX):
            raise ValueError(f"n_coarse + n_fine + 1 must be in [{ACM_LEN_H_MIN}, {ACM_LEN_H_MAX}], got {total}")
        if total < self.len_hd:
            raise ValueError(f"len_h ({total}) must be >= len_hd ({self.len_hd})")

        old_n_coarse, old_n_fine = self.n_coarse, self.n_fine
        old_luts = (
            self.lut_delta_ybyh.copy(),
            self.lut_delta_sbyh.copy(),
            self.lut_delta_hbyh.copy(),
        )

        self.n_coarse = n_coarse
        self.n_fine = n_fine
        self.set_len(self.len_y, self.len_s, total, self.len_hd, kernel)

        old_total = old_n_coarse + old_n_fine + 1
        if len(old_luts[0]) != old_total:
            print(
                f"[ACM] hue partition resample skipped: current len_h({len(old_luts[0])}) "
                f"!= old partition({old_total})"
            )
            return

        old_angles = self._hue_grid(old_n_coarse, old_n_fine)
        new_angles = self._hue_grid(n_coarse, n_fine)
        new_y = self._circular_resample(old_angles, new_angles, old_luts[0])
        new_s = self._circular_resample(old_angles, new_angles, old_luts[1])
        new_h = self._circular_resample(old_angles, new_angles, old_luts[2])

        self._default_lut_delta_ybyh = np.clip(
            np.rint(new_y), ACM_DELTA_Y_MIN, ACM_DELTA_Y_MAX
        ).astype(np.int16)
        self._default_lut_delta_sbyh = np.clip(
            np.rint(new_s), ACM_DELTA_S_MIN, ACM_DELTA_S_MAX
        ).astype(np.int16)
        self._default_lut_delta_hbyh = np.clip(
            np.rint(new_h), ACM_DELTA_H_MIN, ACM_DELTA_H_MAX
        ).astype(np.int16)
        self._default_len_h = total
        self.lut_delta_ybyh = self._default_lut_delta_ybyh.copy()
        self.lut_delta_sbyh = self._default_lut_delta_sbyh.copy()
        self.lut_delta_hbyh = self._default_lut_delta_hbyh.copy()
        self._sync_hue_closure()
        print(f"[ACM] hue partition changed to fine={n_fine}, coarse={n_coarse} (len_h={total})")

    def _sync_hue_closure(self) -> None:
        """Force the last hue-table point to equal index 0 (closed table).

        The 1D tables are point based with the final point at 360 deg, so the
        closing point must mirror index 0 for hardware interpolation. Both the
        running and the default tables are kept closed.
        """
        for name in ("delta_ybyh", "delta_sbyh", "delta_hbyh"):
            lut = getattr(self, f"lut_{name}", None)
            if lut is not None and lut.size > 1:
                lut[-1] = lut[0]
            default = getattr(self, f"_default_lut_{name}", None)
            if default is not None and default.size > 1:
                default[-1] = default[0]

    def _sync_hue_partition_from_len(self) -> None:
        """Keep n_coarse/n_fine consistent when len_h changes externally."""
        total = int(self.len_h)
        if getattr(self, "n_coarse", 0) + getattr(self, "n_fine", 0) + 1 == total:
            return
        intervals = max(2, total - 1)
        # Keep the documented fine-segment share (12 / 32 ~= 0.375).
        self.n_fine = max(1, int(round(intervals * 0.375)))
        self.n_coarse = intervals - self.n_fine
        print(f"[ACM] hue partition re-split to fine={self.n_fine}, coarse={self.n_coarse}")

    def _promote_current_to_default(self) -> None:
        """Promote the current tables/lengths to the canonical default set."""
        self._default_len_y = self.len_y
        self._default_len_s = self.len_s
        self._default_len_h = self.len_h
        self._default_len_hd = self.len_hd
        self._default_lut_delta_ybyh = self.lut_delta_ybyh.copy()
        self._default_lut_delta_sbyh = self.lut_delta_sbyh.copy()
        self._default_lut_delta_hbyh = self.lut_delta_hbyh.copy()
        for name in self.LITE_GAIN_LUTS + self.REMOVED_GAIN_LUTS:
            setattr(self, f"_default_lut_{name}", getattr(self, f"lut_{name}").copy())

    def set_len(self, len_y: int, len_s: int, len_h: int, len_hd: int = 0, kernel: np.ndarray = None) -> None:
        """Set LUT lengths; len_h is re-split when the partition changes."""
        if int(len_hd) > 0 and int(len_h) < int(len_hd):
            raise ValueError(f"len_h ({len_h}) must be >= len_hd ({len_hd})")
        super().set_len(len_y, len_s, len_h, len_hd, kernel)
        self._sync_hue_partition_from_len()
        self._promote_current_to_default()
        self._sync_hue_closure()

    def set_step(
        self, step_y: float, step_s: float, step_h: float, step_h2: float = 0.0, kernel: np.ndarray = None
    ) -> None:
        """Set LUT steps; keep the coarse/fine partition consistent."""
        super().set_step(step_y, step_s, step_h, step_h2, kernel)
        self._sync_hue_partition_from_len()
        self._promote_current_to_default()
        self._sync_hue_closure()

    def set_global_gains(self, gain_y: int, gain_s: int, gain_h: int) -> None:
        """Set global gains in [0, 1023] (256 = 1.0x, 1023 ~= 4.0x)."""
        super().set_global_gains(
            int(np.clip(gain_y, 0, 1023)),
            int(np.clip(gain_s, 0, 1023)),
            int(np.clip(gain_h, 0, 1023)),
        )

    def set_limited_range(self, limited: bool) -> None:
        """Select limited-range (True) or full-range (False) YUV I/O."""
        self.limited_range = bool(limited)
        print(f"[ACM] set limited range: {self.limited_range}")

    # ------------------------------------------------------------------
    # Config persistence
    # ------------------------------------------------------------------
    def dump_json(self, filename: str = "") -> bool:
        """Write the Lite config including the hue partition and HSV options."""
        if not filename:
            super().dump_json("")
            return True
        ok = super().dump_json(filename)
        if not ok:
            return False
        try:
            with open(filename, "r") as f:
                data = json.load(f)
            acm = data.get("pq_tuning_param", {}).get("acm", data)
            acm["acmLite"] = 1
            acm["acmHuePartitionCoarse"] = int(self.n_coarse)
            acm["acmHuePartitionFine"] = int(self.n_fine)
            acm["acmLimitedRange"] = int(bool(self.limited_range))
            acm["acmChromaProtect"] = float(self.chroma_protect)
            with open(filename, "w") as f:
                json.dump(data, f, indent=4, ensure_ascii=False, cls=utl.CompactArrayEncoder)
            return True
        except Exception as exc:
            print(f"[ACM] dump Lite config failed: {exc}")
            return False

    def load_json(self, filename: str) -> bool:
        """Load a config and restore the Lite hue partition and HSV options."""
        if not os.path.exists(filename) or not filename.endswith(".json"):
            return super().load_json(filename)

        try:
            with open(filename, "r") as f:
                raw = json.load(f)
            acm_data = raw.get("pq_tuning_param", {}).get("acm", raw.get("acm", raw))
        except Exception:
            return super().load_json(filename)

        is_lite = bool(acm_data.get("acmLite", 0))
        total = max(
            ACM_LEN_H_MIN,
            min(ACM_LEN_H_MAX, int(acm_data.get("lutLengthH", self.n_coarse + self.n_fine + 1))),
        )
        n_coarse = self.n_coarse
        n_fine = self.n_fine
        if is_lite:
            n_coarse = int(acm_data.get("acmHuePartitionCoarse", -1))
            n_fine = int(acm_data.get("acmHuePartitionFine", -1))
            if n_coarse < 1 or n_fine < 1 or n_coarse + n_fine + 1 != total:
                # Missing or legacy partition: fall back to the default ratio.
                intervals = max(2, total - 1)
                n_fine = max(1, int(round(intervals * 0.375)))
                n_coarse = intervals - n_fine
            # Align canonical lengths with the file so the base loader does
            # not resample the 1D delta LUTs by array index.
            self.n_coarse, self.n_fine = n_coarse, n_fine
            self._default_len_h = total
            self._default_len_y = int(acm_data.get("lutLengthY", self._default_len_y))
            self._default_len_s = int(acm_data.get("lutLengthS", self._default_len_s))
            self._default_len_hd = min(int(acm_data.get("lutLengthHD", self._default_len_hd)), total)
            self.len_y = self._default_len_y
            self.len_s = self._default_len_s
            self.len_h = total
            self.len_hd = self._default_len_hd

        ok = super().load_json(filename)
        if not ok:
            return False

        if is_lite:
            self.limited_range = bool(acm_data.get("acmLimitedRange", 0))
            self.chroma_protect = float(
                np.clip(acm_data.get("acmChromaProtect", self.chroma_protect), 0.0, 1.0)
            )
            self.n_coarse, self.n_fine = n_coarse, n_fine
            self._default_len_h = total
        else:
            # Legacy config: keep the Lite table closed with the default split.
            total = int(self.len_h)
            intervals = max(2, total - 1)
            self.n_fine = max(1, int(round(intervals * 0.375)))
            self.n_coarse = intervals - self.n_fine
            self._default_len_h = total

        self._sync_hue_closure()

        # Removed gain tables are not used by the Lite path; keep them at the
        # identity gain so the UI shows neutral data.
        for name in self.REMOVED_GAIN_LUTS:
            for attr in (f"lut_{name}", f"_default_lut_{name}"):
                if hasattr(self, attr):
                    getattr(self, attr)[...] = 127
        self.b_lut_ready = True
        print(f"[ACM] loaded Lite config: fine={self.n_fine}, coarse={self.n_coarse}, len_h={self.len_h}")
        return True

    # ------------------------------------------------------------------
    # Public processing entry
    # ------------------------------------------------------------------
    def do_acm_u8(self, planar_data: np.ndarray, isRgb: bool = False, use_cordic: Optional[bool] = None) -> np.ndarray:
        """Apply ACM_LITE HSV to an 8-bit RGB or YUV444 planar image."""
        if isRgb:
            return self._do_acm_rgb_lite(planar_data, rng=256)
        return self._do_acm_yuv_lite(planar_data, depth=8)

    def do_acm_u10(self, planar_data: np.ndarray, isRgb: bool = False, use_cordic: Optional[bool] = None) -> np.ndarray:
        """Apply ACM_LITE HSV to a 10-bit RGB or YUV444 planar image."""
        if isRgb:
            return self._do_acm_rgb_lite(planar_data, rng=1024)
        return self._do_acm_yuv_lite(planar_data, depth=10)

    # ------------------------------------------------------------------
    # Domain conversion
    # ------------------------------------------------------------------
    def _do_acm_rgb_lite(self, planar_data: np.ndarray, rng: int) -> np.ndarray:
        """Apply the HSV pipeline to a full-range [H, W, 3] RGB image."""
        if planar_data.ndim != 3 or planar_data.shape[2] != 3:
            raise ValueError(f"RGB input must be [H, W, 3], got {planar_data.shape}")
        scale = float(rng - 1)
        rgb_f = np.clip(planar_data.astype(np.float32) / scale, 0.0, 1.0)
        rgb_out = self._do_hsv_lite(rgb_f)
        out = np.clip(np.rint(rgb_out * scale), 0.0, scale).astype(planar_data.dtype)
        return out.transpose(2, 0, 1)

    def _do_acm_yuv_lite(self, planar_data: np.ndarray, depth: int) -> np.ndarray:
        """Apply the HSV pipeline to a YUV444 planar image."""
        if planar_data.ndim != 3 or planar_data.shape[0] != 3:
            raise ValueError(f"YUV input must be [3, H, W], got {planar_data.shape}")
        rgb_f = self._yuv444_to_rgb(planar_data, depth)
        rgb_out = self._do_hsv_lite(rgb_f)
        return self._rgb_to_yuv444(rgb_out, depth, planar_data.dtype)

    def _yuv444_to_rgb(self, planar_data: np.ndarray, depth: int) -> np.ndarray:
        """Convert YUV444 planar to [H, W, 3] RGB in [0, 1] using BT.709.

        In limited-range mode, Y is expanded from [16, 235] (8-bit) or
        [64, 940] (10-bit), and Cb/Cr from [16, 240] or [64, 960].
        Out-of-gamut values are handled by the configured hue-preserve mode.
        """
        if depth not in (8, 10):
            raise ValueError(f"depth must be 8 or 10, got {depth}")
        max_v = 1023.0 if depth == 10 else 255.0
        y = planar_data[0].astype(np.float32)
        cb = planar_data[1].astype(np.float32)
        cr = planar_data[2].astype(np.float32)

        if self.limited_range:
            if depth == 10:
                y_off, y_scale, c_center, c_scale = 64.0, 876.0, 512.0, 896.0
            else:
                y_off, y_scale, c_center, c_scale = 16.0, 219.0, 128.0, 224.0
            y = (y - y_off) / y_scale
            cb = (cb - c_center) / c_scale
            cr = (cr - c_center) / c_scale
        else:
            c_center = (max_v + 1.0) * 0.5
            y = y / max_v
            cb = (cb - c_center) / max_v
            cr = (cr - c_center) / max_v

        ycbcr = np.stack([y, cb, cr], axis=-1)
        rgb = ycbcr @ g_y2r_mat_bt709.T
        return self._apply_hue_preserve(rgb)

    def _rgb_to_yuv444(self, rgb: np.ndarray, depth: int, dtype: np.dtype) -> np.ndarray:
        """Convert [H, W, 3] RGB in [0, 1] back to YUV444 planar using BT.709."""
        if depth not in (8, 10):
            raise ValueError(f"depth must be 8 or 10, got {depth}")
        max_v = 1023.0 if depth == 10 else 255.0
        yuv = np.clip(rgb, 0.0, 1.0) @ g_r2y_mat_bt709.T
        y = yuv[..., 0]
        cb = yuv[..., 1]
        cr = yuv[..., 2]

        if self.limited_range:
            if depth == 10:
                y_off, y_scale, c_center, c_scale = 64.0, 876.0, 512.0, 896.0
            else:
                y_off, y_scale, c_center, c_scale = 16.0, 219.0, 128.0, 224.0
            out_y = y_off + y_scale * y
            out_cb = c_center + c_scale * cb
            out_cr = c_center + c_scale * cr
        else:
            c_center = (max_v + 1.0) * 0.5
            out_y = y * max_v
            out_cb = cb * max_v + c_center
            out_cr = cr * max_v + c_center

        out = np.empty((3,) + y.shape, dtype=dtype)
        out[0] = np.clip(np.rint(out_y), 0.0, max_v).astype(dtype)
        out[1] = np.clip(np.rint(out_cb), 0.0, max_v).astype(dtype)
        out[2] = np.clip(np.rint(out_cr), 0.0, max_v).astype(dtype)
        return out

    def _apply_hue_preserve(self, rgb: np.ndarray) -> np.ndarray:
        """Handle out-of-gamut RGB produced by YUV->RGB conversion.

        The behavior follows ``clip_type`` so the Lite path reuses the shared
        Clip Type control: ``easy_clip`` clips per channel, ``radial_clip``
        scales all channels uniformly towards black and ``luma_clip`` keeps the
        channel ratio (constant hue).
        """
        clip_type = self.clip_type
        if clip_type == "radial_clip":
            return self._scale_clip(rgb)
        if clip_type == "luma_clip":
            return self._soft_clip_constant_hue(rgb)
        return np.clip(rgb, 0.0, 1.0)

    def apply_hue_preserve(self, rgb: np.ndarray) -> np.ndarray:
        """Public wrapper for the YUV->RGB gamut mapping selected by clip_type."""
        return self._apply_hue_preserve(rgb)

    @staticmethod
    def _soft_clip_constant_hue(rgb: np.ndarray) -> np.ndarray:
        """Map out-of-gamut RGB back while preserving the channel ratio.

        The max channel is clipped to 1.0 and the min channel to 0.0; the
        middle channel is linearly interpolated so that
        ``(mid - min) / (max - min)`` is preserved, which keeps hue constant.
        """
        eps = 1e-6
        flat = rgb.reshape(-1, 3)
        order = np.argsort(flat, axis=-1)
        sorted_rgb = np.take_along_axis(flat, order, axis=-1)
        mn = sorted_rgb[:, 0]
        md = sorted_rgb[:, 1]
        mx = sorted_rgb[:, 2]

        mn2 = np.clip(mn, 0.0, 1.0)
        mx2 = np.clip(mx, 0.0, 1.0)
        chroma = mx - mn
        md2 = np.where(
            chroma > eps,
            mn2 + (mx2 - mn2) * (md - mn) / np.maximum(chroma, eps),
            mn2,
        )
        out_sorted = np.stack([mn2, md2, mx2], axis=-1).astype(np.float32)
        out_flat = np.empty_like(flat)
        np.put_along_axis(out_flat, order, out_sorted, axis=-1)
        out = out_flat.reshape(rgb.shape)
        need_map = ((mx > 1.0) | (mn < 0.0)).reshape(rgb.shape[:-1] + (1,))
        return np.where(need_map, out, rgb)

    @staticmethod
    def _scale_clip(rgb: np.ndarray) -> np.ndarray:
        """Scale RGB uniformly so that the max channel fits [0, 1].

        Uniform scaling preserves hue and saturation; negative values are
        clipped to zero because scaling alone cannot move them into range.
        """
        mx = np.max(rgb, axis=-1, keepdims=True)
        scale = np.where(mx > 1.0, 1.0 / np.maximum(mx, 1e-6), 1.0)
        return np.clip(rgb * scale, 0.0, 1.0)

    # ------------------------------------------------------------------
    # HSV core
    # ------------------------------------------------------------------
    def _do_hsv_lite(self, rgb: np.ndarray) -> np.ndarray:
        """Core HSV adjustment on a full-range [H, W, 3] RGB image."""
        # ---- 1. RGB -> HSV (hexagon model, h in [0, 360)) ----
        h, s, v = rgb_to_hsv(rgb)

        # ---- 2. Neutral protection weight based on chroma C = V * S ----
        chroma = v * s
        chroma_protect = float(np.clip(self.chroma_protect, 0.0, 1.0))
        if chroma_protect > 0.0:
            w = np.clip(chroma / chroma_protect, 0.0, 1.0)
            w = w * w * (3.0 - 2.0 * w)
        else:
            w = np.ones_like(chroma)

        # ---- 3. Coarse/fine hue position for the 1D delta LUTs ----
        i0, i1, fh = self._hue_pos_coarse_fine(h)

        # ---- 4. Sample 1D delta LUTs ----
        dh_raw = self._sample_1d(self.lut_delta_hbyh, i0, i1, fh)
        ds_raw = self._sample_1d(self.lut_delta_sbyh, i0, i1, fh)
        dv_raw = self._sample_1d(self.lut_delta_ybyh, i0, i1, fh)

        # Normalisation: raw code / (RAW_RANGE / delta_range). The raw
        # full-scale stays fixed, so changing delta_range only moves the
        # normalisation denominator.
        dr_y, dr_s, dr_h = self.delta_range
        dh_base = dh_raw * float(dr_h) / self.DELTA_H_RAW_RANGE
        ds_gain = 1.0 + ds_raw * float(dr_s) / self.DELTA_S_RAW_RANGE
        dv_base = dv_raw * float(dr_y) / self.DELTA_Y_RAW_RANGE

        # ---- 5. Uniform hue position for the 2D gain LUTs ----
        j0, j1, fj = self._hue_pos_uniform(h, self.len_hd)

        # ---- 6. Sample the retained 2D gain LUTs ----
        if self.ignore_gain_luts:
            gain_vv = np.ones_like(dh_base)
            gain_sv = np.ones_like(dh_base)
            gain_ss = np.ones_like(dh_base)
            gain_vs = np.ones_like(dh_base)
        else:
            gain_vv = self._sample_gain_2d(self.lut_gain_ybyy, j0, j1, fj, v) / 127.0
            gain_sv = self._sample_gain_2d(self.lut_gain_sbyy, j0, j1, fj, v) / 127.0
            gain_ss = self._sample_gain_2d(self.lut_gain_sbys, j0, j1, fj, s) / 127.0
            gain_vs = self._sample_gain_2d(self.lut_gain_ybys, j0, j1, fj, s) / 127.0

        # ---- 7. Cache intermediates for UI/debug (legacy key names) ----
        self._last_delta_y_raw = dv_base.copy()
        self._last_delta_s_raw = (ds_gain - 1.0).copy()
        self._last_delta_h_raw = dh_base.copy()
        self._last_gain_yy = gain_vv.copy()
        self._last_gain_ys = gain_vs.copy()
        self._last_gain_sy = gain_sv.copy()
        self._last_gain_ss = gain_ss.copy()
        self._last_gain_hy = np.ones_like(gain_vv)
        self._last_gain_hs = np.ones_like(gain_vv)
        self._last_intermediate_shape = h.shape

        # ---- 8. Global gains last; no clamp after gain ----
        # The S delta stays a delta: gain tables scale the delta increment, so
        # a zero delta table always leaves S untouched regardless of gain.
        g_v = float(np.clip(self.gain_y, 0, 1023)) / 256.0
        g_s = float(np.clip(self.gain_s, 0, 1023)) / 256.0
        g_h = float(np.clip(self.gain_h, 0, 1023)) / 256.0
        dh = dh_base * g_h
        ds = 1.0 + (ds_gain - 1.0) * gain_sv * gain_ss * g_s
        dv = dv_base * gain_vv * gain_vs * g_v

        self._final_delta_y = (dv * w).copy()
        self._final_delta_s = ((ds - 1.0) * w).copy()
        self._final_delta_h = (dh * w).copy()

        # ---- 9. Apply in H -> V -> S order ----
        # The chroma weight gates V as well, so neutral (white/gray) backgrounds
        # keep their luminance. This mirrors the legacy HSV paths, which bypass
        # the LUTs entirely for gray pixels.
        h_new = np.mod(h + dh * w, 360.0)
        v_new = np.clip(v + dv * w, 0.0, 1.0)
        s_new = np.clip(s * (1.0 + (ds - 1.0) * w), 0.0, 1.0)

        # ---- 10. HSV -> RGB, always in gamut by construction ----
        rgb_out = hsv_to_rgb(np.stack([h_new, s_new, v_new], axis=-1))
        return np.clip(rgb_out, 0.0, 1.0)

    # ------------------------------------------------------------------
    # LUT sampling helpers
    # ------------------------------------------------------------------
    def _hue_grid(self, n_coarse: int, n_fine: int) -> np.ndarray:
        """Return hue angles in degrees for the point-based hue table.

        Index 0 is 0 deg. The fine segment [0, 60) uses ``n_fine`` intervals,
        the coarse segment [60, 360) uses ``n_coarse`` intervals, and the last
        point duplicates 360 deg (same value as index 0). The returned length
        is ``n_fine + n_coarse + 1``.
        """
        fine = np.linspace(
            0.0, self.HUE_FINE_SPAN_DEG, n_fine + 1, dtype=np.float32)
        coarse = np.linspace(
            self.HUE_FINE_SPAN_DEG,
            self.HUE_FINE_SPAN_DEG + self.HUE_COARSE_SPAN_DEG,
            n_coarse + 1,
            dtype=np.float32,
        )[1:]
        return np.concatenate([fine, coarse])

    @staticmethod
    def _circular_resample(
        old_angles: np.ndarray, new_angles: np.ndarray, old_values: np.ndarray
    ) -> np.ndarray:
        """Resample 1D LUT values by hue angle on a closed 0..360 grid.

        Both angle arrays are expected to be the output of :meth:`_hue_grid`:
        monotonically increasing from 0 to 360 deg with the last value
        mirroring the first one.
        """
        angles = np.asarray(old_angles, dtype=np.float32)
        values = np.asarray(old_values, dtype=np.float32)
        new = np.clip(np.asarray(new_angles, dtype=np.float32), 0.0, 360.0)
        return np.interp(new, angles, values).astype(np.float32)

    def _hue_pos_coarse_fine(self, h_deg: np.ndarray):
        """Map hue to a fractional index in the point-based hue table.

        Index 0 is 0 deg, ``n_fine`` intervals cover [0, 60) and ``n_coarse``
        intervals cover [60, 360). The last point duplicates 360 deg, so the
        closing segment interpolates against it without address wrapping.
        """
        n_coarse = self.n_coarse
        n_fine = self.n_fine
        n_hue = n_coarse + n_fine + 1

        h = np.mod(h_deg, 360.0)
        is_fine = h < self.HUE_FINE_SPAN_DEG
        u_fine = h / self.HUE_FINE_SPAN_DEG * n_fine
        u_coarse = n_fine + (h - self.HUE_FINE_SPAN_DEG) / self.HUE_COARSE_SPAN_DEG * n_coarse
        u = np.where(is_fine, u_fine, u_coarse)

        i0 = np.clip(np.floor(u).astype(np.int32), 0, n_hue - 2)
        i1 = i0 + 1
        f = np.clip(u - i0, 0.0, 1.0).astype(np.float32)
        return i0, i1, f

    def _hue_pos_uniform(self, h_deg: np.ndarray, n_hue: int):
        """Map hue to a fractional index in a uniform 2D-gain hue axis.

        The axis starts at 0 deg and has ``n_hue`` points over 360 deg, with
        the last point duplicating the first one for linear interpolation.
        """
        hp = np.mod(h_deg - self.HUE_START_DEG, 360.0)
        u = hp / 360.0 * (n_hue - 1)
        i0 = np.clip(np.floor(u).astype(np.int32), 0, n_hue - 1)
        i1 = np.minimum(i0 + 1, n_hue - 1)
        f = (u - i0).astype(np.float32)
        return i0, i1, f

    @staticmethod
    def _sample_1d(lut: np.ndarray, i0: np.ndarray, i1: np.ndarray, f: np.ndarray) -> np.ndarray:
        """Linear interpolation on a closed point-based 1D LUT."""
        return lut[i0].astype(np.float32) * (1.0 - f) + lut[i1].astype(np.float32) * f

    @staticmethod
    def _sample_gain_2d(
        lut: np.ndarray, j0: np.ndarray, j1: np.ndarray, fj: np.ndarray, axis_val: np.ndarray
    ) -> np.ndarray:
        """Bilinear interpolation on a [axis, hue] gain LUT.

        ``axis_val`` is V or S in [0, 1]; the hue axis uses j0/j1/fj.
        """
        n_axis = lut.shape[0]
        u = np.clip(axis_val, 0.0, 1.0).astype(np.float32) * (n_axis - 1)
        k0 = np.floor(u).astype(np.int32)
        k1 = np.minimum(k0 + 1, n_axis - 1)
        fk = u - k0

        v00 = lut[k0, j0].astype(np.float32)
        v01 = lut[k0, j1].astype(np.float32)
        v10 = lut[k1, j0].astype(np.float32)
        v11 = lut[k1, j1].astype(np.float32)
        top = v00 * (1.0 - fj) + v01 * fj
        bot = v10 * (1.0 - fj) + v11 * fj
        return top * (1.0 - fk) + bot * fk


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
        self._final_delta_y = delta_y.copy()
        self._final_delta_s = delta_s.copy()
        self._final_delta_h = delta_h.copy()

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
        self._final_delta_y = delta_y.copy()
        self._final_delta_s = delta_s.copy()
        self._final_delta_h = delta_h.copy()

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
