#ifndef VOP_RK3538_H
#define VOP_RK3538_H

// 0x00000000
typedef union sys_ctrl_rk3538 {
    struct {
        union { // name: sys_reg_cfg_done, offset: 0x0
            struct {
                unsigned int reg_load_global0_en  : 1;
                unsigned int reserve_0            : 3;
                unsigned int reg_load_sys0_en     : 1;
                unsigned int reserve_1            : 10;
                unsigned int sw_global_regdone_en : 1;
                unsigned int write_mask           : 16;
            } bits;
            unsigned int val;
        } sys_reg_cfg_done;
        union { // name: sys_version_info, offset: 0x4
            struct {
                unsigned int svnbuild : 16;
                unsigned int minor    : 8;
                unsigned int major    : 8;
            } bits;
            unsigned int val;
        } sys_version_info;
        union { // name: sys_auto_ctrl_imd, offset: 0x8
            struct {
                unsigned int cluster0_auto_gating_en   : 1;
                unsigned int reserve_0                 : 3;
                unsigned int esmart_scl_auto_gating_en : 1;
                unsigned int reserve_1                 : 1;
                unsigned int win_aclk_auto_gating_en   : 1;
                unsigned int pre_aclk_auto_gating_en   : 1;
                unsigned int overlay_auto_gating_en    : 1;
                unsigned int reserve_2                 : 1;
                unsigned int cabc_auto_gating_en       : 1;
                unsigned int reserve_3                 : 1;
                unsigned int pwmclk_auto_gating_en     : 1;
                unsigned int prescan_auto_gating_en    : 1;
                unsigned int vp_dclk_gating_en         : 1;
                unsigned int sw_axi_aclk_gating_en     : 1;
                unsigned int reserve_4                 : 9;
                unsigned int vp0_aclk_gating_en        : 1;
                unsigned int reserve_5                 : 3;
                unsigned int sw_axi0_aclk_gating_en    : 1;
                unsigned int reserve_6                 : 1;
                unsigned int auto_ckg_en               : 1;
            } bits;
            unsigned int val;
        } sys_auto_ctrl_imd;
        union { // name: sys_vop_standby, offset: 0xc
            struct {
                unsigned int reserve_0      : 12;
                unsigned int vp0_standby_en : 1;
                unsigned int reserve_1      : 19;
            } bits;
            unsigned int val;
        } sys_vop_standby;
        struct {
            unsigned int reserve_data[5];
        } reserve_reg_16_36;
        union { // name: sys_axi_lut_ctrl_imd, offset: 0x24
            struct {
                unsigned int lut_dma_en   : 1;
                unsigned int lut_dma_stop : 1;
                unsigned int lut_dma_rlen : 2;
                unsigned int lut_dma_rid  : 5;
                unsigned int lut_use_axi1 : 1;
                unsigned int reserve_0    : 22;
            } bits;
            unsigned int val;
        } sys_axi_lut_ctrl_imd;
        union { // name: sys_port_ctrl_imd, offset: 0x28
            struct {
                unsigned int vp0_ils_reg_done_en : 1;
                unsigned int reserve_0           : 3;
                unsigned int dsp_vs_t_sel        : 1;
                unsigned int auto_cs_en          : 1;
                unsigned int reserve_1           : 2;
                unsigned int vfp0_dma_stop_en    : 1;
                unsigned int reserve_2           : 3;
                unsigned int vp0_dclk_src_sel    : 1;
                unsigned int reserve_3           : 2;
                unsigned int auto_cs_mode        : 1;
                unsigned int write_mask          : 16;
            } bits;
            unsigned int val;
        } sys_port_ctrl_imd;
        union { // name: sys_vop_pre_pd_ctrl_imd, offset: 0x2c
            struct {
                unsigned int vop_pre_pd_en     : 1;
                unsigned int reserve_0         : 14;
                unsigned int vop_pre_pd_imd_en : 1;
                unsigned int write_mask        : 16;
            } bits;
            unsigned int val;
        } sys_vop_pre_pd_ctrl_imd;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_48_52;
        union { // name: sys_esmart_pd_ctrl_imd, offset: 0x34
            struct {
                unsigned int reserve_0      : 6;
                unsigned int esmart_lb_mode : 2;
                unsigned int reserve_1      : 8;
                unsigned int write_mask     : 16;
            } bits;
            unsigned int val;
        } sys_esmart_pd_ctrl_imd;
        union { // name: sys_var_ferq_ctrl_imd, offset: 0x38
            struct {
                unsigned int dma_finish_mode        : 2;
                unsigned int axi_dma_finish_and_en  : 1;
                unsigned int reserve_0              : 1;
                unsigned int vp0_line_flag_and_en   : 1;
                unsigned int reserve_1              : 3;
                unsigned int vp0_dsp_hold_and_en    : 1;
                unsigned int reserve_2              : 3;
                unsigned int vp0_almost_full_and_en : 1;
                unsigned int reserve_3              : 5;
                unsigned int axi_dma_finish_or_en   : 1;
                unsigned int reserve_4              : 1;
                unsigned int vp0_line_flag_or_en    : 1;
                unsigned int reserve_5              : 3;
                unsigned int vp0_dsp_hold_or_en     : 1;
                unsigned int reserve_6              : 3;
                unsigned int vp0_almost_full_or_en  : 1;
                unsigned int reserve_7              : 3;
            } bits;
            unsigned int val;
        } sys_var_ferq_ctrl_imd;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_60_64;
        union { // name: metadata_ctrl, offset: 0x40
            struct {
                unsigned int metadata_lut_en     : 1;
                unsigned int metadata_rd_err_clr : 1;
                unsigned int metadata_is_writing : 1;
                unsigned int metadata_rd_err_t   : 1;
                unsigned int metadata_rid        : 4;
                unsigned int metadata_mem_mst    : 7;
                unsigned int reserve_0           : 1;
                unsigned int metadata_size       : 11;
                unsigned int reserve_1           : 3;
                unsigned int metadata_port_sel   : 2;
            } bits;
            unsigned int val;
        } metadata_ctrl;
        union { // name: metadata_mst, offset: 0x44
            struct {
                unsigned int metadata_mst : 32;
            } bits;
            unsigned int val;
        } metadata_mst;
        union { // name: fbc_timeout_ctrl, offset: 0x48
            struct {
                unsigned int fbcd_timeout_cnt     : 16;
                unsigned int fbcd_soft_rst_dis    : 1;
                unsigned int fbc_prefetch_en      : 1;
                unsigned int fbcd_dec_err_stop_en : 1;
                unsigned int reserve_0            : 12;
                unsigned int fbcd_timeout_en      : 1;
            } bits;
            unsigned int val;
        } fbc_timeout_ctrl;
    } regs;
    unsigned int data[19];
} sys_ctrl_rk3538_u;

// 0x00000100
typedef union sys0_ctrl_rk3538 {
    struct {
        union { // name: sys_axi0_ctrl_imd, offset: 0x0
            struct {
                unsigned int axi0_dma_stop            : 1;
                unsigned int axi0_outstanding_en      : 1;
                unsigned int reserve_0                : 2;
                unsigned int axi0_outstanding_num     : 6;
                unsigned int reserve_1                : 2;
                unsigned int axi0_cluster_priority_en : 1;
                unsigned int axi0_esmart_priority_en  : 1;
                unsigned int reserve_2                : 18;
            } bits;
            unsigned int val;
        } sys_axi0_ctrl_imd;
        union { // name: sys_axi0_hurry_ctrl_imd, offset: 0x4
            struct {
                unsigned int axi0_hurry_w_en       : 1;
                unsigned int axi0_hurry_w_value    : 2;
                unsigned int axi0_hurry_w_mode     : 2;
                unsigned int reserve_0             : 3;
                unsigned int axi0_hurry_en         : 1;
                unsigned int axi0_hurry_value      : 2;
                unsigned int axi0_hurry_threshold  : 1;
                unsigned int axi0_qos_en           : 1;
                unsigned int axi0_qos_value        : 2;
                unsigned int reserve_1             : 9;
                unsigned int axi0_port0_urgency_en : 1;
                unsigned int reserve_2             : 7;
            } bits;
            unsigned int val;
        } sys_axi0_hurry_ctrl_imd;
        union { // name: sys_axi0_mmu_ctrl, offset: 0x8
            struct {
                unsigned int mmu_bypass_en     : 1;
                unsigned int rkmmu_en          : 1;
                unsigned int rkmmu_soft_rst_en : 1;
                unsigned int reserve_0         : 1;
                unsigned int mmu_bypass_id     : 5;
                unsigned int reserve_1         : 1;
                unsigned int mmu_regdone_sel   : 2;
                unsigned int mmu_resetn_en     : 1;
                unsigned int reserve_2         : 1;
                unsigned int mmu_resetn_mode   : 2;
                unsigned int write_mask        : 16;
            } bits;
            unsigned int val;
        } sys_axi0_mmu_ctrl;
        union { // name: sys_axi0_status, offset: 0xc
            struct {
                unsigned int mmu_idle          : 1;
                unsigned int dma_stop          : 1;
                unsigned int reserve_0         : 2;
                unsigned int mmu_raddr_err_num : 4;
                unsigned int reserve_1         : 24;
            } bits;
            unsigned int val;
        } sys_axi0_status;
        union { // name: sys_axi0_mmu_ctrl1, offset: 0x10
            struct {
                unsigned int mmu_fixed_bypass_rid0    : 5;
                unsigned int reserve_0                : 2;
                unsigned int mmu_fixed_bypass_rid0_en : 1;
                unsigned int mmu_fixed_bypass_rid1    : 5;
                unsigned int reserve_1                : 2;
                unsigned int mmu_fixed_bypass_rid1_en : 1;
                unsigned int write_mask               : 16;
            } bits;
            unsigned int val;
        } sys_axi0_mmu_ctrl1;
        struct {
            unsigned int reserve_data[27];
        } reserve_reg_20_128;
        union { // name: sys0_intr_en, offset: 0x80
            struct {
                unsigned int reserve_0           : 1;
                unsigned int intr_en_bus0_error  : 1;
                unsigned int intr_en_dma0_finish : 1;
                unsigned int reserve_1           : 4;
                unsigned int intr_en_mmu         : 1;
                unsigned int reserve_2           : 8;
                unsigned int write_mask          : 16;
            } bits;
            unsigned int val;
        } sys0_intr_en;
        union { // name: sys0_intr_clr, offset: 0x84
            struct {
                unsigned int reserve_0           : 1;
                unsigned int intr_clr_bus_error  : 1;
                unsigned int intr_clr_dma_finish : 1;
                unsigned int reserve_1           : 4;
                unsigned int intr_clr_mmu        : 1;
                unsigned int reserve_2           : 8;
                unsigned int write_mask          : 16;
            } bits;
            unsigned int val;
        } sys0_intr_clr;
        union { // name: sys0_intr_status, offset: 0x88
            struct {
                unsigned int reserve_0              : 1;
                unsigned int intr_status_bus_error  : 1;
                unsigned int intr_status_dma_finish : 1;
                unsigned int reserve_1              : 4;
                unsigned int intr_status_mmu        : 1;
                unsigned int reserve_2              : 24;
            } bits;
            unsigned int val;
        } sys0_intr_status;
        union { // name: sys0_intr_raw_status, offset: 0x8c
            struct {
                unsigned int reserve_0                  : 1;
                unsigned int intr_raw_status_bus_error  : 1;
                unsigned int intr_raw_status_dma_finish : 1;
                unsigned int reserve_1                  : 4;
                unsigned int intr_raw_status_mmu0       : 1;
                unsigned int reserve_2                  : 24;
            } bits;
            unsigned int val;
        } sys0_intr_raw_status;
        union { // name: fbcd_intr_en0, offset: 0x90
            struct {
                unsigned int intr_en_axi0_pld_raddr_err    : 1;
                unsigned int intr_en_axi0_pld_overflow_err : 1;
                unsigned int reserve_0                     : 1;
                unsigned int intr_en_axi0_buff_ctrl_err    : 1;
                unsigned int intr_en_axi0_pld_dec_err      : 1;
                unsigned int intr_en_axi0_hdr0_ctrl_err    : 1;
                unsigned int intr_en_axi0_hdr1_ctrl_err    : 1;
                unsigned int intr_en_axi0_hdr2_ctrl_err    : 1;
                unsigned int intr_en_axi0_hdr3_ctrl_err    : 1;
                unsigned int reserve_1                     : 23;
            } bits;
            unsigned int val;
        } fbcd_intr_en0;
        union { // name: fbcd_intr_clr0, offset: 0x94
            struct {
                unsigned int intr_clr_axi0_pld_raddr_err    : 1;
                unsigned int intr_clr_axi0_pld_overflow_err : 1;
                unsigned int intr_clr_axi0_pld_dec_err      : 1;
                unsigned int intr_clr_axi0_buff_ctrl_err    : 1;
                unsigned int intr_clr_axi0_hdr0_ctrl_err    : 1;
                unsigned int intr_clr_axi0_hdr1_ctrl_err    : 1;
                unsigned int intr_clr_axi0_hdr2_ctrl_err    : 1;
                unsigned int intr_clr_axi0_hdr3_ctrl_err    : 1;
                unsigned int reserve_0                      : 24;
            } bits;
            unsigned int val;
        } fbcd_intr_clr0;
        union { // name: fbcd_intr_status0, offset: 0x98
            struct {
                unsigned int intr_status_axi0_pld_raddr_err    : 1;
                unsigned int intr_status_axi0_pld_overflow_err : 1;
                unsigned int intr_status_axi0_pld_dec_err      : 1;
                unsigned int intr_status_axi0_buff_ctrl_err    : 1;
                unsigned int intr_status_axi0_hdr0_ctrl_err    : 1;
                unsigned int intr_status_axi0_hdr1_ctrl_err    : 1;
                unsigned int intr_status_axi0_hdr2_ctrl_err    : 1;
                unsigned int intr_status_axi0_hdr3_ctrl_err    : 1;
                unsigned int reserve_0                         : 24;
            } bits;
            unsigned int val;
        } fbcd_intr_status0;
        union { // name: fbcd_intr_raw_status0, offset: 0x9c
            struct {
                unsigned int intr_raw_status_axi0_pld_raddr_err    : 1;
                unsigned int intr_raw_status_axi0_pld_overflow_err : 1;
                unsigned int intr_raw_status_axi0_pld_dec_err      : 1;
                unsigned int intr_raw_status_axi0_buff_ctrl_err    : 1;
                unsigned int intr_raw_status_axi0_hdr0_ctrl_err    : 1;
                unsigned int intr_raw_status_axi0_hdr1_ctrl_err    : 1;
                unsigned int intr_raw_status_axi0_hdr2_ctrl_err    : 1;
                unsigned int intr_raw_status_axi0_hdr3_ctrl_err    : 1;
                unsigned int reserve_0                             : 24;
            } bits;
            unsigned int val;
        } fbcd_intr_raw_status0;
    } regs;
    unsigned int data[40];
} sys0_ctrl_rk3538_u;

// 0x00000300
typedef union inface_ctrl_rk3538 {
    struct {
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_0_4;
        union { // name: hdmi0_inface_ctrl, offset: 0x4
            struct {
                unsigned int hdmi_out_en        : 1;
                unsigned int hdmi_clk_gating_en : 1;
                unsigned int hdmi_port_sel      : 2;
                unsigned int hdmi_hsync_pol     : 1;
                unsigned int hdmi_vsync_pol     : 1;
                unsigned int reserve_0          : 2;
                unsigned int hdmi_split_en      : 1;
                unsigned int hdmi_data1_sel     : 1;
                unsigned int reserve_1          : 2;
                unsigned int hdmi_r2y_en        : 1;
                unsigned int reserve_2          : 1;
                unsigned int hdmi_r2y_mode      : 2;
                unsigned int hdmi_yc_swap       : 1;
                unsigned int hdmi_uv_swap       : 1;
                unsigned int reserve_3          : 2;
                unsigned int hdmi_pix_clk_sel   : 1;
                unsigned int hdmi_dclk_sel      : 1;
                unsigned int reserve_4          : 9;
                unsigned int regdone_imd_en     : 1;
            } bits;
            unsigned int val;
        } hdmi0_inface_ctrl;
        struct {
            unsigned int reserve_data[3];
        } reserve_reg_8_20;
        union { // name: rgb_inface_ctrl, offset: 0x14
            struct {
                unsigned int rgb_out_en     : 1;
                unsigned int reserve_0      : 1;
                unsigned int rgb_port_sel   : 2;
                unsigned int rgb_hsync_pol  : 1;
                unsigned int rgb_vsync_pol  : 1;
                unsigned int rgb_den_pol    : 1;
                unsigned int reserve_1      : 1;
                unsigned int rgb_split_en   : 1;
                unsigned int rgb_data1_sel  : 1;
                unsigned int reserve_2      : 2;
                unsigned int bt656_out_en   : 1;
                unsigned int bt656_uv_swap  : 1;
                unsigned int bt656_yc_swap  : 1;
                unsigned int reserve_3      : 6;
                unsigned int rgb_dclk_sel   : 1;
                unsigned int reserve_4      : 9;
                unsigned int regdone_imd_en : 1;
            } bits;
            unsigned int val;
        } rgb_inface_ctrl;
        struct {
            unsigned int reserve_data[18];
        } reserve_reg_24_96;
        union { // name: post_yavg_ctrl, offset: 0x60
            struct {
                unsigned int yavg_en          : 1;
                unsigned int yavg_rst_en      : 1;
                unsigned int yavg_yuv_mode_en : 1;
                unsigned int reserve_0        : 1;
                unsigned int yavg_port_sel    : 2;
                unsigned int reserve_1        : 25;
                unsigned int regdone_imd_en   : 1;
            } bits;
            unsigned int val;
        } post_yavg_ctrl;
        union { // name: post_yavg_div_width, offset: 0x64
            struct {
                unsigned int yavg_1_div_width : 20;
                unsigned int reserve_0        : 12;
            } bits;
            unsigned int val;
        } post_yavg_div_width;
        union { // name: post_yavg_div_height, offset: 0x68
            struct {
                unsigned int yavg_1_div_height : 20;
                unsigned int reserve_0         : 12;
            } bits;
            unsigned int val;
        } post_yavg_div_height;
        union { // name: post_yavg_status, offset: 0x6c
            struct {
                unsigned int yavg_frame_out : 8;
                unsigned int reserve_0      : 24;
            } bits;
            unsigned int val;
        } post_yavg_status;
    } regs;
    unsigned int data[28];
} inface_ctrl_rk3538_u;

// 0x00000500
typedef union secure_ctrl_rk3538 {
    struct {
        union { // name: sec_inface_ctrl, offset: 0x0
            struct {
                unsigned int reserve_0          : 2;
                unsigned int sec_hdmi0_port_sel : 2;
                unsigned int reserve_1          : 6;
                unsigned int sec_cvbs_port_sel  : 2;
                unsigned int reserve_2          : 20;
            } bits;
            unsigned int val;
        } sec_inface_ctrl;
        union { // name: sec_drm_ctrl, offset: 0x4
            struct {
                unsigned int sec_drm_en            : 1;
                unsigned int reserve_0             : 3;
                unsigned int sec_wb_dis            : 1;
                unsigned int sec_rid_lock_en       : 1;
                unsigned int reserve_1             : 2;
                unsigned int sec_cluster0_en       : 1;
                unsigned int reserve_2             : 3;
                unsigned int sec_esmart0_en        : 1;
                unsigned int sec_esmart1_en        : 1;
                unsigned int sec_esmart2_en        : 1;
                unsigned int reserve_3             : 1;
                unsigned int sec_axi0_rid0_prot_en : 1;
                unsigned int sec_axi0_rid1_prot_en : 1;
                unsigned int sec_axi0_rid2_prot_en : 1;
                unsigned int sec_axi0_rid3_prot_en : 1;
                unsigned int sec_axi1_rid0_prot_en : 1;
                unsigned int sec_axi1_rid1_prot_en : 1;
                unsigned int sec_axi1_rid2_prot_en : 1;
                unsigned int sec_axi1_rid3_prot_en : 1;
                unsigned int reserve_4             : 8;
            } bits;
            unsigned int val;
        } sec_drm_ctrl;
        union { // name: sec_drm_port_sel, offset: 0x8
            struct {
                unsigned int drm_cluster0_port_sel : 2;
                unsigned int reserve_0             : 14;
                unsigned int drm_esmart0_port_sel  : 2;
                unsigned int reserve_1             : 2;
                unsigned int drm_esmart1_port_sel  : 2;
                unsigned int reserve_2             : 2;
                unsigned int drm_esmart2_port_sel  : 2;
                unsigned int reserve_3             : 6;
            } bits;
            unsigned int val;
        } sec_drm_port_sel;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_12_16;
        union { // name: sec_port0_layer_sel, offset: 0x10
            struct {
                unsigned int drm_layer0_sel    : 3;
                unsigned int drm_layer0_sel_en : 1;
                unsigned int drm_layer1_sel    : 3;
                unsigned int drm_layer1_sel_en : 1;
                unsigned int drm_layer2_sel    : 3;
                unsigned int drm_layer2_sel_en : 1;
                unsigned int drm_layer3_sel    : 3;
                unsigned int drm_layer3_sel_en : 1;
                unsigned int reserve_0         : 16;
            } bits;
            unsigned int val;
        } sec_port0_layer_sel;
        struct {
            unsigned int reserve_data[3];
        } reserve_reg_20_32;
        union { // name: sec_axi_rid_prot, offset: 0x20
            struct {
                unsigned int sec_axi0_rid0_prot : 4;
                unsigned int sec_axi0_rid1_prot : 4;
                unsigned int sec_axi0_rid2_prot : 4;
                unsigned int sec_axi0_rid3_prot : 4;
                unsigned int sec_axi1_rid0_prot : 4;
                unsigned int sec_axi1_rid1_prot : 4;
                unsigned int sec_axi1_rid2_prot : 4;
                unsigned int sec_axi1_rid3_prot : 4;
            } bits;
            unsigned int val;
        } sec_axi_rid_prot;
        struct {
            unsigned int reserve_data[3];
        } reserve_reg_36_48;
        union { // name: sys_otp_mirr_ctrl_imd, offset: 0x30
            struct {
                unsigned int dis_otp_fuction : 1;
                unsigned int reserve_0       : 31;
            } bits;
            unsigned int val;
        } sys_otp_mirr_ctrl_imd;
    } regs;
    unsigned int data[13];
} secure_ctrl_rk3538_u;

