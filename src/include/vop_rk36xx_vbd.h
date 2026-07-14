#ifndef VOP_RK36XX_VBD_H
#define VOP_RK36XX_VBD_H

typedef union vbd_rk36xx {
    struct {
        union { // name: start, offset: 0x0
            struct {
                unsigned int vbd_start : 1;
                unsigned int reserve_0 : 31;
            } bits;
            unsigned int val;
        } start;
        union { // name: soft_reset, offset: 0x4
            struct {
                unsigned int soft_rst  : 1;
                unsigned int reserve_0 : 31;
            } bits;
            unsigned int val;
        } soft_reset;
        union { // name: version, offset: 0x8
            struct {
                unsigned int version : 32;
            } bits;
            unsigned int val;
        } version;
        union { // name: auto_gating, offset: 0xc
            struct {
                unsigned int auto_gating_en : 1;
                unsigned int reserve_0      : 31;
            } bits;
            unsigned int val;
        } auto_gating;
        union { // name: status0, offset: 0x10
            struct {
                unsigned int core_is_idle   : 1;
                unsigned int reserve_0      : 3;
                unsigned int mmu_is_idle    : 1;
                unsigned int afbc_is_idle   : 1;
                unsigned int axi_wr_is_idle : 1;
                unsigned int axi_rd_is_idle : 1;
                unsigned int reserve_1      : 24;
            } bits;
            unsigned int val;
        } status0;
        union { // name: status1, offset: 0x14
            struct {
                unsigned int scan_line_cnt : 16;
                unsigned int reserve_0     : 16;
            } bits;
            unsigned int val;
        } status1;
        union { // name: status2, offset: 0x18
            struct {
                unsigned int pld_last_waddr : 32;
            } bits;
            unsigned int val;
        } status2;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_28_32;
        union { // name: int_en, offset: 0x20
            struct {
                unsigned int intr_en_wb_dma_finish  : 1;
                unsigned int intr_en_dma_finish     : 1;
                unsigned int intr_en_line_flag0     : 1;
                unsigned int intr_en_line_flag1     : 1;
                unsigned int intr_en_yhdr_overflow  : 1;
                unsigned int intr_en_yhdr_underflow : 1;
                unsigned int intr_en_cpld_overflow  : 1;
                unsigned int intr_en_cpld_underflow : 1;
                unsigned int intr_en_wb_timeout     : 1;
                unsigned int intr_en_wb_resp_err    : 1;
                unsigned int intr_en_rd_resp_err    : 1;
                unsigned int intr_en_mmu            : 1;
                unsigned int reserve_0              : 4;
                unsigned int write_mask             : 16;
            } bits;
            unsigned int val;
        } int_en;
        union { // name: int_clr, offset: 0x24
            struct {
                unsigned int intr_clr_wb_dma_finish  : 1;
                unsigned int intr_clr_dma_finish     : 1;
                unsigned int intr_clr_line_flag0     : 1;
                unsigned int intr_clr_line_flag1     : 1;
                unsigned int intr_clr_yhdr_overflow  : 1;
                unsigned int intr_clr_yhdr_underflow : 1;
                unsigned int intr_clr_cpld_overflow  : 1;
                unsigned int intr_clr_cpld_underflow : 1;
                unsigned int intr_clr_wb_timeout     : 1;
                unsigned int intr_clr_wb_resp_err    : 1;
                unsigned int intr_clr_rd_resp_err    : 1;
                unsigned int intr_clr_mmu            : 1;
                unsigned int reserve_0               : 4;
                unsigned int write_mask              : 16;
            } bits;
            unsigned int val;
        } int_clr;
        union { // name: int_msk, offset: 0x28
            struct {
                unsigned int intr_msk_wb_dma_finish  : 1;
                unsigned int intr_msk_rd_dma_finish  : 1;
                unsigned int intr_msk_line_flag0     : 1;
                unsigned int intr_msk_line_flag1     : 1;
                unsigned int intr_msk_yhdr_overflow  : 1;
                unsigned int intr_msk_yhdr_underflow : 1;
                unsigned int intr_msk_cpld_overflow  : 1;
                unsigned int intr_msk_cpld_underflow : 1;
                unsigned int intr_msk_wb_timeout     : 1;
                unsigned int intr_msk_wb_resp_err    : 1;
                unsigned int intr_msk_rd_resp_err    : 1;
                unsigned int intr_msk_mmu            : 1;
                unsigned int reserve_0               : 20;
            } bits;
            unsigned int val;
        } int_msk;
        union { // name: int_raw, offset: 0x2c
            struct {
                unsigned int intr_raw_wb_dma_finish  : 1;
                unsigned int intr_raw_rd_dma_finish  : 1;
                unsigned int intr_raw_line_flag0     : 1;
                unsigned int intr_raw_line_flag1     : 1;
                unsigned int intr_raw_yhdr_overflow  : 1;
                unsigned int intr_raw_yhdr_underflow : 1;
                unsigned int intr_raw_cpld_overflow  : 1;
                unsigned int intr_raw_cpld_underflow : 1;
                unsigned int intr_raw_wb_timeout     : 1;
                unsigned int intr_raw_wb_resp_err    : 1;
                unsigned int intr_raw_rd_resp_err    : 1;
                unsigned int intr_raw_mmu            : 1;
                unsigned int reserve_0               : 20;
            } bits;
            unsigned int val;
        } int_raw;
        union { // name: dma_ctrl, offset: 0x30
            struct {
                unsigned int dma_stop_en        : 1;
                unsigned int outstanding_en     : 1;
                unsigned int reserve_0          : 2;
                unsigned int outstanding_num    : 8;
                unsigned int noc_rd_hurry_en    : 1;
                unsigned int noc_rd_hurry_value : 2;
                unsigned int reserve_1          : 1;
                unsigned int noc_wr_hurry_mode  : 2;
                unsigned int noc_wr_hurry_value : 2;
                unsigned int noc_rd_qos_en      : 1;
                unsigned int noc_rd_qos_value   : 2;
                unsigned int reserve_2          : 1;
                unsigned int mmu_qos_en         : 1;
                unsigned int mmu_qos_value      : 3;
                unsigned int reserve_3          : 4;
            } bits;
            unsigned int val;
        } dma_ctrl;
        struct {
            unsigned int reserve_data[3];
        } reserve_reg_52_64;
        union { // name: wb_ctrl, offset: 0x40
            struct {
                unsigned int wb_en                          : 1;
                unsigned int wb_afbce_en                    : 1;
                unsigned int wb_afbce_mode                  : 2;
                unsigned int wb_fmt                         : 4;
                unsigned int wb_dma_stop                    : 1;
                unsigned int wb_force_mdwrite_en            : 1;
                unsigned int reserve_0                      : 2;
                unsigned int wb_afbce_yuv_trans             : 1;
                unsigned int wb_afbce_rgb888_lowhalf_nocopy : 1;
                unsigned int wb_afbce_yc_swap               : 1;
                unsigned int wb_dma_opt_en                  : 1;
                unsigned int wb_rid0                        : 5;
                unsigned int reserve_1                      : 3;
                unsigned int wb_rid1                        : 5;
                unsigned int reserve_2                      : 3;
            } bits;
            unsigned int val;
        } wb_ctrl;
        union { // name: wb_size, offset: 0x44
            struct {
                unsigned int wb_width  : 13;
                unsigned int reserve_0 : 3;
                unsigned int wb_height : 13;
                unsigned int reserve_1 : 3;
            } bits;
            unsigned int val;
        } wb_size;
        union { // name: wb_vir_stride, offset: 0x48
            struct {
                unsigned int wb_vir_sride_en : 1;
                unsigned int reserve_0       : 15;
                unsigned int wb_vir_stride   : 16;
            } bits;
            unsigned int val;
        } wb_vir_stride;
        union { // name: wb_timeout_ctrl, offset: 0x4c
            struct {
                unsigned int wb_timeout_num : 31;
                unsigned int wb_timeout_en  : 1;
            } bits;
            unsigned int val;
        } wb_timeout_ctrl;
        union { // name: wb_yhdr_mst, offset: 0x50
            struct {
                unsigned int yhdr_mst : 32;
            } bits;
            unsigned int val;
        } wb_yhdr_mst;
        union { // name: wb_cpld_mst, offset: 0x54
            struct {
                unsigned int cpld_mst : 32;
            } bits;
            unsigned int val;
        } wb_cpld_mst;
        union { // name: wb_pld_offset, offset: 0x58
            struct {
                unsigned int wb_pld_offset : 32;
            } bits;
            unsigned int val;
        } wb_pld_offset;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_92_96;
        union { // name: vwin0_ctrl, offset: 0x60
            struct {
                unsigned int win_en           : 1;
                unsigned int win_tile_en      : 1;
                unsigned int win_superblock   : 2;
                unsigned int win_fmt          : 4;
                unsigned int win_uv_swap      : 1;
                unsigned int reserve_0        : 3;
                unsigned int win_rid_yrgb     : 5;
                unsigned int reserve_1        : 3;
                unsigned int win_rid_cbcr     : 5;
                unsigned int reserve_2        : 3;
                unsigned int win_gather_en    : 1;
                unsigned int win_srep_stop_en : 1;
                unsigned int reserve_3        : 2;
            } bits;
            unsigned int val;
        } vwin0_ctrl;
        union { // name: vwin0_vir_stride, offset: 0x64
            struct {
                unsigned int win_vir_stride : 16;
                unsigned int reserve_0      : 16;
            } bits;
            unsigned int val;
        } vwin0_vir_stride;
        union { // name: vwin0_size, offset: 0x68
            struct {
                unsigned int win_width  : 13;
                unsigned int reserve_0  : 3;
                unsigned int win_height : 13;
                unsigned int reserve_1  : 3;
            } bits;
            unsigned int val;
        } vwin0_size;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_108_112;
        union { // name: vwin0_mst0, offset: 0x70
            struct {
                unsigned int win_mst0 : 32;
            } bits;
            unsigned int val;
        } vwin0_mst0;
        struct {
            unsigned int reserve_data[3];
        } reserve_reg_116_128;
        union { // name: vwin1_ctrl, offset: 0x80
            struct {
                unsigned int win_en           : 1;
                unsigned int win_tile_en      : 1;
                unsigned int win_superblock   : 2;
                unsigned int win_fmt          : 4;
                unsigned int win_uv_swap      : 1;
                unsigned int reserve_0        : 3;
                unsigned int win_rid_yrgb     : 5;
                unsigned int reserve_1        : 3;
                unsigned int win_rid_cbcr     : 5;
                unsigned int reserve_2        : 3;
                unsigned int win_gather_en    : 1;
                unsigned int win_srep_stop_en : 1;
                unsigned int reserve_3        : 2;
            } bits;
            unsigned int val;
        } vwin1_ctrl;
        union { // name: vwin1_vir_stride, offset: 0x84
            struct {
                unsigned int win_vir_stride : 16;
                unsigned int reserve_0      : 16;
            } bits;
            unsigned int val;
        } vwin1_vir_stride;
        union { // name: vwin1_size, offset: 0x88
            struct {
                unsigned int win_width  : 13;
                unsigned int reserve_0  : 3;
                unsigned int win_height : 13;
                unsigned int reserve_1  : 3;
            } bits;
            unsigned int val;
        } vwin1_size;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_140_144;
        union { // name: vwin1_mst0, offset: 0x90
            struct {
                unsigned int win_mst0 : 32;
            } bits;
            unsigned int val;
        } vwin1_mst0;
        struct {
            unsigned int reserve_data[3];
        } reserve_reg_148_160;
        union { // name: awin_ctrl, offset: 0xa0
            struct {
                unsigned int win_en           : 1;
                unsigned int win_tile_en      : 1;
                unsigned int win_superblock   : 2;
                unsigned int win_fmt          : 4;
                unsigned int win_uv_swap      : 1;
                unsigned int reserve_0        : 3;
                unsigned int win_rid_yrgb     : 5;
                unsigned int reserve_1        : 3;
                unsigned int win_rid_cbcr     : 5;
                unsigned int reserve_2        : 3;
                unsigned int win_gather_en    : 1;
                unsigned int win_srep_stop_en : 1;
                unsigned int reserve_3        : 2;
            } bits;
            unsigned int val;
        } awin_ctrl;
        union { // name: awin_vir_stride, offset: 0xa4
            struct {
                unsigned int win_vir_stride : 16;
                unsigned int reserve_0      : 16;
            } bits;
            unsigned int val;
        } awin_vir_stride;
        union { // name: awin_size, offset: 0xa8
            struct {
                unsigned int win_width  : 13;
                unsigned int reserve_0  : 3;
                unsigned int win_height : 13;
                unsigned int reserve_1  : 3;
            } bits;
            unsigned int val;
        } awin_size;
        struct {
            unsigned int reserve_data[1];
        } reserve_reg_172_176;
        union { // name: awin_mst, offset: 0xb0
            struct {
                unsigned int win_mst0 : 32;
            } bits;
            unsigned int val;
        } awin_mst;
        struct {
            unsigned int reserve_data[3];
        } reserve_reg_180_192;
        union { // name: src_color_ctrl, offset: 0xc0
            struct {
                unsigned int src_color_mode     : 1;
                unsigned int src_alpha_mode     : 1;
                unsigned int src_blend_mode     : 2;
                unsigned int src_alpha_cal_mode : 1;
                unsigned int src_factor_mode    : 3;
                unsigned int alpha_en           : 1;
                unsigned int reserve_0          : 7;
                unsigned int src_global_alpha   : 8;
                unsigned int reserve_1          : 8;
            } bits;
            unsigned int val;
        } src_color_ctrl;
        union { // name: dst_color_ctrl, offset: 0xc4
            struct {
                unsigned int dst_color_mode     : 1;
                unsigned int dst_alpha_mode     : 1;
                unsigned int dst_blend_mode     : 2;
                unsigned int dst_alpha_cal_mode : 1;
                unsigned int dst_factor_mode    : 3;
                unsigned int reserve_0          : 8;
                unsigned int dst_global_alpha   : 8;
                unsigned int reserve_1          : 8;
            } bits;
            unsigned int val;
        } dst_color_ctrl;
        struct {
            unsigned int reserve_data[6];
        } reserve_reg_200_224;
        union { // name: axi_perf_ctrl0, offset: 0xe0
            struct {
                unsigned int axi_perf_work          : 1;
                unsigned int axi_perf_clr           : 1;
                unsigned int axi_cnt_type           : 1;
                unsigned int reserve_0              : 1;
                unsigned int axi_ddr_align_type     : 2;
                unsigned int reserve_1              : 2;
                unsigned int axi_perf_rd_latency_id : 5;
                unsigned int reserve_2              : 3;
                unsigned int axi_ar_count_id        : 5;
                unsigned int axi_ar_cnt_id_type     : 1;
                unsigned int reserve_3              : 2;
                unsigned int axi_aw_count_id        : 5;
                unsigned int axi_aw_cnt_id_type     : 1;
                unsigned int reserve_4              : 2;
            } bits;
            unsigned int val;
        } axi_perf_ctrl0;
        union { // name: axi_perf_ctrl1, offset: 0xe4
            struct {
                unsigned int axi_rd_latency_thr      : 12;
                unsigned int reserve_0               : 4;
                unsigned int perf_rd_max_latency_num : 16;
            } bits;
            unsigned int val;
        } axi_perf_ctrl1;
        union { // name: axi_perf_status0, offset: 0xe8
            struct {
                unsigned int perf_rd_latency_samp_num : 32;
            } bits;
            unsigned int val;
        } axi_perf_status0;
        union { // name: axi_perf_status1, offset: 0xec
            struct {
                unsigned int perf_rd_latency_acc_sum : 32;
            } bits;
            unsigned int val;
        } axi_perf_status1;
        union { // name: axi_perf_status2, offset: 0xf0
            struct {
                unsigned int perf_rd_axi_total_byte : 32;
            } bits;
            unsigned int val;
        } axi_perf_status2;
        union { // name: axi_perf_status3, offset: 0xf4
            struct {
                unsigned int perf_wr_axi_total_byte : 1;
                unsigned int reserve_0              : 31;
            } bits;
            unsigned int val;
        } axi_perf_status3;
        union { // name: axi_perf_status4, offset: 0xf8
            struct {
                unsigned int perf_working_cnt : 1;
                unsigned int reserve_0        : 31;
            } bits;
            unsigned int val;
        } axi_perf_status4;
    } regs;
    unsigned int data[63];
} vbd_rk36xx_u;

#endif /* VOP_RK36XX_VBD_H */
