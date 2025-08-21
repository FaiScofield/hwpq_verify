// SPDX-License-Identifier: (GPL-2.0+ OR MIT)
/*
 * Copyright (c) 2022 Rockchip Electronics Co., Ltd.
 * Author: Zhang yubing <yubing.zhang@rock-chips.com>
 */

#include "rockchip_post_csc.h"

#define PQ_CSC_HUE_TABLE_NUM                  256
#define PQ_CSC_MODE_COEF_COMMENT_LEN          32
#define PQ_CSC_SIMPLE_MAT_PARAM_FIX_BIT_WIDTH 10
#define PQ_CSC_SIMPLE_MAT_PARAM_FIX_NUM       (1 << PQ_CSC_SIMPLE_MAT_PARAM_FIX_BIT_WIDTH)

#define PQ_CALC_ENHANCE_BIT                   6
/* csc convert coef fixed-point num bit width */
#define PQ_CSC_PARAM_FIX_BIT_WIDTH            10
/* csc convert coef half fixed-point num bit width */
#define PQ_CSC_PARAM_HALF_FIX_BIT_WIDTH       (PQ_CSC_PARAM_FIX_BIT_WIDTH - 1)
/* csc convert coef fixed-point num */
#define PQ_CSC_PARAM_FIX_NUM                  (1 << PQ_CSC_PARAM_FIX_BIT_WIDTH)
#define PQ_CSC_PARAM_HALF_FIX_NUM             (1 << PQ_CSC_PARAM_HALF_FIX_BIT_WIDTH)
/* csc input param bit width */
#define PQ_CSC_IN_PARAM_NORM_BIT_WIDTH        9
/* csc input param normalization coef */
#define PQ_CSC_IN_PARAM_NORM_COEF             (1 << PQ_CSC_IN_PARAM_NORM_BIT_WIDTH)

/* csc hue table range [0,255] */
#define PQ_CSC_HUE_TABLE_DIV_COEF             2
/* csc brightness offset */
#define PQ_CSC_BRIGHTNESS_OFFSET              256

/* dc coef base bit width */
#define PQ_CSC_DC_COEF_BASE_BIT_WIDTH         10
/* input dc coef offset for 10bit data */
#define PQ_CSC_DC_IN_OFFSET                   64
/* input and output dc coef offset for 10bit data u,v */
#define PQ_CSC_DC_IN_OUT_DEFAULT              512
/* r,g,b color temp div coef, range [-128,128] for 10bit data */
#define PQ_CSC_TEMP_OFFSET_DIV_COEF           2

#ifndef MAX
#define MAX(a, b)             ((a) > (b) ? (a) : (b))
#define MIN(a, b)             ((a) < (b) ? (a) : (b))
#define CLIP(x, min_v, max_v) MIN(MAX(x, min_v), max_v)
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

// union csc_vector_f32
// {
//     struct
//     {
//         float csc_offset0;
//         float csc_offset1;
//         float csc_offset2;
//     };
//     float val[3];
// };

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


#if 0

/* 10bit Hue Sin Look Up Table -> range[-30, 30] */
static const s32 g_hue_sin_table[PQ_CSC_HUE_TABLE_NUM] = {512, 508, 505, 501, 497, 494, 490, 486, 483, 479, 475, 472,
    468, 464, 460, 457, 453, 449, 445, 442, 438, 434, 430, 426, 423, 419, 415, 411, 407, 403, 400, 396, 392, 388, 384,
    380, 376, 372, 369, 365, 361, 357, 353, 349, 345, 341, 337, 333, 329, 325, 321, 317, 313, 309, 305, 301, 297, 293,
    289, 285, 281, 277, 273, 269, 265, 261, 257, 253, 249, 245, 241, 237, 233, 228, 224, 220, 216, 212, 208, 204, 200,
    196, 192, 187, 183, 179, 175, 171, 167, 163, 159, 154, 150, 146, 142, 138, 134, 130, 125, 121, 117, 113, 109, 105,
    100, 96, 92, 88, 84, 80, 75, 71, 67, 63, 59, 54, 50, 46, 42, 38, 34, 29, 25, 21, 17, 13, 8, 4, 0, -4, -8, -13, -17,
    -21, -25, -29, -34, -38, -42, -46, -50, -54, -59, -63, -67, -71, -75, -80, -84, -88, -92, -96, -100, -105, -109,
    -113, -117, -121, -125, -130, -134, -138, -142, -146, -150, -154, -159, -163, -167, -171, -175, -179, -183, -187,
    -192, -196, -200, -204, -208, -212, -216, -220, -224, -228, -233, -237, -241, -245, -249, -253, -257, -261, -265,
    -269, -273, -277, -281, -285, -289, -293, -297, -301, -305, -309, -313, -317, -321, -325, -329, -333, -337, -341,
    -345, -349, -353, -357, -361, -365, -369, -372, -376, -380, -384, -388, -392, -396, -400, -403, -407, -411, -415,
    -419, -423, -426, -430, -434, -438, -442, -445, -449, -453, -457, -460, -464, -468, -472, -475, -479, -483, -486,
    -490, -494, -497, -501, -505, -508};

