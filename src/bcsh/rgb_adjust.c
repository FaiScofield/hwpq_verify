#include "rgb_adjust.h"


/* RGB 域直接 BCSH 调整（单像素），见 hsv_fixed.h 说明 */
void adjust_rgb_fix(uint16_t r, uint16_t g, uint16_t b, uint16_t maxv, int32_t gain_c, int32_t delta_b, int32_t delta_s,
    int32_t tolerance_s, int32_t angle_q14, int gray_coef, int mode_c, int mode_b, uint16_t *ro, uint16_t *go, uint16_t *bo)
{
    /* ---- mode_c 增益（Q11）：mid 取 [0,4]；tanslant 经 tan((c+1)π/4) 查表映射 ---- */
    int32_t gc;
    if (mode_c == ADJ_RGB_MODE_C_TANSLANT) {
        int32_t th = CLIP(gain_c, -FIX_S_ONE, FIX_S_ONE) + FIX_S_ONE; /* (c+1)π/4 ∈ [0,π/2]，Q14 */
        gc = g_adj_tan_q11[th];                                       /* th=4096（c=+1）已截断为 ADJ_TAN_CAP */
    }
    else {
        gc = CLIP(gain_c, 0, 4 * FIX_S_ONE);
    }

    /* ---- delta_b / delta_s 预处理 ---- */
    int32_t gv_q11 = CLIP(delta_b, 0, 4 * FIX_S_ONE);            /* mul 增益，中性 1.0 */
    int32_t d_q11 = CLIP(delta_b, 0, 2 * FIX_S_ONE) - FIX_S_ONE; /* rate2limit 的 db-1（Q11，中性 0） */
    int32_t scale_q11 = CLIP(delta_s, 0, 4 * FIX_S_ONE);         /* 灰阶混合增益，中性 1.0 */
    int32_t wR, wG, wB;
    if (gray_coef == ADJ_RGB_GRAY_BT601) {
        wR = ADJ_LUMA_BT601_R;
        wG = ADJ_LUMA_BT601_G;
        wB = ADJ_LUMA_BT601_B;
    }
    else if (gray_coef == ADJ_RGB_GRAY_BT2020) {
        wR = ADJ_LUMA_BT2020_R;
        wG = ADJ_LUMA_BT2020_G;
        wB = ADJ_LUMA_BT2020_B;
    }
    else {
        wR = ADJ_LUMA_BT709_R;
        wG = ADJ_LUMA_BT709_G;
        wB = ADJ_LUMA_BT709_B;
    }

    /* ---- V：逐通道 contrast + brightness（Q11 像素域，统一舍入在 S 后） ---- */
    int32_t r_v = adj_apply_v((int32_t)r << FIX_BITS_S, maxv, gc, gv_q11, d_q11, mode_b);
    int32_t g_v = adj_apply_v((int32_t)g << FIX_BITS_S, maxv, gc, gv_q11, d_q11, mode_b);
    int32_t b_v = adj_apply_v((int32_t)b << FIX_BITS_S, maxv, gc, gv_q11, d_q11, mode_b);

    /* ---- S：灰阶混合（Q11 像素域，scale 语义，始终生效） ---- */
    int32_t k1 = scale_q11;             /* scale Q11 */
    int32_t k0 = FIX_S_ONE - scale_q11; /* 1-scale Q11 */
    /* gray 保持 Q11 像素域：sum(r*w)/2^16（int64 累加 + 单次舍入，不先量化到整数） */
    int64_t gsum = (int64_t)r_v * wR + (int64_t)g_v * wG + (int64_t)b_v * wB;
    int32_t gray = (int32_t)((gsum + (1LL << (ADJ_LUMA_BITS - 1))) >> ADJ_LUMA_BITS);
    r_v = adj_mul_q(k1, r_v, FIX_BITS_S) + adj_mul_q(k0, gray, FIX_BITS_S);
    g_v = adj_mul_q(k1, g_v, FIX_BITS_S) + adj_mul_q(k0, gray, FIX_BITS_S);
    b_v = adj_mul_q(k1, b_v, FIX_BITS_S) + adj_mul_q(k0, gray, FIX_BITS_S);
    /* 统一舍入回像素域并 clamp（H 步输入需整数像素） */
    r_v = CLIP((r_v + (FIX_S_ONE >> 1)) >> FIX_BITS_S, 0, maxv);
    g_v = CLIP((g_v + (FIX_S_ONE >> 1)) >> FIX_BITS_S, 0, maxv);
    b_v = CLIP((b_v + (FIX_S_ONE >> 1)) >> FIX_BITS_S, 0, maxv);

    /* ---- H：ModeAdd 六边形色相加法（angle=0 恒等跳过）。
       一次 rgb2hsv 取六边形色相 H（M/m/C 不变 -> S/V 天然不变），平移后在 RGB 域
       按 6 段 TAB 重排中间通道（同 hsv2rgb_v4_hexwalk 模型），无需 hsv2rgb 重建 ---- */
    if (angle_q14 != 0) {
        /* per segment: [M channel, m channel, changing channel], 0/1/2 = R/G/B */
        static const uint8_t TAB[6][3] = {
            {0, 2, 1},
            {1, 2, 0},
            {1, 0, 2},
            {2, 0, 1},
            {2, 1, 0},
            {0, 1, 2},
        };
        const uint32_t *rcp6 = rcp6_tbl_u24_fixed(); /* H 表：H=diff/(6C)，C(Chroma) 索引，RCP6_BITS bit */

        /* 一次取调整后像素的六边形色相 H（M/m/C 用 r_v/g_v/b_v 算，避免混用原始输入） */
        int32_t M = MAX3(r_v, g_v, b_v); /* U10: [0, 1023] */
        int32_t m = MIN3(r_v, g_v, b_v); /* U10: [0, 1023] */
        int32_t C = M - m;               /* U10: [0, 1023], chroma（精确，非 S 量化） */
        int32_t H = 0;
        if (C > 0) {
            int32_t hR = (rcp_mul_rsh(g_v - b_v, rcp6[C], RCP6_BITS - FIX_BITS_H) + FIX_H_ONE) & (FIX_H_ONE - 1);
            int32_t hG = rcp_mul_rsh(b_v - r_v, rcp6[C], RCP6_BITS - FIX_BITS_H) + 5461; // U22 max
            int32_t hB = rcp_mul_rsh(r_v - g_v, rcp6[C], RCP6_BITS - FIX_BITS_H) + 10923;
            uint32_t mR = (uint32_t)(M == r_v);
            uint32_t mG = (uint32_t)(M == g_v) & ~mR;
            uint32_t mB = (uint32_t)(M == b_v) & ~(mR | mG);
            int32_t selR = (int32_t)(0u - mR);
            int32_t selG = (int32_t)(0u - mG);
            int32_t selB = (int32_t)(0u - mB);
            H = (hR & selR) | (hG & selG) | (hB & selB);

            H = (uint16_t)(((int32_t)H + angle_q14) & (FIX_H_ONE - 1));

            int32_t t = H * 6;                                    /* U14=>U17 */
            int32_t seg = t >> FIX_BITS_H;                        /* 60° node 0..5 */
            int32_t f14 = t & (FIX_H_ONE - 1);                    /* fraction inside the 60° segment */
            int32_t dm = (C * f14 + (FIX_H_ONE >> 1)) >> FIX_BITS_H;
            int32_t mid = (seg & 1) ? (M - dm) : (m + dm);
            int32_t ch[3] = {m, m, m};
            ch[TAB[seg][0]] = M;
            ch[TAB[seg][2]] = mid;
            r_v = CLIP(ch[0], 0, maxv);
            g_v = CLIP(ch[1], 0, maxv);
            b_v = CLIP(ch[2], 0, maxv);
        }
    }

    *ro = (uint16_t)r_v;
    *go = (uint16_t)g_v;
    *bo = (uint16_t)b_v;
}
