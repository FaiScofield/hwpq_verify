#ifndef __CHIP_REGISTER_H
#define __CHIP_REGISTER_H
///////////////////////////////////////////
//       SYS_CTRL
///////////////////////////////////////////
#define      SYS_CTRL_BASE                        0x00000000

#define      SYS_CTRL_SYS_REG_CFG_DONE            0x000
#define      SYS_CTRL_SYS_VERSION_INFO            0x004
#define      SYS_CTRL_SYS_AUTO_CTRL_IMD           0x008
#define      SYS_CTRL_SYS_AXI0_CTRL_IMD           0x010
#define      SYS_CTRL_SYS_AXI_HURRY_CTRL0_IMD     0x014
#define      SYS_CTRL_SYS_AXI1_CTRL_IMD           0x018
#define      SYS_CTRL_SYS_AXI_HURRY_CTRL1_IMD     0x01C
#define      SYS_CTRL_SYS_MMU_CTRL_IMD            0x020
#define      SYS_CTRL_SYS_AXI_LUT_CTRL_IMD        0x024
#define      SYS_CTRL_SYS_PORT_CTRL_IMD           0x028
#define      SYS_CTRL_SYS_CLUSTER_PD_CTRL_IMD     0x030
#define      SYS_CTRL_SYS_ESMART_PD_CTRL_IMD      0x034
#define      SYS_CTRL_SYS_VAR_FERQ_CTRL_IMD       0x038
#define      SYS_CTRL_METADATA_CTRL               0x040
#define      SYS_CTRL_METADATA_MST                0x044
#define      SYS_CTRL_FBC_TIMEOUT_CTRL            0x048
#define      SYS_CTRL_SYS0_INTR_EN                0x080
#define      SYS_CTRL_SYS0_INTR_CLR               0x084
#define      SYS_CTRL_SYS0_INTR_STATUS            0x088
#define      SYS_CTRL_SYS0_INTR_RAW_STATUS        0x08C
#define      SYS_CTRL_SYS1_INTR_EN                0x090
#define      SYS_CTRL_SYS1_INTR_CLR_SYS           0x094
#define      SYS_CTRL_SYS1_INTR_STATUS            0x098
#define      SYS_CTRL_SYS1_INTR_RAW_STATUS        0x09C
#define      SYS_CTRL_PORT0_INTR_EN               0x0A0
#define      SYS_CTRL_PORT0_INTR_CLR              0x0A4
#define      SYS_CTRL_PORT0_INTR_STATUS           0x0A8
#define      SYS_CTRL_PORT0_INTR_RAW_STATUS       0x0AC
#define      SYS_CTRL_PORT1_INTR_EN               0x0B0
#define      SYS_CTRL_PORT1_INTR_CLR              0x0B4
#define      SYS_CTRL_PORT1_INTR_STATUS           0x0B8
#define      SYS_CTRL_PORT1_INTR_RAW_STATUS       0x0BC
#define      SYS_CTRL_PORT2_INTR_EN               0x0C0
#define      SYS_CTRL_PORT2_INTR_CLR              0x0C4
#define      SYS_CTRL_PORT2_INTR_STATUS           0x0C8
#define      SYS_CTRL_PORT2_INTR_RAW_STATUS       0x0CC
#define      SYS_CTRL_FBCD_INTR_EN0               0x0E0
#define      SYS_CTRL_FBCD_INTR_CLR0              0x0E4
#define      SYS_CTRL_FBCD_INTR_STATUS0           0x0E8
#define      SYS_CTRL_FBCD_INTR_RAW_STATUS0       0x0EC
///////////////////////////////////////////
//       PANEL_CTRL
///////////////////////////////////////////
#define      PANEL_CTRL_BASE                      0x00000100

#define      PANEL_CTRL_MIPI0_INFACE_CTRL         0x000
#define      PANEL_CTRL_HDMI0_INFACE_CTRL         0x004
#define      PANEL_CTRL_EDP0_INFACE_CTRL          0x008
#define      PANEL_CTRL_DP0_INFACE_CTRL           0x00C
#define      PANEL_CTRL_LVDS0_INFACE_CTRL         0x010
#define      PANEL_CTRL_RGB_INFACE_CTRL           0x014
#define      PANEL_CTRL_DP1_INFACE_CTRL           0x024
#define      PANEL_CTRL_LVDS1_INFACE_CTRL         0x028
#define      PANEL_CTRL_DP2_INFACE_CTRL           0x030
///////////////////////////////////////////
//       WB_CTRL
///////////////////////////////////////////
#define      WB_CTRL_BASE                         0x00000200

#define      WB_CTRL_SYS_WB_CTRL0                 0x000
#define      WB_CTRL_SYS_WB_XSPD_FACTOR           0x004
#define      WB_CTRL_SYS_WB_YRGB_MST              0x008
#define      WB_CTRL_SYS_WB_CBR_MST               0x00C
#define      WB_CTRL_SYS_WB_VIR_STRIDE            0x010
#define      WB_CTRL_SYS_WB_TIMEOUT_CTRL          0x014
#define      WB_CTRL_SYS_WB_CFG_DONE              0x01C
///////////////////////////////////////////
//       SECURE_CTRL
///////////////////////////////////////////
#define      SECURE_CTRL_BASE                     0x00000300

#define      SECURE_CTRL_SEC_INFACE_CTRL          0x000
#define      SECURE_CTRL_SEC_DRM_CTRL             0x004
#define      SECURE_CTRL_SEC_DRM_PORT_SEL         0x008
#define      SECURE_CTRL_SEC_PORT0_LAYER_SEL      0x010
#define      SECURE_CTRL_SEC_PORT1_LAYER_SEL      0x014
#define      SECURE_CTRL_SEC_PORT2_LAYER_SEL      0x018
#define      SECURE_CTRL_SEC_AXI_RID_PROT         0x020
#define      SECURE_CTRL_SYS_OTP_MIRR_CTRL_IMD    0x030
///////////////////////////////////////////
//       OVERLAY_PORT0
///////////////////////////////////////////
#define      OVERLAY_PORT0_BASE                   0x00000600

