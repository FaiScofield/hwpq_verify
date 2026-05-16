#include <stdio.h>
#include <stdlib.h>
#include "gen_dci_config.h"


typedef struct dci_hw_params
{
    RK_U8 vopIn_csc_range;
    RK_U16 ca_enable;
    RK_U16 saturation_w;      //6bit Fix
    RK_U16 luma_sat_adj_zero; //[0, 255], 8bit reference
    RK_U16 luma_sat_adj_thrd; //[0, 255], 8bit reference
    RK_U16 luma_sat_adj_k;    //[0, 1024]

    RK_S16 dci_ACT_width;
    RK_S16 dci_ACT_height;

    RK_S16 dci_ACT_start_v_idx;
    RK_S16 dci_ACT_start_h_idx;

    RK_U16 blk_size_h;
    RK_U16 blk_size_v;
    RK_U32 blk_size_fix;

    RK_U16 *p_dci_lut_map;
    RK_U16 *p_dci_ca_div_tab;
    RK_U16 *p_dci_lut_global;
    RK_U16 *p_dci_local_ratio;

    RK_U16 dci_start_offset_v;
    RK_U16 dci_start_offset_h;
} rk_pq_dci_hw_params;

int clip_rand(int min_value, int max_value);

void gen_lut(RK_U8 *p_dci_hw_lut);

void gen_reg(rk_pq_dci_hw_params *p_dci_hw_params, RK_U32 *pReg, int seed, int dci_en, int img_w, int img_h,
    int dci_do_area_u, int dci_do_area_l);

