/* SPDX-License-Identifier: GPL-2.0-only */
/*
 * Copyright (C) Rockchip Electronics Co., Ltd.
 * Author:Mark Yao <mark.yao@rock-chips.com>
 *
 * based on exynos_drm_drv.h
 */

#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
// #include "errno-base.h"


#ifndef _ROCKCHIP_DRM_DRV_H
#define _ROCKCHIP_DRM_DRV_H

typedef uint32_t u32;
typedef uint16_t u16;
typedef uint8_t u8;
typedef int32_t s32;
typedef int16_t s16;
typedef int8_t s8;
typedef uint64_t u64;
typedef int64_t s64;

enum drm_color_encoding
{
    DRM_COLOR_YCBCR_BT601,
    DRM_COLOR_YCBCR_BT709,
    DRM_COLOR_YCBCR_BT2020,
    DRM_COLOR_ENCODING_MAX,
};

enum drm_csc_mode
{
    DRM_RGBL_TO_RGBF,
    DRM_RGBL_TO_BT601L,
    DRM_RGBL_TO_BT601F,
    DRM_RGBL_TO_BT709L,
    DRM_RGBL_TO_BT709F,
    DRM_RGBL_TO_BT2020L,
    DRM_RGBL_TO_BT2020F,
    DRM_RGBF_TO_RGBL,
    DRM_RGBF_TO_BT601L,
    DRM_RGBF_TO_BT601F,
    DRM_RGBF_TO_BT709L,
    DRM_RGBF_TO_BT709F,
    DRM_RGBF_TO_BT2020L,
    DRM_RGBF_TO_BT2020F,
    DRM_BT601L_TO_RGBL,
    DRM_BT601L_TO_RGBF,
    DRM_BT601L_TO_BT601F,
    DRM_BT601L_TO_BT709L,
    DRM_BT601L_TO_BT709F,
    DRM_BT601F_TO_RGBL,
    DRM_BT601F_TO_RGBF,
    DRM_BT601F_TO_BT601L,
    DRM_BT601F_TO_BT709L,
    DRM_BT601F_TO_BT709F,
    DRM_BT709L_TO_RGBL,
    DRM_BT709L_TO_RGBF,
    DRM_BT709L_TO_BT601L,
    DRM_BT709L_TO_BT601F,
    DRM_BT709L_TO_BT709F,
    DRM_BT709F_TO_RGBL,
    DRM_BT709F_TO_RGBF,
    DRM_BT709F_TO_BT601L,
    DRM_BT709F_TO_BT601F,
    DRM_BT709F_TO_BT709L,
    DRM_BT2020L_TO_RGBL,
    DRM_BT2020L_TO_RGBF,
    DRM_BT2020L_TO_BT2020F,
    DRM_BT2020F_TO_RGBL,
    DRM_BT2020F_TO_RGBF,
    DRM_BT2020F_TO_BT2020L,
    DRM_CSC_MODE_MAX,
};

struct post_csc
{
    u16 hue;        // range: [0, 511], default: 256
    u16 saturation; // range: [0, 511], default: 256
    u16 contrast;   // range: [0, 511], default: 256
    u16 brightness; // range: [0, 511], default: 256
    u16 r_gain;     // range: [0, 511], default: 256
    u16 g_gain;     // range: [0, 511], default: 256
    u16 b_gain;     // range: [0, 511], default: 256
    u16 r_offset;   // range: [0, 511], default: 256
    u16 g_offset;   // range: [0, 511], default: 256
    u16 b_offset;   // range: [0, 511], default: 256
    u16 csc_enable; // range: [0, 1], default: 1
};

#define DRM_ERROR(fmt, ...)     printf("rockchip-drm: " fmt, ##__VA_ARGS__)

#define ARRAY_SIZE(arr)         (sizeof(arr) / sizeof((arr)[0]))

#endif /* _ROCKCHIP_DRM_DRV_H_ */
