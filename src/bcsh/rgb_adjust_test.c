/**
 * rgb_adjust_test.c — Sonnoc 固定管线（B -> C -> S -> H）精度与性能对比
 *
 * 对比对象：
 *   fix   : adjust_rgb_sonnoc_fix  （Q11 定点，无浮点、无 math 库依赖）
 *   float : adjust_rgb_sonnoc_float（float 参考实现，精度基准）
 *
 * 精度：各调整场景下逐像素对比输出（max/mean |diff| LSB、非零占比），u8 与 u10；
 *       并验证中性参数恒等与 4 种 luma 系数（BT.601/709/2020/P3）。
 *       为只反映管线计算误差，float 侧使用与定点一致的参数（先量化 Q11/Q14 再回读）。
 * 性能：整帧多轮迭代计时（ns/px、MP/s），fix vs float。
 *
 * 用法: rgb_adjust_test [n_pixels] [iters]   （默认 1920*1080, 30）
 * 建议以 Release（-O2/-O3）构建以获得有意义的性能数据。
 */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <math.h>
#include "rgb_adjust.h"

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
    float gain_c;    /* [0,4]，中性 1.0 */
    float delta_b;   /* [-1,1]，中性 0 */
    float delta_s;   /* [0,4]，中性 1.0 */
    float angle_deg; /* [-180,180]，中性 0 */
    int gray_coef;
} sn_params_t;

static const sn_params_t k_scen[] = {
    {"identity    gc=1.0  db=0     ds=1.0  ang=0",      1.00f,  0.00f, 1.00f,   0.0f, ADJ_RGB_GRAY_BT709},
    {"C 0.5       gc=0.5",                              0.50f,  0.00f, 1.00f,   0.0f, ADJ_RGB_GRAY_BT709},
    {"C 1.5       gc=1.5",                              1.50f,  0.00f, 1.00f,   0.0f, ADJ_RGB_GRAY_BT709},
    {"B +0.1      db=+0.1",                             1.00f,  0.10f, 1.00f,   0.0f, ADJ_RGB_GRAY_BT709},
    {"B -0.1      db=-0.1",                             1.00f, -0.10f, 1.00f,   0.0f, ADJ_RGB_GRAY_BT709},
    {"S 0.5       ds=0.5",                              1.00f,  0.00f, 0.50f,   0.0f, ADJ_RGB_GRAY_BT709},
    {"S 1.5       ds=1.5",                              1.00f,  0.00f, 1.50f,   0.0f, ADJ_RGB_GRAY_BT709},
    {"H +45deg    ang=+45",                             1.00f,  0.00f, 1.00f,  45.0f, ADJ_RGB_GRAY_BT709},
    {"H 180deg    ang=180",                             1.00f,  0.00f, 1.00f, 180.0f, ADJ_RGB_GRAY_BT709},
    {"typical     gc=1.2  db=+0.05 ds=1.3  ang=+30",    1.20f,  0.05f, 1.30f,  30.0f, ADJ_RGB_GRAY_BT709},
    {"extreme     gc=2.0  db=+0.5  ds=2.0  ang=180",    2.00f,  0.50f, 2.00f, 180.0f, ADJ_RGB_GRAY_BT709},
};
#define N_SCEN ((int)(sizeof(k_scen) / sizeof(k_scen[0])))

static const sn_params_t k_gray_scen[] = {
    {"gray BT601 ", 1.20f, 0.05f, 1.30f, 30.0f, ADJ_RGB_GRAY_BT601},
    {"gray BT709 ", 1.20f, 0.05f, 1.30f, 30.0f, ADJ_RGB_GRAY_BT709},
    {"gray BT2020", 1.20f, 0.05f, 1.30f, 30.0f, ADJ_RGB_GRAY_BT2020},
    {"gray P3    ", 1.20f, 0.05f, 1.30f, 30.0f, ADJ_RGB_GRAY_P3},
    {"gray P3-T  ", 1.20f, 0.05f, 1.30f, 30.0f, ADJ_RGB_GRAY_THEATER_P3},
};
#define N_GRAY ((int)(sizeof(k_gray_scen) / sizeof(k_gray_scen[0])))

