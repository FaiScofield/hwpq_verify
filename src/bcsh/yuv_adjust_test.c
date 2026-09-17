/**
 * yuv_adjust_test.c — YCbCr 域固定管线 BCSH（C -> B -> S -> H -> 色域处理）精度与性能对比
 *
 * 对比对象：
 *   fix   : adjust_yuv_fix  （Q11 定点，无浮点、无 math 库依赖）
 *   float : adjust_yuv_float（float 参考实现，精度基准）
 *
 * 固定模式：modeC=MulAtMidPoint / modeB=ModeAdd / modeS=ModeMul / modeH=ModeAdd，
 *           外加 CompLumaFirst 开关（HARDCLIP / COMP_LUMA_FIRST）。
 *
 * 精度：各调整场景下逐像素对比输出（max/mean |diff| LSB、非零占比），u8 与 u10；
 *       并验证中性参数恒等与 3 种 Y2R 色域（BT.601/709/2020，CompLumaFirst 用）。
 *       为只反映管线计算误差，float 侧使用与定点一致的参数（先量化 Q11/Q14 再回读）。
 * 性能：整帧多轮迭代计时（ns/px、MP/s），fix vs float。
 *
 * 用法: yuv_adjust_test [n_pixels] [iters]   （默认 1920*1080, 30）
 * 建议以 Release（-O2/-O3）构建以获得有意义的性能数据。
 */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <math.h>
#include "yuv_adjust.h"

/* 色度存储中心（帧缓冲布局：去中心值 + center） */
#define UV_CENTER8  128
#define UV_CENTER10 512

/* ---------------- high-resolution timer ---------------- */
#if defined(_WIN32)
#include <windows.h>
static double now_sec(void)
{
    static LARGE_INTEGER freq;
    static int ready = 0;
    if (!ready) {
        QueryPerformanceFrequency(&freq);
        ready = 1;
    }
    LARGE_INTEGER c;
    QueryPerformanceCounter(&c);
    return (double)c.QuadPart / (double)freq.QuadPart;
}
#else
#include <time.h>
static double now_sec(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec * 1e-9;
}
#endif

/* ---------------- deterministic LCG ---------------- */
static uint32_t lcg_state = 0x12345678u;
static uint32_t lcg_next(void)
{
    lcg_state = lcg_state * 1664525u + 1013904223u;
    return lcg_state;
}

/* ---------------- adjustment scenario (physical quantities) ---------------- */
typedef struct {
    const char *name;
    float gain_c;    /* [0,4]，中性 1.0（MulAtMidPoint） */
    float delta_b;   /* [-1,1]，中性 0（ModeAdd） */
    float delta_s;   /* [0,4]，中性 1.0（ModeMul） */
    float angle_deg; /* [-180,180]，中性 0（ModeAdd 极角旋转） */
} yuv_params_t;

static const yuv_params_t k_scen[] = {
    {"identity    gc=1.0  db=0     ds=1.0  ang=0",    1.00f, 0.00f, 1.00f,   0.0f},
    {"C 0.5       gc=0.5",                            0.50f, 0.00f, 1.00f,   0.0f},
    {"C 1.5       gc=1.5",                            1.50f, 0.00f, 1.00f,   0.0f},
    {"B +0.1      db=+0.1",                           1.00f, 0.10f, 1.00f,   0.0f},
    {"B -0.1      db=-0.1",                           1.00f, -0.10f, 1.00f,  0.0f},
    {"S 0.5       ds=0.5",                            1.00f, 0.00f, 0.50f,   0.0f},
    {"S 1.5       ds=1.5",                            1.00f, 0.00f, 1.50f,   0.0f},
    {"S 2.5       ds=2.5（色度越界）",                1.00f, 0.00f, 2.50f,   0.0f},
    {"H +45deg    ang=+45",                           1.00f, 0.00f, 1.00f,  45.0f},
    {"H 180deg    ang=180",                           1.00f, 0.00f, 1.00f, 180.0f},
    {"typical     gc=1.2  db=+0.05 ds=1.3  ang=+30",  1.20f, 0.05f, 1.30f,  30.0f},
    {"extreme     gc=2.0  db=+0.5  ds=2.0  ang=180",  2.00f, 0.50f, 2.00f, 180.0f},
};
#define N_SCEN ((int)(sizeof(k_scen) / sizeof(k_scen[0])))

