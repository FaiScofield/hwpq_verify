#ifndef __SHARP_FULL_API_H__
#define __SHARP_FULL_API_H__

#include "rkvop_model_verify_com.h"
// #include "rk3576_vop_regs.h"

typedef void* sharp_full_handle_t;

typedef struct {
    int platform;
    unsigned int debug_dump_mask; // 0 disables temp dumps, 0xff keeps all dumps
    char debug_path[2048];
} sharp_full_init_param_t;

typedef struct {
    int sharp_full_enable;
    int sharp_full_mode; // 0: json, 1: reg

    /* io info */
    img_info_t src_info;
    img_info_t dst_info;
    int frame_idx;
    int frame_num;

    /* config path */
    char config_path[2048];

    int peaking_gain;

} sharp_full_proc_param_t;

int sharpFullVerifyInit(sharp_full_handle_t* handle, sharp_full_init_param_t* init_param);

int sharpFullVerifyDeinit(sharp_full_handle_t handle);

int sharpFullVerifyProc(sharp_full_handle_t handle, sharp_full_proc_param_t* proc_params);

#endif /* __SHARP_FULL_API_H__ */
