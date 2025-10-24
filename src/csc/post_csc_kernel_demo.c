/* SPDX-License-Identifier: (GPL-2.0+ OR MIT) */
/**
 * @copyright: Copyright (C) Rockchip Electronics Co., Ltd.
 * @brief: a demo for csc kernel verification
 * @author: vance.wu@rock-chips.com
 * @history:
 *  - 2025-10-15 vance.wu: add BSCH options of cmd line arguments.
 *  - 2025-10-09 vance.wu: adjust options of cmd line arguments.
 *  - 2025-09-04 vance.wu: implementation adjustment for new csc kernel verification.
 *  - 2025-08-19 vance.wu: enable to get csc coefs with cmd line arguments.
 */


#include "rockchip_post_csc.h"
#include "rockchip_post_csc2.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#ifdef __GNUC__
#include <getopt.h>
#ifndef ARG_NONE
#define ARG_NONE no_argument
#define ARG_REQ  required_argument
#define ARG_OPT  optional_argument
#endif
#else
#include "getopt_win32.h"
#endif


const char *g_colorspace_str[] = {"YUV601", "YUV709", "YUV2020", "RGB"};
const char *g_range_str[] = {"L", "F"};

struct cmd_config_t
{
    struct post_csc_convert_mode convert_mode;
    struct post_csc bcsh_cfg;

    int b_print_all;      // [0, 1]
    int b_use_old_method; // [0, 1]
    int reg_dump_type;    // [0, 2]
    char output_file[1024];
    char platform_name[32];
};

const struct option g_cmd_args_supported_options[] = {
    {        (char *)"bright",  ARG_OPT, 0,   0},
    {      (char *)"contrast",  ARG_OPT, 0,   0},
    {    (char *)"saturation",  ARG_OPT, 0,   0},
    {           (char *)"hue",  ARG_OPT, 0,   0},
    {        (char *)"r_gain",  ARG_OPT, 0,   0},
    {        (char *)"g_gain",  ARG_OPT, 0,   0},
    {        (char *)"b_gain",  ARG_OPT, 0,   0},
    {         (char *)"r_ofs",  ARG_OPT, 0,   0},
    {         (char *)"g_ofs",  ARG_OPT, 0,   0},
    {         (char *)"b_ofs",  ARG_OPT, 0,   0},
    {      (char *)"csc_mode",  ARG_OPT, 0, 'M'},
    {   (char *)"pixel_depth",  ARG_OPT, 0, 'D'},
    {(char *)"coef_precision",  ARG_OPT, 0, 'P'},
    {   (char *)"output_file",  ARG_OPT, 0, 'o'},
    { (char *)"platform_name",  ARG_OPT, 0, 'p'},
    { (char *)"reg_dump_type",  ARG_OPT, 0, 'd'},
    {     (char *)"print_all", ARG_NONE, 0, 'a'},
    { (char *)"swap_channels", ARG_NONE, 0, 's'},
    {(char *)"use_old_method", ARG_NONE, 0, 'O'},
    {          (char *)"help", ARG_NONE, 0, 'h'},
    {                       0,        0, 0,   0}  // end of option list
};

