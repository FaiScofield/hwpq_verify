/**
 * @copyright: Copyright (c) Rockchip Electronics Co., Ltd. 2026-. All rights reserved.
 * @brief:     Color conversion
 * @author:    vance.wu@rock-chips.com
 * @create:    2026-04-18
 */

#ifndef _PIXFMT_COLOR_H_
#define _PIXFMT_COLOR_H_

typedef enum pixfmt_colorspcae {
    PIXFMT_CLRSPC_UNKNOWN = -1,
    PIXFMT_CLRSPC_RGB_LIMITED,
    PIXFMT_CLRSPC_RGB_FULL,
    PIXFMT_CLRSPC_YUV_601L,
    PIXFMT_CLRSPC_YUV_601F,
    PIXFMT_CLRSPC_YUV_709L,
    PIXFMT_CLRSPC_YUV_709F,
    PIXFMT_CLRSPC_YUV_2020L,
    PIXFMT_CLRSPC_YUV_2020F,
} pixfmt_colorspcae_e;


#endif /* _PIXFMT_COLOR_H_ */