/**
 * @copyright: Copyright (c) Rockchip Electronics Co., Ltd. 2026-. All rights reserved.
 * @brief:     YUV format descriptor validation and query tests
 * @author:    vance.wu@rock-chips.com
 * @create:    2026-05-16
 *
 * Included by test_pixfmt.c — relies on g_test_passed/g_test_failed/TEST_ASSERT
 * from test_pixfmt_common.h.
 *
 * NOTE: pixfmt_cvt_impl_y2y is not yet implemented, so YUV<->YUV conversion
 *       via pixfmt_cvt_exec is skipped for now.
 */

/* ============ YUV descriptor validation helpers ============ */

static void pixfmt_yuv_check_sampling(pixfmt_e fmt, pixfmt_yuv_sampling_e exp_sampling,
                                      int exp_h_sub, int exp_v_sub)
{
    int h_sub = 0, v_sub = 0;
    int ret = pixfmt_get_chroma_subsampling(fmt, &h_sub, &v_sub);
    TEST_ASSERT(ret == 0, "%s subsampling query OK", pixfmt_short_name(fmt));
    TEST_ASSERT(h_sub == exp_h_sub && v_sub == exp_v_sub,
        "%s subsampling: h=%d v=%d (expect h=%d v=%d)",
        pixfmt_short_name(fmt), h_sub, v_sub, exp_h_sub, exp_v_sub);
}

static void pixfmt_yuv_check_planes(pixfmt_e fmt, int exp_nb)
{
    int nb = pixfmt_nb_planes(fmt);
    TEST_ASSERT(nb == exp_nb, "%s nb_planes=%d (expect %d)", pixfmt_short_name(fmt), nb, exp_nb);
}

static void pixfmt_yuv_check_bpp_depth(pixfmt_e fmt, int exp_bpp, int exp_depth, int exp_comps)
{
    const pixfmt_attr_s *a = pixfmt_get_attr(fmt);
    TEST_ASSERT(a->bpp == exp_bpp, "%s bpp=%d (expect %d)", pixfmt_short_name(fmt), a->bpp, exp_bpp);
    if (exp_depth > 0)
        TEST_ASSERT(a->depth == exp_depth, "%s depth=%d (expect %d)", pixfmt_short_name(fmt), a->depth, exp_depth);
    if (exp_comps > 0)
        TEST_ASSERT(a->nb_comps == exp_comps, "%s nb_comps=%d (expect %d)", pixfmt_short_name(fmt), a->nb_comps, exp_comps);
}

