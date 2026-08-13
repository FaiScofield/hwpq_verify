
@echo off
::
:: Usage:
::   push_files_to_device.cmd [-a <abi>] [-t <target>] [-h]
::
:: Options:
::   -a, --abi    : target ABI (default: arm64-v8a)
::                  options: arm64-v8a, armeabi-v7a (Android),
::                           aarch64, armhf (Linux)
::   -t, --target : target to push (default: all; group or binary name)
::   -h, --help   : show this help message

:: Directory vars
set SCRIPT_DIR=%~dp0
if "%SCRIPT_DIR:~-1%"=="\" set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%
set BINARY_DIR=%SCRIPT_DIR%\..\output\bin

set ABI=arm64-v8a
set TARGET=all

:: parse command line arguments
:parse_args
if "%~1" == "" goto end_parse_args
if /i "%1"=="-h" goto :show_help
if /i "%1"=="--help" goto :show_help
if /i "%~1" == "-a" (
    set ABI=%~2
    @echo get ABI from cmd: %~2
    shift
    shift
    goto parse_args
)
if /i "%~1" == "--abi" (
    set ABI=%~2
    @echo get ABI from cmd: %~2
    shift
    shift
    goto parse_args
)
if /i "%~1" == "-t" (
    set TARGET=%~2
    @echo get TARGET from cmd: %~2
    shift
    shift
    goto parse_args
)
if /i "%~1" == "--target" (
    set TARGET=%~2
    @echo get TARGET from cmd: %~2
    shift
    shift
    goto parse_args
)
shift
goto parse_args
:end_parse_args

:: map ABI -> platform / remote dirs
if /i "%ABI%"=="arm64-v8a" (
    set PLATFORM=Android
    set REMOTE_DIR_BIN=/vendor/bin/
    set REMOTE_DIR_LIB=/vendor/lib64/
) else if /i "%ABI%"=="armeabi-v7a" (
    set PLATFORM=Android
    set REMOTE_DIR_BIN=/vendor/bin/
    set REMOTE_DIR_LIB=/vendor/lib/
) else if /i "%ABI%"=="aarch64" (
    set PLATFORM=Linux
    set REMOTE_DIR_BIN=/usr/bin/
    set REMOTE_DIR_LIB=/usr/lib64/
) else if /i "%ABI%"=="armhf" (
    set PLATFORM=Linux
    set REMOTE_DIR_BIN=/usr/bin/
    set REMOTE_DIR_LIB=/usr/lib/
) else (
    echo Error: invalid ABI '%ABI%', options: arm64-v8a, armeabi-v7a, aarch64, armhf
    exit /b 1
)

echo.
echo ABI:      %ABI%  (%PLATFORM%)
echo Target:   %TARGET%
echo Bin dir:  %BINARY_DIR%
echo Remote:   %REMOTE_DIR_BIN%
echo.

:: run push commands
adb wait-for-device
adb root
adb remount
adb shell setenforce 0

:: decide which binaries to push: 'all' or a group name (csc/dci/acm/com/hsv)
::   or a single binary name. NOTE: cmd requires `) else if ... (` on one line.
set PUSH_LIST=%TARGET%
if /i "%TARGET%"=="all" (
    set PUSH_LIST=csc_verify_demo dci_verify_demo acm_verify_demo test_verify_com post_csc_kernel_demo hsv_adjust_bench hsv_fixed_test hsv_float_test hsv_precision_test
) else if /i "%TARGET%"=="com" (
    set PUSH_LIST=test_verify_com
) else if /i "%TARGET%"=="csc" (
    set PUSH_LIST=csc_verify_demo post_csc_kernel_demo
) else if /i "%TARGET%"=="dci" (
    set PUSH_LIST=dci_verify_demo
) else if /i "%TARGET%"=="acm" (
    set PUSH_LIST=acm_verify_demo
) else if /i "%TARGET%"=="hsv" (
    set PUSH_LIST=hsv_fixed_test hsv_float_test hsv_precision_test hsv_adjust_bench
)

for %%T in (%PUSH_LIST%) do (
    if exist "%BINARY_DIR%\%%T" (
        adb push "%BINARY_DIR%\%%T" %REMOTE_DIR_BIN%
    ) else (
        echo Warning: %BINARY_DIR%\%%T not found, skipping.
    )
)

echo.
echo Push completed.
exit /b 0
@echo on

:show_help
echo.
echo ========================================
echo   push_files_to_device.cmd - Push Binaries To Device
echo ========================================
echo.
echo Usage:
echo   push_files_to_device.cmd [-a ^<abi^>] [-t ^<target^>] [-h]
echo.
echo Options:
echo   -a, --abi    ^<abi^>       Target ABI (default: arm64-v8a)
echo                        Options: arm64-v8a, armeabi-v7a (Android)
echo                                 aarch64, armhf (Linux)
echo   -t, --target ^<target^>    Target to push (default: all)
 echo                        Options: all, csc, dci, acm, com, hsv,
 echo                                 or a binary name (e.g. hsv_fixed_test)
 echo                        Groups:  csc=csc_verify_demo+post_csc_kernel_demo
 echo                                 dci=dci_verify_demo  acm=acm_verify_demo
 echo                                 com=test_verify_com
 echo                                 hsv=hsv_fixed_test+hsv_float_test+hsv_precision_test+hsv_adjust_bench
echo   -h, --help    Show this help information and exit
echo.
echo ========================================
exit /b 0