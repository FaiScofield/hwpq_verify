/**
 * @copyright: Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @brief:     YUV format descriptor implementation
 * @author:    vance.wu@rock-chips.com
 * @create:    2026-04-16
 */

#include "pixfmt_yuv.h"
#include "pixfmt.h"
#include "verify_com.h"

#include <stdio.h>
#include <string.h>
#include <assert.h>
// #include <math.h>

const pixfmt_yuv_desc_s g_yuv_desc_yuv444i_vu24 = {
    .sampling = PIXFMT_YUV_SAMPLING_444,
    .uv_sample_ratio_ver = PIXFMT_YUV444_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV444_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv444i_vu30 = {
    .sampling = PIXFMT_YUV_SAMPLING_444,
    .uv_sample_ratio_ver = PIXFMT_YUV444_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV444_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv444i_xv30 = {
    .sampling = PIXFMT_YUV_SAMPLING_444,
    .uv_sample_ratio_ver = PIXFMT_YUV444_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV444_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_UYV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv444p_yu24 = {
    .sampling = PIXFMT_YUV_SAMPLING_444,
    .uv_sample_ratio_ver = PIXFMT_YUV444_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV444_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv444p_yv24 = {
    .sampling = PIXFMT_YUV_SAMPLING_444,
    .uv_sample_ratio_ver = PIXFMT_YUV444_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV444_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_YVU,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv444sp_nv24 = {
    .sampling = PIXFMT_YUV_SAMPLING_444,
    .uv_sample_ratio_ver = PIXFMT_YUV444_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV444_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv444sp_nv42 = {
    .sampling = PIXFMT_YUV_SAMPLING_444,
    .uv_sample_ratio_ver = PIXFMT_YUV444_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV444_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_YVU,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv444sp_nv30 = {
    .sampling = PIXFMT_YUV_SAMPLING_444,
    .uv_sample_ratio_ver = PIXFMT_YUV444_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV444_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv444i_10lsb = {
    .sampling = PIXFMT_YUV_SAMPLING_444,
    .uv_sample_ratio_ver = PIXFMT_YUV444_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV444_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv444p_10lsb = {
    .sampling = PIXFMT_YUV_SAMPLING_444,
    .uv_sample_ratio_ver = PIXFMT_YUV444_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV444_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv444sp_10lsb = {
    .sampling = PIXFMT_YUV_SAMPLING_444,
    .uv_sample_ratio_ver = PIXFMT_YUV444_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV444_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv422i_yuyv = {
    .sampling = PIXFMT_YUV_SAMPLING_422,
    .uv_sample_ratio_ver = PIXFMT_YUV422_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV422_SAMPLE_RATIO_HOR,

    .order = PIXFMT_ORDER_YUYV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv422i_yvyu = {
    .sampling = PIXFMT_YUV_SAMPLING_422,
    .uv_sample_ratio_ver = PIXFMT_YUV422_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV422_SAMPLE_RATIO_HOR,

    .order = PIXFMT_ORDER_YVYU,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv422i_uyvy = {
    .sampling = PIXFMT_YUV_SAMPLING_422,
    .uv_sample_ratio_ver = PIXFMT_YUV422_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV422_SAMPLE_RATIO_HOR,

    .order = PIXFMT_ORDER_UYVY,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv422i_vyuy = {
    .sampling = PIXFMT_YUV_SAMPLING_422,
    .uv_sample_ratio_ver = PIXFMT_YUV422_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV422_SAMPLE_RATIO_HOR,

    .order = PIXFMT_ORDER_VYUY,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv422p_yu16 = {
    .sampling = PIXFMT_YUV_SAMPLING_422,
    .uv_sample_ratio_ver = PIXFMT_YUV422_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV422_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv422p_yv16 = {
    .sampling = PIXFMT_YUV_SAMPLING_422,
    .uv_sample_ratio_ver = PIXFMT_YUV422_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV422_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_YVU,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv422sp_nv16 = {
    .sampling = PIXFMT_YUV_SAMPLING_422,
    .uv_sample_ratio_ver = PIXFMT_YUV422_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV422_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv422sp_nv61 = {
    .sampling = PIXFMT_YUV_SAMPLING_422,
    .uv_sample_ratio_ver = PIXFMT_YUV422_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV422_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_YVU,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv422sp_nv20 = {
    .sampling = PIXFMT_YUV_SAMPLING_422,
    .uv_sample_ratio_ver = PIXFMT_YUV422_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV422_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv422p_10lsb = {
    .sampling = PIXFMT_YUV_SAMPLING_422,
    .uv_sample_ratio_ver = PIXFMT_YUV422_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV422_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv422sp_10lsb = {
    .sampling = PIXFMT_YUV_SAMPLING_422,
    .uv_sample_ratio_ver = PIXFMT_YUV422_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV422_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv420p_yu12 = {
    .sampling = PIXFMT_YUV_SAMPLING_420,
    .uv_sample_ratio_ver = PIXFMT_YUV420_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV420_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv420p_yv12 = {
    .sampling = PIXFMT_YUV_SAMPLING_420,
    .uv_sample_ratio_ver = PIXFMT_YUV420_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV420_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_YVU,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv420sp_nv12 = {
    .sampling = PIXFMT_YUV_SAMPLING_420,
    .uv_sample_ratio_ver = PIXFMT_YUV420_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV420_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv420sp_nv21 = {
    .sampling = PIXFMT_YUV_SAMPLING_420,
    .uv_sample_ratio_ver = PIXFMT_YUV420_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV420_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_YVU,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv420sp_nv15 = {
    .sampling = PIXFMT_YUV_SAMPLING_420,
    .uv_sample_ratio_ver = PIXFMT_YUV420_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV420_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv420p_10lsb = {
    .sampling = PIXFMT_YUV_SAMPLING_420,
    .uv_sample_ratio_ver = PIXFMT_YUV420_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV420_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv420sp_10lsb = {
    .sampling = PIXFMT_YUV_SAMPLING_420,
    .uv_sample_ratio_ver = PIXFMT_YUV420_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV420_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv410p_yuv9 = {
    .sampling = PIXFMT_YUV_SAMPLING_410,
    .uv_sample_ratio_ver = PIXFMT_YUV410_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV410_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv410p_yvu9 = {
    .sampling = PIXFMT_YUV_SAMPLING_410,
    .uv_sample_ratio_ver = PIXFMT_YUV410_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV410_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_YVU,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv411p_yu11 = {
    .sampling = PIXFMT_YUV_SAMPLING_411,
    .uv_sample_ratio_ver = PIXFMT_YUV411_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV411_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv411p_yv11 = {
    .sampling = PIXFMT_YUV_SAMPLING_411,
    .uv_sample_ratio_ver = PIXFMT_YUV411_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV411_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_YVU,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv400_r1 = {
    .sampling = PIXFMT_YUV_SAMPLING_400,
    .uv_sample_ratio_ver = PIXFMT_YUV400_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV400_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv400_r2 = {
    .sampling = PIXFMT_YUV_SAMPLING_400,
    .uv_sample_ratio_ver = PIXFMT_YUV400_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV400_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv400_r4 = {
    .sampling = PIXFMT_YUV_SAMPLING_400,
    .uv_sample_ratio_ver = PIXFMT_YUV400_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV400_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv400_r8 = {
    .sampling = PIXFMT_YUV_SAMPLING_400,
    .uv_sample_ratio_ver = PIXFMT_YUV400_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV400_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv400_r10 = {
    .sampling = PIXFMT_YUV_SAMPLING_400,
    .uv_sample_ratio_ver = PIXFMT_YUV400_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV400_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv400_r12 = {
    .sampling = PIXFMT_YUV_SAMPLING_400,
    .uv_sample_ratio_ver = PIXFMT_YUV400_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV400_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv400_r16 = {
    .sampling = PIXFMT_YUV_SAMPLING_400,
    .uv_sample_ratio_ver = PIXFMT_YUV400_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV400_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv444sp_tile4x4 = {
    .sampling = PIXFMT_YUV_SAMPLING_444,
    .uv_sample_ratio_ver = PIXFMT_YUV444_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV444_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_YUV,
    .is_tile = true,
    .tile_wid = 4,
    .tile_hgt = 4,
    .tile_bytes = 48,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv422sp_tile4x4 = {
    .sampling = PIXFMT_YUV_SAMPLING_422,
    .uv_sample_ratio_ver = PIXFMT_YUV422_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV422_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_YUV,
    .is_tile = true,
    .tile_wid = 4,
    .tile_hgt = 4,
    .tile_bytes = 32,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv422i_y210 = {
    .sampling = PIXFMT_YUV_SAMPLING_422,
    .uv_sample_ratio_ver = PIXFMT_YUV422_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV422_SAMPLE_RATIO_HOR,

    .order = PIXFMT_ORDER_YUYV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv420p = {
    .sampling = PIXFMT_YUV_SAMPLING_420,
    .uv_sample_ratio_ver = PIXFMT_YUV420_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV420_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv422p = {
    .sampling = PIXFMT_YUV_SAMPLING_422,
    .uv_sample_ratio_ver = PIXFMT_YUV422_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV422_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_YUV,
    .is_tile = false,
    .tile_wid = 0,
    .tile_hgt = 0,
    .tile_bytes = 0,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const pixfmt_yuv_desc_s g_yuv_desc_yuv420sp_tile4x4 = {
    .sampling = PIXFMT_YUV_SAMPLING_420,
    .uv_sample_ratio_ver = PIXFMT_YUV420_SAMPLE_RATIO_VER,
    .uv_sample_ratio_hor = PIXFMT_YUV420_SAMPLE_RATIO_HOR,
    .order = PIXFMT_ORDER_YUV,
    .is_tile = true,
    .tile_wid = 4,
    .tile_hgt = 4,
    .tile_bytes = 24,
    .tile_offset_uv = 0,
    .is_line_variant = false,
};

const char *pixfmt_yuv_sampling_name(pixfmt_yuv_sampling_e sampling)
{
    switch (sampling) {
    case PIXFMT_YUV_SAMPLING_444: return "444";
    case PIXFMT_YUV_SAMPLING_422: return "422";
    case PIXFMT_YUV_SAMPLING_420: return "420";
    case PIXFMT_YUV_SAMPLING_440: return "440";
    case PIXFMT_YUV_SAMPLING_410: return "410";
    case PIXFMT_YUV_SAMPLING_411: return "411";
    case PIXFMT_YUV_SAMPLING_400: return "400";
    default:                      return "UnknownSampling";
    }
}

const char *pixfmt_uv_order_name(pixfmt_uv_order_e order)
{
    switch (order) {
    case PIXFMT_ORDER_YUV:  return "YUV";
    case PIXFMT_ORDER_YVU:  return "YVU";
    case PIXFMT_ORDER_UYV:  return "UYV";
    case PIXFMT_ORDER_VYU:  return "VYU";
    case PIXFMT_ORDER_YUYV: return "YUYV";
    case PIXFMT_ORDER_YVYU: return "YVYU";
    case PIXFMT_ORDER_UYVY: return "UYVY";
    case PIXFMT_ORDER_VYUY: return "VYUY";
    default:                return "Unknown";
    }
}

bool pixfmt_yuv_desc_is_valid(const pixfmt_yuv_desc_s *desc)
{
    if (!desc)
        return false;
    return desc->sampling >= PIXFMT_YUV_SAMPLING_444 && desc->sampling <= PIXFMT_YUV_SAMPLING_400;
}

bool pixfmt_yuv_desc_is_uv_order(const pixfmt_yuv_desc_s *desc)
{
    return desc ? desc->order == PIXFMT_ORDER_YUV : false;
}

bool pixfmt_yuv_desc_is_tile(const pixfmt_yuv_desc_s *desc) { return desc ? desc->is_tile : false; }

bool pixfmt_yuv_desc_is_line_variant(const pixfmt_yuv_desc_s *desc) { return desc ? desc->is_line_variant : false; }

int pixfmt_yuv_desc_get_tile_size(const pixfmt_yuv_desc_s *desc, int *tile_w, int *tile_h)
{
    if (!desc)
        return -1;

    *tile_w = desc->tile_wid;
    *tile_h = desc->tile_hgt;
    return 0;
}

int pixfmt_yuv_desc_get_chroma_subsampling(const pixfmt_yuv_desc_s *desc, int *h_sub, int *v_sub)
{
    if (!desc)
        return -1;

    *h_sub = desc->uv_sample_ratio_hor;
    *v_sub = desc->uv_sample_ratio_ver;
    return 0;
}

uint8_t pixfmt_yuv_desc_calc_bpp(const pixfmt_yuv_desc_s *desc)
{
    if (!desc)
        return 0;

    switch (desc->sampling) {
    case PIXFMT_YUV_SAMPLING_444: return 24;
    case PIXFMT_YUV_SAMPLING_422: return 16;
    case PIXFMT_YUV_SAMPLING_420: return 12;
    case PIXFMT_YUV_SAMPLING_410: return 10;
    case PIXFMT_YUV_SAMPLING_440: return 16;
    case PIXFMT_YUV_SAMPLING_411: return 10;
    case PIXFMT_YUV_SAMPLING_400: return 8;
    default:                      return 0;
    }
}

int pixfmt_yuv_get_min_align_width(const pixfmt_attr_s *attr, int wid, int *retAlign)
{
    assert(attr && attr->base_type == PIXFMT_TYPE_YUV);

    const pixfmt_yuv_desc_s *desc = attr->desc.yuv;
    int align = 1;

    if (attr->layout == PIXFMT_LAYOUT_TILE) {
        align = desc->tile_wid;
    }
    else if (attr->is_bitpacked) {
        /**
         * for bitpacked formats, most of them must have an align width
         * interleaved: VU30/XV30, bpp=30/32
         * semi-planar: NV30/NV20/NV15, depth=10/10/10
         * planar: R1/R2/R4, depth=1/2/4
         */
        switch (attr->fmt_id) {
        case PIXFMT_YUV444I_VU30:  align = 4; break;
        case PIXFMT_YUV444I_XV30:  break; // no need to align
        case PIXFMT_YUV444SP_NV30:
        case PIXFMT_YUV422SP_NV20:
        case PIXFMT_YUV420SP_NV15: align = 4; break;
        case PIXFMT_YUV400_R1:     align = 8; break;
        case PIXFMT_YUV400_R2:     align = 4; break;
        case PIXFMT_YUV400_R4:     align = 2; break;
        default:                   break;
        }
    }
    else if (attr->layout == PIXFMT_LAYOUT_SEMIPLANAR) {
        // no YUV400 included
        align = desc->uv_sample_ratio_hor;
    }

    wid = ALIGN_N_DIV(wid, align);

    if (retAlign)
        *retAlign = align;

    return wid;
}

int pixfmt_yuv_get_min_align_height(const pixfmt_attr_s *attr, int hgt, int *retAlign)
{
    assert(attr && attr->base_type == PIXFMT_TYPE_YUV);

    const pixfmt_yuv_desc_s *desc = attr->desc.yuv;
    int align = 1;

    if (attr->layout == PIXFMT_LAYOUT_TILE) {
        align = desc->tile_hgt;
    }
    else if (attr->layout == PIXFMT_LAYOUT_INTERLEAVED || desc->sampling == PIXFMT_YUV_SAMPLING_400) {
        align = 1;
    }
    else if (attr->layout == PIXFMT_LAYOUT_SEMIPLANAR || attr->layout == PIXFMT_LAYOUT_PLANAR) {
        // no YUV400 included
        align = desc->uv_sample_ratio_ver;
    }

    hgt = ALIGN_N_DIV(hgt, align);

    if (retAlign)
        *retAlign = align;

    return hgt;
}

int pixfmt_yuv_get_min_pitches(const pixfmt_attr_s *attr, int wid, int *retPitchesx3)
{
    assert(attr && attr->base_type == PIXFMT_TYPE_YUV && attr->desc.yuv);
    assert(retPitchesx3 != NULL);

    // get align width first
    wid = pixfmt_yuv_get_min_align_width(attr, wid, NULL);

    if (PIXFMT_LAYOUT_INTERLEAVED == attr->layout) {
        retPitchesx3[0] = attr->bpp * wid / 8;
        retPitchesx3[1] = retPitchesx3[2] = 0;
    }
    else {
        switch (attr->desc.yuv->sampling) {
        case PIXFMT_YUV_SAMPLING_444: {
            retPitchesx3[0] = attr->bpp / 3 * wid / 8;
            retPitchesx3[1] = retPitchesx3[2] = (PIXFMT_LAYOUT_SEMIPLANAR == attr->layout) ? retPitchesx3[0] * 2
                                                                                           : retPitchesx3[0];
        } break;
        case PIXFMT_YUV_SAMPLING_422: {
            retPitchesx3[0] = attr->bpp / 2 * wid / 8;
            retPitchesx3[1] = retPitchesx3[2] = (PIXFMT_LAYOUT_SEMIPLANAR == attr->layout) ? retPitchesx3[0] * 2
                                                                                           : retPitchesx3[0];
        } break;
        case PIXFMT_YUV_SAMPLING_420: {
            retPitchesx3[0] = attr->bpp * 2 / 3 * wid / 8;
            retPitchesx3[1] = retPitchesx3[2] = (PIXFMT_LAYOUT_SEMIPLANAR == attr->layout) ? retPitchesx3[0]
                                                                                           : retPitchesx3[0] / 2;
        } break;
        case PIXFMT_YUV_SAMPLING_411: {
            retPitchesx3[0] = attr->bpp * 2 / 3 * wid / 8;
            retPitchesx3[1] = retPitchesx3[2] = (PIXFMT_LAYOUT_SEMIPLANAR == attr->layout) ? retPitchesx3[0] / 2
                                                                                           : retPitchesx3[0] / 4;
        } break;
        case PIXFMT_YUV_SAMPLING_410: {
            retPitchesx3[0] = attr->bpp * 8 / 9 * wid / 8;
            retPitchesx3[1] = retPitchesx3[2] = (PIXFMT_LAYOUT_SEMIPLANAR == attr->layout) ? retPitchesx3[0] / 2
                                                                                           : retPitchesx3[0] / 4;
        } break;
        case PIXFMT_YUV_SAMPLING_400: {
            retPitchesx3[0] = attr->bpp * wid / 8;
            retPitchesx3[1] = retPitchesx3[2] = 0;
        } break;
        default: return PIXFMT_INVALID;
        }
    }

    return 0;
}

size_t pixfmt_yuv_get_framesize(const pixfmt_attr_s *attr, int w, int h, int rowpitch, size_t *retPlaneSizesx3)
{
    assert(attr && attr->base_type == PIXFMT_TYPE_YUV);

    const pixfmt_yuv_desc_s *desc = attr->desc.yuv;
    size_t size = 0;

    if (desc->is_tile) {
        int nb_tile_w = (w + desc->tile_wid - 1) / desc->tile_wid;
        int nb_tile_h = (h + desc->tile_hgt - 1) / desc->tile_hgt;
        size = desc->tile_bytes * nb_tile_w * nb_tile_h;
    }
    else {
        int alignment = 1;
        int real_wid = w;
        int align_wid = pixfmt_yuv_get_min_align_width(attr, w, &alignment);
        int align_pitches[3] = {0};
        pixfmt_yuv_get_min_pitches(attr, w, align_pitches);

        if (rowpitch < align_pitches[0]) {
            if (rowpitch > 0) {
                LOGW("rowpitch %d is not valid with w=%d, fmt=%d, need %d at least!", rowpitch, w, attr->fmt_id,
                    align_pitches[0]);
            }
            real_wid = w;
        }
        else {
            if (rowpitch % alignment != 0) {
                LOGW("rowpitch %d is not valid with w=%d, fmt=%d, need to align to %d!", rowpitch, w, attr->fmt_id, alignment);
            }
            rowpitch = ALIGN_N_DIV(rowpitch, alignment);
            real_wid = rowpitch * w / align_pitches[0];
        }

        size = real_wid * h * attr->bpp / 8;
    }

    /* get all plane sizes */
    if (retPlaneSizesx3) {
        int chroma_ratio = desc->uv_sample_ratio_ver * desc->uv_sample_ratio_hor + 2;
        size_t chroma_size = size / chroma_ratio;
        size_t luma_size = size - chroma_size;

        if (PIXFMT_LAYOUT_INTERLEAVED == attr->layout || PIXFMT_LAYOUT_TILE == attr->layout ||
            PIXFMT_YUV_SAMPLING_400 == desc->sampling)
        {
            retPlaneSizesx3[0] = size;
            retPlaneSizesx3[1] = retPlaneSizesx3[2] = 0;
        }
        if (PIXFMT_LAYOUT_PLANAR == attr->layout) {
            retPlaneSizesx3[0] = luma_size;
            retPlaneSizesx3[1] = retPlaneSizesx3[2] = chroma_size;
        }
        else if (PIXFMT_LAYOUT_SEMIPLANAR == attr->layout) {
            retPlaneSizesx3[0] = luma_size;
            retPlaneSizesx3[1] = chroma_size * 2;
            retPlaneSizesx3[2] = 0;
        }
    }

    return size;
}

uint8_t pixfmt_yuv_desc_calc_tile_bytes(const pixfmt_yuv_desc_s *desc)
{
    if (!desc || !desc->is_tile)
        return 0;

    return (uint8_t)desc->tile_bytes;
}

bool pixfmt_yuv_desc_equal(const pixfmt_yuv_desc_s *desc1, const pixfmt_yuv_desc_s *desc2)
{
    if (!desc1 || !desc2)
        return false;

    return desc1->sampling == desc2->sampling && desc1->order == desc2->order && desc1->is_tile == desc2->is_tile &&
           desc1->tile_wid == desc2->tile_wid && desc1->tile_hgt == desc2->tile_hgt &&
           desc1->tile_bytes == desc2->tile_bytes && desc1->tile_offset_uv == desc2->tile_offset_uv &&
           desc1->is_line_variant == desc2->is_line_variant;
}

void pixfmt_yuv_desc_print(const pixfmt_yuv_desc_s *desc)
{
    if (!desc) {
        printf("YUV Format: NULL\n");
        return;
    }

    printf("YUV Format:\n");
    printf("  Sampling: %s\n", pixfmt_yuv_sampling_name(desc->sampling));
    printf("  Order: %s\n", pixfmt_uv_order_name(desc->order));
    printf("  Tile: %s\n", desc->is_tile ? "Yes" : "No");
    if (desc->is_tile) {
        printf("  TileSize: %dx%d, Bytes: %d, Offset: %d\n", desc->tile_wid, desc->tile_hgt, desc->tile_bytes,
            desc->tile_offset_uv);
    }
    printf("  LineVariant: %s\n", desc->is_line_variant ? "Yes" : "No");
    printf("  UV Ratio: V%d H%d\n", desc->uv_sample_ratio_ver, desc->uv_sample_ratio_hor);
}