// 0x00000600
typedef union overlay_port0_rk3538 {
    struct {
        union { // name: overlay_ctrl, offset: 0x0
            struct {
                unsigned int overlay_mode          : 1;
                unsigned int overlay_yuv_full_mode : 1;
                unsigned int reserve_0             : 2;
                unsigned int hdr10_path_en         : 1;
                unsigned int sdr2hdr_path_en       : 1;
                unsigned int reserve_1             : 10;
                unsigned int port_extra_en         : 1;
                unsigned int cgc2hdr_en            : 1;
                unsigned int cgc2hdr_layer_sel     : 1;
                unsigned int hdr10_layer_sel       : 1;
                unsigned int reserve_2             : 12;
            } bits;
            unsigned int val;
        } overlay_ctrl;
        union { // name: layer_sel, offset: 0x4
            struct {
                unsigned int layer0_sel : 4;
                unsigned int layer1_sel : 4;
                unsigned int layer2_sel : 4;
                unsigned int layer3_sel : 4;
                unsigned int reserve_0  : 16;
            } bits;
            unsigned int val;
        } layer_sel;
        struct {
            unsigned int reserve_data[6];
        } reserve_reg_8_32;
        union { // name: mix0_src_color_ctrl, offset: 0x20
            struct {
                unsigned int src_color_mode0     : 1;
                unsigned int src_alpha_mode0     : 1;
                unsigned int src_blend_mode0     : 2;
                unsigned int src_alpha_cal_mode0 : 1;
                unsigned int src_factor_mode0    : 3;
                unsigned int alpha_en            : 1;
                unsigned int src_dst_swap        : 1;
                unsigned int reserve_0           : 6;
                unsigned int src_global_alpha0   : 8;
                unsigned int reserve_1           : 8;
            } bits;
            unsigned int val;
        } mix0_src_color_ctrl;
        union { // name: mix0_dst_color_ctrl, offset: 0x24
            struct {
                unsigned int dst_color_mode0     : 1;
                unsigned int dst_alpha_mode0     : 1;
                unsigned int dst_blend_mode0     : 2;
                unsigned int dst_alpha_cal_mode0 : 1;
                unsigned int dst_factor_mode0    : 3;
                unsigned int reserve_0           : 8;
                unsigned int dst_global_alpha0   : 8;
                unsigned int reserve_1           : 8;
            } bits;
            unsigned int val;
        } mix0_dst_color_ctrl;
        union { // name: mix0_src_alpha_ctrl, offset: 0x28
            struct {
                unsigned int reserve_0           : 1;
                unsigned int src_alpha_mode1     : 1;
                unsigned int src_blend_mode1     : 2;
                unsigned int src_alpha_cal_mode1 : 1;
                unsigned int src_factor_mode1    : 3;
                unsigned int reserve_1           : 24;
            } bits;
            unsigned int val;
        } mix0_src_alpha_ctrl;
        union { // name: mix0_dst_alpha_ctrl, offset: 0x2c
            struct {
                unsigned int reserve_0           : 1;
                unsigned int dst_alpha_mode1     : 1;
                unsigned int dst_blend_mode1     : 2;
                unsigned int dst_alpha_cal_mode1 : 1;
                unsigned int dst_factor_mode1    : 3;
                unsigned int reserve_1           : 24;
            } bits;
            unsigned int val;
        } mix0_dst_alpha_ctrl;
        union { // name: mix1_src_color_ctrl, offset: 0x30
            struct {
                unsigned int src_color_mode0     : 1;
                unsigned int src_alpha_mode0     : 1;
                unsigned int src_blend_mode0     : 2;
                unsigned int src_alpha_cal_mode0 : 1;
                unsigned int src_factor_mode0    : 3;
                unsigned int alpha_en            : 1;
                unsigned int src_dst_swap        : 1;
                unsigned int reserve_0           : 6;
                unsigned int src_global_alpha0   : 8;
                unsigned int reserve_1           : 8;
            } bits;
            unsigned int val;
        } mix1_src_color_ctrl;
        union { // name: mix1_dst_color_ctrl, offset: 0x34
            struct {
                unsigned int dst_color_mode0     : 1;
                unsigned int dst_alpha_mode0     : 1;
                unsigned int dst_blend_mode0     : 2;
                unsigned int dst_alpha_cal_mode0 : 1;
                unsigned int dst_factor_mode0    : 3;
                unsigned int reserve_0           : 8;
                unsigned int dst_global_alpha0   : 8;
                unsigned int reserve_1           : 8;
            } bits;
            unsigned int val;
        } mix1_dst_color_ctrl;
        union { // name: mix1_src_alpha_ctrl, offset: 0x38
            struct {
                unsigned int reserve_0           : 1;
                unsigned int src_alpha_mode1     : 1;
                unsigned int src_blend_mode1     : 2;
                unsigned int src_alpha_cal_mode1 : 1;
                unsigned int src_factor_mode1    : 3;
                unsigned int reserve_1           : 24;
            } bits;
            unsigned int val;
        } mix1_src_alpha_ctrl;
        union { // name: mix1_dst_alpha_ctrl, offset: 0x3c
            struct {
                unsigned int reserve_0           : 1;
                unsigned int dst_alpha_mode1     : 1;
                unsigned int dst_blend_mode1     : 2;
                unsigned int dst_alpha_cal_mode1 : 1;
                unsigned int dst_factor_mode1    : 3;
                unsigned int reserve_1           : 24;
            } bits;
            unsigned int val;
        } mix1_dst_alpha_ctrl;
        union { // name: mix2_src_color_ctrl, offset: 0x40
            struct {
                unsigned int src_color_mode0     : 1;
                unsigned int src_alpha_mode0     : 1;
                unsigned int src_blend_mode0     : 2;
                unsigned int src_alpha_cal_mode0 : 1;
                unsigned int src_factor_mode0    : 3;
                unsigned int alpha_en            : 1;
                unsigned int src_dst_swap        : 1;
                unsigned int reserve_0           : 6;
                unsigned int src_global_alpha0   : 8;
                unsigned int reserve_1           : 8;
            } bits;
            unsigned int val;
        } mix2_src_color_ctrl;
        union { // name: mix2_dst_color_ctrl, offset: 0x44
            struct {
                unsigned int dst_color_mode0     : 1;
                unsigned int dst_alpha_mode0     : 1;
                unsigned int dst_blend_mode0     : 2;
                unsigned int dst_alpha_cal_mode0 : 1;
                unsigned int dst_factor_mode0    : 3;
                unsigned int reserve_0           : 8;
                unsigned int dst_global_alpha0   : 8;
                unsigned int reserve_1           : 8;
            } bits;
            unsigned int val;
        } mix2_dst_color_ctrl;
        union { // name: mix2_src_alpha_ctrl, offset: 0x48
            struct {
                unsigned int reserve_0           : 1;
                unsigned int src_alpha_mode1     : 1;
                unsigned int src_blend_mode1     : 2;
                unsigned int src_alpha_cal_mode1 : 1;
                unsigned int src_factor_mode1    : 3;
                unsigned int reserve_1           : 24;
            } bits;
            unsigned int val;
        } mix2_src_alpha_ctrl;
        union { // name: mix2_dst_alpha_ctrl, offset: 0x4c
            struct {
                unsigned int reserve_0           : 1;
                unsigned int dst_alpha_mode1     : 1;
                unsigned int dst_blend_mode1     : 2;
                unsigned int dst_alpha_cal_mode1 : 1;
                unsigned int dst_factor_mode1    : 3;
                unsigned int reserve_1           : 24;
            } bits;
            unsigned int val;
        } mix2_dst_alpha_ctrl;
        struct {
            unsigned int reserve_data[8];
        } reserve_reg_80_112;
        union { // name: bg_mix_ctrl, offset: 0x70
            struct {
                unsigned int bg_alpha_en       : 1;
                unsigned int bg_alpha_mode     : 1;
                unsigned int bg_alpha_pre_mul  : 1;
                unsigned int bg_alpha_sat_mode : 1;
                unsigned int bg_line_end_mode  : 1;
                unsigned int reserve_0         : 3;
                unsigned int bg_global_alpha   : 8;
                unsigned int reserve_1         : 8;
                unsigned int bg_dly_num        : 8;
            } bits;
            unsigned int val;
        } bg_mix_ctrl;
        struct {
            unsigned int reserve_data[3];
        } reserve_reg_116_128;
        union { // name: cur_src_color_ctrl, offset: 0x80
            struct {
                unsigned int src_color_mode0     : 1;
                unsigned int src_alpha_mode0     : 1;
                unsigned int src_blend_mode0     : 2;
                unsigned int src_alpha_cal_mode0 : 1;
                unsigned int src_factor_mode0    : 3;
                unsigned int alpha_en            : 1;
                unsigned int src_dst_swap        : 1;
                unsigned int reserve_0           : 6;
                unsigned int src_global_alpha0   : 8;
                unsigned int reserve_1           : 8;
            } bits;
            unsigned int val;
        } cur_src_color_ctrl;
        union { // name: cur_dst_color_ctrl, offset: 0x84
            struct {
                unsigned int dst_color_mode0     : 1;
                unsigned int dst_alpha_mode0     : 1;
                unsigned int dst_blend_mode0     : 2;
                unsigned int dst_alpha_cal_mode0 : 1;
                unsigned int dst_factor_mode0    : 3;
                unsigned int reserve_0           : 8;
                unsigned int dst_global_alpha0   : 8;
                unsigned int reserve_1           : 8;
            } bits;
            unsigned int val;
        } cur_dst_color_ctrl;
        union { // name: cur_src_alpha_ctrl, offset: 0x88
            struct {
                unsigned int reserve_0           : 1;
                unsigned int src_alpha_mode1     : 1;
                unsigned int src_blend_mode1     : 2;
                unsigned int src_alpha_cal_mode1 : 1;
                unsigned int src_factor_mode1    : 3;
                unsigned int reserve_1           : 24;
            } bits;
            unsigned int val;
        } cur_src_alpha_ctrl;
        union { // name: cur_dst_alpha_ctrl, offset: 0x8c
            struct {
                unsigned int reserve_0           : 1;
                unsigned int dst_alpha_mode1     : 1;
                unsigned int dst_blend_mode1     : 2;
                unsigned int dst_alpha_cal_mode1 : 1;
                unsigned int dst_factor_mode1    : 3;
                unsigned int reserve_1           : 24;
            } bits;
            unsigned int val;
        } cur_dst_alpha_ctrl;
        struct {
            unsigned int reserve_data[4];
        } reserve_reg_144_160;
        union { // name: hdr_src_color_ctrl, offset: 0xa0
            struct {
                unsigned int src_color_mode0     : 1;
                unsigned int src_alpha_mode0     : 1;
                unsigned int src_blend_mode0     : 2;
                unsigned int src_alpha_cal_mode0 : 1;
                unsigned int src_factor_mode0    : 3;
                unsigned int alpha_en            : 1;
                unsigned int src_dst_swap        : 1;
                unsigned int reserve_0           : 6;
                unsigned int src_global_alpha0   : 8;
                unsigned int reserve_1           : 8;
            } bits;
            unsigned int val;
        } hdr_src_color_ctrl;
        union { // name: hdr_dst_color_ctrl, offset: 0xa4
            struct {
                unsigned int dst_color_mode0     : 1;
                unsigned int dst_alpha_mode0     : 1;
                unsigned int dst_blend_mode0     : 2;
                unsigned int dst_alpha_cal_mode0 : 1;
                unsigned int dst_factor_mode0    : 3;
                unsigned int reserve_0           : 8;
                unsigned int dst_global_alpha0   : 8;
                unsigned int reserve_1           : 8;
            } bits;
            unsigned int val;
        } hdr_dst_color_ctrl;
        union { // name: hdr_src_alpha_ctrl, offset: 0xa8
            struct {
                unsigned int reserve_0           : 1;
                unsigned int src_alpha_mode1     : 1;
                unsigned int src_blend_mode1     : 2;
                unsigned int src_alpha_cal_mode1 : 1;
                unsigned int src_factor_mode1    : 3;
                unsigned int reserve_1           : 24;
            } bits;
            unsigned int val;
        } hdr_src_alpha_ctrl;
        union { // name: hdr_dst_alpha_ctrl, offset: 0xac
            struct {
                unsigned int reserve_0           : 1;
                unsigned int dst_alpha_mode1     : 1;
                unsigned int dst_blend_mode1     : 2;
                unsigned int dst_alpha_cal_mode1 : 1;
                unsigned int dst_factor_mode1    : 3;
                unsigned int reserve_1           : 24;
            } bits;
            unsigned int val;
        } hdr_dst_alpha_ctrl;
        union { // name: cgc_src_color_ctrl, offset: 0xb0
            struct {
                unsigned int src_color_mode0     : 1;
                unsigned int src_alpha_mode0     : 1;
                unsigned int src_blend_mode0     : 2;
                unsigned int src_alpha_cal_mode0 : 1;
                unsigned int src_factor_mode0    : 3;
                unsigned int alpha_en            : 1;
                unsigned int src_dst_swap        : 1;
                unsigned int reserve_0           : 6;
                unsigned int src_global_alpha0   : 8;
                unsigned int reserve_1           : 8;
            } bits;
            unsigned int val;
        } cgc_src_color_ctrl;
        union { // name: cgc_dst_color_ctrl, offset: 0xb4
            struct {
                unsigned int dst_color_mode0     : 1;
                unsigned int dst_alpha_mode0     : 1;
                unsigned int dst_blend_mode0     : 2;
                unsigned int dst_alpha_cal_mode0 : 1;
                unsigned int dst_factor_mode0    : 3;
                unsigned int reserve_0           : 8;
                unsigned int dst_global_alpha0   : 8;
                unsigned int reserve_1           : 8;
            } bits;
            unsigned int val;
        } cgc_dst_color_ctrl;
        union { // name: cgc_src_alpha_ctrl, offset: 0xb8
            struct {
                unsigned int reserve_0           : 1;
                unsigned int src_alpha_mode1     : 1;
                unsigned int src_blend_mode1     : 2;
                unsigned int src_alpha_cal_mode1 : 1;
                unsigned int src_factor_mode1    : 3;
                unsigned int reserve_1           : 24;
            } bits;
            unsigned int val;
        } cgc_src_alpha_ctrl;
        union { // name: cgc_dst_alpha_ctrl, offset: 0xbc
            struct {
                unsigned int reserve_0           : 1;
                unsigned int dst_alpha_mode1     : 1;
                unsigned int dst_blend_mode1     : 2;
                unsigned int dst_alpha_cal_mode1 : 1;
                unsigned int dst_factor_mode1    : 3;
                unsigned int reserve_1           : 24;
            } bits;
            unsigned int val;
        } cgc_dst_alpha_ctrl;
    } regs;
    unsigned int data[48];
} overlay_port0_rk3538_u;

// 0x00000C00
typedef union post0_ctrl_rk3538 {
    struct {
        union { // name: post_dsp_ctrl, offset: 0x0
            struct {
                unsigned int dsp_out_mode          : 4;
                unsigned int reserve_0             : 1;
                unsigned int dsp_p2i_en            : 1;
                unsigned int dsp_filed_pol         : 1;
                unsigned int dsp_interlace         : 1;
                unsigned int dsp_bg_swap           : 1;
                unsigned int dsp_rb_swap           : 1;
                unsigned int dsp_rg_swap           : 1;
                unsigned int dsp_delta_swap        : 1;
                unsigned int dsp_dummy_swap        : 1;
                unsigned int dsp_x_mir_en          : 1;
                unsigned int reserve_1             : 1;
                unsigned int dsp_out_rgb_yuv       : 1;
                unsigned int pre_dither_down_en    : 1;
                unsigned int dither_down_en        : 1;
                unsigned int dither_down_sel       : 2;
                unsigned int dither_down_mode      : 1;
                unsigned int reserve_2             : 2;
                unsigned int post_lb_mode          : 1;
                unsigned int dsp_blank_en          : 1;
                unsigned int reserve_3             : 1;
                unsigned int dsp_out_zero          : 1;
                unsigned int dsp_black_en          : 1;
                unsigned int dsp_lut_en            : 1;
                unsigned int reserve_4             : 1;
                unsigned int vop_fp_standby_en_imd : 1;
                unsigned int vop_standby_en_imd    : 1;
            } bits;
            unsigned int val;
        } post_dsp_ctrl;
        union { // name: post_mipi_ctrl, offset: 0x4
            struct {
                unsigned int reserve_0                : 20;
                unsigned int doub_channel_en          : 1;
                unsigned int doub_channel_swap        : 1;
                unsigned int reserve_1                : 2;
                unsigned int doub_channel_overlap_num : 4;
                unsigned int edpi_te_en               : 1;
                unsigned int edpi_te_mode             : 1;
                unsigned int edpi_wms_hold_en         : 1;
                unsigned int edpi_wms_fs              : 1;
            } bits;
            unsigned int val;
        } post_mipi_ctrl;
        union { // name: post_color_ctrl, offset: 0x8
            struct {
                unsigned int color_bar_en     : 1;
                unsigned int color_bar_mode   : 3;
                unsigned int io_vsync_sel     : 2;
                unsigned int reserve_0        : 1;
                unsigned int vfp_dma_stop_en  : 1;
                unsigned int post_urgency_en  : 1;
                unsigned int post_autocs_en   : 1;
                unsigned int post_full_sel    : 1;
                unsigned int reserve_1        : 1;
                unsigned int post_full_num    : 4;
                unsigned int post_urgency_thl : 4;
                unsigned int post_urgency_thh : 4;
                unsigned int post_autocs_thl  : 4;
                unsigned int post_autocs_thh  : 4;
            } bits;
            unsigned int val;
        } post_color_ctrl;
        union { // name: post_core_clk, offset: 0xc
            struct {
                unsigned int dclk_core_sel : 1;
                unsigned int reserve_0     : 1;
                unsigned int dclk_out_sel  : 1;
                unsigned int reserve_1     : 29;
            } bits;
            unsigned int val;
        } post_core_clk;
        struct {
            unsigned int reserve_data[5];
        } reserve_reg_16_36;
        union { // name: post_crc_check_value, offset: 0x24
            struct {
                unsigned int crc_check_value : 32;
            } bits;
            unsigned int val;
        } post_crc_check_value;
        union { // name: post_crc_out, offset: 0x28
            struct {
                unsigned int crc_data_out : 32;
            } bits;
            unsigned int val;
        } post_crc_out;
        union { // name: post_dsp_bg, offset: 0x2c
            struct {
                unsigned int dsp_bg_green  : 10;
                unsigned int dsp_bg_blue   : 10;
                unsigned int dsp_bg_red    : 10;
                unsigned int reserve_0     : 1;
                unsigned int bg_display_en : 1;
            } bits;
            unsigned int val;
        } post_dsp_bg;
        union { // name: post_pre_scan_htiming, offset: 0x30
            struct {
                unsigned int pre_scan_hblank  : 13;
                unsigned int reserve_0        : 3;
                unsigned int pre_scan_hactive : 13;
                unsigned int reserve_1        : 3;
            } bits;
            unsigned int val;
        } post_pre_scan_htiming;
        union { // name: post_dsp_hact_info, offset: 0x34
            struct {
                unsigned int dsp_hact_end_post : 13;
                unsigned int reserve_0         : 3;
                unsigned int dsp_hact_st_post  : 13;
                unsigned int reserve_1         : 3;
            } bits;
            unsigned int val;
        } post_dsp_hact_info;
        union { // name: post_dsp_vact_info, offset: 0x38
            struct {
                unsigned int dsp_vact_end_post : 13;
                unsigned int reserve_0         : 3;
                unsigned int dsp_vact_st_post  : 13;
                unsigned int reserve_1         : 3;
            } bits;
            unsigned int val;
        } post_dsp_vact_info;
        union { // name: post_scl_factor_yrgb, offset: 0x3c
            struct {
                unsigned int post_hs_factor : 16;
                unsigned int post_vs_factor : 16;
            } bits;
            unsigned int val;
        } post_scl_factor_yrgb;
        union { // name: post_scl_ctrl, offset: 0x40
            struct {
                unsigned int post_hor_sd_en         : 1;
                unsigned int post_ver_sd_en         : 1;
                unsigned int reserve_0              : 2;
                unsigned int post_vsd_dly_en        : 1;
                unsigned int post_empty_cheating_en : 1;
                unsigned int sharpness_cheating_en  : 1;
                unsigned int reserve_1              : 1;
                unsigned int crc_en                 : 1;
                unsigned int crc_check_en           : 1;
                unsigned int reserve_2              : 22;
            } bits;
            unsigned int val;
        } post_scl_ctrl;
        union { // name: post_dsp_vact_info_f1, offset: 0x44
            struct {
                unsigned int dsp_vact_end_post_f1 : 13;
                unsigned int reserve_0            : 3;
                unsigned int dsp_vact_st_post_f1  : 13;
                unsigned int reserve_1            : 3;
            } bits;
            unsigned int val;
        } post_dsp_vact_info_f1;
        union { // name: post_dsp_htotal_hs_end, offset: 0x48
            struct {
                unsigned int dsp_hs_end : 13;
                unsigned int reserve_0  : 3;
                unsigned int dsp_htotal : 13;
                unsigned int reserve_1  : 3;
            } bits;
            unsigned int val;
        } post_dsp_htotal_hs_end;
        union { // name: post_dsp_hact_st_end, offset: 0x4c
            struct {
                unsigned int dsp_hact_end : 13;
                unsigned int reserve_0    : 3;
                unsigned int dsp_hact_st  : 13;
                unsigned int reserve_1    : 3;
            } bits;
            unsigned int val;
        } post_dsp_hact_st_end;
        union { // name: post_dsp_vtotal_vs_end, offset: 0x50
            struct {
                unsigned int dsp_vs_end        : 13;
                unsigned int reserve_0         : 2;
                unsigned int sw_dsp_vtotal_imd : 1;
                unsigned int dsp_vtotal        : 13;
                unsigned int reserve_1         : 3;
            } bits;
            unsigned int val;
        } post_dsp_vtotal_vs_end;
        union { // name: post_dsp_vact_st_end, offset: 0x54
            struct {
                unsigned int dsp_vact_end : 13;
                unsigned int reserve_0    : 3;
                unsigned int dsp_vact_st  : 13;
                unsigned int reserve_1    : 3;
            } bits;
            unsigned int val;
        } post_dsp_vact_st_end;
        union { // name: post_dsp_vs_st_end_f1, offset: 0x58
            struct {
                unsigned int dsp_vs_end_f1 : 13;
                unsigned int reserve_0     : 3;
                unsigned int dsp_vs_st_f1  : 13;
                unsigned int reserve_1     : 3;
            } bits;
            unsigned int val;
        } post_dsp_vs_st_end_f1;
        union { // name: post_dsp_vact_st_end_f1, offset: 0x5c
            struct {
                unsigned int dsp_vact_end_f1 : 13;
                unsigned int reserve_0       : 3;
                unsigned int dsp_vact_st_f1  : 13;
                unsigned int reserve_1       : 3;
            } bits;
            unsigned int val;
        } post_dsp_vact_st_end_f1;
        struct {
            unsigned int reserve_data[4];
        } reserve_reg_96_112;
        union { // name: post_acm_r2y_ctrl, offset: 0x70
            struct {
                unsigned int reserve_0     : 1;
                unsigned int acm_r2y_en    : 1;
                unsigned int reserve_1     : 14;
                unsigned int acm_r2y_coe00 : 16;
            } bits;
            unsigned int val;
        } post_acm_r2y_ctrl;
        union { // name: post_acm_r2y_coe0102, offset: 0x74
            struct {
                unsigned int acm_r2y_coe01 : 16;
                unsigned int acm_r2y_coe02 : 16;
            } bits;
            unsigned int val;
        } post_acm_r2y_coe0102;
        union { // name: post_acm_r2y_coe1011, offset: 0x78
            struct {
                unsigned int acm_r2y_coe10 : 16;
                unsigned int acm_r2y_coe11 : 16;
            } bits;
            unsigned int val;
        } post_acm_r2y_coe1011;
        union { // name: post_acm_r2y_coe1220, offset: 0x7c
            struct {
                unsigned int acm_r2y_coe12 : 16;
                unsigned int acm_r2y_coe20 : 16;
            } bits;
            unsigned int val;
        } post_acm_r2y_coe1220;
        union { // name: post_acm_r2y_coe2122, offset: 0x80
            struct {
                unsigned int acm_r2y_coe21 : 16;
                unsigned int acm_r2y_coe22 : 16;
            } bits;
            unsigned int val;
        } post_acm_r2y_coe2122;
        union { // name: post_acm_r2y_offset0, offset: 0x84
            struct {
                unsigned int acm_r2y_offset0 : 32;
            } bits;
            unsigned int val;
        } post_acm_r2y_offset0;
        union { // name: post_acm_r2y_offset1, offset: 0x88
            struct {
                unsigned int acm_r2y_offset1 : 32;
            } bits;
            unsigned int val;
        } post_acm_r2y_offset1;
        union { // name: post_acm_r2y_offset2, offset: 0x8c
            struct {
                unsigned int acm_r2y_offset2 : 32;
            } bits;
            unsigned int val;
        } post_acm_r2y_offset2;
        union { // name: post_line_flag, offset: 0x90
            struct {
                unsigned int dsp_line_flag_num_0 : 13;
                unsigned int reserve_0           : 3;
                unsigned int dsp_line_flag_num_1 : 13;
                unsigned int reserve_1           : 3;
            } bits;
            unsigned int val;
        } post_line_flag;
        union { // name: post_mcu_bypass_addr, offset: 0x94
            struct {
                unsigned int mcu_bypass_addr : 32;
            } bits;
            unsigned int val;
        } post_mcu_bypass_addr;
        union { // name: post_mcu_ctrl, offset: 0x98
            struct {
                unsigned int mcu_pix_total : 6;
                unsigned int mcu_cs_pst    : 4;
                unsigned int mcu_cs_pend   : 6;
                unsigned int mcu_rw_pst    : 4;
                unsigned int mcu_rw_pend   : 6;
                unsigned int reserve_0     : 1;
                unsigned int mcu_hold_mode : 1;
                unsigned int mcu_frm_st    : 1;
                unsigned int mcu_rs        : 1;
                unsigned int mcu_bypass_en : 1;
                unsigned int mcu_type_en   : 1;
            } bits;
            unsigned int val;
        } post_mcu_ctrl;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_156_160;
        union { // name: post_dither_frc_0, offset: 0xa0
            struct {
                unsigned int sw_frc_dither_mode : 2;
                unsigned int sw_frc_rcr_pattern : 2;
                unsigned int sw_frc_gy_pattern  : 2;
                unsigned int sw_frc_bcb_pattern : 2;
                unsigned int reserve_0          : 24;
            } bits;
            unsigned int val;
        } post_dither_frc_0;
        union { // name: post_dither_frc_1, offset: 0xa4
            struct {
                unsigned int sw_frc_rcr_strength : 10;
                unsigned int reserve_0           : 6;
                unsigned int sw_frc_gy_strength  : 10;
                unsigned int reserve_1           : 6;
            } bits;
            unsigned int val;
        } post_dither_frc_1;
        union { // name: post_dither_frc_2, offset: 0xa8
            struct {
                unsigned int sw_frc_bcb_strength : 10;
                unsigned int reserve_0           : 6;
                unsigned int sw_range_sca        : 14;
                unsigned int reserve_1           : 2;
            } bits;
            unsigned int val;
        } post_dither_frc_2;
        struct {
            unsigned int reserve_data[5];
        } reserve_reg_172_192;
        union { // name: post_intr_en, offset: 0xc0
            struct {
                unsigned int intr_en_fs             : 1;
                unsigned int reserve_0              : 1;
                unsigned int intr_en_line_flag0     : 1;
                unsigned int intr_en_line_flag1     : 1;
                unsigned int intr_en_post_buf_empty : 1;
                unsigned int intr_en_fs_field       : 1;
                unsigned int intr_en_dsp_hold_valid : 1;
                unsigned int intr_en_vfp            : 1;
                unsigned int reserve_1              : 1;
                unsigned int intr_en_post_full      : 1;
                unsigned int intr_en_crc_error      : 1;
                unsigned int reserve_2              : 1;
                unsigned int intr_en_dolby_core1    : 1;
                unsigned int intr_en_dolby_core2    : 1;
                unsigned int intr_en_dolby_core3    : 1;
                unsigned int reserve_3              : 1;
                unsigned int write_mask             : 16;
            } bits;
            unsigned int val;
        } post_intr_en;
        union { // name: post_intr_clr, offset: 0xc4
            struct {
                unsigned int intr_clr_fs             : 1;
                unsigned int reserve_0               : 1;
                unsigned int intr_clr_line_flag0     : 1;
                unsigned int intr_clr_fs_new         : 1;
                unsigned int intr_clr_line_flag1     : 1;
                unsigned int intr_clr_post_buf_empty : 1;
                unsigned int intr_clr_fs_field       : 1;
                unsigned int intr_clr_dsp_hold_valid : 1;
                unsigned int intr_clr_vfp            : 1;
                unsigned int intr_clr_post_full      : 1;
                unsigned int intr_clr_crc_error      : 1;
                unsigned int reserve_1               : 5;
                unsigned int write_mask              : 16;
            } bits;
            unsigned int val;
        } post_intr_clr;
        union { // name: post_intr_status, offset: 0xc8
            struct {
                unsigned int intr_status_fs             : 1;
                unsigned int reserve_0                  : 1;
                unsigned int intr_status_line_flag0     : 1;
                unsigned int intr_status_line_flag1     : 1;
                unsigned int intr_status_post_buf_empty : 1;
                unsigned int intr_status_fs_field       : 1;
                unsigned int intr_status_dsp_hold_valid : 1;
                unsigned int intr_status_vfp            : 1;
                unsigned int reserve_1                  : 1;
                unsigned int intr_status_post_full      : 1;
                unsigned int intr_status_crc_error      : 1;
                unsigned int reserve_2                  : 21;
            } bits;
            unsigned int val;
        } post_intr_status;
        union { // name: post_intr_raw_status, offset: 0xcc
            struct {
                unsigned int intr_raw_status_fs             : 1;
                unsigned int reserve_0                      : 1;
                unsigned int intr_raw_status_line_flag0     : 1;
                unsigned int intr_raw_status_line_flag1     : 1;
                unsigned int intr_raw_status_post_buf_empty : 1;
                unsigned int intr_raw_status_fs_field       : 1;
                unsigned int intr_raw_status_dsp_hold_valid : 1;
                unsigned int intr_raw_status_vfp            : 1;
                unsigned int reserve_1                      : 1;
                unsigned int intr_raw_status_post_full      : 1;
                unsigned int intr_raw_status_crc_error      : 1;
                unsigned int reserve_2                      : 21;
            } bits;
            unsigned int val;
        } post_intr_raw_status;
        union { // name: post_acm_ctrl, offset: 0xd0
            struct {
                unsigned int acm_bypass_en : 1;
                unsigned int acm_y2r_en    : 1;
                unsigned int reserve_0     : 14;
                unsigned int acm_y2r_coe00 : 16;
            } bits;
            unsigned int val;
        } post_acm_ctrl;
        union { // name: post_acm_y2r_coe0102, offset: 0xd4
            struct {
                unsigned int acm_y2r_coe01 : 16;
                unsigned int acm_y2r_coe02 : 16;
            } bits;
            unsigned int val;
        } post_acm_y2r_coe0102;
        union { // name: post_acm_y2r_coe1011, offset: 0xd8
            struct {
                unsigned int acm_y2r_coe10 : 16;
                unsigned int acm_y2r_coe11 : 16;
            } bits;
            unsigned int val;
        } post_acm_y2r_coe1011;
        union { // name: post_acm_y2r_coe1220, offset: 0xdc
            struct {
                unsigned int acm_y2r_coe12 : 16;
                unsigned int acm_y2r_coe20 : 16;
            } bits;
            unsigned int val;
        } post_acm_y2r_coe1220;
        union { // name: post_acm_y2r_coe2122, offset: 0xe0
            struct {
                unsigned int acm_y2r_coe21 : 16;
                unsigned int acm_y2r_coe22 : 16;
            } bits;
            unsigned int val;
        } post_acm_y2r_coe2122;
        union { // name: post_acm_y2r_offset0, offset: 0xe4
            struct {
                unsigned int acm_y2r_offset0 : 32;
            } bits;
            unsigned int val;
        } post_acm_y2r_offset0;
        union { // name: post_acm_y2r_offset1, offset: 0xe8
            struct {
                unsigned int acm_y2r_offset1 : 32;
            } bits;
            unsigned int val;
        } post_acm_y2r_offset1;
        union { // name: post_acm_y2r_offset2, offset: 0xec
            struct {
                unsigned int acm_y2r_offset2 : 32;
            } bits;
            unsigned int val;
        } post_acm_y2r_offset2;
        union { // name: post_status, offset: 0xf0
            struct {
                unsigned int post_empty_dsp_vcnt     : 13;
                unsigned int reserve_0               : 1;
                unsigned int post_empty_dsp_vcnt_en  : 1;
                unsigned int post_empty_dsp_vctn_clr : 1;
                unsigned int dsp_vcnt                : 13;
                unsigned int reserve_1               : 3;
            } bits;
            unsigned int val;
        } post_status;
        union { // name: post_clk_cnt, offset: 0xf4
            struct {
                unsigned int calc_dclk_cnt : 15;
                unsigned int calc_clk_en   : 1;
                unsigned int calc_aclk_cnt : 16;
            } bits;
            unsigned int val;
        } post_clk_cnt;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_248_252;
        union { // name: post_cfg_done, offset: 0xfc
            struct {
                unsigned int reg_load_global0_en    : 1;
                unsigned int reserve_0              : 3;
                unsigned int dsp_vs_t_sel           : 1;
                unsigned int reserve_1              : 3;
                unsigned int interlace_frm_reg_done : 1;
                unsigned int reserve_2              : 23;
            } bits;
            unsigned int val;
        } post_cfg_done;
    } regs;
    unsigned int data[64];
} post0_ctrl_rk3538_u;