/* ---------------- parameter quantization (u8/u10 share the same Q formats) ---------------- */
static int32_t q11(float v) { return (int32_t)lrintf(v * (float)FIX_S_ONE); }
static int32_t q14_deg(float deg) { return (int32_t)lrintf(deg / 360.0f * (float)FIX_H_ONE); }

/* float 侧使用与定点一致的量化参数（回读），使对比只反映管线计算误差 */
static float q11_f(float v) { return (float)q11(v) / (float)FIX_S_ONE; }
static float q14_deg_f(float deg) { return (float)q14_deg(deg) / (float)FIX_H_ONE * 360.0f; }

/* ---------------- buffered paths ---------------- */
static void sonnoc_fix_u8(const uint8_t *rgb, int n, const sn_params_t *p, uint8_t *out)
{
    const int32_t gc = q11(p->gain_c), db = q11(p->delta_b), ds = q11(p->delta_s), ang = q14_deg(p->angle_deg);
    for (int i = 0; i < n; i++) {
        uint16_t r1, g1, b1;
        adjust_rgb_sonnoc_fix(rgb[3 * i], rgb[3 * i + 1], rgb[3 * i + 2], 255, gc, db, ds, ang, p->gray_coef, &r1, &g1,
            &b1);
        out[3 * i] = (uint8_t)r1;
        out[3 * i + 1] = (uint8_t)g1;
        out[3 * i + 2] = (uint8_t)b1;
    }
}

static void sonnoc_float_u8(const uint8_t *rgb, int n, const sn_params_t *p, uint8_t *out)
{
    const float inv = 1.0f / 255.0f;
    const float gc = q11_f(p->gain_c), db = q11_f(p->delta_b), ds = q11_f(p->delta_s), ang = q14_deg_f(p->angle_deg);
    for (int i = 0; i < n; i++) {
        float r1, g1, b1;
        adjust_rgb_sonnoc_float(rgb[3 * i] * inv, rgb[3 * i + 1] * inv, rgb[3 * i + 2] * inv, gc, db, ds, ang,
            p->gray_coef, &r1, &g1, &b1);
        out[3 * i] = (uint8_t)lrintf(r1 * 255.0f);
        out[3 * i + 1] = (uint8_t)lrintf(g1 * 255.0f);
        out[3 * i + 2] = (uint8_t)lrintf(b1 * 255.0f);
    }
}

static void sonnoc_fix_u10(const uint16_t *rgb, int n, const sn_params_t *p, uint16_t *out)
{
    const int32_t gc = q11(p->gain_c), db = q11(p->delta_b), ds = q11(p->delta_s), ang = q14_deg(p->angle_deg);
    for (int i = 0; i < n; i++) {
        uint16_t r1, g1, b1;
        adjust_rgb_sonnoc_fix(rgb[3 * i], rgb[3 * i + 1], rgb[3 * i + 2], 1023, gc, db, ds, ang, p->gray_coef, &r1,
            &g1, &b1);
        out[3 * i] = r1;
        out[3 * i + 1] = g1;
        out[3 * i + 2] = b1;
    }
}

static void sonnoc_float_u10(const uint16_t *rgb, int n, const sn_params_t *p, uint16_t *out)
{
    const float inv = 1.0f / 1023.0f;
    const float gc = q11_f(p->gain_c), db = q11_f(p->delta_b), ds = q11_f(p->delta_s), ang = q14_deg_f(p->angle_deg);
    for (int i = 0; i < n; i++) {
        float r1, g1, b1;
        adjust_rgb_sonnoc_float(rgb[3 * i] * inv, rgb[3 * i + 1] * inv, rgb[3 * i + 2] * inv, gc, db, ds, ang,
            p->gray_coef, &r1, &g1, &b1);
        out[3 * i] = (uint16_t)lrintf(r1 * 1023.0f);
        out[3 * i + 1] = (uint16_t)lrintf(g1 * 1023.0f);
        out[3 * i + 2] = (uint16_t)lrintf(b1 * 1023.0f);
    }
}