#define      OVERLAY_PORT0_OVERLAY_CTRL           0x00000
#define      OVERLAY_PORT0_LAYER_SEL              0x00004
#define      OVERLAY_PORT0_MIX0_SRC_COLOR_CTRL    0x00020
#define      OVERLAY_PORT0_MIX0_DST_COLOR_CTRL    0x00024
#define      OVERLAY_PORT0_MIX0_SRC_ALPHA_CTRL    0x00028
#define      OVERLAY_PORT0_MIX0_DST_ALPHA_CTRL    0x0002C
#define      OVERLAY_PORT0_MIX1_SRC_COLOR_CTRL    0x00030
#define      OVERLAY_PORT0_MIX1_DST_COLOR_CTRL    0x00034
#define      OVERLAY_PORT0_MIX1_SRC_ALPHA_CTRL    0x00038
#define      OVERLAY_PORT0_MIX1_DST_ALPHA_CTRL    0x0003C
#define      OVERLAY_PORT0_MIX2_SRC_COLOR_CTRL    0x00040
#define      OVERLAY_PORT0_MIX2_DST_COLOR_CTRL    0x00044
#define      OVERLAY_PORT0_MIX2_SRC_ALPHA_CTRL    0x00048
#define      OVERLAY_PORT0_MIX2_DST_ALPHA_CTRL    0x0004C
#define      OVERLAY_PORT0_EXTRA_SRC_COLOR_CTRL   0x00050
#define      OVERLAY_PORT0_EXTRA_DST_COLOR_CTRL   0x00054
#define      OVERLAY_PORT0_EXTRA_SRC_ALPHA_CTRL   0x00058
#define      OVERLAY_PORT0_EXTRA_DST_ALPHA_CTRL   0x0005C
#define      OVERLAY_PORT0_HDR_SRC_COLOR_CTRL     0x00060
#define      OVERLAY_PORT0_HDR_DST_COLOR_CTRL     0x00064
#define      OVERLAY_PORT0_HDR_SRC_ALPHA_CTRL     0x00068
#define      OVERLAY_PORT0_HDR_DST_ALPHA_CTRL     0x0006C
#define      OVERLAY_PORT0_BG_MIX_CTRL            0x00070
///////////////////////////////////////////
//       OVERLAY_PORT1
///////////////////////////////////////////
#define      OVERLAY_PORT1_BASE                   0x00000700

#define      OVERLAY_PORT1_OVERLAY_CTRL           0x00000
#define      OVERLAY_PORT1_LAYER_SEL              0x00004
#define      OVERLAY_PORT1_MIX0_SRC_COLOR_CTRL    0x00020
#define      OVERLAY_PORT1_MIX0_DST_COLOR_CTRL    0x00024
#define      OVERLAY_PORT1_MIX0_SRC_ALPHA_CTRL    0x00028
#define      OVERLAY_PORT1_MIX0_DST_ALPHA_CTRL    0x0002C
#define      OVERLAY_PORT1_MIX1_SRC_COLOR_CTRL    0x00030
#define      OVERLAY_PORT1_MIX1_DST_COLOR_CTRL    0x00034
#define      OVERLAY_PORT1_MIX1_SRC_ALPHA_CTRL    0x00038
#define      OVERLAY_PORT1_MIX1_DST_ALPHA_CTRL    0x0003C
#define      OVERLAY_PORT1_MIX2_SRC_COLOR_CTRL    0x00040
#define      OVERLAY_PORT1_MIX2_DST_COLOR_CTRL    0x00044
#define      OVERLAY_PORT1_MIX2_SRC_ALPHA_CTRL    0x00048
#define      OVERLAY_PORT1_MIX2_DST_ALPHA_CTRL    0x0004C
#define      OVERLAY_PORT1_BG_MIX_CTRL            0x00070
///////////////////////////////////////////
//       POST0_CTRL
///////////////////////////////////////////
#define      POST0_CTRL_BASE                      0x00000C00

#define      POST0_CTRL_POST_DSP_CTRL             0x00000
#define      POST0_CTRL_POST_MIPI_CTRL            0x00004
#define      POST0_CTRL_POST_COLOR_CTRL           0x00008
#define      POST0_CTRL_POST_CORE_CLK             0x0000C
#define      POST0_CTRL_POST_3D_LUT_CTRL          0x00010
#define      POST0_CTRL_POST_3D_LUT_R             0x00014
#define      POST0_CTRL_POST_3D_LUT_G             0x00018
#define      POST0_CTRL_POST_3D_LUT_B             0x0001C
#define      POST0_CTRL_POST_3DLUT_MST            0x00020
#define      POST0_CTRL_POST_CRC_CHECK_VALUE      0x00024
#define      POST0_CTRL_POST_CRC_OUT              0x00028
#define      POST0_CTRL_POST_DSP_BG               0x0002C
#define      POST0_CTRL_POST_PRE_SCAN_HTIMING     0x00030
#define      POST0_CTRL_POST_DSP_HACT_INFO        0x00034
#define      POST0_CTRL_POST_DSP_VACT_INFO        0x00038
#define      POST0_CTRL_POST_SCL_FACTOR_YRGB      0x0003C
#define      POST0_CTRL_POST_SCL_CTRL             0x00040
#define      POST0_CTRL_POST_DSP_VACT_INFO_F1     0x00044
#define      POST0_CTRL_POST_DSP_HTOTAL_HS_END    0x00048
#define      POST0_CTRL_POST_DSP_HACT_ST_END      0x0004C
#define      POST0_CTRL_POST_DSP_VTOTAL_VS_END    0x00050
#define      POST0_CTRL_POST_DSP_VACT_ST_END      0x00054
#define      POST0_CTRL_POST_DSP_VS_ST_END_F1     0x00058
#define      POST0_CTRL_POST_DSP_VACT_ST_END_F1   0x0005C
#define      POST0_CTRL_POST_ACM_R2Y_CTRL         0x00070
#define      POST0_CTRL_POST_ACM_R2Y_COE0102      0x00074
#define      POST0_CTRL_POST_ACM_R2Y_COE1011      0x00078
#define      POST0_CTRL_POST_ACM_R2Y_COE1220      0x0007C
#define      POST0_CTRL_POST_ACM_R2Y_COE2122      0x00080
#define      POST0_CTRL_POST_ACM_R2Y_OFFSET0      0x00084
#define      POST0_CTRL_POST_ACM_R2Y_OFFSET1      0x00088
#define      POST0_CTRL_POST_ACM_R2Y_OFFSET2      0x0008C
#define      POST0_CTRL_POST_LINE_FLAG            0x00090
#define      POST0_CTRL_POST_DITHER_FRC_0         0x000A0
#define      POST0_CTRL_POST_DITHER_FRC_1         0x000A4
#define      POST0_CTRL_POST_DITHER_FRC_2         0x000A8
#define      POST0_CTRL_POST_ACM_CTRL             0x000D0
#define      POST0_CTRL_POST_ACM_Y2R_COE0102      0x000D4
#define      POST0_CTRL_POST_ACM_Y2R_COE1011      0x000D8
#define      POST0_CTRL_POST_ACM_Y2R_COE1220      0x000DC
#define      POST0_CTRL_POST_ACM_Y2R_COE2122      0x000E0
#define      POST0_CTRL_POST_ACM_Y2R_OFFSET0      0x000E4
#define      POST0_CTRL_POST_ACM_Y2R_OFFSET1      0x000E8
#define      POST0_CTRL_POST_ACM_Y2R_OFFSET2      0x000EC
#define      POST0_CTRL_POST_STATUS               0x000F0
#define      POST0_CTRL_POST_CLK_CNT              0x000F4
#define      POST0_CTRL_POST_MCU_CTRL             0x000F8
#define      POST0_CTRL_POST_CFG_DONE             0x000FC
///////////////////////////////////////////
//       POST1_CTRL
///////////////////////////////////////////
#define      POST1_CTRL_BASE                      0x00000D00

