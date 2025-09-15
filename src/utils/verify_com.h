/**
 * @copyright Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @description: verify_com.h
 * @author: vance.wu@rock-chips.com
 * @create: 2025-09-05
 * @history:
 *  2025-09-08 vance.wu: Add common macros & functions for commonly usage
 *  2025-09-15 vance.wu: Add pixel format pack/unpack functions
 */

#ifndef _VERIFY_COM_H_
#define _VERIFY_COM_H_

#include <stdbool.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32
#include <direct.h>
#define acess       _access
#define mkdir(a, b) _mkdir(a)
#else
#include <sys/stat.h>
#endif


/********** type define **********/
typedef unsigned char uchar;
typedef unsigned short ushort;
typedef unsigned int uint;
typedef unsigned long ulong;
typedef unsigned long long ullong;


/********** macros for logging **********/
#define LOG_TAG "Hwpq_Verify"
#if ENABLE_SPDLOG
#define SPDLOG_ACTIVE_LEVEL SPDLOG_LEVEL_TRACE
#include <spdlog/spdlog.h>
static char g_logbuf[2048];
#define PRINTF2SPDLOG(fmt, ...) snprintf(g_logbuf, 2048, "[" LOG_TAG "] " fmt, ##__VA_ARGS__)
#define LOGT(fmt, ...)          PRINTF2SPDLOG(fmt, ##__VA_ARGS__), SPDLOG_TRACE(g_logbuf)
#define LOGD(fmt, ...)          PRINTF2SPDLOG(fmt, ##__VA_ARGS__), SPDLOG_DEBUG(g_logbuf)
#define LOGI(fmt, ...)          PRINTF2SPDLOG(fmt, ##__VA_ARGS__), SPDLOG_INFO(g_logbuf)
#define LOGW(fmt, ...)          PRINTF2SPDLOG(fmt, ##__VA_ARGS__), SPDLOG_WARN(g_logbuf)
#define LOGE(fmt, ...)          PRINTF2SPDLOG(fmt, ##__VA_ARGS__), SPDLOG_ERROR(g_logbuf)
#elif defined(__ANDROID__)
#include <android/log.h>
#define LOGT(fmt, ...) __android_log_print(ANDROID_LOG_VERBOSE, LOG_TAG, fmt, ##__VA_ARGS__)
#define LOGD(fmt, ...) __android_log_print(ANDROID_LOG_DEBUG, LOG_TAG, fmt, ##__VA_ARGS__)
#define LOGI(fmt, ...) __android_log_print(ANDROID_LOG_INFO, LOG_TAG, fmt, ##__VA_ARGS__)
#define LOGW(fmt, ...) __android_log_print(ANDROID_LOG_WARN, LOG_TAG, fmt, ##__VA_ARGS__)
#define LOGE(fmt, ...) __android_log_print(ANDROID_LOG_ERROR, LOG_TAG, fmt, ##__VA_ARGS__)
#else // not ANDROID OS, use printf
#define LOGT(fmt, ...) printf("V [" LOG_TAG "] " fmt, ##__VA_ARGS__)
#define LOGD(fmt, ...) printf("D [" LOG_TAG "] " fmt, ##__VA_ARGS__)
#define LOGI(fmt, ...) printf("I [" LOG_TAG "] " fmt, ##__VA_ARGS__)
#define LOGW(fmt, ...) printf("W [" LOG_TAG "] " fmt, ##__VA_ARGS__)
#define LOGE(fmt, ...) printf("E [" LOG_TAG "] " fmt, ##__VA_ARGS__)
#endif // #ifdef ANDROID

/********** common macros **********/
/* alignment */
#define ALIGN_2(x)         (((x) + 1) & (~1))
#define ALIGN_4(x)         (((x) + 3) & (~3))
#define ALIGN_8(x)         (((x) + 7) & (~7))
#define ALIGN_16(x)        (((x) + 15) & (~15))
#define ALIGN_32(x)        (((x) + 31) & (~31))
#define ALIGN_64(x)        (((x) + 63) & (~63))
#define ALIGN_128(x)       (((x) + 127) & (~127))
#define ALIGN_N(x, n)      (((x) + ((n) - 1)) & (~((n) - 1))) // n > 0
#define ALIGN_N_DIV(x, n)  (((x) + ((n) - 1)) / (n) * (n))

