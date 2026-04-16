/**
 * @copyright: Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @brief:     YUV 格式描述符实现
 * @author:
 * @create:    2026-04-16
 */

#include "pqfmt_yuv.h"
#include <string.h>
#include <math.h>

const pqfmt_yuv_desc_s g_yuv_fmt_yuv444p = {
    .layout = PQFMT_YUV_LAYOUT_Planar,
    .sampling = PQFMT_YUV_SAMPLING_444,
    .uv_sample_ratio_ver = 1,
    .uv_sample_ratio_hor = 1,
    .order = {.uv_order = PQFMT_UV_ORDER_UV},
    .packing = PQFMT_PACKING_UNPACKED,
    .line_variant = PQFMT_LINE_UNIFORM,
    .tile_size = PQFMT_RASTER,
    .depth_y = 8,
    .depth_uv = 8,
    .has_packing = false,
    .has_padding = false,
    .format_info = {.subsampling = {.chroma_h_sub = 1, .chroma_v_sub = 1}},
};

const pqfmt_yuv_desc_s g_yuv_fmt_yuv444sp_nv24 = {
    .layout = PQFMT_YUV_LAYOUT_SimiPlanar,
    .sampling = PQFMT_YUV_SAMPLING_444,
    .uv_sample_ratio_ver = 1,
    .uv_sample_ratio_hor = 1,
    .order = {.uv_order = PQFMT_UV_ORDER_UV},
    .packing = PQFMT_PACKING_UNPACKED,
    .line_variant = PQFMT_LINE_UNIFORM,
    .tile_size = PQFMT_RASTER,
    .depth_y = 8,
    .depth_uv = 8,
    .has_packing = false,
    .has_padding = false,
    .format_info = {.subsampling = {.chroma_h_sub = 1, .chroma_v_sub = 1}},
};

const pqfmt_yuv_desc_s g_yuv_fmt_yuv444sp_nv42 = {
    .layout = PQFMT_YUV_LAYOUT_SimiPlanar,
    .sampling = PQFMT_YUV_SAMPLING_444,
    .uv_sample_ratio_ver = 1,
    .uv_sample_ratio_hor = 1,
    .order = {.uv_order = PQFMT_UV_ORDER_VU},
    .packing = PQFMT_PACKING_UNPACKED,
    .line_variant = PQFMT_LINE_UNIFORM,
    .tile_size = PQFMT_RASTER,
    .depth_y = 8,
    .depth_uv = 8,
    .has_packing = false,
    .has_padding = false,
    .format_info = {.subsampling = {.chroma_h_sub = 1, .chroma_v_sub = 1}},
};

const pqfmt_yuv_desc_s g_yuv_fmt_yuv444i = {
    .layout = PQFMT_YUV_LAYOUT_Interleaved,
    .sampling = PQFMT_YUV_SAMPLING_444,
    .uv_sample_ratio_ver = 1,
    .uv_sample_ratio_hor = 1,
    .order = {.uv_order = PQFMT_UV_ORDER_UV},
    .packing = PQFMT_PACKING_UNPACKED,
    .line_variant = PQFMT_LINE_UNIFORM,
    .tile_size = PQFMT_RASTER,
    .depth_y = 8,
    .depth_uv = 8,
    .has_packing = false,
    .has_padding = false,
    .format_info = {.subsampling = {.chroma_h_sub = 1, .chroma_v_sub = 1}},
};

const pqfmt_yuv_desc_s g_yuv_fmt_yuv422p = {
    .layout = PQFMT_YUV_LAYOUT_Planar,
    .sampling = PQFMT_YUV_SAMPLING_422,
    .uv_sample_ratio_ver = 1,
    .uv_sample_ratio_hor = 2,
    .order = {.uv_order = PQFMT_UV_ORDER_UV},
    .packing = PQFMT_PACKING_UNPACKED,
    .line_variant = PQFMT_LINE_UNIFORM,
    .tile_size = PQFMT_RASTER,
    .depth_y = 8,
    .depth_uv = 8,
    .has_packing = false,
    .has_padding = false,
    .format_info = {.subsampling = {.chroma_h_sub = 2, .chroma_v_sub = 1}},
};

