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
 *   - hsv2rgb_v4_hexwalk：六边形走表模型（6 段 TAB + M/m/mid），无分支无除法
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
#define VS_SHIFT   11 /* 重建第一级 V*S 提前右移位数：目的是降低乘法总位宽，最大允许到11不掉往返精度 */
#define RS_SHIFT   (FIX_BITS_H + FIX_BITS_S - VS_SHIFT) /* 重建第二级右移 */

void rgb2hsv_v0_classic(uint16_t r, uint16_t g, uint16_t b, uint16_t *h14, uint16_t *s11, uint16_t *v10);
void rgb2hsv_v1_no_branch(uint16_t r, uint16_t g, uint16_t b, uint16_t *h14, uint16_t *s11, uint16_t *v10);
void rgb2hsv_v2_no_division(uint16_t r, uint16_t g, uint16_t b, uint16_t *h14, uint16_t *s11, uint16_t *v10);
void rgb2hsv_v3_optimal(uint16_t r, uint16_t g, uint16_t b, uint16_t *h14, uint16_t *s11, uint16_t *v10);

static inline void rgb2hsv_fix_u8(uint8_t R, uint8_t G, uint8_t B, uint16_t *H, uint16_t *S, uint16_t *V)
{
    rgb2hsv_v3_optimal(R, G, B, H, S, V);
}

static inline void rgb2hsv_fix_u10(uint16_t R, uint16_t G, uint16_t B, uint16_t *H, uint16_t *S, uint16_t *V)
{
    rgb2hsv_v3_optimal(R, G, B, H, S, V);
}

void hsv2rgb_v0_classic(uint16_t h14, uint16_t s11, uint16_t v10, uint16_t maxv, uint16_t *R, uint16_t *G, uint16_t *B);
void hsv2rgb_v1_no_branch(uint16_t h14, uint16_t s11, uint16_t v10, uint16_t maxv, uint16_t *R, uint16_t *G, uint16_t *B);
void hsv2rgb_v2_no_division(uint16_t h14, uint16_t s11, uint16_t v10, uint16_t maxv, uint16_t *R, uint16_t *G, uint16_t *B);
void hsv2rgb_v3_optimal(uint16_t h14, uint16_t s11, uint16_t v10, uint16_t maxv, uint16_t *R, uint16_t *G, uint16_t *B);
void hsv2rgb_v4_hexwalk(uint16_t h14, uint16_t s11, uint16_t v10, uint16_t maxv, uint16_t *R, uint16_t *G, uint16_t *B);

static inline void hsv2rgb_fix_u8(uint16_t H, uint16_t S, uint16_t V, uint8_t *R, uint8_t *G, uint8_t *B)
{
    uint16_t r, g, b;
    hsv2rgb_v3_optimal(H, S, V, 255, &r, &g, &b);
    *R = (uint8_t)r;
    *G = (uint8_t)g;
    *B = (uint8_t)b;
}

/* HSV -> RGB(10bit) */
static inline void hsv2rgb_fix_u10(uint16_t H, uint16_t S, uint16_t V, uint16_t *R, uint16_t *G, uint16_t *B)
{
    hsv2rgb_v3_optimal(H, S, V, 1023, R, G, B);
}


/* H Q14 -> H Q16（<<2，精确） */
static inline int32_t hsv_h14_to_q16(int32_t H14) { return H14 << 2; }

/* H Q16 -> H Q14（>>2，精确；Q16 低 2 bit 被丢弃） */
static inline int32_t hsv_h14_from_q16(int32_t H16) { return H16 >> 2; }


