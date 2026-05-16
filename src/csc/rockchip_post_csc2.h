/* SPDX-License-Identifier: (GPL-2.0+ OR MIT) */
/**
 * @copyright: Copyright (C) Rockchip Electronics Co., Ltd.
 * @note: Base on 'rockchip_post_csc.h' from the 'drm' project.
 *        This is not the offical updated version but a new implementation for HWPQ kernel verification.
 * @author: vance.wu@rock-chips.com
 * @history:
 *  - 2025-10-15 vance.wu: add auxiliary function 'parse_csc_mode_str'.
 *  - 2025-09-04 vance.wu: new implementation for HWPQ kernel verification.
 */

#ifndef _ROCKCHIP_POST_CSC2_H
#define _ROCKCHIP_POST_CSC2_H

#include "../kernel/rockchip_drm_drv.h"
#include "../kernel/rockchip_drm_vop.h"

// int rockchip_calc_post_csc(const struct post_csc *csc_cfg, // [I] CSC config
//     struct post_csc_coef *csc_simple_coef,                 // [O] return CSC coefs
//     const struct post_csc_convert_mode *convert_mode       // [I] CSC convert mode
// );

#define csc_simple_round(x, n) \
    (((x) + (1 << ((n) - 1)) + ((x) >> 31)) >> (n)) // right shift by n, round to nearest integer

#define ENABLE_POST_CSC_FLOATING_POINT (1) // open this macro to enable floating point calculation
#define CSC_MODE_MAX                   (41)

int rockchip_calc_post_csc_coefs(const struct post_csc *csc_cfg, // [I] CSC config
    struct post_csc_coef *csc_simple_coef,                       // [O] return CSC coefs
    const struct post_csc_convert_mode *convert_mode             // [I] CSC convert mode
);

int get_csc_coefs_float(const struct post_csc *bcsh_cfg, // [I] CSC config
    const struct post_csc_convert_mode *convert_mode,    // [I] CSC convert mode
    float *ret_csc_coef_x12                              // [O] return CSC coefs float
);

int csc_get_mode_index(const struct post_csc_convert_mode *convert_mode);

/* parse mode string like 'rgbl_to_601f' */
int parse_csc_mode_str(const char *mode_str, struct post_csc_convert_mode *mode);

const char *csc_plat_name_str(int plat);

extern const struct post_csc_convert_mode g_supported_standard_convert_mode[CSC_MODE_MAX];
extern const char *g_supported_csc_mode_str[CSC_MODE_MAX];

#endif // _ROCKCHIP_POST_CSC2_H
