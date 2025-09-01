
@echo off

set GENERATOR="Visual Studio 17 2022"
set BUILD_DIR="build_win32_msvc"
set BUILD_TYPE="Release"
set TARGETS="install"

cmake -G %GENERATOR% -H../ -B%BUILD_DIR% ^
    -DCMAKE_VERBOSE_MAKEFILE=OFF ^
    -DCMAKE_EXPORT_COMPILE_COMMANDS=ON ^
    -DCMAKE_BUILD_TYPE=%BUILD_TYPE% ^
    -DRK_SOC="RK3572"

cmake --build %BUILD_DIR% --config %BUILD_TYPE% --target install -j4 --


@echo on