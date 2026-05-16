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
const pixfmt_attr_s g_pixfmt_attr_table[PIXFMT_NB_COUNT] =
    {
        /* RGB format - 8bit */
        [PIXFMT_RGB888] =
            {
                             .fmt_id = PIXFMT_RGB888,
                             .base_type = PIXFMT_TYPE_RGB,
                             .desc = &g_rgb_desc_rgb888,
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .is_bitpacked = false,
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
                             .is_bitpacked = false,
                             .bpp = 24,
                             .depth = 8,
                             .nb_comps = 3,
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
                             .is_bitpacked = false,
                             .bpp = 32,
                             .depth = 8,
                             .nb_comps = 4,
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
                             .is_bitpacked = false,
                             .bpp = 32,
                             .depth = 8,
                             .nb_comps = 4,
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
                             .is_bitpacked = false,
                             .bpp = 32,
                             .depth = 8,
                             .nb_comps = 4,
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
                             .is_bitpacked = false,
                             .bpp = 32,
                             .depth = 8,
                             .nb_comps = 4,
                             .full_name = "abgr8888",
                             .short_name = "abgr32",
                             .alias = "abgr",
                             },

        [PIXFMT_RGB10Lsb] =
            {
                             .fmt_id = PIXFMT_RGB10Lsb,
                             .base_type = PIXFMT_TYPE_RGB,
                             .desc = &g_rgb_desc_rgb10lsb,
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .padding_pos = PIXFMT_PADDING_AT_MSB,
                             .is_bitpacked = false,
                             .bpp = 48,
                             .depth = 10,
                             .nb_comps = 3,
                             .full_name = "rgb10l",
                             .short_name = "rgb10l",
                             .alias = NULL,
                             },

        [PIXFMT_RGBA10Lsb] =
            {
                             .fmt_id = PIXFMT_RGBA10Lsb,

                             .base_type = PIXFMT_TYPE_RGB,
                             .desc = &g_rgb_desc_rgba10lsb,
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .padding_pos = PIXFMT_PADDING_AT_MSB,
                             .is_bitpacked = false,
                             .bpp = 64,
                             .depth = 10,
                             .nb_comps = 4,
                             .full_name = "rgba10l",
                             .short_name = "rgba10l",
                             .alias = NULL,
                             },

        /* RGB bit-packed format */
        [PIXFMT_RGB332] =
            {
                             .fmt_id = PIXFMT_RGB332,
                             .base_type = PIXFMT_TYPE_RGB,
                             .desc = &g_rgb_desc_rgb332,
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .is_bitpacked = true,
                             .bpp = 8,
                             .depth = 3,
                             .nb_comps = 3,
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
                             .is_bitpacked = true,
                             .bpp = 8,
                             .depth = 3,
                             .nb_comps = 3,
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
                             .is_bitpacked = true,
                             .bpp = 16,
                             .depth = 6,
                             .nb_comps = 3,
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
                             .is_bitpacked = true,
                             .bpp = 16,
                             .depth = 6,
                             .nb_comps = 3,
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
                             .is_bitpacked = true,
                             .bpp = 16,
                             .depth = 5,
                             .nb_comps = 4,
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
                             .is_bitpacked = true,
                             .bpp = 16,
                             .depth = 5,
                             .nb_comps = 4,
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
                             .is_bitpacked = true,
                             .bpp = 16,
                             .depth = 4,
                             .nb_comps = 4,
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
                             .is_bitpacked = true,
                             .bpp = 16,
                             .depth = 4,
                             .nb_comps = 4,
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
                             .is_bitpacked = true,
                             .bpp = 32,
                             .depth = 10,
                             .nb_comps = 4,
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
                             .is_bitpacked = true,
                             .bpp = 32,
                             .depth = 10,
                             .nb_comps = 4,
                             .full_name = "abgr2101010",
                             .short_name = "abgr2101010",
                             .alias = NULL,
                             },


        /* YUV Raster format */
        [PIXFMT_YUV444I_VU24] =
            {
                             .fmt_id = PIXFMT_YUV444I_VU24,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv444_yuv},
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .is_bitpacked = false,
                             .bpp = 24,
                             .depth = 8,
                             .nb_comps = 3,
                             .full_name = "yuv444i8",
                             .short_name = "vu24",
                             .alias = "yuv444i_vu24",
                             },
        [PIXFMT_YUV444I_VU30] =
            {
                             .fmt_id = PIXFMT_YUV444I_VU30,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv444_yuv},
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .is_bitpacked = true,
                             .bpp = 30,
                             .depth = 10,
                             .nb_comps = 3,
                             .full_name = "yuv444i10bp",
                             .short_name = "vu30",
                             .alias = "yuv444i_vu30",
                             },

        [PIXFMT_YUV444I_XV30] =
            {
                             .fmt_id = PIXFMT_YUV444I_XV30,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv444_uyv},
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .padding_pos = PIXFMT_PADDING_AT_MSB,
                             .is_bitpacked = true,
                             .bpp = 32,
                             .depth = 10,
                             .nb_comps = 3,
                             .full_name = "uyv444i10bpl",
                             .short_name = "xv30",
                             .alias = "yuv444i_xv30",
                             },
        [PIXFMT_YUV444I_10LSB] =
            {
                             .fmt_id = PIXFMT_YUV444I_10LSB,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv444_yuv},
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .padding_pos = PIXFMT_PADDING_AT_MSB,
                             .is_bitpacked = false,
                             .bpp = 48,
                             .depth = 10,
                             .nb_comps = 3,
                             .full_name = "yuv444i10l",
                             .short_name = "yuv444i10l",
                             .alias = "yuv444i_10lsb",
                             },
        [PIXFMT_YUV444P_YU24] =
            {
                             .fmt_id = PIXFMT_YUV444P_YU24,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv444_yuv},
                             .layout = PIXFMT_LAYOUT_PLANAR,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .is_bitpacked = false,
                             .bpp = 24,
                             .depth = 8,
                             .nb_comps = 3,
                             .full_name = "yuv444p8",
                             .short_name = "yu24",
                             .alias = "yuv444p_yu24",
                             },
        [PIXFMT_YUV444P_YV24] =
            {
                             .fmt_id = PIXFMT_YUV444P_YV24,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv444_yvu},
                             .layout = PIXFMT_LAYOUT_PLANAR,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .is_bitpacked = false,
                             .bpp = 24,
                             .depth = 8,
                             .nb_comps = 3,
                             .full_name = "yvu444p8",
                             .short_name = "yv24",
                             .alias = "yuv444p_yv24",
                             },

        [PIXFMT_YUV444P_10LSB] =
            {
                             .fmt_id = PIXFMT_YUV444P_10LSB,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv444_yuv},
                             .layout = PIXFMT_LAYOUT_PLANAR,
                             .padding_pos = PIXFMT_PADDING_AT_MSB,
                             .is_bitpacked = false,
                             .bpp = 48,
                             .depth = 10,
                             .nb_comps = 3,
                             .full_name = "yuv444p10l",
                             .short_name = "yuv444p10l",
                             .alias = "yuv444p_10lsb",
                             },

        [PIXFMT_YUV444SP_NV24] =
            {
                             .fmt_id = PIXFMT_YUV444SP_NV24,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv444_yuv},
                             .layout = PIXFMT_LAYOUT_SEMIPLANAR,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .is_bitpacked = false,
                             .bpp = 24,
                             .depth = 8,
                             .nb_comps = 3,
                             .full_name = "yuv444sp8",
                             .short_name = "nv24",
                             .alias = "yuv444sp_nv24",
                             },

        [PIXFMT_YUV444SP_NV42] =
            {
                             .fmt_id = PIXFMT_YUV444SP_NV42,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv444_yvu},
                             .layout = PIXFMT_LAYOUT_SEMIPLANAR,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .is_bitpacked = false,
                             .bpp = 24,
                             .depth = 8,
                             .nb_comps = 3,
                             .full_name = "yvu444sp8",
                             .short_name = "nv42",
                             .alias = "yuv444sp_nv42",
                             },

        [PIXFMT_YUV444SP_NV30] =
            {
                             .fmt_id = PIXFMT_YUV444SP_NV30,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv444_yuv},
                             .layout = PIXFMT_LAYOUT_SEMIPLANAR,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .is_bitpacked = true,
                             .bpp = 30,
                             .depth = 10,
                             .nb_comps = 3,
                             .full_name = "yuv444sp10bp",
                             .short_name = "nv30",
                             .alias = "yuv444sp_nv30",
                             },

        [PIXFMT_YUV444SP_10LSB] =
            {
                             .fmt_id = PIXFMT_YUV444SP_10LSB,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv444_yuv},
                             .layout = PIXFMT_LAYOUT_SEMIPLANAR,
                             .padding_pos = PIXFMT_PADDING_AT_MSB,
                             .is_bitpacked = false,
                             .bpp = 48,
                             .depth = 10,
                             .nb_comps = 3,
                             .full_name = "yuv444sp10l",
                             .short_name = "yuv444sp10l",
                             .alias = "yuv444sp_10lsb",
                             },

        [PIXFMT_YUV422I_YUYV] =
            {
                             .fmt_id = PIXFMT_YUV422I_YUYV,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv422_yuyv},
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .is_bitpacked = false,
                             .bpp = 16,
                             .depth = 8,
                             .nb_comps = 3,
                             .full_name = "yuyv422i8",
                             .short_name = "yuyv",
                             .alias = "yuv422i_yuyv",
                             },
        [PIXFMT_YUV422I_YVYU] =
            {
                             .fmt_id = PIXFMT_YUV422I_YVYU,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv422_yvyu},
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .is_bitpacked = false,
                             .bpp = 16,
                             .depth = 8,
                             .nb_comps = 3,
                             .full_name = "yvyu422i8",
                             .short_name = "yvyu",
                             .alias = "yuv422i_yvyu",
                             },

        [PIXFMT_YUV422I_UYVY] =
            {
                             .fmt_id = PIXFMT_YUV422I_UYVY,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv422_uyvy},
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .is_bitpacked = false,
                             .bpp = 16,
                             .depth = 8,
                             .nb_comps = 3,
                             .full_name = "uyvy422i8",
                             .short_name = "uyvy",
                             .alias = "yuv422i_uyvy",
                             },

        [PIXFMT_YUV422I_VYUY] =
            {
                             .fmt_id = PIXFMT_YUV422I_VYUY,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv422_vyuy},
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .is_bitpacked = false,
                             .bpp = 16,
                             .depth = 8,
                             .nb_comps = 3,
                             .full_name = "vyuy422i8",
                             .short_name = "vyuy",
                             .alias = "yuv422i_vyuy",
                             },

        [PIXFMT_YUV422I_Y210] =
            {
                             .fmt_id = PIXFMT_YUV422I_Y210,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv422_yuyv},
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .padding_pos = PIXFMT_PADDING_AT_LSB,
                             .is_bitpacked = false,
                             .bpp = 32,
                             .depth = 10,
                             .nb_comps = 3,
                             .full_name = "yuyv422i10m",
                             .short_name = "y210",
                             .alias = "yuv422i_y210",
                             },

        [PIXFMT_YUV422I_Y212] =
            {
                             .fmt_id = PIXFMT_YUV422I_Y212,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv422_yuyv},
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .padding_pos = PIXFMT_PADDING_AT_LSB,
                             .is_bitpacked = false,
                             .bpp = 32,
                             .depth = 12,
                             .nb_comps = 3,
                             .full_name = "yuyv422i12m",
                             .short_name = "y212",
                             .alias = "yuv422i_y212",
                             },

        [PIXFMT_YUV422I_Y216] =
            {
                             .fmt_id = PIXFMT_YUV422I_Y216,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv422_yuyv},
                             .layout = PIXFMT_LAYOUT_INTERLEAVED,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .is_bitpacked = false,
                             .bpp = 32,
                             .depth = 16,
                             .nb_comps = 3,
                             .full_name = "yuyv422i16",
                             .short_name = "y216",
                             .alias = "yuv422i_y216",
                             },

        [PIXFMT_YUV422P_YU16] =
            {
                             .fmt_id = PIXFMT_YUV422P_YU16,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv422_yuv},
                             .layout = PIXFMT_LAYOUT_PLANAR,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .is_bitpacked = false,
                             .bpp = 16,
                             .depth = 8,
                             .nb_comps = 3,
                             .full_name = "yuv422p8",
                             .short_name = "yu16",
                             .alias = "yuv422p_yu16",
                             },

        [PIXFMT_YUV422P_YV16] =
            {
                             .fmt_id = PIXFMT_YUV422P_YV16,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv422_yvu},
                             .layout = PIXFMT_LAYOUT_PLANAR,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .is_bitpacked = false,
                             .bpp = 16,
                             .depth = 8,
                             .nb_comps = 3,
                             .full_name = "yvu422p8",
                             .short_name = "yv16",
                             .alias = "yuv422p_yv16",
                             },

        [PIXFMT_YUV422P_10LSB] =
            {
                             .fmt_id = PIXFMT_YUV422P_10LSB,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv422_yuv},
                             .layout = PIXFMT_LAYOUT_PLANAR,
                             .padding_pos = PIXFMT_PADDING_AT_MSB,
                             .is_bitpacked = false,
                             .bpp = 32,
                             .depth = 10,
                             .nb_comps = 3,
                             .full_name = "yuv422p10l",
                             .short_name = "yuv422p10l",
                             .alias = "yuv422p_10lsb",
                             },

        [PIXFMT_YUV422SP_NV16] =
            {
                             .fmt_id = PIXFMT_YUV422SP_NV16,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv422_yuv},
                             .layout = PIXFMT_LAYOUT_SEMIPLANAR,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .is_bitpacked = false,
                             .bpp = 16,
                             .depth = 8,
                             .nb_comps = 3,
                             .full_name = "yuv422sp8",
                             .short_name = "nv16",
                             .alias = "yuv422sp_nv16",
                             },

        [PIXFMT_YUV422SP_NV61] =
            {
                             .fmt_id = PIXFMT_YUV422SP_NV61,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv422_yvu},
                             .layout = PIXFMT_LAYOUT_SEMIPLANAR,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .is_bitpacked = false,
                             .bpp = 16,
                             .depth = 8,
                             .nb_comps = 3,
                             .full_name = "yvu422sp8",
                             .short_name = "nv61",
                             .alias = "yuv422sp_nv61",
                             },

        [PIXFMT_YUV422SP_NV20] =
            {
                             .fmt_id = PIXFMT_YUV422SP_NV20,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv422_yuv},
                             .layout = PIXFMT_LAYOUT_SEMIPLANAR,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .is_bitpacked = true,
                             .bpp = 20,
                             .depth = 10,
                             .nb_comps = 3,
                             .full_name = "yuv422sp10bp",
                             .short_name = "nv20",
                             .alias = "yuv422sp_nv20",
                             },

        [PIXFMT_YUV422SP_10LSB] =
            {
                             .fmt_id = PIXFMT_YUV422SP_10LSB,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv422_yuv},
                             .layout = PIXFMT_LAYOUT_SEMIPLANAR,
                             .padding_pos = PIXFMT_PADDING_AT_MSB,
                             .is_bitpacked = false,
                             .bpp = 32,
                             .depth = 10,
                             .nb_comps = 3,
                             .full_name = "yuv422sp10l",
                             .short_name = "yuv422sp10l",
                             .alias = "yuv422sp_10lsb",
                             },

        [PIXFMT_YUV420P_YU12] =
            {
                             .fmt_id = PIXFMT_YUV420P_YU12,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv420_yuv},
                             .layout = PIXFMT_LAYOUT_PLANAR,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .is_bitpacked = false,
                             .bpp = 12,
                             .depth = 8,
                             .nb_comps = 3,
                             .full_name = "yuv420p8",
                             .short_name = "yu12",
                             .alias = "yuv420p_yu12",
                             },

        [PIXFMT_YUV420P_YV12] =
            {
                             .fmt_id = PIXFMT_YUV420P_YV12,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv420_yvu},
                             .layout = PIXFMT_LAYOUT_PLANAR,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .is_bitpacked = false,
                             .bpp = 12,
                             .depth = 8,
                             .nb_comps = 3,
                             .full_name = "yvu420p8",
                             .short_name = "yv12",
                             .alias = "yuv420p_yv12",
                             },

        [PIXFMT_YUV420P_10LSB] =
            {
                             .fmt_id = PIXFMT_YUV420P_10LSB,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv420_yuv},
                             .layout = PIXFMT_LAYOUT_PLANAR,
                             .padding_pos = PIXFMT_PADDING_AT_MSB,
                             .is_bitpacked = false,
                             .bpp = 24,
                             .depth = 10,
                             .nb_comps = 3,
                             .full_name = "yuv420p10l",
                             .short_name = "yuv420p10l",
                             .alias = "yuv420p_10lsb",
                             },


        [PIXFMT_YUV420SP_NV12] =
            {
                             .fmt_id = PIXFMT_YUV420SP_NV12,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv420_yuv},
                             .layout = PIXFMT_LAYOUT_SEMIPLANAR,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .is_bitpacked = false,
                             .bpp = 12,
                             .depth = 8,
                             .nb_comps = 3,
                             .full_name = "yuv420sp8",
                             .short_name = "nv12",
                             .alias = "yuv420sp_nv12",
                             },

        [PIXFMT_YUV420SP_NV21] =
            {
                             .fmt_id = PIXFMT_YUV420SP_NV21,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv420_yvu},
                             .layout = PIXFMT_LAYOUT_SEMIPLANAR,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .is_bitpacked = false,
                             .bpp = 12,
                             .depth = 8,
                             .nb_comps = 3,
                             .full_name = "yvu420sp8",
                             .short_name = "nv21",
                             .alias = "yuv420sp_nv21",
                             },

        [PIXFMT_YUV420SP_NV15] =
            {
                             .fmt_id = PIXFMT_YUV420SP_NV15,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv420_yuv},
                             .layout = PIXFMT_LAYOUT_SEMIPLANAR,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .is_bitpacked = true,
                             .bpp = 15,
                             .depth = 10,
                             .nb_comps = 3,
                             .full_name = "yuv420sp10bp",
                             .short_name = "nv15",
                             .alias = "yuv420sp_nv15",
                             },

        [PIXFMT_YUV420SP_10LSB] =
            {
                             .fmt_id = PIXFMT_YUV420SP_10LSB,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv420_yuv},
                             .layout = PIXFMT_LAYOUT_SEMIPLANAR,
                             .padding_pos = PIXFMT_PADDING_AT_MSB,
                             .is_bitpacked = false,
                             .bpp = 24,
                             .depth = 10,
                             .nb_comps = 3,
                             .full_name = "yuv420sp10l",
                             .short_name = "yuv420sp10l",
                             .alias = "yuv420sp_10lsb",
                             },

        [PIXFMT_YUV411P_YU11] =
            {
                             .fmt_id = PIXFMT_YUV411P_YU11,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv411_yuv},
                             .layout = PIXFMT_LAYOUT_PLANAR,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .is_bitpacked = false,
                             .bpp = 12,
                             .depth = 8,
                             .nb_comps = 3,
                             .full_name = "yuv411p8",
                             .short_name = "yu11",
                             .alias = "yuv411p_yu11",
                             },

        [PIXFMT_YUV411P_YV11] =
            {
                             .fmt_id = PIXFMT_YUV411P_YV11,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv411_yvu},
                             .layout = PIXFMT_LAYOUT_PLANAR,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .is_bitpacked = false,
                             .bpp = 12,
                             .depth = 8,
                             .nb_comps = 3,
                             .full_name = "yvu411p8",
                             .short_name = "yv11",
                             .alias = "yuv411p_yv11",
                             },

        [PIXFMT_YUV410P_YUV9] =
            {
                             .fmt_id = PIXFMT_YUV410P_YUV9,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv410_yuv},
                             .layout = PIXFMT_LAYOUT_PLANAR,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .is_bitpacked = false,
                             .bpp = 9,
                             .depth = 8,
                             .nb_comps = 3,
                             .full_name = "yuv410p8",
                             .short_name = "yuv9",
                             .alias = "yuv410p_yuv9",
                             },

        [PIXFMT_YUV410P_YVU9] =
            {
                             .fmt_id = PIXFMT_YUV410P_YVU9,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv410_yvu},
                             .layout = PIXFMT_LAYOUT_PLANAR,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .is_bitpacked = false,
                             .bpp = 9,
                             .depth = 8,
                             .nb_comps = 3,
                             .full_name = "yvu410p8",
                             .short_name = "yvu9",
                             .alias = "yuv410p_yvu9",
                             },

        [PIXFMT_YUV400_R1] =
            {
                             .fmt_id = PIXFMT_YUV400_R1,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv400},
                             .layout = PIXFMT_LAYOUT_PLANAR,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .is_bitpacked = true,
                             .bpp = 1,
                             .depth = 1,
                             .nb_comps = 1,
                             .full_name = "yuv400r1bp",
                             .short_name = "y1bp",
                             .alias = NULL,
                             },
        [PIXFMT_YUV400_R2] =
            {
                             .fmt_id = PIXFMT_YUV400_R2,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv400},
                             .layout = PIXFMT_LAYOUT_PLANAR,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .is_bitpacked = true,
                             .bpp = 2,
                             .depth = 2,
                             .nb_comps = 1,
                             .full_name = "yuv400r2bp",
                             .short_name = "y2bp",
                             .alias = NULL,
                             },
        [PIXFMT_YUV400_R4] =
            {
                             .fmt_id = PIXFMT_YUV400_R4,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv400},
                             .layout = PIXFMT_LAYOUT_PLANAR,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .is_bitpacked = true,
                             .bpp = 4,
                             .depth = 4,
                             .nb_comps = 1,
                             .full_name = "yuv400r4bp",
                             .short_name = "y4bp",
                             .alias = NULL,
                             },
        [PIXFMT_YUV400_R8] =
            {
                             .fmt_id = PIXFMT_YUV400_R8,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv400},
                             .layout = PIXFMT_LAYOUT_PLANAR,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .is_bitpacked = false,
                             .bpp = 8,
                             .depth = 8,
                             .nb_comps = 1,
                             .full_name = "yuv400r8",
                             .short_name = "y8",
                             .alias = NULL,
                             },
        [PIXFMT_YUV400_R10] =
            {
                             .fmt_id = PIXFMT_YUV400_R10,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv400},
                             .layout = PIXFMT_LAYOUT_PLANAR,
                             .padding_pos = PIXFMT_PADDING_AT_MSB,
                             .is_bitpacked = false,
                             .bpp = 16,
                             .depth = 10,
                             .nb_comps = 1,
                             .full_name = "yuv400r10l",
                             .short_name = "y10l",
                             .alias = NULL,
                             },
        [PIXFMT_YUV400_R12] =
            {
                             .fmt_id = PIXFMT_YUV400_R12,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv400},
                             .layout = PIXFMT_LAYOUT_PLANAR,
                             .padding_pos = PIXFMT_PADDING_AT_MSB,
                             .is_bitpacked = false,
                             .bpp = 16,
                             .depth = 12,
                             .nb_comps = 1,
                             .full_name = "yuv400r12l",
                             .short_name = "y12l",
                             .alias = NULL,
                             },
        [PIXFMT_YUV400_R16] =
            {
                             .fmt_id = PIXFMT_YUV400_R16,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv400},
                             .layout = PIXFMT_LAYOUT_PLANAR,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .is_bitpacked = false,
                             .bpp = 16,
                             .depth = 16,
                             .nb_comps = 1,
                             .full_name = "yuv400r16",
                             .short_name = "y16",
                             .alias = NULL,
                             },

        [PIXFMT_YUV444SP_TILE4x4] =
            {
                             .fmt_id = PIXFMT_YUV444SP_TILE4x4,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv444_tile4x4},
                             .layout = PIXFMT_LAYOUT_TILE,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .is_bitpacked = false,
                             .bpp = 24,
                             .depth = 8,
                             .nb_comps = 3,
                             .full_name = "yuv444sp8_tile4x4",
                             .short_name = "nv24_tile4x4",
                             .alias = NULL,
                             },

        [PIXFMT_YUV422SP_TILE4x4] =
            {
                             .fmt_id = PIXFMT_YUV422SP_TILE4x4,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv422_tile4x4},
                             .layout = PIXFMT_LAYOUT_TILE,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .is_bitpacked = false,
                             .bpp = 16,
                             .depth = 8,
                             .nb_comps = 3,
                             .full_name = "yuv422sp8_tile4x4",
                             .short_name = "nv16_tile4x4",
                             .alias = NULL,
                             },

        [PIXFMT_YUV420SP_TILE4x4] =
            {
                             .fmt_id = PIXFMT_YUV420SP_TILE4x4,
                             .base_type = PIXFMT_TYPE_YUV,
                             .desc = {.yuv = &g_yuv_desc_yuv420_tile4x4},
                             .layout = PIXFMT_LAYOUT_TILE,
                             .padding_pos = PIXFMT_NO_PADDING,
                             .is_bitpacked = false,
                             .bpp = 12,
                             .depth = 8,
                             .nb_comps = 3,
                             .full_name = "yuv420sp_tile4x4",
                             .short_name = "yuv420sp_tile4x4",
                             .alias = NULL,
                             },
};

