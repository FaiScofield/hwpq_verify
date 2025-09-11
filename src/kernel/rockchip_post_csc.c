// SPDX-License-Identifier: (GPL-2.0+ OR MIT)
/*
 * Copyright (c) 2022 Rockchip Electronics Co., Ltd.
 * Author: Zhang yubing <yubing.zhang@rock-chips.com>
 */

#include "rockchip_post_csc.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

#define PQ_CSC_HUE_TABLE_NUM			256
#define PQ_CSC_MODE_COEF_COMMENT_LEN		32
#define PQ_CSC_SIMPLE_MAT_PARAM_FIX_BIT_WIDTH	10
#define PQ_CSC_SIMPLE_MAT_PARAM_FIX_NUM		(1 << PQ_CSC_SIMPLE_MAT_PARAM_FIX_BIT_WIDTH)

#define PQ_CALC_ENHANCE_BIT			6
/* csc convert coef fixed-point num bit width */
#define PQ_CSC_PARAM_FIX_BIT_WIDTH		10
/* csc convert coef half fixed-point num bit width */
#define PQ_CSC_PARAM_HALF_FIX_BIT_WIDTH		(PQ_CSC_PARAM_FIX_BIT_WIDTH - 1)
/* csc convert coef fixed-point num */
#define PQ_CSC_PARAM_FIX_NUM			(1 << PQ_CSC_PARAM_FIX_BIT_WIDTH)
#define PQ_CSC_PARAM_HALF_FIX_NUM		(1 << PQ_CSC_PARAM_HALF_FIX_BIT_WIDTH)
/* csc input param bit width */
#define PQ_CSC_IN_PARAM_NORM_BIT_WIDTH		9
/* csc input param normalization coef */
#define PQ_CSC_IN_PARAM_NORM_COEF		(1 << PQ_CSC_IN_PARAM_NORM_BIT_WIDTH)

/* csc hue table range [0,255] */
#define PQ_CSC_HUE_TABLE_DIV_COEF		2
/* csc brightness offset */
#define PQ_CSC_BRIGHTNESS_OFFSET		256

/* dc coef base bit width */
#define PQ_CSC_DC_COEF_BASE_BIT_WIDTH		10
/* input dc coef offset for 10bit data */
#define PQ_CSC_DC_IN_OFFSET			64
/* input and output dc coef offset for 10bit data u,v */
#define PQ_CSC_DC_IN_OUT_DEFAULT		512
/* r,g,b color temp div coef, range [-128,128] for 10bit data */
#define PQ_CSC_TEMP_OFFSET_DIV_COEF		2

#define	MAX(a, b)				((a) > (b) ? (a) : (b))
#define	MIN(a, b)				((a) < (b) ? (a) : (b))
#define	CLIP(x, min_v, max_v)			MIN(MAX(x, min_v), max_v)

enum rk_pq_csc_mode {
	/* new name & order after RK3572 */
	RGBL_TO_RGBF,
	RGBL_TO_YUV601L,
	RGBL_TO_YUV601F,
	RGBL_TO_YUV709L,
	RGBL_TO_YUV709F,
	RGBL_TO_YUV2020L,
	RGBL_TO_YUV2020F,
	RGBF_TO_RGBL,
	RGBF_TO_YUV601L,
	RGBF_TO_YUV601F,
	RGBF_TO_YUV709L,
	RGBF_TO_YUV709F,
	RGBF_TO_YUV2020L,
	RGBF_TO_YUV2020F,
	YUV601L_TO_RGBL,
	YUV601L_TO_RGBF,
	YUV601L_TO_YUV601F,
	YUV601L_TO_YUV709L,
	YUV601L_TO_YUV709F,
	YUV601F_TO_RGBL,
	YUV601F_TO_RGBF,
	YUV601F_TO_YUV601L,
	YUV601F_TO_YUV709L,
	YUV601F_TO_YUV709F,
	YUV709L_TO_RGBL,
	YUV709L_TO_RGBF,
	YUV709L_TO_YUV601L,
	YUV709L_TO_YUV601F,
	YUV709L_TO_YUV709F,
	YUV709F_TO_RGBL,
	YUV709F_TO_RGBF,
	YUV709F_TO_YUV601L,
	YUV709F_TO_YUV601F,
	YUV709F_TO_YUV709L,
	YUV2020L_TO_RGBL,
	YUV2020L_TO_RGBF,
	YUV2020L_TO_YUV2020F,
	YUV2020F_TO_RGBL,
	YUV2020F_TO_RGBF,
	YUV2020F_TO_YUV2020L,
	IDENTITY_MODE, /* A_to_A */

    /* DEPRECATED: assign to new order for RK3576 compatibility */
	RK_PQ_CSC_YUV2RGB_601 = YUV601L_TO_RGBF,                   /* YCbCr_601 LIMIT-> RGB FULL */
	RK_PQ_CSC_YUV2RGB_709 = YUV709L_TO_RGBF,                   /* YCbCr_709 LIMIT-> RGB FULL */
	RK_PQ_CSC_RGB2YUV_601 = RGBF_TO_YUV601L,                   /* RGB FULL->YCbCr_601 LIMIT */
	RK_PQ_CSC_RGB2YUV_709 = RGBF_TO_YUV709L,                   /* RGB FULL->YCbCr_709 LIMIT */
	RK_PQ_CSC_YUV2YUV_709_601 = YUV709L_TO_YUV601L,            /* YCbCr_709 LIMIT->YCbCr_601 LIMIT */
	RK_PQ_CSC_YUV2YUV_601_709 = YUV601L_TO_YUV709L,            /* YCbCr_601 LIMIT->YCbCr_709 LIMIT */
	RK_PQ_CSC_YUV2YUV = IDENTITY_MODE,                         /* YCbCr LIMIT->YCbCr LIMIT */
	RK_PQ_CSC_YUV2RGB_601_FULL = YUV601F_TO_RGBF,              /* YCbCr_601 FULL-> RGB FULL */
	RK_PQ_CSC_YUV2RGB_709_FULL = YUV709F_TO_RGBF,              /* YCbCr_709 FULL-> RGB FULL */
	RK_PQ_CSC_RGB2YUV_601_FULL = RGBF_TO_YUV601F,              /* RGB FULL->YCbCr_601 FULL */
	RK_PQ_CSC_RGB2YUV_709_FULL = RGBF_TO_YUV709F,              /* RGB FULL->YCbCr_709 FULL */
	RK_PQ_CSC_YUV2YUV_709_601_FULL = YUV709F_TO_YUV601F,       /* YCbCr_709 FULL->YCbCr_601 FULL */
	RK_PQ_CSC_YUV2YUV_601_709_FULL = YUV601F_TO_YUV709F,       /* YCbCr_601 FULL->YCbCr_709 FULL */
	RK_PQ_CSC_YUV2YUV_FULL = IDENTITY_MODE,                    /* YCbCr FULL->YCbCr FULL */
	RK_PQ_CSC_YUV2YUV_LIMIT2FULL = YUV709L_TO_YUV709F,         /* YCbCr  LIMIT->YCbCr  FULL */
	RK_PQ_CSC_YUV2YUV_601_709_LIMIT2FULL = YUV601L_TO_YUV709F, /* YCbCr 601 LIMIT->YCbCr 709 FULL */
	RK_PQ_CSC_YUV2YUV_709_601_LIMIT2FULL = YUV709L_TO_YUV601F, /* YCbCr 709 LIMIT->YCbCr 601 FULL */
	RK_PQ_CSC_YUV2YUV_FULL2LIMIT = YUV709F_TO_YUV709L,         /* YCbCr  FULL->YCbCr  LIMIT */
	RK_PQ_CSC_YUV2YUV_601_709_FULL2LIMIT = YUV601F_TO_YUV709L, /* YCbCr 601 FULL->YCbCr 709 LIMIT */
	RK_PQ_CSC_YUV2YUV_709_601_FULL2LIMIT = YUV709F_TO_YUV601L, /* YCbCr 709 FULL->YCbCr 601 LIMIT */
	RK_PQ_CSC_YUV2RGBL_601 = YUV601L_TO_RGBL,                  /* YCbCr_601 LIMIT-> RGB LIMIT */
	RK_PQ_CSC_YUV2RGBL_709 = YUV709L_TO_RGBL,                  /* YCbCr_709 LIMIT-> RGB LIMIT */
	RK_PQ_CSC_RGBL2YUV_601 = RGBL_TO_YUV601L,                  /* RGB LIMIT->YCbCr_601 LIMIT */
	RK_PQ_CSC_RGBL2YUV_709 = RGBL_TO_YUV709L,                  /* RGB LIMIT->YCbCr_709 LIMIT */
	RK_PQ_CSC_YUV2RGBL_601_FULL = YUV601F_TO_RGBL,             /* YCbCr_601 FULL-> RGB LIMIT */
	RK_PQ_CSC_YUV2RGBL_709_FULL = YUV709F_TO_RGBL,             /* YCbCr_709 FULL-> RGB LIMIT */
	RK_PQ_CSC_RGBL2YUV_601_FULL = RGBL_TO_YUV601F,             /* RGB LIMIT->YCbCr_601 FULL */
	RK_PQ_CSC_RGBL2YUV_709_FULL = RGBL_TO_YUV709F,             /* RGB LIMIT->YCbCr_709 FULL */
	RK_PQ_CSC_RGB2RGBL = RGBF_TO_RGBL,                         /* RGB FULL->RGB LIMIT */
	RK_PQ_CSC_RGBL2RGB = RGBL_TO_RGBF,                         /* RGB LIMIT->RGB FULL */
	RK_PQ_CSC_RGBL2RGBL = IDENTITY_MODE,                       /* RGB LIMIT->RGB LIMIT */
	RK_PQ_CSC_RGB2RGB = IDENTITY_MODE,                         /* RGB FULL->RGB FULL */
	RK_PQ_CSC_YUV2RGB_2020 = YUV2020F_TO_RGBF,                 /* YUV 2020 FULL->RGB  2020 FULL */
	RK_PQ_CSC_RGB2YUV2020_LIMIT2FULL = RGBL_TO_YUV2020F,       /* BT2020RGBLIMIT -> BT2020YUVFULL */
	RK_PQ_CSC_RGB2YUV2020_LIMIT = RGBL_TO_YUV2020L,            /* BT2020RGBLIMIT -> BT2020YUVLIMIT */
	RK_PQ_CSC_RGB2YUV2020_FULL2LIMIT = RGBF_TO_YUV2020L,       /* BT2020RGBFULL -> BT2020YUVLIMIT */
	RK_PQ_CSC_RGB2YUV2020_FULL = RGBF_TO_YUV2020F,             /* BT2020RGBFULL -> BT2020YUVFULL */
	RK_PQ_CSC_YUVL2RGBL_2020 = YUV2020L_TO_RGBL,               /* BT2020 YUVL -> BT2020 RGBL */
	RK_PQ_CSC_YUVL2RGBF_2020 = YUV2020L_TO_RGBF,               /* BT2020 YUVL -> BT2020 RGBF */
	RK_PQ_CSC_YUVF2RGBL_2020 = YUV2020F_TO_RGBL,               /* BT2020 YUVF -> BT2020 RGBL */
};

enum color_space_type {
	OPTM_CS_E_UNKNOWN = 0,
	OPTM_CS_E_ITU_R_BT_709 = 1,
	OPTM_CS_E_FCC = 4,
	OPTM_CS_E_ITU_R_BT_470_2_BG = 5,
	OPTM_CS_E_SMPTE_170_M = 6,
	OPTM_CS_E_SMPTE_240_M = 7,
	OPTM_CS_E_XV_YCC_709 = OPTM_CS_E_ITU_R_BT_709,
	OPTM_CS_E_XV_YCC_601 = 8,
	OPTM_CS_E_RGB = 9,
	OPTM_CS_E_XV_YCC_2020 = 10,
	OPTM_CS_E_RGB_2020 = 11,
};

