/**
 * @copyright: Copyright (c) Rockchip Electronics Co., Ltd. 2026-. All rights reserved.
 * @brief:     Image format management module
 * @author:    vance.wu@rock-chips.com
 * @create:    2026-04-16
 */

#ifndef _PIXFMT_H_
#define _PIXFMT_H_

#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stddef.h>

/**
 * Image format enumeration
 */
typedef enum pixfmt {
    PIXFMT_INVALID = -1,

    /* RGB unpacked formats */
    PIXFMT_RGB888,   // DRM_FORMAT_BGR888,   24bpp, [23:0] B:G:R 8:8:8,     unpacked
    PIXFMT_BGR888,   // DRM_FORMAT_RGB888,   24bpp, [23:0] R:G:B 8:8:8,     unpacked
    PIXFMT_RGBA8888, // DRM_FORMAT_ABGR8888, 32bpp, [31:0] A:B:G:R 8:8:8:8, unpacked
    PIXFMT_BGRA8888, // DRM_FORMAT_ARGB8888, 32bpp, [31:0] A:R:G:B 8:8:8:8, unpacked
    PIXFMT_ARGB8888, // DRM_FORMAT_BGRA8888, 32bpp, [31:0] B:G:R:A 8:8:8:8, unpacked
    PIXFMT_ABGR8888, // DRM_FORMAT_RGBA8888, 32bpp, [31:0] R:G:B:A 8:8:8:8, unpacked

    /* RGB bitpacked formats */
    PIXFMT_RGB332,      // DRM_FORMAT_RGB332,       8bpp, [ 7:0] R:G:B 3:3:2,        bitpacked
    PIXFMT_BGR233,      // DRM_FORMAT_BGR233,       8bpp, [ 7:0] B:G:R 2:3:3,        bitpacked
    PIXFMT_RGB565,      // DRM_FORMAT_RGB565,      16bpp, [15:0] R:G:B 5:6:5,        bitpacked
    PIXFMT_BGR565,      // DRM_FORMAT_BGR565,      16bpp, [15:0] B:G:R 5:6:5,        bitpacked
    PIXFMT_RGBA5551,    // DRM_FORMAT_RGBA5551,    16bpp, [15:0] R:G:B:A 5:5:5:1,    bitpacked
    PIXFMT_ABGR1555,    // DRM_FORMAT_ARGB1555,    16bpp, [15:0] A:B:G:R 1:5:5:5,    bitpacked
    PIXFMT_RGBA4444,    // DRM_FORMAT_RGBA4444,    16bpp, [15:0] R:G:B:A 4:4:4:4,    bitpacked
    PIXFMT_ABGR4444,    // DRM_FORMAT_ABGR4444,    16bpp, [15:0] A:B:G:R 4:4:4:4,    bitpacked
    PIXFMT_RGBA1010102, // DRM_FORMAT_RGBA1010102, 32bpp, [31:0] R:G:B:A 10:10:10:2, bitpacked
    PIXFMT_ABGR2101010, // DRM_FORMAT_ABGR2101010, 32bpp, [31:0] R:G:B:A 10:10:10:2, bitpacked

    /* YUV444 raster formats */
    PIXFMT_YUV444I_VU24, // DRM_FORMAT_VUY888,      24bpp, 1 plane: [23:0] V:U:Y 8:8:8,        unpacked
    PIXFMT_YUV444I_VU30, // DRM_FORMAT_VUY101010,   30bpp, 1 plane: [29:0] V:U:Y 10:10:10,     bitpacked
    PIXFMT_YUV444I_XV30, // DRM_FORMAT_XVYU2101010, 32bpp, 1 plane: [31:0] X:V:Y:U 2:10:10:10, bitpacked

    PIXFMT_YUV444P_YU24, // DRM_FORMAT_YUV444, 24bpp, 3 planes: Y8-U8-V8, unpacked
    PIXFMT_YUV444P_YV24, // DRM_FORMAT_YVU444, 24bpp, 3 planes: Y8-V8-U8, unpacked

    PIXFMT_YUV444SP_NV24, // DRM_FORMAT_NV24, 24bpp, 2 planes: Y8-U8V8,    unpacked
    PIXFMT_YUV444SP_NV42, // DRM_FORMAT_NV42, 24bpp, 2 planes: Y8-V8U8,    unpacked
    PIXFMT_YUV444SP_NV30, // DRM_FORMAT_NV30, 30bpp, 2 planes: Y10-U10V10, bitpacked

    /* YUV422 raster formats */
    PIXFMT_YUV422I_YUYV, // DRM_FORMAT_YUYV, 16bpp, 1 plane: [31:0] V0:Y1:U0:Y0 8:8:8:8, unpacked
    PIXFMT_YUV422I_YVYU, // DRM_FORMAT_YVYU, 16bpp, 1 plane: [31:0] U0:Y1:V0:Y0 8:8:8:8, unpacked
    PIXFMT_YUV422I_UYVY, // DRM_FORMAT_UYVY, 16bpp, 1 plane: [31:0] Y1:V0:Y1:U0 8:8:8:8, unpacked
    PIXFMT_YUV422I_VYUY, // DRM_FORMAT_VYUY, 16bpp, 1 plane: [31:0] Y1:U0:Y1:V0 8:8:8:8, unpacked
    PIXFMT_YUV422I_Y210, // DRM_FORMAT_Y210, 32bpp, 1 plane: [63:0] V0:X:Y1:X:U0:X:Y0:X 10:6:10:6:10:6:10:6, unpacked + paddingOnLsb
    PIXFMT_YUV422I_Y212, // DRM_FORMAT_Y212, 32bpp, 1 plane: [63:0] V0:X:Y1:X:U0:X:Y0:X 12:4:12:4:12:4:12:4, unpacked + paddingOnLsb
    PIXFMT_YUV422I_Y216, // DRM_FORMAT_Y216, 32bpp, 1 plane: [63:0] V0:Y1:U0:Y0 16:16:16:16, unpacked

    PIXFMT_YUV422P_YU16, // DRM_FORMAT_YUV422, 16bpp, 3 planes: Y8-U8-V8, unpacked
    PIXFMT_YUV422P_YV16, // DRM_FORMAT_YVU422, 16bpp, 3 planes: Y8-V8-U8, unpacked

    PIXFMT_YUV422SP_NV16, // DRM_FORMAT_NV16, 16bpp, 2 planes: Y8-U8V8,    unpacked
    PIXFMT_YUV422SP_NV61, // DRM_FORMAT_NV61, 16bpp, 2 planes: Y8-V8U8,    unpacked
    PIXFMT_YUV422SP_NV20, // DRM_FORMAT_NV20, 20bpp, 2 planes: Y10-U10V10, unpacked

    /* YUV420 raster formats */
    PIXFMT_YUV420P_YU12, // DRM_FORMAT_YUV420, 12bpp, 3 planes: Y8-U8-V8, unpacked
    PIXFMT_YUV420P_YV12, // DRM_FORMAT_YVU420, 12bpp, 3 planes: Y8-V8-U8, unpacked

    PIXFMT_YUV420SP_NV12, // DRM_FORMAT_NV12, 12bpp, 2 planes: Y8-U8V8,    unpacked
    PIXFMT_YUV420SP_NV21, // DRM_FORMAT_NV21, 12bpp, 2 planes: Y8-V8U8,    unpacked
    PIXFMT_YUV420SP_NV15, // DRM_FORMAT_NV15, 15bpp, 2 planes: Y10-U10V10, unpacked

    /* YUV411 raster formats */
    PIXFMT_YUV411P_YU11, // DRM_FORMAT_YUV411, 12bpp, 3 planes: Y8-U8-V8, unpacked
    PIXFMT_YUV411P_YV11, // DRM_FORMAT_YVU411, 12bpp, 3 planes: Y8-V8-U8, unpacked

    /* YUV410 raster formats */
    PIXFMT_YUV410P_YUV9, // DRM_FORMAT_YUV410, 9bpp, 3 planes: Y8-U8-V8, unpacked
    PIXFMT_YUV410P_YVU9, // DRM_FORMAT_YVU410, 9bpp, 3 planes: Y8-V8-U8, unpacked

    /* YUV400 raster formats */
    PIXFMT_YUV400_R1,  // DRM_FORMAT_R1,   1bpp, [7:0] R0:R1:R2:R3:R4:R5:R6:R7 1:1:1:1:1:1:1:1, bitpacked
    PIXFMT_YUV400_R2,  // DRM_FORMAT_R2,   2bpp, [7:0] R0:R1:R2:R3 2:2:2:2, bitpacked
    PIXFMT_YUV400_R4,  // DRM_FORMAT_R4,   4bpp, [7:0] R0:R1 4:4, bitpacked
    PIXFMT_YUV400_R8,  // DRM_FORMAT_R8,   8bpp, unpacked
    PIXFMT_YUV400_R10, // DRM_FORMAT_R10, 16bpp, [15:0] X:R 6:10, unpacked + paddingOnMsb
    PIXFMT_YUV400_R12, // DRM_FORMAT_R12, 16bpp, [15:0] X:R 4:12, unpacked + paddingOnMsb
    PIXFMT_YUV400_R16, // DRM_FORMAT_R16, 16bpp, unpacked

    /* YUV tile formats */
    PIXFMT_YUV444SP_TILE4X4, // tile for PIXFMT_YUV444SP_NV24, 24bpp, 16+32=48 tile bytes
    PIXFMT_YUV422SP_TILE4x4, // tile for PIXFMT_YUV422SP_NV16, 16bpp, 16+16=32 tile bytes
    PIXFMT_YUV420SP_TILE4X4, // tile for PIXFMT_YUV420SP_NV12, 12bpp, 16+ 8=24 tile bytes

    /* Reserved for maximum value */
    PIXFMT_MAX
} pixfmt_e;

