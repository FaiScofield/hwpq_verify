/**
 * @copyright Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @description: verify_crc32.c
 * @author: vance.wu@rock-chips.com
 * @create: 2025-09-10
 * @history:
 */

#include "verify_crc32.h"

#include <stdlib.h>
#include <string.h>

#define CRC32_TABLE_SIZE         256

/* Standard CRC-32 (zip/gzip style) */
#define CRC32_INIT               0xFFFFFFFF
#define CRC32_POLY_REFLECTED     0x04C11DB7

/* RTL-compatible CRC-32 (byte-reversed, bitrev per byte) */
#define CRC32_RTL_INIT           0xFFFFFFFF
#define CRC32_RTL_POLY_REFLECTED 0xEDB88320

typedef unsigned char uint8_t;
typedef unsigned short uint16_t;
typedef unsigned int uint32_t;

/**
 * @note: the data in RTL is like: [31,24],[23,16],[15,8],[7,0]
 *  but in cmodel is like: [7:0],[15,8],[16,23],[31,24]
 *  so you need to swap data byte by bittrev()
 */
static inline uint32_t bittrev(uint32_t data, int bit_len)
{
    int i;
    uint32_t poly = 0;
    for (i = 0; i < bit_len; i++) {
        if (data & 0x01)
            poly |= 1 << (bit_len - 1 - i);
        data >>= 1;
    }
    return poly;
}

/**
 * @brief: calc CRC32 in RTL-compatible mode (byte-reversed order, bitrev per byte)
 *   The algorithm matches hardware (RTL) behavior: process data from end to
 *   start, apply bittrev to each byte, and bittrev the final result.
 */
uint32_t calc_crc32_rtl(const void *data, size_t len)
{
    static uint32_t table[CRC32_TABLE_SIZE];
    static int inited = 0;
    const unsigned char *p = (const unsigned char *)data;
    uint32_t crc = CRC32_RTL_INIT;
    int i;

    if (!inited) {
        for (i = 0; i < CRC32_TABLE_SIZE; i++) {
            uint32_t c = i;
            for (int j = 0; j < 8; j++)
                c = (c >> 1) ^ (c & 1 ? CRC32_RTL_POLY_REFLECTED : 0);
            table[i] = c;
        }
        inited = 1;
    }

    p = p + len - 1;
    for (i = 0; i < (int)len; i++)
        crc = table[(crc ^ bittrev(*p--, 8)) & 0xFF] ^ (crc >> 8);

    return bittrev(crc, 32);
}

uint32_t calc_crc32_rtl_10bit_planar(const void *data, int width, int height, int pitch, bool is_vyu_order)
{
    const int pixel_count = width * height;
    uint32_t *u32_data = (uint32_t *)malloc(pixel_count * sizeof(uint32_t));
    if (!u32_data)
        return 0;

    int idx = 0;
    for (int i = 0; i < height; i++) {
        const uint16_t *row_yr = (const uint16_t *)((uint8_t *)data + 0 * pitch * height + i * pitch);
        const uint16_t *row_ug = (const uint16_t *)((uint8_t *)data + 1 * pitch * height + i * pitch);
        const uint16_t *row_vb = (const uint16_t *)((uint8_t *)data + 2 * pitch * height + i * pitch);
        for (int j = 0; j < width; j++) {
            const uint32_t yr = row_yr[j];
            const uint32_t ug = row_ug[j];
            const uint32_t vb = row_vb[j];
            // VYU, same to fpga YCbCr444
            const uint32_t u32_pix = is_vyu_order ? ((vb << 20) + (yr << 10) + ug) : ((yr << 20) + (ug << 10) + vb);
            u32_data[idx++] = u32_pix;
        }
    }

    uint32_t crc_result = calc_crc32_rtl(u32_data, pixel_count * sizeof(uint32_t));
    free(u32_data);
    return crc_result;
}

uint32_t calc_crc32(const void *data, size_t len)
{
    const unsigned char *p = (const unsigned char *)data;
    uint32_t crc = CRC32_INIT;
    static uint32_t table[CRC32_TABLE_SIZE];
    static int inited = 0;
    int i;

    if (!inited) {
        for (i = 0; i < CRC32_TABLE_SIZE; i++) {
            uint32_t c = i;
            for (int j = 0; j < 8; j++)
                c = (c >> 1) ^ (c & 1 ? CRC32_POLY_REFLECTED : 0);
            table[i] = c;
        }
        inited = 1;
    }

    for (i = 0; i < (int)len; i++)
        crc = table[(crc ^ p[i]) & 0xFF] ^ (crc >> 8);

    return crc ^ CRC32_INIT;
}