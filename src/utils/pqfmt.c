/**
 * @copyright: Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @brief:     图像格式管理模块实现
 * @author:
 * @create:    2026-04-16
 */

#include "pqfmt.h"
#include "pqfmt_cvt.h"
#include <string.h>
#include <stdlib.h>

/**
 * 格式描述表
 */
static const pqvf_fmt_attr g_fmt_desc_table[] = {
    /* Gray 格式 */
    [PQVF_FMT_GRAY8] = {
        .full_name = "Gray 8-bit",
        .short_name = "gray8",
        .alias = NULL,
        .fmt_id = PQVF_FMT_GRAY8,
        .base_type = PQVF_BASE_TYPE_GRAY,
        .bpp = 8,
        .depth = 8,
        .is_packed = false,
        .has_padding = false,
        .plane_count = 1,
        .is_drm_fourcc = false,
        .drm_fourcc = 0,
        .pitch_ratio = 1.0f,
        .framesize_ratio = 1.0f,
        .tile_bytes = 0,
    },

    /* RGB 格式 - 8bit */
    [PQVF_FMT_RGB888] = {
        .full_name = "RGB 888",
        .short_name = "rgb24",
        .alias = "rgb888",
        .fmt_id = PQVF_FMT_RGB888,
        .base_type = PQVF_BASE_TYPE_RGB,
        .bpp = 24,
        .depth = 8,
        .is_packed = false,
        .has_padding = false,
        .plane_count = 1,
        .is_drm_fourcc = false,
        .drm_fourcc = 0,
        .pitch_ratio = 3.0f,
        .framesize_ratio = 1.0f,
        .tile_bytes = 0,
    },

    [PQVF_FMT_BGR888] = {
        .full_name = "BGR 888",
        .short_name = "bgr24",
        .alias = "bgr888",
        .fmt_id = PQVF_FMT_BGR888,
        .base_type = PQVF_BASE_TYPE_RGB,
        .bpp = 24,
        .depth = 8,
        .is_packed = false,
        .has_padding = false,
        .plane_count = 1,
        .is_drm_fourcc = false,
        .drm_fourcc = 0,
        .pitch_ratio = 3.0f,
        .framesize_ratio = 1.0f,
        .tile_bytes = 0,
    },

    [PQVF_FMT_RGBA8888] = {
        .full_name = "RGBA 8888",
        .short_name = "rgba32",
        .alias = "rgba8888",
        .fmt_id = PQVF_FMT_RGBA8888,
        .base_type = PQVF_BASE_TYPE_RGB,
        .bpp = 32,
        .depth = 8,
        .is_packed = false,
        .has_padding = false,
        .plane_count = 1,
        .is_drm_fourcc = false,
        .drm_fourcc = 0,
        .pitch_ratio = 4.0f,
        .framesize_ratio = 1.0f,
        .tile_bytes = 0,
    },

    /* YUV 8bit Raster */
    [PQVF_FMT_YUV420SP_NV12] = {
        .full_name = "YUV420 Semi-Planar NV12",
        .short_name = "nv12",
        .alias = "yuv420sp",
        .fmt_id = PQVF_FMT_YUV420SP_NV12,
        .base_type = PQVF_BASE_TYPE_YUV,
        .bpp = 12,
        .depth = 8,
        .is_packed = false,
        .has_padding = false,
        .plane_count = 2,
        .is_drm_fourcc = false,
        .drm_fourcc = 0,
        .pitch_ratio = 1.0f,
        .framesize_ratio = 1.5f,
        .tile_bytes = 0,
    },

    [PQVF_FMT_YUV422I_YUYV] = {
        .full_name = "YUV422 Interleaved YUYV",
        .short_name = "yuyv",
        .alias = "yuv422i",
        .fmt_id = PQVF_FMT_YUV422I_YUYV,
        .base_type = PQVF_BASE_TYPE_YUV,
        .bpp = 16,
        .depth = 8,
        .is_packed = false,
        .has_padding = false,
        .plane_count = 1,
        .is_drm_fourcc = false,
        .drm_fourcc = 0,
        .pitch_ratio = 2.0f,
        .framesize_ratio = 2.0f,
        .tile_bytes = 0,
    },

    /* YUV Tile 格式 */
    [PQVF_FMT_YUV420SP_TILE4X4] = {
        .full_name = "YUV420 Semi-Planar Tile 4x4",
        .short_name = "yuv420sp_tile4x4",
        .alias = NULL,
        .fmt_id = PQVF_FMT_YUV420SP_TILE4X4,
        .base_type = PQVF_BASE_TYPE_YUV,
        .bpp = 12,
        .depth = 8,
        .is_packed = false,
        .has_padding = false,
        .plane_count = 2,
        .is_drm_fourcc = false,
        .drm_fourcc = 0,
        .pitch_ratio = 1.0f,
        .framesize_ratio = 1.5f,
        .tile_bytes = 24,
    },
};