/* 色域矩阵覆盖（CompLumaFirst 的可行区间求解） */
static const yuv_params_t k_cs_scen[] = {
    {"Y2R BT601 ", 1.20f, 0.05f, 1.30f, 30.0f},
    {"Y2R BT709 ", 1.20f, 0.05f, 1.30f, 30.0f},
    {"Y2R BT2020", 1.20f, 0.05f, 1.30f, 30.0f},
};
static const int k_cs_code[] = {ADJ_YUV_CS_BT601, ADJ_YUV_CS_BT709, ADJ_YUV_CS_BT2020};
#define N_CS ((int)(sizeof(k_cs_scen) / sizeof(k_cs_scen[0])))

/* ---------------- parameter quantization (u8/u10 share the same Q formats) ---------------- */
static int32_t q11(float v) { return (int32_t)lrintf(v * (float)FIX_S_ONE); }
static int32_t q14_deg(float deg) { return (int32_t)lrintf(deg / 360.0f * (float)FIX_H_ONE); }

/* float 侧使用与定点一致的量化参数（回读），使对比只反映管线计算误差 */
static float q11_f(float v) { return (float)q11(v) / (float)FIX_S_ONE; }
static float q14_deg_f(float deg) { return (float)q14_deg(deg) / (float)FIX_H_ONE * 360.0f; }

static inline int clampi(int v, int lo, int hi) { return v < lo ? lo : (v > hi ? hi : v); }

/* ---------------- buffered paths ---------------- */
/* 输出布局与输入一致：out[3i]=Y、out[3i+1]=Cb（去中心带符号）、out[3i+2]=Cr
   （不偏移、不钳位，便于直接比较；Y 已在函数内钳位） */
static void run_fix_u8(const uint8_t *in, int n, int32_t gc, int32_t db, int32_t ds, int32_t ang, int gamut, int cs,
    int16_t *out)
{
    for (int i = 0; i < n; i++) {
        uint16_t yo;
        int32_t cbo, cro;
        adjust_yuv_fix(in[3 * i], (int32_t)in[3 * i + 1] - UV_CENTER8, (int32_t)in[3 * i + 2] - UV_CENTER8, 255, gc,
            db, ds, ang, gamut, cs, &yo, &cbo, &cro);
        out[3 * i] = (int16_t)yo;
        out[3 * i + 1] = (int16_t)cbo;
        out[3 * i + 2] = (int16_t)cro;
    }
}

static void run_flt_u8(const uint8_t *in, int n, float gc, float db, float ds, float ang, int gamut, int cs,
    int16_t *out)
{
    const float inv = 1.0f / 255.0f;
    for (int i = 0; i < n; i++) {
        float yo, cbo, cro;
        adjust_yuv_float(in[3 * i] * inv, (float)((int32_t)in[3 * i + 1] - UV_CENTER8) * inv,
            (float)((int32_t)in[3 * i + 2] - UV_CENTER8) * inv, gc, db, ds, ang, gamut, cs, &yo, &cbo, &cro);
        out[3 * i] = (int16_t)lrintf(yo * 255.0f);
        out[3 * i + 1] = (int16_t)lrintf(cbo * 255.0f);
        out[3 * i + 2] = (int16_t)lrintf(cro * 255.0f);
    }
}

static void run_fix_u10(const uint16_t *in, int n, int32_t gc, int32_t db, int32_t ds, int32_t ang, int gamut, int cs,
    int16_t *out)
{
    for (int i = 0; i < n; i++) {
        uint16_t yo;
        int32_t cbo, cro;
        adjust_yuv_fix(in[3 * i], (int32_t)in[3 * i + 1] - UV_CENTER10, (int32_t)in[3 * i + 2] - UV_CENTER10, 1023, gc,
            db, ds, ang, gamut, cs, &yo, &cbo, &cro);
        out[3 * i] = (int16_t)yo;
        out[3 * i + 1] = (int16_t)cbo;
        out[3 * i + 2] = (int16_t)cro;
    }
}

static void run_flt_u10(const uint16_t *in, int n, float gc, float db, float ds, float ang, int gamut, int cs,
    int16_t *out)
{
    const float inv = 1.0f / 1023.0f;
    for (int i = 0; i < n; i++) {
        float yo, cbo, cro;
        adjust_yuv_float(in[3 * i] * inv, (float)((int32_t)in[3 * i + 1] - UV_CENTER10) * inv,
            (float)((int32_t)in[3 * i + 2] - UV_CENTER10) * inv, gc, db, ds, ang, gamut, cs, &yo, &cbo, &cro);
        out[3 * i] = (int16_t)lrintf(yo * 1023.0f);
        out[3 * i + 1] = (int16_t)lrintf(cbo * 1023.0f);
        out[3 * i + 2] = (int16_t)lrintf(cro * 1023.0f);
    }
}

