/**
 * @copyright: Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @bref:      test_verify_com.c
 * @author:    vance.wu@rock-chips.com
 * @create:    2025-10-21
 * @modifier:  vance.wu@rock-chips.com
 * @modify:    2026-03-10
 */

#include "verify_img_io.h"
#include "verify_cmd_parser.h"
#include <errno.h>
#include <stdio.h>
#include <string.h>

int main(int argc, char *const argv[])
{
    int ret = 0;

    /* parse cmd parameters */
    struct common_verify_cmd_config config = {0};
    ret = common_verify_arg_get_cmd_config(argc, argv, &config);
    if (ret < 0)
        return ret;
    common_verify_arg_dump_config(&config);

    void *p_src = NULL, *p_dst = NULL, *p_src_raw = NULL;
    FILE *fp_src = NULL, *fp_dst = NULL;
    int src_depth = common_verify_imgfmt_depth(config.src_fmt);
    const int dst_depth = common_verify_imgfmt_depth(config.dst_fmt);
    const int mid_depth = MAX(src_depth, dst_depth);
    int mid_fmt = RGB_PLANAR;
    int mid_fmt_bpp = 24;
    int mid_fmt_size = 0;
    size_t frame_size_max = 0;

    /* alloc i/o/t memories */
    const bool is_src_stb_img = is_stb_image(config.input_file);
    if (is_src_stb_img) {
        int nb_channels = 0;
        p_src_raw = read_stb_image_auto(config.input_file, &config.src_wid, &config.src_hgt, &nb_channels, 3);
        if (p_src_raw) {
            // update resolution
            config.nb_frame = 1;
            config.src_fmt = RGB888;
            config.src_wid_vir = config.src_wid * 3;
            config.src_hgt_vir = config.src_hgt;
            src_depth = 8;
            LOGW("stb image read success, src size: %dx%d, fmt: RGB888\n", config.src_wid, config.src_hgt);
            if (config.dst_hgt != config.src_hgt || config.dst_wid != config.src_wid) {
                config.dst_hgt = config.src_hgt;
                config.dst_wid = config.src_wid;
                config.dst_wid_vir = MAX(config.dst_wid_vir,
                    ROUND_S32(config.dst_wid * common_verify_imgfmt_pitch_ratio(config.dst_fmt)));
                config.dst_hgt_vir = MAX(config.dst_hgt_vir, config.dst_hgt);
                LOGW("dst size updated to: %dx%d, the resolution in dst filename '%s' might not match!\n",
                    config.dst_wid, config.dst_hgt, config.output_file);
            }
        }
        else
            goto EXIT;
    }
    else {
        fp_src = fopen(config.input_file, "rb");
        if (!fp_src) {
            LOGE("Failed to open the input file '%s'! %s\n", config.input_file, strerror(errno));
            goto EXIT;
        }
    }

    mid_fmt = common_verify_imgfmt_get_def_planar(config.src_fmt, mid_depth);
    mid_fmt_bpp = common_verify_imgfmt_bpp(mid_fmt);
    mid_fmt_size = (config.src_wid * config.src_hgt * mid_fmt_bpp + 7) / 8;
    frame_size_max = config.src_wid_vir * config.src_hgt_vir * 4 * sizeof(uint16_t);
    LOGI("mid_fmt: %#x(%s), bpp: %d, frame_size: %d\n", mid_fmt, common_verify_imgfmt_name(mid_fmt), mid_fmt_bpp, mid_fmt_size);

    p_src = calloc(frame_size_max, 1);
    // p_dst = calloc(frame_size_max, 1);
    if (!p_src) {
        goto EXIT;
    }
    fp_dst = fopen(config.output_file, "wb");
    if (!fp_dst) {
        LOGE("Failed to open the output file '%s'! %s\n", config.output_file, strerror(errno));
        goto EXIT;
    }

    /* run format convert */
    for (int k = 0; k < config.nb_frame; k++) {
        // read src data
        if (is_src_stb_img) {
            if (mid_depth == 8) { // to RGB_planar
                ret = imgcvt_to_planar_8bit_lsb((uint8_t *)p_src_raw, (uint8_t *)p_src, config.src_wid, config.src_hgt,
                    config.src_wid_vir, config.src_hgt_vir, config.src_wid, config.src_hgt, config.src_fmt, false, 0);
            }
            else if (mid_depth == 10) { // to RGB10l_planar
                ret = imgcvt_to_planar_10bit_lsb((uint8_t *)p_src_raw, (uint16_t *)p_src, config.src_wid, config.src_hgt,
                    config.src_wid_vir, config.src_hgt_vir, config.src_wid * 2, config.src_hgt, config.src_fmt, false, 0);
            }
            else {
                LOGE("unsupported mid depth: %d\n", mid_depth);
                break;
            }
        }
        else {
            ret = image_read_to_planar(fp_src, p_src, k, config.src_wid, config.src_hgt, config.src_wid_vir,
                config.src_hgt_vir, config.src_fmt, mid_depth, config.dither_up);
        }
        if (ret) {
            LOGE("Failed to read frame #%d from input file '%s'! %s\n", k, config.input_file, strerror(errno));
            break;
        }

        // int crc_src = common_verify_crc32(p_src, mid_fmt_size);

        // write planar src data
        if (1) {
            char filename[1024];
            snprintf(filename, 1023, "%s_midFmt_%s.%s", config.output_file, common_verify_imgfmt_name(mid_fmt),
                common_verify_imgfmt_exten_str(mid_fmt));
            FILE *fp = fopen(filename, "wb");
            fwrite(p_src, 1, mid_fmt_size, fp);
            fclose(fp);
        }

        // write dst data
        ret = image_write_from_plannar(fp_dst, p_src, k, config.dst_wid, config.dst_hgt, config.dst_wid_vir,
            config.dst_hgt_vir, config.dst_fmt, mid_depth, config.dither_dn);
        if (ret) {
            LOGE("Failed to write frame #%d to output file '%s'! %s\n", k, config.output_file, strerror(errno));
            break;
        }
    }

    if (0 == ret) {
        LOGI("done. write output to file: '%s'\n", config.output_file);
    }
    else {
        LOGE("error happened, please have a check!\n");
    }

EXIT:
    if (p_src_raw)
        free_stb_image_auto(p_src_raw);
    if (fp_src)
        fclose(fp_src);
    if (fp_dst)
        fclose(fp_dst);
    if (p_src)
        free(p_src);
    // if (p_dst)
    //     free(p_dst);

    LOGI("done. ret=%d\n", ret);
    return ret;
}