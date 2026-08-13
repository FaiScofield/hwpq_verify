/**
 * hsv_adjust_bench.c — Performance comparison:
 *   direct RGB-domain HSV adjustment (adjust_hsv_on_rgb_*) vs
 *   HSV roundtrip (adjust_hsv_on_hsv_*: rgb2hsv_fix -> adjust -> hsv2rgb_fix)
 *
 * Paths (all header-only static inline, fully inlined into the timing loop —
 * fair best-case comparison), over both 8bit and 10bit pixels:
 *   u8 :
 *     A   adjust_hsv_on_rgb_u8    one-pass RGB-domain adjustment
 *     B   adjust_hsv_on_hsv_u8    rgb2hsv_fix_u8 -> HSV adjust -> hsv2rgb_fix_u8
 *     C   rgb2hsv_float -> HSV adjust -> hsv2rgb_float   (float reference)
 *   u10:
 *     A10 adjust_hsv_on_rgb_u10   one-pass RGB-domain adjustment
 *     B10 adjust_hsv_on_hsv_u10   rgb2hsv_fix_u10 -> HSV adjust -> hsv2rgb_fix_u10
 *
 * Also validates output equivalence (max per-channel |diff| in LSB) of all
 * paths. They keep the same semantics: gray (S=0) pixels only get V adjusted
 * and stay gray; H uses the original hue.
 *
 * Usage:
 *   hsv_adjust_bench [n_pixels] [iters]
 *   (default: n_pixels = 1920*1080, iters = 30)
 *
 * Build with optimization for meaningful numbers (-O2/-O3, i.e. Release build).
 */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <math.h>
#include "hsv_adjust.h"
#include "hsv_float.h"

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

/* ---------------- Path C: float roundtrip (reference, u8) ---------------- */
static void adjust_hsv_via_float(const uint8_t *rgb, int n, int16_t dv, int16_t ds8, int16_t dh, uint8_t *out)
{
    const float inv = 1.0f / 255.0f;
    const float dvn = dv / 1023.0f;            /* dv Q10: 1023 = ΔV full scale (u8: 1023=255 gray, ÷4 same as A/B) */
    const float ds = ds8 / 1023.0f;            /* ds Q10: 1023 = ΔS 1.0 */
    const float dhv = dh * (360.0f / 1023.0f); /* dh Q10: 1023 = 360° */
    for (int i = 0; i < n; i++) {
        hsv_f h = rgb2hsv_float(rgb[3 * i] * inv, rgb[3 * i + 1] * inv, rgb[3 * i + 2] * inv);

        float vn = h.V + dvn;
        if (vn < 0.0f)
            vn = 0.0f;
        else if (vn > 1.0f)
            vn = 1.0f;
        float sn = (h.S > 0.0f) ? h.S + ds : 0.0f;
        if (sn < 0.0f)
            sn = 0.0f;
        else if (sn > 1.0f)
            sn = 1.0f;
        float hn = h.H + dhv;
        hn = fmodf(hn, 360.0f);
        if (hn < 0.0f)
            hn += 360.0f;

        float R, G, B;
        hsv2rgb_float(hn, sn, vn, &R, &G, &B);
        out[3 * i] = (uint8_t)lrintf(R * 255.0f);
        out[3 * i + 1] = (uint8_t)lrintf(G * 255.0f);
        out[3 * i + 2] = (uint8_t)lrintf(B * 255.0f);
    }
}

/* ---------------- helpers ---------------- */
/* deterministic LCG, so runs are reproducible */
static uint32_t lcg_state = 0x12345678u;
static uint32_t lcg_next(void)
{
    lcg_state = lcg_state * 1664525u + 1013904223u;
    return lcg_state;
}

/* max per-channel |diff| between two buffers (3*n samples) */
static int buf_max_diff(const uint8_t *a, const uint8_t *b, int n)
{
    int md = 0;
    for (int i = 0; i < 3 * n; i++) {
        int d = (int)a[i] - (int)b[i];
        if (d < 0)
            d = -d;
        if (d > md)
            md = d;
    }
    return md;
}

static int buf_max_diff16(const uint16_t *a, const uint16_t *b, int n)
{
    int md = 0;
    for (int i = 0; i < 3 * n; i++) {
        int d = (int)a[i] - (int)b[i];
        if (d < 0)
            d = -d;
        if (d > md)
            md = d;
    }
    return md;
}

