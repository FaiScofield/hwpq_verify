/**
 * @copyright Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @description: csc_verify_demo.c
 * @author: vance.wu@rock-chips.com
 * @create: 2025-09-05
 * @history:
 *  2025-09-10 vance.wu: print crc32 value for input/output data.
 */

#include "verify_com.h"
#include "verify_cmd_parser.h"
#include "verify_crc32.h"
#include "rockchip_post_csc.h"
#include "rockchip_post_csc2.h"
#include "cJSON.h"
#include <errno.h>
#include <stdio.h>
#include <string.h>


static const char *g_csc_mode_strs[DRM_CSC_MODE_MAX] = {
    "RGBL_TO_RGBF",
    "RGBL_TO_YUV601L",
    "RGBL_TO_YUV601F",
    "RGBL_TO_YUV709L",
    "RGBL_TO_YUV709F",
    "RGBL_TO_YUV2020L",
    "RGBL_TO_YUV2020F",
    "RGBF_TO_RGBL",
    "RGBF_TO_YUV601L",
    "RGBF_TO_YUV601F",
    "RGBF_TO_YUV709L",
    "RGBF_TO_YUV709F",
    "RGBF_TO_YUV2020L",
    "RGBF_TO_YUV2020F",
    "YUV601L_TO_RGBL",
    "YUV601L_TO_RGBF",
    "YUV601L_TO_YUV601F",
    "YUV601L_TO_YUV709L",
    "YUV601L_TO_YUV709F",
    "YUV601F_TO_RGBL",
    "YUV601F_TO_RGBF",
    "YUV601F_TO_YUV601L",
    "YUV601F_TO_YUV709L",
    "YUV601F_TO_YUV709F",
    "YUV709L_TO_RGBL",
    "YUV709L_TO_RGBF",
    "YUV709L_TO_YUV601L",
    "YUV709L_TO_YUV601F",
    "YUV709L_TO_YUV709F",
    "YUV709F_TO_RGBL",
    "YUV709F_TO_RGBF",
    "YUV709F_TO_YUV601L",
    "YUV709F_TO_YUV601F",
    "YUV709F_TO_YUV709L",
    "YUV2020L_TO_RGBL",
    "YUV2020L_TO_RGBF",
    "YUV2020L_TO_YUV2020F",
    "YUV2020F_TO_RGBL",
    "YUV2020F_TO_RGBF",
    "YUV2020F_TO_YUV2020L",
    "Identity_Convertion",
};

struct cmd_config_addition_csc
{
    char mode_str[32];   // csc mode string like: '709l_to_rgbf'
    int pixel_depth;     // {8,10}
    int coef_precision;  // {8,10,13}
    bool use_float_coef; // {0, 1} TODO
};

void print_usage_addition()
{
    LOGI("CSC Aditional Options:\n");
    LOGI("  -D  --pixel_depth    [val] | pixel depth, range: {8,10}, default: 10bit\n");
    LOGI("  -P  --coef_precision [val] | coef precision, range: {8,10,13}, default: 10bit\n");
    LOGI("  -M  --mode_str       [val] | csc mode string like: '709l_to_rgbf', default: 'NULL'\n");
    LOGI("\n");
}

int get_cmd_config_addition(int argc, char *const argv[], struct cmd_config_addition_csc *cmd_config)
{
    static const struct option g_cmd_args_options_csc[] = {
        {   (char *)"pixel_depth", ARG_REQ, NULL, 'D'},
        {(char *)"coef_precision", ARG_REQ, NULL, 'P'},
        {      (char *)"mode_str", ARG_REQ, NULL, 'M'},
        {                       0,       0,    0,   0}  // end of option list
    };

    cmd_config->pixel_depth = 10;
    cmd_config->coef_precision = 10;

    /*! NOTE: need to reset 'optind' before parsing addition options */
    optind = 1;
    int opt = -1;
    int idx = -1;
    while ((opt = getopt_long(argc, argv, "-D:P:M:", g_cmd_args_options_csc, &idx)) != -1) {
        switch (opt) {
        case 'D': cmd_config->pixel_depth = atoi(optarg); break;
        case 'P': cmd_config->coef_precision = atoi(optarg); break;
        case 'M': strcpy_s(cmd_config->mode_str, 32, optarg); break;
        default:  break;
        }
    }

    return 0;
}

