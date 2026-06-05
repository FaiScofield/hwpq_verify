/**
 * @copyright: Copyright (c) Rockchip Electronics Co., Ltd. 2026-. All rights reserved.
 * @bref:      verify_img_io.h
 * @author:    vance.wu@rock-chips.com
 * @create:    2026-06-05
 * @modifier:  vance.wu@rock-chips.com
 * @modify:    2026-06-05
 */
#ifndef __VERIFY_IMG_IO_H__
#define __VERIFY_IMG_IO_H__

#include "verify_com.h"
#include "verify_img_fmt.h"

#ifdef __cplusplus
extern "C" {
#endif

/********** RAW file image IO functions **********/

// read image data from fp
int image_read(FILE *fp, void *p_buf, int frmidx, int w, int h, int fmt);
// write image data to fp
int image_write(FILE *fp, void *p_buf, int frmidx, int w, int h, int fmt);

// read image data from fp, then convert to U8/U10bit YUV444P or planar RGB
int image_read_to_planar(FILE *fp, void *p_buf, int frmidx, int w, int h, int wstrd, int hstrd, int src_fmt, int depth,
    int dither);
// write 8/10bit image data to fp from U8/U10bit YUV444P or planar RGB
int image_write_from_plannar(FILE *fp, void *p_buf, int frmidx, int w, int h, int wstrd, int hstrd, int dst_fmt,
    int depth, int dither);

// read image data from fp (then shift) to U10bit YUV444P or planar RGB
int image_read_to_10bit_planar(FILE *fp, void *p_buf, int frmidx, int w, int h, int wstrd, int hstrd, int src_fmt, int dither);
// write 10bit image data to fp from U10bit YUV444P or planar RGB
int image_write_from_10bit_plannar(FILE *fp, void *p_buf, int frmidx, int w, int h, int wstrd, int hstrd, int dst_fmt,
    int dither);


// pack an 10bit-lsb image format
int imgcvt_pack_10bit(uint16_t const *p_src, uint8_t *p_dst, int w, int h, int src_strd, int dst_strd, int src_fmt);
// unpack an 10bit-packed image format
int imgcvt_unpack_10bit(uint8_t const *p_src, uint16_t *p_dst, int w, int h, int src_strd, int dst_strd, int src_fmt);

// convert image to 10bit lsb planar format from any 8/10bit input format
int imgcvt_to_planar_10bit_lsb(uint8_t const *p_src, uint16_t *p_dst, int w, int h, int sw_strd, int sh_strd,
    int dw_strd, int dh_strd, int src_fmt, bool has_alpha, int dither);
// convert image to any 10bit output format from 10bit lsb planar format
int imgcvt_from_planar_10bit_lsb(uint16_t const *p_src, uint8_t *p_dst, int w, int h, int sw_strd, int sh_strd,
    int dw_strd, int dh_strd, int dst_fmt, bool has_alpha, int dither);
// convert image to 8bit lsb planar format from any 8bit input format
int imgcvt_to_planar_8bit_lsb(uint8_t const *p_src, uint8_t *p_dst, int w, int h, int sw_strd, int sh_strd, int dw_strd,
    int dh_strd, int src_fmt, bool has_alpha, int dither);
// convert image to any 8bit output format from 8bit lsb planar format
int imgcvt_from_planar_8bit_lsb(uint8_t const *p_src, uint8_t *p_dst, int w, int h, int sw_strd, int sh_strd,
    int dw_strd, int dh_strd, int dst_fmt, bool has_alpha, int dither);


/********** STB image IO functions **********/
bool is_stb_image(const char *filename);
uint8_t *read_stb_image_auto(const char *filename, int *width, int *height, int *channel, int reqChannel); // memory allocated!
int write_stb_image_auto(const char *filename, int width, int height, int channel, const void *data, int pitch);
void free_stb_image_auto(uint8_t *data); // free memory allocated by read_stb_image_auto()

#ifdef __cplusplus
}
#endif

#endif /* __VERIFY_IMG_IO_H__ */