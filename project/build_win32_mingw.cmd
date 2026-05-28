@echo off
::
:: Usage:
::   make-mingw.bat [-t debug|release] [-p rk3572] [-c] [-e] [-h]
::
:: Options:
::   -t, --type    : Build type (default: debug, options: debug, release)
::   -p, --platform: Platform type (default: RK3572)
::   -c, --clean   : Clean build artifacts before build
::   -e, --export  : Export compile_commands.json to .vscode/
::   -h, --help    : Show help information

:: Directory vars
set SCRIPT_DIR=%~dp0
if "%SCRIPT_DIR:~-1%"=="\" set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%
set PROJECT_ROOT=%SCRIPT_DIR%\..

:: NOTE: change the mingw64 directory to your own. :: use a version such as: 'x86_64-8.1.0-release-posix-seh-rt_v6'
:: You might check the target compiler by running `D:/mingw64/bin/gcc.exe -v` Target: x86_64-w64-mingw32
set MINGW_DIR=D:/mingw64
SET RK_SOC=RK3572
set BUILD_TYPE=debug
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
        set BUILD_TYPE=release
        @echo get BUILD_TYPE from cmd: %~2
    ) else (
        set BUILD_TYPE=debug
        @echo get BUILD_TYPE from cmd: %~2
    )
    shift
    shift
    goto parse_args
)
if /i "%~1" == "--type" (
    if /i "%~2" == "release" (
        set BUILD_TYPE=release
        @echo get BUILD_TYPE from cmd: %~2
    ) else (
        set BUILD_TYPE=debug
        @echo get BUILD_TYPE from cmd: %~2
    )
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


set BUILD_DIR=%SCRIPT_DIR%\build_mingw_%BUILD_TYPE%
echo .
echo Mingw dir: %MINGW_DIR%
echo Script dir: %SCRIPT_DIR%
echo Project root: %PROJECT_ROOT%
echo Build type: %BUILD_TYPE%
echo Build directory: %BUILD_DIR%
echo Clean build cache: %CLEAN_BUILD%
echo.

if not exist "%MINGW_DIR%\bin\gcc.exe" (
    echo Error: MinGW not found at %MINGW_DIR%
    echo Please set MINGW_DIR correctly in this script.
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
    -DCMAKE_C_COMPILER="%MINGW_DIR%/bin/gcc.exe" ^
    -DCMAKE_CXX_COMPILER="%MINGW_DIR%/bin/g++.exe" ^
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
echo   make-mingw.bat - Build Script
echo ========================================
echo.
echo Usage:
echo   make-mingw.bat [-t debug^|release] [-p rk3572] [-c] [-e] [-h]
echo.
echo Options:
echo   -t, --type     ^<type^>      Build type (default: debug) Options: debug, release
echo   -p, --platform ^<platform^>  Platform type (default: RK3572) Options: rk3572
echo   -c, --clean    Removes entire build directory before build
echo   -e, --export   Export compile_commands.json to .vscode/
echo   -h, --help     Show this help information and exit
echo.
echo ========================================
exit /b 0
