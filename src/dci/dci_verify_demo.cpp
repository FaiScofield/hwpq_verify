/**
 * @copyright Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @description: dci_verify_demo.c
 * @author: vance.wu@rock-chips.com
 * @create: 2025-09-15
 * @modify: 2026-05-25
 */

#ifdef __cplusplus
extern "C" {
#endif
#include "dci_api.h"
#include "rockchip_post_csc.h"
#ifdef __cplusplus
}
#endif

#include "verify_com.h"
#include "verify_cmd_parser.h"
#include "verify_crc32.h"
#include "cJSON.h"
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
    double clahe_clip_value;
    int clahe_local_ratio;
    bool has_clahe_en;
    bool has_clahe_clip_value;
    bool has_clahe_local_ratio;
};

/**
 * @brief Print extra DCI command line options.
 */
static void print_usage_addition(void)
{
    LOGI("DCI Aditional Options:\n");
    LOGI("      --clahe_en           [val] | CLAHE enable flag, range: {0,1}\n");
    LOGI("      --clahe_clip_value   [val] | CLAHE clip value, default follows json config\n");
    LOGI("      --clahe_local_ratio  [val] | CLAHE local ratio, default follows json config\n");
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
        {0,                           0,       0, 0}
    };

    memset(config, 0, sizeof(*config));

    optind = 1;
    int opt = -1;
    int idx = -1;
    while ((opt = getopt_long(argc, argv, "-", g_cmd_args_options_dci, &idx)) != -1) {
        if (opt != 0) {
            continue;
        }

        switch (idx) {
        case 0:
            config->clahe_en = strtol(optarg, NULL, 10);
            config->has_clahe_en = true;
            break;
        case 1:
            config->clahe_clip_value = strtod(optarg, NULL);
            config->has_clahe_clip_value = true;
            break;
        case 2:
            config->clahe_local_ratio = strtol(optarg, NULL, 10);
            config->has_clahe_local_ratio = true;
            break;
        default: break;
        }
        LOGI(" - get %dth option: %s = %s\n", idx, g_cmd_args_options_dci[idx].name, optarg);
    }

    return 0;
}

/**
 * @brief Return whether any DCI runtime override is requested from CLI.
 */
static bool has_runtime_override(const struct cmd_config_addition_dci *config)
{
    return config->has_clahe_en || config->has_clahe_clip_value || config->has_clahe_local_ratio;
}

/**
 * @brief Get or create a child JSON object.
 */
static cJSON *get_or_create_object(cJSON *parent, const char *key)
{
    cJSON *node = cJSON_GetObjectItem(parent, key);
    if (node && cJSON_IsObject(node)) {
        return node;
    }

    node = cJSON_CreateObject();
    if (!node) {
        return NULL;
    }
    cJSON_AddItemToObject(parent, key, node);
    return node;
}

/**
 * @brief Replace an existing number item or create it if missing.
 */
static int set_json_number(cJSON *parent, const char *key, double value)
{
    cJSON *number = cJSON_CreateNumber(value);
    if (!number) {
        return -1;
    }

    cJSON *old = cJSON_GetObjectItem(parent, key);
    if (old) {
        cJSON_ReplaceItemInObject(parent, key, number);
    }
    else {
        cJSON_AddItemToObject(parent, key, number);
    }
    return 0;
}

/**
 * @brief Generate a runtime JSON file with the requested CLI overrides.
 */
