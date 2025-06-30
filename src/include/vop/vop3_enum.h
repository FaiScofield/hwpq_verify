/*
 * vop3_em.h
 *
 *  Created on: 2021-9-7
 *      Author: rihui
 */

#include "./vop3_define.h"
#include "./vop3_typedef.h"
// #include "./typedef.h"
#ifdef VOP3_ROBIN
enum {
    DSP_PORT0         = 0 ,
    DSP_PORT1         = 1 ,
    DSP_PORT2         = 2 ,
    DSP_PORT3         = 3 ,
	MEGER_PORT0_1	  = 4 ,
	DSP_PORT_NUM      = 4
};
typedef enum _AFBC_IMG_ROT_MODE {
    AFBC_FUNC_NORMAL      = 0x0 ,
    AFBC_FUNC_XMIR        = 0x1 ,
    AFBC_FUNC_YMIR        = 0x2 ,
    AFBC_FUNC_XYMIR       = 0x3 ,
    AFBC_FUNC_ROT90       = 0x4 ,
    AFBC_FUNC_ROT90_XMIR  = 0x5 ,
    AFBC_FUNC_ROT270      = 0x6 ,
    AFBC_FUNC_ROT270_XMIR = 0x7
} AFBC_IMG_ROT_MODE;

enum {
    DISABLE = 0 ,
    ENABLE
};


enum{
	BLACK_SREEN = 0 ,
	BLUE_SREEN,
	COLOR_BARS
};

typedef enum _CHANNEL_INDEX_TYPE{
    CHANNEL_RY = 0,
    CHANNEL_GCb,
    CHANNEL_BCr,
    CHANNEL_A,
    CHANNEL_INDEX_COUNT
} CHANNEL_INDEX_TYPE;

typedef enum _AFBC_IMG_FORMAT{
    AFBC_RGB565    = 0x0   ,
    AFBC_R10G10B10A2 = 0x2 ,
    AFBC_YUV420_10 = 0x3   ,
    AFBC_RGB888    = 0x4   ,
    AFBC_RGBA8888  = 0x5   ,
    AFBC_YUV420_8  = 0x9   ,
    AFBC_YUV422_8  = 0xb   ,
    AFBC_YUV444_8  = 0xc   ,
    AFBC_YUV444_10 = 0xd   ,
    AFBC_YUV422_10 = 0xe   //add by whs,2017,6,17

}AFBC_IMG_FORMAT;

enum {
    AFBCD_FMT_R5G6B5            = 0x0 ,
    AFBCD_FMT_R10G10B10A2       = 0x2 , //yuv444_10bit
    AFBCD_FMT_YUV420_10B        = 0x3 ,
    AFBCD_FMT_R8G8B8            = 0x4 , //YUV444
    AFBCD_FMT_R8G8B8A8          = 0x5 ,
    AFBCD_FMT_YUV420_8B         = 0x9 ,
    AFBCD_FMT_YUV422_8B         = 0xb,
    AFBCD_FMT_YUV444_8B         = 0xc,
    AFBCD_FMT_YUV422_10B        = 0xe,
    AFBCD_FMT_COUNT
};


enum {
	LAYER0 			  = 0 ,
	LAYER1 			  = 1 ,
	LAYER2 			  = 2 ,
	LAYER3 			  = 3 ,
	LAYER4 			  = 4 ,
	LAYER5 			  = 5 ,
	LAYER6 			  = 6 ,
	LAYER7 			  = 7

};
enum {
    OVERLAY_CLUSTER0       = 0 ,
    OVERLAY_CLUSTER1       = 1 ,
    OVERLAY_ESMART0        = 2 ,
    OVERLAY_SMART0         = 3 ,
    OVERLAY_CLUSTER2       = 4 ,
    OVERLAY_CLUSTER3       = 5 ,
    OVERLAY_ESMART1        = 6 ,
    OVERLAY_SMART1         = 7
};

