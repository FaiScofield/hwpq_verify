/**
 * @copyright: Copyright (C) Rockchip Electronics Co., Ltd.
 * @note: This file is part of the original 'drm_color_mgmt.h' from the 'drm' project.
 *        Only nessary structures are kept here to support the HWPQ kernel verification.
 * @author: vance.wu@rock-chips.com
 * @history:
 *  - 2025/09/04 vance.wu: sync with the 'drm' project for RK3572 verification.
 */

#ifndef __DRM_COLOR_MGMT_H__
#define __DRM_COLOR_MGMT_H__

enum drm_color_encoding {
	DRM_COLOR_YCBCR_BT601,
	DRM_COLOR_YCBCR_BT709,
	DRM_COLOR_YCBCR_BT2020,
	DRM_COLOR_ENCODING_MAX,
};

enum drm_color_range {
	DRM_COLOR_YCBCR_LIMITED_RANGE,
	DRM_COLOR_YCBCR_FULL_RANGE,
	DRM_COLOR_RANGE_MAX,
};

#endif // __DRM_COLOR_MGMT_H__
