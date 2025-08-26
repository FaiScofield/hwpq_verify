// SPDX-License-Identifier: (GPL-2.0+ OR MIT)
/*
 * Copyright (c) 2022 Rockchip Electronics Co., Ltd.
 * Author: Zhang yubing <yubing.zhang@rock-chips.com>
 */

#include "rockchip_post_csc.h"

#define _USE_MATH_DEFINES // define this before including math.h to get M_PI
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#ifndef ABS
#define ABS(x) ((x) >= 0 ? (x) : -(x))
#endif
#ifndef ROUND
#define ROUND(x) ((x) >= 0 ? ((x) + 0.5f) : ((x) - 0.5f))
#endif

union csc_matrix_f32
{
    struct
    {
        float csc_coef00;
        float csc_coef01;
        float csc_coef02;
        float csc_coef10;
        float csc_coef11;
        float csc_coef12;
        float csc_coef20;
        float csc_coef21;
        float csc_coef22;
    };
    float val[3][3];
};

union csc_matrix_s32
{
    struct
    {
        s32 csc_coef00;
        s32 csc_coef01;
        s32 csc_coef02;
        s32 csc_coef10;
        s32 csc_coef11;
        s32 csc_coef12;
        s32 csc_coef20;
        s32 csc_coef21;
        s32 csc_coef22;
    };
    s32 val[3][3];
};

union csc_vector_s32
{
    struct
    {
        s32 csc_offset0;
        s32 csc_offset1;
        s32 csc_offset2;
    };
    s32 val[3];
};

static const union csc_matrix_f32 g_identity_mat_f32 = {1.f, 0.f, 0.f, 0.f, 1.f, 0.f, 0.f, 0.f, 1.f};

#if 1   /* matrix from Rec ITU-R BT.601-7 / BT.709-6 / BT.2020-2 */
static const union csc_matrix_f32 g_r2y_mat_bt601_f32 = {
    0.299f, 0.587f, 0.114f, -0.168736f, -0.331264f, 0.5, 0.5, -0.418688f, -0.081312f};
static const union csc_matrix_f32 g_y2r_mat_bt601_f32 = {
    1.f, 0.f, 1.402f, 1.f, -0.344136f, -0.714136f, 1.f, 1.772f, 0.f};
static const union csc_matrix_f32 g_r2y_mat_bt709_f32 = {
    0.2126f, 0.7152f, 0.0722f, -0.114572f, -0.385428f, 0.5f, 0.5f, -0.454153f, -0.045847f};
static const union csc_matrix_f32 g_y2r_mat_bt709_f32 = {
    1.f, 0.f, 1.5748f, 1.f, -0.187324f, -0.468124f, 1.f, 1.8556f, 0.f};
static const union csc_matrix_f32 g_r2y_mat_bt2020_f32 = {
    0.2627f, 0.678f, 0.0593f, -0.13963f, -0.36037f, 0.5f, 0.5f, -0.459786f, -0.040214f};
static const union csc_matrix_f32 g_y2r_mat_bt2020_f32 = {
    1.f, 0.f,  1.4746f, 1.f, -0.164553f, -0.571353f, 1.f, 1.8814f, 0.f};
#else   /* matrix from xyz calculation */
static const union csc_matrix_f32 g_r2y_mat_bt601_f32 = {
    0.298939f, 0.586625f, 0.114436f, -0.168785f, -0.331215f, 0.5f, 0.5f, -0.418384f, -0.081616f};
static const union csc_matrix_f32 g_y2r_mat_bt601_f32 = {
    1.f, 0.f, 1.402122f, 1.f, -0.345502f, -0.714509f, 1.f, 1.771129f, 0.f};
static const union csc_matrix_f32 g_r2y_mat_bt709_f32 = {
    0.212639f, 0.715169f, 0.072192f, -0.114592f, -0.385408f, 0.5f, 0.5f, -0.454156f, -0.045844f};
