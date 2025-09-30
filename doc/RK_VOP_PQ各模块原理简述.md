# RK VOP PQ 各模块原理简述

发布版本：v0.1.0

发布日期：2025-09-22

文件密级：□绝密   □秘密   ■内部资料   □公开

---

**免责声明**

本文档按“现状”提供，瑞芯微电子股份有限公司（“本公司”，下同）不对本文档的任何陈述、信息和内容的准确性、可靠性、完整性、适销性、特定目的性和非侵权性提供任何明示或暗示的声明或保证。本文档仅作为使用指导的参考。

由于产品版本升级或其他原因，本文档将可能在未经任何通知的情况下，不定期进行更新或修改。

**商标声明**

“Rockchip”、“瑞芯微”、“瑞芯”均为本公司的注册商标，归本公司所有。

本文档可能提及的其他所有注册商标或商标，由其各自拥有者所有。

**版权所有** **© 瑞芯微电子股份有限公司**

超越合理使用范畴，非经本公司书面许可，任何单位和个人不得擅自摘抄、复制本文档内容的部分或全部，并不得以任何形式传播。

瑞芯微电子股份有限公司

Rockchip Electronics Co., Ltd.

地址：     福建省福州市铜盘路软件园A区18号

网址：     [www.rock-chips.com](http://www.rock-chips.com)

客户服务电话： +86-4007-700-590

客户服务传真： +86-591-83951833

客户服务邮箱： [fae@rock-chips.com](mailto:fae@rock-chips.com)

---

**读者对象**

本文档主要适用于以下工程师：

- **Rockchip内部**技术支持工程师
- **Rockchip内部**软件开发工程师

**修订记录**

| **日期**   | **版本** |  **作者** | **审核**           | **修改说明**                    |
|:----------:|:--------:|:----------:|:-------:|:---------------------------------------- |
| 2025/09/22 | 0.1.0   | vance.wu | \ | 初始版本，仅包含CSC模块的原理简述 |

## CSC - 色彩空间转换

CSC 全程为 **Color Space Conversion**， 具有以下2个功能：

1. 主要实现YUV、RGB之间的色彩空间转换，也支持Y2Y和R2R转换，包含 FullRange 和 LimitedRange 之间互转；
2. 实现亮度、色相、饱和度、对比度与白平衡的调节。

### 基础公式

CSC色彩空间转换的基础公式为：
$$\begin{bmatrix}y_0\\y_1\\y_2\end{bmatrix}= \begin{bmatrix}a_{00}&a_{01}&a_{02}\\a_{10}&a_{11}&a_{12}\\a_{20}&a_{21}&a_{22}\end{bmatrix} \begin{bmatrix}x_0+\Delta{x_0} \\x_1+\Delta{x_1}\\x_2+\Delta{x_2}\end{bmatrix}+\begin{bmatrix}\Delta{y_0}\\\Delta{y_1}\\\Delta{y_2}\end{bmatrix}$$

其中：

- $T = \begin{bmatrix}a_{00}&a_{01}&a_{02}\\a_{10}&a_{11}&a_{12}\\a_{20}&a_{21}&a_{22}\end{bmatrix}$ 为色彩空间转换矩阵，具体的取值跟输入/输出的像素是RGB/YUV以及所处的色彩空间有关系，标准系数可以从REC-BT.601/709/2020的建议书中获取。
- $X = [x_0, x_1, x_2]^T$，  $Y = [y_0, y_1, y_2]^T$ 分别为输入/输出像素，可以是RGB也是可以YUV像素.
- $\Delta{X} = [\Delta{x_0}, \Delta{x_1}, \Delta{x_2}]^T$ 和 $\Delta{Y} = [\Delta{y_0}, \Delta{y_1}, \Delta{y_2}]^T$ 分别为输入/输出像素的**RangeOffset**，以8bit像素深度为例，有:
  - 如果像素是**FullRange + RGB**, 则$\Delta{X}=[0, 0, 0]^T$， $\Delta{Y}=[0, 0, 0]^T$
  - 如果像素是**FullRange + YUV**, 则$\Delta{X}=[0, -128, -128]^T$， $\Delta{Y}=[0, 128, 128]^T$
  - 如果像素是**LimitedRange + RGB**, 则$\Delta{X}=[-16, -16, -16]^T$， $\Delta{Y}=[16, 16, 16]^T$
  - 如果像素是**LimitedRange + YUV**, 则$\Delta{X}=[-16, -128, -128]^T$， $\Delta{Y}=[16, 128, 128]^T$

### RK3572-VOP 寄存器对应关系

- 根据基础转换公式，完成CSC转换一共需要9+3+3=15个参数。
- 根据矩阵乘法的分配率，可以优化成12个参数，即: $$\begin{bmatrix}y_0\\y_1\\y_2\end{bmatrix}= \begin{bmatrix}a_{00}&a_{01}&a_{02}\\a_{10}&a_{11}&a_{12}\\a_{20}&a_{21}&a_{22}\end{bmatrix} \begin{bmatrix}x_0\\x_1\\x_2\end{bmatrix}+\begin{bmatrix}\Delta{b_0}\\\Delta{b_1}\\\Delta{b_2}\end{bmatrix}$$
- $a_{00} \sim a_{22}$对应VOP中CSC模块的寄存器 `CSC_COEF00 ~ CSC_COEF22`，$b_0 \sim b_2$对应寄存器 `CSC_OFFSET0 ~ CSC_OFFSET2`。

### BCSH的支持原理

BCSH 是指 (亮度-Brightness, 对比度-Contrast, 饱和度-Saturation, 色调-Hue) 四个色彩调节参数。CSC支持在色彩空间转换的同时实现对该4个参数的调整。 <br>
主要原理是根据下文的计算公式，将这些参数对应的调整矩阵作用于标准转换矩阵$T$，生成新的矩阵$T'$。 <br>
在硬件实现中可以根据BCSH参数直接计算好最终的$T'$矩阵，$T'$矩阵更新后，Offset向量$\Delta{B}$也需要更新。

Y2R和R2Y的基础公式:
$$\begin{bmatrix}R^{\prime}\\G^{\prime}\\B^{\prime}\end{bmatrix}=M_1\times T\times M_0\begin{bmatrix}Y\\U\\V\end{bmatrix}+\begin{bmatrix}r_{offset}\\g_{offset}\\b_{offset}\end{bmatrix}+k_{bright}$$
$$\begin{bmatrix}Y^\prime\\U^\prime\\V^\prime\end{bmatrix}=M_0\times T\times M_1\begin{bmatrix}R\\G\\B\end{bmatrix}+\begin{bmatrix}k_{bright}\\0\\0\end{bmatrix}$$
$$M_0=\begin{bmatrix}1&0&0\\0&cos(h)&sin(h)\\0&-sin(h)&cos(h)\end{bmatrix}\times\begin{bmatrix}1&0&0\\0&s&0\\0&0&s\end{bmatrix}$$
$$M_1=\begin{bmatrix}r_{gain}&0&0\\0&b_{gain}&0\\0&0&g_{gain}\end{bmatrix}\times\begin{bmatrix}c&0&0\\0&c&0\\0&0&c\end{bmatrix}$$

Y2Y公式:
$$\begin{bmatrix}Y^{\prime}\\U^{\prime}\\V^{\prime}\end{bmatrix}=T\times M_0\times N_{r2y}\times M_1\times N_{y2r}\begin{bmatrix}Y\\U\\V\end{bmatrix}+\begin{bmatrix}k_{bright}\\0\\0\end{bmatrix}$$

R2R公式:
$$\begin{bmatrix}R^{\prime}\\G^{\prime}\\B^{\prime}\end{bmatrix}=T\times M_1\times N_{y2r}\times M_0\times N_{r2y}\begin{bmatrix}R\\G\\B\end{bmatrix}+\begin{bmatrix}k_{bright}\\k_{bright}\\k_{bright}\end{bmatrix}$$

其中:

- $M_0$表示色相`Hue`与饱和度`Saturation`，作用于YUV域。
- $M_1$表示RGB通道增益`rgb_gain`与对比度`Contrast`的调节矩阵，作用于RGB域。
- $T$表示3x3色彩空间转换矩阵。
- $N_{r2y}$和$N_{y2r}$表示R2Y和Y2R的标准转换矩阵。
  - $h=0, s=1$时，$M_0$为对角矩阵，此时和$M0$相乘符合交换律
  - $r_{gain}=g_{gain}=b_{gain}$时，$M_1$为对角矩阵，此时和$M1$相乘符合交换律
  - 在$M_0$或$M_1$矩阵为对角的情况下，从定点化计算精度优化的角度考虑，可以省略R2Y和Y2R的转换，减少精度损失

## ACM - 自动色彩管理

ACM 全称为 **Auto Color Management**， 主要通过亮度(Brightness)、色调(Hue)和饱和度(Saturation)三个维度调整画面的颜色，以获取色彩更丰富的画面。

ACM 模块可以实现色彩的校正和增强。 数据处理基于**YHS色彩空间**，模块内部会将 YUV 信号先转换到 YHS 空间，调节完毕后再转换回 YUV 空间中。

### YHS的改变量计算

YHS的改变量


```c
typedef struct post_acm {
 short delta_lut_h[ACM_DELTA_LUT_H_TOTAL_LENGTH]; // 65*3 -> pack to 65 regs
 short gain_lut_hy[ACM_GAIN_LUT_HY_TOTAL_LENGTH]; // 9*17*3 -> pack to 153 regs
 short gain_lut_hs[ACM_GAIN_LUT_HS_TOTAL_LENGTH]; // 13*17*3 -> pack to 221 regs
 unsigned short y_gain;
 unsigned short h_gain;
 unsigned short s_gain;
 unsigned short acm_enable;
} kernel_acm_t;

int y, u, v;
int y, s, h; // calculated from y, u, v

short delta_yh = delta_lut_h[h];
short delta_sh = delta_lut_h[h + 65*1];
short delta_hh = delta_lut_h[h + 65*2];
short gain_yy = gain_lut_hy[y];
short gain_sy = gain_lut_hy[y + 9*17*1];
short gain_hy = gain_lut_hy[y + 9*17*2];
short gain_ys = gain_lut_hs[s];
short gain_ss = gain_lut_hs[s + 13*17*1];
short gain_hs = gain_lut_hs[s + 13*17*2];
delta_yh *= gain_yy * gain_ys;
delta_sh *= gain_sy * gain_ss;
delta_hh *= gain_hy * gain_hs;
y += delta_yh; // 输出的ysh还需要转回yuv
s += delta_sh;
h += delta_hh;
```


### 三角函数在硬件上的计算 - Cordic 算法

TODO


## Sharpness - 锐化
