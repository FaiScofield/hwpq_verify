/**
 * @copyright Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @description: verify_com.c
 * @author: vance.wu@rock-chips.com
 * @create: 2025-09-12
 * @history:
 *  2025-12-01 vance.wu: Add/fix more 8/10bit pixel formats support for IO.
 *  2025-10-23 vance.wu: Add more 8bit pixel formats support for IO.
 *  2025-10-12 vance.wu: Add 10bit-packed-YUV444 formats support for IO.
 *  2025-09-08 vance.wu: Add common macros & functions for commonly usage.
 *  2025-09-15 vance.wu: Add pixel format pack/unpack functions.
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
int image_read_to_planar(FILE *fp, void *p_buf, int frmidx, int w, int h, int fmt, int depth)
{
    if (!fp || !p_buf) {
        LOGE("invalid fp or output buffer!\n");
        return -1;
    }
    if (frmidx < 0 || w <= 0 || h <= 0) {
        LOGE("invalid argument! frmidx: %d, w: %d, h: %d, fmt: %d %s\n", frmidx, w, h, fmt, common_verify_imgfmt_str(fmt));
        return -1;
    }

    // src format info
    int ret = 0;
    const int plane_elems = w * h;
    const int bpp = common_verify_imgfmt_bpp(fmt);
    const int frame_size = (w * h * bpp + 7) / 8;

    uchar *p_src = (uchar *)malloc(frame_size);
    fseek(fp, frame_size * frmidx, SEEK_SET);
    const size_t read_size = fread(p_src, 1, frame_size, fp);
    if (read_size != frame_size) {
        LOGE("readSize(%zu) != frameSize(%d) for frame#%d format %d!\n", read_size, frame_size, frmidx, fmt);
        ret = -1;
    }

    const int src_stride = common_verify_imgfmt_pitch_ratio(fmt) * w;
    const bool keep_alpha = false; // ignore alpha channel here

    if (0 == ret) {
        if (depth == 8) {
            const int dst_stride = w * 1;
            ret = imgcvt_to_planar_8bit_lsb(p_src, (uint8_t *)p_buf, w, h, src_stride, dst_stride, fmt, keep_alpha);
        }
        else if (depth == 10) {
            const int dst_stride = w * 2;
            ret = imgcvt_to_planar_10bit_lsb(p_src, (uint16_t *)p_buf, w, h, src_stride, dst_stride, fmt, keep_alpha);
        }
        else {
            LOGE("%s: invalid target depth=%d !\n", __func__, depth);
            ret = -1;
        }
    }

    free(p_src);
    return ret;
}

int image_write_from_plannar(FILE *fp, void *p_buf, int frmidx, int w, int h, int fmt, int depth)
{
    if (!fp || !p_buf) {
        LOGE("invalid fp or output buffer!\n");
        return -1;
    }
    if (frmidx < 0 || w <= 0 || h <= 0) {
        LOGE("invalid argument! frmidx: %d, w: %d, h: %d\n", frmidx, w, h);
        return -1;
    }

    // dst format info
    int ret = 0;
    const int bpp = common_verify_imgfmt_bpp(fmt);
    const int frame_size = (w * h * bpp + 7) / 8;
    ushort *p_dst = (ushort *)calloc(frame_size, 1);

    const int dst_stride = common_verify_imgfmt_pitch_ratio(fmt) * w;
    const bool has_alpha = false; // ignore alpha channel here

    if (depth == 8) {
        const int src_stride = w;
        ret = imgcvt_from_planar_8bit_lsb((uint8_t *)p_buf, (uint8_t *)p_dst, w, h, src_stride, dst_stride, fmt, has_alpha);
    }
    else if (depth == 10) {
        const int src_stride = w * 2;
        ret = imgcvt_from_planar_10bit_lsb((uint16_t *)p_buf, (uint8_t *)p_dst, w, h, src_stride, dst_stride, fmt, has_alpha);
    }
    else {
        LOGE("%s: invalid target depth=%d !\n", __func__, depth);
        ret = -1;
    }

    if (0 == ret) {
        fseek(fp, frame_size * frmidx, SEEK_SET);
        size_t write_size = fwrite(p_dst, 1, frame_size, fp);
        if (write_size != frame_size) {
            LOGE("writeSize(%zu) != frameSize(%d) for frame#%d format %d!\n", write_size, frame_size, frmidx, fmt);
            ret = -1;
        }
    }
    else {
        LOGE("%s: imgcvt_from_planar failed! %d\n", __func__, ret);
        ret = -1;
    }

    free(p_dst);
    return ret;
}

int image_read_to_10bit_planar(FILE *fp, void *p_buf, int frmidx, int w, int h, int fmt)
{
    return image_read_to_planar(fp, p_buf, frmidx, w, h, fmt, 10);
}

int image_write_from_10bit_plannar(FILE *fp, void *p_buf, int frmidx, int w, int h, int fmt)
{
    return image_write_from_plannar(fp, p_buf, frmidx, w, h, fmt, 10);
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
    LOGD("fmt: %d(%s), bpp: %d, frame_size: %d\n", fmt, common_verify_imgfmt_str(fmt), bpp, frame_size);

    fseek(fp, frame_size * frmidx, SEEK_SET);
    size_t read_size = fread(p_buf, 1, frame_size, fp);
    if (read_size != frame_size) {
        LOGE("readSize(%zu) != frameSize(%d) for frame#%d format %d!\n", read_size, frame_size, frmidx, fmt);
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
    LOGD("fmt: %d(%s), bpp: %d, frame_size: %d\n", fmt, common_verify_imgfmt_str(fmt), bpp, frame_size);

    size_t write_size = fwrite(p_buf, 1, frame_size, fp);
    if (write_size != frame_size) {
        LOGE("writeSize(%zu) != frameSize(%d) for frame#%d format %d!\n", write_size, frame_size, frmidx, fmt);
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
    default: LOGE("%s: unsupported image format %d case to pack !\n", __func__, fmt); return -1;
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
    default: LOGE("%s: unsupported image format %d case to pack !\n", __func__, fmt); return -1;
    }
    return 0;
}

int imgcvt_to_planar_10bit_lsb(uint8_t const *p_src, uint16_t *p_dst, int w, int h, int src_strd, int dst_strd,
    int src_fmt, bool keep_alpha)
{
    assert(p_src != (uint8_t *)p_dst);
    assert(dst_strd >= w * 2);

    // src format info
    const int bpp = common_verify_imgfmt_bpp(src_fmt);
    const int frame_size = (w * h * bpp + 7) / 8;
    LOGD_f("src fmt: %d(%s), bpp: %d, frame_size: %d\n", src_fmt, common_verify_imgfmt_str(src_fmt), bpp, frame_size);
    LOGD_f("src_strd: %d, dst_strd: %d\n", src_strd, dst_strd);

    int chnl_num = 3;
    int chroma_hgt = (src_fmt % 10 >= YUV420P) ? h / 2 : h;
    int chroma_wid = (src_fmt % 10 >= YUV422P) ? w / 2 : w;

    // dst planar addrs
    ushort *p_dst_yr = (ushort *)p_dst;
    ushort *p_dst_ug = (ushort *)((uint8_t *)p_dst + dst_strd * h);
    ushort *p_dst_vb = (ushort *)((uint8_t *)p_dst + dst_strd * h * 2);
    ushort *p_dst_a = keep_alpha ? (ushort *)((uint8_t *)p_dst + dst_strd * h * 3) : NULL;
    // need to update p_dst_vb for YUV422P & YUV420P
    if (src_fmt % 10 == 6 || src_fmt % 10 == 7) {
        p_dst_vb = (ushort *)((uint8_t *)p_dst_ug + dst_strd / 2 * h);
    }
    if (src_fmt % 10 == 8 || src_fmt % 10 == 9) {
        p_dst_vb = (ushort *)((uint8_t *)p_dst_ug + dst_strd / 2 * h / 2);
    }
    LOGT_f("dst u/v offset: %td / %td\n", p_dst_ug - p_dst_yr, p_dst_vb - p_dst_yr);

    switch (src_fmt) {
    /* 8bit normal data to 10bit planar lsb data */
    case RGBA8888: chnl_num = 4; // NO break here!
    case RGB888:
    case YUV444I:  {
        assert(src_strd >= w * chnl_num);
        for (int y = 0; y < h; y++) {
            for (int x = 0; x < w; x++) {
                const int src_ofs = y * src_strd + x * chnl_num;
                const int dst_ofs = y * dst_strd / 2 + x;
                p_dst_yr[dst_ofs] = p_src[src_ofs + 0] << 2;
                p_dst_ug[dst_ofs] = p_src[src_ofs + 1] << 2;
                p_dst_vb[dst_ofs] = p_src[src_ofs + 2] << 2;
                // ignore alpha channel here
            }
        }
    } break;
    case RGB_PLANAR:
    case YUV444P:    {
        assert(src_strd >= w * 1);
        const uchar *p_src_yr = p_src;
        const uchar *p_src_ug = p_src + src_strd * h;
        const uchar *p_src_vb = p_src + src_strd * h * 2;
        for (int y = 0; y < h; y++) {
            for (int x = 0; x < w; x++) {
                const int src_ofs = y * src_strd + x;
                const int dst_ofs = y * dst_strd / 2 + x;
                p_dst_yr[dst_ofs] = p_src_yr[src_ofs] << 2;
                p_dst_ug[dst_ofs] = p_src_ug[src_ofs] << 2;
                p_dst_vb[dst_ofs] = p_src_vb[src_ofs] << 2;
            }
        }
    } break;
    case YUV444SP: {
        assert(src_strd >= w * 1);
        const uchar *p_src_y = p_src;
        const uchar *p_src_c = p_src + src_strd * h;
        for (int y = 0; y < h; y++) {
            for (int x = 0; x < w; x++) {
                const int src_ofs_y = y * src_strd + x;
                const int src_ofs_c = y * src_strd * 2 + x * 2;
                const int dst_ofs = y * dst_strd / 2 + x;
                p_dst_yr[dst_ofs] = p_src_y[src_ofs_y + 0] << 2;
                p_dst_ug[dst_ofs] = p_src_c[src_ofs_c + 0] << 2;
                p_dst_vb[dst_ofs] = p_src_c[src_ofs_c + 1] << 2;
            }
        }
    } break;
    case YUV422SP: {
        assert(src_strd >= w * 1);
        const uchar *p_src_y = p_src;
        const uchar *p_src_c = p_src + src_strd * h;
        for (int y = 0; y < h; y++) {
            for (int x = 0; x < w; x++) {
                const int src_ofs_y = y * src_strd + x;
                const int dst_ofs_y = y * dst_strd / 2 + x;
                p_dst_yr[dst_ofs_y] = p_src_y[src_ofs_y] << 2;
            }
            for (int x = 0; x < w / 2; x++) {
                const int src_ofs_c = y * src_strd + x * 2;
                const int dst_ofs_c = y * dst_strd / 4 + x;
                p_dst_ug[dst_ofs_c] = p_src_c[src_ofs_c + 0] << 2;
                p_dst_vb[dst_ofs_c] = p_src_c[src_ofs_c + 1] << 2;
            }
        }
    } break;
    case YUV420SP: {
        assert(src_strd >= w * 1);
        const uchar *p_src_y = p_src;
        const uchar *p_src_c = p_src + src_strd * h;
        for (int y = 0; y < h; y++) {
            for (int x = 0; x < w; x++) {
                const int src_ofs_y = y * src_strd + x;
                const int dst_ofs_y = y * dst_strd / 2 + x;
                p_dst_yr[dst_ofs_y] = p_src_y[src_ofs_y] << 2;
            }
        }
        for (int y = 0; y < h / 2; y++) {
            for (int x = 0; x < w / 2; x++) {
                const int src_ofs_c = y * src_strd + x * 2;
                const int dst_ofs_c = y * dst_strd / 4 + x;
                p_dst_ug[dst_ofs_c] = p_src_c[src_ofs_c + 0] << 2;
                p_dst_vb[dst_ofs_c] = p_src_c[src_ofs_c + 1] << 2;
            }
        }
    } break;

    /* 10bit lsb data to 10bit planar lsb data */
    case RGB_101010LSB:
    case YUV444I_10LSB: {
        assert(src_strd >= w * 3 * 2);
        for (int y = 0; y < h; y++) {
            const ushort *p_src_row = (ushort *)((uint8_t *)p_src + y * src_strd);
            for (int x = 0, j = 0; x < w; x++, j += 3) {
                const int dst_ofs = y * dst_strd / 2 + x;
                p_dst_yr[dst_ofs] = p_src_row[j + 0] & 0x3ff;
                p_dst_ug[dst_ofs] = p_src_row[j + 1] & 0x3ff;
                p_dst_vb[dst_ofs] = p_src_row[j + 2] & 0x3ff;
            }
        }
    } break;
    case RGB_PLANAR10LSB:
    case YUV444P_10LSB:
    case YUV422P_10LSB:
    case YUV420P_10LSB:   {
        assert(src_strd >= w * 2);
        assert(src_strd == dst_strd);
        memcpy(p_dst, p_src, frame_size);
    } break;
    case YUV444SP_10LSB: {
        assert(src_strd >= w * 2);
        const ushort *p_src_y = (ushort *)p_src;
        const ushort *p_src_c = (ushort *)((uint8_t *)p_src + h * src_strd);
        for (int y = 0; y < h; y++) {
            for (int x = 0, j = 0; x < w; x++, j += 2) {
                const int src_ofs_y = y * src_strd / 2 + x;
                const int src_ofs_c = y * src_strd + j;
                const int dst_ofs = y * dst_strd / 2 + x;
                p_dst_yr[dst_ofs] = p_src_y[src_ofs_y] & 0x3ff;
                p_dst_ug[dst_ofs] = p_src_c[src_ofs_c + 0] & 0x3ff;
                p_dst_vb[dst_ofs] = p_src_c[src_ofs_c + 1] & 0x3ff;
            }
        }
    } break;
    case YUV422SP_10LSB: {
        assert(src_strd >= w * 2);
        const ushort *p_src_y = (ushort *)p_src;
        const ushort *p_src_c = (ushort *)((uint8_t *)p_src + h * src_strd);
        for (int y = 0; y < h; y++) {
            for (int x = 0; x < w; x++) {
                const int src_ofs = y * src_strd / 2 + x;
                const int dst_ofs = y * dst_strd / 2 + x;
                p_dst_yr[dst_ofs] = p_src_y[src_ofs] & 0x3ff;
            }
            for (int x = 0, j = 0; x < w / 2; x++, j += 2) {
                const int src_ofs = y * src_strd / 2 + j;
                const int dst_ofs = y * dst_strd / 4 + x;
                p_dst_ug[dst_ofs] = p_src_c[src_ofs + 0] & 0x3ff;
                p_dst_vb[dst_ofs] = p_src_c[src_ofs + 1] & 0x3ff;
            }
        }
    } break;
    case YUV420SP_10LSB: {
        assert(src_strd >= w * 2);
        const ushort *p_src_y = (ushort *)p_src;
        const ushort *p_src_c = (ushort *)((uint8_t *)p_src + h * src_strd);
        for (int y = 0; y < h; y++) {
            for (int x = 0; x < w; x++) {
                const int src_ofs = y * src_strd / 2 + x;
                const int dst_ofs = y * dst_strd / 2 + x;
                p_dst_yr[dst_ofs] = p_src_y[src_ofs] & 0x3ff;
            }
        }
        for (int y = 0; y < h / 2; y++) {
            for (int x = 0, j = 0; x < w / 2; x++, j += 2) {
                const int src_ofs = y * src_strd / 2 + j;
                const int dst_ofs = y * dst_strd / 4 + x;
                p_dst_ug[dst_ofs] = p_src_c[src_ofs + 0] & 0x3ff;
                p_dst_vb[dst_ofs] = p_src_c[src_ofs + 1] & 0x3ff;
            }
        }
    } break;

    /* 10bit packed data to 10bit planar lsb data */
    case RGB_10PACKED:
    case YUV444I_10PACKED: {
        assert(w % 4 == 0); // must align with 4 pixels
        assert(src_strd >= w * 3 * 5 / 4);
        ushort unpack_data[4] = {0};
        for (int y = 0; y < h; y++) {
            // 4 pixel per iteration, unpack 15xU8 data to 12xU10 data
            for (int x = 0, j = 0; x <= w - 4; x += 4, j += 15) {
                const int dst_ofs = y * dst_strd / 2 + x;
                const int src_ofs = y * src_strd + j;
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
        assert(src_strd >= w * 4);
        for (int y = 0; y < h; y++) {
            uint *p_src_row = (uint *)((uint8_t *)p_src + y * src_strd);
            for (int x = 0; x < w; x++) {
                const int dst_ofs = y * dst_strd / 2 + x;
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
        assert(src_strd >= w * 5 / 4);
        for (int y = 0; y < h; y++) {
            // 4 pixel per iteration, unpack 5xU8 data to 4xU10 data
            uchar *p_src_yr = (uchar *)p_src;
            uchar *p_src_ug = (uchar *)p_src + src_strd * h;
            uchar *p_src_vb = (uchar *)p_src + src_strd * h * 2;
            for (int x = 0, j = 0; x <= w - 4; x += 4, j += 5) {
                const int src_ofs = y * src_strd + j;
                const int dst_ofs = y * dst_strd / 2 + x;
                unpack_data_10bit(p_src_yr + src_ofs, p_dst_yr + dst_ofs);
                unpack_data_10bit(p_src_ug + src_ofs, p_dst_ug + dst_ofs);
                unpack_data_10bit(p_src_vb + src_ofs, p_dst_vb + dst_ofs);
            }
        }
    } break;
    case YUV444SP_10PACKED: {
        assert(w % 4 == 0); // must align with 4 pixels
        assert(src_strd >= w * 5 / 4);
        ushort unpack_data[4] = {0};
        for (int y = 0; y < h; y++) {
            uchar *p_src_y = (uchar *)p_src;
            uchar *p_src_c = (uchar *)p_src + src_strd * h;
            for (int x = 0, j = 0; x <= w - 4; x += 4, j += 5) {
                const int src_ofs_y = y * src_strd + j;
                const int src_ofs_c = y * src_strd * 2 + j * 2;
                const int dst_ofs = y * dst_strd / 2 + x;
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
        assert(src_strd >= w * 5 / 4);
        const uchar *p_src_y = (uchar *)p_src;
        const uchar *p_src_c = (uchar *)p_src + src_strd * h;
        ushort unpack_data[4] = {0};
        for (int y = 0; y < h; y++) {
            for (int x = 0, j = 0; x <= w - 4; x += 4, j += 5) {
                const int src_ofs_y = y * src_strd + j;
                const int dst_ofs_y = y * dst_strd / 2 + x;
                unpack_data_10bit(p_src_y + src_ofs_y, p_dst_yr + dst_ofs_y);
            }
            for (int x = 0, j = 0; x <= w / 2 - 2; x += 2, j += 5) {
                const int src_ofs_c = y * src_strd + j;
                const int dst_ofs_c = y * dst_strd / 4 + x;
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
        assert(src_strd >= w * 5 / 4);
        const uchar *p_src_y = (uchar *)p_src;
        const uchar *p_src_c = (uchar *)p_src + src_strd * h;
        ushort unpack_data[4] = {0};
        for (int y = 0; y < h; y++) {
            uchar *p_src_y = (uchar *)p_src;
            for (int x = 0, j = 0; x <= w - 4; x += 4, j += 5) {
                const int src_ofs_y = y * src_strd + j;
                const int dst_ofs_y = y * dst_strd / 2 + x;
                unpack_data_10bit(p_src_y + src_ofs_y, p_dst_yr + dst_ofs_y);
            }
        }
        for (int y = 0; y < h / 2; y++) {
            uchar *p_src_c = (uchar *)p_src + src_strd * h;
            for (int x = 0, j = 0; x <= w / 2 - 2; x += 2, j += 5) {
                const int src_ofs_c = y * src_strd + j;
                const int dst_ofs_c = y * dst_strd / 4 + x;
                unpack_data_10bit(p_src_c + src_ofs_c, unpack_data);
                p_dst_ug[dst_ofs_c + 0] = unpack_data[0];
                p_dst_vb[dst_ofs_c + 0] = unpack_data[1];
                p_dst_ug[dst_ofs_c + 1] = unpack_data[2];
                p_dst_vb[dst_ofs_c + 1] = unpack_data[3];
            }
        }
    } break;
    default: LOGE("%s: unsupported image format %d for now!\n", __func__, src_fmt); return -1;
    }

    return 0;
}

int imgcvt_from_planar_10bit_lsb(uint16_t const *p_src, uint8_t *p_dst, int w, int h, int src_strd, int dst_strd,
    int dst_fmt, bool has_alpha)
{
    assert((uint8_t *)p_src != p_dst);
    assert(src_strd >= w * 2);

    // dst format info
    const int bpp = common_verify_imgfmt_bpp(dst_fmt);
    const int frame_size = (w * h * bpp + 7) / 8;
    LOGD_f("dst fmt: %d(%s), bpp: %d, frame_size: %d\n", dst_fmt, common_verify_imgfmt_str(dst_fmt), bpp, frame_size);
    LOGD_f("src_strd: %d, dst_strd: %d\n", src_strd, dst_strd);

    int chroma_hgt = (dst_fmt % 10 >= YUV420P) ? h / 2 : h;
    int chroma_wid = (dst_fmt % 10 >= YUV422P) ? w / 2 : w;

    const ushort *p_src_yr = (ushort *)p_src;
    const ushort *p_src_ug = (ushort *)((uint8_t *)p_src + src_strd * h);
    const ushort *p_src_vb = (ushort *)((uint8_t *)p_src + src_strd * h * 2);
    const ushort *p_src_a = has_alpha ? (ushort *)((uint8_t *)p_src + src_strd * h * 3) : NULL;
    // need to update p_src_vb for YUV422P & YUV420P
    if (dst_fmt % 10 == 6 || dst_fmt % 10 == 7) {
        p_src_vb = (ushort *)((uint8_t *)p_src_ug + src_strd / 2 * h);
    }
    if (dst_fmt % 10 == 8 || dst_fmt % 10 == 9) {
        p_src_vb = (ushort *)((uint8_t *)p_src_ug + src_strd / 2 * h / 2);
    }
    LOGT_f("src u/v offset: %td / %td\n", p_src_ug - p_src_yr, p_src_vb - p_src_yr);

    switch (dst_fmt) {
    /* 10bit plannar to 10bit lsb data */
    case RGB_101010LSB:
    case YUV444I_10LSB: {
        assert(dst_strd >= w * 3 * 2);
        for (int y = 0; y < h; y++) {
            ushort *p_dst_row = (ushort *)((uint8_t *)p_dst + y * dst_strd);
            for (int x = 0, j = 0; x < w; x++, j += 3) {
                const int src_ofs = y * src_strd / 2 + x;
                p_dst_row[j + 0] = p_src_yr[src_ofs];
                p_dst_row[j + 1] = p_src_ug[src_ofs];
                p_dst_row[j + 2] = p_src_vb[src_ofs];
            }
        }
    } break;
    case RGB_PLANAR10LSB:
    case YUV444P_10LSB:
    case YUV422P_10LSB:
    case YUV420P_10LSB:   {
        assert(dst_strd >= w * 2);
        assert(src_strd == dst_strd);
        memcpy(p_dst, p_src, frame_size);
    } break;
    case YUV444SP_10LSB: {
        assert(dst_strd >= w * 2);
        ushort *p_dst_y = (ushort *)p_dst;
        ushort *p_dst_c = (ushort *)((uint8_t *)p_dst + h * dst_strd);
        for (int y = 0; y < h; y++) {
            for (int x = 0, j = 0; x < w; x++, j += 2) {
                const int src_ofs = y * src_strd / 2 + x;
                const int dst_ofs_y = y * dst_strd / 2 + x;
                const int dst_ofs_c = y * dst_strd + j;
                p_dst_y[dst_ofs_y] = p_src_yr[src_ofs];
                p_dst_c[dst_ofs_c + 0] = p_src_ug[src_ofs];
                p_dst_c[dst_ofs_c + 1] = p_src_vb[src_ofs];
            }
        }
    } break;
    case YUV422SP_10LSB: {
        assert(dst_strd >= w * 2);
        ushort *p_dst_y = (ushort *)p_dst;
        ushort *p_dst_c = (ushort *)((uint8_t *)p_dst + h * dst_strd);
        for (int y = 0; y < h; y++) {
            for (int x = 0, j = 0; x < w; x++, j += 2) {
                const int src_ofs = y * src_strd / 2 + x;
                const int dst_ofs = y * dst_strd / 2 + x;
                p_dst_y[dst_ofs] = p_src_yr[src_ofs];
            }
            for (int x = 0, j = 0; x < w / 2; x++, j += 2) {
                const int src_ofs = y * src_strd / 4 + x;
                const int dst_ofs = y * dst_strd / 2 + j;
                p_dst_c[dst_ofs + 0] = p_src_ug[src_ofs];
                p_dst_c[dst_ofs + 1] = p_src_vb[src_ofs];
            }
        }
    } break;
    case YUV420SP_10LSB: {
        assert(dst_strd >= w * 2);
        ushort *p_dst_y = (ushort *)p_dst;
        ushort *p_dst_c = (ushort *)((uint8_t *)p_dst + h * dst_strd);
        for (int y = 0; y < h; y++) {
            for (int x = 0, j = 0; x < w; x++, j += 2) {
                const int src_ofs = y * src_strd / 2 + x;
                const int dst_ofs = y * dst_strd / 2 + x;
                p_dst_y[dst_ofs] = p_src_yr[src_ofs];
            }
        }
        for (int y = 0; y < h / 2; y++) {
            for (int x = 0, j = 0; x < w / 2; x++, j += 2) {
                const int src_ofs = y * src_strd / 4 + x;
                const int dst_ofs = y * dst_strd / 2 + j;
                p_dst_c[dst_ofs + 0] = p_src_ug[src_ofs];
                p_dst_c[dst_ofs + 1] = p_src_vb[src_ofs];
            }
        }
    } break;

    /* 10bit plannar to 10bit packed data */
    case RGB_10PACKED:
    case YUV444I_10PACKED: {
        assert(w % 4 == 0); // must align with 4 pixels
        assert(dst_strd >= w * 3 * 5 / 4);
        ushort unpack_data[4] = {0};
        for (int y = 0; y < h; y++) {
            // 4 pixel per iteration, pack 12xU10 data to 15xU8 data
            for (int x = 0, j = 0; x <= w - 4; x += 4, j += 15) {
                const int src_ofs = y * src_strd / 2 + x;
                const int dst_ofs = y * dst_strd + j;
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
        assert(dst_strd >= w * 4);
        ushort rgba[4] = {0};
        for (int y = 0; y < h; y++) {
            uint *p_dst_row = (uint *)((uint8_t *)p_dst + y * dst_strd);
            for (int x = 0; x < w; x++) {
                const int src_ofs = y * src_strd / 2 + x;
                const int dst_ofs = y * dst_strd + x * 3;
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
        assert(dst_strd >= w * 5 / 4);
        for (int y = 0; y < h; y++) {
            // 4 pixel per iteration, pack 4xU10 data to 5xU8 data
            uchar *p_dst_yr = (uchar *)p_dst;
            uchar *p_dst_ug = (uchar *)p_dst + dst_strd * h;
            uchar *p_dst_vb = (uchar *)p_dst + dst_strd * h * 2;
            for (int x = 0, j = 0; x <= w - 4; x += 4, j += 5) {
                const int src_ofs = y * src_strd / 2 + x;
                const int dst_ofs = y * dst_strd + j;
                pack_data_10bit(p_src_yr + src_ofs, p_dst_yr + dst_ofs);
                pack_data_10bit(p_src_ug + src_ofs, p_dst_ug + dst_ofs);
                pack_data_10bit(p_src_vb + src_ofs, p_dst_vb + dst_ofs);
            }
        }
    } break;
    case YUV422P_10PACKED:
    case YUV420P_10PACKED: {
        assert(w % 4 == 0); // must align with 4 pixels
        assert(dst_strd >= w * 5 / 4);
        for (int y = 0; y < h; y++) {
            uchar *p_dst_yr = (uchar *)p_dst;
            for (int x = 0, j = 0; x <= w - 4; x += 4, j += 5) {
                const int src_ofs = y * src_strd / 2 + x;
                const int dst_ofs = y * dst_strd + j;
                pack_data_10bit(p_src_yr + src_ofs, p_dst_yr + dst_ofs);
            }
        }
        for (int y = 0; y < chroma_hgt; y++) {
            uchar *p_dst_ug = (uchar *)p_dst + dst_strd * h;
            uchar *p_dst_vb = (uchar *)p_dst + (YUV422P_10PACKED == dst_fmt ? dst_strd * h * 3 / 2 : dst_strd * h * 5 / 4);
            for (int x = 0, j = 0; x <= chroma_wid - 4; x += 4, j += 5) {
                const int src_ofs = y * src_strd / 4 + x;
                const int dst_ofs = y * dst_strd / 2 + j;
                pack_data_10bit(p_src_ug + src_ofs, p_dst_ug + dst_ofs);
                pack_data_10bit(p_src_vb + src_ofs, p_dst_vb + dst_ofs);
            }
        }
    } break;
    case YUV444SP_10PACKED: {
        assert(w % 4 == 0); // must align with 4 pixels
        assert(dst_strd >= w * 5 / 4);
        ushort unpack_data[4] = {0};
        for (int y = 0; y < h; y++) {
            // 4 pixel per iteration, pack 4xU10 data to 5xU8 data
            uchar *p_dst_y = (uchar *)p_dst;
            uchar *p_dst_c = (uchar *)p_dst + dst_strd * h;
            for (int x = 0, j = 0; x <= w - 4; x += 4, j += 5) {
                const int src_ofs = y * src_strd / 2 + x;
                const int dst_ofs_y = y * dst_strd + j;
                const int dst_ofs_c = y * dst_strd * 2 + j * 2;
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
        assert(dst_strd >= w * 5 / 4);
        ushort unpack_data[4] = {0};
        for (int y = 0; y < h; y++) {
            // 4 pixel per iteration, pack 4xU10 data to 5xU8 data
            uchar *p_dst_y = (uchar *)p_dst;
            uchar *p_dst_c = (uchar *)p_dst + dst_strd * h;
            for (int x = 0, j = 0; x <= w - 4; x += 4, j += 5) {
                const int src_ofs = y * src_strd / 2 + x;
                const int dst_ofs_y = y * dst_strd + j;
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
        assert(dst_strd >= w * 5 / 4);
        ushort unpack_data[4] = {0};
        for (int y = 0; y < h; y++) {
            // 4 pixel per iteration, pack 4xU10 data to 5xU8 data
            uchar *p_dst_y = (uchar *)p_dst;
            for (int x = 0, j = 0; x <= w - 4; x += 4, j += 5) {
                const int src_ofs = y * src_strd / 2 + x;
                const int dst_ofs_y = y * dst_strd + j;
                pack_data_10bit(p_src_yr + src_ofs, p_dst_y + dst_ofs_y);
            }
        }
        for (int y = 0; y < h / 2; y++) {
            // 4 pixel per iteration, pack 4xU10 data to 5xU8 data
            uchar *p_dst_c = (uchar *)p_dst + dst_strd * h;
            for (int x = 0, j = 0; x <= w / 2 - 2; x += 2, j += 5) {
                const int src_ofs = y * src_strd / 4 + x;
                const int dst_ofs_c = y * dst_strd + j;
                unpack_data[0] = p_src_ug[src_ofs + 0] & 0x3ff;
                unpack_data[1] = p_src_vb[src_ofs + 0] & 0x3ff;
                unpack_data[2] = p_src_ug[src_ofs + 1] & 0x3ff;
                unpack_data[3] = p_src_vb[src_ofs + 1] & 0x3ff;
                pack_data_10bit(unpack_data, p_dst_c + dst_ofs_c);
            }
        }
    } break;
    default: LOGE("%s: unsupported image format %d for now!\n", __func__, dst_fmt); return -1;
    }
    return 0;
}

int imgcvt_to_planar_8bit_lsb(uint8_t const *p_src, uint8_t *p_dst, int w, int h, int src_strd, int dst_strd,
    int src_fmt, bool keep_alpha)
{
    assert(p_src != p_dst);
    assert(dst_strd >= w * 1);

    // src format info
    int ret = 0;
    const int bpp = common_verify_imgfmt_bpp(src_fmt);
    const int frame_size = (w * h * bpp + 7) / 8;
    LOGD("src fmt: %d(%s), bpp: %d, frame_size: %d\n", src_fmt, common_verify_imgfmt_str(src_fmt), bpp, frame_size);
    LOGD("src_strd: %d, dst_strd: %d\n", src_strd, dst_strd);

    int chnl_num = 3;
    int chroma_hgt = (src_fmt % 10 >= YUV420P) ? h / 2 : h;
    int chroma_wid = (src_fmt % 10 >= YUV422P) ? w / 2 : w;

    uint8_t *p_dst_yr = p_dst;
    uint8_t *p_dst_ug = p_dst + dst_strd * h;
    uint8_t *p_dst_vb = p_dst + dst_strd * h * 2;
    uint8_t *p_dst_a = keep_alpha ? (p_dst + dst_strd * h * 3) : NULL;
    LOGT("%s: dst u/v offset: %td / %td\n", __func__, p_dst_ug - p_dst_yr, p_dst_vb - p_dst_yr);

    switch (src_fmt) {
    /* 8bit normal data to 8bit planar lsb data */
    case RGBA8888: chnl_num = 4; // NO break here!
    case RGB888:
    case YUV444I:  {
        assert(src_strd >= w * chnl_num);
        for (int y = 0; y < h; y++) {
            for (int x = 0; x < w; x++) {
                const int src_ofs = y * src_strd + x * chnl_num;
                const int dst_ofs = y * dst_strd + x;
                p_dst_yr[dst_ofs] = p_src[src_ofs + 0];
                p_dst_ug[dst_ofs] = p_src[src_ofs + 1];
                p_dst_vb[dst_ofs] = p_src[src_ofs + 2];
                // ignore alpha channel here
                // p_dst_a[dst_ofs] = p_src[src_ofs + 3];
            }
        }
    } break;
    case RGB_PLANAR:
    case YUV444P:
    case YUV422P:
    case YUV420P:    {
        assert(src_strd >= w * 1);
        assert(src_strd == dst_strd);
        memcpy(p_dst, p_src, frame_size);
    } break;
    case YUV444SP: {
        assert(src_strd >= w * 1);
        const uchar *p_src_y = p_src;
        const uchar *p_src_c = p_src + src_strd * h;
        for (int y = 0; y < h; y++) {
            for (int x = 0; x < w; x++) {
                const int src_ofs_y = y * src_strd + x;
                const int src_ofs_c = y * src_strd + x * 2;
                const int dst_ofs = y * dst_strd + x;
                p_dst_yr[dst_ofs] = p_src_y[src_ofs_y + 0];
                p_dst_ug[dst_ofs] = p_src_c[src_ofs_c + 0];
                p_dst_vb[dst_ofs] = p_src_c[src_ofs_c + 1];
            }
        }
    } break;
    case YUV422SP:
    case YUV420SP: {
        assert(src_strd >= w * 1);
        assert(src_strd == dst_strd);
        const uchar *p_src_y = p_src;
        const uchar *p_src_c = p_src + src_strd * h;
        memcpy(p_dst_yr, p_src_y, src_strd * h);
        p_dst_vb = p_dst_ug + dst_strd * h / (src_fmt == YUV422SP ? 2 : 4); // update dst_v;
        for (int y = 0; y < chroma_hgt; y++) {
            for (int x = 0; x < chroma_wid; x++) {
                const int src_ofs_c = y * src_strd + x * 2;
                const int dst_ofs_c = y * dst_strd / 2 + x;
                p_dst_ug[dst_ofs_c] = p_src_c[src_ofs_c + 0];
                p_dst_vb[dst_ofs_c] = p_src_c[src_ofs_c + 1];
            }
        }
    } break;
    default: LOGE("%s: unsupported image format %d for now!\n", __func__, src_fmt); return -1;
    }
    return 0;
}

int imgcvt_from_planar_8bit_lsb(uint8_t const *p_src, uint8_t *p_dst, int w, int h, int src_strd, int dst_strd,
    int dst_fmt, bool has_alpha)
{
    assert(p_src != p_dst);
    assert(dst_strd >= w * 1);

    // src format info
    int ret = 0;
    const int bpp = common_verify_imgfmt_bpp(dst_fmt);
    const int frame_size = (w * h * bpp + 7) / 8;
    LOGD("dst fmt: %d(%s), bpp: %d, frame_size: %d\n", dst_fmt, common_verify_imgfmt_str(dst_fmt), bpp, frame_size);
    LOGD("src_strd: %d, dst_strd: %d\n", src_strd, dst_strd);

    int chnl_num = 3;
    int chroma_hgt = (dst_fmt % 10 >= YUV420P) ? h / 2 : h;
    int chroma_wid = (dst_fmt % 10 >= YUV422P) ? w / 2 : w;

    const uint8_t *p_src_yr = p_src;
    const uint8_t *p_src_ug = p_src + src_strd * h;
    const uint8_t *p_src_vb = p_src + src_strd * h * 2;
    const uint8_t *p_src_a = has_alpha ? (p_src + src_strd * h * 3) : NULL;
    LOGT("%s: src u/v offset: %td / %td\n", __func__, p_src_ug - p_src_yr, p_src_vb - p_src_yr);

    switch (dst_fmt) {
    /* 8bit planar lsb data to 8bit normal data */
    case RGBA8888: chnl_num = 4; // NO break here!
    case RGB888:
    case YUV444I:  {
        assert(dst_strd >= w * chnl_num);
        for (int y = 0; y < h; y++) {
            for (int x = 0; x < w; x++) {
                const int src_ofs = y * src_strd + x;
                const int dst_ofs = y * dst_strd + x * chnl_num;
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
    case YUV444P:
    case YUV422P:
    case YUV420P:    {
        assert(dst_strd >= w * 1);
        assert(src_strd == dst_strd);
        memcpy(p_dst, p_src, frame_size);
    } break;
    case YUV444SP: {
        assert(dst_strd >= w * 1);
        uchar *p_dst_y = p_dst;
        uchar *p_dst_c = p_dst + dst_strd * h;
        for (int y = 0; y < h; y++) {
            for (int x = 0; x < w; x++) {
                const int dst_ofs_y = y * dst_strd + x;
                const int dst_ofs_c = y * dst_strd * 2 + x * 2;
                const int src_ofs = y * src_strd + x;
                p_dst_y[dst_ofs_y] = p_src_yr[src_ofs];
                p_dst_c[dst_ofs_c + 0] = p_src_ug[src_ofs];
                p_dst_c[dst_ofs_c + 1] = p_src_vb[src_ofs];
            }
        }
    } break;
    case YUV422SP:
    case YUV420SP: {
        assert(dst_strd >= w * 1);
        assert(src_strd == dst_strd);
        uchar *p_dst_y = p_dst;
        uchar *p_dst_c = p_dst + dst_strd * h;
        memcpy(p_dst_y, p_src_yr, src_strd * h);
        p_src_vb = p_src_ug + src_strd * h / (dst_fmt == YUV422SP ? 2 : 4); // update src_v;
        for (int y = 0; y < chroma_hgt; y++) {
            for (int x = 0; x < chroma_wid; x++) {
                const int dst_ofs_c = y * dst_strd + x * 2;
                const int src_ofs_c = y * src_strd / 2 + x;
                p_dst_c[dst_ofs_c + 0] = p_src_ug[src_ofs_c];
                p_dst_c[dst_ofs_c + 1] = p_src_vb[src_ofs_c];
            }
        }
    } break;
    default: LOGE("%s: unsupported image format %d for now!\n", __func__, dst_fmt); return -1;
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