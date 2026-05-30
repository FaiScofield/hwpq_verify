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

/* ------------------------------------------------------------------ */
/* Frame I/O helpers                                                  */
/* ------------------------------------------------------------------ */

/**
 * @brief  Read one YUV frame from a raw file into malloc'd buffer.
 * @param  path      File path.
 * @param  width     Frame width in pixels.
 * @param  height    Frame height in pixels.
 * @param  bits      Bit depth (8 or 10).
 * @param  frame_idx Zero-based frame index.
 * @param  out_size  [out] Number of bytes read.
 * @return malloc'd buffer, or nullptr on failure.
 */
static uint8_t *read_yuv_frame(const char *path, int width, int height,
                               int bits, int frame_idx, size_t *out_size) {
    if (!path || width <= 0 || height <= 0) return nullptr;

    size_t frame_bytes;
    if (bits == 10) {
        /* 10-bit YUV444: 4 bytes per 3 samples packed */
        frame_bytes = static_cast<size_t>(width) * height * 4;
    } else {
        frame_bytes = static_cast<size_t>(width) * height * 3 / 2;
    }

    FILE *fp = fopen(path, "rb");
    if (!fp) {
        fprintf(stderr, "cannot open input file: %s\n", path);
        return nullptr;
    }

    long offset = static_cast<long>(frame_idx) * static_cast<long>(frame_bytes);
    if (fseek(fp, offset, SEEK_SET) != 0) {
        fclose(fp);
        fprintf(stderr, "seek to frame %d failed\n", frame_idx);
        return nullptr;
    }

    uint8_t *buf = static_cast<uint8_t *>(malloc(frame_bytes));
    if (!buf) {
        fclose(fp);
        fprintf(stderr, "memory allocation failed for frame\n");
        return nullptr;
    }

    size_t read_bytes = fread(buf, 1, frame_bytes, fp);
    fclose(fp);

    if (read_bytes != frame_bytes) {
        free(buf);
        fprintf(stderr, "short read: got %zu, expected %zu\n", read_bytes,
                frame_bytes);
        return nullptr;
    }

    *out_size = frame_bytes;
    return buf;
}

/**
 * @brief  Write one YUV frame buffer to a raw file.
 * @return true on success.
 */
static bool write_yuv_frame(const char *path, const uint8_t *data,
                            size_t size) {
    FILE *fp = fopen(path, "wb");
    if (!fp) return false;
    size_t written = fwrite(data, 1, size, fp);
    fclose(fp);
    return written == size;
}

/**
 * @brief  Fill an img_info_t for a YUV444 10-bit planar buffer.
 *
 * The DCI library expects planar layout. For 10-bit YUV444 this means
 * three planes (Y, U, V) each width*height samples, stored as 16-bit
 * values in little-endian.
 */
static void fill_img_info_10bit_planar(img_info_t *info, uint8_t *buf,
                                       int width, int height, int bits) {
    memset(info, 0, sizeof(*info));
    info->plane_num = 3;
    int sample_size = (bits == 10) ? 2 : 1;

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
    info->is_yuv = 1;
    info->is_rgb = 0;
}

/* ------------------------------------------------------------------ */
/* Library struct translation                                         */
/* ------------------------------------------------------------------ */

static void dci_fill_init_param(const dci_runner_request_t &request,
                                dci_init_param_t *init_param) {
    memset(init_param, 0, sizeof(*init_param));
    init_param->platform = request.platform;
    init_param->debug_dump_mask =
        static_cast<unsigned int>(request.debug_dump_mask);
    snprintf(init_param->debug_path, sizeof(init_param->debug_path), "%s",
             request.debug_path.c_str());
}