#define      POST1_CTRL_POST_DSP_CTRL             0x00000
#define      POST1_CTRL_POST_MIPI_CTRL            0x00004
#define      POST1_CTRL_POST_COLOR_CTRL           0x00008
#define      POST1_CTRL_POST_CORE_CLK             0x0000C
#define      POST1_CTRL_POST_CRC_CHECK_VALUE      0x00024
#define      POST1_CTRL_POST_CRC_OUT              0x00028
#define      POST1_CTRL_POST_DSP_BG               0x0002C
#define      POST1_CTRL_POST_PRE_SCAN_HTIMING     0x00030
#define      POST1_CTRL_POST_DSP_HACT_INFO        0x00034
#define      POST1_CTRL_POST_DSP_VACT_INFO        0x00038
#define      POST1_CTRL_POST_SCL_FACTOR_YRGB      0x0003C
#define      POST1_CTRL_POST_SCL_CTRL             0x00040
#define      POST1_CTRL_POST_DSP_VACT_INFO_F1     0x00044
#define      POST1_CTRL_POST_DSP_HTOTAL_HS_END    0x00048
#define      POST1_CTRL_POST_DSP_HACT_ST_END      0x0004C
#define      POST1_CTRL_POST_DSP_VTOTAL_VS_END    0x00050
#define      POST1_CTRL_POST_DSP_VACT_ST_END      0x00054
#define      POST1_CTRL_POST_DSP_VS_ST_END_F1     0x00058
#define      POST1_CTRL_POST_DSP_VACT_ST_END_F1   0x0005C
#define      POST1_CTRL_POST_BCSH_CTRL            0x00060
#define      POST1_CTRL_POST_BCSH_BCS             0x00064
#define      POST1_CTRL_POST_BCSH_H               0x00068
#define      POST1_CTRL_POST_BCSH_COLOR_BAR       0x0006C
#define      POST1_CTRL_POST_BCSH_R2Y_COE00       0x00070
#define      POST1_CTRL_POST_BCSH_R2Y_COE02_01    0x00074
#define      POST1_CTRL_POST_BCSH_R2Y_COE11_10    0x00078
#define      POST1_CTRL_POST_BCSH_R2Y_COE20_12    0x0007C
#define      POST1_CTRL_POST_BCSH_R2Y_COE22_21    0x00080
#define      POST1_CTRL_POST_BCSH_R2Y_OFFSET0     0x00084
#define      POST1_CTRL_POST_BCSH_R2Y_OFFSET1     0x00088
#define      POST1_CTRL_POST_BCSH_R2Y_OFFSET2     0x0008C
#define      POST1_CTRL_POST_LINE_FLAG            0x00090
#define      POST1_CTRL_POST_DITHER_FRC_0         0x000A0
#define      POST1_CTRL_POST_DITHER_FRC_1         0x000A4
#define      POST1_CTRL_POST_DITHER_FRC_2         0x000A8
#define      POST1_CTRL_POST_BCSH_Y2R_COE00       0x000D0
#define      POST1_CTRL_POST_BCSH_Y2R_COE02_01    0x000D4
#define      POST1_CTRL_POST_BCSH_Y2R_COE11_10    0x000D8
#define      POST1_CTRL_POST_BCSH_Y2R_COE20_12    0x000DC
#define      POST1_CTRL_POST_BCSH_Y2R_COE22_21    0x000E0
#define      POST1_CTRL_POST_BCSH_Y2R_OFFSET0     0x000E4
#define      POST1_CTRL_POST_BCSH_Y2R_OFFSET1     0x000E8
#define      POST1_CTRL_POST_BCSH_Y2R_OFFSET2     0x000EC
#define      POST1_CTRL_POST_CLK_CNT              0x000F4
#define      POST1_CTRL_POST_MCU_CTRL             0x000F8
///////////////////////////////////////////
//       CLUSTER0
///////////////////////////////////////////
#define      CLUSTER0_BASE                        0x00001000

