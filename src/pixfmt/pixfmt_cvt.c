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

#ifndef fourcc_code
#define fourcc_code(a, b, c, d) ((uint32_t)(a) | ((uint32_t)(b) << 8) | ((uint32_t)(c) << 16) | ((uint32_t)(d) << 24))

#define DRM_FORMAT_RGB888       fourcc_code('R', 'G', '2', '4') /* [23:0] R:G:B little endian */
#define DRM_FORMAT_BGR888       fourcc_code('B', 'G', '2', '4') /* [23:0] B:G:R little endian */
#define DRM_FORMAT_ARGB8888     fourcc_code('A', 'R', '2', '4') /* [31:0] A:R:G:B 8:8:8:8 little endian */
#define DRM_FORMAT_ABGR8888     fourcc_code('A', 'B', '2', '4') /* [31:0] A:B:G:R 8:8:8:8 little endian */
#define DRM_FORMAT_RGBA8888     fourcc_code('R', 'A', '2', '4') /* [31:0] R:G:B:A 8:8:8:8 little endian */
#define DRM_FORMAT_BGRA8888     fourcc_code('B', 'A', '2', '4') /* [31:0] B:G:R:A 8:8:8:8 little endian */
#define DRM_FORMAT_RGB332       fourcc_code('R', 'G', 'B', '8') /* [7:0] R:G:B 3:3:2 */
#define DRM_FORMAT_BGR233       fourcc_code('B', 'G', 'R', '8') /* [7:0] B:G:R 2:3:3 */
#define DRM_FORMAT_RGB565       fourcc_code('R', 'G', '1', '6') /* [15:0] R:G:B 5:6:5 little endian */
#define DRM_FORMAT_BGR565       fourcc_code('B', 'G', '1', '6') /* [15:0] B:G:R 5:6:5 little endian */
#define DRM_FORMAT_ABGR1555     fourcc_code('A', 'B', '1', '5') /* [15:0] A:B:G:R 1:5:5:5 little endian */
#define DRM_FORMAT_RGBA5551     fourcc_code('R', 'A', '1', '5') /* [15:0] R:G:B:A 5:5:5:1 little endian */
#define DRM_FORMAT_ABGR4444     fourcc_code('A', 'B', '1', '2') /* [15:0] A:B:G:R 4:4:4:4 little endian */
#define DRM_FORMAT_RGBA4444     fourcc_code('R', 'A', '1', '2') /* [15:0] R:G:B:A 4:4:4:4 little endian */
#define DRM_FORMAT_ABGR2101010  fourcc_code('A', 'B', '3', '0') /* [31:0] A:B:G:R 2:10:10:10 little endian */
#define DRM_FORMAT_RGBA1010102  fourcc_code('R', 'A', '3', '0') /* [31:0] R:G:B:A 10:10:10:2 little endian */