static const union csc_matrix_f32 g_y2r_mat_bt709_f32 = {
    1.f, 0.f, 1.574722f, 1.f, -0.187314f, -0.468207f, 1.f, 1.855615f, 0.f};
static const union csc_matrix_f32 g_r2y_mat_bt2020_f32 = {
    0.262700f, 0.677998f, 0.059302f, -0.139630f, -0.360370f, 0.5f, 0.5f, -0.459785f, -0.040215f};
static const union csc_matrix_f32 g_y2r_mat_bt2020_f32 = {
    1.f, 0.f, 1.474600f, 1.f, -0.164558f, -0.571355f, 1.f, 1.881397f, 0.f};
#endif


static inline void csc_matrix_mul_f32(union csc_matrix_f32 * dst, const union csc_matrix_f32 *m0, const union csc_matrix_f32 *m1)
{
    dst->val[0][0] = m0->val[0][0] * m1->val[0][0] + m0->val[0][1] * m1->val[1][0] + m0->val[0][2] * m1->val[2][0];
    dst->val[0][1] = m0->val[0][0] * m1->val[0][1] + m0->val[0][1] * m1->val[1][1] + m0->val[0][2] * m1->val[2][1];
    dst->val[0][2] = m0->val[0][0] * m1->val[0][2] + m0->val[0][1] * m1->val[1][2] + m0->val[0][2] * m1->val[2][2];
    dst->val[1][0] = m0->val[1][0] * m1->val[0][0] + m0->val[1][1] * m1->val[1][0] + m0->val[1][2] * m1->val[2][0];
    dst->val[1][1] = m0->val[1][0] * m1->val[0][1] + m0->val[1][1] * m1->val[1][1] + m0->val[1][2] * m1->val[2][1];
    dst->val[1][2] = m0->val[1][0] * m1->val[0][2] + m0->val[1][1] * m1->val[1][2] + m0->val[1][2] * m1->val[2][2];
    dst->val[2][0] = m0->val[2][0] * m1->val[0][0] + m0->val[2][1] * m1->val[1][0] + m0->val[2][2] * m1->val[2][0];
    dst->val[2][1] = m0->val[2][0] * m1->val[0][1] + m0->val[2][1] * m1->val[1][1] + m0->val[2][2] * m1->val[2][1];
    dst->val[2][2] = m0->val[2][0] * m1->val[0][2] + m0->val[2][1] * m1->val[1][2] + m0->val[2][2] * m1->val[2][2];
}

static inline void csc_matrix_mul_s32(union csc_matrix_s32 *dst, const union csc_matrix_s32 *m0, const union csc_matrix_s32 *m1)
{
    dst->val[0][0] = m0->val[0][0] * m1->val[0][0] + m0->val[0][1] * m1->val[1][0] + m0->val[0][2] * m1->val[2][0];
    dst->val[0][1] = m0->val[0][0] * m1->val[0][1] + m0->val[0][1] * m1->val[1][1] + m0->val[0][2] * m1->val[2][1];
    dst->val[0][2] = m0->val[0][0] * m1->val[0][2] + m0->val[0][1] * m1->val[1][2] + m0->val[0][2] * m1->val[2][2];
    dst->val[1][0] = m0->val[1][0] * m1->val[0][0] + m0->val[1][1] * m1->val[1][0] + m0->val[1][2] * m1->val[2][0];
    dst->val[1][1] = m0->val[1][0] * m1->val[0][1] + m0->val[1][1] * m1->val[1][1] + m0->val[1][2] * m1->val[2][1];
    dst->val[1][2] = m0->val[1][0] * m1->val[0][2] + m0->val[1][1] * m1->val[1][2] + m0->val[1][2] * m1->val[2][2];
    dst->val[2][0] = m0->val[2][0] * m1->val[0][0] + m0->val[2][1] * m1->val[1][0] + m0->val[2][2] * m1->val[2][0];
    dst->val[2][1] = m0->val[2][0] * m1->val[0][1] + m0->val[2][1] * m1->val[1][1] + m0->val[2][2] * m1->val[2][1];
    dst->val[2][2] = m0->val[2][0] * m1->val[0][2] + m0->val[2][1] * m1->val[1][2] + m0->val[2][2] * m1->val[2][2];
}

