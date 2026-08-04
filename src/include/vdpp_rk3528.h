#ifndef VDPP_RK3528_H
#define VDPP_RK3528_H

// 0x00000000
typedef union iep2_rk3528 {
    struct {
        union { // name: frm_start, offset: 0x0
            struct {
                unsigned int sw_iep_frm_en : 1;
                unsigned int reserve_0     : 31;
            } bits;
            unsigned int val;
        } frm_start;
        union { // name: iep_config0, offset: 0x4
            struct {
                unsigned int sw_iep_src_fmt         : 2;
                unsigned int reserve_0              : 2;
                unsigned int sw_iep_src_yuv_swap    : 2;
                unsigned int reserve_1              : 2;
                unsigned int sw_iep_dst_fmt         : 2;
                unsigned int reserve_2              : 2;
                unsigned int sw_iep_dst_yuv_swap    : 2;
                unsigned int reserve_3              : 2;
                unsigned int sw_iep_debug_data_en   : 1;
                unsigned int reserve_4              : 3;
                unsigned int sw_iep_rst_protect_dis : 1;
                unsigned int sys_iep_sreset_p       : 1;
                unsigned int sw_iep_init_dis        : 1;
                unsigned int reserve_5              : 9;
            } bits;
            unsigned int val;
        } iep_config0;
        union { // name: working_mode, offset: 0x8
            struct {
                unsigned int sw_vdpp_working_mode : 2;
                unsigned int reserve_0            : 30;
            } bits;
            unsigned int val;
        } working_mode;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_12_16;
        union { // name: gating_ctrl, offset: 0x10
            struct {
                unsigned int sw_iep_clk_on  : 1;
                unsigned int sw_md_clk_on   : 1;
                unsigned int sw_dect_clk_on : 1;
                unsigned int sw_me_clk_on   : 1;
                unsigned int sw_mc_clk_on   : 1;
                unsigned int sw_eedi_clk_on : 1;
                unsigned int sw_ble_clk_on  : 1;
                unsigned int sw_out_clk_on  : 1;
                unsigned int sw_ctrl_clk_on : 1;
                unsigned int sw_ram_clk_on  : 1;
                unsigned int sw_dma_clk_on  : 1;
                unsigned int sw_reg_clk_on  : 1;
                unsigned int reserve_0      : 20;
            } bits;
            unsigned int val;
        } gating_ctrl;
        union { // name: status, offset: 0x14
            struct {
                unsigned int ro_arst_finish_done : 1;
                unsigned int reserve_0           : 31;
            } bits;
            unsigned int val;
        } status;
        struct {
            unsigned int reserve_data[2];
        } reserve_reg_24_32;
        union { // name: int_en, offset: 0x20
            struct {
                unsigned int sw_iep_frm_done_en    : 1;
                unsigned int sw_iep_osd_max_en     : 1;
                unsigned int reserve_0             : 2;
                unsigned int sw_iep_bus_error_en   : 1;
                unsigned int sw_iep_timeout_int_en : 1;
                unsigned int reserve_1             : 26;
            } bits;
            unsigned int val;
        } int_en;
        union { // name: int_clr, offset: 0x24
            struct {
                unsigned int sw_iep_frm_done_clr    : 1;
                unsigned int sw_iep_osd_max_clr     : 1;
                unsigned int reserve_0              : 2;
                unsigned int sw_iep_bus_error_clr   : 1;
                unsigned int sw_iep_timeout_int_clr : 1;
                unsigned int reserve_1              : 26;
            } bits;
            unsigned int val;
        } int_clr;
        union { // name: int_sts, offset: 0x28
            struct {
                unsigned int ro_frm_done_sts  : 1;
                unsigned int ro_osd_max_sts   : 1;
                unsigned int reserve_0        : 2;
                unsigned int ro_bus_error_sts : 1;
                unsigned int ro_timeout_sts   : 1;
                unsigned int reserve_1        : 26;
            } bits;
            unsigned int val;
        } int_sts;
        union { // name: int_raw_sts, offset: 0x2c
            struct {
                unsigned int ro_frm_done_raw  : 1;
                unsigned int ro_osd_max_raw   : 1;
                unsigned int reserve_0        : 2;
                unsigned int ro_bus_error_raw : 1;
                unsigned int ro_timeout_raw   : 1;
                unsigned int reserve_1        : 26;
            } bits;
            unsigned int val;
        } int_raw_sts;
        union { // name: vir_src_img_width, offset: 0x30
            struct {
                unsigned int sw_iep_src_vir_y_stride  : 16;
                unsigned int sw_iep_src_vir_uv_stride : 16;
            } bits;
            unsigned int val;
        } vir_src_img_width;
        union { // name: vir_dst_img_width, offset: 0x34
            struct {
                unsigned int sw_iep_dst_vir_stride : 16;
                unsigned int reserve_0             : 16;
            } bits;
            unsigned int val;
        } vir_dst_img_width;
        union { // name: src_img_size, offset: 0x38
            struct {
                unsigned int sw_iep_src_pic_width  : 11;
                unsigned int reserve_0             : 5;
                unsigned int sw_iep_src_pic_height : 11;
                unsigned int reserve_1             : 5;
            } bits;
            unsigned int val;
        } src_img_size;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_60_64;
        union { // name: dil_config0, offset: 0x40
            struct {
                unsigned int sw_dil_mode        : 4;
                unsigned int sw_dil_out_mode    : 1;
                unsigned int sw_dil_field_order : 1;
                unsigned int reserve_0          : 2;
                unsigned int sw_dil_md_pre_en   : 1;
                unsigned int sw_dil_ff_en       : 1;
                unsigned int sw_dil_pd_en       : 1;
                unsigned int sw_dil_osd_en      : 1;
                unsigned int sw_dil_memc_en     : 1;
                unsigned int reserve_1          : 2;
                unsigned int sw_dil_comb_en     : 1;
                unsigned int sw_dil_roi_en      : 1;
                unsigned int sw_dil_mv_hist_en  : 1;
                unsigned int reserve_2          : 14;
            } bits;
            unsigned int val;
        } dil_config0;
        struct {
            unsigned int reserve_data[3];
        } reserve_reg_68_80;
        union { // name: iep_timeout_cfg, offset: 0x50
            struct {
                unsigned int sw_iep_timeout_cnt : 31;
                unsigned int sw_iep_timeout_en  : 1;
            } bits;
            unsigned int val;
        } iep_timeout_cfg;
        union { // name: iep_version_info, offset: 0x54
            struct {
                unsigned int svnbuild : 20;
                unsigned int minor    : 8;
                unsigned int major    : 4;
            } bits;
            unsigned int val;
        } iep_version_info;
        union { // name: dbg_frm_cnt, offset: 0x58
            struct {
                unsigned int dbg_frm_cnt : 16;
                unsigned int reserve_0   : 16;
            } bits;
            unsigned int val;
        } dbg_frm_cnt;
        union { // name: dbg_timeout_cnt, offset: 0x5c
            struct {
                unsigned int dbg_timeout_cnt : 31;
                unsigned int reserve_0       : 1;
            } bits;
            unsigned int val;
        } dbg_timeout_cnt;
        union { // name: src_addr_cury, offset: 0x60
            struct {
                unsigned int sw_iep_src_addr_cury : 32;
            } bits;
            unsigned int val;
        } src_addr_cury;
        union { // name: src_addr_nxty, offset: 0x64
            struct {
                unsigned int sw_iep_src_addr_nxty : 32;
            } bits;
            unsigned int val;
        } src_addr_nxty;
        union { // name: src_addr_prey, offset: 0x68
            struct {
                unsigned int sw_iep_src_addr_prey : 32;
            } bits;
            unsigned int val;
        } src_addr_prey;
        union { // name: src_addr_curuv, offset: 0x6c
            struct {
                unsigned int sw_iep_src_addr_curuv : 32;
            } bits;
            unsigned int val;
        } src_addr_curuv;
        union { // name: src_addr_curv, offset: 0x70
            struct {
                unsigned int sw_iep_src_addr_curv : 32;
            } bits;
            unsigned int val;
        } src_addr_curv;
        union { // name: src_addr_nxtuv, offset: 0x74
            struct {
                unsigned int sw_iep_src_addr_nxtuv : 32;
            } bits;
            unsigned int val;
        } src_addr_nxtuv;
        union { // name: src_addr_nxtv, offset: 0x78
            struct {
                unsigned int sw_iep_src_addr_nxtv : 32;
            } bits;
            unsigned int val;
        } src_addr_nxtv;
        union { // name: src_addr_preuv, offset: 0x7c
            struct {
                unsigned int sw_iep_src_addr_preuv : 32;
            } bits;
            unsigned int val;
        } src_addr_preuv;
        union { // name: src_addr_prev, offset: 0x80
            struct {
                unsigned int sw_iep_src_addr_prev : 32;
            } bits;
            unsigned int val;
        } src_addr_prev;
        union { // name: src_addr_md, offset: 0x84
            struct {
                unsigned int sw_iep_src_addr_md : 32;
            } bits;
            unsigned int val;
        } src_addr_md;
        union { // name: src_addr_mv, offset: 0x88
            struct {
                unsigned int sw_iep_src_addr_mv : 32;
            } bits;
            unsigned int val;
        } src_addr_mv;
        union { // name: roi_addr, offset: 0x8c
            struct {
                unsigned int sw_iep_addr_roi : 32;
            } bits;
            unsigned int val;
        } roi_addr;
        struct {
            unsigned int reserve_data[8];
        } reserve_reg_144_176;
        union { // name: dst_addr_topy, offset: 0xb0
            struct {
                unsigned int sw_iep_dst_addr_topy : 32;
            } bits;
            unsigned int val;
        } dst_addr_topy;
        union { // name: dst_addr_boty, offset: 0xb4
            struct {
                unsigned int sw_iep_dst_addr_boty : 32;
            } bits;
            unsigned int val;
        } dst_addr_boty;
        union { // name: dst_addr_topc, offset: 0xb8
            struct {
                unsigned int sw_iep_dst_addr_topc : 32;
            } bits;
            unsigned int val;
        } dst_addr_topc;
        union { // name: dst_addr_botc, offset: 0xbc
            struct {
                unsigned int sw_iep_dst_addr_botc : 32;
            } bits;
            unsigned int val;
        } dst_addr_botc;
        union { // name: dst_addr_md, offset: 0xc0
            struct {
                unsigned int sw_iep_dst_addr_md : 32;
            } bits;
            unsigned int val;
        } dst_addr_md;
        union { // name: dst_addr_mv, offset: 0xc4
            struct {
                unsigned int sw_iep_dst_addr_mv : 32;
            } bits;
            unsigned int val;
        } dst_addr_mv;
        struct {
            unsigned int reserve_data[6];
        } reserve_reg_200_224;
        union { // name: md_config0, offset: 0xe0
            struct {
                unsigned int sw_md_lambda : 4;
                unsigned int sw_md_r      : 4;
                unsigned int sw_md_theta  : 2;
                unsigned int reserve_0    : 22;
            } bits;
            unsigned int val;
        } md_config0;
        union { // name: dect_config0, offset: 0xe4
            struct {
                unsigned int sw_dect_resi_thr : 8;
                unsigned int sw_osd_area_num  : 4;
                unsigned int reserve_0        : 4;
                unsigned int sw_osd_gradh_thr : 8;
                unsigned int sw_osd_gradv_thr : 8;
            } bits;
            unsigned int val;
        } dect_config0;
        struct {
            unsigned int reserve_data[2];
        } reserve_reg_232_240;
        union { // name: osd_limit_config, offset: 0xf0
            struct {
                unsigned int sw_osd_pos_limit_en  : 1;
                unsigned int reserve_0            : 3;
                unsigned int sw_osd_pos_limit_num : 1;
                unsigned int reserve_1            : 27;
            } bits;
            unsigned int val;
        } osd_limit_config;
        union { // name: osd_limit_area0, offset: 0xf4
            struct {
                unsigned int sw_osd_limit_area0 : 32;
            } bits;
            unsigned int val;
        } osd_limit_area0;
        union { // name: osd_limit_area1, offset: 0xf8
            struct {
                unsigned int sw_osd_limit_area1 : 32;
            } bits;
            unsigned int val;
        } osd_limit_area1;
        union { // name: osd_config0, offset: 0xfc
            struct {
                unsigned int sw_osd_pec_thr  : 11;
                unsigned int reserve_0       : 5;
                unsigned int sw_osd_line_num : 9;
                unsigned int reserve_1       : 7;
            } bits;
            unsigned int val;
        } osd_config0;
        union { // name: osd_area_conf0, offset: 0x100
            struct {
                unsigned int sw_osd_x_sta0 : 7;
                unsigned int sw_osd_x_end0 : 7;
                unsigned int sw_osd_y_sta0 : 9;
                unsigned int sw_osd_y_end0 : 9;
            } bits;
            unsigned int val;
        } osd_area_conf0;
        union { // name: osd_area_conf1, offset: 0x104
            struct {
                unsigned int sw_osd_x_sta1 : 7;
                unsigned int sw_osd_x_end1 : 7;
                unsigned int sw_osd_y_sta1 : 9;
                unsigned int sw_osd_y_end1 : 9;
            } bits;
            unsigned int val;
        } osd_area_conf1;
        union { // name: osd_area_conf2, offset: 0x108
            struct {
                unsigned int sw_osd_x_sta2 : 7;
                unsigned int sw_osd_x_end2 : 7;
                unsigned int sw_osd_y_sta2 : 9;
                unsigned int sw_osd_y_end2 : 9;
            } bits;
            unsigned int val;
        } osd_area_conf2;
        union { // name: osd_area_conf3, offset: 0x10c
            struct {
                unsigned int sw_osd_x_sta3 : 7;
                unsigned int sw_osd_x_end3 : 7;
                unsigned int sw_osd_y_sta3 : 9;
                unsigned int sw_osd_y_end3 : 9;
            } bits;
            unsigned int val;
        } osd_area_conf3;
        union { // name: osd_area_conf4, offset: 0x110
            struct {
                unsigned int sw_osd_x_sta4 : 7;
                unsigned int sw_osd_x_end4 : 7;
                unsigned int sw_osd_y_sta4 : 9;
                unsigned int sw_osd_y_end4 : 9;
            } bits;
            unsigned int val;
        } osd_area_conf4;
        union { // name: osd_area_conf5, offset: 0x114
            struct {
                unsigned int sw_osd_x_sta5 : 7;
                unsigned int sw_osd_x_end5 : 7;
                unsigned int sw_osd_y_sta5 : 9;
                unsigned int sw_osd_y_end5 : 9;
            } bits;
            unsigned int val;
        } osd_area_conf5;
        union { // name: osd_area_conf6, offset: 0x118
            struct {
                unsigned int sw_osd_x_sta6 : 7;
                unsigned int sw_osd_x_end6 : 7;
                unsigned int sw_osd_y_sta6 : 9;
                unsigned int sw_osd_y_end6 : 9;
            } bits;
            unsigned int val;
        } osd_area_conf6;
        union { // name: osd_area_conf7, offset: 0x11c
            struct {
                unsigned int sw_osd_x_sta7 : 7;
                unsigned int sw_osd_x_end7 : 7;
                unsigned int sw_osd_y_sta7 : 9;
                unsigned int sw_osd_y_end7 : 9;
            } bits;
            unsigned int val;
        } osd_area_conf7;
        union { // name: me_config0, offset: 0x120
            struct {
                unsigned int sw_me_pena             : 4;
                unsigned int sw_mv_bonus            : 4;
                unsigned int sw_mv_similar_thr      : 4;
                unsigned int sw_mv_similar_num_thr0 : 4;
                unsigned int sw_me_thr_offset       : 8;
                unsigned int reserve_0              : 8;
            } bits;
            unsigned int val;
        } me_config0;
        union { // name: me_limit_config, offset: 0x124
            struct {
                unsigned int sw_mv_left_limt  : 6;
                unsigned int reserve_0        : 2;
                unsigned int sw_mv_right_limt : 6;
                unsigned int reserve_1        : 18;
            } bits;
            unsigned int val;
        } me_limit_config;
        union { // name: mv_tru_list0, offset: 0x128
            struct {
                unsigned int sw_mv_tru_list0_vld : 1;
                unsigned int reserve_0           : 1;
                unsigned int sw_mv_tru_list0_mv  : 6;
                unsigned int sw_mv_tru_list1_vld : 1;
                unsigned int reserve_1           : 1;
                unsigned int sw_mv_tru_list1_mv  : 6;
                unsigned int sw_mv_tru_list2_vld : 1;
                unsigned int reserve_2           : 1;
                unsigned int sw_mv_tru_list2_mv  : 6;
                unsigned int sw_mv_tru_list3_vld : 1;
                unsigned int reserve_3           : 1;
                unsigned int sw_mv_tru_list3_mv  : 6;
            } bits;
            unsigned int val;
        } mv_tru_list0;
        union { // name: mv_tru_list1, offset: 0x12c
            struct {
                unsigned int sw_mv_tru_list4_vld : 1;
                unsigned int reserve_0           : 1;
                unsigned int sw_mv_tru_list4_mv  : 6;
                unsigned int sw_mv_tru_list5_vld : 1;
                unsigned int reserve_1           : 1;
                unsigned int sw_mv_tru_list5_mv  : 6;
                unsigned int sw_mv_tru_list6_vld : 1;
                unsigned int reserve_2           : 1;
                unsigned int sw_mv_tru_list6_mv  : 6;
                unsigned int sw_mv_tru_list7_vld : 1;
                unsigned int reserve_3           : 1;
                unsigned int sw_mv_tru_list7_mv  : 6;
            } bits;
            unsigned int val;
        } mv_tru_list1;
        union { // name: eedi_config0, offset: 0x130
            struct {
                unsigned int sw_eedi_thr0 : 5;
                unsigned int reserve_0    : 27;
            } bits;
            unsigned int val;
        } eedi_config0;
        union { // name: ble_config0, offset: 0x134
            struct {
                unsigned int sw_ble_backtoma_num : 3;
                unsigned int reserve_0           : 29;
            } bits;
            unsigned int val;
        } ble_config0;
        union { // name: comb_config0, offset: 0x138
            struct {
                unsigned int sw_comb_osd_vld     : 8;
                unsigned int sw_comb_t_thr       : 8;
                unsigned int sw_comb_feature_thr : 6;
                unsigned int reserve_0           : 2;
                unsigned int sw_comb_cnt_thr     : 4;
                unsigned int reserve_1           : 4;
            } bits;
            unsigned int val;
        } comb_config0;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_316_320;
        union { // name: dil_mtn_tab0, offset: 0x140
            struct {
                unsigned int sw_mtn_sub_tab00 : 7;
                unsigned int reserve_0        : 1;
                unsigned int sw_mtn_sub_tab01 : 7;
                unsigned int reserve_1        : 1;
                unsigned int sw_mtn_sub_tab02 : 7;
                unsigned int reserve_2        : 1;
                unsigned int sw_mtn_sub_tab03 : 7;
                unsigned int reserve_3        : 1;
            } bits;
            unsigned int val;
        } dil_mtn_tab0;
        union { // name: dil_mtn_tab1, offset: 0x144
            struct {
                unsigned int sw_mtn_sub_tab04 : 7;
                unsigned int reserve_0        : 1;
                unsigned int sw_mtn_sub_tab05 : 7;
                unsigned int reserve_1        : 1;
                unsigned int sw_mtn_sub_tab06 : 7;
                unsigned int reserve_2        : 1;
                unsigned int sw_mtn_sub_tab07 : 7;
                unsigned int reserve_3        : 1;
            } bits;
            unsigned int val;
        } dil_mtn_tab1;
        union { // name: dil_mtn_tab2, offset: 0x148
            struct {
                unsigned int sw_mtn_sub_tab08 : 7;
                unsigned int reserve_0        : 1;
                unsigned int sw_mtn_sub_tab09 : 7;
                unsigned int reserve_1        : 1;
                unsigned int sw_mtn_sub_tab10 : 7;
                unsigned int reserve_2        : 1;
                unsigned int sw_mtn_sub_tab11 : 7;
                unsigned int reserve_3        : 1;
            } bits;
            unsigned int val;
        } dil_mtn_tab2;
        union { // name: dil_mtn_tab3, offset: 0x14c
            struct {
                unsigned int sw_mtn_sub_tab12 : 7;
                unsigned int reserve_0        : 1;
                unsigned int sw_mtn_sub_tab13 : 7;
                unsigned int reserve_1        : 1;
                unsigned int sw_mtn_sub_tab14 : 7;
                unsigned int reserve_2        : 1;
                unsigned int sw_mtn_sub_tab15 : 7;
                unsigned int reserve_3        : 1;
            } bits;
            unsigned int val;
        } dil_mtn_tab3;
        union { // name: dil_mtn_tab4, offset: 0x150
            struct {
                unsigned int sw_mtn_sub_tab16 : 7;
                unsigned int reserve_0        : 1;
                unsigned int sw_mtn_sub_tab17 : 7;
                unsigned int reserve_1        : 1;
                unsigned int sw_mtn_sub_tab18 : 7;
                unsigned int reserve_2        : 1;
                unsigned int sw_mtn_sub_tab19 : 7;
                unsigned int reserve_3        : 1;
            } bits;
            unsigned int val;
        } dil_mtn_tab4;
        union { // name: dil_mtn_tab5, offset: 0x154
            struct {
                unsigned int sw_mtn_sub_tab20 : 7;
                unsigned int reserve_0        : 1;
                unsigned int sw_mtn_sub_tab21 : 7;
                unsigned int reserve_1        : 1;
                unsigned int sw_mtn_sub_tab22 : 7;
                unsigned int reserve_2        : 1;
                unsigned int sw_mtn_sub_tab23 : 7;
                unsigned int reserve_3        : 1;
            } bits;
            unsigned int val;
        } dil_mtn_tab5;
        union { // name: dil_mtn_tab6, offset: 0x158
            struct {
                unsigned int sw_mtn_sub_tab24 : 7;
                unsigned int reserve_0        : 1;
                unsigned int sw_mtn_sub_tab25 : 7;
                unsigned int reserve_1        : 1;
                unsigned int sw_mtn_sub_tab26 : 7;
                unsigned int reserve_2        : 1;
                unsigned int sw_mtn_sub_tab27 : 7;
                unsigned int reserve_3        : 1;
            } bits;
            unsigned int val;
        } dil_mtn_tab6;
        union { // name: dil_mtn_tab7, offset: 0x15c
            struct {
                unsigned int sw_mtn_sub_tab28 : 7;
                unsigned int reserve_0        : 1;
                unsigned int sw_mtn_sub_tab29 : 7;
                unsigned int reserve_1        : 1;
                unsigned int sw_mtn_sub_tab30 : 7;
                unsigned int reserve_2        : 1;
                unsigned int sw_mtn_sub_tab31 : 7;
                unsigned int reserve_3        : 1;
            } bits;
            unsigned int val;
        } dil_mtn_tab7;
        union { // name: dil_mtn_tab8, offset: 0x160
            struct {
                unsigned int sw_mtn_sub_tab32 : 7;
                unsigned int reserve_0        : 1;
                unsigned int sw_mtn_sub_tab33 : 7;
                unsigned int reserve_1        : 1;
                unsigned int sw_mtn_sub_tab34 : 7;
                unsigned int reserve_2        : 1;
                unsigned int sw_mtn_sub_tab35 : 7;
                unsigned int reserve_3        : 1;
            } bits;
            unsigned int val;
        } dil_mtn_tab8;
        union { // name: dil_mtn_tab9, offset: 0x164
            struct {
                unsigned int sw_mtn_sub_tab36 : 7;
                unsigned int reserve_0        : 1;
                unsigned int sw_mtn_sub_tab37 : 7;
                unsigned int reserve_1        : 1;
                unsigned int sw_mtn_sub_tab38 : 7;
                unsigned int reserve_2        : 1;
                unsigned int sw_mtn_sub_tab39 : 7;
                unsigned int reserve_3        : 1;
            } bits;
            unsigned int val;
        } dil_mtn_tab9;
        union { // name: dil_mtn_tab10, offset: 0x168
            struct {
                unsigned int sw_mtn_sub_tab40 : 7;
                unsigned int reserve_0        : 1;
                unsigned int sw_mtn_sub_tab41 : 7;
                unsigned int reserve_1        : 1;
                unsigned int sw_mtn_sub_tab42 : 7;
                unsigned int reserve_2        : 1;
                unsigned int sw_mtn_sub_tab43 : 7;
                unsigned int reserve_3        : 1;
            } bits;
            unsigned int val;
        } dil_mtn_tab10;
        union { // name: dil_mtn_tab11, offset: 0x16c
            struct {
                unsigned int sw_mtn_sub_tab44 : 7;
                unsigned int reserve_0        : 1;
                unsigned int sw_mtn_sub_tab45 : 7;
                unsigned int reserve_1        : 1;
                unsigned int sw_mtn_sub_tab46 : 7;
                unsigned int reserve_2        : 1;
                unsigned int sw_mtn_sub_tab47 : 7;
                unsigned int reserve_3        : 1;
            } bits;
            unsigned int val;
        } dil_mtn_tab11;
        union { // name: dil_mtn_tab12, offset: 0x170
            struct {
                unsigned int sw_mtn_sub_tab48 : 7;
                unsigned int reserve_0        : 1;
                unsigned int sw_mtn_sub_tab49 : 7;
                unsigned int reserve_1        : 1;
                unsigned int sw_mtn_sub_tab50 : 7;
                unsigned int reserve_2        : 1;
                unsigned int sw_mtn_sub_tab51 : 7;
                unsigned int reserve_3        : 1;
            } bits;
            unsigned int val;
        } dil_mtn_tab12;
        union { // name: dil_mtn_tab13, offset: 0x174
            struct {
                unsigned int sw_mtn_sub_tab52 : 7;
                unsigned int reserve_0        : 1;
                unsigned int sw_mtn_sub_tab53 : 7;
                unsigned int reserve_1        : 1;
                unsigned int sw_mtn_sub_tab54 : 7;
                unsigned int reserve_2        : 1;
                unsigned int sw_mtn_sub_tab55 : 7;
                unsigned int reserve_3        : 1;
            } bits;
            unsigned int val;
        } dil_mtn_tab13;
        union { // name: dil_mtn_tab14, offset: 0x178
            struct {
                unsigned int sw_mtn_sub_tab56 : 7;
                unsigned int reserve_0        : 1;
                unsigned int sw_mtn_sub_tab57 : 7;
                unsigned int reserve_1        : 1;
                unsigned int sw_mtn_sub_tab58 : 7;
                unsigned int reserve_2        : 1;
                unsigned int sw_mtn_sub_tab59 : 7;
                unsigned int reserve_3        : 1;
            } bits;
            unsigned int val;
        } dil_mtn_tab14;
        union { // name: dil_mtn_tab15, offset: 0x17c
            struct {
                unsigned int sw_mtn_sub_tab60 : 7;
                unsigned int reserve_0        : 1;
                unsigned int sw_mtn_sub_tab61 : 7;
                unsigned int reserve_1        : 1;
                unsigned int sw_mtn_sub_tab62 : 7;
                unsigned int reserve_2        : 1;
                unsigned int sw_mtn_sub_tab63 : 7;
                unsigned int reserve_3        : 1;
            } bits;
            unsigned int val;
        } dil_mtn_tab15;
        struct {
            unsigned int reserve_data[160];
        } reserve_reg_384_1024;
        union { // name: ro_pd_tcnt, offset: 0x400
            struct {
                unsigned int ro_dect_pd_tcnt : 20;
                unsigned int reserve_0       : 12;
            } bits;
            unsigned int val;
        } ro_pd_tcnt;
        union { // name: ro_pd_bcnt, offset: 0x404
            struct {
                unsigned int ro_dect_pd_bcnt : 20;
                unsigned int reserve_0       : 12;
            } bits;
            unsigned int val;
        } ro_pd_bcnt;
        union { // name: ro_ff_cur_tcnt, offset: 0x408
            struct {
                unsigned int ro_dect_ff_cur_tcnt : 32;
            } bits;
            unsigned int val;
        } ro_ff_cur_tcnt;
        union { // name: ro_ff_cur_bcnt, offset: 0x40c
            struct {
                unsigned int ro_dect_ff_cur_bcnt : 32;
            } bits;
            unsigned int val;
        } ro_ff_cur_bcnt;
        union { // name: ro_ff_nxt_tcnt, offset: 0x410
            struct {
                unsigned int ro_dect_ff_nxt_tcnt : 32;
            } bits;
            unsigned int val;
        } ro_ff_nxt_tcnt;
        union { // name: ro_ff_nxt_bcnt, offset: 0x414
            struct {
                unsigned int ro_dect_ff_nxt_bcnt : 32;
            } bits;
            unsigned int val;
        } ro_ff_nxt_bcnt;
        union { // name: ro_ff_ble_tcnt, offset: 0x418
            struct {
                unsigned int ro_dect_ff_ble_tcnt : 32;
            } bits;
            unsigned int val;
        } ro_ff_ble_tcnt;
        union { // name: ro_ff_ble_bcnt, offset: 0x41c
            struct {
                unsigned int ro_dect_ff_ble_bcnt : 32;
            } bits;
            unsigned int val;
        } ro_ff_ble_bcnt;
        union { // name: ro_ff_comb_nz, offset: 0x420
            struct {
                unsigned int ro_dect_ff_nz : 21;
                unsigned int reserve_0     : 11;
            } bits;
            unsigned int val;
        } ro_ff_comb_nz;
        union { // name: ro_ff_comb_f, offset: 0x424
            struct {
                unsigned int ro_dect_ff_comb_f : 21;
                unsigned int reserve_0         : 11;
            } bits;
            unsigned int val;
        } ro_ff_comb_f;
        union { // name: ro_osd_num, offset: 0x428
            struct {
                unsigned int ro_dect_osd_cnt : 4;
                unsigned int reserve_0       : 28;
            } bits;
            unsigned int val;
        } ro_osd_num;
        union { // name: ro_out_comb_cnt, offset: 0x42c
            struct {
                unsigned int ro_out_comb_cnt     : 16;
                unsigned int ro_out_osd_comb_cnt : 16;
            } bits;
            unsigned int val;
        } ro_out_comb_cnt;
        union { // name: ro_ff_gradt_tcnt, offset: 0x430
            struct {
                unsigned int ro_ff_gradt_tcnt : 28;
                unsigned int reserve_0        : 4;
            } bits;
            unsigned int val;
        } ro_ff_gradt_tcnt;
        union { // name: ro_ff_gradt_bcnt, offset: 0x434
            struct {
                unsigned int ro_ff_gradt_bcnt : 28;
                unsigned int reserve_0        : 4;
            } bits;
            unsigned int val;
        } ro_ff_gradt_bcnt;
        union { // name: ro_mc_vld_cnt, offset: 0x438
            struct {
                unsigned int ro_mc_vld_cnt : 15;
                unsigned int reserve_0     : 17;
            } bits;
            unsigned int val;
        } ro_mc_vld_cnt;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_1084_1088;
        union { // name: ro_osd_area0_x, offset: 0x440
            struct {
                unsigned int ro_x_sta0 : 11;
                unsigned int reserve_0 : 5;
                unsigned int ro_x_end0 : 11;
                unsigned int reserve_1 : 5;
            } bits;
            unsigned int val;
        } ro_osd_area0_x;
        union { // name: ro_osd_area0_y, offset: 0x444
            struct {
                unsigned int ro_y_sta0 : 11;
                unsigned int reserve_0 : 5;
                unsigned int ro_y_end0 : 11;
                unsigned int reserve_1 : 5;
            } bits;
            unsigned int val;
        } ro_osd_area0_y;
        union { // name: ro_osd_area1_x, offset: 0x448
            struct {
                unsigned int ro_x_sta1 : 11;
                unsigned int reserve_0 : 5;
                unsigned int ro_x_end1 : 11;
                unsigned int reserve_1 : 5;
            } bits;
            unsigned int val;
        } ro_osd_area1_x;
        union { // name: ro_osd_area1_y, offset: 0x44c
            struct {
                unsigned int ro_y_sta1 : 11;
                unsigned int reserve_0 : 5;
                unsigned int ro_y_end1 : 11;
                unsigned int reserve_1 : 5;
            } bits;
            unsigned int val;
        } ro_osd_area1_y;
        union { // name: ro_osd_area2_x, offset: 0x450
            struct {
                unsigned int ro_x_sta2 : 11;
                unsigned int reserve_0 : 5;
                unsigned int ro_x_end2 : 11;
                unsigned int reserve_1 : 5;
            } bits;
            unsigned int val;
        } ro_osd_area2_x;
        union { // name: ro_osd_area2_y, offset: 0x454
            struct {
                unsigned int ro_y_sta2 : 11;
                unsigned int reserve_0 : 5;
                unsigned int ro_y_end2 : 11;
                unsigned int reserve_1 : 5;
            } bits;
            unsigned int val;
        } ro_osd_area2_y;
        union { // name: ro_osd_area3_x, offset: 0x458
            struct {
                unsigned int ro_x_sta3 : 11;
                unsigned int reserve_0 : 5;
                unsigned int ro_x_end3 : 11;
                unsigned int reserve_1 : 5;
            } bits;
            unsigned int val;
        } ro_osd_area3_x;
        union { // name: ro_osd_area3_y, offset: 0x45c
            struct {
                unsigned int ro_y_sta3 : 11;
                unsigned int reserve_0 : 5;
                unsigned int ro_y_end3 : 11;
                unsigned int reserve_1 : 5;
            } bits;
            unsigned int val;
        } ro_osd_area3_y;
        union { // name: ro_osd_area4_x, offset: 0x460
            struct {
                unsigned int ro_x_sta4 : 11;
                unsigned int reserve_0 : 5;
                unsigned int ro_x_end4 : 11;
                unsigned int reserve_1 : 5;
            } bits;
            unsigned int val;
        } ro_osd_area4_x;
        union { // name: ro_osd_area4_y, offset: 0x464
            struct {
                unsigned int ro_y_sta4 : 11;
                unsigned int reserve_0 : 5;
                unsigned int ro_y_end4 : 11;
                unsigned int reserve_1 : 5;
            } bits;
            unsigned int val;
        } ro_osd_area4_y;
        union { // name: ro_osd_area5_x, offset: 0x468
            struct {
                unsigned int ro_x_sta5 : 11;
                unsigned int reserve_0 : 5;
                unsigned int ro_x_end5 : 11;
                unsigned int reserve_1 : 5;
            } bits;
            unsigned int val;
        } ro_osd_area5_x;
        union { // name: ro_osd_area5_y, offset: 0x46c
            struct {
                unsigned int ro_y_sta5 : 11;
                unsigned int reserve_0 : 5;
                unsigned int ro_y_end5 : 11;
                unsigned int reserve_1 : 5;
            } bits;
            unsigned int val;
        } ro_osd_area5_y;
        union { // name: ro_osd_area6_x, offset: 0x470
            struct {
                unsigned int ro_x_sta6 : 11;
                unsigned int reserve_0 : 5;
                unsigned int ro_x_end6 : 11;
                unsigned int reserve_1 : 5;
            } bits;
            unsigned int val;
        } ro_osd_area6_x;
        union { // name: ro_osd_area6_y, offset: 0x474
            struct {
                unsigned int ro_y_sta6 : 11;
                unsigned int reserve_0 : 5;
                unsigned int ro_y_end6 : 11;
                unsigned int reserve_1 : 5;
            } bits;
            unsigned int val;
        } ro_osd_area6_y;
        union { // name: ro_osd_area7_x, offset: 0x478
            struct {
                unsigned int ro_x_sta7 : 11;
                unsigned int reserve_0 : 5;
                unsigned int ro_x_end7 : 11;
                unsigned int reserve_1 : 5;
            } bits;
            unsigned int val;
        } ro_osd_area7_x;
        union { // name: ro_osd_area7_y, offset: 0x47c
            struct {
                unsigned int ro_y_sta7 : 11;
                unsigned int reserve_0 : 5;
                unsigned int ro_y_end7 : 11;
                unsigned int reserve_1 : 5;
            } bits;
            unsigned int val;
        } ro_osd_area7_y;
        union { // name: ro_mv_hist_bin0, offset: 0x480
            struct {
                unsigned int ro_mv_hist00 : 16;
                unsigned int ro_mv_hist01 : 16;
            } bits;
            unsigned int val;
        } ro_mv_hist_bin0;
        union { // name: ro_mv_hist_bin1, offset: 0x484
            struct {
                unsigned int ro_mv_hist02 : 16;
                unsigned int ro_mv_hist03 : 16;
            } bits;
            unsigned int val;
        } ro_mv_hist_bin1;
        union { // name: ro_mv_hist_bin2, offset: 0x488
            struct {
                unsigned int ro_mv_hist04 : 16;
                unsigned int ro_mv_hist05 : 16;
            } bits;
            unsigned int val;
        } ro_mv_hist_bin2;
        union { // name: ro_mv_hist_bin3, offset: 0x48c
            struct {
                unsigned int ro_mv_hist06 : 16;
                unsigned int ro_mv_hist07 : 16;
            } bits;
            unsigned int val;
        } ro_mv_hist_bin3;
        union { // name: ro_mv_hist_bin4, offset: 0x490
            struct {
                unsigned int ro_mv_hist08 : 16;
                unsigned int ro_mv_hist09 : 16;
            } bits;
            unsigned int val;
        } ro_mv_hist_bin4;
        union { // name: ro_mv_hist_bin5, offset: 0x494
            struct {
                unsigned int ro_mv_hist10 : 16;
                unsigned int ro_mv_hist11 : 16;
            } bits;
            unsigned int val;
        } ro_mv_hist_bin5;
        union { // name: ro_mv_hist_bin6, offset: 0x498
            struct {
                unsigned int ro_mv_hist12 : 16;
                unsigned int ro_mv_hist13 : 16;
            } bits;
            unsigned int val;
        } ro_mv_hist_bin6;
        union { // name: ro_mv_hist_bin7, offset: 0x49c
            struct {
                unsigned int ro_mv_hist14 : 16;
                unsigned int ro_mv_hist15 : 16;
            } bits;
            unsigned int val;
        } ro_mv_hist_bin7;
        union { // name: ro_mv_hist_bin8, offset: 0x4a0
            struct {
                unsigned int ro_mv_hist16 : 16;
                unsigned int ro_mv_hist17 : 16;
            } bits;
            unsigned int val;
        } ro_mv_hist_bin8;
        union { // name: ro_mv_hist_bin9, offset: 0x4a4
            struct {
                unsigned int ro_mv_hist18 : 16;
                unsigned int ro_mv_hist19 : 16;
            } bits;
            unsigned int val;
        } ro_mv_hist_bin9;
        union { // name: ro_mv_hist_bin10, offset: 0x4a8
            struct {
                unsigned int ro_mv_hist20 : 16;
                unsigned int ro_mv_hist21 : 16;
            } bits;
            unsigned int val;
        } ro_mv_hist_bin10;
        union { // name: ro_mv_hist_bin11, offset: 0x4ac
            struct {
                unsigned int ro_mv_hist22 : 16;
                unsigned int ro_mv_hist23 : 16;
            } bits;
            unsigned int val;
        } ro_mv_hist_bin11;
        union { // name: ro_mv_hist_bin12, offset: 0x4b0
            struct {
                unsigned int ro_mv_hist24 : 16;
                unsigned int ro_mv_hist25 : 16;
            } bits;
            unsigned int val;
        } ro_mv_hist_bin12;
        union { // name: ro_mv_hist_bin13, offset: 0x4b4
            struct {
                unsigned int ro_mv_hist26 : 16;
                unsigned int ro_mv_hist27 : 16;
            } bits;
            unsigned int val;
        } ro_mv_hist_bin13;
        union { // name: ro_mv_hist_bin14, offset: 0x4b8
            struct {
                unsigned int ro_mv_hist28 : 16;
                unsigned int ro_mv_hist29 : 16;
            } bits;
            unsigned int val;
        } ro_mv_hist_bin14;
        union { // name: ro_mv_hist_bin15, offset: 0x4bc
            struct {
                unsigned int ro_mv_hist30 : 16;
                unsigned int ro_mv_hist31 : 16;
            } bits;
            unsigned int val;
        } ro_mv_hist_bin15;
        union { // name: ro_mv_hist_bin16, offset: 0x4c0
            struct {
                unsigned int ro_mv_hist32 : 16;
                unsigned int ro_mv_hist33 : 16;
            } bits;
            unsigned int val;
        } ro_mv_hist_bin16;
        union { // name: ro_mv_hist_bin17, offset: 0x4c4
            struct {
                unsigned int ro_mv_hist34 : 16;
                unsigned int ro_mv_hist35 : 16;
            } bits;
            unsigned int val;
        } ro_mv_hist_bin17;
        union { // name: ro_mv_hist_bin18, offset: 0x4c8
            struct {
                unsigned int ro_mv_hist36 : 16;
                unsigned int ro_mv_hist37 : 16;
            } bits;
            unsigned int val;
        } ro_mv_hist_bin18;
        union { // name: ro_mv_hist_bin19, offset: 0x4cc
            struct {
                unsigned int ro_mv_hist38 : 16;
                unsigned int ro_mv_hist39 : 16;
            } bits;
            unsigned int val;
        } ro_mv_hist_bin19;
        union { // name: ro_mv_hist_bin20, offset: 0x4d0
            struct {
                unsigned int ro_mv_hist40 : 16;
                unsigned int ro_mv_hist41 : 16;
            } bits;
            unsigned int val;
        } ro_mv_hist_bin20;
        union { // name: ro_mv_hist_bin21, offset: 0x4d4
            struct {
                unsigned int ro_mv_hist42 : 16;
                unsigned int ro_mv_hist43 : 16;
            } bits;
            unsigned int val;
        } ro_mv_hist_bin21;
        union { // name: ro_mv_hist_bin22, offset: 0x4d8
            struct {
                unsigned int ro_mv_hist44 : 16;
                unsigned int ro_mv_hist45 : 16;
            } bits;
            unsigned int val;
        } ro_mv_hist_bin22;
        union { // name: ro_mv_hist_bin23, offset: 0x4dc
            struct {
                unsigned int ro_mv_hist46 : 16;
                unsigned int ro_mv_hist47 : 16;
            } bits;
            unsigned int val;
        } ro_mv_hist_bin23;
        union { // name: ro_mv_hist_bin24, offset: 0x4e0
            struct {
                unsigned int ro_mv_hist48 : 16;
                unsigned int ro_mv_hist49 : 16;
            } bits;
            unsigned int val;
        } ro_mv_hist_bin24;
        union { // name: ro_mv_hist_bin25, offset: 0x4e4
            struct {
                unsigned int ro_mv_hist50 : 16;
                unsigned int ro_mv_hist51 : 16;
            } bits;
            unsigned int val;
        } ro_mv_hist_bin25;
        union { // name: ro_mv_hist_bin26, offset: 0x4e8
            struct {
                unsigned int ro_mv_hist52 : 16;
                unsigned int ro_mv_hist53 : 16;
            } bits;
            unsigned int val;
        } ro_mv_hist_bin26;
        union { // name: ro_mv_hist_bin27, offset: 0x4ec
            struct {
                unsigned int ro_mv_hist54 : 16;
                unsigned int ro_mv_hist55 : 16;
            } bits;
            unsigned int val;
        } ro_mv_hist_bin27;
        struct {
            unsigned int reserve_data[68];
        } reserve_reg_1264_1536;
        union { // name: perf_latency_ctrl0, offset: 0x600
            struct {
                unsigned int sw_axi_perf_work_e   : 1;
                unsigned int sw_axi_perf_clr_e    : 1;
                unsigned int sw_axi_perf_frm_type : 1;
                unsigned int sw_axi_cnt_type      : 1;
                unsigned int sw_rd_latency_id     : 4;
                unsigned int sw_rd_latency_thr    : 12;
                unsigned int reserve_0            : 12;
            } bits;
            unsigned int val;
        } perf_latency_ctrl0;
        union { // name: perf_latency_ctrl1, offset: 0x604
            struct {
                unsigned int sw_addr_align_type : 2;
                unsigned int sw_ar_cnt_id_type  : 1;
                unsigned int sw_aw_cnt_id_type  : 1;
                unsigned int sw_ar_count_id     : 4;
                unsigned int sw_aw_count_id     : 4;
                unsigned int reserve_0          : 20;
            } bits;
            unsigned int val;
        } perf_latency_ctrl1;
        union { // name: perf_rd_max_latency_num, offset: 0x608
            struct {
                unsigned int rd_max_latency_num : 16;
                unsigned int reserve_0          : 16;
            } bits;
            unsigned int val;
        } perf_rd_max_latency_num;
        union { // name: perf_rd_latency_samp_num, offset: 0x60c
            struct {
                unsigned int rd_latency_thr_num : 32;
            } bits;
            unsigned int val;
        } perf_rd_latency_samp_num;
        union { // name: perf_rd_latency_acc_sum, offset: 0x610
            struct {
                unsigned int rd_latency_acc_sum : 32;
            } bits;
            unsigned int val;
        } perf_rd_latency_acc_sum;
        union { // name: perf_rd_axi_total_byte, offset: 0x614
            struct {
                unsigned int perf_rd_axi_total_byte : 32;
            } bits;
            unsigned int val;
        } perf_rd_axi_total_byte;
        union { // name: perf_wr_axi_total_byte, offset: 0x618
            struct {
                unsigned int perf_wr_axi_total_byte : 32;
            } bits;
            unsigned int val;
        } perf_wr_axi_total_byte;
        union { // name: perf_working_cnt, offset: 0x61c
            struct {
                unsigned int perf_working_cnt : 32;
            } bits;
            unsigned int val;
        } perf_working_cnt;
        struct {
            unsigned int reserve_data[120];
        } reserve_reg_1568_2048;
        union { // name: mmu_dte_addr, offset: 0x800
            struct {
                unsigned int mmu_dte_addr : 32;
            } bits;
            unsigned int val;
        } mmu_dte_addr;
        union { // name: mmu_status, offset: 0x804
            struct {
                unsigned int mmu_paging_enabled      : 1;
                unsigned int mmu_page_fault_active   : 1;
                unsigned int mmu_stall_active        : 1;
                unsigned int mmu_idle                : 1;
                unsigned int mmu_replay_buffer_empty : 1;
                unsigned int mmu_page_fault_is_write : 1;
                unsigned int mmu_page_fault_bus_id   : 5;
                unsigned int reserve_0               : 21;
            } bits;
            unsigned int val;
        } mmu_status;
        union { // name: mmu_cmd, offset: 0x808
            struct {
                unsigned int mmu_cmd   : 3;
                unsigned int reserve_0 : 29;
            } bits;
            unsigned int val;
        } mmu_cmd;
        union { // name: mmu_page_fault_addr, offset: 0x80c
            struct {
                unsigned int mmu_page_fault_addr : 32;
            } bits;
            unsigned int val;
        } mmu_page_fault_addr;
        union { // name: mmu_zap_one_line, offset: 0x810
            struct {
                unsigned int mmu_zap_one_line : 1;
                unsigned int reserve_0        : 31;
            } bits;
            unsigned int val;
        } mmu_zap_one_line;
        union { // name: mmu_int_rawstat, offset: 0x814
            struct {
                unsigned int page_fault     : 1;
                unsigned int read_bus_error : 1;
                unsigned int reserve_0      : 30;
            } bits;
            unsigned int val;
        } mmu_int_rawstat;
        union { // name: mmu_int_clear, offset: 0x818
            struct {
                unsigned int page_fault_clear     : 1;
                unsigned int read_bus_error_clear : 1;
                unsigned int reserve_0            : 30;
            } bits;
            unsigned int val;
        } mmu_int_clear;
        union { // name: mmu_int_mask, offset: 0x81c
            struct {
                unsigned int page_fault_int_en     : 1;
                unsigned int read_bus_error_int_en : 1;
                unsigned int reserve_0             : 30;
            } bits;
            unsigned int val;
        } mmu_int_mask;
        union { // name: mmu_int_status, offset: 0x820
            struct {
                unsigned int page_fault     : 1;
                unsigned int read_bus_error : 1;
                unsigned int reserve_0      : 30;
            } bits;
            unsigned int val;
        } mmu_int_status;
        union { // name: mmu_auto_gating, offset: 0x824
            struct {
                unsigned int mmu_auto_gating : 1;
                unsigned int reserve_0       : 31;
            } bits;
            unsigned int val;
        } mmu_auto_gating;
        union { // name: mmu_id, offset: 0x828
            struct {
                unsigned int reg_load_mmu_en : 1;
                unsigned int reserve_0       : 3;
                unsigned int mmu_axi_id      : 4;
                unsigned int reserve_1       : 24;
            } bits;
            unsigned int val;
        } mmu_id;
    } regs;
    unsigned int data[523];
} iep2_rk3528_u;

