/**
 * hsv_fixed.h — RGB <-> HSV 定点(fixed-point)转换，无浮点、无三角函数
 *
 * 定标约定（H/S 独立位宽归一化定点，见 hsv_precision_test / hsv_h_norm_test）：
 *   FIX_BITS_H = 14 : H 归一化，360° = 2^14 = 16384，有效范围 [0, FIX_H_ONE)
 *   FIX_BITS_S = 11 : S 归一化，1.0 = 2^11 = 2048，有效范围 [0, FIX_S_ONE]
 *   V : 明度，像素域 [0, maxv]        （u8 时 maxv=255，u10 时 maxv=1023，不缩放）
 *   （u10 输入零误差最小组合 (H=14, S=11)，u8 也满足 H+S>=21bit，两者均 0 误差）
 *
 * 特点：
 *   - 无 float/double、无三角函数
 *   - rgb2hsv 用优先级掩码消除 6 路分支；hsv2rgb 用 f(n) 公式消除扇区分支
 *   - 除法全部消除：S=C/V、色相 /C 用倒数表 rcp_tbl；hsv2rgb 扇区定位
 *     h6 = H*6 为纯乘法；rgb2hsv 的 H=(A+base*FIX_H_ONE)/6 中固定除数 6 用常量 RCP6
 *   - hsv2rgb 重建 (V*S*t)>>(FIX_BITS_H+FIX_BITS_S) 用四舍五入 (+2^(bits-1))，
 *     u8/u10 往返 0 误差
 *   - hsv2rgb_v4_hexwalk：六边形走表模型（6 段 TAB + M/m/mid），无分支无除法
 *   - rgb2hsv_fix_u8 / hsv2rgb_fix_u8 为 u8(0..255) 接口；rgb2hsv_fix_u10 / hsv2rgb_fix_u10 为 u10(0..1023)
 */
#ifndef HSV_FIXED_H
#define HSV_FIXED_H

#include "verify_com.h"
#include <stdint.h>

#define FIX_BITS_H 14                         /* H 归一化位宽：360° = 2^14 */
#define FIX_BITS_S 11                         /* S 归一化位宽：1.0 = 2^11 */
#define FIX_H_ONE  ((int32_t)1 << FIX_BITS_H) /* 360°（H 归一化满量程） */
#define FIX_S_ONE  ((int32_t)1 << FIX_BITS_S) /* 1.0 */
#define VS_SHIFT   11 /* 重建第一级 V*S 提前右移位数：目的是降低乘法总位宽，最大允许到11不掉往返精度 */
#define RS_SHIFT   (FIX_BITS_H + FIX_BITS_S - VS_SHIFT) /* 重建第二级右移 */

extern const int32_t g_adj_tan_q11[4097]; /* tan(11bit) */

/* ---------- 定点乘/舍入与 luma 权重（hsv_fixed.c 与 rgb_adjust.h 共用） ---------- */
/* 有符号右移四舍五入（负数向 0 外舍入）：round(p/2^sh) */
static inline int32_t adj_rsh_round(int64_t p, int sh)
{
    p += (1LL << (sh - 1)) + (p >> 63);
    return (int32_t)(p >> sh);
}

/* 有符号定点乘：round(a*b/2^sh)，int64 中间量防溢出 */
static inline int32_t adj_mul_q(int32_t a, int32_t b, int sh) { return adj_rsh_round((int64_t)a * b, sh); }

/* 有符号定点乘（32bit 窄版）：round(a*b/2^sh)，语义与 adj_mul_q 一致（half-away-from-zero）。
   要求 |a·b| ≤ 2^25（int32 内不溢出），省去 64bit 中间量/乘法器，适合硬件。
   典型用法：a、b 分别为 11bit 与 ≤15bit 的有符号量（如 S×gain、angle×progress）。 */
static inline int32_t adj_mul_q32(int32_t a, int32_t b, int sh)
{
    int32_t p = a * b;
    p += (1 << (sh - 1)) + (p >> 31); /* 负数补 -1，与 adj_rsh_round 的 half-away 语义一致 */
    return p >> sh;
}


