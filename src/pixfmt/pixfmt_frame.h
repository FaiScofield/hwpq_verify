/**
 * @copyright: Copyright (c) Rockchip Electronics Co., Ltd. 2026-. All rights reserved.
 * @brief:     Image frame definition
 * @author:    vance.wu@rock-chips.com
 * @create:    2026-04-18
 */

#ifndef _PIXFMT_FRAME_H_
#define _PIXFMT_FRAME_H_

#include "pixfmt.h"
#include "pixfmt_color_cvt.h"

#include <stddef.h>

/**
 * @brief: Image frame structure
 * @note: the attributes marked as [I/O] can be filled by function `pixfmt_fill_frame_attr()`
 */
typedef struct pixfmt_frame {
    pixfmt_e fmt;               // [I]
    pixfmt_colorspcae_e clrspc; // [I/O] set to RGBF/709F when fill

    int wid;   // [I] width, unit: pixel
    int hgt;   // [I] height, unit: pixel
    int vwid;  // [I/O] virtual width, unit: pixel
    int vhgt;  // [I/O] virtual height, unit: pixel
    int pitch; // [I/O] row pitch, unit: byte

    void *addr;  // [I]
    int fd;      // [I]
    int offset;  // [I]
    size_t size; // [I/O]
} pixfmt_frame_s;


/// @brief: Fill vwid/vhgt/pitch/size when given fmt/wid/hgt
extern bool pixfmt_frame_fill(pixfmt_frame_s *frame);

/// @brief: Check if the frame attributes are valid
extern bool pixfmt_frame_check(const pixfmt_frame_s *frame);

/// @brief: Get the plane address/size from given plane index
extern void *pixfmt_frame_get_addr(const pixfmt_frame_s *frame, int plane_idx, void **retPlaneAddrsx3);
extern size_t pixfmt_frame_get_size(const pixfmt_frame_s *frame, int plane_idx, size_t *retPlaneSizesx3);
extern int pixfmt_frame_get_align_width(pixfmt_e fmt, int wid, int *retAlign);
extern int pixfmt_frame_get_align_height(pixfmt_e fmt, int hgt, int *retAlign);
extern int pixfmt_frame_get_min_pitches(pixfmt_e fmt, int wid, int *retPitchesx3);

/// @brief: Dump the frame attributes
extern void pixfmt_frame_dump_info(const pixfmt_frame_s *frame);
extern void pixfmt_frame_dump_data(const pixfmt_frame_s *frame, const char *filename);

#endif /* _PIXFMT_FRAME_H_ */