/* ---------------- diff statistics ---------------- */
typedef struct {
    int max_d;          /* max per-channel |diff| (LSB) */
    double mean_d;      /* mean per-channel |diff| */
    long long nz;       /* samples with |diff| > 0 */
    long long big;      /* samples with |diff| > 1 */
    long long total;    /* 3*n samples */
} dstats_t;

static dstats_t dstats8(const uint8_t *a, const uint8_t *b, int n)
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

static dstats_t dstats16(const uint16_t *a, const uint16_t *b, int n)
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
static uint64_t cs8(const uint8_t *p, int n)
{
    uint64_t h = 1469598103934665603ull;
    for (int i = 0; i < 3 * n; i++) {
        h ^= p[i];
        h *= 1099511628211ull;
    }
    return h;
}

static uint64_t cs16(const uint16_t *p, int n)
{
    uint64_t h = 1469598103934665603ull;
    for (int i = 0; i < 3 * n; i++) {
        h ^= (uint64_t)p[i];
        h *= 1099511628211ull;
    }
    return h;
}

/* run fn iters times, return elapsed seconds (with one warmup call) */
typedef void (*path8_fn)(const uint8_t *, int, const sn_params_t *, uint8_t *);
typedef void (*path16_fn)(const uint16_t *, int, const sn_params_t *, uint16_t *);

static double bench8(path8_fn fn, const uint8_t *in, uint8_t *out, int n, int iters, const sn_params_t *p)
{
    fn(in, n, p, out); /* warmup */
    double t0 = now_sec();
    for (int it = 0; it < iters; it++)
        fn(in, n, p, out);
    return now_sec() - t0;
}

