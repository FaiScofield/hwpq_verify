/**
 * @copyright: Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @bref:      verify_img_fmt.c
 * @author:    vance.wu@rock-chips.com
 * @create:    2025-09-05
 * @modifier:  vance.wu@rock-chips.com
 * @modify:    2026-03-10
 */

#include "verify_img_fmt.h"
#include "verify_com.h"

const char *common_verify_imgfmt_str(int fmt)
{
    switch (fmt) {
    case RGB888:             return "rgb24";
    case RGBA8888:           return "rgba32";
    case RGB_PLANAR:         return "rgb_planar";
    case YUV444P:            return "yu24";
    case YUV444SP:           return "nv24";
    case YUV444I:            return "vu24";
    case YUV422P:            return "yu16";
    case YUV422SP:           return "nv16";
    case YUV420P:            return "yu12";
    case YUV420SP:           return "nv12";
    case YUV400:             return "gray";
    case RGB_101010LSB:      return "rgb101010l";
    case RGB_PLANAR10LSB:    return "rgb10l_planar";
    case YUV444P_10LSB:      return "yuv444p10l";
    case YUV444SP_10LSB:     return "yuv444sp10l";
    case YUV444I_10LSB:      return "yuv444i10l";
    case YUV422P_10LSB:      return "yuv422p10l";
    case YUV422SP_10LSB:     return "yuv422sp10l";
    case YUV420P_10LSB:      return "yuv420p10l";
    case YUV420SP_10LSB:     return "yuv420sp10l";
    case YUV400_10LSB:       return "gray10l";
    case RGB_10PACKED:       return "rgb10bp";
    case RGBA_1010102:       return "rgba1010102";
    case RGB_PLANAR10PACKED: return "rgb10bp_planar";
    case YUV444P_10PACKED:   return "yuv444p10bp";
    case YUV444SP_10PACKED:  return "nv30";
    case YUV444I_10PACKED:   return "yuv444i10bp";
    case YUV422P_10PACKED:   return "yuv422p10bp";
    case YUV422SP_10PACKED:  return "nv20";
    case YUV420P_10PACKED:   return "yuv420p10bp";
    case YUV420SP_10PACKED:  return "nv15";
    case YUV400_10PACKED:    return "gray10bp";
    default:                 return "UnknownImgFmt";
    }
}

const char *common_verify_imgfmt_exten_str(int fmt)
{
    // valid range now: [0, 29]
    if (fmt & VERIFY_IMG_FMT_MASK) {
        return common_verify_imgfmt_is_rgb(fmt) ? "rgb" : "yuv";
    }
    LOGE("%s: UnknownImgFmt=%d!\n", __func__, fmt);
    return "bin";
}

int common_verify_imgfmt_bpp(int fmt)
{
    switch (fmt) {
    case RGBA8888:
    case RGBA_1010102:       return 32;
    case RGB888:
    case RGB_PLANAR:
    case YUV444P:
    case YUV444SP:
    case YUV444I:            return 24;
    case YUV422P:
    case YUV422SP:           return 16;
    case YUV420P:
    case YUV420SP:           return 12;
    case RGB_101010LSB:
    case RGB_PLANAR10LSB:
    case YUV444P_10LSB:
    case YUV444SP_10LSB:
    case YUV444I_10LSB:      return 48; // 24*2
    case YUV422P_10LSB:
    case YUV422SP_10LSB:     return 32; // 16*2
    case YUV420P_10LSB:
    case YUV420SP_10LSB:     return 24; // 12*2
    case RGB_10PACKED:
    case RGB_PLANAR10PACKED:
    case YUV444P_10PACKED:
    case YUV444SP_10PACKED:
    case YUV444I_10PACKED:   return 30; // 24/4*5
    case YUV422P_10PACKED:
    case YUV422SP_10PACKED:  return 20; // 16/4*5
    case YUV420P_10PACKED:
    case YUV420SP_10PACKED:  return 15; // 12/4*5
    case YUV400_10LSB:       return 16;
    case YUV400_10PACKED:    return 10;
    case YUV400:             return 8;
    default:                 LOGE("%s: UnknownImgFmt=%d!\n", __func__, fmt); return 0;
    }
}

float common_verify_imgfmt_pitch_ratio(int fmt)
{
    switch (fmt) {
    case RGB888:
    case YUV444I:            return 3.f;
    case RGBA8888:           return 4.f;
    case RGB_PLANAR:
    case YUV444P:
    case YUV444SP:
    case YUV422P:
    case YUV422SP:
    case YUV420P:
    case YUV420SP:
    case YUV400:             return 1.f;
    case RGB_101010LSB:
    case YUV444I_10LSB:      return 3 * 2.f;
    case RGB_PLANAR10LSB:
    case YUV444P_10LSB:
    case YUV444SP_10LSB:
    case YUV422P_10LSB:
    case YUV422SP_10LSB:
    case YUV420P_10LSB:
    case YUV420SP_10LSB:
    case YUV400_10LSB:       return 2.f;
    case RGB_10PACKED:
    case YUV444I_10PACKED:   return 3 * 5 / 4.f;
    case RGBA_1010102:       return 4.f;
    case RGB_PLANAR10PACKED:
    case YUV444P_10PACKED:
    case YUV444SP_10PACKED:
    case YUV422P_10PACKED:
    case YUV422SP_10PACKED:
    case YUV420P_10PACKED:
    case YUV420SP_10PACKED:
    case YUV400_10PACKED:    return 5 / 4.f;
    default:                 LOGE("%s: unsupported image format %d for now!\n", __func__, fmt); return 0.f;
    }
}

