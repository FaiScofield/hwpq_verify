# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for the HSV test application (script/verify_tool_app/test_app_hsv.py)
# Build (recommended):
#   project\build_pyinstaller.cmd test_app_hsv
# Or directly:
#   pyinstaller --noconfirm --distpath output/pyinstaller/dist --workpath output/pyinstaller/build project/pyinstaller/test_app_hsv.spec
# Output: output/pyinstaller/dist/test_app_hsv/test_app_hsv.exe (onedir)


a = Analysis(
    ['G:\\Codes\\gerrit_projects\\hwpq_verify\\script\\verify_tool_app\\test_app_hsv.py'],
    # script/csc 必须加入 pathex：run_csc.py 用 sys.path.insert + 平级导入
    # （from get_csc_coef_hsv import ...），PyInstaller 分析时不执行该插入，
    # 需显式提供搜索路径才能收集 get_csc_coefs / get_csc_coef_hsv。
    pathex=['G:\\Codes\\gerrit_projects\\hwpq_verify\\script\\verify_tool_app',
            'G:\\Codes\\gerrit_projects\\hwpq_verify\\script\\csc',
            'G:\\Codes\\gerrit_projects\\hwpq_verify'],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='test_app_hsv',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='test_app_hsv',
)