#define DRM_FORMAT_VUY888       fourcc_code('V', 'U', '2', '4') /* [23:0] Cr:Cb:Y 8:8:8 little endian */
#define DRM_FORMAT_VUY101010    fourcc_code('V', 'U', '3', '0') /* Y followed by U then V, 10:10:10 */
#define DRM_FORMAT_XVYU2101010  fourcc_code('X', 'V', '3', '0') /* [31:0] X:Cr:Y:Cb 2:10:10:10 little endian */
#define DRM_FORMAT_YUV410       fourcc_code('Y', 'U', 'V', '9') /* 4x4 subsampled Cb (1) and Cr (2) planes */
#define DRM_FORMAT_YVU410       fourcc_code('Y', 'V', 'U', '9') /* 4x4 subsampled Cr (1) and Cb (2) planes */
#define DRM_FORMAT_YUV411       fourcc_code('Y', 'U', '1', '1') /* 4x1 subsampled Cb (1) and Cr (2) planes */
#define DRM_FORMAT_YVU411       fourcc_code('Y', 'V', '1', '1') /* 4x1 subsampled Cr (1) and Cb (2) planes */
#define DRM_FORMAT_YUV420       fourcc_code('Y', 'U', '1', '2') /* 2x2 subsampled Cb (1) and Cr (2) planes */
#define DRM_FORMAT_YVU420       fourcc_code('Y', 'V', '1', '2') /* 2x2 subsampled Cr (1) and Cb (2) planes */
#define DRM_FORMAT_YUV422       fourcc_code('Y', 'U', '1', '6') /* 2x1 subsampled Cb (1) and Cr (2) planes */
#define DRM_FORMAT_YVU422       fourcc_code('Y', 'V', '1', '6') /* 2x1 subsampled Cr (1) and Cb (2) planes */
#define DRM_FORMAT_YUV444       fourcc_code('Y', 'U', '2', '4') /* non-subsampled Cb (1) and Cr (2) planes */
#define DRM_FORMAT_YVU444       fourcc_code('Y', 'V', '2', '4') /* non-subsampled Cr (1) and Cb (2) planes */
#define DRM_FORMAT_NV12         fourcc_code('N', 'V', '1', '2') /* 2x2 subsampled Cr:Cb plane */
#define DRM_FORMAT_NV21         fourcc_code('N', 'V', '2', '1') /* 2x2 subsampled Cb:Cr plane */
#define DRM_FORMAT_NV16         fourcc_code('N', 'V', '1', '6') /* 2x1 subsampled Cr:Cb plane */
#define DRM_FORMAT_NV61         fourcc_code('N', 'V', '6', '1') /* 2x1 subsampled Cb:Cr plane */
#define DRM_FORMAT_NV24         fourcc_code('N', 'V', '2', '4') /* non-subsampled Cr:Cb plane */
#define DRM_FORMAT_NV42         fourcc_code('N', 'V', '4', '2') /* non-subsampled Cb:Cr plane */
#define DRM_FORMAT_YUYV         fourcc_code('Y', 'U', 'Y', 'V') /* [31:0] V0:Y1:U0:Y0 8:8:8:8 little endian */
#define DRM_FORMAT_YVYU         fourcc_code('Y', 'V', 'Y', 'U') /* [31:0] U0:Y1:V0:Y0 8:8:8:8 little endian */
#define DRM_FORMAT_UYVY         fourcc_code('U', 'Y', 'V', 'Y') /* [31:0] Y1:V0:Y0:U0 8:8:8:8 little endian */
#define DRM_FORMAT_VYUY         fourcc_code('V', 'Y', 'U', 'Y') /* [31:0] Y1:U0:Y0:V0 8:8:8:8 little endian */
#define DRM_FORMAT_Y210         fourcc_code('Y', '2', '1', '0') /* [63:0] V:X 10:6 little endian per 2 Y pixels */
#define DRM_FORMAT_Y212         fourcc_code('Y', '2', '1', '2') /* [63:0] V:X 12:4 little endian per 2 Y pixels */
#define DRM_FORMAT_Y216         fourcc_code('Y', '2', '1', '6') /* [63:0] V0:Y1:U0:Y0 16:16:16:16 */
#define DRM_FORMAT_NV15         fourcc_code('N', 'V', '1', '5') /* 2x2 subsampled Cr:Cb plane */
#define DRM_FORMAT_NV20         fourcc_code('N', 'V', '2', '0') /* 2x1 subsampled Cr:Cb plane */
#define DRM_FORMAT_NV30         fourcc_code('N', 'V', '3', '0') /* non-subsampled Cr:Cb plane */
#define DRM_FORMAT_R1           fourcc_code('R', '1', ' ', ' ') /* [7:0] 1:1:1:1:1:1:1:1 eight pixels/byte */
#define DRM_FORMAT_R2           fourcc_code('R', '2', ' ', ' ') /* [7:0] R0:R1:R2:R3 2:2:2:2 four pixels/byte */
#define DRM_FORMAT_R4           fourcc_code('R', '4', ' ', ' ') /* [7:0] R0:R1 4:4 two pixels/byte */
#define DRM_FORMAT_R8           fourcc_code('R', '8', ' ', ' ') /* [7:0] R */
#define DRM_FORMAT_R10          fourcc_code('R', '1', '0', ' ') /* [15:0] x:R 6:10 little endian */
#define DRM_FORMAT_R12          fourcc_code('R', '1', '2', ' ') /* [15:0] x:R 4:12 little endian */
#define DRM_FORMAT_R16          fourcc_code('R', '1', '6', ' ') /* [15:0] R little endian */
#endif

