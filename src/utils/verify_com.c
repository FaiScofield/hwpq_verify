/**
 * @copyright:   Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @description: verify_com.c
 * @author:      vance.wu@rock-chips.com
 * @create:      2025-09-12
 * @modifier:    vance.wu@rock-chips.com
 * @modify:      2026-03-03
 */

#include "verify_com.h"
#include <assert.h>

/********** directory / file operation **********/
#if defined(_WIN32)

#include <windows.h>

const char *errcode2str(DWORD ErrorCode)
{
    HLOCAL LocalAddress = NULL;
    FormatMessage(FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_IGNORE_INSERTS | FORMAT_MESSAGE_FROM_SYSTEM, NULL,
        ErrorCode, MAKELANGID(LANG_ENGLISH, SUBLANG_ENGLISH_US), (PTSTR)&LocalAddress, 0, NULL);
    return (const char *)LocalAddress;
}

int is_directory(const char *path)
{
    DWORD attr = GetFileAttributes(path);
    if (attr == INVALID_FILE_ATTRIBUTES) {
        DWORD err = GetLastError();
        LOGE("GetFileAttributes(%s) failed! error code: %d - %s\n", path, (int)err, errcode2str(err));
        return -1;
    }
    return (attr & FILE_ATTRIBUTE_DIRECTORY) != 0;
}

int is_regular_file(const char *path)
{
    DWORD attr = GetFileAttributes(path);
    if (attr == INVALID_FILE_ATTRIBUTES) {
        DWORD err = GetLastError();
        LOGE("GetFileAttributes(%s) failed! error code: %d - %s\n", path, (int)err, errcode2str(err));
        return -1;
    }
    return (attr & FILE_ATTRIBUTE_DIRECTORY) == 0;
}

const char *get_dirname(const char *path)
{
    char drive[_MAX_DRIVE] = {0};
    char dir[_MAX_DIR] = {0};
    char fname[_MAX_FNAME] = {0};
    char ext[_MAX_EXT] = {0};
    _splitpath(path, drive, dir, fname, ext);

    static char dirname[_MAX_DRIVE + _MAX_DIR];
    snprintf(dirname, _MAX_DRIVE + _MAX_DIR, "%s%s", drive, dir);
    return dirname;
}

const char *get_basename(const char *path)
{
    if (path == NULL || *path == '\0')
        return ".";

    bool back_slash = false;
    char *last_slash = (char *)strrchr(path, '/');
    if (last_slash == NULL) {
        last_slash = (char *)strrchr(path, '\\');
        if (last_slash)
            back_slash = true;
        else
            return path;
    }

    if (*(last_slash + 1) == '\0') {
        *last_slash = '\0';
        last_slash = (char *)strrchr(path, back_slash ? '\\' : '/');
        if (last_slash == NULL)
            return path;
    }

    return (const char *)last_slash + 1;
}

#else

#include <sys/stat.h> // lstat
#include <libgen.h>   // POSIX header for dirname, basename
#include <errno.h>
#include <string.h>

int is_directory(const char *path)
{
    struct stat statbuf;
    if (lstat(path, &statbuf) != 0) {
        LOGE("%s: call lstat failed! %s\n", __func__, strerror(errno));
        return -1;
    }
    return S_ISDIR(statbuf.st_mode);
}

int is_regular_file(const char *path)
{
    struct stat statbuf;
    if (lstat(path, &statbuf) != 0) {
        LOGE("%s: call lstat failed! %s\n", __func__, strerror(errno));
        return -1;
    }
    return S_ISREG(statbuf.st_mode);
}

const char *get_dirname(const char *path) { return dirname((char *)path); }

const char *get_basename(const char *path) { return basename((char *)path); }
#endif


/********** image io functions **********/
int image_read_to_planar(FILE *fp, void *p_buf, int frmidx, int w, int h, int wstrd, int hstrd, int fmt, int depth, int dither)
{
    if (!fp || !p_buf) {
        LOGE_f("invalid fp or output buffer!\n");
        return -1;
    }
    if (frmidx < 0 || w <= 0 || h <= 0 || wstrd < w || hstrd < h) {
        LOGE_f("invalid argument! frmidx: %d, w: %d, h: %d, wstrd: %d, hstrd: %d, fmt: %#x, %s\n", frmidx, w, h, wstrd,
            hstrd, fmt, common_verify_imgfmt_name(fmt));
        return -1;
    }

    // src format info
    int ret = 0;
    const int bpp = common_verify_imgfmt_bpp(fmt);
    // const int frame_size = (w * h * bpp + 7) / 8;
    const int frame_size = wstrd * hstrd * common_verify_imgfmt_framesize_ratio(fmt);

    uchar *p_src = (uchar *)malloc(frame_size);
    fseek(fp, frame_size * frmidx, SEEK_SET);
    const size_t read_size = fread(p_src, 1, frame_size, fp);
    if (read_size != frame_size) {
        LOGE_f("readSize(%zu) != frameSize(%d) for frame#%d format %#x!\n", read_size, frame_size, frmidx, fmt);
        ret = -1;
    }

    const int src_stride = wstrd;  //common_verify_imgfmt_pitch_ratio(fmt) * w;
    const bool keep_alpha = false; // ignore alpha channel here

    if (0 == ret) {
        if (depth == 8) {
            const int dst_stride = w * 1;
            ret = imgcvt_to_planar_8bit_lsb(p_src, (uint8_t *)p_buf, w, h, wstrd, hstrd, dst_stride, h, fmt, keep_alpha, dither);
        }
        else if (depth == 10) {
            const int dst_stride = w * 2;
            ret = imgcvt_to_planar_10bit_lsb(p_src, (uint16_t *)p_buf, w, h, wstrd, hstrd, dst_stride, h, fmt,
                keep_alpha, dither);
        }
        else {
            LOGE_f("invalid target depth=%d !\n", depth);
            ret = -1;
        }
    }

    free(p_src);
    return ret;
}

int image_write_from_plannar(FILE *fp, void *p_buf, int frmidx, int w, int h, int wstrd, int hstrd, int fmt, int depth, int dither)
{
    if (!fp || !p_buf) {
        LOGE_f("invalid fp or output buffer!\n");
        return -1;
    }
    if (frmidx < 0 || w <= 0 || h <= 0 || wstrd < w || hstrd < h) {
        LOGE_f("invalid argument! frmidx: %d, w: %d, h: %d, wstrd: %d, hstrd: %d, fmt: %#x, %s\n", frmidx, w, h, wstrd,
            hstrd, fmt, common_verify_imgfmt_name(fmt));
        return -1;
    }

    // dst format info
    int ret = 0;
    const int bpp = common_verify_imgfmt_bpp(fmt);
    // const int frame_size = (w * h * bpp + 7) / 8;
    const int frame_size = wstrd * hstrd * common_verify_imgfmt_framesize_ratio(fmt);
    const int dst_wstrd = wstrd;  //common_verify_imgfmt_pitch_ratio(fmt) * w;
    const bool has_alpha = false; // ignore alpha channel here

    ushort *p_dst = (ushort *)calloc(frame_size, 1);
    if (depth == 8) {
        const int src_wstrd = w;
        ret = imgcvt_from_planar_8bit_lsb((uint8_t *)p_buf, (uint8_t *)p_dst, w, h, src_wstrd, h, wstrd, hstrd, fmt,
            has_alpha, dither);
    }
    else if (depth == 10) {
        const int src_wstrd = w * 2;
        ret = imgcvt_from_planar_10bit_lsb((uint16_t *)p_buf, (uint8_t *)p_dst, w, h, src_wstrd, h, wstrd, hstrd, fmt,
            has_alpha, dither);
    }
    else {
        LOGE_f("invalid target depth=%d !\n", depth);
        ret = -1;
    }

    if (0 == ret) {
        fseek(fp, frame_size * frmidx, SEEK_SET);
        size_t write_size = fwrite(p_dst, 1, frame_size, fp);
        if (write_size != frame_size) {
            LOGE_f("writeSize(%zu) != frameSize(%d) for frame#%d format %#x!\n", write_size, frame_size, frmidx, fmt);
            ret = -1;
        }
    }
    else {
        LOGE_f("imgcvt_from_planar failed! %d\n", ret);
        ret = -1;
    }

    free(p_dst);
    return ret;
}

int image_read_to_10bit_planar(FILE *fp, void *p_buf, int frmidx, int w, int h, int wstrd, int hstrd, int fmt, int dither)
{
    return image_read_to_planar(fp, p_buf, frmidx, w, h, wstrd, hstrd, fmt, 10, dither);
}

int image_write_from_10bit_plannar(FILE *fp, void *p_buf, int frmidx, int w, int h, int wstrd, int hstrd, int fmt, int dither)
{
    return image_write_from_plannar(fp, p_buf, frmidx, w, h, wstrd, hstrd, fmt, 10, dither);
}

int image_read(FILE *fp, void *p_buf, int frmidx, int w, int h, int fmt)
{
    if (!fp || !p_buf) {
        LOGE("invalid fp or input buffer!\n");
        return -1;
    }
    if (frmidx < 0 || w <= 0 || h <= 0) {
        LOGE("invalid argument! frmidx: %d, w: %d, h: %d\n", frmidx, w, h);
        return -1;
    }

    const int bpp = common_verify_imgfmt_bpp(fmt);
    const int frame_size = (w * h * bpp + 7) / 8;
    LOGD("fmt: %#x(%s), bpp: %d, frame_size: %d\n", fmt, common_verify_imgfmt_name(fmt), bpp, frame_size);

    fseek(fp, frame_size * frmidx, SEEK_SET);
    size_t read_size = fread(p_buf, 1, frame_size, fp);
    if (read_size != frame_size) {
        LOGE("readSize(%zu) != frameSize(%d) for frame#%d format %#x!\n", read_size, frame_size, frmidx, fmt);
        return -1;
    }

    return 0;
}

int image_write(FILE *fp, void *p_buf, int frmidx, int w, int h, int fmt)
{
    if (!fp || !p_buf) {
        LOGE("invalid fp or output buffer!\n");
        return -1;
    }
    if (frmidx < 0 || w <= 0 || h <= 0) {
        LOGE("invalid argument! frmidx: %d, w: %d, h: %d\n", frmidx, w, h);
        return -1;
    }

    const int bpp = common_verify_imgfmt_bpp(fmt);
    const int frame_size = (w * h * bpp + 7) / 8;
    LOGD("fmt: %#x(%s), bpp: %d, frame_size: %d\n", fmt, common_verify_imgfmt_name(fmt), bpp, frame_size);

    size_t write_size = fwrite(p_buf, 1, frame_size, fp);
    if (write_size != frame_size) {
        LOGE("writeSize(%zu) != frameSize(%d) for frame#%d format %#x!\n", write_size, frame_size, frmidx, fmt);
        return -1;
    }

    return 0;
}

/* pack / unpack */
inline static void pack_data_10bit(uint16_t const *unpacked_data_u16x4, uint8_t *packed_data_u8x5)
{
    packed_data_u8x5[0] = unpacked_data_u16x4[0] & 0xFF;
    packed_data_u8x5[1] = ((unpacked_data_u16x4[1] & 0x3F) << 2) | ((unpacked_data_u16x4[0] >> 8) & 0x03);
    packed_data_u8x5[2] = ((unpacked_data_u16x4[2] & 0x0F) << 4) | ((unpacked_data_u16x4[1] >> 6) & 0x0F);
    packed_data_u8x5[3] = ((unpacked_data_u16x4[3] & 0x03) << 6) | ((unpacked_data_u16x4[2] >> 4) & 0x3F);
    packed_data_u8x5[4] = (unpacked_data_u16x4[3] >> 2) & 0xFF;
}

inline static void unpack_data_10bit(uint8_t const *packed_data_u8x5, uint16_t *unpacked_data_u16x4)
{
    unpacked_data_u16x4[0] = (uint16_t)((packed_data_u8x5[0] >> 0) & 0xFF) | ((packed_data_u8x5[1] & 0x03) << 8);
    unpacked_data_u16x4[1] = (uint16_t)((packed_data_u8x5[1] >> 2) & 0x3F) | ((packed_data_u8x5[2] & 0x0F) << 6);
    unpacked_data_u16x4[2] = (uint16_t)((packed_data_u8x5[2] >> 4) & 0x0F) | ((packed_data_u8x5[3] & 0x3F) << 4);
    unpacked_data_u16x4[3] = (uint16_t)((packed_data_u8x5[3] >> 6) & 0x03) | ((packed_data_u8x5[4] & 0xFF) << 2);
}

