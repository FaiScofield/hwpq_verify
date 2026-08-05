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
    float H, S, V;
} hsv_f; /* H∈[0,360), S,V∈[0,1] */

/* RGB(0..1) -> HSV */
static inline hsv_f rgb2hsv_float(float r, float g, float b)
{
    float M = MAX3(r, g, b);
    float m = MIN3(r, g, b);
    float C = M - m;

    hsv_f o;
    o.V = M;
    o.S = (M > 0.0f) ? C / M : 0.0f;

    o.H = 0.0f;
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
        o.H = 60.0f * hp;
    }
    return o;
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
