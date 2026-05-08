/**
 * @copyright: Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @brief:     Image format conversion module implementation
 * @author:    vance.wu@rock-chips.com
 * @create:    2026-04-16
 */

#include "pixfmt_cvt.h"
#include "pixfmt.h"
#include "verify_com.h"

#include <string.h>
#include <math.h>
#include <assert.h>

extern int pixfmt_cvt_r2r_to_common(const pixfmt_frame_s *frame0, pixfmt_frame_s *frame1)
{
    assert(frame0 && frame1);
    int ret = 0;

    const pixfmt_attr_s *src_attr = pixfmt_get_attr(frame0->fmt);
    const pixfmt_attr_s *dst_attr = pixfmt_get_attr(frame1->fmt);
    const pixfmt_rgb_desc_s *src_desc = src_attr->desc.rgb;
    const pixfmt_rgb_desc_s *dst_desc = dst_attr->desc.rgb;
    assert(src_attr && dst_attr);

    int r_shift = 0;
    int g_shift = 0;
    int b_shift = 0;
    int a_shift = 0;
    if (src_desc->order == PIXFMT_RGB_ORDER_RGB) {
        if (src_desc->alpha_pos == PIXFMT_ALPHA_AT_MSB) {
            r_shift = 0;
            g_shift = src_desc->comp_bits[0];
            b_shift = g_shift + src_desc->comp_bits[1];
            a_shift = b_shift + src_desc->comp_bits[2];
        }
        else { /* ALPHA_AT_LSB or NO_ALPHA */
            a_shift = 0;
            r_shift = src_desc->comp_bits[2];
            g_shift = r_shift + src_desc->comp_bits[0];
            b_shift = g_shift + src_desc->comp_bits[1];
        }
    }
    else {
        if (src_desc->alpha_pos == PIXFMT_ALPHA_AT_MSB) {
            b_shift = 0;
            g_shift = src_desc->comp_bits[0];
            r_shift = g_shift + src_desc->comp_bits[1];
            a_shift = b_shift + src_desc->comp_bits[2];
        }
        else { /* ALPHA_AT_LSB or NO_ALPHA */
            a_shift = 0;
            b_shift = src_desc->comp_bits[2];
            g_shift = r_shift + src_desc->comp_bits[0];
            r_shift = g_shift + src_desc->comp_bits[1];
        }
    }

    const int r_max = (1 << src_desc->comp_bits[0]) - 1;
    const int g_max = (1 << src_desc->comp_bits[1]) - 1;
    const int b_max = (1 << src_desc->comp_bits[2]) - 1;
    const int a_max = src_desc->comp_bits[3] > 0 ? ((1 << src_desc->comp_bits[3]) - 1) : 0;
    const int r_mask = r_max << r_shift;
    const int g_mask = g_max << g_shift;
    const int b_mask = b_max << b_shift;
    const int a_mask = a_max << a_shift;

    bool has_alpha_src = pixfmt_has_alpha(frame0->fmt);
    bool need_alpha_dst = pixfmt_has_alpha(frame1->fmt);
    const int dst_comps = need_alpha_dst ? 4 : 3;

    switch (frame0->fmt) {
    // 8bpp RGB
    case PIXFMT_RGB332:
    case PIXFMT_BGR233: {
        for (int i = 0; i < frame0->hgt; i++) {
            const uint8_t *psrc = (uint8_t *)frame0->addr + i * frame0->pitch;
            uint8_t *pdst = (uint8_t *)frame1->addr + i * frame1->pitch;
            for (int j = 0; j < frame0->wid; j++) {
                const uint8_t val = psrc[j];
                uint16_t r = (val & r_mask) >> r_shift;
                uint16_t g = (val & g_mask) >> g_shift;
                uint16_t b = (val & b_mask) >> b_shift;
                pdst[j * dst_comps + 0] = (r * 255 + (r_max >> 1)) / r_max;
                pdst[j * dst_comps + 1] = (g * 255 + (g_max >> 1)) / g_max;
                pdst[j * dst_comps + 2] = (b * 255 + (b_max >> 1)) / b_max;
                if (need_alpha_dst)
                    pdst[j * dst_comps + 3] = 255;
            }
        }
    } break;
    // 16bpp RGB
    case PIXFMT_RGB565:
    case PIXFMT_BGR565:
    case PIXFMT_RGBA5551:
    case PIXFMT_ABGR1555:
    case PIXFMT_RGBA4444:
    case PIXFMT_ABGR4444: {
        for (int i = 0; i < frame0->hgt; i++) {
            const uint16_t *psrc = (uint16_t *)((uint8_t *)frame0->addr + i * frame0->pitch);
            uint8_t *pdst = (uint8_t *)frame1->addr + i * frame1->pitch;
            for (int j = 0; j < frame0->wid; j++) {
                const uint16_t val = psrc[j];
                uint16_t r = (val & r_mask) >> r_shift;
                uint16_t g = (val & g_mask) >> g_shift;
                uint16_t b = (val & b_mask) >> b_shift;
                uint16_t a = (val & a_mask) >> a_shift;
                pdst[j * dst_comps + 0] = (r * 255 + (r_max >> 1)) / r_max;
                pdst[j * dst_comps + 1] = (g * 255 + (g_max >> 1)) / g_max;
                pdst[j * dst_comps + 2] = (b * 255 + (b_max >> 1)) / b_max;
                if (need_alpha_dst)
                    pdst[j * dst_comps + 3] = has_alpha_src ? (a * 255 + (a_max >> 1)) / a_max : 255;
            }
        }
    } break;
    // 24bpp RGB
    case PIXFMT_RGB888:
    case PIXFMT_BGR888: {
        const bool same_order = src_desc->order == dst_desc->order;
        for (int i = 0; i < frame0->hgt; i++) {
            const uint8_t *psrc = (uint8_t *)frame0->addr + i * frame0->pitch;
            uint8_t *pdst = (uint8_t *)frame1->addr + i * frame1->pitch;
            for (int j = 0, k = 0; j < frame0->wid; j++, k += 3) {
                uint8_t r = psrc[k + 0];
                uint8_t g = psrc[k + 1];
                uint8_t b = psrc[k + 2];
                pdst[j * dst_comps + 0] = same_order ? r : b;
                pdst[j * dst_comps + 1] = g;
                pdst[j * dst_comps + 2] = same_order ? b : r;
                if (need_alpha_dst)
                    pdst[j * dst_comps + 3] = 255;
            }
        }
    } break;
    // 32bpp RGB
    case PIXFMT_RGBA8888:
    case PIXFMT_BGRA8888:
    case PIXFMT_ARGB8888:
    case PIXFMT_ABGR8888: {
        for (int i = 0; i < frame0->hgt; i++) {
            const uint32_t *psrc = (uint32_t *)((uint8_t *)frame0->addr + i * frame0->pitch);
            uint8_t *pdst = (uint8_t *)frame1->addr + i * frame1->pitch;
            for (int j = 0; j < frame0->wid; j++) {
                const uint32_t val = psrc[j];
                uint32_t r = (val & r_mask) >> r_shift;
                uint32_t g = (val & g_mask) >> g_shift;
                uint32_t b = (val & b_mask) >> b_shift;
                uint32_t a = (val & a_mask) >> a_shift;
                pdst[j * dst_comps + 0] = r;
                pdst[j * dst_comps + 1] = g;
                pdst[j * dst_comps + 2] = b;
                if (need_alpha_dst)
                    pdst[j * dst_comps + 3] = has_alpha_src ? a : 255;
            }
        }
    } break;
    // 10bit
    case PIXFMT_RGBA1010102:
    case PIXFMT_ABGR2101010: {

    } break;
    case PIXFMT_RGB10Lsb:
    case PIXFMT_RGBA10Lsb: {

    } break;
    default: {
        LOGE("pixfmt_cvt_r2r_to_common: unsupported format %d!\n", frame0->fmt);
        ret = -1;
    } break;
    }

    return ret;
}