/* ============ cover ALL YUV format descriptors ============ */
static void test_pixfmt_yuv_desc_all(void)
{
    printf("\n=== Test: All YUV Format Descriptors ===\n");

    /* --- YUV444 Interleaved --- */
    pixfmt_yuv_check_bpp_depth(PIXFMT_YUV444I_VU24,  24, 8, 3);
    pixfmt_yuv_check_bpp_depth(PIXFMT_YUV444I_VU30,  30, 10, 3);
    pixfmt_yuv_check_bpp_depth(PIXFMT_YUV444I_XV30,  32, 10, 3);
    pixfmt_yuv_check_bpp_depth(PIXFMT_YUV444I_10LSB, 48, 10, 3);
    pixfmt_yuv_check_sampling(PIXFMT_YUV444I_VU24,  PIXFMT_YUV_SAMPLING_444, 1, 1);
    pixfmt_yuv_check_sampling(PIXFMT_YUV444I_10LSB, PIXFMT_YUV_SAMPLING_444, 1, 1);
    pixfmt_yuv_check_planes(PIXFMT_YUV444I_VU24, 1);

    const pixfmt_attr_s *a_vu30 = pixfmt_get_attr(PIXFMT_YUV444I_VU30);
    TEST_ASSERT(a_vu30->is_bitpacked, "VU30 is bitpacked");
    const pixfmt_attr_s *a_xv30 = pixfmt_get_attr(PIXFMT_YUV444I_XV30);
    TEST_ASSERT(a_xv30->padding_pos == PIXFMT_PADDING_AT_MSB, "XV30 padding at MSB");
    const pixfmt_attr_s *a_yuv444i10l = pixfmt_get_attr(PIXFMT_YUV444I_10LSB);
    TEST_ASSERT(a_yuv444i10l->padding_pos == PIXFMT_PADDING_AT_MSB, "YUV444I_10LSB padding at MSB");
    TEST_ASSERT(!a_yuv444i10l->is_bitpacked, "YUV444I_10LSB is not bitpacked");

    /* --- YUV444 Planar --- */
    pixfmt_yuv_check_bpp_depth(PIXFMT_YUV444P_YU24,  24, 8, 3);
    pixfmt_yuv_check_bpp_depth(PIXFMT_YUV444P_YV24,  24, 8, 3);
    pixfmt_yuv_check_bpp_depth(PIXFMT_YUV444P_10LSB, 48, 10, 3);
    pixfmt_yuv_check_sampling(PIXFMT_YUV444P_YU24,  PIXFMT_YUV_SAMPLING_444, 1, 1);
    pixfmt_yuv_check_sampling(PIXFMT_YUV444P_YV24,  PIXFMT_YUV_SAMPLING_444, 1, 1);
    pixfmt_yuv_check_planes(PIXFMT_YUV444P_YU24, 3);

    /* --- YUV444 Semi-Planar --- */
    pixfmt_yuv_check_bpp_depth(PIXFMT_YUV444SP_NV24,  24, 8, 3);
    pixfmt_yuv_check_bpp_depth(PIXFMT_YUV444SP_NV42,  24, 8, 3);
    pixfmt_yuv_check_bpp_depth(PIXFMT_YUV444SP_NV30,  30, 10, 3);
    pixfmt_yuv_check_bpp_depth(PIXFMT_YUV444SP_10LSB, 48, 10, 3);
    pixfmt_yuv_check_planes(PIXFMT_YUV444SP_NV24, 2);

    const pixfmt_attr_s *a_nv30 = pixfmt_get_attr(PIXFMT_YUV444SP_NV30);
    TEST_ASSERT(a_nv30->is_bitpacked, "NV30 is bitpacked");

    /* --- YUV422 Interleaved --- */
    pixfmt_yuv_check_bpp_depth(PIXFMT_YUV422I_YUYV, 16, 8, 3);
    pixfmt_yuv_check_bpp_depth(PIXFMT_YUV422I_YVYU, 16, 8, 3);
    pixfmt_yuv_check_bpp_depth(PIXFMT_YUV422I_UYVY, 16, 8, 3);
    pixfmt_yuv_check_bpp_depth(PIXFMT_YUV422I_VYUY, 16, 8, 3);
    pixfmt_yuv_check_bpp_depth(PIXFMT_YUV422I_Y210, 32, 10, 3);
    pixfmt_yuv_check_bpp_depth(PIXFMT_YUV422I_Y212, 32, 12, 3);
    pixfmt_yuv_check_bpp_depth(PIXFMT_YUV422I_Y216, 32, 16, 3);
    pixfmt_yuv_check_sampling(PIXFMT_YUV422I_YUYV, PIXFMT_YUV_SAMPLING_422, 2, 1);
    pixfmt_yuv_check_planes(PIXFMT_YUV422I_YUYV, 1);

    const pixfmt_attr_s *a_y210 = pixfmt_get_attr(PIXFMT_YUV422I_Y210);
    TEST_ASSERT(a_y210->padding_pos == PIXFMT_PADDING_AT_LSB, "Y210 padding at LSB");
    const pixfmt_attr_s *a_y212 = pixfmt_get_attr(PIXFMT_YUV422I_Y212);
    TEST_ASSERT(a_y212->padding_pos == PIXFMT_PADDING_AT_LSB, "Y212 padding at LSB");

    /* --- YUV422 Planar --- */
    pixfmt_yuv_check_bpp_depth(PIXFMT_YUV422P_YU16,  16, 8, 3);
    pixfmt_yuv_check_bpp_depth(PIXFMT_YUV422P_YV16,  16, 8, 3);
    pixfmt_yuv_check_bpp_depth(PIXFMT_YUV422P_10LSB, 32, 10, 3);
    pixfmt_yuv_check_sampling(PIXFMT_YUV422P_YU16, PIXFMT_YUV_SAMPLING_422, 2, 1);
    pixfmt_yuv_check_planes(PIXFMT_YUV422P_YU16, 3);

    /* --- YUV422 Semi-Planar --- */
    pixfmt_yuv_check_bpp_depth(PIXFMT_YUV422SP_NV16,  16, 8, 3);
    pixfmt_yuv_check_bpp_depth(PIXFMT_YUV422SP_NV61,  16, 8, 3);
    pixfmt_yuv_check_bpp_depth(PIXFMT_YUV422SP_NV20,  20, 10, 3);
    pixfmt_yuv_check_bpp_depth(PIXFMT_YUV422SP_10LSB, 32, 10, 3);
    pixfmt_yuv_check_planes(PIXFMT_YUV422SP_NV16, 2);

    const pixfmt_attr_s *a_nv20 = pixfmt_get_attr(PIXFMT_YUV422SP_NV20);
    TEST_ASSERT(a_nv20->is_bitpacked, "NV20 is bitpacked");

    /* --- YUV420 Planar --- */
    pixfmt_yuv_check_bpp_depth(PIXFMT_YUV420P_YU12,  12, 8, 3);
    pixfmt_yuv_check_bpp_depth(PIXFMT_YUV420P_YV12,  12, 8, 3);
    pixfmt_yuv_check_bpp_depth(PIXFMT_YUV420P_10LSB, 24, 10, 3);
    pixfmt_yuv_check_sampling(PIXFMT_YUV420P_YU12, PIXFMT_YUV_SAMPLING_420, 2, 2);
    pixfmt_yuv_check_planes(PIXFMT_YUV420P_YU12, 3);

    /* --- YUV420 Semi-Planar --- */
    pixfmt_yuv_check_bpp_depth(PIXFMT_YUV420SP_NV12,  12, 8, 3);
    pixfmt_yuv_check_bpp_depth(PIXFMT_YUV420SP_NV21,  12, 8, 3);
    pixfmt_yuv_check_bpp_depth(PIXFMT_YUV420SP_NV15,  15, 10, 3);
    pixfmt_yuv_check_bpp_depth(PIXFMT_YUV420SP_10LSB, 24, 10, 3);
    pixfmt_yuv_check_planes(PIXFMT_YUV420SP_NV12, 2);

    const pixfmt_attr_s *a_nv15 = pixfmt_get_attr(PIXFMT_YUV420SP_NV15);
    TEST_ASSERT(a_nv15->is_bitpacked, "NV15 is bitpacked");

    /* --- YUV411 / 410 Planar --- */
    pixfmt_yuv_check_bpp_depth(PIXFMT_YUV411P_YU11, 12, 8, 3);
    pixfmt_yuv_check_bpp_depth(PIXFMT_YUV411P_YV11, 12, 8, 3);
    pixfmt_yuv_check_bpp_depth(PIXFMT_YUV410P_YUV9, 9,  8, 3);
    pixfmt_yuv_check_bpp_depth(PIXFMT_YUV410P_YVU9, 9,  8, 3);
    pixfmt_yuv_check_sampling(PIXFMT_YUV411P_YU11, PIXFMT_YUV_SAMPLING_411, 4, 1);
    pixfmt_yuv_check_sampling(PIXFMT_YUV410P_YUV9, PIXFMT_YUV_SAMPLING_410, 4, 4);
    pixfmt_yuv_check_planes(PIXFMT_YUV411P_YU11, 3);

    /* --- YUV400 (Grayscale) --- */
    struct {
        pixfmt_e fmt; int bpp; int depth; bool is_bp;
    } y400_fmts[] = {
        {PIXFMT_YUV400_R1,  1,  1, true},
        {PIXFMT_YUV400_R2,  2,  2, true},
        {PIXFMT_YUV400_R4,  4,  4, true},
        {PIXFMT_YUV400_R8,  8,  8, false},
        {PIXFMT_YUV400_R10, 16, 10, false},
        {PIXFMT_YUV400_R12, 16, 12, false},
        {PIXFMT_YUV400_R16, 16, 16, false},
    };
    for (int i = 0; i < ARRAY_SIZE(y400_fmts); i++) {
        pixfmt_yuv_check_bpp_depth(y400_fmts[i].fmt, y400_fmts[i].bpp, y400_fmts[i].depth, 1);
        const pixfmt_attr_s *a = pixfmt_get_attr(y400_fmts[i].fmt);
        TEST_ASSERT(a->is_bitpacked == y400_fmts[i].is_bp,
            "%s is_bitpacked=%d (expect %d)", pixfmt_short_name(y400_fmts[i].fmt), a->is_bitpacked, y400_fmts[i].is_bp);
        pixfmt_yuv_check_planes(y400_fmts[i].fmt, 1);
    }

    const pixfmt_attr_s *a_r10 = pixfmt_get_attr(PIXFMT_YUV400_R10);
    TEST_ASSERT(a_r10->padding_pos == PIXFMT_PADDING_AT_MSB, "YUV400_R10 padding at MSB");

    /* --- YUV Tile --- */
    pixfmt_yuv_check_bpp_depth(PIXFMT_YUV444SP_TILE4x4, 24, 8, 3);
    pixfmt_yuv_check_bpp_depth(PIXFMT_YUV422SP_TILE4x4, 16, 8, 3);
    pixfmt_yuv_check_bpp_depth(PIXFMT_YUV420SP_TILE4x4, 12, 8, 3);

    TEST_ASSERT(pixfmt_is_tile(PIXFMT_YUV444SP_TILE4x4), "YUV444 TILE4x4 is tile");
    TEST_ASSERT(!pixfmt_is_tile(PIXFMT_YUV444SP_NV24), "NV24 is not tile");

    int tw = 0, th = 0;
    pixfmt_get_tile_size(PIXFMT_YUV420SP_TILE4x4, &tw, &th);
    TEST_ASSERT(tw == 4 && th == 4, "TILE4x4 tile size should be 4x4, got %dx%d", tw, th);
}

