


#ifndef YUV_ADJUST_H
#define YUV_ADJUST_H

#include "hsv_fixed.h"

/* ===================== YCbCr 域固定管线 BCSH（无 mode 分支） ===================== */
/* 对应 script/verify_tool_app/ui_impl/bcsh_ui_impl.py 的 YCbCr 处理域（Adjust Field
   = YCbCr，步骤 3️⃣~5️⃣ 中的 BCSH 调整）。处理域为 yuv444p full-range 的归一化
   (Y, Cb, Cr)（Cb/Cr 去中心：Y∈[0,1]、Cb,Cr∈[-0.5,0.5]）；BCSH 直接作用在
   “亮度 Y + 色度极坐标 (radius, θ)”上，B 通道即 Y：

     执行顺序：B(ModeAdd) -> C(MulAtMidPoint) -> S(ModeMul) -> H(ModeAdd)（db 先于 gc 生效）

     B  ModeAdd        Y1 = clip(Y + db)             db∈[-1,1]，中性 0（归一化量，×maxv）
     C  MulAtMidPoint  Y2 = clip((Y1-0.5)·gc + 0.5)  gc∈[0,4]，中性 1.0（过 Y=0.5 中点）
     S  ModeMul        r' = r·ds                     ds∈[0,4]，中性 1.0（r=√(Cb²+Cr²)）
     H  ModeAdd        θ' = θ + angle                angle 为极角增量（色度向量旋转）

   要点：
     - S/H 直接作用在 (Cb,Cr) 分量上（先乘 ds、再按 angle 旋转），**不需要 atan2
       与开方**：极坐标的“半径缩放 + 角度旋转”等价于对色度向量做“缩放 + 旋转”
     - 极角旋转的 cos/sin 用 hsv_fixed.h 的 257 项 Q15 表 + 线性插值（与 RGB 域
       绕灰轴旋转共用同一份），无 float、无 math 库依赖
     - 全程 Q11 像素域运算（pixel<<11），中间步骤不逐步舍入，末尾统一回像素域

   CompLumaFirst 开关（comp_luma_first，见 adj_yuv_gamut_t）：调整后 (Y,Cb,Cr) 可能
   越出 RGB 色域（如 S 增益 > 1），该开关决定步骤 5️⃣ 的色域处理方式：
     - 关闭（ADJ_YUV_GAMUT_HARDCLIP，Python 的 HardClip 策略，默认）：Y、Cb、Cr
       各自硬钳到格式范围（Y∈[0,maxv]、Cb/Cr∈[-maxv/2,maxv/2]）。
     - 开启（ADJ_YUV_GAMUT_COMP_LUMA_FIRST，Python 的 CompLumaFirst 策略）：保极角
       的亮度补偿——先只调 Y，把 Y 钳到该 (θ,r) 下的可行区间 [Y_lo, Y_hi]
       （Y_lo=max_i(-k_i)、Y_hi=maxv-max_i(k_i)，k_i 为 Y2R 第 i 通道的色度贡献）；
       若区间为空（Y 单独调不够），再把色度缩到恰好可解并顶 Y，结果落在色域边界
       （max(RGB)=1、min(RGB)=0，全饱和），色相严格保持。此分支不做色度格式范围
       钳位（与 Python 一致：RGB 已入域，Cb/Cr 仍可能略超 ±maxv/2，由编码侧钳位）。

   定点格式（与 hsv_fixed/rgb_adjust 一致）：
     gain_c    : Q11（1.0 = FIX_S_ONE = 2048），[0,4]
     delta_b   : Q11（1.0 = FIX_S_ONE），[-1,1]（归一化量，内部按 ×maxv 折算到像素域）
     delta_s   : Q11（1.0 = FIX_S_ONE），[0,4]
     angle_q14 : Q14（360° = FIX_H_ONE = 16384），极角旋转量（0 恒等跳过）
     cs        : adj_yuv_cs_t，CompLumaFirst 求解可行区间所用的 Y2R 色域矩阵
   像素域：Y∈[0, maxv]，Cb/Cr 为**去中心带符号**值 ∈[-maxv/2, maxv/2]
   （u8: -128..127 / u10: -512..511），内部统一 Q11（pixel<<11）运算。

   注：S 步为纯色度增益 r'=r·ds，不额外做“r 钳到归一化 1.0”的截断——该截断是通用
   adjust_hsv 对 S∈[0,1] 的假设带入的（YCbCr 极径天然 ≤0.7071，仅 ds>1.414 时才可能
   触发），此处按硬件语义取纯增益，越界统一由末尾色域处理兜底。 */

/* Y2R 色域矩阵（CompLumaFirst 求 Y 的可行区间用）。系数见 yuv_adjust.c */
typedef enum {
    ADJ_YUV_CS_BT601 = 0, /* BT.601 Y2R = [1,0,1.402; 1,-0.344136,-0.714136; 1,1.772,0] */
    ADJ_YUV_CS_BT709,     /* BT.709 Y2R = [1,0,1.5748; 1,-0.187324,-0.468124; 1,1.8556,0]（默认） */
    ADJ_YUV_CS_BT2020,    /* BT.2020 Y2R = [1,0,1.4746; 1,-0.164553,-0.571353; 1,1.8814,0] */
} adj_yuv_cs_t;

/* 步骤 5️⃣ 色域处理策略（即 CompLumaFirst 开关） */
typedef enum {
    ADJ_YUV_GAMUT_HARDCLIP = 0,    /* 关闭：Y/Cb/Cr 各自硬钳到格式范围（默认） */
    ADJ_YUV_GAMUT_COMP_LUMA_FIRST, /* 开启：保极角亮度补偿（Y 优先、S 兜底） */
} adj_yuv_gamut_t;

/* 单像素 YCbCr 域固定管线 BCSH 调整（定点，无浮点、无 math 库依赖）。
   输入 y∈[0,maxv]、cb/cr∈[-maxv/2,maxv/2]（去中心带符号）；
   输出 *yo∈[0,maxv]，色度输出 *cbo 与 *cro 为去中心带符号值（HARDCLIP 分支已钳位、
   COMP_LUMA_FIRST 分支不钳）。 */
void adjust_yuv_fix(uint16_t y, int32_t cb, int32_t cr, uint16_t maxv, int32_t gain_c, int32_t delta_b,
    int32_t delta_s, int32_t angle_q14, int comp_luma_first, int cs, uint16_t *yo, int32_t *cbo, int32_t *cro);

/* 同管线的浮点参考实现（精度基准，无定点量化）：y∈[0,1]、cb/cr∈[-0.5,0.5]（归一化），
   参数为物理量 gain_c∈[0,4] / delta_b∈[-1,1] / delta_s∈[0,4] / angle_deg（度），
   输出 yo∈[0,1]、cbo/cro 为归一化色度。实现见 yuv_adjust.c（依赖 math.h）。 */
void adjust_yuv_float(float y, float cb, float cr, float gain_c, float delta_b, float delta_s, float angle_deg,
    int comp_luma_first, int cs, float *yo, float *cbo, float *cro);

#endif /* YUV_ADJUST_H */