/**
 * @copyright: Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @brief:     RGB 格式描述子及相关辅助函数
 * @author:
 * @create:    2026-04-16
 */

#ifndef _PQFMT_RGB_H_
#define _PQFMT_RGB_H_

#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * RGB 通道顺序枚举
 */
typedef enum pqfmt_rgb_order {
    PQFMT_RGB_ORDER_RGB = 0,
    PQFMT_RGB_ORDER_BGR = 1,
} pqfmt_rgb_order_e;

/**
 * Alpha 位置枚举
 */
typedef enum pqfmt_alpha_pos {
    PQFMT_ALPHA_NONE = 0,
    PQFMT_ALPHA_LSM = 1,
    PQFMT_ALPHA_MSB = 2,
} pqfmt_alpha_pos_e;

/**
 * RGB 存储布局枚举
 */
typedef enum pqfmt_rgb_layout {
    PQFMT_RGB_LAYOUT_PACKED = 0,
    PQFMT_RGB_LAYOUT_PLANAR = 1,
    PQFMT_RGB_LAYOUT_SEMIPLANAR = 2, // rgb plane + alpha plane
} pqfmt_rgb_layout_e;

/**
 * RGB 格式描述子
 */
typedef struct pqfmt_rgb_desc {
    pqfmt_alpha_pos_e alpha_pos;
    pqfmt_rgb_layout_e layout;
    pqfmt_rgb_order_e order;
    uint8_t comp_bits[4];
} pqfmt_rgb_desc_s;

/**
 * RGB 预定义格式描述符
 */
extern const pqfmt_rgb_desc_s g_rgb_fmt_rgb888;
extern const pqfmt_rgb_desc_s g_rgb_fmt_bgr888;
extern const pqfmt_rgb_desc_s g_rgb_fmt_rgba8888;
extern const pqfmt_rgb_desc_s g_rgb_fmt_bgra8888;
extern const pqfmt_rgb_desc_s g_rgb_fmt_argb8888;
extern const pqfmt_rgb_desc_s g_rgb_fmt_abgr8888;
extern const pqfmt_rgb_desc_s g_rgb_fmt_rgb332;
extern const pqfmt_rgb_desc_s g_rgb_fmt_bgr233;
extern const pqfmt_rgb_desc_s g_rgb_fmt_rgb565;
extern const pqfmt_rgb_desc_s g_rgb_fmt_bgr565;
extern const pqfmt_rgb_desc_s g_rgb_fmt_rgba5551;
extern const pqfmt_rgb_desc_s g_rgb_fmt_argb1555;
extern const pqfmt_rgb_desc_s g_rgb_fmt_rgba1010102;
extern const pqfmt_rgb_desc_s g_rgb_fmt_bgra1010102;

/**
 * RGB 格式名称字符串
 */
extern const char *pqfmt_rgb_order_name(pqfmt_rgb_order_e order);
extern const char *pqfmt_alpha_pos_name(pqfmt_alpha_pos_e pos);
extern const char *pqfmt_rgb_layout_name(pqfmt_rgb_layout_e layout);

/**
 * RGB 格式描述符初始化函数
 */
extern void pqfmt_rgb_desc_init(pqfmt_rgb_desc_s *desc, pqfmt_alpha_pos_e alpha_pos, pqfmt_rgb_order_e order,
    pqfmt_rgb_layout_e layout, uint8_t comp_bits[4], uint8_t bpp);

/**
 * RGB 格式信息查询函数
 */
extern bool pqfmt_rgb_desc_is_valid(const pqfmt_rgb_desc_s *desc);
extern bool pqfmt_rgb_desc_has_alpha(const pqfmt_rgb_desc_s *desc);
extern bool pqfmt_rgb_desc_is_bgr_order(const pqfmt_rgb_desc_s *desc);
extern uint8_t pqfmt_rgb_desc_get_channel_bits(const pqfmt_rgb_desc_s *desc, uint8_t *r, uint8_t *g, uint8_t *b, uint8_t *a);

/**
 * RGB 格式转换辅助函数
 */
extern float pqfmt_rgb_desc_calc_pitch_ratio(const pqfmt_rgb_desc_s *desc);
extern size_t pqfmt_rgb_desc_calc_framesize(const pqfmt_rgb_desc_s *desc, int w, int h, int stride);

/**
 * RGB 格式比较函数
 */
extern bool pqfmt_rgb_desc_equal(const pqfmt_rgb_desc_s *desc1, const pqfmt_rgb_desc_s *desc2);

/**
 * RGB 格式信息打印函数 (调试用)
 */
extern void pqfmt_rgb_desc_print(const pqfmt_rgb_desc_s *desc);

#ifdef __cplusplus
}
#endif

#endif
