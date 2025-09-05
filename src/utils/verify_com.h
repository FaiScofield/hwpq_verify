/**
 * @copyright Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
 * @description: verify_com.h
 * @author: vance.wu@rock-chips.com
 * @create: 2025-09-05
 * @history:
 */

#ifndef _VERIFY_COM_H_
#define _VERIFY_COM_H_

#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32
#include <direct.h>
#define acess       _access
#define mkdir(a, b) _mkdir(a)
#else
#include <sys/stat.h>
#endif

/********** directory / file operation **********/


bool is_directory(const char *path);
bool is_regular_file(const char *path);
const char *get_dirname(const char *path);
const char *get_basename(const char *path);

#endif /* _VERIFY_COM_H_ */