/**
 * @file    dci_verify_stubs.cpp
 * @brief   Placeholder stubs for dciVerify* API functions.
 *
 * The real implementations are expected from the RkVopAlgos_git DCI verify
 * library (linked via a separate prebuilt .a/.lib). These stubs allow the
 * runner to compile and link until the library is available.
 *
 * Once the real library is placed in prebuilt/, remove this file and update
 * CMakeLists.txt to link against it.
 */

#include "dci_verify_api.h"
#include <cstdio>

#ifdef __cplusplus
extern "C" {
#endif

int dciVerifyInit(dci_handle_t *handle, dci_init_param_t *init_param) {
    (void)init_param;
    *handle = reinterpret_cast<void *>(1);
    fprintf(stderr, "[STUB] dciVerifyInit called\n");
    return 0;
}

int dciVerifyDeinit(dci_handle_t handle) {
    (void)handle;
    fprintf(stderr, "[STUB] dciVerifyDeinit called\n");
    return 0;
}

int dciVerifyProc(dci_handle_t handle, dci_proc_param_t *proc_params) {
    (void)handle;
    (void)proc_params;
    fprintf(stderr, "[STUB] dciVerifyProc called\n");
    return 0;
}

#ifdef __cplusplus
}
#endif
