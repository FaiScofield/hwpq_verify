/**
 * hsv_float_test.c — RGB<->HSV 浮点参考实现 + 往返精度损失评估
 *
 * 目标：
 *   1) 提供浮点参考实现 rgb2hsv_float / hsv2rgb_float（六边形模型标准公式）
 *      + rgb2h2sv_float（圆柱/极坐标 atan2 色相版）及两者输出对比
 *   2) 评估 rgb -> hsv -> rgb 往返精度损失（浮点六边形 / 浮点圆柱 / 定点 三路对照）
 *   3) 输入精度遍历 u8(0..255) 全遍历 + u10(0..1023) 抽样/全遍历
 *
 * 误差单位 = 输入 LSB：输出先四舍五入回整数，再与输入逐通道求差。
 * 运行：
 *   hsv_float_test           u8 全遍历 + u10 抽样（步长=3）
 *   hsv_float_test 1         u10 全遍历 1024^3（较慢，数秒~十几秒）
 *   hsv_float_test 7         u10 抽样步长 7
 */
#include <math.h>
#include <stdio.h>
#include <stdint.h>
#include <time.h>
#include "hsv_fixed.h" /* 定点版，用于对照 */
#include "hsv_float.h" /* 浮点参考实现 */

/* ============ 2) 精度损失评估 ============ */
typedef struct {
    const char *name;
    uint64_t n;                          /* 样本总数 */
    uint64_t n_err;                      /* 有偏差样本数 */
    int max_abs;                         /* 最大单通道 |Δ|（LSB） */
    double sum_abs;                      /* 累计 |Δ|（用于均值） */
    double sum_sq;                       /* 累计 Δ²（用于 RMS） */
    int w_r, w_g, w_b, w_dr, w_dg, w_db; /* 最坏样本 */
} stats_t;

static void stats_init(stats_t *s, const char *name)
{
    s->name = name;
    s->n = s->n_err = 0;
    s->max_abs = 0;
    s->sum_abs = s->sum_sq = 0.0;
    s->w_r = s->w_g = s->w_b = s->w_dr = s->w_dg = s->w_db = 0;
}

static void stats_add(stats_t *s, int r, int g, int b, int dr, int dg, int db)
{
    int ar = dr < 0 ? -dr : dr;
    int ag = dg < 0 ? -dg : dg;
    int ab = db < 0 ? -db : db;
    int mx = ar > ag ? ar : ag;
    if (ab > mx)
        mx = ab;

    s->n++;
    if (mx) {
        s->n_err++;
        s->sum_abs += (double)(ar + ag + ab);
        s->sum_sq += (double)dr * dr + (double)dg * dg + (double)db * db;
        if (mx > s->max_abs) {
            s->max_abs = mx;
            s->w_r = r;
            s->w_g = g;
            s->w_b = b;
            s->w_dr = dr;
            s->w_dg = dg;
            s->w_db = db;
        }
    }
}

static void stats_report(const stats_t *s, int bits, double sec)
{
    double mean = s->n ? s->sum_abs / (3.0 * (double)s->n) : 0.0;
    double rms = s->n ? sqrt(s->sum_sq / (3.0 * (double)s->n)) : 0.0;
    printf("%-7s u%-2d  n=%9llu  有偏差=%9llu (%.5f%%)  max|Δ|=%d LSB"
           "  mean|Δ|=%.4f  RMS=%.4f  耗时 %.2fs\n",
        s->name, bits, (unsigned long long)s->n, (unsigned long long)s->n_err, 100.0 * s->n_err / (double)s->n,
        s->max_abs, mean, rms, sec);
    if (s->max_abs)
        printf("         最坏样本 RGB(%d,%d,%d) -> (%+d,%+d,%+d)\n", s->w_r, s->w_g, s->w_b, s->w_dr, s->w_dg, s->w_db);
}

/* 浮点版往返评估：遍历 bits 位输入（等间隔 stride），误差按输入 LSB 计 */
static void eval_float_roundtrip(const char *name, int bits, int stride)
{
    int maxv = (1 << bits) - 1;
    static float nrm[1024];
    for (int i = 0; i <= maxv; i++)
        nrm[i] = (float)i / (float)maxv;

    stats_t st;
    stats_init(&st, name);
    double t0 = (double)clock() / CLOCKS_PER_SEC;

    for (int r = 0; r <= maxv; r += stride)
        for (int g = 0; g <= maxv; g += stride)
            for (int b = 0; b <= maxv; b += stride) {
                hsv_f h = rgb2hsv_float(nrm[r], nrm[g], nrm[b]);
                float R, G, B;
                hsv2rgb_float(h.H, h.S, h.V, &R, &G, &B);
                stats_add(&st, r, g, b, (int)lrintf(R * (float)maxv) - r, (int)lrintf(G * (float)maxv) - g,
                    (int)lrintf(B * (float)maxv) - b);
            }
    double dt = (double)clock() / CLOCKS_PER_SEC - t0;
    stats_report(&st, bits, dt);
}