inline static void unpack_data_1010102(uint32_t packed_data, uint16_t *unpacked_data_u16x4, bool save_alpha)
{
    unpacked_data_u16x4[0] = (packed_data >> 0) & 0x03FF;
    unpacked_data_u16x4[1] = (packed_data >> 10) & 0x03FF;
    unpacked_data_u16x4[2] = (packed_data >> 20) & 0x03FF;
    if (save_alpha) {
        unpacked_data_u16x4[3] = (packed_data >> 30) & 0x03;
    }
}

int imgcvt_pack_10bit(uint16_t const *p_src, uint8_t *p_dst, int w, int h, int src_strd, int dst_strd, int fmt)
{
    switch (fmt) {
    case RGB_101010LSB:
    case YUV444I_10LSB: {
        for (int i = 0; i < h; i++) {
            const uint16_t *src_y = (uint16_t *)((uint8_t *)p_src + i * src_strd);
            uint8_t *dst_y = (uint8_t *)((uint8_t *)p_dst + i * dst_strd);
            for (int j = 0, k = 0; j < w * 3; j += 4, k += 5) {
                pack_data_10bit(src_y + j, dst_y + k);
            }
        }
    } break;
    case RGB_PLANAR10LSB:
    case YUV444P_10LSB:   {
        for (int i = 0; i < h; i++) {
            const uint16_t *src_y = (uint16_t *)((uint8_t *)p_src + i * src_strd);
            const uint16_t *src_u = (uint16_t *)((uint8_t *)src_y + src_strd * h);
            const uint16_t *src_v = (uint16_t *)((uint8_t *)src_u + src_strd * h);
            uint8_t *dst_y = (uint8_t *)((uint8_t *)p_dst + i * dst_strd);
            uint8_t *dst_u = (uint8_t *)((uint8_t *)dst_y + dst_strd * h);
            uint8_t *dst_v = (uint8_t *)((uint8_t *)dst_u + dst_strd * h);
            for (int j = 0, k = 0; j < w; j += 4, k += 5) {
                pack_data_10bit(src_y + j, dst_y + k);
                pack_data_10bit(src_u + j, dst_u + k);
                pack_data_10bit(src_v + j, dst_v + k);
            }
        }
    } break;
    case YUV444SP_10LSB: {
        for (int i = 0; i < h; i++) {
            const uint16_t *src_y = (uint16_t *)((uint8_t *)p_src + i * src_strd);
            const uint16_t *src_c = (uint16_t *)((uint8_t *)src_y + src_strd * h);
            uint8_t *dst_y = (uint8_t *)((uint8_t *)p_dst + i * dst_strd);
            uint8_t *dst_c = (uint8_t *)((uint8_t *)dst_y + dst_strd * h);
            int jc = 0, kc = 0;
            for (int j = 0, k = 0; j < w; j += 4, k += 5) {
                pack_data_10bit(src_y + j, dst_y + k);
                pack_data_10bit(src_c + jc, dst_c + kc);
                pack_data_10bit(src_c + jc + 4, dst_c + kc + 5);
                jc += 8;
                kc += 10;
            }
        }
    } break;
    case YUV422SP_10LSB: {
        for (int i = 0; i < h; i++) {
            const uint16_t *src_y = (uint16_t *)((uint8_t *)p_src + i * src_strd);
            const uint16_t *src_c = (uint16_t *)((uint8_t *)src_y + src_strd * h);
            uint8_t *dst_y = (uint8_t *)((uint8_t *)p_dst + i * dst_strd);
            uint8_t *dst_c = (uint8_t *)((uint8_t *)dst_y + dst_strd * h);
            for (int j = 0, k = 0; j < w; j += 4, k += 5) {
                pack_data_10bit(src_y + j, dst_y + k);
                pack_data_10bit(src_c + j, dst_c + k);
            }
        }
    } break;
    case YUV420SP_10LSB: {
        for (int i = 0; i < h / 2; i++) {
            const uint16_t *src_y0 = (uint16_t *)((uint8_t *)p_src + i * 2 * src_strd);
            const uint16_t *src_y1 = (uint16_t *)((uint8_t *)src_y0 + src_strd);
            const uint16_t *src_uv = (uint16_t *)((uint8_t *)p_src + h * src_strd + i * src_strd);
            uint8_t *dst_y0 = (uint8_t *)((uint8_t *)p_dst + i * 2 * dst_strd);
            uint8_t *dst_y1 = (uint8_t *)((uint8_t *)dst_y0 + dst_strd);
            uint8_t *dst_uv = (uint8_t *)((uint8_t *)p_dst + h * dst_strd + i * dst_strd);
            for (int j = 0, k = 0; j < w; j += 4, k += 5) {
                pack_data_10bit(src_y0 + j, dst_y0 + k);
                pack_data_10bit(src_y1 + j, dst_y1 + k);
                pack_data_10bit(src_uv + j, dst_uv + k);
            }
        }
    } break;
    default: LOGE_f("unsupported image format %#x case to pack !\n", fmt); return -1;
    }
    return 0;
}

int imgcvt_unpack_10bit(uint8_t const *p_src, uint16_t *p_dst, int w, int h, int src_strd, int dst_strd, int fmt)
{
    switch (fmt) {
    case RGB_10PACKED:
    case YUV444I_10PACKED: {
        for (int i = 0; i < h; i++) {
            const uint8_t *src_y = (uint8_t *)((uint8_t *)p_src + i * src_strd);
            uint16_t *dst_y = (uint16_t *)((uint8_t *)p_dst + i * dst_strd);
            for (int j = 0, k = 0; j < w * 3; j += 4, k += 5) {
                unpack_data_10bit(src_y + k, dst_y + j);
            }
        }
    } break;
    case RGBA_1010102: { // [A2:B10:G10:R10]
        assert(dst_strd >= w * sizeof(uint16_t) * 3);
        const bool b_save_alpha = dst_strd >= w * sizeof(uint16_t) * 4;
        const int channels = b_save_alpha ? 4 : 3;
        for (int i = 0; i < h; i++) {
            const uint32_t *src_y = (uint32_t *)((uint8_t *)p_src + i * src_strd);
            uint16_t *dst_y = (uint16_t *)((uint8_t *)p_dst + i * dst_strd);
            for (int j = 0; j < w; j++) {
                unpack_data_1010102(src_y[j], dst_y + j * channels, b_save_alpha);
            }
        }
    } break;
    case RGB_PLANAR10PACKED:
    case YUV444P_10PACKED:   {
        for (int i = 0; i < h; i++) {
            const uint8_t *src_y = (uint8_t *)((uint8_t *)p_src + i * src_strd);
            const uint8_t *src_u = (uint8_t *)((uint8_t *)src_y + src_strd * h);
            const uint8_t *src_v = (uint8_t *)((uint8_t *)src_u + src_strd * h);
            uint16_t *dst_y = (uint16_t *)((uint8_t *)p_dst + i * dst_strd);
            uint16_t *dst_u = (uint16_t *)((uint8_t *)dst_y + dst_strd * h);
            uint16_t *dst_v = (uint16_t *)((uint8_t *)dst_u + dst_strd * h);
            for (int j = 0, k = 0; j < w; j += 4, k += 5) {
                unpack_data_10bit(src_y + k, dst_y + j);
                unpack_data_10bit(src_u + k, dst_u + j);
                unpack_data_10bit(src_v + k, dst_v + j);
            }
        }
    } break;
    case YUV444SP_10PACKED: {
        for (int i = 0; i < h; i++) {
            const uint8_t *src_y = (uint8_t *)((uint8_t *)p_src + i * src_strd);
            const uint8_t *src_c = (uint8_t *)((uint8_t *)src_y + src_strd * h);
            uint16_t *dst_y = (uint16_t *)((uint8_t *)p_dst + i * dst_strd);
            uint16_t *dst_c = (uint16_t *)((uint8_t *)dst_y + dst_strd * h);
            int jc = 0, kc = 0;
            for (int j = 0, k = 0; j < w; j += 4, k += 5) {
                unpack_data_10bit(src_y + k, dst_y + j);
                unpack_data_10bit(src_c + kc, dst_c + jc);
                unpack_data_10bit(src_c + kc + 5, dst_c + jc + 4);
                jc += 8;
                kc += 10;
            }
        }
    } break;
    case YUV422SP_10PACKED: {
        for (int i = 0; i < h; i++) {
            const uint8_t *src_y = (uint8_t *)((uint8_t *)p_src + i * src_strd);
            const uint8_t *src_c = (uint8_t *)((uint8_t *)src_y + src_strd * h);
            uint16_t *dst_y = (uint16_t *)((uint8_t *)p_dst + i * dst_strd);
            uint16_t *dst_c = (uint16_t *)((uint8_t *)dst_y + dst_strd * h);
            for (int j = 0, k = 0; j < w; j += 4, k += 5) {
                unpack_data_10bit(src_y + k, dst_y + j);
                unpack_data_10bit(src_c + k, dst_c + j);
            }
        }
    } break;
    case YUV420SP_10PACKED: {
        for (int i = 0; i < h / 2; i++) {
            const uint8_t *src_y0 = (uint8_t *)((uint8_t *)p_src + i * 2 * src_strd);
            const uint8_t *src_y1 = (uint8_t *)((uint8_t *)src_y0 + src_strd);
            const uint8_t *src_uv = (uint8_t *)((uint8_t *)p_src + h * src_strd + i * src_strd);
            uint16_t *dst_y0 = (uint16_t *)((uint8_t *)p_dst + i * 2 * dst_strd);
            uint16_t *dst_y1 = (uint16_t *)((uint8_t *)dst_y0 + dst_strd);
            uint16_t *dst_uv = (uint16_t *)((uint8_t *)p_dst + h * dst_strd + i * dst_strd);
            for (int j = 0, k = 0; j < w; j += 4, k += 5) {
                unpack_data_10bit(src_y0 + k, dst_y0 + j);
                unpack_data_10bit(src_y1 + k, dst_y1 + j);
                unpack_data_10bit(src_uv + k, dst_uv + j);
            }
        }
    } break;
    case YUV400_10PACKED: {
        for (int i = 0; i < h; i++) {
            const uint8_t *src_y = (uint8_t *)((uint8_t *)p_src + i * src_strd);
            uint16_t *dst_y = (uint16_t *)((uint8_t *)p_dst + i * dst_strd);
            for (int j = 0, k = 0; j < w; j += 4, k += 5) {
                unpack_data_10bit(src_y + k, dst_y + j);
            }
        }
    } break;
    default: LOGE_f("unsupported image format %#x case to pack !\n", fmt); return -1;
    }
    return 0;
}