// 0x00001000
typedef union vdpp_rk3528 {
    struct {
        union { // name: frm_start, offset: 0x0
            struct {
                unsigned int sw_vdpp_frm_en : 1;
                unsigned int reserve_0      : 31;
            } bits;
            unsigned int val;
        } frm_start;
        union { // name: config0, offset: 0x4
            struct {
                unsigned int sw_vdpp_src_fmt         : 2;
                unsigned int reserve_0               : 2;
                unsigned int sw_vdpp_src_yuv_swap    : 2;
                unsigned int reserve_1               : 2;
                unsigned int sw_vdpp_dst_fmt         : 2;
                unsigned int sw_vdpp_yuvout_diff_en  : 1;
                unsigned int reserve_2               : 1;
                unsigned int sw_vdpp_dst_yuv_swap    : 2;
                unsigned int reserve_3               : 2;
                unsigned int sw_vdpp_debug_data_en   : 1;
                unsigned int reserve_4               : 3;
                unsigned int sw_vdpp_rst_protect_dis : 1;
                unsigned int sys_vdpp_sreset_p       : 1;
                unsigned int sw_vdpp_init_dis        : 1;
                unsigned int reserve_5               : 1;
                unsigned int sw_vdpp_dmsr_en         : 1;
                unsigned int sw_dci_en               : 1;
                unsigned int reserve_6               : 6;
            } bits;
            unsigned int val;
        } config0;
        union { // name: working_mode, offset: 0x8
            struct {
                unsigned int sw_vdpp_working_mode : 2;
                unsigned int reserve_0            : 30;
            } bits;
            unsigned int val;
        } working_mode;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_12_16;
        union { // name: gating_ctrl, offset: 0x10
            struct {
                unsigned int sw_vdpp_clk_on : 1;
                unsigned int reserve_0      : 7;
                unsigned int sw_ctrl_clk_on : 1;
                unsigned int sw_ram_clk_on  : 1;
                unsigned int sw_dma_clk_on  : 1;
                unsigned int sw_reg_clk_on  : 1;
                unsigned int reserve_1      : 20;
            } bits;
            unsigned int val;
        } gating_ctrl;
        union { // name: status, offset: 0x14
            struct {
                unsigned int ro_arst_finish_done : 1;
                unsigned int reserve_0           : 31;
            } bits;
            unsigned int val;
        } status;
        struct {
            unsigned int reserve_data[2];
        } reserve_reg_24_32;
        union { // name: int_en, offset: 0x20
            struct {
                unsigned int sw_vdpp_frm_done_en     : 1;
                unsigned int sw_vdpp_osd_max_en      : 1;
                unsigned int reserve_0               : 2;
                unsigned int sw_vdpp_bus_error_en    : 1;
                unsigned int sw_vdpp_timeout_int_en  : 1;
                unsigned int sw_vdpp_config_error_en : 1;
                unsigned int reserve_1               : 25;
            } bits;
            unsigned int val;
        } int_en;
        union { // name: int_clr, offset: 0x24
            struct {
                unsigned int sw_vdpp_frm_done_clr     : 1;
                unsigned int sw_vdpp_osd_max_clr      : 1;
                unsigned int reserve_0                : 2;
                unsigned int sw_vdpp_bus_error_clr    : 1;
                unsigned int sw_vdpp_timeout_int_clr  : 1;
                unsigned int sw_vdpp_config_error_clr : 1;
                unsigned int reserve_1                : 25;
            } bits;
            unsigned int val;
        } int_clr;
        union { // name: int_sts, offset: 0x28
            struct {
                unsigned int ro_frm_done_sts     : 1;
                unsigned int ro_osd_max_sts      : 1;
                unsigned int reserve_0           : 2;
                unsigned int ro_bus_error_sts    : 1;
                unsigned int ro_timeout_sts      : 1;
                unsigned int ro_config_error_sts : 1;
                unsigned int reserve_1           : 25;
            } bits;
            unsigned int val;
        } int_sts;
        union { // name: int_raw_sts, offset: 0x2c
            struct {
                unsigned int ro_frm_done_raw     : 1;
                unsigned int ro_osd_max_raw      : 1;
                unsigned int reserve_0           : 2;
                unsigned int ro_bus_error_raw    : 1;
                unsigned int ro_timeout_raw      : 1;
                unsigned int ro_config_error_raw : 1;
                unsigned int reserve_1           : 25;
            } bits;
            unsigned int val;
        } int_raw_sts;
        union { // name: vir_src_img_width, offset: 0x30
            struct {
                unsigned int sw_vdpp_src_vir_y_stride : 16;
                unsigned int reserve_0                : 16;
            } bits;
            unsigned int val;
        } vir_src_img_width;
        union { // name: vir_dst_img_width, offset: 0x34
            struct {
                unsigned int sw_vdpp_dst_vir_y_stride : 16;
                unsigned int reserve_0                : 16;
            } bits;
            unsigned int val;
        } vir_dst_img_width;
        union { // name: src_img_size, offset: 0x38
            struct {
                unsigned int sw_vdpp_src_pic_width       : 11;
                unsigned int reserve_0                   : 1;
                unsigned int sw_vdpp_src_right_redundant : 4;
                unsigned int sw_vdpp_src_pic_height      : 11;
                unsigned int reserve_1                   : 1;
                unsigned int sw_vdpp_src_down_redundant  : 3;
                unsigned int reserve_2                   : 1;
            } bits;
            unsigned int val;
        } src_img_size;
        union { // name: dst_img_size, offset: 0x3c
            struct {
                unsigned int sw_vdpp_dst_pic_width       : 11;
                unsigned int reserve_0                   : 1;
                unsigned int sw_vdpp_dst_right_redundant : 4;
                unsigned int sw_vdpp_dst_pic_height      : 11;
                unsigned int reserve_1                   : 5;
            } bits;
            unsigned int val;
        } dst_img_size;
        union { // name: dst_img_size_c, offset: 0x40
            struct {
                unsigned int sw_vdpp_dst_pic_width_c       : 11;
                unsigned int reserve_0                     : 1;
                unsigned int sw_vdpp_dst_right_redundant_c : 4;
                unsigned int sw_vdpp_dst_pic_height_c      : 11;
                unsigned int reserve_1                     : 5;
            } bits;
            unsigned int val;
        } dst_img_size_c;
        struct {
            unsigned int reserve_data[3];
        } reserve_reg_68_80;
        union { // name: timeout_cfg, offset: 0x50
            struct {
                unsigned int sw_vdpp_timeout_cnt : 31;
                unsigned int sw_vdpp_timeout_en  : 1;
            } bits;
            unsigned int val;
        } timeout_cfg;
        union { // name: version_info, offset: 0x54
            struct {
                unsigned int svnbuild : 20;
                unsigned int minor    : 8;
                unsigned int major    : 4;
            } bits;
            unsigned int val;
        } version_info;
        union { // name: dbg_frm_cnt, offset: 0x58
            struct {
                unsigned int dbg_frm_cnt : 16;
                unsigned int reserve_0   : 16;
            } bits;
            unsigned int val;
        } dbg_frm_cnt;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_92_96;
        union { // name: src_addr_y, offset: 0x60
            struct {
                unsigned int sw_vdpp_src_addr_y : 32;
            } bits;
            unsigned int val;
        } src_addr_y;
        union { // name: src_addr_uv, offset: 0x64
            struct {
                unsigned int sw_vdpp_src_addr_uv : 32;
            } bits;
            unsigned int val;
        } src_addr_uv;
        union { // name: dst_addr_y, offset: 0x68
            struct {
                unsigned int sw_vdpp_dst_addr_y : 32;
            } bits;
            unsigned int val;
        } dst_addr_y;
        union { // name: dst_addr_uv, offset: 0x6c
            struct {
                unsigned int sw_vdpp_dst_addr_uv : 32;
            } bits;
            unsigned int val;
        } dst_addr_uv;
        struct {
            unsigned int reserve_data[4];
        } reserve_reg_112_128;
        union { // name: dmsr_edge_thre0, offset: 0x80
            struct {
                unsigned int sw_dmsr_edge_low_thre_0  : 16;
                unsigned int sw_dmsr_edge_high_thre_0 : 16;
            } bits;
            unsigned int val;
        } dmsr_edge_thre0;
        union { // name: dmsr_edge_thre1, offset: 0x84
            struct {
                unsigned int sw_dmsr_edge_low_thre_1  : 16;
                unsigned int sw_dmsr_edge_high_thre_1 : 16;
            } bits;
            unsigned int val;
        } dmsr_edge_thre1;
        union { // name: dmsr_edge_thre2, offset: 0x88
            struct {
                unsigned int sw_dmsr_edge_low_thre_2  : 16;
                unsigned int sw_dmsr_edge_high_thre_2 : 16;
            } bits;
            unsigned int val;
        } dmsr_edge_thre2;
        union { // name: dmsr_edge_thre3, offset: 0x8c
            struct {
                unsigned int sw_dmsr_edge_low_thre_3  : 16;
                unsigned int sw_dmsr_edge_high_thre_3 : 16;
            } bits;
            unsigned int val;
        } dmsr_edge_thre3;
        union { // name: dmsr_edge_thre4, offset: 0x90
            struct {
                unsigned int sw_dmsr_edge_low_thre_4  : 16;
                unsigned int sw_dmsr_edge_high_thre_4 : 16;
            } bits;
            unsigned int val;
        } dmsr_edge_thre4;
        union { // name: dmsr_edge_thre5, offset: 0x94
            struct {
                unsigned int sw_dmsr_edge_low_thre_5  : 16;
                unsigned int sw_dmsr_edge_high_thre_5 : 16;
            } bits;
            unsigned int val;
        } dmsr_edge_thre5;
        union { // name: dmsr_edge_thre6, offset: 0x98
            struct {
                unsigned int sw_dmsr_edge_low_thre_6  : 16;
                unsigned int sw_dmsr_edge_high_thre_6 : 16;
            } bits;
            unsigned int val;
        } dmsr_edge_thre6;
        union { // name: dmsr_edge_k0, offset: 0x9c
            struct {
                unsigned int sw_dmsr_edge_k_0 : 16;
                unsigned int sw_dmsr_edge_k_1 : 16;
            } bits;
            unsigned int val;
        } dmsr_edge_k0;
        union { // name: dmsr_edge_k1, offset: 0xa0
            struct {
                unsigned int sw_dmsr_edge_k_2 : 16;
                unsigned int sw_dmsr_edge_k_3 : 16;
            } bits;
            unsigned int val;
        } dmsr_edge_k1;
        union { // name: dmsr_edge_k2, offset: 0xa4
            struct {
                unsigned int sw_dmsr_edge_k_4 : 16;
                unsigned int sw_dmsr_edge_k_5 : 16;
            } bits;
            unsigned int val;
        } dmsr_edge_k2;
        union { // name: dmsr_edge_k3, offset: 0xa8
            struct {
                unsigned int sw_dmsr_edge_k_6            : 16;
                unsigned int sw_dmsr_dir_contrast_conf_f : 16;
            } bits;
            unsigned int val;
        } dmsr_edge_k3;
        union { // name: dmsr_dir_contrast_conf_x, offset: 0xac
            struct {
                unsigned int sw_dmsr_dir_contrast_conf_x0 : 16;
                unsigned int sw_dmsr_dir_contrast_conf_x1 : 16;
            } bits;
            unsigned int val;
        } dmsr_dir_contrast_conf_x;
        union { // name: dmsr_dir_contrast_conf_y, offset: 0xb0
            struct {
                unsigned int sw_dmsr_dir_contrast_conf_y0 : 16;
                unsigned int sw_dmsr_dir_contrast_conf_y1 : 16;
            } bits;
            unsigned int val;
        } dmsr_dir_contrast_conf_y;
        union { // name: dmsr_flatness_thre, offset: 0xb4
            struct {
                unsigned int sw_dmsr_var_th : 16;
                unsigned int reserve_0      : 16;
            } bits;
            unsigned int val;
        } dmsr_flatness_thre;
        union { // name: dmsr_diff_coring_thre, offset: 0xb8
            struct {
                unsigned int sw_dmsr_diff_coring_th0 : 8;
                unsigned int sw_dmsr_diff_coring_th1 : 8;
                unsigned int reserve_0               : 16;
            } bits;
            unsigned int val;
        } dmsr_diff_coring_thre;
        union { // name: dmsr_diff_coring_weight, offset: 0xbc
            struct {
                unsigned int sw_dmsr_diff_coring_wgt0 : 6;
                unsigned int reserve_0                : 2;
                unsigned int sw_dmsr_diff_coring_wgt1 : 6;
                unsigned int reserve_1                : 2;
                unsigned int sw_dmsr_diff_coring_wgt2 : 6;
                unsigned int reserve_2                : 10;
            } bits;
            unsigned int val;
        } dmsr_diff_coring_weight;
        union { // name: dmsr_diff_coring_y, offset: 0xc0
            struct {
                unsigned int sw_dmsr_diff_coring_y0 : 14;
                unsigned int reserve_0              : 2;
                unsigned int sw_dmsr_diff_coring_y1 : 14;
                unsigned int reserve_1              : 2;
            } bits;
            unsigned int val;
        } dmsr_diff_coring_y;
        union { // name: dmsr_filter_primary_tap_weight_gain, offset: 0xc4
            struct {
                unsigned int sw_dmsr_wgt_pri_gain_1_odd  : 6;
                unsigned int reserve_0                   : 2;
                unsigned int sw_dmsr_wgt_pri_gain_1_even : 6;
                unsigned int reserve_1                   : 2;
                unsigned int sw_dmsr_wgt_pri_gain_2_odd  : 6;
                unsigned int reserve_2                   : 2;
                unsigned int sw_dmsr_wgt_pri_gain_2_even : 6;
                unsigned int reserve_3                   : 2;
            } bits;
            unsigned int val;
        } dmsr_filter_primary_tap_weight_gain;
        union { // name: dmsr_filter_secondary_tap_weight_gain, offset: 0xc8
            struct {
                unsigned int sw_dmsr_wgt_sec_gain_1 : 6;
                unsigned int reserve_0              : 2;
                unsigned int sw_dmsr_wgt_sec_gain_2 : 6;
                unsigned int reserve_1              : 18;
            } bits;
            unsigned int val;
        } dmsr_filter_secondary_tap_weight_gain;
        union { // name: dmsr_filter_strength, offset: 0xcc
            struct {
                unsigned int sw_dmsr_strength_pri : 5;
                unsigned int reserve_0            : 3;
                unsigned int sw_dmsr_strength_sec : 5;
                unsigned int reserve_1            : 3;
                unsigned int sw_dmsr_dump         : 4;
                unsigned int reserve_2            : 12;
            } bits;
            unsigned int val;
        } dmsr_filter_strength;
        union { // name: dmsr_dbg_mode, offset: 0xd0
            struct {
                unsigned int sw_dmsr_obv_point_h : 12;
                unsigned int sw_dmsr_obv_point_v : 12;
                unsigned int sw_dmsr_obv_enable  : 1;
                unsigned int sw_dmsr_obv_mode    : 1;
                unsigned int reserve_0           : 6;
            } bits;
            unsigned int val;
        } dmsr_dbg_mode;
    } regs;
    unsigned int data[53];
} vdpp_rk3528_u;