// 0x00001000
typedef union cluster0_rk3538 {
    struct {
        union { // name: win0_ctrl0, offset: 0x0
            struct {
                unsigned int win0_en            : 1;
                unsigned int win0_data_fmt      : 6;
                unsigned int win0_tile_mode0_en : 1;
                unsigned int win0_csc_y2r_en    : 1;
                unsigned int win0_csc_r2y_en    : 1;
                unsigned int reserve_0          : 4;
                unsigned int win0_rb_swap       : 1;
                unsigned int win0_alpha_swap    : 1;
                unsigned int win0_mid_swap      : 1;
                unsigned int win0_uv_swap       : 1;
                unsigned int win0_dither_up_en  : 1;
                unsigned int win0_yuv_clip      : 1;
                unsigned int reserve_1          : 1;
                unsigned int win0_y_mir         : 1;
                unsigned int reserve_2          : 10;
            } bits;
            unsigned int val;
        } win0_ctrl0;
        union { // name: win0_ctrl1, offset: 0x4
            struct {
                unsigned int win0_yrgb_axi_gather_en : 1;
                unsigned int win0_cbcr_axi_gather_en : 1;
                unsigned int reserve_0               : 2;
                unsigned int win0_yrgb_gather_num    : 4;
                unsigned int win0_cbcr_gather_num    : 4;
                unsigned int win0_yscl_mode          : 2;
                unsigned int win0_ysu_en             : 1;
                unsigned int win0_ysd_en             : 1;
                unsigned int reserve_1               : 2;
                unsigned int win0_vsd_avg2           : 1;
                unsigned int win0_vsd_avg4           : 1;
                unsigned int win0_xscl_mode          : 2;
                unsigned int win0_xsu_en             : 1;
                unsigned int win0_xsd_en             : 1;
                unsigned int win0_xgt_en             : 1;
                unsigned int win0_xgt_mode           : 2;
                unsigned int win0_xavg_en            : 1;
                unsigned int win0_yrgb_vsd_gt2       : 1;
                unsigned int win0_yrgb_vsd_gt4       : 1;
                unsigned int win0_cbcr_vsd_gt2       : 1;
                unsigned int win0_cbcr_vsd_gt4       : 1;
            } bits;
            unsigned int val;
        } win0_ctrl1;
        union { // name: win0_ctrl2, offset: 0x8
            struct {
                unsigned int win0_rid_yrgb         : 5;
                unsigned int win0_rid_cbr          : 5;
                unsigned int reserve_0             : 10;
                unsigned int win0_dma_burst_length : 2;
                unsigned int reserve_1             : 2;
                unsigned int win0_sresp_stop_en    : 1;
                unsigned int reserve_2             : 7;
            } bits;
            unsigned int val;
        } win0_ctrl2;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_12_16;
        union { // name: win0_yrgb_mst, offset: 0x10
            struct {
                unsigned int win0_yrgb_mst : 32;
            } bits;
            unsigned int val;
        } win0_yrgb_mst;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_20_24;
        union { // name: win0_vir, offset: 0x18
            struct {
                unsigned int win0_vir_stride : 16;
                unsigned int reserve_0       : 16;
            } bits;
            unsigned int val;
        } win0_vir;
        union { // name: win0_key_ctrl, offset: 0x1c
            struct {
                unsigned int win0_key_color : 30;
                unsigned int reserve_0      : 1;
                unsigned int win0_key_en    : 1;
            } bits;
            unsigned int val;
        } win0_key_ctrl;
        union { // name: win0_act_info, offset: 0x20
            struct {
                unsigned int win0_act_width  : 13;
                unsigned int reserve_0       : 3;
                unsigned int win0_act_height : 13;
                unsigned int reserve_1       : 3;
            } bits;
            unsigned int val;
        } win0_act_info;
        union { // name: win0_dsp_info, offset: 0x24
            struct {
                unsigned int win0_dsp_width  : 12;
                unsigned int reserve_0       : 4;
                unsigned int win0_dsp_height : 12;
                unsigned int reserve_1       : 4;
            } bits;
            unsigned int val;
        } win0_dsp_info;
        union { // name: win0_dsp_st, offset: 0x28
            struct {
                unsigned int win0_dsp_xst : 13;
                unsigned int reserve_0    : 3;
                unsigned int win0_dsp_yst : 13;
                unsigned int reserve_1    : 3;
            } bits;
            unsigned int val;
        } win0_dsp_st;
        union { // name: win0_dsp_bg, offset: 0x2c
            struct {
                unsigned int win0_dsp_bg_blue  : 10;
                unsigned int win0_dsp_bg_green : 10;
                unsigned int win0_dsp_bg_red   : 10;
                unsigned int reserve_0         : 1;
                unsigned int win0_bg_en        : 1;
            } bits;
            unsigned int val;
        } win0_dsp_bg;
        union { // name: win0_scl_factor_yrgb, offset: 0x30
            struct {
                unsigned int win0_hs_factor_yrgb : 16;
                unsigned int win0_vs_factor_yrgb : 16;
            } bits;
            unsigned int val;
        } win0_scl_factor_yrgb;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_52_56;
        union { // name: win0_scl_offset, offset: 0x38
            struct {
                unsigned int win0_hs_offset_yrgb : 8;
                unsigned int reserve_0           : 8;
                unsigned int win0_vs_offset_yrgb : 8;
                unsigned int reserve_1           : 8;
            } bits;
            unsigned int val;
        } win0_scl_offset;
        union { // name: win0_transformed_offset, offset: 0x3c
            struct {
                unsigned int transformed_xoffset : 5;
                unsigned int reserve_0           : 11;
                unsigned int transformed_yoffset : 4;
                unsigned int reserve_1           : 12;
            } bits;
            unsigned int val;
        } win0_transformed_offset;
        union { // name: win0_zme_ctrl, offset: 0x40
            struct {
                unsigned int reserve_0          : 3;
                unsigned int win0_zme_dering_en : 1;
                unsigned int reserve_1          : 27;
                unsigned int win0_zme_gating_en : 1;
            } bits;
            unsigned int val;
        } win0_zme_ctrl;
        union { // name: win0_zme_dering_para, offset: 0x44
            struct {
                unsigned int win0_dering_alpha : 5;
                unsigned int reserve_0         : 3;
                unsigned int win0_dering_beta  : 5;
                unsigned int reserve_1         : 3;
                unsigned int win0_dering_sen0  : 5;
                unsigned int reserve_2         : 3;
                unsigned int win0_dering_sen1  : 5;
                unsigned int reserve_3         : 3;
            } bits;
            unsigned int val;
        } win0_zme_dering_para;
        struct {
            unsigned int reserve_data[2];
        } reserve_reg_72_80;
        union { // name: win0_fbcd_output_ctrl, offset: 0x50
            struct {
                unsigned int reserve_0           : 4;
                unsigned int win0_fbcd_gating_en : 1;
                unsigned int reserve_1           : 27;
            } bits;
            unsigned int val;
        } win0_fbcd_output_ctrl;
        union { // name: win0_fbcd_mode, offset: 0x54
            struct {
                unsigned int reserve_0    : 2;
                unsigned int win0_xmir_en : 1;
                unsigned int win0_ymir_en : 1;
                unsigned int reserve_1    : 28;
            } bits;
            unsigned int val;
        } win0_fbcd_mode;
        union { // name: win0_fbcd_hdr_ptr, offset: 0x58
            struct {
                unsigned int win0_fbcd_hdr_ptr : 32;
            } bits;
            unsigned int val;
        } win0_fbcd_hdr_ptr;
        union { // name: win0_fbcd_vir_width, offset: 0x5c
            struct {
                unsigned int win0_fbcd_pic_vir_width : 16;
                unsigned int win0_fbcd_tail_num      : 16;
            } bits;
            unsigned int val;
        } win0_fbcd_vir_width;
        union { // name: win0_fbcd_size, offset: 0x60
            struct {
                unsigned int win0_fbcd_pic_width  : 16;
                unsigned int win0_fbcd_pic_height : 16;
            } bits;
            unsigned int val;
        } win0_fbcd_size;
        union { // name: win0_fbcd_pic_offset, offset: 0x64
            struct {
                unsigned int win0_fbcd_pic_xoffset : 16;
                unsigned int win0_fbcd_pic_yoffset : 16;
            } bits;
            unsigned int val;
        } win0_fbcd_pic_offset;
        union { // name: win0_fbcd_dis_offset, offset: 0x68
            struct {
                unsigned int win0_fbcd_dis_xoffset : 16;
                unsigned int win0_fbcd_dis_yoffset : 16;
            } bits;
            unsigned int val;
        } win0_fbcd_dis_offset;
        union { // name: win0_fbcd_ctrl, offset: 0x6c
            struct {
                unsigned int reserve_0                   : 2;
                unsigned int win0_fbcd_pixel_packing_fmt : 5;
                unsigned int win0_fbcd_half_block        : 1;
                unsigned int win0_fbcd_block_split       : 1;
                unsigned int win0_fbcd_rb_swap_en        : 1;
                unsigned int win0_fbcd_uv_swap_en        : 1;
                unsigned int win0_fbcd_alpha_swap_en     : 1;
                unsigned int win0_fbcd_bg_swap_en        : 1;
                unsigned int reserve_1                   : 3;
                unsigned int win0_fbcd_pld_offset_en     : 1;
                unsigned int win0_fbcd_pld_range_en      : 1;
                unsigned int reserve_2                   : 2;
                unsigned int win0_fbcd_compress_mode     : 4;
                unsigned int reserve_3                   : 8;
            } bits;
            unsigned int val;
        } win0_fbcd_ctrl;
        struct {
            unsigned int reserve_data[2];
        } reserve_reg_112_120;
        union { // name: win0_pld_ptr_offset, offset: 0x78
            struct {
                unsigned int win0_pld_ptr_offset : 32;
            } bits;
            unsigned int val;
        } win0_pld_ptr_offset;
        union { // name: win0_pld_ptr_range, offset: 0x7c
            struct {
                unsigned int win0_pld_ptr_range : 32;
            } bits;
            unsigned int val;
        } win0_pld_ptr_range;
        union { // name: win1_ctrl0, offset: 0x80
            struct {
                unsigned int win1_en            : 1;
                unsigned int win1_data_fmt      : 6;
                unsigned int win1_tile_mode0_en : 1;
                unsigned int win1_csc_y2r_en    : 1;
                unsigned int win1_csc_r2y_en    : 1;
                unsigned int reserve_0          : 4;
                unsigned int win1_rb_swap       : 1;
                unsigned int reserve_1          : 1;
                unsigned int win1_rg_swap       : 1;
                unsigned int win1_alpha_swap    : 1;
                unsigned int win1_uv_swap       : 1;
                unsigned int win1_dither_up_en  : 1;
                unsigned int win1_yuv_clip      : 1;
                unsigned int reserve_2          : 11;
            } bits;
            unsigned int val;
        } win1_ctrl0;
        union { // name: win1_ctrl1, offset: 0x84
            struct {
                unsigned int win1_yrgb_axi_gather_en : 1;
                unsigned int reserve_0               : 3;
                unsigned int win1_yrgb_gather_num    : 4;
                unsigned int win1_cbcr_gather_num    : 4;
                unsigned int win1_yscl_mode          : 2;
                unsigned int win1_ysu_en             : 1;
                unsigned int win1_ysd_en             : 1;
                unsigned int reserve_1               : 2;
                unsigned int win1_vsd_avg2           : 1;
                unsigned int win1_vsd_avg4           : 1;
                unsigned int win1_xscl_mode          : 2;
                unsigned int win1_xsu_en             : 1;
                unsigned int win1_xsd_en             : 1;
                unsigned int win1_xgt_en             : 1;
                unsigned int win1_xgt_mode           : 2;
                unsigned int win1_xavg_en            : 1;
                unsigned int win1_yrgb_vsd_gt2       : 1;
                unsigned int win1_yrgb_vsd_gt4       : 1;
                unsigned int win1_cbcr_vsd_gt2       : 1;
                unsigned int win1_cbcr_vsd_gt4       : 1;
            } bits;
            unsigned int val;
        } win1_ctrl1;
        union { // name: win1_ctrl2, offset: 0x88
            struct {
                unsigned int win1_rid_yrgb : 4;
                unsigned int reserve_0     : 1;
                unsigned int win1_rid_cbr  : 4;
                unsigned int reserve_1     : 23;
            } bits;
            unsigned int val;
        } win1_ctrl2;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_140_144;
        union { // name: win1_yrgb_mst, offset: 0x90
            struct {
                unsigned int win1_yrgb_mst : 32;
            } bits;
            unsigned int val;
        } win1_yrgb_mst;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_148_152;
        union { // name: win1_vir, offset: 0x98
            struct {
                unsigned int win1_vir_stride : 16;
                unsigned int reserve_0       : 16;
            } bits;
            unsigned int val;
        } win1_vir;
        union { // name: win1_key_ctrl, offset: 0x9c
            struct {
                unsigned int win1_key_color : 30;
                unsigned int reserve_0      : 1;
                unsigned int win1_key_en    : 1;
            } bits;
            unsigned int val;
        } win1_key_ctrl;
        union { // name: win1_act_info, offset: 0xa0
            struct {
                unsigned int win1_act_width  : 13;
                unsigned int reserve_0       : 3;
                unsigned int win1_act_height : 13;
                unsigned int reserve_1       : 3;
            } bits;
            unsigned int val;
        } win1_act_info;
        union { // name: win1_dsp_info, offset: 0xa4
            struct {
                unsigned int win1_dsp_width  : 12;
                unsigned int reserve_0       : 4;
                unsigned int win1_dsp_height : 12;
                unsigned int reserve_1       : 4;
            } bits;
            unsigned int val;
        } win1_dsp_info;
        union { // name: win1_dsp_st, offset: 0xa8
            struct {
                unsigned int win1_dsp_xst : 13;
                unsigned int reserve_0    : 3;
                unsigned int win1_dsp_yst : 13;
                unsigned int reserve_1    : 3;
            } bits;
            unsigned int val;
        } win1_dsp_st;
        union { // name: win1_dsp_bg, offset: 0xac
            struct {
                unsigned int win1_dsp_bg_blue  : 10;
                unsigned int win1_dsp_bg_green : 10;
                unsigned int win1_dsp_bg_red   : 10;
                unsigned int reserve_0         : 1;
                unsigned int win1_bg_en        : 1;
            } bits;
            unsigned int val;
        } win1_dsp_bg;
        union { // name: win1_scl_factor_yrgb, offset: 0xb0
            struct {
                unsigned int win1_hs_factor_yrgb : 16;
                unsigned int win1_vs_factor_yrgb : 16;
            } bits;
            unsigned int val;
        } win1_scl_factor_yrgb;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_180_184;
        union { // name: win1_scl_offset, offset: 0xb8
            struct {
                unsigned int win1_hs_offset_yrgb : 8;
                unsigned int reserve_0           : 8;
                unsigned int win1_vs_offset_yrgb : 8;
                unsigned int reserve_1           : 8;
            } bits;
            unsigned int val;
        } win1_scl_offset;
        union { // name: win1_transformed_offset, offset: 0xbc
            struct {
                unsigned int transformed_xoffset : 4;
                unsigned int reserve_0           : 12;
                unsigned int transformed_yoffset : 4;
                unsigned int reserve_1           : 12;
            } bits;
            unsigned int val;
        } win1_transformed_offset;
        union { // name: win1_zme_ctrl, offset: 0xc0
            struct {
                unsigned int reserve_0          : 3;
                unsigned int win1_zme_dering_en : 1;
                unsigned int reserve_1          : 27;
                unsigned int win1_zme_gating_en : 1;
            } bits;
            unsigned int val;
        } win1_zme_ctrl;
        union { // name: win1_zme_dering_para, offset: 0xc4
            struct {
                unsigned int win1_dering_alpha : 5;
                unsigned int reserve_0         : 3;
                unsigned int win1_dering_beta  : 5;
                unsigned int reserve_1         : 3;
                unsigned int win1_dering_sen0  : 5;
                unsigned int reserve_2         : 3;
                unsigned int win1_dering_sen1  : 5;
                unsigned int reserve_3         : 3;
            } bits;
            unsigned int val;
        } win1_zme_dering_para;
        struct {
            unsigned int reserve_data[2];
        } reserve_reg_200_208;
        union { // name: win1_fbcd_mask_en, offset: 0xd0
            struct {
                unsigned int reserve_0           : 4;
                unsigned int win1_fbcd_gating_en : 1;
                unsigned int reserve_1           : 27;
            } bits;
            unsigned int val;
        } win1_fbcd_mask_en;
        union { // name: win1_fbcd_mode, offset: 0xd4
            struct {
                unsigned int reserve_0    : 2;
                unsigned int win1_xmir_en : 1;
                unsigned int win1_ymir_en : 1;
                unsigned int reserve_1    : 28;
            } bits;
            unsigned int val;
        } win1_fbcd_mode;
        union { // name: win1_fbcd_hdr_ptr, offset: 0xd8
            struct {
                unsigned int win1_fbcd_hdr_ptr : 32;
            } bits;
            unsigned int val;
        } win1_fbcd_hdr_ptr;
        union { // name: win1_fbcd_vir_width, offset: 0xdc
            struct {
                unsigned int win1_fbcd_pic_vir_width : 16;
                unsigned int win1_fbcd_tail_num      : 16;
            } bits;
            unsigned int val;
        } win1_fbcd_vir_width;
        union { // name: win1_fbcd_size, offset: 0xe0
            struct {
                unsigned int win1_fbcd_pic_width  : 16;
                unsigned int win1_fbcd_pic_height : 16;
            } bits;
            unsigned int val;
        } win1_fbcd_size;
        union { // name: win1_fbcd_pic_offset, offset: 0xe4
            struct {
                unsigned int win1_fbcd_pic_xoffset : 16;
                unsigned int win1_fbcd_pic_yoffset : 16;
            } bits;
            unsigned int val;
        } win1_fbcd_pic_offset;
        union { // name: win1_fbcd_dis_offset, offset: 0xe8
            struct {
                unsigned int win1_fbcd_dis_xoffset : 16;
                unsigned int win1_fbcd_dis_yoffset : 16;
            } bits;
            unsigned int val;
        } win1_fbcd_dis_offset;
        union { // name: win1_fbcd_ctrl, offset: 0xec
            struct {
                unsigned int reserve_0                   : 2;
                unsigned int win1_fbcd_pixel_packing_fmt : 5;
                unsigned int win1_fbcd_half_block        : 1;
                unsigned int win1_fbcd_block_split       : 1;
                unsigned int win1_fbcd_rb_swap_en        : 1;
                unsigned int win1_fbcd_uv_swap_en        : 1;
                unsigned int reserve_1                   : 5;
                unsigned int win1_fbcd_pld_offset_en     : 1;
                unsigned int win1_fbcd_pld_range_en      : 1;
                unsigned int reserve_2                   : 2;
                unsigned int win1_fbcd_compress_mode     : 4;
                unsigned int reserve_3                   : 8;
            } bits;
            unsigned int val;
        } win1_fbcd_ctrl;
        struct {
            unsigned int reserve_data[2];
        } reserve_reg_240_248;
        union { // name: win1_pld_ptr_offset, offset: 0xf8
            struct {
                unsigned int win1_pld_ptr_offset : 32;
            } bits;
            unsigned int val;
        } win1_pld_ptr_offset;
        union { // name: win1_pld_ptr_range, offset: 0xfc
            struct {
                unsigned int win1_pld_ptr_range : 32;
            } bits;
            unsigned int val;
        } win1_pld_ptr_range;
        union { // name: cluster_ctrl, offset: 0x100
            struct {
                unsigned int cluster_en              : 1;
                unsigned int cluster_fbcd_en         : 1;
                unsigned int reserve_0               : 2;
                unsigned int cluster_lb_mode         : 2;
                unsigned int reserve_1               : 6;
                unsigned int cluster_dma_stop        : 1;
                unsigned int reserve_2               : 1;
                unsigned int cluster_mmu_bypass      : 1;
                unsigned int cluster_cap_buff_en     : 1;
                unsigned int cluster_dma_hurry_en    : 1;
                unsigned int cluster_dma_hurry_thold : 2;
                unsigned int reserve_3               : 9;
                unsigned int cluster_fbcd_overlap_en : 1;
                unsigned int clusrer_fbcd_priorit_en : 1;
                unsigned int fbcd_bug_fix_dis        : 1;
                unsigned int cluster_frm_resetn_en   : 1;
            } bits;
            unsigned int val;
        } cluster_ctrl;
        union { // name: dci_blk_size, offset: 0x104
            struct {
                unsigned int reserve_0  : 16;
                unsigned int blk_size_v : 9;
                unsigned int blk_size_h : 9;
            } bits;
            unsigned int val;
        } dci_blk_size;
        union { // name: dci_blk_offset, offset: 0x108
            struct {
                unsigned int reserve_0    : 16;
                unsigned int blk_offset_v : 9;
                unsigned int blk_offset_h : 9;
            } bits;
            unsigned int val;
        } dci_blk_offset;
        union { // name: dci_pix_region, offset: 0x10c
            struct {
                unsigned int blk_size_fix       : 20;
                unsigned int pix_region_start_h : 5;
                unsigned int reserve_0          : 1;
                unsigned int pix_region_start_v : 5;
                unsigned int reserve_1          : 1;
            } bits;
            unsigned int val;
        } dci_pix_region;
        union { // name: dci_luma_sat_adj_0, offset: 0x110
            struct {
                unsigned int sat_adj_zero : 16;
                unsigned int sat_adj_thr  : 16;
            } bits;
            unsigned int val;
        } dci_luma_sat_adj_0;
        union { // name: dci_luma_sat_adj_1, offset: 0x114
            struct {
                unsigned int sat_adj_k : 16;
                unsigned int sat_w     : 7;
                unsigned int reserve_0 : 9;
            } bits;
            unsigned int val;
        } dci_luma_sat_adj_1;
        union { // name: dci_ctrl, offset: 0x118
            struct {
                unsigned int dci_en           : 1;
                unsigned int uv_adjust_en     : 1;
                unsigned int reserve_0        : 2;
                unsigned int dma_rid          : 5;
                unsigned int reserve_1        : 3;
                unsigned int dma_rlen         : 2;
                unsigned int reserve_2        : 2;
                unsigned int dci_demo_width   : 13;
                unsigned int reserve_3        : 1;
                unsigned int dci_demo_mode    : 1;
                unsigned int dci_demo_mode_en : 1;
            } bits;
            unsigned int val;
        } dci_ctrl;
        union { // name: dci_lut_mst, offset: 0x11c
            struct {
                unsigned int dci_dma_mst : 32;
            } bits;
            unsigned int val;
        } dci_lut_mst;
        union { // name: dci_dbg_ctrl, offset: 0x120
            struct {
                unsigned int debug_point_h : 13;
                unsigned int reserve_0     : 3;
                unsigned int debug_point_v : 13;
                unsigned int reserve_1     : 1;
                unsigned int debug_mode    : 1;
                unsigned int debug_en      : 1;
            } bits;
            unsigned int val;
        } dci_dbg_ctrl;
        struct {
            unsigned int reserve_data[3];
        } reserve_reg_292_304;
        union { // name: dci_dbg_pix, offset: 0x130
            struct {
                unsigned int dci_debug_pix : 32;
            } bits;
            unsigned int val;
        } dci_dbg_pix;
        struct {
            unsigned int reserve_data[3];
        } reserve_reg_308_320;
        union { // name: dci_csc_coe01_00, offset: 0x140
            struct {
                unsigned int dci_csc_coe00 : 16;
                unsigned int dci_csc_coe01 : 16;
            } bits;
            unsigned int val;
        } dci_csc_coe01_00;
        union { // name: dci_csc_coe10_02, offset: 0x144
            struct {
                unsigned int dci_csc_coe02 : 16;
                unsigned int dci_csc_coe10 : 16;
            } bits;
            unsigned int val;
        } dci_csc_coe10_02;
        union { // name: dci_csc_coe12_11, offset: 0x148
            struct {
                unsigned int dci_csc_coe11 : 16;
                unsigned int dci_csc_coe12 : 16;
            } bits;
            unsigned int val;
        } dci_csc_coe12_11;
        union { // name: dci_csc_coe21_20, offset: 0x14c
            struct {
                unsigned int dci_csc_coe20 : 16;
                unsigned int dci_csc_coe21 : 16;
            } bits;
            unsigned int val;
        } dci_csc_coe21_20;
        union { // name: dci_csc_coe22, offset: 0x150
            struct {
                unsigned int dci_csc_coe22 : 16;
                unsigned int reserve_0     : 16;
            } bits;
            unsigned int val;
        } dci_csc_coe22;
        union { // name: dci_csc_offset0, offset: 0x154
            struct {
                unsigned int dci_csc_offset0 : 32;
            } bits;
            unsigned int val;
        } dci_csc_offset0;
        union { // name: dci_csc_offset1, offset: 0x158
            struct {
                unsigned int dci_csc_offset1 : 32;
            } bits;
            unsigned int val;
        } dci_csc_offset1;
        union { // name: dci_csc_offset2, offset: 0x15c
            struct {
                unsigned int dci_csc_offset2 : 32;
            } bits;
            unsigned int val;
        } dci_csc_offset2;
        union { // name: cap_buff_data0, offset: 0x160
            struct {
                unsigned int cap_buff_data0 : 32;
            } bits;
            unsigned int val;
        } cap_buff_data0;
        union { // name: cap_buff_data1, offset: 0x164
            struct {
                unsigned int cap_buff_data1 : 32;
            } bits;
            unsigned int val;
        } cap_buff_data1;
        union { // name: cap_buff_data2, offset: 0x168
            struct {
                unsigned int cap_buff_data2 : 32;
            } bits;
            unsigned int val;
        } cap_buff_data2;
        union { // name: cap_buff_data3, offset: 0x16c
            struct {
                unsigned int cap_buff_data3 : 32;
            } bits;
            unsigned int val;
        } cap_buff_data3;
        union { // name: win_status, offset: 0x170
            struct {
                unsigned int cap_buff_data_vld : 1;
                unsigned int reserve_0         : 15;
                unsigned int win0_lb_status    : 4;
                unsigned int win1_lb_status    : 4;
                unsigned int reserve_1         : 8;
            } bits;
            unsigned int val;
        } win_status;
        struct {
            unsigned int reserve_data[3];
        } reserve_reg_372_384;
        union { // name: win0_csc_coe01_00, offset: 0x180
            struct {
                unsigned int win0_csc_coe00 : 16;
                unsigned int win0_csc_coe01 : 16;
            } bits;
            unsigned int val;
        } win0_csc_coe01_00;
        union { // name: win0_csc_coe10_02, offset: 0x184
            struct {
                unsigned int win0_csc_coe02 : 16;
                unsigned int win0_csc_coe10 : 16;
            } bits;
            unsigned int val;
        } win0_csc_coe10_02;
        union { // name: win0_csc_coe12_11, offset: 0x188
            struct {
                unsigned int win0_csc_coe11 : 16;
                unsigned int win0_csc_coe12 : 16;
            } bits;
            unsigned int val;
        } win0_csc_coe12_11;
        union { // name: win0_csc_coe21_20, offset: 0x18c
            struct {
                unsigned int win0_csc_coe20 : 16;
                unsigned int win0_csc_coe21 : 16;
            } bits;
            unsigned int val;
        } win0_csc_coe21_20;
        union { // name: win0_csc_coe22, offset: 0x190
            struct {
                unsigned int win0_csc_coe22 : 16;
                unsigned int reserve_0      : 16;
            } bits;
            unsigned int val;
        } win0_csc_coe22;
        union { // name: win0_csc_offset0, offset: 0x194
            struct {
                unsigned int win0_csc_offset0 : 32;
            } bits;
            unsigned int val;
        } win0_csc_offset0;
        union { // name: win0_csc_offset1, offset: 0x198
            struct {
                unsigned int win0_csc_offset1 : 32;
            } bits;
            unsigned int val;
        } win0_csc_offset1;
        union { // name: win0_csc_offset2, offset: 0x19c
            struct {
                unsigned int win0_csc_offset2 : 32;
            } bits;
            unsigned int val;
        } win0_csc_offset2;
        union { // name: win1_csc_coe01_00, offset: 0x1a0
            struct {
                unsigned int win0_csc_coe00 : 16;
                unsigned int win0_csc_coe01 : 16;
            } bits;
            unsigned int val;
        } win1_csc_coe01_00;
        union { // name: win1_csc_coe10_02, offset: 0x1a4
            struct {
                unsigned int win0_csc_coe02 : 16;
                unsigned int win0_csc_coe10 : 16;
            } bits;
            unsigned int val;
        } win1_csc_coe10_02;
        union { // name: win1_csc_coe12_11, offset: 0x1a8
            struct {
                unsigned int win0_csc_coe11 : 16;
                unsigned int win0_csc_coe12 : 16;
            } bits;
            unsigned int val;
        } win1_csc_coe12_11;
        union { // name: win1_csc_coe21_20, offset: 0x1ac
            struct {
                unsigned int win0_csc_coe20 : 16;
                unsigned int win0_csc_coe21 : 16;
            } bits;
            unsigned int val;
        } win1_csc_coe21_20;
        union { // name: win1_csc_coe22, offset: 0x1b0
            struct {
                unsigned int win0_csc_coe22 : 16;
                unsigned int reserve_0      : 16;
            } bits;
            unsigned int val;
        } win1_csc_coe22;
        union { // name: win1_csc_offset0, offset: 0x1b4
            struct {
                unsigned int win0_csc_offset0 : 32;
            } bits;
            unsigned int val;
        } win1_csc_offset0;
        union { // name: win1_csc_offset1, offset: 0x1b8
            struct {
                unsigned int win0_csc_offset1 : 32;
            } bits;
            unsigned int val;
        } win1_csc_offset1;
        union { // name: win1_csc_offset2, offset: 0x1bc
            struct {
                unsigned int win0_csc_offset2 : 32;
            } bits;
            unsigned int val;
        } win1_csc_offset2;
        struct {
            unsigned int reserve_data[4];
        } reserve_reg_448_464;
        union { // name: cluster_src_color_ctrl, offset: 0x1d0
            struct {
                unsigned int src_color_mode0     : 1;
                unsigned int src_alpha_mode0     : 1;
                unsigned int src_blend_mode0     : 2;
                unsigned int src_alpha_cal_mode0 : 1;
                unsigned int src_factor_mode0    : 3;
                unsigned int alpha_en            : 1;
                unsigned int src_dst_swap        : 1;
                unsigned int reserve_0           : 6;
                unsigned int src_global_alpha0   : 8;
                unsigned int reserve_1           : 8;
            } bits;
            unsigned int val;
        } cluster_src_color_ctrl;
        union { // name: cluster_dst_color_ctrl, offset: 0x1d4
            struct {
                unsigned int dst_color_mode0     : 1;
                unsigned int dst_alpha_mode0     : 1;
                unsigned int dst_blend_mode0     : 2;
                unsigned int dst_alpha_cal_mode0 : 1;
                unsigned int dst_factor_mode0    : 3;
                unsigned int reserve_0           : 8;
                unsigned int dst_global_alpha0   : 8;
                unsigned int reserve_1           : 8;
            } bits;
            unsigned int val;
        } cluster_dst_color_ctrl;
        union { // name: cluster_src_alpha_ctrl, offset: 0x1d8
            struct {
                unsigned int reserve_0           : 1;
                unsigned int src_alpha_mode1     : 1;
                unsigned int src_blend_mode1     : 2;
                unsigned int src_alpha_cal_mode1 : 1;
                unsigned int src_factor_mode1    : 3;
                unsigned int reserve_1           : 24;
            } bits;
            unsigned int val;
        } cluster_src_alpha_ctrl;
        union { // name: cluster_dst_alpha_ctrl, offset: 0x1dc
            struct {
                unsigned int reserve_0           : 1;
                unsigned int dst_alpha_mode1     : 1;
                unsigned int dst_blend_mode1     : 2;
                unsigned int dst_alpha_cal_mode1 : 1;
                unsigned int dst_factor_mode1    : 3;
                unsigned int reserve_1           : 24;
            } bits;
            unsigned int val;
        } cluster_dst_alpha_ctrl;
        union { // name: cluster_win0_crc_en, offset: 0x1e0
            struct {
                unsigned int crc_en    : 1;
                unsigned int reserve_0 : 31;
            } bits;
            unsigned int val;
        } cluster_win0_crc_en;
        union { // name: cluster_win0_crc_status, offset: 0x1e4
            struct {
                unsigned int crc_cap_value : 32;
            } bits;
            unsigned int val;
        } cluster_win0_crc_status;
        union { // name: cluster_win1_crc_en, offset: 0x1e8
            struct {
                unsigned int crc_en    : 1;
                unsigned int reserve_0 : 31;
            } bits;
            unsigned int val;
        } cluster_win1_crc_en;
        union { // name: cluster_win1_crc_status, offset: 0x1ec
            struct {
                unsigned int crc_cap_value : 32;
            } bits;
            unsigned int val;
        } cluster_win1_crc_status;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_496_500;
        union { // name: cluster_port_sel_imd, offset: 0x1f4
            struct {
                unsigned int cluster_port_sel : 2;
                unsigned int reserve_0        : 30;
            } bits;
            unsigned int val;
        } cluster_port_sel_imd;
        union { // name: cluster_dly_num, offset: 0x1f8
            struct {
                unsigned int win0_dly_num : 8;
                unsigned int win1_dly_num : 8;
                unsigned int reserve_0    : 16;
            } bits;
            unsigned int val;
        } cluster_dly_num;
        union { // name: cluster_cfg_done, offset: 0x1fc
            struct {
                unsigned int reg_load_cluster_en : 1;
                unsigned int reserve_0           : 15;
                unsigned int write_mask          : 16;
            } bits;
            unsigned int val;
        } cluster_cfg_done;
    } regs;
    unsigned int data[128];
} cluster0_rk3538_u;