/* ================= RGB 域直接 BCSH 调整（adjust_rgb 定点版） ================= */
/* 对应 script/bcsh/hsv_adjust.py 的 adjust_rgb：不经过 HSV 域转换，逐通道直接调整。
   - V：三通道统一 contrast(mode_c) 后按 mode_b 施加 brightness（全程像素域，不归一化）
        mode_c='mid'   v'=clip((v-0.5)*gc+0.5)（过 v=0.5 中点，gc∈[0,4]，中性 1.0）
        mode_c='tanslant' v'=clip((v-0.5)*tan((c+1)π/4)+0.5)（c∈[-1,1]，中性 0）
        mode_b='mul'   v'=clip(v'*gv)（gv∈[0,4]，中性 1.0）
        mode_b='rate2limit'  db∈[0,2]，中性 1：db<1 向黑靠拢 v'=v*db（混入 1-db 黑）；
        db>1 向白靠拢 v'=v+(db-1)*(maxv-v)（混入 db-1 白）
   - S：灰阶混合 out = scale*in + (1-scale)*gray，gray 为 luma（BT.709/BT.601/BT.2020）；
   - H：恒为 ModeAdd 六边形色相加法 h'=(h+angle)%360：一次 rgb2hsv 取色相（M/m/C 不变
        -> S/V 天然不变），平移后在 RGB 域按 6 段 TAB 重排中间通道（同
        hsv2rgb_v4_hexwalk 模型），无需 hsv2rgb 重建
   定点格式（与 hsv_fixed 其余接口一致）：
     gain_c     : Q11（1.0 = FIX_S_ONE）；mid 取 [0,4]，tanslant 取 [-1,1]
     delta_b    : Q11（1.0 = FIX_S_ONE）；mul 取 [0,4]，rate2limit 取 [0,2]
     delta_s    : Q11（1.0 = FIX_S_ONE）；灰阶混合乘性增益 [0,4]，中性 1.0
     tolerance_s: Q11（1.0 = FIX_S_ONE）；S 门控 [0,1]（保留参数位，当前未启用）
     angle_q14  : Q14（360° = FIX_H_ONE）；H 平移量
   tanslant 的 tan 用 4097 项 Q11 直接查表（θ Q14 直接索引，无插值，无 float/math 依赖）。 */
typedef enum {
    ADJ_RGB_MODE_C_MID = 0,  /* GainAtMid：过 v=0.5 中点 */
    ADJ_RGB_MODE_C_TANSLANT, /* TanSlant：tan((c+1)π/4) */
} adj_rgb_mode_c_t;

typedef enum {
    ADJ_RGB_MODE_B_MUL = 0,      /* 乘性 */
    ADJ_RGB_MODE_B_RATE2LIMIT, /* 按比例向黑/白极限靠拢 */
} adj_rgb_mode_b_t;

typedef enum {
    ADJ_RGB_MODE_S_MUL = 0,      /* 乘性 scale */
    ADJ_RGB_MODE_S_RATE2LIMIT, /* 按比例向灰度/全饱和靠拢 */
} adj_rgb_mode_s_t;

typedef enum {
    ADJ_RGB_GRAY_BT709 = 0, /* luma BT.709 */
    ADJ_RGB_GRAY_BT601,     /* luma BT.601 */
    ADJ_RGB_GRAY_BT2020,    /* luma BT.2020 */
} adj_rgb_gray_coef_t;

/* 单像素 RGB 域 BCSH 调整核心（像素域 [0,maxv]，maxv=255(u8)/1023(u10)）。
   参数定点格式见上；mode 参数用 adj_rgb_* 枚举。H 恒为 ModeAdd（六边形色相加法）。 */
void adjust_rgb_fix(uint16_t r, uint16_t g, uint16_t b, uint16_t maxv, int32_t gain_c, int32_t delta_b, int32_t delta_s,
    int32_t tolerance_s, int32_t angle_q14, int gray_coef, int mode_c, int mode_b, uint16_t *ro, uint16_t *go, uint16_t *bo);

/* 单像素 HSV 域 BCSH 调整核心（像素域 [0,maxv]，maxv=255(u8)/1023(u10)）。
   与 adjust_rgb_fix 参数/模式完全一致，但走 HSV 域往返：
   rgb2hsv_v3_optimal 取 H/S/V，在 HSV 域调整 V（contrast+brightness）、
   S（mode_s：mul 乘性 scale 或 rate2limit 按比例向灰度/全饱和靠拢）、
   H（ModeAdd 平移），再用 hsv2rgb_v4_hexwalk 重建 RGB。
   对应 script/bcsh/hsv_adjust.py 的 adjust_hsv。
   mode_s='rate2limit'：delta_s∈[0,2]，中性 1（d=ds-1∈[-1,1]）；d<0 向灰度靠拢
   s'=s*ds、d>0 向全饱和靠拢 s'=s+d*(1-s)；增色（d>0）时 S<tolerance_s 的像素
   保持原样（S 门控，与 Python 一致）。 */