/* ============ YUV name-based & type queries ============ */
static void test_pixfmt_yuv_queries(void)
{
    printf("\n=== Test: YUV Format Queries ===\n");

    TEST_ASSERT(pixfmt_is_yuv(PIXFMT_YUV420SP_NV12), "NV12 is YUV");
    TEST_ASSERT(!pixfmt_is_rgb(PIXFMT_YUV420SP_NV12), "NV12 is not RGB");

    /* uv_order (YUV order) */
    TEST_ASSERT(pixfmt_is_uv_order(PIXFMT_YUV420P_YU12), "YU12 is YUV order");
    TEST_ASSERT(!pixfmt_is_uv_order(PIXFMT_YUV420P_YV12), "YV12 is not YUV order");

    /* nb_planes key regression */
    pixfmt_yuv_check_planes(PIXFMT_YUV422I_YUYV, 1);
    pixfmt_yuv_check_planes(PIXFMT_YUV422SP_NV16, 2);
    pixfmt_yuv_check_planes(PIXFMT_YUV422P_YU16, 3);
    pixfmt_yuv_check_planes(PIXFMT_YUV400_R8, 1);
    pixfmt_yuv_check_planes(PIXFMT_YUV444SP_TILE4x4, 1);

    /* tile flag */
    TEST_ASSERT(!pixfmt_is_tile(PIXFMT_YUV420SP_NV12), "NV12 is not tile");
    TEST_ASSERT(pixfmt_is_tile(PIXFMT_YUV420SP_TILE4x4), "TILE4x4 is tile");
}

