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

static void pixfmt_cvt_rgb_calc_param(const pixfmt_attr_s *attr, int comp_seq[4], int *seq_len_out,
                                      int comp_offset[4], int comp_shift[4], int comp_mask[4], int *pixel_bytes)
{
    const pixfmt_rgb_desc_s *desc = attr->desc.rgb;
    bool has_alpha = (desc->comp_bits[3] > 0);
    int slen;

    int rgb_seq[3];
    if (desc->order == PIXFMT_RGB_ORDER_RGB) {
        rgb_seq[0] = 0; rgb_seq[1] = 1; rgb_seq[2] = 2;
    } else {
        rgb_seq[0] = 2; rgb_seq[1] = 1; rgb_seq[2] = 0;
    }

    if (has_alpha) {
        slen = 4;
        if (desc->alpha_pos == PIXFMT_ALPHA_AT_LSB) {
            comp_seq[0] = 3; comp_seq[1] = rgb_seq[0]; comp_seq[2] = rgb_seq[1]; comp_seq[3] = rgb_seq[2];
        } else {
            comp_seq[0] = rgb_seq[0]; comp_seq[1] = rgb_seq[1]; comp_seq[2] = rgb_seq[2]; comp_seq[3] = 3;
        }
    } else {
        slen = 3;
        comp_seq[0] = rgb_seq[0]; comp_seq[1] = rgb_seq[1]; comp_seq[2] = rgb_seq[2];
    }

    if (attr->is_bitpacked) {
        int bit_pos = 0;
        for (int i = 0; i < slen; i++) {
            int ci = comp_seq[i];
            comp_shift[ci] = bit_pos;
            comp_mask[ci] = (1 << desc->comp_bits[ci]) - 1;
            comp_offset[ci] = 0;
            bit_pos += desc->comp_bits[ci];
        }
        *pixel_bytes = ALIGN_N_DIV(bit_pos, 8) / 8;
    } else {
        int byte_pos = 0;
        for (int i = 0; i < slen; i++) {
            int ci = comp_seq[i];
            int stride = ALIGN_N_DIV(desc->comp_bits[ci], 8) / 8;
            comp_offset[ci] = byte_pos;
            comp_shift[ci] = 0;
            comp_mask[ci] = (1 << desc->comp_bits[ci]) - 1;
            byte_pos += stride;
        }
        *pixel_bytes = byte_pos;
    }

    *seq_len_out = slen;
}

static uint32_t pixfmt_cvt_rgb_read_comp(const uint8_t *pixel, int byte_offset, int bit_shift, int mask, bool is_bitpacked)
{
    if (mask == 0) return 0;
    if (is_bitpacked) {
        uint64_t val = 0;
        memcpy(&val, pixel, sizeof(val));
        return (uint32_t)((val >> bit_shift) & mask);
    } else {
        const uint8_t *ptr = pixel + byte_offset;
        if (mask <= 0xFF) {
            return *ptr & mask;
        } else {
            uint16_t val = 0;
            memcpy(&val, ptr, sizeof(val));
            return val & mask;
        }
    }
}

static void pixfmt_cvt_rgb_write_comp(uint8_t *pixel, int byte_offset, int bit_shift, int mask,
                                      uint32_t value, bool is_bitpacked)
{
    if (mask == 0) return;
    if (is_bitpacked) {
        uint64_t val = 0;
        memcpy(&val, pixel, sizeof(val));
        val &= ~((uint64_t)mask << bit_shift);
        val |= ((uint64_t)(value & mask) << bit_shift);
        memcpy(pixel, &val, sizeof(val));
    } else {
        uint8_t *ptr = pixel + byte_offset;
        if (mask <= 0xFF) {
            *ptr = (uint8_t)(value & mask);
        } else {
            uint16_t val = 0;
            memcpy(&val, ptr, sizeof(val));
            val = (val & ~mask) | (value & mask);
            memcpy(ptr, &val, sizeof(val));
        }
    }
}

static uint32_t pixfmt_cvt_scale_comp(uint32_t val, int src_bits, int dst_bits)
{
    if (src_bits == dst_bits || src_bits == 0 || dst_bits == 0)
        return val;
    if (dst_bits > src_bits) {
        int shift = dst_bits - src_bits;
        return (val << shift) | (val >> (src_bits - shift > 0 ? src_bits - shift : 0));
    } else {
        int src_max = (1 << src_bits) - 1;
        int dst_max = (1 << dst_bits) - 1;
        return (val * dst_max + src_max / 2) / src_max;
    }
}

