/**
 * @copyright Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @description: verify_img_fmt.h
 * @author: vance.wu@rock-chips.com
 * @create: 2025-09-05
 * @history:
 */

#ifndef _VERIFY_IMG_FMT_H_
#define _VERIFY_IMG_FMT_H_

#ifdef __cplusplus
extern "C" {
#endif

/* image format definition */
enum common_verify_image_format
{
    RGB888 = 0,
    RGBA8888 = 1,
    RGB_PLANAR = 2,
    YUV444P = 3,
    YUV444SP = 4, // NV24
    YUV444I = 5,
    YUV422P = 6, // NV16
    YUV422SP = 7,
    YUV420P = 8, // NV12
    YUV420SP = 9,

    RGB_101010LSB = RGB888 + 10,
    RGB_PLANAR10LSB = RGB_PLANAR + 10,
    YUV444P_10LSB = YUV444P + 10,
    YUV444SP_10LSB = YUV444SP + 10,
    YUV444I_10LSB = YUV444I + 10,
    YUV422P_10LSB = YUV422P + 10,
    YUV422SP_10LSB = YUV422SP + 10,
    YUV420P_10LSB = YUV420P + 10,
    YUV420SP_10LSB = YUV420SP + 10,

    RGB_10PACKED = RGB888 + 20,
    RGBA_1010102 = RGBA8888 + 20,
    RGB_PLANAR10PACKED = RGB_PLANAR + 20,
    YUV444P_10PACKED = YUV444P + 20,
    YUV444SP_10PACKED = YUV444SP + 20,
    YUV444I_10PACKED = YUV444I + 20,
    YUV422P_10PACKED = YUV422P + 20,
    YUV422SP_10PACKED = YUV422SP + 20,
    YUV420P_10PACKED = YUV420P + 20,
    YUV420SP_10PACKED = YUV420SP + 20,
};

const char *common_verify_imgfmt_str(int fmt);
const char *common_verify_imgfmt_exten_str(int fmt);
int common_verify_imgfmt_bpp(int fmt);
int common_verify_imgfmt_check(int fmt);


/* colorspace definition */
enum common_verify_colorspace
{
    RGBLIMIT = 0x0,
    RGBFULL = 0x1,
    YUV601L = 0x2,
    YUV601F = 0x3,
    YUV709L = 0x4,
    YUV709F = 0x5,
    YUV2020L = 0x8,
    YUV2020F = 0x9,
};

const char *common_verify_clrspc_str(int clrspc);
int common_verify_clrspc_offset(int clrspc, int bit_depth, int *offsetx3);

#ifdef __cplusplus
}
#endif
#endif // _VERIFY_IMG_FMT_H_