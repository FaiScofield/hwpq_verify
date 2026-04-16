/**
 * @copyright Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @description: csc_verify_demo.c
 * @author: vance.wu@rock-chips.com
 * @create: 2025-09-05
 * @history:
 *  - 2025-12-30 vance.wu: fix BCSH etc. options of cmd line arguments.
 *  - 2025-11-14 vance.wu: add CSC_Y2Y support for 8bit YUV420/422 formats.
 *  - 2025-10-15 vance.wu: add BSCH options of cmd line arguments.
 *  - 2025-09-10 vance.wu: print crc32 value for input/output data.
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


struct cmd_config_addition_csc {
    struct post_csc_convert_mode convert_mode;
    struct post_csc bcsh_cfg;

    char mode_str[32];
    bool b_use_float_coef; // {0, 1} TODO
    bool b_use_old_method; // [0, 1]
    int reg_dump_type;     // [0, 2]
};

void print_usage_addition()
{
    LOGI("CSC Aditional Options:\n");
    LOGI("      --bright         [val] | BCSH.brightness, range: [0, 511], default: 256\n");
    LOGI("      --contrast       [val] | BCSH.contrast,   range: [0, 511], default: 256\n");
    LOGI("      --saturation     [val] | BCSH.saturation, range: [0, 511], default: 256\n");
    LOGI("      --hue            [val] | BCSH.hue,        range: [0, 511], default: 256\n");
    LOGI("      --r_gain         [val] | BCSH.r_gain,     range: [0, 511], default: 256\n");
    LOGI("      --g_gain         [val] | BCSH.g_gain,     range: [0, 511], default: 256\n");
    LOGI("      --b_gain         [val] | BCSH.b_gain,     range: [0, 511], default: 256\n");
    LOGI("      --r_ofs          [val] | BCSH.r_offset ,  range: [0, 511], default: 256\n");
    LOGI("      --g_ofs          [val] | BCSH.g_offset ,  range: [0, 511], default: 256\n");
    LOGI("      --b_ofs          [val] | BCSH.b_offset ,  range: [0, 511], default: 256\n");
    LOGI("  -M  --csc_mode       [val] | csc mode string like: '709l_to_rgbf', default: 'NULL'\n");
    LOGI("  -D  --pixel_depth    [val] | pixel depth, range: {8,10}, default: 10bit\n");
    LOGI("  -P  --coef_precision [val] | coef precision, range: {8,10,13}, default: 10bit\n");
    LOGI("  -d  --reg_dump_type  [val] | dump type for register values, range: [0, 2]\n");
    LOGI("  -O  --use_old_method       | use old method, range: [0, 1], default: 0\n");

    LOGI("\n");
}

int get_cmd_config_addition(int argc, char *const argv[], struct cmd_config_addition_csc *config)
{
    static const struct option g_cmd_args_options_csc[] = {
        {(char *)"bright",         ARG_REQ,  0, 0  }, // 0
        {(char *)"contrast",       ARG_REQ,  0, 0  }, // 1
        {(char *)"saturation",     ARG_REQ,  0, 0  }, // 2
        {(char *)"hue",            ARG_REQ,  0, 0  }, // 3
        {(char *)"r_gain",         ARG_REQ,  0, 0  }, // 4
        {(char *)"g_gain",         ARG_REQ,  0, 0  },
        {(char *)"b_gain",         ARG_REQ,  0, 0  },
        {(char *)"r_offset",       ARG_REQ,  0, 0  }, // 7
        {(char *)"g_offset",       ARG_REQ,  0, 0  },
        {(char *)"b_offset",       ARG_REQ,  0, 0  },
        {(char *)"csc_mode",       ARG_REQ,  0, 'M'},
        {(char *)"pixel_depth",    ARG_REQ,  0, 'D'},
        {(char *)"coef_precision", ARG_REQ,  0, 'P'},
        {(char *)"reg_dump_type",  ARG_REQ,  0, 'd'},
        {(char *)"use_old_method", ARG_NONE, 0, 'O'},
        {0,                        0,        0, 0  }  // end of option list
    };

    config->convert_mode.plat = VOP_VERSION_RK3572;
    config->convert_mode.swap_channels = 0; // always be 0 in this file!
    config->convert_mode.pixel_depth = 10;
    config->convert_mode.coef_precision = 10;
    config->bcsh_cfg.brightness = 256;
    config->bcsh_cfg.contrast = 256;
    config->bcsh_cfg.saturation = 256;
    config->bcsh_cfg.hue = 256;
    config->bcsh_cfg.r_gain = 256;
    config->bcsh_cfg.g_gain = 256;
    config->bcsh_cfg.b_gain = 256;
    config->bcsh_cfg.r_offset = 256;
    config->bcsh_cfg.g_offset = 256;
    config->bcsh_cfg.b_offset = 256;
    config->bcsh_cfg.csc_enable = 1;

    /*! NOTE: need to reset 'optind' before parsing addition options */
    optind = 1;
    int opt = -1;
    int idx = -1;
    while ((opt = getopt_long(argc, argv, "-M:D:P:d:O", g_cmd_args_options_csc, &idx)) != -1) {
        switch (opt) {
        case 0: {
            switch (idx) {
            case 0: config->bcsh_cfg.brightness = atoi(optarg); break;
            case 1: config->bcsh_cfg.contrast = atoi(optarg); break;
            case 2: config->bcsh_cfg.saturation = atoi(optarg); break;
            case 3: config->bcsh_cfg.hue = atoi(optarg); break;
            case 4: config->bcsh_cfg.r_gain = atoi(optarg); break;
            case 5: config->bcsh_cfg.g_gain = atoi(optarg); break;
            case 6: config->bcsh_cfg.b_gain = atoi(optarg); break;
            case 7: config->bcsh_cfg.r_offset = atoi(optarg); break;
            case 8: config->bcsh_cfg.g_offset = atoi(optarg); break;
            case 9: config->bcsh_cfg.b_offset = atoi(optarg); break;
            }
            LOGI(" - get %dth option: %s = %s\n", idx, g_cmd_args_options_csc[idx].name, optarg);
        } break;
        case 'M': strncpy(config->mode_str, optarg, 32); break;
        case 'D': config->convert_mode.pixel_depth = atoi(optarg); break;
        case 'P': config->convert_mode.coef_precision = atoi(optarg); break;
        case 'd': config->reg_dump_type = atoi(optarg); break;
        case 'O': config->b_use_old_method = 1; break;
        default:  break;
        }
    }

    return 0;
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
        LOGI("\t- load cscConvertMode: %d (%s)\n", mode_idx, g_supported_csc_mode_str[mode_idx]);
        if (mode_idx >= 0 && mode_idx < CSC_MODE_MAX) {
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

void run_csc_with_coef(const void *p_src, void *p_dst, int img_w, int img_h, int planar_fmt,
    const struct post_csc_coef *csc_coefs, const struct post_csc_convert_mode *mode)
{
    const int csc_min_vl_1 = mode->is_output_full_range ? 0 : (16 << (mode->pixel_depth - 8));
    const int csc_max_vl_1 = mode->is_output_full_range ? ((1 << mode->pixel_depth) - 1) : (235 << (mode->pixel_depth - 8));
    const int csc_min_vl_2 = csc_min_vl_1;
    const int csc_max_vl_2 = mode->is_output_yuv && !mode->is_output_full_range ? (240 << (mode->pixel_depth - 8)) : csc_max_vl_1;

    const int bit_num_0 = mode->coef_precision;
    const int offset0 = csc_coefs->csc_dc0;
    const int offset1 = csc_coefs->csc_dc1;
    const int offset2 = csc_coefs->csc_dc2;

    int src_color[3] = {0};
    int dst_color[3] = {0};

    if (planar_fmt == RGB_PLANAR10LSB || planar_fmt == YUV444P_10LSB) {
        // 10bit YUV444P or RGB planar
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
                    /* (M * Channel >> nb_shift) + Offset. low precision! */
                    dst_color[0] = csc_simple_round(csc_chl0, bit_num_0) + offset0;
                    dst_color[1] = csc_simple_round(csc_chl1, bit_num_0) + offset1;
                    dst_color[2] = csc_simple_round(csc_chl2, bit_num_0) + offset2;
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
    else if (planar_fmt == RGB_PLANAR || planar_fmt == YUV444P) {
        // 8bit YUV444P or RGB planar
        uchar *p_src_y = (uchar *)p_src;
        uchar *p_src_u = (uchar *)p_src + img_w * img_h;
        uchar *p_src_v = (uchar *)p_src + img_w * img_h * 2;
        uchar *p_dst_y = (uchar *)p_dst;
        uchar *p_dst_u = (uchar *)p_dst + img_w * img_h;
        uchar *p_dst_v = (uchar *)p_dst + img_w * img_h * 2;
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
                    dst_color[0] = csc_simple_round(csc_chl0, bit_num_0) + offset0;
                    dst_color[1] = csc_simple_round(csc_chl1, bit_num_0) + offset1;
                    dst_color[2] = csc_simple_round(csc_chl2, bit_num_0) + offset2;
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
    else if (mode->is_input_yuv && mode->is_input_yuv && planar_fmt == YUV422P) {
        // Y2Y for 8bit YUV422P
        uchar *p_src_y = (uchar *)p_src;
        uchar *p_src_u = (uchar *)p_src + img_w * img_h;
        uchar *p_src_v = (uchar *)p_src + img_w * img_h * 3 / 2;
        uchar *p_dst_y = (uchar *)p_dst;
        uchar *p_dst_u = (uchar *)p_dst + img_w * img_h;
        uchar *p_dst_v = (uchar *)p_dst + img_w * img_h * 3 / 2;

        int src_luma[2] = {0};
        for (int i = 0; i < img_h; i++) {
            for (int j = 0; j < img_w / 2; j++) {
                const int idx_y = i * img_w + j * 2;
                const int idx_c = i * img_w / 2 + j;
                src_luma[0] = p_src_y[idx_y + 0];
                src_luma[1] = p_src_y[idx_y + 1];
                src_color[0] = (src_luma[0] + src_luma[1] + 1) >> 1;
                src_color[1] = p_src_u[idx_c];
                src_color[2] = p_src_v[idx_c];

                int dy0 = csc_coefs->csc_coef00 * src_luma[0] + csc_coefs->csc_coef01 * src_color[1] +
                          csc_coefs->csc_coef02 * src_color[2];
                int dy1 = csc_coefs->csc_coef00 * src_luma[1] + csc_coefs->csc_coef01 * src_color[1] +
                          csc_coefs->csc_coef02 * src_color[2];
                int du = csc_coefs->csc_coef10 * src_color[0] + csc_coefs->csc_coef11 * src_color[1] +
                         csc_coefs->csc_coef12 * src_color[2];
                int dv = csc_coefs->csc_coef20 * src_color[0] + csc_coefs->csc_coef21 * src_color[1] +
                         csc_coefs->csc_coef22 * src_color[2];
                if (mode->plat == VOP_VERSION_RK3576) {
                    /* (M * Channel >> nb_shift) + Offset. low precision! */
                    dy0 = csc_simple_round(dy0, bit_num_0) + offset0;
                    dy1 = csc_simple_round(dy1, bit_num_0) + offset0;
                    du = csc_simple_round(du, bit_num_0) + offset1;
                    dv = csc_simple_round(dv, bit_num_0) + offset2;
                }
                else {
                    /* (M * Channel + Offset) >> nb_shift. use this after RK3576! */
                    dy0 = csc_simple_round(dy0 + offset0, bit_num_0);
                    dy1 = csc_simple_round(dy1 + offset0, bit_num_0);
                    du = csc_simple_round(du + offset1, bit_num_0);
                    dv = csc_simple_round(dv + offset2, bit_num_0);
                }
                p_dst_y[idx_y + 0] = CLIP(dy0, csc_min_vl_1, csc_max_vl_1);
                p_dst_y[idx_y + 1] = CLIP(dy1, csc_min_vl_1, csc_max_vl_1);
                p_dst_u[idx_c] = CLIP(du, csc_min_vl_2, csc_max_vl_2);
                p_dst_v[idx_c] = CLIP(dv, csc_min_vl_2, csc_max_vl_2);
            }
        }
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
    else if (mode->is_input_yuv && mode->is_input_yuv && planar_fmt == YUV420P) {
        // Y2Y for 8bit YUV420P
        uchar *p_src_y = (uchar *)p_src;
        uchar *p_src_u = (uchar *)p_src + img_w * img_h;
        uchar *p_src_v = (uchar *)p_src + img_w * img_h * 5 / 4;
        uchar *p_dst_y = (uchar *)p_dst;
        uchar *p_dst_u = (uchar *)p_dst + img_w * img_h;
        uchar *p_dst_v = (uchar *)p_dst + img_w * img_h * 5 / 4;

        int src_luma[4] = {0};
        for (int i = 0; i < img_h / 2; i++) {
            for (int j = 0; j < img_w / 2; j++) {
                const int idx_y0 = i * 2 * img_w + j * 2;
                const int idx_y1 = idx_y0 + img_w;
                const int idx_uv = i * img_w / 2 + j;
                src_luma[0] = p_src_y[idx_y0 + 0];
                src_luma[1] = p_src_y[idx_y0 + 1];
                src_luma[2] = p_src_y[idx_y1 + 0];
                src_luma[3] = p_src_y[idx_y1 + 1];
                src_color[0] = (src_luma[0] + src_luma[1] + src_luma[2] + src_luma[3] + 2) >> 2;
                src_color[1] = p_src_u[idx_uv];
                src_color[2] = p_src_v[idx_uv];

                int dy0 = csc_coefs->csc_coef00 * src_luma[0] + csc_coefs->csc_coef01 * src_color[1] +
                          csc_coefs->csc_coef02 * src_color[2];
                int dy1 = csc_coefs->csc_coef00 * src_luma[1] + csc_coefs->csc_coef01 * src_color[1] +
                          csc_coefs->csc_coef02 * src_color[2];
                int dy2 = csc_coefs->csc_coef00 * src_luma[2] + csc_coefs->csc_coef01 * src_color[1] +
                          csc_coefs->csc_coef02 * src_color[2];
                int dy3 = csc_coefs->csc_coef00 * src_luma[3] + csc_coefs->csc_coef01 * src_color[1] +
                          csc_coefs->csc_coef02 * src_color[2];
                int du = csc_coefs->csc_coef10 * src_color[0] + csc_coefs->csc_coef11 * src_color[1] +
                         csc_coefs->csc_coef12 * src_color[2];
                int dv = csc_coefs->csc_coef20 * src_color[0] + csc_coefs->csc_coef21 * src_color[1] +
                         csc_coefs->csc_coef22 * src_color[2];
                if (mode->plat == VOP_VERSION_RK3576) {
                    /* (M * Channel >> nb_shift) + Offset. low precision! */
                    dy0 = csc_simple_round(dy0, bit_num_0) + offset0;
                    dy1 = csc_simple_round(dy1, bit_num_0) + offset0;
                    dy2 = csc_simple_round(dy2, bit_num_0) + offset0;
                    dy3 = csc_simple_round(dy3, bit_num_0) + offset0;
                    du = csc_simple_round(du, bit_num_0) + offset1;
                    dv = csc_simple_round(dv, bit_num_0) + offset2;
                }
                else {
                    /* (M * Channel + Offset) >> nb_shift. use this after RK3576! */
                    dy0 = csc_simple_round(dy0 + offset0, bit_num_0);
                    dy1 = csc_simple_round(dy1 + offset0, bit_num_0);
                    dy2 = csc_simple_round(dy2 + offset0, bit_num_0);
                    dy3 = csc_simple_round(dy3 + offset0, bit_num_0);
                    du = csc_simple_round(du + offset1, bit_num_0);
                    dv = csc_simple_round(dv + offset2, bit_num_0);
                }
                p_dst_y[idx_y0 + 0] = CLIP(dy0, csc_min_vl_1, csc_max_vl_1);
                p_dst_y[idx_y0 + 1] = CLIP(dy1, csc_min_vl_1, csc_max_vl_1);
                p_dst_y[idx_y1 + 0] = CLIP(dy2, csc_min_vl_1, csc_max_vl_1);
                p_dst_y[idx_y1 + 1] = CLIP(dy3, csc_min_vl_1, csc_max_vl_1);
                p_dst_u[idx_uv] = CLIP(du, csc_min_vl_2, csc_max_vl_2);
                p_dst_v[idx_uv] = CLIP(dv, csc_min_vl_2, csc_max_vl_2);
            }
        }
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
    else {
        LOGE("%s: unsupported planar format %d!\n", __func__, planar_fmt);
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

    ret = get_cmd_config_addition(argc, argv, &cmd_config2);
    common_verify_arg_dump_config(&cmd_config);

    struct post_csc_convert_mode *p_mode = &cmd_config2.convert_mode;
    struct post_csc *p_bcsh = &cmd_config2.bcsh_cfg;
    const int depth = (cmd_config.src_fmt < 10 && cmd_config.dst_fmt < 10) ? 8 : 10;
    if (8 == depth) {
        p_mode->pixel_depth = 8;
    }
    LOGI("dump CSC mode info from cmd line:\n");
    LOGI(" - pixel_depth/coef_precision: %d/%dbit\n", p_mode->pixel_depth, p_mode->coef_precision);
    LOGI(" - b/c/s/h: %d/%d/%d/%d\n", p_bcsh->brightness, p_bcsh->contrast, p_bcsh->saturation, p_bcsh->hue);
    LOGI(" - r/g/b_gain: %d/%d/%d\n", p_bcsh->r_gain, p_bcsh->g_gain, p_bcsh->b_gain);
    LOGI(" - r/g/b_offset: %d/%d/%d\n", p_bcsh->r_offset, p_bcsh->g_offset, p_bcsh->b_offset);
    LOGI(" - use old method: %d %s\n", cmd_config2.b_use_old_method,
        cmd_config2.b_use_old_method ? "(only 10-10bit coefs supported)" : "");

    // check nessary parameters
    if (cmd_config.crc_file[0] == '\0') {
        snprintf(cmd_config.crc_file, 1024, "%s/csc_crc_out.dat", cmd_config.output_dir);
        LOGI(" - crc_file update to: '%s'!\n", cmd_config.crc_file);
    }

    struct post_csc_convert_mode csc_mode = {0}; // final csc mode
    struct post_csc_coef csc_coefs = {0};        // final csc coefs
    int mode_idx = cmd_config.mode;
    const int pixel_depth = p_mode->pixel_depth;
    const int precision = p_mode->coef_precision;
    const bool b_use_old_method = cmd_config2.b_use_old_method;

    // parse csc coefs from 'cmd_config.mode' (mode=ppii: pp-precision, ii-index)
    if (mode_idx >= 0 && mode_idx < CSC_MODE_MAX) {
        LOGI(" - get a valid csc mode(%d, %s), test with standard coefs!\n", mode_idx, g_supported_csc_mode_str[mode_idx]);
        memcpy(&csc_mode, &g_supported_standard_convert_mode[mode_idx], sizeof(struct post_csc_convert_mode));
        csc_mode.plat = p_mode->plat;
        csc_mode.swap_channels = 0;
        csc_mode.pixel_depth = p_mode->pixel_depth;
        csc_mode.coef_precision = p_mode->coef_precision;
        if (b_use_old_method) {
            ret = rockchip_calc_post_csc(NULL, &csc_coefs, &csc_mode);
        }
        else {
            ret = rockchip_calc_post_csc_coefs(NULL, &csc_coefs, &csc_mode);
        }
    }
    // parse csc coefs from 'cmd_config2.mode_str'
    else if (cmd_config2.mode_str[0] != '\0') {
        ret = parse_csc_mode_str(cmd_config2.mode_str, &csc_mode);
        if (ret) {
            return ret;
        }
        csc_mode.plat = p_mode->plat;
        csc_mode.swap_channels = 0;
        csc_mode.pixel_depth = p_mode->pixel_depth;
        csc_mode.coef_precision = p_mode->coef_precision;
        if (b_use_old_method) {
            ret = rockchip_calc_post_csc(p_bcsh, &csc_coefs, &csc_mode);
        }
        else {
            ret = rockchip_calc_post_csc_coefs(p_bcsh, &csc_coefs, &csc_mode);
        }
        mode_idx = csc_get_mode_index(&csc_mode);
        LOGI(" - mode_string: %s -> mode_index: %d\n", cmd_config2.mode_str, mode_idx);
        if (ret || mode_idx < 0 || mode_idx >= CSC_MODE_MAX) {
            return ret;
        }
    }
    // parse csc coefs from 'cmd_config.config_file'
    else if (cmd_config.config_file[0] != '\0') {
        ret = parse_csc_config(cmd_config.config_file, &csc_coefs, p_bcsh, &csc_mode);
        if (ret) {
            return ret;
        }
    }
    else {
        csc_mode.plat = p_mode->plat;
        csc_mode.swap_channels = 0;
        csc_mode.pixel_depth = p_mode->pixel_depth;
        csc_mode.coef_precision = p_mode->coef_precision;
        csc_mode.is_input_yuv = common_verify_imgfmt_is_yuv(cmd_config.src_fmt);
        csc_mode.is_input_full_range = common_verify_clrspc_is_full_range(cmd_config.src_clrspc);
        csc_mode.is_output_yuv = common_verify_imgfmt_is_yuv(cmd_config.dst_fmt);
        csc_mode.is_output_full_range = common_verify_clrspc_is_full_range(cmd_config.dst_clrspc);
        int src_encoding = common_verify_clrspc_to_kernel_encoding(cmd_config.src_clrspc);
        int dst_encoding = common_verify_clrspc_to_kernel_encoding(cmd_config.dst_clrspc);
        if (csc_mode.is_input_yuv && !csc_mode.is_output_yuv) {
            dst_encoding = src_encoding;
        }
        else if (!csc_mode.is_input_yuv && csc_mode.is_output_yuv) {
            src_encoding = dst_encoding;
        }
        else if (!csc_mode.is_input_yuv && !csc_mode.is_output_yuv) {
            src_encoding = dst_encoding = 1; // 709
        }
        csc_mode.intput_color_encoding = src_encoding;
        csc_mode.output_color_encoding = dst_encoding;
        if (b_use_old_method) {
            ret = rockchip_calc_post_csc(p_bcsh, &csc_coefs, &csc_mode);
        }
        else {
            ret = rockchip_calc_post_csc_coefs(p_bcsh, &csc_coefs, &csc_mode);
        }
        mode_idx = csc_get_mode_index(&csc_mode);
        LOGI(" - get mode_index: %d(%s) from IO formats.\n", mode_idx, g_supported_csc_mode_str[mode_idx]);
        if (ret || mode_idx < 0 || mode_idx >= CSC_MODE_MAX) {
            return ret;
        }
    }

    LOGI(" - get csc_coef matrix: [%d, %d, %d; %d, %d, %d; %d, %d, %d]\n", csc_coefs.csc_coef00, csc_coefs.csc_coef01,
        csc_coefs.csc_coef02, csc_coefs.csc_coef10, csc_coefs.csc_coef11, csc_coefs.csc_coef12, csc_coefs.csc_coef20,
        csc_coefs.csc_coef21, csc_coefs.csc_coef22);
    LOGI(" - get csc_coef offset: [%d, %d, %d], bFullRangeOut: %d\n", csc_coefs.csc_dc0, csc_coefs.csc_dc1,
        csc_coefs.csc_dc2, csc_coefs.range_type);
    const int bCscEnable = 1; //csc_coefs[12] > 0;
    const int bIsInputYuv = csc_mode.is_input_yuv;
    const int bIsOutputYuv = bCscEnable ? csc_mode.is_output_yuv : bIsInputYuv;
    const int bIsPostCsc = 0;
    LOGI(" - bCscEnable: %d, bIsOutputYuv: %d, bIsPostCsc: %d\n", bCscEnable, bIsOutputYuv, bIsPostCsc);

    /* alloc i/o/t memories */
    const size_t frame_size_max = cmd_config.src_wid * cmd_config.src_hgt * 4 * 2; // 4 channels x 16bpp
    void *p_src = calloc(frame_size_max, 1);
    void *p_dst = calloc(frame_size_max, 1);
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
    const int mid_fmt = common_verify_imgfmt_get_def_planar(cmd_config.src_fmt, depth);
    LOGI("mid_fmt: %d (%s)\n", mid_fmt, common_verify_imgfmt_name(mid_fmt));

    for (int k = 0; k < cmd_config.nb_frame; k++) {
        ret = image_read_to_planar(fp_src, p_src, k, cmd_config.src_wid, cmd_config.src_hgt, cmd_config.src_wid_vir,
            cmd_config.src_hgt_vir, cmd_config.src_fmt, depth, cmd_config.dither_up);
        if (ret) {
            LOGE("Failed to read frame #%d from input file '%s'! %s\n", k, cmd_config.input_file, strerror(errno));
            break;
        }

        if (depth == 10) {
            crc_val = get_crc_for_planar_frame_10bit(p_src, cmd_config.src_wid, cmd_config.src_hgt, bIsInputYuv);
            LOGI("src CRC (%s MSB order) of frame #%04d: 0x%08X\n", bIsInputYuv ? "VYU" : "RGB", k, crc_val);
        }

        run_csc_with_coef(p_src, p_dst, cmd_config.src_wid, cmd_config.src_hgt, mid_fmt, &csc_coefs, &csc_mode);
        dump_csc_regs(NULL, 0x0, &csc_coefs, bIsPostCsc);
        ret = image_write_from_plannar(fp_dst, (ushort *)p_dst, k, cmd_config.dst_wid, cmd_config.dst_hgt,
            cmd_config.dst_wid_vir, cmd_config.dst_hgt_vir, cmd_config.dst_fmt, depth, cmd_config.dither_dn);
        if (ret) {
            break;
        }
        // fwrite(p_src, 2, cmd_config.src_wid * cmd_config.src_hgt * 3, fp_dst); // write src after dst

        // get CRC
        if (depth == 10) {
            crc_val = get_crc_for_planar_frame_10bit(p_dst, cmd_config.src_wid, cmd_config.src_hgt, bIsOutputYuv);
            LOGI("dst CRC (%s MSB order) of frame #%04d: 0x%08X\n", bIsOutputYuv ? "VYU" : "RGB", k, crc_val);
            if (fp_crc) {
                if (mode_idx >= 0 && mode_idx < CSC_MODE_MAX) {
                    fprintf(fp_crc,
                        "input: %s, cmd_config: csc_standard_mode_%02d_%s, crc (%s MSB order) of frame #%04d: 0x%08X\n",
                        get_basename(cmd_config.input_file), mode_idx, g_supported_csc_mode_str[mode_idx],
                        bIsOutputYuv ? "VYU" : "RGB", k, crc_val);
                }
                else {
                    fprintf(fp_crc, "input: %s, cmd_config: %s, crc (%s MSB order) of frame #%04d: 0x%08X\n",
                        get_basename(cmd_config.input_file), get_basename(cmd_config.config_file),
                        bIsOutputYuv ? "VYU" : "RGB", k, crc_val);
                }
            }
        }
    }
    if (0 == ret) {
        LOGI("done. write output to file: '%s'\n", cmd_config.output_file);
    }
    else {
        LOGE("error happened, please have a check!\n");
    }

    fclose(fp_src);
    fclose(fp_dst);
    if (fp_crc)
        fclose(fp_crc);
    free(p_src);
    free(p_dst);

    return ret;
}