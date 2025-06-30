/*
 * vop3_reg.h
 *
 *  Created on: 2021-11-19
 *      Author: rihui.bao@rock-chips.com
 */

#include "./vop3_define.h"
#ifdef  VOP3_ROBIN

#ifdef HDMITX_TEST
	#define	VOP_BASE	0xf9010000
#else
	#define	VOP_BASE	0xf9000000
#endif
#define     VOPLITE_BASE    VOP_BASE

#define      VOP3_SYS_CTRL_BASE                        0x00000000
#define      VOP3_SYS0_CTRL_BASE                       0x00000100
#define      VOP3_SYS1_CTRL_BASE                       0x00000200
#define      VOP3_INFACE_CTRL_BASE                     0x00000300
#define      VOP3_WB_CTRL_BASE                         0x00000400
#define      VOP3_SECURE_CTRL_BASE                     0x00000500
#define      VOP3_OVERLAY_PORT0_BASE                   0x00000600
#define      VOP3_OVERLAY_PORT1_BASE                   0x00000700
#define      VOP3_POST0_CTRL_BASE                      0x00000C00
#define      VOP3_POST1_CTRL_BASE                      0x00000D00
#define      VOP3_CLUSTER0_BASE                        0x00001000
#define      VOP3_CLUSTER1_BASE                        0x00001200
#define      VOP3_ESMART0_BASE                         0x00001800
#define      VOP3_ESMART1_BASE                         0x00001A00
#define      VOP3_MSMART0_BASE                         0x00001C00
#define      VOP3_MSMART1_BASE                         0x00001E00
#define      VOP3_HDR_VIVID_BASE                       0x00002000
#define      VOP3_HWC0_BASE                            0x00003800
#define      VOP3_HWC1_BASE                            0x00003900
#define      GAMMA_LUT_WRADDR_BASE                     0x00005000
#define      VOP3_ACM_BASE                             0x00006400
#define      VOP3_SHARP_BASE                           0x00006C00
#define      MMU0_BASE                                 0x00007E00
#define      MMU1_BASE                                 0x00007F00


#define CLUSTER0_0_YRGB_RID                 2
#define CLUSTER0_0_CBCR_RID                 3
#define CLUSTER0_1_YRGB_RID                 4
#define CLUSTER0_1_CBCR_RID                 5

#define CLUSTER1_0_YRGB_RID                 6
#define CLUSTER1_0_CBCR_RID                 7
#define CLUSTER1_1_YRGB_RID                 8
#define CLUSTER1_1_CBCR_RID                 9
#define CLUSTER2_0_YRGB_RID                 2
#define CLUSTER2_0_CBCR_RID                 3
#define CLUSTER2_1_YRGB_RID                 4
#define CLUSTER2_1_CBCR_RID                 5
#define CLUSTER3_0_YRGB_RID                 2
#define CLUSTER3_0_CBCR_RID                 3
#define CLUSTER3_1_YRGB_RID                 4
#define CLUSTER3_1_CBCR_RID                 5


#define HWC0_YRGB_RID                       12
#define HWC1_YRGB_RID                       13

#define NVR0_YRGB_RID                       17
#define NVR0_CBCR_RID                       19


#define NVR1_YRGB_RID                       20
#define NVR1_CBCR_RID                       22



//#define ESMART0_YRGB_RID                    10 //2
//#define ESMART0_CBCR_RID                    11 //3
//#define SMART0_YRGB_RID                     12 //6
//#define SMART0_CBCR_RID                     13 //7
//#define ESMART1_YRGB_RID                    10 //4
//#define ESMART1_CBCR_RID                    11 //5
//#define SMART1_YRGB_RID                     12 //8
//#define SMART1_CBCR_RID                     13 //9


#define ESMART0_YRGB_RID                    0x15 //2
#define ESMART0_CBCR_RID                    0x16 //3
#define SMART0_YRGB_RID                     0x12 //6
#define SMART0_CBCR_RID                     0x13 //7
#define ESMART1_YRGB_RID                    0x10 //4
#define ESMART1_CBCR_RID                    0x11 //5
#define SMART1_YRGB_RID                     0x12 //8
#define SMART1_CBCR_RID                     0x13 //9




#define VOP_MCU     						   0x00F8
#define VOP_MCU_RW_BYPASS_PORT                 0x00FC
//define RGA PIC DATA

#define RGA_TILE422_720X480_0 			0x1106000
#define RGA_TILE422_720X480_1 			0x1206000
#define RGA_TILE422_720X480_2 			0x1306000
#define RGA_TILE422_720X480_3 			0x1406000
#define RGA_TILE420_720X480_0 			0x1506000
#define RGA_TILE420_720X480_1 			0x1606000
#define RGA_TILE420_720X480_2 			0x1706000
#define RGA_TILE420_720X480_3 			0x1806000

#define RGA_RASTER_800X480_ARGB8888		0x11006000
#define RGA_RASTER_800X480_RGB888		0x11206000
#define RGA_RASTER_800X480_RGBA5551		0x11406000
#define RGA_RASTER_800X480_RGB565		0x11606000

#define RGA_RASTER_800X480_YUYV422		0x11806000
#define RGA_RASTER_800X480_VYUY422		0x11a06000

#define RGA_RASTER_800X480_Y444			0x11c06000
#define RGA_RASTER_800X480_UV444		0x11e06000
#define RGA_RASTER_800X480_UV422		0x12006000
#define RGA_RASTER_800X480_UV420		0x12206000

//define VIDEO PIC DATA
//line
#define VIDEO_YUV444_720x480 			0x00600000 //0x0060 0000 ~ 0x006f ffff
#define VIDEO_YUV422_720x480 			0x00700000 //0x0070 0000 ~ 0x007f ffff
#define VIDEO_YUV420_720x480 			0x00800000 //0x0080 0000 ~ 0x008f ffff
#define VIDEO_YUV400_720x480 			0x00900000 //0x0090 0000 ~ 0x009f ffff

#define VIDEO_YUV444_10BIT_720x480 		0x00a00000 //0x00a0 0000 ~ 0x00b4 0000
#define VIDEO_YUV422_10BIT_720x480 		0x00b40000 //0x00b4 0000 ~ 0x00C1 4000鈥�
#define VIDEO_YUV420_10BIT_720x480 		0x00c14000 //0x00c1 4000 ~ 0x00cb 4000
#define VIDEO_YUV400_10BIT_720x480 		0x00cb4000 //0x00cb 4000 ~ 0x00d2 0000
//tile
#define VIDEO_YUV444_TILE_720x480 		0x01000000 //0x0100 0000 ~ 0x011f c000
#define VIDEO_YUV422_TILE_720x480 		0x01200000 //0x0100 0000 ~ 0x011f c000
#define VIDEO_YUV420_TILE_720x480 		0x01400000 //0x0100 0000 ~ 0x011f c000
#define VIDEO_YUV400_TILE_720x480 		0x01600000 //0x0100 0000 ~ 0x011f c000

#define VIDEO_YUV444_TILE_720x480_10bit	0x01800000 //0x0100 0000 ~ 0x011f c000
#define VIDEO_YUV422_TILE_720x480_10bit 0x01a00000 //0x0100 0000 ~ 0x011f c000
#define VIDEO_YUV420_TILE_720x480_10bit 0x01c00000 //0x0100 0000 ~ 0x011f c000
#define VIDEO_YUV400_TILE_720x480_10bit 0x02000000 //0x0100 0000 ~ 0x011f c000
//afbce
#define VIDEO_AFBCD_YUV444_8BIT			0x20000000
#define VIDEO_AFBCD_YUV422_8BIT			0x21000000
#define VIDEO_AFBCD_YUV420_8BIT			0x22000000
#define VIDEO_AFBCD_YUV400_8BIT			0x23000000

#define VIDEO_AFBCD_YUV444_10BIT		0x24000000
#define VIDEO_AFBCD_YUV422_10BIT		0x25000000
#define VIDEO_AFBCD_YUV420_10BIT		0x26000000
#define VIDEO_AFBCD_YUV400_10BIT		0x27000000
//VP_SHARP_LUT

//720X480p
//overlay_test
#define overlay_1280x1280 					0x06000000
#define overlay_720x1280					0x07000000
#define overlay_720x24 						0x08000000
#define overlay_720x48 						0x09000000

#define ARGB8888_720x480 			0x00600000  // 0x6075 1800
#define RGB888_720x480				0x00752000  // 0x6084 F200
#define RGB565_720x480 				0x00850000  // 0x608f 8c00
#define YUV444_Y_720x480			0x008f9000  // 0x6094 d600
#define YUV444_UV_720x480 			0x0094e000  // 0x609F 6C00
#define YUV422_UV_720x480			0x009f7000  // 0x60A4 B600
#define YUV420_UV_720x480 			0x00a4c000  // 0x60A7 6300

#define YUYV422_720x480 			0x00a77000  // 0x60B1 FC00

#define VYUY422_720x480				0x00b20000  // 0x60BC 8C00

#define YUV444_Y_10Bit_720x480 		0x00bc9000  // 0x60C3 2780
#define YUV444_UV_10Bit_720x480		0x00c33000  // 0x60D0 5F00
#define YUV422_UV_10Bit_720x480		0x00d06000  // 0x60D6 F780
#define YUV420_UV_10Bit_720x480		0x00d70000  // 0x60DA 4BC0
#define RGBA5551_720x480 			0x00e00000  // 0x00eb 4000
#define ARG101010B2_4096x2160       0x00ec0000
//VICAP
#define YUV444I_1920x1080 			0x20ec0000
#define YUV444I_720x480 			0x22ec0000

//HDR YUV
#define HDR_480X270_0   			0x02000000
#define HDR_480X270_1				0x02400000
#define HDR_480X270_2				0x02800000
#define HDR_480X270_3				0x02c00000

//DCI
#define DCI_DEMO0_1920x1080_YUV420  0x22000000   //0X222f 8000
#define DCI_DEMO1_1920x1080_YUV420  0x22300000   //0x2260 0000

#define DCI_DEMO0_LUT0 				0x22700000
#define DCI_DEMO0_LUT1 				0x22800000

#define DCI_DEMO1_LUT0 				0x22900000
#define DCI_DEMO1_LUT1 				0x22A00000

//ARGB    0x6060_0000~0x627C 0000
#define ARGB888_4096x2160  0x00600000
#define RGB888_4096x2160   0x027C1000
//RGB565  0x6411 2000~0X651F 2000
#define RGB565_4096x2160  0x04112000
//YUV444 0X651F 3000~0X65A6 3000
#define YUV444_4096x2160_Y  0x051F3000

#define YUV444_4096x2160_UV  			   0x05A64000
//YUV422 0X66B4 4000~0X673B 5000
#define YUV422_4096x2160_UV 			   0x06B45000
//YUV420 0x673B 6000~0x677E E000
#define YUV420_4096x2160_UV 			   0x073B6000
//YUYV422 0x677E F000~0x688C F000
#define YUYV422_4096x2160 				   0x077EF000
//VYUY422 0x688D 0000~0x699B 0000
#define VYUY422_4096x2160 				   0x088D0000
//YUYV420 0x699B 1000~0x6AA9 1000
#define YUYV420_4096x2160 				   0x099B1000
//VYUY420 0x6AA9 2000~0x6BB7 2000
#define VYUY420_4096x2160 				   0x0AA92000
//YUV444-10B 0x6BB7 3000~0x6C5F F000
#define YUV444_10B_4096x2304_Y 			   0x0BB73000
// UV 0x6C60 0000~0x6DB1 8000
#define YUV444_10B_4096x2304_UV 		   	0x0C600000
#define YUV422_10B_4096x2304_UV  			0x0DB19000
#define YUV420_10B_4096x2304_UV  			0x0E5A6000

//TILE8x8 MODE
#define YUV444_TILE_Y						0x10100000  // 0x7010 0000~0x7012 8000
#define YUV444_TILE_UV 						0x10200000  // 0x7012 9000~0x7017 9000
#define YUV422_TILE_Y 						0x10300000  // 0x7017 a000~0x701a 2000
#define YUV422_TILE_UV						0x10400000  // 0x701a 3000~0x701c b000
#define YUV420_TILE_Y 						0x10500000  // 0x701c c000~0x701f 4000
#define YUV420_TILE_UV						0x10600000  // 0x701f 5000~0x7020 9000
#define YUV400_TILE_Y						0x10700000  // 0x7020 a000~0x7023 2000
#define YUV444_TILE_Y_10B 					0x10800000  // 0x7023 3000~0x7026 5000
#define YUV444_TILE_UV_10B 					0x10900000  // 0x7026 6000~0x702c a000
#define YUV422_TILE_Y_10B 					0x10a00000  // 0x702c b000~0x702f d000
#define YUV422_TILE_UV_10B 					0x10b00000  // 0x702f e000~0x7033 0000
#define YUV420_TILE_Y_10B 					0x10c00000  // 0x7033 1000~0x7036 3000
#define YUV420_TILE_UV_10B 					0x10d00000  // 0x7036 4000~0x7037 c000
#define YUV400_TILE_Y_10B 					0x10e00000  // 0x7037 d000~0x703A F000
//TILE4x4 MODE
#define YUV444_TILE4x4_Y					0x20100000  // 0x7010 0000~0x7012 8000
#define YUV444_TILE4x4_UV 					0x20200000  // 0x7012 9000~0x7017 9000
#define YUV422_TILE4x4_Y 					0x20300000  // 0x7017 a000~0x701a 2000
#define YUV422_TILE4x4_UV					0x20400000  // 0x701a 3000~0x701c b000
#define YUV420_TILE4x4_Y 					0x20500000  // 0x701c c000~0x701f 4000
#define YUV420_TILE4x4_UV					0x20600000  // 0x701f 5000~0x7020 9000
#define YUV400_TILE4x4_Y					0x20700000  // 0x7020 a000~0x7023 2000
#define YUV444_TILE4x4_Y_10B 				0x20800000  // 0x7023 3000~0x7026 5000
#define YUV444_TILE4x4_UV_10B 				0x20900000  // 0x7026 6000~0x702c a000
#define YUV422_TILE4x4_Y_10B 				0x20a00000  // 0x702c b000~0x702f d000
#define YUV422_TILE4x4_UV_10B 				0x20b00000  // 0x702f e000~0x7033 0000
#define YUV420_TILE4x4_Y_10B 				0x20c00000  // 0x7033 1000~0x7036 3000
#define YUV420_TILE4x4_UV_10B 				0x20d00000  // 0x7036 4000~0x7037 c000
#define YUV400_TILE4x4_Y_10B 				0x20e00000  // 0x7037 d000~0x703A F000



//TILE END
#define ARGB_AFBCE 							0x2a000000  // 0x8a00 0000~0x8a03_2538
#define RGB888_AFBCE 						0x2a040000  // 0x8a04 0000~0x8a07 0628
#define RGB565_AFBCE 						0x2a080000  // 0x8a08 0000~0x8a0a 68e0
#define RGBA1010102_AFBCE					0x2a0b0000  // 0x8a0b 0000~0x8a0e d808
#define YUV444_AFBCE 						0x2a100000  // 0x8a10 0000~0x8A12 6A00
#define YUV422_AFBCE 						0x2a130000  // 0x8A13 0000~0x8A14 D310
#define YUV420_AFBCE 						0x2a150000  // 0x8a15 0000~0x8A16 74A0
#define YUV444_101010_AFBCE 				0x2a170000  // 0x8a17 0000~0x8A1B D000
#define YUV422_101010_AFBCE					0x2a1c0000  // 0x8a1c 0000~0x8A1F 03E0
#define YUV420_101010_AFBCE 				0x2a200000  // 0x8a20 0000~0x8A22 47C0

//AFBCD 4K
#define ARGB_AFBCE_4K 						0x2b000000  // 0x8b00 0000~0x8bF2 3000
#define RGB888_AFBCE_4K 					0x2c400000  // 0x8bf2 4000~0x8CC9 E000
#define RGB565_AFBCE_4K 					0x2d800000  // 0x8CC9 F000~0x8D3B D000
#define YUV444_8BIT_AFBCE_4K                0x2e200000  // 0x8DD9 E000-0x8E77 D000
#define YUV422_8BIT_AFBCE_4K 				0x30000000  // 0x8E77 E000-0x8EF4 A000
#define YUV420_8BIT_AFBCE_4K 				0x31200000  // 0x8EF4 B000-0x8F5A 5000
#define YUV444_10BIT_AFBCE_4K 				0x32400000  // 0x8F5A 6000-0x904E D000
#define YUV422_10BIT_AFBCE_4K 				0x34000000  // 0x904E E000-0x910D 5000
#define YUV420_10BIT_AFBCE_4K 				0x36000000  // 0x910D 6000-0x91C6 0000
#define RGBA1010102_AFBCE_4K 				0x38000000  // 0x8b00 0000~0x8bF2 3000
//AFBCD_SPLIT_320X240
#define ARGB8888_AFBCD_SPLIT   				0x7BA00000
#define RGB888_AFBCD_SPLIT   				0x42347000
#define RGB565_AFBCD_SPLIT   				0x43d1e000

#define YUV422_8B_AFBCD_SPLIT				0x40500000
#define YUV422_10B_AFBCD_SPLIT				0x40600000
#define YUV420_8B_AFBCD_SPLIT				0x40700000
#define YUV420_10B_AFBCD_SPLIT				0x40800000

#define RGBA1010102_AFBCD_SPLIT   			0x44e85000
//AFBCD_COLOR_TRANSFORM

#define ARGB8888_COLOR_TRANSFORM			0x41000000
#define RGB888_COLOR_TRANSFORM				0x43000000
#define RGB565_COLOR_TRANSFORM				0x45000000
#define RGBA1010102_COLOR_TRANSFORM			0x47000000


#define LUT3D_MST_BASE              	    0x04A00000
#define SHARP_MST_BASE 						0x4ffff800
#define AFBCD_YUV_420_192X256_CP    		0x50000000

#define YUV444_TILE4X4_320x240_SP    		0x50030000
#define YUV422_TILE4X4_320x240_SP    		0x50080000
#define YUV420_TILE4X4_320x240_SP    		0x500b0000
#define YUV444_TILE4X4_320x240_10B_SP    	0x500E0000
#define YUV422_TILE4X4_320x240_10B_SP    	0x50130000
#define YUV420_TILE4X4_320x240_10B_SP    	0x50170000

#define YUV422_TILE4X4_720x480_SP 			0x50200000
#define YUV420_TILE4X4_720X480_SP 			0x502b0000


#define DCI_REG_MST							0x502ef000
#define DCI_MST								0x502f0000
#define ACM_CFG_MST 				    	0x50300000
#define ACM_CFG_MST_1 				    	0x50310000
#define ACM_CFG_MST_2 				    	0x50320000
#define ACM_CFG_MST_3 				    	0x50330000
#define FPGA_RAND_MST 						0x50500000
#define ACM_CFG_MST_7 				    	0x50370000
#define ACM_CFG_MST_8 				    	0x50380000
#define ACM_CFG_MST_9 				    	0x50390000

#define ACM_DEBUG_DDR       			    0x40400000

#define ACM_1920X1080_NV12_Y_0 			    0x50400000
#define ACM_1920X1080_NV12_UV_0			  	0x505FA400

#define ACM_1920X1080_NV12_Y_1 			    0x506F8000

#define ACM_1920X1080_NV12_Y_2 			    0x509F0000

#define ACM_1920X1080_NV12_Y_3 			    0x50ce8000
#define ACM_1920X1080_NV12_Y_4 			    0x50fe0000
#define ACM_1920X1080_NV12_Y_5 			    0x512d8000
#define ACM_1920X1080_NV12_Y_6 			    0x515d0000
#define ACM_1920X1080_NV12_Y_7 			    0x518c8000
#define ACM_1920X1080_NV12_Y_8 			    0x51bc0000
#define ACM_1920X1080_NV12_Y_9 			    0x51eb8000
#define ACM_1920X1080_NV12_Y_10 		    0x521b0000
#define ACM_1920X1080_NV12_Y_11 		    0x524a8000

#define RGBA1010102_AFBCE_TEST              0x54000000	//0x5400_0000 ~ 0x54c3_0000
#define RGBA1010102_AFBCE_TEST1             0x55000000  //0x5500_0000 ~ 0x55c3_0000


#define WB_YRGB_MST_BASE                    0x4b000000
#define WB_CBCR_MST_BASE                    0x4e000000

#define ARGB8888_8k 						0x39000000


///////////////////////////////////////////
//       SYS_CTRL
///////////////////////////////////////////
#define      VOP3_SYS_REG_CFG_DONE            0x00000
#define      VOP3_SYS_VERSION_INFO            0x00004
#define      VOP3_SYS_AUTO_CTRL_IMD           0x00008
#define      VOP3_SYS_VOP_STANDBY             0x0000C
#define      VOP3_SYS_AXI_LUT_CTRL_IMD        0x00024
#define      VOP3_SYS_PORT_CTRL_IMD           0x00028
#define      VOP3_SYS_VOP_PRE_PD_CTRL_IMD     0x0002C
#define      VOP3_SYS_CLUSTER_PD_CTRL_IMD     0x00030
#define      VOP3_SYS_ESMART_PD_CTRL_IMD      0x00034
#define      VOP3_SYS_VAR_FERQ_CTRL_IMD       0x00038
#define      VOP3_METADATA_CTRL               0x00040
#define      VOP3_METADATA_MST                0x00044
#define      VOP3_FBC_TIMEOUT_CTRL            0x00048
///////////////////////////////////////////
//       SYS0_CTRL
///////////////////////////////////////////
#define      VOP3_SYS_AXI0_CTRL_IMD          0x00000
#define      VOP3_SYS_AXI0_HURRY_CTRL_IMD    0x00004
#define      VOP3_SYS_AXI0_MMU_CTRL          0x00008
#define      VOP3_SYS_AXI0_STATUS            0x0000C
#define      VOP3_SYS0_INTR_EN               0x00080
#define      VOP3_SYS0_INTR_CLR              0x00084
#define      VOP3_SYS0_INTR_STATUS           0x00088
#define      VOP3_SYS0_INTR_RAW_STATUS       0x0008C
#define      VOP3_FBCD_INTR_EN0              0x00090
#define      VOP3_FBCD_INTR_CLR0             0x00094
#define      VOP3_FBCD_INTR_STATUS0          0x00098
#define      VOP3_FBCD_INTR_RAW_STATUS0      0x0009C
///////////////////////////////////////////
//       SYS1_CTRL
///////////////////////////////////////////
#define      VOP3_SYS_AXI1_CTRL_IMD          0x00000
#define      VOP3_SYS_AXI1_HURRY_CTRL_IMD    0x00004
#define      VOP3_SYS_AXI1_MMU_CTRL          0x00008
#define      VOP3_SYS_AXI1_STATUS            0x0000C
#define      VOP3_SYS1_INTR_EN               0x00080
#define      VOP3_SYS1_INTR_CLR              0x00084
#define      VOP3_SYS1_INTR_STATUS           0x00088
#define      VOP3_SYS1_INTR_RAW_STATUS       0x0008C
#define      VOP3_FBCD_INTR_EN0              0x00090
#define      VOP3_FBCD_INTR_CLR0             0x00094
#define      VOP3_FBCD_INTR_STATUS0          0x00098
#define      VOP3_FBCD_INTR_RAW_STATUS0      0x0009C
///////////////////////////////////////////
//       INFACE_CTRL
///////////////////////////////////////////
#define      VOP3_MIPI0_INFACE_CTRL        0x00000
#define      VOP3_HDMI0_INFACE_CTRL        0x00004
#define      VOP3_EDP0_INFACE_CTRL         0x00008
#define      VOP3_DP0_INFACE_CTRL          0x0000C
#define      VOP3_RGB_INFACE_CTRL          0x00014
#define      VOP3_DP1_INFACE_CTRL          0x00024
#define      VOP3_DP2_INFACE_CTRL          0x00030
///////////////////////////////////////////
//       WB_CTRL
///////////////////////////////////////////
#define      VOP3_WB_CTRL0                 0x00000
#define      VOP3_WB_XSPD_FACTOR           0x00004
#define      VOP3_WB_YRGB_MST              0x00008
#define      VOP3_WB_CBR_MST               0x0000C
#define      VOP3_WB_VIR_STRIDE            0x00010
#define      VOP3_WB_TIMEOUT_CTRL          0x00014
#define      VOP3_WB_WIN_CTRL              0x00018
#define      VOP3_WB_CSC_COE01_00          0x00020
#define      VOP3_WB_CSC_COE10_02          0x00024
#define      VOP3_WB_CSC_COE12_11          0x00028
#define      VOP3_WB_CSC_COE21_20          0x0002C
#define      VOP3_WB_CSC_COE22             0x00030
#define      VOP3_WB_CSC_OFFSET0           0x00034
#define      VOP3_WB_CSC_OFFSET1           0x00038
#define      VOP3_WB_CSC_OFFSET2           0x0003C
#define      VOP3_WB_CFG_DONE              0x00040
///////////////////////////////////////////
//       SECURE_CTRL
///////////////////////////////////////////
#define      VOP3_SEC_INFACE_CTRL          0x00000
#define      VOP3_SEC_DRM_CTRL             0x00004
#define      VOP3_SEC_DRM_PORT_SEL         0x00008
#define      VOP3_SEC_PORT0_LAYER_SEL      0x00010
#define      VOP3_SEC_PORT1_LAYER_SEL      0x00014
#define      VOP3_SEC_PORT2_LAYER_SEL      0x00018
#define      VOP3_SEC_AXI_RID_PROT         0x00020
#define      VOP3_SYS_OTP_MIRR_CTRL_IMD    0x00030
///////////////////////////////////////////
//       VOP3
///////////////////////////////////////////
#define      VOP3_OVERLAY_CTRL           0x00000
#define      VOP3_LAYER_SEL              0x00004
#define      VOP3_MIX0_SRC_COLOR_CTRL    0x00020
#define      VOP3_MIX0_DST_COLOR_CTRL    0x00024
#define      VOP3_MIX0_SRC_ALPHA_CTRL    0x00028
#define      VOP3_MIX0_DST_ALPHA_CTRL    0x0002C
#define      VOP3_MIX1_SRC_COLOR_CTRL    0x00030
#define      VOP3_MIX1_DST_COLOR_CTRL    0x00034
#define      VOP3_MIX1_SRC_ALPHA_CTRL    0x00038
#define      VOP3_MIX1_DST_ALPHA_CTRL    0x0003C
#define      VOP3_MIX2_SRC_COLOR_CTRL    0x00040
#define      VOP3_MIX2_DST_COLOR_CTRL    0x00044
#define      VOP3_MIX2_SRC_ALPHA_CTRL    0x00048
#define      VOP3_MIX2_DST_ALPHA_CTRL    0x0004C
#define      VOP3_BG_MIX_CTRL            0x00070
#define      VOP3_CUR_SRC_COLOR_CTRL     0x00080
#define      VOP3_CUR_DST_COLOR_CTRL     0x00084
#define      VOP3_CUR_SRC_ALPHA_CTRL     0x00088
#define      VOP3_CUR_DST_ALPHA_CTRL     0x0008C
#define      VOP3_EXTRA_SRC_COLOR_CTRL   0x00090
#define      VOP3_EXTRA_DST_COLOR_CTRL   0x00094
#define      VOP3_EXTRA_SRC_ALPHA_CTRL   0x00098
#define      VOP3_EXTRA_DST_ALPHA_CTRL   0x0009C
#define      VOP3_HDR_SRC_COLOR_CTRL     0x000A0
#define      VOP3_HDR_DST_COLOR_CTRL     0x000A4
#define      VOP3_HDR_SRC_ALPHA_CTRL     0x000A8
#define      VOP3_HDR_DST_ALPHA_CTRL     0x000AC
#define      VOP3_CGC_SRC_COLOR_CTRL     0x000B0
#define      VOP3_CGC_DST_COLOR_CTRL     0x000B4
#define      VOP3_CGC_SRC_ALPHA_CTRL     0x000B8
#define      VOP3_CGC_DST_ALPHA_CTRL     0x000BC
///////////////////////////////////////////
//       POST0_CTRL
///////////////////////////////////////////
#define      VOP3_POST_DSP_CTRL             0x00000
#define      VOP3_POST_MIPI_CTRL            0x00004
#define      VOP3_POST_COLOR_CTRL           0x00008
#define      VOP3_POST_CORE_CLK             0x0000C
#define      VOP3_POST_3D_LUT_CTRL          0x00010
#define      VOP3_POST_3D_LUT_R             0x00014
#define      VOP3_POST_3D_LUT_G             0x00018
#define      VOP3_POST_3D_LUT_B             0x0001C
#define      VOP3_POST_3DLUT_MST            0x00020
#define      VOP3_POST_CRC_CHECK_VALUE      0x00024
#define      VOP3_POST_CRC_OUT              0x00028
#define      VOP3_POST_DSP_BG               0x0002C
#define      VOP3_POST_PRE_SCAN_HTIMING     0x00030
#define      VOP3_POST_DSP_HACT_INFO        0x00034
#define      VOP3_POST_DSP_VACT_INFO        0x00038
#define      VOP3_POST_SCL_FACTOR_YRGB      0x0003C
#define      VOP3_POST_SCL_CTRL             0x00040
#define      VOP3_POST_DSP_VACT_INFO_F1     0x00044
#define      VOP3_POST_DSP_HTOTAL_HS_END    0x00048
#define      VOP3_POST_DSP_HACT_ST_END      0x0004C
#define      VOP3_POST_DSP_VTOTAL_VS_END    0x00050
#define      VOP3_POST_DSP_VACT_ST_END      0x00054
#define      VOP3_POST_DSP_VS_ST_END_F1     0x00058
#define      VOP3_POST_DSP_VACT_ST_END_F1   0x0005C
#define      VOP3_POST_BCSH_CTRL            0x00060
#define      VOP3_POST_BCSH_BCS             0x00064
#define      VOP3_POST_BCSH_H               0x00068
#define      VOP3_POST_BCSH_COLOR_BAR       0x0006C
#define      VOP3_POST_ACM_R2Y_CTRL         0x00070
#define      VOP3_POST_ACM_R2Y_COE0102      0x00074
#define      VOP3_POST_ACM_R2Y_COE1011      0x00078
#define      VOP3_POST_ACM_R2Y_COE1220      0x0007C
#define      VOP3_POST_ACM_R2Y_COE2122      0x00080
#define      VOP3_POST_ACM_R2Y_OFFSET0      0x00084
#define      VOP3_POST_ACM_R2Y_OFFSET1      0x00088
#define      VOP3_POST_ACM_R2Y_OFFSET2      0x0008C
#define      VOP3_POST_LINE_FLAG            0x00090
#define      VOP3_POST_DITHER_FRC_0         0x000A0
#define      VOP3_POST_DITHER_FRC_1         0x000A4
#define      VOP3_POST_DITHER_FRC_2         0x000A8
#define      VOP3_POST_INTR_EN              0x000C0
#define      VOP3_POST_INTR_CLR             0x000C4
#define      VOP3_POST_INTR_STATUS          0x000C8
#define      VOP3_POST_INTR_RAW_STATUS      0x000CC
#define      VOP3_POST_ACM_CTRL             0x000D0
#define      VOP3_POST_ACM_Y2R_COE0102      0x000D4
#define      VOP3_POST_ACM_Y2R_COE1011      0x000D8
#define      VOP3_POST_ACM_Y2R_COE1220      0x000DC
#define      VOP3_POST_ACM_Y2R_COE2122      0x000E0
#define      VOP3_POST_ACM_Y2R_OFFSET0      0x000E4
#define      VOP3_POST_ACM_Y2R_OFFSET1      0x000E8
#define      VOP3_POST_ACM_Y2R_OFFSET2      0x000EC
#define      VOP3_POST_STATUS               0x000F0
#define      VOP3_POST_CLK_CNT              0x000F4
#define      VOP3_POST_MCU_CTRL             0x000F8
#define      VOP3_POST_CFG_DONE             0x000FC