const pqfmt_yuv_desc_s g_yuv_fmt_yuv422sp_nv16 = {
    .layout = PQFMT_YUV_LAYOUT_SimiPlanar,
    .sampling = PQFMT_YUV_SAMPLING_422,
    .uv_sample_ratio_ver = 1,
    .uv_sample_ratio_hor = 2,
    .order = {.uv_order = PQFMT_UV_ORDER_UV},
    .packing = PQFMT_PACKING_UNPACKED,
    .line_variant = PQFMT_LINE_UNIFORM,
    .tile_size = PQFMT_RASTER,
    .depth_y = 8,
    .depth_uv = 8,
    .has_packing = false,
    .has_padding = false,
    .format_info = {.subsampling = {.chroma_h_sub = 2, .chroma_v_sub = 1}},
};

const pqfmt_yuv_desc_s g_yuv_fmt_yuv422sp_nv61 = {
    .layout = PQFMT_YUV_LAYOUT_SimiPlanar,
    .sampling = PQFMT_YUV_SAMPLING_422,
    .uv_sample_ratio_ver = 1,
    .uv_sample_ratio_hor = 2,
    .order = {.uv_order = PQFMT_UV_ORDER_VU},
    .packing = PQFMT_PACKING_UNPACKED,
    .line_variant = PQFMT_LINE_UNIFORM,
    .tile_size = PQFMT_RASTER,
    .depth_y = 8,
    .depth_uv = 8,
    .has_packing = false,
    .has_padding = false,
    .format_info = {.subsampling = {.chroma_h_sub = 2, .chroma_v_sub = 1}},
};

const pqfmt_yuv_desc_s g_yuv_fmt_yuv422i_yuyv = {
    .layout = PQFMT_YUV_LAYOUT_Interleaved,
    .sampling = PQFMT_YUV_SAMPLING_422,
    .uv_sample_ratio_ver = 1,
    .uv_sample_ratio_hor = 2,
    .order = {.uv_order = PQFMT_UV_ORDER_UV},
    .packing = PQFMT_PACKING_UNPACKED,
    .line_variant = PQFMT_LINE_UNIFORM,
    .tile_size = PQFMT_RASTER,
    .depth_y = 8,
    .depth_uv = 8,
    .has_packing = false,
    .has_padding = false,
    .format_info = {.subsampling = {.chroma_h_sub = 2, .chroma_v_sub = 1}},
};

const pqfmt_yuv_desc_s g_yuv_fmt_yuv422i_yvyu = {
    .layout = PQFMT_YUV_LAYOUT_Interleaved,
    .sampling = PQFMT_YUV_SAMPLING_422,
    .uv_sample_ratio_ver = 1,
    .uv_sample_ratio_hor = 2,
    .order = {.uv_order = PQFMT_UV_ORDER_VU},
    .packing = PQFMT_PACKING_UNPACKED,
    .line_variant = PQFMT_LINE_UNIFORM,
    .tile_size = PQFMT_RASTER,
    .depth_y = 8,
    .depth_uv = 8,
    .has_packing = false,
    .has_padding = false,
    .format_info = {.subsampling = {.chroma_h_sub = 2, .chroma_v_sub = 1}},
};

const pqfmt_yuv_desc_s g_yuv_fmt_yuv422i_uyvy = {
    .layout = PQFMT_YUV_LAYOUT_Interleaved,
    .sampling = PQFMT_YUV_SAMPLING_422,
    .uv_sample_ratio_ver = 1,
    .uv_sample_ratio_hor = 2,
    .order = {.uv_order = PQFMT_UV_ORDER_UV},
    .packing = PQFMT_PACKING_UNPACKED,
    .line_variant = PQFMT_LINE_UNIFORM,
    .tile_size = PQFMT_RASTER,
    .depth_y = 8,
    .depth_uv = 8,
    .has_packing = false,
    .has_padding = false,
    .format_info = {.subsampling = {.chroma_h_sub = 2, .chroma_v_sub = 1}},
};

