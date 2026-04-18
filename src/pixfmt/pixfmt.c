/**
 * @copyright: Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @brief:     Image format management module implementation
 * @author:    vance.wu@rock-chips.com
 * @create:    2026-04-16
 */

#include "pixfmt.h"
#include "pixfmt_rgb.h"
#include "pixfmt_yuv.h"
#include "verify_com.h"

#include <assert.h>
#include <string.h>

/**
 * Format description table */
static const pixfmt_attr_s g_pixfmt_attr_table[] =
    {
        /* RGB format - 8bit */
        [PIXFMT_RGB888] =
            {
                             .fmt_id = PIXFMT_RGB888,
                             .base_type = PIXFMT_TYPE_RGB,
                             .desc = &g_rgb_desc_rgb888,
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             .bpp = 24,
                             .depth = 8,
                             .nb_comps = 3,
                             .full_name = "rgb888",
                             .short_name = "rgb24",
                             .alias = "rgb",
                             },

        [PIXFMT_BGR888] =
            {
                             .fmt_id = PIXFMT_BGR888,
                             .base_type = PIXFMT_TYPE_RGB,
                             .desc = &g_rgb_desc_bgr888,
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             .bpp = 24,
                             .depth = 8,
                             .full_name = "bgr888",
                             .short_name = "bgr24",
                             .alias = "bgr",
                             },

        [PIXFMT_RGBA8888] =
            {
                             .fmt_id = PIXFMT_RGBA8888,
                             .base_type = PIXFMT_TYPE_RGB,
                             .desc = &g_rgb_desc_rgba8888,
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             .bpp = 32,
                             .depth = 8,
                             .full_name = "rgba8888",
                             .short_name = "rgba32",
                             .alias = "rgba",
                             },

        [PIXFMT_BGRA8888] =
            {
                             .fmt_id = PIXFMT_BGRA8888,
                             .base_type = PIXFMT_TYPE_RGB,
                             .desc = &g_rgb_desc_bgra8888,
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             .bpp = 32,
                             .depth = 8,
                             .full_name = "bgra8888",
                             .short_name = "bgra32",
                             .alias = "bgra",
                             },

        [PIXFMT_ARGB8888] =
            {
                             .fmt_id = PIXFMT_ARGB8888,
                             .base_type = PIXFMT_TYPE_RGB,
                             .desc = &g_rgb_desc_argb8888,
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             .bpp = 32,
                             .depth = 8,
                             .full_name = "argb8888",
                             .short_name = "argb32",
                             .alias = "argb",
                             },

        [PIXFMT_ABGR8888] =
            {
                             .fmt_id = PIXFMT_ABGR8888,
                             .base_type = PIXFMT_TYPE_RGB,
                             .desc = &g_rgb_desc_abgr8888,
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             .bpp = 32,
                             .depth = 8,
                             .full_name = "abgr8888",
                             .short_name = "abgr32",
                             .alias = "abgr",
                             },

        /* RGB bit-packed format */
        [PIXFMT_RGB332] =
            {
                             .fmt_id = PIXFMT_RGB332,
                             .base_type = PIXFMT_TYPE_RGB,
                             .desc = &g_rgb_desc_rgb332,
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_BITPACKED_LSB,
                             .bpp = 8,
                             .depth = 8,
                             .full_name = "rgb332",
                             .short_name = "rgb332",
                             .alias = NULL,
                             },

        [PIXFMT_BGR233] =
            {
                             .fmt_id = PIXFMT_BGR233,
                             .base_type = PIXFMT_TYPE_RGB,
                             .desc = &g_rgb_desc_bgr233,
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_BITPACKED_LSB,
                             .bpp = 8,
                             .depth = 8,
                             .full_name = "bgr233",
                             .short_name = "bgr233",
                             .alias = NULL,
                             },

        [PIXFMT_RGB565] =
            {
                             .fmt_id = PIXFMT_RGB565,
                             .base_type = PIXFMT_TYPE_RGB,
                             .desc = &g_rgb_desc_rgb565,
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_BITPACKED_LSB,
                             .bpp = 16,
                             .depth = 16,
                             .full_name = "rgb565",
                             .short_name = "rgb565",
                             .alias = NULL,
                             },

        [PIXFMT_BGR565] =
            {
                             .fmt_id = PIXFMT_BGR565,
                             .base_type = PIXFMT_TYPE_RGB,
                             .desc = &g_rgb_desc_bgr565,
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_BITPACKED_LSB,
                             .bpp = 16,
                             .depth = 16,
                             .full_name = "bgr565",
                             .short_name = "bgr565",
                             .alias = NULL,
                             },

        [PIXFMT_RGBA5551] =
            {
                             .fmt_id = PIXFMT_RGBA5551,
                             .base_type = PIXFMT_TYPE_RGB,
                             .desc = &g_rgb_desc_rgba5551,
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_BITPACKED_LSB,
                             .bpp = 16,
                             .depth = 16,
                             .full_name = "rgba5551",
                             .short_name = "rgba5551",
                             .alias = NULL,
                             },

        [PIXFMT_ABGR1555] =
            {
                             .fmt_id = PIXFMT_ABGR1555,

                             .base_type = PIXFMT_TYPE_RGB,
                             .desc = &g_rgb_desc_abgr1555,
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_BITPACKED_LSB,
                             .bpp = 16,
                             .depth = 16,
                             .full_name = "abgr1555",
                             .short_name = "abgr1555",
                             .alias = NULL,
                             },

        [PIXFMT_RGBA4444] =
            {
                             .fmt_id = PIXFMT_RGBA4444,

                             .base_type = PIXFMT_TYPE_RGB,
                             .desc = &g_rgb_desc_rgba4444,
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_BITPACKED_LSB,
                             .bpp = 16,
                             .depth = 16,
                             .full_name = "rgba4444",
                             .short_name = "rgba4444",
                             .alias = NULL,
                             },

        [PIXFMT_ABGR4444] =
            {
                             .fmt_id = PIXFMT_ABGR4444,

                             .base_type = PIXFMT_TYPE_RGB,
                             .desc = &g_rgb_desc_abgr4444,
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_BITPACKED_LSB,
                             .bpp = 16,
                             .depth = 16,
                             .full_name = "abgr4444",
                             .short_name = "abgr4444",
                             .alias = NULL,
                             },

        [PIXFMT_RGBA1010102] =
            {
                             .fmt_id = PIXFMT_RGBA1010102,

                             .base_type = PIXFMT_TYPE_RGB,
                             .desc = &g_rgb_desc_rgba1010102,
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_BITPACKED_LSB,
                             .bpp = 32,
                             .depth = 32,
                             .full_name = "rgba1010102",
                             .short_name = "rgba1010102",
                             .alias = NULL,
                             },

        [PIXFMT_ABGR2101010] =
            {
                             .fmt_id = PIXFMT_ABGR2101010,

                             .base_type = PIXFMT_TYPE_RGB,
                             .desc = &g_rgb_desc_abgr2101010,
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_BITPACKED_LSB,
                             .bpp = 32,
                             .depth = 32,
                             .full_name = "abgr2101010",
                             .short_name = "abgr2101010",
                             .alias = NULL,
                             },

        /* YUV Raster format */
        [PIXFMT_YUV444I_VU24] =
            {
                             .fmt_id = PIXFMT_YUV444I_VU24,

                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv444i_vu24},
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             .bpp = 24,
                             .depth = 8,
                             .full_name = "yuv444i_vu24",
                             .short_name = "yuv444i_vu24",
                             .alias = NULL,
                             },

        [PIXFMT_YUV444P_YU24] =
            {
                             .fmt_id = PIXFMT_YUV444P_YU24,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv444p_yu24},
                             .layout = PIXFMT_LAYOUT_PLANAR,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             .bpp = 24,
                             .depth = 8,
                             .full_name = "yuv444p_yu24",
                             .short_name = "yuv444p_yu24",
                             .alias = NULL,
                             },

        [PIXFMT_YUV444SP_NV24] =
            {
                             .fmt_id = PIXFMT_YUV444SP_NV24,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv444sp_nv24},
                             .layout = PIXFMT_LAYOUT_SEMIPLANAR,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             .bpp = 24,
                             .depth = 8,
                             .full_name = "yuv444sp_nv24",
                             .short_name = "yuv444sp_nv24",
                             .alias = NULL,
                             },

        [PIXFMT_YUV444SP_NV42] =
            {
                             .fmt_id = PIXFMT_YUV444SP_NV42,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv444sp_nv42},
                             .layout = PIXFMT_LAYOUT_SEMIPLANAR,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             .bpp = 24,
                             .depth = 8,
                             .full_name = "yuv444sp_nv42",
                             .short_name = "yuv444sp_nv42",
                             .alias = NULL,
                             },

        [PIXFMT_YUV422I_YUYV] =
            {
                             .fmt_id = PIXFMT_YUV422I_YUYV,

                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv422i_yuyv},
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             .bpp = 16,
                             .depth = 8,
                             .full_name = "yuv422i_yuyv",
                             .short_name = "yuyv",
                             .alias = "yuv422i",
                             },

        [PIXFMT_YUV422SP_NV16] =
            {
                             .fmt_id = PIXFMT_YUV422SP_NV16,

                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv422sp_nv16},
                             .layout = PIXFMT_LAYOUT_SEMIPLANAR,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             .bpp = 16,
                             .depth = 8,
                             .full_name = "yuv422sp_nv16",
                             .short_name = "nv16",
                             .alias = "yuv422sp",
                             },

        [PIXFMT_YUV420P_YU12] =
            {
                             .fmt_id = PIXFMT_YUV420P_YU12,

                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv420p_yu12},
                             .layout = PIXFMT_LAYOUT_PLANAR,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             .bpp = 12,
                             .depth = 8,
                             .full_name = "yuv420p_yu12",
                             .short_name = "yu12",
                             .alias = "yuv420p",
                             },

        [PIXFMT_YUV420P_YV12] =
            {
                             .fmt_id = PIXFMT_YUV420P_YV12,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv420p_yv12},
                             .layout = PIXFMT_LAYOUT_PLANAR,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             .bpp = 12,
                             .depth = 8,
                             .full_name = "yuv420p_yv12",
                             .short_name = "yv12",
                             .alias = NULL,
                             },

        [PIXFMT_YUV420SP_NV12] =
            {
                             .fmt_id = PIXFMT_YUV420SP_NV12,

                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv420sp_nv12},
                             .layout = PIXFMT_LAYOUT_SEMIPLANAR,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             .bpp = 12,
                             .depth = 8,
                             .full_name = "yuv420sp_nv12",
                             .short_name = "nv12",
                             .alias = "yuv420sp",
                             },

        /* YUV Tile format */
        [PIXFMT_YUV420SP_TILE4X4] =
            {
                             .fmt_id = PIXFMT_YUV420SP_TILE4X4,

                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv420sp_tile4x4},
                             .layout = PIXFMT_LAYOUT_TILE,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             .bpp = 12,
                             .depth = 8,
                             .full_name = "yuv420sp_tile4x4",
                             .short_name = "yuv420sp_tile4x4",
                             .alias = NULL,
                             },

        /* YUV Raster format - 10bit */
        [PIXFMT_YUV444I_VU30] =
            {
                             .fmt_id = PIXFMT_YUV444I_VU30,

                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv444i_vu30},
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_BITPACKED_LSB,
                             .bpp = 30,
                             .depth = 10,
                             .full_name = "yuv444i_vu30",
                             .short_name = "yuv444i_vu30",
                             .alias = NULL,
                             },

        [PIXFMT_YUV444I_XV30] =
            {
                             .fmt_id = PIXFMT_YUV444I_XV30,

                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv444i_xv30},
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .padding_pos = PIXFMT_PADDING_ON_MSB,
                             .bitpacked_order = PIXFMT_BITPACKED_LSB,
                             .bpp = 32,
                             .depth = 10,
                             .full_name = "yuv444i_xv30",
                             .short_name = "yuv444i_xv30",
                             .alias = NULL,
                             },

        [PIXFMT_YUV444P_YV24] =
            {
                             .fmt_id = PIXFMT_YUV444P_YV24,

                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv444p_yv24},
                             .layout = PIXFMT_LAYOUT_PLANAR,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             .bpp = 24,
                             .depth = 8,
                             .full_name = "yuv444p_yv24",
                             .short_name = "yuv444p_yv24",
                             .alias = NULL,
                             },

        [PIXFMT_YUV444SP_NV30] =
            {
                             .fmt_id = PIXFMT_YUV444SP_NV30,

                             .full_name = "YUV444 Semi-Planar NV30",
                             .short_name = "nv30",
                             .alias = NULL,
                             .bpp = 30,
                             .depth = 10,
                             .layout = PIXFMT_LAYOUT_SEMIPLANAR,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv444sp_nv30},
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             },

        [PIXFMT_YUV422I_YVYU] =
            {
                             .fmt_id = PIXFMT_YUV422I_YVYU,

                             .full_name = "YUV422 Interleaved YVYU",
                             .short_name = "yvyu",
                             .alias = NULL,
                             .bpp = 16,
                             .depth = 8,
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv422i_yvyu},
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             },

        [PIXFMT_YUV422I_UYVY] =
            {
                             .fmt_id = PIXFMT_YUV422I_UYVY,

                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv422i_uyvy},
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             .bpp = 16,
                             .depth = 8,
                             .full_name = "yuv422i_uyvy",
                             .short_name = "uyvy",
                             .alias = NULL,
                             },

        [PIXFMT_YUV422I_VYUY] =
            {
                             .fmt_id = PIXFMT_YUV422I_VYUY,

                             .full_name = "YUV422 Interleaved VYUY",
                             .short_name = "vyuy",
                             .alias = NULL,
                             .bpp = 16,
                             .depth = 8,
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv422i_vyuy},
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             },

        [PIXFMT_YUV422I_Y210] =
            {
                             .fmt_id = PIXFMT_YUV422I_Y210,

                             .full_name = "YUV422 Interleaved Y210",
                             .short_name = "y210",
                             .alias = NULL,
                             .bpp = 32,
                             .depth = 10,
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv422i_y210},
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             },

        [PIXFMT_YUV422I_Y212] =
            {
                             .fmt_id = PIXFMT_YUV422I_Y212,

                             .full_name = "YUV422 Interleaved Y212",
                             .short_name = "y212",
                             .alias = NULL,
                             .bpp = 32,
                             .depth = 12,
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv422i_y210},
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             },

        [PIXFMT_YUV422I_Y216] =
            {
                             .fmt_id = PIXFMT_YUV422I_Y216,

                             .full_name = "YUV422 Interleaved Y216",
                             .short_name = "y216",
                             .alias = NULL,
                             .bpp = 32,
                             .depth = 16,
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv422i_y210},
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             },

        [PIXFMT_YUV422P_YU16] =
            {
                             .fmt_id = PIXFMT_YUV422P_YU16,

                             .full_name = "YUV422 Planar YU16",
                             .short_name = "yu16",
                             .alias = NULL,
                             .bpp = 16,
                             .depth = 8,
                             .layout = PIXFMT_LAYOUT_PLANAR,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv422p_yu16},
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             },

        [PIXFMT_YUV422P_YV16] =
            {
                             .fmt_id = PIXFMT_YUV422P_YV16,

                             .full_name = "YUV422 Planar YV16",
                             .short_name = "yv16",
                             .alias = NULL,
                             .bpp = 16,
                             .depth = 8,
                             .layout = PIXFMT_LAYOUT_PLANAR,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv422p_yv16},
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             },

        [PIXFMT_YUV422SP_NV61] =
            {
                             .fmt_id = PIXFMT_YUV422SP_NV61,

                             .full_name = "YUV422 Semi-Planar NV61",
                             .short_name = "nv61",
                             .alias = NULL,
                             .bpp = 16,
                             .depth = 8,
                             .layout = PIXFMT_LAYOUT_SEMIPLANAR,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv422sp_nv61},
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             },

        [PIXFMT_YUV422SP_NV20] =
            {
                             .fmt_id = PIXFMT_YUV422SP_NV20,

                             .full_name = "YUV422 Semi-Planar NV20",
                             .short_name = "nv20",
                             .alias = NULL,
                             .bpp = 20,
                             .depth = 10,
                             .layout = PIXFMT_LAYOUT_SEMIPLANAR,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv422sp_nv20},
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             },

        [PIXFMT_YUV420SP_NV21] =
            {
                             .fmt_id = PIXFMT_YUV420SP_NV21,

                             .full_name = "YUV420 Semi-Planar NV21",
                             .short_name = "nv21",
                             .alias = NULL,
                             .bpp = 12,
                             .depth = 8,
                             .layout = PIXFMT_LAYOUT_SEMIPLANAR,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv420sp_nv21},
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             },

        [PIXFMT_YUV420SP_NV15] =
            {
                             .fmt_id = PIXFMT_YUV420SP_NV15,

                             .full_name = "YUV420 Semi-Planar NV15",
                             .short_name = "nv15",
                             .alias = NULL,
                             .bpp = 15,
                             .depth = 10,
                             .layout = PIXFMT_LAYOUT_SEMIPLANAR,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv420sp_nv15},
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             },

        [PIXFMT_YUV411P_YU11] =
            {
                             .fmt_id = PIXFMT_YUV411P_YU11,

                             .full_name = "YUV411 Planar YU11",
                             .short_name = "yu11",
                             .alias = NULL,
                             .bpp = 12,
                             .depth = 8,
                             .layout = PIXFMT_LAYOUT_PLANAR,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv411p_yu11},
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             },

        [PIXFMT_YUV411P_YV11] =
            {
                             .fmt_id = PIXFMT_YUV411P_YV11,

                             .full_name = "YUV411 Planar YV11",
                             .short_name = "yv11",
                             .alias = NULL,
                             .bpp = 12,
                             .depth = 8,
                             .layout = PIXFMT_LAYOUT_PLANAR,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv411p_yv11},
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             },

        [PIXFMT_YUV410P_YUV9] =
            {
                             .fmt_id = PIXFMT_YUV410P_YUV9,

                             .full_name = "YUV410 Planar YUV9",
                             .short_name = "yuv9",
                             .alias = NULL,
                             .bpp = 9,
                             .depth = 8,
                             .layout = PIXFMT_LAYOUT_PLANAR,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv410p_yuv9},
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             },

        [PIXFMT_YUV410P_YVU9] =
            {
                             .fmt_id = PIXFMT_YUV410P_YVU9,

                             .full_name = "YUV410 Planar YVU9",
                             .short_name = "yvu9",
                             .alias = NULL,
                             .bpp = 9,
                             .depth = 8,
                             .layout = PIXFMT_LAYOUT_PLANAR,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv410p_yvu9},
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             },

        /* YUV Tile format */
        [PIXFMT_YUV444SP_TILE4X4] =
            {
                             .fmt_id = PIXFMT_YUV444SP_TILE4X4,

                             .full_name = "YUV444 Semi-Planar Tile 4x4",
                             .short_name = "yuv444sp_tile4x4",
                             .alias = NULL,
                             .bpp = 24,
                             .depth = 8,
                             .layout = PIXFMT_LAYOUT_TILE,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv444sp_tile4x4},
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             },

        [PIXFMT_YUV422SP_TILE4x4] =
            {
                             .fmt_id = PIXFMT_YUV422SP_TILE4x4,

                             .full_name = "YUV422 Semi-Planar Tile 4x4",
                             .short_name = "yuv422sp_tile4x4",
                             .alias = NULL,
                             .bpp = 16,
                             .depth = 8,
                             .layout = PIXFMT_LAYOUT_TILE,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv422sp_tile4x4},
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             },

        /* YUV400 format */
        [PIXFMT_YUV400_R1] =
            {
                             .fmt_id = PIXFMT_YUV400_R1,

                             .full_name = "YUV400 R1",
                             .short_name = "yuv400_r1",
                             .alias = NULL,
                             .bpp = 1,
                             .depth = 1,
                             .layout = PIXFMT_LAYOUT_PLANAR,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv400_r1},
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             },
        [PIXFMT_YUV400_R2] =
            {
                             .fmt_id = PIXFMT_YUV400_R2,

                             .full_name = "YUV400 R2",
                             .short_name = "yuv400_r2",
                             .alias = NULL,
                             .bpp = 2,
                             .depth = 2,
                             .layout = PIXFMT_LAYOUT_PLANAR,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv400_r2},
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             },
        [PIXFMT_YUV400_R4] =
            {
                             .fmt_id = PIXFMT_YUV400_R4,

                             .full_name = "YUV400 R4",
                             .short_name = "yuv400_r4",
                             .alias = NULL,
                             .bpp = 4,
                             .depth = 4,
                             .layout = PIXFMT_LAYOUT_PLANAR,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv400_r4},
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             },
        [PIXFMT_YUV400_R8] =
            {
                             .fmt_id = PIXFMT_YUV400_R8,

                             .full_name = "YUV400 R8",
                             .short_name = "yuv400_r8",
                             .alias = NULL,
                             .bpp = 8,
                             .depth = 8,
                             .layout = PIXFMT_LAYOUT_PLANAR,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv400_r8},
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             },
        [PIXFMT_YUV400_R10] =
            {
                             .fmt_id = PIXFMT_YUV400_R10,

                             .full_name = "YUV400 R10",
                             .short_name = "yuv400_r10",
                             .alias = NULL,
                             .bpp = 10,
                             .depth = 10,
                             .layout = PIXFMT_LAYOUT_PLANAR,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv400_r10},
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             },
        [PIXFMT_YUV400_R12] =
            {
                             .fmt_id = PIXFMT_YUV400_R12,

                             .full_name = "YUV400 R12",
                             .short_name = "yuv400_r12",
                             .alias = NULL,
                             .bpp = 12,
                             .depth = 12,
                             .layout = PIXFMT_LAYOUT_PLANAR,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv400_r12},
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             },
        [PIXFMT_YUV400_R16] =
            {
                             .fmt_id = PIXFMT_YUV400_R16,

                             .full_name = "YUV400 R16",
                             .short_name = "yuv400_r16",
                             .alias = NULL,
                             .bpp = 16,
                             .depth = 16,
                             .layout = PIXFMT_LAYOUT_PLANAR,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv400_r16},
                             .padding_pos = PIXFMT_NO_PADDING,
                             .bitpacked_order = PIXFMT_UNPACKED,
                             },
};

