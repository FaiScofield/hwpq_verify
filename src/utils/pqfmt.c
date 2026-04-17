/**
 * @copyright: Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @brief:     Image format management module implementation
 * @author:
 * @create:    2026-04-16
 */

#include "pqfmt.h"
#include "pqfmt_rgb.h"
#include "pqfmt_yuv.h"

#include <string.h>


/**
 * Format description table */
static const pqvf_fmt_attr_s g_fmt_desc_table[] = {
    /* RGB format - 8bit */
    [PQVF_FMT_RGB888] = {
        .fmt_id = PQVF_FMT_RGB888,
        .drm_fourcc = 0,
        .full_name = "rgb888",
        .short_name = "rgb24",
        .alias = "rgb",
        .bpp = 24,
        .depth = 8,
        .layout = PQFMT_LAYOUT_INTERLEAVED,
        .base_type = PQVF_BASE_TYPE_RGB,
        .desc = &g_rgb_desc_rgb888,
        .is_packed = false,
        .has_padding = false,
    },

    [PQVF_FMT_BGR888] = {
        .fmt_id = PQVF_FMT_BGR888,
        .drm_fourcc = 0,
        .full_name = "bgr888",
        .short_name = "bgr24",
        .alias = "bgr",
        .bpp = 24,
        .depth = 8,
        .layout = PQFMT_LAYOUT_INTERLEAVED,
        .base_type = PQVF_BASE_TYPE_RGB,
        .desc = &g_rgb_desc_bgr888,
        .is_packed = false,
        .has_padding = false,
    },

    [PQVF_FMT_RGBA8888] = {
        .fmt_id = PQVF_FMT_RGBA8888,
        .drm_fourcc = 0,
        .full_name = "rgba8888",
        .short_name = "rgba32",
        .alias = "rgba",
        .bpp = 32,
        .depth = 8,
        .layout = PQFMT_LAYOUT_INTERLEAVED,
        .base_type = PQVF_BASE_TYPE_RGB,
        .desc = &g_rgb_desc_rgba8888,
        .is_packed = false,
        .has_padding = false,
    },

    [PQVF_FMT_BGRA8888] = {
        .fmt_id = PQVF_FMT_BGRA8888,
        .drm_fourcc = 0,
        .full_name = "bgra8888",
        .short_name = "bgra32",
        .alias = "bgra",
        .bpp = 32,
        .depth = 8,
        .layout = PQFMT_LAYOUT_INTERLEAVED,
        .base_type = PQVF_BASE_TYPE_RGB,
        .desc = &g_rgb_desc_bgra8888,
        .is_packed = false,
        .has_padding = false,
    },

    [PQVF_FMT_ARGB8888] = {
        .fmt_id = PQVF_FMT_ARGB8888,
        .drm_fourcc = 0,
        .full_name = "argb8888",
        .short_name = "argb32",
        .alias = "argb",
        .bpp = 32,
        .depth = 8,
        .layout = PQFMT_LAYOUT_INTERLEAVED,
        .base_type = PQVF_BASE_TYPE_RGB,
        .desc = &g_rgb_desc_argb8888,
        .is_packed = false,
        .has_padding = false,
    },

    [PQVF_FMT_ABGR8888] = {
        .fmt_id = PQVF_FMT_ABGR8888,
        .drm_fourcc = 0,
        .full_name = "abgr8888",
        .short_name = "abgr32",
        .alias = "abgr",
        .bpp = 32,
        .depth = 8,
        .layout = PQFMT_LAYOUT_INTERLEAVED,
        .base_type = PQVF_BASE_TYPE_RGB,
        .desc = &g_rgb_desc_abgr8888,
        .is_packed = false,
        .has_padding = false,
    },

    /* RGB bit-packed format */
    [PQVF_FMT_RGB332] = {
        .fmt_id = PQVF_FMT_RGB332,
        .drm_fourcc = 0,
        .full_name = "rgb332",
        .short_name = "rgb332",
        .alias = NULL,
        .bpp = 8,
        .depth = 8,
        .layout = PQFMT_LAYOUT_INTERLEAVED,
        .base_type = PQVF_BASE_TYPE_RGB,
        .desc = &g_rgb_desc_rgb332,
        .is_packed = true,
        .has_padding = false,
    },

    [PQVF_FMT_BGR233] = {
        .fmt_id = PQVF_FMT_BGR233,
        .drm_fourcc = 0,
        .full_name = "bgr233",
        .short_name = "bgr233",
        .alias = NULL,
        .bpp = 8,
        .depth = 8,
        .layout = PQFMT_LAYOUT_INTERLEAVED,
        .base_type = PQVF_BASE_TYPE_RGB,
        .desc = &g_rgb_desc_bgr233,
        .is_packed = true,
        .has_padding = false,
    },

    [PQVF_FMT_RGB565] = {
        .fmt_id = PQVF_FMT_RGB565,
        .drm_fourcc = 0,
        .full_name = "rgb565",
        .short_name = "rgb565",
        .alias = NULL,
        .bpp = 16,
        .depth = 16,
        .layout = PQFMT_LAYOUT_INTERLEAVED,
        .base_type = PQVF_BASE_TYPE_RGB,
        .desc = &g_rgb_desc_rgb565,
        .is_packed = true,
        .has_padding = false,
    },

    [PQVF_FMT_BGR565] = {
        .fmt_id = PQVF_FMT_BGR565,
        .drm_fourcc = 0,
        .full_name = "bgr565",
        .short_name = "bgr565",
        .alias = NULL,
        .bpp = 16,
        .depth = 16,
        .layout = PQFMT_LAYOUT_INTERLEAVED,
        .base_type = PQVF_BASE_TYPE_RGB,
        .desc = &g_rgb_desc_bgr565,
        .is_packed = true,
        .has_padding = false,
    },

    [PQVF_FMT_RGBA5551] = {
        .fmt_id = PQVF_FMT_RGBA5551,
        .drm_fourcc = 0,
        .full_name = "rgba5551",
        .short_name = "rgba5551",
        .alias = NULL,
        .bpp = 16,
        .depth = 16,
        .layout = PQFMT_LAYOUT_INTERLEAVED,
        .base_type = PQVF_BASE_TYPE_RGB,
        .desc = &g_rgb_desc_rgba5551,
        .is_packed = true,
        .has_padding = false,
    },

    [PQVF_FMT_ABGR1555] = {
        .fmt_id = PQVF_FMT_ABGR1555,
        .drm_fourcc = 0,
        .full_name = "abgr1555",
        .short_name = "abgr1555",
        .alias = NULL,
        .bpp = 16,
        .depth = 16,
        .layout = PQFMT_LAYOUT_INTERLEAVED,
        .base_type = PQVF_BASE_TYPE_RGB,
        .desc = &g_rgb_desc_abgr1555,
        .is_packed = true,
        .has_padding = false,
    },

    [PQVF_FMT_RGBA4444] = {
        .fmt_id = PQVF_FMT_RGBA4444,
        .drm_fourcc = 0,
        .full_name = "rgba4444",
        .short_name = "rgba4444",
        .alias = NULL,
        .bpp = 16,
        .depth = 16,
        .layout = PQFMT_LAYOUT_INTERLEAVED,
        .base_type = PQVF_BASE_TYPE_RGB,
        .desc = &g_rgb_desc_rgba4444,
        .is_packed = true,
        .has_padding = false,
    },

    [PQVF_FMT_ABGR4444] = {
        .fmt_id = PQVF_FMT_ABGR4444,
        .drm_fourcc = 0,
        .full_name = "abgr4444",
        .short_name = "abgr4444",
        .alias = NULL,
        .bpp = 16,
        .depth = 16,
        .layout = PQFMT_LAYOUT_INTERLEAVED,
        .base_type = PQVF_BASE_TYPE_RGB,
        .desc = &g_rgb_desc_abgr4444,
        .is_packed = true,
        .has_padding = false,
    },

    [PQVF_FMT_RGBA1010102] = {
        .fmt_id = PQVF_FMT_RGBA1010102,
        .drm_fourcc = 0,
        .full_name = "rgba1010102",
        .short_name = "rgba1010102",
        .alias = NULL,
        .bpp = 32,
        .depth = 32,
        .layout = PQFMT_LAYOUT_INTERLEAVED,
        .base_type = PQVF_BASE_TYPE_RGB,
        .desc = &g_rgb_desc_rgba1010102,
        .is_packed = true,
        .has_padding = true,
    },

    [PQVF_FMT_ABGR2101010] = {
        .fmt_id = PQVF_FMT_ABGR2101010,
        .drm_fourcc = 0,
        .full_name = "abgr2101010",
        .short_name = "abgr2101010",
        .alias = NULL,
        .bpp = 32,
        .depth = 32,
        .layout = PQFMT_LAYOUT_INTERLEAVED,
        .base_type = PQVF_BASE_TYPE_RGB,
        .desc = &g_rgb_desc_abgr1010102,
        .is_packed = true,
        .has_padding = true,
    },

    /* YUV Raster format */
    [PQVF_FMT_YUV444I_VU24] = {
        .fmt_id = PQVF_FMT_YUV444I_VU24,
        .drm_fourcc = 0,
        .full_name = "YUV444 Interleaved VU24",
        .short_name = "yuv444i_vu24",
        .alias = NULL,
        .bpp = 24,
        .depth = 8,
        .layout = PQFMT_LAYOUT_INTERLEAVED,
        .base_type = PQVF_BASE_TYPE_YUV,
        .desc = {.yuv = &g_yuv_desc_yuv444i_vu24},
        .is_packed = false,
        .has_padding = false,
    },

    [PQVF_FMT_YUV444P_YU24] = {
        .fmt_id = PQVF_FMT_YUV444P_YU24,
        .drm_fourcc = 0,
        .full_name = "YUV444 Planar YU24",
        .short_name = "yuv444p_yu24",
        .alias = NULL,
        .bpp = 24,
        .depth = 8,
        .layout = PQFMT_LAYOUT_PLANAR,
        .base_type = PQVF_BASE_TYPE_YUV,
        .desc = {.yuv = &g_yuv_desc_yuv444p_yu24},
        .is_packed = false,
        .has_padding = false,
    },

    [PQVF_FMT_YUV444SP_NV24] = {
        .fmt_id = PQVF_FMT_YUV444SP_NV24,
        .drm_fourcc = 0,
        .full_name = "YUV444 Semi-Planar NV24",
        .short_name = "nv24",
        .alias = "yuv444sp",
        .bpp = 24,
        .depth = 8,
        .layout = PQFMT_LAYOUT_SEMIPLANAR,
        .base_type = PQVF_BASE_TYPE_YUV,
        .desc = {.yuv = &g_yuv_desc_yuv444sp_nv24},
        .is_packed = false,
        .has_padding = false,
    },

    [PQVF_FMT_YUV444SP_NV42] = {
        .fmt_id = PQVF_FMT_YUV444SP_NV42,
        .drm_fourcc = 0,
        .full_name = "YUV444 Semi-Planar NV42",
        .short_name = "nv42",
        .alias = NULL,
        .bpp = 24,
        .depth = 8,
        .layout = PQFMT_LAYOUT_SEMIPLANAR,
        .base_type = PQVF_BASE_TYPE_YUV,
        .desc = {.yuv = &g_yuv_desc_yuv444sp_nv42},
        .is_packed = false,
        .has_padding = false,
    },

    [PQVF_FMT_YUV422I_YUYV] = {
        .fmt_id = PQVF_FMT_YUV422I_YUYV,
        .drm_fourcc = 0,
        .full_name = "YUV422 Interleaved YUYV",
        .short_name = "yuyv",
        .alias = "yuv422i",
        .bpp = 16,
        .depth = 8,
        .layout = PQFMT_LAYOUT_INTERLEAVED,
        .base_type = PQVF_BASE_TYPE_YUV,
        .desc = {.yuv = &g_yuv_desc_yuv422i_yuyv},
        .is_packed = false,
        .has_padding = false,
    },

    [PQVF_FMT_YUV422SP_NV16] = {
        .fmt_id = PQVF_FMT_YUV422SP_NV16,
        .drm_fourcc = 0,
        .full_name = "YUV422 Semi-Planar NV16",
        .short_name = "nv16",
        .alias = "yuv422sp",
        .bpp = 16,
        .depth = 8,
        .layout = PQFMT_LAYOUT_SEMIPLANAR,
        .base_type = PQVF_BASE_TYPE_YUV,
        .desc = {.yuv = &g_yuv_desc_yuv422sp_nv16},
        .is_packed = false,
        .has_padding = false,
    },

    [PQVF_FMT_YUV420P_YU12] = {
        .fmt_id = PQVF_FMT_YUV420P_YU12,
        .drm_fourcc = 0,
        .full_name = "YUV420 Planar YU12",
        .short_name = "yu12",
        .alias = "yuv420p",
        .bpp = 12,
        .depth = 8,
        .layout = PQFMT_LAYOUT_PLANAR,
        .base_type = PQVF_BASE_TYPE_YUV,
        .desc = {.yuv = &g_yuv_desc_yuv420p_yu12},
        .is_packed = false,
        .has_padding = false,
    },

    [PQVF_FMT_YUV420P_YV12] = {
        .fmt_id = PQVF_FMT_YUV420P_YV12,
        .drm_fourcc = 0,
        .full_name = "YUV420 Planar YV12",
        .short_name = "yv12",
        .alias = NULL,
        .bpp = 12,
        .depth = 8,
        .layout = PQFMT_LAYOUT_PLANAR,
        .base_type = PQVF_BASE_TYPE_YUV,
        .desc = {.yuv = &g_yuv_desc_yuv420p_yu12},
        .is_packed = false,
        .has_padding = false,
    },

    [PQVF_FMT_YUV420SP_NV12] = {
        .fmt_id = PQVF_FMT_YUV420SP_NV12,
        .drm_fourcc = 0,
        .full_name = "YUV420 Semi-Planar NV12",
        .short_name = "nv12",
        .alias = "yuv420sp",
        .bpp = 12,
        .depth = 8,
        .layout = PQFMT_LAYOUT_SEMIPLANAR,
        .base_type = PQVF_BASE_TYPE_YUV,
        .desc = {.yuv = &g_yuv_desc_yuv420sp_nv12},
        .is_packed = false,
        .has_padding = false,
    },

    /* YUV Tile format */
    [PQVF_FMT_YUV420SP_TILE4X4] = {
        .fmt_id = PQVF_FMT_YUV420SP_TILE4X4,
        .drm_fourcc = 0,
        .full_name = "YUV420 Semi-Planar Tile 4x4",
        .short_name = "yuv420sp_tile4x4",
        .alias = NULL,
        .bpp = 12,
        .depth = 8,
        .layout = PQFMT_LAYOUT_TILE,
        .base_type = PQVF_BASE_TYPE_YUV,
        .desc = {.yuv = &g_yuv_desc_yuv420sp_tile4x4},
        .is_packed = false,
        .has_padding = false,
    },

    /* YUV Raster format - 10bit */
    [PQVF_FMT_YUV444I_VU30] = {
        .fmt_id = PQVF_FMT_YUV444I_VU30,
        .drm_fourcc = 0,
        .full_name = "YUV444 Interleaved VU30",
        .short_name = "yuv444i_vu30",
        .alias = NULL,
        .bpp = 30,
        .depth = 10,
        .layout = PQFMT_LAYOUT_INTERLEAVED,
        .base_type = PQVF_BASE_TYPE_YUV,
        .desc = {.yuv = &g_yuv_desc_yuv444i_vu30},
        .is_packed = false,
        .has_padding = false,
    },

    [PQVF_FMT_YUV444I_XV30] = {
        .fmt_id = PQVF_FMT_YUV444I_XV30,
        .drm_fourcc = 0,
        .full_name = "YUV444 Interleaved XV30",
        .short_name = "yuv444i_xv30",
        .alias = NULL,
        .bpp = 32,
        .depth = 10,
        .layout = PQFMT_LAYOUT_INTERLEAVED,
        .base_type = PQVF_BASE_TYPE_YUV,
        .desc = {.yuv = &g_yuv_desc_yuv444i_xv30},
        .is_packed = false,
        .has_padding = false,
    },

    [PQVF_FMT_YUV444P_YV24] = {
        .fmt_id = PQVF_FMT_YUV444P_YV24,
        .drm_fourcc = 0,
        .full_name = "YUV444 Planar YV24",
        .short_name = "yuv444p_yv24",
        .alias = NULL,
        .bpp = 24,
        .depth = 8,
        .layout = PQFMT_LAYOUT_PLANAR,
        .base_type = PQVF_BASE_TYPE_YUV,
        .desc = {.yuv = &g_yuv_desc_yuv444p_yv24},
        .is_packed = false,
        .has_padding = false,
    },

    [PQVF_FMT_YUV444SP_NV30] = {
        .fmt_id = PQVF_FMT_YUV444SP_NV30,
        .drm_fourcc = 0,
        .full_name = "YUV444 Semi-Planar NV30",
        .short_name = "nv30",
        .alias = NULL,
        .bpp = 30,
        .depth = 10,
        .layout = PQFMT_LAYOUT_SEMIPLANAR,
        .base_type = PQVF_BASE_TYPE_YUV,
        .desc = {.yuv = &g_yuv_desc_yuv444sp_nv30},
        .is_packed = false,
        .has_padding = false,
    },

    [PQVF_FMT_YUV422I_YVYU] = {
        .fmt_id = PQVF_FMT_YUV422I_YVYU,
        .drm_fourcc = 0,
        .full_name = "YUV422 Interleaved YVYU",
        .short_name = "yvyu",
        .alias = NULL,
        .bpp = 16,
        .depth = 8,
        .layout = PQFMT_LAYOUT_INTERLEAVED,
        .base_type = PQVF_BASE_TYPE_YUV,
        .desc = {.yuv = &g_yuv_desc_yuv422i_yvyu},
        .is_packed = false,
        .has_padding = false,
    },

    [PQVF_FMT_YUV422I_UYVY] = {
        .fmt_id = PQVF_FMT_YUV422I_UYVY,
        .drm_fourcc = 0,
        .full_name = "YUV422 Interleaved UYVY",
        .short_name = "uyvy",
        .alias = NULL,
        .bpp = 16,
        .depth = 8,
        .layout = PQFMT_LAYOUT_INTERLEAVED,
        .base_type = PQVF_BASE_TYPE_YUV,
        .desc = {.yuv = &g_yuv_desc_yuv422i_uyvy},
        .is_packed = false,
        .has_padding = false,
    },

    [PQVF_FMT_YUV422I_VYUY] = {
        .fmt_id = PQVF_FMT_YUV422I_VYUY,
        .drm_fourcc = 0,
        .full_name = "YUV422 Interleaved VYUY",
        .short_name = "vyuy",
        .alias = NULL,
        .bpp = 16,
        .depth = 8,
        .layout = PQFMT_LAYOUT_INTERLEAVED,
        .base_type = PQVF_BASE_TYPE_YUV,
        .desc = {.yuv = &g_yuv_desc_yuv422i_vyuy},
        .is_packed = false,
        .has_padding = false,
    },

    [PQVF_FMT_YUV422I_Y210] = {
        .fmt_id = PQVF_FMT_YUV422I_Y210,
        .drm_fourcc = 0,
        .full_name = "YUV422 Interleaved Y210",
        .short_name = "y210",
        .alias = NULL,
        .bpp = 32,
        .depth = 10,
        .layout = PQFMT_LAYOUT_INTERLEAVED,
        .base_type = PQVF_BASE_TYPE_YUV,
        .desc = {.yuv = &g_yuv_desc_yuv422i_y210},
        .is_packed = false,
        .has_padding = false,
    },

    [PQVF_FMT_YUV422P_YU16] = {
        .fmt_id = PQVF_FMT_YUV422P_YU16,
        .drm_fourcc = 0,
        .full_name = "YUV422 Planar YU16",
        .short_name = "yu16",
        .alias = NULL,
        .bpp = 16,
        .depth = 8,
        .layout = PQFMT_LAYOUT_PLANAR,
        .base_type = PQVF_BASE_TYPE_YUV,
        .desc = {.yuv = &g_yuv_desc_yuv422p_yu16},
        .is_packed = false,
        .has_padding = false,
    },

    [PQVF_FMT_YUV422P_YV16] = {
        .fmt_id = PQVF_FMT_YUV422P_YV16,
        .drm_fourcc = 0,
        .full_name = "YUV422 Planar YV16",
        .short_name = "yv16",
        .alias = NULL,
        .bpp = 16,
        .depth = 8,
        .layout = PQFMT_LAYOUT_PLANAR,
        .base_type = PQVF_BASE_TYPE_YUV,
        .desc = {.yuv = &g_yuv_desc_yuv422p_yv16},
        .is_packed = false,
        .has_padding = false,
    },

    [PQVF_FMT_YUV422SP_NV61] = {
        .fmt_id = PQVF_FMT_YUV422SP_NV61,
        .drm_fourcc = 0,
        .full_name = "YUV422 Semi-Planar NV61",
        .short_name = "nv61",
        .alias = NULL,
        .bpp = 16,
        .depth = 8,
        .layout = PQFMT_LAYOUT_SEMIPLANAR,
        .base_type = PQVF_BASE_TYPE_YUV,
        .desc = {.yuv = &g_yuv_desc_yuv422sp_nv61},
        .is_packed = false,
        .has_padding = false,
    },

    [PQVF_FMT_YUV422SP_NV20] = {
        .fmt_id = PQVF_FMT_YUV422SP_NV20,
        .drm_fourcc = 0,
        .full_name = "YUV422 Semi-Planar NV20",
        .short_name = "nv20",
        .alias = NULL,
        .bpp = 20,
        .depth = 10,
        .layout = PQFMT_LAYOUT_SEMIPLANAR,
        .base_type = PQVF_BASE_TYPE_YUV,
        .desc = {.yuv = &g_yuv_desc_yuv422sp_nv20},
        .is_packed = false,
        .has_padding = false,
    },

    [PQVF_FMT_YUV420SP_NV21] = {
        .fmt_id = PQVF_FMT_YUV420SP_NV21,
        .drm_fourcc = 0,
        .full_name = "YUV420 Semi-Planar NV21",
        .short_name = "nv21",
        .alias = NULL,
        .bpp = 12,
        .depth = 8,
        .layout = PQFMT_LAYOUT_SEMIPLANAR,
        .base_type = PQVF_BASE_TYPE_YUV,
        .desc = {.yuv = &g_yuv_desc_yuv420sp_nv21},
        .is_packed = false,
        .has_padding = false,
    },

    [PQVF_FMT_YUV420SP_NV15] = {
        .fmt_id = PQVF_FMT_YUV420SP_NV15,
        .drm_fourcc = 0,
        .full_name = "YUV420 Semi-Planar NV15",
        .short_name = "nv15",
        .alias = NULL,
        .bpp = 15,
        .depth = 10,
        .layout = PQFMT_LAYOUT_SEMIPLANAR,
        .base_type = PQVF_BASE_TYPE_YUV,
        .desc = {.yuv = &g_yuv_desc_yuv420sp_nv15},
        .is_packed = false,
        .has_padding = false,
    },

    [PQVF_FMT_YUV410P_YUV9] = {
        .fmt_id = PQVF_FMT_YUV410P_YUV9,
        .drm_fourcc = 0,
        .full_name = "YUV410 Planar YUV9",
        .short_name = "yuv9",
        .alias = NULL,
        .bpp = 9,
        .depth = 8,
        .layout = PQFMT_LAYOUT_PLANAR,
        .base_type = PQVF_BASE_TYPE_YUV,
        .desc = {.yuv = &g_yuv_desc_yuv410p_yuv9},
        .is_packed = false,
        .has_padding = false,
    },

    [PQVF_FMT_YUV410P_YVU9] = {
        .fmt_id = PQVF_FMT_YUV410P_YVU9,
        .drm_fourcc = 0,
        .full_name = "YUV410 Planar YVU9",
        .short_name = "yvu9",
        .alias = NULL,
        .bpp = 9,
        .depth = 8,
        .layout = PQFMT_LAYOUT_PLANAR,
        .base_type = PQVF_BASE_TYPE_YUV,
        .desc = {.yuv = &g_yuv_desc_yuv410p_yvu9},
        .is_packed = false,
        .has_padding = false,
    },

    [PQVF_FMT_YUV411P_YU11] = {
        .fmt_id = PQVF_FMT_YUV411P_YU11,
        .drm_fourcc = 0,
        .full_name = "YUV411 Planar YU11",
        .short_name = "yu11",
        .alias = NULL,
        .bpp = 12,
        .depth = 8,
        .layout = PQFMT_LAYOUT_PLANAR,
        .base_type = PQVF_BASE_TYPE_YUV,
        .desc = {.yuv = &g_yuv_desc_yuv411p_yu11},
        .is_packed = false,
        .has_padding = false,
    },

    [PQVF_FMT_YUV411P_YV11] = {
        .fmt_id = PQVF_FMT_YUV411P_YV11,
        .drm_fourcc = 0,
        .full_name = "YUV411 Planar YV11",
        .short_name = "yv11",
        .alias = NULL,
        .bpp = 12,
        .depth = 8,
        .layout = PQFMT_LAYOUT_PLANAR,
        .base_type = PQVF_BASE_TYPE_YUV,
        .desc = {.yuv = &g_yuv_desc_yuv411p_yv11},
        .is_packed = false,
        .has_padding = false,
    },

    /* YUV Tile format */
    [PQVF_FMT_YUV444SP_TILE4X4] = {
        .fmt_id = PQVF_FMT_YUV444SP_TILE4X4,
        .drm_fourcc = 0,
        .full_name = "YUV444 Semi-Planar Tile 4x4",
        .short_name = "yuv444sp_tile4x4",
        .alias = NULL,
        .bpp = 24,
        .depth = 8,
        .layout = PQFMT_LAYOUT_TILE,
        .base_type = PQVF_BASE_TYPE_YUV,
        .desc = {.yuv = &g_yuv_desc_yuv444sp_tile4x4},
        .is_packed = false,
        .has_padding = false,
    },

    [PQVF_FMT_YUV422SP_TILE4x4] = {
        .fmt_id = PQVF_FMT_YUV422SP_TILE4x4,
        .drm_fourcc = 0,
        .full_name = "YUV422 Semi-Planar Tile 4x4",
        .short_name = "yuv422sp_tile4x4",
        .alias = NULL,
        .bpp = 16,
        .depth = 8,
        .layout = PQFMT_LAYOUT_TILE,
        .base_type = PQVF_BASE_TYPE_YUV,
        .desc = {.yuv = &g_yuv_desc_yuv422sp_tile4x4},
        .is_packed = false,
        .has_padding = false,
    },
};

