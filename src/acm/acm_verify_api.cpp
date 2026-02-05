#include <string.h>
#include <stdio.h>
#include <stdlib.h>

#include "acm_verify_api.h"
#include "verify_com.h"
// #include "rkpq_acm.h"

// #include "rkvop_register.h"
// #include "rkvop_cfg_parameter.h"

typedef struct
{
    int platform;
    int status;
    // rkvop_pq_acm *acm_proc_handle;

    // struct rkvop_register_global vop_glb_regs;
    acm_proc_param_t proc_configs;

    // rkvop_interface p_interface_src;
    // rkvop_interface p_interface_dst;
    // debug_para_t debug_params;

} acm_ctx_t;

int acmVerifyInit(acm_handle_t *handle, acm_init_param_t *init_param)
{
    // LOGD_FUNC_IN();

    /* allocate memory for acm context */
    acm_ctx_t *ctx = (acm_ctx_t *)malloc(sizeof(acm_ctx_t));
    memset(ctx, 0, sizeof(acm_ctx_t));
    if (ctx == NULL) {
        LOGE("acmVerifyInit malloc failed");
        ctx->status = -1;
        return -1;
    }
    *handle = (acm_handle_t)ctx;
    LOGD("acmVerifyInit handle: %p\n", ctx);

    ctx->platform = init_param->platform;
    ctx->status = 0;
    // sprintf(ctx->debug_params.pathReslut, "%s", init_param->debug_path);
    // sprintf(ctx->debug_params.pathReslut_byname, "%s", init_param->debug_path);
    // sprintf(ctx->debug_params.crc_result_path, "%s", init_param->debug_path);
    // LOGD("acmVerifyInit debug_path: %s\n", ctx->debug_params.pathReslut);

    // ctx->acm_proc_handle = new rkvop_pq_acm();
    // ctx->acm_proc_handle->pDebugParas = &ctx->debug_params;
    // LOGD("acmVerifyInit new acm class, handle: %p\n", ctx->acm_proc_handle);

    // LOGD_FUNC_OUT();
    return 0;
}

int acmVerifyDeinit(acm_handle_t handle)
{
    // LOGD_FUNC_IN();

    /* delete acm class */
    // delete ((acm_ctx_t *)handle)->acm_proc_handle;
    LOGD("acmVerifyDeinit delete acm class\n");

    /* free acm context */
    if (handle == NULL) {
        LOGE("acmVerifyDeinit handle is NULL\n");
        return -1;
    }
    free(handle);

    // LOGD_FUNC_OUT();
    return 0;
}

