/**
 * @copyright Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @description: dci_verify_demo.cpp
 * @author: vance.wu@rock-chips.com
 * @create: 2025-09-15
 * @history:
 */

#include "verify_com.h"
#include "verify_cmd_parser.h"
#include "verify_crc32.h"
#include "cJSON.h"
#include "stb_image.h"
#include <errno.h>
#include <stdio.h>
#include <string.h>

/**
 * @file    dci_verify_runner.cpp
 * @brief   Layer 1 DCI native runner executable.
 *
 * Accepts one structured JSON request file, translates it into
 * dci_init_param_t / dci_proc_param_t, calls the compiled DCI verify
 * library, and writes a small runner_result.json at the end.
 *
 * CLI contract:
 *   dci_verify_runner --request <request.json> [--result <result.json>]
 *
 * Exit codes:
 *   0  - success
 *   1  - runtime error (library call failed)
 *   2  - invalid arguments
 */

#include "dci_request_io.h"
#include "dci_verify_api.h"

#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>


/**
 * @brief  Fill an img_info_t for a YUV444 10-bit planar buffer.
 *
 * The DCI library expects planar layout. For 10-bit YUV444 this means
 * three planes (Y, U, V) each width*height samples, stored as 16-bit
 * values in little-endian.
 */
static void fill_img_info_10bit_planar(img_info_t *info, uint8_t *buf, int width, int height, int bits, bool is_yuv)
{
    memset(info, 0, sizeof(*info));
    info->plane_num = 3;
    int sample_size = (bits > 8) ? 2 : 1;

    for (int p = 0; p < 3; p++) {
        info->plane_info[p].ptr = buf + p * width * height * sample_size;
        info->plane_info[p].offset = 0;
        info->plane_info[p].pix_strd = 1;
        info->img_w[p] = width;
        info->img_h[p] = height;
        info->img_ws[p] = width;
        info->img_hs[p] = height;
    }
    info->img_bits = bits;
    info->is_yuv = is_yuv;
    info->is_rgb = !is_yuv;
}

/* ------------------------------------------------------------------ */
/* Library struct translation                                         */
/* ------------------------------------------------------------------ */

static void dci_fill_init_param(const dci_runner_request_t& request, dci_init_param_t *init_param)
{
    memset(init_param, 0, sizeof(*init_param));
    init_param->platform = request.platform;
    init_param->debug_dump_mask = static_cast<unsigned int>(request.debug_dump_mask);
    snprintf(init_param->debug_path, sizeof(init_param->debug_path), "%s", request.debug_path.c_str());
}

static void dci_fill_proc_param(const dci_runner_request_t& request, dci_proc_param_t *proc_param, uint8_t *src_buf,
    uint8_t *dst_buf, int width, int height, int bits)
{
    memset(proc_param, 0, sizeof(*proc_param));
    proc_param->dci_enable = 1;

    /* Fill source image info */
    fill_img_info_10bit_planar(&proc_param->src_info, src_buf, width, height, bits,
        common_verify_imgfmt_is_yuv(request.pixel_format));

    /* Fill destination image info (output buffer) */
    fill_img_info_10bit_planar(&proc_param->dst_info, dst_buf, width, height, bits,
        common_verify_imgfmt_is_yuv(request.pixel_format));

    proc_param->frame_idx = request.frame_idx;
    proc_param->frame_num = request.frame_num;

    snprintf(proc_param->config_path, sizeof(proc_param->config_path), "%s", request.config_path.c_str());
    snprintf(proc_param->reg_path, sizeof(proc_param->reg_path), "%s", request.reg_path.c_str());

    proc_param->is_src_fullrange = request.is_src_fullrange;

    /* Copy audit struct directly - field names must match the library ABI */
    memcpy(&proc_param->audit, &request.audit, sizeof(proc_param->audit));
}

/* ------------------------------------------------------------------ */
/* Entry point                                                        */
/* ------------------------------------------------------------------ */

