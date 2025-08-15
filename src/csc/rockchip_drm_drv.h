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
#include "errno-base.h"


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

struct post_csc
{
    u16 hue;
    u16 saturation;
    u16 contrast;
    u16 brightness;
    u16 r_gain;
    u16 g_gain;
    u16 b_gain;
    u16 r_offset;
    u16 g_offset;
    u16 b_offset;
    u16 csc_enable;
};

#define DRM_ERROR(fmt, args...) printf("rockchip-drm: " fmt, ##args)

#define ARRAY_SIZE(arr)         (sizeof(arr) / sizeof((arr)[0]))

#endif /* _ROCKCHIP_DRM_DRV_H_ */
