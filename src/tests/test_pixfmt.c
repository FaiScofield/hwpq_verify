/**
 * @copyright: Copyright (c) Rockchip Electronics Co., Ltd. 2026-. All rights reserved.
 * @brief:     pixfmt unit test
 * @author:    vance.wu@rock-chips.com
 * @create:    2026-04-17
 */

#include "pixfmt.h"
#include "pixfmt_cvt.h"
#include "verify_com.h"
#include "test_pixfmt_common.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>

int g_test_passed = 0;
int g_test_failed = 0;

static void test_pixfmt_check_invalid(void)
{
    printf("\n=== Test: PIXFMT_INVALID ===\n");

    TEST_ASSERT(PIXFMT_INVALID == -1, "PIXFMT_INVALID should be -1");

    const pixfmt_attr_s *attr = pixfmt_get_attr(PIXFMT_INVALID);
    TEST_ASSERT(attr == NULL, "pixfmt_get_attr(PIXFMT_INVALID) should return NULL");

    TEST_ASSERT(pixfmt_bpp(PIXFMT_INVALID) == 0, "pixfmt_bpp(PIXFMT_INVALID) should return 0");
    TEST_ASSERT(pixfmt_depth(PIXFMT_INVALID) == 0, "pixfmt_depth(PIXFMT_INVALID) should return 0");
    TEST_ASSERT(pixfmt_nb_comps(PIXFMT_INVALID) == 0, "pixfmt_nb_comps(PIXFMT_INVALID) should return 0");
    TEST_ASSERT(pixfmt_nb_planes(PIXFMT_INVALID) == 0, "pixfmt_nb_planes(PIXFMT_INVALID) should return 0");
}

static void test_pixfmt_attr_by_name(void)
{
    printf("\n=== Test: Get Format by Name ===\n");

    for (int i = 0; i < PIXFMT_NB_COUNT; i++) {
        const pixfmt_attr_s *attr = pixfmt_get_attr((pixfmt_e)i);
        TEST_ASSERT(attr != NULL, "the attr of pixfmt %#02d should not be NULL!", i);
        TEST_ASSERT(attr == pixfmt_get_attr_by_name(attr->full_name),
            "the attr get by full_name of pixfmt %#02d should be %p", i, attr);
        TEST_ASSERT(attr == pixfmt_get_attr_by_name(attr->short_name),
            "the attr get by short_name of pixfmt %#02d should be %p", i, attr);
        TEST_ASSERT(attr->fmt_id == i, "the attr of pixfmt %#02d should have fmt_id %#02d", i, attr->fmt_id);
    }

    const pixfmt_attr_s *attr = pixfmt_get_attr_by_name("nonexistent");
    TEST_ASSERT(attr == NULL, "pixfmt_get_attr_by_name('nonexistent') should return NULL");
}

static void test_pixfmt_all_formats_registered(bool dump_attr)
{
    printf("\n=== Test: All Formats Registered ===\n");

    TEST_ASSERT(ARRAY_SIZE(g_pixfmt_attr_table) == PIXFMT_NB_COUNT, "Number of formats registered should match!");

    for (int i = 0; i < PIXFMT_NB_COUNT; i++) {
        const pixfmt_attr_s *attr = pixfmt_get_attr((pixfmt_e)i);
        TEST_ASSERT(attr != NULL, "Format index %d registered", i);
        if (attr) {
            TEST_ASSERT(attr->fmt_id == i, "Format ID %d match index %d", attr->fmt_id, i);
        }
        if (dump_attr)
            pixfmt_dump_attr(attr);
    }
}