void main(int argc, const char *argv[])
{
    char dst_path[512];
    sprintf(dst_path, "%s", argv[1]);

    int seed = strtol(argv[2], NULL, 10);
    int img_w = strtol(argv[3], NULL, 10);
    int img_h = strtol(argv[4], NULL, 10);
    int dci_en = strtol(argv[5], NULL, 10);
    int csc_range = strtol(argv[6], NULL, 10);
    int ca_en = strtol(argv[7], NULL, 10);
    int hsd_mode = strtol(argv[8], NULL, 10);
    int vsd_mode = strtol(argv[9], NULL, 10);

    srand(seed);

    rk_pq_dci_hw_params dci_hw_cfg;
    RK_U8 *p_dci_hw_lut = (RK_U8 *)malloc(5632); //(256*10bit + 16*16*6bit + 16*16*10bit*16) / 8 = 5632Byte
    RK_U32 *pReg = (RK_U32 *)malloc(10 * sizeof(RK_U32));

    // generate img ROI-config
    int dci_do_area_l, dci_do_area_r, dci_do_area_u, dci_do_area_d;
    dci_do_area_l = 0;
    dci_do_area_r = img_w;
    dci_do_area_u = 0;
    dci_do_area_d = img_h;

    int h_dnsample_step, v_dnsample_step;
    int blk_size_hor, blk_size_ver;
    switch (hsd_mode) {
    case 0:  h_dnsample_step = 2; break;
    case 1:  h_dnsample_step = 4; break;
    default: h_dnsample_step = 2; break;
    }
    switch (vsd_mode) {
    case 0:  v_dnsample_step = 1; break;
    case 1:  v_dnsample_step = 2; break;
    case 2:  v_dnsample_step = 4; break;
    default: v_dnsample_step = 1; break;
    }


    if (img_h < 1080) {
        blk_size_ver = FLOOR(((RK_F32)img_h / 16) / (RK_F32)v_dnsample_step);
    }
    else {
        blk_size_ver = CEIL(((RK_F32)img_h / 16) / (RK_F32)v_dnsample_step);
    }
    if (img_w < 1080) {
        blk_size_hor = FLOOR(((RK_F32)img_w / 16) / (RK_F32)h_dnsample_step);
    }
    else {
        blk_size_hor = CEIL(((RK_F32)img_w / 16) / (RK_F32)h_dnsample_step);
    }

    blk_size_hor = blk_size_hor * h_dnsample_step;
    blk_size_ver = blk_size_ver * v_dnsample_step;

    RK_U32 blkSizeFix = ROUND_U32((RK_F32)(1 << 25) / (RK_F32)((blk_size_hor - 1) * (blk_size_ver - 1))); //最小分辨率支持64x64，取值为[0, 2^25/((64/16)*(64/16))]
    dci_hw_cfg.blk_size_fix = blkSizeFix;
    RK_S16 blk_size_hor_half, blk_size_ver_half;
    blk_size_hor_half = (blk_size_hor + 1) >> 1;
    blk_size_ver_half = (blk_size_ver + 1) >> 1;
    RK_S16 dci_ACT_start_v = dci_do_area_u;
    RK_S16 dci_ACT_start_h = dci_do_area_l;
    dci_hw_cfg.dci_ACT_width = dci_do_area_r - dci_do_area_l;
    dci_hw_cfg.dci_ACT_height = dci_do_area_d - dci_do_area_u;

    dci_hw_cfg.dci_ACT_start_h_idx = MIN(FLOOR((RK_F32)(dci_ACT_start_h - blk_size_hor_half) / (RK_F32)blk_size_hor), 16 - 1);
    dci_hw_cfg.dci_ACT_start_v_idx = MIN(FLOOR((RK_F32)(dci_ACT_start_v - blk_size_ver_half) / (RK_F32)blk_size_ver), 16 - 1);

    dci_hw_cfg.dci_start_offset_h = (RK_U16)CLIP(
        (RK_U64)(dci_ACT_start_h - (RK_S32)blk_size_hor_half - (dci_hw_cfg.dci_ACT_start_h_idx * (RK_S32)blk_size_hor)),
        0, img_w);
    dci_hw_cfg.dci_start_offset_v = (RK_U16)CLIP(
        (RK_U64)(dci_ACT_start_v - (RK_S32)blk_size_ver_half - (dci_hw_cfg.dci_ACT_start_v_idx * (RK_S32)blk_size_ver)),
        0, img_h);

    dci_hw_cfg.blk_size_h = blk_size_hor;
    dci_hw_cfg.blk_size_v = blk_size_ver;

    gen_lut(p_dci_hw_lut);

    // generate color-adjust config
    RK_U16 Lum_zero, Lum_thr, Lum_tmp;
    Lum_zero = clip_rand(0, 256);
    Lum_thr = clip_rand(0, 256);

    while ((Lum_thr == Lum_zero) || (ABS_S16((RK_S16)Lum_zero - (RK_S16)Lum_thr) > 40)) {
        // Lum_thr = rand() % 256;
        Lum_thr = clip_rand(0, 256);
    }
    Lum_thr = Lum_thr * 4;
    Lum_zero = Lum_zero * 4;

    if (Lum_zero > Lum_thr) {
        Lum_tmp = Lum_thr;
        Lum_thr = Lum_zero;
        Lum_zero = Lum_tmp;
    }
    dci_hw_cfg.luma_sat_adj_zero = Lum_zero;
    dci_hw_cfg.luma_sat_adj_thrd = Lum_thr;

    // p_pq_hw_params->vdp_dci_hw_params.saturation_w = rand() % 65;
    dci_hw_cfg.saturation_w = clip_rand(0, 65);
    dci_hw_cfg.luma_sat_adj_k =
        ROUND_U16((RK_F32)(1 << 10) / MAX(1.0, (RK_F32)(dci_hw_cfg.luma_sat_adj_thrd - dci_hw_cfg.luma_sat_adj_zero)));

    dci_hw_cfg.vopIn_csc_range = csc_range;
    dci_hw_cfg.ca_enable = ca_en;


    gen_reg(&dci_hw_cfg, pReg, seed, dci_en, img_w, img_h, dci_do_area_u, dci_do_area_l);


    char dci_reg_file_name[1024];
    sprintf(dci_reg_file_name, "%s//dci_reg_list_%08d.dat", dst_path, seed);
    char dci_hw_lut_file_name[1024];
    sprintf(dci_hw_lut_file_name, "%s//dci_hw_lut_%08d.dat", dst_path, seed);

    FILE *fp_dci_reg = fopen(dci_reg_file_name, "wb");
    fwrite(pReg, 4, 10, fp_dci_reg);
    fclose(fp_dci_reg);

    FILE *fp_dci_hw_lut = fopen(dci_hw_lut_file_name, "wb");
    fwrite(p_dci_hw_lut, 1, 5632, fp_dci_hw_lut);
    fclose(fp_dci_hw_lut);

    free(p_dci_hw_lut);
    free(pReg);
}