enum {
    FMT_ARGB888         = 0 ,
    FMT_RGB888          = 1 ,
    FMT_RGB565          = 2 ,
    FMT_R10G10B10A2     = 3 ,
    FMT_YCbCr420_888    = 4 ,
    FMT_YCbCr422_888    = 5 ,
    FMT_YCbCr444_888    = 6 ,
    FMT_YCbCr400_888    = 7 ,
    FMT_YVYU422         = 8 ,
    FMT_YVYU420         = 9 ,
    FMT_VYUY422         = 10,
    FMT_VYUY420         = 11,
	FMT_YUV420_TILE_4x4 = 12,
	FMT_YUV422_TILE_4x4 = 13,
	FMT_YUV444_TILE_4x4 = 14,
	FMT_YUV400_TILE_4x4 = 15,
    FMT_BPP_08          = 16, //5'b1_0000
    FMT_BPP_26          = 17, //5'b1_0001
    FMT_BPP_44          = 18, //5'b1_0010
    FMT_BPP_62          = 19, //5'b1_0011
    FMT_YCbCr420_101010 = 20, //5'b1_0100
    FMT_YCbCr422_101010 = 21, //5'b1_0101
    FMT_YCbCr444_101010 = 22, //5'b1_0101
	FMT_YCbCr400_101010 = 23,
	FMT_YUV420_TILE_101010_4x4 = 28,
	FMT_YUV422_TILE_101010_4x4 = 29,
	FMT_YUV444_TILE_101010_4x4 = 30,
	FMT_YUV400_TILE_101010_4x4 = 31,
	FMT_YUV420_TILE_8x8 = 44,
	FMT_YUV422_TILE_8x8 = 45,
	FMT_YUV444_TILE_8x8 = 46,
	FMT_YUV400_TILE_8x8 = 47,
	FMT_YUV420_TILE_101010_8x8 = 60,
	FMT_YUV422_TILE_101010_8x8 = 61,
	FMT_YUV444_TILE_101010_8x8 = 62,
	FMT_YUV400_TILE_101010_8x8 = 63,
    FMT_COUNT
};

typedef enum _CUBIC_MODE_SELETION
{
    CUBIC_PRECISE = 0 ,
    CUBIC_SPLINE      ,
    CUBIC_CATROM      ,
    CUBIC_MITCHELL
}CUBIC_MODE_SELETION;

typedef enum _SCALE_MODE{
    SCALE_MODE_NONE = 0 ,
    SCALE_MODE_UP       ,
    SCALE_MODE_DOWN     ,
    SCALE_MODE_COUNT
}SCALE_MODE;
typedef enum _SCALE_TYPE{
    SCALE_DOWN_NEI     = 0 ,
    SCALE_DOWN_BILI    = 1 ,
    SCALE_DOWN_AVERAGE = 2 ,
    SCALE_UP_NEI       = 0 ,
    SCALE_UP_BIL       = 1 ,
    SCALE_UP_BIC       = 2 ,
    SCALE_UP_ZME       = 3 ,
    SCALE_TYPE_COUNT
}SCALE_TYPE;

typedef enum _IMG_FORMAT{
    IMG_FORMAT_ARGB888          = 0  ,
    IMG_FORMAT_RGB888           = 1  ,
    IMG_FORMAT_RGB565           = 2  ,
    IMG_FORMAT_ARGB2AAA         = 3  ,
	IMG_FORMAT_RGB666			= 3  ,
    IMG_FORMAT_YCbCr420_888     = 4  ,
    IMG_FORMAT_YCbCr422_888     = 5  ,
    IMG_FORMAT_YCbCr444_888     = 6  ,
    IMG_FORMAT_YCbCr400_888     = 7  ,
    IMG_FORMAT_YVYU422          = 8  ,
    IMG_FORMAT_YVYU420          = 9  ,
    IMG_FORMAT_VYUY422          = 10 ,
    IMG_FORMAT_VYUY420          = 11 ,
    IMG_FORMAT_8bpp             = 16 ,
    IMG_FORMAT_6bpp             = 17 ,
    IMG_FORMAT_4bpp             = 18 ,
    IMG_FORMAT_2bpp             = 19 ,
    IMG_FORMAT_YCbCr420_101010  = 20 ,
    IMG_FORMAT_YCbCr422_101010  = 21 ,
    IMG_FORMAT_YCbCr444_101010  = 22 ,
    IMG_FORMAT_YCbCr400_101010  = 23,
  //IMG_FORMAT_RGB666           = 23 ,
    IMG_FORMAT_COUNT
}IMG_FORMAT;

typedef enum _CSC_MODE{
	CSC_YUV_ENC_601 = 0 ,
	CSC_YUV_ENC_709,
	CSC_YUV_ENC_JPEG,
	CSC_YUV_ENC_2020,
	CSC_YUV_ENC_USER_DEF,
	CSC_MODE_COUNT
}CSC_MODE;
typedef enum _OVERLAY_LAYER_SEL_PORT{
           DP_PORT0 = 0 ,
           DP_PORT1 = 1 ,
           DP_PORT2 = 2 ,
		   DP_PORT3 = 3
} LAYER_SEL_PORT;
typedef enum _lut_style
{
	LUT_3D_BLUE = 0  ,
	LUT_3D_GREEN   ,
	LUT_3D_PURPLE  ,
	LUT_3D_RED     ,
	LUT_3D_STYLE4  ,
	LUT_3D_STYLE5  ,
	LUT_3D_STYLE6
} LUT_STYLE;