struct rk_pq_csc_coef {
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

struct rk_pq_csc_ventor {
	s32 csc_offset0;
	s32 csc_offset1;
	s32 csc_offset2;
};

struct rk_pq_csc_dc_coef {
	s32 csc_in_dc0;
	s32 csc_in_dc1;
	s32 csc_in_dc2;
	s32 csc_out_dc0;
	s32 csc_out_dc1;
	s32 csc_out_dc2;
};

/* color space param */
struct rk_csc_colorspace_info {
	enum color_space_type input_color_space;
	enum color_space_type output_color_space;
	bool in_full_range;
	bool out_full_range;
};

struct rk_csc_mode_coef {
	enum rk_pq_csc_mode csc_mode;
	char c_csc_comment[PQ_CSC_MODE_COEF_COMMENT_LEN];
	const struct rk_pq_csc_coef *pst_csc_coef;
	const struct rk_pq_csc_dc_coef *pst_csc_dc_coef;
	struct rk_csc_colorspace_info st_csc_color_info;
};

/* for 8bit pixel depth + 8bit coef precision case */
static const struct rk_pq_csc_coef g_mode_csc_coefs_8bit_pix_8bit_precision[] = {
    {298,   0,   0,   0,  298,    0,   0,    0, 298}, /* RGBL_TO_RGBF */
    { 77, 150,  29, -44,  -87,  131, 131, -110, -21}, /* RGBL_TO_YUV601L */
    { 89, 175,  34, -50,  -99,  149, 149, -125, -24}, /* RGBL_TO_YUV601F */
    { 54, 183,  19, -30, -101,  131, 131, -119, -12}, /* RGBL_TO_YUV709L */
    { 63, 213,  22, -34, -115,  149, 149, -135, -14}, /**RGBL_TO_YUV709F */
    { 67, 174,  15, -37,  -94,  131, 131, -120, -11}, /**RGBL_TO_YUV2020L */
    { 78, 202,  18, -42, -107,  149, 149, -137, -12}, /* RGBL_TO_YUV2020F */
    {220,   0,   0,   0,  220,    0,   0,    0, 220}, /* RGBF_TO_RGBL */
    { 66, 129,  25, -38,  -74,  112, 112,  -94, -18}, /**RGBF_TO_YUV601L */
    { 77, 150,  29, -43,  -85,  128, 128, -107, -21}, /* RGBF_TO_YUV601F */
    { 47, 157,  16, -26,  -87,  113, 112, -102, -10}, /**RGBF_TO_YUV709L */
    { 54, 183,  19, -29,  -99,  128, 128, -116, -12}, /* RGBF_TO_YUV709F */
    { 58, 149,  13, -31,  -81,  112, 112, -103,  -9}, /* RGBF_TO_YUV2020L */
    { 67, 174,  15, -36,  -92,  128, 128, -118, -10}, /* RGBF_TO_YUV2020F */
    {256,   0, 351, 256,  -86, -179, 256,  444,   0}, /**YUV601L_TO_RGBL */
    {298,   0, 409, 298, -100, -208, 298,  516,   0}, /* YUV601L_TO_RGBF */
    {298,   0,   0,   0,  291,    0,   0,    0, 291}, /* YUV601L_TO_YUV601F */
    {256, -30, -53,   0,  261,   29,   0,   19, 262}, /* YUV601L_TO_YUV709L */
    {298, -34, -62,   0,  297,   33,   0,   22, 299}, /* YUV601L_TO_YUV709F */
    {220,   0, 308, 220,  -76, -157, 220,  390,   0}, /* YUV601F_TO_RGBL */
    {256,   0, 359, 256,  -88, -183, 256,  454,   0}, /* YUV601F_TO_RGBF */
    {220,   0,   0,   0,  225,    0,   0,    0, 225}, /* YUV601F_TO_YUV601L */
    {220, -26, -47,   0,  229,   26,   0,   17, 231}, /**YUV601F_TO_YUV709L */
    {256, -30, -54,   0,  261,   29,   0,   19, 262}, /* YUV601F_TO_YUV709F */
    {256,   0, 394, 256,  -47, -117, 256,  464,   0}, /* YUV709L_TO_RGBL */
    {298,   0, 459, 298,  -55, -136, 298,  541,   0}, /* YUV709L_TO_RGBF */
    {256,  25,  49,   0,  253,  -28,   0,  -19, 252}, /**YUV709L_TO_YUV601L */
    {298,  30,  57,   0,  288,  -32,   0,  -21, 287}, /* YUV709L_TO_YUV601F */
    {298,   0,   0,   0,  291,    0,   0,    0, 291}, /* YUV709L_TO_YUV709F */
    {220,   0, 346, 220,  -41, -103, 220,  408,   0}, /* YUV709F_TO_RGBL */
    {256,   0, 403, 256,  -48, -120, 256,  475,   0}, /* YUV709F_TO_RGBF */
    {220,  22,  43,   0,  223,  -25,   0,  -16, 221}, /**YUV709F_TO_YUV601L */
    {256,  26,  50,   0,  253,  -28,   0,  -19, 252}, /* YUV709F_TO_YUV601F */
    {220,   0,   0,   0,  225,    0,   0,    0, 225}, /* YUV709F_TO_YUV709L */
    {256,   0, 369, 256,  -41, -143, 256,  471,   0}, /* YUV2020L_TO_RGBL */
    {298,   0, 430, 298,  -48, -167, 298,  548,   0}, /* YUV2020L_TO_RGBF */
    {298,   0,   0,   0,  291,    0,   0,    0, 291}, /* YUV2020L_TO_YUV2020F */
    {220,   0, 324, 220,  -36, -126, 220,  414,   0}, /* YUV2020F_TO_RGBL */
    {256,   0, 377, 256,  -42, -146, 256,  482,   0}, /* YUV2020F_TO_RGBF */
    {220,   0,   0,   0,  225,    0,   0,    0, 225}, /* YUV2020F_TO_YUV2020L */
	{256,   0,   0,   0,  256,    0,   0,    0, 256}, /* IDENTITY_MODE */
};

/* for 10bit pixel depth + 13bit coef precision case */
static const struct rk_pq_csc_coef g_mode_csc_coefs_10bit_pix_13bit_precision[] = {
    {9567,     0,     0,     0,  9567,     0,    0,     0, 9567}, /* RGBL_TO_RGBF */
    {2449,  4809,   934, -1414, -2776,  4190, 4189, -3508, -681}, /* RGBL_TO_YUV601L */
    {2860,  5616,  1091, -1614, -3169,  4783, 4783, -4005, -778}, /* RGBL_TO_YUV601F */
    {1742,  5859,   591,  -960, -3230,  4190, 4189, -3805, -384}, /* RGBL_TO_YUV709L */
    {2034,  6842,   691, -1096, -3687,  4783, 4783, -4345, -438}, /**RGBL_TO_YUV709F */
    {2152,  5554,   486, -1170, -3020,  4190, 4190, -3853, -337}, /**RGBL_TO_YUV2020L */
    {2513,  6486,   568, -1336, -3447,  4783, 4783, -4398, -385}, /* RGBL_TO_YUV2020F */
    {7015,     0,     0,     0,  7015,     0,    0,     0, 7015}, /* RGBF_TO_RGBL */
    {2097,  4118,   800, -1211, -2377,  3588, 3587, -3004, -583}, /**RGBF_TO_YUV601L */
    {2449,  4809,   934, -1382, -2714,  4096, 4096, -3430, -666}, /* RGBF_TO_YUV601F */
    {1491,  5017,   507,  -822, -2765,  3587, 3588, -3259, -329}, /**RGBF_TO_YUV709L */
    {1742,  5859,   591,  -939, -3157,  4096, 4096, -3720, -376}, /* RGBF_TO_YUV709F */
    {1843,  4756,   416, -1002, -2586,  3588, 3588, -3299, -289}, /* RGBF_TO_YUV2020L */
    {2152,  5554,   486, -1144, -2952,  4096, 4096, -3767, -329}, /* RGBF_TO_YUV2020F */
    {8192,     0, 11229,  8192, -2756, -5720, 8192, 14192,    0}, /**YUV601L_TO_RGBL */
    {9567,     0, 13113,  9567, -3219, -6679, 9567, 16574,    0}, /* YUV601L_TO_RGBF */
    {9567,     0,     0,     0,  9353,     0,    0,     0, 9353}, /* YUV601L_TO_YUV601F */
    {8192,  -947, -1703,     0,  8345,   939,    0,   615, 8399}, /* YUV601L_TO_YUV709L */
    {9567, -1105, -1989,     0,  9527,  1072,    0,   702, 9590}, /* YUV601L_TO_YUV709F */
    {7015,     0,  9835,  7015, -2414, -5010, 7015, 12430,    0}, /* YUV601F_TO_RGBL */
    {8192,     0, 11485,  8192, -2819, -5850, 8192, 14516,    0}, /* YUV601F_TO_RGBF */
    {7015,     0,     0,     0,  7175,     0,    0,     0, 7175}, /* YUV601F_TO_YUV601L */
    {7015,  -829, -1492,     0,  7309,   822,    0,   538, 7357}, /**YUV601F_TO_YUV709L */
    {8192,  -968, -1742,     0,  8345,   939,    0,   615, 8399}, /* YUV601F_TO_YUV709F */
    {8192,     0, 12613,  8192, -1500, -3749, 8192, 14862,    0}, /* YUV709L_TO_RGBL */
    {9567,     0, 14729,  9567, -1752, -4378, 9567, 17356,    0}, /* YUV709L_TO_RGBF */
    {8192,   814,  1570,     0,  8109,  -906,    0,  -594, 8056}, /**YUV709L_TO_YUV601L */
    {9567,   950,  1834,     0,  9258, -1035,    0,  -678, 9198}, /* YUV709L_TO_YUV601F */
    {9567,     0,     0,     0,  9353,     0,    0,     0, 9353}, /* YUV709L_TO_YUV709F */
    {7015,     0, 11047,  7015, -1314, -3284, 7015, 13017,    0}, /* YUV709F_TO_RGBL */
    {8192,     0, 12901,  8192, -1535, -3835, 8192, 15201,    0}, /* YUV709F_TO_RGBF */
    {7015,   713,  1375,     0,  7102,  -794,    0,  -520, 7056}, /**YUV709F_TO_YUV601L */
    {8192,   832,  1606,     0,  8109,  -906,    0,  -594, 8056}, /* YUV709F_TO_YUV601F */
    {7015,     0,     0,     0,  7175,     0,    0,     0, 7175}, /* YUV709F_TO_YUV709L */
    {8192,     0, 11810,  8192, -1318, -4576, 8192, 15068,    0}, /* YUV2020L_TO_RGBL */
    {9567,     0, 13792,  9567, -1539, -5344, 9567, 17597,    0}, /* YUV2020L_TO_RGBF */
    {9567,     0,     0,     0,  9353,     0,    0,     0, 9353}, /* YUV2020L_TO_YUV2020F */
    {7015,     0, 10344,  7015, -1154, -4008, 7015, 13198,    0}, /* YUV2020F_TO_RGBL */
    {8192,     0, 12080,  8192, -1348, -4681, 8192, 15412,    0}, /* YUV2020F_TO_RGBF */
    {7015,     0,     0,     0,  7175,     0,    0,     0, 7175}, /* YUV2020F_TO_YUV2020L */
    {8192,     0,     0,     0,  8192,     0,    0,     0, 8192}, /* IDENTITY_MODE */
};

/*
 *CSC matrix
 */
/* xv_ycc BT.601 limit(i.e. SD) -> RGB full */
static const struct rk_pq_csc_coef rk_csc_table_xv_yccsdy_cb_cr_limit_to_rgb_full = {
	1196, 0, 1639,
	1196, -402, -835,
	1196, 2072, 0
};

static const struct rk_pq_csc_dc_coef rk_dc_csc_table_xv_yccsdy_cb_cr_limit_to_rgb_full = {
	-64, -512, -512,
	0, 0, 0
};

/* BT.709 limit(i.e. HD) -> RGB full */
static const struct rk_pq_csc_coef rk_csc_table_hdy_cb_cr_limit_to_rgb_full = {
	1196, 0, 1841,
	1196, -219, -547,
	1196, 2169, 0
};

static const struct rk_pq_csc_dc_coef rk_dc_csc_table_hdy_cb_cr_limit_to_rgb_full = {
	-64, -512, -512,
	0, 0, 0
};

/* RGB full-> YUV601 (i.e. SD) limit */
static const struct rk_pq_csc_coef rk_csc_table_rgb_to_xv_yccsdy_cb_cr = {
	262, 515, 100,
	-151, -297, 448,
	448, -376, -73
};

static const struct rk_pq_csc_dc_coef rk_dc_csc_table_rgb_to_xv_yccsdy_cb_cr = {
	0, 0, 0,
	64, 512, 512
};

/* RGB full-> YUV709 (i.e. SD) limit */
static const struct rk_pq_csc_coef rk_csc_table_rgb_to_hdy_cb_cr = {
	186, 627, 63,
	-103, -346, 448,
	448, -407, -41
};

static const struct rk_pq_csc_dc_coef rk_dc_csc_table_rgb_to_hdy_cb_cr = {
	0, 0, 0,
	64, 512, 512
};

/* BT.709 (i.e. HD) -> to xv_ycc BT.601 (i.e. SD) */
static const struct rk_pq_csc_coef rk_csc_table_hdy_cb_cr_to_xv_yccsdy_cb_cr = {
	1024, 104, 201,
	0, 1014, -113,
	0, -74, 1007
};
static const struct rk_pq_csc_dc_coef rk_dc_csc_table_hdy_cb_cr_to_xv_yccsdy_cb_cr = {
	-64, -512, -512,
	64, 512, 512
};
static const struct rk_pq_csc_dc_coef rk_dc_csc_table_hdy_cb_cr_full_to_xv_yccsdy_cb_cr_full = {
	0, -512, -512,
	0, 512, 512
};

/* xv_ycc BT.601 (i.e. SD) -> to BT.709 (i.e. HD) */
static const struct rk_pq_csc_coef rk_csc_table_xv_yccsdy_cb_cr_to_hdy_cb_cr = {
	1024, -118, -213,
	0, 1043, 117,
	0, 77, 1050
};

/* xv_ycc BT.601 full(i.e. SD) -> to BT.709 full(i.e. HD) */
static const struct rk_pq_csc_coef rk_csc_table_xv_yccsdy_cb_cr_full_to_hdy_cb_cr_full = {
	1024, -121, -218,
	0, 1043, 117,
	0, 77, 1050
};

static const struct rk_pq_csc_dc_coef rk_dc_csc_table_xv_yccsdy_cb_cr_to_hdy_cb_cr = {
	-64, -512, -512,
	64, 512, 512
};

/* xv_ycc BT.601 full(i.e. SD) -> RGB full */
static const struct rk_pq_csc_coef rk_csc_table_xv_yccsdy_cb_cr_to_rgb_full = {
	1024, 0, 1436,
	1024, -352, -731,
	1024, 1815, 0
};
static const struct rk_pq_csc_dc_coef rk_dc_csc_table_xv_yccsdy_cb_cr_to_rgb_full = {
	0, -512, -512,
	0, 0, 0
};

/* BT.709 full(i.e. HD) -> RGB full */
static const struct rk_pq_csc_coef rk_csc_table_hdy_cb_cr_to_rgb_full = {
	1024, 0, 1613,
	1024, -192, -479,
	1024, 1900, 0
};
static const struct rk_pq_csc_dc_coef rk_dc_csc_table_hdy_cb_cr_to_rgb_full = {
	0, -512, -512,
	0, 0, 0
};

/* RGB full-> YUV601 full(i.e. SD) */
static const struct rk_pq_csc_coef rk_csc_table_rgb_to_xv_yccsdy_cb_cr_full = {
	306, 601, 117,
	-173, -339, 512,
	512, -429, -83
};
static const struct rk_pq_csc_dc_coef rk_dc_csc_table_rgb_to_xv_yccsdy_cb_cr_full = {
	0, 0, 0,
	0, 512, 512
};

/* RGB full-> YUV709 full (i.e. SD) */
static const struct rk_pq_csc_coef rk_csc_table_rgb_to_hdy_cb_cr_full = {
	218, 732, 74,
	-117, -395, 512,
	512, -465, -47
};
static const struct rk_pq_csc_dc_coef rk_dc_csc_table_rgb_to_hdy_cb_cr_full = {
	0, 0, 0,
	0, 512, 512
};

/* limit -> full */
static const struct rk_pq_csc_coef rk_csc_table_identity_y_cb_cr_limit_to_y_cb_cr_full = {
	1196, 0, 0,
	0, 1169, 0,
	0, 0, 1169
};
static const struct rk_pq_csc_dc_coef rk_dc_csc_table_identity_y_cb_cr_limit_to_y_cb_cr_full = {
	-64, -512, -512,
	0, 512, 512
};

/* 601 limit -> 709 full */
static const struct rk_pq_csc_coef rk_csc_table_identity_601_limit_to_709_full = {
	1196, -138, -249,
	0, 1191, 134,
	0, 88, 1199
};
static const struct rk_pq_csc_dc_coef rk_dc_csc_table_identity_601_limit_to_709_full = {
	-64, -512, -512,
	0, 512, 512
};

/* 709 limit -> 601 full */
static const struct rk_pq_csc_coef rk_csc_table_identity_709_limit_to_601_full = {
	1196, 119, 229,
	0, 1157, -129,
	0, -85, 1150
};
static const struct rk_pq_csc_dc_coef rk_dc_csc_table_identity_709_limit_to_601_full = {
	-64, -512, -512,
	0, 512, 512
};

/* full ->   limit */
static const struct rk_pq_csc_coef rk_csc_table_identity_y_cb_cr_full_to_y_cb_cr_limit = {
	877, 0, 0,
	0, 897, 0,
	0, 0, 897
};
static const struct rk_pq_csc_dc_coef rk_dc_csc_table_identity_y_cb_cr_full_to_y_cb_cr_limit = {
	0, -512, -512,
	64, 512, 512
};

/* 601 full ->  709 limit */
static const struct rk_pq_csc_coef rk_csc_table_identity_y_cb_cr_601_full_to_y_cb_cr_709_limit = {
	877, -106, -191,
	0, 914, 103,
	0, 67, 920
};
static const struct rk_pq_csc_dc_coef
rk_dc_csc_table_identity_y_cb_cr_601_full_to_y_cb_cr_709_limit = {
	0, -512, -512,
	64, 512, 512
};

/* 709 full ->  601 limit */
static const struct rk_pq_csc_coef rk_csc_table_identity_y_cb_cr_709_full_to_y_cb_cr_601_limit = {
	877, 91, 176,
	0, 888, -99,
	0, -65, 882
};
static const struct rk_pq_csc_dc_coef
rk_dc_csc_table_identity_y_cb_cr_709_full_to_y_cb_cr_601_limit = {
	0, -512, -512,
	64, 512, 512
};

/* xv_ycc BT.601 limit(i.e. SD) -> RGB limit */
static const struct rk_pq_csc_coef rk_csc_table_xv_yccsdy_cb_cr_limit_to_rgb_limit = {
	1024, 0, 1404,
	1024, -344, -715,
	1024, 1774, 0
};
static const struct rk_pq_csc_dc_coef rk_dc_csc_table_xv_yccsdy_cb_cr_limit_to_rgb_limit = {
	-64, -512, -512,
	64, 64, 64
};

/* BT.709 limit(i.e. HD) -> RGB limit */
static const struct rk_pq_csc_coef rk_csc_table_hdy_cb_cr_limit_to_rgb_limit = {
	1024, 0, 1577,
	1024, -188, -469,
	1024, 1858, 0
};
static const struct rk_pq_csc_dc_coef rk_dc_csc_table_hdy_cb_cr_limit_to_rgb_limit = {
	-64, -512, -512,
	64, 64, 64
};

/* RGB limit-> YUV601 (i.e. SD) limit */
static const struct rk_pq_csc_coef rk_csc_table_rgb_limit_to_xv_yccsdy_cb_cr = {
	306, 601, 117,
	-177, -347, 524,
	524, -439, -85
};
static const struct rk_pq_csc_dc_coef rk_dc_csc_table_rgb_limit_to_xv_yccsdy_cb_cr = {
	-64, -64, -64,
	64, 512, 512
};

/* RGB limit -> YUV709 (i.e. SD) limit */
static const struct rk_pq_csc_coef rk_csc_table_rgb_limit_to_hdy_cb_cr = {
	218, 732, 74,
	-120, -404, 524,
	524, -476, -48
};
static const struct rk_pq_csc_dc_coef rk_dc_csc_table_rgb_limit_to_hdy_cb_cr = {
	-64, -64, -64,
	64, 512, 512
};

/* xv_ycc BT.601 full(i.e. SD) -> RGB limit */
static const struct rk_pq_csc_coef rk_csc_table_xv_yccsdy_cb_cr_to_rgb_limit = {
	877, 0, 1229,
	877, -302, -626,
	877, 1554, 0
};
static const struct rk_pq_csc_dc_coef rk_dc_csc_table_xv_yccsdy_cb_cr_to_rgb_limit = {
	0, -512, -512,
	64, 64, 64
};

/* BT.709 full(i.e. HD) -> RGB limit */
static const struct rk_pq_csc_coef rk_csc_table_hdy_cb_cr_to_rgb_limit = {
	877, 0, 1381,
	877, -164, -410,
	877, 1627, 0
};
static const struct rk_pq_csc_dc_coef rk_dc_csc_table_hdy_cb_cr_to_rgb_limit = {
	0, -512, -512,
	64, 64, 64
};

/* RGB limit-> YUV601 full(i.e. SD) */
static const struct rk_pq_csc_coef rk_csc_table_rgb_limit_to_xv_yccsdy_cb_cr_full = {
	358, 702, 136,
	-202, -396, 598,
	598, -501, -97
};
static const struct rk_pq_csc_dc_coef rk_dc_csc_table_rgb_limit_to_xv_yccsdy_cb_cr_full = {
	-64, -64, -64,
	0, 512, 512
};

/* RGB limit-> YUV709 full (i.e. SD) */
static const struct rk_pq_csc_coef rk_csc_table_rgb_limit_to_hdy_cb_cr_full = {
	254, 855, 86,
	-137, -461, 598,
	598, -543, -55
};
static const struct rk_pq_csc_dc_coef rk_dc_csc_table_rgb_limit_to_hdy_cb_cr_full = {
	-64, -64, -64,
	0, 512, 512
};

/* RGB full -> RGB limit */
static const struct rk_pq_csc_coef rk_csc_table_identity_rgb_to_rgb_limit = {
	877, 0, 0,
	0, 877, 0,
	0, 0, 877
};
static const struct rk_pq_csc_dc_coef rk_dc_csc_table_identity_rgb_to_rgb_limit = {
	0, 0, 0,
	64, 64, 64
};

/* RGB limit -> RGB full */
static const struct rk_pq_csc_coef rk_csc_table_identity_rgb_limit_to_rgb = {
	1196, 0, 0,
	0, 1196, 0,
	0, 0, 1196
};
static const struct rk_pq_csc_dc_coef rk_dc_csc_table_identity_rgb_limit_to_rgb = {
	-64, -64, -64,
	0, 0, 0
};

/* RGB limit/full -> RGB limit/full */
static const struct rk_pq_csc_coef rk_csc_table_identity_rgb_to_rgb = {
	1024, 0, 0,
	0, 1024, 0,
	0, 0, 1024
};
static const struct rk_pq_csc_dc_coef rk_dc_csc_table_identity_rgb_to_rgb1 = {
	-64, -64, -64,
	64, 64, 64
};

static const struct rk_pq_csc_dc_coef rk_dc_csc_table_identity_rgb_to_rgb2 = {
	0, 0, 0,
	0, 0, 0
};

static const struct rk_pq_csc_coef rk_csc_table_identity_yuv_to_rgb_2020 = {
	1024, 0, 1510,
	1024, -169, -585,
	1024, 1927, 0
};
static const struct rk_pq_csc_dc_coef rk_dc_csc_table_identity_yuv_to_rgb_2020 = {
	0, -512, -512,
	0, 0, 0
};

/* 2020 RGB LIMIT ->YUV LIMIT */
static const struct rk_pq_csc_coef rk_csc_table_identity_rgb_limit_to_yuv_limit_2020 = {
	269, 694, 61,
	-146, -377, 524,
	524, -482, -42
};
static const struct rk_pq_csc_dc_coef rk_dc_csc_table_identity_rgb_limit_to_yuv_limit_2020 = {
	-64, -64, -64,
	64, 512, 512
};

/* 2020 RGB LIMIT ->YUV FULL */
static const struct rk_pq_csc_coef rk_csc_table_identity_rgb_limit_to_yuv_full_2020 = {
	314, 811, 71,
	-167, -431, 598,
	598, -550, -48
};
static const struct rk_pq_csc_dc_coef rk_dc_csc_table_identity_rgb_limit_to_yuv_full_2020 = {
	-64, -64, -64,
	0, 512, 512
};

/* 2020 RGB FULL ->YUV LIMIT */
static const struct rk_pq_csc_coef rk_csc_table_identity_rgb_full_to_yuv_limit_2020 = {
	230, 595, 52,
	-125, -323, 448,
	448, -412, -36
};
static const struct rk_pq_csc_dc_coef rk_dc_csc_table_identity_rgb_full_to_yuv_limit_2020 = {
	0, 0, 0,
	64, 512, 512
};

/* 2020 RGB FULL ->YUV FULL */
static const struct rk_pq_csc_coef rk_csc_table_identity_rgb_full_to_yuv_full_2020 = {
	269, 694, 61,
	-143, -369, 512,
	512, -471, -41
};
static const struct rk_pq_csc_dc_coef rk_dc_csc_table_identity_rgb_full_to_yuv_full_2020 = {
	0, 0, 0,
	0, 512, 512
};

/* identity matrix */
static const struct rk_pq_csc_coef rk_csc_table_identity_y_cb_cr_to_y_cb_cr = {
	1024, 0, 0,
	0, 1024, 0,
	0, 0, 1024
};

/* 2020 Y2R */
static const struct rk_pq_csc_coef rk_csc_table_y2r_l2l_2020 = {1024, 0, 1476, 1024, -165, -572, 1024, 1884, 0};
static const struct rk_pq_csc_coef rk_csc_table_y2r_l2f_2020 = {1196, 0, 1724, 1196, -192, -668, 1196, 2200, 0};
static const struct rk_pq_csc_coef rk_csc_table_y2r_f2l_2020 = {877, 0, 1293, 877, -144, -501, 877, 1650, 0};

/* 10bit Hue Sin Look Up Table -> range[30, -30] */
static const s32 g_hue_sin_table[PQ_CSC_HUE_TABLE_NUM] = {
	512, 508, 505, 501, 497, 494, 490, 486,
	483, 479, 475, 472, 468, 464, 460, 457,
	453, 449, 445, 442, 438, 434, 430, 426,
	423, 419, 415, 411, 407, 403, 400, 396,
	392, 388, 384, 380, 376, 372, 369, 365,
	361, 357, 353, 349, 345, 341, 337, 333,
	329, 325, 321, 317, 313, 309, 305, 301,
	297, 293, 289, 285, 281, 277, 273, 269,
	265, 261, 257, 253, 249, 245, 241, 237,
	233, 228, 224, 220, 216, 212, 208, 204,
	200, 196, 192, 187, 183, 179, 175, 171,
	167, 163, 159, 154, 150, 146, 142, 138,
	134, 130, 125, 121, 117, 113, 109, 105,
	100, 96, 92, 88, 84, 80, 75, 71,
	67, 63, 59, 54, 50, 46, 42, 38,
	34, 29, 25, 21, 17, 13, 8, 4,
	0, -4, -8, -13, -17, -21, -25, -29,
	-34, -38, -42, -46, -50, -54, -59, -63,
	-67, -71, -75, -80, -84, -88, -92, -96,
	-100, -105, -109, -113, -117, -121, -125, -130,
	-134, -138, -142, -146, -150, -154, -159, -163,
	-167, -171, -175, -179, -183, -187, -192, -196,
	-200, -204, -208, -212, -216, -220, -224, -228,
	-233, -237, -241, -245, -249, -253, -257, -261,
	-265, -269, -273, -277, -281, -285, -289, -293,
	-297, -301, -305, -309, -313, -317, -321, -325,
	-329, -333, -337, -341, -345, -349, -353, -357,
	-361, -365, -369, -372, -376, -380, -384, -388,
	-392, -396, -400, -403, -407, -411, -415, -419,
	-423, -426, -430, -434, -438, -442, -445, -449,
	-453, -457, -460, -464, -468, -472, -475, -479,
	-483, -486, -490, -494, -497, -501, -505, -508,
};

/* 10bit Hue Cos Look Up Table  -> range[-30, 30] */
static const s32 g_hue_cos_table[PQ_CSC_HUE_TABLE_NUM] = {
	887, 889, 891, 893, 895, 897, 899, 901,
	903, 905, 907, 909, 911, 913, 915, 917,
	919, 920, 922, 924, 926, 928, 929, 931,
	933, 935, 936, 938, 940, 941, 943, 945,
	946, 948, 949, 951, 953, 954, 956, 957,
	959, 960, 962, 963, 964, 966, 967, 969,
	970, 971, 973, 974, 975, 976, 978, 979,
	980, 981, 983, 984, 985, 986, 987, 988,
	989, 990, 992, 993, 994, 995, 996, 997,
	998, 998, 999, 1000, 1001, 1002, 1003, 1004,
	1005, 1005, 1006, 1007, 1008, 1008, 1009, 1010,
	1011, 1011, 1012, 1013, 1013, 1014, 1014, 1015,
	1015, 1016, 1016, 1017, 1017, 1018, 1018, 1019,
	1019, 1020, 1020, 1020, 1021, 1021, 1021, 1022,
	1022, 1022, 1022, 1023, 1023, 1023, 1023, 1023,
	1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024,
	1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024,
	1023, 1023, 1023, 1023, 1023, 1022, 1022, 1022,
	1022, 1021, 1021, 1021, 1020, 1020, 1020, 1019,
	1019, 1018, 1018, 1017, 1017, 1016, 1016, 1015,
	1015, 1014, 1014, 1013, 1013, 1012, 1011, 1011,
	1010, 1009, 1008, 1008, 1007, 1006, 1005, 1005,
	1004, 1003, 1002, 1001, 1000, 999, 998, 998,
	997, 996, 995, 994, 993, 992, 990, 989,
	988, 987, 986, 985, 984, 983, 981, 980,
	979, 978, 976, 975, 974, 973, 971, 970,
	969, 967, 966, 964, 963, 962, 960, 959,
	957, 956, 954, 953, 951, 949, 948, 946,
	945, 943, 941, 940, 938, 936, 935, 933,
	931, 929, 928, 926, 924, 922, 920, 919,
	917, 915, 913, 911, 909, 907, 905, 903,
	901, 899, 897, 895, 893, 891, 889, 887
};

/*
 *CSC Param Struct
 */
static const struct rk_csc_mode_coef g_mode_csc_coef[] = {
	{
		RK_PQ_CSC_YUV2RGB_601, "YUV601 L->RGB F",
		&rk_csc_table_xv_yccsdy_cb_cr_limit_to_rgb_full,
		&rk_dc_csc_table_xv_yccsdy_cb_cr_limit_to_rgb_full,
		{
			OPTM_CS_E_XV_YCC_601, OPTM_CS_E_RGB, false, true
		}
	},
	{
		RK_PQ_CSC_YUV2RGB_709, "YUV709 L->RGB F",
		&rk_csc_table_hdy_cb_cr_limit_to_rgb_full,
		&rk_dc_csc_table_hdy_cb_cr_limit_to_rgb_full,
		{
			OPTM_CS_E_ITU_R_BT_709, OPTM_CS_E_RGB, false, true
		}
	},
	{
		RK_PQ_CSC_RGB2YUV_601, "RGB F->YUV601 L",
		&rk_csc_table_rgb_to_xv_yccsdy_cb_cr,
		&rk_dc_csc_table_rgb_to_xv_yccsdy_cb_cr,
		{
			OPTM_CS_E_RGB, OPTM_CS_E_XV_YCC_601, true, false
		}
	},
	{
		RK_PQ_CSC_RGB2YUV_709, "RGB F->YUV709 L",
		&rk_csc_table_rgb_to_hdy_cb_cr,
		&rk_dc_csc_table_rgb_to_hdy_cb_cr,
		{
			OPTM_CS_E_RGB, OPTM_CS_E_ITU_R_BT_709, true, false
		}
	},
	{
		RK_PQ_CSC_YUV2YUV_709_601, "YUV709 L->YUV601 L",
		&rk_csc_table_hdy_cb_cr_to_xv_yccsdy_cb_cr,
		&rk_dc_csc_table_hdy_cb_cr_to_xv_yccsdy_cb_cr,
		{
			OPTM_CS_E_ITU_R_BT_709, OPTM_CS_E_XV_YCC_601, false, false
		}
	},
	{
		RK_PQ_CSC_YUV2YUV_601_709, "YUV601 L->YUV709 L",
		&rk_csc_table_xv_yccsdy_cb_cr_to_hdy_cb_cr,
		&rk_dc_csc_table_xv_yccsdy_cb_cr_to_hdy_cb_cr,
		{
			OPTM_CS_E_XV_YCC_601, OPTM_CS_E_ITU_R_BT_709, false, false
		}
	},
	{
		RK_PQ_CSC_YUV2YUV, "YUV L->YUV L",
		&rk_csc_table_identity_y_cb_cr_to_y_cb_cr,
		&rk_dc_csc_table_xv_yccsdy_cb_cr_to_hdy_cb_cr,
		{
			OPTM_CS_E_ITU_R_BT_709, OPTM_CS_E_ITU_R_BT_709, false, false
		}
	},
	{
		RK_PQ_CSC_YUV2RGB_601_FULL, "YUV601 F->RGB F",
		&rk_csc_table_xv_yccsdy_cb_cr_to_rgb_full,
		&rk_dc_csc_table_xv_yccsdy_cb_cr_to_rgb_full,
		{
			OPTM_CS_E_XV_YCC_601, OPTM_CS_E_RGB, true, true
		}
	},
		{
		RK_PQ_CSC_YUV2RGB_709_FULL, "YUV709 F->RGB F",
		&rk_csc_table_hdy_cb_cr_to_rgb_full,
		&rk_dc_csc_table_hdy_cb_cr_to_rgb_full,
		{
			OPTM_CS_E_ITU_R_BT_709, OPTM_CS_E_RGB, true, true
		}
	},
	{
		RK_PQ_CSC_RGB2YUV_601_FULL, "RGB F->YUV601 F",
		&rk_csc_table_rgb_to_xv_yccsdy_cb_cr_full,
		&rk_dc_csc_table_rgb_to_xv_yccsdy_cb_cr_full,
		{
			OPTM_CS_E_RGB, OPTM_CS_E_XV_YCC_601, true, true
		}
	},
	{
		RK_PQ_CSC_RGB2YUV_709_FULL, "RGB F->YUV709 F",
		&rk_csc_table_rgb_to_hdy_cb_cr_full,
		&rk_dc_csc_table_rgb_to_hdy_cb_cr_full,
		{
			OPTM_CS_E_RGB, OPTM_CS_E_ITU_R_BT_709, true, true
		}
	},
	{
		RK_PQ_CSC_YUV2YUV_709_601_FULL, "YUV709 F->YUV601 F",
		&rk_csc_table_hdy_cb_cr_to_xv_yccsdy_cb_cr,
		&rk_dc_csc_table_hdy_cb_cr_full_to_xv_yccsdy_cb_cr_full,
		{
			OPTM_CS_E_ITU_R_BT_709, OPTM_CS_E_XV_YCC_601, true, true
		}
	},
	{
		RK_PQ_CSC_YUV2YUV_601_709_FULL, "YUV601 F->YUV709 F",
		&rk_csc_table_xv_yccsdy_cb_cr_full_to_hdy_cb_cr_full,
		&rk_dc_csc_table_hdy_cb_cr_full_to_xv_yccsdy_cb_cr_full,
		{
			OPTM_CS_E_XV_YCC_601, OPTM_CS_E_ITU_R_BT_709, true, true
		}
	},
	{
		RK_PQ_CSC_YUV2YUV_FULL, "YUV F->YUV F",
		&rk_csc_table_identity_y_cb_cr_to_y_cb_cr,
		&rk_dc_csc_table_hdy_cb_cr_full_to_xv_yccsdy_cb_cr_full,
		{
			OPTM_CS_E_ITU_R_BT_709, OPTM_CS_E_ITU_R_BT_709, true, true
		}
	},
	{
		RK_PQ_CSC_YUV2YUV_LIMIT2FULL, "YUV L->YUV F",
		&rk_csc_table_identity_y_cb_cr_limit_to_y_cb_cr_full,
		&rk_dc_csc_table_identity_y_cb_cr_limit_to_y_cb_cr_full,
		{
			OPTM_CS_E_ITU_R_BT_709, OPTM_CS_E_ITU_R_BT_709, false, true
		}
	},
	{
		RK_PQ_CSC_YUV2YUV_601_709_LIMIT2FULL, "YUV601 L->YUV709 F",
		&rk_csc_table_identity_601_limit_to_709_full,
		&rk_dc_csc_table_identity_601_limit_to_709_full,
		{
			OPTM_CS_E_XV_YCC_601, OPTM_CS_E_ITU_R_BT_709, false, true
		}
	},
	{
		RK_PQ_CSC_YUV2YUV_709_601_LIMIT2FULL, "YUV709 L->YUV601 F",
		&rk_csc_table_identity_709_limit_to_601_full,
		&rk_dc_csc_table_identity_709_limit_to_601_full,
		{
			OPTM_CS_E_ITU_R_BT_709, OPTM_CS_E_XV_YCC_601, false, true
		}
	},
	{
		RK_PQ_CSC_YUV2YUV_FULL2LIMIT, "YUV F->YUV L",
		&rk_csc_table_identity_y_cb_cr_full_to_y_cb_cr_limit,
		&rk_dc_csc_table_identity_y_cb_cr_full_to_y_cb_cr_limit,
		{
			OPTM_CS_E_ITU_R_BT_709, OPTM_CS_E_ITU_R_BT_709, true, false
		}
	},
	{
		RK_PQ_CSC_YUV2YUV_601_709_FULL2LIMIT, "YUV601 F->YUV709 L",
		&rk_csc_table_identity_y_cb_cr_601_full_to_y_cb_cr_709_limit,
		&rk_dc_csc_table_identity_y_cb_cr_601_full_to_y_cb_cr_709_limit,
		{
			OPTM_CS_E_XV_YCC_601, OPTM_CS_E_ITU_R_BT_709, true, false
		}
	},
	{
		RK_PQ_CSC_YUV2YUV_709_601_FULL2LIMIT, "YUV709 F->YUV601 L",
		&rk_csc_table_identity_y_cb_cr_709_full_to_y_cb_cr_601_limit,
		&rk_dc_csc_table_identity_y_cb_cr_709_full_to_y_cb_cr_601_limit,
		{
			OPTM_CS_E_ITU_R_BT_709, OPTM_CS_E_XV_YCC_601, true, false
		}
	},
	{
		RK_PQ_CSC_YUV2RGBL_601, "YUV601 L->RGB L",
		&rk_csc_table_xv_yccsdy_cb_cr_limit_to_rgb_limit,
		&rk_dc_csc_table_xv_yccsdy_cb_cr_limit_to_rgb_limit,
		{
			OPTM_CS_E_XV_YCC_601, OPTM_CS_E_RGB, false, false
		}
	},
	{
		RK_PQ_CSC_YUV2RGBL_709, "YUV709 L->RGB L",
		&rk_csc_table_hdy_cb_cr_limit_to_rgb_limit,
		&rk_dc_csc_table_hdy_cb_cr_limit_to_rgb_limit,
		{
			OPTM_CS_E_ITU_R_BT_709, OPTM_CS_E_RGB, false, false
		}
	},
	{
		RK_PQ_CSC_RGBL2YUV_601, "RGB L->YUV601 L",
		&rk_csc_table_rgb_limit_to_xv_yccsdy_cb_cr,
		&rk_dc_csc_table_rgb_limit_to_xv_yccsdy_cb_cr,
		{
			OPTM_CS_E_RGB, OPTM_CS_E_XV_YCC_601, false, false
		}
	},
	{
		RK_PQ_CSC_RGBL2YUV_709, "RGB L->YUV709 L",
		&rk_csc_table_rgb_limit_to_hdy_cb_cr,
		&rk_dc_csc_table_rgb_limit_to_hdy_cb_cr,
		{
			OPTM_CS_E_RGB, OPTM_CS_E_ITU_R_BT_709, false, false
		}
	},
	{
		RK_PQ_CSC_YUV2RGBL_601_FULL, "YUV601 F->RGB L",
		&rk_csc_table_xv_yccsdy_cb_cr_to_rgb_limit,
		&rk_dc_csc_table_xv_yccsdy_cb_cr_to_rgb_limit,
		{
			OPTM_CS_E_XV_YCC_601, OPTM_CS_E_RGB, true, false
		}
	},
	{
		RK_PQ_CSC_YUV2RGBL_709_FULL, "YUV709 F->RGB L",
		&rk_csc_table_hdy_cb_cr_to_rgb_limit,
		&rk_dc_csc_table_hdy_cb_cr_to_rgb_limit,
		{
			OPTM_CS_E_ITU_R_BT_709, OPTM_CS_E_RGB, true, false
		}
	},
	{
		RK_PQ_CSC_RGBL2YUV_601_FULL, "RGB L->YUV601 F",
		&rk_csc_table_rgb_limit_to_xv_yccsdy_cb_cr_full,
		&rk_dc_csc_table_rgb_limit_to_xv_yccsdy_cb_cr_full,
		{
			OPTM_CS_E_RGB, OPTM_CS_E_XV_YCC_601, false, true
		}
	},
	{
		RK_PQ_CSC_RGBL2YUV_709_FULL, "RGB L->YUV709 F",
		&rk_csc_table_rgb_limit_to_hdy_cb_cr_full,
		&rk_dc_csc_table_rgb_limit_to_hdy_cb_cr_full,
		{
			OPTM_CS_E_RGB, OPTM_CS_E_ITU_R_BT_709, false, true
		}
	},
	{
		RK_PQ_CSC_RGB2RGBL, "RGB F->RGB L",
		&rk_csc_table_identity_rgb_to_rgb_limit,
		&rk_dc_csc_table_identity_rgb_to_rgb_limit,
		{
			OPTM_CS_E_RGB, OPTM_CS_E_RGB, true, false
		}
	},
	{
		RK_PQ_CSC_RGBL2RGB, "RGB L->RGB F",
		&rk_csc_table_identity_rgb_limit_to_rgb,
		&rk_dc_csc_table_identity_rgb_limit_to_rgb,
		{
			OPTM_CS_E_RGB, OPTM_CS_E_RGB, false, true
		}
	},
	{
		RK_PQ_CSC_RGBL2RGBL, "RGB L->RGB L",
		&rk_csc_table_identity_rgb_to_rgb,
		&rk_dc_csc_table_identity_rgb_to_rgb1,
		{
			OPTM_CS_E_RGB, OPTM_CS_E_RGB, false, false
		}
	},
	{
		RK_PQ_CSC_RGB2RGB, "RGB F->RGB F",
		&rk_csc_table_identity_rgb_to_rgb,
		&rk_dc_csc_table_identity_rgb_to_rgb2,
		{
			OPTM_CS_E_RGB, OPTM_CS_E_RGB, true, true
		}
	},
	{
		RK_PQ_CSC_YUV2RGB_2020, "YUV2020 F->RGB2020 F",
		&rk_csc_table_identity_yuv_to_rgb_2020,
		&rk_dc_csc_table_identity_yuv_to_rgb_2020,
		{
			OPTM_CS_E_XV_YCC_2020, OPTM_CS_E_RGB_2020, true, true
		}
	},
	{
		RK_PQ_CSC_RGB2YUV2020_LIMIT2FULL, "RGB2020 L->YUV2020 F",
		&rk_csc_table_identity_rgb_limit_to_yuv_full_2020,
		&rk_dc_csc_table_identity_rgb_limit_to_yuv_full_2020,
		{
			OPTM_CS_E_RGB_2020, OPTM_CS_E_XV_YCC_2020, false, true
		}
	},
	{
		RK_PQ_CSC_RGB2YUV2020_LIMIT, "RGB2020 L->YUV2020 L",
		&rk_csc_table_identity_rgb_limit_to_yuv_limit_2020,
		&rk_dc_csc_table_identity_rgb_limit_to_yuv_limit_2020,
		{
			OPTM_CS_E_RGB_2020, OPTM_CS_E_XV_YCC_2020, false, false
		}
	},
	{
		RK_PQ_CSC_RGB2YUV2020_FULL2LIMIT, "RGB2020 F->YUV2020 L",
		&rk_csc_table_identity_rgb_full_to_yuv_limit_2020,
		&rk_dc_csc_table_identity_rgb_full_to_yuv_limit_2020,
		{
			OPTM_CS_E_RGB_2020, OPTM_CS_E_XV_YCC_2020, true, false
		}
	},
	{
		RK_PQ_CSC_RGB2YUV2020_FULL, "RGB2020 F->YUV2020 F",
		&rk_csc_table_identity_rgb_full_to_yuv_full_2020,
		&rk_dc_csc_table_identity_rgb_full_to_yuv_full_2020,
		{
			OPTM_CS_E_RGB_2020, OPTM_CS_E_XV_YCC_2020, true, true
		}
	},
	{
		RK_PQ_CSC_YUV2YUV, "YUV 601 L->YUV 601 L",
		&rk_csc_table_identity_y_cb_cr_to_y_cb_cr,
		&rk_dc_csc_table_xv_yccsdy_cb_cr_to_hdy_cb_cr,
		{
			OPTM_CS_E_XV_YCC_601, OPTM_CS_E_XV_YCC_601, false, false
		}
	},
	{
		RK_PQ_CSC_YUV2YUV_FULL, "YUV 601 F->YUV 601 F",
		&rk_csc_table_identity_y_cb_cr_to_y_cb_cr,
		&rk_dc_csc_table_hdy_cb_cr_full_to_xv_yccsdy_cb_cr_full,
		{
			OPTM_CS_E_XV_YCC_601, OPTM_CS_E_XV_YCC_601, true, true
		}
	},
	{
		RK_PQ_CSC_YUV2YUV_LIMIT2FULL, "YUV 601 L->YUV 601 F",
		&rk_csc_table_identity_y_cb_cr_limit_to_y_cb_cr_full,
		&rk_dc_csc_table_identity_y_cb_cr_limit_to_y_cb_cr_full,
		{
			OPTM_CS_E_XV_YCC_601, OPTM_CS_E_XV_YCC_601,  false, true
		}
	},
	{
		RK_PQ_CSC_YUV2YUV_FULL2LIMIT, "YUV 601 F->YUV 601 L",
		&rk_csc_table_identity_y_cb_cr_full_to_y_cb_cr_limit,
		&rk_dc_csc_table_identity_y_cb_cr_full_to_y_cb_cr_limit,
		{
			OPTM_CS_E_XV_YCC_601, OPTM_CS_E_XV_YCC_601, true, false
		}
	},
	{
		RK_PQ_CSC_YUV2YUV, "YUV 2020 L->YUV 2020 L",
		&rk_csc_table_identity_y_cb_cr_to_y_cb_cr,
		&rk_dc_csc_table_xv_yccsdy_cb_cr_to_hdy_cb_cr,
		{
			OPTM_CS_E_XV_YCC_2020, OPTM_CS_E_XV_YCC_2020, false, false
		}
	},
	{
		RK_PQ_CSC_YUV2YUV_FULL, "YUV 2020 F->YUV 2020 F",
		&rk_csc_table_identity_y_cb_cr_to_y_cb_cr,
		&rk_dc_csc_table_hdy_cb_cr_full_to_xv_yccsdy_cb_cr_full,
		{
			OPTM_CS_E_XV_YCC_2020, OPTM_CS_E_XV_YCC_2020, true, true
		}
	},
	{
		RK_PQ_CSC_YUV2YUV_LIMIT2FULL, "YUV 2020 L->YUV 2020 F",
		&rk_csc_table_identity_y_cb_cr_limit_to_y_cb_cr_full,
		&rk_dc_csc_table_identity_y_cb_cr_limit_to_y_cb_cr_full,
		{
			OPTM_CS_E_XV_YCC_2020, OPTM_CS_E_XV_YCC_2020, false, true
		}
	},
	{
		RK_PQ_CSC_YUV2YUV_FULL2LIMIT, "YUV 2020 F->YUV 2020 L",
		&rk_csc_table_identity_y_cb_cr_full_to_y_cb_cr_limit,
		&rk_dc_csc_table_identity_y_cb_cr_full_to_y_cb_cr_limit,
		{
			OPTM_CS_E_XV_YCC_2020, OPTM_CS_E_XV_YCC_2020, true, false
		}
	},
	{
		RK_PQ_CSC_RGB2RGBL, "RGB 2020 F->RGB 2020 L",
		&rk_csc_table_identity_rgb_to_rgb_limit,
		&rk_dc_csc_table_identity_rgb_to_rgb_limit,
		{
			OPTM_CS_E_RGB_2020, OPTM_CS_E_RGB_2020, true, false
		}
	},
	{
		RK_PQ_CSC_RGBL2RGB, "RGB 2020 L->RGB 2020 F",
		&rk_csc_table_identity_rgb_limit_to_rgb,
		&rk_dc_csc_table_identity_rgb_limit_to_rgb,
		{
			OPTM_CS_E_RGB_2020, OPTM_CS_E_RGB_2020, false, true
		}
	},
	{
		RK_PQ_CSC_RGBL2RGBL, "RGB 2020 L->RGB 2020 L",
		&rk_csc_table_identity_rgb_to_rgb,
		&rk_dc_csc_table_identity_rgb_to_rgb1,
		{
			OPTM_CS_E_RGB_2020, OPTM_CS_E_RGB_2020, false, false
		}
	},
	{
		RK_PQ_CSC_RGB2RGB, "RGB 2020 F->RGB 2020 F",
		&rk_csc_table_identity_rgb_to_rgb,
		&rk_dc_csc_table_identity_rgb_to_rgb2,
		{
			OPTM_CS_E_RGB_2020, OPTM_CS_E_RGB_2020, true, true
		}
	},
	{
		RK_PQ_CSC_YUVL2RGBL_2020, "YUV 2020 L->RGB 2020 L",
		&rk_csc_table_y2r_l2l_2020,
		&rk_dc_csc_table_xv_yccsdy_cb_cr_limit_to_rgb_limit,
		{
			OPTM_CS_E_XV_YCC_2020, OPTM_CS_E_RGB_2020, false, false
		}
	},
	{
		RK_PQ_CSC_YUVL2RGBF_2020, "YUV 2020 L->RGB 2020 F",
		&rk_csc_table_y2r_l2f_2020,
		&rk_dc_csc_table_hdy_cb_cr_limit_to_rgb_full,
		{
			OPTM_CS_E_XV_YCC_2020, OPTM_CS_E_RGB_2020, false, true
		}
	},
	{
		RK_PQ_CSC_YUVF2RGBL_2020, "YUV 2020 F->RGB 2020 L",
		&rk_csc_table_y2r_f2l_2020,
		&rk_dc_csc_table_xv_yccsdy_cb_cr_to_rgb_limit,
		{
			OPTM_CS_E_XV_YCC_2020, OPTM_CS_E_RGB_2020, true, false
		}
	},
};

static const struct rk_pq_csc_coef r2y_for_y2y = {
	306, 601, 117,
	-173, -339, 512,
	512, -429, -83,
}; // same to 'RGBF->YUV601F' (10bit)

static const struct rk_pq_csc_coef y2r_for_y2y = {
	1024, -1, 1436,
	1024, -353, -731,
	1024, 1814, 1,
}; // a little bit different to 'YUV601F->RGBF'

static const struct rk_pq_csc_coef r2y_for_r2r = {
	218, 732, 74,
	-117, -395, 512,
	512, -465, -47,
}; // same to 'RGBF->YUV709F' (10bit)

static const struct rk_pq_csc_coef y2r_for_r2r = {
	1024, 0, 1612,
	1024, -192, -480,
	1024, 1900, -2,
}; // a little bit different to 'YUV709F->RGBF'

static const struct rk_pq_csc_coef rgb_input_swap_matrix = {
	0, 0, 1,
	1, 0, 0,
	0, 1, 0,
};

static const struct rk_pq_csc_coef yuv_output_swap_matrix = {
	0, 0, 1,
	1, 0, 0,
	0, 1, 0,
};

static
enum color_space_type get_color_space_type(enum drm_color_encoding color_encoding, bool is_yuv)
{
	enum color_space_type color_space_type;

