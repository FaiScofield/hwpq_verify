/**
 * @copyright: Copyright (c) Rockchip Electronics Co., Ltd. 2026-. All rights reserved.
 * @brief:     Color space conversion definitions
 * @author:    vance.wu@rock-chips.com
 * @create:    2026-05-16
 */

#include "pixfmt_csc.h"
#include "pixfmt_cvt.h"

#include <string.h>

const char *pixfmt_colorspcae_name(pixfmt_colorspcae_e clrspc)
{
    switch (clrspc) {
    case PIXFMT_CLRSPC_RGB_LIMITED: return "RGB_Limited";
    case PIXFMT_CLRSPC_RGB_FULL:    return "RGB_FULL";
    case PIXFMT_CLRSPC_YUV_601L:    return "YUV_601L";
    case PIXFMT_CLRSPC_YUV_601F:    return "YUV_601F";
    case PIXFMT_CLRSPC_YUV_709L:    return "YUV_709L";
    case PIXFMT_CLRSPC_YUV_709F:    return "YUV_709F";
    case PIXFMT_CLRSPC_YUV_2020L:   return "YUV_2020L";
    case PIXFMT_CLRSPC_YUV_2020F:   return "YUV_2020F";
    default:                        return "UnknownColorSpace";
    }
}

int pixfmt_csc_exec(const pixfmt_frame_s *src, pixfmt_frame_s *dst)
{
    if (!src || !dst || !src->addr || !dst->addr)
        return -1;

    if (pixfmt_is_rgb(src->fmt) && pixfmt_is_rgb(dst->fmt)) {
        memcpy(dst->addr, src->addr, src->size);
        return 0;
    }
    if (pixfmt_is_yuv(src->fmt) && pixfmt_is_yuv(dst->fmt)) {
        memcpy(dst->addr, src->addr, src->size);
        return 0;
    }

    // TODO: implement RGB <-> YUV color space conversion
    return -1;
}
