/* SPDX-License-Identifier: (GPL-2.0+ OR MIT) */
/*
 * Copyright (C) Rockchip Electronics Co., Ltd.
 * Author:
 *      Zhang Yubing <yubing.zhang@rock-chips.com>
 */

#ifndef _ROCKCHIP_POST_CSC_H
#define _ROCKCHIP_POST_CSC_H

#include "rockchip_drm_drv.h"
#include "rockchip_drm_vop.h"

int rockchip_calc_post_csc(const struct post_csc *csc_cfg, // [I] CSC config
    struct post_csc_coef *csc_simple_coef,                 // [O] return CSC coefs
    const struct post_csc_convert_mode *convert_mode       // [I] CSC convert mode
);

extern const struct post_csc_convert_mode g_supported_standard_convert_mode[];

#endif
