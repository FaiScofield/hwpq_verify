/**
 * @copyright Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @description: dci_verify_demo.c
 * @author: vance.wu@rock-chips.com
 * @create: 2025-09-15
 * @modify: 2026-05-26
 */

#ifdef __cplusplus
extern "C" {
#endif
#include "dci_api.h"
#include "sharp_full_api.h"
#include "sharp_lite_api.h"
#include "rockchip_post_csc.h"
#ifdef __cplusplus
}
#endif

#include "verify_com.h"
#include "verify_cmd_parser.h"
#include "verify_crc32.h"
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Fallback pix_fmt values used by the prebuilt DCI library. */
#ifndef PIX_YUV420P_10
#define PIX_YUV420P_10 0x1000f222
#endif
#ifndef PIX_YUV422P_10
#define PIX_YUV422P_10 0x10014242
#endif
#ifndef PIX_YUV444P_10
#define PIX_YUV444P_10 0x1001e442
#endif
#ifndef PIX_RGB101010
#define PIX_RGB101010 0x2001E000
#endif
#ifndef csc_simple_round
#define csc_simple_round(x, n) \
    (((x) + (1 << ((n) - 1)) + ((x) >> 31)) >> (n)) // right shift by n, round to nearest integer
#endif

struct cmd_config_addition_dci {
    int clahe_en;
    float clahe_clip_value;
    int clahe_local_ratio;
    float clahe_abld_ratio;
    int clahe_scd_thr_min;
    int clahe_scd_thr_max;
    int shp_type; // 0-off, 1-full, 2-lite
    int shp_peaking_gain;
};

#define SHP_OVERRIDE_INVALID_INT (-1)

/**
 * @brief Print extra DCI command line options.
 */
static void print_usage_addition(void)
{
    LOGI("DCI Aditional Options:\n");
    LOGI("      --clahe_en           [val] | CLAHE enable flag, range: {0,1}\n");
    LOGI("      --clahe_clip_value   [val] | CLAHE clip value, default follows json config\n");
    LOGI("      --clahe_local_ratio  [val] | CLAHE local ratio, default follows json config\n");
    LOGI("      --clahe_abld_ratio   [val] | CLAHE abld ratio, default follows json config\n");
    LOGI("      --clahe_scd_thr_min  [val] | CLAHE scd threshold min, default follows json config\n");
    LOGI("      --clahe_scd_thr_max  [val] | CLAHE scd threshold max, default follows json config\n");
    LOGI("      --shp_type           [val] | Sharp type, range: {0-disable, 1-sharp_full, 2-sharp_lite}\n");
    LOGI("      --shp_peaking_gain   [val] | Sharp peaking gain override, range: [0, 1023]\n");
    LOGI("\n");
}

/**
 * @brief Parse extra DCI command line options after the common parser.
 */
static int get_cmd_config_addition(int argc, char *const argv[], struct cmd_config_addition_dci *config)
{
    static const struct option g_cmd_args_options_dci[] = {
        {(char *)"clahe_en",          ARG_REQ, 0, 0},
        {(char *)"clahe_clip_value",  ARG_REQ, 0, 0},
        {(char *)"clahe_local_ratio", ARG_REQ, 0, 0},
        {(char *)"clahe_abld_ratio",  ARG_REQ, 0, 0},
        {(char *)"clahe_scd_thr_min", ARG_REQ, 0, 0},
        {(char *)"clahe_scd_thr_max", ARG_REQ, 0, 0},
        {(char *)"shp_type",          ARG_REQ, 0, 0},
        {(char *)"shp_peaking_gain",  ARG_REQ, 0, 0},
        {0,                           0,       0, 0}
    };

    config->clahe_en = DCI_CLAHE_OVERRIDE_INVALID_INT;
    config->clahe_clip_value = DCI_CLAHE_OVERRIDE_INVALID_F32;
    config->clahe_local_ratio = DCI_CLAHE_OVERRIDE_INVALID_INT;
    config->clahe_abld_ratio = DCI_CLAHE_OVERRIDE_INVALID_F32;
    config->clahe_scd_thr_min = DCI_CLAHE_OVERRIDE_INVALID_INT;
    config->clahe_scd_thr_max = DCI_CLAHE_OVERRIDE_INVALID_INT;
    config->shp_type = SHP_OVERRIDE_INVALID_INT;
    config->shp_peaking_gain = SHP_OVERRIDE_INVALID_INT;

    optind = 1;
    int opt = -1;
    int idx = -1;
    while ((opt = getopt_long(argc, argv, "-", g_cmd_args_options_dci, &idx)) != -1) {
        if (opt != 0) {
            continue;
        }

        switch (idx) {
        case 0:  config->clahe_en = strtol(optarg, NULL, 10); break;
        case 1:  config->clahe_clip_value = strtod(optarg, NULL); break;
        case 2:  config->clahe_local_ratio = strtol(optarg, NULL, 10); break;
        case 3:  config->clahe_abld_ratio = strtod(optarg, NULL); break;
        case 4:  config->clahe_scd_thr_min = strtol(optarg, NULL, 10); break;
        case 5:  config->clahe_scd_thr_max = strtol(optarg, NULL, 10); break;
        case 6:  config->shp_type = strtol(optarg, NULL, 10); break;
        case 7:  config->shp_peaking_gain = strtol(optarg, NULL, 10); break;
        default: break;
        }
        LOGI(" - get %dth option: %s = %s\n", idx, g_cmd_args_options_dci[idx].name, optarg);
    }

    return 0;
}