#define      CLUSTER0_WIN0_CTRL0                  0x00000
#define      CLUSTER0_WIN0_CTRL1                  0x00004
#define      CLUSTER0_WIN0_CTRL2                  0x00008
#define      CLUSTER0_WIN0_YRGB_MST               0x00010
#define      CLUSTER0_WIN0_VIR                    0x00018
#define      CLUSTER0_WIN0_ACT_INFO               0x00020
#define      CLUSTER0_WIN0_DSP_INFO               0x00024
#define      CLUSTER0_WIN0_DSP_ST                 0x00028
#define      CLUSTER0_WIN0_DSP_BG                 0x0002C
#define      CLUSTER0_WIN0_SCL_FACTOR_YRGB        0x00030
#define      CLUSTER0_WIN0_SCL_OFFSET             0x00038
#define      CLUSTER0_WIN0_TRANSFORMED_OFFSET     0x0003C
#define      CLUSTER0_WIN0_ZME_CTRL               0x00040
#define      CLUSTER0_WIN0_ZME_DERING_PARA        0x00044
#define      CLUSTER0_WIN0_FBCD_OUTPUT_CTRL       0x00050
#define      CLUSTER0_WIN0_FBCD_MODE              0x00054
#define      CLUSTER0_WIN0_FBCD_HDR_PTR           0x00058
#define      CLUSTER0_WIN0_FBCD_VIR_WIDTH         0x0005C
#define      CLUSTER0_WIN0_FBCD_SIZE              0x00060
#define      CLUSTER0_WIN0_FBCD_PIC_OFFSET        0x00064
#define      CLUSTER0_WIN0_FBCD_DIS_OFFSET        0x00068
#define      CLUSTER0_WIN0_FBCD_CTRL              0x0006C
#define      CLUSTER0_WIN0_PLD_PTR_OFFSET         0x00078
#define      CLUSTER0_WIN0_PLD_PTR_RANGE          0x0007C
#define      CLUSTER0_WIN1_CTRL0                  0x00080
#define      CLUSTER0_WIN1_CTRL1                  0x00084
#define      CLUSTER0_WIN1_CTRL2                  0x00088
#define      CLUSTER0_WIN1_YRGB_MST               0x00090
#define      CLUSTER0_WIN1_VIR                    0x00098
#define      CLUSTER0_WIN1_ACT_INFO               0x000A0
#define      CLUSTER0_WIN1_DSP_INFO               0x000A4
#define      CLUSTER0_WIN1_DSP_ST                 0x000A8
#define      CLUSTER0_WIN1_DSP_BG                 0x000AC
#define      CLUSTER0_WIN1_SCL_FACTOR_YRGB        0x000B0
#define      CLUSTER0_WIN1_SCL_OFFSET             0x000B8
#define      CLUSTER0_WIN1_TRANSFORMED_OFFSET     0x000BC
#define      CLUSTER0_WIN1_ZME_CTRL               0x000C0
#define      CLUSTER0_WIN1_ZME_DERING_PARA        0x000C4
#define      CLUSTER0_WIN1_FBCD_MASK_EN           0x000D0
#define      CLUSTER0_WIN1_FBCD_MODE              0x000D4
#define      CLUSTER0_WIN1_FBCD_HDR_PTR           0x000D8
#define      CLUSTER0_WIN1_FBCD_VIR_WIDTH         0x000DC
#define      CLUSTER0_WIN1_FBCD_SIZE              0x000E0
#define      CLUSTER0_WIN1_FBCD_PIC_OFFSET        0x000E4
#define      CLUSTER0_WIN1_FBCD_DIS_OFFSET        0x000E8
#define      CLUSTER0_WIN1_FBCD_CTRL              0x000EC
#define      CLUSTER0_WIN1_PLD_PTR_OFFSET         0x000F8
#define      CLUSTER0_WIN1_PLD_PTR_RANGE          0x000FC
#define      CLUSTER0_CLUSTER_CTRL                0x00100
#define      CLUSTER0_DCI_BLK_SIZE                0x00104
#define      CLUSTER0_DCI_BLK_OFFSET              0x00108
#define      CLUSTER0_DCI_PIX_REGION              0x0010C
#define      CLUSTER0_DCI_LUMA_SAT_ADJ_0          0x00110
#define      CLUSTER0_DCI_LUMA_SAT_ADJ_1          0x00114
#define      CLUSTER0_DCI_CTRL                    0x00118
#define      CLUSTER0_DCI_LUT_MST                 0x0011C
#define      CLUSTER0_DCI_DBG_CTRL                0x00120
#define      CLUSTER0_DCI_DBG_PIX                 0x00130
#define      CLUSTER0_DCI_CSC_COE01_00            0x00140
#define      CLUSTER0_DCI_CSC_COE10_02            0x00144
#define      CLUSTER0_DCI_CSC_COE12_11            0x00148
#define      CLUSTER0_DCI_CSC_COE21_20            0x0014C
#define      CLUSTER0_DCI_CSC_COE22               0x00150
#define      CLUSTER0_DCI_CSC_OFFSET0             0x00154
#define      CLUSTER0_DCI_CSC_OFFSET1             0x00158
#define      CLUSTER0_DCI_CSC_OFFSET2             0x0015C
#define      CLUSTER0_WIN0_CSC_COE01_00           0x00180
#define      CLUSTER0_WIN0_CSC_COE10_02           0x00184
#define      CLUSTER0_WIN0_CSC_COE12_11           0x00188
#define      CLUSTER0_WIN0_CSC_COE21_20           0x0018C
#define      CLUSTER0_WIN0_CSC_COE22              0x00190
#define      CLUSTER0_WIN0_CSC_OFFSET0            0x00194
#define      CLUSTER0_WIN0_CSC_OFFSET1            0x00198
#define      CLUSTER0_WIN0_CSC_OFFSET2            0x0019C
#define      CLUSTER0_WIN1_CSC_COE01_00           0x001A0
#define      CLUSTER0_WIN1_CSC_COE10_02           0x001A4
#define      CLUSTER0_WIN1_CSC_COE12_11           0x001A8
#define      CLUSTER0_WIN1_CSC_COE21_20           0x001AC
#define      CLUSTER0_WIN1_CSC_COE22              0x001B0
#define      CLUSTER0_WIN1_CSC_OFFSET0            0x001B4
#define      CLUSTER0_WIN1_CSC_OFFSET1            0x001B8
#define      CLUSTER0_WIN1_CSC_OFFSET2            0x001BC
#define      CLUSTER0_CLUSTER_SRC_COLOR_CTRL      0x000E0
#define      CLUSTER0_CLUSTER_DST_COLOR_CTRL      0x000E4
#define      CLUSTER0_CLUSTER_SRC_ALPHA_CTRL      0x000E8
#define      CLUSTER0_CLUSTER_DST_ALPHA_CTRL      0x000EC
#define      CLUSTER0_CLUSTER_PORT_SEL_IMD        0x001F4
#define      CLUSTER0_CLUSTER_DLY_NUM             0x001F8
#define      CLUSTER0_CLUSTER_CFG_DONE            0x001FC
///////////////////////////////////////////
//       CLUSTER1
///////////////////////////////////////////
#define      CLUSTER1_BASE                        0x00001200

