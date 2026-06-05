/**
 * @copyright:   Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @description: verify_com.c
 * @author:      vance.wu@rock-chips.com
 * @create:      2025-09-12
 * @modifier:    vance.wu@rock-chips.com
 * @modify:      2026-05-25
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

bool starts_with(const char *str, const char *prefix, bool case_sensitive)
{
    if (str == NULL || prefix == NULL) {
        return false;
    }

    size_t str_len = strlen(str);
    size_t prefix_len = strlen(prefix);

    if (prefix_len > str_len) {
        return false;
    }

    if (case_sensitive) {
        return strncmp(str, prefix, prefix_len) == 0;
    }
    else {
#if defined(_WIN32)
        return _strnicmp(str, prefix, prefix_len) == 0;
#else
        return strncasecmp(str, prefix, prefix_len) == 0;
#endif
    }
}

bool ends_with(const char *str, const char *suffix, bool case_sensitive)
{
    if (str == NULL || suffix == NULL) {
        return false;
    }

    size_t str_len = strlen(str);
    size_t suffix_len = strlen(suffix);

    if (suffix_len > str_len) {
        return false;
    }

    const char *str_end = str + str_len - suffix_len;

    if (case_sensitive) {
        return strcmp(str_end, suffix) == 0;
    }
    else {
#if defined(_WIN32)
        return _stricmp(str_end, suffix) == 0;
#else
        return strcasecmp(str_end, suffix) == 0;
#endif
    }
}