static inline void csc_matrix_vector_mul_s32(union csc_vector_s32 *dst, const union csc_matrix_s32 *m0,
    const union csc_vector_s32 *v0)
{
    dst->val[0] = m0->val[0][0] * v0->val[0] + m0->val[0][1] * v0->val[1] + m0->val[0][2] * v0->val[2];
    dst->val[1] = m0->val[1][0] * v0->val[0] + m0->val[1][1] * v0->val[1] + m0->val[1][2] * v0->val[2];
    dst->val[2] = m0->val[2][0] * v0->val[0] + m0->val[2][1] * v0->val[1] + m0->val[2][2] * v0->val[2];
}

static void csc_get_range_conversion_matrix_offset(const struct post_csc_convert_mode *mode,
    union csc_matrix_f32 *range_mat_i, union csc_matrix_f32 *range_mat_o,
    union csc_vector_s32 *offset_vec_i, union csc_vector_s32 *offset_vec_o)
{
    // assert(mode->pixel_depth >= 8);
    const int ratio_gain = 1 << (mode->pixel_depth - 8);
    const int ratio_denorm = (1 << mode->pixel_depth) - 1;

    union csc_vector_s32 offset_i = {0};
    union csc_vector_s32 offset_o = {0};
    memset(range_mat_i, 0, sizeof(union csc_matrix_f32));
    memset(range_mat_o, 0, sizeof(union csc_matrix_f32));
    memset(offset_vec_i, 0, sizeof(union csc_vector_s32));
    memset(offset_vec_o, 0, sizeof(union csc_vector_s32));

    /* get matrix and vector for input */
    // F2F case
    float ratio_y = 1.f;
    float ratio_c = 1.f;
    float offset_y = 0;
    float offset_c = mode->is_input_yuv ? 128 : 0;
    // L2F case
    if (!mode->is_input_full_range)
    {
        ratio_y = (235.f - 16.f) * ratio_gain / ratio_denorm;
        offset_y = 16;
        if (mode->is_input_yuv)
        { // L2F_yuv case
            ratio_c = (240.f - 16.f) * ratio_gain / ratio_denorm;
            offset_c = 128;
        }
        else
        { // L2F_rgb case
            ratio_c = ratio_y;
            offset_c = offset_y;
        }
    }
    range_mat_i->val[0][0] = 1.f / ratio_y;
    range_mat_i->val[1][1] = 1.f / ratio_c;
    range_mat_i->val[2][2] = 1.f / ratio_c;
    offset_vec_i->val[0] = -offset_y * ratio_gain;
    offset_vec_i->val[1] = -offset_c * ratio_gain;
    offset_vec_i->val[2] = -offset_c * ratio_gain;

    /* get matrix and vector for output */
    // F2F case
    ratio_y = 1.f;
    ratio_c = 1.f;
    offset_y = 0;
    offset_c = mode->is_output_yuv ? 128 : 0;
    // F2L case
    if (!mode->is_output_full_range)
    {
        ratio_y = (235.f - 16.f) * ratio_gain / ratio_denorm;
        offset_y = 16;
        if (mode->is_output_yuv)
        { // F2L_yuv case
            ratio_c = (240.f - 16.f) * ratio_gain / ratio_denorm;
            offset_c = 128;
        }
        else
        { // F2L_rgb case
            ratio_c = ratio_y;
            offset_c = offset_y;
        }
    }
    range_mat_o->val[0][0] = ratio_y;
    range_mat_o->val[1][1] = ratio_c;
    range_mat_o->val[2][2] = ratio_c;
    offset_vec_o->val[0] = offset_y * ratio_gain;
    offset_vec_o->val[1] = offset_c * ratio_gain;
    offset_vec_o->val[2] = offset_c * ratio_gain;
}

