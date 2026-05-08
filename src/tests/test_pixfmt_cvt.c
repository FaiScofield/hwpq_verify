
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