/* SPDX-License-Identifier: (GPL-2.0+ OR MIT) */
/*
 * Copyright (C) Rockchip Electronics Co., Ltd.
 * Author:
 *      Zhang Yubing <yubing.zhang@rock-chips.com>
 */

#ifndef _ROCKCHIP_POST_CSC_H
#define _ROCKCHIP_POST_CSC_H

// #include <drm/drm_crtc.h>
#include "rockchip_drm_drv.h"
#include "rockchip_drm_vop.h"

// for post_csc_convert_mode::swap_channels
enum post_csc_channel_swap_type {
	NO_SWAP = 0,
	RK3576_DEF_SWAP = 1,
	R2R_ON_Y2R = 2,
	R2R_ON_R2Y = 3,
	Y2Y_ON_Y2R = 4,
	Y2Y_ON_R2Y = 5,
};

int rockchip_calc_post_csc(struct post_csc *csc_cfg, struct post_csc_coef *csc_simple_coef,
			   struct post_csc_convert_mode *convert_mode);


#endif
