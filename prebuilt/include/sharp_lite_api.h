#ifndef __SHARP_LITE_API_H__
#define __SHARP_LITE_API_H__

#include "rkvop_model_verify_com.h"
#include "rk3576_vop_regs.h"

typedef void* sharp_lite_handle_t;

typedef struct {
    int platform;
    unsigned int debug_dump_mask;
    char debug_path[2048];
} sharp_lite_init_param_t;

typedef struct {
    int sharp_lite_enable;

    /* io info */
    img_info_t src_info;
    img_info_t dst_info;
    int frame_idx;
    int frame_num;

    /* config path */
    char config_path[2048]; // config or reg_bin_file
    int legacy_config_mode; // 1: hw-regs, 2: kernel-driver; other: defualt '.json' config

    int peaking_gain;
} sharp_lite_proc_param_t;

#ifdef __cplusplus
extern "C" {
#endif
int sharpLiteVerifyInit(sharp_lite_handle_t* handle, sharp_lite_init_param_t* init_param);

int sharpLiteVerifyDeinit(sharp_lite_handle_t handle);

int sharpLiteVerifyProc(sharp_lite_handle_t handle, sharp_lite_proc_param_t* proc_params);

#ifdef __cplusplus
}
#endif

#endif /* __SHARP_LITE_API_H__ */
