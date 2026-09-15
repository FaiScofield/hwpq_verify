
#ifndef RGB_ADJUST_H
#define RGB_ADJUST_H

#include "hsv_fixed.h"

/* ===================== RGB 域固定管线 BCSH（adjust_rgb 专用版） ===================== */
/* 对应 script/verify_tool_app/test_app_hsv.py 的 RGB 处理域（Adjust Field = RGB），
   即 script/bcsh/hsv_adjust.py 的 adjust_rgb。与通用版 adjust_rgb_fix 的区别是各参数
   的实现方法是**固定**的（无 mode 参数）：

     执行顺序：B(ModeMul) -> C(GainAtZeroPoint) -> S(MixGray) -> H(RotateOnGray)，Hue Goal = SameOffset

     B  ModeMul          v1 = clip(v * gb)                  gb∈[0,4]，中性 1.0
     C  GainAtZeroPoint  v2 = clip(v1 * gc)                 gc∈[0,4]，中性 1.0（以黑为锚点，v'=gc*v）
     S  MixGray          out = s*in + (1-s)*gray(in)        s∈[0,4]，中性 1.0；gray = luma(in)
                                                           灰度系数：BT.601 / BT.709 / BT.2020 / Display P3
     H  RotateOnGray     绕灰轴 (1,1,1)/√3 旋转（SameOffset：全图统一角度，不逐像素取弧长）

   要点：
     - **B 先于 C**：C 作用在 B 之后的值上，故 B 的幅度会被 C 缩放；B/C 两步之间各自
       clip 到 [0, maxv]（与 Python 一致，中间钳位会实际影响大增益下的结果）
     - S 步不再钳位，H 步直接用未钳位的中间值旋转，**末尾统一 clip**（与 Python 的
       np.clip(rgb_h, 0, 1) 一致）
     - gray 由 B/C 之后的像素计算（gray = luma(v2)，与 Python 的 rgb_v 一致）
     - S Tolerance 不参与：Python 的 RGB 域已去掉该门控，S 恒生效（乘性 scale 语义）
     - 无 float、无 math 库：绕灰轴的 cos/sin 用 257 项 Q15 表 + 线性插值（表覆盖
       0~360°，步长 360/256 = 1.40625°，插值最大误差 ≈3 LSB(Q15)，折合 u10 像素 < 0.1 LSB）

   定点格式（与 hsv_fixed 其余接口一致）：
     gain_c / gain_b / scale_s : Q11（1.0 = FIX_S_ONE = 2048），[0, 4]
     angle_q14                 : Q14（360° = FIX_H_ONE = 16384），SameOffset 旋转角
     gray_coef                 : ADJ_RGB_GRAY_BT601 / BT709 / BT2020 / P3（见 hsv_fixed.h）
   像素域 [0, maxv]（u8: 255 / u10: 1023），内部统一 Q11（pixel<<11）运算。 */

