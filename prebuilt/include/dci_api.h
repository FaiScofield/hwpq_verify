#ifndef __dci_API_H__
#define __dci_API_H__

#include "rkvop_model_verify_com.h"
// #include "rk3576_vop_regs.h"

typedef void *dci_handle_t;

#define DCI_CLAHE_OVERRIDE_INVALID_INT (-1)
#define DCI_CLAHE_OVERRIDE_INVALID_F32 (-1.0f)

typedef struct {
    int          platform;
    unsigned int debug_dump_mask; // 0 disables temp dumps, ~0ULL keeps all dumps
    char         debug_path[2048];
} dci_init_param_t;

typedef struct {
    int dci_enable;
    int dci_mode; // 1-reg_cfg, 2-kernel_cfg, 3-vop_prop, 4-only_hist, others-json_cfg

    /* io info */
    img_info_t src_info;
    img_info_t dst_info;
    int        is_src_fullrange;
    int        frame_idx;
    int        frame_num;
    // input pixel format (10bit planar) for DCI, see pix_fmt. (PIX_YUV444P_10 or PIX_RGB101010)
    int pixel_format;

    /* config path */
    char config_path[2048];
    char reg_path[2048];

    /* optional CLAHE overrides, keep invalid values to use JSON defaults */
    int   clahe_en;          // valid: 0 or 1, default: 1, invalid: -1
    float clahe_clip_value;  // valid: >= 0.0f, default: 1.0f, invalid: -1
    int   clahe_local_ratio; // valid: [0, 32], default: 19, invalid: -1
    float clahe_abld_ratio;  // valid: [0.0f, 1.0f], default: 0.7f, invalid: -1
    int   clahe_scd_thr_min; // valid: >= 0, default: 0.7f, invalid: -1
    int   clahe_scd_thr_max; // valid: >= 0, default: 3.0f, invalid: -1

} dci_proc_param_t;

#ifdef __cplusplus
extern "C" {
#endif

int dciVerifyInit(dci_handle_t *handle, dci_init_param_t *init_param);

int dciVerifyDeinit(dci_handle_t handle);

int dciVerifyProc(dci_handle_t handle, dci_proc_param_t *proc_params);

#ifdef __cplusplus
}
#endif

#endif /* __dci_API_H__ */