#define FMT_DESC_TABLE_SIZE (sizeof(g_fmt_desc_table) / sizeof(pqvf_fmt_attr_s))

const pqvf_fmt_attr_s *pqvf_get_fmt_desc(pqvf_imgfmt_e fmt_id) {
    if (fmt_id >= 0 && fmt_id < PQVF_FMT_MAX) {
        return &g_fmt_desc_table[fmt_id];
    }
    return NULL;
}

const pqvf_fmt_attr_s *pqvf_get_fmt_desc_by_name(const char *name) {
    for (int i = 0; i < FMT_DESC_TABLE_SIZE; i++) {
        if (g_fmt_desc_table[i].full_name && strcmp(g_fmt_desc_table[i].full_name, name) == 0) {
            return &g_fmt_desc_table[i];
        }
        if (g_fmt_desc_table[i].short_name && strcmp(g_fmt_desc_table[i].short_name, name) == 0) {
            return &g_fmt_desc_table[i];
        }
        if (g_fmt_desc_table[i].alias && strcmp(g_fmt_desc_table[i].alias, name) == 0) {
            return &g_fmt_desc_table[i];
        }
    }
    return NULL;
}

const pqvf_fmt_attr_s *pqvf_get_fmt_desc_by_fourcc(uint32_t fourcc) {
    for (int i = 0; i < FMT_DESC_TABLE_SIZE; i++) {
        if (g_fmt_desc_table[i].drm_fourcc == fourcc) {
            return &g_fmt_desc_table[i];
        }
    }
    return NULL;
}

