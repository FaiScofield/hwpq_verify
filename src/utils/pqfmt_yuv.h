/**
 * @copyright: Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @brief:     YUV format descriptor and related helper functions
 * @author:
 * @create:    2026-04-16
 */

#ifndef _PQFMT_YUV_H_
#define _PQFMT_YUV_H_

#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>

#define PQFMT_YUV444_SAMPLE_RATIO_VER 1
#define PQFMT_YUV444_SAMPLE_RATIO_HOR 1
#define PQFMT_YUV422_SAMPLE_RATIO_VER 1
#define PQFMT_YUV422_SAMPLE_RATIO_HOR 2
#define PQFMT_YUV420_SAMPLE_RATIO_VER 2
#define PQFMT_YUV420_SAMPLE_RATIO_HOR 2
#define PQFMT_YUV440_SAMPLE_RATIO_VER 2
#define PQFMT_YUV440_SAMPLE_RATIO_HOR 1
#define PQFMT_YUV411_SAMPLE_RATIO_VER 1
#define PQFMT_YUV411_SAMPLE_RATIO_HOR 4
#define PQFMT_YUV410_SAMPLE_RATIO_VER 4
#define PQFMT_YUV410_SAMPLE_RATIO_HOR 4
#define PQFMT_YUV400_SAMPLE_RATIO_VER 0
#define PQFMT_YUV400_SAMPLE_RATIO_HOR 0

/**
 * YUV sampling format enumeration
 */
typedef enum pqfmt_yuv_sampling {
    PQFMT_YUV_SAMPLING_444 = 0, // No subsampling
    PQFMT_YUV_SAMPLING_422 = 1, // Chroma vertical/horizontal sample ratio: x1/x2
    PQFMT_YUV_SAMPLING_420 = 2, // Chroma vertical/horizontal sample ratio: x2/x2
    PQFMT_YUV_SAMPLING_440 = 3, // Chroma vertical/horizontal sample ratio: x2/x1
    PQFMT_YUV_SAMPLING_411 = 4, // Chroma vertical/horizontal sample ratio: x1/x4
    PQFMT_YUV_SAMPLING_410 = 5, // Chroma vertical/horizontal sample ratio: x4/x4
    PQFMT_YUV_SAMPLING_400 = 6, // Luma only
} pqfmt_yuv_sampling_e;

/**
 * YUV plane layout enumeration
 */
typedef enum pqfmt_yuv_layout {
    PQFMT_YUV_LAYOUT_Interleaved,
    PQFMT_YUV_LAYOUT_Planar,
    PQFMT_YUV_LAYOUT_SimiPlanar,
} pqfmt_yuv_layout_e;

/**
 * UV/VU order enumeration
 */
typedef enum pqfmt_uv_order {
    PQFMT_ORDER_YUV,
    PQFMT_ORDER_YVU,
    PQFMT_ORDER_YUYV,
    PQFMT_ORDER_YVYU,
    PQFMT_ORDER_UYVY,
    PQFMT_ORDER_VYUY,
} pqfmt_uv_order_e;


/**
 * Tile size enumeration
 */
typedef enum pqfmt_tile_size {
    PQFMT_RASTER,
    PQFMT_TILE_4X4,
} pqfmt_tile_size_e;


/**
 * YUV format description structure
 */
typedef struct pqfmt_yuv_desc {
    pqfmt_yuv_sampling_e sampling;
    uint8_t uv_sample_ratio_ver;
    uint8_t uv_sample_ratio_hor;

    pqfmt_yuv_layout_e layout;
    pqfmt_uv_order_e order;

    // tile info
    bool is_tile;
    int tile_wid;
    int tile_hgt;
    int tile_bytes;
    int tile_offset_uv;

    bool is_line_variant;
} pqfmt_yuv_desc_s;

/**
 * YUV predefined format descriptors
 */
extern const pqfmt_yuv_desc_s g_yuv_desc_yuv444i_vu24;
extern const pqfmt_yuv_desc_s g_yuv_desc_yuv444i_vu30;
extern const pqfmt_yuv_desc_s g_yuv_desc_yuv444i_xv30;
extern const pqfmt_yuv_desc_s g_yuv_desc_yuv444p_yu24;
extern const pqfmt_yuv_desc_s g_yuv_desc_yuv444p_yv24;
extern const pqfmt_yuv_desc_s g_yuv_desc_yuv444sp_nv24;
extern const pqfmt_yuv_desc_s g_yuv_desc_yuv444sp_nv42;
extern const pqfmt_yuv_desc_s g_yuv_desc_yuv444sp_nv30;

extern const pqfmt_yuv_desc_s g_yuv_desc_yuv422i_yuyv;
extern const pqfmt_yuv_desc_s g_yuv_desc_yuv422i_yvyu;
extern const pqfmt_yuv_desc_s g_yuv_desc_yuv422i_uyvy;
extern const pqfmt_yuv_desc_s g_yuv_desc_yuv422i_vyuy;
extern const pqfmt_yuv_desc_s g_yuv_desc_yuv422i_y210;
extern const pqfmt_yuv_desc_s g_yuv_desc_yuv422i_y212;
extern const pqfmt_yuv_desc_s g_yuv_desc_yuv422i_y216;
extern const pqfmt_yuv_desc_s g_yuv_desc_yuv422p_yu16;
extern const pqfmt_yuv_desc_s g_yuv_desc_yuv422p_yv16;
extern const pqfmt_yuv_desc_s g_yuv_desc_yuv422sp_nv16;
extern const pqfmt_yuv_desc_s g_yuv_desc_yuv422sp_nv61;
extern const pqfmt_yuv_desc_s g_yuv_desc_yuv422sp_nv20;