/* FNV-1a checksum over the output, so the timing loops cannot be elided */
static uint64_t buf_checksum(const uint8_t *p, int n)
{
    uint64_t h = 1469598103934665603ull;
    for (int i = 0; i < 3 * n; i++) {
        h ^= p[i];
        h *= 1099511628211ull;
    }
    return h;
}

static uint64_t buf_checksum16(const uint16_t *p, int n)
{
    uint64_t h = 1469598103934665603ull;
    for (int i = 0; i < 3 * n; i++) {
        h ^= p[i];
        h *= 1099511628211ull;
    }
    return h;
}

/* run `fn` iters times over n pixels with fixed deltas, return elapsed seconds */
static double run_bench8(void (*fn)(const uint8_t *, int, int16_t, int16_t, int16_t, uint8_t *), const uint8_t *in,
    uint8_t *out, int n, int iters, int16_t dv, int16_t ds, int16_t dh)
{
    fn(in, n, dv, ds, dh, out); /* warmup */
    double t0 = now_sec();
    for (int it = 0; it < iters; it++)
        fn(in, n, dv, ds, dh, out);
    return now_sec() - t0;
}

static double run_bench10(void (*fn)(const uint16_t *, int, int16_t, int16_t, int16_t, uint16_t *), const uint16_t *in,
    uint16_t *out, int n, int iters, int16_t dv, int16_t ds, int16_t dh)
{
    fn(in, n, dv, ds, dh, out); /* warmup */
    double t0 = now_sec();
    for (int it = 0; it < iters; it++)
        fn(in, n, dv, ds, dh, out);
    return now_sec() - t0;
}

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

    /* deltas: u8 dv=+64px (≈+0.25 of 255); u10 dv=+256px (≈+0.25 of 1023);
       S +0.25 (ds8=256: 1023 = ΔS 1.0), H +45° (dh=128: 1023 = 360°) */
    const int16_t dv8 = 64, dv10 = 256, ds8 = 256, dh = 128;

    uint8_t *in = (uint8_t *)malloc(3 * (size_t)n);
    uint8_t *outA = (uint8_t *)malloc(3 * (size_t)n);
    uint8_t *outB = (uint8_t *)malloc(3 * (size_t)n);
    uint8_t *outC = (uint8_t *)malloc(3 * (size_t)n);
    uint16_t *in10 = (uint16_t *)malloc(3 * (size_t)n * sizeof(uint16_t));
    uint16_t *outA10 = (uint16_t *)malloc(3 * (size_t)n * sizeof(uint16_t));
    uint16_t *outB10 = (uint16_t *)malloc(3 * (size_t)n * sizeof(uint16_t));
    if (!in || !outA || !outB || !outC || !in10 || !outA10 || !outB10) {
        printf("malloc failed\n");
        return 1;
    }
    for (int i = 0; i < 3 * n; i++) {
        in[i] = (uint8_t)(lcg_next() >> 24);
        in10[i] = (uint16_t)(lcg_next() >> 22); /* 10bit: [0, 1023] */
    }

    printf("== HSV adjust: direct RGB-domain vs rgb2hsv + adjust + hsv2rgb ==\n");
    printf("n_pixels = %d (%.1f MP), iters = %d, dv8=%d dv10=%d ds8=%d dh=%d\n\n", n, n / 1e6, iters, (int)dv8,
        (int)dv10, (int)ds8, (int)dh);

    /* ---- correctness: output equivalence across all paths (full deltas) ---- */
    adjust_hsv_on_rgb_u8(in, n, dv8, ds8, dh, outA);
    adjust_hsv_on_hsv_u8(in, n, dv8, ds8, dh, outB);
    adjust_hsv_via_float(in, n, dv8, ds8, dh, outC);
    adjust_hsv_on_rgb_u10(in10, n, dv10, ds8, dh, outA10);
    adjust_hsv_on_hsv_u10(in10, n, dv10, ds8, dh, outB10);

    printf("-- output equivalence with full deltas (max per-channel |diff|, LSB) --\n");
    printf("  u8  A(rgb direct) vs B(hsv roundtrip): %d\n", buf_max_diff(outA, outB, n));
    printf("  u8  A(rgb direct) vs C(float):          %d\n", buf_max_diff(outA, outC, n));
    printf("  u8  B(hsv roundtrip) vs C(float):       %d\n", buf_max_diff(outB, outC, n));
    printf("  u10 A(rgb direct) vs B(hsv roundtrip):  %d\n", buf_max_diff16(outA10, outB10, n));
    /* identity: zero deltas must reproduce the input exactly */
    adjust_hsv_on_rgb_u8(in, n, 0, 0, 0, outA);
    adjust_hsv_on_rgb_u10(in10, n, 0, 0, 0, outA10);
    printf("  identity (zero deltas): u8=%s u10=%s\n", buf_max_diff(in, outA, n) == 0 ? "OK (exact)" : "FAIL",
        buf_max_diff16(in10, outA10, n) == 0 ? "OK (exact)" : "FAIL");
    printf("\n");

    /* ---- performance: per adjustment scenario ---- */
    static const struct {
        const char *name;
        int16_t dv8, dv10, ds8, dh;
    } scen[] = {
        {"V only            (dv=+64px/+256px)", 64, 256, 0,   0  },
        {"S only            (ds=+0.25)",        0,  0,   256, 0  },
        {"H only            (dh=+45deg = 128)", 0,  0,   0,   128},
        {"V+S               (dv=+64 ds=+0.25)", 64, 256, 256, 0  },
        {"V+S+H             (all)",             64, 256, 256, 128},
    };
    const int nscen = (int)(sizeof(scen) / sizeof(scen[0]));
    const double total = (double)n * iters;

    printf("-- performance (per pixel, n=%d, iters=%d) --\n", n, iters);
    for (int s = 0; s < nscen; s++) {
        double tA = run_bench8(adjust_hsv_on_rgb_u8, in, outA, n, iters, scen[s].dv8, scen[s].ds8, scen[s].dh);
        double tB = run_bench8(adjust_hsv_on_hsv_u8, in, outB, n, iters, scen[s].dv8, scen[s].ds8, scen[s].dh);
        double tC = run_bench8(adjust_hsv_via_float, in, outC, n, iters, scen[s].dv8, scen[s].ds8, scen[s].dh);
        double tA10 = run_bench10(adjust_hsv_on_rgb_u10, in10, outA10, n, iters, scen[s].dv10, scen[s].ds8, scen[s].dh);
        double tB10 = run_bench10(adjust_hsv_on_hsv_u10, in10, outB10, n, iters, scen[s].dv10, scen[s].ds8, scen[s].dh);
        printf("[%-38s]\n", scen[s].name);
        printf("  u8  A rgb direct    %7.2f ns/px   %7.2f MP/s\n", tA / total * 1e9, total / tA / 1e6);
        printf("  u8  B hsv roundtrip %7.2f ns/px   %7.2f MP/s   (B/A = %.2fx)\n", tB / total * 1e9, total / tB / 1e6, tB / tA);
        printf("  u8  C float ref     %7.2f ns/px   %7.2f MP/s\n", tC / total * 1e9, total / tC / 1e6);
        printf("  u10 A rgb direct    %7.2f ns/px   %7.2f MP/s\n", tA10 / total * 1e9, total / tA10 / 1e6);
        printf("  u10 B hsv roundtrip %7.2f ns/px   %7.2f MP/s   (B/A = %.2fx)\n", tB10 / total * 1e9,
            total / tB10 / 1e6, tB10 / tA10);
        printf("\n");
    }

    /* final full-delta runs so the buffers are used and nothing is elided */
    adjust_hsv_on_rgb_u8(in, n, dv8, ds8, dh, outA);
    adjust_hsv_on_hsv_u8(in, n, dv8, ds8, dh, outB);
    adjust_hsv_via_float(in, n, dv8, ds8, dh, outC);
    adjust_hsv_on_rgb_u10(in10, n, dv10, ds8, dh, outA10);
    adjust_hsv_on_hsv_u10(in10, n, dv10, ds8, dh, outB10);
    printf("  checksum: u8 A=%016llx B=%016llx C=%016llx | u10 A=%016llx B=%016llx\n",
        (unsigned long long)buf_checksum(outA, n), (unsigned long long)buf_checksum(outB, n),
        (unsigned long long)buf_checksum(outC, n), (unsigned long long)buf_checksum16(outA10, n),
        (unsigned long long)buf_checksum16(outB10, n));

    free(in);
    free(outA);
    free(outB);
    free(outC);
    free(in10);
    free(outA10);
    free(outB10);
    return 0;
}
