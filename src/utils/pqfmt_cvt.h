/**
 * @copyright: Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @brief:     Image format conversion module
 * @author:
 * @create:    2026-04-16
 */

#ifndef _PIXFMT_CVT_H_
#define _PIXFMT_CVT_H_

#include "pqfmt.h"

#include <stdbool.h>
#include <stdint.h>

/**
 * Format conversion context
 */
typedef struct pixfmt_cvt_ctx {
    pixfmt_e src_fmt;
    pixfmt_e dst_fmt;
    int src_w;
    int src_h;
    int dst_w;
    int dst_h;
    int src_stride;
    int dst_stride;
} pixfmt_cvt_ctx_s;


#ifdef __cplusplus
extern "C" {
#endif

/**
 * Format conversion initialization
 */
extern int pixfmt_cvt_init(pixfmt_cvt_ctx_s *ctx, pixfmt_e src_fmt, pixfmt_e dst_fmt, int w, int h);

/**
 * Format conversion execution
 */
extern int pixfmt_cvt_exec(const pixfmt_cvt_ctx_s *ctx, const uint8_t *src, uint8_t *dst);

/**
 * Check if format conversion is supported
 */
extern bool pixfmt_cvt_is_supported(pixfmt_e src_fmt, pixfmt_e dst_fmt);

/**
 * Get intermediate format required for conversion
 */
extern pixfmt_e pixfmt_cvt_get_intermediate_fmt(pixfmt_e src_fmt, pixfmt_e dst_fmt);


/**
 * RGB conversion functions
 */
extern int pixfmt_cvt_rgb888_to_rgb565(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride);
extern int pixfmt_cvt_rgb565_to_rgb888(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride);
extern int pixfmt_cvt_rgb888_to_rgb332(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride);
extern int pixfmt_cvt_rgb332_to_rgb888(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride);

/**
 * YUV conversion functions
 */
extern int pixfmt_cvt_yuv420sp_to_yuv420p(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride);
extern int pixfmt_cvt_yuv420p_to_yuv420sp(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride);
extern int pixfmt_cvt_yuv420sp_to_yuv422sp(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride);
extern int pixfmt_cvt_yuv420sp_to_yuv444sp(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride);
extern int pixfmt_cvt_yuv422i_to_yuv422sp(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride);
extern int pixfmt_cvt_yuv420sp_tile4x4_to_yuv420p(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride);

/**
 * RGB/YUV cross-format conversion functions
 */
extern int pixfmt_cvt_rgb888_to_yuv420p(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride);
extern int pixfmt_cvt_yuv420p_to_rgb888(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride);
extern int pixfmt_cvt_rgb565_to_yuv420p(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride);
extern int pixfmt_cvt_yuv420p_to_rgb565(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride);

#ifdef __cplusplus
}
#endif

#endif
