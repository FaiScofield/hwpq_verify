/**
 * hsv_adjust.h — HSV adjustment on pixels: direct RGB-domain vs HSV roundtrip
 *
 * Two families with identical delta semantics (dv / ds / dh):
 *
 *   adjust_hsv_on_rgb_u8/u10 : direct RGB-domain adjustment, no RGB<->HSV
 *                     roundtrip (see run_csc_note.md). Only ONE rgb2hsv pass
 *                     per pixel; RGB is reconstructed in place:
 *                     - V (value)   : RGB' = k*RGB, k = V'/V
 *                                     (gray/black pixels directly get V')
 *                     - S (saturation): keep V (M untouched); each channel's
 *                                     distance to m (or M) is scaled by k = S'/S:
 *                                     RGB'_i = m' + k*(RGB_i - m), m' = V*(1-S')
 *                     - H (hue)     : keep S/V (M/m/C unchanged); RGB values
 *                                     permute inside [m, M] along the hexagon
 *                                     edge (6-segment lookup, M/m roles swap at
 *                                     every 60° node)
 *                     Execution order V -> S -> H; after V re-derive M/m; if
 *                     S=0 no further step; after S, if S'=0 no H step. H uses
 *                     the ORIGINAL hue (V/S never change H), so only one
 *                     rgb2hsv pass is needed and no hsv2rgb reconstruction.
 *
 *   adjust_hsv_on_hsv_u8/u10 : RGB<->HSV roundtrip. Color conversion via
 *                     hsv_fixed (rgb2hsv_fix_u8/u10 -> adjust V/S/H in the HSV
 *                     domain -> hsv2rgb_fix_u8/u10).
 *
 * Fixed-point formats (shared by both families, see hsv_fixed.h):
 *   V  : pixel domain [0, maxv]   (u8: maxv=255, u10: maxv=1023)
 *   S  : Q11, 1.0 = FIX_S_ONE = 2048
 *   H  : normalized Q14, 360° = FIX_H_ONE = 16384
 *   dv : Q10 pixel-domain ΔV ([-1023,1023]), applied by addition
 *   ds : Q10 normalized ΔS ([-1023,1023] => [-1, 1]), S' = S + ds*(FIX_S_ONE/1023)
 *   dh : Q10 hue delta ([-1023,1023] => [-1, 1] turns; LSB = 360°/1023 ≈ 0.35°),
 *        H' = H + dh*(FIX_H_ONE/1023), no division in loop.
 *        Convert from degrees: dh = round(deg * 1023 / 360).
 *   Internal int32 math; multiplies use int64 to prevent overflow
 *   (kk11 can reach 2^22 at very low S).
 *
 * All functions are header-only `static inline`, consistent with hsv_fixed.h /
 * hsv_float.h, so they inline into the caller and vectorize well.
 */
#ifndef HSV_ADJUST_H
#define HSV_ADJUST_H

#include "hsv_fixed.h"

/* ---------------- direct RGB-domain core (shared by u8/u10) ---------------- */
/* one-pixel core of adjust_hsv_on_rgb_u8/u10: int32 math, pixel domain [0, maxv].
   Uses a single rgb2hsv pass (hsv_fixed: H Q14 / S Q11 / V pixel) and applies
   V -> S -> H directly on RGB; no hsv2rgb reconstruction.
   maxv is a compile-time constant at every call site (wrappers pass 255/1023),
   so the u8/u10 dispatch below folds away after inlining. */
