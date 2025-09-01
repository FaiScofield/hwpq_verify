
## work on Linux/WSL

BUILD_DIR="build_linux_x64"
BUILD_TYPE="Release"

cmake -G "Unix Makefiles" -H./ -B${BUILD_DIR} \
    -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
    -DCMAKE_BUILD_TYPE=${BUILD_TYPE} \
    -DRK_SOC="RK3572"

# get current working directory for later return
# WORK_DIR=$PWD
(cd ${BUILD_DIR} && make -j4 install) || exit 1
# cd ${WORK_DIR}