const char *pqvf_fmt_full_name(pqvf_imgfmt_e fmt_id) {
    const pqvf_fmt_attr_s *desc = pqvf_get_fmt_desc(fmt_id);
    return desc ? desc->full_name : "UnknownFmt";
}

const char *pqvf_fmt_short_name(pqvf_imgfmt_e fmt_id) {
    const pqvf_fmt_attr_s *desc = pqvf_get_fmt_desc(fmt_id);
    return desc ? desc->short_name : "unknown";
}

const char *pqvf_fmt_alias(pqvf_imgfmt_e fmt_id) {
    const pqvf_fmt_attr_s *desc = pqvf_get_fmt_desc(fmt_id);
    return desc ? (desc->alias ? desc->alias : "") : "";
}

int pqvf_fmt_bpp(pqvf_imgfmt_e fmt_id) {
    const pqvf_fmt_attr_s *desc = pqvf_get_fmt_desc(fmt_id);
    return desc ? desc->bpp : 0;
}

int pqvf_fmt_depth(pqvf_imgfmt_e fmt_id) {
    const pqvf_fmt_attr_s *desc = pqvf_get_fmt_desc(fmt_id);
    return desc ? desc->depth : 0;
}

int pqvf_fmt_plane_count(pqvf_imgfmt_e fmt_id) {
    const pqvf_fmt_attr_s *desc = pqvf_get_fmt_desc(fmt_id);
    if (!desc) return 0;

    switch (desc->layout) {
        case PQFMT_LAYOUT_PLANAR: return 3;
        case PQFMT_LAYOUT_SEMIPLANAR: return 2;
        case PQFMT_LAYOUT_INTERLEAVED: return 1;
        default: return 0;
    }
}