/* ============ frame size / pitch regression ============ */
static void test_pixfmt_yuv_framesize(void)
{
    printf("\n=== Test: YUV Frame Size Calculations ===\n");

    const int W = 1920, H = 1080;

    struct {
        pixfmt_e fmt; size_t expect_size;
    } cases[] = {
        {PIXFMT_YUV420P_YU12,  (size_t)W * H * 3 / 2},
        {PIXFMT_YUV420SP_NV12, (size_t)W * H * 3 / 2},
        {PIXFMT_YUV422P_YU16,  (size_t)W * H * 2},
        {PIXFMT_YUV422I_YUYV,  (size_t)W * H * 2},
        {PIXFMT_YUV444P_YU24,  (size_t)W * H * 3},
        {PIXFMT_YUV400_R8,     (size_t)W * H},
    };
    for (int i = 0; i < ARRAY_SIZE(cases); i++) {
        pixfmt_frame_s frame = {0};
        frame.fmt = cases[i].fmt;
        frame.wid = W;
        frame.hgt = H;
        bool ok = pixfmt_frame_fill(&frame);
        TEST_ASSERT(ok, "%s frame_fill OK", pixfmt_short_name(cases[i].fmt));
        TEST_ASSERT(frame.size >= cases[i].expect_size,
            "%s frame size %zu >= %zu", pixfmt_short_name(cases[i].fmt), frame.size, cases[i].expect_size);
    }

    /* pitch checks */
    int pitches[3] = {0};
    pixfmt_frame_get_min_pitches(PIXFMT_YUV420P_YU12, 1920, pitches);
    TEST_ASSERT(pitches[0] == 1920, "YU12 luma pitch=1920");
    TEST_ASSERT(pitches[1] == 960, "YU12 chroma pitch=960");

    pixfmt_frame_get_min_pitches(PIXFMT_YUV420SP_NV12, 1920, pitches);
    TEST_ASSERT(pitches[0] == 1920, "NV12 luma pitch=1920");
    TEST_ASSERT(pitches[1] == 1920, "NV12 chroma pitch=1920 (interleaved UV)");

    /* plane size checks */
    pixfmt_frame_s frame = {.fmt = PIXFMT_YUV420P_YU12, .wid = 1920, .hgt = 1080};
    pixfmt_frame_fill(&frame);
    size_t psizes[3] = {0};
    size_t total = pixfmt_frame_get_size(&frame, -1, psizes);
    TEST_ASSERT(psizes[0] == (size_t)1920 * 1080, "YU12 plane0 luma size");
    TEST_ASSERT(psizes[1] == (size_t)960 * 540, "YU12 plane1 U size");
    TEST_ASSERT(psizes[2] == psizes[1], "YU12 plane2 V size == U size");
    TEST_ASSERT(total == psizes[0] + psizes[1] + psizes[2], "YU12 total == sum of planes");
}

