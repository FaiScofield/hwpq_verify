/* SPDX-License-Identifier: (GPL-2.0+ OR MIT) */
/**
 * @copyright: Copyright (C) Rockchip Electronics Co., Ltd.
 * @brief: a demo for csc kernel verification
 * @author: vance.wu@rock-chips.com
 * @history:
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
    int input_color_encoding;  // [0, 2]
    int output_color_encoding; // [0, 2]
    int is_input_yuv;          // [0, 1]
    int is_output_yuv;         // [0, 1]
    int is_input_full_range;   // [0, 1]
    int is_output_full_range;  // [0, 1]
    int swap_channels;         // [0, 1] for now
    int pixel_depth;           // {8,10}
    int coef_precision;        // {8,10,13}
    int b_print_all;           // [0, 1]
    int b_use_old_method;      // [0, 1]
    int reg_dump_type;         // [0, 2]
    char output_file[1024];
    char platform_name[32];
};

const struct option g_cmd_args_supported_options[] = {
    // {     (char *)"src_color",  ARG_OPT, 0, 'c'},
    // {       (char *)"src_yuv",  ARG_OPT, 0, 'y'},
    // {     (char *)"src_range",  ARG_OPT, 0, 'r'},
    // {     (char *)"dst_color",  ARG_OPT, 0, 'C'},
    // {       (char *)"dst_yuv",  ARG_OPT, 0, 'Y'},
    // {     (char *)"dst_range",  ARG_OPT, 0, 'R'},
    {      (char *)"csc_mode",  ARG_OPT, 0, 'm'},
    {   (char *)"pixel_depth",  ARG_OPT, 0, 'd'},
    {(char *)"coef_precision",  ARG_OPT, 0, 'p'},
    {   (char *)"output_file",  ARG_OPT, 0, 'o'},
    { (char *)"platform_name",  ARG_OPT, 0, 'P'},
    { (char *)"reg_dump_type",  ARG_OPT, 0, 'r'},
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
    // printf("  -c  --src_color      [val] | input colorspcae, range: [0, 2], default: 0\n");
    // printf("  -y  --src_yuv        [val] | input yuv format, range: [0, 2], default: 0\n");
    // printf("  -r  --src_range      [val] | input full range, range: [0, 1], default: 0\n");
    // printf("  -C  --dst_color      [val] | output colorspcae, range: [0, 1], default: 1\n");
    // printf("  -Y  --dst_yuv        [val] | output yuv format, range: [0, 1], default: 1\n");
    // printf("  -R  --dst_range      [val] | output full range, range: [0, 1], default: 1\n");
    printf("  -m  --csc_mode       [val] | csc mode, like 'rgbl_to_601f'...,  default: NULL. "
           "Recommend to use this option instead of above arguments!\n");
    printf("  -d  --pixel_depth    [val] | pixel depth, range: {8,10}, default: 10bit\n");
    printf("  -p  --coef_precision [val] | coef precision, range: {8,10,13}, default: 10bit\n");
    printf("  -o  --output_file    [val] | write all coefs to an output file when '-a' specified\n");
    printf("  -P  --platform_name  [val] | platform name like: 'rk3576'/'rk3572'...\n");
    printf("  -r  --reg_dump_type  [val] | dump type for register values, range: [0, 2]\n");
    printf("  -a  --print_all            | print coefs for all supported case,  range: [0, 1], default: 0\n");
    printf("  -s  --swap_channels        | swap channels, range: [0, 1], default: 0\n");
    printf("  -O  --use_old_method       | use old method, range: [0, 1], default: 0\n");
    printf("  -h  --help                 | print this message\n");
    printf("\n");
}

int get_cmd_config(int argc, char *const argv[], struct cmd_config_t *config)
{
    int ret = 0;
    int out_clr_pos = 0;
    int opt = 0;
    const char *mode_str = NULL;
    // while ((opt = getopt_long(argc, argv, "c:y:r:C:Y:R:M:D:P:o:p:asmh", g_cmd_args_supported_options, NULL)) != -1) {
    while ((opt = getopt_long(argc, argv, "m:d:p:o:P:r:O:ash", g_cmd_args_supported_options, NULL)) != -1) {
        switch (opt) {
        // case 'c': config->input_color_encoding = atoi(optarg); break;
        // case 'y': config->is_input_yuv = atoi(optarg); break;
        // case 'r': config->is_input_full_range = atoi(optarg); break;
        // case 'C': config->output_color_encoding = atoi(optarg); break;
        // case 'Y': config->is_output_yuv = atoi(optarg); break;
        // case 'R': config->is_output_full_range = atoi(optarg); break;
        case 'd': config->pixel_depth = atoi(optarg); break;
        case 'p': config->coef_precision = atoi(optarg); break;
        case 'o': strncpy(config->output_file, optarg, 1024); break;
        case 'P': strncpy(config->platform_name, optarg, 32); break;
        case 'r': config->reg_dump_type = atoi(optarg); break;
        case 'a': config->b_print_all = 1; break;
        case 's': config->swap_channels = 1; break;
        case 'O': config->b_use_old_method = 1; break;
        case 'h':
            print_usage(argv[0]);
            ret = -1;
            break;
        case 'm': {
            // parse mode string like 'rgbl_to_601f'
            mode_str = (const char *)optarg;
            printf("parse from csc_mode_str: %s\n", mode_str);
            out_clr_pos = 8;
            config->is_input_yuv = 1;
            config->is_input_full_range = mode_str[3] == 'f' || mode_str[3] == 'F';
            if (0 == strncmp(mode_str, "rgb", 3)) {
                config->input_color_encoding = -1; // mark -1 for later update
                config->is_input_yuv = 0;
            }
            else if (0 == strncmp(mode_str, "601", 3)) {
                config->input_color_encoding = DRM_COLOR_YCBCR_BT601;
            }
            else if (0 == strncmp(mode_str, "709", 3)) {
                config->input_color_encoding = DRM_COLOR_YCBCR_BT709;
            }
            else if (0 == strncmp(mode_str, "2020", 4)) {
                config->input_color_encoding = DRM_COLOR_YCBCR_BT2020;
                config->is_input_full_range = mode_str[4] == 'f' || mode_str[4] == 'F';
                out_clr_pos = 9;
            }
            else {
                printf("unknow csc_mode_str: %s\n", mode_str);
                ret = -1;
            }

            config->is_output_yuv = 1;
            config->is_output_full_range = mode_str[out_clr_pos + 3] == 'f' || mode_str[out_clr_pos + 3] == 'F';
            if (0 == strncmp(mode_str + out_clr_pos, "rgb", 3)) {
                config->output_color_encoding = -1; // mark -1 for later update
                config->is_output_yuv = 0;
            }
            else if (0 == strncmp(mode_str + out_clr_pos, "601", 3)) {
                config->output_color_encoding = DRM_COLOR_YCBCR_BT601;
            }
            else if (0 == strncmp(mode_str + out_clr_pos, "709", 3)) {
                config->output_color_encoding = DRM_COLOR_YCBCR_BT709;
            }
            else if (0 == strncmp(mode_str + out_clr_pos, "2020", 4)) {
                config->output_color_encoding = DRM_COLOR_YCBCR_BT2020;
                config->is_output_full_range = mode_str[out_clr_pos + 4] == 'f' || mode_str[out_clr_pos + 4] == 'F';
            }
            else {
                printf("unknow csc_mode_str: %s\n", mode_str);
                ret = -1;
            }

            // update input/output colorspace if not specified
            if (config->input_color_encoding == -1) {
                config->input_color_encoding = config->output_color_encoding == -1 ? DRM_COLOR_YCBCR_BT709
                                                                                   : config->output_color_encoding;
            }
            if (config->output_color_encoding == -1) {
                config->output_color_encoding = config->input_color_encoding;
            }
        } break;
        default: // ignore unknown options
            break;
        }
    }
    return ret;
}


int main(int argc, char *const argv[])
{
    int ret = 0;
    struct post_csc_coef csc_simple_coef = {0};      // [O] return CSC coefs
    struct post_csc csc_cfg = {0};                   // [I] CSC config
    struct post_csc_convert_mode convert_mode = {0}; // [I] CSC convert mode
    struct cmd_config_t config = {0};
    config.output_color_encoding = 1;
    config.is_output_yuv = 1;
    config.is_output_full_range = 1;
    config.pixel_depth = 10;    // pixel depth for input, range: {8,10}
    config.coef_precision = 10; // precision for CSC coef: range: {8,10,13}
    config.reg_dump_type = 0;   // [0, 2]

    // get cmd config & dump
    ret = get_cmd_config(argc, argv, &config);
    if (ret < 0) {
        return ret;
    }
    printf("dump CSC mode info from cmd line:\n");
    printf("\t- input  colorspace: %d, is_yuv: %d, is_full_range: %d\n", config.input_color_encoding,
        config.is_input_yuv, config.is_input_full_range);
    printf("\t- output colorspace: %d, is_yuv: %d, is_full_range: %d\n", config.output_color_encoding,
        config.is_output_yuv, config.is_output_full_range);
    printf("\t- pixel_depth/coef_precision: %d/%dbit\n", config.pixel_depth, config.coef_precision);
    printf("\t- swap_channels: %d, channel order: %s\n", config.swap_channels,
        config.swap_channels ? "B-G-R/V-Y-U" : "R-G-B/Y-U-V");
    printf("\t- output file: %s\n", config.output_file);
    printf("\t- platform name: %s\n", config.platform_name[0] == '\0' ? "RK3572 (default)" : config.platform_name);
    printf("\t- use old method: %d %s\n", config.b_use_old_method,
        config.b_use_old_method ? "(only 10-10bit coefs supported)" : "");
    printf("\t- reg_dump_type: %d\n", config.reg_dump_type);
    if (config.pixel_depth < 8 || config.pixel_depth > 16) {
        printf("Error: pixel depth should be in range [8,16]!\n");
        return -1;
    }
    if (config.coef_precision < 8 || config.coef_precision > 16) {
        printf("Error: coef precision should be in range [8,%d]!\n", 16);
        return -1;
    }

    // set CSC config
    csc_cfg.hue = 256;
    csc_cfg.saturation = 256;
    csc_cfg.contrast = 256;
    csc_cfg.brightness = 256;
    csc_cfg.r_gain = 256;
    csc_cfg.g_gain = 256;
    csc_cfg.b_gain = 256;
    csc_cfg.r_offset = 256;
    csc_cfg.g_offset = 256;
    csc_cfg.b_offset = 256;
    csc_cfg.csc_enable = 0;
    /* const */ struct post_csc *bcsh_config = csc_cfg.csc_enable ? &csc_cfg : NULL;

    // set CSC convert mode
    convert_mode.intput_color_encoding = (enum drm_color_encoding)config.input_color_encoding;
    convert_mode.output_color_encoding = (enum drm_color_encoding)config.output_color_encoding;
    convert_mode.is_input_yuv = config.is_input_yuv;
    convert_mode.is_output_yuv = config.is_output_yuv;
    convert_mode.is_input_full_range = config.is_input_full_range;
    convert_mode.is_output_full_range = config.is_output_full_range;
    convert_mode.swap_channels = config.swap_channels;
    convert_mode.pixel_depth = config.pixel_depth;
    convert_mode.coef_precision = config.coef_precision;
    convert_mode.plat = VOP_VERSION_RK3572;
    if (0 == strcmp(config.platform_name, "rk3576")) {
        convert_mode.plat = VOP_VERSION_RK3576;
    }

    // get CSC coefs & dump
    int nb_mode = 1;
    const struct post_csc_convert_mode *mode_list = &convert_mode;
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


    printf("\n");
    for (int i = 0; i < nb_mode; i++) {
        struct post_csc_convert_mode mode = mode_list[i];
        mode.swap_channels = config.swap_channels;
        mode.pixel_depth = config.pixel_depth;
        mode.coef_precision = config.coef_precision;

        if (config.b_use_old_method) {
            ret = rockchip_calc_post_csc(bcsh_config, &csc_simple_coef, &mode);
        }
        else {
            ret = rockchip_calc_post_csc_coefs(bcsh_config, &csc_simple_coef, &mode);
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