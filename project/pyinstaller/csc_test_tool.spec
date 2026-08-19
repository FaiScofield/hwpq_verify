# -*- mode: python ; coding: utf-8 -*-

import os

# 仓库根目录由 spec 文件自身位置（SPECPATH）推导，全部路径用相对仓库的
# 相对路径拼接，不依赖执行 pyinstaller 时的当前工作目录，可跨机器构建。
_SPEC_DIR = os.path.abspath(SPECPATH)
_REPO_ROOT = os.path.abspath(os.path.join(_SPEC_DIR, '..', '..'))
_APP_MAIN = os.path.join(_REPO_ROOT, 'script', 'csc', 'run_csc_ui.py')
_FONT = os.path.join(_REPO_ROOT, 'data', 'fonts', 'NotoSans-Regular.ttf')


a = Analysis(
    [_APP_MAIN],
    pathex=[],
    binaries=[],
    datas=[(_FONT, 'assets/fonts')],
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
    name='csc_test_tool',
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
    name='csc_test_tool',
)