float pqvf_fmt_pitch_ratio(pqvf_imgfmt_e fmt_id) {
    const pqvf_fmt_attr_s *desc = pqvf_get_fmt_desc(fmt_id);
    if (!desc) return 0.0f;

    if (desc->base_type == PQVF_BASE_TYPE_RGB) {
        return pqfmt_rgb_desc_calc_pitch_ratio(desc->desc.rgb);
    } else if (desc->base_type == PQVF_BASE_TYPE_YUV) {
        return pqfmt_yuv_desc_calc_pitch_ratio(desc->desc.yuv);
    }
    return 0.0f;
}

float pqvf_fmt_framesize_ratio(pqvf_imgfmt_e fmt_id) {
    const pqvf_fmt_attr_s *desc = pqvf_get_fmt_desc(fmt_id);
    if (!desc) return 0.0f;

    if (desc->base_type == PQVF_BASE_TYPE_YUV) {
        return pqfmt_yuv_desc_calc_framesize_ratio(desc->desc.yuv);
    }
    return 1.0f;
}

int pqvf_fmt_vir_wid(pqvf_imgfmt_e fmt_id, int wid, int hs) {
    return (int)(wid * pqvf_fmt_pitch_ratio(fmt_id));
}

size_t pqvf_fmt_framesize(pqvf_imgfmt_e fmt_id, int w, int h, int ws, int hs) {
    const pqvf_fmt_attr_s *desc = pqvf_get_fmt_desc(fmt_id);
    if (!desc) return 0;

    int vir_w = pqvf_fmt_vir_wid(fmt_id, w, hs);
    return (size_t)(vir_w * h * pqvf_fmt_framesize_ratio(fmt_id));
}

