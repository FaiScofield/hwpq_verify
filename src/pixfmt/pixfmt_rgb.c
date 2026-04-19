/**
 * @copyright: Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @brief:     RGB format descriptor implementation
 * @author:    vance.wu@rock-chips.com
 * @create:    2026-04-16
 */

#include "pixfmt_rgb.h"
#include "pixfmt.h"
#include "verify_com.h"

#include <stdio.h>
#include <string.h>
#include <assert.h>

const pixfmt_rgb_desc_s g_rgb_desc_rgb888 = {
    .order = PIXFMT_RGB_ORDER_RGB,
    .alpha_pos = PIXFMT_ALPHA_NONE,
    .comp_bits = {8, 8, 8, 0},
};

const pixfmt_rgb_desc_s g_rgb_desc_bgr888 = {
    .order = PIXFMT_RGB_ORDER_BGR,
    .alpha_pos = PIXFMT_ALPHA_NONE,
    .comp_bits = {8, 8, 8, 0},
};

const pixfmt_rgb_desc_s g_rgb_desc_rgba8888 = {
    .order = PIXFMT_RGB_ORDER_RGB,
    .alpha_pos = PIXFMT_ALPHA_AT_LSB,
    .comp_bits = {8, 8, 8, 8},
};

const pixfmt_rgb_desc_s g_rgb_desc_bgra8888 = {
    .order = PIXFMT_RGB_ORDER_BGR,
    .alpha_pos = PIXFMT_ALPHA_AT_LSB,
    .comp_bits = {8, 8, 8, 8},
};

const pixfmt_rgb_desc_s g_rgb_desc_argb8888 = {
    .order = PIXFMT_RGB_ORDER_RGB,
    .alpha_pos = PIXFMT_ALPHA_AT_MSB,
    .comp_bits = {8, 8, 8, 8},
};

const pixfmt_rgb_desc_s g_rgb_desc_abgr8888 = {
    .order = PIXFMT_RGB_ORDER_BGR,
    .alpha_pos = PIXFMT_ALPHA_AT_MSB,
    .comp_bits = {8, 8, 8, 8},
};

const pixfmt_rgb_desc_s g_rgb_desc_rgb332 = {
    .order = PIXFMT_RGB_ORDER_BGR,
    .alpha_pos = PIXFMT_ALPHA_NONE,
    .comp_bits = {3, 3, 2, 0},
};

const pixfmt_rgb_desc_s g_rgb_desc_bgr233 = {
    .order = PIXFMT_RGB_ORDER_RGB,
    .alpha_pos = PIXFMT_ALPHA_NONE,
    .comp_bits = {3, 3, 2, 0},
};

const pixfmt_rgb_desc_s g_rgb_desc_rgb565 = {
    .order = PIXFMT_RGB_ORDER_BGR,
    .alpha_pos = PIXFMT_ALPHA_NONE,
    .comp_bits = {5, 6, 5, 0},
};

const pixfmt_rgb_desc_s g_rgb_desc_bgr565 = {
    .order = PIXFMT_RGB_ORDER_RGB,
    .alpha_pos = PIXFMT_ALPHA_NONE,
    .comp_bits = {5, 6, 5, 0},
};

const pixfmt_rgb_desc_s g_rgb_desc_rgba5551 = {
    .order = PIXFMT_RGB_ORDER_BGR,
    .alpha_pos = PIXFMT_ALPHA_AT_LSB,
    .comp_bits = {5, 5, 5, 1},
};

const pixfmt_rgb_desc_s g_rgb_desc_abgr1555 = {
    .order = PIXFMT_RGB_ORDER_RGB,
    .alpha_pos = PIXFMT_ALPHA_AT_MSB,
    .comp_bits = {5, 5, 5, 1},
};

const pixfmt_rgb_desc_s g_rgb_desc_rgba4444 = {
    .order = PIXFMT_RGB_ORDER_BGR,
    .alpha_pos = PIXFMT_ALPHA_AT_LSB,
    .comp_bits = {4, 4, 4, 4},
};

const pixfmt_rgb_desc_s g_rgb_desc_abgr4444 = {
    .order = PIXFMT_RGB_ORDER_RGB,
    .alpha_pos = PIXFMT_ALPHA_AT_MSB,
    .comp_bits = {4, 4, 4, 4},
};

const pixfmt_rgb_desc_s g_rgb_desc_rgba1010102 = {
    .order = PIXFMT_RGB_ORDER_BGR,
    .alpha_pos = PIXFMT_ALPHA_AT_LSB,
    .comp_bits = {10, 10, 10, 2},
};

