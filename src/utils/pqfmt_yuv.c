/**
 * @copyright: Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @brief:     YUV format descriptor implementation
 * @author:
 * @create:    2026-04-16
 */

#include "pqfmt_yuv.h"
#include <stdio.h>
#include <string.h>
#include <math.h>

const pqfmt_yuv_desc_s g_yuv_desc_yuv444i_vu24 = {
    .sampling = PQFMT_YUV_SAMPLING_444,
    .uv_sample_ratio_ver = PQFMT_YUV444_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PQFMT_YUV444_SAMPLE_RATIO_HOR,
    .layout = PQFMT_YUV_LAYOUT_Interleaved,
    .order = PQFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pqfmt_yuv_desc_s g_yuv_desc_yuv444i_vu30 = {
    .sampling = PQFMT_YUV_SAMPLING_444,
    .uv_sample_ratio_ver = PQFMT_YUV444_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PQFMT_YUV444_SAMPLE_RATIO_HOR,
    .layout = PQFMT_YUV_LAYOUT_Interleaved,
    .order = PQFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pqfmt_yuv_desc_s g_yuv_desc_yuv444i_xv30 = {
    .sampling = PQFMT_YUV_SAMPLING_444,
    .uv_sample_ratio_ver = PQFMT_YUV444_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PQFMT_YUV444_SAMPLE_RATIO_HOR,
    .layout = PQFMT_YUV_LAYOUT_Interleaved,
    .order = PQFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pqfmt_yuv_desc_s g_yuv_desc_yuv444p_yu24 = {
    .sampling = PQFMT_YUV_SAMPLING_444,
    .uv_sample_ratio_ver = PQFMT_YUV444_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PQFMT_YUV444_SAMPLE_RATIO_HOR,
    .layout = PQFMT_YUV_LAYOUT_Planar,
    .order = PQFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pqfmt_yuv_desc_s g_yuv_desc_yuv444p_yv24 = {
    .sampling = PQFMT_YUV_SAMPLING_444,
    .uv_sample_ratio_ver = PQFMT_YUV444_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PQFMT_YUV444_SAMPLE_RATIO_HOR,
    .layout = PQFMT_YUV_LAYOUT_Planar,
    .order = PQFMT_ORDER_YVU,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pqfmt_yuv_desc_s g_yuv_desc_yuv444sp_nv24 = {
    .sampling = PQFMT_YUV_SAMPLING_444,
    .uv_sample_ratio_ver = PQFMT_YUV444_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PQFMT_YUV444_SAMPLE_RATIO_HOR,
    .layout = PQFMT_YUV_LAYOUT_SimiPlanar,
    .order = PQFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pqfmt_yuv_desc_s g_yuv_desc_yuv444sp_nv42 = {
    .sampling = PQFMT_YUV_SAMPLING_444,
    .uv_sample_ratio_ver = PQFMT_YUV444_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PQFMT_YUV444_SAMPLE_RATIO_HOR,
    .layout = PQFMT_YUV_LAYOUT_SimiPlanar,
    .order = PQFMT_ORDER_YVU,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pqfmt_yuv_desc_s g_yuv_desc_yuv444sp_nv30 = {
    .sampling = PQFMT_YUV_SAMPLING_444,
    .uv_sample_ratio_ver = PQFMT_YUV444_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PQFMT_YUV444_SAMPLE_RATIO_HOR,
    .layout = PQFMT_YUV_LAYOUT_SimiPlanar,
    .order = PQFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pqfmt_yuv_desc_s g_yuv_desc_yuv422i_yuyv = {
    .sampling = PQFMT_YUV_SAMPLING_422,
    .uv_sample_ratio_ver = PQFMT_YUV422_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PQFMT_YUV422_SAMPLE_RATIO_HOR,
    .layout = PQFMT_YUV_LAYOUT_Interleaved,
    .order = PQFMT_ORDER_YUYV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pqfmt_yuv_desc_s g_yuv_desc_yuv422i_yvyu = {
    .sampling = PQFMT_YUV_SAMPLING_422,
    .uv_sample_ratio_ver = PQFMT_YUV422_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PQFMT_YUV422_SAMPLE_RATIO_HOR,
    .layout = PQFMT_YUV_LAYOUT_Interleaved,
    .order = PQFMT_ORDER_YVYU,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pqfmt_yuv_desc_s g_yuv_desc_yuv422i_uyvy = {
    .sampling = PQFMT_YUV_SAMPLING_422,
    .uv_sample_ratio_ver = PQFMT_YUV422_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PQFMT_YUV422_SAMPLE_RATIO_HOR,
    .layout = PQFMT_YUV_LAYOUT_Interleaved,
    .order = PQFMT_ORDER_UYVY,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pqfmt_yuv_desc_s g_yuv_desc_yuv422i_vyuy = {
    .sampling = PQFMT_YUV_SAMPLING_422,
    .uv_sample_ratio_ver = PQFMT_YUV422_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PQFMT_YUV422_SAMPLE_RATIO_HOR,
    .layout = PQFMT_YUV_LAYOUT_Interleaved,
    .order = PQFMT_ORDER_VYUY,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pqfmt_yuv_desc_s g_yuv_desc_yuv422p_yu16 = {
    .sampling = PQFMT_YUV_SAMPLING_422,
    .uv_sample_ratio_ver = PQFMT_YUV422_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PQFMT_YUV422_SAMPLE_RATIO_HOR,
    .layout = PQFMT_YUV_LAYOUT_Planar,
    .order = PQFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pqfmt_yuv_desc_s g_yuv_desc_yuv422p_yv16 = {
    .sampling = PQFMT_YUV_SAMPLING_422,
    .uv_sample_ratio_ver = PQFMT_YUV422_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PQFMT_YUV422_SAMPLE_RATIO_HOR,
    .layout = PQFMT_YUV_LAYOUT_Planar,
    .order = PQFMT_ORDER_YVU,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pqfmt_yuv_desc_s g_yuv_desc_yuv422sp_nv16 = {
    .sampling = PQFMT_YUV_SAMPLING_422,
    .uv_sample_ratio_ver = PQFMT_YUV422_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PQFMT_YUV422_SAMPLE_RATIO_HOR,
    .layout = PQFMT_YUV_LAYOUT_SimiPlanar,
    .order = PQFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pqfmt_yuv_desc_s g_yuv_desc_yuv422sp_nv61 = {
    .sampling = PQFMT_YUV_SAMPLING_422,
    .uv_sample_ratio_ver = PQFMT_YUV422_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PQFMT_YUV422_SAMPLE_RATIO_HOR,
    .layout = PQFMT_YUV_LAYOUT_SimiPlanar,
    .order = PQFMT_ORDER_YVU,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pqfmt_yuv_desc_s g_yuv_desc_yuv422sp_nv20 = {
    .sampling = PQFMT_YUV_SAMPLING_422,
    .uv_sample_ratio_ver = PQFMT_YUV422_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PQFMT_YUV422_SAMPLE_RATIO_HOR,
    .layout = PQFMT_YUV_LAYOUT_SimiPlanar,
    .order = PQFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pqfmt_yuv_desc_s g_yuv_desc_yuv420p_yu12 = {
    .sampling = PQFMT_YUV_SAMPLING_420,
    .uv_sample_ratio_ver = PQFMT_YUV420_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PQFMT_YUV420_SAMPLE_RATIO_HOR,
    .layout = PQFMT_YUV_LAYOUT_Planar,
    .order = PQFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pqfmt_yuv_desc_s g_yuv_desc_yuv420p_yv12 = {
    .sampling = PQFMT_YUV_SAMPLING_420,
    .uv_sample_ratio_ver = PQFMT_YUV420_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PQFMT_YUV420_SAMPLE_RATIO_HOR,
    .layout = PQFMT_YUV_LAYOUT_Planar,
    .order = PQFMT_ORDER_YVU,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pqfmt_yuv_desc_s g_yuv_desc_yuv420sp_nv12 = {
    .sampling = PQFMT_YUV_SAMPLING_420,
    .uv_sample_ratio_ver = PQFMT_YUV420_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PQFMT_YUV420_SAMPLE_RATIO_HOR,
    .layout = PQFMT_YUV_LAYOUT_SimiPlanar,
    .order = PQFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pqfmt_yuv_desc_s g_yuv_desc_yuv420sp_nv21 = {
    .sampling = PQFMT_YUV_SAMPLING_420,
    .uv_sample_ratio_ver = PQFMT_YUV420_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PQFMT_YUV420_SAMPLE_RATIO_HOR,
    .layout = PQFMT_YUV_LAYOUT_SimiPlanar,
    .order = PQFMT_ORDER_YVU,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pqfmt_yuv_desc_s g_yuv_desc_yuv420sp_nv15 = {
    .sampling = PQFMT_YUV_SAMPLING_420,
    .uv_sample_ratio_ver = PQFMT_YUV420_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PQFMT_YUV420_SAMPLE_RATIO_HOR,
    .layout = PQFMT_YUV_LAYOUT_SimiPlanar,
    .order = PQFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pqfmt_yuv_desc_s g_yuv_desc_yuv410p_yuv9 = {
    .sampling = PQFMT_YUV_SAMPLING_410,
    .uv_sample_ratio_ver = PQFMT_YUV410_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PQFMT_YUV410_SAMPLE_RATIO_HOR,
    .layout = PQFMT_YUV_LAYOUT_Planar,
    .order = PQFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pqfmt_yuv_desc_s g_yuv_desc_yuv410p_yvu9 = {
    .sampling = PQFMT_YUV_SAMPLING_410,
    .uv_sample_ratio_ver = PQFMT_YUV410_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PQFMT_YUV410_SAMPLE_RATIO_HOR,
    .layout = PQFMT_YUV_LAYOUT_Planar,
    .order = PQFMT_ORDER_YVU,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pqfmt_yuv_desc_s g_yuv_desc_yuv411p_yu11 = {
    .sampling = PQFMT_YUV_SAMPLING_411,
    .uv_sample_ratio_ver = PQFMT_YUV411_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PQFMT_YUV411_SAMPLE_RATIO_HOR,
    .layout = PQFMT_YUV_LAYOUT_Planar,
    .order = PQFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pqfmt_yuv_desc_s g_yuv_desc_yuv411p_yv11 = {
    .sampling = PQFMT_YUV_SAMPLING_411,
    .uv_sample_ratio_ver = PQFMT_YUV411_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PQFMT_YUV411_SAMPLE_RATIO_HOR,
    .layout = PQFMT_YUV_LAYOUT_Planar,
    .order = PQFMT_ORDER_YVU,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pqfmt_yuv_desc_s g_yuv_desc_yuv400_r1 = {
    .sampling = PQFMT_YUV_SAMPLING_400,
    .uv_sample_ratio_ver = PQFMT_YUV400_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PQFMT_YUV400_SAMPLE_RATIO_HOR,
    .layout = PQFMT_YUV_LAYOUT_Planar,
    .order = PQFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pqfmt_yuv_desc_s g_yuv_desc_yuv400_r2 = {
    .sampling = PQFMT_YUV_SAMPLING_400,
    .uv_sample_ratio_ver = PQFMT_YUV400_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PQFMT_YUV400_SAMPLE_RATIO_HOR,
    .layout = PQFMT_YUV_LAYOUT_Planar,
    .order = PQFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pqfmt_yuv_desc_s g_yuv_desc_yuv400_r4 = {
    .sampling = PQFMT_YUV_SAMPLING_400,
    .uv_sample_ratio_ver = PQFMT_YUV400_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PQFMT_YUV400_SAMPLE_RATIO_HOR,
    .layout = PQFMT_YUV_LAYOUT_Planar,
    .order = PQFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pqfmt_yuv_desc_s g_yuv_desc_yuv400_r8 = {
    .sampling = PQFMT_YUV_SAMPLING_400,
    .uv_sample_ratio_ver = PQFMT_YUV400_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PQFMT_YUV400_SAMPLE_RATIO_HOR,
    .layout = PQFMT_YUV_LAYOUT_Planar,
    .order = PQFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pqfmt_yuv_desc_s g_yuv_desc_yuv400_r10 = {
    .sampling = PQFMT_YUV_SAMPLING_400,
    .uv_sample_ratio_ver = PQFMT_YUV400_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PQFMT_YUV400_SAMPLE_RATIO_HOR,
    .layout = PQFMT_YUV_LAYOUT_Planar,
    .order = PQFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pqfmt_yuv_desc_s g_yuv_desc_yuv400_r12 = {
    .sampling = PQFMT_YUV_SAMPLING_400,
    .uv_sample_ratio_ver = PQFMT_YUV400_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PQFMT_YUV400_SAMPLE_RATIO_HOR,
    .layout = PQFMT_YUV_LAYOUT_Planar,
    .order = PQFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pqfmt_yuv_desc_s g_yuv_desc_yuv400_r16 = {
    .sampling = PQFMT_YUV_SAMPLING_400,
    .uv_sample_ratio_ver = PQFMT_YUV400_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PQFMT_YUV400_SAMPLE_RATIO_HOR,
    .layout = PQFMT_YUV_LAYOUT_Planar,
    .order = PQFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pqfmt_yuv_desc_s g_yuv_desc_yuv444sp_tile4x4 = {
    .sampling = PQFMT_YUV_SAMPLING_444,
    .uv_sample_ratio_ver = PQFMT_YUV444_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PQFMT_YUV444_SAMPLE_RATIO_HOR,
    .layout = PQFMT_YUV_LAYOUT_SimiPlanar,
    .order = PQFMT_ORDER_YUV,
    .is_tile = true,
    .tile_wid = 4,
    .tile_hgt = 4,
    .tile_bytes = 48,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pqfmt_yuv_desc_s g_yuv_desc_yuv422sp_tile4x4 = {
    .sampling = PQFMT_YUV_SAMPLING_422,
    .uv_sample_ratio_ver = PQFMT_YUV422_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PQFMT_YUV422_SAMPLE_RATIO_HOR,
    .layout = PQFMT_YUV_LAYOUT_SimiPlanar,
    .order = PQFMT_ORDER_YUV,
    .is_tile = true,
    .tile_wid = 4,
    .tile_hgt = 4,
    .tile_bytes = 32,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pqfmt_yuv_desc_s g_yuv_desc_yuv422i_y210 = {
    .sampling = PQFMT_YUV_SAMPLING_422,
    .uv_sample_ratio_ver = PQFMT_YUV422_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PQFMT_YUV422_SAMPLE_RATIO_HOR,
    .layout = PQFMT_YUV_LAYOUT_Interleaved,
    .order = PQFMT_ORDER_YUYV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pqfmt_yuv_desc_s g_yuv_desc_yuv420p = {
    .sampling = PQFMT_YUV_SAMPLING_420,
    .uv_sample_ratio_ver = PQFMT_YUV420_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PQFMT_YUV420_SAMPLE_RATIO_HOR,
    .layout = PQFMT_YUV_LAYOUT_Planar,
    .order = PQFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pqfmt_yuv_desc_s g_yuv_desc_yuv422p = {
    .sampling = PQFMT_YUV_SAMPLING_422,
    .uv_sample_ratio_ver = PQFMT_YUV422_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PQFMT_YUV422_SAMPLE_RATIO_HOR,
    .layout = PQFMT_YUV_LAYOUT_Planar,
    .order = PQFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pqfmt_yuv_desc_s g_yuv_desc_yuv420sp_tile4x4 = {
    .sampling = PQFMT_YUV_SAMPLING_420,
    .uv_sample_ratio_ver = PQFMT_YUV420_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PQFMT_YUV420_SAMPLE_RATIO_HOR,
    .layout = PQFMT_YUV_LAYOUT_SimiPlanar,
    .order = PQFMT_ORDER_YUV,
    .is_tile = true,
    .tile_wid = 4,
    .tile_hgt = 4,
    .tile_bytes = 24,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const char* pqfmt_yuv_sampling_name(pqfmt_yuv_sampling_e sampling) {
    switch (sampling) {
        case PQFMT_YUV_SAMPLING_444: return "444";
        case PQFMT_YUV_SAMPLING_422: return "422";
        case PQFMT_YUV_SAMPLING_420: return "420";
        case PQFMT_YUV_SAMPLING_440: return "440";
        case PQFMT_YUV_SAMPLING_410: return "410";
        case PQFMT_YUV_SAMPLING_411: return "411";
        case PQFMT_YUV_SAMPLING_400: return "400";
        default: return "Unknown";
    }
}

const char* pqfmt_yuv_layout_name(pqfmt_yuv_layout_e layout) {
    switch (layout) {
        case PQFMT_YUV_LAYOUT_Interleaved: return "Interleaved";
        case PQFMT_YUV_LAYOUT_Planar: return "Planar";
        case PQFMT_YUV_LAYOUT_SimiPlanar: return "Semi-Planar";
        default: return "Unknown";
    }
}

const char* pqfmt_uv_order_name(pqfmt_uv_order_e order) {
    switch (order) {
        case PQFMT_ORDER_YUV: return "YUV";
        case PQFMT_ORDER_YVU: return "YVU";
        case PQFMT_ORDER_YUYV: return "YUYV";
        case PQFMT_ORDER_YVYU: return "YVYU";
        case PQFMT_ORDER_UYVY: return "UYVY";
        case PQFMT_ORDER_VYUY: return "VYUY";
        default: return "Unknown";
    }
}

const char* pqfmt_tile_size_name(pqfmt_tile_size_e size) {
    switch (size) {
        case PQFMT_RASTER: return "Raster";
        case PQFMT_TILE_4X4: return "Tile4x4";
        default: return "Unknown";
    }
}

void pqfmt_yuv_desc_init(pqfmt_yuv_desc_s *desc, pqfmt_yuv_sampling_e sampling, pqfmt_yuv_layout_e layout,
    pqfmt_uv_order_e uv_order, pqfmt_tile_size_e tile_size, bool is_line_variant) {
    if (!desc) return;

    desc->sampling = sampling;
    desc->layout = layout;
    desc->order = uv_order;
    desc->is_line_variant = is_line_variant;

    desc->is_tile = (tile_size != PQFMT_RASTER);
    if (desc->is_tile) {
        switch (tile_size) {
            case PQFMT_TILE_4X4:
                desc->tile_wid = 4;
                desc->tile_hgt = 4;
                break;
            default:
                desc->tile_wid = 0;
                desc->tile_hgt = 0;
                break;
        }
    } else {
        desc->tile_wid = 0;
        desc->tile_hgt = 0;
    }

    desc->tile_bytes = 0;
    desc->tile_offset_uv = 0;
}

bool pqfmt_yuv_desc_is_valid(const pqfmt_yuv_desc_s *desc) {
    if (!desc) return false;
    return desc->sampling >= PQFMT_YUV_SAMPLING_444 && desc->sampling <= PQFMT_YUV_SAMPLING_400;
}

bool pqfmt_yuv_desc_is_uv_order(const pqfmt_yuv_desc_s *desc) {
    return desc ? desc->order == PQFMT_ORDER_YUV : false;
}

bool pqfmt_yuv_desc_is_tile(const pqfmt_yuv_desc_s *desc) {
    return desc ? desc->is_tile : false;
}

bool pqfmt_yuv_desc_is_line_variant(const pqfmt_yuv_desc_s *desc) {
    return desc ? desc->is_line_variant : false;
}

int pqfmt_yuv_desc_get_plane_count(const pqfmt_yuv_desc_s *desc) {
    if (!desc) return 0;

    switch (desc->layout) {
        case PQFMT_YUV_LAYOUT_Planar: return 3;
        case PQFMT_YUV_LAYOUT_SimiPlanar: return 2;
        case PQFMT_YUV_LAYOUT_Interleaved: return 1;
        default: return 0;
    }
}

int pqfmt_yuv_desc_get_tile_size(const pqfmt_yuv_desc_s *desc, int *tile_w, int *tile_h) {
    if (!desc) return -1;

    *tile_w = desc->tile_wid;
    *tile_h = desc->tile_hgt;
    return 0;
}

int pqfmt_yuv_desc_get_chroma_subsampling(const pqfmt_yuv_desc_s *desc, int *h_sub, int *v_sub) {
    if (!desc) return -1;

    *h_sub = desc->uv_sample_ratio_hor;
    *v_sub = desc->uv_sample_ratio_ver;
    return 0;
}

uint8_t pqfmt_yuv_desc_calc_bpp(const pqfmt_yuv_desc_s *desc) {
    if (!desc) return 0;

    switch (desc->sampling) {
        case PQFMT_YUV_SAMPLING_444: return 24;
        case PQFMT_YUV_SAMPLING_422: return 16;
        case PQFMT_YUV_SAMPLING_420: return 12;
        case PQFMT_YUV_SAMPLING_410: return 10;
        case PQFMT_YUV_SAMPLING_440: return 16;
        case PQFMT_YUV_SAMPLING_411: return 10;
        case PQFMT_YUV_SAMPLING_400: return 8;
        default: return 0;
    }
}

float pqfmt_yuv_desc_calc_pitch_ratio(const pqfmt_yuv_desc_s *desc) {
    if (!desc) return 0.0f;

    switch (desc->layout) {
        case PQFMT_YUV_LAYOUT_Planar: return 1.0f;
        case PQFMT_YUV_LAYOUT_SimiPlanar:
            if (desc->sampling == PQFMT_YUV_SAMPLING_444) return 2.0f;
            if (desc->sampling == PQFMT_YUV_SAMPLING_422) return 1.5f;
            if (desc->sampling == PQFMT_YUV_SAMPLING_420) return 1.0f;
            if (desc->sampling == PQFMT_YUV_SAMPLING_410) return 0.5f;
            if (desc->sampling == PQFMT_YUV_SAMPLING_440) return 1.5f;
            if (desc->sampling == PQFMT_YUV_SAMPLING_411) return 0.5f;
            return 0.0f;
        case PQFMT_YUV_LAYOUT_Interleaved:
            if (desc->sampling == PQFMT_YUV_SAMPLING_422) return 2.0f;
            if (desc->sampling == PQFMT_YUV_SAMPLING_444) return 3.0f;
            return 0.0f;
        default: return 0.0f;
    }
}

float pqfmt_yuv_desc_calc_framesize_ratio(const pqfmt_yuv_desc_s *desc) {
    if (!desc) return 0.0f;

    switch (desc->sampling) {
        case PQFMT_YUV_SAMPLING_444: return 3.0f;
        case PQFMT_YUV_SAMPLING_422: return 2.0f;
        case PQFMT_YUV_SAMPLING_420: return 1.5f;
        case PQFMT_YUV_SAMPLING_410: return 1.25f;
        case PQFMT_YUV_SAMPLING_440: return 2.0f;
        case PQFMT_YUV_SAMPLING_411: return 1.25f;
        case PQFMT_YUV_SAMPLING_400: return 1.0f;
        default: return 0.0f;
    }
}

uint8_t pqfmt_yuv_desc_calc_tile_bytes(const pqfmt_yuv_desc_s *desc) {
    if (!desc || !desc->is_tile) return 0;

    return (uint8_t)desc->tile_bytes;
}

size_t pqfmt_yuv_desc_calc_framesize(const pqfmt_yuv_desc_s *desc, int w, int h, int stride) {
    if (!desc) return 0;

    int pitch = stride > 0 ? stride : (int)(w * pqfmt_yuv_desc_calc_pitch_ratio(desc));
    return (size_t)(pitch * h * pqfmt_yuv_desc_calc_framesize_ratio(desc));
}

size_t pqfmt_yuv_desc_calc_planesize(const pqfmt_yuv_desc_s *desc, int plane_idx, int w, int h, int stride) {
    if (!desc) return 0;

    int pitch = stride > 0 ? stride : (int)(w * pqfmt_yuv_desc_calc_pitch_ratio(desc));
    int plane_count = pqfmt_yuv_desc_get_plane_count(desc);

    if (plane_idx >= plane_count) return 0;

    switch (desc->layout) {
        case PQFMT_YUV_LAYOUT_Planar:
            return (size_t)(pitch * h);
        case PQFMT_YUV_LAYOUT_SimiPlanar:
            if (plane_idx == 0) return (size_t)(pitch * h);
            return (size_t)(pitch * h / desc->uv_sample_ratio_ver / desc->uv_sample_ratio_hor);
        case PQFMT_YUV_LAYOUT_Interleaved:
            return (size_t)(pitch * h);
        default:
            return 0;
    }
}

bool pqfmt_yuv_desc_equal(const pqfmt_yuv_desc_s *desc1, const pqfmt_yuv_desc_s *desc2) {
    if (!desc1 || !desc2) return false;

    return desc1->sampling == desc2->sampling &&
           desc1->layout == desc2->layout &&
           desc1->order == desc2->order &&
           desc1->is_tile == desc2->is_tile &&
           desc1->is_line_variant == desc2->is_line_variant;
}

void pqfmt_yuv_desc_print(const pqfmt_yuv_desc_s *desc) {
    if (!desc) {
        printf("YUV Format: NULL\n");
        return;
    }

    printf("YUV Format:\n");
    printf("  Sampling: %s\n", pqfmt_yuv_sampling_name(desc->sampling));
    printf("  Layout: %s\n", pqfmt_yuv_layout_name(desc->layout));
    printf("  Order: %s\n", pqfmt_uv_order_name(desc->order));
    printf("  Tile: %s\n", desc->is_tile ? "Yes" : "No");
    if (desc->is_tile) {
        printf("  TileSize: %dx%d, Bytes: %d\n", desc->tile_wid, desc->tile_hgt, desc->tile_bytes);
    }
    printf("  LineVariant: %s\n", desc->is_line_variant ? "Yes" : "No");
    printf("  UV Ratio: V%d H%d\n", desc->uv_sample_ratio_ver, desc->uv_sample_ratio_hor);
}