#define      VOP3_POST_BCSH_Y2R_COE00       0x000D0
#define      VOP3_POST_BCSH_Y2R_COE02_01    0x000D4
#define      VOP3_POST_BCSH_Y2R_COE11_10    0x000D8
#define      VOP3_POST_BCSH_Y2R_COE20_12    0x000DC
#define      VOP3_POST_BCSH_Y2R_COE22_21    0x000E0
#define      VOP3_POST_BCSH_Y2R_OFFSET0     0x000E4
#define      VOP3_POST_BCSH_Y2R_OFFSET1     0x000E8
#define      VOP3_POST_BCSH_Y2R_OFFSET2     0x000EC
///////////////////////////////////////////
//       CLUSTER0
///////////////////////////////////////////
#define      CLUSTER_CTRL0                  0x00000
#define      CLUSTER_CTRL1                  0x00004
#define      CLUSTER_CTRL2                  0x00008
#define      CLUSTER_YRGB_MST               0x00010
#define      CLUSTER_CBCR_MST               0x00014
#define      CLUSTER_VIR                    0x00018
#define      CLUSTER_KEY_CTRL               0x0001C
#define      CLUSTER_ACT_INFO               0x00020
#define      CLUSTER_DSP_INFO               0x00024
#define      CLUSTER_DSP_ST                 0x00028
#define      CLUSTER_DSP_BG                 0x0002C
#define      CLUSTER_SCL_FACTOR_YRGB        0x00030
#define      CLUSTER_SCL_FACTOR_CBCR        0x00030
#define      CLUSTER_SCL_OFFSET             0x00038
#define      CLUSTER_TRANSFORMED_OFFSET     0x0003C
#define      CLUSTER_ZME_CTRL               0x00040
#define      CLUSTER_ZME_DERING_PARA        0x00044
#define      CLUSTER_FBCD_OUTPUT_CTRL       0x00050
#define      CLUSTER_FBCD_MODE              0x00054
#define      CLUSTER_FBCD_HDR_PTR           0x00058
#define      CLUSTER_FBCD_VIR_WIDTH         0x0005C
#define      CLUSTER_FBCD_SIZE              0x00060
#define      CLUSTER_FBCD_PIC_OFFSET        0x00064
#define      CLUSTER_FBCD_DIS_OFFSET        0x00068
#define      CLUSTER_FBCD_CTRL              0x0006C
#define      CLUSTER_PLD_PTR_OFFSET         0x00078
#define      CLUSTER_PLD_PTR_RANGE          0x0007C
#define      CLUSTER_CTRL                	0x00100
#define      CLUSTER_DCI_BLK_SIZE                0x00104
#define      CLUSTER_DCI_BLK_OFFSET              0x00108
#define      CLUSTER_DCI_PIX_REGION              0x0010C
#define      CLUSTER_DCI_LUMA_SAT_ADJ_0          0x00110
#define      CLUSTER_DCI_LUMA_SAT_ADJ_1          0x00114
#define      CLUSTER_DCI_CTRL                    0x00118
#define      CLUSTER_DCI_LUT_MST                 0x0011C
#define      CLUSTER_DCI_DBG_CTRL                0x00120
#define      CLUSTER_DCI_DBG_PIX                 0x00130
#define      CLUSTER_DCI_CSC_COE01_00            0x00140
#define      CLUSTER_DCI_CSC_COE10_02            0x00144
#define      CLUSTER_DCI_CSC_COE12_11            0x00148
#define      CLUSTER_DCI_CSC_COE21_20            0x0014C
#define      CLUSTER_DCI_CSC_COE22               0x00150
#define      CLUSTER_DCI_CSC_OFFSET0             0x00154
#define      CLUSTER_DCI_CSC_OFFSET1             0x00158
#define      CLUSTER_DCI_CSC_OFFSET2             0x0015C
#define      CLUSTER_CAP_BUFF_DATA0              0x00160
#define      CLUSTER_CAP_BUFF_DATA1              0x00164
#define      CLUSTER_CAP_BUFF_DATA2              0x00168
#define      CLUSTER_CAP_BUFF_DATA3              0x0016C
#define      CLUSTER_WIN0_CSC_COE01_00           0x00180
#define      CLUSTER_WIN0_CSC_COE10_02           0x00184
#define      CLUSTER_WIN0_CSC_COE12_11           0x00188
#define      CLUSTER_WIN0_CSC_COE21_20           0x0018C
#define      CLUSTER_WIN0_CSC_COE22              0x00190
#define      CLUSTER_WIN0_CSC_OFFSET0            0x00194
#define      CLUSTER_WIN0_CSC_OFFSET1            0x00198
#define      CLUSTER_WIN0_CSC_OFFSET2            0x0019C
#define      CLUSTER_WIN1_CSC_COE01_00           0x001A0
#define      CLUSTER_WIN1_CSC_COE10_02           0x001A4
#define      CLUSTER_WIN1_CSC_COE12_11           0x001A8
#define      CLUSTER_WIN1_CSC_COE21_20           0x001AC
#define      CLUSTER_WIN1_CSC_COE22              0x001B0
#define      CLUSTER_WIN1_CSC_OFFSET0            0x001B4
#define      CLUSTER_WIN1_CSC_OFFSET1            0x001B8
#define      CLUSTER_WIN1_CSC_OFFSET2            0x001BC
#define      CLUSTER_CLUSTER_SRC_COLOR_CTRL      0x001D0
#define      CLUSTER_CLUSTER_DST_COLOR_CTRL      0x001D4
#define      CLUSTER_CLUSTER_SRC_ALPHA_CTRL      0x001D8
#define      CLUSTER_CLUSTER_DST_ALPHA_CTRL      0x001DC
#define      CLUSTER_CLUSTER_WIN0_CRC_EN         0x001E0
#define      CLUSTER_CLUSTER_WIN0_CRC_STATUS     0x001E4
#define      CLUSTER_CLUSTER_WIN1_CRC_EN         0x001E8
#define      CLUSTER_CLUSTER_WIN1_CRC_STATUS     0x001EC
#define      CLUSTER_CLUSTER_PORT_SEL_IMD        0x001F4
#define      CLUSTER_CLUSTER_DLY_NUM             0x001F8
#define      CLUSTER_CLUSTER_CFG_DONE            0x001FC
///////////////////////////////////////////
//       ESMART0
///////////////////////////////////////////
#define      ESMART_CTRL0                		 0x00000
#define      ESMART_CTRL1                		 0x00004
#define      ESMART_AXI_CTRL_IMD         		 0x00008

#define      ESMART_FMT_CTRL             		 0x0000
#define      ESMART_YRGB_MST             		 0x0004
#define      ESMART_CBCR_MST             		 0x0008
#define      ESMART_VIR_STRIDE                   0x000C
#define      ESMART_ACT_INFO             		 0x0010
#define      ESMART_DSP_INFO            		 0x0014
#define      ESMART_DSP_OFFSET           		 0x0018
#define      ESMART_SCL_CTRL            		 0x0020
#define      ESMART_SCL_FACTOR_YRGB     		 0x0024
#define      ESMART_SCL_FACTOR_CBCR     		 0x0028
#define      ESMART_SCL_OFFSET          		 0x002C

#define      ESMART_KEY_CTRL              0x000D0
#define      ESMART_BG_CTRL               0x000D4
#define      ESMART_ALPHA_MAP             0x000D8
#define      ESMART_CRC_EN                0x000E0
#define      ESMART_CRC_STATUS            0x000E4
#define      ESMART_PORT_SEL_IMD          0x000F4
#define      ESMART_DLY_NUM               0x000F8
#define      ESMART_CSC_COE01_00          0x00100
#define      ESMART_CSC_COE10_02          0x00104
#define      ESMART_CSC_COE12_11          0x00108
#define      ESMART_CSC_COE21_20          0x0010C
#define      ESMART_CSC_COE22             0x00110
#define      ESMART_CSC_OFFSET0           0x00114
#define      ESMART_CSC_OFFSET1           0x00118
#define      ESMART_CSC_OFFSET2           0x0011C
#define      ESMART_CAP_BUFF_DATA0        0x00120
#define      ESMART_CAP_BUFF_DATA1        0x00124
#define      ESMART_CAP_BUFF_DATA2        0x00128
#define      ESMART_CAP_BUFF_DATA3        0x0012C
#define      ESMART_CFG_DONE              0x001FC
///////////////////////////////////////////
///////////////////////////////////////////
//       MSMART0
///////////////////////////////////////////
#define      MSMART_WIN_CTRL0                    0x00000
#define      MSMART_WIN_AXI_CTRL                 0x00004
#define      MSMART_WIN_ALHPE_VP                 0x00008
#define      MSMART_WIN_REGION_MST               0x0000C
#define      MSMART_WIN_SCL_CTRL                 0x00010
#define      MSMART_WIN_SCL_FACTOR_YRGB          0x00014
#define      MSMART_WIN_CRC_CHKOU_STATUS         0x00018
#define      MSMART_WIN_ACT_PRE_INFO             0x0001C
#define      MSMART_WIN_DSP_INFO                 0x00020
#define      MSMART_WIN_DSP_ST                   0x00024
#define      MSMART_WIN_DSP_BG                   0x00028
#define      MSMART_WIN_COLOR_KEY                0x0002C
#define      MSMART_WIN_CSC_COE_0                0x00030
#define      MSMART_WIN_CSC_COE_1                0x00034
#define      MSMART_WIN_CSC_COE_2                0x00038
#define      MSMART_WIN_CSC_COE_3                0x0003C
#define      MSMART_WIN_CSC_COE_4                0x00040
#define      MSMART_WIN_CSC_OFFSET0              0x00044
#define      MSMART_WIN_CSC_OFFSET1              0x00048
#define      MSMART_WIN_CSC_OFFSET2              0x0004C
#define      MSMART_WIN_REGION0_YRGB_MST         0x00050
#define      MSMART_WIN_REGION0_CBCR_MST         0x00054
#define      MSMART_WIN_REGION0_VIR              0x00058
#define      MSMART_WIN_REGION0_ACT_INFO         0x0005C
#define      MSMART_WIN_REGION0_ACT_OFFSET       0x00060
#define      MSMART_WIN_REGION0_DSP_OFFSET       0x00064
#define      MSMART_WIN_CAP_BUFF_DATA0           0x001E0
#define      MSMART_WIN_CAP_BUFF_DATA1           0x001E4
#define      MSMART_WIN_CAP_BUFF_DATA2           0x001E8
#define      MSMART_WIN_CAP_BUFF_DATA3           0x001EC
#define      MSMART_WIN_CAP_BUFF_STATUS          0x001F0
#define      MSMART_WIN_CFG_DONE                 0x001FC
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
//       HWC
///////////////////////////////////////////
#define      HWC_BASE                            0x00003800

#define      HWC_HWC_CTRL0                       0x00000
#define      HWC_HWC_CTRL1                       0x00004
#define      HWC_HWC_AXI_CTRL_IMD                0x00008
#define      HWC_HWC_MST_CTL                     0x0000C
#define      HWC_HWC_MST                         0x00010
#define      HWC_HWC_VIR                         0x00014
#define      HWC_HWC_SIZE_INFO                   0x00018
#define      HWC_HWC_DSP_OFFSET                  0x0001C
#define      HWC_HWC_KEY_CTRL                    0x00020
#define      HWC_HWC_BG_EN                       0x00024
#define      HWC_HWC_PORT_SEL_IMD                0x00028
#define      HWC_HWC_DLY_NUM                     0x0002C
#define      HWC_HWC_CSC_COE00_01                0x00030
#define      HWC_HWC_CSC_COE02_10                0x00034
#define      HWC_HWC_CSC_COE11_12                0x00038
#define      HWC_HWC_CSC_COE20_21                0x0003C
#define      HWC_HWC_CSC_COE22                   0x00040
#define      HWC_HWC_CSC_OFFSET0                 0x00044
#define      HWC_HWC_CSC_OFFSET1                 0x00048
#define      HWC_HWC_CSC_OFFSET2                 0x0004C
///////////////////////////////////////////
//       GAMMA_LUT_WRADDR
///////////////////////////////////////////
#define      GAMMA_LUT_WRADDR_BASE                0x00005000
///////////////////////////////////////////
//       ACM
///////////////////////////////////////////
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


//0x0010//0x001c
#define v_AXI_DMA_STOP(x)                      			(((x)&0x1)<<0)
#define v_AXI_OUTSTANDING_NUM_EN(x)                     (((x)&0x1)<<1)
#define v_AXI_OUTSTANDING_NUM(x)                        (((x)&0x3f)<<4)
#define v_AXI_CLUSTER_PRIORITY_EN(x)                    (((x)&0x1)<<12)

#define m_AXI_DMA_STOP             						(0x1<<0)
#define m_AXI_OUTSTANDING_NUM_EN             			(0x1<<1)
#define m_AXI_OUTSTANDING_NUM                			(0x3f<<4)
#define m_AXI_CLUSTER_PRIORITY_EN             			(0x3f<<12)

//0x0014/0x0018
#define v_AXI_HURRY_W_EN(x)             					(((x)&0x1)<<0)
#define v_AXI_HURRY_W_VALUE(x)             					(((x)&0x3)<<1)
#define v_AXI_HURRY_W_MODE(x)          						(((x)&0x3)<<3)
#define v_AXI_HURRY_R_EN(x)             					(((x)&0x1)<<8)
#define v_AXI_HURRY_R_VALUE(x)             					(((x)&0x3)<<9)

#define v_AXI_QOS_EN(x)             					    (((x)&0x1)<12)
#define v_AXI_QOS_VALUE(x)             					    (((x)&0x3)<<13)



#define v_AXI_URGENCY_EN(x)             					(((x)&0x1)<<24)

#define m_AXI_HURRY_W_EN             						(0x1<<0)
#define m_AXI_HURRY_W_VALUE             					(0x3<<1)
#define m_AXI_HURRY_W_MODE          						(0x3<<3)
#define m_AXI_HURRY_R_EN             						(0x1<<8)
#define m_AXI_HURRY_R_VALUE             					(0x3<<9)

#define m_AXI_QOS_EN             					        (0x1<<12)
#define m_AXI_QOS_VALUE             					    (0x3<<13)

#define m_AXI_URGENCY_EN             					    (0x1<<24)

//0x0020
#define v_RKMMU2_EN(x)                      	    	(((x)&0x1)<<0)
#define v_RKMMU2_SEL(x)                      	    	(((x)&0x1)<<1)
#define v_RKMMU_RST_EN(x)                      	    	(((x)&0x1)<<11)

#define v_MMU_BYPASS_EN(x)                      		(((x)&0x1)<<0)
#define v_MMU_BYPASS_ID(x)                      		(((x)&0x1f)<<4)
#define v_MMU_REGDONE_SEL(x)                            (((x)&0x3)<<10)

#define m_RKMMU2_EN           					        (0x1<<0)
#define m_RKMMU2_SEL           					        (0x1<<1)
#define m_RKMMU_RST_EN           					    (0x1<<11)

#define m_MMU_BYPASS_EN           					    (0x1<<0)
#define m_MMU_BYPASS_ID           					    (0x1f<<4)
#define m_MMU_REGDONE_SEL                               (0x3<<10)


//0x0024
#define v_LUT_DMA_EN(x)                      		(((x)&0x1)<<0)
#define v_LUT_DMA_STOP(x)                      		(((x)&0x1)<<1)
#define v_LUT_DMA_RLEN(x)                      		(((x)&0x3)<<2)
#define v_LUT_DMA_RID(x)                      		(((x)&0x1f)<<4)
#define v_LUT_USE_AXI1(x)                         	(((x)&0x1)<<9)

#define m_LUT_DMA_EN           						(0x1<<0)
#define m_LUT_DMA_STOP         						(0x1<<1)
#define m_LUT_DMA_RLEN         						(0x3<<2)
#define m_LUT_DMA_RID           					(0x1f<<4)
#define m_LUT_USE_AXI1                        	    (0x1<<9)

//0x0028
#define v_VP0_INTERLACE_FRM_REG_DONE(x)                     (((x)&0x1)<<0 )
#define v_VP1_INTERLACE_FRM_REG_DONE(x)                     (((x)&0x1)<<1 )
#define v_VP2_INTERLACE_FRM_REG_DONE(x)                     (((x)&0x1)<<2 )
#define v_DSP_VS_T_SEL(x)                           		(((x)&0x1)<<4 )
#define v_AUTO_CS_EN(x)                           		    (((x)&0x1)<<5 )
#define v_PORT0_8K_MODE(x)                           		(((x)&0x1)<<6 )
#define v_PORT0_MEM_SHARE(x)                           		(((x)&0x1)<<7 )
#define v_PORT0_VFP_DMA_STOP(x)                      		(((x)&0x1)<<8 )
#define v_PORT1_VFP_DMA_STOP(x)                      		(((x)&0x1)<<9 )
#define v_PORT2_VFP_DMA_STOP(x)                      		(((x)&0x1)<<10)
#define v_PORT3_VFP_DMA_STOP(x)                      		(((x)&0x1)<<11)
#define v_PORT0_DCLK_SRC_SEL(x)                             (((x)&0x1)<<12)
#define v_PORT1_DCLK_SRC_SEL(x)                             (((x)&0x1)<<13)
#define v_PORT2_DCLK_SRC_SEL(x)                             (((x)&0x1)<<14)
#define v_VP_INTR_MERGE_EN(x)                      	    	(((x)&0x1)<<14)  //TODO


#define m_VP0_INTERLACE_FRM_REG_DONE                            (0x1<<0 )
#define m_VP1_INTERLACE_FRM_REG_DONE                            (0x1<<1 )
#define m_VP2_INTERLACE_FRM_REG_DONE                            (0x1<<2 )
#define m_DSP_VS_T_SEL        						            (0x1<<4 )
#define m_AUTO_CS_EN        						            (0x1<<5 )
#define m_PORT0_8K_MODE        						            (0x1<<6 )
#define m_PORT0_MEM_SHARE        						        (0x1<<7 )
#define m_PORT0_VFP_DMA_STOP             						(0x1<<8 )
#define m_PORT1_VFP_DMA_STOP             						(0x1<<9 )
#define m_PORT2_VFP_DMA_STOP             						(0x1<<10)
#define m_PORT3_VFP_DMA_STOP             						(0x1<<11)
#define m_PORT0_DCLK_SRC_SEL                                    (0x1<<12)
#define m_PORT1_DCLK_SRC_SEL                                    (0x1<<13)
#define m_PORT2_DCLK_SRC_SEL                                    (0x1<<14)
#define m_VP_INTR_MERGE_EN              						(0x1<<14)  //TODO

//0x0030
#define v_CLUSTER01_PD_EN(x)                           		(((x)&0x1)<<0 )
#define m_CLUSTER01_PD_EN        						    (0x1<<0 )

//0x0034
#define v_ESMART_PD_EN(x)                           		(((x)&0x1)<<0 )
#define v_ESMART01_8k_EN(x)                           		(((x)&0x1)<<4 )
#define v_ESMART23_8k_EN(x)                           		(((x)&0x1)<<5 )
#define v_ESMART_LB_MODE(x)                           		(((x)&0x3)<<6 )
#define v_ESMART_BPP_LUT_EN(x)                           	(((x)&0x1)<<8 )
#define v_ESMART_BPP_LUT_SEL(x)                           	(((x)&0x3)<<10)

#define m_ESMART_PD_EN        						        (0x1<<0 )
#define m_ESMART01_8k_EN        						    (0x1<<4 )
#define m_ESMART23_8k_EN        						    (0x1<<5 )
#define m_ESMART_LB_MODE        						    (0x3<<6 )
#define m_ESMART_BPP_LUT_EN        						    (0x1<<8 )
#define m_ESMART_BPP_LUT_SEL        						(0x3<<10)

//0x0040
#define v_METADATA_LUT_EN(x)                           		(((x)&0x1)<<0 )
#define v_METADATA_RD_ERR_CLR(x)                            (((x)&0x1)<<1 )
#define v_METADATA_LUT_RID(x)                           	(((x)&0xf)<<4 )
#define v_METADATA_LUT_WRITE_START(x)                       (((x)&0x7f)<<8 )
#define v_METADATA_LUT_SIZE(x)                              (((x)&0x7ff)<<16 )
#define v_METADATA_LUT_PORT_SEL(x)                          (((x)&0x3)<<30 )

#define m_METADATA_LUT_EN        						    (0x1<<0 )
#define m_METADATA_RD_ERR_CLR                               (0x1<<1 )
#define m_METADATA_LUT_RID        						    (0xf<<4 )
#define m_METADATA_LUT_WRITE_START       					(0x7f<<8 )
#define m_METADATA_LUT_SIZE        						    (0x7ff<<16 )
#define m_METADATA_LUT_PORT_SEL       						(0x3<<30 )

//0x0044
#define v_METADATA_LUT_MST(x)                           	(((x)&0xffffffff)<<0 )
#define m_METADATA_LUT_MST        						    (0xffffffff<<0 )

