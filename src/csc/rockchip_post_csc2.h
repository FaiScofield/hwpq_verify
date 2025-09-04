/* SPDX-License-Identifier: (GPL-2.0+ OR MIT) */
/**
 * @copyright: Copyright (C) Rockchip Electronics Co., Ltd.
 * @note: Base on 'rockchip_post_csc.h' from the 'drm' project.
 *        This is not the offical updated version but a new implementation for HWPQ kernel verification.
 * @author: vance.wu@rock-chips.com
 * @history:
 *  - 2025/09/04 vance.wu: new implementation for HWPQ kernel verification.
 */

#ifndef _ROCKCHIP_POST_CSC2_H
#define _ROCKCHIP_POST_CSC2_H

#include "rockchip_drm_drv.h"
#include "rockchip_drm_vop.h"

// int rockchip_calc_post_csc(const struct post_csc *csc_cfg, // [I] CSC config
//     struct post_csc_coef *csc_simple_coef,                 // [O] return CSC coefs
//     const struct post_csc_convert_mode *convert_mode       // [I] CSC convert mode
// );


#define ENABLE_POST_CSC_FLOATING_POINT (0) // open this macro to enable floating point calculation

int rockchip_calc_post_csc_coefs(const struct post_csc *csc_cfg, // [I] CSC config
    const struct post_csc_convert_mode *convert_mode,            // [I] CSC convert mode
    struct post_csc_coef *csc_simple_coef                        // [O] return CSC coefs
);

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

extern const struct post_csc_convert_mode g_supported_standard_convert_mode[DRM_CSC_MODE_MAX];
extern const int g_csc_max_coef_precision;


#endif // _ROCKCHIP_POST_CSC2_H