/* sin(2*pi*k/256) 的 Q15 表（k = 0..256，末项为 360°，用于 wrap 处插值；1.0 = 32768） */
static const int16_t s_rgb_sin_q15[257] = {0, 804, 1608, 2411, 3212, 4011, 4808, 5602, 6393, 7180, 7962, 8740, 9512,
    10279, 11039, 11793, 12540, 13279, 14010, 14733, 15447, 16151, 16846, 17531, 18205, 18868, 19520, 20160, 20788,
    21403, 22006, 22595, 23170, 23732, 24279, 24812, 25330, 25833, 26320, 26791, 27246, 27684, 28106, 28511, 28899,
    29269, 29622, 29957, 30274, 30572, 30853, 31114, 31357, 31581, 31786, 31972, 32138, 32286, 32413, 32522, 32610,
    32679, 32729, 32758, 32767, 32758, 32729, 32679, 32610, 32522, 32413, 32286, 32138, 31972, 31786, 31581, 31357,
    31114, 30853, 30572, 30274, 29957, 29622, 29269, 28899, 28511, 28106, 27684, 27246, 26791, 26320, 25833, 25330,
    24812, 24279, 23732, 23170, 22595, 22006, 21403, 20788, 20160, 19520, 18868, 18205, 17531, 16846, 16151, 15447,
    14733, 14010, 13279, 12540, 11793, 11039, 10279, 9512, 8740, 7962, 7180, 6393, 5602, 4808, 4011, 3212, 2411, 1608,
    804, 0, -804, -1608, -2411, -3212, -4011, -4808, -5602, -6393, -7180, -7962, -8740, -9512, -10279, -11039, -11793,
    -12540, -13279, -14010, -14733, -15447, -16151, -16846, -17531, -18205, -18868, -19520, -20160, -20788, -21403,
    -22006, -22595, -23170, -23732, -24279, -24812, -25330, -25833, -26320, -26791, -27246, -27684, -28106, -28511,
    -28899, -29269, -29622, -29957, -30274, -30572, -30853, -31114, -31357, -31581, -31786, -31972, -32138, -32286,
    -32413, -32522, -32610, -32679, -32729, -32758, -32768, -32758, -32729, -32679, -32610, -32522, -32413, -32286,
    -32138, -31972, -31786, -31581, -31357, -31114, -30853, -30572, -30274, -29957, -29622, -29269, -28899, -28511,
    -28106, -27684, -27246, -26791, -26320, -25833, -25330, -24812, -24279, -23732, -23170, -22595, -22006, -21403,
    -20788, -20160, -19520, -18868, -18205, -17531, -16846, -16151, -15447, -14733, -14010, -13279, -12540, -11793,
    -11039, -10279, -9512, -8740, -7962, -7180, -6393, -5602, -4808, -4011, -3212, -2411, -1608, -804, 0};

/* 1.0（Q15 三角量表满量程）与几个常量 */
#define RGB_ADJ_TRIG_ONE      32768
#define RGB_ADJ_INV_SQRT3_Q15 18919 /* round(2^15/√3) */
#define RGB_ADJ_RCP3_Q16      21845 /* round(2^16/3) */

/* angle_q14（360° = FIX_H_ONE）的 sin，Q15（1.0 = 32768）。
   表索引取 Q14 的高 8 bit（256 等分 360°），低 6 bit 线性插值。 */
static inline int32_t rgb_adj_sin_q15(int32_t angle_q14)
{
    uint32_t h = (uint32_t)angle_q14 & (uint32_t)(FIX_H_ONE - 1); /* 归一化到 [0, 360°) */
    uint32_t i = h >> (FIX_BITS_H - 8);                           /* 0..255 */
    int32_t f = (int32_t)(h & ((1u << (FIX_BITS_H - 8)) - 1));    /* 段内小数 0..63 */
    int32_t a = s_rgb_sin_q15[i];
    int32_t d = (int32_t)s_rgb_sin_q15[i + 1] - a;
    /* 注意：插值偏移量必须用有符号字面量，否则 d*f 会被提升为无符号、右移变逻辑移位 */
    return a + ((d * f + (1 << (FIX_BITS_H - 9))) >> (FIX_BITS_H - 8));
}

/* angle_q14 的 cos，Q15：cos(x) = sin(x + 90°) */
static inline int32_t rgb_adj_cos_q15(int32_t angle_q14) { return rgb_adj_sin_q15(angle_q14 + (FIX_H_ONE >> 2)); }

/* 绕灰轴 (1,1,1)/√3 旋转 angle_q14（Q11 像素域，原地修改）。
   o0 = cos·r + (1-cos)·(r+g+b)/3 + sin·(b-g)/√3，另两通道按 r->g->b 轮换；
   灰阶保持不变。对应 hsv_adjust.py 的 _rotate_hue（RGB 域 H 步 RotateOnGray）。
   qr/qg/qb 为 Q11 像素域（pixel<<11），允许传未钳位的中间值（与浮点参考一致：
   Python 在未钳位的 S 步输出上旋转，末尾才统一 clip）。 */