#define PIXFMT_ATTR_TABLE_SIZE (sizeof(g_pixfmt_attr_table) / sizeof(pixfmt_attr_s))


const char *pixfmt_get_extern_str(pixfmt_e fmt)
{
    const pixfmt_attr_s *attr = pixfmt_get_attr(fmt);
    if (attr->base_type == PIXFMT_TYPE_RGB)
        return "rgb";
    if (attr->base_type == PIXFMT_TYPE_YUV)
        return "yuv";
    return "InvalidFmt";
}

const char *pixfmt_get_layout_str(pixfmt_layout_e layout)
{
    switch (layout) {
    case PIXFMT_LAYOUT_INTERLEAVED: return "Interleaved";
    case PIXFMT_LAYOUT_PLANAR:      return "Planar";
    case PIXFMT_LAYOUT_SEMIPLANAR:  return "Semi-Planar";
    case PIXFMT_LAYOUT_TILE:        return "Sp-Tile";
    case PIXFMT_LAYOUT_IRREGULAR:   return "Irregular";
    default:                        return "InvalidLayout";
    }
}
const char *pixfmt_get_padding_str(pixfmt_padding_pos_e padpos)
{
    switch (padpos) {
    case PIXFMT_NO_PADDING:     return "NoPadding";
    case PIXFMT_PADDING_AT_MSB: return "PaddingAtMSB";
    case PIXFMT_PADDING_AT_LSB: return "PaddingAtLSB";
    }
}