/* 圆柱色相版往返评估：rgb2h2sv_float -> hsv2rgb_float（u8/u10，stride=1 全遍历） */
static void eval_h2_roundtrip(const char *name, int bits, int stride)
{
    const int maxv = (1 << bits) - 1;
    static float nrm[1024];
    for (int i = 0; i <= maxv; i++)
        nrm[i] = (float)i / (float)maxv;

    stats_t st;
    stats_init(&st, name);
    double t0 = (double)clock() / CLOCKS_PER_SEC;
    for (int r = 0; r <= maxv; r += stride)
        for (int g = 0; g <= maxv; g += stride)
            for (int b = 0; b <= maxv; b += stride) {
                hsv_f h = rgb2h2sv_float(nrm[r], nrm[g], nrm[b]);
                float R, G, B;
                hsv2rgb_float(h.H, h.S, h.V, &R, &G, &B);
                stats_add(&st, r, g, b, (int)lrintf(R * (float)maxv) - r, (int)lrintf(G * (float)maxv) - g,
                    (int)lrintf(B * (float)maxv) - b);
            }
    double dt = (double)clock() / CLOCKS_PER_SEC - t0;
    stats_report(&st, bits, dt);
}

/* 圆柱自洽往返：rgb2h2sv_float -> h2sv2rgb_float（u8/u10，stride=1 全遍历） */
static void eval_h2r_roundtrip(const char *name, int bits, int stride)
{
    const int maxv = (1 << bits) - 1;
    static float nrm[1024];
    for (int i = 0; i <= maxv; i++)
        nrm[i] = (float)i / (float)maxv;

    stats_t st;
    stats_init(&st, name);
    double t0 = (double)clock() / CLOCKS_PER_SEC;
    for (int r = 0; r <= maxv; r += stride)
        for (int g = 0; g <= maxv; g += stride)
            for (int b = 0; b <= maxv; b += stride) {
                hsv_f h = rgb2h2sv_float(nrm[r], nrm[g], nrm[b]);
                float R, G, B;
                h2sv2rgb_float(h.H, h.S, h.V, &R, &G, &B);
                stats_add(&st, r, g, b, (int)lrintf(R * (float)maxv) - r, (int)lrintf(G * (float)maxv) - g,
                    (int)lrintf(B * (float)maxv) - b);
            }
    double dt = (double)clock() / CLOCKS_PER_SEC - t0;
    stats_report(&st, bits, dt);
}

/* rgb2h2sv_float vs rgb2hsv_float 输出对比（H 圆环角度差 / ΔS / ΔV） */
static void compare_hsv_models(int bits, int stride)
{
    const int maxv = (1 << bits) - 1;
    static float nrm[1024];
    for (int i = 0; i <= maxv; i++)
        nrm[i] = (float)i / (float)maxv;
    uint64_t n = 0;
    double max_dH = 0.0, sum_dH = 0.0, max_dS = 0.0, max_dV = 0.0;
    for (int r = 0; r <= maxv; r += stride)
        for (int g = 0; g <= maxv; g += stride)
            for (int b = 0; b <= maxv; b += stride) {
                hsv_f a = rgb2hsv_float(nrm[r], nrm[g], nrm[b]);
                hsv_f b2 = rgb2h2sv_float(nrm[r], nrm[g], nrm[b]);
                double dH = fabs((double)a.H - b2.H);
                if (dH > 180.0)
                    dH = 360.0 - dH; /* 圆环距离 */
                double dS = fabs((double)a.S - b2.S);
                double dV = fabs((double)a.V - b2.V);
                if (dH > max_dH)
                    max_dH = dH;
                if (dS > max_dS)
                    max_dS = dS;
                if (dV > max_dV)
                    max_dV = dV;
                sum_dH += dH;
                n++;
            }
    printf("  u%-2d n=%9llu  H: max|Δ|=%.3f° mean=%.4f°  |  S: max|Δ|=%.6f  |  V: max|Δ|=%.6f\n", bits,
        (unsigned long long)n, max_dH, sum_dH / (double)n, max_dS, max_dV);
}