static void csc_get_space_conversion_matrix(const struct post_csc_convert_mode *mode, union csc_matrix_f32 *convert_mat)
{
    union csc_matrix_f32 *range_mat_i;
    union csc_matrix_f32 *pOutputRangeMat;

    // R2R case
    if (mode->is_input_yuv == 0 && mode->is_output_yuv == 0) {
        memcpy(convert_mat, &g_identity_mat_f32, sizeof(union csc_matrix_f32));
    }
    // R2Y case
    else if (mode->is_input_yuv == 0 && mode->is_output_yuv == 1)
    {
        if (mode->output_color_encoding == DRM_COLOR_YCBCR_BT601)
            memcpy(convert_mat, &g_r2y_mat_bt601_f32, sizeof(union csc_matrix_f32));
        else if (mode->output_color_encoding == DRM_COLOR_YCBCR_BT2020)
            memcpy(convert_mat, &g_r2y_mat_bt2020_f32, sizeof(union csc_matrix_f32));
        else //if (mode->output_color_encoding == DRM_COLOR_YCBCR_BT709)
            memcpy(convert_mat, &g_r2y_mat_bt709_f32, sizeof(union csc_matrix_f32));
    }
    // Y2R case
    else if (mode->is_input_yuv == 1 && mode->is_output_yuv == 0)
    {
        if (mode->input_color_encoding == DRM_COLOR_YCBCR_BT601)
            memcpy(convert_mat, &g_y2r_mat_bt601_f32, sizeof(union csc_matrix_f32));
        else if (mode->input_color_encoding == DRM_COLOR_YCBCR_BT2020)
            memcpy(convert_mat, &g_y2r_mat_bt2020_f32, sizeof(union csc_matrix_f32));
        else //if (mode->input_color_encoding == DRM_COLOR_YCBCR_BT709)
            memcpy(convert_mat, &g_y2r_mat_bt709_f32, sizeof(union csc_matrix_f32));
    }
    // Y2Y case with L2L or F2F
    else if (mode->input_color_encoding == mode->output_color_encoding) {
        memcpy(convert_mat, &g_identity_mat_f32, sizeof(union csc_matrix_f32));
    }
    // Y2Y case with L2F or F2L
    else
    {
        const union csc_matrix_f32 *mat_y2r, *mat_r2y;
        if (mode->input_color_encoding == DRM_COLOR_YCBCR_BT601)
            mat_y2r = &g_y2r_mat_bt601_f32;
        else if (mode->input_color_encoding == DRM_COLOR_YCBCR_BT2020)
            mat_y2r = &g_y2r_mat_bt2020_f32;
        else //if (mode->input_color_encoding == DRM_COLOR_YCBCR_BT709)
            mat_y2r = &g_y2r_mat_bt709_f32;
        if (mode->output_color_encoding == DRM_COLOR_YCBCR_BT601)
            mat_r2y = &g_r2y_mat_bt601_f32;
        else if (mode->output_color_encoding == DRM_COLOR_YCBCR_BT2020)
            mat_r2y = &g_r2y_mat_bt2020_f32;
        else //if (mode->output_color_encoding == DRM_COLOR_YCBCR_BT709)
            mat_r2y = &g_r2y_mat_bt709_f32;
        csc_matrix_mul_f32(convert_mat, mat_r2y, mat_y2r);
    }
}