extern int pixfmt_cvt_r2r_from_common(const pixfmt_frame_s *frame0, pixfmt_frame_s *frame1)
{
    assert(frame0 && frame1);
    assert(pixfmt_is_rgb(frame0->fmt));
    assert(pixfmt_is_rgb(frame1->fmt));

    /* copy frame info */
    frame1->clrspc = frame0->clrspc;
    frame1->wid = frame0->wid;
    frame1->hgt = frame0->hgt;
    frame1->vwid = frame0->vwid;
    frame1->vhgt = frame0->vhgt;

    /* calculate pitch and size for target format */
    if (!pixfmt_fill_frame_attr(frame1)) {
        LOGE("pixfmt_cvt_r2r_from_common: failed to fill frame attr!\n");
        return -1;
    }

    /* perform conversion */
    return pixfmt_cvt_impl_r2r(frame0, frame1);
}

static int pixfmt_cvt_impl_r2r(const pixfmt_frame_s *frame0, pixfmt_frame_s *frame1)
{
    assert(frame0 && frame1);
    assert(pixfmt_is_rgb(frame0->fmt));
    assert(pixfmt_is_rgb(frame1->fmt));

    const pixfmt_attr_s *src_attr = pixfmt_get_attr(frame0->fmt);
    const pixfmt_attr_s *dst_attr = pixfmt_get_attr(frame1->fmt);
    assert(src_attr && dst_attr);

    /* if same format, just copy */
    if (frame0->fmt == frame1->fmt) {
        if (frame0->pitch == frame1->pitch) {
            assert(frame0->size == frame1->size);
            memcpy(frame1->addr, frame0->addr, frame0->size);
        }
        else {
            int copy_row_size = MIN(frame0->pitch, frame1->pitch);
            for (int i = 0; i < frame0->hgt; i++) {
                memcpy((uchar *)frame1->addr + i * frame1->pitch, (uchar *)frame0->addr + i * frame0->pitch, copy_row_size);
            }
        }
        return 0;
    }

    /* TODO: implement format conversion for different RGB formats */
    /* For now, return error for unsupported conversions */
    LOGE("pixfmt_cvt_impl_r2r: conversion from %s to %s not implemented yet!\n", pixfmt_short_name(frame0->fmt),
        pixfmt_short_name(frame1->fmt));
    return -1;
}

