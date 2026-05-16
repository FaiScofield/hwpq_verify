/**
 * @copyright: Copyright (c) Rockchip Electronics Co., Ltd. 2026-. All rights reserved.
 * @brief:     Common definitions for pixfmt unit tests
 * @author:    vance.wu@rock-chips.com
 * @create:    2026-05-16
 */

#ifndef _TEST_PIXFMT_COMMON_H_
#define _TEST_PIXFMT_COMMON_H_

#include <stdio.h>

#define ARRAY_SIZE(arr) (sizeof(arr) / sizeof((arr)[0]))

extern int g_test_passed;
extern int g_test_failed;

#define TEST_ASSERT(cond, fmt, ...)                    \
    do {                                               \
        if (cond) {                                    \
            g_test_passed++;                           \
            printf("[PASS] " fmt "\n", ##__VA_ARGS__); \
        }                                              \
        else {                                         \
            g_test_failed++;                           \
            printf("[FAIL] " fmt "\n", ##__VA_ARGS__); \
        }                                              \
    } while (0)

#endif /* _TEST_PIXFMT_COMMON_H_ */