static void csc_adjust_convert_matrix(const struct post_csc_convert_mode *mode,
    const struct post_csc *bcsh_cfg, union csc_matrix_f32 *out_mat, union csc_vector_s32 *out_vec)
{
    union csc_matrix_f32 M0 = {0}, M1 = {0};
    union csc_matrix_f32 tmp0 = {0}, tmp1 = {0};
    const union csc_matrix_f32 *r2y_matrix = NULL;
    const union csc_matrix_f32 *y2r_matrix = NULL;
    const struct rk_csc_colorspace_info *color_info;

    // assert(mode->pixel_depth >= 8 && mode->pixel_depth <= 10);
    const float contrast = bcsh_cfg->contrast / 256.f;                       // [0, 511] -> [0, 2)
    const float saturation = bcsh_cfg->saturation / 256.f;                   // [0, 511] -> [0, 2)
    const float r_gain = bcsh_cfg->r_gain / 256.f;                           // [0, 511] -> [0, 2)
    const float g_gain = bcsh_cfg->g_gain / 256.f;                           // [0, 511] -> [0, 2)
    const float b_gain = bcsh_cfg->b_gain / 256.f;                           // [0, 511] -> [0, 2)
    const float hue_rad = (bcsh_cfg->hue - 256) * 30 / 256.f * M_PI / 180.f; // [0, 511] -> [-pi/6, pi/6]
    const float cos_hue = cos(hue_rad);
    const float sin_hue = sin(hue_rad);
    const s32 offset_shift_bits = 3 - (mode->pixel_depth - 8);                              // [1, 3]
    const s32 r_offset = ((s32)bcsh_cfg->r_offset - 256) >> offset_shift_bits; // [-32, 32) for U8
    const s32 g_offset = ((s32)bcsh_cfg->g_offset - 256) >> offset_shift_bits; // [-32, 32) for U8
    const s32 b_offset = ((s32)bcsh_cfg->b_offset - 256) >> offset_shift_bits; // [-32, 32) for U8
    s32 brightness = (s32)bcsh_cfg->brightness - 256;
    if (mode->pixel_depth <= 10) {
        brightness >>= 10 - mode->pixel_depth; // [-64, 64) for U8
    } else {
        brightness <<= mode->pixel_depth - 10; // [-256, 256) for U10
    }

    const union csc_matrix_f32 gain_matrix = {r_gain, 0.f, 0.f, 0.f, g_gain, 0.f, 0.f, 0.f, b_gain};
    const union csc_matrix_f32 contrast_matrix = {contrast, 0.f, 0.f, 0.f, contrast, 0.f, 0.f, 0.f, contrast};
    const union csc_matrix_f32 hue_matrix = {1.f, 0.f, 0.f, 0.f, cos_hue, sin_hue, 0.f, -sin_hue, cos_hue};
    const union csc_matrix_f32 saturation_matrix = {saturation, 0.f, 0.f, 0.f, saturation, 0.f, 0.f, 0.f, saturation};
    // const union csc_matrix_f32 r2y_for_y2y

    // M0 = hue_matrix * saturation_matrix,
    // M1 = gain_matrix * contrast_matrix,
    csc_matrix_mul_f32(&M0, &hue_matrix, &saturation_matrix);
    csc_matrix_mul_f32(&M1, &gain_matrix, &contrast_matrix);

    // Y2Y: output = T * M0 * N_r2y * M1 * N_y2r
    if (mode->is_input_yuv && mode->is_output_yuv)
    {
        r2y_matrix = &g_r2y_mat_bt709_f32;
        y2r_matrix = &g_y2r_mat_bt709_f32;
        csc_matrix_mul_f32(&tmp0, out_mat, &M0);
        csc_matrix_mul_f32(&tmp1, &tmp0, r2y_matrix);
        csc_matrix_mul_f32(&tmp0, &tmp1, &M1);
        csc_matrix_mul_f32(out_mat, &tmp0, y2r_matrix);
        out_vec->val[0] += brightness;
    }
    // Y2R: output = M1 * T * M0
    else if (mode->is_input_yuv && !mode->is_output_yuv)
    {
        csc_matrix_mul_f32(&tmp0, &M1, out_mat);
        csc_matrix_mul_f32(out_mat, &tmp0, &M0);
        out_vec->val[0] += brightness + r_offset;
        out_vec->val[1] += brightness + g_offset;
        out_vec->val[2] += brightness + b_offset;
    }
    // R2Y: output = M0 * T * M1
    else if (!mode->is_input_yuv && mode->is_output_yuv)
    {
        csc_matrix_mul_f32(&tmp0, &M0, out_mat);
        csc_matrix_mul_f32(out_mat, &tmp0, &M1);
        out_vec->val[0] += brightness;
    }
    // R2R: output = T * M1 * N_y2r * M0 * N_r2y,
    else
    {
        r2y_matrix = &g_r2y_mat_bt709_f32;
        y2r_matrix = &g_y2r_mat_bt709_f32;
        csc_matrix_mul_f32(&tmp0, out_mat, &M1);
        csc_matrix_mul_f32(&tmp1, &tmp0, y2r_matrix);
        csc_matrix_mul_f32(&tmp0, &tmp1, &M0);
        csc_matrix_mul_f32(out_mat, &tmp0, r2y_matrix);
        out_vec->val[0] += brightness + r_offset;
        out_vec->val[1] += brightness + g_offset;
        out_vec->val[2] += brightness + b_offset;
    }
}