static int pixfmt_cvt_impl_y2y(const pixfmt_frame_s *frame0, pixfmt_frame_s *frame1)
{
    // todo
    return -1;
}

static int pixfmt_cvt_range_r2r(const pixfmt_frame_s *frame0, pixfmt_frame_s *frame1)
{
    // todo
    return -1;
}

static int pixfmt_cvt_range_y2y(const pixfmt_frame_s *frame0, pixfmt_frame_s *frame1)
{
    // todo
    return -1;
}

bool pixfmt_cvt_is_supported(pixfmt_e src_fmt, pixfmt_e dst_fmt, pixfmt_e *retSrcBaseFmt, pixfmt_e *retDstBaseFmt)
{
    pixfmt_e src_base = src_fmt;
    pixfmt_e dst_base = dst_fmt;

    do {
        if (src_fmt == dst_fmt)
            break;

        const pixfmt_attr_s *src_attr = pixfmt_get_attr(src_fmt);
        const pixfmt_attr_s *dst_attr = pixfmt_get_attr(dst_fmt);
        assert(src_attr && dst_attr);

        const bool need_alpha = pixfmt_has_alpha(dst_fmt);
        src_base = pixfmt_get_common_fmt(src_fmt, src_attr->layout, need_alpha);
        dst_base = pixfmt_get_common_fmt(src_fmt, src_attr->layout, need_alpha);
        if (src_base != PIXFMT_INVALID && dst_base != PIXFMT_INVALID)
            break;

        src_base = pixfmt_get_common_fmt(src_fmt, dst_attr->layout, need_alpha);
        dst_base = pixfmt_get_common_fmt(src_fmt, dst_attr->layout, need_alpha);
    } while (0);

    if (src_base != PIXFMT_INVALID && dst_base != PIXFMT_INVALID) {
        if (retSrcBaseFmt)
            *retSrcBaseFmt = src_base;
        if (retDstBaseFmt)
            *retDstBaseFmt = dst_base;
        return true;
    }

    return false;
}

bool pixfmt_cvt_check(const pixfmt_frame_s *frame0, const pixfmt_frame_s *frame1)
{
    // check if same resolution
    if (frame0->wid != frame1->wid || frame0->hgt != frame1->hgt)
        return false;

    /* check if same color space */
    if (!pixfmt_colorspcae_check_same(frame0->clrspc, frame1->clrspc))
        return false;

    /* check if memory valid */
    if (!frame0->addr || !frame1->addr)
        return false;
    if (frame0->fd > 0 && frame1->fd > 0 && frame0->fd == frame1->fd)
        return false;

    return true;
}

