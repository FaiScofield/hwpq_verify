/**
 * hsv_fixed.c — RGB <-> HSV 定点(fixed-point)转换，全程无浮点数
 *
 * 定标约定 (Q16.16)：
 *   FIX_ONE = 1 << 16 = 65536
 *   H : 色相，单位"度"，1 度 = FIX_ONE，有效范围 [0, 360*FIX_ONE)
 *   S : 饱和度，[0, FIX_ONE]            （1.0 = FIX_ONE）
 *   V : 明度，[0, 255]                  （与 8bit RGB 同尺度，不缩放）
 *
 * 特点：
 *   - 无任何 float/double、无三角函数（六边形模型天生不需要）
 *   - rgb2hsv 用"优先级掩码"消除 6 路分支；hsv2rgb 用 f(n) 公式
 *     （min/max/clamp）消除扇区分支；均可直接向量化
 *   - 仅剩 3 处整数除法：S=C/V、色相 /C、hsv2rgb 的 H/60
 *     （都可用"倒数表 + 乘法"进一步消除，见文末注释）
 *   - hsv2rgb 重建 (V*S*t)>>32 用四舍五入 (+2^31)，u8 全遍历往返 0 误差
 */
#include "hsv_fixed.h"
#include <stdio.h>

/* ---------------- 自测：文章示例色往返 ---------------- */
int main(void)
{
    static const struct { uint8_t r, g, b; const char *name; } tab[] = {
        {255,255,255, "#FFFFFF"}, {128,128,128, "#808080"}, {  0,  0,  0, "#000000"},
        {255,  0,  0, "#FF0000"}, {191,191,  0, "#BFBF00"}, {  0,128,  0, "#008000"},
        {128,255,255, "#80FFFF"}, {128,128,255, "#8080FF"}, {191, 64,191, "#BF40BF"},
        {160,164, 36, "#A0A424"}, { 65, 27,234, "#411BEA"}, {237,118, 81, "#ED7651"},
    };
    int i, n = (int)(sizeof(tab) / sizeof(tab[0]));
    int maxerr = 0;

    for (i = 0; i < n; i++) {
        hsv_fix_t hsv = rgb2hsv_fix(tab[i].r, tab[i].g, tab[i].b);
        uint8_t R, G, B;
        int dr, dg, db, err;

        hsv2rgb_fix(hsv.H, hsv.S, hsv.V, &R, &G, &B);

        dr = (int)R - (int)tab[i].r;
        dg = (int)G - (int)tab[i].g;
        db = (int)B - (int)tab[i].b;
        err = (dr < 0 ? -dr : dr) + (dg < 0 ? -dg : dg) + (db < 0 ? -db : db);
        if (err > maxerr)
            maxerr = err;

        /* 全部整数打印：H 显示 "度.百分度"，S 显示千分数，V 直接显示 */
        int h_deg  = (int)(hsv.H / FIX_ONE);
        int h_cent = (int)((hsv.H % FIX_ONE) * 100 / FIX_ONE);
        int s_pm   = (int)(((int64_t)hsv.S * 1000) / FIX_ONE);

        printf("%-8s H=%3d.%02d  S=%3d.%1d%%  V=%3d  ->  RGB(%3d,%3d,%3d)  err=(%+d,%+d,%+d)\n",
               tab[i].name, h_deg, h_cent, s_pm / 10, s_pm % 10, (int)hsv.V,
               R, G, B, dr, dg, db);
    }
    printf("max abs err (sum of |dR|+|dG|+|dB|) = %d / 765\n", maxerr);
    return 0;
}

/*
 * 进一步优化（可选）：
 * 1) 除法 -> 倒数表：S = C * rcpTbl[V]>>16；色相 /C 同理（rcpTbl 256 项即可）
 * 2) H/60 -> H * (FIX_ONE/60)>>16，即乘 1092（误差 <1/60 度，可接受）
 * 3) 全部比较选择(?: / if)在 ARM/NEON、x86 上编译为 CSEL/CMOV 或 setcc，
 *    天然无分支；若要纯位运算版，把 clamp01 与 mod 改为掩码 select 即可
 */