#define FMT_DESC_TABLE_SIZE (sizeof(g_fmt_desc_table) / sizeof(pqvf_fmt_desc_t))

/**
 * 输入格式支持 Map
 */
static const pqvf_fmt_cap g_input_fmt_map[] = {
    {PQVF_FMT_YUV420SP_NV12, PQVF_CAP_BIDIR, PQVF_FMT_YUV420P},
    {PQVF_FMT_YUV420SP_NV21, PQVF_CAP_BIDIR, PQVF_FMT_YUV420P},
    {PQVF_FMT_YUV420SP_NV15, PQVF_CAP_INPUT, PQVF_FMT_YUV420P},
    {PQVF_FMT_YUV420SP_P010, PQVF_CAP_INPUT, PQVF_FMT_YUV420P},
    {PQVF_FMT_YUV422SP_NV16, PQVF_CAP_BIDIR, PQVF_FMT_YUV422P},
    {PQVF_FMT_YUV422SP_NV61, PQVF_CAP_BIDIR, PQVF_FMT_YUV422P},
    {PQVF_FMT_YUV422SP_NV20, PQVF_CAP_INPUT, PQVF_FMT_YUV422P},
    {PQVF_FMT_YUV422SP_P210, PQVF_CAP_INPUT, PQVF_FMT_YUV422P},
    {PQVF_FMT_YUV422I_YUYV, PQVF_CAP_INPUT, PQVF_FMT_YUV422P},
    {PQVF_FMT_YUV422I_YVYU, PQVF_CAP_INPUT, PQVF_FMT_YUV422P},
    {PQVF_FMT_YUV422I_UYVY, PQVF_CAP_INPUT, PQVF_FMT_YUV422P},
    {PQVF_FMT_YUV422I_VYUY, PQVF_CAP_INPUT, PQVF_FMT_YUV422P},
    {PQVF_FMT_YUV444SP_NV24, PQVF_CAP_BIDIR, PQVF_FMT_YUV444P},
    {PQVF_FMT_YUV444SP_NV42, PQVF_CAP_BIDIR, PQVF_FMT_YUV444P},
    {PQVF_FMT_YUV444SP_NV30, PQVF_CAP_INPUT, PQVF_FMT_YUV444P},
    {PQVF_FMT_YUV420SP_TILE4X4, PQVF_CAP_INPUT, PQVF_FMT_YUV420P},
    {PQVF_FMT_YUV420SP_TILE8X8, PQVF_CAP_INPUT, PQVF_FMT_YUV420P},
    {PQVF_FMT_YUV422SP_TILE4X4, PQVF_CAP_INPUT, PQVF_FMT_YUV422P},
    {PQVF_FMT_RGB888, PQVF_CAP_BIDIR, PQVF_FMT_RGB888},
    {PQVF_FMT_BGR888, PQVF_CAP_BIDIR, PQVF_FMT_BGR888},
    {PQVF_FMT_RGBA8888, PQVF_CAP_BIDIR, PQVF_FMT_RGBA8888},
    {PQVF_FMT_BGRA8888, PQVF_CAP_BIDIR, PQVF_FMT_BGRA8888},
    {PQVF_FMT_ARGB8888, PQVF_CAP_BIDIR, PQVF_FMT_ARGB8888},
    {PQVF_FMT_ABGR8888, PQVF_CAP_BIDIR, PQVF_FMT_ABGR8888},
    {PQVF_FMT_RGB565, PQVF_CAP_INPUT, PQVF_FMT_RGB888},
    {PQVF_FMT_BGR565, PQVF_CAP_INPUT, PQVF_FMT_BGR888},
    {PQVF_FMT_RGB332, PQVF_CAP_INPUT, PQVF_FMT_RGB888},
    {PQVF_FMT_BGR233, PQVF_CAP_INPUT, PQVF_FMT_BGR888},
    {PQVF_FMT_RGBA5551, PQVF_CAP_INPUT, PQVF_FMT_RGBA8888},
    {PQVF_FMT_ARGB1555, PQVF_CAP_INPUT, PQVF_FMT_ARGB8888},
    {PQVF_FMT_RGBA1010102, PQVF_CAP_OUTPUT, PQVF_FMT_RGBA8888},
    {PQVF_FMT_BGRA1010102, PQVF_CAP_OUTPUT, PQVF_FMT_BGRA8888},
};

