/**
 * hsv_precision_test.c — 分析 H/S 定点量化精度对往返误差的影响 + 位宽参数扫描
 *
 * 用例：
 *   [1] u8 只量化 S（H 精确）     [2] u8 只量化 H（S 精确）   [3] u8 组合边界确认
 *   [4] u10 只量化 S（H 精确）    [5] u10 只量化 H（S 精确）   [6] u10 组合边界确认
 *   [7] 定点版往返精度（u8 + u10，H=Q14/S=Q11 当前实现）
 *   [8] 扫描 RCP_BITS：往返 0 损失下的最小值（VS_SHIFT 固定当前值）
 *   [9] 扫描 VS_SHIFT：往返 0 损失下的最大值（RCP_BITS 固定当前值）
 *   [10] (RCP_BITS, VS_SHIFT) 组合扫描：往返 0 损失下最大乘法器位宽最低
 *
 * 用法（getopt_win32.h）：
 *   hsv_precision_test -s <n> -S <n> -t <n1,n2,...> -h
 *     -s u8 采样间隔 [1,16]（默认 3）
 *     -S u10 采样间隔 [1,32]（默认 7）
 *     -t <n1,n2,...> 指定运行用例列表（逗号分隔，缺省全跑；-s/-S 仅设定采样间隔）
 *     -h 帮助
 *   例：hsv_precision_test -s 1 -S 3             # u8 全遍历 + u10 密抽样 + 全部用例
 *       hsv_precision_test -t 8                  # 只跑 RCP_BITS 扫描
 *       hsv_precision_test -t 1,2,3,7 -s 3 -S 7  # 跑指定用例
 */

#include "hsv_fixed.h"
#include "hsv_float.h"
#include "getopt_win32.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <limits.h>
#include <assert.h>

/* RCP_BITS/RCP6_BITS/RCP6/RCP_MAX 宏定义在 hsv_fixed.c（测试程序不可见），此处复制常量供参数化扫描 */
#define RCP_BITS  24
#define RCP6_BITS 18
#define RCP_MAX   1023
#define RCP6      ((int32_t)((((int64_t)1 << RCP6_BITS) + 3) / 6))

/* ---------- H/S 定点量化模拟 ---------- */
/* H(度) 量化到 bh 位：0..360 用 2^bh 个台阶 */
static float quantH(float H, int bh)
{
    int q = (int)lrintf(H / 360.0f * (float)(1 << bh));
    q = MIN(q, (1 << bh) - 1);
    return (float)q / (float)(1 << bh) * 360.0f;
}

/* S∈[0,1] 量化到 bs 位：0..1 用 2^bs 个台阶 */
static float quantS(float S, int bs)
{
    int q = (int)lrintf(S * (float)(1 << bs));
    q = MIN(q, (1 << bs));
    return (float)q / (float)(1 << bs);
}

/* 计算 (bh, bs) 下 bits 位输入（步长 stride，保证含端点 maxv）的最大单通道往返误差(LSB) */
static int eval_quant_bits(int bh, int bs, int stride, int bits, float *err_ratio)
{
    const int maxv = (1 << bits) - 1;
    int vals[1024], nv = 0;
    for (int v = 0; v <= maxv; v += stride)
        vals[nv++] = v;
    if (vals[nv - 1] != maxv)
        vals[nv++] = maxv; // [0,str,2*str,...,maxv]，保证含端点 maxv

    int errcnt = 0;
    int maxerr = 0;
    for (int i = 0; i < nv; i++)
        for (int j = 0; j < nv; j++)
            for (int k = 0; k < nv; k++) {
                int r = vals[i], g = vals[j], b = vals[k];
                hsv_f hsv = rgb2hsv_float(r / (float)maxv, g / (float)maxv, b / (float)maxv);
                float Hq = quantH(hsv.H, bh);
                float Sq = quantS(hsv.S, bs);
                float R, G, B;
                hsv2rgb_float(Hq, Sq, hsv.V, &R, &G, &B); /* 其余保持精确 */
                int dr = (int)lrintf(R * (float)maxv) - r;
                int dg = (int)lrintf(G * (float)maxv) - g;
                int db = (int)lrintf(B * (float)maxv) - b;
                int m = MAX3(abs(dr), abs(dg), abs(db));
                maxerr = MAX(m, maxerr);
                if (m)
                    errcnt++;
            }
    if (err_ratio)
        *err_ratio = errcnt / (float)(nv * nv * nv);
    return maxerr;
}