static inline void adjust_hsv_on_rgb_impl(uint16_t r, uint16_t g, uint16_t b, uint16_t maxv, int16_t dv, int16_t ds,
    int16_t dh, uint16_t *ro, uint16_t *go, uint16_t *bo)
{
    /* per segment: [M channel, m channel, changing channel], 0/1/2 = R/G/B */
    static const uint8_t TAB[6][3] = {
        {0, 2, 1},
        {1, 2, 0},
        {1, 0, 2},
        {2, 0, 1},
        {2, 1, 0},
        {0, 1, 2},
    };
    uint16_t H, S, V;
    if (maxv == 255) {
        rgb2hsv_fix_u8((uint8_t)r, (uint8_t)g, (uint8_t)b, &H, &S, &V);
        dv = dv >> 2; // Q10 => Q8
    }
    else
        rgb2hsv_fix_u10((uint16_t)r, (uint16_t)g, (uint16_t)b, &H, &S, &V);

    /* ---- adjust V: pixel-domain dv by addition; non-gray scaled by k=V'/V,
       gray set directly, dv=0 keeps original ---- */
    int32_t vn = CLIP(V + dv, 0, maxv);
    int32_t r1 = r, g1 = g, b1 = b;
    if (dv != 0) {
        if (V > 0 && S > 0) {
            const int sh = (maxv == 255) ? 8 : 10; /* k is Q(sh) */
            const int32_t rnd = 1 << (sh - 1);
            int32_t k = ((vn << sh) + (V >> 1)) / V; /* round(vn*2^sh/v8), Q(sh) */
            r1 = CLIP((r * k + rnd) >> sh, 0, maxv);
            g1 = CLIP((g * k + rnd) >> sh, 0, maxv);
            b1 = CLIP((b * k + rnd) >> sh, 0, maxv);
        }
        else {
            r1 = g1 = b1 = vn;
        }
    }

    /* ---- adjust S: （灰色保持 S'=0；ds=0 时 S'=S）提前计算，供 S/H 两步判断 */
    int32_t M = vn;
    int32_t m = MIN3(r1, g1, b1);
    int32_t sn = (S > 0) ? CLIP(S + (int32_t)ds * (FIX_S_ONE / 1024), 0, FIX_S_ONE) : 0;
    if (S > 0 && ds != 0) {
        /* ---- adjust S: m' + k*(RGB_i - m); gray keeps V-step result ---- */
        int32_t k = ((sn << FIX_BITS_S) + (S >> 1)) / S; /* S'/S, Q11 */
        int32_t mn = ((vn * (FIX_S_ONE - sn) + (FIX_S_ONE >> 1)) >> FIX_BITS_S);
        r1 = CLIP(mn + ((k * (r1 - m) + (FIX_S_ONE >> 1)) >> FIX_BITS_S), 0, maxv);
        g1 = CLIP(mn + ((k * (g1 - m) + (FIX_S_ONE >> 1)) >> FIX_BITS_S), 0, maxv);
        b1 = CLIP(mn + ((k * (b1 - m) + (FIX_S_ONE >> 1)) >> FIX_BITS_S), 0, maxv);
        m = mn;
    }

    /* ---- adjust H (uses original H; V/S do not change H); skipped when
       gray (S'=0) or dh=0 (identity) ---- */
    if (sn > 0 && dh != 0) {
        int32_t hn = (H + (int32_t)dh * (FIX_H_ONE / 1024) + FIX_H_ONE) & (FIX_H_ONE - 1); /* dh Q10 -> Q14 */
        int32_t t = hn * 6;
        int32_t seg = t >> FIX_BITS_H;     /* 60° node 0..5, /FIX_H_ONE */
        int32_t f14 = t & (FIX_H_ONE - 1); /* fraction inside the 60° segment */
        int32_t dm = (M - m) * f14;
        int32_t mid = (seg & 1) ? (M - ((dm + (FIX_H_ONE >> 1)) >> FIX_BITS_H))
                                : (m + ((dm + (FIX_H_ONE >> 1)) >> FIX_BITS_H));
        int32_t ch[3] = {m, m, m};
        ch[TAB[seg][0]] = M;
        ch[TAB[seg][2]] = mid;
        r1 = CLIP(ch[0], 0, maxv);
        g1 = CLIP(ch[1], 0, maxv);
        b1 = CLIP(ch[2], 0, maxv);
    }
    *ro = r1;
    *go = g1;
    *bo = b1;
}

/* direct RGB-domain HSV adjustment, 8bit pixels (maxv=255) */
static inline void adjust_hsv_on_rgb_u8(const uint8_t *rgb, int n, int16_t dv, int16_t ds, int16_t dh, uint8_t *out)
{
    for (int i = 0; i < n; i++) {
        uint16_t r1, g1, b1;
        adjust_hsv_on_rgb_impl(rgb[3 * i], rgb[3 * i + 1], rgb[3 * i + 2], 255, dv, ds, dh, &r1, &g1, &b1);
        out[3 * i] = (uint8_t)r1;
        out[3 * i + 1] = (uint8_t)g1;
        out[3 * i + 2] = (uint8_t)b1;
    }
}