void print_usage(const char *prog_name)
{
    printf("\nUsage: %s [options]\n", prog_name);
    printf("Program Options:\n");
    printf("      --bright         [val] | BCSH.brightness, range: [0, 511], default: 256\n");
    printf("      --contrast       [val] | BCSH.contrast,   range: [0, 511], default: 256\n");
    printf("      --saturation     [val] | BCSH.saturation, range: [0, 511], default: 256\n");
    printf("      --hue            [val] | BCSH.hue,        range: [0, 511], default: 256\n");
    printf("      --r_gain         [val] | BCSH.r_gain,     range: [0, 511], default: 256\n");
    printf("      --g_gain         [val] | BCSH.g_gain,     range: [0, 511], default: 256\n");
    printf("      --b_gain         [val] | BCSH.b_gain,     range: [0, 511], default: 256\n");
    printf("      --r_ofs          [val] | BCSH.r_offset ,  range: [0, 511], default: 256\n");
    printf("      --g_ofs          [val] | BCSH.g_offset ,  range: [0, 511], default: 256\n");
    printf("      --b_ofs          [val] | BCSH.b_offset ,  range: [0, 511], default: 256\n");
    printf("  -M  --csc_mode       [val] | csc mode, like 'rgbl_to_601f'...,  default: NULL\n");
    printf("  -D  --pixel_depth    [val] | pixel depth, range: {8,10}, default: 10bit\n");
    printf("  -P  --coef_precision [val] | coef precision, range: {8,10,13}, default: 10bit\n");
    printf("  -s  --swap_channels  [val] | swap channel type, range: [0, 5], default: 0\n");
    printf("  -o  --output_file    [val] | write all coefs to an output file when '-a' specified\n");
    printf("  -p  --platform_name  [val] | platform name like: 'rk3576'/'rk3572'...\n");
    printf("  -d  --reg_dump_type  [val] | dump type for register values, range: [0, 2]\n");
    printf("  -a  --print_all            | print coefs for all supported case,  range: [0, 1], default: 0\n");
    printf("  -O  --use_old_method       | use old method, range: [0, 1], default: 0\n");
    printf("  -h  --help                 | print this message\n");
    printf("\n");
}

int get_cmd_config(int argc, char *const argv[], struct cmd_config_t *config)
{
    int ret = 0;
    int out_clr_pos = 0;
    int opt = 0, idx = 0;
    const char *mode_str = NULL;
    while ((opt = getopt_long(argc, argv, "M:D:P:s:o:p:d:aOh", g_cmd_args_supported_options, &idx)) != -1) {
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
            if (idx >= 0 && idx <= 9) {
                config->bcsh_cfg.csc_enable = 1;
            }
        } break;
        case 'M': parse_csc_mode_str(optarg, &config->convert_mode); break;
        case 'D': config->convert_mode.pixel_depth = atoi(optarg); break;
        case 'P': config->convert_mode.coef_precision = atoi(optarg); break;
        case 's': config->convert_mode.swap_channels = atoi(optarg); break;
        case 'o': strncpy(config->output_file, optarg, 1024); break;
        case 'p': strncpy(config->platform_name, optarg, 32); break;
        case 'd': config->reg_dump_type = atoi(optarg); break;
        case 'a': config->b_print_all = 1; break;
        case 'O': config->b_use_old_method = 1; break;
        case 'h':
            print_usage(argv[0]);
            ret = -1;
            break;
        default: // ignore unknown options
            break;
        }
    }
    return ret;
}