/* 10bit Hue Cos Look Up Table  -> range[-30, 30] */
static const s32 g_hue_cos_table[PQ_CSC_HUE_TABLE_NUM] = {887, 889, 891, 893, 895, 897, 899, 901, 903, 905, 907, 909,
    911, 913, 915, 917, 919, 920, 922, 924, 926, 928, 929, 931, 933, 935, 936, 938, 940, 941, 943, 945, 946, 948, 949,
    951, 953, 954, 956, 957, 959, 960, 962, 963, 964, 966, 967, 969, 970, 971, 973, 974, 975, 976, 978, 979, 980, 981,
    983, 984, 985, 986, 987, 988, 989, 990, 992, 993, 994, 995, 996, 997, 998, 998, 999, 1000, 1001, 1002, 1003, 1004,
    1005, 1005, 1006, 1007, 1008, 1008, 1009, 1010, 1011, 1011, 1012, 1013, 1013, 1014, 1014, 1015, 1015, 1016, 1016,
    1017, 1017, 1018, 1018, 1019, 1019, 1020, 1020, 1020, 1021, 1021, 1021, 1022, 1022, 1022, 1022, 1023, 1023, 1023,
    1023, 1023, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1023,
    1023, 1023, 1023, 1023, 1022, 1022, 1022, 1022, 1021, 1021, 1021, 1020, 1020, 1020, 1019, 1019, 1018, 1018, 1017,
    1017, 1016, 1016, 1015, 1015, 1014, 1014, 1013, 1013, 1012, 1011, 1011, 1010, 1009, 1008, 1008, 1007, 1006, 1005,
    1005, 1004, 1003, 1002, 1001, 1000, 999, 998, 998, 997, 996, 995, 994, 993, 992, 990, 989, 988, 987, 986, 985, 984,
    983, 981, 980, 979, 978, 976, 975, 974, 973, 971, 970, 969, 967, 966, 964, 963, 962, 960, 959, 957, 956, 954, 953,
    951, 949, 948, 946, 945, 943, 941, 940, 938, 936, 935, 933, 931, 929, 928, 926, 924, 922, 920, 919, 917, 915, 913,
    911, 909, 907, 905, 903, 901, 899, 897, 895, 893, 891, 889, 887};

static void csc_matrix_right_shift(struct rk_pq_csc_coef *m, int n)
{
    m->csc_coef00 = m->csc_coef00 >> n;
    m->csc_coef01 = m->csc_coef01 >> n;
    m->csc_coef02 = m->csc_coef02 >> n;
    m->csc_coef10 = m->csc_coef10 >> n;
    m->csc_coef11 = m->csc_coef11 >> n;
    m->csc_coef12 = m->csc_coef12 >> n;
    m->csc_coef20 = m->csc_coef20 >> n;
    m->csc_coef21 = m->csc_coef21 >> n;
    m->csc_coef22 = m->csc_coef22 >> n;
}

static inline s32 csc_simple_round(s32 x, s32 n) { return (x + (1 << (n - 1)) + (x >> 31)) >> n; }

