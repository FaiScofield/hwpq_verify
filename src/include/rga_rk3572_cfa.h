#ifndef RGA_RK3572_CFA_H
#define RGA_RK3572_CFA_H

#ifndef RM1
#define RM1  0x00000001
#define RM2  0x00000003
#define RM3  0x00000007
#define RM4  0x0000000F
#define RM5  0x0000001F
#define RM6  0x0000003F
#define RM7  0x0000007F
#define RM8  0x000000FF
#define RM9  0x000001FF
#define RM10 0x000003FF
#define RM11 0x000007FF
#define RM12 0x00000FFF
#define RM13 0x00001FFF
#define RM14 0x00003FFF
#define RM15 0x00007FFF
#define RM16 0x0000FFFF
#define RM20 0x000FFFFF
#define RM24 0x00FFFFFF
#define RM32 0xFFFFFFFF
#endif

typedef union rga2p5_rkcfa_rk3572 {
    struct {
        struct {
            unsigned int reserve_data[72];
        } reserve_reg_0_288;
        union { // name: rkcfa_ctrl0, offset: 0x120
            struct {
                unsigned int reserve_0          : 1;
                unsigned int sw_cfa_bcsh_lut_en : 1;
                unsigned int sw_cfa_midflt_en   : 1;
                unsigned int sw_cfa_highpass_en : 1;
                unsigned int sw_cfa_panel_mode  : 1;
                unsigned int sw_cfa_c2p_id      : 3;
                unsigned int sw_cfa_r2y_mode    : 2;
                unsigned int sw_cfa_r2y_clip    : 1;
                unsigned int reserve_1          : 1;
                unsigned int sw_cfa_sat_gain    : 8;
                unsigned int reserve_2          : 12;
            } bits;
            unsigned int val;
        } rkcfa_ctrl0;
        union { // name: apattern, offset: 0x124
            struct {
                unsigned int sw_cfa_c2p_apattern : 32;
            } bits;
            unsigned int val;
        } apattern;
        union { // name: edcoef05, offset: 0x128
            struct {
                unsigned int sw_cfa_dither_coef0 : 5;
                unsigned int sw_cfa_dither_coef1 : 5;
                unsigned int sw_cfa_dither_coef2 : 5;
                unsigned int sw_cfa_dither_coef3 : 5;
                unsigned int sw_cfa_dither_coef4 : 5;
                unsigned int sw_cfa_dither_coef5 : 5;
                unsigned int reserve_0           : 2;
            } bits;
            unsigned int val;
        } edcoef05;
        union { // name: edcoef6b, offset: 0x12c
            struct {
                unsigned int sw_cfa_dither_coef6  : 5;
                unsigned int sw_cfa_dither_coef7  : 5;
                unsigned int sw_cfa_dither_coef8  : 5;
                unsigned int sw_cfa_dither_coef9  : 5;
                unsigned int sw_cfa_dither_coef10 : 5;
                unsigned int sw_cfa_dither_coef11 : 5;
                unsigned int reserve_0            : 2;
            } bits;
            unsigned int val;
        } edcoef6b;
        union { // name: rkcfa_ctrl1, offset: 0x130
            struct {
                unsigned int sw_cfa_dither_en       : 1;
                unsigned int sw_cfa_modulate_lps_en : 1;
                unsigned int sw_cfa_modulate_hps_en : 1;
                unsigned int sw_cfa_modulate_err_en : 1;
                unsigned int sw_cfa_cfa_mode        : 2;
                unsigned int sw_cfa_clr_low4bit_en  : 1;
                unsigned int sw_cfa_comps_en        : 1;
                unsigned int sw_cfa_out_fmt         : 2;
                unsigned int sw_cfa_pat_out_en      : 1;
                unsigned int reserve_0              : 5;
                unsigned int sw_cfa_sharp_level     : 7;
                unsigned int reserve_1              : 1;
                unsigned int sw_cfa_comps_level     : 6;
                unsigned int reserve_2              : 2;
            } bits;
            unsigned int val;
        } rkcfa_ctrl1;
    } regs;
    unsigned int data[77];
} rga2p5_rkcfa_rk3572_u;

#endif /* RGA_RK3572_CFA_H */