//0x0048
#define v_AFBC_TIME_OUT_CNT(x)                           	(((x)&0x7fffffff)<<0 )
#define v_AFBC_TIME_OUT_CNT_EN(x)                           (((x)&0x1)<<31 )

#define m_AFBC_TIME_OUT_CNT        						    (0x7fffffff<<0 )
#define m_AFBC_TIME_OUT_CNT_EN        						(0x1<<31 )

//0x004c
#define v_VOP_IO_VP0_VSYNC_SEL(x)                           (((x)&0x3) << 0)
#define v_VOP_IO_VP1_VSYNC_SEL(x)                           (((x)&0x3) << 2)
#define v_VOP_IO_VP2_VSYNC_SEL(x)                           (((x)&0x3) << 4)

#define m_VOP_IO_VP0_VSYNC_SEL                              ((0x3) << 0)
#define m_VOP_IO_VP1_VSYNC_SEL                              ((0x3) << 2)
#define m_VOP_IO_VP2_VSYNC_SEL                              ((0x3) << 4)


//0x0058
#define v_SHARP_AHB_PORT_SEL(x)         			        (((x)&0x3)<<10)
#define v_GAMMA_AHB_PORT_SEL(x)         			        (((x)&0x3)<<12)
#define v_ACM_AHB_PORT_SEL(x)           			        (((x)&0x3)<<14)


#define m_SHARP_AHB_PORT_SEL              			        (0x3<<10)
#define m_GAMMA_AHB_PORT_SEL            			        (0x3<<12)
#define m_ACM_AHB_PORT_SEL              			        (0x3<<14)

//
#define v_DSP_LINE_FLAG_NUM1(x)         			(((x)&0x1fff)<<16)
#define v_DSP_LINE_FLAG_NUM0(x)         			(((x)&0xffff)<<0)
#define v_DSP_PORT_FULL_THOLD(x)                    (((x)&0x7   )<<29)

#define m_DSP_LINE_FLAG_NUM1            			(0x1fff<<16)
#define m_DSP_LINE_FLAG_NUM0            			(0xffff<<0)
#define m_DSP_PORT_FULL_THOLD                       (0x7   <<29)


#define v_INTR_EN(x)         			            (((x)&0xffffffff)<<0)
#define m_INTR_EN            			            (0xffffffff<<0)

#define v_INTR_CLR(x)         			            (((x)&0xffffffff)<<0)
#define m_INTR_CLR            			            (0xffffffff<<0)

//#define m_HDMI0_EDP0_DCLK_SEL                           ((0x3)<<16)
//#define m_HDMI0_EDP0_PIX_CLK_SEL                        ((0x1)<<18)
//#define m_HDMI1_EDP1_DCLK_SEL                           ((0x3)<<20)
//#define m_HDMI1_EDP1_PIX_CLK_SEL                        ((0x1)<<22)
//#define m_MIPI0_PIX_CLK_SEL                             ((0x3)<<24)
//#define m_MIPI1_PIX_CLK_SEL                             ((0x3)<<26)
//#define m_RGB_PIX_CLK_SEL                               ((0x1)<<28)
//#define m_RGB_CORE_CLK_SEL                              ((0x1)<<29)

////DSC_CTRL
//#define v_DSC0_PORT_SEL(x)                              ((x&0x1)<<0 )
//#define v_DSC_8K_SLICE_CLK_SEL(x)                       ((x&0x1)<<1 )
//#define v_DSC_8K_FLUSH(x)                               ((x&0x1)<<2 )
//#define v_MIPI0_DSC_EN(x)                               ((x&0x1)<<3 )
//#define v_HDMI0_DSC_EN(x)                               ((x&0x1)<<4 )
//#define v_DSC1_PORT_SEL(x)                              ((x&0x1)<<16)
//#define v_DSC_4K_SLICE_CLK_SEL(x)                       ((x&0x1)<<17)
//#define v_DSC_4K_FLUSH(x)                               ((x&0x1)<<18)
//#define v_MIPI1_DSC_EN(x)                               ((x&0x1)<<19)
//#define v_HDMI1_DSC_EN(x)                               ((x&0x1)<<20)
//
//#define m_DSC0_PORT_SEL                                 ((0x1)<<0 )
//#define m_DSC_8K_SLICE_CLK_SEL                          ((0x1)<<1 )
//#define m_DSC_8K_FLUSH                                  ((0x1)<<2 )
//#define m_MIPI0_DSC_EN                                  ((0x1)<<3 )
//#define m_HDMI0_DSC_EN                                  ((0x1)<<4 )
//#define m_DSC1_PORT_SEL                                 ((0x1)<<16)
//#define m_DSC_4K_SLICE_CLK_SEL                          ((0x1)<<17)
//#define m_DSC_4K_FLUSH                                  ((0x1)<<18)
//#define m_MIPI1_DSC_EN                                  ((0x1)<<19)
//#define m_HDMI1_DSC_EN                                  ((0x1)<<20)


//WB_CTRL0
#define v_WB_EN(x)                      			(((x)&0x1)<<0)
#define v_WB_FMT(x)                     			(((x)&0x7)<<1)
#define v_WB_DITHER_EN(x)               			(((x)&0x1)<<4)
#define v_WB_RGB2YUV_EN(x)              			(((x)&0x1)<<5)
#define v_WB_YUV2RGB_EN(x)                          (((x)&0x1)<<29)

#define v_WB_RGB2YUV_MODE(x)            			(((x)&0x1)<<6)
#define v_WB_XPSD_BIL_EN(x)             			(((x)&0x1)<<7)
#define v_WB_YTHROW_EN(x)               			(((x)&0x1)<<8)
#define v_WB_YTHROW_MODE(x)             			(((x)&0x1)<<9)
#define v_WB_LINE_WRITE_MODE(x)                     (((x)&0x1)<<10)

//#define v_WB_HANDSHAKE_MODE(x)          			(((x)&0x1)<<11)

#define v_WB_POST_EMPTY_STOP_EN(x)          	    (((x)&0x1)<<11)

#define v_WB_ONEFRAME_EN(x)          	    		(((x)&0x1)<<12)
#define v_WB_RB_SWAP_EN(x)          	    		(((x)&0x1)<<14)
#define v_WB_RG_SWAP_EN(x)          	    		(((x)&0x1)<<15)

#define v_WB_WIN_BYPASS(x)                			(((x)&0x1)<<16)
#define v_WB_DIS_STOP(x)                			(((x)&0x1)<<17)
#define v_WB_XGT2_EN(x)                 			(((x)&0x1)<<18)

#define v_WB_WID_YRGB(x)          		        	(((x)&0xf)<<20)
#define v_WB_WID_CBCR(x)          		        	(((x)&0xf)<<24)

#define v_WB_PORT_SEL(x)         			        (((x)&0x3)<<30)

#define m_WB_EN             						(0x1<<0)
#define m_WB_FMT            						(0x7<<1)
#define m_WB_DITHER_EN     							(0x1<<4)
#define m_WB_RGB2YUV_EN     						(0x1<<5)
#define m_WB_YUV2RGB_EN                             (0x1<<29)
#define m_WB_RGB2YUV_MODE   						(0x1<<6)
#define m_WB_XPSD_BIL_EN    						(0x1<<7)
#define m_WB_YTHROW_EN      						(0x1<<8)
#define m_WB_YTHROW_MODE    						(0x1<<9)
#define m_WB_LINE_WRITE_MODE                        (0x1<<10)
//#define m_WB_HANDSHAKE_MODE             			(0x1<<11)
#define m_WB_POST_EMPTY_STOP_EN          	        (0x1<<11)
#define m_WB_ONEFRAME_EN                			(0x1<<12)
#define m_WB_RB_SWAP_EN          	    		    (0x1<<14)
#define m_WB_RG_SWAP_EN          	    		    (0x1<<15)
#define m_WB_WIN_BYPASS                 			(0x1<<16)
#define m_WB_DIS_STOP                   			(0x1<<17)
#define m_WB_XGT2_EN                    			(0x1<<18)
#define m_WB_WID_YRGB                    			(0xf<<20)
#define m_WB_WID_CBCR                    			(0xf<<24)
#define m_WB_PORT_SEL            			        (0x3<<30)

//WB_CTRL1 0x0104
#define v_WB_FIFO_THOLD(x)         		         	(((x)&0x3ff)<<0)
#define v_WB_XPSD_BIL_FACTOR(x)         			(((x)&0x3fff)<<16)
#define m_WB_XPSD_BIL_FACTOR            			(0x3fff<<16)
#define m_WB_FIFO_THOLD            		        	(0x3ff<<0)

#define v_WB_MST(x)         			            (((x)&0xffffffff)<<0)
#define m_WB_MST            			            (0xffffffff<<0)

#define v_WB_VIR_STRIDE(x)         			        (((x)&0xfff)<<0)
#define v_WB_VIR_STRIDE_EN(x)         			    (((x)&0x1)<<15)
#define v_WB_ACT_WIDTH(x)         			        (((x)&0xfff)<<16)
#define m_WB_VIR_STRIDE            			        (0xfff<<0)
#define m_WB_VIR_STRIDE_EN            			    (0x1<<15)
#define m_WB_ACT_WIDTH            			        (0xfff<<16)

#define v_WB_TIMEOUT_CNT(x)         			    (((x)&0x7fffffff)<<0)
#define v_WB_TIMEOUT_EN(x)         			        (((x)&0x1)<<31)
#define m_WB_TIMEOUT_CNT            			    (0x7fffffff<<0)
#define m_WB_TIMEOUT_EN            			        (0x1<<31)

#define v_WB_WIN_EN(x)                      		(((x)&0x1)<<0)
#define v_WB_WIN_SEL(x)                      		(((x)&0x1)<<4)
#define v_WB_WIN_HEIGHT(x)                      	(((x)&0x1fff)<<16)

#define m_WB_WIN_EN             					(0x1<<0)
#define m_WB_WIN_SEL             					(0x1<<4)
#define m_WB_WIN_HEIGHT             				(0x1fff<<16)

//0x120/0x124/0x128/0x130
#define v_SW_WB_CSC_COE_LOW(x)                      (((x)&0xffff)<<0 )
#define v_SW_WB_CSC_COE_HIG(x)                      (((x)&0xffff)<<16)

#define m_SW_WB_CSC_COE_LOW                         (0xffff      <<0 )
#define m_SW_WB_CSC_COE_HIG                         (0xffff      <<16)

//0x134/0x138/0x13c
#define v_SW_WB_CSC_OFFSET(x)                       (((x)&0xffffffff)<<0 )
#define m_SW_WB_CSC_OFFSET                          (0xffffffff      <<0 )




#define v_AXI_PERF_WORK(x)         			(((x)&0x1)<<0)
#define v_AXI_PERF_CLR(x)         			(((x)&0x1)<<1)
#define v_AXI_CNT_TYPE(x)         			(((x)&0x1)<<2)
#define v_AXI_AR_CNT_ID_TYPE(x)         	(((x)&0x1)<<3)
#define v_AXI_AW_CNT_ID_TYPE(x)         	(((x)&0x1)<<4)
#define v_AXI_DDR_ALING_TYPE(x)         	(((x)&0x3)<<6)
#define v_AXI_RD_LATENCY_THR(x)         	(((x)&0xfff)<<8)
#define v_AXI_RD_LATENCY_ID(x)          	(((x)&0xf)<<20)
#define v_AXI_AR_COUNT_ID(x)              	(((x)&0xf)<<24)
#define v_AXI_AW_COUNT_ID(x)              	(((x)&0xf)<<28)

#define m_AXI_PERF_WORK            			(0x1<<0)
#define m_AXI_PERF_CLR            			(0x1<<1)
#define m_AXI_CNT_TYPE            			(0x1<<2)
#define m_AXI_AR_CNT_ID_TYPE           		(0x1<<3)
#define m_AXI_AW_CNT_ID_TYPE           		(0x1<<4)
#define m_AXI_DDR_ALING_TYPE        		(0x3<<6)
#define m_AXI_RD_LATENCY_THR   	    		(0xfff<<8)
#define m_AXI_RD_LATENCY_ID        			(0xf<<20)
#define m_AXI_AR_COUNT_ID        	    	(0xf<<24)
#define m_AXI_AW_COUNT_ID               	(0xf<<28)

#define v_INFACE_OUT_EN(x)                         	    	(((x)&0x1)<<0)
#define v_INFACE_PIX_CLK_EN(x)                         	    (((x)&0x1)<<1)
#define v_INFACE_PORT_SEL(x)                         	    (((x)&0x3)<<2)
#define v_INFACE_HSYNC_POL(x)                         	    (((x)&0x1)<<4)
#define v_INFACE_VSYNC_POL(x)                         	    (((x)&0x1)<<5)
#define v_INFACE_DEN_POL(x)                         	    (((x)&0x1)<<6)
#define v_INFACE_DCLK_POL(x)                         	    (((x)&0x1)<<7)
#define v_INFACE_SPLIT_EN(x)                         	    (((x)&0x1)<<8)
#define v_INFACE_DATA1_SEL(x)                         	    (((x)&0x1)<<9)
#define v_INFACE_R2Y_EN(x)                           	    (((x)&0x1)<<12)
#define v_INFACE_CSC_MODE(x)                           	    (((x)&0x7)<<13)
#define v_INFACE_YC_SWAP(x)                           	    (((x)&0x3)<<16)
#define v_INFACE_UV_SWAP(x)                           	    (((x)&0x3)<<17)
#define v_INFACE_PIX_CLK_SEL(x)                         	(((x)&0x1)<<20)
#define v_INFACE_DCLK_SEL(x)                         	    (((x)&0x1)<<21)
#define v_INFACE_LVDS_CHASEL(x)                             (((x)&0x1)<<12)
#define v_INFACE_LVDS_DUAL_SEL(x)                           (((x)&0x1)<<13)
#define v_INFACE_LVDS_DUAL_SWAP(x)                          (((x)&0x1)<<14)
#define v_INFACE_REGDONE_IMD(x)                         	(((x)&0x1)<<31)

#define v_MIPI_COMMAND_MODE(x)                              (((x)&0x1)<<11)

#define v_LVDS_DUAL_CHANNNEL_EN(x)                          (((x)&0x1)<<12)
#define v_LVDS_DUAL_CHANNNEL_MODE(x)                        (((x)&0x1)<<13)
#define v_LVDS_DUAL_CHANNNEL_SWAP(x)                        (((x)&0x1)<<14)

#define v_BT656_OUT_EN(x)                                   (((x)&0x1)<<12)
#define v_BT656_UV_SWAP(x)                                  (((x)&0x1)<<13)
#define v_BT656_YC_SWAP(x)                                  (((x)&0x1)<<14)
#define v_BT656_DCLK_POL(x)                                 (((x)&0x1)<<15)

#define v_BT1120_OUT_EN(x)                                  (((x)&0x1)<<16)
#define v_BT1120_UV_SWAP(x)                                 (((x)&0x1)<<17)
#define v_BT1120_YC_SWAP(x)                                 (((x)&0x1)<<18)
#define v_BT1120_DCLK_POL(x)                                (((x)&0x1)<<19)

#define m_INFACE_OUT_EN                         	(0x1<<0)
#define m_INFACE_PIX_CLK_EN                         (0x1<<1)
#define m_INFACE_PORT_SEL                         	(0x3<<2)
#define m_INFACE_HSYNC_POL                         	(0x1<<4)
#define m_INFACE_VSYNC_POL                         	(0x1<<5)
#define m_INFACE_DEN_POL                         	(0x1<<6)
#define m_INFACE_DCLK_POL                         	(0x1<<7)
#define m_INFACE_SPLIT_EN                         	(0x1<<8)
#define m_INFACE_DATA1_SEL                         	(0x1<<9)
#define m_INFACE_R2Y_EN                           	(0x1<<12)
#define m_INFACE_CSC_MODE                           (0x7<<13)
#define m_INFACE_YC_SWAP                            (0x1<<16)
#define m_INFACE_UV_SWAP                            (0x1<<17)
#define m_INFACE_PIX_CLK_SEL                        (0x1<<20)
#define m_INFACE_DCLK_SEL                           (0x1<<21)
#define m_INFACE_LVDS_CHASEL                        (0x1<<12)
#define m_INFACE_LVDS_DUAL_SEL                      (0x1<<13)
#define m_INFACE_LVDS_DUAL_SWAP                     (0x1<<14)
#define m_INFACE_REGDONE_IMD                        (0x1<<31)

#define m_MIPI_COMMAND_MODE                         (0x1<<11)

#define m_LVDS_DUAL_CHANNNEL_EN                     (0x1<<12)
#define m_LVDS_DUAL_CHANNNEL_MODE                   (0x1<<13)
#define m_LVDS_DUAL_CHANNNEL_SWAP                   (0x1<<14)

#define m_BT656_OUT_EN                              (0x1<<12)
#define m_BT656_UV_SWAP                             (0x1<<13)
#define m_BT656_YC_SWAP                             (0x1<<14)
#define m_BT656_DCLK_POL                            (0x1<<15)

#define m_BT1120_OUT_EN                             (0x1<<16)
#define m_BT1120_UV_SWAP                            (0x1<<17)
#define m_BT1120_YC_SWAP                            (0x1<<18)
#define m_BT1120_DCLK_POL                           (0x1<<19)

//0x01e0
#define v_SEC_DRM_EN(x)                                  (((x)&0x1)<<0)
#define v_SEC_WB_DIS(x)                                  (((x)&0x1)<<4)
#define v_SEC_RID_LOCK_EN(x)                             (((x)&0x1)<<5)
#define v_SEC_CLUSTER0_EN(x)                             (((x)&0x1)<<8)
#define v_SEC_CLUSTER1_EN(x)                             (((x)&0x1)<<9)
#define v_SEC_CLUSTER2_EN(x)                             (((x)&0x1)<<10)
#define v_SEC_CLUSTER3_EN(x)                             (((x)&0x1)<<11)
#define v_SEC_ESMART0_EN(x)                              (((x)&0x1)<<12)
#define v_SEC_ESMART1_EN(x)                              (((x)&0x1)<<13)
#define v_SEC_ESMART2_EN(x)                              (((x)&0x1)<<14)
#define v_SEC_ESMART3_EN(x)                              (((x)&0x1)<<15)
#define v_SEC_AXI0_RID0_PROT_EN(x)                       (((x)&0x1)<<16)
#define v_SEC_AXI0_RID1_PROT_EN(x)                       (((x)&0x1)<<17)
#define v_SEC_AXI0_RID2_PROT_EN(x)                       (((x)&0x1)<<18)
#define v_SEC_AXI0_RID3_PROT_EN(x)                       (((x)&0x1)<<19)
#define v_SEC_AXI1_RID0_PROT_EN(x)                       (((x)&0x1)<<20)
#define v_SEC_AXI1_RID1_PROT_EN(x)                       (((x)&0x1)<<21)
#define v_SEC_AXI1_RID2_PROT_EN(x)                       (((x)&0x1)<<22)
#define v_SEC_AXI1_RID3_PROT_EN(x)                       (((x)&0x1)<<23)

#define m_SEC_DRM_EN                             (0x1<<0)
#define m_SEC_WB_DIS                             (0x1<<4)
#define m_SEC_RID_LOCK_EN                        (0x1<<5)
#define m_SEC_CLUSTER0_EN                        (0x1<<8)
#define m_SEC_CLUSTER1_EN                        (0x1<<9)
#define m_SEC_CLUSTER2_EN                        (0x1<<10)
#define m_SEC_CLUSTER3_EN                        (0x1<<11)
#define m_SEC_ESMART0_EN                         (0x1<<12)
#define m_SEC_ESMART1_EN                         (0x1<<13)
#define m_SEC_ESMART2_EN                         (0x1<<14)
#define m_SEC_ESMART3_EN                         (0x1<<15)
#define m_SEC_AXI0_RID0_PROT_EN                  (0x1<<16)
#define m_SEC_AXI0_RID1_PROT_EN                  (0x1<<17)
#define m_SEC_AXI0_RID2_PROT_EN                  (0x1<<18)
#define m_SEC_AXI0_RID3_PROT_EN                  (0x1<<19)
#define m_SEC_AXI1_RID0_PROT_EN                  (0x1<<20)
#define m_SEC_AXI1_RID1_PROT_EN                  (0x1<<21)
#define m_SEC_AXI1_RID2_PROT_EN                  (0x1<<22)
#define m_SEC_AXI1_RID3_PROT_EN                  (0x1<<23)

//0x01e4
#define v_SEC_CLUSTER0_PORT_SEL(x)                             (((x)&0x3)<<0)
#define v_SEC_CLUSTER1_PORT_SEL(x)                             (((x)&0x3)<<4)
#define v_SEC_CLUSTER2_PORT_SEL(x)                             (((x)&0x3)<<8)
#define v_SEC_CLUSTER3_PORT_SEL(x)                             (((x)&0x3)<<12)
#define v_SEC_ESMART0_PORT_SEL(x)                              (((x)&0x3)<<16)
#define v_SEC_ESMART1_PORT_SEL(x)                              (((x)&0x3)<<20)
#define v_SEC_ESMART2_PORT_SEL(x)                              (((x)&0x3)<<24)
#define v_SEC_ESMART3_PORT_SEL(x)                              (((x)&0x3)<<28)

#define m_SEC_CLUSTER0_PORT_SEL                        (0x3<<0)
#define m_SEC_CLUSTER1_PORT_SEL                        (0x3<<4)
#define m_SEC_CLUSTER2_PORT_SEL                        (0x3<<8)
#define m_SEC_CLUSTER3_PORT_SEL                        (0x3<<12)
#define m_SEC_ESMART0_PORT_SEL                        (0x3<<16)
#define m_SEC_ESMART1_PORT_SEL                        (0x3<<20)
#define m_SEC_ESMART2_PORT_SEL                        (0x3<<24)
#define m_SEC_ESMART3_PORT_SEL                        (0x3<<28)

//0x01e8/0x1ec/0x1f0
#define v_SEC_LAYER0_SEL_EN(x)                          (((x)&0x1)<<3)
#define v_SEC_LAYER1_SEL_EN(x)                          (((x)&0x1)<<7)
#define v_SEC_LAYER2_SEL_EN(x)                          (((x)&0x1)<<11)
#define v_SEC_LAYER3_SEL_EN(x)                          (((x)&0x1)<<15)
#define v_SEC_LAYER0_SEL(x)                             (((x)&0x7)<<0)
#define v_SEC_LAYER1_SEL(x)                             (((x)&0x7)<<4)
#define v_SEC_LAYER2_SEL(x)                             (((x)&0x7)<<8)
#define v_SEC_LAYER3_SEL(x)                             (((x)&0x7)<<12)

#define m_SEC_LAYER0_SEL_EN                     (0x1<<3)
#define m_SEC_LAYER1_SEL_EN                     (0x1<<7)
#define m_SEC_LAYER2_SEL_EN                     (0x1<<11)
#define m_SEC_LAYER3_SEL_EN                     (0x1<<15)
#define m_SEC_LAYER0_SEL                        (0x7<<0)
#define m_SEC_LAYER1_SEL                        (0x7<<4)
#define m_SEC_LAYER2_SEL                        (0x7<<8)
#define m_SEC_LAYER3_SEL                        (0x7<<12)

//0x01f8
#define v_SEC_AXI0_RID0_PROT(x)                       (((x)&0xf)<<0)
#define v_SEC_AXI0_RID1_PROT(x)                       (((x)&0xf)<<4)
#define v_SEC_AXI0_RID2_PROT(x)                       (((x)&0xf)<<8)
#define v_SEC_AXI0_RID3_PROT(x)                       (((x)&0xf)<<12)
#define v_SEC_AXI1_RID0_PROT(x)                       (((x)&0xf)<<16)
#define v_SEC_AXI1_RID1_PROT(x)                       (((x)&0xf)<<20)
#define v_SEC_AXI1_RID2_PROT(x)                       (((x)&0xf)<<24)
#define v_SEC_AXI1_RID3_PROT(x)                       (((x)&0xf)<<28)

#define m_SEC_AXI0_RID0_PROT                  (0xf<<0)
#define m_SEC_AXI0_RID1_PROT                  (0xf<<4)
#define m_SEC_AXI0_RID2_PROT                  (0xf<<8)
#define m_SEC_AXI0_RID3_PROT                  (0xf<<12)
#define m_SEC_AXI1_RID0_PROT                  (0xf<<16)
#define m_SEC_AXI1_RID1_PROT                  (0xf<<20)
#define m_SEC_AXI1_RID2_PROT                  (0xf<<24)
#define m_SEC_AXI1_RID3_PROT                  (0xf<<28)


//#define v_HDMI0_SPLIT_EN(x)         			(((x)&0x1)<<0)
//#define v_HDMI0_DATA1_SEL(x)         			(((x)&0x1)<<1)
//#define v_EDP0_SPLIT_EN(x)         		    	(((x)&0x1)<<4)
//#define v_EDP0_DATA1_SEL(x)         			(((x)&0x1)<<5)
//#define v_DP0_SPLIT_EN(x)         			    (((x)&0x1)<<8)
//#define v_DP0_DATA1_SEL(x)         			    (((x)&0x1)<<9)
//#define v_MIPI0_SPLIT_EN(x)         			(((x)&0x1)<<12)
//#define v_MIPI0_DATA1_SEL(x)         			(((x)&0x1)<<13)
//#define v_RGB_SPLIT_EN(x)         		     	(((x)&0x1)<<16)
//#define v_RGB_DATA1_SEL(x)         		    	(((x)&0x1)<<17)
//
//#define m_HDMI0_SPLIT_EN            			(0x1<<0)
//#define m_HDMI0_DATA1_SEL           			(0x1<<1)
//#define m_EDP0_SPLIT_EN            			(0x1<<4)
//#define m_EDP0_DATA1_SEL           			(0x1<<5)
//#define m_DP0_SPLIT_EN            			(0x1<<8)
//#define m_DP0_DATA1_SEL           			(0x1<<9)
//#define m_MIPI0_SPLIT_EN            			(0x1<<12)
//#define m_MIPI0_DATA1_SEL           			(0x1<<13)
//#define m_RGB_SPLIT_EN            			(0x1<<16)
//#define m_RGB_DATA1_SEL           			(0x1<<17)
//CLUSTER_CTRL0
#define		CLUSTER_WIN0_BASE                0x0000
#define		CLUSTER_WIN1_BASE                0x0080

