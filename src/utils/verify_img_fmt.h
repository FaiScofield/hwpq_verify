/**
 * @copyright Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @description: verify_img_fmt.h
 * @author: vance.wu@rock-chips.com
 * @create: 2025-09-05
 * @history:
 *  2025-10-12 vance.wu: Add function 'common_verify_imgfmt_pitch_ratio' to calculate row pitch (unit: byte).
 */

#ifndef _VERIFY_IMG_FMT_H_
#define _VERIFY_IMG_FMT_H_

#ifdef __cplusplus
extern "C" {
#endif

/* image format definition */
enum common_verify_image_format
{
    RGB888 = 0,     // I
    RGBA8888 = 1,   // I
    RGB_PLANAR = 2, // I
    YUV444P = 3,    // I
    YUV444SP = 4,   // I, NV24
    YUV444I = 5,    // I
    YUV422P = 6,    // X, NV16
    YUV422SP = 7,   // X
    YUV420P = 8,    // X, NV12
    YUV420SP = 9,   // X

    RGB_101010LSB = RGB888 + 10,       // IO
    RGB_PLANAR10LSB = RGB_PLANAR + 10, // IO
    YUV444P_10LSB = YUV444P + 10,      // IO
    YUV444SP_10LSB = YUV444SP + 10,    // IO
    YUV444I_10LSB = YUV444I + 10,      // IO
    YUV422P_10LSB = YUV422P + 10,      // X
    YUV422SP_10LSB = YUV422SP + 10,    // X
    YUV420P_10LSB = YUV420P + 10,      // X
    YUV420SP_10LSB = YUV420SP + 10,    // X

    RGB_10PACKED = RGB888 + 20,           // IO
    RGBA_1010102 = RGBA8888 + 20,         // IO, [A2:B10:G10:R10]
    RGB_PLANAR10PACKED = RGB_PLANAR + 20, // IO
    YUV444P_10PACKED = YUV444P + 20,      // IO
    YUV444SP_10PACKED = YUV444SP + 20,    // IO
    YUV444I_10PACKED = YUV444I + 20,      // IO
    YUV422P_10PACKED = YUV422P + 20,      // X
    YUV422SP_10PACKED = YUV422SP + 20,    // IO
    YUV420P_10PACKED = YUV420P + 20,      // X
    YUV420SP_10PACKED = YUV420SP + 20,    // IO

    ABGR_2101010 = RGBA_1010102, // same to RGBA_1010102
};

const char *common_verify_imgfmt_str(int fmt);
const char *common_verify_imgfmt_exten_str(int fmt);
int common_verify_imgfmt_bpp(int fmt);
int common_verify_imgfmt_check(int fmt);
float common_verify_imgfmt_pitch_ratio(int fmt);

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