static void dci_fill_proc_param(const dci_runner_request_t &request,
                                dci_proc_param_t *proc_param, uint8_t *src_buf,
                                uint8_t *dst_buf, int width, int height,
                                int bits) {
    memset(proc_param, 0, sizeof(*proc_param));
    proc_param->dci_enable = 1;

    /* Fill source image info */
    fill_img_info_10bit_planar(&proc_param->src_info, src_buf, width, height,
                               bits);

    /* Fill destination image info (output buffer) */
    fill_img_info_10bit_planar(&proc_param->dst_info, dst_buf, width, height,
                               bits);

    proc_param->frame_idx = request.frame_idx;
    proc_param->frame_num = request.frame_num;

    snprintf(proc_param->config_path, sizeof(proc_param->config_path), "%s",
             request.config_path.c_str());
    snprintf(proc_param->reg_path, sizeof(proc_param->reg_path), "%s",
             request.reg_path.c_str());

    proc_param->is_src_fullrange = request.is_src_fullrange;

    /* Copy audit struct directly - field names must match the library ABI */
    memcpy(&proc_param->audit, &request.audit, sizeof(proc_param->audit));
}

/* ------------------------------------------------------------------ */
/* Entry point                                                        */
/* ------------------------------------------------------------------ */

int main(int argc, char *argv[]) {
    const char *request_path = nullptr;
    const char *result_path = nullptr;

    /* Parse CLI arguments */
    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--request") == 0 && i + 1 < argc) {
            request_path = argv[++i];
        } else if (strcmp(argv[i], "--result") == 0 && i + 1 < argc) {
            result_path = argv[++i];
        }
    }

    if (request_path == nullptr) {
        fprintf(stderr,
                "usage: dci_verify_runner --request <file> [--result <file>]\n");
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
    size_t frame_size = 0;
    int bits = (request.pixel_format == 19) ? 10 : 8;
    uint8_t *src_buf = read_yuv_frame(request.input_file.c_str(), request.width,
                                      request.height, bits, request.frame_idx,
                                      &frame_size);
    if (!src_buf) {
        result.exit_code = 1;
        result.status = "request_error";
        result.message = "failed to read input frame";
        result.working_dir = request.audit.working_dir;
        dci_write_runner_result(result_path, result, nullptr);
        return 1;
    }

    /* Allocate output buffer */
    uint8_t *dst_buf =
        static_cast<uint8_t *>(calloc(1, frame_size));
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
    dci_fill_proc_param(request, &proc_param, src_buf, dst_buf, request.width,
                        request.height, bits);

    ret = dciVerifyProc(handle, &proc_param);

    /* Step 5: Deinit */
    dciVerifyDeinit(handle);

    /* Step 6: Write output frame if requested */
    if (ret == 0 && !request.output_file.empty()) {
        if (!write_yuv_frame(request.output_file.c_str(), dst_buf, frame_size)) {
            fprintf(stderr, "warning: failed to write output frame\n");
        }
    }

    /* Step 7: Write runner_result.json */
    result.exit_code = ret;
    result.status = (ret == 0) ? "ok" : "runtime_error";
    result.message =
        (ret == 0) ? "dci request finished" : "dciVerifyProc failed";
    result.working_dir = request.audit.working_dir;
    dci_write_runner_result(result_path, result, nullptr);

    /* Step 8: Copy runner_request.json into working_dir for traceability */
    if (request.audit.working_dir[0] != '\0') {
        std::string req_copy =
            std::string(request.audit.working_dir) + "/runner_request.json";
        /* best-effort copy; don't fail if directory doesn't exist yet */
        FILE *src = fopen(request_path, "rb");
        FILE *dst = fopen(req_copy.c_str(), "wb");
        if (src && dst) {
            char ch;
            while (fread(&ch, 1, 1, src) == 1) fwrite(&ch, 1, 1, dst);
        }
        if (src) fclose(src);
        if (dst) fclose(dst);
    }

    free(src_buf);
    free(dst_buf);

    if (ret != 0) {
        fprintf(stderr, "dciVerifyProc returned %d\n", ret);
        return 1;
    }

    return 0;
}