// 0x00001800
typedef union esmart0_rk3538 {
    struct {
        union { // name: esmart_ctrl0, offset: 0x0
            struct {
                unsigned int esmart_yuv2rgb_en    : 1;
                unsigned int esmart_rgb2yuv_en    : 1;
                unsigned int reserve_0            : 6;
                unsigned int esmart_mid_swap      : 1;
                unsigned int esmart_endian_swap   : 1;
                unsigned int reserve_1            : 21;
                unsigned int esmart_frm_resetn_en : 1;
            } bits;
            unsigned int val;
        } esmart_ctrl0;
        union { // name: esmart_ctrl1, offset: 0x4
            struct {
                unsigned int esmart_esmart_axi_rlen   : 2;
                unsigned int esmart_yrgb_gather_en    : 1;
                unsigned int esmart_cbcr_gather_en    : 1;
                unsigned int esmart_yrgb_rid          : 5;
                unsigned int reserve_0                : 3;
                unsigned int esmart_cbcr_rid          : 5;
                unsigned int reserve_1                : 3;
                unsigned int esmart_yrgb_gather_num   : 4;
                unsigned int esmart_cbcr_gather_num   : 4;
                unsigned int esmart_dma_rreq_hurry_en : 1;
                unsigned int esmart_dma_rreq_thold    : 2;
                unsigned int esmart_ymir_en           : 1;
            } bits;
            unsigned int val;
        } esmart_ctrl1;
        union { // name: esmart_axi_ctrl_imd, offset: 0x8
            struct {
                unsigned int esmart_dma_sop         : 1;
                unsigned int esmart_axi_sel         : 1;
                unsigned int esmart_mmu_bypass      : 1;
                unsigned int esmart_outstanding_en  : 1;
                unsigned int esmart_outstanding_num : 4;
                unsigned int esmart_auto_gating_en  : 1;
                unsigned int reserve_0              : 7;
                unsigned int esmart_dma_4k_addr_opt : 1;
                unsigned int esmart_err_stop_en     : 1;
                unsigned int reserve_1              : 14;
            } bits;
            unsigned int val;
        } esmart_axi_ctrl_imd;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_12_16;
        union { // name: region0_mst_ctl, offset: 0x10
            struct {
                unsigned int region0_mst_en       : 1;
                unsigned int region0_data_fmt     : 5;
                unsigned int reserve_0            : 1;
                unsigned int region0_argb5551_en  : 1;
                unsigned int region0_yrgb_2gt     : 1;
                unsigned int region0_yrgb_4gt     : 1;
                unsigned int region0_cbcr_2gt     : 1;
                unsigned int region0_cbcr_4gt     : 1;
                unsigned int region0_dither_up_en : 1;
                unsigned int region0_alpha_swap   : 1;
                unsigned int region0_rb_swap      : 1;
                unsigned int region0_mid_swap     : 1;
                unsigned int region0_uv_swap      : 1;
                unsigned int region0_yuv_clip     : 1;
                unsigned int region0_rg_swap      : 1;
                unsigned int reserve_1            : 1;
                unsigned int region0_avg_en       : 1;
                unsigned int region0_xgt_en       : 1;
                unsigned int region0_xgt_mode     : 2;
                unsigned int reserve_2            : 8;
            } bits;
            unsigned int val;
        } region0_mst_ctl;
        union { // name: region0_mst_yrgb, offset: 0x14
            struct {
                unsigned int region0_yrgb_mst : 32;
            } bits;
            unsigned int val;
        } region0_mst_yrgb;
        union { // name: region0_mst_cbcr, offset: 0x18
            struct {
                unsigned int region0_cbcr_mst : 32;
            } bits;
            unsigned int val;
        } region0_mst_cbcr;
        union { // name: region0_vir, offset: 0x1c
            struct {
                unsigned int region0_vir_stride    : 16;
                unsigned int region0_vir_stride_uv : 16;
            } bits;
            unsigned int val;
        } region0_vir;
        union { // name: region0_act_info, offset: 0x20
            struct {
                unsigned int region0_act_width  : 13;
                unsigned int reserve_0          : 3;
                unsigned int region0_act_heigth : 13;
                unsigned int reserve_1          : 3;
            } bits;
            unsigned int val;
        } region0_act_info;
        union { // name: region0_dsp_info, offset: 0x24
            struct {
                unsigned int region0_dsp_width  : 13;
                unsigned int reserve_0          : 3;
                unsigned int region0_dsp_height : 13;
                unsigned int reserve_1          : 3;
            } bits;
            unsigned int val;
        } region0_dsp_info;
        union { // name: region0_dsp_offset, offset: 0x28
            struct {
                unsigned int region0_dsp_xoff : 13;
                unsigned int reserve_0        : 3;
                unsigned int region0_dsp_yoff : 13;
                unsigned int reserve_1        : 3;
            } bits;
            unsigned int val;
        } region0_dsp_offset;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_44_48;
        union { // name: region0_scl_ctrl, offset: 0x30
            struct {
                unsigned int region0_yrgb_xsu_en    : 1;
                unsigned int region0_yrgb_xsd_en    : 1;
                unsigned int region0_yrgb_xscl_mode : 2;
                unsigned int region0_yrgb_ysu_en    : 1;
                unsigned int region0_yrgb_ysd_en    : 1;
                unsigned int region0_yrgb_yscl_mode : 2;
                unsigned int reserve_0              : 8;
                unsigned int region0_xsu_bic_mode   : 2;
                unsigned int reserve_1              : 14;
            } bits;
            unsigned int val;
        } region0_scl_ctrl;
        union { // name: region0_scl_factor_yrgb, offset: 0x34
            struct {
                unsigned int region0_yrgb_xfactor : 16;
                unsigned int region0_yrgb_yfactor : 16;
            } bits;
            unsigned int val;
        } region0_scl_factor_yrgb;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_56_60;
        union { // name: region0_scl_offset, offset: 0x3c
            struct {
                unsigned int region0_yrgb_xscl_offset : 8;
                unsigned int region0_yrgb_yscl_offset : 8;
                unsigned int reserve_0                : 16;
            } bits;
            unsigned int val;
        } region0_scl_offset;
        union { // name: region1_mst_ctl, offset: 0x40
            struct {
                unsigned int region1_mst_en       : 1;
                unsigned int region1_data_fmt     : 5;
                unsigned int reserve_0            : 1;
                unsigned int region1_argb5551_en  : 1;
                unsigned int region1_yrgb_2gt     : 1;
                unsigned int region1_yrgb_4gt     : 1;
                unsigned int region1_cbcr_2gt     : 1;
                unsigned int region1_cbcr_4gt     : 1;
                unsigned int region1_dither_up_en : 1;
                unsigned int region1_alpha_swap   : 1;
                unsigned int region1_rb_swap      : 1;
                unsigned int region1_mid_swap     : 1;
                unsigned int region1_uv_swap      : 1;
                unsigned int region1_yuv_clip     : 1;
                unsigned int region1_rg_swap      : 1;
                unsigned int reserve_1            : 1;
                unsigned int region1_avg_en       : 1;
                unsigned int region1_xgt_en       : 1;
                unsigned int region1_xgt_mode     : 2;
                unsigned int reserve_2            : 8;
            } bits;
            unsigned int val;
        } region1_mst_ctl;
        union { // name: region1_mst_yrgb, offset: 0x44
            struct {
                unsigned int region1_yrgb_mst : 32;
            } bits;
            unsigned int val;
        } region1_mst_yrgb;
        union { // name: region1_mst_cbcr, offset: 0x48
            struct {
                unsigned int region1_cbcr_mst : 32;
            } bits;
            unsigned int val;
        } region1_mst_cbcr;
        union { // name: region1_vir, offset: 0x4c
            struct {
                unsigned int region1_vir_stride    : 16;
                unsigned int region1_vir_stride_uv : 16;
            } bits;
            unsigned int val;
        } region1_vir;
        union { // name: region1_act_info, offset: 0x50
            struct {
                unsigned int region1_act_width  : 13;
                unsigned int reserve_0          : 3;
                unsigned int region1_act_heigth : 13;
                unsigned int reserve_1          : 3;
            } bits;
            unsigned int val;
        } region1_act_info;
        union { // name: region1_dsp_info, offset: 0x54
            struct {
                unsigned int region1_dsp_width  : 13;
                unsigned int reserve_0          : 3;
                unsigned int region1_dsp_height : 13;
                unsigned int reserve_1          : 3;
            } bits;
            unsigned int val;
        } region1_dsp_info;
        union { // name: region1_dsp_offset, offset: 0x58
            struct {
                unsigned int region1_dsp_xoff : 13;
                unsigned int reserve_0        : 3;
                unsigned int region1_dsp_yoff : 13;
                unsigned int reserve_1        : 3;
            } bits;
            unsigned int val;
        } region1_dsp_offset;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_92_96;
        union { // name: region1_scl_ctrl, offset: 0x60
            struct {
                unsigned int region1_yrgb_xsu_en    : 1;
                unsigned int region1_yrgb_xsd_en    : 1;
                unsigned int region1_yrgb_xscl_mode : 2;
                unsigned int region1_yrgb_ysu_en    : 1;
                unsigned int region1_yrgb_ysd_en    : 1;
                unsigned int region1_yrgb_yscl_mode : 2;
                unsigned int reserve_0              : 8;
                unsigned int region1_xsu_bic_mode   : 2;
                unsigned int reserve_1              : 14;
            } bits;
            unsigned int val;
        } region1_scl_ctrl;
        union { // name: region1_scl_factor_yrgb, offset: 0x64
            struct {
                unsigned int region1_yrgb_xfactor : 16;
                unsigned int region1_yrgb_yfactor : 16;
            } bits;
            unsigned int val;
        } region1_scl_factor_yrgb;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_104_108;
        union { // name: region1_scl_offset, offset: 0x6c
            struct {
                unsigned int region1_yrgb_xscl_offset : 8;
                unsigned int region1_yrgb_yscl_offset : 8;
                unsigned int reserve_0                : 16;
            } bits;
            unsigned int val;
        } region1_scl_offset;
        union { // name: region2_mst_ctl, offset: 0x70
            struct {
                unsigned int region2_mst_en       : 1;
                unsigned int region2_data_fmt     : 5;
                unsigned int reserve_0            : 1;
                unsigned int region2_argb5551_en  : 1;
                unsigned int region2_yrgb_2gt     : 1;
                unsigned int region2_yrgb_4gt     : 1;
                unsigned int region2_cbcr_2gt     : 1;
                unsigned int region2_cbcr_4gt     : 1;
                unsigned int region2_dither_up_en : 1;
                unsigned int region2_alpha_swap   : 1;
                unsigned int region2_rb_swap      : 1;
                unsigned int region2_mid_swap     : 1;
                unsigned int region2_uv_swap      : 1;
                unsigned int region2_yuv_clip     : 1;
                unsigned int region2_rg_swap      : 1;
                unsigned int reserve_1            : 1;
                unsigned int region2_avg_en       : 1;
                unsigned int region2_xgt_en       : 1;
                unsigned int region2_xgt_mode     : 2;
                unsigned int reserve_2            : 8;
            } bits;
            unsigned int val;
        } region2_mst_ctl;
        union { // name: region2_mst_yrgb, offset: 0x74
            struct {
                unsigned int region2_yrgb_mst : 32;
            } bits;
            unsigned int val;
        } region2_mst_yrgb;
        union { // name: region2_mst_cbcr, offset: 0x78
            struct {
                unsigned int region2_cbcr_mst : 32;
            } bits;
            unsigned int val;
        } region2_mst_cbcr;
        union { // name: region2_vir, offset: 0x7c
            struct {
                unsigned int region2_vir_stride    : 16;
                unsigned int region2_vir_stride_uv : 16;
            } bits;
            unsigned int val;
        } region2_vir;
        union { // name: region2_act_info, offset: 0x80
            struct {
                unsigned int region2_act_width  : 13;
                unsigned int reserve_0          : 3;
                unsigned int region2_act_heigth : 13;
                unsigned int reserve_1          : 3;
            } bits;
            unsigned int val;
        } region2_act_info;
        union { // name: region2_dsp_info, offset: 0x84
            struct {
                unsigned int region2_dsp_width  : 13;
                unsigned int reserve_0          : 3;
                unsigned int region2_dsp_height : 13;
                unsigned int reserve_1          : 3;
            } bits;
            unsigned int val;
        } region2_dsp_info;
        union { // name: region2_dsp_offset, offset: 0x88
            struct {
                unsigned int region2_dsp_xoff : 13;
                unsigned int reserve_0        : 3;
                unsigned int region2_dsp_yoff : 13;
                unsigned int reserve_1        : 3;
            } bits;
            unsigned int val;
        } region2_dsp_offset;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_140_144;
        union { // name: region2_scl_ctrl, offset: 0x90
            struct {
                unsigned int region2_yrgb_xsu_en    : 1;
                unsigned int region2_yrgb_xsd_en    : 1;
                unsigned int region2_yrgb_xscl_mode : 2;
                unsigned int region2_yrgb_ysu_en    : 1;
                unsigned int region2_yrgb_ysd_en    : 1;
                unsigned int region2_yrgb_yscl_mode : 2;
                unsigned int reserve_0              : 8;
                unsigned int region2_xsu_bic_mode   : 2;
                unsigned int reserve_1              : 14;
            } bits;
            unsigned int val;
        } region2_scl_ctrl;
        union { // name: region2_scl_factor_yrgb, offset: 0x94
            struct {
                unsigned int region2_yrgb_xfactor : 16;
                unsigned int region2_yrgb_yfactor : 16;
            } bits;
            unsigned int val;
        } region2_scl_factor_yrgb;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_152_156;
        union { // name: region2_scl_offset, offset: 0x9c
            struct {
                unsigned int region2_yrgb_xscl_offset : 8;
                unsigned int region2_yrgb_yscl_offset : 8;
                unsigned int reserve_0                : 16;
            } bits;
            unsigned int val;
        } region2_scl_offset;
        union { // name: region3_mst_ctl, offset: 0xa0
            struct {
                unsigned int region3_mst_en       : 1;
                unsigned int region3_data_fmt     : 5;
                unsigned int reserve_0            : 2;
                unsigned int region3_yrgb_2gt     : 1;
                unsigned int region3_yrgb_4gt     : 1;
                unsigned int region3_cbcr_2gt     : 1;
                unsigned int region3_cbcr_4gt     : 1;
                unsigned int region3_dither_up_en : 1;
                unsigned int region3_alpha_swap   : 1;
                unsigned int region3_rb_swap      : 1;
                unsigned int region3_mid_swap     : 1;
                unsigned int region3_uv_swap      : 1;
                unsigned int region3_yuv_clip     : 1;
                unsigned int region3_rg_swap      : 1;
                unsigned int reserve_1            : 1;
                unsigned int region3_avg_en       : 1;
                unsigned int region3_xgt_en       : 1;
                unsigned int region3_xgt_mode     : 2;
                unsigned int reserve_2            : 8;
            } bits;
            unsigned int val;
        } region3_mst_ctl;
        union { // name: region3_mst_yrgb, offset: 0xa4
            struct {
                unsigned int region3_yrgb_mst : 32;
            } bits;
            unsigned int val;
        } region3_mst_yrgb;
        union { // name: region3_mst_cbcr, offset: 0xa8
            struct {
                unsigned int region3_cbcr_mst : 32;
            } bits;
            unsigned int val;
        } region3_mst_cbcr;
        union { // name: region3_vir, offset: 0xac
            struct {
                unsigned int region3_vir_stride    : 16;
                unsigned int region3_vir_stride_uv : 16;
            } bits;
            unsigned int val;
        } region3_vir;
        union { // name: region3_act_info, offset: 0xb0
            struct {
                unsigned int region3_act_width  : 13;
                unsigned int reserve_0          : 3;
                unsigned int region3_act_heigth : 13;
                unsigned int reserve_1          : 3;
            } bits;
            unsigned int val;
        } region3_act_info;
        union { // name: region3_dsp_info, offset: 0xb4
            struct {
                unsigned int region3_dsp_width  : 13;
                unsigned int reserve_0          : 3;
                unsigned int region3_dsp_height : 13;
                unsigned int reserve_1          : 3;
            } bits;
            unsigned int val;
        } region3_dsp_info;
        union { // name: region3_dsp_offset, offset: 0xb8
            struct {
                unsigned int region3_dsp_xoff : 13;
                unsigned int reserve_0        : 3;
                unsigned int region3_dsp_yoff : 13;
                unsigned int reserve_1        : 3;
            } bits;
            unsigned int val;
        } region3_dsp_offset;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_188_192;
        union { // name: region3_scl_ctrl, offset: 0xc0
            struct {
                unsigned int region3_yrgb_xsu_en    : 1;
                unsigned int region3_yrgb_xsd_en    : 1;
                unsigned int region3_yrgb_xscl_mode : 2;
                unsigned int region3_yrgb_ysu_en    : 1;
                unsigned int region3_yrgb_ysd_en    : 1;
                unsigned int region3_yrgb_yscl_mode : 2;
                unsigned int reserve_0              : 8;
                unsigned int region3_xsu_bic_mode   : 2;
                unsigned int reserve_1              : 14;
            } bits;
            unsigned int val;
        } region3_scl_ctrl;
        union { // name: region3_scl_factor_yrgb, offset: 0xc4
            struct {
                unsigned int region3_yrgb_xfactor : 16;
                unsigned int region3_yrgb_yfactor : 16;
            } bits;
            unsigned int val;
        } region3_scl_factor_yrgb;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_200_204;
        union { // name: region3_scl_offset, offset: 0xcc
            struct {
                unsigned int region3_yrgb_xscl_offset : 8;
                unsigned int region3_yrgb_yscl_offset : 8;
                unsigned int reserve_0                : 16;
            } bits;
            unsigned int val;
        } region3_scl_offset;
        union { // name: esmart_key_ctrl, offset: 0xd0
            struct {
                unsigned int esmart_b_key_value : 10;
                unsigned int esmart_g_key_value : 10;
                unsigned int esmart_r_key_value : 10;
                unsigned int reserve_0          : 1;
                unsigned int esmart_key_en      : 1;
            } bits;
            unsigned int val;
        } esmart_key_ctrl;
        union { // name: esmart_bg_en, offset: 0xd4
            struct {
                unsigned int esmart_b_value : 10;
                unsigned int esmart_g_value : 10;
                unsigned int esmart_r_value : 10;
                unsigned int reserve_0      : 1;
                unsigned int esmart_bg_en   : 1;
            } bits;
            unsigned int val;
        } esmart_bg_en;
        union { // name: esmart_alpha_map, offset: 0xd8
            struct {
                unsigned int alpha_0_map  : 8;
                unsigned int alpha_1_map  : 8;
                unsigned int reserve_0    : 15;
                unsigned int alpha_map_en : 1;
            } bits;
            unsigned int val;
        } esmart_alpha_map;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_220_224;
        union { // name: esmart_crc_en, offset: 0xe0
            struct {
                unsigned int crc_en    : 1;
                unsigned int reserve_0 : 31;
            } bits;
            unsigned int val;
        } esmart_crc_en;
        union { // name: esmart_crc_status, offset: 0xe4
            struct {
                unsigned int crc_cap_value : 32;
            } bits;
            unsigned int val;
        } esmart_crc_status;
        struct {
            unsigned int reserve_data[3];
        } reserve_reg_232_244;
        union { // name: esmart_port_sel_imd, offset: 0xf4
            struct {
                unsigned int esmart_port_sel : 2;
                unsigned int reserve_0       : 30;
            } bits;
            unsigned int val;
        } esmart_port_sel_imd;
        union { // name: esmart_dly_num, offset: 0xf8
            struct {
                unsigned int esmart_dly_num : 8;
                unsigned int reserve_0      : 24;
            } bits;
            unsigned int val;
        } esmart_dly_num;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_252_256;
        union { // name: esmart_csc_coe01_00, offset: 0x100
            struct {
                unsigned int sw_win_csc_coe00 : 16;
                unsigned int sw_win_csc_coe01 : 16;
            } bits;
            unsigned int val;
        } esmart_csc_coe01_00;
        union { // name: esmart_csc_coe10_02, offset: 0x104
            struct {
                unsigned int sw_win_csc_coe02 : 16;
                unsigned int sw_win_csc_coe10 : 16;
            } bits;
            unsigned int val;
        } esmart_csc_coe10_02;
        union { // name: esmart_csc_coe12_11, offset: 0x108
            struct {
                unsigned int sw_win_csc_coe11 : 16;
                unsigned int sw_win_csc_coe12 : 16;
            } bits;
            unsigned int val;
        } esmart_csc_coe12_11;
        union { // name: esmart_csc_coe21_20, offset: 0x10c
            struct {
                unsigned int sw_win_csc_coe20 : 16;
                unsigned int sw_win_csc_coe21 : 16;
            } bits;
            unsigned int val;
        } esmart_csc_coe21_20;
        union { // name: esmart_csc_coe22, offset: 0x110
            struct {
                unsigned int sw_win_csc_coe22 : 16;
                unsigned int reserve_0        : 16;
            } bits;
            unsigned int val;
        } esmart_csc_coe22;
        union { // name: esmart_csc_offset0, offset: 0x114
            struct {
                unsigned int sw_win_csc_offset0 : 32;
            } bits;
            unsigned int val;
        } esmart_csc_offset0;
        union { // name: esmart_csc_offset1, offset: 0x118
            struct {
                unsigned int sw_win_csc_offset1 : 32;
            } bits;
            unsigned int val;
        } esmart_csc_offset1;
        union { // name: esmart_csc_offset2, offset: 0x11c
            struct {
                unsigned int sw_win_csc_offset2 : 32;
            } bits;
            unsigned int val;
        } esmart_csc_offset2;
        union { // name: esmart_cap_buff_data0, offset: 0x120
            struct {
                unsigned int cap_buff_data0 : 32;
            } bits;
            unsigned int val;
        } esmart_cap_buff_data0;
        union { // name: esmart_cap_buff_data1, offset: 0x124
            struct {
                unsigned int cap_buff_data1 : 32;
            } bits;
            unsigned int val;
        } esmart_cap_buff_data1;
        union { // name: esmart_cap_buff_data2, offset: 0x128
            struct {
                unsigned int cap_buff_data2 : 32;
            } bits;
            unsigned int val;
        } esmart_cap_buff_data2;
        union { // name: esmart_cap_buff_data3, offset: 0x12c
            struct {
                unsigned int cap_buff_data3 : 32;
            } bits;
            unsigned int val;
        } esmart_cap_buff_data3;
        struct {
            unsigned int reserve_data[51];
        } reserve_reg_304_508;
        union { // name: emsart_cfg_done, offset: 0x1fc
            struct {
                unsigned int reg_load_esmart_en : 1;
                unsigned int reserve_0          : 31;
            } bits;
            unsigned int val;
        } emsart_cfg_done;
    } regs;
    unsigned int data[128];
} esmart0_rk3538_u;

