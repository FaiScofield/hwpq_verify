#ifndef __RK3576_VOP_REGS_H__
#define __RK3576_VOP_REGS_H__

typedef union sys_ctrl_0x27d00000_u {
	struct sys_ctrl_0x27d00000_s {
		union sys_reg_cfg_done_u { 
			struct sys_reg_cfg_done_s { 
				unsigned int reg_load_global0_en: 1;
				unsigned int reg_load_global1_en: 1;
				unsigned int reg_load_global2_en: 1;
				unsigned int reserve_0: 1;
				unsigned int reg_load_sys0_en: 1;
				unsigned int reg_load_sys1_en: 1;
				unsigned int reg_load_sys2_en: 1;
				unsigned int reserve_1: 7;
				unsigned int reg_load_wb_en: 1;
				unsigned int sw_global_regdone_en: 1;
				unsigned int write_mask: 16;
			} bits;
			unsigned int u32;
		} sw_sys_reg_cfg_done;
		union sys_version_info_u { 
			struct sys_version_info_s { 
				unsigned int svnbuild: 16;
				unsigned int minor: 8;
				unsigned int major: 8;
			} bits;
			unsigned int u32;
		} sw_sys_version_info;
		union sys_auto_gating_ctrl_imd_u { 
			struct sys_auto_gating_ctrl_imd_s { 
				unsigned int cluster0_aclk_gating_en: 1;
				unsigned int cluster1_aclk_gating_en: 1;
				unsigned int reserve_0: 2;
				unsigned int esmart_scl_gating_en: 1;
				unsigned int reserve_1: 1;
				unsigned int win_aclk_gating_en: 1;
				unsigned int aclk_pre_auto_gating_en: 1;
				unsigned int overlay_aclk_gating_en: 1;
				unsigned int reserve_2: 2;
				unsigned int wb_aclk_gating_en: 1;
				unsigned int reserve_3: 1;
				unsigned int prescan_aclk_gating_en: 1;
				unsigned int port_dclk_gating_en: 1;
				unsigned int axi_aclk_gating_en: 1;
				unsigned int dp_pix_clk_gating_en: 1;
				unsigned int reserve_4: 1;
				unsigned int hdmi_pix_clk_gating_en: 1;
				unsigned int reserve_5: 1;
				unsigned int mipi_pix_clk_gating_en: 1;
				unsigned int reserve_6: 1;
				unsigned int edp_pix_clk_en: 1;
				unsigned int reserve_7: 1;
				unsigned int rgb_clk_gating_en: 1;
				unsigned int reserve_8: 4;
				unsigned int axi0_aclk_static_gating_en: 1;
				unsigned int axi1_aclk_static_gating_en: 1;
				unsigned int auto_gating_en: 1;
			} bits;
			unsigned int u32;
		} sw_sys_auto_gating_ctrl_imd;
		union sys_win_reg_cfg_done_u { 
			struct sys_win_reg_cfg_done_s { 
				unsigned int reg_load_cluster0_en: 1;
				unsigned int reg_load_cluster1_en: 1;
				unsigned int reserve_0: 2;
				unsigned int reg_load_esmart0_en: 1;
				unsigned int reg_load_esmart1_en: 1;
				unsigned int reg_load_esmart2_en: 1;
				unsigned int reg_load_esmart3_en: 1;
				unsigned int reserve_1: 8;
				unsigned int write_mask: 16;
			} bits;
			unsigned int u32;
		} sw_sys_win_reg_cfg_done;
		union sys_axi0_ctrl_imd_u { 
			struct sys_axi0_ctrl_imd_s { 
				unsigned int axi0_dma_stop: 1;
				unsigned int axi0_outstanding_en: 1;
				unsigned int reserve_0: 2;
				unsigned int axi0_outstanding_num: 6;
				unsigned int reserve_1: 6;
				unsigned int axi0_mmu_idle: 1;
				unsigned int reserve_2: 15;
			} bits;
			unsigned int u32;
		} sw_sys_axi0_ctrl_imd;
		union sys_axi_hurry_ctrl0_imd_u { 
			struct sys_axi_hurry_ctrl0_imd_s { 
				unsigned int axi0_hurry_w_en: 1;
				unsigned int axi0_hurry_w_value: 2;
				unsigned int axi0_hurry_w_mode: 2;
				unsigned int reserve_0: 3;
				unsigned int axi0_hurry_en: 1;
				unsigned int axi0_hurry_value: 2;
				unsigned int axi0_hurry_threshold: 1;
				unsigned int axi0_qos_en: 1;
				unsigned int axi0_qos_value: 2;
				unsigned int reserve_1: 17;
			} bits;
			unsigned int u32;
		} sw_sys_axi_hurry_ctrl0_imd;
		union sys_axi_hurry_ctrl1_imd_u { 
			struct sys_axi_hurry_ctrl1_imd_s { 
				unsigned int axi1_hurry_w_en: 1;
				unsigned int axi1_hurry_w_value: 2;
				unsigned int axi1_hurry_w_mode: 2;
				unsigned int reserve_0: 3;
				unsigned int axi1_hurry_en: 1;
				unsigned int axi1_hurry_value: 2;
				unsigned int axi1_hurry_threshold: 1;
				unsigned int axi1_qos_en: 1;
				unsigned int axi1_qos_value: 2;
				unsigned int reserve_1: 17;
			} bits;
			unsigned int u32;
		} sw_sys_axi_hurry_ctrl1_imd;
		union sys_axi1_ctrl_imd_u { 
			struct sys_axi1_ctrl_imd_s { 
				unsigned int axi1_dma_stop: 1;
				unsigned int axi1_outstanding_en: 1;
				unsigned int reserve_0: 2;
				unsigned int axi1_outstanding_num: 6;
				unsigned int reserve_1: 6;
				unsigned int axi1_mmu_idle: 1;
				unsigned int reserve_2: 15;
			} bits;
			unsigned int u32;
		} sw_sys_axi1_ctrl_imd;
		union sys_mmu_ctrl_imd_u { 
			struct sys_mmu_ctrl_imd_s { 
				unsigned int rkmmu2_0_en: 1;
				unsigned int rkmmu2_0_sel: 1;
				unsigned int mmu_bypass_en: 1;
				unsigned int reserve_0: 1;
				unsigned int mmu_bypass_id: 5;
				unsigned int mmu1_bypass_en: 1;
				unsigned int reserve_1: 1;
				unsigned int mmu2_0_soft_rst_en: 1;
				unsigned int mmu_regdone_sel: 2;
				unsigned int mmu1_regdone_sel: 2;
				unsigned int write_mask: 16;
			} bits;
			unsigned int u32;
		} sw_sys_mmu_ctrl_imd;
		union sys_axi_lut_ctrl_imd_u { 
			struct sys_axi_lut_ctrl_imd_s { 
				unsigned int lut_dma_en: 1;
				unsigned int lut_dma_stop: 1;
				unsigned int lut_dma_rlen: 2;
				unsigned int lut_dma_rid: 4;
				unsigned int reserve_0: 1;
				unsigned int lut_use_axi1: 1;
				unsigned int reserve_1: 22;
			} bits;
			unsigned int u32;
		} sw_sys_axi_lut_ctrl_imd;
		union sys_port_ctrl_imd_u { 
			struct sys_port_ctrl_imd_s { 
				unsigned int vp0_interlace_frm_reg_done: 1;
				unsigned int vp1_interlace_frm_reg_done: 1;
				unsigned int vp2_interlace_frm_reg_done: 1;
				unsigned int reserve_0: 1;
				unsigned int dsp_vs_t_sel: 1;
				unsigned int auto_cs_en: 1;
				unsigned int reserve_1: 2;
				unsigned int vfp0_dma_stop_en: 1;
				unsigned int vfp1_dma_stop_en: 1;
				unsigned int vfp2_dma_stop_en: 1;
				unsigned int reserve_2: 5;
				unsigned int write_mask: 16;
			} bits;
			unsigned int u32;
		} sw_sys_port_ctrl_imd;
		struct { 
			unsigned int reserve_data[8];
		} reserve_reg_44_48;
		union sys_cluster_pd_ctrl_imd_u { 
			struct sys_cluster_pd_ctrl_imd_s { 
				unsigned int cluster01_pd_en: 1;
				unsigned int reserve_0: 15;
				unsigned int write_mask: 16;
			} bits;
			unsigned int u32;
		} sw_sys_cluster_pd_ctrl_imd;
		union sys_esmart_pd_ctrl_imd_u { 
			struct sys_esmart_pd_ctrl_imd_s { 
				unsigned int esmart_pd_en: 1;
				unsigned int reserve_0: 5;
				unsigned int esmart_lb_mode: 2;
				unsigned int bpp_lut_en: 1;
				unsigned int reserve_1: 1;
				unsigned int bpp_win_sel: 2;
				unsigned int reserve_2: 4;
				unsigned int write_mask: 16;
			} bits;
			unsigned int u32;
		} sw_sys_esmart_pd_ctrl_imd;
		union sys_var_ferq_ctrl_imd_u { 
			struct sys_var_ferq_ctrl_imd_s { 
				unsigned int dma_finish_mode: 2;
				unsigned int axi_dma_finish_and_en: 1;
				unsigned int wb_dma_finish_and_en: 1;
				unsigned int vp0_line_flag_and_en: 1;
				unsigned int vp1_line_flag_and_en: 1;
				unsigned int vp2_line_flag_and_en: 1;
				unsigned int reserve_0: 1;
				unsigned int vp0_dsp_hold_and_en: 1;
				unsigned int vp1_dsp_hold_and_en: 1;
				unsigned int vp2_dsp_hold_and_en: 1;
				unsigned int reserve_1: 1;
				unsigned int vp0_almost_full_and_en: 1;
				unsigned int vp1_almost_full_and_en: 1;
				unsigned int vp2_almost_full_and_en: 1;
				unsigned int reserve_2: 3;
				unsigned int axi_dma_finish_or_en: 1;
				unsigned int wb_dma_finish_or_en: 1;
				unsigned int vp0_line_flag_or_en: 1;
				unsigned int vp1_line_flag_or_en: 1;
				unsigned int vp2_line_flag_or_en: 1;
				unsigned int reserve_3: 1;
				unsigned int vp0_dsp_hold_or_en: 1;
				unsigned int vp1_dsp_hold_or_en: 1;
				unsigned int vp2_dsp_hold_or_en: 1;
				unsigned int reserve_4: 1;
				unsigned int vp0_almost_full_or_en: 1;
				unsigned int vp1_almost_full_or_en: 1;
				unsigned int vp2_almost_full_or_en: 1;
				unsigned int reserve_5: 1;
			} bits;
			unsigned int u32;
		} sw_sys_var_ferq_ctrl_imd;
		union metadata_ctrl_u { 
			struct metadata_ctrl_s { 
				unsigned int metadata_lut_en: 1;
				unsigned int metadata_rd_err_clr: 1;
				unsigned int metadata_is_writing: 1;
				unsigned int metadata_rd_err_t: 1;
				unsigned int metadata_rid: 4;
				unsigned int metadata_mem_mst: 7;
				unsigned int reserve_0: 1;
				unsigned int metadata_size: 11;
				unsigned int reserve_1: 3;
				unsigned int metadata_port_sel: 2;
			} bits;
			unsigned int u32;
		} sw_metadata_ctrl;
		union metadata_mst_u { 
			struct metadata_mst_s { 
				unsigned int metadata_mst: 32;
			} bits;
			unsigned int u32;
		} sw_metadata_mst;
		union fbcd_timeout_ctrl_u { 
			struct fbcd_timeout_ctrl_s { 
				unsigned int fbcd_timeout_cnt: 31;
				unsigned int fbcd_timeout_en: 1;
			} bits;
			unsigned int u32;
		} sw_fbcd_timeout_ctrl;
		union vop_io_vsync_ctrl_u { 
			struct vop_io_vsync_ctrl_s { 
				unsigned int vop_io_vp0_vsync_sel: 2;
				unsigned int vop_io_vp1_vsync_sel: 2;
				unsigned int vop_io_vp2_vsync_sel: 2;
				unsigned int reserve_0: 26;
			} bits;
			unsigned int u32;
		} sw_vop_io_vsync_ctrl;
		struct { 
			unsigned int reserve_data[12];
		} reserve_reg_80_88;
		union sys_lut_port_sel_u { 
			struct sys_lut_port_sel_s { 
				unsigned int reserve_0: 10;
				unsigned int sharp_ahb_port_sel: 2;
				unsigned int gamma_ahb_write_sel: 2;
				unsigned int acm_ahb_port_sel: 2;
				unsigned int write_mask: 16;
			} bits;
			unsigned int u32;
		} sw_sys_lut_port_sel;
		union sys_status0_u { 
			struct sys_status0_s { 
				unsigned int dma_stop_valid0: 1;
				unsigned int mmu_idle: 1;
				unsigned int reserve_0: 14;
				unsigned int dsp_vcnt0: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_sys_status0;
		union sys_status1_u { 
			struct sys_status1_s { 
				unsigned int dma_stop_valid1: 1;
				unsigned int mmu_idle: 1;
				unsigned int reserve_0: 14;
				unsigned int dsp_vcnt1: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_sys_status1;
		union sys_status2_u { 
			struct sys_status2_s { 
				unsigned int reserve_0: 16;
				unsigned int dsp_vcnt2: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_sys_status2;
		struct { 
			unsigned int reserve_data[8];
		} reserve_reg_108_112;
		union sys_line_flag0_u { 
			struct sys_line_flag0_s { 
				unsigned int dsp_line_flag_num_0: 13;
				unsigned int reserve_0: 2;
				unsigned int dsp_line_flag0_sel: 1;
				unsigned int dsp_line_flag_num_1: 13;
				unsigned int dsp_almost_full_thold: 3;
			} bits;
			unsigned int u32;
		} sw_sys_line_flag0;
		union sys_line_flag1_u { 
			struct sys_line_flag1_s { 
				unsigned int dsp_line_flag_num_0: 13;
				unsigned int reserve_0: 2;
				unsigned int dsp_line_flag1_sel: 1;
				unsigned int dsp_line_flag_num_1: 13;
				unsigned int dsp_almost_full_thold: 3;
			} bits;
			unsigned int u32;
		} sw_sys_line_flag1;
		union sys_line_flag2_u { 
			struct sys_line_flag2_s { 
				unsigned int dsp_line_flag_num_0: 13;
				unsigned int reserve_0: 2;
				unsigned int dsp_line_flag2_sel: 1;
				unsigned int dsp_line_flag_num_1: 13;
				unsigned int dsp_almost_full_thold: 3;
			} bits;
			unsigned int u32;
		} sw_sys_line_flag2;
		union sys0_intr_en_u { 
			struct sys0_intr_en_s { 
				unsigned int reserve_0: 1;
				unsigned int intr_en_bus0_error: 1;
				unsigned int intr_en_dma0_finish: 1;
				unsigned int int_en_wb_uv_fifo_full: 1;
				unsigned int int_en_wb_yrgb_fifo_full: 1;
				unsigned int int_en_wb_finish: 1;
				unsigned int reserve_1: 1;
				unsigned int intr_en_mmu: 1;
				unsigned int intr_en_wb_resp_err: 1;
				unsigned int intr_en_wb_time_out: 1;
				unsigned int reserve_2: 6;
				unsigned int write_mask: 16;
			} bits;
			unsigned int u32;
		} sw_sys0_intr_en;
		union sys0_intr_clr_u { 
			struct sys0_intr_clr_s { 
				unsigned int reserve_0: 1;
				unsigned int intr_clr_bus_error: 1;
				unsigned int intr_clr_dma_finish: 1;
				unsigned int intr_clr_wb_uv_fifo_full: 1;
				unsigned int intr_clr_wb_yrgb_fifo_full: 1;
				unsigned int intr_clr_wb_dma_finish: 1;
				unsigned int reserve_1: 1;
				unsigned int intr_clr_mmu: 1;
				unsigned int intr_clr_wb_resp_err: 1;
				unsigned int intr_clr_wb_time_out: 1;
				unsigned int reserve_2: 6;
				unsigned int write_mask: 16;
			} bits;
			unsigned int u32;
		} sw_sys0_intr_clr;
		union sys0_intr_status_u { 
			struct sys0_intr_status_s { 
				unsigned int reserve_0: 1;
				unsigned int intr_status_bus_error: 1;
				unsigned int intr_status_dma_finish: 1;
				unsigned int intr_status_wb_uv_fifo_full: 1;
				unsigned int intr_status_wb_yrgb_fifo_full: 1;
				unsigned int intr_status_wb_dma_finish: 1;
				unsigned int reserve_1: 1;
				unsigned int intr_status_mmu: 1;
				unsigned int intr_status_wb_resp_err: 1;
				unsigned int intr_status_wb_time_out: 1;
				unsigned int reserve_2: 22;
			} bits;
			unsigned int u32;
		} sw_sys0_intr_status;
		union sys0_intr_raw_status_u { 
			struct sys0_intr_raw_status_s { 
				unsigned int reserve_0: 1;
				unsigned int intr_raw_status_bus_error: 1;
				unsigned int intr_raw_status_dma_finish: 1;
				unsigned int intr_raw_status_wb_uv_fifo_full: 1;
				unsigned int intr_raw_status_wb_yrgb_fifo_full: 1;
				unsigned int intr_raw_status_wb_dma_finish: 1;
				unsigned int reserve_1: 1;
				unsigned int intr_raw_status_mmu0: 1;
				unsigned int intr_status_wb_resp_err: 1;
				unsigned int intr_status_wb_time_out: 1;
				unsigned int reserve_2: 22;
			} bits;
			unsigned int u32;
		} sw_sys0_intr_raw_status;
		union sys1_intr_en_u { 
			struct sys1_intr_en_s { 
				unsigned int reserve_0: 1;
				unsigned int intr_en_bus1_error: 1;
				unsigned int intr_en_dma1_finish: 1;
				unsigned int reserve_1: 4;
				unsigned int intr_en_mmu1: 1;
				unsigned int reserve_2: 8;
				unsigned int write_mask: 16;
			} bits;
			unsigned int u32;
		} sw_sys1_intr_en;
		union sys1_intr_clr_sys_u { 
			struct sys1_intr_clr_sys_s { 
				unsigned int reserve_0: 1;
				unsigned int intr_clr_bus_error: 1;
				unsigned int intr_clr_dma_finish: 1;
				unsigned int reserve_1: 4;
				unsigned int intr_clr_mmu1: 1;
				unsigned int reserve_2: 8;
				unsigned int write_mask: 16;
			} bits;
			unsigned int u32;
		} sw_sys1_intr_clr_sys;
		union sys1_intr_status_u { 
			struct sys1_intr_status_s { 
				unsigned int reserve_0: 1;
				unsigned int intr_status_bus_error: 1;
				unsigned int intr_status_dma_finish: 1;
				unsigned int reserve_1: 4;
				unsigned int intr_status_mmu1: 1;
				unsigned int reserve_2: 24;
			} bits;
			unsigned int u32;
		} sw_sys1_intr_status;
		union sys1_intr_raw_status_u { 
			struct sys1_intr_raw_status_s { 
				unsigned int reserve_0: 1;
				unsigned int intr_raw_status_bus_error: 1;
				unsigned int intr_raw_status_dma_finish: 1;
				unsigned int reserve_1: 4;
				unsigned int intr_raw_status_mmu1: 1;
				unsigned int reserve_2: 24;
			} bits;
			unsigned int u32;
		} sw_sys1_intr_raw_status;
		union port0_intr_en_u { 
			struct port0_intr_en_s { 
				unsigned int intr_en_fs: 1;
				unsigned int reserve_0: 1;
				unsigned int intr_en_line_flag0: 1;
				unsigned int intr_en_line_flag1: 1;
				unsigned int intr_en_post_buf_empty: 1;
				unsigned int intr_en_fs_field: 1;
				unsigned int intr_en_dsp_hold_valid: 1;
				unsigned int intr_en_vfp: 1;
				unsigned int reserve_1: 1;
				unsigned int intr_en_post_full: 1;
				unsigned int reserve_2: 2;
				unsigned int intr_en_dolby_core1: 1;
				unsigned int intr_en_dolby_core2: 1;
				unsigned int intr_en_dolby_core3: 1;
				unsigned int reserve_3: 1;
				unsigned int write_mask: 16;
			} bits;
			unsigned int u32;
		} sw_port0_intr_en;
		union port0_intr_clr_u { 
			struct port0_intr_clr_s { 
				unsigned int intr_clr_fs: 1;
				unsigned int intr_clr_fs_new: 1;
				unsigned int intr_clr_line_flag0: 1;
				unsigned int intr_clr_line_flag1: 1;
				unsigned int intr_clr_post_buf_empty: 1;
				unsigned int intr_clr_fs_field: 1;
				unsigned int intr_clr_dsp_hold_valid: 1;
				unsigned int intr_clr_vfp: 1;
				unsigned int reserve_0: 1;
				unsigned int intr_clr_post_full: 1;
				unsigned int reserve_1: 6;
				unsigned int write_mask: 16;
			} bits;
			unsigned int u32;
		} sw_port0_intr_clr;
		union port0_intr_status_u { 
			struct port0_intr_status_s { 
				unsigned int intr_status_fs: 1;
				unsigned int reserve_0: 1;
				unsigned int intr_status_line_flag0: 1;
				unsigned int intr_status_line_flag1: 1;
				unsigned int intr_status_post_buf_empty: 1;
				unsigned int intr_status_fs_field: 1;
				unsigned int intr_status_dsp_hold_valid: 1;
				unsigned int intr_status_vfp: 1;
				unsigned int reserve_1: 1;
				unsigned int intr_status_post_full: 1;
				unsigned int reserve_2: 22;
			} bits;
			unsigned int u32;
		} sw_port0_intr_status;
		union port0_intr_raw_status_u { 
			struct port0_intr_raw_status_s { 
				unsigned int intr_raw_status_fs: 1;
				unsigned int reserve_0: 1;
				unsigned int intr_raw_status_line_flag0: 1;
				unsigned int intr_raw_status_line_flag1: 1;
				unsigned int intr_raw_status_post_buf_empty: 1;
				unsigned int intr_raw_status_fs_field: 1;
				unsigned int intr_raw_status_dsp_hold_valid: 1;
				unsigned int intr_raw_status_vfp: 1;
				unsigned int reserve_1: 1;
				unsigned int intr_raw_status_post_full: 1;
				unsigned int reserve_2: 22;
			} bits;
			unsigned int u32;
		} sw_port0_intr_raw_status;
		union port1_intr_en_u { 
			struct port1_intr_en_s { 
				unsigned int intr_en_fs: 1;
				unsigned int reserve_0: 1;
				unsigned int intr_en_line_flag0: 1;
				unsigned int intr_en_line_flag1: 1;
				unsigned int intr_en_post_buf_empty: 1;
				unsigned int intr_en_fs_field: 1;
				unsigned int intr_en_dsp_hold_valid: 1;
				unsigned int intr_en_vfp: 1;
				unsigned int reserve_1: 1;
				unsigned int intr_en_post_full: 1;
				unsigned int reserve_2: 6;
				unsigned int write_mask: 16;
			} bits;
			unsigned int u32;
		} sw_port1_intr_en;
		union port1_intr_clr_u { 
			struct port1_intr_clr_s { 
				unsigned int intr_clr_fs: 1;
				unsigned int reserve_0: 1;
				unsigned int intr_clr_line_flag0: 1;
				unsigned int intr_clr_line_flag1: 1;
				unsigned int intr_clr_post_buf_empty: 1;
				unsigned int intr_clr_fs_field: 1;
				unsigned int intr_clr_dsp_hold_valid: 1;
				unsigned int intr_clr_vfp: 1;
				unsigned int reserve_1: 1;
				unsigned int intr_clr_post_full: 1;
				unsigned int reserve_2: 6;
				unsigned int write_mask: 16;
			} bits;
			unsigned int u32;
		} sw_port1_intr_clr;
		union port1_intr_status_u { 
			struct port1_intr_status_s { 
				unsigned int intr_status_fs: 1;
				unsigned int reserve_0: 1;
				unsigned int intr_status_line_flag0: 1;
				unsigned int intr_status_line_flag1: 1;
				unsigned int intr_status_post_buf_empty: 1;
				unsigned int intr_status_fs_field: 1;
				unsigned int intr_status_dsp_hold_valid: 1;
				unsigned int intr_status_vfp: 1;
				unsigned int reserve_1: 1;
				unsigned int intr_status_post_full: 1;
				unsigned int reserve_2: 22;
			} bits;
			unsigned int u32;
		} sw_port1_intr_status;
		union port1_intr_raw_status_u { 
			struct port1_intr_raw_status_s { 
				unsigned int intr_raw_status_fs: 1;
				unsigned int reserve_0: 1;
				unsigned int intr_raw_status_line_flag0: 1;
				unsigned int intr_raw_status_line_flag1: 1;
				unsigned int intr_raw_status_post_buf_empty: 1;
				unsigned int intr_raw_status_fs_field: 1;
				unsigned int intr_raw_status_dsp_hold_valid: 1;
				unsigned int intr_raw_status_vfp: 1;
				unsigned int reserve_1: 1;
				unsigned int intr_raw_status_post_full: 1;
				unsigned int reserve_2: 22;
			} bits;
			unsigned int u32;
		} sw_port1_intr_raw_status;
		union port2_intr_en_u { 
			struct port2_intr_en_s { 
				unsigned int intr_en_fs: 1;
				unsigned int reserve_0: 1;
				unsigned int intr_en_line_flag0: 1;
				unsigned int intr_en_line_flag1: 1;
				unsigned int intr_en_post_buf_empty: 1;
				unsigned int intr_en_fs_field: 1;
				unsigned int intr_en_dsp_hold_valid: 1;
				unsigned int intr_en_vfp: 1;
				unsigned int reserve_1: 1;
				unsigned int intr_en_post_full: 1;
				unsigned int reserve_2: 6;
				unsigned int write_mask: 16;
			} bits;
			unsigned int u32;
		} sw_port2_intr_en;
		union port2_intr_clr_u { 
			struct port2_intr_clr_s { 
				unsigned int intr_clr_fs: 1;
				unsigned int reserve_0: 1;
				unsigned int intr_clr_line_flag0: 1;
				unsigned int intr_clr_line_flag1: 1;
				unsigned int intr_clr_post_buf_empty: 1;
				unsigned int intr_clr_fs_field: 1;
				unsigned int intr_clr_dsp_hold_valid: 1;
				unsigned int intr_clr_vfp: 1;
				unsigned int reserve_1: 1;
				unsigned int intr_clr_post_full: 1;
				unsigned int reserve_2: 6;
				unsigned int write_mask: 16;
			} bits;
			unsigned int u32;
		} sw_port2_intr_clr;
		union port2_intr_status_u { 
			struct port2_intr_status_s { 
				unsigned int intr_status_fs: 1;
				unsigned int reserve_0: 1;
				unsigned int intr_status_line_flag0: 1;
				unsigned int intr_status_line_flag1: 1;
				unsigned int intr_status_post_buf_empty: 1;
				unsigned int intr_status_fs_field: 1;
				unsigned int intr_status_dsp_hold_valid: 1;
				unsigned int intr_status_vfp: 1;
				unsigned int reserve_1: 1;
				unsigned int intr_status_post_full: 1;
				unsigned int reserve_2: 22;
			} bits;
			unsigned int u32;
		} sw_port2_intr_status;
		union port2_intr_raw_status_u { 
			struct port2_intr_raw_status_s { 
				unsigned int intr_raw_status_fs: 1;
				unsigned int reserve_0: 1;
				unsigned int intr_raw_status_line_flag0: 1;
				unsigned int intr_raw_status_line_flag1: 1;
				unsigned int intr_raw_status_post_buf_empty: 1;
				unsigned int intr_raw_status_fs_field: 1;
				unsigned int intr_raw_status_dsp_hold_valid: 1;
				unsigned int intr_raw_status_vfp: 1;
				unsigned int reserve_1: 1;
				unsigned int intr_raw_status_post_full: 1;
				unsigned int reserve_2: 22;
			} bits;
			unsigned int u32;
		} sw_port2_intr_raw_status;
		struct { 
			unsigned int reserve_data[20];
		} reserve_reg_208_224;
		union fbcd_intr_en0_u { 
			struct fbcd_intr_en0_s { 
				unsigned int intr_en_axi0_pld_raddr_err: 1;
				unsigned int intr_en_axi0_pld_overflow_err: 1;
				unsigned int intr_en_axi0_pld_dec_err: 1;
				unsigned int intr_en_axi0_buff_ctrl_err: 1;
				unsigned int intr_en_axi0_hdr0_ctrl_err: 1;
				unsigned int intr_en_axi0_hdr1_ctrl_err: 1;
				unsigned int intr_en_axi0_hdr2_ctrl_err: 1;
				unsigned int intr_en_axi0_hdr3_ctrl_err: 1;
				unsigned int reserve_0: 24;
			} bits;
			unsigned int u32;
		} sw_fbcd_intr_en0;
		union fbcd_intr_clr0_u { 
			struct fbcd_intr_clr0_s { 
				unsigned int intr_clr_axi0_pld_raddr_err: 1;
				unsigned int intr_clr_axi0_pld_overflow_err: 1;
				unsigned int intr_clr_axi0_pld_dec_err: 1;
				unsigned int intr_clr_axi0_buff_ctrl_err: 1;
				unsigned int intr_clr_axi0_hdr0_ctrl_err: 1;
				unsigned int intr_clr_axi0_hdr1_ctrl_err: 1;
				unsigned int intr_clr_axi0_hdr2_ctrl_err: 1;
				unsigned int intr_clr_axi0_hdr3_ctrl_err: 1;
				unsigned int reserve_0: 24;
			} bits;
			unsigned int u32;
		} sw_fbcd_intr_clr0;
		union fbcd_intr_status0_u { 
			struct fbcd_intr_status0_s { 
				unsigned int intr_status_axi0_pld_raddr_err: 1;
				unsigned int intr_status_axi0_pld_overflow_err: 1;
				unsigned int intr_status_axi0_pld_dec_err: 1;
				unsigned int intr_status_axi0_buff_ctrl_err: 1;
				unsigned int intr_status_axi0_hdr0_ctrl_err: 1;
				unsigned int intr_status_axi0_hdr1_ctrl_err: 1;
				unsigned int intr_status_axi0_hdr2_ctrl_err: 1;
				unsigned int intr_status_axi0_hdr3_ctrl_err: 1;
				unsigned int reserve_0: 24;
			} bits;
			unsigned int u32;
		} sw_fbcd_intr_status0;
		union fbcd_intr_raw_status0_u { 
			struct fbcd_intr_raw_status0_s { 
				unsigned int intr_raw_status_axi0_pld_raddr_err: 1;
				unsigned int intr_raw_status_axi0_pld_overflow_err: 1;
				unsigned int intr_raw_status_axi0_pld_dec_err: 1;
				unsigned int intr_raw_status_axi0_buff_ctrl_err: 1;
				unsigned int intr_raw_status_axi0_hdr0_ctrl_err: 1;
				unsigned int intr_raw_status_axi0_hdr1_ctrl_err: 1;
				unsigned int intr_raw_status_axi0_hdr2_ctrl_err: 1;
				unsigned int intr_raw_status_axi0_hdr3_ctrl_err: 1;
				unsigned int reserve_0: 24;
			} bits;
			unsigned int u32;
		} sw_fbcd_intr_raw_status0;
		struct { 
			unsigned int reserve_data[16];
		} reserve_reg_244_256;
		union sys_wb_ctrl0_u { 
			struct sys_wb_ctrl0_s { 
				unsigned int wb_en: 1;
				unsigned int wb_fmt: 3;
				unsigned int wb_dither_en: 1;
				unsigned int wb_rgb2yuv_en: 1;
				unsigned int wb_rgb2yuv_mode: 1;
				unsigned int wb_xpsd_bil_en: 1;
				unsigned int wb_ythrow_en: 1;
				unsigned int wb_ythrow_mode: 1;
				unsigned int reserve_0: 1;
				unsigned int wb_post_empty_stop_en: 1;
				unsigned int wb_oneframe_mode: 1;
				unsigned int reserve_1: 1;
				unsigned int wb_rb_swap_en: 1;
				unsigned int wb_rg_swap_en: 1;
				unsigned int reserve_2: 2;
				unsigned int wb_xgt2_en: 1;
				unsigned int reserve_3: 1;
				unsigned int wb_yrgb_id: 4;
				unsigned int wb_uv_id: 4;
				unsigned int reserve_4: 2;
				unsigned int wb_port_sel_imd: 2;
			} bits;
			unsigned int u32;
		} sw_sys_wb_ctrl0;
		union sys_wb_xspd_factor_u { 
			struct sys_wb_xspd_factor_s { 
				unsigned int fifo_thold: 10;
				unsigned int reserve_0: 6;
				unsigned int wb_xpsd_bil_factor: 14;
				unsigned int reserve_1: 2;
			} bits;
			unsigned int u32;
		} sw_sys_wb_xspd_factor;
		union sys_wb_yrgb_mst_u { 
			struct sys_wb_yrgb_mst_s { 
				unsigned int wb_yrgb_mst: 32;
			} bits;
			unsigned int u32;
		} sw_sys_wb_yrgb_mst;
		union sys_wb_cbr_mst_u { 
			struct sys_wb_cbr_mst_s { 
				unsigned int wb_cbr_mst: 32;
			} bits;
			unsigned int u32;
		} sw_sys_wb_cbr_mst;
		union sys_wb_vir_stride_u { 
			struct sys_wb_vir_stride_s { 
				unsigned int wb_vir_stride: 13;
				unsigned int reserve_0: 2;
				unsigned int wb_vir_stride_en: 1;
				unsigned int wb_dsp_width: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_sys_wb_vir_stride;
		union sys_wb_timeout_ctrl_u { 
			struct sys_wb_timeout_ctrl_s { 
				unsigned int wb_timeout_cnt: 31;
				unsigned int reserve_0: 1;
			} bits;
			unsigned int u32;
		} sw_sys_wb_timeout_ctrl;
		struct { 
			unsigned int reserve_data[104];
		} reserve_reg_284_384;
		union mipi0_inface_ctrl_u { 
			struct mipi0_inface_ctrl_s { 
				unsigned int mipi_out_en: 1;
				unsigned int mipi_clk_out_en: 1;
				unsigned int mipi_port_sel: 2;
				unsigned int mipi_hsync_pol: 1;
				unsigned int mipi_vsync_pol: 1;
				unsigned int reserve_0: 2;
				unsigned int mipi_split_en: 1;
				unsigned int mipi_data1_sel: 1;
				unsigned int reserve_1: 1;
				unsigned int mipi_cmd_mode: 1;
				unsigned int reserve_2: 8;
				unsigned int mipi_pix_clk_sel: 1;
				unsigned int mipi_dclk_sel: 1;
				unsigned int reserve_3: 9;
				unsigned int regdone_imd_en: 1;
			} bits;
			unsigned int u32;
		} sw_mipi0_inface_ctrl;
		union hdmi0_inface_ctrl_u { 
			struct hdmi0_inface_ctrl_s { 
				unsigned int hdmi_out_en: 1;
				unsigned int hdmi_clk_out_en: 1;
				unsigned int hdmi_port_sel: 2;
				unsigned int hdmi_hsync_pol: 1;
				unsigned int hdmi_vsync_pol: 1;
				unsigned int reserve_0: 2;
				unsigned int hdmi_split_en: 1;
				unsigned int hdmi_data1_sel: 1;
				unsigned int reserve_1: 2;
				unsigned int hdmi_r2y_en: 1;
				unsigned int reserve_2: 1;
				unsigned int hdmi_r2y_mode: 2;
				unsigned int hdmi_yc_swap: 1;
				unsigned int hdmi_uv_swap: 1;
				unsigned int reserve_3: 2;
				unsigned int hdmi_pix_clk_sel: 1;
				unsigned int hdmi_dclk_sel: 1;
				unsigned int reserve_4: 9;
				unsigned int regdone_imd_en: 1;
			} bits;
			unsigned int u32;
		} sw_hdmi0_inface_ctrl;
		union edp0_inface_ctrl_u { 
			struct edp0_inface_ctrl_s { 
				unsigned int edp_out_en: 1;
				unsigned int edp_clk_out_en: 1;
				unsigned int edp_port_sel: 2;
				unsigned int edp_hsync_pol: 1;
				unsigned int edp_vsync_pol: 1;
				unsigned int reserve_0: 2;
				unsigned int edp_split_en: 1;
				unsigned int edp_data1_sel: 1;
				unsigned int reserve_1: 10;
				unsigned int edp_pix_clk_sel: 1;
				unsigned int edp_dclk_sel: 1;
				unsigned int reserve_2: 9;
				unsigned int regdone_imd_en: 1;
			} bits;
			unsigned int u32;
		} sw_edp0_inface_ctrl;
		union dp0_inface_ctrl_u { 
			struct dp0_inface_ctrl_s { 
				unsigned int dp_out_en: 1;
				unsigned int dp_clk_out_en: 1;
				unsigned int dp_port_sel: 2;
				unsigned int dp_hsync_pol: 1;
				unsigned int dp_vsync_pol: 1;
				unsigned int reserve_0: 2;
				unsigned int dp_split_en: 1;
				unsigned int dp_data1_sel: 1;
				unsigned int reserve_1: 10;
				unsigned int dp_pix_clk_sel: 1;
				unsigned int dp_dclk_sel: 1;
				unsigned int reserve_2: 9;
				unsigned int regdone_imd_en: 1;
			} bits;
			unsigned int u32;
		} sw_dp0_inface_ctrl;
		union rgb_inface_ctrl_u { 
			struct rgb_inface_ctrl_s { 
				unsigned int rgb_out_en: 1;
				unsigned int rgb_clk_out_en: 1;
				unsigned int rgb_port_sel: 2;
				unsigned int rgb_hsync_pol: 1;
				unsigned int rgb_vsync_pol: 1;
				unsigned int rgb_den_pol: 1;
				unsigned int fpga_dclk_inv: 1;
				unsigned int rgb_split_en: 1;
				unsigned int rgb_data1_sel: 1;
				unsigned int reserve_0: 2;
				unsigned int bt656_out_en: 1;
				unsigned int bt656_uv_swap: 1;
				unsigned int bt656_yc_swap: 1;
				unsigned int reserve_1: 1;
				unsigned int bt1120_out_en: 1;
				unsigned int bt1120_uv_swap: 1;
				unsigned int bt1120_yc_swap: 1;
				unsigned int reserve_2: 2;
				unsigned int rgb_dclk_sel: 1;
				unsigned int reserve_3: 9;
				unsigned int regdone_imd_en: 1;
			} bits;
			unsigned int u32;
		} sw_rgb_inface_ctrl;
		struct { 
			unsigned int reserve_data[16];
		} reserve_reg_408_420;
		union dp1_inface_ctrl_u { 
			struct dp1_inface_ctrl_s { 
				unsigned int dp_out_en: 1;
				unsigned int dp_clk_out_en: 1;
				unsigned int dp_port_sel: 2;
				unsigned int dp_hsync_pol: 1;
				unsigned int dp_vsync_pol: 1;
				unsigned int reserve_0: 2;
				unsigned int dp_split_en: 1;
				unsigned int dp_data1_sel: 1;
				unsigned int reserve_1: 10;
				unsigned int dp_pix_clk_sel: 1;
				unsigned int dp_dclk_sel: 1;
				unsigned int reserve_2: 9;
				unsigned int regdone_imd_en: 1;
			} bits;
			unsigned int u32;
		} sw_dp1_inface_ctrl;
		struct { 
			unsigned int reserve_data[8];
		} reserve_reg_428_432;
		union dp2_inface_ctrl_u { 
			struct dp2_inface_ctrl_s { 
				unsigned int dp_out_en: 1;
				unsigned int dp_clk_out_en: 1;
				unsigned int dp_port_sel: 2;
				unsigned int dp_hsync_pol: 1;
				unsigned int dp_vsync_pol: 1;
				unsigned int reserve_0: 2;
				unsigned int dp_split_en: 1;
				unsigned int dp_data1_sel: 1;
				unsigned int reserve_1: 10;
				unsigned int dp_pix_clk_sel: 1;
				unsigned int dp_dclk_sel: 1;
				unsigned int reserve_2: 9;
				unsigned int regdone_imd_en: 1;
			} bits;
			unsigned int u32;
		} sw_dp2_inface_ctrl;
		struct { 
			unsigned int reserve_data[44];
		} reserve_reg_440_480;
		union sec_drm_ctrl_u { 
			struct sec_drm_ctrl_s { 
				unsigned int sec_drm_en: 1;
				unsigned int reserve_0: 3;
				unsigned int sec_wb_dis: 1;
				unsigned int sec_rid_lock_en: 1;
				unsigned int reserve_1: 2;
				unsigned int sec_cluster0_en: 1;
				unsigned int sec_cluster1_en: 1;
				unsigned int reserve_2: 2;
				unsigned int sec_esmart0_en: 1;
				unsigned int sec_esmart1_en: 1;
				unsigned int sec_esmart2_en: 1;
				unsigned int sec_esmart3_en: 1;
				unsigned int sec_axi0_rid0_prot_en: 1;
				unsigned int sec_axi0_rid1_prot_en: 1;
				unsigned int sec_axi0_rid2_prot_en: 1;
				unsigned int sec_axi0_rid3_prot_en: 1;
				unsigned int sec_axi1_rid0_prot_en: 1;
				unsigned int sec_axi1_rid1_prot_en: 1;
				unsigned int sec_axi1_rid2_prot_en: 1;
				unsigned int sec_axi1_rid3_prot_en: 1;
				unsigned int reserve_3: 8;
			} bits;
			unsigned int u32;
		} sw_sec_drm_ctrl;
		union sec_drm_port_sel_u { 
			struct sec_drm_port_sel_s { 
				unsigned int drm_cluster0_port_sel: 2;
				unsigned int reserve_0: 2;
				unsigned int drm_cluster1_port_sel: 2;
				unsigned int reserve_1: 10;
				unsigned int drm_esmart0_port_sel: 2;
				unsigned int reserve_2: 2;
				unsigned int drm_esmart1_port_sel: 2;
				unsigned int reserve_3: 2;
				unsigned int drm_esmart2_port_sel: 2;
				unsigned int reserve_4: 2;
				unsigned int drm_esmart3_port_sel: 2;
				unsigned int reserve_5: 2;
			} bits;
			unsigned int u32;
		} sw_sec_drm_port_sel;
		union sec_port0_layer_sel_u { 
			struct sec_port0_layer_sel_s { 
				unsigned int drm_layer0_sel: 3;
				unsigned int drm_layer0_sel_en: 1;
				unsigned int drm_layer1_sel: 3;
				unsigned int drm_layer1_sel_en: 1;
				unsigned int drm_layer2_sel: 3;
				unsigned int drm_layer2_sel_en: 1;
				unsigned int drm_layer3_sel: 3;
				unsigned int drm_layer3_sel_en: 1;
				unsigned int reserve_0: 16;
			} bits;
			unsigned int u32;
		} sw_sec_port0_layer_sel;
		union sec_port1_layer_sel_u { 
			struct sec_port1_layer_sel_s { 
				unsigned int drm_layer0_sel: 3;
				unsigned int drm_layer0_sel_en: 1;
				unsigned int drm_layer1_sel: 3;
				unsigned int drm_layer1_sel_en: 1;
				unsigned int drm_layer2_sel: 3;
				unsigned int drm_layer2_sel_en: 1;
				unsigned int drm_layer3_sel: 3;
				unsigned int drm_layer3_sel_en: 1;
				unsigned int reserve_0: 16;
			} bits;
			unsigned int u32;
		} sw_sec_port1_layer_sel;
		union sec_port2_layer_sel_u { 
			struct sec_port2_layer_sel_s { 
				unsigned int drm_layer0_sel: 3;
				unsigned int drm_layer0_sel_en: 1;
				unsigned int drm_layer1_sel: 3;
				unsigned int drm_layer1_sel_en: 1;
				unsigned int drm_layer2_sel: 3;
				unsigned int drm_layer2_sel_en: 1;
				unsigned int drm_layer3_sel: 3;
				unsigned int drm_layer3_sel_en: 1;
				unsigned int reserve_0: 16;
			} bits;
			unsigned int u32;
		} sw_sec_port2_layer_sel;
		union sec_axi_rid_prot_u { 
			struct sec_axi_rid_prot_s { 
				unsigned int sec_axi0_rid0_prot: 4;
				unsigned int sec_axi0_rid1_prot: 4;
				unsigned int sec_axi0_rid2_prot: 4;
				unsigned int sec_axi0_rid3_prot: 4;
				unsigned int sec_axi1_rid0_prot: 4;
				unsigned int sec_axi1_rid1_prot: 4;
				unsigned int sec_axi1_rid2_prot: 4;
				unsigned int sec_axi1_rid3_prot: 4;
			} bits;
			unsigned int u32;
		} sw_sec_axi_rid_prot;
		union sys_otp_mirr_ctrl_imd_u { 
			struct sys_otp_mirr_ctrl_imd_s { 
				unsigned int dis_otp_fuction: 1;
				unsigned int reserve_0: 31;
			} bits;
			unsigned int u32;
		} sw_sys_otp_mirr_ctrl_imd;
	} regs;
	unsigned int p_reg_addr[69];
}sys_ctrl_0x27d00000_t;

typedef union overlay_system_0x27d00500_u {
	struct overlay_system_0x27d00500_s {
		union extra_alpha_ctrl_imd_u { 
			struct extra_alpha_ctrl_imd_s { 
				unsigned int port0_extra_alpha_en: 1;
				unsigned int reserve_0: 31;
			} bits;
			unsigned int u32;
		} sw_extra_alpha_ctrl_imd;
		struct { 
			unsigned int reserve_data[48];
		} reserve_reg_4_48;
		union cluster0_src_color_ctrl_u { 
			struct cluster0_src_color_ctrl_s { 
				unsigned int src_color_mode0: 1;
				unsigned int src_alpha_mode0: 1;
				unsigned int src_blend_mode0: 2;
				unsigned int src_alpha_cal_mode0: 1;
				unsigned int src_factor_mode0: 3;
				unsigned int alpha_en: 1;
				unsigned int src_dst_swap: 1;
				unsigned int reserve_0: 6;
				unsigned int src_global_alpha0: 8;
				unsigned int reserve_1: 8;
			} bits;
			unsigned int u32;
		} sw_cluster0_src_color_ctrl;
		union cluster0_dst_color_ctrl_u { 
			struct cluster0_dst_color_ctrl_s { 
				unsigned int dst_color_mode0: 1;
				unsigned int dst_alpha_mode0: 1;
				unsigned int dst_blend_mode0: 2;
				unsigned int dst_alpha_cal_mode0: 1;
				unsigned int dst_factor_mode0: 3;
				unsigned int reserve_0: 8;
				unsigned int dst_global_alpha0: 8;
				unsigned int reserve_1: 8;
			} bits;
			unsigned int u32;
		} sw_cluster0_dst_color_ctrl;
		union cluster0_src_alpha_ctrl_u { 
			struct cluster0_src_alpha_ctrl_s { 
				unsigned int reserve_0: 1;
				unsigned int src_alpha_mode1: 1;
				unsigned int src_blend_mode1: 2;
				unsigned int src_alpha_cal_mode1: 1;
				unsigned int src_factor_mode1: 3;
				unsigned int reserve_1: 24;
			} bits;
			unsigned int u32;
		} sw_cluster0_src_alpha_ctrl;
		union cluster0_dst_alpha_ctrl_u { 
			struct cluster0_dst_alpha_ctrl_s { 
				unsigned int reserve_0: 1;
				unsigned int dst_alpha_mode1: 1;
				unsigned int dst_blend_mode1: 2;
				unsigned int dst_alpha_cal_mode1: 1;
				unsigned int dst_factor_mode1: 3;
				unsigned int reserve_1: 24;
			} bits;
			unsigned int u32;
		} sw_cluster0_dst_alpha_ctrl;
		union cluster1_src_color_ctrl_u { 
			struct cluster1_src_color_ctrl_s { 
				unsigned int src_color_mode0: 1;
				unsigned int src_alpha_mode0: 1;
				unsigned int src_blend_mode0: 2;
				unsigned int src_alpha_cal_mode0: 1;
				unsigned int src_factor_mode0: 3;
				unsigned int alpha_en: 1;
				unsigned int src_dst_swap: 1;
				unsigned int reserve_0: 6;
				unsigned int src_global_alpha0: 8;
				unsigned int reserve_1: 8;
			} bits;
			unsigned int u32;
		} sw_cluster1_src_color_ctrl;
		union cluster1_dst_color_ctrl_u { 
			struct cluster1_dst_color_ctrl_s { 
				unsigned int dst_color_mode0: 1;
				unsigned int dst_alpha_mode0: 1;
				unsigned int dst_blend_mode0: 2;
				unsigned int dst_alpha_cal_mode0: 1;
				unsigned int dst_factor_mode0: 3;
				unsigned int reserve_0: 8;
				unsigned int dst_global_alpha0: 8;
				unsigned int reserve_1: 8;
			} bits;
			unsigned int u32;
		} sw_cluster1_dst_color_ctrl;
		union cluster1_src_alpha_ctrl_u { 
			struct cluster1_src_alpha_ctrl_s { 
				unsigned int reserve_0: 1;
				unsigned int src_alpha_mode1: 1;
				unsigned int src_blend_mode1: 2;
				unsigned int src_alpha_cal_mode1: 1;
				unsigned int src_factor_mode1: 3;
				unsigned int reserve_1: 24;
			} bits;
			unsigned int u32;
		} sw_cluster1_src_alpha_ctrl;
		union cluster1_dst_alpha_ctrl_u { 
			struct cluster1_dst_alpha_ctrl_s { 
				unsigned int reserve_0: 1;
				unsigned int dst_alpha_mode1: 1;
				unsigned int dst_blend_mode1: 2;
				unsigned int dst_alpha_cal_mode1: 1;
				unsigned int dst_factor_mode1: 3;
				unsigned int reserve_1: 24;
			} bits;
			unsigned int u32;
		} sw_cluster1_dst_alpha_ctrl;
	} regs;
	unsigned int p_reg_addr[9];
}overlay_system_0x27d00500_t;

typedef union overlay_port0_0x27d00600_u {
	struct overlay_port0_0x27d00600_s {
		union overlay_ctrl_u { 
			struct overlay_ctrl_s { 
				unsigned int overlay_mode: 1;
				unsigned int reserve_0: 3;
				unsigned int hdr10_path_en: 1;
				unsigned int sdr2hdr_path_en: 1;
				unsigned int reserve_1: 26;
			} bits;
			unsigned int u32;
		} sw_overlay_ctrl;
		union layer_sel_u { 
			struct layer_sel_s { 
				unsigned int layer0_sel: 4;
				unsigned int layer1_sel: 4;
				unsigned int layer2_sel: 4;
				unsigned int layer3_sel: 4;
				unsigned int reserve_0: 16;
			} bits;
			unsigned int u32;
		} sw_layer_sel;
		struct { 
			unsigned int reserve_data[28];
		} reserve_reg_8_32;
		union mix0_src_color_ctrl_u { 
			struct mix0_src_color_ctrl_s { 
				unsigned int src_color_mode0: 1;
				unsigned int src_alpha_mode0: 1;
				unsigned int src_blend_mode0: 2;
				unsigned int src_alpha_cal_mode0: 1;
				unsigned int src_factor_mode0: 3;
				unsigned int alpha_en: 1;
				unsigned int src_dst_swap: 1;
				unsigned int reserve_0: 6;
				unsigned int src_global_alpha0: 8;
				unsigned int reserve_1: 8;
			} bits;
			unsigned int u32;
		} sw_mix0_src_color_ctrl;
		union mix0_dst_color_ctrl_u { 
			struct mix0_dst_color_ctrl_s { 
				unsigned int dst_color_mode0: 1;
				unsigned int dst_alpha_mode0: 1;
				unsigned int dst_blend_mode0: 2;
				unsigned int dst_alpha_cal_mode0: 1;
				unsigned int dst_factor_mode0: 3;
				unsigned int reserve_0: 8;
				unsigned int dst_global_alpha0: 8;
				unsigned int reserve_1: 8;
			} bits;
			unsigned int u32;
		} sw_mix0_dst_color_ctrl;
		union mix0_src_alpha_ctrl_u { 
			struct mix0_src_alpha_ctrl_s { 
				unsigned int reserve_0: 1;
				unsigned int src_alpha_mode1: 1;
				unsigned int src_blend_mode1: 2;
				unsigned int src_alpha_cal_mode1: 1;
				unsigned int src_factor_mode1: 3;
				unsigned int reserve_1: 24;
			} bits;
			unsigned int u32;
		} sw_mix0_src_alpha_ctrl;
		union mix0_dst_alpha_ctrl_u { 
			struct mix0_dst_alpha_ctrl_s { 
				unsigned int reserve_0: 1;
				unsigned int dst_alpha_mode1: 1;
				unsigned int dst_blend_mode1: 2;
				unsigned int dst_alpha_cal_mode1: 1;
				unsigned int dst_factor_mode1: 3;
				unsigned int reserve_1: 24;
			} bits;
			unsigned int u32;
		} sw_mix0_dst_alpha_ctrl;
		union mix1_src_color_ctrl_u { 
			struct mix1_src_color_ctrl_s { 
				unsigned int src_color_mode0: 1;
				unsigned int src_alpha_mode0: 1;
				unsigned int src_blend_mode0: 2;
				unsigned int src_alpha_cal_mode0: 1;
				unsigned int src_factor_mode0: 3;
				unsigned int alpha_en: 1;
				unsigned int src_dst_swap: 1;
				unsigned int reserve_0: 6;
				unsigned int src_global_alpha0: 8;
				unsigned int reserve_1: 8;
			} bits;
			unsigned int u32;
		} sw_mix1_src_color_ctrl;
		union mix1_dst_color_ctrl_u { 
			struct mix1_dst_color_ctrl_s { 
				unsigned int dst_color_mode0: 1;
				unsigned int dst_alpha_mode0: 1;
				unsigned int dst_blend_mode0: 2;
				unsigned int dst_alpha_cal_mode0: 1;
				unsigned int dst_factor_mode0: 3;
				unsigned int reserve_0: 8;
				unsigned int dst_global_alpha0: 8;
				unsigned int reserve_1: 8;
			} bits;
			unsigned int u32;
		} sw_mix1_dst_color_ctrl;
		union mix1_src_alpha_ctrl_u { 
			struct mix1_src_alpha_ctrl_s { 
				unsigned int reserve_0: 1;
				unsigned int src_alpha_mode1: 1;
				unsigned int src_blend_mode1: 2;
				unsigned int src_alpha_cal_mode1: 1;
				unsigned int src_factor_mode1: 3;
				unsigned int reserve_1: 24;
			} bits;
			unsigned int u32;
		} sw_mix1_src_alpha_ctrl;
		union mix1_dst_alpha_ctrl_u { 
			struct mix1_dst_alpha_ctrl_s { 
				unsigned int reserve_0: 1;
				unsigned int dst_alpha_mode1: 1;
				unsigned int dst_blend_mode1: 2;
				unsigned int dst_alpha_cal_mode1: 1;
				unsigned int dst_factor_mode1: 3;
				unsigned int reserve_1: 24;
			} bits;
			unsigned int u32;
		} sw_mix1_dst_alpha_ctrl;
		union mix2_src_color_ctrl_u { 
			struct mix2_src_color_ctrl_s { 
				unsigned int src_color_mode0: 1;
				unsigned int src_alpha_mode0: 1;
				unsigned int src_blend_mode0: 2;
				unsigned int src_alpha_cal_mode0: 1;
				unsigned int src_factor_mode0: 3;
				unsigned int alpha_en: 1;
				unsigned int src_dst_swap: 1;
				unsigned int reserve_0: 6;
				unsigned int src_global_alpha0: 8;
				unsigned int reserve_1: 8;
			} bits;
			unsigned int u32;
		} sw_mix2_src_color_ctrl;
		union mix2_dst_color_ctrl_u { 
			struct mix2_dst_color_ctrl_s { 
				unsigned int dst_color_mode0: 1;
				unsigned int dst_alpha_mode0: 1;
				unsigned int dst_blend_mode0: 2;
				unsigned int dst_alpha_cal_mode0: 1;
				unsigned int dst_factor_mode0: 3;
				unsigned int reserve_0: 8;
				unsigned int dst_global_alpha0: 8;
				unsigned int reserve_1: 8;
			} bits;
			unsigned int u32;
		} sw_mix2_dst_color_ctrl;
		union mix2_src_alpha_ctrl_u { 
			struct mix2_src_alpha_ctrl_s { 
				unsigned int reserve_0: 1;
				unsigned int src_alpha_mode1: 1;
				unsigned int src_blend_mode1: 2;
				unsigned int src_alpha_cal_mode1: 1;
				unsigned int src_factor_mode1: 3;
				unsigned int reserve_1: 24;
			} bits;
			unsigned int u32;
		} sw_mix2_src_alpha_ctrl;
		union mix2_dst_alpha_ctrl_u { 
			struct mix2_dst_alpha_ctrl_s { 
				unsigned int reserve_0: 1;
				unsigned int dst_alpha_mode1: 1;
				unsigned int dst_blend_mode1: 2;
				unsigned int dst_alpha_cal_mode1: 1;
				unsigned int dst_factor_mode1: 3;
				unsigned int reserve_1: 24;
			} bits;
			unsigned int u32;
		} sw_mix2_dst_alpha_ctrl;
		union extra_src_color_ctrl_u { 
			struct extra_src_color_ctrl_s { 
				unsigned int src_color_mode0: 1;
				unsigned int src_alpha_mode0: 1;
				unsigned int src_blend_mode0: 2;
				unsigned int src_alpha_cal_mode0: 1;
				unsigned int src_factor_mode0: 3;
				unsigned int alpha_en: 1;
				unsigned int src_dst_swap: 1;
				unsigned int reserve_0: 6;
				unsigned int src_global_alpha0: 8;
				unsigned int reserve_1: 8;
			} bits;
			unsigned int u32;
		} sw_extra_src_color_ctrl;
		union extra_dst_color_ctrl_u { 
			struct extra_dst_color_ctrl_s { 
				unsigned int dst_color_mode0: 1;
				unsigned int dst_alpha_mode0: 1;
				unsigned int dst_blend_mode0: 2;
				unsigned int dst_alpha_cal_mode0: 1;
				unsigned int dst_factor_mode0: 3;
				unsigned int reserve_0: 8;
				unsigned int dst_global_alpha0: 8;
				unsigned int reserve_1: 8;
			} bits;
			unsigned int u32;
		} sw_extra_dst_color_ctrl;
		union extra_src_alpha_ctrl_u { 
			struct extra_src_alpha_ctrl_s { 
				unsigned int reserve_0: 1;
				unsigned int src_alpha_mode1: 1;
				unsigned int src_blend_mode1: 2;
				unsigned int src_alpha_cal_mode1: 1;
				unsigned int src_factor_mode1: 3;
				unsigned int reserve_1: 24;
			} bits;
			unsigned int u32;
		} sw_extra_src_alpha_ctrl;
		union extra_dst_alpha_ctrl_u { 
			struct extra_dst_alpha_ctrl_s { 
				unsigned int reserve_0: 1;
				unsigned int dst_alpha_mode1: 1;
				unsigned int dst_blend_mode1: 2;
				unsigned int dst_alpha_cal_mode1: 1;
				unsigned int dst_factor_mode1: 3;
				unsigned int reserve_1: 24;
			} bits;
			unsigned int u32;
		} sw_extra_dst_alpha_ctrl;
		union hdr_src_color_ctrl_u { 
			struct hdr_src_color_ctrl_s { 
				unsigned int src_color_mode0: 1;
				unsigned int src_alpha_mode0: 1;
				unsigned int src_blend_mode0: 2;
				unsigned int src_alpha_cal_mode0: 1;
				unsigned int src_factor_mode0: 3;
				unsigned int alpha_en: 1;
				unsigned int src_dst_swap: 1;
				unsigned int reserve_0: 6;
				unsigned int src_global_alpha0: 8;
				unsigned int reserve_1: 8;
			} bits;
			unsigned int u32;
		} sw_hdr_src_color_ctrl;
		union hdr_dst_color_ctrl_u { 
			struct hdr_dst_color_ctrl_s { 
				unsigned int dst_color_mode0: 1;
				unsigned int dst_alpha_mode0: 1;
				unsigned int dst_blend_mode0: 2;
				unsigned int dst_alpha_cal_mode0: 1;
				unsigned int dst_factor_mode0: 3;
				unsigned int reserve_0: 8;
				unsigned int dst_global_alpha0: 8;
				unsigned int reserve_1: 8;
			} bits;
			unsigned int u32;
		} sw_hdr_dst_color_ctrl;
		union hdr_src_alpha_ctrl_u { 
			struct hdr_src_alpha_ctrl_s { 
				unsigned int reserve_0: 1;
				unsigned int src_alpha_mode1: 1;
				unsigned int src_blend_mode1: 2;
				unsigned int src_alpha_cal_mode1: 1;
				unsigned int src_factor_mode1: 3;
				unsigned int reserve_1: 24;
			} bits;
			unsigned int u32;
		} sw_hdr_src_alpha_ctrl;
		union hdr_dst_alpha_ctrl_u { 
			struct hdr_dst_alpha_ctrl_s { 
				unsigned int reserve_0: 1;
				unsigned int dst_alpha_mode1: 1;
				unsigned int dst_blend_mode1: 2;
				unsigned int dst_alpha_cal_mode1: 1;
				unsigned int dst_factor_mode1: 3;
				unsigned int reserve_1: 24;
			} bits;
			unsigned int u32;
		} sw_hdr_dst_alpha_ctrl;
		union bg_mix_ctrl_u { 
			struct bg_mix_ctrl_s { 
				unsigned int bg_alpha_en: 1;
				unsigned int bg_alpha_mode: 1;
				unsigned int bg_alpha_pre_mul: 1;
				unsigned int bg_alpha_sat_mode: 1;
				unsigned int bg_line_end_mode: 1;
				unsigned int reserve_0: 3;
				unsigned int bg_global_alpha: 8;
				unsigned int reserve_1: 8;
				unsigned int bg_dly_num: 8;
			} bits;
			unsigned int u32;
		} sw_bg_mix_ctrl;
	} regs;
	unsigned int p_reg_addr[23];
}overlay_port0_0x27d00600_t;

typedef union overlay_port1_0x27d00700_u {
	struct overlay_port1_0x27d00700_s {
		union overlay_ctrl_u { 
			struct overlay_ctrl_s { 
				unsigned int overlay_mode: 1;
				unsigned int reserve_0: 31;
			} bits;
			unsigned int u32;
		} sw_overlay_ctrl;
		union layer_sel_u { 
			struct layer_sel_s { 
				unsigned int layer0_sel: 4;
				unsigned int layer1_sel: 4;
				unsigned int layer2_sel: 4;
				unsigned int layer3_sel: 4;
				unsigned int reserve_0: 16;
			} bits;
			unsigned int u32;
		} sw_layer_sel;
		struct { 
			unsigned int reserve_data[28];
		} reserve_reg_8_32;
		union mix0_src_color_ctrl_u { 
			struct mix0_src_color_ctrl_s { 
				unsigned int src_color_mode0: 1;
				unsigned int src_alpha_mode0: 1;
				unsigned int src_blend_mode0: 2;
				unsigned int src_alpha_cal_mode0: 1;
				unsigned int src_factor_mode0: 3;
				unsigned int alpha_en: 1;
				unsigned int src_dst_swap: 1;
				unsigned int reserve_0: 6;
				unsigned int src_global_alpha0: 8;
				unsigned int reserve_1: 8;
			} bits;
			unsigned int u32;
		} sw_mix0_src_color_ctrl;
		union mix0_dst_color_ctrl_u { 
			struct mix0_dst_color_ctrl_s { 
				unsigned int dst_color_mode0: 1;
				unsigned int dst_alpha_mode0: 1;
				unsigned int dst_blend_mode0: 2;
				unsigned int dst_alpha_cal_mode0: 1;
				unsigned int dst_factor_mode0: 3;
				unsigned int reserve_0: 8;
				unsigned int dst_global_alpha0: 8;
				unsigned int reserve_1: 8;
			} bits;
			unsigned int u32;
		} sw_mix0_dst_color_ctrl;
		union mix0_src_alpha_ctrl_u { 
			struct mix0_src_alpha_ctrl_s { 
				unsigned int reserve_0: 1;
				unsigned int src_alpha_mode1: 1;
				unsigned int src_blend_mode1: 2;
				unsigned int src_alpha_cal_mode1: 1;
				unsigned int src_factor_mode1: 3;
				unsigned int reserve_1: 24;
			} bits;
			unsigned int u32;
		} sw_mix0_src_alpha_ctrl;
		union mix0_dst_alpha_ctrl_u { 
			struct mix0_dst_alpha_ctrl_s { 
				unsigned int reserve_0: 1;
				unsigned int dst_alpha_mode1: 1;
				unsigned int dst_blend_mode1: 2;
				unsigned int dst_alpha_cal_mode1: 1;
				unsigned int dst_factor_mode1: 3;
				unsigned int reserve_1: 24;
			} bits;
			unsigned int u32;
		} sw_mix0_dst_alpha_ctrl;
		union mix1_src_color_ctrl_u { 
			struct mix1_src_color_ctrl_s { 
				unsigned int src_color_mode0: 1;
				unsigned int src_alpha_mode0: 1;
				unsigned int src_blend_mode0: 2;
				unsigned int src_alpha_cal_mode0: 1;
				unsigned int src_factor_mode0: 3;
				unsigned int alpha_en: 1;
				unsigned int src_dst_swap: 1;
				unsigned int reserve_0: 6;
				unsigned int src_global_alpha0: 8;
				unsigned int reserve_1: 8;
			} bits;
			unsigned int u32;
		} sw_mix1_src_color_ctrl;
		union mix1_dst_color_ctrl_u { 
			struct mix1_dst_color_ctrl_s { 
				unsigned int dst_color_mode0: 1;
				unsigned int dst_alpha_mode0: 1;
				unsigned int dst_blend_mode0: 2;
				unsigned int dst_alpha_cal_mode0: 1;
				unsigned int dst_factor_mode0: 3;
				unsigned int reserve_0: 8;
				unsigned int dst_global_alpha0: 8;
				unsigned int reserve_1: 8;
			} bits;
			unsigned int u32;
		} sw_mix1_dst_color_ctrl;
		union mix1_src_alpha_ctrl_u { 
			struct mix1_src_alpha_ctrl_s { 
				unsigned int reserve_0: 1;
				unsigned int src_alpha_mode1: 1;
				unsigned int src_blend_mode1: 2;
				unsigned int src_alpha_cal_mode1: 1;
				unsigned int src_factor_mode1: 3;
				unsigned int reserve_1: 24;
			} bits;
			unsigned int u32;
		} sw_mix1_src_alpha_ctrl;
		union mix1_dst_alpha_ctrl_u { 
			struct mix1_dst_alpha_ctrl_s { 
				unsigned int reserve_0: 1;
				unsigned int dst_alpha_mode1: 1;
				unsigned int dst_blend_mode1: 2;
				unsigned int dst_alpha_cal_mode1: 1;
				unsigned int dst_factor_mode1: 3;
				unsigned int reserve_1: 24;
			} bits;
			unsigned int u32;
		} sw_mix1_dst_alpha_ctrl;
		union mix2_src_color_ctrl_u { 
			struct mix2_src_color_ctrl_s { 
				unsigned int src_color_mode0: 1;
				unsigned int src_alpha_mode0: 1;
				unsigned int src_blend_mode0: 2;
				unsigned int src_alpha_cal_mode0: 1;
				unsigned int src_factor_mode0: 3;
				unsigned int alpha_en: 1;
				unsigned int src_dst_swap: 1;
				unsigned int reserve_0: 6;
				unsigned int src_global_alpha0: 8;
				unsigned int reserve_1: 8;
			} bits;
			unsigned int u32;
		} sw_mix2_src_color_ctrl;
		union mix2_dst_color_ctrl_u { 
			struct mix2_dst_color_ctrl_s { 
				unsigned int dst_color_mode0: 1;
				unsigned int dst_alpha_mode0: 1;
				unsigned int dst_blend_mode0: 2;
				unsigned int dst_alpha_cal_mode0: 1;
				unsigned int dst_factor_mode0: 3;
				unsigned int reserve_0: 8;
				unsigned int dst_global_alpha0: 8;
				unsigned int reserve_1: 8;
			} bits;
			unsigned int u32;
		} sw_mix2_dst_color_ctrl;
		union mix2_src_alpha_ctrl_u { 
			struct mix2_src_alpha_ctrl_s { 
				unsigned int reserve_0: 1;
				unsigned int src_alpha_mode1: 1;
				unsigned int src_blend_mode1: 2;
				unsigned int src_alpha_cal_mode1: 1;
				unsigned int src_factor_mode1: 3;
				unsigned int reserve_1: 24;
			} bits;
			unsigned int u32;
		} sw_mix2_src_alpha_ctrl;
		union mix2_dst_alpha_ctrl_u { 
			struct mix2_dst_alpha_ctrl_s { 
				unsigned int reserve_0: 1;
				unsigned int dst_alpha_mode1: 1;
				unsigned int dst_blend_mode1: 2;
				unsigned int dst_alpha_cal_mode1: 1;
				unsigned int dst_factor_mode1: 3;
				unsigned int reserve_1: 24;
			} bits;
			unsigned int u32;
		} sw_mix2_dst_alpha_ctrl;
		struct { 
			unsigned int reserve_data[32];
		} reserve_reg_84_112;
		union bg_mix_ctrl_u { 
			struct bg_mix_ctrl_s { 
				unsigned int bg_alpha_en: 1;
				unsigned int bg_alpha_mode: 1;
				unsigned int bg_alpha_pre_mul: 1;
				unsigned int bg_alpha_sat_mode: 1;
				unsigned int bg_line_end_mode: 1;
				unsigned int reserve_0: 3;
				unsigned int bg_global_alpha: 8;
				unsigned int reserve_1: 8;
				unsigned int bg_dly_num: 8;
			} bits;
			unsigned int u32;
		} sw_bg_mix_ctrl;
	} regs;
	unsigned int p_reg_addr[15];
}overlay_port1_0x27d00700_t;

typedef union overlay_port2_0x27d00800_u {
	struct overlay_port2_0x27d00800_s {
		union overlay_ctrl_u { 
			struct overlay_ctrl_s { 
				unsigned int overlay_mode: 1;
				unsigned int reserve_0: 31;
			} bits;
			unsigned int u32;
		} sw_overlay_ctrl;
		union layer_sel_u { 
			struct layer_sel_s { 
				unsigned int layer0_sel: 4;
				unsigned int layer1_sel: 4;
				unsigned int layer2_sel: 4;
				unsigned int layer3_sel: 4;
				unsigned int reserve_0: 16;
			} bits;
			unsigned int u32;
		} sw_layer_sel;
		struct { 
			unsigned int reserve_data[28];
		} reserve_reg_8_32;
		union mix0_src_color_ctrl_u { 
			struct mix0_src_color_ctrl_s { 
				unsigned int src_color_mode0: 1;
				unsigned int src_alpha_mode0: 1;
				unsigned int src_blend_mode0: 2;
				unsigned int src_alpha_cal_mode0: 1;
				unsigned int src_factor_mode0: 3;
				unsigned int alpha_en: 1;
				unsigned int src_dst_swap: 1;
				unsigned int reserve_0: 6;
				unsigned int src_global_alpha0: 8;
				unsigned int reserve_1: 8;
			} bits;
			unsigned int u32;
		} sw_mix0_src_color_ctrl;
		union mix0_dst_color_ctrl_u { 
			struct mix0_dst_color_ctrl_s { 
				unsigned int dst_color_mode0: 1;
				unsigned int dst_alpha_mode0: 1;
				unsigned int dst_blend_mode0: 2;
				unsigned int dst_alpha_cal_mode0: 1;
				unsigned int dst_factor_mode0: 3;
				unsigned int reserve_0: 8;
				unsigned int dst_global_alpha0: 8;
				unsigned int reserve_1: 8;
			} bits;
			unsigned int u32;
		} sw_mix0_dst_color_ctrl;
		union mix0_src_alpha_ctrl_u { 
			struct mix0_src_alpha_ctrl_s { 
				unsigned int reserve_0: 1;
				unsigned int src_alpha_mode1: 1;
				unsigned int src_blend_mode1: 2;
				unsigned int src_alpha_cal_mode1: 1;
				unsigned int src_factor_mode1: 3;
				unsigned int reserve_1: 24;
			} bits;
			unsigned int u32;
		} sw_mix0_src_alpha_ctrl;
		union mix0_dst_alpha_ctrl_u { 
			struct mix0_dst_alpha_ctrl_s { 
				unsigned int reserve_0: 1;
				unsigned int dst_alpha_mode1: 1;
				unsigned int dst_blend_mode1: 2;
				unsigned int dst_alpha_cal_mode1: 1;
				unsigned int dst_factor_mode1: 3;
				unsigned int reserve_1: 24;
			} bits;
			unsigned int u32;
		} sw_mix0_dst_alpha_ctrl;
		union mix1_src_color_ctrl_u { 
			struct mix1_src_color_ctrl_s { 
				unsigned int src_color_mode0: 1;
				unsigned int src_alpha_mode0: 1;
				unsigned int src_blend_mode0: 2;
				unsigned int src_alpha_cal_mode0: 1;
				unsigned int src_factor_mode0: 3;
				unsigned int alpha_en: 1;
				unsigned int src_dst_swap: 1;
				unsigned int reserve_0: 6;
				unsigned int src_global_alpha0: 8;
				unsigned int reserve_1: 8;
			} bits;
			unsigned int u32;
		} sw_mix1_src_color_ctrl;
		union mix1_dst_color_ctrl_u { 
			struct mix1_dst_color_ctrl_s { 
				unsigned int dst_color_mode0: 1;
				unsigned int dst_alpha_mode0: 1;
				unsigned int dst_blend_mode0: 2;
				unsigned int dst_alpha_cal_mode0: 1;
				unsigned int dst_factor_mode0: 3;
				unsigned int reserve_0: 8;
				unsigned int dst_global_alpha0: 8;
				unsigned int reserve_1: 8;
			} bits;
			unsigned int u32;
		} sw_mix1_dst_color_ctrl;
		union mix1_src_alpha_ctrl_u { 
			struct mix1_src_alpha_ctrl_s { 
				unsigned int reserve_0: 1;
				unsigned int src_alpha_mode1: 1;
				unsigned int src_blend_mode1: 2;
				unsigned int src_alpha_cal_mode1: 1;
				unsigned int src_factor_mode1: 3;
				unsigned int reserve_1: 24;
			} bits;
			unsigned int u32;
		} sw_mix1_src_alpha_ctrl;
		union mix1_dst_alpha_ctrl_u { 
			struct mix1_dst_alpha_ctrl_s { 
				unsigned int reserve_0: 1;
				unsigned int dst_alpha_mode1: 1;
				unsigned int dst_blend_mode1: 2;
				unsigned int dst_alpha_cal_mode1: 1;
				unsigned int dst_factor_mode1: 3;
				unsigned int reserve_1: 24;
			} bits;
			unsigned int u32;
		} sw_mix1_dst_alpha_ctrl;
		union mix2_src_color_ctrl_u { 
			struct mix2_src_color_ctrl_s { 
				unsigned int src_color_mode0: 1;
				unsigned int src_alpha_mode0: 1;
				unsigned int src_blend_mode0: 2;
				unsigned int src_alpha_cal_mode0: 1;
				unsigned int src_factor_mode0: 3;
				unsigned int alpha_en: 1;
				unsigned int src_dst_swap: 1;
				unsigned int reserve_0: 6;
				unsigned int src_global_alpha0: 8;
				unsigned int reserve_1: 8;
			} bits;
			unsigned int u32;
		} sw_mix2_src_color_ctrl;
		union mix2_dst_color_ctrl_u { 
			struct mix2_dst_color_ctrl_s { 
				unsigned int dst_color_mode0: 1;
				unsigned int dst_alpha_mode0: 1;
				unsigned int dst_blend_mode0: 2;
				unsigned int dst_alpha_cal_mode0: 1;
				unsigned int dst_factor_mode0: 3;
				unsigned int reserve_0: 8;
				unsigned int dst_global_alpha0: 8;
				unsigned int reserve_1: 8;
			} bits;
			unsigned int u32;
		} sw_mix2_dst_color_ctrl;
		union mix2_src_alpha_ctrl_u { 
			struct mix2_src_alpha_ctrl_s { 
				unsigned int reserve_0: 1;
				unsigned int src_alpha_mode1: 1;
				unsigned int src_blend_mode1: 2;
				unsigned int src_alpha_cal_mode1: 1;
				unsigned int src_factor_mode1: 3;
				unsigned int reserve_1: 24;
			} bits;
			unsigned int u32;
		} sw_mix2_src_alpha_ctrl;
		union mix2_dst_alpha_ctrl_u { 
			struct mix2_dst_alpha_ctrl_s { 
				unsigned int reserve_0: 1;
				unsigned int dst_alpha_mode1: 1;
				unsigned int dst_blend_mode1: 2;
				unsigned int dst_alpha_cal_mode1: 1;
				unsigned int dst_factor_mode1: 3;
				unsigned int reserve_1: 24;
			} bits;
			unsigned int u32;
		} sw_mix2_dst_alpha_ctrl;
		struct { 
			unsigned int reserve_data[32];
		} reserve_reg_84_112;
		union bg_mix_ctrl_u { 
			struct bg_mix_ctrl_s { 
				unsigned int bg_alpha_en: 1;
				unsigned int bg_alpha_mode: 1;
				unsigned int bg_alpha_pre_mul: 1;
				unsigned int bg_alpha_sat_mode: 1;
				unsigned int bg_line_end_mode: 1;
				unsigned int reserve_0: 3;
				unsigned int bg_global_alpha: 8;
				unsigned int reserve_1: 8;
				unsigned int bg_dly_num: 8;
			} bits;
			unsigned int u32;
		} sw_bg_mix_ctrl;
	} regs;
	unsigned int p_reg_addr[15];
}overlay_port2_0x27d00800_t;

typedef union post0_ctrl_0x27d00c00_u {
	struct post0_ctrl_0x27d00c00_s {
		union post_dsp_ctrl_u { 
			struct post_dsp_ctrl_s { 
				unsigned int dsp_out_mode: 4;
				unsigned int reserve_0: 1;
				unsigned int dsp_p2i_en: 1;
				unsigned int dsp_filed_pol: 1;
				unsigned int dsp_interlace: 1;
				unsigned int dsp_bg_swap: 1;
				unsigned int dsp_rb_swap: 1;
				unsigned int dsp_rg_swap: 1;
				unsigned int dsp_delta_swap: 1;
				unsigned int dsp_dummy_swap: 1;
				unsigned int dsp_x_mir_en: 1;
				unsigned int reserve_1: 1;
				unsigned int dsp_out_rgb_yuv: 1;
				unsigned int pre_dither_down_en: 1;
				unsigned int dither_down_en: 1;
				unsigned int dither_down_sel: 2;
				unsigned int dither_down_mode: 1;
				unsigned int reserve_2: 1;
				unsigned int gamma_update_en: 1;
				unsigned int post_lb_mode: 1;
				unsigned int dsp_blank_en: 1;
				unsigned int reserve_3: 1;
				unsigned int dsp_out_zero: 1;
				unsigned int dsp_black_en: 1;
				unsigned int dsp_lut_en: 1;
				unsigned int reserve_4: 1;
				unsigned int vop_fp_standby_en_imd: 1;
				unsigned int vop_standby_en_imd: 1;
			} bits;
			unsigned int u32;
		} sw_post_dsp_ctrl;
		union post_mipi_ctrl_u { 
			struct post_mipi_ctrl_s { 
				unsigned int reserve_0: 20;
				unsigned int doub_channel_en: 1;
				unsigned int doub_channel_swap: 1;
				unsigned int reserve_1: 2;
				unsigned int doub_channel_overlap_num: 4;
				unsigned int edpi_te_en: 1;
				unsigned int edpi_te_mode: 1;
				unsigned int edpi_wms_hold_en: 1;
				unsigned int edpi_wms_fs: 1;
			} bits;
			unsigned int u32;
		} sw_post_mipi_ctrl;
		union post_color_ctrl_u { 
			struct post_color_ctrl_s { 
				unsigned int color_bar_en: 1;
				unsigned int color_bar_mode: 1;
				unsigned int reserve_0: 2;
				unsigned int io_vsync_sel: 2;
				unsigned int reserve_1: 2;
				unsigned int vfp_dma_stop: 1;
				unsigned int reserve_2: 23;
			} bits;
			unsigned int u32;
		} sw_post_color_ctrl;
		union post_core_clk_u { 
			struct post_core_clk_s { 
				unsigned int dclk_core_sel: 1;
				unsigned int reserve_0: 1;
				unsigned int dclk_out_sel: 1;
				unsigned int reserve_1: 29;
			} bits;
			unsigned int u32;
		} sw_post_core_clk;
		union post_3d_lut_ctrl_u { 
			struct post_3d_lut_ctrl_s { 
				unsigned int dsp_3dlut_en: 1;
				unsigned int dsp_3dlut_bypass_en: 1;
				unsigned int dsp_3dlut_update_en: 1;
				unsigned int dsp_3dlut_mode: 1;
				unsigned int dsp_3dlut_gating_en: 1;
				unsigned int reserve_0: 11;
				unsigned int dsp_3dlut_addr: 16;
			} bits;
			unsigned int u32;
		} sw_post_3d_lut_ctrl;
		union post_3d_lut_r_u { 
			struct post_3d_lut_r_s { 
				unsigned int lut_3d_r_comp: 12;
				unsigned int reserve_0: 20;
			} bits;
			unsigned int u32;
		} sw_post_3d_lut_r;
		union post_3d_lut_g_u { 
			struct post_3d_lut_g_s { 
				unsigned int lut_3d_g_comp: 12;
				unsigned int reserve_0: 20;
			} bits;
			unsigned int u32;
		} sw_post_3d_lut_g;
		union post_3d_lut_b_u { 
			struct post_3d_lut_b_s { 
				unsigned int lut_3d_b_comp: 12;
				unsigned int reserve_0: 20;
			} bits;
			unsigned int u32;
		} sw_post_3d_lut_b;
		union post_3dlut_mst_u { 
			struct post_3dlut_mst_s { 
				unsigned int post_3dlut_mst: 32;
			} bits;
			unsigned int u32;
		} sw_post_3dlut_mst;
		struct { 
			unsigned int reserve_data[12];
		} reserve_reg_36_44;
		union post_dsp_bg_u { 
			struct post_dsp_bg_s { 
				unsigned int dsp_bg_green: 10;
				unsigned int dsp_bg_blue: 10;
				unsigned int dsp_bg_red: 10;
				unsigned int reserve_0: 1;
				unsigned int bg_display_en: 1;
			} bits;
			unsigned int u32;
		} sw_post_dsp_bg;
		union post_pre_scan_htiming_u { 
			struct post_pre_scan_htiming_s { 
				unsigned int pre_scan_hblank: 13;
				unsigned int reserve_0: 3;
				unsigned int pre_scan_hactive: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_post_pre_scan_htiming;
		union post_dsp_hact_info_u { 
			struct post_dsp_hact_info_s { 
				unsigned int dsp_hact_end_post: 13;
				unsigned int reserve_0: 3;
				unsigned int dsp_hact_st_post: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_post_dsp_hact_info;
		union post_dsp_vact_info_u { 
			struct post_dsp_vact_info_s { 
				unsigned int dsp_vact_end_post: 13;
				unsigned int reserve_0: 3;
				unsigned int dsp_vact_st_post: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_post_dsp_vact_info;
		union post_scl_factor_yrgb_u { 
			struct post_scl_factor_yrgb_s { 
				unsigned int post_hs_factor: 16;
				unsigned int post_vs_factor: 16;
			} bits;
			unsigned int u32;
		} sw_post_scl_factor_yrgb;
		union post_scl_ctrl_u { 
			struct post_scl_ctrl_s { 
				unsigned int post_hor_sd_en: 1;
				unsigned int post_ver_sd_en: 1;
				unsigned int reserve_0: 2;
				unsigned int post_vsd_dly_en: 1;
				unsigned int post_empty_cheating_en: 1;
				unsigned int sharpness_cheating_en: 1;
				unsigned int reserve_1: 25;
			} bits;
			unsigned int u32;
		} sw_post_scl_ctrl;
		union post_dsp_vact_info_f1_u { 
			struct post_dsp_vact_info_f1_s { 
				unsigned int dsp_vact_end_post_f1: 13;
				unsigned int reserve_0: 3;
				unsigned int dsp_vact_st_post_f1: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_post_dsp_vact_info_f1;
		union post_dsp_htotal_hs_end_u { 
			struct post_dsp_htotal_hs_end_s { 
				unsigned int dsp_hs_end: 13;
				unsigned int reserve_0: 3;
				unsigned int dsp_htotal: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_post_dsp_htotal_hs_end;
		union post_dsp_hact_st_end_u { 
			struct post_dsp_hact_st_end_s { 
				unsigned int dsp_hact_end: 13;
				unsigned int reserve_0: 3;
				unsigned int dsp_hact_st: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_post_dsp_hact_st_end;
		union post_dsp_vtotal_vs_end_u { 
			struct post_dsp_vtotal_vs_end_s { 
				unsigned int dsp_vs_end: 13;
				unsigned int reserve_0: 2;
				unsigned int sw_dsp_vtotal_imd: 1;
				unsigned int dsp_vtotal: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_post_dsp_vtotal_vs_end;
		union post_dsp_vact_st_end_u { 
			struct post_dsp_vact_st_end_s { 
				unsigned int dsp_vact_end: 13;
				unsigned int reserve_0: 3;
				unsigned int dsp_vact_st: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_post_dsp_vact_st_end;
		union post_dsp_vs_st_end_f1_u { 
			struct post_dsp_vs_st_end_f1_s { 
				unsigned int dsp_vs_end_f1: 13;
				unsigned int reserve_0: 3;
				unsigned int dsp_vs_st_f1: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_post_dsp_vs_st_end_f1;
		union post_dsp_vact_st_end_f1_u { 
			struct post_dsp_vact_st_end_f1_s { 
				unsigned int dsp_vact_end_f1: 13;
				unsigned int reserve_0: 3;
				unsigned int dsp_vact_st_f1: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_post_dsp_vact_st_end_f1;
		struct { 
			unsigned int reserve_data[64];
		} reserve_reg_100_160;
		union post_dither_frc_0_u { 
			struct post_dither_frc_0_s { 
				unsigned int sw_frc_dither_mode: 2;
				unsigned int sw_frc_rcr_pattern: 2;
				unsigned int sw_frc_gy_pattern: 2;
				unsigned int sw_frc_bcb_pattern: 2;
				unsigned int reserve_0: 24;
			} bits;
			unsigned int u32;
		} sw_post_dither_frc_0;
		union post_dither_frc_1_u { 
			struct post_dither_frc_1_s { 
				unsigned int sw_frc_rcr_strength: 10;
				unsigned int reserve_0: 6;
				unsigned int sw_frc_gy_strength: 10;
				unsigned int reserve_1: 6;
			} bits;
			unsigned int u32;
		} sw_post_dither_frc_1;
		union post_dither_frc_2_u { 
			struct post_dither_frc_2_s { 
				unsigned int sw_frc_bcb_strength: 10;
				unsigned int reserve_0: 6;
				unsigned int sw_range_sca: 14;
				unsigned int reserve_1: 2;
			} bits;
			unsigned int u32;
		} sw_post_dither_frc_2;
		struct { 
			unsigned int reserve_data[36];
		} reserve_reg_176_208;
		union post_acm_ctrl_u { 
			struct post_acm_ctrl_s { 
				unsigned int acm_bypass_en: 1;
				unsigned int acm_y2r_en: 1;
				unsigned int acm_r2y_en: 1;
				unsigned int reserve_0: 5;
				unsigned int acm_r2y_mode: 3;
				unsigned int reserve_1: 5;
				unsigned int acm_y2r_coe00: 16;
			} bits;
			unsigned int u32;
		} sw_post_acm_ctrl;
		union post_acm_y2r_coe0102_u { 
			struct post_acm_y2r_coe0102_s { 
				unsigned int acm_y2r_coe01: 16;
				unsigned int acm_y2r_coe02: 16;
			} bits;
			unsigned int u32;
		} sw_post_acm_y2r_coe0102;
		union post_acm_y2r_coe1011_u { 
			struct post_acm_y2r_coe1011_s { 
				unsigned int acm_y2r_coe10: 16;
				unsigned int acm_y2r_coe11: 16;
			} bits;
			unsigned int u32;
		} sw_post_acm_y2r_coe1011;
		union post_acm_y2r_coe1220_u { 
			struct post_acm_y2r_coe1220_s { 
				unsigned int acm_y2r_coe12: 16;
				unsigned int acm_y2r_coe20: 16;
			} bits;
			unsigned int u32;
		} sw_post_acm_y2r_coe1220;
		union post_acm_y2r_coe2122_u { 
			struct post_acm_y2r_coe2122_s { 
				unsigned int acm_y2r_coe21: 16;
				unsigned int acm_y2r_coe22: 16;
			} bits;
			unsigned int u32;
		} sw_post_acm_y2r_coe2122;
		union post_acm_y2r_offset0_u { 
			struct post_acm_y2r_offset0_s { 
				unsigned int acm_y2r_offset0: 32;
			} bits;
			unsigned int u32;
		} sw_post_acm_y2r_offset0;
		union post_acm_y2r_offset1_u { 
			struct post_acm_y2r_offset1_s { 
				unsigned int acm_y2r_offset1: 32;
			} bits;
			unsigned int u32;
		} sw_post_acm_y2r_offset1;
		union post_acm_y2r_offset2_u { 
			struct post_acm_y2r_offset2_s { 
				unsigned int acm_y2r_offset2: 32;
			} bits;
			unsigned int u32;
		} sw_post_acm_y2r_offset2;
		union post_clk_cnt_u { 
			struct post_clk_cnt_s { 
				unsigned int calc_dclk_cnt: 15;
				unsigned int calc_clk_en: 1;
				unsigned int calc_aclk_cnt: 16;
			} bits;
			unsigned int u32;
		} sw_post_clk_cnt;
		union post_mcu_ctrl_u { 
			struct post_mcu_ctrl_s { 
				unsigned int mcu_pix_total: 6;
				unsigned int mcu_cs_pst: 4;
				unsigned int mcu_cs_pend: 6;
				unsigned int mcu_rw_pst: 4;
				unsigned int mcu_rw_pend: 6;
				unsigned int reserve_0: 1;
				unsigned int mcu_hold_mode: 1;
				unsigned int mcu_frm_st: 1;
				unsigned int mcu_rs: 1;
				unsigned int mcu_bypass_en: 1;
				unsigned int mcu_type_en: 1;
			} bits;
			unsigned int u32;
		} sw_post_mcu_ctrl;
	} regs;
	unsigned int p_reg_addr[35];
}post0_ctrl_0x27d00c00_t;

typedef union post1_ctrl_0x27d00d00_u {
	struct post1_ctrl_0x27d00d00_s {
		union post_dsp_ctrl_u { 
			struct post_dsp_ctrl_s { 
				unsigned int dsp_out_mode: 4;
				unsigned int reserve_0: 1;
				unsigned int dsp_p2i_en: 1;
				unsigned int dsp_filed_pol: 1;
				unsigned int dsp_interlace: 1;
				unsigned int dsp_bg_swap: 1;
				unsigned int dsp_rb_swap: 1;
				unsigned int dsp_rg_swap: 1;
				unsigned int dsp_delta_swap: 1;
				unsigned int dsp_dummy_swap: 1;
				unsigned int dsp_x_mir_en: 1;
				unsigned int reserve_1: 1;
				unsigned int dsp_out_rgb_yuv: 1;
				unsigned int pre_dither_down_en: 1;
				unsigned int dither_down_en: 1;
				unsigned int dither_down_sel: 2;
				unsigned int dither_down_mode: 1;
				unsigned int reserve_2: 1;
				unsigned int gamma_update_en: 1;
				unsigned int reserve_3: 1;
				unsigned int dsp_blank_en: 1;
				unsigned int reserve_4: 1;
				unsigned int dsp_out_zero: 1;
				unsigned int dsp_black_en: 1;
				unsigned int dsp_lut_en: 1;
				unsigned int reserve_5: 1;
				unsigned int vop_fp_standby_en_imd: 1;
				unsigned int vop_standby_en_imd: 1;
			} bits;
			unsigned int u32;
		} sw_post_dsp_ctrl;
		union post_mipi_ctrl_u { 
			struct post_mipi_ctrl_s { 
				unsigned int reserve_0: 20;
				unsigned int doub_channel_en: 1;
				unsigned int doub_channel_swap: 1;
				unsigned int reserve_1: 2;
				unsigned int doub_channel_overlap_num: 4;
				unsigned int edpi_te_en: 1;
				unsigned int edpi_te_mode: 1;
				unsigned int edpi_wms_hold_en: 1;
				unsigned int edpi_wms_fs: 1;
			} bits;
			unsigned int u32;
		} sw_post_mipi_ctrl;
		union post_color_ctrl_u { 
			struct post_color_ctrl_s { 
				unsigned int color_bar_en: 1;
				unsigned int color_bar_mode: 1;
				unsigned int reserve_0: 2;
				unsigned int io_vsync_sel: 2;
				unsigned int reserve_1: 26;
			} bits;
			unsigned int u32;
		} sw_post_color_ctrl;
		union post_core_clk_u { 
			struct post_core_clk_s { 
				unsigned int dclk_core_sel: 1;
				unsigned int reserve_0: 1;
				unsigned int dclk_out_sel: 1;
				unsigned int reserve_1: 29;
			} bits;
			unsigned int u32;
		} sw_post_core_clk;
		struct { 
			unsigned int reserve_data[32];
		} reserve_reg_16_44;
		union post_dsp_bg_u { 
			struct post_dsp_bg_s { 
				unsigned int dsp_bg_green: 10;
				unsigned int dsp_bg_blue: 10;
				unsigned int dsp_bg_red: 10;
				unsigned int reserve_0: 1;
				unsigned int bg_display_en: 1;
			} bits;
			unsigned int u32;
		} sw_post_dsp_bg;
		union post_pre_scan_htiming_u { 
			struct post_pre_scan_htiming_s { 
				unsigned int pre_scan_hblank: 13;
				unsigned int reserve_0: 3;
				unsigned int pre_scan_hactive: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_post_pre_scan_htiming;
		union post_dsp_hact_info_u { 
			struct post_dsp_hact_info_s { 
				unsigned int dsp_hact_end_post: 13;
				unsigned int reserve_0: 3;
				unsigned int dsp_hact_st_post: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_post_dsp_hact_info;
		union post_dsp_vact_info_u { 
			struct post_dsp_vact_info_s { 
				unsigned int dsp_vact_end_post: 13;
				unsigned int reserve_0: 3;
				unsigned int dsp_vact_st_post: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_post_dsp_vact_info;
		union post_scl_factor_yrgb_u { 
			struct post_scl_factor_yrgb_s { 
				unsigned int post_hs_factor: 16;
				unsigned int post_vs_factor: 16;
			} bits;
			unsigned int u32;
		} sw_post_scl_factor_yrgb;
		union post_scl_ctrl_u { 
			struct post_scl_ctrl_s { 
				unsigned int post_hor_sd_en: 1;
				unsigned int post_ver_sd_en: 1;
				unsigned int reserve_0: 2;
				unsigned int post_vsd_dly_en: 1;
				unsigned int post_empty_cheating_en: 1;
				unsigned int reserve_1: 26;
			} bits;
			unsigned int u32;
		} sw_post_scl_ctrl;
		union post_dsp_vact_info_f1_u { 
			struct post_dsp_vact_info_f1_s { 
				unsigned int dsp_vact_end_post_f1: 13;
				unsigned int reserve_0: 3;
				unsigned int dsp_vact_st_post_f1: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_post_dsp_vact_info_f1;
		union post_dsp_htotal_hs_end_u { 
			struct post_dsp_htotal_hs_end_s { 
				unsigned int dsp_hs_end: 13;
				unsigned int reserve_0: 3;
				unsigned int dsp_htotal: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_post_dsp_htotal_hs_end;
		union post_dsp_hact_st_end_u { 
			struct post_dsp_hact_st_end_s { 
				unsigned int dsp_hact_end: 13;
				unsigned int reserve_0: 3;
				unsigned int dsp_hact_st: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_post_dsp_hact_st_end;
		union post_dsp_vtotal_vs_end_u { 
			struct post_dsp_vtotal_vs_end_s { 
				unsigned int dsp_vs_end: 13;
				unsigned int reserve_0: 2;
				unsigned int sw_dsp_vtotal_imd: 1;
				unsigned int dsp_vtotal: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_post_dsp_vtotal_vs_end;
		union post_dsp_vact_st_end_u { 
			struct post_dsp_vact_st_end_s { 
				unsigned int dsp_vact_end: 13;
				unsigned int reserve_0: 3;
				unsigned int dsp_vact_st: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_post_dsp_vact_st_end;
		union post_dsp_vs_st_end_f1_u { 
			struct post_dsp_vs_st_end_f1_s { 
				unsigned int dsp_vs_end_f1: 13;
				unsigned int reserve_0: 3;
				unsigned int dsp_vs_st_f1: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_post_dsp_vs_st_end_f1;
		union post_dsp_vact_st_end_f1_u { 
			struct post_dsp_vact_st_end_f1_s { 
				unsigned int dsp_vact_end_f1: 13;
				unsigned int reserve_0: 3;
				unsigned int dsp_vact_st_f1: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_post_dsp_vact_st_end_f1;
		union post_bcsh_ctrl_u { 
			struct post_bcsh_ctrl_s { 
				unsigned int bcsh_y2r_en: 1;
				unsigned int reserve_0: 1;
				unsigned int bcsh_y2r_csc_mode: 2;
				unsigned int bcsh_r2y_en: 1;
				unsigned int reserve_1: 1;
				unsigned int bcsh_r2y_csc_mode: 2;
				unsigned int reserve_2: 24;
			} bits;
			unsigned int u32;
		} sw_post_bcsh_ctrl;
		union post_bcsh_bcs_u { 
			struct post_bcsh_bcs_s { 
				unsigned int brightness: 8;
				unsigned int contrast: 9;
				unsigned int reserve_0: 3;
				unsigned int sat_con: 10;
				unsigned int out_mode: 2;
			} bits;
			unsigned int u32;
		} sw_post_bcsh_bcs;
		union post_bcsh_h_u { 
			struct post_bcsh_h_s { 
				unsigned int sin_hue: 9;
				unsigned int reserve_0: 7;
				unsigned int cos_hue: 9;
				unsigned int reserve_1: 7;
			} bits;
			unsigned int u32;
		} sw_post_bcsh_h;
		union post_bcsh_color_bar_u { 
			struct post_bcsh_color_bar_s { 
				unsigned int color_bar_y: 10;
				unsigned int color_bar_u: 10;
				unsigned int color_bar_v: 10;
				unsigned int reserve_0: 1;
				unsigned int bcsh_en: 1;
			} bits;
			unsigned int u32;
		} sw_post_bcsh_color_bar;
		struct { 
			unsigned int reserve_data[48];
		} reserve_reg_116_160;
		union post_dither_frc_0_u { 
			struct post_dither_frc_0_s { 
				unsigned int sw_frc_dither_mode: 2;
				unsigned int sw_frc_rcr_pattern: 2;
				unsigned int sw_frc_gy_pattern: 2;
				unsigned int sw_frc_bcb_pattern: 2;
				unsigned int reserve_0: 24;
			} bits;
			unsigned int u32;
		} sw_post_dither_frc_0;
		union post_dither_frc_1_u { 
			struct post_dither_frc_1_s { 
				unsigned int sw_frc_rcr_strength: 10;
				unsigned int reserve_0: 6;
				unsigned int sw_frc_gy_strength: 10;
				unsigned int reserve_1: 6;
			} bits;
			unsigned int u32;
		} sw_post_dither_frc_1;
		union post_dither_frc_2_u { 
			struct post_dither_frc_2_s { 
				unsigned int sw_frc_bcb_strength: 10;
				unsigned int reserve_0: 6;
				unsigned int sw_range_sca: 14;
				unsigned int reserve_1: 2;
			} bits;
			unsigned int u32;
		} sw_post_dither_frc_2;
		struct { 
			unsigned int reserve_data[72];
		} reserve_reg_176_244;
		union post_clk_cnt_u { 
			struct post_clk_cnt_s { 
				unsigned int calc_dclk_cnt: 15;
				unsigned int calc_clk_en: 1;
				unsigned int calc_aclk_cnt: 16;
			} bits;
			unsigned int u32;
		} sw_post_clk_cnt;
		union post_mcu_ctrl_u { 
			struct post_mcu_ctrl_s { 
				unsigned int mcu_pix_total: 6;
				unsigned int mcu_cs_pst: 4;
				unsigned int mcu_cs_pend: 6;
				unsigned int mcu_rw_pst: 4;
				unsigned int mcu_rw_pend: 6;
				unsigned int reserve_0: 1;
				unsigned int mcu_hold_mode: 1;
				unsigned int mcu_frm_st: 1;
				unsigned int mcu_rs: 1;
				unsigned int mcu_bypass_en: 1;
				unsigned int mcu_type_en: 1;
			} bits;
			unsigned int u32;
		} sw_post_mcu_ctrl;
	} regs;
	unsigned int p_reg_addr[26];
}post1_ctrl_0x27d00d00_t;

typedef union post2_ctrl_0x27d00e00_u {
	struct post2_ctrl_0x27d00e00_s {
		union post_dsp_ctrl_u { 
			struct post_dsp_ctrl_s { 
				unsigned int dsp_out_mode: 4;
				unsigned int reserve_0: 1;
				unsigned int dsp_p2i_en: 1;
				unsigned int dsp_filed_pol: 1;
				unsigned int dsp_interlace: 1;
				unsigned int dsp_bg_swap: 1;
				unsigned int dsp_rb_swap: 1;
				unsigned int dsp_rg_swap: 1;
				unsigned int dsp_delta_swap: 1;
				unsigned int dsp_dummy_swap: 1;
				unsigned int dsp_x_mir_en: 1;
				unsigned int reserve_1: 1;
				unsigned int dsp_out_rgb_yuv: 1;
				unsigned int reserve_2: 1;
				unsigned int dither_down_en: 1;
				unsigned int dither_down_sel: 2;
				unsigned int dither_down_mode: 1;
				unsigned int reserve_3: 1;
				unsigned int gamma_update_en: 1;
				unsigned int post_lb_mode: 1;
				unsigned int dsp_blank_en: 1;
				unsigned int reserve_4: 1;
				unsigned int dsp_out_zero: 1;
				unsigned int dsp_black_en: 1;
				unsigned int dsp_lut_en: 1;
				unsigned int reserve_5: 1;
				unsigned int vop_fp_standby_en_imd: 1;
				unsigned int vop_standby_en_imd: 1;
			} bits;
			unsigned int u32;
		} sw_post_dsp_ctrl;
		union post_mipi_ctrl_u { 
			struct post_mipi_ctrl_s { 
				unsigned int reserve_0: 20;
				unsigned int doub_channel_en: 1;
				unsigned int doub_channel_swap: 1;
				unsigned int reserve_1: 2;
				unsigned int doub_channel_overlap_num: 4;
				unsigned int edpi_te_en: 1;
				unsigned int edpi_te_mode: 1;
				unsigned int edpi_wms_hold_en: 1;
				unsigned int edpi_wms_fs: 1;
			} bits;
			unsigned int u32;
		} sw_post_mipi_ctrl;
		union post_color_ctrl_u { 
			struct post_color_ctrl_s { 
				unsigned int color_bar_en: 1;
				unsigned int color_bar_mode: 1;
				unsigned int reserve_0: 2;
				unsigned int io_vsync_sel: 2;
				unsigned int reserve_1: 26;
			} bits;
			unsigned int u32;
		} sw_post_color_ctrl;
		union post_core_clk_u { 
			struct post_core_clk_s { 
				unsigned int dclk_core_sel: 1;
				unsigned int reserve_0: 1;
				unsigned int dclk_out_sel: 1;
				unsigned int reserve_1: 29;
			} bits;
			unsigned int u32;
		} sw_post_core_clk;
		struct { 
			unsigned int reserve_data[32];
		} reserve_reg_16_44;
		union post_dsp_bg_u { 
			struct post_dsp_bg_s { 
				unsigned int dsp_bg_green: 10;
				unsigned int dsp_bg_blue: 10;
				unsigned int dsp_bg_red: 10;
				unsigned int reserve_0: 1;
				unsigned int bg_display_en: 1;
			} bits;
			unsigned int u32;
		} sw_post_dsp_bg;
		union post_pre_scan_htiming_u { 
			struct post_pre_scan_htiming_s { 
				unsigned int pre_scan_hblank: 13;
				unsigned int reserve_0: 3;
				unsigned int pre_scan_hactive: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_post_pre_scan_htiming;
		union post_dsp_hact_info_u { 
			struct post_dsp_hact_info_s { 
				unsigned int dsp_hact_end_post: 13;
				unsigned int reserve_0: 3;
				unsigned int dsp_hact_st_post: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_post_dsp_hact_info;
		union post_dsp_vact_info_u { 
			struct post_dsp_vact_info_s { 
				unsigned int dsp_vact_end_post: 13;
				unsigned int reserve_0: 3;
				unsigned int dsp_vact_st_post: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_post_dsp_vact_info;
		union post_scl_factor_yrgb_u { 
			struct post_scl_factor_yrgb_s { 
				unsigned int post_hs_factor: 16;
				unsigned int post_vs_factor: 16;
			} bits;
			unsigned int u32;
		} sw_post_scl_factor_yrgb;
		union post_scl_ctrl_u { 
			struct post_scl_ctrl_s { 
				unsigned int post_hor_sd_en: 1;
				unsigned int post_ver_sd_en: 1;
				unsigned int reserve_0: 2;
				unsigned int post_vsd_dly_en: 1;
				unsigned int post_empty_cheating_en: 1;
				unsigned int reserve_1: 26;
			} bits;
			unsigned int u32;
		} sw_post_scl_ctrl;
		union post_dsp_vact_info_f1_u { 
			struct post_dsp_vact_info_f1_s { 
				unsigned int dsp_vact_end_post_f1: 13;
				unsigned int reserve_0: 3;
				unsigned int dsp_vact_st_post_f1: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_post_dsp_vact_info_f1;
		union post_dsp_htotal_hs_end_u { 
			struct post_dsp_htotal_hs_end_s { 
				unsigned int dsp_hs_end: 13;
				unsigned int reserve_0: 3;
				unsigned int dsp_htotal: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_post_dsp_htotal_hs_end;
		union post_dsp_hact_st_end_u { 
			struct post_dsp_hact_st_end_s { 
				unsigned int dsp_hact_end: 13;
				unsigned int reserve_0: 3;
				unsigned int dsp_hact_st: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_post_dsp_hact_st_end;
		union post_dsp_vtotal_vs_end_u { 
			struct post_dsp_vtotal_vs_end_s { 
				unsigned int dsp_vs_end: 13;
				unsigned int reserve_0: 2;
				unsigned int sw_dsp_vtotal_imd: 1;
				unsigned int dsp_vtotal: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_post_dsp_vtotal_vs_end;
		union post_dsp_vact_st_end_u { 
			struct post_dsp_vact_st_end_s { 
				unsigned int dsp_vact_end: 13;
				unsigned int reserve_0: 3;
				unsigned int dsp_vact_st: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_post_dsp_vact_st_end;
		union post_dsp_vs_st_end_f1_u { 
			struct post_dsp_vs_st_end_f1_s { 
				unsigned int dsp_vs_end_f1: 13;
				unsigned int reserve_0: 3;
				unsigned int dsp_vs_st_f1: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_post_dsp_vs_st_end_f1;
		union post_dsp_vact_st_end_f1_u { 
			struct post_dsp_vact_st_end_f1_s { 
				unsigned int dsp_vact_end_f1: 13;
				unsigned int reserve_0: 3;
				unsigned int dsp_vact_st_f1: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_post_dsp_vact_st_end_f1;
		union post_bcsh_ctrl_u { 
			struct post_bcsh_ctrl_s { 
				unsigned int bcsh_y2r_en: 1;
				unsigned int reserve_0: 1;
				unsigned int bcsh_y2r_csc_mode: 2;
				unsigned int bcsh_r2y_en: 1;
				unsigned int reserve_1: 1;
				unsigned int bcsh_r2y_csc_mode: 2;
				unsigned int reserve_2: 24;
			} bits;
			unsigned int u32;
		} sw_post_bcsh_ctrl;
		union post_bcsh_bcs_u { 
			struct post_bcsh_bcs_s { 
				unsigned int brightness: 8;
				unsigned int contrast: 9;
				unsigned int reserve_0: 3;
				unsigned int sat_con: 10;
				unsigned int out_mode: 2;
			} bits;
			unsigned int u32;
		} sw_post_bcsh_bcs;
		union post_bcsh_h_u { 
			struct post_bcsh_h_s { 
				unsigned int sin_hue: 9;
				unsigned int reserve_0: 7;
				unsigned int cos_hue: 9;
				unsigned int reserve_1: 7;
			} bits;
			unsigned int u32;
		} sw_post_bcsh_h;
		union post_bcsh_color_bar_u { 
			struct post_bcsh_color_bar_s { 
				unsigned int color_bar_y: 10;
				unsigned int color_bar_u: 10;
				unsigned int color_bar_v: 10;
				unsigned int reserve_0: 1;
				unsigned int bcsh_en: 1;
			} bits;
			unsigned int u32;
		} sw_post_bcsh_color_bar;
		struct { 
			unsigned int reserve_data[48];
		} reserve_reg_116_160;
		union post_frc_lower01_0_u { 
			struct post_frc_lower01_0_s { 
				unsigned int lower01_frm0: 16;
				unsigned int lower01_frm1: 16;
			} bits;
			unsigned int u32;
		} sw_post_frc_lower01_0;
		union post_frc_lower01_1_u { 
			struct post_frc_lower01_1_s { 
				unsigned int lower01_frm2: 16;
				unsigned int lower01_frm3: 16;
			} bits;
			unsigned int u32;
		} sw_post_frc_lower01_1;
		union post_frc_lower10_0_u { 
			struct post_frc_lower10_0_s { 
				unsigned int lower10_frm0: 16;
				unsigned int lower10_frm1: 16;
			} bits;
			unsigned int u32;
		} sw_post_frc_lower10_0;
		union post_frc_lower10_1_u { 
			struct post_frc_lower10_1_s { 
				unsigned int lower10_frm2: 16;
				unsigned int lower10_frm3: 16;
			} bits;
			unsigned int u32;
		} sw_post_frc_lower10_1;
		union post_frc_lower11_0_u { 
			struct post_frc_lower11_0_s { 
				unsigned int lower11_frm0: 16;
				unsigned int lower11_frm1: 16;
			} bits;
			unsigned int u32;
		} sw_post_frc_lower11_0;
		union post_frc_lower11_1_u { 
			struct post_frc_lower11_1_s { 
				unsigned int lower11_frm2: 16;
				unsigned int lower11_frm3: 16;
			} bits;
			unsigned int u32;
		} sw_post_frc_lower11_1;
		struct { 
			unsigned int reserve_data[60];
		} reserve_reg_188_244;
		union post_clk_cnt_u { 
			struct post_clk_cnt_s { 
				unsigned int calc_dclk_cnt: 15;
				unsigned int calc_clk_en: 1;
				unsigned int calc_aclk_cnt: 16;
			} bits;
			unsigned int u32;
		} sw_post_clk_cnt;
		union post_mcu_ctrl_u { 
			struct post_mcu_ctrl_s { 
				unsigned int mcu_pix_total: 6;
				unsigned int mcu_cs_pst: 4;
				unsigned int mcu_cs_pend: 6;
				unsigned int mcu_rw_pst: 4;
				unsigned int mcu_rw_pend: 6;
				unsigned int reserve_0: 1;
				unsigned int mcu_hold_mode: 1;
				unsigned int mcu_frm_st: 1;
				unsigned int mcu_rs: 1;
				unsigned int mcu_bypass_en: 1;
				unsigned int mcu_type_en: 1;
			} bits;
			unsigned int u32;
		} sw_post_mcu_ctrl;
	} regs;
	unsigned int p_reg_addr[29];
}post2_ctrl_0x27d00e00_t;

typedef union cluster0_0x27d01000_u {
	struct cluster0_0x27d01000_s {
		union win0_ctrl0_u { 
			struct win0_ctrl0_s { 
				unsigned int win0_en: 1;
				unsigned int win0_data_fmt: 6;
				unsigned int win0_tile_mode_sel: 1;
				unsigned int win0_csc_y2r_en: 1;
				unsigned int win0_csc_r2y_en: 1;
				unsigned int win0_csc_mode: 3;
				unsigned int reserve_0: 1;
				unsigned int win0_rb_swap: 1;
				unsigned int win0_alpha_swap: 1;
				unsigned int win0_rg_swap: 1;
				unsigned int win0_uv_swap: 1;
				unsigned int win0_dither_up_en: 1;
				unsigned int win0_yuv_clip: 1;
				unsigned int reserve_1: 1;
				unsigned int win0_y_mir: 1;
				unsigned int reserve_2: 2;
				unsigned int win0_csc_out_path_sel: 1;
				unsigned int reserve_3: 7;
			} bits;
			unsigned int u32;
		} sw_win0_ctrl0;
		union win0_ctrl1_u { 
			struct win0_ctrl1_s { 
				unsigned int win0_yrgb_axi_gather_en: 1;
				unsigned int reserve_0: 3;
				unsigned int win0_yrgb_gather_num: 4;
				unsigned int win0_cbcr_gather_num: 4;
				unsigned int win0_yscl_mode: 2;
				unsigned int win0_ysu_en: 1;
				unsigned int win0_ysd_en: 1;
				unsigned int reserve_1: 2;
				unsigned int win0_vsd_avg2: 1;
				unsigned int win0_vsd_avg4: 1;
				unsigned int win0_xscl_mode: 2;
				unsigned int win0_xsu_en: 1;
				unsigned int win0_xsd_en: 1;
				unsigned int win0_xgt_en: 1;
				unsigned int win0_xgt_mode: 2;
				unsigned int win0_xavg_en: 1;
				unsigned int win0_yrgb_vsd_gt2: 1;
				unsigned int win0_yrgb_vsd_gt4: 1;
				unsigned int win0_cbcr_vsd_gt2: 1;
				unsigned int win0_cbcr_vsd_gt4: 1;
			} bits;
			unsigned int u32;
		} sw_win0_ctrl1;
		union win0_ctrl2_u { 
			struct win0_ctrl2_s { 
				unsigned int win0_rid_yrgb: 4;
				unsigned int reserve_0: 1;
				unsigned int win0_rid_cbr: 4;
				unsigned int reserve_1: 23;
			} bits;
			unsigned int u32;
		} sw_win0_ctrl2;
		struct { 
			unsigned int reserve_data[8];
		} reserve_reg_12_16;
		union win0_yrgb_mst_u { 
			struct win0_yrgb_mst_s { 
				unsigned int win0_yrgb_mst: 32;
			} bits;
			unsigned int u32;
		} sw_win0_yrgb_mst;
		union win0_cbcr_mst_u { 
			struct win0_cbcr_mst_s { 
				unsigned int win0_cbcr_mst: 32;
			} bits;
			unsigned int u32;
		} sw_win0_cbcr_mst;
		union win0_vir_u { 
			struct win0_vir_s { 
				unsigned int win0_vir_stride: 16;
				unsigned int reserve_0: 16;
			} bits;
			unsigned int u32;
		} sw_win0_vir;
		union win0_key_color_u { 
			struct win0_key_color_s { 
				unsigned int win0_key_color_bv: 10;
				unsigned int win0_key_color_gu: 10;
				unsigned int win0_key_color_ry: 10;
				unsigned int win0_key_color_en: 1;
				unsigned int reserve_0: 1;
			} bits;
			unsigned int u32;
		} sw_win0_key_color;
		union win0_act_info_u { 
			struct win0_act_info_s { 
				unsigned int win0_act_width: 13;
				unsigned int reserve_0: 3;
				unsigned int win0_act_height: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_win0_act_info;
		union win0_dsp_info_u { 
			struct win0_dsp_info_s { 
				unsigned int win0_dsp_width: 12;
				unsigned int reserve_0: 4;
				unsigned int win0_dsp_height: 12;
				unsigned int reserve_1: 4;
			} bits;
			unsigned int u32;
		} sw_win0_dsp_info;
		union win0_dsp_st_u { 
			struct win0_dsp_st_s { 
				unsigned int win0_dsp_xst: 13;
				unsigned int reserve_0: 3;
				unsigned int win0_dsp_yst: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_win0_dsp_st;
		union win0_dsp_bg_u { 
			struct win0_dsp_bg_s { 
				unsigned int win0_dsp_bg_blue: 10;
				unsigned int win0_dsp_bg_green: 10;
				unsigned int win0_dsp_bg_red: 10;
				unsigned int reserve_0: 1;
				unsigned int win0_bg_en: 1;
			} bits;
			unsigned int u32;
		} sw_win0_dsp_bg;
		union win0_scl_factor_yrgb_u { 
			struct win0_scl_factor_yrgb_s { 
				unsigned int win0_hs_factor_yrgb: 16;
				unsigned int win0_vs_factor_yrgb: 16;
			} bits;
			unsigned int u32;
		} sw_win0_scl_factor_yrgb;
		union win0_scl_offset_u { 
			struct win0_scl_offset_s { 
				unsigned int win0_hs_offset_yrgb: 8;
				unsigned int reserve_0: 8;
				unsigned int win0_vs_offset_yrgb: 8;
				unsigned int reserve_1: 8;
			} bits;
			unsigned int u32;
		} sw_win0_scl_offset;
		union win0_transformed_offset_u { 
			struct win0_transformed_offset_s { 
				unsigned int transformed_xoffset: 4;
				unsigned int reserve_0: 12;
				unsigned int transformed_yoffset: 4;
				unsigned int reserve_1: 12;
			} bits;
			unsigned int u32;
		} sw_win0_transformed_offset;
		union win0_zme_ctrl_u { 
			struct win0_zme_ctrl_s { 
				unsigned int reserve_0: 3;
				unsigned int win0_zme_dering_en: 1;
				unsigned int reserve_1: 27;
				unsigned int win0_zme_gating_en: 1;
			} bits;
			unsigned int u32;
		} sw_win0_zme_ctrl;
		union win0_zme_dering_para_u { 
			struct win0_zme_dering_para_s { 
				unsigned int win0_dering_alpha: 5;
				unsigned int reserve_0: 3;
				unsigned int win0_dering_beta: 5;
				unsigned int reserve_1: 3;
				unsigned int win0_dering_sen0: 5;
				unsigned int reserve_2: 3;
				unsigned int win0_dering_sen1: 5;
				unsigned int reserve_3: 3;
			} bits;
			unsigned int u32;
		} sw_win0_zme_dering_para;
		struct { 
			unsigned int reserve_data[12];
		} reserve_reg_72_80;
		union win0_fbcd_output_ctrl_u { 
			struct win0_fbcd_output_ctrl_s { 
				unsigned int reserve_0: 4;
				unsigned int win0_fbcd_gating_en: 1;
				unsigned int reserve_1: 27;
			} bits;
			unsigned int u32;
		} sw_win0_fbcd_output_ctrl;
		union win0_fbcd_mode_u { 
			struct win0_fbcd_mode_s { 
				unsigned int reserve_0: 2;
				unsigned int win0_xmir_en: 1;
				unsigned int win0_ymir_en: 1;
				unsigned int reserve_1: 28;
			} bits;
			unsigned int u32;
		} sw_win0_fbcd_mode;
		union win0_fbcd_hdr_ptr_u { 
			struct win0_fbcd_hdr_ptr_s { 
				unsigned int win0_fbcd_hdr_ptr: 32;
			} bits;
			unsigned int u32;
		} sw_win0_fbcd_hdr_ptr;
		union win0_fbcd_vir_width_u { 
			struct win0_fbcd_vir_width_s { 
				unsigned int win0_fbcd_pic_vir_width: 16;
				unsigned int win0_fbcd_tail_num: 16;
			} bits;
			unsigned int u32;
		} sw_win0_fbcd_vir_width;
		union win0_fbcd_size_u { 
			struct win0_fbcd_size_s { 
				unsigned int win0_fbcd_pic_width: 16;
				unsigned int win0_fbcd_pic_height: 16;
			} bits;
			unsigned int u32;
		} sw_win0_fbcd_size;
		union win0_fbcd_pic_offset_u { 
			struct win0_fbcd_pic_offset_s { 
				unsigned int win0_fbcd_pic_xoffset: 16;
				unsigned int win0_fbcd_pic_yoffset: 16;
			} bits;
			unsigned int u32;
		} sw_win0_fbcd_pic_offset;
		union win0_fbcd_dis_offset_u { 
			struct win0_fbcd_dis_offset_s { 
				unsigned int win0_fbcd_dis_xoffset: 16;
				unsigned int win0_fbcd_dis_yoffset: 16;
			} bits;
			unsigned int u32;
		} sw_win0_fbcd_dis_offset;
		union win0_fbcd_ctrl_u { 
			struct win0_fbcd_ctrl_s { 
				unsigned int reserve_0: 2;
				unsigned int win0_fbcd_pixel_packing_fmt: 5;
				unsigned int win0_fbcd_half_block: 1;
				unsigned int win0_fbcd_block_split: 1;
				unsigned int win0_fbcd_rb_swap_en: 1;
				unsigned int win0_fbcd_uv_swap_en: 1;
				unsigned int win0_fbcd_alpha_swap_en: 1;
				unsigned int win0_fbcd_bg_swap_en: 1;
				unsigned int reserve_1: 3;
				unsigned int win0_fbcd_pld_offset_en: 1;
				unsigned int win0_fbcd_pld_range_en: 1;
				unsigned int reserve_2: 14;
			} bits;
			unsigned int u32;
		} sw_win0_fbcd_ctrl;
		struct { 
			unsigned int reserve_data[8];
		} reserve_reg_116_120;
		union win0_pld_ptr_offset_u { 
			struct win0_pld_ptr_offset_s { 
				unsigned int win0_pld_ptr_offset: 32;
			} bits;
			unsigned int u32;
		} sw_win0_pld_ptr_offset;
		union win0_pld_ptr_range_u { 
			struct win0_pld_ptr_range_s { 
				unsigned int win0_pld_ptr_range: 32;
			} bits;
			unsigned int u32;
		} sw_win0_pld_ptr_range;
		union win1_ctrl0_u { 
			struct win1_ctrl0_s { 
				unsigned int win1_en: 1;
				unsigned int win1_data_fmt: 6;
				unsigned int reserve_0: 1;
				unsigned int win1_csc_y2r_en: 1;
				unsigned int win1_csc_r2y_en: 1;
				unsigned int win1_csc_mode: 2;
				unsigned int reserve_1: 2;
				unsigned int win1_rb_swap: 1;
				unsigned int win1_alpha_swap: 1;
				unsigned int win1_rg_swap: 1;
				unsigned int win1_uv_swap: 1;
				unsigned int win1_dither_up_en: 1;
				unsigned int win1_yuv_clip: 1;
				unsigned int win1_y_mir: 1;
				unsigned int reserve_2: 3;
				unsigned int win1_csc_out_path_sel: 1;
				unsigned int reserve_3: 7;
			} bits;
			unsigned int u32;
		} sw_win1_ctrl0;
		union win1_ctrl1_u { 
			struct win1_ctrl1_s { 
				unsigned int win1_yrgb_axi_gather_en: 1;
				unsigned int reserve_0: 3;
				unsigned int win1_yrgb_gather_num: 4;
				unsigned int win1_cbcr_gather_num: 4;
				unsigned int win1_yscl_mode: 2;
				unsigned int win1_ysu_en: 1;
				unsigned int win1_ysd_en: 1;
				unsigned int reserve_1: 2;
				unsigned int win1_vsd_avg2: 1;
				unsigned int win1_vsd_avg4: 1;
				unsigned int win1_xscl_mode: 2;
				unsigned int win1_xsu_en: 1;
				unsigned int win1_xsd_en: 1;
				unsigned int win1_xgt_en: 1;
				unsigned int win1_xgt_mode: 2;
				unsigned int win1_xavg_en: 1;
				unsigned int win1_yrgb_vsd_gt2: 1;
				unsigned int win1_yrgb_vsd_gt4: 1;
				unsigned int win1_cbcr_vsd_gt2: 1;
				unsigned int win1_cbcr_vsd_gt4: 1;
			} bits;
			unsigned int u32;
		} sw_win1_ctrl1;
		union win1_ctrl2_u { 
			struct win1_ctrl2_s { 
				unsigned int win1_rid_yrgb: 4;
				unsigned int reserve_0: 1;
				unsigned int win1_rid_cbr: 4;
				unsigned int reserve_1: 23;
			} bits;
			unsigned int u32;
		} sw_win1_ctrl2;
		union win1_yrgb_mst_u { 
			struct win1_yrgb_mst_s { 
				unsigned int win1_yrgb_mst: 32;
			} bits;
			unsigned int u32;
		} sw_win1_yrgb_mst;
		union win1_cbcr_mst_u { 
			struct win1_cbcr_mst_s { 
				unsigned int win1_cbcr_mst: 32;
			} bits;
			unsigned int u32;
		} sw_win1_cbcr_mst;
		union win1_vir_u { 
			struct win1_vir_s { 
				unsigned int win1_vir_stride: 16;
				unsigned int reserve_0: 16;
			} bits;
			unsigned int u32;
		} sw_win1_vir;
		union win1_key_color_u { 
			struct win1_key_color_s { 
				unsigned int win1_key_color_bv: 10;
				unsigned int win1_key_color_gu: 10;
				unsigned int win1_key_color_ry: 10;
				unsigned int win1_key_color_en: 1;
				unsigned int reserve_0: 1;
			} bits;
			unsigned int u32;
		} sw_win1_key_color;
		union win1_act_info_u { 
			struct win1_act_info_s { 
				unsigned int win1_act_width: 13;
				unsigned int reserve_0: 3;
				unsigned int win1_act_height: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_win1_act_info;
		union win1_dsp_info_u { 
			struct win1_dsp_info_s { 
				unsigned int win1_dsp_width: 12;
				unsigned int reserve_0: 4;
				unsigned int win1_dsp_height: 12;
				unsigned int reserve_1: 4;
			} bits;
			unsigned int u32;
		} sw_win1_dsp_info;
		union win1_dsp_st_u { 
			struct win1_dsp_st_s { 
				unsigned int win1_dsp_xst: 13;
				unsigned int reserve_0: 3;
				unsigned int win1_dsp_yst: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_win1_dsp_st;
		union win1_dsp_bg_u { 
			struct win1_dsp_bg_s { 
				unsigned int win1_dsp_bg_blue: 10;
				unsigned int win1_dsp_bg_green: 10;
				unsigned int win1_dsp_bg_red: 10;
				unsigned int reserve_0: 1;
				unsigned int win1_bg_en: 1;
			} bits;
			unsigned int u32;
		} sw_win1_dsp_bg;
		union win1_scl_factor_yrgb_u { 
			struct win1_scl_factor_yrgb_s { 
				unsigned int win1_hs_factor_yrgb: 16;
				unsigned int win1_vs_factor_yrgb: 16;
			} bits;
			unsigned int u32;
		} sw_win1_scl_factor_yrgb;
		struct { 
			unsigned int reserve_data[8];
		} reserve_reg_180_184;
		union win1_scl_offset_u { 
			struct win1_scl_offset_s { 
				unsigned int win1_hs_offset_yrgb: 8;
				unsigned int reserve_0: 8;
				unsigned int win1_vs_offset_yrgb: 8;
				unsigned int reserve_1: 8;
			} bits;
			unsigned int u32;
		} sw_win1_scl_offset;
		union win1_transformed_offset_u { 
			struct win1_transformed_offset_s { 
				unsigned int transformed_xoffset: 4;
				unsigned int reserve_0: 12;
				unsigned int transformed_yoffset: 4;
				unsigned int reserve_1: 12;
			} bits;
			unsigned int u32;
		} sw_win1_transformed_offset;
		union win1_zme_ctrl_u { 
			struct win1_zme_ctrl_s { 
				unsigned int reserve_0: 3;
				unsigned int win1_zme_dering_en: 1;
				unsigned int reserve_1: 27;
				unsigned int win1_zme_gating_en: 1;
			} bits;
			unsigned int u32;
		} sw_win1_zme_ctrl;
		union win1_zme_dering_para_u { 
			struct win1_zme_dering_para_s { 
				unsigned int win1_dering_alpha: 5;
				unsigned int reserve_0: 3;
				unsigned int win1_dering_beta: 5;
				unsigned int reserve_1: 3;
				unsigned int win1_dering_sen0: 5;
				unsigned int reserve_2: 3;
				unsigned int win1_dering_sen1: 5;
				unsigned int reserve_3: 3;
			} bits;
			unsigned int u32;
		} sw_win1_zme_dering_para;
		struct { 
			unsigned int reserve_data[8];
		} reserve_reg_204_208;
		union win1_fbcd_mask_en_u { 
			struct win1_fbcd_mask_en_s { 
				unsigned int reserve_0: 4;
				unsigned int win1_fbcd_gating_en: 1;
				unsigned int reserve_1: 27;
			} bits;
			unsigned int u32;
		} sw_win1_fbcd_mask_en;
		union win1_fbcd_mode_u { 
			struct win1_fbcd_mode_s { 
				unsigned int reserve_0: 2;
				unsigned int win1_xmir_en: 1;
				unsigned int win1_ymir_en: 1;
				unsigned int reserve_1: 28;
			} bits;
			unsigned int u32;
		} sw_win1_fbcd_mode;
		union win1_fbcd_hdr_ptr_u { 
			struct win1_fbcd_hdr_ptr_s { 
				unsigned int win1_fbcd_hdr_ptr: 32;
			} bits;
			unsigned int u32;
		} sw_win1_fbcd_hdr_ptr;
		union win1_fbcd_vir_width_u { 
			struct win1_fbcd_vir_width_s { 
				unsigned int win1_fbcd_pic_vir_width: 16;
				unsigned int win1_fbcd_tail_num: 16;
			} bits;
			unsigned int u32;
		} sw_win1_fbcd_vir_width;
		union win1_fbcd_size_u { 
			struct win1_fbcd_size_s { 
				unsigned int win1_fbcd_pic_width: 16;
				unsigned int win1_fbcd_pic_height: 16;
			} bits;
			unsigned int u32;
		} sw_win1_fbcd_size;
		union win1_fbcd_pic_offset_u { 
			struct win1_fbcd_pic_offset_s { 
				unsigned int win1_fbcd_pic_xoffset: 16;
				unsigned int win1_fbcd_pic_yoffset: 16;
			} bits;
			unsigned int u32;
		} sw_win1_fbcd_pic_offset;
		union win1_fbcd_dis_offset_u { 
			struct win1_fbcd_dis_offset_s { 
				unsigned int win1_fbcd_dis_xoffset: 16;
				unsigned int win1_fbcd_dis_yoffset: 16;
			} bits;
			unsigned int u32;
		} sw_win1_fbcd_dis_offset;
		union win1_fbcd_ctrl_u { 
			struct win1_fbcd_ctrl_s { 
				unsigned int reserve_0: 2;
				unsigned int win1_fbcd_pixel_packing_fmt: 5;
				unsigned int win1_fbcd_half_block: 1;
				unsigned int win1_fbcd_block_split: 1;
				unsigned int win1_fbcd_rb_swap_en: 1;
				unsigned int win1_fbcd_uv_swap_en: 1;
				unsigned int reserve_1: 5;
				unsigned int win1_fbcd_pld_offset_en: 1;
				unsigned int win1_fbcd_pld_range_en: 1;
				unsigned int reserve_2: 14;
			} bits;
			unsigned int u32;
		} sw_win1_fbcd_ctrl;
		struct { 
			unsigned int reserve_data[8];
		} reserve_reg_244_248;
		union win1_pld_ptr_offset_u { 
			struct win1_pld_ptr_offset_s { 
				unsigned int win1_pld_ptr_offset: 32;
			} bits;
			unsigned int u32;
		} sw_win1_pld_ptr_offset;
		union win1_pld_ptr_range_u { 
			struct win1_pld_ptr_range_s { 
				unsigned int win1_pld_ptr_range: 32;
			} bits;
			unsigned int u32;
		} sw_win1_pld_ptr_range;
		union cluster_ctrl_u { 
			struct cluster_ctrl_s { 
				unsigned int cluster_en: 1;
				unsigned int cluster_fbcd_en: 1;
				unsigned int reserve_0: 2;
				unsigned int cluster_lb_mode: 2;
				unsigned int reserve_1: 6;
				unsigned int cluster_dma_stop: 1;
				unsigned int reserve_2: 1;
				unsigned int cluster_mmu_bypass: 1;
				unsigned int reserve_3: 1;
				unsigned int cluster_dma_hurry_en: 1;
				unsigned int cluster_dma_hurry_thold: 2;
				unsigned int reserve_4: 8;
				unsigned int cluster_pld_dma_priority_en: 1;
				unsigned int cluster_fbcd_overlap_en: 1;
				unsigned int clusrer_fbcd_st_alige_en: 1;
				unsigned int reserve_5: 1;
				unsigned int cluster_frm_resetn_en: 1;
			} bits;
			unsigned int u32;
		} sw_cluster_ctrl;
		union dci_blk_size_u { 
			struct dci_blk_size_s { 
				unsigned int blk_size_h: 9;
				unsigned int reserve_0: 7;
				unsigned int blk_size_v: 9;
				unsigned int reserve_1: 7;
			} bits;
			unsigned int u32;
		} sw_dci_blk_size;
		union dci_blk_offset_u { 
			struct dci_blk_offset_s { 
				unsigned int blk_offset_h: 9;
				unsigned int reserve_0: 7;
				unsigned int blk_offset_v: 9;
				unsigned int reserve_1: 7;
			} bits;
			unsigned int u32;
		} sw_dci_blk_offset;
		union dci_pix_region_u { 
			struct dci_pix_region_s { 
				unsigned int blk_size_fix: 20;
				unsigned int pix_region_start_h: 5;
				unsigned int reserve_0: 1;
				unsigned int pix_region_start_v: 5;
				unsigned int reserve_1: 1;
			} bits;
			unsigned int u32;
		} sw_dci_pix_region;
		union dci_luma_sat_adj_0_u { 
			struct dci_luma_sat_adj_0_s { 
				unsigned int sat_adj_zero: 16;
				unsigned int sat_adj_thr: 16;
			} bits;
			unsigned int u32;
		} sw_dci_luma_sat_adj_0;
		union dci_luma_sat_adj_1_u { 
			struct dci_luma_sat_adj_1_s { 
				unsigned int sat_adj_k: 16;
				unsigned int sat_w: 7;
				unsigned int reserve_0: 9;
			} bits;
			unsigned int u32;
		} sw_dci_luma_sat_adj_1;
		union dci_ctrl_u { 
			struct dci_ctrl_s { 
				unsigned int dci_en: 1;
				unsigned int uv_adjust_en: 1;
				unsigned int csc_range: 1;
				unsigned int reserve_0: 1;
				unsigned int dma_rid: 5;
				unsigned int reserve_1: 3;
				unsigned int dma_rlen: 2;
				unsigned int reserve_2: 18;
			} bits;
			unsigned int u32;
		} sw_dci_ctrl;
		union dci_lut_mst_u { 
			struct dci_lut_mst_s { 
				unsigned int dci_dma_mst: 32;
			} bits;
			unsigned int u32;
		} sw_dci_lut_mst;
		union dci_dbg_ctrl_u { 
			struct dci_dbg_ctrl_s { 
				unsigned int debug_point_h: 13;
				unsigned int reserve_0: 3;
				unsigned int debug_point_v: 13;
				unsigned int reserve_1: 1;
				unsigned int debug_mode: 1;
				unsigned int debug_en: 1;
			} bits;
			unsigned int u32;
		} sw_dci_dbg_ctrl;
		struct { 
			unsigned int reserve_data[12];
		} reserve_reg_296_304;
		union dci_dbg_pix_u { 
			struct dci_dbg_pix_s { 
				unsigned int dci_debug_pix: 32;
			} bits;
			unsigned int u32;
		} sw_dci_dbg_pix;
		struct { 
			unsigned int reserve_data[192];
		} reserve_reg_312_500;
		union cluster_port_sel_imd_u { 
			struct cluster_port_sel_imd_s { 
				unsigned int cluster_port_sel: 2;
				unsigned int reserve_0: 30;
			} bits;
			unsigned int u32;
		} sw_cluster_port_sel_imd;
		union cluster_dly_num_u { 
			struct cluster_dly_num_s { 
				unsigned int win0_dly_num: 8;
				unsigned int win1_dly_num: 8;
				unsigned int reserve_0: 16;
			} bits;
			unsigned int u32;
		} sw_cluster_dly_num;
	} regs;
	unsigned int p_reg_addr[64];
}cluster0_0x27d01000_t;

typedef union cluster1_0x27d01200_u {
	struct cluster1_0x27d01200_s {
		union win0_ctrl0_u { 
			struct win0_ctrl0_s { 
				unsigned int win0_en: 1;
				unsigned int win0_data_fmt: 6;
				unsigned int win0_tile_mode_sel: 1;
				unsigned int win0_csc_y2r_en: 1;
				unsigned int win0_csc_r2y_en: 1;
				unsigned int win0_csc_mode: 3;
				unsigned int reserve_0: 1;
				unsigned int win0_rb_swap: 1;
				unsigned int win0_alpha_swap: 1;
				unsigned int win0_rg_swap: 1;
				unsigned int win0_uv_swap: 1;
				unsigned int win0_dither_up_en: 1;
				unsigned int win0_yuv_clip: 1;
				unsigned int reserve_1: 1;
				unsigned int win0_y_mir: 1;
				unsigned int reserve_2: 2;
				unsigned int win0_csc_out_path_sel: 1;
				unsigned int reserve_3: 7;
			} bits;
			unsigned int u32;
		} sw_win0_ctrl0;
		union win0_ctrl1_u { 
			struct win0_ctrl1_s { 
				unsigned int win0_yrgb_axi_gather_en: 1;
				unsigned int reserve_0: 3;
				unsigned int win0_yrgb_gather_num: 4;
				unsigned int win0_cbcr_gather_num: 4;
				unsigned int win0_yscl_mode: 2;
				unsigned int win0_ysu_en: 1;
				unsigned int win0_ysd_en: 1;
				unsigned int reserve_1: 2;
				unsigned int win0_vsd_avg2: 1;
				unsigned int win0_vsd_avg4: 1;
				unsigned int win0_xscl_mode: 2;
				unsigned int win0_xsu_en: 1;
				unsigned int win0_xsd_en: 1;
				unsigned int win0_xgt_en: 1;
				unsigned int win0_xgt_mode: 2;
				unsigned int win0_xavg_en: 1;
				unsigned int win0_yrgb_vsd_gt2: 1;
				unsigned int win0_yrgb_vsd_gt4: 1;
				unsigned int win0_cbcr_vsd_gt2: 1;
				unsigned int win0_cbcr_vsd_gt4: 1;
			} bits;
			unsigned int u32;
		} sw_win0_ctrl1;
		union win0_ctrl2_u { 
			struct win0_ctrl2_s { 
				unsigned int win0_rid_yrgb: 4;
				unsigned int reserve_0: 1;
				unsigned int win0_rid_cbr: 4;
				unsigned int reserve_1: 23;
			} bits;
			unsigned int u32;
		} sw_win0_ctrl2;
		struct { 
			unsigned int reserve_data[8];
		} reserve_reg_12_16;
		union win0_yrgb_mst_u { 
			struct win0_yrgb_mst_s { 
				unsigned int win0_yrgb_mst: 32;
			} bits;
			unsigned int u32;
		} sw_win0_yrgb_mst;
		union win0_cbcr_mst_u { 
			struct win0_cbcr_mst_s { 
				unsigned int win0_cbcr_mst: 32;
			} bits;
			unsigned int u32;
		} sw_win0_cbcr_mst;
		union win0_vir_u { 
			struct win0_vir_s { 
				unsigned int win0_vir_stride: 16;
				unsigned int reserve_0: 16;
			} bits;
			unsigned int u32;
		} sw_win0_vir;
		union win0_key_color_u { 
			struct win0_key_color_s { 
				unsigned int win0_key_color_bv: 10;
				unsigned int win0_key_color_gu: 10;
				unsigned int win0_key_color_ry: 10;
				unsigned int win0_key_color_en: 1;
				unsigned int reserve_0: 1;
			} bits;
			unsigned int u32;
		} sw_win0_key_color;
		union win0_act_info_u { 
			struct win0_act_info_s { 
				unsigned int win0_act_width: 13;
				unsigned int reserve_0: 3;
				unsigned int win0_act_height: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_win0_act_info;
		union win0_dsp_info_u { 
			struct win0_dsp_info_s { 
				unsigned int win0_dsp_width: 12;
				unsigned int reserve_0: 4;
				unsigned int win0_dsp_height: 12;
				unsigned int reserve_1: 4;
			} bits;
			unsigned int u32;
		} sw_win0_dsp_info;
		union win0_dsp_st_u { 
			struct win0_dsp_st_s { 
				unsigned int win0_dsp_xst: 13;
				unsigned int reserve_0: 3;
				unsigned int win0_dsp_yst: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_win0_dsp_st;
		union win0_dsp_bg_u { 
			struct win0_dsp_bg_s { 
				unsigned int win0_dsp_bg_blue: 10;
				unsigned int win0_dsp_bg_green: 10;
				unsigned int win0_dsp_bg_red: 10;
				unsigned int reserve_0: 1;
				unsigned int win0_bg_en: 1;
			} bits;
			unsigned int u32;
		} sw_win0_dsp_bg;
		union win0_scl_factor_yrgb_u { 
			struct win0_scl_factor_yrgb_s { 
				unsigned int win0_hs_factor_yrgb: 16;
				unsigned int win0_vs_factor_yrgb: 16;
			} bits;
			unsigned int u32;
		} sw_win0_scl_factor_yrgb;
		union win0_scl_offset_u { 
			struct win0_scl_offset_s { 
				unsigned int win0_hs_offset_yrgb: 8;
				unsigned int reserve_0: 8;
				unsigned int win0_vs_offset_yrgb: 8;
				unsigned int reserve_1: 8;
			} bits;
			unsigned int u32;
		} sw_win0_scl_offset;
		union win0_transformed_offset_u { 
			struct win0_transformed_offset_s { 
				unsigned int transformed_xoffset: 4;
				unsigned int reserve_0: 12;
				unsigned int transformed_yoffset: 4;
				unsigned int reserve_1: 12;
			} bits;
			unsigned int u32;
		} sw_win0_transformed_offset;
		union win0_zme_ctrl_u { 
			struct win0_zme_ctrl_s { 
				unsigned int reserve_0: 3;
				unsigned int win0_zme_dering_en: 1;
				unsigned int reserve_1: 27;
				unsigned int win0_zme_gating_en: 1;
			} bits;
			unsigned int u32;
		} sw_win0_zme_ctrl;
		union win0_zme_dering_para_u { 
			struct win0_zme_dering_para_s { 
				unsigned int win0_dering_alpha: 5;
				unsigned int reserve_0: 3;
				unsigned int win0_dering_beta: 5;
				unsigned int reserve_1: 3;
				unsigned int win0_dering_sen0: 5;
				unsigned int reserve_2: 3;
				unsigned int win0_dering_sen1: 5;
				unsigned int reserve_3: 3;
			} bits;
			unsigned int u32;
		} sw_win0_zme_dering_para;
		struct { 
			unsigned int reserve_data[12];
		} reserve_reg_72_80;
		union win0_fbcd_output_ctrl_u { 
			struct win0_fbcd_output_ctrl_s { 
				unsigned int reserve_0: 4;
				unsigned int win0_fbcd_gating_en: 1;
				unsigned int reserve_1: 27;
			} bits;
			unsigned int u32;
		} sw_win0_fbcd_output_ctrl;
		union win0_fbcd_mode_u { 
			struct win0_fbcd_mode_s { 
				unsigned int reserve_0: 2;
				unsigned int win0_xmir_en: 1;
				unsigned int win0_ymir_en: 1;
				unsigned int reserve_1: 28;
			} bits;
			unsigned int u32;
		} sw_win0_fbcd_mode;
		union win0_fbcd_hdr_ptr_u { 
			struct win0_fbcd_hdr_ptr_s { 
				unsigned int win0_fbcd_hdr_ptr: 32;
			} bits;
			unsigned int u32;
		} sw_win0_fbcd_hdr_ptr;
		union win0_fbcd_vir_width_u { 
			struct win0_fbcd_vir_width_s { 
				unsigned int win0_fbcd_pic_vir_width: 16;
				unsigned int win0_fbcd_tail_num: 16;
			} bits;
			unsigned int u32;
		} sw_win0_fbcd_vir_width;
		union win0_fbcd_size_u { 
			struct win0_fbcd_size_s { 
				unsigned int win0_fbcd_pic_width: 16;
				unsigned int win0_fbcd_pic_height: 16;
			} bits;
			unsigned int u32;
		} sw_win0_fbcd_size;
		union win0_fbcd_pic_offset_u { 
			struct win0_fbcd_pic_offset_s { 
				unsigned int win0_fbcd_pic_xoffset: 16;
				unsigned int win0_fbcd_pic_yoffset: 16;
			} bits;
			unsigned int u32;
		} sw_win0_fbcd_pic_offset;
		union win0_fbcd_dis_offset_u { 
			struct win0_fbcd_dis_offset_s { 
				unsigned int win0_fbcd_dis_xoffset: 16;
				unsigned int win0_fbcd_dis_yoffset: 16;
			} bits;
			unsigned int u32;
		} sw_win0_fbcd_dis_offset;
		union win0_fbcd_ctrl_u { 
			struct win0_fbcd_ctrl_s { 
				unsigned int reserve_0: 2;
				unsigned int win0_fbcd_pixel_packing_fmt: 5;
				unsigned int win0_fbcd_half_block: 1;
				unsigned int win0_fbcd_block_split: 1;
				unsigned int win0_fbcd_rb_swap_en: 1;
				unsigned int win0_fbcd_uv_swap_en: 1;
				unsigned int win0_fbcd_alpha_swap_en: 1;
				unsigned int win0_fbcd_bg_swap_en: 1;
				unsigned int reserve_1: 3;
				unsigned int win0_fbcd_pld_offset_en: 1;
				unsigned int win0_fbcd_pld_range_en: 1;
				unsigned int reserve_2: 14;
			} bits;
			unsigned int u32;
		} sw_win0_fbcd_ctrl;
		struct { 
			unsigned int reserve_data[8];
		} reserve_reg_116_120;
		union win0_pld_ptr_offset_u { 
			struct win0_pld_ptr_offset_s { 
				unsigned int win0_pld_ptr_offset: 32;
			} bits;
			unsigned int u32;
		} sw_win0_pld_ptr_offset;
		union win0_pld_ptr_range_u { 
			struct win0_pld_ptr_range_s { 
				unsigned int win0_pld_ptr_range: 32;
			} bits;
			unsigned int u32;
		} sw_win0_pld_ptr_range;
		union win1_ctrl0_u { 
			struct win1_ctrl0_s { 
				unsigned int win1_en: 1;
				unsigned int win1_data_fmt: 6;
				unsigned int reserve_0: 1;
				unsigned int win1_csc_y2r_en: 1;
				unsigned int win1_csc_r2y_en: 1;
				unsigned int win1_csc_mode: 2;
				unsigned int reserve_1: 2;
				unsigned int win1_rb_swap: 1;
				unsigned int win1_alpha_swap: 1;
				unsigned int win1_rg_swap: 1;
				unsigned int win1_uv_swap: 1;
				unsigned int win1_dither_up_en: 1;
				unsigned int win1_yuv_clip: 1;
				unsigned int win1_y_mir: 1;
				unsigned int reserve_2: 3;
				unsigned int win1_csc_out_path_sel: 1;
				unsigned int reserve_3: 7;
			} bits;
			unsigned int u32;
		} sw_win1_ctrl0;
		union win1_ctrl1_u { 
			struct win1_ctrl1_s { 
				unsigned int win1_yrgb_axi_gather_en: 1;
				unsigned int reserve_0: 3;
				unsigned int win1_yrgb_gather_num: 4;
				unsigned int win1_cbcr_gather_num: 4;
				unsigned int win1_yscl_mode: 2;
				unsigned int win1_ysu_en: 1;
				unsigned int win1_ysd_en: 1;
				unsigned int reserve_1: 2;
				unsigned int win1_vsd_avg2: 1;
				unsigned int win1_vsd_avg4: 1;
				unsigned int win1_xscl_mode: 2;
				unsigned int win1_xsu_en: 1;
				unsigned int win1_xsd_en: 1;
				unsigned int win1_xgt_en: 1;
				unsigned int win1_xgt_mode: 2;
				unsigned int win1_xavg_en: 1;
				unsigned int win1_yrgb_vsd_gt2: 1;
				unsigned int win1_yrgb_vsd_gt4: 1;
				unsigned int win1_cbcr_vsd_gt2: 1;
				unsigned int win1_cbcr_vsd_gt4: 1;
			} bits;
			unsigned int u32;
		} sw_win1_ctrl1;
		union win1_ctrl2_u { 
			struct win1_ctrl2_s { 
				unsigned int win1_rid_yrgb: 4;
				unsigned int reserve_0: 1;
				unsigned int win1_rid_cbr: 4;
				unsigned int reserve_1: 23;
			} bits;
			unsigned int u32;
		} sw_win1_ctrl2;
		union win1_yrgb_mst_u { 
			struct win1_yrgb_mst_s { 
				unsigned int win1_yrgb_mst: 32;
			} bits;
			unsigned int u32;
		} sw_win1_yrgb_mst;
		union win1_cbcr_mst_u { 
			struct win1_cbcr_mst_s { 
				unsigned int win1_cbcr_mst: 32;
			} bits;
			unsigned int u32;
		} sw_win1_cbcr_mst;
		union win1_vir_u { 
			struct win1_vir_s { 
				unsigned int win1_vir_stride: 16;
				unsigned int reserve_0: 16;
			} bits;
			unsigned int u32;
		} sw_win1_vir;
		struct { 
			unsigned int reserve_data[8];
		} reserve_reg_156_160;
		union win1_act_info_u { 
			struct win1_act_info_s { 
				unsigned int win1_act_width: 13;
				unsigned int reserve_0: 3;
				unsigned int win1_act_height: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_win1_act_info;
		union win1_dsp_info_u { 
			struct win1_dsp_info_s { 
				unsigned int win1_dsp_width: 12;
				unsigned int reserve_0: 4;
				unsigned int win1_dsp_height: 12;
				unsigned int reserve_1: 4;
			} bits;
			unsigned int u32;
		} sw_win1_dsp_info;
		union win1_dsp_st_u { 
			struct win1_dsp_st_s { 
				unsigned int win1_dsp_xst: 13;
				unsigned int reserve_0: 3;
				unsigned int win1_dsp_yst: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_win1_dsp_st;
		union win1_dsp_bg_u { 
			struct win1_dsp_bg_s { 
				unsigned int win1_dsp_bg_blue: 10;
				unsigned int win1_dsp_bg_green: 10;
				unsigned int win1_dsp_bg_red: 10;
				unsigned int reserve_0: 1;
				unsigned int win1_bg_en: 1;
			} bits;
			unsigned int u32;
		} sw_win1_dsp_bg;
		union win1_scl_factor_yrgb_u { 
			struct win1_scl_factor_yrgb_s { 
				unsigned int win1_hs_factor_yrgb: 16;
				unsigned int win1_vs_factor_yrgb: 16;
			} bits;
			unsigned int u32;
		} sw_win1_scl_factor_yrgb;
		union win1_scl_offset_u { 
			struct win1_scl_offset_s { 
				unsigned int win1_hs_offset_yrgb: 8;
				unsigned int reserve_0: 8;
				unsigned int win1_vs_offset_yrgb: 8;
				unsigned int reserve_1: 8;
			} bits;
			unsigned int u32;
		} sw_win1_scl_offset;
		union win1_transformed_offset_u { 
			struct win1_transformed_offset_s { 
				unsigned int transformed_xoffset: 4;
				unsigned int reserve_0: 12;
				unsigned int transformed_yoffset: 4;
				unsigned int reserve_1: 12;
			} bits;
			unsigned int u32;
		} sw_win1_transformed_offset;
		union win1_zme_ctrl_u { 
			struct win1_zme_ctrl_s { 
				unsigned int reserve_0: 3;
				unsigned int win1_zme_dering_en: 1;
				unsigned int reserve_1: 27;
				unsigned int win1_zme_gating_en: 1;
			} bits;
			unsigned int u32;
		} sw_win1_zme_ctrl;
		union win1_zme_dering_para_u { 
			struct win1_zme_dering_para_s { 
				unsigned int win1_dering_alpha: 5;
				unsigned int reserve_0: 3;
				unsigned int win1_dering_beta: 5;
				unsigned int reserve_1: 3;
				unsigned int win1_dering_sen0: 5;
				unsigned int reserve_2: 3;
				unsigned int win1_dering_sen1: 5;
				unsigned int reserve_3: 3;
			} bits;
			unsigned int u32;
		} sw_win1_zme_dering_para;
		struct { 
			unsigned int reserve_data[12];
		} reserve_reg_200_208;
		union win1_fbcd_mask_en_u { 
			struct win1_fbcd_mask_en_s { 
				unsigned int reserve_0: 4;
				unsigned int win1_fbcd_gating_en: 1;
				unsigned int reserve_1: 27;
			} bits;
			unsigned int u32;
		} sw_win1_fbcd_mask_en;
		union win1_fbcd_mode_u { 
			struct win1_fbcd_mode_s { 
				unsigned int reserve_0: 2;
				unsigned int win1_xmir_en: 1;
				unsigned int win1_ymir_en: 1;
				unsigned int reserve_1: 28;
			} bits;
			unsigned int u32;
		} sw_win1_fbcd_mode;
		union win1_fbcd_hdr_ptr_u { 
			struct win1_fbcd_hdr_ptr_s { 
				unsigned int win1_fbcd_hdr_ptr: 32;
			} bits;
			unsigned int u32;
		} sw_win1_fbcd_hdr_ptr;
		union win1_fbcd_vir_width_u { 
			struct win1_fbcd_vir_width_s { 
				unsigned int win1_fbcd_pic_vir_width: 16;
				unsigned int win1_fbcd_tail_num: 16;
			} bits;
			unsigned int u32;
		} sw_win1_fbcd_vir_width;
		union win1_fbcd_size_u { 
			struct win1_fbcd_size_s { 
				unsigned int win1_fbcd_pic_width: 16;
				unsigned int win1_fbcd_pic_height: 16;
			} bits;
			unsigned int u32;
		} sw_win1_fbcd_size;
		union win1_fbcd_pic_offset_u { 
			struct win1_fbcd_pic_offset_s { 
				unsigned int win1_fbcd_pic_xoffset: 16;
				unsigned int win1_fbcd_pic_yoffset: 16;
			} bits;
			unsigned int u32;
		} sw_win1_fbcd_pic_offset;
		union win1_fbcd_dis_offset_u { 
			struct win1_fbcd_dis_offset_s { 
				unsigned int win1_fbcd_dis_xoffset: 16;
				unsigned int win1_fbcd_dis_yoffset: 16;
			} bits;
			unsigned int u32;
		} sw_win1_fbcd_dis_offset;
		union win1_fbcd_ctrl_u { 
			struct win1_fbcd_ctrl_s { 
				unsigned int reserve_0: 2;
				unsigned int win1_fbcd_pixel_packing_fmt: 5;
				unsigned int win1_fbcd_half_block: 1;
				unsigned int win1_fbcd_block_split: 1;
				unsigned int win1_fbcd_rb_swap_en: 1;
				unsigned int win1_fbcd_uv_swap_en: 1;
				unsigned int reserve_1: 5;
				unsigned int win1_fbcd_pld_offset_en: 1;
				unsigned int win1_fbcd_pld_range_en: 1;
				unsigned int reserve_2: 14;
			} bits;
			unsigned int u32;
		} sw_win1_fbcd_ctrl;
		struct { 
			unsigned int reserve_data[8];
		} reserve_reg_244_248;
		union win1_pld_ptr_offset_u { 
			struct win1_pld_ptr_offset_s { 
				unsigned int win1_pld_ptr_offset: 32;
			} bits;
			unsigned int u32;
		} sw_win1_pld_ptr_offset;
		union win1_pld_ptr_range_u { 
			struct win1_pld_ptr_range_s { 
				unsigned int win1_pld_ptr_range: 32;
			} bits;
			unsigned int u32;
		} sw_win1_pld_ptr_range;
		union cluster_ctrl_u { 
			struct cluster_ctrl_s { 
				unsigned int cluster_en: 1;
				unsigned int cluster_fbcd_en: 1;
				unsigned int reserve_0: 2;
				unsigned int cluster_lb_mode: 2;
				unsigned int reserve_1: 6;
				unsigned int cluster_dma_stop: 1;
				unsigned int reserve_2: 1;
				unsigned int cluster_mmu_bypass: 1;
				unsigned int reserve_3: 15;
				unsigned int fbcd_bug_fix_dis: 1;
				unsigned int cluster_frm_resetn_en: 1;
			} bits;
			unsigned int u32;
		} sw_cluster_ctrl;
		struct { 
			unsigned int reserve_data[240];
		} reserve_reg_264_500;
		union cluster_port_sel_imd_u { 
			struct cluster_port_sel_imd_s { 
				unsigned int cluster_port_sel: 2;
				unsigned int reserve_0: 30;
			} bits;
			unsigned int u32;
		} sw_cluster_port_sel_imd;
		union cluster_dly_num_u { 
			struct cluster_dly_num_s { 
				unsigned int win0_dly_num: 8;
				unsigned int win1_dly_num: 8;
				unsigned int reserve_0: 16;
			} bits;
			unsigned int u32;
		} sw_cluster_dly_num;
	} regs;
	unsigned int p_reg_addr[54];
}cluster1_0x27d01200_t;

typedef union esmart0_0x27d01800_u {
	struct esmart0_0x27d01800_s {
		union esmart_ctrl0_u { 
			struct esmart_ctrl0_s { 
				unsigned int esmart_yuv2rgb_en: 1;
				unsigned int esmart_rgb2yuv_en: 1;
				unsigned int esmart_csc_mode: 2;
				unsigned int esmart_8bpp_lut_en: 1;
				unsigned int esmart_8bpp_alpha_en: 1;
				unsigned int reserve_0: 2;
				unsigned int esmart_mid_swap: 1;
				unsigned int esmart_endian_swap: 1;
				unsigned int reserve_1: 2;
				unsigned int esmart_scl_num: 2;
				unsigned int reserve_2: 2;
				unsigned int esmart_y2r_csc_13bit_en: 1;
				unsigned int reserve_3: 7;
				unsigned int esmart_yuv2rgb_force_en: 1;
				unsigned int reserve_4: 6;
				unsigned int esmart_frm_resetn_en: 1;
			} bits;
			unsigned int u32;
		} sw_esmart_ctrl0;
		union esmart_ctrl1_u { 
			struct esmart_ctrl1_s { 
				unsigned int esmart_esmart_axi_rlen: 2;
				unsigned int esmart_yrgb_gather_en: 1;
				unsigned int esmart_cbcr_gather_en: 1;
				unsigned int esmart_yrgb_rid: 5;
				unsigned int reserve_0: 3;
				unsigned int esmart_cbcr_rid: 5;
				unsigned int reserve_1: 3;
				unsigned int esmart_yrgb_gather_num: 4;
				unsigned int esmart_cbcr_gather_num: 4;
				unsigned int esmart_dma_rreq_hurry_en: 1;
				unsigned int esmart_dma_rreq_thold: 2;
				unsigned int esmart_ymir_en: 1;
			} bits;
			unsigned int u32;
		} sw_esmart_ctrl1;
		union esmart_axi_ctrl_imd_u { 
			struct esmart_axi_ctrl_imd_s { 
				unsigned int esmart_dma_sop: 1;
				unsigned int esmart_axi_sel: 1;
				unsigned int esmart_mmu_bypass: 1;
				unsigned int esmart_outstanding_en: 1;
				unsigned int esmart_outstanding_num: 4;
				unsigned int esmart_auto_gating_en: 1;
				unsigned int reserve_0: 7;
				unsigned int esmart_dma_4k_addr_opt: 1;
				unsigned int reserve_1: 15;
			} bits;
			unsigned int u32;
		} sw_esmart_axi_ctrl_imd;
		struct { 
			unsigned int reserve_data[8];
		} reserve_reg_12_16;
		union region0_mst_ctl_u { 
			struct region0_mst_ctl_s { 
				unsigned int region0_mst_en: 1;
				unsigned int region0_data_fmt: 5;
				unsigned int reserve_0: 1;
				unsigned int region0_argb5551_en: 1;
				unsigned int region0_yrgb_2gt: 1;
				unsigned int region0_yrgb_4gt: 1;
				unsigned int region0_cbcr_2gt: 1;
				unsigned int region0_cbcr_4gt: 1;
				unsigned int region0_dither_up_en: 1;
				unsigned int region0_alpha_swap: 1;
				unsigned int region0_rb_swap: 1;
				unsigned int region0_mid_swap: 1;
				unsigned int region0_uv_swap: 1;
				unsigned int region0_yuv_clip: 1;
				unsigned int region0_rg_swap: 1;
				unsigned int reserve_1: 1;
				unsigned int region0_avg_en: 1;
				unsigned int region0_xgt_en: 1;
				unsigned int region0_xgt_mode: 2;
				unsigned int reserve_2: 8;
			} bits;
			unsigned int u32;
		} sw_region0_mst_ctl;
		union region0_mst_yrgb_u { 
			struct region0_mst_yrgb_s { 
				unsigned int region0_yrgb_mst: 32;
			} bits;
			unsigned int u32;
		} sw_region0_mst_yrgb;
		union region0_mst_cbcr_u { 
			struct region0_mst_cbcr_s { 
				unsigned int region0_cbcr_mst: 32;
			} bits;
			unsigned int u32;
		} sw_region0_mst_cbcr;
		union region0_vir_u { 
			struct region0_vir_s { 
				unsigned int region0_vir_stride: 16;
				unsigned int region0_vir_stride_uv: 16;
			} bits;
			unsigned int u32;
		} sw_region0_vir;
		union region0_act_info_u { 
			struct region0_act_info_s { 
				unsigned int region0_act_width: 13;
				unsigned int reserve_0: 3;
				unsigned int region0_act_heigth: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region0_act_info;
		union region0_dsp_info_u { 
			struct region0_dsp_info_s { 
				unsigned int region0_dsp_width: 13;
				unsigned int reserve_0: 3;
				unsigned int region0_dsp_height: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region0_dsp_info;
		union region0_dsp_offset_u { 
			struct region0_dsp_offset_s { 
				unsigned int region0_dsp_xoff: 13;
				unsigned int reserve_0: 3;
				unsigned int region0_dsp_yoff: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region0_dsp_offset;
		union region0_scl_ctrl_u { 
			struct region0_scl_ctrl_s { 
				unsigned int region0_yrgb_xsu_en: 1;
				unsigned int region0_yrgb_xsd_en: 1;
				unsigned int region0_yrgb_xscl_mode: 2;
				unsigned int region0_yrgb_ysu_en: 1;
				unsigned int region0_yrgb_ysd_en: 1;
				unsigned int region0_yrgb_yscl_mode: 2;
				unsigned int reserve_0: 8;
				unsigned int region0_xsu_bic_mode: 2;
				unsigned int reserve_1: 14;
			} bits;
			unsigned int u32;
		} sw_region0_scl_ctrl;
		union region0_scl_factor_yrgb_u { 
			struct region0_scl_factor_yrgb_s { 
				unsigned int region0_yrgb_xfactor: 16;
				unsigned int region0_yrgb_yfactor: 16;
			} bits;
			unsigned int u32;
		} sw_region0_scl_factor_yrgb;
		struct { 
			unsigned int reserve_data[8];
		} reserve_reg_56_60;
		union region0_scl_offset_u { 
			struct region0_scl_offset_s { 
				unsigned int region0_yrgb_xscl_offset: 8;
				unsigned int region0_yrgb_yscl_offset: 8;
				unsigned int reserve_0: 16;
			} bits;
			unsigned int u32;
		} sw_region0_scl_offset;
		union region1_mst_ctl_u { 
			struct region1_mst_ctl_s { 
				unsigned int region1_mst_en: 1;
				unsigned int region1_data_fmt: 5;
				unsigned int reserve_0: 1;
				unsigned int region1_argb5551_en: 1;
				unsigned int region1_yrgb_2gt: 1;
				unsigned int region1_yrgb_4gt: 1;
				unsigned int region1_cbcr_2gt: 1;
				unsigned int region1_cbcr_4gt: 1;
				unsigned int region1_dither_up_en: 1;
				unsigned int region1_alpha_swap: 1;
				unsigned int region1_rb_swap: 1;
				unsigned int region1_mid_swap: 1;
				unsigned int region1_uv_swap: 1;
				unsigned int region1_yuv_clip: 1;
				unsigned int region1_rg_swap: 1;
				unsigned int reserve_1: 1;
				unsigned int region1_avg_en: 1;
				unsigned int region1_xgt_en: 1;
				unsigned int region1_xgt_mode: 2;
				unsigned int reserve_2: 8;
			} bits;
			unsigned int u32;
		} sw_region1_mst_ctl;
		union region1_mst_yrgb_u { 
			struct region1_mst_yrgb_s { 
				unsigned int region1_yrgb_mst: 32;
			} bits;
			unsigned int u32;
		} sw_region1_mst_yrgb;
		union region1_mst_cbcr_u { 
			struct region1_mst_cbcr_s { 
				unsigned int region1_cbcr_mst: 32;
			} bits;
			unsigned int u32;
		} sw_region1_mst_cbcr;
		union region1_vir_u { 
			struct region1_vir_s { 
				unsigned int region1_vir_stride: 16;
				unsigned int region1_vir_stride_uv: 16;
			} bits;
			unsigned int u32;
		} sw_region1_vir;
		union region1_act_info_u { 
			struct region1_act_info_s { 
				unsigned int region1_act_width: 13;
				unsigned int reserve_0: 3;
				unsigned int region1_act_heigth: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region1_act_info;
		union region1_dsp_info_u { 
			struct region1_dsp_info_s { 
				unsigned int region1_dsp_width: 13;
				unsigned int reserve_0: 3;
				unsigned int region1_dsp_height: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region1_dsp_info;
		union region1_dsp_offset_u { 
			struct region1_dsp_offset_s { 
				unsigned int region1_dsp_xoff: 13;
				unsigned int reserve_0: 3;
				unsigned int region1_dsp_yoff: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region1_dsp_offset;
		union region1_scl_ctrl_u { 
			struct region1_scl_ctrl_s { 
				unsigned int region1_yrgb_xsu_en: 1;
				unsigned int region1_yrgb_xsd_en: 1;
				unsigned int region1_yrgb_xscl_mode: 2;
				unsigned int region1_yrgb_ysu_en: 1;
				unsigned int region1_yrgb_ysd_en: 1;
				unsigned int region1_yrgb_yscl_mode: 2;
				unsigned int reserve_0: 8;
				unsigned int region1_xsu_bic_mode: 2;
				unsigned int reserve_1: 14;
			} bits;
			unsigned int u32;
		} sw_region1_scl_ctrl;
		union region1_scl_factor_yrgb_u { 
			struct region1_scl_factor_yrgb_s { 
				unsigned int region1_yrgb_xfactor: 16;
				unsigned int region1_yrgb_yfactor: 16;
			} bits;
			unsigned int u32;
		} sw_region1_scl_factor_yrgb;
		struct { 
			unsigned int reserve_data[8];
		} reserve_reg_104_108;
		union region1_scl_offset_u { 
			struct region1_scl_offset_s { 
				unsigned int region1_yrgb_xscl_offset: 8;
				unsigned int region1_yrgb_yscl_offset: 8;
				unsigned int reserve_0: 16;
			} bits;
			unsigned int u32;
		} sw_region1_scl_offset;
		union region2_mst_ctl_u { 
			struct region2_mst_ctl_s { 
				unsigned int region2_mst_en: 1;
				unsigned int region2_data_fmt: 5;
				unsigned int reserve_0: 1;
				unsigned int region2_argb5551_en: 1;
				unsigned int region2_yrgb_2gt: 1;
				unsigned int region2_yrgb_4gt: 1;
				unsigned int region2_cbcr_2gt: 1;
				unsigned int region2_cbcr_4gt: 1;
				unsigned int region2_dither_up_en: 1;
				unsigned int region2_alpha_swap: 1;
				unsigned int region2_rb_swap: 1;
				unsigned int region2_mid_swap: 1;
				unsigned int region2_uv_swap: 1;
				unsigned int region2_yuv_clip: 1;
				unsigned int region2_rg_swap: 1;
				unsigned int reserve_1: 1;
				unsigned int region2_avg_en: 1;
				unsigned int region2_xgt_en: 1;
				unsigned int region2_xgt_mode: 2;
				unsigned int reserve_2: 8;
			} bits;
			unsigned int u32;
		} sw_region2_mst_ctl;
		union region2_mst_yrgb_u { 
			struct region2_mst_yrgb_s { 
				unsigned int region2_yrgb_mst: 32;
			} bits;
			unsigned int u32;
		} sw_region2_mst_yrgb;
		union region2_mst_cbcr_u { 
			struct region2_mst_cbcr_s { 
				unsigned int region2_cbcr_mst: 32;
			} bits;
			unsigned int u32;
		} sw_region2_mst_cbcr;
		union region2_vir_u { 
			struct region2_vir_s { 
				unsigned int region2_vir_stride: 16;
				unsigned int region2_vir_stride_uv: 16;
			} bits;
			unsigned int u32;
		} sw_region2_vir;
		union region2_act_info_u { 
			struct region2_act_info_s { 
				unsigned int region2_act_width: 13;
				unsigned int reserve_0: 3;
				unsigned int region2_act_heigth: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region2_act_info;
		union region2_dsp_info_u { 
			struct region2_dsp_info_s { 
				unsigned int region2_dsp_width: 13;
				unsigned int reserve_0: 3;
				unsigned int region2_dsp_height: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region2_dsp_info;
		union region2_dsp_offset_u { 
			struct region2_dsp_offset_s { 
				unsigned int region2_dsp_xoff: 13;
				unsigned int reserve_0: 3;
				unsigned int region2_dsp_yoff: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region2_dsp_offset;
		union region2_scl_ctrl_u { 
			struct region2_scl_ctrl_s { 
				unsigned int region2_yrgb_xsu_en: 1;
				unsigned int region2_yrgb_xsd_en: 1;
				unsigned int region2_yrgb_xscl_mode: 2;
				unsigned int region2_yrgb_ysu_en: 1;
				unsigned int region2_yrgb_ysd_en: 1;
				unsigned int region2_yrgb_yscl_mode: 2;
				unsigned int reserve_0: 8;
				unsigned int region2_xsu_bic_mode: 2;
				unsigned int reserve_1: 14;
			} bits;
			unsigned int u32;
		} sw_region2_scl_ctrl;
		union region2_scl_factor_yrgb_u { 
			struct region2_scl_factor_yrgb_s { 
				unsigned int region2_yrgb_xfactor: 16;
				unsigned int region2_yrgb_yfactor: 16;
			} bits;
			unsigned int u32;
		} sw_region2_scl_factor_yrgb;
		struct { 
			unsigned int reserve_data[8];
		} reserve_reg_152_156;
		union region2_scl_offset_u { 
			struct region2_scl_offset_s { 
				unsigned int region2_yrgb_xscl_offset: 8;
				unsigned int region2_yrgb_yscl_offset: 8;
				unsigned int reserve_0: 16;
			} bits;
			unsigned int u32;
		} sw_region2_scl_offset;
		union region3_mst_ctl_u { 
			struct region3_mst_ctl_s { 
				unsigned int region3_mst_en: 1;
				unsigned int region3_data_fmt: 5;
				unsigned int reserve_0: 2;
				unsigned int region3_yrgb_2gt: 1;
				unsigned int region3_yrgb_4gt: 1;
				unsigned int region3_cbcr_2gt: 1;
				unsigned int region3_cbcr_4gt: 1;
				unsigned int region3_dither_up_en: 1;
				unsigned int region3_alpha_swap: 1;
				unsigned int region3_rb_swap: 1;
				unsigned int region3_mid_swap: 1;
				unsigned int region3_uv_swap: 1;
				unsigned int region3_yuv_clip: 1;
				unsigned int region3_rg_swap: 1;
				unsigned int reserve_1: 1;
				unsigned int region3_avg_en: 1;
				unsigned int region3_xgt_en: 1;
				unsigned int region3_xgt_mode: 2;
				unsigned int reserve_2: 8;
			} bits;
			unsigned int u32;
		} sw_region3_mst_ctl;
		union region3_mst_yrgb_u { 
			struct region3_mst_yrgb_s { 
				unsigned int region3_yrgb_mst: 32;
			} bits;
			unsigned int u32;
		} sw_region3_mst_yrgb;
		union region3_mst_cbcr_u { 
			struct region3_mst_cbcr_s { 
				unsigned int region3_cbcr_mst: 32;
			} bits;
			unsigned int u32;
		} sw_region3_mst_cbcr;
		union region3_vir_u { 
			struct region3_vir_s { 
				unsigned int region3_vir_stride: 16;
				unsigned int region3_vir_stride_uv: 16;
			} bits;
			unsigned int u32;
		} sw_region3_vir;
		union region3_act_info_u { 
			struct region3_act_info_s { 
				unsigned int region3_act_width: 13;
				unsigned int reserve_0: 3;
				unsigned int region3_act_heigth: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region3_act_info;
		union region3_dsp_info_u { 
			struct region3_dsp_info_s { 
				unsigned int region3_dsp_width: 13;
				unsigned int reserve_0: 3;
				unsigned int region3_dsp_height: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region3_dsp_info;
		union region3_dsp_offset_u { 
			struct region3_dsp_offset_s { 
				unsigned int region3_dsp_xoff: 13;
				unsigned int reserve_0: 3;
				unsigned int region3_dsp_yoff: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region3_dsp_offset;
		union region3_scl_ctrl_u { 
			struct region3_scl_ctrl_s { 
				unsigned int region3_yrgb_xsu_en: 1;
				unsigned int region3_yrgb_xsd_en: 1;
				unsigned int region3_yrgb_xscl_mode: 2;
				unsigned int region3_yrgb_ysu_en: 1;
				unsigned int region3_yrgb_ysd_en: 1;
				unsigned int region3_yrgb_yscl_mode: 2;
				unsigned int reserve_0: 8;
				unsigned int region3_xsu_bic_mode: 2;
				unsigned int reserve_1: 14;
			} bits;
			unsigned int u32;
		} sw_region3_scl_ctrl;
		union region3_scl_factor_yrgb_u { 
			struct region3_scl_factor_yrgb_s { 
				unsigned int region3_yrgb_xfactor: 16;
				unsigned int region3_yrgb_yfactor: 16;
			} bits;
			unsigned int u32;
		} sw_region3_scl_factor_yrgb;
		struct { 
			unsigned int reserve_data[8];
		} reserve_reg_200_204;
		union region3_scl_offset_u { 
			struct region3_scl_offset_s { 
				unsigned int region3_yrgb_xscl_offset: 8;
				unsigned int region3_yrgb_yscl_offset: 8;
				unsigned int reserve_0: 16;
			} bits;
			unsigned int u32;
		} sw_region3_scl_offset;
		union esmart_key_ctrl_u { 
			struct esmart_key_ctrl_s { 
				unsigned int esmart_b_key_value: 10;
				unsigned int esmart_g_key_value: 10;
				unsigned int esmart_r_key_value: 10;
				unsigned int reserve_0: 1;
				unsigned int esmart_key_en: 1;
			} bits;
			unsigned int u32;
		} sw_esmart_key_ctrl;
		union esmart_bg_en_u { 
			struct esmart_bg_en_s { 
				unsigned int esmart_b_value: 10;
				unsigned int esmart_g_value: 10;
				unsigned int esmart_r_value: 10;
				unsigned int reserve_0: 1;
				unsigned int esmart_bg_en: 1;
			} bits;
			unsigned int u32;
		} sw_esmart_bg_en;
		union esmart_alpha_map_u { 
			struct esmart_alpha_map_s { 
				unsigned int alpha_0_map: 8;
				unsigned int alpha_1_map: 8;
				unsigned int reserve_0: 15;
				unsigned int alpha_map_en: 1;
			} bits;
			unsigned int u32;
		} sw_esmart_alpha_map;
		struct { 
			unsigned int reserve_data[24];
		} reserve_reg_224_244;
		union esmart_port_sel_imd_u { 
			struct esmart_port_sel_imd_s { 
				unsigned int esmart_port_sel: 2;
				unsigned int reserve_0: 30;
			} bits;
			unsigned int u32;
		} sw_esmart_port_sel_imd;
		union esmart_dly_num_u { 
			struct esmart_dly_num_s { 
				unsigned int esmart_dly_num: 8;
				unsigned int reserve_0: 24;
			} bits;
			unsigned int u32;
		} sw_esmart_dly_num;
	} regs;
	unsigned int p_reg_addr[48];
}esmart0_0x27d01800_t;

typedef union esmart1_0x27d01a00_u {
	struct esmart1_0x27d01a00_s {
		union esmart_ctrl0_u { 
			struct esmart_ctrl0_s { 
				unsigned int esmart_yuv2rgb_en: 1;
				unsigned int esmart_rgb2yuv_en: 1;
				unsigned int esmart_csc_mode: 2;
				unsigned int esmart_8bpp_lut_en: 1;
				unsigned int esmart_8bpp_alpha_en: 1;
				unsigned int reserve_0: 2;
				unsigned int esmart_mid_swap: 1;
				unsigned int esmart_endian_swap: 1;
				unsigned int reserve_1: 2;
				unsigned int esmart_scl_num: 2;
				unsigned int reserve_2: 10;
				unsigned int esmart_yuv2rgb_force_en: 1;
				unsigned int reserve_3: 6;
				unsigned int esmart_frm_resetn_en: 1;
			} bits;
			unsigned int u32;
		} sw_esmart_ctrl0;
		union esmart_ctrl1_u { 
			struct esmart_ctrl1_s { 
				unsigned int esmart_esmart_axi_rlen: 2;
				unsigned int esmart_yrgb_gather_en: 1;
				unsigned int esmart_cbcr_gather_en: 1;
				unsigned int esmart_yrgb_rid: 5;
				unsigned int reserve_0: 3;
				unsigned int esmart_cbcr_rid: 5;
				unsigned int reserve_1: 3;
				unsigned int esmart_yrgb_gather_num: 4;
				unsigned int esmart_cbcr_gather_num: 4;
				unsigned int esmart_dma_rreq_hurry_en: 1;
				unsigned int esmart_dma_rreq_thold: 2;
				unsigned int esmart_ymir_en: 1;
			} bits;
			unsigned int u32;
		} sw_esmart_ctrl1;
		union esmart_axi_ctrl_imd_u { 
			struct esmart_axi_ctrl_imd_s { 
				unsigned int esmart_dma_sop: 1;
				unsigned int esmart_axi_sel: 1;
				unsigned int esmart_mmu_bypass: 1;
				unsigned int esmart_outstanding_en: 1;
				unsigned int esmart_outstanding_num: 4;
				unsigned int esmart_auto_gating_en: 1;
				unsigned int reserve_0: 7;
				unsigned int esmart_dma_4k_addr_opt: 1;
				unsigned int reserve_1: 15;
			} bits;
			unsigned int u32;
		} sw_esmart_axi_ctrl_imd;
		struct { 
			unsigned int reserve_data[8];
		} reserve_reg_12_16;
		union region0_mst_ctl_u { 
			struct region0_mst_ctl_s { 
				unsigned int region0_mst_en: 1;
				unsigned int region0_data_fmt: 5;
				unsigned int reserve_0: 1;
				unsigned int region0_argb5551_en: 1;
				unsigned int region0_yrgb_2gt: 1;
				unsigned int region0_yrgb_4gt: 1;
				unsigned int region0_cbcr_2gt: 1;
				unsigned int region0_cbcr_4gt: 1;
				unsigned int region0_dither_up_en: 1;
				unsigned int region0_alpha_swap: 1;
				unsigned int region0_rb_swap: 1;
				unsigned int region0_mid_swap: 1;
				unsigned int region0_uv_swap: 1;
				unsigned int region0_yuv_clip: 1;
				unsigned int region0_rg_swap: 1;
				unsigned int reserve_1: 1;
				unsigned int region0_avg_en: 1;
				unsigned int region0_xgt_en: 1;
				unsigned int region0_xgt_mode: 2;
				unsigned int reserve_2: 8;
			} bits;
			unsigned int u32;
		} sw_region0_mst_ctl;
		union region0_mst_yrgb_u { 
			struct region0_mst_yrgb_s { 
				unsigned int region0_yrgb_mst: 32;
			} bits;
			unsigned int u32;
		} sw_region0_mst_yrgb;
		union region0_mst_cbcr_u { 
			struct region0_mst_cbcr_s { 
				unsigned int region0_cbcr_mst: 32;
			} bits;
			unsigned int u32;
		} sw_region0_mst_cbcr;
		union region0_vir_u { 
			struct region0_vir_s { 
				unsigned int region0_vir_stride: 16;
				unsigned int region0_vir_stride_uv: 16;
			} bits;
			unsigned int u32;
		} sw_region0_vir;
		union region0_act_info_u { 
			struct region0_act_info_s { 
				unsigned int region0_act_width: 13;
				unsigned int reserve_0: 3;
				unsigned int region0_act_heigth: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region0_act_info;
		union region0_dsp_info_u { 
			struct region0_dsp_info_s { 
				unsigned int region0_dsp_width: 13;
				unsigned int reserve_0: 3;
				unsigned int region0_dsp_height: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region0_dsp_info;
		union region0_dsp_offset_u { 
			struct region0_dsp_offset_s { 
				unsigned int region0_dsp_xoff: 13;
				unsigned int reserve_0: 3;
				unsigned int region0_dsp_yoff: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region0_dsp_offset;
		union region0_scl_ctrl_u { 
			struct region0_scl_ctrl_s { 
				unsigned int region0_yrgb_xsu_en: 1;
				unsigned int region0_yrgb_xsd_en: 1;
				unsigned int region0_yrgb_xscl_mode: 2;
				unsigned int region0_yrgb_ysu_en: 1;
				unsigned int region0_yrgb_ysd_en: 1;
				unsigned int region0_yrgb_yscl_mode: 2;
				unsigned int reserve_0: 8;
				unsigned int region0_xsu_bic_mode: 2;
				unsigned int reserve_1: 14;
			} bits;
			unsigned int u32;
		} sw_region0_scl_ctrl;
		union region0_scl_factor_yrgb_u { 
			struct region0_scl_factor_yrgb_s { 
				unsigned int region0_yrgb_xfactor: 16;
				unsigned int region0_yrgb_yfactor: 16;
			} bits;
			unsigned int u32;
		} sw_region0_scl_factor_yrgb;
		struct { 
			unsigned int reserve_data[8];
		} reserve_reg_56_60;
		union region0_scl_offset_u { 
			struct region0_scl_offset_s { 
				unsigned int region0_yrgb_xscl_offset: 8;
				unsigned int region0_yrgb_yscl_offset: 8;
				unsigned int reserve_0: 16;
			} bits;
			unsigned int u32;
		} sw_region0_scl_offset;
		union region1_mst_ctl_u { 
			struct region1_mst_ctl_s { 
				unsigned int region1_mst_en: 1;
				unsigned int region1_data_fmt: 5;
				unsigned int reserve_0: 1;
				unsigned int region1_argb5551_en: 1;
				unsigned int region1_yrgb_2gt: 1;
				unsigned int region1_yrgb_4gt: 1;
				unsigned int region1_cbcr_2gt: 1;
				unsigned int region1_cbcr_4gt: 1;
				unsigned int region1_dither_up_en: 1;
				unsigned int region1_alpha_swap: 1;
				unsigned int region1_rb_swap: 1;
				unsigned int region1_mid_swap: 1;
				unsigned int region1_uv_swap: 1;
				unsigned int region1_yuv_clip: 1;
				unsigned int region1_rg_swap: 1;
				unsigned int reserve_1: 1;
				unsigned int region1_avg_en: 1;
				unsigned int region1_xgt_en: 1;
				unsigned int region1_xgt_mode: 2;
				unsigned int reserve_2: 8;
			} bits;
			unsigned int u32;
		} sw_region1_mst_ctl;
		union region1_mst_yrgb_u { 
			struct region1_mst_yrgb_s { 
				unsigned int region1_yrgb_mst: 32;
			} bits;
			unsigned int u32;
		} sw_region1_mst_yrgb;
		union region1_mst_cbcr_u { 
			struct region1_mst_cbcr_s { 
				unsigned int region1_cbcr_mst: 32;
			} bits;
			unsigned int u32;
		} sw_region1_mst_cbcr;
		union region1_vir_u { 
			struct region1_vir_s { 
				unsigned int region1_vir_stride: 16;
				unsigned int region1_vir_stride_uv: 16;
			} bits;
			unsigned int u32;
		} sw_region1_vir;
		union region1_act_info_u { 
			struct region1_act_info_s { 
				unsigned int region1_act_width: 13;
				unsigned int reserve_0: 3;
				unsigned int region1_act_heigth: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region1_act_info;
		union region1_dsp_info_u { 
			struct region1_dsp_info_s { 
				unsigned int region1_dsp_width: 13;
				unsigned int reserve_0: 3;
				unsigned int region1_dsp_height: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region1_dsp_info;
		union region1_dsp_offset_u { 
			struct region1_dsp_offset_s { 
				unsigned int region1_dsp_xoff: 13;
				unsigned int reserve_0: 3;
				unsigned int region1_dsp_yoff: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region1_dsp_offset;
		union region1_scl_ctrl_u { 
			struct region1_scl_ctrl_s { 
				unsigned int region1_yrgb_xsu_en: 1;
				unsigned int region1_yrgb_xsd_en: 1;
				unsigned int region1_yrgb_xscl_mode: 2;
				unsigned int region1_yrgb_ysu_en: 1;
				unsigned int region1_yrgb_ysd_en: 1;
				unsigned int region1_yrgb_yscl_mode: 2;
				unsigned int reserve_0: 8;
				unsigned int region1_xsu_bic_mode: 2;
				unsigned int reserve_1: 14;
			} bits;
			unsigned int u32;
		} sw_region1_scl_ctrl;
		union region1_scl_factor_yrgb_u { 
			struct region1_scl_factor_yrgb_s { 
				unsigned int region1_yrgb_xfactor: 16;
				unsigned int region1_yrgb_yfactor: 16;
			} bits;
			unsigned int u32;
		} sw_region1_scl_factor_yrgb;
		struct { 
			unsigned int reserve_data[8];
		} reserve_reg_104_108;
		union region1_scl_offset_u { 
			struct region1_scl_offset_s { 
				unsigned int region1_yrgb_xscl_offset: 8;
				unsigned int region1_yrgb_yscl_offset: 8;
				unsigned int reserve_0: 16;
			} bits;
			unsigned int u32;
		} sw_region1_scl_offset;
		union region2_mst_ctl_u { 
			struct region2_mst_ctl_s { 
				unsigned int region2_mst_en: 1;
				unsigned int region2_data_fmt: 5;
				unsigned int reserve_0: 1;
				unsigned int region2_argb5551_en: 1;
				unsigned int region2_yrgb_2gt: 1;
				unsigned int region2_yrgb_4gt: 1;
				unsigned int region2_cbcr_2gt: 1;
				unsigned int region2_cbcr_4gt: 1;
				unsigned int region2_dither_up_en: 1;
				unsigned int region2_alpha_swap: 1;
				unsigned int region2_rb_swap: 1;
				unsigned int region2_mid_swap: 1;
				unsigned int region2_uv_swap: 1;
				unsigned int region2_yuv_clip: 1;
				unsigned int region2_rg_swap: 1;
				unsigned int reserve_1: 1;
				unsigned int region2_avg_en: 1;
				unsigned int region2_xgt_en: 1;
				unsigned int region2_xgt_mode: 2;
				unsigned int reserve_2: 8;
			} bits;
			unsigned int u32;
		} sw_region2_mst_ctl;
		union region2_mst_yrgb_u { 
			struct region2_mst_yrgb_s { 
				unsigned int region2_yrgb_mst: 32;
			} bits;
			unsigned int u32;
		} sw_region2_mst_yrgb;
		union region2_mst_cbcr_u { 
			struct region2_mst_cbcr_s { 
				unsigned int region2_cbcr_mst: 32;
			} bits;
			unsigned int u32;
		} sw_region2_mst_cbcr;
		union region2_vir_u { 
			struct region2_vir_s { 
				unsigned int region2_vir_stride: 16;
				unsigned int region2_vir_stride_uv: 16;
			} bits;
			unsigned int u32;
		} sw_region2_vir;
		union region2_act_info_u { 
			struct region2_act_info_s { 
				unsigned int region2_act_width: 13;
				unsigned int reserve_0: 3;
				unsigned int region2_act_heigth: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region2_act_info;
		union region2_dsp_info_u { 
			struct region2_dsp_info_s { 
				unsigned int region2_dsp_width: 13;
				unsigned int reserve_0: 3;
				unsigned int region2_dsp_height: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region2_dsp_info;
		union region2_dsp_offset_u { 
			struct region2_dsp_offset_s { 
				unsigned int region2_dsp_xoff: 13;
				unsigned int reserve_0: 3;
				unsigned int region2_dsp_yoff: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region2_dsp_offset;
		union region2_scl_ctrl_u { 
			struct region2_scl_ctrl_s { 
				unsigned int region2_yrgb_xsu_en: 1;
				unsigned int region2_yrgb_xsd_en: 1;
				unsigned int region2_yrgb_xscl_mode: 2;
				unsigned int region2_yrgb_ysu_en: 1;
				unsigned int region2_yrgb_ysd_en: 1;
				unsigned int region2_yrgb_yscl_mode: 2;
				unsigned int reserve_0: 8;
				unsigned int region2_xsu_bic_mode: 2;
				unsigned int reserve_1: 14;
			} bits;
			unsigned int u32;
		} sw_region2_scl_ctrl;
		union region2_scl_factor_yrgb_u { 
			struct region2_scl_factor_yrgb_s { 
				unsigned int region2_yrgb_xfactor: 16;
				unsigned int region2_yrgb_yfactor: 16;
			} bits;
			unsigned int u32;
		} sw_region2_scl_factor_yrgb;
		struct { 
			unsigned int reserve_data[8];
		} reserve_reg_152_156;
		union region2_scl_offset_u { 
			struct region2_scl_offset_s { 
				unsigned int region2_yrgb_xscl_offset: 8;
				unsigned int region2_yrgb_yscl_offset: 8;
				unsigned int reserve_0: 16;
			} bits;
			unsigned int u32;
		} sw_region2_scl_offset;
		union region3_mst_ctl_u { 
			struct region3_mst_ctl_s { 
				unsigned int region3_mst_en: 1;
				unsigned int region3_data_fmt: 5;
				unsigned int reserve_0: 2;
				unsigned int region3_yrgb_2gt: 1;
				unsigned int region3_yrgb_4gt: 1;
				unsigned int region3_cbcr_2gt: 1;
				unsigned int region3_cbcr_4gt: 1;
				unsigned int region3_dither_up_en: 1;
				unsigned int region3_alpha_swap: 1;
				unsigned int region3_rb_swap: 1;
				unsigned int region3_mid_swap: 1;
				unsigned int region3_uv_swap: 1;
				unsigned int region3_yuv_clip: 1;
				unsigned int region3_rg_swap: 1;
				unsigned int reserve_1: 1;
				unsigned int region3_avg_en: 1;
				unsigned int region3_xgt_en: 1;
				unsigned int region3_xgt_mode: 2;
				unsigned int reserve_2: 8;
			} bits;
			unsigned int u32;
		} sw_region3_mst_ctl;
		union region3_mst_yrgb_u { 
			struct region3_mst_yrgb_s { 
				unsigned int region3_yrgb_mst: 32;
			} bits;
			unsigned int u32;
		} sw_region3_mst_yrgb;
		union region3_mst_cbcr_u { 
			struct region3_mst_cbcr_s { 
				unsigned int region3_cbcr_mst: 32;
			} bits;
			unsigned int u32;
		} sw_region3_mst_cbcr;
		union region3_vir_u { 
			struct region3_vir_s { 
				unsigned int region3_vir_stride: 16;
				unsigned int region3_vir_stride_uv: 16;
			} bits;
			unsigned int u32;
		} sw_region3_vir;
		union region3_act_info_u { 
			struct region3_act_info_s { 
				unsigned int region3_act_width: 13;
				unsigned int reserve_0: 3;
				unsigned int region3_act_heigth: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region3_act_info;
		union region3_dsp_info_u { 
			struct region3_dsp_info_s { 
				unsigned int region3_dsp_width: 13;
				unsigned int reserve_0: 3;
				unsigned int region3_dsp_height: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region3_dsp_info;
		union region3_dsp_offset_u { 
			struct region3_dsp_offset_s { 
				unsigned int region3_dsp_xoff: 13;
				unsigned int reserve_0: 3;
				unsigned int region3_dsp_yoff: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region3_dsp_offset;
		union region3_scl_ctrl_u { 
			struct region3_scl_ctrl_s { 
				unsigned int region3_yrgb_xsu_en: 1;
				unsigned int region3_yrgb_xsd_en: 1;
				unsigned int region3_yrgb_xscl_mode: 2;
				unsigned int region3_yrgb_ysu_en: 1;
				unsigned int region3_yrgb_ysd_en: 1;
				unsigned int region3_yrgb_yscl_mode: 2;
				unsigned int reserve_0: 8;
				unsigned int region3_xsu_bic_mode: 2;
				unsigned int reserve_1: 14;
			} bits;
			unsigned int u32;
		} sw_region3_scl_ctrl;
		union region3_scl_factor_yrgb_u { 
			struct region3_scl_factor_yrgb_s { 
				unsigned int region3_yrgb_xfactor: 16;
				unsigned int region3_yrgb_yfactor: 16;
			} bits;
			unsigned int u32;
		} sw_region3_scl_factor_yrgb;
		struct { 
			unsigned int reserve_data[8];
		} reserve_reg_200_204;
		union region3_scl_offset_u { 
			struct region3_scl_offset_s { 
				unsigned int region3_yrgb_xscl_offset: 8;
				unsigned int region3_yrgb_yscl_offset: 8;
				unsigned int reserve_0: 16;
			} bits;
			unsigned int u32;
		} sw_region3_scl_offset;
		union esmart_key_ctrl_u { 
			struct esmart_key_ctrl_s { 
				unsigned int esmart_b_key_value: 10;
				unsigned int esmart_g_key_value: 10;
				unsigned int esmart_r_key_value: 10;
				unsigned int reserve_0: 1;
				unsigned int esmart_key_en: 1;
			} bits;
			unsigned int u32;
		} sw_esmart_key_ctrl;
		union esmart_bg_en_u { 
			struct esmart_bg_en_s { 
				unsigned int esmart_b_value: 10;
				unsigned int esmart_g_value: 10;
				unsigned int esmart_r_value: 10;
				unsigned int reserve_0: 1;
				unsigned int esmart_bg_en: 1;
			} bits;
			unsigned int u32;
		} sw_esmart_bg_en;
		union esmart_alpha_map_u { 
			struct esmart_alpha_map_s { 
				unsigned int alpha_0_map: 8;
				unsigned int alpha_1_map: 8;
				unsigned int reserve_0: 15;
				unsigned int alpha_map_en: 1;
			} bits;
			unsigned int u32;
		} sw_esmart_alpha_map;
		struct { 
			unsigned int reserve_data[24];
		} reserve_reg_224_244;
		union esmart_port_sel_imd_u { 
			struct esmart_port_sel_imd_s { 
				unsigned int esmart_port_sel: 2;
				unsigned int reserve_0: 30;
			} bits;
			unsigned int u32;
		} sw_esmart_port_sel_imd;
		union esmart_dly_num_u { 
			struct esmart_dly_num_s { 
				unsigned int esmart_dly_num: 8;
				unsigned int reserve_0: 24;
			} bits;
			unsigned int u32;
		} sw_esmart_dly_num;
	} regs;
	unsigned int p_reg_addr[48];
}esmart1_0x27d01a00_t;

typedef union esmart2_0x27d01c00_u {
	struct esmart2_0x27d01c00_s {
		union esmart_ctrl0_u { 
			struct esmart_ctrl0_s { 
				unsigned int esmart_yuv2rgb_en: 1;
				unsigned int esmart_rgb2yuv_en: 1;
				unsigned int esmart_csc_mode: 2;
				unsigned int esmart_8bpp_lut_en: 1;
				unsigned int esmart_8bpp_alpha_en: 1;
				unsigned int reserve_0: 2;
				unsigned int esmart_mid_swap: 1;
				unsigned int esmart_endian_swap: 1;
				unsigned int reserve_1: 2;
				unsigned int esmart_scl_num: 2;
				unsigned int reserve_2: 10;
				unsigned int esmart_yuv2rgb_force_en: 1;
				unsigned int reserve_3: 6;
				unsigned int esmart_frm_resetn_en: 1;
			} bits;
			unsigned int u32;
		} sw_esmart_ctrl0;
		union esmart_ctrl1_u { 
			struct esmart_ctrl1_s { 
				unsigned int esmart_esmart_axi_rlen: 2;
				unsigned int esmart_yrgb_gather_en: 1;
				unsigned int esmart_cbcr_gather_en: 1;
				unsigned int esmart_yrgb_rid: 5;
				unsigned int reserve_0: 3;
				unsigned int esmart_cbcr_rid: 5;
				unsigned int reserve_1: 3;
				unsigned int esmart_yrgb_gather_num: 4;
				unsigned int esmart_cbcr_gather_num: 4;
				unsigned int esmart_dma_rreq_hurry_en: 1;
				unsigned int esmart_dma_rreq_thold: 2;
				unsigned int esmart_ymir_en: 1;
			} bits;
			unsigned int u32;
		} sw_esmart_ctrl1;
		union esmart_axi_ctrl_imd_u { 
			struct esmart_axi_ctrl_imd_s { 
				unsigned int esmart_dma_sop: 1;
				unsigned int esmart_axi_sel: 1;
				unsigned int esmart_mmu_bypass: 1;
				unsigned int esmart_outstanding_en: 1;
				unsigned int esmart_outstanding_num: 4;
				unsigned int esmart_auto_gating_en: 1;
				unsigned int reserve_0: 7;
				unsigned int esmart_dma_4k_addr_opt: 1;
				unsigned int reserve_1: 15;
			} bits;
			unsigned int u32;
		} sw_esmart_axi_ctrl_imd;
		struct { 
			unsigned int reserve_data[8];
		} reserve_reg_12_16;
		union region0_mst_ctl_u { 
			struct region0_mst_ctl_s { 
				unsigned int region0_mst_en: 1;
				unsigned int region0_data_fmt: 5;
				unsigned int reserve_0: 1;
				unsigned int region0_argb5551_en: 1;
				unsigned int region0_yrgb_2gt: 1;
				unsigned int region0_yrgb_4gt: 1;
				unsigned int region0_cbcr_2gt: 1;
				unsigned int region0_cbcr_4gt: 1;
				unsigned int region0_dither_up_en: 1;
				unsigned int region0_alpha_swap: 1;
				unsigned int region0_rb_swap: 1;
				unsigned int region0_mid_swap: 1;
				unsigned int region0_uv_swap: 1;
				unsigned int region0_yuv_clip: 1;
				unsigned int region0_rg_swap: 1;
				unsigned int reserve_1: 1;
				unsigned int region0_avg_en: 1;
				unsigned int region0_xgt_en: 1;
				unsigned int region0_xgt_mode: 2;
				unsigned int reserve_2: 8;
			} bits;
			unsigned int u32;
		} sw_region0_mst_ctl;
		union region0_mst_yrgb_u { 
			struct region0_mst_yrgb_s { 
				unsigned int region0_yrgb_mst: 32;
			} bits;
			unsigned int u32;
		} sw_region0_mst_yrgb;
		union region0_mst_cbcr_u { 
			struct region0_mst_cbcr_s { 
				unsigned int region0_cbcr_mst: 32;
			} bits;
			unsigned int u32;
		} sw_region0_mst_cbcr;
		union region0_vir_u { 
			struct region0_vir_s { 
				unsigned int region0_vir_stride: 16;
				unsigned int region0_vir_stride_uv: 16;
			} bits;
			unsigned int u32;
		} sw_region0_vir;
		union region0_act_info_u { 
			struct region0_act_info_s { 
				unsigned int region0_act_width: 13;
				unsigned int reserve_0: 3;
				unsigned int region0_act_heigth: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region0_act_info;
		union region0_dsp_info_u { 
			struct region0_dsp_info_s { 
				unsigned int region0_dsp_width: 13;
				unsigned int reserve_0: 3;
				unsigned int region0_dsp_height: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region0_dsp_info;
		union region0_dsp_offset_u { 
			struct region0_dsp_offset_s { 
				unsigned int region0_dsp_xoff: 13;
				unsigned int reserve_0: 3;
				unsigned int region0_dsp_yoff: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region0_dsp_offset;
		union region0_scl_ctrl_u { 
			struct region0_scl_ctrl_s { 
				unsigned int region0_yrgb_xsu_en: 1;
				unsigned int region0_yrgb_xsd_en: 1;
				unsigned int region0_yrgb_xscl_mode: 2;
				unsigned int region0_yrgb_ysu_en: 1;
				unsigned int region0_yrgb_ysd_en: 1;
				unsigned int region0_yrgb_yscl_mode: 2;
				unsigned int reserve_0: 8;
				unsigned int region0_xsu_bic_mode: 2;
				unsigned int reserve_1: 14;
			} bits;
			unsigned int u32;
		} sw_region0_scl_ctrl;
		union region0_scl_factor_yrgb_u { 
			struct region0_scl_factor_yrgb_s { 
				unsigned int region0_yrgb_xfactor: 16;
				unsigned int region0_yrgb_yfactor: 16;
			} bits;
			unsigned int u32;
		} sw_region0_scl_factor_yrgb;
		struct { 
			unsigned int reserve_data[8];
		} reserve_reg_56_60;
		union region0_scl_offset_u { 
			struct region0_scl_offset_s { 
				unsigned int region0_yrgb_xscl_offset: 8;
				unsigned int region0_yrgb_yscl_offset: 8;
				unsigned int reserve_0: 16;
			} bits;
			unsigned int u32;
		} sw_region0_scl_offset;
		union region1_mst_ctl_u { 
			struct region1_mst_ctl_s { 
				unsigned int region1_mst_en: 1;
				unsigned int region1_data_fmt: 5;
				unsigned int reserve_0: 1;
				unsigned int region1_argb5551_en: 1;
				unsigned int region1_yrgb_2gt: 1;
				unsigned int region1_yrgb_4gt: 1;
				unsigned int region1_cbcr_2gt: 1;
				unsigned int region1_cbcr_4gt: 1;
				unsigned int region1_dither_up_en: 1;
				unsigned int region1_alpha_swap: 1;
				unsigned int region1_rb_swap: 1;
				unsigned int region1_mid_swap: 1;
				unsigned int region1_uv_swap: 1;
				unsigned int region1_yuv_clip: 1;
				unsigned int region1_rg_swap: 1;
				unsigned int reserve_1: 1;
				unsigned int region1_avg_en: 1;
				unsigned int region1_xgt_en: 1;
				unsigned int region1_xgt_mode: 2;
				unsigned int reserve_2: 8;
			} bits;
			unsigned int u32;
		} sw_region1_mst_ctl;
		union region1_mst_yrgb_u { 
			struct region1_mst_yrgb_s { 
				unsigned int region1_yrgb_mst: 32;
			} bits;
			unsigned int u32;
		} sw_region1_mst_yrgb;
		union region1_mst_cbcr_u { 
			struct region1_mst_cbcr_s { 
				unsigned int region1_cbcr_mst: 32;
			} bits;
			unsigned int u32;
		} sw_region1_mst_cbcr;
		union region1_vir_u { 
			struct region1_vir_s { 
				unsigned int region1_vir_stride: 16;
				unsigned int region1_vir_stride_uv: 16;
			} bits;
			unsigned int u32;
		} sw_region1_vir;
		union region1_act_info_u { 
			struct region1_act_info_s { 
				unsigned int region1_act_width: 13;
				unsigned int reserve_0: 3;
				unsigned int region1_act_heigth: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region1_act_info;
		union region1_dsp_info_u { 
			struct region1_dsp_info_s { 
				unsigned int region1_dsp_width: 13;
				unsigned int reserve_0: 3;
				unsigned int region1_dsp_height: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region1_dsp_info;
		union region1_dsp_offset_u { 
			struct region1_dsp_offset_s { 
				unsigned int region1_dsp_xoff: 13;
				unsigned int reserve_0: 3;
				unsigned int region1_dsp_yoff: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region1_dsp_offset;
		union region1_scl_ctrl_u { 
			struct region1_scl_ctrl_s { 
				unsigned int region1_yrgb_xsu_en: 1;
				unsigned int region1_yrgb_xsd_en: 1;
				unsigned int region1_yrgb_xscl_mode: 2;
				unsigned int region1_yrgb_ysu_en: 1;
				unsigned int region1_yrgb_ysd_en: 1;
				unsigned int region1_yrgb_yscl_mode: 2;
				unsigned int reserve_0: 8;
				unsigned int region1_xsu_bic_mode: 2;
				unsigned int reserve_1: 14;
			} bits;
			unsigned int u32;
		} sw_region1_scl_ctrl;
		union region1_scl_factor_yrgb_u { 
			struct region1_scl_factor_yrgb_s { 
				unsigned int region1_yrgb_xfactor: 16;
				unsigned int region1_yrgb_yfactor: 16;
			} bits;
			unsigned int u32;
		} sw_region1_scl_factor_yrgb;
		struct { 
			unsigned int reserve_data[8];
		} reserve_reg_104_108;
		union region1_scl_offset_u { 
			struct region1_scl_offset_s { 
				unsigned int region1_yrgb_xscl_offset: 8;
				unsigned int region1_yrgb_yscl_offset: 8;
				unsigned int reserve_0: 16;
			} bits;
			unsigned int u32;
		} sw_region1_scl_offset;
		union region2_mst_ctl_u { 
			struct region2_mst_ctl_s { 
				unsigned int region2_mst_en: 1;
				unsigned int region2_data_fmt: 5;
				unsigned int reserve_0: 1;
				unsigned int region2_argb5551_en: 1;
				unsigned int region2_yrgb_2gt: 1;
				unsigned int region2_yrgb_4gt: 1;
				unsigned int region2_cbcr_2gt: 1;
				unsigned int region2_cbcr_4gt: 1;
				unsigned int region2_dither_up_en: 1;
				unsigned int region2_alpha_swap: 1;
				unsigned int region2_rb_swap: 1;
				unsigned int region2_mid_swap: 1;
				unsigned int region2_uv_swap: 1;
				unsigned int region2_yuv_clip: 1;
				unsigned int region2_rg_swap: 1;
				unsigned int reserve_1: 1;
				unsigned int region2_avg_en: 1;
				unsigned int region2_xgt_en: 1;
				unsigned int region2_xgt_mode: 2;
				unsigned int reserve_2: 8;
			} bits;
			unsigned int u32;
		} sw_region2_mst_ctl;
		union region2_mst_yrgb_u { 
			struct region2_mst_yrgb_s { 
				unsigned int region2_yrgb_mst: 32;
			} bits;
			unsigned int u32;
		} sw_region2_mst_yrgb;
		union region2_mst_cbcr_u { 
			struct region2_mst_cbcr_s { 
				unsigned int region2_cbcr_mst: 32;
			} bits;
			unsigned int u32;
		} sw_region2_mst_cbcr;
		union region2_vir_u { 
			struct region2_vir_s { 
				unsigned int region2_vir_stride: 16;
				unsigned int region2_vir_stride_uv: 16;
			} bits;
			unsigned int u32;
		} sw_region2_vir;
		union region2_act_info_u { 
			struct region2_act_info_s { 
				unsigned int region2_act_width: 13;
				unsigned int reserve_0: 3;
				unsigned int region2_act_heigth: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region2_act_info;
		union region2_dsp_info_u { 
			struct region2_dsp_info_s { 
				unsigned int region2_dsp_width: 13;
				unsigned int reserve_0: 3;
				unsigned int region2_dsp_height: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region2_dsp_info;
		union region2_dsp_offset_u { 
			struct region2_dsp_offset_s { 
				unsigned int region2_dsp_xoff: 13;
				unsigned int reserve_0: 3;
				unsigned int region2_dsp_yoff: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region2_dsp_offset;
		union region2_scl_ctrl_u { 
			struct region2_scl_ctrl_s { 
				unsigned int region2_yrgb_xsu_en: 1;
				unsigned int region2_yrgb_xsd_en: 1;
				unsigned int region2_yrgb_xscl_mode: 2;
				unsigned int region2_yrgb_ysu_en: 1;
				unsigned int region2_yrgb_ysd_en: 1;
				unsigned int region2_yrgb_yscl_mode: 2;
				unsigned int reserve_0: 8;
				unsigned int region2_xsu_bic_mode: 2;
				unsigned int reserve_1: 14;
			} bits;
			unsigned int u32;
		} sw_region2_scl_ctrl;
		union region2_scl_factor_yrgb_u { 
			struct region2_scl_factor_yrgb_s { 
				unsigned int region2_yrgb_xfactor: 16;
				unsigned int region2_yrgb_yfactor: 16;
			} bits;
			unsigned int u32;
		} sw_region2_scl_factor_yrgb;
		struct { 
			unsigned int reserve_data[8];
		} reserve_reg_152_156;
		union region2_scl_offset_u { 
			struct region2_scl_offset_s { 
				unsigned int region2_yrgb_xscl_offset: 8;
				unsigned int region2_yrgb_yscl_offset: 8;
				unsigned int reserve_0: 16;
			} bits;
			unsigned int u32;
		} sw_region2_scl_offset;
		union region3_mst_ctl_u { 
			struct region3_mst_ctl_s { 
				unsigned int region3_mst_en: 1;
				unsigned int region3_data_fmt: 5;
				unsigned int reserve_0: 2;
				unsigned int region3_yrgb_2gt: 1;
				unsigned int region3_yrgb_4gt: 1;
				unsigned int region3_cbcr_2gt: 1;
				unsigned int region3_cbcr_4gt: 1;
				unsigned int region3_dither_up_en: 1;
				unsigned int region3_alpha_swap: 1;
				unsigned int region3_rb_swap: 1;
				unsigned int region3_mid_swap: 1;
				unsigned int region3_uv_swap: 1;
				unsigned int region3_yuv_clip: 1;
				unsigned int region3_rg_swap: 1;
				unsigned int reserve_1: 1;
				unsigned int region3_avg_en: 1;
				unsigned int region3_xgt_en: 1;
				unsigned int region3_xgt_mode: 2;
				unsigned int reserve_2: 8;
			} bits;
			unsigned int u32;
		} sw_region3_mst_ctl;
		union region3_mst_yrgb_u { 
			struct region3_mst_yrgb_s { 
				unsigned int region3_yrgb_mst: 32;
			} bits;
			unsigned int u32;
		} sw_region3_mst_yrgb;
		union region3_mst_cbcr_u { 
			struct region3_mst_cbcr_s { 
				unsigned int region3_cbcr_mst: 32;
			} bits;
			unsigned int u32;
		} sw_region3_mst_cbcr;
		union region3_vir_u { 
			struct region3_vir_s { 
				unsigned int region3_vir_stride: 16;
				unsigned int region3_vir_stride_uv: 16;
			} bits;
			unsigned int u32;
		} sw_region3_vir;
		union region3_act_info_u { 
			struct region3_act_info_s { 
				unsigned int region3_act_width: 13;
				unsigned int reserve_0: 3;
				unsigned int region3_act_heigth: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region3_act_info;
		union region3_dsp_info_u { 
			struct region3_dsp_info_s { 
				unsigned int region3_dsp_width: 13;
				unsigned int reserve_0: 3;
				unsigned int region3_dsp_height: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region3_dsp_info;
		union region3_dsp_offset_u { 
			struct region3_dsp_offset_s { 
				unsigned int region3_dsp_xoff: 13;
				unsigned int reserve_0: 3;
				unsigned int region3_dsp_yoff: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region3_dsp_offset;
		union region3_scl_ctrl_u { 
			struct region3_scl_ctrl_s { 
				unsigned int region3_yrgb_xsu_en: 1;
				unsigned int region3_yrgb_xsd_en: 1;
				unsigned int region3_yrgb_xscl_mode: 2;
				unsigned int region3_yrgb_ysu_en: 1;
				unsigned int region3_yrgb_ysd_en: 1;
				unsigned int region3_yrgb_yscl_mode: 2;
				unsigned int reserve_0: 8;
				unsigned int region3_xsu_bic_mode: 2;
				unsigned int reserve_1: 14;
			} bits;
			unsigned int u32;
		} sw_region3_scl_ctrl;
		union region3_scl_factor_yrgb_u { 
			struct region3_scl_factor_yrgb_s { 
				unsigned int region3_yrgb_xfactor: 16;
				unsigned int region3_yrgb_yfactor: 16;
			} bits;
			unsigned int u32;
		} sw_region3_scl_factor_yrgb;
		struct { 
			unsigned int reserve_data[8];
		} reserve_reg_200_204;
		union region3_scl_offset_u { 
			struct region3_scl_offset_s { 
				unsigned int region3_yrgb_xscl_offset: 8;
				unsigned int region3_yrgb_yscl_offset: 8;
				unsigned int reserve_0: 16;
			} bits;
			unsigned int u32;
		} sw_region3_scl_offset;
		union esmart_key_ctrl_u { 
			struct esmart_key_ctrl_s { 
				unsigned int esmart_b_key_value: 10;
				unsigned int esmart_g_key_value: 10;
				unsigned int esmart_r_key_value: 10;
				unsigned int reserve_0: 1;
				unsigned int esmart_key_en: 1;
			} bits;
			unsigned int u32;
		} sw_esmart_key_ctrl;
		union esmart_bg_en_u { 
			struct esmart_bg_en_s { 
				unsigned int esmart_b_value: 10;
				unsigned int esmart_g_value: 10;
				unsigned int esmart_r_value: 10;
				unsigned int reserve_0: 1;
				unsigned int esmart_bg_en: 1;
			} bits;
			unsigned int u32;
		} sw_esmart_bg_en;
		union esmart_alpha_map_u { 
			struct esmart_alpha_map_s { 
				unsigned int alpha_0_map: 8;
				unsigned int alpha_1_map: 8;
				unsigned int reserve_0: 15;
				unsigned int alpha_map_en: 1;
			} bits;
			unsigned int u32;
		} sw_esmart_alpha_map;
		struct { 
			unsigned int reserve_data[24];
		} reserve_reg_224_244;
		union esmart_port_sel_imd_u { 
			struct esmart_port_sel_imd_s { 
				unsigned int esmart_port_sel: 2;
				unsigned int reserve_0: 30;
			} bits;
			unsigned int u32;
		} sw_esmart_port_sel_imd;
		union esmart_dly_num_u { 
			struct esmart_dly_num_s { 
				unsigned int esmart_dly_num: 8;
				unsigned int reserve_0: 24;
			} bits;
			unsigned int u32;
		} sw_esmart_dly_num;
	} regs;
	unsigned int p_reg_addr[48];
}esmart2_0x27d01c00_t;

typedef union esmart3_0x27d01e00_u {
	struct esmart3_0x27d01e00_s {
		union esmart_ctrl0_u { 
			struct esmart_ctrl0_s { 
				unsigned int esmart_yuv2rgb_en: 1;
				unsigned int esmart_rgb2yuv_en: 1;
				unsigned int esmart_csc_mode: 2;
				unsigned int esmart_8bpp_lut_en: 1;
				unsigned int esmart_8bpp_alpha_en: 1;
				unsigned int reserve_0: 2;
				unsigned int esmart_mid_swap: 1;
				unsigned int esmart_endian_swap: 1;
				unsigned int reserve_1: 2;
				unsigned int esmart_scl_num: 2;
				unsigned int reserve_2: 10;
				unsigned int esmart_yuv2rgb_force_en: 1;
				unsigned int reserve_3: 6;
				unsigned int esmart_frm_resetn_en: 1;
			} bits;
			unsigned int u32;
		} sw_esmart_ctrl0;
		union esmart_ctrl1_u { 
			struct esmart_ctrl1_s { 
				unsigned int esmart_esmart_axi_rlen: 2;
				unsigned int esmart_yrgb_gather_en: 1;
				unsigned int esmart_cbcr_gather_en: 1;
				unsigned int esmart_yrgb_rid: 5;
				unsigned int reserve_0: 3;
				unsigned int esmart_cbcr_rid: 5;
				unsigned int reserve_1: 3;
				unsigned int esmart_yrgb_gather_num: 4;
				unsigned int esmart_cbcr_gather_num: 4;
				unsigned int esmart_dma_rreq_hurry_en: 1;
				unsigned int esmart_dma_rreq_thold: 2;
				unsigned int esmart_ymir_en: 1;
			} bits;
			unsigned int u32;
		} sw_esmart_ctrl1;
		union esmart_axi_ctrl_imd_u { 
			struct esmart_axi_ctrl_imd_s { 
				unsigned int esmart_dma_sop: 1;
				unsigned int esmart_axi_sel: 1;
				unsigned int esmart_mmu_bypass: 1;
				unsigned int esmart_outstanding_en: 1;
				unsigned int esmart_outstanding_num: 4;
				unsigned int esmart_auto_gating_en: 1;
				unsigned int reserve_0: 7;
				unsigned int esmart_dma_4k_addr_opt: 1;
				unsigned int reserve_1: 15;
			} bits;
			unsigned int u32;
		} sw_esmart_axi_ctrl_imd;
		struct { 
			unsigned int reserve_data[8];
		} reserve_reg_12_16;
		union region0_mst_ctl_u { 
			struct region0_mst_ctl_s { 
				unsigned int region0_mst_en: 1;
				unsigned int region0_data_fmt: 5;
				unsigned int reserve_0: 1;
				unsigned int region0_argb5551_en: 1;
				unsigned int region0_yrgb_2gt: 1;
				unsigned int region0_yrgb_4gt: 1;
				unsigned int region0_cbcr_2gt: 1;
				unsigned int region0_cbcr_4gt: 1;
				unsigned int region0_dither_up_en: 1;
				unsigned int region0_alpha_swap: 1;
				unsigned int region0_rb_swap: 1;
				unsigned int region0_mid_swap: 1;
				unsigned int region0_uv_swap: 1;
				unsigned int region0_yuv_clip: 1;
				unsigned int region0_rg_swap: 1;
				unsigned int reserve_1: 1;
				unsigned int region0_avg_en: 1;
				unsigned int region0_xgt_en: 1;
				unsigned int region0_xgt_mode: 2;
				unsigned int reserve_2: 8;
			} bits;
			unsigned int u32;
		} sw_region0_mst_ctl;
		union region0_mst_yrgb_u { 
			struct region0_mst_yrgb_s { 
				unsigned int region0_yrgb_mst: 32;
			} bits;
			unsigned int u32;
		} sw_region0_mst_yrgb;
		union region0_mst_cbcr_u { 
			struct region0_mst_cbcr_s { 
				unsigned int region0_cbcr_mst: 32;
			} bits;
			unsigned int u32;
		} sw_region0_mst_cbcr;
		union region0_vir_u { 
			struct region0_vir_s { 
				unsigned int region0_vir_stride: 16;
				unsigned int region0_vir_stride_uv: 16;
			} bits;
			unsigned int u32;
		} sw_region0_vir;
		union region0_act_info_u { 
			struct region0_act_info_s { 
				unsigned int region0_act_width: 13;
				unsigned int reserve_0: 3;
				unsigned int region0_act_heigth: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region0_act_info;
		union region0_dsp_info_u { 
			struct region0_dsp_info_s { 
				unsigned int region0_dsp_width: 13;
				unsigned int reserve_0: 3;
				unsigned int region0_dsp_height: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region0_dsp_info;
		union region0_dsp_offset_u { 
			struct region0_dsp_offset_s { 
				unsigned int region0_dsp_xoff: 13;
				unsigned int reserve_0: 3;
				unsigned int region0_dsp_yoff: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region0_dsp_offset;
		union region0_scl_ctrl_u { 
			struct region0_scl_ctrl_s { 
				unsigned int region0_yrgb_xsu_en: 1;
				unsigned int region0_yrgb_xsd_en: 1;
				unsigned int region0_yrgb_xscl_mode: 2;
				unsigned int region0_yrgb_ysu_en: 1;
				unsigned int region0_yrgb_ysd_en: 1;
				unsigned int region0_yrgb_yscl_mode: 2;
				unsigned int reserve_0: 8;
				unsigned int region0_xsu_bic_mode: 2;
				unsigned int reserve_1: 14;
			} bits;
			unsigned int u32;
		} sw_region0_scl_ctrl;
		union region0_scl_factor_yrgb_u { 
			struct region0_scl_factor_yrgb_s { 
				unsigned int region0_yrgb_xfactor: 16;
				unsigned int region0_yrgb_yfactor: 16;
			} bits;
			unsigned int u32;
		} sw_region0_scl_factor_yrgb;
		struct { 
			unsigned int reserve_data[8];
		} reserve_reg_56_60;
		union region0_scl_offset_u { 
			struct region0_scl_offset_s { 
				unsigned int region0_yrgb_xscl_offset: 8;
				unsigned int region0_yrgb_yscl_offset: 8;
				unsigned int reserve_0: 16;
			} bits;
			unsigned int u32;
		} sw_region0_scl_offset;
		union region1_mst_ctl_u { 
			struct region1_mst_ctl_s { 
				unsigned int region1_mst_en: 1;
				unsigned int region1_data_fmt: 5;
				unsigned int reserve_0: 1;
				unsigned int region1_argb5551_en: 1;
				unsigned int region1_yrgb_2gt: 1;
				unsigned int region1_yrgb_4gt: 1;
				unsigned int region1_cbcr_2gt: 1;
				unsigned int region1_cbcr_4gt: 1;
				unsigned int region1_dither_up_en: 1;
				unsigned int region1_alpha_swap: 1;
				unsigned int region1_rb_swap: 1;
				unsigned int region1_mid_swap: 1;
				unsigned int region1_uv_swap: 1;
				unsigned int region1_yuv_clip: 1;
				unsigned int region1_rg_swap: 1;
				unsigned int reserve_1: 1;
				unsigned int region1_avg_en: 1;
				unsigned int region1_xgt_en: 1;
				unsigned int region1_xgt_mode: 2;
				unsigned int reserve_2: 8;
			} bits;
			unsigned int u32;
		} sw_region1_mst_ctl;
		union region1_mst_yrgb_u { 
			struct region1_mst_yrgb_s { 
				unsigned int region1_yrgb_mst: 32;
			} bits;
			unsigned int u32;
		} sw_region1_mst_yrgb;
		union region1_mst_cbcr_u { 
			struct region1_mst_cbcr_s { 
				unsigned int region1_cbcr_mst: 32;
			} bits;
			unsigned int u32;
		} sw_region1_mst_cbcr;
		union region1_vir_u { 
			struct region1_vir_s { 
				unsigned int region1_vir_stride: 16;
				unsigned int region1_vir_stride_uv: 16;
			} bits;
			unsigned int u32;
		} sw_region1_vir;
		union region1_act_info_u { 
			struct region1_act_info_s { 
				unsigned int region1_act_width: 13;
				unsigned int reserve_0: 3;
				unsigned int region1_act_heigth: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region1_act_info;
		union region1_dsp_info_u { 
			struct region1_dsp_info_s { 
				unsigned int region1_dsp_width: 13;
				unsigned int reserve_0: 3;
				unsigned int region1_dsp_height: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region1_dsp_info;
		union region1_dsp_offset_u { 
			struct region1_dsp_offset_s { 
				unsigned int region1_dsp_xoff: 13;
				unsigned int reserve_0: 3;
				unsigned int region1_dsp_yoff: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region1_dsp_offset;
		union region1_scl_ctrl_u { 
			struct region1_scl_ctrl_s { 
				unsigned int region1_yrgb_xsu_en: 1;
				unsigned int region1_yrgb_xsd_en: 1;
				unsigned int region1_yrgb_xscl_mode: 2;
				unsigned int region1_yrgb_ysu_en: 1;
				unsigned int region1_yrgb_ysd_en: 1;
				unsigned int region1_yrgb_yscl_mode: 2;
				unsigned int reserve_0: 8;
				unsigned int region1_xsu_bic_mode: 2;
				unsigned int reserve_1: 14;
			} bits;
			unsigned int u32;
		} sw_region1_scl_ctrl;
		union region1_scl_factor_yrgb_u { 
			struct region1_scl_factor_yrgb_s { 
				unsigned int region1_yrgb_xfactor: 16;
				unsigned int region1_yrgb_yfactor: 16;
			} bits;
			unsigned int u32;
		} sw_region1_scl_factor_yrgb;
		struct { 
			unsigned int reserve_data[8];
		} reserve_reg_104_108;
		union region1_scl_offset_u { 
			struct region1_scl_offset_s { 
				unsigned int region1_yrgb_xscl_offset: 8;
				unsigned int region1_yrgb_yscl_offset: 8;
				unsigned int reserve_0: 16;
			} bits;
			unsigned int u32;
		} sw_region1_scl_offset;
		union region2_mst_ctl_u { 
			struct region2_mst_ctl_s { 
				unsigned int region2_mst_en: 1;
				unsigned int region2_data_fmt: 5;
				unsigned int reserve_0: 1;
				unsigned int region2_argb5551_en: 1;
				unsigned int region2_yrgb_2gt: 1;
				unsigned int region2_yrgb_4gt: 1;
				unsigned int region2_cbcr_2gt: 1;
				unsigned int region2_cbcr_4gt: 1;
				unsigned int region2_dither_up_en: 1;
				unsigned int region2_alpha_swap: 1;
				unsigned int region2_rb_swap: 1;
				unsigned int region2_mid_swap: 1;
				unsigned int region2_uv_swap: 1;
				unsigned int region2_yuv_clip: 1;
				unsigned int region2_rg_swap: 1;
				unsigned int reserve_1: 1;
				unsigned int region2_avg_en: 1;
				unsigned int region2_xgt_en: 1;
				unsigned int region2_xgt_mode: 2;
				unsigned int reserve_2: 8;
			} bits;
			unsigned int u32;
		} sw_region2_mst_ctl;
		union region2_mst_yrgb_u { 
			struct region2_mst_yrgb_s { 
				unsigned int region2_yrgb_mst: 32;
			} bits;
			unsigned int u32;
		} sw_region2_mst_yrgb;
		union region2_mst_cbcr_u { 
			struct region2_mst_cbcr_s { 
				unsigned int region2_cbcr_mst: 32;
			} bits;
			unsigned int u32;
		} sw_region2_mst_cbcr;
		union region2_vir_u { 
			struct region2_vir_s { 
				unsigned int region2_vir_stride: 16;
				unsigned int region2_vir_stride_uv: 16;
			} bits;
			unsigned int u32;
		} sw_region2_vir;
		union region2_act_info_u { 
			struct region2_act_info_s { 
				unsigned int region2_act_width: 13;
				unsigned int reserve_0: 3;
				unsigned int region2_act_heigth: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region2_act_info;
		union region2_dsp_info_u { 
			struct region2_dsp_info_s { 
				unsigned int region2_dsp_width: 13;
				unsigned int reserve_0: 3;
				unsigned int region2_dsp_height: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region2_dsp_info;
		union region2_dsp_offset_u { 
			struct region2_dsp_offset_s { 
				unsigned int region2_dsp_xoff: 13;
				unsigned int reserve_0: 3;
				unsigned int region2_dsp_yoff: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region2_dsp_offset;
		union region2_scl_ctrl_u { 
			struct region2_scl_ctrl_s { 
				unsigned int region2_yrgb_xsu_en: 1;
				unsigned int region2_yrgb_xsd_en: 1;
				unsigned int region2_yrgb_xscl_mode: 2;
				unsigned int region2_yrgb_ysu_en: 1;
				unsigned int region2_yrgb_ysd_en: 1;
				unsigned int region2_yrgb_yscl_mode: 2;
				unsigned int reserve_0: 8;
				unsigned int region2_xsu_bic_mode: 2;
				unsigned int reserve_1: 14;
			} bits;
			unsigned int u32;
		} sw_region2_scl_ctrl;
		union region2_scl_factor_yrgb_u { 
			struct region2_scl_factor_yrgb_s { 
				unsigned int region2_yrgb_xfactor: 16;
				unsigned int region2_yrgb_yfactor: 16;
			} bits;
			unsigned int u32;
		} sw_region2_scl_factor_yrgb;
		struct { 
			unsigned int reserve_data[8];
		} reserve_reg_152_156;
		union region2_scl_offset_u { 
			struct region2_scl_offset_s { 
				unsigned int region2_yrgb_xscl_offset: 8;
				unsigned int region2_yrgb_yscl_offset: 8;
				unsigned int reserve_0: 16;
			} bits;
			unsigned int u32;
		} sw_region2_scl_offset;
		union region3_mst_ctl_u { 
			struct region3_mst_ctl_s { 
				unsigned int region3_mst_en: 1;
				unsigned int region3_data_fmt: 5;
				unsigned int reserve_0: 2;
				unsigned int region3_yrgb_2gt: 1;
				unsigned int region3_yrgb_4gt: 1;
				unsigned int region3_cbcr_2gt: 1;
				unsigned int region3_cbcr_4gt: 1;
				unsigned int region3_dither_up_en: 1;
				unsigned int region3_alpha_swap: 1;
				unsigned int region3_rb_swap: 1;
				unsigned int region3_mid_swap: 1;
				unsigned int region3_uv_swap: 1;
				unsigned int region3_yuv_clip: 1;
				unsigned int region3_rg_swap: 1;
				unsigned int reserve_1: 1;
				unsigned int region3_avg_en: 1;
				unsigned int region3_xgt_en: 1;
				unsigned int region3_xgt_mode: 2;
				unsigned int reserve_2: 8;
			} bits;
			unsigned int u32;
		} sw_region3_mst_ctl;
		union region3_mst_yrgb_u { 
			struct region3_mst_yrgb_s { 
				unsigned int region3_yrgb_mst: 32;
			} bits;
			unsigned int u32;
		} sw_region3_mst_yrgb;
		union region3_mst_cbcr_u { 
			struct region3_mst_cbcr_s { 
				unsigned int region3_cbcr_mst: 32;
			} bits;
			unsigned int u32;
		} sw_region3_mst_cbcr;
		union region3_vir_u { 
			struct region3_vir_s { 
				unsigned int region3_vir_stride: 16;
				unsigned int region3_vir_stride_uv: 16;
			} bits;
			unsigned int u32;
		} sw_region3_vir;
		union region3_act_info_u { 
			struct region3_act_info_s { 
				unsigned int region3_act_width: 13;
				unsigned int reserve_0: 3;
				unsigned int region3_act_heigth: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region3_act_info;
		union region3_dsp_info_u { 
			struct region3_dsp_info_s { 
				unsigned int region3_dsp_width: 13;
				unsigned int reserve_0: 3;
				unsigned int region3_dsp_height: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region3_dsp_info;
		union region3_dsp_offset_u { 
			struct region3_dsp_offset_s { 
				unsigned int region3_dsp_xoff: 13;
				unsigned int reserve_0: 3;
				unsigned int region3_dsp_yoff: 13;
				unsigned int reserve_1: 3;
			} bits;
			unsigned int u32;
		} sw_region3_dsp_offset;
		union region3_scl_ctrl_u { 
			struct region3_scl_ctrl_s { 
				unsigned int region3_yrgb_xsu_en: 1;
				unsigned int region3_yrgb_xsd_en: 1;
				unsigned int region3_yrgb_xscl_mode: 2;
				unsigned int region3_yrgb_ysu_en: 1;
				unsigned int region3_yrgb_ysd_en: 1;
				unsigned int region3_yrgb_yscl_mode: 2;
				unsigned int reserve_0: 8;
				unsigned int region3_xsu_bic_mode: 2;
				unsigned int reserve_1: 14;
			} bits;
			unsigned int u32;
		} sw_region3_scl_ctrl;
		union region3_scl_factor_yrgb_u { 
			struct region3_scl_factor_yrgb_s { 
				unsigned int region3_yrgb_xfactor: 16;
				unsigned int region3_yrgb_yfactor: 16;
			} bits;
			unsigned int u32;
		} sw_region3_scl_factor_yrgb;
		struct { 
			unsigned int reserve_data[8];
		} reserve_reg_200_204;
		union region3_scl_offset_u { 
			struct region3_scl_offset_s { 
				unsigned int region3_yrgb_xscl_offset: 8;
				unsigned int region3_yrgb_yscl_offset: 8;
				unsigned int reserve_0: 16;
			} bits;
			unsigned int u32;
		} sw_region3_scl_offset;
		union esmart_key_ctrl_u { 
			struct esmart_key_ctrl_s { 
				unsigned int esmart_b_key_value: 10;
				unsigned int esmart_g_key_value: 10;
				unsigned int esmart_r_key_value: 10;
				unsigned int reserve_0: 1;
				unsigned int esmart_key_en: 1;
			} bits;
			unsigned int u32;
		} sw_esmart_key_ctrl;
		union esmart_bg_en_u { 
			struct esmart_bg_en_s { 
				unsigned int esmart_b_value: 10;
				unsigned int esmart_g_value: 10;
				unsigned int esmart_r_value: 10;
				unsigned int reserve_0: 1;
				unsigned int esmart_bg_en: 1;
			} bits;
			unsigned int u32;
		} sw_esmart_bg_en;
		union esmart_alpha_map_u { 
			struct esmart_alpha_map_s { 
				unsigned int alpha_0_map: 8;
				unsigned int alpha_1_map: 8;
				unsigned int reserve_0: 15;
				unsigned int alpha_map_en: 1;
			} bits;
			unsigned int u32;
		} sw_esmart_alpha_map;
		struct { 
			unsigned int reserve_data[24];
		} reserve_reg_224_244;
		union esmart_port_sel_imd_u { 
			struct esmart_port_sel_imd_s { 
				unsigned int esmart_port_sel: 2;
				unsigned int reserve_0: 30;
			} bits;
			unsigned int u32;
		} sw_esmart_port_sel_imd;
		union esmart_dly_num_u { 
			struct esmart_dly_num_s { 
				unsigned int esmart_dly_num: 8;
				unsigned int reserve_0: 24;
			} bits;
			unsigned int u32;
		} sw_esmart_dly_num;
	} regs;
	unsigned int p_reg_addr[48];
}esmart3_0x27d01e00_t;

typedef union hdr_vivid_0x27d02000_u {
	struct hdr_vivid_0x27d02000_s {
		union hdr_lut_ctrl_u { 
			struct hdr_lut_ctrl_s { 
				unsigned int hdr_lut_update_en: 1;
				unsigned int hdr_lut_mode: 1;
				unsigned int reserve_0: 30;
			} bits;
			unsigned int u32;
		} sw_hdr_lut_ctrl;
		union hdr_lut_mst_u { 
			struct hdr_lut_mst_s { 
				unsigned int hdr_lut_mst: 32;
			} bits;
			unsigned int u32;
		} sw_hdr_lut_mst;
		union hdr_lut_status_u { 
			struct hdr_lut_status_s { 
				unsigned int hdr_lut_fetch_done: 1;
				unsigned int reserve_0: 31;
			} bits;
			unsigned int u32;
		} sw_hdr_lut_status;
		struct { 
			unsigned int reserve_data[8];
		} reserve_reg_12_16;
		union sdr2hdr_ctrl_u { 
			struct sdr2hdr_ctrl_s { 
				unsigned int sdr2hdr_en: 1;
				unsigned int sdr2hdr_gating_en: 1;
				unsigned int sdr2hdr_bypass_en: 1;
				unsigned int sdr2hdr_dstmode: 1;
				unsigned int reserve_0: 28;
			} bits;
			unsigned int u32;
		} sw_sdr2hdr_ctrl;
		union sdr_cfg_coe0_u { 
			struct sdr_cfg_coe0_s { 
				unsigned int sdr_s_fix: 12;
				unsigned int reserve_0: 4;
				unsigned int sdr_r_fix: 12;
				unsigned int reserve_1: 4;
			} bits;
			unsigned int u32;
		} sw_sdr_cfg_coe0;
		union sdr_cfg_coe1_u { 
			struct sdr_cfg_coe1_s { 
				unsigned int sdr_t_fix: 14;
				unsigned int reserve_0: 18;
			} bits;
			unsigned int u32;
		} sw_sdr_cfg_coe1;
		union sdr_csc_coe00_01_u { 
			struct sdr_csc_coe00_01_s { 
				unsigned int coe00: 14;
				unsigned int reserve_0: 2;
				unsigned int coe01: 14;
				unsigned int reserve_1: 2;
			} bits;
			unsigned int u32;
		} sw_sdr_csc_coe00_01;
		union sdr_csc_coe02_10_u { 
			struct sdr_csc_coe02_10_s { 
				unsigned int coe02: 14;
				unsigned int reserve_0: 2;
				unsigned int coe10: 14;
				unsigned int reserve_1: 2;
			} bits;
			unsigned int u32;
		} sw_sdr_csc_coe02_10;
		union sdr_csc_coe11_12_u { 
			struct sdr_csc_coe11_12_s { 
				unsigned int coe11: 14;
				unsigned int reserve_0: 2;
				unsigned int coe12: 14;
				unsigned int reserve_1: 2;
			} bits;
			unsigned int u32;
		} sw_sdr_csc_coe11_12;
		union sdr_csc_coe20_21_u { 
			struct sdr_csc_coe20_21_s { 
				unsigned int coe20: 14;
				unsigned int reserve_0: 2;
				unsigned int coe21: 14;
				unsigned int reserve_1: 2;
			} bits;
			unsigned int u32;
		} sw_sdr_csc_coe20_21;
		union sdr_csc_coe22_u { 
			struct sdr_csc_coe22_s { 
				unsigned int coe22: 14;
				unsigned int reserve_0: 18;
			} bits;
			unsigned int u32;
		} sw_sdr_csc_coe22;
		struct { 
			unsigned int reserve_data[16];
		} reserve_reg_52_64;
		union hdrvivid_ctrl_u { 
			struct hdrvivid_ctrl_s { 
				unsigned int hdrvivid_en: 1;
				unsigned int hdrvivid_gating_en: 1;
				unsigned int hdrvivid_bypass_en: 1;
				unsigned int path_mode: 3;
				unsigned int dstgamut: 1;
				unsigned int reserve_0: 1;
				unsigned int pqmode_max_y: 1;
				unsigned int sca_bypass_en: 1;
				unsigned int reserve_1: 22;
			} bits;
			unsigned int u32;
		} sw_hdrvivid_ctrl;
		union hdr_pq_gamma_u { 
			struct hdr_pq_gamma_s { 
				unsigned int pq_gamma_b: 8;
				unsigned int reserve_0: 8;
				unsigned int pq_gamma_k: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_hdr_pq_gamma;
		union hlg_rfix_scalefac_u { 
			struct hlg_rfix_scalefac_s { 
				unsigned int r_fix: 12;
				unsigned int reserve_0: 4;
				unsigned int scalefac: 10;
				unsigned int reserve_1: 6;
			} bits;
			unsigned int u32;
		} sw_hlg_rfix_scalefac;
		union hlg_maxluma_u { 
			struct hlg_maxluma_s { 
				unsigned int maxdstluma: 12;
				unsigned int reserve_0: 4;
				unsigned int maxsetluma: 12;
				unsigned int reserve_1: 4;
			} bits;
			unsigned int u32;
		} sw_hlg_maxluma;
		union hlg_r_tm_lin2non_u { 
			struct hlg_r_tm_lin2non_s { 
				unsigned int r_tm_lin2non: 10;
				unsigned int reserve_0: 22;
			} bits;
			unsigned int u32;
		} sw_hlg_r_tm_lin2non;
		union hdr_csc_coe00_01_u { 
			struct hdr_csc_coe00_01_s { 
				unsigned int coe00: 16;
				unsigned int coe01: 16;
			} bits;
			unsigned int u32;
		} sw_hdr_csc_coe00_01;
		union hdr_csc_coe02_10_u { 
			struct hdr_csc_coe02_10_s { 
				unsigned int coe02: 16;
				unsigned int coe10: 16;
			} bits;
			unsigned int u32;
		} sw_hdr_csc_coe02_10;
		union hdr_csc_coe11_12_u { 
			struct hdr_csc_coe11_12_s { 
				unsigned int coe11: 16;
				unsigned int coe12: 16;
			} bits;
			unsigned int u32;
		} sw_hdr_csc_coe11_12;
		union hdr_csc_coe20_21_u { 
			struct hdr_csc_coe20_21_s { 
				unsigned int coe20: 16;
				unsigned int coe21: 16;
			} bits;
			unsigned int u32;
		} sw_hdr_csc_coe20_21;
		union hdr_csc_coe22_u { 
			struct hdr_csc_coe22_s { 
				unsigned int coe22: 16;
				unsigned int reserve_0: 16;
			} bits;
			unsigned int u32;
		} sw_hdr_csc_coe22;
		struct { 
			unsigned int reserve_data[24];
		} reserve_reg_108_128;
		union hdr_debug_ctrl_u { 
			struct hdr_debug_ctrl_s { 
				unsigned int sw_h_active: 12;
				unsigned int reserve_0: 3;
				unsigned int debug_en: 1;
				unsigned int sw_v_active: 12;
				unsigned int debug_mode_sel: 4;
			} bits;
			unsigned int u32;
		} sw_hdr_debug_ctrl;
		union debug_point0_cfg_u { 
			struct debug_point0_cfg_s { 
				unsigned int debug_point0_h: 12;
				unsigned int reserve_0: 4;
				unsigned int debug_point0_v: 12;
				unsigned int reserve_1: 4;
			} bits;
			unsigned int u32;
		} sw_debug_point0_cfg;
		union debug_point1_cfg_u { 
			struct debug_point1_cfg_s { 
				unsigned int debug_point1_h: 12;
				unsigned int reserve_0: 4;
				unsigned int debug_point1_v: 12;
				unsigned int reserve_1: 4;
			} bits;
			unsigned int u32;
		} sw_debug_point1_cfg;
		union debug_point0_r0_u { 
			struct debug_point0_r0_s { 
				unsigned int debug_point0_r0: 24;
				unsigned int reserve_0: 8;
			} bits;
			unsigned int u32;
		} sw_debug_point0_r0;
		union debug_point0_g0_u { 
			struct debug_point0_g0_s { 
				unsigned int debug_point0_g0: 24;
				unsigned int reserve_0: 8;
			} bits;
			unsigned int u32;
		} sw_debug_point0_g0;
		union debug_point0_b0_u { 
			struct debug_point0_b0_s { 
				unsigned int debug_point0_b0: 24;
				unsigned int reserve_0: 8;
			} bits;
			unsigned int u32;
		} sw_debug_point0_b0;
		union debug_point0_r1_u { 
			struct debug_point0_r1_s { 
				unsigned int debug_point0_r1: 24;
				unsigned int reserve_0: 8;
			} bits;
			unsigned int u32;
		} sw_debug_point0_r1;
		union debug_point0_g1_u { 
			struct debug_point0_g1_s { 
				unsigned int debug_point0_g1: 24;
				unsigned int reserve_0: 8;
			} bits;
			unsigned int u32;
		} sw_debug_point0_g1;
		union debug_point0_b1_u { 
			struct debug_point0_b1_s { 
				unsigned int debug_point0_b1: 24;
				unsigned int reserve_0: 8;
			} bits;
			unsigned int u32;
		} sw_debug_point0_b1;
		union debug_point1_r0_u { 
			struct debug_point1_r0_s { 
				unsigned int debug_point0_r0: 24;
				unsigned int reserve_0: 8;
			} bits;
			unsigned int u32;
		} sw_debug_point1_r0;
		union debug_point1_g0_u { 
			struct debug_point1_g0_s { 
				unsigned int debug_point1_g0: 24;
				unsigned int reserve_0: 8;
			} bits;
			unsigned int u32;
		} sw_debug_point1_g0;
		union debug_point1_b0_u { 
			struct debug_point1_b0_s { 
				unsigned int debug_point1_b0: 24;
				unsigned int reserve_0: 8;
			} bits;
			unsigned int u32;
		} sw_debug_point1_b0;
		union debug_point1_r1_u { 
			struct debug_point1_r1_s { 
				unsigned int debug_point1_r1: 24;
				unsigned int reserve_0: 8;
			} bits;
			unsigned int u32;
		} sw_debug_point1_r1;
		union debug_point1_g1_u { 
			struct debug_point1_g1_s { 
				unsigned int debug_point1_g1: 24;
				unsigned int reserve_0: 8;
			} bits;
			unsigned int u32;
		} sw_debug_point1_g1;
		union debug_point1_b1_u { 
			struct debug_point1_b1_s { 
				unsigned int debug_point1_b1: 24;
				unsigned int reserve_0: 8;
			} bits;
			unsigned int u32;
		} sw_debug_point1_b1;
		struct { 
			unsigned int reserve_data[128];
		} reserve_reg_192_316;
		union hdr_tone_sca_u { 
			struct hdr_tone_sca_s { 
				unsigned int addr: 1;
				unsigned int reserve_0: 31;
			} bits;
			unsigned int u32;
		} sw_hdr_tone_sca;
		struct { 
			unsigned int reserve_data[1024];
		} reserve_reg_324_1344;
		union hdrgamma_curve_u { 
			struct hdrgamma_curve_s { 
				unsigned int addr: 1;
				unsigned int reserve_0: 31;
			} bits;
			unsigned int u32;
		} sw_hdrgamma_curve;
		struct { 
			unsigned int reserve_data[332];
		} reserve_reg_1352_1680;
		union hdrgamma_mdfvalue_u { 
			struct hdrgamma_mdfvalue_s { 
				unsigned int addr: 1;
				unsigned int reserve_0: 31;
			} bits;
			unsigned int u32;
		} sw_hdrgamma_mdfvalue;
		struct { 
			unsigned int reserve_data[108];
		} reserve_reg_1688_1792;
		union sdrinvgamma_curve_u { 
			struct sdrinvgamma_curve_s { 
				unsigned int addr: 1;
				unsigned int reserve_0: 31;
			} bits;
			unsigned int u32;
		} sw_sdrinvgamma_curve;
		struct { 
			unsigned int reserve_data[284];
		} reserve_reg_1800_2080;
		union sdrinvgamma_startidx_u { 
			struct sdrinvgamma_startidx_s { 
				unsigned int addr: 1;
				unsigned int reserve_0: 31;
			} bits;
			unsigned int u32;
		} sw_sdrinvgamma_startidx;
		struct { 
			unsigned int reserve_data[28];
		} reserve_reg_2088_2112;
		union sdrinvgamma_changeidx_u { 
			struct sdrinvgamma_changeidx_s { 
				unsigned int addr: 1;
				unsigned int reserve_0: 31;
			} bits;
			unsigned int u32;
		} sw_sdrinvgamma_changeidx;
		struct { 
			unsigned int reserve_data[188];
		} reserve_reg_2120_2304;
		union sdr_smgain_u { 
			struct sdr_smgain_s { 
				unsigned int addr: 1;
				unsigned int reserve_0: 31;
			} bits;
			unsigned int u32;
		} sw_sdr_smgain;
	} regs;
	unsigned int p_reg_addr[43];
}hdr_vivid_0x27d02000_t;

typedef union gamma_lut_wraddr_0x27d05000_u {
	struct gamma_lut_wraddr_0x27d05000_s {
	} regs;
	unsigned int p_reg_addr[0];
}gamma_lut_wraddr_0x27d05000_t;

typedef union bpp_lut_wraddr_0x27d06000_u {
	struct bpp_lut_wraddr_0x27d06000_s {
	} regs;
	unsigned int p_reg_addr[0];
}bpp_lut_wraddr_0x27d06000_t;

typedef union acm_0x27d06400_u {
	struct acm_0x27d06400_s {
		union acm_ctrl_u { 
			struct acm_ctrl_s { 
				unsigned int acm_en: 1;
				unsigned int acm_bypass: 1;
				unsigned int debug_en: 1;
				unsigned int reserve_0: 1;
				unsigned int debug_data_sel: 3;
				unsigned int reserve_1: 1;
				unsigned int acm_width: 12;
				unsigned int acm_height: 12;
			} bits;
			unsigned int u32;
		} sw_acm_ctrl;
		union delta_range_u { 
			struct delta_range_s { 
				unsigned int y_gain: 10;
				unsigned int h_gain: 10;
				unsigned int s_gain: 10;
				unsigned int reserve_0: 2;
			} bits;
			unsigned int u32;
		} sw_delta_range;
		union fetch_start_u { 
			struct fetch_start_s { 
				unsigned int fetch_start: 1;
				unsigned int reserve_0: 31;
			} bits;
			unsigned int u32;
		} sw_fetch_start;
		struct { 
			unsigned int reserve_data[8];
		} reserve_reg_12_16;
		union debug_point0_cfg_u { 
			struct debug_point0_cfg_s { 
				unsigned int point0_h: 12;
				unsigned int reserve_0: 4;
				unsigned int point0_v: 12;
				unsigned int reserve_1: 4;
			} bits;
			unsigned int u32;
		} sw_debug_point0_cfg;
		union debug_point1_cfg_u { 
			struct debug_point1_cfg_s { 
				unsigned int point1_h: 12;
				unsigned int reserve_0: 4;
				unsigned int point1_v: 12;
				unsigned int reserve_1: 4;
			} bits;
			unsigned int u32;
		} sw_debug_point1_cfg;
		union debug_point2_cfg_u { 
			struct debug_point2_cfg_s { 
				unsigned int point2_h: 12;
				unsigned int reserve_0: 4;
				unsigned int point2_v: 12;
				unsigned int reserve_1: 4;
			} bits;
			unsigned int u32;
		} sw_debug_point2_cfg;
		union debug_point3_cfg_u { 
			struct debug_point3_cfg_s { 
				unsigned int point3_h: 12;
				unsigned int reserve_0: 4;
				unsigned int point3_v: 12;
				unsigned int reserve_1: 4;
			} bits;
			unsigned int u32;
		} sw_debug_point3_cfg;
		union fetch_done_u { 
			struct fetch_done_s { 
				unsigned int fetch_done: 1;
				unsigned int reserve_0: 31;
			} bits;
			unsigned int u32;
		} sw_fetch_done;
		struct { 
			unsigned int reserve_data[12];
		} reserve_reg_40_48;
		union debug0_data0_u { 
			struct debug0_data0_s { 
				unsigned int debug0_data0: 32;
			} bits;
			unsigned int u32;
		} sw_debug0_data0;
		union debug0_data1_u { 
			struct debug0_data1_s { 
				unsigned int debug0_data1: 32;
			} bits;
			unsigned int u32;
		} sw_debug0_data1;
		union debug0_data2_u { 
			struct debug0_data2_s { 
				unsigned int debug0_data2: 32;
			} bits;
			unsigned int u32;
		} sw_debug0_data2;
		union debug0_data3_u { 
			struct debug0_data3_s { 
				unsigned int debug0_data3: 32;
			} bits;
			unsigned int u32;
		} sw_debug0_data3;
		union debug1_data0_u { 
			struct debug1_data0_s { 
				unsigned int debug1_data0: 32;
			} bits;
			unsigned int u32;
		} sw_debug1_data0;
		union debug1_data1_u { 
			struct debug1_data1_s { 
				unsigned int debug1_data1: 32;
			} bits;
			unsigned int u32;
		} sw_debug1_data1;
		union debug1_data2_u { 
			struct debug1_data2_s { 
				unsigned int debug1_data2: 32;
			} bits;
			unsigned int u32;
		} sw_debug1_data2;
		union debug1_data3_u { 
			struct debug1_data3_s { 
				unsigned int debug1_data3: 32;
			} bits;
			unsigned int u32;
		} sw_debug1_data3;
		union debug2_data0_u { 
			struct debug2_data0_s { 
				unsigned int debug2_data0: 32;
			} bits;
			unsigned int u32;
		} sw_debug2_data0;
		union debug2_data1_u { 
			struct debug2_data1_s { 
				unsigned int debug2_data1: 32;
			} bits;
			unsigned int u32;
		} sw_debug2_data1;
		union debug2_data2_u { 
			struct debug2_data2_s { 
				unsigned int debug2_data2: 32;
			} bits;
			unsigned int u32;
		} sw_debug2_data2;
		union debug2_data3_u { 
			struct debug2_data3_s { 
				unsigned int debug2_data3: 32;
			} bits;
			unsigned int u32;
		} sw_debug2_data3;
		union debug3_data0_u { 
			struct debug3_data0_s { 
				unsigned int debug3_data0: 32;
			} bits;
			unsigned int u32;
		} sw_debug3_data0;
		union debug3_data1_u { 
			struct debug3_data1_s { 
				unsigned int debug3_data1: 32;
			} bits;
			unsigned int u32;
		} sw_debug3_data1;
		union debug3_data2_u { 
			struct debug3_data2_s { 
				unsigned int debug3_data2: 32;
			} bits;
			unsigned int u32;
		} sw_debug3_data2;
		union debug3_data3_u { 
			struct debug3_data3_s { 
				unsigned int debug3_data3: 32;
			} bits;
			unsigned int u32;
		} sw_debug3_data3;
		struct { 
			unsigned int reserve_data[144];
		} reserve_reg_116_256;
		union yhs_gain_by_y_seg0_u { 
			struct yhs_gain_by_y_seg0_s { 
				unsigned int ygain_y_0: 8;
				unsigned int hgain_y_0: 8;
				unsigned int sgain_y_0: 8;
				unsigned int reserve_0: 8;
			} bits;
			unsigned int u32;
		} sw_yhs_gain_by_y_seg0;
		struct { 
			unsigned int reserve_data[604];
		} reserve_reg_264_864;
		union yhs_gain_by_y_seg152_u { 
			struct yhs_gain_by_y_seg152_s { 
				unsigned int ygain_y_152: 8;
				unsigned int hgain_y_152: 8;
				unsigned int sgain_y_152: 8;
				unsigned int reserve_0: 8;
			} bits;
			unsigned int u32;
		} sw_yhs_gain_by_y_seg152;
		union yhs_gain_by_s_seg0_u { 
			struct yhs_gain_by_s_seg0_s { 
				unsigned int ygain_s_0: 8;
				unsigned int hgain_s_0: 8;
				unsigned int sgain_s_0: 8;
				unsigned int reserve_0: 8;
			} bits;
			unsigned int u32;
		} sw_yhs_gain_by_s_seg0;
		struct { 
			unsigned int reserve_data[876];
		} reserve_reg_876_1748;
		union yhs_gain_by_s_seg220_u { 
			struct yhs_gain_by_s_seg220_s { 
				unsigned int ygain_s_220: 8;
				unsigned int hgain_s_220: 8;
				unsigned int sgain_s_220: 8;
				unsigned int reserve_0: 8;
			} bits;
			unsigned int u32;
		} sw_yhs_gain_by_s_seg220;
		union yhs_del_by_h_seg0_u { 
			struct yhs_del_by_h_seg0_s { 
				unsigned int ydel_h_0: 10;
				unsigned int reserve_0: 2;
				unsigned int hdel_h_0: 8;
				unsigned int sdel_h_0: 10;
				unsigned int reserve_1: 2;
			} bits;
			unsigned int u32;
		} sw_yhs_del_by_h_seg0;
		struct { 
			unsigned int reserve_data[252];
		} reserve_reg_1760_2008;
		union yhs_del_by_h_seg64_u { 
			struct yhs_del_by_h_seg64_s { 
				unsigned int ydel_h_64: 10;
				unsigned int reserve_0: 2;
				unsigned int hdel_h_64: 8;
				unsigned int sdel_h_64: 10;
				unsigned int reserve_1: 2;
			} bits;
			unsigned int u32;
		} sw_yhs_del_by_h_seg64;
	} regs;
	unsigned int p_reg_addr[30];
}acm_0x27d06400_t;

typedef union sharp_0x27d06c00_u {
	struct sharp_0x27d06c00_s {
		union ctrl_u { 
			struct ctrl_s { 
				unsigned int sw_sharp_enable: 1;
				unsigned int sw_lti_enable: 1;
				unsigned int sw_cti_enable: 1;
				unsigned int sw_peaking_enable: 1;
				unsigned int sw_peaking_ctrl_enable: 1;
				unsigned int sw_peaking_shoot_ctrl_enable: 1;
				unsigned int sw_edge_proc_enable: 1;
				unsigned int sw_shoot_ctrl_enable: 1;
				unsigned int sw_gain_ctrl_enable: 1;
				unsigned int sw_color_adj_enable: 1;
				unsigned int sw_texture_adj_enable: 1;
				unsigned int reserve_0: 1;
				unsigned int sw_ink_enable: 1;
				unsigned int reserve_1: 19;
			} bits;
			unsigned int u32;
		} sw_ctrl;
		union auto_gating_imd_u { 
			struct auto_gating_imd_s { 
				unsigned int reserve_0: 1;
				unsigned int sw_lti_gating_en: 1;
				unsigned int sw_cti_gating_en: 1;
				unsigned int sw_peaking_gating_en: 1;
				unsigned int sw_peaking_ctrl_gating_en: 1;
				unsigned int sw_peaking_shoot_ctrl_gating_en: 1;
				unsigned int sw_edge_proc_gating_en: 1;
				unsigned int sw_shoot_ctrl_gating_en: 1;
				unsigned int sw_gain_ctrl_gating_en: 1;
				unsigned int sw_color_adj_gating_en: 1;
				unsigned int sw_texture_adj_gating_en: 1;
				unsigned int reserve_1: 21;
			} bits;
			unsigned int u32;
		} sw_auto_gating_imd;
		union peaking_filter_coe0_u { 
			struct peaking_filter_coe0_s { 
				unsigned int sw_peaking_v00: 4;
				unsigned int sw_peaking_v01: 4;
				unsigned int sw_peaking_v02: 4;
				unsigned int sw_peaking_v10: 4;
				unsigned int sw_peaking_v11: 4;
				unsigned int sw_peaking_v12: 4;
				unsigned int reserve_0: 8;
			} bits;
			unsigned int u32;
		} sw_peaking_filter_coe0;
		union peaking_filter_coe1_u { 
			struct peaking_filter_coe1_s { 
				unsigned int sw_peaking_v20: 4;
				unsigned int sw_peaking_v21: 4;
				unsigned int sw_peaking_v22: 4;
				unsigned int sw_peaking_usm0: 4;
				unsigned int sw_peaking_usm1: 4;
				unsigned int sw_peaking_usm2: 4;
				unsigned int sw_diag_coef: 3;
				unsigned int reserve_0: 5;
			} bits;
			unsigned int u32;
		} sw_peaking_filter_coe1;
		union peaking_filter_coe2_u { 
			struct peaking_filter_coe2_s { 
				unsigned int sw_peaking_h00: 5;
				unsigned int reserve_0: 3;
				unsigned int sw_peaking_h01: 7;
				unsigned int reserve_1: 1;
				unsigned int sw_peaking_h02: 9;
				unsigned int reserve_2: 7;
			} bits;
			unsigned int u32;
		} sw_peaking_filter_coe2;
		union peaking_filter_coe3_u { 
			struct peaking_filter_coe3_s { 
				unsigned int sw_peaking_h03: 10;
				unsigned int sw_peaking_h04: 11;
				unsigned int sw_peaking_h05: 10;
				unsigned int reserve_0: 1;
			} bits;
			unsigned int u32;
		} sw_peaking_filter_coe3;
		union peaking_filter_coe4_u { 
			struct peaking_filter_coe4_s { 
				unsigned int sw_peaking_h10: 5;
				unsigned int reserve_0: 3;
				unsigned int sw_peaking_h11: 7;
				unsigned int reserve_1: 1;
				unsigned int sw_peaking_h12: 9;
				unsigned int reserve_2: 7;
			} bits;
			unsigned int u32;
		} sw_peaking_filter_coe4;
		union peaking_filter_coe5_u { 
			struct peaking_filter_coe5_s { 
				unsigned int sw_peaking_h13: 10;
				unsigned int sw_peaking_h14: 11;
				unsigned int sw_peaking_h15: 10;
				unsigned int reserve_0: 1;
			} bits;
			unsigned int u32;
		} sw_peaking_filter_coe5;
		union peaking_filter_coe6_u { 
			struct peaking_filter_coe6_s { 
				unsigned int sw_peaking_h20: 5;
				unsigned int reserve_0: 3;
				unsigned int sw_peaking_h21: 7;
				unsigned int reserve_1: 1;
				unsigned int sw_peaking_h22: 9;
				unsigned int reserve_2: 7;
			} bits;
			unsigned int u32;
		} sw_peaking_filter_coe6;
		union peaking_filter_coe7_u { 
			struct peaking_filter_coe7_s { 
				unsigned int sw_peaking_h23: 10;
				unsigned int sw_peaking_h24: 11;
				unsigned int sw_peaking_h25: 10;
				unsigned int reserve_0: 1;
			} bits;
			unsigned int u32;
		} sw_peaking_filter_coe7;
		union peaking_filter_coe8_u { 
			struct peaking_filter_coe8_s { 
				unsigned int sw_peaking_h30: 5;
				unsigned int reserve_0: 3;
				unsigned int sw_peaking_h31: 7;
				unsigned int reserve_1: 1;
				unsigned int sw_peaking_h32: 9;
				unsigned int reserve_2: 7;
			} bits;
			unsigned int u32;
		} sw_peaking_filter_coe8;
		union peaking_filter_coe9_u { 
			struct peaking_filter_coe9_s { 
				unsigned int sw_peaking_h33: 10;
				unsigned int sw_peaking_h34: 11;
				unsigned int sw_peaking_h35: 10;
				unsigned int reserve_0: 1;
			} bits;
			unsigned int u32;
		} sw_peaking_filter_coe9;
		union peaking0_ctrl_coe0_u { 
			struct peaking0_ctrl_coe0_s { 
				unsigned int sw_peaking0_idx_n0: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking0_idx_n1: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking0_ctrl_coe0;
		union peaking0_ctrl_coe1_u { 
			struct peaking0_ctrl_coe1_s { 
				unsigned int sw_peaking0_idx_n2: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking0_idx_n3: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking0_ctrl_coe1;
		union peaking0_ctrl_coe2_u { 
			struct peaking0_ctrl_coe2_s { 
				unsigned int sw_peaking0_idx_p0: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking0_idx_p1: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking0_ctrl_coe2;
		union peaking0_ctrl_coe3_u { 
			struct peaking0_ctrl_coe3_s { 
				unsigned int sw_peaking0_idx_p2: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking0_idx_p3: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking0_ctrl_coe3;
		union peaking0_ctrl_coe4_u { 
			struct peaking0_ctrl_coe4_s { 
				unsigned int sw_peaking0_value_n1: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking0_value_n2: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking0_ctrl_coe4;
		union peaking0_ctrl_coe5_u { 
			struct peaking0_ctrl_coe5_s { 
				unsigned int sw_peaking0_value_n3: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking0_value_p1: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking0_ctrl_coe5;
		union peaking0_ctrl_coe6_u { 
			struct peaking0_ctrl_coe6_s { 
				unsigned int sw_peaking0_value_p2: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking0_value_p3: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking0_ctrl_coe6;
		union peaking0_ctrl_coe7_u { 
			struct peaking0_ctrl_coe7_s { 
				unsigned int sw_peaking0_ratio_n01: 12;
				unsigned int reserve_0: 4;
				unsigned int sw_peaking0_ratio_n12: 12;
				unsigned int reserve_1: 4;
			} bits;
			unsigned int u32;
		} sw_peaking0_ctrl_coe7;
		union peaking0_ctrl_coe8_u { 
			struct peaking0_ctrl_coe8_s { 
				unsigned int sw_peaking0_ratio_n23: 12;
				unsigned int reserve_0: 4;
				unsigned int sw_peaking0_ratio_p01: 12;
				unsigned int reserve_1: 4;
			} bits;
			unsigned int u32;
		} sw_peaking0_ctrl_coe8;
		union peaking0_ctrl_coe9_u { 
			struct peaking0_ctrl_coe9_s { 
				unsigned int sw_peaking0_ratio_p12: 12;
				unsigned int sw_peaking0_ratio_p23: 12;
				unsigned int sw_peaking0_shoot_delta_offset: 8;
			} bits;
			unsigned int u32;
		} sw_peaking0_ctrl_coe9;
		union peaking0_ctrl_coe10_u { 
			struct peaking0_ctrl_coe10_s { 
				unsigned int sw_peaking0_shoot_alpha_over: 7;
				unsigned int reserve_0: 1;
				unsigned int sw_peaking0_shoot_alpha_under: 7;
				unsigned int reserve_1: 1;
				unsigned int sw_peaking0_shoot_alpha_over_unlimit: 7;
				unsigned int reserve_2: 1;
				unsigned int sw_peaking0_shoot_alpha_under_unlimit: 7;
				unsigned int reserve_3: 1;
			} bits;
			unsigned int u32;
		} sw_peaking0_ctrl_coe10;
		union peaking1_ctrl_coe0_u { 
			struct peaking1_ctrl_coe0_s { 
				unsigned int sw_peaking1_idx_n0: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking1_idx_n1: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking1_ctrl_coe0;
		union peaking1_ctrl_coe1_u { 
			struct peaking1_ctrl_coe1_s { 
				unsigned int sw_peaking1_idx_n2: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking1_idx_n3: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking1_ctrl_coe1;
		union peaking1_ctrl_coe2_u { 
			struct peaking1_ctrl_coe2_s { 
				unsigned int sw_peaking1_idx_p0: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking1_idx_p1: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking1_ctrl_coe2;
		union peaking1_ctrl_coe3_u { 
			struct peaking1_ctrl_coe3_s { 
				unsigned int sw_peaking1_idx_p2: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking1_idx_p3: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking1_ctrl_coe3;
		union peaking1_ctrl_coe4_u { 
			struct peaking1_ctrl_coe4_s { 
				unsigned int sw_peaking1_value_n1: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking1_value_n2: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking1_ctrl_coe4;
		union peaking1_ctrl_coe5_u { 
			struct peaking1_ctrl_coe5_s { 
				unsigned int sw_peaking1_value_n3: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking1_value_p1: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking1_ctrl_coe5;
		union peaking1_ctrl_coe6_u { 
			struct peaking1_ctrl_coe6_s { 
				unsigned int sw_peaking1_value_p2: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking1_value_p3: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking1_ctrl_coe6;
		union peaking1_ctrl_coe7_u { 
			struct peaking1_ctrl_coe7_s { 
				unsigned int sw_peaking1_ratio_n01: 12;
				unsigned int reserve_0: 4;
				unsigned int sw_peaking1_ratio_n12: 12;
				unsigned int reserve_1: 4;
			} bits;
			unsigned int u32;
		} sw_peaking1_ctrl_coe7;
		union peaking1_ctrl_coe8_u { 
			struct peaking1_ctrl_coe8_s { 
				unsigned int sw_peaking1_ratio_n23: 12;
				unsigned int reserve_0: 4;
				unsigned int sw_peaking1_ratio_p01: 12;
				unsigned int reserve_1: 4;
			} bits;
			unsigned int u32;
		} sw_peaking1_ctrl_coe8;
		union peaking1_ctrl_coe9_u { 
			struct peaking1_ctrl_coe9_s { 
				unsigned int sw_peaking1_ratio_p12: 12;
				unsigned int sw_peaking1_ratio_p23: 12;
				unsigned int sw_peaking1_shoot_delta_offset: 8;
			} bits;
			unsigned int u32;
		} sw_peaking1_ctrl_coe9;
		union peaking1_ctrl_coe10_u { 
			struct peaking1_ctrl_coe10_s { 
				unsigned int sw_peaking1_shoot_alpha_over: 7;
				unsigned int reserve_0: 1;
				unsigned int sw_peaking1_shoot_alpha_under: 7;
				unsigned int reserve_1: 1;
				unsigned int sw_peaking1_shoot_alpha_over_unlimit: 7;
				unsigned int reserve_2: 1;
				unsigned int sw_peaking1_shoot_alpha_under_unlimit: 7;
				unsigned int reserve_3: 1;
			} bits;
			unsigned int u32;
		} sw_peaking1_ctrl_coe10;
		union peaking2_ctrl_coe0_u { 
			struct peaking2_ctrl_coe0_s { 
				unsigned int sw_peaking2_idx_n0: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking2_idx_n1: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking2_ctrl_coe0;
		union peaking2_ctrl_coe1_u { 
			struct peaking2_ctrl_coe1_s { 
				unsigned int sw_peaking2_idx_n2: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking2_idx_n3: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking2_ctrl_coe1;
		union peaking2_ctrl_coe2_u { 
			struct peaking2_ctrl_coe2_s { 
				unsigned int sw_peaking2_idx_p0: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking2_idx_p1: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking2_ctrl_coe2;
		union peaking2_ctrl_coe3_u { 
			struct peaking2_ctrl_coe3_s { 
				unsigned int sw_peaking2_idx_p2: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking2_idx_p3: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking2_ctrl_coe3;
		union peaking2_ctrl_coe4_u { 
			struct peaking2_ctrl_coe4_s { 
				unsigned int sw_peaking2_value_n1: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking2_value_n2: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking2_ctrl_coe4;
		union peaking2_ctrl_coe5_u { 
			struct peaking2_ctrl_coe5_s { 
				unsigned int sw_peaking2_value_n3: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking2_value_p1: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking2_ctrl_coe5;
		union peaking2_ctrl_coe6_u { 
			struct peaking2_ctrl_coe6_s { 
				unsigned int sw_peaking2_value_p2: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking2_value_p3: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking2_ctrl_coe6;
		union peaking2_ctrl_coe7_u { 
			struct peaking2_ctrl_coe7_s { 
				unsigned int sw_peaking2_ratio_n01: 12;
				unsigned int reserve_0: 4;
				unsigned int sw_peaking2_ratio_n12: 12;
				unsigned int reserve_1: 4;
			} bits;
			unsigned int u32;
		} sw_peaking2_ctrl_coe7;
		union peaking2_ctrl_coe8_u { 
			struct peaking2_ctrl_coe8_s { 
				unsigned int sw_peaking2_ratio_n23: 12;
				unsigned int reserve_0: 4;
				unsigned int sw_peaking2_ratio_p01: 12;
				unsigned int reserve_1: 4;
			} bits;
			unsigned int u32;
		} sw_peaking2_ctrl_coe8;
		union peaking2_ctrl_coe9_u { 
			struct peaking2_ctrl_coe9_s { 
				unsigned int sw_peaking2_ratio_p12: 12;
				unsigned int sw_peaking2_ratio_p23: 12;
				unsigned int sw_peaking2_shoot_delta_offset: 8;
			} bits;
			unsigned int u32;
		} sw_peaking2_ctrl_coe9;
		union peaking2_ctrl_coe10_u { 
			struct peaking2_ctrl_coe10_s { 
				unsigned int sw_peaking2_shoot_alpha_over: 7;
				unsigned int reserve_0: 1;
				unsigned int sw_peaking2_shoot_alpha_under: 7;
				unsigned int reserve_1: 1;
				unsigned int sw_peaking2_shoot_alpha_over_unlimit: 7;
				unsigned int reserve_2: 1;
				unsigned int sw_peaking2_shoot_alpha_under_unlimit: 7;
				unsigned int reserve_3: 1;
			} bits;
			unsigned int u32;
		} sw_peaking2_ctrl_coe10;
		union peaking3_ctrl_coe0_u { 
			struct peaking3_ctrl_coe0_s { 
				unsigned int sw_peaking3_idx_n0: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking3_idx_n1: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking3_ctrl_coe0;
		union peaking3_ctrl_coe1_u { 
			struct peaking3_ctrl_coe1_s { 
				unsigned int sw_peaking3_idx_n2: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking3_idx_n3: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking3_ctrl_coe1;
		union peaking3_ctrl_coe2_u { 
			struct peaking3_ctrl_coe2_s { 
				unsigned int sw_peaking3_idx_p0: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking3_idx_p1: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking3_ctrl_coe2;
		union peaking3_ctrl_coe3_u { 
			struct peaking3_ctrl_coe3_s { 
				unsigned int sw_peaking3_idx_p2: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking3_idx_p3: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking3_ctrl_coe3;
		union peaking3_ctrl_coe4_u { 
			struct peaking3_ctrl_coe4_s { 
				unsigned int sw_peaking3_value_n1: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking3_value_n2: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking3_ctrl_coe4;
		union peaking3_ctrl_coe5_u { 
			struct peaking3_ctrl_coe5_s { 
				unsigned int sw_peaking3_value_n3: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking3_value_p1: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking3_ctrl_coe5;
		union peaking3_ctrl_coe6_u { 
			struct peaking3_ctrl_coe6_s { 
				unsigned int sw_peaking3_value_p2: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking3_value_p3: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking3_ctrl_coe6;
		union peaking3_ctrl_coe7_u { 
			struct peaking3_ctrl_coe7_s { 
				unsigned int sw_peaking3_ratio_n01: 12;
				unsigned int reserve_0: 4;
				unsigned int sw_peaking3_ratio_n12: 12;
				unsigned int reserve_1: 4;
			} bits;
			unsigned int u32;
		} sw_peaking3_ctrl_coe7;
		union peaking3_ctrl_coe8_u { 
			struct peaking3_ctrl_coe8_s { 
				unsigned int sw_peaking3_ratio_n23: 12;
				unsigned int reserve_0: 4;
				unsigned int sw_peaking3_ratio_p01: 12;
				unsigned int reserve_1: 4;
			} bits;
			unsigned int u32;
		} sw_peaking3_ctrl_coe8;
		union peaking3_ctrl_coe9_u { 
			struct peaking3_ctrl_coe9_s { 
				unsigned int sw_peaking3_ratio_p12: 12;
				unsigned int sw_peaking3_ratio_p23: 12;
				unsigned int sw_peaking3_shoot_delta_offset: 8;
			} bits;
			unsigned int u32;
		} sw_peaking3_ctrl_coe9;
		union peaking3_ctrl_coe10_u { 
			struct peaking3_ctrl_coe10_s { 
				unsigned int sw_peaking3_shoot_alpha_over: 7;
				unsigned int reserve_0: 1;
				unsigned int sw_peaking3_shoot_alpha_under: 7;
				unsigned int reserve_1: 1;
				unsigned int sw_peaking3_shoot_alpha_over_unlimit: 7;
				unsigned int reserve_2: 1;
				unsigned int sw_peaking3_shoot_alpha_under_unlimit: 7;
				unsigned int reserve_3: 1;
			} bits;
			unsigned int u32;
		} sw_peaking3_ctrl_coe10;
		union peaking4_ctrl_coe0_u { 
			struct peaking4_ctrl_coe0_s { 
				unsigned int sw_peaking4_idx_n0: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking4_idx_n1: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking4_ctrl_coe0;
		union peaking4_ctrl_coe1_u { 
			struct peaking4_ctrl_coe1_s { 
				unsigned int sw_peaking4_idx_n2: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking4_idx_n3: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking4_ctrl_coe1;
		union peaking4_ctrl_coe2_u { 
			struct peaking4_ctrl_coe2_s { 
				unsigned int sw_peaking4_idx_p0: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking4_idx_p1: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking4_ctrl_coe2;
		union peaking4_ctrl_coe3_u { 
			struct peaking4_ctrl_coe3_s { 
				unsigned int sw_peaking4_idx_p2: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking4_idx_p3: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking4_ctrl_coe3;
		union peaking4_ctrl_coe4_u { 
			struct peaking4_ctrl_coe4_s { 
				unsigned int sw_peaking4_value_n1: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking4_value_n2: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking4_ctrl_coe4;
		union peaking4_ctrl_coe5_u { 
			struct peaking4_ctrl_coe5_s { 
				unsigned int sw_peaking4_value_n3: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking4_value_p1: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking4_ctrl_coe5;
		union peaking4_ctrl_coe6_u { 
			struct peaking4_ctrl_coe6_s { 
				unsigned int sw_peaking4_value_p2: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking4_value_p3: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking4_ctrl_coe6;
		union peaking4_ctrl_coe7_u { 
			struct peaking4_ctrl_coe7_s { 
				unsigned int sw_peaking4_ratio_n01: 12;
				unsigned int reserve_0: 4;
				unsigned int sw_peaking4_ratio_n12: 12;
				unsigned int reserve_1: 4;
			} bits;
			unsigned int u32;
		} sw_peaking4_ctrl_coe7;
		union peaking4_ctrl_coe8_u { 
			struct peaking4_ctrl_coe8_s { 
				unsigned int sw_peaking4_ratio_n23: 12;
				unsigned int reserve_0: 4;
				unsigned int sw_peaking4_ratio_p01: 12;
				unsigned int reserve_1: 4;
			} bits;
			unsigned int u32;
		} sw_peaking4_ctrl_coe8;
		union peaking4_ctrl_coe9_u { 
			struct peaking4_ctrl_coe9_s { 
				unsigned int sw_peaking4_ratio_p12: 12;
				unsigned int sw_peaking4_ratio_p23: 12;
				unsigned int sw_peaking4_shoot_delta_offset: 8;
			} bits;
			unsigned int u32;
		} sw_peaking4_ctrl_coe9;
		union peaking4_ctrl_coe10_u { 
			struct peaking4_ctrl_coe10_s { 
				unsigned int sw_peaking4_shoot_alpha_over: 7;
				unsigned int reserve_0: 1;
				unsigned int sw_peaking4_shoot_alpha_under: 7;
				unsigned int reserve_1: 1;
				unsigned int sw_peaking4_shoot_alpha_over_unlimit: 7;
				unsigned int reserve_2: 1;
				unsigned int sw_peaking4_shoot_alpha_under_unlimit: 7;
				unsigned int reserve_3: 1;
			} bits;
			unsigned int u32;
		} sw_peaking4_ctrl_coe10;
		union peaking5_ctrl_coe0_u { 
			struct peaking5_ctrl_coe0_s { 
				unsigned int sw_peaking5_idx_n0: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking5_idx_n1: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking5_ctrl_coe0;
		union peaking5_ctrl_coe1_u { 
			struct peaking5_ctrl_coe1_s { 
				unsigned int sw_peaking5_idx_n2: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking5_idx_n3: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking5_ctrl_coe1;
		union peaking5_ctrl_coe2_u { 
			struct peaking5_ctrl_coe2_s { 
				unsigned int sw_peaking5_idx_p0: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking5_idx_p1: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking5_ctrl_coe2;
		union peaking5_ctrl_coe3_u { 
			struct peaking5_ctrl_coe3_s { 
				unsigned int sw_peaking5_idx_p2: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking5_idx_p3: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking5_ctrl_coe3;
		union peaking5_ctrl_coe4_u { 
			struct peaking5_ctrl_coe4_s { 
				unsigned int sw_peaking5_value_n1: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking5_value_n2: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking5_ctrl_coe4;
		union peaking5_ctrl_coe5_u { 
			struct peaking5_ctrl_coe5_s { 
				unsigned int sw_peaking5_value_n3: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking5_value_p1: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking5_ctrl_coe5;
		union peaking5_ctrl_coe6_u { 
			struct peaking5_ctrl_coe6_s { 
				unsigned int sw_peaking5_value_p2: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking5_value_p3: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking5_ctrl_coe6;
		union peaking5_ctrl_coe7_u { 
			struct peaking5_ctrl_coe7_s { 
				unsigned int sw_peaking5_ratio_n01: 12;
				unsigned int reserve_0: 4;
				unsigned int sw_peaking5_ratio_n12: 12;
				unsigned int reserve_1: 4;
			} bits;
			unsigned int u32;
		} sw_peaking5_ctrl_coe7;
		union peaking5_ctrl_coe8_u { 
			struct peaking5_ctrl_coe8_s { 
				unsigned int sw_peaking5_ratio_n23: 12;
				unsigned int reserve_0: 4;
				unsigned int sw_peaking5_ratio_p01: 12;
				unsigned int reserve_1: 4;
			} bits;
			unsigned int u32;
		} sw_peaking5_ctrl_coe8;
		union peaking5_ctrl_coe9_u { 
			struct peaking5_ctrl_coe9_s { 
				unsigned int sw_peaking5_ratio_p12: 12;
				unsigned int sw_peaking5_ratio_p23: 12;
				unsigned int sw_peaking5_shoot_delta_offset: 8;
			} bits;
			unsigned int u32;
		} sw_peaking5_ctrl_coe9;
		union peaking5_ctrl_coe10_u { 
			struct peaking5_ctrl_coe10_s { 
				unsigned int sw_peaking5_shoot_alpha_over: 7;
				unsigned int reserve_0: 1;
				unsigned int sw_peaking5_shoot_alpha_under: 7;
				unsigned int reserve_1: 1;
				unsigned int sw_peaking5_shoot_alpha_over_unlimit: 7;
				unsigned int reserve_2: 1;
				unsigned int sw_peaking5_shoot_alpha_under_unlimit: 7;
				unsigned int reserve_3: 1;
			} bits;
			unsigned int u32;
		} sw_peaking5_ctrl_coe10;
		union peaking6_ctrl_coe0_u { 
			struct peaking6_ctrl_coe0_s { 
				unsigned int sw_peaking6_idx_n0: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking6_idx_n1: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking6_ctrl_coe0;
		union peaking6_ctrl_coe1_u { 
			struct peaking6_ctrl_coe1_s { 
				unsigned int sw_peaking6_idx_n2: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking6_idx_n3: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking6_ctrl_coe1;
		union peaking6_ctrl_coe2_u { 
			struct peaking6_ctrl_coe2_s { 
				unsigned int sw_peaking6_idx_p0: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking6_idx_p1: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking6_ctrl_coe2;
		union peaking6_ctrl_coe3_u { 
			struct peaking6_ctrl_coe3_s { 
				unsigned int sw_peaking6_idx_p2: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking6_idx_p3: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking6_ctrl_coe3;
		union peaking6_ctrl_coe4_u { 
			struct peaking6_ctrl_coe4_s { 
				unsigned int sw_peaking6_value_n1: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking6_value_n2: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking6_ctrl_coe4;
		union peaking6_ctrl_coe5_u { 
			struct peaking6_ctrl_coe5_s { 
				unsigned int sw_peaking6_value_n3: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking6_value_p1: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking6_ctrl_coe5;
		union peaking6_ctrl_coe6_u { 
			struct peaking6_ctrl_coe6_s { 
				unsigned int sw_peaking6_value_p2: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking6_value_p3: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking6_ctrl_coe6;
		union peaking6_ctrl_coe7_u { 
			struct peaking6_ctrl_coe7_s { 
				unsigned int sw_peaking6_ratio_n01: 12;
				unsigned int reserve_0: 4;
				unsigned int sw_peaking6_ratio_n12: 12;
				unsigned int reserve_1: 4;
			} bits;
			unsigned int u32;
		} sw_peaking6_ctrl_coe7;
		union peaking6_ctrl_coe8_u { 
			struct peaking6_ctrl_coe8_s { 
				unsigned int sw_peaking6_ratio_n23: 12;
				unsigned int reserve_0: 4;
				unsigned int sw_peaking6_ratio_p01: 12;
				unsigned int reserve_1: 4;
			} bits;
			unsigned int u32;
		} sw_peaking6_ctrl_coe8;
		union peaking6_ctrl_coe9_u { 
			struct peaking6_ctrl_coe9_s { 
				unsigned int sw_peaking6_ratio_p12: 12;
				unsigned int sw_peaking6_ratio_p23: 12;
				unsigned int sw_peaking6_shoot_delta_offset: 8;
			} bits;
			unsigned int u32;
		} sw_peaking6_ctrl_coe9;
		union peaking6_ctrl_coe10_u { 
			struct peaking6_ctrl_coe10_s { 
				unsigned int sw_peaking6_shoot_alpha_over: 7;
				unsigned int reserve_0: 1;
				unsigned int sw_peaking6_shoot_alpha_under: 7;
				unsigned int reserve_1: 1;
				unsigned int sw_peaking6_shoot_alpha_over_unlimit: 7;
				unsigned int reserve_2: 1;
				unsigned int sw_peaking6_shoot_alpha_under_unlimit: 7;
				unsigned int reserve_3: 1;
			} bits;
			unsigned int u32;
		} sw_peaking6_ctrl_coe10;
		union peaking7_ctrl_coe0_u { 
			struct peaking7_ctrl_coe0_s { 
				unsigned int sw_peaking7_idx_n0: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking7_idx_n1: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking7_ctrl_coe0;
		union peaking7_ctrl_coe1_u { 
			struct peaking7_ctrl_coe1_s { 
				unsigned int sw_peaking7_idx_n2: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking7_idx_n3: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking7_ctrl_coe1;
		union peaking7_ctrl_coe2_u { 
			struct peaking7_ctrl_coe2_s { 
				unsigned int sw_peaking7_idx_p0: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking7_idx_p1: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking7_ctrl_coe2;
		union peaking7_ctrl_coe3_u { 
			struct peaking7_ctrl_coe3_s { 
				unsigned int sw_peaking7_idx_p2: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking7_idx_p3: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking7_ctrl_coe3;
		union peaking7_ctrl_coe4_u { 
			struct peaking7_ctrl_coe4_s { 
				unsigned int sw_peaking7_value_n1: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking7_value_n2: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking7_ctrl_coe4;
		union peaking7_ctrl_coe5_u { 
			struct peaking7_ctrl_coe5_s { 
				unsigned int sw_peaking7_value_n3: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking7_value_p1: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking7_ctrl_coe5;
		union peaking7_ctrl_coe6_u { 
			struct peaking7_ctrl_coe6_s { 
				unsigned int sw_peaking7_value_p2: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_peaking7_value_p3: 11;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking7_ctrl_coe6;
		union peaking7_ctrl_coe7_u { 
			struct peaking7_ctrl_coe7_s { 
				unsigned int sw_peaking7_ratio_n01: 12;
				unsigned int reserve_0: 4;
				unsigned int sw_peaking7_ratio_n12: 12;
				unsigned int reserve_1: 4;
			} bits;
			unsigned int u32;
		} sw_peaking7_ctrl_coe7;
		union peaking7_ctrl_coe8_u { 
			struct peaking7_ctrl_coe8_s { 
				unsigned int sw_peaking7_ratio_n23: 12;
				unsigned int reserve_0: 4;
				unsigned int sw_peaking7_ratio_p01: 12;
				unsigned int reserve_1: 4;
			} bits;
			unsigned int u32;
		} sw_peaking7_ctrl_coe8;
		union peaking7_ctrl_coe9_u { 
			struct peaking7_ctrl_coe9_s { 
				unsigned int sw_peaking7_ratio_p12: 12;
				unsigned int sw_peaking7_ratio_p23: 12;
				unsigned int sw_peaking7_shoot_delta_offset: 8;
			} bits;
			unsigned int u32;
		} sw_peaking7_ctrl_coe9;
		union peaking7_ctrl_coe10_u { 
			struct peaking7_ctrl_coe10_s { 
				unsigned int sw_peaking7_shoot_alpha_over: 7;
				unsigned int reserve_0: 1;
				unsigned int sw_peaking7_shoot_alpha_under: 7;
				unsigned int reserve_1: 1;
				unsigned int sw_peaking7_shoot_alpha_over_unlimit: 7;
				unsigned int reserve_2: 1;
				unsigned int sw_peaking7_shoot_alpha_under_unlimit: 7;
				unsigned int reserve_3: 1;
			} bits;
			unsigned int u32;
		} sw_peaking7_ctrl_coe10;
		union peaking_ctrl0_u { 
			struct peaking_ctrl0_s { 
				unsigned int sw_peaking_gain: 10;
				unsigned int reserve_0: 2;
				unsigned int sw_nondir_thr: 7;
				unsigned int reserve_1: 1;
				unsigned int sw_dir_cmp_ratio: 4;
				unsigned int sw_nondir_wgt_ratio: 5;
				unsigned int reserve_2: 3;
			} bits;
			unsigned int u32;
		} sw_peaking_ctrl0;
		union peaking_ctrl1_u { 
			struct peaking_ctrl1_s { 
				unsigned int sw_nondir_wgt_offset: 8;
				unsigned int sw_dir_cnt_thr: 4;
				unsigned int sw_dir_cnt_avg: 3;
				unsigned int reserve_0: 1;
				unsigned int sw_dir_cnt_offset: 4;
				unsigned int sw_diag_dir_thr: 7;
				unsigned int reserve_1: 5;
			} bits;
			unsigned int u32;
		} sw_peaking_ctrl1;
		union peaking_ctrl2_u { 
			struct peaking_ctrl2_s { 
				unsigned int sw_diag_adjgain_tab0: 4;
				unsigned int sw_diag_adjgain_tab1: 4;
				unsigned int sw_diag_adjgain_tab2: 4;
				unsigned int sw_diag_adjgain_tab3: 4;
				unsigned int sw_diag_adjgain_tab4: 4;
				unsigned int sw_diag_adjgain_tab5: 4;
				unsigned int sw_diag_adjgain_tab6: 4;
				unsigned int sw_diag_adjgain_tab7: 4;
			} bits;
			unsigned int u32;
		} sw_peaking_ctrl2;
		union peaking_ctrl3_u { 
			struct peaking_ctrl3_s { 
				unsigned int sw_edge_alpha_over_non: 7;
				unsigned int reserve_0: 1;
				unsigned int sw_edge_alpha_under_non: 7;
				unsigned int reserve_1: 1;
				unsigned int sw_edge_alpha_over_unlimit_non: 7;
				unsigned int reserve_2: 1;
				unsigned int sw_edge_alpha_under_unlimit_non: 7;
				unsigned int reserve_3: 1;
			} bits;
			unsigned int u32;
		} sw_peaking_ctrl3;
		union peaking_ctrl4_u { 
			struct peaking_ctrl4_s { 
				unsigned int sw_edge_alpha_over_v: 7;
				unsigned int reserve_0: 1;
				unsigned int sw_edge_alpha_under_v: 7;
				unsigned int reserve_1: 1;
				unsigned int sw_edge_alpha_over_unlimit_v: 7;
				unsigned int reserve_2: 1;
				unsigned int sw_edge_alpha_under_unlimit_v: 7;
				unsigned int reserve_3: 1;
			} bits;
			unsigned int u32;
		} sw_peaking_ctrl4;
		union peaking_ctrl5_u { 
			struct peaking_ctrl5_s { 
				unsigned int sw_edge_alpha_over_h: 7;
				unsigned int reserve_0: 1;
				unsigned int sw_edge_alpha_under_h: 7;
				unsigned int reserve_1: 1;
				unsigned int sw_edge_alpha_over_unlimit_h: 7;
				unsigned int reserve_2: 1;
				unsigned int sw_edge_alpha_under_unlimit_h: 7;
				unsigned int reserve_3: 1;
			} bits;
			unsigned int u32;
		} sw_peaking_ctrl5;
		union peaking_ctrl6_u { 
			struct peaking_ctrl6_s { 
				unsigned int sw_edge_alpha_over_d0: 7;
				unsigned int reserve_0: 1;
				unsigned int sw_edge_alpha_under_d0: 7;
				unsigned int reserve_1: 1;
				unsigned int sw_edge_alpha_over_unlimit_d0: 7;
				unsigned int reserve_2: 1;
				unsigned int sw_edge_alpha_under_unlimit_d0: 7;
				unsigned int reserve_3: 1;
			} bits;
			unsigned int u32;
		} sw_peaking_ctrl6;
		union peaking_ctrl7_u { 
			struct peaking_ctrl7_s { 
				unsigned int sw_edge_alpha_over_d1: 7;
				unsigned int reserve_0: 1;
				unsigned int sw_edge_alpha_under_d1: 7;
				unsigned int reserve_1: 1;
				unsigned int sw_edge_alpha_over_unlimit_d1: 7;
				unsigned int reserve_2: 1;
				unsigned int sw_edge_alpha_under_unlimit_d1: 7;
				unsigned int reserve_3: 1;
			} bits;
			unsigned int u32;
		} sw_peaking_ctrl7;
		union peaking_ctrl8_u { 
			struct peaking_ctrl8_s { 
				unsigned int sw_edge_delta_offset_non: 8;
				unsigned int sw_edge_delta_offset_v: 8;
				unsigned int sw_edge_delta_offset_h: 8;
				unsigned int reserve_0: 8;
			} bits;
			unsigned int u32;
		} sw_peaking_ctrl8;
		union peaking_ctrl9_u { 
			struct peaking_ctrl9_s { 
				unsigned int sw_edge_delta_offset_d0: 8;
				unsigned int sw_edge_delta_offset_d1: 8;
				unsigned int reserve_0: 16;
			} bits;
			unsigned int u32;
		} sw_peaking_ctrl9;
		union shoot_ctrl0_u { 
			struct shoot_ctrl0_s { 
				unsigned int sw_shoot_filt_radius: 1;
				unsigned int reserve_0: 3;
				unsigned int sw_shoot_delta_offset: 8;
				unsigned int sw_shoot_alpha_over: 7;
				unsigned int reserve_1: 1;
				unsigned int sw_shoot_alpha_under: 7;
				unsigned int reserve_2: 5;
			} bits;
			unsigned int u32;
		} sw_shoot_ctrl0;
		union shoot_ctrl1_u { 
			struct shoot_ctrl1_s { 
				unsigned int sw_shoot_alpha_over_unlimit: 7;
				unsigned int reserve_0: 1;
				unsigned int sw_shoot_alpha_under_unlimit: 7;
				unsigned int reserve_1: 17;
			} bits;
			unsigned int u32;
		} sw_shoot_ctrl1;
		union gain_ctrl0_u { 
			struct gain_ctrl0_s { 
				unsigned int sw_adp_idx0: 10;
				unsigned int sw_adp_idx1: 10;
				unsigned int sw_adp_idx2: 10;
				unsigned int reserve_0: 2;
			} bits;
			unsigned int u32;
		} sw_gain_ctrl0;
		union gain_ctrl1_u { 
			struct gain_ctrl1_s { 
				unsigned int sw_adp_idx3: 10;
				unsigned int reserve_0: 2;
				unsigned int sw_adp_gain0: 7;
				unsigned int reserve_1: 1;
				unsigned int sw_adp_gain1: 7;
				unsigned int reserve_2: 5;
			} bits;
			unsigned int u32;
		} sw_gain_ctrl1;
		union gain_ctrl2_u { 
			struct gain_ctrl2_s { 
				unsigned int sw_adp_gain2: 7;
				unsigned int reserve_0: 1;
				unsigned int sw_adp_gain3: 7;
				unsigned int reserve_1: 1;
				unsigned int sw_adp_gain4: 7;
				unsigned int reserve_2: 9;
			} bits;
			unsigned int u32;
		} sw_gain_ctrl2;
		union gain_ctrl3_u { 
			struct gain_ctrl3_s { 
				unsigned int sw_adp_slp01: 11;
				unsigned int reserve_0: 1;
				unsigned int sw_adp_slp12: 11;
				unsigned int reserve_1: 9;
			} bits;
			unsigned int u32;
		} sw_gain_ctrl3;
		struct { 
			unsigned int reserve_data[52];
		} reserve_reg_464_512;
		union gain_ctrl4_u { 
			struct gain_ctrl4_s { 
				unsigned int sw_adp_slp23: 11;
				unsigned int reserve_0: 1;
				unsigned int sw_adp_slp34: 11;
				unsigned int reserve_1: 9;
			} bits;
			unsigned int u32;
		} sw_gain_ctrl4;
		union gain_ctrl5_u { 
			struct gain_ctrl5_s { 
				unsigned int sw_adp_slp45: 11;
				unsigned int sw_var_idx0: 10;
				unsigned int sw_var_idx1: 10;
				unsigned int reserve_0: 1;
			} bits;
			unsigned int u32;
		} sw_gain_ctrl5;
		union gain_ctrl6_u { 
			struct gain_ctrl6_s { 
				unsigned int sw_var_idx2: 10;
				unsigned int reserve_0: 2;
				unsigned int sw_var_idx3: 10;
				unsigned int reserve_1: 2;
				unsigned int sw_var_gain0: 7;
				unsigned int reserve_2: 1;
			} bits;
			unsigned int u32;
		} sw_gain_ctrl6;
		union gain_ctrl7_u { 
			struct gain_ctrl7_s { 
				unsigned int sw_var_gain1: 7;
				unsigned int reserve_0: 1;
				unsigned int sw_var_gain2: 7;
				unsigned int reserve_1: 1;
				unsigned int sw_var_gain3: 7;
				unsigned int reserve_2: 1;
				unsigned int sw_var_gain4: 7;
				unsigned int reserve_3: 1;
			} bits;
			unsigned int u32;
		} sw_gain_ctrl7;
		union gain_ctrl8_u { 
			struct gain_ctrl8_s { 
				unsigned int sw_var_slp01: 11;
				unsigned int reserve_0: 1;
				unsigned int sw_var_slp12: 11;
				unsigned int reserve_1: 9;
			} bits;
			unsigned int u32;
		} sw_gain_ctrl8;
		union gain_ctrl9_u { 
			struct gain_ctrl9_s { 
				unsigned int sw_var_slp23: 11;
				unsigned int reserve_0: 1;
				unsigned int sw_var_slp34: 11;
				unsigned int reserve_1: 9;
			} bits;
			unsigned int u32;
		} sw_gain_ctrl9;
		union gain_ctrl10_u { 
			struct gain_ctrl10_s { 
				unsigned int sw_var_slp45: 11;
				unsigned int reserve_0: 5;
				unsigned int sw_lum_select: 2;
				unsigned int reserve_1: 2;
				unsigned int sw_lum_idx0: 10;
				unsigned int reserve_2: 2;
			} bits;
			unsigned int u32;
		} sw_gain_ctrl10;
		union gain_ctrl11_u { 
			struct gain_ctrl11_s { 
				unsigned int sw_lum_idx1: 10;
				unsigned int sw_lum_idx2: 10;
				unsigned int sw_lum_idx3: 10;
				unsigned int reserve_0: 2;
			} bits;
			unsigned int u32;
		} sw_gain_ctrl11;
		union gain_ctrl12_u { 
			struct gain_ctrl12_s { 
				unsigned int sw_lum_gain0: 7;
				unsigned int reserve_0: 1;
				unsigned int sw_lum_gain1: 7;
				unsigned int reserve_1: 1;
				unsigned int sw_lum_gain2: 7;
				unsigned int reserve_2: 1;
				unsigned int sw_lum_gain3: 7;
				unsigned int reserve_3: 1;
			} bits;
			unsigned int u32;
		} sw_gain_ctrl12;
		union gain_ctrl13_u { 
			struct gain_ctrl13_s { 
				unsigned int sw_lum_gain4: 7;
				unsigned int reserve_0: 1;
				unsigned int sw_lum_slp01: 11;
				unsigned int reserve_1: 1;
				unsigned int sw_lum_slp12: 11;
				unsigned int reserve_2: 1;
			} bits;
			unsigned int u32;
		} sw_gain_ctrl13;
		union gain_ctrl14_u { 
			struct gain_ctrl14_s { 
				unsigned int sw_lum_slp23: 11;
				unsigned int reserve_0: 1;
				unsigned int sw_lum_slp34: 11;
				unsigned int reserve_1: 9;
			} bits;
			unsigned int u32;
		} sw_gain_ctrl14;
		union gain_ctrl15_u { 
			struct gain_ctrl15_s { 
				unsigned int sw_lum_slp45: 11;
				unsigned int reserve_0: 21;
			} bits;
			unsigned int u32;
		} sw_gain_ctrl15;
		union coloradj_ctrl0_u { 
			struct coloradj_ctrl0_s { 
				unsigned int sw_adj_point_x0: 10;
				unsigned int reserve_0: 2;
				unsigned int sw_adj_point_y0: 10;
				unsigned int reserve_1: 2;
				unsigned int sw_adj_scaling_coef0: 3;
				unsigned int reserve_2: 5;
			} bits;
			unsigned int u32;
		} sw_coloradj_ctrl0;
		union coloradj_ctrl1_u { 
			struct coloradj_ctrl1_s { 
				unsigned int sw_coloradj_tab0_0: 5;
				unsigned int sw_coloradj_tab0_1: 5;
				unsigned int sw_coloradj_tab0_2: 5;
				unsigned int sw_coloradj_tab0_3: 5;
				unsigned int sw_coloradj_tab0_4: 5;
				unsigned int sw_coloradj_tab0_5: 5;
				unsigned int reserve_0: 2;
			} bits;
			unsigned int u32;
		} sw_coloradj_ctrl1;
		union coloradj_ctrl2_u { 
			struct coloradj_ctrl2_s { 
				unsigned int sw_coloradj_tab0_6: 5;
				unsigned int sw_coloradj_tab0_7: 5;
				unsigned int sw_coloradj_tab0_8: 5;
				unsigned int sw_coloradj_tab0_9: 5;
				unsigned int sw_coloradj_tab0_10: 5;
				unsigned int sw_coloradj_tab0_11: 5;
				unsigned int reserve_0: 2;
			} bits;
			unsigned int u32;
		} sw_coloradj_ctrl2;
		union coloradj_ctrl3_u { 
			struct coloradj_ctrl3_s { 
				unsigned int sw_coloradj_tab0_12: 5;
				unsigned int sw_coloradj_tab0_13: 5;
				unsigned int sw_coloradj_tab0_14: 5;
				unsigned int sw_coloradj_tab0_15: 5;
				unsigned int reserve_0: 12;
			} bits;
			unsigned int u32;
		} sw_coloradj_ctrl3;
		union coloradj_ctrl4_u { 
			struct coloradj_ctrl4_s { 
				unsigned int sw_adj_point_x1: 10;
				unsigned int reserve_0: 2;
				unsigned int sw_adj_point_y1: 10;
				unsigned int reserve_1: 2;
				unsigned int sw_adj_scaling_coef1: 3;
				unsigned int reserve_2: 5;
			} bits;
			unsigned int u32;
		} sw_coloradj_ctrl4;
		union coloradj_ctrl5_u { 
			struct coloradj_ctrl5_s { 
				unsigned int sw_coloradj_tab1_0: 5;
				unsigned int sw_coloradj_tab1_1: 5;
				unsigned int sw_coloradj_tab1_2: 5;
				unsigned int sw_coloradj_tab1_3: 5;
				unsigned int sw_coloradj_tab1_4: 5;
				unsigned int sw_coloradj_tab1_5: 5;
				unsigned int reserve_0: 2;
			} bits;
			unsigned int u32;
		} sw_coloradj_ctrl5;
		union coloradj_ctrl6_u { 
			struct coloradj_ctrl6_s { 
				unsigned int sw_coloradj_tab1_6: 5;
				unsigned int sw_coloradj_tab1_7: 5;
				unsigned int sw_coloradj_tab1_8: 5;
				unsigned int sw_coloradj_tab1_9: 5;
				unsigned int sw_coloradj_tab1_10: 5;
				unsigned int sw_coloradj_tab1_11: 5;
				unsigned int reserve_0: 2;
			} bits;
			unsigned int u32;
		} sw_coloradj_ctrl6;
		union coloradj_ctrl7_u { 
			struct coloradj_ctrl7_s { 
				unsigned int sw_coloradj_tab1_12: 5;
				unsigned int sw_coloradj_tab1_13: 5;
				unsigned int sw_coloradj_tab1_14: 5;
				unsigned int sw_coloradj_tab1_15: 5;
				unsigned int reserve_0: 12;
			} bits;
			unsigned int u32;
		} sw_coloradj_ctrl7;
		union coloradj_ctrl8_u { 
			struct coloradj_ctrl8_s { 
				unsigned int sw_adj_point_x2: 10;
				unsigned int reserve_0: 2;
				unsigned int sw_adj_point_y2: 10;
				unsigned int reserve_1: 2;
				unsigned int sw_adj_scaling_coef2: 3;
				unsigned int reserve_2: 5;
			} bits;
			unsigned int u32;
		} sw_coloradj_ctrl8;
		union coloradj_ctrl9_u { 
			struct coloradj_ctrl9_s { 
				unsigned int sw_coloradj_tab2_0: 5;
				unsigned int sw_coloradj_tab2_1: 5;
				unsigned int sw_coloradj_tab2_2: 5;
				unsigned int sw_coloradj_tab2_3: 5;
				unsigned int sw_coloradj_tab2_4: 5;
				unsigned int sw_coloradj_tab2_5: 5;
				unsigned int reserve_0: 2;
			} bits;
			unsigned int u32;
		} sw_coloradj_ctrl9;
		union coloradj_ctrl10_u { 
			struct coloradj_ctrl10_s { 
				unsigned int sw_coloradj_tab2_6: 5;
				unsigned int sw_coloradj_tab2_7: 5;
				unsigned int sw_coloradj_tab2_8: 5;
				unsigned int sw_coloradj_tab2_9: 5;
				unsigned int sw_coloradj_tab2_10: 5;
				unsigned int sw_coloradj_tab2_11: 5;
				unsigned int reserve_0: 2;
			} bits;
			unsigned int u32;
		} sw_coloradj_ctrl10;
		union coloradj_ctrl11_u { 
			struct coloradj_ctrl11_s { 
				unsigned int sw_coloradj_tab2_12: 5;
				unsigned int sw_coloradj_tab2_13: 5;
				unsigned int sw_coloradj_tab2_14: 5;
				unsigned int sw_coloradj_tab2_15: 5;
				unsigned int reserve_0: 12;
			} bits;
			unsigned int u32;
		} sw_coloradj_ctrl11;
		union coloradj_ctrl12_u { 
			struct coloradj_ctrl12_s { 
				unsigned int sw_adj_point_x3: 10;
				unsigned int reserve_0: 2;
				unsigned int sw_adj_point_y3: 10;
				unsigned int reserve_1: 2;
				unsigned int sw_adj_scaling_coef3: 3;
				unsigned int reserve_2: 5;
			} bits;
			unsigned int u32;
		} sw_coloradj_ctrl12;
		union coloradj_ctrl13_u { 
			struct coloradj_ctrl13_s { 
				unsigned int sw_coloradj_tab3_0: 5;
				unsigned int sw_coloradj_tab3_1: 5;
				unsigned int sw_coloradj_tab3_2: 5;
				unsigned int sw_coloradj_tab3_3: 5;
				unsigned int sw_coloradj_tab3_4: 5;
				unsigned int sw_coloradj_tab3_5: 5;
				unsigned int reserve_0: 2;
			} bits;
			unsigned int u32;
		} sw_coloradj_ctrl13;
		union coloradj_ctrl14_u { 
			struct coloradj_ctrl14_s { 
				unsigned int sw_coloradj_tab3_6: 5;
				unsigned int sw_coloradj_tab3_7: 5;
				unsigned int sw_coloradj_tab3_8: 5;
				unsigned int sw_coloradj_tab3_9: 5;
				unsigned int sw_coloradj_tab3_10: 5;
				unsigned int sw_coloradj_tab3_11: 5;
				unsigned int reserve_0: 2;
			} bits;
			unsigned int u32;
		} sw_coloradj_ctrl14;
		union coloradj_ctrl15_u { 
			struct coloradj_ctrl15_s { 
				unsigned int sw_coloradj_tab3_12: 5;
				unsigned int sw_coloradj_tab3_13: 5;
				unsigned int sw_coloradj_tab3_14: 5;
				unsigned int sw_coloradj_tab3_15: 5;
				unsigned int reserve_0: 12;
			} bits;
			unsigned int u32;
		} sw_coloradj_ctrl15;
		union texture_ctrl0_u { 
			struct texture_ctrl0_s { 
				unsigned int sw_idxmode_select: 1;
				unsigned int sw_ymode_select: 2;
				unsigned int reserve_0: 1;
				unsigned int sw_tex_idx0: 10;
				unsigned int reserve_1: 2;
				unsigned int sw_tex_idx1: 10;
				unsigned int reserve_2: 6;
			} bits;
			unsigned int u32;
		} sw_texture_ctrl0;
		union texture_ctrl1_u { 
			struct texture_ctrl1_s { 
				unsigned int sw_tex_idx2: 10;
				unsigned int reserve_0: 2;
				unsigned int sw_tex_idx3: 10;
				unsigned int reserve_1: 2;
				unsigned int sw_tex_gain0: 7;
				unsigned int reserve_2: 1;
			} bits;
			unsigned int u32;
		} sw_texture_ctrl1;
		union texture_ctrl2_u { 
			struct texture_ctrl2_s { 
				unsigned int sw_tex_gain1: 7;
				unsigned int reserve_0: 1;
				unsigned int sw_tex_gain2: 7;
				unsigned int reserve_1: 1;
				unsigned int sw_tex_gain3: 7;
				unsigned int reserve_2: 1;
				unsigned int sw_tex_gain4: 7;
				unsigned int reserve_3: 1;
			} bits;
			unsigned int u32;
		} sw_texture_ctrl2;
		union texture_ctrl3_u { 
			struct texture_ctrl3_s { 
				unsigned int sw_tex_slp01: 11;
				unsigned int reserve_0: 1;
				unsigned int sw_tex_slp12: 11;
				unsigned int reserve_1: 9;
			} bits;
			unsigned int u32;
		} sw_texture_ctrl3;
		union texture_ctrl4_u { 
			struct texture_ctrl4_s { 
				unsigned int sw_tex_slp23: 11;
				unsigned int reserve_0: 1;
				unsigned int sw_tex_slp34: 11;
				unsigned int reserve_1: 9;
			} bits;
			unsigned int u32;
		} sw_texture_ctrl4;
		union texture_ctrl5_u { 
			struct texture_ctrl5_s { 
				unsigned int sw_tex_slp45: 11;
				unsigned int reserve_0: 21;
			} bits;
			unsigned int u32;
		} sw_texture_ctrl5;
		union lti_ctrl0_u { 
			struct lti_ctrl0_s { 
				unsigned int sw_ltih_radius: 1;
				unsigned int reserve_0: 3;
				unsigned int sw_ltih_slp1: 9;
				unsigned int reserve_1: 3;
				unsigned int sw_ltih_thr1: 9;
				unsigned int reserve_2: 7;
			} bits;
			unsigned int u32;
		} sw_lti_ctrl0;
		union lti_ctrl1_u { 
			struct lti_ctrl1_s { 
				unsigned int sw_ltih_noisethrneg: 10;
				unsigned int reserve_0: 2;
				unsigned int sw_ltih_noisethrpos: 10;
				unsigned int reserve_1: 2;
				unsigned int sw_ltih_tigain: 5;
				unsigned int reserve_2: 3;
			} bits;
			unsigned int u32;
		} sw_lti_ctrl1;
		union lti_ctrl2_u { 
			struct lti_ctrl2_s { 
				unsigned int sw_ltiv_radius: 1;
				unsigned int reserve_0: 3;
				unsigned int sw_ltiv_slp1: 9;
				unsigned int reserve_1: 3;
				unsigned int sw_ltiv_thr1: 9;
				unsigned int reserve_2: 7;
			} bits;
			unsigned int u32;
		} sw_lti_ctrl2;
		union lti_ctrl3_u { 
			struct lti_ctrl3_s { 
				unsigned int sw_ltiv_noisethrneg: 10;
				unsigned int reserve_0: 2;
				unsigned int sw_ltiv_noisethrpos: 10;
				unsigned int reserve_1: 2;
				unsigned int sw_ltiv_tigain: 5;
				unsigned int reserve_2: 3;
			} bits;
			unsigned int u32;
		} sw_lti_ctrl3;
		union cti_ctrl0_u { 
			struct cti_ctrl0_s { 
				unsigned int sw_ctih_radius: 1;
				unsigned int reserve_0: 3;
				unsigned int sw_ctih_slp1: 9;
				unsigned int reserve_1: 3;
				unsigned int sw_ctih_thr1: 9;
				unsigned int reserve_2: 7;
			} bits;
			unsigned int u32;
		} sw_cti_ctrl0;
		union cti_ctrl1_u { 
			struct cti_ctrl1_s { 
				unsigned int sw_ctih_noisethrneg: 10;
				unsigned int reserve_0: 2;
				unsigned int sw_ctih_noisethrpos: 10;
				unsigned int reserve_1: 2;
				unsigned int sw_ctih_tigain: 5;
				unsigned int reserve_2: 3;
			} bits;
			unsigned int u32;
		} sw_cti_ctrl1;
		union cti_ctrl2_u { 
			struct cti_ctrl2_s { 
				unsigned int sw_ctiv_radius: 1;
				unsigned int reserve_0: 3;
				unsigned int sw_ctiv_slp1: 9;
				unsigned int reserve_1: 3;
				unsigned int sw_ctiv_thr1: 9;
				unsigned int reserve_2: 7;
			} bits;
			unsigned int u32;
		} sw_cti_ctrl2;
		union cti_ctrl3_u { 
			struct cti_ctrl3_s { 
				unsigned int sw_ctiv_noisethrneg: 10;
				unsigned int reserve_0: 2;
				unsigned int sw_ctiv_noisethrpos: 10;
				unsigned int reserve_1: 2;
				unsigned int sw_ctiv_tigain: 5;
				unsigned int reserve_2: 3;
			} bits;
			unsigned int u32;
		} sw_cti_ctrl3;
		union dbg_ctrl0_u { 
			struct dbg_ctrl0_s { 
				unsigned int sw_debug_mode: 4;
				unsigned int reserve_0: 28;
			} bits;
			unsigned int u32;
		} sw_dbg_ctrl0;
		union roi_ctrl0_u { 
			struct roi_ctrl0_s { 
				unsigned int sw_roi_xstart: 12;
				unsigned int reserve_0: 4;
				unsigned int sw_roi_ystart: 12;
				unsigned int reserve_1: 3;
				unsigned int sw_roi_en: 1;
			} bits;
			unsigned int u32;
		} sw_roi_ctrl0;
		union roi_ctrl1_u { 
			struct roi_ctrl1_s { 
				unsigned int sw_roi_xend: 12;
				unsigned int reserve_0: 4;
				unsigned int sw_roi_yend: 12;
				unsigned int reserve_1: 4;
			} bits;
			unsigned int u32;
		} sw_roi_ctrl1;
	} regs;
	unsigned int p_reg_addr[161];
}sharp_0x27d06c00_t;

typedef union mmu0_0x27d07e00_u {
	struct mmu0_0x27d07e00_s {
		union mmu_dte_addr_u { 
			struct mmu_dte_addr_s { 
				unsigned int dte_addr: 32;
			} bits;
			unsigned int u32;
		} sw_mmu_dte_addr;
		union mmu_status_u { 
			struct mmu_status_s { 
				unsigned int paging_en: 1;
				unsigned int page_fault_active: 1;
				unsigned int stail_active: 1;
				unsigned int mmu_idle: 1;
				unsigned int replay_buffer_empty: 1;
				unsigned int page_fault_is_write: 1;
				unsigned int page_fault_bus_id: 5;
				unsigned int reserve_0: 21;
			} bits;
			unsigned int u32;
		} sw_mmu_status;
		union mmu_command_u { 
			struct mmu_command_s { 
				unsigned int mmu_cmd: 3;
				unsigned int reserve_0: 29;
			} bits;
			unsigned int u32;
		} sw_mmu_command;
		union mmu_page_fault_addr_u { 
			struct mmu_page_fault_addr_s { 
				unsigned int page_fault_addr: 32;
			} bits;
			unsigned int u32;
		} sw_mmu_page_fault_addr;
		union mmu_zap_one_line_u { 
			struct mmu_zap_one_line_s { 
				unsigned int mmu_zap_one_line: 32;
			} bits;
			unsigned int u32;
		} sw_mmu_zap_one_line;
		union mmu_int_rawstat_u { 
			struct mmu_int_rawstat_s { 
				unsigned int rawst_page_fault: 1;
				unsigned int rawst_bus_error: 1;
				unsigned int reserve_0: 30;
			} bits;
			unsigned int u32;
		} sw_mmu_int_rawstat;
		union mmu_int_clear_u { 
			struct mmu_int_clear_s { 
				unsigned int clr_page_fault: 1;
				unsigned int clr_bus_error: 1;
				unsigned int reserve_0: 30;
			} bits;
			unsigned int u32;
		} sw_mmu_int_clear;
		union mmu_int_mask_u { 
			struct mmu_int_mask_s { 
				unsigned int mask_page_fault: 1;
				unsigned int mask_bus_error: 1;
				unsigned int reserve_0: 30;
			} bits;
			unsigned int u32;
		} sw_mmu_int_mask;
		union mmu_int_status_u { 
			struct mmu_int_status_s { 
				unsigned int st_page_fault: 1;
				unsigned int st_bus_error: 1;
				unsigned int reserve_0: 30;
			} bits;
			unsigned int u32;
		} sw_mmu_int_status;
		union mmu_auto_gating_u { 
			struct mmu_auto_gating_s { 
				unsigned int mmu_auto_gating: 1;
				unsigned int mmu_cfg_mode: 1;
				unsigned int reserve_0: 30;
			} bits;
			unsigned int u32;
		} sw_mmu_auto_gating;
	} regs;
	unsigned int p_reg_addr[10];
}mmu0_0x27d07e00_t;

typedef union mmu1_0x27d07f00_u {
	struct mmu1_0x27d07f00_s {
		union mmu_dte_addr_u { 
			struct mmu_dte_addr_s { 
				unsigned int dte_addr: 32;
			} bits;
			unsigned int u32;
		} sw_mmu_dte_addr;
		union mmu_status_u { 
			struct mmu_status_s { 
				unsigned int paging_en: 1;
				unsigned int page_fault_active: 1;
				unsigned int stail_active: 1;
				unsigned int mmu_idle: 1;
				unsigned int replay_buffer_empty: 1;
				unsigned int page_fault_is_write: 1;
				unsigned int page_fault_bus_id: 5;
				unsigned int reserve_0: 21;
			} bits;
			unsigned int u32;
		} sw_mmu_status;
		union mmu_command_u { 
			struct mmu_command_s { 
				unsigned int mmu_cmd: 3;
				unsigned int reserve_0: 29;
			} bits;
			unsigned int u32;
		} sw_mmu_command;
		union mmu_page_fault_addr_u { 
			struct mmu_page_fault_addr_s { 
				unsigned int page_fault_addr: 32;
			} bits;
			unsigned int u32;
		} sw_mmu_page_fault_addr;
		union mmu_zap_one_line_u { 
			struct mmu_zap_one_line_s { 
				unsigned int mmu_zap_one_line: 32;
			} bits;
			unsigned int u32;
		} sw_mmu_zap_one_line;
		union mmu_int_rawstat_u { 
			struct mmu_int_rawstat_s { 
				unsigned int rawst_page_fault: 1;
				unsigned int rawst_bus_error: 1;
				unsigned int reserve_0: 30;
			} bits;
			unsigned int u32;
		} sw_mmu_int_rawstat;
		union mmu_int_clear_u { 
			struct mmu_int_clear_s { 
				unsigned int clr_page_fault: 1;
				unsigned int clr_bus_error: 1;
				unsigned int reserve_0: 30;
			} bits;
			unsigned int u32;
		} sw_mmu_int_clear;
		union mmu_int_mask_u { 
			struct mmu_int_mask_s { 
				unsigned int mask_page_fault: 1;
				unsigned int mask_bus_error: 1;
				unsigned int reserve_0: 30;
			} bits;
			unsigned int u32;
		} sw_mmu_int_mask;
		union mmu_int_status_u { 
			struct mmu_int_status_s { 
				unsigned int st_page_fault: 1;
				unsigned int st_bus_error: 1;
				unsigned int reserve_0: 30;
			} bits;
			unsigned int u32;
		} sw_mmu_int_status;
		union mmu_auto_gating_u { 
			struct mmu_auto_gating_s { 
				unsigned int mmu_auto_gating: 1;
				unsigned int mmu_cfg_mode: 1;
				unsigned int reserve_0: 30;
			} bits;
			unsigned int u32;
		} sw_mmu_auto_gating;
	} regs;
	unsigned int p_reg_addr[10];
}mmu1_0x27d07f00_t;

#endif //__RK3576_VOP_REGS_H__