int run_as_runner(int argc, char *const argv[])
{
    const char *request_path = nullptr;
    const char *result_path = nullptr;

    /* Parse CLI arguments using getopt */
    int opt;
    opterr = 0; // handle errors manually

    // We only need to support --request and optionally --result for the runner mode
    // We need to use getopt_long for long options
    struct option long_options[] = {
        {"request", required_argument, 0, 'r'},
        {"result",  required_argument, 0, 'o'},
        {0,         0,                 0, 0  }
    };

    // Reset optind to ensure correct parsing
    optind = 1;

    while ((opt = getopt_long(argc, argv, "r:o:", long_options, nullptr)) != -1) {
        switch (opt) {
        case 'r': request_path = optarg; break;
        case 'o': result_path = optarg; break;
        default:  break; // ignore other options, might be invalid
        }
    }

    if (request_path == nullptr) {
        fprintf(stderr, "usage: dci_verify_runner --request <file> [--result <file>]\n");
        return 2;
    }

    /* Default result path next to request file */
    std::string default_result_path;
    if (result_path == nullptr) {
        default_result_path = std::string(request_path);
        size_t dot = default_result_path.rfind('.');
        if (dot != std::string::npos)
            default_result_path = default_result_path.substr(0, dot);
        default_result_path += "_result.json";
        result_path = default_result_path.c_str();
    }

    dci_runner_result_t result;
    result.working_dir = "";

    /* Step 1: Parse request JSON */
    dci_runner_request_t request;
    std::string error_msg;
    if (!dci_load_runner_request(request_path, &request, &error_msg)) {
        result.exit_code = 1;
        result.status = "request_error";
        result.message = error_msg;
        dci_write_runner_result(result_path, result, nullptr);
        fprintf(stderr, "request error: %s\n", error_msg.c_str());
        return 1;
    }

    /* Step 2: Load input frame */
    const int bits = common_verify_imgfmt_depth(request.pixel_format);
    const int vir_w = request.width;
    const int vir_h = request.height;
    size_t frame_size = vir_w * vir_h * 4 * 2; // 4 channels x 16bpp
    uint8_t *src_buf = (uint8_t *)malloc(frame_size);
    if (!src_buf) {
        result.exit_code = 1;
        result.status = "request_error";
        result.message = "memory allocation failed for input frame";
        result.working_dir = request.audit.working_dir;
        dci_write_runner_result(result_path, result, nullptr);
        return 1;
    }

    FILE *fp_in = fopen(request.input_file.c_str(), "rb");
    if (!fp_in || image_read_to_planar(fp_in, src_buf, request.frame_idx, request.width, request.height, request.width,
                      request.height, request.pixel_format, bits, 0) != 0)
    {
        if (fp_in)
            fclose(fp_in);
        free(src_buf);
        result.exit_code = 1;
        result.status = "request_error";
        result.message = "failed to read input frame";
        result.working_dir = request.audit.working_dir;
        dci_write_runner_result(result_path, result, nullptr);
        return 1;
    }
    if (fp_in)
        fclose(fp_in);

    /* Allocate output buffer */
    uint8_t *dst_buf = static_cast<uint8_t *>(calloc(1, frame_size));
    if (!dst_buf) {
        free(src_buf);
        result.exit_code = 1;
        result.status = "request_error";
        result.message = "memory allocation failed for output buffer";
        result.working_dir = request.audit.working_dir;
        dci_write_runner_result(result_path, result, nullptr);
        return 1;
    }

    /* Step 3: Fill init param and call dciVerifyInit */
    dci_init_param_t init_param;
    dci_fill_init_param(request, &init_param);

    dci_handle_t handle = nullptr;
    int ret = dciVerifyInit(&handle, &init_param);
    if (ret != 0) {
        free(src_buf);
        free(dst_buf);
        result.exit_code = ret;
        result.status = "runtime_error";
        result.message = "dciVerifyInit failed";
        result.working_dir = request.audit.working_dir;
        dci_write_runner_result(result_path, result, nullptr);
        fprintf(stderr, "dciVerifyInit returned %d\n", ret);
        return 1;
    }

    /* Step 4: Fill proc param and call dciVerifyProc */
    dci_proc_param_t proc_param;
    dci_fill_proc_param(request, &proc_param, src_buf, dst_buf, request.width, request.height, bits);

    ret = dciVerifyProc(handle, &proc_param);

    /* Step 5: Deinit */
    dciVerifyDeinit(handle);

    /* Step 6: Write output frame if requested */
    if (ret == 0 && !request.output_file.empty()) {
        FILE *fp_out = fopen(request.output_file.c_str(), "wb");
        if (!fp_out || image_write_from_plannar(fp_out, dst_buf, 0, request.width, request.height, request.width,
                           request.height, request.pixel_format, bits, 0) != 0)
        {
            fprintf(stderr, "warning: failed to write output frame\n");
        }
        if (fp_out)
            fclose(fp_out);
    }

    /* Step 7: Write runner_result.json */
    result.exit_code = ret;
    result.status = (ret == 0) ? "ok" : "runtime_error";
    result.message = (ret == 0) ? "dci request finished" : "dciVerifyProc failed";
    result.working_dir = request.audit.working_dir;
    dci_write_runner_result(result_path, result, nullptr);

    /* Step 8: Copy runner_request.json into working_dir for traceability */
    if (request.audit.working_dir[0] != '\0') {
        std::string req_copy = std::string(request.audit.working_dir) + "/runner_request.json";
        /* best-effort copy; don't fail if directory doesn't exist yet */
        FILE *src = fopen(request_path, "rb");
        FILE *dst = fopen(req_copy.c_str(), "wb");
        if (src && dst) {
            char ch;
            while (fread(&ch, 1, 1, src) == 1)
                fwrite(&ch, 1, 1, dst);
        }
        if (src)
            fclose(src);
        if (dst)
            fclose(dst);
    }

    free(src_buf);
    free(dst_buf);

    if (ret != 0) {
        fprintf(stderr, "dciVerifyProc returned %d\n", ret);
        return 1;
    }

    return 0;
}


