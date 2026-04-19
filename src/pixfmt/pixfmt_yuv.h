/**
 * @copyright: Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @brief:     YUV format descriptor and related helper functions
 * @author:    vance.wu@rock-chips.com
 * @create:    2026-04-16
 */

#ifndef _PIXFMT_YUV_H_
#define _PIXFMT_YUV_H_

#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>

#define PIXFMT_YUV444_SAMPLE_RATIO_VER 1
#define PIXFMT_YUV444_SAMPLE_RATIO_HOR 1
#define PIXFMT_YUV422_SAMPLE_RATIO_VER 1
#define PIXFMT_YUV422_SAMPLE_RATIO_HOR 2
#define PIXFMT_YUV420_SAMPLE_RATIO_VER 2
#define PIXFMT_YUV420_SAMPLE_RATIO_HOR 2
#define PIXFMT_YUV440_SAMPLE_RATIO_VER 2
#define PIXFMT_YUV440_SAMPLE_RATIO_HOR 1
#define PIXFMT_YUV411_SAMPLE_RATIO_VER 1
#define PIXFMT_YUV411_SAMPLE_RATIO_HOR 4
#define PIXFMT_YUV410_SAMPLE_RATIO_VER 4
#define PIXFMT_YUV410_SAMPLE_RATIO_HOR 4
#define PIXFMT_YUV400_SAMPLE_RATIO_VER 0
#define PIXFMT_YUV400_SAMPLE_RATIO_HOR 0

/**
 * YUV sampling format enumeration
 */
typedef enum pixfmt_yuv_sampling {
    PIXFMT_YUV_SAMPLING_444 = 0, // No subsampling
    PIXFMT_YUV_SAMPLING_422 = 1, // Chroma vertical/horizontal sample ratio: x1/x2
    PIXFMT_YUV_SAMPLING_420 = 2, // Chroma vertical/horizontal sample ratio: x2/x2
    PIXFMT_YUV_SAMPLING_440 = 3, // Chroma vertical/horizontal sample ratio: x2/x1
    PIXFMT_YUV_SAMPLING_411 = 4, // Chroma vertical/horizontal sample ratio: x1/x4
    PIXFMT_YUV_SAMPLING_410 = 5, // Chroma vertical/horizontal sample ratio: x4/x4
    PIXFMT_YUV_SAMPLING_400 = 6, // Luma only
} pixfmt_yuv_sampling_e;

/**
 * UV/VU order enumeration
 */
typedef enum pixfmt_uv_order {
    PIXFMT_ORDER_YUV,
    PIXFMT_ORDER_YVU,
    PIXFMT_ORDER_YUYV,
    PIXFMT_ORDER_YVYU,
    PIXFMT_ORDER_UYVY,
    PIXFMT_ORDER_VYUY,
} pixfmt_uv_order_e;


/**
 * YUV format description structure
 */
typedef struct pixfmt_yuv_desc {
    pixfmt_yuv_sampling_e sampling;
    uint8_t uv_sample_ratio_ver;
    uint8_t uv_sample_ratio_hor;

    pixfmt_uv_order_e order;

    // tile info
    bool is_tile;
    int tile_wid;
    int tile_hgt;
    int tile_bytes;
    int tile_offset_uv;

    bool is_line_variant;
} pixfmt_yuv_desc_s;

/**
 * YUV predefined format descriptors
 */
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv444i_vu24;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv444i_vu30;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv444i_xv30;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv444i_10lsb;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv444p_yu24;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv444p_yv24;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv444p_10lsb;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv444sp_nv24;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv444sp_nv42;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv444sp_nv30;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv444sp_10lsb;

extern const pixfmt_yuv_desc_s g_yuv_desc_yuv422i_yuyv;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv422i_yvyu;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv422i_uyvy;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv422i_vyuy;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv422i_y210;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv422i_y212;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv422i_y216;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv422p_yu16;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv422p_yv16;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv422p_10lsb;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv422sp_nv16;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv422sp_nv61;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv422sp_nv20;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv422sp_10lsb;

extern const pixfmt_yuv_desc_s g_yuv_desc_yuv420p_yu12;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv420p_yv12;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv420p_10lsb;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv420sp_nv12;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv420sp_nv21;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv420sp_nv15;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv420sp_10lsb;

extern const pixfmt_yuv_desc_s g_yuv_desc_yuv410p_yuv9;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv410p_yvu9;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv411p_yu11;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv411p_yv11;

extern const pixfmt_yuv_desc_s g_yuv_desc_yuv400_r1;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv400_r2;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv400_r4;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv400_r8;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv400_r10;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv400_r12;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv400_r16;

extern const pixfmt_yuv_desc_s g_yuv_desc_yuv444sp_tile4x4;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv422sp_tile4x4;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv420sp_tile4x4;

/* forward declaration */
typedef struct pixfmt_attr pixfmt_attr_s;

#ifdef __cplusplus
extern "C" {
#endif

/**
 * YUV format name strings */
extern const char *pixfmt_yuv_sampling_name(pixfmt_yuv_sampling_e sampling);
extern const char *pixfmt_uv_order_name(pixfmt_uv_order_e order);

/**
 * YUV format information query functions
 */
extern bool pixfmt_yuv_desc_is_valid(const pixfmt_yuv_desc_s *desc);
extern bool pixfmt_yuv_desc_is_uv_order(const pixfmt_yuv_desc_s *desc);
extern bool pixfmt_yuv_desc_is_tile(const pixfmt_yuv_desc_s *desc);
extern bool pixfmt_yuv_desc_is_line_variant(const pixfmt_yuv_desc_s *desc);

extern int pixfmt_yuv_desc_get_tile_size(const pixfmt_yuv_desc_s *desc, int *tile_w, int *tile_h);
extern int pixfmt_yuv_desc_get_chroma_subsampling(const pixfmt_yuv_desc_s *desc, int *h_sub, int *v_sub);

/**
 * YUV format calculation helper functions
 */
extern int pixfmt_yuv_get_min_align_width(const pixfmt_attr_s *attr, int wid, int *retAlign);
extern int pixfmt_yuv_get_min_align_height(const pixfmt_attr_s *attr, int hgt, int *retAlign);
extern int pixfmt_yuv_get_min_pitches(const pixfmt_attr_s *attr, int wid, int *retPitchesx3);
extern size_t pixfmt_yuv_get_framesize(const pixfmt_attr_s *attr, int w, int h, int rowpitch, size_t *retPlaneSizesx3);
extern uint8_t pixfmt_yuv_desc_calc_tile_bytes(const pixfmt_yuv_desc_s *desc);

extern size_t pixfmt_yuv_desc_calc_framesize(const pixfmt_yuv_desc_s *desc, int w, int h, int stride);
extern size_t pixfmt_yuv_desc_calc_planesize(const pixfmt_yuv_desc_s *desc, int plane_idx, int w, int h, int stride);

/**
 * YUV format comparison function
 */
extern bool pixfmt_yuv_desc_equal(const pixfmt_yuv_desc_s *desc1, const pixfmt_yuv_desc_s *desc2);

/**
 * YUV format information print function (for debugging)
 */
extern void pixfmt_yuv_desc_print(const pixfmt_yuv_desc_s *desc);

#ifdef __cplusplus
}
#endif

#endif /* _PIXFMT_YUV_H_ */