// 0x00001A00
typedef union esmart1_rk3538 {
    struct {
        union { // name: esmart_ctrl0, offset: 0x0
            struct {
                unsigned int esmart_yuv2rgb_en  : 1;
                unsigned int esmart_rgb2yuv_en  : 1;
                unsigned int reserve_0          : 6;
                unsigned int esmart_mid_swap    : 1;
                unsigned int esmart_endian_swap : 1;
                unsigned int reserve_1          : 22;
            } bits;
            unsigned int val;
        } esmart_ctrl0;
        union { // name: esmart_ctrl1, offset: 0x4
            struct {
                unsigned int esmart_esmart_axi_rlen   : 2;
                unsigned int esmart_yrgb_gather_en    : 1;
                unsigned int esmart_cbcr_gather_en    : 1;
                unsigned int esmart_yrgb_rid          : 5;
                unsigned int reserve_0                : 3;
                unsigned int esmart_cbcr_rid          : 5;
                unsigned int reserve_1                : 3;
                unsigned int esmart_yrgb_gather_num   : 4;
                unsigned int esmart_cbcr_gather_num   : 4;
                unsigned int esmart_dma_rreq_hurry_en : 1;
                unsigned int esmart_dma_rreq_thold    : 2;
                unsigned int esmart_ymir_en           : 1;
            } bits;
            unsigned int val;
        } esmart_ctrl1;
        union { // name: esmart_axi_ctrl_imd, offset: 0x8
            struct {
                unsigned int esmart_dma_sop         : 1;
                unsigned int esmart_axi_sel         : 1;
                unsigned int esmart_mmu_bypass      : 1;
                unsigned int esmart_outstanding_en  : 1;
                unsigned int esmart_outstanding_num : 4;
                unsigned int esmart_auto_gating_en  : 1;
                unsigned int reserve_0              : 7;
                unsigned int esmart_dma_4k_addr_opt : 1;
                unsigned int esmart_err_stop_en     : 1;
                unsigned int reserve_1              : 14;
            } bits;
            unsigned int val;
        } esmart_axi_ctrl_imd;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_12_16;
        union { // name: region0_mst_ctl, offset: 0x10
            struct {
                unsigned int region0_mst_en       : 1;
                unsigned int region0_data_fmt     : 5;
                unsigned int reserve_0            : 1;
                unsigned int region0_argb5551_en  : 1;
                unsigned int region0_yrgb_2gt     : 1;
                unsigned int region0_yrgb_4gt     : 1;
                unsigned int region0_cbcr_2gt     : 1;
                unsigned int region0_cbcr_4gt     : 1;
                unsigned int region0_dither_up_en : 1;
                unsigned int region0_alpha_swap   : 1;
                unsigned int region0_rb_swap      : 1;
                unsigned int region0_mid_swap     : 1;
                unsigned int region0_uv_swap      : 1;
                unsigned int region0_yuv_clip     : 1;
                unsigned int region0_rg_swap      : 1;
                unsigned int reserve_1            : 1;
                unsigned int region0_avg_en       : 1;
                unsigned int region0_xgt_en       : 1;
                unsigned int region0_xgt_mode     : 2;
                unsigned int region0_force_yuv_en : 1;
                unsigned int reserve_2            : 7;
            } bits;
            unsigned int val;
        } region0_mst_ctl;
        union { // name: region0_mst_yrgb, offset: 0x14
            struct {
                unsigned int region0_yrgb_mst : 32;
            } bits;
            unsigned int val;
        } region0_mst_yrgb;
        union { // name: region0_mst_cbcr, offset: 0x18
            struct {
                unsigned int region0_cbcr_mst : 32;
            } bits;
            unsigned int val;
        } region0_mst_cbcr;
        union { // name: region0_vir, offset: 0x1c
            struct {
                unsigned int region0_vir_stride    : 16;
                unsigned int region0_vir_stride_uv : 16;
            } bits;
            unsigned int val;
        } region0_vir;
        union { // name: region0_act_info, offset: 0x20
            struct {
                unsigned int region0_act_width  : 13;
                unsigned int reserve_0          : 3;
                unsigned int region0_act_heigth : 13;
                unsigned int reserve_1          : 3;
            } bits;
            unsigned int val;
        } region0_act_info;
        union { // name: region0_dsp_info, offset: 0x24
            struct {
                unsigned int region0_dsp_width  : 13;
                unsigned int reserve_0          : 3;
                unsigned int region0_dsp_height : 13;
                unsigned int reserve_1          : 3;
            } bits;
            unsigned int val;
        } region0_dsp_info;
        union { // name: region0_dsp_offset, offset: 0x28
            struct {
                unsigned int region0_dsp_xoff : 13;
                unsigned int reserve_0        : 3;
                unsigned int region0_dsp_yoff : 13;
                unsigned int reserve_1        : 3;
            } bits;
            unsigned int val;
        } region0_dsp_offset;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_44_48;
        union { // name: region0_scl_ctrl, offset: 0x30
            struct {
                unsigned int region0_yrgb_xsu_en    : 1;
                unsigned int region0_yrgb_xsd_en    : 1;
                unsigned int region0_yrgb_xscl_mode : 2;
                unsigned int region0_yrgb_ysu_en    : 1;
                unsigned int region0_yrgb_ysd_en    : 1;
                unsigned int region0_yrgb_yscl_mode : 2;
                unsigned int reserve_0              : 8;
                unsigned int region0_xsu_bic_mode   : 2;
                unsigned int reserve_1              : 14;
            } bits;
            unsigned int val;
        } region0_scl_ctrl;
        union { // name: region0_scl_factor_yrgb, offset: 0x34
            struct {
                unsigned int region0_yrgb_xfactor : 16;
                unsigned int region0_yrgb_yfactor : 16;
            } bits;
            unsigned int val;
        } region0_scl_factor_yrgb;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_56_60;
        union { // name: region0_scl_offset, offset: 0x3c
            struct {
                unsigned int region0_yrgb_xscl_offset : 8;
                unsigned int region0_yrgb_yscl_offset : 8;
                unsigned int reserve_0                : 16;
            } bits;
            unsigned int val;
        } region0_scl_offset;
        union { // name: region1_mst_ctl, offset: 0x40
            struct {
                unsigned int region1_mst_en       : 1;
                unsigned int region1_data_fmt     : 5;
                unsigned int reserve_0            : 1;
                unsigned int region1_argb5551_en  : 1;
                unsigned int region1_yrgb_2gt     : 1;
                unsigned int region1_yrgb_4gt     : 1;
                unsigned int region1_cbcr_2gt     : 1;
                unsigned int region1_cbcr_4gt     : 1;
                unsigned int region1_dither_up_en : 1;
                unsigned int region1_alpha_swap   : 1;
                unsigned int region1_rb_swap      : 1;
                unsigned int region1_mid_swap     : 1;
                unsigned int region1_uv_swap      : 1;
                unsigned int region1_yuv_clip     : 1;
                unsigned int region1_rg_swap      : 1;
                unsigned int reserve_1            : 1;
                unsigned int region1_avg_en       : 1;
                unsigned int region1_xgt_en       : 1;
                unsigned int region1_xgt_mode     : 2;
                unsigned int reserve_2            : 8;
            } bits;
            unsigned int val;
        } region1_mst_ctl;
        union { // name: region1_mst_yrgb, offset: 0x44
            struct {
                unsigned int region1_yrgb_mst : 32;
            } bits;
            unsigned int val;
        } region1_mst_yrgb;
        union { // name: region1_mst_cbcr, offset: 0x48
            struct {
                unsigned int region1_cbcr_mst : 32;
            } bits;
            unsigned int val;
        } region1_mst_cbcr;
        union { // name: region1_vir, offset: 0x4c
            struct {
                unsigned int region1_vir_stride    : 16;
                unsigned int region1_vir_stride_uv : 16;
            } bits;
            unsigned int val;
        } region1_vir;
        union { // name: region1_act_info, offset: 0x50
            struct {
                unsigned int region1_act_width  : 13;
                unsigned int reserve_0          : 3;
                unsigned int region1_act_heigth : 13;
                unsigned int reserve_1          : 3;
            } bits;
            unsigned int val;
        } region1_act_info;
        union { // name: region1_dsp_info, offset: 0x54
            struct {
                unsigned int region1_dsp_width  : 13;
                unsigned int reserve_0          : 3;
                unsigned int region1_dsp_height : 13;
                unsigned int reserve_1          : 3;
            } bits;
            unsigned int val;
        } region1_dsp_info;
        union { // name: region1_dsp_offset, offset: 0x58
            struct {
                unsigned int region1_dsp_xoff : 13;
                unsigned int reserve_0        : 3;
                unsigned int region1_dsp_yoff : 13;
                unsigned int reserve_1        : 3;
            } bits;
            unsigned int val;
        } region1_dsp_offset;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_92_96;
        union { // name: region1_scl_ctrl, offset: 0x60
            struct {
                unsigned int region1_yrgb_xsu_en    : 1;
                unsigned int region1_yrgb_xsd_en    : 1;
                unsigned int region1_yrgb_xscl_mode : 2;
                unsigned int region1_yrgb_ysu_en    : 1;
                unsigned int region1_yrgb_ysd_en    : 1;
                unsigned int region1_yrgb_yscl_mode : 2;
                unsigned int reserve_0              : 8;
                unsigned int region1_xsu_bic_mode   : 2;
                unsigned int reserve_1              : 14;
            } bits;
            unsigned int val;
        } region1_scl_ctrl;
        union { // name: region1_scl_factor_yrgb, offset: 0x64
            struct {
                unsigned int region1_yrgb_xfactor : 16;
                unsigned int region1_yrgb_yfactor : 16;
            } bits;
            unsigned int val;
        } region1_scl_factor_yrgb;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_104_108;
        union { // name: region1_scl_offset, offset: 0x6c
            struct {
                unsigned int region1_yrgb_xscl_offset : 8;
                unsigned int region1_yrgb_yscl_offset : 8;
                unsigned int reserve_0                : 16;
            } bits;
            unsigned int val;
        } region1_scl_offset;
        union { // name: region2_mst_ctl, offset: 0x70
            struct {
                unsigned int region2_mst_en       : 1;
                unsigned int region2_data_fmt     : 5;
                unsigned int reserve_0            : 1;
                unsigned int region2_argb5551_en  : 1;
                unsigned int region2_yrgb_2gt     : 1;
                unsigned int region2_yrgb_4gt     : 1;
                unsigned int region2_cbcr_2gt     : 1;
                unsigned int region2_cbcr_4gt     : 1;
                unsigned int region2_dither_up_en : 1;
                unsigned int region2_alpha_swap   : 1;
                unsigned int region2_rb_swap      : 1;
                unsigned int region2_mid_swap     : 1;
                unsigned int region2_uv_swap      : 1;
                unsigned int region2_yuv_clip     : 1;
                unsigned int region2_rg_swap      : 1;
                unsigned int reserve_1            : 1;
                unsigned int region2_avg_en       : 1;
                unsigned int region2_xgt_en       : 1;
                unsigned int region2_xgt_mode     : 2;
                unsigned int reserve_2            : 8;
            } bits;
            unsigned int val;
        } region2_mst_ctl;
        union { // name: region2_mst_yrgb, offset: 0x74
            struct {
                unsigned int region2_yrgb_mst : 32;
            } bits;
            unsigned int val;
        } region2_mst_yrgb;
        union { // name: region2_mst_cbcr, offset: 0x78
            struct {
                unsigned int region2_cbcr_mst : 32;
            } bits;
            unsigned int val;
        } region2_mst_cbcr;
        union { // name: region2_vir, offset: 0x7c
            struct {
                unsigned int region2_vir_stride    : 16;
                unsigned int region2_vir_stride_uv : 16;
            } bits;
            unsigned int val;
        } region2_vir;
        union { // name: region2_act_info, offset: 0x80
            struct {
                unsigned int region2_act_width  : 13;
                unsigned int reserve_0          : 3;
                unsigned int region2_act_heigth : 13;
                unsigned int reserve_1          : 3;
            } bits;
            unsigned int val;
        } region2_act_info;
        union { // name: region2_dsp_info, offset: 0x84
            struct {
                unsigned int region2_dsp_width  : 13;
                unsigned int reserve_0          : 3;
                unsigned int region2_dsp_height : 13;
                unsigned int reserve_1          : 3;
            } bits;
            unsigned int val;
        } region2_dsp_info;
        union { // name: region2_dsp_offset, offset: 0x88
            struct {
                unsigned int region2_dsp_xoff : 13;
                unsigned int reserve_0        : 3;
                unsigned int region2_dsp_yoff : 13;
                unsigned int reserve_1        : 3;
            } bits;
            unsigned int val;
        } region2_dsp_offset;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_140_144;
        union { // name: region2_scl_ctrl, offset: 0x90
            struct {
                unsigned int region2_yrgb_xsu_en    : 1;
                unsigned int region2_yrgb_xsd_en    : 1;
                unsigned int region2_yrgb_xscl_mode : 2;
                unsigned int region2_yrgb_ysu_en    : 1;
                unsigned int region2_yrgb_ysd_en    : 1;
                unsigned int region2_yrgb_yscl_mode : 2;
                unsigned int reserve_0              : 8;
                unsigned int region2_xsu_bic_mode   : 2;
                unsigned int reserve_1              : 14;
            } bits;
            unsigned int val;
        } region2_scl_ctrl;
        union { // name: region2_scl_factor_yrgb, offset: 0x94
            struct {
                unsigned int region2_yrgb_xfactor : 16;
                unsigned int region2_yrgb_yfactor : 16;
            } bits;
            unsigned int val;
        } region2_scl_factor_yrgb;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_152_156;
        union { // name: region2_scl_offset, offset: 0x9c
            struct {
                unsigned int region2_yrgb_xscl_offset : 8;
                unsigned int region2_yrgb_yscl_offset : 8;
                unsigned int reserve_0                : 16;
            } bits;
            unsigned int val;
        } region2_scl_offset;
        union { // name: region3_mst_ctl, offset: 0xa0
            struct {
                unsigned int region3_mst_en       : 1;
                unsigned int region3_data_fmt     : 5;
                unsigned int reserve_0            : 2;
                unsigned int region3_yrgb_2gt     : 1;
                unsigned int region3_yrgb_4gt     : 1;
                unsigned int region3_cbcr_2gt     : 1;
                unsigned int region3_cbcr_4gt     : 1;
                unsigned int region3_dither_up_en : 1;
                unsigned int region3_alpha_swap   : 1;
                unsigned int region3_rb_swap      : 1;
                unsigned int region3_mid_swap     : 1;
                unsigned int region3_uv_swap      : 1;
                unsigned int region3_yuv_clip     : 1;
                unsigned int region3_rg_swap      : 1;
                unsigned int reserve_1            : 1;
                unsigned int region3_avg_en       : 1;
                unsigned int region3_xgt_en       : 1;
                unsigned int region3_xgt_mode     : 2;
                unsigned int reserve_2            : 8;
            } bits;
            unsigned int val;
        } region3_mst_ctl;
        union { // name: region3_mst_yrgb, offset: 0xa4
            struct {
                unsigned int region3_yrgb_mst : 32;
            } bits;
            unsigned int val;
        } region3_mst_yrgb;
        union { // name: region3_mst_cbcr, offset: 0xa8
            struct {
                unsigned int region3_cbcr_mst : 32;
            } bits;
            unsigned int val;
        } region3_mst_cbcr;
        union { // name: region3_vir, offset: 0xac
            struct {
                unsigned int region3_vir_stride    : 16;
                unsigned int region3_vir_stride_uv : 16;
            } bits;
            unsigned int val;
        } region3_vir;
        union { // name: region3_act_info, offset: 0xb0
            struct {
                unsigned int region3_act_width  : 13;
                unsigned int reserve_0          : 3;
                unsigned int region3_act_heigth : 13;
                unsigned int reserve_1          : 3;
            } bits;
            unsigned int val;
        } region3_act_info;
        union { // name: region3_dsp_info, offset: 0xb4
            struct {
                unsigned int region3_dsp_width  : 13;
                unsigned int reserve_0          : 3;
                unsigned int region3_dsp_height : 13;
                unsigned int reserve_1          : 3;
            } bits;
            unsigned int val;
        } region3_dsp_info;
        union { // name: region3_dsp_offset, offset: 0xb8
            struct {
                unsigned int region3_dsp_xoff : 13;
                unsigned int reserve_0        : 3;
                unsigned int region3_dsp_yoff : 13;
                unsigned int reserve_1        : 3;
            } bits;
            unsigned int val;
        } region3_dsp_offset;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_188_192;
        union { // name: region3_scl_ctrl, offset: 0xc0
            struct {
                unsigned int region3_yrgb_xsu_en    : 1;
                unsigned int region3_yrgb_xsd_en    : 1;
                unsigned int region3_yrgb_xscl_mode : 2;
                unsigned int region3_yrgb_ysu_en    : 1;
                unsigned int region3_yrgb_ysd_en    : 1;
                unsigned int region3_yrgb_yscl_mode : 2;
                unsigned int reserve_0              : 8;
                unsigned int region3_xsu_bic_mode   : 2;
                unsigned int reserve_1              : 14;
            } bits;
            unsigned int val;
        } region3_scl_ctrl;
        union { // name: region3_scl_factor_yrgb, offset: 0xc4
            struct {
                unsigned int region3_yrgb_xfactor : 16;
                unsigned int region3_yrgb_yfactor : 16;
            } bits;
            unsigned int val;
        } region3_scl_factor_yrgb;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_200_204;
        union { // name: region3_scl_offset, offset: 0xcc
            struct {
                unsigned int region3_yrgb_xscl_offset : 8;
                unsigned int region3_yrgb_yscl_offset : 8;
                unsigned int reserve_0                : 16;
            } bits;
            unsigned int val;
        } region3_scl_offset;
        union { // name: esmart_key_ctrl, offset: 0xd0
            struct {
                unsigned int esmart_b_key_value : 10;
                unsigned int esmart_g_key_value : 10;
                unsigned int esmart_r_key_value : 10;
                unsigned int reserve_0          : 1;
                unsigned int esmart_key_en      : 1;
            } bits;
            unsigned int val;
        } esmart_key_ctrl;
        union { // name: esmart_bg_en, offset: 0xd4
            struct {
                unsigned int esmart_b_value : 10;
                unsigned int esmart_g_value : 10;
                unsigned int esmart_r_value : 10;
                unsigned int reserve_0      : 1;
                unsigned int esmart_bg_en   : 1;
            } bits;
            unsigned int val;
        } esmart_bg_en;
        union { // name: esmart_alpha_map, offset: 0xd8
            struct {
                unsigned int alpha_0_map  : 8;
                unsigned int alpha_1_map  : 8;
                unsigned int reserve_0    : 15;
                unsigned int alpha_map_en : 1;
            } bits;
            unsigned int val;
        } esmart_alpha_map;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_220_224;
        union { // name: esmart_crc_en, offset: 0xe0
            struct {
                unsigned int crc_en    : 1;
                unsigned int reserve_0 : 31;
            } bits;
            unsigned int val;
        } esmart_crc_en;
        union { // name: esmart_crc_status, offset: 0xe4
            struct {
                unsigned int Field000 : 32;
            } bits;
            unsigned int val;
        } esmart_crc_status;
        struct {
            unsigned int reserve_data[3];
        } reserve_reg_232_244;
        union { // name: esmart_port_sel_imd, offset: 0xf4
            struct {
                unsigned int esmart_port_sel : 2;
                unsigned int reserve_0       : 30;
            } bits;
            unsigned int val;
        } esmart_port_sel_imd;
        union { // name: esmart_dly_num, offset: 0xf8
            struct {
                unsigned int esmart_dly_num : 8;
                unsigned int reserve_0      : 24;
            } bits;
            unsigned int val;
        } esmart_dly_num;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_252_256;
        union { // name: esmart_csc_coe01_00, offset: 0x100
            struct {
                unsigned int sw_win_csc_coe00 : 16;
                unsigned int sw_win_csc_coe01 : 16;
            } bits;
            unsigned int val;
        } esmart_csc_coe01_00;
        union { // name: esmart_csc_coe10_02, offset: 0x104
            struct {
                unsigned int sw_win_csc_coe02 : 16;
                unsigned int sw_win_csc_coe10 : 16;
            } bits;
            unsigned int val;
        } esmart_csc_coe10_02;
        union { // name: esmart_csc_coe12_11, offset: 0x108
            struct {
                unsigned int sw_win_csc_coe11 : 16;
                unsigned int sw_win_csc_coe12 : 16;
            } bits;
            unsigned int val;
        } esmart_csc_coe12_11;
        union { // name: esmart_csc_coe21_20, offset: 0x10c
            struct {
                unsigned int sw_win_csc_coe20 : 16;
                unsigned int sw_win_csc_coe21 : 16;
            } bits;
            unsigned int val;
        } esmart_csc_coe21_20;
        union { // name: esmart_csc_coe22, offset: 0x110
            struct {
                unsigned int sw_win_csc_coe22 : 16;
                unsigned int reserve_0        : 16;
            } bits;
            unsigned int val;
        } esmart_csc_coe22;
        union { // name: esmart_csc_offset0, offset: 0x114
            struct {
                unsigned int sw_win_csc_offset0 : 32;
            } bits;
            unsigned int val;
        } esmart_csc_offset0;
        union { // name: esmart_csc_offset1, offset: 0x118
            struct {
                unsigned int sw_win_csc_offset1 : 32;
            } bits;
            unsigned int val;
        } esmart_csc_offset1;
        union { // name: esmart_csc_offset2, offset: 0x11c
            struct {
                unsigned int sw_win_csc_offset2 : 32;
            } bits;
            unsigned int val;
        } esmart_csc_offset2;
        struct {
            unsigned int reserve_data[55];
        } reserve_reg_288_508;
        union { // name: esmart_cfg_done, offset: 0x1fc
            struct {
                unsigned int reg_load_cluster_en : 1;
                unsigned int reserve_0           : 31;
            } bits;
            unsigned int val;
        } esmart_cfg_done;
    } regs;
    unsigned int data[128];
} esmart1_rk3538_u;