const pixfmt_attr_s *pixfmt_get_attr(pixfmt_e fmt)
{
    if (fmt >= 0 && fmt < PIXFMT_NB_COUNT) {
        return &g_pixfmt_attr_table[fmt];
    }
    LOGE("pixfmt_get_attr: no attr found! invalid fmt %d\n", fmt);
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
    LOGE("pixfmt_get_attr_by_name: name '%s' not found!\n", name);
    return NULL;
}

const char *pixfmt_full_name(pixfmt_e fmt)
{
    const pixfmt_attr_s *attr = pixfmt_get_attr(fmt);
    return attr ? attr->full_name : "InvalidFmt";
}

const char *pixfmt_short_name(pixfmt_e fmt)
{
    const pixfmt_attr_s *attr = pixfmt_get_attr(fmt);
    return attr ? attr->short_name : "InvalidFmt";
}

const char *pixfmt_alias(pixfmt_e fmt)
{
    const pixfmt_attr_s *attr = pixfmt_get_attr(fmt);
    return attr ? attr->alias : "InvalidFmt";
}

int pixfmt_bpp(pixfmt_e fmt)
{
    const pixfmt_attr_s *attr = pixfmt_get_attr(fmt);
    return attr ? attr->bpp : 0;
}

int pixfmt_depth(pixfmt_e fmt)
{
    const pixfmt_attr_s *attr = pixfmt_get_attr(fmt);
    return attr ? attr->depth : 0;
}