#define PIXFMT_ATTR_TABLE_SIZE (sizeof(g_pixfmt_attr_table) / sizeof(pixfmt_attr_s))

const pixfmt_attr_s *pixfmt_get_attr(pixfmt_e fmt)
{
    if (fmt >= 0 && fmt < PIXFMT_MAX) {
        return &g_pixfmt_attr_table[fmt];
    }
    LOGE("pixfmt_get_attr: no attr found! invalid fmt %d", fmt);
    return NULL;
}

const pixfmt_attr_s *pixfmt_get_attr_by_name(const char *name)
{
    for (int i = 0; i < PIXFMT_ATTR_TABLE_SIZE; i++) {
        if (g_pixfmt_attr_table[i].full_name && strcmp(g_pixfmt_attr_table[i].full_name, name) == 0) {
            return &g_pixfmt_attr_table[i];
        }
        if (g_pixfmt_attr_table[i].short_name && strcmp(g_pixfmt_attr_table[i].short_name, name) == 0) {
            return &g_pixfmt_attr_table[i];
        }
        if (g_pixfmt_attr_table[i].alias && strcmp(g_pixfmt_attr_table[i].alias, name) == 0) {
            return &g_pixfmt_attr_table[i];
        }
    }
    LOGE("pixfmt_get_attr_by_name: name %s not found!", name);
    return NULL;
}

