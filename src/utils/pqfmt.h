/**
 * @copyright: Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @brief:     Image format management module
 * @author:
 * @create:    2026-04-16
 */

#ifndef _PQFMT_H_
#define _PQFMT_H_

#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stddef.h>

/**
 * Image format enumeration
 */
typedef enum pqvf_imgfmt {
    PQVF_FMT_INVALID = -1,

    /* RGB unpacked formats */
    PQVF_FMT_RGB888,
    PQVF_FMT_BGR888,
    PQVF_FMT_RGBA8888,
    PQVF_FMT_BGRA8888,
    PQVF_FMT_ARGB8888,
    PQVF_FMT_ABGR8888,

    /* RGB bit-packed formats */
    PQVF_FMT_RGB332,
    PQVF_FMT_BGR233,
    PQVF_FMT_RGB565,
    PQVF_FMT_BGR565,
    PQVF_FMT_RGBA5551,
    PQVF_FMT_ABGR1555,
    PQVF_FMT_RGBA4444,
    PQVF_FMT_ABGR4444,
    PQVF_FMT_RGBA1010102,
    PQVF_FMT_ABGR2101010,

    /* YUV444 raster formats */
    PQVF_FMT_YUV444I_VU24, // DRM_FORMAT_VUY888, YUV444I 8bit, [31:0]=[V8:U8:Y8]
    PQVF_FMT_YUV444I_VU30, // DRM_FORMAT_VUY101010, YUV444I 10bit bit-packed, [29:0]=[V10:U10:Y10]
    PQVF_FMT_YUV444I_XV30, // DRM_FORMAT_XVYU2101010, YUV444I 10bit bit-packed, [31:0]=[X2:V10:Y10:U10]

    PQVF_FMT_YUV444P_YU24, // DRM_FORMAT_YUV444, YUV444P 8bit, planes: Y8-U8-V8
    PQVF_FMT_YUV444P_YV24, // DRM_FORMAT_YVU444, YUV444P 8bit, planes: Y8-V8-U8

    PQVF_FMT_YUV444SP_NV24, // DRM_FORMAT_NV24, YUV444SP 8bit, planes: Y8-U8V8
    PQVF_FMT_YUV444SP_NV42, // DRM_FORMAT_NV42, YUV444SP 8bit, planes: Y8-V8U8
    PQVF_FMT_YUV444SP_NV30, // DRM_FORMAT_NV30, YUV444SP 10bit bit-packed, planes: Y10-U10V10

    /* YUV422 raster formats */
    PQVF_FMT_YUV422I_YUYV, // DRM_FORMAT_YUYV
    PQVF_FMT_YUV422I_YVYU, // DRM_FORMAT_YVYU
    PQVF_FMT_YUV422I_UYVY, // DRM_FORMAT_UYVY
    PQVF_FMT_YUV422I_VYUY, // DRM_FORMAT_VYUY
    PQVF_FMT_YUV422I_Y210, // DRM_FORMAT_Y210, 10bit
    PQVF_FMT_YUV422I_Y212, // DRM_FORMAT_Y212, 12bit
    PQVF_FMT_YUV422I_Y216, // DRM_FORMAT_Y216, 16bit

    PQVF_FMT_YUV422P_YU16, // DRM_FORMAT_YUV422
    PQVF_FMT_YUV422P_YV16, // DRM_FORMAT_YVU422

    PQVF_FMT_YUV422SP_NV16, // DRM_FORMAT_NV16
    PQVF_FMT_YUV422SP_NV61, // DRM_FORMAT_NV61
    PQVF_FMT_YUV422SP_NV20, // DRM_FORMAT_NV20, 10bit

    /* YUV420 raster formats */
    PQVF_FMT_YUV420P_YU12, // DRM_FORMAT_YUV420
    PQVF_FMT_YUV420P_YV12, // DRM_FORMAT_YVU420

    PQVF_FMT_YUV420SP_NV12, // DRM_FORMAT_NV12
    PQVF_FMT_YUV420SP_NV21, // DRM_FORMAT_NV21
    PQVF_FMT_YUV420SP_NV15, // DRM_FORMAT_NV15, 10bit

    /* YUV410 raster formats */
    PQVF_FMT_YUV410P_YUV9, // DRM_FORMAT_YUV410
    PQVF_FMT_YUV410P_YVU9, // DRM_FORMAT_YVU410

    /* YUV411 raster formats */
    PQVF_FMT_YUV411P_YU11, // DRM_FORMAT_YUV411
    PQVF_FMT_YUV411P_YV11, // DRM_FORMAT_YVU411

    /* YUV400 raster formats */
    PQVF_FMT_YUV400_R1,  // DRM_FORMAT_R1, 1bit bit-packed, [7:0]=[R0:R1:R2:R3:R4:R5:R6:R7], Msb order
    PQVF_FMT_YUV400_R2,  // DRM_FORMAT_R2, 2bit bit-packed, [7:0]=[R0:R1:R2:R3]
    PQVF_FMT_YUV400_R4,  // DRM_FORMAT_R4, 4bit bit-packed, [7:0]=[R0:R1]
    PQVF_FMT_YUV400_R8,  // DRM_FORMAT_R8, 8bit unpacked
    PQVF_FMT_YUV400_R10, // DRM_FORMAT_R10, 10bit bit-packed, [15:0]=[X6:R10]
    PQVF_FMT_YUV400_R12, // DRM_FORMAT_R12, 12bit bit-packed, [15:0]=[X4:R12]
    PQVF_FMT_YUV400_R16, // DRM_FORMAT_R16, 16bit unpacked

    /* YUV tile formats */
    PQVF_FMT_YUV444SP_TILE4X4,
    PQVF_FMT_YUV422SP_TILE4x4,
    PQVF_FMT_YUV420SP_TILE4X4,

    /* Reserved for maximum value */
    PQVF_FMT_MAX
} pqvf_imgfmt_e;