/* ------------------------------------------------------------------ */
/* Demo mode (standard CLI arguments)                                 */
/* ------------------------------------------------------------------ */

int run_as_demo(int argc, char *const argv[])
{
    int ret = 0;
    struct common_verify_cmd_config cmd_config = {0};
    ret = common_verify_arg_get_cmd_config(argc, argv, &cmd_config);
    if (ret < 0) {
        return ret;
    }
    common_verify_arg_dump_config(&cmd_config);

    if (cmd_config.crc_file[0] == '\0') {
        snprintf(cmd_config.crc_file, 1024, "%s/dci_crc_out.dat", cmd_config.output_dir);
        printf(" - crc_file update to: '%s'!\n", cmd_config.crc_file);
    }

    const int bIsInputYuv = common_verify_imgfmt_is_yuv(cmd_config.src_fmt);
    const int bIsOutputYuv = common_verify_imgfmt_is_yuv(cmd_config.dst_fmt);
    const size_t frame_size_max = cmd_config.src_wid * cmd_config.src_hgt * 4 * 2; // 4 channels x 16bpp

    void *p_src_raw = NULL;
    uint8_t *p_src = NULL;
    uint8_t *p_dst = NULL;
    FILE *fp_src = NULL, *fp_dst = NULL, *fp_crc = NULL;
    int crc_val = -1;

    const bool is_src_stb_img = is_stb_image(cmd_config.input_file);
    if (is_src_stb_img) {
        int nb_channels = 0;
        p_src_raw = read_stb_image_auto(cmd_config.input_file, &cmd_config.src_wid, &cmd_config.src_hgt, &nb_channels, 3);
        if (p_src_raw) {
            cmd_config.nb_frame = 1;
            cmd_config.src_fmt = RGB888;
            cmd_config.src_wid_vir = cmd_config.src_wid * 3;
            cmd_config.src_hgt_vir = cmd_config.src_hgt;
            printf("stb image read success, src size: %dx%d, fmt: RGB888\n", cmd_config.src_wid, cmd_config.src_hgt);
            if (cmd_config.dst_hgt != cmd_config.src_hgt || cmd_config.dst_wid != cmd_config.src_wid) {
                cmd_config.dst_hgt = cmd_config.src_hgt;
                cmd_config.dst_wid = cmd_config.src_wid;
                cmd_config.dst_wid_vir = MAX(cmd_config.dst_wid_vir,
                    ROUND_S32(cmd_config.dst_wid * common_verify_imgfmt_pitch_ratio(cmd_config.dst_fmt)));
                cmd_config.dst_hgt_vir = MAX(cmd_config.dst_hgt_vir, cmd_config.dst_hgt);
                printf("dst size updated to: %dx%d, the resolution in dst filename '%s' might not match!\n",
                    cmd_config.dst_wid, cmd_config.dst_hgt, cmd_config.output_file);
            }
        }
        else {
            goto EXIT;
        }
    }
    else {
        fp_src = fopen(cmd_config.input_file, "rb");
        if (!fp_src) {
            fprintf(stderr, "Failed to open the input file '%s'! %s\n", cmd_config.input_file, strerror(errno));
            goto EXIT;
        }
    }

    p_src = (uint8_t *)calloc(frame_size_max, 1);
    p_dst = (uint8_t *)calloc(frame_size_max, 1);
    if (!p_src || !p_dst) {
        goto EXIT;
    }

    fp_dst = fopen(cmd_config.output_file, "wb");
    if (!fp_dst) {
        fprintf(stderr, "Failed to open the output file '%s'! %s\n", cmd_config.output_file, strerror(errno));
        goto EXIT;
    }

    fp_crc = fopen(cmd_config.crc_file, "a");
    if (!fp_crc) {
        fprintf(stderr, "Failed to open the crc output file '%s'! %s. CRC value will not be written!\n",
            cmd_config.crc_file, strerror(errno));
    }

    dci_handle_t handle;
    dci_init_param_t init_param;
    memset(&init_param, 0, sizeof(init_param));
    init_param.platform = 3572; // default or parse from cmd_config.platform_name

    ret = dciVerifyInit(&handle, &init_param);
    if (ret != 0) {
        fprintf(stderr, "dciVerifyInit returned %d\n", ret);
        goto EXIT;
    }

    for (int k = 0; k < cmd_config.nb_frame; k++) {
        if (is_src_stb_img) {
            // DCI library expects 10-bit planar YUV or RGB?
            // Currently DCI process expects planar layout, let's use 10bit planar
            ret = imgcvt_to_planar_10bit_lsb((uint8_t *)p_src_raw, (uint16_t *)p_src, cmd_config.src_wid,
                cmd_config.src_hgt, cmd_config.src_wid_vir, cmd_config.src_hgt_vir, cmd_config.src_wid * 2,
                cmd_config.src_hgt, cmd_config.src_fmt, false, 0);
        }
        else {
            ret = image_read_to_10bit_planar(fp_src, p_src, k, cmd_config.src_wid, cmd_config.src_hgt,
                cmd_config.src_wid_vir, cmd_config.src_hgt_vir, cmd_config.src_fmt, cmd_config.dither_up);
        }
        if (ret) {
            fprintf(stderr, "Failed to read frame #%d from input file '%s'! %s\n", k, cmd_config.input_file, strerror(errno));
            break;
        }

        crc_val = get_crc_for_planar_frame_10bit(p_src, cmd_config.src_wid, cmd_config.src_hgt, bIsInputYuv);
        printf("src CRC (%s MSB order) of frame #%04d: 0x%08X\n", bIsInputYuv ? "VYU" : "RGB", k, crc_val);

        dci_proc_param_t proc_param;
        memset(&proc_param, 0, sizeof(proc_param));
        proc_param.dci_enable = 1;
        fill_img_info_10bit_planar(&proc_param.src_info, p_src, cmd_config.src_wid, cmd_config.src_hgt, 10,
            common_verify_imgfmt_is_yuv(cmd_config.src_fmt));
        fill_img_info_10bit_planar(&proc_param.dst_info, p_dst, cmd_config.dst_wid, cmd_config.dst_hgt, 10,
            common_verify_imgfmt_is_yuv(cmd_config.dst_fmt));
        proc_param.frame_idx = k;
        proc_param.frame_num = cmd_config.nb_frame;
        snprintf(proc_param.config_path, sizeof(proc_param.config_path), "%s", cmd_config.config_file);

        proc_param.is_src_fullrange = common_verify_clrspc_is_full_range(cmd_config.src_clrspc);

        ret = dciVerifyProc(handle, &proc_param);
        if (ret != 0) {
            fprintf(stderr, "dciVerifyProc failed for frame %d\n", k);
            break;
        }

        ret = image_write_from_plannar(fp_dst, (ushort *)p_dst, k, cmd_config.dst_wid, cmd_config.dst_hgt,
            cmd_config.dst_wid_vir, cmd_config.dst_hgt_vir, cmd_config.dst_fmt, 10, cmd_config.dither_dn);
        if (ret) {
            break;
        }

        crc_val = get_crc_for_planar_frame_10bit(p_dst, cmd_config.dst_wid, cmd_config.dst_hgt, bIsOutputYuv);
        printf("dst CRC (%s MSB order) of frame #%04d: 0x%08X\n", bIsOutputYuv ? "VYU" : "RGB", k, crc_val);
        if (fp_crc) {
            fprintf(fp_crc, "input: %s, cmd_config: %s, crc (%s MSB order) of frame #%04d: 0x%08X\n",
                get_basename(cmd_config.input_file), get_basename(cmd_config.config_file), bIsOutputYuv ? "VYU" : "RGB",
                k, crc_val);
        }
    }

    dciVerifyDeinit(handle);

    if (0 == ret) {
        printf("done. write output to file: '%s'\n", cmd_config.output_file);
    }
    else {
        fprintf(stderr, "error happened, please have a check!\n");
    }

EXIT:
    if (fp_src)
        fclose(fp_src);
    if (fp_dst)
        fclose(fp_dst);
    if (fp_crc)
        fclose(fp_crc);
    if (p_src_raw)
        free(p_src_raw);
    if (p_src)
        free(p_src);
    if (p_dst)
        free(p_dst);

    return ret;
}

int main(int argc, char *const argv[])
{
    // If --request is present, run as runner mode
    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--request") == 0) {
            return run_as_runner(argc, argv);
        }
    }

    // Otherwise, run as demo mode
    return run_as_demo(argc, argv);
}