/* ---------------- diff statistics ---------------- */
typedef struct {
    int max_d;     /* max per-channel |diff| (LSB) */
    double mean_d; /* mean per-channel |diff| */
    long long nz;  /* samples with |diff| > 0 */
    long long big; /* samples with |diff| > 1 */
    long long total;
} dstats_t;

static dstats_t dstats16(const int16_t *a, const int16_t *b, int n)
{
    dstats_t s = {0, 0.0, 0, 0, (long long)3 * n};
    long long sum = 0;
    for (int i = 0; i < 3 * n; i++) {
        int d = (int)a[i] - (int)b[i];
        if (d < 0)
            d = -d;
        if (d > s.max_d)
            s.max_d = d;
        if (d > 0)
            s.nz++;
        if (d > 1)
            s.big++;
        sum += d;
    }
    s.mean_d = (double)sum / (double)s.total;
    return s;
}

/* FNV-1a checksum, so timing-loop outputs cannot be elided */
static uint64_t cs16in(const int16_t *p, int n)
{
    uint64_t h = 1469598103934665603ull;
    for (int i = 0; i < 3 * n; i++) {
        h ^= (uint64_t)(uint16_t)p[i];
        h *= 1099511628211ull;
    }
    return h;
}

/* BT.709 Y2R 的 Cb/Cr 两列（测试侧独立副本，用于把输出还原成 RGB 判越界） */
static const float s_test_y2r_cbcr[3][2] = {
    {0.0f, 1.5748f}, {-0.187324f, -0.468124f}, {1.8556f, 0.0f}};

/* 把归一化 (Y,Cb,Cr) 还原为 RGB，返回超出 [0,1] 的最大越界量（0 表示完全在域内） */
static float rgb_excursion(float y, float cb, float cr)
{
    float lo = 1e9f, hi = -1e9f;
    for (int i = 0; i < 3; i++) {
        const float v = y + s_test_y2r_cbcr[i][0] * cb + s_test_y2r_cbcr[i][1] * cr;
        if (v < lo)
            lo = v;
        if (v > hi)
            hi = v;
    }
    const float e = fmaxf(-lo, hi - 1.0f);
    return e > 0.0f ? e : 0.0f;
}

