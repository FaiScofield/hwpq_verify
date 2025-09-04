/* SPDX-License-Identifier: GPL-2.0-only */
/**
 * @copyright: Copyright (C) Rockchip Electronics Co., Ltd.
 * @note: This file is part of the original 'rockchip_drm_vop.h' from the 'drm' project.
 *        Only nessary structures are kept here to support the HWPQ kernel verification.
 * @author: vance.wu@rock-chips.com
 * @history:
 *  - 2025/09/04 vance.wu: sync with the 'drm' project for RK3572 verification.
 */

#ifndef _ROCKCHIP_DRM_VOP_H
#define _ROCKCHIP_DRM_VOP_H

#include "rockchip_drm_drv.h"
#include "drm_color_mgmt.h" // drm_color_encoding


struct post_csc_convert_mode
{
	enum drm_color_encoding intput_color_encoding;
	enum drm_color_encoding output_color_encoding;
	bool is_input_yuv;
	bool is_output_yuv;
	bool is_input_full_range;
	bool is_output_full_range;
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