bool pqvf_fmt_is_yuv(pqvf_imgfmt_e fmt_id) {
    const pqvf_fmt_attr_s *desc = pqvf_get_fmt_desc(fmt_id);
    return desc ? desc->base_type == PQVF_BASE_TYPE_YUV : false;
}

bool pqvf_fmt_is_rgb(pqvf_imgfmt_e fmt_id) {
    const pqvf_fmt_attr_s *desc = pqvf_get_fmt_desc(fmt_id);
    return desc ? desc->base_type == PQVF_BASE_TYPE_RGB : false;
}

bool pqvf_fmt_is_uv_order(pqvf_imgfmt_e fmt_id) {
    const pqvf_fmt_attr_s *desc = pqvf_get_fmt_desc(fmt_id);
    if (!desc || desc->base_type != PQVF_BASE_TYPE_YUV) return false;
    return pqfmt_yuv_desc_is_uv_order(desc->desc.yuv);
}

bool pqvf_fmt_is_tile(pqvf_imgfmt_e fmt_id) {
    const pqvf_fmt_attr_s *desc = pqvf_get_fmt_desc(fmt_id);
    if (!desc || desc->base_type != PQVF_BASE_TYPE_YUV) return false;
    return pqfmt_yuv_desc_is_tile(desc->desc.yuv);
}