/* direct RGB-domain HSV adjustment, 10bit pixels (maxv=1023) */
static inline void adjust_hsv_on_rgb_u10(const uint16_t *rgb, int n, int16_t dv, int16_t ds, int16_t dh, uint16_t *out)
{
    for (int i = 0; i < n; i++) {
        uint16_t r1, g1, b1;
        adjust_hsv_on_rgb_impl(rgb[3 * i], rgb[3 * i + 1], rgb[3 * i + 2], 1023, dv, ds, dh, &r1, &g1, &b1);
        out[3 * i] = (uint16_t)r1;
        out[3 * i + 1] = (uint16_t)g1;
        out[3 * i + 2] = (uint16_t)b1;
    }
}

/* ---------------- HSV roundtrip core (shared by u8/u10) ---------------- */
/* one-pixel core of adjust_hsv_on_hsv_u8/u10: rgb2hsv -> HSV adjust -> hsv2rgb,
   color space conversion via hsv_fixed (rgb2hsv_fix_* / hsv2rgb_fix_*).
   maxv is a compile-time constant at every call site (wrappers pass 255/1023),
   so the u8/u10 dispatch below folds away after inlining. */
static inline void adjust_hsv_on_hsv_impl(uint16_t r, uint16_t g, uint16_t b, uint16_t maxv, int16_t dv, int16_t ds,
    int16_t dh, uint16_t *ro, uint16_t *go, uint16_t *bo)
{
    uint16_t H, S, V;
    if (maxv == 255) {
        rgb2hsv_fix_u8((uint8_t)r, (uint8_t)g, (uint8_t)b, &H, &S, &V);
        dv = dv >> 2;
    }
    else
        rgb2hsv_fix_u10((uint16_t)r, (uint16_t)g, (uint16_t)b, &H, &S, &V);

    /* HSV-domain adjustment, same delta semantics as the RGB-domain family */
    int32_t vn = CLIP((int32_t)V + dv, 0, maxv);
    int32_t sn = (S > 0) ? CLIP((int32_t)S + (int32_t)ds * (FIX_S_ONE / 1024), 0, FIX_S_ONE) : 0;
    int32_t hn = (int32_t)H + (int32_t)dh * (FIX_H_ONE / 1024) + FIX_H_ONE;
    hn &= (FIX_H_ONE - 1);

    if (maxv == 255) {
        uint8_t R, G, B;
        hsv2rgb_fix_u8((uint16_t)hn, (uint16_t)sn, (uint16_t)vn, &R, &G, &B);
        *ro = R;
        *go = G;
        *bo = B;
    }
    else {
        uint16_t R, G, B;
        hsv2rgb_fix_u10((uint16_t)hn, (uint16_t)sn, (uint16_t)vn, &R, &G, &B);
        *ro = R;
        *go = G;
        *bo = B;
    }
}

/* HSV roundtrip adjustment (rgb2hsv -> adjust -> hsv2rgb), 8bit pixels */
static inline void adjust_hsv_on_hsv_u8(const uint8_t *rgb, int n, int16_t dv, int16_t ds, int16_t dh, uint8_t *out)
{
    for (int i = 0; i < n; i++) {
        uint16_t r1, g1, b1;
        adjust_hsv_on_hsv_impl(rgb[3 * i], rgb[3 * i + 1], rgb[3 * i + 2], 255, dv, ds, dh, &r1, &g1, &b1);
        out[3 * i] = (uint8_t)r1;
        out[3 * i + 1] = (uint8_t)g1;
        out[3 * i + 2] = (uint8_t)b1;
    }
}

/* HSV roundtrip adjustment (rgb2hsv -> adjust -> hsv2rgb), 10bit pixels */
static inline void adjust_hsv_on_hsv_u10(const uint16_t *rgb, int n, int16_t dv, int16_t ds, int16_t dh, uint16_t *out)
{
    for (int i = 0; i < n; i++) {
        uint16_t r1, g1, b1;
        adjust_hsv_on_hsv_impl(rgb[3 * i], rgb[3 * i + 1], rgb[3 * i + 2], 1023, dv, ds, dh, &r1, &g1, &b1);
        out[3 * i] = (uint16_t)r1;
        out[3 * i + 1] = (uint16_t)g1;
        out[3 * i + 2] = (uint16_t)b1;
    }
}

#endif /* HSV_ADJUST_H */
