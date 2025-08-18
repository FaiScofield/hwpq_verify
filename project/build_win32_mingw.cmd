@echo off

set PWD="%~dp0"
set BUILD_TYPE=Debug
set BUILD_DIR=build_win32_%BUILD_TYPE%
:: NOTE: change the mingw64 directory to your own. :: use a version such as: 'x86_64-8.1.0-release-posix-seh-rt_v6'
:: You might check the target compiler by running `D:/mingw64/bin/gcc.exe -v` Target: x86_64-w64-mingw32
set MINGW_DIR="D:/mingw64"

cmake -G "MinGW Makefiles" -H../ -B%BUILD_DIR% ^
    -DCMAKE_MAKE_PROGRAM="%MINGW_DIR%/bin/mingw32-make.exe" ^
    -DCMAKE_C_COMPILER="%MINGW_DIR%/bin/gcc.exe" ^
    -DCMAKE_CXX_COMPILER="%MINGW_DIR%/bin/g++.exe" ^
    -DCMAKE_VERBOSE_MAKEFILE=OFF ^
    -DCMAKE_EXPORT_COMPILE_COMMANDS=ON ^
    -DCMAKE_BUILD_TYPE=%BUILD_TYPE% ^
    -DRK_SOC="RK3572"

cmake --build %BUILD_DIR% --target install -j 6 --


@echo on