#define INPUT_FMT_MAP_SIZE (sizeof(g_input_fmt_map) / sizeof(pqvf_fmt_cap_t))

/**
 * 输出格式支持 Map
 */
static const pqvf_fmt_cap g_output_fmt_map[] = {
    {PQVF_FMT_YUV420SP_NV12, PQVF_CAP_BIDIR, PQVF_FMT_YUV420P},
    {PQVF_FMT_YUV420SP_NV21, PQVF_CAP_BIDIR, PQVF_FMT_YUV420P},
    {PQVF_FMT_YUV420SP_NV15, PQVF_CAP_OUTPUT, PQVF_FMT_YUV420P},
    {PQVF_FMT_YUV420SP_P010, PQVF_CAP_OUTPUT, PQVF_FMT_YUV420P},
    {PQVF_FMT_YUV420SP_TILE4X4, PQVF_CAP_OUTPUT, PQVF_FMT_YUV420P},
    {PQVF_FMT_YUV420SP_TILE8X8, PQVF_CAP_OUTPUT, PQVF_FMT_YUV420P},
    {PQVF_FMT_YUV422SP_NV16, PQVF_CAP_BIDIR, PQVF_FMT_YUV422P},
    {PQVF_FMT_YUV422SP_NV61, PQVF_CAP_BIDIR, PQVF_FMT_YUV422P},
    {PQVF_FMT_YUV422SP_NV20, PQVF_CAP_OUTPUT, PQVF_FMT_YUV422P},
    {PQVF_FMT_YUV422SP_P210, PQVF_CAP_OUTPUT, PQVF_FMT_YUV422P},
    {PQVF_FMT_YUV422SP_TILE4X4, PQVF_CAP_OUTPUT, PQVF_FMT_YUV422P},
    {PQVF_FMT_YUV444SP_NV24, PQVF_CAP_BIDIR, PQVF_FMT_YUV444P},
    {PQVF_FMT_YUV444SP_NV42, PQVF_CAP_BIDIR, PQVF_FMT_YUV444P},
    {PQVF_FMT_YUV444SP_NV30, PQVF_CAP_OUTPUT, PQVF_FMT_YUV444P},
    {PQVF_FMT_RGB888, PQVF_CAP_BIDIR, PQVF_FMT_RGB888},
    {PQVF_FMT_BGR888, PQVF_CAP_BIDIR, PQVF_FMT_BGR888},
    {PQVF_FMT_RGBA8888, PQVF_CAP_BIDIR, PQVF_FMT_RGBA8888},
    {PQVF_FMT_BGRA8888, PQVF_CAP_BIDIR, PQVF_FMT_BGRA8888},
    {PQVF_FMT_ARGB8888, PQVF_CAP_BIDIR, PQVF_FMT_ARGB8888},
    {PQVF_FMT_ABGR8888, PQVF_CAP_BIDIR, PQVF_FMT_ABGR8888},
    {PQVF_FMT_RGB565, PQVF_CAP_OUTPUT, PQVF_FMT_RGB888},
    {PQVF_FMT_BGR565, PQVF_CAP_OUTPUT, PQVF_FMT_BGR888},
    {PQVF_FMT_RGB332, PQVF_CAP_OUTPUT, PQVF_FMT_RGB888},
    {PQVF_FMT_BGR233, PQVF_CAP_OUTPUT, PQVF_FMT_BGR888},
    {PQVF_FMT_RGBA5551, PQVF_CAP_OUTPUT, PQVF_FMT_RGBA8888},
    {PQVF_FMT_ARGB1555, PQVF_CAP_OUTPUT, PQVF_FMT_ARGB8888},
    {PQVF_FMT_RGBA1010102, PQVF_CAP_INPUT, PQVF_FMT_RGBA8888},
    {PQVF_FMT_BGRA1010102, PQVF_CAP_INPUT, PQVF_FMT_BGRA8888},
};

#define OUTPUT_FMT_MAP_SIZE (sizeof(g_output_fmt_map) / sizeof(pqvf_fmt_cap_t))

const pqvf_fmt_attr* pqvf_get_fmt_desc(pqvf_imgfmt_e fmt_id) {
    if (fmt_id >= 0 && fmt_id < FMT_DESC_TABLE_SIZE) {
        return &g_fmt_desc_table[fmt_id];
    }
    return NULL;
}

const char* pqvf_fmt_full_name(pqvf_imgfmt_e fmt_id) {
    const pqvf_fmt_attr *desc = pqvf_get_fmt_desc(fmt_id);
    return desc ? desc->full_name : "UnknownFmt";
}

