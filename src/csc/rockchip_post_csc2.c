// SPDX-License-Identifier: (GPL-2.0+ OR MIT)
/*
 * Copyright (c) 2025 Rockchip Electronics Co., Ltd.
 * Author: Wu Fangyi <vance.wu@rock-chips.com>
 */

#include "rockchip_post_csc.h"
#include <assert.h>


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

static inline void csc_matrix_mul_s32(union csc_matrix_s32 *dst, const union csc_matrix_s32 *m0, const union csc_matrix_s32 *m1)
{
    assert(dst != m0 && dst != m1);
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
    assert(dst != v0);
    dst->val[0] = m0->val[0][0] * v0->val[0] + m0->val[0][1] * v0->val[1] + m0->val[0][2] * v0->val[2];
    dst->val[1] = m0->val[1][0] * v0->val[0] + m0->val[1][1] * v0->val[1] + m0->val[1][2] * v0->val[2];
    dst->val[2] = m0->val[2][0] * v0->val[0] + m0->val[2][1] * v0->val[1] + m0->val[2][2] * v0->val[2];
}

#if ENABLE_POST_CSC_FLOATING_POINT

#define _USE_MATH_DEFINES // define this before including math.h to get M_PI
#include <math.h>
#ifndef M_PI
#define M_PI 3.14159265358979323846f
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

static const union csc_matrix_f32 g_identity_mat_f32 = {1.f, 0.f, 0.f, 0.f, 1.f, 0.f, 0.f, 0.f, 1.f};

/* matrix from Rec ITU-R BT.601-7 / BT.709-6 / BT.2020-2 */
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

static void csc_get_range_conversion_matrix_offset(const struct post_csc_convert_mode *mode,
    union csc_matrix_f32 *range_mat_i, union csc_matrix_f32 *range_mat_o,
    union csc_vector_s32 *offset_vec_i, union csc_vector_s32 *offset_vec_o)
{
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
    int offset_y = mode->is_input_full_range ? 0 : 16;
    int offset_c = mode->is_input_yuv ? 128 : offset_y;
    // L2F case
    if (!mode->is_input_full_range)
    {
        ratio_y = (235 - 16) * ratio_gain / (float)ratio_denorm;
        ratio_c = mode->is_input_yuv ? (240 - 16) * ratio_gain / (float)ratio_denorm : ratio_y;
        ratio_y = 1.f / ratio_y;
        ratio_c = 1.f / ratio_c;
    }
    range_mat_i->val[0][0] = ratio_y;
    range_mat_i->val[1][1] = ratio_c;
    range_mat_i->val[2][2] = range_mat_i->val[1][1];
    offset_vec_i->val[0] = -offset_y * ratio_gain;
    offset_vec_i->val[1] = -offset_c * ratio_gain;
    offset_vec_i->val[2] = -offset_c * ratio_gain;

    /* get matrix and vector for output */
    // F2F case
    ratio_y = 1.f;
    ratio_c = 1.f;
    offset_y = mode->is_output_full_range ? 0 : 16;
    offset_c = mode->is_output_yuv ? 128 : offset_y;
    // F2L case
    if (!mode->is_output_full_range)
    {
        ratio_y = (235 - 16) * ratio_gain / (float)ratio_denorm;
        ratio_c = mode->is_output_yuv ? (240 - 16) * ratio_gain / (float)ratio_denorm : ratio_y;
    }
    range_mat_o->val[0][0] = ratio_y;
    range_mat_o->val[1][1] = ratio_c;
    range_mat_o->val[2][2] = range_mat_o->val[1][1];
    offset_vec_o->val[0] = offset_y * ratio_gain;
    offset_vec_o->val[1] = offset_c * ratio_gain;
    offset_vec_o->val[2] = offset_c * ratio_gain;
}

