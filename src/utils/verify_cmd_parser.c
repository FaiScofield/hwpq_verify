/**
 * @copyright Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @description: verify_cmd_parser.c
 * @author: vance.wu@rock-chips.com
 * @create: 2025-09-05
 * @history:
 */

#include "verify_cmd_parser.h"
#include "verify_com.h"
#include "verify_img_fmt.h"
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>


const struct option g_common_verify_arg_supported_options[] = {
    {    "help", ARG_NONE, 0, 'h'}, // print help message
    {   "input",  ARG_REQ, 0, 'i'}, // input filename
    {   "width",  ARG_OPT, 0, 'w'}, // input image width, set to '1920' if not specified
    {  "height",  ARG_OPT, 0, 'g'}, // input image height, set to '1080' if not specified
    {  "format",  ARG_OPT, 0, 'f'}, // input image format, set to '0' if not specified
    {  "clrspc",  ARG_OPT, 0, 's'}, // input image colorspace, set to '1-RGBF/5-709F' if not specified
    {  "output",  ARG_OPT, 0, 'o'}, // output filename, set to 'dirname(input)/custom_output_basename' if not specified
    {  "outwid",  ARG_OPT, 0, 'W'}, // output image width, same to 'width' if not specified
    {  "outhgt",  ARG_OPT, 0, 'G'}, // output image height, same to 'height' if not specified
    {  "outfmt",  ARG_OPT, 0, 'F'}, // output image format, same to 'format' if not specified
    {  "outclr",  ARG_OPT, 0, 'S'}, // output image colorspace, set to 'clrspc' if not specified
    { "nframes",  ARG_OPT, 0, 'n'}, // number of frames of to process, set to '1' if not specified
    {  "config",  ARG_OPT, 0, 'c'}, // config file ('.json' for config; '.bin/.dat' for register data), set to 'NULL' if not specified
    {     "crc",  ARG_OPT, 0, 'C'}, // crc file ('.txt/.dat'), set to 'NULL' if not specified
    {"platform",  ARG_OPT, 0, 'p'}, // RK3572, RK3576, RK3538..., set to 'RK3572' if not specified
    {    "mode",  ARG_OPT, 0, 'm'}, // test mode, customized by each model, set to '-1' if not specified
    {    "args",  ARG_OPT, 0, 'a'}, // other arguments, parsed by each model, set to 'NULL' if not specified
    {         0,        0, 0,   0}  // end of option list
};

void common_verify_arg_print_usage(const char *program)
{
    printf("\nUsage: %s [options]\n", program);
    printf("\nProgram Optional Options:\n");
    printf("  -i  --input       [intput_file] | input filename\n");
    printf("  -w  --width       [input_width] | input image width, default: 1920\n");
    printf("  -g  --height     [input_height] | input image height, default: 1080\n");
    printf("  -f  --format     [input_format] | input image format, default: 0, support: {rgb(0)[a(1)|planar(2)]; "
           "yuv[444p(3)|444sp(4)|444i(5)|422p(6)|422sp(7)|420p(8)|420sp(9)}"
           "(+10 for 10bit unpacked(LSB); +20 for 10bit packed)\n");
    printf("  -r  --clrspc [input_colorspace] | input image colorspace, default: 1-RGBF/5-709F, support: {0/1(RGBL/F), "
           "2/3(601L/F), 4/5(709L/F), 8/9(2020L/F)}\n");
    printf("  -o  --output      [output_file] | output filename, default: 'dirname(input)/custom_output_basename'\n");
    printf("  -W  --outwid     [output_width] | output image width, default: same to 'width'\n");
    printf("  -G  --outhgt    [output_height] | output image height, default: same to 'height'\n");
    printf("  -F  --outfmt    [output_format] | output image format, default: mod('format',10)+10\n");
    printf("  -R  --outclr [output_colorspace]| output image colorspace, default: same to 'clrspc'\n");
    printf("  -n  --nframes      [num_frames] | number of frames to process, default: 1\n");
    printf("  -c  --config      [config_file] | config filename, default: 'NULL'; '.json' for config; '.bin/.dat' for "
           "register data\n");
    printf("  -C  --crc            [crc_file] | crc output filename with write mode 'a', default: 'NULL'\n");
    printf("  -p  --platform  [platform_name] | platform like: RK3572(default)/RK3576/RK3538...\n");
    printf("  -m  --mode           [mode_num] | test mode, customized by each model, default: -1\n");
    printf("  -s  --seed        [random_seed] | random seed, customized using by each model, default: -1\n");
    printf("  -a  --args         [other_args] | other args customized by each model, default: 'NULL'\n");
    printf("  -h  --help                      | print this message\n");
    printf("\n");
}

