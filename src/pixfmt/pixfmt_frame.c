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
    frame->size = pixfmt_get_frame_size(frame->fmt, frame->vwid, frame->vhgt, frame->pitch);

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

    size_t size = pixfmt_get_frame_size(frame->fmt, frame->vwid, frame->vhgt, frame->pitch);
    if (frame->size < size) {
        LOGW("invalid frame since frame size=%zu shoule >= %zu for current size!\n", frame->size, size);
        return false;
    }

    return true;
}

void *pixfmt_get_plane_addr(const pixfmt_frame_s *frame, int plane_idx, void *retPlaneAddrsx3)
{
    assert(frame != NULL && frame->fmt != PIXFMT_INVALID);

    if (!frame->addr) {
        LOGE();
        return NULL;
    }

    int nb_planes = pixfmt_nb_planes(frame->fmt);
    if (plane_idx < 0 || plane_idx >= nb_planes) {
        LOGE();
        return NULL;
    }

    if (plane_idx == 0) {
        return frame->addr;
    }

    const pixfmt_attr_s *attr = pixfmt_get_attr(frame->fmt);
    if (attr == NULL) {
        LOGE();
        return NULL;
    }

    size_t offset = 0;

    switch (attr->layout) {
    case PIXFMT_LAYOUT_PLANAR: {
        size_t plane_size = 0;
        int plane_hgt = frame->hgt;

        for (int i = 0; i < plane_idx; i++) {
            int plane_wid = frame->wid;

            if (frame->fmt >= PIXFMT_YUV422P_YU16 && frame->fmt <= PIXFMT_YUV422P_YV16) {
                if (i > 0) {
                    plane_wid = (frame->wid + 1) / 2;
                }
            }
            else if (frame->fmt >= PIXFMT_YUV420P_YU12 && frame->fmt <= PIXFMT_YUV420P_YV12) {
                if (i > 0) {
                    plane_wid = (frame->wid + 1) / 2;
                    plane_hgt = (frame->hgt + 1) / 2;
                }
            }
            else if (frame->fmt >= PIXFMT_YUV411P_YU11 && frame->fmt <= PIXFMT_YUV411P_YV11) {
                if (i > 0) {
                    plane_wid = (frame->wid + 3) / 4;
                }
            }
            else if (frame->fmt >= PIXFMT_YUV410P_YUV9 && frame->fmt <= PIXFMT_YUV410P_YVU9) {
                if (i > 0) {
                    plane_wid = (frame->wid + 3) / 4;
                    plane_hgt = (frame->hgt + 3) / 4;
                }
            }
            else if (frame->fmt >= PIXFMT_YUV444P_YU24 && frame->fmt <= PIXFMT_YUV444P_YV24) {}

            if (i == 0) {
                plane_size = (size_t)frame->pitch * plane_hgt;
            }
            else {
                int uv_sample_ratio_hor = 1;
                if (frame->fmt >= PIXFMT_YUV422P_YU16 && frame->fmt <= PIXFMT_YUV422P_YV16) {
                    uv_sample_ratio_hor = 2;
                }
                else if (frame->fmt >= PIXFMT_YUV420P_YU12 && frame->fmt <= PIXFMT_YUV420P_YV12) {
                    uv_sample_ratio_hor = 2;
                }
                else if (frame->fmt >= PIXFMT_YUV411P_YU11 && frame->fmt <= PIXFMT_YUV411P_YV11) {
                    uv_sample_ratio_hor = 4;
                }
                else if (frame->fmt >= PIXFMT_YUV410P_YUV9 && frame->fmt <= PIXFMT_YUV410P_YVU9) {
                    uv_sample_ratio_hor = 4;
                }

                int uv_pitch = (frame->pitch + uv_sample_ratio_hor - 1) / uv_sample_ratio_hor;
                int uv_hgt = (i > 0 && (frame->fmt >= PIXFMT_YUV420P_YU12 || frame->fmt >= PIXFMT_YUV410P_YUV9))
                               ? ((frame->hgt + 1) / 2)
                               : frame->hgt;
                if (frame->fmt >= PIXFMT_YUV410P_YUV9 && frame->fmt <= PIXFMT_YUV410P_YVU9) {
                    uv_hgt = (frame->hgt + 3) / 4;
                }
                plane_size = (size_t)uv_pitch * uv_hgt;
            }

            offset += plane_size;
        }
        break;
    }

    case PIXFMT_LAYOUT_SEMIPLANAR: {
        size_t y_plane_size = (size_t)frame->pitch * frame->hgt;
        offset = y_plane_size;
        break;
    }

    case PIXFMT_LAYOUT_INTERLEAVED:
    case PIXFMT_LAYOUT_TILE:
    case PIXFMT_LAYOUT_IRREGULAR:
    default:                        offset = 0; break;
    }

    return (uint8_t *)frame->addr + offset;
}

