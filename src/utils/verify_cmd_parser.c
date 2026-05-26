/**
 * @copyright: Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @brief:     verify_cmd_parser.c
 * @author:    vance.wu@rock-chips.com
 * @create:    2025-09-05
 * @modifier:  vance.wu@rock-chips.com
 * @modify:    2026-05-25
 */

#include "verify_cmd_parser.h"
#include "verify_com.h"
#include "verify_img_fmt.h"
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>


const struct option g_common_verify_arg_supported_options[] = {
    {"swvir",    ARG_REQ,  NULL, 0  }, // src width  stride
    {"shvir",    ARG_REQ,  NULL, 0  }, // src height stride
    {"dwvir",    ARG_REQ,  NULL, 0  }, // dst width  stride
    {"dhvir",    ARG_REQ,  NULL, 0  }, // dst height stride
    {"dup",      ARG_REQ,  NULL, 0  }, // dither up
    {"ddn",      ARG_REQ,  NULL, 0  }, // dither down
    {"dump",     ARG_REQ,  NULL, 0  }, // debug dump bitmask
    {"help",     ARG_NONE, NULL, 'h'}, // print help message
    {"input",    ARG_REQ,  NULL, 'i'}, // input filename
    {"width",    ARG_REQ,  NULL, 'w'}, // input image width, set to '1920' if not specified
    {"height",   ARG_REQ,  NULL, 'g'}, // input image height, set to '1080' if not specified
    {"format",   ARG_REQ,  NULL, 'f'}, // input image format, set to '0' if not specified
    {"clrspc",   ARG_REQ,  NULL, 's'}, // input image colorspace, set to '1-RGBF/5-709F' if not specified
    {"output",   ARG_REQ,  NULL, 'o'}, // output filename, set to 'dirname(input)/custom_output_basename' if not specified
    {"outwid",   ARG_REQ,  NULL, 'W'}, // output image width, same to 'width' if not specified
    {"outhgt",   ARG_REQ,  NULL, 'G'}, // output image height, same to 'height' if not specified
    {"outfmt",   ARG_REQ,  NULL, 'F'}, // output image format, same to 'format' if not specified
    {"outclr",   ARG_REQ,  NULL, 'S'}, // output image colorspace, set to 'clrspc' if not specified
    {"nframes",  ARG_REQ,  NULL, 'n'}, // number of frames of to process, set to '1' if not specified
    {"config",   ARG_REQ,  NULL, 'c'}, // config file ('.json' for config; '.bin/.dat' for register data), set to 'NULL' if not specified
    {"crc",      ARG_REQ,  NULL, 'C'}, // crc file ('.txt/.dat'), set to 'NULL' if not specified
    {"platform", ARG_REQ,  NULL, 'p'}, // RK3572, RK3576, RK3538..., set to 'RK3572' if not specified
    {"mode",     ARG_REQ,  NULL, 'm'}, // test mode, customized by each model, set to '-1' if not specified
    {0,          0,        0,    0  }  // end of option list
};

void common_verify_arg_print_usage(const char *program)
{
    printf("\nUsage: %s [options]\n", program);
    printf("\nProgram Common Options:\n");
    printf("  -h  --help                      | print this message\n");
    printf("  -i  --input       [intput_file] | input filename\n");
    printf("  -w  --width       [input_width] | input image width, default: 1920\n");
    printf("  -g  --height     [input_height] | input image height, default: 1080\n");
    printf("  -f  --format     [input_format] | input image format, default: 0x0, support: {rgb(0)[a(1)|planar(2)]; "
           "yuv[444p(3)|444sp(4)|444i(5)|422p(6)|422sp(7)|420p(8)|420sp(9)|400(a)}"
           "(+0x10 for 10bit unpacked(LSB); +0x20 for 10bit packed, +0x30 for tile4x4)\n");
    printf("  -r  --clrspc [input_colorspace] | input image colorspace, default: 1-RGBF/5-709F, support: {0/1(RGBL/F), "
           "2/3(601L/F), 4/5(709L/F), 8/9(2020L/F)}\n");
    printf("  -o  --output      [output_file] | output filename, default: 'dirname(input)/custom_output_basename'\n");
    printf("  -W  --outwid     [output_width] | output image width, default: same to 'width'\n");
    printf("  -G  --outhgt    [output_height] | output image height, default: same to 'height'\n");
    printf("  -F  --outfmt    [output_format] | output image format, default: mod('format',16)+0x10\n");
    printf("  -R  --outclr [output_colorspace]| output image colorspace, default: same to 'clrspc'\n");
    printf("  -n  --nframes      [num_frames] | number of frames to process, default: 1\n");
    printf("  -c  --config      [config_file] | config filename, default: 'NULL'; '.json' for config; '.bin/.dat' for "
           "register data\n");
    printf("  -C  --crc            [crc_file] | crc output filename with write mode 'a', default: 'NULL'\n");
    printf("  -p  --platform  [platform_name] | platform like: RK3572(default)/RK3576/RK3538...\n");
    printf("  -m  --mode           [mode_num] | test mode, customized by each model, default: -1\n");
    printf("  -s  --seed        [random_seed] | random seed, customized using by each model, default: -1\n");
    printf("      --swvir    [src_wid_stride] | src width  stride\n");
    printf("      --shvir    [src_hgt_stride] | src height stride\n");
    printf("      --dwvir    [dst_wid_stride] | dst width  stride\n");
    printf("      --dhvir    [dst_hgt_stride] | dst height stride\n");
    printf("      --dup           [dither_up] | dither up method, default: 0, support: {1-scale, 2-fillMsb, "
           "else-shift}\n");
    printf("      --ddn         [dither_down] | dither down method, default: 0, support: {1-scale, 2-fillMsb, "
           "else-shift}\n");
    printf("      --dump          [dump_mask] | debug dump flag mask, default: 0x0, support: 0x{1-cfg, 2-reg, 4-blob, "
           "8-crc, 10-io, 20-med, 40-lut}\n");
    printf("\n");
}

