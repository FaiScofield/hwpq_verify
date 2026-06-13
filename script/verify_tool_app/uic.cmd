@echo off
setlocal EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
set "UI_DIR=%SCRIPT_DIR%ui"
set "OUT_DIR=%SCRIPT_DIR%ui_gen"
set "UIC_CMD="
set /a TOTAL_COUNT=0
set /a SUCCESS_COUNT=0
set /a FAIL_COUNT=0
set "FAIL_LOG=%TEMP%\verify_tool_app_uic_fail_%RANDOM%%RANDOM%.log"

if exist "%FAIL_LOG%" del /q "%FAIL_LOG%"

:parse_args
if "%~1"=="" goto args_done
if /I "%~1"=="--exe" (
    if "%~2"=="" (
        echo Missing value for --exe.
        exit /b 1
    )
    set "UIC_CMD=%~2"
    shift
    shift
    goto parse_args
)

echo Unknown argument: %~1
exit /b 1

:args_done
if not exist "%OUT_DIR%" (
    mkdir "%OUT_DIR%"
)

if not defined UIC_CMD (
    where pyside6-uic.exe >nul 2>nul
    if not errorlevel 1 (
        set "UIC_CMD=pyside6-uic.exe"
    )
)

if not defined UIC_CMD (
    where pyside6-uic >nul 2>nul
    if not errorlevel 1 (
        set "UIC_CMD=pyside6-uic"
    )
)

if not defined UIC_CMD (
    echo Cannot find pyside6-uic executable.
    exit /b 1
)

echo Generating PySide6 UI modules...
echo Using UIC command: %UIC_CMD%

call :run_uic "%UI_DIR%\io_ui.ui" "%OUT_DIR%\io_ui.py"
call :run_uic "%UI_DIR%\acm_ui.ui" "%OUT_DIR%\acm_ui.py"
call :run_uic "%UI_DIR%\io_preview_ui.ui" "%OUT_DIR%\io_preview_ui.py"
call :run_uic "%UI_DIR%\acm_test_app_mainwindow.ui" "%OUT_DIR%\acm_test_app_mainwindow.py"

if not exist "%OUT_DIR%\__init__.py" (
    > "%OUT_DIR%\__init__.py" echo """Generated UI package for verify_tool_app."""
)

echo.
echo UI generation summary:
echo   Total:   %TOTAL_COUNT%
echo   Success: %SUCCESS_COUNT%
echo   Failed:  %FAIL_COUNT%

if %FAIL_COUNT% gtr 0 (
    echo.
    echo Failed files:
    type "%FAIL_LOG%"
    del /q "%FAIL_LOG%" >nul 2>nul
    exit /b 1
)

if exist "%FAIL_LOG%" del /q "%FAIL_LOG%" >nul 2>nul
echo.
echo UI generation finished: %OUT_DIR%
exit /b 0

:run_uic
set /a TOTAL_COUNT+=1
set "SRC_FILE=%~1"
set "DST_FILE=%~2"
set "TMP_LOG=%TEMP%\verify_tool_app_uic_%RANDOM%%RANDOM%.log"
set "HAS_REASON="

echo   [%TOTAL_COUNT%] %~nx1
"%UIC_CMD%" "%SRC_FILE%" -o "%DST_FILE%" > "%TMP_LOG%" 2>&1
if errorlevel 1 (
    set /a FAIL_COUNT+=1
    >> "%FAIL_LOG%" echo - %~nx1
    >> "%FAIL_LOG%" echo   Source: %SRC_FILE%
    >> "%FAIL_LOG%" echo   Output: %DST_FILE%
    for /f "usebackq delims=" %%L in ("%TMP_LOG%") do (
        if not defined HAS_REASON (
            >> "%FAIL_LOG%" echo   Reason:
            set "HAS_REASON=1"
        )
        >> "%FAIL_LOG%" echo     %%L
    )
    if not defined HAS_REASON (
        >> "%FAIL_LOG%" echo   Reason: ^(no error output^)
    )
    >> "%FAIL_LOG%" echo.
    echo      failed
    del /q "%TMP_LOG%" >nul 2>nul
    goto :eof
)

set /a SUCCESS_COUNT+=1
echo      success
del /q "%TMP_LOG%" >nul 2>nul
goto :eof