const pqfmt_yuv_desc_s g_yuv_fmt_yuv422i_vyuy = {
    .layout = PQFMT_YUV_LAYOUT_Interleaved,
    .sampling = PQFMT_YUV_SAMPLING_422,
    .uv_sample_ratio_ver = 1,
    .uv_sample_ratio_hor = 2,
    .order = {.uv_order = PQFMT_UV_ORDER_UV},
    .packing = PQFMT_PACKING_UNPACKED,
    .line_variant = PQFMT_LINE_UNIFORM,
    .tile_size = PQFMT_RASTER,
    .depth_y = 8,
    .depth_uv = 8,
    .has_packing = false,
    .has_padding = false,
    .format_info = {.subsampling = {.chroma_h_sub = 2, .chroma_v_sub = 1}},
};

const pqfmt_yuv_desc_s g_yuv_fmt_yuv420p = {
    .layout = PQFMT_YUV_LAYOUT_Planar,
    .sampling = PQFMT_YUV_SAMPLING_420,
    .uv_sample_ratio_ver = 2,
    .uv_sample_ratio_hor = 2,
    .order = {.uv_order = PQFMT_UV_ORDER_UV},
    .packing = PQFMT_PACKING_UNPACKED,
    .line_variant = PQFMT_LINE_UNIFORM,
    .tile_size = PQFMT_RASTER,
    .depth_y = 8,
    .depth_uv = 8,
    .has_packing = false,
    .has_padding = false,
    .format_info = {.subsampling = {.chroma_h_sub = 2, .chroma_v_sub = 2}},
};

const pqfmt_yuv_desc_s g_yuv_fmt_yuv420sp_nv12 = {
    .layout = PQFMT_YUV_LAYOUT_SimiPlanar,
    .sampling = PQFMT_YUV_SAMPLING_420,
    .uv_sample_ratio_ver = 2,
    .uv_sample_ratio_hor = 2,
    .order = {.uv_order = PQFMT_UV_ORDER_UV},
    .packing = PQFMT_PACKING_UNPACKED,
    .line_variant = PQFMT_LINE_UNIFORM,
    .tile_size = PQFMT_RASTER,
    .depth_y = 8,
    .depth_uv = 8,
    .has_packing = false,
    .has_padding = false,
    .format_info = {.subsampling = {.chroma_h_sub = 2, .chroma_v_sub = 2}},
};

const pqfmt_yuv_desc_s g_yuv_fmt_yuv420sp_nv21 = {
    .layout = PQFMT_YUV_LAYOUT_SimiPlanar,
    .sampling = PQFMT_YUV_SAMPLING_420,
    .uv_sample_ratio_ver = 2,
    .uv_sample_ratio_hor = 2,
    .order = {.uv_order = PQFMT_UV_ORDER_VU},
    .packing = PQFMT_PACKING_UNPACKED,
    .line_variant = PQFMT_LINE_UNIFORM,
    .tile_size = PQFMT_RASTER,
    .depth_y = 8,
    .depth_uv = 8,
    .has_packing = false,
    .has_padding = false,
    .format_info = {.subsampling = {.chroma_h_sub = 2, .chroma_v_sub = 2}},
};

const pqfmt_yuv_desc_s g_yuv_fmt_yuv420sp_nv15 = {
    .layout = PQFMT_YUV_LAYOUT_SimiPlanar,
    .sampling = PQFMT_YUV_SAMPLING_420,
    .uv_sample_ratio_ver = 2,
    .uv_sample_ratio_hor = 2,
    .order = {.uv_order = PQFMT_UV_ORDER_UV},
    .packing = PQFMT_PACKING_PACKED,
    .line_variant = PQFMT_LINE_UNIFORM,
    .tile_size = PQFMT_RASTER,
    .depth_y = 8,
    .depth_uv = 10,
    .has_packing = true,
    .has_padding = false,
    .format_info = {.subsampling = {.chroma_h_sub = 2, .chroma_v_sub = 2}},
};

