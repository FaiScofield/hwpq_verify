
#include "hsv_fixed.h"


/* ---------- 除法消除：倒数表 ---------- */
/* 用倒数表替换 rgb2hsv 的运行时除法（S=C/V、色相 /C）：
   rcp[k] = round(2^RCP_BITS / k)，k ∈ [1, RCP_MAX]（RCP_MAX 覆盖 u10 最大除数 1023）。
   乘法带符号四舍五入，与精确除法误差 < 0.1 LSB，u8/u10 往返 0 误差保持。 */
#define RCP_BITS  24 /* 倒数表定标位宽；可用 -DRCP_BITS=N 覆盖（最小值 24 由 hsv_fixed_test 全遍历确定） */
#define RCP6_BITS 18 /* /6 固定除数倒数位宽，可 -DRCP6_BITS=N 独立覆盖（最小值 18 由 hsv_fixed_test 确定） */
#define RCP_MAX   1023
#define RCP6      ((int32_t)((((int64_t)1 << RCP6_BITS) + 3) / 6)) /* round(2^RCP6_BITS/6)：rgb2hsv 求 H 的固定 /6 倒数 */

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

/* clamp4h(k) = max(0, min(min(k, 4*FIX_H_ONE - k), FIX_H_ONE))，k ∈ [0, 6*FIX_H_ONE)，Q(FIX_BITS_H)
   全三目（编译为 CMOV），无分支预测失败 */
static inline int32_t clamp4h(int32_t k)
{
    int32_t t = k < 4 * FIX_H_ONE - k ? k : 4 * FIX_H_ONE - k; /* min(k, 4F-k) */
    t = t < 0 ? 0 : t;                                         /* max(t, 0)    */
    t = t > FIX_H_ONE ? FIX_H_ONE : t;                         /* min(t, 1)    */
    return t;
}


/* ---------------- RGB(maxv) -> HSV（Q14/Q11 参考族） ---------------- */
/* trad：经典，分支 + 除法 */
void rgb2hsv_v0_classic(uint16_t r, uint16_t g, uint16_t b, uint16_t *h14, uint16_t *s11, uint16_t *v10)
{
    int32_t M = MAX3(r, g, b);
    int32_t m = MIN3(r, g, b);
    int32_t c = M - m;
    *v10 = M;
    *s11 = (c > 0) ? ((c << FIX_BITS_S) + (M >> 1)) / M : 0;
    int32_t h = 0;
    if (c > 0) {
        int32_t d, base; /* base: 0=R 段 2=G 段 4=B 段 */
        if (M == r) {
            d = g - b;
            base = 0;
        }
        else if (M == g) {
            d = b - r;
            base = 2;
        }
        else {
            d = r - g;
            base = 4;
        }
        d = ((d << FIX_BITS_H) + (d < 0 ? -(c >> 1) : (c >> 1))) / c; /* [-1.0, 1.0]*FIX_BITS_H */
        h = ((base << FIX_BITS_H) + d);                               /* 先算+d之后的h */
        h = (h + (h < 0 ? -3 : 3)) / 6 + FIX_H_ONE;                   /* 再按h的符号做除法的舍入 */
        h = h & (FIX_H_ONE - 1);                                      /* mod 2^13，负值由 +FIX_H_ONE 回绕 */
    }
    *h14 = h;
}

/* v1：取消分支（优先级掩码选 H 候选；S 仍用除法） */
void rgb2hsv_v1_no_branch(uint16_t r, uint16_t g, uint16_t b, uint16_t *h14, uint16_t *s11, uint16_t *v10)
{
    int32_t M = MAX3(r, g, b);
    int32_t m = MIN3(r, g, b);
    int32_t c = M - m;
    *v10 = M;
    *s11 = (c > 0) ? ((c << FIX_BITS_S) + (M >> 1)) / M : 0;
    int32_t h = 0;
    if (c > 0) {
        int32_t dR = g - b, dG = b - r, dB = r - g;
        int32_t aR = ((dR << FIX_BITS_H) + (dR < 0 ? -(c >> 1) : (c >> 1))) / c; // dR might be negative
        int32_t aG = ((dG << FIX_BITS_H) + (dG < 0 ? -(c >> 1) : (c >> 1))) / c;
        int32_t aB = ((dB << FIX_BITS_H) + (dB < 0 ? -(c >> 1) : (c >> 1))) / c;
        /* H = round((a + base*F)/6)，base∈{6,2,4}（6 使 hR 恒正、& mask 回绕） */
        int32_t hR = (((6 << FIX_BITS_H) + aR + 3) / 6) & (FIX_H_ONE - 1);
        int32_t hG = ((2 << FIX_BITS_H) + aG + 3) / 6;
        int32_t hB = ((4 << FIX_BITS_H) + aB + 3) / 6;
        uint32_t mR = (uint32_t)(M == r);
        uint32_t mG = (uint32_t)(M == g) & ~mR;
        uint32_t mB = (uint32_t)(M == b) & ~(mR | mG);
        int32_t selR = (int32_t)(0u - mR); /* 0 或 -1 */
        int32_t selG = (int32_t)(0u - mG);
        int32_t selB = (int32_t)(0u - mB);
        h = (hR & selR) | (hG & selG) | (hB & selB);
    }
    *h14 = h;
}