#define v_CLUSTER_WIN_CONTRAST_CSC_MODE(x)				(((x)&0x3)<<27)
#define v_CLUSTER_WIN_CONTRAST_CSC_EN(x)                (((x)&0x1)<<26)
//#define v_CLUSTER_WIN_CONTRAST_EN(x)                    (((x)&0x1)<<25)
//#define v_CLUSTER_WIN_HG_EN(x)                    		(((x)&0x1)<<24)
#define v_CLUSTER_WIN_RG_SWAP(x)                        (((x)&0x1)<<25)
#define v_CLUSTER_WIN_CSC_YUV2RGB_FORCE(x)              (((x)&0x1)<<24)
#define v_CLUSTER_WIN_LG_EN(x)                    		(((x)&0x1)<<23)
#define v_CLUSTER_WIN_FEED_BACK_EN(x)             		(((x)&0x1)<<22)
#define v_CLUSTER_WIN_Y_MIR_EN(x)                 		(((x)&0x1)<<21)
//#define v_CLUSTER_WIN_X_MIR_EN(x)                 		(((x)&0x1)<<20)
#define v_CLUSTER_WIN_YUV_CLIP(x)                 		(((x)&0x1)<<19)
#define v_CLUSTER_WIN_DITHER_UP_EN(x)             		(((x)&0x1)<<18)
#define v_CLUSTER_WIN_UV_SWAP(x)                  		(((x)&0x1)<<17)
#define v_CLUSTER_WIN_MID_SWAP(x)                 		(((x)&0x1)<<16)
#define v_CLUSTER_WIN_ALPHA_SWAP(x)               		(((x)&0x1)<<15)
#define v_CLUSTER_WIN_RB_SWAP(x)                  		(((x)&0x1)<<14)
#define v_CLUSTER_WIN_CSC_MODE(x)                    	(((x)&0x7)<<10)
#define v_CLUSTER_WIN_CSC_R2Y_EN(x)               		(((x)&0x1)<<9)
#define v_CLUSTER_WIN_CSC_Y2R_EN(x)               		(((x)&0x1)<<8)
#define v_CLUSTER_WIN_TILE4X4_GA(x)           		    (((x)&0x1)<<7)
//#define v_CLUSTER_WIN_TILE_MODE(x)                      (((x)&0x1)<<6)
#define v_CLUSTER_WIN_DATA_FMT(x)                 		(((x)&0x3f)<<1)
#define v_CLUSTER_WIN_EN(x)                       		(((x)&0x1)<<0)

#define m_CLUSTER_WIN_CONTRAST_CSC_MODE 				(0x3<<27)
#define m_CLUSTER_WIN_CONTRAST_CSC_EN					(0x1<<26)
//#define m_CLUSTER_WIN_CONTRAST_EN						(0x1<<25)
//#define m_CLUSTER_WIN_HG_EN                     		(0x1<<24)
#define m_CLUSTER_WIN_RG_SWAP                           (0x1<<25)
#define m_CLUSTER_WIN_CSC_YUV2RGB_FORCE                 (0x1<<24)
#define m_CLUSTER_WIN_LG_EN                     		(0x1<<23)
#define m_CLUSTER_WIN_FEED_BACK_EN              		(0x1<<22)
#define m_CLUSTER_WIN_Y_MIR_EN                  		(0x1<<21)
#define m_CLUSTER_WIN_X_MIR_EN                  		(0x1<<20)
#define m_CLUSTER_WIN_YUV_CLIP                  		(0x1<<19)
#define m_CLUSTER_WIN_DITHER_UP_EN              		(0x1<<18)
#define m_CLUSTER_WIN_UV_SWAP                   		(0x1<<17)
#define m_CLUSTER_WIN_MID_SWAP                  		(0x1<<16)
#define m_CLUSTER_WIN_ALPHA_SWAP                		(0x1<<15)
#define m_CLUSTER_WIN_RB_SWAP                   		(0x1<<14)
#define m_CLUSTER_WIN_CSC_MODE                      	(0x7<<10)
#define m_CLUSTER_WIN_CSC_R2Y_EN                		(0x1<<9)
#define m_CLUSTER_WIN_CSC_Y2R_EN                		(0x1<<8)
#define m_CLUSTER_WIN_TILE4X4_GA           		        (0x1<<7)
#define m_CLUSTER_WIN_TILE_MODE                         (0x1<<6)
#define m_CLUSTER_WIN_DATA_FMT                  		(0x3f<<1)
#define m_CLUSTER_WIN_EN                        		(0x1<<0)

//CLUSTER_CTRL1
#define v_CLUSTER_WIN_GT4_CBCR(x)                       (((x)&0x1)<<31)
#define v_CLUSTER_WIN_GT2_CBCR(x)                       (((x)&0x1)<<30)
#define v_CLUSTER_WIN_GT4_YRGB(x)                       (((x)&0x1)<<29)
#define v_CLUSTER_WIN_GT2_YRGB(x)                       (((x)&0x1)<<28)
#define v_CLUSTER_WIN_XAVG_EN(x)                        (((x)&0x1)<<27)
#define v_CLUSTER_WIN_XGT_MODE(x)                       (((x)&0x3)<<25)
#define v_CLUSTER_WIN_XGT_EN(x)                         (((x)&0x1)<<24)
#define v_CLUSTER_WIN_XSD_EN(x)                         (((x)&0x1)<<23)
#define v_CLUSTER_WIN_XSU_EN(x)                         (((x)&0x1)<<22)
#define v_CLUSTER_WIN_XRGB_HOR_SCL_MODE(x)              (((x)&0x3)<<20)
#define v_CLUSTER_WIN_VSD_AVG4(x)                       (((x)&0x1)<<19)
#define v_CLUSTER_WIN_VSD_AVG2(x)                       (((x)&0x1)<<18)
#define v_CLUSTER_WIN_YSD_EN(x)                         (((x)&0x1)<<15)
#define v_CLUSTER_WIN_YSU_EN(x)                         (((x)&0x1)<<14)
#define v_CLUSTER_WIN_YRGB_HOR_SCL_MODE(x)              (((x)&0x3)<<12)
#define v_CLUSTER_WIN_CBR_AXI_GATHER_NUM(x)      		(((x)&0xf)<<8)
#define v_CLUSTER_WIN_YRGB_AXI_GATHER_NUM(x)     		(((x)&0xf)<<4)
#define v_CLUSTER_WIN_BIC_COE_SEL(x)             		(((x)&0x3)<<2)
#define v_CLUSTER_WIN_CBR_AXI_GATHER_EN(x)       		(((x)&0x1)<<1)
#define v_CLUSTER_WIN_YRGB_AXI_GATHER_EN(x)      		(((x)&0x1)<<0)

#define m_CLUSTER_WIN_GT4_CBCR                          (0x1<<31)
#define m_CLUSTER_WIN_GT2_CBCR                          (0x1<<30)
#define m_CLUSTER_WIN_GT4_YRGB                          (0x1<<29)
#define m_CLUSTER_WIN_GT2_YRGB                          (0x1<<28)
#define m_CLUSTER_WIN_XAVG_EN                           (0x1<<27)
#define m_CLUSTER_WIN_XGT_MODE                          (0x3<<25)
#define m_CLUSTER_WIN_XGT_EN                            (0x1<<24)
#define m_CLUSTER_WIN_XSD_EN                            (0x1<<23)
#define m_CLUSTER_WIN_XSU_EN                            (0x1<<22)
#define m_CLUSTER_WIN_XRGB_HOR_SCL_MODE                 (0x3<<20)
#define m_CLUSTER_WIN_VSD_AVG4                          (0x1<<19)
#define m_CLUSTER_WIN_VSD_AVG2                          (0x1<<18)
#define m_CLUSTER_WIN_YSD_EN                            (0x1<<15)
#define m_CLUSTER_WIN_YSU_EN                            (0x1<<14)
#define m_CLUSTER_WIN_YRGB_HOR_SCL_MODE                 (0x3<<12)

#define m_CLUSTER_WIN_CBR_AXI_GATHER_NUM      		    (0xf<<8)
#define m_CLUSTER_WIN_YRGB_AXI_GATHER_NUM     		    (0xf<<4)
#define m_CLUSTER_WIN_BIC_COE_SEL             		    (0x3<<2)
#define m_CLUSTER_WIN_CBR_AXI_GATHER_EN       		    (0x1<<1)
#define m_CLUSTER_WIN_YRGB_AXI_GATHER_EN      		    (0x1<<0)



//CLUSTER_CTRL2
#define m_CLUSTER_WIN_DMA_BURST_LENGTH					(0x3<<20)
#define m_CLUSTER_WIN_DMA_ARBITER_THRESHOLD			    (0x7<<17)
#define m_CLUSTER_WIN_DMA_ARBITER_PRIORITY_EN			(0x1<<16)
#define m_CLUSTER_WIN_AXI_OUTSTANDING_MAX_NUM			(0x1f<<11)
#define m_CLUSTER_WIN_AXI_MAX_OUTSTANDING_EN			(0x1<<10)
#define m_CLUSTER_WIN_RID_CBR							(0x1f<<5)
#define m_CLUSTER_WIN_RID_YRGB							(0x1f<<0)

#define v_CLUSTER_WIN_DMA_BURST_LENGTH(x)				(((x)&0x3)<<20)
#define v_CLUSTER_WIN_DMA_ARBITER_THRESHOLD(x)			(((x)&0x7)<<17)
#define v_CLUSTER_WIN_DMA_ARBITER_PRIORITY_EN(x)		(((x)&0x1)<<16)
#define v_CLUSTER_WIN_AXI_OUTSTANDING_MAX_NUM(x)		(((x)&0x1f)<<11)
#define v_CLUSTER_WIN_AXI_MAX_OUTSTANDING_EN(x)		    (((x)&0x1)<<10)
#define v_CLUSTER_WIN_RID_CBR(x)						(((x)&0x1f)<<5)
#define v_CLUSTER_WIN_RID_YRGB(x)						(((x)&0x1f)<<0)

//CLUSTER_YRGB_MST
//CLUSTER_CBR_MST
#define v_CLUSTER_WIN_MST(x)					    (((x)&0xffffffff)<<0)
#define m_CLUSTER_WIN_MST							(0xffffffff<<0)

//CLUSTER_VIR
#define v_CLUSTER_WIN_VIR_STRIDE(x)        			(((x)&0xffff)<<0)
#define v_CLUSTER_WIN_VIR_STRIDE_UV(x)       		(((x)&0xffff)<<16)

#define m_CLUSTER_WIN_VIR_STRIDE	    			(0xffff<<0)
#define m_CLUSTER_WIN_VIR_STRIDE_UV        			(0xffff<<16)

//CLUSTER_COLOR_KEY
#define v_CLUSTER_WIN_COLOR_KEY_RY(x)					(((x)&0x3ff)<<20)
#define v_CLUSTER_WIN_COLOR_KEY_GU(x)					(((x)&0x3ff)<<10)
#define v_CLUSTER_WIN_COLOR_KEY_BV(x)					(((x)&0x3ff)<<0)
#define v_CLUSTER_WIN_COLOR_KEY_EN(x)       		    (((x)&1)<<31)

#define m_CLUSTER_WIN_COLOR_KEY_RY					(0x3ff<<20)
#define m_CLUSTER_WIN_COLOR_KEY_GU					(0x3ff<<10)
#define m_CLUSTER_WIN_COLOR_KEY_BV					(0x3ff<<0)
#define m_CLUSTER_WIN_COLOR_KEY_EN					((u32)1<<31)

//CLUSTER_ACT_INFO
#define v_CLUSTER_WIN_ACT_WIDTH(x)        			(((x)&0x1fff)<<0)
#define v_CLUSTER_WIN_ACT_HEIGHT(x)       		 	(((x)&0x1fff)<<16)
#define m_CLUSTER_WIN_ACT_WIDTH         			(0x1fff<<0)
#define m_CLUSTER_WIN_ACT_HEIGHT         			(0x1fff<<16)

//CLUSTER_DSP_INFO
#define v_CLUSTER_WIN_DSP_WIDTH(x)        			(((x)&0x1fff)<<0)
#define v_CLUSTER_WIN_DSP_HEIGHT(x)       			(((x)&0x1fff)<<16)
#define m_CLUSTER_WIN_DSP_WIDTH         			(0x1fff<<0)
#define m_CLUSTER_WIN_DSP_HEIGHT         			(0x1fff<<16)

//CLUSTER_DSP_ST
#define v_CLUSTER_WIN_DSP_XST(x)         			(((x)&0x1fff)<<0)
#define v_CLUSTER_WIN_DSP_YST(x)        			(((x)&0x1fff)<<16)
#define m_CLUSTER_WIN_DSP_XST             			(0x1fff<<0)
#define m_CLUSTER_WIN_DSP_YST             			(0x1fff<<16)

//CLUSTER_DSP_BG
#define v_CLUSTER_WIN_DSP_BG_EN(x)        				(((x)&0x0001)<<31)
#define v_CLUSTER_WIN_DSP_BG_RED(x)       				(((x)&0x03ff)<<20)
#define v_CLUSTER_WIN_DSP_BG_GREEN(x)        			(((x)&0x03ff)<<10)
#define v_CLUSTER_WIN_DSP_BG_BLUE(x)        			(((x)&0x03ff)<<0)

#define m_CLUSTER_WIN_DSP_BG_EN         				(0x0001<<31)
#define m_CLUSTER_WIN_DSP_BG_RED       				    (0x03ff<<20)
#define m_CLUSTER_WIN_DSP_BG_GREEN        			    (0x03ff<<10)
#define m_CLUSTER_WIN_DSP_BG_BLUE        			    (0x03ff<<0)

//CLUSTER_SCL_FACTOR_YRGB
#define v_CLUSTER_WIN_HS_FACTOR_YRGB(x)    		    	(((x)&0xffff)<<0)
#define v_CLUSTER_WIN_VS_FACTOR_YRGB(x)    		    	(((x)&0xffff)<<16)
#define m_CLUSTER_WIN_HS_FACTOR_YRGB	    			(0xffff<<0)
#define m_CLUSTER_WIN_VS_FACTOR_YRGB	    			(0xffff<<16)

//CLUSTER_SCL_FACTOR_CBR
#define v_CLUSTER_WIN_HS_FACTOR_CBR(x)        			(((x)&0xffff)<<0)
#define v_CLUSTER_WIN_VS_FACTOR_CBR(x)        			(((x)&0xffff)<<16)
#define m_CLUSTER_WIN_HS_FACTOR_CBR	    			    (0xffff<<0)
#define m_CLUSTER_WIN_VS_FACTOR_CBR	    			    (0xffff<<16)

//CLUSTER_SCL_OFFSET
#define v_CLUSTER_WIN_HS_OFFSET_YRGB(x)   				(((x)&0xff)<<0)
#define v_CLUSTER_WIN_HS_OFFSET_CBR(x)       			(((x)&0xff)<<8)
#define v_CLUSTER_WIN_VS_OFFSET_YRGB(x)    			    (((x)&0xff)<<16)
#define v_CLUSTER_WIN_VS_OFFSET_CBR(x)        			(((x)&0xff)<<24)

#define m_CLUSTER_WIN_HS_OFFSET_YRGB	    			(0xff<<0)
#define m_CLUSTER_WIN_HS_OFFSET_CBR	    		    	(0xff<<8)
#define m_CLUSTER_WIN_VS_OFFSET_YRGB	    			(0xff<<16)
#define m_CLUSTER_WIN_VS_OFFSET_CBR	    			    (0xff<<24)

//CLUSTER_TRANSFORMED_OFFSET
#define v_CLUSTER_WIN_TRANSFORMED_YOFFSET(x)        (((x)&0xf)<<16)
#define v_CLUSTER_WIN_TRANSFORMED_XOFFSET(x)        (((x)&0x3f)<<0)

#define m_CLUSTER_WIN_TRANSFORMED_YOFFSET	    		(0xf<<16)
#define m_CLUSTER_WIN_TRANSFORMED_XOFFSET	    		(0x3f<<0)

//CLUSTER_FADING_CTRL
#define v_CLUSTER_WIN_FADING_EN(x)        	 			(((x)&0x1)<<31)
#define v_CLUSTER_WIN_FADING_OFFSET_R(x)    			(((x)&0x03ff)<<0)
#define v_CLUSTER_WIN_FADING_OFFSET_G(x)    			(((x)&0x03ff)<<10)
#define v_CLUSTER_WIN_FADING_OFFSET_B(x)    			(((x)&0x03ff)<<20)

#define m_CLUSTER_WIN_FADING_EN						    (0x1<<31)
#define m_CLUSTER_WIN_FADING_OFFSET_R       			(0x03ff<<0)
#define m_CLUSTER_WIN_FADING_OFFSET_G       			(0x03ff<<10)
#define m_CLUSTER_WIN_FADING_OFFSET_B       			(0x03ff<<20)

//CLUSTER_FADING_VAL
#define v_CLUSTER_WIN_FADING_VALUE(x)       			(((x)&0x3ff)<<0)
#define m_CLUSTER_WIN_FADING_VALUE	    				(0x3ff<<0)

//CLUSTER_AFBCD_GATING_EN
#define v_CLUSTER_WIN_AFBCD_GATING_EN(x)			(((x)&0x1) << 4)
#define m_CLUSTER_WIN_AFBCD_GATING_EN				(0x1 << 4)

//CLUSTER_AFBCD_MASK_EN
#define v_CLUSTER_WIN_AFBCD_OUTPUT_MASK_EN(x)			(((x)&0x1) << 0)
#define m_CLUSTER_WIN_AFBCD_OUTPUT_MASK_EN				(0x1 << 0)

//CLUSTER_WATER_LINE_LEVEL
#define v_CLUSTER_WATER_LINE_LEVEL(x)			         (((x)&0x7) << 5)
#define m_CLUSTER_WATER_LINE_LEVEL      			 (0x7 << 5)

//CLUSTER_WATER_LINE_EN
#define v_CLUSTER_WATER_LINE_EN(x)			         (((x)&0x1) << 8)
#define m_CLUSTER_WATER_LINE_EN      		        	 (0x1 << 8)

//CLUSTER_WATER_LINE_MODE
#define v_CLUSTER_WATER_LINE_MODE(x)			         (((x)&0x1) << 9)
#define m_CLUSTER_WATER_LINE_MODE      		        	 (0x1 << 9)

//CLUSTER_WIN0_WATER_LINE_MODE
#define v_CLUSTER_WATER_LINE_NUM(x)			         (((x)&0x3ff) << 16)
#define m_CLUSTER_WATER_LINE_NUM      		       	         (0x3ff << 16)


//CLUSTER_AFBCD_MODE
#define v_CLUSTER_WIN_YMIR_EN(x)                       (((x)&0x1) << 3 )
#define v_CLUSTER_WIN_XMIR_EN(x)                       (((x)&0x1) << 2 )
#define v_CLUSTER_WIN_ROT270_EN(x)                     (((x)&0x1) << 1 )
#define v_CLUSTER_WIN_ROT90_EN(x)                      (((x)&0x1) << 0 )

#define m_CLUSTER_WIN_YMIR_EN                          (0x1 << 3 )
#define m_CLUSTER_WIN_XMIR_EN                          (0x1 << 2 )
#define m_CLUSTER_WIN_ROT270_EN                        (0x1 << 1 )
#define m_CLUSTER_WIN_ROT90_EN                         (0x1 << 0 )

//CLUSTER_AFBCD_HDR_PTR
#define v_CLUSTER_WIN_AFBCD_HDR_PTR(x)				  (((x)&0xffffffff)<< 0 )
#define m_CLUSTER_WIN_AFBCD_HDR_PTR					  (0xffffffff	   << 0 )

//CLUSTER_AFBCD_VIR_WIDTH
#define v_CLUSTER_WIN_AFBCD_TAIL_NUM(x)				   (((x) & 0xffff) << 16)
#define v_CLUSTER_WIN_AFBCD_PIC_VIR_WIDTH(x)           (((x) & 0xffff) << 0 )

#define m_CLUSTER_WIN_AFBCD_TAIL_NUM                   (0xffff  << 16 )
#define m_CLUSTER_WIN_AFBCD_PIC_VIR_WIDTH              (0xffff  << 0  )

//CLUSTER_AFBCD_SIZE
#define v_CLUSTER_WIN_AFBCD_PIC_HEIGHT(x)              (((x) & 0xffff) << 16 )
#define v_CLUSTER_WIN_AFBCD_PIC_WIDTH(x)               (((x) & 0xffff) <<  0 )

#define m_CLUSTER_WIN_AFBCD_PIC_HEIGHT                 (0xffff  << 16 )
#define m_CLUSTER_WIN_AFBCD_PIC_WIDTH                  (0xffff  <<  0 )

//CLUSTER_AFBCD_PIC_OFFSET
#define v_CLUSTER_WIN_AFBCD_PIC_XOFFSET(x)             (((x)&0xffff) <<  0 )
#define v_CLUSTER_WIN_AFBCD_PIC_YOFFSET(x)             (((x)&0xffff) << 16 )

#define m_CLUSTER_WIN_AFBCD_PIC_XOFFSET                (0xffff  <<  0 )
#define m_CLUSTER_WIN_AFBCD_PIC_YOFFSET                (0xffff  << 16 )

//CLUSTER_AFBCD_DIS_OFFSET
#define v_CLUSTER_WIN_AFBCD_DIS_XOFFSET(x)             (((x)&0xffff) <<  0 )
#define v_CLUSTER_WIN_AFBCD_DIS_YOFFSET(x)             (((x)&0xffff) << 16 )

#define m_CLUSTER_WIN_AFBCD_DIS_XOFFSET                (0xffff  <<  0 )
#define m_CLUSTER_WIN_AFBCD_DIS_YOFFSET                (0xffff  << 16 )

//CLUSTER_AFBCD_CTRL
#define v_CLUSTER_WIN_AFBCD_COMPRESS_MODE(x)           (((x)&0xf) << 20)
#define v_CLUSTER_WIN_AFBCD_PLD_RANGE_EN(x)            (((x)&0x1) << 17)
#define v_CLUSTER_WIN_AFBCD_PLD_OFFSET_EN(x)           (((x)&0x1) << 16)
#define v_CLUSTER_WIN_AFBCD_BG_SWAP_EN(x)              (((x)&0x1) << 12)
#define v_CLUSTER_WIN_AFBCD_ALPHA_SWAP_EN(x)           (((x)&0x1) << 11)
#define v_CLUSTER_WIN_AFBCD_UV_SWAP_EN(x)              (((x)&0x1) << 10)
#define v_CLUSTER_WIN_AFBCD_RB_SWAP_EN(x)              (((x)&0x1) << 9)
#define v_CLUSTER_WIN_AFBCD_BLOCK_SPLIT(x)             (((x)&0x1) << 8)
#define v_CLUSTER_WIN_AFBCD_HALF_BLOCK(x)              (((x)&0x1) << 7)
//#define v_CLUSTER_WIN_AFBCD_COLOR_TRANSFORM(x)         (((x)&0x1) << 6)
#define v_CLUSTER_WIN_AFBCD_PIXEL_PACKING_FMT(x)       (((x)&0x1f) << 2)
#define v_CLUSTER_WIN_AFBCD_VIDEO_TOP_CROP(x)          (((x)&0x3) << 0)

#define m_CLUSTER_WIN_AFBCD_COMPRESS_MODE              (0xf << 20 )
#define m_CLUSTER_WIN_AFBCD_PLD_RANGE_EN               (0x1 << 17 )
#define m_CLUSTER_WIN_AFBCD_PLD_OFFSET_EN              (0x1 << 16 )
#define m_CLUSTER_WIN_AFBCD_BG_SWAP_EN                 (0x1 << 12 )
#define m_CLUSTER_WIN_AFBCD_ALPHA_SWAP_EN              (0x1 << 11 )
#define m_CLUSTER_WIN_AFBCD_UV_SWAP_EN                 (0x1 << 10 )
#define m_CLUSTER_WIN_AFBCD_RB_SWAP_EN                 (0x1 << 9 )
#define m_CLUSTER_WIN_AFBCD_BLOCK_SPLIT                (0x1 << 8 )
#define m_CLUSTER_WIN_AFBCD_HALF_BLOCK                 (0x1 << 7 )
//#define m_CLUSTER_WIN_AFBCD_COLOR_TRANSFORM            (0x1 << 6 )
#define m_CLUSTER_WIN_AFBCD_PIXEL_PACKING_FMT          (0x1f << 2 )
#define m_CLUSTER_WIN_AFBCD_VIDEO_TOP_CROP             (0x3 << 0 )

#define v_CLUSTER_FRM_RESETN_EN(x)                          (((x) & 0x1) << 31 )
#define v_CLUSTER_PRIORITY_EN(x)                            (((x) & 0x1) << 29 )
#define v_CLUSTER_OVERLAP_EN(x)                             (((x) & 0x1) << 28 )
#define v_CLUSTER_PLD_PRIORITY_EN(x)                        (((x) & 0x1) << 27 )
#define v_CLUSTER_AFBCD_PRIORITY_MODE(x)                    (((x) & 0x1) << 21 )
#define v_CLUSTER_HURRY_THOLD(x)                            (((x) & 0x3) << 17 )
#define v_CLUSTER_HURRY_EN(x)                               (((x) & 0x1) << 16 )
#define v_CLUSTER_MMU_BYPASS(x)                             (((x) & 0x1) << 14 )
#define v_CLUSTER_AXI_SEL(x)                                (((x) & 0x1) << 13 )
#define v_CLUSTER_DMA_STOP(x)                               (((x) & 0x1) << 12 )
//#define v_CLUSTER_FILTER_ONLY_ONE_GAUSS(x)                  (((x) & 0x3) << 10 )
//#define v_CLUSTER_FILTER_EN(x)                              (((x) & 0x3) << 8 )
#define v_CLUSTER_SCL_LB_MODE(x)                            (((x) & 0x3)  << 9 ) //@brh add 2021/9/24
#define v_CLUSTER_8K_EN(x)                                  (((x) & 0x1)  << 8 ) //@brh add 2021/9/24
//#define v_CLUSTER_LB_SHARE_MODE(x)                          (((x) & 0x1)  << 7 ) //@brh add 2021/9/24
#define v_CLUSTER_LB_MODE(x)                          		(((x) & 0xf)  << 4 ) //@brh add 2021/9/24

#define v_CLUSTER_LB_MODE(x)                       			(((x) & 0xf) << 4 )
#define v_CLUSTER_WIN1_EN_STATUS(x)                			(((x) & 0x1) << 3 )
#define v_CLUSTER_WIN0_EN_STATUS(x)                			(((x) & 0x1) << 2 )
#define v_CLUSTER_AFBCD_EN(x)                      			(((x) & 0x1) << 1 )
#define v_CLUSTER_EN(x)                            			(((x) & 0x1) << 0 )