static void csc_matrix_element_right_shift_with_simple_round(struct rk_pq_csc_coef *m, int n)
{
    m->csc_coef00 = csc_simple_round(m->csc_coef00, n);
    m->csc_coef01 = csc_simple_round(m->csc_coef01, n);
    m->csc_coef02 = csc_simple_round(m->csc_coef02, n);
    m->csc_coef10 = csc_simple_round(m->csc_coef10, n);
    m->csc_coef11 = csc_simple_round(m->csc_coef11, n);
    m->csc_coef12 = csc_simple_round(m->csc_coef12, n);
    m->csc_coef20 = csc_simple_round(m->csc_coef20, n);
    m->csc_coef21 = csc_simple_round(m->csc_coef21, n);
    m->csc_coef22 = csc_simple_round(m->csc_coef22, n);
}

static struct rk_pq_csc_coef create_rgb_gain_matrix(s32 r_gain, s32 g_gain, s32 b_gain)
{
    struct rk_pq_csc_coef m;

    m.csc_coef00 = r_gain;
    m.csc_coef01 = 0;
    m.csc_coef02 = 0;

    m.csc_coef10 = 0;
    m.csc_coef11 = g_gain;
    m.csc_coef12 = 0;

    m.csc_coef20 = 0;
    m.csc_coef21 = 0;
    m.csc_coef22 = b_gain;

    return m;
}

static struct rk_pq_csc_coef create_contrast_matrix(s32 contrast)
{
    struct rk_pq_csc_coef m;

    m.csc_coef00 = contrast;
    m.csc_coef01 = 0;
    m.csc_coef02 = 0;

    m.csc_coef10 = 0;
    m.csc_coef11 = contrast;
    m.csc_coef12 = 0;

    m.csc_coef20 = 0;
    m.csc_coef21 = 0;
    m.csc_coef22 = contrast;

    return m;
}

static struct rk_pq_csc_coef create_hue_matrix(s32 hue)
{
    struct rk_pq_csc_coef m;
    s32 hue_idx;
    s32 sin_hue;
    s32 cos_hue;

    hue_idx = CLIP(hue / PQ_CSC_HUE_TABLE_DIV_COEF, 0, PQ_CSC_HUE_TABLE_NUM - 1);
    sin_hue = g_hue_sin_table[hue_idx];
    cos_hue = g_hue_cos_table[hue_idx];

    m.csc_coef00 = 1024;
    m.csc_coef01 = 0;
    m.csc_coef02 = 0;

    m.csc_coef10 = 0;
    m.csc_coef11 = cos_hue;
    m.csc_coef12 = sin_hue;

    m.csc_coef20 = 0;
    m.csc_coef21 = -sin_hue;
    m.csc_coef22 = cos_hue;

    return m;
}

static struct rk_pq_csc_coef create_saturation_matrix(s32 saturation)
{
    struct rk_pq_csc_coef m;

    m.csc_coef00 = 512;
    m.csc_coef01 = 0;
    m.csc_coef02 = 0;

    m.csc_coef10 = 0;
    m.csc_coef11 = saturation;
    m.csc_coef12 = 0;

    m.csc_coef20 = 0;
    m.csc_coef21 = 0;
    m.csc_coef22 = saturation;

    return m;
}
#endif

/////////////////////////////////////// new method below /////////////////////////////////////
static inline void csc_matrix_mul_f32(union csc_matrix_f32 *dst, const union csc_matrix_f32 *m0, const union csc_matrix_f32 *m1)
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