/* v2：取消除法（倒数表替代 /C、/6；分支保留） */
void rgb2hsv_v2_no_division(uint16_t r, uint16_t g, uint16_t b, uint16_t *h14, uint16_t *s11, uint16_t *v10)
{
    const int32_t *rcp = rcp_tbl_u24_fixed();
    int32_t M = MAX3(r, g, b);
    int32_t m = MIN3(r, g, b);
    int32_t c = M - m;
    *v10 = M;
    *s11 = (c > 0) ? rcp_mul_rsh(c, rcp[M], RCP_BITS - FIX_BITS_S) : 0;
    int32_t h = 0;
    if (c > 0) {
        int32_t d, base; /* 分支保留 */
        if (M == r) {
            d = g - b;
            base = 0;
        }
        else if (M == g) {
            d = b - r;
            base = 2;
        }
        else {
            d = r - g;
            base = 4;
        }
        int32_t a = rcp_mul_rsh(d, rcp[c], RCP_BITS - FIX_BITS_H);                   /* round(diff<<13/C) */
        int32_t h_ = rcp_mul_rsh(a + base * FIX_H_ONE, RCP6, RCP6_BITS) + FIX_H_ONE; /* /6 */
        h = h_ & (FIX_H_ONE - 1);
    }
    *h14 = h;
}

/* v3：取消分支 + 取消除法（优先级掩码 + 倒数表，硬件友好） */
void rgb2hsv_v3_optimal(uint16_t r, uint16_t g, uint16_t b, uint16_t *h14, uint16_t *s11, uint16_t *v10)
{
    const int32_t *rcp = rcp_tbl_u24_fixed();
    int32_t M = MAX3(r, g, b); /* U10: [0, 1023] */
    int32_t m = MIN3(r, g, b); /* U10: [0, 1023] */
    int32_t C = M - m;         /* U10: [0, 1023], chroma */
    *v10 = M;
    *s11 = (C > 0) ? rcp_mul_rsh(C, rcp[M], RCP_BITS - FIX_BITS_S) : 0;
    /* H：三个候选 + 优先级掩码选择（互斥、无分支），定标 Q(FIX_BITS_H)
       先求 A = Q14 的 diff/C（倒数表），再 H = round((A + base*FIX_H_ONE)/6)，
       base∈{6,2,4}；÷6 用常量 RCP6=round(2^RCP6_BITS/6)，避免 FIX_H_6=2731(≠2^14/6) 的系统偏差 */
    int32_t h = 0;
    if (C > 0) {
        int32_t aR = rcp_mul_rsh(g - b, rcp[C], RCP_BITS - FIX_BITS_H);
        int32_t aG = rcp_mul_rsh(b - r, rcp[C], RCP_BITS - FIX_BITS_H);
        int32_t aB = rcp_mul_rsh(r - g, rcp[C], RCP_BITS - FIX_BITS_H);
        /* H = round((A + base*F)/6)，base∈{6,2,4}（6 使 hR 恒正，& mask 回绕） */
        int32_t hR = rcp_mul_rsh(aR + (6 << FIX_BITS_H), RCP6, RCP6_BITS) & (FIX_H_ONE - 1);
        int32_t hG = rcp_mul_rsh(aG + (2 << FIX_BITS_H), RCP6, RCP6_BITS);
        int32_t hB = rcp_mul_rsh(aB + (4 << FIX_BITS_H), RCP6, RCP6_BITS);
        uint32_t mR = (uint32_t)(M == r);
        uint32_t mG = (uint32_t)(M == g) & ~mR;
        uint32_t mB = (uint32_t)(M == b) & ~(mR | mG);
        int32_t selR = (int32_t)(0u - mR);
        int32_t selG = (int32_t)(0u - mG);
        int32_t selB = (int32_t)(0u - mB);
        h = (hR & selR) | (hG & selG) | (hB & selB);
    }
    *h14 = h;
}

/* ---------------- HSV -> RGB(maxv)（Q14/Q11 参考族） ---------------- */
/* v0：经典 C/X/m 模型，switch 分支 + 除法；
   改进：全程 Q11（像素域×F_S13）保精度，舍入推迟到最后一步，消除提前舍入 C 的 1 LSB */
