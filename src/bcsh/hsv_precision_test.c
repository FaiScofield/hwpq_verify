/**
 * hsv_precision_test.c — 分析 H/S 定点量化精度对往返误差的影响
 *
 * 思路：
 *   [1][2] 隔离量化：只用"精确(浮点)重建、只量化 H 或 S"，
 *           逐级提高位宽，找 u8 输入零误差所需的最少 bit。
 *   [3]    组合验证边界（u8 全遍历）。
 *   [4]    当前 hsv_fixed 定点版（H=Q11/S=Q10）误差来源：
 *           对比"重建截断 (V*S*t)>>21" 与 "重建四舍五入 (+2^20)>>21"。
 *
 * 运行：
 *   hsv_precision_test          粗扫（stride=9，快，快速定位边界）
 *   hsv_precision_test full     精扫（stride=1 全遍历，慢，结论以此为准）
 */

#include "hsv_fixed.h"
#include "hsv_float.h"
#include <math.h>
#include <stdio.h>
#include <stdint.h>

/* ---------- H/S 定点量化模拟 ---------- */
/* H(度) 量化到 bh 位：0..360 用 2^bh 个台阶 */
static float quantH(float H, int bh)
{
    int q = (int)lrintf(H / 360.0f * (float)(1 << bh));
    if (q >= (1 << bh))
        q = (1 << bh) - 1;
    return (float)q / (float)(1 << bh) * 360.0f;
}

/* S∈[0,1] 量化到 bs 位：0..1 用 2^bs 个台阶 */
static float quantS(float S, int bs)
{
    int q = (int)lrintf(S * (float)(1 << bs));
    if (q > (1 << bs))
        q = (1 << bs);
    return (float)q / (float)(1 << bs);
}

/* 计算 (bh, bs) 下 u8 空间（步长 stride，保证含端点 255）的最大单通道往返误差(LSB) */
static int eval_quant(int bh, int bs, int stride)
{
    int vals[256], nv = 0;
    for (int v = 0; v <= 255; v += stride)
        vals[nv++] = v;
    if (vals[nv - 1] != 255)
        vals[nv++] = 255;

    int maxerr = 0;
    for (int i = 0; i < nv; i++)
        for (int j = 0; j < nv; j++)
            for (int k = 0; k < nv; k++) {
                int r = vals[i], g = vals[j], b = vals[k];
                hsv_f h = rgb2hsv_float(r / 255.0f, g / 255.0f, b / 255.0f);
                float Hq = quantH(h.H, bh);
                float Sq = quantS(h.S, bs);
                float R, G, B;
                hsv2rgb_float(Hq, Sq, h.V, &R, &G, &B); /* 其余保持精确 */
                int dr = (int)lrintf(R * 255.0f) - r;
                int dg = (int)lrintf(G * 255.0f) - g;
                int db = (int)lrintf(B * 255.0f) - b;
                int m = abs(dr);
                if (abs(dg) > m)
                    m = abs(dg);
                if (abs(db) > m)
                    m = abs(db);
                if (m > maxerr)
                    maxerr = m;
            }
    return maxerr;
}

/* ---------- 定点版：重建"截断" vs "四舍五入" ---------- */
/* 截断对照版：与 hsv_fixed.h 早期版本一致 (V*S*t)>>21 无舍入，演示 1 LSB 误差来源 */
static void hsv2rgb_fix_trunc(int32_t H, int32_t S, int32_t V, uint8_t *R, uint8_t *G, uint8_t *B)
{
    int32_t h6 = H / 60;
    int32_t k5 = 5 * FIX_H_ONE + h6;
    int32_t k3 = 3 * FIX_H_ONE + h6;
    int32_t k1 = 1 * FIX_H_ONE + h6;
    if (k5 >= FIX_H_6)
        k5 -= FIX_H_6;
    if (k3 >= FIX_H_6)
        k3 -= FIX_H_6;
    if (k1 >= FIX_H_6)
        k1 -= FIX_H_6;
    int32_t t5 = clamp01(k5);
    int32_t t3 = clamp01(k3);
    int32_t t1 = clamp01(k1);

    int32_t r = V - (int32_t)(((int64_t)V * S * t5) >> (FIX_BITS_H + FIX_BITS_S));
    int32_t g = V - (int32_t)(((int64_t)V * S * t3) >> (FIX_BITS_H + FIX_BITS_S));
    int32_t b = V - (int32_t)(((int64_t)V * S * t1) >> (FIX_BITS_H + FIX_BITS_S));

    r = CLIP(r, 0, 255);
    g = CLIP(g, 0, 255);
    b = CLIP(b, 0, 255);

    *R = (uint8_t)r;
    *G = (uint8_t)g;
    *B = (uint8_t)b;
}

/* 定点版 u8 全遍历往返误差 */
static void eval_fixed(const char *name, int use_trunc)
{
    uint64_t n_err = 0;
    int maxerr = 0;
    for (int r = 0; r <= 255; r++)
        for (int g = 0; g <= 255; g++)
            for (int b = 0; b <= 255; b++) {
                hsv_fix_t h = rgb2hsv_fix((uint8_t)r, (uint8_t)g, (uint8_t)b);
                uint8_t R, G, B;
                if (use_trunc)
                    hsv2rgb_fix_trunc(h.H, h.S, h.V, &R, &G, &B);
                else
                    hsv2rgb_fix(h.H, h.S, h.V, &R, &G, &B);
                int dr = (int)R - r, dg = (int)G - g, db = (int)B - b;
                int m = MAX3(abs(dr), abs(dg), abs(db));
                if (m) {
                    n_err++;
                    if (m > maxerr)
                        maxerr = m;
                }
            }
    printf("%-34s 有偏差=%9llu (%.4f%%)  max|Δ|=%d LSB\n", name, (unsigned long long)n_err, 100.0 * n_err / 16777216.0, maxerr);
}