int imgcvt_to_planar_10bit_lsb(uint8_t const *p_src, uint16_t *p_dst, int w, int h, int sw_strd, int sh_strd,
    int dw_strd, int dh_strd, int src_fmt, bool keep_alpha, int dither)
{
    assert(p_src && p_dst && p_src != (uint8_t *)p_dst);
    assert(dw_strd >= w * 2);

    // src format info
    const int bpp = common_verify_imgfmt_bpp(src_fmt);
    const float ratio = common_verify_imgfmt_framesize_ratio(src_fmt);
    // const int frame_size = (w * h * bpp + 7) / 8;
    const int frame_size = sw_strd * sh_strd * ratio;
    LOGD_f("src fmt: %#x(%s), bpp: %d, frame_size: %d, plane_size_ratio: %.1f, ditherType: %d\n", src_fmt,
        common_verify_imgfmt_name(src_fmt), bpp, frame_size, ratio, dither);
    LOGD_f("src_stride: %dx%d, dst_stride: %dx%d\n", sw_strd, sh_strd, dw_strd, dh_strd);

    int chnl_num = 3;
    const int src_base_fmt = src_fmt & 0xF;
    const int chroma_hgt = src_base_fmt == YUV400 ? 0 : (src_base_fmt >= YUV420P ? h / 2 : h);
    const int chroma_wid = src_base_fmt == YUV400 ? 0 : (src_base_fmt >= YUV422P ? w / 2 : w);
    const int dhc_strd = src_base_fmt == YUV400 ? 0 : (src_base_fmt >= YUV420P ? dh_strd / 2 : dh_strd);
    const int dwc_strd = src_base_fmt == YUV400 ? 0 : (src_base_fmt >= YUV422P ? dw_strd / 2 : dw_strd);
    const int swc_strd = src_base_fmt == YUV400 ? 0 : (src_base_fmt >= YUV422P ? sw_strd / 2 : sw_strd);
    const int shc_strd = src_base_fmt == YUV400 ? 0 : (src_base_fmt >= YUV420P ? sh_strd / 2 : sh_strd);

    // dst planar addrs
    ushort *p_dst_yr = (ushort *)p_dst;
    ushort *p_dst_ug = (ushort *)((uint8_t *)p_dst + dw_strd * dh_strd);
    ushort *p_dst_vb = (ushort *)((uint8_t *)p_dst_ug + dwc_strd * dhc_strd);
    ushort *p_dst_a = keep_alpha ? (ushort *)((uint8_t *)p_dst_vb + dwc_strd * dhc_strd) : NULL;
    LOGT_f("dst u/v offset: %td / %td\n", (uint8_t *)p_dst_ug - (uint8_t *)p_dst_yr, (uint8_t *)p_dst_vb - (uint8_t *)p_dst_yr);

    switch (src_fmt) {
    /* 8bit normal data to 10bit planar lsb data */
    case RGBA8888: chnl_num = 4; // NO break here!
    case RGB888:   {
        assert(sw_strd >= w * chnl_num);
        for (int y = 0; y < h; y++) {
            for (int x = 0; x < w; x++) {
                const int src_ofs = y * sw_strd + x * chnl_num;
                const int dst_ofs = y * dw_strd / 2 + x;
                int r = p_src[src_ofs + 0];
                int g = p_src[src_ofs + 1];
                int b = p_src[src_ofs + 2];
                if (DITHER_SCALE == dither) {
                    p_dst_yr[dst_ofs] = ROUND_S32(r / 255.f * 1023.f);
                    p_dst_ug[dst_ofs] = ROUND_S32(g / 255.f * 1023.f);
                    p_dst_vb[dst_ofs] = ROUND_S32(b / 255.f * 1023.f);
                }
                else if (DITHER_FILL_MSB == dither) {
                    p_dst_yr[dst_ofs] = (r << 2) | (r >> 6);
                    p_dst_ug[dst_ofs] = (g << 2) + (g >> 6);
                    p_dst_vb[dst_ofs] = (b << 2) + (b >> 6);
                }
                else {
                    p_dst_yr[dst_ofs] = r << 2;
                    p_dst_ug[dst_ofs] = g << 2;
                    p_dst_vb[dst_ofs] = b << 2;
                }
                // ignore alpha channel here
            }
        }
    } break;
    case YUV444I: {
        assert(sw_strd >= w * chnl_num);
        for (int y = 0; y < h; y++) {
            for (int x = 0; x < w; x++) {
                const int src_ofs = y * sw_strd + x * chnl_num;
                const int dst_ofs = y * dw_strd / 2 + x;
                int y = p_src[src_ofs + 0];
                int cb = p_src[src_ofs + 1] - 128;
                int cr = p_src[src_ofs + 2] - 128;
                if (DITHER_SCALE == dither) {
                    p_dst_yr[dst_ofs] = ROUND_S32(y / 255.f * 1023.f);
                    p_dst_ug[dst_ofs] = ROUND_S32(cb / 255.f * 1023.f + 512);
                    p_dst_vb[dst_ofs] = ROUND_S32(cr / 255.f * 1023.f + 512);
                }
                else if (DITHER_FILL_MSB == dither) {
                    p_dst_yr[dst_ofs] = (y << 2) | (y >> 6);
                    p_dst_ug[dst_ofs] = (cb << 2) + (cb >> 6) + 512;
                    p_dst_vb[dst_ofs] = (cr << 2) + (cr >> 6) + 512;
                }
                else {
                    p_dst_yr[dst_ofs] = y << 2;
                    p_dst_ug[dst_ofs] = (cb << 2) + 512;
                    p_dst_vb[dst_ofs] = (cr << 2) + 512;
                }
                // ignore alpha channel here
            }
        }
    } break;
    case RGB_PLANAR: {
        assert(sw_strd >= w * 1);
        const uchar *p_src_yr = p_src;
        const uchar *p_src_ug = p_src + sw_strd * sh_strd;
        const uchar *p_src_vb = p_src + sw_strd * sh_strd * 2;
        for (int y = 0; y < h; y++) {
            for (int x = 0; x < w; x++) {
                const int src_ofs = y * sw_strd + x;
                const int dst_ofs = y * dw_strd / 2 + x;
                int r = p_src_yr[src_ofs];
                int g = p_src_ug[src_ofs];
                int b = p_src_vb[src_ofs];
                if (DITHER_SCALE == dither) {
                    p_dst_yr[dst_ofs] = ROUND_S32(r / 255.f * 1023.f);
                    p_dst_ug[dst_ofs] = ROUND_S32(g / 255.f * 1023.f);
                    p_dst_vb[dst_ofs] = ROUND_S32(b / 255.f * 1023.f);
                }
                else if (DITHER_FILL_MSB == dither) {
                    p_dst_yr[dst_ofs] = (r << 2) | (r >> 6);
                    p_dst_ug[dst_ofs] = (g << 2) + (g >> 6);
                    p_dst_vb[dst_ofs] = (b << 2) + (b >> 6);
                }
                else {
                    p_dst_yr[dst_ofs] = r << 2;
                    p_dst_ug[dst_ofs] = g << 2;
                    p_dst_vb[dst_ofs] = b << 2;
                }
            }
        }
    } break;
    case YUV444P: {
        assert(sw_strd >= w * 1);
        const uchar *p_src_yr = p_src;
        const uchar *p_src_ug = p_src + sw_strd * sh_strd;
        const uchar *p_src_vb = p_src + sw_strd * sh_strd * 2;
        for (int y = 0; y < h; y++) {
            for (int x = 0; x < w; x++) {
                const int src_ofs = y * sw_strd + x;
                const int dst_ofs = y * dw_strd / 2 + x;
                int y = p_src_yr[src_ofs];
                int cb = p_src_ug[src_ofs] - 128;
                int cr = p_src_vb[src_ofs] - 128;
                if (DITHER_SCALE == dither) {
                    p_dst_yr[dst_ofs] = ROUND_S32(y / 255.f * 1023.f);
                    p_dst_ug[dst_ofs] = ROUND_S32(cb / 255.f * 1023.f + 512);
                    p_dst_vb[dst_ofs] = ROUND_S32(cr / 255.f * 1023.f + 512);
                }
                else if (DITHER_FILL_MSB == dither) {
                    p_dst_yr[dst_ofs] = (y << 2) | (y >> 6);
                    p_dst_ug[dst_ofs] = (cb << 2) + (cb >> 6) + 512;
                    p_dst_vb[dst_ofs] = (cr << 2) + (cr >> 6) + 512;
                }
                else {
                    p_dst_yr[dst_ofs] = y << 2;
                    p_dst_ug[dst_ofs] = (cb << 2) + 512;
                    p_dst_vb[dst_ofs] = (cr << 2) + 512;
                }
            }
        }
    } break;
    case YUV422P:
    case YUV420P:
    case YUV400:  {
        assert(sw_strd >= w * 1);
        const uchar *p_src_y = p_src;
        const uchar *p_src_u = p_src_y + sw_strd * sh_strd;
        const uchar *p_src_v = p_src_u + swc_strd / 2 * shc_strd;
        for (int y = 0; y < h; y++) {
            for (int x = 0; x < w; x++) {
                const int src_ofs_y = y * sw_strd + x;
                const int dst_ofs_y = y * dw_strd / 2 + x;
                int y = p_src_y[src_ofs_y];
                if (DITHER_SCALE == dither)
                    p_dst_yr[dst_ofs_y] = ROUND_S32(y / 255.f * 1023.f);
                else if (DITHER_FILL_MSB == dither)
                    p_dst_yr[dst_ofs_y] = (y << 2) | (y >> 6);
                else
                    p_dst_yr[dst_ofs_y] = y << 2;
            }
        }
        for (int y = 0; y < chroma_hgt; y++) {
            for (int x = 0; x < chroma_wid; x++) {
                const int src_ofs_c = y * swc_strd + x;
                const int dst_ofs_c = y * dwc_strd / 2 + x;
                int cb = p_src_u[src_ofs_c] - 128;
                int cr = p_src_v[src_ofs_c] - 128;
                if (DITHER_SCALE == dither) {
                    p_dst_ug[dst_ofs_c] = ROUND_S32(cb / 255.f * 1023.f + 512);
                    p_dst_vb[dst_ofs_c] = ROUND_S32(cr / 255.f * 1023.f + 512);
                }
                else if (DITHER_FILL_MSB == dither) {
                    p_dst_ug[dst_ofs_c] = (cb << 2) + (cb >> 6) + 512;
                    p_dst_vb[dst_ofs_c] = (cr << 2) + (cr >> 6) + 512;
                }
                else {
                    p_dst_ug[dst_ofs_c] = (cb << 2) + 512;
                    p_dst_vb[dst_ofs_c] = (cr << 2) + 512;
                }
            }
        }
    } break;
    case YUV444SP: {
        assert(sw_strd >= w * 1);
        const uchar *p_src_y = p_src;
        const uchar *p_src_c = p_src + sw_strd * sh_strd;
        for (int y = 0; y < h; y++) {
            for (int x = 0; x < w; x++) {
                const int src_ofs_y = y * sw_strd + x;
                const int src_ofs_c = y * sw_strd * 2 + x * 2;
                const int dst_ofs = y * dw_strd / 2 + x;
                int y = p_src_y[src_ofs_y];
                int cb = p_src_c[src_ofs_c + 0] - 128;
                int cr = p_src_c[src_ofs_c + 1] - 128;
                if (DITHER_SCALE == dither) {
                    p_dst_yr[dst_ofs] = ROUND_S32(y / 255.f * 1023.f);
                    p_dst_ug[dst_ofs] = ROUND_S32(cb / 255.f * 1023.f + 512);
                    p_dst_vb[dst_ofs] = ROUND_S32(cr / 255.f * 1023.f + 512);
                }
                else if (DITHER_FILL_MSB == dither) {
                    p_dst_yr[dst_ofs] = (y << 2) | (y >> 6);
                    p_dst_ug[dst_ofs] = (cb << 2) + (cb >> 6) + 512;
                    p_dst_vb[dst_ofs] = (cr << 2) + (cr >> 6) + 512;
                }
                else {
                    p_dst_yr[dst_ofs] = y << 2;
                    p_dst_ug[dst_ofs] = (cb << 2) + 512;
                    p_dst_vb[dst_ofs] = (cr << 2) + 512;
                }
            }
        }
    } break;
    case YUV422SP:
    case YUV420SP: {
        assert(sw_strd >= w * 1);
        const uchar *p_src_y = p_src;
        const uchar *p_src_c = p_src + sw_strd * sh_strd;
        for (int y = 0; y < h; y++) {
            for (int x = 0; x < w; x++) {
                const int src_ofs_y = y * sw_strd + x;
                const int dst_ofs_y = y * dw_strd / 2 + x;
                if (DITHER_SCALE == dither)
                    p_dst_yr[dst_ofs_y] = ROUND_S32(p_src_y[src_ofs_y] / 255.f * 1023.f);
                else if (DITHER_FILL_MSB == dither)
                    p_dst_yr[dst_ofs_y] = (p_src_y[src_ofs_y] >> 6) | (p_src_y[src_ofs_y] << 2);
                else
                    p_dst_yr[dst_ofs_y] = p_src_y[src_ofs_y] << 2;
            }
        }
        for (int y = 0; y < chroma_hgt; y++) {
            for (int x = 0; x < chroma_wid; x++) {
                const int src_ofs_c = y * sw_strd + x * 2;
                const int dst_ofs_c = y * dw_strd / 4 + x;
                int cb = p_src_c[src_ofs_c + 0] - 128;
                int cr = p_src_c[src_ofs_c + 1] - 128;
                if (DITHER_SCALE == dither) {
                    p_dst_ug[dst_ofs_c] = ROUND_S32(cb / 225.f * 1023.f + 512);
                    p_dst_vb[dst_ofs_c] = ROUND_S32(cr / 225.f * 1023.f + 512);
                }
                else if (DITHER_FILL_MSB == dither) {
                    p_dst_ug[dst_ofs_c] = (cb << 2) + (cb >> 6) + 512;
                    p_dst_vb[dst_ofs_c] = (cr << 2) + (cr >> 6) + 512;
                }
                else {
                    p_dst_ug[dst_ofs_c] = (cb << 2) + 512;
                    p_dst_vb[dst_ofs_c] = (cr << 2) + 512;
                }
            }
        }
    } break;

    /* 10bit lsb data to 10bit planar lsb data */
    case RGB_101010LSB:
    case YUV444I_10LSB: {
        assert(sw_strd >= w * 3 * 2);
        for (int y = 0; y < h; y++) {
            const ushort *p_src_row = (ushort *)((uint8_t *)p_src + y * sw_strd);
            for (int x = 0, j = 0; x < w; x++, j += 3) {
                const int dst_ofs = y * dw_strd / 2 + x;
                p_dst_yr[dst_ofs] = p_src_row[j + 0] & 0x3ff;
                p_dst_ug[dst_ofs] = p_src_row[j + 1] & 0x3ff;
                p_dst_vb[dst_ofs] = p_src_row[j + 2] & 0x3ff;
            }
        }
    } break;
    case RGB_PLANAR10LSB:
    case YUV400_10LSB:
    case YUV444P_10LSB:
    case YUV422P_10LSB:
    case YUV420P_10LSB:   {
        assert(sw_strd >= w * 2);
        assert(sw_strd == dw_strd);
        // todo: support different stride
        memcpy(p_dst, p_src, frame_size);
    } break;
    case YUV444SP_10LSB: {
        assert(sw_strd >= w * 2);
        const ushort *p_src_y = (ushort *)p_src;
        const ushort *p_src_c = (ushort *)((uint8_t *)p_src + sh_strd * sw_strd);
        for (int y = 0; y < h; y++) {
            for (int x = 0, j = 0; x < w; x++, j += 2) {
                const int src_ofs_y = y * sw_strd / 2 + x;
                const int src_ofs_c = y * sw_strd + j;
                const int dst_ofs = y * dw_strd / 2 + x;
                p_dst_yr[dst_ofs] = p_src_y[src_ofs_y] & 0x3ff;
                p_dst_ug[dst_ofs] = p_src_c[src_ofs_c + 0] & 0x3ff;
                p_dst_vb[dst_ofs] = p_src_c[src_ofs_c + 1] & 0x3ff;
            }
        }
    } break;
    case YUV422SP_10LSB: {
        assert(sw_strd >= w * 2);
        const ushort *p_src_y = (ushort *)p_src;
        const ushort *p_src_c = (ushort *)((uint8_t *)p_src + sh_strd * sw_strd);
        for (int y = 0; y < h; y++) {
            for (int x = 0; x < w; x++) {
                const int src_ofs = y * sw_strd / 2 + x;
                const int dst_ofs = y * dw_strd / 2 + x;
                p_dst_yr[dst_ofs] = p_src_y[src_ofs] & 0x3ff;
            }
            for (int x = 0, j = 0; x < w / 2; x++, j += 2) {
                const int src_ofs = y * sw_strd / 2 + j;
                const int dst_ofs = y * dw_strd / 4 + x;
                p_dst_ug[dst_ofs] = p_src_c[src_ofs + 0] & 0x3ff;
                p_dst_vb[dst_ofs] = p_src_c[src_ofs + 1] & 0x3ff;
            }
        }
    } break;
    case YUV420SP_10LSB: {
        assert(sw_strd >= w * 2);
        const ushort *p_src_y = (ushort *)p_src;
        const ushort *p_src_c = (ushort *)((uint8_t *)p_src + sh_strd * sw_strd);
        for (int y = 0; y < h; y++) {
            for (int x = 0; x < w; x++) {
                const int src_ofs = y * sw_strd / 2 + x;
                const int dst_ofs = y * dw_strd / 2 + x;
                p_dst_yr[dst_ofs] = p_src_y[src_ofs] & 0x3ff;
            }
        }
        for (int y = 0; y < h / 2; y++) {
            for (int x = 0, j = 0; x < w / 2; x++, j += 2) {
                const int src_ofs = y * sw_strd / 2 + j;
                const int dst_ofs = y * dw_strd / 4 + x;
                p_dst_ug[dst_ofs] = p_src_c[src_ofs + 0] & 0x3ff;
                p_dst_vb[dst_ofs] = p_src_c[src_ofs + 1] & 0x3ff;
            }
        }
    } break;

    /* 10bit packed data to 10bit planar lsb data */
    case RGB_10PACKED:
    case YUV444I_10PACKED: {
        assert(w % 4 == 0); // must align with 4 pixels
        assert(sw_strd >= w * 3 * 5 / 4);
        ushort unpack_data[4] = {0};
        for (int y = 0; y < h; y++) {
            // 4 pixel per iteration, unpack 15xU8 data to 12xU10 data
            for (int x = 0, j = 0; x <= w - 4; x += 4, j += 15) {
                const int dst_ofs = y * dw_strd / 2 + x;
                const int src_ofs = y * sw_strd + j;
                unpack_data_10bit(p_src + src_ofs, unpack_data);
                p_dst_yr[dst_ofs + 0] = unpack_data[0];
                p_dst_ug[dst_ofs + 0] = unpack_data[1];
                p_dst_vb[dst_ofs + 0] = unpack_data[2];
                p_dst_yr[dst_ofs + 1] = unpack_data[3];
                unpack_data_10bit(p_src + src_ofs + 5, unpack_data);
                p_dst_ug[dst_ofs + 1] = unpack_data[0];
                p_dst_vb[dst_ofs + 1] = unpack_data[1];
                p_dst_yr[dst_ofs + 2] = unpack_data[2];
                p_dst_ug[dst_ofs + 2] = unpack_data[3];
                unpack_data_10bit(p_src + src_ofs + 10, unpack_data);
                p_dst_vb[dst_ofs + 2] = unpack_data[0];
                p_dst_yr[dst_ofs + 3] = unpack_data[1];
                p_dst_ug[dst_ofs + 3] = unpack_data[2];
                p_dst_vb[dst_ofs + 3] = unpack_data[3];
            }
        }
    } break;
    case RGBA_1010102: {
        assert(w % 4 == 0); // must align with 4 pixels
        assert(sw_strd >= w * 4);
        for (int y = 0; y < h; y++) {
            uint *p_src_row = (uint *)((uint8_t *)p_src + y * sw_strd);
            for (int x = 0; x < w; x++) {
                const int dst_ofs = y * dw_strd / 2 + x;
                const uint rgba = p_src_row[x];
                p_dst_yr[dst_ofs] = (rgba >> 0) & 0x3ff;
                p_dst_ug[dst_ofs] = (rgba >> 10) & 0x3ff;
                p_dst_vb[dst_ofs] = (rgba >> 20) & 0x3ff;
                if (keep_alpha) {
                    p_dst_a[dst_ofs] = (rgba >> 30) << 8; // to 10bit alpha
                }
                // unpack_data_1010102(rgba, )
            }
        }
    } break;
    case RGB_PLANAR10PACKED:
    case YUV444P_10PACKED:   {
        assert(w % 4 == 0); // must align with 4 pixels
        assert(sw_strd >= w * 5 / 4);
        for (int y = 0; y < h; y++) {
            // 4 pixel per iteration, unpack 5xU8 data to 4xU10 data
            uchar *p_src_yr = (uchar *)p_src;
            uchar *p_src_ug = (uchar *)p_src + sw_strd * sh_strd;
            uchar *p_src_vb = (uchar *)p_src + sw_strd * sh_strd * 2;
            for (int x = 0, j = 0; x <= w - 4; x += 4, j += 5) {
                const int src_ofs = y * sw_strd + j;
                const int dst_ofs = y * dw_strd / 2 + x;
                unpack_data_10bit(p_src_yr + src_ofs, p_dst_yr + dst_ofs);
                unpack_data_10bit(p_src_ug + src_ofs, p_dst_ug + dst_ofs);
                unpack_data_10bit(p_src_vb + src_ofs, p_dst_vb + dst_ofs);
            }
        }
    } break;
    case YUV422P_10PACKED:
    case YUV420P_10PACKED:
    case YUV400_10PACKED:  {
        assert(w % 4 == 0);
        assert(sw_strd >= w * 5 / 4);
        uchar *p_src_y = (uchar *)p_src;
        uchar *p_src_u = (uchar *)p_src_y + sw_strd * sh_strd;
        uchar *p_src_v = (uchar *)p_src_u + swc_strd / 2 * shc_strd;
        for (int y = 0; y < h; y++) {
            for (int x = 0, j = 0; x <= w - 4; x += 4, j += 5) {
                const int src_ofs = y * sw_strd + j;
                const int dst_ofs = y * dw_strd / 2 + x;
                unpack_data_10bit(p_src_y + src_ofs, p_dst_yr + dst_ofs);
            }
        }
        for (int y = 0; y < chroma_hgt; y++) {
            for (int x = 0, j = 0; x <= chroma_wid - 2; x += 2, j += 5) {
                const int src_ofs = y * swc_strd + j;
                const int dst_ofs = y * dwc_strd / 2 + x;
                unpack_data_10bit(p_src_u + src_ofs, p_dst_ug + dst_ofs);
                unpack_data_10bit(p_src_v + src_ofs, p_dst_vb + dst_ofs);
            }
        }
    } break;
    case YUV444SP_10PACKED: {
        assert(w % 4 == 0); // must align with 4 pixels
        assert(sw_strd >= w * 5 / 4);
        ushort unpack_data[4] = {0};
        for (int y = 0; y < h; y++) {
            uchar *p_src_y = (uchar *)p_src;
            uchar *p_src_c = (uchar *)p_src + sw_strd * sh_strd;
            for (int x = 0, j = 0; x <= w - 4; x += 4, j += 5) {
                const int src_ofs_y = y * sw_strd + j;
                const int src_ofs_c = y * sw_strd * 2 + j * 2;
                const int dst_ofs = y * dw_strd / 2 + x;
                unpack_data_10bit(p_src_y + src_ofs_y, p_dst_yr + dst_ofs);
                unpack_data_10bit(p_src_c + src_ofs_c, unpack_data);
                p_dst_ug[dst_ofs + 0] = unpack_data[0];
                p_dst_vb[dst_ofs + 0] = unpack_data[1];
                p_dst_ug[dst_ofs + 1] = unpack_data[2];
                p_dst_vb[dst_ofs + 1] = unpack_data[3];
                unpack_data_10bit(p_src_c + src_ofs_c + 5, unpack_data);
                p_dst_ug[dst_ofs + 2] = unpack_data[0];
                p_dst_vb[dst_ofs + 2] = unpack_data[1];
                p_dst_ug[dst_ofs + 3] = unpack_data[2];
                p_dst_vb[dst_ofs + 3] = unpack_data[3];
            }
        }
    } break;
    case YUV422SP_10PACKED: {
        assert(w % 4 == 0); // must align with 4 pixels
        assert(sw_strd >= w * 5 / 4);
        const uchar *p_src_y = (uchar *)p_src;
        const uchar *p_src_c = (uchar *)p_src + sw_strd * sh_strd;
        ushort unpack_data[4] = {0};
        for (int y = 0; y < h; y++) {
            for (int x = 0, j = 0; x <= w - 4; x += 4, j += 5) {
                const int src_ofs_y = y * sw_strd + j;
                const int dst_ofs_y = y * dw_strd / 2 + x;
                unpack_data_10bit(p_src_y + src_ofs_y, p_dst_yr + dst_ofs_y);
            }
            for (int x = 0, j = 0; x <= w / 2 - 2; x += 2, j += 5) {
                const int src_ofs_c = y * sw_strd + j;
                const int dst_ofs_c = y * dw_strd / 4 + x;
                unpack_data_10bit(p_src_c + src_ofs_c, unpack_data);
                p_dst_ug[dst_ofs_c + 0] = unpack_data[0];
                p_dst_vb[dst_ofs_c + 0] = unpack_data[1];
                p_dst_ug[dst_ofs_c + 1] = unpack_data[2];
                p_dst_vb[dst_ofs_c + 1] = unpack_data[3];
            }
        }
    } break;
    case YUV420SP_10PACKED: {
        assert(w % 4 == 0); // must align with 4 pixels
        assert(sw_strd >= w * 5 / 4);
        const uchar *p_src_y = (uchar *)p_src;
        const uchar *p_src_c = (uchar *)p_src + sw_strd * sh_strd;
        ushort unpack_data[4] = {0};
        for (int y = 0; y < h; y++) {
            uchar *p_src_y = (uchar *)p_src;
            for (int x = 0, j = 0; x <= w - 4; x += 4, j += 5) {
                const int src_ofs_y = y * sw_strd + j;
                const int dst_ofs_y = y * dw_strd / 2 + x;
                unpack_data_10bit(p_src_y + src_ofs_y, p_dst_yr + dst_ofs_y);
            }
        }
        for (int y = 0; y < h / 2; y++) {
            uchar *p_src_c = (uchar *)p_src + sw_strd * sh_strd;
            for (int x = 0, j = 0; x <= w / 2 - 2; x += 2, j += 5) {
                const int src_ofs_c = y * sw_strd + j;
                const int dst_ofs_c = y * dw_strd / 4 + x;
                unpack_data_10bit(p_src_c + src_ofs_c, unpack_data);
                p_dst_ug[dst_ofs_c + 0] = unpack_data[0];
                p_dst_vb[dst_ofs_c + 0] = unpack_data[1];
                p_dst_ug[dst_ofs_c + 1] = unpack_data[2];
                p_dst_vb[dst_ofs_c + 1] = unpack_data[3];
            }
        }
    } break;

    case YUV420SP_TILE4X4: {
        assert(w % 4 == 0 && h % 4 == 0);
        const int tile_w = w / 4;
        const int tile_h = h / 4;

        for (int ty = 0; ty < tile_h; ty++) {
            for (int tx = 0; tx < tile_w; tx++) {
                const int tile_idx = ty * tile_w + tx;
                const int src_tile_offset = tile_idx * 24;

                const uchar *p_src_tile_y = p_src + src_tile_offset;
                const uchar *p_src_tile_uv = p_src_tile_y + 16;

                for (int row = 0; row < 4; row++) {
                    const int y = ty * 4 + row;
                    for (int col = 0; col < 4; col++) {
                        const int x = tx * 4 + col;
                        const int src_ofs = row * 4 + col;
                        const int dst_ofs = y * dw_strd / 2 + x;
                        int y_val = p_src_tile_y[src_ofs];
                        if (DITHER_SCALE == dither)
                            p_dst_yr[dst_ofs] = ROUND_S32(y_val / 255.f * 1023.f);
                        else if (DITHER_FILL_MSB == dither)
                            p_dst_yr[dst_ofs] = (y_val << 2) | (y_val >> 6);
                        else
                            p_dst_yr[dst_ofs] = y_val << 2;
                    }
                }

                for (int row = 0; row < 2; row++) {
                    for (int col = 0; col < 2; col++) {
                        const int y = ty * 2 + row;
                        const int x = tx * 2 + col;
                        const int src_ofs = row * 4 + col * 2;
                        const int dst_ofs = y * dw_strd / 4 + x;
                        int u_val = p_src_tile_uv[src_ofs + 0] - 128;
                        int v_val = p_src_tile_uv[src_ofs + 1] - 128;
                        if (DITHER_SCALE == dither) {
                            p_dst_ug[dst_ofs] = ROUND_S32(u_val / 255.f * 1023.f + 512);
                            p_dst_vb[dst_ofs] = ROUND_S32(v_val / 255.f * 1023.f + 512);
                        }
                        else if (DITHER_FILL_MSB == dither) {
                            p_dst_ug[dst_ofs] = (u_val << 2) + (u_val >> 6) + 512;
                            p_dst_vb[dst_ofs] = (v_val << 2) + (v_val >> 6) + 512;
                        }
                        else {
                            p_dst_ug[dst_ofs] = (u_val << 2) + 512;
                            p_dst_vb[dst_ofs] = (v_val << 2) + 512;
                        }
                    }
                }
            }
        }
    } break;
    case YUV422SP_TILE4X4: {
        assert(w % 4 == 0 && h % 4 == 0);
        const int tile_w = w / 4;
        const int tile_h = h / 4;

        for (int ty = 0; ty < tile_h; ty++) {
            for (int tx = 0; tx < tile_w; tx++) {
                const int tile_idx = ty * tile_w + tx;
                const int src_tile_offset = tile_idx * 32;

                const uchar *p_src_tile_y = p_src + src_tile_offset;
                const uchar *p_src_tile_uv = p_src_tile_y + 16;

                for (int row = 0; row < 4; row++) {
                    const int y = ty * 4 + row;
                    for (int col = 0; col < 4; col++) {
                        const int x = tx * 4 + col;
                        const int src_ofs = row * 4 + col;
                        const int dst_ofs = y * dw_strd / 2 + x;
                        int y_val = p_src_tile_y[src_ofs];
                        if (DITHER_SCALE == dither)
                            p_dst_yr[dst_ofs] = ROUND_S32(y_val / 255.f * 1023.f);
                        else if (DITHER_FILL_MSB == dither)
                            p_dst_yr[dst_ofs] = (y_val << 2) | (y_val >> 6);
                        else
                            p_dst_yr[dst_ofs] = y_val << 2;
                    }
                }

                for (int row = 0; row < 4; row++) {
                    for (int col = 0; col < 4; col++) {
                        const int y = ty * 4 + row;
                        const int x = tx * 4 + col;
                        const int src_ofs = row * 4 + col;
                        const int dst_ofs = y * dw_strd / 2 + x;
                        int u_val = p_src_tile_uv[src_ofs * 2 + 0] - 128;
                        int v_val = p_src_tile_uv[src_ofs * 2 + 1] - 128;
                        if (DITHER_SCALE == dither) {
                            p_dst_ug[dst_ofs] = ROUND_S32(u_val / 255.f * 1023.f + 512);
                            p_dst_vb[dst_ofs] = ROUND_S32(v_val / 255.f * 1023.f + 512);
                        }
                        else if (DITHER_FILL_MSB == dither) {
                            p_dst_ug[dst_ofs] = (u_val << 2) + (u_val >> 6) + 512;
                            p_dst_vb[dst_ofs] = (v_val << 2) + (v_val >> 6) + 512;
                        }
                        else {
                            p_dst_ug[dst_ofs] = (u_val << 2) + 512;
                            p_dst_vb[dst_ofs] = (v_val << 2) + 512;
                        }
                    }
                }
            }
        }
    } break;
    case YUV444SP_TILE4X4: {
        assert(w % 4 == 0 && h % 4 == 0);
        const int tile_w = w / 4;
        const int tile_h = h / 4;

        for (int ty = 0; ty < tile_h; ty++) {
            for (int tx = 0; tx < tile_w; tx++) {
                const int tile_idx = ty * tile_w + tx;
                const int src_tile_offset = tile_idx * 48;

                const uchar *p_src_tile_y = p_src + src_tile_offset;
                const uchar *p_src_tile_uv = p_src_tile_y + 16;

                for (int row = 0; row < 4; row++) {
                    const int y = ty * 4 + row;
                    for (int col = 0; col < 4; col++) {
                        const int x = tx * 4 + col;
                        const int src_ofs = row * 4 + col;
                        const int dst_ofs = y * dw_strd / 2 + x;
                        int y_val = p_src_tile_y[src_ofs];
                        if (DITHER_SCALE == dither)
                            p_dst_yr[dst_ofs] = ROUND_S32(y_val / 255.f * 1023.f);
                        else if (DITHER_FILL_MSB == dither)
                            p_dst_yr[dst_ofs] = (y_val << 2) | (y_val >> 6);
                        else
                            p_dst_yr[dst_ofs] = y_val << 2;
                    }
                }

                for (int row = 0; row < 4; row++) {
                    for (int col = 0; col < 4; col++) {
                        const int y = ty * 4 + row;
                        const int x = tx * 4 + col;
                        const int src_ofs = row * 4 + col;
                        const int dst_ofs = y * dw_strd / 2 + x;
                        int u_val = p_src_tile_uv[src_ofs * 2 + 0] - 128;
                        int v_val = p_src_tile_uv[src_ofs * 2 + 1] - 128;
                        if (DITHER_SCALE == dither) {
                            p_dst_ug[dst_ofs] = ROUND_S32(u_val / 255.f * 1023.f + 512);
                            p_dst_vb[dst_ofs] = ROUND_S32(v_val / 255.f * 1023.f + 512);
                        }
                        else if (DITHER_FILL_MSB == dither) {
                            p_dst_ug[dst_ofs] = (u_val << 2) + (u_val >> 6) + 512;
                            p_dst_vb[dst_ofs] = (v_val << 2) + (v_val >> 6) + 512;
                        }
                        else {
                            p_dst_ug[dst_ofs] = (u_val << 2) + 512;
                            p_dst_vb[dst_ofs] = (v_val << 2) + 512;
                        }
                    }
                }
            }
        }
    } break;
    default: LOGE_f("unsupported image format %#x for now!\n", src_fmt); return -1;
    }

    return 0;
}

