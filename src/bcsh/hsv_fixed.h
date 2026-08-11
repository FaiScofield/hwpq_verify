/**
 * hsv_fixed.h — RGB <-> HSV 定点(fixed-point)转换，无浮点、无三角函数
 *
 * 定标约定（H/S 独立位宽归一化定点，见 hsv_precision_test / hsv_h_norm_test）：
 *   FIX_BITS_H = 14 : H 归一化，360° = 2^14 = 16384，有效范围 [0, FIX_H_ONE)
 *   FIX_BITS_S = 11 : S 归一化，1.0 = 2^11 = 2048，有效范围 [0, FIX_S_ONE]
 *   V : 明度，像素域 [0, maxv]        （u8 时 maxv=255，u10 时 maxv=1023，不缩放）
 *   （u10 输入零误差最小组合 (H=14, S=11)，u8 也满足 H+S>=21bit，两者均 0 误差）
 *
 * 特点：
 *   - 无 float/double、无三角函数
 *   - rgb2hsv 用优先级掩码消除 6 路分支；hsv2rgb 用 f(n) 公式消除扇区分支
 *   - 除法全部消除：S=C/V、色相 /C 用倒数表 rcp_tbl；hsv2rgb 扇区定位
 *     h6 = H*6 为纯乘法；rgb2hsv 的 H=(A+base*FIX_H_ONE)/6 中固定除数 6 用常量 RCP6
 *   - hsv2rgb 重建 (V*S*t)>>(FIX_BITS_H+FIX_BITS_S) 用四舍五入 (+2^(bits-1))，
 *     u8/u10 往返 0 误差
 *   - rgb2hsv_fix_u8 / hsv2rgb_fix_u8 为 u8(0..255) 接口；rgb2hsv_fix_u10 / hsv2rgb_fix_u10 为 u10(0..1023)
 */
#ifndef HSV_FIXED_H
#define HSV_FIXED_H

#include "verify_com.h"
#include <stdint.h>

#define FIX_BITS_H 14                         /* H 归一化位宽：360° = 2^14 */
#define FIX_BITS_S 11                         /* S 归一化位宽：1.0 = 2^11 */
#define FIX_H_ONE  ((int32_t)1 << FIX_BITS_H) /* 360°（H 归一化满量程） */
#define FIX_S_ONE  ((int32_t)1 << FIX_BITS_S) /* 1.0 */

/* 重建第一级 V*S 提前右移位数：使第二级 (V*S>>VS_SHIFT)*t 不超过 int32。
   约束：maxv_bits(10) + FIX_BITS_S(11) + FIX_BITS_H(14) - 31 = 4，取 5 留 1 位余量
   （(2^21>>5)*2^14 = 2^30 < 2^31）。
   额外误差 ≈ 2^(VS_SHIFT-1-FIX_BITS_S) LSB，VS_SHIFT<=8 时 <0.1 LSB，0 误差保持。 */
#define VS_SHIFT   5

typedef struct {
    int32_t H; /* U14: [0, FIX_H_ONE)（360° 归一化），灰度时为 0 */
    int32_t S; /* U11: [0, FIX_S_ONE]（1.0 归一化） */
    int32_t V; /* U10: [0, 1023] */
} hsv_fix_t;

/* ---------- 除法消除：倒数表 ---------- */
/* 用倒数表替换 rgb2hsv 的运行时除法（S=C/V、色相 /C）：
   rcp[k] = round(2^RCP_BITS / k)，k ∈ [1, RCP_MAX]（RCP_MAX 覆盖 u10 最大除数 1023）。
   乘法带符号四舍五入，与精确除法误差 < 0.1 LSB，u8/u10 往返 0 误差保持。 */
#ifndef RCP_BITS
#define RCP_BITS 24 /* 倒数表定标位宽；可用 -DRCP_BITS=N 覆盖（最小值 24 由 hsv_fixed_test 全遍历确定） */
#endif
#define RCP_MAX 1023
#ifndef RCP6_BITS
#define RCP6_BITS 18 /* /6 固定除数倒数位宽，可 -DRCP6_BITS=N 独立覆盖（最小值 18 由 hsv_fixed_test 确定） */
#endif
#define RCP6 ((int32_t)((((int64_t)1 << RCP6_BITS) + 3) / 6)) /* round(2^RCP6_BITS/6)：rgb2hsv 求 H 的固定 /6 倒数 */
static inline const int32_t *rcp_tbl_u24_fixed(void)
{
    static int32_t t[RCP_MAX + 1];
    static int ready = 0;
    if (!ready) {
        t[0] = 0;
        for (int k = 1; k <= RCP_MAX; k++)
            t[k] = (int32_t)((((int64_t)1 << RCP_BITS) + (k >> 1)) / k); /* round(2^RCP_BITS/k) */
        ready = 1;
    }
    return t;
}

/* 除法消除（窄乘法形式）：round(a * rcp / 2^rsh)，a ≤ 17bit 有符号、rcp ≤ RCP_BITS bit。
   调用方把 a 自带的 2 的幂缩放(×2^SH)拆成右移 rsh = RCP_BITS - SH，乘法器只需 a×rcp 位宽
   （相比 a<<SH × rcp 少 SH 位），适合硬件实现 */
