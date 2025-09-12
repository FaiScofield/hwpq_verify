
@echo off

set GENERATOR="Visual Studio 17 2022"
set BUILD_DIR="build_win32_msvc"
set BUILD_TYPE="Debug"
SET RK_SOC="RK3572"
set TARGETS="install"

:: parse command line arguments
if /i "%~1" == "Release" (
    set BUILD_TYPE=Release
    @echo get BUILD_TYPE from cmd: %~1
)
if NOT "%~2" == "" (
    set RK_SOC=%~2
    @echo get RK_SOC from cmd: %~2
)
@echo -------------------------------

cmake -G %GENERATOR% -H../ -B%BUILD_DIR% ^
    -DCMAKE_VERBOSE_MAKEFILE=OFF ^
    -DCMAKE_EXPORT_COMPILE_COMMANDS=ON ^
    -DCMAKE_BUILD_TYPE=%BUILD_TYPE% ^
    -DRK_SOC=%RK_SOC%

cmake --build %BUILD_DIR% --config %BUILD_TYPE% --target install -j4 --


@echo on