static void test_get_common_fmt()
{
    // rgb formats
    for (int i = 0; i <= PIXFMT_ABGR8888; i++) {
        TEST_ASSERT(pixfmt_get_common_fmt(i, PIXFMT_LAYOUT_SEMIPLANAR, false) == PIXFMT_RGB888,
            "base fmt of %02d (without alpha) shoudble be RGB24", i);
        TEST_ASSERT(pixfmt_get_common_fmt(i, PIXFMT_LAYOUT_SEMIPLANAR, true) == PIXFMT_RGBA8888,
            "base fmt of %02d (with alpha) shoudble be RGBA32", i);
    }
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_RGB10Lsb, PIXFMT_LAYOUT_INTERLEAVED, false) == PIXFMT_RGB10Lsb,
        "base fmt of %02d (without alpha) shoudble be RGB24", PIXFMT_RGB10Lsb);
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_RGB10Lsb, PIXFMT_LAYOUT_INTERLEAVED, true) == PIXFMT_RGBA10Lsb,
        "base fmt of %02d (with alpha) shoudble be RGBA32", PIXFMT_RGB10Lsb);
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_RGBA10Lsb, PIXFMT_LAYOUT_INTERLEAVED, false) == PIXFMT_RGB10Lsb,
        "base fmt of %02d (without alpha) shoudble be RGB24", PIXFMT_RGBA10Lsb);
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_RGBA10Lsb, PIXFMT_LAYOUT_INTERLEAVED, true) == PIXFMT_RGBA10Lsb,
        "base fmt of %02d (with alpha) shoudble be RGBA32", PIXFMT_RGBA10Lsb);
    for (int i = PIXFMT_RGB332; i <= PIXFMT_ABGR4444; i++) {
        TEST_ASSERT(pixfmt_get_common_fmt(i, PIXFMT_LAYOUT_INTERLEAVED, false) == PIXFMT_RGB888,
            "base fmt of %02d (without alpha) shoudble be RGB24", i);
        TEST_ASSERT(pixfmt_get_common_fmt(i, PIXFMT_LAYOUT_INTERLEAVED, true) == PIXFMT_RGBA8888,
            "base fmt of %02d (with alpha) shoudble be RGBA32", i);
    }
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_RGBA1010102, PIXFMT_LAYOUT_INTERLEAVED, false) == PIXFMT_RGB10Lsb,
        "base fmt of %02d (without alpha) shoudble be RGB24", PIXFMT_RGBA1010102);
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_RGBA1010102, PIXFMT_LAYOUT_INTERLEAVED, true) == PIXFMT_RGBA10Lsb,
        "base fmt of %02d (with alpha) shoudble be RGBA32", PIXFMT_RGBA1010102);
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_ABGR2101010, PIXFMT_LAYOUT_INTERLEAVED, false) == PIXFMT_RGB10Lsb,
        "base fmt of %02d (without alpha) shoudble be RGB24", PIXFMT_ABGR2101010);
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_ABGR2101010, PIXFMT_LAYOUT_INTERLEAVED, true) == PIXFMT_RGBA10Lsb,
        "base fmt of %02d (with alpha) shoudble be RGBA32", PIXFMT_ABGR2101010);

    // yuv444 formats
    for (int i = PIXFMT_YUV444I_VU24; i <= PIXFMT_YUV444SP_10LSB; i++) {
        const pixfmt_attr_s *attr = pixfmt_get_attr((pixfmt_e)i);

        if (attr->depth <= 8) {
            TEST_ASSERT(pixfmt_get_common_fmt((pixfmt_e)i, PIXFMT_LAYOUT_INTERLEAVED, false) == PIXFMT_YUV444I_VU24,
                "base fmt of %02d (I) shoudble be YUV444I_VU24", i);
            TEST_ASSERT(pixfmt_get_common_fmt((pixfmt_e)i, PIXFMT_LAYOUT_PLANAR, false) == PIXFMT_YUV444P_YU24,
                "base fmt of %02d (P) shoudble be YUV444P_YU24", i);
            TEST_ASSERT(pixfmt_get_common_fmt((pixfmt_e)i, PIXFMT_LAYOUT_SEMIPLANAR, false) == PIXFMT_YUV444SP_NV24,
                "base fmt of %02d (SP) shoudble be YUV444SP_NV24", i);
        }
        else if (attr->depth == 10) {
            TEST_ASSERT(pixfmt_get_common_fmt((pixfmt_e)i, PIXFMT_LAYOUT_INTERLEAVED, false) == PIXFMT_YUV444I_10LSB,
                "base fmt of %02d (I) shoudble be YUV444I_10LSB", i);
            TEST_ASSERT(pixfmt_get_common_fmt((pixfmt_e)i, PIXFMT_LAYOUT_PLANAR, false) == PIXFMT_YUV444P_10LSB,
                "base fmt of %02d (P) shoudble be YUV444P_10LSB", i);
            TEST_ASSERT(pixfmt_get_common_fmt((pixfmt_e)i, PIXFMT_LAYOUT_SEMIPLANAR, false) == PIXFMT_YUV444SP_10LSB,
                "base fmt of %02d (SP) shoudble be YUV444SP_10LSB", i);
        }
    }

    // yuv422 formats
    for (int i = PIXFMT_YUV422I_YUYV; i <= PIXFMT_YUV422SP_10LSB; i++) {
        const pixfmt_attr_s *attr = pixfmt_get_attr((pixfmt_e)i);

        if (attr->depth <= 8) {
            TEST_ASSERT(pixfmt_get_common_fmt((pixfmt_e)i, PIXFMT_LAYOUT_INTERLEAVED, false) == PIXFMT_YUV422I_YUYV,
                "base fmt of %02d (I) shoudble be YUV422I_YUYV", i);
            TEST_ASSERT(pixfmt_get_common_fmt((pixfmt_e)i, PIXFMT_LAYOUT_PLANAR, false) == PIXFMT_YUV422P_YU16,
                "base fmt of %02d (P) shoudble be YUV422P_YU16", i);
            TEST_ASSERT(pixfmt_get_common_fmt((pixfmt_e)i, PIXFMT_LAYOUT_SEMIPLANAR, false) == PIXFMT_YUV422SP_NV16,
                "base fmt of %02d (SP) shoudble be YUV422SP_NV16", i);
        }
        else if (attr->depth == 10) {
            TEST_ASSERT(pixfmt_get_common_fmt((pixfmt_e)i, PIXFMT_LAYOUT_INTERLEAVED, false) == PIXFMT_YUV422I_Y210,
                "base fmt of %02d (I) shoudble be YUV422I_Y210", i);
            TEST_ASSERT(pixfmt_get_common_fmt((pixfmt_e)i, PIXFMT_LAYOUT_PLANAR, false) == PIXFMT_YUV422P_10LSB,
                "base fmt of %02d (P) shoudble be YUV422P_10LSB", i);
            TEST_ASSERT(pixfmt_get_common_fmt((pixfmt_e)i, PIXFMT_LAYOUT_SEMIPLANAR, false) == PIXFMT_YUV422SP_10LSB,
                "base fmt of %02d (SP) shoudble be YUV422SP_10LSB", i);
        }
    }

    // yuv420 formats
    for (int i = PIXFMT_YUV420P_YU12; i <= PIXFMT_YUV420SP_10LSB; i++) {
        const pixfmt_attr_s *attr = pixfmt_get_attr((pixfmt_e)i);

        if (attr->depth <= 8) {
            TEST_ASSERT(pixfmt_get_common_fmt((pixfmt_e)i, PIXFMT_LAYOUT_INTERLEAVED, false) == PIXFMT_INVALID,
                "base fmt of %02d (I) shoudble be INVALID", i);
            TEST_ASSERT(pixfmt_get_common_fmt((pixfmt_e)i, PIXFMT_LAYOUT_PLANAR, false) == PIXFMT_YUV420P_YU12,
                "base fmt of %02d (P) shoudble be YUV420P_YU12", i);
            TEST_ASSERT(pixfmt_get_common_fmt((pixfmt_e)i, PIXFMT_LAYOUT_SEMIPLANAR, false) == PIXFMT_YUV420SP_NV12,
                "base fmt of %02d (SP) shoudble be YUV420SP_NV12", i);
        }
        else if (attr->depth == 10) {
            TEST_ASSERT(pixfmt_get_common_fmt((pixfmt_e)i, PIXFMT_LAYOUT_INTERLEAVED, false) == PIXFMT_INVALID,
                "base fmt of %02d (I) shoudble be INVALID", i);
            TEST_ASSERT(pixfmt_get_common_fmt((pixfmt_e)i, PIXFMT_LAYOUT_PLANAR, false) == PIXFMT_YUV420P_10LSB,
                "base fmt of %02d (P) shoudble be YUV420P_10LSB", i);
            TEST_ASSERT(pixfmt_get_common_fmt((pixfmt_e)i, PIXFMT_LAYOUT_SEMIPLANAR, false) == PIXFMT_YUV420SP_10LSB,
                "base fmt of %02d (SP) shoudble be YUV420SP_10LSB", i);
        }
    }

    // yuv411 formats
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_YUV411P_YU11, PIXFMT_LAYOUT_INTERLEAVED, false) == PIXFMT_INVALID,
        "base fmt of %02d (I) shoudble be INVALID", PIXFMT_YUV411P_YU11);
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_YUV411P_YU11, PIXFMT_LAYOUT_PLANAR, false) == PIXFMT_YUV411P_YU11,
        "base fmt of %02d (P) shoudble be YUV411P_YU11", PIXFMT_YUV411P_YU11);
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_YUV411P_YU11, PIXFMT_LAYOUT_SEMIPLANAR, false) == PIXFMT_INVALID,
        "base fmt of %02d (SP) shoudble be INVALID", PIXFMT_YUV411P_YU11);
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_YUV411P_YV11, PIXFMT_LAYOUT_INTERLEAVED, false) == PIXFMT_INVALID,
        "base fmt of %02d (I) shoudble be INVALID", PIXFMT_YUV411P_YV11);
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_YUV411P_YV11, PIXFMT_LAYOUT_PLANAR, false) == PIXFMT_YUV411P_YU11,
        "base fmt of %02d (P) shoudble be YUV411P_YU11", PIXFMT_YUV411P_YV11);
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_YUV411P_YV11, PIXFMT_LAYOUT_SEMIPLANAR, false) == PIXFMT_INVALID,
        "base fmt of %02d (SP) shoudble be INVALID", PIXFMT_YUV411P_YV11);

    // yuv410 formats
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_YUV410P_YUV9, PIXFMT_LAYOUT_INTERLEAVED, false) == PIXFMT_INVALID,
        "base fmt of %02d (I) shoudble be INVALID", PIXFMT_YUV410P_YUV9);
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_YUV410P_YUV9, PIXFMT_LAYOUT_PLANAR, false) == PIXFMT_YUV410P_YUV9,
        "base fmt of %02d (P) shoudble be YUV410P_YUV9", PIXFMT_YUV410P_YUV9);
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_YUV410P_YUV9, PIXFMT_LAYOUT_SEMIPLANAR, false) == PIXFMT_INVALID,
        "base fmt of %02d (SP) shoudble be INVALID", PIXFMT_YUV410P_YUV9);
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_YUV410P_YVU9, PIXFMT_LAYOUT_INTERLEAVED, false) == PIXFMT_INVALID,
        "base fmt of %02d (I) shoudble be INVALID", PIXFMT_YUV410P_YVU9);
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_YUV410P_YVU9, PIXFMT_LAYOUT_PLANAR, false) == PIXFMT_YUV410P_YUV9,
        "base fmt of %02d (P) shoudble be YUV410P_YUV9", PIXFMT_YUV410P_YVU9);
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_YUV410P_YVU9, PIXFMT_LAYOUT_SEMIPLANAR, false) == PIXFMT_INVALID,
        "base fmt of %02d (SP) shoudble be INVALID", PIXFMT_YUV410P_YVU9);

    // yuv400 formats
    for (int i = PIXFMT_YUV400_R1; i <= PIXFMT_YUV400_R4; i++) {
        TEST_ASSERT(pixfmt_get_common_fmt((pixfmt_e)i, PIXFMT_LAYOUT_INTERLEAVED, false) == PIXFMT_YUV400_R8,
            "base fmt of %02d (I) shoudble be INVALID", i);
        TEST_ASSERT(pixfmt_get_common_fmt((pixfmt_e)i, PIXFMT_LAYOUT_PLANAR, false) == PIXFMT_YUV400_R8,
            "base fmt of %02d (P) shoudble be YUV400_R8", i);
        TEST_ASSERT(pixfmt_get_common_fmt((pixfmt_e)i, PIXFMT_LAYOUT_SEMIPLANAR, false) == PIXFMT_YUV400_R8,
            "base fmt of %02d (SP) shoudble be INVALID", i);
    }
    for (int i = PIXFMT_YUV400_R8; i <= PIXFMT_YUV400_R16; i++) {
        TEST_ASSERT(pixfmt_get_common_fmt((pixfmt_e)i, PIXFMT_LAYOUT_INTERLEAVED, false) == (pixfmt_e)i,
            "base fmt of %02d (I) shoudble be INVALID", i);
        TEST_ASSERT(pixfmt_get_common_fmt((pixfmt_e)i, PIXFMT_LAYOUT_PLANAR, false) == (pixfmt_e)i,
            "base fmt of %02d (P) shoudble be itself", i);
        TEST_ASSERT(pixfmt_get_common_fmt((pixfmt_e)i, PIXFMT_LAYOUT_SEMIPLANAR, false) == (pixfmt_e)i,
            "base fmt of %02d (SP) shoudble be INVALID", i);
    }

    // YUV tile formats
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_YUV444SP_TILE4x4, PIXFMT_LAYOUT_INTERLEAVED, false) == PIXFMT_INVALID,
        "base fmt of %02d (I) shoudble be INVALID", PIXFMT_YUV444SP_TILE4x4);
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_YUV444SP_TILE4x4, PIXFMT_LAYOUT_PLANAR, false) == PIXFMT_INVALID,
        "base fmt of %02d (P) shoudble be INVALID", PIXFMT_YUV444SP_TILE4x4);
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_YUV444SP_TILE4x4, PIXFMT_LAYOUT_SEMIPLANAR, false) == PIXFMT_YUV444SP_NV24,
        "base fmt of %02d (SP) shoudble be YUV444SP_NV24", PIXFMT_YUV444SP_TILE4x4);
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_YUV422SP_TILE4x4, PIXFMT_LAYOUT_INTERLEAVED, false) == PIXFMT_INVALID,
        "base fmt of %02d (I) shoudble be INVALID", PIXFMT_YUV422SP_TILE4x4);
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_YUV422SP_TILE4x4, PIXFMT_LAYOUT_PLANAR, false) == PIXFMT_INVALID,
        "base fmt of %02d (P) shoudble be INVALID", PIXFMT_YUV422SP_TILE4x4);
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_YUV422SP_TILE4x4, PIXFMT_LAYOUT_SEMIPLANAR, false) == PIXFMT_YUV422SP_NV16,
        "base fmt of %02d (SP) shoudble be YUV422SP_NV16", PIXFMT_YUV422SP_TILE4x4);
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_YUV420SP_TILE4x4, PIXFMT_LAYOUT_INTERLEAVED, false) == PIXFMT_INVALID,
        "base fmt of %02d (I) shoudble be INVALID", PIXFMT_YUV420SP_TILE4x4);
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_YUV420SP_TILE4x4, PIXFMT_LAYOUT_PLANAR, false) == PIXFMT_INVALID,
        "base fmt of %02d (P) shoudble be INVALID", PIXFMT_YUV420SP_TILE4x4);
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_YUV420SP_TILE4x4, PIXFMT_LAYOUT_SEMIPLANAR, false) == PIXFMT_YUV420SP_NV12,
        "base fmt of %02d (SP) shoudble be YUV420SP_NV12", PIXFMT_YUV420SP_TILE4x4);
}

#include "test_pixfmt_rgb.c"
#include "test_pixfmt_yuv.c"

int main(void)
{
    bool dump_attr = false;

    printf("===========================================\n");
    printf("       PIXFMT Unit Test Suite\n");
    printf("===========================================\n");

    //test_pixfmt_check_invalid();
    //test_pixfmt_attr_by_name();
    //test_pixfmt_all_formats_registered(dump_attr);
    //test_get_common_fmt();

    test_pixfmt_rgb_desc_all();
    test_pixfmt_rgb_cvt();

    test_pixfmt_yuv_desc_all();
    test_pixfmt_yuv_queries();
    test_pixfmt_yuv_framesize();
    test_pixfmt_yuv_drm();
    test_pixfmt_yuv_common_fmt();

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