int clip_rand(int min_value, int max_value)
{
    max_value = max_value - 1;
    int ext_value = (max_value - min_value) >> 1;
    ext_value = MAX(1, ext_value);

    int rand_range = (max_value - min_value + 2 * ext_value);
    int rand_tmp = rand() % (rand_range) + min_value - ext_value;

    int rand_value = CLIP(rand_tmp, min_value, max_value);
    return rand_value;
}

void gen_lut(RK_U8 *p_dci_hw_lut)
{
    // Generate Lut
    RK_U16 global_lut[256] = {0};
    for (int kk = 0; kk < 1024; kk++) {
        int a = clip_rand(0, 1024);
        if (kk % 4 == 0)
            global_lut[kk >> 2] = a;
    }
    RK_U16 local_lut[16 * 16 * 16] = {0};
    for (int kk = 0; kk < 16 * 16 * 16; kk++) {
        int a_p = clip_rand(0, 1024);
        local_lut[kk] = a_p;
    }
    RK_U16 local_abld_ratio[16 * 16] = {0};
    for (int kk = 0; kk < 16 * 16; kk++) {
        int a_p = clip_rand(0, 33);
        local_abld_ratio[kk] = a_p;
    }

    RK_U16 hw_lut_idx = 0;
    // Global Lut
    for (int ii = 0; ii < 256; ii += 4) {
        RK_U16 tmp0_u10, tmp1_u10, tmp2_u10, tmp3_u10;
        RK_U8 tmp0_u8, tmp1_u8, tmp2_u8, tmp3_u8, tmp4_u8;
        tmp0_u10 = *(global_lut + ii + 0);
        tmp1_u10 = *(global_lut + ii + 1);
        tmp2_u10 = *(global_lut + ii + 2);
        tmp3_u10 = *(global_lut + ii + 3);

        tmp0_u8 = tmp0_u10 & ((1 << 8) - 1);
        tmp1_u8 = ((tmp1_u10 & ((1 << 6) - 1)) << 2) + (tmp0_u10 >> 8);
        tmp2_u8 = ((tmp2_u10 & ((1 << 4) - 1)) << 4) + (tmp1_u10 >> 6);
        tmp3_u8 = ((tmp3_u10 & ((1 << 2) - 1)) << 6) + (tmp2_u10 >> 4);
        tmp4_u8 = (tmp3_u10 >> 2);

        *(p_dci_hw_lut + hw_lut_idx + 0) = tmp0_u8;
        *(p_dci_hw_lut + hw_lut_idx + 1) = tmp1_u8;
        *(p_dci_hw_lut + hw_lut_idx + 2) = tmp2_u8;
        *(p_dci_hw_lut + hw_lut_idx + 3) = tmp3_u8;
        *(p_dci_hw_lut + hw_lut_idx + 4) = tmp4_u8;
        hw_lut_idx += 5;
    }
    // Local ratio Lut
    for (int ii = 0; ii < 16 * 16; ii += 4) {
        RK_U16 tmp0_u6, tmp1_u6, tmp2_u6, tmp3_u6;
        RK_U8 tmp0_u8, tmp1_u8, tmp2_u8;
        tmp0_u6 = *(local_abld_ratio + ii + 0);
        tmp1_u6 = *(local_abld_ratio + ii + 1);
        tmp2_u6 = *(local_abld_ratio + ii + 2);
        tmp3_u6 = *(local_abld_ratio + ii + 3);

        tmp0_u8 = ((tmp1_u6 & ((1 << 2) - 1)) << 6) + (tmp0_u6 >> 0);
        tmp1_u8 = ((tmp2_u6 & ((1 << 4) - 1)) << 4) + (tmp1_u6 >> 2);
        tmp2_u8 = ((tmp3_u6 & ((1 << 6) - 1)) << 2) + (tmp2_u6 >> 4);

        *(p_dci_hw_lut + hw_lut_idx + 0) = tmp0_u8;
        *(p_dci_hw_lut + hw_lut_idx + 1) = tmp1_u8;
        *(p_dci_hw_lut + hw_lut_idx + 2) = tmp2_u8;
        hw_lut_idx += 3;
    }
    // Local Tone Lut
    for (int ii = 0; ii < 16 * 16 * 16; ii += 4) {
        RK_U16 tmp0_u10, tmp1_u10, tmp2_u10, tmp3_u10;
        RK_U8 tmp0_u8, tmp1_u8, tmp2_u8, tmp3_u8, tmp4_u8;
        tmp0_u10 = *(local_lut + ii + 0);
        tmp1_u10 = *(local_lut + ii + 1);
        tmp2_u10 = *(local_lut + ii + 2);
        tmp3_u10 = *(local_lut + ii + 3);

        tmp0_u8 = tmp0_u10 & ((1 << 8) - 1);
        tmp1_u8 = ((tmp1_u10 & ((1 << 6) - 1)) << 2) + (tmp0_u10 >> 8);
        tmp2_u8 = ((tmp2_u10 & ((1 << 4) - 1)) << 4) + (tmp1_u10 >> 6);
        tmp3_u8 = ((tmp3_u10 & ((1 << 2) - 1)) << 6) + (tmp2_u10 >> 4);
        tmp4_u8 = (tmp3_u10 >> 2);

        *(p_dci_hw_lut + hw_lut_idx + 0) = tmp0_u8;
        *(p_dci_hw_lut + hw_lut_idx + 1) = tmp1_u8;
        *(p_dci_hw_lut + hw_lut_idx + 2) = tmp2_u8;
        *(p_dci_hw_lut + hw_lut_idx + 3) = tmp3_u8;
        *(p_dci_hw_lut + hw_lut_idx + 4) = tmp4_u8;
        hw_lut_idx += 5;
    }
}


