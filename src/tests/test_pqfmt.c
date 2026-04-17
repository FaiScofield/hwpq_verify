/**
 * @copyright: Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @brief:     pqfmt 单元测试
 * @author:
 * @create:    2026-04-17
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include "pqfmt.h"
#include "pqfmt_rgb.h"
#include "pqfmt_yuv.h"
#include "pqfmt_cvt.h"

#define TEST_PASSED 0
#define TEST_FAILED -1

static int g_test_passed = 0;
static int g_test_failed = 0;

#define TEST_ASSERT(cond, msg) do { \
    if (cond) { \
        g_test_passed++; \
        printf("[PASS] %s\n", msg); \
    } else { \
        g_test_failed++; \
        printf("[FAIL] %s\n", msg); \
    } \
} while(0)

static void test_pqfmt_invalid_format(void) {
    printf("\n=== Test: PQVF_FMT_INVALID ===\n");

    TEST_ASSERT(PQVF_FMT_INVALID == -1, "PQVF_FMT_INVALID should be -1");

    const pqvf_fmt_attr_s *desc = pqvf_get_fmt_desc(PQVF_FMT_INVALID);
    TEST_ASSERT(desc == NULL, "pqvf_get_fmt_desc(PQVF_FMT_INVALID) should return NULL");

    TEST_ASSERT(pqvf_fmt_bpp(PQVF_FMT_INVALID) == 0, "pqvf_fmt_bpp(PQVF_FMT_INVALID) should return 0");
    TEST_ASSERT(pqvf_fmt_depth(PQVF_FMT_INVALID) == 0, "pqvf_fmt_depth(PQVF_FMT_INVALID) should return 0");
}

static void test_pqfmt_rgb888(void) {
    printf("\n=== Test: RGB888 Format ===\n");

    const pqvf_fmt_attr_s *desc = pqvf_get_fmt_desc(PQVF_FMT_RGB888);
    TEST_ASSERT(desc != NULL, "pqvf_get_fmt_desc(RGB888) should not be NULL");
    if (!desc) return;

    TEST_ASSERT(desc->fmt_id == PQVF_FMT_RGB888, "fmt_id should be RGB888");
    TEST_ASSERT(desc->bpp == 24, "RGB888 bpp should be 24");
    TEST_ASSERT(desc->depth == 8, "RGB888 depth should be 8");
    TEST_ASSERT(desc->layout == PQFMT_LAYOUT_INTERLEAVED, "RGB888 layout should be interleaved");
    TEST_ASSERT(desc->base_type == PQVF_BASE_TYPE_RGB, "RGB888 base_type should be RGB");

    TEST_ASSERT(strcmp(desc->full_name, "RGB 888") == 0, "full_name should be 'RGB 888'");
    TEST_ASSERT(strcmp(desc->short_name, "rgb24") == 0, "short_name should be 'rgb24'");
    TEST_ASSERT(strcmp(desc->alias, "rgb888") == 0, "alias should be 'rgb888'");

    TEST_ASSERT(pqvf_fmt_bpp(PQVF_FMT_RGB888) == 24, "pqvf_fmt_bpp(RGB888) should be 24");
    TEST_ASSERT(pqvf_fmt_depth(PQVF_FMT_RGB888) == 8, "pqvf_fmt_depth(RGB888) should be 8");
    TEST_ASSERT(pqvf_fmt_is_rgb(PQVF_FMT_RGB888) == true, "RGB888 should be recognized as RGB");
    TEST_ASSERT(pqvf_fmt_is_yuv(PQVF_FMT_RGB888) == false, "RGB888 should not be recognized as YUV");
    TEST_ASSERT(pqvf_fmt_has_alpha(PQVF_FMT_RGB888) == false, "RGB888 should not have alpha");
}

static void test_pqfmt_rgba8888(void) {
    printf("\n=== Test: RGBA8888 Format ===\n");

    const pqvf_fmt_attr_s *desc = pqvf_get_fmt_desc(PQVF_FMT_RGBA8888);
    TEST_ASSERT(desc != NULL, "pqvf_get_fmt_desc(RGBA8888) should not be NULL");
    if (!desc) return;

    TEST_ASSERT(desc->bpp == 32, "RGBA8888 bpp should be 32");
    TEST_ASSERT(desc->has_padding == false, "RGBA8888 has_padding should be false");
    TEST_ASSERT(pqvf_fmt_has_alpha(PQVF_FMT_RGBA8888) == true, "RGBA8888 should have alpha");
}

static void test_pqfmt_rgb565(void) {
    printf("\n=== Test: RGB565 Format ===\n");

    const pqvf_fmt_attr_s *desc = pqvf_get_fmt_desc(PQVF_FMT_RGB565);
    TEST_ASSERT(desc != NULL, "pqvf_get_fmt_desc(RGB565) should not be NULL");
    if (!desc) return;

    TEST_ASSERT(desc->bpp == 16, "RGB565 bpp should be 16");
    TEST_ASSERT(desc->is_packed == true, "RGB565 is_packed should be true");
    TEST_ASSERT(desc->has_padding == false, "RGB565 has_padding should be false");
}

static void test_pqfmt_yuv420p(void) {
    printf("\n=== Test: YUV420P Format ===\n");

    const pqvf_fmt_attr_s *desc = pqvf_get_fmt_desc(PQVF_FMT_YUV420P_YU12);
    TEST_ASSERT(desc != NULL, "pqvf_get_fmt_desc(YUV420P) should not be NULL");
    if (!desc) return;

    TEST_ASSERT(desc->base_type == PQVF_BASE_TYPE_YUV, "YUV420P base_type should be YUV");
    TEST_ASSERT(desc->layout == PQFMT_LAYOUT_PLANAR, "YUV420P layout should be planar");
    TEST_ASSERT(pqvf_fmt_is_yuv(PQVF_FMT_YUV420P_YU12) == true, "YUV420P should be recognized as YUV");
    TEST_ASSERT(pqvf_fmt_is_rgb(PQVF_FMT_YUV420P_YU12) == false, "YUV420P should not be recognized as RGB");

    int h_sub = 0, v_sub = 0;
    pqvf_fmt_get_chroma_subsampling(PQVF_FMT_YUV420P_YU12, &h_sub, &v_sub);
    TEST_ASSERT(h_sub == 2 && v_sub == 2, "YUV420P chroma subsampling should be 2x2");
}

static void test_pqfmt_yuv420sp(void) {
    printf("\n=== Test: YUV420SP (NV12) Format ===\n");

    const pqvf_fmt_attr_s *desc = pqvf_get_fmt_desc(PQVF_FMT_YUV420SP_NV12);
    TEST_ASSERT(desc != NULL, "pqvf_get_fmt_desc(NV12) should not be NULL");
    if (!desc) return;

    TEST_ASSERT(desc->layout == PQFMT_LAYOUT_SEMIPLANAR, "NV12 layout should be semi-planar");
}

static void test_pqfmt_get_by_name(void) {
    printf("\n=== Test: Get Format by Name ===\n");

    const pqvf_fmt_attr_s *desc = pqvf_get_fmt_desc_by_name("rgb888");
    TEST_ASSERT(desc != NULL, "get_fmt_desc_by_name('rgb888') should not be NULL");
    if (desc) {
        TEST_ASSERT(desc->fmt_id == PQVF_FMT_RGB888, "Should find RGB888 by alias 'rgb888'");
    }

    desc = pqvf_get_fmt_desc_by_name("rgb24");
    TEST_ASSERT(desc != NULL, "get_fmt_desc_by_name('rgb24') should not be NULL");
    if (desc) {
        TEST_ASSERT(desc->fmt_id == PQVF_FMT_RGB888, "Should find RGB888 by short_name 'rgb24'");
    }

    desc = pqvf_get_fmt_desc_by_name("RGB 888");
    TEST_ASSERT(desc != NULL, "get_fmt_desc_by_name('RGB 888') should not be NULL");
    if (desc) {
        TEST_ASSERT(desc->fmt_id == PQVF_FMT_RGB888, "Should find RGB888 by full_name 'RGB 888'");
    }

    desc = pqvf_get_fmt_desc_by_name("nonexistent");
    TEST_ASSERT(desc == NULL, "get_fmt_desc_by_name('nonexistent') should return NULL");
}

static void test_pqfmt_framesize(void) {
    printf("\n=== Test: Framesize Calculation ===\n");

    size_t rgb888_size = pqvf_fmt_framesize(PQVF_FMT_RGB888, 1920, 1080, 0, 0);
    TEST_ASSERT(rgb888_size == 1920 * 1080 * 3, "RGB888 1920x1080 framesize should be 6,220,800");

    size_t rgba8888_size = pqvf_fmt_framesize(PQVF_FMT_RGBA8888, 1920, 1080, 0, 0);
    TEST_ASSERT(rgba8888_size == 1920 * 1080 * 4, "RGBA8888 1920x1080 framesize should be 8,294,400");

    size_t yuv420p_size = pqvf_fmt_framesize(PQVF_FMT_YUV420P_YU12, 1920, 1080, 0, 0);
    TEST_ASSERT(yuv420p_size == 1920 * 1080 * 3 / 2, "YUV420P 1920x1080 framesize should be 3,110,400");
}

static void test_pqfmt_vir_wid(void) {
    printf("\n=== Test: Virtual Width Calculation ===\n");

    int vir_wid = pqvf_fmt_vir_wid(PQVF_FMT_RGB888, 1920, 0);
    TEST_ASSERT(vir_wid == 1920, "RGB888 vir_wid with align 0 should be same as width");

    vir_wid = pqvf_fmt_vir_wid(PQVF_FMT_RGB565, 1920, 16);
    TEST_ASSERT(vir_wid == 1920, "RGB565 vir_wid with height_shift 16 should be 1920");

    vir_wid = pqvf_fmt_vir_wid(PQVF_FMT_RGBA8888, 1920, 0);
    TEST_ASSERT(vir_wid == 1920 * 4, "RGBA8888 vir_wid should account for 4 channels");
}

static void test_pqfmt_rgb_desc(void) {
    printf("\n=== Test: RGB Descriptor ===\n");

    TEST_ASSERT(pqfmt_rgb_desc_is_valid(&g_rgb_desc_rgb888) == true, "RGB888 desc should be valid");
    TEST_ASSERT(pqfmt_rgb_desc_has_alpha(&g_rgb_desc_rgb888) == false, "RGB888 should not have alpha");
    TEST_ASSERT(pqfmt_rgb_desc_is_bgr_order(&g_rgb_desc_rgb888) == false, "RGB888 should not be BGR order");

    TEST_ASSERT(pqfmt_rgb_desc_is_valid(&g_rgb_desc_rgba8888) == true, "RGBA8888 desc should be valid");
    TEST_ASSERT(pqfmt_rgb_desc_has_alpha(&g_rgb_desc_rgba8888) == true, "RGBA8888 should have alpha");

    uint8_t r, g, b, a;
    pqfmt_rgb_desc_get_channel_bits(&g_rgb_desc_rgb565, &r, &g, &b, &a);
    TEST_ASSERT(r == 5 && g == 6 && b == 5, "RGB565 channel bits should be R=5, G=6, B=5");
    TEST_ASSERT(a == 0, "RGB565 alpha should be 0");
}

static void test_pqfmt_yuv_desc(void) {
    printf("\n=== Test: YUV Descriptor ===\n");

    TEST_ASSERT(pqfmt_yuv_desc_is_valid(&g_yuv_desc_yuv420p_yu12) == true, "YUV420P desc should be valid");
    TEST_ASSERT(pqfmt_yuv_desc_is_tile(&g_yuv_desc_yuv420p_yv12) == false, "YUV420P should not be tile format");
    TEST_ASSERT(pqfmt_yuv_desc_is_line_variant(&g_yuv_desc_yuv420p_yu12) == false, "YUV420P should not be line variant");

    TEST_ASSERT(pqfmt_yuv_desc_is_tile(&g_yuv_desc_yuv420sp_tile4x4) == true, "TILE4x4 should be tile format");

    int plane_count = pqfmt_yuv_desc_get_plane_count(&g_yuv_desc_yuv420p_yu12);
    TEST_ASSERT(plane_count == 3, "YUV420P should have 3 planes");

    plane_count = pqfmt_yuv_desc_get_plane_count(&g_yuv_desc_yuv420sp_nv12);
    TEST_ASSERT(plane_count == 2, "NV12 should have 2 planes");

    int h_sub = 0, v_sub = 0;
    pqfmt_yuv_desc_get_chroma_subsampling(&g_yuv_desc_yuv420p_yu12, &h_sub, &v_sub);
    TEST_ASSERT(h_sub == 2 && v_sub == 2, "YUV420P subsampling should be 2x2");

    pqfmt_yuv_desc_get_chroma_subsampling(&g_yuv_desc_yuv422p_yu16, &h_sub, &v_sub);
    TEST_ASSERT(h_sub == 2 && v_sub == 1, "YUV422P subsampling should be 2x1");
}

static void test_pqfmt_cvt_init(void) {
    printf("\n=== Test: Format Conversion Init ===\n");

    pqvf_cvt_ctx_t ctx;
    int ret = pqvf_cvt_init(&ctx, PQVF_FMT_RGB888, PQVF_FMT_RGB565, 1920, 1080);
    TEST_ASSERT(ret == 0, "pqvf_cvt_init should succeed");
    TEST_ASSERT(ctx.src_fmt == PQVF_FMT_RGB888, "src_fmt should be RGB888");
    TEST_ASSERT(ctx.dst_fmt == PQVF_FMT_RGB565, "dst_fmt should be RGB565");
    TEST_ASSERT(ctx.src_w == 1920 && ctx.src_h == 1080, "src dimensions should be 1920x1080");

    ret = pqvf_cvt_init(NULL, PQVF_FMT_RGB888, PQVF_FMT_RGB565, 1920, 1080);
    TEST_ASSERT(ret == -1, "pqvf_cvt_init with NULL ctx should return -1");
}

static void test_pqfmt_cvt_is_supported(void) {
    printf("\n=== Test: Conversion Support Check ===\n");

    TEST_ASSERT(pqvf_cvt_is_supported(PQVF_FMT_RGB888, PQVF_FMT_RGB888) == true,
                "Same format conversion should be supported");
    TEST_ASSERT(pqvf_cvt_is_supported(PQVF_FMT_RGB888, PQVF_FMT_RGB565) == true,
                "RGB888 to RGB565 should be supported");
    TEST_ASSERT(pqvf_cvt_is_supported(PQVF_FMT_RGB888, PQVF_FMT_YUV420P_YU12) == true,
                "RGB888 to YUV420P should be supported");
    TEST_ASSERT(pqvf_cvt_is_supported(PQVF_FMT_YUV420P_YU12, PQVF_FMT_RGB888) == true,
                "YUV420P to RGB888 should be supported");
}

static void test_pqfmt_cvt_intermediate_fmt(void) {
    printf("\n=== Test: Intermediate Format ===\n");

    pqvf_imgfmt_e inter = pqvf_cvt_get_intermediate_fmt(PQVF_FMT_RGB888, PQVF_FMT_RGB888);
    TEST_ASSERT(inter == PQVF_FMT_RGB888, "Same format intermediate should be the format itself");

    inter = pqvf_cvt_get_intermediate_fmt(PQVF_FMT_RGB888, PQVF_FMT_RGB565);
    TEST_ASSERT(inter == PQVF_FMT_RGB888, "RGB to RGB intermediate should be RGB888");

    inter = pqvf_cvt_get_intermediate_fmt(PQVF_FMT_YUV420P_YU12, PQVF_FMT_YUV422P_YU16);
    TEST_ASSERT(inter == PQVF_FMT_YUV420P_YU12, "YUV to YUV intermediate should be YUV420P");

    inter = pqvf_cvt_get_intermediate_fmt(PQVF_FMT_RGB888, PQVF_FMT_YUV420P_YU12);
    TEST_ASSERT(inter == PQVF_FMT_YUV420P_YU12 || inter == PQVF_FMT_RGB888,
                "RGB to YUV intermediate should be YUV420P or RGB888");
}

static void test_pqfmt_supported_fmts(void) {
    printf("\n=== Test: Supported Format Lists ===\n");

    int count = 0;
    pqvf_imgfmt_e *fmts = pqvf_get_supported_input_fmts(&count);
    TEST_ASSERT(count > 0, "Should have some supported input formats");
    TEST_ASSERT(fmts != NULL, "Input formats array should not be NULL");

    fmts = pqvf_get_supported_output_fmts(&count);
    TEST_ASSERT(count > 0, "Should have some supported output formats");
    TEST_ASSERT(fmts != NULL, "Output formats array should not be NULL");
}

static void test_pqfmt_rgb_cvt_functions(void) {
    printf("\n=== Test: RGB Conversion Functions ===\n");

    uint8_t src_rgb888[3] = {0xFF, 0x80, 0x40};
    uint8_t dst_rgb565[2] = {0};
    uint8_t dst_rgb888[3] = {0};

    int ret = pqvf_cvt_rgb888_to_rgb565(src_rgb888, dst_rgb565, 1, 1, 3, 2);
    TEST_ASSERT(ret == 0, "rgb888_to_rgb565 should succeed");
    TEST_ASSERT(dst_rgb565[0] != 0 || dst_rgb565[1] != 0, "RGB565 output should not be zero");

    ret = pqvf_cvt_rgb565_to_rgb888(dst_rgb565, dst_rgb888, 1, 1, 2, 3);
    TEST_ASSERT(ret == 0, "rgb565_to_rgb888 should succeed");

    uint8_t src_rgb332[1] = {0xE0};
    uint8_t dst_rgb888_332[3] = {0};
    ret = pqvf_cvt_rgb332_to_rgb888(src_rgb332, dst_rgb888_332, 1, 1, 1, 3);
    TEST_ASSERT(ret == 0, "rgb332_to_rgb888 should succeed");
}

static void test_pqfmt_yuv_cvt_functions(void) {
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

    int ret = pqvf_cvt_yuv420sp_to_yuv420p(src_yuv420sp, dst_yuv420p, w, h, w, w);
    TEST_ASSERT(ret == 0, "yuv420sp_to_yuv420p should succeed");

    ret = pqvf_cvt_yuv420p_to_yuv420sp(src_yuv420sp, dst_yuv420p, w, h, w, w);
    TEST_ASSERT(ret == 0, "yuv420p_to_yuv420sp should succeed");
}

static void test_pqfmt_rgb_yuv_cvt_functions(void) {
    printf("\n=== Test: RGB-YUV Cross Conversion ===\n");

    int w = 4, h = 4;
    uint8_t src_rgb[4 * 4 * 3];
    uint8_t dst_yuv[4 * 4 * 3 / 2];
    uint8_t dst_rgb_back[4 * 4 * 3];

    for (int i = 0; i < sizeof(src_rgb); i++) {
        src_rgb[i] = i % 256;
    }

    int ret = pqvf_cvt_rgb888_to_yuv420p(src_rgb, dst_yuv, w, h, w * 3, w);
    TEST_ASSERT(ret == 0, "rgb888_to_yuv420p should succeed");

    ret = pqvf_cvt_yuv420p_to_rgb888(dst_yuv, dst_rgb_back, w, h, w, w * 3);
    TEST_ASSERT(ret == 0, "yuv420p_to_rgb888 should succeed");
}

static void test_pqfmt_rgb_desc_equal(void) {
    printf("\n=== Test: RGB Descriptor Equal ===\n");

    TEST_ASSERT(pqfmt_rgb_desc_equal(&g_rgb_desc_rgb888, &g_rgb_desc_rgb888) == true,
                "Same descriptor should be equal");
    TEST_ASSERT(pqfmt_rgb_desc_equal(&g_rgb_desc_rgb888, &g_rgb_desc_bgr888) == false,
                "Different descriptors should not be equal");
}

static void test_pqfmt_yuv_desc_equal(void) {
    printf("\n=== Test: YUV Descriptor Equal ===\n");

    TEST_ASSERT(pqfmt_yuv_desc_equal(&g_yuv_desc_yuv420p_yu12, &g_yuv_desc_yuv420p_yu12) == true,
                "Same YUV descriptor should be equal");
    TEST_ASSERT(pqfmt_yuv_desc_equal(&g_yuv_desc_yuv420p_yu12, &g_yuv_desc_yuv420sp_nv12) == false,
                "Different YUV descriptors should not be equal");
}

static void test_pqfmt_all_formats_registered(void) {
    printf("\n=== Test: All Formats Registered ===\n");

    for (int i = 0; i < PQVF_FMT_MAX; i++) {
        if (i == PQVF_FMT_INVALID) continue;
        const pqvf_fmt_attr_s *desc = pqvf_get_fmt_desc((pqvf_imgfmt_e)i);
        TEST_ASSERT(desc != NULL, "Format index should be registered");
        if (desc) {
            TEST_ASSERT(desc->fmt_id == i, "Format ID should match index");
        }
    }
}

int main(void) {
    printf("===========================================\n");
    printf("       PQFMT Unit Test Suite\n");
    printf("===========================================\n");

    test_pqfmt_invalid_format();
    test_pqfmt_rgb888();
    test_pqfmt_rgba8888();
    test_pqfmt_rgb565();
    test_pqfmt_yuv420p();
    test_pqfmt_yuv420sp();
    test_pqfmt_get_by_name();
    test_pqfmt_framesize();
    test_pqfmt_vir_wid();
    test_pqfmt_rgb_desc();
    test_pqfmt_yuv_desc();
    test_pqfmt_cvt_init();
    test_pqfmt_cvt_is_supported();
    test_pqfmt_cvt_intermediate_fmt();
    test_pqfmt_supported_fmts();
    test_pqfmt_rgb_cvt_functions();
    test_pqfmt_yuv_cvt_functions();
    test_pqfmt_rgb_yuv_cvt_functions();
    test_pqfmt_rgb_desc_equal();
    test_pqfmt_yuv_desc_equal();
    test_pqfmt_all_formats_registered();

    printf("\n===========================================\n");
    printf("       Test Results\n");
    printf("===========================================\n");
    printf("Passed: %d\n", g_test_passed);
    printf("Failed: %d\n", g_test_failed);
    printf("Total:  %d\n", g_test_passed + g_test_failed);

    if (g_test_failed > 0) {
        printf("\n*** SOME TESTS FAILED ***\n");
        return 1;
    } else {
        printf("\n*** ALL TESTS PASSED ***\n");
        return 0;
    }
}