const char *pixfmt_full_name(pixfmt_e fmt)
{
    const pixfmt_attr_s *desc = pixfmt_get_attr(fmt);
    return desc ? desc->full_name : "InvalidFmt";
}

const char *pixfmt_short_name(pixfmt_e fmt)
{
    const pixfmt_attr_s *desc = pixfmt_get_attr(fmt);
    return desc ? desc->short_name : "InvalidFmt";
}

const char *pixfmt_alias(pixfmt_e fmt)
{
    const pixfmt_attr_s *desc = pixfmt_get_attr(fmt);
    return desc ? desc->alias : "InvalidFmt";
}

int pixfmt_bpp(pixfmt_e fmt)
{
    const pixfmt_attr_s *desc = pixfmt_get_attr(fmt);
    return desc ? desc->bpp : 0;
}

int pixfmt_depth(pixfmt_e fmt)
{
    const pixfmt_attr_s *desc = pixfmt_get_attr(fmt);
    return desc ? desc->depth : 0;
}

int pixfmt_nb_comps(pixfmt_e fmt)
{
    const pixfmt_attr_s *desc = pixfmt_get_attr(fmt);
    return desc ? desc->nb_comps : 0;
}

int pixfmt_nb_planes(pixfmt_e fmt)
{
    const pixfmt_attr_s *desc = pixfmt_get_attr(fmt);
    if (!desc)
        return 0;

    switch (desc->layout) {
    case PIXFMT_LAYOUT_PLANAR:      return desc->nb_comps;
    case PIXFMT_LAYOUT_SEMIPLANAR:  return 2;
    case PIXFMT_LAYOUT_INTERLEAVED:
    case PIXFMT_LAYOUT_TILE:
    case PIXFMT_LAYOUT_IRREGULAR:   return 1;
    default:                        return 0;
    }
}