#if 0
static void csc_adjust_convert_matrix(const struct post_csc_convert_mode *convert_mode,
    const struct post_csc *bcsh_cfg, union csc_matrix_f32 *out_matrix)
{
    struct rk_pq_csc_coef gain_matrix;
    struct rk_pq_csc_coef contrast_matrix;
    struct rk_pq_csc_coef hue_matrix;
    struct rk_pq_csc_coef saturation_matrix;
    struct rk_pq_csc_coef temp0, temp1;
    const struct rk_pq_csc_coef *r2y_matrix;
    const struct rk_pq_csc_coef *y2r_matrix;
    struct rk_pq_csc_vector dc_in_ventor;
    struct rk_pq_csc_vector dc_out_ventor;
    struct rk_pq_csc_vector v;
    const struct rk_csc_colorspace_info *color_info;
    s32 contrast, saturation, brightness;
    s32 r_gain, g_gain, b_gain;
    s32 r_offset, g_offset, b_offset;
    s32 dc_in_offset, dc_out_offset;

    contrast = csc_input_cfg->contrast * PQ_CSC_PARAM_FIX_NUM / PQ_CSC_IN_PARAM_NORM_COEF;
    saturation = csc_input_cfg->saturation * PQ_CSC_PARAM_FIX_NUM / PQ_CSC_IN_PARAM_NORM_COEF;
    r_gain = csc_input_cfg->r_gain * PQ_CSC_PARAM_FIX_NUM / PQ_CSC_IN_PARAM_NORM_COEF;
    g_gain = csc_input_cfg->g_gain * PQ_CSC_PARAM_FIX_NUM / PQ_CSC_IN_PARAM_NORM_COEF;
    b_gain = csc_input_cfg->b_gain * PQ_CSC_PARAM_FIX_NUM / PQ_CSC_IN_PARAM_NORM_COEF;
    r_offset = ((s32)csc_input_cfg->r_offset - PQ_CSC_BRIGHTNESS_OFFSET) / PQ_CSC_TEMP_OFFSET_DIV_COEF;
    g_offset = ((s32)csc_input_cfg->g_offset - PQ_CSC_BRIGHTNESS_OFFSET) / PQ_CSC_TEMP_OFFSET_DIV_COEF;
    b_offset = ((s32)csc_input_cfg->b_offset - PQ_CSC_BRIGHTNESS_OFFSET) / PQ_CSC_TEMP_OFFSET_DIV_COEF;

    gain_matrix = create_rgb_gain_matrix(r_gain, g_gain, b_gain);
    contrast_matrix = create_contrast_matrix(contrast);
    hue_matrix = create_hue_matrix(csc_input_cfg->hue);
    saturation_matrix = create_saturation_matrix(saturation);

    color_info = &csc_mode_cfg->st_csc_color_info;
    brightness = (s32)csc_input_cfg->brightness - PQ_CSC_BRIGHTNESS_OFFSET;
    dc_in_offset = color_info->in_full_range ? 0 : -PQ_CSC_DC_IN_OFFSET;
    dc_out_offset = color_info->out_full_range ? 0 : PQ_CSC_DC_IN_OFFSET;

    /*
     * M0 = hue_matrix * saturation_matrix,
     * M1 = gain_matrix * contrast_matrix,
     */
    /*
     * The value bits width is 32 bit, so every time 2 matirx multiplied,
     * right shift is necessary to avoid overflow. For enhancing the
     * calculator precision, PQ_CALC_ENHANCE_BIT bits is reserved and
     * right shift before get the final result.
     */
    if (is_input_yuv && is_output_yuv)
    {
        /*
         * yuv2yuv: output = T * M0 * N_r2y * M1 * N_y2r,
         * so output = T * hue_matrix * saturation_matrix *
         * N_r2y * gain_matrix * contrast_matrix * N_y2r
         */
        r2y_matrix = &r2y_for_y2y;
        y2r_matrix = &y2r_for_y2y;
        csc_matrix_multiply(&temp0, csc_mode_cfg->pst_csc_coef, &hue_matrix);
        csc_matrix_element_right_shift(&temp0, PQ_CSC_PARAM_FIX_BIT_WIDTH - PQ_CALC_ENHANCE_BIT);
        csc_matrix_multiply(&temp1, &temp0, &saturation_matrix);
        csc_matrix_element_right_shift(&temp1, PQ_CSC_PARAM_HALF_FIX_BIT_WIDTH);
        csc_matrix_multiply(&temp0, &temp1, r2y_matrix);
        csc_matrix_element_right_shift(&temp0, PQ_CSC_PARAM_FIX_BIT_WIDTH);
        csc_matrix_multiply(&temp1, &temp0, &gain_matrix);
        csc_matrix_element_right_shift(&temp1, PQ_CSC_PARAM_HALF_FIX_BIT_WIDTH);
        csc_matrix_multiply(&temp0, &temp1, &contrast_matrix);
        csc_matrix_element_right_shift(&temp0, PQ_CSC_PARAM_HALF_FIX_BIT_WIDTH);
        csc_matrix_multiply(out_matrix, &temp0, y2r_matrix);
        csc_matrix_element_right_shift_with_simple_round(out_matrix, PQ_CSC_PARAM_FIX_BIT_WIDTH + PQ_CALC_ENHANCE_BIT);

        dc_in_ventor.csc_offset0 = dc_in_offset;
        dc_in_ventor.csc_offset1 = -PQ_CSC_DC_IN_OUT_DEFAULT;
        dc_in_ventor.csc_offset2 = -PQ_CSC_DC_IN_OUT_DEFAULT;
        dc_out_ventor.csc_offset0 = brightness + dc_out_offset;
        dc_out_ventor.csc_offset1 = PQ_CSC_DC_IN_OUT_DEFAULT;
        dc_out_ventor.csc_offset2 = PQ_CSC_DC_IN_OUT_DEFAULT;
    }
    else if (is_input_yuv && !is_output_yuv)
    {
        /*
         * yuv2rgb: output = M1 * T * M0,
         * so output = gain_matrix * contrast_matrix * T *
         * hue_matrix * saturation_matrix
         */
        csc_matrix_multiply(&temp0, csc_mode_cfg->pst_csc_coef, &hue_matrix);
        csc_matrix_element_right_shift(&temp0, PQ_CSC_PARAM_FIX_BIT_WIDTH - PQ_CALC_ENHANCE_BIT);
        csc_matrix_multiply(&temp1, &temp0, &saturation_matrix);
        csc_matrix_element_right_shift(&temp1, PQ_CSC_PARAM_HALF_FIX_BIT_WIDTH);
        csc_matrix_multiply(&temp0, &contrast_matrix, &temp1);
        csc_matrix_element_right_shift(&temp0, PQ_CSC_PARAM_HALF_FIX_BIT_WIDTH);
        csc_matrix_multiply(out_matrix, &gain_matrix, &temp0);
        csc_matrix_element_right_shift(out_matrix, PQ_CSC_PARAM_HALF_FIX_BIT_WIDTH + PQ_CALC_ENHANCE_BIT);

        dc_in_ventor.csc_offset0 = dc_in_offset;
        dc_in_ventor.csc_offset1 = -PQ_CSC_DC_IN_OUT_DEFAULT;
        dc_in_ventor.csc_offset2 = -PQ_CSC_DC_IN_OUT_DEFAULT;
        dc_out_ventor.csc_offset0 = brightness + dc_out_offset + r_offset;
        dc_out_ventor.csc_offset1 = brightness + dc_out_offset + g_offset;
        dc_out_ventor.csc_offset2 = brightness + dc_out_offset + b_offset;
    }
    else if (!is_input_yuv && is_output_yuv)
    {
        /*
         * rgb2yuv: output = M0 * T * M1,
         * so output = hue_matrix * saturation_matrix * T *
         * gain_matrix * contrast_matrix
         */
        csc_matrix_multiply(&temp0, csc_mode_cfg->pst_csc_coef, &gain_matrix);
        csc_matrix_element_right_shift(&temp0, PQ_CSC_PARAM_HALF_FIX_BIT_WIDTH - PQ_CALC_ENHANCE_BIT);
        csc_matrix_multiply(&temp1, &temp0, &contrast_matrix);
        csc_matrix_element_right_shift(&temp1, PQ_CSC_PARAM_HALF_FIX_BIT_WIDTH);
        csc_matrix_multiply(&temp0, &saturation_matrix, &temp1);
        csc_matrix_element_right_shift(&temp0, PQ_CSC_PARAM_HALF_FIX_BIT_WIDTH);
        csc_matrix_multiply(out_matrix, &hue_matrix, &temp0);
        csc_matrix_element_right_shift(out_matrix, PQ_CSC_PARAM_FIX_BIT_WIDTH + PQ_CALC_ENHANCE_BIT);

        dc_in_ventor.csc_offset0 = dc_in_offset;
        dc_in_ventor.csc_offset1 = dc_in_offset;
        dc_in_ventor.csc_offset2 = dc_in_offset;
        dc_out_ventor.csc_offset0 = brightness + dc_out_offset;
        dc_out_ventor.csc_offset1 = PQ_CSC_DC_IN_OUT_DEFAULT;
        dc_out_ventor.csc_offset2 = PQ_CSC_DC_IN_OUT_DEFAULT;
    }
    else
    {
        /*
         * rgb2rgb: output = T * M1 * N_y2r * M0 * N_r2y,
         * so output = T * gain_matrix * contrast_matrix *
         * N_y2r * hue_matrix * saturation_matrix * N_r2y
         */
        r2y_matrix = &r2y_for_r2r;
        y2r_matrix = &y2r_for_r2r;
        csc_matrix_multiply(&temp0, &contrast_matrix, y2r_matrix);
        csc_matrix_element_right_shift(&temp0, PQ_CSC_PARAM_HALF_FIX_BIT_WIDTH - PQ_CALC_ENHANCE_BIT);
        csc_matrix_multiply(&temp1, &gain_matrix, &temp0);
        csc_matrix_element_right_shift(&temp1, PQ_CSC_PARAM_HALF_FIX_BIT_WIDTH);
        csc_matrix_multiply(&temp0, &temp1, &hue_matrix);
        csc_matrix_element_right_shift(&temp0, PQ_CSC_PARAM_FIX_BIT_WIDTH);
        csc_matrix_multiply(&temp1, &temp0, &saturation_matrix);
        csc_matrix_element_right_shift(&temp1, PQ_CSC_PARAM_HALF_FIX_BIT_WIDTH);
        csc_matrix_multiply(&temp0, &temp1, r2y_matrix);
        csc_matrix_element_right_shift(&temp0, PQ_CSC_PARAM_FIX_BIT_WIDTH);
        csc_matrix_multiply(out_matrix, csc_mode_cfg->pst_csc_coef, &temp0);
        csc_matrix_element_right_shift_with_simple_round(out_matrix, PQ_CSC_PARAM_FIX_BIT_WIDTH + PQ_CALC_ENHANCE_BIT);

        dc_in_ventor.csc_offset0 = dc_in_offset;
        dc_in_ventor.csc_offset1 = dc_in_offset;
        dc_in_ventor.csc_offset2 = dc_in_offset;
        dc_out_ventor.csc_offset0 = brightness + dc_out_offset + r_offset;
        dc_out_ventor.csc_offset1 = brightness + dc_out_offset + g_offset;
        dc_out_ventor.csc_offset2 = brightness + dc_out_offset + b_offset;
    }
}

