/**
 * @copyright Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @description: verify_crc32.h
 * @author: vance.wu@rock-chips.com
 * @create: 2025-09-10
 * @history:
 */

#ifndef _VERIFY_CRC32_H_
#define _VERIFY_CRC32_H_

#ifdef __cplusplus
extern "C" {
#endif

typedef void *crc_handle;
int common_verify_crc_create(crc_handle *handle);                             // create crc handle
int common_verify_crc_release(crc_handle handle);                             // release crc handle
int common_verify_crc_calc(crc_handle handle, unsigned char *data, int size); // calc crc value of data (one pixel)
unsigned int common_verify_get_crc_val(crc_handle handle);                    // get crc value
unsigned int get_crc_for_planar_frame_10bit(void *p_buf, int img_w, int img_h, int is_vyu_order); // calc crc value for a 10bit plannar frame

#ifdef __cplusplus
}
#endif
#endif // _VERIFY_CRC32_H_
