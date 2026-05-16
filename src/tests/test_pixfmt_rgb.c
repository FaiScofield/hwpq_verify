/**
 * @copyright: Copyright (c) Rockchip Electronics Co., Ltd. 2026-. All rights reserved.
 * @brief:     RGB format descriptor validation and R2R conversion tests
 * @author:    vance.wu@rock-chips.com
 * @create:    2026-04-22
 *
 * Included by test_pixfmt.c — relies on g_test_passed/g_test_failed/TEST_ASSERT
 * from test_pixfmt_common.h.
 *
 * NOTE: pixfmt_frame_fill requires wid > 4 && hgt > 2, so all test frames
 *       use w >= 8, h >= 4.
 */

/* ============ validate comp_bits for a specific RGB format ============ */
static void pixfmt_rgb_check_comp_bits(pixfmt_e fmt, uint8_t eb_r, uint8_t eb_g, uint8_t eb_b, uint8_t eb_a)
{
    uint8_t r, g, b, a;
    pixfmt_get_channel_bits(fmt, &r, &g, &b, &a);
    TEST_ASSERT(r == eb_r && g == eb_g && b == eb_b && a == eb_a,
        "%s comp_bits: R=%d G=%d B=%d A=%d (expect R=%d G=%d B=%d A=%d)",
        pixfmt_short_name(fmt), r, g, b, a, eb_r, eb_g, eb_b, eb_a);
}