static void csc_swap_color_channel(const struct post_csc_convert_mode *mode,
    union csc_matrix_s32 *out_mat, union csc_vector_s32 *out_vec)
{
    static const union csc_matrix_s32 rgb_input_swap_matrix = {0, 0, 1, 1, 0, 0, 0, 1, 0}; // BRG ?
    static const union csc_matrix_s32 yuv_output_swap_matrix = {0, 0, 1, 1, 0, 0, 0, 1, 0}; // VYU
    union csc_matrix_s32 tmp_mat = {0};
    union csc_vector_s32 tmp_vec = {0};

    if (mode->swap_channels)
    {
        if (!mode->is_input_yuv)
        {
            memcpy(&tmp_mat, out_mat, sizeof(union csc_matrix_s32));
            csc_matrix_mul_s32(out_mat, &tmp_mat, &rgb_input_swap_matrix);
        }
        if (mode->is_output_yuv)
        {
            memcpy(&tmp_mat, out_mat, sizeof(union csc_matrix_s32));
            memcpy(&tmp_vec, out_vec, sizeof(union csc_vector_s32));
            csc_matrix_mul_s32(out_mat, &yuv_output_swap_matrix, &tmp_mat);
            csc_matrix_vector_mul_s32(out_vec, &yuv_output_swap_matrix, &tmp_vec);
        }
        // printf("NOTE: CSC coefs & offset has been swapped!\n");
    }
}

static void csc_get_fixed_coefs_matrix(const union csc_matrix_f32 *mat, union csc_matrix_s32 *fixed_mat, const int coef_precision)
{
    const int fator = 1 << coef_precision;
    fixed_mat->val[0][0] = (int)(mat->val[0][0] * fator + (mat->val[0][0] >= 0 ? 0.5f : -0.5f));
    fixed_mat->val[0][1] = (int)(mat->val[0][1] * fator + (mat->val[0][1] >= 0 ? 0.5f : -0.5f));
    fixed_mat->val[0][2] = (int)(mat->val[0][2] * fator + (mat->val[0][2] >= 0 ? 0.5f : -0.5f));
    fixed_mat->val[1][0] = (int)(mat->val[1][0] * fator + (mat->val[1][0] >= 0 ? 0.5f : -0.5f));
    fixed_mat->val[1][1] = (int)(mat->val[1][1] * fator + (mat->val[1][1] >= 0 ? 0.5f : -0.5f));
    fixed_mat->val[1][2] = (int)(mat->val[1][2] * fator + (mat->val[1][2] >= 0 ? 0.5f : -0.5f));
    fixed_mat->val[2][0] = (int)(mat->val[2][0] * fator + (mat->val[2][0] >= 0 ? 0.5f : -0.5f));
    fixed_mat->val[2][1] = (int)(mat->val[2][1] * fator + (mat->val[2][1] >= 0 ? 0.5f : -0.5f));
    fixed_mat->val[2][2] = (int)(mat->val[2][2] * fator + (mat->val[2][2] >= 0 ? 0.5f : -0.5f));
}