#define      CLUSTER1_WIN0_CTRL0                  0x00000
#define      CLUSTER1_WIN0_CTRL1                  0x00004
#define      CLUSTER1_WIN0_CTRL2                  0x00008
#define      CLUSTER1_WIN0_YRGB_MST               0x00010
#define      CLUSTER1_WIN0_VIR                    0x00018
#define      CLUSTER1_WIN0_ACT_INFO               0x00020
#define      CLUSTER1_WIN0_DSP_INFO               0x00024
#define      CLUSTER1_WIN0_DSP_ST                 0x00028
#define      CLUSTER1_WIN0_DSP_BG                 0x0002C
#define      CLUSTER1_WIN0_SCL_FACTOR_YRGB        0x00030
#define      CLUSTER1_WIN0_SCL_OFFSET             0x00038
#define      CLUSTER1_WIN0_TRANSFORMED_OFFSET     0x0003C
#define      CLUSTER1_WIN0_ZME_CTRL               0x00040
#define      CLUSTER1_WIN0_ZME_DERING_PARA        0x00044
#define      CLUSTER1_WIN0_FBCD_OUTPUT_CTRL       0x00050
#define      CLUSTER1_WIN0_FBCD_MODE              0x00054
#define      CLUSTER1_WIN0_FBCD_HDR_PTR           0x00058
#define      CLUSTER1_WIN0_FBCD_VIR_WIDTH         0x0005C
#define      CLUSTER1_WIN0_FBCD_SIZE              0x00060
#define      CLUSTER1_WIN0_FBCD_PIC_OFFSET        0x00064
#define      CLUSTER1_WIN0_FBCD_DIS_OFFSET        0x00068
#define      CLUSTER1_WIN0_FBCD_CTRL              0x0006C
#define      CLUSTER1_WIN0_PLD_PTR_OFFSET         0x00078
#define      CLUSTER1_WIN0_PLD_PTR_RANGE          0x0007C
#define      CLUSTER1_WIN1_CTRL0                  0x00080
#define      CLUSTER1_WIN1_CTRL1                  0x00084
#define      CLUSTER1_WIN1_CTRL2                  0x00088
#define      CLUSTER1_WIN1_YRGB_MST               0x00090
#define      CLUSTER1_WIN1_VIR                    0x00098
#define      CLUSTER1_WIN1_ACT_INFO               0x000A0
#define      CLUSTER1_WIN1_DSP_INFO               0x000A4
#define      CLUSTER1_WIN1_DSP_ST                 0x000A8
#define      CLUSTER1_WIN1_DSP_BG                 0x000AC
#define      CLUSTER1_WIN1_SCL_FACTOR_YRGB        0x000B0
#define      CLUSTER1_WIN1_SCL_OFFSET             0x000B8
#define      CLUSTER1_WIN1_TRANSFORMED_OFFSET     0x000BC
#define      CLUSTER1_WIN1_ZME_CTRL               0x000C0
#define      CLUSTER1_WIN1_ZME_DERING_PARA        0x000C4
#define      CLUSTER1_WIN1_FBCD_MASK_EN           0x000D0
#define      CLUSTER1_WIN1_FBCD_MODE              0x000D4
#define      CLUSTER1_WIN1_FBCD_HDR_PTR           0x000D8
#define      CLUSTER1_WIN1_FBCD_VIR_WIDTH         0x000DC
#define      CLUSTER1_WIN1_FBCD_SIZE              0x000E0
#define      CLUSTER1_WIN1_FBCD_PIC_OFFSET        0x000E4
#define      CLUSTER1_WIN1_FBCD_DIS_OFFSET        0x000E8
#define      CLUSTER1_WIN1_FBCD_CTRL              0x000EC
#define      CLUSTER1_WIN1_PLD_PTR_OFFSET         0x000F8
#define      CLUSTER1_WIN1_PLD_PTR_RANGE          0x000FC
#define      CLUSTER1_CLUSTER_CTRL                0x00100
#define      CLUSTER1_WIN0_CSC_COE01_00           0x00180
#define      CLUSTER1_WIN0_CSC_COE10_02           0x00184
#define      CLUSTER1_WIN0_CSC_COE12_11           0x00188
#define      CLUSTER1_WIN0_CSC_COE21_20           0x0018C
#define      CLUSTER1_WIN0_CSC_COE22              0x00190
#define      CLUSTER1_WIN0_CSC_OFFSET0            0x00194
#define      CLUSTER1_WIN0_CSC_OFFSET1            0x00198
#define      CLUSTER1_WIN0_CSC_OFFSET2            0x0019C
#define      CLUSTER1_WIN1_CSC_COE01_00           0x001A0
#define      CLUSTER1_WIN1_CSC_COE10_02           0x001A4
#define      CLUSTER1_WIN1_CSC_COE12_11           0x001A8
#define      CLUSTER1_WIN1_CSC_COE21_20           0x001AC
#define      CLUSTER1_WIN1_CSC_COE22              0x001B0
#define      CLUSTER1_WIN1_CSC_OFFSET0            0x001B4
#define      CLUSTER1_WIN1_CSC_OFFSET1            0x001B8
#define      CLUSTER1_WIN1_CSC_OFFSET2            0x001BC
#define      CLUSTER1_CLUSTER_SRC_COLOR_CTRL      0x000E0
#define      CLUSTER1_CLUSTER_DST_COLOR_CTRL      0x000E4
#define      CLUSTER1_CLUSTER_SRC_ALPHA_CTRL      0x000E8
#define      CLUSTER1_CLUSTER_DST_ALPHA_CTRL      0x000EC
#define      CLUSTER1_CLUSTER_PORT_SEL_IMD        0x001F4
#define      CLUSTER1_CLUSTER_DLY_NUM             0x001F8
#define      CLUSTER1_CLUSTER_CFG_DONE            0x001FC
///////////////////////////////////////////
//       MSMART0
///////////////////////////////////////////
#define      MSMART0_BASE                         0x00001800

#define      MSMART0_WIN_CTRL0                    0x00000
#define      MSMART0_WIN_AXI_CTRL                 0x00004
#define      MSMART0_WIN_ALHPE_VP                 0x00008
#define      MSMART0_WIN_REGION_MST               0x0000C
#define      MSMART0_WIN_SCL_CTRL                 0x00010
#define      MSMART0_WIN_SCL_FACTOR_YRGB          0x00014
#define      MSMART0_WIN_CRC_CHKOU_STATUS         0x00018
#define      MSMART0_WIN_ACT_PRE_INFO             0x0001C
#define      MSMART0_WIN_DSP_INFO                 0x00020
#define      MSMART0_WIN_DSP_ST                   0x00024
#define      MSMART0_WIN_DSP_BG                   0x00028
#define      MSMART0_WIN_COLOR_KEY                0x0002C
#define      MSMART0_WIN_CSC_COE_0                0x00030
#define      MSMART0_WIN_CSC_COE_1                0x00034
#define      MSMART0_WIN_CSC_COE_2                0x00038
#define      MSMART0_WIN_CSC_COE_3                0x0003C
#define      MSMART0_WIN_CSC_COE_4                0x00040
#define      MSMART0_WIN_CSC_OFFSET0              0x00044
#define      MSMART0_WIN_CSC_OFFSET1              0x00048
#define      MSMART0_WIN_CSC_OFFSET2              0x0004C
#define      MSMART0_WIN_REGION0_YRGB_MST         0x00050
#define      MSMART0_WIN_REGION0_CBCR_MST         0x00054
#define      MSMART0_WIN_REGION0_VIR              0x00058
#define      MSMART0_WIN_REGION0_ACT_INFO         0x0005C
#define      MSMART0_WIN_REGION0_ACT_OFFSET       0x00060
#define      MSMART0_WIN_REGION0_DSP_OFFSET       0x00064
#define      MSMART0_WIN_CFG_DONE                 0x001FC
///////////////////////////////////////////
//       MSMART1
///////////////////////////////////////////
#define      MSMART1_BASE                         0x00001A00

