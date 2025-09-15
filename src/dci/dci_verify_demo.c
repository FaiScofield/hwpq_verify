/**
 * @copyright Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @description: dci_verify_demo.c
 * @author: vance.wu@rock-chips.com
 * @create: 2025-09-15
 * @history:
 */

#include "verify_com.h"
#include "verify_cmd_parser.h"
#include "verify_crc32.h"
#include "cJSON.h"
#include <errno.h>
#include <stdio.h>
#include <string.h>


int main(int argc, char *const argv[])
{
    int ret = 0;
// dump_regs_to_dat();
    /* parse cmd parameters */
    opterr = 0; // disable getopt error message
    struct common_verify_cmd_config cmd_config = {0};
    ret = common_verify_arg_get_cmd_config(argc, argv, &cmd_config);
    if (ret < 0) {
        return ret;
    }
    common_verify_arg_dump_config(&cmd_config);

    // check nessary parameters
    if (cmd_config.crc_file[0] == '\0') {
        snprintf(cmd_config.crc_file, 1024, "%s/dci_crc_out.dat", cmd_config.output_dir);
        LOGI(" - crc_file update to: '%s'!\n", cmd_config.crc_file);
    }

    const int bIsInputYuv = cmd_config.src_fmt % 10 >= 3;
    const int bIsOutputYuv = cmd_config.dst_fmt % 10 >= 3;

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
#if 0
    int crc_val = -1;
    for (int k = 0; k < cmd_config.nb_frame; k++) {
        ret = image_read_to_10bit_planar(fp_src, (ushort *)p_src, k, cmd_config.src_wid, cmd_config.src_hgt, cmd_config.src_fmt);
        if (ret) {
            LOGE("Failed to read frame #%d from input file '%s'! %s\n", k, cmd_config.input_file, strerror(errno));
            break;
        }

        crc_val = get_crc_for_planar_frame_10bit(p_src, cmd_config.src_wid, cmd_config.src_hgt, bIsInputYuv);
        LOGI("src CRC (%s MSB order) of frame #%04d: 0x%08X\n", bIsInputYuv ? "VYU" : "RGB", k, crc_val);

        run_dci_with_coef(p_src, p_dst, cmd_config.src_wid, cmd_config.src_hgt, &dci_coefs, &dci_mode);
        dump_dci_regs(NULL, 0x0, &dci_coefs, bIsPostDCI);
        fwrite(p_dst, 2, cmd_config.src_wid * cmd_config.src_hgt * 3, fp_dst);
        fwrite(p_src, 2, cmd_config.src_wid * cmd_config.src_hgt * 3, fp_dst); // write src after dst

        // get CRC
        crc_val = get_crc_for_planar_frame_10bit(p_dst, cmd_config.src_wid, cmd_config.src_hgt, bIsOutputYuv);
        LOGI("dst CRC (%s MSB order) of frame #%04d: 0x%08X\n", bIsOutputYuv ? "VYU" : "RGB", k, crc_val);
        if (fp_crc) {
            if (mode_idx >= 0 && mode_idx < DCI_MODE_MAX) {
                fprintf(fp_crc, "input: %s, cmd_config: dci_standard_mode_%02d_%s, crc (%s MSB order) of frame #%04d: 0x%08X\n",
                    get_basename(cmd_config.input_file), mode_idx, g_supported_dci_mode_str[mode_idx],
                    bIsOutputYuv ? "VYU" : "RGB", k, crc_val);
            }
            else {
                fprintf(fp_crc, "input: %s, cmd_config: %s, crc (%s MSB order) of frame #%04d: 0x%08X\n",
                    get_basename(cmd_config.input_file), get_basename(cmd_config.config_file),
                    bIsOutputYuv ? "VYU" : "RGB", k, crc_val);
            }
        }
    }
    LOGI("done. write output to file: '%s'\n", cmd_config.output_file);
#endif
    fclose(fp_src);
    fclose(fp_dst);
    if (fp_crc)
        fclose(fp_crc);
    free(p_src);
    free(p_dst);

    return ret;
}