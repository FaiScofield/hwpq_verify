#ifndef VOP_RK3572_H
#define VOP_RK3572_H

// 0x00000000
typedef union sys_ctrl_rk3572 {
    struct {
        union { // name: sys_reg_cfg_done, offset: 0x0
            struct {
                unsigned int reg_load_global0_en  : 1;
                unsigned int reg_load_global1_en  : 1;
                unsigned int reg_load_global2_en  : 1;
                unsigned int reserve_0            : 1;
                unsigned int reg_load_sys0_en     : 1;
                unsigned int reg_load_sys1_en     : 1;
                unsigned int reg_load_sys2_en     : 1;
                unsigned int reserve_1            : 7;
                unsigned int reg_load_wb_en       : 1;
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
        union { // name: sys_auto_gating_ctrl_imd, offset: 0x8
            struct {
                unsigned int cluster0_aclk_gating_en    : 1;
                unsigned int cluster1_aclk_gating_en    : 1;
                unsigned int reserve_0                  : 2;
                unsigned int esmart_scl_gating_en       : 1;
                unsigned int reserve_1                  : 1;
                unsigned int win_aclk_gating_en         : 1;
                unsigned int aclk_pre_auto_gating_en    : 1;
                unsigned int overlay_aclk_gating_en     : 1;
                unsigned int reserve_2                  : 2;
                unsigned int wb_aclk_gating_en          : 1;
                unsigned int reserve_3                  : 1;
                unsigned int prescan_aclk_gating_en     : 1;
                unsigned int port_dclk_gating_en        : 1;
                unsigned int axi_aclk_gating_en         : 1;
                unsigned int dp_pix_clk_gating_en       : 1;
                unsigned int reserve_4                  : 1;
                unsigned int hdmi_pix_clk_gating_en     : 1;
                unsigned int reserve_5                  : 1;
                unsigned int mipi_pix_clk_gating_en     : 1;
                unsigned int reserve_6                  : 1;
                unsigned int edp_pix_clk_en             : 1;
                unsigned int reserve_7                  : 1;
                unsigned int rgb_clk_gating_en          : 1;
                unsigned int reserve_8                  : 4;
                unsigned int axi0_aclk_static_gating_en : 1;
                unsigned int axi1_aclk_static_gating_en : 1;
                unsigned int auto_gating_en             : 1;
            } bits;
            unsigned int val;
        } sys_auto_gating_ctrl_imd;
        union { // name: sys_win_reg_cfg_done, offset: 0xc
            struct {
                unsigned int reg_load_cluster0_en : 1;
                unsigned int reg_load_cluster1_en : 1;
                unsigned int reserve_0            : 2;
                unsigned int reg_load_esmart0_en  : 1;
                unsigned int reg_load_esmart1_en  : 1;
                unsigned int reg_load_esmart2_en  : 1;
                unsigned int reg_load_esmart3_en  : 1;
                unsigned int reserve_1            : 8;
                unsigned int write_mask           : 16;
            } bits;
            unsigned int val;
        } sys_win_reg_cfg_done;
        union { // name: sys_axi0_ctrl_imd, offset: 0x10
            struct {
                unsigned int axi0_dma_stop        : 1;
                unsigned int axi0_outstanding_en  : 1;
                unsigned int reserve_0            : 2;
                unsigned int axi0_outstanding_num : 6;
                unsigned int reserve_1            : 6;
                unsigned int axi0_mmu_idle        : 1;
                unsigned int reserve_2            : 15;
            } bits;
            unsigned int val;
        } sys_axi0_ctrl_imd;
        union { // name: sys_axi_hurry_ctrl0_imd, offset: 0x14
            struct {
                unsigned int axi0_hurry_w_en      : 1;
                unsigned int axi0_hurry_w_value   : 2;
                unsigned int axi0_hurry_w_mode    : 2;
                unsigned int reserve_0            : 3;
                unsigned int axi0_hurry_en        : 1;
                unsigned int axi0_hurry_value     : 2;
                unsigned int axi0_hurry_threshold : 1;
                unsigned int axi0_qos_en          : 1;
                unsigned int axi0_qos_value       : 2;
                unsigned int reserve_1            : 17;
            } bits;
            unsigned int val;
        } sys_axi_hurry_ctrl0_imd;
        union { // name: sys_axi_hurry_ctrl1_imd, offset: 0x18
            struct {
                unsigned int axi1_hurry_w_en      : 1;
                unsigned int axi1_hurry_w_value   : 2;
                unsigned int axi1_hurry_w_mode    : 2;
                unsigned int reserve_0            : 3;
                unsigned int axi1_hurry_en        : 1;
                unsigned int axi1_hurry_value     : 2;
                unsigned int axi1_hurry_threshold : 1;
                unsigned int axi1_qos_en          : 1;
                unsigned int axi1_qos_value       : 2;
                unsigned int reserve_1            : 17;
            } bits;
            unsigned int val;
        } sys_axi_hurry_ctrl1_imd;
        union { // name: sys_axi1_ctrl_imd, offset: 0x1c
            struct {
                unsigned int axi1_dma_stop        : 1;
                unsigned int axi1_outstanding_en  : 1;
                unsigned int reserve_0            : 2;
                unsigned int axi1_outstanding_num : 6;
                unsigned int reserve_1            : 6;
                unsigned int axi1_mmu_idle        : 1;
                unsigned int reserve_2            : 15;
            } bits;
            unsigned int val;
        } sys_axi1_ctrl_imd;
        union { // name: sys_mmu_ctrl_imd, offset: 0x20
            struct {
                unsigned int rkmmu2_0_en        : 1;
                unsigned int rkmmu2_0_sel       : 1;
                unsigned int mmu_bypass_en      : 1;
                unsigned int reserve_0          : 1;
                unsigned int mmu_bypass_id      : 5;
                unsigned int mmu1_bypass_en     : 1;
                unsigned int reserve_1          : 1;
                unsigned int mmu2_0_soft_rst_en : 1;
                unsigned int mmu_regdone_sel    : 2;
                unsigned int mmu1_regdone_sel   : 2;
                unsigned int write_mask         : 16;
            } bits;
            unsigned int val;
        } sys_mmu_ctrl_imd;
        union { // name: sys_axi_lut_ctrl_imd, offset: 0x24
            struct {
                unsigned int lut_dma_en   : 1;
                unsigned int lut_dma_stop : 1;
                unsigned int lut_dma_rlen : 2;
                unsigned int lut_dma_rid  : 4;
                unsigned int reserve_0    : 1;
                unsigned int lut_use_axi1 : 1;
                unsigned int reserve_1    : 22;
            } bits;
            unsigned int val;
        } sys_axi_lut_ctrl_imd;
        union { // name: sys_port_ctrl_imd, offset: 0x28
            struct {
                unsigned int vp0_interlace_frm_reg_done : 1;
                unsigned int vp1_interlace_frm_reg_done : 1;
                unsigned int vp2_interlace_frm_reg_done : 1;
                unsigned int reserve_0                  : 1;
                unsigned int dsp_vs_t_sel               : 1;
                unsigned int auto_cs_en                 : 1;
                unsigned int reserve_1                  : 2;
                unsigned int vfp0_dma_stop_en           : 1;
                unsigned int vfp1_dma_stop_en           : 1;
                unsigned int vfp2_dma_stop_en           : 1;
                unsigned int reserve_2                  : 1;
                unsigned int vp0_dclk_src_sel           : 1;
                unsigned int vp2_dclk_src_sel           : 1;
                unsigned int reserve_3                  : 2;
                unsigned int write_mask                 : 16;
            } bits;
            unsigned int val;
        } sys_port_ctrl_imd;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_44_48;
        union { // name: sys_cluster_pd_ctrl_imd, offset: 0x30
            struct {
                unsigned int cluster01_pd_en : 1;
                unsigned int reserve_0       : 15;
                unsigned int write_mask      : 16;
            } bits;
            unsigned int val;
        } sys_cluster_pd_ctrl_imd;
        union { // name: sys_esmart_pd_ctrl_imd, offset: 0x34
            struct {
                unsigned int esmart_pd_en   : 1;
                unsigned int reserve_0      : 5;
                unsigned int esmart_lb_mode : 2;
                unsigned int bpp_lut_en     : 1;
                unsigned int reserve_1      : 1;
                unsigned int bpp_win_sel    : 2;
                unsigned int reserve_2      : 4;
                unsigned int write_mask     : 16;
            } bits;
            unsigned int val;
        } sys_esmart_pd_ctrl_imd;
        union { // name: sys_var_ferq_ctrl_imd, offset: 0x38
            struct {
                unsigned int dma_finish_mode        : 2;
                unsigned int axi_dma_finish_and_en  : 1;
                unsigned int wb_dma_finish_and_en   : 1;
                unsigned int vp0_line_flag_and_en   : 1;
                unsigned int vp1_line_flag_and_en   : 1;
                unsigned int vp2_line_flag_and_en   : 1;
                unsigned int reserve_0              : 1;
                unsigned int vp0_dsp_hold_and_en    : 1;
                unsigned int vp1_dsp_hold_and_en    : 1;
                unsigned int vp2_dsp_hold_and_en    : 1;
                unsigned int reserve_1              : 1;
                unsigned int vp0_almost_full_and_en : 1;
                unsigned int vp1_almost_full_and_en : 1;
                unsigned int vp2_almost_full_and_en : 1;
                unsigned int reserve_2              : 3;
                unsigned int axi_dma_finish_or_en   : 1;
                unsigned int wb_dma_finish_or_en    : 1;
                unsigned int vp0_line_flag_or_en    : 1;
                unsigned int vp1_line_flag_or_en    : 1;
                unsigned int vp2_line_flag_or_en    : 1;
                unsigned int reserve_3              : 1;
                unsigned int vp0_dsp_hold_or_en     : 1;
                unsigned int vp1_dsp_hold_or_en     : 1;
                unsigned int vp2_dsp_hold_or_en     : 1;
                unsigned int reserve_4              : 1;
                unsigned int vp0_almost_full_or_en  : 1;
                unsigned int vp1_almost_full_or_en  : 1;
                unsigned int vp2_almost_full_or_en  : 1;
                unsigned int reserve_5              : 1;
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
                unsigned int fbcd_timeout_cnt : 31;
                unsigned int fbcd_timeout_en  : 1;
            } bits;
            unsigned int val;
        } fbc_timeout_ctrl;
        union { // name: vop_io_vsync_ctrl, offset: 0x4c
            struct {
                unsigned int vop_io_vp0_vsync_sel : 2;
                unsigned int vop_io_vp1_vsync_sel : 2;
                unsigned int vop_io_vp2_vsync_sel : 2;
                unsigned int reserve_0            : 26;
            } bits;
            unsigned int val;
        } vop_io_vsync_ctrl;
        struct {
            unsigned int reserve_data[2];
        } reserve_reg_80_88;
        union { // name: sys_lut_port_sel, offset: 0x58
            struct {
                unsigned int reserve_0           : 10;
                unsigned int sharp_ahb_port_sel  : 2;
                unsigned int gamma_ahb_write_sel : 2;
                unsigned int acm_ahb_port_sel    : 2;
                unsigned int write_mask          : 16;
            } bits;
            unsigned int val;
        } sys_lut_port_sel;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_92_96;
        union { // name: sys_status0, offset: 0x60
            struct {
                unsigned int dma_stop_valid0 : 1;
                unsigned int mmu_idle        : 1;
                unsigned int reserve_0       : 14;
                unsigned int dsp_vcnt0       : 13;
                unsigned int reserve_1       : 3;
            } bits;
            unsigned int val;
        } sys_status0;
        union { // name: sys_status1, offset: 0x64
            struct {
                unsigned int dma_stop_valid1 : 1;
                unsigned int mmu_idle        : 1;
                unsigned int reserve_0       : 14;
                unsigned int dsp_vcnt1       : 13;
                unsigned int reserve_1       : 3;
            } bits;
            unsigned int val;
        } sys_status1;
        union { // name: sys_status2, offset: 0x68
            struct {
                unsigned int reserve_0 : 16;
                unsigned int dsp_vcnt2 : 13;
                unsigned int reserve_1 : 3;
            } bits;
            unsigned int val;
        } sys_status2;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_108_112;
        union { // name: sys_line_flag0, offset: 0x70
            struct {
                unsigned int dsp_line_flag_num_0   : 13;
                unsigned int reserve_0             : 2;
                unsigned int ddr_line_flag_sel     : 1;
                unsigned int dsp_line_flag_num_1   : 13;
                unsigned int dsp_almost_full_thold : 3;
            } bits;
            unsigned int val;
        } sys_line_flag0;
        union { // name: sys_line_flag1, offset: 0x74
            struct {
                unsigned int dsp_line_flag_num_0   : 13;
                unsigned int reserve_0             : 3;
                unsigned int dsp_line_flag_num_1   : 13;
                unsigned int dsp_almost_full_thold : 3;
            } bits;
            unsigned int val;
        } sys_line_flag1;
        union { // name: sys_line_flag2, offset: 0x78
            struct {
                unsigned int dsp_line_flag_num_0   : 13;
                unsigned int reserve_0             : 3;
                unsigned int dsp_line_flag_num_1   : 13;
                unsigned int dsp_almost_full_thold : 3;
            } bits;
            unsigned int val;
        } sys_line_flag2;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_124_128;
        union { // name: sys0_intr_en, offset: 0x80
            struct {
                unsigned int reserve_0                : 1;
                unsigned int intr_en_bus0_error       : 1;
                unsigned int intr_en_dma0_finish      : 1;
                unsigned int int_en_wb_uv_fifo_full   : 1;
                unsigned int int_en_wb_yrgb_fifo_full : 1;
                unsigned int int_en_wb_finish         : 1;
                unsigned int reserve_1                : 1;
                unsigned int intr_en_mmu              : 1;
                unsigned int intr_en_wb_resp_err      : 1;
                unsigned int intr_en_wb_time_out      : 1;
                unsigned int reserve_2                : 6;
                unsigned int write_mask               : 16;
            } bits;
            unsigned int val;
        } sys0_intr_en;
        union { // name: sys0_intr_clr, offset: 0x84
            struct {
                unsigned int reserve_0                  : 1;
                unsigned int intr_clr_bus_error         : 1;
                unsigned int intr_clr_dma_finish        : 1;
                unsigned int intr_clr_wb_uv_fifo_full   : 1;
                unsigned int intr_clr_wb_yrgb_fifo_full : 1;
                unsigned int intr_clr_wb_dma_finish     : 1;
                unsigned int reserve_1                  : 1;
                unsigned int intr_clr_mmu               : 1;
                unsigned int intr_clr_wb_resp_err       : 1;
                unsigned int intr_clr_wb_time_out       : 1;
                unsigned int reserve_2                  : 6;
                unsigned int write_mask                 : 16;
            } bits;
            unsigned int val;
        } sys0_intr_clr;
        union { // name: sys0_intr_status, offset: 0x88
            struct {
                unsigned int reserve_0                     : 1;
                unsigned int intr_status_bus_error         : 1;
                unsigned int intr_status_dma_finish        : 1;
                unsigned int intr_status_wb_uv_fifo_full   : 1;
                unsigned int intr_status_wb_yrgb_fifo_full : 1;
                unsigned int intr_status_wb_dma_finish     : 1;
                unsigned int reserve_1                     : 1;
                unsigned int intr_status_mmu               : 1;
                unsigned int intr_status_wb_resp_err       : 1;
                unsigned int intr_status_wb_time_out       : 1;
                unsigned int reserve_2                     : 22;
            } bits;
            unsigned int val;
        } sys0_intr_status;
        union { // name: sys0_intr_raw_status, offset: 0x8c
            struct {
                unsigned int reserve_0                         : 1;
                unsigned int intr_raw_status_bus_error         : 1;
                unsigned int intr_raw_status_dma_finish        : 1;
                unsigned int intr_raw_status_wb_uv_fifo_full   : 1;
                unsigned int intr_raw_status_wb_yrgb_fifo_full : 1;
                unsigned int intr_raw_status_wb_dma_finish     : 1;
                unsigned int reserve_1                         : 1;
                unsigned int intr_raw_status_mmu0              : 1;
                unsigned int intr_status_wb_resp_err           : 1;
                unsigned int intr_status_wb_time_out           : 1;
                unsigned int reserve_2                         : 22;
            } bits;
            unsigned int val;
        } sys0_intr_raw_status;
        union { // name: sys1_intr_en, offset: 0x90
            struct {
                unsigned int reserve_0           : 1;
                unsigned int intr_en_bus1_error  : 1;
                unsigned int intr_en_dma1_finish : 1;
                unsigned int reserve_1           : 4;
                unsigned int intr_en_mmu1        : 1;
                unsigned int reserve_2           : 8;
                unsigned int write_mask          : 16;
            } bits;
            unsigned int val;
        } sys1_intr_en;
        union { // name: sys1_intr_clr_sys, offset: 0x94
            struct {
                unsigned int reserve_0           : 1;
                unsigned int intr_clr_bus_error  : 1;
                unsigned int intr_clr_dma_finish : 1;
                unsigned int reserve_1           : 4;
                unsigned int intr_clr_mmu1       : 1;
                unsigned int reserve_2           : 8;
                unsigned int write_mask          : 16;
            } bits;
            unsigned int val;
        } sys1_intr_clr_sys;
        union { // name: sys1_intr_status, offset: 0x98
            struct {
                unsigned int reserve_0              : 1;
                unsigned int intr_status_bus_error  : 1;
                unsigned int intr_status_dma_finish : 1;
                unsigned int reserve_1              : 4;
                unsigned int intr_status_mmu1       : 1;
                unsigned int reserve_2              : 24;
            } bits;
            unsigned int val;
        } sys1_intr_status;
        union { // name: sys1_intr_raw_status, offset: 0x9c
            struct {
                unsigned int reserve_0                  : 1;
                unsigned int intr_raw_status_bus_error  : 1;
                unsigned int intr_raw_status_dma_finish : 1;
                unsigned int reserve_1                  : 4;
                unsigned int intr_raw_status_mmu1       : 1;
                unsigned int reserve_2                  : 24;
            } bits;
            unsigned int val;
        } sys1_intr_raw_status;
        union { // name: port0_intr_en, offset: 0xa0
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
        } port0_intr_en;
        union { // name: port0_intr_clr, offset: 0xa4
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
        } port0_intr_clr;
        union { // name: port0_intr_status, offset: 0xa8
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
        } port0_intr_status;
        union { // name: port0_intr_raw_status, offset: 0xac
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
        } port0_intr_raw_status;
        union { // name: port1_intr_en, offset: 0xb0
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
                unsigned int reserve_2              : 6;
                unsigned int write_mask             : 16;
            } bits;
            unsigned int val;
        } port1_intr_en;
        union { // name: port1_intr_clr, offset: 0xb4
            struct {
                unsigned int intr_clr_fs             : 1;
                unsigned int reserve_0               : 1;
                unsigned int intr_clr_line_flag0     : 1;
                unsigned int intr_clr_line_flag1     : 1;
                unsigned int intr_clr_post_buf_empty : 1;
                unsigned int intr_clr_fs_field       : 1;
                unsigned int intr_clr_dsp_hold_valid : 1;
                unsigned int intr_clr_vfp            : 1;
                unsigned int reserve_1               : 1;
                unsigned int intr_clr_post_full      : 1;
                unsigned int reserve_2               : 6;
                unsigned int write_mask              : 16;
            } bits;
            unsigned int val;
        } port1_intr_clr;
        union { // name: port1_intr_status, offset: 0xb8
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
                unsigned int reserve_2                  : 22;
            } bits;
            unsigned int val;
        } port1_intr_status;
        union { // name: port1_intr_raw_status, offset: 0xbc
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
                unsigned int reserve_2                      : 22;
            } bits;
            unsigned int val;
        } port1_intr_raw_status;
        union { // name: port2_intr_en, offset: 0xc0
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
                unsigned int reserve_2              : 6;
                unsigned int write_mask             : 16;
            } bits;
            unsigned int val;
        } port2_intr_en;
        union { // name: port2_intr_clr, offset: 0xc4
            struct {
                unsigned int intr_clr_fs             : 1;
                unsigned int reserve_0               : 1;
                unsigned int intr_clr_line_flag0     : 1;
                unsigned int intr_clr_line_flag1     : 1;
                unsigned int intr_clr_post_buf_empty : 1;
                unsigned int intr_clr_fs_field       : 1;
                unsigned int intr_clr_dsp_hold_valid : 1;
                unsigned int intr_clr_vfp            : 1;
                unsigned int reserve_1               : 1;
                unsigned int intr_clr_post_full      : 1;
                unsigned int reserve_2               : 6;
                unsigned int write_mask              : 16;
            } bits;
            unsigned int val;
        } port2_intr_clr;
        union { // name: port2_intr_status, offset: 0xc8
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
                unsigned int reserve_2                  : 22;
            } bits;
            unsigned int val;
        } port2_intr_status;
        union { // name: port2_intr_raw_status, offset: 0xcc
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
                unsigned int reserve_2                      : 22;
            } bits;
            unsigned int val;
        } port2_intr_raw_status;
        struct {
            unsigned int reserve_data[4];
        } reserve_reg_208_224;
        union { // name: fbcd_intr_en0, offset: 0xe0
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
        union { // name: fbcd_intr_clr0, offset: 0xe4
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
        union { // name: fbcd_intr_status0, offset: 0xe8
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
        union { // name: fbcd_intr_raw_status0, offset: 0xec
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
        struct {
            unsigned int reserve_data[4];
        } reserve_reg_240_256;
        union { // name: sys_wb_ctrl0, offset: 0x100
            struct {
                unsigned int wb_en                 : 1;
                unsigned int wb_fmt                : 3;
                unsigned int wb_dither_en          : 1;
                unsigned int wb_rgb2yuv_en         : 1;
                unsigned int wb_rgb2yuv_mode       : 1;
                unsigned int wb_xpsd_bil_en        : 1;
                unsigned int wb_ythrow_en          : 1;
                unsigned int wb_ythrow_mode        : 1;
                unsigned int reserve_0             : 1;
                unsigned int wb_post_empty_stop_en : 1;
                unsigned int wb_oneframe_mode      : 1;
                unsigned int reserve_1             : 1;
                unsigned int wb_rb_swap_en         : 1;
                unsigned int wb_rg_swap_en         : 1;
                unsigned int reserve_2             : 2;
                unsigned int wb_xgt2_en            : 1;
                unsigned int reserve_3             : 1;
                unsigned int wb_yrgb_id            : 4;
                unsigned int wb_uv_id              : 4;
                unsigned int reserve_4             : 2;
                unsigned int wb_port_sel_imd       : 2;
            } bits;
            unsigned int val;
        } sys_wb_ctrl0;
        union { // name: sys_wb_xspd_factor, offset: 0x104
            struct {
                unsigned int fifo_thold         : 10;
                unsigned int reserve_0          : 6;
                unsigned int wb_xpsd_bil_factor : 14;
                unsigned int reserve_1          : 2;
            } bits;
            unsigned int val;
        } sys_wb_xspd_factor;
        union { // name: sys_wb_yrgb_mst, offset: 0x108
            struct {
                unsigned int wb_yrgb_mst : 32;
            } bits;
            unsigned int val;
        } sys_wb_yrgb_mst;
        union { // name: sys_wb_cbr_mst, offset: 0x10c
            struct {
                unsigned int wb_cbr_mst : 32;
            } bits;
            unsigned int val;
        } sys_wb_cbr_mst;
        union { // name: sys_wb_vir_stride, offset: 0x110
            struct {
                unsigned int wb_vir_stride    : 13;
                unsigned int reserve_0        : 2;
                unsigned int wb_vir_stride_en : 1;
                unsigned int wb_dsp_width     : 13;
                unsigned int reserve_1        : 3;
            } bits;
            unsigned int val;
        } sys_wb_vir_stride;
        union { // name: sys_wb_timeout_ctrl, offset: 0x114
            struct {
                unsigned int wb_timeout_cnt : 31;
                unsigned int reserve_0      : 1;
            } bits;
            unsigned int val;
        } sys_wb_timeout_ctrl;
        struct {
            unsigned int reserve_data[26];
        } reserve_reg_280_384;
        union { // name: mipi0_inface_ctrl, offset: 0x180
            struct {
                unsigned int mipi_out_en        : 1;
                unsigned int mipi_clk_gating_en : 1;
                unsigned int mipi_port_sel      : 2;
                unsigned int mipi_hsync_pol     : 1;
                unsigned int mipi_vsync_pol     : 1;
                unsigned int reserve_0          : 2;
                unsigned int mipi_split_en      : 1;
                unsigned int mipi_data1_sel     : 1;
                unsigned int reserve_1          : 1;
                unsigned int mipi_cmd_mode      : 1;
                unsigned int reserve_2          : 8;
                unsigned int mipi_pix_clk_sel   : 1;
                unsigned int mipi_dclk_sel      : 1;
                unsigned int reserve_3          : 9;
                unsigned int regdone_imd_en     : 1;
            } bits;
            unsigned int val;
        } mipi0_inface_ctrl;
        union { // name: hdmi0_inface_ctrl, offset: 0x184
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
        union { // name: edp0_inface_ctrl, offset: 0x188
            struct {
                unsigned int edp_out_en        : 1;
                unsigned int edp_clk_gating_en : 1;
                unsigned int edp_port_sel      : 2;
                unsigned int edp_hsync_pol     : 1;
                unsigned int edp_vsync_pol     : 1;
                unsigned int reserve_0         : 2;
                unsigned int edp_split_en      : 1;
                unsigned int edp_data1_sel     : 1;
                unsigned int reserve_1         : 10;
                unsigned int edp_pix_clk_sel   : 1;
                unsigned int edp_dclk_sel      : 1;
                unsigned int reserve_2         : 9;
                unsigned int regdone_imd_en    : 1;
            } bits;
            unsigned int val;
        } edp0_inface_ctrl;
        union { // name: dp0_inface_ctrl, offset: 0x18c
            struct {
                unsigned int dp_out_en        : 1;
                unsigned int dp_clk_gating_en : 1;
                unsigned int dp_port_sel      : 2;
                unsigned int dp_hsync_pol     : 1;
                unsigned int dp_vsync_pol     : 1;
                unsigned int reserve_0        : 2;
                unsigned int dp_split_en      : 1;
                unsigned int dp_data1_sel     : 1;
                unsigned int reserve_1        : 10;
                unsigned int dp_pix_clk_sel   : 1;
                unsigned int dp_dclk_sel      : 1;
                unsigned int reserve_2        : 9;
                unsigned int regdone_imd_en   : 1;
            } bits;
            unsigned int val;
        } dp0_inface_ctrl;
        union { // name: lvds0_inface_ctrl, offset: 0x190
            struct {
                unsigned int lvds_out_en        : 1;
                unsigned int lvds_clk_gating_en : 1;
                unsigned int lvds_port_sel      : 2;
                unsigned int lvds_hsync_pol     : 1;
                unsigned int lvds_vsync_pol     : 1;
                unsigned int lvds_den_pol       : 1;
                unsigned int lvds_dclk_pol      : 1;
                unsigned int reserve_0          : 1;
                unsigned int lvds_data1_sel     : 1;
                unsigned int reserve_1          : 2;
                unsigned int lvds_con_chasel    : 1;
                unsigned int lvds_con_dual_sel  : 1;
                unsigned int lvds_con_dual_swap : 1;
                unsigned int reserve_2          : 16;
                unsigned int regdone_imd_en     : 1;
            } bits;
            unsigned int val;
        } lvds0_inface_ctrl;
        union { // name: rgb_inface_ctrl, offset: 0x194
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
                unsigned int reserve_3      : 1;
                unsigned int bt1120_out_en  : 1;
                unsigned int bt1120_uv_swap : 1;
                unsigned int bt1120_yc_swap : 1;
                unsigned int reserve_4      : 2;
                unsigned int rgb_dclk_sel   : 1;
                unsigned int reserve_5      : 9;
                unsigned int regdone_imd_en : 1;
            } bits;
            unsigned int val;
        } rgb_inface_ctrl;
        struct {
            unsigned int reserve_data[3];
        } reserve_reg_408_420;
        union { // name: dp1_inface_ctrl, offset: 0x1a4
            struct {
                unsigned int dp_out_en        : 1;
                unsigned int dp_clk_gating_en : 1;
                unsigned int dp_port_sel      : 2;
                unsigned int dp_hsync_pol     : 1;
                unsigned int dp_vsync_pol     : 1;
                unsigned int reserve_0        : 2;
                unsigned int dp_split_en      : 1;
                unsigned int dp_data1_sel     : 1;
                unsigned int reserve_1        : 10;
                unsigned int dp_pix_clk_sel   : 1;
                unsigned int dp_dclk_sel      : 1;
                unsigned int reserve_2        : 9;
                unsigned int regdone_imd_en   : 1;
            } bits;
            unsigned int val;
        } dp1_inface_ctrl;
        union { // name: lvds1_inface_ctrl, offset: 0x1a8
            struct {
                unsigned int lvds_out_en        : 1;
                unsigned int lvds_clk_gating_en : 1;
                unsigned int lvds_port_sel      : 2;
                unsigned int lvds_hsync_pol     : 1;
                unsigned int lvds_vsync_pol     : 1;
                unsigned int lvds_den_pol       : 1;
                unsigned int lvds_dclk_pol      : 1;
                unsigned int reserve_0          : 1;
                unsigned int lvds_data1_sel     : 1;
                unsigned int reserve_1          : 2;
                unsigned int lvds_con_chasel    : 1;
                unsigned int lvds_con_dual_sel  : 1;
                unsigned int lvds_con_dual_swap : 1;
                unsigned int reserve_2          : 16;
                unsigned int regdone_imd_en     : 1;
            } bits;
            unsigned int val;
        } lvds1_inface_ctrl;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_428_432;
        union { // name: dp2_inface_ctrl, offset: 0x1b0
            struct {
                unsigned int dp_out_en        : 1;
                unsigned int dp_clk_gating_en : 1;
                unsigned int dp_port_sel      : 2;
                unsigned int dp_hsync_pol     : 1;
                unsigned int dp_vsync_pol     : 1;
                unsigned int reserve_0        : 2;
                unsigned int dp_split_en      : 1;
                unsigned int dp_data1_sel     : 1;
                unsigned int reserve_1        : 10;
                unsigned int dp_pix_clk_sel   : 1;
                unsigned int dp_dclk_sel      : 1;
                unsigned int reserve_2        : 9;
                unsigned int regdone_imd_en   : 1;
            } bits;
            unsigned int val;
        } dp2_inface_ctrl;
        struct {
            unsigned int reserve_data[6];
        } reserve_reg_436_460;
        union { // name: sec_inface_ctrl, offset: 0x1cc
            struct {
                unsigned int sec_mipi0_port_sel : 2;
                unsigned int sec_hdmi0_port_sel : 2;
                unsigned int sec_edp0_port_sel  : 2;
                unsigned int sec_dp0_port_sel   : 2;
                unsigned int sec_lvds0_port_sel : 2;
                unsigned int sec_rgb_port_sel   : 2;
                unsigned int sec_mipi1_port_sel : 2;
                unsigned int sec_hdmi1_port_sel : 2;
                unsigned int sec_edp1_port_sel  : 2;
                unsigned int sec_dp1_port_sel   : 2;
                unsigned int sec_lvds1_port_sel : 2;
                unsigned int sec_edp2_port_sel  : 2;
                unsigned int sec_dp2_port_sel   : 2;
                unsigned int reserve_0          : 6;
            } bits;
            unsigned int val;
        } sec_inface_ctrl;
        struct {
            unsigned int reserve_data[4];
        } reserve_reg_464_480;
        union { // name: sec_drm_ctrl, offset: 0x1e0
            struct {
                unsigned int sec_drm_en            : 1;
                unsigned int reserve_0             : 3;
                unsigned int sec_wb_dis            : 1;
                unsigned int sec_rid_lock_en       : 1;
                unsigned int reserve_1             : 2;
                unsigned int sec_cluster0_en       : 1;
                unsigned int sec_cluster1_en       : 1;
                unsigned int reserve_2             : 2;
                unsigned int sec_esmart0_en        : 1;
                unsigned int sec_esmart1_en        : 1;
                unsigned int sec_esmart2_en        : 1;
                unsigned int sec_esmart3_en        : 1;
                unsigned int sec_axi0_rid0_prot_en : 1;
                unsigned int sec_axi0_rid1_prot_en : 1;
                unsigned int sec_axi0_rid2_prot_en : 1;
                unsigned int sec_axi0_rid3_prot_en : 1;
                unsigned int sec_axi1_rid0_prot_en : 1;
                unsigned int sec_axi1_rid1_prot_en : 1;
                unsigned int sec_axi1_rid2_prot_en : 1;
                unsigned int sec_axi1_rid3_prot_en : 1;
                unsigned int reserve_3             : 8;
            } bits;
            unsigned int val;
        } sec_drm_ctrl;
        union { // name: sec_drm_port_sel, offset: 0x1e4
            struct {
                unsigned int drm_cluster0_port_sel : 2;
                unsigned int reserve_0             : 2;
                unsigned int drm_cluster1_port_sel : 2;
                unsigned int reserve_1             : 10;
                unsigned int drm_esmart0_port_sel  : 2;
                unsigned int reserve_2             : 2;
                unsigned int drm_esmart1_port_sel  : 2;
                unsigned int reserve_3             : 2;
                unsigned int drm_esmart2_port_sel  : 2;
                unsigned int reserve_4             : 2;
                unsigned int drm_esmart3_port_sel  : 2;
                unsigned int reserve_5             : 2;
            } bits;
            unsigned int val;
        } sec_drm_port_sel;
        union { // name: sec_port0_layer_sel, offset: 0x1e8
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
        union { // name: sec_port1_layer_sel, offset: 0x1ec
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
        } sec_port1_layer_sel;
        union { // name: sec_port2_layer_sel, offset: 0x1f0
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
        } sec_port2_layer_sel;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_500_504;
        union { // name: sec_axi_rid_prot, offset: 0x1f8
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
        union { // name: sys_otp_mirr_ctrl_imd, offset: 0x1fc
            struct {
                unsigned int dis_otp_fuction : 1;
                unsigned int reserve_0       : 31;
            } bits;
            unsigned int val;
        } sys_otp_mirr_ctrl_imd;
    } regs;
    unsigned int data[128];
} sys_ctrl_rk3572_u;

// 0x00000500
typedef union overlay_system_rk3572 {
    struct {
        union { // name: extra_alpha_ctrl_imd, offset: 0x0
            struct {
                unsigned int port0_extra_alpha_en : 1;
                unsigned int reserve_0            : 31;
            } bits;
            unsigned int val;
        } extra_alpha_ctrl_imd;
        struct {
            unsigned int reserve_data[11];
        } reserve_reg_4_48;
        union { // name: cluster0_src_color_ctrl, offset: 0x30
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
        } cluster0_src_color_ctrl;
        union { // name: cluster0_dst_color_ctrl, offset: 0x34
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
        } cluster0_dst_color_ctrl;
        union { // name: cluster0_src_alpha_ctrl, offset: 0x38
            struct {
                unsigned int reserve_0           : 1;
                unsigned int src_alpha_mode1     : 1;
                unsigned int src_blend_mode1     : 2;
                unsigned int src_alpha_cal_mode1 : 1;
                unsigned int src_factor_mode1    : 3;
                unsigned int reserve_1           : 24;
            } bits;
            unsigned int val;
        } cluster0_src_alpha_ctrl;
        union { // name: cluster0_dst_alpha_ctrl, offset: 0x3c
            struct {
                unsigned int reserve_0           : 1;
                unsigned int dst_alpha_mode1     : 1;
                unsigned int dst_blend_mode1     : 2;
                unsigned int dst_alpha_cal_mode1 : 1;
                unsigned int dst_factor_mode1    : 3;
                unsigned int reserve_1           : 24;
            } bits;
            unsigned int val;
        } cluster0_dst_alpha_ctrl;
        union { // name: cluster1_src_color_ctrl, offset: 0x40
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
        } cluster1_src_color_ctrl;
        union { // name: cluster1_dst_color_ctrl, offset: 0x44
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
        } cluster1_dst_color_ctrl;
        union { // name: cluster1_src_alpha_ctrl, offset: 0x48
            struct {
                unsigned int reserve_0           : 1;
                unsigned int src_alpha_mode1     : 1;
                unsigned int src_blend_mode1     : 2;
                unsigned int src_alpha_cal_mode1 : 1;
                unsigned int src_factor_mode1    : 3;
                unsigned int reserve_1           : 24;
            } bits;
            unsigned int val;
        } cluster1_src_alpha_ctrl;
        union { // name: cluster1_dst_alpha_ctrl, offset: 0x4c
            struct {
                unsigned int reserve_0           : 1;
                unsigned int dst_alpha_mode1     : 1;
                unsigned int dst_blend_mode1     : 2;
                unsigned int dst_alpha_cal_mode1 : 1;
                unsigned int dst_factor_mode1    : 3;
                unsigned int reserve_1           : 24;
            } bits;
            unsigned int val;
        } cluster1_dst_alpha_ctrl;
    } regs;
    unsigned int data[20];
} overlay_system_rk3572_u;

// 0x00000600
typedef union overlay_port0_rk3572 {
    struct {
        union { // name: overlay_ctrl, offset: 0x0
            struct {
                unsigned int overlay_mode    : 1;
                unsigned int reserve_0       : 3;
                unsigned int hdr10_path_en   : 1;
                unsigned int sdr2hdr_path_en : 1;
                unsigned int reserve_1       : 26;
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
        union { // name: extra_src_color_ctrl, offset: 0x50
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
        } extra_src_color_ctrl;
        union { // name: extra_dst_color_ctrl, offset: 0x54
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
        } extra_dst_color_ctrl;
        union { // name: extra_src_alpha_ctrl, offset: 0x58
            struct {
                unsigned int reserve_0           : 1;
                unsigned int src_alpha_mode1     : 1;
                unsigned int src_blend_mode1     : 2;
                unsigned int src_alpha_cal_mode1 : 1;
                unsigned int src_factor_mode1    : 3;
                unsigned int reserve_1           : 24;
            } bits;
            unsigned int val;
        } extra_src_alpha_ctrl;
        union { // name: extra_dst_alpha_ctrl, offset: 0x5c
            struct {
                unsigned int reserve_0           : 1;
                unsigned int dst_alpha_mode1     : 1;
                unsigned int dst_blend_mode1     : 2;
                unsigned int dst_alpha_cal_mode1 : 1;
                unsigned int dst_factor_mode1    : 3;
                unsigned int reserve_1           : 24;
            } bits;
            unsigned int val;
        } extra_dst_alpha_ctrl;
        union { // name: hdr_src_color_ctrl, offset: 0x60
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
        union { // name: hdr_dst_color_ctrl, offset: 0x64
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
        union { // name: hdr_src_alpha_ctrl, offset: 0x68
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
        union { // name: hdr_dst_alpha_ctrl, offset: 0x6c
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
    } regs;
    unsigned int data[29];
} overlay_port0_rk3572_u;

// 0x00000700
typedef union overlay_port1_rk3572 {
    struct {
        union { // name: overlay_ctrl, offset: 0x0
            struct {
                unsigned int overlay_mode : 1;
                unsigned int reserve_0    : 31;
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
    } regs;
    unsigned int data[29];
} overlay_port1_rk3572_u;

// 0x00000800
typedef union overlay_port2_rk3572 {
    struct {
        union { // name: overlay_ctrl, offset: 0x0
            struct {
                unsigned int overlay_mode : 1;
                unsigned int reserve_0    : 31;
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
    } regs;
    unsigned int data[29];
} overlay_port2_rk3572_u;

// 0x00000c00
typedef union post0_ctrl_rk3572 {
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
                unsigned int reserve_2             : 1;
                unsigned int gamma_update_en       : 1;
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
                unsigned int color_bar_en   : 1;
                unsigned int color_bar_mode : 1;
                unsigned int reserve_0      : 2;
                unsigned int io_vsync_sel   : 2;
                unsigned int reserve_1      : 2;
                unsigned int vfp_dma_stop   : 1;
                unsigned int reserve_2      : 23;
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
        union { // name: post_3d_lut_ctrl, offset: 0x10
            struct {
                unsigned int dsp_3dlut_en        : 1;
                unsigned int dsp_3dlut_bypass_en : 1;
                unsigned int dsp_3dlut_update_en : 1;
                unsigned int dsp_3dlut_mode      : 1;
                unsigned int dsp_3dlut_gating_en : 1;
                unsigned int reserve_0           : 11;
                unsigned int dsp_3dlut_addr      : 16;
            } bits;
            unsigned int val;
        } post_3d_lut_ctrl;
        union { // name: post_3d_lut_r, offset: 0x14
            struct {
                unsigned int lut_3d_r_comp : 12;
                unsigned int reserve_0     : 20;
            } bits;
            unsigned int val;
        } post_3d_lut_r;
        union { // name: post_3d_lut_g, offset: 0x18
            struct {
                unsigned int lut_3d_g_comp : 12;
                unsigned int reserve_0     : 20;
            } bits;
            unsigned int val;
        } post_3d_lut_g;
        union { // name: post_3d_lut_b, offset: 0x1c
            struct {
                unsigned int lut_3d_b_comp : 12;
                unsigned int reserve_0     : 20;
            } bits;
            unsigned int val;
        } post_3d_lut_b;
        union { // name: post_3dlut_mst, offset: 0x20
            struct {
                unsigned int post_3dlut_mst : 32;
            } bits;
            unsigned int val;
        } post_3dlut_mst;
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
            unsigned int reserve_data[16];
        } reserve_reg_96_160;
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
            unsigned int reserve_data[9];
        } reserve_reg_172_208;
        union { // name: post_acm_ctrl, offset: 0xd0
            struct {
                unsigned int acm_bypass_en : 1;
                unsigned int acm_y2r_en    : 1;
                unsigned int acm_r2y_en    : 1;
                unsigned int reserve_0     : 5;
                unsigned int acm_r2y_mode  : 3;
                unsigned int reserve_1     : 5;
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
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_240_244;
        union { // name: post_clk_cnt, offset: 0xf4
            struct {
                unsigned int calc_dclk_cnt : 15;
                unsigned int calc_clk_en   : 1;
                unsigned int calc_aclk_cnt : 16;
            } bits;
            unsigned int val;
        } post_clk_cnt;
        union { // name: post_mcu_ctrl, offset: 0xf8
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
    } regs;
    unsigned int data[63];
} post0_ctrl_rk3572_u;

// 0x00000d00
typedef union post1_ctrl_rk3572 {
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
                unsigned int reserve_2             : 1;
                unsigned int gamma_update_en       : 1;
                unsigned int reserve_3             : 1;
                unsigned int dsp_blank_en          : 1;
                unsigned int reserve_4             : 1;
                unsigned int dsp_out_zero          : 1;
                unsigned int dsp_black_en          : 1;
                unsigned int dsp_lut_en            : 1;
                unsigned int reserve_5             : 1;
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
                unsigned int color_bar_en   : 1;
                unsigned int color_bar_mode : 1;
                unsigned int reserve_0      : 2;
                unsigned int io_vsync_sel   : 2;
                unsigned int reserve_1      : 26;
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
                unsigned int reserve_1              : 25;
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
        union { // name: post_bcsh_ctrl, offset: 0x60
            struct {
                unsigned int bcsh_y2r_en       : 1;
                unsigned int reserve_0         : 1;
                unsigned int bcsh_y2r_csc_mode : 2;
                unsigned int bcsh_r2y_en       : 1;
                unsigned int reserve_1         : 1;
                unsigned int bcsh_r2y_csc_mode : 2;
                unsigned int reserve_2         : 24;
            } bits;
            unsigned int val;
        } post_bcsh_ctrl;
        union { // name: post_bcsh_bcs, offset: 0x64
            struct {
                unsigned int brightness : 8;
                unsigned int contrast   : 9;
                unsigned int reserve_0  : 3;
                unsigned int sat_con    : 10;
                unsigned int out_mode   : 2;
            } bits;
            unsigned int val;
        } post_bcsh_bcs;
        union { // name: post_bcsh_h, offset: 0x68
            struct {
                unsigned int sin_hue   : 9;
                unsigned int reserve_0 : 7;
                unsigned int cos_hue   : 9;
                unsigned int reserve_1 : 7;
            } bits;
            unsigned int val;
        } post_bcsh_h;
        union { // name: post_bcsh_color_bar, offset: 0x6c
            struct {
                unsigned int color_bar_y : 10;
                unsigned int color_bar_u : 10;
                unsigned int color_bar_v : 10;
                unsigned int reserve_0   : 1;
                unsigned int bcsh_en     : 1;
            } bits;
            unsigned int val;
        } post_bcsh_color_bar;
        struct {
            unsigned int reserve_data[12];
        } reserve_reg_112_160;
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
            unsigned int reserve_data[18];
        } reserve_reg_172_244;
        union { // name: post_clk_cnt, offset: 0xf4
            struct {
                unsigned int calc_dclk_cnt : 15;
                unsigned int calc_clk_en   : 1;
                unsigned int calc_aclk_cnt : 16;
            } bits;
            unsigned int val;
        } post_clk_cnt;
        union { // name: post_mcu_ctrl, offset: 0xf8
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
    } regs;
    unsigned int data[63];
} post1_ctrl_rk3572_u;

// 0x00000e00
typedef union post2_ctrl_rk3572 {
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
                unsigned int reserve_2             : 1;
                unsigned int dither_down_en        : 1;
                unsigned int dither_down_sel       : 2;
                unsigned int dither_down_mode      : 1;
                unsigned int reserve_3             : 1;
                unsigned int gamma_update_en       : 1;
                unsigned int post_lb_mode          : 1;
                unsigned int dsp_blank_en          : 1;
                unsigned int reserve_4             : 1;
                unsigned int dsp_out_zero          : 1;
                unsigned int dsp_black_en          : 1;
                unsigned int dsp_lut_en            : 1;
                unsigned int reserve_5             : 1;
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
                unsigned int color_bar_en   : 1;
                unsigned int color_bar_mode : 1;
                unsigned int reserve_0      : 2;
                unsigned int io_vsync_sel   : 2;
                unsigned int reserve_1      : 26;
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
                unsigned int post_hor_sd_en : 1;
                unsigned int post_ver_sd_en : 1;
                unsigned int reserve_0      : 30;
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
        union { // name: post_bcsh_ctrl, offset: 0x60
            struct {
                unsigned int bcsh_y2r_en       : 1;
                unsigned int reserve_0         : 1;
                unsigned int bcsh_y2r_csc_mode : 2;
                unsigned int bcsh_r2y_en       : 1;
                unsigned int reserve_1         : 1;
                unsigned int bcsh_r2y_csc_mode : 2;
                unsigned int reserve_2         : 24;
            } bits;
            unsigned int val;
        } post_bcsh_ctrl;
        union { // name: post_bcsh_bcs, offset: 0x64
            struct {
                unsigned int brightness : 8;
                unsigned int contrast   : 9;
                unsigned int reserve_0  : 3;
                unsigned int sat_con    : 10;
                unsigned int out_mode   : 2;
            } bits;
            unsigned int val;
        } post_bcsh_bcs;
        union { // name: post_bcsh_h, offset: 0x68
            struct {
                unsigned int sin_hue   : 9;
                unsigned int reserve_0 : 7;
                unsigned int cos_hue   : 9;
                unsigned int reserve_1 : 7;
            } bits;
            unsigned int val;
        } post_bcsh_h;
        union { // name: post_bcsh_color_bar, offset: 0x6c
            struct {
                unsigned int color_bar_y : 10;
                unsigned int color_bar_u : 10;
                unsigned int color_bar_v : 10;
                unsigned int reserve_0   : 1;
                unsigned int bcsh_en     : 1;
            } bits;
            unsigned int val;
        } post_bcsh_color_bar;
        struct {
            unsigned int reserve_data[12];
        } reserve_reg_112_160;
        union { // name: post_frc_lower01_0, offset: 0xa0
            struct {
                unsigned int lower01_frm0 : 16;
                unsigned int lower01_frm1 : 16;
            } bits;
            unsigned int val;
        } post_frc_lower01_0;
        union { // name: post_frc_lower01_1, offset: 0xa4
            struct {
                unsigned int lower01_frm2 : 16;
                unsigned int lower01_frm3 : 16;
            } bits;
            unsigned int val;
        } post_frc_lower01_1;
        union { // name: post_frc_lower10_0, offset: 0xa8
            struct {
                unsigned int lower10_frm0 : 16;
                unsigned int lower10_frm1 : 16;
            } bits;
            unsigned int val;
        } post_frc_lower10_0;
        union { // name: post_frc_lower10_1, offset: 0xac
            struct {
                unsigned int lower10_frm2 : 16;
                unsigned int lower10_frm3 : 16;
            } bits;
            unsigned int val;
        } post_frc_lower10_1;
        union { // name: post_frc_lower11_0, offset: 0xb0
            struct {
                unsigned int lower11_frm0 : 16;
                unsigned int lower11_frm1 : 16;
            } bits;
            unsigned int val;
        } post_frc_lower11_0;
        union { // name: post_frc_lower11_1, offset: 0xb4
            struct {
                unsigned int lower11_frm2 : 16;
                unsigned int lower11_frm3 : 16;
            } bits;
            unsigned int val;
        } post_frc_lower11_1;
        struct {
            unsigned int reserve_data[15];
        } reserve_reg_184_244;
        union { // name: post_clk_cnt, offset: 0xf4
            struct {
                unsigned int calc_dclk_cnt : 15;
                unsigned int calc_clk_en   : 1;
                unsigned int calc_aclk_cnt : 16;
            } bits;
            unsigned int val;
        } post_clk_cnt;
        union { // name: post_mcu_ctrl, offset: 0xf8
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
    } regs;
    unsigned int data[63];
} post2_ctrl_rk3572_u;

// 0x00001000
typedef union cluster0_rk3572 {
    struct {
        union { // name: win0_ctrl0, offset: 0x0
            struct {
                unsigned int win0_en               : 1;
                unsigned int win0_data_fmt         : 6;
                unsigned int win0_tile_mode_sel    : 1;
                unsigned int win0_csc_y2r_en       : 1;
                unsigned int win0_csc_r2y_en       : 1;
                unsigned int win0_csc_mode         : 3;
                unsigned int reserve_0             : 1;
                unsigned int win0_rb_swap          : 1;
                unsigned int win0_alpha_swap       : 1;
                unsigned int win0_rg_swap          : 1;
                unsigned int win0_uv_swap          : 1;
                unsigned int win0_dither_up_en     : 1;
                unsigned int win0_yuv_clip         : 1;
                unsigned int reserve_1             : 1;
                unsigned int win0_y_mir            : 1;
                unsigned int reserve_2             : 2;
                unsigned int win0_csc_y2r_force_en : 1;
                unsigned int reserve_3             : 7;
            } bits;
            unsigned int val;
        } win0_ctrl0;
        union { // name: win0_ctrl1, offset: 0x4
            struct {
                unsigned int win0_yrgb_axi_gather_en : 1;
                unsigned int reserve_0               : 3;
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
                unsigned int win0_rid_yrgb : 4;
                unsigned int reserve_0     : 1;
                unsigned int win0_rid_cbr  : 4;
                unsigned int reserve_1     : 23;
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
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_28_32;
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
                unsigned int transformed_xoffset : 4;
                unsigned int reserve_0           : 12;
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
                unsigned int reserve_2                   : 14;
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
                unsigned int win1_en               : 1;
                unsigned int win1_data_fmt         : 6;
                unsigned int reserve_0             : 1;
                unsigned int win1_csc_y2r_en       : 1;
                unsigned int win1_csc_r2y_en       : 1;
                unsigned int win1_csc_mode         : 2;
                unsigned int reserve_1             : 2;
                unsigned int win1_rb_swap          : 1;
                unsigned int reserve_2             : 1;
                unsigned int win1_rg_swap          : 1;
                unsigned int win1_alpha_swap       : 1;
                unsigned int win1_uv_swap          : 1;
                unsigned int win1_dither_up_en     : 1;
                unsigned int win1_yuv_clip         : 1;
                unsigned int win1_y_mir            : 1;
                unsigned int reserve_3             : 2;
                unsigned int win1_csc_y2r_force_en : 1;
                unsigned int reserve_4             : 7;
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
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_156_160;
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
                unsigned int reserve_2                   : 14;
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
                unsigned int reserve_1               : 3;
                unsigned int cluster_scl_lb_mode     : 2;
                unsigned int reserve_2               : 1;
                unsigned int cluster_dma_stop        : 1;
                unsigned int reserve_3               : 1;
                unsigned int cluster_mmu_bypass      : 1;
                unsigned int reserve_4               : 1;
                unsigned int cluster_dma_hurry_en    : 1;
                unsigned int cluster_dma_hurry_thold : 2;
                unsigned int reserve_5               : 9;
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
                unsigned int dci_en       : 1;
                unsigned int uv_adjust_en : 1;
                unsigned int csc_range    : 1;
                unsigned int reserve_0    : 1;
                unsigned int dma_rid      : 5;
                unsigned int reserve_1    : 3;
                unsigned int dma_rlen     : 2;
                unsigned int reserve_2    : 18;
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
            unsigned int reserve_data[48];
        } reserve_reg_308_500;
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
    } regs;
    unsigned int data[127];
} cluster0_rk3572_u;

// 0x00001200
typedef union cluster1_rk3572 {
    struct {
        union { // name: win0_ctrl0, offset: 0x0
            struct {
                unsigned int win0_en               : 1;
                unsigned int win0_data_fmt         : 6;
                unsigned int win0_tile_mode_sel    : 1;
                unsigned int win0_csc_y2r_en       : 1;
                unsigned int win0_csc_r2y_en       : 1;
                unsigned int win0_csc_mode         : 3;
                unsigned int reserve_0             : 1;
                unsigned int win0_rb_swap          : 1;
                unsigned int win0_alpha_swap       : 1;
                unsigned int win0_rg_swap          : 1;
                unsigned int win0_uv_swap          : 1;
                unsigned int win0_dither_up_en     : 1;
                unsigned int win0_yuv_clip         : 1;
                unsigned int reserve_1             : 1;
                unsigned int win0_y_mir            : 1;
                unsigned int reserve_2             : 2;
                unsigned int win0_csc_y2r_force_en : 1;
                unsigned int reserve_3             : 7;
            } bits;
            unsigned int val;
        } win0_ctrl0;
        union { // name: win0_ctrl1, offset: 0x4
            struct {
                unsigned int win0_yrgb_axi_gather_en : 1;
                unsigned int reserve_0               : 3;
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
                unsigned int win0_rid_yrgb : 4;
                unsigned int reserve_0     : 1;
                unsigned int win0_rid_cbr  : 4;
                unsigned int reserve_1     : 23;
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
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_28_32;
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
                unsigned int transformed_xoffset : 4;
                unsigned int reserve_0           : 12;
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
                unsigned int reserve_2                   : 14;
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
                unsigned int win1_en               : 1;
                unsigned int win1_data_fmt         : 6;
                unsigned int reserve_0             : 1;
                unsigned int win1_csc_y2r_en       : 1;
                unsigned int win1_csc_r2y_en       : 1;
                unsigned int win1_csc_mode         : 2;
                unsigned int reserve_1             : 2;
                unsigned int win1_rb_swap          : 1;
                unsigned int reserve_2             : 1;
                unsigned int win1_rg_swap          : 1;
                unsigned int win1_alpha_swap       : 1;
                unsigned int win1_uv_swap          : 1;
                unsigned int win1_dither_up_en     : 1;
                unsigned int win1_yuv_clip         : 1;
                unsigned int win1_y_mir            : 1;
                unsigned int reserve_3             : 2;
                unsigned int win1_csc_y2r_force_en : 1;
                unsigned int reserve_4             : 7;
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
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_156_160;
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
                unsigned int reserve_2                   : 14;
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
                unsigned int reserve_1               : 3;
                unsigned int cluster_scl_lb_mode     : 2;
                unsigned int reserve_2               : 1;
                unsigned int cluster_dma_stop        : 1;
                unsigned int reserve_3               : 1;
                unsigned int cluster_mmu_bypass      : 1;
                unsigned int reserve_4               : 1;
                unsigned int cluster_dma_hurry_en    : 1;
                unsigned int cluster_dma_hurry_thold : 2;
                unsigned int reserve_5               : 9;
                unsigned int cluster_fbcd_overlap_en : 1;
                unsigned int clusrer_fbcd_priorit_en : 1;
                unsigned int fbcd_bug_fix_dis        : 1;
                unsigned int cluster_frm_resetn_en   : 1;
            } bits;
            unsigned int val;
        } cluster_ctrl;
        struct {
            unsigned int reserve_data[60];
        } reserve_reg_260_500;
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
    } regs;
    unsigned int data[127];
} cluster1_rk3572_u;

// 0x00001800
typedef union esmart0_rk3572 {
    struct {
        union { // name: esmart_ctrl0, offset: 0x0
            struct {
                unsigned int esmart_yuv2rgb_en       : 1;
                unsigned int esmart_rgb2yuv_en       : 1;
                unsigned int esmart_csc_mode         : 2;
                unsigned int esmart_8bpp_lut_en      : 1;
                unsigned int esmart_8bpp_alpha_en    : 1;
                unsigned int reserve_0               : 2;
                unsigned int esmart_mid_swap         : 1;
                unsigned int esmart_endian_swap      : 1;
                unsigned int reserve_1               : 2;
                unsigned int esmart_scl_num          : 2;
                unsigned int reserve_2               : 2;
                unsigned int esmart_y2r_csc_13bit_en : 1;
                unsigned int reserve_3               : 7;
                unsigned int esmart_yuv2rgb_force_en : 1;
                unsigned int reserve_4               : 6;
                unsigned int esmart_frm_resetn_en    : 1;
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
                unsigned int reserve_1              : 15;
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
            unsigned int reserve_data[6];
        } reserve_reg_220_244;
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
    } regs;
    unsigned int data[63];
} esmart0_rk3572_u;

// 0x00001a00
typedef union esmart1_rk3572 {
    struct {
        union { // name: esmart_ctrl0, offset: 0x0
            struct {
                unsigned int esmart_yuv2rgb_en       : 1;
                unsigned int esmart_rgb2yuv_en       : 1;
                unsigned int esmart_csc_mode         : 2;
                unsigned int esmart_8bpp_lut_en      : 1;
                unsigned int esmart_8bpp_alpha_en    : 1;
                unsigned int reserve_0               : 2;
                unsigned int esmart_mid_swap         : 1;
                unsigned int esmart_endian_swap      : 1;
                unsigned int reserve_1               : 2;
                unsigned int esmart_scl_num          : 2;
                unsigned int reserve_2               : 10;
                unsigned int esmart_yuv2rgb_force_en : 1;
                unsigned int reserve_3               : 6;
                unsigned int esmart_frm_resetn_en    : 1;
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
                unsigned int reserve_1              : 15;
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
            unsigned int reserve_data[6];
        } reserve_reg_220_244;
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
    } regs;
    unsigned int data[63];
} esmart1_rk3572_u;

// 0x00001c00
typedef union esmart2_rk3572 {
    struct {
        union { // name: esmart_ctrl0, offset: 0x0
            struct {
                unsigned int esmart_yuv2rgb_en       : 1;
                unsigned int esmart_rgb2yuv_en       : 1;
                unsigned int esmart_csc_mode         : 2;
                unsigned int esmart_8bpp_lut_en      : 1;
                unsigned int esmart_8bpp_alpha_en    : 1;
                unsigned int reserve_0               : 2;
                unsigned int esmart_mid_swap         : 1;
                unsigned int esmart_endian_swap      : 1;
                unsigned int reserve_1               : 2;
                unsigned int esmart_scl_num          : 2;
                unsigned int reserve_2               : 10;
                unsigned int esmart_yuv2rgb_force_en : 1;
                unsigned int reserve_3               : 6;
                unsigned int esmart_frm_resetn_en    : 1;
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
                unsigned int reserve_1              : 15;
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
            unsigned int reserve_data[6];
        } reserve_reg_220_244;
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
    } regs;
    unsigned int data[63];
} esmart2_rk3572_u;

// 0x00001e00
typedef union esmart3_rk3572 {
    struct {
        union { // name: esmart_ctrl0, offset: 0x0
            struct {
                unsigned int esmart_yuv2rgb_en       : 1;
                unsigned int esmart_rgb2yuv_en       : 1;
                unsigned int esmart_csc_mode         : 2;
                unsigned int esmart_8bpp_lut_en      : 1;
                unsigned int esmart_8bpp_alpha_en    : 1;
                unsigned int reserve_0               : 2;
                unsigned int esmart_mid_swap         : 1;
                unsigned int esmart_endian_swap      : 1;
                unsigned int reserve_1               : 2;
                unsigned int esmart_scl_num          : 2;
                unsigned int reserve_2               : 10;
                unsigned int esmart_yuv2rgb_force_en : 1;
                unsigned int reserve_3               : 6;
                unsigned int esmart_frm_resetn_en    : 1;
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
                unsigned int reserve_1              : 15;
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
            unsigned int reserve_data[6];
        } reserve_reg_220_244;
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
    } regs;
    unsigned int data[63];
} esmart3_0x00001e00_u;

// 0x00002000
typedef union hrk3572k3572 {
    struct {
        union { // name: hdr_lut_ctrl, offset: 0x0
            struct {
                unsigned int hdr_lut_update_en : 1;
                unsigned int hdr_lut_mode      : 1;
                unsigned int reserve_0         : 30;
            } bits;
            unsigned int val;
        } hdr_lut_ctrl;
        union { // name: hdr_lut_mst, offset: 0x4
            struct {
                unsigned int hdr_lut_mst : 32;
            } bits;
            unsigned int val;
        } hdr_lut_mst;
        union { // name: hdr_lut_status, offset: 0x8
            struct {
                unsigned int hdr_lut_fetch_done : 1;
                unsigned int reserve_0          : 31;
            } bits;
            unsigned int val;
        } hdr_lut_status;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_12_16;
        union { // name: sdr2hdr_ctrl, offset: 0x10
            struct {
                unsigned int sdr2hdr_en        : 1;
                unsigned int sdr2hdr_gating_en : 1;
                unsigned int sdr2hdr_bypass_en : 1;
                unsigned int sdr2hdr_dstmode   : 1;
                unsigned int reserve_0         : 28;
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
                unsigned int coe00     : 14;
                unsigned int reserve_0 : 2;
                unsigned int coe01     : 14;
                unsigned int reserve_1 : 2;
            } bits;
            unsigned int val;
        } sdr_csc_coe00_01;
        union { // name: sdr_csc_coe02_10, offset: 0x20
            struct {
                unsigned int coe02     : 14;
                unsigned int reserve_0 : 2;
                unsigned int coe10     : 14;
                unsigned int reserve_1 : 2;
            } bits;
            unsigned int val;
        } sdr_csc_coe02_10;
        union { // name: sdr_csc_coe11_12, offset: 0x24
            struct {
                unsigned int coe11     : 14;
                unsigned int reserve_0 : 2;
                unsigned int coe12     : 14;
                unsigned int reserve_1 : 2;
            } bits;
            unsigned int val;
        } sdr_csc_coe11_12;
        union { // name: sdr_csc_coe20_21, offset: 0x28
            struct {
                unsigned int coe20     : 14;
                unsigned int reserve_0 : 2;
                unsigned int coe21     : 14;
                unsigned int reserve_1 : 2;
            } bits;
            unsigned int val;
        } sdr_csc_coe20_21;
        union { // name: sdr_csc_coe22, offset: 0x2c
            struct {
                unsigned int coe22     : 14;
                unsigned int reserve_0 : 18;
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
        union { // name: hdr_pq_gamma, offset: 0x44
            struct {
                unsigned int pq_gamma_b : 8;
                unsigned int reserve_0  : 8;
                unsigned int pq_gamma_k : 11;
                unsigned int reserve_1  : 5;
            } bits;
            unsigned int val;
        } hdr_pq_gamma;
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
        union { // name: hdr_csc_coe00_01, offset: 0x54
            struct {
                unsigned int coe00 : 16;
                unsigned int coe01 : 16;
            } bits;
            unsigned int val;
        } hdr_csc_coe00_01;
        union { // name: hdr_csc_coe02_10, offset: 0x58
            struct {
                unsigned int coe02 : 16;
                unsigned int coe10 : 16;
            } bits;
            unsigned int val;
        } hdr_csc_coe02_10;
        union { // name: hdr_csc_coe11_12, offset: 0x5c
            struct {
                unsigned int coe11 : 16;
                unsigned int coe12 : 16;
            } bits;
            unsigned int val;
        } hdr_csc_coe11_12;
        union { // name: hdr_csc_coe20_21, offset: 0x60
            struct {
                unsigned int coe20 : 16;
                unsigned int coe21 : 16;
            } bits;
            unsigned int val;
        } hdr_csc_coe20_21;
        union { // name: hdr_csc_coe22, offset: 0x64
            struct {
                unsigned int coe22     : 16;
                unsigned int reserve_0 : 16;
            } bits;
            unsigned int val;
        } hdr_csc_coe22;
        struct {
            unsigned int reserve_data[6];
        } reserve_reg_104_128;
        union { // name: hdr_debug_ctrl, offset: 0x80
            struct {
                unsigned int sw_h_active    : 12;
                unsigned int reserve_0      : 3;
                unsigned int debug_en       : 1;
                unsigned int sw_v_active    : 12;
                unsigned int debug_mode_sel : 4;
            } bits;
            unsigned int val;
        } hdr_debug_ctrl;
        union { // name: debug_point0_cfg, offset: 0x84
            struct {
                unsigned int debug_point0_h : 12;
                unsigned int reserve_0      : 4;
                unsigned int debug_point0_v : 12;
                unsigned int reserve_1      : 4;
            } bits;
            unsigned int val;
        } debug_point0_cfg;
        union { // name: debug_point1_cfg, offset: 0x88
            struct {
                unsigned int debug_point1_h : 12;
                unsigned int reserve_0      : 4;
                unsigned int debug_point1_v : 12;
                unsigned int reserve_1      : 4;
            } bits;
            unsigned int val;
        } debug_point1_cfg;
        union { // name: debug_point0_r0, offset: 0x8c
            struct {
                unsigned int debug_point0_r0 : 24;
                unsigned int reserve_0       : 8;
            } bits;
            unsigned int val;
        } debug_point0_r0;
        union { // name: debug_point0_g0, offset: 0x90
            struct {
                unsigned int debug_point0_g0 : 24;
                unsigned int reserve_0       : 8;
            } bits;
            unsigned int val;
        } debug_point0_g0;
        union { // name: debug_point0_b0, offset: 0x94
            struct {
                unsigned int debug_point0_b0 : 24;
                unsigned int reserve_0       : 8;
            } bits;
            unsigned int val;
        } debug_point0_b0;
        union { // name: debug_point0_r1, offset: 0x98
            struct {
                unsigned int debug_point0_r1 : 24;
                unsigned int reserve_0       : 8;
            } bits;
            unsigned int val;
        } debug_point0_r1;
        union { // name: debug_point0_g1, offset: 0x9c
            struct {
                unsigned int debug_point0_g1 : 24;
                unsigned int reserve_0       : 8;
            } bits;
            unsigned int val;
        } debug_point0_g1;
        union { // name: debug_point0_b1, offset: 0xa0
            struct {
                unsigned int debug_point0_b1 : 24;
                unsigned int reserve_0       : 8;
            } bits;
            unsigned int val;
        } debug_point0_b1;
        union { // name: debug_point1_r0, offset: 0xa4
            struct {
                unsigned int debug_point0_r0 : 24;
                unsigned int reserve_0       : 8;
            } bits;
            unsigned int val;
        } debug_point1_r0;
        union { // name: debug_point1_g0, offset: 0xa8
            struct {
                unsigned int debug_point1_g0 : 24;
                unsigned int reserve_0       : 8;
            } bits;
            unsigned int val;
        } debug_point1_g0;
        union { // name: debug_point1_b0, offset: 0xac
            struct {
                unsigned int debug_point1_b0 : 24;
                unsigned int reserve_0       : 8;
            } bits;
            unsigned int val;
        } debug_point1_b0;
        union { // name: debug_point1_r1, offset: 0xb0
            struct {
                unsigned int debug_point1_r1 : 24;
                unsigned int reserve_0       : 8;
            } bits;
            unsigned int val;
        } debug_point1_r1;
        union { // name: debug_point1_g1, offset: 0xb4
            struct {
                unsigned int debug_point1_g1 : 24;
                unsigned int reserve_0       : 8;
            } bits;
            unsigned int val;
        } debug_point1_g1;
        union { // name: debug_point1_b1, offset: 0xb8
            struct {
                unsigned int debug_point1_b1 : 24;
                unsigned int reserve_0       : 8;
            } bits;
            unsigned int val;
        } debug_point1_b1;
        struct {
            unsigned int reserve_data[32];
        } reserve_reg_188_316;
        union { // name: hdr_tone_sca, offset: 0x13c
            struct {
                unsigned int addr      : 1;
                unsigned int reserve_0 : 31;
            } bits;
            unsigned int val;
        } hdr_tone_sca;
        struct {
            unsigned int reserve_data[256];
        } reserve_reg_320_1344;
        union { // name: hdrgamma_curve, offset: 0x540
            struct {
                unsigned int addr      : 1;
                unsigned int reserve_0 : 31;
            } bits;
            unsigned int val;
        } hdrgamma_curve;
        struct {
            unsigned int reserve_data[83];
        } reserve_reg_1348_1680;
        union { // name: hdrgamma_mdfvalue, offset: 0x690
            struct {
                unsigned int addr      : 1;
                unsigned int reserve_0 : 31;
            } bits;
            unsigned int val;
        } hdrgamma_mdfvalue;
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
        union { // name: sdr_smgain, offset: 0x900
            struct {
                unsigned int addr      : 1;
                unsigned int reserve_0 : 31;
            } bits;
            unsigned int val;
        } sdr_smgain;
    } regs;
    unsigned int data[577];
} hdr_vivid_rk3572_u;

// 0x00005000
typedef union gamma_lut_wraddr_rk3572 {
    struct {
    } regs;
    unsigned int data[0];
} gamma_lut_wraddr_rk3572_u;

// 0x00006000
typedef union bpp_lut_wraddr_rk3572 {
    struct {
    } regs;
    unsigned int data[0];
} bpp_lut_wraddr_rk3572_u;

// 0x00006400
typedef union acm_rk3572 {
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
} acm_rk3572_u;

// 0x00006c00
typedef union sharp_rk3572 {
    struct {
        union { // name: ctrl, offset: 0x0
            struct {
                unsigned int sw_sharp_enable              : 1;
                unsigned int sw_lti_enable                : 1;
                unsigned int sw_cti_enable                : 1;
                unsigned int sw_peaking_enable            : 1;
                unsigned int sw_peaking_ctrl_enable       : 1;
                unsigned int sw_peaking_shoot_ctrl_enable : 1;
                unsigned int sw_edge_proc_enable          : 1;
                unsigned int sw_shoot_ctrl_enable         : 1;
                unsigned int sw_gain_ctrl_enable          : 1;
                unsigned int sw_color_adj_enable          : 1;
                unsigned int sw_texture_adj_enable        : 1;
                unsigned int sw_ink_enable                : 1;
                unsigned int reserve_0                    : 20;
            } bits;
            unsigned int val;
        } ctrl;
        union { // name: auto_gating_imd, offset: 0x4
            struct {
                unsigned int reserve_0                       : 1;
                unsigned int sw_lti_gating_en                : 1;
                unsigned int sw_cti_gating_en                : 1;
                unsigned int sw_peaking_gating_en            : 1;
                unsigned int sw_peaking_ctrl_gating_en       : 1;
                unsigned int sw_peaking_shoot_ctrl_gating_en : 1;
                unsigned int sw_edge_proc_gating_en          : 1;
                unsigned int sw_shoot_ctrl_gating_en         : 1;
                unsigned int sw_gain_ctrl_gating_en          : 1;
                unsigned int sw_color_adj_gating_en          : 1;
                unsigned int sw_texture_adj_gating_en        : 1;
                unsigned int reserve_1                       : 21;
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
                unsigned int sw_peaking0_ratio_p12          : 12;
                unsigned int sw_peaking0_ratio_p23          : 12;
                unsigned int sw_peaking0_shoot_delta_offset : 8;
            } bits;
            unsigned int val;
        } peaking0_ctrl_coe9;
        union { // name: peaking0_ctrl_coe10, offset: 0x58
            struct {
                unsigned int sw_peaking0_shoot_alpha_over          : 7;
                unsigned int reserve_0                             : 1;
                unsigned int sw_peaking0_shoot_alpha_under         : 7;
                unsigned int reserve_1                             : 1;
                unsigned int sw_peaking0_shoot_alpha_over_unlimit  : 7;
                unsigned int reserve_2                             : 1;
                unsigned int sw_peaking0_shoot_alpha_under_unlimit : 7;
                unsigned int reserve_3                             : 1;
            } bits;
            unsigned int val;
        } peaking0_ctrl_coe10;
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
                unsigned int sw_peaking1_ratio_p12          : 12;
                unsigned int sw_peaking1_ratio_p23          : 12;
                unsigned int sw_peaking1_shoot_delta_offset : 8;
            } bits;
            unsigned int val;
        } peaking1_ctrl_coe9;
        union { // name: peaking1_ctrl_coe10, offset: 0x84
            struct {
                unsigned int sw_peaking1_shoot_alpha_over          : 7;
                unsigned int reserve_0                             : 1;
                unsigned int sw_peaking1_shoot_alpha_under         : 7;
                unsigned int reserve_1                             : 1;
                unsigned int sw_peaking1_shoot_alpha_over_unlimit  : 7;
                unsigned int reserve_2                             : 1;
                unsigned int sw_peaking1_shoot_alpha_under_unlimit : 7;
                unsigned int reserve_3                             : 1;
            } bits;
            unsigned int val;
        } peaking1_ctrl_coe10;
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
                unsigned int sw_peaking2_ratio_p12          : 12;
                unsigned int sw_peaking2_ratio_p23          : 12;
                unsigned int sw_peaking2_shoot_delta_offset : 8;
            } bits;
            unsigned int val;
        } peaking2_ctrl_coe9;
        union { // name: peaking2_ctrl_coe10, offset: 0xb0
            struct {
                unsigned int sw_peaking2_shoot_alpha_over          : 7;
                unsigned int reserve_0                             : 1;
                unsigned int sw_peaking2_shoot_alpha_under         : 7;
                unsigned int reserve_1                             : 1;
                unsigned int sw_peaking2_shoot_alpha_over_unlimit  : 7;
                unsigned int reserve_2                             : 1;
                unsigned int sw_peaking2_shoot_alpha_under_unlimit : 7;
                unsigned int reserve_3                             : 1;
            } bits;
            unsigned int val;
        } peaking2_ctrl_coe10;
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
                unsigned int sw_peaking3_ratio_p12          : 12;
                unsigned int sw_peaking3_ratio_p23          : 12;
                unsigned int sw_peaking3_shoot_delta_offset : 8;
            } bits;
            unsigned int val;
        } peaking3_ctrl_coe9;
        union { // name: peaking3_ctrl_coe10, offset: 0xdc
            struct {
                unsigned int sw_peaking3_shoot_alpha_over          : 7;
                unsigned int reserve_0                             : 1;
                unsigned int sw_peaking3_shoot_alpha_under         : 7;
                unsigned int reserve_1                             : 1;
                unsigned int sw_peaking3_shoot_alpha_over_unlimit  : 7;
                unsigned int reserve_2                             : 1;
                unsigned int sw_peaking3_shoot_alpha_under_unlimit : 7;
                unsigned int reserve_3                             : 1;
            } bits;
            unsigned int val;
        } peaking3_ctrl_coe10;
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
                unsigned int sw_peaking4_ratio_p12          : 12;
                unsigned int sw_peaking4_ratio_p23          : 12;
                unsigned int sw_peaking4_shoot_delta_offset : 8;
            } bits;
            unsigned int val;
        } peaking4_ctrl_coe9;
        union { // name: peaking4_ctrl_coe10, offset: 0x108
            struct {
                unsigned int sw_peaking4_shoot_alpha_over          : 7;
                unsigned int reserve_0                             : 1;
                unsigned int sw_peaking4_shoot_alpha_under         : 7;
                unsigned int reserve_1                             : 1;
                unsigned int sw_peaking4_shoot_alpha_over_unlimit  : 7;
                unsigned int reserve_2                             : 1;
                unsigned int sw_peaking4_shoot_alpha_under_unlimit : 7;
                unsigned int reserve_3                             : 1;
            } bits;
            unsigned int val;
        } peaking4_ctrl_coe10;
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
                unsigned int sw_peaking5_ratio_p12          : 12;
                unsigned int sw_peaking5_ratio_p23          : 12;
                unsigned int sw_peaking5_shoot_delta_offset : 8;
            } bits;
            unsigned int val;
        } peaking5_ctrl_coe9;
        union { // name: peaking5_ctrl_coe10, offset: 0x134
            struct {
                unsigned int sw_peaking5_shoot_alpha_over          : 7;
                unsigned int reserve_0                             : 1;
                unsigned int sw_peaking5_shoot_alpha_under         : 7;
                unsigned int reserve_1                             : 1;
                unsigned int sw_peaking5_shoot_alpha_over_unlimit  : 7;
                unsigned int reserve_2                             : 1;
                unsigned int sw_peaking5_shoot_alpha_under_unlimit : 7;
                unsigned int reserve_3                             : 1;
            } bits;
            unsigned int val;
        } peaking5_ctrl_coe10;
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
                unsigned int sw_peaking6_ratio_p12          : 12;
                unsigned int sw_peaking6_ratio_p23          : 12;
                unsigned int sw_peaking6_shoot_delta_offset : 8;
            } bits;
            unsigned int val;
        } peaking6_ctrl_coe9;
        union { // name: peaking6_ctrl_coe10, offset: 0x160
            struct {
                unsigned int sw_peaking6_shoot_alpha_over          : 7;
                unsigned int reserve_0                             : 1;
                unsigned int sw_peaking6_shoot_alpha_under         : 7;
                unsigned int reserve_1                             : 1;
                unsigned int sw_peaking6_shoot_alpha_over_unlimit  : 7;
                unsigned int reserve_2                             : 1;
                unsigned int sw_peaking6_shoot_alpha_under_unlimit : 7;
                unsigned int reserve_3                             : 1;
            } bits;
            unsigned int val;
        } peaking6_ctrl_coe10;
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
                unsigned int sw_peaking7_ratio_p12          : 12;
                unsigned int sw_peaking7_ratio_p23          : 12;
                unsigned int sw_peaking7_shoot_delta_offset : 8;
            } bits;
            unsigned int val;
        } peaking7_ctrl_coe9;
        union { // name: peaking7_ctrl_coe10, offset: 0x18c
            struct {
                unsigned int sw_peaking7_shoot_alpha_over          : 7;
                unsigned int reserve_0                             : 1;
                unsigned int sw_peaking7_shoot_alpha_under         : 7;
                unsigned int reserve_1                             : 1;
                unsigned int sw_peaking7_shoot_alpha_over_unlimit  : 7;
                unsigned int reserve_2                             : 1;
                unsigned int sw_peaking7_shoot_alpha_under_unlimit : 7;
                unsigned int reserve_3                             : 1;
            } bits;
            unsigned int val;
        } peaking7_ctrl_coe10;
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
        union { // name: coloradj_ctrl0, offset: 0x230
            struct {
                unsigned int sw_adj_point_x0      : 10;
                unsigned int reserve_0            : 2;
                unsigned int sw_adj_point_y0      : 10;
                unsigned int reserve_1            : 2;
                unsigned int sw_adj_scaling_coef0 : 3;
                unsigned int reserve_2            : 5;
            } bits;
            unsigned int val;
        } coloradj_ctrl0;
        union { // name: coloradj_ctrl1, offset: 0x234
            struct {
                unsigned int sw_coloradj_tab0_0 : 5;
                unsigned int sw_coloradj_tab0_1 : 5;
                unsigned int sw_coloradj_tab0_2 : 5;
                unsigned int sw_coloradj_tab0_3 : 5;
                unsigned int sw_coloradj_tab0_4 : 5;
                unsigned int sw_coloradj_tab0_5 : 5;
                unsigned int reserve_0          : 2;
            } bits;
            unsigned int val;
        } coloradj_ctrl1;
        union { // name: coloradj_ctrl2, offset: 0x238
            struct {
                unsigned int sw_coloradj_tab0_6  : 5;
                unsigned int sw_coloradj_tab0_7  : 5;
                unsigned int sw_coloradj_tab0_8  : 5;
                unsigned int sw_coloradj_tab0_9  : 5;
                unsigned int sw_coloradj_tab0_10 : 5;
                unsigned int sw_coloradj_tab0_11 : 5;
                unsigned int reserve_0           : 2;
            } bits;
            unsigned int val;
        } coloradj_ctrl2;
        union { // name: coloradj_ctrl3, offset: 0x23c
            struct {
                unsigned int sw_coloradj_tab0_12 : 5;
                unsigned int sw_coloradj_tab0_13 : 5;
                unsigned int sw_coloradj_tab0_14 : 5;
                unsigned int sw_coloradj_tab0_15 : 5;
                unsigned int reserve_0           : 12;
            } bits;
            unsigned int val;
        } coloradj_ctrl3;
        union { // name: coloradj_ctrl4, offset: 0x240
            struct {
                unsigned int sw_adj_point_x1      : 10;
                unsigned int reserve_0            : 2;
                unsigned int sw_adj_point_y1      : 10;
                unsigned int reserve_1            : 2;
                unsigned int sw_adj_scaling_coef1 : 3;
                unsigned int reserve_2            : 5;
            } bits;
            unsigned int val;
        } coloradj_ctrl4;
        union { // name: coloradj_ctrl5, offset: 0x244
            struct {
                unsigned int sw_coloradj_tab1_0 : 5;
                unsigned int sw_coloradj_tab1_1 : 5;
                unsigned int sw_coloradj_tab1_2 : 5;
                unsigned int sw_coloradj_tab1_3 : 5;
                unsigned int sw_coloradj_tab1_4 : 5;
                unsigned int sw_coloradj_tab1_5 : 5;
                unsigned int reserve_0          : 2;
            } bits;
            unsigned int val;
        } coloradj_ctrl5;
        union { // name: coloradj_ctrl6, offset: 0x248
            struct {
                unsigned int sw_coloradj_tab1_6  : 5;
                unsigned int sw_coloradj_tab1_7  : 5;
                unsigned int sw_coloradj_tab1_8  : 5;
                unsigned int sw_coloradj_tab1_9  : 5;
                unsigned int sw_coloradj_tab1_10 : 5;
                unsigned int sw_coloradj_tab1_11 : 5;
                unsigned int reserve_0           : 2;
            } bits;
            unsigned int val;
        } coloradj_ctrl6;
        union { // name: coloradj_ctrl7, offset: 0x24c
            struct {
                unsigned int sw_coloradj_tab1_12 : 5;
                unsigned int sw_coloradj_tab1_13 : 5;
                unsigned int sw_coloradj_tab1_14 : 5;
                unsigned int sw_coloradj_tab1_15 : 5;
                unsigned int reserve_0           : 12;
            } bits;
            unsigned int val;
        } coloradj_ctrl7;
        union { // name: coloradj_ctrl8, offset: 0x250
            struct {
                unsigned int sw_adj_point_x2      : 10;
                unsigned int reserve_0            : 2;
                unsigned int sw_adj_point_y2      : 10;
                unsigned int reserve_1            : 2;
                unsigned int sw_adj_scaling_coef2 : 3;
                unsigned int reserve_2            : 5;
            } bits;
            unsigned int val;
        } coloradj_ctrl8;
        union { // name: coloradj_ctrl9, offset: 0x254
            struct {
                unsigned int sw_coloradj_tab2_0 : 5;
                unsigned int sw_coloradj_tab2_1 : 5;
                unsigned int sw_coloradj_tab2_2 : 5;
                unsigned int sw_coloradj_tab2_3 : 5;
                unsigned int sw_coloradj_tab2_4 : 5;
                unsigned int sw_coloradj_tab2_5 : 5;
                unsigned int reserve_0          : 2;
            } bits;
            unsigned int val;
        } coloradj_ctrl9;
        union { // name: coloradj_ctrl10, offset: 0x258
            struct {
                unsigned int sw_coloradj_tab2_6  : 5;
                unsigned int sw_coloradj_tab2_7  : 5;
                unsigned int sw_coloradj_tab2_8  : 5;
                unsigned int sw_coloradj_tab2_9  : 5;
                unsigned int sw_coloradj_tab2_10 : 5;
                unsigned int sw_coloradj_tab2_11 : 5;
                unsigned int reserve_0           : 2;
            } bits;
            unsigned int val;
        } coloradj_ctrl10;
        union { // name: coloradj_ctrl11, offset: 0x25c
            struct {
                unsigned int sw_coloradj_tab2_12 : 5;
                unsigned int sw_coloradj_tab2_13 : 5;
                unsigned int sw_coloradj_tab2_14 : 5;
                unsigned int sw_coloradj_tab2_15 : 5;
                unsigned int reserve_0           : 12;
            } bits;
            unsigned int val;
        } coloradj_ctrl11;
        union { // name: coloradj_ctrl12, offset: 0x260
            struct {
                unsigned int sw_adj_point_x3      : 10;
                unsigned int reserve_0            : 2;
                unsigned int sw_adj_point_y3      : 10;
                unsigned int reserve_1            : 2;
                unsigned int sw_adj_scaling_coef3 : 3;
                unsigned int reserve_2            : 5;
            } bits;
            unsigned int val;
        } coloradj_ctrl12;
        union { // name: coloradj_ctrl13, offset: 0x264
            struct {
                unsigned int sw_coloradj_tab3_0 : 5;
                unsigned int sw_coloradj_tab3_1 : 5;
                unsigned int sw_coloradj_tab3_2 : 5;
                unsigned int sw_coloradj_tab3_3 : 5;
                unsigned int sw_coloradj_tab3_4 : 5;
                unsigned int sw_coloradj_tab3_5 : 5;
                unsigned int reserve_0          : 2;
            } bits;
            unsigned int val;
        } coloradj_ctrl13;
        union { // name: coloradj_ctrl14, offset: 0x268
            struct {
                unsigned int sw_coloradj_tab3_6  : 5;
                unsigned int sw_coloradj_tab3_7  : 5;
                unsigned int sw_coloradj_tab3_8  : 5;
                unsigned int sw_coloradj_tab3_9  : 5;
                unsigned int sw_coloradj_tab3_10 : 5;
                unsigned int sw_coloradj_tab3_11 : 5;
                unsigned int reserve_0           : 2;
            } bits;
            unsigned int val;
        } coloradj_ctrl14;
        union { // name: coloradj_ctrl15, offset: 0x26c
            struct {
                unsigned int sw_coloradj_tab3_12 : 5;
                unsigned int sw_coloradj_tab3_13 : 5;
                unsigned int sw_coloradj_tab3_14 : 5;
                unsigned int sw_coloradj_tab3_15 : 5;
                unsigned int reserve_0           : 12;
            } bits;
            unsigned int val;
        } coloradj_ctrl15;
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
        union { // name: cti_ctrl0, offset: 0x298
            struct {
                unsigned int sw_ctih_radius : 1;
                unsigned int reserve_0      : 3;
                unsigned int sw_ctih_slp1   : 9;
                unsigned int reserve_1      : 3;
                unsigned int sw_ctih_thr1   : 9;
                unsigned int reserve_2      : 7;
            } bits;
            unsigned int val;
        } cti_ctrl0;
        union { // name: cti_ctrl1, offset: 0x29c
            struct {
                unsigned int sw_ctih_noisethrneg : 10;
                unsigned int reserve_0           : 2;
                unsigned int sw_ctih_noisethrpos : 10;
                unsigned int reserve_1           : 2;
                unsigned int sw_ctih_tigain      : 5;
                unsigned int reserve_2           : 3;
            } bits;
            unsigned int val;
        } cti_ctrl1;
        union { // name: cti_ctrl2, offset: 0x2a0
            struct {
                unsigned int sw_ctiv_radius : 1;
                unsigned int reserve_0      : 3;
                unsigned int sw_ctiv_slp1   : 9;
                unsigned int reserve_1      : 3;
                unsigned int sw_ctiv_thr1   : 9;
                unsigned int reserve_2      : 7;
            } bits;
            unsigned int val;
        } cti_ctrl2;
        union { // name: cti_ctrl3, offset: 0x2a4
            struct {
                unsigned int sw_ctiv_noisethrneg : 10;
                unsigned int reserve_0           : 2;
                unsigned int sw_ctiv_noisethrpos : 10;
                unsigned int reserve_1           : 2;
                unsigned int sw_ctiv_tigain      : 5;
                unsigned int reserve_2           : 3;
            } bits;
            unsigned int val;
        } cti_ctrl3;
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
} sharp_rk3572_u;

// 0x00007e00
typedef union mmu0_rk3572 {
    struct {
        union { // name: mmu_dte_addr, offset: 0x0
            struct {
                unsigned int dte_addr : 32;
            } bits;
            unsigned int val;
        } mmu_dte_addr;
        union { // name: mmu_status, offset: 0x4
            struct {
                unsigned int paging_en           : 1;
                unsigned int page_fault_active   : 1;
                unsigned int stail_active        : 1;
                unsigned int mmu_idle            : 1;
                unsigned int replay_buffer_empty : 1;
                unsigned int page_fault_is_write : 1;
                unsigned int page_fault_bus_id   : 5;
                unsigned int reserve_0           : 21;
            } bits;
            unsigned int val;
        } mmu_status;
        union { // name: mmu_command, offset: 0x8
            struct {
                unsigned int mmu_cmd   : 3;
                unsigned int reserve_0 : 29;
            } bits;
            unsigned int val;
        } mmu_command;
        union { // name: mmu_page_fault_addr, offset: 0xc
            struct {
                unsigned int page_fault_addr : 32;
            } bits;
            unsigned int val;
        } mmu_page_fault_addr;
        union { // name: mmu_zap_one_line, offset: 0x10
            struct {
                unsigned int mmu_zap_one_line : 32;
            } bits;
            unsigned int val;
        } mmu_zap_one_line;
        union { // name: mmu_int_rawstat, offset: 0x14
            struct {
                unsigned int rawst_page_fault : 1;
                unsigned int rawst_bus_error  : 1;
                unsigned int reserve_0        : 30;
            } bits;
            unsigned int val;
        } mmu_int_rawstat;
        union { // name: mmu_int_clear, offset: 0x18
            struct {
                unsigned int clr_page_fault : 1;
                unsigned int clr_bus_error  : 1;
                unsigned int reserve_0      : 30;
            } bits;
            unsigned int val;
        } mmu_int_clear;
        union { // name: mmu_int_mask, offset: 0x1c
            struct {
                unsigned int mask_page_fault : 1;
                unsigned int mask_bus_error  : 1;
                unsigned int reserve_0       : 30;
            } bits;
            unsigned int val;
        } mmu_int_mask;
        union { // name: mmu_int_status, offset: 0x20
            struct {
                unsigned int st_page_fault : 1;
                unsigned int st_bus_error  : 1;
                unsigned int reserve_0     : 30;
            } bits;
            unsigned int val;
        } mmu_int_status;
        union { // name: mmu_auto_gating, offset: 0x24
            struct {
                unsigned int mmu_auto_gating : 1;
                unsigned int mmu_cfg_mode    : 1;
                unsigned int reserve_0       : 30;
            } bits;
            unsigned int val;
        } mmu_auto_gating;
    } regs;
    unsigned int data[10];
} mmu0_rk3572_u;

// 0x00007f00
typedef union mmu1_rk3572 {
    struct {
        union { // name: mmu_dte_addr, offset: 0x0
            struct {
                unsigned int dte_addr : 32;
            } bits;
            unsigned int val;
        } mmu_dte_addr;
        union { // name: mmu_status, offset: 0x4
            struct {
                unsigned int paging_en           : 1;
                unsigned int page_fault_active   : 1;
                unsigned int stail_active        : 1;
                unsigned int mmu_idle            : 1;
                unsigned int replay_buffer_empty : 1;
                unsigned int page_fault_is_write : 1;
                unsigned int page_fault_bus_id   : 5;
                unsigned int reserve_0           : 21;
            } bits;
            unsigned int val;
        } mmu_status;
        union { // name: mmu_command, offset: 0x8
            struct {
                unsigned int mmu_cmd   : 3;
                unsigned int reserve_0 : 29;
            } bits;
            unsigned int val;
        } mmu_command;
        union { // name: mmu_page_fault_addr, offset: 0xc
            struct {
                unsigned int page_fault_addr : 32;
            } bits;
            unsigned int val;
        } mmu_page_fault_addr;
        union { // name: mmu_zap_one_line, offset: 0x10
            struct {
                unsigned int mmu_zap_one_line : 32;
            } bits;
            unsigned int val;
        } mmu_zap_one_line;
        union { // name: mmu_int_rawstat, offset: 0x14
            struct {
                unsigned int rawst_page_fault : 1;
                unsigned int rawst_bus_error  : 1;
                unsigned int reserve_0        : 30;
            } bits;
            unsigned int val;
        } mmu_int_rawstat;
        union { // name: mmu_int_clear, offset: 0x18
            struct {
                unsigned int clr_page_fault : 1;
                unsigned int clr_bus_error  : 1;
                unsigned int reserve_0      : 30;
            } bits;
            unsigned int val;
        } mmu_int_clear;
        union { // name: mmu_int_mask, offset: 0x1c
            struct {
                unsigned int mask_page_fault : 1;
                unsigned int mask_bus_error  : 1;
                unsigned int reserve_0       : 30;
            } bits;
            unsigned int val;
        } mmu_int_mask;
        union { // name: mmu_int_status, offset: 0x20
            struct {
                unsigned int st_page_fault : 1;
                unsigned int st_bus_error  : 1;
                unsigned int reserve_0     : 30;
            } bits;
            unsigned int val;
        } mmu_int_status;
        union { // name: mmu_auto_gating, offset: 0x24
            struct {
                unsigned int mmu_auto_gating : 1;
                unsigned int mmu_cfg_mode    : 1;
                unsigned int reserve_0       : 30;
            } bits;
            unsigned int val;
        } mmu_auto_gating;
    } regs;
    unsigned int data[10];
} mmu1_rk3572_u;

#endif /* VOP_RK3572_H */
