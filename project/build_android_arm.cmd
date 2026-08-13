@echo off
::
:: Usage:
::   build_android_arm.cmd [-t debug|release] [-a 64|32|arm64-v8a|armeabi-v7a] [-p rk3572] [-c] [-e] [-h]
::
:: Options:
::   -t, --type     : Build type (default: release, options: debug, release)
::   -a, --abi      : Android ABI (default: arm64-v8a, options: 64, 32, arm64-v8a, armeabi-v7a)
::   -p, --platform : Platform type (default: RK3572)
::   -c, --clean    : Clean build artifacts before build
::   -e, --export   : Export compile_commands.json to project root
::   -h, --help     : Show help information

:: Directory vars
set SCRIPT_DIR=%~dp0
if "%SCRIPT_DIR:~-1%"=="\" set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%
set PROJECT_ROOT=%SCRIPT_DIR%\..

:: NOTE: change the NDK path to your own. Requires android.toolchain.cmake at:
::   %ANDROID_NDK%/build/cmake/android.toolchain.cmake
set ANDROID_NDK=D:/android-ndk-r21e
set ANDROID_ABI=arm64-v8a
set ANDROID_PLATFORM=android-21
SET RK_SOC=RK3572
set BUILD_TYPE=release
set EXPORT_JSON=OFF
set CLEAN_BUILD=0

:: parse command line arguments
:parse_args
if "%~1" == "" goto end_parse_args
if /i "%1"=="-h" goto :show_help
if /i "%1"=="--help" goto :show_help
if /i "%1"=="-c" (
    set CLEAN_BUILD=1
    shift
    goto :parse_args
)
if /i "%1"=="--clean" (
    set CLEAN_BUILD=1
    shift
    goto :parse_args
)
if /i "%~1" == "-t" (
    if /i "%~2" == "release" (
        set BUILD_TYPE=Release
        @echo get BUILD_TYPE from cmd: %~2
    ) else (
        set BUILD_TYPE=Debug
        @echo get BUILD_TYPE from cmd: %~2
    )
    shift
    shift
    goto parse_args
)
if /i "%~1" == "--type" (
    if /i "%~2" == "release" (
        set BUILD_TYPE=Release
        @echo get BUILD_TYPE from cmd: %~2
    ) else (
        set BUILD_TYPE=Debug
        @echo get BUILD_TYPE from cmd: %~2
    )
    shift
    shift
    goto parse_args
)
if /i "%~1" == "-a" (
    set ANDROID_ABI=%~2
    @echo get ANDROID_ABI from cmd: %~2
    shift
    shift
    goto parse_args
)
if /i "%~1" == "--abi" (
    set ANDROID_ABI=%~2
    @echo get ANDROID_ABI from cmd: %~2
    shift
    shift
    goto parse_args
)
if /i "%~1" == "-p" (
    set RK_SOC=%~2
    @echo get RK_SOC from cmd: %~2
    shift
    shift
    goto parse_args
)
if /i "%~1" == "--platform" (
    set RK_SOC=%~2
    @echo get RK_SOC from cmd: %~2
    shift
    shift
    goto parse_args
)
if /i "%~1" == "-e" (
    set EXPORT_JSON=ON
    @echo get EXPORT_JSON from cmd: ON
    shift
    goto parse_args
)
if /i "%~1" == "--export" (
    set EXPORT_JSON=ON
    @echo get EXPORT_JSON from cmd: ON
    shift
    goto parse_args
)
shift
goto parse_args
:end_parse_args

:: normalize ABI aliases: 64 -> arm64-v8a, 32 -> armeabi-v7a
if /i "%ANDROID_ABI%"=="64" set ANDROID_ABI=arm64-v8a
if /i "%ANDROID_ABI%"=="32" set ANDROID_ABI=armeabi-v7a

