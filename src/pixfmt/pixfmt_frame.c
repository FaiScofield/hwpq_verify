/**
 * @copyright: Copyright (c) Rockchip Electronics Co., Ltd. 2026-. All rights reserved.
 * @brief:     Image frame implementation
 * @author:    vance.wu@rock-chips.com
 * @create:    2026-04-18
 */

#include "pixfmt_frame.h"
#include "verify_com.h"

#include <assert.h>
#include <string.h>

bool pixfmt_fill_frame_attr(pixfmt_frame_s *frame)
{
    assert(frame != NULL && frame->fmt != PIXFMT_INVALID);

    if (frame->wid <= 4 || frame->hgt <= 2) {
        LOGE("pixfmt_fill_frame_attr: invalid frame size: wid=%d, hgt=%d!\n", frame->wid, frame->hgt);
        return false;
    }

    int row_pitches[3] = {0};
    int ret = pixfmt_get_min_pitches(frame->fmt, frame->wid, row_pitches);
    if (ret != 0) {
        return false;
    }

    frame->clrspc = pixfmt_is_rgb(frame->fmt)
                      ? PIXFMT_CLRSPC_RGB_FULL
                      : (pixfmt_is_yuv(frame->fmt) ? PIXFMT_CLRSPC_YUV_709F : PIXFMT_CLRSPC_UNKNOWN);
    frame->vwid = pixfmt_get_min_align_width(frame->fmt, frame->wid, NULL);
    frame->vhgt = pixfmt_get_min_align_height(frame->fmt, frame->hgt, NULL);
    frame->pitch = row_pitches[0];
    frame->size = pixfmt_get_frame_size(frame->fmt, frame->vwid, frame->vhgt, frame->pitch, NULL);

    return true;
}

bool pixfmt_check_frame_valid(const pixfmt_frame_s *frame)
{
    assert(frame != NULL && frame->fmt != PIXFMT_INVALID);

    // check frame size is valid
    if (frame->wid <= 4 || frame->hgt <= 2) {
        LOGW("invalid frame since frame size %dx%d too small!\n", frame->wid, frame->hgt);
        return false;
    }

    int align_wid = 0;
    const int vwid = pixfmt_get_min_align_width(frame->fmt, frame->wid, &align_wid);
    if (frame->vwid < vwid || (frame->vwid & align_wid) > 0) {
        LOGW("invalid frame since vwid=%d invalid, it should be >= %d and align to %d\n", frame->vwid, vwid, align_wid);
        return false;
    }

    int align_hgt = 0;
    const int vhgt = pixfmt_get_min_align_height(frame->fmt, frame->hgt, &align_hgt);
    if (frame->vhgt < vhgt || (frame->vhgt & align_hgt) > 0) {
        LOGW("invalid frame since vhgt=%d invalid, it should be >= %d and align to %d\n", frame->vhgt, vhgt, align_hgt);
        return false;
    }

    // check memory size is enough
    if (frame->addr == NULL && frame->fd < 0) {
        LOGW("invalid frame since none of frame addr=%p or fd=%d is valid!\n", frame->addr, frame->fd);
        return false;
    }

    size_t size = pixfmt_get_frame_size(frame->fmt, frame->vwid, frame->vhgt, frame->pitch, NULL);
    if (frame->size < size) {
        LOGW("invalid frame since frame size=%zu shoule >= %zu for current size!\n", frame->size, size);
        return false;
    }

    return true;
}

void *pixfmt_get_plane_addr(const pixfmt_frame_s *frame, int plane_idx, void **retPlaneAddrsx3)
{
    assert(frame != NULL && frame->fmt != PIXFMT_INVALID);

    if (!frame->addr) {
        LOGE("frame addr is NULL!\n");
        return NULL;
    }

    const int nb_planes = pixfmt_nb_planes(frame->fmt);
    if ((plane_idx < 0 && !retPlaneAddrsx3) || plane_idx >= nb_planes) {
        LOGE("invalid plane_idx=%d, since nb_planes=%d!\n", plane_idx, nb_planes);
        return NULL;
    }

    if (plane_idx == 0)
        return frame->addr;

    size_t plane_sizes[3] = {0};
    pixfmt_get_plane_size(frame, -1, plane_sizes);

    size_t offset = 0;
    for (int i = 0; i < plane_idx; i++) {
        offset += plane_sizes[i];
    }

    if (retPlaneAddrsx3) {
        retPlaneAddrsx3[0] = frame->addr;
        retPlaneAddrsx3[1] = (nb_planes > 1) ? ((uint8_t *)retPlaneAddrsx3[0] + plane_sizes[0]) : NULL;
        retPlaneAddrsx3[2] = (nb_planes > 2) ? ((uint8_t *)retPlaneAddrsx3[1] + plane_sizes[1]) : NULL;
    }

    return (uint8_t *)frame->addr + offset;
}

size_t pixfmt_get_plane_size(const pixfmt_frame_s *frame, int plane_idx, size_t *retPlaneSizesx3)
{
    if (frame == NULL) {
        return 0;
    }

    if (plane_idx < 0 && !retPlaneSizesx3) {
        LOGW();
        return 0;
    }

    int nb_planes = pixfmt_nb_planes(frame->fmt);
    if (plane_idx >= nb_planes) {
        return 0;
    }

    size_t plane_sizes[3] = {0};
    pixfmt_get_frame_size(frame->fmt, frame->vwid, frame->vhgt, frame->pitch, plane_sizes);

    if (retPlaneSizesx3)
        memcpy(retPlaneSizesx3, plane_sizes, sizeof(plane_sizes));

    return plane_sizes[plane_idx];
}

void pixfmt_dump_frame_attr(const pixfmt_frame_s *frame)
{
    LOGI(" - pixel format: %d (%s)\n", frame->fmt, pixfmt_full_name(frame->fmt));
    LOGI(" - colorspace:   %d (%s)\n", frame->clrspc, pixfmt_colorspcae_name(frame->clrspc));
    LOGI(" - real size:    %dx%d [pixel]\n", frame->wid, frame->hgt);
    LOGI(" - virtual size: %dx%d [pixel]\n", frame->vwid, frame->vhgt);
    LOGI(" - row pitch:    %d [byte]\n", frame->pitch);
    LOGI(" - mem address:  %p, mem size: %zu [byte]\n", frame->addr, frame->size);
    LOGI(" - mem fd:       %d, mem offset: %d [byte]\n", frame->fd, frame->offset);
}