/* parse mode string like 'rgbl_to_601f' */
int parse_csc_mode_str(const char *mode_str, struct post_csc_convert_mode *mode)
{
    LOGI("parse from csc_mode_str: %s\n", mode_str);
    int ret = 0;
    int out_clr_pos = 8;
    int in_clr = -1;
    int out_clr = -1;

    mode->is_input_yuv = 1;
    mode->is_input_full_range = mode_str[3] == 'f' || mode_str[3] == 'F';
    if (0 == strncmp(mode_str, "rgb", 3)) {
        mode->intput_color_encoding = DRM_COLOR_ENCODING_MAX; // mark for later update
        mode->is_input_yuv = 0;
    }
    else if (0 == strncmp(mode_str, "601", 3)) {
        mode->intput_color_encoding = DRM_COLOR_YCBCR_BT601;
    }
    else if (0 == strncmp(mode_str, "709", 3)) {
        mode->intput_color_encoding = DRM_COLOR_YCBCR_BT709;
    }
    else if (0 == strncmp(mode_str, "2020", 4)) {
        mode->intput_color_encoding = DRM_COLOR_YCBCR_BT2020;
        mode->is_input_full_range = mode_str[4] == 'f' || mode_str[4] == 'F';
        out_clr_pos = 9;
    }
    else {
        LOGE("unknow csc_mode_str: %s\n", mode_str);
        ret = -1;
    }

    mode->is_output_yuv = 1;
    mode->is_output_full_range = mode_str[out_clr_pos + 3] == 'f' || mode_str[out_clr_pos + 3] == 'F';
    if (0 == strncmp(mode_str + out_clr_pos, "rgb", 3)) {
        mode->output_color_encoding = DRM_COLOR_ENCODING_MAX; // mark for later update
        mode->is_output_yuv = 0;
    }
    else if (0 == strncmp(mode_str + out_clr_pos, "601", 3)) {
        mode->output_color_encoding = DRM_COLOR_YCBCR_BT601;
    }
    else if (0 == strncmp(mode_str + out_clr_pos, "709", 3)) {
        mode->output_color_encoding = DRM_COLOR_YCBCR_BT709;
    }
    else if (0 == strncmp(mode_str + out_clr_pos, "2020", 4)) {
        mode->output_color_encoding = DRM_COLOR_YCBCR_BT2020;
        mode->is_output_full_range = mode_str[out_clr_pos + 4] == 'f' || mode_str[out_clr_pos + 4] == 'F';
    }
    else {
        LOGE("unknow csc_mode_str: %s\n", mode_str);
        ret = -1;
    }

    // update input/output colorspace if not specified
    if (mode->intput_color_encoding == DRM_COLOR_ENCODING_MAX) {
        mode->intput_color_encoding = (mode->output_color_encoding == DRM_COLOR_ENCODING_MAX) ? DRM_COLOR_YCBCR_BT709
                                                                                              : mode->output_color_encoding;
    }
    if (mode->output_color_encoding == DRM_COLOR_ENCODING_MAX) {
        mode->output_color_encoding = mode->intput_color_encoding;
    }
    return ret;
}