/**
 * @brief Convert the platform name from CLI into the prebuilt DCI platform id.
 */
static int get_platform_id(const char *platform_name)
{
    if (platform_name && (_stricmp(platform_name, "RK3572") == 0)) {
        return RK_PLATFORM_RK3572;
    }
    return RK_PLATFORM_RK3576;
}

/**
 * @brief Convert verify image format into the prebuilt DCI pixel format.
 */
static int get_dci_pixel_format(int src_fmt)
{
    switch (src_fmt & 0xFF) {
    case YUV422P_10LSB:
    case YUV422P_10PACKED: return PIX_YUV422P_10;
    case YUV420P_10LSB:
    case YUV420P_10PACKED: return PIX_YUV420P_10;
    case RGB_101010LSB:
    case RGB_10PACKED:     return PIX_RGB101010;
    case YUV444P_10LSB:
    case YUV444P_10PACKED: return PIX_YUV444P_10;
    default:               return common_verify_imgfmt_is_yuv(src_fmt) ? PIX_YUV444P_10 : PIX_RGB101010;
    }
}

/**
 * @brief Configure a fixed YUV709F to RGB full-range CSC path for DCI output.
 */
static int init_rgb_output_csc(struct post_csc_convert_mode *mode, struct post_csc_coef *coef)
{
    memset(mode, 0, sizeof(*mode));
    memset(coef, 0, sizeof(*coef));
    mode->intput_color_encoding = DRM_COLOR_YCBCR_BT709;
    mode->output_color_encoding = DRM_COLOR_YCBCR_BT709;
    mode->is_input_yuv = true;
    mode->is_output_yuv = false;
    mode->is_input_full_range = true;
    mode->is_output_full_range = true;
    mode->swap_channels = 0;
    mode->plat = VOP_VERSION_RK3572;
    mode->pixel_depth = 10;
    mode->coef_precision = 13;

    return rockchip_calc_post_csc(NULL, coef, mode);
}

/**
 * @brief Run a 10-bit planar CSC conversion for RGB/YUV444 buffers.
 */
static void run_csc_with_coef_13bit(const void *p_src, void *p_dst, int img_w, int img_h,
    const struct post_csc_coef *csc_coefs, const struct post_csc_convert_mode *mode)
{
    const int csc_min_vl_1 = mode->is_output_full_range ? 0 : (16 << (mode->pixel_depth - 8));
    const int csc_max_vl_1 = mode->is_output_full_range ? ((1 << mode->pixel_depth) - 1) : (235 << (mode->pixel_depth - 8));
    const int csc_min_vl_2 = csc_min_vl_1;
    const int csc_max_vl_2 = mode->is_output_yuv && !mode->is_output_full_range ? (240 << (mode->pixel_depth - 8)) : csc_max_vl_1;
    const int bit_num_0 = 13;
    const int offset0 = csc_coefs->csc_dc0;
    const int offset1 = csc_coefs->csc_dc1;
    const int offset2 = csc_coefs->csc_dc2;

    int src_color[3] = {0};
    int dst_color[3] = {0};
    ushort *p_src_y = (ushort *)p_src;
    ushort *p_src_u = (ushort *)p_src + img_w * img_h;
    ushort *p_src_v = (ushort *)p_src + img_w * img_h * 2;
    ushort *p_dst_y = (ushort *)p_dst;
    ushort *p_dst_u = (ushort *)p_dst + img_w * img_h;
    ushort *p_dst_v = (ushort *)p_dst + img_w * img_h * 2;

    for (int i = 0; i < img_h; i++) {
        for (int j = 0; j < img_w; j++) {
            src_color[0] = *p_src_y++;
            src_color[1] = *p_src_u++;
            src_color[2] = *p_src_v++;

            int a0 = csc_coefs->csc_coef00 * src_color[0];
            int a1 = csc_coefs->csc_coef01 * src_color[1];
            int a2 = csc_coefs->csc_coef02 * src_color[2];
            int a3 = csc_coefs->csc_coef10 * src_color[0];
            int a4 = csc_coefs->csc_coef11 * src_color[1];
            int a5 = csc_coefs->csc_coef12 * src_color[2];
            int a6 = csc_coefs->csc_coef20 * src_color[0];
            int a7 = csc_coefs->csc_coef21 * src_color[1];
            int a8 = csc_coefs->csc_coef22 * src_color[2];
            int csc_chl0 = a0 + a1 + a2;
            int csc_chl1 = a3 + a4 + a5;
            int csc_chl2 = a6 + a7 + a8;

            if (mode->plat == VOP_VERSION_RK3576) {
                dst_color[0] = csc_simple_round(csc_chl0, bit_num_0) + offset0;
                dst_color[1] = csc_simple_round(csc_chl1, bit_num_0) + offset1;
                dst_color[2] = csc_simple_round(csc_chl2, bit_num_0) + offset2;
            }
            else {
                dst_color[0] = csc_simple_round(csc_chl0 + offset0, bit_num_0);
                dst_color[1] = csc_simple_round(csc_chl1 + offset1, bit_num_0);
                dst_color[2] = csc_simple_round(csc_chl2 + offset2, bit_num_0);
            }

            dst_color[0] = CLIP(dst_color[0], csc_min_vl_1, csc_max_vl_1);
            dst_color[1] = CLIP(dst_color[1], csc_min_vl_2, csc_max_vl_2);
            dst_color[2] = CLIP(dst_color[2], csc_min_vl_2, csc_max_vl_2);
            *p_dst_y++ = dst_color[0];
            *p_dst_u++ = dst_color[1];
            *p_dst_v++ = dst_color[2];
        }
    }
}

