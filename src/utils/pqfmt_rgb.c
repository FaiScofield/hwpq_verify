/**
 * @copyright: Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @brief:     RGB format descriptor implementation
 * @author:
 * @create:    2026-04-16
 */

#include "pqfmt_rgb.h"
#include <stdio.h>
#include <string.h>

const pqfmt_rgb_desc_s g_rgb_desc_rgb888 = {
    .order = PQFMT_RGB_ORDER_RGB,
    .alpha_pos = PQFMT_ALPHA_NONE,
    .layout = PQFMT_RGB_LAYOUT_PACKED,
    .comp_bits = {8, 8, 8, 0},
};

const pqfmt_rgb_desc_s g_rgb_desc_bgr888 = {
    .order = PQFMT_RGB_ORDER_BGR,
    .alpha_pos = PQFMT_ALPHA_NONE,
    .layout = PQFMT_RGB_LAYOUT_PACKED,
    .comp_bits = {8, 8, 8, 0},
};

const pqfmt_rgb_desc_s g_rgb_desc_rgba8888 = {
    .order = PQFMT_RGB_ORDER_RGB,
    .alpha_pos = PQFMT_ALPHA_LSM,
    .layout = PQFMT_RGB_LAYOUT_PACKED,
    .comp_bits = {8, 8, 8, 8},
};

const pqfmt_rgb_desc_s g_rgb_desc_bgra8888 = {
    .order = PQFMT_RGB_ORDER_BGR,
    .alpha_pos = PQFMT_ALPHA_LSM,
    .layout = PQFMT_RGB_LAYOUT_PACKED,
    .comp_bits = {8, 8, 8, 8},
};

const pqfmt_rgb_desc_s g_rgb_desc_argb8888 = {
    .order = PQFMT_RGB_ORDER_RGB,
    .alpha_pos = PQFMT_ALPHA_MSB,
    .layout = PQFMT_RGB_LAYOUT_PACKED,
    .comp_bits = {8, 8, 8, 8},
};

const pqfmt_rgb_desc_s g_rgb_desc_abgr8888 = {
    .order = PQFMT_RGB_ORDER_BGR,
    .alpha_pos = PQFMT_ALPHA_MSB,
    .layout = PQFMT_RGB_LAYOUT_PACKED,
    .comp_bits = {8, 8, 8, 8},
};

const pqfmt_rgb_desc_s g_rgb_desc_rgb332 = {
    .order = PQFMT_RGB_ORDER_RGB,
    .alpha_pos = PQFMT_ALPHA_NONE,
    .layout = PQFMT_RGB_LAYOUT_PACKED,
    .comp_bits = {3, 3, 2, 0},
};

const pqfmt_rgb_desc_s g_rgb_desc_bgr233 = {
    .order = PQFMT_RGB_ORDER_BGR,
    .alpha_pos = PQFMT_ALPHA_NONE,
    .layout = PQFMT_RGB_LAYOUT_PACKED,
    .comp_bits = {2, 3, 3, 0},
};

const pqfmt_rgb_desc_s g_rgb_desc_rgb565 = {
    .order = PQFMT_RGB_ORDER_RGB,
    .alpha_pos = PQFMT_ALPHA_NONE,
    .layout = PQFMT_RGB_LAYOUT_PACKED,
    .comp_bits = {5, 6, 5, 0},
};

const pqfmt_rgb_desc_s g_rgb_desc_bgr565 = {
    .order = PQFMT_RGB_ORDER_BGR,
    .alpha_pos = PQFMT_ALPHA_NONE,
    .layout = PQFMT_RGB_LAYOUT_PACKED,
    .comp_bits = {5, 6, 5, 0},
};

const pqfmt_rgb_desc_s g_rgb_desc_rgba5551 = {
    .order = PQFMT_RGB_ORDER_RGB,
    .alpha_pos = PQFMT_ALPHA_LSM,
    .layout = PQFMT_RGB_LAYOUT_PACKED,
    .comp_bits = {5, 5, 5, 1},
};

const pqfmt_rgb_desc_s g_rgb_desc_abgr1555 = {
    .order = PQFMT_RGB_ORDER_BGR,
    .alpha_pos = PQFMT_ALPHA_MSB,
    .layout = PQFMT_RGB_LAYOUT_PACKED,
    .comp_bits = {5, 5, 5, 1},
};

const pqfmt_rgb_desc_s g_rgb_desc_rgba4444 = {
    .order = PQFMT_RGB_ORDER_RGB,
    .alpha_pos = PQFMT_ALPHA_LSM,
    .layout = PQFMT_RGB_LAYOUT_PACKED,
    .comp_bits = {4, 4, 4, 4},
};

const pqfmt_rgb_desc_s g_rgb_desc_abgr4444 = {
    .order = PQFMT_RGB_ORDER_BGR,
    .alpha_pos = PQFMT_ALPHA_MSB,
    .layout = PQFMT_RGB_LAYOUT_PACKED,
    .comp_bits = {4, 4, 4, 4},
};

const pqfmt_rgb_desc_s g_rgb_desc_rgba1010102 = {
    .order = PQFMT_RGB_ORDER_RGB,
    .alpha_pos = PQFMT_ALPHA_LSM,
    .layout = PQFMT_RGB_LAYOUT_PACKED,
    .comp_bits = {10, 10, 10, 2},
};