static inline void rgb_adj_rotate_on_gray_q11(int32_t *qr, int32_t *qg, int32_t *qb, int32_t angle_q14)
{
    const int32_t cs = rgb_adj_cos_q15(angle_q14);
    const int32_t sn = rgb_adj_sin_q15(angle_q14);
    const int32_t r0 = *qr, g0 = *qg, b0 = *qb;
    /* (1-cos)/3 先算成 Q15，再与 (r+g+b) 相乘 —— 把除以 3 合并进常数 */
    const int32_t k3 = adj_mul_q(adj_mul_q(RGB_ADJ_TRIG_ONE - cs, RGB_ADJ_RCP3_Q16, 16), r0 + g0 + b0, 15);
    *qr = adj_mul_q(cs, r0, 15) + k3 + adj_mul_q(adj_mul_q(sn, b0 - g0, 15), RGB_ADJ_INV_SQRT3_Q15, 15);
    *qg = adj_mul_q(cs, g0, 15) + k3 + adj_mul_q(adj_mul_q(sn, r0 - b0, 15), RGB_ADJ_INV_SQRT3_Q15, 15);
    *qb = adj_mul_q(cs, b0, 15) + k3 + adj_mul_q(adj_mul_q(sn, g0 - r0, 15), RGB_ADJ_INV_SQRT3_Q15, 15);
}

/* 单像素 RGB 域固定管线 BCSH 调整（像素域 [0,maxv]）。 */
static inline void rgb_bcsh_fix(uint16_t r, uint16_t g, uint16_t b, uint16_t maxv, int32_t gain_c, int32_t gain_b,
    int32_t scale_s, int32_t angle_q14, int gray_coef, uint16_t *ro, uint16_t *go, uint16_t *bo)
{
    const int32_t cap = (int32_t)maxv << FIX_BITS_S; /* maxv 的 Q11 像素域表示 */
    const int32_t gc = CLIP(gain_c, 0, 4 * FIX_S_ONE);
    const int32_t gb = CLIP(gain_b, 0, 4 * FIX_S_ONE);
    const int32_t sc = CLIP(scale_s, 0, 4 * FIX_S_ONE);
    int32_t qr, qg, qb, gray, wR, wG, wB;

    /* ---- 1. B（ModeMul）---- */
    qr = CLIP(adj_mul_q((int32_t)r << FIX_BITS_S, gb, FIX_BITS_S), 0, cap);
    qg = CLIP(adj_mul_q((int32_t)g << FIX_BITS_S, gb, FIX_BITS_S), 0, cap);
    qb = CLIP(adj_mul_q((int32_t)b << FIX_BITS_S, gb, FIX_BITS_S), 0, cap);

    /* ---- 2. C（GainAtZeroPoint）：作用在 B 之后 -> B 的幅度受 C 缩放 ---- */
    qr = CLIP(adj_mul_q(qr, gc, FIX_BITS_S), 0, cap);
    qg = CLIP(adj_mul_q(qg, gc, FIX_BITS_S), 0, cap);
    qb = CLIP(adj_mul_q(qb, gc, FIX_BITS_S), 0, cap);

    /* ---- 3. S（MixGray）：gray 取 B/C 之后的像素（对应 Python 的 rgb_v） ---- */
    switch (gray_coef) {
    case ADJ_RGB_GRAY_BT601:
        wR = ADJ_LUMA_BT601_R;
        wG = ADJ_LUMA_BT601_G;
        wB = ADJ_LUMA_BT601_B;
        break;
    case ADJ_RGB_GRAY_BT2020:
        wR = ADJ_LUMA_BT2020_R;
        wG = ADJ_LUMA_BT2020_G;
        wB = ADJ_LUMA_BT2020_B;
        break;
    case ADJ_RGB_GRAY_P3:
        wR = ADJ_LUMA_P3_R;
        wG = ADJ_LUMA_P3_G;
        wB = ADJ_LUMA_P3_B;
        break;
    default:
        wR = ADJ_LUMA_BT709_R;
        wG = ADJ_LUMA_BT709_G;
        wB = ADJ_LUMA_BT709_B;
        break;
    }
    gray = adj_rsh_round((int64_t)qr * wR + (int64_t)qg * wG + (int64_t)qb * wB, ADJ_LUMA_BITS);
    {
        const int32_t k1 = sc; /* scale（>1 时 k0<0，向 gray 反向发散=增饱和） */
        const int32_t k0 = FIX_S_ONE - sc;
        qr = adj_mul_q(k1, qr, FIX_BITS_S) + adj_mul_q(k0, gray, FIX_BITS_S);
        qg = adj_mul_q(k1, qg, FIX_BITS_S) + adj_mul_q(k0, gray, FIX_BITS_S);
        qb = adj_mul_q(k1, qb, FIX_BITS_S) + adj_mul_q(k0, gray, FIX_BITS_S);
    }

    /* ---- 4. H（RotateOnGray，SameOffset）：绕灰轴 (1,1,1)/√3 旋转 ---- */
    if (angle_q14 != 0) {
        rgb_adj_rotate_on_gray_q11(&qr, &qg, &qb, angle_q14);
    }

    /* ---- 统一舍入回像素域并 clip ---- */
    *ro = (uint16_t)CLIP(adj_rsh_round(qr, FIX_BITS_S), 0, maxv);
    *go = (uint16_t)CLIP(adj_rsh_round(qg, FIX_BITS_S), 0, maxv);
    *bo = (uint16_t)CLIP(adj_rsh_round(qb, FIX_BITS_S), 0, maxv);
}

