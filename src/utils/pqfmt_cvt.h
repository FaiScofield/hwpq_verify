/**
 * @copyright: Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @brief:     Image format conversion module
 * @author:
 * @create:    2026-04-16
 */

#ifndef _PQFMT_CVT_H_
#define _PQFMT_CVT_H_

#include <stdbool.h>
#include <stdint.h>
#include "pqfmt.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Format conversion context
 */
typedef struct pqvf_cvt_ctx {
    pqvf_imgfmt_e src_fmt;
    pqvf_imgfmt_e dst_fmt;
    int src_w;
    int src_h;
    int dst_w;
    int dst_h;
    int src_stride;
    int dst_stride;
} pqvf_cvt_ctx_t;

/**
 * Format conversion initialization
 */
extern int pqvf_cvt_init(pqvf_cvt_ctx_t *ctx, pqvf_imgfmt_e src_fmt, pqvf_imgfmt_e dst_fmt, int w, int h);

/**
 * Format conversion execution
 */
extern int pqvf_cvt_exec(const pqvf_cvt_ctx_t *ctx, const uint8_t *src, uint8_t *dst);

/**
 * Check if format conversion is supported
 */
extern bool pqvf_cvt_is_supported(pqvf_imgfmt_e src_fmt, pqvf_imgfmt_e dst_fmt);

/**
 * Get intermediate format required for conversion
 */
extern pqvf_imgfmt_e pqvf_cvt_get_intermediate_fmt(pqvf_imgfmt_e src_fmt, pqvf_imgfmt_e dst_fmt);

/**
 * RGB conversion functions
 */
extern int pqvf_cvt_rgb888_to_rgb565(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride);
extern int pqvf_cvt_rgb565_to_rgb888(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride);
extern int pqvf_cvt_rgb888_to_rgb332(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride);
extern int pqvf_cvt_rgb332_to_rgb888(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride);

/**
 * YUV conversion functions
 */
extern int pqvf_cvt_yuv420sp_to_yuv420p(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride);
extern int pqvf_cvt_yuv420p_to_yuv420sp(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride);
extern int pqvf_cvt_yuv420sp_to_yuv422sp(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride);
extern int pqvf_cvt_yuv420sp_to_yuv444sp(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride);
extern int pqvf_cvt_yuv422i_to_yuv422sp(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride);
extern int pqvf_cvt_yuv420sp_tile4x4_to_yuv420p(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride);

/**
 * RGB/YUV cross-format conversion functions
 */
extern int pqvf_cvt_rgb888_to_yuv420p(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride);
extern int pqvf_cvt_yuv420p_to_rgb888(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride);
extern int pqvf_cvt_rgb565_to_yuv420p(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride);
extern int pqvf_cvt_yuv420p_to_rgb565(const uint8_t *src, uint8_t *dst, int w, int h, int src_stride, int dst_stride);

#ifdef __cplusplus
}
#endif

#endif
