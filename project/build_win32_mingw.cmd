@echo off
@echo usage: build_win32_mingw.cmd ^[Debug^|Release^]

:: NOTE: change the mingw64 directory to your own. :: use a version such as: 'x86_64-8.1.0-release-posix-seh-rt_v6'
:: You might check the target compiler by running `D:/mingw64/bin/gcc.exe -v` Target: x86_64-w64-mingw32
@REM set MINGW_DIR="D:/mingw64"
set MINGW_DIR="D:/Qt/Tools/mingw1310_64"
set BUILD_TYPE=Debug

:: parse command line arguments
if /i "%~1" == "Release" (
    set BUILD_TYPE=Release
    @echo get BUILD_TYPE from cmd: %~1
)
@echo -------------------------------

set PROJECT_DIR=%~dp0\..\
set BUILD_DIR=%~dp0\build_win32_%BUILD_TYPE%
echo PROJECT_DIR: %PROJECT_DIR%
echo BUILD_DIR: %BUILD_DIR%

cmake -G "Ninja" -H%PROJECT_DIR% -B%BUILD_DIR% ^
    -DCMAKE_C_COMPILER="%MINGW_DIR%/bin/gcc.exe" ^
    -DCMAKE_CXX_COMPILER="%MINGW_DIR%/bin/g++.exe" ^
    -DCMAKE_VERBOSE_MAKEFILE=OFF ^
    -DCMAKE_EXPORT_COMPILE_COMMANDS=ON ^
    -DCMAKE_BUILD_TYPE="%BUILD_TYPE%"

cmake --build %BUILD_DIR% --config %BUILD_TYPE% --target install -j 4 -- -d explain

:: copy compile_commands.json to project root
copy /Y %BUILD_DIR%\compile_commands.json %PROJECT_DIR%\.vscode\

@echo on
