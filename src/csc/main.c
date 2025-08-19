/* SPDX-License-Identifier: (GPL-2.0+ OR MIT) */
/*
 * Copyright (C) Rockchip Electronics Co., Ltd.
 * Author:
 *      Wu Fangyi <vance.wu@rock-chips.com>
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#ifdef __GNUC__
#include <getopt.h>
#else
#include "getopt_win32.h"
#endif
#include "rockchip_post_csc.h"


struct cmd_config_t
{
    int input_color_encoding;  // [0, 2]
    int output_color_encoding; // [0, 2]
    int is_input_yuv;          // [0, 1]
    int is_output_yuv;         // [0, 1]
    int is_input_full_range;   // [0, 1]
    int is_output_full_range;  // [0, 1]
    int precision;             // {8,10,13}
    int swap_channels;         // [0, 1] for now
    int b_print_all;           // [0, 1]
};

void print_usage(const char *prog_name)
{
    printf("\nUsage: %s [options]\n", prog_name);
    printf("Program Options:\n");
    printf("  -c  --src_clr      [src_color] | input colorspcae, range: [0, 2], default: 0\n");
    printf("  -y  --src_yuv        [src_yuv] | input yuv format, range: [0, 2], default: 0\n");
    printf("  -f  --src_range    [src_range] | input full range, range: [0, 1], default: 0\n");
    printf("  -C  --dst_clr      [dst_color] | output colorspcae, range: [0, 1], default: 1\n");
    printf("  -Y  --dst_yuv        [dst_yuv] | output yuv format, range: [0, 1], default: 1\n");
    printf("  -F  --dst_range    [dst_range] | output full range, range: [0, 1], default: 1\n");
    printf("  -m  --csc_mode      [csc_mode] | csc mode, like 'rgbl_to_601f'..., default: NULL\n");
    printf("  -p  --precision    [precision] | coef precision, range: {8,10,13}, default: 10bit\n");
    printf("  -s  --swap_channels            | swap channels, range: [0, 1], default: 0\n");
    printf("  -a  --print_all                | print coefs for all supported case,  range: [0, 1], default: 0\n");
    printf("  -h  --help                     | print this message\n");
    printf("\n");
}

int get_cmd_config(int argc, char *const argv[], struct cmd_config_t *config)
{
    int ret = 0;
    int out_clr_pos = 0;
    int opt = 0;
    const char *mode_str = NULL;
    while ((opt = getopt(argc, argv, "c:y:f:C:Y:F:m:p:sah")) != -1)
    {
        switch (opt)
        {
        case 'c':
            config->input_color_encoding = atoi(optarg);
            break;
        case 'y':
            config->is_input_yuv = atoi(optarg);
            break;
        case 'f':
            config->is_input_full_range = atoi(optarg);
            break;
        case 'C':
            config->output_color_encoding = atoi(optarg);
            break;
        case 'Y':
            config->is_output_yuv = atoi(optarg);
            break;
        case 'F':
            config->is_output_full_range = atoi(optarg);
            break;
        case 'p':
            config->precision = atoi(optarg);
            break;
        case 's':
            config->swap_channels = 1;
            break;
        case 'a':
            config->b_print_all = 1;
            break;
        case 'h':
            print_usage(argv[0]);
            ret = -1;
            break;
        case 'm':
            // parse mode string like 'rgbl_to_601f'
            mode_str = (const char *)optarg;
            printf("parse from csc_mode_str: %s\n", mode_str);
            out_clr_pos = 8;
            config->is_input_yuv = 1;
            config->is_input_full_range = mode_str[3] == 'f' || mode_str[3] == 'F';
            if (0 == strncmp(mode_str, "rgb", 3)) {
                config->input_color_encoding = 1;
                config->is_input_yuv = 0;
            } else if (0 == strncmp(mode_str, "601", 3)) {
                config->input_color_encoding = 0;
            } else if (0 == strncmp(mode_str, "709", 3)) {
                config->input_color_encoding = 1;
            } else if (0 == strncmp(mode_str, "2020", 4)) {
                config->input_color_encoding = 2;
                config->is_input_full_range = mode_str[4] == 'f' || mode_str[4] == 'F';
                out_clr_pos = 9;
            } else {
                printf("unknow csc_mode_str: %s\n", mode_str);
                ret = -1;
            }

            config->is_output_yuv = 1;
            config->is_output_full_range = mode_str[out_clr_pos + 3] == 'f' || mode_str[out_clr_pos + 3] == 'F';
            if (0 == strncmp(mode_str + out_clr_pos, "rgb", 3)) {
                config->output_color_encoding = config->input_color_encoding;
                config->is_output_yuv = 0;
            } else if (0 == strncmp(mode_str + out_clr_pos, "601", 3)) {
                config->output_color_encoding = 0;
            } else if (0 == strncmp(mode_str + out_clr_pos, "709", 3)) {
                config->output_color_encoding = 1;
            } else if (0 == strncmp(mode_str + out_clr_pos, "2020", 4)) {
                config->output_color_encoding = 2;
                config->is_output_full_range = mode_str[out_clr_pos + 4] == 'f' || mode_str[out_clr_pos + 4] == 'F';
            } else {
                printf("unknow csc_mode_str: %s\n", mode_str);
                ret = -1;
            }
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
    struct post_csc_coef csc_simple_coef = {0};      // [O] return CSC coefs
    struct post_csc csc_cfg = {0};                   // [I] CSC config
    struct post_csc_convert_mode convert_mode = {0}; // [I] CSC convert mode
    const int precision = 10;                        // precision for CSC coef: range: {8,10,13}
    struct cmd_config_t config = {0, 1, 0, 1, 0, 1, precision, 0, 0};

    // get cmd config & dump
    ret = get_cmd_config(argc, argv, &config);
    if (ret < 0)
    {
        return ret;
    }
    printf("dump CSC mode info from cmd line:\n");
    printf("\t- input  colorspace: %d, is_yuv: %d, is_full_range: %d\n", config.input_color_encoding,
        config.is_input_yuv, config.is_input_full_range);
    printf("\t- output colorspace: %d, is_yuv: %d, is_full_range: %d\n", config.output_color_encoding,
        config.is_output_yuv, config.is_output_full_range);
    printf("\t- coef precision: %dbit, swap_channels: %d\n", config.precision, config.swap_channels);
    printf("\t- print all supported case: %d\n", config.b_print_all);

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
    csc_cfg.csc_enable = 1;

    // set CSC convert mode
    convert_mode.input_color_encoding = config.input_color_encoding;
    convert_mode.output_color_encoding = config.output_color_encoding;
    convert_mode.is_input_yuv = config.is_input_yuv;
    convert_mode.is_output_yuv = config.is_output_yuv;
    convert_mode.is_input_full_range = config.is_input_full_range;
    convert_mode.is_output_full_range = config.is_output_full_range;
    convert_mode.swap_channels = config.swap_channels;
    convert_mode.precision = config.precision;

    // get CSC coefs & dump
    printf("\n");
    int nb_mode = 1;
    const struct post_csc_convert_mode *mode_list = &convert_mode;
    if (config.b_print_all)
    {
        nb_mode = 37;
        mode_list = g_supported_standard_convert_mode;
    }

    for (int i = 0; i < nb_mode; i++)
    {
        const struct post_csc_convert_mode *mode = &mode_list[i];
        ret = rockchip_calc_post_csc(&csc_cfg, &csc_simple_coef, mode);
        if (0 == ret)
        {
            printf("\t- get CSC matrix: [%4d, %4d, %4d; %4d, %4d, %4d; %4d, %4d, %4d]\n", csc_simple_coef.csc_coef00,
                csc_simple_coef.csc_coef01, csc_simple_coef.csc_coef02, csc_simple_coef.csc_coef10, csc_simple_coef.csc_coef11,
                csc_simple_coef.csc_coef12, csc_simple_coef.csc_coef20, csc_simple_coef.csc_coef21, csc_simple_coef.csc_coef22);
            printf("\t- get CSC offset: [%d, %d, %d]\n", csc_simple_coef.csc_dc0, csc_simple_coef.csc_dc1, csc_simple_coef.csc_dc2);
        } else {
            printf("\t - get CSC matrix & offset failed!\n");
        }
    }

    return ret;
}