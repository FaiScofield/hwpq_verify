/**
 * @copyright: Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @brief:     RGB 格式描述符实现
 * @author:
 * @create:    2026-04-16
 */

#include "pqfmt_rgb.h"
#include <string.h>

const pqfmt_rgb_desc_s g_rgb_fmt_rgb888 = {
    .order = PQFMT_RGB_ORDER_RGB,
    .alpha_pos = PQFMT_ALPHA_NONE,
    .layout = PQFMT_RGB_LAYOUT_PACKED,
    .is_packed = false,
    .has_padding = false,
    .r_bits = 8,
    .g_bits = 8,
    .b_bits = 8,
    .a_bits = 0,
    .bpp = 24,
    .elem_bits = 8,
};

const pqfmt_rgb_desc_s g_rgb_fmt_bgr888 = {
    .order = PQFMT_RGB_ORDER_BGR,
    .alpha_pos = PQFMT_ALPHA_NONE,
    .layout = PQFMT_RGB_LAYOUT_PACKED,
    .is_packed = false,
    .has_padding = false,
    .r_bits = 8,
    .g_bits = 8,
    .b_bits = 8,
    .a_bits = 0,
    .bpp = 24,
    .elem_bits = 8,
};

const pqfmt_rgb_desc_s g_rgb_fmt_rgba8888 = {
    .order = PQFMT_RGB_ORDER_RGB,
    .alpha_pos = PQFMT_ALPHA_LOW,
    .layout = PQFMT_RGB_LAYOUT_PACKED,
    .is_packed = false,
    .has_padding = false,
    .r_bits = 8,
    .g_bits = 8,
    .b_bits = 8,
    .a_bits = 8,
    .bpp = 32,
    .elem_bits = 8,
};

const pqfmt_rgb_desc_s g_rgb_fmt_bgra8888 = {
    .order = PQFMT_RGB_ORDER_BGR,
    .alpha_pos = PQFMT_ALPHA_LOW,
    .layout = PQFMT_RGB_LAYOUT_PACKED,
    .is_packed = false,
    .has_padding = false,
    .r_bits = 8,
    .g_bits = 8,
    .b_bits = 8,
    .a_bits = 8,
    .bpp = 32,
    .elem_bits = 8,
};

const pqfmt_rgb_desc_s g_rgb_fmt_argb8888 = {
    .order = PQFMT_RGB_ORDER_RGB,
    .alpha_pos = PQFMT_ALPHA_HIGH,
    .layout = PQFMT_RGB_LAYOUT_PACKED,
    .is_packed = false,
    .has_padding = false,
    .r_bits = 8,
    .g_bits = 8,
    .b_bits = 8,
    .a_bits = 8,
    .bpp = 32,
    .elem_bits = 8,
};

const pqfmt_rgb_desc_s g_rgb_fmt_abgr8888 = {
    .order = PQFMT_RGB_ORDER_BGR,
    .alpha_pos = PQFMT_ALPHA_HIGH,
    .layout = PQFMT_RGB_LAYOUT_PACKED,
    .is_packed = false,
    .has_padding = false,
    .r_bits = 8,
    .g_bits = 8,
    .b_bits = 8,
    .a_bits = 8,
    .bpp = 32,
    .elem_bits = 8,
};

const pqfmt_rgb_desc_s g_rgb_fmt_rgb332 = {
    .order = PQFMT_RGB_ORDER_RGB,
    .alpha_pos = PQFMT_ALPHA_NONE,
    .layout = PQFMT_RGB_LAYOUT_PACKED,
    .is_packed = true,
    .has_padding = false,
    .r_bits = 3,
    .g_bits = 3,
    .b_bits = 2,
    .a_bits = 0,
    .bpp = 8,
    .elem_bits = 8,
};

const pqfmt_rgb_desc_s g_rgb_fmt_bgr233 = {
    .order = PQFMT_RGB_ORDER_BGR,
    .alpha_pos = PQFMT_ALPHA_NONE,
    .layout = PQFMT_RGB_LAYOUT_PACKED,
    .is_packed = true,
    .has_padding = false,
    .r_bits = 2,
    .g_bits = 3,
    .b_bits = 3,
    .a_bits = 0,
    .bpp = 8,
    .elem_bits = 8,
};