bool pixfmt_cvt_is_supported(pixfmt_e src_fmt, pixfmt_e dst_fmt)
{
    if (src_fmt == dst_fmt)
        return true;

    // if (!pixfmt_can_input(src_fmt))
    //     return false;
    // if (!pixfmt_can_output(dst_fmt))
    //     return false;

    pixfmt_e src_canonical = pixfmt_cvt_get_canonical(src_fmt);
    pixfmt_e dst_canonical = pixfmt_cvt_get_canonical(dst_fmt);

    return src_canonical != PIXFMT_INVALID && dst_canonical != PIXFMT_INVALID;
}

pixfmt_e pixfmt_cvt_get_intermediate_fmt(pixfmt_e src_fmt, pixfmt_e dst_fmt)
{
    if (src_fmt == dst_fmt)
        return src_fmt;

    pixfmt_e src_canonical = pixfmt_get_common_fmt(src_fmt);
    pixfmt_e dst_canonical = pixfmt_get_common_fmt(dst_fmt);

    if (src_canonical != PIXFMT_INVALID && dst_canonical != PIXFMT_INVALID) {
        if (src_canonical == dst_canonical) {
            return src_canonical;
        }
        if (pixfmt_is_yuv(src_fmt) && pixfmt_is_yuv(dst_fmt)) {
            return PIXFMT_YUV420P_YU12;
        }
        if (pixfmt_is_rgb(src_fmt) && pixfmt_is_rgb(dst_fmt)) {
            return PIXFMT_RGB888;
        }
    }

    return PIXFMT_INVALID;
}

int pixfmt_cvt_exec(const pixfmt_cvt_info_s *ctx, const uint8_t *src, uint8_t *dst)
{
    if (!ctx || !src || !dst)
        return -1;

    if (ctx->src_fmt == ctx->dst_fmt) {
        memcpy(dst, src, pixfmt_get_frame_size(ctx->dst_fmt, ctx->dst_w, ctx->dst_h, ctx->dst_stride));
        return 0;
    }

    pixfmt_e src_canonical = pixfmt_cvt_get_canonical(ctx->src_fmt);
    pixfmt_e dst_canonical = pixfmt_cvt_get_canonical(ctx->dst_fmt);

    if (src_canonical == PIXFMT_INVALID || dst_canonical == PIXFMT_INVALID) {
        return -1;
    }

    if (src_canonical == dst_canonical) {
        return pixfmt_cvt_exec_same_canonical(ctx, src, dst);
    }

    return pixfmt_cvt_exec_different_canonical(ctx, src_canonical, dst_canonical, src, dst);
}

static int pixfmt_cvt_exec_same_canonical(const pixfmt_cvt_info_s *ctx, const uint8_t *src, uint8_t *dst)
{
    pixfmt_e inter_fmt = pixfmt_cvt_get_intermediate_fmt(ctx->src_fmt, ctx->dst_fmt);
    if (inter_fmt == PIXFMT_INVALID)
        return -1;

    size_t src_size = pixfmt_get_frame_size(ctx->src_fmt, ctx->src_w, ctx->src_h, ctx->src_stride);
    size_t dst_size = pixfmt_get_frame_size(ctx->dst_fmt, ctx->dst_w, ctx->dst_h, ctx->dst_stride);

    if (ctx->src_fmt == ctx->dst_fmt) {
        memcpy(dst, src, src_size);
        return 0;
    }

    return -1;
}

static int pixfmt_cvt_exec_different_canonical(const pixfmt_cvt_info_s *ctx, pixfmt_e src_canonical,
    pixfmt_e dst_canonical, const uint8_t *src, uint8_t *dst)
{
    size_t inter_size = pixfmt_get_frame_size(src_canonical, ctx->src_w, ctx->src_h, ctx->src_stride);
    size_t dst_size = pixfmt_get_frame_size(ctx->dst_fmt, ctx->dst_w, ctx->dst_h, ctx->dst_stride);

    return -1;
}

int pixfmt_cvt_rgb888_to_rgb565(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride)
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

int pixfmt_cvt_rgb565_to_rgb888(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride)
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

int pixfmt_cvt_rgb888_to_rgb332(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride)
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