/* 便捷封装 */
static int eval_quant_u8(int bh, int bs, int stride, float *err_ratio)
{
    return eval_quant_bits(bh, bs, stride, 8, err_ratio);
}
static int eval_quant_u10(int bh, int bs, int stride, float *err_ratio)
{
    return eval_quant_bits(bh, bs, stride, 10, err_ratio);
}

/* ---------- 定点版往返精度 ---------- */
/* 定点版往返误差：bits 位输入（u8 全遍历 stride=1；u10 用抽样）；返回有偏差样本百分比 */
static double eval_fixed_bits(const char *name, int bits, int stride)
{
    const int maxv = (1 << bits) - 1;
    uint64_t n = 0, n_err = 0;
    int maxerr = 0;
    for (int r = 0; r <= maxv; r += stride)
        for (int g = 0; g <= maxv; g += stride)
            for (int b = 0; b <= maxv; b += stride) {
                uint16_t H, S, V;
                uint16_t R = 0, G = 0, B = 0;
                if (bits == 8) {
                    rgb2hsv_fix_u8((uint8_t)r, (uint8_t)g, (uint8_t)b, &H, &S, &V);
                    uint8_t r8, g8, b8;
                    hsv2rgb_fix_u8(H, S, V, &r8, &g8, &b8);
                    R = r8;
                    G = g8;
                    B = b8;
                }
                else {
                    rgb2hsv_fix_u10((uint16_t)r, (uint16_t)g, (uint16_t)b, &H, &S, &V);
                    hsv2rgb_fix_u10(H, S, V, &R, &G, &B);
                }
                int dr = (int)R - r, dg = (int)G - g, db = (int)B - b;
                int m = MAX3(abs(dr), abs(dg), abs(db));
                if (m) {
                    n_err++;
                    maxerr = MAX(m, maxerr);
                }
                n++;
            }
    double pct = 100.0 * n_err / (double)n;
    printf("%-40s 有偏差=%9llu (%.4f%%)  max|Δ|=%d LSB\n", name, (unsigned long long)n_err, pct, maxerr);
    return pct;
}

/* ================= 参数化 v3（供 [8][9][10] 扫描 RCP_BITS / VS_SHIFT） ================= */
/* -t 指定的用例列表（逗号分隔，缺省=全跑） */
static int g_tids[16];
static int g_tn = 0;
static int want(int id)
{
    if (g_tn == 0)
        return 1; /* 未指定 -t：全跑 */
    for (int i = 0; i < g_tn; i++)
        if (g_tids[i] == id)
            return 1;
    return 0;
}

/* 同 hsv_fixed.c 的 rcp_mul_rsh（.c 内 static，此处复制以便参数化） */
static int32_t rcp_mul_rsh_p(int32_t a, uint32_t rcp, int rsh)
{
    assert(rsh >= 0);
    int64_t p = (int64_t)a * rcp;
    p += (1LL << (rsh - 1)) + (p >> 63); /* 有符号四舍五入 */
    return (int32_t)(p >> rsh);
}

/* 建 RCP_BITS 可变的倒数表 */
static void build_rcp_tbl(int rcp_bits, uint32_t *tbl)
{
    assert(rcp_bits >= FIX_BITS_S && rcp_bits <= 31);
    tbl[0] = 0;
    for (int k = 1; k <= RCP_MAX; k++)
        tbl[k] = ((1u << rcp_bits) + (k >> 1)) / k;
}