void hsv2rgb_v0_classic(uint16_t H, uint16_t S, uint16_t V, uint16_t maxv, uint16_t *R, uint16_t *G, uint16_t *B)
{
    if (S == 0) {
        *R = *G = *B = V;
        return;
    }
    int32_t C11 = V * S;                   /* Q11 色度（不提前舍入） */
    int32_t m11 = (V << FIX_BITS_S) - C11; /* Q11 = V*(1-S') */
    int32_t h6 = H * 6;
    int32_t seg = h6 / FIX_H_ONE;       /* 扇区 0..5 */
    int32_t hp2 = h6 % (2 * FIX_H_ONE); /* hp mod 2（120° 帐篷周期） */
    int32_t t = hp2 - FIX_H_ONE;
    if (t < 0)
        t = -t;                                                                       /* |hp mod 2 - 1| */
    int32_t X11 = C11 - (int32_t)(((int64_t)C11 * t + (FIX_H_ONE >> 1)) / FIX_H_ONE); /* Q11 = C*(1-|..|) */
    int32_t r11, g11, b11;
    switch (seg) {
    case 0:
        r11 = C11 + m11;
        g11 = X11 + m11;
        b11 = m11;
        break;
    case 1:
        r11 = X11 + m11;
        g11 = C11 + m11;
        b11 = m11;
        break;
    case 2:
        r11 = m11;
        g11 = C11 + m11;
        b11 = X11 + m11;
        break;
    case 3:
        r11 = m11;
        g11 = X11 + m11;
        b11 = C11 + m11;
        break;
    case 4:
        r11 = X11 + m11;
        g11 = m11;
        b11 = C11 + m11;
        break;
    default:
        r11 = C11 + m11;
        g11 = m11;
        b11 = X11 + m11;
        break;
    }
    /* 最后一步四舍五入 Q11→像素域 */
    *R = CLIP((r11 + (FIX_S_ONE >> 1)) >> FIX_BITS_S, 0, maxv);
    *G = CLIP((g11 + (FIX_S_ONE >> 1)) >> FIX_BITS_S, 0, maxv);
    *B = CLIP((b11 + (FIX_S_ONE >> 1)) >> FIX_BITS_S, 0, maxv);
}

/* v1：取消分支（f(n) 公式 + 三目 clamp01 替代 switch；保留 % 除法） */
void hsv2rgb_v1_no_branch(uint16_t H, uint16_t S, uint16_t V, uint16_t maxv, uint16_t *R, uint16_t *G, uint16_t *B)
{
    if (S == 0) {
        *R = *G = *B = V;
        return;
    }
    int32_t h6 = H * 6;
    int32_t k5 = (5 * FIX_H_ONE + h6) % (6 * FIX_H_ONE);
    int32_t k3 = (3 * FIX_H_ONE + h6) % (6 * FIX_H_ONE);
    int32_t k1 = (1 * FIX_H_ONE + h6) % (6 * FIX_H_ONE);
    int32_t t5 = clamp4h(k5);
    int32_t t3 = clamp4h(k3);
    int32_t t1 = clamp4h(k1);
    int32_t vsq = (V * S + (1 << (VS_SHIFT - 1))) >> VS_SHIFT;                 // U10*U12>>5 => U17
    int32_t r = V - (int32_t)((vsq * t5 + (1 << (RS_SHIFT - 1))) >> RS_SHIFT); // U17*U13>>20 => U10
    int32_t g = V - (int32_t)((vsq * t3 + (1 << (RS_SHIFT - 1))) >> RS_SHIFT);
    int32_t b = V - (int32_t)((vsq * t1 + (1 << (RS_SHIFT - 1))) >> RS_SHIFT);
    *R = CLIP(r, 0, maxv);
    *G = CLIP(g, 0, maxv);
    *B = CLIP(b, 0, maxv);
}

/* v2：取消除法（除法全改移位；switch 保留）；
   改进：全程 Q11 保精度，舍入推迟到最后一步（同 v0） */