#define m_CLUSTER_FRM_RESETN_EN                             (0x1  << 31 )
#define m_CLUSTER_PRIORITY_EN                               (0x1  << 29 )
#define m_CLUSTER_OVERLAP_EN                                (0x1  << 28 )
#define m_CLUSTER_PLD_PRIORITY_EN                           (0x1  << 27 )
#define m_CLUSTER_AFBCD_PRIORITY_MODE                       (0x1  << 21 )
#define m_CLUSTER_HURRY_THOLD                               (0x3  << 17 )
#define m_CLUSTER_HURRY_EN                                  (0x1  << 16 )
#define m_CLUSTER_MMU_BYPASS                                (0x1  << 14 )
#define m_CLUSTER_AXI_SEL                                   (0x1  << 13 )
#define m_CLUSTER_DMA_STOP                                  (0x1  << 12 )
//#define m_CLUSTER_FILTER_ONLY_ONE_GAUSS                     (0x3  << 10 )
//#define m_CLUSTER_FILTER_EN                                 (0x3  << 8 )
#define m_CLUSTER_SCL_LB_MODE                               (0x3  << 9 ) //@brh add 2021/9/24
#define m_CLUSTER_8K_EN                                     (0x1  << 8 ) //@brh add 2021/9/24
//#define m_CLUSTER_LB_SHARE_MODE                             (x1  << 7 ) //@brh add 2021/9/24
#define m_CLUSTER_LB_MODE                          			(0xf  << 4 ) //@brh add 2021/9/24

#define m_CLUSTER_WIN1_EN_STATUS                  			(0x1  << 3 )
#define m_CLUSTER_WIN0_EN_STATUS                  			(0x1  << 2 )
#define m_CLUSTER_AFBCD_EN                         			(0x1  << 1 )
#define m_CLUSTER_EN                               			(0x1  << 0 )

//DCI
#define v_CLUSTER_BLK_SIZE_H(x)        ( (x&0x1ff)    << 0 )
#define v_CLUSTER_BLK_SIZE_V(x)        ( (x&0x1ff)    << 16 )
#define v_CLUSTER_BLK_OFFSET_H(x)      ( (x&0x1ff)    << 0 )
#define v_CLUSTER_BLK_OFFSET_V(x)      ( (x&0x1ff)    << 16 )
#define v_CLUSTER_BLK_SIZE_FIX(x)      ( (x&0xfffff)  << 0 )
#define v_CLUSTER_PIX_REGION_START_H(x)       ( (x&0x3f)     << 20)
#define v_CLUSTER_PIX_REGION_START_V(x)       ( (x&0x3f)     << 26)
#define m_CLUSTER_BLK_SIZE_H        ( (0x1ff)    << 0 )
#define m_CLUSTER_BLK_SIZE_V        ( (0x1ff)    << 16 )
#define m_CLUSTER_BLK_OFFSET_H      ( (0x1ff)    << 0 )
#define m_CLUSTER_BLK_OFFSET_V      ( (0x1ff)    << 16 )
#define m_CLUSTER_BLK_SIZE_FIX      ( (0xfffff)  << 0 )
#define m_CLUSTER_PIX_REGION_START_H       ( (0x3f)     << 20)
#define m_CLUSTER_PIX_REGION_START_V       ( (0x3f)     << 26)

#define v_CLUSTER_SAT_ADJ_ZERO(x)	((x&0xffff)    << 0 )
#define v_CLUSTER_SAT_ADJ_THR(x) 	((x&0xffff)    << 16)
#define m_CLUSTER_SAT_ADJ_ZERO		(0xffff    << 0 )
#define m_CLUSTER_SAT_ADJ_THR 		(0xffff    << 16)


#define v_CLUSTER_SAT_ADJ_K(x)		((x&0xffff)    << 0 )
#define v_CLUSTER_SAT_W(x) 			((x&0x7f)      << 16)


#define m_CLUSTER_SAT_ADJ_K 		(0xffff    << 0 )
#define m_CLUSTER_SAT_W 			(0x7f      << 16)


#define v_CLUSTER_UV_ABJUST_EN(x) 	((x&0x1) 	<< 1)
#define v_CLUSTER_CSC_RANGE(x)		((x&0x1) 	<< 2)
#define v_CLUSTER_DCI_DMA_RID(x)	((x&0x1f) 	<< 4)
#define v_CLUSTER_DCI_DMA_RLEN(x)	((x&0x3) 	<< 12)
#define v_CLUSTER_DCI_EN(x) 		((x&0x1) 	<< 0)


#define m_CLUSTER_UV_ABJUST_EN   	(0x1 	<< 1)
#define m_CLUSTER_CSC_RANGE    		(0x1 	<< 2)
#define m_CLUSTER_DCI_DMA_RID		(0x1f 	<< 4)
#define m_CLUSTER_DCI_DMA_RLEN  	(0x3 	<< 12)
#define m_CLUSTER_DCI_EN   			(0x1 	<< 0)


#define m_CLUSTER_DCI_MST			(0xffffffff   	   << 0 )
#define v_CLUSTER_DCI_MST(x) 		((x&0xffffffff)    << 0 )
//CLUSTER_AFBCD_HDR_DMA_CTRL
#define m_CLUSTER_AFBCD_HDR_DMA_CMD_ARBITER_EN              (0x1        << 0 )
#define m_CLUSTER_AFBCD_HDR_TAIL_NUM                        (0xffff     << 16)
#define v_CLUSTER_AFBCD_HDR_DMA_CMD_ARBITER_EN(x)           ((x&0x1)    << 0 )
#define v_CLUSTER_AFBCD_HDR_TAIL_NUM(x)                     ((x&0xffff) << 16)

#define v_CLUSTER_PLD_OFFSET(x)                       		(((x) & 0xffffffff) << 0 )
#define m_CLUSTER_PLD_OFFSET                         		(0xffffffff<< 0)

#define v_CLUSTER_PLD_RANGE(x)                       		(((x) & 0xffffffff) << 0 )
#define m_CLUSTER_PLD_RANGE                         		(0xffffffff<< 0)

#define v_CLUSTER_EDGE_MAX_TH(x)                       		(((x) & 0x00ff) << 0 )
#define v_CLUSTER_MMM_MIN_TH(x)                       		(((x) & 0x00ff) << 8 )
#define v_CLUSTER_CNT_MIN_TH(x)                       		(((x) & 0x0ffff)<< 16)

#define m_CLUSTER_EDGE_MAX_TH                       		(0xff  << 0 )
#define m_CLUSTER_MMM_MIN_TH                       		    (0xff  << 8 )
#define m_CLUSTER_CNT_MIN_TH                       		    (0xffff<< 16)

#define v_CLUSTER_LG_COE(x)                       		    (((x) & 0xffffffff) << 0 )
#define m_CLUSTER_LG_COE                         		    (0xffffffff<< 0)

#define v_CLUSTER_HG_COE(x)                       		    (((x) & 0xffffffff) << 0 )
#define m_CLUSTER_HG_COE                         		    (0xffffffff<< 0)

//CSC
#define v_SW_CSC_COE_LOW(x)                      (((x)&0xffff)<<0 )
#define v_SW_CSC_COE_HIG(x)                      (((x)&0xffff)<<16)

#define m_SW_CSC_COE_LOW                         (0xffff      <<0 )
#define m_SW_CSC_COE_HIG                         (0xffff      <<16)

//0x134/0x138/0x13c
#define v_SW_CSC_OFFSET(x)                       (((x)&0xffffffff)<<0 )
#define m_SW_CSC_OFFSET                          (0xffffffff      <<0 )


//ZEM_CTRL
#define v_CLUSTER_ZME_XSD_BYPASS(x)                         (((x) & 0x1) <<0 )
#define v_CLUSTER_ZME_XSU_BYPASS(x)                         (((x) & 0x1) <<1 )
#define v_CLUSTER_ZME_YS_BYPASS(x)                          (((x) & 0x1) <<2 )

#define v_CLUSTER_ZME_DERING_EN(x)                          (((x) & 0x1) <<3 )
#define v_CLUSTER_ZME_XGT_EN(x)                             (((x) & 0x1) <<4 )
#define v_CLUSTER_ZME_XGT_MODE(x)                           (((x) & 0x3) <<6 )
#define v_CLUSTER_ZME_YGT_EN(x)                             (((x) & 0x1) <<8 )
#define v_CLUSTER_ZME_YGT_MODE(x)                           (((x) & 0x3) <<10)
#define v_CLUSTER_ZME_GATING(x)                             (((x) & 0x1) <<31)

#define m_CLUSTER_ZME_XSD_BYPASS                         ((0x1) <<0 )
#define m_CLUSTER_ZME_XSU_BYPASS                         ((0x1) <<1 )
#define m_CLUSTER_ZME_YS_BYPASS                          ((0x1) <<2 )

#define m_CLUSTER_ZME_DERING_EN                          ((0x1) <<3 )
#define m_CLUSTER_ZME_XGT_EN                             ((0x1) <<4 )
#define m_CLUSTER_ZME_XGT_MODE                           ((0x3) <<6 )
#define m_CLUSTER_ZME_YGT_EN                             ((0x1) <<8 )
#define m_CLUSTER_ZME_YGT_MODE                           ((0x3) <<10)
#define m_CLUSTER_ZME_GATING                             ((0x1) <<31)

//DERING
#define v_CLUSTER_DERING_ALPHA(x)                       (((x) & 0x1f) <<0)
#define v_CLUSTER_DERING_BETA(x)                        (((x) & 0x1f) <<8)
#define v_CLUSTER_DERING_SEN0(x)                        (((x) & 0x1f) <<16)
#define v_CLUSTER_DERING_SEN1(x)                        (((x) & 0x1f) <<24)

#define m_CLUSTER_DERING_ALPHA                       ((0x1f) <<0)
#define m_CLUSTER_DERING_BETA                        ((0x1f) <<8)
#define m_CLUSTER_DERING_SEN0                        ((0x1f) <<16)
#define m_CLUSTER_DERING_SEN1                        ((0x1f) <<24)

//0X1E0 0x1e8
#define m_CLUSTER_WIN_CRC_EN                        (0x1 << 0)
#define v_CLUSTER_WIN_CRC_EN(x)                     (((x) & 0x1) <<0)


//0x1f4
#define v_CLUSTER_PORT_SEL(x)                       (((x) & 0x3) <<0)
#define m_CLUSTER_PORT_SEL                          ((0x3) <<0)

//0x1f8
#define v_CLUSTER_WIN0_DLY_NUM(x)                   (((x) & 0xff) <<0)
#define v_CLUSTER_WIN1_DLY_NUM(x)                   (((x) & 0xff) <<8)

#define m_CLUSTER_WIN0_DLY_NUM                      ((0xff) <<0)
#define m_CLUSTER_WIN1_DLY_NUM                      ((0xff) <<8)

//ESNART
#define     ESMART_REGION0_BASE    0x0010
#define     ESMART_REGION1_BASE    0x0040
#define     ESMART_REGION2_BASE    0x0070
#define     ESMART_REGION3_BASE    0x00a0


#define m_ESMART_CRC_EN               (0x1<<0)
#define v_ESMART_CRC_EN(x)            (((x)&0x1)<<0)


#define m_ESMART_YUV2RGB_EN           (0x1<<0)
#define m_ESMART_RGB2YUV_EN           (0x1<<1)
#define m_ESMART_CSC_MODE             (0x3<<2)
#define m_ESMART_LUT_EN               (0x1<<4)
#define m_ESMART_BPP_ALPHA_EN         (0x1<<5)
#define m_ESMART_MID_SWAP             (0x1<<8)
#define m_ESMART_ENDIAN_SWAP          (0x1<<9)
#define m_ESMART_SCL_NUM              (0x3<<12)
#define m_ESMART_CSC_PLUS             (0x1<<16)
#define m_ESMART_YUV2RGB_FORCE_EN     (0x1<<24)
#define m_ESMART_SOFT_RESET_EN        (0x1<<31)




#define v_ESMART_YUV2RGB_EN(x)        (((x)&0x1)<<0)
#define v_ESMART_RGB2YUV_EN(x)        (((x)&0x1)<<1)
#define v_ESMART_CSC_MODE(x)          (((x)&0x3)<<2)
#define v_ESMART_LUT_EN(x)            (((x)&0x1)<<4)
#define v_ESMART_BPP_ALPHA_EN(x)      (((x)&0x1)<<5)
#define v_ESMART_MID_SWAP(x)          (((x)&0x1)<<8)
#define v_ESMART_ENDIAN_SWAP(x)       (((x)&0x1)<<9)
#define v_ESMART_SCL_NUM(x)           (((x)&0x3)<<12)
#define v_ESMART_CSC_PLUS(x)          (((x)&0x1)<<16)
#define v_ESMART_YUV2RGB_FORCE_EN(x)  (((x)&0x1)<<24)
#define v_ESMART_SOFT_RESET_EN(x)     (((x)&0x1)<<31)




#define v_ESMART_COLOR_KEY_EN(x)          (((x)&0x1  )<<31)
#define v_ESMART_COLOR_R_KEY(x)           (((x)&0x3ff)<<20)
#define v_ESMART_COLOR_G_KEY(x)           (((x)&0x3ff)<<10)
#define v_ESMART_COLOR_B_KEY(x)           (((x)&0x3ff)<<0)

#define m_ESMART_COLOR_KEY_EN          (0x1<<31)
#define m_ESMART_COLOR_R_KEY           (0x3ff<<20)
#define m_ESMART_COLOR_G_KEY           (0x3ff<<10)
#define m_ESMART_COLOR_B_KEY           (0x3ff<<0)

#define v_ESMART_BG_EN(x)                 (((x)&0x1  )<<31)
#define v_ESMART_BG_R(x)                  (((x)&0x3ff)<<20)
#define v_ESMART_BG_G(x)                  (((x)&0x3ff)<<10)
#define v_ESMART_BG_B(x)                  (((x)&0x3ff)<<0)

#define m_ESMART_BG_EN          (0x1<<31)
#define m_ESMART_BG_R           (0x3ff<<20)
#define m_ESMART_BG_G           (0x3ff<<10)
#define m_ESMART_BG_B           (0x3ff<<0)

#define m_ESMART_ALPHA_0_MAP    (0xff << 0)
#define m_ESMART_ALPHA_1_MAP    (0xff << 8)
#define m_ESMART_ALPHA_EN       (0x1  << 31)

#define v_ESMART_ALPHA_0_MAP(x) (((x)&0xff) << 0)
#define v_ESMART_ALPHA_1_MAP(x) (((x)&0xff) << 8)
#define v_ESMART_ALPHA_EN(x)    (((x)&0x1 ) << 31)



#define m_ESMART_RLEN                      (0x3 <<0  )
#define m_ESMART_YRGB_GATHER_EN            (0x1 <<2  )
#define m_ESMART_CBCR_GATHER_EN            (0x1 <<3  )
#define m_ESMART_YRGB_RID                  (0x1f<<4  )
#define m_ESMART_CBCR_RID                  (0x1f<<12 )
#define m_ESMART_YRGB_GATHER_NUM           (0xf <<20 )
#define m_ESMART_CBCR_GATHER_NUM           (0xf <<24 )
#define m_ESMART_DMA_HURRY_EN              (0x1 <<28 )
#define m_ESMART_DMA_HURRY_THOLD           (0x3 <<29 )
#define m_ESMART_VREV_EN                   (0x1 <<31 )

#define v_ESMART_RLEN(x)                   (((x)&0x3 )<<0  )
#define v_ESMART_YRGB_GATHER_EN(x)         (((x)&0x1 )<<2  )
#define v_ESMART_CBCR_GATHER_EN(x)         (((x)&0x1 )<<3  )
#define v_ESMART_YRGB_RID(x)               (((x)&0x1f)<<4  )
#define v_ESMART_CBCR_RID(x)               (((x)&0x1f)<<12 )
#define v_ESMART_YRGB_GATHER_NUM(x)        (((x)&0xf )<<20 )
#define v_ESMART_CBCR_GATHER_NUM(x)        (((x)&0xf )<<24 )
#define v_ESMART_DMA_HURRY_EN(x)           (((x)&0x1 )<<28 )
#define v_ESMART_DMA_HURRY_THOLD(x)        (((x)&0x3 )<<29 )
#define v_ESMART_VREV_EN(x)                (((x)&0x1 )<<31 )

#define m_ESMART_DMA_STOP                  (0x1 <<0  )
#define m_ESMART_AXI_SEL                   (0x1 <<1  )
#define m_ESMART_MMU_BYPASS                (0x1 <<2  )
#define m_ESMART_OUTSTANDING_EN            (0x1 <<3  )
#define m_ESMART_OUTSTANDING_NUM           (0xf <<4  )
#define m_ESMART_AUTO_GATING               (0x1 <<8  )
#define m_ESMART_DMA_OPT_EN                (0x1 <<16 )

#define v_ESMART_DMA_STOP(x)               (((x)&0x1 )<<0  )
#define v_ESMART_AXI_SEL(x)                (((x)&0x1 )<<1  )
#define v_ESMART_MMU_BYPASS(x)             (((x)&0x1 )<<2  )
#define v_ESMART_OUTSTANDING_EN(x)         (((x)&0x1 )<<3  )
#define v_ESMART_OUTSTANDING_NUM(x)        (((x)&0xf )<<4  )
#define v_ESMART_AUTO_GATING(x)            (((x)&0x1 )<<8  )
#define v_ESMART_DMA_OPT_EN(x)             (((x)&0x1 )<<16  )

#define m_ESMART_WIN_EN              (0x1 <<0 )
#define m_ESMART_DATA_FMT            (0x1f<<1 )
#define m_ESMART_DATA_FMT_SEL        (0x1 <<7 )
#define m_ESMART_YRGB_2GT            (0x1 <<8 )
#define m_ESMART_YRGB_4GT            (0x1 <<9 )
#define m_ESMART_CBCR_2GT            (0x1 <<10)
#define m_ESMART_CBCR_4GT            (0x1 <<11)
#define m_ESMART_DITHER_UP           (0x1 <<12)
#define m_ESMART_ALPHA_SWAP          (0x1 <<13)
#define m_ESMART_RB_SWAP             (0x1 <<14)
//#define m_ESMART_MID_SWAP            (0x1 <<15)
#define m_ESMART_UV_SWAP             (0x1 <<16)
#define m_ESMART_YUV_CLIP            (0x1 <<17)
#define m_ESMART_RG_SWAP             (0x1 <<18)
#define m_ESMART_XAVG_EN             (0x1 <<20)
#define m_ESMART_XGT_EN              (0x1 <<21)
#define m_ESMART_XGT_MODE            (0x3<<22)



#define v_ESMART_WIN_EN(x)              (((x)&0x1 )<<0 )
#define v_ESMART_DATA_FMT(x)            (((x)&0x1f)<<1 )
#define v_ESMART_DATA_FMT_SEL(x)        (((x)&0x1 )<<7 )

#define v_ESMART_YRGB_2GT(x)            (((x)&0x1 )<<8 )
#define v_ESMART_YRGB_4GT(x)            (((x)&0x1 )<<9 )
#define v_ESMART_CBCR_2GT(x)            (((x)&0x1 )<<10)
#define v_ESMART_CBCR_4GT(x)            (((x)&0x1 )<<11)
#define v_ESMART_DITHER_UP(x)           (((x)&0x1 )<<12)
#define v_ESMART_ALPHA_SWAP(x)          (((x)&0x1 )<<13)
#define v_ESMART_RB_SWAP(x)             (((x)&0x1 )<<14)
//#define v_ESMART_MID_SWAP(x)            (((x)&0x1 )<<15)
#define v_ESMART_UV_SWAP(x)             (((x)&0x1 )<<16)
#define v_ESMART_YUV_CLIP(x)            (((x)&0x1 )<<17)
#define v_ESMART_RG_SWAP(x)             (((x)&0x1 )<<18)

#define v_ESMART_XAVG_EN(x)             (((x)&0x1 )<<20)
#define v_ESMART_XGT_EN(x)              (((x)&0x1 )<<21)
#define v_ESMART_XGT_MODE(x)            (((x)&0x3 )<<22)


#define m_ESMART_YRGB_MST                (0xffffffff<<0)
#define v_ESMART_YRGB_MST(x)             (((x)&0xffffffff)<<0)

#define m_ESMART_CBCR_MST                (0xffffffff<<0)
#define v_ESMART_CBCR_MST(x)             (((x)&0xffffffff)<<0)

#define m_ESMART_YRGB_VIR                (0xffff<<0)
#define m_ESMART_CBCR_VIR                (0xffff<<16)
#define v_ESMART_YRGB_VIR(x)             (((x)&0xffff)<<0)
#define v_ESMART_CBCR_VIR(x)             (((x)&0xffff)<<16)

#define m_ESMART_ACT_WIDTH                (0x1fff<<0)
#define m_ESMART_ACT_HEIGHT               (0x1fff<<16)
#define v_ESMART_ACT_WIDTH(x)              (((x)&0x1fff)<<0)
#define v_ESMART_ACT_HEIGHT(x)             (((x)&0x1fff)<<16)

#define m_ESMART_DSP_WIDTH                (0x1fff<<0)
#define m_ESMART_DSP_HEIGHT               (0x1fff<<16)
#define v_ESMART_DSP_WIDTH(x)              (((x)&0x1fff)<<0)
#define v_ESMART_DSP_HEIGHT(x)             (((x)&0x1fff)<<16)

#define m_ESMART_DSP_XOFF                (0x1fff<<0)
#define m_ESMART_DSP_YOFF                (0x1fff<<16)
#define v_ESMART_DSP_XOFF(x)             (((x)&0x1fff)<<0)
#define v_ESMART_DSP_YOFF(x)             (((x)&0x1fff)<<16)

#define m_ESMART_YRGB_XSU_EN              (0x1 <<0 )
#define m_ESMART_YRGB_XSD_EN              (0x1 <<1 )
#define m_ESMART_YRGB_XS_MODE             (0x3 <<2 )
#define m_ESMART_YRGB_YSU_EN              (0x1 <<4 )
#define m_ESMART_YRGB_YSD_EN              (0x1 <<5 )
#define m_ESMART_YRGB_YS_MODE             (0x3 <<6 )
#define m_ESMART_CBCR_XSU_EN              (0x1 <<8 )
#define m_ESMART_CBCR_XSD_EN              (0x1 <<9 )
#define m_ESMART_CBCR_XS_MODE             (0x3 <<10)
#define m_ESMART_CBCR_YSU_EN              (0x1 <<12)
#define m_ESMART_CBCR_YSD_EN              (0x1 <<13)
#define m_ESMART_CBCR_YS_MODE             (0x3 <<14)
#define m_ESMART_XSU_BIC_MODE             (0x3 <<16)
#define m_ESMART_YSU_BIC_MODE             (0x3 <<18)

#define v_ESMART_YRGB_XSU_EN(x)              (((x)&0x1) <<0 )
#define v_ESMART_YRGB_XSD_EN(x)              (((x)&0x1) <<1 )
#define v_ESMART_YRGB_XS_MODE(x)             (((x)&0x3) <<2 )
#define v_ESMART_YRGB_YSU_EN(x)              (((x)&0x1) <<4 )
#define v_ESMART_YRGB_YSD_EN(x)              (((x)&0x1) <<5 )
#define v_ESMART_YRGB_YS_MODE(x)             (((x)&0x3) <<6 )
#define v_ESMART_CBCR_XSU_EN(x)              (((x)&0x1) <<8 )
#define v_ESMART_CBCR_XSD_EN(x)              (((x)&0x1) <<9 )
#define v_ESMART_CBCR_XS_MODE(x)             (((x)&0x3) <<10)
#define v_ESMART_CBCR_YSU_EN(x)              (((x)&0x1) <<12)
#define v_ESMART_CBCR_YSD_EN(x)              (((x)&0x1) <<13)
#define v_ESMART_CBCR_YS_MODE(x)             (((x)&0x3) <<14)
#define v_ESMART_XSU_BIC_MODE(x)             (((x)&0x3) <<16)
#define v_ESMART_YSU_BIC_MODE(x)             (((x)&0x3) <<18)

#define m_ESMART_YRGB_XFACTOR                (0xffff<<0)
#define m_ESMART_YRGB_YFACTOR                (0xffff<<16)
#define v_ESMART_YRGB_XFACTOR(x)             (((x)&0xffff)<<0)
#define v_ESMART_YRGB_YFACTOR(x)             (((x)&0xffff)<<16)

#define m_ESMART_CBCR_XFACTOR                (0xffff<<0)
#define m_ESMART_CBCR_YFACTOR                (0xffff<<16)
#define v_ESMART_CBCR_XFACTOR(x)             (((x)&0xffff)<<0)
#define v_ESMART_CBCR_YFACTOR(x)             (((x)&0xffff)<<16)

#define m_ESMART_YRGB_XOFFSET                (0xff<<0 )
#define m_ESMART_YRGB_YOFFSET                (0xff<<8 )
#define m_ESMART_CBCR_XOFFSET                (0xff<<16)
#define m_ESMART_CBCR_YOFFSET                (0xff<<24)
#define v_ESMART_YRGB_XOFFSET(x)                (((x)&0xff)<<0 )
#define v_ESMART_YRGB_YOFFSET(x)                (((x)&0xff)<<8 )
#define v_ESMART_CBCR_XOFFSET(x)                (((x)&0xff)<<16)
#define v_ESMART_CBCR_YOFFSET(x)                (((x)&0xff)<<24)

//0x00f4
#define v_ESMART_PORT_SEL(x)                (((x)&0x3)<<0 )
#define m_ESMART_PORT_SEL                   (0x3<<0 )

//0x00f8
#define v_ESMART_DLY_NUM(x)                (((x)&0xff)<<0 )
#define m_ESMART_DLY_NUM                   (0xff<<0 )

//-----------------------------------------------------------------------------
//OVERLAY
#define v_DP0_EXTRA_WIN_EN(x)                   ( ((x) & 0x0001) << 0  )
#define v_DP1_EXTRA_WIN_EN(x)                   ( ((x) & 0x0001) << 4  )

#define m_DP0_EXTRA_WIN_EN                      ( 0x0001 << 0  )
#define m_DP1_EXTRA_WIN_EN                      ( 0x0001 << 4  )

#define v_OVERLAY_GATING_EN(x)                  ( ((x) & 0x0001) << 0  )
#define m_OVERLAY_GATING_EN                     ( 0x0001 << 0  )