bool pqvf_fmt_is_bgr_order(pqvf_imgfmt_e fmt_id) {
    const pqvf_fmt_attr_s *desc = pqvf_get_fmt_desc(fmt_id);
    if (!desc || desc->base_type != PQVF_BASE_TYPE_RGB) return false;
    return pqfmt_rgb_desc_is_bgr_order(desc->desc.rgb);
}

bool pqvf_fmt_has_alpha(pqvf_imgfmt_e fmt_id) {
    const pqvf_fmt_attr_s *desc = pqvf_get_fmt_desc(fmt_id);
    if (!desc || desc->base_type != PQVF_BASE_TYPE_RGB) return false;
    return pqfmt_rgb_desc_has_alpha(desc->desc.rgb);
}

int pqvf_fmt_get_channel_bits(pqvf_imgfmt_e fmt_id, uint8_t *r, uint8_t *g, uint8_t *b, uint8_t *a) {
    const pqvf_fmt_attr_s *desc = pqvf_get_fmt_desc(fmt_id);
    if (!desc || desc->base_type != PQVF_BASE_TYPE_RGB) return 0;
    return pqfmt_rgb_desc_get_channel_bits(desc->desc.rgb, r, g, b, a);
}

int pqvf_fmt_get_tile_size(pqvf_imgfmt_e fmt_id, int *tile_w, int *tile_h) {
    const pqvf_fmt_attr_s *desc = pqvf_get_fmt_desc(fmt_id);
    if (!desc || desc->base_type != PQVF_BASE_TYPE_YUV) return -1;
    return pqfmt_yuv_desc_get_tile_size(desc->desc.yuv, tile_w, tile_h);
}