/* ============ cover EVERY registered RGB format descriptor ============ */
static void test_pixfmt_rgb_desc_all(void)
{
    printf("\n=== Test: All RGB Format Descriptors ===\n");

    /* --- 8bit unpacked --- */
    pixfmt_rgb_check_comp_bits(PIXFMT_RGB888,   8, 8, 8, 0);
    pixfmt_rgb_check_comp_bits(PIXFMT_BGR888,   8, 8, 8, 0);
    pixfmt_rgb_check_comp_bits(PIXFMT_RGBA8888, 8, 8, 8, 8);
    pixfmt_rgb_check_comp_bits(PIXFMT_BGRA8888, 8, 8, 8, 8);
    pixfmt_rgb_check_comp_bits(PIXFMT_ARGB8888, 8, 8, 8, 8);
    pixfmt_rgb_check_comp_bits(PIXFMT_ABGR8888, 8, 8, 8, 8);

    TEST_ASSERT(pixfmt_has_alpha(PIXFMT_RGBA8888), "RGBA8888 should have alpha");
    TEST_ASSERT(!pixfmt_has_alpha(PIXFMT_RGB888), "RGB888 should not have alpha");
    TEST_ASSERT(!pixfmt_is_bgr_order(PIXFMT_RGB888), "RGB888 is RGB order");
    TEST_ASSERT(pixfmt_is_bgr_order(PIXFMT_BGR888), "BGR888 is BGR order");

    /* --- 10bit LSB (unpacked, padding at MSB) --- */
    pixfmt_rgb_check_comp_bits(PIXFMT_RGB10Lsb,  10, 10, 10, 0);
    pixfmt_rgb_check_comp_bits(PIXFMT_RGBA10Lsb, 10, 10, 10, 10);

    const pixfmt_attr_s *a10l = pixfmt_get_attr(PIXFMT_RGB10Lsb);
    TEST_ASSERT(a10l->padding_pos == PIXFMT_PADDING_AT_MSB, "RGB10Lsb padding at MSB");
    TEST_ASSERT(!a10l->is_bitpacked, "RGB10Lsb is not bitpacked");
    TEST_ASSERT(a10l->bpp == 48, "RGB10Lsb bpp=48");
    TEST_ASSERT(a10l->depth == 10, "RGB10Lsb depth=10");

    const pixfmt_attr_s *a10la = pixfmt_get_attr(PIXFMT_RGBA10Lsb);
    TEST_ASSERT(a10la->padding_pos == PIXFMT_PADDING_AT_MSB, "RGBA10Lsb padding at MSB");
    TEST_ASSERT(!a10la->is_bitpacked, "RGBA10Lsb is not bitpacked");
    TEST_ASSERT(a10la->bpp == 64, "RGBA10Lsb bpp=64");

    /* --- 8bpp bitpacked --- */
    pixfmt_rgb_check_comp_bits(PIXFMT_RGB332, 3, 3, 2, 0);
    pixfmt_rgb_check_comp_bits(PIXFMT_BGR233, 3, 3, 2, 0);

    const pixfmt_attr_s *a332 = pixfmt_get_attr(PIXFMT_RGB332);
    TEST_ASSERT(a332->is_bitpacked, "RGB332 is bitpacked");
    TEST_ASSERT(a332->bpp == 8, "RGB332 bpp=8");
    TEST_ASSERT(a332->depth == 3, "RGB332 depth=3");

    /* --- 16bpp bitpacked --- */
    pixfmt_rgb_check_comp_bits(PIXFMT_RGB565,   5, 6, 5, 0);
    pixfmt_rgb_check_comp_bits(PIXFMT_BGR565,   5, 6, 5, 0);
    pixfmt_rgb_check_comp_bits(PIXFMT_RGBA5551, 5, 5, 5, 1);
    pixfmt_rgb_check_comp_bits(PIXFMT_ABGR1555, 5, 5, 5, 1);
    pixfmt_rgb_check_comp_bits(PIXFMT_RGBA4444, 4, 4, 4, 4);
    pixfmt_rgb_check_comp_bits(PIXFMT_ABGR4444, 4, 4, 4, 4);

    const pixfmt_attr_s *a565 = pixfmt_get_attr(PIXFMT_RGB565);
    TEST_ASSERT(a565->is_bitpacked, "RGB565 is bitpacked");
    TEST_ASSERT(a565->bpp == 16, "RGB565 bpp=16");

    /* --- 32bpp 10bit bitpacked --- */
    pixfmt_rgb_check_comp_bits(PIXFMT_RGBA1010102, 10, 10, 10, 2);
    pixfmt_rgb_check_comp_bits(PIXFMT_ABGR2101010, 10, 10, 10, 2);

    const pixfmt_attr_s *a1010 = pixfmt_get_attr(PIXFMT_RGBA1010102);
    TEST_ASSERT(a1010->is_bitpacked, "RGBA1010102 is bitpacked");
    TEST_ASSERT(a1010->bpp == 32, "RGBA1010102 bpp=32");
    TEST_ASSERT(a1010->depth == 10, "RGBA1010102 depth=10");

    /* --- name-based lookups --- */
    TEST_ASSERT(pixfmt_get_attr_by_name("rgb888") != NULL, "find 'rgb888' by full_name");
    TEST_ASSERT(pixfmt_get_attr_by_name("rgb24") != NULL, "find 'rgb24' by short_name");
    TEST_ASSERT(pixfmt_get_attr_by_name("rgb")   != NULL, "find 'rgb' by alias");

    /* --- DRM FourCC round-trip (non-10LSB formats) --- */
    pixfmt_e drm_rgb_fmts[] = {
        PIXFMT_RGB888, PIXFMT_BGR888,
        PIXFMT_RGBA8888, PIXFMT_BGRA8888, PIXFMT_ARGB8888, PIXFMT_ABGR8888,
        PIXFMT_RGB332, PIXFMT_BGR233,
        PIXFMT_RGB565, PIXFMT_BGR565,
        PIXFMT_RGBA5551, PIXFMT_ABGR1555,
        PIXFMT_RGBA4444, PIXFMT_ABGR4444,
        PIXFMT_RGBA1010102, PIXFMT_ABGR2101010,
    };
    for (int i = 0; i < ARRAY_SIZE(drm_rgb_fmts); i++) {
        uint32_t fourcc = pixfmt_to_drm_fourcc(drm_rgb_fmts[i]);
        TEST_ASSERT(fourcc != 0, "%s drm_fourcc should be non-zero", pixfmt_short_name(drm_rgb_fmts[i]));
        pixfmt_e back = pixfmt_from_drm_fourcc(fourcc);
        TEST_ASSERT(back == drm_rgb_fmts[i], "%s drm_fourcc round-trip", pixfmt_short_name(drm_rgb_fmts[i]));
    }
}

/* ============ RGB-to-RGB conversion test helpers ============ */

#define TEST_R2R_W  8
#define TEST_R2R_H  4
#define TEST_R2R_BUF_SIZE 2048

static void pixfmt_setup_frame(pixfmt_frame_s *f, pixfmt_e fmt, int w, int h, void *buf, size_t buf_sz)
{
    memset(f, 0, sizeof(*f));
    f->fmt = fmt;
    f->clrspc = PIXFMT_CLRSPC_RGB_FULL;
    f->wid = w;
    f->hgt = h;
    f->vwid = w;
    f->vhgt = h;

    int pitches[3] = {0};
    pixfmt_frame_get_min_pitches(fmt, w, pitches);
    f->pitch = pitches[0];
    f->addr = buf;
    f->size = buf_sz;
}

/* fill rgb888 src with known ramp: pixel(x,y) = { (x*17)&0xFF, (y*37)&0xFF, 0x80 } */
static void fill_rgb888_ramp(uint8_t *buf, int w, int h, int pitch)
{
    for (int y = 0; y < h; y++) {
        uint8_t *row = buf + y * pitch;
        for (int x = 0; x < w; x++) {
            row[x * 3 + 0] = (uint8_t)((x * 17) & 0xFF);
            row[x * 3 + 1] = (uint8_t)((y * 37) & 0xFF);
            row[x * 3 + 2] = 0x80;
        }
    }
}