/* ===================== 指定色调过渡区（Sonnoc 色彩匹配模式） ===================== */
/* 对应 UI 的 groupBox_setHueRange（Specified Hue Adjust）+ Trans Factor/Ratio：
   只在目标色相区间及其过渡带内调整，过渡带内“调整量渐变 + 降饱和”。

   处理区 = [hs - sp, he + ep]（可跨 0° 环绕），内含三段：
     起点过渡  [hs-sp, hs]       w 0 → 1
     核心区    [hs, he]          w = 1
     终点过渡  [he, he+ep]       w 1 → 0
   sp==ep==0 时为硬边界 [hs, he]（含两端）。过渡锥形线性、连续，两端天然衔接
   （核心区含两端），不存在任何单点空洞。

   角度全部为 Q14（360° = FIX_H_ONE = 16384 → 0.02197°/LSB）；权重 w 为 Q11（1.0 = FIX_S_ONE）。
   Trans Factor 为整数≥1（UI 范围 1..5）：同时作为融合权重陡度与降饱和平台陡度。
   Trans Ratio 为 Q11（0=关闭降饱和）。 */
#define ADJ_ZONE_RAMP_SH 16 /* 斜坡倒数定标：inv = (Δw << ADJ_ZONE_RAMP_SH) / 段长 */
#define ADJ_ZONE_TF_MAX 8   /* Trans Factor 上限（UI 为 5，留余量） */

/* 过渡区参数（UI 原样参数，Q14 角度 / Q11 比例） */
typedef struct {
    int32_t enabled;         /* 0 = 不做过渡区处理（等价全图调整） */
    int32_t hue_start_q14;   /* hs：目标色相范围起始角（支持跨 0° 环绕） */
    int32_t hue_end_q14;     /* he：目标色相范围结束角；**允许 FIX_H_ONE(=16384) 表示 360°**
                                （与 0° 区分：he=16384,hs=0 为整圈，he=0,hs=0 为单点） */
    int32_t start_pad_q14;   /* sp：起始端向外过渡角（0 = 无过渡，硬边界） */
    int32_t end_pad_q14;     /* ep：结束端向外过渡角（0 = 无过渡，硬边界） */
    int32_t trans_factor;    /* Trans Factor（整数，≥1）：融合陡度 + 降饱和平台陡度 */
    int32_t trans_ratio_q11; /* Trans Ratio（Q11，[0,FIX_S_ONE]）：过渡区降饱和强度 */
} adj_hue_zone_cfg_t;

/* 过渡区浮点参数（UI 原样物理量：角度为度、比率为 [0,1]） */
typedef struct {
    int enabled;
    float hue_start;    /* 度 */
    float hue_end;      /* 度 */
    float start_pad;    /* 度 */
    float end_pad;      /* 度 */
    float trans_factor; /* ≥1 */
    float trans_ratio;  /* [0,1] */
} adj_hue_zone_cfg_f_t;

/* 预计算后的过渡区（每帧由 adj_hue_zone_setup 算一次，逐像素只需 adj_hue_zone_weight）。
   斜坡统一形式：w = w0 ± ramp(d, lo, len, inv)，ramp 把 (d-lo) 夹到 [0,len] 后乘 inv 右移
   ADJ_ZONE_RAMP_SH —— 逐像素无除法，乘积上界 = Δw<<ADJ_ZONE_RAMP_SH = 2^27（int32 安全）。 */
typedef struct {
    int32_t hsp;     /* 处理区起点 hs-sp（Q14，已回绕） */
    int32_t span;    /* 处理区长度 (he+ep)-(hs-sp)（Q14，≤整圈） */
    int32_t len_s;   /* 起点过渡长度 sp（Q14）；0 = 无起点过渡 */
    int32_t len_e;   /* 终点过渡长度 ep（Q14）；0 = 无终点过渡 */
    int32_t inv_s;   /* (FIX_S_ONE << ADJ_ZONE_RAMP_SH) / len_s（len_s=0 时为 0） */
    int32_t inv_e;   /* (FIX_S_ONE << ADJ_ZONE_RAMP_SH) / len_e（len_e=0 时为 0） */
    int32_t tf;      /* Trans Factor（整数 ≥1） */
    int32_t ratio_q11; /* Trans Ratio（Q11） */
    int32_t hard;      /* 1 = 无 Pad，硬边界 [hs,he] */
    int32_t enabled;
} adj_hue_zone_t;

/* 过渡区预计算（每帧一次）：参数合法化 + 斜坡倒数预计算。cfg=NULL 或 enabled=0 时置为关闭态。 */
void adj_hue_zone_setup(const adj_hue_zone_cfg_t *cfg, adj_hue_zone_t *z);

