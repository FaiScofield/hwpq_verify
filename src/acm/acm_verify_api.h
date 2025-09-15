#ifndef _ACM_VERIFY_API_H_
#define _ACM_VERIFY_API_H_

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


typedef void* acm_handle_t;

typedef struct {
    int platform;
    char debug_path[2048];
} acm_init_param_t;

typedef struct {
    int acm_enable;

    /* io info */
    img_info_t src_info;
    img_info_t dst_info;
    int frame_idx;
    int frame_num;

    /* config path */
    char config_path[2048];
} acm_proc_param_t;

int acmVerifyInit(acm_handle_t* handle, acm_init_param_t* init_param);

int acmVerifyDeinit(acm_handle_t handle);

int acmVerifyProc(acm_handle_t handle, acm_proc_param_t* proc_params);

#ifdef __cplusplus
}
#endif
#endif /* _ACM_VERIFY_API_H_ */
