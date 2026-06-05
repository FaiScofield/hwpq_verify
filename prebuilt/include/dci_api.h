#ifndef __dci_API_H__
#define __dci_API_H__

#include "rkvop_model_verify_com.h"
// #include "rk3576_vop_regs.h"

typedef void *dci_handle_t;

#define DCI_CLAHE_OVERRIDE_INVALID_INT (-1)
#define DCI_CLAHE_OVERRIDE_INVALID_F32 (-1.0f)

#define DCI_AUDIT_TAG_MAX_LEN  256
#define DCI_AUDIT_PATH_MAX_LEN 2048

#define DCI_AUDIT_NODE_INPUT    (1u << 0)
#define DCI_AUDIT_NODE_CF       (1u << 1)
#define DCI_AUDIT_NODE_HE       (1u << 2)
#define DCI_AUDIT_NODE_CF_HE    (1u << 3)
#define DCI_AUDIT_NODE_BWS      (1u << 4)
#define DCI_AUDIT_NODE_LOCAL    (1u << 5)
#define DCI_AUDIT_NODE_PACK_PRE (1u << 6)

#define DCI_AUDIT_EXPORT_MANIFEST      (1u << 0)
#define DCI_AUDIT_EXPORT_METRICS_JSON  (1u << 1)
#define DCI_AUDIT_EXPORT_CURVES_JSON   (1u << 2)
#define DCI_AUDIT_EXPORT_HISTS_JSON    (1u << 3)
#define DCI_AUDIT_EXPORT_RAW_META_JSON (1u << 4)

typedef struct {
    int          platform;
    unsigned int debug_dump_mask; // 0 disables temp dumps, 0xff keeps all dumps
    char         debug_path[2048];
} dci_init_param_t;

typedef struct {
    int enable_cf_he_ratio_override;
    int cf_he_ratio;
    int enable_bs_set_point_override;
    int bs_set_point;
    int enable_ws_set_point_override;
    int ws_set_point;
    int enable_clahe_local_ratio_override;
    int clahe_local_ratio;
    int enable_clahe_clip_value_override;
    float clahe_clip_value;
} dci_audit_override_t;

typedef struct {
    int                  enable;
    int                  static_only;
    unsigned int         node_mask;
    unsigned int         export_mask;
    char                 tag[DCI_AUDIT_TAG_MAX_LEN];
    char                 working_dir[DCI_AUDIT_PATH_MAX_LEN];
    int                  save_snapshot;
    char                 snapshot_dir[DCI_AUDIT_PATH_MAX_LEN];
    dci_audit_override_t override_cfg;
} dci_audit_param_t;

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
    int        pixel_format; // [O]

    /* config path */
    char config_path[2048];
    char reg_path[2048];

    /* optional parameter overrides, set to invalid values (-1) to use JSON defaults */
    int   clahe_en;          // [0, (1)]
    float clahe_clip_value;  // [0.0f, (1.0f), 2.0f], higher value means higher local effect
    int   clahe_local_ratio; // [0, (19), 32], higher value means higher local effect and less global effect
    float clahe_abld_ratio;  // [0.0f, (0.7), 1.0f], higher value means higher history effect
    int   cf_gain_low;       // 5bit fixed, [0, (32)], 0 means no CF_low  effct
    int   cf_gain_mid;       // 5bit fixed, [0, (32)], 0 means no CF_mid  effct
    int   cf_gain_high;      // 5bit fixed, [0, (32)], 0 means no CF_high effct
    int   cf_he_ratio;       // 6bit fixed, [0, (64)], 0 means no HE effct

    dci_audit_param_t audit;

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
