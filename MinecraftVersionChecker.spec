# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['combined_checker.py'],
    pathex=[],
    binaries=[],
    datas=[('version_info.txt', '.')],
    hiddenimports=['os', 'sys', 'hashlib', 'json', 'zipfile', 'datetime', 'pathlib', 'time', 'collections'],
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
    a.binaries,
    a.datas,
    [],
    name='MinecraftVersionChecker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=['vcruntime140.dll'],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=True,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.txt',
    icon=['icon.ico'],
)
