
#include "hsv_fixed.h"


/* ---------- 除法消除：双倒数表（S 表 / H 表，位宽独立） ---------- */
/* 用两张倒数表替换 rgb2hsv 的运行时除法（S=C/V、色相 diff/(6C)）：
   rcp[k]  = round(2^RCP_BITS/k)    —— S=C/V 用，以 V(M) 为索引
   rcp6[k] = round(2^RCP6_BITS/(6k)) —— H=diff/(6C) 用，以 C(Chroma) 为索引
   rcp6 把原两级乘法 (diff×rcp[C])×RCP6 合并为一级乘法 diff×rcp6[C]，省 3 个 /6 乘法器；
   两表索引（M vs C）与定标（/k vs /6k）均不同，无法共用，故独立。
   最小位宽由 hsv_precision_test [11] 全遍历确定：S 表 21bit、H 表 24bit。 */
#define RCP_BITS      21 /* S 表定标位宽；可用 -DRCP_BITS=N 覆盖（最小值 21 由 [11] 全遍历确定） */
#define RCP6_BITS     24 /* H 表 rcp6 定标位宽；可用 -DRCP6_BITS=N 覆盖（最小值 24 由 [11] 全遍历确定） */
#define RCP_MAX       1023
/* v2 参考族保留的固定 /6 常量（独立于双表，勿改） */
#define RCP6_DIV_BITS 18
#define RCP6_DIV      (((1 << RCP6_DIV_BITS) + 3) / 6) /* round(2^18/6)=43691 */

/* S 表：rcp[k] = round(2^RCP_BITS/k)，k∈[1,RCP_MAX]，V(M) 索引 */
static inline const uint32_t *rcp_tbl_u21_fixed(void)
{
    static uint32_t t[RCP_MAX + 1];
    static int ready = 0;
    if (!ready) {
        t[0] = 0;
        for (int k = 1; k <= RCP_MAX; k++)
            t[k] = ((1u << RCP_BITS) + (k >> 1)) / k; /* round(2^RCP_BITS/k) */
        ready = 1;
    }
    return t;
}

/* H 表：rcp6[k] = round(2^RCP6_BITS/(6k))，k∈[1,RCP_MAX]，C(Chroma) 索引。
   利用 (diff×2^14/C)/6 = diff×2^14/(6C) 恒等，H 用 rcp6 一级乘法直接得 Q14 候选 */
static inline const uint32_t *rcp6_tbl_u24_fixed(void)
{
    static uint32_t t[RCP_MAX + 1];
    static int ready = 0;
    if (!ready) {
        t[0] = 0;
        for (int k = 1; k <= RCP_MAX; k++)
            t[k] = ((1u << RCP6_BITS) + 3 * k) / (6 * k); /* round(2^RCP6_BITS/(6k)) */
        ready = 1;
    }
    return t;
}

/* 除法消除（窄乘法形式）：round(a * rcp / 2^rsh)，a ≤ 17bit 有符号、rcp ≤ 24bit。
   调用方把 a 自带的 2 的幂缩放(×2^SH)拆成右移 rsh = 定标位 - SH，乘法器只需 a×rcp 位宽
   （相比 a<<SH × rcp 少 SH 位），适合硬件实现 */
static inline int32_t rcp_mul_rsh(int32_t a, uint32_t rcp, int rsh)
{
    int32_t p = a * rcp;
    p += (1LL << (rsh - 1)) + (p >> 31); /* 有符号四舍五入到 2^rsh */
    return p >> rsh;
}

/* clamp4h(k) = max(0, min(min(k, 4*FIX_H_ONE - k), FIX_H_ONE))，k ∈ [0, 6*FIX_H_ONE)，Q(FIX_BITS_H)
   全三目（编译为 CMOV），无分支预测失败 */
