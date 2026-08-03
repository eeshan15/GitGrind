# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\ASUS\\OneDrive\\Desktop\\GATE\\gitgrind\\app.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\ASUS\\OneDrive\\Desktop\\GATE\\gitgrind\\static', 'static'), ('C:\\Users\\ASUS\\OneDrive\\Desktop\\GATE\\gitgrind\\content', 'content')],
    hiddenimports=['demo_data', 'pystray', 'pystray._win32', 'PIL', 'PIL.Image', 'PIL.ImageDraw'],
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
    name='GitGrind',
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
    icon=['C:\\Users\\ASUS\\OneDrive\\Desktop\\GATE\\gitgrind\\static\\icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GitGrind',
)