/* 逐像素过渡区权重（Q11）：0=保持原色、FIX_S_ONE=完全调整。
   轮廓： w=0（处理区外）→ [0,len_s] 升到 1 → 核心区 [len_s, span-len_e] 保持 1
   → [span-len_e, span] 降到 0 → w=0。三段依次覆盖赋值（后写优先），核心区**含两端**，
   因此 len_s==0（起点无过渡）时 d=0、或 len_e==0（终点无过渡）时 d=span 都不会落进
   掩码缝隙而回退到 0。len_s/len_e≤span 恒成立（span = 跨度 + len_s + len_e），故不存在
   两侧过渡带重叠的退化配置。 */
static inline int32_t adj_hue_zone_weight(const adj_hue_zone_t *z, int32_t h_q14)
{
    int32_t d, w;
    if (z->enabled == 0)
        return FIX_S_ONE;
    d = (h_q14 - z->hsp) & (FIX_H_ONE - 1);
    if (z->hard)
        return (d <= z->span) ? FIX_S_ONE : 0; /* 硬边界 [hs, he]（含两端） */
    w = 0;
    if (d <= z->len_s) /* 起点上升段（len_s==0 时 d=0 由核心区给 1） */
        w = ((d * z->inv_s) >> ADJ_ZONE_RAMP_SH); /* d≤len_s → 乘积 ≤ 2^27，int32 安全 */
    if (d >= z->len_s && d <= z->span - z->len_e)
        w = FIX_S_ONE; /* 核心区（含两端） */
    if (d >= z->span - z->len_e && d <= z->span) { /* 终点下降段（起点处 w=1，与核心区衔接） */
        int32_t dd = d - (z->span - z->len_e);
        if (dd > z->len_e)
            dd = z->len_e;
        w = FIX_S_ONE - ((dd * z->inv_e) >> ADJ_ZONE_RAMP_SH);
    }
    return CLIP(w, 0, FIX_S_ONE);
}

/* H 倒数表（惰性构建，全工程共用一份）。实现见 hsv_fixed.c */
const uint32_t *rcp6_tbl_u24_fixed(void);

/* 除法消除（窄乘法形式）：round(a * rcp / 2^rsh)，a ≤ 17bit 有符号、rcp ≤ 24bit。
   调用方把 a 自带的 2 的幂缩放(×2^SH)拆成右移 rsh = 定标位 - SH，乘法器只需 a×rcp 位宽
   （相比 a<<SH × rcp 少 SH 位），适合硬件实现。实现见 hsv_fixed.c */
int32_t rcp_mul_rsh(int32_t a, uint32_t rcp, int rsh);

/* ---------- 角度三角量（domain 无关；RGB 域绕灰轴旋转与 YCbCr 域极角旋转共用） ---------- */
/* sin(2*pi*k/256) 的 Q15 表（k = 0..256，末项为 360°，用于 wrap 处插值；1.0 = 32768）。
   定义见 hsv_fixed.c */
extern const int16_t g_adj_sin_q15[257];

/* angle_q14（360° = FIX_H_ONE）的 sin，Q15（1.0 = 32768）。
   表索引取 Q14 的高 8 bit（256 等分 360°），低 6 bit 线性插值。 */
static inline int32_t adj_sin_q15(int32_t angle_q14)
{
    uint32_t h = (uint32_t)angle_q14 & (uint32_t)(FIX_H_ONE - 1); /* 归一化到 [0, 360°) */
    uint32_t i = h >> (FIX_BITS_H - 8);                           /* 0..255 */
    int32_t f = (int32_t)(h & ((1u << (FIX_BITS_H - 8)) - 1));    /* 段内小数 0..63 */
    int32_t a = g_adj_sin_q15[i];
    int32_t d = (int32_t)g_adj_sin_q15[i + 1] - a;
    /* 注意：插值偏移量必须用有符号字面量，否则 d*f 会被提升为无符号、右移变逻辑移位 */
    return a + ((d * f + (1 << (FIX_BITS_H - 9))) >> (FIX_BITS_H - 8));
}

/* angle_q14 的 cos，Q15（1.0 = 32768）：cos(x) = sin(x + 90°) */
static inline int32_t adj_cos_q15(int32_t angle_q14) { return adj_sin_q15(angle_q14 + (FIX_H_ONE >> 2)); }