/**
 * @brief Fill image plane metadata for the DCI prebuilt interface.
 */
static void fill_img_info(img_info_t *info, int width, int height, int fmt, void *plane_y, void *plane_u, void *plane_v)
{
    memset(info, 0, sizeof(*info));
    info->img_bits = 10;
    info->is_yuv = common_verify_imgfmt_is_yuv(fmt);
    info->is_rgb = common_verify_imgfmt_is_rgb(fmt);

    info->img_w[0] = width;
    info->img_h[0] = height;
    info->img_ws[0] = (fmt == RGB_101010LSB) ? width * 3 : width;
    info->img_hs[0] = height;
    info->plane_info[0].ptr = plane_y;
    info->plane_info[0].pix_strd = 1;

    if (fmt == RGB_101010LSB) {
        info->plane_num = 1;
        return;
    }

    info->plane_num = 3;

    int chroma_w = width;
    int chroma_h = height;
    if ((fmt & 0xF) >= YUV422P) {
        chroma_w = width / 2;
    }
    if ((fmt & 0xF) >= YUV420P) {
        chroma_h = height / 2;
    }

    info->img_w[1] = chroma_w;
    info->img_h[1] = chroma_h;
    info->img_ws[1] = chroma_w;
    info->img_hs[1] = chroma_h;
    info->plane_info[1].ptr = plane_u;
    info->plane_info[1].pix_strd = 1;

    info->img_w[2] = chroma_w;
    info->img_h[2] = chroma_h;
    info->img_ws[2] = chroma_w;
    info->img_hs[2] = chroma_h;
    info->plane_info[2].ptr = plane_v;
    info->plane_info[2].pix_strd = 1;
}

/**
 * @brief Return the U/V plane offsets of a planar 10-bit frame.
 */
static void get_plane_pointers(void *buffer, int width, int height, int fmt, void **plane_y, void **plane_u, void **plane_v)
{
    const size_t luma_pixels = (size_t)width * height;
    size_t chroma_pixels = luma_pixels;
    if ((fmt & 0xF) >= YUV422P) {
        chroma_pixels /= 2;
    }
    if ((fmt & 0xF) >= YUV420P) {
        chroma_pixels /= 2;
    }

    *plane_y = buffer;
    *plane_u = (void *)((ushort *)buffer + luma_pixels);
    *plane_v = (void *)((ushort *)buffer + luma_pixels + chroma_pixels);
}

/**
 * @brief Build a file path for dumping intermediate image data.
 */
static void build_dump_path(char *path, size_t path_size, const char *output_dir, const char *tag, int frame_idx,
    int fmt, int width, int height)
{
    snprintf(path, path_size, "%s/%s_frm%d_%dx%d_%s.%s", output_dir, tag, frame_idx, width, height,
        common_verify_imgfmt_name(fmt), common_verify_imgfmt_exten_str(fmt));
}

/**
 * @brief Dump a raw image buffer into a standalone file.
 */
static int dump_image_file(const char *output_dir, const char *tag, int frame_idx, const void *buffer, int width,
    int height, int width_stride, int height_stride, int fmt, int depth, int dither)
{
    char dump_path[1024] = {0};
    build_dump_path(dump_path, sizeof(dump_path), output_dir, tag, frame_idx, fmt, width, height);
    FILE *fp = fopen(dump_path, "wb");
    if (!fp) {
        LOGE("failed to create dump file '%s'! %s\n", dump_path, strerror(errno));
        return -1;
    }

    int ret = 0;
    if (depth == 10) {
        ret = image_write_from_10bit_plannar(fp, (void *)buffer, 0, width, height, width_stride, height_stride, fmt, dither);
    }
    else {
        ret = image_write_from_plannar(fp, (void *)buffer, 0, width, height, width_stride, height_stride, fmt, depth, dither);
    }
    fclose(fp);
    if (ret == 0) {
        LOGI("dump intermediate image to: %s\n", dump_path);
    }
    return ret;
}