void adjust_hsv_fix(uint16_t r, uint16_t g, uint16_t b, uint16_t maxv, int32_t gain_c, int32_t delta_b, int32_t delta_s,
    int32_t tolerance_s, int32_t angle_q14, int gray_coef, int mode_c, int mode_b, int mode_s, uint16_t *ro, uint16_t *go,
    uint16_t *bo);

/* u8 缓冲接口（整帧统一参数） */
static inline void adjust_rgb_fix_u8(const uint8_t *rgb, int n, int32_t gain_c, int32_t delta_b, int32_t delta_s,
    int32_t tolerance_s, int32_t angle_q14, int gray_coef, int mode_c, int mode_b, uint8_t *out)
{
    for (int i = 0; i < n; i++) {
        uint16_t r1, g1, b1;
        adjust_rgb_fix(rgb[3 * i], rgb[3 * i + 1], rgb[3 * i + 2], 255, gain_c, delta_b, delta_s, tolerance_s,
            angle_q14, gray_coef, mode_c, mode_b, &r1, &g1, &b1);
        out[3 * i] = (uint8_t)r1;
        out[3 * i + 1] = (uint8_t)g1;
        out[3 * i + 2] = (uint8_t)b1;
    }
}

/* u10 缓冲接口（整帧统一参数） */
static inline void adjust_rgb_fix_u10(const uint16_t *rgb, int n, int32_t gain_c, int32_t delta_b, int32_t delta_s,
    int32_t tolerance_s, int32_t angle_q14, int gray_coef, int mode_c, int mode_b, uint16_t *out)
{
    for (int i = 0; i < n; i++) {
        uint16_t r1, g1, b1;
        adjust_rgb_fix(rgb[3 * i], rgb[3 * i + 1], rgb[3 * i + 2], 1023, gain_c, delta_b, delta_s, tolerance_s,
            angle_q14, gray_coef, mode_c, mode_b, &r1, &g1, &b1);
        out[3 * i] = r1;
        out[3 * i + 1] = g1;
        out[3 * i + 2] = b1;
    }
}

/* u8 缓冲接口（整帧统一参数） */
static inline void adjust_hsv_fix_u8(const uint8_t *rgb, int n, int32_t gain_c, int32_t delta_b, int32_t delta_s,
    int32_t tolerance_s, int32_t angle_q14, int gray_coef, int mode_c, int mode_b, int mode_s, uint8_t *out)
{
    for (int i = 0; i < n; i++) {
        uint16_t r1, g1, b1;
        adjust_hsv_fix(rgb[3 * i], rgb[3 * i + 1], rgb[3 * i + 2], 255, gain_c, delta_b, delta_s, tolerance_s,
            angle_q14, gray_coef, mode_c, mode_b, mode_s, &r1, &g1, &b1);
        out[3 * i] = (uint8_t)r1;
        out[3 * i + 1] = (uint8_t)g1;
        out[3 * i + 2] = (uint8_t)b1;
    }
}

/* u10 缓冲接口（整帧统一参数） */
static inline void adjust_hsv_fix_u10(const uint16_t *rgb, int n, int32_t gain_c, int32_t delta_b, int32_t delta_s,
    int32_t tolerance_s, int32_t angle_q14, int gray_coef, int mode_c, int mode_b, int mode_s, uint16_t *out)
{
    for (int i = 0; i < n; i++) {
        uint16_t r1, g1, b1;
        adjust_hsv_fix(rgb[3 * i], rgb[3 * i + 1], rgb[3 * i + 2], 1023, gain_c, delta_b, delta_s, tolerance_s,
            angle_q14, gray_coef, mode_c, mode_b, mode_s, &r1, &g1, &b1);
        out[3 * i] = r1;
        out[3 * i + 1] = g1;
        out[3 * i + 2] = b1;
    }
}

#endif /* HSV_FIXED_H */