set ABI_OK=0
if /i "%ANDROID_ABI%"=="arm64-v8a" set ABI_OK=1
if /i "%ANDROID_ABI%"=="armeabi-v7a" set ABI_OK=1
if not "%ABI_OK%"=="1" (
    echo Error: invalid ABI '%ANDROID_ABI%', options: 64, 32, arm64-v8a, armeabi-v7a
    exit /b 1
)

:: add NDK prebuilt tools (ninja/make) to PATH
set PATH=%ANDROID_NDK%/prebuilt/windows-x86_64/bin/;%PATH%

set TOOLCHAIN_FILE=%ANDROID_NDK%/build/cmake/android.toolchain.cmake
set BUILD_DIR=%SCRIPT_DIR%\build_%ANDROID_ABI%_%BUILD_TYPE%

echo .
echo Android NDK: %ANDROID_NDK%
echo Script dir: %SCRIPT_DIR%
echo Project root: %PROJECT_ROOT%
echo Build type: %BUILD_TYPE%
echo Android ABI: %ANDROID_ABI%
echo Android platform: %ANDROID_PLATFORM%
echo Build directory: %BUILD_DIR%
echo Clean build cache: %CLEAN_BUILD%
echo.

if not exist "%TOOLCHAIN_FILE%" (
    echo Error: Android NDK toolchain not found at %TOOLCHAIN_FILE%
    echo Please set ANDROID_NDK correctly in this script.
    exit /b 1
)

:: Clean build artifacts if requested
if /i "%CLEAN_BUILD%"=="1" (
    echo Cleaning build directory: %BUILD_DIR%
    if exist "%BUILD_DIR%" (
        rd /S /Q "%BUILD_DIR%"
        echo Deleted build directory
    )
)

cmake -G "Ninja" -H"%PROJECT_ROOT%" -B"%BUILD_DIR%" ^
    -DCMAKE_TOOLCHAIN_FILE="%TOOLCHAIN_FILE%" ^
    -DANDROID_NDK="%ANDROID_NDK%" ^
    -DANDROID_ABI=%ANDROID_ABI% ^
    -DANDROID_PLATFORM=%ANDROID_PLATFORM% ^
    -DCMAKE_VERBOSE_MAKEFILE=OFF ^
    -DCMAKE_EXPORT_COMPILE_COMMANDS=ON ^
    -DCMAKE_BUILD_TYPE=%BUILD_TYPE% ^
    -DRK_SOC=%RK_SOC%

if errorlevel 1 (
    echo.
    echo Error: CMake configuration failed.
    exit /b 1
)

echo.
echo CMake configuration completed.
echo.

cmake --build "%BUILD_DIR%" --config %BUILD_TYPE% --target install -j 4 -- -d explain

if errorlevel 1 (
    echo.
    echo Error: Build failed.
    exit /b 1
)

:: copy compile_commands.json to project root
if /i "%EXPORT_JSON%" == "ON" (
    if exist "%BUILD_DIR%\compile_commands.json" (
        copy /Y "%BUILD_DIR%\compile_commands.json" "%PROJECT_ROOT%\"
        echo Exported compile_commands.json to %PROJECT_ROOT%
    ) else (
        echo Warning: compile_commands.json not found, skipping export.
    )
)

echo.
echo Build completed.
exit /b 0
@echo on

:show_help
echo.
echo ========================================
echo   build_android_arm.cmd - Android ARM Build Script
echo ========================================
echo.
echo Usage:
echo   build_android_arm.cmd [-t debug^|release] [-a 64^|32^|arm64-v8a^|armeabi-v7a] [-p rk3572] [-c] [-e] [-h]
echo.
echo Options:
echo   -t, --type     ^<type^>      Build type (default: release) Options: debug, release
echo   -a, --abi      ^<abi^>       Android ABI (default: arm64-v8a) Options: 64, 32, arm64-v8a, armeabi-v7a
echo   -p, --platform ^<platform^>  Platform type (default: RK3572)
echo   -c, --clean    Removes entire build directory before build
echo   -e, --export   Export compile_commands.json to project root
echo   -h, --help     Show this help information and exit
echo.
echo ========================================
exit /b 0