int common_verify_arg_get_cmd_config(int argc, char *argv[], struct common_verify_cmd_config *pConfigRet, bool bSetDefault)
{
    if (!argv || !pConfigRet) {
        return -1;
    }

    /* set default values frist */
    struct common_verify_cmd_config config = {0};
    memset(&config.src_wid, 0xFF,
        sizeof(struct common_verify_cmd_config) - offsetof(struct common_verify_cmd_config, src_wid)); // set to -1

    /* parse cmd args */
    int opt;
    int idx;
    const char *short_option_str = "hi:w:g:f:r:o:W:G:F:R:n:c:C:p:m:s:a::";
    while ((opt = getopt_long(argc, argv, short_option_str, g_common_verify_arg_supported_options, &idx)) != -1) {
        switch (opt) {
        case 'h': common_verify_arg_print_usage(argv[0]); return -1;
        case 'i': strncpy(config.input_file, optarg, 1024); break;
        case 'o': strncpy(config.output_file, optarg, 1024); break;
        case 'c': strncpy(config.config_file, optarg, 1024); break;
        case 'C': strncpy(config.crc_file, optarg, 1024); break;
        case 'a': strncpy(config.other_args, optarg, 1024); break;
        case 'p': strncpy(config.platform, optarg, 32); break;
        case 'w': config.src_wid = atoi(optarg); break;
        case 'g': config.src_hgt = atoi(optarg); break;
        case 'f': config.src_fmt = atoi(optarg); break;
        case 'r': config.src_clrspc = atoi(optarg); break;
        case 'W': config.dst_wid = atoi(optarg); break;
        case 'G': config.dst_hgt = atoi(optarg); break;
        case 'F': config.dst_fmt = atoi(optarg); break;
        case 'R': config.dst_clrspc = atoi(optarg); break;
        case 'n': config.nb_frame = atoi(optarg); break;
        case 'm': config.mode = atoi(optarg); break;
        case 's': config.seed = atoi(optarg); break;
        default:  break;
        }
    }

    /* check args, set default values if necessary */
    if (config.input_file[0] == '\0') {
        printf(" - input_file not set!\n");
        // return -1;
    }
    if (config.platform[0] == '\0') {
        strncpy(config.platform, "RK3572", 32);
    }
    if (config.src_wid < 0) {
        config.src_wid = 1920;
    }
    if (config.src_hgt < 0) {
        config.src_hgt = 1080;
    }
    if (config.src_fmt < 0) {
        config.src_fmt = 0;
    }
    if (config.src_clrspc < 0) {
        config.src_clrspc = config.src_fmt % 10 < 3 ? RGBFULL : YUV709F; // default to RGBF/709F
    }
    if (config.dst_wid < 0) {
        config.dst_wid = config.src_wid;
    }
    if (config.dst_hgt < 0) {
        config.dst_hgt = config.src_hgt;
    }
    if (config.dst_fmt < 0) {
        config.dst_fmt = config.src_fmt % 10 + 10; // default to [10, 19], 10bit unpacked data
    }
    if (config.dst_clrspc < 0) {
        config.dst_clrspc = config.dst_fmt % 10 < 3 ? RGBFULL : YUV709F; // default to RGBF/709F
    }
    if (config.nb_frame < 0) {
        config.nb_frame = 1;
    }
    if (config.output_file[0] == '\0') {
        strcpy(config.output_dir, get_dirname(config.input_file));
        snprintf(config.output_file, 1024, "%s/verify_out_%dx%d_%s.%s", config.output_dir, config.dst_wid,
            config.dst_hgt, common_verify_imgfmt_str(config.dst_fmt), common_verify_imgfmt_exten_str(config.dst_fmt));
        printf(" - output_file no set, force update to '%s'!\n", config.output_file);
    }
    else {
        strcpy(config.output_dir, get_dirname(config.output_file));
        mkdir(config.output_dir, 0777); // mkdir before checking
        int flag = is_directory(config.output_file);
        if (flag == 1) {
            strcpy(config.output_dir, config.output_file);
            snprintf(config.output_file, 1024, "%s/verify_out_%dx%d_%s.%s", config.output_dir, config.dst_wid,
                config.dst_hgt, common_verify_imgfmt_str(config.dst_fmt), common_verify_imgfmt_exten_str(config.dst_fmt));
            printf(" - output_file is a directory, force update to: '%s'!\n", config.output_file);
        }
    }

    memcpy(pConfigRet, &config, sizeof(struct common_verify_cmd_config));
    return 0;
}

int common_verify_arg_dump_config(struct common_verify_cmd_config *config)
{
    if (!config) {
        return -1;
    }
    printf("----------------------------------------\n");
    printf("dump common verify cmd config below: \n");
    printf(" - input_file: %s\n", config->input_file);
    printf(" - output_file: %s\n", config->output_file);
    printf(" - output_dir: %s\n", config->output_dir);
    printf(" - config_file: %s\n", config->config_file);
    printf(" - crc_file: %s\n", config->crc_file);
    printf(" - platform: %s\n", config->platform);
    printf(" - src_wid: %d\n", config->src_wid);
    printf(" - src_hgt: %d\n", config->src_hgt);
    printf(" - src_fmt: %d (%s)\n", config->src_fmt, common_verify_imgfmt_str(config->src_fmt));
    printf(" - src_clrspc: %d (%s)\n", config->src_clrspc, common_verify_clrspc_str(config->src_clrspc));
    printf(" - dst_wid: %d\n", config->dst_wid);
    printf(" - dst_hgt: %d\n", config->dst_hgt);
    printf(" - dst_fmt: %d (%s)\n", config->dst_fmt, common_verify_imgfmt_str(config->dst_fmt));
    printf(" - dst_clrspc: %d (%s)\n", config->dst_clrspc, common_verify_clrspc_str(config->dst_clrspc));
    printf(" - nb_frame: %d\n", config->nb_frame);
    printf(" - custom mode: %d\n", config->mode);
    printf(" - random seed: %d\n", config->seed);
    printf(" - other_args: %s\n", config->other_args);
    printf("----------------------------------------\n");
    return 0;
}