/* luma 权重 Q16（1.0 = 2^16；末位调整使权重和恰为 2^16，保证灰阶混合不偏色） */
#define ADJ_LUMA_BITS         16
#define ADJ_LUMA_BT709_R      13933
#define ADJ_LUMA_BT709_G      46877
#define ADJ_LUMA_BT709_B      4726 /* 65536-13933-46877 */
#define ADJ_LUMA_BT601_R      19594
#define ADJ_LUMA_BT601_G      38470
#define ADJ_LUMA_BT601_B      7472 /* 65536-19594-38470 */
#define ADJ_LUMA_BT2020_R     17218
#define ADJ_LUMA_BT2020_G     44433
#define ADJ_LUMA_BT2020_B     3885 /* 65536-17218-44433 */
#define ADJ_LUMA_Display_P3_R 15006
#define ADJ_LUMA_Display_P3_G 45334
#define ADJ_LUMA_Display_P3_B 5196 /* 65536-15006-45334（Display P3：DCI-P3 原色 + D65） */
#define ADJ_LUMA_Theater_P3_R 13729
#define ADJ_LUMA_Theater_P3_G 47290
#define ADJ_LUMA_Theater_P3_B 4517 /* 65536-13729-47290（Theater P3：DCI-P3 原色 + D63） */

void rgb2hsv_v0_classic(uint16_t r, uint16_t g, uint16_t b, uint16_t *h14, uint16_t *s11, uint16_t *v10);
void rgb2hsv_v1_no_branch(uint16_t r, uint16_t g, uint16_t b, uint16_t *h14, uint16_t *s11, uint16_t *v10);
void rgb2hsv_v2_no_division(uint16_t r, uint16_t g, uint16_t b, uint16_t *h14, uint16_t *s11, uint16_t *v10);
void rgb2hsv_v3_optimal(uint16_t r, uint16_t g, uint16_t b, uint16_t *h14, uint16_t *s11, uint16_t *v10);
void rgb2hsv_v4_optimal(uint16_t r, uint16_t g, uint16_t b, uint16_t *h14, uint16_t *s11, uint16_t *v10);

static inline void rgb2hsv_fix_u8(uint8_t R, uint8_t G, uint8_t B, uint16_t *H, uint16_t *S, uint16_t *V)
{
    rgb2hsv_v3_optimal(R, G, B, H, S, V);
}

static inline void rgb2hsv_fix_u10(uint16_t R, uint16_t G, uint16_t B, uint16_t *H, uint16_t *S, uint16_t *V)
{
    rgb2hsv_v3_optimal(R, G, B, H, S, V);
}

void hsv2rgb_v0_classic(uint16_t h14, uint16_t s11, uint16_t v10, uint16_t maxv, uint16_t *R, uint16_t *G, uint16_t *B);
void hsv2rgb_v1_no_branch(uint16_t h14, uint16_t s11, uint16_t v10, uint16_t maxv, uint16_t *R, uint16_t *G, uint16_t *B);
void hsv2rgb_v2_no_division(uint16_t h14, uint16_t s11, uint16_t v10, uint16_t maxv, uint16_t *R, uint16_t *G, uint16_t *B);
void hsv2rgb_v3_optimal(uint16_t h14, uint16_t s11, uint16_t v10, uint16_t maxv, uint16_t *R, uint16_t *G, uint16_t *B);
void hsv2rgb_v4_hexwalk(uint16_t h14, uint16_t s11, uint16_t v10, uint16_t maxv, uint16_t *R, uint16_t *G, uint16_t *B);

static inline void hsv2rgb_fix_u8(uint16_t H, uint16_t S, uint16_t V, uint8_t *R, uint8_t *G, uint8_t *B)
{
    uint16_t r, g, b;
    hsv2rgb_v3_optimal(H, S, V, 255, &r, &g, &b);
    *R = (uint8_t)r;
    *G = (uint8_t)g;
    *B = (uint8_t)b;
}

/* HSV -> RGB(10bit) */
static inline void hsv2rgb_fix_u10(uint16_t H, uint16_t S, uint16_t V, uint16_t *R, uint16_t *G, uint16_t *B)
{
    hsv2rgb_v3_optimal(H, S, V, 1023, R, G, B);
}


/* H Q14 -> H Q16（<<2，精确） */
static inline int32_t hsv_h14_to_q16(int32_t H14) { return H14 << 2; }