const pixfmt_rgb_desc_s g_rgb_desc_abgr2101010 = {
    .order = PIXFMT_RGB_ORDER_RGB,
    .alpha_pos = PIXFMT_ALPHA_AT_MSB,
    .comp_bits = {10, 10, 10, 2},
};

const pixfmt_rgb_desc_s g_rgb_desc_rgba10lsb = {
    .order = PIXFMT_RGB_ORDER_RGB,
    .alpha_pos = PIXFMT_ALPHA_AT_MSB,
    .comp_bits = {10, 10, 10, 10},
};

const char *pixfmt_rgb_order_name(pixfmt_rgb_order_e order)
{
    switch (order) {
    case PIXFMT_RGB_ORDER_RGB: return "RGB";
    case PIXFMT_RGB_ORDER_BGR: return "BGR";
    default:                   return "UnknownRgbOrder";
    }
}

const char *pixfmt_alpha_pos_name(pixfmt_alpha_pos_e pos)
{
    switch (pos) {
    case PIXFMT_ALPHA_NONE:   return "NoAlpha";
    case PIXFMT_ALPHA_AT_LSB: return "AlphaInLSM";
    case PIXFMT_ALPHA_AT_MSB: return "AlphaInMSB";
    default:                  return "UnknownAlphaPos";
    }
}

bool pixfmt_rgb_desc_is_valid(const pixfmt_rgb_desc_s *desc)
{
    if (!desc)
        return false;
    if (desc->comp_bits[0] == 0 || desc->comp_bits[1] == 0 || desc->comp_bits[2] == 0)
        return false;
    return true;
}

bool pixfmt_rgb_desc_has_alpha(const pixfmt_rgb_desc_s *desc) { return desc ? desc->comp_bits[3] > 0 : false; }

bool pixfmt_rgb_desc_is_bgr_order(const pixfmt_rgb_desc_s *desc)
{
    return desc ? desc->order == PIXFMT_RGB_ORDER_BGR : false;
}

uint8_t pixfmt_rgb_desc_get_channel_bits(const pixfmt_rgb_desc_s *desc, uint8_t *r, uint8_t *g, uint8_t *b, uint8_t *a)
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

int pixfmt_rgb_get_min_align_width(const pixfmt_attr_s *attr, int wid, int *retAlign)
{
    assert(attr && attr->base_type == PIXFMT_TYPE_RGB);
    assert(attr->bpp % 8 == 0);
    if (retAlign)
        *retAlign = 1;
    return wid;
}

int pixfmt_rgb_get_min_pitches(const pixfmt_attr_s *attr, int wid, int *retPitch)
{
    assert(attr && attr->base_type == PIXFMT_TYPE_RGB && attr->desc.rgb);
    assert(retPitch != NULL);

    if (attr->layout == PIXFMT_LAYOUT_INTERLEAVED) {
        *retPitch = attr->bpp * wid / 8;
        return 0;
    }

    LOGE("pixfmt_rgb_calc_pitch_ratio: rgb layout %d not supported!", attr->layout);
    return PIXFMT_INVALID;
}

size_t pixfmt_rgb_get_framesize(const pixfmt_attr_s *attr, int w, int h, int rowpitch, size_t *retPlaneSize)
{
    assert(attr && attr->base_type == PIXFMT_TYPE_RGB);

    if (rowpitch < w)
        pixfmt_rgb_get_min_pitches(attr, w, &rowpitch);
    size_t size = rowpitch * h;

    if (retPlaneSize)
        *retPlaneSize = size;
    return size;
}

bool pixfmt_rgb_desc_equal(const pixfmt_rgb_desc_s *desc1, const pixfmt_rgb_desc_s *desc2)
{
    if (!desc1 || !desc2)
        return false;

    return desc1->order == desc2->order && desc1->alpha_pos == desc2->alpha_pos &&
           memcmp(desc1->comp_bits, desc2->comp_bits, 4) == 0;
}

void pixfmt_rgb_desc_print(const pixfmt_rgb_desc_s *desc)
{
    LOGI(" - order: %d %s%s%s\n", desc->order, desc->alpha_pos == PIXFMT_ALPHA_AT_LSB ? "A" : "", pixfmt_rgb_order_name(desc->order),
        desc->alpha_pos == PIXFMT_ALPHA_AT_MSB ? "A" : "");
    LOGI(" - bits: R-%d G-%d B-%d A-%d\n", desc->comp_bits[0], desc->comp_bits[1], desc->comp_bits[2], desc->comp_bits[3]);
}