#define v_LAYER_SEL_REGDONE_SEL(x)              ( ((x) & 0x0003) << 30 )
#define v_LAYER_SEL_REGDONE_IMD(x)              ( ((x) & 0x0001) << 28 )
#define v_DP1_HDR10_OUT_FMT(x)                  ( ((x) & 0x0001) << 25 ) //lyx add@20201117
#define v_DP1_HDR10_IN_FMT(x)                   ( ((x) & 0x0001) << 24 ) //lyx add@20201117
#define v_DP0_DOLBY_LUT_UPDATE(x)               ( ((x) & 0x0001) << 11 ) //lyx add@20210119
#define v_DP0_DOLBY_CORE3_EN(x)                 ( ((x) & 0x0001) << 10 ) //lyx add@20201117
#define v_DP0_DOLBY_CORE2_EN(x)                 ( ((x) & 0x0001) << 9  ) //lyx add@20201117
#define v_DP0_DOLBY_CORE1_EN(x)                 ( ((x) & 0x0001) << 8  ) //lyx add@20201117
#define v_DP0_HDR10_OUT_FMT(x)                  ( ((x) & 0x0001) << 5  )
#define v_DP0_HDR10_IN_FMT(x)                   ( ((x) & 0x0001) << 4  )
#define v_OVERLAY_MODE3(x)                      ( ((x) & 0x0001) << 3  )
#define v_OVERLAY_MODE2(x)                      ( ((x) & 0x0001) << 2  )
#define v_OVERLAY_MODE1(x)                      ( ((x) & 0x0001) << 1  )
#define v_OVERLAY_MODE0(x)                      ( ((x) & 0x0001) << 0  )

#define m_LAYER_SEL_REGDONE_SEL                 (  0x0003 << 30	)
#define m_LAYER_SEL_REGDONE_IMD                 (  0x0001 << 28	)
#define m_DP1_HDR10_OUT_FMT                     (  0x0001 << 25 ) //lyx add@20201117
#define m_DP1_HDR10_IN_FMT                      (  0x0001 << 24 ) //lyx add@20201117
#define m_DP0_DOLBY_LUT_UPDATE                  (  0x0001 << 11 ) //lyx add@20210119
#define m_DP0_DOLBY_CORE3_EN                    (  0x0001 << 10 ) //lyx add@20201117
#define m_DP0_DOLBY_CORE2_EN                    (  0x0001 << 9  ) //lyx add@20201117
#define m_DP0_DOLBY_CORE1_EN                    (  0x0001 << 8  ) //lyx add@20201117
#define m_DP0_HDR10_OUT_FMT                     (  0x0001 << 5	)
#define m_DP0_HDR10_IN_FMT                      (  0x0001 << 4	)
#define m_OVERLAY_MODE3                         (  0x0001 << 3  )
#define m_OVERLAY_MODE2                         (  0x0001 << 2	)
#define m_OVERLAY_MODE1                         (  0x0001 << 1	)
#define m_OVERLAY_MODE0				            (  0x0001 << 0	)

#define v_DOLBY_CORE2_DLY_EN(x)                 ( ((x) & 0x0001) << 13 )
#define v_DOLBY_CORE2_LUT_UPDATE(x)             ( ((x) & 0x0001) << 12 )
#define v_DOLBY_CORE1_LUT_UPDATE(x)             ( ((x) & 0x0001) << 11 )
#define v_DOLBY_CORE3_EN(x)                     ( ((x) & 0x0001) << 10 )
#define v_DOLBY_CORE2_EN(x)                     ( ((x) & 0x0001) << 9  )
#define v_DOLBY_CORE1_EN(x)                     ( ((x) & 0x0001) << 8  )
#define v_DOLBY_CORE2_YUV422_EN(x)              ( ((x) & 0x0001) << 7	)
#define v_DOLBY_YUV_SWAP(x)                     ( ((x) & 0x0001) << 6	)
#define v_SDR2HDR10_PATH_EN(x)                  ( ((x) & 0x0001) << 5	)
#define v_HDR10_PATH_EN(x)                      ( ((x) & 0x0001) << 4	)
#define v_OVERLAY_MODE(x)				        ( ((x) & 0x0001) << 0	)

#define m_DOLBY_CORE2_DLY_EN                    (  0x0001 << 13 )
#define m_DOLBY_CORE2_LUT_UPDATE                (  0x0001 << 12 )
#define m_DOLBY_CORE1_LUT_UPDATE                (  0x0001 << 11 )
#define m_DOLBY_CORE3_EN                        (  0x0001 << 10 )
#define m_DOLBY_CORE2_EN                        (  0x0001 << 9  )
#define m_DOLBY_CORE1_EN                        (  0x0001 << 8  )
#define m_DOLBY_CORE2_YUV422_EN                 (  0x0001 << 7	)
#define m_DOLBY_YUV_SWAP                        (  0x0001 << 6	)
#define m_SDR2HDR10_PATH_EN                     (  0x0001 << 5	)
#define m_HDR10_PATH_EN                         (  0x0001 << 4	)
#define m_OVERLAY_MODE				            (  0x0001 << 0	)

//OVERLAY_LAYER_SEL
#define v_LAYER7_SEL(x)                         (((x)&0x000f) << 28)
#define v_LAYER6_SEL(x)                         (((x)&0x000f) << 24)
#define v_LAYER5_SEL(x)                         (((x)&0x000f) << 20)
#define v_LAYER4_SEL(x)                         (((x)&0x000f) << 16)
#define v_LAYER3_SEL(x)                         (((x)&0x000f) << 12)
#define v_LAYER2_SEL(x)                         (((x)&0x000f) << 8 )
#define v_LAYER1_SEL(x)                         (((x)&0x000f) << 4 )
#define v_LAYER0_SEL(x)                         (((x)&0x000f) << 0 )
#define m_LAYER7_SEL                            (  0x000f << 28)
#define m_LAYER6_SEL                            (  0x000f << 24)
#define m_LAYER5_SEL                            (  0x000f << 20)
#define m_LAYER4_SEL                            (  0x000f << 16)
#define m_LAYER3_SEL                            (  0x000f << 12)
#define m_LAYER2_SEL                            (  0x000f << 8 )
#define m_LAYER1_SEL                            (  0x000f << 4 )
#define m_LAYER0_SEL                            (  0x000f << 0 )

////OVERLAY_PORT_SEL
//#define v_SMART1_SEL_PORT(x)                    (((x) & 0x0003) << 28)
//#define v_SMART0_SEL_PORT(x)                    (((x) & 0x0003) << 24)
//#define v_ESMART1_SEL_PORT(x)                   (((x) & 0x0003) << 20)
//#define v_ESMART0_SEL_PORT(x)                   (((x) & 0x0003) << 16)
//#define v_CLUSTER3_SEL_PORT(x)                  (((x) & 0x0003) << 12)
//#define v_CLUSTER2_SEL_PORT(x)                  (((x) & 0x0003) << 8 )
//#define v_CLUSTER1_SEL_PORT(x)                  (((x) & 0x0003) << 4 )
//#define v_CLUSTER0_SEL_PORT(x)                  (((x) & 0x0003) << 0 )
////#define v_PORT3_MUX(x)                          (((x) & 0x000f) << 12)
////#define v_PORT2_MUX(x)                          (((x) & 0x000f) << 8 )
////#define v_PORT1_MUX(x)                          (((x) & 0x000f) << 4 )
////#define v_PORT0_MUX(x)                          (((x) & 0x000f) << 0 )
//
//#define m_SMART1_SEL_PORT                       ( 0x0003 << 28)
//#define m_SMART0_SEL_PORT                       ( 0x0003 << 24)
//#define m_ESMART1_SEL_PORT                      ( 0x0003 << 20)
//#define m_ESMART0_SEL_PORT                      ( 0x0003 << 16)
//#define m_CLUSTER3_SEL_PORT                     ( 0x0003 << 12)
//#define m_CLUSTER2_SEL_PORT                     ( 0x0003 << 8 )
//#define m_CLUSTER1_SEL_PORT                     ( 0x0003 << 4 )
//#define m_CLUSTER0_SEL_PORT                     ( 0x0003 << 0 )
//#define m_PORT3_MUX                             ( 0x000f << 12)
//#define m_PORT2_MUX                             ( 0x000f << 8 )
//#define m_PORT1_MUX                             ( 0x000f << 4 )
//#define m_PORT0_MUX                             ( 0x000f << 0 )

//OVERLAY_DOLBY_LUT_MST
#define v_DOLBY_LUT_MST(x)                      (((x) & 0xffffffff) << 0 )

#define m_DOLBY_LUT_MST                         ( 0xffffffff << 0 )

//MIX_SRC_COLOR_CTRL
#define v_MIX_SRC_COLOR_M0(x)       				(((x)&0x1)<<0)
#define v_MIX_SRC_ALPHA_M0(x)       				(((x)&0x1)<<1)
#define v_MIX_SRC_BLEND_M0(x)       				(((x)&0x3)<<2)
#define v_MIX_SRC_ALPHA_CAL_M0(x)   				(((x)&0x1)<<4)
#define v_MIX_SRC_FACTOR_M0(x)      				(((x)&0x7)<<5)
#define v_MIX_SRC_ALPHA_EN(x)       				(((x)&0x1)<<8)
#define v_MIX_SRC_TOP_SWAP(x)       				(((x)&0x1)<<9)
#define v_MIX_SRC_GLOBAL_ALPHA(x)   				(((x)&0xff)<<16)
#define m_MIX_SRC_COLOR_M0       					( 0x1 <<0)
#define m_MIX_SRC_ALPHA_M0       					( 0x1 <<1)
#define m_MIX_SRC_BLEND_M0       					( 0x3 <<2)
#define m_MIX_SRC_ALPHA_CAL_M0   					( 0x1 <<4)
#define m_MIX_SRC_FACTOR_M0      					( 0x7 <<5)
#define m_MIX_SRC_ALPHA_EN       					( 0x1 <<8)
#define m_MIX_SRC_TOP_SWAP       					( 0x1 <<9)
#define m_MIX_SRC_GLOBAL_ALPHA   					( 0xff<<16)

//MIX_DST_COLOR_CTRL
#define v_MIX_DST_COLOR_M0(x)       				(((x)&1)<<0)
#define v_MIX_DST_ALPHA_M0(x)       				(((x)&1)<<1)
#define v_MIX_DST_BLEND_M0(x)       				(((x)&3)<<2)
#define v_MIX_DST_ALPHA_CAL_M0(x)   				(((x)&1)<<4)
#define v_MIX_DST_FACTOR_M0(x)      				(((x)&7)<<5)
#define v_MIX_DST_GLOBAL_ALPHA(x)   				(((x)&0xff)<<16)
#define m_MIX_DST_COLOR_M0       					( 0x1 <<0)
#define m_MIX_DST_ALPHA_M0       					( 0x1 <<1)
#define m_MIX_DST_BLEND_M0       					( 0x3 <<2)
#define m_MIX_DST_ALPHA_CAL_M0   					( 0x1 <<4)
#define m_MIX_DST_FACTOR_M0      					( 0x7 <<5)
#define m_MIX_DST_GLOBAL_ALPHA   					( 0xff<<16)

//MIX_SRC_ALPHA_CTRL
#define m_MIX_SRC_ALPHA_M1       					( 0x1 <<1)
#define m_MIX_SRC_BLEND_M1       					( 0x3 <<2)
#define m_MIX_SRC_ALPHA_CAL_M1   					( 0x1 <<4)
#define m_MIX_SRC_FACTOR_M1      					( 0x7 <<5)
#define v_MIX_SRC_ALPHA_M1(x)       				(((x)&1)<<1)
#define v_MIX_SRC_BLEND_M1(x)       				(((x)&3)<<2)
#define v_MIX_SRC_ALPHA_CAL_M1(x)   				(((x)&1)<<4)
#define v_MIX_SRC_FACTOR_M1(x)      				(((x)&7)<<5)

//MIX_DST_ALPHA_CTRL
#define m_MIX_DST_ALPHA_M1       					( 0x1 <<1)
#define m_MIX_DST_BLEND_M1       					( 0x3 <<2)
#define m_MIX_DST_ALPHA_CAL_M1   					( 0x1 <<4)
#define m_MIX_DST_FACTOR_M1      					( 0x7 <<5)
#define v_MIX_DST_ALPHA_M1(x)       				(((x)&1)<<1)
#define v_MIX_DST_BLEND_M1(x)       				(((x)&3)<<2)
#define v_MIX_DST_ALPHA_CAL_M1(x)   				(((x)&1)<<4)
#define v_MIX_DST_FACTOR_M1(x)      				(((x)&7)<<5)

#define m_BG_ALPHA_EN  	                            ( 0x1 <<0)
#define m_BG_ALPHA_MODE                             ( 0x1 <<1)
#define m_BG_ALPHA_PRE_MUL                          ( 0x1 <<2)
#define m_BG_ALPHA_SAT_MODE                         ( 0x1 <<3)
#define m_BG_LINE_END_MODE                          ( 0x1 <<4)
#define m_BG_ALPHA_GLOBAL                           ( 0xff<<8)
#define m_BG_DLY_NUM                                ( 0xff<<24)

#define v_BG_ALPHA_EN(x)  	                        (((x)&0x1 )<<0)
#define v_BG_ALPHA_MODE(x)                          (((x)&0x1 )<<1)
#define v_BG_ALPHA_PRE_MUL(x)                       (((x)&0x1 )<<2)
#define v_BG_ALPHA_SAT_MODE(x)                      (((x)&0x1 )<<3)
#define v_BG_LINE_END_MODE(x)                       (((x)&0x1 )<<4)
#define v_BG_ALPHA_GLOBAL(x)                        (((x)&0xff)<<8)
#define v_BG_DLY_NUM(x)                             (((x)&0xff)<<24)

//#define v_CLUSTER0_0_DLY_NUM(x)              (((x)&0xff)<<0 )
//#define v_CLUSTER0_1_DLY_NUM(x)              (((x)&0xff)<<8 )
//#define v_CLUSTER1_0_DLY_NUM(x)              (((x)&0xff)<<0 )
//#define v_CLUSTER1_1_DLY_NUM(x)              (((x)&0xff)<<8 )
//
//#define m_CLUSTER0_0_DLY_NUM              (0xff<<0 )
//#define m_CLUSTER0_1_DLY_NUM              (0xff<<8 )
//#define m_CLUSTER1_0_DLY_NUM              (0xff<<0 )
//#define m_CLUSTER1_1_DLY_NUM              (0xff<<8 )
//
//#define v_CLUSTER2_0_DLY_NUM(x)              (((x)&0xff)<<0 )
//#define v_CLUSTER2_1_DLY_NUM(x)              (((x)&0xff)<<8 )
//#define v_CLUSTER3_0_DLY_NUM(x)              (((x)&0xff)<<0)
//#define v_CLUSTER3_1_DLY_NUM(x)              (((x)&0xff)<<8)
//
//#define m_CLUSTER2_0_DLY_NUM              (0xff<<0 )
//#define m_CLUSTER2_1_DLY_NUM              (0xff<<8 )
//#define m_CLUSTER3_0_DLY_NUM              (0xff<<0 )
//#define m_CLUSTER3_1_DLY_NUM              (0xff<<8 )
//
//#define v_ESMART0_DLY_NUM(x)              (((x)&0xff)<<0 )
//#define v_ESMART1_DLY_NUM(x)              (((x)&0xff)<<0 )
//#define v_SMART0_DLY_NUM(x)               (((x)&0xff)<<0 )
//#define v_SMART1_DLY_NUM(x)               (((x)&0xff)<<0 )
//
//#define m_ESMART0_DLY_NUM              (0xff<<0 )
//#define m_ESMART1_DLY_NUM              (0xff<<0 )
//#define m_SMART0_DLY_NUM               (0xff<<0 )
//#define m_SMART1_DLY_NUM               (0xff<<0 )


//------------------------------------------------------------------------------
#define v_VOP_STANDBY_EN(x)							(((x)&0x1)<<31)
#define v_VOP_FP_STANDBY_EN(x)						(((x)&0x1)<<30)
#define v_DSP_DCF_EN(x)                             (((x)&0x1)<<29)
#define v_DSP_LUT_EN(x)	                            (((x)&0x1)<<28)
#define v_DSP_BLACK_EN(x)							(((x)&0x1)<<27)
#define v_DSP_OUT_ZERO(x)                           (((x)&0x1)<<26)
#define v_SW_TVE_OUTPUT_SEL(x)                      (((x)&0x1)<<25)
#define v_DSP_BLANK_EN(x)                           (((x)&0x1)<<24)
#define v_POST_LB_MODE(x)                           (((x)&0x1)<<23)
//#define v_DSP_DN_SAMPLE_Y_EN(x)                     (((x)&0x1)<<22)
//#define v_DSP_DN_SAMPLE_X_EN(x)                     (((x)&0x1)<<21)
#define v_DUAL_GAMMA_UPDATE(x)                      (((x)&0x1)<<22)
#define v_WIN_BYPASS_EN(x)                          (((x)&0x1)<<21)
#define v_DITHER_DOWN_MODE(x)                       (((x)&0x1)<<20)
#define v_DITHER_DOWN_SEL(x)                        (((x)&0x3)<<18)
#define v_DITHER_DOWN_EN(x)                         (((x)&0x1)<<17)
#define v_PRE_DITHER_DOWN_EN(x)                     (((x)&0x1)<<16)
#define v_DSP_OUT_RGB_YUV(x)                        (((x)&0x1)<<15)
#define v_DSP_Y_MIR_EN(x)                           (((x)&0x1)<<14)
#define v_DSP_X_MIR_EN(x)                           (((x)&0x1)<<13)
#define v_DSP_DUMMY_SWAP(x)                         (((x)&0x1)<<12)
#define v_DSP_DELTA_SWAP(x)                         (((x)&0x1)<<11)
#define v_DSP_RG_SWAP(x)                            (((x)&0x1)<<10)
#define v_DSP_RB_SWAP(x)                            (((x)&0x1)<<9)
#define v_DSP_BG_SWAP(x)                            (((x)&0x1)<<8)
#define v_DSP_INTERLACE(x)							(((x)&0x1)<<7)
#define v_DSP_FIELD_POL(x)                          (((x)&0x1)<<6)
#define v_DSP_P2I_EN(x)                             (((x)&0x1)<<5)
#define v_DSP_CORE_DCLK_SEL(x)                      (((x)&0x1)<<4)
#define v_DSP_OUT_MODE(x)                           (((x)&0x000f)<<0)

#define m_VOP_STANDBY_EN                            (0x1<<31)
#define m_VOP_FP_STANDBY_EN                         (0x1<<30)
#define m_DSP_DCF_EN                                (0x1<<29)
#define m_DSP_LUT_EN	                            (0x1<<28)
#define m_DSP_BLACK_EN                              (0x1<<27)
#define m_DSP_OUT_ZERO                              (0x1<<26)
#define m_SW_TVE_OUTPUT_SEL                         (0x1<<25)
#define m_DSP_BLANK_EN                              (0x1<<24)
#define m_POST_LB_MODE                              (0x1<<23)
//#define m_DSP_DN_SAMPLE_Y_EN                        (0x1<<22)
//#define m_DSP_DN_SAMPLE_X_EN                        (0x1<<21)
#define m_DUAL_GAMMA_UPDATE                         (0x1<<22)
#define m_WIN_BYPASS_EN                             (0x1<<21)
#define m_DITHER_DOWN_MODE                          (0x1<<20)
#define m_DITHER_DOWN_SEL                           (0x3<<18)
#define m_DITHER_DOWN_EN                            (0x1<<17)
#define m_PRE_DITHER_DOWN_EN                        (0x1<<16)
#define m_DSP_OUT_RGB_YUV                           (0x1<<15)
#define m_DSP_Y_MIR_EN                              (0x1<<14)
#define m_DSP_X_MIR_EN                              (0x1<<13)
#define m_DSP_DUMMY_SWAP                            (0x1<<12)
#define m_DSP_DELTA_SWAP                            (0x1<<11)
#define m_DSP_RG_SWAP                               (0x1<<10)
#define m_DSP_RB_SWAP                               (0x1<<9)
#define m_DSP_BG_SWAP                               (0x1<<8)
#define m_DSP_INTERLACE 							(0x1<<7)
#define m_DSP_FIELD_POL                             (0x1<<6)
#define m_DSP_P2I_EN                                (0x1<<5)
#define m_DSP_CORE_DCLK_SEL                         (0x1<<4)
#define m_DSP_OUT_MODE                              (0x000f<<0)

#define v_EDPI_WMS_FS(x)                               (((x)&0x1)<<31)
#define v_EDPI_HOLD_MODE(x)                            (((x)&0x1)<<30)
#define v_EDPI_TE_MODE(x)                              (((x)&0x1)<<29)
#define v_EDPI_TE_EN(x)                                (((x)&0x1)<<28)
#define v_DOUB_CHANNEL_OVERLAP(x)					   (((x)&0xf)<<24)
#define v_DOUB_CHANNEL_SWAP(x)                         (((x)&0x1)<<21)
#define v_DOUB_CHANNEL_EN(x)                           (((x)&0x1)<<20)
#define v_DCLK_DDR_EN1(x)                              (((x)&0x1)<<5)
#define v_DCLK_DDR_EN0(x)                              (((x)&0x1)<<4)
#define v_DCLK_DDR_EN(x)                               (((x)&0x3)<<4)
#define v_DSP_DATA_10B_EN(x)                           (((x)&0x1)<<0)

#define m_EDPI_WMS_FS                               (0x1<<31)
#define m_EDPI_HOLD_MODE                            (0x1<<30)
#define m_EDPI_TE_MODE                              (0x1<<29)
#define m_EDPI_TE_EN                                (0x1<<28)
#define m_DOUB_CHANNEL_OVERLAP						(0xf<<24)
#define m_DOUB_CHANNEL_SWAP                         (0x1<<21)
#define m_DOUB_CHANNEL_EN                           (0x1<<20)
#define m_DCLK_DDR_EN1                              (0x1<<5)
#define m_DCLK_DDR_EN0                              (0x1<<4)
#define m_DSP_DATA_10B_EN                           (0x1<<0)

#define v_COLOR_BAR_MODE(x)                         (((x)&0x1)<<1)
#define v_COLOR_BAR_EN(x)                           (((x)&0x1)<<0)
#define v_POST_URGENCY_EN(x)                        (((x)&0x1)<<8)
#define v_POST_AUTOCS_EN(x)                         (((x)&0x1)<<9)
#define v_POST_ALMOST_FULL_TH(x)                    (((x)&0xf)<<12)
#define v_POST_URGENCY_THL(x)                       (((x)&0xf)<<16)
#define v_POST_URGENCY_THH(x)                       (((x)&0xf)<<20)
#define v_POST_AUTOCS_THL(x)                        (((x)&0xf)<<24)
#define v_POST_AUTOCS_THH(x)                        (((x)&0xf)<<28)

#define m_COLOR_BAR_MODE                            (0x1<<1)
#define m_COLOR_BAR_EN                              (0x1<<0)
#define m_POST_URGENCY_EN                           (0x1<<8)
#define m_POST_AUTOCS_EN                            (0x1<<9)
#define m_POST_ALMOST_FULL_TH                       (0xf<<12)
#define m_POST_URGENCY_THL                          (0xf<<16)
#define m_POST_URGENCY_THH                          (0xf<<20)
#define m_POST_AUTOCS_THL                           (0xf<<24)
#define m_POST_AUTOCS_THH                           (0xf<<28)

#define v_DCLK_CORE_DIV_SEL(x)                   (((x)&0x3)<<0)
#define v_DCLK_OUT_DIV_SEL(x)                    (((x)&0x3)<<2)

#define m_DCLK_CORE_DIV_SEL                   (0x3<<0)
#define m_DCLK_OUT_DIV_SEL                    (0x3<<2)
#define m_POST_AUTO_GATING                    (0x1<<30)
#define m_POST_TIMING_CLEAR                   (0x1<<31)

#define v_POST_AUTO_GATING(x)                    (((x)&0x1)<<30)
#define v_POST_TIMING_CLEAR(x)                   (((x)&0x1)<<31)

#define v_3DLUT_ADDR(x)                           (((x)&0x3ff)<<16)
#define v_3DLUT_GATING_EN(x)                      (((x)&0x1)<<4)
#define v_3DLUT_MODE(x)                           (((x)&0x1)<<3)
#define v_3DLUT_UPDATE_EN(x)                      (((x)&0x1)<<2)
#define v_3DLUT_BYPASS_EN(x)                      (((x)&0x1)<<1)
#define v_3DLUT_EN(x)                             (((x)&0x1)<<0)

#define m_3DLUT_ADDR                              (0x3ff<<16)
#define m_3DLUT_GATING_EN                         (0x1<<4)
#define m_3DLUT_MODE                              (0x1<<3)
#define m_3DLUT_UPDATE_EN                         (0x1<<2)
#define m_3DLUT_BYPASS_EN                         (0x1<<1)
#define m_3DLUT_EN                                (0x1<<0)

#define v_3DLUT_COMP(x)                           (((x)&0xfff)<<0)
#define m_3DLUT_COMP                              (0xfff<<0)

#define v_3DLUT_MST(x)                           (((x)&0xffffffff)<<0)
#define m_3DLUT_MST                              (0xffffffff<<0)
//POST_CRC_CHECK_DATA
#define v_POST_CRC_CHECK_DATA(x)                    (((x)&0xffffffff)<<0)
#define m_POST_CRC_CHECK_DATA                       ((0xffffffff)<<0)


#define v_PRE_SCAN_HBLANK(x)						(((x)&0x1fff)<<0)
#define v_PRE_SCAN_HACTIVE(x)						(((x)&0x1fff)<<16)
#define m_PRE_SCAN_HBLANK							(0x1fff<<0)
#define m_PRE_SCAN_HACTIVE       					(0x1fff<<16)

#define v_DSP_BG_BLUE(x) 							(((x)&0x3ff)<<  0)
#define v_DSP_BG_GREEN(x)							(((x)&0x3ff)<< 10)
#define v_DSP_BG_RED(x)  							(((x)&0x3ff)<< 20)
#define v_DSP_WIN_BYPASS(x)                         (((x)&0x1  )<< 31)
#define m_DSP_BG_BLUE        	    				(0x3ff <<  0)
#define m_DSP_BG_GREEN      	    				(0x3ff << 10)
#define m_DSP_BG_RED        	    				(0x3ff << 20)
#define m_DSP_WIN_BYPASS                            (0x1   << 31)