static double bench16(path16_fn fn, const uint16_t *in, uint16_t *out, int n, int iters, const sn_params_t *p)
{
    fn(in, n, p, out); /* warmup */
    double t0 = now_sec();
    for (int it = 0; it < iters; it++)
        fn(in, n, p, out);
    return now_sec() - t0;
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
    uint8_t *fix8 = (uint8_t *)malloc(3 * (size_t)n);
    uint8_t *flt8 = (uint8_t *)malloc(3 * (size_t)n);
    uint16_t *in10 = (uint16_t *)malloc(3 * (size_t)n * sizeof(uint16_t));
    uint16_t *fix10 = (uint16_t *)malloc(3 * (size_t)n * sizeof(uint16_t));
    uint16_t *flt10 = (uint16_t *)malloc(3 * (size_t)n * sizeof(uint16_t));
    if (!in8 || !fix8 || !flt8 || !in10 || !fix10 || !flt10) {
        printf("malloc failed\n");
        return 1;
    }
    for (int i = 0; i < 3 * n; i++) {
        in8[i] = (uint8_t)(lcg_next() >> 24);            /* full [0,255] */
        in10[i] = (uint16_t)(lcg_next() >> 22) & 1023u;  /* full [0,1023] */
    }

    printf("== Sonnoc RGB BCSH pipeline: fix (Q11) vs float reference ==\n");
    printf("n_pixels = %d (%.2f MP), iters = %d\n\n", n, (double)n / 1e6, iters);

    /* ---------------- precision ---------------- */
    printf("-- precision: fix vs float (per-channel |diff| in LSB; mean/%% over 3*%d samples) --\n", n);
    for (int s = 0; s < N_SCEN; s++) {
        const sn_params_t *p = &k_scen[s];
        sonnoc_fix_u8(in8, n, p, fix8);
        sonnoc_float_u8(in8, n, p, flt8);
        dstats_t d8 = dstats8(fix8, flt8, n);
        sonnoc_fix_u10(in10, n, p, fix10);
        sonnoc_float_u10(in10, n, p, flt10);
        dstats_t d10 = dstats16(fix10, flt10, n);
        printf("[%s]\n", p->name);
        printf("  u8 : max=%d mean=%.4f nz=%.3f%% gt1=%.4f%%\n", d8.max_d, d8.mean_d, 100.0 * (double)d8.nz / (double)d8.total,
            100.0 * (double)d8.big / (double)d8.total);
        printf("  u10: max=%d mean=%.4f nz=%.3f%% gt1=%.4f%%\n", d10.max_d, d10.mean_d,
            100.0 * (double)d10.nz / (double)d10.total, 100.0 * (double)d10.big / (double)d10.total);
    }

    /* gray coefficient coverage */
    printf("-- precision: luma coefficient coverage (typical params) --\n");
    for (int s = 0; s < N_GRAY; s++) {
        const sn_params_t *p = &k_gray_scen[s];
        sonnoc_fix_u8(in8, n, p, fix8);
        sonnoc_float_u8(in8, n, p, flt8);
        dstats_t d8 = dstats8(fix8, flt8, n);
        sonnoc_fix_u10(in10, n, p, fix10);
        sonnoc_float_u10(in10, n, p, flt10);
        dstats_t d10 = dstats16(fix10, flt10, n);
        printf("  %s  u8 max=%d mean=%.4f | u10 max=%d mean=%.4f\n", p->name, d8.max_d, d8.mean_d, d10.max_d,
            d10.mean_d);
    }

    /* identity: neutral parameters must reproduce the input exactly */
    {
        const sn_params_t neutral = {"neutral", 1.0f, 0.0f, 1.0f, 0.0f, ADJ_RGB_GRAY_BT709};
        sonnoc_fix_u8(in8, n, &neutral, fix8);
        sonnoc_fix_u10(in10, n, &neutral, fix10);
        int id8 = 0, id10 = 0;
        for (int i = 0; i < 3 * n; i++) {
            if (fix8[i] != in8[i])
                id8 = 1;
            if (fix10[i] != in10[i])
                id10 = 1;
        }
        printf("-- identity check (neutral params, fix) --\n");
        printf("  u8 : %s | u10: %s\n", id8 ? "FAIL" : "OK (exact)", id10 ? "FAIL" : "OK (exact)");
    }
    printf("\n");

    /* ---------------- performance ---------------- */
    static const int perf_idx[] = {0, 6, 7, 9, 10}; /* identity / S1.5 / H45 / typical / extreme */
    const int nperf = (int)(sizeof(perf_idx) / sizeof(perf_idx[0]));
    const double total = (double)n * iters;

    printf("-- performance (per pixel, n=%d, iters=%d) --\n", n, iters);
    for (int k = 0; k < nperf; k++) {
        const sn_params_t *p = &k_scen[perf_idx[k]];
        double tf8 = bench8(sonnoc_fix_u8, in8, fix8, n, iters, p);
        double tr8 = bench8(sonnoc_float_u8, in8, flt8, n, iters, p);
        double tf10 = bench16(sonnoc_fix_u10, in10, fix10, n, iters, p);
        double tr10 = bench16(sonnoc_float_u10, in10, flt10, n, iters, p);
        printf("[%s]\n", p->name);
        printf("  u8  fix   %7.2f ns/px   %8.2f MP/s\n", tf8 / total * 1e9, total / tf8 / 1e6);
        printf("  u8  float %7.2f ns/px   %8.2f MP/s   (float/fix = %.2fx)\n", tr8 / total * 1e9,
            total / tr8 / 1e6, tr8 / tf8);
        printf("  u10 fix   %7.2f ns/px   %8.2f MP/s\n", tf10 / total * 1e9, total / tf10 / 1e6);
        printf("  u10 float %7.2f ns/px   %8.2f MP/s   (float/fix = %.2fx)\n", tr10 / total * 1e9,
            total / tr10 / 1e6, tr10 / tf10);
    }

    /* final runs so all buffers are consumed */
    sonnoc_fix_u8(in8, n, &k_scen[10], fix8);
    sonnoc_float_u8(in8, n, &k_scen[10], flt8);
    sonnoc_fix_u10(in10, n, &k_scen[10], fix10);
    sonnoc_float_u10(in10, n, &k_scen[10], flt10);
    printf("\n  checksum: u8 fix=%016llx float=%016llx | u10 fix=%016llx float=%016llx\n",
        (unsigned long long)cs8(fix8, n), (unsigned long long)cs8(flt8, n), (unsigned long long)cs16(fix10, n),
        (unsigned long long)cs16(flt10, n));

    free(in8);
    free(fix8);
    free(flt8);
    free(in10);
    free(fix10);
    free(flt10);
    return 0;
}
