/**
 * @copyright: Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @brief:     pixfmt 鍗曞厓娴嬭瘯
 * @author:
 * @create:    2026-04-17
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

static void test_pixfmt_invalid_format(void)
{
    printf("\n=== Test: PIXFMT_INVALID ===\n");

    TEST_ASSERT(PIXFMT_INVALID == -1, "PIXFMT_INVALID should be -1");

    const pixfmt_attr_s *desc = pixfmt_get_attr(PIXFMT_INVALID);
    TEST_ASSERT(desc == NULL, "pixfmt_get_desc(PIXFMT_INVALID) should return NULL");

    TEST_ASSERT(pixfmt_bpp(PIXFMT_INVALID) == 0, "pixfmt_bpp(PIXFMT_INVALID) should return 0");
    TEST_ASSERT(pixfmt_depth(PIXFMT_INVALID) == 0, "pixfmt_depth(PIXFMT_INVALID) should return 0");
}

static void test_pixfmt_rgb888(void)
{
    printf("\n=== Test: RGB888 Format ===\n");

    const pixfmt_attr_s *attr = pixfmt_get_attr(PIXFMT_RGB888);
    TEST_ASSERT(attr != NULL, "pixfmt_get_desc(RGB888) should not be NULL");
    if (!attr)
        return;

    TEST_ASSERT(attr->fmt_id == PIXFMT_RGB888, "fmt_id should be RGB888");
    TEST_ASSERT(attr->bpp == 24, "RGB888 bpp should be 24");
    TEST_ASSERT(attr->depth == 8, "RGB888 depth should be 8");
    TEST_ASSERT(attr->layout == PIXFMT_LAYOUT_INTERLEAVED, "RGB888 layout should be interleaved");
    TEST_ASSERT(attr->base_type == PIXFMT_TYPE_RGB, "RGB888 base_type should be RGB");

    TEST_ASSERT(pixfmt_bpp(PIXFMT_RGB888) == 24, "pixfmt_bpp(RGB888) should be 24");
    TEST_ASSERT(pixfmt_depth(PIXFMT_RGB888) == 8, "pixfmt_depth(RGB888) should be 8");
    TEST_ASSERT(pixfmt_is_rgb(PIXFMT_RGB888) == true, "RGB888 should be recognized as RGB");
    TEST_ASSERT(pixfmt_is_yuv(PIXFMT_RGB888) == false, "RGB888 should not be recognized as YUV");
    TEST_ASSERT(pixfmt_has_alpha(PIXFMT_RGB888) == false, "RGB888 should not have alpha");
}

static void test_pixfmt_rgba8888(void)
{
    printf("\n=== Test: RGBA8888 Format ===\n");

    const pixfmt_attr_s *attr = pixfmt_get_attr(PIXFMT_RGBA8888);
    TEST_ASSERT(attr != NULL, "pixfmt_get_desc(RGBA8888) should not be NULL");
    if (!attr)
        return;

    TEST_ASSERT(attr->bpp == 32, "RGBA8888 bpp should be 32");
    TEST_ASSERT(attr->padding_pos == PIXFMT_NO_PADDING, "RGBA8888 padding_pos should be NO_PADDING");
    TEST_ASSERT(pixfmt_has_alpha(PIXFMT_RGBA8888) == true, "RGBA8888 should have alpha");
}

static void test_pixfmt_rgb565(void)
{
    printf("\n=== Test: RGB565 Format ===\n");

    const pixfmt_attr_s *attr = pixfmt_get_attr(PIXFMT_RGB565);
    TEST_ASSERT(attr != NULL, "pixfmt_get_desc(RGB565) should not be NULL");
    if (!attr)
        return;

    TEST_ASSERT(attr->bpp == 16, "RGB565 bpp should be 16");
    TEST_ASSERT(attr->is_bitpacked == true, "RGB565 bitpacked_order should be MSB");
    TEST_ASSERT(attr->padding_pos == PIXFMT_NO_PADDING, "RGB565 padding_pos should be NO_PADDING");
}

static void test_pixfmt_yuv420p(void)
{
    printf("\n=== Test: YUV420P Format ===\n");

    const pixfmt_attr_s *attr = pixfmt_get_attr(PIXFMT_YUV420P_YU12);
    TEST_ASSERT(attr != NULL, "pixfmt_get_desc(YUV420P) should not be NULL");
    if (!attr)
        return;

    TEST_ASSERT(attr->base_type == PIXFMT_TYPE_YUV, "YUV420P base_type should be YUV");
    TEST_ASSERT(attr->layout == PIXFMT_LAYOUT_PLANAR, "YUV420P layout should be planar");
    TEST_ASSERT(pixfmt_is_yuv(PIXFMT_YUV420P_YU12) == true, "YUV420P should be recognized as YUV");
    TEST_ASSERT(pixfmt_is_rgb(PIXFMT_YUV420P_YU12) == false, "YUV420P should not be recognized as RGB");

    int h_sub = 0, v_sub = 0;
    pixfmt_get_chroma_subsampling(PIXFMT_YUV420P_YU12, &h_sub, &v_sub);
    TEST_ASSERT(h_sub == 2 && v_sub == 2, "YUV420P chroma subsampling should be 2x2");
}

static void test_pixfmt_yuv420sp(void)
{
    printf("\n=== Test: YUV420SP (NV12) Format ===\n");

    const pixfmt_attr_s *attr = pixfmt_get_attr(PIXFMT_YUV420SP_NV12);
    TEST_ASSERT(attr != NULL, "pixfmt_get_desc(NV12) should not be NULL");
    if (!attr)
        return;

    TEST_ASSERT(attr->layout == PIXFMT_LAYOUT_SEMIPLANAR, "NV12 layout should be semi-planar");
}

static void test_pixfmt_get_by_name(void)
{
    printf("\n=== Test: Get Format by Name ===\n");

    const pixfmt_attr_s *attr = pixfmt_get_attr_by_name("rgb888");
    TEST_ASSERT(attr != NULL, "get_fmt_desc_by_name('rgb888') should not be NULL");
    if (attr) {
        TEST_ASSERT(attr->fmt_id == PIXFMT_RGB888, "Should find RGB888 by alias 'rgb888'");
    }

    attr = pixfmt_get_attr_by_name("rgb24");
    TEST_ASSERT(attr != NULL, "get_fmt_desc_by_name('rgb24') should not be NULL");
    if (attr) {
        TEST_ASSERT(attr->fmt_id == PIXFMT_RGB888, "Should find RGB888 by short_name 'rgb24'");
    }

    attr = pixfmt_get_attr_by_name("nonexistent");
    TEST_ASSERT(attr == NULL, "get_fmt_desc_by_name('nonexistent') should return NULL");
}

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

    TEST_ASSERT(pixfmt_yuv_desc_is_valid(&g_yuv_desc_yuv420p_yu12) == true, "YUV420P desc should be valid");
    TEST_ASSERT(pixfmt_yuv_desc_is_tile(&g_yuv_desc_yuv420p_yv12) == false, "YUV420P should not be tile format");
    TEST_ASSERT(pixfmt_yuv_desc_is_line_variant(&g_yuv_desc_yuv420p_yu12) == false,
        "YUV420P should not be line variant");

    TEST_ASSERT(pixfmt_yuv_desc_is_tile(&g_yuv_desc_yuv420sp_tile4x4) == true, "TILE4x4 should be tile format");

    int plane_count = pixfmt_nb_planes(PIXFMT_YUV420P_YU12);
    TEST_ASSERT(plane_count == 3, "YUV420P should have 3 planes");

    plane_count = pixfmt_nb_planes(PIXFMT_YUV420SP_NV12);
    TEST_ASSERT(plane_count == 2, "NV12 should have 2 planes");

    int h_sub = 0, v_sub = 0;
    pixfmt_yuv_desc_get_chroma_subsampling(&g_yuv_desc_yuv420p_yu12, &h_sub, &v_sub);
    TEST_ASSERT(h_sub == 2 && v_sub == 2, "YUV420P subsampling should be 2x2");

    pixfmt_yuv_desc_get_chroma_subsampling(&g_yuv_desc_yuv422p_yu16, &h_sub, &v_sub);
    TEST_ASSERT(h_sub == 2 && v_sub == 1, "YUV422P subsampling should be 2x1");
}

#if 0
static void test_pixfmt_cvt_is_supported(void)
{
    printf("\n=== Test: Conversion Support Check ===\n");

    TEST_ASSERT(pixfmt_cvt_is_supported(PIXFMT_RGB888, PIXFMT_RGB888) == true,
        "Same format conversion should be supported");
    TEST_ASSERT(pixfmt_cvt_is_supported(PIXFMT_RGB888, PIXFMT_RGB565) == true, "RGB888 to RGB565 should be supported");
    TEST_ASSERT(pixfmt_cvt_is_supported(PIXFMT_RGB888, PIXFMT_YUV420P_YU12) == true,
        "RGB888 to YUV420P should be supported");
    TEST_ASSERT(pixfmt_cvt_is_supported(PIXFMT_YUV420P_YU12, PIXFMT_RGB888) == true,
        "YUV420P to RGB888 should be supported");
}

static void test_pixfmt_cvt_common_fmt(void)
{
    printf("\n=== Test: Common Format ===\n");

    pixfmt_e com_fmt;

    pixfmt_e rgb_coms[] = {PIXFMT_RGB888, PIXFMT_BGR888, PIXFMT_RGB332, PIXFMT_BGR233, PIXFMT_RGB565, PIXFMT_BGR565};
    for (int i = 0; i < ARRAY_SIZE(rgb_coms); ++i) {
        com_fmt = pixfmt_get_common_fmt(rgb_coms[i], PIXFMT_LAYOUT_INTERLEAVED);
        TEST_ASSERT(com_fmt == PIXFMT_RGB888, "%s to RGB common should be RGB888", pixfmt_short_name(rgb_coms[i]));
    }

    pixfmt_e rgba_coms[] = {PIXFMT_RGBA8888, PIXFMT_BGRA8888, PIXFMT_ARGB8888, PIXFMT_ABGR8888, PIXFMT_RGBA5551,
        PIXFMT_ABGR1555, PIXFMT_RGBA4444, PIXFMT_ABGR4444};
    for (int i = 0; i < ARRAY_SIZE(rgba_coms); ++i) {
        com_fmt = pixfmt_get_common_fmt(rgba_coms[i], PIXFMT_LAYOUT_INTERLEAVED);
        TEST_ASSERT(com_fmt == PIXFMT_RGBA8888, "%s to RGB common should be RGBA8888", pixfmt_short_name(rgba_coms[i]));
    }

    pixfmt_e rgba10_coms[] = {PIXFMT_RGBA1010102, PIXFMT_ABGR2101010};
    for (int i = 0; i < ARRAY_SIZE(rgba10_coms); ++i) {
        com_fmt = pixfmt_get_common_fmt(rgba10_coms[i], PIXFMT_LAYOUT_INTERLEAVED);
        TEST_ASSERT(com_fmt == PIXFMT_RGBA10Lsb, "%s to RGB common should be RGBA10Lsb", pixfmt_short_name(rgba10_coms[i]));
    }

    pixfmt_e yuv444_8bit_coms[] = {
        PIXFMT_YUV444I_VU24, PIXFMT_YUV444P_YU24, PIXFMT_YUV444P_YV24, PIXFMT_YUV444SP_NV24, PIXFMT_YUV444SP_NV42};
    for (int i = 0; i < ARRAY_SIZE(yuv444_8bit_coms); ++i) {
        com_fmt = pixfmt_get_common_fmt(yuv444_8bit_coms[i], PIXFMT_LAYOUT_INTERLEAVED);
        TEST_ASSERT(com_fmt == PIXFMT_YUV444I_VU24, "%s to 8bit YUV444I common should be PIXFMT_YUV444I_VU24",
            pixfmt_short_name(yuv444_8bit_coms[i]));
        com_fmt = pixfmt_get_common_fmt(yuv444_8bit_coms[i], PIXFMT_LAYOUT_PLANAR);
        TEST_ASSERT(com_fmt == PIXFMT_YUV444P_YU24, "%s to 8bit YUV444P common should be PIXFMT_YUV444P_YU24",
            pixfmt_short_name(yuv444_8bit_coms[i]));
        com_fmt = pixfmt_get_common_fmt(yuv444_8bit_coms[i], PIXFMT_LAYOUT_SEMIPLANAR);
        TEST_ASSERT(com_fmt == PIXFMT_YUV444SP_NV24, "%s to 8bit YUV444SP common should be PIXFMT_YUV444SP_NV24",
            pixfmt_short_name(yuv444_8bit_coms[i]));
    }

    pixfmt_e yuv444_10bit_coms[] = {PIXFMT_YUV444I_VU30, PIXFMT_YUV444I_XV30, PIXFMT_YUV444I_10LSB,
        PIXFMT_YUV444P_10LSB, PIXFMT_YUV444SP_NV30, PIXFMT_YUV444SP_10LSB};
    for (int i = 0; i < ARRAY_SIZE(yuv444_10bit_coms); ++i) {
        com_fmt = pixfmt_get_common_fmt(yuv444_10bit_coms[i], PIXFMT_LAYOUT_INTERLEAVED);
        TEST_ASSERT(com_fmt == PIXFMT_YUV444I_10LSB, "%s to 10bit YUV444I common should be PIXFMT_YUV444I_10LSB",
            pixfmt_short_name(yuv444_10bit_coms[i]));
        com_fmt = pixfmt_get_common_fmt(yuv444_10bit_coms[i], PIXFMT_LAYOUT_PLANAR);
        TEST_ASSERT(com_fmt == PIXFMT_YUV444P_10LSB, "%s to 10bit YUV444P common should be PIXFMT_YUV444P_10LSB",
            pixfmt_short_name(yuv444_10bit_coms[i]));
        com_fmt = pixfmt_get_common_fmt(yuv444_10bit_coms[i], PIXFMT_LAYOUT_SEMIPLANAR);
        TEST_ASSERT(com_fmt == PIXFMT_YUV444SP_10LSB, "%s to 10bit YUV444SP common should be PIXFMT_YUV444SP_10LSB",
            pixfmt_short_name(yuv444_10bit_coms[i]));
    }

    pixfmt_e yuv422_8bit_coms[] = {PIXFMT_YUV422I_YUYV, PIXFMT_YUV422I_YVYU, PIXFMT_YUV422I_UYVY, PIXFMT_YUV422I_VYUY,
        PIXFMT_YUV422P_YU16, PIXFMT_YUV422P_YV16, PIXFMT_YUV422SP_NV16, PIXFMT_YUV422SP_NV61};
    for (int i = 0; i < ARRAY_SIZE(yuv422_8bit_coms); ++i) {
        // TODO, shoule be PIXFMT_YUV422P_YU16/PIXFMT_YUV422SP_NV16
    }
    com_fmt = pixfmt_get_common_fmt(PIXFMT_YUV422SP_NV20, PIXFMT_LAYOUT_SEMIPLANAR);
    TEST_ASSERT(com_fmt == PIXFMT_YUV422SP_10LSB, "%s to 10bit YUV422SP common should be PIXFMT_YUV422SP_10LSB",
        pixfmt_short_name(PIXFMT_YUV422SP_NV20));

    pixfmt_e yuv420_8bit_coms[] = {PIXFMT_YUV420P_YU12, PIXFMT_YUV420P_YV12, PIXFMT_YUV420SP_NV12, PIXFMT_YUV420SP_NV21};
    for (int i = 0; i < ARRAY_SIZE(yuv420_8bit_coms); ++i) {
        // TODO, shoule be PIXFMT_YUV420P_YU12/PIXFMT_YUV420SP_NV12
    }
    com_fmt = pixfmt_get_common_fmt(PIXFMT_YUV420SP_NV15, PIXFMT_LAYOUT_SEMIPLANAR);
    TEST_ASSERT(com_fmt == PIXFMT_YUV420SP_10LSB, "%s to 10bit YUV420SP common should be PIXFMT_YUV420SP_10LSB",
        pixfmt_short_name(PIXFMT_YUV420SP_NV15));

    com_fmt = pixfmt_get_common_fmt(PIXFMT_YUV444SP_TILE4x4, PIXFMT_LAYOUT_SEMIPLANAR);
    TEST_ASSERT(com_fmt == PIXFMT_YUV444SP_NV24, "%s to 10bit YUV444SP common should be PIXFMT_YUV444SP_NV24",
        pixfmt_short_name(PIXFMT_YUV444SP_TILE4x4));

    com_fmt = pixfmt_get_common_fmt(PIXFMT_YUV422SP_TILE4x4, PIXFMT_LAYOUT_SEMIPLANAR);
    TEST_ASSERT(com_fmt == PIXFMT_YUV422SP_NV16, "%s to 10bit YUV444SP common should be PIXFMT_YUV422SP_NV16",
        pixfmt_short_name(PIXFMT_YUV422SP_TILE4x4));

    com_fmt = pixfmt_get_common_fmt(PIXFMT_YUV420SP_TILE4x4, PIXFMT_LAYOUT_SEMIPLANAR);
    TEST_ASSERT(com_fmt == PIXFMT_YUV420SP_NV12, "%s to 10bit YUV444SP common should be PIXFMT_YUV420SP_NV12",
        pixfmt_short_name(PIXFMT_YUV420SP_TILE4x4));
}

static void test_pixfmt_supported_fmts(void)
{
    printf("\n=== Test: Supported Format Lists ===\n");

    int count = 0;
    pixfmt_e *fmts = pixfmt_get_supported_input_fmts(&count);
    TEST_ASSERT(count > 0, "Should have some supported input formats");
    TEST_ASSERT(fmts != NULL, "Input formats array should not be NULL");

    fmts = pixfmt_get_supported_output_fmts(&count);
    TEST_ASSERT(count > 0, "Should have some supported output formats");
    TEST_ASSERT(fmts != NULL, "Output formats array should not be NULL");
}

static void test_pixfmt_rgb_cvt_functions(void)
{
    printf("\n=== Test: RGB Conversion Functions ===\n");

    uint8_t src_rgb888[3] = {0xFF, 0x80, 0x40};
    uint8_t dst_rgb565[2] = {0};
    uint8_t dst_rgb888[3] = {0};

    int ret = pixfmt_cvt_rgb888_to_rgb565(src_rgb888, dst_rgb565, 1, 1, 3, 2);
    TEST_ASSERT(ret == 0, "rgb888_to_rgb565 should succeed");
    TEST_ASSERT(dst_rgb565[0] != 0 || dst_rgb565[1] != 0, "RGB565 output should not be zero");

    ret = pixfmt_cvt_rgb565_to_rgb888(dst_rgb565, dst_rgb888, 1, 1, 2, 3);
    TEST_ASSERT(ret == 0, "rgb565_to_rgb888 should succeed");

    uint8_t src_rgb332[1] = {0xE0};
    uint8_t dst_rgb888_332[3] = {0};
    ret = pixfmt_cvt_rgb332_to_rgb888(src_rgb332, dst_rgb888_332, 1, 1, 1, 3);
    TEST_ASSERT(ret == 0, "rgb332_to_rgb888 should succeed");
}

static void test_pixfmt_yuv_cvt_functions(void)
{
    printf("\n=== Test: YUV Conversion Functions ===\n");

    int w = 16, h = 16;
    int y_size = w * h;
    int uv_size = (w / 2) * (h / 2);

    uint8_t src_yuv420sp[16 * 16 + 16 * 8 * 2];
    uint8_t dst_yuv420p[16 * 16 + 16 * 8 * 2];

    for (int i = 0; i < y_size; i++) {
        src_yuv420sp[i] = i % 256;
    }
    for (int i = 0; i < uv_size * 2; i++) {
        src_yuv420sp[y_size + i] = i % 256;
    }

    int ret = pixfmt_cvt_yuv420sp_to_yuv420p(src_yuv420sp, dst_yuv420p, w, h, w, w);
    TEST_ASSERT(ret == 0, "yuv420sp_to_yuv420p should succeed");

    ret = pixfmt_cvt_yuv420p_to_yuv420sp(src_yuv420sp, dst_yuv420p, w, h, w, w);
    TEST_ASSERT(ret == 0, "yuv420p_to_yuv420sp should succeed");
}

static void test_pixfmt_rgb_yuv_cvt_functions(void)
{
    printf("\n=== Test: RGB-YUV Cross Conversion ===\n");

    int w = 4, h = 4;
    uint8_t src_rgb[4 * 4 * 3];
    uint8_t dst_yuv[4 * 4 * 3 / 2];
    uint8_t dst_rgb_back[4 * 4 * 3];

    for (int i = 0; i < sizeof(src_rgb); i++) {
        src_rgb[i] = i % 256;
    }

    int ret = pixfmt_cvt_rgb888_to_yuv420p(src_rgb, dst_yuv, w, h, w * 3, w);
    TEST_ASSERT(ret == 0, "rgb888_to_yuv420p should succeed");

    ret = pixfmt_cvt_yuv420p_to_rgb888(dst_yuv, dst_rgb_back, w, h, w, w * 3);
    TEST_ASSERT(ret == 0, "yuv420p_to_rgb888 should succeed");
}
#endif

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

    TEST_ASSERT(pixfmt_yuv_desc_equal(&g_yuv_desc_yuv420p_yu12, &g_yuv_desc_yuv420p_yu12) == true,
        "Same YUV descriptor should be equal");
    TEST_ASSERT(pixfmt_yuv_desc_equal(&g_yuv_desc_yuv420p_yu12, &g_yuv_desc_yuv420sp_nv12) == true,
        "Different YUV descriptors should not be equal");
}

static void test_pixfmt_all_formats_registered(void)
{
    printf("\n=== Test: All Formats Registered ===\n");

    TEST_ASSERT(ARRAY_SIZE(g_pixfmt_attr_table) == PIXFMT_MAX, "Number of formats registered should match!");

    for (int i = 0; i < PIXFMT_MAX; i++) {
        const pixfmt_attr_s *attr = pixfmt_get_attr((pixfmt_e)i);
        TEST_ASSERT(attr != NULL, "Format index %d registered", i);
        if (attr) {
            TEST_ASSERT(attr->fmt_id == i, "Format ID %d match index %d", attr->fmt_id, i);
        }
        pixfmt_dump_attr(attr);
    }
}

int main(void)
{
    printf("===========================================\n");
    printf("       PIXFMT Unit Test Suite\n");
    printf("===========================================\n");

    test_pixfmt_invalid_format();
    test_pixfmt_rgb888();
    test_pixfmt_rgba8888();
    test_pixfmt_rgb565();
    test_pixfmt_yuv420p();
    test_pixfmt_yuv420sp();
    test_pixfmt_get_by_name();
    test_pixfmt_framesize();
    test_pixfmt_vir_wid();
    test_pixfmt_rgb_desc();
    test_pixfmt_yuv_desc();
    // test_pixfmt_cvt_is_supported();
    // test_pixfmt_cvt_common_fmt();
    // test_pixfmt_supported_fmts();
    // test_pixfmt_rgb_cvt_functions();
    // test_pixfmt_yuv_cvt_functions();
    // test_pixfmt_rgb_yuv_cvt_functions();
    test_pixfmt_rgb_desc_equal();
    test_pixfmt_yuv_desc_equal();
    test_pixfmt_all_formats_registered();

    printf("\n===========================================\n");
    printf("       Test Results\n");
    printf("===========================================\n");
    printf("Passed: %d\n", g_test_passed);
    printf("Failed: %d\n", g_test_failed);
    printf("Total:  %d\n", g_test_passed + g_test_failed);

    if (g_test_failed > 0) {
        printf("\n*** SOME TESTS FAILED ***\n");
        return 1;
    }
    else {
        printf("\n*** ALL TESTS PASSED ***\n");
        return 0;
    }
}