int pixfmt_cvt_exec(const pixfmt_frame_s *frame0, pixfmt_frame_s *frame1)
{
    assert(frame0 && frame1);

    bool ok = pixfmt_cvt_check(frame0, frame1);
    if (!ok)
        return -1;

    pixfmt_frame_s src_base_frame = {0};
    pixfmt_frame_s dst_base_frame = {0};
    pixfmt_e src_base_fmt = PIXFMT_INVALID;
    pixfmt_e dst_base_fmt = PIXFMT_INVALID;
    bool src_base_frame_reuse = true;
    bool dst_base_frame_reuse = true;
    int ret = 0;

    do {
        ok = pixfmt_cvt_is_supported(frame0->fmt, frame1->fmt, &src_base_fmt, &dst_base_fmt);
        if (!ok) {
            ret = -1;
            break;
        }
        /* do conversion directly from frame0 to frame1 */
        if (frame0->fmt == frame1->fmt) {
            if (frame0->clrspc == frame1->clrspc) {
                if (frame0->pitch == frame1->pitch) {
                    assert(frame0->size == frame1->size);
                    memcpy(frame1->addr, frame0->addr, frame0->size);
                }
                else {
                    int copy_row_size = MIN(frame0->pitch, frame1->pitch);
                    for (int i = 0; i < frame0->hgt; i++) {
                        memcpy((uchar *)frame1->addr + i * frame1->pitch, (uchar *)frame0->addr + i * frame0->pitch,
                            copy_row_size);
                    }
                }
            }
            else {
                assert(pixfmt_colorspcae_check_same(frame0->clrspc, frame1->clrspc) == true);
                if (pixfmt_is_rgb(frame0->fmt)) {
                    ret = pixfmt_cvt_range_r2r(frame0, frame1);
                    break;
                }
                else if (pixfmt_is_yuv(frame0->fmt)) {
                    ret = pixfmt_cvt_range_y2y(frame0, frame1);
                    break;
                }
                else {
                    ret = -1;
                    break;
                }
            }
        }

        /* do conversion from frame0 to src_base_frame, malloc memory if need */
        if (src_base_fmt == frame0->fmt)
            memcpy(&src_base_frame, frame0, sizeof(src_base_frame));
        else {
            // malloc memory for src_base_frame
            src_base_frame.fmt = src_base_fmt;
            src_base_frame.clrspc = frame0->clrspc;
            src_base_frame.wid = frame0->wid;
            src_base_frame.hgt = frame0->hgt;
            pixfmt_frame_fill(&src_base_frame);
            src_base_frame.addr = malloc(src_base_frame.size);
            src_base_frame_reuse = false;

            // src to src_base
            if (pixfmt_is_rgb(frame0->fmt))
                ret = pixfmt_cvt_impl_r2r(frame0, &src_base_frame);
            else if (pixfmt_is_yuv(frame0->fmt))
                ret = pixfmt_cvt_impl_y2y(frame0, &src_base_frame);
            else {
                ret = -1;
                break;
            }
        }

        /* malloc memory for dst_base_frame if need */
        if (dst_base_fmt == frame1->fmt)
            memcpy(&dst_base_frame, frame1, sizeof(dst_base_frame));
        else {
            dst_base_frame.fmt = dst_base_fmt;
            dst_base_frame.clrspc = frame1->clrspc;
            dst_base_frame.wid = frame1->wid;
            dst_base_frame.hgt = frame1->hgt;
            pixfmt_frame_fill(&dst_base_frame);
            dst_base_frame.addr = malloc(dst_base_frame.size);
            dst_base_frame_reuse = false;
        }

        /* do conversion from src_base_frame to dst_base_frame */
        if (src_base_fmt == dst_base_fmt) {
            memcpy(dst_base_frame.addr, src_base_frame.addr, src_base_frame.size);
        }
        else {
            if (pixfmt_is_rgb(src_base_fmt))
                ret = pixfmt_cvt_impl_r2r(&src_base_frame, &dst_base_frame);
            else if (pixfmt_is_yuv(src_base_fmt))
                ret = pixfmt_cvt_impl_y2y(&src_base_frame, &dst_base_frame);
            else {
                ret = -1;
                break;
            }
        }

        /* do conversion from dst_base_frame to frame1 */
        if (dst_base_fmt != frame1->fmt) {
            if (pixfmt_is_rgb(dst_base_fmt))
                ret = pixfmt_cvt_impl_r2r(&dst_base_frame, frame1);
            else if (pixfmt_is_yuv(dst_base_fmt))
                ret = pixfmt_cvt_impl_y2y(&dst_base_frame, frame1);
            else {
                ret = -1;
                break;
            }
        }
    } while (0);

    /* release the base frames */
    if (!src_base_frame_reuse && src_base_frame.addr)
        free(src_base_frame.addr);
    if (!dst_base_frame_reuse && dst_base_frame.addr)
        free(dst_base_frame.addr);

    return ret;
}