extern const pqfmt_yuv_desc_s g_yuv_desc_yuv420p_yu12;
extern const pqfmt_yuv_desc_s g_yuv_desc_yuv420p_yv12;
extern const pqfmt_yuv_desc_s g_yuv_desc_yuv420sp_nv12;
extern const pqfmt_yuv_desc_s g_yuv_desc_yuv420sp_nv21;
extern const pqfmt_yuv_desc_s g_yuv_desc_yuv420sp_nv15;

extern const pqfmt_yuv_desc_s g_yuv_desc_yuv410p_yuv9;
extern const pqfmt_yuv_desc_s g_yuv_desc_yuv410p_yvu9;
extern const pqfmt_yuv_desc_s g_yuv_desc_yuv411p_yu11;
extern const pqfmt_yuv_desc_s g_yuv_desc_yuv411p_yv11;

extern const pqfmt_yuv_desc_s g_yuv_desc_yuv400_r1;
extern const pqfmt_yuv_desc_s g_yuv_desc_yuv400_r2;
extern const pqfmt_yuv_desc_s g_yuv_desc_yuv400_r4;
extern const pqfmt_yuv_desc_s g_yuv_desc_yuv400_r8;
extern const pqfmt_yuv_desc_s g_yuv_desc_yuv400_r10;
extern const pqfmt_yuv_desc_s g_yuv_desc_yuv400_r12;
extern const pqfmt_yuv_desc_s g_yuv_desc_yuv400_r16;

extern const pqfmt_yuv_desc_s g_yuv_desc_yuv444sp_tile4x4;
extern const pqfmt_yuv_desc_s g_yuv_desc_yuv422sp_tile4x4;
extern const pqfmt_yuv_desc_s g_yuv_desc_yuv420sp_tile4x4;



#ifdef __cplusplus
extern "C" {
#endif

/**
 * YUV format name strings */
extern const char *pqfmt_yuv_sampling_name(pqfmt_yuv_sampling_e sampling);
extern const char *pqfmt_yuv_layout_name(pqfmt_yuv_layout_e layout);
extern const char *pqfmt_uv_order_name(pqfmt_uv_order_e order);
extern const char *pqfmt_tile_size_name(pqfmt_tile_size_e size);

/**
 * YUV format descriptor initialization function
 */
extern void pqfmt_yuv_desc_init(pqfmt_yuv_desc_s *desc, pqfmt_yuv_sampling_e sampling, pqfmt_yuv_layout_e layout,
    pqfmt_uv_order_e uv_order, pqfmt_tile_size_e tile_size, bool is_line_variant);

/**
 * YUV format information query functions
 */
extern bool pqfmt_yuv_desc_is_valid(const pqfmt_yuv_desc_s *desc);
extern bool pqfmt_yuv_desc_is_uv_order(const pqfmt_yuv_desc_s *desc);
extern bool pqfmt_yuv_desc_is_tile(const pqfmt_yuv_desc_s *desc);
extern bool pqfmt_yuv_desc_is_line_variant(const pqfmt_yuv_desc_s *desc);

extern int pqfmt_yuv_desc_get_plane_count(const pqfmt_yuv_desc_s *desc);
extern int pqfmt_yuv_desc_get_tile_size(const pqfmt_yuv_desc_s *desc, int *tile_w, int *tile_h);
extern int pqfmt_yuv_desc_get_chroma_subsampling(const pqfmt_yuv_desc_s *desc, int *h_sub, int *v_sub);

/**
 * YUV format calculation helper functions
 */
extern uint8_t pqfmt_yuv_desc_calc_bpp(const pqfmt_yuv_desc_s *desc);
extern float pqfmt_yuv_desc_calc_pitch_ratio(const pqfmt_yuv_desc_s *desc);
extern float pqfmt_yuv_desc_calc_framesize_ratio(const pqfmt_yuv_desc_s *desc);
extern uint8_t pqfmt_yuv_desc_calc_tile_bytes(const pqfmt_yuv_desc_s *desc);

extern size_t pqfmt_yuv_desc_calc_framesize(const pqfmt_yuv_desc_s *desc, int w, int h, int stride);
extern size_t pqfmt_yuv_desc_calc_planesize(const pqfmt_yuv_desc_s *desc, int plane_idx, int w, int h, int stride);

/**
 * YUV format comparison function
 */
extern bool pqfmt_yuv_desc_equal(const pqfmt_yuv_desc_s *desc1, const pqfmt_yuv_desc_s *desc2);

/**
 * YUV format information print function (for debugging)
 */
extern void pqfmt_yuv_desc_print(const pqfmt_yuv_desc_s *desc);

#ifdef __cplusplus
}
#endif

#endif /* _PQFMT_YUV_H_ */