int acmVerifyProc(acm_handle_t handle, acm_proc_param_t *proc_params)
{
#if 0
    // LOGD_FUNC_IN();
    acm_ctx_t *ctx = (acm_ctx_t *)handle;
    LOGD("acmVerifyProc handle: %p\n", handle);
    LOGI("acmVerifyProc platform: %d\n", ctx->platform);

    /* copy proc_params to ctx */
    memcpy(&ctx->proc_configs, proc_params, sizeof(acm_proc_param_t));
    RK_S16 *p_acm_LUT2D_HY = NULL; // HY Gain 9 * 17 * 3 * s8, range: [-128, 127]
    RK_S16 *p_acm_LUT2D_HS = NULL; // HS Gain 13 * 17 * 3 * s8, range: [-128, 127]
    RK_S16 *p_acm_H_map = NULL;    // YHS delta, 3 * 65, precision: s9/s7/s9, range: [-256, 255]/[-64, 63]/[-256, 255]

    ctx->vop_glb_regs.rgs_pq_acm.acm_reg_cfg_mode = proc_params->mode;
    if (proc_params->mode >= 1 && proc_params->mode <= 2) {
        strncpy(ctx->vop_glb_regs.rgs_pq_acm.acm_reg_file_path, proc_params->config_path, 1024);
    }
    else {
        /* parse config parameters */
        rkvop_cfg_parameter cfg_param(proc_params->config_path);

        // acm buffer malloc
        MALLOC(p_acm_LUT2D_HY, RK_S16, RKVOP_PQ_ACM_CHANNEL_NUMBER * RKVOP_PQ_ACM_YLUT_LENGTH * RKVOP_PQ_ACM_HLUT_DOWN_LENGTH);
        MALLOC(p_acm_LUT2D_HS, RK_S16, RKVOP_PQ_ACM_CHANNEL_NUMBER * RKVOP_PQ_ACM_SLUT_LENGTH * RKVOP_PQ_ACM_HLUT_DOWN_LENGTH);
        MALLOC(p_acm_H_map, RK_S16, RKVOP_PQ_ACM_CHANNEL_NUMBER * RKVOP_PQ_ACM_HLUT_LENGTH);
        const RK_U16 g_acm_ATAN_LUT[14] = {11520, 6801, 3593, 1824, 916, 458, 229, 115, 57, 29, 14, 7, 4, 2};

        ctx->vop_glb_regs.rgs_pq_acm.acm_enable = cfg_param.ACM.acmEnable;
        memcpy(p_acm_H_map + 0 * RKVOP_PQ_ACM_HLUT_LENGTH, cfg_param.ACM.acmTableDeltaYbyH,
            sizeof(RK_S16) * RKVOP_PQ_ACM_HLUT_LENGTH);
        memcpy(p_acm_H_map + 1 * RKVOP_PQ_ACM_HLUT_LENGTH, cfg_param.ACM.acmTableDeltaHbyH,
            sizeof(RK_S16) * RKVOP_PQ_ACM_HLUT_LENGTH);
        memcpy(p_acm_H_map + 2 * RKVOP_PQ_ACM_HLUT_LENGTH, cfg_param.ACM.acmTableDeltaSbyH,
            sizeof(RK_S16) * RKVOP_PQ_ACM_HLUT_LENGTH);
        memcpy(p_acm_LUT2D_HY + 0 * RKVOP_PQ_ACM_YLUT_LENGTH * RKVOP_PQ_ACM_HLUT_DOWN_LENGTH,
            cfg_param.ACM.acmTableGainYbyY, sizeof(RK_S16) * RKVOP_PQ_ACM_YLUT_LENGTH * RKVOP_PQ_ACM_HLUT_DOWN_LENGTH);
        memcpy(p_acm_LUT2D_HY + 1 * RKVOP_PQ_ACM_YLUT_LENGTH * RKVOP_PQ_ACM_HLUT_DOWN_LENGTH,
            cfg_param.ACM.acmTableGainHbyY, sizeof(RK_S16) * RKVOP_PQ_ACM_YLUT_LENGTH * RKVOP_PQ_ACM_HLUT_DOWN_LENGTH);
        memcpy(p_acm_LUT2D_HY + 2 * RKVOP_PQ_ACM_YLUT_LENGTH * RKVOP_PQ_ACM_HLUT_DOWN_LENGTH,
            cfg_param.ACM.acmTableGainSbyY, sizeof(RK_S16) * RKVOP_PQ_ACM_YLUT_LENGTH * RKVOP_PQ_ACM_HLUT_DOWN_LENGTH);
        memcpy(p_acm_LUT2D_HS + 0 * RKVOP_PQ_ACM_SLUT_LENGTH * RKVOP_PQ_ACM_HLUT_DOWN_LENGTH,
            cfg_param.ACM.acmTableGainYbyS, sizeof(RK_S16) * RKVOP_PQ_ACM_SLUT_LENGTH * RKVOP_PQ_ACM_HLUT_DOWN_LENGTH);
        memcpy(p_acm_LUT2D_HS + 1 * RKVOP_PQ_ACM_SLUT_LENGTH * RKVOP_PQ_ACM_HLUT_DOWN_LENGTH,
            cfg_param.ACM.acmTableGainHbyS, sizeof(RK_S16) * RKVOP_PQ_ACM_SLUT_LENGTH * RKVOP_PQ_ACM_HLUT_DOWN_LENGTH);
        memcpy(p_acm_LUT2D_HS + 2 * RKVOP_PQ_ACM_SLUT_LENGTH * RKVOP_PQ_ACM_HLUT_DOWN_LENGTH,
            cfg_param.ACM.acmTableGainSbyS, sizeof(RK_S16) * RKVOP_PQ_ACM_SLUT_LENGTH * RKVOP_PQ_ACM_HLUT_DOWN_LENGTH);

        ctx->vop_glb_regs.rgs_pq_acm.vdp_acm_hw_param.p_gain_lut_HY = p_acm_LUT2D_HY;
        ctx->vop_glb_regs.rgs_pq_acm.vdp_acm_hw_param.p_gain_lut_HS = p_acm_LUT2D_HS;
        ctx->vop_glb_regs.rgs_pq_acm.vdp_acm_hw_param.p_delta_lut_H = p_acm_H_map;
        ctx->vop_glb_regs.rgs_pq_acm.p_atan_lut = g_acm_ATAN_LUT; // USELESS

        // Y/H/S gain, U10, range: [0, 1023]
        ctx->vop_glb_regs.rgs_pq_acm.vdp_acm_hw_param.Y_Gain = cfg_param.ACM.lumGain;
        ctx->vop_glb_regs.rgs_pq_acm.vdp_acm_hw_param.H_Gain = cfg_param.ACM.hueGain;
        ctx->vop_glb_regs.rgs_pq_acm.vdp_acm_hw_param.S_Gain = cfg_param.ACM.satGain;
        LOGD("in line %d, after acm config\n", __LINE__);
    }

    /* set interface info */
    ctx->p_interface_src.mImgIn[0].pix.yuv.p = (uint16_t *)ctx->proc_configs.src_info.plane_info[0].ptr;
    ctx->p_interface_src.mImgOut[0].pix.yuv.p = (uint16_t *)ctx->proc_configs.dst_info.plane_info[0].ptr;
    ctx->p_interface_src.mImgIn[0].fmt = PIX_YUV444P_10;
    ctx->p_interface_src.mImgOut[0].fmt = PIX_YUV444P_10;
    ctx->p_interface_src.mImgWid = ctx->proc_configs.src_info.img_w[0];
    ctx->p_interface_src.mImgHgt = ctx->proc_configs.src_info.img_h[0];
    ctx->p_interface_src.mImgWStride = ctx->proc_configs.src_info.img_ws[0];
    ctx->p_interface_src.mImgHStride = ctx->proc_configs.src_info.img_hs[0];
    ctx->p_interface_src.pDebugParas = &ctx->debug_params;

    /* run acm process */
    ctx->acm_proc_handle->cfg(&ctx->vop_glb_regs);
    ctx->acm_proc_handle->run(&ctx->p_interface_src, &ctx->p_interface_dst);

    FREE(p_acm_LUT2D_HY);
    FREE(p_acm_LUT2D_HS);
    FREE(p_acm_H_map);
    // LOGD_FUNC_OUT();
#endif
    return 0;
}