const pqfmt_rgb_desc_s g_rgb_desc_abgr1010102 = {
    .order = PQFMT_RGB_ORDER_BGR,
    .alpha_pos = PQFMT_ALPHA_MSB,
    .layout = PQFMT_RGB_LAYOUT_PACKED,
    .comp_bits = {10, 10, 10, 2},
};

const pqfmt_rgb_desc_s g_rgb_desc_abgr2101010 = {
    .order = PQFMT_RGB_ORDER_BGR,
    .alpha_pos = PQFMT_ALPHA_MSB,
    .layout = PQFMT_RGB_LAYOUT_PACKED,
    .comp_bits = {10, 10, 10, 2},
};

const char *pqfmt_rgb_order_name(pqfmt_rgb_order_e order)
{
    switch (order) {
    case PQFMT_RGB_ORDER_RGB: return "RGB";
    case PQFMT_RGB_ORDER_BGR: return "BGR";
    default:                  return "Unknown";
    }
}

const char *pqfmt_alpha_pos_name(pqfmt_alpha_pos_e pos)
{
    switch (pos) {
    case PQFMT_ALPHA_NONE: return "NoAlpha";
    case PQFMT_ALPHA_LSM:  return "AlphaLSM";
    case PQFMT_ALPHA_MSB:  return "AlphaMSB";
    default:               return "Unknown";
    }
}

const char *pqfmt_rgb_layout_name(pqfmt_rgb_layout_e layout)
{
    switch (layout) {
    case PQFMT_RGB_LAYOUT_PACKED:     return "Packed";
    case PQFMT_RGB_LAYOUT_PLANAR:     return "Planar";
    case PQFMT_RGB_LAYOUT_SEMIPLANAR: return "Semi-Planar";
    default:                          return "Unknown";
    }
}

void pqfmt_rgb_desc_init(pqfmt_rgb_desc_s *desc, pqfmt_alpha_pos_e alpha_pos, pqfmt_rgb_order_e order,
    pqfmt_rgb_layout_e layout, uint8_t comp_bits[4], uint8_t bpp)
{
    if (!desc)
        return;

    desc->alpha_pos = alpha_pos;
    desc->order = order;
    desc->layout = layout;
    memcpy(desc->comp_bits, comp_bits, 4);
}

bool pqfmt_rgb_desc_is_valid(const pqfmt_rgb_desc_s *desc)
{
    if (!desc)
        return false;
    if (desc->comp_bits[0] == 0 || desc->comp_bits[1] == 0 || desc->comp_bits[2] == 0)
        return false;
    return true;
}

bool pqfmt_rgb_desc_has_alpha(const pqfmt_rgb_desc_s *desc) { return desc ? desc->comp_bits[3] > 0 : false; }

bool pqfmt_rgb_desc_is_bgr_order(const pqfmt_rgb_desc_s *desc)
{
    return desc ? desc->order == PQFMT_RGB_ORDER_BGR : false;
}

uint8_t pqfmt_rgb_desc_get_channel_bits(const pqfmt_rgb_desc_s *desc, uint8_t *r, uint8_t *g, uint8_t *b, uint8_t *a)
{
    if (!desc)
        return 0;

    if (r)
        *r = desc->comp_bits[0];
    if (g)
        *g = desc->comp_bits[1];
    if (b)
        *b = desc->comp_bits[2];
    if (a)
        *a = desc->comp_bits[3];

    return desc->comp_bits[0] + desc->comp_bits[1] + desc->comp_bits[2] + desc->comp_bits[3];
}

float pqfmt_rgb_desc_calc_pitch_ratio(const pqfmt_rgb_desc_s *desc)
{
    if (!desc)
        return 0.0f;

    if (desc->layout == PQFMT_RGB_LAYOUT_PLANAR) {
        return 1.0f;
    }

    uint8_t total_bits = desc->comp_bits[0] + desc->comp_bits[1] + desc->comp_bits[2] + desc->comp_bits[3];
    return (float)total_bits / 8.0f;
}

size_t pqfmt_rgb_desc_calc_framesize(const pqfmt_rgb_desc_s *desc, int w, int h, int stride)
{
    if (!desc)
        return 0;

    int pitch = stride > 0 ? stride : (int)(w * pqfmt_rgb_desc_calc_pitch_ratio(desc));
    return (size_t)(pitch * h);
}

bool pqfmt_rgb_desc_equal(const pqfmt_rgb_desc_s *desc1, const pqfmt_rgb_desc_s *desc2)
{
    if (!desc1 || !desc2)
        return false;

    return desc1->order == desc2->order && desc1->alpha_pos == desc2->alpha_pos && desc1->layout == desc2->layout &&
           memcmp(desc1->comp_bits, desc2->comp_bits, 4) == 0;
}

void pqfmt_rgb_desc_print(const pqfmt_rgb_desc_s *desc)
{
    if (!desc) {
        printf("RGB Format: NULL\n");
        return;
    }

    printf("RGB Format:\n");
    printf("  Order: %s\n", pqfmt_rgb_order_name(desc->order));
    printf("  Alpha: %s\n", pqfmt_alpha_pos_name(desc->alpha_pos));
    printf("  Layout: %s\n", pqfmt_rgb_layout_name(desc->layout));
    printf("  Bits: R%d G%d B%d A%d\n", desc->comp_bits[0], desc->comp_bits[1], desc->comp_bits[2], desc->comp_bits[3]);
}