	switch (color_encoding) {
	case DRM_COLOR_YCBCR_BT601:
		if (is_yuv)
			color_space_type = OPTM_CS_E_XV_YCC_601;
		else
			color_space_type = OPTM_CS_E_RGB;
		break;
	case DRM_COLOR_YCBCR_BT709:
		if (is_yuv)
			color_space_type = OPTM_CS_E_XV_YCC_709;
		else
			color_space_type = OPTM_CS_E_RGB;
		break;
	case DRM_COLOR_YCBCR_BT2020:
		if (is_yuv)
			color_space_type = OPTM_CS_E_XV_YCC_2020;
		else
			color_space_type = OPTM_CS_E_RGB_2020;
		break;
	default:
		if (is_yuv)
			color_space_type = OPTM_CS_E_XV_YCC_601;
		else
			color_space_type = OPTM_CS_E_RGB_2020;
	}

	return color_space_type;
}

/* static */ int csc_get_mode_index(struct post_csc_convert_mode *convert_mode)
{
	const struct rk_csc_colorspace_info *colorspace_info;
	int i, j;
	enum color_space_type input_color_space, output_color_space;
	bool is_input_full_range = convert_mode->is_input_full_range;
	bool is_output_full_range = convert_mode->is_output_full_range;
	bool is_input_yuv = convert_mode->is_input_yuv;
	bool is_output_yuv = convert_mode->is_output_yuv;

	for (i = 0; i < 2; i++) {
		input_color_space = get_color_space_type(convert_mode->intput_color_encoding,
							 is_input_yuv);
		output_color_space = get_color_space_type(convert_mode->output_color_encoding,
							  is_output_yuv);

		for (j = 0; j < ARRAY_SIZE(g_mode_csc_coef); j++) {
			colorspace_info = &g_mode_csc_coef[j].st_csc_color_info;
			if (colorspace_info->input_color_space == input_color_space &&
			    colorspace_info->output_color_space == output_color_space &&
			    colorspace_info->in_full_range == is_input_full_range &&
			    colorspace_info->out_full_range == is_output_full_range)
				return j;
		}

		/*
		 * If no csc matrix can be found for current input/output
		 * colorspace of post-csc, then csc matrix is found based
		 * on colorspace of post-csc output.
		 */
		convert_mode->intput_color_encoding = convert_mode->output_color_encoding;
	}

	return -EINVAL;
}

static void csc_matrix_multiply(struct rk_pq_csc_coef *dst, const struct rk_pq_csc_coef *m0,
				const struct rk_pq_csc_coef *m1)
{
	dst->csc_coef00 = m0->csc_coef00 * m1->csc_coef00 +
			  m0->csc_coef01 * m1->csc_coef10 +
			  m0->csc_coef02 * m1->csc_coef20;

	dst->csc_coef01 = m0->csc_coef00 * m1->csc_coef01 +
			  m0->csc_coef01 * m1->csc_coef11 +
			  m0->csc_coef02 * m1->csc_coef21;

	dst->csc_coef02 = m0->csc_coef00 * m1->csc_coef02 +
			  m0->csc_coef01 * m1->csc_coef12 +
			  m0->csc_coef02 * m1->csc_coef22;

	dst->csc_coef10 = m0->csc_coef10 * m1->csc_coef00 +
			  m0->csc_coef11 * m1->csc_coef10 +
			  m0->csc_coef12 * m1->csc_coef20;

	dst->csc_coef11 = m0->csc_coef10 * m1->csc_coef01 +
			  m0->csc_coef11 * m1->csc_coef11 +
			  m0->csc_coef12 * m1->csc_coef21;

	dst->csc_coef12 = m0->csc_coef10 * m1->csc_coef02 +
			  m0->csc_coef11 * m1->csc_coef12 +
			  m0->csc_coef12 * m1->csc_coef22;

	dst->csc_coef20 = m0->csc_coef20 * m1->csc_coef00 +
			  m0->csc_coef21 * m1->csc_coef10 +
			  m0->csc_coef22 * m1->csc_coef20;

	dst->csc_coef21 = m0->csc_coef20 * m1->csc_coef01 +
			  m0->csc_coef21 * m1->csc_coef11 +
			  m0->csc_coef22 * m1->csc_coef21;

	dst->csc_coef22 = m0->csc_coef20 * m1->csc_coef02 +
			  m0->csc_coef21 * m1->csc_coef12 +
			  m0->csc_coef22 * m1->csc_coef22;
}

static void csc_matrix_ventor_multiply(struct rk_pq_csc_ventor *dst,
				       const struct rk_pq_csc_coef *m0,
				       const struct rk_pq_csc_ventor *v0)
{
	dst->csc_offset0 = m0->csc_coef00 * v0->csc_offset0 +
			   m0->csc_coef01 * v0->csc_offset1 +
			   m0->csc_coef02 * v0->csc_offset2;

	dst->csc_offset1 = m0->csc_coef10 * v0->csc_offset0 +
			   m0->csc_coef11 * v0->csc_offset1 +
			   m0->csc_coef12 * v0->csc_offset2;

	dst->csc_offset2 = m0->csc_coef20 * v0->csc_offset0 +
			   m0->csc_coef21 * v0->csc_offset1 +
			   m0->csc_coef22 * v0->csc_offset2;
}

static void csc_matrix_element_right_shift(struct rk_pq_csc_coef *m, int n)
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

static inline s32 csc_simple_round(s32 x, s32 n)
{
	s32 value = 0;

	if (n == 0)
		return x;

	value = (abs(x) + (1 << (n - 1))) >> (n);
	return (((x) >= 0) ? value : -value);
}

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
	sin_hue = g_hue_sin_table[hue_idx]; // note: the angle is reversed!
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

static int csc_calc_adjust_output_coef(const struct post_csc_convert_mode *mode,
						const struct post_csc *csc_input_cfg,
						const struct rk_csc_mode_coef *csc_mode_cfg,
						struct rk_pq_csc_coef *out_matrix,
						struct rk_pq_csc_ventor *out_dc)
{
	struct rk_pq_csc_coef gain_matrix;
	struct rk_pq_csc_coef contrast_matrix;
	struct rk_pq_csc_coef hue_matrix;
	struct rk_pq_csc_coef saturation_matrix;
	struct rk_pq_csc_coef temp0, temp1;
	const struct rk_pq_csc_coef *r2y_matrix;
	const struct rk_pq_csc_coef *y2r_matrix;
	struct rk_pq_csc_ventor dc_in_ventor;
	struct rk_pq_csc_ventor dc_out_ventor;
	struct rk_pq_csc_ventor v;
	const struct rk_csc_colorspace_info *color_info;
	s32 contrast, saturation, brightness;
	s32 r_gain, g_gain, b_gain;
	s32 r_offset, g_offset, b_offset;
	s32 dc_in_offset, dc_out_offset;
	s32 offset_shift_bits;