static int generate_runtime_config(const char *src_cfg_path, const char *dst_cfg_path,
    const struct cmd_config_addition_dci *config)
{
    FILE *fp = fopen(src_cfg_path, "rb");
    if (!fp) {
        LOGE("failed to open config file '%s'! %s\n", src_cfg_path, strerror(errno));
        return -1;
    }

    if (fseek(fp, 0, SEEK_END) != 0) {
        LOGE("failed to seek config file '%s'! %s\n", src_cfg_path, strerror(errno));
        fclose(fp);
        return -1;
    }
    long cfg_size = ftell(fp);
    if (cfg_size <= 0 || fseek(fp, 0, SEEK_SET) != 0) {
        LOGE("invalid config file length for '%s'! %s\n", src_cfg_path, strerror(errno));
        fclose(fp);
        return -1;
    }

    char *cfg_text = (char *)calloc((size_t)cfg_size + 1, 1);
    if (!cfg_text) {
        fclose(fp);
        return -1;
    }
    size_t read_size = fread(cfg_text, 1, (size_t)cfg_size, fp);
    fclose(fp);
    if (read_size != (size_t)cfg_size) {
        LOGE("failed to read config file '%s'! %s\n", src_cfg_path, strerror(errno));
        free(cfg_text);
        return -1;
    }

    cJSON *root = cJSON_Parse(cfg_text);
    free(cfg_text);
    if (!root) {
        LOGE("failed to parse config file '%s'! %s\n", src_cfg_path, cJSON_GetErrorPtr());
        return -1;
    }

    cJSON *node_dci = root;
    if (cJSON_HasObjectItem(node_dci, "pq_tuning_param")) {
        node_dci = get_or_create_object(node_dci, "pq_tuning_param");
    }
    node_dci = get_or_create_object(node_dci, "dci");
    cJSON *interp_params = get_or_create_object(node_dci, "s_vop_dci_interp_params");
    cJSON *ctrl_params = get_or_create_object(interp_params, "s_vop_dci_ctrl");
    cJSON *clahe_params = get_or_create_object(interp_params, "s_clahe_params");
    if (!node_dci || !interp_params || !ctrl_params || !clahe_params) {
        LOGE("failed to create runtime json nodes for DCI config\n");
        cJSON_Delete(root);
        return -1;
    }

    if (config->has_clahe_en) {
        set_json_number(ctrl_params, "i_dciEnable", config->clahe_en ? 1 : 0);
        set_json_number(clahe_params, "i_dci_CLAHE_en", config->clahe_en ? 1 : 0);
    }
    if (config->has_clahe_clip_value) {
        set_json_number(clahe_params, "i_dci_CLAHE_clip_value", config->clahe_clip_value);
    }
    if (config->has_clahe_local_ratio) {
        set_json_number(clahe_params, "i_dci_CLAHE_LocalRatio", config->clahe_local_ratio);
    }

    char *out_text = cJSON_Print(root);
    cJSON_Delete(root);
    if (!out_text) {
        return -1;
    }

    fp = fopen(dst_cfg_path, "wb");
    if (!fp) {
        LOGE("failed to create runtime config '%s'! %s\n", dst_cfg_path, strerror(errno));
        cJSON_free(out_text);
        return -1;
    }
    fwrite(out_text, 1, strlen(out_text), fp);
    fclose(fp);
    cJSON_free(out_text);

    LOGI("write DCI runtime config to file: '%s'\n", dst_cfg_path);
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
static void build_dump_path(char *path, size_t path_size, const char *output_dir, const char *tag, int frame_idx, int fmt, int width, int height)
{
    snprintf(path, path_size, "%s/%s_frm%d_%dx%d_%s.%s", output_dir, tag, frame_idx, width, height,
        common_verify_imgfmt_name(fmt), common_verify_imgfmt_exten_str(fmt));
}

/**
 * @brief Dump a raw image buffer into a standalone file.
 */
static int dump_image_file(const char *output_dir, const char *tag, int frame_idx, const void *buffer, int width, int height, int width_stride,
    int height_stride, int fmt, int depth, int dither)
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
static int write_rgb_stb_image(const char *filename, const void *buffer, int width, int height, int dither, const char *output_dir,
    int dump_flag, int frame_idx)
{
    const int rgb_stride = width * 3;
    uint8_t *rgb_data = (uint8_t *)malloc((size_t)rgb_stride * height);
    if (!rgb_data) {
        return -1;
    }

    int ret = imgcvt_from_planar_10bit_lsb((uint16_t const *)buffer, rgb_data, width, height, width * 2, height,
        rgb_stride, height, RGB888, false, dither);
    if (ret == 0) {
        if (VERIFY_DBG_DUMP_ENABLED(dump_flag, VERIFY_DBG_DUMP_MED_IMG)) {
            ret = dump_rgb888_buffer(output_dir, "dci_dbg_input_stb", frame_idx, rgb_data, width, height);
        }
    }
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
    void *p_rgb = NULL;
    void *p_src_stb = NULL;
    void *p_src_y = NULL;
    void *p_src_u = NULL;
    void *p_src_v = NULL;
    void *p_dst_y = NULL;
    void *p_dst_u = NULL;
    void *p_dst_v = NULL;
    FILE *fp_src = NULL;
    FILE *fp_dst = NULL;
    FILE *fp_crc = NULL;
    dci_handle_t handle = NULL;
    size_t frame_size_max = 0;
    int ret = 0;
    int nb_channels = 0;
    unsigned int src_crc = 0;
    unsigned int dst_crc = 0;
    bool is_src_stb_img = false;
    bool is_dst_stb_img = false;
    bool need_rgb_input_pack = false;
    bool need_rgb_output = false;
    bool enable_dump_med_img = false;
    bool can_calc_crc = false;
    int bIsInputYuv = 0;
    int bIsOutputYuv = 0;
    int dci_dst_fmt = YUV444P_10LSB;
    int dci_src_dump_fmt = YUV444P_10LSB;
    char runtime_cfg_path[1024] = {0};
    const char *config_path = NULL;
    void *p_final_out = NULL;
    dci_proc_param_t proc_param = {0};
    dci_init_param_t init_param = {0};
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
    struct cmd_config_addition_dci config2 = {0};
    ret = get_cmd_config_addition(argc, argv, &config2);
    common_verify_arg_dump_config(&config);

    // check necessary parameters
    if (config.crc_file[0] == '\0') {
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
    enable_dump_med_img = VERIFY_DBG_DUMP_ENABLED(config.dump_flag, VERIFY_DBG_DUMP_MED_IMG);

    config_path = config.config_file;
    if (has_runtime_override(&config2)) {
        if (!ends_with(config.config_file, ".json", false)) {
            LOGW("CLAHE runtime options only take effect with a json config file. Current config: '%s'\n", config.config_file);
        }
        else {
            snprintf(runtime_cfg_path, sizeof(runtime_cfg_path), "%s/dci_runtime_override.json", config.output_dir);
            ret = generate_runtime_config(config.config_file, runtime_cfg_path, &config2);
            if (ret) {
                return ret;
            }
            config_path = runtime_cfg_path;
        }
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
            dump_rgb888_buffer(config.output_dir, "dci_dbg_intput_stb", 0, p_src_stb, config.src_wid, config.src_hgt);
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
    fp_crc = fopen(config.crc_file, "a");
    if (!fp_crc) {
        LOGW("Failed to open the crc output file '%s'! %s. CRC value will not be written!\n", config.crc_file, strerror(errno));
    }

    frame_size_max = (size_t)config.src_wid * config.src_hgt * 4 * 2; // 4 channels x 16bpp
    p_src = calloc(frame_size_max, 1);
    if (need_rgb_input_pack) {
        p_src_dci = calloc(frame_size_max, 1);
    }
    p_dst = calloc(frame_size_max, 1);
    if (need_rgb_output) {
        p_rgb = calloc(frame_size_max, 1);
    }
    if (!p_src || (need_rgb_input_pack && !p_src_dci) || !p_dst || (need_rgb_output && !p_rgb)) {
        ret = -1;
        goto EXIT;
    }

    /* create handler */
    proc_param.dci_enable = 1;
    proc_param.dci_mode = config.mode >= 0 ? config.mode : 1;
    proc_param.is_src_fullrange = common_verify_clrspc_is_full_range(config.src_clrspc);
    proc_param.pixel_format = get_dci_pixel_format(config.src_fmt);
    dci_src_dump_fmt = common_verify_imgfmt_get_def_planar(config.src_fmt, 10);
    init_param.platform = get_platform_id(config.platform_name);
    snprintf(init_param.debug_path, sizeof(init_param.debug_path), "%s", config.output_dir);

    if (ends_with(config_path, ".json", false)) {
        snprintf(proc_param.config_path, sizeof(proc_param.config_path), "%s", config_path);
        if (proc_param.dci_mode >= 1 && proc_param.dci_mode <= 3) {
            LOGE(" - for .json config file, dci_mode(%d) should NOT be in [1, 3]!\n", proc_param.dci_mode);
            ret = -1;
            goto EXIT;
        }
    }
    else if (ends_with(config_path, ".bin", false)) {
        snprintf(proc_param.reg_path, sizeof(proc_param.reg_path), "%s", config_path);
        if (proc_param.dci_mode != 1 && proc_param.dci_mode != 2) {
            LOGE(" - for .bin reg file, dci_mode(%d) should be 1 or 2!\n", proc_param.dci_mode);
            ret = -1;
            goto EXIT;
        }
    }
    else if (config.mode != 4) {
        LOGE("invalid config file suffix: %s !\n", config_path);
        ret = -1;
        goto EXIT;
    }

    ret = dciVerifyInit(&handle, &init_param);
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
            ret = dump_image_file(config.output_dir, "dci_dbg_input", k, p_src, config.src_wid, config.src_hgt,
                config.src_wid * 2, config.src_hgt, dci_src_dump_fmt, 10, config.dither_up);
            if (ret) {
                break;
            }
        }

        if (can_calc_crc) {
            src_crc = get_crc_for_planar_frame_10bit(p_src, config.src_wid, config.src_hgt, bIsInputYuv);
            LOGI("src CRC (%s MSB order) of frame #%04d: 0x%08X\n", bIsInputYuv ? "VYU" : "RGB", k, src_crc);
        }

        if (need_rgb_input_pack) {
            ret = imgcvt_from_planar_10bit_lsb((uint16_t const *)p_src, (uint8_t *)p_src_dci, config.src_wid, config.src_hgt,
                config.src_wid * 2, config.src_hgt, config.src_wid * 3 * 2, config.src_hgt, RGB_101010LSB, false, config.dither_up);
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

        fill_img_info(&proc_param.src_info, config.src_wid, config.src_hgt, need_rgb_input_pack ? RGB_101010LSB : config.src_fmt,
            p_src_y, p_src_u, p_src_v);
        fill_img_info(&proc_param.dst_info, config.dst_wid, config.dst_hgt, dci_dst_fmt, p_dst_y, p_dst_u, p_dst_v);
        proc_param.frame_idx = k;
        proc_param.frame_num = config.nb_frame;

        // supported formats: RGB101010l, YUV444P10l, YUV420P10l
        ret = dciVerifyProc(handle, &proc_param);
        if (ret) {
            LOGE("dciVerifyProc failed on frame #%d, ret=%d\n", k, ret);
            break;
        }
        if (enable_dump_med_img) {
            ret = dump_image_file(config.output_dir, "dci_dbg_output", k, p_dst, config.dst_wid, config.dst_hgt,
                config.dst_wid * 2, config.dst_hgt, YUV444P_10LSB, 10, config.dither_dn);
            if (ret) {
                break;
            }
        }

        p_final_out = p_dst;
        if (need_rgb_output) {
            run_csc_with_coef_13bit(p_dst, p_rgb, config.dst_wid, config.dst_hgt, &rgb_output_csc_coef, &rgb_output_csc_mode);
            if (enable_dump_med_img) {
                ret = dump_image_file(config.output_dir, "dci_dbg_output_y2r", k, p_rgb, config.dst_wid, config.dst_hgt,
                    config.dst_wid * 2, config.dst_hgt, RGB_PLANAR10LSB, 10, config.dither_dn);
                if (ret) {
                    break;
                }
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
                    get_basename(config_path[0] ? config_path : "mode_only"), k, dst_crc);
            }
        }
    }

EXIT:
    if (handle) {
        dciVerifyDeinit(handle);
    }
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
    if (p_rgb)
        free(p_rgb);
    if (p_src_stb)
        free_stb_image_auto((uint8_t *)p_src_stb);

    if (ret == 0) {
        LOGI("verify done. please check the output file: %s\n", config.output_file);
    }
    return ret;
}