static bool csc_fixed_coefs_fine_tuning(const struct post_csc_convert_mode *mode, const union csc_matrix_f32 *float_mat,
    union csc_matrix_s32 *fixed_mat)
{
    bool ret = false;
    const int coef_factor = 1 << mode->coef_precision;
    const int max_pixel_val = (1 << mode->pixel_depth) - 1;
    int denorms[3] = {coef_factor, 0, 0};
    const float ratio_y = (219 << (mode->pixel_depth - 8)) / (float)max_pixel_val;
    const float ratio_c = (224 << (mode->pixel_depth - 8)) / (float)max_pixel_val;
    if (mode->is_input_full_range && !mode->is_output_full_range) { // F2L
        denorms[0] = ROUND(coef_factor * ratio_y);
    } else if (!mode->is_input_full_range && mode->is_output_full_range) { // L2F
        denorms[0] = ROUND(coef_factor / ratio_y);
    }

    // R2Y case
    if (!mode->is_input_yuv && mode->is_output_yuv)
    {
        int row_sums[3] = {0};
        row_sums[0] = fixed_mat->val[0][0] + fixed_mat->val[0][1] + fixed_mat->val[0][2];
        row_sums[1] = fixed_mat->val[1][0] + fixed_mat->val[1][1] + fixed_mat->val[1][2];
        row_sums[2] = fixed_mat->val[2][0] + fixed_mat->val[2][1] + fixed_mat->val[2][2];

        for (int i = 0; i < 3; ++i)
        {
            if (row_sums[i] != denorms[i])
            {
                const int delta = denorms[i] - row_sums[i];
                int col = -1;
                float min_diff = 999999.f;
                for (int j = 0; j < 3; ++j)
                {
                    float diff = ABS((float)(fixed_mat->val[i][j] + delta) - float_mat->val[i][j] * coef_factor);
                    if (diff < min_diff) {
                        min_diff = diff;
                        col = j;
                    }
                }
                printf("NOTE: fine-tuning CSC coef[%d][%d] = %d => %d, since row_sums[%d] = %d != %d, delta = %d.\n",
                    i, col, fixed_mat->val[i][col], fixed_mat->val[i][col] + delta, i, row_sums[i], denorms[i], delta);
                fixed_mat->val[i][col] += delta;
            }
        }
    }
    // Y2R case
    else if (mode->is_input_yuv && !mode->is_output_yuv)
    {
        if (fixed_mat->val[0][0] != denorms[0]) {
            printf("NOTE: fine-tuning CSC coef[0][0] = %d => %d, since RY2 case!\n", fixed_mat->val[0][0], denorms[0]);
            fixed_mat->val[0][0] = denorms[0];
        }
        if (fixed_mat->val[1][0] != denorms[0]) {
            printf("NOTE: fine-tuning CSC coef[1][0] = %d => %d, since RY2 case!\n", fixed_mat->val[1][0], denorms[0]);
            fixed_mat->val[1][0] = denorms[0];
        }
        if (fixed_mat->val[2][0] != denorms[0]) {
            printf("NOTE: fine-tuning CSC coef[2][0] = %d => %d, since RY2 case!\n", fixed_mat->val[2][0], denorms[0]);
            fixed_mat->val[2][0] = denorms[0];
        }
        if (fixed_mat->val[0][1] != 0) {
            printf("NOTE: fine-tuning CSC coef[0][1] = %d => 0, since RY2 case!\n", fixed_mat->val[0][1]);
            fixed_mat->val[0][1] = 0;
        }
        if (fixed_mat->val[2][2] != 0) {
            printf("NOTE: fine-tuning CSC coef[1][0] = %d => 0, since RY2 case!\n", fixed_mat->val[2][2]);
            fixed_mat->val[2][2] = 0;
        }
    }

    return ret;
}

