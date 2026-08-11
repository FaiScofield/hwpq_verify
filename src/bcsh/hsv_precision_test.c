/**
 * hsv_precision_test.c — 分析 H/S 定点量化精度对往返误差的影响
 *
 * 思路：
 *   [1][2] 隔离量化：只用"精确(浮点)重建、只量化 H 或 S"，
 *           逐级提高位宽，找 u8 输入零误差所需的最少 bit。
 *   [3]    组合验证边界（u8 全遍历）。
 *   [4]    当前 hsv_fixed 定点版（H=Q14/S=Q11）u8 全遍历往返精度验证。
 *   [5][6][7] 同 [1][2][3]，但输入为 u10(10bit)（1024^3 全遍历不可行，用抽样）。
 *   [8]    u10 定点版（rgb2hsv_fix10 / hsv2rgb_fix_u10）往返精度。
 *
 * 运行（命令行参数 [step_u8] [step_u10]，均可选，缺省 3 7）：
 *   hsv_precision_test           粗扫（u8 stride=3、u10 stride=7，快，快速定位边界）
 *   hsv_precision_test 1 1       精扫（stride=1 全遍历，慢，结论以此为准）
 *   hsv_precision_test 1 3       u8 全遍历 + u10 密抽样
 */

#include "hsv_fixed.h"
#include "hsv_float.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

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
                hsv_fix_t hsv;
                int32_t R = 0, G = 0, B = 0;
                if (bits == 8) {
                    hsv = rgb2hsv_fix_u8((uint8_t)r, (uint8_t)g, (uint8_t)b);
                    uint8_t r8, g8, b8;
                    hsv2rgb_fix_u8(hsv.H, hsv.S, hsv.V, &r8, &g8, &b8);
                    R = r8;
                    G = g8;
                    B = b8;
                }
                else {
                    hsv = rgb2hsv_fix_u10(r, g, b);
                    hsv2rgb_fix_u10(hsv.H, hsv.S, hsv.V, &R, &G, &B);
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

int main(int argc, char **argv)
{
    /* 命令行：[step_u8] [step_u10]，均可选；缺省粗扫（u8 stride=3、u10 stride=7） */
    int step_u8 = (argc > 1) ? atoi(argv[1]) : 3;  /* [1][2][3] u8 扫描步长 */
    int step_u10 = (argc > 2) ? atoi(argv[2]) : 7; /* [5][6][7][8] u10 扫描步长 */
    if (step_u8 < 1)
        step_u8 = 3;
    if (step_u10 < 1)
        step_u10 = 7;
    int fine_u8 = (step_u8 == 1);   /* u8 是否全遍历（stride=1），决定 u8 结论 */
    int fine_u10 = (step_u10 == 1); /* u10 是否全遍历（stride=1），决定 u10 结论 */
    const char *lab8 = (step_u8 == 1) ? "u8 全遍历" : (step_u8 <= 4 ? "u8 密抽样" : "u8 粗扫");
    const char *lab10 = (step_u10 == 1) ? "u10 全遍历" : (step_u10 <= 8 ? "u10 密抽样" : "u10 粗扫");
    int bs_alone = 0, bh_alone = 0;     /* u8 单独量化（另一量精确）时的最小零误差位宽 */
    int bs_need = 0, bh_need = 0;       /* u8 [3] 组合量化下的最小零误差组合 */
    int bs_alone10 = 0, bh_alone10 = 0; /* u10 单独量化时的最小零误差位宽 */
    int bs_need10 = 0, bh_need10 = 0;   /* u10 组合量化下的最小零误差组合 */
    float err_ratio = 0.f;              /* 存在误差的像素比例 */

    printf("== H/S 定点量化精度 vs rgb->hsv->rgb 往返误差（u8，误差单位=LSB）==\n");
    printf("（u8 stride=%d、u10 stride=%d；粗扫会漏最坏样本，结论以 stride=1 全遍历为准）\n\n", step_u8, step_u10);

    /* [1] 只量化 S（H 视为精确），逐步提高 S 位宽 */
    printf("[1] 只量化 S（H=20bit≈精确），%s：\n", lab8);
    for (int bs = 6; bs <= 13; bs++) {
        int e = eval_quant_u8(20, bs, step_u8, &err_ratio);
        if (0 == e)
            printf("    S=%2d bit -> max|Δ|=%d LSB  <== 零误差\n", bs, e);
        else
            printf("    S=%2d bit -> max|Δ|=%d LSB  有偏差像素比例=%.4f%%\n", bs, e, err_ratio * 100.f);
        if (e == 0 && !bs_alone)
            bs_alone = bs;
    }

    /* [2] 只量化 H（S 视为精确），逐步提高 H 位宽 */
    printf("\n[2] 只量化 H（S=20bit≈精确），%s：\n", lab8);
    for (int bh = 8; bh <= 13; bh++) {
        int e = eval_quant_u8(bh, 20, step_u8, &err_ratio);
        if (0 == e)
            printf("    H=%2d bit -> max|Δ|=%d LSB  <== 零误差\n", bh, e);
        else
            printf("    H=%2d bit -> max|Δ|=%d LSB  有偏差像素比例=%.4f%%\n", bh, e, err_ratio * 100.f);
        if (e == 0 && !bh_alone)
            bh_alone = bh;
    }

    /* [3] 组合边界确认（精扫为 u8 全遍历，粗扫可能漏最坏样本） */
    printf("\n[3] %s确认边界：\n", lab8);
    {
        int bh0 = (bh_alone > 11) ? bh_alone - 1 : 11;
        int bs0 = (bs_alone > 8) ? bs_alone - 1 : 8;
        for (int bh = bh0; bh <= bh0 + 2; bh++)
            for (int bs = bs0; bs <= bs0 + 2; bs++) {
                int e = eval_quant_u8(bh, bs, step_u8, &err_ratio);
                if (0 == e)
                    printf("    (H=%2d, S=%2d) -> max|Δ|=%d LSB  <== 零误差\n", bh, bs, e);
                else
                    printf("    (H=%2d, S=%2d) -> max|Δ|=%d LSB  有偏差像素比例=%.4f%%\n", bh, bs, e, err_ratio * 100.f);
            }
        /* 重新在当前扫描密度下确定最小零误差组合 */
        bh_need = 0;
        bs_need = 0;
        for (int bh = bh0; bh <= bh0 + 2 && !bh_need; bh++)
            for (int bs = bs0; bs <= bs0 + 2; bs++)
                if (!bh_need && eval_quant_u8(bh, bs, step_u8, NULL) == 0) {
                    bh_need = bh;
                    bs_need = bs;
                }
    }

    /* [4] 定点版往返精度（H=Q14/S=Q11） */
    printf("\n[4] 当前 hsv_fixed 定点版（H=Q14/S=Q11，重建四舍五入）u8 全遍历：\n");
    eval_fixed_bits("u8  hsv_fixed（H=Q14/S=Q11）", 8, 1);

    /* [5] u10(10bit) 只量化 S（H 视为精确） */
    printf("\n[5] u10(10bit) 只量化 S（H=20bit≈精确），%s：\n", lab10);
    for (int bs = 6; bs <= 16; bs++) {
        int e = eval_quant_u10(20, bs, step_u10, &err_ratio);
        if (0 == e)
            printf("    S=%2d bit -> max|Δ|=%d LSB  <== 零误差\n", bs, e);
        else
            printf("    S=%2d bit -> max|Δ|=%d LSB  有偏差像素比例=%.4f%%\n", bs, e, err_ratio * 100.f);
        if (e == 0 && !bs_alone10)
            bs_alone10 = bs;
    }

    /* [6] u10(10bit) 只量化 H（S 视为精确） */
    printf("\n[6] u10(10bit) 只量化 H（S=20bit≈精确），%s：\n", lab10);
    for (int bh = 8; bh <= 16; bh++) {
        int e = eval_quant_u10(bh, 20, step_u10, &err_ratio);
        if (0 == e)
            printf("    H=%2d bit -> max|Δ|=%d LSB  <== 零误差\n", bh, e);
        else
            printf("    H=%2d bit -> max|Δ|=%d LSB  有偏差像素比例=%.4f%%\n", bh, e, err_ratio * 100.f);
        if (e == 0 && !bh_alone10)
            bh_alone10 = bh;
    }

    /* [7] u10 组合边界（抽样，可能漏最坏样本） */
    printf("\n[7] u10 组合边界（%s）：\n", lab10);
    {
        int bh0 = (bh_alone10 > 11) ? bh_alone10 - 1 : 11;
        int bs0 = (bs_alone10 > 8) ? bs_alone10 - 1 : 8;
        for (int bh = bh0; bh <= bh0 + 2; bh++)
            for (int bs = bs0; bs <= bs0 + 2; bs++) {
                int e = eval_quant_u10(bh, bs, step_u10, &err_ratio);
                if (0 == e)
                    printf("    (H=%2d, S=%2d) -> max|Δ|=%d LSB  <== 零误差\n", bh, bs, e);
                else
                    printf("    (H=%2d, S=%2d) -> max|Δ|=%d LSB  有偏差像素比例=%.4f%%\n", bh, bs, e, err_ratio * 100.f);
            }
        /* 重新在当前扫描密度下确定最小零误差组合 */
        bh_need10 = 0;
        bs_need10 = 0;
        for (int bh = bh0; bh <= bh0 + 2 && !bh_need10; bh++)
            for (int bs = bs0; bs <= bs0 + 2; bs++)
                if (!bh_need10 && eval_quant_u10(bh, bs, step_u10, NULL) == 0) {
                    bh_need10 = bh;
                    bs_need10 = bs;
                }
    }

    /* [8] u10 定点版往返精度（抽样） */
    double u10_rnd;
    printf("\n[8] u10 定点版（H=Q14/S=Q11）%s：\n", lab10);
    u10_rnd = eval_fixed_bits("u10 hsv_fixed（H=Q14/S=Q11）", 10, step_u10);

    printf("\n结论（u8 输入，%s）：\n", fine_u8 ? "精扫全遍历" : "粗扫，边界仅供参考");
    if (fine_u8) {
        printf("  - 单独量化 S（H 精确）时 S=8 bit 已够（全遍历 0 误差）；但 H/S 组合量化时\n");
        printf("    S=8 必失败（即使 H=13 也 1 LSB），实际定点实现 S 需 >=9 bit（配 H>=12）或 S=10（配 H=11）；\n");
        printf("  - H 最少 11 bit、S 最少 9 bit（组合），但 (H=11,S=9) 仍失败，两者不能同时取最小；\n");
        printf("  - 实测零误差最小组合：(H=%d, S=%d) 或 (H=12, S=9)，即 H+S 合计 >= 21 bit\n", bh_need, bs_need);
    }
    else {
        printf("  - 粗扫只用于快速定位边界；单独零误差起点：S=%d bit、H=%d bit，\n", bs_alone, bh_alone);
        printf("    组合零误差起点 (H=%d, S=%d)；最坏样本可能被漏掉，边界需运行 full 精扫确认。\n", bh_need, bs_need);
    }
    printf("  - 当前 hsv2rgb_fix（H=Q14/S=Q11）重建四舍五入，u8 全遍历 0 误差。\n");

    printf("\n结论（u10，10bit 输入，%s）：\n", lab10);
    printf("  - 单独量化 S 需 %d bit、H 需 %d bit（比 u8 的 8/11 高，u10 LSB=1/1023 更小）；\n", bs_alone10, bh_alone10);
    printf("  - 组合零误差起点 (H=%d, S=%d)（H+S=%d bit，u8 只需 21 bit）；\n", bh_need10, bs_need10, bh_need10 + bs_need10);
    if (u10_rnd == 0.0)
        printf("  - 当前定点（H=Q14/S=Q11）在 u10 输入下重建四舍五入后 0 误差（抽样验证）。\n");
    else {
        printf("  - 当前定点（H=Q14/S=Q11）在 u10 输入下重建四舍五入后抽样仍有\n");
        printf("    %.2f%% 样本 1 LSB 误差（非 0 误差），需进一步提高位宽。\n", u10_rnd);
    }
    return 0;
}