/* parse json cmd_config */
int parse_csc_config(const char *cfg_path, struct post_csc_coef *coef, struct post_csc *bcsh, struct post_csc_convert_mode *mode)
{
    if (!cfg_path || !coef) {
        LOGE("invalid input arguments!\n");
        return -1;
    }

    // open cmd_config file and get root node
    uint len = 0;
    char *cfg_text = NULL;
    FILE *fp = fopen(cfg_path, "r");
    if (!fp) {
        LOGE("open cfg file fail! %s. %s\n", cfg_path, strerror(errno));
        return -1;
    }
    if (fseek(fp, 0, SEEK_END) != 0 || (len = ftell(fp)) == 0 || fseek(fp, 0, SEEK_SET) != 0) {
        LOGE("cfg file len (%u) error! %s\n", len, strerror(errno));
        fclose(fp);
        return -1;
    }
    cfg_text = (char *)malloc(len + 1);
    uint read_size = fread(cfg_text, 1, len, fp);
    if (!cfg_text /* || read_size != len */) {
        LOGE("read cfg text fail!\n");
        fclose(fp);
        return -1;
    };
    fclose(fp);

    // get csc root node
    cJSON *cfg_root = cJSON_Parse(cfg_text);
    if (cfg_root == NULL) {
        free(cfg_text);
        LOGE("cJSON_Parse fail! %s\n", cJSON_GetErrorPtr());
        return -1;
    }
    cJSON *node_csc = cfg_root;
    if (cJSON_HasObjectItem(node_csc, "pq_tuning_param")) {
        node_csc = cJSON_GetObjectItem(node_csc, "pq_tuning_param");
    }
    if (cJSON_HasObjectItem(node_csc, "csc")) {
        node_csc = cJSON_GetObjectItem(node_csc, "csc");
    }

    int ret = 0;
    int pixel_depth = 10, precision = 10, passthrough = 1, mode_idx = -1;
    int csc_coefsx13[13] = {0};
    struct post_csc bcsh_cfg = {0};
    const struct post_csc_convert_mode *convert_mode = NULL;

    // parse csc configs
    if (cJSON_HasObjectItem(node_csc, "cscPassthrough")) {
        passthrough = cJSON_GetObjectItem(node_csc, "cscPassthrough")->valueint;
        LOGI("\t- load cscPassthrough: %d\n", passthrough);
    }
    if (cJSON_HasObjectItem(node_csc, "cscPixelDepth")) {
        pixel_depth = cJSON_GetObjectItem(node_csc, "cscPixelDepth")->valueint;
        LOGI("\t- load cscPixelDepth: %d\n", pixel_depth);
    }
    if (cJSON_HasObjectItem(node_csc, "cscCoefPrecision")) {
        precision = cJSON_GetObjectItem(node_csc, "cscCoefPrecision")->valueint;
        LOGI("\t- load cscCoefPrecision: %d\n", precision);
    }
    if (cJSON_HasObjectItem(node_csc, "cscConvertMode")) {
        mode_idx = cJSON_GetObjectItem(node_csc, "cscConvertMode")->valueint;
        LOGI("\t- load cscConvertMode: %d (%s)\n", mode_idx, g_csc_mode_strs[mode_idx]);
        if (mode_idx >= 0 && mode_idx < DRM_CSC_MODE_MAX) {
            convert_mode = &g_supported_standard_convert_mode[mode_idx];
            if (mode) {
                memcpy(mode, convert_mode, sizeof(struct post_csc_convert_mode));
                mode->plat = VOP_VERSION_RK3572;
                mode->pixel_depth = pixel_depth;
                mode->coef_precision = precision;
            }
        }
    }
    bcsh_cfg.csc_enable = cJSON_GetObjectItem(node_csc, "cscEnable")->valueint;
    // bcsh_cfg.cscCctCtrlEn = cJSON_GetObjectItem(node_csc, "cscCctCtrlEn")->valueint;
    bcsh_cfg.brightness = cJSON_GetObjectItem(node_csc, "cscBrightness")->valueint;
    bcsh_cfg.hue = cJSON_GetObjectItem(node_csc, "cscHue")->valueint;
    bcsh_cfg.contrast = cJSON_GetObjectItem(node_csc, "cscContrast")->valueint;
    bcsh_cfg.saturation = cJSON_GetObjectItem(node_csc, "cscSaturation")->valueint;
    bcsh_cfg.r_gain = cJSON_GetObjectItem(node_csc, "cscRGain")->valueint;
    bcsh_cfg.g_gain = cJSON_GetObjectItem(node_csc, "cscGGain")->valueint;
    bcsh_cfg.b_gain = cJSON_GetObjectItem(node_csc, "cscBGain")->valueint;
    bcsh_cfg.r_offset = cJSON_GetObjectItem(node_csc, "cscROffset")->valueint;
    bcsh_cfg.g_offset = cJSON_GetObjectItem(node_csc, "cscGOffset")->valueint;
    bcsh_cfg.b_offset = cJSON_GetObjectItem(node_csc, "cscBOffset")->valueint;
    if (bcsh) {
        memcpy(bcsh, &bcsh_cfg, sizeof(struct post_csc));
    }

    csc_coefsx13[12] = 1; //cJSON_GetObjectItem(node_csc, "cscEnable")->valueint;
    if (cJSON_HasObjectItem(node_csc, "cscMatrix") && cJSON_HasObjectItem(node_csc, "cscVector")) {
        cJSON *node_matrix = cJSON_GetObjectItem(node_csc, "cscMatrix");
        cJSON *node_vector = cJSON_GetObjectItem(node_csc, "cscVector");
        const int sieze_matrix = cJSON_GetArraySize(node_matrix);
        const int sieze_vector = cJSON_GetArraySize(node_vector);
        if (sieze_matrix != 9 || sieze_vector != 3) {
            LOGE("cscMatrix or cscVector size error! %d / %d\n", sieze_matrix, sieze_vector);
            ret = -1;
        }
        else {
            for (int i = 0; i < 9; i++) {
                csc_coefsx13[i] = cJSON_GetArrayItem(node_matrix, i)->valueint;
            }
            csc_coefsx13[9] = cJSON_GetArrayItem(node_vector, 0)->valueint;
            csc_coefsx13[10] = cJSON_GetArrayItem(node_vector, 1)->valueint;
            csc_coefsx13[11] = cJSON_GetArrayItem(node_vector, 2)->valueint;
        }
    }

    // adjust csc coefs if necessary
    if (passthrough == 0 && convert_mode) {
        struct post_csc_convert_mode mode;
        memcpy(&mode, convert_mode, sizeof(struct post_csc_convert_mode));
        mode.plat = VOP_VERSION_RK3572;
        mode.pixel_depth = pixel_depth;
        mode.coef_precision = precision;
        ret = rockchip_calc_post_csc(&bcsh_cfg, coef, &mode);
        ret = rockchip_calc_post_csc_coefs(&bcsh_cfg, coef, &mode);
        LOGI("\t- get csc coefs from convert mode...\n");
    }
    else {
        memcpy(coef, csc_coefsx13, sizeof(struct post_csc_coef));
        coef->range_type = convert_mode ? convert_mode->is_output_full_range : -1;
        LOGI("\t- load csc coefs from cscMatrix & cscVector...\n");
    }


    return ret;
}