	dc_in_ventor.csc_offset0 = csc_mode_cfg->pst_csc_dc_coef->csc_in_dc0; // 10bit
	dc_in_ventor.csc_offset1 = csc_mode_cfg->pst_csc_dc_coef->csc_in_dc1;
	dc_in_ventor.csc_offset2 = csc_mode_cfg->pst_csc_dc_coef->csc_in_dc2;
	dc_out_ventor.csc_offset0 = csc_mode_cfg->pst_csc_dc_coef->csc_out_dc0; // 10bit
	dc_out_ventor.csc_offset1 = csc_mode_cfg->pst_csc_dc_coef->csc_out_dc1;
	dc_out_ventor.csc_offset2 = csc_mode_cfg->pst_csc_dc_coef->csc_out_dc2;

	contrast = csc_input_cfg->contrast * PQ_CSC_PARAM_FIX_NUM / PQ_CSC_IN_PARAM_NORM_COEF;
	saturation = csc_input_cfg->saturation  * PQ_CSC_PARAM_FIX_NUM / PQ_CSC_IN_PARAM_NORM_COEF;
	r_gain = csc_input_cfg->r_gain * PQ_CSC_PARAM_FIX_NUM / PQ_CSC_IN_PARAM_NORM_COEF;
	g_gain = csc_input_cfg->g_gain * PQ_CSC_PARAM_FIX_NUM / PQ_CSC_IN_PARAM_NORM_COEF;
	b_gain = csc_input_cfg->b_gain * PQ_CSC_PARAM_FIX_NUM / PQ_CSC_IN_PARAM_NORM_COEF;
	r_offset = ((s32)csc_input_cfg->r_offset - PQ_CSC_BRIGHTNESS_OFFSET) /
		   PQ_CSC_TEMP_OFFSET_DIV_COEF;
	g_offset = ((s32)csc_input_cfg->g_offset - PQ_CSC_BRIGHTNESS_OFFSET) /
		   PQ_CSC_TEMP_OFFSET_DIV_COEF;
	b_offset = ((s32)csc_input_cfg->b_offset - PQ_CSC_BRIGHTNESS_OFFSET) /
		   PQ_CSC_TEMP_OFFSET_DIV_COEF;
	brightness = (s32)csc_input_cfg->brightness - PQ_CSC_BRIGHTNESS_OFFSET;