int imgcvt_from_planar_10bit_lsb(uint16_t const *p_src, uint8_t *p_dst, int w, int h, int sw_strd, int sh_strd,
    int dw_strd, int dh_strd, int dst_fmt, bool has_alpha, int dither)
{
    assert(p_src && p_dst && (uint8_t *)p_src != p_dst);
    assert(sw_strd >= w * 2);

    // dst format info
    const int bpp = common_verify_imgfmt_bpp(dst_fmt);
    // const int frame_size = (w * h * bpp + 7) / 8;
    const int frame_size = dw_strd * dh_strd * common_verify_imgfmt_framesize_ratio(dst_fmt);
    LOGD_f("dst fmt: %#x(%s), bpp: %d, frame_size: %d, ditherType: %d\n", dst_fmt, common_verify_imgfmt_name(dst_fmt),
        bpp, frame_size, dither);
    LOGD_f("src_stride: %dx%d, dst_stride: %dx%d\n", sw_strd, sh_strd, dw_strd, dh_strd);

    const int dst_base_fmt = dst_fmt & 0xF;
    const int chroma_hgt = dst_base_fmt == YUV400 ? 0 : (dst_base_fmt >= YUV420P ? h / 2 : h);
    const int chroma_wid = dst_base_fmt == YUV400 ? 0 : (dst_base_fmt >= YUV422P ? w / 2 : w);
    const int shc_strd = dst_base_fmt == YUV400 ? 0 : (dst_base_fmt >= YUV420P ? sh_strd / 2 : sh_strd);
    const int swc_strd = dst_base_fmt == YUV400 ? 0 : (dst_base_fmt >= YUV422P ? sw_strd / 2 : sw_strd);
    const int dhc_strd = dst_base_fmt == YUV400 ? 0 : (dst_base_fmt >= YUV420P ? dh_strd / 2 : dh_strd);
    const int dwc_strd = dst_base_fmt == YUV400 ? 0 : (dst_base_fmt >= YUV422P ? dw_strd / 2 : dw_strd);

    const ushort *p_src_yr = (ushort *)p_src;
    const ushort *p_src_ug = (ushort *)((uint8_t *)p_src + sw_strd * sh_strd);
    const ushort *p_src_vb = (ushort *)((uint8_t *)p_src_ug + swc_strd * shc_strd);
    const ushort *p_src_a = has_alpha ? (ushort *)((uint8_t *)p_src_vb + swc_strd * shc_strd) : NULL;
    LOGT_f("src u/v offset: %td / %td\n", (uint8_t *)p_src_ug - (uint8_t *)p_src_yr, (uint8_t *)p_src_vb - (uint8_t *)p_src_yr);

    switch (dst_fmt) {
    /* dither down to 8bit formats */
    case RGB888:
    case RGBA8888: {
        const int nb_comps = dst_fmt == RGBA8888 ? 4 : 3;
        assert(dw_strd >= w * nb_comps);
        for (int y = 0; y < h; y++) {
            uint8_t *p_dst_row = (uint8_t *)p_dst + y * dw_strd;
            for (int x = 0, j = 0; x < w; x++, j += nb_comps) {
                const int src_ofs = y * sw_strd / 2 + x;
                uint16_t yr = p_src_yr[src_ofs];
                uint16_t ug = p_src_ug[src_ofs];
                uint16_t vb = p_src_vb[src_ofs];
                uint16_t a = p_src_a ? p_src_a[src_ofs] : 1023;
                if (DITHER_SCALE == dither) {
                    p_dst_row[j + 0] = ROUND_S32(yr / 1023.f * 255.f);
                    p_dst_row[j + 1] = ROUND_S32(ug / 1023.f * 255.f);
                    p_dst_row[j + 2] = ROUND_S32(vb / 1023.f * 255.f);
                    if (nb_comps == 4)
                        p_dst_row[j + 3] = ROUND_S32(a / 1023.f * 255.f);
                }
                else {
                    p_dst_row[j + 0] = MIN((yr + 2) >> 2, 255);
                    p_dst_row[j + 1] = MIN((ug + 2) >> 2, 255);
                    p_dst_row[j + 2] = MIN((vb + 2) >> 2, 255);
                    if (nb_comps == 4)
                        p_dst_row[j + 3] =  MIN((a + 2) >> 2, 255);
                }
            }
        }
    } break;
    /* 10bit plannar to 10bit lsb data */
    case RGB_101010LSB:
    case YUV444I_10LSB: {
        assert(dw_strd >= w * 3 * 2);
        for (int y = 0; y < h; y++) {
            ushort *p_dst_row = (ushort *)((uint8_t *)p_dst + y * dw_strd);
            for (int x = 0, j = 0; x < w; x++, j += 3) {
                const int src_ofs = y * sw_strd / 2 + x;
                p_dst_row[j + 0] = p_src_yr[src_ofs];
                p_dst_row[j + 1] = p_src_ug[src_ofs];
                p_dst_row[j + 2] = p_src_vb[src_ofs];
            }
        }
    } break;
    case RGB_PLANAR10LSB:
    case YUV400_10LSB:
    case YUV444P_10LSB:
    case YUV422P_10LSB:
    case YUV420P_10LSB:   {
        assert(dw_strd >= w * 2);
        assert(sw_strd == dw_strd);
        ushort *p_dst_y = (ushort *)p_dst;
        ushort *p_dst_u = (ushort *)((uint8_t *)p_dst + dh_strd * dw_strd);
        ushort *p_dst_v = (ushort *)((uint8_t *)p_dst_u + dhc_strd * dwc_strd);
        LOGT_f("dst u/v offset: %td / %td\n", (uint8_t *)p_dst_u - (uint8_t *)p_dst_y, (uint8_t *)p_dst_v - (uint8_t *)p_dst_y);
        for (int y = 0; y < h; y++)
            memcpy((uint8_t *)p_dst_y + y * dw_strd, (uint8_t *)p_src_yr + sw_strd * y, MIN(dw_strd, sw_strd));
        for (int y = 0; y < chroma_hgt; y++) {
            memcpy((uint8_t *)p_dst_u + y * dwc_strd, (uint8_t *)p_src_ug + swc_strd * y, MIN(dwc_strd, swc_strd));
            memcpy((uint8_t *)p_dst_v + y * dwc_strd, (uint8_t *)p_src_vb + swc_strd * y, MIN(dwc_strd, swc_strd));
        }
    } break;
    case YUV444SP_10LSB: {
        assert(dw_strd >= w * 2);
        ushort *p_dst_y = (ushort *)p_dst;
        ushort *p_dst_c = (ushort *)((uint8_t *)p_dst + dh_strd * dw_strd);
        for (int y = 0; y < h; y++) {
            for (int x = 0, j = 0; x < w; x++, j += 2) {
                const int src_ofs = y * sw_strd / 2 + x;
                const int dst_ofs_y = y * dw_strd / 2 + x;
                const int dst_ofs_c = y * dw_strd + j;
                p_dst_y[dst_ofs_y] = p_src_yr[src_ofs];
                p_dst_c[dst_ofs_c + 0] = p_src_ug[src_ofs];
                p_dst_c[dst_ofs_c + 1] = p_src_vb[src_ofs];
            }
        }
    } break;
    case YUV422SP_10LSB: {
        assert(dw_strd >= w * 2);
        ushort *p_dst_y = (ushort *)p_dst;
        ushort *p_dst_c = (ushort *)((uint8_t *)p_dst + dh_strd * dw_strd);
        for (int y = 0; y < h; y++) {
            memcpy((uint8_t *)p_dst_y + y * dw_strd, (uint8_t *)p_src_yr + y * sw_strd, MIN(dw_strd, sw_strd));
            for (int x = 0, j = 0; x < chroma_wid; x++, j += 2) {
                const int src_ofs = y * sw_strd / 4 + x;
                const int dst_ofs = y * dw_strd / 2 + j;
                p_dst_c[dst_ofs + 0] = p_src_ug[src_ofs];
                p_dst_c[dst_ofs + 1] = p_src_vb[src_ofs];
            }
        }
    } break;
    case YUV420SP_10LSB: {
        assert(dw_strd >= w * 2);
        ushort *p_dst_y = (ushort *)p_dst;
        ushort *p_dst_c = (ushort *)((uint8_t *)p_dst + dh_strd * dw_strd);
        for (int y = 0; y < h; y++) {
            memcpy((uint8_t *)p_dst_y + y * dw_strd, (uint8_t *)p_src_yr + sw_strd * y, MIN(dw_strd, sw_strd));
        }
        for (int y = 0; y < chroma_hgt; y++) {
            for (int x = 0, j = 0; x < chroma_wid; x++, j += 2) {
                const int src_ofs = y * sw_strd / 4 + x;
                const int dst_ofs = y * dw_strd / 2 + j;
                p_dst_c[dst_ofs + 0] = p_src_ug[src_ofs];
                p_dst_c[dst_ofs + 1] = p_src_vb[src_ofs];
            }
        }
    } break;

    /* 10bit plannar to 10bit packed data */
    case RGB_10PACKED:
    case YUV444I_10PACKED: {
        assert(w % 4 == 0); // must align with 4 pixels
        assert(dw_strd >= w * 3 * 5 / 4);
        ushort unpack_data[4] = {0};
        for (int y = 0; y < h; y++) {
            // 4 pixel per iteration, pack 12xU10 data to 15xU8 data
            for (int x = 0, j = 0; x <= w - 4; x += 4, j += 15) {
                const int src_ofs = y * sw_strd / 2 + x;
                const int dst_ofs = y * dw_strd + j;
                unpack_data[0] = p_src_yr[src_ofs + 0] & 0x3ff;
                unpack_data[1] = p_src_ug[src_ofs + 0] & 0x3ff;
                unpack_data[2] = p_src_vb[src_ofs + 0] & 0x3ff;
                unpack_data[3] = p_src_yr[src_ofs + 1] & 0x3ff;
                pack_data_10bit(unpack_data, p_dst + dst_ofs);
                unpack_data[0] = p_src_ug[src_ofs + 1] & 0x3ff;
                unpack_data[1] = p_src_vb[src_ofs + 1] & 0x3ff;
                unpack_data[2] = p_src_yr[src_ofs + 2] & 0x3ff;
                unpack_data[3] = p_src_ug[src_ofs + 2] & 0x3ff;
                pack_data_10bit(unpack_data, p_dst + dst_ofs + 5);
                unpack_data[0] = p_src_vb[src_ofs + 2] & 0x3ff;
                unpack_data[1] = p_src_yr[src_ofs + 3] & 0x3ff;
                unpack_data[2] = p_src_ug[src_ofs + 3] & 0x3ff;
                unpack_data[3] = p_src_vb[src_ofs + 3] & 0x3ff;
                pack_data_10bit(unpack_data, p_dst + dst_ofs + 10);
            }
        }
    } break;
    case RGBA_1010102: {
        assert(w % 4 == 0); // must align with 4 pixels
        assert(dw_strd >= w * 4);
        ushort rgba[4] = {0};
        for (int y = 0; y < h; y++) {
            uint *p_dst_row = (uint *)((uint8_t *)p_dst + y * dw_strd);
            for (int x = 0; x < w; x++) {
                const int src_ofs = y * sw_strd / 2 + x;
                const int dst_ofs = y * dw_strd + x * 3;
                rgba[0] = p_src_yr[src_ofs] & 0x3ff;
                rgba[1] = p_src_ug[src_ofs] & 0x3ff;
                rgba[2] = p_src_vb[src_ofs] & 0x3ff;
                rgba[3] = has_alpha ? ((p_src_a[src_ofs] + 128) >> 8) : 0x3; // 2bit alpha
                p_dst_row[x] = rgba[0] | (rgba[1] << 10) | (rgba[2] << 20) | (rgba[3] << 30);
            }
        }
    } break;
    case RGB_PLANAR10PACKED:
    case YUV444P_10PACKED:   {
        assert(w % 4 == 0); // must align with 4 pixels
        assert(dw_strd >= w * 5 / 4);
        for (int y = 0; y < h; y++) {
            // 4 pixel per iteration, pack 4xU10 data to 5xU8 data
            uchar *p_dst_yr = (uchar *)p_dst;
            uchar *p_dst_ug = (uchar *)p_dst + dw_strd * dh_strd;
            uchar *p_dst_vb = (uchar *)p_dst + dw_strd * dh_strd * 2;
            for (int x = 0, j = 0; x <= w - 4; x += 4, j += 5) {
                const int src_ofs = y * sw_strd / 2 + x;
                const int dst_ofs = y * dw_strd + j;
                pack_data_10bit(p_src_yr + src_ofs, p_dst_yr + dst_ofs);
                pack_data_10bit(p_src_ug + src_ofs, p_dst_ug + dst_ofs);
                pack_data_10bit(p_src_vb + src_ofs, p_dst_vb + dst_ofs);
            }
        }
    } break;
    case YUV400_10PACKED:
    case YUV422P_10PACKED:
    case YUV420P_10PACKED: {
        assert(w % 4 == 0); // must align with 4 pixels
        assert(dw_strd >= w * 5 / 4);
        for (int y = 0; y < h; y++) {
            uchar *p_dst_yr = (uchar *)p_dst;
            for (int x = 0, j = 0; x <= w - 4; x += 4, j += 5) {
                const int src_ofs = y * sw_strd / 2 + x;
                const int dst_ofs = y * dw_strd + j;
                pack_data_10bit(p_src_yr + src_ofs, p_dst_yr + dst_ofs);
            }
        }
        for (int y = 0; y < chroma_hgt; y++) {
            uchar *p_dst_ug = (uchar *)p_dst + dw_strd * dh_strd;
            uchar *p_dst_vb = (uchar *)p_dst_ug + dwc_strd * dhc_strd;
            //   (YUV422P_10PACKED == dst_fmt ? dw_strd * dh_strd * 3 / 2 : dw_strd * dh_strd * 5 / 4);
            for (int x = 0, j = 0; x <= chroma_wid - 4; x += 4, j += 5) {
                const int src_ofs = y * sw_strd / 4 + x;
                const int dst_ofs = y * dw_strd / 2 + j;
                pack_data_10bit(p_src_ug + src_ofs, p_dst_ug + dst_ofs);
                pack_data_10bit(p_src_vb + src_ofs, p_dst_vb + dst_ofs);
            }
        }
    } break;
    case YUV444SP_10PACKED: {
        assert(w % 4 == 0); // must align with 4 pixels
        assert(dw_strd >= w * 5 / 4);
        ushort unpack_data[4] = {0};
        for (int y = 0; y < h; y++) {
            // 4 pixel per iteration, pack 4xU10 data to 5xU8 data
            uchar *p_dst_y = (uchar *)p_dst;
            uchar *p_dst_c = (uchar *)p_dst + dw_strd * dh_strd;
            for (int x = 0, j = 0; x <= w - 4; x += 4, j += 5) {
                const int src_ofs = y * sw_strd / 2 + x;
                const int dst_ofs_y = y * dw_strd + j;
                const int dst_ofs_c = y * dw_strd * 2 + j * 2;
                pack_data_10bit(p_src_yr + src_ofs, p_dst_y + dst_ofs_y);
                unpack_data[0] = p_src_ug[src_ofs + 0] & 0x3ff;
                unpack_data[1] = p_src_vb[src_ofs + 0] & 0x3ff;
                unpack_data[2] = p_src_ug[src_ofs + 1] & 0x3ff;
                unpack_data[3] = p_src_vb[src_ofs + 1] & 0x3ff;
                pack_data_10bit(unpack_data, p_dst_c + dst_ofs_c);
                unpack_data[0] = p_src_ug[src_ofs + 2] & 0x3ff;
                unpack_data[1] = p_src_vb[src_ofs + 2] & 0x3ff;
                unpack_data[2] = p_src_ug[src_ofs + 3] & 0x3ff;
                unpack_data[3] = p_src_vb[src_ofs + 3] & 0x3ff;
                pack_data_10bit(unpack_data, p_dst_c + dst_ofs_c + 5);
            }
        }
    } break;
    case YUV422SP_10PACKED: {
        assert(w % 4 == 0); // must align with 4 pixels
        assert(dw_strd >= w * 5 / 4);
        ushort unpack_data[4] = {0};
        for (int y = 0; y < h; y++) {
            // 4 pixel per iteration, pack 4xU10 data to 5xU8 data
            uchar *p_dst_y = (uchar *)p_dst;
            uchar *p_dst_c = (uchar *)p_dst + dw_strd * dh_strd;
            for (int x = 0, j = 0; x <= w - 4; x += 4, j += 5) {
                const int src_ofs = y * sw_strd / 2 + x;
                const int dst_ofs_y = y * dw_strd + j;
                const int dst_ofs_c = dst_ofs_y;
                pack_data_10bit(p_src_yr + src_ofs, p_dst_y + dst_ofs_y);
                unpack_data[0] = p_src_ug[src_ofs + 0] & 0x3ff;
                unpack_data[1] = p_src_vb[src_ofs + 0] & 0x3ff;
                unpack_data[2] = p_src_ug[src_ofs + 1] & 0x3ff;
                unpack_data[3] = p_src_vb[src_ofs + 1] & 0x3ff;
                pack_data_10bit(unpack_data, p_dst_c + dst_ofs_c);
            }
        }
    } break;
    case YUV420SP_10PACKED: {
        assert(w % 4 == 0); // must align with 4 pixels
        assert(dw_strd >= w * 5 / 4);
        ushort unpack_data[4] = {0};
        for (int y = 0; y < h; y++) {
            // 4 pixel per iteration, pack 4xU10 data to 5xU8 data
            uchar *p_dst_y = (uchar *)p_dst;
            for (int x = 0, j = 0; x <= w - 4; x += 4, j += 5) {
                const int src_ofs = y * sw_strd / 2 + x;
                const int dst_ofs_y = y * dw_strd + j;
                pack_data_10bit(p_src_yr + src_ofs, p_dst_y + dst_ofs_y);
            }
        }
        for (int y = 0; y < chroma_hgt; y++) {
            // 4 pixel per iteration, pack 4xU10 data to 5xU8 data
            uchar *p_dst_c = (uchar *)p_dst + dw_strd * dh_strd;
            for (int x = 0, j = 0; x <= chroma_wid - 2; x += 2, j += 5) {
                const int src_ofs = y * sw_strd / 4 + x;
                const int dst_ofs_c = y * dw_strd + j;
                unpack_data[0] = p_src_ug[src_ofs + 0] & 0x3ff;
                unpack_data[1] = p_src_vb[src_ofs + 0] & 0x3ff;
                unpack_data[2] = p_src_ug[src_ofs + 1] & 0x3ff;
                unpack_data[3] = p_src_vb[src_ofs + 1] & 0x3ff;
                pack_data_10bit(unpack_data, p_dst_c + dst_ofs_c);
            }
        }
    } break;
    default: LOGE_f("unsupported image format %#x for now!\n", dst_fmt); return -1;
    }
    return 0;
}

