/**
 * @copyright: Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @brief:     RGB format descriptor and related helper functions
 * @author:
 * @create:    2026-04-16
 */

#ifndef _PQFMT_RGB_H_
#define _PQFMT_RGB_H_

#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * RGB channel order enumeration
 */
typedef enum pqfmt_rgb_order {
    PQFMT_RGB_ORDER_RGB,
    PQFMT_RGB_ORDER_BGR,
} pqfmt_rgb_order_e;

/**
 * Alpha position enumeration
 */
typedef enum pqfmt_alpha_pos {
    PQFMT_ALPHA_NONE,
    PQFMT_ALPHA_LSM,
    PQFMT_ALPHA_MSB,
} pqfmt_alpha_pos_e;

/**
 * RGB storage layout enumeration
 */
typedef enum pqfmt_rgb_layout {
    PQFMT_RGB_LAYOUT_PACKED,
    PQFMT_RGB_LAYOUT_PLANAR,
    PQFMT_RGB_LAYOUT_SEMIPLANAR, // rgb plane + alpha plane
} pqfmt_rgb_layout_e;

/**
 * RGB format descriptor
 */
typedef struct pqfmt_rgb_desc {
    pqfmt_alpha_pos_e alpha_pos;
    pqfmt_rgb_layout_e layout;
    pqfmt_rgb_order_e order;
    uint8_t comp_bits[4];
} pqfmt_rgb_desc_s;

/**
 * RGB predefined format descriptors
 */
extern const pqfmt_rgb_desc_s g_rgb_desc_rgb888;
extern const pqfmt_rgb_desc_s g_rgb_desc_bgr888;
extern const pqfmt_rgb_desc_s g_rgb_desc_rgba8888;
extern const pqfmt_rgb_desc_s g_rgb_desc_bgra8888;
extern const pqfmt_rgb_desc_s g_rgb_desc_argb8888;
extern const pqfmt_rgb_desc_s g_rgb_desc_abgr8888;
extern const pqfmt_rgb_desc_s g_rgb_desc_rgb332;
extern const pqfmt_rgb_desc_s g_rgb_desc_bgr233;
extern const pqfmt_rgb_desc_s g_rgb_desc_rgb565;
extern const pqfmt_rgb_desc_s g_rgb_desc_bgr565;
extern const pqfmt_rgb_desc_s g_rgb_desc_rgba5551;
extern const pqfmt_rgb_desc_s g_rgb_desc_abgr1555;
extern const pqfmt_rgb_desc_s g_rgb_desc_rgba4444;
extern const pqfmt_rgb_desc_s g_rgb_desc_abgr4444;
extern const pqfmt_rgb_desc_s g_rgb_desc_rgba1010102;
extern const pqfmt_rgb_desc_s g_rgb_desc_abgr1010102;
extern const pqfmt_rgb_desc_s g_rgb_desc_abgr2101010;

/**
 * RGB format name strings
 */
extern const char *pqfmt_rgb_order_name(pqfmt_rgb_order_e order);
extern const char *pqfmt_alpha_pos_name(pqfmt_alpha_pos_e pos);
extern const char *pqfmt_rgb_layout_name(pqfmt_rgb_layout_e layout);

/**
 * RGB format descriptor initialization function
 */
extern void pqfmt_rgb_desc_init(pqfmt_rgb_desc_s *desc, pqfmt_alpha_pos_e alpha_pos, pqfmt_rgb_order_e order,
    pqfmt_rgb_layout_e layout, uint8_t comp_bits[4], uint8_t bpp);

/**
 * RGB format information query functions
 */
extern bool pqfmt_rgb_desc_is_valid(const pqfmt_rgb_desc_s *desc);
extern bool pqfmt_rgb_desc_has_alpha(const pqfmt_rgb_desc_s *desc);
extern bool pqfmt_rgb_desc_is_bgr_order(const pqfmt_rgb_desc_s *desc);
extern uint8_t pqfmt_rgb_desc_get_channel_bits(const pqfmt_rgb_desc_s *desc, uint8_t *r, uint8_t *g, uint8_t *b, uint8_t *a);

/**
 * RGB format conversion helper functions
 */
extern float pqfmt_rgb_desc_calc_pitch_ratio(const pqfmt_rgb_desc_s *desc);
extern size_t pqfmt_rgb_desc_calc_framesize(const pqfmt_rgb_desc_s *desc, int w, int h, int stride);

/**
 * RGB format comparison function
 */
extern bool pqfmt_rgb_desc_equal(const pqfmt_rgb_desc_s *desc1, const pqfmt_rgb_desc_s *desc2);

/**
 * RGB format information print function (for debugging)
 */
extern void pqfmt_rgb_desc_print(const pqfmt_rgb_desc_s *desc);

#ifdef __cplusplus
}
#endif

#endif