/* verify dst matches rgb888 ramp (allow small rounding error) */
static void verify_rgb888_ramp(const uint8_t *buf, int w, int h, int pitch, const char *tag, int tolerance)
{
    for (int y = 0; y < h; y++) {
        const uint8_t *row = buf + y * pitch;
        for (int x = 0; x < w; x++) {
            int exp_r = (x * 17) & 0xFF;
            int exp_g = (y * 37) & 0xFF;
            int exp_b = 0x80;
            int got_r = row[x * 3 + 0];
            int got_g = row[x * 3 + 1];
            int got_b = row[x * 3 + 2];
            TEST_ASSERT(abs(got_r - exp_r) <= tolerance &&
                        abs(got_g - exp_g) <= tolerance &&
                        abs(got_b - exp_b) <= tolerance,
                "%s pixel(%d,%d): got RGB=%d/%d/%d expect ~%d/%d/%d",
                tag, x, y, got_r, got_g, got_b, exp_r, exp_g, exp_b);
        }
    }
}

static void test_pixfmt_rgb_cvt(void)
{
    printf("\n=== Test: RGB-to-RGB Conversion ===\n");

    uint8_t src_buf[TEST_R2R_BUF_SIZE];
    uint8_t dst_buf[TEST_R2R_BUF_SIZE];
    int w = TEST_R2R_W, h = TEST_R2R_H;

    /* ----- 1. Same format, different pitch (copy) ----- */
    {
        pixfmt_frame_s src, dst;
        memset(src_buf, 0, sizeof(src_buf));
        memset(dst_buf, 0, sizeof(dst_buf));
        pixfmt_setup_frame(&src, PIXFMT_RGB888, w, h, src_buf, sizeof(src_buf));
        src.pitch = w * 4; // extra padding per row
        fill_rgb888_ramp(src_buf, w, h, src.pitch);

        pixfmt_setup_frame(&dst, PIXFMT_RGB888, w, h, dst_buf, sizeof(dst_buf));
        dst.pitch = w * 3; // normal pitch

        int ret = pixfmt_cvt_exec(&src, &dst);
        TEST_ASSERT(ret == 0, "R2R same-format copy OK");
        verify_rgb888_ramp(dst_buf, w, h, dst.pitch, "same-fmt-copy", 0);
    }

    /* ----- 2. RGB888 -> BGR888 (channel swap) ----- */
    {
        pixfmt_frame_s src, dst;
        memset(src_buf, 0, sizeof(src_buf));
        memset(dst_buf, 0, sizeof(dst_buf));
        pixfmt_setup_frame(&src, PIXFMT_RGB888, w, h, src_buf, sizeof(src_buf));
        fill_rgb888_ramp(src_buf, w, h, src.pitch);

        pixfmt_setup_frame(&dst, PIXFMT_BGR888, w, h, dst_buf, sizeof(dst_buf));

        int ret = pixfmt_cvt_exec(&src, &dst);
        TEST_ASSERT(ret == 0, "RGB888->BGR888 cvt OK");

        for (int y = 0; y < h; y++) {
            const uint8_t *sr = src_buf + y * src.pitch;
            const uint8_t *dr = dst_buf + y * dst.pitch;
            for (int x = 0; x < w; x++) {
                TEST_ASSERT(dr[x*3+0] == sr[x*3+2], "BGR[%d,%d] B==src.R", x, y);
                TEST_ASSERT(dr[x*3+1] == sr[x*3+1], "BGR[%d,%d] G==src.G", x, y);
                TEST_ASSERT(dr[x*3+2] == sr[x*3+0], "BGR[%d,%d] R==src.B", x, y);
            }
        }
    }

    /* ----- 3. RGB888 -> RGB565 -> RGB888 roundtrip ----- */
    {
        pixfmt_frame_s src, dst;
        memset(src_buf, 0, sizeof(src_buf));
        memset(dst_buf, 0, sizeof(dst_buf));
        pixfmt_setup_frame(&src, PIXFMT_RGB888, w, h, src_buf, sizeof(src_buf));
        fill_rgb888_ramp(src_buf, w, h, src.pitch);

        pixfmt_setup_frame(&dst, PIXFMT_RGB565, w, h, dst_buf, sizeof(dst_buf));

        int ret = pixfmt_cvt_exec(&src, &dst);
        TEST_ASSERT(ret == 0, "RGB888->RGB565 cvt OK");

        uint8_t back_buf[TEST_R2R_BUF_SIZE];
        pixfmt_frame_s back;
        memset(back_buf, 0, sizeof(back_buf));
        pixfmt_setup_frame(&src, PIXFMT_RGB565, w, h, dst_buf, sizeof(dst_buf));
        pixfmt_setup_frame(&back, PIXFMT_RGB888, w, h, back_buf, sizeof(back_buf));

        ret = pixfmt_cvt_exec(&src, &back);
        TEST_ASSERT(ret == 0, "RGB565->RGB888 cvt OK");

        verify_rgb888_ramp(back_buf, w, h, back.pitch, "565-rt", 8);
    }

    /* ----- 4. RGBA8888 -> ABGR8888 (full reorder) ----- */
    {
        pixfmt_frame_s src, dst;
        memset(src_buf, 0, sizeof(src_buf));
        memset(dst_buf, 0, sizeof(dst_buf));
        pixfmt_setup_frame(&src, PIXFMT_RGBA8888, w, h, src_buf, sizeof(src_buf));
        src_buf[0]=0x11; src_buf[1]=0x22; src_buf[2]=0x33; src_buf[3]=0xAA;
        src_buf[4]=0xCC; src_buf[5]=0xDD; src_buf[6]=0xEE; src_buf[7]=0xFF;

        pixfmt_setup_frame(&dst, PIXFMT_ABGR8888, w, h, dst_buf, sizeof(dst_buf));

        int ret = pixfmt_cvt_exec(&src, &dst);
        TEST_ASSERT(ret == 0, "RGBA->ABGR cvt OK");

        TEST_ASSERT(dst_buf[0]==0xAA && dst_buf[1]==0x33 && dst_buf[2]==0x22 && dst_buf[3]==0x11,
            "p0 RGBA->ABGR: A=%02x B=%02x G=%02x R=%02x", dst_buf[0], dst_buf[1], dst_buf[2], dst_buf[3]);
        TEST_ASSERT(dst_buf[4]==0xFF && dst_buf[5]==0xEE && dst_buf[6]==0xDD && dst_buf[7]==0xCC,
            "p1 RGBA->ABGR: A=%02x B=%02x G=%02x R=%02x", dst_buf[4], dst_buf[5], dst_buf[6], dst_buf[7]);
    }

    /* ----- 5. RGB888 -> RGBA8888 (alpha fill=255) ----- */
    {
        pixfmt_frame_s src, dst;
        memset(src_buf, 0, sizeof(src_buf));
        memset(dst_buf, 0, sizeof(dst_buf));
        pixfmt_setup_frame(&src, PIXFMT_RGB888, w, h, src_buf, sizeof(src_buf));
        src_buf[0]=10; src_buf[1]=20; src_buf[2]=30;
        src_buf[3]=40; src_buf[4]=50; src_buf[5]=60;

        pixfmt_setup_frame(&dst, PIXFMT_RGBA8888, w, h, dst_buf, sizeof(dst_buf));

        int ret = pixfmt_cvt_exec(&src, &dst);
        TEST_ASSERT(ret == 0, "RGB->RGBA cvt OK");

        TEST_ASSERT(dst_buf[0]==10 && dst_buf[1]==20 && dst_buf[2]==30 && dst_buf[3]==255,
            "p0 RGB->RGBA: R=%d G=%d B=%d A=%d", dst_buf[0], dst_buf[1], dst_buf[2], dst_buf[3]);
        TEST_ASSERT(dst_buf[4]==40 && dst_buf[5]==50 && dst_buf[6]==60 && dst_buf[7]==255,
            "p1 RGB->RGBA: R=%d G=%d B=%d A=%d", dst_buf[4], dst_buf[5], dst_buf[6], dst_buf[7]);
    }

    /* ----- 6. RGBA8888 -> RGB888 (drop alpha) ----- */
    {
        pixfmt_frame_s src, dst;
        memset(src_buf, 0, sizeof(src_buf));
        memset(dst_buf, 0, sizeof(dst_buf));
        pixfmt_setup_frame(&src, PIXFMT_RGBA8888, w, h, src_buf, sizeof(src_buf));
        src_buf[0]=10; src_buf[1]=20; src_buf[2]=30; src_buf[3]=0xAA;
        src_buf[4]=40; src_buf[5]=50; src_buf[6]=60; src_buf[7]=0xBB;

        pixfmt_setup_frame(&dst, PIXFMT_RGB888, w, h, dst_buf, sizeof(dst_buf));

        int ret = pixfmt_cvt_exec(&src, &dst);
        TEST_ASSERT(ret == 0, "RGBA->RGB cvt OK");

        TEST_ASSERT(dst_buf[0]==10 && dst_buf[1]==20 && dst_buf[2]==30,
            "p0 RGBA->RGB: R=%d G=%d B=%d", dst_buf[0], dst_buf[1], dst_buf[2]);
        TEST_ASSERT(dst_buf[3]==40 && dst_buf[4]==50 && dst_buf[5]==60,
            "p1 RGBA->RGB: R=%d G=%d B=%d", dst_buf[3], dst_buf[4], dst_buf[5]);
    }
}