/* u8 缓冲接口（整帧统一参数） */
static inline void rgb_bcsh_fix_u8(const uint8_t *rgb, int n, int32_t gain_c, int32_t gain_b, int32_t scale_s,
    int32_t angle_q14, int gray_coef, uint8_t *out)
{
    for (int i = 0; i < n; i++) {
        uint16_t r1, g1, b1;
        rgb_bcsh_fix(rgb[3 * i], rgb[3 * i + 1], rgb[3 * i + 2], 255, gain_c, gain_b, scale_s, angle_q14, gray_coef,
            &r1, &g1, &b1);
        out[3 * i] = (uint8_t)r1;
        out[3 * i + 1] = (uint8_t)g1;
        out[3 * i + 2] = (uint8_t)b1;
    }
}

/* u10 缓冲接口（整帧统一参数） */
static inline void rgb_bcsh_fix_u10(const uint16_t *rgb, int n, int32_t gain_c, int32_t gain_b, int32_t scale_s,
    int32_t angle_q14, int gray_coef, uint16_t *out)
{
    for (int i = 0; i < n; i++) {
        uint16_t r1, g1, b1;
        rgb_bcsh_fix(rgb[3 * i], rgb[3 * i + 1], rgb[3 * i + 2], 1023, gain_c, gain_b, scale_s, angle_q14, gray_coef,
            &r1, &g1, &b1);
        out[3 * i] = r1;
        out[3 * i + 1] = g1;
        out[3 * i + 2] = b1;
    }
}

/* ===================== 通用版（mode 可选） ===================== */
/* 实现见 rgb_adjust.c；参数定点格式与上同：
     gain_c     : Q11（1.0 = FIX_S_ONE）；mid/zero/both 取 [0,4]，tanslant 取 [-1,1]
     delta_b    : Q11（1.0 = FIX_S_ONE）；add 取 [-1,1]，mul 取 [0,4]，rate2limit 取 [0,2]
     delta_s    : Q11（1.0 = FIX_S_ONE）；灰阶混合乘性增益 [0,4]，中性 1.0
     tolerance_s: Q11（1.0 = FIX_S_ONE）；S 门控 [0,1]（保留参数位，当前未启用）
     angle_q14  : Q14（360° = FIX_H_ONE）；H 平移量
   mode 用 adj_rgb_mode_c_t / adj_rgb_mode_b_t / adj_rgb_mode_h_t / adj_rgb_gray_coef_t
   （见 hsv_fixed.h）。
   tanslant 的 tan 用 4097 项 Q11 直接查表（θ Q14 直接索引，无插值，无 float/math 依赖）。 */