// 0x00001C00
typedef union esmart2_rk3538 {
    struct {
        union { // name: esmart_ctrl0, offset: 0x0
            struct {
                unsigned int esmart_yuv2rgb_en  : 1;
                unsigned int esmart_rgb2yuv_en  : 1;
                unsigned int reserve_0          : 6;
                unsigned int esmart_mid_swap    : 1;
                unsigned int esmart_endian_swap : 1;
                unsigned int reserve_1          : 22;
            } bits;
            unsigned int val;
        } esmart_ctrl0;
        union { // name: esmart_ctrl1, offset: 0x4
            struct {
                unsigned int esmart_esmart_axi_rlen   : 2;
                unsigned int esmart_yrgb_gather_en    : 1;
                unsigned int esmart_cbcr_gather_en    : 1;
                unsigned int esmart_yrgb_rid          : 5;
                unsigned int reserve_0                : 3;
                unsigned int esmart_cbcr_rid          : 5;
                unsigned int reserve_1                : 3;
                unsigned int esmart_yrgb_gather_num   : 4;
                unsigned int esmart_cbcr_gather_num   : 4;
                unsigned int esmart_dma_rreq_hurry_en : 1;
                unsigned int esmart_dma_rreq_thold    : 2;
                unsigned int esmart_ymir_en           : 1;
            } bits;
            unsigned int val;
        } esmart_ctrl1;
        union { // name: esmart_axi_ctrl_imd, offset: 0x8
            struct {
                unsigned int esmart_dma_sop         : 1;
                unsigned int esmart_axi_sel         : 1;
                unsigned int esmart_mmu_bypass      : 1;
                unsigned int esmart_outstanding_en  : 1;
                unsigned int esmart_outstanding_num : 4;
                unsigned int esmart_auto_gating_en  : 1;
                unsigned int reserve_0              : 7;
                unsigned int esmart_dma_4k_addr_opt : 1;
                unsigned int esmart_err_stop_en     : 1;
                unsigned int reserve_1              : 14;
            } bits;
            unsigned int val;
        } esmart_axi_ctrl_imd;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_12_16;
        union { // name: region0_mst_ctl, offset: 0x10
            struct {
                unsigned int region0_mst_en       : 1;
                unsigned int region0_data_fmt     : 5;
                unsigned int reserve_0            : 1;
                unsigned int region0_argb5551_en  : 1;
                unsigned int region0_yrgb_2gt     : 1;
                unsigned int region0_yrgb_4gt     : 1;
                unsigned int region0_cbcr_2gt     : 1;
                unsigned int region0_cbcr_4gt     : 1;
                unsigned int region0_dither_up_en : 1;
                unsigned int region0_alpha_swap   : 1;
                unsigned int region0_rb_swap      : 1;
                unsigned int region0_mid_swap     : 1;
                unsigned int region0_uv_swap      : 1;
                unsigned int region0_yuv_clip     : 1;
                unsigned int region0_rg_swap      : 1;
                unsigned int reserve_1            : 1;
                unsigned int region0_avg_en       : 1;
                unsigned int region0_xgt_en       : 1;
                unsigned int region0_xgt_mode     : 2;
                unsigned int region0_force_yuv_en : 1;
                unsigned int reserve_2            : 7;
            } bits;
            unsigned int val;
        } region0_mst_ctl;
        union { // name: region0_mst_yrgb, offset: 0x14
            struct {
                unsigned int region0_yrgb_mst : 32;
            } bits;
            unsigned int val;
        } region0_mst_yrgb;
        union { // name: region0_mst_cbcr, offset: 0x18
            struct {
                unsigned int region0_cbcr_mst : 32;
            } bits;
            unsigned int val;
        } region0_mst_cbcr;
        union { // name: region0_vir, offset: 0x1c
            struct {
                unsigned int region0_vir_stride    : 16;
                unsigned int region0_vir_stride_uv : 16;
            } bits;
            unsigned int val;
        } region0_vir;
        union { // name: region0_act_info, offset: 0x20
            struct {
                unsigned int region0_act_width  : 13;
                unsigned int reserve_0          : 3;
                unsigned int region0_act_heigth : 13;
                unsigned int reserve_1          : 3;
            } bits;
            unsigned int val;
        } region0_act_info;
        union { // name: region0_dsp_info, offset: 0x24
            struct {
                unsigned int region0_dsp_width  : 13;
                unsigned int reserve_0          : 3;
                unsigned int region0_dsp_height : 13;
                unsigned int reserve_1          : 3;
            } bits;
            unsigned int val;
        } region0_dsp_info;
        union { // name: region0_dsp_offset, offset: 0x28
            struct {
                unsigned int region0_dsp_xoff : 13;
                unsigned int reserve_0        : 3;
                unsigned int region0_dsp_yoff : 13;
                unsigned int reserve_1        : 3;
            } bits;
            unsigned int val;
        } region0_dsp_offset;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_44_48;
        union { // name: region0_scl_ctrl, offset: 0x30
            struct {
                unsigned int region0_yrgb_xsu_en    : 1;
                unsigned int region0_yrgb_xsd_en    : 1;
                unsigned int region0_yrgb_xscl_mode : 2;
                unsigned int region0_yrgb_ysu_en    : 1;
                unsigned int region0_yrgb_ysd_en    : 1;
                unsigned int region0_yrgb_yscl_mode : 2;
                unsigned int reserve_0              : 8;
                unsigned int region0_xsu_bic_mode   : 2;
                unsigned int reserve_1              : 14;
            } bits;
            unsigned int val;
        } region0_scl_ctrl;
        union { // name: region0_scl_factor_yrgb, offset: 0x34
            struct {
                unsigned int region0_yrgb_xfactor : 16;
                unsigned int region0_yrgb_yfactor : 16;
            } bits;
            unsigned int val;
        } region0_scl_factor_yrgb;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_56_60;
        union { // name: region0_scl_offset, offset: 0x3c
            struct {
                unsigned int region0_yrgb_xscl_offset : 8;
                unsigned int region0_yrgb_yscl_offset : 8;
                unsigned int reserve_0                : 16;
            } bits;
            unsigned int val;
        } region0_scl_offset;
        union { // name: region1_mst_ctl, offset: 0x40
            struct {
                unsigned int region1_mst_en       : 1;
                unsigned int region1_data_fmt     : 5;
                unsigned int reserve_0            : 1;
                unsigned int region1_argb5551_en  : 1;
                unsigned int region1_yrgb_2gt     : 1;
                unsigned int region1_yrgb_4gt     : 1;
                unsigned int region1_cbcr_2gt     : 1;
                unsigned int region1_cbcr_4gt     : 1;
                unsigned int region1_dither_up_en : 1;
                unsigned int region1_alpha_swap   : 1;
                unsigned int region1_rb_swap      : 1;
                unsigned int region1_mid_swap     : 1;
                unsigned int region1_uv_swap      : 1;
                unsigned int region1_yuv_clip     : 1;
                unsigned int region1_rg_swap      : 1;
                unsigned int reserve_1            : 1;
                unsigned int region1_avg_en       : 1;
                unsigned int region1_xgt_en       : 1;
                unsigned int region1_xgt_mode     : 2;
                unsigned int reserve_2            : 8;
            } bits;
            unsigned int val;
        } region1_mst_ctl;
        union { // name: region1_mst_yrgb, offset: 0x44
            struct {
                unsigned int region1_yrgb_mst : 32;
            } bits;
            unsigned int val;
        } region1_mst_yrgb;
        union { // name: region1_mst_cbcr, offset: 0x48
            struct {
                unsigned int region1_cbcr_mst : 32;
            } bits;
            unsigned int val;
        } region1_mst_cbcr;
        union { // name: region1_vir, offset: 0x4c
            struct {
                unsigned int region1_vir_stride    : 16;
                unsigned int region1_vir_stride_uv : 16;
            } bits;
            unsigned int val;
        } region1_vir;
        union { // name: region1_act_info, offset: 0x50
            struct {
                unsigned int region1_act_width  : 13;
                unsigned int reserve_0          : 3;
                unsigned int region1_act_heigth : 13;
                unsigned int reserve_1          : 3;
            } bits;
            unsigned int val;
        } region1_act_info;
        union { // name: region1_dsp_info, offset: 0x54
            struct {
                unsigned int region1_dsp_width  : 13;
                unsigned int reserve_0          : 3;
                unsigned int region1_dsp_height : 13;
                unsigned int reserve_1          : 3;
            } bits;
            unsigned int val;
        } region1_dsp_info;
        union { // name: region1_dsp_offset, offset: 0x58
            struct {
                unsigned int region1_dsp_xoff : 13;
                unsigned int reserve_0        : 3;
                unsigned int region1_dsp_yoff : 13;
                unsigned int reserve_1        : 3;
            } bits;
            unsigned int val;
        } region1_dsp_offset;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_92_96;
        union { // name: region1_scl_ctrl, offset: 0x60
            struct {
                unsigned int region1_yrgb_xsu_en    : 1;
                unsigned int region1_yrgb_xsd_en    : 1;
                unsigned int region1_yrgb_xscl_mode : 2;
                unsigned int region1_yrgb_ysu_en    : 1;
                unsigned int region1_yrgb_ysd_en    : 1;
                unsigned int region1_yrgb_yscl_mode : 2;
                unsigned int reserve_0              : 8;
                unsigned int region1_xsu_bic_mode   : 2;
                unsigned int reserve_1              : 14;
            } bits;
            unsigned int val;
        } region1_scl_ctrl;
        union { // name: region1_scl_factor_yrgb, offset: 0x64
            struct {
                unsigned int region1_yrgb_xfactor : 16;
                unsigned int region1_yrgb_yfactor : 16;
            } bits;
            unsigned int val;
        } region1_scl_factor_yrgb;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_104_108;
        union { // name: region1_scl_offset, offset: 0x6c
            struct {
                unsigned int region1_yrgb_xscl_offset : 8;
                unsigned int region1_yrgb_yscl_offset : 8;
                unsigned int reserve_0                : 16;
            } bits;
            unsigned int val;
        } region1_scl_offset;
        union { // name: region2_mst_ctl, offset: 0x70
            struct {
                unsigned int region2_mst_en       : 1;
                unsigned int region2_data_fmt     : 5;
                unsigned int reserve_0            : 1;
                unsigned int region2_argb5551_en  : 1;
                unsigned int region2_yrgb_2gt     : 1;
                unsigned int region2_yrgb_4gt     : 1;
                unsigned int region2_cbcr_2gt     : 1;
                unsigned int region2_cbcr_4gt     : 1;
                unsigned int region2_dither_up_en : 1;
                unsigned int region2_alpha_swap   : 1;
                unsigned int region2_rb_swap      : 1;
                unsigned int region2_mid_swap     : 1;
                unsigned int region2_uv_swap      : 1;
                unsigned int region2_yuv_clip     : 1;
                unsigned int region2_rg_swap      : 1;
                unsigned int reserve_1            : 1;
                unsigned int region2_avg_en       : 1;
                unsigned int region2_xgt_en       : 1;
                unsigned int region2_xgt_mode     : 2;
                unsigned int reserve_2            : 8;
            } bits;
            unsigned int val;
        } region2_mst_ctl;
        union { // name: region2_mst_yrgb, offset: 0x74
            struct {
                unsigned int region2_yrgb_mst : 32;
            } bits;
            unsigned int val;
        } region2_mst_yrgb;
        union { // name: region2_mst_cbcr, offset: 0x78
            struct {
                unsigned int region2_cbcr_mst : 32;
            } bits;
            unsigned int val;
        } region2_mst_cbcr;
        union { // name: region2_vir, offset: 0x7c
            struct {
                unsigned int region2_vir_stride    : 16;
                unsigned int region2_vir_stride_uv : 16;
            } bits;
            unsigned int val;
        } region2_vir;
        union { // name: region2_act_info, offset: 0x80
            struct {
                unsigned int region2_act_width  : 13;
                unsigned int reserve_0          : 3;
                unsigned int region2_act_heigth : 13;
                unsigned int reserve_1          : 3;
            } bits;
            unsigned int val;
        } region2_act_info;
        union { // name: region2_dsp_info, offset: 0x84
            struct {
                unsigned int region2_dsp_width  : 13;
                unsigned int reserve_0          : 3;
                unsigned int region2_dsp_height : 13;
                unsigned int reserve_1          : 3;
            } bits;
            unsigned int val;
        } region2_dsp_info;
        union { // name: region2_dsp_offset, offset: 0x88
            struct {
                unsigned int region2_dsp_xoff : 13;
                unsigned int reserve_0        : 3;
                unsigned int region2_dsp_yoff : 13;
                unsigned int reserve_1        : 3;
            } bits;
            unsigned int val;
        } region2_dsp_offset;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_140_144;
        union { // name: region2_scl_ctrl, offset: 0x90
            struct {
                unsigned int region2_yrgb_xsu_en    : 1;
                unsigned int region2_yrgb_xsd_en    : 1;
                unsigned int region2_yrgb_xscl_mode : 2;
                unsigned int region2_yrgb_ysu_en    : 1;
                unsigned int region2_yrgb_ysd_en    : 1;
                unsigned int region2_yrgb_yscl_mode : 2;
                unsigned int reserve_0              : 8;
                unsigned int region2_xsu_bic_mode   : 2;
                unsigned int reserve_1              : 14;
            } bits;
            unsigned int val;
        } region2_scl_ctrl;
        union { // name: region2_scl_factor_yrgb, offset: 0x94
            struct {
                unsigned int region2_yrgb_xfactor : 16;
                unsigned int region2_yrgb_yfactor : 16;
            } bits;
            unsigned int val;
        } region2_scl_factor_yrgb;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_152_156;
        union { // name: region2_scl_offset, offset: 0x9c
            struct {
                unsigned int region2_yrgb_xscl_offset : 8;
                unsigned int region2_yrgb_yscl_offset : 8;
                unsigned int reserve_0                : 16;
            } bits;
            unsigned int val;
        } region2_scl_offset;
        union { // name: region3_mst_ctl, offset: 0xa0
            struct {
                unsigned int region3_mst_en       : 1;
                unsigned int region3_data_fmt     : 5;
                unsigned int reserve_0            : 2;
                unsigned int region3_yrgb_2gt     : 1;
                unsigned int region3_yrgb_4gt     : 1;
                unsigned int region3_cbcr_2gt     : 1;
                unsigned int region3_cbcr_4gt     : 1;
                unsigned int region3_dither_up_en : 1;
                unsigned int region3_alpha_swap   : 1;
                unsigned int region3_rb_swap      : 1;
                unsigned int region3_mid_swap     : 1;
                unsigned int region3_uv_swap      : 1;
                unsigned int region3_yuv_clip     : 1;
                unsigned int region3_rg_swap      : 1;
                unsigned int reserve_1            : 1;
                unsigned int region3_avg_en       : 1;
                unsigned int region3_xgt_en       : 1;
                unsigned int region3_xgt_mode     : 2;
                unsigned int reserve_2            : 8;
            } bits;
            unsigned int val;
        } region3_mst_ctl;
        union { // name: region3_mst_yrgb, offset: 0xa4
            struct {
                unsigned int region3_yrgb_mst : 32;
            } bits;
            unsigned int val;
        } region3_mst_yrgb;
        union { // name: region3_mst_cbcr, offset: 0xa8
            struct {
                unsigned int region3_cbcr_mst : 32;
            } bits;
            unsigned int val;
        } region3_mst_cbcr;
        union { // name: region3_vir, offset: 0xac
            struct {
                unsigned int region3_vir_stride    : 16;
                unsigned int region3_vir_stride_uv : 16;
            } bits;
            unsigned int val;
        } region3_vir;
        union { // name: region3_act_info, offset: 0xb0
            struct {
                unsigned int region3_act_width  : 13;
                unsigned int reserve_0          : 3;
                unsigned int region3_act_heigth : 13;
                unsigned int reserve_1          : 3;
            } bits;
            unsigned int val;
        } region3_act_info;
        union { // name: region3_dsp_info, offset: 0xb4
            struct {
                unsigned int region3_dsp_width  : 13;
                unsigned int reserve_0          : 3;
                unsigned int region3_dsp_height : 13;
                unsigned int reserve_1          : 3;
            } bits;
            unsigned int val;
        } region3_dsp_info;
        union { // name: region3_dsp_offset, offset: 0xb8
            struct {
                unsigned int region3_dsp_xoff : 13;
                unsigned int reserve_0        : 3;
                unsigned int region3_dsp_yoff : 13;
                unsigned int reserve_1        : 3;
            } bits;
            unsigned int val;
        } region3_dsp_offset;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_188_192;
        union { // name: region3_scl_ctrl, offset: 0xc0
            struct {
                unsigned int region3_yrgb_xsu_en    : 1;
                unsigned int region3_yrgb_xsd_en    : 1;
                unsigned int region3_yrgb_xscl_mode : 2;
                unsigned int region3_yrgb_ysu_en    : 1;
                unsigned int region3_yrgb_ysd_en    : 1;
                unsigned int region3_yrgb_yscl_mode : 2;
                unsigned int reserve_0              : 8;
                unsigned int region3_xsu_bic_mode   : 2;
                unsigned int reserve_1              : 14;
            } bits;
            unsigned int val;
        } region3_scl_ctrl;
        union { // name: region3_scl_factor_yrgb, offset: 0xc4
            struct {
                unsigned int region3_yrgb_xfactor : 16;
                unsigned int region3_yrgb_yfactor : 16;
            } bits;
            unsigned int val;
        } region3_scl_factor_yrgb;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_200_204;
        union { // name: region3_scl_offset, offset: 0xcc
            struct {
                unsigned int region3_yrgb_xscl_offset : 8;
                unsigned int region3_yrgb_yscl_offset : 8;
                unsigned int reserve_0                : 16;
            } bits;
            unsigned int val;
        } region3_scl_offset;
        union { // name: esmart_key_ctrl, offset: 0xd0
            struct {
                unsigned int esmart_b_key_value : 10;
                unsigned int esmart_g_key_value : 10;
                unsigned int esmart_r_key_value : 10;
                unsigned int reserve_0          : 1;
                unsigned int esmart_key_en      : 1;
            } bits;
            unsigned int val;
        } esmart_key_ctrl;
        union { // name: esmart_bg_en, offset: 0xd4
            struct {
                unsigned int esmart_b_value : 10;
                unsigned int esmart_g_value : 10;
                unsigned int esmart_r_value : 10;
                unsigned int reserve_0      : 1;
                unsigned int esmart_bg_en   : 1;
            } bits;
            unsigned int val;
        } esmart_bg_en;
        union { // name: esmart_alpha_map, offset: 0xd8
            struct {
                unsigned int alpha_0_map  : 8;
                unsigned int alpha_1_map  : 8;
                unsigned int reserve_0    : 15;
                unsigned int alpha_map_en : 1;
            } bits;
            unsigned int val;
        } esmart_alpha_map;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_220_224;
        union { // name: esmart_crc_en, offset: 0xe0
            struct {
                unsigned int crc_en    : 1;
                unsigned int reserve_0 : 31;
            } bits;
            unsigned int val;
        } esmart_crc_en;
        union { // name: esmart_crc_status, offset: 0xe4
            struct {
                unsigned int Field000 : 32;
            } bits;
            unsigned int val;
        } esmart_crc_status;
        struct {
            unsigned int reserve_data[3];
        } reserve_reg_232_244;
        union { // name: esmart_port_sel_imd, offset: 0xf4
            struct {
                unsigned int esmart_port_sel : 2;
                unsigned int reserve_0       : 30;
            } bits;
            unsigned int val;
        } esmart_port_sel_imd;
        union { // name: esmart_dly_num, offset: 0xf8
            struct {
                unsigned int esmart_dly_num : 8;
                unsigned int reserve_0      : 24;
            } bits;
            unsigned int val;
        } esmart_dly_num;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_252_256;
        union { // name: esmart_csc_coe01_00, offset: 0x100
            struct {
                unsigned int sw_win_csc_coe00 : 16;
                unsigned int sw_win_csc_coe01 : 16;
            } bits;
            unsigned int val;
        } esmart_csc_coe01_00;
        union { // name: esmart_csc_coe10_02, offset: 0x104
            struct {
                unsigned int sw_win_csc_coe02 : 16;
                unsigned int sw_win_csc_coe10 : 16;
            } bits;
            unsigned int val;
        } esmart_csc_coe10_02;
        union { // name: esmart_csc_coe12_11, offset: 0x108
            struct {
                unsigned int sw_win_csc_coe11 : 16;
                unsigned int sw_win_csc_coe12 : 16;
            } bits;
            unsigned int val;
        } esmart_csc_coe12_11;
        union { // name: esmart_csc_coe21_20, offset: 0x10c
            struct {
                unsigned int sw_win_csc_coe20 : 16;
                unsigned int sw_win_csc_coe21 : 16;
            } bits;
            unsigned int val;
        } esmart_csc_coe21_20;
        union { // name: esmart_csc_coe22, offset: 0x110
            struct {
                unsigned int sw_win_csc_coe22 : 16;
                unsigned int reserve_0        : 16;
            } bits;
            unsigned int val;
        } esmart_csc_coe22;
        union { // name: esmart_csc_offset0, offset: 0x114
            struct {
                unsigned int sw_win_csc_offset0 : 32;
            } bits;
            unsigned int val;
        } esmart_csc_offset0;
        union { // name: esmart_csc_offset1, offset: 0x118
            struct {
                unsigned int sw_win_csc_offset1 : 32;
            } bits;
            unsigned int val;
        } esmart_csc_offset1;
        union { // name: esmart_csc_offset2, offset: 0x11c
            struct {
                unsigned int sw_win_csc_offset2 : 32;
            } bits;
            unsigned int val;
        } esmart_csc_offset2;
        struct {
            unsigned int reserve_data[55];
        } reserve_reg_288_508;
        union { // name: esmart_cfg_done, offset: 0x1fc
            struct {
                unsigned int reg_load_cluster_en : 1;
                unsigned int reserve_0           : 31;
            } bits;
            unsigned int val;
        } esmart_cfg_done;
    } regs;
    unsigned int data[128];
} esmart2_rk3538_u;

// 0x00002000
typedef union hdr_vivid_rk3538 {
    struct {
        union { // name: lut_ctrl, offset: 0x0
            struct {
                unsigned int hdr_lut_update_en : 1;
                unsigned int hdr_lut_mode      : 1;
                unsigned int reserve_0         : 30;
            } bits;
            unsigned int val;
        } lut_ctrl;
        union { // name: lut_mst, offset: 0x4
            struct {
                unsigned int hdr_lut_mst : 32;
            } bits;
            unsigned int val;
        } lut_mst;
        union { // name: lut_status, offset: 0x8
            struct {
                unsigned int hdr_lut_fetch_done : 1;
                unsigned int reserve_0          : 31;
            } bits;
            unsigned int val;
        } lut_status;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_12_16;
        union { // name: sdr2hdr_ctrl, offset: 0x10
            struct {
                unsigned int sdr2hdr_en        : 1;
                unsigned int sdr2hdr_gating_en : 1;
                unsigned int sdr2hdr_bypass_en : 1;
                unsigned int reserve_0         : 29;
            } bits;
            unsigned int val;
        } sdr2hdr_ctrl;
        union { // name: sdr_cfg_coe0, offset: 0x14
            struct {
                unsigned int sdr_s_fix : 12;
                unsigned int reserve_0 : 4;
                unsigned int sdr_r_fix : 12;
                unsigned int reserve_1 : 4;
            } bits;
            unsigned int val;
        } sdr_cfg_coe0;
        union { // name: sdr_cfg_coe1, offset: 0x18
            struct {
                unsigned int sdr_t_fix : 14;
                unsigned int reserve_0 : 18;
            } bits;
            unsigned int val;
        } sdr_cfg_coe1;
        union { // name: sdr_csc_coe00_01, offset: 0x1c
            struct {
                unsigned int coe00 : 16;
                unsigned int coe01 : 16;
            } bits;
            unsigned int val;
        } sdr_csc_coe00_01;
        union { // name: sdr_csc_coe02_10, offset: 0x20
            struct {
                unsigned int coe02 : 16;
                unsigned int coe10 : 16;
            } bits;
            unsigned int val;
        } sdr_csc_coe02_10;
        union { // name: sdr_csc_coe11_12, offset: 0x24
            struct {
                unsigned int coe11 : 16;
                unsigned int coe12 : 16;
            } bits;
            unsigned int val;
        } sdr_csc_coe11_12;
        union { // name: sdr_csc_coe20_21, offset: 0x28
            struct {
                unsigned int coe20 : 16;
                unsigned int coe21 : 16;
            } bits;
            unsigned int val;
        } sdr_csc_coe20_21;
        union { // name: sdr_csc_coe22, offset: 0x2c
            struct {
                unsigned int coe22     : 16;
                unsigned int reserve_0 : 16;
            } bits;
            unsigned int val;
        } sdr_csc_coe22;
        struct {
            unsigned int reserve_data[4];
        } reserve_reg_48_64;
        union { // name: hdrvivid_ctrl, offset: 0x40
            struct {
                unsigned int hdrvivid_en        : 1;
                unsigned int hdrvivid_gating_en : 1;
                unsigned int hdrvivid_bypass_en : 1;
                unsigned int path_mode          : 3;
                unsigned int dstgamut           : 1;
                unsigned int reserve            : 1;
                unsigned int pqmode_max_y       : 1;
                unsigned int sca_bypass_en      : 1;
                unsigned int reserve_0          : 22;
            } bits;
            unsigned int val;
        } hdrvivid_ctrl;
        union { // name: hdrvivid_pq_gamma, offset: 0x44
            struct {
                unsigned int pq_gamma_b : 8;
                unsigned int reserve_0  : 8;
                unsigned int pq_gamma_k : 11;
                unsigned int reserve_1  : 5;
            } bits;
            unsigned int val;
        } hdrvivid_pq_gamma;
        union { // name: hlg_rfix_scalefac, offset: 0x48
            struct {
                unsigned int r_fix     : 12;
                unsigned int reserve_0 : 4;
                unsigned int scalefac  : 10;
                unsigned int reserve_1 : 6;
            } bits;
            unsigned int val;
        } hlg_rfix_scalefac;
        union { // name: hlg_maxluma, offset: 0x4c
            struct {
                unsigned int maxdstluma : 12;
                unsigned int reserve_0  : 4;
                unsigned int maxsetluma : 12;
                unsigned int reserve_1  : 4;
            } bits;
            unsigned int val;
        } hlg_maxluma;
        union { // name: hlg_r_tm_lin2non, offset: 0x50
            struct {
                unsigned int r_tm_lin2non : 10;
                unsigned int reserve_0    : 22;
            } bits;
            unsigned int val;
        } hlg_r_tm_lin2non;
        union { // name: hdrvivid_csc_coe00_01, offset: 0x54
            struct {
                unsigned int coe00 : 16;
                unsigned int coe01 : 16;
            } bits;
            unsigned int val;
        } hdrvivid_csc_coe00_01;
        union { // name: hdrvivid_csc_coe02_10, offset: 0x58
            struct {
                unsigned int coe02 : 16;
                unsigned int coe10 : 16;
            } bits;
            unsigned int val;
        } hdrvivid_csc_coe02_10;
        union { // name: hdrvivid_csc_coe11_12, offset: 0x5c
            struct {
                unsigned int coe11 : 16;
                unsigned int coe12 : 16;
            } bits;
            unsigned int val;
        } hdrvivid_csc_coe11_12;
        union { // name: hdrvivid_csc_coe20_21, offset: 0x60
            struct {
                unsigned int coe20 : 16;
                unsigned int coe21 : 16;
            } bits;
            unsigned int val;
        } hdrvivid_csc_coe20_21;
        union { // name: hdrvivid_csc_coe22, offset: 0x64
            struct {
                unsigned int coe22     : 16;
                unsigned int reserve_0 : 16;
            } bits;
            unsigned int val;
        } hdrvivid_csc_coe22;
        struct {
            unsigned int reserve_data[6];
        } reserve_reg_104_128;
        union { // name: ink_cfg, offset: 0x80
            struct {
                unsigned int reserve_0  : 15;
                unsigned int sw_dbg_en  : 1;
                unsigned int reserve_1  : 12;
                unsigned int sw_dbg_sel : 4;
            } bits;
            unsigned int val;
        } ink_cfg;
        union { // name: ink_point0_cfg, offset: 0x84
            struct {
                unsigned int sw_point0_h : 12;
                unsigned int reserve_0   : 4;
                unsigned int sw_point0_v : 12;
                unsigned int reserve_1   : 4;
            } bits;
            unsigned int val;
        } ink_point0_cfg;
        union { // name: ink_point1_cfg, offset: 0x88
            struct {
                unsigned int sw_point1_h : 12;
                unsigned int reserve_0   : 4;
                unsigned int sw_point1_v : 12;
                unsigned int reserve_1   : 4;
            } bits;
            unsigned int val;
        } ink_point1_cfg;
        union { // name: ink_point0_r0, offset: 0x8c
            struct {
                unsigned int ink_point0_r0 : 24;
                unsigned int reserve_0     : 8;
            } bits;
            unsigned int val;
        } ink_point0_r0;
        union { // name: ink_point0_g0, offset: 0x90
            struct {
                unsigned int ink_point0_g0 : 24;
                unsigned int reserve_0     : 8;
            } bits;
            unsigned int val;
        } ink_point0_g0;
        union { // name: ink_point0_b0, offset: 0x94
            struct {
                unsigned int ink_point0_b0 : 24;
                unsigned int reserve_0     : 8;
            } bits;
            unsigned int val;
        } ink_point0_b0;
        union { // name: ink_point0_r1, offset: 0x98
            struct {
                unsigned int ink_point0_r1 : 24;
                unsigned int reserve_0     : 8;
            } bits;
            unsigned int val;
        } ink_point0_r1;
        union { // name: ink_point0_g1, offset: 0x9c
            struct {
                unsigned int ink_point0_g1 : 24;
                unsigned int reserve_0     : 8;
            } bits;
            unsigned int val;
        } ink_point0_g1;
        union { // name: ink_point0_b1, offset: 0xa0
            struct {
                unsigned int ink_point0_b1 : 24;
                unsigned int reserve_0     : 8;
            } bits;
            unsigned int val;
        } ink_point0_b1;
        union { // name: ink_point1_r0, offset: 0xa4
            struct {
                unsigned int ink_point0_r0 : 24;
                unsigned int reserve_0     : 8;
            } bits;
            unsigned int val;
        } ink_point1_r0;
        union { // name: ink_point1_g0, offset: 0xa8
            struct {
                unsigned int ink_point1_g0 : 24;
                unsigned int reserve_0     : 8;
            } bits;
            unsigned int val;
        } ink_point1_g0;
        union { // name: ink_point1_b0, offset: 0xac
            struct {
                unsigned int ink_point1_b0 : 24;
                unsigned int reserve_0     : 8;
            } bits;
            unsigned int val;
        } ink_point1_b0;
        union { // name: ink_point1_r1, offset: 0xb0
            struct {
                unsigned int ink_point1_r1 : 24;
                unsigned int reserve_0     : 8;
            } bits;
            unsigned int val;
        } ink_point1_r1;
        union { // name: ink_point1_g1, offset: 0xb4
            struct {
                unsigned int ink_point1_g1 : 24;
                unsigned int reserve_0     : 8;
            } bits;
            unsigned int val;
        } ink_point1_g1;
        union { // name: ink_point1_b1, offset: 0xb8
            struct {
                unsigned int ink_point1_b1 : 24;
                unsigned int reserve_0     : 8;
            } bits;
            unsigned int val;
        } ink_point1_b1;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_188_192;
        union { // name: cgc_ctrl, offset: 0xc0
            struct {
                unsigned int cgc_en        : 1;
                unsigned int cgc_gating_en : 1;
                unsigned int cgc_bypass_en : 1;
                unsigned int reserve_0     : 29;
            } bits;
            unsigned int val;
        } cgc_ctrl;
        union { // name: cgc_cfg_coe0, offset: 0xc4
            struct {
                unsigned int cgc_s_fix : 12;
                unsigned int reserve_0 : 4;
                unsigned int cgc_r_fix : 12;
                unsigned int reserve_1 : 4;
            } bits;
            unsigned int val;
        } cgc_cfg_coe0;
        union { // name: cgc_cfg_coe1, offset: 0xc8
            struct {
                unsigned int cgc_t_fix : 14;
                unsigned int reserve_0 : 18;
            } bits;
            unsigned int val;
        } cgc_cfg_coe1;
        union { // name: cgc_csc_coe00_01, offset: 0xcc
            struct {
                unsigned int coe00 : 16;
                unsigned int coe01 : 16;
            } bits;
            unsigned int val;
        } cgc_csc_coe00_01;
        union { // name: cgc_csc_coe02_10, offset: 0xd0
            struct {
                unsigned int coe02 : 16;
                unsigned int coe10 : 16;
            } bits;
            unsigned int val;
        } cgc_csc_coe02_10;
        union { // name: cgc_csc_coe11_12, offset: 0xd4
            struct {
                unsigned int coe11 : 16;
                unsigned int coe12 : 16;
            } bits;
            unsigned int val;
        } cgc_csc_coe11_12;
        union { // name: cgc_csc_coe20_21, offset: 0xd8
            struct {
                unsigned int coe20 : 16;
                unsigned int coe21 : 16;
            } bits;
            unsigned int val;
        } cgc_csc_coe20_21;
        union { // name: cgc_csc_coe22, offset: 0xdc
            struct {
                unsigned int coe22     : 16;
                unsigned int reserve_0 : 16;
            } bits;
            unsigned int val;
        } cgc_csc_coe22;
        struct {
            unsigned int reserve_data[23];
        } reserve_reg_224_316;
        union { // name: hdrvivid_tone_sca, offset: 0x13c
            struct {
                unsigned int addr      : 1;
                unsigned int reserve_0 : 31;
            } bits;
            unsigned int val;
        } hdrvivid_tone_sca;
        struct {
            unsigned int reserve_data[256];
        } reserve_reg_320_1344;
        union { // name: hdrvividgamma_curve, offset: 0x540
            struct {
                unsigned int addr      : 1;
                unsigned int reserve_0 : 31;
            } bits;
            unsigned int val;
        } hdrvividgamma_curve;
        struct {
            unsigned int reserve_data[83];
        } reserve_reg_1348_1680;
        union { // name: hdrvividgamma_mdfvalue, offset: 0x690
            struct {
                unsigned int addr      : 1;
                unsigned int reserve_0 : 31;
            } bits;
            unsigned int val;
        } hdrvividgamma_mdfvalue;
        struct {
            unsigned int reserve_data[27];
        } reserve_reg_1684_1792;
        union { // name: sdrinvgamma_curve, offset: 0x700
            struct {
                unsigned int addr      : 1;
                unsigned int reserve_0 : 31;
            } bits;
            unsigned int val;
        } sdrinvgamma_curve;
        struct {
            unsigned int reserve_data[71];
        } reserve_reg_1796_2080;
        union { // name: sdrinvgamma_startidx, offset: 0x820
            struct {
                unsigned int addr      : 1;
                unsigned int reserve_0 : 31;
            } bits;
            unsigned int val;
        } sdrinvgamma_startidx;
        struct {
            unsigned int reserve_data[7];
        } reserve_reg_2084_2112;
        union { // name: sdrinvgamma_changeidx, offset: 0x840
            struct {
                unsigned int addr      : 1;
                unsigned int reserve_0 : 31;
            } bits;
            unsigned int val;
        } sdrinvgamma_changeidx;
        struct {
            unsigned int reserve_data[47];
        } reserve_reg_2116_2304;
        union { // name: sdroeft_curve, offset: 0x900
            struct {
                unsigned int addr      : 1;
                unsigned int reserve_0 : 31;
            } bits;
            unsigned int val;
        } sdroeft_curve;
        struct {
            unsigned int reserve_data[127];
        } reserve_reg_2308_2816;
        union { // name: cgcinvgamma_curve, offset: 0xb00
            struct {
                unsigned int addr      : 1;
                unsigned int reserve_0 : 31;
            } bits;
            unsigned int val;
        } cgcinvgamma_curve;
        struct {
            unsigned int reserve_data[71];
        } reserve_reg_2820_3104;
        union { // name: cgcinvgamma_startidx, offset: 0xc20
            struct {
                unsigned int addr      : 1;
                unsigned int reserve_0 : 31;
            } bits;
            unsigned int val;
        } cgcinvgamma_startidx;
        struct {
            unsigned int reserve_data[7];
        } reserve_reg_3108_3136;
        union { // name: cgcinvgamma_changeidx, offset: 0xc40
            struct {
                unsigned int addr      : 1;
                unsigned int reserve_0 : 31;
            } bits;
            unsigned int val;
        } cgcinvgamma_changeidx;
        struct {
            unsigned int reserve_data[47];
        } reserve_reg_3140_3328;
        union { // name: cgcoeft_curve, offset: 0xd00
            struct {
                unsigned int addr      : 1;
                unsigned int reserve_0 : 31;
            } bits;
            unsigned int val;
        } cgcoeft_curve;
    } regs;
    unsigned int data[833];
} hdr_vivid_rk3538_u;