const pqfmt_yuv_desc_s g_yuv_fmt_yuv420sp_p010 = {
    .layout = PQFMT_YUV_LAYOUT_SimiPlanar,
    .sampling = PQFMT_YUV_SAMPLING_420,
    .uv_sample_ratio_ver = 2,
    .uv_sample_ratio_hor = 2,
    .order = {.uv_order = PQFMT_UV_ORDER_UV},
    .packing = PQFMT_PACKING_MSB,
    .line_variant = PQFMT_LINE_UNIFORM,
    .tile_size = PQFMT_RASTER,
    .depth_y = 10,
    .depth_uv = 10,
    .has_packing = false,
    .has_padding = true,
    .format_info = {.subsampling = {.chroma_h_sub = 2, .chroma_v_sub = 2}},
};

const pqfmt_yuv_desc_s g_yuv_fmt_yuv422sp_nv20 = {
    .layout = PQFMT_YUV_LAYOUT_SimiPlanar,
    .sampling = PQFMT_YUV_SAMPLING_422,
    .uv_sample_ratio_ver = 1,
    .uv_sample_ratio_hor = 2,
    .order = {.uv_order = PQFMT_UV_ORDER_UV},
    .packing = PQFMT_PACKING_PACKED,
    .line_variant = PQFMT_LINE_UNIFORM,
    .tile_size = PQFMT_RASTER,
    .depth_y = 8,
    .depth_uv = 10,
    .has_packing = true,
    .has_padding = false,
    .format_info = {.subsampling = {.chroma_h_sub = 2, .chroma_v_sub = 1}},
};

const pqfmt_yuv_desc_s g_yuv_fmt_yuv422sp_p210 = {
    .layout = PQFMT_YUV_LAYOUT_SimiPlanar,
    .sampling = PQFMT_YUV_SAMPLING_422,
    .uv_sample_ratio_ver = 1,
    .uv_sample_ratio_hor = 2,
    .order = {.uv_order = PQFMT_UV_ORDER_UV},
    .packing = PQFMT_PACKING_MSB,
    .line_variant = PQFMT_LINE_UNIFORM,
    .tile_size = PQFMT_RASTER,
    .depth_y = 10,
    .depth_uv = 10,
    .has_packing = false,
    .has_padding = true,
    .format_info = {.subsampling = {.chroma_h_sub = 2, .chroma_v_sub = 1}},
};

const pqfmt_yuv_desc_s g_yuv_fmt_yuv444sp_nv30 = {
    .layout = PQFMT_YUV_LAYOUT_SimiPlanar,
    .sampling = PQFMT_YUV_SAMPLING_444,
    .uv_sample_ratio_ver = 1,
    .uv_sample_ratio_hor = 1,
    .order = {.uv_order = PQFMT_UV_ORDER_UV},
    .packing = PQFMT_PACKING_PACKED,
    .line_variant = PQFMT_LINE_UNIFORM,
    .tile_size = PQFMT_RASTER,
    .depth_y = 8,
    .depth_uv = 10,
    .has_packing = true,
    .has_padding = false,
    .format_info = {.subsampling = {.chroma_h_sub = 1, .chroma_v_sub = 1}},
};

const pqfmt_yuv_desc_s g_yuv_fmt_yuv420sp_tile4x4 = {
    .layout = PQFMT_YUV_LAYOUT_SimiPlanar,
    .sampling = PQFMT_YUV_SAMPLING_420,
    .uv_sample_ratio_ver = 2,
    .uv_sample_ratio_hor = 2,
    .order = {.uv_order = PQFMT_UV_ORDER_UV},
    .packing = PQFMT_PACKING_UNPACKED,
    .line_variant = PQFMT_LINE_UNIFORM,
    .tile_size = PQFMT_TILE_4X4,
    .depth_y = 8,
    .depth_uv = 8,
    .has_packing = false,
    .has_padding = false,
    .format_info = {.subsampling = {.chroma_h_sub = 2, .chroma_v_sub = 2}},
};

