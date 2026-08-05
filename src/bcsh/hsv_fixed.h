/**
 * hsv_fixed.h — RGB <-> HSV 定点(fixed-point)转换（Q16.16），无浮点、无三角函数
 *
 * 定标约定 (Q16.16)：
 *   FIX_ONE = 1 << 16 = 65536
 *   H : 色相，单位"度"，1 度 = FIX_ONE，有效范围 [0, 360*FIX_ONE)
 *   S : 饱和度，[0, FIX_ONE]            （1.0 = FIX_ONE）
 *   V : 明度，[0, 255]                  （与 8bit RGB 同尺度，不缩放）
 *
 * 特点：
 *   - 无 float/double、无三角函数
 *   - rgb2hsv 用优先级掩码消除 6 路分支；hsv2rgb 用 f(n) 公式消除扇区分支
 *   - 仅剩 3 处整数除法（可用倒数表消除）
 *   - hsv2rgb 重建 (V*S*t)>>32 用四舍五入 (+2^31)，u8 全遍历往返 0 误差
 */
#ifndef HSV_FIXED_H
#define HSV_FIXED_H

#include "verify_com.h"
#include <stdint.h>

#define FIX_SHIFT 16
#define FIX_ONE   ((int32_t)1 << FIX_SHIFT) /* 65536 = 1.0 */
#define FIX_6     (6 * FIX_ONE)
#define FIX_360   (360 * FIX_ONE)


typedef struct {
    int32_t H; /* [0, 360*FIX_ONE)，灰度时为 0 */
    int32_t S; /* [0, FIX_ONE] */
    int32_t V; /* [0, 255] */
} hsv_fix_t;

/* 有符号四舍五入除法：x / d，d > 0 */
static inline int32_t div_rnd(int64_t x, int32_t d)
{
    if (x >= 0)
        return (int32_t)((x + d / 2) / d);
    else
        return (int32_t)((x - d / 2) / d);
}

/* clamp01(k) = max(0, min(min(k, 4*FIX_ONE - k), FIX_ONE))，k ∈ [0, 6*FIX_ONE) */
static inline int32_t clamp01(int32_t k)
{
    int32_t t = k;
    if (4 * FIX_ONE - k < t)
        t = 4 * FIX_ONE - k; /* min(k, 4F-k) */
    if (FIX_ONE < t)
        t = FIX_ONE; /* min(t, 1)    */
    if (0 > t)
        t = 0; /* max(t, 0)    */
    return t;
}

/* ---------------- RGB(8bit) -> HSV ---------------- */
static inline hsv_fix_t rgb2hsv_fix(uint8_t R, uint8_t G, uint8_t B)
{
    const int32_t r = R, g = G, b = B;

    int32_t M = MAX3(r, g, b);
    int32_t m = MIN3(r, g, b);
    int32_t C = M - m; /* chroma */

    hsv_fix_t ret;
    ret.V = M;

    /* S = C / V，V==0 -> S=0 */
    ret.S = 0;
    if (M != 0)
        ret.S = div_rnd((int64_t)C << FIX_SHIFT, M); /* [0, FIX_ONE] */

    /* H：三个候选 + 优先级掩码选择（互斥、无分支） */
    ret.H = 0;
    if (C != 0) {
        int32_t hR = div_rnd((int64_t)(g - b) << FIX_SHIFT, C);               /* (G-B)/C */
        int32_t hG = div_rnd((int64_t)(b - r) << FIX_SHIFT, C) + 2 * FIX_ONE; /* +2 */
        int32_t hB = div_rnd((int64_t)(r - g) << FIX_SHIFT, C) + 4 * FIX_ONE; /* +4 */

        /* 优先级：R > G > B，平局(如黄 R=G)时取前者，结果等价 */
        uint32_t mR = (uint32_t)(M == r);
        uint32_t mG = (uint32_t)(M == g) & ~mR;
        uint32_t mB = (uint32_t)(M == b) & ~(mR | mG);

        int32_t selR = (int32_t)(0u - mR); /* 0 或全 1(-1) */
        int32_t selG = (int32_t)(0u - mG);
        int32_t selB = (int32_t)(0u - mB);

        int32_t h = (hR & selR) | (hG & selG) | (hB & selB); /* 恰好选中一个 */

        if (h < 0)
            h += FIX_6; /* 仅 M==R 且 G<B 时为负 */
        ret.H = 60 * h;   /* h 为 Q16.16，×60 即"度" */
    }
    return ret;
}

/* ---------------- HSV -> RGB(8bit) ---------------- */
static inline void hsv2rgb_fix(int32_t H, int32_t S, int32_t V, uint8_t *R, uint8_t *G, uint8_t *B)
{
    /* f(n) = V - V*S*max(0, min(k, 4-k, 1))，k = (n + H/60°) mod 6，n = 5,3,1 */
    int32_t h6 = H / 60; /* H 为"度"的 Q16.16，H/60 单位不变 */

    /* k = n + h6 ∈ [FIX_ONE, 11*FIX_ONE)，mod 6*FIX_ONE 最多减一次 */
    int32_t k5 = 5 * FIX_ONE + h6;
    int32_t k3 = 3 * FIX_ONE + h6;
    int32_t k1 = 1 * FIX_ONE + h6;

    if (k5 >= FIX_6)
        k5 -= FIX_6;
    if (k3 >= FIX_6)
        k3 -= FIX_6;
    if (k1 >= FIX_6)
        k1 -= FIX_6;

    int32_t t5 = clamp01(k5);
    int32_t t3 = clamp01(k3);
    int32_t t1 = clamp01(k1);

    /* f = V - V*S*t / 2^32（V∈[0,255] 原始尺度，S、t 为 Q16.16），重建四舍五入 (+2^31) */
    int32_t r = V - (int32_t)(((int64_t)V * S * t5 + (1LL << 31)) >> (2 * FIX_SHIFT));
    int32_t g = V - (int32_t)(((int64_t)V * S * t3 + (1LL << 31)) >> (2 * FIX_SHIFT));
    int32_t b = V - (int32_t)(((int64_t)V * S * t1 + (1LL << 31)) >> (2 * FIX_SHIFT));

    /* 钳位（输入 H/S 越界或舍入误差时防溢出） */
    r = CLIP(r, 0, 255);
    g = CLIP(g, 0, 255);
    b = CLIP(b, 0, 255);

    *R = (uint8_t)r;
    *G = (uint8_t)g;
    *B = (uint8_t)b;
}

#endif /* HSV_FIXED_H */