/**
 * @brief Dump an interleaved 8-bit RGB buffer to a raw file.
 */
static int dump_rgb888_buffer(const char *output_dir, const char *tag, int frame_idx, const void *buffer, int width, int height)
{
    char dump_path[1024] = {0};
    build_dump_path(dump_path, sizeof(dump_path), output_dir, tag, frame_idx, RGB888, width, height);
    FILE *fp = fopen(dump_path, "wb");
    if (!fp) {
        LOGE("failed to create dump file '%s'! %s\n", dump_path, strerror(errno));
        return -1;
    }

    int ret = image_write(fp, (void *)buffer, 0, width, height, RGB888);
    fclose(fp);
    if (ret == 0) {
        LOGI("dump intermediate RGB data to: %s\n", dump_path);
    }
    return ret;
}

/**
 * @brief Dump a planar 10-bit RGB frame into an stb image file.
 */
static int write_rgb_stb_image(const char *filename, const void *buffer, int width, int height, int dither,
    const char *output_dir, int dump_flag, int frame_idx)
{
    const int rgb_stride = width * 3;
    uint8_t *rgb_data = (uint8_t *)malloc((size_t)rgb_stride * height);
    if (!rgb_data) {
        return -1;
    }

    int ret = imgcvt_from_planar_10bit_lsb((uint16_t const *)buffer, rgb_data, width, height, width * 2, height,
        rgb_stride, height, RGB888, false, dither);
    // if (ret == 0) {
    //     if (VERIFY_DBG_DUMP_ENABLED(dump_flag, VERIFY_DBG_DUMP_MED_IMG)) {
    //         ret = dump_rgb888_buffer(output_dir, "dci_dbg_input_stb", frame_idx, rgb_data, width, height);
    //     }
    // }
    if (ret == 0) {
        ret = write_stb_image_auto(filename, width, height, 3, rgb_data, rgb_stride);
    }
    free(rgb_data);
    return ret;
}