int pixfmt_nb_comps(pixfmt_e fmt)
{
    const pixfmt_attr_s *attr = pixfmt_get_attr(fmt);
    return attr ? attr->nb_comps : 0;
}

int pixfmt_nb_planes(pixfmt_e fmt)
{
    const pixfmt_attr_s *attr = pixfmt_get_attr(fmt);
    if (!attr)
        return 0;

    switch (attr->layout) {
    case PIXFMT_LAYOUT_PLANAR:      return attr->nb_comps;
    case PIXFMT_LAYOUT_SEMIPLANAR:  return 2;
    case PIXFMT_LAYOUT_INTERLEAVED:
    case PIXFMT_LAYOUT_TILE:
    case PIXFMT_LAYOUT_IRREGULAR:   return 1;
    default:                        return 0;
    }
}

bool pixfmt_is_yuv(pixfmt_e fmt)
{
    const pixfmt_attr_s *attr = pixfmt_get_attr(fmt);
    return attr ? attr->base_type == PIXFMT_TYPE_YUV : false;
}

bool pixfmt_is_rgb(pixfmt_e fmt)
{
    const pixfmt_attr_s *attr = pixfmt_get_attr(fmt);
    return attr ? attr->base_type == PIXFMT_TYPE_RGB : false;
}

bool pixfmt_is_uv_order(pixfmt_e fmt)
{
    const pixfmt_attr_s *attr = pixfmt_get_attr(fmt);
    if (!attr || attr->base_type != PIXFMT_TYPE_YUV)
        return false;
    return pixfmt_yuv_desc_is_yuv_order(attr->desc.yuv);
}

