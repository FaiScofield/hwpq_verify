#ifndef VDPP_RK3572_H
#define VDPP_RK3572_H

// 0x00000000
typedef union iep2_rk3572 {
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
        union { // name: qos_config, offset: 0xc
            struct {
                unsigned int sw_vdpp_arqos_en : 1;
                unsigned int sw_vdpp_awqos_en : 1;
                unsigned int reserve_0        : 2;
                unsigned int sw_ar_mmu_qos3   : 4;
                unsigned int reserve_1        : 24;
            } bits;
            unsigned int val;
        } qos_config;
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
        union { // name: arqos_config, offset: 0x18
            struct {
                unsigned int sw_ar_y_qos1  : 4;
                unsigned int sw_ar_y_qos2  : 4;
                unsigned int sw_ar_uv_qos1 : 4;
                unsigned int sw_ar_uv_qos2 : 4;
                unsigned int sw_ar_md_qos  : 4;
                unsigned int sw_ar_mv_qos  : 4;
                unsigned int reserve_0     : 8;
            } bits;
            unsigned int val;
        } arqos_config;
        union { // name: awqos_config, offset: 0x1c
            struct {
                unsigned int sw_aw_id7_qos  : 4;
                unsigned int sw_aw_id8_qos  : 4;
                unsigned int sw_aw_id9_qos  : 4;
                unsigned int sw_aw_id10_qos : 4;
                unsigned int reserve_0      : 16;
            } bits;
            unsigned int val;
        } awqos_config;
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
} iep2_rk3572_u;

