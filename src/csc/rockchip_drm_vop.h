/* SPDX-License-Identifier: GPL-2.0-only */
/*
 * Copyright (C) Rockchip Electronics Co., Ltd.
 * Author:Mark Yao <mark.yao@rock-chips.com>
 */

#ifndef _ROCKCHIP_DRM_VOP_H
#define _ROCKCHIP_DRM_VOP_H

#include "rockchip_drm_drv.h"

struct post_csc_convert_mode
{
    // enum drm_color_encoding intput_color_encoding;
    // enum drm_color_encoding output_color_encoding;
    int input_color_encoding;  // see drm_color_encoding
    int output_color_encoding; // see drm_color_encoding
    bool is_input_yuv;
    bool is_output_yuv;
    bool is_input_full_range;
    bool is_output_full_range;
    int swap_channels;  // swap YUV to VYU
    int pixel_depth;    // {8/10}
    int coef_precision; // {8, 10, 13}, NOTE: coef_precision should be >= pixel_depth
};

struct post_csc_coef
{
    s32 csc_coef00;
    s32 csc_coef01;
    s32 csc_coef02;
    s32 csc_coef10;
    s32 csc_coef11;
    s32 csc_coef12;
    s32 csc_coef20;
    s32 csc_coef21;
    s32 csc_coef22;

    s32 csc_dc0;
    s32 csc_dc1;
    s32 csc_dc2;

    u32 range_type;
};

#endif /* _ROCKCHIP_DRM_VOP_H */