const char* pqvf_fmt_short_name(pqvf_imgfmt_e fmt_id) {
    const pqvf_fmt_attr *desc = pqvf_get_fmt_desc(fmt_id);
    return desc ? desc->short_name : "unknown";
}

const char* pqvf_fmt_alias(pqvf_imgfmt_e fmt_id) {
    const pqvf_fmt_attr *desc = pqvf_get_fmt_desc(fmt_id);
    return desc ? (desc->alias ? desc->alias : "") : "";
}

int pqvf_fmt_bpp(pqvf_imgfmt_e fmt_id) {
    const pqvf_fmt_attr *desc = pqvf_get_fmt_desc(fmt_id);
    return desc ? desc->bpp : 0;
}

int pqvf_fmt_depth(pqvf_imgfmt_e fmt_id) {
    const pqvf_fmt_attr *desc = pqvf_get_fmt_desc(fmt_id);
    return desc ? desc->depth : 0;
}

int pqvf_fmt_plane_count(pqvf_imgfmt_e fmt_id) {
    const pqvf_fmt_attr *desc = pqvf_get_fmt_desc(fmt_id);
    return desc ? desc->plane_count : 0;
}

float pqvf_fmt_pitch_ratio(pqvf_imgfmt_e fmt_id) {
    const pqvf_fmt_attr *desc = pqvf_get_fmt_desc(fmt_id);
    return desc ? desc->pitch_ratio : 0.0f;
}

float pqvf_fmt_framesize_ratio(pqvf_imgfmt_e fmt_id) {
    const pqvf_fmt_attr *desc = pqvf_get_fmt_desc(fmt_id);
    return desc ? desc->framesize_ratio : 0.0f;
}

size_t pqvf_fmt_framesize(pqvf_imgfmt_e fmt_id, int w, int h, int ws, int hs) {
    const pqvf_fmt_attr *desc = pqvf_get_fmt_desc(fmt_id);
    if (!desc) return 0;

    int vir_w = pqvf_fmt_vir_wid(fmt_id, w, hs);
    return (size_t)(vir_w * h * desc->framesize_ratio);
}

int pqvf_fmt_vir_wid(pqvf_imgfmt_e fmt_id, int wid, int hs) {
    const pqvf_fmt_attr *desc = pqvf_get_fmt_desc(fmt_id);
    if (!desc) return 0;

    return (int)(wid * desc->pitch_ratio);
}

bool pqvf_fmt_is_yuv(pqvf_imgfmt_e fmt_id) {
    const pqvf_fmt_attr *desc = pqvf_get_fmt_desc(fmt_id);
    return desc ? desc->base_type == PQVF_BASE_TYPE_YUV : false;
}

bool pqvf_fmt_is_rgb(pqvf_imgfmt_e fmt_id) {
    const pqvf_fmt_attr *desc = pqvf_get_fmt_desc(fmt_id);
    return desc ? desc->base_type == PQVF_BASE_TYPE_RGB : false;
}

bool pqvf_fmt_is_tile(pqvf_imgfmt_e fmt_id) {
    const pqvf_fmt_attr *desc = pqvf_get_fmt_desc(fmt_id);
    return desc ? desc->tile_bytes > 0 : false;
}

bool pqvf_fmt_can_input(pqvf_imgfmt_e fmt_id) {
    for (int i = 0; i < INPUT_FMT_MAP_SIZE; i++) {
        if (g_input_fmt_map[i].fmt_id == fmt_id) {
            return (g_input_fmt_map[i].cap & PQVF_CAP_INPUT) != 0;
        }
    }
    return false;
}

bool pqvf_fmt_can_output(pqvf_imgfmt_e fmt_id) {
    for (int i = 0; i < OUTPUT_FMT_MAP_SIZE; i++) {
        if (g_output_fmt_map[i].fmt_id == fmt_id) {
            return (g_output_fmt_map[i].cap & PQVF_CAP_OUTPUT) != 0;
        }
    }
    return false;
}

pqvf_imgfmt_e pqvf_fmt_get_canonical(pqvf_imgfmt_e fmt_id) {
    for (int i = 0; i < INPUT_FMT_MAP_SIZE; i++) {
        if (g_input_fmt_map[i].fmt_id == fmt_id) {
            return g_input_fmt_map[i].canonical_fmt;
        }
    }
    for (int i = 0; i < OUTPUT_FMT_MAP_SIZE; i++) {
        if (g_output_fmt_map[i].fmt_id == fmt_id) {
            return g_output_fmt_map[i].canonical_fmt;
        }
    }
    return PQVF_FMT_INVALID;
}
