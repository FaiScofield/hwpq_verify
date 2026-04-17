/**
 * @copyright: Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @brief:     Image format conversion module implementation
 * @author:
 * @create:    2026-04-16
 */

#include "pqfmt_cvt.h"
#include "pqfmt.h"
#include "verify_com.h"
#include <string.h>
#include <math.h>

static int pqvf_cvt_exec_same_canonical(const pqvf_cvt_ctx_t *ctx, const uint8_t *src, uint8_t *dst);
static int pqvf_cvt_exec_different_canonical(const pqvf_cvt_ctx_t *ctx, pqvf_imgfmt_e src_canonical, pqvf_imgfmt_e dst_canonical, const uint8_t *src, uint8_t *dst);

int pqvf_cvt_init(pqvf_cvt_ctx_t *ctx, pqvf_imgfmt_e src_fmt, pqvf_imgfmt_e dst_fmt, int w, int h) {
    if (!ctx) return -1;

    ctx->src_fmt = src_fmt;
    ctx->dst_fmt = dst_fmt;
    ctx->src_w = w;
    ctx->src_h = h;
    ctx->dst_w = w;
    ctx->dst_h = h;
    ctx->src_stride = pqvf_fmt_vir_wid(src_fmt, w, 0);
    ctx->dst_stride = pqvf_fmt_vir_wid(dst_fmt, w, 0);

    return 0;
}

bool pqvf_cvt_is_supported(pqvf_imgfmt_e src_fmt, pqvf_imgfmt_e dst_fmt) {
    if (src_fmt == dst_fmt) return true;

    if (!pqvf_fmt_can_input(src_fmt)) return false;
    if (!pqvf_fmt_can_output(dst_fmt)) return false;

    pqvf_imgfmt_e src_canonical = pqvf_fmt_get_canonical(src_fmt);
    pqvf_imgfmt_e dst_canonical = pqvf_fmt_get_canonical(dst_fmt);

    return src_canonical != PQVF_FMT_INVALID && dst_canonical != PQVF_FMT_INVALID;
}

pqvf_imgfmt_e pqvf_cvt_get_intermediate_fmt(pqvf_imgfmt_e src_fmt, pqvf_imgfmt_e dst_fmt) {
    if (src_fmt == dst_fmt) return src_fmt;

    pqvf_imgfmt_e src_canonical = pqvf_fmt_get_canonical(src_fmt);
    pqvf_imgfmt_e dst_canonical = pqvf_fmt_get_canonical(dst_fmt);

    if (src_canonical != PQVF_FMT_INVALID && dst_canonical != PQVF_FMT_INVALID) {
        if (src_canonical == dst_canonical) {
            return src_canonical;
        }
        if (pqvf_fmt_is_yuv(src_fmt) && pqvf_fmt_is_yuv(dst_fmt)) {
            return PQVF_FMT_YUV420P_YU12;
        }
        if (pqvf_fmt_is_rgb(src_fmt) && pqvf_fmt_is_rgb(dst_fmt)) {
            return PQVF_FMT_RGB888;
        }
    }

    return PQVF_FMT_INVALID;
}

int pqvf_cvt_exec(const pqvf_cvt_ctx_t *ctx, const uint8_t *src, uint8_t *dst) {
    if (!ctx || !src || !dst) return -1;

    if (ctx->src_fmt == ctx->dst_fmt) {
        memcpy(dst, src, pqvf_fmt_framesize(ctx->dst_fmt, ctx->dst_w, ctx->dst_h, ctx->dst_stride, 0));
        return 0;
    }

    pqvf_imgfmt_e src_canonical = pqvf_fmt_get_canonical(ctx->src_fmt);
    pqvf_imgfmt_e dst_canonical = pqvf_fmt_get_canonical(ctx->dst_fmt);

    if (src_canonical == PQVF_FMT_INVALID || dst_canonical == PQVF_FMT_INVALID) {
        return -1;
    }

    if (src_canonical == dst_canonical) {
        return pqvf_cvt_exec_same_canonical(ctx, src, dst);
    }

    return pqvf_cvt_exec_different_canonical(ctx, src_canonical, dst_canonical, src, dst);
}

static int pqvf_cvt_exec_same_canonical(const pqvf_cvt_ctx_t *ctx, const uint8_t *src, uint8_t *dst) {
    pqvf_imgfmt_e inter_fmt = pqvf_cvt_get_intermediate_fmt(ctx->src_fmt, ctx->dst_fmt);
    if (inter_fmt == PQVF_FMT_INVALID) return -1;

    size_t src_size = pqvf_fmt_framesize(ctx->src_fmt, ctx->src_w, ctx->src_h, ctx->src_stride, 0);
    size_t dst_size = pqvf_fmt_framesize(ctx->dst_fmt, ctx->dst_w, ctx->dst_h, ctx->dst_stride, 0);

    if (ctx->src_fmt == ctx->dst_fmt) {
        memcpy(dst, src, src_size);
        return 0;
    }

    return -1;
}

static int pqvf_cvt_exec_different_canonical(const pqvf_cvt_ctx_t *ctx, pqvf_imgfmt_e src_canonical, pqvf_imgfmt_e dst_canonical, const uint8_t *src, uint8_t *dst) {
    size_t inter_size = pqvf_fmt_framesize(src_canonical, ctx->src_w, ctx->src_h, ctx->src_stride, 0);
    size_t dst_size = pqvf_fmt_framesize(ctx->dst_fmt, ctx->dst_w, ctx->dst_h, ctx->dst_stride, 0);

    return -1;
}

int pqvf_cvt_rgb888_to_rgb565(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride) {
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

int pqvf_cvt_rgb565_to_rgb888(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride) {
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

int pqvf_cvt_rgb888_to_rgb332(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride) {
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

int pqvf_cvt_rgb332_to_rgb888(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride) {
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

int pqvf_cvt_yuv420sp_to_yuv420p(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride) {
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

int pqvf_cvt_yuv420p_to_yuv420sp(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride) {
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

int pqvf_cvt_rgb888_to_yuv420p(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride) {
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

int pqvf_cvt_yuv420p_to_rgb888(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride) {
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
