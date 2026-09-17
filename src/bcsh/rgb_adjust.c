#include <math.h>

#include "rgb_adjust.h"

#ifndef RCP6_BITS
#define RCP6_BITS 24
#endif

/* RGB 域直接 BCSH 调整（单像素），见 hsv_fixed.h 说明 */
void adjust_rgb_fix(uint16_t r, uint16_t g, uint16_t b, uint16_t maxv, int32_t gain_c, int32_t delta_b, int32_t delta_s,
    int32_t tolerance_s, int32_t angle_q14, int gray_coef, int mode_c, int mode_b, int mode_h, uint16_t *ro,
    uint16_t *go, uint16_t *bo)
{
    (void)tolerance_s; /* 保留参数位，RGB 域 S 步为灰阶混合（Python 侧该门控已注释掉） */

    /* ---- mode_c 增益（Q11）：mid/zero/both 取 [0,4]；tanslant 经 tan((c+1)π/4) 查表映射 ---- */
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
    int32_t db_q11 = CLIP(delta_b, -FIX_S_ONE, FIX_S_ONE);       /* add 的 db（Q11，中性 0） */
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
    else if (gray_coef == ADJ_RGB_GRAY_P3) {
        wR = ADJ_LUMA_P3_R;
        wG = ADJ_LUMA_P3_G;
        wB = ADJ_LUMA_P3_B;
    }
    else {
        wR = ADJ_LUMA_BT709_R;
        wG = ADJ_LUMA_BT709_G;
        wB = ADJ_LUMA_BT709_B;
    }

    /* ---- V：逐通道先 brightness(mode_b) 后 contrast(mode_c)（Q11 像素域，统一舍入在 S 后） ---- */
    int32_t r_v = adj_apply_v((int32_t)r << FIX_BITS_S, maxv, gc, mode_c, gv_q11, d_q11, db_q11, mode_b);
    int32_t g_v = adj_apply_v((int32_t)g << FIX_BITS_S, maxv, gc, mode_c, gv_q11, d_q11, db_q11, mode_b);
    int32_t b_v = adj_apply_v((int32_t)b << FIX_BITS_S, maxv, gc, mode_c, gv_q11, d_q11, db_q11, mode_b);

    /* ---- S：灰阶混合（Q11 像素域，scale 语义，始终生效） ---- */
    int32_t k1 = scale_q11;             /* scale Q11 */
    int32_t k0 = FIX_S_ONE - scale_q11; /* 1-scale Q11 */
    /* gray 保持 Q11 像素域：sum(r*w)/2^16（int64 累加 + 单次舍入，不先量化到整数） */
    int64_t gsum = (int64_t)r_v * wR + (int64_t)g_v * wG + (int64_t)b_v * wB;
    int32_t gray = (int32_t)((gsum + (1LL << (ADJ_LUMA_BITS - 1))) >> ADJ_LUMA_BITS);
    r_v = adj_mul_q(k1, r_v, FIX_BITS_S) + adj_mul_q(k0, gray, FIX_BITS_S);
    g_v = adj_mul_q(k1, g_v, FIX_BITS_S) + adj_mul_q(k0, gray, FIX_BITS_S);
    b_v = adj_mul_q(k1, b_v, FIX_BITS_S) + adj_mul_q(k0, gray, FIX_BITS_S);

    /* ---- H（angle=0 恒等跳过） ----
       'rotategray'：绕灰轴 (1,1,1)/√3 旋转。在 Q11 域对**未钳位**的 S 步输出旋转
       （与浮点参考一致：Python 在 rgb_s 上旋转，末尾才统一 clip）。
       'add'：六边形色相加法，需整数像素 —— 先统一舍入回像素域并 clamp。 ---- */
    if (mode_h == ADJ_RGB_MODE_H_ROTATEGRAY) {
        if (angle_q14 != 0)
            rgb_adj_rotate_on_gray_q11(&r_v, &g_v, &b_v, angle_q14);
        r_v = CLIP((r_v + (FIX_S_ONE >> 1)) >> FIX_BITS_S, 0, maxv);
        g_v = CLIP((g_v + (FIX_S_ONE >> 1)) >> FIX_BITS_S, 0, maxv);
        b_v = CLIP((b_v + (FIX_S_ONE >> 1)) >> FIX_BITS_S, 0, maxv);
    }
    else {
        /* 统一舍入回像素域并 clamp（H 步输入需整数像素） */
        r_v = CLIP((r_v + (FIX_S_ONE >> 1)) >> FIX_BITS_S, 0, maxv);
        g_v = CLIP((g_v + (FIX_S_ONE >> 1)) >> FIX_BITS_S, 0, maxv);
        b_v = CLIP((b_v + (FIX_S_ONE >> 1)) >> FIX_BITS_S, 0, maxv);

        /* ---- H：ModeAdd 六边形色相加法。
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

                int32_t t = H * 6;                 /* U14=>U17 */
                int32_t seg = t >> FIX_BITS_H;     /* 60° node 0..5 */
                int32_t f14 = t & (FIX_H_ONE - 1); /* fraction inside the 60° segment */
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
    }

    *ro = (uint16_t)r_v;
    *go = (uint16_t)g_v;
    *bo = (uint16_t)b_v;
}

