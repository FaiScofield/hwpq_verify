/**
 * @copyright Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @description: verify_cmd_parser.h
 * @author: vance.wu@rock-chips.com
 * @create: 2025-09-05
 * @history:
 *  2025-09-08 vance.wu: Adjust cmd line options for second parsing support.
 */

#ifndef _VERIFY_CMD_PARSER_
#define _VERIFY_CMD_PARSER_

#include "verify_img_fmt.h"
#include <stdbool.h>
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

#ifdef __cplusplus
extern "C" {
#endif

/* common verify arguments */
struct common_verify_cmd_config
{
    char input_file[1024];  // input raw file
    char output_file[1024]; // output raw file
    char output_dir[1024];  // parsed from 'output_file'
    char config_file[1024]; // '.json' config file
    char crc_file[1024];    // '.txt' file to record CRC values. NOTE: opened by mode 'a'
    char platform_name[32]; // RK3576/RK3572/...

    int src_wid;            // defaut: 1920
    int src_hgt;            // default: 1080
    int src_wid_vir;        // default: src_wid
    int src_hgt_vir;        // default: src_hgt
    int src_fmt;            // {0-yuv444p, 1-nyuv444sp(nv24), 2-yuv444i, 3-rgb888, 4-rgba8888}
                            //   (+10 for 10bit lsb unpacked; +20 for 10bit packed)
    int src_clrspc;         // {0/1(RGBL/F), 2/3(601L/F), 4/5(709L/F), 8/9(2020L/F)}

    int dst_wid;            // default: 1920
    int dst_hgt;            // default: 1080
    int dst_wid_vir;        // default: dst_wid
    int dst_hgt_vir;        // default: dst_hgt
    int dst_fmt;            // same to src_fmt
    int dst_clrspc;         // same to src_clrspc

    int nb_frame;           // default: 1
    int mode;               // default: -1, further parsed for some modules needed
    int seed;               // random seed, default: -1
};

void common_verify_arg_print_usage(const char *program);
int common_verify_arg_get_cmd_config(int argc, char *const argv[], struct common_verify_cmd_config *config);
int common_verify_arg_dump_config(struct common_verify_cmd_config *config);

extern const struct option g_common_verify_arg_supported_options[];

#ifdef __cplusplus
}
#endif
#endif /* _VERIFY_CMD_PARSER_ */