#define      MSMART1_WIN_CTRL0                    0x00000
#define      MSMART1_WIN_AXI_CTRL                 0x00004
#define      MSMART1_WIN_ALHPE_VP                 0x00008
#define      MSMART1_WIN_REGION_MST               0x0000C
#define      MSMART1_WIN_SCL_CTRL                 0x00010
#define      MSMART1_WIN_SCL_FACTOR_YRGB          0x00014
#define      MSMART1_WIN_CRC_CHKOU_STATUS         0x00018
#define      MSMART1_WIN_ACT_PRE_INFO             0x0001C
#define      MSMART1_WIN_DSP_INFO                 0x00020
#define      MSMART1_WIN_DSP_ST                   0x00024
#define      MSMART1_WIN_DSP_BG                   0x00028
#define      MSMART1_WIN_COLOR_KEY                0x0002C
#define      MSMART1_WIN_CSC_COE_0                0x00030
#define      MSMART1_WIN_CSC_COE_1                0x00034
#define      MSMART1_WIN_CSC_COE_2                0x00038
#define      MSMART1_WIN_CSC_COE_3                0x0003C
#define      MSMART1_WIN_CSC_COE_4                0x00040
#define      MSMART1_WIN_CSC_OFFSET0              0x00044
#define      MSMART1_WIN_CSC_OFFSET1              0x00048
#define      MSMART1_WIN_CSC_OFFSET2              0x0004C
#define      MSMART1_WIN_REGION0_YRGB_MST         0x00050
#define      MSMART1_WIN_REGION0_CBCR_MST         0x00054
#define      MSMART1_WIN_REGION0_VIR              0x00058
#define      MSMART1_WIN_REGION0_ACT_INFO         0x0005C
#define      MSMART1_WIN_REGION0_ACT_OFFSET       0x00060
#define      MSMART1_WIN_REGION0_DSP_OFFSET       0x00064
#define      MSMART1_WIN_CFG_DONE                 0x001FC
///////////////////////////////////////////
//       ESMART0
///////////////////////////////////////////
#define      ESMART0_BASE                         0x00001C00

#define      ESMART0_ESMART_CTRL0                 0x00000
#define      ESMART0_ESMART_CTRL1                 0x00004
#define      ESMART0_ESMART_AXI_CTRL_IMD          0x00008
#define      ESMART0_REGION0_MST_CTL              0x00010
#define      ESMART0_REGION0_MST_YRGB             0x00014
#define      ESMART0_REGION0_MST_CBCR             0x00018
#define      ESMART0_REGION0_VIR                  0x0001C
#define      ESMART0_REGION0_ACT_INFO             0x00020
#define      ESMART0_REGION0_DSP_INFO             0x00024
#define      ESMART0_REGION0_DSP_OFFSET           0x00028
#define      ESMART0_REGION0_SCL_CTRL             0x00030
#define      ESMART0_REGION0_SCL_FACTOR_YRGB      0x00034
#define      ESMART0_REGION0_SCL_OFFSET           0x0003C
#define      ESMART0_REGION1_MST_CTL              0x00040
#define      ESMART0_REGION1_MST_YRGB             0x00044
#define      ESMART0_REGION1_MST_CBCR             0x00048
#define      ESMART0_REGION1_VIR                  0x0004C
#define      ESMART0_REGION1_ACT_INFO             0x00050
#define      ESMART0_REGION1_DSP_INFO             0x00054
#define      ESMART0_REGION1_DSP_OFFSET           0x00058
#define      ESMART0_REGION1_SCL_CTRL             0x00060
#define      ESMART0_REGION1_SCL_FACTOR_YRGB      0x00064
#define      ESMART0_REGION1_SCL_OFFSET           0x0006C
#define      ESMART0_REGION2_MST_CTL              0x00070
#define      ESMART0_REGION2_MST_YRGB             0x00074
#define      ESMART0_REGION2_MST_CBCR             0x00078
#define      ESMART0_REGION2_VIR                  0x0007C
#define      ESMART0_REGION2_ACT_INFO             0x00080
#define      ESMART0_REGION2_DSP_INFO             0x00084
#define      ESMART0_REGION2_DSP_OFFSET           0x00088
#define      ESMART0_REGION2_SCL_CTRL             0x00090
#define      ESMART0_REGION2_SCL_FACTOR_YRGB      0x00094
#define      ESMART0_REGION2_SCL_OFFSET           0x0009C
#define      ESMART0_REGION3_MST_CTL              0x000A0
#define      ESMART0_REGION3_MST_YRGB             0x000A4
#define      ESMART0_REGION3_MST_CBCR             0x000A8
#define      ESMART0_REGION3_VIR                  0x000AC
#define      ESMART0_REGION3_ACT_INFO             0x000B0
#define      ESMART0_REGION3_DSP_INFO             0x000B4
#define      ESMART0_REGION3_DSP_OFFSET           0x000B8
#define      ESMART0_REGION3_SCL_CTRL             0x000C0
#define      ESMART0_REGION3_SCL_FACTOR_YRGB      0x000C4
#define      ESMART0_REGION3_SCL_OFFSET           0x000CC
#define      ESMART0_ESMART_KEY_CTRL              0x000D0
#define      ESMART0_ESMART_BG_EN                 0x000D4
#define      ESMART0_ESMART_ALPHA_MAP             0x000D8
#define      ESMART0_ESMART_PORT_SEL_IMD          0x000F4
#define      ESMART0_ESMART_DLY_NUM               0x000F8
#define      ESMART0_ESMART_CSC_COE01_00          0x00100
#define      ESMART0_ESMART_CSC_COE10_02          0x00104
#define      ESMART0_ESMART_CSC_COE12_11          0x00108
#define      ESMART0_ESMART_CSC_COE21_20          0x0010C
#define      ESMART0_ESMART_CSC_COE22             0x00110
#define      ESMART0_ESMART_CSC_OFFSET0           0x00114
#define      ESMART0_ESMART_CSC_OFFSET1           0x00118
#define      ESMART0_ESMART_CSC_OFFSET2           0x0011C
#define      ESMART0_EMSART_CFG_DONE              0x001FC
///////////////////////////////////////////
//       ESMART1
///////////////////////////////////////////
#define      ESMART1_BASE                         0x00001E00