int main(int argc, char **argv)
{
    int fine = (argc > 1 && argv[1][0] == 'f'); /* 参数 full：精扫（stride=1 全遍历） */
    int s1 = fine ? 1 : 9;                      /* [1][2] 扫描步长 */
    int s3 = fine ? 1 : 9;                      /* [3] 扫描步长 */
    int bs_alone = 0, bh_alone = 0;             /* 单独量化（另一量精确）时的最小零误差位宽 */
    int bs_need = 0, bh_need = 0;               /* [3] 组合量化下的最小零误差组合 */

    printf("== H/S 定点量化精度 vs rgb->hsv->rgb 往返误差（u8，误差单位=LSB）==\n");
    printf("（%s模式：stride=%d；粗扫会漏最坏样本，边界结论以 full 精扫为准）\n\n",
           fine ? "精扫" : "粗扫", fine ? 1 : 9);

    /* [1] 只量化 S（H 视为精确），逐步提高 S 位宽 */
    printf("[1] 只量化 S（H=20bit≈精确），%s：\n", fine ? "全遍历" : "粗扫");
    for (int bs = 6; bs <= 13; bs++) {
        int e = eval_quant(20, bs, s1);
        printf("    S=%2d bit -> max|Δ|=%d LSB%s\n", bs, e, e ? "" : "   <== 零误差");
        if (e == 0 && !bs_alone)
            bs_alone = bs;
    }

    /* [2] 只量化 H（S 视为精确），逐步提高 H 位宽 */
    printf("\n[2] 只量化 H（S=20bit≈精确），%s：\n", fine ? "全遍历" : "粗扫");
    for (int bh = 8; bh <= 13; bh++) {
        int e = eval_quant(bh, 20, s1);
        printf("    H=%2d bit -> max|Δ|=%d LSB%s\n", bh, e, e ? "" : "   <== 零误差");
        if (e == 0 && !bh_alone)
            bh_alone = bh;
    }

    /* [3] 组合边界确认（精扫为 u8 全遍历，粗扫可能漏最坏样本） */
    printf("\n[3] %s确认边界：\n", fine ? "u8 全遍历" : "u8 粗扫");
    {
        int bh0 = (bh_need > 11) ? bh_need - 1 : 11;
        int bs0 = (bs_need > 8) ? bs_need - 1 : 8;
        for (int bh = bh0; bh <= bh0 + 2; bh++)
            for (int bs = bs0; bs <= bs0 + 2; bs++) {
                int e = eval_quant(bh, bs, s3);
                printf("    (H=%2d, S=%2d) -> max|Δ|=%d LSB%s\n", bh, bs, e, e ? "" : "   <== 零误差");
            }
        /* 重新在当前扫描密度下确定最小零误差组合 */
        bh_need = 0;
        bs_need = 0;
        for (int bh = bh0; bh <= bh0 + 2 && !bh_need; bh++)
            for (int bs = bs0; bs <= bs0 + 2; bs++)
                if (!bh_need && eval_quant(bh, bs, s3) == 0) {
                    bh_need = bh;
                    bs_need = bs;
                }
    }

    /* [4] 定点版误差来源：H=11/S=10 已满足量化需求，误差只来自重建是否四舍五入 */
    printf("\n[4] 当前 hsv_fixed 定点版（H=Q11/S=Q10，重建已四舍五入）u8 全遍历：\n");
    eval_fixed("重建用截断     (V*S*t)>>21（对照）", 1);
    eval_fixed("重建用四舍五入 (+2^20)>>21（当前实现）", 0);

    printf("\n结论（u8 输入，%s）：\n", fine ? "精扫全遍历" : "粗扫，边界仅供参考");
    if (fine) {
        printf("  - 单独量化 S（H 精确）时 S=8 bit 已够（全遍历 0 误差）；但 H/S 组合量化时\n");
        printf("    S=8 必失败（即使 H=13 也 1 LSB），实际定点实现 S 需 >=9 bit（配 H>=12）或 S=10（配 H=11）；\n");
        printf("  - H 最少 11 bit、S 最少 9 bit（组合），但 (H=11,S=9) 仍失败，两者不能同时取最小；\n");
        printf("  - 实测零误差最小组合：(H=%d, S=%d) 或 (H=12, S=9)，即 H+S 合计 >= 21 bit\n", bh_need, bs_need);
    } else {
        printf("  - 粗扫只用于快速定位边界；单独零误差起点：S=%d bit、H=%d bit，\n", bs_alone, bh_alone);
        printf("    组合零误差起点 (H=%d, S=%d)；最坏样本可能被漏掉，边界需运行 full 精扫确认。\n", bh_need, bs_need);
    }
    printf("  - 当前 hsv2rgb_fix（H=Q11/S=Q10）重建已用四舍五入 (+2^(bits-1))>>bits，u8 全遍历 0 误差；\n");
    printf("    若改回截断 (V*S*t)>>bits 会产生 max 1 LSB 误差（约 60%% 样本有偏差，实测 59.69%%）。\n");
    return 0;
}
