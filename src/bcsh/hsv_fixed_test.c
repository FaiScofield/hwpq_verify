/**
 * hsv_fixed.c — RGB <-> HSV 定点(fixed-point)转换，全程无浮点数
 *
 * 定标约定（H/S 独立位宽归一化定点）：
 *   FIX_BITS_H = 14 : H 归一化，360° = 2^14 = 16384，有效范围 [0, FIX_H_ONE)
 *   FIX_BITS_S = 11 : S 归一化，1.0 = 2^11 = 2048，有效范围 [0, FIX_S_ONE]
 *   V : 明度，[0, 255/1023]，与 8/10bit RGB 同尺度，不缩放
 *
 * 特点：
 *   - 无任何 float/double、无三角函数（六边形模型天生不需要）
 *   - rgb2hsv 用"优先级掩码"消除 6 路分支；hsv2rgb 用 f(n) 公式
 *     （min/max/clamp）消除扇区分支；均可直接向量化
 *   - 除法全部消除：S=C/V、色相 /C 用倒数表；H 归一化后 hsv2rgb 的 h6=H*6 纯乘法
 *   - hsv2rgb 重建 (V*S*t)>>20 用四舍五入 (+2^19)，u8/u10 往返 0 误差
 */
#include "hsv_fixed.h"
#include "hsv_float.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#if defined(_WIN32)
#include <windows.h>
#else
#include <time.h>
#endif

/* 计时器 */
static double now_s(void)
{
#if defined(_WIN32)
    LARGE_INTEGER f, c;
    QueryPerformanceFrequency(&f);
    QueryPerformanceCounter(&c);
    return (double)c.QuadPart / (double)f.QuadPart;
#else
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec * 1e-9;
#endif
}

/* Q14/Q11 参考族函数指针（防内联，测真实调用开销） */
typedef void (*rgb2hsv_fn)(uint16_t, uint16_t, uint16_t, uint16_t *, uint16_t *, uint16_t *);
typedef void (*hsv2rgb_fn)(uint16_t, uint16_t, uint16_t, uint16_t, uint16_t *, uint16_t *, uint16_t *);