/* H Q16 -> H Q14（>>2，精确；Q16 低 2 bit 被丢弃） */
static inline int32_t hsv_h14_from_q16(int32_t H16) { return H16 >> 2; }


/* ================= RGB 域直接 BCSH 调整（adjust_rgb 定点版） ================= */
/* 对应 script/bcsh/hsv_adjust.py 的 adjust_rgb：不经过 HSV 域转换，逐通道直接调整。
   - V：三通道统一先按 mode_b 施加 brightness、再施加 contrast(mode_c)（**db 先于 gc 生效**；
        全程像素域，不归一化；每步各自 clamp 到 [0, maxv]）
        mode_b='add'   v'=clip(v+db)（db∈[-1,1]，中性 0）
        mode_b='mul'   v'=clip(v*gv)（gv∈[0,4]，中性 1.0）
        mode_b='rate2limit'  db∈[0,2]，中性 1：db<1 向黑靠拢 v'=v*db（混入 1-db 黑）；
        db>1 向白靠拢 v'=v+(db-1)*(maxv-v)（混入 db-1 白）
        mode_c='mid'   v'=clip((v-0.5)*gc+0.5)（过 v=0.5 中点，gc∈[0,4]，中性 1.0）
        mode_c='zero'  v'=clip(gc*v)（过 v=0 原点，gc∈[0,4]，中性 1.0）
        mode_c='both'  gc<1 用 'zero'、gc>=1 用 'mid'（gc==1 恒等）
        mode_c='tanslant' v'=clip((v-0.5)*tan((c+1)π/4)+0.5)（c∈[-1,1]，中性 0）
   - S：灰阶混合 out = scale*in + (1-scale)*gray，gray 为 luma（BT.709/BT.601/BT.2020）；
   - H：按 mode_h：
        'add'        ModeAdd 六边形色相加法 h'=(h+angle)%360：一次 rgb2hsv 取色相（M/m/C 不变
                     -> S/V 天然不变），平移后在 RGB 域按 6 段 TAB 重排中间通道（同
                     hsv2rgb_v4_hexwalk 模型），无需 hsv2rgb 重建
        'rotategray' RotateOnGray 绕灰轴 (1,1,1)/√3 旋转（灰阶不变，会色相偏移）
   定点格式（与 hsv_fixed 其余接口一致）：
     gain_c     : Q11（1.0 = FIX_S_ONE）；mid/zero/both 取 [0,4]，tanslant 取 [-1,1]
     delta_b    : Q11（1.0 = FIX_S_ONE）；add 取 [-1,1]，mul 取 [0,4]，rate2limit 取 [0,2]
     delta_s    : Q11（1.0 = FIX_S_ONE）；灰阶混合乘性增益 [0,4]，中性 1.0
     tolerance_s: Q11（1.0 = FIX_S_ONE）；S 门控 [0,1]（保留参数位，当前未启用）
     angle_q14  : Q14（360° = FIX_H_ONE）；H 平移/旋转量
   tanslant 的 tan 用 4097 项 Q11 直接查表（θ Q14 直接索引，无插值，无 float/math 依赖）。 */
typedef enum {
    ADJ_RGB_MODE_C_MID = 0,  /* GainAtMid：过 v=0.5 中点 */
    ADJ_RGB_MODE_C_ZERO,     /* GainAtZero：过 v=0 原点 */
    ADJ_RGB_MODE_C_BOTH,     /* GainAtBoth：gc<1 用 Zero、gc>=1 用 Mid（gc==1 恒等） */
    ADJ_RGB_MODE_C_TANSLANT, /* TanSlant：tan((c+1)π/4) */
} adj_rgb_mode_c_t;

typedef enum {
    ADJ_RGB_MODE_B_ADD = 0,    /* 加性（默认，同 Python） */
    ADJ_RGB_MODE_B_MUL,        /* 乘性 */
    ADJ_RGB_MODE_B_RATE2LIMIT, /* 按比例向黑/白极限靠拢 */
} adj_rgb_mode_b_t;

typedef enum {
    ADJ_RGB_MODE_S_ADD = 0,    /* 加性（默认，同 Python） */
    ADJ_RGB_MODE_S_MUL,        /* 乘性 scale */
    ADJ_RGB_MODE_S_RATE2LIMIT, /* 按比例向灰度/全饱和靠拢 */
} adj_rgb_mode_s_t;

