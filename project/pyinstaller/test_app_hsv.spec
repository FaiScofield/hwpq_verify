# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for the HSV test application (script/verify_tool_app/test_app_hsv.py)
# Build (recommended):
#   project\build_pyinstaller.cmd test_app_hsv
# Or directly:
#   pyinstaller --noconfirm --distpath output/pyinstaller/dist --workpath output/pyinstaller/build project/pyinstaller/test_app_hsv.spec
# Output: output/pyinstaller/dist/test_app_hsv/test_app_hsv.exe (onedir)

import os

# 仓库根目录由 spec 文件自身位置（SPECPATH）推导，全部路径用相对仓库的
# 相对路径拼接，不依赖执行 pyinstaller 时的当前工作目录，可跨机器构建。
_SPEC_DIR = os.path.abspath(SPECPATH)
_REPO_ROOT = os.path.abspath(os.path.join(_SPEC_DIR, '..', '..'))
_APP_MAIN = os.path.join(_REPO_ROOT, 'script', 'verify_tool_app', 'test_app_hsv.py')

# script/csc 必须加入 pathex：run_csc.py 用 sys.path.insert + 平级导入
# （from get_csc_coef_hsv import ...），PyInstaller 分析时不执行该插入，
# 需显式提供搜索路径才能收集 get_csc_coefs / get_csc_coef_hsv。
_PATHEX = [
    os.path.join(_REPO_ROOT, 'script', 'verify_tool_app'),
    os.path.join(_REPO_ROOT, 'script', 'csc'),
    _REPO_ROOT,
]


a = Analysis(
    [_APP_MAIN],
    pathex=_PATHEX,
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