void adjust_rgb_fix(uint16_t r, uint16_t g, uint16_t b, uint16_t maxv, int32_t gain_c, int32_t delta_b, int32_t delta_s,
    int32_t tolerance_s, int32_t angle_q14, int gray_coef, int mode_c, int mode_b, int mode_h, uint16_t *ro,
    uint16_t *go, uint16_t *bo);


/* u8 缓冲接口（整帧统一参数） */
static inline void adjust_rgb_fix_u8(const uint8_t *rgb, int n, int32_t gain_c, int32_t delta_b, int32_t delta_s,
    int32_t tolerance_s, int32_t angle_q14, int gray_coef, int mode_c, int mode_b, int mode_h, uint8_t *out)
{
    for (int i = 0; i < n; i++) {
        uint16_t r1, g1, b1;
        adjust_rgb_fix(rgb[3 * i], rgb[3 * i + 1], rgb[3 * i + 2], 255, gain_c, delta_b, delta_s, tolerance_s,
            angle_q14, gray_coef, mode_c, mode_b, mode_h, &r1, &g1, &b1);
        out[3 * i] = (uint8_t)r1;
        out[3 * i + 1] = (uint8_t)g1;
        out[3 * i + 2] = (uint8_t)b1;
    }
}

/* u10 缓冲接口（整帧统一参数） */
static inline void adjust_rgb_fix_u10(const uint16_t *rgb, int n, int32_t gain_c, int32_t delta_b, int32_t delta_s,
    int32_t tolerance_s, int32_t angle_q14, int gray_coef, int mode_c, int mode_b, int mode_h, uint16_t *out)
{
    for (int i = 0; i < n; i++) {
        uint16_t r1, g1, b1;
        adjust_rgb_fix(rgb[3 * i], rgb[3 * i + 1], rgb[3 * i + 2], 1023, gain_c, delta_b, delta_s, tolerance_s,
            angle_q14, gray_coef, mode_c, mode_b, mode_h, &r1, &g1, &b1);
        out[3 * i] = r1;
        out[3 * i + 1] = g1;
        out[3 * i + 2] = b1;
    }
}

/* ===================== Sonnoc 固定管线（无 mode 分支） ===================== */
/* 固定 C(GainAtZero 过零点乘法) -> B(add 加性) -> S(MixGray luma 灰阶混合)
   -> H(RotateOnGray 绕灰轴旋转)，与 adjust_rgb_fix(mode_c=ZERO, mode_b=ADD,
   mode_h=ROTATEGRAY) 逐位等价，供 Sonnoc 竞品模拟使用。实现见 rgb_adjust.c。
   参数定点格式：gain_c/delta_b/delta_s 均为 Q11（1.0 = FIX_S_ONE），
   angle_q14 为 Q14（360° = FIX_H_ONE），gray_coef 见 adj_rgb_gray_coef_t。 */
void adjust_rgb_sonnoc_fix(uint16_t r, uint16_t g, uint16_t b, uint16_t maxv, int32_t gain_c, int32_t delta_b,
    int32_t delta_s, int32_t angle_q14, int gray_coef, uint16_t *ro, uint16_t *go, uint16_t *bo);

/* 同管线的浮点参考实现（精度基准，无定点量化）：r/g/b ∈ [0,1]（归一化像素域），
   参数为物理量 gain_c∈[0,4] / delta_b∈[-1,1] / delta_s∈[0,4] / angle_deg（度），
   gray_coef 同定点版；输出 ro/go/bo ∈ [0,1]（已 clip）。实现见 rgb_adjust.c（依赖 math.h）。 */
void adjust_rgb_sonnoc_float(float r, float g, float b, float gain_c, float delta_b, float delta_s, float angle_deg,
    int gray_coef, float *ro, float *go, float *bo);

#endif /* RGB_ADJUST_H */