typedef enum _ESMART_MST{
    ESMART_MST0 = 0  ,
    ESMART_MST1      ,
    ESMART_MST2      ,
    ESMART_MST3      ,
    ESMART_COUNT_END
}ESMART_MST;

typedef struct layer_vir_width{
	u16    yrgb_vir_width_word 	  ;
	u16    cbcr_vir_width_word    ;
} LAYER_VIR_WIDTH;

typedef struct scl_info{
    u16 act_width;
    u16 dsp_width;

    u16 act_height;
    u16 dsp_height;

    u8  xsd_en     ;
    u8  xsu_en     ;
    u8  xavg_en    ;
    u8  xgt_en 	   ;
    u8  xscl_mode  ;
    u8  xgt_mode   ;
    u16 scl_xfactor;
    u8  xscl_offset;

    u8  yscl_offset;
    u8  yavg_en    ;
    u8  ygt_en     ;
    u8  ysd_en     ;
    u8  ysu_en     ;
    u8  yscl_mode  ;
    u16 scl_yfactor;
    u8  ygt_mode   ;

} SCL_INFO;

typedef struct alpha_para{
		u8	 src_alpha_en;
		u8	 dst_alpha_en;
		u8	 src_top_swap;
		//COLOR_SRC
		u8	 src_color_m0;
		u8	 src_alpha_m0;
		u8	 src_blend_m0;
		u8	 src_alpha_cal_m0;
		u8	 src_factor_m0	 ;
		u8	 src_global_alpha;
		//COLOR_DST
		u8	 dst_color_m0;
		u8	 dst_alpha_m0;
		u8	 dst_blend_m0;
		u8	 dst_alpha_cal_m0;
		u8	 dst_factor_m0	 ;
		u8	 dst_global_alpha;
		//ALPHA_SRC
		u8	 src_alpha_m1;
		u8	 src_blend_m1;
		u8	 src_alpha_cal_m1;
		u8	 src_factor_m1	 ;
		//ALPHA_DST
		u8	 dst_alpha_m1;
		u8	 dst_blend_m1;
		u8	 dst_alpha_cal_m1;
		u8	 dst_factor_m1	 ;
} ALPHA_PARA;

typedef enum _OVERLAY_LAYER_SEL{
    LAYER_SEL_CLUSTER0 = 0 ,
    LAYER_SEL_CLUSTER1     ,
    LAYER_SEL_ESMART0      ,
    LAYER_SEL_SMART0       ,
    LAYER_SEL_CLUSTER2     ,
    LAYER_SEL_CLUSTER3     ,
    LAYER_SEL_ESMART1      ,
    LAYER_SEL_SMART1       ,
    LAYER_SEL_COUNT
}LAYER_SEL;

typedef enum _OVERLAY_PORT_MUX{
    PORT_MUX_LAYER0_BYPASS = 0 ,
    PORT_MUX_MIX4              ,
    PORT_MUX_MIX5              ,
    PORT_MUX_MIX6              ,
    PORT_MUX_MIX7              ,
    PORT_MUX_MIX8              ,
    PORT_MUX_MIX9              ,
    PORT_MUX_MIX10
} LAYER_PORT_MUX;

enum {
    XSCALE_UP_NEI=0,
    XSCALE_UP_BIL=1,
    XSCALE_UP_BIC=2
};

enum {
    XSCALE_DOWN_NEI=0,
    XSCALE_DOWN_BIL=1,
    XSCALE_DOWN_AVG=2
};

enum {
    YSCALE_UP_NEI=0,
    YSCALE_UP_BIL=1,
    YSCALE_UP_BIC=2
};

enum {
    YSCALE_DOWN_NEI=0,
    YSCALE_DOWN_BIL=1,
    YSCALE_DOWN_AVG=2
};



enum
{
	AA_STRAIGHT	       = 0x0,
	AA_INVERSE         = 0x1
};//src_alpha_mode
enum
{
	AA_GLOBAL          = 0x0,
	AA_PER_PIX         = 0x1,
	AA_PER_PIX_GLOBAL  = 0x2
};//src_global_alpha_mode
enum
{
	AA_NO_SAT	= 0x1,
	AA_SAT	    = 0x0
};//src_alpha_sel

