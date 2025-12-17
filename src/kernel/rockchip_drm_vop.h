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

/*
 * major: IP major version, used for IP structure
 * minor: big feature change under same structure
 * build: RTL current SVN number
 */
#define VOP_VERSION(major, minor)	((major) << 8 | (minor))
#define VOP_MAJOR(version)		((version) >> 8)
#define VOP_MINOR(version)		((version) & 0xff)

#define VOP_VERSION_RK3066		VOP_VERSION(2, 1)
#define VOP_VERSION_RK3036		VOP_VERSION(2, 2)
#define VOP_VERSION_RK3126		VOP_VERSION(2, 4)
#define VOP_VERSION_PX30_LITE		VOP_VERSION(2, 5)
#define VOP_VERSION_PX30_BIG		VOP_VERSION(2, 6)
#define VOP_VERSION_RK3308		VOP_VERSION(2, 7)
#define VOP_VERSION_RV1126		VOP_VERSION(2, 0xb)
#define VOP_VERSION_RV1106		VOP_VERSION(2, 0xc)
#define VOP_VERSION_RK3576_LITE		VOP_VERSION(2, 0xd)
#define VOP_VERSION_RK3506		VOP_VERSION(2, 0xe)
#define VOP_VERSION_RV1126B		VOP_VERSION(2, 0xf)
#define VOP_VERSION_RK3572_LITE		VOP_VERSION(2, 0x10)
#define VOP_VERSION_RK3288		VOP_VERSION(3, 0)
#define VOP_VERSION_RK3288W		VOP_VERSION(3, 1)
#define VOP_VERSION_RK3368		VOP_VERSION(3, 2)
#define VOP_VERSION_RK3366		VOP_VERSION(3, 4)
#define VOP_VERSION_RK3399_BIG		VOP_VERSION(3, 5)
#define VOP_VERSION_RK3399_LITE		VOP_VERSION(3, 6)
#define VOP_VERSION_RK3228		VOP_VERSION(3, 7)
#define VOP_VERSION_RK3328		VOP_VERSION(3, 8)

#define VOP2_VERSION(major, minor, build)	((major) << 24 | (minor) << 16 | (build))
#define VOP2_MAJOR(version)		(((version) >> 24) & 0xff)
#define VOP2_MINOR(version)		(((version) >> 16) & 0xff)
#define VOP2_BUILD(version)		((version) & 0xffff)

/* The new SOC VOP version is bigger than the old */
#define VOP_VERSION_RK3568	VOP2_VERSION(0x40, 0x15, 0x8023)
#define VOP_VERSION_RK3588	VOP2_VERSION(0x40, 0x17, 0x6786)
#define VOP_VERSION_RK3528	VOP2_VERSION(0x50, 0x17, 0x1263)
#define VOP_VERSION_RK3562	VOP2_VERSION(0x50, 0x17, 0x4350)
#define VOP_VERSION_RK3576	VOP2_VERSION(0x50, 0x19, 0x9765)
#define VOP_VERSION_RK3572	VOP2_VERSION(0x50, 0x20, 0x9372)
#define VOP_VERSION_RK3538	VOP2_VERSION(0x50, 0x30, 0x9328)


enum rk_pq_csc_swap_type {
	RK_PQ_CSC_SWAP_NONE = 0,
	RK_PQ_CSC_V1_SWAP,		/* for rk3576 csc */
	RK_PQ_CSC_V2_VP_Y2R_R2R,
	RK_PQ_CSC_V2_R2Y_R2R,
	RK_PQ_CSC_V2_Y2R_Y2Y,
	RK_PQ_CSC_V2_VP_R2Y_Y2Y,
};

struct post_csc_convert_mode {
	enum drm_color_encoding intput_color_encoding;
	enum drm_color_encoding output_color_encoding;
	bool is_input_yuv;
	bool is_output_yuv;
	bool is_input_full_range;
	bool is_output_full_range;
	/* new after RK3572 & RK3538 */
	u8 swap_channels;	/* For now, only rg swap in DCI mode is required */
	u32 plat;		/* To distinguish platform */
	u8 pixel_depth;         /* {8, 10} */
	u8 coef_precision;      /* {8, 10, 13}, NOTE: coef_precision should be >= pixel_depth */
};

struct post_csc_coef {
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
