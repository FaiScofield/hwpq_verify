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

#endif /* HSV_FIXED_H */