// 0x00001000
typedef union vep_rk3572 {
    struct {
        union { // name: frm_start, offset: 0x0
            struct {
                unsigned int sw_vep_frm_en : 1;
                unsigned int reserve_0     : 31;
            } bits;
            unsigned int val;
        } frm_start;
        union { // name: config0, offset: 0x4
            struct {
                unsigned int sw_vep_src_fmt         : 2;
                unsigned int reserve_0              : 2;
                unsigned int sw_vep_src_yuv_swap    : 2;
                unsigned int reserve_1              : 2;
                unsigned int sw_vep_dst_fmt         : 2;
                unsigned int sw_vep_yuvout_diff_en  : 1;
                unsigned int reserve_2              : 1;
                unsigned int sw_vep_dst_yuv_swap    : 2;
                unsigned int reserve_3              : 2;
                unsigned int sw_vep_debug_data_en   : 1;
                unsigned int reserve_4              : 3;
                unsigned int sw_vep_rst_protect_dis : 1;
                unsigned int sys_vep_sreset_p       : 1;
                unsigned int sw_vep_init_dis        : 1;
                unsigned int reserve_5              : 1;
                unsigned int sw_vep_dmsr_en         : 1;
                unsigned int sw_dci_en              : 1;
                unsigned int reserve_6              : 6;
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
        union { // name: qos_config, offset: 0xc
            struct {
                unsigned int sw_vep_arqos_en : 1;
                unsigned int sw_vep_awqos_en : 1;
                unsigned int reserve_0       : 2;
                unsigned int sw_ar_mmu_qos3  : 4;
                unsigned int reserve_1       : 24;
            } bits;
            unsigned int val;
        } qos_config;
        union { // name: gating_ctrl, offset: 0x10
            struct {
                unsigned int sw_vep_clk_on  : 1;
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
        union { // name: arqos_config, offset: 0x18
            struct {
                unsigned int sw_ar_y_qos1  : 4;
                unsigned int sw_ar_y_qos2  : 4;
                unsigned int sw_ar_uv_qos1 : 4;
                unsigned int sw_ar_uv_qos2 : 4;
                unsigned int reserve_0     : 16;
            } bits;
            unsigned int val;
        } arqos_config;
        union { // name: awqos_config, offset: 0x1c
            struct {
                unsigned int sw_aw_id7_qos  : 4;
                unsigned int sw_aw_id8_qos  : 4;
                unsigned int sw_aw_id9_qos  : 4;
                unsigned int sw_aw_id10_qos : 4;
                unsigned int reserve_0      : 16;
            } bits;
            unsigned int val;
        } awqos_config;
        union { // name: int_en, offset: 0x20
            struct {
                unsigned int sw_vep_frm_done_en     : 1;
                unsigned int sw_vep_osd_max_en      : 1;
                unsigned int reserve_0              : 2;
                unsigned int sw_vep_bus_error_en    : 1;
                unsigned int sw_vep_timeout_int_en  : 1;
                unsigned int sw_vep_config_error_en : 1;
                unsigned int reserve_1              : 25;
            } bits;
            unsigned int val;
        } int_en;
        union { // name: int_clr, offset: 0x24
            struct {
                unsigned int sw_vep_frm_done_clr     : 1;
                unsigned int sw_vep_osd_max_clr      : 1;
                unsigned int reserve_0               : 2;
                unsigned int sw_vep_bus_error_clr    : 1;
                unsigned int sw_vep_timeout_int_clr  : 1;
                unsigned int sw_vep_config_error_clr : 1;
                unsigned int reserve_1               : 25;
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
                unsigned int sw_vep_src_vir_y_stride : 16;
                unsigned int reserve_0               : 16;
            } bits;
            unsigned int val;
        } vir_src_img_width;
        union { // name: vir_dst_img_width, offset: 0x34
            struct {
                unsigned int sw_vep_dst_vir_y_stride : 16;
                unsigned int sw_vep_dst_vir_c_stride : 16;
            } bits;
            unsigned int val;
        } vir_dst_img_width;
        union { // name: src_img_size, offset: 0x38
            struct {
                unsigned int sw_vep_src_pic_width       : 11;
                unsigned int reserve_0                  : 1;
                unsigned int sw_vep_src_right_redundant : 4;
                unsigned int sw_vep_src_pic_height      : 11;
                unsigned int reserve_1                  : 1;
                unsigned int sw_vep_src_down_redundant  : 3;
                unsigned int reserve_2                  : 1;
            } bits;
            unsigned int val;
        } src_img_size;
        union { // name: dst_img_size, offset: 0x3c
            struct {
                unsigned int sw_vep_dst_pic_width       : 11;
                unsigned int reserve_0                  : 1;
                unsigned int sw_vep_dst_right_redundant : 4;
                unsigned int sw_vep_dst_pic_height      : 11;
                unsigned int reserve_1                  : 5;
            } bits;
            unsigned int val;
        } dst_img_size;
        union { // name: dst_img_size_c, offset: 0x40
            struct {
                unsigned int sw_vep_dst_pic_width_c       : 11;
                unsigned int reserve_0                    : 1;
                unsigned int sw_vep_dst_right_redundant_c : 4;
                unsigned int sw_vep_dst_pic_height_c      : 11;
                unsigned int reserve_1                    : 5;
            } bits;
            unsigned int val;
        } dst_img_size_c;
        struct {
            unsigned int reserve_data[3];
        } reserve_reg_68_80;
        union { // name: timeout_cfg, offset: 0x50
            struct {
                unsigned int sw_vep_timeout_cnt : 31;
                unsigned int sw_vep_timeout_en  : 1;
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
                unsigned int sw_vep_src_addr_y : 32;
            } bits;
            unsigned int val;
        } src_addr_y;
        union { // name: src_addr_uv, offset: 0x64
            struct {
                unsigned int sw_vep_src_addr_uv : 32;
            } bits;
            unsigned int val;
        } src_addr_uv;
        union { // name: dst_addr_y, offset: 0x68
            struct {
                unsigned int sw_vep_dst_addr_y : 32;
            } bits;
            unsigned int val;
        } dst_addr_y;
        union { // name: dst_addr_uv, offset: 0x6c
            struct {
                unsigned int sw_vep_dst_addr_uv : 32;
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
        struct {
            unsigned int reserve_data[3];
        } reserve_reg_212_224;
        union { // name: dci_yrgb_addr, offset: 0xe0
            struct {
                unsigned int sw_dci_yrgb_addr : 32;
            } bits;
            unsigned int val;
        } dci_yrgb_addr;
        union { // name: dci_yrgb_vir_stride, offset: 0xe4
            struct {
                unsigned int sw_dci_yrgb_vir_stride : 16;
                unsigned int sw_dci_yrgb_gather_num : 4;
                unsigned int sw_dci_yrgb_gather_en  : 1;
                unsigned int reserve_0              : 11;
            } bits;
            unsigned int val;
        } dci_yrgb_vir_stride;
        union { // name: dci_img_size, offset: 0xe8
            struct {
                unsigned int sw_vep_src_pic_width  : 12;
                unsigned int reserve_0             : 4;
                unsigned int sw_vep_src_pic_height : 12;
                unsigned int reserve_1             : 4;
            } bits;
            unsigned int val;
        } dci_img_size;
        union { // name: dci_ctrl, offset: 0xec
            struct {
                unsigned int sw_dci_data_format : 3;
                unsigned int sw_dci_csc_range   : 1;
                unsigned int sw_dci_vsd_mode    : 2;
                unsigned int sw_dci_hsd_mode    : 1;
                unsigned int sw_dci_alpha_swap  : 1;
                unsigned int sw_dci_rb_swap     : 1;
                unsigned int reserve_0          : 7;
                unsigned int sw_dci_blk_hsize   : 8;
                unsigned int sw_dci_blk_vsize   : 8;
            } bits;
            unsigned int val;
        } dci_ctrl;
        union { // name: dci_hist_addr, offset: 0xf0
            struct {
                unsigned int sw_dci_hist_addr : 32;
            } bits;
            unsigned int val;
        } dci_hist_addr;
        struct {
            unsigned int reserve_data[39];
        } reserve_reg_244_400;
        union { // name: pyramid_ctrl, offset: 0x190
            struct {
                unsigned int sw_pyramid_en : 1;
                unsigned int reserve_0     : 31;
            } bits;
            unsigned int val;
        } pyramid_ctrl;
        union { // name: pyramid_layer1_dst_addr, offset: 0x194
            struct {
                unsigned int sw_pyramid_layer1_dst_addr : 32;
            } bits;
            unsigned int val;
        } pyramid_layer1_dst_addr;
        union { // name: pyramid_layer1_dst_cfg, offset: 0x198
            struct {
                unsigned int sw_pyramid_layer1_dst_vir_wid : 16;
                unsigned int reserve_0                     : 16;
            } bits;
            unsigned int val;
        } pyramid_layer1_dst_cfg;
        union { // name: pyramid_layer2_dst_addr, offset: 0x19c
            struct {
                unsigned int sw_pyramid_layer2_dst_addr : 32;
            } bits;
            unsigned int val;
        } pyramid_layer2_dst_addr;
        union { // name: pyramid_layer2_dst_cfg, offset: 0x1a0
            struct {
                unsigned int sw_pyramid_layer2_dst_vir_wid : 16;
                unsigned int reserve_0                     : 16;
            } bits;
            unsigned int val;
        } pyramid_layer2_dst_cfg;
        union { // name: pyramid_layer3_dst_addr, offset: 0x1a4
            struct {
                unsigned int sw_pyramid_layer3_dst_addr : 32;
            } bits;
            unsigned int val;
        } pyramid_layer3_dst_addr;
        union { // name: pyramid_layer3_dst_cfg, offset: 0x1a8
            struct {
                unsigned int sw_pyramid_layer3_dst_vir_wid : 16;
                unsigned int reserve_0                     : 16;
            } bits;
            unsigned int val;
        } pyramid_layer3_dst_cfg;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_428_432;
        union { // name: det_ctrl, offset: 0x1b0
            struct {
                unsigned int sw_det_en      : 1;
                unsigned int reserve_0      : 3;
                unsigned int sw_det_blckLmt : 8;
                unsigned int reserve_1      : 20;
            } bits;
            unsigned int val;
        } det_ctrl;
        union { // name: det_bar_size_out0, offset: 0x1b4
            struct {
                unsigned int blckbar_size_top    : 12;
                unsigned int reserve_0           : 4;
                unsigned int blckbar_size_bottom : 12;
                unsigned int reserve_1           : 4;
            } bits;
            unsigned int val;
        } det_bar_size_out0;
        union { // name: det_bar_size_out1, offset: 0x1b8
            struct {
                unsigned int blckbar_size_left  : 12;
                unsigned int reserve_0          : 4;
                unsigned int blckbar_size_right : 12;
                unsigned int reserve_1          : 4;
            } bits;
            unsigned int val;
        } det_bar_size_out1;
    } regs;
    unsigned int data[111];
} vep_rk3572_u;

// 0x00001100
typedef union es_rk3572 {
    struct {
        union { // name: en, offset: 0x0
            struct {
                unsigned int ES_ENABLE : 1;
                unsigned int reserve_0 : 31;
            } bits;
            unsigned int val;
        } en;
        union { // name: dir_th, offset: 0x4
            struct {
                unsigned int reserve_0 : 8;
                unsigned int DIR_TH    : 8;
                unsigned int FLAT_TH   : 8;
                unsigned int reserve_1 : 8;
            } bits;
            unsigned int val;
        } dir_th;
        union { // name: dir_tan, offset: 0x8
            struct {
                unsigned int reserve_0 : 16;
                unsigned int TAN_LO_TH : 9;
                unsigned int TAN_HI_TH : 9;
            } bits;
            unsigned int val;
        } dir_tan;
        union { // name: dir_chk, offset: 0xc
            struct {
                unsigned int reserve_0  : 8;
                unsigned int MEM_GAT_EN : 1;
                unsigned int EP_CHK_EN  : 1;
                unsigned int reserve_1  : 22;
            } bits;
            unsigned int val;
        } dir_chk;
        union { // name: fil_diff0, offset: 0x10
            struct {
                unsigned int reserve_0  : 16;
                unsigned int DIFF_LIMIT : 16;
                unsigned int DIFF_GAIN0 : 16;
            } bits;
            unsigned int val;
        } fil_diff0;
        union { // name: fil_diff1, offset: 0x14
            struct {
                unsigned int reserve_0  : 16;
                unsigned int DIFF_GAIN1 : 16;
                unsigned int LUT_X0     : 16;
            } bits;
            unsigned int val;
        } fil_diff1;
        union { // name: fil_lut_x0, offset: 0x18
            struct {
                unsigned int reserve_0 : 16;
                unsigned int LUT_X1    : 16;
                unsigned int LUT_X2    : 16;
            } bits;
            unsigned int val;
        } fil_lut_x0;
        union { // name: fil_lut_x1, offset: 0x1c
            struct {
                unsigned int reserve_0 : 16;
                unsigned int LUT_X3    : 16;
                unsigned int LUT_X4    : 16;
            } bits;
            unsigned int val;
        } fil_lut_x1;
        union { // name: fil_lut_x2, offset: 0x20
            struct {
                unsigned int reserve_0 : 16;
                unsigned int LUT_X5    : 16;
                unsigned int LUT_X6    : 16;
            } bits;
            unsigned int val;
        } fil_lut_x2;
        union { // name: fil_lut_x3, offset: 0x24
            struct {
                unsigned int reserve_0 : 16;
                unsigned int LUT_X7    : 16;
                unsigned int LUT_X8    : 16;
            } bits;
            unsigned int val;
        } fil_lut_x3;
        union { // name: fil_lut_y0, offset: 0x28
            struct {
                unsigned int reserve_0 : 24;
                unsigned int LUT_Y3    : 8;
                unsigned int LUT_Y2    : 8;
                unsigned int LUT_Y1    : 8;
                unsigned int LUT_Y0    : 8;
            } bits;
            unsigned int val;
        } fil_lut_y0;
        union { // name: fil_lut_y1, offset: 0x2c
            struct {
                unsigned int reserve_0 : 24;
                unsigned int LUT_Y7    : 8;
                unsigned int LUT_Y6    : 8;
                unsigned int LUT_Y5    : 8;
                unsigned int LUT_Y4    : 8;
            } bits;
            unsigned int val;
        } fil_lut_y1;
        union { // name: fil_lut_y2, offset: 0x30
            struct {
                unsigned int LUT_Y8    : 8;
                unsigned int reserve_0 : 24;
            } bits;
            unsigned int val;
        } fil_lut_y2;
        union { // name: fil_lut_k0, offset: 0x34
            struct {
                unsigned int reserve_0 : 24;
                unsigned int LUT_K3    : 8;
                unsigned int LUT_K2    : 8;
                unsigned int LUT_K1    : 8;
                unsigned int LUT_K0    : 8;
            } bits;
            unsigned int val;
        } fil_lut_k0;
        union { // name: fil_lut_k1, offset: 0x38
            struct {
                unsigned int reserve_0 : 24;
                unsigned int LUT_K7    : 8;
                unsigned int LUT_K6    : 8;
                unsigned int LUT_K5    : 8;
                unsigned int LUT_K4    : 8;
            } bits;
            unsigned int val;
        } fil_lut_k1;
        union { // name: fil_wgt, offset: 0x3c
            struct {
                unsigned int reserve_0 : 8;
                unsigned int WGT_GAIN  : 8;
                unsigned int WGT_DECAY : 8;
                unsigned int reserve_1 : 8;
            } bits;
            unsigned int val;
        } fil_wgt;
        union { // name: fil_conf, offset: 0x40
            struct {
                unsigned int reserve_0      : 24;
                unsigned int LOW_CONF_TH    : 8;
                unsigned int LOW_CONF_RATIO : 8;
                unsigned int CONF_CNT_TH    : 4;
                unsigned int CONF_MEAN_TH   : 8;
            } bits;
            unsigned int val;
        } fil_conf;
        union { // name: dbg_inl, offset: 0x44
            struct {
                unsigned int reserve_0 : 4;
                unsigned int INK_MODE  : 4;
                unsigned int INK_EN    : 1;
                unsigned int reserve_1 : 23;
            } bits;
            unsigned int val;
        } dbg_inl;
        struct {
            unsigned int reserve_data[10];
        } reserve_reg_72_112;
        union { // name: dbg_info0, offset: 0x70
            struct {
                unsigned int reserve_0       : 16;
                unsigned int MEM_IN_LINE_CNT : 11;
                unsigned int IN_VLD          : 1;
                unsigned int IN_HSYNC        : 1;
                unsigned int MEM_IN_VSYNC    : 1;
                unsigned int IN_RDY          : 1;
                unsigned int reserve_1       : 1;
            } bits;
            unsigned int val;
        } dbg_info0;
        union { // name: dbg_info1, offset: 0x74
            struct {
                unsigned int reserve_0 : 24;
                unsigned int IN_FLAT   : 2;
                unsigned int IN_DIR    : 6;
                unsigned int IN_PIX    : 16;
            } bits;
            unsigned int val;
        } dbg_info1;
        union { // name: dbg_info2, offset: 0x78
            struct {
                unsigned int reserve_0    : 16;
                unsigned int OUT_LINE_CNT : 11;
                unsigned int OUT_VLD      : 1;
                unsigned int OUT_HSYNC    : 1;
                unsigned int OUT_VSYNC    : 1;
                unsigned int OUT_RDY      : 1;
                unsigned int reserve_1    : 1;
            } bits;
            unsigned int val;
        } dbg_info2;
        union { // name: dbg_info3, offset: 0x7c
            struct {
                unsigned int OUT_PIX   : 16;
                unsigned int reserve_0 : 16;
            } bits;
            unsigned int val;
        } dbg_info3;
    } regs;
    unsigned int data[32];
} es_rk3572_u;

// 0x00001200
typedef union sharp_rk3572 {
    struct {
        union { // name: ctrl, offset: 0x0
            struct {
                unsigned int sw_sharp_enable        : 1;
                unsigned int sw_lti_enable          : 1;
                unsigned int reserve_0              : 1;
                unsigned int sw_peaking_enable      : 1;
                unsigned int sw_peaking_ctrl_enable : 1;
                unsigned int reserve_1              : 1;
                unsigned int sw_edge_proc_enable    : 1;
                unsigned int sw_shoot_ctrl_enable   : 1;
                unsigned int sw_gain_ctrl_enable    : 1;
                unsigned int reserve_2              : 1;
                unsigned int sw_texture_adj_enable  : 1;
                unsigned int reserve_3              : 1;
                unsigned int sw_ink_enable          : 1;
                unsigned int reserve_4              : 19;
            } bits;
            unsigned int val;
        } ctrl;
        union { // name: auto_gating_imd, offset: 0x4
            struct {
                unsigned int sw_mem_gating_en          : 1;
                unsigned int sw_lti_gating_en          : 1;
                unsigned int reserve_0                 : 1;
                unsigned int sw_peaking_gating_en      : 1;
                unsigned int sw_peaking_ctrl_gating_en : 1;
                unsigned int reserve_1                 : 1;
                unsigned int sw_edge_proc_gating_en    : 1;
                unsigned int sw_shoot_ctrl_gating_en   : 1;
                unsigned int sw_gain_ctrl_gating_en    : 1;
                unsigned int reserve_2                 : 1;
                unsigned int sw_texture_adj_gating_en  : 1;
                unsigned int reserve_3                 : 21;
            } bits;
            unsigned int val;
        } auto_gating_imd;
        union { // name: peaking_filter_coe0, offset: 0x8
            struct {
                unsigned int sw_peaking_v00 : 4;
                unsigned int sw_peaking_v01 : 4;
                unsigned int sw_peaking_v02 : 4;
                unsigned int sw_peaking_v10 : 4;
                unsigned int sw_peaking_v11 : 4;
                unsigned int sw_peaking_v12 : 4;
                unsigned int reserve_0      : 8;
            } bits;
            unsigned int val;
        } peaking_filter_coe0;
        union { // name: peaking_filter_coe1, offset: 0xc
            struct {
                unsigned int sw_peaking_v20  : 4;
                unsigned int sw_peaking_v21  : 4;
                unsigned int sw_peaking_v22  : 4;
                unsigned int sw_peaking_usm0 : 4;
                unsigned int sw_peaking_usm1 : 4;
                unsigned int sw_peaking_usm2 : 4;
                unsigned int sw_diag_coef    : 3;
                unsigned int reserve_0       : 5;
            } bits;
            unsigned int val;
        } peaking_filter_coe1;
        union { // name: peaking_filter_coe2, offset: 0x10
            struct {
                unsigned int sw_peaking_h00 : 6;
                unsigned int reserve_0      : 2;
                unsigned int sw_peaking_h01 : 6;
                unsigned int reserve_1      : 2;
                unsigned int sw_peaking_h02 : 6;
                unsigned int reserve_2      : 10;
            } bits;
            unsigned int val;
        } peaking_filter_coe2;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_20_24;
        union { // name: peaking_filter_coe4, offset: 0x18
            struct {
                unsigned int sw_peaking_h10 : 6;
                unsigned int reserve_0      : 2;
                unsigned int sw_peaking_h11 : 6;
                unsigned int reserve_1      : 2;
                unsigned int sw_peaking_h12 : 6;
                unsigned int reserve_2      : 10;
            } bits;
            unsigned int val;
        } peaking_filter_coe4;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_28_32;
        union { // name: peaking_filter_coe6, offset: 0x20
            struct {
                unsigned int sw_peaking_h20 : 6;
                unsigned int reserve_0      : 2;
                unsigned int sw_peaking_h21 : 6;
                unsigned int reserve_1      : 2;
                unsigned int sw_peaking_h22 : 6;
                unsigned int reserve_2      : 10;
            } bits;
            unsigned int val;
        } peaking_filter_coe6;
        struct {
            unsigned int reserve_data[3];
        } reserve_reg_36_48;
        union { // name: peaking0_ctrl_coe0, offset: 0x30
            struct {
                unsigned int sw_peaking0_idx_n0 : 9;
                unsigned int reserve_0          : 7;
                unsigned int sw_peaking0_idx_n1 : 9;
                unsigned int reserve_1          : 7;
            } bits;
            unsigned int val;
        } peaking0_ctrl_coe0;
        union { // name: peaking0_ctrl_coe1, offset: 0x34
            struct {
                unsigned int sw_peaking0_idx_n2 : 9;
                unsigned int reserve_0          : 7;
                unsigned int sw_peaking0_idx_n3 : 9;
                unsigned int reserve_1          : 7;
            } bits;
            unsigned int val;
        } peaking0_ctrl_coe1;
        union { // name: peaking0_ctrl_coe2, offset: 0x38
            struct {
                unsigned int sw_peaking0_idx_p0 : 9;
                unsigned int reserve_0          : 7;
                unsigned int sw_peaking0_idx_p1 : 9;
                unsigned int reserve_1          : 7;
            } bits;
            unsigned int val;
        } peaking0_ctrl_coe2;
        union { // name: peaking0_ctrl_coe3, offset: 0x3c
            struct {
                unsigned int sw_peaking0_idx_p2 : 9;
                unsigned int reserve_0          : 7;
                unsigned int sw_peaking0_idx_p3 : 9;
                unsigned int reserve_1          : 7;
            } bits;
            unsigned int val;
        } peaking0_ctrl_coe3;
        union { // name: peaking0_ctrl_coe4, offset: 0x40
            struct {
                unsigned int sw_peaking0_value_n1 : 9;
                unsigned int reserve_0            : 7;
                unsigned int sw_peaking0_value_n2 : 9;
                unsigned int reserve_1            : 7;
            } bits;
            unsigned int val;
        } peaking0_ctrl_coe4;
        union { // name: peaking0_ctrl_coe5, offset: 0x44
            struct {
                unsigned int sw_peaking0_value_n3 : 9;
                unsigned int reserve_0            : 7;
                unsigned int sw_peaking0_value_p1 : 9;
                unsigned int reserve_1            : 7;
            } bits;
            unsigned int val;
        } peaking0_ctrl_coe5;
        union { // name: peaking0_ctrl_coe6, offset: 0x48
            struct {
                unsigned int sw_peaking0_value_p2 : 9;
                unsigned int reserve_0            : 7;
                unsigned int sw_peaking0_value_p3 : 9;
                unsigned int reserve_1            : 7;
            } bits;
            unsigned int val;
        } peaking0_ctrl_coe6;
        union { // name: peaking0_ctrl_coe7, offset: 0x4c
            struct {
                unsigned int sw_peaking0_ratio_n01 : 12;
                unsigned int reserve_0             : 4;
                unsigned int sw_peaking0_ratio_n12 : 12;
                unsigned int reserve_1             : 4;
            } bits;
            unsigned int val;
        } peaking0_ctrl_coe7;
        union { // name: peaking0_ctrl_coe8, offset: 0x50
            struct {
                unsigned int sw_peaking0_ratio_n23 : 12;
                unsigned int reserve_0             : 4;
                unsigned int sw_peaking0_ratio_p01 : 12;
                unsigned int reserve_1             : 4;
            } bits;
            unsigned int val;
        } peaking0_ctrl_coe8;
        union { // name: peaking0_ctrl_coe9, offset: 0x54
            struct {
                unsigned int sw_peaking0_ratio_p12 : 12;
                unsigned int sw_peaking0_ratio_p23 : 12;
                unsigned int reserve_0             : 8;
            } bits;
            unsigned int val;
        } peaking0_ctrl_coe9;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_88_92;
        union { // name: peaking1_ctrl_coe0, offset: 0x5c
            struct {
                unsigned int sw_peaking1_idx_n0 : 9;
                unsigned int reserve_0          : 7;
                unsigned int sw_peaking1_idx_n1 : 9;
                unsigned int reserve_1          : 7;
            } bits;
            unsigned int val;
        } peaking1_ctrl_coe0;
        union { // name: peaking1_ctrl_coe1, offset: 0x60
            struct {
                unsigned int sw_peaking1_idx_n2 : 9;
                unsigned int reserve_0          : 7;
                unsigned int sw_peaking1_idx_n3 : 9;
                unsigned int reserve_1          : 7;
            } bits;
            unsigned int val;
        } peaking1_ctrl_coe1;
        union { // name: peaking1_ctrl_coe2, offset: 0x64
            struct {
                unsigned int sw_peaking1_idx_p0 : 9;
                unsigned int reserve_0          : 7;
                unsigned int sw_peaking1_idx_p1 : 9;
                unsigned int reserve_1          : 7;
            } bits;
            unsigned int val;
        } peaking1_ctrl_coe2;
        union { // name: peaking1_ctrl_coe3, offset: 0x68
            struct {
                unsigned int sw_peaking1_idx_p2 : 9;
                unsigned int reserve_0          : 7;
                unsigned int sw_peaking1_idx_p3 : 9;
                unsigned int reserve_1          : 7;
            } bits;
            unsigned int val;
        } peaking1_ctrl_coe3;
        union { // name: peaking1_ctrl_coe4, offset: 0x6c
            struct {
                unsigned int sw_peaking1_value_n1 : 9;
                unsigned int reserve_0            : 7;
                unsigned int sw_peaking1_value_n2 : 9;
                unsigned int reserve_1            : 7;
            } bits;
            unsigned int val;
        } peaking1_ctrl_coe4;
        union { // name: peaking1_ctrl_coe5, offset: 0x70
            struct {
                unsigned int sw_peaking1_value_n3 : 9;
                unsigned int reserve_0            : 7;
                unsigned int sw_peaking1_value_p1 : 9;
                unsigned int reserve_1            : 7;
            } bits;
            unsigned int val;
        } peaking1_ctrl_coe5;
        union { // name: peaking1_ctrl_coe6, offset: 0x74
            struct {
                unsigned int sw_peaking1_value_p2 : 9;
                unsigned int reserve_0            : 7;
                unsigned int sw_peaking1_value_p3 : 9;
                unsigned int reserve_1            : 7;
            } bits;
            unsigned int val;
        } peaking1_ctrl_coe6;
        union { // name: peaking1_ctrl_coe7, offset: 0x78
            struct {
                unsigned int sw_peaking1_ratio_n01 : 12;
                unsigned int reserve_0             : 4;
                unsigned int sw_peaking1_ratio_n12 : 12;
                unsigned int reserve_1             : 4;
            } bits;
            unsigned int val;
        } peaking1_ctrl_coe7;
        union { // name: peaking1_ctrl_coe8, offset: 0x7c
            struct {
                unsigned int sw_peaking1_ratio_n23 : 12;
                unsigned int reserve_0             : 4;
                unsigned int sw_peaking1_ratio_p01 : 12;
                unsigned int reserve_1             : 4;
            } bits;
            unsigned int val;
        } peaking1_ctrl_coe8;
        union { // name: peaking1_ctrl_coe9, offset: 0x80
            struct {
                unsigned int sw_peaking1_ratio_p12 : 12;
                unsigned int sw_peaking1_ratio_p23 : 12;
                unsigned int reserve_0             : 8;
            } bits;
            unsigned int val;
        } peaking1_ctrl_coe9;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_132_136;
        union { // name: peaking2_ctrl_coe0, offset: 0x88
            struct {
                unsigned int sw_peaking2_idx_n0 : 9;
                unsigned int reserve_0          : 7;
                unsigned int sw_peaking2_idx_n1 : 9;
                unsigned int reserve_1          : 7;
            } bits;
            unsigned int val;
        } peaking2_ctrl_coe0;
        union { // name: peaking2_ctrl_coe1, offset: 0x8c
            struct {
                unsigned int sw_peaking2_idx_n2 : 9;
                unsigned int reserve_0          : 7;
                unsigned int sw_peaking2_idx_n3 : 9;
                unsigned int reserve_1          : 7;
            } bits;
            unsigned int val;
        } peaking2_ctrl_coe1;
        union { // name: peaking2_ctrl_coe2, offset: 0x90
            struct {
                unsigned int sw_peaking2_idx_p0 : 9;
                unsigned int reserve_0          : 7;
                unsigned int sw_peaking2_idx_p1 : 9;
                unsigned int reserve_1          : 7;
            } bits;
            unsigned int val;
        } peaking2_ctrl_coe2;
        union { // name: peaking2_ctrl_coe3, offset: 0x94
            struct {
                unsigned int sw_peaking2_idx_p2 : 9;
                unsigned int reserve_0          : 7;
                unsigned int sw_peaking2_idx_p3 : 9;
                unsigned int reserve_1          : 7;
            } bits;
            unsigned int val;
        } peaking2_ctrl_coe3;
        union { // name: peaking2_ctrl_coe4, offset: 0x98
            struct {
                unsigned int sw_peaking2_value_n1 : 9;
                unsigned int reserve_0            : 7;
                unsigned int sw_peaking2_value_n2 : 9;
                unsigned int reserve_1            : 7;
            } bits;
            unsigned int val;
        } peaking2_ctrl_coe4;
        union { // name: peaking2_ctrl_coe5, offset: 0x9c
            struct {
                unsigned int sw_peaking2_value_n3 : 9;
                unsigned int reserve_0            : 7;
                unsigned int sw_peaking2_value_p1 : 9;
                unsigned int reserve_1            : 7;
            } bits;
            unsigned int val;
        } peaking2_ctrl_coe5;
        union { // name: peaking2_ctrl_coe6, offset: 0xa0
            struct {
                unsigned int sw_peaking2_value_p2 : 9;
                unsigned int reserve_0            : 7;
                unsigned int sw_peaking2_value_p3 : 9;
                unsigned int reserve_1            : 7;
            } bits;
            unsigned int val;
        } peaking2_ctrl_coe6;
        union { // name: peaking2_ctrl_coe7, offset: 0xa4
            struct {
                unsigned int sw_peaking2_ratio_n01 : 12;
                unsigned int reserve_0             : 4;
                unsigned int sw_peaking2_ratio_n12 : 12;
                unsigned int reserve_1             : 4;
            } bits;
            unsigned int val;
        } peaking2_ctrl_coe7;
        union { // name: peaking2_ctrl_coe8, offset: 0xa8
            struct {
                unsigned int sw_peaking2_ratio_n23 : 12;
                unsigned int reserve_0             : 4;
                unsigned int sw_peaking2_ratio_p01 : 12;
                unsigned int reserve_1             : 4;
            } bits;
            unsigned int val;
        } peaking2_ctrl_coe8;
        union { // name: peaking2_ctrl_coe9, offset: 0xac
            struct {
                unsigned int sw_peaking2_ratio_p12 : 12;
                unsigned int sw_peaking2_ratio_p23 : 12;
                unsigned int reserve_0             : 8;
            } bits;
            unsigned int val;
        } peaking2_ctrl_coe9;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_176_180;
        union { // name: peaking3_ctrl_coe0, offset: 0xb4
            struct {
                unsigned int sw_peaking3_idx_n0 : 9;
                unsigned int reserve_0          : 7;
                unsigned int sw_peaking3_idx_n1 : 9;
                unsigned int reserve_1          : 7;
            } bits;
            unsigned int val;
        } peaking3_ctrl_coe0;
        union { // name: peaking3_ctrl_coe1, offset: 0xb8
            struct {
                unsigned int sw_peaking3_idx_n2 : 9;
                unsigned int reserve_0          : 7;
                unsigned int sw_peaking3_idx_n3 : 9;
                unsigned int reserve_1          : 7;
            } bits;
            unsigned int val;
        } peaking3_ctrl_coe1;
        union { // name: peaking3_ctrl_coe2, offset: 0xbc
            struct {
                unsigned int sw_peaking3_idx_p0 : 9;
                unsigned int reserve_0          : 7;
                unsigned int sw_peaking3_idx_p1 : 9;
                unsigned int reserve_1          : 7;
            } bits;
            unsigned int val;
        } peaking3_ctrl_coe2;
        union { // name: peaking3_ctrl_coe3, offset: 0xc0
            struct {
                unsigned int sw_peaking3_idx_p2 : 9;
                unsigned int reserve_0          : 7;
                unsigned int sw_peaking3_idx_p3 : 9;
                unsigned int reserve_1          : 7;
            } bits;
            unsigned int val;
        } peaking3_ctrl_coe3;
        union { // name: peaking3_ctrl_coe4, offset: 0xc4
            struct {
                unsigned int sw_peaking3_value_n1 : 9;
                unsigned int reserve_0            : 7;
                unsigned int sw_peaking3_value_n2 : 9;
                unsigned int reserve_1            : 7;
            } bits;
            unsigned int val;
        } peaking3_ctrl_coe4;
        union { // name: peaking3_ctrl_coe5, offset: 0xc8
            struct {
                unsigned int sw_peaking3_value_n3 : 9;
                unsigned int reserve_0            : 7;
                unsigned int sw_peaking3_value_p1 : 9;
                unsigned int reserve_1            : 7;
            } bits;
            unsigned int val;
        } peaking3_ctrl_coe5;
        union { // name: peaking3_ctrl_coe6, offset: 0xcc
            struct {
                unsigned int sw_peaking3_value_p2 : 9;
                unsigned int reserve_0            : 7;
                unsigned int sw_peaking3_value_p3 : 9;
                unsigned int reserve_1            : 7;
            } bits;
            unsigned int val;
        } peaking3_ctrl_coe6;
        union { // name: peaking3_ctrl_coe7, offset: 0xd0
            struct {
                unsigned int sw_peaking3_ratio_n01 : 12;
                unsigned int reserve_0             : 4;
                unsigned int sw_peaking3_ratio_n12 : 12;
                unsigned int reserve_1             : 4;
            } bits;
            unsigned int val;
        } peaking3_ctrl_coe7;
        union { // name: peaking3_ctrl_coe8, offset: 0xd4
            struct {
                unsigned int sw_peaking3_ratio_n23 : 12;
                unsigned int reserve_0             : 4;
                unsigned int sw_peaking3_ratio_p01 : 12;
                unsigned int reserve_1             : 4;
            } bits;
            unsigned int val;
        } peaking3_ctrl_coe8;
        union { // name: peaking3_ctrl_coe9, offset: 0xd8
            struct {
                unsigned int sw_peaking3_ratio_p12 : 12;
                unsigned int sw_peaking3_ratio_p23 : 12;
                unsigned int reserve_0             : 8;
            } bits;
            unsigned int val;
        } peaking3_ctrl_coe9;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_220_224;
        union { // name: peaking4_ctrl_coe0, offset: 0xe0
            struct {
                unsigned int sw_peaking4_idx_n0 : 9;
                unsigned int reserve_0          : 7;
                unsigned int sw_peaking4_idx_n1 : 9;
                unsigned int reserve_1          : 7;
            } bits;
            unsigned int val;
        } peaking4_ctrl_coe0;
        union { // name: peaking4_ctrl_coe1, offset: 0xe4
            struct {
                unsigned int sw_peaking4_idx_n2 : 9;
                unsigned int reserve_0          : 7;
                unsigned int sw_peaking4_idx_n3 : 9;
                unsigned int reserve_1          : 7;
            } bits;
            unsigned int val;
        } peaking4_ctrl_coe1;
        union { // name: peaking4_ctrl_coe2, offset: 0xe8
            struct {
                unsigned int sw_peaking4_idx_p0 : 9;
                unsigned int reserve_0          : 7;
                unsigned int sw_peaking4_idx_p1 : 9;
                unsigned int reserve_1          : 7;
            } bits;
            unsigned int val;
        } peaking4_ctrl_coe2;
        union { // name: peaking4_ctrl_coe3, offset: 0xec
            struct {
                unsigned int sw_peaking4_idx_p2 : 9;
                unsigned int reserve_0          : 7;
                unsigned int sw_peaking4_idx_p3 : 9;
                unsigned int reserve_1          : 7;
            } bits;
            unsigned int val;
        } peaking4_ctrl_coe3;
        union { // name: peaking4_ctrl_coe4, offset: 0xf0
            struct {
                unsigned int sw_peaking4_value_n1 : 9;
                unsigned int reserve_0            : 7;
                unsigned int sw_peaking4_value_n2 : 9;
                unsigned int reserve_1            : 7;
            } bits;
            unsigned int val;
        } peaking4_ctrl_coe4;
        union { // name: peaking4_ctrl_coe5, offset: 0xf4
            struct {
                unsigned int sw_peaking4_value_n3 : 9;
                unsigned int reserve_0            : 7;
                unsigned int sw_peaking4_value_p1 : 9;
                unsigned int reserve_1            : 7;
            } bits;
            unsigned int val;
        } peaking4_ctrl_coe5;
        union { // name: peaking4_ctrl_coe6, offset: 0xf8
            struct {
                unsigned int sw_peaking4_value_p2 : 9;
                unsigned int reserve_0            : 7;
                unsigned int sw_peaking4_value_p3 : 9;
                unsigned int reserve_1            : 7;
            } bits;
            unsigned int val;
        } peaking4_ctrl_coe6;
        union { // name: peaking4_ctrl_coe7, offset: 0xfc
            struct {
                unsigned int sw_peaking4_ratio_n01 : 12;
                unsigned int reserve_0             : 4;
                unsigned int sw_peaking4_ratio_n12 : 12;
                unsigned int reserve_1             : 4;
            } bits;
            unsigned int val;
        } peaking4_ctrl_coe7;
        union { // name: peaking4_ctrl_coe8, offset: 0x100
            struct {
                unsigned int sw_peaking4_ratio_n23 : 12;
                unsigned int reserve_0             : 4;
                unsigned int sw_peaking4_ratio_p01 : 12;
                unsigned int reserve_1             : 4;
            } bits;
            unsigned int val;
        } peaking4_ctrl_coe8;
        union { // name: peaking4_ctrl_coe9, offset: 0x104
            struct {
                unsigned int sw_peaking4_ratio_p12 : 12;
                unsigned int sw_peaking4_ratio_p23 : 12;
                unsigned int reserve_0             : 8;
            } bits;
            unsigned int val;
        } peaking4_ctrl_coe9;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_264_268;
        union { // name: peaking5_ctrl_coe0, offset: 0x10c
            struct {
                unsigned int sw_peaking5_idx_n0 : 9;
                unsigned int reserve_0          : 7;
                unsigned int sw_peaking5_idx_n1 : 9;
                unsigned int reserve_1          : 7;
            } bits;
            unsigned int val;
        } peaking5_ctrl_coe0;
        union { // name: peaking5_ctrl_coe1, offset: 0x110
            struct {
                unsigned int sw_peaking5_idx_n2 : 9;
                unsigned int reserve_0          : 7;
                unsigned int sw_peaking5_idx_n3 : 9;
                unsigned int reserve_1          : 7;
            } bits;
            unsigned int val;
        } peaking5_ctrl_coe1;
        union { // name: peaking5_ctrl_coe2, offset: 0x114
            struct {
                unsigned int sw_peaking5_idx_p0 : 9;
                unsigned int reserve_0          : 7;
                unsigned int sw_peaking5_idx_p1 : 9;
                unsigned int reserve_1          : 7;
            } bits;
            unsigned int val;
        } peaking5_ctrl_coe2;
        union { // name: peaking5_ctrl_coe3, offset: 0x118
            struct {
                unsigned int sw_peaking5_idx_p2 : 9;
                unsigned int reserve_0          : 7;
                unsigned int sw_peaking5_idx_p3 : 9;
                unsigned int reserve_1          : 7;
            } bits;
            unsigned int val;
        } peaking5_ctrl_coe3;
        union { // name: peaking5_ctrl_coe4, offset: 0x11c
            struct {
                unsigned int sw_peaking5_value_n1 : 9;
                unsigned int reserve_0            : 7;
                unsigned int sw_peaking5_value_n2 : 9;
                unsigned int reserve_1            : 7;
            } bits;
            unsigned int val;
        } peaking5_ctrl_coe4;
        union { // name: peaking5_ctrl_coe5, offset: 0x120
            struct {
                unsigned int sw_peaking5_value_n3 : 9;
                unsigned int reserve_0            : 7;
                unsigned int sw_peaking5_value_p1 : 9;
                unsigned int reserve_1            : 7;
            } bits;
            unsigned int val;
        } peaking5_ctrl_coe5;
        union { // name: peaking5_ctrl_coe6, offset: 0x124
            struct {
                unsigned int sw_peaking5_value_p2 : 9;
                unsigned int reserve_0            : 7;
                unsigned int sw_peaking5_value_p3 : 9;
                unsigned int reserve_1            : 7;
            } bits;
            unsigned int val;
        } peaking5_ctrl_coe6;
        union { // name: peaking5_ctrl_coe7, offset: 0x128
            struct {
                unsigned int sw_peaking5_ratio_n01 : 12;
                unsigned int reserve_0             : 4;
                unsigned int sw_peaking5_ratio_n12 : 12;
                unsigned int reserve_1             : 4;
            } bits;
            unsigned int val;
        } peaking5_ctrl_coe7;
        union { // name: peaking5_ctrl_coe8, offset: 0x12c
            struct {
                unsigned int sw_peaking5_ratio_n23 : 12;
                unsigned int reserve_0             : 4;
                unsigned int sw_peaking5_ratio_p01 : 12;
                unsigned int reserve_1             : 4;
            } bits;
            unsigned int val;
        } peaking5_ctrl_coe8;
        union { // name: peaking5_ctrl_coe9, offset: 0x130
            struct {
                unsigned int sw_peaking5_ratio_p12 : 12;
                unsigned int sw_peaking5_ratio_p23 : 12;
                unsigned int reserve_0             : 8;
            } bits;
            unsigned int val;
        } peaking5_ctrl_coe9;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_308_312;
        union { // name: peaking6_ctrl_coe0, offset: 0x138
            struct {
                unsigned int sw_peaking6_idx_n0 : 9;
                unsigned int reserve_0          : 7;
                unsigned int sw_peaking6_idx_n1 : 9;
                unsigned int reserve_1          : 7;
            } bits;
            unsigned int val;
        } peaking6_ctrl_coe0;
        union { // name: peaking6_ctrl_coe1, offset: 0x13c
            struct {
                unsigned int sw_peaking6_idx_n2 : 9;
                unsigned int reserve_0          : 7;
                unsigned int sw_peaking6_idx_n3 : 9;
                unsigned int reserve_1          : 7;
            } bits;
            unsigned int val;
        } peaking6_ctrl_coe1;
        union { // name: peaking6_ctrl_coe2, offset: 0x140
            struct {
                unsigned int sw_peaking6_idx_p0 : 9;
                unsigned int reserve_0          : 7;
                unsigned int sw_peaking6_idx_p1 : 9;
                unsigned int reserve_1          : 7;
            } bits;
            unsigned int val;
        } peaking6_ctrl_coe2;
        union { // name: peaking6_ctrl_coe3, offset: 0x144
            struct {
                unsigned int sw_peaking6_idx_p2 : 9;
                unsigned int reserve_0          : 7;
                unsigned int sw_peaking6_idx_p3 : 9;
                unsigned int reserve_1          : 7;
            } bits;
            unsigned int val;
        } peaking6_ctrl_coe3;
        union { // name: peaking6_ctrl_coe4, offset: 0x148
            struct {
                unsigned int sw_peaking6_value_n1 : 9;
                unsigned int reserve_0            : 7;
                unsigned int sw_peaking6_value_n2 : 9;
                unsigned int reserve_1            : 7;
            } bits;
            unsigned int val;
        } peaking6_ctrl_coe4;
        union { // name: peaking6_ctrl_coe5, offset: 0x14c
            struct {
                unsigned int sw_peaking6_value_n3 : 9;
                unsigned int reserve_0            : 7;
                unsigned int sw_peaking6_value_p1 : 9;
                unsigned int reserve_1            : 7;
            } bits;
            unsigned int val;
        } peaking6_ctrl_coe5;
        union { // name: peaking6_ctrl_coe6, offset: 0x150
            struct {
                unsigned int sw_peaking6_value_p2 : 9;
                unsigned int reserve_0            : 7;
                unsigned int sw_peaking6_value_p3 : 9;
                unsigned int reserve_1            : 7;
            } bits;
            unsigned int val;
        } peaking6_ctrl_coe6;
        union { // name: peaking6_ctrl_coe7, offset: 0x154
            struct {
                unsigned int sw_peaking6_ratio_n01 : 12;
                unsigned int reserve_0             : 4;
                unsigned int sw_peaking6_ratio_n12 : 12;
                unsigned int reserve_1             : 4;
            } bits;
            unsigned int val;
        } peaking6_ctrl_coe7;
        union { // name: peaking6_ctrl_coe8, offset: 0x158
            struct {
                unsigned int sw_peaking6_ratio_n23 : 12;
                unsigned int reserve_0             : 4;
                unsigned int sw_peaking6_ratio_p01 : 12;
                unsigned int reserve_1             : 4;
            } bits;
            unsigned int val;
        } peaking6_ctrl_coe8;
        union { // name: peaking6_ctrl_coe9, offset: 0x15c
            struct {
                unsigned int sw_peaking6_ratio_p12 : 12;
                unsigned int sw_peaking6_ratio_p23 : 12;
                unsigned int reserve_0             : 8;
            } bits;
            unsigned int val;
        } peaking6_ctrl_coe9;
        struct {
            unsigned int reserve_data[12];
        } reserve_reg_352_400;
        union { // name: peaking_ctrl0, offset: 0x190
            struct {
                unsigned int sw_peaking_gain     : 10;
                unsigned int reserve_0           : 2;
                unsigned int sw_nondir_thr       : 7;
                unsigned int reserve_1           : 1;
                unsigned int sw_dir_cmp_ratio    : 4;
                unsigned int sw_nondir_wgt_ratio : 5;
                unsigned int reserve_2           : 3;
            } bits;
            unsigned int val;
        } peaking_ctrl0;
        union { // name: peaking_ctrl1, offset: 0x194
            struct {
                unsigned int sw_nondir_wgt_offset : 8;
                unsigned int sw_dir_cnt_thr       : 4;
                unsigned int sw_dir_cnt_avg       : 3;
                unsigned int reserve_0            : 1;
                unsigned int sw_dir_cnt_offset    : 4;
                unsigned int sw_diag_dir_thr      : 7;
                unsigned int reserve_1            : 5;
            } bits;
            unsigned int val;
        } peaking_ctrl1;
        union { // name: peaking_ctrl2, offset: 0x198
            struct {
                unsigned int sw_diag_adjgain_tab0 : 4;
                unsigned int sw_diag_adjgain_tab1 : 4;
                unsigned int sw_diag_adjgain_tab2 : 4;
                unsigned int sw_diag_adjgain_tab3 : 4;
                unsigned int sw_diag_adjgain_tab4 : 4;
                unsigned int sw_diag_adjgain_tab5 : 4;
                unsigned int sw_diag_adjgain_tab6 : 4;
                unsigned int sw_diag_adjgain_tab7 : 4;
            } bits;
            unsigned int val;
        } peaking_ctrl2;
        union { // name: peaking_ctrl3, offset: 0x19c
            struct {
                unsigned int sw_edge_alpha_over_non          : 7;
                unsigned int reserve_0                       : 1;
                unsigned int sw_edge_alpha_under_non         : 7;
                unsigned int reserve_1                       : 1;
                unsigned int sw_edge_alpha_over_unlimit_non  : 7;
                unsigned int reserve_2                       : 1;
                unsigned int sw_edge_alpha_under_unlimit_non : 7;
                unsigned int reserve_3                       : 1;
            } bits;
            unsigned int val;
        } peaking_ctrl3;
        union { // name: peaking_ctrl4, offset: 0x1a0
            struct {
                unsigned int sw_edge_alpha_over_v          : 7;
                unsigned int reserve_0                     : 1;
                unsigned int sw_edge_alpha_under_v         : 7;
                unsigned int reserve_1                     : 1;
                unsigned int sw_edge_alpha_over_unlimit_v  : 7;
                unsigned int reserve_2                     : 1;
                unsigned int sw_edge_alpha_under_unlimit_v : 7;
                unsigned int reserve_3                     : 1;
            } bits;
            unsigned int val;
        } peaking_ctrl4;
        union { // name: peaking_ctrl5, offset: 0x1a4
            struct {
                unsigned int sw_edge_alpha_over_h          : 7;
                unsigned int reserve_0                     : 1;
                unsigned int sw_edge_alpha_under_h         : 7;
                unsigned int reserve_1                     : 1;
                unsigned int sw_edge_alpha_over_unlimit_h  : 7;
                unsigned int reserve_2                     : 1;
                unsigned int sw_edge_alpha_under_unlimit_h : 7;
                unsigned int reserve_3                     : 1;
            } bits;
            unsigned int val;
        } peaking_ctrl5;
        union { // name: peaking_ctrl6, offset: 0x1a8
            struct {
                unsigned int sw_edge_alpha_over_d0          : 7;
                unsigned int reserve_0                      : 1;
                unsigned int sw_edge_alpha_under_d0         : 7;
                unsigned int reserve_1                      : 1;
                unsigned int sw_edge_alpha_over_unlimit_d0  : 7;
                unsigned int reserve_2                      : 1;
                unsigned int sw_edge_alpha_under_unlimit_d0 : 7;
                unsigned int reserve_3                      : 1;
            } bits;
            unsigned int val;
        } peaking_ctrl6;
        union { // name: peaking_ctrl7, offset: 0x1ac
            struct {
                unsigned int sw_edge_alpha_over_d1          : 7;
                unsigned int reserve_0                      : 1;
                unsigned int sw_edge_alpha_under_d1         : 7;
                unsigned int reserve_1                      : 1;
                unsigned int sw_edge_alpha_over_unlimit_d1  : 7;
                unsigned int reserve_2                      : 1;
                unsigned int sw_edge_alpha_under_unlimit_d1 : 7;
                unsigned int reserve_3                      : 1;
            } bits;
            unsigned int val;
        } peaking_ctrl7;
        union { // name: peaking_ctrl8, offset: 0x1b0
            struct {
                unsigned int sw_edge_delta_offset_non : 8;
                unsigned int sw_edge_delta_offset_v   : 8;
                unsigned int sw_edge_delta_offset_h   : 8;
                unsigned int reserve_0                : 8;
            } bits;
            unsigned int val;
        } peaking_ctrl8;
        union { // name: peaking_ctrl9, offset: 0x1b4
            struct {
                unsigned int sw_edge_delta_offset_d0 : 8;
                unsigned int sw_edge_delta_offset_d1 : 8;
                unsigned int reserve_0               : 16;
            } bits;
            unsigned int val;
        } peaking_ctrl9;
        union { // name: shoot_ctrl0, offset: 0x1b8
            struct {
                unsigned int sw_shoot_filt_radius  : 1;
                unsigned int reserve_0             : 3;
                unsigned int sw_shoot_delta_offset : 8;
                unsigned int sw_shoot_alpha_over   : 7;
                unsigned int reserve_1             : 1;
                unsigned int sw_shoot_alpha_under  : 7;
                unsigned int reserve_2             : 5;
            } bits;
            unsigned int val;
        } shoot_ctrl0;
        union { // name: shoot_ctrl1, offset: 0x1bc
            struct {
                unsigned int sw_shoot_alpha_over_unlimit  : 7;
                unsigned int reserve_0                    : 1;
                unsigned int sw_shoot_alpha_under_unlimit : 7;
                unsigned int reserve_1                    : 17;
            } bits;
            unsigned int val;
        } shoot_ctrl1;
        union { // name: gain_ctrl0, offset: 0x1c0
            struct {
                unsigned int sw_adp_idx0 : 8;
                unsigned int reserve_0   : 2;
                unsigned int sw_adp_idx1 : 8;
                unsigned int reserve_1   : 2;
                unsigned int sw_adp_idx2 : 8;
                unsigned int reserve_2   : 4;
            } bits;
            unsigned int val;
        } gain_ctrl0;
        union { // name: gain_ctrl1, offset: 0x1c4
            struct {
                unsigned int sw_adp_idx3  : 8;
                unsigned int reserve_0    : 4;
                unsigned int sw_adp_gain0 : 7;
                unsigned int reserve_1    : 1;
                unsigned int sw_adp_gain1 : 7;
                unsigned int reserve_2    : 5;
            } bits;
            unsigned int val;
        } gain_ctrl1;
        union { // name: gain_ctrl2, offset: 0x1c8
            struct {
                unsigned int sw_adp_gain2 : 7;
                unsigned int reserve_0    : 1;
                unsigned int sw_adp_gain3 : 7;
                unsigned int reserve_1    : 1;
                unsigned int sw_adp_gain4 : 7;
                unsigned int reserve_2    : 9;
            } bits;
            unsigned int val;
        } gain_ctrl2;
        union { // name: gain_ctrl3, offset: 0x1cc
            struct {
                unsigned int sw_adp_slp01 : 11;
                unsigned int reserve_0    : 1;
                unsigned int sw_adp_slp12 : 11;
                unsigned int reserve_1    : 9;
            } bits;
            unsigned int val;
        } gain_ctrl3;
        struct {
            unsigned int reserve_data[12];
        } reserve_reg_464_512;
        union { // name: gain_ctrl4, offset: 0x200
            struct {
                unsigned int sw_adp_slp23 : 11;
                unsigned int reserve_0    : 1;
                unsigned int sw_adp_slp34 : 11;
                unsigned int reserve_1    : 9;
            } bits;
            unsigned int val;
        } gain_ctrl4;
        union { // name: gain_ctrl5, offset: 0x204
            struct {
                unsigned int sw_adp_slp45 : 11;
                unsigned int sw_var_idx0  : 8;
                unsigned int reserve_0    : 2;
                unsigned int sw_var_idx1  : 8;
                unsigned int reserve_1    : 3;
            } bits;
            unsigned int val;
        } gain_ctrl5;
        union { // name: gain_ctrl6, offset: 0x208
            struct {
                unsigned int sw_var_idx2  : 8;
                unsigned int reserve_0    : 4;
                unsigned int sw_var_idx3  : 8;
                unsigned int reserve_1    : 4;
                unsigned int sw_var_gain0 : 7;
                unsigned int reserve_2    : 1;
            } bits;
            unsigned int val;
        } gain_ctrl6;
        union { // name: gain_ctrl7, offset: 0x20c
            struct {
                unsigned int sw_var_gain1 : 7;
                unsigned int reserve_0    : 1;
                unsigned int sw_var_gain2 : 7;
                unsigned int reserve_1    : 1;
                unsigned int sw_var_gain3 : 7;
                unsigned int reserve_2    : 1;
                unsigned int sw_var_gain4 : 7;
                unsigned int reserve_3    : 1;
            } bits;
            unsigned int val;
        } gain_ctrl7;
        union { // name: gain_ctrl8, offset: 0x210
            struct {
                unsigned int sw_var_slp01 : 11;
                unsigned int reserve_0    : 1;
                unsigned int sw_var_slp12 : 11;
                unsigned int reserve_1    : 9;
            } bits;
            unsigned int val;
        } gain_ctrl8;
        union { // name: gain_ctrl9, offset: 0x214
            struct {
                unsigned int sw_var_slp23 : 11;
                unsigned int reserve_0    : 1;
                unsigned int sw_var_slp34 : 11;
                unsigned int reserve_1    : 9;
            } bits;
            unsigned int val;
        } gain_ctrl9;
        union { // name: gain_ctrl10, offset: 0x218
            struct {
                unsigned int sw_var_slp45  : 11;
                unsigned int reserve_0     : 5;
                unsigned int sw_lum_select : 2;
                unsigned int reserve_1     : 2;
                unsigned int sw_lum_idx0   : 8;
                unsigned int reserve_2     : 4;
            } bits;
            unsigned int val;
        } gain_ctrl10;
        union { // name: gain_ctrl11, offset: 0x21c
            struct {
                unsigned int sw_lum_idx1 : 8;
                unsigned int reserve_0   : 2;
                unsigned int sw_lum_idx2 : 8;
                unsigned int reserve_1   : 2;
                unsigned int sw_lum_idx3 : 8;
                unsigned int reserve_2   : 4;
            } bits;
            unsigned int val;
        } gain_ctrl11;
        union { // name: gain_ctrl12, offset: 0x220
            struct {
                unsigned int sw_lum_gain0 : 7;
                unsigned int reserve_0    : 1;
                unsigned int sw_lum_gain1 : 7;
                unsigned int reserve_1    : 1;
                unsigned int sw_lum_gain2 : 7;
                unsigned int reserve_2    : 1;
                unsigned int sw_lum_gain3 : 7;
                unsigned int reserve_3    : 1;
            } bits;
            unsigned int val;
        } gain_ctrl12;
        union { // name: gain_ctrl13, offset: 0x224
            struct {
                unsigned int sw_lum_gain4 : 7;
                unsigned int reserve_0    : 1;
                unsigned int sw_lum_slp01 : 11;
                unsigned int reserve_1    : 1;
                unsigned int sw_lum_slp12 : 11;
                unsigned int reserve_2    : 1;
            } bits;
            unsigned int val;
        } gain_ctrl13;
        union { // name: gain_ctrl14, offset: 0x228
            struct {
                unsigned int sw_lum_slp23 : 11;
                unsigned int reserve_0    : 1;
                unsigned int sw_lum_slp34 : 11;
                unsigned int reserve_1    : 9;
            } bits;
            unsigned int val;
        } gain_ctrl14;
        union { // name: gain_ctrl15, offset: 0x22c
            struct {
                unsigned int sw_lum_slp45 : 11;
                unsigned int reserve_0    : 21;
            } bits;
            unsigned int val;
        } gain_ctrl15;
        struct {
            unsigned int reserve_data[16];
        } reserve_reg_560_624;
        union { // name: texture_ctrl0, offset: 0x270
            struct {
                unsigned int sw_idxmode_select : 1;
                unsigned int sw_ymode_select   : 2;
                unsigned int reserve_0         : 1;
                unsigned int sw_tex_idx0       : 8;
                unsigned int reserve_1         : 4;
                unsigned int sw_tex_idx1       : 8;
                unsigned int reserve_2         : 8;
            } bits;
            unsigned int val;
        } texture_ctrl0;
        union { // name: texture_ctrl1, offset: 0x274
            struct {
                unsigned int sw_tex_idx2  : 8;
                unsigned int reserve_0    : 4;
                unsigned int sw_tex_idx3  : 8;
                unsigned int reserve_1    : 4;
                unsigned int sw_tex_gain0 : 7;
                unsigned int reserve_2    : 1;
            } bits;
            unsigned int val;
        } texture_ctrl1;
        union { // name: texture_ctrl2, offset: 0x278
            struct {
                unsigned int sw_tex_gain1 : 7;
                unsigned int reserve_0    : 1;
                unsigned int sw_tex_gain2 : 7;
                unsigned int reserve_1    : 1;
                unsigned int sw_tex_gain3 : 7;
                unsigned int reserve_2    : 1;
                unsigned int sw_tex_gain4 : 7;
                unsigned int reserve_3    : 1;
            } bits;
            unsigned int val;
        } texture_ctrl2;
        union { // name: texture_ctrl3, offset: 0x27c
            struct {
                unsigned int sw_tex_slp01 : 11;
                unsigned int reserve_0    : 1;
                unsigned int sw_tex_slp12 : 11;
                unsigned int reserve_1    : 9;
            } bits;
            unsigned int val;
        } texture_ctrl3;
        union { // name: texture_ctrl4, offset: 0x280
            struct {
                unsigned int sw_tex_slp23 : 11;
                unsigned int reserve_0    : 1;
                unsigned int sw_tex_slp34 : 11;
                unsigned int reserve_1    : 9;
            } bits;
            unsigned int val;
        } texture_ctrl4;
        union { // name: texture_ctrl5, offset: 0x284
            struct {
                unsigned int sw_tex_slp45 : 11;
                unsigned int reserve_0    : 21;
            } bits;
            unsigned int val;
        } texture_ctrl5;
        union { // name: lti_ctrl0, offset: 0x288
            struct {
                unsigned int sw_ltih_radius : 1;
                unsigned int reserve_0      : 3;
                unsigned int sw_ltih_slp1   : 9;
                unsigned int reserve_1      : 3;
                unsigned int sw_ltih_thr1   : 9;
                unsigned int reserve_2      : 7;
            } bits;
            unsigned int val;
        } lti_ctrl0;
        union { // name: lti_ctrl1, offset: 0x28c
            struct {
                unsigned int sw_ltih_noisethrneg : 10;
                unsigned int reserve_0           : 2;
                unsigned int sw_ltih_noisethrpos : 10;
                unsigned int reserve_1           : 2;
                unsigned int sw_ltih_tigain      : 5;
                unsigned int reserve_2           : 3;
            } bits;
            unsigned int val;
        } lti_ctrl1;
        union { // name: lti_ctrl2, offset: 0x290
            struct {
                unsigned int sw_ltiv_radius : 1;
                unsigned int reserve_0      : 3;
                unsigned int sw_ltiv_slp1   : 9;
                unsigned int reserve_1      : 3;
                unsigned int sw_ltiv_thr1   : 9;
                unsigned int reserve_2      : 7;
            } bits;
            unsigned int val;
        } lti_ctrl2;
        union { // name: lti_ctrl3, offset: 0x294
            struct {
                unsigned int sw_ltiv_noisethrneg : 10;
                unsigned int reserve_0           : 2;
                unsigned int sw_ltiv_noisethrpos : 10;
                unsigned int reserve_1           : 2;
                unsigned int sw_ltiv_tigain      : 5;
                unsigned int reserve_2           : 3;
            } bits;
            unsigned int val;
        } lti_ctrl3;
        struct {
            unsigned int reserve_data[4];
        } reserve_reg_664_680;
        union { // name: debug_ctrl0, offset: 0x2a8
            struct {
                unsigned int sw_debug_mode : 4;
                unsigned int reserve_0     : 28;
            } bits;
            unsigned int val;
        } debug_ctrl0;
    } regs;
    unsigned int data[171];
} sharp_rk3572_u;

// 0x00002000
typedef union zme_rk3572 {
    struct {
        struct {
            unsigned int reserve_data[512];
        } reserve_reg_0_2048;
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
                unsigned int yrgb_xsd_en       : 1;
                unsigned int yrgb_xsu_en       : 1;
                unsigned int yrgb_xscl_mode    : 2;
                unsigned int yrgb_ysd_en       : 1;
                unsigned int yrgb_ysu_en       : 1;
                unsigned int yrgb_yscl_mode    : 2;
                unsigned int yrgb_dering_en    : 1;
                unsigned int yrgb_gt_en        : 1;
                unsigned int yrgb_gt_mode      : 2;
                unsigned int reserve_0         : 4;
                unsigned int yrgb_xsd_bypass   : 1;
                unsigned int yrgb_ys_bypass    : 1;
                unsigned int yrgb_xsu_bypass   : 1;
                unsigned int reserve_1         : 1;
                unsigned int yrgb_xscl_coe_sel : 4;
                unsigned int yrgb_yscl_coe_sel : 4;
                unsigned int reserve_2         : 4;
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
                unsigned int cbcr_xsd_en       : 1;
                unsigned int cbcr_xsu_en       : 1;
                unsigned int cbcr_xscl_mode    : 2;
                unsigned int cbcr_ysd_en       : 1;
                unsigned int cbcr_ysu_en       : 1;
                unsigned int cbcr_yscl_mode    : 2;
                unsigned int cbcr_dering_en    : 1;
                unsigned int cbcr_gt_en        : 1;
                unsigned int cbcr_gt_mode      : 2;
                unsigned int reserve_0         : 4;
                unsigned int cbcr_xsd_bypass   : 1;
                unsigned int cbcr_ys_bypass    : 1;
                unsigned int cbcr_xsu_bypass   : 1;
                unsigned int reserve_1         : 1;
                unsigned int cbcr_xscl_coe_sel : 4;
                unsigned int cbcr_yscl_coe_sel : 4;
                unsigned int reserve_2         : 4;
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
} zme_rk3572_u;

#endif /* VDPP_RK3572_H */