const pqfmt_rgb_desc_s g_rgb_fmt_rgb565 = {
    .order = PQFMT_RGB_ORDER_RGB,
    .alpha_pos = PQFMT_ALPHA_NONE,
    .layout = PQFMT_RGB_LAYOUT_PACKED,
    .is_packed = true,
    .has_padding = false,
    .r_bits = 5,
    .g_bits = 6,
    .b_bits = 5,
    .a_bits = 0,
    .bpp = 16,
    .elem_bits = 16,
};

const pqfmt_rgb_desc_s g_rgb_fmt_bgr565 = {
    .order = PQFMT_RGB_ORDER_BGR,
    .alpha_pos = PQFMT_ALPHA_NONE,
    .layout = PQFMT_RGB_LAYOUT_PACKED,
    .is_packed = true,
    .has_padding = false,
    .r_bits = 5,
    .g_bits = 6,
    .b_bits = 5,
    .a_bits = 0,
    .bpp = 16,
    .elem_bits = 16,
};

const pqfmt_rgb_desc_s g_rgb_fmt_rgba5551 = {
    .order = PQFMT_RGB_ORDER_RGB,
    .alpha_pos = PQFMT_ALPHA_LOW,
    .layout = PQFMT_RGB_LAYOUT_PACKED,
    .is_packed = true,
    .has_padding = false,
    .r_bits = 5,
    .g_bits = 5,
    .b_bits = 5,
    .a_bits = 1,
    .bpp = 16,
    .elem_bits = 16,
};

const pqfmt_rgb_desc_s g_rgb_fmt_argb1555 = {
    .order = PQFMT_RGB_ORDER_RGB,
    .alpha_pos = PQFMT_ALPHA_HIGH,
    .layout = PQFMT_RGB_LAYOUT_PACKED,
    .is_packed = true,
    .has_padding = false,
    .r_bits = 5,
    .g_bits = 5,
    .b_bits = 5,
    .a_bits = 1,
    .bpp = 16,
    .elem_bits = 16,
};

const pqfmt_rgb_desc_s g_rgb_fmt_rgba1010102 = {
    .order = PQFMT_RGB_ORDER_RGB,
    .alpha_pos = PQFMT_ALPHA_LOW,
    .layout = PQFMT_RGB_LAYOUT_PACKED,
    .is_packed = true,
    .has_padding = true,
    .r_bits = 10,
    .g_bits = 10,
    .b_bits = 10,
    .a_bits = 2,
    .bpp = 32,
    .elem_bits = 32,
};

const pqfmt_rgb_desc_s g_rgb_fmt_bgra1010102 = {
    .order = PQFMT_RGB_ORDER_BGR,
    .alpha_pos = PQFMT_ALPHA_LOW,
    .layout = PQFMT_RGB_LAYOUT_PACKED,
    .is_packed = true,
    .has_padding = true,
    .r_bits = 10,
    .g_bits = 10,
    .b_bits = 10,
    .a_bits = 2,
    .bpp = 32,
    .elem_bits = 32,
};

const char* pqfmt_rgb_order_name(pqfmt_rgb_order_e order) {
    switch (order) {
        case PQFMT_RGB_ORDER_RGB: return "RGB";
        case PQFMT_RGB_ORDER_BGR: return "BGR";
        case PQFMT_RGB_ORDER_GRB: return "GRB";
        case PQFMT_RGB_ORDER_GBR: return "GBR";
        default: return "Unknown";
    }
}

const char* pqfmt_alpha_pos_name(pqfmt_alpha_pos_e pos) {
    switch (pos) {
        case PQFMT_ALPHA_NONE: return "NoAlpha";
        case PQFMT_ALPHA_LOW: return "AlphaLow";
        case PQFMT_ALPHA_HIGH: return "AlphaHigh";
        default: return "Unknown";
    }
}

const char* pqfmt_rgb_layout_name(pqfmt_rgb_layout_e layout) {
    switch (layout) {
        case PQFMT_RGB_LAYOUT_PACKED: return "Packed";
        case PQFMT_RGB_LAYOUT_PLANAR: return "Planar";
        default: return "Unknown";
    }
}