static void csc_swap_color_channel(const struct post_csc_convert_mode *convert_mode,
    union csc_matrix_f32 *out_matrix, union csc_vector_f32 *out_dc)
{
    struct rk_pq_csc_coef tmp_matrix;
    struct rk_pq_csc_vector tmp_v;

    if (!convert_mode->is_input_yuv)
    {
        memcpy(&tmp_matrix, out_matrix, sizeof(struct rk_pq_csc_coef));
        csc_matrix_multiply(out_matrix, &tmp_matrix, &rgb_input_swap_matrix);
    }
    if (convert_mode->is_output_yuv)
    {
        memcpy(&tmp_matrix, out_matrix, sizeof(struct rk_pq_csc_coef));
        memcpy(&tmp_v, out_dc, sizeof(struct rk_pq_csc_vector));
        csc_matrix_multiply(out_matrix, &yuv_output_swap_matrix, &tmp_matrix);
        csc_matrix_ventor_multiply(out_dc, &yuv_output_swap_matrix, &tmp_v);
    }
    printf("NOTE: CSC coefs & offset has been swapped!\n");
}

#endif

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

    // TODO: adjust final_mat with bsch configs
    if (bcsh_cfg) {
        // csc_adjust_convert_matrix(convert_mode, bcsh_cfg, &final_mat);
    }

    // get fixed mat
    csc_get_fixed_coefs_matrix(&final_mat, &final_mat_fix, convert_mode->coef_precision);

    // TODO: fine-tuning for fixed matrix (R2Y)
    if (!bcsh_cfg) {
        // csc_fine_tuning(&final_mat_fix, convert_mode->coef_precision);
    }

    // get fixed vec
    csc_get_fixed_coefs_offset(&final_mat_fix, &range_ofs_i, &range_ofs_o, &final_vec, convert_mode->coef_precision);

    // TODO: swap channles if necessary
    if (convert_mode->swap_channels == 1) {
        // csc_swap_color_channel(&convert_mode, &final_mat, &final_vec);
    }

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