/* ============ DRM FourCC round-trip ============ */
static void test_pixfmt_yuv_drm(void)
{
    printf("\n=== Test: YUV DRM FourCC Round-Trip ===\n");

    pixfmt_e drm_yuv_fmts[] = {
        /* 444 */
        PIXFMT_YUV444I_VU24, PIXFMT_YUV444I_VU30, PIXFMT_YUV444I_XV30,
        PIXFMT_YUV444P_YU24, PIXFMT_YUV444P_YV24,
        PIXFMT_YUV444SP_NV24, PIXFMT_YUV444SP_NV42, PIXFMT_YUV444SP_NV30,
        /* 422 */
        PIXFMT_YUV422I_YUYV, PIXFMT_YUV422I_YVYU, PIXFMT_YUV422I_UYVY, PIXFMT_YUV422I_VYUY,
        PIXFMT_YUV422I_Y210, PIXFMT_YUV422I_Y212, PIXFMT_YUV422I_Y216,
        PIXFMT_YUV422P_YU16, PIXFMT_YUV422P_YV16,
        PIXFMT_YUV422SP_NV16, PIXFMT_YUV422SP_NV61, PIXFMT_YUV422SP_NV20,
        /* 420 */
        PIXFMT_YUV420P_YU12, PIXFMT_YUV420P_YV12,
        PIXFMT_YUV420SP_NV12, PIXFMT_YUV420SP_NV21, PIXFMT_YUV420SP_NV15,
        /* 411 / 410 */
        PIXFMT_YUV411P_YU11, PIXFMT_YUV411P_YV11,
        PIXFMT_YUV410P_YUV9, PIXFMT_YUV410P_YVU9,
        /* YUV400 */
        PIXFMT_YUV400_R1, PIXFMT_YUV400_R2, PIXFMT_YUV400_R4,
        PIXFMT_YUV400_R8, PIXFMT_YUV400_R10, PIXFMT_YUV400_R12, PIXFMT_YUV400_R16,
    };
    for (int i = 0; i < ARRAY_SIZE(drm_yuv_fmts); i++) {
        uint32_t fourcc = pixfmt_to_drm_fourcc(drm_yuv_fmts[i]);
        TEST_ASSERT(fourcc != 0, "%s drm_fourcc non-zero", pixfmt_short_name(drm_yuv_fmts[i]));
        pixfmt_e back = pixfmt_from_drm_fourcc(fourcc);
        TEST_ASSERT(back == drm_yuv_fmts[i], "%s fourcc round-trip", pixfmt_short_name(drm_yuv_fmts[i]));
    }
}

