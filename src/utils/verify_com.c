/**
 * @copyright Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @description: verify_com.c
 * @author: vance.wu@rock-chips.com
 * @create: 2025-09-05
 * @history:
 *  2025-09-08 vance.wu: Add common macros & functions for commonly usage
 *  2025-09-15 vance.wu: Add function 'dump_regs_to_dat()' for dumping registers to file
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