static void csc_get_fixed_coefs_offset(const union csc_matrix_s32 *fixed_mat, const union csc_vector_s32 *offset_vec_i,
    const union csc_vector_s32 *offset_vec_o, union csc_vector_s32 *final_vec, const int coef_precision)
{
    const int factor = 1 << coef_precision;
    union csc_vector_s32 tmp_vec = {0};
    csc_matrix_vector_mul_s32(&tmp_vec, fixed_mat, offset_vec_i);
    final_vec->val[0] = tmp_vec.val[0] + offset_vec_o->val[0] * factor;
    final_vec->val[1] = tmp_vec.val[1] + offset_vec_o->val[1] * factor;
    final_vec->val[2] = tmp_vec.val[2] + offset_vec_o->val[2] * factor;
}


int rockchip_calc_post_csc_coefs(const struct post_csc *bcsh_cfg, // [I] CSC config
    const struct post_csc_convert_mode *convert_mode,             // [I] CSC convert mode
    struct post_csc_coef *csc_simple_coef                         // [O] return CSC coefs
)
{
    // assert(convert_mode->coef_precision >= convert_mode->pixel_depth);
    int ret = 0;
    union csc_matrix_f32 range_mat_i = {0}, range_mat_o = {0};
    union csc_matrix_f32 color_convert_mat = {0}, tmp_mat = {0}, final_mat = {0};
    union csc_matrix_s32 final_mat_fix = {0};
    union csc_vector_s32 range_ofs_i = {0}, range_ofs_o = {0}, final_vec = {0};

    // get convert mat & vec first
    csc_get_range_conversion_matrix_offset(convert_mode, &range_mat_i, &range_mat_o, &range_ofs_i, &range_ofs_o);
    csc_get_space_conversion_matrix(convert_mode, &color_convert_mat);
    csc_matrix_mul_f32(&tmp_mat, &range_mat_o, &color_convert_mat);
    csc_matrix_mul_f32(&final_mat, &tmp_mat, &range_mat_i);

    // adjust final_mat with bsch configs
    if (bcsh_cfg && bcsh_cfg->csc_enable) {
        csc_adjust_convert_matrix(convert_mode, bcsh_cfg, &final_mat, &range_ofs_o);
    }

    // get fixed mat
    csc_get_fixed_coefs_matrix(&final_mat, &final_mat_fix, convert_mode->coef_precision);

    // TODO: fine-tuning for fixed matrix (R2Y)
    bool fine_tuned = false;
    if (!bcsh_cfg || !bcsh_cfg->csc_enable) {
        fine_tuned = csc_fixed_coefs_fine_tuning(convert_mode, &final_mat, &final_mat_fix);
    }

    // get fixed vec
    csc_get_fixed_coefs_offset(&final_mat_fix, &range_ofs_i, &range_ofs_o, &final_vec, convert_mode->coef_precision);

    // swap channles if necessary
    csc_swap_color_channel(convert_mode, &final_mat_fix, &final_vec);

    // return final mat_coefs & vec_offset
    csc_simple_coef->csc_coef00 = final_mat_fix.csc_coef00;
    csc_simple_coef->csc_coef01 = final_mat_fix.csc_coef01;
    csc_simple_coef->csc_coef02 = final_mat_fix.csc_coef02;
    csc_simple_coef->csc_coef10 = final_mat_fix.csc_coef10;
    csc_simple_coef->csc_coef11 = final_mat_fix.csc_coef11;
    csc_simple_coef->csc_coef12 = final_mat_fix.csc_coef12;
    csc_simple_coef->csc_coef20 = final_mat_fix.csc_coef20;
    csc_simple_coef->csc_coef21 = final_mat_fix.csc_coef21;
    csc_simple_coef->csc_coef22 = final_mat_fix.csc_coef22;
    csc_simple_coef->csc_dc0 = final_vec.csc_offset0;
    csc_simple_coef->csc_dc1 = final_vec.csc_offset1;
    csc_simple_coef->csc_dc2 = final_vec.csc_offset2;
    csc_simple_coef->range_type = convert_mode->is_output_full_range;

    return ret;
}