bool pixfmt_is_tile(pixfmt_e fmt)
{
    const pixfmt_attr_s *attr = pixfmt_get_attr(fmt);
    if (!attr || attr->base_type != PIXFMT_TYPE_YUV)
        return false;
    return pixfmt_yuv_desc_is_tile(attr->desc.yuv);
}

bool pixfmt_is_bgr_order(pixfmt_e fmt)
{
    const pixfmt_attr_s *attr = pixfmt_get_attr(fmt);
    if (!attr || attr->base_type != PIXFMT_TYPE_RGB)
        return false;
    return pixfmt_rgb_desc_is_bgr_order(attr->desc.rgb);
}

bool pixfmt_has_alpha(pixfmt_e fmt)
{
    const pixfmt_attr_s *attr = pixfmt_get_attr(fmt);
    if (!attr || attr->base_type != PIXFMT_TYPE_RGB)
        return false;
    return pixfmt_rgb_desc_has_alpha(attr->desc.rgb);
}

int pixfmt_get_channel_bits(pixfmt_e fmt, uint8_t *r, uint8_t *g, uint8_t *b, uint8_t *a)
{
    const pixfmt_attr_s *attr = pixfmt_get_attr(fmt);
    if (!attr || attr->base_type != PIXFMT_TYPE_RGB)
        return 0;
    return pixfmt_rgb_desc_get_channel_bits(attr->desc.rgb, r, g, b, a);
}

