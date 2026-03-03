@echo off
@echo usage: build_win32_mingw.cmd ^[Debug^|Release^] ^[RK_PLATFORM^]

:: NOTE: change the mingw64 directory to your own. :: use a version such as: 'x86_64-8.1.0-release-posix-seh-rt_v6'
:: You might check the target compiler by running `D:/mingw64/bin/gcc.exe -v` Target: x86_64-w64-mingw32
set MINGW_DIR="D:/mingw64"
SET RK_SOC="RK3572"
set BUILD_TYPE=Debug

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

set PWD=%dp0
set BUILD_DIR=build_win32_%BUILD_TYPE%


cmake -G "MinGW Makefiles" -H../ -B%BUILD_DIR% ^
    -DCMAKE_MAKE_PROGRAM="%MINGW_DIR%/bin/mingw32-make.exe" ^
    -DCMAKE_C_COMPILER="%MINGW_DIR%/bin/gcc.exe" ^
    -DCMAKE_CXX_COMPILER="%MINGW_DIR%/bin/g++.exe" ^
    -DCMAKE_VERBOSE_MAKEFILE=OFF ^
    -DCMAKE_EXPORT_COMPILE_COMMANDS=ON ^
    -DCMAKE_BUILD_TYPE=%BUILD_TYPE% ^
    -DRK_SOC=%RK_SOC%

cmake --build %BUILD_DIR% --target install -j 6 --

:: copy compile_commands.json to project root
copy /Y %BUILD_DIR%/compile_commands.json ../

@echo on