//POST0_DSP_HACT_INFO
#define v_DSP_HACT_END_POST(x)						(((x)&0x7fff)<<0)
#define v_DSP_HACT_ST_POST(x)						(((x)&0x7fff)<<16)
#define m_DSP_HACT_END_POST							(0x7fff<<0)
#define m_DSP_HACT_ST_POST							(0x7fff<<16)

//POST0_DSP_VACT_INFO
#define v_DSP_VACT_END_POST(x)						(((x)&0x7fff)<<0)
#define v_DSP_VACT_ST_POST(x)						(((x)&0x7fff)<<16)
#define m_DSP_VACT_END_POST							(0x7fff<<0)
#define m_DSP_VACT_ST_POST							(0x7fff<<16)

//POST0_SCL_FACTOR_YRGB
#define v_POST_HS_FACTOR_YRGB(x)					(((x)&0xffff)<<0)
#define v_POST_VS_FACTOR_YRGB(x)					(((x)&0xffff)<<16)
#define m_POST_HS_FACTOR_YRGB						(0xffff<<0)
#define m_POST_VS_FACTOR_YRGB						(0xffff<<16)

//#define POST_SCL_FACTOR_CBR
#define v_POST_HS_FACTOR_CBR(x)						(((x)&0xffff)<<0)
#define v_POST_VS_FACTOR_CBR(x)						(((x)&0xffff)<<0)
#define m_POST_HS_FACTOR_CBR						(0xffff<<0)
#define m_POST_VS_FACTOR_CBR						(0xffff<<0)

//POST0_SCL_CTRL
#define v_POST_HOR_SD_EN(x)        					(((x)&1)<<0)
#define v_POST_VER_SD_EN(x)        					(((x)&1)<<1)
#define v_POST_DSP_RGB_YUV(x)      					(((x)&1)<<2)
#define v_POST_VER_SD_DLY_EN(x)      				(((x)&1)<<4)
#define v_POST_POST_CHEATING_EN(x)      			(((x)&1)<<5)
#define v_POST_SHARP_CHEATING_EN(x)      			(((x)&1)<<6)
#define v_POST_CRC_EN(x)                            (((x)&1)<<8)
#define v_POST_CRC_CHECK_EN(x)                      (((x)&1)<<9)

#define m_POST_HOR_SD_EN	    					(0x1<<0)
#define m_POST_VER_SD_EN	    					(0x1<<1)
#define m_POST_DSP_RGB_YUV      					(0x1<<2)
#define m_POST_VER_SD_DLY_EN      					(0x1<<4)
#define m_POST_POST_CHEATING_EN      				(0x1<<5)
#define m_POST_SHARP_CHEATING_EN      				(0x1<<6)
#define m_POST_CRC_EN                               (0x1<<8)
#define m_POST_CRC_CHECK_EN                         (0x1<<9)

//POST0_DSP_VACT_INFO_F1
#define v_DSP_VACT_END_POST(x)						(((x)&0x7fff)<<0)
#define v_DSP_VACT_ST_POST(x)             			(((x)&0x7fff)<<16)
#define m_DSP_VACT_END_POST                			(0x7fff<<0)
#define m_DSP_VACT_ST_POST                			(0x7fff<<16)

//POST0_DSP_HTOTAL_HS_END
#define v_DSP_HS_PW(x)            					(((x)&0xffff)<<0)
#define v_DSP_HTOTAL(x)            					(((x)&0xffff)<<16)
#define m_DSP_HS_PW	       							(0xffff<<0)
#define m_DSP_HTOTAL	        					(0xffff<<16)

//POST0_DSP_HTOTAL_HS_END
#define v_DSP_HACT_END(x)        					(((x)&0xffff)<<0)
#define v_DSP_HACT_ST(x)       						(((x)&0xffff)<<16)
#define m_DSP_HACT_END	        					(0xffff<<0)
#define m_DSP_HACT_ST	        					(0xffff<<16)


//POST0_DSP_VTOTAL_VS_END
#define v_DSP_VS_PW(x)            					(((x)&0x7fff)<<0)
#define v_DSP_VTOTAL(x)            					(((x)&0x7fff)<<16)
#define m_DSP_VS_PW	        						(0x7fff<<0)
#define m_DSP_VTOTAL	        					(0x7fff<<16)


//POST0_DSP_WIN_VACT_ST_END
#define v_DSP_VACT_END(x)        					(((x)&0x7fff)<<0)
#define v_DSP_VACT_ST(x)        					(((x)&0x7fff)<<16)
#define m_DSP_VACT_END	        					(0x7fff<<0)
#define m_DSP_VACT_ST	        					(0x7fff<<16)


//POST0_DSP_VS_ST_END_F1
#define v_DSP_VS_END_F1(x)        					(((x)&0x7fff)<<0)
#define v_DSP_VS_ST_F1(x)        					(((x)&0x7fff)<<16)
#define m_DSP_VS_END_F1	        					(0x7fff<<0)
#define m_DSP_VS_ST_F1	        					(0x7fff<<16)


//POST0_DSP_VACT_ST_END_F1
#define v_DSP_VACT_END_F1(x)        				(((x)&0x7fff)<<0)
#define v_DSP_VACT_ST_F1(x)        					(((x)&0x7fff)<<16)
#define m_DSP_VACT_END_F1	    					(0x7fff<<0)
#define m_DSP_VACT_ST_F1	        				(0x7fff<<16)

//POST0_BCSH_CTRL
#define   m_BCSH_Y2R_EN        						(1<<0)
#define   m_BCSH_Y2R_CSC_MODE  						(3<<2)
#define   m_BCSH_R2Y_EN        						(1<<4)
#define   m_BCSH_R2Y_CSC_MODE  						(3<<6)

#define   v_BCSH_Y2R_EN(x)        					(((x)&0x1)<<0)
#define   v_BCSH_Y2R_CSC_MODE(x)  					(((x)&0x3)<<2)
#define   v_BCSH_R2Y_EN(x)        					(((x)&0x1)<<4)
#define   v_BCSH_R2Y_CSC_MODE(x)  					(((x)&0x3)<<6)

//POST0_BCSH_COLOR_BAR
#define v_BCSH_EN(x)            					(((x)&0x1)<<31)
#define v_BCSH_COLOR_BAR_Y(x)       		 		(((x)&0x03ff)<<0)
#define v_BCSH_COLOR_BAR_U(x)        				(((x)&0x03ff)<<10)
#define v_BCSH_COLOR_BAR_V(x)        				(((x)&0x03ff)<<20)
#define v_BCSH_COLOR_BAR_Y_8bit(x)       		 	(((x)&0xff)<<0)
#define v_BCSH_COLOR_BAR_U_8bit(x)        			(((x)&0xff)<<8)
#define v_BCSH_COLOR_BAR_V_8bit(x)        			(((x)&0xff)<<16)
#define m_BCSH_EN	        						(1<<31)
#define m_BCSH_COLOR_BAR_Y	    					(0x03ff<<0)
#define m_BCSH_COLOR_BAR_U	    					(0x03ff<<10)
#define m_BCSH_COLOR_BAR_V	    					(0x03ff<<20)
#define m_BCSH_COLOR_BAR_Y_8bit	    				(0xff<<0)
#define m_BCSH_COLOR_BAR_U_8bit	    				(0xff<<8)
#define m_BCSH_COLOR_BAR_V_8bit	    				(0xff<<16)

//POST0_BCSH_BCS
#define v_BCSH_BRIGHTNESS(x)        				(((x)&0xff)<<0)
#define v_BCSH_CONTRAST(x)       					(((x)&0x1ff)<<8)
//Bit[19:17]ReseRved
#define v_BCSH_SAT_CON(x)       					(((x)&0x3ff)<<20)
#define v_BCSH_OUT_MODE(x)        					(((x)&0x3)<<30)
#define m_BCSH_BRIGHTNESS	    					(0xff<<0)
#define m_BCSH_CONTRAST	        					(0x1ff<<8)
//Bit[19:17]ReseRved
#define m_BCSH_SAT_CON	        					(0x3ff<<20)
#define m_BCSH_OUT_MODE	        					(3<<30)


//POST0_BCSH_H
#define v_BCSH_SIN_HUE(x)        					(((x)&0x1ff)<<0)
//Bit[15:9]ReseRved
#define v_BCSH_COS_HUE(x)        					(((x)&0x1ff)<<16)
#define m_BCSH_SIN_HUE	        					(0x1ff<<0)
#define m_BCSH_COS_HUE	       						(0x1ff<<16)

//POST0_CABC_CTRL0
#define v_CABC_EN(x)								(((x)&1)<<0)
#define v_CABC_HANDLE_EN(x)							(((x)&1)<<3)
#define v_PWM_CONFIG_MODE(x)	        			(((x)&0x3)<<1)
#define v_CABC_CALC_PIXEL_NUM(x)					(((x)&0x7fffff)<<4)
#define m_CABC_EN									(1<<0)
#define m_CABC_HANDLE_EN							(1<<3)
#define m_PWM_CONFIG_MODE    						(0x3<<1)
#define m_CABC_CALC_PIXEL_NUM						(0x7fffff<<4)

//POST0_CABC_CTRL1
#define v_CABC_LUT_EN(x)	        				(((x)&1)<<0)
#define v_CABC_TOTAL_PIXEL_NUM(x)					(((x)&0x7fffff)<<4)
#define m_CABC_LUT_EN								(1<<0)
#define m_CABC_TOTAL_PIXEL_NUM						(0x7fffff<<4)

//POST0_CABC_CTRL2
#define v_CABC_STAGE_DOWN(x)	        			(((x)&0xff)<<0)
#define v_CABC_STAGE_UP(x)							(((x)&0x1ff)<<8)
#define v_CABC_STAGE_UP_MODE(x)						(((x)&0x1)<<19)
#define v_MAX_SCALE_CFG_VALUE(x)        			(((x)&0x1ff)<<20)
#define v_MAX_SCALE_CFG_ENABLE(x)       			(((x)&0x1ff)<<31)
#define m_CABC_STAGE_DOWN							(0xff<<0)
#define m_CABC_STAGE_UP								(0x1ff<<8)
#define m_CABC_STAGE_UP_MODE						(0x1<<19)
#define m_MAX_SCALE_CFG_VALUE           			(0x1ff<<20)
#define m_MAX_SCALE_CFG_ENABLE         				(0x1ff<<31)

//POST0_CABC_CTRL3
#define v_CABC_GLOBAL_DN(x)            				(((x)&0xff)<<0)
#define v_CABC_GLOBAL_DN_LIMIT_EN(x)   				(((x)&0x1)<<8)
#define m_CABC_GLOBAL_DN               				(0xff<<0)
#define m_CABC_GLOBAL_DN_LIMIT_EN      				(0x1<<8)

//POST0_CABC_GAUSS_LINE0_0
#define v_CABC_T_LINE0_0(x)        					(((x)&0xff)<<0)
#define v_CABC_T_LINE0_1(x)        					(((x)&0xff)<<8)
#define v_CABC_T_LINE0_2(x)        					(((x)&0xff)<<16)
#define v_CABC_T_LINE0_3(x)        					(((x)&0xff)<<24)
#define m_CABC_T_LINE0_0	    					(0xff<<0)
#define m_CABC_T_LINE0_1	    					(0xff<<8)
#define m_CABC_T_LINE0_2	    					(0xff<<16)
#define m_CABC_T_LINE0_3	    					((u32)0xff<<24)

//POST0_CABC_GAUSS_LINE0_1
#define v_CABC_T_LINE0_4(x)        					(((x)&0xff)<<0)
#define v_CABC_T_LINE0_5(x)        					(((x)&0xff)<<8)
#define v_CABC_T_LINE0_6(x)        					(((x)&0xff)<<16)
#define m_CABC_T_LINE0_4	    					(0xff<<0)
#define m_CABC_T_LINE0_5	    					(0xff<<8)
#define m_CABC_T_LINE0_6	    					(0xff<<16)


//POST0_CABC_GAUSS_LINE1_0
#define v_CABC_T_LINE1_0(x)        					(((x)&0xff)<<0)
#define v_CABC_T_LINE1_1(x)        					(((x)&0xff)<<8)
#define v_CABC_T_LINE1_2(x)        					(((x)&0xff)<<16)
#define v_CABC_T_LINE1_3(x)        					(((x)&0xff)<<24)
#define m_CABC_T_LINE1_0	    					(0xff<<0)
#define m_CABC_T_LINE1_1	    					(0xff<<8)
#define m_CABC_T_LINE1_2	    					(0xff<<16)
#define m_CABC_T_LINE1_3	    					((u32)0xff<<24)

//POST0_CABC_GAUSS_LINE1_1
#define v_CABC_T_LINE1_4(x)        					(((x)&0xff)<<0)
#define v_CABC_T_LINE1_5(x)        					(((x)&0xff)<<8)
#define v_CABC_T_LINE1_6(x)        					(((x)&0xff)<<16)
#define m_CABC_T_LINE1_4	    					(0xff<<0)
#define m_CABC_T_LINE1_5	    					(0xff<<8)
#define m_CABC_T_LINE1_6	    					(0xff<<16)

//POST0_CABC_GAUSS_LINE2_0
#define v_CABC_T_LINE2_0(x)        					(((x)&0xff)<<0)
#define v_CABC_T_LINE2_1(x)        					(((x)&0xff)<<8)
#define v_CABC_T_LINE2_2(x)        					(((x)&0xff)<<16)
#define v_CABC_T_LINE2_3(x)        					(((x)&0xff)<<24)
#define m_CABC_T_LINE2_0	    					(0xff<<0)
#define m_CABC_T_LINE2_1	    					(0xff<<8)
#define m_CABC_T_LINE2_2	    					(0xff<<16)
#define m_CABC_T_LINE2_3	    					((u32)0xff<<24)

//POST0_CABC_GAUSS_LINE2_1
#define v_CABC_T_LINE2_4(x)        					(((x)&0xff)<<0)
#define v_CABC_T_LINE2_5(x)        					(((x)&0xff)<<8)
#define v_CABC_T_LINE2_6(x)        					(((x)&0xff)<<16)
#define m_CABC_T_LINE2_4	    					(0xff<<0)
#define m_CABC_T_LINE2_5	    					(0xff<<8)
#define m_CABC_T_LINE2_6	    					(0xff<<16)

//POST0_FRC_LOWER01_0
#define v_FRC_LOWER01_FRM0(x)        				(((x)&0xffff)<<0)
#define v_FRC_LOWER01_FRM1(x)        				(((x)&0xffff)<<16)
#define m_FRC_LOWER01_FRM0	   						(0xffff<<0)
#define m_FRC_LOWER01_FRM1	   						((u32)0xffff<<16)

//POST0_FRC_LOWER01_1
#define v_FRC_LOWER01_FRM2(x)        				(((x)&0xffff)<<0)
#define v_FRC_LOWER01_FRM3(x)        				(((x)&0xffff)<<16)
#define m_FRC_LOWER01_FRM2	    					(0xffff<<0)
#define m_FRC_LOWER01_FRM3	    					((u32)0xffff<<16)


//POST0_FRC_LOWER10_0
#define v_FRC_LOWER10_FRM0(x)        				(((x)&0xffff)<<0)
#define v_FRC_LOWER10_FRM1(x)        				(((x)&0xffff)<<16)
#define m_FRC_LOWER10_FRM0	    					(0xffff<<0)
#define m_FRC_LOWER10_FRM1	    					((u32)0xffff<<16)


//POST0_FRC_LOWER10_1
#define v_FRC_LOWER10_FRM2(x)        				(((x)&0xffff)<<0)
#define v_FRC_LOWER10_FRM3(x)        				(((x)&0xffff)<<16)
#define m_FRC_LOWER10_FRM2	    					(0xffff<<0)
#define m_FRC_LOWER10_FRM3	    					((u32)0xffff<<16)


//POST0_FRC_LOWER11_0
#define v_FRC_LOWER11_FRM0(x)        				(((x)&0xffff)<<0)
#define v_FRC_LOWER11_FRM1(x)        				(((x)&0xffff)<<16)
#define m_FRC_LOWER11_FRM0	    					(0xffff<<0)
#define m_FRC_LOWER11_FRM1	    					((u32)0xffff<<16)


//POST0_FRC_LOWER11_1
#define v_FRC_LOWER11_FRM2(x)        				(((x)&0xffff)<<0)
#define v_FRC_LOWER11_FRM3(x)        				(((x)&0xffff)<<16)
#define m_FRC_LOWER11_FRM2	    					(0xffff<<0)
#define m_FRC_LOWER11_FRM3	    					((u32)0xffff<<16)
//#define FRC_RESERVED0	    						(0x01f8)
//#define FRC_RESERVED1	    						(0x01fc)


//PWM ReGisteR
//POST0_PWM_CTRL
#define v_PWM_EN(x)            						(((x)&1)<<0)
#define v_PWM_MODE(x)                				(((x)&3)<<1)
#define v_PWM_DUTY_POL(x)                			(((x)&1)<<3)
#define v_PWM_INACTIVE_POL(x)        				(((x)&1)<<4)
#define v_PWM_OUTPUT_MODE(x)        				(((x)&1)<<5)
#define v_PWM_BL_EN(x)            					(((x)&1)<<8)
#define v_PWM_CLK_SEL(x)                			(((x)&1)<<9)
#define v_PWM_PRESCALE(x)                			(((x)&7)<<12)
#define v_PWM_SCALE(x)            					(((x)&0xff)<<16)
#define v_PWM_RPT(x)            					(((x)&0xff)<<24)

#define m_PWM_EN	        						(0x1<<0)
#define m_PWM_MODE	        						(0x3<<1)
#define m_PWM_DUTY_POL	        					(0x1<<3)
#define m_PWM_INACTIVE_POL	            			(0x1<<4)
#define m_PWM_OUTPUT_MODE	            			(0x1<<5)
#define m_PWM_BL_EN	                				(0x1<<8)
#define m_PWM_CLK_SEL	        					(0x1<<9)
#define m_PWM_PRESCALE	        					(0x7<<12)
#define m_PWM_SCALE									(0xff<<16)
#define m_PWM_RPT									(0xff<<24)


#define v_PWM_PERIOD_HPR(x)							(((x)&0xffffffff)<<0)
#define m_PWM_PERIOD_HPR							(0xffffffff<<0)
//new add ----------------
#define v_ACM_R2Y_EN(x)                             (((x)&0x1)<<1 )
#define v_ACM_R2Y_MODE(x)                           (((x)&0x7)   <<4 )
#define v_ACM_R2Y_COE_LOW(x)                        (((x)&0xffff)<<0 )
#define v_ACM_R2Y_COE_HIG(x)                        (((x)&0xffff)<<16)
#define v_ACM_R2Y_OFFSET0(x)                        (((x)&0xffffffff)<<0)
#define v_ACM_R2Y_OFFSET1(x)                        (((x)&0xffffffff)<<0)
#define v_ACM_R2Y_OFFSET2(x)                        (((x)&0xffffffff)<<0)


#define m_ACM_R2Y_EN                                ((0x1       )<<1 )
#define m_ACM_R2Y_MODE                              ((0x7       )<<4 )
#define m_ACM_R2Y_COE_LOW                           ((0xffff    )<<0 )
#define m_ACM_R2Y_COE_HIG                           ((0xffff    )<<16)
#define m_ACM_R2Y_OFFSET0                           ((0xffffffff)<<0 )
#define m_ACM_R2Y_OFFSET1                           ((0xffffffff)<<0 )
#define m_ACM_R2Y_OFFSET2                           ((0xffffffff)<<0 )

//DB_DITHER
#define v_FRC_DITHER_MODE(x)                        (((x)&0x3)   <<0 )
#define v_FRC_RCR_PATTERN(x)                        (((x)&0x3)   <<2 )
#define v_FRC_GY_PATTERN(x)                         (((x)&0x3)   <<4 )
#define v_FRC_BCB_PATTERN(x)                        (((x)&0x3)   <<6 )
#define m_FRC_DITHER_MODE                           (    (0x3)   <<0 )
#define m_FRC_RCR_PATTERN                           (    (0x3)   <<2 )
#define m_FRC_GY_PATTERN                            (    (0x3)   <<4 )
#define m_FRC_BCB_PATTERN                           (    (0x3)   <<6 )


#define v_FRC_RCR_STRENGTH(x)                       (((x)&0x3ff) <<0 )
#define v_FRC_GY_STRENGTH(x)                        (((x)&0x3ff) <<16)
#define v_FRC_BCB_STRENGTH(x)                       (((x)&0x3ff) <<0 )

#define m_FRC_RCR_STRENGTH                          ((0x3ff) <<0 )
#define m_FRC_GY_STRENGTH                           ((0x3ff) <<16)
#define m_FRC_BCB_STRENGTH                          ((0x3ff) <<0 )


#define v_FRC_RANGE_SCA(x)                          (((x)&0x3fff)<<16)
#define m_FRC_RANGE_SCA                             (    (0x3fff)<<16)

//-----------------
#define v_ACM_BYPASS(x)            				     	(((x)&1)<<0)
#define v_ACM_EN(x)            				     		(((x)&1)<<12)
#define v_ACM_Y2R_EN(x)            						(((x)&1)<<1)
#define v_ACM_Y2R_MODE(x)                				(((x)&7)<<4)
#define v_ACM_Y2R_COE00(x)                				(((x)&0xffff)<<16)
#define v_ACM_Y2R_COE01(x)                				(((x)&0xffff)<<0)
#define v_ACM_Y2R_COE02(x)                				(((x)&0xffff)<<16)
#define v_ACM_Y2R_COE10(x)                				(((x)&0xffff)<<0)
#define v_ACM_Y2R_COE11(x)                				(((x)&0xffff)<<16)
#define v_ACM_Y2R_COE12(x)                				(((x)&0xffff)<<0)
#define v_ACM_Y2R_COE20(x)                				(((x)&0xffff)<<16)
#define v_ACM_Y2R_COE21(x)                				(((x)&0xffff)<<0)
#define v_ACM_Y2R_COE22(x)                				(((x)&0xffff)<<16)
#define v_ACM_Y2R_OFFSET0(x)                			(((x)&0xffffffff)<<0)
#define v_ACM_Y2R_OFFSET1(x)                			(((x)&0xffffffff)<<0)
#define v_ACM_Y2R_OFFSET2(x)                			(((x)&0xffffffff)<<0)

#define m_ACM_BYPASS            						(0x1<<0)
#define m_ACM_EN	             						(0x1<<12)
#define m_ACM_Y2R_EN	        						(0x1<<1)
#define m_ACM_Y2R_MODE	        						(0x7<<4)

#define m_ACM_Y2R_COE00                                 (0xffff<<16)
#define m_ACM_Y2R_COE01                                 (0xffff<<0)
#define m_ACM_Y2R_COE02                                 (0xffff<<16)
#define m_ACM_Y2R_COE10                                 (0xffff<<0)
#define m_ACM_Y2R_COE11                                 (0xffff<<16)
#define m_ACM_Y2R_COE12                                 (0xffff<<0)
#define m_ACM_Y2R_COE20                                 (0xffff<<16)
#define m_ACM_Y2R_COE21                                 (0xffff<<0)
#define m_ACM_Y2R_COE22                                 (0xffff<<16)
#define m_ACM_Y2R_OFFSET0                               (0xffffffff<<0)
#define m_ACM_Y2R_OFFSET1                               (0xffffffff<<0)
#define m_ACM_Y2R_OFFSET2                               (0xffffffff<<0)

//------------------------------------------------------------------------------
//HDR10 0x2000
#define v_HDR10_LUT_UPDATE_EN(x)            				(((x)&1)<<0)
#define v_HDR10_LUT_UPDATE_MODE(x)                			(((x)&1)<<1)

#define m_HDR10_LUT_UPDATE_EN          						(0x1<<0)
#define m_HDR10_LUT_UPDATE_MODE       						(0x1<<1)

#define v_HDR10_LUT_MST(x)            				(((x)&0xffffffff)<<0)
#define m_HDR10_LUT_MST       						(0xffffffff<<0)

#define v_SDR2HDR_EOTF_EN(x)        					(((x)&0x1)<<0)
#define v_SDR2HDR_R2R_EN(x)       						(((x)&0x1)<<1)
#define v_SDR2HDR_R2R_MODE(x)     						(((x)&0x1)<<2)
#define v_SDR2HDR_OETF_EN(x)       				        (((x)&0x1)<<3)
#define v_SDR2HDR_BYPASS_EN(x)       				    (((x)&0x1)<<8)
#define v_SDR2HDR_GATING_EN(x)       				    (((x)&0x1)<<9)

#define m_SDR2HDR_EOTF_EN        					(0x1<<0)
#define m_SDR2HDR_R2R_EN       						(0x1<<1)
#define m_SDR2HDR_R2R_MODE     						(0x1<<2)
#define m_SDR2HDR_OETF_EN       				    (0x1<<3)
#define m_SDR2HDR_BYPASS_EN       				    (0x1<<8)
#define m_SDR2HDR_GATING_EN       				    (0x1<<9)

#define v_HDR2SDR_EN(x)        					        (((x)&0x1)<<0)
#define v_HDR2SDR_BYPASS_EN(x)       				    (((x)&0x1)<<8)
#define v_HDR2SDR_GATING_EN(x)       				    (((x)&0x1)<<9)
#define m_HDR2SDR_EN        					    (0x1<<0)
#define m_HDR2SDR_BYPASS_EN       				    (0x1<<8)
#define m_HDR2SDR_GATING_EN       				    (0x1<<9)

#define v_HDR2SDR_SRC_MAX(x)        				(((x)&0x3fff)<<16)
#define v_HDR2SDR_SRC_MIN(x)        				(((x)&0x3fff)<<0)
#define m_HDR2SDR_SRC_MAX        					(0x3fff<<16)
#define m_HDR2SDR_SRC_MIN        					(0x3fff<<0)

#define v_HDR2SDR_NORMFACEETF(x)        		    (((x)&0xfff)<<0)
#define m_HDR2SDR_NORMFACEETF        				(0xfff<<0)

#define v_HDR2SDR_DST_MAX(x)        				(((x)&0xffff)<<16)
#define v_HDR2SDR_DST_MIN(x)        				(((x)&0xffff)<<0)
#define m_HDR2SDR_DST_MAX        					(0xffff<<16)
#define m_HDR2SDR_DST_MIN        					(0xffff<<0)