int main(int argc, char *const argv[])
{
    int ret = 0;
    struct post_csc_coef csc_simple_coef = {0}; // [O] return CSC coefs
    struct cmd_config_t config = {0};
    config.reg_dump_type = 0; // [0, 2]
    // set CSC convert mode
    config.convert_mode.intput_color_encoding = DRM_COLOR_YCBCR_BT709;
    config.convert_mode.output_color_encoding = DRM_COLOR_YCBCR_BT709;
    config.convert_mode.is_input_yuv = 0;
    config.convert_mode.is_output_yuv = 1;
    config.convert_mode.is_input_full_range = 1;
    config.convert_mode.is_output_full_range = 1;
    config.convert_mode.plat = VOP_VERSION_RK3572;
    config.convert_mode.swap_channels = 0;
    config.convert_mode.pixel_depth = 10;    // pixel depth for input, range: {8,10}
    config.convert_mode.coef_precision = 10; // precision for CSC coef: range: {8,10,13}
    // set BCSH config
    config.bcsh_cfg.brightness = 256;
    config.bcsh_cfg.contrast = 256;
    config.bcsh_cfg.saturation = 256;
    config.bcsh_cfg.hue = 256;
    config.bcsh_cfg.r_gain = 256;
    config.bcsh_cfg.g_gain = 256;
    config.bcsh_cfg.b_gain = 256;
    config.bcsh_cfg.r_offset = 256;
    config.bcsh_cfg.g_offset = 256;
    config.bcsh_cfg.b_offset = 256;
    config.bcsh_cfg.csc_enable = 0; // enbale in 'get_cmd_config'

    /* get cmd config & dump */
    struct post_csc_convert_mode *p_mode = &config.convert_mode;
    struct post_csc *p_bcsh = &config.bcsh_cfg;
    ret = get_cmd_config(argc, argv, &config);
    if (ret < 0) {
        return ret;
    }
    if (0 == strcmp(config.platform_name, "rk3576")) {
        p_mode->plat = VOP_VERSION_RK3576;
    }
    else if (0 == strcmp(config.platform_name, "rk3538")) {
        p_mode->plat = VOP_VERSION_RK3538;
    }
    printf("dump CSC mode info from cmd line:\n");
    printf("\t- input  colorspace: %d, is_yuv: %d, is_full_range: %d\n", p_mode->intput_color_encoding,
        p_mode->is_input_yuv, p_mode->is_input_full_range);
    printf("\t- output colorspace: %d, is_yuv: %d, is_full_range: %d\n", p_mode->output_color_encoding,
        p_mode->is_output_yuv, p_mode->is_output_full_range);
    printf("\t- pixel_depth/coef_precision: %d/%dbit\n", p_mode->pixel_depth, p_mode->coef_precision);
    printf("\t- plat: 0x%08X (%s), swap_channel type: %d\n", p_mode->plat, csc_plat_name_str(p_mode->plat), p_mode->swap_channels);
    printf("\t- b/c/s/h: %d/%d/%d/%d\n", p_bcsh->brightness, p_bcsh->contrast, p_bcsh->saturation, p_bcsh->hue);
    printf("\t- r/g/b_gain: %d/%d/%d\n", p_bcsh->r_gain, p_bcsh->g_gain, p_bcsh->b_gain);
    printf("\t- r/g/b_offset: %d/%d/%d\n", p_bcsh->r_offset, p_bcsh->g_offset, p_bcsh->b_offset);
    printf("\t- output file: %s\n", config.output_file);
    printf("\t- platform name: %s\n", config.platform_name[0] == '\0' ? "RK3572 (default)" : config.platform_name);
    printf("\t- use old method: %d %s\n", config.b_use_old_method,
        config.b_use_old_method ? "(only 10-10bit coefs supported)" : "");
    printf("\t- reg_dump_type: %d\n", config.reg_dump_type);
    if (p_mode->pixel_depth < 8 || p_mode->pixel_depth > 16) {
        printf("Error: pixel depth should be in range [8,16]!\n");
        return -1;
    }
    if (p_mode->coef_precision < 8 || p_mode->coef_precision > 16) {
        printf("Error: coef precision should be in range [8,%d]!\n", 16);
        return -1;
    }

    /* get CSC coefs & dump */
    int nb_mode = 1;
    const struct post_csc_convert_mode *mode_list = p_mode;
    FILE *fp_out = stdout;
    if (config.b_print_all) {
        mode_list = g_supported_standard_convert_mode;
        nb_mode = sizeof(g_supported_standard_convert_mode) / sizeof(struct post_csc_convert_mode);
        if (config.output_file[0]) {
            fp_out = fopen(config.output_file, "wt");
            if (NULL == fp_out) {
                printf("Warning: failed to open output file: %s. %s\n", config.output_file, strerror(errno));
                fp_out = stdout; // print to stdout instead
            }
        }
        printf("'-a' option is set, dump all %d supported cases to %s\n", nb_mode, fp_out ? config.output_file : "stdout:");
    }

    struct post_csc *p_bcsh_config = config.bcsh_cfg.csc_enable ? &config.bcsh_cfg : NULL;
    printf("\n");
    for (int i = 0; i < nb_mode; i++) {
        struct post_csc_convert_mode mode = mode_list[i];
        mode.plat = p_mode->plat;
        mode.swap_channels = p_mode->swap_channels;
        mode.pixel_depth = p_mode->pixel_depth;
        mode.coef_precision = p_mode->coef_precision;

        if (config.b_use_old_method) {
            ret = rockchip_calc_post_csc(p_bcsh_config, &csc_simple_coef, &mode);
        }
        else {
            ret = rockchip_calc_post_csc_coefs(p_bcsh_config, &csc_simple_coef, &mode);
        }
        if (0 == ret) {
            fprintf(fp_out, "CSC mode: %s_%s -> %s_%s:\n",
                mode.is_input_yuv ? g_colorspace_str[mode.intput_color_encoding] : "RGB",
                g_range_str[mode.is_input_full_range], mode.is_output_yuv ? g_colorspace_str[mode.output_color_encoding] : "RGB",
                g_range_str[mode.is_output_full_range]);
            fprintf(fp_out, "\t- get CSC matrix: [%4d, %4d, %4d, %4d, %4d, %4d, %4d, %4d, %4d]\n",
                csc_simple_coef.csc_coef00, csc_simple_coef.csc_coef01, csc_simple_coef.csc_coef02,
                csc_simple_coef.csc_coef10, csc_simple_coef.csc_coef11, csc_simple_coef.csc_coef12,
                csc_simple_coef.csc_coef20, csc_simple_coef.csc_coef21, csc_simple_coef.csc_coef22);
            fprintf(fp_out, "\t- get CSC offset: [%d, %d, %d]\n", csc_simple_coef.csc_dc0, csc_simple_coef.csc_dc1,
                csc_simple_coef.csc_dc2);
        }
        else {
            printf("\t - get CSC matrix & offset failed!\n");
        }
    }

    if (nb_mode == 1 && config.reg_dump_type > 0) {
        int regs[8] = {0};
        if (config.reg_dump_type == 2) {
            regs[0] = 0x1 | (0x1 << 1) | ((csc_simple_coef.csc_coef00 & 0xFFFF) << 16); // 0-bypass, 1-en, 15-coef00
            regs[1] = (csc_simple_coef.csc_coef01 & 0xFFFF) | ((csc_simple_coef.csc_coef02 & 0xFFFF) << 16);
            regs[2] = (csc_simple_coef.csc_coef10 & 0xFFFF) | ((csc_simple_coef.csc_coef11 & 0xFFFF) << 16);
            regs[3] = (csc_simple_coef.csc_coef12 & 0xFFFF) | ((csc_simple_coef.csc_coef20 & 0xFFFF) << 16);
            regs[4] = (csc_simple_coef.csc_coef21 & 0xFFFF) | ((csc_simple_coef.csc_coef22 & 0xFFFF) << 16);
        }
        else {
            regs[0] = (csc_simple_coef.csc_coef00 & 0xFFFF) | ((csc_simple_coef.csc_coef01 & 0xFFFF) << 16);
            regs[1] = (csc_simple_coef.csc_coef02 & 0xFFFF) | ((csc_simple_coef.csc_coef10 & 0xFFFF) << 16);
            regs[2] = (csc_simple_coef.csc_coef11 & 0xFFFF) | ((csc_simple_coef.csc_coef12 & 0xFFFF) << 16);
            regs[3] = (csc_simple_coef.csc_coef20 & 0xFFFF) | ((csc_simple_coef.csc_coef21 & 0xFFFF) << 16);
            regs[4] = csc_simple_coef.csc_coef22 & 0xFFFF;
        }
        regs[5] = csc_simple_coef.csc_dc0;
        regs[6] = csc_simple_coef.csc_dc1;
        regs[7] = csc_simple_coef.csc_dc2;
        printf("\t- get CSC reg[0:4]: 0x%08X 0x%08X 0x%08X 0x%08X\n", regs[0], regs[1], regs[2], regs[3]);
        printf("\t- get CSC reg[4:8]: 0x%08X 0x%08X 0x%08X 0x%08X\n", regs[4], regs[5], regs[6], regs[7]);
    }

    if (fp_out != stdout) {
        fclose(fp_out);
        printf("write all CSC coefs to file: %s\n", config.output_file);
    }

    return ret;
}