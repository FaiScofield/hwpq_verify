/**
 * @copyright Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @description: test_verify_com.c
 * @author: vance.wu@rock-chips.com
 * @create: 2025-10-21
 * @history:
 *  - 2025-10-21 vance.wu: first version, support image format convertion.
 */

#include "verify_com.h"
#include "verify_cmd_parser.h"
#include <errno.h>
#include <stdio.h>
#include <string.h>

#define STB_IMAGE_IMPLEMENTATION
#define STBI_NO_PSD
#define STBI_NO_TGA
#define STBI_NO_GIF
#define STBI_NO_HDR
#define STBI_NO_PIC
#define STBI_NO_PNM
#include "stb_image.h" // only jpeg//png/bmp support

int main(int argc, char *const argv[])
{
    int ret = 0;

    /* parse cmd parameters */
    struct common_verify_cmd_config config = {0};
    ret = common_verify_arg_get_cmd_config(argc, argv, &config);
    if (ret < 0) {
        return ret;
    }
    common_verify_arg_dump_config(&config);

    /* alloc i/o/t memories */
    
    const size_t frame_size_max = config.src_wid_vir * config.src_hgt_vir * 4 * sizeof(uint16_t);
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

    const int depth = (config.src_fmt < 10 && config.dst_fmt < 10) ? 8 : 10;
    const int mid_fmt = common_verify_imgfmt_get_def_planar(config.src_fmt, depth);
    const int mid_fmt_bpp = common_verify_imgfmt_bpp(mid_fmt);
    const int mid_fmt_size = (config.src_wid * config.src_hgt * mid_fmt_bpp + 7) / 8;
    LOGI("mid_fmt: %d(%s), bpp: %d, frame_size: %d\n", mid_fmt, common_verify_imgfmt_str(mid_fmt), mid_fmt_bpp, mid_fmt_size);

    for (int k = 0; k < config.nb_frame; k++) {
        // read src data
        ret = image_read_to_planar(fp_src, p_src, k, config.src_wid, config.src_hgt, config.src_wid_vir,
            config.src_hgt_vir, config.src_fmt, depth);
        if (ret) {
            LOGE("Failed to read frame #%d from input file '%s'! %s\n", k, config.input_file, strerror(errno));
            break;
        }

        // write planar src data
        if (1) {
            char filename[1024];
            snprintf(filename, 1023, "%s_%s.%s", config.output_file, common_verify_imgfmt_str(mid_fmt),
                common_verify_imgfmt_exten_str(mid_fmt));
            FILE *fp = fopen(filename, "wb");
            fwrite(p_src, 1, mid_fmt_size, fp);
            fclose(fp);
        }

        // write dst data
        ret = image_write_from_plannar(fp_dst, p_src, k, config.dst_wid, config.dst_hgt, config.dst_wid_vir,
            config.dst_hgt_vir, config.dst_fmt, depth);
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

    fclose(fp_src);
    fclose(fp_dst);
    free(p_src);
    free(p_dst);

    return ret;
}