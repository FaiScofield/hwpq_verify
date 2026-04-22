/**
 * @copyright: Copyright (c) Rockchip Electronics Co., Ltd. 2026-. All rights reserved.
 * @brief:     Color conversion
 * @author:    vance.wu@rock-chips.com
 * @create:    2026-04-18
 */

#ifndef _PIXFMT_COLOR_H_
#define _PIXFMT_COLOR_H_

#include <stdbool.h>

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

extern const char *pixfmt_colorspcae_name(pixfmt_colorspcae_e clrspc);

extern bool pixfmt_colorspcae_check_same(pixfmt_colorspcae_e clrspc0, pixfmt_colorspcae_e clrspc1)
{
    return clrspc0 != PIXFMT_CLRSPC_UNKNOWN && clrspc1 != PIXFMT_CLRSPC_UNKNOWN && (clrspc0 & 0xE) == (clrspc1 & 0xE);
}
inline bool pixfmt_colorspcae_is_fullrange(pixfmt_colorspcae_e clrspc)
{
    return clrspc != PIXFMT_CLRSPC_UNKNOWN && (clrspc & 0x1) == 1;
}
inline bool pixfmt_colorspcae_is_limitrange(pixfmt_colorspcae_e clrspc)
{
    return clrspc != PIXFMT_CLRSPC_UNKNOWN && (clrspc & 0x1) == 0;
}

#endif /* _PIXFMT_COLOR_H_ */