/* Sonnoc 客户固定管线 RGB 域 BCSH（单像素），模式全部固定、无 mode 分支：
     B(add) -> C(GainAtZero) -> S(MixGray) -> H(RotateOnGray)
   与 adjust_rgb_fix(mode_c=ZERO, mode_b=ADD, mode_h=ROTATEGRAY) 逐位等价，
   用于 Sonnoc 竞品模拟（db 先于 gc 生效；B/C 为全图调整、S 为乘性灰阶混合、
   H 绕灰轴旋转）。

     gain_c    : Q11（1.0 = FIX_S_ONE）；过零点乘法增益 [0,4]，中性 1.0
     delta_b   : Q11（1.0 = FIX_S_ONE）；加性 [-1,1]，中性 0
     delta_s   : Q11（1.0 = FIX_S_ONE）；灰阶混合 scale [0,4]，中性 1.0
     angle_q14 : Q14（360° = FIX_H_ONE）；绕灰轴旋转角，0 恒等跳过
     gray_coef : ADJ_RGB_GRAY_BT601 / BT709 / BT2020 / P3（MixGray 的 luma 系数）
   像素域 [0, maxv]（u8: 255 / u10: 1023），内部统一 Q11（pixel<<11）运算。 */
void adjust_rgb_sonnoc_fix(uint16_t r, uint16_t g, uint16_t b, uint16_t maxv, int32_t gain_c, int32_t delta_b,
    int32_t delta_s, int32_t angle_q14, int gray_coef, uint16_t *ro, uint16_t *go, uint16_t *bo)
{
    const int32_t cap = (int32_t)maxv << FIX_BITS_S; /* maxv 的 Q11 像素域表示 */
    const int32_t gc = CLIP(gain_c, 0, 4 * FIX_S_ONE);
    const int32_t db_q11 = CLIP(delta_b, -FIX_S_ONE, FIX_S_ONE);
    const int32_t sc = CLIP(delta_s, 0, 4 * FIX_S_ONE);
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
    else if (gray_coef == ADJ_RGB_GRAY_P3) {
        wR = ADJ_LUMA_P3_R;
        wG = ADJ_LUMA_P3_G;
        wB = ADJ_LUMA_P3_B;
    }
    else {
        wR = ADJ_LUMA_BT709_R;
        wG = ADJ_LUMA_BT709_G;
        wB = ADJ_LUMA_BT709_B;
    }

    /* ---- 1. B（add 加性）：x' = clip(x + db·maxv)（db 为归一化量，折算到 Q11 像素域） ---- */
    const int32_t off_q11 = db_q11 * maxv;
    int32_t qr = CLIP(((int32_t)r << FIX_BITS_S) + off_q11, 0, cap);
    int32_t qg = CLIP(((int32_t)g << FIX_BITS_S) + off_q11, 0, cap);
    int32_t qb = CLIP(((int32_t)b << FIX_BITS_S) + off_q11, 0, cap);

    /* ---- 2. C（GainAtZero 过零点乘法）：x'' = clip(gc·x')；作用在 B 之后 -> B 的幅度受 C 缩放 ---- */
    qr = CLIP(adj_mul_q(qr, gc, FIX_BITS_S), 0, cap);
    qg = CLIP(adj_mul_q(qg, gc, FIX_BITS_S), 0, cap);
    qb = CLIP(adj_mul_q(qb, gc, FIX_BITS_S), 0, cap);

    /* ---- 3. S（MixGray 灰阶混合）：out = scale·in + (1-scale)·gray，gray = luma(in)，单次舍入 ---- */
    const int64_t gsum = (int64_t)qr * wR + (int64_t)qg * wG + (int64_t)qb * wB;
    const int32_t gray = (int32_t)((gsum + (1LL << (ADJ_LUMA_BITS - 1))) >> ADJ_LUMA_BITS);
    const int32_t k1 = sc;
    const int32_t k0 = FIX_S_ONE - sc;
    qr = adj_mul_q(k1, qr, FIX_BITS_S) + adj_mul_q(k0, gray, FIX_BITS_S);
    qg = adj_mul_q(k1, qg, FIX_BITS_S) + adj_mul_q(k0, gray, FIX_BITS_S);
    qb = adj_mul_q(k1, qb, FIX_BITS_S) + adj_mul_q(k0, gray, FIX_BITS_S);

    /* ---- 4. H（RotateOnGray 绕灰轴 (1,1,1)/√3 旋转；angle=0 恒等跳过） ---- */
    if (angle_q14 != 0)
        rgb_adj_rotate_on_gray_q11(&qr, &qg, &qb, angle_q14);

    /* ---- 统一舍入回像素域并 clip ---- */
    *ro = (uint16_t)CLIP((qr + (FIX_S_ONE >> 1)) >> FIX_BITS_S, 0, maxv);
    *go = (uint16_t)CLIP((qg + (FIX_S_ONE >> 1)) >> FIX_BITS_S, 0, maxv);
    *bo = (uint16_t)CLIP((qb + (FIX_S_ONE >> 1)) >> FIX_BITS_S, 0, maxv);
}