/**
 * Base format type enumeration
 */
typedef enum pixfmt_type {
    PIXFMT_TYPE_UNKNOWN = -1,
    PIXFMT_TYPE_YUV,
    PIXFMT_TYPE_RGB,
    PIXFMT_TYPE_MAX
} pixfmt_type_e;

typedef enum pixfmt_layout {
    PIXFMT_LAYOUT_UNKNOWN = -1,
    PIXFMT_LAYOUT_INTERLEAVED,
    PIXFMT_LAYOUT_PLANAR,
    PIXFMT_LAYOUT_SEMIPLANAR,
    PIXFMT_LAYOUT_TILE,
    PIXFMT_LAYOUT_IRREGULAR,
    PIXFMT_LAYOUT_MAX
} pixfmt_layout_e;

typedef enum pixfmt_bitpacked_order {
    PIXFMT_UNPACKED = 0,
    PIXFMT_BITPACKED_LSB = 1,
    PIXFMT_BITPACKED_MSB = 2,
} pixfmt_bitpacked_order_e;

typedef enum pixfmt_padding_pos {
    PIXFMT_NO_PADDING = 0,
    PIXFMT_PADDING_ON_LSB = 1,
    PIXFMT_PADDING_ON_MSB = 2,
} pixfmt_padding_pos_e;