void hsv2rgb_v2_no_division(uint16_t H, uint16_t S, uint16_t V, uint16_t maxv, uint16_t *R, uint16_t *G, uint16_t *B)
{
    if (S == 0) {
        *R = *G = *B = V;
        return;
    }
    int32_t C11 = V * S;                   /* Q11 色度（不提前舍入） */
    int32_t m11 = (V << FIX_BITS_S) - C11; /* Q11 = V*(1-S') */
    int32_t h6 = H * 6;
    int32_t seg = h6 >> FIX_BITS_H;         /* /F_H → >>14 */
    int32_t hp2 = h6 & (2 * FIX_H_ONE - 1); /* %2F → &(2F-1)（120° 帐篷周期） */
    int32_t t = hp2 - FIX_H_ONE;
    if (t < 0)
        t = -t;                                                                         /* |hp mod 2 - 1| */
    int32_t X11 = C11 - (int32_t)(((int64_t)C11 * t + (FIX_H_ONE >> 1)) >> FIX_BITS_H); /* Q11，/F → >>14 四舍五入 */
    int32_t r11, g11, b11;
    switch (seg) {
    case 0:
        r11 = C11 + m11;
        g11 = X11 + m11;
        b11 = m11;
        break;
    case 1:
        r11 = X11 + m11;
        g11 = C11 + m11;
        b11 = m11;
        break;
    case 2:
        r11 = m11;
        g11 = C11 + m11;
        b11 = X11 + m11;
        break;
    case 3:
        r11 = m11;
        g11 = X11 + m11;
        b11 = C11 + m11;
        break;
    case 4:
        r11 = X11 + m11;
        g11 = m11;
        b11 = C11 + m11;
        break;
    default:
        r11 = C11 + m11;
        g11 = m11;
        b11 = X11 + m11;
        break;
    }
    /* 最后一步四舍五入 Q11→像素域 */
    *R = CLIP((r11 + (FIX_S_ONE >> 1)) >> FIX_BITS_S, 0, maxv);
    *G = CLIP((g11 + (FIX_S_ONE >> 1)) >> FIX_BITS_S, 0, maxv);
    *B = CLIP((b11 + (FIX_S_ONE >> 1)) >> FIX_BITS_S, 0, maxv);
}

/* v3：取消分支 + 取消除法（f(n) + 单次减 mod + 三目 + 全移位，硬件友好） */
void hsv2rgb_v3_optimal(uint16_t H, uint16_t S, uint16_t V, uint16_t maxv, uint16_t *R, uint16_t *G, uint16_t *B)
{
    /* 灰度：H 无效，V 直接输出 */
    if (S == 0) {
        *R = *G = *B = V;
        return;
    }
    /* f(n) = V - V*S*max(0, min(k, 4-k, 1))，k = (n + 6*H') mod 6，n = 5,3,1，
       H' = H/360 ∈ [0,1)。H 归一化 Q14（360°=FIX_H_ONE）后 h6 = H*6 纯乘法。 */
    int32_t h6 = H * 6; /* 六边形位置（0..6 扇区）× FIX_H_ONE */

    /* k = n + h6 ∈ [FIX_H_ONE, 11*FIX_H_ONE)，mod 6*FIX_H_ONE（整圈）最多减一次；
       三目（CMOV）无分支（注意是整圈 6*FIX_H_ONE，不是单扇区 FIX_H_6） */
    int32_t k5 = 5 * FIX_H_ONE + h6;
    int32_t k3 = 3 * FIX_H_ONE + h6;
    int32_t k1 = 1 * FIX_H_ONE + h6;
    k5 = (k5 >= 6 * FIX_H_ONE) ? k5 - 6 * FIX_H_ONE : k5;
    k3 = (k3 >= 6 * FIX_H_ONE) ? k3 - 6 * FIX_H_ONE : k3;
    k1 = (k1 >= 6 * FIX_H_ONE) ? k1 - 6 * FIX_H_ONE : k1;
    int32_t t5 = clamp4h(k5);
    int32_t t3 = clamp4h(k3);
    int32_t t1 = clamp4h(k1);
    /* f = V - V*S*t / 2^bits（V∈[0,maxv] 像素域，S 为 Q(FIX_BITS_S)、t 为 Q(FIX_BITS_H)），
       重建四舍五入 (+2^(rs-1))>>rs。第一级 V*S（Q11 像素域 ≤ 2^21）先右移 VS_SHIFT
       提前降位宽，使第二级 (V*S>>VS_SHIFT)*t ≤ 2^30 < 2^31，全程 32 位。
       额外误差 ≈ 2^(VS_SHIFT-1-FIX_BITS_S) LSB，VS_SHIFT=5 时 0.008 LSB。 */
    int32_t vsq = (V * S + (1 << (VS_SHIFT - 1))) >> VS_SHIFT;
    int32_t r = V - (int32_t)((vsq * t5 + (1 << (RS_SHIFT - 1))) >> RS_SHIFT);
    int32_t g = V - (int32_t)((vsq * t3 + (1 << (RS_SHIFT - 1))) >> RS_SHIFT);
    int32_t b = V - (int32_t)((vsq * t1 + (1 << (RS_SHIFT - 1))) >> RS_SHIFT);
    *R = CLIP(r, 0, maxv);
    *G = CLIP(g, 0, maxv);
    *B = CLIP(b, 0, maxv);
}