/* ============ common format selection quick smoke ============ */
static void test_pixfmt_yuv_common_fmt(void)
{
    printf("\n=== Test: YUV Common Format ===\n");

    /* 8bit 444 */
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_YUV444P_YU24, PIXFMT_LAYOUT_PLANAR, false) == PIXFMT_YUV444P_YU24,
        "YU24 planar common is YU24");
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_YUV444P_YV24, PIXFMT_LAYOUT_PLANAR, false) == PIXFMT_YUV444P_YU24,
        "YV24 planar common is YU24");
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_YUV444SP_NV24, PIXFMT_LAYOUT_SEMIPLANAR, false) == PIXFMT_YUV444SP_NV24,
        "NV24 semi common is NV24");

    /* 10bit 444 */
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_YUV444I_10LSB, PIXFMT_LAYOUT_INTERLEAVED, false) == PIXFMT_YUV444I_10LSB,
        "YUV444I_10LSB interleaved common is YUV444I_10LSB");
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_YUV444SP_NV30, PIXFMT_LAYOUT_SEMIPLANAR, false) == PIXFMT_YUV444SP_10LSB,
        "NV30 semi common is YUV444SP_10LSB");

    /* 8bit 422 */
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_YUV422I_YUYV, PIXFMT_LAYOUT_INTERLEAVED, false) == PIXFMT_YUV422I_YUYV,
        "YUYV interleaved common is YUYV");
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_YUV422P_YU16, PIXFMT_LAYOUT_PLANAR, false) == PIXFMT_YUV422P_YU16,
        "YU16 planar common is YU16");
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_YUV422SP_NV16, PIXFMT_LAYOUT_SEMIPLANAR, false) == PIXFMT_YUV422SP_NV16,
        "NV16 semi common is NV16");

    /* 10bit 422 */
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_YUV422SP_NV20, PIXFMT_LAYOUT_SEMIPLANAR, false) == PIXFMT_YUV422SP_10LSB,
        "NV20 semi common is YUV422SP_10LSB");

    /* 8bit 420 */
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_YUV420P_YU12, PIXFMT_LAYOUT_PLANAR, false) == PIXFMT_YUV420P_YU12,
        "YU12 planar common is YU12");
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_YUV420SP_NV12, PIXFMT_LAYOUT_SEMIPLANAR, false) == PIXFMT_YUV420SP_NV12,
        "NV12 semi common is NV12");

    /* 10bit 420 */
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_YUV420SP_NV15, PIXFMT_LAYOUT_SEMIPLANAR, false) == PIXFMT_YUV420SP_10LSB,
        "NV15 semi common is YUV420SP_10LSB");

    /* tile -> semiplanar */
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_YUV420SP_TILE4x4, PIXFMT_LAYOUT_SEMIPLANAR, false) == PIXFMT_YUV420SP_NV12,
        "TILE4x4 semi common is NV12");

    /* 420 interleaved should be invalid */
    TEST_ASSERT(pixfmt_get_common_fmt(PIXFMT_YUV420P_YU12, PIXFMT_LAYOUT_INTERLEAVED, false) == PIXFMT_INVALID,
        "YU12 interleaved common is INVALID");
}