int common_verify_arg_get_cmd_config(int argc, char *const argv[], struct common_verify_cmd_config *pConfigRet)
{
    if (!argv || !pConfigRet) {
        return -1;
    }

    /* set default values frist */
    struct common_verify_cmd_config config = {0};
    memset(&config.src_wid, 0xFF,
        sizeof(struct common_verify_cmd_config) - offsetof(struct common_verify_cmd_config, src_wid)); // set to -1

    /* parse cmd args */
    int opt = -1;
    int idx = -1;
    const char *short_option_str = "-hi:w:g:f:r:o:W:G:F:R:n:c:C:p:m:s:"; // -1 for keep unknow option index unchanged
    while ((opt = getopt_long_only(argc, argv, short_option_str, g_common_verify_arg_supported_options, &idx)) != -1) {
        switch (opt) {
        case 0: {
            switch (idx) {
            case 0:  config.src_wid_vir = strtol(optarg, NULL, 0); break;
            case 1:  config.src_hgt_vir = strtol(optarg, NULL, 0); break;
            case 2:  config.dst_wid_vir = strtol(optarg, NULL, 0); break;
            case 3:  config.dst_hgt_vir = strtol(optarg, NULL, 0); break;
            case 4:  config.dither_up = strtol(optarg, NULL, 0); break;
            case 5:  config.dither_dn = strtol(optarg, NULL, 0); break;
            case 6:  config.dump_flag = strtol(optarg, NULL, 0); break;
            default: break;
            }
            printf(" - set %dth option: %s = %s\n", idx, g_common_verify_arg_supported_options[idx].name, optarg);
        } break;
        case 'h': common_verify_arg_print_usage(argv[0]); return -1;
        case 'i': strncpy(config.input_file, optarg, 1024); break;
        case 'o': strncpy(config.output_file, optarg, 1024); break;
        case 'c': strncpy(config.config_file, optarg, 1024); break;
        case 'C': strncpy(config.crc_file, optarg, 1024); break;
        case 'p': strncpy(config.platform_name, optarg, 32); break;
        case 'w': config.src_wid = strtol(optarg, NULL, 0); break;
        case 'g': config.src_hgt = strtol(optarg, NULL, 0); break;
        case 'f': config.src_fmt = strtol(optarg, NULL, 0); break;
        case 'r': config.src_clrspc = strtol(optarg, NULL, 0); break;
        case 'W': config.dst_wid = strtol(optarg, NULL, 0); break;
        case 'G': config.dst_hgt = strtol(optarg, NULL, 0); break;
        case 'F': config.dst_fmt = strtol(optarg, NULL, 0); break;
        case 'R': config.dst_clrspc = strtol(optarg, NULL, 0); break;
        case 'n': config.nb_frame = strtol(optarg, NULL, 0); break;
        case 'm': config.mode = strtol(optarg, NULL, 0); break;
        case 's': config.seed = strtol(optarg, NULL, 0); break;
        default:  break;
        }
    }

    /* check args, set default values if necessary */
    if (config.input_file[0] == '\0')
        printf(" - input_file not set!\n");
    if (config.platform_name[0] == '\0')
        strncpy(config.platform_name, "RK3572", 32);

    if (config.src_wid < 0)
        config.src_wid = 1920;
    if (config.src_hgt < 0)
        config.src_hgt = 1080;
    if (config.src_fmt < 0)
        config.src_fmt = 0;
    if (config.src_clrspc < 0)
        config.src_clrspc = common_verify_imgfmt_is_rgb(config.src_fmt) ? RGBFULL : YUV709F; // default to RGBF/709F
    if (config.src_wid_vir < 0)
        config.src_wid_vir = ROUND_S32(config.src_wid * common_verify_imgfmt_pitch_ratio(config.src_fmt));
    if (config.src_hgt_vir < 0)
        config.src_hgt_vir = config.src_hgt;

    if (config.dst_wid < 0)
        config.dst_wid = config.src_wid;
    if (config.dst_hgt < 0)
        config.dst_hgt = config.src_hgt;
    if (config.dst_fmt < 0)
        config.dst_fmt = (config.src_fmt & 0xF) + 0x10; // default to [0x10, 0x1a], 10bit unpacked data
    if (config.dst_clrspc < 0)
        config.dst_clrspc = common_verify_imgfmt_is_rgb(config.dst_fmt) ? RGBFULL : YUV709F; // default to RGBF/709F
    if (config.dst_wid_vir < 0)
        config.dst_wid_vir = ROUND_S32(config.dst_wid * common_verify_imgfmt_pitch_ratio(config.dst_fmt));
    if (config.dst_hgt_vir < 0)
        config.dst_hgt_vir = config.dst_hgt;

    if (config.nb_frame < 0)
        config.nb_frame = 1;
    if (config.dump_flag < 0)
        config.dump_flag = VERIFY_DBG_DUMP_NONE;
    if (config.output_file[0] == '\0') {
        strncpy(config.output_dir, get_dirname(config.input_file), 1024);
        snprintf(config.output_file, 1024, "%s/verify_out_%dx%d_%s.%s", config.output_dir, config.dst_wid,
            config.dst_hgt, common_verify_imgfmt_name(config.dst_fmt), common_verify_imgfmt_exten_str(config.dst_fmt));
        printf(" - output_file no set, force update to '%s'!\n", config.output_file);
    }
    else {
        strncpy(config.output_dir, get_dirname(config.output_file), 1024);
        mkdir(config.output_dir, 0777); // mkdir before checking
        int flag = is_directory(config.output_file);
        if (flag == 1) {
            strncpy(config.output_dir, config.output_file, 1024);
            snprintf(config.output_file, 1024, "%s/verify_out_%dx%d_%s.%s", config.output_dir, config.dst_wid,
                config.dst_hgt, common_verify_imgfmt_name(config.dst_fmt), common_verify_imgfmt_exten_str(config.dst_fmt));
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
    LOGI("----------------------------------------\n");
    LOGI("dump common verify cmd config below: \n");
    LOGI(" - input_file: %s\n", config->input_file);
    LOGI(" - output_file: %s\n", config->output_file);
    LOGI(" - output_dir: %s\n", config->output_dir);
    LOGI(" - config_file: %s\n", config->config_file);
    LOGI(" - crc_file: %s\n", config->crc_file);
    LOGI(" - platform name: %s\n", config->platform_name);
    LOGI(" - src_wid: %d (%d)\n", config->src_wid, config->src_wid_vir);
    LOGI(" - src_hgt: %d (%d)\n", config->src_hgt, config->src_hgt_vir);
    LOGI(" - src_fmt: %d (%s)\n", config->src_fmt, common_verify_imgfmt_name(config->src_fmt));
    LOGI(" - src_clrspc: %d (%s)\n", config->src_clrspc, common_verify_clrspc_str(config->src_clrspc));
    LOGI(" - dst_wid: %d (%d)\n", config->dst_wid, config->dst_wid_vir);
    LOGI(" - dst_hgt: %d (%d)\n", config->dst_hgt, config->dst_hgt_vir);
    LOGI(" - dst_fmt: %d (%s)\n", config->dst_fmt, common_verify_imgfmt_name(config->dst_fmt));
    LOGI(" - dst_clrspc: %d (%s)\n", config->dst_clrspc, common_verify_clrspc_str(config->dst_clrspc));
    LOGI(" - nb_frame: %d\n", config->nb_frame);
    LOGI(" - custom mode: %d\n", config->mode);
    LOGI(" - random seed: %d\n", config->seed);
    LOGI(" - dither up/down: %d / %d\n", config->dither_up, config->dither_dn);
    LOGI(" - dump_flag: 0x%X\n", config->dump_flag);
    LOGI("----------------------------------------\n");
    return 0;
}