#include "yuv_adjust.h"

#include <math.h>

/* Y2R 矩阵的 Cb/Cr 两列（Q14，1.0 = 2^14；Y 列恒为 1.0 故不存）。
   RGB_i = Y + (m[i][0]·Cb + m[i][1]·Cr)，CompLumaFirst 求 Y 的可行区间时用。
   数值与 src/csc/rockchip_post_csc2.c 的 fix14 矩阵同源（BT.709 逐项一致）。 */
static const int32_t s_y2r_cbcr_q14[3][3][2] = {
    /* BT.601 : R(0, 1.4020)      G(-0.344136, -0.714136)  B(1.7720, 0) */
    {{0, 22970}, {-5638, -11700}, {29032, 0}},
    /* BT.709 : R(0, 1.5748)      G(-0.187324, -0.468124)  B(1.8556, 0) */
    {{0, 25802}, {-3069, -7670}, {30402, 0}},
    /* BT.2020: R(0, 1.4746)      G(-0.164553, -0.571353)  B(1.8814, 0) */
    {{0, 24160}, {-2696, -9361}, {30825, 0}},
};

/* 单像素 YCbCr 域固定管线 BCSH（定点），见 yuv_adjust.h 说明：
     C(MulAtMidPoint) -> B(ModeAdd) -> S(ModeMul) -> H(ModeAdd) -> 色域处理
   Y 在 Q11 像素域做 contrast/brightness；(Cb,Cr) 先乘 ds（极径缩放）再按 angle
   旋转（极角加法），不需要 atan2/开方。 */
void adjust_yuv_fix(uint16_t y, int32_t cb, int32_t cr, uint16_t maxv, int32_t gain_c, int32_t delta_b,
    int32_t delta_s, int32_t angle_q14, int comp_luma_first, int cs, uint16_t *yo, int32_t *cbo, int32_t *cro)
{
    const int32_t cap_y = (int32_t)maxv << FIX_BITS_S;        /* maxv 的 Q11 像素域 */
    const int32_t half_y = (int32_t)maxv << (FIX_BITS_S - 1); /* maxv/2 的 Q11 像素域（mid 中点） */
    const int32_t cap_c = (int32_t)maxv << (FIX_BITS_S - 1);  /* 色度格式上限 maxv/2（Q11） */
    const int32_t gc = CLIP(gain_c, 0, 4 * FIX_S_ONE);
    const int32_t db = CLIP(delta_b, -FIX_S_ONE, FIX_S_ONE);
    const int32_t gs = CLIP(delta_s, 0, 4 * FIX_S_ONE);

    /* ---- 1. C（MulAtMidPoint 过 Y=0.5 中点乘法）：Y1 = clip((Y-0.5)·gc + 0.5) ---- */
    int32_t qy = CLIP(adj_mul_q(((int32_t)y << FIX_BITS_S) - half_y, gc, FIX_BITS_S) + half_y, 0, cap_y);

    /* ---- 2. B（ModeAdd 加性）：Y2 = clip(Y1 + db·maxv)（db 为归一化量，折算到像素域） ---- */
    qy = CLIP(qy + db * maxv, 0, cap_y);

    /* ---- 3. S（ModeMul）：(Cb,Cr) *= ds（色度向量缩放 = 极径乘 ds） ---- */
    int32_t qcb = adj_mul_q(cb * FIX_S_ONE, gs, FIX_BITS_S);
    int32_t qcr = adj_mul_q(cr * FIX_S_ONE, gs, FIX_BITS_S);

    /* ---- 4. H（ModeAdd 极角旋转）：θ' = θ + angle，等价于对色度向量做单位圆旋转 ---- */
    if (angle_q14 != 0) {
        const int32_t cos_q15 = adj_cos_q15(angle_q14);
        const int32_t sin_q15 = adj_sin_q15(angle_q14);
        const int32_t cb0 = qcb, cr0 = qcr;
        qcb = adj_mul_q(cos_q15, cb0, 15) - adj_mul_q(sin_q15, cr0, 15);
        qcr = adj_mul_q(sin_q15, cb0, 15) + adj_mul_q(cos_q15, cr0, 15);
    }

    /* ---- 5. 色域处理：CompLumaFirst（保极角亮度补偿）或硬钳 ---- */
    if (comp_luma_first) {
        const int cs_idx =
            (cs >= (int)ADJ_YUV_CS_BT601 && cs <= (int)ADJ_YUV_CS_BT2020) ? cs : (int)ADJ_YUV_CS_BT709;
        const int32_t(*m)[2] = s_y2r_cbcr_q14[cs_idx];
        /* k_i：Y2R 第 i 通道的色度贡献（Q11 像素域，即 RGB_i = (Y + k_i)/maxv） */
        const int32_t k_r = adj_mul_q(m[0][0], qcb, 14) + adj_mul_q(m[0][1], qcr, 14);
        const int32_t k_g = adj_mul_q(m[1][0], qcb, 14) + adj_mul_q(m[1][1], qcr, 14);
        const int32_t k_b = adj_mul_q(m[2][0], qcb, 14) + adj_mul_q(m[2][1], qcr, 14);
        /* 可行区间 [A, cap_y - B]：A = max_i(-k_i) = -min_i(k_i)，B = max_i(k_i) */
        const int32_t a_lo = -MIN3(k_r, k_g, k_b);
        const int32_t b_hi = MAX3(k_r, k_g, k_b);
        if (a_lo + b_hi <= cap_y) {
            qy = CLIP(qy, a_lo, cap_y - b_hi); /* 可行：只调 Y（色度不动） */
        }
        else {
            /* 不可行：色度缩到 r*=r·maxv/(A+B)，Y 顶到 Y*=A/(A+B)·maxv（落在色域边界） */
            const int32_t denom = a_lo + b_hi; /* > cap_y > 0 */
            const int32_t half_d = denom >> 1;
            qy = (int32_t)(((int64_t)a_lo * maxv * FIX_S_ONE + half_d) / denom);
            qcb = (int32_t)(((int64_t)qcb * maxv * FIX_S_ONE + half_d) / denom);
            qcr = (int32_t)(((int64_t)qcr * maxv * FIX_S_ONE + half_d) / denom);
        }
    }
    else {
        qcb = CLIP(qcb, -cap_c, cap_c);
        qcr = CLIP(qcr, -cap_c, cap_c);
    }

    /* ---- 输出：统一舍入回像素域（Cb/Cr 为去中心带符号值） ---- */
    *yo = (uint16_t)CLIP(adj_rsh_round(qy, FIX_BITS_S), 0, maxv);
    *cbo = adj_rsh_round(qcb, FIX_BITS_S);
    *cro = adj_rsh_round(qcr, FIX_BITS_S);
}