int pixfmt_get_min_align_width(pixfmt_e fmt, int wid, int *retAlign)
{
    const pixfmt_attr_s *attr = pixfmt_get_attr(fmt);
    assert(attr != NULL);

    if (attr->base_type == PIXFMT_TYPE_RGB)
        return pixfmt_rgb_get_min_align_width(attr, wid, retAlign);
    if (attr->base_type == PIXFMT_TYPE_YUV)
        return pixfmt_yuv_get_min_align_width(attr, wid, retAlign);

    return PIXFMT_INVALID;
}

int pixfmt_get_min_align_height(pixfmt_e fmt, int hgt, int *retAlign)
{
    const pixfmt_attr_s *attr = pixfmt_get_attr(fmt);
    assert(attr != NULL);

    if (attr->base_type == PIXFMT_TYPE_RGB)
        return hgt;
    if (attr->base_type == PIXFMT_TYPE_YUV)
        return pixfmt_yuv_get_min_align_height(attr, hgt, retAlign);

    return PIXFMT_INVALID;
}

int pixfmt_get_min_pitches(pixfmt_e fmt, int wid, int *retPitchesx3)
{
    const pixfmt_attr_s *attr = pixfmt_get_attr(fmt);
    assert(attr != NULL);

    if (attr->base_type == PIXFMT_TYPE_RGB)
        return pixfmt_rgb_get_min_pitches(attr, wid, retPitchesx3);
    if (attr->base_type == PIXFMT_TYPE_YUV)
        return pixfmt_yuv_get_min_pitches(attr, wid, retPitchesx3);

    return PIXFMT_INVALID;
}