/* forward declarations */
struct pixfmt_rgb_desc;
struct pixfmt_yuv_desc;

/**
 * Format description structure
 */
typedef struct pixfmt_attr {
    pixfmt_e fmt_id;

    pixfmt_type_e base_type;
    union {
        const struct pixfmt_rgb_desc *rgb;
        const struct pixfmt_yuv_desc *yuv;
    } desc;

    pixfmt_layout_e layout;
    pixfmt_padding_pos_e padding_pos;         // padding_pos is valid only when (depth % 8 != 0)
    pixfmt_bitpacked_order_e bitpacked_order; // bitpacked_order is valid only when (depth % 8 != 0)

    uint8_t bpp;
    uint8_t depth;    // bit-depth of the main channel
    uint8_t nb_comps; // number of components (channels)

    const char *full_name;
    const char *short_name;
    const char *alias;
} pixfmt_attr_s;

#ifdef __cplusplus
extern "C" {
#endif

/* ========== Format query functions ========== */
extern const pixfmt_attr_s *pixfmt_get_attr(pixfmt_e fmt);
extern const pixfmt_attr_s *pixfmt_get_attr_by_name(const char *name);

/* ========== General information retrieval ========== */
extern const char *pixfmt_full_name(pixfmt_e fmt);
extern const char *pixfmt_short_name(pixfmt_e fmt);
extern const char *pixfmt_alias(pixfmt_e fmt);
extern int pixfmt_bpp(pixfmt_e fmt);
extern int pixfmt_depth(pixfmt_e fmt);
extern int pixfmt_nb_comps(pixfmt_e fmt);
extern int pixfmt_nb_planes(pixfmt_e fmt);

/* ========== Size calculation ========== */
extern int pixfmt_get_min_align_width(pixfmt_e fmt, int wid, int *retAlign);
extern int pixfmt_get_min_align_height(pixfmt_e fmt, int hgt, int *retAlign);
extern int pixfmt_get_min_pitches(pixfmt_e fmt, int wid, int *retPitchesx3);
extern size_t pixfmt_get_frame_size(pixfmt_e fmt, int wid, int hgt, int rowpitch);
// extern size_t pixfmt_planesize(pixfmt_e fmt, int plane_idx, int w, int h, int ws, int hs);

/* ========== YUV specific functions ========== */
extern bool pixfmt_is_yuv(pixfmt_e fmt);
extern bool pixfmt_is_uv_order(pixfmt_e fmt);
extern bool pixfmt_is_tile(pixfmt_e fmt);
extern int pixfmt_get_tile_size(pixfmt_e fmt, int *tile_w, int *tile_h);
extern int pixfmt_get_chroma_subsampling(pixfmt_e fmt, int *h_sub, int *v_sub);

/* ========== RGB specific functions ========== */
extern bool pixfmt_is_rgb(pixfmt_e fmt);
extern bool pixfmt_is_bgr_order(pixfmt_e fmt);
extern bool pixfmt_has_alpha(pixfmt_e fmt);
extern int pixfmt_get_channel_bits(pixfmt_e fmt, uint8_t *r, uint8_t *g, uint8_t *b, uint8_t *a);

/* ========== Conversion capability query ========== */
extern bool pixfmt_can_input(pixfmt_e fmt);
extern bool pixfmt_can_output(pixfmt_e fmt);
extern pixfmt_e pixfmt_get_canonical(pixfmt_e fmt);
extern pixfmt_e *pixfmt_get_supported_input_fmts(int *count);
extern pixfmt_e *pixfmt_get_supported_output_fmts(int *count);

/* ========== DRM FourCC mapping ========== */
extern pixfmt_e pixfmt_from_drm_fourcc(uint32_t fourcc);
extern uint32_t pixfmt_to_drm_fourcc(pixfmt_e fmt);

#ifdef __cplusplus
}
#endif

#endif
