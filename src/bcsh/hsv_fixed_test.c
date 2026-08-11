/**
 * hsv_fixed.c — RGB <-> HSV 定点(fixed-point)转换，全程无浮点数
 *
 * 定标约定（H/S 独立位宽归一化定点）：
 *   FIX_BITS_H = 14 : H 归一化，360° = 2^14 = 16384，有效范围 [0, FIX_H_ONE)
 *   FIX_BITS_S = 11 : S 归一化，1.0 = 2^11 = 2048，有效范围 [0, FIX_S_ONE]
 *   V : 明度，[0, 255]                  （与 8bit RGB 同尺度，不缩放）
 *
 * 特点：
 *   - 无任何 float/double、无三角函数（六边形模型天生不需要）
 *   - rgb2hsv 用"优先级掩码"消除 6 路分支；hsv2rgb 用 f(n) 公式
 *     （min/max/clamp）消除扇区分支；均可直接向量化
 *   - 除法全部消除：S=C/V、色相 /C 用倒数表；H 归一化后 hsv2rgb 的 h6=H*6 纯乘法
 *   - hsv2rgb 重建 (V*S*t)>>20 用四舍五入 (+2^19)，u8/u10 往返 0 误差
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
    const int u10_step = 1;
    int i, n = (int)(sizeof(tab) / sizeof(tab[0]));
    int maxerr = 0;

    for (i = 0; i < n; i++) {
        hsv_fix_t hsv = rgb2hsv_fix_u8(tab[i].r, tab[i].g, tab[i].b);
        uint8_t R, G, B;
        int dr, dg, db, err;

        hsv2rgb_fix_u8(hsv.H, hsv.S, hsv.V, &R, &G, &B);

        dr = (int)R - (int)tab[i].r;
        dg = (int)G - (int)tab[i].g;
        db = (int)B - (int)tab[i].b;
        err = (dr < 0 ? -dr : dr) + (dg < 0 ? -dg : dg) + (db < 0 ? -db : db);
        if (err > maxerr)
            maxerr = err;

        /* 全部整数打印：H 显示 "度.百分度"（H 归一化 360°=FIX_H_ONE），S 千分数，V 直接 */
        int h_deg  = (int)(hsv.H * 360 / FIX_H_ONE);
        int h_cent = (int)(hsv.H * 360 % FIX_H_ONE * 100 / FIX_H_ONE);
        int s_pm   = (int)(((int64_t)hsv.S * 1000) / FIX_S_ONE);

        printf("%-8s H=%3d.%02d  S=%3d.%1d%%  V=%3d  ->  RGB(%3d,%3d,%3d)  err=(%+d,%+d,%+d)\n",
               tab[i].name, h_deg, h_cent, s_pm / 10, s_pm % 10, (int)hsv.V,
               R, G, B, dr, dg, db);
    }
    printf("max abs err (sum of |dR|+|dG|+|dB|) = %d / 765\n", maxerr);

    /* ---------------- 往返 0 误差验证（u8 全遍历 + u10 抽样） ---------------- */
    printf("\n-- rgb->hsv->rgb 往返 0 误差验证（H=Q14/S=Q11 归一化定点）--\n");
    {
        uint64_t n8 = 0, e8 = 0, n10 = 0, e10 = 0;
        int maxerr8 = 0, maxerr10 = 0;
        for (int r = 0; r <= 255; r++)
            for (int g = 0; g <= 255; g++)
                for (int b = 0; b <= 255; b++) {
                    hsv_fix_t h = rgb2hsv_fix_u8((uint8_t)r, (uint8_t)g, (uint8_t)b);
                    uint8_t R, G, B;
                    hsv2rgb_fix_u8(h.H, h.S, h.V, &R, &G, &B);
                    int dr = (int)R - r;
                    if (dr < 0)
                        dr = -dr;
                    int dg = (int)G - g;
                    if (dg < 0)
                        dg = -dg;
                    int db = (int)B - b;
                    if (db < 0)
                        db = -db;
                    int e = dr > dg ? dr : dg;
                    if (db > e)
                        e = db;
                    if (e) {
                        e8++;
                        if (e > maxerr8)
                            maxerr8 = e;
                    }
                    n8++;
                }
        /* u10 抽样（1024^3 全遍历不可行，stride=7） */
        for (int r = 0; r <= 1023; r += u10_step)
            for (int g = 0; g <= 1023; g += u10_step)
                for (int b = 0; b <= 1023; b += u10_step) {
                    hsv_fix_t h = rgb2hsv_fix_u10(r, g, b);
                    int32_t R, G, B;
                    hsv2rgb_fix_u10(h.H, h.S, h.V, &R, &G, &B);
                    int dr = (int)R - r;
                    if (dr < 0)
                        dr = -dr;
                    int dg = (int)G - g;
                    if (dg < 0)
                        dg = -dg;
                    int db = (int)B - b;
                    if (db < 0)
                        db = -db;
                    int e = dr > dg ? dr : dg;
                    if (db > e)
                        e = db;
                    if (e) {
                        e10++;
                        if (e > maxerr10)
                            maxerr10 = e;
                    }
                    n10++;
                }
        printf("  u8  全遍历 n=%llu: 有偏差=%llu  max|Δ|=%d LSB  %s\n",
               (unsigned long long)n8, (unsigned long long)e8, maxerr8, e8 ? "FAIL" : "0 误差 OK");
        printf("  u10 %s n=%llu: 有偏差=%llu  max|Δ|=%d LSB  %s\n", u10_step > 1 ? "抽样 " : "全遍历",
               (unsigned long long)n10, (unsigned long long)e10, maxerr10, e10 ? "FAIL" : "0 误差 OK");
        printf("结论：%s\n", (e8 == 0 && e10 == 0)
            ? "H/S 14/11 bit 归一化定点下 u8/u10 往返均 0 误差" : "存在误差！");
    }
    return 0;
}

/*
 * 进一步优化（可选）：
 * 1) 除法 -> 倒数表：S = C * rcpTbl[V]>>16；色相 /C 同理（rcpTbl 256 项即可）
 * 2) H/60 -> H * (FIX_H_ONE/60)>>FIX_BITS_H，即乘 34（误差 <1/60 度，可接受）
 * 3) 全部比较选择(?: / if)在 ARM/NEON、x86 上编译为 CSEL/CMOV 或 setcc，
 *    天然无分支；若要纯位运算版，把 clamp01 与 mod 改为掩码 select 即可
 */