/* minimum, maximum, clip */
#define MAX(a, b)          ((a) > (b) ? (a) : (b))
#define MIN(a, b)          ((a) < (b) ? (a) : (b))
#define MAX2(a, b)         MAX(a, b)
#define MIN2(a, b)         MIN(a, b)
#define MAX3(a, b, c)      MAX(MAX(a, b), c)
#define MIN3(a, b, c)      MIN(MIN(a, b), c)
#define MAX4(a, b, c, d)   MAX(MAX(a, b), MAX(c, d))
#define MIN4(a, b, c, d)   MIN(MIN(a, b), MIN(c, d))
#define CLIP(x, a, b)      MIN(MAX(x, a), b)
#define CLAMP(x, a, b)     CLIP(x, a, b)

/* absolute value */
#define ABS_S8(x)          (char)((x) + ((x) >> 7)) ^ (((x) >> 7)) // without branching
#define ABS_U8(x)          (uchar)((x) + ((x) >> 7)) ^ (((x) >> 7))
#define ABS_S16(x)         (short)((x) + ((x) >> 15)) ^ (((x) >> 15))
#define ABS_U16(x)         (ushort)((x) + ((x) >> 15)) ^ (((x) >> 15))
#define ABS_S32(x)         (int)((x) + ((x) >> 31)) ^ (((x) >> 31))
#define ABS_U32(x)         (uint)((x) + ((x) >> 31)) ^ (((x) >> 31))
#define ABS_F32(x)         (float)((x) > 0 ? (x) : (-(x)))
#define ABS_F64(x)         (double)((x) > 0 ? (x) : (-(x)))
#define ABS(x)             ABS_S32(x)
#define ABSF(x)            ABS_F32(x)

/* rounding */
#define ROUND_U(x)         ((float)(x) + 0.5f)
#define ROUND_F(x)         ((x) > 0 ? ((float)(x) + 0.5f) : ((float)(x) - 0.5f))
#define ROUND_D(x)         ((x) > 0 ? ((double)(x) + 0.5) : ((double)(x) - 0.5))
#define ROUND_U8(x)        (uchar) ROUND_U(x)
#define ROUND_U16(x)       (ushort) ROUND_U(x)
#define ROUND_U32(x)       (uint) ROUND_U(x)
#define ROUND_S8(x)        (char)ROUND_F(x)
#define ROUND_S16(x)       (short)ROUND_F(x)
#define ROUND_S32(x)       (int)ROUND_F(x)
#define ROUND_F32(x)       ROUND_F(x)
#define ROUND_F64(x)       ROUND_D(x)

/**
 * Bit Twiddling Hacks
 * @see https://graphics.stanford.edu/~seander/bithacks.html
 */
#define SIGN_I8(x)         (+1 | ((x) >> 7))  // if v < 0 then -1, else +1
#define SIGN_I16(x)        (+1 | ((x) >> 15)) // if v < 0 then -1, else +1
#define SIGN_I32(x)        (+1 | ((x) >> 31)) // if v < 0 then -1, else +1
#define SIGN_I64(x)        (+1 | ((x) >> 63)) // if v < 0 then -1, else +1
#define SIGN(x)            SIGN_I32(x)
#define SIGN_BIT(x)        (((int)(x) >> 31) & 0x1) // if v < 0 then +1 else 0
#define IS_POSITIVE(x)     (((int)(x) >> 31) ^ 1)   // if v > 0 then 1 else 0
#define IF_DIFF_SIGN(x, y) (((x) ^ (y)) < 0)        // true if x and y have opposite signs

#define IS_POWER_OF_2(x)   (((x) & -(x)) == (x)).


/********** directory / file functions **********/
bool is_directory(const char *path);
bool is_regular_file(const char *path);
const char *get_dirname(const char *path);
const char *get_basename(const char *path);


/********** image io functions **********/
#include "verify_img_fmt.h"

// read image data from fp then shift to U10bit YUV444P or planar RGB
int image_read_to_10bit_planar(FILE *fp, void *p_buf, int frmidx, int w, int h, int fmt);
// read image data from fp
int image_read(FILE *fp, void *p_buf, int frmidx, int w, int h, int fmt);
// write image data to fp
int image_write(FILE *fp, void *p_buf, int frmidx, int w, int h, int fmt);

int imgcvt_pack_10bit(uint16_t *p_src, uint8_t *p_dst, int w, int h, int src_strd, int dst_strd, int fmt);
int imgcvt_unpack_10bit(uint8_t *p_src, uint16_t *p_dst, int w, int h, int src_strd, int dst_strd, int fmt);


// dump regisers data to a file or stdout, with 4 registers in each row
void dump_regs_to_dat(const char *filename, uint const *regs, int nb_regs, uint start_addr);

#endif /* _VERIFY_COM_H_ */