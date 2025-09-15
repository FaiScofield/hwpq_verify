#!/bin/bash

## work on Linux/WSL
echo usage: build_linux_host.cmd \[Debug\|Release\] \[RK_PLATFORM\]

ARG_1ST_LOWER=$(echo "$1" | tr '[:upper:]' '[:lower:]')

RK_SOC="RK3572"
BUILD_TYPE=Debug

## parse command line arguments
if [ "$ARG_1ST_LOWER" = "release" ]; then
    BUILD_TYPE=Release
    echo get BUILD_TYPE from cmd: $ARG_1ST_LOWER
fi
if [ "$2" != "" ]; then
    RK_SOC=$2
    echo get RK_SOC from cmd: $2
fi
echo -------------------------------

PWD=$dp0
BUILD_DIR=build_linux_x64_${BUILD_TYPE}


cmake -G "Unix Makefiles" -H../ -B${BUILD_DIR} \
    -DCMAKE_VERBOSE_MAKEFILE=OFF \
    -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
    -DCMAKE_BUILD_TYPE=${BUILD_TYPE} \
    -DRK_SOC=${RK_SOC}

# cmake --build ${BUILD_DIR} --target install -j 6 --
(cd ${BUILD_DIR} && make -j4 install) || exit 1