static inline int32_t rcp_mul_rsh(int32_t a, int32_t rcp, int rsh)
{
    int64_t p = (int64_t)a * rcp;
    p += (1LL << (rsh - 1)) + (p >> 63); /* 有符号四舍五入到 2^rsh */
    return (int32_t)(p >> rsh);
}

/* clamp01(k) = max(0, min(min(k, 4*FIX_H_ONE - k), FIX_H_ONE))，k ∈ [0, 6*FIX_H_ONE)，Q(FIX_BITS_H)
   全三目（编译为 CMOV），无分支预测失败 */
static inline int32_t clamp01(int32_t k)
{
    int32_t t = k < 4 * FIX_H_ONE - k ? k : 4 * FIX_H_ONE - k; /* min(k, 4F-k) */
    t = t < 0 ? 0 : t;                                         /* max(t, 0)    */
    t = t > FIX_H_ONE ? FIX_H_ONE : t;                         /* min(t, 1)    */
    return t;
}

/* ---------- H 归一化 Q14 <-> hsv_adjust 归一化 Q16(360°=2^16) 互转 ----------
   hsv_adjust.h 的内部 H 是归一化 Q16（360° = 65536 = 2^16，H ∈ [0, 65536)）；
   本文件 H 是归一化 Q14（360° = FIX_H_ONE = 2^14，H ∈ [0, FIX_H_ONE)）。
   两者恒比例 4（2^16/2^14），纯移位、精确无损失。 */
#define FIX_H_Q16_ONE ((int32_t)1 << 16) /* hsv_adjust 归一化 H：360° = 65536 */

/* H Q14 -> H Q16（<<2，精确） */
static inline int32_t hsv_h_to_q16(int32_t H14) { return H14 << 2; }

/* H Q16 -> H Q14（>>2，精确；Q16 低 2 bit 被丢弃） */
static inline int32_t hsv_h_from_q16(int32_t H16) { return H16 >> 2; }

/* ---------------- RGB(maxv) -> HSV（通用核心） ---------------- */
/* 通用：R/G/B ∈ [0, maxv]（8bit/10bit 均可），S/H 为比值/角度，与位深无关 */
static inline hsv_fix_t rgb2hsv_fix_impl(int32_t r, int32_t g, int32_t b)
{
    const int32_t *rcp_u24 = rcp_tbl_u24_fixed();

    int32_t M = MAX3(r, g, b); /* U10: [0, 1023] */
    int32_t m = MIN3(r, g, b); /* U10: [0, 1023] */
    int32_t C = M - m;         /* U10: [0, 1023], chroma */

    hsv_fix_t ret = {0};
    ret.V = M;

    /* S = C / V，V==0 -> S=0，定标 Q(FIX_BITS_S)；倒数表替代除法 */
    ret.S = 0;
    if (M != 0)
        ret.S = rcp_mul_rsh(C, rcp_u24[M], RCP_BITS - FIX_BITS_S); /* round(C<<S / M)，[0, FIX_S_ONE] */

    /* H：三个候选 + 优先级掩码选择（互斥、无分支），定标 Q(FIX_BITS_H)
       先求 A = Q14 的 diff/C（倒数表，四舍五入），再 H = round((A + base*FIX_H_ONE)/6)，
       base∈{6,2,4}；÷6 用常量 RCP6=round(2^28/6)，避免 FIX_H_6=2731(≠2^14/6) 的系统偏差 */
    ret.H = 0;
    if (C != 0) {
        int32_t aR = rcp_mul_rsh(g - b, rcp_u24[C], RCP_BITS - FIX_BITS_H);              /* Q14: (g-b)/C ∈ [-1,1] */
        int32_t aG = rcp_mul_rsh(b - r, rcp_u24[C], RCP_BITS - FIX_BITS_H);              /* Q14: (b-r)/C ∈ [-1,1] */
        int32_t aB = rcp_mul_rsh(r - g, rcp_u24[C], RCP_BITS - FIX_BITS_H);              /* Q14: (r-g)/C ∈ [-1,1] */
        int32_t hR = rcp_mul_rsh(aR + 6 * FIX_H_ONE, RCP6, RCP6_BITS) & (FIX_H_ONE - 1); /* ([0,2]+6)/6 => 360°=>0 回绕 */
        int32_t hG = rcp_mul_rsh(aG + 2 * FIX_H_ONE, RCP6, RCP6_BITS);                   /* ([-1,1]+2)/6 => [1,3]/6 */
        int32_t hB = rcp_mul_rsh(aB + 4 * FIX_H_ONE, RCP6, RCP6_BITS);                   /* ([-1,1]+4)/6 => [3,5]/6 */

        /* 优先级：R > G > B，平局(如黄 R=G)时取前者，结果等价 */
        uint32_t mR = (uint32_t)(M == r);
        uint32_t mG = (uint32_t)(M == g) & ~mR;
        uint32_t mB = (uint32_t)(M == b) & ~(mR | mG);
        int32_t selR = (int32_t)(0u - mR); /* 0 或全 1(-1) */
        int32_t selG = (int32_t)(0u - mG);
        int32_t selB = (int32_t)(0u - mB);

        ret.H = (hR & selR) | (hG & selG) | (hB & selB); /* 恰好选中一个候选，Q(FIX_BITS_H) */
    }
    return ret;
}