int pqvf_fmt_get_chroma_subsampling(pqvf_imgfmt_e fmt_id, int *h_sub, int *v_sub) {
    const pqvf_fmt_attr_s *desc = pqvf_get_fmt_desc(fmt_id);
    if (!desc || desc->base_type != PQVF_BASE_TYPE_YUV) return -1;
    return pqfmt_yuv_desc_get_chroma_subsampling(desc->desc.yuv, h_sub, v_sub);
}

bool pqvf_fmt_can_input(pqvf_imgfmt_e fmt_id) {
    const pqvf_fmt_attr_s *desc = pqvf_get_fmt_desc(fmt_id);
    return desc != NULL;
}

bool pqvf_fmt_can_output(pqvf_imgfmt_e fmt_id) {
    const pqvf_fmt_attr_s *desc = pqvf_get_fmt_desc(fmt_id);
    return desc != NULL;
}

pqvf_imgfmt_e pqvf_fmt_get_canonical(pqvf_imgfmt_e fmt_id) {
    return fmt_id;
}

pqvf_imgfmt_e pqvf_from_drm_fourcc(uint32_t fourcc) {
    return PQVF_FMT_INVALID;
}

uint32_t pqvf_to_drm_fourcc(pqvf_imgfmt_e fmt_id) {
    const pqvf_fmt_attr_s *desc = pqvf_get_fmt_desc(fmt_id);
    return desc ? desc->drm_fourcc : 0;
}

pqvf_imgfmt_e *pqvf_get_supported_input_fmts(int *count) {
    *count = FMT_DESC_TABLE_SIZE;
    pqvf_imgfmt_e *fmts = malloc(sizeof(pqvf_imgfmt_e) * FMT_DESC_TABLE_SIZE);
    if (fmts) {
        for (int i = 0; i < FMT_DESC_TABLE_SIZE; i++) {
            fmts[i] = g_fmt_desc_table[i].fmt_id;
        }
    }
    return fmts;
}

pqvf_imgfmt_e *pqvf_get_supported_output_fmts(int *count) {
    *count = FMT_DESC_TABLE_SIZE;
    pqvf_imgfmt_e *fmts = malloc(sizeof(pqvf_imgfmt_e) * FMT_DESC_TABLE_SIZE);
    if (fmts) {
        for (int i = 0; i < FMT_DESC_TABLE_SIZE; i++) {
            fmts[i] = g_fmt_desc_table[i].fmt_id;
        }
    }
    return fmts;
}
