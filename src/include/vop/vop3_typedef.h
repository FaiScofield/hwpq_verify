/*
 * vop3_typedef.h

 *
 *  Created on: 2021-9-8
 *      Author: rihui
 */
#include "./vop3_define.h"

#ifdef VOP3_ROBIN
#define PASS      {printf("^_^ ARM_SUCESS ^_^\n");word32(ARM_SUCESS_ADD) = 0x1;}
#define FAIL      {printf("-_- ARM_FAILED -_-\n");word32(ARM_FAILED_ADD) = 0x1;}
#define word32    *(unsigned int  volatile *)

#define fix_ed 							12
#define SIG0  							0.5
#define SIG1 							0.8
#define SIGW							25.0
#define W_TEMPORARIT					256.0
#define MMM_MIN_TH						50
#define EDGE_MAX_TH 					25
#define CNT_MIN_TH 						8191
#define ROUND_I(_T_,x,scale_f)     		(int)(((_T_)(x) + (1<<(scale_f-1))>>scale_f))
#define ROUND_F(x) 						(int)(x+(x>0 ? 0.5: -0.5))
#define FREE(ptr)                       do{\
                                                if((ptr) != NULL){ free(ptr); (ptr) = NULL;}\
                                        }while(0);

#define MALLOC(ptr, type, size)               do{(ptr) = (type *)malloc((sizeof(type))*(size)); \
                                                if((ptr) == NULL){ printf("Malloc Fail!\n"); exit(1);} \
                                                memset(ptr, 0, (sizeof(type))*(size));\
                                              }while(0);

#define MIN(a,b)							(a <= b) ? a:b
#define MAX(a,b)							(a >= b) ? a:b
#define COLOR_ENH_FIXPOINT_SHIFT 8
#define COLOR_ENH_FIXPOINT(x) 				((int)((x)* (1<<COLOR_ENH_FIXPOINT_SHIFT)))
#define CLIP(a, min, max)			    	(((a) < (min)) ? (min) : (((a) > (max)) ? (max) : (a)))
#define ABS(A) 								(A>0 ? A : -A)
#define MAX_ALPHA_VAL 		   255
#define BRIGHT_BITS_10B 		7
#define BRIGHT_MIN_10B			-127
#define BRIGHT_MAX_10B 			127
#define BRIGHT_MIN_8B			-63
#define BRIGHT_MAX_8B 			63
#define BRIGHT_BITS_8B 			5
#define shiftdown 				4
#define ALPHA_FIXPOINT_ONE 		256
#define ALPHA_FIXPOINT_MULT(x,alpha) 		(((int)(x)*alpha) + 128)>>8
#define ALPHA_FIXPOINT_REVERT(x) 			((x+128) >>8)
#define MAX_UINT8 				(1<<8)-1
#define BIT_MASK(i) 			((1<<i)-1)
#define EXIT(ret) 				exit(ret)
#define INT10_TO_INT32(val) 	(int)(val&0x3ff)
#define INT8_TO_10(val) 		(val*4)
#define INT8_TO_INT32(val) 		(int)(val&0xff)
/*****************************************************************************************************/
#define SCALE_FACTOR_BILI_DN_FIXPOINT_SHIFT   12   // 4.12
#define SCALE_FACTOR_BILI_DN_FIXPOINT(x)      ((INT32)((x)*(1 << SCALE_FACTOR_BILI_DN_FIXPOINT_SHIFT)))

#define SCALE_FACTOR_BILI_UP_FIXPOINT_SHIFT   16   // 0.16

#define SCALE_FACTOR_AVRG_FIXPOINT_SHIFT   16   //0.16
#define SCALE_FACTOR_AVRG_FIXPOINT(x)      ((INT32)((x)*(1 << SCALE_FACTOR_AVRG_FIXPOINT_SHIFT)))

#define SCALE_FACTOR_BIC_FIXPOINT_SHIFT    16   // 0.16
#define SCALE_FACTOR_BIC_FIXPOINT(x)       ((INT32)((x)*(1 << SCALE_FACTOR_BIC_FIXPOINT_SHIFT)))

#define SCALE_FACTOR_DEFAULT_FIXPOINT_SHIFT    12  //NONE SCALE,vsd_bil
#define SCALE_FACTOR_VSDBIL_FIXPOINT_SHIFT     12  //VER SCALE DOWN BIL
/*****************************************************************************************************/
#define GET_SCALE_FACTOR_BILI_DN(src, dst)  ((src*2-3) << (SCALE_FACTOR_BILI_DN_FIXPOINT_SHIFT-1)) / ((dst-1) )
#define GET_SCALE_FACTOR_BILI_UP(src, dst)  (((src*2-3) << (SCALE_FACTOR_BILI_UP_FIXPOINT_SHIFT-1)) / ((dst) - 1))
#define GET_SCALE_FACTOR_BIC(src, dst)      ((((src*2)-3) << (SCALE_FACTOR_BIC_FIXPOINT_SHIFT-1))     / ((dst) - 1))

#define GET_SCALE_FACTOR_BILI_DN_LINE(src, dst)  (((src*2-3) << (SCALE_FACTOR_BILI_DN_FIXPOINT_SHIFT-1)) / ((dst-1) ))