/* RGB(8bit) -> HSV */
static inline hsv_fix_t rgb2hsv_fix_u8(uint8_t R, uint8_t G, uint8_t B) { return rgb2hsv_fix_impl(R, G, B); }

/* RGB(10bit) -> HSV */
static inline hsv_fix_t rgb2hsv_fix_u10(int32_t R, int32_t G, int32_t B) { return rgb2hsv_fix_impl(R, G, B); }

/* ---------------- HSV -> RGB(maxv)（通用核心） ---------------- */
/* 通用：输出 clamp [0, maxv]，V ∈ [0, maxv]（u8 maxv=255，u10 maxv=1023） */
static inline void hsv2rgb_fix_impl(int32_t H_u14, int32_t S_u11, int32_t V_u10, int32_t maxv, int32_t *R, int32_t *G,
    int32_t *B)
{
    /* 灰度：H 无效，V 直接输出 */
    if (0 == S_u11) {
        *R = V_u10;
        *G = V_u10;
        *B = V_u10;
        return;
    }

    /* f(n) = V - V*S*max(0, min(k, 4-k, 1))，k = (n + 6*H') mod 6，n = 5,3,1，
       H' = H/360 ∈ [0,1)。H 归一化 Q14（360°=FIX_H_ONE）后 h6 = H*6 纯乘法。 */
    int32_t h6 = H_u14 * 6; /* 六边形位置（0..6 扇区）× FIX_H_ONE */

    /* k = n + h6 ∈ [FIX_H_ONE, 11*FIX_H_ONE)，mod 6*FIX_H_ONE（整圈）最多减一次；
       三目（CMOV）无分支（注意是整圈 6*FIX_H_ONE，不是单扇区 FIX_H_6） */
    int32_t k5 = 5 * FIX_H_ONE + h6;
    int32_t k3 = 3 * FIX_H_ONE + h6;
    int32_t k1 = 1 * FIX_H_ONE + h6;

    k5 = k5 >= 6 * FIX_H_ONE ? k5 - 6 * FIX_H_ONE : k5;
    k3 = k3 >= 6 * FIX_H_ONE ? k3 - 6 * FIX_H_ONE : k3;
    k1 = k1 >= 6 * FIX_H_ONE ? k1 - 6 * FIX_H_ONE : k1;

    int32_t t5 = clamp01(k5);
    int32_t t3 = clamp01(k3);
    int32_t t1 = clamp01(k1);

    /* f = V - V*S*t / 2^bits（V∈[0,maxv] 像素域，S 为 Q(FIX_BITS_S)、t 为 Q(FIX_BITS_H)），
       重建四舍五入 (+2^(rs-1))>>rs。第一级 V*S（Q11 像素域 ≤ 2^21）先右移 VS_SHIFT
       提前降位宽，使第二级 (V*S>>VS_SHIFT)*t ≤ 2^30 < 2^31，全程 32 位。
       额外误差 ≈ 2^(VS_SHIFT-1-FIX_BITS_S) LSB，VS_SHIFT=5 时 0.008 LSB。 */
    int32_t vs = V_u10 * S_u11;                             /* Q11 像素域，≤ 2095104 < 2^31 */
    int32_t vsq = (vs + (1 << (VS_SHIFT - 1))) >> VS_SHIFT; /* 四舍五入，Q(11-5)=Q6，≤ 65472 */
    int32_t rs = FIX_BITS_H + FIX_BITS_S - VS_SHIFT;        /* 20 */
    int32_t r = V_u10 - (int32_t)((vsq * t5 + (1 << (rs - 1))) >> rs);
    int32_t g = V_u10 - (int32_t)((vsq * t3 + (1 << (rs - 1))) >> rs);
    int32_t b = V_u10 - (int32_t)((vsq * t1 + (1 << (rs - 1))) >> rs);

    /* 钳位（输入 H/S 越界或舍入误差时防溢出） */
    r = CLIP(r, 0, maxv);
    g = CLIP(g, 0, maxv);
    b = CLIP(b, 0, maxv);

    *R = r;
    *G = g;
    *B = b;
}

/* HSV -> RGB(8bit) */
static inline void hsv2rgb_fix_u8(int32_t H, int32_t S, int32_t V, uint8_t *R, uint8_t *G, uint8_t *B)
{
    int32_t r, g, b;
    hsv2rgb_fix_impl(H, S, V, 255, &r, &g, &b);
    *R = (uint8_t)r;
    *G = (uint8_t)g;
    *B = (uint8_t)b;
}

/* HSV -> RGB(10bit) */
static inline void hsv2rgb_fix_u10(int32_t H, int32_t S, int32_t V, int32_t *R, int32_t *G, int32_t *B)
{
    hsv2rgb_fix_impl(H, S, V, 1023, R, G, B);
}

#endif /* HSV_FIXED_H */