#if 0
int pixfmt_cvt_rgb888_to_rgb565(const void *src, void *dst, int w, int h, int src_stride, int dst_stride)
{
    for (int y = 0; y < h; y++) {
        const uint8_t *src_row = src + y * src_stride;
        uint16_t *dst_row = (uint16_t *)(dst + y * dst_stride);

        for (int x = 0; x < w; x++) {
            const uint8_t *pixel = src_row + x * 3;
            uint8_t r = pixel[0];
            uint8_t g = pixel[1];
            uint8_t b = pixel[2];

            uint16_t rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3);
            dst_row[x] = rgb565;
        }
    }

    return 0;
}

int pixfmt_cvt_rgb565_to_rgb888(const void *src, void *dst, int w, int h, int src_stride, int dst_stride)
{
    for (int y = 0; y < h; y++) {
        const uint16_t *src_row = (const uint16_t *)(src + y * src_stride);
        uint8_t *dst_row = dst + y * dst_stride;

        for (int x = 0; x < w; x++) {
            uint16_t rgb565 = src_row[x];
            uint8_t r = (rgb565 >> 11) & 0x1F;
            uint8_t g = (rgb565 >> 5) & 0x3F;
            uint8_t b = (rgb565 << 3) & 0xF8;

            dst_row[x * 3 + 0] = r;
            dst_row[x * 3 + 1] = g;
            dst_row[x * 3 + 2] = b;
        }
    }

    return 0;
}

int pixfmt_cvt_rgb888_to_rgb332(const void *src, void *dst, int w, int h, int src_stride, int dst_stride)
{
    for (int y = 0; y < h; y++) {
        const uint8_t *src_row = src + y * src_stride;
        uint8_t *dst_row = dst + y * dst_stride;

        for (int x = 0; x < w; x++) {
            const uint8_t *pixel = src_row + x * 3;
            uint8_t r = pixel[0] >> 5;
            uint8_t g = (pixel[1] >> 5) & 0x07;
            uint8_t b = (pixel[2] >> 6) & 0x03;

            dst_row[x] = (r << 5) | (g << 2) | b;
        }
    }

    return 0;
}

int pixfmt_cvt_rgb332_to_rgb888(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride)
{
    for (int y = 0; y < h; y++) {
        const uint8_t *src_row = src + y * src_stride;
        uint8_t *dst_row = dst + y * dst_stride;

        for (int x = 0; x < w; x++) {
            uint8_t rgb332 = src_row[x];
            uint8_t r = (rgb332 >> 5) & 0x07;
            uint8_t g = (rgb332 >> 2) & 0x07;
            uint8_t b = rgb332 & 0x03;

            dst_row[x * 3 + 0] = (r << 5) | r;
            dst_row[x * 3 + 1] = (g << 5) | g;
            dst_row[x * 3 + 2] = (b << 6) | b;
        }
    }

    return 0;
}

