# HWPQ Kernel Verify Note

本文主要介绍 HWPQ 内核驱动相关验证内容。

TODO: 调用框图

## CSC模块验证

CSC 在 RTL 中设置的位宽如下:

| module | input | csc_coef(3x3 matrix) | csc_offset(3x1 vector) | output |
| --- | --- | --- | --- | --- |
| esmart0/cluster0_win0 | 10 | 16 | 10+16=26 | 10 |
| write back | 8 | 13 | 8+13=21 | 8 |
| Other | 10 | 13 | 10+13=23 | 10 |

### post csc

- RK3572 CSC 系数寄存器计算公式:
  - $$ Dst = (M*(Src + V_s) + (V_d << 10)) >> 10 $$
  - $$ M' = M, \quad V' = M*V_s + (V_d << 10)$$
  - $Src, Dst, M$ 分别为输入、输出、色彩空间转换矩阵； $V_s, V_d$分别为输入和输出的Range offset向量。
  - $M', V'$ 为CSC系数的寄存器取值。
  - **注**：右移带有四舍五入。
- RK3576 CSC 系数寄存器计算公式:
  - $$ Dst = (M*(Src + V_s) >> 10) + V_d $$
  - $$ M' = M, \qquad V' = (M*V_s >> 10) + V_d$$
- RK3576 CSC 驱动系数的向量部分计算本质上是等效的：
  - $$ V' = (M*V_s + (V_d<<10)) >> 10 = (M*V_s >> 10) + V_d$$


## DCI模块验证

DCI验证涉及软件处理部分。

`librkhwpq.so`