int main(int argc, char *const argv[])
{
    void *p_src = NULL;
    void *p_src_dci = NULL;
    void *p_dst = NULL;
    void *p_shp = NULL;
    void *p_rgb = NULL;
    void *p_src_stb = NULL;
    void *p_src_y = NULL;
    void *p_src_u = NULL;
    void *p_src_v = NULL;
    void *p_dst_y = NULL;
    void *p_dst_u = NULL;
    void *p_dst_v = NULL;
    void *p_shp_y = NULL;
    void *p_shp_u = NULL;
    void *p_shp_v = NULL;
    FILE *fp_src = NULL;
    FILE *fp_dst = NULL;
    FILE *fp_crc = NULL;
    dci_handle_t handle = NULL;
    sharp_full_handle_t sharp_full_handle = NULL;
    sharp_lite_handle_t sharp_lite_handle = NULL;
    size_t frame_size_max = 0;
    int ret = 0;
    int nb_channels = 0;
    unsigned int src_crc = 0;
    unsigned int dst_crc = 0;
    bool is_src_stb_img = false;
    bool is_dst_stb_img = false;
    bool need_rgb_input_pack = false;
    bool need_rgb_output = false;
    bool need_sharp = false;
    bool enable_dump_med_img = false;
    bool can_calc_crc = false;
    int shp_type = 0;
    int bIsInputYuv = 0;
    int bIsOutputYuv = 0;
    int dci_dst_fmt = YUV444P_10LSB;
    int dci_src_dump_fmt = YUV444P_10LSB;
    void *p_final_out = NULL;
    dci_proc_param_t dci_proc_param = {0};
    dci_init_param_t dci_init_param = {0};
    sharp_full_proc_param_t shpfull_proc_param = {0};
    sharp_full_init_param_t shpfull_init_param = {0};
    sharp_lite_proc_param_t shplite_proc_param = {0};
    sharp_lite_init_param_t shplite_init_param = {0};
    struct post_csc_convert_mode rgb_output_csc_mode {};
    // memset(&rgb_output_csc_mode, 0, sizeof(rgb_output_csc_mode));
    struct post_csc_coef rgb_output_csc_coef;

    /* parse cmd parameters */
    opterr = 0; // disable getopt error message
    struct common_verify_cmd_config config = {0};
    ret = common_verify_arg_get_cmd_config(argc, argv, &config);
    if (ret < 0) {
        print_usage_addition();
        return ret;
    }
    common_verify_arg_dump_config(&config);

    struct cmd_config_addition_dci config2 = {0};
    ret = get_cmd_config_addition(argc, argv, &config2);
    LOGI("dump DCI config from cmd line:\n");
    LOGI(" - clahe_en: %d\n", config2.clahe_en);
    LOGI(" - clahe_clip_value: %f\n", config2.clahe_clip_value);
    LOGI(" - clahe_local_ratio: %d\n", config2.clahe_local_ratio);
    LOGI(" - clahe_abld_ratio: %f\n", config2.clahe_abld_ratio);
    LOGI(" - clahe_scd_thr_min: %d\n", config2.clahe_scd_thr_min);
    LOGI(" - clahe_scd_thr_max: %d\n", config2.clahe_scd_thr_max);
    LOGI(" - shp_type: %d\n", config2.shp_type);
    LOGI(" - shp_peaking_gain: %d\n", config2.shp_peaking_gain);

    // check necessary parameters
    const bool write_crc = ((config.dump_flag & VERIFY_DBG_DUMP_CRC) != 0) && (config.crc_file[0] != '\0');
    if (write_crc) {
        snprintf(config.crc_file, 1024, "%s/dci_crc_out.dat", config.output_dir);
        LOGI(" - crc_file update to: '%s'!\n", config.crc_file);
    }

    is_src_stb_img = is_stb_image(config.input_file);
    is_dst_stb_img = is_stb_image(config.output_file);
    if (is_dst_stb_img && config.nb_frame != 1) {
        LOGE("stb image output only supports a single frame!\n");
        return -1;
    }

    if (config.mode != 4 && config.config_file[0] == '\0') {
        LOGE(" - config_file is not specified when dci_mode != 4\n");
        return -1;
    }
    if (is_dst_stb_img && !common_verify_imgfmt_is_rgb(config.dst_fmt)) {
        LOGE("stb image output currently requires an RGB-family dst_fmt\n");
        return -1;
    }
    need_rgb_output = is_dst_stb_img || common_verify_imgfmt_is_rgb(config.dst_fmt);
    shp_type = (config2.shp_type == SHP_OVERRIDE_INVALID_INT) ? 0 : config2.shp_type;
    need_sharp = (shp_type == 1 || shp_type == 2);
    enable_dump_med_img = VERIFY_DBG_DUMP_ENABLED(config.dump_flag, VERIFY_DBG_DUMP_MED_IMG);
    if (shp_type < 0 || shp_type > 2) {
        LOGW("invalid --shp_type value: %d, expected 0/1/2\n", shp_type);
        need_sharp = false;
    }
    if (need_sharp && config.config_file[0] == '\0') {
        LOGE("sharp post-process requires config_file when --shp_type is enabled\n");
        return -1;
    }

    if (is_src_stb_img) {
        p_src_stb = read_stb_image_auto(config.input_file, &config.src_wid, &config.src_hgt, &nb_channels, 3);
        if (!p_src_stb) {
            return -1;
        }
        config.nb_frame = 1;
        config.src_fmt = RGB888;
        config.src_wid_vir = config.src_wid * 3;
        config.src_hgt_vir = config.src_hgt;
        LOGW("stb image read success, src size: %dx%d, fmt: RGB888\n", config.src_wid, config.src_hgt);
        if (enable_dump_med_img) {
            dump_rgb888_buffer(config.output_dir, "dci_dbg1_intput_stb", 0, p_src_stb, config.src_wid, config.src_hgt);
        }
        if (config.dst_wid != config.src_wid || config.dst_hgt != config.src_hgt) {
            config.dst_wid = config.src_wid;
            config.dst_hgt = config.src_hgt;
            config.dst_wid_vir = ROUND_S32(config.dst_wid * common_verify_imgfmt_pitch_ratio(config.dst_fmt));
            config.dst_hgt_vir = config.dst_hgt;
            LOGW("dst size updated to: %dx%d\n", config.dst_wid, config.dst_hgt);
        }
    }
    else {
        fp_src = fopen(config.input_file, "rb");
        if (!fp_src) {
            LOGE("Failed to open the input file '%s'! %s\n", config.input_file, strerror(errno));
            ret = -1;
            goto EXIT;
        }
    }

    need_rgb_input_pack = common_verify_imgfmt_is_rgb(config.src_fmt);

    if (!is_dst_stb_img) {
        fp_dst = fopen(config.output_file, "wb");
        if (!fp_dst) {
            LOGE("Failed to open the output file '%s'! %s\n", config.output_file, strerror(errno));
            ret = -1;
            goto EXIT;
        }
    }
    if (write_crc) {
        fp_crc = fopen(config.crc_file, "a");
        if (!fp_crc) {
            LOGW("Failed to open the crc output file '%s'! %s. CRC value will not be written!\n", config.crc_file,
                strerror(errno));
        }
    }

    frame_size_max = (size_t)config.src_wid * config.src_hgt * 4 * 2; // 4 channels x 16bpp
    p_src = calloc(frame_size_max, 1);
    if (need_rgb_input_pack) {
        p_src_dci = calloc(frame_size_max, 1);
    }
    p_dst = calloc(frame_size_max, 1);
    if (need_sharp) {
        p_shp = calloc(frame_size_max, 1);
    }
    if (need_rgb_output) {
        p_rgb = calloc(frame_size_max, 1);
    }
    if (!p_src || (need_rgb_input_pack && !p_src_dci) || !p_dst || (need_sharp && !p_shp) || (need_rgb_output && !p_rgb))
    {
        ret = -1;
        goto EXIT;
    }

    /* create handler */
    dci_proc_param.dci_enable = 1;
    dci_proc_param.dci_mode = config.mode >= 0 ? config.mode : 1;
    dci_proc_param.is_src_fullrange = common_verify_clrspc_is_full_range(config.src_clrspc);
    dci_proc_param.pixel_format = get_dci_pixel_format(config.src_fmt);
    dci_proc_param.clahe_en = config2.clahe_en;
    dci_proc_param.clahe_clip_value = config2.clahe_clip_value;
    dci_proc_param.clahe_local_ratio = config2.clahe_local_ratio;
    dci_proc_param.clahe_abld_ratio = config2.clahe_abld_ratio;
    dci_proc_param.clahe_scd_thr_min = config2.clahe_scd_thr_min;
    dci_proc_param.clahe_scd_thr_max = config2.clahe_scd_thr_max;
    dci_src_dump_fmt = common_verify_imgfmt_get_def_planar(config.src_fmt, 10);
    dci_init_param.platform = get_platform_id(config.platform_name);
    dci_init_param.debug_dump_mask = (unsigned int)config.dump_flag;
    snprintf(dci_init_param.debug_path, sizeof(dci_init_param.debug_path), "%s", config.output_dir);
    shpfull_init_param.platform = dci_init_param.platform;
    shpfull_init_param.debug_dump_mask = dci_init_param.debug_dump_mask;
    snprintf(shpfull_init_param.debug_path, sizeof(shpfull_init_param.debug_path), "%s", config.output_dir);
    shplite_init_param.platform = dci_init_param.platform;
    shplite_init_param.debug_dump_mask = dci_init_param.debug_dump_mask;
    snprintf(shplite_init_param.debug_path, sizeof(shplite_init_param.debug_path), "%s", config.output_dir);

    if (ends_with(config.config_file, ".json", false)) {
        snprintf(dci_proc_param.config_path, sizeof(dci_proc_param.config_path), "%s", config.config_file);
        if (dci_proc_param.dci_mode >= 1 && dci_proc_param.dci_mode <= 3) {
            LOGE(" - for .json config file, dci_mode(%d) should NOT be in [1, 3]!\n", dci_proc_param.dci_mode);
            ret = -1;
            goto EXIT;
        }
    }
    else if (ends_with(config.config_file, ".bin", false)) {
        snprintf(dci_proc_param.reg_path, sizeof(dci_proc_param.reg_path), "%s", config.config_file);
        if (dci_proc_param.dci_mode != 1 && dci_proc_param.dci_mode != 2) {
            LOGE(" - for .bin reg file, dci_mode(%d) should be 1 or 2!\n", dci_proc_param.dci_mode);
            ret = -1;
            goto EXIT;
        }
    }
    else if (config.mode != 4) {
        LOGE("invalid config file suffix: %s !\n", config.config_file);
        ret = -1;
        goto EXIT;
    }
    if (shp_type == 1) {
        shpfull_proc_param.sharp_full_enable = 1;
        shpfull_proc_param.sharp_full_mode = ends_with(config.config_file, ".json", false) ? 0 : 1;
        shpfull_proc_param.peaking_gain = (config2.shp_peaking_gain != SHP_OVERRIDE_INVALID_INT) ? config2.shp_peaking_gain
                                                                                                    : 320;
        snprintf(shpfull_proc_param.config_path, sizeof(shpfull_proc_param.config_path), "%s", config.config_file);
    }
    else if (shp_type == 2) {
        shplite_proc_param.sharp_lite_enable = 1;
        shplite_proc_param.legacy_config_mode = 0;
        if (ends_with(config.config_file, ".bin", false)) {
            if (config.mode == 1)
                shplite_proc_param.legacy_config_mode = 1;
            else if (config.mode == 2)
                shplite_proc_param.legacy_config_mode = 2;
        }
        shplite_proc_param.peaking_gain = (config2.shp_peaking_gain != SHP_OVERRIDE_INVALID_INT) ? config2.shp_peaking_gain
                                                                                                    : 320;
        snprintf(shplite_proc_param.config_path, sizeof(shplite_proc_param.config_path), "%s", config.config_file);

        shplite_proc_param.src_info.img_w[0] = config.src_wid;
        shplite_proc_param.src_info.img_h[0] = config.src_hgt;
        shplite_proc_param.src_info.img_ws[0] = config.src_wid;
        shplite_proc_param.src_info.img_hs[0] = config.src_hgt;
    }

    ret = dciVerifyInit(&handle, &dci_init_param);
    if (ret) {
        LOGE("failed to init handler! %d\n", ret);
        goto EXIT;
    }

    if (need_rgb_output) {
        ret = init_rgb_output_csc(&rgb_output_csc_mode, &rgb_output_csc_coef);
        if (ret) {
            LOGE("failed to init RGB output CSC! %d\n", ret);
            goto EXIT;
        }
    }
    if (shp_type == 1) {
        ret = sharpFullVerifyInit(&sharp_full_handle, &shpfull_init_param);
        if (ret) {
            LOGE("failed to init sharp_full handler! %d\n", ret);
            goto EXIT;
        }
    }
    else if (shp_type == 2) {
        ret = sharpLiteVerifyInit(&sharp_lite_handle, &shplite_init_param);
        if (ret) {
            LOGE("failed to init sharp_lite handler! %d\n", ret);
            goto EXIT;
        }
    }

    bIsInputYuv = common_verify_imgfmt_is_yuv(config.src_fmt);
    bIsOutputYuv = common_verify_imgfmt_is_yuv(config.dst_fmt);
    can_calc_crc = ((config.dst_fmt & 0xF) <= YUV444P);

    for (int k = 0; k < config.nb_frame; k++) {
        if (is_src_stb_img) {
            ret = imgcvt_to_planar_10bit_lsb((uint8_t const *)p_src_stb, (uint16_t *)p_src, config.src_wid, config.src_hgt,
                config.src_wid_vir, config.src_hgt_vir, config.src_wid * 2, config.src_hgt, config.src_fmt, false, 0);
        }
        else {
            ret = image_read_to_10bit_planar(fp_src, p_src, k, config.src_wid, config.src_hgt, config.src_wid_vir,
                config.src_hgt_vir, config.src_fmt, config.dither_up);
        }
        if (ret) {
            LOGE("Failed to read frame #%d from input file '%s'! %s\n", k, config.input_file, strerror(errno));
            break;
        }
        if (enable_dump_med_img) {
            ret = dump_image_file(config.output_dir, "dci_dbg2_input_10bit", k, p_src, config.src_wid, config.src_hgt,
                config.src_wid * 2, config.src_hgt, dci_src_dump_fmt, 10, config.dither_up);
        }

        if (can_calc_crc) {
            src_crc = get_crc_for_planar_frame_10bit(p_src, config.src_wid, config.src_hgt, bIsInputYuv);
            LOGI("src CRC (%s MSB order) of frame #%04d: 0x%08X\n", bIsInputYuv ? "VYU" : "RGB", k, src_crc);
        }

        if (need_rgb_input_pack) {
            ret = imgcvt_from_planar_10bit_lsb((uint16_t const *)p_src, (uint8_t *)p_src_dci, config.src_wid,
                config.src_hgt, config.src_wid * 2, config.src_hgt, config.src_wid * 3 * 2, config.src_hgt,
                RGB_101010LSB, false, config.dither_up);
            if (ret) {
                LOGE("failed to convert frame #%d from RGB_PLANAR10LSB to RGB_101010LSB\n", k);
                break;
            }
            p_src_y = p_src_dci;
            p_src_u = NULL;
            p_src_v = NULL;
        }
        else {
            get_plane_pointers(p_src, config.src_wid, config.src_hgt, config.src_fmt, &p_src_y, &p_src_u, &p_src_v);
        }
        get_plane_pointers(p_dst, config.dst_wid, config.dst_hgt, dci_dst_fmt, &p_dst_y, &p_dst_u, &p_dst_v);
        if (need_sharp) {
            get_plane_pointers(p_shp, config.dst_wid, config.dst_hgt, dci_dst_fmt, &p_shp_y, &p_shp_u, &p_shp_v);
        }

        fill_img_info(&dci_proc_param.src_info, config.src_wid, config.src_hgt,
            need_rgb_input_pack ? RGB_101010LSB : config.src_fmt, p_src_y, p_src_u, p_src_v);
        fill_img_info(&dci_proc_param.dst_info, config.dst_wid, config.dst_hgt, dci_dst_fmt, p_dst_y, p_dst_u, p_dst_v);
        dci_proc_param.frame_idx = k;
        dci_proc_param.frame_num = config.nb_frame;

        // supported formats: RGB101010l, YUV444P10l, YUV420P10l
        ret = dciVerifyProc(handle, &dci_proc_param);
        if (ret) {
            LOGE("dciVerifyProc failed on frame #%d, ret=%d\n", k, ret);
            break;
        }
        if (enable_dump_med_img) {
            ret = dump_image_file(config.output_dir, "dci_dbg3_output_10bit", k, p_dst, config.dst_wid, config.dst_hgt,
                config.dst_wid * 2, config.dst_hgt, YUV444P_10LSB, 10, config.dither_dn);
        }

        p_final_out = p_dst;
        if (need_sharp) {
            if (shp_type == 1) {
                fill_img_info(&shpfull_proc_param.src_info, config.dst_wid, config.dst_hgt, dci_dst_fmt, p_dst_y,
                    p_dst_u, p_dst_v);
                fill_img_info(&shpfull_proc_param.dst_info, config.dst_wid, config.dst_hgt, dci_dst_fmt, p_shp_y,
                    p_shp_u, p_shp_v);
                shpfull_proc_param.frame_idx = k;
                shpfull_proc_param.frame_num = config.nb_frame;
                ret = sharpFullVerifyProc(sharp_full_handle, &shpfull_proc_param);
                if (ret) {
                    LOGE("sharpFullVerifyProc failed on frame #%d, ret=%d\n", k, ret);
                    break;
                }
            }
            else if (shp_type == 2) {
                fill_img_info(&shplite_proc_param.src_info, config.dst_wid, config.dst_hgt, dci_dst_fmt, p_dst_y,
                    p_dst_u, p_dst_v);
                fill_img_info(&shplite_proc_param.dst_info, config.dst_wid, config.dst_hgt, dci_dst_fmt, p_shp_y,
                    p_shp_u, p_shp_v);
                shplite_proc_param.frame_idx = k;
                ret = sharpLiteVerifyProc(sharp_lite_handle, &shplite_proc_param);
                if (ret) {
                    LOGE("sharpLiteVerifyProc failed on frame #%d, ret=%d\n", k, ret);
                    break;
                }
            }
            p_final_out = p_shp;
            if (enable_dump_med_img) {
                ret = dump_image_file(config.output_dir, "dci_dbg4_output_shp", k, p_shp, config.dst_wid, config.dst_hgt,
                    config.dst_wid * 2, config.dst_hgt, YUV444P_10LSB, 10, config.dither_dn);
            }
        }

        if (need_rgb_output) {
            run_csc_with_coef_13bit(p_final_out, p_rgb, config.dst_wid, config.dst_hgt, &rgb_output_csc_coef,
                &rgb_output_csc_mode);
            if (enable_dump_med_img) {
                ret = dump_image_file(config.output_dir, "dci_dbg5_output_y2r", k, p_rgb, config.dst_wid, config.dst_hgt,
                    config.dst_wid * 2, config.dst_hgt, RGB_PLANAR10LSB, 10, config.dither_dn);
            }
            p_final_out = p_rgb;
        }

        if (is_dst_stb_img) {
            /* Convert 10bit RGB planar to 8bit interleaved RGB before stb output. */
            ret = write_rgb_stb_image(config.output_file, p_final_out, config.dst_wid, config.dst_hgt, config.dither_dn,
                config.output_dir, config.dump_flag, k);
            if (ret)
                break;
        }
        else {
            /* image_write_from_10bit_plannar() handles 10bit RGB planar -> 8bit RGB(A) raw output when dst_fmt is RGB888/RGBA8888. */
            ret = image_write_from_10bit_plannar(fp_dst, p_final_out, k, config.dst_wid, config.dst_hgt,
                config.dst_wid_vir, config.dst_hgt_vir, config.dst_fmt, config.dither_dn);
            if (ret) {
                LOGE("failed to write frame #%d to output file '%s'\n", k, config.output_file);
                break;
            }
            if (config.nb_frame == 1) {
                image_write_from_10bit_plannar(fp_dst, p_src, 0, config.src_wid, config.src_hgt, config.src_wid_vir,
                    config.src_hgt_vir, config.src_fmt, config.dither_dn);
            }
        }

        if (can_calc_crc) {
            dst_crc = get_crc_for_planar_frame_10bit(p_final_out, config.dst_wid, config.dst_hgt, bIsOutputYuv);
            LOGI("dst CRC (%s MSB order) of frame #%04d: 0x%08X\n", bIsOutputYuv ? "VYU" : "RGB", k, dst_crc);
            if (fp_crc) {
                fprintf(fp_crc, "input: %s, config: %s, crc of frame #%04d: 0x%08X\n", get_basename(config.input_file),
                    get_basename(config.config_file[0] ? config.config_file : "mode_only"), k, dst_crc);
            }
        }
    }

EXIT:
    if (sharp_full_handle)
        sharpFullVerifyDeinit(sharp_full_handle);
    if (sharp_lite_handle)
        sharpLiteVerifyDeinit(sharp_lite_handle);
    if (handle)
        dciVerifyDeinit(handle);
    if (fp_src)
        fclose(fp_src);
    if (fp_dst)
        fclose(fp_dst);
    if (fp_crc)
        fclose(fp_crc);
    if (p_src)
        free(p_src);
    if (p_src_dci)
        free(p_src_dci);
    if (p_dst)
        free(p_dst);
    if (p_shp)
        free(p_shp);
    if (p_rgb)
        free(p_rgb);
    if (p_src_stb)
        free_stb_image_auto((uint8_t *)p_src_stb);

    if (ret == 0) {
        LOGI("verify done. please check the output file: %s\n", config.output_file);
    }
    return ret;
}