const pqfmt_yuv_desc_s g_yuv_fmt_yuv420sp_tile8x8 = {
    .layout = PQFMT_YUV_LAYOUT_SimiPlanar,
    .sampling = PQFMT_YUV_SAMPLING_420,
    .uv_sample_ratio_ver = 2,
    .uv_sample_ratio_hor = 2,
    .order = {.uv_order = PQFMT_UV_ORDER_UV},
    .packing = PQFMT_PACKING_UNPACKED,
    .line_variant = PQFMT_LINE_UNIFORM,
    .tile_size = PQFMT_TILE_8X8,
    .depth_y = 8,
    .depth_uv = 8,
    .has_packing = false,
    .has_padding = false,
    .format_info = {.subsampling = {.chroma_h_sub = 2, .chroma_v_sub = 2}},
};

const pqfmt_yuv_desc_s g_yuv_fmt_yuv422sp_tile4x4 = {
    .layout = PQFMT_YUV_LAYOUT_SimiPlanar,
    .sampling = PQFMT_YUV_SAMPLING_422,
    .uv_sample_ratio_ver = 1,
    .uv_sample_ratio_hor = 2,
    .order = {.uv_order = PQFMT_UV_ORDER_UV},
    .packing = PQFMT_PACKING_UNPACKED,
    .line_variant = PQFMT_LINE_UNIFORM,
    .tile_size = PQFMT_TILE_4X4,
    .depth_y = 8,
    .depth_uv = 8,
    .has_packing = false,
    .has_padding = false,
    .format_info = {.subsampling = {.chroma_h_sub = 2, .chroma_v_sub = 1}},
};

const pqfmt_yuv_desc_s g_yuv_fmt_yuv410p = {
    .layout = PQFMT_YUV_LAYOUT_Planar,
    .sampling = PQFMT_YUV_SAMPLING_410,
    .uv_sample_ratio_ver = 4,
    .uv_sample_ratio_hor = 4,
    .order = {.uv_order = PQFMT_UV_ORDER_UV},
    .packing = PQFMT_PACKING_UNPACKED,
    .line_variant = PQFMT_LINE_UNIFORM,
    .tile_size = PQFMT_RASTER,
    .depth_y = 8,
    .depth_uv = 8,
    .has_packing = false,
    .has_padding = false,
    .format_info = {.subsampling = {.chroma_h_sub = 4, .chroma_v_sub = 4}},
};

const pqfmt_yuv_desc_s g_yuv_fmt_yuv440p = {
    .layout = PQFMT_YUV_LAYOUT_Planar,
    .sampling = PQFMT_YUV_SAMPLING_440,
    .uv_sample_ratio_ver = 2,
    .uv_sample_ratio_hor = 1,
    .order = {.uv_order = PQFMT_UV_ORDER_UV},
    .packing = PQFMT_PACKING_UNPACKED,
    .line_variant = PQFMT_LINE_UNIFORM,
    .tile_size = PQFMT_RASTER,
    .depth_y = 8,
    .depth_uv = 8,
    .has_packing = false,
    .has_padding = false,
    .format_info = {.subsampling = {.chroma_h_sub = 2, .chroma_v_sub = 1}},
};

const char* pqfmt_yuv_sampling_name(pqfmt_yuv_sampling_e sampling) {
    switch (sampling) {
        case PQFMT_YUV_SAMPLING_444: return "444";
        case PQFMT_YUV_SAMPLING_422: return "422";
        case PQFMT_YUV_SAMPLING_420: return "420";
        case PQFMT_YUV_SAMPLING_410: return "410";
        case PQFMT_YUV_SAMPLING_440: return "440";
        case PQFMT_YUV_SAMPLING_411: return "411";
        case PQFMT_YUV_SAMPLING_400: return "400";
        default: return "Unknown";
    }
}

const char* pqfmt_yuv_layout_name(pqfmt_yuv_layout_e layout) {
    switch (layout) {
        case PQFMT_YUV_LAYOUT_Planar: return "Planar";
        case PQFMT_YUV_LAYOUT_SimiPlanar: return "Semi-Planar";
        case PQFMT_YUV_LAYOUT_Interleaved: return "Interleaved";
        default: return "Unknown";
    }
}