size_t pixfmt_get_frame_size(pixfmt_e fmt, int wid, int hgt, int rowpitch)
{
    const pixfmt_attr_s *attr = pixfmt_get_attr(fmt);
    assert(attr != NULL);

    if (attr->base_type == PIXFMT_TYPE_RGB)
        return pixfmt_rgb_get_framesize(attr, wid, hgt, rowpitch);
    if (attr->base_type == PIXFMT_TYPE_YUV)
        return pixfmt_yuv_get_framesize(attr, wid, hgt, rowpitch);

    return 0;
}

bool pixfmt_is_yuv(pixfmt_e fmt)
{
    const pixfmt_attr_s *desc = pixfmt_get_attr(fmt);
    return desc ? desc->base_type == PIXFMT_TYPE_YUV : false;
}

bool pixfmt_is_rgb(pixfmt_e fmt)
{
    const pixfmt_attr_s *desc = pixfmt_get_attr(fmt);
    return desc ? desc->base_type == PIXFMT_TYPE_RGB : false;
}

bool pixfmt_is_uv_order(pixfmt_e fmt)
{
    const pixfmt_attr_s *desc = pixfmt_get_attr(fmt);
    if (!desc || desc->base_type != PIXFMT_TYPE_YUV)
        return false;
    return pixfmt_yuv_desc_is_uv_order(desc->desc.yuv);
}