/* ---- 浮点参考实现（精度基准，无定点量化） ---- */
/* 与 adjust_yuv_fix 同语义（C -> B -> S -> H -> 色域处理），归一化域：
     Y∈[0,1]、Cb,Cr∈[-0.5,0.5]；C/B 逐步 clip01；S 为纯色度增益（不额外截断 r）；
     H 为极角旋转；末尾统一按 gamut 策略处理（HardClip 各自钳位 /
     CompLumaFirst 保极角补偿）。参数取物理量（与定点版同一套限幅）。 */
static inline float yuv_adj_clipf(float x, float lo, float hi) { return x < lo ? lo : (x > hi ? hi : x); }

/* Y2R 的 Cb/Cr 两列（float，与定点 Q14 表同源） */
static const float s_y2r_cbcr_f[3][3][2] = {
    {{0.0f, 1.402f}, {-0.344136f, -0.714136f}, {1.772f, 0.0f}},   /* BT.601 */
    {{0.0f, 1.5748f}, {-0.187324f, -0.468124f}, {1.8556f, 0.0f}}, /* BT.709 */
    {{0.0f, 1.4746f}, {-0.164553f, -0.571353f}, {1.8814f, 0.0f}}, /* BT.2020 */
};

void adjust_yuv_float(float y, float cb, float cr, float gain_c, float delta_b, float delta_s, float angle_deg,
    int comp_luma_first, int cs, float *yo, float *cbo, float *cro)
{
    const int cs_idx = (cs >= (int)ADJ_YUV_CS_BT601 && cs <= (int)ADJ_YUV_CS_BT2020) ? cs : (int)ADJ_YUV_CS_BT709;
    gain_c = yuv_adj_clipf(gain_c, 0.0f, 4.0f); /* 参数限幅与定点版一致 */
    delta_b = yuv_adj_clipf(delta_b, -1.0f, 1.0f);
    delta_s = yuv_adj_clipf(delta_s, 0.0f, 4.0f);

    /* 1. C（MulAtMidPoint）：Y1 = clip01((Y-0.5)·gc + 0.5) */
    y = yuv_adj_clipf((y - 0.5f) * gain_c + 0.5f, 0.0f, 1.0f);
    /* 2. B（ModeAdd）：Y2 = clip01(Y1 + db) */
    y = yuv_adj_clipf(y + delta_b, 0.0f, 1.0f);
    /* 3. S（ModeMul）：极径乘 ds */
    cb *= delta_s;
    cr *= delta_s;
    /* 4. H（ModeAdd）：极角旋转 angle_deg */
    if (angle_deg != 0.0f) {
        const float th = angle_deg * 0.01745329252f; /* π/180 */
        const float cf = cosf(th), sf = sinf(th);
        const float cb0 = cb, cr0 = cr;
        cb = cb0 * cf - cr0 * sf;
        cr = cb0 * sf + cr0 * cf;
    }
    /* 5. 色域处理 */
    if (comp_luma_first) {
        const float(*mf)[2] = s_y2r_cbcr_f[cs_idx];
        const float k_r = mf[0][0] * cb + mf[0][1] * cr;
        const float k_g = mf[1][0] * cb + mf[1][1] * cr;
        const float k_b = mf[2][0] * cb + mf[2][1] * cr;
        const float y_lo = -fminf(fminf(k_r, k_g), k_b);         /* A = max_i(-k_i) */
        const float y_hi = 1.0f - fmaxf(fmaxf(k_r, k_g), k_b);   /* 1 - B，B = max_i(k_i) */
        if (y_lo <= y_hi) {
            y = yuv_adj_clipf(yuv_adj_clipf(y, y_lo, y_hi), 0.0f, 1.0f); /* 可行：只调 Y */
        }
        else {
            const float inv = 1.0f / (y_lo + (1.0f - y_hi)); /* 1/(A+B) */
            y = y_lo * inv;                                  /* Y* = A/(A+B) */
            cb *= inv;
            cr *= inv;
        }
    }
    else {
        y = yuv_adj_clipf(y, 0.0f, 1.0f);
        cb = yuv_adj_clipf(cb, -0.5f, 0.5f);
        cr = yuv_adj_clipf(cr, -0.5f, 0.5f);
    }
    *yo = y;
    *cbo = cb;
    *cro = cr;
}