const char* pqfmt_uv_order_name(pqfmt_uv_order_e order) {
    switch (order) {
        case PQFMT_UV_ORDER_UV: return "UV";
        case PQFMT_UV_ORDER_VU: return "VU";
        case PQFMT_YUV422I_YUYV: return "YUYV";
        case PQFMT_YUV422I_YVYU: return "YVYU";
        case PQFMT_YUV422I_UYVY: return "UYVY";
        case PQFMT_YUV422I_VYUY: return "VYUY";
        default: return "Unknown";
    }
}

const char* pqfmt_tile_size_name(pqfmt_tile_size_e size) {
    switch (size) {
        case PQFMT_RASTER: return "Raster";
        case PQFMT_TILE_4X4: return "Tile4x4";
        case PQFMT_TILE_8X8: return "Tile8x8";
        case PQFMT_TILE_4X8: return "Tile4x8";
        case PQFMT_TILE_8X4: return "Tile8x4";
        default: return "Unknown";
    }
}

const char* pqfmt_data_packing_name(pqfmt_data_packing_e packing) {
    switch (packing) {
        case PQFMT_PACKING_UNPACKED: return "Unpacked";
        case PQFMT_PACKING_PACKED: return "Packed";
        case PQFMT_PACKING_MSB: return "MSB Aligned";
        default: return "Unknown";
    }
}

const char* pqfmt_line_variant_name(pqfmt_line_variant_e variant) {
    switch (variant) {
        case PQFMT_LINE_UNIFORM: return "Uniform";
        case PQFMT_LINE_VARIANT: return "Variant";
        default: return "Unknown";
    }
}

void pqfmt_yuv_desc_init(pqfmt_yuv_desc_s *desc,
                       pqfmt_yuv_sampling_e sampling,
                       pqfmt_yuv_layout_e layout,
                       pqfmt_uv_order_e uv_order,
                       pqfmt_yuv422i_order_e yuv422i_order,
                       pqfmt_tile_size_e tile_size,
                       pqfmt_data_packing_e packing,
                       pqfmt_line_variant_e line_variant,
                       uint8_t depth_y,
                       uint8_t depth_uv,
                       bool has_packing,
                       bool has_padding) {
    if (!desc) return;

    desc->sampling = sampling;
    desc->layout = layout;
    desc->order.uv_order = uv_order;
    desc->order.yuv422i_order = yuv422i_order;
    desc->tile_size = tile_size;
    desc->packing = packing;
    desc->line_variant = line_variant;
    desc->depth_y = depth_y;
    desc->depth_uv = depth_uv;
    desc->has_packing = has_packing;
    desc->has_padding = has_padding;
}

bool pqfmt_yuv_desc_is_valid(const pqfmt_yuv_desc_s *desc) {
    if (!desc) return false;
    if (desc->depth_y == 0) return false;
    if (desc->layout == PQFMT_YUV_LAYOUT_Interleaved && desc->sampling != PQFMT_YUV_SAMPLING_422) return false;
    return true;
}

bool pqfmt_yuv_desc_is_uv_order(const pqfmt_yuv_desc_s *desc) {
    return desc ? desc->order.uv_order == PQFMT_UV_ORDER_UV : false;
}

bool pqfmt_yuv_desc_is_tile(const pqfmt_yuv_desc_s *desc) {
    return desc ? desc->tile_size != PQFMT_RASTER : false;
}

bool pqfmt_yuv_desc_is_packed_10bit(const pqfmt_yuv_desc_s *desc) {
    return desc ? desc->has_packing && desc->depth_y == 10 : false;
}

bool pqfmt_yuv_desc_has_line_variant(const pqfmt_yuv_desc_s *desc) {
    return desc ? desc->line_variant == PQFMT_LINE_VARIANT : false;
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

    switch (desc->tile_size) {
        case PQFMT_RASTER: *tile_w = 0; *tile_h = 0; break;
        case PQFMT_TILE_4X4: *tile_w = 4; *tile_h = 4; break;
        case PQFMT_TILE_8X8: *tile_w = 8; *tile_h = 8; break;
        case PQFMT_TILE_4X8: *tile_w = 4; *tile_h = 8; break;
        case PQFMT_TILE_8X4: *tile_w = 8; *tile_h = 4; break;
        default: *tile_w = 0; *tile_h = 0; break;
    }
    return 0;
}