void gen_reg(rk_pq_dci_hw_params *p_dci_hw_params, RK_U32 *pReg, int seed, int dci_en, int img_w, int img_h,
    int dci_do_area_u, int dci_do_area_l)
{
    *(pReg + 0) = seed;
    *(pReg + 1) = (img_h << 16) + (img_w);
    *(pReg + 2) = (dci_do_area_u << 16) + (dci_do_area_l);
    *(pReg + 3) = ((p_dci_hw_params->dci_ACT_height - 1) << 16) + (p_dci_hw_params->dci_ACT_width - 1);

    *(pReg + 4) = (p_dci_hw_params->blk_size_h << 0) + (p_dci_hw_params->blk_size_v << 16);
    *(pReg + 5) = (p_dci_hw_params->dci_start_offset_h << 0) + (p_dci_hw_params->dci_start_offset_v << 16);
    *(pReg + 6) = (p_dci_hw_params->blk_size_fix << 0) + ((p_dci_hw_params->dci_ACT_start_h_idx + 1) << 20) +
                  ((p_dci_hw_params->dci_ACT_start_v_idx + 1) << 26);
    *(pReg + 7) = (p_dci_hw_params->luma_sat_adj_zero << 0) + (p_dci_hw_params->luma_sat_adj_thrd << 16);
    *(pReg + 8) = (p_dci_hw_params->luma_sat_adj_k << 0) + (p_dci_hw_params->saturation_w << 16);
    *(pReg + 9) = (dci_en << 0) + (p_dci_hw_params->ca_enable << 1) + (p_dci_hw_params->vopIn_csc_range << 2);
}