/**
 * @copyright: Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @brief:     Image format conversion module
 * @author:    vance.wu@rock-chips.com
 * @create:    2026-04-16
 */

#ifndef _PIXFMT_CVT_H_
#define _PIXFMT_CVT_H_

#include "pixfmt_frame.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Check if format conversion is supported
 */
extern bool pixfmt_cvt_is_supported(pixfmt_e src_fmt, pixfmt_e dst_fmt, pixfmt_e *retSrcBaseFmt, pixfmt_e *retDstBaseFmt);

/**
 * Format conversion initialization
 */
extern bool pixfmt_cvt_check(const pixfmt_frame_s *frame0, const pixfmt_frame_s *frame1);

/**
 * Format conversion execution
 */
extern int pixfmt_cvt_exec(const pixfmt_frame_s *frame0, pixfmt_frame_s *frame1);



/**
 * RGB conversion functions
 */


/**
 * YUV conversion functions
 */
extern int pixfmt_cvt_yuv420sp_to_yuv420p(const void *src, void *dst, int w, int h, int src_stride, int dst_stride);
extern int pixfmt_cvt_yuv420p_to_yuv420sp(const void *src, void *dst, int w, int h, int src_stride, int dst_stride);
extern int pixfmt_cvt_yuv420sp_to_yuv422sp(const void *src, void *dst, int w, int h, int src_stride, int dst_stride);
extern int pixfmt_cvt_yuv420sp_to_yuv444sp(const void *src, void *dst, int w, int h, int src_stride, int dst_stride);
extern int pixfmt_cvt_yuv422i_to_yuv422sp(const void *src, void *dst, int w, int h, int src_stride, int dst_stride);
extern int pixfmt_cvt_yuv420sp_tile4x4_to_yuv420p(const void *src, void *dst, int w, int h, int src_stride, int dst_stride);

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