/* ---------------- 自测：文章示例色往返 ---------------- */
int main(int argc, char **argv)
{
    int step1 = 7;
    int step2 = (argc > 1) ? atoi(argv[1]) : step1;

    static const struct {
        uint8_t r, g, b;
        const char *name;
    } tab[] = {
        /* 灰度 */
        {255, 255, 255, "#FFFFFF"},
        {128, 128, 128, "#808080"},
        {0,   0,   0,   "#000000"},
        /* 六经典色（满饱） */
        {255, 0,   0,   "#FF0000"},
        {255, 255, 0,   "#FFFF00"},
        {0,   255, 0,   "#00FF00"},
        {0,   255, 255, "#00FFFF"},
        {0,   0,   255, "#0000FF"},
        {255, 0,   255, "#FF00FF"},
        /* 六经典色（中饱） */
        {191, 0,   0,   "#BF0000"},
        {191, 191, 0,   "#BFBF00"},
        {0,   128, 0,   "#008000"},
        {128, 255, 255, "#80FFFF"},
        {128, 128, 255, "#8080FF"},
        {191, 64,  191, "#BF40BF"},
        /* 杂色 */
        {160, 164, 36,  "#A0A424"},
        {65,  27,  234, "#411BEA"},
        {237, 118, 81,  "#ED7651"},
        /* 更多典型色 */
        {128, 0,   0,   "#800000"},
        {64,  64,  0,   "#404000"},
        {0,   64,  0,   "#004000"},
    };
    const int u10_step = 1;
    int i, n = (int)(sizeof(tab) / sizeof(tab[0]));
    int maxerr = 0;

    /* ---------------- Q14/Q11 文档参考族：精度 + 性能 ---------------- */
    if (1) {
        static const rgb2hsv_fn rfn[] = {
            /* rgb2hsv_v0_classic, rgb2hsv_v1_no_branch, rgb2hsv_v2_no_division, rgb2hsv_v3_optimal, */ rgb2hsv_v4_optimal};
        static const hsv2rgb_fn hfn[] = {
            /* hsv2rgb_v0_classic, hsv2rgb_v1_no_branch, hsv2rgb_v2_no_division, hsv2rgb_v3_optimal, */ hsv2rgb_v4_hexwalk};
        static const char *nm[] = {/* "v0_classic", "v1_no_branch", "v2_no_division", "v3_optimal",  */"v4_optimal"};
        const int nscen = sizeof(rfn) / sizeof(rfn[0]);

        printf("\n== Q%d/Q%d 文档参考族（v0/v1/v2/v3）精度与性能 ==\n", FIX_BITS_H, FIX_BITS_S);

        /* [a] rgb2hsv 精度：对比 float 参考（H 量化 Q14、S 量化 Q11），u8 全遍历 + u10 抽样 */
        printf("\n[a] rgb2hsv 精度（max|Δ| vs float 参考，Q%d/Q%d LSB, step_u10=%d）：\n", FIX_BITS_H, FIX_BITS_S, step1);
        for (int fi = 0; fi < nscen; fi++) {
            int mH8 = 0, mS8 = 0, mH10 = 0, mS10 = 0;
            for (int r = 0; r <= 255; r++) {
                for (int g = 0; g <= 255; g++) {
                    for (int b = 0; b <= 255; b++) {
                        hsv_f hf = rgb2hsv_float(r / 255.0f, g / 255.0f, b / 255.0f);
                        int Hr = ((int)lrintf(hf.H / 360.0f * (float)FIX_H_ONE)) & (FIX_H_ONE - 1);
                        int Sr = (int)lrintf(hf.S * (float)FIX_S_ONE);
                        if (Sr > FIX_S_ONE)
                            Sr = FIX_S_ONE;
                        uint16_t h13, s11, v10;
                        rfn[fi](r, g, b, &h13, &s11, &v10);
                        int dH = abs(h13 - Hr);
                        if (dH > FIX_H_ONE / 2)
                            dH = FIX_H_ONE - dH; /* 圆环距离 */
                        int dS = abs(s11 - Sr);
                        if (dH > mH8)
                            mH8 = dH;
                        if (dS > mS8)
                            mS8 = dS;
                    }
                }
            }
            for (int r = 0; r <= 1023; r += step1) {
                for (int g = 0; g <= 1023; g += step1) {
                    for (int b = 0; b <= 1023; b += step1) {
                        hsv_f hf = rgb2hsv_float(r / 1023.0f, g / 1023.0f, b / 1023.0f);
                        int Hr = ((int)lrintf(hf.H / 360.0f * (float)FIX_H_ONE)) & (FIX_H_ONE - 1);
                        int Sr = (int)lrintf(hf.S * (float)FIX_S_ONE);
                        if (Sr > FIX_S_ONE)
                            Sr = FIX_S_ONE;
                        uint16_t h13, s11, v10;
                        rfn[fi](r, g, b, &h13, &s11, &v10);
                        int dH = abs(h13 - Hr);
                        if (dH > FIX_H_ONE / 2)
                            dH = FIX_H_ONE - dH; /* 圆环距离 */
                        int dS = abs(s11 - Sr);
                        if (dH > mH10)
                            mH10 = dH;
                        if (dS > mS10)
                            mS10 = dS;
                    }
                }
            }
            printf("  rgb2hsv_%-20s u8: ΔH=%2d ΔS=%2d | u10抽样: ΔH=%2d ΔS=%2d\n", nm[fi], mH8, mS8, mH10, mS10);
        }

        /* [b] hsv2rgb 精度：对比 float 参考，u8 全遍历 + u10 抽样/全遍历 */
        printf("\n[b] hsv2rgb 精度（max|Δ| vs float 参考，u8/u10 LSB）：\n");
        for (int fi = 0; fi < nscen; fi++) {
            int mE8 = 0, mE10 = 0;
            for (int H = 0; H < FIX_H_ONE; H += FIX_H_ONE / 128) {
                for (int S = 0; S <= FIX_S_ONE; S += FIX_S_ONE / 64) {
                    for (int V = 0; V <= 255; V += 17) {
                        float Rf, Gf, Bf;
                        hsv2rgb_float(H / (float)FIX_H_ONE * 360.0f, S / (float)FIX_S_ONE, V / 255.0f, &Rf, &Gf, &Bf);
                        int Rr = (int)lrintf(Rf * 255.0f);
                        int Gr = (int)lrintf(Gf * 255.0f);
                        int Br = (int)lrintf(Bf * 255.0f);
                        uint16_t R, G, B;
                        hfn[fi](H, S, V, 255, &R, &G, &B);
                        int e = abs(R - Rr);
                        if (abs(G - Gr) > e)
                            e = abs(G - Gr);
                        if (abs(B - Br) > e)
                            e = abs(B - Br);
                        if (e > mE8)
                            mE8 = e;
                    }
                }
                /* u10：H/S 抽样同 u8，V 步长 step_u10（=1 时 V 全遍历） */
                for (int S = 0; S <= FIX_S_ONE; S += FIX_S_ONE / 64) {
                    for (int V = 0; V <= 1023; V += step1) {
                        float Rf, Gf, Bf;
                        hsv2rgb_float(H / (float)FIX_H_ONE * 360.0f, S / (float)FIX_S_ONE, V / 1023.0f, &Rf, &Gf, &Bf);
                        int Rr = (int)lrintf(Rf * 1023.0f);
                        int Gr = (int)lrintf(Gf * 1023.0f);
                        int Br = (int)lrintf(Bf * 1023.0f);
                        uint16_t R, G, B;
                        hfn[fi](H, S, V, 1023, &R, &G, &B);
                        int e = abs(R - Rr);
                        if (abs(G - Gr) > e)
                            e = abs(G - Gr);
                        if (abs(B - Br) > e)
                            e = abs(B - Br);
                        if (e > mE10)
                            mE10 = e;
                    }
                }
            }
            printf("  hsv2rgb_%-20s u8: max|Δ|=%2d LSB | u10%s: max|Δ|=%2d LSB\n", nm[fi], mE8,
                step2 > 1 ? "抽样" : "全遍历", mE10);
        }

        /* [c] 往返精度：rgb2hsv_vx -> hsv2rgb_vx，u8 全遍历 + u10 抽样/全遍历 */
        printf("\n[c] 往返精度（同版本配对，u8 全遍历 + u10 %s）：\n", step2 > 1 ? "抽样" : "全遍历");
        for (int fi = 0; fi < nscen; fi++) {
            int mE8 = 0, mE10 = 0;
            for (int r = 0; r <= 255; r++) {
                for (int g = 0; g <= 255; g++) {
                    for (int b = 0; b <= 255; b++) {
                        uint16_t h13, s11, v10, R, G, B;
                        rfn[fi](r, g, b, &h13, &s11, &v10);
                        hfn[fi](h13, s11, v10, 255, &R, &G, &B);
                        int e = abs(R - r);
                        if (abs(G - g) > e)
                            e = abs(G - g);
                        if (abs(B - b) > e)
                            e = abs(B - b);
                        if (e > mE8)
                            mE8 = e;
                    }
                }
            }
            for (int r = 0; r <= 1023; r += step2) {
                for (int g = 0; g <= 1023; g += step2) {
                    for (int b = 0; b <= 1023; b += step2) {
                        uint16_t h13, s11, v10, R, G, B;
                        rfn[fi](r, g, b, &h13, &s11, &v10);
                        hfn[fi](h13, s11, v10, 1023, &R, &G, &B);
                        int e = abs(R - r);
                        if (abs(G - g) > e)
                            e = abs(G - g);
                        if (abs(B - b) > e)
                            e = abs(B - b);
                        if (e > mE10)
                            mE10 = e;
                    }
                }
            }
            printf("  rgb<->hsv_%-20s u8: max|Δ|=%2d LSB | u10%s: max|Δ|=%2d LSB\n", nm[fi], mE8,
                step2 > 1 ? "抽样" : "全遍历", mE10);
        }

        /* [d] 性能：100 万像素，LCG 输入，函数指针调用 */
        printf("\n[d] 性能（ns/px，100 万像素，函数指针调用防内联）：\n");
        {
#define NPERF 1000000
            static int32_t px[NPERF], py[NPERF], pz[NPERF];
            static int32_t qx[NPERF], qy[NPERF], qz[NPERF];
            uint32_t sd = 0x12345678u;
            for (int i = 0; i < NPERF; i++) {
                sd = sd * 1664525u + 1013904223u;
                px[i] = (int32_t)(sd >> 24);
                py[i] = (int32_t)((sd >> 16) & 255u);
                pz[i] = (int32_t)((sd >> 8) & 255u);
                qx[i] = (int32_t)((sd >> 16) & (uint32_t)(FIX_H_ONE - 1)); /* H Q(FIX_BITS_H) */
                qy[i] = (int32_t)((sd >> 8) & (uint32_t)(FIX_S_ONE - 1));  /* S Q(FIX_BITS_S) */
                qz[i] = (int32_t)(sd & 255u);                              /* V */
            }
            for (int fi = 0; fi < nscen; fi++) {
                uint16_t h, s, v;
                int32_t acc = 0;
                double t0 = now_s();
                for (int i = 0; i < NPERF; i++) {
                    rfn[fi](px[i], py[i], pz[i], &h, &s, &v);
                    acc += h + s + v;
                }
                double t1 = now_s();
                printf("  rgb2hsv_%-20s %9.2f ns/px\n", nm[fi], (t1 - t0) * 1e9 / NPERF);
            }
            for (int fi = 0; fi < nscen; fi++) {
                uint16_t R, G, B;
                int32_t acc = 0;
                double t0 = now_s();
                for (int i = 0; i < NPERF; i++) {
                    hfn[fi](qx[i], qy[i], qz[i], 255, &R, &G, &B);
                    acc += R + G + B;
                }
                double t1 = now_s();
                printf("  hsv2rgb_%-20s %9.2f ns/px\n", nm[fi], (t1 - t0) * 1e9 / NPERF);
            }
#undef NPERF
        }
    }

    /* ---------------- v4_hexwalk：正确性专项 ---------------- */
    if (0) {
        printf("\n== hsv2rgb_v4_hexwalk 正确性专项 ==\n");

        /* [e1] hsv2rgb 精度 vs float 参考（抽样同 [b]） */
        {
            int mE8 = 0, mE10 = 0;
            for (int H = 0; H < FIX_H_ONE; H += FIX_H_ONE / 128) {
                for (int S = 0; S <= FIX_S_ONE; S += FIX_S_ONE / 64) {
                    for (int V = 0; V <= 255; V += 17) {
                        float Rf, Gf, Bf;
                        hsv2rgb_float(H / (float)FIX_H_ONE * 360.0f, S / (float)FIX_S_ONE, V / 255.0f, &Rf, &Gf, &Bf);
                        int Rr = (int)lrintf(Rf * 255.0f);
                        int Gr = (int)lrintf(Gf * 255.0f);
                        int Br = (int)lrintf(Bf * 255.0f);
                        uint16_t R, G, B;
                        hsv2rgb_v4_hexwalk(H, S, V, 255, &R, &G, &B);
                        int e = abs(R - Rr);
                        if (abs(G - Gr) > e)
                            e = abs(G - Gr);
                        if (abs(B - Br) > e)
                            e = abs(B - Br);
                        if (e > mE8)
                            mE8 = e;
                    }
                }
                for (int S = 0; S <= FIX_S_ONE; S += FIX_S_ONE / 64) {
                    for (int V = 0; V <= 1023; V += step1) {
                        float Rf, Gf, Bf;
                        hsv2rgb_float(H / (float)FIX_H_ONE * 360.0f, S / (float)FIX_S_ONE, V / 1023.0f, &Rf, &Gf, &Bf);
                        int Rr = (int)lrintf(Rf * 1023.0f);
                        int Gr = (int)lrintf(Gf * 1023.0f);
                        int Br = (int)lrintf(Bf * 1023.0f);
                        uint16_t R, G, B;
                        hsv2rgb_v4_hexwalk(H, S, V, 1023, &R, &G, &B);
                        int e = abs(R - Rr);
                        if (abs(G - Gr) > e)
                            e = abs(G - Gr);
                        if (abs(B - Br) > e)
                            e = abs(B - Br);
                        if (e > mE10)
                            mE10 = e;
                    }
                }
            }
            printf("  [e1] hsv2rgb_v4_hexwalk vs float: u8 max|Δ|=%2d LSB | u10抽样 max|Δ|=%2d LSB\n", mE8, mE10);
        }

        /* [e2] 往返 rgb2hsv_v3 -> hsv2rgb_v4（v3 即 fix_u8/u10 包装用的正向），u8 全遍历 + u10 全遍历/抽样 */
        {
            int mE8 = 0, mE10 = 0;
            for (int r = 0; r <= 255; r++)
                for (int g = 0; g <= 255; g++)
                    for (int b = 0; b <= 255; b++) {
                        uint16_t h13, s11, v10, R, G, B;
                        rgb2hsv_v3_optimal(r, g, b, &h13, &s11, &v10);
                        hsv2rgb_v4_hexwalk(h13, s11, v10, 255, &R, &G, &B);
                        int e = abs(R - r);
                        if (abs(G - g) > e)
                            e = abs(G - g);
                        if (abs(B - b) > e)
                            e = abs(B - b);
                        if (e > mE8)
                            mE8 = e;
                    }
            for (int r = 0; r <= 1023; r += step2)
                for (int g = 0; g <= 1023; g += step2)
                    for (int b = 0; b <= 1023; b += step2) {
                        uint16_t h13, s11, v10, R, G, B;
                        rgb2hsv_v3_optimal(r, g, b, &h13, &s11, &v10);
                        hsv2rgb_v4_hexwalk(h13, s11, v10, 1023, &R, &G, &B);
                        int e = abs(R - r);
                        if (abs(G - g) > e)
                            e = abs(G - g);
                        if (abs(B - b) > e)
                            e = abs(B - b);
                        if (e > mE10)
                            mE10 = e;
                    }
            printf("  [e2] v3->v4 往返: \t\tu8 max|Δ|=%2d LSB | u10%s max|Δ|=%2d LSB\n", mE8,
                step2 > 1 ? "抽样" : "全遍历", mE10);
        }

        /* [e5] rgb2hsv_v4 vs v3：H/S 精度对比（v4 仅用 rcp 表 + 移位多项式 /6；u8 全遍历 + u10 抽样） */
        {
            int mH8 = 0, mS8 = 0, mH10 = 0, mS10 = 0;
            for (int r = 0; r <= 255; r++)
                for (int g = 0; g <= 255; g++)
                    for (int b = 0; b <= 255; b++) {
                        uint16_t h3, s3, v3, h4, s4, v4;
                        rgb2hsv_v3_optimal(r, g, b, &h3, &s3, &v3);
                        rgb2hsv_v4_optimal(r, g, b, &h4, &s4, &v4);
                        int dH = abs(h3 - h4);
                        if (dH > FIX_H_ONE / 2)
                            dH = FIX_H_ONE - dH; /* 圆环距离 */
                        int dS = abs(s3 - s4);
                        if (dH > mH8)
                            mH8 = dH;
                        if (dS > mS8)
                            mS8 = dS;
                    }
            for (int r = 0; r <= 1023; r += step2)
                for (int g = 0; g <= 1023; g += step2)
                    for (int b = 0; b <= 1023; b += step2) {
                        uint16_t h3, s3, v3, h4, s4, v4;
                        rgb2hsv_v3_optimal(r, g, b, &h3, &s3, &v3);
                        rgb2hsv_v4_optimal(r, g, b, &h4, &s4, &v4);
                        int dH = abs(h3 - h4);
                        if (dH > FIX_H_ONE / 2)
                            dH = FIX_H_ONE - dH;
                        int dS = abs(s3 - s4);
                        if (dH > mH10)
                            mH10 = dH;
                        if (dS > mS10)
                            mS10 = dS;
                    }
            printf("  [e5] rgb2hsv v4 vs v3: \tu8 H=%2d S=%2d | u10%s H=%2d S=%2d (Q14/Q11 LSB)\n", mH8, mS8,
                step2 > 1 ? "抽样" : "全遍历", mH10, mS10);
        }

        /* [e6] 往返重建（hsv2rgb_v4_hexwalk）：v3 往返 vs v4 往返 vs 两者输出差（u8 全遍历 + u10 抽样） */
        {
            int m3 = 0, m4 = 0, m34 = 0, m3_10 = 0, m4_10 = 0, m34_10 = 0;
            for (int r = 0; r <= 255; r++)
                for (int g = 0; g <= 255; g++)
                    for (int b = 0; b <= 255; b++) {
                        uint16_t h3, s3, v3, h4, s4, v4, R3, G3, B3, R4, G4, B4;
                        rgb2hsv_v3_optimal(r, g, b, &h3, &s3, &v3);
                        hsv2rgb_v4_hexwalk(h3, s3, v3, 255, &R3, &G3, &B3);
                        rgb2hsv_v4_optimal(r, g, b, &h4, &s4, &v4);
                        hsv2rgb_v4_hexwalk(h4, s4, v4, 255, &R4, &G4, &B4);
                        int e3 = abs(R3 - r), e4 = abs(R4 - r);
                        if (abs(G3 - g) > e3)
                            e3 = abs(G3 - g);
                        if (abs(B3 - b) > e3)
                            e3 = abs(B3 - b);
                        if (abs(G4 - g) > e4)
                            e4 = abs(G4 - g);
                        if (abs(B4 - b) > e4)
                            e4 = abs(B4 - b);
                        int d34 = abs(R3 - R4);
                        if (abs(G3 - G4) > d34)
                            d34 = abs(G3 - G4);
                        if (abs(B3 - B4) > d34)
                            d34 = abs(B3 - B4);
                        if (e3 > m3)
                            m3 = e3;
                        if (e4 > m4)
                            m4 = e4;
                        if (d34 > m34)
                            m34 = d34;
                    }
            for (int r = 0; r <= 1023; r += step2)
                for (int g = 0; g <= 1023; g += step2)
                    for (int b = 0; b <= 1023; b += step2) {
                        uint16_t h3, s3, v3, h4, s4, v4, R3, G3, B3, R4, G4, B4;
                        rgb2hsv_v3_optimal(r, g, b, &h3, &s3, &v3);
                        hsv2rgb_v4_hexwalk(h3, s3, v3, 1023, &R3, &G3, &B3);
                        rgb2hsv_v4_optimal(r, g, b, &h4, &s4, &v4);
                        hsv2rgb_v4_hexwalk(h4, s4, v4, 1023, &R4, &G4, &B4);
                        int e3 = abs(R3 - r), e4 = abs(R4 - r);
                        if (abs(G3 - g) > e3)
                            e3 = abs(G3 - g);
                        if (abs(B3 - b) > e3)
                            e3 = abs(B3 - b);
                        if (abs(G4 - g) > e4)
                            e4 = abs(G4 - g);
                        if (abs(B4 - b) > e4)
                            e4 = abs(B4 - b);
                        int d34 = abs(R3 - R4);
                        if (abs(G3 - G4) > d34)
                            d34 = abs(G3 - G4);
                        if (abs(B3 - B4) > d34)
                            d34 = abs(B3 - B4);
                        if (e3 > m3_10)
                            m3_10 = e3;
                        if (e4 > m4_10)
                            m4_10 = e4;
                        if (d34 > m34_10)
                            m34_10 = d34;
                    }
            printf(
                "  [e6] 往返重建(v4_hexwalk): \tu8 v3=%2d v4=%2d v3-vs-v4=%2d | u10%s v3=%2d v4=%2d v3-vs-v4=%2d LSB\n",
                m3, m4, m34, step2 > 1 ? "抽样" : "全遍历", m3_10, m4_10, m34_10);
        }

        /* [e3] 与 hsv2rgb_v3 输出一致性（同输入 max diff） */
        {
            int mE8 = 0, mE10 = 0;
            for (int H = 0; H < FIX_H_ONE; H += FIX_H_ONE / 256) {
                for (int S = 0; S <= FIX_S_ONE; S += FIX_S_ONE / 128) {
                    for (int V = 0; V <= 255; V += 7) {
                        uint16_t R3, G3, B3, R4, G4, B4;
                        hsv2rgb_v3_optimal(H, S, V, 255, &R3, &G3, &B3);
                        hsv2rgb_v4_hexwalk(H, S, V, 255, &R4, &G4, &B4);
                        int e = abs(R3 - R4);
                        if (abs(G3 - G4) > e)
                            e = abs(G3 - G4);
                        if (abs(B3 - B4) > e)
                            e = abs(B3 - B4);
                        if (e > mE8)
                            mE8 = e;
                    }
                    for (int V = 0; V <= 1023; V += step1) {
                        uint16_t R3, G3, B3, R4, G4, B4;
                        hsv2rgb_v3_optimal(H, S, V, 1023, &R3, &G3, &B3);
                        hsv2rgb_v4_hexwalk(H, S, V, 1023, &R4, &G4, &B4);
                        int e = abs(R3 - R4);
                        if (abs(G3 - G4) > e)
                            e = abs(G3 - G4);
                        if (abs(B3 - B4) > e)
                            e = abs(B3 - B4);
                        if (e > mE10)
                            mE10 = e;
                    }
                }
            }
            printf("  [e3] v4 vs v3 一致性:\t\tu8 max|Δ|=%2d LSB | u10抽样 max|Δ|=%2d LSB\n", mE8, mE10);
        }

        /* [e4] 性能（100 万像素，同 [d] 输入分布） */
        {
#define NPERF4 1000000
            static int32_t qx[NPERF4], qy[NPERF4], qz[NPERF4];
            uint32_t sd = 0x12345678u;
            for (int i = 0; i < NPERF4; i++) {
                sd = sd * 1664525u + 1013904223u;
                qx[i] = (int32_t)((sd >> 16) & (uint32_t)(FIX_H_ONE - 1)); /* H Q(FIX_BITS_H) */
                qy[i] = (int32_t)((sd >> 8) & (uint32_t)(FIX_S_ONE - 1));  /* S Q(FIX_BITS_S) */
                qz[i] = (int32_t)(sd & 255u);                              /* V */
            }
            uint16_t R, G, B;
            int32_t acc = 0;
            double t0 = now_s();
            for (int i = 0; i < NPERF4; i++) {
                hsv2rgb_v4_hexwalk(qx[i], qy[i], qz[i], 255, &R, &G, &B);
                acc += R + G + B;
            }
            double t1 = now_s();
            printf("  [e4] hsv2rgb_v4_hexwalk\t %9.2f ns/px\n", (t1 - t0) * 1e9 / NPERF4);
#undef NPERF4
        }
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