#define      ESMART1_ESMART_CTRL0                 0x00000
#define      ESMART1_ESMART_CTRL1                 0x00004
#define      ESMART1_ESMART_AXI_CTRL_IMD          0x00008
#define      ESMART1_REGION0_MST_CTL              0x00010
#define      ESMART1_REGION0_MST_YRGB             0x00014
#define      ESMART1_REGION0_MST_CBCR             0x00018
#define      ESMART1_REGION0_VIR                  0x0001C
#define      ESMART1_REGION0_ACT_INFO             0x00020
#define      ESMART1_REGION0_DSP_INFO             0x00024
#define      ESMART1_REGION0_DSP_OFFSET           0x00028
#define      ESMART1_REGION0_SCL_CTRL             0x00030
#define      ESMART1_REGION0_SCL_FACTOR_YRGB      0x00034
#define      ESMART1_REGION0_SCL_OFFSET           0x0003C
#define      ESMART1_REGION1_MST_CTL              0x00040
#define      ESMART1_REGION1_MST_YRGB             0x00044
#define      ESMART1_REGION1_MST_CBCR             0x00048
#define      ESMART1_REGION1_VIR                  0x0004C
#define      ESMART1_REGION1_ACT_INFO             0x00050
#define      ESMART1_REGION1_DSP_INFO             0x00054
#define      ESMART1_REGION1_DSP_OFFSET           0x00058
#define      ESMART1_REGION1_SCL_CTRL             0x00060
#define      ESMART1_REGION1_SCL_FACTOR_YRGB      0x00064
#define      ESMART1_REGION1_SCL_OFFSET           0x0006C
#define      ESMART1_REGION2_MST_CTL              0x00070
#define      ESMART1_REGION2_MST_YRGB             0x00074
#define      ESMART1_REGION2_MST_CBCR             0x00078
#define      ESMART1_REGION2_VIR                  0x0007C
#define      ESMART1_REGION2_ACT_INFO             0x00080
#define      ESMART1_REGION2_DSP_INFO             0x00084
#define      ESMART1_REGION2_DSP_OFFSET           0x00088
#define      ESMART1_REGION2_SCL_CTRL             0x00090
#define      ESMART1_REGION2_SCL_FACTOR_YRGB      0x00094
#define      ESMART1_REGION2_SCL_OFFSET           0x0009C
#define      ESMART1_REGION3_MST_CTL              0x000A0
#define      ESMART1_REGION3_MST_YRGB             0x000A4
#define      ESMART1_REGION3_MST_CBCR             0x000A8
#define      ESMART1_REGION3_VIR                  0x000AC
#define      ESMART1_REGION3_ACT_INFO             0x000B0
#define      ESMART1_REGION3_DSP_INFO             0x000B4
#define      ESMART1_REGION3_DSP_OFFSET           0x000B8
#define      ESMART1_REGION3_SCL_CTRL             0x000C0
#define      ESMART1_REGION3_SCL_FACTOR_YRGB      0x000C4
#define      ESMART1_REGION3_SCL_OFFSET           0x000CC
#define      ESMART1_ESMART_KEY_CTRL              0x000D0
#define      ESMART1_ESMART_BG_EN                 0x000D4
#define      ESMART1_ESMART_ALPHA_MAP             0x000D8
#define      ESMART1_ESMART_PORT_SEL_IMD          0x000F4
#define      ESMART1_ESMART_DLY_NUM               0x000F8
#define      ESMART1_ESMART_CSC_COE01_00          0x00100
#define      ESMART1_ESMART_CSC_COE10_02          0x00104
#define      ESMART1_ESMART_CSC_COE12_11          0x00108
#define      ESMART1_ESMART_CSC_COE21_20          0x0010C
#define      ESMART1_ESMART_CSC_COE22             0x00110
#define      ESMART1_ESMART_CSC_OFFSET0           0x00114
#define      ESMART1_ESMART_CSC_OFFSET1           0x00118
#define      ESMART1_ESMART_CSC_OFFSET2           0x0011C
#define      ESMART1_ESMART_CFG_DONE              0x001FC
///////////////////////////////////////////
//       HDR_VIVID
///////////////////////////////////////////
#define      HDR_VIVID_BASE                       0x00002000

#define      HDR_VIVID_HDR_LUT_CTRL               0x00000
#define      HDR_VIVID_HDR_LUT_MST                0x00004
#define      HDR_VIVID_HDR_LUT_STATUS             0x00008
#define      HDR_VIVID_SDR2HDR_CTRL               0x00010
#define      HDR_VIVID_SDR_CFG_COE0               0x00014
#define      HDR_VIVID_SDR_CFG_COE1               0x00018
#define      HDR_VIVID_SDR_CSC_COE00_01           0x0001C
#define      HDR_VIVID_SDR_CSC_COE02_10           0x00020
#define      HDR_VIVID_SDR_CSC_COE11_12           0x00024
#define      HDR_VIVID_SDR_CSC_COE20_21           0x00028
#define      HDR_VIVID_SDR_CSC_COE22              0x0002C
#define      HDR_VIVID_HDRVIVID_CTRL              0x00040
#define      HDR_VIVID_HDR_PQ_GAMMA               0x00044
#define      HDR_VIVID_HLG_RFIX_SCALEFAC          0x00048
#define      HDR_VIVID_HLG_MAXLUMA                0x0004C
#define      HDR_VIVID_HLG_R_TM_LIN2NON           0x00050
#define      HDR_VIVID_HDR_CSC_COE00_01           0x00054
#define      HDR_VIVID_HDR_CSC_COE02_10           0x00058
#define      HDR_VIVID_HDR_CSC_COE11_12           0x0005C
#define      HDR_VIVID_HDR_CSC_COE20_21           0x00060
#define      HDR_VIVID_HDR_CSC_COE22              0x00064
#define      HDR_VIVID_HDR_DEBUG_CTRL             0x00080
#define      HDR_VIVID_DEBUG_POINT0_CFG           0x00084
#define      HDR_VIVID_DEBUG_POINT1_CFG           0x00088
#define      HDR_VIVID_DEBUG_POINT0_R0            0x0008C
#define      HDR_VIVID_DEBUG_POINT0_G0            0x00090
#define      HDR_VIVID_DEBUG_POINT0_B0            0x00094
#define      HDR_VIVID_DEBUG_POINT0_R1            0x00098
#define      HDR_VIVID_DEBUG_POINT0_G1            0x0009C
#define      HDR_VIVID_DEBUG_POINT0_B1            0x000A0
#define      HDR_VIVID_DEBUG_POINT1_R0            0x000A4
#define      HDR_VIVID_DEBUG_POINT1_G0            0x000A8
#define      HDR_VIVID_DEBUG_POINT1_B0            0x000AC
#define      HDR_VIVID_DEBUG_POINT1_R1            0x000B0
#define      HDR_VIVID_DEBUG_POINT1_G1            0x000B4
#define      HDR_VIVID_DEBUG_POINT1_B1            0x000B8
#define      HDR_VIVID_HDR_TONE_SCA               0x0013C
#define      HDR_VIVID_HDRGAMMA_CURVE             0x00540
#define      HDR_VIVID_HDRGAMMA_MDFVALUE          0x00690
#define      HDR_VIVID_SDRINVGAMMA_CURVE          0x00700
#define      HDR_VIVID_SDRINVGAMMA_STARTIDX       0x00820
#define      HDR_VIVID_SDRINVGAMMA_CHANGEIDX      0x00840
#define      HDR_VIVID_SDR_SMGAIN                 0x00900
///////////////////////////////////////////
//       HWC0
///////////////////////////////////////////
#define      HWC0_BASE                            0x00003800

