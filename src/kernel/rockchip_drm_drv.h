/* SPDX-License-Identifier: GPL-2.0-only */
/**
 * @copyright: Copyright (C) Rockchip Electronics Co., Ltd.
 * @note: This file is part of the original 'rockchip_drm_drv.h' from the 'drm' project.
 *        Only nessary structures are kept here to support the HWPQ kernel verification.
 * @author: vance.wu@rock-chips.com
 * @history:
 *  - 2025/09/04 vance.wu: sync with the 'drm' project for RK3572 verification.
 */

#ifndef _ROCKCHIP_DRM_DRV_H
#define _ROCKCHIP_DRM_DRV_H

#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>

typedef uint32_t    u32;
typedef uint16_t    u16;
typedef uint8_t     u8;
typedef int32_t     s32;
typedef int16_t     s16;
typedef int8_t      s8;
typedef uint64_t    u64;
typedef int64_t     s64;


#define ACM_GAIN_LUT_HY_LENGTH			(9*17)
#define ACM_GAIN_LUT_HY_TOTAL_LENGTH	(ACM_GAIN_LUT_HY_LENGTH * 3)
#define ACM_GAIN_LUT_HS_LENGTH			(13*17)
#define ACM_GAIN_LUT_HS_TOTAL_LENGTH	(ACM_GAIN_LUT_HS_LENGTH * 3)
#define ACM_DELTA_LUT_H_LENGTH			65
#define ACM_DELTA_LUT_H_TOTAL_LENGTH	(ACM_DELTA_LUT_H_LENGTH * 3)

struct post_acm {
	s16 delta_lut_h[ACM_DELTA_LUT_H_TOTAL_LENGTH];
	s16 gain_lut_hy[ACM_GAIN_LUT_HY_TOTAL_LENGTH];
	s16 gain_lut_hs[ACM_GAIN_LUT_HS_TOTAL_LENGTH];
	u16 y_gain;
	u16 h_gain;
	u16 s_gain;
	u16 acm_enable;
};


struct post_csc {
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


#define ROCKCHIP_VOP_DCI_LUT_LENGTH 5632

struct dci_data {
	u32 plat; /* Reserved to distinguish later platform */
	u8 dci_lut_data[ROCKCHIP_VOP_DCI_LUT_LENGTH];
	u32 blk_size_h_ratio;
	u32 blk_size_v_ratio;
	u32 dci_act_w;
	u32 dci_act_h;
	u32 adj0;
	u32 adj1;
	u32 uv_adj;
	u32 dci_en;
};


#define SHARP_REG_LENGTH 692

struct post_sharp {
	u32 plat; /* Reserved to distinguish later platform */
	u32 regs[SHARP_REG_LENGTH / 4];
};


#define DRM_ERROR(fmt, ...) printf("rockchip-drm: " fmt, ##__VA_ARGS__)
#define ARRAY_SIZE(arr)     (sizeof(arr) / sizeof((arr)[0]))

#endif /* _ROCKCHIP_DRM_DRV_H_ */