/* 定点版往返评估（u8/u10，stride=1 时全遍历） */
static void eval_fixed_roundtrip(const char *name, int bits, int stride)
{
    const int maxv = (1 << bits) - 1;
    stats_t st;
    stats_init(&st, name);
    double t0 = (double)clock() / CLOCKS_PER_SEC;

    for (int r = 0; r <= maxv; r += stride)
        for (int g = 0; g <= maxv; g += stride)
            for (int b = 0; b <= maxv; b += stride) {
                uint16_t H, S, V;
                if (bits == 8) {
                    uint8_t R, G, B;
                    rgb2hsv_fix_u8((uint8_t)r, (uint8_t)g, (uint8_t)b, &H, &S, &V);
                    hsv2rgb_fix_u8(H, S, V, &R, &G, &B);
                    stats_add(&st, r, g, b, (int)R - r, (int)G - g, (int)B - b);
                }
                else {
                    uint16_t R, G, B;
                    rgb2hsv_fix_u10((uint16_t)r, (uint16_t)g, (uint16_t)b, &H, &S, &V);
                    hsv2rgb_fix_u10(H, S, V, &R, &G, &B);
                    stats_add(&st, r, g, b, (int)R - r, (int)G - g, (int)B - b);
                }
            }
    double dt = (double)clock() / CLOCKS_PER_SEC - t0;
    stats_report(&st, bits, dt);
}

/* 浮点实现本身的正确性抽查（对照文章示例表） */
static void spot_check(void)
{
    static const struct {
        float r, g, b;
    } tab[] = {
        {1.0f,   0.0f,   0.0f  }, /* 红   H=0    S=1.000 V=1.000 */
        {0.75f,  0.75f,  0.0f  }, /* 黄   H=60   S=1.000 V=0.750 */
        {0.0f,   0.5f,   0.0f  }, /* 绿   H=120  S=1.000 V=0.500 */
        {0.5f,   1.0f,   1.0f  }, /* 青   H=180  S=0.500 V=1.000 */
        {0.5f,   0.5f,   1.0f  }, /* 蓝   H=240  S=0.500 V=1.000 */
        {0.75f,  0.25f,  0.75f }, /* 品红 H=300  S=0.667 V=0.750 */
        {0.628f, 0.643f, 0.142f}, /*      H=61.8 S=0.779 V=0.643 */
        {0.255f, 0.104f, 0.918f}, /*      H=251.1 S=0.887 V=0.918 */
    };
    printf("-- 浮点版 spot check（对照文章示例表）--\n");
    for (int i = 0; i < (int)(sizeof(tab) / sizeof(tab[0])); i++) {
        hsv_f h = rgb2hsv_float(tab[i].r, tab[i].g, tab[i].b);
        float R, G, B;
        hsv2rgb_float(h.H, h.S, h.V, &R, &G, &B);
        printf("RGB(%.3f,%.3f,%.3f) -> H=%7.2f° S=%6.3f V=%6.3f"
               " -> RGB(%.4f,%.4f,%.4f)\n",
            tab[i].r, tab[i].g, tab[i].b, h.H, h.S, h.V, R, G, B);
    }
    printf("\n");
}

int main(int argc, char **argv)
{
    int step_u10 = (argc > 1) ? atoi(argv[1]) : 3; /* u10 抽样步长，=1 全遍历 */
    if (step_u10 < 1)
        step_u10 = 3;
    const char *lab10 = (step_u10 == 1) ? "全遍历" : "抽样";

    printf("== rgb -> hsv -> rgb 往返偏差（误差单位 = 输入 LSB，输出四舍五入回整数）==\n");
    printf("（u8 恒全遍历；u10 步长=%d -> %s）\n\n", step_u10, lab10);
    spot_check();

    printf("-- 浮点六边形版（rgb2hsv_float）--\n");
    eval_float_roundtrip("float", 8, 1);
    eval_float_roundtrip("float", 10, step_u10);

    printf("\n-- 浮点圆柱色相版（rgb2h2sv_float -> hsv2rgb_float，六边形逆，模型不互逆）--\n");
    eval_h2_roundtrip("h2", 8, 1);
    eval_h2_roundtrip("h2", 10, 5);

    printf("\n-- 浮点圆柱自洽（rgb2h2sv_float -> h2sv2rgb_float，圆柱逆）--\n");
    eval_h2r_roundtrip("h2r", 8, 1);
    eval_h2r_roundtrip("h2r", 10, step_u10);

    printf("\n-- 定点版（H=Q14/S=Q11 归一化，对照）--\n");
    eval_fixed_roundtrip("fixed", 8, 1);
    eval_fixed_roundtrip("fixed", 10, step_u10);

    printf("\n-- rgb2h2sv_float vs rgb2hsv_float 输出对比（圆柱 vs 六边形色相）--\n");
    compare_hsv_models(8, 1);
    compare_hsv_models(10, step_u10);

    return 0;
}