size_t pixfmt_get_plane_size(const pixfmt_frame_s *frame, int plane_idx, size_t *retPlaneSizesx3)
{
    if (frame == NULL) {
        return 0;
    }

    if (plane_idx < 0) {
        return 0;
    }

    int nb_planes = pixfmt_nb_planes(frame->fmt);
    if (plane_idx >= nb_planes) {
        return 0;
    }

    const pixfmt_attr_s *attr = pixfmt_get_attr(frame->fmt);
    if (attr == NULL) {
        return 0;
    }

    size_t plane_size = 0;

    switch (attr->layout) {
    case PIXFMT_LAYOUT_PLANAR: {
        int plane_wid = frame->wid;
        int plane_hgt = frame->hgt;

        if (plane_idx > 0) {
            if (frame->fmt >= PIXFMT_YUV422P_YU16 && frame->fmt <= PIXFMT_YUV422P_YV16) {
                plane_wid = (frame->wid + 1) / 2;
            }
            else if (frame->fmt >= PIXFMT_YUV420P_YU12 && frame->fmt <= PIXFMT_YUV420P_YV12) {
                plane_wid = (frame->wid + 1) / 2;
                plane_hgt = (frame->hgt + 1) / 2;
            }
            else if (frame->fmt >= PIXFMT_YUV411P_YU11 && frame->fmt <= PIXFMT_YUV411P_YV11) {
                plane_wid = (frame->wid + 3) / 4;
            }
            else if (frame->fmt >= PIXFMT_YUV410P_YUV9 && frame->fmt <= PIXFMT_YUV410P_YVU9) {
                plane_wid = (frame->wid + 3) / 4;
                plane_hgt = (frame->hgt + 3) / 4;
            }
        }

        int plane_pitch = frame->pitch;
        if (plane_idx > 0) {
            int uv_sample_ratio_hor = 1;
            if (frame->fmt >= PIXFMT_YUV422P_YU16 && frame->fmt <= PIXFMT_YUV422P_YV16) {
                uv_sample_ratio_hor = 2;
            }
            else if (frame->fmt >= PIXFMT_YUV420P_YU12 && frame->fmt <= PIXFMT_YUV420P_YV12) {
                uv_sample_ratio_hor = 2;
            }
            else if (frame->fmt >= PIXFMT_YUV411P_YU11 && frame->fmt <= PIXFMT_YUV411P_YV11) {
                uv_sample_ratio_hor = 4;
            }
            else if (frame->fmt >= PIXFMT_YUV410P_YUV9 && frame->fmt <= PIXFMT_YUV410P_YVU9) {
                uv_sample_ratio_hor = 4;
            }
            plane_pitch = (frame->pitch + uv_sample_ratio_hor - 1) / uv_sample_ratio_hor;
        }

        plane_size = (size_t)plane_pitch * plane_hgt;
        break;
    }

    case PIXFMT_LAYOUT_SEMIPLANAR: {
        if (plane_idx == 0) {
            plane_size = (size_t)frame->pitch * frame->hgt;
        }
        else {
            int uv_sample_ratio_hor = 1;
            if (frame->fmt >= PIXFMT_YUV422SP_NV16 && frame->fmt <= PIXFMT_YUV422SP_NV61) {
                uv_sample_ratio_hor = 2;
            }
            else if (frame->fmt >= PIXFMT_YUV420SP_NV12 && frame->fmt <= PIXFMT_YUV420SP_NV21) {
                uv_sample_ratio_hor = 2;
            }
            else if (frame->fmt >= PIXFMT_YUV444SP_NV24 && frame->fmt <= PIXFMT_YUV444SP_NV42) {
                uv_sample_ratio_hor = 1;
            }

            int uv_pitch = (frame->pitch + uv_sample_ratio_hor - 1) / uv_sample_ratio_hor;
            plane_size = (size_t)uv_pitch * frame->hgt;
        }
        break;
    }

    case PIXFMT_LAYOUT_INTERLEAVED:
    case PIXFMT_LAYOUT_TILE:
    case PIXFMT_LAYOUT_IRREGULAR:
    default:                        {
        plane_size = frame->size;
        break;
    }
    }

    return plane_size;
}