static int pixfmt_cvt_impl_r2r(const pixfmt_frame_s *frame0, pixfmt_frame_s *frame1)
{
    assert(frame0 && frame1);
    assert(pixfmt_is_rgb(frame0->fmt));
    assert(pixfmt_is_rgb(frame1->fmt));

    const pixfmt_attr_s *src_attr = pixfmt_get_attr(frame0->fmt);
    const pixfmt_attr_s *dst_attr = pixfmt_get_attr(frame1->fmt);
    const pixfmt_rgb_desc_s *src_desc = src_attr->desc.rgb;
    const pixfmt_rgb_desc_s *dst_desc = dst_attr->desc.rgb;
    assert(src_attr && dst_attr);

    /* if same format, just copy */
    if (frame0->fmt == frame1->fmt) {
        int copy_row_size = MIN(frame0->pitch, frame1->pitch);
        for (int i = 0; i < frame0->hgt; i++) {
            memcpy((uint8_t *)frame1->addr + i * frame1->pitch,
                   (uint8_t *)frame0->addr + i * frame0->pitch, copy_row_size);
        }
        return 0;
    }

    /* do R2R */
    int src_seq[4], src_offset[4], src_shift[4], src_mask[4], src_pbytes;
    int dst_seq[4], dst_offset[4], dst_shift[4], dst_mask[4], dst_pbytes;
    int src_slen, dst_slen;

    pixfmt_cvt_rgb_calc_param(src_attr, src_seq, &src_slen, src_offset, src_shift, src_mask, &src_pbytes);
    pixfmt_cvt_rgb_calc_param(dst_attr, dst_seq, &dst_slen, dst_offset, dst_shift, dst_mask, &dst_pbytes);

    for (int i = 0; i < frame0->hgt; i++) {
        const uint8_t *psrc = (uint8_t *)frame0->addr + i * frame0->pitch;
        uint8_t *pdst = (uint8_t *)frame1->addr + i * frame1->pitch;

        for (int j = 0; j < frame0->wid; j++) {
            uint32_t r = pixfmt_cvt_rgb_read_comp(psrc, src_offset[0], src_shift[0], src_mask[0], src_attr->is_bitpacked);
            uint32_t g = pixfmt_cvt_rgb_read_comp(psrc, src_offset[1], src_shift[1], src_mask[1], src_attr->is_bitpacked);
            uint32_t b = pixfmt_cvt_rgb_read_comp(psrc, src_offset[2], src_shift[2], src_mask[2], src_attr->is_bitpacked);
            uint32_t a = pixfmt_cvt_rgb_read_comp(psrc, src_offset[3], src_shift[3], src_mask[3], src_attr->is_bitpacked);

            r = pixfmt_cvt_scale_comp(r, src_desc->comp_bits[0], dst_desc->comp_bits[0]);
            g = pixfmt_cvt_scale_comp(g, src_desc->comp_bits[1], dst_desc->comp_bits[1]);
            b = pixfmt_cvt_scale_comp(b, src_desc->comp_bits[2], dst_desc->comp_bits[2]);
            a = pixfmt_cvt_scale_comp(a, src_desc->comp_bits[3], dst_desc->comp_bits[3]);

            pixfmt_cvt_rgb_write_comp(pdst, dst_offset[0], dst_shift[0], dst_mask[0], r, dst_attr->is_bitpacked);
            pixfmt_cvt_rgb_write_comp(pdst, dst_offset[1], dst_shift[1], dst_mask[1], g, dst_attr->is_bitpacked);
            pixfmt_cvt_rgb_write_comp(pdst, dst_offset[2], dst_shift[2], dst_mask[2], b, dst_attr->is_bitpacked);
            pixfmt_cvt_rgb_write_comp(pdst, dst_offset[3], dst_shift[3], dst_mask[3], a, dst_attr->is_bitpacked);

            psrc += src_pbytes;
            pdst += dst_pbytes;
        }
    }

    return 0;
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
        dst_base = pixfmt_get_common_fmt(dst_fmt, src_attr->layout, need_alpha);
        if (src_base != PIXFMT_INVALID && dst_base != PIXFMT_INVALID)
            break;

        src_base = pixfmt_get_common_fmt(src_fmt, dst_attr->layout, need_alpha);
        dst_base = pixfmt_get_common_fmt(dst_fmt, dst_attr->layout, need_alpha);
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

        /* do conversion from src_base_frame to dst_base_frame via CSC */
        if (src_base_fmt == dst_base_fmt) {
            memcpy(dst_base_frame.addr, src_base_frame.addr, src_base_frame.size);
        }
        else {
            ret = pixfmt_csc_exec(&src_base_frame, &dst_base_frame);
            if (ret != 0)
                break;
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