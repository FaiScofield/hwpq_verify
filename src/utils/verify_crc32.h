/**
 * @copyright Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @description: verify_crc32.h
 * @author: vance.wu@rock-chips.com
 * @create: 2025-09-10
 * @history:
 */

#ifndef _VERIFY_CRC32_H_
#define _VERIFY_CRC32_H_

#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Standard CRC-32 (zip/gzip style) */
unsigned int calc_crc32(const void *data, size_t len);

/* RTL-compatible CRC-32 (byte-reversed, bitrev per byte) */
unsigned int calc_crc32_rtl(const void *data, size_t len);

// calc crc value for a 10bit rgb/yuv plannar frame
unsigned int calc_crc32_rtl_10bit_planar(const void *data, int width, int height, int pitch, bool is_vyu_order);

#ifdef __cplusplus
}
#endif
#endif // _VERIFY_CRC32_H_