/* 参数化 rgb2hsv v3（rcp_bits 可变；rcp 表与 RCP6 由调用方给定） */
static void rgb2hsv_v3_p(int32_t r, int32_t g, int32_t b, const uint32_t *rcp, int rcp_bits, int32_t *h14, int32_t *s11,
    int32_t *v10)
{
    int32_t M = MAX3(r, g, b);
    int32_t m = MIN3(r, g, b);
    int32_t C = M - m;
    *v10 = M;
    *s11 = (C > 0) ? rcp_mul_rsh_p(C, rcp[M], rcp_bits - FIX_BITS_S) : 0;
    int32_t h = 0;
    if (C > 0) {
        int32_t aR = rcp_mul_rsh_p(g - b, rcp[C], rcp_bits - FIX_BITS_H);
        int32_t aG = rcp_mul_rsh_p(b - r, rcp[C], rcp_bits - FIX_BITS_H);
        int32_t aB = rcp_mul_rsh_p(r - g, rcp[C], rcp_bits - FIX_BITS_H);
        int32_t hR = rcp_mul_rsh_p(aR + (6 << FIX_BITS_H), RCP6, RCP6_BITS) & (FIX_H_ONE - 1);
        int32_t hG = rcp_mul_rsh_p(aG + (2 << FIX_BITS_H), RCP6, RCP6_BITS);
        int32_t hB = rcp_mul_rsh_p(aB + (4 << FIX_BITS_H), RCP6, RCP6_BITS);
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

/* clamp（复制 hsv_fixed.c 的 hsv2rgb_clamp_k） */
static int32_t clamp_k_p(int32_t k)
{
    int32_t t = k < 4 * FIX_H_ONE - k ? k : 4 * FIX_H_ONE - k;
    t = t < 0 ? 0 : t;
    t = t > FIX_H_ONE ? FIX_H_ONE : t;
    return t;
}

/* 参数化 hsv2rgb v3（vs_shift 可变） */
static void hsv2rgb_v3_p(int32_t H, int32_t S, int32_t V, int maxv, int vs_shift, int32_t *R, int32_t *G, int32_t *B)
{
    if (S == 0) {
        *R = *G = *B = V;
        return;
    }
    int32_t h6 = H * 6;
    int32_t k5 = 5 * FIX_H_ONE + h6;
    int32_t k3 = 3 * FIX_H_ONE + h6;
    int32_t k1 = 1 * FIX_H_ONE + h6;
    k5 = (k5 >= 6 * FIX_H_ONE) ? k5 - 6 * FIX_H_ONE : k5;
    k3 = (k3 >= 6 * FIX_H_ONE) ? k3 - 6 * FIX_H_ONE : k3;
    k1 = (k1 >= 6 * FIX_H_ONE) ? k1 - 6 * FIX_H_ONE : k1;
    int32_t t5 = clamp_k_p(k5);
    int32_t t3 = clamp_k_p(k3);
    int32_t t1 = clamp_k_p(k1);
    int32_t rs = FIX_BITS_H + FIX_BITS_S - vs_shift;
    int32_t vsq = (V * S + (1 << (vs_shift - 1))) >> vs_shift;
    int32_t r = V - (int32_t)((vsq * t5 + (1 << (rs - 1))) >> rs);
    int32_t g = V - (int32_t)((vsq * t3 + (1 << (rs - 1))) >> rs);
    int32_t b = V - (int32_t)((vsq * t1 + (1 << (rs - 1))) >> rs);
    *R = CLIP(r, 0, maxv);
    *G = CLIP(g, 0, maxv);
    *B = CLIP(b, 0, maxv);
}

/* 参数化往返最大误差（LSB）：给定 rcp_bits / vs_shift / bits 位深 / 步长 */
static int roundtrip_maxerr_p(int rcp_bits, int vs_shift, int bits, int stride)
{
    const int maxv = (1 << bits) - 1;
    uint32_t tbl[RCP_MAX + 1];
    build_rcp_tbl(rcp_bits, tbl);
    int maxerr = 0;
    for (int r = 0; r <= maxv; r += stride)
        for (int g = 0; g <= maxv; g += stride)
            for (int b = 0; b <= maxv; b += stride) {
                int32_t H, S, V, R, G, B;
                rgb2hsv_v3_p(r, g, b, tbl, rcp_bits, &H, &S, &V);
                hsv2rgb_v3_p(H, S, V, maxv, vs_shift, &R, &G, &B);
                int e = MAX3(abs((int)R - r), abs((int)G - g), abs((int)B - b));
                if (e > maxerr)
                    maxerr = e;
            }
    return maxerr;
}

/* 估算整套函数最大乘法器输入位宽（bit）：
   S=C/M: C(≤10bit)×rcp；diff/C: diff(≤11bit)×rcp；(a+6F)/6: ≤17bit×RCP6；vsq×t: ≤2^(21-vs)×2^14 */
static int mult_width(int rcp_bits, int vs_shift)
{
    int w_s = 0 + rcp_bits; /* 导数表是按U10做分母的，乘回U10最大值不会超过 2^rcp_bits */
    int w_a = 1 + rcp_bits; /* 多一个符号位 */
    int w_h = (FIX_BITS_H + 3) + RCP6_BITS;              /* /6的定点化 */
    int w_v = (10 + FIX_BITS_S - vs_shift) + FIX_BITS_H; /* hsv2rgb 内使用 */
    int m = MAX3(w_a, w_h, w_v);
    if (w_s > m)
        m = w_s;
    return m;
}

/* [8] 扫描 RCP_BITS：往返 0 损失的最小值（VS_SHIFT 固定当前值） */
static void test_rcp_scan(int step_u8, int step_u10)
{
    printf("\n[8] 扫描 RCP_BITS（VS_SHIFT=%d 固定，往返 0 损失的最小值，u8 步长=%d / u10 步长=%d）：\n", VS_SHIFT,
        step_u8, step_u10);
    int best = -1;
    for (int rb = FIX_BITS_S; rb <= 28; rb++) {
        int e8 = roundtrip_maxerr_p(rb, VS_SHIFT, 8, step_u8);
        int e10 = roundtrip_maxerr_p(rb, VS_SHIFT, 10, step_u10);
        int ok = (e8 == 0 && e10 == 0);
        if (ok && best < 0)
            best = rb;
        printf("    RCP_BITS=%2d -> u8 max|Δ|=%2d  u10 max|Δ|=%2d%s\n", rb, e8, e10, ok ? "  <== 0误差" : "");
    }
    printf("  => 往返 0 损失的最小 RCP_BITS = %d%s\n", best, best < 0 ? "（范围内未找到）" : "");
}

/* [9] 扫描 VS_SHIFT：往返 0 损失的最大值（RCP_BITS 固定当前值） */
static void test_vs_scan(int step_u8, int step_u10)
{
    printf("\n[9] 扫描 VS_SHIFT（RCP_BITS=%d 固定，往返 0 损失的最大值）：\n", RCP_BITS);
    int best = -1;
    for (int vs = 16; vs >= 4; vs--) { /* 从大到小，第一个 0 误差即最大 */
        int e8 = roundtrip_maxerr_p(RCP_BITS, vs, 8, step_u8);
        int e10 = roundtrip_maxerr_p(RCP_BITS, vs, 10, step_u10);
        int ok = (e8 == 0 && e10 == 0);
        if (ok && best < 0)
            best = vs;
        printf("    VS_SHIFT=%2d -> u8 max|Δ|=%2d  u10 max|Δ|=%2d%s\n", vs, e8, e10, ok ? "  <== 0误差" : "");
    }
    printf("  => 往返 0 损失的最大 VS_SHIFT = %d%s\n", best, best < 0 ? "（范围内未找到）" : "");
}

/* [10] (RCP_BITS, VS_SHIFT) 组合扫描：往返 0 损失下最大乘法器位宽最低（粗步长加速） */
static void test_combo_scan(int step_u8, int step_u10)
{
    printf("\n[10] (RCP_BITS, VS_SHIFT) 组合扫描：往返 0 损失下最大乘法器位宽最低\n");
    int s8 = (step_u8 > 16) ? step_u8 : 16; /* 粗步长：u8=16、u10=31，快 */
    int s10 = (step_u10 > 31) ? step_u10 : 31;
    int best_w = INT_MAX, best_rb = 0, best_vs = 0;
    for (int rb = FIX_BITS_S; rb <= 28; rb += 1)
        for (int vs = 4; vs <= 16; vs += 1) {
            int e8 = roundtrip_maxerr_p(rb, vs, 8, s8);
            int e10 = roundtrip_maxerr_p(rb, vs, 10, s10);
            if (e8 == 0 && e10 == 0) {
                int w = mult_width(rb, vs);
                if (w < best_w || (w == best_w && (rb + vs) > (best_rb + best_vs))) {
                    best_w = w;
                    best_rb = rb;
                    best_vs = vs;
                }
            }
            printf("  RCP_BITS=%2d, VS_SHIFT=%2d -> u8 max|Δ|=%2d  u10 max|Δ|=%2d%s\n", rb, vs, e8, e10,
                (e8 == 0 && e10 == 0) ? "  <== 0误差" : "");
        }
    if (best_rb) {
        printf("  => 最佳组合: RCP_BITS=%d, VS_SHIFT=%d，最大乘法器输入位宽=%d bit\n", best_rb, best_vs, best_w);
        printf("     （S=C/M:%d、diff/C:%d、h/6:%d、vsq*t:%d）\n", 10 + best_rb, 11 + best_rb, 17 + RCP6_BITS, 35 - best_vs);
    }
    else
        printf("  => 粗扫未找到 0 损失组合（需更细步长复核）\n");
}

/* [1][2][3] u8 量化精度分析（-s 指定后运行） */
static void test_u8_quant(int step_u8)
{
    const char *lab8 = (step_u8 == 1) ? "u8 全遍历" : (step_u8 <= 4 ? "u8 密抽样" : "u8 粗扫");
    float err_ratio = 0.f;
    int bs_alone = 0, bh_alone = 0, bs_need = 0, bh_need = 0;

    if (want(1)) {
        printf("[1] 只量化 S（H=20bit≈精确），%s：\n", lab8);
        for (int bs = 6; bs <= 13; bs++) {
            int e = eval_quant_u8(20, bs, step_u8, &err_ratio);
            printf("    S=%2d bit -> max|Δ|=%d LSB%s\n", bs, e, e ? "" : "  <== 零误差");
            if (e == 0 && !bs_alone)
                bs_alone = bs;
        }
    }
    if (want(2)) {
        printf("\n[2] 只量化 H（S=20bit≈精确），%s：\n", lab8);
        for (int bh = 8; bh <= 13; bh++) {
            int e = eval_quant_u8(bh, 20, step_u8, &err_ratio);
            printf("    H=%2d bit -> max|Δ|=%d LSB%s\n", bh, e, e ? "" : "  <== 零误差");
            if (e == 0 && !bh_alone)
                bh_alone = bh;
        }
    }
    if (want(3)) {
        /* 依赖 [1][2] 的单独零误差位宽定位边界；单独跑 [3] 时用已知兜底 11/9 */
        int bh0 = bh_alone ? bh_alone - 1 : 11;
        int bs0 = bs_alone ? bs_alone - 1 : 9;
        printf("\n[3] %s确认边界：\n", lab8);
        for (int bh = bh0; bh <= bh0 + 2; bh++)
            for (int bs = bs0; bs <= bs0 + 2; bs++) {
                int e = eval_quant_u8(bh, bs, step_u8, &err_ratio);
                printf("    (H=%2d, S=%2d) -> max|Δ|=%d LSB%s\n", bh, bs, e, e ? "" : "  <== 零误差");
            }
        for (int bh = bh0; bh <= bh0 + 2 && !bh_need; bh++)
            for (int bs = bs0; bs <= bs0 + 2; bs++)
                if (!bh_need && eval_quant_u8(bh, bs, step_u8, NULL) == 0) {
                    bh_need = bh;
                    bs_need = bs;
                }
        printf("  零误差最小组合 (H=%d, S=%d)，H+S >= 21 bit\n", bh_need, bs_need);
    }
}

/* [4][5][6] u10 量化精度分析（-S 指定后运行） */
static void test_u10_quant(int step_u10)
{
    const char *lab10 = (step_u10 == 1) ? "u10 全遍历" : (step_u10 <= 8 ? "u10 密抽样" : "u10 粗扫");
    float err_ratio = 0.f;
    int bs_alone10 = 0, bh_alone10 = 0, bs_need10 = 0, bh_need10 = 0;

    if (want(4)) {
        printf("[4] u10(10bit) 只量化 S（H=20bit≈精确），%s：\n", lab10);
        for (int bs = 8; bs <= 16; bs++) {
            int e = eval_quant_u10(20, bs, step_u10, &err_ratio);
            printf("    S=%2d bit -> max|Δ|=%d LSB%s\n", bs, e, e ? "" : "  <== 零误差");
            if (e == 0 && !bs_alone10)
                bs_alone10 = bs;
        }
    }
    if (want(5)) {
        printf("\n[5] u10(10bit) 只量化 H（S=20bit≈精确），%s：\n", lab10);
        for (int bh = 10; bh <= 16; bh++) {
            int e = eval_quant_u10(bh, 20, step_u10, &err_ratio);
            printf("    H=%2d bit -> max|Δ|=%d LSB%s\n", bh, e, e ? "" : "  <== 零误差");
            if (e == 0 && !bh_alone10)
                bh_alone10 = bh;
        }
    }
    if (want(6)) {
        int bh0 = bh_alone10 ? bh_alone10 - 1 : 13;
        int bs0 = bs_alone10 ? bs_alone10 - 1 : 11;
        printf("\n[6] u10 组合边界（%s）：\n", lab10);
        for (int bh = bh0; bh <= bh0 + 2; bh++)
            for (int bs = bs0; bs <= bs0 + 2; bs++) {
                int e = eval_quant_u10(bh, bs, step_u10, &err_ratio);
                printf("    (H=%2d, S=%2d) -> max|Δ|=%d LSB%s\n", bh, bs, e, e ? "" : "  <== 零误差");
            }
        for (int bh = bh0; bh <= bh0 + 2 && !bh_need10; bh++)
            for (int bs = bs0; bs <= bs0 + 2; bs++)
                if (!bh_need10 && eval_quant_u10(bh, bs, step_u10, NULL) == 0) {
                    bh_need10 = bh;
                    bs_need10 = bs;
                }
        printf("  零误差最小组合 (H=%d, S=%d)，H+S >= 25 bit\n", bh_need10, bs_need10);
    }
}

static void usage(const char *prog)
{
    printf("用法: %s [选项]\n", prog);
    printf("  -s <n>  u8 采样间隔 [1,16]，默认 3\n");
    printf("  -S <n>  u10 采样间隔 [1,32]，默认 7\n");
    printf("  -t <n1,n2,...> 指定运行用例列表（逗号分隔，缺省全跑）\n");
    printf("                -s/-S 仅设定采样间隔，不再触发量化用例；用例由 -t 控制\n");
    printf("  -h      帮助\n");
    printf("用例: [1]u8只量化S [2]u8只量化H [3]u8组合边界 [4]u10只量化S [5]u10只量化H\n");
    printf("      [6]u10组合边界 [7]定点往返(u8+u10) [8]RCP_BITS最小 [9]VS_SHIFT最大\n");
    printf("      [10](RCP_BITS,VS_SHIFT)最优组合(最大乘法位宽最低)\n");
}

int main(int argc, char **argv)
{
    int step_u8 = 3, step_u10 = 7;

    int opt;
    while ((opt = getopt(argc, argv, "s:S:t:h")) != -1) {
        switch (opt) {
        case 's':
            step_u8 = atoi(optarg);
            if (step_u8 < 1)
                step_u8 = 1;
            if (step_u8 > 16)
                step_u8 = 16;
            break;
        case 'S':
            step_u10 = atoi(optarg);
            if (step_u10 < 1)
                step_u10 = 1;
            if (step_u10 > 32)
                step_u10 = 32;
            break;
        case 't': {
            /* 逗号分隔的用例 id 列表，如 "1,2,3,7" */
            const char *p = (const char *)optarg;
            g_tn = 0;
            while (*p && g_tn < 16) {
                while (*p == ',' || *p == ' ' || *p == '\t')
                    p++;
                if (!*p)
                    break;
                char *end;
                long v = strtol(p, &end, 10);
                if (end == p)
                    break; /* 非法字符 */
                g_tids[g_tn++] = (int)v;
                p = end;
            }
            break;
        }
        case 'h':
        default:  usage(argv[0]); return (opt == 'h') ? 0 : 1;
        }
    }

    printf("== H/S 定点量化精度 vs rgb->hsv->rgb 往返误差 + 位宽参数扫描 ==\n");
    if (g_tn) {
        printf("（u8 步长=%d、u10 步长=%d；用例=", step_u8, step_u10);
        for (int i = 0; i < g_tn; i++)
            printf("%d%s", g_tids[i], i + 1 < g_tn ? "," : "");
        printf("）\n\n");
    }
    else
        printf("（u8 步长=%d、u10 步长=%d；用例=全跑）\n\n", step_u8, step_u10);

    if (want(1) || want(2) || want(3))
        test_u8_quant(step_u8);
    if (want(4) || want(5) || want(6))
        test_u10_quant(step_u10);

    if (want(7)) {
        printf("[7] 定点版往返精度（H=Q14/S=Q11 当前实现，u8 步长=%d / u10 步长=%d）：\n", step_u8, step_u10);
        eval_fixed_bits("u8  hsv_fixed（H=Q14/S=Q11）", 8, step_u8);
        eval_fixed_bits("u10 hsv_fixed（H=Q14/S=Q11）", 10, step_u10);
    }
    if (want(8))
        test_rcp_scan(step_u8, step_u10);
    if (want(9))
        test_vs_scan(step_u8, step_u10);
    if (want(10))
        test_combo_scan(step_u8, step_u10);

    return 0;
}