void pqfmt_rgb_desc_init(pqfmt_rgb_desc_s *desc,
                       pqfmt_rgb_order_e order,
                       pqfmt_alpha_pos_e alpha_pos,
                       pqfmt_rgb_layout_e layout,
                       bool is_packed,
                       bool has_padding,
                       uint8_t r_bits,
                       uint8_t g_bits,
                       uint8_t b_bits,
                       uint8_t a_bits,
                       uint8_t bpp,
                       uint8_t elem_bits) {
    if (!desc) return;

    desc->order = order;
    desc->alpha_pos = alpha_pos;
    desc->layout = layout;
    desc->is_packed = is_packed;
    desc->has_padding = has_padding;
    desc->r_bits = r_bits;
    desc->g_bits = g_bits;
    desc->b_bits = b_bits;
    desc->a_bits = a_bits;
    desc->bpp = bpp;
    desc->elem_bits = elem_bits;
}

bool pqfmt_rgb_desc_is_valid(const pqfmt_rgb_desc_s *desc) {
    if (!desc) return false;
    if (desc->r_bits == 0 || desc->g_bits == 0 || desc->b_bits == 0) return false;
    if (desc->bpp == 0) return false;
    return true;
}

bool pqfmt_rgb_desc_has_alpha(const pqfmt_rgb_desc_s *desc) {
    return desc ? desc->a_bits > 0 : false;
}

bool pqfmt_rgb_desc_is_bgr_order(const pqfmt_rgb_desc_s *desc) {
    return desc ? desc->order == PQFMT_RGB_ORDER_BGR : false;
}

uint8_t pqfmt_rgb_desc_get_channel_bits(const pqfmt_rgb_desc_s *desc,
                                        uint8_t *r,
                                        uint8_t *g,
                                        uint8_t *b,
                                        uint8_t *a) {
    if (!desc) return 0;

    if (r) *r = desc->r_bits;
    if (g) *g = desc->g_bits;
    if (b) *b = desc->b_bits;
    if (a) *a = desc->a_bits;

    return desc->r_bits + desc->g_bits + desc->b_bits + desc->a_bits;
}

float pqfmt_rgb_desc_calc_pitch_ratio(const pqfmt_rgb_desc_s *desc) {
    if (!desc) return 0.0f;

    if (desc->layout == PQFMT_RGB_LAYOUT_PLANAR) {
        return 1.0f;
    }

    return desc->bpp / 8.0f;
}

size_t pqfmt_rgb_desc_calc_framesize(const pqfmt_rgb_desc_s *desc,
                                   int w,
                                   int h,
                                   int stride) {
    if (!desc) return 0;

    int pitch = stride > 0 ? stride : (int)(w * pqfmt_rgb_desc_calc_pitch_ratio(desc));
    return (size_t)(pitch * h);
}

bool pqfmt_rgb_desc_equal(const pqfmt_rgb_desc_s *desc1,
                           const pqfmt_rgb_desc_s *desc2) {
    if (!desc1 || !desc2) return false;

    return desc1->order == desc2->order &&
           desc1->alpha_pos == desc2->alpha_pos &&
           desc1->layout == desc2->layout &&
           desc1->is_packed == desc2->is_packed &&
           desc1->has_padding == desc2->has_padding &&
           desc1->r_bits == desc2->r_bits &&
           desc1->g_bits == desc2->g_bits &&
           desc1->b_bits == desc2->b_bits &&
           desc1->a_bits == desc2->a_bits &&
           desc1->bpp == desc2->bpp &&
           desc1->elem_bits == desc2->elem_bits;
}

void pqfmt_rgb_desc_print(const pqfmt_rgb_desc_s *desc) {
    if (!desc) {
        printf("RGB Format: NULL\n");
        return;
    }

    printf("RGB Format:\n");
    printf("  Order: %s\n", pqfmt_rgb_order_name(desc->order));
    printf("  Alpha: %s\n", pqfmt_alpha_pos_name(desc->alpha_pos));
    printf("  Layout: %s\n", pqfmt_rgb_layout_name(desc->layout));
    printf("  Packed: %s\n", desc->is_packed ? "Yes" : "No");
    printf("  Padding: %s\n", desc->has_padding ? "Yes" : "No");
    printf("  Bits: R%d G%d B%d A%d\n", desc->r_bits, desc->g_bits, desc->b_bits, desc->a_bits);
    printf("  BPP: %d\n", desc->bpp);
    printf("  ElemBits: %d\n", desc->elem_bits);
}