int pqfmt_yuv_desc_get_chroma_subsampling(const pqfmt_yuv_desc_s *desc, int *h_sub, int *v_sub) {
    if (!desc) return -1;

    *h_sub = desc->uv_sample_ratio_hor;
    *v_sub = desc->uv_sample_ratio_ver;
    return 0;
}

const pqfmt_line_format_s* pqfmt_yuv_desc_get_odd_line_format(const pqfmt_yuv_desc_s *desc) {
    if (!desc || !desc->has_line_variant) return NULL;
    return &desc->format_info.variant_lines.odd_line;
}

const pqfmt_line_format_s* pqfmt_yuv_desc_get_even_line_format(const pqfmt_yuv_desc_s *desc) {
    if (!desc || !desc->has_line_variant) return NULL;
    return &desc->format_info.variant_lines.even_line;
}

uint8_t pqfmt_yuv_desc_calc_bpp(const pqfmt_yuv_desc_s *desc) {
    if (!desc) return 0;

    float y_ratio = desc->uv_sample_ratio_hor * desc->uv_sample_ratio_ver;
    float uv_ratio = 1.0f;

    switch (desc->sampling) {
        case PQFMT_YUV_SAMPLING_444: uv_ratio = 2.0f; break;
        case PQFMT_YUV_SAMPLING_422: uv_ratio = 1.0f; break;
        case PQFMT_YUV_SAMPLING_420: uv_ratio = 0.5f; break;
        case PQFMT_YUV_SAMPLING_410: uv_ratio = 0.25f; break;
        case PQFMT_YUV_SAMPLING_440: uv_ratio = 1.0f; break;
        case PQFMT_YUV_SAMPLING_411: uv_ratio = 0.25f; break;
        case PQFMT_YUV_SAMPLING_400: uv_ratio = 0.0f; break;
    }

    uint8_t depth = desc->has_packing ? desc->depth_y : desc->depth_y;
    return (uint8_t)(depth * y_ratio + depth * uv_ratio);
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
    if (!desc) return 0;

    int tile_w, tile_h;
    pqfmt_yuv_desc_get_tile_size(desc, &tile_w, &tile_h);
    if (tile_w == 0 || tile_h == 0) return 0;

    int pixels_per_tile = tile_w * tile_h;
    return (uint8_t)(pqfmt_yuv_desc_calc_bpp(desc) * pixels_per_tile / 8);
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
           desc1->order.uv_order == desc2->order.uv_order &&
           desc1->order.yuv422i_order == desc2->order.yuv422i_order &&
           desc1->tile_size == desc2->tile_size &&
           desc1->packing == desc2->packing &&
           desc1->line_variant == desc2->line_variant &&
           desc1->depth_y == desc2->depth_y &&
           desc1->depth_uv == desc2->depth_uv &&
           desc1->has_packing == desc2->has_packing &&
           desc1->has_padding == desc2->has_padding;
}

void pqfmt_yuv_desc_print(const pqfmt_yuv_desc_s *desc) {
    if (!desc) {
        printf("YUV Format: NULL\n");
        return;
    }

    printf("YUV Format:\n");
    printf("  Sampling: %s\n", pqfmt_yuv_sampling_name(desc->sampling));
    printf("  Layout: %s\n", pqfmt_yuv_layout_name(desc->layout));
    printf("  Order: %s\n", pqfmt_uv_order_name(desc->order.uv_order));
    printf("  Tile: %s\n", pqfmt_tile_size_name(desc->tile_size));
    printf("  Packing: %s\n", pqfmt_data_packing_name(desc->packing));
    printf("  LineVariant: %s\n", pqfmt_line_variant_name(desc->line_variant));
    printf("  DepthY: %d, DepthUV: %d\n", desc->depth_y, desc->depth_uv);
    printf("  HasPacking: %s\n", desc->has_packing ? "Yes" : "No");
    printf("  HasPadding: %s\n", desc->has_padding ? "Yes" : "No");
    printf("  UV Ratio: V%d H%d\n", desc->uv_sample_ratio_ver, desc->uv_sample_ratio_hor);
}
