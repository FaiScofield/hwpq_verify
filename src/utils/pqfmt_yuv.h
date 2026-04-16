/**
 * @copyright: Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @brief:     YUV 格式描述子及相关辅助函数
 * @author:
 * @create:    2026-04-16
 */

#ifndef _PQFMT_YUV_H_
#define _PQFMT_YUV_H_

#include <stdbool.h>
#include <stdint.h>



/**
 * YUV 采样格式枚举
 */
typedef enum pqfmt_yuv_sampling {
    PQFMT_YUV_SAMPLING_444 = 0, // No subsampling
    PQFMT_YUV_SAMPLING_422 = 1, // Chroma vertical/horizontal sample ratio: x1/x2
    PQFMT_YUV_SAMPLING_420 = 2, // Chroma vertical/horizontal sample ratio: x2/x2
    PQFMT_YUV_SAMPLING_440 = 3, // Chroma vertical/horizontal sample ratio: x2/x1
    PQFMT_YUV_SAMPLING_410 = 4, // Chroma vertical/horizontal sample ratio: x4/x4
    PQFMT_YUV_SAMPLING_411 = 5, // Chroma vertical/horizontal sample ratio: x1/x4
    PQFMT_YUV_SAMPLING_400 = 6, // Luma only
} pqfmt_yuv_sampling_e;

/**
 * YUV 平面布局枚举
 */
typedef enum pqfmt_yuv_layout {
    PQFMT_YUV_LAYOUT_Interleaved = 0,
    PQFMT_YUV_LAYOUT_Planar = 1,
    PQFMT_YUV_LAYOUT_SimiPlanar = 2,
} pqfmt_yuv_layout_e;

/**
 * UV/VU 顺序枚举
 */
typedef enum pqfmt_uv_order {
    PQFMT_UV_ORDER_UV = 0,
    PQFMT_UV_ORDER_VU = 1,
    PQFMT_YUV422I_YUYV = 2,
    PQFMT_YUV422I_YVYU = 3,
    PQFMT_YUV422I_UYVY = 4,
    PQFMT_YUV422I_VYUY = 5,
} pqfmt_uv_order_e;


/**
 * Tile 尺寸枚举
 */
typedef enum pqfmt_tile_size_e {
    PQFMT_RASTER = 0,
    PQFMT_TILE_4X4 = 1,
} pqfmt_tile_size_t;


/**
 * YUV 格式描述子
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
    int tile_hght;
    int tile_bytes;
    int tile_offset_uv;

    bool is_line_variant;
} pqfmt_yuv_desc_s;

/**
 * YUV 预定义格式描述符
 */
extern const pqfmt_yuv_desc_s g_yuv_fmt_yuv444p;
extern const pqfmt_yuv_desc_s g_yuv_fmt_yuv444sp_nv24;
extern const pqfmt_yuv_desc_s g_yuv_fmt_yuv444sp_nv42;
extern const pqfmt_yuv_desc_s g_yuv_fmt_yuv444i;
extern const pqfmt_yuv_desc_s g_yuv_fmt_yuv422p;
extern const pqfmt_yuv_desc_s g_yuv_fmt_yuv422sp_nv16;
extern const pqfmt_yuv_desc_s g_yuv_fmt_yuv422sp_nv61;
extern const pqfmt_yuv_desc_s g_yuv_fmt_yuv422i_yuyv;
extern const pqfmt_yuv_desc_s g_yuv_fmt_yuv422i_yvyu;
extern const pqfmt_yuv_desc_s g_yuv_fmt_yuv422i_uyvy;
extern const pqfmt_yuv_desc_s g_yuv_fmt_yuv422i_vyuy;
extern const pqfmt_yuv_desc_s g_yuv_fmt_yuv420p;
extern const pqfmt_yuv_desc_s g_yuv_fmt_yuv420sp_nv12;
extern const pqfmt_yuv_desc_s g_yuv_fmt_yuv420sp_nv21;
extern const pqfmt_yuv_desc_s g_yuv_fmt_yuv420sp_nv15;
extern const pqfmt_yuv_desc_s g_yuv_fmt_yuv420sp_p010;
extern const pqfmt_yuv_desc_s g_yuv_fmt_yuv422sp_nv20;
extern const pqfmt_yuv_desc_s g_yuv_fmt_yuv422sp_p210;
extern const pqfmt_yuv_desc_s g_yuv_fmt_yuv444sp_nv30;
extern const pqfmt_yuv_desc_s g_yuv_fmt_yuv420sp_tile4x4;
extern const pqfmt_yuv_desc_s g_yuv_fmt_yuv420sp_tile8x8;
extern const pqfmt_yuv_desc_s g_yuv_fmt_yuv422sp_tile4x4;
extern const pqfmt_yuv_desc_s g_yuv_fmt_yuv410p;
extern const pqfmt_yuv_desc_s g_yuv_fmt_yuv440p;


