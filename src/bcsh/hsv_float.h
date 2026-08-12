/**
 * hsv_float.h — RGB <-> HSV 浮点参考实现（六边形模型标准公式）
 * 无定点、无优化，作为精度对照基准。
 *
 * 约定：R,G,B ∈ [0,1]；H∈[0,360), S∈[0,1], V∈[0,1]
 */
#ifndef HSV_FLOAT_H
#define HSV_FLOAT_H

#include "verify_com.h"
#include <math.h>

typedef struct {
    float H; // [0.0, 360.0)
    float S; // [0.0, 1.0]
    float V; // [0.0, 1.0]
} hsv_f;

/* RGB(0..1) -> HSV */
static inline hsv_f rgb2hsv_float(float r, float g, float b)
{
    float M = MAX3(r, g, b);
    float m = MIN3(r, g, b);
    float C = M - m;

    hsv_f hsv;
    hsv.V = M;
    hsv.S = (M > 0.0f) ? C / M : 0.0f;

    hsv.H = 0.0f;
    if (C > 0.0f) {
        float hp;
        if (M == r)
            hp = fmodf((g - b) / C, 6.0f);
        else if (M == g)
            hp = (b - r) / C + 2.0f;
        else
            hp = (r - g) / C + 4.0f;
        if (hp < 0.0f)
            hp += 6.0f;
        hsv.H = 60.0f * hp;
    }
    return hsv;
}

/* RGB(0..1) -> HSV（圆柱/极坐标色相版：atan2 直接求 H）
   色度平面坐标 α=(2R-G-B)/2、β=(G-B)√3/2，H=atan2(β,α)，0°=红（与六边形模型一致）；
   与六边形分段线性 H 的差异：R/G/B 三顶点处相同，中间色相略有偏差（圆柱 vs 六边形模型固有差）。 */
static inline hsv_f rgb2h2sv_float(float r, float g, float b)
{
    float M = MAX3(r, g, b);
    float m = MIN3(r, g, b);
    float C = M - m;

    float alpha = (2.f * r - g - b) * 0.5f;
    float beta  = (g - b) * sqrtf(3.0f) * 0.5f;

    hsv_f hsv;
    hsv.V = M;
    hsv.S = (M > 0.0f) ? C / M : 0.0f;
    hsv.H = atan2f(beta, alpha) * (180.0f / M_PI);
    if (hsv.H < 0.0f)
        hsv.H += 360.0f; /* atan2 ∈ [-180,180]，负值 +360 归一到 [0,360)，0°=红 */
    return hsv;
}

/* HSV(圆柱/极坐标色相版) -> RGB(0..1)：rgb2h2sv_float 的精确逆变换
   给定 H,S,V：C=V*S、m=V-C（min 通道），按 60° 扇区解中间通道 X 的线性方程
   （由 α=(2R-G-B)/2、β=(G-B)√3/2、H=atan2(β,α) 逐扇区推导，与正向严格互逆） */
static inline void h2sv2rgb_float(float H, float S, float V, float *R, float *G, float *B)
{
    if (S <= 0.0f) { *R = *G = *B = V; return; }
    float Hn = fmodf(H, 360.0f);
    if (Hn < 0.0f)
        Hn += 360.0f;
    const float C = V * S;
    const float m = V - C;
    const float s3 = sqrtf(3.0f);
    const float t = tanf(Hn * (M_PI / 180.0f)); /* 各扇区内 tan 有限或 1/t→0，无除零 */
    int seg = (int)(Hn / 60.0f) % 6;
    float X, r, g, b;
    switch (seg) {
    case 0: /* R=max, B=min, G=X */ X = (t * (2.0f * V - m) + s3 * m) / (s3 + t);  r = V; g = X; b = m; break;
    case 1: /* G=max, B=min, R=X */ X = (s3 * (V - m) / t + V + m) * 0.5f;         r = X; g = V; b = m; break;
    case 2: /* G=max, R=min, B=X */ X = (V * (s3 + t) - 2.0f * m * t) / (s3 - t);  r = m; g = V; b = X; break;
    case 3: /* B=max, R=min, G=X */ X = (s3 * V + t * (2.0f * m - V)) / (s3 + t);  r = m; g = X; b = V; break;
    case 4: /* B=max, G=min, R=X */ X = (s3 * (m - V) / t + m + V) * 0.5f;         r = X; g = m; b = V; break;
    default: /* R=max, G=min, B=X */ X = (m * (s3 + t) - 2.0f * V * t) / (s3 - t); r = V; g = m; b = X; break;
    }
    *R = CLIP(r, 0.0f, 1.0f);
    *G = CLIP(g, 0.0f, 1.0f);
    *B = CLIP(b, 0.0f, 1.0f);
}


/* HSV -> RGB(0..1) */
static inline void hsv2rgb_float(float H, float S, float V, float *R, float *G, float *B)
{
    float C = V * S;
    float hp = H * (1.0f / 60.0f);
    float X = C * (1.0f - fabsf(fmodf(hp, 2.0f) - 1.0f));
    float m = V - C;

    float r1, g1, b1;
    switch ((int)hp % 6) { /* H=360° 时 (int)6%6=0，等价 0° */
    case 0:
        r1 = C;
        g1 = X;
        b1 = 0.0f;
        break;
    case 1:
        r1 = X;
        g1 = C;
        b1 = 0.0f;
        break;
    case 2:
        r1 = 0.0f;
        g1 = C;
        b1 = X;
        break;
    case 3:
        r1 = 0.0f;
        g1 = X;
        b1 = C;
        break;
    case 4:
        r1 = X;
        g1 = 0.0f;
        b1 = C;
        break;
    default:
        r1 = C;
        g1 = 0.0f;
        b1 = X;
        break;
    }
    *R = r1 + m;
    *G = g1 + m;
    *B = b1 + m;
}

#endif /* HSV_FLOAT_H */