void pixfmt_dump_attr(const pixfmt_attr_s *attr)
{
    LOGI("dump format %d attr below:\n", attr->fmt_id);
    LOGI(" - name: %s / %s / %s\n", attr->full_name, attr->short_name, attr->alias);
    LOGI(" - base_type: %d(%s), layout: %s, padding: %s\n", attr->base_type, pixfmt_get_extern_str(attr->fmt_id),
        pixfmt_get_layout_str(attr->layout), pixfmt_get_padding_str(attr->padding_pos));
    LOGI(" - bpp: %d, depth: %d, nb_comps: %d, is_bitpacked: %d\n", attr->bpp, attr->depth, attr->nb_comps, attr->is_bitpacked);
    if (attr->base_type == PIXFMT_TYPE_RGB) {
        pixfmt_rgb_dump_desc(attr->desc.rgb);
    }
    else if (attr->base_type == PIXFMT_TYPE_YUV) {
        pixfmt_yuv_dump_desc(attr->desc.yuv);
    }
}

int pixfmt_get_tile_size(pixfmt_e fmt, int *tile_w, int *tile_h)
{
    const pixfmt_attr_s *attr = pixfmt_get_attr(fmt);
    if (!attr || attr->base_type != PIXFMT_TYPE_YUV)
        return -1;
    return pixfmt_yuv_desc_get_tile_size(attr->desc.yuv, tile_w, tile_h);
}

int pixfmt_get_chroma_subsampling(pixfmt_e fmt, int *h_sub, int *v_sub)
{
    const pixfmt_attr_s *attr = pixfmt_get_attr(fmt);
    if (!attr || attr->base_type != PIXFMT_TYPE_YUV)
        return -1;
    return pixfmt_yuv_desc_get_chroma_subsampling(attr->desc.yuv, h_sub, v_sub);
}

pixfmt_e pixfmt_init_common_fmt_rgb(int depth, bool need_alpha)
{
    if (depth <= 8)
        return need_alpha ? PIXFMT_RGBA8888 : PIXFMT_RGB888;
    else if (depth == 10)
        // only PIXFMT_RGBA1010102 / PIXFMT_ABGR2101010
        return need_alpha ? PIXFMT_RGBA10Lsb : PIXFMT_RGB10Lsb;
    return PIXFMT_INVALID;
}

pixfmt_e pixfmt_init_common_fmt_yuv(int depth, pixfmt_layout_e layout, pixfmt_yuv_sampling_e sampling)
{
    pixfmt_e com_fmt = PIXFMT_INVALID;
    switch (sampling) {
    case PIXFMT_YUV_SAMPLING_444: {
        if (depth <= 8) {
            if (layout == PIXFMT_LAYOUT_INTERLEAVED)
                com_fmt = PIXFMT_YUV444I_VU24;
            else if (layout == PIXFMT_LAYOUT_PLANAR)
                com_fmt = PIXFMT_YUV444P_YU24;
            else if (layout == PIXFMT_LAYOUT_SEMIPLANAR)
                com_fmt = PIXFMT_YUV444SP_NV24;
        }
        else if (depth == 10) {
            if (layout == PIXFMT_LAYOUT_INTERLEAVED)
                com_fmt = PIXFMT_YUV444I_10LSB;
            else if (layout == PIXFMT_LAYOUT_PLANAR)
                com_fmt = PIXFMT_YUV444P_10LSB;
            else if (layout == PIXFMT_LAYOUT_SEMIPLANAR)
                com_fmt = PIXFMT_YUV444SP_10LSB;
        }
    } break;
    case PIXFMT_YUV_SAMPLING_422: {
        if (depth <= 8) {
            if (layout == PIXFMT_LAYOUT_INTERLEAVED)
                com_fmt = PIXFMT_YUV422I_YUYV;
            else if (layout == PIXFMT_LAYOUT_PLANAR)
                com_fmt = PIXFMT_YUV422P_YU16;
            else if (layout == PIXFMT_LAYOUT_SEMIPLANAR)
                com_fmt = PIXFMT_YUV422SP_NV16;
        }
        else if (depth == 10) {
            if (layout == PIXFMT_LAYOUT_INTERLEAVED)
                com_fmt = PIXFMT_YUV422I_Y210;
            else if (layout == PIXFMT_LAYOUT_PLANAR)
                com_fmt = PIXFMT_YUV422P_10LSB;
            else if (layout == PIXFMT_LAYOUT_SEMIPLANAR)
                com_fmt = PIXFMT_YUV422SP_10LSB;
        }
    } break;
    case PIXFMT_YUV_SAMPLING_420: {
        if (depth <= 8) {
            if (layout == PIXFMT_LAYOUT_PLANAR)
                com_fmt = PIXFMT_YUV420P_YU12;
            else if (layout == PIXFMT_LAYOUT_SEMIPLANAR)
                com_fmt = PIXFMT_YUV420SP_NV12;
        }
        else if (depth == 10) {
            if (layout == PIXFMT_LAYOUT_PLANAR)
                com_fmt = PIXFMT_YUV420P_10LSB;
            else if (layout == PIXFMT_LAYOUT_SEMIPLANAR)
                com_fmt = PIXFMT_YUV420SP_10LSB;
        }
    } break;
    case PIXFMT_YUV_SAMPLING_411: {
        if (depth <= 8 && layout == PIXFMT_LAYOUT_PLANAR)
            com_fmt = PIXFMT_YUV411P_YU11;
    } break;
    case PIXFMT_YUV_SAMPLING_410: {
        if (depth <= 8 && layout == PIXFMT_LAYOUT_PLANAR)
            com_fmt = PIXFMT_YUV410P_YUV9;
    } break;
    case PIXFMT_YUV_SAMPLING_400: {
        if (depth <= 8)
            com_fmt = PIXFMT_YUV400_R8;
        else if (depth == 10)
            com_fmt = PIXFMT_YUV400_R10;
        else if (depth == 12)
            com_fmt = PIXFMT_YUV400_R12;
        else if (depth == 16)
            com_fmt = PIXFMT_YUV400_R16;
    } break;
    case PIXFMT_YUV_SAMPLING_440: // no YUV440 formats for now
    default:                      break;
    }
    return com_fmt;
}