#ifdef __cplusplus
extern "C" {
#endif

/**
 * YUV 格式名称字符串
 */
extern const char *pqfmt_yuv_sampling_name(pqfmt_yuv_sampling_e sampling);
extern const char *pqfmt_yuv_layout_name(pqfmt_yuv_layout_e layout);
extern const char *pqfmt_uv_order_name(pqfmt_uv_order_e order);
extern const char *pqfmt_tile_size_name(pqfmt_tile_size_e size);

/**
 * YUV 格式描述符初始化函数
 */
extern void pqfmt_yuv_desc_init(pqfmt_yuv_desc_s *desc, pqfmt_yuv_sampling_e sampling, pqfmt_yuv_layout_e layout,
    pqfmt_uv_order_e uv_order, pqfmt_tile_size_e tile_size, bool is_line_variant);

/**
 * YUV 格式信息查询函数
 */
extern bool pqfmt_yuv_desc_is_valid(const pqfmt_yuv_desc_s *desc);
inline bool pqfmt_yuv_desc_is_uv_order(const pqfmt_yuv_desc_s *desc);
inline bool pqfmt_yuv_desc_is_tile(const pqfmt_yuv_desc_s *desc);
inline bool pqfmt_yuv_desc_is_line_variant(const pqfmt_yuv_desc_s *desc);

extern int pqfmt_yuv_desc_get_plane_count(const pqfmt_yuv_desc_s *desc);
extern int pqfmt_yuv_desc_get_tile_size(const pqfmt_yuv_desc_s *desc, int *tile_w, int *tile_h);
extern int pqfmt_yuv_desc_get_chroma_subsampling(const pqfmt_yuv_desc_s *desc, int *h_sub, int *v_sub);

/**
 * YUV 格式计算辅助函数
 */
extern uint8_t pqfmt_yuv_desc_calc_bpp(const pqfmt_yuv_desc_s *desc);
extern float pqfmt_yuv_desc_calc_pitch_ratio(const pqfmt_yuv_desc_s *desc);
extern float pqfmt_yuv_desc_calc_framesize_ratio(const pqfmt_yuv_desc_s *desc);
extern uint8_t pqfmt_yuv_desc_calc_tile_bytes(const pqfmt_yuv_desc_s *desc);

extern size_t pqfmt_yuv_desc_calc_framesize(const pqfmt_yuv_desc_s *desc, int w, int h, int stride);
extern size_t pqfmt_yuv_desc_calc_planesize(const pqfmt_yuv_desc_s *desc, int plane_idx, int w, int h, int stride);

/**
 * YUV 格式比较函数
 */
extern bool pqfmt_yuv_desc_equal(const pqfmt_yuv_desc_s *desc1, const pqfmt_yuv_desc_s *desc2);

/**
 * YUV 格式信息打印函数 (调试用)
 */
extern void pqfmt_yuv_desc_print(const pqfmt_yuv_desc_s *desc);

#ifdef __cplusplus
}
#endif

#endif /* _PQFMT_YUV_H_ */
