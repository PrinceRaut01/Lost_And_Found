# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\princ\\Downloads\\Lost_and_Found_Desk-App\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\princ\\Downloads\\Lost_and_Found_Desk-App\\assets\\icon.ico', 'assets')],
    hiddenimports=['admin_page', 'user_page'],
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
    name='LostAndFoundDesk',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='C:\\Users\\princ\\Downloads\\Lost_and_Found_Desk-App\\version_info.txt',
    icon=['C:\\Users\\princ\\Downloads\\Lost_and_Found_Desk-App\\assets\\icon.ico'],
)