bool pixfmt_is_tile(pixfmt_e fmt)
{
    const pixfmt_attr_s *desc = pixfmt_get_attr(fmt);
    if (!desc || desc->base_type != PIXFMT_TYPE_YUV)
        return false;
    return pixfmt_yuv_desc_is_tile(desc->desc.yuv);
}

bool pixfmt_is_bgr_order(pixfmt_e fmt)
{
    const pixfmt_attr_s *desc = pixfmt_get_attr(fmt);
    if (!desc || desc->base_type != PIXFMT_TYPE_RGB)
        return false;
    return pixfmt_rgb_desc_is_bgr_order(desc->desc.rgb);
}

bool pixfmt_has_alpha(pixfmt_e fmt)
{
    const pixfmt_attr_s *desc = pixfmt_get_attr(fmt);
    if (!desc || desc->base_type != PIXFMT_TYPE_RGB)
        return false;
    return pixfmt_rgb_desc_has_alpha(desc->desc.rgb);
}

int pixfmt_get_channel_bits(pixfmt_e fmt, uint8_t *r, uint8_t *g, uint8_t *b, uint8_t *a)
{
    const pixfmt_attr_s *desc = pixfmt_get_attr(fmt);
    if (!desc || desc->base_type != PIXFMT_TYPE_RGB)
        return 0;
    return pixfmt_rgb_desc_get_channel_bits(desc->desc.rgb, r, g, b, a);
}