typedef enum {
    ADJ_RGB_MODE_H_ADD = 0,    /* ModeAdd：六边形色相加法 h'=(h+angle)%360 */
    ADJ_RGB_MODE_H_ROTATEGRAY, /* RotateOnGray：绕灰轴 (1,1,1)/√3 旋转 */
} adj_rgb_mode_h_t;

typedef enum {
    ADJ_RGB_GRAY_BT709 = 0,  /* luma BT.709 */
    ADJ_RGB_GRAY_BT601,      /* luma BT.601 */
    ADJ_RGB_GRAY_BT2020,     /* luma BT.2020 */
    ADJ_RGB_GRAY_P3,         /* luma Display P3（DCI-P3 原色 + D65） */
    ADJ_RGB_GRAY_THEATER_P3, /* luma Theater P3（DCI-P3 原色 + D63） */
} adj_rgb_gray_coef_t;


/* 单通道 V 步（Q11 像素域，pixel×2^11）：brightness(mode_b) → contrast(mode_c)。
   q 为 Q11 像素域输入；gc 为 Q11 增益；gv_q11/d_q11/db_q11 分别为 Q11 的
   mul 增益（中性 1.0）、rate2limit 的 d=db-1（中性 0）、add 的 db∈[-1,1]（中性 0）。
   **先施加 brightness（db）、再施加 contrast（gc）**，每步各自 clamp 到
   [0, maxv<<11]；maxv/2 的 Q11 表示为 maxv<<10（精确）。
   add 的 db 是**归一化量**（∈[-1,1]，1.0 对应满量程），内部按 ×maxv 折算到
   Q11 像素域后再相加；mul/rate2limit 为无量纲比例，直接作用。
   返回值 Q11 像素域，由上层统一舍入回像素（避免逐步骤舍入误差累积）。
   RGB 域（adjust_rgb_fix）与 HSV 域（adjust_hsv_fix）共用。实现见 hsv_fixed.c */
int32_t adj_apply_v(int32_t q, int32_t maxv, int32_t gc, int mode_c, int32_t gv_q11, int32_t d_q11, int32_t db_q11, int mode_b);


/* 单像素 HSV 域 BCSH 调整核心（像素域 [0,maxv]，maxv=255(u8)/1023(u10)）。
   与 adjust_rgb_fix 参数/模式完全一致（mode_h 除外，HSV 域 H 恒为 ModeAdd），
   但走 HSV 域往返：rgb2hsv_v3_optimal 取 H/S/V，在 HSV 域调整 V（先 brightness 后 contrast，
   db 先于 gc 生效）、
   S（mode_s：add 加性 / mul 乘性 scale / rate2limit 按比例向灰度/全饱和靠拢）、
   H（ModeAdd 平移），再用 hsv2rgb_v4_hexwalk 重建 RGB。
   对应 script/bcsh/hsv_adjust.py 的 adjust_hsv。
   tolerance_s（Q11）：S 增色（放大）门控，三个 mode_s 共用——S<tolerance_s 的像素
   保持原样；减色/中性始终允许（add 的 ds<=0、mul 的 gs<=1、rate2limit 的 d<=0）。 */
void adjust_hsv_fix(uint16_t r, uint16_t g, uint16_t b, uint16_t maxv, int32_t gain_c, int32_t delta_b, int32_t delta_s,
    int32_t tolerance_s, int32_t angle_q14, int gray_coef, int mode_c, int mode_b, int mode_s, uint16_t *ro,
    uint16_t *go, uint16_t *bo);

/* u8 缓冲接口（整帧统一参数） */
static inline void adjust_hsv_fix_u8(const uint8_t *rgb, int n, int32_t gain_c, int32_t delta_b, int32_t delta_s,
    int32_t tolerance_s, int32_t angle_q14, int gray_coef, int mode_c, int mode_b, int mode_s, uint8_t *out)
{
    for (int i = 0; i < n; i++) {
        uint16_t r1, g1, b1;
        adjust_hsv_fix(rgb[3 * i], rgb[3 * i + 1], rgb[3 * i + 2], 255, gain_c, delta_b, delta_s, tolerance_s,
            angle_q14, gray_coef, mode_c, mode_b, mode_s, &r1, &g1, &b1);
        out[3 * i] = (uint8_t)r1;
        out[3 * i + 1] = (uint8_t)g1;
        out[3 * i + 2] = (uint8_t)b1;
    }
}