/* ---- Sonnoc 固定管线浮点参考实现（精度基准，无定点量化） ---- */
/* 与 adjust_rgb_sonnoc_fix 同语义（B -> C -> S -> H）：
     B/C 逐步 clip01（db 先于 gc 生效）；S 不钳位（scale>1 时 k0<0，向 gray 反向发散）；
     H 对未钳位值旋转；末尾统一 clip01（与 Python np.clip(rgb_h,0,1) 一致）。
   归一化域 [0,1]；参数为物理量：gain_c∈[0,4]、delta_b∈[-1,1]、delta_s∈[0,4]、
   angle_deg（度，对应定点 angle_q14 = angle/360°×FIX_H_ONE）；
   luma 权重与定点版共用同一套 Q16 常量（÷65536 精确），gray_coef 见 adj_rgb_gray_coef_t。 */
static inline float rgb_adj_clipf(float x, float lo, float hi)
{
    return x < lo ? lo : (x > hi ? hi : x);
}

void adjust_rgb_sonnoc_float(float r, float g, float b, float gain_c, float delta_b, float delta_s, float angle_deg,
    int gray_coef, float *ro, float *go, float *bo)
{
    float wR, wG, wB;
    if (gray_coef == ADJ_RGB_GRAY_BT601) {
        wR = (float)ADJ_LUMA_BT601_R / 65536.0f;
        wG = (float)ADJ_LUMA_BT601_G / 65536.0f;
        wB = (float)ADJ_LUMA_BT601_B / 65536.0f;
    }
    else if (gray_coef == ADJ_RGB_GRAY_BT2020) {
        wR = (float)ADJ_LUMA_BT2020_R / 65536.0f;
        wG = (float)ADJ_LUMA_BT2020_G / 65536.0f;
        wB = (float)ADJ_LUMA_BT2020_B / 65536.0f;
    }
    else if (gray_coef == ADJ_RGB_GRAY_P3) {
        wR = (float)ADJ_LUMA_P3_R / 65536.0f;
        wG = (float)ADJ_LUMA_P3_G / 65536.0f;
        wB = (float)ADJ_LUMA_P3_B / 65536.0f;
    }
    else {
        wR = (float)ADJ_LUMA_BT709_R / 65536.0f;
        wG = (float)ADJ_LUMA_BT709_G / 65536.0f;
        wB = (float)ADJ_LUMA_BT709_B / 65536.0f;
    }
    gain_c = rgb_adj_clipf(gain_c, 0.0f, 4.0f);   /* 与定点版参数限幅一致 */
    delta_b = rgb_adj_clipf(delta_b, -1.0f, 1.0f);
    delta_s = rgb_adj_clipf(delta_s, 0.0f, 4.0f);

    /* ---- 1. B（add 加性）：x' = clip01(x + db) ---- */
    float xr = rgb_adj_clipf(r + delta_b, 0.0f, 1.0f);
    float xg = rgb_adj_clipf(g + delta_b, 0.0f, 1.0f);
    float xb = rgb_adj_clipf(b + delta_b, 0.0f, 1.0f);

    /* ---- 2. C（GainAtZero 过零点乘法）：x'' = clip01(gc·x') ---- */
    xr = rgb_adj_clipf(xr * gain_c, 0.0f, 1.0f);
    xg = rgb_adj_clipf(xg * gain_c, 0.0f, 1.0f);
    xb = rgb_adj_clipf(xb * gain_c, 0.0f, 1.0f);

    /* ---- 3. S（MixGray 灰阶混合，不钳位）：out = scale·in + (1-scale)·gray ---- */
    const float gray = xr * wR + xg * wG + xb * wB;
    const float k0 = 1.0f - delta_s;
    xr = delta_s * xr + k0 * gray;
    xg = delta_s * xg + k0 * gray;
    xb = delta_s * xb + k0 * gray;

    /* ---- 4. H（RotateOnGray 绕灰轴 (1,1,1)/√3 旋转；angle=0 恒等跳过） ---- */
    if (angle_deg != 0.0f) {
        const float th = angle_deg * (3.14159265358979323846f / 180.0f);
        const float cs = cosf(th);
        const float sn = sinf(th);
        const float k3 = (1.0f - cs) * (xr + xg + xb) * (1.0f / 3.0f);
        const float inv_s3 = 1.0f / sqrtf(3.0f);
        const float r0 = xr, g0 = xg, b0 = xb;
        xr = cs * r0 + k3 + sn * (b0 - g0) * inv_s3;
        xg = cs * g0 + k3 + sn * (r0 - b0) * inv_s3;
        xb = cs * b0 + k3 + sn * (g0 - r0) * inv_s3;
    }

    /* ---- 统一 clip ---- */
    *ro = rgb_adj_clipf(xr, 0.0f, 1.0f);
    *go = rgb_adj_clipf(xg, 0.0f, 1.0f);
    *bo = rgb_adj_clipf(xb, 0.0f, 1.0f);
}