pixfmt_e pixfmt_get_common_fmt(pixfmt_e fmt, pixfmt_layout_e target_layout, bool need_alpha)
{
    const pixfmt_attr_s *attr = pixfmt_get_attr(fmt);
    assert(attr != NULL);

    pixfmt_e com_fmt = PIXFMT_INVALID;

    if (pixfmt_is_rgb(fmt)) {
        /* convert to 8/10bit rgb[a], ignore target_layout */
        com_fmt = pixfmt_init_common_fmt_rgb(attr->depth, need_alpha);
    }
    else if (pixfmt_is_yuv(fmt)) {
        /* convert to 8/10bit planar yuv in common */
        const pixfmt_yuv_desc_s *desc = attr->desc.yuv;
        if (desc->is_tile && target_layout == PIXFMT_LAYOUT_SEMIPLANAR)
            com_fmt = pixfmt_init_common_fmt_yuv(attr->depth, PIXFMT_LAYOUT_SEMIPLANAR, desc->sampling);
        else if (!desc->is_tile)
            com_fmt = pixfmt_init_common_fmt_yuv(attr->depth, target_layout, desc->sampling);
    }

    return com_fmt;
}

#if 0
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
#endif

/* ========== DRM FourCC mapping ========== */
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

pixfmt_e pixfmt_from_drm_fourcc(uint32_t fourcc)
{
    switch (fourcc) {
    /* RGB formats */
    case DRM_FORMAT_RGB888:      return PIXFMT_BGR888;
    case DRM_FORMAT_BGR888:      return PIXFMT_RGB888;
    case DRM_FORMAT_ARGB8888:    return PIXFMT_BGRA8888;
    case DRM_FORMAT_ABGR8888:    return PIXFMT_RGBA8888;
    case DRM_FORMAT_RGBA8888:    return PIXFMT_ABGR8888;
    case DRM_FORMAT_BGRA8888:    return PIXFMT_ARGB8888;
    case DRM_FORMAT_RGB332:      return PIXFMT_RGB332;
    case DRM_FORMAT_BGR233:      return PIXFMT_BGR233;
    case DRM_FORMAT_RGB565:      return PIXFMT_RGB565;
    case DRM_FORMAT_BGR565:      return PIXFMT_BGR565;
    case DRM_FORMAT_ABGR1555:    return PIXFMT_ABGR1555;
    case DRM_FORMAT_RGBA5551:    return PIXFMT_RGBA5551;
    case DRM_FORMAT_ABGR4444:    return PIXFMT_ABGR4444;
    case DRM_FORMAT_RGBA4444:    return PIXFMT_RGBA4444;
    case DRM_FORMAT_ABGR2101010: return PIXFMT_ABGR2101010;
    case DRM_FORMAT_RGBA1010102: return PIXFMT_RGBA1010102;

    /* YUV interleaved/planar/semiplanar formats */
    case DRM_FORMAT_VUY888:      return PIXFMT_YUV444I_VU24;
    case DRM_FORMAT_VUY101010:   return PIXFMT_YUV444I_VU30;
    case DRM_FORMAT_XVYU2101010: return PIXFMT_YUV444I_XV30;
    case DRM_FORMAT_YUV444:      return PIXFMT_YUV444P_YU24;
    case DRM_FORMAT_YVU444:      return PIXFMT_YUV444P_YV24;
    case DRM_FORMAT_NV24:        return PIXFMT_YUV444SP_NV24;
    case DRM_FORMAT_NV42:        return PIXFMT_YUV444SP_NV42;
    case DRM_FORMAT_NV30:        return PIXFMT_YUV444SP_NV30;
    case DRM_FORMAT_YUYV:        return PIXFMT_YUV422I_YUYV;
    case DRM_FORMAT_YVYU:        return PIXFMT_YUV422I_YVYU;
    case DRM_FORMAT_UYVY:        return PIXFMT_YUV422I_UYVY;
    case DRM_FORMAT_VYUY:        return PIXFMT_YUV422I_VYUY;
    case DRM_FORMAT_Y210:        return PIXFMT_YUV422I_Y210;
    case DRM_FORMAT_Y212:        return PIXFMT_YUV422I_Y212;
    case DRM_FORMAT_Y216:        return PIXFMT_YUV422I_Y216;
    case DRM_FORMAT_YUV422:      return PIXFMT_YUV422P_YU16;
    case DRM_FORMAT_YVU422:      return PIXFMT_YUV422P_YV16;
    case DRM_FORMAT_NV16:        return PIXFMT_YUV422SP_NV16;
    case DRM_FORMAT_NV61:        return PIXFMT_YUV422SP_NV61;
    case DRM_FORMAT_NV20:        return PIXFMT_YUV422SP_NV20;
    case DRM_FORMAT_YUV420:      return PIXFMT_YUV420P_YU12;
    case DRM_FORMAT_YVU420:      return PIXFMT_YUV420P_YV12;
    case DRM_FORMAT_NV12:        return PIXFMT_YUV420SP_NV12;
    case DRM_FORMAT_NV21:        return PIXFMT_YUV420SP_NV21;
    case DRM_FORMAT_NV15:        return PIXFMT_YUV420SP_NV15;
    case DRM_FORMAT_YUV411:      return PIXFMT_YUV411P_YU11;
    case DRM_FORMAT_YVU411:      return PIXFMT_YUV411P_YV11;
    case DRM_FORMAT_YUV410:      return PIXFMT_YUV410P_YUV9;
    case DRM_FORMAT_YVU410:      return PIXFMT_YUV410P_YVU9;

    /* YUV400 (grayscale) formats */
    case DRM_FORMAT_R1:          return PIXFMT_YUV400_R1;
    case DRM_FORMAT_R2:          return PIXFMT_YUV400_R2;
    case DRM_FORMAT_R4:          return PIXFMT_YUV400_R4;
    case DRM_FORMAT_R8:          return PIXFMT_YUV400_R8;
    case DRM_FORMAT_R10:         return PIXFMT_YUV400_R10;
    case DRM_FORMAT_R12:         return PIXFMT_YUV400_R12;
    case DRM_FORMAT_R16:         return PIXFMT_YUV400_R16;

    default:                     return PIXFMT_INVALID;
    }
}