/* u10 缓冲接口（整帧统一参数） */
static inline void adjust_hsv_fix_u10(const uint16_t *rgb, int n, int32_t gain_c, int32_t delta_b, int32_t delta_s,
    int32_t tolerance_s, int32_t angle_q14, int gray_coef, int mode_c, int mode_b, int mode_s, uint16_t *out)
{
    for (int i = 0; i < n; i++) {
        uint16_t r1, g1, b1;
        adjust_hsv_fix(rgb[3 * i], rgb[3 * i + 1], rgb[3 * i + 2], 1023, gain_c, delta_b, delta_s, tolerance_s,
            angle_q14, gray_coef, mode_c, mode_b, mode_s, &r1, &g1, &b1);
        out[3 * i] = r1;
        out[3 * i + 1] = g1;
        out[3 * i + 2] = b1;
    }
}


/* ===================== Sonnoc 固定管线 HSV 域 BCSH（无 mode 分支） ===================== */
/* 对应 UI 的 HSV 处理域（Adjust Field = HSV），固定 mode：B(add) -> S(mul) -> H(add)，
   Hue Goal = SameTarget（目标色相 + 进度），无 C（对比度）步：

     B  add   v' = clip(v + delta_b)                              delta_b∈[-1,1]，中性 0
     S  mul   s' = clip(s * delta_s)                              delta_s∈[0,4]，中性 1.0
     H  add   h' = (h + progress·wrap180(hue_goal − h)) mod 360   progress∈[0,1]，中性 0
              （SameTarget：沿最短有向弧向目标色相旋转 progress 比例；progress=1 时
                rot 恰等于弧长，**精确到达目标色相**）

   定点格式（与 hsv_fixed 其余接口一致）：
     delta_b      : Q11（1.0 = FIX_S_ONE = 2048），[-1,1]
     delta_s      : Q11（1.0 = FIX_S_ONE），[0,4]
     hue_goal_q14 : Q14（360° = FIX_H_ONE = 16384）→ 0.02197°/LSB，
                    **满足 0.3° 精度要求**（0.3° 仅需 11 bit，Q14 有 8 倍余量）
     progress_q11 : Q11（1.0 = FIX_S_ONE），内部 clip 到 [0,1]
   像素域 [0, maxv]（u8: 255 / u10: 1023），内部保持像素域 + Q11/Q14 定点。
   位宽优化：B 折算为**整数像素偏移**（11bit，逐像素只 1 次加法，无 Q11 中间量）；
   S/H 用 adj_mul_q32（S 11bit × gain 13bit、arc 15bit × progress 11bit，均在 int32 内）。

   过渡区（zone 非 NULL 且 enabled）额外做两步（与 Python UI 步骤 5️⃣ 一致）：
     ① 按融合权重 w = steepen(w_raw, Trans Factor) 把“原色”与“完全调整结果”融合
        （H 走圆环插值、S/V 线性），权重 w_raw 由 hs/he + 两端 Pad 决定；
     ② 降饱和：S ← S·(1 − damp)，damp = Trans Ratio·(1 − |2·w_raw−1|^Trans Factor)。
   zone=NULL / enabled=0 时 w≡1.0、damp≡0，退化为全图调整。 */
void adjust_hsv_sonnoc_fix(uint16_t r, uint16_t g, uint16_t b, uint16_t maxv, int32_t delta_b, int32_t delta_s,
    int32_t hue_goal_q14, int32_t progress_q11, const adj_hue_zone_t *zone, uint16_t *ro, uint16_t *go, uint16_t *bo);

/* 同管线的浮点参考实现（精度基准，无定点量化）：r/g/b∈[0,1]（归一化像素域），
   参数为物理量 delta_b∈[-1,1] / delta_s∈[0,4] / hue_goal_deg（度）/ progress∈[0,1]；
   zone 为浮点参数形式（度），NULL 表示不做过渡区处理；
   输出 ro/go/bo∈[0,1]（已 clip）。六边形 HSV 模型（与定点版同模型），
   实现见 hsv_fixed.c（仅依赖 math.h 的 fmodf/fabsf/fminf/fmaxf）。 */
void adjust_hsv_sonnoc_float(float r, float g, float b, float delta_b, float delta_s, float hue_goal_deg,
    float progress, const adj_hue_zone_cfg_f_t *zone, float *ro, float *go, float *bo);

#endif /* HSV_FIXED_H */
