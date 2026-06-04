#ifndef __RKVOP_MODEL_VERIFY_COM_H__
#define __RKVOP_MODEL_VERIFY_COM_H__

#include <stdio.h>

/* DATA TYPE DEFINITIONS */
typedef enum {
    RKVOP_MODEL_VERIFY_OK = 0,
    RKVOP_MODEL_VERIFY_ERROR = -1,
    RKVOP_MODEL_ALLOCA_ERROR = -2,
} rkvop_model_verify_status_t;

typedef enum {
    RK_PLATFORM_RK3528, // 2023
    RK_PLATFORM_RK3576, // 2024
    RK_PLATFORM_RK3572, // 2025
    RK_PLATFORM_RK3538, // 2025
} rkvop_platform_t;
#if 0 /* move to rkvop_register.h */
const char *rkvop_platform_str(int plat_id);
int rkvop_platform_to_kernel_macro(int plat_id);
#endif

/* LOGGING MACROS */
#define RKVOP_LOGI(fmt, ...) printf("RKVOP-[I]-%s\tLine-%d:\t" fmt "\n", __func__, __LINE__, ##__VA_ARGS__)
#define RKVOP_LOGE(fmt, ...) printf("RKVOP-[E]-%s\tLine-%d:\t" fmt "\n", __func__, __LINE__, ##__VA_ARGS__)
#define RKVOP_LOGD(fmt, ...) printf("RKVOP-[D]-%s\tLine-%d:\t" fmt "\n", __func__, __LINE__, ##__VA_ARGS__)
#define LOGD_FUNC_IN()  LOGD("----s---- %s\n", __func__)
#define LOGD_FUNC_OUT() LOGD("----e---- %s\n", __func__)


#ifndef ARRAY_SIZE
#define ARRAY_SIZE(arr)     (sizeof(arr) / sizeof((arr)[0]))
#endif

#define DIV_255_FAST(x)     (((x) + 1 + (((x) + 1) >> 8)) >> 8)



/* DATA STRUCTURES DEFINITIONS */
#define RKVOP_IMG_MAX_PLANES 4
typedef struct {
    void *ptr;
    int offset;
    int pix_strd;
} plane_info_t;
typedef struct {
    plane_info_t plane_info[RKVOP_IMG_MAX_PLANES];
    int plane_num;
    int img_w[RKVOP_IMG_MAX_PLANES];
    int img_h[RKVOP_IMG_MAX_PLANES];
    int img_ws[RKVOP_IMG_MAX_PLANES];
    int img_hs[RKVOP_IMG_MAX_PLANES];
    int img_bits;
    int is_yuv;
    int is_rgb;
} img_info_t;


#endif /* __RKVOP_MODEL_VERIFY_COM_H__ */