	gain_matrix = create_rgb_gain_matrix(r_gain, g_gain, b_gain); // 9bit fixed
	contrast_matrix = create_contrast_matrix(contrast); // 9bit fixed
	hue_matrix = create_hue_matrix(csc_input_cfg->hue); // 10bit fixed
	saturation_matrix = create_saturation_matrix(saturation); // 9bit fixed

	/*
	 * M0 = hue_matrix * saturation_matrix,
	 * M1 = gain_matrix * constrast_matrix,
	 */

	if (mode->is_input_yuv && mode->is_output_yuv) {
		/*
		 * yuv2yuv: output = T * M0 * N_r2y * M1 * N_y2r,
		 * so output = T * hue_matrix * saturation_matrix *
		 * N_r2y * gain_matrix * contrast_matrix * N_y2r
		 */
		r2y_matrix = &r2y_for_y2y;
		y2r_matrix = &y2r_for_y2y;
		csc_matrix_multiply(&temp0, csc_mode_cfg->pst_csc_coef, &hue_matrix);
		/*
		 * The value bits width is 32 bit, so every time 2 matirx multifly,
		 * right shift is necessary to avoid overflow. For enhancing the
		 * calculator precision, PQ_CALC_ENHANCE_BIT bits is reserved and
		 * right shift before get the final result.
		 */
		csc_matrix_element_right_shift(&temp0, PQ_CSC_PARAM_FIX_BIT_WIDTH -
					       PQ_CALC_ENHANCE_BIT);
		csc_matrix_multiply(&temp1, &temp0, &saturation_matrix);
		csc_matrix_element_right_shift(&temp1, PQ_CSC_PARAM_HALF_FIX_BIT_WIDTH);
		csc_matrix_multiply(&temp0, &temp1, r2y_matrix);
		csc_matrix_element_right_shift(&temp0, PQ_CSC_PARAM_FIX_BIT_WIDTH);
		csc_matrix_multiply(&temp1, &temp0, &gain_matrix);
		csc_matrix_element_right_shift(&temp1, PQ_CSC_PARAM_HALF_FIX_BIT_WIDTH);
		csc_matrix_multiply(&temp0, &temp1, &contrast_matrix);
		csc_matrix_element_right_shift(&temp0, PQ_CSC_PARAM_HALF_FIX_BIT_WIDTH);
		csc_matrix_multiply(out_matrix, &temp0, y2r_matrix);
		csc_matrix_element_right_shift_with_simple_round(out_matrix,
			PQ_CSC_PARAM_FIX_BIT_WIDTH + PQ_CALC_ENHANCE_BIT);

		dc_out_ventor.csc_offset0 += brightness;
	} else if (mode->is_input_yuv && !mode->is_output_yuv) {
		/*
		 * yuv2rgb: output = M1 * T * M0,
		 * so output = gain_matrix * contrast_matrix * T *
		 * hue_matrix * saturation_matrix
		 */
		csc_matrix_multiply(&temp0, csc_mode_cfg->pst_csc_coef, &hue_matrix);
		csc_matrix_element_right_shift(&temp0, PQ_CSC_PARAM_FIX_BIT_WIDTH -
					       PQ_CALC_ENHANCE_BIT);
		csc_matrix_multiply(&temp1, &temp0, &saturation_matrix);
		csc_matrix_element_right_shift(&temp1, PQ_CSC_PARAM_HALF_FIX_BIT_WIDTH);
		csc_matrix_multiply(&temp0, &contrast_matrix, &temp1);
		csc_matrix_element_right_shift(&temp0, PQ_CSC_PARAM_HALF_FIX_BIT_WIDTH);
		csc_matrix_multiply(out_matrix, &gain_matrix, &temp0);
		csc_matrix_element_right_shift(out_matrix, PQ_CSC_PARAM_HALF_FIX_BIT_WIDTH +
					       PQ_CALC_ENHANCE_BIT);

		dc_out_ventor.csc_offset0 += brightness + r_offset;
		dc_out_ventor.csc_offset1 += brightness + g_offset;
		dc_out_ventor.csc_offset2 += brightness + b_offset;
	} else if (!mode->is_input_yuv && mode->is_output_yuv) {
		/*
		 * rgb2yuv: output = M0 * T * M1,
		 * so output = hue_matrix * saturation_matrix * T *
		 * gain_matrix * contrast_matrix
		 */
		csc_matrix_multiply(&temp0, csc_mode_cfg->pst_csc_coef, &gain_matrix);
		csc_matrix_element_right_shift(&temp0, PQ_CSC_PARAM_HALF_FIX_BIT_WIDTH -
					       PQ_CALC_ENHANCE_BIT);
		csc_matrix_multiply(&temp1, &temp0, &contrast_matrix);
		csc_matrix_element_right_shift(&temp1, PQ_CSC_PARAM_HALF_FIX_BIT_WIDTH);
		csc_matrix_multiply(&temp0, &saturation_matrix, &temp1);
		csc_matrix_element_right_shift(&temp0, PQ_CSC_PARAM_HALF_FIX_BIT_WIDTH);
		csc_matrix_multiply(out_matrix, &hue_matrix, &temp0);
		csc_matrix_element_right_shift(out_matrix, PQ_CSC_PARAM_FIX_BIT_WIDTH +
					       PQ_CALC_ENHANCE_BIT);

		dc_out_ventor.csc_offset0 += brightness;
	} else {
		/*
		 * rgb2rgb: output = T * M1 * N_y2r * M0 * N_r2y,
		 * so output = T * gain_matrix * contrast_matrix *
		 * N_y2r * hue_matrix * saturation_matrix * N_r2y
		 */
		r2y_matrix = &r2y_for_r2r;
		y2r_matrix = &y2r_for_r2r;
		csc_matrix_multiply(&temp0, csc_mode_cfg->pst_csc_coef, &gain_matrix);
		csc_matrix_element_right_shift(&temp0, PQ_CSC_PARAM_FIX_BIT_WIDTH - PQ_CALC_ENHANCE_BIT);
		csc_matrix_multiply(&temp1, &temp0, &contrast_matrix);
		csc_matrix_element_right_shift(&temp1, PQ_CSC_PARAM_HALF_FIX_BIT_WIDTH);
		csc_matrix_multiply(&temp0, &temp1, y2r_matrix);
		csc_matrix_element_right_shift(&temp0, PQ_CSC_PARAM_FIX_BIT_WIDTH);
		csc_matrix_multiply(&temp1, &temp0, &hue_matrix);
		csc_matrix_element_right_shift(&temp1, PQ_CSC_PARAM_HALF_FIX_BIT_WIDTH);
		csc_matrix_multiply(&temp0, &temp1, &saturation_matrix);
		csc_matrix_element_right_shift(&temp0, PQ_CSC_PARAM_HALF_FIX_BIT_WIDTH);
		csc_matrix_multiply(out_matrix, &temp0, r2y_matrix);
		csc_matrix_element_right_shift_with_simple_round(out_matrix,
			PQ_CSC_PARAM_FIX_BIT_WIDTH + PQ_CALC_ENHANCE_BIT);

		dc_out_ventor.csc_offset0 += brightness + r_offset;
		dc_out_ventor.csc_offset1 += brightness + g_offset;
		dc_out_ventor.csc_offset2 += brightness + b_offset;
	}