void run_csc_with_coef(const void *p_src, void *p_dst, int img_w, int img_h, const struct post_csc_coef *csc_coefs,
    const struct post_csc_convert_mode *mode)
{
    const int csc_min_vl_1 = mode->is_output_full_range ? 0 : (16 << (mode->pixel_depth - 8));
    const int csc_max_vl_1 = mode->is_output_full_range ? ((1 << mode->pixel_depth) - 1) : (235 << (mode->pixel_depth - 8));
    const int csc_min_vl_2 = csc_min_vl_1;
    const int csc_max_vl_2 = mode->is_output_yuv && !mode->is_output_full_range ? (240 << (mode->pixel_depth - 8)) : csc_max_vl_1;

    // YUV444P
    ushort *p_src_y = (ushort *)p_src;
    ushort *p_src_u = (ushort *)p_src + img_w * img_h;
    ushort *p_src_v = (ushort *)p_src + img_w * img_h * 2;
    ushort *p_dst_y = (ushort *)p_dst;
    ushort *p_dst_u = (ushort *)p_dst + img_w * img_h;
    ushort *p_dst_v = (ushort *)p_dst + img_w * img_h * 2;

    const int bit_num_0 = mode->coef_precision;
    const int offset0 = csc_coefs->csc_dc0;
    const int offset1 = csc_coefs->csc_dc1;
    const int offset2 = csc_coefs->csc_dc2;

    int src_color[3] = {0};
    int dst_color[3] = {0};
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
                /* (M * Channel >> nb_shift) + Offset. low precision! */
                csc_chl0 = csc_simple_round(csc_chl0, bit_num_0);
                csc_chl1 = csc_simple_round(csc_chl1, bit_num_0);
                csc_chl2 = csc_simple_round(csc_chl2, bit_num_0);
                dst_color[0] = csc_chl0 + offset0;
                dst_color[1] = csc_chl1 + offset1;
                dst_color[2] = csc_chl2 + offset2;
            }
            else {
                /* (M * Channel + Offset) >> nb_shift. use this after RK3576! */
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

void dump_csc_regs(const char *filename, unsigned int base_addr, const struct post_csc_coef *csc_coefs, int is_post_csc)
{
    FILE *fp = stdout;
    if (filename) {
        fp = fopen(filename, "wb");
        if (fp == NULL) {
            LOGE("open file %s failed! dump to stdout instead!\n", filename);
            fp = stdout;
        }
    }

    // swap YUV order to VYU order: c0->c1, c1->c2, c2->c0
    int coefs[13] = {0};
    memcpy(coefs, csc_coefs, sizeof(int) * 12);
    coefs[12] = 1; // enable

    // coefs to regs
    const int len = 8;
    const int CM = 0xFFFF; // coef mask = 0x3FF or 0xFFFF
    int regs[8] = {0};     // 8 32bit regs total
    if (is_post_csc) {
        regs[0] = 0x1 | (coefs[12] << 1) | ((coefs[0] & CM) << 16);
        regs[1] = (coefs[1] & CM) | ((coefs[2] & CM) << 16);
        regs[2] = (coefs[3] & CM) | ((coefs[4] & CM) << 16);
        regs[3] = (coefs[5] & CM) | ((coefs[6] & CM) << 16);
        regs[4] = (coefs[7] & CM) | ((coefs[8] & CM) << 16);
    }
    else {
        regs[0] = (coefs[0] & CM) | ((coefs[1] & CM) << 16);
        regs[1] = (coefs[2] & CM) | ((coefs[3] & CM) << 16);
        regs[2] = (coefs[4] & CM) | ((coefs[5] & CM) << 16);
        regs[3] = (coefs[6] & CM) | ((coefs[7] & CM) << 16);
        regs[4] = (coefs[8] & CM);
    }
    regs[5] = coefs[9];
    regs[6] = coefs[10];
    regs[7] = coefs[11];
    LOGI("dump regs to %s, base_addr: 0x%08X, num: %d\n", fp == stdout ? "stdout" : filename, base_addr, len);

    // dump regs
    const unsigned int start_addr = base_addr;
    int i = 0;
    for (i = 0; i <= len - 4; i += 4) {
        fprintf(fp, "0x%08X:  0x%08X 0x%08X 0x%08X 0x%08X\n", start_addr + i * 4, regs[i], regs[i + 1], regs[i + 2],
            regs[i + 3]);
    }

    if (fp != stdout)
        fclose(fp);
}

int main(int argc, char *const argv[])
{
    int ret = 0;

    /* parse cmd parameters */
    opterr = 0; // disable getopt error message
    struct common_verify_cmd_config cmd_config = {0};
    struct cmd_config_addition_csc cmd_config2 = {0};
    ret = common_verify_arg_get_cmd_config(argc, argv, &cmd_config);
    if (ret < 0) {
        print_usage_addition();
        return ret;
    }

    get_cmd_config_addition(argc, argv, &cmd_config2);
    common_verify_arg_dump_config(&cmd_config);

    // check nessary parameters
    if (cmd_config.crc_file[0] == '\0') {
        snprintf(cmd_config.crc_file, 1024, "%s/csc_crc_out.dat", cmd_config.output_dir);
        LOGI(" - crc_file update to: '%s'!\n", cmd_config.crc_file);
    }

    struct post_csc_convert_mode csc_mode = {0};
    struct post_csc_coef csc_coefs = {0};
    struct post_csc csc_bcsh = {0};
    int mode_idx = cmd_config.mode;
    int pixel_depth = cmd_config2.pixel_depth;
    int precision = cmd_config2.coef_precision;

    // parse csc coefs from 'cmd_config.mode' (mode=ppii: pp-precision, ii-index)
    if (mode_idx >= 0 && mode_idx < DRM_CSC_MODE_MAX) {
        LOGI(" - get a valid csc mode(%d, %s), test with standard coefs!\n", mode_idx, g_csc_mode_strs[mode_idx]);
        memcpy(&csc_mode, &g_supported_standard_convert_mode[mode_idx], sizeof(struct post_csc_convert_mode));
        ret = rockchip_calc_post_csc(NULL, &csc_coefs, &csc_mode);
        ret = rockchip_calc_post_csc_coefs(NULL, &csc_coefs, &csc_mode);
    }
    // parse csc coefs from 'cmd_config2.mode_str'
    else if (cmd_config2.mode_str[0] != '\0') {
        ret = parse_csc_mode_str(cmd_config2.mode_str, &csc_mode);
        csc_mode.pixel_depth = cmd_config2.pixel_depth;
        csc_mode.coef_precision = cmd_config2.coef_precision;
        ret |= rockchip_calc_post_csc(NULL, &csc_coefs, &csc_mode);
        ret |= rockchip_calc_post_csc_coefs(NULL, &csc_coefs, &csc_mode);
        mode_idx = csc_get_mode_index(&csc_mode);
        LOGI(" - pixel_depth: %d\n", cmd_config2.pixel_depth);
        LOGI(" - coef_precision: %d\n", cmd_config2.coef_precision);
        LOGI(" - mode_string: %s -> index: %d\n", cmd_config2.mode_str, mode_idx);
    }
    // parse csc coefs from 'cmd_config.config_file'
    else if (cmd_config.config_file[0] != '\0') {
        ret = parse_csc_config(cmd_config.config_file, &csc_coefs, &csc_bcsh, &csc_mode);
        if (ret) {
            return ret;
        }
    }
    else {
        LOGE(" - no csc coefs or cmd_config file set, please have a check!\n");
        return -1;
    }


    LOGI(" - csc_coef matrix original: [%d, %d, %d; %d, %d, %d; %d, %d, %d]\n", csc_coefs.csc_coef00,
        csc_coefs.csc_coef01, csc_coefs.csc_coef02, csc_coefs.csc_coef10, csc_coefs.csc_coef11, csc_coefs.csc_coef12,
        csc_coefs.csc_coef20, csc_coefs.csc_coef21, csc_coefs.csc_coef22);
    LOGI(" - csc_coef offset original: [%d, %d, %d], bFullRangeOut: %d\n", csc_coefs.csc_dc0, csc_coefs.csc_dc1,
        csc_coefs.csc_dc2, csc_coefs.range_type);
    // LOGI(" - csc_coef limit: range0=[%d, %d] range1=[%d, %d]\n", csc_limits[0], csc_limits[1], csc_limits[2], csc_limits[3]);
    const int bCscEnable = 1; //csc_coefs[12] > 0;
    const int bIsInputYuv = csc_mode.is_input_yuv;
    const int bIsOutputYuv = bCscEnable ? csc_mode.is_output_yuv : bIsInputYuv;
    const int bIsPostCsc = 0;
    LOGI(" - bCscEnable: %d, bIsOutputYuv: %d, bIsPostCsc: %d\n", bCscEnable, bIsOutputYuv, bIsPostCsc);

    /* alloc i/o/t memories */
    const int frame_size = cmd_config.src_wid * cmd_config.src_hgt * 3;
    void *p_src = calloc(cmd_config.src_wid * cmd_config.src_hgt * sizeof(unsigned short) * 4, 1);
    void *p_dst = calloc(cmd_config.src_wid * cmd_config.src_hgt * sizeof(unsigned short) * 4, 1);
    if (!p_src || !p_dst) {
        return -1;
    }

    FILE *fp_src = fopen(cmd_config.input_file, "rb");
    FILE *fp_dst = fopen(cmd_config.output_file, "wb");
    if (!fp_src) {
        LOGE("Failed to open the input file '%s'! %s\n", cmd_config.input_file, strerror(errno));
        return -1;
    }
    if (!fp_dst) {
        LOGE("Failed to open the output file '%s'! %s\n", cmd_config.output_file, strerror(errno));
        return -1;
    }
    FILE *fp_crc = fopen(cmd_config.crc_file, "a");
    if (!fp_crc) {
        LOGW("Failed to open the crc output file '%s'! %s. CRC value will not be written!\n", cmd_config.crc_file,
            strerror(errno));
    }

    int crc_val = -1;
    for (int k = 0; k < cmd_config.nb_frame; k++) {
        fseek(fp_src, frame_size * k, SEEK_SET);
        ret = read_image_2_10bit_planar(fp_src, (ushort *)p_src, k, cmd_config.src_wid, cmd_config.src_hgt, cmd_config.src_fmt);
        if (ret) {
            LOGE("Failed to read frame #%d from input file '%s'! %s\n", k, cmd_config.input_file, strerror(errno));
            break;
        }

        crc_val = get_crc_for_planar_frame_10bit(p_src, cmd_config.src_wid, cmd_config.src_hgt, bIsInputYuv);
        LOGI("src CRC (%s MSB order) of frame #%04d: 0x%08X\n", bIsInputYuv ? "VYU" : "RGB", k, crc_val);

        run_csc_with_coef(p_src, p_dst, cmd_config.src_wid, cmd_config.src_hgt, &csc_coefs, &csc_mode);
        dump_csc_regs(NULL, 0x0, &csc_coefs, bIsPostCsc);
        fwrite(p_dst, 2, cmd_config.src_wid * cmd_config.src_hgt * 3, fp_dst);
        fwrite(p_src, 2, cmd_config.src_wid * cmd_config.src_hgt * 3, fp_dst); // write src after dst

        // get CRC
        crc_val = get_crc_for_planar_frame_10bit(p_dst, cmd_config.src_wid, cmd_config.src_hgt, bIsOutputYuv);
        LOGI("dst CRC (%s MSB order) of frame #%04d: 0x%08X\n", bIsOutputYuv ? "VYU" : "RGB", k, crc_val);
        if (fp_crc) {
            if (mode_idx >= 0 && mode_idx < DRM_CSC_MODE_MAX) {
                fprintf(fp_crc, "input: %s, cmd_config: csc_standard_mode_%02d_%s, crc (%s MSB order) of frame #%04d: 0x%08X\n",
                    get_basename(cmd_config.input_file), mode_idx, g_csc_mode_strs[mode_idx],
                    bIsOutputYuv ? "VYU" : "RGB", k, crc_val);
            }
            else {
                fprintf(fp_crc, "input: %s, cmd_config: %s, crc (%s MSB order) of frame #%04d: 0x%08X\n",
                    get_basename(cmd_config.input_file), get_basename(cmd_config.config_file),
                    bIsOutputYuv ? "VYU" : "RGB", k, crc_val);
            }
        }
    }
    LOGI("done. write output to file: '%s'\n", cmd_config.output_file);

    fclose(fp_src);
    fclose(fp_dst);
    if (fp_crc)
        fclose(fp_crc);
    free(p_src);
    free(p_dst);

    return ret;
}