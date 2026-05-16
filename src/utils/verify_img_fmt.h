/**
 * @copyright: Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @bref:      verify_img_fmt.h
 * @author:    vance.wu@rock-chips.com
 * @create:    2025-09-05
 * @modifier:  vance.wu@rock-chips.com
 * @modify:    2026-03-10
 */

#ifndef _VERIFY_IMG_FMT_H_
#define _VERIFY_IMG_FMT_H_

#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#define PQVF_IMG_FMT_MAX_CODE 0x003F

/* image format definition */
enum common_verify_imgfmt {
    /* 8bit unpacked formats */
    RGB888 = 0x0,     // [23:0]=[B8:G8:R8]. DRM_FORMAT_BGR888
    RGBA8888 = 0x1,   // [31:0]=[A8:B8:G8:R8]. DRM_FORMAT_ABGR8888
    RGB_PLANAR = 0x2, // plane order: R-G-B
    YUV444P = 0x3,    // YU24, plane order: Y-U-V. DRM_FORMAT_YUV444
    YUV444SP = 0x4,   // NV24, plane order: Y-UV. DRM_FORMAT_NV24
    YUV444I = 0x5,    // VU24, [23:0]=[V8:U8:Y8]. DRM_FORMAT_VUY888
    YUV422P = 0x6,    // YU16, plane order: Y-U-V. DRM_FORMAT_YUV422
    YUV422SP = 0x7,   // NV16, plane order: Y-UV. DRM_FORMAT_NV16
    YUV420P = 0x8,    // YU12, plane order: Y-U-V. DRM_FORMAT_YUV420
    YUV420SP = 0x9,   // NV12, plane order: Y-UV. DRM_FORMAT_NV12
    YUV400 = 0xa,     // Grayscale, DRM_FORMAT_R8

    /* 10bit lsb + 6bit padding formats */
    RGB_101010LSB = RGB888 + 0x10,
    /* NO RGBA_10101010LSB format */
    RGB_PLANAR10LSB = RGB_PLANAR + 0x10,
    YUV444P_10LSB = YUV444P + 0x10,
    YUV444SP_10LSB = YUV444SP + 0x10,
    YUV444I_10LSB = YUV444I + 0x10,
    YUV422P_10LSB = YUV422P + 0x10,
    YUV422SP_10LSB = YUV422SP + 0x10,
    YUV420P_10LSB = YUV420P + 0x10,
    YUV420SP_10LSB = YUV420SP + 0x10,
    YUV400_10LSB = YUV400 + 0x10,

    /* 10bit packed formats */
    RGB_10PACKED = RGB888 + 0x20,           // [29:0]=[B10:G10:R10]
    RGBA_1010102 = RGBA8888 + 0x20,         // [31:0]=[A2:B10:G10:R10], DRM_FORMAT_ABGR2101010
    RGB_PLANAR10PACKED = RGB_PLANAR + 0x20, //
    YUV444P_10PACKED = YUV444P + 0x20,      //
    YUV444SP_10PACKED = YUV444SP + 0x20,    // NV30, [19:0]=[V10:U10] for chroma plane. DRM_FORMAT_NV30
    YUV444I_10PACKED = YUV444I + 0x20,      // [29:0]=[V10:U10:Y10], DRM_FORMAT_VUY101010
    YUV422P_10PACKED = YUV422P + 0x20,      //
    YUV422SP_10PACKED = YUV422SP + 0x20,    // NV20, [19:0]=[V10:U10] for chroma plane. DRM_FORMAT_NV20
    YUV420P_10PACKED = YUV420P + 0x20,      //
    YUV420SP_10PACKED = YUV420SP + 0x20,    // NV15, [19:0]=[V10:U10] for chroma plane. DRM_FORMAT_NV15
    YUV400_10PACKED = YUV400 + 0x20,

    /* 8bit tile 4x4 */
    YUV444SP_TILE4X4 = YUV444SP + 0x30,
    YUV422SP_TILE4X4 = YUV422SP + 0x30,
    YUV420SP_TILE4X4 = YUV420SP + 0x30,
    YUV400_TILE4X4 = YUV400 + 0x30,

    /* 10bit tile 4x4 */
    YUV444SP_TILE4X4_10PACKED = YUV444SP + 0x40,
    YUV422SP_TILE4X4_10PACKED = YUV422SP + 0x40,
    YUV420SP_TILE4X4_10PACKED = YUV420SP + 0x40,
    YUV400_TILE4X4_10PACKED = YUV400 + 0x40,
};

const char *common_verify_imgfmt_name(int fmt);
const char *common_verify_imgfmt_full_name(int fmt);
const char *common_verify_imgfmt_exten_str(int fmt);
int common_verify_imgfmt_depth(int fmt);
int common_verify_imgfmt_bpp(int fmt);
// ws/hs set to 0 to use default virtual size
int common_verify_imgfmt_framesize(int fmt, int w, int h, int ws, int hs);
float common_verify_imgfmt_pitch_ratio(int fmt);
float common_verify_imgfmt_framesize_ratio(int fmt); // get the framesize ratio to the first planesize
static inline bool common_verify_imgfmt_is_yuv(int fmt) { return (fmt & 0xF) >= 3; }
static inline bool common_verify_imgfmt_is_yuv444(int fmt) { return (fmt & 0xF) >= 3 && (fmt & 0xF) <= 5; }
static inline bool common_verify_imgfmt_is_yuv422(int fmt) { return (fmt & 0xF) >= 6 && (fmt & 0xF) <= 7; }
static inline bool common_verify_imgfmt_is_yuv420(int fmt) { return (fmt & 0xF) >= 8 && (fmt & 0xF) <= 9; }
static inline bool common_verify_imgfmt_is_rgb(int fmt) { return (fmt & 0xF) < 3; }
static inline bool common_verify_imgfmt_is_raster(int fmt) { return fmt < 0x30; }
static inline bool common_verify_imgfmt_is_tile(int fmt) { return fmt >= 0x30; }
int common_verify_imgfmt_get_tile_bytes(int fmt);
int common_verify_imgfmt_get_def_planar(int fmt, int depth);

/* colorspace definition */
enum common_verify_colorspace {
    RGBLIMIT = 0x0,
    RGBFULL = 0x1,
    YUV601L = 0x2,
    YUV601F = 0x3,
    YUV709L = 0x4,
    YUV709F = 0x5,
    YUV2020L = 0x8,
    YUV2020F = 0x9,
};

const char *common_verify_clrspc_str(int clrspc);
int common_verify_clrspc_offset(int clrspc, int bit_depth, int *offsetx3);
static inline bool common_verify_clrspc_is_full_range(int clrspc) { return clrspc & 0x1; }
/* convert common_verify_colorspace to drm_color_encoding, <0 if error */
int common_verify_clrspc_to_kernel_encoding(int clrspc);

/* dither type definition */
enum common_verify_dither_type {
    DITHER_NONE = 0,     // roud + shift
    DITHER_SCALE = 1,    // up/down
    DITHER_FILL_MSB = 2, // up
};

#ifdef __cplusplus
}
#endif
#endif // _VERIFY_IMG_FMT_H_