// 0x00003800
typedef union cursor0_rk3538 {
    struct {
        union { // name: cursor_ctrl0, offset: 0x0
            struct {
                unsigned int cursor_csc_en        : 1;
                unsigned int reserve_0            : 30;
                unsigned int cursor_frm_resetn_en : 1;
            } bits;
            unsigned int val;
        } cursor_ctrl0;
        union { // name: cursor_ctrl1, offset: 0x4
            struct {
                unsigned int cursor_axi_rlen   : 2;
                unsigned int cursor_gather_en  : 1;
                unsigned int reserve_0         : 1;
                unsigned int cursor_rid        : 5;
                unsigned int reserve_1         : 11;
                unsigned int cursor_gather_num : 4;
                unsigned int reserve_2         : 7;
                unsigned int cursor_ymir_en    : 1;
            } bits;
            unsigned int val;
        } cursor_ctrl1;
        union { // name: cursor_axi_ctrl_imd, offset: 0x8
            struct {
                unsigned int cursor_dma_sop         : 1;
                unsigned int cursor_axi_sel         : 1;
                unsigned int reserve_0              : 1;
                unsigned int cursor_outstanding_en  : 1;
                unsigned int cursor_outstanding_num : 4;
                unsigned int cursor_auto_gating_en  : 1;
                unsigned int reserve_1              : 7;
                unsigned int cursor_dma_4k_addr_opt : 1;
                unsigned int cursor_err_stop_en     : 1;
                unsigned int reserve_2              : 14;
            } bits;
            unsigned int val;
        } cursor_axi_ctrl_imd;
        union { // name: cursor_mst_ctl, offset: 0xc
            struct {
                unsigned int cursor_en           : 1;
                unsigned int cursor_data_fmt     : 4;
                unsigned int cursor_argb5551_en  : 1;
                unsigned int reserve_0           : 4;
                unsigned int cursor_dither_up_en : 1;
                unsigned int cursor_alpha_swap   : 1;
                unsigned int cursor_rb_swap      : 1;
                unsigned int cursor_mid_swap     : 1;
                unsigned int cursor_rg_swap      : 1;
                unsigned int cursor_alpha_map_en : 1;
                unsigned int cursor_alpha_0_map  : 8;
                unsigned int cursor_alpha_1_map  : 1;
                unsigned int reserve_1           : 7;
            } bits;
            unsigned int val;
        } cursor_mst_ctl;
        union { // name: cursor_mst, offset: 0x10
            struct {
                unsigned int cursor_mst : 32;
            } bits;
            unsigned int val;
        } cursor_mst;
        union { // name: cursor_vir, offset: 0x14
            struct {
                unsigned int cursor_vir_stride : 16;
                unsigned int reserve_0         : 16;
            } bits;
            unsigned int val;
        } cursor_vir;
        union { // name: cursor_size_info, offset: 0x18
            struct {
                unsigned int cursor_width  : 13;
                unsigned int reserve_0     : 3;
                unsigned int cursor_heigth : 13;
                unsigned int reserve_1     : 3;
            } bits;
            unsigned int val;
        } cursor_size_info;
        union { // name: cursor_dsp_offset, offset: 0x1c
            struct {
                unsigned int cursor_dsp_xoff : 13;
                unsigned int reserve_0       : 3;
                unsigned int cursor_dsp_yoff : 13;
                unsigned int reserve_1       : 3;
            } bits;
            unsigned int val;
        } cursor_dsp_offset;
        union { // name: cursor_key_ctrl, offset: 0x20
            struct {
                unsigned int cursor_b_key_value : 10;
                unsigned int cursor_g_key_value : 10;
                unsigned int cursor_r_key_value : 10;
                unsigned int reserve_0          : 1;
                unsigned int cursor_key_en      : 1;
            } bits;
            unsigned int val;
        } cursor_key_ctrl;
        union { // name: cursor_bg_en, offset: 0x24
            struct {
                unsigned int cursor_b_value : 10;
                unsigned int cursor_g_value : 10;
                unsigned int cursor_r_value : 10;
                unsigned int reserve_0      : 1;
                unsigned int cursor_bg_en   : 1;
            } bits;
            unsigned int val;
        } cursor_bg_en;
        union { // name: cursor_port_sel_imd, offset: 0x28
            struct {
                unsigned int cursor_port_sel : 2;
                unsigned int reserve_0       : 30;
            } bits;
            unsigned int val;
        } cursor_port_sel_imd;
        union { // name: cursor_dly_num, offset: 0x2c
            struct {
                unsigned int cursor_dly_num : 8;
                unsigned int reserve_0      : 24;
            } bits;
            unsigned int val;
        } cursor_dly_num;
        union { // name: cursor_csc_coe00_01, offset: 0x30
            struct {
                unsigned int sw_csc_coe00 : 16;
                unsigned int sw_csc_coe01 : 16;
            } bits;
            unsigned int val;
        } cursor_csc_coe00_01;
        union { // name: cursor_csc_coe02_10, offset: 0x34
            struct {
                unsigned int sw_csc_coe02 : 16;
                unsigned int sw_csc_coe10 : 1;
                unsigned int reserve_0    : 15;
            } bits;
            unsigned int val;
        } cursor_csc_coe02_10;
        union { // name: cursor_csc_coe11_12, offset: 0x38
            struct {
                unsigned int sw_csc_coe11 : 16;
                unsigned int sw_csc_coe12 : 16;
            } bits;
            unsigned int val;
        } cursor_csc_coe11_12;
        union { // name: cursor_csc_coe20_21, offset: 0x3c
            struct {
                unsigned int sw_csc_coe20 : 16;
                unsigned int sw_csc_coe21 : 16;
            } bits;
            unsigned int val;
        } cursor_csc_coe20_21;
        union { // name: cursor_csc_coe22, offset: 0x40
            struct {
                unsigned int sw_csc_coe22 : 16;
                unsigned int reserve_0    : 16;
            } bits;
            unsigned int val;
        } cursor_csc_coe22;
        union { // name: cursor_csc_offset0, offset: 0x44
            struct {
                unsigned int sw_csc_offset0 : 32;
            } bits;
            unsigned int val;
        } cursor_csc_offset0;
        union { // name: cursor_csc_offset1, offset: 0x48
            struct {
                unsigned int sw_csc_offset1 : 32;
            } bits;
            unsigned int val;
        } cursor_csc_offset1;
        union { // name: cursor_csc_offset2, offset: 0x4c
            struct {
                unsigned int sw_csc_offset2 : 32;
            } bits;
            unsigned int val;
        } cursor_csc_offset2;
        struct {
            unsigned int reserve_data[11];
        } reserve_reg_80_124;
        union { // name: cursor_cfg_done, offset: 0x7c
            struct {
                unsigned int win_cfg_done_en : 1;
                unsigned int reserve_0       : 31;
            } bits;
            unsigned int val;
        } cursor_cfg_done;
    } regs;
    unsigned int data[32];
} cursor0_rk3538_u;

// 0x00006400
typedef union acm_rk3538 {
    struct {
        union { // name: acm_ctrl, offset: 0x0
            struct {
                unsigned int acm_en         : 1;
                unsigned int acm_bypass     : 1;
                unsigned int debug_en       : 1;
                unsigned int reserve_0      : 1;
                unsigned int debug_data_sel : 3;
                unsigned int reserve_1      : 1;
                unsigned int acm_width      : 12;
                unsigned int acm_height     : 12;
            } bits;
            unsigned int val;
        } acm_ctrl;
        union { // name: delta_range, offset: 0x4
            struct {
                unsigned int y_gain    : 10;
                unsigned int h_gain    : 10;
                unsigned int s_gain    : 10;
                unsigned int reserve_0 : 2;
            } bits;
            unsigned int val;
        } delta_range;
        union { // name: fetch_start, offset: 0x8
            struct {
                unsigned int fetch_start : 1;
                unsigned int reserve_0   : 31;
            } bits;
            unsigned int val;
        } fetch_start;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_12_16;
        union { // name: debug_point0_cfg, offset: 0x10
            struct {
                unsigned int point0_h  : 12;
                unsigned int reserve_0 : 4;
                unsigned int point0_v  : 12;
                unsigned int reserve_1 : 4;
            } bits;
            unsigned int val;
        } debug_point0_cfg;
        union { // name: debug_point1_cfg, offset: 0x14
            struct {
                unsigned int point1_h  : 12;
                unsigned int reserve_0 : 4;
                unsigned int point1_v  : 12;
                unsigned int reserve_1 : 4;
            } bits;
            unsigned int val;
        } debug_point1_cfg;
        union { // name: debug_point2_cfg, offset: 0x18
            struct {
                unsigned int point2_h  : 12;
                unsigned int reserve_0 : 4;
                unsigned int point2_v  : 12;
                unsigned int reserve_1 : 4;
            } bits;
            unsigned int val;
        } debug_point2_cfg;
        union { // name: debug_point3_cfg, offset: 0x1c
            struct {
                unsigned int point3_h  : 12;
                unsigned int reserve_0 : 4;
                unsigned int point3_v  : 12;
                unsigned int reserve_1 : 4;
            } bits;
            unsigned int val;
        } debug_point3_cfg;
        union { // name: fetch_done, offset: 0x20
            struct {
                unsigned int fetch_done : 1;
                unsigned int reserve_0  : 31;
            } bits;
            unsigned int val;
        } fetch_done;
        struct {
            unsigned int reserve_data[3];
        } reserve_reg_36_48;
        union { // name: debug0_data0, offset: 0x30
            struct {
                unsigned int debug0_data0 : 32;
            } bits;
            unsigned int val;
        } debug0_data0;
        union { // name: debug0_data1, offset: 0x34
            struct {
                unsigned int debug0_data1 : 32;
            } bits;
            unsigned int val;
        } debug0_data1;
        union { // name: debug0_data2, offset: 0x38
            struct {
                unsigned int debug0_data2 : 32;
            } bits;
            unsigned int val;
        } debug0_data2;
        union { // name: debug0_data3, offset: 0x3c
            struct {
                unsigned int debug0_data3 : 32;
            } bits;
            unsigned int val;
        } debug0_data3;
        union { // name: debug1_data0, offset: 0x40
            struct {
                unsigned int debug1_data0 : 32;
            } bits;
            unsigned int val;
        } debug1_data0;
        union { // name: debug1_data1, offset: 0x44
            struct {
                unsigned int debug1_data1 : 32;
            } bits;
            unsigned int val;
        } debug1_data1;
        union { // name: debug1_data2, offset: 0x48
            struct {
                unsigned int debug1_data2 : 32;
            } bits;
            unsigned int val;
        } debug1_data2;
        union { // name: debug1_data3, offset: 0x4c
            struct {
                unsigned int debug1_data3 : 32;
            } bits;
            unsigned int val;
        } debug1_data3;
        union { // name: debug2_data0, offset: 0x50
            struct {
                unsigned int debug2_data0 : 32;
            } bits;
            unsigned int val;
        } debug2_data0;
        union { // name: debug2_data1, offset: 0x54
            struct {
                unsigned int debug2_data1 : 32;
            } bits;
            unsigned int val;
        } debug2_data1;
        union { // name: debug2_data2, offset: 0x58
            struct {
                unsigned int debug2_data2 : 32;
            } bits;
            unsigned int val;
        } debug2_data2;
        union { // name: debug2_data3, offset: 0x5c
            struct {
                unsigned int debug2_data3 : 32;
            } bits;
            unsigned int val;
        } debug2_data3;
        union { // name: debug3_data0, offset: 0x60
            struct {
                unsigned int debug3_data0 : 32;
            } bits;
            unsigned int val;
        } debug3_data0;
        union { // name: debug3_data1, offset: 0x64
            struct {
                unsigned int debug3_data1 : 32;
            } bits;
            unsigned int val;
        } debug3_data1;
        union { // name: debug3_data2, offset: 0x68
            struct {
                unsigned int debug3_data2 : 32;
            } bits;
            unsigned int val;
        } debug3_data2;
        union { // name: debug3_data3, offset: 0x6c
            struct {
                unsigned int debug3_data3 : 32;
            } bits;
            unsigned int val;
        } debug3_data3;
        struct {
            unsigned int reserve_data[36];
        } reserve_reg_112_256;
        union { // name: yhs_gain_by_y_seg0, offset: 0x100
            struct {
                unsigned int ygain_y_0 : 8;
                unsigned int hgain_y_0 : 8;
                unsigned int sgain_y_0 : 8;
                unsigned int reserve_0 : 8;
            } bits;
            unsigned int val;
        } yhs_gain_by_y_seg0;
        struct {
            unsigned int reserve_data[151];
        } reserve_reg_260_864;
        union { // name: yhs_gain_by_y_seg152, offset: 0x360
            struct {
                unsigned int ygain_y_152 : 8;
                unsigned int hgain_y_152 : 8;
                unsigned int sgain_y_152 : 8;
                unsigned int reserve_0   : 8;
            } bits;
            unsigned int val;
        } yhs_gain_by_y_seg152;
        union { // name: yhs_gain_by_s_seg0, offset: 0x364
            struct {
                unsigned int ygain_s_0 : 8;
                unsigned int hgain_s_0 : 8;
                unsigned int sgain_s_0 : 8;
                unsigned int reserve_0 : 8;
            } bits;
            unsigned int val;
        } yhs_gain_by_s_seg0;
        struct {
            unsigned int reserve_data[219];
        } reserve_reg_872_1748;
        union { // name: yhs_gain_by_s_seg220, offset: 0x6d4
            struct {
                unsigned int ygain_s_220 : 8;
                unsigned int hgain_s_220 : 8;
                unsigned int sgain_s_220 : 8;
                unsigned int reserve_0   : 8;
            } bits;
            unsigned int val;
        } yhs_gain_by_s_seg220;
        union { // name: yhs_del_by_h_seg0, offset: 0x6d8
            struct {
                unsigned int ydel_h_0  : 10;
                unsigned int reserve_0 : 2;
                unsigned int hdel_h_0  : 8;
                unsigned int sdel_h_0  : 10;
                unsigned int reserve_1 : 2;
            } bits;
            unsigned int val;
        } yhs_del_by_h_seg0;
        struct {
            unsigned int reserve_data[63];
        } reserve_reg_1756_2008;
        union { // name: yhs_del_by_h_seg64, offset: 0x7d8
            struct {
                unsigned int ydel_h_64 : 10;
                unsigned int reserve_0 : 2;
                unsigned int hdel_h_64 : 8;
                unsigned int sdel_h_64 : 10;
                unsigned int reserve_1 : 2;
            } bits;
            unsigned int val;
        } yhs_del_by_h_seg64;
    } regs;
    unsigned int data[503];
} acm_rk3538_u;