	if (mode->pixel_depth < 10) {
		offset_shift_bits = 10 - mode->pixel_depth; // [1, 2]
		dc_in_ventor.csc_offset0 >>= offset_shift_bits;
		dc_in_ventor.csc_offset1 >>= offset_shift_bits;
		dc_in_ventor.csc_offset2 >>= offset_shift_bits;
		dc_out_ventor.csc_offset0 >>= offset_shift_bits;
		dc_out_ventor.csc_offset1 >>= offset_shift_bits;
		dc_out_ventor.csc_offset2 >>= offset_shift_bits;
	}
	else {
		offset_shift_bits = mode->pixel_depth - 10; // [0, 3]
		dc_in_ventor.csc_offset0 <<= offset_shift_bits;
		dc_in_ventor.csc_offset1 <<= offset_shift_bits;
		dc_in_ventor.csc_offset2 <<= offset_shift_bits;
		dc_out_ventor.csc_offset0 <<= offset_shift_bits;
		dc_out_ventor.csc_offset1 <<= offset_shift_bits;
		dc_out_ventor.csc_offset2 <<= offset_shift_bits;
	}

	csc_matrix_ventor_multiply(&v, out_matrix, &dc_in_ventor);
	out_dc->csc_offset0 = v.csc_offset0 + (dc_out_ventor.csc_offset0 << mode->coef_precision);
	out_dc->csc_offset1 = v.csc_offset1 + (dc_out_ventor.csc_offset1 << mode->coef_precision);
	out_dc->csc_offset2 = v.csc_offset2 + (dc_out_ventor.csc_offset2 << mode->coef_precision);