static inline int32_t hsv2rgb_clamp_k(int32_t k)
{
    int32_t t = MIN(k, 4 * FIX_H_ONE - k); /* min(k, 4F-k) */
    t = CLIP(t, 0, FIX_H_ONE);
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
            base = 6;
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
        h = ((base << FIX_BITS_H) + d + 3) / 6;                       /* 先算+d之后的h，这里h已经确保>0 */
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

/* v2：取消除法（倒数表替代 /C、/6；分支保留），适合RTL实现 */
void rgb2hsv_v2_no_division(uint16_t r, uint16_t g, uint16_t b, uint16_t *h14, uint16_t *s11, uint16_t *v10)
{
    const uint32_t *rcp = rcp_tbl_u21_fixed();
    const uint32_t *rcp6 = rcp6_tbl_u24_fixed();
    int32_t M = MAX3(r, g, b);
    int32_t m = MIN3(r, g, b);
    int32_t c = M - m;
    *v10 = M;
    *s11 = (c > 0) ? rcp_mul_rsh(c, rcp[M], RCP_BITS - FIX_BITS_S) : 0; // U21=>U11
    int32_t h = 0;
    if (c > 0) {
        if (M == r) {
            h = (rcp_mul_rsh(g - b, rcp6[c], RCP6_BITS - FIX_BITS_H) + FIX_H_ONE) & (FIX_H_ONE - 1);
        }
        else if (M == g) {
            h = rcp_mul_rsh(b - r, rcp6[c], RCP6_BITS - FIX_BITS_H) + 5461; // U24 max
        }
        else {
            h = rcp_mul_rsh(r - g, rcp6[c], RCP6_BITS - FIX_BITS_H) + 10923;
        }
    }
    *h14 = h;
}

/* v3：取消分支 + 取消除法（优先级掩码 + 双倒数表，CPU友好） */
void rgb2hsv_v3_optimal(uint16_t r, uint16_t g, uint16_t b, uint16_t *h14, uint16_t *s11, uint16_t *v10)
{
    const uint32_t *rcp = rcp_tbl_u21_fixed();   /* S 表：S=C/V，V(M) 索引，RCP_BITS bit */
    const uint32_t *rcp6 = rcp6_tbl_u24_fixed(); /* H 表：H=diff/(6C)，C(Chroma) 索引，RCP6_BITS bit */
    int32_t M = MAX3(r, g, b);                   /* U10: [0, 1023] */
    int32_t m = MIN3(r, g, b);                   /* U10: [0, 1023] */
    int32_t C = M - m;                           /* U10: [0, 1023], chroma */
    *v10 = M;
    *s11 = (C > 0) ? rcp_mul_rsh(C, rcp[M], RCP_BITS - FIX_BITS_S) : 0; // S 表 RCP_BITS(U21)=>U11
    /* H：三个候选 + 优先级掩码选择（互斥、无分支），定标 Q(FIX_BITS_H)。
       双表合并：H = round((A + base*F)/6) = round(diff*2^14/(6C)) + CF_base，
       用 rcp6[C]=round(2^RCP6_BITS/(6C)) 一级乘法直接得 Q14，省掉原 (diff/C) 后再 /6
       的 3 个第二级乘法器；base*F/6 拆为编译期常量 CF（base=6→16384、2→5461、4→10923）。
       diff(≤11bit)×rcp6(≤24bit) 单级乘法，延迟比原两级低一级 */
    int32_t h = 0;
    if (C > 0) {
        int32_t hR = (rcp_mul_rsh(g - b, rcp6[C], RCP6_BITS - FIX_BITS_H) + FIX_H_ONE) & (FIX_H_ONE - 1);
        int32_t hG = rcp_mul_rsh(b - r, rcp6[C], RCP6_BITS - FIX_BITS_H) + 5461; // U22 max
        int32_t hB = rcp_mul_rsh(r - g, rcp6[C], RCP6_BITS - FIX_BITS_H) + 10923;
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
   改进：C11=V*S 提前量化到 2^FIX_BITS_S 对齐（低 11bit 清零），末步舍入因此
   对 H 的 1 Q14 LSB 量化误差不敏感（u8/u10 全遍历 0 误差，对近似 H 同样鲁棒） */
void hsv2rgb_v0_classic(uint16_t H, uint16_t S, uint16_t V, uint16_t maxv, uint16_t *R, uint16_t *G, uint16_t *B)
{
    if (S == 0) {
        *R = *G = *B = V;
        return;
    }
    int32_t C11 = ((V * S + (FIX_S_ONE >> 1)) >> FIX_BITS_S) << FIX_BITS_S; /* Q11 色度，提前量化到 2^11 对齐 */
    int32_t m11 = (V << FIX_BITS_S) - C11;                                  /* Q11 = V*(1-S') */
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
    int32_t h6 = H * 6; // U14*6 => U17
    int32_t k5 = (5 * FIX_H_ONE + h6) % (6 * FIX_H_ONE);
    int32_t k3 = (3 * FIX_H_ONE + h6) % (6 * FIX_H_ONE);
    int32_t k1 = (1 * FIX_H_ONE + h6) % (6 * FIX_H_ONE);
    int32_t t5 = hsv2rgb_clamp_k(k5); // U14
    int32_t t3 = hsv2rgb_clamp_k(k3);
    int32_t t1 = hsv2rgb_clamp_k(k1);
    int32_t vsq = (V * S + (1 << (VS_SHIFT - 1))) >> VS_SHIFT;                 // U10*U11>>11 => U10
    int32_t r = V - (int32_t)((vsq * t5 + (1 << (RS_SHIFT - 1))) >> RS_SHIFT); // U10*U14>>14 => U10
    int32_t g = V - (int32_t)((vsq * t3 + (1 << (RS_SHIFT - 1))) >> RS_SHIFT);
    int32_t b = V - (int32_t)((vsq * t1 + (1 << (RS_SHIFT - 1))) >> RS_SHIFT);
    *R = CLIP(r, 0, maxv);
    *G = CLIP(g, 0, maxv);
    *B = CLIP(b, 0, maxv);
}

/* v2：取消除法（除法全改移位；switch 保留）；
   改进：C11 提前量化到 2^11 对齐（同 v0），末步舍入对 H 量化误差不敏感 */
void hsv2rgb_v2_no_division(uint16_t H, uint16_t S, uint16_t V, uint16_t maxv, uint16_t *R, uint16_t *G, uint16_t *B)
{
    if (S == 0) {
        *R = *G = *B = V;
        return;
    }
    int32_t C11 = ((V * S + (FIX_S_ONE >> 1)) >> FIX_BITS_S) << FIX_BITS_S; /* Q11 色度，提前量化到 2^11 对齐 */
    int32_t m11 = (V << FIX_BITS_S) - C11;                                  /* Q11 = V*(1-S') */
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
    int32_t t5 = hsv2rgb_clamp_k(k5); // U14
    int32_t t3 = hsv2rgb_clamp_k(k3);
    int32_t t1 = hsv2rgb_clamp_k(k1);
    /* f = V - V*S*t / 2^bits（V∈[0,maxv] 像素域，S 为 Q(FIX_BITS_S)、t 为 Q(FIX_BITS_H)），
       重建四舍五入 (+2^(rs-1))>>rs。第一级 V*S（Q11 像素域 ≤ 2^21）先右移 VS_SHIFT
       提前降位宽，使第二级 (V*S>>VS_SHIFT)*t ≤ 2^30 < 2^31，全程 32 位。
       额外误差 ≈ 2^(VS_SHIFT-1-FIX_BITS_S) LSB，VS_SHIFT=5 时 0.008 LSB。 */
    int32_t vsq = (V * S + (1 << (VS_SHIFT - 1))) >> VS_SHIFT;                 // U10*U11>>11 => U10
    int32_t r = V - (int32_t)((vsq * t5 + (1 << (RS_SHIFT - 1))) >> RS_SHIFT); // U10*U14>>14 => U10
    int32_t g = V - (int32_t)((vsq * t3 + (1 << (RS_SHIFT - 1))) >> RS_SHIFT);
    int32_t b = V - (int32_t)((vsq * t1 + (1 << (RS_SHIFT - 1))) >> RS_SHIFT);
    *R = CLIP(r, 0, maxv);
    *G = CLIP(g, 0, maxv);
    *B = CLIP(b, 0, maxv);
}

/* v4：六边形走表模型（M/m/mid + 6 段 TAB，同 hsv_adjust.h 的 H 步）。
   C = round(V*S/2^FIX_BITS_S) 像素域、m = V - C，mid = m + round(C*f14/F)（奇段为 M - dm）；
   无分支（仅灰度判）、无除法、2 个乘法（S*M、C*f14）；末步 CLIP。 */
void hsv2rgb_v4_hexwalk(uint16_t H, uint16_t S, uint16_t V, uint16_t maxv, uint16_t *R, uint16_t *G, uint16_t *B)
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

    /* 灰度：H 无效，V 直接输出 */
    if (S == 0) {
        *R = *G = *B = V;
        return;
    }

    int32_t M = V;
    int32_t C = (S * M + (FIX_S_ONE >> 1)) >> FIX_BITS_S; // U10*U11=>U10
    int32_t m = M - C;
    int32_t t = H * 6; // U14=>U17
    int32_t seg = t >> FIX_BITS_H;     /* 60° node 0..5, /FIX_H_ONE */
    int32_t f14 = t & (FIX_H_ONE - 1); /* fraction inside the 60° segment */
#if 0 /* 和v3输出一致，性能稍低一些 */
    int32_t dm = (seg & 1) ? ((C * f14 + (FIX_H_ONE >> 1)) >> FIX_BITS_H)
                           : ((C * (FIX_H_ONE - f14) + (FIX_H_ONE >> 1)) >> FIX_BITS_H);
    int32_t mid = (M - dm);
#else /* 可以保证和 rgb2hsv_v3 往返误差为0 */
    int32_t dm = ((C * f14 + (FIX_H_ONE >> 1)) >> FIX_BITS_H);
    int32_t mid = (seg & 1) ? (M - dm) : (m + dm);
#endif
    int32_t ch[3] = {m, m, m};
    ch[TAB[seg][0]] = M;
    ch[TAB[seg][2]] = mid;
    *R = CLIP(ch[0], 0, maxv);
    *G = CLIP(ch[1], 0, maxv);
    *B = CLIP(ch[2], 0, maxv);
}