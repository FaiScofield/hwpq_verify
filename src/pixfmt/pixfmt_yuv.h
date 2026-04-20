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
 * UV/VU order from LSB to MSB
 */
typedef enum pixfmt_uv_order {
    PIXFMT_ORDER_YUV,
    PIXFMT_ORDER_YVU,
    PIXFMT_ORDER_UYV,
    PIXFMT_ORDER_VYU,
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
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv444_yuv;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv444_yvu;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv444_uyv;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv422_yuyv;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv422_yvyu;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv422_uyvy;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv422_vyuy;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv422_yuv;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv422_yvu;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv420_yuv;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv420_yvu;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv410_yuv;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv410_yvu;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv411_yuv;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv411_yvu;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv400;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv444_tile4x4;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv422_tile4x4;
extern const pixfmt_yuv_desc_s g_yuv_desc_yuv420_tile4x4;

/* forward declaration */
struct pixfmt_attr;

#ifdef __cplusplus
extern "C" {
#endif


/** YUV format name strings */
extern const char *pixfmt_yuv_sampling_name(pixfmt_yuv_sampling_e sampling);
extern const char *pixfmt_uv_order_name(pixfmt_uv_order_e order);

/** YUV format information query functions */
extern bool pixfmt_yuv_desc_is_valid(const pixfmt_yuv_desc_s *desc);
extern bool pixfmt_yuv_desc_is_uv_order(const pixfmt_yuv_desc_s *desc);
extern bool pixfmt_yuv_desc_is_tile(const pixfmt_yuv_desc_s *desc);
extern bool pixfmt_yuv_desc_is_line_variant(const pixfmt_yuv_desc_s *desc);

extern int pixfmt_yuv_desc_get_tile_size(const pixfmt_yuv_desc_s *desc, int *tile_w, int *tile_h);
extern int pixfmt_yuv_desc_get_chroma_subsampling(const pixfmt_yuv_desc_s *desc, int *h_sub, int *v_sub);

/** YUV format calculation helper functions */
extern int pixfmt_yuv_get_min_align_width(const struct pixfmt_attr *attr, int wid, int *retAlign);
extern int pixfmt_yuv_get_min_align_height(const struct pixfmt_attr *attr, int hgt, int *retAlign);
extern int pixfmt_yuv_get_min_pitches(const struct pixfmt_attr *attr, int wid, int *retPitchesx3);
extern size_t pixfmt_yuv_get_framesize(const struct pixfmt_attr *attr, int w, int h, int rowpitch, size_t *retPlaneSizesx3);
extern uint8_t pixfmt_yuv_desc_calc_tile_bytes(const pixfmt_yuv_desc_s *desc);

extern size_t pixfmt_yuv_desc_calc_framesize(const pixfmt_yuv_desc_s *desc, int w, int h, int stride);
extern size_t pixfmt_yuv_desc_calc_planesize(const pixfmt_yuv_desc_s *desc, int plane_idx, int w, int h, int stride);

/** YUV format comparison function */
extern bool pixfmt_yuv_desc_equal(const pixfmt_yuv_desc_s *desc1, const pixfmt_yuv_desc_s *desc2);

/** YUV format information print function (for debugging) */
extern void pixfmt_yuv_dump_desc(const pixfmt_yuv_desc_s *desc);

#ifdef __cplusplus
}
#endif

#endif /* _PIXFMT_YUV_H_ */
