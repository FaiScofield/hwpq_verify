#ifndef __dci_API_H__
#define __dci_API_H__

#include "rkvop_model_verify_com.h"
#include <stdint.h>
// #include "rk3576_vop_regs.h"

typedef void *dci_handle_t;

typedef struct {
    int         platform;
    uint32_t    debug_dump_mask; // 0 disables temp dumps, 0xff keeps all dumps
    char        debug_path[2048];
} dci_init_param_t;

typedef struct {
    int dci_enable;
    int dci_mode; // 1-reg_cfg, 2-kernel_cfg, 3-vop_prop, 4-only_hist, others-json_cfg

    /* io info */
    img_info_t src_info;
    img_info_t dst_info;
    int        is_src_fullrange;
    int        frame_idx;
    int        frame_num;
    // input pixel format (10bit planar) for DCI, see pix_fmt. (PIX_YUV444P_10 or PIX_RGB101010)
    int        pixel_format; //[O] output for now

    /* config path */
    char config_path[2048];
    char reg_path[2048];

    /* optional parameter overrides, set to invalid values (-1) to use JSON defaults */
    struct {
        int     gain_low;       // 32 norm, [0, (32)], 低亮度曲线增益
        int     gain_mid;       // 32 norm, [0, (32)], 中亮度曲线增益
        int     gain_high;      // 32 norm, [0, (32)], 高亮度曲线增益
    } cf;

    struct {
        int     splitPoint;   // [0, (125), 1023](rec), 直方图分隔点, on U10 domain, 代码内会移位到 8bit 域
        float   leftClip;     // [0.01f, (1.0f)](rec), 左半直方图 clip 比例
        float   rightClip;    // [0.01f, (1.0f)](rec), 右半直方图 clip 比例
        int     overLap;      // [0, (16), 128](rec), 分隔点 overlap 宽度，取 ±overLap 两条曲线平均使过渡平滑
    } he;

    int         cf_he_ratio;  // 64 norm, [0, (64)], 0/64 means no CF/HE effct

    struct {
        int     enable;     // [0, 1], 0-禁用, 1-启用
        int     set_point;  // [0, (80), 1023](rec), 黑场拉伸锚点, 10bit 域
        int     ratio;      // 64 norm, [0, (64)], 拉伸强度, 0 表示不拉伸
        int     overlap;    // 64 norm, [(0), 64], 锚点 overlap 宽度
    } bs;

    struct {
        int     enable;     // [0, 1], 0-禁用, 1-启用
        int     set_point;  // [0, (80), 1023](rec), 白场拉伸锚点, 10bit 域
        int     ratio;      // 64 norm, [0, (64)], 拉伸强度, 0 表示不拉伸
        int     overlap;    // 64 norm, [(0), 64], 锚点 overlap 宽度
    } ws;

    struct {
        int     enable;         // range: [0, (1)], def: 1, 局部 CLAHE 使能
        float   clip_value;     // range: [0.0, 2.0], def: 1.0, 直方图 clip 强度, 越大局部效果越强
        int     local_ratio;    // range: [0, 32], def: 19, local/global 插值结果融合比例
        float   left_alpha;     // range: [0.1, 10.0],def: 3.0, 暗部 clip 增益
        float   left_ThrLmin;   // range: [0.0, 1.0], def: 0.5, 暗部 clip 下界
        float   left_ThrLmax;   // range: [0.5, 5.0], def: 2.3, 暗部 clip 上界
        float   left_lumRatio;  // range: [0.0, 1.0], def: 0.7, 暗部 block 的 clip 缩放
        float   right_alpha;    // range: [0.1, 10.0],def: 1.5, 亮部 clip 增益
        float   right_ThrRmin;  // range: [0.0, 1.0], def: 0.7, 亮部 clip 下界
        float   right_ThrRmax;  // range: [0.5, 6.0], def: 3.0, 亮部 clip 上界
    } clahe;

    struct {
        int     enable;                // range: [0, 1], def: 1
        int     saturation_w;          // range: [0, 64], def: 56, 饱和度权重, 对应硬件 saturation_w
        int     adj_luma_coring_zero;  // range: [0, 1023], def: 8, 色度门限下界
        int     adj_luma_coring_thrd;  // range: [0, 1023], def: 16, 色度门限上界
    } ca;
} dci_proc_param_t;

#ifdef __cplusplus
extern "C" {
#endif

int dciVerifyInit(dci_handle_t *handle, dci_init_param_t *init_param);

int dciVerifyDeinit(dci_handle_t handle);

int dciVerifyProc(dci_handle_t handle, dci_proc_param_t *proc_params);

int dciSetDefaultParams(dci_proc_param_t *proc_params);

#ifdef __cplusplus
}
#endif

#endif /* __dci_API_H__ */