int imgcvt_to_planar_8bit_lsb(uint8_t const *p_src, uint8_t *p_dst, int w, int h, int sw_strd, int sh_strd, int dw_strd,
    int dh_strd, int src_fmt, bool keep_alpha, int dither)
{
    assert(p_src && p_dst && p_src != p_dst);
    assert(dw_strd >= w * 1);

    // src format info
    int ret = 0;
    const int bpp = common_verify_imgfmt_bpp(src_fmt);
    const float ratio = common_verify_imgfmt_framesize_ratio(src_fmt);
    // const int frame_size = (w * h * bpp + 7) / 8;
    const int frame_size = sw_strd * sh_strd * ratio;
    LOGD_f("src fmt: %#x(%s), bpp: %d, frame_size: %d, plane_size_ratio: %.1f, ditherType: %d\n", src_fmt,
        common_verify_imgfmt_name(src_fmt), bpp, frame_size, ratio, dither);
    LOGD_f("src_stride: %dx%d, dst_stride: %dx%d\n", sw_strd, sh_strd, dw_strd, dh_strd);

    int chnl_num = 3;
    const int src_base_fmt = src_fmt & 0xF;
    const int chroma_hgt = src_base_fmt == YUV400 ? 0 : (src_base_fmt >= YUV420P ? h / 2 : h);
    const int chroma_wid = src_base_fmt == YUV400 ? 0 : (src_base_fmt >= YUV422P ? w / 2 : w);
    const int dhc_strd = src_base_fmt == YUV400 ? 0 : (src_base_fmt >= YUV420P ? dh_strd / 2 : dh_strd);
    const int dwc_strd = src_base_fmt == YUV400 ? 0 : (src_base_fmt >= YUV422P ? dw_strd / 2 : dw_strd);

    uint8_t *p_dst_yr = p_dst;
    uint8_t *p_dst_ug = p_dst + dw_strd * dh_strd;
    uint8_t *p_dst_vb = p_dst_ug + dwc_strd * dhc_strd;
    uint8_t *p_dst_a = keep_alpha ? (p_dst_vb + dwc_strd * dhc_strd) : NULL;
    LOGT_f("dst u/v offset: %td / %td\n", (uint8_t *)p_dst_ug - (uint8_t *)p_dst_yr, (uint8_t *)p_dst_vb - (uint8_t *)p_dst_yr);

    switch (src_fmt) {
    /* 8bit normal data to 8bit planar lsb data */
    case RGBA8888: chnl_num = 4; // NO break here!
    case RGB888:
    case YUV444I:  {
        assert(sw_strd >= w * chnl_num);
        for (int y = 0; y < h; y++) {
            for (int x = 0; x < w; x++) {
                const int src_ofs = y * sw_strd + x * chnl_num;
                const int dst_ofs = y * dw_strd + x;
                p_dst_yr[dst_ofs] = p_src[src_ofs + 0];
                p_dst_ug[dst_ofs] = p_src[src_ofs + 1];
                p_dst_vb[dst_ofs] = p_src[src_ofs + 2];
                // ignore alpha channel here
                // p_dst_a[dst_ofs] = p_src[src_ofs + 3];
            }
        }
    } break;
    case RGB_PLANAR:
    case YUV400:
    case YUV444P:
    case YUV422P:
    case YUV420P:    {
        assert(sw_strd >= w * 1);
        assert(sw_strd == dw_strd);
        // todo: support different stride
        memcpy(p_dst, p_src, frame_size);
    } break;
    case YUV444SP: {
        assert(sw_strd >= w * 1);
        const uchar *p_src_y = p_src;
        const uchar *p_src_c = p_src + sw_strd * h;
        for (int y = 0; y < h; y++) {
            for (int x = 0; x < w; x++) {
                const int src_ofs_y = y * sw_strd + x;
                const int src_ofs_c = y * sw_strd * 2 + x * 2;
                const int dst_ofs = y * dw_strd + x;
                p_dst_yr[dst_ofs] = p_src_y[src_ofs_y + 0];
                p_dst_ug[dst_ofs] = p_src_c[src_ofs_c + 0];
                p_dst_vb[dst_ofs] = p_src_c[src_ofs_c + 1];
            }
        }
    } break;
    case YUV422SP:
    case YUV420SP: {
        assert(sw_strd >= w * 1);
        assert(sw_strd >= dw_strd);
        const uchar *p_src_y = p_src;
        const uchar *p_src_c = p_src + sw_strd * h;

        for (int y = 0; y < h; y++)
            memcpy(p_dst_yr + y * dw_strd, p_src_y + y * sw_strd, w * sizeof(uchar));

        p_dst_vb = p_dst_ug + dw_strd * h / (src_fmt == YUV422SP ? 2 : 4); // update dst_v;
        for (int y = 0; y < chroma_hgt; y++) {
            for (int x = 0; x < chroma_wid; x++) {
                const int src_ofs_c = y * sw_strd + x * 2;
                const int dst_ofs_c = y * dw_strd / 2 + x;
                p_dst_ug[dst_ofs_c] = p_src_c[src_ofs_c + 0];
                p_dst_vb[dst_ofs_c] = p_src_c[src_ofs_c + 1];
            }
        }
    } break;

    case YUV420SP_TILE4X4: {
        assert(w % 4 == 0 && h % 4 == 0);
        const int tile_w = w / 4;
        const int tile_h = h / 4;

        for (int ty = 0; ty < tile_h; ty++) {
            for (int tx = 0; tx < tile_w; tx++) {
                const int tile_idx = ty * tile_w + tx;
                const int src_tile_offset = tile_idx * 24;

                const uchar *p_src_tile_y = p_src + src_tile_offset;
                const uchar *p_src_tile_uv = p_src_tile_y + 16;

                for (int row = 0; row < 4; row++) {
                    const int dy = ty * 4 + row;
                    for (int col = 0; col < 4; col++) {
                        const int dx = tx * 4 + col;
                        const int src_ofs = row * 4 + col;
                        const int dst_ofs = dy * dw_strd + dx;
                        p_dst_yr[dst_ofs] = p_src_tile_y[src_ofs];
                    }
                }

                for (int row = 0; row < 2; row++) {
                    for (int col = 0; col < 2; col++) {
                        const int dy = ty * 2 + row;
                        const int dx = tx * 2 + col;
                        const int src_ofs = row * 4 + col * 2;
                        const int dst_ofs = dy * dw_strd / 2 + dx;
                        p_dst_ug[dst_ofs] = p_src_tile_uv[src_ofs + 0];
                        p_dst_vb[dst_ofs] = p_src_tile_uv[src_ofs + 1];
                    }
                }
            }
        }
    } break;
    case YUV422SP_TILE4X4: {
        assert(w % 4 == 0 && h % 4 == 0);
        const int tile_w = w / 4;
        const int tile_h = h / 4;

        for (int ty = 0; ty < tile_h; ty++) {
            for (int tx = 0; tx < tile_w; tx++) {
                const int tile_idx = ty * tile_w + tx;
                const int src_tile_offset = tile_idx * 32;

                const uchar *p_src_tile_y = p_src + src_tile_offset;
                const uchar *p_src_tile_uv = p_src_tile_y + 16;

                for (int row = 0; row < 4; row++) {
                    const int dy = ty * 4 + row;
                    for (int col = 0; col < 4; col++) {
                        const int dx = tx * 4 + col;
                        const int src_ofs = row * 4 + col;
                        const int dst_ofs = dy * dw_strd + dx;
                        p_dst_yr[dst_ofs] = p_src_tile_y[src_ofs];
                    }
                }

                for (int row = 0; row < 2; row++) {
                    for (int col = 0; col < 4; col++) {
                        const int dy = ty * 2 + row;
                        const int dx = tx * 4 + col;
                        const int src_ofs = row * 4 + col;
                        const int dst_ofs = dy * dw_strd + dx;
                        int u_val = p_src_tile_uv[src_ofs * 2 + 0] - 128;
                        int v_val = p_src_tile_uv[src_ofs * 2 + 1] - 128;
                        p_dst_ug[dst_ofs] = u_val;
                        p_dst_vb[dst_ofs] = v_val;
                    }
                }
            }
        }
    } break;
    case YUV444SP_TILE4X4: {
        assert(w % 4 == 0 && h % 4 == 0);
        const int tile_w = w / 4;
        const int tile_h = h / 4;

        for (int ty = 0; ty < tile_h; ty++) {
            for (int tx = 0; tx < tile_w; tx++) {
                const int tile_idx = ty * tile_w + tx;
                const int src_tile_offset = tile_idx * 48;

                const uchar *p_src_tile_y = p_src + src_tile_offset;
                const uchar *p_src_tile_uv = p_src_tile_y + 16;

                for (int row = 0; row < 4; row++) {
                    const int dy = ty * 4 + row;
                    for (int col = 0; col < 4; col++) {
                        const int dx = tx * 4 + col;
                        const int src_ofs = row * 4 + col;
                        const int dst_ofs = dy * dw_strd + dx;
                        p_dst_yr[dst_ofs] = p_src_tile_y[src_ofs];
                    }
                }

                for (int row = 0; row < 4; row++) {
                    const int dy = ty * 4 + row;
                    for (int col = 0; col < 4; col++) {
                        const int dx = tx * 4 + col;
                        const int src_ofs = row * 4 + col;
                        const int dst_ofs = dy * dw_strd / 2 + dx;
                        int u_val = p_src_tile_uv[src_ofs * 2 + 0] - 128;
                        int v_val = p_src_tile_uv[src_ofs * 2 + 1] - 128;
                        p_dst_ug[dst_ofs] = u_val;
                        p_dst_vb[dst_ofs] = v_val;
                    }
                }
            }
        }
    } break;
    default: LOGE_f("unsupported image format %#x for now!\n", src_fmt); return -1;
    }
    return 0;
}