	return 0;
}

static int csc_calc_default_output_coef(const struct post_csc_convert_mode *mode,
					const struct rk_csc_mode_coef *csc_mode_cfg,
					struct rk_pq_csc_coef *out_matrix,
					struct rk_pq_csc_ventor *out_dc)
{
	const struct rk_pq_csc_coef *csc_coef;
	const struct rk_pq_csc_dc_coef *csc_dc_coef;
	struct rk_pq_csc_ventor dc_in_ventor;
	struct rk_pq_csc_ventor dc_out_ventor;
	struct rk_pq_csc_ventor v;
	s32 offset_shift_bits;

	csc_coef = csc_mode_cfg->pst_csc_coef;
	csc_dc_coef = csc_mode_cfg->pst_csc_dc_coef;

	out_matrix->csc_coef00 = csc_coef->csc_coef00;
	out_matrix->csc_coef01 = csc_coef->csc_coef01;
	out_matrix->csc_coef02 = csc_coef->csc_coef02;
	out_matrix->csc_coef10 = csc_coef->csc_coef10;
	out_matrix->csc_coef11 = csc_coef->csc_coef11;
	out_matrix->csc_coef12 = csc_coef->csc_coef12;
	out_matrix->csc_coef20 = csc_coef->csc_coef20;
	out_matrix->csc_coef21 = csc_coef->csc_coef21;
	out_matrix->csc_coef22 = csc_coef->csc_coef22;