float common_verify_imgfmt_framesize_ratio(int fmt)
{
    switch (fmt) {
    case RGB888:
    case RGBA8888:
    case RGB_101010LSB:
    case RGB_10PACKED:
    case RGBA_1010102:
    case YUV400:
    case YUV400_10LSB:
    case YUV400_10PACKED:
    case YUV444I:
    case YUV444I_10LSB:
    case YUV444I_10PACKED:   return 1.f;
    case RGB_PLANAR:
    case RGB_PLANAR10LSB:
    case RGB_PLANAR10PACKED:
    case YUV444P:
    case YUV444SP:
    case YUV444P_10LSB:
    case YUV444SP_10LSB:
    case YUV444P_10PACKED:
    case YUV444SP_10PACKED:  return 3.f;
    case YUV422P:
    case YUV422SP:
    case YUV422P_10LSB:
    case YUV422SP_10LSB:
    case YUV422P_10PACKED:
    case YUV422SP_10PACKED:  return 2.f;
    case YUV420P:
    case YUV420SP:
    case YUV420P_10LSB:
    case YUV420SP_10LSB:
    case YUV420P_10PACKED:
    case YUV420SP_10PACKED:  return 1.5f;
    default:                 LOGE("%s: unsupported image format %d for now!\n", __func__, fmt); return 0.f;
    }
}

int common_verify_imgfmt_get_def_planar(int fmt, int depth)
{
    switch (fmt) {
    case RGBA8888:
    case RGB888:
    case RGB_PLANAR:         return depth <= 8 ? RGB_PLANAR : RGB_PLANAR10LSB;
    case YUV444P:
    case YUV444SP:
    case YUV444I:            return depth <= 8 ? YUV444P : YUV444P_10LSB;
    case YUV422P:
    case YUV422SP:           return depth <= 8 ? YUV422P : YUV422P_10LSB;
    case YUV420P:
    case YUV420SP:           return depth <= 8 ? YUV420P : YUV420P_10LSB;
    case RGB_101010LSB:
    case RGB_PLANAR10LSB:
    case RGBA_1010102:
    case RGB_10PACKED:
    case RGB_PLANAR10PACKED: return RGB_PLANAR10LSB;
    case YUV444P_10LSB:
    case YUV444SP_10LSB:
    case YUV444I_10LSB:
    case YUV444P_10PACKED:
    case YUV444SP_10PACKED:
    case YUV444I_10PACKED:   return YUV444P_10LSB;
    case YUV422P_10LSB:
    case YUV422SP_10LSB:
    case YUV422P_10PACKED:
    case YUV422SP_10PACKED:  return YUV422P_10LSB;
    case YUV420P_10LSB:
    case YUV420SP_10LSB:
    case YUV420P_10PACKED:
    case YUV420SP_10PACKED:  return YUV420P_10LSB;
    case YUV400:             return depth <= 8 ? YUV400 : YUV400_10LSB;
    case YUV400_10LSB:
    case YUV400_10PACKED:    return YUV400_10LSB;
    default:                 LOGE("%s: unsupported image format %d for now!\n", __func__, fmt); return -1;
    }
}

const char *common_verify_clrspc_str(int clrspc)
{
    switch (clrspc) {
    case RGBLIMIT: return "RGBL";
    case RGBFULL:  return "RGBF";
    case YUV601L:  return "YUV601L";
    case YUV601F:  return "YUV601F";
    case YUV709L:  return "YUV709L";
    case YUV709F:  return "YUV709F";
    case YUV2020L: return "YUV2020L";
    case YUV2020F: return "YUV2020F";
    default:       return "UnknownClrspc";
    }
}

int common_verify_clrspc_offset(int clrspc, int bit_depth, int *offsetx3)
{
    if (!offsetx3) {
        return -1;
    }
    if (bit_depth != 8 && bit_depth != 10 && bit_depth != 13) {
        LOGE("%s: Unsupported bit_depth=%d! It should be 8/10/13.\n", __func__, bit_depth);
        return -1;
    }
    int offset[3] = {0, 128, 128};
    switch (clrspc) {
    case RGBLIMIT: offset[0] = offset[1] = offset[2] = 16; break;
    case RGBFULL:  offset[0] = offset[1] = offset[2] = 0; break;
    case YUV601L:
    case YUV709L:
    case YUV2020L:
        offset[0] = 16;
        offset[1] = offset[2] = 128;
        break;
    case YUV601F:
    case YUV709F:
    case YUV2020F:
        offset[0] = 0;
        offset[1] = offset[2] = 128;
        break;
    default: LOGE("%s: UnknownClrspc=%d!\n", __func__, clrspc); return -1;
    }

    offsetx3[0] = offset[0] << (bit_depth - 8);
    offsetx3[1] = offset[1] << (bit_depth - 8);
    offsetx3[2] = offset[2] << (bit_depth - 8);
    return 0;
}

int common_verify_clrspc_to_kernel_encoding(int clrspc)
{
    switch (clrspc) {
    case RGBLIMIT:
    case RGBFULL:  return -2;
    case YUV601L:
    case YUV601F:  return 0;
    case YUV709L:
    case YUV709F:  return 1;
    case YUV2020L:
    case YUV2020F: return 2;
    default:       LOGE("%s: UnknownClrspc=%d!\n", __func__, clrspc); return -1;
    }
}