// 0x00006c00
typedef union sharp_rk3538 {
    struct {
        union { // name: ctrl, offset: 0x0
            struct {
                unsigned int sw_sharp_enable        : 1;
                unsigned int reserve_0              : 2;
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
                unsigned int reserve_0                 : 3;
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
                unsigned int sw_peaking_h00 : 5;
                unsigned int reserve_0      : 3;
                unsigned int sw_peaking_h01 : 7;
                unsigned int reserve_1      : 1;
                unsigned int sw_peaking_h02 : 9;
                unsigned int reserve_2      : 7;
            } bits;
            unsigned int val;
        } peaking_filter_coe2;
        union { // name: peaking_filter_coe3, offset: 0x14
            struct {
                unsigned int sw_peaking_h03 : 10;
                unsigned int sw_peaking_h04 : 11;
                unsigned int sw_peaking_h05 : 10;
                unsigned int reserve_0      : 1;
            } bits;
            unsigned int val;
        } peaking_filter_coe3;
        union { // name: peaking_filter_coe4, offset: 0x18
            struct {
                unsigned int sw_peaking_h10 : 5;
                unsigned int reserve_0      : 3;
                unsigned int sw_peaking_h11 : 7;
                unsigned int reserve_1      : 1;
                unsigned int sw_peaking_h12 : 9;
                unsigned int reserve_2      : 7;
            } bits;
            unsigned int val;
        } peaking_filter_coe4;
        union { // name: peaking_filter_coe5, offset: 0x1c
            struct {
                unsigned int sw_peaking_h13 : 10;
                unsigned int sw_peaking_h14 : 11;
                unsigned int sw_peaking_h15 : 10;
                unsigned int reserve_0      : 1;
            } bits;
            unsigned int val;
        } peaking_filter_coe5;
        union { // name: peaking_filter_coe6, offset: 0x20
            struct {
                unsigned int sw_peaking_h20 : 5;
                unsigned int reserve_0      : 3;
                unsigned int sw_peaking_h21 : 7;
                unsigned int reserve_1      : 1;
                unsigned int sw_peaking_h22 : 9;
                unsigned int reserve_2      : 7;
            } bits;
            unsigned int val;
        } peaking_filter_coe6;
        union { // name: peaking_filter_coe7, offset: 0x24
            struct {
                unsigned int sw_peaking_h23 : 10;
                unsigned int sw_peaking_h24 : 11;
                unsigned int sw_peaking_h25 : 10;
                unsigned int reserve_0      : 1;
            } bits;
            unsigned int val;
        } peaking_filter_coe7;
        union { // name: peaking_filter_coe8, offset: 0x28
            struct {
                unsigned int sw_peaking_h30 : 5;
                unsigned int reserve_0      : 3;
                unsigned int sw_peaking_h31 : 7;
                unsigned int reserve_1      : 1;
                unsigned int sw_peaking_h32 : 9;
                unsigned int reserve_2      : 7;
            } bits;
            unsigned int val;
        } peaking_filter_coe8;
        union { // name: peaking_filter_coe9, offset: 0x2c
            struct {
                unsigned int sw_peaking_h33 : 10;
                unsigned int sw_peaking_h34 : 11;
                unsigned int sw_peaking_h35 : 10;
                unsigned int reserve_0      : 1;
            } bits;
            unsigned int val;
        } peaking_filter_coe9;
        union { // name: peaking0_ctrl_coe0, offset: 0x30
            struct {
                unsigned int sw_peaking0_idx_n0 : 11;
                unsigned int reserve_0          : 5;
                unsigned int sw_peaking0_idx_n1 : 11;
                unsigned int reserve_1          : 5;
            } bits;
            unsigned int val;
        } peaking0_ctrl_coe0;
        union { // name: peaking0_ctrl_coe1, offset: 0x34
            struct {
                unsigned int sw_peaking0_idx_n2 : 11;
                unsigned int reserve_0          : 5;
                unsigned int sw_peaking0_idx_n3 : 11;
                unsigned int reserve_1          : 5;
            } bits;
            unsigned int val;
        } peaking0_ctrl_coe1;
        union { // name: peaking0_ctrl_coe2, offset: 0x38
            struct {
                unsigned int sw_peaking0_idx_p0 : 11;
                unsigned int reserve_0          : 5;
                unsigned int sw_peaking0_idx_p1 : 11;
                unsigned int reserve_1          : 5;
            } bits;
            unsigned int val;
        } peaking0_ctrl_coe2;
        union { // name: peaking0_ctrl_coe3, offset: 0x3c
            struct {
                unsigned int sw_peaking0_idx_p2 : 11;
                unsigned int reserve_0          : 5;
                unsigned int sw_peaking0_idx_p3 : 11;
                unsigned int reserve_1          : 5;
            } bits;
            unsigned int val;
        } peaking0_ctrl_coe3;
        union { // name: peaking0_ctrl_coe4, offset: 0x40
            struct {
                unsigned int sw_peaking0_value_n1 : 11;
                unsigned int reserve_0            : 5;
                unsigned int sw_peaking0_value_n2 : 11;
                unsigned int reserve_1            : 5;
            } bits;
            unsigned int val;
        } peaking0_ctrl_coe4;
        union { // name: peaking0_ctrl_coe5, offset: 0x44
            struct {
                unsigned int sw_peaking0_value_n3 : 11;
                unsigned int reserve_0            : 5;
                unsigned int sw_peaking0_value_p1 : 11;
                unsigned int reserve_1            : 5;
            } bits;
            unsigned int val;
        } peaking0_ctrl_coe5;
        union { // name: peaking0_ctrl_coe6, offset: 0x48
            struct {
                unsigned int sw_peaking0_value_p2 : 11;
                unsigned int reserve_0            : 5;
                unsigned int sw_peaking0_value_p3 : 11;
                unsigned int reserve_1            : 5;
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
                unsigned int sw_peaking1_idx_n0 : 11;
                unsigned int reserve_0          : 5;
                unsigned int sw_peaking1_idx_n1 : 11;
                unsigned int reserve_1          : 5;
            } bits;
            unsigned int val;
        } peaking1_ctrl_coe0;
        union { // name: peaking1_ctrl_coe1, offset: 0x60
            struct {
                unsigned int sw_peaking1_idx_n2 : 11;
                unsigned int reserve_0          : 5;
                unsigned int sw_peaking1_idx_n3 : 11;
                unsigned int reserve_1          : 5;
            } bits;
            unsigned int val;
        } peaking1_ctrl_coe1;
        union { // name: peaking1_ctrl_coe2, offset: 0x64
            struct {
                unsigned int sw_peaking1_idx_p0 : 11;
                unsigned int reserve_0          : 5;
                unsigned int sw_peaking1_idx_p1 : 11;
                unsigned int reserve_1          : 5;
            } bits;
            unsigned int val;
        } peaking1_ctrl_coe2;
        union { // name: peaking1_ctrl_coe3, offset: 0x68
            struct {
                unsigned int sw_peaking1_idx_p2 : 11;
                unsigned int reserve_0          : 5;
                unsigned int sw_peaking1_idx_p3 : 11;
                unsigned int reserve_1          : 5;
            } bits;
            unsigned int val;
        } peaking1_ctrl_coe3;
        union { // name: peaking1_ctrl_coe4, offset: 0x6c
            struct {
                unsigned int sw_peaking1_value_n1 : 11;
                unsigned int reserve_0            : 5;
                unsigned int sw_peaking1_value_n2 : 11;
                unsigned int reserve_1            : 5;
            } bits;
            unsigned int val;
        } peaking1_ctrl_coe4;
        union { // name: peaking1_ctrl_coe5, offset: 0x70
            struct {
                unsigned int sw_peaking1_value_n3 : 11;
                unsigned int reserve_0            : 5;
                unsigned int sw_peaking1_value_p1 : 11;
                unsigned int reserve_1            : 5;
            } bits;
            unsigned int val;
        } peaking1_ctrl_coe5;
        union { // name: peaking1_ctrl_coe6, offset: 0x74
            struct {
                unsigned int sw_peaking1_value_p2 : 11;
                unsigned int reserve_0            : 5;
                unsigned int sw_peaking1_value_p3 : 11;
                unsigned int reserve_1            : 5;
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
                unsigned int sw_peaking2_idx_n0 : 11;
                unsigned int reserve_0          : 5;
                unsigned int sw_peaking2_idx_n1 : 11;
                unsigned int reserve_1          : 5;
            } bits;
            unsigned int val;
        } peaking2_ctrl_coe0;
        union { // name: peaking2_ctrl_coe1, offset: 0x8c
            struct {
                unsigned int sw_peaking2_idx_n2 : 11;
                unsigned int reserve_0          : 5;
                unsigned int sw_peaking2_idx_n3 : 11;
                unsigned int reserve_1          : 5;
            } bits;
            unsigned int val;
        } peaking2_ctrl_coe1;
        union { // name: peaking2_ctrl_coe2, offset: 0x90
            struct {
                unsigned int sw_peaking2_idx_p0 : 11;
                unsigned int reserve_0          : 5;
                unsigned int sw_peaking2_idx_p1 : 11;
                unsigned int reserve_1          : 5;
            } bits;
            unsigned int val;
        } peaking2_ctrl_coe2;
        union { // name: peaking2_ctrl_coe3, offset: 0x94
            struct {
                unsigned int sw_peaking2_idx_p2 : 11;
                unsigned int reserve_0          : 5;
                unsigned int sw_peaking2_idx_p3 : 11;
                unsigned int reserve_1          : 5;
            } bits;
            unsigned int val;
        } peaking2_ctrl_coe3;
        union { // name: peaking2_ctrl_coe4, offset: 0x98
            struct {
                unsigned int sw_peaking2_value_n1 : 11;
                unsigned int reserve_0            : 5;
                unsigned int sw_peaking2_value_n2 : 11;
                unsigned int reserve_1            : 5;
            } bits;
            unsigned int val;
        } peaking2_ctrl_coe4;
        union { // name: peaking2_ctrl_coe5, offset: 0x9c
            struct {
                unsigned int sw_peaking2_value_n3 : 11;
                unsigned int reserve_0            : 5;
                unsigned int sw_peaking2_value_p1 : 11;
                unsigned int reserve_1            : 5;
            } bits;
            unsigned int val;
        } peaking2_ctrl_coe5;
        union { // name: peaking2_ctrl_coe6, offset: 0xa0
            struct {
                unsigned int sw_peaking2_value_p2 : 11;
                unsigned int reserve_0            : 5;
                unsigned int sw_peaking2_value_p3 : 11;
                unsigned int reserve_1            : 5;
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
                unsigned int sw_peaking3_idx_n0 : 11;
                unsigned int reserve_0          : 5;
                unsigned int sw_peaking3_idx_n1 : 11;
                unsigned int reserve_1          : 5;
            } bits;
            unsigned int val;
        } peaking3_ctrl_coe0;
        union { // name: peaking3_ctrl_coe1, offset: 0xb8
            struct {
                unsigned int sw_peaking3_idx_n2 : 11;
                unsigned int reserve_0          : 5;
                unsigned int sw_peaking3_idx_n3 : 11;
                unsigned int reserve_1          : 5;
            } bits;
            unsigned int val;
        } peaking3_ctrl_coe1;
        union { // name: peaking3_ctrl_coe2, offset: 0xbc
            struct {
                unsigned int sw_peaking3_idx_p0 : 11;
                unsigned int reserve_0          : 5;
                unsigned int sw_peaking3_idx_p1 : 11;
                unsigned int reserve_1          : 5;
            } bits;
            unsigned int val;
        } peaking3_ctrl_coe2;
        union { // name: peaking3_ctrl_coe3, offset: 0xc0
            struct {
                unsigned int sw_peaking3_idx_p2 : 11;
                unsigned int reserve_0          : 5;
                unsigned int sw_peaking3_idx_p3 : 11;
                unsigned int reserve_1          : 5;
            } bits;
            unsigned int val;
        } peaking3_ctrl_coe3;
        union { // name: peaking3_ctrl_coe4, offset: 0xc4
            struct {
                unsigned int sw_peaking3_value_n1 : 11;
                unsigned int reserve_0            : 5;
                unsigned int sw_peaking3_value_n2 : 11;
                unsigned int reserve_1            : 5;
            } bits;
            unsigned int val;
        } peaking3_ctrl_coe4;
        union { // name: peaking3_ctrl_coe5, offset: 0xc8
            struct {
                unsigned int sw_peaking3_value_n3 : 11;
                unsigned int reserve_0            : 5;
                unsigned int sw_peaking3_value_p1 : 11;
                unsigned int reserve_1            : 5;
            } bits;
            unsigned int val;
        } peaking3_ctrl_coe5;
        union { // name: peaking3_ctrl_coe6, offset: 0xcc
            struct {
                unsigned int sw_peaking3_value_p2 : 11;
                unsigned int reserve_0            : 5;
                unsigned int sw_peaking3_value_p3 : 11;
                unsigned int reserve_1            : 5;
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
                unsigned int sw_peaking4_idx_n0 : 11;
                unsigned int reserve_0          : 5;
                unsigned int sw_peaking4_idx_n1 : 11;
                unsigned int reserve_1          : 5;
            } bits;
            unsigned int val;
        } peaking4_ctrl_coe0;
        union { // name: peaking4_ctrl_coe1, offset: 0xe4
            struct {
                unsigned int sw_peaking4_idx_n2 : 11;
                unsigned int reserve_0          : 5;
                unsigned int sw_peaking4_idx_n3 : 11;
                unsigned int reserve_1          : 5;
            } bits;
            unsigned int val;
        } peaking4_ctrl_coe1;
        union { // name: peaking4_ctrl_coe2, offset: 0xe8
            struct {
                unsigned int sw_peaking4_idx_p0 : 11;
                unsigned int reserve_0          : 5;
                unsigned int sw_peaking4_idx_p1 : 11;
                unsigned int reserve_1          : 5;
            } bits;
            unsigned int val;
        } peaking4_ctrl_coe2;
        union { // name: peaking4_ctrl_coe3, offset: 0xec
            struct {
                unsigned int sw_peaking4_idx_p2 : 11;
                unsigned int reserve_0          : 5;
                unsigned int sw_peaking4_idx_p3 : 11;
                unsigned int reserve_1          : 5;
            } bits;
            unsigned int val;
        } peaking4_ctrl_coe3;
        union { // name: peaking4_ctrl_coe4, offset: 0xf0
            struct {
                unsigned int sw_peaking4_value_n1 : 11;
                unsigned int reserve_0            : 5;
                unsigned int sw_peaking4_value_n2 : 11;
                unsigned int reserve_1            : 5;
            } bits;
            unsigned int val;
        } peaking4_ctrl_coe4;
        union { // name: peaking4_ctrl_coe5, offset: 0xf4
            struct {
                unsigned int sw_peaking4_value_n3 : 11;
                unsigned int reserve_0            : 5;
                unsigned int sw_peaking4_value_p1 : 11;
                unsigned int reserve_1            : 5;
            } bits;
            unsigned int val;
        } peaking4_ctrl_coe5;
        union { // name: peaking4_ctrl_coe6, offset: 0xf8
            struct {
                unsigned int sw_peaking4_value_p2 : 11;
                unsigned int reserve_0            : 5;
                unsigned int sw_peaking4_value_p3 : 11;
                unsigned int reserve_1            : 5;
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
                unsigned int sw_peaking5_idx_n0 : 11;
                unsigned int reserve_0          : 5;
                unsigned int sw_peaking5_idx_n1 : 11;
                unsigned int reserve_1          : 5;
            } bits;
            unsigned int val;
        } peaking5_ctrl_coe0;
        union { // name: peaking5_ctrl_coe1, offset: 0x110
            struct {
                unsigned int sw_peaking5_idx_n2 : 11;
                unsigned int reserve_0          : 5;
                unsigned int sw_peaking5_idx_n3 : 11;
                unsigned int reserve_1          : 5;
            } bits;
            unsigned int val;
        } peaking5_ctrl_coe1;
        union { // name: peaking5_ctrl_coe2, offset: 0x114
            struct {
                unsigned int sw_peaking5_idx_p0 : 11;
                unsigned int reserve_0          : 5;
                unsigned int sw_peaking5_idx_p1 : 11;
                unsigned int reserve_1          : 5;
            } bits;
            unsigned int val;
        } peaking5_ctrl_coe2;
        union { // name: peaking5_ctrl_coe3, offset: 0x118
            struct {
                unsigned int sw_peaking5_idx_p2 : 11;
                unsigned int reserve_0          : 5;
                unsigned int sw_peaking5_idx_p3 : 11;
                unsigned int reserve_1          : 5;
            } bits;
            unsigned int val;
        } peaking5_ctrl_coe3;
        union { // name: peaking5_ctrl_coe4, offset: 0x11c
            struct {
                unsigned int sw_peaking5_value_n1 : 11;
                unsigned int reserve_0            : 5;
                unsigned int sw_peaking5_value_n2 : 11;
                unsigned int reserve_1            : 5;
            } bits;
            unsigned int val;
        } peaking5_ctrl_coe4;
        union { // name: peaking5_ctrl_coe5, offset: 0x120
            struct {
                unsigned int sw_peaking5_value_n3 : 11;
                unsigned int reserve_0            : 5;
                unsigned int sw_peaking5_value_p1 : 11;
                unsigned int reserve_1            : 5;
            } bits;
            unsigned int val;
        } peaking5_ctrl_coe5;
        union { // name: peaking5_ctrl_coe6, offset: 0x124
            struct {
                unsigned int sw_peaking5_value_p2 : 11;
                unsigned int reserve_0            : 5;
                unsigned int sw_peaking5_value_p3 : 11;
                unsigned int reserve_1            : 5;
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
                unsigned int sw_peaking6_idx_n0 : 11;
                unsigned int reserve_0          : 5;
                unsigned int sw_peaking6_idx_n1 : 11;
                unsigned int reserve_1          : 5;
            } bits;
            unsigned int val;
        } peaking6_ctrl_coe0;
        union { // name: peaking6_ctrl_coe1, offset: 0x13c
            struct {
                unsigned int sw_peaking6_idx_n2 : 11;
                unsigned int reserve_0          : 5;
                unsigned int sw_peaking6_idx_n3 : 11;
                unsigned int reserve_1          : 5;
            } bits;
            unsigned int val;
        } peaking6_ctrl_coe1;
        union { // name: peaking6_ctrl_coe2, offset: 0x140
            struct {
                unsigned int sw_peaking6_idx_p0 : 11;
                unsigned int reserve_0          : 5;
                unsigned int sw_peaking6_idx_p1 : 11;
                unsigned int reserve_1          : 5;
            } bits;
            unsigned int val;
        } peaking6_ctrl_coe2;
        union { // name: peaking6_ctrl_coe3, offset: 0x144
            struct {
                unsigned int sw_peaking6_idx_p2 : 11;
                unsigned int reserve_0          : 5;
                unsigned int sw_peaking6_idx_p3 : 11;
                unsigned int reserve_1          : 5;
            } bits;
            unsigned int val;
        } peaking6_ctrl_coe3;
        union { // name: peaking6_ctrl_coe4, offset: 0x148
            struct {
                unsigned int sw_peaking6_value_n1 : 11;
                unsigned int reserve_0            : 5;
                unsigned int sw_peaking6_value_n2 : 11;
                unsigned int reserve_1            : 5;
            } bits;
            unsigned int val;
        } peaking6_ctrl_coe4;
        union { // name: peaking6_ctrl_coe5, offset: 0x14c
            struct {
                unsigned int sw_peaking6_value_n3 : 11;
                unsigned int reserve_0            : 5;
                unsigned int sw_peaking6_value_p1 : 11;
                unsigned int reserve_1            : 5;
            } bits;
            unsigned int val;
        } peaking6_ctrl_coe5;
        union { // name: peaking6_ctrl_coe6, offset: 0x150
            struct {
                unsigned int sw_peaking6_value_p2 : 11;
                unsigned int reserve_0            : 5;
                unsigned int sw_peaking6_value_p3 : 11;
                unsigned int reserve_1            : 5;
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
            unsigned int reserve_data[1];
        } reserve_reg_352_356;
        union { // name: peaking7_ctrl_coe0, offset: 0x164
            struct {
                unsigned int sw_peaking7_idx_n0 : 11;
                unsigned int reserve_0          : 5;
                unsigned int sw_peaking7_idx_n1 : 11;
                unsigned int reserve_1          : 5;
            } bits;
            unsigned int val;
        } peaking7_ctrl_coe0;
        union { // name: peaking7_ctrl_coe1, offset: 0x168
            struct {
                unsigned int sw_peaking7_idx_n2 : 11;
                unsigned int reserve_0          : 5;
                unsigned int sw_peaking7_idx_n3 : 11;
                unsigned int reserve_1          : 5;
            } bits;
            unsigned int val;
        } peaking7_ctrl_coe1;
        union { // name: peaking7_ctrl_coe2, offset: 0x16c
            struct {
                unsigned int sw_peaking7_idx_p0 : 11;
                unsigned int reserve_0          : 5;
                unsigned int sw_peaking7_idx_p1 : 11;
                unsigned int reserve_1          : 5;
            } bits;
            unsigned int val;
        } peaking7_ctrl_coe2;
        union { // name: peaking7_ctrl_coe3, offset: 0x170
            struct {
                unsigned int sw_peaking7_idx_p2 : 11;
                unsigned int reserve_0          : 5;
                unsigned int sw_peaking7_idx_p3 : 11;
                unsigned int reserve_1          : 5;
            } bits;
            unsigned int val;
        } peaking7_ctrl_coe3;
        union { // name: peaking7_ctrl_coe4, offset: 0x174
            struct {
                unsigned int sw_peaking7_value_n1 : 11;
                unsigned int reserve_0            : 5;
                unsigned int sw_peaking7_value_n2 : 11;
                unsigned int reserve_1            : 5;
            } bits;
            unsigned int val;
        } peaking7_ctrl_coe4;
        union { // name: peaking7_ctrl_coe5, offset: 0x178
            struct {
                unsigned int sw_peaking7_value_n3 : 11;
                unsigned int reserve_0            : 5;
                unsigned int sw_peaking7_value_p1 : 11;
                unsigned int reserve_1            : 5;
            } bits;
            unsigned int val;
        } peaking7_ctrl_coe5;
        union { // name: peaking7_ctrl_coe6, offset: 0x17c
            struct {
                unsigned int sw_peaking7_value_p2 : 11;
                unsigned int reserve_0            : 5;
                unsigned int sw_peaking7_value_p3 : 11;
                unsigned int reserve_1            : 5;
            } bits;
            unsigned int val;
        } peaking7_ctrl_coe6;
        union { // name: peaking7_ctrl_coe7, offset: 0x180
            struct {
                unsigned int sw_peaking7_ratio_n01 : 12;
                unsigned int reserve_0             : 4;
                unsigned int sw_peaking7_ratio_n12 : 12;
                unsigned int reserve_1             : 4;
            } bits;
            unsigned int val;
        } peaking7_ctrl_coe7;
        union { // name: peaking7_ctrl_coe8, offset: 0x184
            struct {
                unsigned int sw_peaking7_ratio_n23 : 12;
                unsigned int reserve_0             : 4;
                unsigned int sw_peaking7_ratio_p01 : 12;
                unsigned int reserve_1             : 4;
            } bits;
            unsigned int val;
        } peaking7_ctrl_coe8;
        union { // name: peaking7_ctrl_coe9, offset: 0x188
            struct {
                unsigned int sw_peaking7_ratio_p12 : 12;
                unsigned int sw_peaking7_ratio_p23 : 12;
                unsigned int reserve_0             : 8;
            } bits;
            unsigned int val;
        } peaking7_ctrl_coe9;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_396_400;
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
                unsigned int sw_adp_idx0 : 10;
                unsigned int sw_adp_idx1 : 10;
                unsigned int sw_adp_idx2 : 10;
                unsigned int reserve_0   : 2;
            } bits;
            unsigned int val;
        } gain_ctrl0;
        union { // name: gain_ctrl1, offset: 0x1c4
            struct {
                unsigned int sw_adp_idx3  : 10;
                unsigned int reserve_0    : 2;
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
                unsigned int sw_var_idx0  : 10;
                unsigned int sw_var_idx1  : 10;
                unsigned int reserve_0    : 1;
            } bits;
            unsigned int val;
        } gain_ctrl5;
        union { // name: gain_ctrl6, offset: 0x208
            struct {
                unsigned int sw_var_idx2  : 10;
                unsigned int reserve_0    : 2;
                unsigned int sw_var_idx3  : 10;
                unsigned int reserve_1    : 2;
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
                unsigned int sw_lum_idx0   : 10;
                unsigned int reserve_2     : 2;
            } bits;
            unsigned int val;
        } gain_ctrl10;
        union { // name: gain_ctrl11, offset: 0x21c
            struct {
                unsigned int sw_lum_idx1 : 10;
                unsigned int sw_lum_idx2 : 10;
                unsigned int sw_lum_idx3 : 10;
                unsigned int reserve_0   : 2;
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
                unsigned int sw_tex_idx0       : 10;
                unsigned int reserve_1         : 2;
                unsigned int sw_tex_idx1       : 10;
                unsigned int reserve_2         : 6;
            } bits;
            unsigned int val;
        } texture_ctrl0;
        union { // name: texture_ctrl1, offset: 0x274
            struct {
                unsigned int sw_tex_idx2  : 10;
                unsigned int reserve_0    : 2;
                unsigned int sw_tex_idx3  : 10;
                unsigned int reserve_1    : 2;
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
        struct {
            unsigned int reserve_data[8];
        } reserve_reg_648_680;
        union { // name: dbg_ctrl0, offset: 0x2a8
            struct {
                unsigned int sw_debug_mode : 4;
                unsigned int reserve_0     : 28;
            } bits;
            unsigned int val;
        } dbg_ctrl0;
        union { // name: roi_ctrl0, offset: 0x2ac
            struct {
                unsigned int sw_roi_xstart : 12;
                unsigned int reserve_0     : 4;
                unsigned int sw_roi_ystart : 12;
                unsigned int reserve_1     : 3;
                unsigned int sw_roi_en     : 1;
            } bits;
            unsigned int val;
        } roi_ctrl0;
        union { // name: roi_ctrl1, offset: 0x2b0
            struct {
                unsigned int sw_roi_xend : 12;
                unsigned int reserve_0   : 4;
                unsigned int sw_roi_yend : 12;
                unsigned int reserve_1   : 4;
            } bits;
            unsigned int val;
        } roi_ctrl1;
    } regs;
    unsigned int data[173];
} sharp_rk3538_u;

// 0x00007e00
typedef union mmu0_rk3538 {
    struct {
        union { // name: dte_addr, offset: 0x0
            struct {
                unsigned int reserve_0       : 12;
                unsigned int MMU_DTE_ADDR    : 20;
                unsigned int MMU_DTE_ADDR_H  : 8;
            } bits;
            unsigned int val;
        } dte_addr;
        union { // name: status, offset: 0x4
            struct {
                unsigned int PAGING_ENABLED       : 1;
                unsigned int PAGE_FAULT_ACTIVE    : 1;
                unsigned int STAIL_ACTIVE         : 1;
                unsigned int MMU_IDLE             : 1;
                unsigned int REPLAY_BUFFER_EMPTY  : 1;
                unsigned int PAGE_FAULT_IS_WRITE  : 1;
                unsigned int PAGE_FAULT_BUS_ID    : 6;
                unsigned int PAGE_FAULT_MST       : 2;
                unsigned int reserve_0            : 6;
                unsigned int PAGE_FAULT_TYPE      : 3;
                unsigned int reserve_1            : 5;
                unsigned int FSM_STATE            : 4;
            } bits;
            unsigned int val;
        } status;
        union { // name: command, offset: 0x8
            struct {
                unsigned int MMU_CMD   : 3;
                unsigned int reserve_0 : 29;
            } bits;
            unsigned int val;
        } command;
        union { // name: page_fault_addr, offset: 0xc
            struct {
                unsigned int PAGE_FAULT_ADDR : 32;
            } bits;
            unsigned int val;
        } page_fault_addr;
        union { // name: zap_one_line, offset: 0x10
            struct {
                unsigned int MMU_ZAP_ONE_LINE : 32;
            } bits;
            unsigned int val;
        } zap_one_line;
        union { // name: int_rawstat , offset: 0x14
            struct {
                unsigned int PAGE_FAULT           : 1;
                unsigned int READ_BUS_ERROR       : 1;
                unsigned int PAGE_FAULT1          : 1;
                unsigned int reserve_0            : 13;
                unsigned int PAGE_FAULT_FAKE_MST0 : 1;
                unsigned int PAGE_FAULT_FAKE_MST1 : 1;
                unsigned int reserve_1            : 14;
            } bits;
            unsigned int val;
        } int_rawstat ;
        union { // name: int_clear, offset: 0x18
            struct {
                unsigned int PAGE_FAULT           : 1;
                unsigned int READ_BUS_ERROR       : 1;
                unsigned int PAGE_FAULT1          : 1;
                unsigned int reserve_0            : 13;
                unsigned int PAGE_FAULT_FAKE_MST0 : 1;
                unsigned int PAGE_FAULT_FAKE_MST1 : 1;
                unsigned int reserve_1            : 14;
            } bits;
            unsigned int val;
        } int_clear;
        union { // name: int_mask , offset: 0x1c
            struct {
                unsigned int PAGE_FAULT           : 1;
                unsigned int READ_BUS_ERROR       : 1;
                unsigned int PAGE_FAULT1          : 1;
                unsigned int reserve_0            : 13;
                unsigned int PAGE_FAULT_FAKE_MST0 : 1;
                unsigned int PAGE_FAULT_FAKE_MST1 : 1;
                unsigned int reserve_1            : 14;
            } bits;
            unsigned int val;
        } int_mask ;
        union { // name: int_status, offset: 0x20
            struct {
                unsigned int PAGE_FAULT           : 1;
                unsigned int READ_BUS_ERROR       : 1;
                unsigned int PAGE_FAULT1          : 1;
                unsigned int reserve_0            : 13;
                unsigned int PAGE_FAULT_FAKE_MST0 : 1;
                unsigned int PAGE_FAULT_FAKE_MST1 : 1;
                unsigned int reserve_1            : 14;
            } bits;
            unsigned int val;
        } int_status;
        union { // name: auto_gating, offset: 0x24
            struct {
                unsigned int MMU_AUTO_GATING       : 1;
                unsigned int MMU_LOOKUP_GATING     : 1;
                unsigned int RESET_MODE            : 1;
                unsigned int CLK_MMU_EN_FORCE      : 1;
                unsigned int CLK_MMU_DISABLE_FORCE : 1;
                unsigned int reserve_0             : 27;
            } bits;
            unsigned int val;
        } auto_gating;
        struct {
            unsigned int reserve_data[2];
        } reserve_reg_40_48;
        union { // name: blcok_config, offset: 0x30
            struct {
                unsigned int BIG_PAGE_SIZE : 16;
                unsigned int reserve_0     : 16;
            } bits;
            unsigned int val;
        } blcok_config;
        union { // name: bypass_fix_ids, offset: 0x34
            struct {
                unsigned int BYPASS_FIX_ID0 : 8;
                unsigned int BYPASS_FIX_ID1 : 8;
                unsigned int BYPASS_FIX_ID2 : 8;
                unsigned int BYPASS_FIX_ID3 : 8;
            } bits;
            unsigned int val;
        } bypass_fix_ids;
        union { // name: zap_mst, offset: 0x38
            struct {
                unsigned int ZAP_EN    : 1;
                unsigned int MST_SEL   : 1;
                unsigned int reserve_0 : 30;
            } bits;
            unsigned int val;
        } zap_mst;
        union { // name: bypass, offset: 0x3c
            struct {
                unsigned int BYPASS_EN0         : 1;
                unsigned int BYPASS_EN1         : 1;
                unsigned int reserve_0          : 5;
                unsigned int BYPASS_EN_LARGE_ID : 1;
                unsigned int BYPASS_EN_FIX_ID0  : 1;
                unsigned int BYPASS_EN_FIX_ID1  : 1;
                unsigned int BYPASS_EN_FIX_ID2  : 1;
                unsigned int BYPASS_EN_FIX_ID3  : 1;
                unsigned int reserve_1          : 4;
                unsigned int BYPASS_LARGER_ID   : 16;
            } bits;
            unsigned int val;
        } bypass;
        union { // name: invalid, offset: 0x40
            struct {
                unsigned int MODE       : 2;
                unsigned int UPDATE_MST : 1;
                unsigned int reserve_0  : 29;
            } bits;
            unsigned int val;
        } invalid;
        union { // name: page_fault, offset: 0x44
            struct {
                unsigned int MST0_DONE           : 1;
                unsigned int MST1_DONE           : 1;
                unsigned int reserve_0           : 6;
                unsigned int STALL               : 1;
                unsigned int reserve_1           : 7;
                unsigned int PF_VAL_SLV_BRESP    : 2;
                unsigned int PF_VAL_SLV_RRESP    : 2;
                unsigned int PF_VAL_SLV_BRESP_EN : 1;
                unsigned int PF_VAL_SLV_RRESP_EN : 1;
                unsigned int PF_VAL_MST_WSTRB    : 1;
                unsigned int PF_FAKE_ADDR_EN     : 1;
                unsigned int PF_FAKE_MODE        : 1;
                unsigned int PF_WSTRB_EN         : 1;
                unsigned int reserve_2           : 6;
            } bits;
            unsigned int val;
        } page_fault;
        union { // name: fake_addr, offset: 0x48
            struct {
                unsigned int FAKE_ADDR_HIGH32 : 32;
            } bits;
            unsigned int val;
        } fake_addr;
        struct {
            unsigned int reserve_data[5];
        } reserve_reg_76_96;
        union { // name: status1, offset: 0x60
            struct {
                unsigned int FSM_STATE    : 4;
                unsigned int IFIFO_EMPTY  : 1;
                unsigned int OFIFO_EMPTY  : 1;
                unsigned int RFIFO_EMPTY  : 1;
                unsigned int PGFIFO_EMPTY : 1;
                unsigned int IFIFO_FULL   : 1;
                unsigned int OFIFO_FULL   : 1;
                unsigned int RPFIFO_FULL  : 1;
                unsigned int PGFIFO_FULL  : 1;
                unsigned int CORE_EMPTY   : 1;
                unsigned int READ_ERROR   : 1;
                unsigned int reserve_0    : 17;
                unsigned int BUS_IDLE     : 1;
            } bits;
            unsigned int val;
        } status1;
        union { // name: bus_done_ctrl, offset: 0x64
            struct {
                unsigned int WRAXI_EN_BCH_DONE              : 1;
                unsigned int WRAXI_EN_WCH_DONE              : 1;
                unsigned int BUS_DONE_ERR_CLR               : 1;
                unsigned int BUS_DONE_WR_FIFO_CLR           : 1;
                unsigned int BUS_DONE_AXIRD_ENABLE_FORCERST : 1;
                unsigned int BUS_DONE_AXIWR_ENABLE_FORCERST : 1;
                unsigned int BUS_DONE_AXIRD_ENABLE          : 1;
                unsigned int BUS_DONE_AXIWR_ENABLE          : 1;
                unsigned int BUS_DONE_AXIRD_PERMIT          : 1;
                unsigned int BUS_DONE_AXIWR_PERMIT          : 1;
                unsigned int reserve_0                      : 21;
                unsigned int BUS_DONE_AXI_WSTRB             : 1;
            } bits;
            unsigned int val;
        } bus_done_ctrl;
        union { // name: bus_done_timeout_cnt, offset: 0x68
            struct {
                unsigned int BUS_DONE_TIMEOUT_COUNTER : 32;
            } bits;
            unsigned int val;
        } bus_done_timeout_cnt;
        union { // name: bus_done_status, offset: 0x6c
            struct {
                unsigned int BUS_DONE_FIFO_EMPTY : 1;
                unsigned int BUS_DONE_FIFO_FULL  : 1;
                unsigned int MON_AXI_READ_IDLE   : 1;
                unsigned int MON_AXI_WRITE_IDLE  : 1;
                unsigned int reserve_0           : 28;
            } bits;
            unsigned int val;
        } bus_done_status;
        union { // name: tlb_config, offset: 0x70
            struct {
                unsigned int PAGE_COMMON : 1;
                unsigned int reserve_0   : 3;
                unsigned int PTE_SIZE    : 8;
                unsigned int MMU_TLB_WR  : 1;
                unsigned int reserve_1   : 19;
            } bits;
            unsigned int val;
        } tlb_config;
        union { // name: tlb_config_0, offset: 0x74
            struct {
                unsigned int PTE_START : 8;
                unsigned int PTE_SIZE  : 8;
                unsigned int DTE_START : 8;
                unsigned int DTE_SIZE  : 8;
            } bits;
            unsigned int val;
        } tlb_config_0;
        union { // name: tlb_config_1, offset: 0x78
            struct {
                unsigned int PTE_START : 8;
                unsigned int PTE_SIZE  : 8;
                unsigned int DTE_START : 8;
                unsigned int DTE_SIZE  : 8;
            } bits;
            unsigned int val;
        } tlb_config_1;
        struct {
            unsigned int reserve_data[13];
        } reserve_reg_124_176;
        union { // name: mon_perf_cnt_send, offset: 0xb0
            struct {
                unsigned int PERF_CRU_CNT_SEND : 16;
                unsigned int reserve_0         : 16;
            } bits;
            unsigned int val;
        } mon_perf_cnt_send;
        union { // name: mon_perf_cnt_miss_dte, offset: 0xb4
            struct {
                unsigned int PERI_AVG_CNT_MISS_DTE : 16;
                unsigned int PERI_CUR_CNT_MISS_DTE : 16;
            } bits;
            unsigned int val;
        } mon_perf_cnt_miss_dte;
        union { // name: mon_perf_cnt_miss_pte, offset: 0xb8
            struct {
                unsigned int PERI_AVG_CNT_MISS_PTE : 16;
                unsigned int PERI_CUR_CNT_MISS_PTE : 16;
            } bits;
            unsigned int val;
        } mon_perf_cnt_miss_pte;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_188_192;
        union { // name: mon_cmd, offset: 0xc0
            struct {
                unsigned int MON_ENTRY_ADDR        : 6;
                unsigned int reserve_0             : 10;
                unsigned int MON_TLB_ADDR          : 7;
                unsigned int MON_PERF_CLR          : 1;
                unsigned int MON_PERF_EMPYT_CLR_EN : 1;
                unsigned int MON_PERF_SEND_EN      : 1;
                unsigned int reserve_1             : 5;
                unsigned int MON_TLB_ADDR_EN       : 1;
            } bits;
            unsigned int val;
        } mon_cmd;
        union { // name: mon_entry_rdata, offset: 0xc4
            struct {
                unsigned int MON_CACHE_TAGS    : 24;
                unsigned int MON_LRU_ENTRY_VAL : 6;
                unsigned int reserve_0         : 2;
            } bits;
            unsigned int val;
        } mon_entry_rdata;
        union { // name: mon_perf, offset: 0xc8
            struct {
                unsigned int reserve_0           : 16;
                unsigned int MON_PERF_THROUGHPUT : 16;
                unsigned int MON_PERF_LATENCY    : 16;
            } bits;
            unsigned int val;
        } mon_perf;
        union { // name: mon_perf_send_num, offset: 0xcc
            struct {
                unsigned int PERF_SEND_NUM : 16;
                unsigned int reserve_0     : 16;
            } bits;
            unsigned int val;
        } mon_perf_send_num;
        union { // name: mon_tlb_rdata0, offset: 0xd0
            struct {
                unsigned int MON_TLB_RDATA0 : 32;
            } bits;
            unsigned int val;
        } mon_tlb_rdata0;
        union { // name: mon_tlb_rdata1, offset: 0xd4
            struct {
                unsigned int MON_TLB_RDATA1 : 32;
            } bits;
            unsigned int val;
        } mon_tlb_rdata1;
        union { // name: mon_tlb_rdata2, offset: 0xd8
            struct {
                unsigned int MON_TLB_RDATA2 : 32;
            } bits;
            unsigned int val;
        } mon_tlb_rdata2;
        union { // name: mon_tlb_rdata3, offset: 0xdc
            struct {
                unsigned int MON_TLB_RDATA3 : 32;
            } bits;
            unsigned int val;
        } mon_tlb_rdata3;
        union { // name: dbg_set1, offset: 0xe0
            struct {
                unsigned int DbgErrClr               : 1;
                unsigned int MmuBypassPageRch        : 1;
                unsigned int PageFaultPipeLineEnable : 1;
                unsigned int AxiPageSecure           : 1;
                unsigned int reserve_0               : 28;
            } bits;
            unsigned int val;
        } dbg_set1;
        union { // name: dbg_set2, offset: 0xe4
            struct {
                unsigned int ReplayFifoWaterMark : 8;
                unsigned int PageVaFifoWaterMark : 8;
                unsigned int reserve_0           : 16;
            } bits;
            unsigned int val;
        } dbg_set2;
        union { // name: dbg_err, offset: 0xe8
            struct {
                unsigned int ErrPageData        : 1;
                unsigned int ErrDteTagHits      : 1;
                unsigned int ErrPteTagHits      : 1;
                unsigned int ErrArPa            : 1;
                unsigned int ErrAwPa            : 1;
                unsigned int reserve_0          : 11;
                unsigned int ErrLruPteRange     : 1;
                unsigned int ErrLruDteRange     : 1;
                unsigned int ErrLruPteZero      : 1;
                unsigned int ErrLruDteZero      : 1;
                unsigned int ErrLruPteOneHotOrg : 1;
                unsigned int ErrLruDteOneHotOrg : 1;
                unsigned int ErrLruPteOneHot    : 1;
                unsigned int ErrLruDteOneHot    : 1;
                unsigned int reserve_1          : 8;
            } bits;
            unsigned int val;
        } dbg_err;
        union { // name: dbg_cnt0, offset: 0xec
            struct {
                unsigned int EXT_RXCNT    : 8;
                unsigned int EXT_TXCNT    : 8;
                unsigned int MCNT_PAGE_R  : 8;
                unsigned int MCNT_PAGE_AR : 8;
            } bits;
            unsigned int val;
        } dbg_cnt0;
        union { // name: dbg_cnt1, offset: 0xf0
            struct {
                unsigned int SCNT_B    : 8;
                unsigned int SCNT_W    : 8;
                unsigned int SCNT_AW   : 8;
                unsigned int reserve_0 : 8;
            } bits;
            unsigned int val;
        } dbg_cnt1;
        union { // name: dbg_cnt2, offset: 0xf4
            struct {
                unsigned int MCNT_B    : 8;
                unsigned int MCNT_W    : 8;
                unsigned int MCNT_AW   : 8;
                unsigned int reserve_0 : 8;
            } bits;
            unsigned int val;
        } dbg_cnt2;
        union { // name: dbg_cnt3, offset: 0xf8
            struct {
                unsigned int SCNT_R  : 8;
                unsigned int SCNT_AR : 8;
                unsigned int MCNT_R  : 8;
                unsigned int MCNT_AR : 8;
            } bits;
            unsigned int val;
        } dbg_cnt3;
        union { // name: version, offset: 0xfc
            struct {
                unsigned int VERSION   : 8;
                unsigned int reserve_0 : 24;
            } bits;
            unsigned int val;
        } version;
    } regs;
    unsigned int data[64];
} mmu0_rk3538_u;

#endif /* VOP_RK3538_H */