enum
{
	ALPHA_NO_SAT	= 0x0,
	ALPHA_SAT	    = 0x1
};//src_alpha_sel


enum
{
	AA_SRC_PRE_MUL   = 0x0,
	AA_SRC_NO_PRE_MUL	    = 0x1
};//src_color_mode
enum{
	AB_USER_DEFINE   	= 0x0,
	AB_CLEAR 			= 0x1,
	AB_SRC 				= 0x2,
	AB_DST 				= 0x3,
	AB_SRC_OVER 		= 0x4,
	AB_DST_OVER 		= 0x5,
	AB_SRC_IN	 		= 0x6,
	AB_DST_IN 			= 0x7,
	AB_SRC_OUT 			= 0x8,
	AB_DST_OUT 			= 0x9,
	AB_SRC_ATOP 		= 0xa,
	AB_DST_ATOP 		= 0xb,
	XOR 				= 0xc,
	AB_SRC_OVER_GLOBAL  = 0xd,
	AB_ABDRIOD_PREMUL   = 0xe,
	AB_COUNT 			= 0xf
};


enum
{
	ALPHA_NO_PRE_MUL    = 0x0,
	ALPHA_PRE_MUL	    = 0x1
};//src_color_mode VOP LITE USE


enum
{
	AA_ZERO	         = 0x0,
	AA_ONE           = 0x1,
	AA_SRC	         = 0x2,
	AA_SRC_INVERSE   = 0x3,
	AA_DST 			 = 0X4,
	AA_DST_GLOBAL    = 0x5
};//src_factor_mode  &&  dst_factor_mode

enum
{	PARALLEL_24_BIT_RGB888      = 0x0,
	PARALLEL_18_BIT_RGB666      = 0x1,
	PARALLEL_16_BIT_RGB565      = 0x2,
 	PARALLEL_24_BIT_RGB888_DDR  = 0x3,
	EDP_YUV422 					= 0X3,
	ITU_656_L                   = 0x5,
	ITU_656_M                   = 0x6,
	ITU_656_H                   = 0x7,
	SERIAL_3X8_BIT_RGB888       = 0x8,
	DP_YUV422                   = 0xc,
	DP_YUV420                   = 0xd,
	HDMI_YUV420                 = 0xe,
	PARALLEL_RGBAAA 			= 0xf,
	SERIAL_2X16_BIT_RGB888X     = 0xb
};

enum {
    IMG_POST_FORMAT_RGB888  	 = 0x0  ,
    IMG_POST_FORMAT_666    		 = 0x1  ,
    IMG_POST_FORMAT_565    		 = 0x2  ,
	IMG_POST_FORMAT_EDP_YUV422   = 0x3  ,
	IMG_POST_FORMAT_DP_YUV422    = 0xc  ,
	IMG_POST_FORMAT_DP_YUV420    = 0xd  ,
    IMG_POST_FORMAT_HDMI_YUV420  = 0xe  ,
    IMG_POST_FORMAT_aaa     	 = 0xf
} ;

enum{
	WB_FORMAT_ARGB888 = 0,
	WB_FORMAT_RGB888  = 1,
	WB_FORMAT_RGB565  = 2,
	WB_FORMAT_YUV420  = 4
};

typedef enum _IMG_RAW{
    IMG_Cluster0_0 = 0  ,
    IMG_Cluster0_1 = 1  ,
    IMG_Cluster1_0 = 2  ,
    IMG_Cluster1_1 = 3  ,
    IMG_Esmart0_0  = 4  ,
    IMG_Esmart0_1  = 5  ,
    IMG_Esmart0_2  = 6  ,
	IMG_Esmart0_3  = 7  ,
    IMG_Esmart1_0  = 8 ,
    IMG_Esmart1_1  = 9 ,
    IMG_Esmart1_2  = 10 ,
	IMG_Esmart1_3  = 11 ,
    IMG_Cluster2_0 = 12 ,
    IMG_Cluster2_1 = 13 ,
    IMG_Cluster3_0 = 14 ,
    IMG_Cluster3_1 = 15 ,
   	IMG_Smart0_0   = 16  ,
	IMG_Smart0_1   = 17  ,
	IMG_Smart0_2   = 18 ,
    IMG_Smart0_3   = 19 ,
	IMG_Smart1_0   = 20 ,
	IMG_Smart1_1   = 21 ,
	IMG_Smart1_2   = 22 ,
    IMG_Smart1_3   = 23 ,
    IGM_COUNT      = 24
}IMG_RAW;


#endif /* DRIVERS_TEST_VOP3_VOP3_ENUM_H_ */
