@echo off
setlocal EnableDelayedExpansion

rem ============================================================================
rem  Reusable PyInstaller build script for verify_tool_app / script tools.
rem
rem  Usage:
rem    project\build_pyinstaller.cmd [app_name]
rem
rem  Examples:
rem    project\build_pyinstaller.cmd                -> build test_app_hsv (default)
rem    project\build_pyinstaller.cmd test_app_acm   -> build test_app_acm
rem
rem  NOTE: each entry-point app needs its own .spec file under project\pyinstaller\
rem        (e.g. project\pyinstaller\test_app_hsv.spec). Copy an existing spec and
rem        adjust: Analysis entry script, name, pathex / datas / hiddenimports.
rem ============================================================================

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "REPO_ROOT=%%~fI"
set "SPEC_DIR=%REPO_ROOT%\project\pyinstaller"
set "ARTIFACT_DIR=%REPO_ROOT%\output\pyinstaller"
set "APP_NAME=test_app_hsv"

if not "%~1"=="" set "APP_NAME=%~1"

set "SPEC_FILE=%SPEC_DIR%\%APP_NAME%.spec"
if not exist "%SPEC_FILE%" (
    echo [ERROR] Spec file not found: %SPEC_FILE%
    echo   Each entry-point program needs its own .spec file under project\pyinstaller\.
    exit /b 1
)

echo Building "%APP_NAME%" with PyInstaller ...
echo   Spec: %SPEC_FILE%
python -m PyInstaller --noconfirm --clean ^
    --distpath "%ARTIFACT_DIR%\dist" ^
    --workpath "%ARTIFACT_DIR%\build" ^
    "%SPEC_FILE%"
if errorlevel 1 (
    echo [ERROR] PyInstaller build failed.
    exit /b 1
)

rem 把参数配置模板（doc\test_app_hsv_params.json.demo）复制到发布目录
rem （exe 同目录的 test_app_hsv_params.json，load_params 的默认加载位置）。
set "DEMO_FILE=%REPO_ROOT%\doc\test_app_hsv_params.json.demo"
set "DIST_DIR=%ARTIFACT_DIR%\dist\%APP_NAME%"
if exist "%DEMO_FILE%" (
    copy /y "%DEMO_FILE%" "%DIST_DIR%" >nul
    echo   Copied params template: %DEMO_FILE%
    echo     -^> %DIST_DIR%\test_app_hsv_params.json
) else (
    echo   [WARN] Params template not found: %DEMO_FILE%
)
echo.
echo Build complete: %DIST_DIR%\
echo Run: %DIST_DIR%\%APP_NAME%.exe
exit /b 0
