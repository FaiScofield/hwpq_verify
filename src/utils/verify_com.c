/**
 * @copyright Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @description: verify_com.c
 * @author: vance.wu@rock-chips.com
 * @create: 2025-09-05
 * @history:
 *  2025-09-08 vance.wu: Add common macros & functions for commonly usage
 *  2025-09-15 vance.wu: Add pixel format pack/unpack functions
 */

#include "verify_com.h"

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

bool is_directory(const char *path)
{
    DWORD attr = GetFileAttributes(path);
    if (attr == INVALID_FILE_ATTRIBUTES) {
        DWORD err = GetLastError();
        LOGE("GetFileAttributes(%s) failed! error code: %d - %s\n", path, (int)err, errcode2str(err));
        return -1;
    }
    return (attr & FILE_ATTRIBUTE_DIRECTORY) != 0;
}

bool is_regular_file(const char *path)
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

bool is_directory(const char *path)
{
    struct stat statbuf;
    if (lstat(path, &statbuf) != 0) {
        LOGE("%s: call lstat failed! %s\n", __func__, strerror(errno));
        return -1;
    }
    return S_ISDIR(statbuf.st_mode);
}

bool is_regular_file(const char *path)
{
    struct stat statbuf;
    if (lstat(path, &statbuf) != 0) {
        LOGE("%s: call lstat failed! %s\n", __func__, strerror(errno));
        return -1;
    }
    return S_ISREG(statbuf.st_mode);
}

const char *get_dirname(const char *path)
{
    return dirname((char *)path);
}

const char *get_basename(const char *path)
{
    return basename((char *)path);
}
#endif


/********** image io functions **********/
int image_read_to_10bit_planar(FILE *fp, void *p_buf, int frmidx, int w, int h, int fmt)
{
    if (!fp || !p_buf) {
        LOGE("invalid fp or output buffer!\n");
        return -1;
    }
    if (frmidx < 0 || w <= 0 || h <= 0 || !common_verify_imgfmt_check(fmt)) {
        LOGE("invalid argument! frmidx: %d, w: %d, h: %d, fmt: %d %s\n", frmidx, w, h, fmt, common_verify_imgfmt_str(fmt));
        return -1;
    }

    const int plane_elems = w * h;
    const int bpp = common_verify_imgfmt_bpp(fmt);
    const int frame_size = (w * h * bpp + 7) / 8;
    LOGD("fmt: %d(%s), bpp: %d, frame_size: %d, plane_elems: %d,\n", fmt, common_verify_imgfmt_str(fmt), bpp,
        frame_size, plane_elems);

    ushort *p_dst_yr = (ushort *)p_buf;
    ushort *p_dst_ug = (ushort *)p_buf + plane_elems;
    ushort *p_dst_vb = (ushort *)p_buf + plane_elems * 2;
    ushort *p_dst_a = (ushort *)p_buf + plane_elems * 3;
    uchar *p_temp = (uchar *)malloc(frame_size);
    fseek(fp, frame_size * frmidx, SEEK_SET);
    size_t read_size = fread(p_temp, 1, frame_size, fp);
    if (read_size != frame_size) {
        LOGE("readSize(%zu) != frameSize(%d) for frame#%d format %d!\n", read_size, frame_size, frmidx, fmt);
        return -1;
    }

    switch (fmt) {
    case RGB_PLANAR:
    case YUV444P:    {
        for (int i = 0; i < frame_size; i++) {
            ((ushort *)p_buf)[i] = (p_temp[i] << 2) & 0x3ff;
        }
    } break;
    case YUV444SP: {
        uchar *p_src_y = p_temp;
        uchar *p_src_uv = p_temp + plane_elems;
        for (int i = 0; i < plane_elems; i++) {
            int j = i * 2;
            p_dst_yr[i] = (p_src_y[i] << 2) & 0x3ff;
            p_dst_ug[i] = (p_src_uv[j + 0] << 2) & 0x3ff;
            p_dst_vb[i] = (p_src_uv[j + 1] << 2) & 0x3ff;
        }
    } break;
    case YUV444I:
    case RGB888:  {
        for (int i = 0; i < plane_elems; i++) {
            const int j = i * 3;
            p_dst_yr[i] = (p_temp[j + 0] << 2) & 0x3ff;
            p_dst_ug[i] = (p_temp[j + 1] << 2) & 0x3ff;
            p_dst_vb[i] = (p_temp[j + 2] << 2) & 0x3ff;
        }
    } break;
    case RGBA8888: {
        for (int i = 0; i < plane_elems; i++) {
            const int j = i * 4;
            p_dst_yr[i] = (p_temp[j + 0] << 2) & 0x3ff;
            p_dst_ug[i] = (p_temp[j + 1] << 2) & 0x3ff;
            p_dst_vb[i] = (p_temp[j + 2] << 2) & 0x3ff;
            p_dst_a[i] = (p_temp[j + 3] << 2) & 0x3ff;
        }
    } break;
    case RGB_PLANAR10LSB:
    case YUV444P_10LSB:   memcpy(p_buf, p_temp, frame_size); break;
    case YUV444SP_10LSB:  {
        ushort *p_src_y = (ushort *)p_temp;
        ushort *p_src_uv = (ushort *)p_temp + plane_elems;
        for (int i = 0; i < plane_elems; i++) {
            int j = i * 2;
            p_dst_yr[i] = p_src_y[i] & 0x3ff;
            p_dst_ug[i] = p_src_uv[j + 0] & 0x3ff;
            p_dst_vb[i] = p_src_uv[j + 1] & 0x3ff;
        }
    } break;
    case RGB_101010LSB:
    case YUV444I_10LSB: {
        for (int i = 0; i < plane_elems; i++) {
            const int j = i * 3;
            p_dst_yr[i] = ((ushort *)p_temp)[j + 0] & 0x3ff;
            p_dst_ug[i] = ((ushort *)p_temp)[j + 1] & 0x3ff;
            p_dst_vb[i] = ((ushort *)p_temp)[j + 2] & 0x3ff;
        }
    } break;
    case RGBA_1010102: {
        for (int i = 0; i < plane_elems; i++) {
            const uint val = ((uint *)p_temp)[i];
            p_dst_yr[i] = (val >> 22) & 0x3ff;
            p_dst_ug[i] = (val >> 12) & 0x3ff;
            p_dst_vb[i] = (val >> 2) & 0x3ff;
        }
    } break;
    default: LOGE("unsupported image format %d for now!\n", fmt); return -1;
    }

    free(p_temp);
    return 0;
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

int imgcvt_pack_10bit(uint16_t *p_src, uint8_t *p_dst, int w, int h, int src_strd, int dst_strd, int fmt)
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
    default: LOGE("unsupported image format %d case to pack !\n", fmt); return -1;
    }
    return 0;
}

int imgcvt_unpack_10bit(uint8_t *p_src, uint16_t *p_dst, int w, int h, int src_strd, int dst_strd, int fmt)
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
    default: LOGE("unsupported image format %d case to pack !\n", fmt); return -1;
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