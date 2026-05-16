/**
 * @copyright: Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @brief:     RGB format descriptor and related helper functions
 * @author:    vance.wu@rock-chips.com
 * @create:    2026-04-16
 */

#ifndef _PIXFMT_RGB_H_
#define _PIXFMT_RGB_H_

#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>

/**
 * RGB channel order from LSB to MSB
 */
typedef enum pixfmt_rgb_order {
    PIXFMT_RGB_ORDER_RGB,
    PIXFMT_RGB_ORDER_BGR,
} pixfmt_rgb_order_e;

/**
 * Alpha position enumeration
 */
typedef enum pixfmt_alpha_pos {
    PIXFMT_NO_ALPHA,
    PIXFMT_ALPHA_AT_LSB,
    PIXFMT_ALPHA_AT_MSB,
} pixfmt_alpha_pos_e;

/**
 * RGB format descriptor
 */
typedef struct pixfmt_rgb_desc {
    pixfmt_alpha_pos_e alpha_pos; // at LSB or MSB
    pixfmt_rgb_order_e order;     // always form LSB to MSB
    uint8_t comp_bits[4];         // always in R-G-B-A order
} pixfmt_rgb_desc_s;

/**
 * RGB predefined format descriptors
 */
extern const pixfmt_rgb_desc_s g_rgb_desc_rgb888;
extern const pixfmt_rgb_desc_s g_rgb_desc_bgr888;
extern const pixfmt_rgb_desc_s g_rgb_desc_rgba8888;
extern const pixfmt_rgb_desc_s g_rgb_desc_bgra8888;
extern const pixfmt_rgb_desc_s g_rgb_desc_argb8888;
extern const pixfmt_rgb_desc_s g_rgb_desc_abgr8888;
extern const pixfmt_rgb_desc_s g_rgb_desc_rgb10lsb;
extern const pixfmt_rgb_desc_s g_rgb_desc_rgba10lsb;
extern const pixfmt_rgb_desc_s g_rgb_desc_rgb332;
extern const pixfmt_rgb_desc_s g_rgb_desc_bgr233;
extern const pixfmt_rgb_desc_s g_rgb_desc_rgb565;
extern const pixfmt_rgb_desc_s g_rgb_desc_bgr565;
extern const pixfmt_rgb_desc_s g_rgb_desc_rgba5551;
extern const pixfmt_rgb_desc_s g_rgb_desc_abgr1555;
extern const pixfmt_rgb_desc_s g_rgb_desc_rgba4444;
extern const pixfmt_rgb_desc_s g_rgb_desc_abgr4444;
extern const pixfmt_rgb_desc_s g_rgb_desc_rgba1010102;
extern const pixfmt_rgb_desc_s g_rgb_desc_abgr2101010;

/* forward declaration */
struct pixfmt_attr;

#ifdef __cplusplus
extern "C" {
#endif

/**
 * RGB format name strings
 */
extern const char *pixfmt_rgb_order_name(pixfmt_rgb_order_e order);
extern const char *pixfmt_alpha_pos_name(pixfmt_alpha_pos_e pos);

/**
 * RGB format information query functions
 */
extern bool pixfmt_rgb_desc_is_valid(const pixfmt_rgb_desc_s *desc);
extern bool pixfmt_rgb_desc_has_alpha(const pixfmt_rgb_desc_s *desc);
extern bool pixfmt_rgb_desc_is_bgr_order(const pixfmt_rgb_desc_s *desc);
extern uint8_t pixfmt_rgb_desc_get_channel_bits(const pixfmt_rgb_desc_s *desc, uint8_t *r, uint8_t *g, uint8_t *b, uint8_t *a);

/**
 * RGB format conversion helper functions
 */
extern int pixfmt_rgb_get_min_align_width(const struct pixfmt_attr *attr, int wid, int *retAlign);
extern int pixfmt_rgb_get_min_pitches(const struct pixfmt_attr *attr, int wid, int *retPitch);
extern size_t pixfmt_rgb_get_framesize(const struct pixfmt_attr *attr, int w, int h, int rowpitch, size_t *retPlaneSize);

/**
 * RGB format comparison function
 */
extern bool pixfmt_rgb_desc_equal(const pixfmt_rgb_desc_s *desc1, const pixfmt_rgb_desc_s *desc2);

/**
 * RGB format information print function (for debugging)
 */
extern void pixfmt_rgb_dump_desc(const pixfmt_rgb_desc_s *desc);

#ifdef __cplusplus
}
#endif

#endif