#define      HWC0_HWC_CTRL0                       0x000
#define      HWC0_HWC_CTRL1                       0x004
#define      HWC0_HWC_AXI_CTRL_IMD                0x008
#define      HWC0_HWC_MST_CTL                     0x00C
#define      HWC0_HWC_MST                         0x010
#define      HWC0_HWC_VIR                         0x014
#define      HWC0_HWC_SIZE_INFO                   0x018
#define      HWC0_HWC_DSP_OFFSET                  0x01C
#define      HWC0_HWC_KEY_CTRL                    0x020
#define      HWC0_HWC_BG_EN                       0x024
#define      HWC0_HWC_PORT_SEL_IMD                0x028
#define      HWC0_HWC_DLY_NUM                     0x02C
#define      HWC0_HWC_CSC_COE00_01                0x030
#define      HWC0_HWC_CSC_COE02_10                0x034
#define      HWC0_HWC_CSC_COE11_12                0x038
#define      HWC0_HWC_CSC_COE20_21                0x03C
#define      HWC0_HWC_CSC_COE22                   0x040
#define      HWC0_HWC_CSC_OFFSET0                 0x044
#define      HWC0_HWC_CSC_OFFSET1                 0x048
#define      HWC0_HWC_CSC_OFFSET2                 0x04C
///////////////////////////////////////////
//       HWC1
///////////////////////////////////////////
#define      HWC1_BASE                            0x00003900

#define      HWC1_HWC_CTRL0                       0x000
#define      HWC1_HWC_CTRL1                       0x004
#define      HWC1_HWC_AXI_CTRL_IMD                0x008
#define      HWC1_HWC_MST_CTL                     0x00C
#define      HWC1_HWC_MST                         0x010
#define      HWC1_HWC_VIR                         0x014
#define      HWC1_HWC_SIZE_INFO                   0x018
#define      HWC1_HWC_DSP_OFFSET                  0x01C
#define      HWC1_HWC_KEY_CTRL                    0x020
#define      HWC1_HWC_BG_EN                       0x024
#define      HWC1_HWC_PORT_SEL_IMD                0x028
#define      HWC1_HWC_DLY_NUM                     0x02C
#define      HWC1_HWC_CSC_COE00_01                0x030
#define      HWC1_HWC_CSC_COE02_10                0x034
#define      HWC1_HWC_CSC_COE11_12                0x038
#define      HWC1_HWC_CSC_COE20_21                0x03C
#define      HWC1_HWC_CSC_COE22                   0x040
#define      HWC1_HWC_CSC_OFFSET0                 0x044
#define      HWC1_HWC_CSC_OFFSET1                 0x048
#define      HWC1_HWC_CSC_OFFSET2                 0x04C
///////////////////////////////////////////
//       GAMMA_LUT_WRADDR
///////////////////////////////////////////
#define      GAMMA_LUT_WRADDR_BASE                0x00005000

///////////////////////////////////////////
//       BPP_LUT_WRADDR
///////////////////////////////////////////
#define      BPP_LUT_WRADDR_BASE                  0x00006000

///////////////////////////////////////////
//       ACM
///////////////////////////////////////////
#define      ACM_BASE                             0x00006400

#define      ACM_ACM_CTRL                         0x00000
#define      ACM_DELTA_RANGE                      0x00004
#define      ACM_FETCH_START                      0x00008
#define      ACM_DEBUG_POINT0_CFG                 0x00010
#define      ACM_DEBUG_POINT1_CFG                 0x00014
#define      ACM_DEBUG_POINT2_CFG                 0x00018
#define      ACM_DEBUG_POINT3_CFG                 0x0001C
#define      ACM_FETCH_DONE                       0x00020
#define      ACM_DEBUG0_DATA0                     0x00030
#define      ACM_DEBUG0_DATA1                     0x00034
#define      ACM_DEBUG0_DATA2                     0x00038
#define      ACM_DEBUG0_DATA3                     0x0003C
#define      ACM_DEBUG1_DATA0                     0x00040
#define      ACM_DEBUG1_DATA1                     0x00044
#define      ACM_DEBUG1_DATA2                     0x00048
#define      ACM_DEBUG1_DATA3                     0x0004C
#define      ACM_DEBUG2_DATA0                     0x00050
#define      ACM_DEBUG2_DATA1                     0x00054
#define      ACM_DEBUG2_DATA2                     0x00058
#define      ACM_DEBUG2_DATA3                     0x0005C
#define      ACM_DEBUG3_DATA0                     0x00060
#define      ACM_DEBUG3_DATA1                     0x00064
#define      ACM_DEBUG3_DATA2                     0x00068
#define      ACM_DEBUG3_DATA3                     0x0006C
#define      ACM_YHS_GAIN_BY_Y_SEG0               0x00100
#define      ACM_YHS_GAIN_BY_Y_SEG152             0x00360
#define      ACM_YHS_GAIN_BY_S_SEG0               0x00364
#define      ACM_YHS_GAIN_BY_S_SEG220             0x006D4
#define      ACM_YHS_DEL_BY_H_SEG0                0x006D8
#define      ACM_YHS_DEL_BY_H_SEG64               0x007D8
///////////////////////////////////////////
//       SHARP
///////////////////////////////////////////
#define      SHARP_BASE                           0x00006C00

#define      SHARP_ENABLE_CTRL                    0x00000
#define      SHARP_GATING_CTRL                    0x00004
#define      SHARP_USM_CTRL                       0x00010
#define      SHARP_USM_COEF                       0x00014
#define      SHARP_SHOOT_CTRL_REG0                0x00020
#define      SHARP_SHOOT_CTRL_REG1                0x00024
#define      SHARP_SHOOT_CTRL_REG2                0x00028
#define      SHARP_ROI_CTRL0                      0x0002C
#define      SHARP_ROI_CTRL1                      0x00030
///////////////////////////////////////////
//       MMU0
///////////////////////////////////////////
#define      MMU0_BASE                            0x00007E00

#define      MMU0_MMU_DTE_ADDR                    0x00000
#define      MMU0_MMU_STATUS                      0x00004
#define      MMU0_MMU_COMMAND                     0x00008
#define      MMU0_MMU_PAGE_FAULT_ADDR             0x0000C
#define      MMU0_MMU_ZAP_ONE_LINE                0x00010
#define      MMU0_MMU_INT_RAWSTAT                 0x00014
#define      MMU0_MMU_INT_CLEAR                   0x00018
#define      MMU0_MMU_INT_MASK                    0x0001C
#define      MMU0_MMU_INT_STATUS                  0x00020
#define      MMU0_MMU_AUTO_GATING                 0x00024
///////////////////////////////////////////
//       MMU1
///////////////////////////////////////////
#define      MMU1_BASE                            0x00007F00

#define      MMU1_MMU_DTE_ADDR                    0x00000
#define      MMU1_MMU_STATUS                      0x00004
#define      MMU1_MMU_COMMAND                     0x00008
#define      MMU1_MMU_PAGE_FAULT_ADDR             0x0000C
#define      MMU1_MMU_ZAP_ONE_LINE                0x00010
#define      MMU1_MMU_INT_RAWSTAT                 0x00014
#define      MMU1_MMU_INT_CLEAR                   0x00018
#define      MMU1_MMU_INT_MASK                    0x0001C
#define      MMU1_MMU_INT_STATUS                  0x00020
#define      MMU1_MMU_AUTO_GATING                 0x00024
#endif /* __CHIP_REGISTER_H */