// 0x00002000
typedef union zme_rk3528 {
    struct {
        union { // name: yrgb_hor_coe0_10, offset: 0x0
            struct {
                unsigned int yrgb_hor_coe0_0 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_hor_coe0_1 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe0_10;
        union { // name: yrgb_hor_coe0_32, offset: 0x4
            struct {
                unsigned int yrgb_hor_coe0_2 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_hor_coe0_3 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe0_32;
        union { // name: yrgb_hor_coe0_54, offset: 0x8
            struct {
                unsigned int yrgb_hor_coe0_4 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_hor_coe0_5 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe0_54;
        union { // name: yrgb_hor_coe0_76, offset: 0xc
            struct {
                unsigned int yrgb_hor_coe0_6 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_hor_coe0_7 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe0_76;
        union { // name: yrgb_hor_coe1_10, offset: 0x10
            struct {
                unsigned int yrgb_hor_coe1_0 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_hor_coe1_1 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe1_10;
        union { // name: yrgb_hor_coe1_32, offset: 0x14
            struct {
                unsigned int yrgb_hor_coe1_2 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_hor_coe1_3 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe1_32;
        union { // name: yrgb_hor_coe1_54, offset: 0x18
            struct {
                unsigned int yrgb_hor_coe1_4 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_hor_coe1_5 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe1_54;
        union { // name: yrgb_hor_coe1_76, offset: 0x1c
            struct {
                unsigned int yrgb_hor_coe1_6 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_hor_coe1_7 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe1_76;
        union { // name: yrgb_hor_coe2_10, offset: 0x20
            struct {
                unsigned int yrgb_hor_coe2_0 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_hor_coe2_1 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe2_10;
        union { // name: yrgb_hor_coe2_32, offset: 0x24
            struct {
                unsigned int yrgb_hor_coe2_2 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_hor_coe2_3 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe2_32;
        union { // name: yrgb_hor_coe2_54, offset: 0x28
            struct {
                unsigned int yrgb_hor_coe2_4 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_hor_coe2_5 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe2_54;
        union { // name: yrgb_hor_coe2_76, offset: 0x2c
            struct {
                unsigned int yrgb_hor_coe2_6 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_hor_coe2_7 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe2_76;
        union { // name: yrgb_hor_coe3_10, offset: 0x30
            struct {
                unsigned int yrgb_hor_coe3_0 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_hor_coe3_1 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe3_10;
        union { // name: yrgb_hor_coe3_32, offset: 0x34
            struct {
                unsigned int yrgb_hor_coe3_2 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_hor_coe3_3 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe3_32;
        union { // name: yrgb_hor_coe3_54, offset: 0x38
            struct {
                unsigned int yrgb_hor_coe3_4 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_hor_coe3_5 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe3_54;
        union { // name: yrgb_hor_coe3_76, offset: 0x3c
            struct {
                unsigned int yrgb_hor_coe3_6 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_hor_coe3_7 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe3_76;
        union { // name: yrgb_hor_coe4_10, offset: 0x40
            struct {
                unsigned int yrgb_hor_coe4_0 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_hor_coe4_1 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe4_10;
        union { // name: yrgb_hor_coe4_32, offset: 0x44
            struct {
                unsigned int yrgb_hor_coe4_2 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_hor_coe4_3 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe4_32;
        union { // name: yrgb_hor_coe4_54, offset: 0x48
            struct {
                unsigned int yrgb_hor_coe4_4 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_hor_coe4_5 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe4_54;
        union { // name: yrgb_hor_coe4_76, offset: 0x4c
            struct {
                unsigned int yrgb_hor_coe4_6 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_hor_coe4_7 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe4_76;
        union { // name: yrgb_hor_coe5_10, offset: 0x50
            struct {
                unsigned int yrgb_hor_coe5_0 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_hor_coe5_1 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe5_10;
        union { // name: yrgb_hor_coe5_32, offset: 0x54
            struct {
                unsigned int yrgb_hor_coe5_2 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_hor_coe5_3 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe5_32;
        union { // name: yrgb_hor_coe5_54, offset: 0x58
            struct {
                unsigned int yrgb_hor_coe5_4 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_hor_coe5_5 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe5_54;
        union { // name: yrgb_hor_coe5_76, offset: 0x5c
            struct {
                unsigned int yrgb_hor_coe5_6 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_hor_coe5_7 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe5_76;
        union { // name: yrgb_hor_coe6_10, offset: 0x60
            struct {
                unsigned int yrgb_hor_coe6_0 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_hor_coe6_1 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe6_10;
        union { // name: yrgb_hor_coe6_32, offset: 0x64
            struct {
                unsigned int yrgb_hor_coe6_2 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_hor_coe6_3 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe6_32;
        union { // name: yrgb_hor_coe6_54, offset: 0x68
            struct {
                unsigned int yrgb_hor_coe6_4 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_hor_coe6_5 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe6_54;
        union { // name: yrgb_hor_coe6_76, offset: 0x6c
            struct {
                unsigned int yrgb_hor_coe6_6 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_hor_coe6_7 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe6_76;
        union { // name: yrgb_hor_coe7_10, offset: 0x70
            struct {
                unsigned int yrgb_hor_coe7_0 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_hor_coe7_1 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe7_10;
        union { // name: yrgb_hor_coe7_32, offset: 0x74
            struct {
                unsigned int yrgb_hor_coe7_2 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_hor_coe7_3 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe7_32;
        union { // name: yrgb_hor_coe7_54, offset: 0x78
            struct {
                unsigned int yrgb_hor_coe7_4 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_hor_coe7_5 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe7_54;
        union { // name: yrgb_hor_coe7_76, offset: 0x7c
            struct {
                unsigned int yrgb_hor_coe7_6 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_hor_coe7_7 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe7_76;
        union { // name: yrgb_hor_coe8_10, offset: 0x80
            struct {
                unsigned int yrgb_hor_coe8_0 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_hor_coe8_1 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe8_10;
        union { // name: yrgb_hor_coe8_32, offset: 0x84
            struct {
                unsigned int yrgb_hor_coe8_2 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_hor_coe8_3 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe8_32;
        union { // name: yrgb_hor_coe8_54, offset: 0x88
            struct {
                unsigned int yrgb_hor_coe8_4 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_hor_coe8_5 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe8_54;
        union { // name: yrgb_hor_coe8_76, offset: 0x8c
            struct {
                unsigned int yrgb_hor_coe8_6 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_hor_coe8_7 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe8_76;
        union { // name: yrgb_hor_coe9_10, offset: 0x90
            struct {
                unsigned int yrgb_hor_coe9_0 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_hor_coe9_1 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe9_10;
        union { // name: yrgb_hor_coe9_32, offset: 0x94
            struct {
                unsigned int yrgb_hor_coe9_2 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_hor_coe9_3 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe9_32;
        union { // name: yrgb_hor_coe9_54, offset: 0x98
            struct {
                unsigned int yrgb_hor_coe9_4 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_hor_coe9_5 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe9_54;
        union { // name: yrgb_hor_coe9_76, offset: 0x9c
            struct {
                unsigned int yrgb_hor_coe9_6 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_hor_coe9_7 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe9_76;
        union { // name: yrgb_hor_coe10_10, offset: 0xa0
            struct {
                unsigned int yrgb_hor_coe10_0 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_hor_coe10_1 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe10_10;
        union { // name: yrgb_hor_coe10_32, offset: 0xa4
            struct {
                unsigned int yrgb_hor_coe10_2 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_hor_coe10_3 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe10_32;
        union { // name: yrgb_hor_coe10_54, offset: 0xa8
            struct {
                unsigned int yrgb_hor_coe10_4 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_hor_coe10_5 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe10_54;
        union { // name: yrgb_hor_coe10_76, offset: 0xac
            struct {
                unsigned int yrgb_hor_coe10_6 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_hor_coe10_7 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe10_76;
        union { // name: yrgb_hor_coe11_10, offset: 0xb0
            struct {
                unsigned int yrgb_hor_coe11_0 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_hor_coe11_1 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe11_10;
        union { // name: yrgb_hor_coe11_32, offset: 0xb4
            struct {
                unsigned int yrgb_hor_coe11_2 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_hor_coe11_3 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe11_32;
        union { // name: yrgb_hor_coe11_54, offset: 0xb8
            struct {
                unsigned int yrgb_hor_coe11_4 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_hor_coe11_5 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe11_54;
        union { // name: yrgb_hor_coe11_76, offset: 0xbc
            struct {
                unsigned int yrgb_hor_coe11_6 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_hor_coe11_7 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe11_76;
        union { // name: yrgb_hor_coe12_10, offset: 0xc0
            struct {
                unsigned int yrgb_hor_coe12_0 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_hor_coe12_1 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe12_10;
        union { // name: yrgb_hor_coe12_32, offset: 0xc4
            struct {
                unsigned int yrgb_hor_coe12_2 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_hor_coe12_3 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe12_32;
        union { // name: yrgb_hor_coe12_54, offset: 0xc8
            struct {
                unsigned int yrgb_hor_coe12_4 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_hor_coe12_5 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe12_54;
        union { // name: yrgb_hor_coe12_76, offset: 0xcc
            struct {
                unsigned int yrgb_hor_coe12_6 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_hor_coe12_7 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe12_76;
        union { // name: yrgb_hor_coe13_10, offset: 0xd0
            struct {
                unsigned int yrgb_hor_coe13_0 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_hor_coe13_1 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe13_10;
        union { // name: yrgb_hor_coe13_32, offset: 0xd4
            struct {
                unsigned int yrgb_hor_coe13_2 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_hor_coe13_3 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe13_32;
        union { // name: yrgb_hor_coe13_54, offset: 0xd8
            struct {
                unsigned int yrgb_hor_coe13_4 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_hor_coe13_5 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe13_54;
        union { // name: yrgb_hor_coe13_76, offset: 0xdc
            struct {
                unsigned int yrgb_hor_coe13_6 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_hor_coe13_7 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe13_76;
        union { // name: yrgb_hor_coe14_10, offset: 0xe0
            struct {
                unsigned int yrgb_hor_coe14_0 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_hor_coe14_1 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe14_10;
        union { // name: yrgb_hor_coe14_32, offset: 0xe4
            struct {
                unsigned int yrgb_hor_coe14_2 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_hor_coe14_3 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe14_32;
        union { // name: yrgb_hor_coe14_54, offset: 0xe8
            struct {
                unsigned int yrgb_hor_coe14_4 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_hor_coe14_5 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe14_54;
        union { // name: yrgb_hor_coe14_76, offset: 0xec
            struct {
                unsigned int yrgb_hor_coe14_6 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_hor_coe14_7 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe14_76;
        union { // name: yrgb_hor_coe15_10, offset: 0xf0
            struct {
                unsigned int yrgb_hor_coe15_0 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_hor_coe15_1 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe15_10;
        union { // name: yrgb_hor_coe15_32, offset: 0xf4
            struct {
                unsigned int yrgb_hor_coe15_2 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_hor_coe15_3 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe15_32;
        union { // name: yrgb_hor_coe15_54, offset: 0xf8
            struct {
                unsigned int yrgb_hor_coe15_4 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_hor_coe15_5 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe15_54;
        union { // name: yrgb_hor_coe15_76, offset: 0xfc
            struct {
                unsigned int yrgb_hor_coe15_6 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_hor_coe15_7 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe15_76;
        union { // name: yrgb_hor_coe16_10, offset: 0x100
            struct {
                unsigned int yrgb_hor_coe16_0 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_hor_coe16_1 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe16_10;
        union { // name: yrgb_hor_coe16_32, offset: 0x104
            struct {
                unsigned int yrgb_hor_coe16_2 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_hor_coe16_3 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe16_32;
        union { // name: yrgb_hor_coe16_54, offset: 0x108
            struct {
                unsigned int yrgb_hor_coe16_4 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_hor_coe16_5 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe16_54;
        union { // name: yrgb_hor_coe16_76, offset: 0x10c
            struct {
                unsigned int yrgb_hor_coe16_6 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_hor_coe16_7 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_hor_coe16_76;
        struct {
            unsigned int reserve_data[60];
        } reserve_reg_272_512;
        union { // name: yrgb_ver_coe0_10, offset: 0x200
            struct {
                unsigned int yrgb_ver_coe0_0 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_ver_coe0_1 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe0_10;
        union { // name: yrgb_ver_coe0_32, offset: 0x204
            struct {
                unsigned int yrgb_ver_coe0_2 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_ver_coe0_3 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe0_32;
        union { // name: yrgb_ver_coe0_54, offset: 0x208
            struct {
                unsigned int yrgb_ver_coe0_4 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_ver_coe0_5 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe0_54;
        union { // name: yrgb_ver_coe0_76, offset: 0x20c
            struct {
                unsigned int yrgb_ver_coe0_6 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_ver_coe0_7 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe0_76;
        union { // name: yrgb_ver_coe1_10, offset: 0x210
            struct {
                unsigned int yrgb_ver_coe1_0 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_ver_coe1_1 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe1_10;
        union { // name: yrgb_ver_coe1_32, offset: 0x214
            struct {
                unsigned int yrgb_ver_coe1_2 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_ver_coe1_3 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe1_32;
        union { // name: yrgb_ver_coe1_54, offset: 0x218
            struct {
                unsigned int yrgb_ver_coe1_4 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_ver_coe1_5 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe1_54;
        union { // name: yrgb_ver_coe1_76, offset: 0x21c
            struct {
                unsigned int yrgb_ver_coe1_6 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_ver_coe1_7 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe1_76;
        union { // name: yrgb_ver_coe2_10, offset: 0x220
            struct {
                unsigned int yrgb_ver_coe2_0 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_ver_coe2_1 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe2_10;
        union { // name: yrgb_ver_coe2_32, offset: 0x224
            struct {
                unsigned int yrgb_ver_coe2_2 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_ver_coe2_3 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe2_32;
        union { // name: yrgb_ver_coe2_54, offset: 0x228
            struct {
                unsigned int yrgb_ver_coe2_4 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_ver_coe2_5 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe2_54;
        union { // name: yrgb_ver_coe2_76, offset: 0x22c
            struct {
                unsigned int yrgb_ver_coe2_6 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_ver_coe2_7 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe2_76;
        union { // name: yrgb_ver_coe3_10, offset: 0x230
            struct {
                unsigned int yrgb_ver_coe3_0 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_ver_coe3_1 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe3_10;
        union { // name: yrgb_ver_coe3_32, offset: 0x234
            struct {
                unsigned int yrgb_ver_coe3_2 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_ver_coe3_3 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe3_32;
        union { // name: yrgb_ver_coe3_54, offset: 0x238
            struct {
                unsigned int yrgb_ver_coe3_4 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_ver_coe3_5 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe3_54;
        union { // name: yrgb_ver_coe3_76, offset: 0x23c
            struct {
                unsigned int yrgb_ver_coe3_6 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_ver_coe3_7 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe3_76;
        union { // name: yrgb_ver_coe4_10, offset: 0x240
            struct {
                unsigned int yrgb_ver_coe4_0 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_ver_coe4_1 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe4_10;
        union { // name: yrgb_ver_coe4_32, offset: 0x244
            struct {
                unsigned int yrgb_ver_coe4_2 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_ver_coe4_3 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe4_32;
        union { // name: yrgb_ver_coe4_54, offset: 0x248
            struct {
                unsigned int yrgb_ver_coe4_4 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_ver_coe4_5 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe4_54;
        union { // name: yrgb_ver_coe4_76, offset: 0x24c
            struct {
                unsigned int yrgb_ver_coe4_6 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_ver_coe4_7 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe4_76;
        union { // name: yrgb_ver_coe5_10, offset: 0x250
            struct {
                unsigned int yrgb_ver_coe5_0 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_ver_coe5_1 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe5_10;
        union { // name: yrgb_ver_coe5_32, offset: 0x254
            struct {
                unsigned int yrgb_ver_coe5_2 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_ver_coe5_3 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe5_32;
        union { // name: yrgb_ver_coe5_54, offset: 0x258
            struct {
                unsigned int yrgb_ver_coe5_4 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_ver_coe5_5 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe5_54;
        union { // name: yrgb_ver_coe5_76, offset: 0x25c
            struct {
                unsigned int yrgb_ver_coe5_6 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_ver_coe5_7 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe5_76;
        union { // name: yrgb_ver_coe6_10, offset: 0x260
            struct {
                unsigned int yrgb_ver_coe6_0 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_ver_coe6_1 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe6_10;
        union { // name: yrgb_ver_coe6_32, offset: 0x264
            struct {
                unsigned int yrgb_ver_coe6_2 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_ver_coe6_3 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe6_32;
        union { // name: yrgb_ver_coe6_54, offset: 0x268
            struct {
                unsigned int yrgb_ver_coe6_4 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_ver_coe6_5 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe6_54;
        union { // name: yrgb_ver_coe6_76, offset: 0x26c
            struct {
                unsigned int yrgb_ver_coe6_6 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_ver_coe6_7 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe6_76;
        union { // name: yrgb_ver_coe7_10, offset: 0x270
            struct {
                unsigned int yrgb_ver_coe7_0 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_ver_coe7_1 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe7_10;
        union { // name: yrgb_ver_coe7_32, offset: 0x274
            struct {
                unsigned int yrgb_ver_coe7_2 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_ver_coe7_3 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe7_32;
        union { // name: yrgb_ver_coe7_54, offset: 0x278
            struct {
                unsigned int yrgb_ver_coe7_4 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_ver_coe7_5 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe7_54;
        union { // name: yrgb_ver_coe7_76, offset: 0x27c
            struct {
                unsigned int yrgb_ver_coe7_6 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_ver_coe7_7 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe7_76;
        union { // name: yrgb_ver_coe8_10, offset: 0x280
            struct {
                unsigned int yrgb_ver_coe8_0 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_ver_coe8_1 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe8_10;
        union { // name: yrgb_ver_coe8_32, offset: 0x284
            struct {
                unsigned int yrgb_ver_coe8_2 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_ver_coe8_3 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe8_32;
        union { // name: yrgb_ver_coe8_54, offset: 0x288
            struct {
                unsigned int yrgb_ver_coe8_4 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_ver_coe8_5 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe8_54;
        union { // name: yrgb_ver_coe8_76, offset: 0x28c
            struct {
                unsigned int yrgb_ver_coe8_6 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_ver_coe8_7 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe8_76;
        union { // name: yrgb_ver_coe9_10, offset: 0x290
            struct {
                unsigned int yrgb_ver_coe9_0 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_ver_coe9_1 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe9_10;
        union { // name: yrgb_ver_coe9_32, offset: 0x294
            struct {
                unsigned int yrgb_ver_coe9_2 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_ver_coe9_3 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe9_32;
        union { // name: yrgb_ver_coe9_54, offset: 0x298
            struct {
                unsigned int yrgb_ver_coe9_4 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_ver_coe9_5 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe9_54;
        union { // name: yrgb_ver_coe9_76, offset: 0x29c
            struct {
                unsigned int yrgb_ver_coe9_6 : 10;
                unsigned int reserve_0       : 6;
                unsigned int yrgb_ver_coe9_7 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe9_76;
        union { // name: yrgb_ver_coe10_10, offset: 0x2a0
            struct {
                unsigned int yrgb_ver_coe10_0 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_ver_coe10_1 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe10_10;
        union { // name: yrgb_ver_coe10_32, offset: 0x2a4
            struct {
                unsigned int yrgb_ver_coe10_2 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_ver_coe10_3 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe10_32;
        union { // name: yrgb_ver_coe10_54, offset: 0x2a8
            struct {
                unsigned int yrgb_ver_coe10_4 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_ver_coe10_5 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe10_54;
        union { // name: yrgb_ver_coe10_76, offset: 0x2ac
            struct {
                unsigned int yrgb_ver_coe10_6 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_ver_coe10_7 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe10_76;
        union { // name: yrgb_ver_coe11_10, offset: 0x2b0
            struct {
                unsigned int yrgb_ver_coe11_0 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_ver_coe11_1 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe11_10;
        union { // name: yrgb_ver_coe11_32, offset: 0x2b4
            struct {
                unsigned int yrgb_ver_coe11_2 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_ver_coe11_3 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe11_32;
        union { // name: yrgb_ver_coe11_54, offset: 0x2b8
            struct {
                unsigned int yrgb_ver_coe11_4 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_ver_coe11_5 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe11_54;
        union { // name: yrgb_ver_coe11_76, offset: 0x2bc
            struct {
                unsigned int yrgb_ver_coe11_6 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_ver_coe11_7 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe11_76;
        union { // name: yrgb_ver_coe12_10, offset: 0x2c0
            struct {
                unsigned int yrgb_ver_coe12_0 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_ver_coe12_1 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe12_10;
        union { // name: yrgb_ver_coe12_32, offset: 0x2c4
            struct {
                unsigned int yrgb_ver_coe12_2 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_ver_coe12_3 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe12_32;
        union { // name: yrgb_ver_coe12_54, offset: 0x2c8
            struct {
                unsigned int yrgb_ver_coe12_4 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_ver_coe12_5 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe12_54;
        union { // name: yrgb_ver_coe12_76, offset: 0x2cc
            struct {
                unsigned int yrgb_ver_coe12_6 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_ver_coe12_7 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe12_76;
        union { // name: yrgb_ver_coe13_10, offset: 0x2d0
            struct {
                unsigned int yrgb_ver_coe13_0 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_ver_coe13_1 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe13_10;
        union { // name: yrgb_ver_coe13_32, offset: 0x2d4
            struct {
                unsigned int yrgb_ver_coe13_2 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_ver_coe13_3 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe13_32;
        union { // name: yrgb_ver_coe13_54, offset: 0x2d8
            struct {
                unsigned int yrgb_ver_coe13_4 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_ver_coe13_5 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe13_54;
        union { // name: yrgb_ver_coe13_76, offset: 0x2dc
            struct {
                unsigned int yrgb_ver_coe13_6 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_ver_coe13_7 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe13_76;
        union { // name: yrgb_ver_coe14_10, offset: 0x2e0
            struct {
                unsigned int yrgb_ver_coe14_0 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_ver_coe14_1 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe14_10;
        union { // name: yrgb_ver_coe14_32, offset: 0x2e4
            struct {
                unsigned int yrgb_ver_coe14_2 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_ver_coe14_3 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe14_32;
        union { // name: yrgb_ver_coe14_54, offset: 0x2e8
            struct {
                unsigned int yrgb_ver_coe14_4 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_ver_coe14_5 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe14_54;
        union { // name: yrgb_ver_coe14_76, offset: 0x2ec
            struct {
                unsigned int yrgb_ver_coe14_6 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_ver_coe14_7 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe14_76;
        union { // name: yrgb_ver_coe15_10, offset: 0x2f0
            struct {
                unsigned int yrgb_ver_coe15_0 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_ver_coe15_1 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe15_10;
        union { // name: yrgb_ver_coe15_32, offset: 0x2f4
            struct {
                unsigned int yrgb_ver_coe15_2 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_ver_coe15_3 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe15_32;
        union { // name: yrgb_ver_coe15_54, offset: 0x2f8
            struct {
                unsigned int yrgb_ver_coe15_4 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_ver_coe15_5 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe15_54;
        union { // name: yrgb_ver_coe15_76, offset: 0x2fc
            struct {
                unsigned int yrgb_ver_coe15_6 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_ver_coe15_7 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe15_76;
        union { // name: yrgb_ver_coe16_10, offset: 0x300
            struct {
                unsigned int yrgb_ver_coe16_0 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_ver_coe16_1 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe16_10;
        union { // name: yrgb_ver_coe16_32, offset: 0x304
            struct {
                unsigned int yrgb_ver_coe16_2 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_ver_coe16_3 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe16_32;
        union { // name: yrgb_ver_coe16_54, offset: 0x308
            struct {
                unsigned int yrgb_ver_coe16_4 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_ver_coe16_5 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe16_54;
        union { // name: yrgb_ver_coe16_76, offset: 0x30c
            struct {
                unsigned int yrgb_ver_coe16_6 : 10;
                unsigned int reserve_0        : 6;
                unsigned int yrgb_ver_coe16_7 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } yrgb_ver_coe16_76;
        struct {
            unsigned int reserve_data[60];
        } reserve_reg_784_1024;
        union { // name: cbcr_hor_coe0_10, offset: 0x400
            struct {
                unsigned int cbcr_hor_coe0_0 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_hor_coe0_1 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe0_10;
        union { // name: cbcr_hor_coe0_32, offset: 0x404
            struct {
                unsigned int cbcr_hor_coe0_2 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_hor_coe0_3 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe0_32;
        union { // name: cbcr_hor_coe0_54, offset: 0x408
            struct {
                unsigned int cbcr_hor_coe0_4 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_hor_coe0_5 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe0_54;
        union { // name: cbcr_hor_coe0_76, offset: 0x40c
            struct {
                unsigned int cbcr_hor_coe0_6 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_hor_coe0_7 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe0_76;
        union { // name: cbcr_hor_coe1_10, offset: 0x410
            struct {
                unsigned int cbcr_hor_coe1_0 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_hor_coe1_1 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe1_10;
        union { // name: cbcr_hor_coe1_32, offset: 0x414
            struct {
                unsigned int cbcr_hor_coe1_2 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_hor_coe1_3 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe1_32;
        union { // name: cbcr_hor_coe1_54, offset: 0x418
            struct {
                unsigned int cbcr_hor_coe1_4 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_hor_coe1_5 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe1_54;
        union { // name: cbcr_hor_coe1_76, offset: 0x41c
            struct {
                unsigned int cbcr_hor_coe1_6 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_hor_coe1_7 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe1_76;
        union { // name: cbcr_hor_coe2_10, offset: 0x420
            struct {
                unsigned int cbcr_hor_coe2_0 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_hor_coe2_1 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe2_10;
        union { // name: cbcr_hor_coe2_32, offset: 0x424
            struct {
                unsigned int cbcr_hor_coe2_2 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_hor_coe2_3 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe2_32;
        union { // name: cbcr_hor_coe2_54, offset: 0x428
            struct {
                unsigned int cbcr_hor_coe2_4 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_hor_coe2_5 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe2_54;
        union { // name: cbcr_hor_coe2_76, offset: 0x42c
            struct {
                unsigned int cbcr_hor_coe2_6 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_hor_coe2_7 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe2_76;
        union { // name: cbcr_hor_coe3_10, offset: 0x430
            struct {
                unsigned int cbcr_hor_coe3_0 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_hor_coe3_1 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe3_10;
        union { // name: cbcr_hor_coe3_32, offset: 0x434
            struct {
                unsigned int cbcr_hor_coe3_2 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_hor_coe3_3 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe3_32;
        union { // name: cbcr_hor_coe3_54, offset: 0x438
            struct {
                unsigned int cbcr_hor_coe3_4 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_hor_coe3_5 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe3_54;
        union { // name: cbcr_hor_coe3_76, offset: 0x43c
            struct {
                unsigned int cbcr_hor_coe3_6 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_hor_coe3_7 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe3_76;
        union { // name: cbcr_hor_coe4_10, offset: 0x440
            struct {
                unsigned int cbcr_hor_coe4_0 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_hor_coe4_1 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe4_10;
        union { // name: cbcr_hor_coe4_32, offset: 0x444
            struct {
                unsigned int cbcr_hor_coe4_2 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_hor_coe4_3 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe4_32;
        union { // name: cbcr_hor_coe4_54, offset: 0x448
            struct {
                unsigned int cbcr_hor_coe4_4 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_hor_coe4_5 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe4_54;
        union { // name: cbcr_hor_coe4_76, offset: 0x44c
            struct {
                unsigned int cbcr_hor_coe4_6 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_hor_coe4_7 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe4_76;
        union { // name: cbcr_hor_coe5_10, offset: 0x450
            struct {
                unsigned int cbcr_hor_coe5_0 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_hor_coe5_1 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe5_10;
        union { // name: cbcr_hor_coe5_32, offset: 0x454
            struct {
                unsigned int cbcr_hor_coe5_2 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_hor_coe5_3 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe5_32;
        union { // name: cbcr_hor_coe5_54, offset: 0x458
            struct {
                unsigned int cbcr_hor_coe5_4 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_hor_coe5_5 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe5_54;
        union { // name: cbcr_hor_coe5_76, offset: 0x45c
            struct {
                unsigned int cbcr_hor_coe5_6 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_hor_coe5_7 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe5_76;
        union { // name: cbcr_hor_coe6_10, offset: 0x460
            struct {
                unsigned int cbcr_hor_coe6_0 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_hor_coe6_1 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe6_10;
        union { // name: cbcr_hor_coe6_32, offset: 0x464
            struct {
                unsigned int cbcr_hor_coe6_2 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_hor_coe6_3 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe6_32;
        union { // name: cbcr_hor_coe6_54, offset: 0x468
            struct {
                unsigned int cbcr_hor_coe6_4 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_hor_coe6_5 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe6_54;
        union { // name: cbcr_hor_coe6_76, offset: 0x46c
            struct {
                unsigned int cbcr_hor_coe6_6 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_hor_coe6_7 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe6_76;
        union { // name: cbcr_hor_coe7_10, offset: 0x470
            struct {
                unsigned int cbcr_hor_coe7_0 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_hor_coe7_1 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe7_10;
        union { // name: cbcr_hor_coe7_32, offset: 0x474
            struct {
                unsigned int cbcr_hor_coe7_2 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_hor_coe7_3 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe7_32;
        union { // name: cbcr_hor_coe7_54, offset: 0x478
            struct {
                unsigned int cbcr_hor_coe7_4 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_hor_coe7_5 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe7_54;
        union { // name: cbcr_hor_coe7_76, offset: 0x47c
            struct {
                unsigned int cbcr_hor_coe7_6 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_hor_coe7_7 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe7_76;
        union { // name: cbcr_hor_coe8_10, offset: 0x480
            struct {
                unsigned int cbcr_hor_coe8_0 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_hor_coe8_1 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe8_10;
        union { // name: cbcr_hor_coe8_32, offset: 0x484
            struct {
                unsigned int cbcr_hor_coe8_2 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_hor_coe8_3 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe8_32;
        union { // name: cbcr_hor_coe8_54, offset: 0x488
            struct {
                unsigned int cbcr_hor_coe8_4 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_hor_coe8_5 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe8_54;
        union { // name: cbcr_hor_coe8_76, offset: 0x48c
            struct {
                unsigned int cbcr_hor_coe8_6 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_hor_coe8_7 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe8_76;
        union { // name: cbcr_hor_coe9_10, offset: 0x490
            struct {
                unsigned int cbcr_hor_coe9_0 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_hor_coe9_1 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe9_10;
        union { // name: cbcr_hor_coe9_32, offset: 0x494
            struct {
                unsigned int cbcr_hor_coe9_2 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_hor_coe9_3 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe9_32;
        union { // name: cbcr_hor_coe9_54, offset: 0x498
            struct {
                unsigned int cbcr_hor_coe9_4 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_hor_coe9_5 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe9_54;
        union { // name: cbcr_hor_coe9_76, offset: 0x49c
            struct {
                unsigned int cbcr_hor_coe9_6 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_hor_coe9_7 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe9_76;
        union { // name: cbcr_hor_coe10_10, offset: 0x4a0
            struct {
                unsigned int cbcr_hor_coe10_0 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_hor_coe10_1 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe10_10;
        union { // name: cbcr_hor_coe10_32, offset: 0x4a4
            struct {
                unsigned int cbcr_hor_coe10_2 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_hor_coe10_3 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe10_32;
        union { // name: cbcr_hor_coe10_54, offset: 0x4a8
            struct {
                unsigned int cbcr_hor_coe10_4 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_hor_coe10_5 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe10_54;
        union { // name: cbcr_hor_coe10_76, offset: 0x4ac
            struct {
                unsigned int cbcr_hor_coe10_6 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_hor_coe10_7 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe10_76;
        union { // name: cbcr_hor_coe11_10, offset: 0x4b0
            struct {
                unsigned int cbcr_hor_coe11_0 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_hor_coe11_1 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe11_10;
        union { // name: cbcr_hor_coe11_32, offset: 0x4b4
            struct {
                unsigned int cbcr_hor_coe11_2 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_hor_coe11_3 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe11_32;
        union { // name: cbcr_hor_coe11_54, offset: 0x4b8
            struct {
                unsigned int cbcr_hor_coe11_4 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_hor_coe11_5 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe11_54;
        union { // name: cbcr_hor_coe11_76, offset: 0x4bc
            struct {
                unsigned int cbcr_hor_coe11_6 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_hor_coe11_7 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe11_76;
        union { // name: cbcr_hor_coe12_10, offset: 0x4c0
            struct {
                unsigned int cbcr_hor_coe12_0 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_hor_coe12_1 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe12_10;
        union { // name: cbcr_hor_coe12_32, offset: 0x4c4
            struct {
                unsigned int cbcr_hor_coe12_2 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_hor_coe12_3 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe12_32;
        union { // name: cbcr_hor_coe12_54, offset: 0x4c8
            struct {
                unsigned int cbcr_hor_coe12_4 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_hor_coe12_5 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe12_54;
        union { // name: cbcr_hor_coe12_76, offset: 0x4cc
            struct {
                unsigned int cbcr_hor_coe12_6 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_hor_coe12_7 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe12_76;
        union { // name: cbcr_hor_coe13_10, offset: 0x4d0
            struct {
                unsigned int cbcr_hor_coe13_0 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_hor_coe13_1 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe13_10;
        union { // name: cbcr_hor_coe13_32, offset: 0x4d4
            struct {
                unsigned int cbcr_hor_coe13_2 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_hor_coe13_3 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe13_32;
        union { // name: cbcr_hor_coe13_54, offset: 0x4d8
            struct {
                unsigned int cbcr_hor_coe13_4 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_hor_coe13_5 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe13_54;
        union { // name: cbcr_hor_coe13_76, offset: 0x4dc
            struct {
                unsigned int cbcr_hor_coe13_6 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_hor_coe13_7 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe13_76;
        union { // name: cbcr_hor_coe14_10, offset: 0x4e0
            struct {
                unsigned int cbcr_hor_coe14_0 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_hor_coe14_1 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe14_10;
        union { // name: cbcr_hor_coe14_32, offset: 0x4e4
            struct {
                unsigned int cbcr_hor_coe14_2 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_hor_coe14_3 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe14_32;
        union { // name: cbcr_hor_coe14_54, offset: 0x4e8
            struct {
                unsigned int cbcr_hor_coe14_4 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_hor_coe14_5 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe14_54;
        union { // name: cbcr_hor_coe14_76, offset: 0x4ec
            struct {
                unsigned int cbcr_hor_coe14_6 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_hor_coe14_7 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe14_76;
        union { // name: cbcr_hor_coe15_10, offset: 0x4f0
            struct {
                unsigned int cbcr_hor_coe15_0 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_hor_coe15_1 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe15_10;
        union { // name: cbcr_hor_coe15_32, offset: 0x4f4
            struct {
                unsigned int cbcr_hor_coe15_2 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_hor_coe15_3 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe15_32;
        union { // name: cbcr_hor_coe15_54, offset: 0x4f8
            struct {
                unsigned int cbcr_hor_coe15_4 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_hor_coe15_5 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe15_54;
        union { // name: cbcr_hor_coe15_76, offset: 0x4fc
            struct {
                unsigned int cbcr_hor_coe15_6 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_hor_coe15_7 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe15_76;
        union { // name: cbcr_hor_coe16_10, offset: 0x500
            struct {
                unsigned int cbcr_hor_coe16_0 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_hor_coe16_1 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe16_10;
        union { // name: cbcr_hor_coe16_32, offset: 0x504
            struct {
                unsigned int cbcr_hor_coe16_2 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_hor_coe16_3 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe16_32;
        union { // name: cbcr_hor_coe16_54, offset: 0x508
            struct {
                unsigned int cbcr_hor_coe16_4 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_hor_coe16_5 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe16_54;
        union { // name: cbcr_hor_coe16_76, offset: 0x50c
            struct {
                unsigned int cbcr_hor_coe16_6 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_hor_coe16_7 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_hor_coe16_76;
        struct {
            unsigned int reserve_data[60];
        } reserve_reg_1296_1536;
        union { // name: cbcr_ver_coe0_10, offset: 0x600
            struct {
                unsigned int cbcr_ver_coe0_0 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_ver_coe0_1 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe0_10;
        union { // name: cbcr_ver_coe0_32, offset: 0x604
            struct {
                unsigned int cbcr_ver_coe0_2 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_ver_coe0_3 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe0_32;
        union { // name: cbcr_ver_coe0_54, offset: 0x608
            struct {
                unsigned int cbcr_ver_coe0_4 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_ver_coe0_5 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe0_54;
        union { // name: cbcr_ver_coe0_76, offset: 0x60c
            struct {
                unsigned int cbcr_ver_coe0_6 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_ver_coe0_7 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe0_76;
        union { // name: cbcr_ver_coe1_10, offset: 0x610
            struct {
                unsigned int cbcr_ver_coe1_0 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_ver_coe1_1 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe1_10;
        union { // name: cbcr_ver_coe1_32, offset: 0x614
            struct {
                unsigned int cbcr_ver_coe1_2 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_ver_coe1_3 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe1_32;
        union { // name: cbcr_ver_coe1_54, offset: 0x618
            struct {
                unsigned int cbcr_ver_coe1_4 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_ver_coe1_5 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe1_54;
        union { // name: cbcr_ver_coe1_76, offset: 0x61c
            struct {
                unsigned int cbcr_ver_coe1_6 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_ver_coe1_7 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe1_76;
        union { // name: cbcr_ver_coe2_10, offset: 0x620
            struct {
                unsigned int cbcr_ver_coe2_0 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_ver_coe2_1 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe2_10;
        union { // name: cbcr_ver_coe2_32, offset: 0x624
            struct {
                unsigned int cbcr_ver_coe2_2 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_ver_coe2_3 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe2_32;
        union { // name: cbcr_ver_coe2_54, offset: 0x628
            struct {
                unsigned int cbcr_ver_coe2_4 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_ver_coe2_5 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe2_54;
        union { // name: cbcr_ver_coe2_76, offset: 0x62c
            struct {
                unsigned int cbcr_ver_coe2_6 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_ver_coe2_7 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe2_76;
        union { // name: cbcr_ver_coe3_10, offset: 0x630
            struct {
                unsigned int cbcr_ver_coe3_0 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_ver_coe3_1 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe3_10;
        union { // name: cbcr_ver_coe3_32, offset: 0x634
            struct {
                unsigned int cbcr_ver_coe3_2 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_ver_coe3_3 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe3_32;
        union { // name: cbcr_ver_coe3_54, offset: 0x638
            struct {
                unsigned int cbcr_ver_coe3_4 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_ver_coe3_5 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe3_54;
        union { // name: cbcr_ver_coe3_76, offset: 0x63c
            struct {
                unsigned int cbcr_ver_coe3_6 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_ver_coe3_7 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe3_76;
        union { // name: cbcr_ver_coe4_10, offset: 0x640
            struct {
                unsigned int cbcr_ver_coe4_0 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_ver_coe4_1 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe4_10;
        union { // name: cbcr_ver_coe4_32, offset: 0x644
            struct {
                unsigned int cbcr_ver_coe4_2 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_ver_coe4_3 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe4_32;
        union { // name: cbcr_ver_coe4_54, offset: 0x648
            struct {
                unsigned int cbcr_ver_coe4_4 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_ver_coe4_5 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe4_54;
        union { // name: cbcr_ver_coe4_76, offset: 0x64c
            struct {
                unsigned int cbcr_ver_coe4_6 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_ver_coe4_7 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe4_76;
        union { // name: cbcr_ver_coe5_10, offset: 0x650
            struct {
                unsigned int cbcr_ver_coe5_0 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_ver_coe5_1 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe5_10;
        union { // name: cbcr_ver_coe5_32, offset: 0x654
            struct {
                unsigned int cbcr_ver_coe5_2 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_ver_coe5_3 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe5_32;
        union { // name: cbcr_ver_coe5_54, offset: 0x658
            struct {
                unsigned int cbcr_ver_coe5_4 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_ver_coe5_5 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe5_54;
        union { // name: cbcr_ver_coe5_76, offset: 0x65c
            struct {
                unsigned int cbcr_ver_coe5_6 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_ver_coe5_7 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe5_76;
        union { // name: cbcr_ver_coe6_10, offset: 0x660
            struct {
                unsigned int cbcr_ver_coe6_0 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_ver_coe6_1 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe6_10;
        union { // name: cbcr_ver_coe6_32, offset: 0x664
            struct {
                unsigned int cbcr_ver_coe6_2 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_ver_coe6_3 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe6_32;
        union { // name: cbcr_ver_coe6_54, offset: 0x668
            struct {
                unsigned int cbcr_ver_coe6_4 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_ver_coe6_5 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe6_54;
        union { // name: cbcr_ver_coe6_76, offset: 0x66c
            struct {
                unsigned int cbcr_ver_coe6_6 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_ver_coe6_7 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe6_76;
        union { // name: cbcr_ver_coe7_10, offset: 0x670
            struct {
                unsigned int cbcr_ver_coe7_0 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_ver_coe7_1 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe7_10;
        union { // name: cbcr_ver_coe7_32, offset: 0x674
            struct {
                unsigned int cbcr_ver_coe7_2 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_ver_coe7_3 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe7_32;
        union { // name: cbcr_ver_coe7_54, offset: 0x678
            struct {
                unsigned int cbcr_ver_coe7_4 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_ver_coe7_5 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe7_54;
        union { // name: cbcr_ver_coe7_76, offset: 0x67c
            struct {
                unsigned int cbcr_ver_coe7_6 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_ver_coe7_7 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe7_76;
        union { // name: cbcr_ver_coe8_10, offset: 0x680
            struct {
                unsigned int cbcr_ver_coe8_0 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_ver_coe8_1 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe8_10;
        union { // name: cbcr_ver_coe8_32, offset: 0x684
            struct {
                unsigned int cbcr_ver_coe8_2 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_ver_coe8_3 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe8_32;
        union { // name: cbcr_ver_coe8_54, offset: 0x688
            struct {
                unsigned int cbcr_ver_coe8_4 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_ver_coe8_5 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe8_54;
        union { // name: cbcr_ver_coe8_76, offset: 0x68c
            struct {
                unsigned int cbcr_ver_coe8_6 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_ver_coe8_7 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe8_76;
        union { // name: cbcr_ver_coe9_10, offset: 0x690
            struct {
                unsigned int cbcr_ver_coe9_0 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_ver_coe9_1 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe9_10;
        union { // name: cbcr_ver_coe9_32, offset: 0x694
            struct {
                unsigned int cbcr_ver_coe9_2 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_ver_coe9_3 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe9_32;
        union { // name: cbcr_ver_coe9_54, offset: 0x698
            struct {
                unsigned int cbcr_ver_coe9_4 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_ver_coe9_5 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe9_54;
        union { // name: cbcr_ver_coe9_76, offset: 0x69c
            struct {
                unsigned int cbcr_ver_coe9_6 : 10;
                unsigned int reserve_0       : 6;
                unsigned int cbcr_ver_coe9_7 : 10;
                unsigned int reserve_1       : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe9_76;
        union { // name: cbcr_ver_coe10_10, offset: 0x6a0
            struct {
                unsigned int cbcr_ver_coe10_0 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_ver_coe10_1 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe10_10;
        union { // name: cbcr_ver_coe10_32, offset: 0x6a4
            struct {
                unsigned int cbcr_ver_coe10_2 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_ver_coe10_3 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe10_32;
        union { // name: cbcr_ver_coe10_54, offset: 0x6a8
            struct {
                unsigned int cbcr_ver_coe10_4 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_ver_coe10_5 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe10_54;
        union { // name: cbcr_ver_coe10_76, offset: 0x6ac
            struct {
                unsigned int cbcr_ver_coe10_6 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_ver_coe10_7 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe10_76;
        union { // name: cbcr_ver_coe11_10, offset: 0x6b0
            struct {
                unsigned int cbcr_ver_coe11_0 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_ver_coe11_1 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe11_10;
        union { // name: cbcr_ver_coe11_32, offset: 0x6b4
            struct {
                unsigned int cbcr_ver_coe11_2 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_ver_coe11_3 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe11_32;
        union { // name: cbcr_ver_coe11_54, offset: 0x6b8
            struct {
                unsigned int cbcr_ver_coe11_4 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_ver_coe11_5 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe11_54;
        union { // name: cbcr_ver_coe11_76, offset: 0x6bc
            struct {
                unsigned int cbcr_ver_coe11_6 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_ver_coe11_7 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe11_76;
        union { // name: cbcr_ver_coe12_10, offset: 0x6c0
            struct {
                unsigned int cbcr_ver_coe12_0 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_ver_coe12_1 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe12_10;
        union { // name: cbcr_ver_coe12_32, offset: 0x6c4
            struct {
                unsigned int cbcr_ver_coe12_2 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_ver_coe12_3 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe12_32;
        union { // name: cbcr_ver_coe12_54, offset: 0x6c8
            struct {
                unsigned int cbcr_ver_coe12_4 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_ver_coe12_5 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe12_54;
        union { // name: cbcr_ver_coe12_76, offset: 0x6cc
            struct {
                unsigned int cbcr_ver_coe12_6 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_ver_coe12_7 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe12_76;
        union { // name: cbcr_ver_coe13_10, offset: 0x6d0
            struct {
                unsigned int cbcr_ver_coe13_0 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_ver_coe13_1 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe13_10;
        union { // name: cbcr_ver_coe13_32, offset: 0x6d4
            struct {
                unsigned int cbcr_ver_coe13_2 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_ver_coe13_3 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe13_32;
        union { // name: cbcr_ver_coe13_54, offset: 0x6d8
            struct {
                unsigned int cbcr_ver_coe13_4 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_ver_coe13_5 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe13_54;
        union { // name: cbcr_ver_coe13_76, offset: 0x6dc
            struct {
                unsigned int cbcr_ver_coe13_6 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_ver_coe13_7 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe13_76;
        union { // name: cbcr_ver_coe14_10, offset: 0x6e0
            struct {
                unsigned int cbcr_ver_coe14_0 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_ver_coe14_1 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe14_10;
        union { // name: cbcr_ver_coe14_32, offset: 0x6e4
            struct {
                unsigned int cbcr_ver_coe14_2 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_ver_coe14_3 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe14_32;
        union { // name: cbcr_ver_coe14_54, offset: 0x6e8
            struct {
                unsigned int cbcr_ver_coe14_4 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_ver_coe14_5 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe14_54;
        union { // name: cbcr_ver_coe14_76, offset: 0x6ec
            struct {
                unsigned int cbcr_ver_coe14_6 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_ver_coe14_7 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe14_76;
        union { // name: cbcr_ver_coe15_10, offset: 0x6f0
            struct {
                unsigned int cbcr_ver_coe15_0 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_ver_coe15_1 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe15_10;
        union { // name: cbcr_ver_coe15_32, offset: 0x6f4
            struct {
                unsigned int cbcr_ver_coe15_2 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_ver_coe15_3 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe15_32;
        union { // name: cbcr_ver_coe15_54, offset: 0x6f8
            struct {
                unsigned int cbcr_ver_coe15_4 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_ver_coe15_5 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe15_54;
        union { // name: cbcr_ver_coe15_76, offset: 0x6fc
            struct {
                unsigned int cbcr_ver_coe15_6 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_ver_coe15_7 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe15_76;
        union { // name: cbcr_ver_coe16_10, offset: 0x700
            struct {
                unsigned int cbcr_ver_coe16_0 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_ver_coe16_1 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe16_10;
        union { // name: cbcr_ver_coe16_32, offset: 0x704
            struct {
                unsigned int cbcr_ver_coe16_2 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_ver_coe16_3 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe16_32;
        union { // name: cbcr_ver_coe16_54, offset: 0x708
            struct {
                unsigned int cbcr_ver_coe16_4 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_ver_coe16_5 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe16_54;
        union { // name: cbcr_ver_coe16_76, offset: 0x70c
            struct {
                unsigned int cbcr_ver_coe16_6 : 10;
                unsigned int reserve_0        : 6;
                unsigned int cbcr_ver_coe16_7 : 10;
                unsigned int reserve_1        : 6;
            } bits;
            unsigned int val;
        } cbcr_ver_coe16_76;
        struct {
            unsigned int reserve_data[60];
        } reserve_reg_1808_2048;
        union { // name: zme_ctrl, offset: 0x800
            struct {
                unsigned int bypass_en      : 1;
                unsigned int align_en       : 1;
                unsigned int reserve_0      : 2;
                unsigned int format_in      : 4;
                unsigned int format_out     : 4;
                unsigned int reserve_1      : 19;
                unsigned int auto_gating_en : 1;
            } bits;
            unsigned int val;
        } zme_ctrl;
        struct {
            unsigned int reserve_data[3];
        } reserve_reg_2052_2064;
        union { // name: yrgb_scl_ctrl, offset: 0x810
            struct {
                unsigned int yrgb_xsd_en     : 1;
                unsigned int yrgb_xsu_en     : 1;
                unsigned int yrgb_xscl_mode  : 2;
                unsigned int yrgb_ysd_en     : 1;
                unsigned int yrgb_ysu_en     : 1;
                unsigned int yrgb_yscl_mode  : 2;
                unsigned int yrgb_dering_en  : 1;
                unsigned int yrgb_gt_en      : 1;
                unsigned int yrgb_gt_mode    : 2;
                unsigned int reserve_0       : 4;
                unsigned int yrgb_xsd_bypass : 1;
                unsigned int yrgb_ys_bypass  : 1;
                unsigned int yrgb_xsu_bypass : 1;
                unsigned int reserve_1       : 13;
            } bits;
            unsigned int val;
        } yrgb_scl_ctrl;
        struct {
            unsigned int reserve_data[2];
        } reserve_reg_2068_2076;
        union { // name: yrgb_dering_para, offset: 0x81c
            struct {
                unsigned int yrgb_dering_sen0  : 5;
                unsigned int reserve_0         : 3;
                unsigned int yrgb_dering_sen1  : 5;
                unsigned int reserve_1         : 3;
                unsigned int yrgb_dering_alpha : 5;
                unsigned int reserve_2         : 3;
                unsigned int yrgb_dering_delta : 5;
                unsigned int reserve_3         : 3;
            } bits;
            unsigned int val;
        } yrgb_dering_para;
        union { // name: yrgb_xscl_factor, offset: 0x820
            struct {
                unsigned int yrgb_xscl_factor : 16;
                unsigned int yrgb_xscl_offset : 16;
            } bits;
            unsigned int val;
        } yrgb_xscl_factor;
        union { // name: yrgb_yscl_factor, offset: 0x824
            struct {
                unsigned int yrgb_yscl_factor : 16;
                unsigned int yrgb_yscl_offset : 16;
            } bits;
            unsigned int val;
        } yrgb_yscl_factor;
        struct {
            unsigned int reserve_data[2];
        } reserve_reg_2088_2096;
        union { // name: cbcr_scl_ctrl, offset: 0x830
            struct {
                unsigned int cbcr_xsd_en     : 1;
                unsigned int cbcr_xsu_en     : 1;
                unsigned int cbcr_xscl_mode  : 2;
                unsigned int cbcr_ysd_en     : 1;
                unsigned int cbcr_ysu_en     : 1;
                unsigned int cbcr_yscl_mode  : 2;
                unsigned int cbcr_dering_en  : 1;
                unsigned int cbcr_gt_en      : 1;
                unsigned int cbcr_gt_mode    : 2;
                unsigned int reserve_0       : 4;
                unsigned int cbcr_xsd_bypass : 1;
                unsigned int cbcr_ys_bypass  : 1;
                unsigned int cbcr_xsu_bypass : 1;
                unsigned int reserve_1       : 13;
            } bits;
            unsigned int val;
        } cbcr_scl_ctrl;
        struct {
            unsigned int reserve_data[2];
        } reserve_reg_2100_2108;
        union { // name: cbcr_dering_para, offset: 0x83c
            struct {
                unsigned int cbcr_dering_sen0  : 5;
                unsigned int reserve_0         : 3;
                unsigned int cbcr_dering_sen1  : 5;
                unsigned int reserve_1         : 3;
                unsigned int cbcr_dering_alpha : 5;
                unsigned int reserve_2         : 3;
                unsigned int cbcr_dering_delta : 5;
                unsigned int reserve_3         : 3;
            } bits;
            unsigned int val;
        } cbcr_dering_para;
        union { // name: cbcr_xscl_factor, offset: 0x840
            struct {
                unsigned int cbcr_xscl_factor : 16;
                unsigned int cbcr_xscl_offset : 16;
            } bits;
            unsigned int val;
        } cbcr_xscl_factor;
        union { // name: cbcr_yscl_factor, offset: 0x844
            struct {
                unsigned int cbcr_yscl_factor : 16;
                unsigned int cbcr_yscl_offset : 16;
            } bits;
            unsigned int val;
        } cbcr_yscl_factor;
    } regs;
    unsigned int data[530];
} zme_rk3528_u;

#endif /* VDPP_RK3528_H */
