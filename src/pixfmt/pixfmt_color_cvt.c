#include "pixfmt_color_cvt.h"

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