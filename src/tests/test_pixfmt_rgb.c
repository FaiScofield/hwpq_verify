/**
 * @copyright: Copyright (c) Rockchip Electronics Co., Ltd. 2026-. All rights reserved.
 * @brief:     pixfmt unit test
 * @author:    vance.wu@rock-chips.com
 * @create:    2026-04-22
 */

#include "pixfmt.h"
#include "pixfmt_cvt.h"
#include "verify_com.h"
#include <assert.h>
#include <stdio.h>

#define ARRAY_SIZE(arr) (sizeof(arr) / sizeof((arr)[0]))
#define TEST_PASSED     0
#define TEST_FAILED     -1

static int g_test_passed = 0;
static int g_test_failed = 0;

#define TEST_ASSERT(cond, fmt, ...)                    \
    do {                                               \
        if (cond) {                                    \
            g_test_passed++;                           \
            printf("[PASS] " fmt "\n", ##__VA_ARGS__); \
        }                                              \
        else {                                         \
            g_test_failed++;                           \
            printf("[FAIL] " fmt "\n", ##__VA_ARGS__); \
        }                                              \
    } while (0)



static void test_pixfmt_framesize(void)
{
    printf("\n=== Test: Framesize Calculation ===\n");

    size_t rgb888_size = pixfmt_get_frame_size(PIXFMT_RGB888, 1920, 1080, 0, NULL);
    TEST_ASSERT(rgb888_size == 1920 * 1080 * 3, "RGB888 1920x1080 framesize should be 6,220,800");

    size_t rgba8888_size = pixfmt_get_frame_size(PIXFMT_RGBA8888, 1920, 1080, 0, NULL);
    TEST_ASSERT(rgba8888_size == 1920 * 1080 * 4, "RGBA8888 1920x1080 framesize should be 8,294,400");

    size_t yuv420p_size = pixfmt_get_frame_size(PIXFMT_YUV420P_YU12, 1920, 1080, 0, NULL);
    TEST_ASSERT(yuv420p_size == 1920 * 1080 * 3 / 2, "YUV420P 1920x1080 framesize should be 3,110,400");
}


static void test_pixfmt_vir_wid(void)
{
    printf("\n=== Test: Virtual Width Calculation ===\n");

    int row_pitches[3] = {0};
    pixfmt_get_min_pitches(PIXFMT_RGB888, 1920, row_pitches);
    TEST_ASSERT(row_pitches[0] == 1920 * 3, "RGB888 row pitch should be widthx3");

    pixfmt_get_min_pitches(PIXFMT_RGB565, 1920, row_pitches);
    TEST_ASSERT(row_pitches[0] == 1920 * 2, "RGB565 row pitch should be widthx2");

    pixfmt_get_min_pitches(PIXFMT_RGBA8888, 1920, row_pitches);
    TEST_ASSERT(row_pitches[0] == 1920 * 4, "RGBA8888 row pitch should be widthx4");
}


static void test_pixfmt_rgb_desc(void)
{
    printf("\n=== Test: RGB Descriptor ===\n");

    TEST_ASSERT(pixfmt_rgb_desc_is_valid(&g_rgb_desc_rgb888) == true, "RGB888 desc should be valid");
    TEST_ASSERT(pixfmt_rgb_desc_has_alpha(&g_rgb_desc_rgb888) == false, "RGB888 should not have alpha");
    TEST_ASSERT(pixfmt_rgb_desc_is_bgr_order(&g_rgb_desc_rgb888) == false, "RGB888 should not be BGR order");

    TEST_ASSERT(pixfmt_rgb_desc_is_valid(&g_rgb_desc_rgba8888) == true, "RGBA8888 desc should be valid");
    TEST_ASSERT(pixfmt_rgb_desc_has_alpha(&g_rgb_desc_rgba8888) == true, "RGBA8888 should have alpha");

    uint8_t r, g, b, a;
    pixfmt_rgb_desc_get_channel_bits(&g_rgb_desc_rgb565, &r, &g, &b, &a);
    TEST_ASSERT(r == 5 && g == 6 && b == 5, "RGB565 channel bits should be R=5, G=6, B=5");
    TEST_ASSERT(a == 0, "RGB565 alpha should be 0");
}

static void test_pixfmt_yuv_desc(void)
{
    printf("\n=== Test: YUV Descriptor ===\n");

    TEST_ASSERT(pixfmt_yuv_desc_is_valid(&g_yuv_desc_yuv420_yuv) == true, "YUV420P desc should be valid");
    TEST_ASSERT(pixfmt_yuv_desc_is_tile(&g_yuv_desc_yuv420_yvu) == false, "YUV420P should not be tile format");
    TEST_ASSERT(pixfmt_yuv_desc_is_line_variant(&g_yuv_desc_yuv420_yuv) == false, "YUV420P should not be line variant");

    TEST_ASSERT(pixfmt_yuv_desc_is_tile(&g_yuv_desc_yuv420_tile4x4) == true, "TILE4x4 should be tile format");

    int plane_count = pixfmt_nb_planes(PIXFMT_YUV420P_YU12);
    TEST_ASSERT(plane_count == 3, "YUV420P should have 3 planes");

    plane_count = pixfmt_nb_planes(PIXFMT_YUV420SP_NV12);
    TEST_ASSERT(plane_count == 2, "NV12 should have 2 planes");

    int h_sub = 0, v_sub = 0;
    pixfmt_yuv_desc_get_chroma_subsampling(&g_yuv_desc_yuv420_yuv, &h_sub, &v_sub);
    TEST_ASSERT(h_sub == 2 && v_sub == 2, "YUV420P subsampling should be 2x2");

    pixfmt_yuv_desc_get_chroma_subsampling(&g_yuv_desc_yuv422_yuv, &h_sub, &v_sub);
    TEST_ASSERT(h_sub == 2 && v_sub == 1, "YUV422P subsampling should be 2x1");
}


static void test_pixfmt_rgb_desc_equal(void)
{
    printf("\n=== Test: RGB Descriptor Equal ===\n");

    TEST_ASSERT(pixfmt_rgb_desc_equal(&g_rgb_desc_rgb888, &g_rgb_desc_rgb888) == true,
        "Same descriptor should be equal");
    TEST_ASSERT(pixfmt_rgb_desc_equal(&g_rgb_desc_rgb888, &g_rgb_desc_bgr888) == false,
        "Different descriptors should not be equal");
}

static void test_pixfmt_yuv_desc_equal(void)
{
    printf("\n=== Test: YUV Descriptor Equal ===\n");

    TEST_ASSERT(pixfmt_yuv_desc_equal(&g_yuv_desc_yuv420_yuv, &g_yuv_desc_yuv420_yuv) == true,
        "Same YUV descriptor should be equal");
    TEST_ASSERT(pixfmt_yuv_desc_equal(&g_yuv_desc_yuv420_yuv, &g_yuv_desc_yuv420_yvu) == false,
        "Different YUV descriptors should not be equal");
}