	dc_in_ventor.csc_offset0 = csc_dc_coef->csc_in_dc0;
	dc_in_ventor.csc_offset1 = csc_dc_coef->csc_in_dc1;
	dc_in_ventor.csc_offset2 = csc_dc_coef->csc_in_dc2;
	dc_out_ventor.csc_offset0 = csc_dc_coef->csc_out_dc0;
	dc_out_ventor.csc_offset1 = csc_dc_coef->csc_out_dc1;
	dc_out_ventor.csc_offset2 = csc_dc_coef->csc_out_dc2;
	if (mode->pixel_depth < 10) {
		offset_shift_bits = 10 - mode->pixel_depth; // [1, 2]
		dc_in_ventor.csc_offset0 >>= offset_shift_bits;
		dc_in_ventor.csc_offset1 >>= offset_shift_bits;
		dc_in_ventor.csc_offset2 >>= offset_shift_bits;
		dc_out_ventor.csc_offset0 >>= offset_shift_bits;
		dc_out_ventor.csc_offset1 >>= offset_shift_bits;
		dc_out_ventor.csc_offset2 >>= offset_shift_bits;
	}
	else {
		offset_shift_bits = mode->pixel_depth - 10; // [0, 3]
		dc_in_ventor.csc_offset0 <<= offset_shift_bits;
		dc_in_ventor.csc_offset1 <<= offset_shift_bits;
		dc_in_ventor.csc_offset2 <<= offset_shift_bits;
		dc_out_ventor.csc_offset0 <<= offset_shift_bits;
		dc_out_ventor.csc_offset1 <<= offset_shift_bits;
		dc_out_ventor.csc_offset2 <<= offset_shift_bits;
	}

	csc_matrix_ventor_multiply(&v, out_matrix, &dc_in_ventor);
	out_dc->csc_offset0 = v.csc_offset0 + (dc_out_ventor.csc_offset0 << mode->coef_precision);
	out_dc->csc_offset1 = v.csc_offset1 + (dc_out_ventor.csc_offset1 << mode->coef_precision);
	out_dc->csc_offset2 = v.csc_offset2 + (dc_out_ventor.csc_offset2 << mode->coef_precision);

	return 0;
}

static inline s32 pq_csc_simple_round(s32 x, s32 n)
{
	s32 value = 0;

	if (n == 0)
		return x;

	value = (abs(x) + (1 << (n - 1))) >> (n);
	return (((x) >= 0) ? value : -value);
}

static void rockchip_swap_color_channel(const struct post_csc_convert_mode *mode,
					struct post_csc_coef *csc_simple_coef,
					struct rk_pq_csc_coef *out_matrix,
					struct rk_pq_csc_ventor *out_dc)
{
	struct rk_pq_csc_coef tmp_matrix;
	struct rk_pq_csc_ventor tmp_v;

	if (mode->swap_channels == 1 || mode->plat == VOP_VERSION_RK3576) {
		if (!mode->is_input_yuv) {
			memcpy(&tmp_matrix, out_matrix, sizeof(struct rk_pq_csc_coef));
			csc_matrix_multiply(out_matrix, &tmp_matrix, &rgb_input_swap_matrix);
		}

		if (mode->is_output_yuv) {
			memcpy(&tmp_matrix, out_matrix, sizeof(struct rk_pq_csc_coef));
			memcpy(&tmp_v, out_dc, sizeof(struct rk_pq_csc_ventor));
			csc_matrix_multiply(out_matrix, &yuv_output_swap_matrix, &tmp_matrix);
			csc_matrix_ventor_multiply(out_dc, &yuv_output_swap_matrix, &tmp_v);
		}
	}
}

int rockchip_calc_post_csc(struct post_csc *csc_cfg, struct post_csc_coef *csc_simple_coef,
			   struct post_csc_convert_mode *convert_mode)
{
	int ret = 0;
	struct rk_pq_csc_coef out_matrix;
	struct rk_pq_csc_ventor out_dc;
	struct rk_csc_mode_coef csc_mode_cfg;
	const int bit_num = convert_mode->coef_precision;

	/* get csc mode index first */
	ret = csc_get_mode_index(convert_mode);
	if (ret < 0) {
		DRM_ERROR("get csc index err:\n");
		DRM_ERROR("input: colorspace=%d, yuv=%d, full_range=%d; output: colorspace=%d, yuv=%d, full_range=%d\n",
			convert_mode->intput_color_encoding, convert_mode->is_input_yuv, convert_mode->is_input_full_range,
			convert_mode->output_color_encoding, convert_mode->is_output_yuv, convert_mode->is_output_full_range);
		return ret;
	}

	// 10bit pixel depth + 10bit coef precision. default coef precision
	memcpy(&csc_mode_cfg, &g_mode_csc_coef[ret], sizeof(struct rk_csc_mode_coef));

	/* change coefs if target precision is not 10-10 */
	if (convert_mode->pixel_depth == 8 && convert_mode->coef_precision == 8)
		// 8bit pixel depth + 8bit coef precision
		csc_mode_cfg.pst_csc_coef = &g_mode_csc_coefs_8bit_pix_8bit_precision[csc_mode_cfg.csc_mode];
	else if (convert_mode->pixel_depth == 10 && convert_mode->coef_precision == 13)
		// 10bit pixel depth + 13bit coef precision
		csc_mode_cfg.pst_csc_coef = &g_mode_csc_coefs_10bit_pix_13bit_precision[csc_mode_cfg.csc_mode];
	else if (convert_mode->pixel_depth != 10 || convert_mode->coef_precision != 10) {
		DRM_ERROR("Invalid coef precision=%d for %dbit pixel depth!\n", convert_mode->coef_precision, convert_mode->pixel_depth);
		return -1;
	}

	/* adjust out_matric & out_dc if BCSH config is available */
	if (csc_cfg && csc_cfg->csc_enable)
		ret = csc_calc_adjust_output_coef(convert_mode, csc_cfg, &csc_mode_cfg, &out_matrix, &out_dc);
	else
		ret = csc_calc_default_output_coef(convert_mode, &csc_mode_cfg, &out_matrix, &out_dc);

	rockchip_swap_color_channel(convert_mode, csc_simple_coef, &out_matrix, &out_dc);

	// return final coefs & offset
	csc_simple_coef->csc_coef00 = out_matrix.csc_coef00;
	csc_simple_coef->csc_coef01 = out_matrix.csc_coef01;
	csc_simple_coef->csc_coef02 = out_matrix.csc_coef02;
	csc_simple_coef->csc_coef10 = out_matrix.csc_coef10;
	csc_simple_coef->csc_coef11 = out_matrix.csc_coef11;
	csc_simple_coef->csc_coef12 = out_matrix.csc_coef12;
	csc_simple_coef->csc_coef20 = out_matrix.csc_coef20;
	csc_simple_coef->csc_coef21 = out_matrix.csc_coef21;
	csc_simple_coef->csc_coef22 = out_matrix.csc_coef22;
	csc_simple_coef->csc_dc0 = out_dc.csc_offset0;
	csc_simple_coef->csc_dc1 = out_dc.csc_offset1;
	csc_simple_coef->csc_dc2 = out_dc.csc_offset2;
	if (convert_mode->plat == VOP_VERSION_RK3576) {
		csc_simple_coef->csc_dc0 = csc_simple_round(csc_simple_coef->csc_dc0, bit_num);
		csc_simple_coef->csc_dc1 = csc_simple_round(csc_simple_coef->csc_dc1, bit_num);
		csc_simple_coef->csc_dc2 = csc_simple_round(csc_simple_coef->csc_dc2, bit_num);
	}
	csc_simple_coef->range_type = csc_mode_cfg.st_csc_color_info.out_full_range;

	return ret;
}