/* ---------------- main ---------------- */
int main(int argc, char **argv)
{
    int n = 1920 * 1080;
    int iters = 30;
    if (argc > 1) {
        n = atoi(argv[1]);
        if (n < 1)
            n = 1;
    }
    if (argc > 2) {
        iters = atoi(argv[2]);
        if (iters < 1)
            iters = 1;
    }

    uint8_t *in8 = (uint8_t *)malloc(3 * (size_t)n);
    uint16_t *in10 = (uint16_t *)malloc(3 * (size_t)n * sizeof(uint16_t));
    int16_t *fix8 = (int16_t *)malloc(3 * (size_t)n * sizeof(int16_t));
    int16_t *flt8 = (int16_t *)malloc(3 * (size_t)n * sizeof(int16_t));
    int16_t *fix10 = (int16_t *)malloc(3 * (size_t)n * sizeof(int16_t));
    int16_t *flt10 = (int16_t *)malloc(3 * (size_t)n * sizeof(int16_t));
    if (!in8 || !in10 || !fix8 || !flt8 || !fix10 || !flt10) {
        printf("malloc failed\n");
        return 1;
    }
    /* 输入 Y 全域随机；Cb/Cr 取 [1,255]/[1,1023] 存储值 => 去中心后 [-(maxv/2), maxv/2]
       （天然在格式范围内，故中性参数下硬钳恒等） */
    for (int i = 0; i < n; i++) {
        in8[3 * i] = (uint8_t)(lcg_next() >> 24);
        in8[3 * i + 1] = (uint8_t)(lcg_next() % 255u) + 1;
        in8[3 * i + 2] = (uint8_t)(lcg_next() % 255u) + 1;
        in10[3 * i] = (uint16_t)(lcg_next() >> 22) & 1023u;
        in10[3 * i + 1] = (uint16_t)(lcg_next() % 1023u) + 1;
        in10[3 * i + 2] = (uint16_t)(lcg_next() % 1023u) + 1;
    }

    printf("== YCbCr fixed pipeline BCSH: fix (Q11) vs float reference ==\n");
    printf("   fixed modes: C=MulAtMidPoint B=ModeAdd S=ModeMul H=ModeAdd (+CompLumaFirst switch)\n");
    printf("n_pixels = %d (%.2f MP), iters = %d\n\n", n, (double)n / 1e6, iters);

    /* ---------------- precision: all scenarios x both gamut modes ---------------- */
    static const char *gamut_name[2] = {"HardClip", "CompLumaFirst"};
    printf("-- precision: fix vs float (per-channel |diff| in LSB; mean/%% over 3*%d samples) --\n", n);
    for (int g = 0; g < 2; g++) {
        printf("[gamut = %s]\n", gamut_name[g]);
        for (int s = 0; s < N_SCEN; s++) {
            const yuv_params_t *p = &k_scen[s];
            const int32_t gc = q11(p->gain_c), db = q11(p->delta_b), ds = q11(p->delta_s), ang = q14_deg(p->angle_deg);
            const float gcf = q11_f(p->gain_c), dbf = q11_f(p->delta_b), dsf = q11_f(p->delta_s),
                        angf = q14_deg_f(p->angle_deg);
            run_fix_u8(in8, n, gc, db, ds, ang, g, ADJ_YUV_CS_BT709, fix8);
            run_flt_u8(in8, n, gcf, dbf, dsf, angf, g, ADJ_YUV_CS_BT709, flt8);
            dstats_t d8 = dstats16(fix8, flt8, n);
            run_fix_u10(in10, n, gc, db, ds, ang, g, ADJ_YUV_CS_BT709, fix10);
            run_flt_u10(in10, n, gcf, dbf, dsf, angf, g, ADJ_YUV_CS_BT709, flt10);
            dstats_t d10 = dstats16(fix10, flt10, n);
            printf("  [%s]\n", p->name);
            printf("    u8 : max=%d mean=%.4f nz=%.3f%% gt1=%.4f%%\n", d8.max_d, d8.mean_d,
                100.0 * (double)d8.nz / (double)d8.total, 100.0 * (double)d8.big / (double)d8.total);
            printf("    u10: max=%d mean=%.4f nz=%.3f%% gt1=%.4f%%\n", d10.max_d, d10.mean_d,
                100.0 * (double)d10.nz / (double)d10.total, 100.0 * (double)d10.big / (double)d10.total);
        }
    }

    /* color space coverage (only used by CompLumaFirst) */
    printf("-- precision: Y2R color space coverage (typical params, CompLumaFirst) --\n");
    for (int s = 0; s < N_CS; s++) {
        const yuv_params_t *p = &k_cs_scen[s];
        const int32_t gc = q11(p->gain_c), db = q11(p->delta_b), ds = q11(p->delta_s), ang = q14_deg(p->angle_deg);
        const float gcf = q11_f(p->gain_c), dbf = q11_f(p->delta_b), dsf = q11_f(p->delta_s),
                    angf = q14_deg_f(p->angle_deg);
        run_fix_u8(in8, n, gc, db, ds, ang, ADJ_YUV_GAMUT_COMP_LUMA_FIRST, k_cs_code[s], fix8);
        run_flt_u8(in8, n, gcf, dbf, dsf, angf, ADJ_YUV_GAMUT_COMP_LUMA_FIRST, k_cs_code[s], flt8);
        dstats_t d8 = dstats16(fix8, flt8, n);
        run_fix_u10(in10, n, gc, db, ds, ang, ADJ_YUV_GAMUT_COMP_LUMA_FIRST, k_cs_code[s], fix10);
        run_flt_u10(in10, n, gcf, dbf, dsf, angf, ADJ_YUV_GAMUT_COMP_LUMA_FIRST, k_cs_code[s], flt10);
        dstats_t d10 = dstats16(fix10, flt10, n);
        printf("  %s  u8 max=%d mean=%.4f | u10 max=%d mean=%.4f\n", p->name, d8.max_d, d8.mean_d, d10.max_d,
            d10.mean_d);
    }

    /* identity: neutral parameters must reproduce the input exactly（HardClip 分支）
       注：CompLumaFirst 分支对“输入本就超出 RGB 色域”的像素会主动调 Y/缩色度
       （与 Python 一致），故恒等仅对 HardClip 成立。 */
    {
        int ok8 = 1, ok10 = 1;
        run_fix_u8(in8, n, q11(1.0f), q11(0.0f), q11(1.0f), q14_deg(0.0f), ADJ_YUV_GAMUT_HARDCLIP, ADJ_YUV_CS_BT709,
            fix8);
        run_fix_u10(in10, n, q11(1.0f), q11(0.0f), q11(1.0f), q14_deg(0.0f), ADJ_YUV_GAMUT_HARDCLIP,
            ADJ_YUV_CS_BT709, fix10);
        for (int i = 0; i < n; i++) {
            if (fix8[3 * i] != (int16_t)in8[3 * i] ||
                fix8[3 * i + 1] != (int16_t)((int32_t)in8[3 * i + 1] - UV_CENTER8) ||
                fix8[3 * i + 2] != (int16_t)((int32_t)in8[3 * i + 2] - UV_CENTER8))
                ok8 = 0;
            if (fix10[3 * i] != (int16_t)in10[3 * i] ||
                fix10[3 * i + 1] != (int16_t)((int32_t)in10[3 * i + 1] - UV_CENTER10) ||
                fix10[3 * i + 2] != (int16_t)((int32_t)in10[3 * i + 2] - UV_CENTER10))
                ok10 = 0;
        }
        printf("-- identity check (neutral params, HardClip, fix) --\n");
        printf("  u8 : %s | u10: %s\n", ok8 ? "OK (exact)" : "FAIL", ok10 ? "OK (exact)" : "FAIL");
    }

    /* CompLumaFirst 不变量：保极角补偿后 RGB 应回到 [0,1] 内（HardClip 则不保证） */
    {
        const yuv_params_t *p = &k_scen[11]; /* extreme：色度大幅越界 */
        const int32_t gc = q11(p->gain_c), db = q11(p->delta_b), ds = q11(p->delta_s), ang = q14_deg(p->angle_deg);
        printf("-- gamut invariant: max RGB excursion beyond [0,1] (extreme params, fix u8) --\n");
        for (int g = 0; g < 2; g++) {
            run_fix_u8(in8, n, gc, db, ds, ang, g, ADJ_YUV_CS_BT709, fix8);
            float mx = 0.0f;
            for (int i = 0; i < n; i++) {
                const float e = rgb_excursion(fix8[3 * i] / 255.0f, fix8[3 * i + 1] / 255.0f,
                    fix8[3 * i + 2] / 255.0f);
                if (e > mx)
                    mx = e;
            }
            printf("  %-14s max excursion = %.5f (%.2f LSB u8)\n", gamut_name[g], mx, mx * 255.0f);
        }
    }
    printf("\n");

    /* ---------------- performance ---------------- */
    static const int perf_idx[] = {0, 7, 8, 10, 11}; /* identity / S2.5 / H45 / typical / extreme */
    const int nperf = (int)(sizeof(perf_idx) / sizeof(perf_idx[0]));
    const double total = (double)n * iters;

    printf("-- performance (per pixel, n=%d, iters=%d) --\n", n, iters);
    printf("  %-28s %10s %10s %10s %10s\n", "scenario", "fix ns/px", "flt ns/px", "fix MP/s", "flt MP/s");
    for (int k = 0; k < nperf; k++) {
        const yuv_params_t *p = &k_scen[perf_idx[k]];
        const int32_t gc = q11(p->gain_c), db = q11(p->delta_b), ds = q11(p->delta_s), ang = q14_deg(p->angle_deg);
        const float gcf = q11_f(p->gain_c), dbf = q11_f(p->delta_b), dsf = q11_f(p->delta_s),
                    angf = q14_deg_f(p->angle_deg);
        uint64_t h = 0;
        double t0, t1;
        run_fix_u8(in8, n, gc, db, ds, ang, ADJ_YUV_GAMUT_COMP_LUMA_FIRST, ADJ_YUV_CS_BT709, fix8); /* warmup */
        t0 = now_sec();
        for (int it = 0; it < iters; it++)
            run_fix_u8(in8, n, gc, db, ds, ang, ADJ_YUV_GAMUT_COMP_LUMA_FIRST, ADJ_YUV_CS_BT709, fix8);
        t1 = now_sec();
        h ^= cs16in(fix8, n);
        double tf = t1 - t0;
        run_flt_u8(in8, n, gcf, dbf, dsf, angf, ADJ_YUV_GAMUT_COMP_LUMA_FIRST, ADJ_YUV_CS_BT709, flt8); /* warmup */
        t0 = now_sec();
        for (int it = 0; it < iters; it++)
            run_flt_u8(in8, n, gcf, dbf, dsf, angf, ADJ_YUV_GAMUT_COMP_LUMA_FIRST, ADJ_YUV_CS_BT709, flt8);
        t1 = now_sec();
        h ^= cs16in(flt8, n);
        double tg = t1 - t0;
        printf("  %-28s %10.2f %10.2f %10.2f %10.2f\n", p->name, tf / total * 1e9, tg / total * 1e9,
            (double)n * iters / tf / 1e6, (double)n * iters / tg / 1e6);
        printf("  (checksum 0x%016llx)\n", (unsigned long long)h);
    }

    free(in8);
    free(in10);
    free(fix8);
    free(flt8);
    free(fix10);
    free(flt10);
    return 0;
}