#define v_HDR2SDR_NORMFACGAMMA(x)        		    (((x)&0xffff)<<0)
#define m_HDR2SDR_NORMFACGAMMA        				(0xffff<<0)


#define v_HDR2SDR_BT1886OETF_Y(x)        		(((x)&0x3fff)<<16)
#define v_HDR2SDR_EETF_Y(x)        		        (((x)&0x3fff)<<0)
#define m_HDR2SDR_BT1886OETF_Y        			(0x3fff<<16)
#define m_HDR2SDR_EETF_Y        				(0x3fff<<0)

#define v_HDR2SDR_SAT_Y(x)        		        (((x)&0x3fff)<<0)
#define m_HDR2SDR_SAT_Y        				    (0x3fff<<0)

#define v_SDR2HDR_ST2084OETF_Y(x)        		(((x)&0x3fff)<<18)
#define v_SDR2HDR_BT1886EOTF_Y(x)        		(((x)&0x3ffff)<<0)
#define m_SDR2HDR_ST2084OETF_Y       			(0x3fff<<18)
#define m_SDR2HDR_BT1886EOTF_Y 			    	(0x3ffff<<0)

#define v_SDR2HDR_ST2084OETF_DXPOW(x)        	(((x)&0xf)<<16)
#define v_SDR2HDR_ST2084OETF_DX(x)        		(((x)&0xffff)<<0)
#define m_SDR2HDR_ST2084OETF_DXPOW   			(0xf<<16)
#define m_SDR2HDR_ST2084OETF_DX       			(0xffff<<0)

#define v_SDR2HDR_ST2084OETF_X(x)        		(((x)&0x7ffff)<<0)
#define m_SDR2HDR_ST2084OETF_X       			(0x7ffff<<0)

//NVR reg define
#define NVR_WIN_CTRL        0       //0x0000
#define NVR_AXI_CTRL        1       //0x0004
#define NVR_ALPHA_VP        2       //0x0008
#define NVR_REGION_MST      3       //0x000c
#define NVR_SCL_CTRL        4       //0x0010
#define NVR_SCL_FACTOR_YRGB 5       //0x0014
#define NVR_CHKOUT_STATUS   6       //0x0018
#define NVR_ACT_INFO        7       //0x001c
#define NVR_DSP_INFO        8       //0x0020
#define NVR_DSP_OFFSET      9       //0X0024
#define NVR_DSP_BG          10      //0x0028
#define NVR_COLOR_KEY       11      //0x002c
#define NVR_CSC_COE00_01    12      //0x0030
#define NVR_CSC_COE02_10    13      //0x0034
#define NVR_CSC_COE11_12    14      //0x0038
#define NVR_CSC_COE20_21    15      //0x003c
#define NVR_CSC_COE22       16      //0x0040
#define NVR_CSC_COE_OFFSET0 17      //0x0044
#define NVR_CSC_COE_OFFSET1 18      //0x0048
#define NVR_CSC_COE_OFFSET2 19      //0x004c


#define  NVR_WIN_REGION_YRGB_MST   20
#define  NVR_WIN_REGION_CBCR_MST   21
#define  NVR_WIN_REGION_VIR        22
#define  NVR_WIN_REGION_ACT_INFO   23
#define  NVR_WIN_REGION_ACT_OFFSET 24
#define  NVR_WIN_REGION_DSP_OFFSET 25

//
#define  NVR0_REGION_BASE      0
#define  NVR1_REGION_BASE      384
//nvr win info
#define  WIN_REGION_YRGB_MST   0
#define  WIN_REGION_CBCR_MST   1
#define  WIN_REGION_VIR        2
#define  WIN_REGION_ACT_INFO   3
#define  WIN_REGION_ACT_OFFSET 4
#define  WIN_REGION_DSP_OFFSET 5

//NVR_WIN_CTRL
#define m_WIN_EN                                (0x0  << 0)
#define m_WIN_DATA_FMT                          (0x3f << 1)
#define m_WIN_TILE_MODE                         (0x1  << 7)
#define m_WIN_CSC_Y2R_EN                        (0x1  << 8)
#define m_WIN_CSC_R2Y_EN                        (0x1  << 9)
#define m_WIN_CSC_MODE                          (0x3  << 10)
#define m_WIN_DATA_FMT_SEL                      (0x1  << 13)
#define m_WIN_RB_SWAP                           (0x1  << 14)
#define m_WIN_ALPHA_SWAP                        (0x1  << 15)
#define m_WIN_CONFIG_RAM_DEBUG                  (0x1  << 16)
#define m_WIN_UV_SWAP                           (0x1  << 17)
#define m_WIN_DITHER_UP_EN                      (0x1  << 18)
#define m_WIN_YUV_CLIP                          (0x1  << 19)
#define m_WIN_LINE_Y_MIR                        (0x1  << 21)
#define m_WIN_MID_SWAP                          (0X1  << 22)
#define m_WIN_ENDIAN_SWAP                       (0X1  << 23)
#define m_WIN_NVR_EN                            (0X1  << 24)
#define m_WIN_CHECH_EN                          (0X1  << 25)
#define m_WIN_NUM                               (0X3f << 26)

#define v_WIN_EN(x)                             (((x) & 0x1  ) << 0)
#define v_WIN_DATA_FMT(x)                       (((x) & 0x3f ) << 1)
#define v_WIN_TILE_MODE(x)                      (((x) & 0x1  ) << 7)
#define v_WIN_CSC_Y2R_EN(x)                     (((x) & 0x1  ) << 8)
#define v_WIN_CSC_R2Y_EN(x)                     (((x) & 0x1  ) << 9)
#define v_WIN_CSC_MODE(x)                       (((x) & 0x3  ) << 10)
#define v_WIN_DATA_FMT_SEL(x)                   (((x) & 0x1  ) << 13)
#define v_WIN_RB_SWAP(x)                        (((x) & 0x1  ) << 14)
#define v_WIN_ALPHA_SWAP(x)                     (((x) & 0x1  ) << 15)
#define v_WIN_CONFIG_RAM_DEBUG(x)               (((x) & 0x1  ) << 16)
#define v_WIN_UV_SWAP(x)                        (((x) & 0x1  ) << 17)
#define v_WIN_DITHER_UP_EN(x)                   (((x) & 0x1  ) << 18)
#define v_WIN_YUV_CLIP(x)                       (((x) & 0x1  ) << 19)
#define v_WIN_LINE_Y_MIR(x)                     (((x) & 0x1  ) << 21)
#define v_WIN_MID_SWAP(x)                       (((x) & 0X1  ) << 22)
#define v_WIN_ENDIAN_SWAP(x)                    (((x) & 0X1  ) << 23)
#define v_WIN_NVR_EN(x)                         (((x) & 0X1  ) << 24)
#define v_WIN_CHECH_EN(x)                       (((x) & 0X1  ) << 25)
#define v_WIN_NUM(x)                            (((x) & 0X3f ) << 26)

//NVR_AXI_CTRL
#define m_WIN_YRGB_GATHER_EN                    (0x1  << 0)
#define m_WIN_YRGB_GATHER_NUM                   (0x3  << 1)
#define m_WIN_CBCR_GATHER_EN                    (0x1  << 4)
#define m_WIN_CBCR_GATHER_NUM                   (0x3  << 5)
#define m_WIN_RID_YRGB                          (0x1f << 8)
#define m_WIN_RID_CBCR                          (0x1f << 16)
#define m_WIN_AXI_SEL                           (0x1  << 21)
#define m_WIN_DMA_STOP                          (0x1  << 24)
#define m_WIN_AUTO_GATING                       (0x1  << 25)
#define m_WIN_SOFT_RESET                        (0x1  << 27)
#define m_WIN_SCL_NUM                           (0x3  << 28)
#define m_WIN_MEMORY_AUTO_GATING                (0x1  << 31)

#define v_WIN_YRGB_GATHER_EN(x)                 (((x) & 0x1 ) << 0)
#define v_WIN_YRGB_GATHER_NUM(x)                (((x) & 0x3 ) << 1)
#define v_WIN_CBCR_GATHER_EN(x)                 (((x) & 0x1 ) << 4)
#define v_WIN_CBCR_GATHER_NUM(x)                (((x) & 0x3 ) << 5)
#define v_WIN_RID_YRGB(x)                       (((x) & 0x1f) << 8)
#define v_WIN_RID_CBCR(x)                       (((x) & 0x1f) << 16)
#define v_WIN_AXI_SEL(x)                        (((x) & 0x1 ) << 21)

#define v_WIN_DMA_STOP(x)                       (((x) & 0x1 ) << 24)
#define v_WIN_AUTO_GATING(x)                    (((x) & 0x1 ) << 25)
#define v_WIN_SOFT_RESET(x)                     (((x) & 0x1 ) << 27)
#define v_WIN_SCL_NUM(x)                        (((x) & 0x3 ) << 28)
#define v_WIN_MEMORY_AUTO_GATING(x)             (((x) & 0x1 ) << 31)
//NVR_ALPHA
#define m_WIN_ALPHA_0                           (0xff << 0)
#define m_WIN_ALPHA_1                           (0xff << 8)
#define m_WIN_ALPHA_MAPPING_EN                  (0x1  << 16)
#define m_WIN_DLY_NUM                           (0xff << 20)
#define m_WIN_POST_SEL                          (0x3  << 28)
#define v_WIN_ALPHA_0(x)                        (((x) & 0xff ) << 0)
#define v_WIN_ALPHA_1(x)                        (((x) & 0xff ) << 8)
#define v_WIN_ALPHA_MAPPING_EN(x)               (((x) & 0x1  ) << 16)
#define v_WIN_DLY_NUM(x)                        (((x) & 0xff ) << 20)
#define v_WIN_POST_SEL(x)                       (((x) & 0x3  ) << 28)

//NVR_REGION_MST
#define m_WIN_REGION_CONFIG_MST                 (0xffffffff << 0)
#define v_WIN_REGION_CONFIG_MST(x)              (((x) & 0xffffffff) << 0)

//NVR_SCL_CTRL
#define m_WIN_VER_SCL_UP                        (0x1  << 0)
#define m_WIN_VER_SCL_DN                        (0x1  << 1)
#define m_WIN_VER_FILTER_MODE                   (0x3  << 2)
#define m_WIN_VSD_AVG2                          (0x1  << 4)
#define m_WIN_VSD_AVG4                          (0x1  << 5)
#define m_WIN_HOR_SCL_UP                        (0x1  << 8)
#define m_WIN_HOR_SCL_DN                        (0x1  << 9)
#define m_WIN_HOR_FILTER_MODE                   (0x3  << 10)
#define m_WIN_XGT_EN                            (0x1  << 12)
#define m_WIN_XGT_MODE                          (0x3  << 13)
#define m_WIN_XAVG_EN                           (0x1  << 15)
#define m_WIN_YRGB_VSD_GT2                      (0x1  << 16)
#define m_WIN_YRGB_VSD_GT4                      (0x1  << 17)
#define m_WIN_CBCR_VSD_GT2                      (0x1  << 18)
#define m_WIN_CBCR_VSD_GT4                      (0x1  << 19)
#define m_WIN_BIC_MODE                          (0x3  << 20)

#define v_WIN_VER_SCL_UP(x)                     (((x) & 0x1 ) << 0)
#define v_WIN_VER_SCL_DN(x)                     (((x) & 0x1 ) << 1)
#define v_WIN_VER_FILTER_MODE(x)                (((x) & 0x3 ) << 2)
#define v_WIN_VSD_AVG2(x)                       (((x) & 0x1 ) << 4)
#define v_WIN_VSD_AVG4(x)                       (((x) & 0x1 ) << 5)
#define v_WIN_HOR_SCL_UP(x)                     (((x) & 0x1 ) << 8)
#define v_WIN_HOR_SCL_DN(x)                     (((x) & 0x1 ) << 9)
#define v_WIN_HOR_FILTER_MODE(x)                (((x) & 0x3 ) << 10)
#define v_WIN_XGT_EN(x)                         (((x) & 0x1 ) << 12)
#define v_WIN_XGT_MODE(x)                       (((x) & 0x3 ) << 13)
#define v_WIN_XAVG_EN(x)                        (((x) & 0x1 ) << 15)
#define v_WIN_YRGB_VSD_GT2(x)                   (((x) & 0x1 ) << 16)
#define v_WIN_YRGB_VSD_GT4(x)                   (((x) & 0x1 ) << 17)
#define v_WIN_CBCR_VSD_GT2(x)                   (((x) & 0x1 ) << 18)
#define v_WIN_CBCR_VSD_GT4(x)                   (((x) & 0x1 ) << 19)
#define v_WIN_BIC_MODE(x)                       (((x) & 0x3 ) << 20)

//NVR_SCL_FACTOR
#define m_WIN_HS_FACTOR                         (0xffff << 0)
#define m_WIN_VS_FACTOR                         (0xffff << 16)
#define v_WIN_HS_FACTOR(x)                      (((x) & 0xffff ) << 0)
#define v_WIN_VS_FACTOR(x)                      (((x) & 0xffff ) << 16)
//NVR_ACT_INFO
//#define m_WIN_ACT_WIDTH                         (0x3fff << 0)
//#define m_WIN_ACT_HEIGHT                        (0x3fff << 16)
//
//#define v_WIN_ACT_WIDTH(x)                      (((x) & 0x3fff )_<< 0)
//#define v_WIN_ACT_HEIGHT(x)                     (((x) & 0x3fff )_<< 16)
//NVR_DSP_INFO
#define m_WIN_DSP_WIDTH                         (0x1fff << 0)
#define m_WIN_DSP_HEIGHT                        (0x1fff << 16)

#define v_WIN_DSP_WIDTH(x)                      (((x) & 0x1fff ) << 0)
#define v_WIN_DSP_HEIGHT(x)                     (((x) & 0x1fff ) << 16)
//NVR_DSP_OFFSET
#define m_WIN_DSP_XST                           (0x1fff << 0)
#define m_WIN_DSP_YST                           (0x1fff << 16)

#define v_WIN_DSP_XST(x)                        (((x) & 0x1fff ) << 0)
#define v_WIN_DSP_YST(x)                        (((x) & 0x1fff ) << 16)
//NVR_DSP_BG
#define m_WIN_DSP_BG_BLUE                       (0x3ff  << 0 )
#define m_WIN_DSP_BG_GREEN                      (0x3ff  << 10)
#define m_WIN_DSP_BG_RED                        (0x3ff  << 20)
#define m_WIN_DSP_BG_BYPASS_EN                  (0x1    << 30)
#define m_WIN_DSP_BG_ALPHA_FULL                 (0x1    << 31)

#define v_WIN_DSP_BG_BLUE(x)                    (((x) & 0x3ff ) <<  0)
#define v_WIN_DSP_BG_GREEN(x)                   (((x) & 0x3ff ) << 10)
#define v_WIN_DSP_BG_RED(x)                     (((x) & 0x3ff ) << 20)
#define v_WIN_DSP_BG_BYPASS_EN(x)               (((x) & 0x1   ) << 30)
#define v_WIN_DSP_BG_ALPHA_FULL(x)              (((x) & 0x1   ) << 31)
//NVR_COLOR_KEY
#define m_WIN_COLOR_BV                          (0x3ff  << 0)
#define m_WIN_COLOR_GU                          (0x3ff  << 10)
#define m_WIN_COLOR_RY                          (0x3ff  << 20)
#define m_WIN_COLOR_KEY_EN                      (0x1    << 31)

#define v_WIN_COLOR_BV(x)                       (((x) & 0x3ff ) << 0)
#define v_WIN_COLOR_GU(x)                       (((x) & 0x3ff ) << 10)
#define v_WIN_COLOR_RY(x)                       (((x) & 0x3ff ) << 20)
#define v_WIN_COLOR_KEY_EN(x)                   (((x) & 0x1   ) << 31)
//NVR_CSC_COE00_01/NVR_CSC_COE02_10/NVR_CSC_COE11_12/NVR_CSC_COE20_21/NVR_CSC_COE22
#define m_WIN_CSC_COE_LOW                       (0xffff <<  0)
#define m_WIN_CSC_COE_HIG                       (0xffff << 16)

#define v_WIN_CSC_COE_LOW(x)                    (((x) & 0xffff) <<  0)
#define v_WIN_CSC_COE_HIG(x)                    (((x) & 0xffff) << 16)
//NVR_CSC_COE_OFFSET0 /NVR_CSC_COE_OFFSET1 /NVR_CSC_COE_OFFSET2
#define m_WIN_CSC_OFFSET                       (0xffffffff <<  0)
#define v_WIN_CSC_OFFSET(x)                    (((x) & 0xffffffff) << 0)


//NVR_WIN_YRGB_MST
#define m_WIN_YRGB_MST                          (0xffffffff << 0)
#define v_WIN_YRGB_MST(x)                       (((x) & 0xffffffff ) << 0)
//NVR_WIN_CBCR_MST
#define m_WIN_CBCR_MST                          (0xffffffff << 0)
#define v_WIN_CBCR_MST(x)                       (((x) & 0xffffffff ) << 0)
//NVR_WIN_VIR
#define m_WIN_VIR_STRIDE                        (0xffff     << 0)
#define m_WIN_VIR_STRIDE_UV                     (0xffff     << 16)

#define v_WIN_VIR_STRIDE(x)                     (((x) & 0xffff ) << 0)
#define v_WIN_VIR_STRIDE_UV(x)                  (((x) & 0xffff ) << 16)
//NVR_WIN_ACT_INFO
#define m_WIN_ACT_WIDTH                         (0x1fff     << 0)
#define m_WIN_ACT_HEIGHT                        (0x1fff     << 16)

#define v_WIN_ACT_WIDTH(x)                      (((x) & 0x1fff ) << 0)
#define v_WIN_ACT_HEIGHT(x)                     (((x) & 0x1fff ) << 16)
//NVR_WIN_ACT_OFFSET
#define m_WIN_ACT_XOFFSET                       (0x3          <<  0)
#define m_WIN_ACT_YOFFSET                       (0x3          << 16)
#define v_WIN_ACT_XOFFSET(x)                    (((x) & 0x3 ) <<  0)
#define v_WIN_ACT_YOFFSET(x)                    (((x) & 0x3 ) << 16)
//NVR_WIN_DSP_OFFSET
#define m_WIN_DSP_XOFFSET                       (0x1fff     << 0)
#define m_WIN_DSP_YOFFSET                       (0x1fff     << 16)

#define v_WIN_DSP_XOFFSET(x)                    (((x) & 0x1fff) << 0)
#define v_WIN_DSP_YOFFSET(x)                    (((x) & 0x1fff) << 16)


//HWC
//HWC_CTRL0          0x0000
#define         v_HWC_CSC_EN(x)                 (((x)&0x1)<<0 )
#define         v_HWC_CSC_MODE(x)               (((x)&0x7)<<1 )
#define         v_HWC_FRM_RESET_EN(x)           (((x)&0x1)<<31)

#define         m_HWC_CSC_EN                    ((0x1)<<0 )
#define         m_HWC_CSC_MODE                  ((0x7)<<1 )
#define         m_HWC_FRM_RESET_EN              ((0x1)<<31)
//HWC_CTRL1          0x0004
#define         v_HWC_AXI_RLEN(x)               (((x)&0x3)<<0 )
#define         v_HWC_GATHER_EN(x)              (((x)&0x1)<<2 )
#define         v_HWC_RID(x)                    (((x)&0x1f)<<4 )
#define         v_HWC_GATHER_NUM(x)             (((x)&0xf)<<20)
#define         v_HWC_YMIR_EN(x)                (((x)&0x1)<<31)

#define         m_HWC_AXI_RLEN                  ((0x3)<<0 )
#define         m_HWC_GATHER_EN                 ((0x1)<<2 )
#define         m_HWC_RID                       ((0x1f)<<4 )
#define         m_HWC_GATHER_NUM                ((0xf)<<20)
#define         m_HWC_YMIR_EN                   ((0x1)<<31)
//HWC_AXI_CTRL_IMD   0x0008
#define         v_HWC_DMA_STOP(x)               (((x)&0x1)<<0 )
#define         v_HWC_AXI_SEL(x)                (((x)&0x1)<<1 )
#define         v_HWC_OUTSTANDING_EN(x)         (((x)&0x1)<<3 )
#define         v_HWC_OUTSTANDING_NUM(x)        (((x)&0xf)<<4 )
#define         v_HWC_AUTO_GATING_EN(x)         (((x)&0x1)<<8 )
#define         v_HWC_DMA_4K_OPT(x)             (((x)&0x1)<<16 )

#define         m_HWC_DMA_STOP                  ((   0x1)<<0 )
#define         m_HWC_AXI_SEL                   ((   0x1)<<1 )
#define         m_HWC_OUTSTANDING_EN            ((   0x1)<<3 )
#define         m_HWC_OUTSTANDING_NUM           ((   0xf)<<4 )
#define         m_HWC_AUTO_GATING_EN            ((   0x1)<<8 )
#define         m_HWC_DMA_4K_OPT                ((   0x1)<<16 )
//HWC_MST_CTRL       0x000c
#define         v_HWC_EN(x)                     (((x)&0x1 ) <<  0 )
#define         v_HWC_DATA_FMT(x)               (((x)&0xf ) <<  1 )
#define         v_HWC_ARGB5551_EN(x)            (((x)&0x1 ) <<  5 )
#define         v_HWC_DITHER_UP_EN(x)           (((x)&0x1 ) << 10 )
#define         v_HWC_ALPHA_SWAP(x)             (((x)&0x1 ) << 11 )
#define         v_HWC_RB_SWAP(x)                (((x)&0x1 ) << 12 )
#define         v_HWC_MID_SWAP(x)               (((x)&0x1 ) << 13 )
#define         v_HWC_RG_SWAP(x)                (((x)&0x1 ) << 14 )
#define         v_HWC_ALPHA_MAP_EN(x)           (((x)&0x1 ) << 15 )
#define         v_HWC_ALPHA_0_MAP(x)            (((x)&0xff) << 16 )
#define         v_HWC_ALPHA_1_MAP(x)            (((x)&0xff) << 24 )

#define         m_HWC_EN                        ((   0x1 ) <<  0 )
#define         m_HWC_DATA_FMT                  ((   0xf ) <<  1 )
#define         m_HWC_ARGB5551_EN               ((   0x1 ) <<  5 )
#define         m_HWC_DITHER_UP_EN              ((   0x1 ) << 10 )
#define         m_HWC_ALPHA_SWAP                ((   0x1 ) << 11 )
#define         m_HWC_RB_SWAP                   ((   0x1 ) << 12 )
#define         m_HWC_MID_SWAP                  ((   0x1 ) << 13 )
#define         m_HWC_RG_SWAP                   ((   0x1 ) << 14 )
#define         m_HWC_ALPHA_MAP_EN              ((   0x1 ) << 15 )
#define         m_HWC_ALPHA_0_MAP               ((   0xff) << 16 )
#define         m_HWC_ALPHA_1_MAP               ((   0xff) << 24 )
//HWC_MST            0x0010
#define         v_HWC_MST(x)                    (((x)&0xffffffff) << 0)
#define         m_HWC_MST                       ((    0xffffffff) << 0)
//HWC_VIR            0x0014
#define         v_HWC_VIR_WIDTH(x)              (((x)&0xffff) << 0)
#define         m_HWC_VIR_WIDTH                 ((    0xffff) << 0)
//HWC_SIZE_INFO      0x0018
#define         v_HWC_width(x)                  (((x)&0x1fff) << 0)
#define         v_HWC_height(x)                 (((x)&0x1fff) << 16)
#define         m_HWC_width                     ((    0x1fff) << 0)
#define         m_HWC_height                    ((    0x1fff) << 16)
//HWC_DSP_OFFSET     0x001c
#define         v_HWC_XOFFSET(x)                (((x)&0x1fff) << 0)
#define         v_HWC_YOFFSET(x)                (((x)&0x1fff) << 16)
#define         m_HWC_XOFFSET                   ((    0x1fff) << 0)
#define         m_HWC_YOFFSET                   ((    0x1fff) << 16)
//HWC_KEY_CTRL       0x0020
#define         v_HWC_KEY_EN(x)                 (((x)&0x3ff) <<30)
#define         v_HWC_R_KEY_VALUE(x)            (((x)&0x3ff) <<20)
#define         v_HWC_G_KEY_VALUE(x)            (((x)&0x3ff) <<10)
#define         v_HWC_B_KEY_VALUE(x)            (((x)&0x3ff) << 0)

#define         m_HWC_KEY_EN                    ((    0x3ff) <<30)
#define         m_HWC_R_KEY_VALUE               ((    0x3ff) <<20)
#define         m_HWC_G_KEY_VALUE               ((    0x3ff) <<10)
#define         m_HWC_B_KEY_VALUE               ((    0x3ff) << 0)
//HWC_BG_EN          0x0024
#define         v_HWC_BG_EN(x)                 (((x)&0x3ff) <<30)
#define         v_HWC_BG_R_VALUE(x)            (((x)&0x3ff) <<20)
#define         v_HWC_BG_G_VALUE(x)            (((x)&0x3ff) <<10)
#define         v_HWC_BG_B_VALUE(x)            (((x)&0x3ff) << 0)

#define         m_HWC_BG_EN                    ((    0x3ff) <<30)
#define         m_HWC_BG_R_VALUE               ((    0x3ff) <<20)
#define         m_HWC_BG_G_VALUE               ((    0x3ff) <<10)
#define         m_HWC_BG_B_VALUE               ((    0x3ff) << 0)
//HWC_PORT_SEL       0x0028
#define         v_HWC_PORT_SEL(x)              (((x)&0x3) << 0)
#define         m_HWC_PORT_SEL                 ((    0x3) << 0)
//HWC_DLY_NUM        0x002c
#define         v_HWC_DLY_NUM(x)               (((x)&0xff) << 0)
#define         m_HWC_DLY_NUM                  ((    0xff) << 0)


#define v_SW_HWC_CSC_COE_LOW(x)                      (((x)&0xffff)<<0 )
#define v_SW_HWC_CSC_COE_HIG(x)                      (((x)&0xffff)<<16)

#define m_SW_HWC_CSC_COE_LOW                         (0xffff      <<0 )
#define m_SW_HWC_CSC_COE_HIG                         (0xffff      <<16)

//0x134/0x138/0x13c
#define v_SW_HWC_CSC_OFFSET(x)                       (((x)&0xffffffff)<<0 )
#define m_SW_HWC_CSC_OFFSET                          (0xffffffff      <<0 )
#endif /* DRIVERS_TEST_VOP3_VOP3_H_ */
