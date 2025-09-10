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

struct crc32_ctx
{
    unsigned int poly;
    unsigned int init;
    unsigned int lut[256];
};


/**
 * @note: the data in RTL is like: [31,24],[23,16],[15,8],[7,0]
 *  but in cmodel is like: [7:0],[15,8],[16,23],[31,24]
 *  so you need to swap data byte by bittrev()
 */
static inline unsigned int bittrev(unsigned int data, int bit_len)
{
    int i;
    unsigned int poly = 0;
    for (i = 0; i < bit_len; i++) {
        if (data & 0x01)
            poly |= 1 << (bit_len - 1 - i);
        data >>= 1;
    }
    return poly;
}

/**
 * @brief: generate crc32 lookup table to accelerate crc calculation
 */
static void gen_crc32_lut(crc_handle handle)
{
    struct crc32_ctx *ctx = (struct crc32_ctx *)handle;
    unsigned int crc;
    unsigned int poly;
    int i, j;
    poly = bittrev(ctx->poly, 32);
    for (i = 0; i < 256; i++) {
        crc = i;
        for (j = 0; j < 8; j++) {
            if (crc & 1) {
                crc = (crc >> 1) ^ poly;
            }
            else {
                crc >>= 1;
            }
        }
        ctx->lut[i] = crc;
    }
}

int common_verify_crc_create(crc_handle *handle)
{
    struct crc32_ctx *ctx = (struct crc32_ctx *)malloc(sizeof(struct crc32_ctx));
    if (ctx) {
        memset(ctx->lut, 0, sizeof(ctx->lut));
        ctx->poly = 0x04c11db7;
        ctx->init = 0xffffffff;
        *handle = (crc_handle)ctx;
        gen_crc32_lut(*handle);
        return 0;
    }
    return -1;
}

int common_verify_crc_release(crc_handle handle)
{
    struct crc32_ctx *ctx = (struct crc32_ctx *)handle;
    if (ctx) {
        free(ctx);
    }
    return 0;
}

int common_verify_crc_calc(crc_handle handle, unsigned char *data, int size)
{
    struct crc32_ctx *ctx = (struct crc32_ctx *)handle;
    unsigned int CRC32 = ctx->init;
    int i;
    unsigned char *pData;
    pData = (unsigned char *)data + size - 1;
    for (i = 0; i < size; i++) {
        CRC32 = ctx->lut[(CRC32 ^ (bittrev(*pData--, 8))) & 0xff] ^ (CRC32 >> 8);
    }
    ctx->init = CRC32;
    return 0;
}

unsigned int common_verify_get_crc_val(crc_handle handle)
{
    struct crc32_ctx *ctx = (struct crc32_ctx *)handle;
    return bittrev(ctx->init, 32);
}

unsigned int get_crc_for_planar_frame_10bit(void *p_buf, int img_w, int img_h, int is_vyu_order)
{
    crc_handle crc_ctx;
    common_verify_crc_create(&crc_ctx);
    for (int i = 0; i < img_h; i++) {
        for (int j = 0; j < img_w; j++) {
            int y_val = *((unsigned short *)p_buf + 0 * img_w * img_h + i * img_w + j);
            int u_val = *((unsigned short *)p_buf + 1 * img_w * img_h + i * img_w + j);
            int v_val = *((unsigned short *)p_buf + 2 * img_w * img_h + i * img_w + j);
            unsigned int crc_tmp = (y_val << 20) + (u_val << 10) + v_val;
            if (is_vyu_order) {
                crc_tmp = (v_val << 20) + (y_val << 10) + u_val; // VYU, same to fpga YCbCr444
            }
            common_verify_crc_calc(crc_ctx, (unsigned char *)&crc_tmp, sizeof(crc_tmp));
        }
    }
    unsigned int crc_result = common_verify_get_crc_val(crc_ctx);
    common_verify_crc_release(crc_ctx);
    return crc_result;
}