/**
 * Base format type enumeration
 */
typedef enum pqvf_base_type {
    PQVF_BASE_TYPE_UNKNOWN = 0,
    PQVF_BASE_TYPE_YUV = 1,
    PQVF_BASE_TYPE_RGB = 2,
    PQVF_BASE_TYPE_MAX
} pqvf_base_type_e;

typedef enum pqfmt_layout {
    PQFMT_LAYOUT_INTERLEAVED = 0,
    PQFMT_LAYOUT_PLANAR = 1,
    PQFMT_LAYOUT_SEMIPLANAR = 2,
    PQFMT_LAYOUT_TILE = 3,
    PQFMT_LAYOUT_IRREGULAR = 4,
    PQFMT_LAYOUT_MAX
} pqfmt_layout_e;


/* forward declarations */
struct pqfmt_rgb_desc;
struct pqfmt_yuv_desc;

/**
 * Format description structure
 */
typedef struct pqvf_fmt_attr {
    pqvf_imgfmt_e fmt_id;
    uint32_t drm_fourcc;

    const char *full_name;
    const char *short_name;
    const char *alias;

    uint8_t bpp;
    uint8_t depth;
    pqfmt_layout_e layout;

    pqvf_base_type_e base_type;
    union {
        const struct pqfmt_rgb_desc *rgb;
        const struct pqfmt_yuv_desc *yuv;
    } desc;

    bool is_packed;
    bool has_padding;
} pqvf_fmt_attr_s;

#ifdef __cplusplus
extern "C" {
#endif

/* ========== Format query functions ========== */
extern const pqvf_fmt_attr_s *pqvf_get_fmt_desc(pqvf_imgfmt_e fmt_id);
extern const pqvf_fmt_attr_s *pqvf_get_fmt_desc_by_name(const char *name);
extern const pqvf_fmt_attr_s *pqvf_get_fmt_desc_by_fourcc(uint32_t fourcc);

/* ========== General information retrieval ========== */
extern const char *pqvf_fmt_full_name(pqvf_imgfmt_e fmt_id);
extern const char *pqvf_fmt_short_name(pqvf_imgfmt_e fmt_id);
extern const char *pqvf_fmt_alias(pqvf_imgfmt_e fmt_id);
extern int pqvf_fmt_bpp(pqvf_imgfmt_e fmt_id);
extern int pqvf_fmt_depth(pqvf_imgfmt_e fmt_id);
extern int pqvf_fmt_plane_count(pqvf_imgfmt_e fmt_id);

/* ========== Size calculation ========== */
extern float pqvf_fmt_pitch_ratio(pqvf_imgfmt_e fmt_id);
extern float pqvf_fmt_framesize_ratio(pqvf_imgfmt_e fmt_id);
extern int pqvf_fmt_vir_wid(pqvf_imgfmt_e fmt_id, int wid, int hs);
extern size_t pqvf_fmt_framesize(pqvf_imgfmt_e fmt_id, int w, int h, int ws, int hs);
extern size_t pqvf_fmt_planesize(pqvf_imgfmt_e fmt_id, int plane_idx, int w, int h, int ws, int hs);

/* ========== YUV specific functions ========== */
extern bool pqvf_fmt_is_yuv(pqvf_imgfmt_e fmt_id);
extern bool pqvf_fmt_is_uv_order(pqvf_imgfmt_e fmt_id);
extern bool pqvf_fmt_is_tile(pqvf_imgfmt_e fmt_id);
extern int pqvf_fmt_get_tile_size(pqvf_imgfmt_e fmt_id, int *tile_w, int *tile_h);
extern int pqvf_fmt_get_chroma_subsampling(pqvf_imgfmt_e fmt_id, int *h_sub, int *v_sub);

/* ========== RGB specific functions ========== */
extern bool pqvf_fmt_is_rgb(pqvf_imgfmt_e fmt_id);
extern bool pqvf_fmt_is_bgr_order(pqvf_imgfmt_e fmt_id);
extern bool pqvf_fmt_has_alpha(pqvf_imgfmt_e fmt_id);
extern int pqvf_fmt_get_channel_bits(pqvf_imgfmt_e fmt_id, uint8_t *r, uint8_t *g, uint8_t *b, uint8_t *a);

/* ========== Conversion capability query ========== */
extern bool pqvf_fmt_can_input(pqvf_imgfmt_e fmt_id);
extern bool pqvf_fmt_can_output(pqvf_imgfmt_e fmt_id);
extern pqvf_imgfmt_e pqvf_fmt_get_canonical(pqvf_imgfmt_e fmt_id);
extern pqvf_imgfmt_e *pqvf_get_supported_input_fmts(int *count);
extern pqvf_imgfmt_e *pqvf_get_supported_output_fmts(int *count);

/* ========== DRM FourCC mapping ========== */
extern pqvf_imgfmt_e pqvf_from_drm_fourcc(uint32_t fourcc);
extern uint32_t pqvf_to_drm_fourcc(pqvf_imgfmt_e fmt_id);

#ifdef __cplusplus
}
#endif

#endif