uint32_t pixfmt_to_drm_fourcc(pixfmt_e fmt)
{
    switch (fmt) {
    /* RGB formats */
    case PIXFMT_RGB888:           return DRM_FORMAT_BGR888;
    case PIXFMT_BGR888:           return DRM_FORMAT_RGB888;
    case PIXFMT_RGBA8888:         return DRM_FORMAT_ABGR8888;
    case PIXFMT_BGRA8888:         return DRM_FORMAT_ARGB8888;
    case PIXFMT_ARGB8888:         return DRM_FORMAT_BGRA8888;
    case PIXFMT_ABGR8888:         return DRM_FORMAT_RGBA8888;
    case PIXFMT_RGB332:           return DRM_FORMAT_RGB332;
    case PIXFMT_BGR233:           return DRM_FORMAT_BGR233;
    case PIXFMT_RGB565:           return DRM_FORMAT_RGB565;
    case PIXFMT_BGR565:           return DRM_FORMAT_BGR565;
    case PIXFMT_ABGR1555:         return DRM_FORMAT_ABGR1555;
    case PIXFMT_RGBA5551:         return DRM_FORMAT_RGBA5551;
    case PIXFMT_ABGR4444:         return DRM_FORMAT_ABGR4444;
    case PIXFMT_RGBA4444:         return DRM_FORMAT_RGBA4444;
    case PIXFMT_ABGR2101010:      return DRM_FORMAT_ABGR2101010;
    case PIXFMT_RGBA1010102:      return DRM_FORMAT_RGBA1010102;

    /* YUV interleaved/planar/semiplanar formats */
    case PIXFMT_YUV444I_VU24:     return DRM_FORMAT_VUY888;
    case PIXFMT_YUV444I_VU30:     return DRM_FORMAT_VUY101010;
    case PIXFMT_YUV444I_XV30:     return DRM_FORMAT_XVYU2101010;
    case PIXFMT_YUV444P_YU24:     return DRM_FORMAT_YUV444;
    case PIXFMT_YUV444P_YV24:     return DRM_FORMAT_YVU444;
    case PIXFMT_YUV444SP_NV24:    return DRM_FORMAT_NV24;
    case PIXFMT_YUV444SP_NV42:    return DRM_FORMAT_NV42;
    case PIXFMT_YUV444SP_NV30:    return DRM_FORMAT_NV30;
    case PIXFMT_YUV422I_YUYV:     return DRM_FORMAT_YUYV;
    case PIXFMT_YUV422I_YVYU:     return DRM_FORMAT_YVYU;
    case PIXFMT_YUV422I_UYVY:     return DRM_FORMAT_UYVY;
    case PIXFMT_YUV422I_VYUY:     return DRM_FORMAT_VYUY;
    case PIXFMT_YUV422I_Y210:     return DRM_FORMAT_Y210;
    case PIXFMT_YUV422I_Y212:     return DRM_FORMAT_Y212;
    case PIXFMT_YUV422I_Y216:     return DRM_FORMAT_Y216;
    case PIXFMT_YUV422P_YU16:     return DRM_FORMAT_YUV422;
    case PIXFMT_YUV422P_YV16:     return DRM_FORMAT_YVU422;
    case PIXFMT_YUV422SP_NV16:    return DRM_FORMAT_NV16;
    case PIXFMT_YUV422SP_NV61:    return DRM_FORMAT_NV61;
    case PIXFMT_YUV422SP_NV20:    return DRM_FORMAT_NV20;
    case PIXFMT_YUV420P_YU12:     return DRM_FORMAT_YUV420;
    case PIXFMT_YUV420P_YV12:     return DRM_FORMAT_YVU420;
    case PIXFMT_YUV420SP_NV12:    return DRM_FORMAT_NV12;
    case PIXFMT_YUV420SP_NV21:    return DRM_FORMAT_NV21;
    case PIXFMT_YUV420SP_NV15:    return DRM_FORMAT_NV15;
    case PIXFMT_YUV411P_YU11:     return DRM_FORMAT_YUV411;
    case PIXFMT_YUV411P_YV11:     return DRM_FORMAT_YVU411;
    case PIXFMT_YUV410P_YUV9:     return DRM_FORMAT_YUV410;
    case PIXFMT_YUV410P_YVU9:     return DRM_FORMAT_YVU410;

    /* YUV400 (grayscale) formats */
    case PIXFMT_YUV400_R1:        return DRM_FORMAT_R1;
    case PIXFMT_YUV400_R2:        return DRM_FORMAT_R2;
    case PIXFMT_YUV400_R4:        return DRM_FORMAT_R4;
    case PIXFMT_YUV400_R8:        return DRM_FORMAT_R8;
    case PIXFMT_YUV400_R10:       return DRM_FORMAT_R10;
    case PIXFMT_YUV400_R12:       return DRM_FORMAT_R12;
    case PIXFMT_YUV400_R16:       return DRM_FORMAT_R16;

    /* No DRM format for these */
    case PIXFMT_RGB10Lsb:
    case PIXFMT_RGBA10Lsb:
    case PIXFMT_YUV444I_10LSB:
    case PIXFMT_YUV444P_10LSB:
    case PIXFMT_YUV444SP_10LSB:
    case PIXFMT_YUV422P_10LSB:
    case PIXFMT_YUV422SP_10LSB:
    case PIXFMT_YUV420P_10LSB:
    case PIXFMT_YUV420SP_10LSB:
    case PIXFMT_YUV444SP_TILE4x4:
    case PIXFMT_YUV422SP_TILE4x4:
    case PIXFMT_YUV420SP_TILE4x4:
    default:                      return 0;
    }
}