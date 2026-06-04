#ifndef _DCI_VERIFY_API_H_
#define _DCI_VERIFY_API_H_

#ifdef __cplusplus
extern "C" {
#endif

/* DATA STRUCTURES DEFINITIONS */
#define RKVOP_IMG_MAX_PLANES 4

typedef struct {
    void *ptr;
    int offset;
    int pix_strd;
} plane_info_t;

typedef struct {
    plane_info_t plane_info[RKVOP_IMG_MAX_PLANES];
    int plane_num;
    int img_w[RKVOP_IMG_MAX_PLANES];
    int img_h[RKVOP_IMG_MAX_PLANES];
    int img_ws[RKVOP_IMG_MAX_PLANES];
    int img_hs[RKVOP_IMG_MAX_PLANES];
    int img_bits;
    int is_yuv;
    int is_rgb;
} img_info_t;

/* DCI audit override configuration */
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

/* DCI audit configuration */
typedef struct {
    int enable;
    int static_only;
    int node_mask;
    int export_mask;
    char tag[256];
    char working_dir[2048];
    int save_snapshot;
    char snapshot_dir[2048];
    dci_audit_override_t override_cfg;
} dci_audit_param_t;

/* DCI handle type */
typedef void *dci_handle_t;

/* DCI init parameters */
typedef struct {
    int platform;
    unsigned int debug_dump_mask;
    char debug_path[2048];
} dci_init_param_t;

/* DCI processing parameters */
typedef struct {
    int dci_enable;

    /* io info */
    img_info_t src_info;
    img_info_t dst_info;
    int frame_idx;
    int frame_num;

    /* config paths */
    char config_path[2048];
    char reg_path[2048];

    /* source range */
    int is_src_fullrange;

    /* audit */
    dci_audit_param_t audit;
} dci_proc_param_t;

/* DCI verification API */
int dciVerifyInit(dci_handle_t *handle, dci_init_param_t *init_param);
int dciVerifyDeinit(dci_handle_t handle);
int dciVerifyProc(dci_handle_t handle, dci_proc_param_t *proc_params);

#ifdef __cplusplus
}
#endif
#endif /* _DCI_VERIFY_API_H_ */
