/**
 * @copyright Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @description: acm_verify_demo.c
 * @author: vance.wu@rock-chips.com
 * @create: 2025-09-15
 * @history:
 */

#include "verify_img_io.h"
#include "verify_cmd_parser.h"
#include "verify_crc32.h"
#include "cJSON.h"
#include "acm_verify_api.h"
#include <errno.h>
#include <stdio.h>
#include <string.h>


int main(int argc, char *const argv[])
{
    int ret = 0;

    /* parse cmd parameters */
    // opterr = 0; // disable getopt error message
    struct common_verify_cmd_config config = {0};
    ret = common_verify_arg_get_cmd_config(argc, argv, &config);
    if (ret < 0) {
        return ret;
    }
    common_verify_arg_dump_config(&config);

    const bool bIsInputYuv = common_verify_imgfmt_is_yuv(config.src_fmt);
    const bool bIsOutputYuv = common_verify_imgfmt_is_yuv(config.dst_fmt);

    // check nessary parameters
    if (config.config_file[0] == '\0') {
        LOGE(" - config_file is not specified!\n");
        return -1;
    }
    if (config.src_clrspc <= RGBFULL || config.dst_clrspc <= RGBFULL || common_verify_imgfmt_is_rgb(config.src_fmt) ||
        common_verify_imgfmt_is_rgb(config.dst_fmt))
    {
        LOGE(" - src_fmt(%d) & dst_fmt(%d) should be YUV family! (also to the colorspaces)\n", config.src_fmt, config.dst_fmt);
        return -1;
    }
    if (config.crc_file[0] == '\0') {
        snprintf(config.crc_file, 1024, "%s/acm_crc_out.dat", config.output_dir);
        LOGI(" - crc_file update to: '%s'!\n", config.crc_file);
    }

    /* create handler */
    acm_handle_t handle = {0};
    acm_proc_param_t proc_param = {0};
    acm_init_param_t init_param = {0};
    init_param.platform = 0;
    if (strcmp(config.platform_name, "RK3572")) {
        init_param.platform = 1;
    }
    sprintf(init_param.debug_path, "%s", config.output_dir);
    sprintf(proc_param.config_path, "%s", config.config_file);
    ret = acmVerifyInit(&handle, &init_param);
    if (ret) {
        LOGE("failed to init handler! %d\n", ret);
        return ret;
    }

    /* alloc i/o/t memories */
    const size_t frame_size_max = config.src_wid * config.src_hgt * 4 * 2; // 4 channels x 16bpp
    void *p_src = calloc(frame_size_max, 1);
    void *p_dst = calloc(frame_size_max, 1);
    if (!p_src || !p_dst) {
        return -1;
    }

    FILE *fp_src = fopen(config.input_file, "rb");
    FILE *fp_dst = fopen(config.output_file, "wb");
    if (!fp_src) {
        LOGE("Failed to open the input file '%s'! %s\n", config.input_file, strerror(errno));
        return -1;
    }
    if (!fp_dst) {
        LOGE("Failed to open the output file '%s'! %s\n", config.output_file, strerror(errno));
        return -1;
    }
    FILE *fp_crc = fopen(config.crc_file, "a");
    if (!fp_crc) {
        LOGW("Failed to open the crc output file '%s'! %s. CRC value will not be written!\n", config.crc_file, strerror(errno));
    }

    /* start to process */
    int crc_val = -1;
    for (int k = 0; k < config.nb_frame; k++) {
        ret = image_read_to_10bit_planar(fp_src, (ushort *)p_src, k, config.src_wid, config.src_hgt, config.src_wid_vir,
            config.src_hgt_vir, config.src_fmt, config.dither_up);
        if (ret) {
            LOGE("Failed to read frame #%d from input file '%s'! %s\n", k, config.input_file, strerror(errno));
            break;
        }

        crc_val = calc_crc32_rtl_10bit_planar(p_src, config.src_wid, config.src_hgt, config.src_wid_vir, bIsInputYuv);
        LOGI("src CRC (%s MSB order) of frame #%04d: 0x%08X\n", bIsInputYuv ? "VYU" : "RGB", k, crc_val);

        void *p_src_y = p_src;
        void *p_src_u = (void *)((unsigned short *)p_src + config.src_wid * config.src_hgt);
        void *p_src_v = (void *)((unsigned short *)p_src + config.src_wid * config.src_hgt * 2);
        void *p_dst_y = p_dst;
        void *p_dst_u = (void *)((unsigned short *)p_dst + config.src_wid * config.src_hgt);
        void *p_dst_v = (void *)((unsigned short *)p_dst + config.src_wid * config.src_hgt * 2);

        proc_param.src_info.img_bits = 10;
        proc_param.src_info.plane_num = 3;
        proc_param.src_info.img_w[0] = config.src_wid;
        proc_param.src_info.img_h[0] = config.src_hgt;
        proc_param.src_info.img_ws[0] = config.src_wid;
        proc_param.src_info.img_hs[0] = config.src_hgt;
        proc_param.src_info.plane_info[0].ptr = p_src_y;
        proc_param.src_info.plane_info[0].offset = 0;
        proc_param.src_info.plane_info[0].pix_strd = 1;
        proc_param.src_info.img_w[1] = config.src_wid;
        proc_param.src_info.img_h[1] = config.src_hgt;
        proc_param.src_info.plane_info[1].ptr = p_src_u;
        proc_param.src_info.plane_info[1].offset = 0;
        proc_param.src_info.plane_info[1].pix_strd = 1;
        proc_param.src_info.img_ws[1] = config.src_wid;
        proc_param.src_info.img_hs[1] = config.src_hgt;
        proc_param.src_info.img_w[2] = config.src_wid;
        proc_param.src_info.img_h[2] = config.src_hgt;
        proc_param.src_info.img_ws[2] = config.src_wid;
        proc_param.src_info.img_hs[2] = config.src_hgt;
        proc_param.src_info.plane_info[2].ptr = p_src_v;
        proc_param.src_info.plane_info[2].offset = 0;
        proc_param.src_info.plane_info[2].pix_strd = 1;

        proc_param.dst_info.img_bits = 10;
        proc_param.dst_info.plane_num = 3;
        proc_param.dst_info.img_w[0] = config.src_wid;
        proc_param.dst_info.img_h[0] = config.src_hgt;
        proc_param.dst_info.img_ws[0] = config.src_wid;
        proc_param.dst_info.img_hs[0] = config.src_hgt;
        proc_param.dst_info.plane_info[0].ptr = p_dst_y;
        proc_param.dst_info.plane_info[0].offset = 0;
        proc_param.dst_info.plane_info[0].pix_strd = 1;
        proc_param.dst_info.img_w[1] = config.src_wid;
        proc_param.dst_info.img_h[1] = config.src_hgt;
        proc_param.dst_info.plane_info[1].ptr = p_dst_u;
        proc_param.dst_info.plane_info[1].offset = 0;
        proc_param.dst_info.plane_info[1].pix_strd = 1;
        proc_param.dst_info.img_ws[1] = config.src_wid;
        proc_param.dst_info.img_hs[1] = config.src_hgt;
        proc_param.dst_info.img_w[2] = config.src_wid;
        proc_param.dst_info.img_h[2] = config.src_hgt;
        proc_param.dst_info.img_ws[2] = config.src_wid;
        proc_param.dst_info.img_hs[2] = config.src_hgt;
        proc_param.dst_info.plane_info[2].ptr = p_dst_v;
        proc_param.dst_info.plane_info[2].offset = 0;
        proc_param.dst_info.plane_info[2].pix_strd = 1;

        proc_param.frame_idx = k;
        proc_param.frame_num = config.nb_frame;

        ret = acmVerifyProc(handle, &proc_param);
        fwrite(p_dst, 2, config.src_wid * config.src_hgt * 3, fp_dst);
        fwrite(p_src, 2, config.src_wid * config.src_hgt * 3, fp_dst); // write src after dst

        // get CRC
        crc_val = calc_crc32_rtl_10bit_planar(p_dst, config.dst_wid, config.dst_hgt, config.dst_wid_vir, bIsOutputYuv);
        LOGI("dst CRC (%s MSB order) of frame #%04d: 0x%08X\n", bIsOutputYuv ? "VYU" : "RGB", k, crc_val);
        if (fp_crc) {
            fprintf(fp_crc, "input: %s, cmd_config: %s, crc (%s MSB order) of frame #%04d: 0x%08X\n",
                get_basename(config.input_file), get_basename(config.config_file), bIsOutputYuv ? "VYU" : "RGB", k, crc_val);
        }
    }
    LOGI("done. write output to file: '%s'\n", config.output_file);

    ret = acmVerifyDeinit(handle);

    fclose(fp_src);
    fclose(fp_dst);
    if (fp_crc)
        fclose(fp_crc);
    free(p_src);
    free(p_dst);

    return ret;
}