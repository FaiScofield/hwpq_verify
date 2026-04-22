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
    return pixfmt_yuv_desc_is_uv_order(attr->desc.yuv);
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