int imgcvt_from_planar_8bit_lsb(uint8_t const *p_src, uint8_t *p_dst, int w, int h, int sw_strd, int sh_strd,
    int dw_strd, int dh_strd, int dst_fmt, bool has_alpha, int dither)
{
    assert(p_src && p_dst && p_src != p_dst);
    assert(dw_strd >= w * 1);

    // src format info
    int ret = 0;
    const int bpp = common_verify_imgfmt_bpp(dst_fmt);
    // const int frame_size = (w * h * bpp + 7) / 8;
    const int frame_size = dw_strd * h * common_verify_imgfmt_framesize_ratio(dst_fmt);
    LOGD_f("dst fmt: %#x(%s), bpp: %d, frame_size: %d, ditherType: %d\n", dst_fmt, common_verify_imgfmt_name(dst_fmt),
        bpp, frame_size, dither);
    LOGD_f("src_stride: %dx%d, dst_stride: %dx%d\n", sw_strd, sh_strd, dw_strd, dh_strd);

    int chnl_num = 3;
    const int dst_base_fmt = dst_fmt & 0xF;
    const int chroma_hgt = dst_base_fmt == YUV400 ? 0 : (dst_base_fmt >= YUV420P ? h / 2 : h);
    const int chroma_wid = dst_base_fmt == YUV400 ? 0 : (dst_base_fmt >= YUV422P ? w / 2 : w);
    const int shc_strd = dst_base_fmt == YUV400 ? 0 : (dst_base_fmt >= YUV420P ? sh_strd / 2 : sh_strd);
    const int swc_strd = dst_base_fmt == YUV400 ? 0 : (dst_base_fmt >= YUV422P ? sw_strd / 2 : sw_strd);
    const int dhc_strd = dst_base_fmt == YUV400 ? 0 : (dst_base_fmt >= YUV420P ? dh_strd / 2 : dh_strd);
    const int dwc_strd = dst_base_fmt == YUV400 ? 0 : (dst_base_fmt >= YUV422P ? dw_strd / 2 : dw_strd);

    const uint8_t *p_src_yr = p_src;
    const uint8_t *p_src_ug = p_src + sw_strd * sh_strd;
    const uint8_t *p_src_vb = p_src_ug + swc_strd * shc_strd;
    const uint8_t *p_src_a = has_alpha ? (p_src_vb + swc_strd * shc_strd) : NULL;
    LOGT_f("src u/v offset: %td / %td\n", (uint8_t *)p_src_ug - (uint8_t *)p_src_yr, (uint8_t *)p_src_vb - (uint8_t *)p_src_yr);

    switch (dst_fmt) {
    /* 8bit planar lsb data to 8bit normal data */
    case RGBA8888: chnl_num = 4; // NO break here!
    case RGB888:
    case YUV444I:  {
        assert(dw_strd >= w * chnl_num);
        for (int y = 0; y < h; y++) {
            for (int x = 0; x < w; x++) {
                const int src_ofs = y * sw_strd + x;
                const int dst_ofs = y * dw_strd + x * chnl_num;
                p_dst[dst_ofs + 0] = p_src_yr[src_ofs];
                p_dst[dst_ofs + 1] = p_src_ug[src_ofs];
                p_dst[dst_ofs + 2] = p_src_vb[src_ofs];
                if (chnl_num == 4) {
                    p_dst[dst_ofs + 3] = 0xFF;
                }
            }
        }
    } break;
    case RGB_PLANAR:
    case YUV400:
    case YUV444P:
    case YUV422P:
    case YUV420P:    {
        assert(dw_strd >= w * 1);
        assert(sw_strd == dw_strd);
        uchar *p_dst_y = p_dst;
        uchar *p_dst_u = p_dst + dw_strd * dh_strd;
        uchar *p_dst_v = p_dst_u + dwc_strd * dhc_strd;
        for (int y = 0; y < h; ++y)
            memcpy(p_dst_y + y * dw_strd, p_src_yr + y * sw_strd, MIN(dw_strd, sw_strd));
        for (int y = 0; y < chroma_hgt; ++y) {
            memcpy(p_dst_u + y * dwc_strd, p_src_ug + y * swc_strd, MIN(dwc_strd, swc_strd));
            memcpy(p_dst_v + y * dwc_strd, p_src_vb + y * swc_strd, MIN(dwc_strd, swc_strd));
        }
    } break;
    case YUV444SP: {
        assert(dw_strd >= w * 1);
        uchar *p_dst_y = p_dst;
        uchar *p_dst_c = p_dst + dw_strd * dh_strd;
        for (int y = 0; y < h; y++) {
            for (int x = 0; x < w; x++) {
                const int dst_ofs_y = y * dw_strd + x;
                const int dst_ofs_c = y * dw_strd * 2 + x * 2;
                const int src_ofs = y * sw_strd + x;
                p_dst_y[dst_ofs_y] = p_src_yr[src_ofs];
                p_dst_c[dst_ofs_c + 0] = p_src_ug[src_ofs];
                p_dst_c[dst_ofs_c + 1] = p_src_vb[src_ofs];
            }
        }
    } break;
    case YUV422SP:
    case YUV420SP: {
        assert(dw_strd >= w * 1);
        assert(sw_strd == dw_strd);
        uchar *p_dst_y = p_dst;
        uchar *p_dst_c = p_dst + dw_strd * dh_strd;
        for (int y = 0; y < h; ++y)
            memcpy(p_dst_y + y * dw_strd, p_src_yr + y * sw_strd, MIN(dw_strd, sw_strd));
        // p_src_vb = p_src_ug + sw_strd * sw_strd / (dst_fmt == YUV422SP ? 2 : 4); // update src_v;
        for (int y = 0; y < chroma_hgt; y++) {
            for (int x = 0; x < chroma_wid; x++) {
                const int dst_ofs_c = y * dw_strd + x * 2;
                const int src_ofs_c = y * sw_strd / 2 + x;
                p_dst_c[dst_ofs_c + 0] = p_src_ug[src_ofs_c];
                p_dst_c[dst_ofs_c + 1] = p_src_vb[src_ofs_c];
            }
        }
    } break;

    case YUV420SP_TILE4X4: {
        assert(w % 4 == 0 && h % 4 == 0);
        const int tile_w = w / 4;
        const int tile_h = h / 4;

        for (int ty = 0; ty < tile_h; ty++) {
            for (int tx = 0; tx < tile_w; tx++) {
                const int tile_idx = ty * tile_w + tx;
                const int dst_tile_offset = tile_idx * 24;

                uchar *p_dst_tile_y = p_dst + dst_tile_offset;
                uchar *p_dst_tile_uv = p_dst_tile_y + 16;

                for (int row = 0; row < 4; row++) {
                    const int sy = ty * 4 + row;
                    for (int col = 0; col < 4; col++) {
                        const int sx = tx * 4 + col;
                        const int dst_ofs = row * 4 + col;
                        const int src_ofs = sy * sw_strd + sx;
                        p_dst_tile_y[dst_ofs] = p_src_yr[src_ofs];
                    }
                }

                for (int row = 0; row < 2; row++) {
                    for (int col = 0; col < 2; col++) {
                        const int sy = ty * 2 + row;
                        const int sx = tx * 2 + col;
                        const int dst_ofs = row * 4 + col * 2;
                        const int src_ofs = sy * sw_strd / 2 + sx;
                        p_dst_tile_uv[dst_ofs + 0] = p_src_ug[src_ofs];
                        p_dst_tile_uv[dst_ofs + 1] = p_src_vb[src_ofs];
                    }
                }
            }
        }
    } break;
    case YUV422SP_TILE4X4: {
        assert(w % 4 == 0 && h % 4 == 0);
        const int tile_w = w / 4;
        const int tile_h = h / 4;

        for (int ty = 0; ty < tile_h; ty++) {
            for (int tx = 0; tx < tile_w; tx++) {
                const int tile_idx = ty * tile_w + tx;
                const int dst_tile_offset = tile_idx * 32;

                uchar *p_dst_tile_y = p_dst + dst_tile_offset;
                uchar *p_dst_tile_uv = p_dst_tile_y + 16;

                for (int row = 0; row < 4; row++) {
                    const int sy = ty * 4 + row;
                    for (int col = 0; col < 4; col++) {
                        const int sx = tx * 4 + col;
                        const int dst_ofs = row * 4 + col;
                        const int src_ofs = sy * sw_strd + sx;
                        p_dst_tile_y[dst_ofs] = p_src_yr[src_ofs];
                    }
                }

                for (int row = 0; row < 4; row++) {
                    const int sy = ty * 4 + row;
                    for (int col = 0; col < 4; col++) {
                        const int sx = tx * 4 + col;
                        const int dst_ofs = row * 4 + col;
                        const int src_ofs = sy * sw_strd / 2 + sx;
                        int u_val = p_src_ug[src_ofs] + 128;
                        int v_val = p_src_vb[src_ofs] + 128;
                        p_dst_tile_uv[dst_ofs * 2 + 0] = u_val;
                        p_dst_tile_uv[dst_ofs * 2 + 1] = v_val;
                    }
                }
            }
        }
    } break;
    case YUV444SP_TILE4X4: {
        assert(w % 4 == 0 && h % 4 == 0);
        const int tile_w = w / 4;
        const int tile_h = h / 4;

        for (int ty = 0; ty < tile_h; ty++) {
            for (int tx = 0; tx < tile_w; tx++) {
                const int tile_idx = ty * tile_w + tx;
                const int dst_tile_offset = tile_idx * 48;

                uchar *p_dst_tile_y = p_dst + dst_tile_offset;
                uchar *p_dst_tile_uv = p_dst_tile_y + 16;

                for (int row = 0; row < 4; row++) {
                    const int sy = ty * 4 + row;
                    for (int col = 0; col < 4; col++) {
                        const int sx = tx * 4 + col;
                        const int dst_ofs = row * 4 + col;
                        const int src_ofs = sy * sw_strd + sx;
                        p_dst_tile_y[dst_ofs] = p_src_yr[src_ofs];
                    }
                }

                for (int row = 0; row < 4; row++) {
                    const int sy = ty * 4 + row;
                    for (int col = 0; col < 4; col++) {
                        const int sx = tx * 4 + col;
                        const int dst_ofs = row * 4 + col;
                        const int src_ofs = sy * sw_strd + sx;
                        int u_val = p_src_ug[src_ofs] + 128;
                        int v_val = p_src_vb[src_ofs] + 128;
                        p_dst_tile_uv[dst_ofs * 2 + 0] = u_val;
                        p_dst_tile_uv[dst_ofs * 2 + 1] = v_val;
                    }
                }
            }
        }
    } break;
    default: LOGE_f("unsupported image format %#x for now!\n", dst_fmt); return -1;
    }
    return 0;
}

void dump_regs_to_dat(const char *filename, uint const *regs, int nb_regs, unsigned int start_addr)
{
    FILE *fp = stdout;
    if (filename) {
        fp = fopen(filename, "wb");
        if (fp == NULL) {
            LOGE("open file %s failed! dump to stdout instead!\n", filename);
            fp = stdout;
        }
    }

    // dump regs
    int i = 0;
    for (; i <= nb_regs - 4; i += 4) {
        fprintf(fp, "0x%08X:  0x%08X 0x%08X 0x%08X 0x%08X\n", start_addr + i * 4, regs[i], regs[i + 1], regs[i + 2],
            regs[i + 3]);
    }
    if (i < nb_regs) {
        fprintf(fp, "0x%08X: ", start_addr + i * 4);
        for (; i < nb_regs; ++i) {
            fprintf(fp, " 0x%08X", regs[i]);
        }
        fprintf(fp, "\n");
    }

    if (fp != stdout) {
        fclose(fp);
        LOGI("write reg data(length=%d) to file: %s\n", nb_regs, filename);
    }
}