static void csc_get_space_conversion_matrix(const struct post_csc_convert_mode *mode, union csc_matrix_f32 *convert_mat)
{
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
    // Y2Y case with same colorspace
    else if (mode->input_color_encoding == mode->output_color_encoding) {
        memcpy(convert_mat, &g_identity_mat_f32, sizeof(union csc_matrix_f32));
    }
    // Y2Y case with different colorspace
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

    const float contrast = bcsh_cfg->contrast / 256.f;                       // [0, 511] -> [0, 2)
    const float saturation = bcsh_cfg->saturation / 256.f;                   // [0, 511] -> [0, 2)
    const float r_gain = bcsh_cfg->r_gain / 256.f;                           // [0, 511] -> [0, 2)
    const float g_gain = bcsh_cfg->g_gain / 256.f;                           // [0, 511] -> [0, 2)
    const float b_gain = bcsh_cfg->b_gain / 256.f;                           // [0, 511] -> [0, 2)
    const float hue_rad = (bcsh_cfg->hue - 256) * 30 / 256.f * M_PI / 180.f; // [0, 511] -> [-pi/6, pi/6]
    const float cos_hue = cos(hue_rad);
    const float sin_hue = sin(hue_rad);
    s32 r_offset = (s32)bcsh_cfg->r_offset - 256;
    s32 g_offset = (s32)bcsh_cfg->g_offset - 256;
    s32 b_offset = (s32)bcsh_cfg->b_offset - 256;
    s32 brightness = (s32)bcsh_cfg->brightness - 256;
    const s32 offset_shift_bits = 3 - (mode->pixel_depth - 8); // [1, 3]
    if (offset_shift_bits >= 0) {
        r_offset >>= offset_shift_bits; // [-32, 32) for U8
        g_offset >>= offset_shift_bits;
        b_offset >>= offset_shift_bits;
    } else {
        r_offset <<= -offset_shift_bits;
        g_offset <<= -offset_shift_bits;
        b_offset <<= -offset_shift_bits;
    }
    if (mode->pixel_depth <= 10) {
        brightness >>= 10 - mode->pixel_depth; // [-64, 64) for U8
    } else {
        brightness <<= mode->pixel_depth - 10; // [-256, 256) for U10
    }

    const union csc_matrix_f32 gain_matrix = {r_gain, 0.f, 0.f, 0.f, g_gain, 0.f, 0.f, 0.f, b_gain};
    const union csc_matrix_f32 contrast_matrix = {contrast, 0.f, 0.f, 0.f, contrast, 0.f, 0.f, 0.f, contrast};
    const union csc_matrix_f32 hue_matrix = {1.f, 0.f, 0.f, 0.f, cos_hue, sin_hue, 0.f, -sin_hue, cos_hue};
    const union csc_matrix_f32 saturation_matrix = {saturation, 0.f, 0.f, 0.f, saturation, 0.f, 0.f, 0.f, saturation};

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
    // const float ratio_c = (224 << (mode->pixel_depth - 8)) / (float)max_pixel_val;
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

#else

static const union csc_matrix_s32 g_csc_fixed_coefs_8bit_pix_8bit_precision[DRM_CSC_MODE_MAX] = {
    {298, 0, 0, 0, 298, 0, 0, 0, 298},             /*DRM_RGBL_TO_RGBF*/
    {77, 150, 29, -44, -87, 131, 131, -110, -21},  /*DRM_RGBL_TO_BT601L*/
    {89, 175, 34, -50, -99, 149, 149, -125, -24},  /*DRM_RGBL_TO_BT601F*/
    {54, 183, 19, -30, -101, 131, 131, -119, -12}, /*DRM_RGBL_TO_BT709L*/
    {63, 213, 22, -34, -115, 149, 149, -135, -14}, /*DRM_RGBL_TO_BT709F*/
    {67, 174, 15, -37, -94, 131, 131, -120, -11},  /*DRM_RGBL_TO_BT2020L*/
    {78, 202, 18, -42, -107, 149, 149, -137, -12}, /*DRM_RGBL_TO_BT2020F*/
    {220, 0, 0, 0, 220, 0, 0, 0, 220},             /*DRM_RGBF_TO_RGBL*/
    {66, 129, 25, -38, -74, 112, 112, -94, -18},   /*DRM_RGBF_TO_BT601L*/
    {77, 150, 29, -43, -85, 128, 128, -107, -21},  /*DRM_RGBF_TO_BT601F*/
    {47, 157, 16, -26, -87, 113, 112, -102, -10},  /*DRM_RGBF_TO_BT709L*/
    {54, 183, 19, -29, -99, 128, 128, -116, -12},  /*DRM_RGBF_TO_BT709F*/
    {58, 149, 13, -31, -81, 112, 112, -103, -9},   /*DRM_RGBF_TO_BT2020L*/
    {67, 174, 15, -36, -92, 128, 128, -118, -10},  /*DRM_RGBF_TO_BT2020F*/
    {256, 0, 351, 256, -86, -179, 256, 444, 0},    /*DRM_BT601L_TO_RGBL*/
    {298, 0, 409, 298, -100, -208, 298, 516, 0},   /*DRM_BT601L_TO_RGBF*/
    {298, 0, 0, 0, 291, 0, 0, 0, 291},             /*DRM_BT601L_TO_BT601F*/
    {256, -30, -53, 0, 261, 29, 0, 19, 262},       /*DRM_BT601L_TO_BT709L*/
    {298, -34, -62, 0, 297, 33, 0, 22, 299},       /*DRM_BT601L_TO_BT709F*/
    {220, 0, 308, 220, -76, -157, 220, 390, 0},    /*DRM_BT601F_TO_RGBL*/
    {256, 0, 359, 256, -88, -183, 256, 454, 0},    /*DRM_BT601F_TO_RGBF*/
    {220, 0, 0, 0, 225, 0, 0, 0, 225},             /*DRM_BT601F_TO_BT601L*/
    {220, -26, -47, 0, 229, 26, 0, 17, 231},       /*DRM_BT601F_TO_BT709L*/
    {256, -30, -54, 0, 261, 29, 0, 19, 262},       /*DRM_BT601F_TO_BT709F*/
    {256, 0, 394, 256, -47, -117, 256, 464, 0},    /*DRM_BT709L_TO_RGBL*/
    {298, 0, 459, 298, -55, -136, 298, 541, 0},    /*DRM_BT709L_TO_RGBF*/
    {256, 25, 49, 0, 253, -28, 0, -19, 252},       /*DRM_BT709L_TO_BT601L*/
    {298, 30, 57, 0, 288, -32, 0, -21, 287},       /*DRM_BT709L_TO_BT601F*/
    {298, 0, 0, 0, 291, 0, 0, 0, 291},             /*DRM_BT709L_TO_BT709F*/
    {220, 0, 346, 220, -41, -103, 220, 408, 0},    /*DRM_BT709F_TO_RGBL*/
    {256, 0, 403, 256, -48, -120, 256, 475, 0},    /*DRM_BT709F_TO_RGBF*/
    {220, 22, 43, 0, 223, -25, 0, -16, 221},       /*DRM_BT709F_TO_BT601L*/
    {256, 26, 50, 0, 253, -28, 0, -19, 252},       /*DRM_BT709F_TO_BT601F*/
    {220, 0, 0, 0, 225, 0, 0, 0, 225},             /*DRM_BT709F_TO_BT709L*/
    {256, 0, 369, 256, -41, -143, 256, 471, 0},    /*DRM_BT2020L_TO_RGBL*/
    {298, 0, 430, 298, -48, -167, 298, 548, 0},    /*DRM_BT2020L_TO_RGBF*/
    {298, 0, 0, 0, 291, 0, 0, 0, 291},             /*DRM_BT2020L_TO_BT2020F*/
    {220, 0, 324, 220, -36, -126, 220, 414, 0},    /*DRM_BT2020F_TO_RGBL*/
    {256, 0, 377, 256, -42, -146, 256, 482, 0},    /*DRM_BT2020F_TO_RGBF*/
    {220, 0, 0, 0, 225, 0, 0, 0, 225},             /*DRM_BT2020F_TO_BT2020L*/
};

static const union csc_matrix_s32 g_csc_fixed_coefs_10bit_pix_10bit_precision[DRM_CSC_MODE_MAX] = {
    {1196, 0, 0, 0, 1196, 0, 0, 0, 1196},             /*DRM_RGBL_TO_RGBF*/
    {306, 601, 117, -177, -347, 524, 524, -439, -85}, /*DRM_RGBL_TO_BT601L*/
    {358, 702, 136, -202, -396, 598, 598, -501, -97}, /*DRM_RGBL_TO_BT601F*/
    {218, 732, 74, -120, -404, 524, 524, -476, -48},  /*DRM_RGBL_TO_BT709L*/
    {254, 855, 87, -137, -461, 598, 598, -543, -55},  /*DRM_RGBL_TO_BT709F*/
    {269, 694, 61, -146, -378, 524, 524, -482, -42},  /*DRM_RGBL_TO_BT2020L*/
    {314, 811, 71, -167, -431, 598, 598, -550, -48},  /*DRM_RGBL_TO_BT2020F*/
    {877, 0, 0, 0, 877, 0, 0, 0, 877},                /*DRM_RGBF_TO_RGBL*/
    {262, 515, 100, -151, -297, 448, 448, -375, -73}, /*DRM_RGBF_TO_BT601L*/
    {306, 601, 117, -173, -339, 512, 512, -429, -83}, /*DRM_RGBF_TO_BT601F*/
    {187, 627, 63, -103, -346, 449, 448, -407, -41},  /*DRM_RGBF_TO_BT709L*/
    {218, 732, 74, -117, -395, 512, 512, -465, -47},  /*DRM_RGBF_TO_BT709F*/
    {230, 595, 52, -125, -323, 448, 448, -412, -36},  /*DRM_RGBF_TO_BT2020L*/
    {269, 694, 61, -143, -369, 512, 512, -471, -41},  /*DRM_RGBF_TO_BT2020F*/
    {1024, 0, 1404, 1024, -345, -715, 1024, 1774, 0}, /*DRM_BT601L_TO_RGBL*/
    {1196, 0, 1639, 1196, -402, -835, 1196, 2072, 0}, /*DRM_BT601L_TO_RGBF*/
    {1196, 0, 0, 0, 1169, 0, 0, 0, 1169},             /*DRM_BT601L_TO_BT601F*/
    {1024, -118, -213, 0, 1043, 117, 0, 77, 1050},    /*DRM_BT601L_TO_BT709L*/
    {1196, -138, -249, 0, 1191, 134, 0, 88, 1199},    /*DRM_BT601L_TO_BT709F*/
    {877, 0, 1229, 877, -302, -626, 877, 1554, 0},    /*DRM_BT601F_TO_RGBL*/
    {1024, 0, 1436, 1024, -352, -731, 1024, 1815, 0}, /*DRM_BT601F_TO_RGBF*/
    {877, 0, 0, 0, 897, 0, 0, 0, 897},                /*DRM_BT601F_TO_BT601L*/
    {877, -104, -186, 0, 914, 103, 0, 67, 920},       /*DRM_BT601F_TO_BT709L*/
    {1024, -121, -218, 0, 1043, 117, 0, 77, 1050},    /*DRM_BT601F_TO_BT709F*/
    {1024, 0, 1577, 1024, -188, -469, 1024, 1858, 0}, /*DRM_BT709L_TO_RGBL*/
    {1196, 0, 1841, 1196, -219, -547, 1196, 2169, 0}, /*DRM_BT709L_TO_RGBF*/
    {1024, 102, 196, 0, 1014, -113, 0, -74, 1007},    /*DRM_BT709L_TO_BT601L*/
    {1196, 119, 229, 0, 1157, -129, 0, -85, 1150},    /*DRM_BT709L_TO_BT601F*/
    {1196, 0, 0, 0, 1169, 0, 0, 0, 1169},             /*DRM_BT709L_TO_BT709F*/
    {877, 0, 1381, 877, -164, -410, 877, 1627, 0},    /*DRM_BT709F_TO_RGBL*/
    {1024, 0, 1613, 1024, -192, -479, 1024, 1900, 0}, /*DRM_BT709F_TO_RGBF*/
    {877, 89, 172, 0, 888, -99, 0, -65, 882},         /*DRM_BT709F_TO_BT601L*/
    {1024, 104, 201, 0, 1014, -113, 0, -74, 1007},    /*DRM_BT709F_TO_BT601F*/
    {877, 0, 0, 0, 897, 0, 0, 0, 897},                /*DRM_BT709F_TO_BT709L*/
    {1024, 0, 1476, 1024, -165, -572, 1024, 1884, 0}, /*DRM_BT2020L_TO_RGBL*/
    {1196, 0, 1724, 1196, -192, -668, 1196, 2200, 0}, /*DRM_BT2020L_TO_RGBF*/
    {1196, 0, 0, 0, 1169, 0, 0, 0, 1169},             /*DRM_BT2020L_TO_BT2020F*/
    {877, 0, 1293, 877, -144, -501, 877, 1650, 0},    /*DRM_BT2020F_TO_RGBL*/
    {1024, 0, 1510, 1024, -169, -585, 1024, 1927, 0}, /*DRM_BT2020F_TO_RGBF*/
    {877, 0, 0, 0, 897, 0, 0, 0, 897},                /*DRM_BT2020F_TO_BT2020L*/
};

static const union csc_matrix_s32 g_csc_fixed_coefs_10bit_pix_13bit_precision[DRM_CSC_MODE_MAX] = {
    {9567, 0, 0, 0, 9567, 0, 0, 0, 9567},                      /*DRM_RGBL_TO_RGBF*/
    {2449, 4809, 934, -1414, -2776, 4190, 4189, -3508, -681},  /*DRM_RGBL_TO_BT601L*/
    {2860, 5616, 1091, -1614, -3169, 4783, 4783, -4005, -778}, /*DRM_RGBL_TO_BT601F*/
    {1742, 5859, 591, -960, -3230, 4190, 4189, -3805, -384},   /*DRM_RGBL_TO_BT709L*/
    {2034, 6842, 691, -1096, -3687, 4783, 4783, -4345, -438},  /*DRM_RGBL_TO_BT709F*/
    {2152, 5554, 486, -1170, -3020, 4190, 4190, -3853, -337},  /*DRM_RGBL_TO_BT2020L*/
    {2513, 6486, 568, -1336, -3447, 4783, 4783, -4398, -385},  /*DRM_RGBL_TO_BT2020F*/
    {7015, 0, 0, 0, 7015, 0, 0, 0, 7015},                      /*DRM_RGBF_TO_RGBL*/
    {2097, 4118, 800, -1211, -2377, 3588, 3587, -3004, -583},  /*DRM_RGBF_TO_BT601L*/
    {2449, 4809, 934, -1382, -2714, 4096, 4096, -3430, -666},  /*DRM_RGBF_TO_BT601F*/
    {1491, 5017, 507, -822, -2765, 3587, 3588, -3259, -329},   /*DRM_RGBF_TO_BT709L*/
    {1742, 5859, 591, -939, -3157, 4096, 4096, -3720, -376},   /*DRM_RGBF_TO_BT709F*/
    {1843, 4756, 416, -1002, -2586, 3588, 3588, -3299, -289},  /*DRM_RGBF_TO_BT2020L*/
    {2152, 5554, 486, -1144, -2952, 4096, 4096, -3767, -329},  /*DRM_RGBF_TO_BT2020F*/
    {8192, 0, 11229, 8192, -2756, -5720, 8192, 14192, 0},      /*DRM_BT601L_TO_RGBL*/
    {9567, 0, 13113, 9567, -3219, -6679, 9567, 16574, 0},      /*DRM_BT601L_TO_RGBF*/
    {9567, 0, 0, 0, 9353, 0, 0, 0, 9353},                      /*DRM_BT601L_TO_BT601F*/
    {8192, -947, -1703, 0, 8345, 939, 0, 615, 8399},           /*DRM_BT601L_TO_BT709L*/
    {9567, -1105, -1989, 0, 9527, 1072, 0, 702, 9590},         /*DRM_BT601L_TO_BT709F*/
    {7015, 0, 9835, 7015, -2414, -5010, 7015, 12430, 0},       /*DRM_BT601F_TO_RGBL*/
    {8192, 0, 11485, 8192, -2819, -5850, 8192, 14516, 0},      /*DRM_BT601F_TO_RGBF*/
    {7015, 0, 0, 0, 7175, 0, 0, 0, 7175},                      /*DRM_BT601F_TO_BT601L*/
    {7015, -829, -1492, 0, 7309, 822, 0, 538, 7357},           /*DRM_BT601F_TO_BT709L*/
    {8192, -968, -1742, 0, 8345, 939, 0, 615, 8399},           /*DRM_BT601F_TO_BT709F*/
    {8192, 0, 12613, 8192, -1500, -3749, 8192, 14862, 0},      /*DRM_BT709L_TO_RGBL*/
    {9567, 0, 14729, 9567, -1752, -4378, 9567, 17356, 0},      /*DRM_BT709L_TO_RGBF*/
    {8192, 814, 1570, 0, 8109, -906, 0, -594, 8056},           /*DRM_BT709L_TO_BT601L*/
    {9567, 950, 1834, 0, 9258, -1035, 0, -678, 9198},          /*DRM_BT709L_TO_BT601F*/
    {9567, 0, 0, 0, 9353, 0, 0, 0, 9353},                      /*DRM_BT709L_TO_BT709F*/
    {7015, 0, 11047, 7015, -1314, -3284, 7015, 13017, 0},      /*DRM_BT709F_TO_RGBL*/
    {8192, 0, 12901, 8192, -1535, -3835, 8192, 15201, 0},      /*DRM_BT709F_TO_RGBF*/
    {7015, 713, 1375, 0, 7102, -794, 0, -520, 7056},           /*DRM_BT709F_TO_BT601L*/
    {8192, 832, 1606, 0, 8109, -906, 0, -594, 8056},           /*DRM_BT709F_TO_BT601F*/
    {7015, 0, 0, 0, 7175, 0, 0, 0, 7175},                      /*DRM_BT709F_TO_BT709L*/
    {8192, 0, 11810, 8192, -1318, -4576, 8192, 15068, 0},      /*DRM_BT2020L_TO_RGBL*/
    {9567, 0, 13792, 9567, -1539, -5344, 9567, 17597, 0},      /*DRM_BT2020L_TO_RGBF*/
    {9567, 0, 0, 0, 9353, 0, 0, 0, 9353},                      /*DRM_BT2020L_TO_BT2020F*/
    {7015, 0, 10344, 7015, -1154, -4008, 7015, 13198, 0},      /*DRM_BT2020F_TO_RGBL*/
    {8192, 0, 12080, 8192, -1348, -4681, 8192, 15412, 0},      /*DRM_BT2020F_TO_RGBF*/
    {7015, 0, 0, 0, 7175, 0, 0, 0, 7175},                      /*DRM_BT2020F_TO_BT2020L*/
};

#endif // ENABLE_POST_CSC_FLOATING_POINT

static void csc_get_range_offset(const struct post_csc_convert_mode *mode,
    union csc_vector_s32 *offset_i, union csc_vector_s32 *offset_o)
{
    const int ratio_gain = 1 << (mode->pixel_depth - 8);

    int offset_y = mode->is_input_full_range ? 0 : 16;
    int offset_c = mode->is_input_yuv ? 128 : offset_y;
    offset_i->val[0] = -offset_y * ratio_gain;
    offset_i->val[1] = -offset_c * ratio_gain;
    offset_i->val[2] = -offset_c * ratio_gain;

    offset_y = mode->is_output_full_range ? 0 : 16;
    offset_c = mode->is_output_yuv ? 128 : offset_y;
    offset_o->val[0] = offset_y * ratio_gain;
    offset_o->val[1] = offset_c * ratio_gain;
    offset_o->val[2] = offset_c * ratio_gain;
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

static int csc_get_drm_csc_mode_enum(const struct post_csc_convert_mode *mode)
{
    for (int i = 0; i < DRM_CSC_MODE_MAX; ++i)
    {
        const struct post_csc_convert_mode *mode_i = &g_supported_standard_convert_mode[i];
        if (mode_i->input_color_encoding == mode->input_color_encoding &&
            mode_i->output_color_encoding == mode->output_color_encoding &&
            mode_i->is_input_yuv == mode->is_input_yuv &&
            mode_i->is_output_yuv == mode->is_output_yuv &&
            mode_i->is_input_full_range == mode->is_input_full_range &&
            mode_i->is_output_full_range == mode->is_output_full_range)
        {
            return i;
        }
    }
    return -1;
}

int rockchip_calc_post_csc_coefs(const struct post_csc *bcsh_cfg, // [I] CSC config
    const struct post_csc_convert_mode *convert_mode,             // [I] CSC convert mode
    struct post_csc_coef *csc_simple_coef                         // [O] return CSC coefs
)
{
    int ret = 0;
    union csc_matrix_s32 final_mat_fix = {0};
    union csc_vector_s32 range_ofs_i = {0}, range_ofs_o = {0}, final_vec = {0};

#if ENABLE_POST_CSC_FLOATING_POINT
    assert(convert_mode->pixel_depth >= 8 && convert_mode->pixel_depth <= 16);
    assert(convert_mode->coef_precision >= 8 && convert_mode->coef_precision <= 16);
    // assert(convert_mode->coef_precision >= convert_mode->pixel_depth);

    union csc_matrix_f32 range_mat_i = {0}, range_mat_o = {0};
    union csc_matrix_f32 color_convert_mat = {0}, tmp_mat = {0}, final_mat = {0};

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
#else // ENABLE_POST_CSC_FLOATING_POINT
    int mode_idx = csc_get_drm_csc_mode_enum(convert_mode);
    if (mode_idx < 0 || mode_idx >= DRM_CSC_MODE_MAX) {
        printf("ERROR: unsupported CSC convert mode!\n");
        return -1;
    }

    /* 8bit pixel depth + 8bit coef precision */
    if (convert_mode->pixel_depth == 8)
    {
        if (convert_mode->coef_precision == 8) {
            memcpy(&final_mat_fix, &g_csc_fixed_coefs_8bit_pix_8bit_precision[mode_idx], sizeof(union csc_matrix_s32));
        } else {
            printf("Invalid coef precision %d, only 8 supported for 8bit pixel depth!\n", convert_mode->coef_precision);
            return -1;
        }
    }
    /* 10bit pixel depth + 10/13bit coef precision */
    else if (convert_mode->pixel_depth == 10)
    {
        if (convert_mode->coef_precision == 10) {
            memcpy(&final_mat_fix, &g_csc_fixed_coefs_10bit_pix_10bit_precision[mode_idx], sizeof(union csc_matrix_s32));
        } else if (convert_mode->coef_precision == 13) {
            memcpy(&final_mat_fix, &g_csc_fixed_coefs_10bit_pix_13bit_precision[mode_idx], sizeof(union csc_matrix_s32));
        } else {
            printf("Invalid coef precision %d, only 10/13 supported for 8bit pixel depth!\n", convert_mode->coef_precision);
            return -1;
        }
    }
    else
    {
        printf("Invalid pixel depth %d, only 8/10 supported!\n", convert_mode->pixel_depth);
        return -1;
    }

    csc_get_range_offset(convert_mode, &range_ofs_i, &range_ofs_o);
#endif // ENABLE_POST_CSC_FLOATING_POINT

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