#define GET_SCALE_FACTOR_BILI_DN_WB(src, dst)  ((src-1) << (SCALE_FACTOR_BILI_DN_FIXPOINT_SHIFT)) / ((dst-1) )

/*****************************************************************/
#define GET_SCALE_DN_ACT_HEIGHT(srcH, vScaleDnMult) (((srcH)+(vScaleDnMult)-1)/(vScaleDnMult))

//#define VSKIP_MORE_PRECISE

#ifdef VSKIP_MORE_PRECISE
#define MIN_SCALE_FACTOR_AFTER_VSKIP        1.5f
#define GET_SCALE_FACTOR_BILI_DN_VSKIP(srcH, dstH, vScaleDnMult) \
            (GET_SCALE_FACTOR_BILI_DN(GET_SCALE_DN_ACT_HEIGHT((srcH), (vScaleDnMult)), (dstH)))
#else
#define MIN_SCALE_FACTOR_AFTER_VSKIP        1
#define GET_SCALE_FACTOR_BILI_DN_VSKIP(srcH, dstH, vScaleDnMult) \
            ( (GET_SCALE_DN_ACT_HEIGHT((srcH), (vScaleDnMult)) == (dstH))      ? (GET_SCALE_FACTOR_BILI_DN_LINE((srcH), (dstH))/(vScaleDnMult)) : \
              (GET_SCALE_DN_ACT_HEIGHT((srcH), (vScaleDnMult)) == ((dstH)*2) ) ?  GET_SCALE_FACTOR_BILI_DN_LINE(GET_SCALE_DN_ACT_HEIGHT(((srcH-1)), (vScaleDnMult)), (dstH)) : \
                                                                                  GET_SCALE_FACTOR_BILI_DN_LINE(GET_SCALE_DN_ACT_HEIGHT((srcH),     (vScaleDnMult)), (dstH)) )
#endif
/*****************************************************************/

#define GET_SCALE_FACTOR_AVRG(src, dst)  ((((dst) << (SCALE_FACTOR_AVRG_FIXPOINT_SHIFT+1)))/(2*(src) - 1))

/*****************************************************************************************************/
//Scale Coordinate Accumulate, x.16
#define SCALE_COOR_ACC_FIXPOINT_SHIFT     16
#define SCALE_COOR_ACC_FIXPOINT_ONE       (1 << SCALE_COOR_ACC_FIXPOINT_SHIFT)
#define SCALE_COOR_ACC_FIXPOINT(x)        ((INT32)((x)*(1 << SCALE_COOR_ACC_FIXPOINT_SHIFT)))
#define SCALE_COOR_ACC_FIXPOINT_REVERT(x) ((((x) >> (SCALE_COOR_ACC_FIXPOINT_SHIFT-1)) + 1) >> 1)

#define SCALE_GET_COOR_ACC_FIXPOINT(scaleFactor, factorFixpointShift)  \
        ((scaleFactor) << (SCALE_COOR_ACC_FIXPOINT_SHIFT - (factorFixpointShift)))
/*****************************************************************************************************/
#define SCALE_FILTER_FACTOR_FIXPOINT_SHIFT     8
#define SCALE_FILTER_FACTOR_FIXPOINT_ONE       (1 << SCALE_FILTER_FACTOR_FIXPOINT_SHIFT)
#define SCALE_FILTER_FACTOR_FIXPOINT(x)        ((INT32)((x)*(1 << SCALE_FILTER_FACTOR_FIXPOINT_SHIFT)))
#define SCALE_FILTER_FACTOR_FIXPOINT_REVERT(x) ((((x) >> (SCALE_FILTER_FACTOR_FIXPOINT_SHIFT-1)) + 1) >> 1)

#define SCALE_GET_FILTER_FACTOR_FIXPOINT(coorAccumulate, coorAccFixpointShift) \
  (((coorAccumulate)>>((coorAccFixpointShift)-SCALE_FILTER_FACTOR_FIXPOINT_SHIFT))&(SCALE_FILTER_FACTOR_FIXPOINT_ONE-1))

#define SCALE_OFFSET_FIXPOINT_SHIFT            8
#define SCALE_OFFSET_FIXPOINT(x)              ((INT32)((x)*(1 << SCALE_OFFSET_FIXPOINT_SHIFT)))
/*****************************************************************************************************/

//System typedef
#define BCSH_HW_BITDEPTH   8  //10

#define COLOR_ENH_FIXPOINT_SHIFT 8
//#define COLOR_ENH_FIXPOINT(x)        ((int32)((x)*(1 << COLOR_ENH_FIXPOINT_SHIFT)))
#define CONTRAST_MIN    0
#define CONTRAST_MAX	   (COLOR_ENH_FIXPOINT(1.992))

#define SIN_HUE_MIN        (COLOR_ENH_FIXPOINT(-0.5))
#define SIN_HUE_MAX        (COLOR_ENH_FIXPOINT(+0.5))

#define COS_HUE_MIN        (COLOR_ENH_FIXPOINT(0.866))
#define COS_HUE_MAX        (COLOR_ENH_FIXPOINT(1))

#define SAT_CON_MIN        0
#define SAT_CON_MAX        (COLOR_ENH_FIXPOINT(1.992*1.992))

#endif