int pixfmt_get_tile_size(pixfmt_e fmt, int *tile_w, int *tile_h)
{
    const pixfmt_attr_s *desc = pixfmt_get_attr(fmt);
    if (!desc || desc->base_type != PIXFMT_TYPE_YUV)
        return -1;
    return pixfmt_yuv_desc_get_tile_size(desc->desc.yuv, tile_w, tile_h);
}

int pixfmt_get_chroma_subsampling(pixfmt_e fmt, int *h_sub, int *v_sub)
{
    const pixfmt_attr_s *desc = pixfmt_get_attr(fmt);
    if (!desc || desc->base_type != PIXFMT_TYPE_YUV)
        return -1;
    return pixfmt_yuv_desc_get_chroma_subsampling(desc->desc.yuv, h_sub, v_sub);
}

bool pixfmt_can_input(pixfmt_e fmt)
{
    const pixfmt_attr_s *desc = pixfmt_get_attr(fmt);
    return desc != NULL;
}

bool pixfmt_can_output(pixfmt_e fmt)
{
    const pixfmt_attr_s *desc = pixfmt_get_attr(fmt);
    return desc != NULL;
}

pixfmt_e pixfmt_get_canonical(pixfmt_e fmt) { return fmt; }


pixfmt_e *pixfmt_get_supported_input_fmts(int *count)
{
    *count = PIXFMT_ATTR_TABLE_SIZE;
    pixfmt_e *fmts = malloc(sizeof(pixfmt_e) * PIXFMT_ATTR_TABLE_SIZE);
    if (fmts) {
        for (int i = 0; i < PIXFMT_ATTR_TABLE_SIZE; i++) {
            fmts[i] = g_pixfmt_attr_table[i].fmt_id;
        }
    }
    return fmts;
}

pixfmt_e *pixfmt_get_supported_output_fmts(int *count)
{
    *count = PIXFMT_ATTR_TABLE_SIZE;
    pixfmt_e *fmts = malloc(sizeof(pixfmt_e) * PIXFMT_ATTR_TABLE_SIZE);
    if (fmts) {
        for (int i = 0; i < PIXFMT_ATTR_TABLE_SIZE; i++) {
            fmts[i] = g_pixfmt_attr_table[i].fmt_id;
        }
    }
    return fmts;
}