int pixfmt_cvt_yuv420sp_to_yuv420p(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride)
{
    int uv_w = (w + 1) / 2;
    int uv_h = (h + 1) / 2;

    size_t y_size = w * h;
    size_t uv_size = uv_w * uv_h;

    const uint8_t *y_plane = src;
    const uint8_t *uv_plane = src + y_size;

    uint8_t *dst_y = dst;
    uint8_t *dst_u = dst + y_size;
    uint8_t *dst_v = dst + y_size + uv_size;

    memcpy(dst_y, y_plane, y_size);
    memcpy(dst_u, uv_plane, uv_size);
    memcpy(dst_v, uv_plane + uv_size, uv_size);

    return 0;
}

int pixfmt_cvt_yuv420p_to_yuv420sp(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride)
{
    int uv_w = (w + 1) / 2;
    int uv_h = (h + 1) / 2;

    size_t y_size = w * h;
    size_t uv_size = uv_w * uv_h;

    const uint8_t *y_plane = src;
    const uint8_t *u_plane = src + y_size;
    const uint8_t *v_plane = src + y_size + uv_size;

    uint8_t *dst_y = dst;
    uint8_t *dst_uv = dst + y_size;

    memcpy(dst_y, y_plane, y_size);
    memcpy(dst_uv, u_plane, uv_size);
    memcpy(dst_uv + uv_size, v_plane, uv_size);

    return 0;
}

int pixfmt_cvt_rgb888_to_yuv420p(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride)
{
    int uv_w = (w + 1) / 2;
    int uv_h = (h + 1) / 2;

    size_t y_size = w * h;
    size_t uv_size = uv_w * uv_h;

    uint8_t *dst_y = dst;
    uint8_t *dst_u = dst + y_size;
    uint8_t *dst_v = dst + y_size + uv_size;

    for (int y = 0; y < h; y++) {
        const uint8_t *src_row = src + y * src_stride;
        uint8_t *dst_y_row = dst_y + y * w;
        uint8_t *dst_u_row = dst_u + (y / 2) * uv_w;
        uint8_t *dst_v_row = dst_v + (y / 2) * uv_w;

        for (int x = 0; x < w; x++) {
            uint8_t r = src_row[x * 3 + 0];
            uint8_t g = src_row[x * 3 + 1];
            uint8_t b = src_row[x * 3 + 2];

            uint8_t y = (uint8_t)((66 * r + 129 * g + 25 * b + 16) >> 8);
            uint8_t u = (uint8_t)((-38 * r - 74 * g + 112 * b + 128) >> 8);
            uint8_t v = (uint8_t)((112 * r - 94 * g - 18 * b + 128) >> 8);

            dst_y_row[x] = y;
            if (x % 2 == 0 && y % 2 == 0) {
                dst_u_row[x / 2] = u;
                dst_v_row[x / 2] = v;
            }
        }
    }

    return 0;
}

int pixfmt_cvt_yuv420p_to_rgb888(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride)
{
    int uv_w = (w + 1) / 2;
    int uv_h = (h + 1) / 2;

    size_t y_size = w * h;
    size_t uv_size = uv_w * uv_h;

    const uint8_t *y_plane = src;
    const uint8_t *u_plane = src + y_size;
    const uint8_t *v_plane = src + y_size + uv_size;

    for (int y = 0; y < h; y++) {
        const uint8_t *src_y_row = y_plane + y * w;
        const uint8_t *src_u_row = u_plane + (y / 2) * uv_w;
        const uint8_t *src_v_row = v_plane + (y / 2) * uv_w;
        uint8_t *dst_row = dst + y * dst_stride;

        for (int x = 0; x < w; x++) {
            uint8_t y = src_y_row[x];
            uint8_t u = (x % 2 == 0) ? src_u_row[x / 2] : src_u_row[(x + 1) / 2];
            uint8_t v = (x % 2 == 0) ? src_v_row[x / 2] : src_v_row[(x + 1) / 2];

            int16_t c = y - 16;
            int16_t d = 5 * u - 128;
            int16_t e = 409 * v - 128;
            int16_t r = (298 * c + 409 * e + 128) >> 8;
            int16_t g = (100 * c - 208 * e - 519 * d) >> 8;
            int16_t b = (516 * c + 100 * e + 127 * d) >> 8;

            dst_row[x * 3 + 0] = (uint8_t)r;
            dst_row[x * 3 + 1] = (uint8_t)g;
            dst_row[x * 3 + 2] = (uint8_t)b;
        }
    }

    return 0;
}
#endif