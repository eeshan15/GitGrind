# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for GitGrind.

Use this when you want to tweak the build by hand:

    pyinstaller gitgrind.spec --noconfirm

tools/build_exe.py generates an equivalent build without needing this file, so
reach for that first. This spec exists for the cases where you need to add an
icon, sign the binary, or exclude something.

Note what is NOT bundled: data/gitgrind.db and papers/. The database has to stay
outside the executable or a rebuild would replace your history with an empty one.
"""

import os

block_cipher = None
ROOT = os.path.abspath(os.getcwd())
ICON = os.path.join(ROOT, 'static', 'icon.ico')
if not os.path.isfile(ICON):
    ICON = None
a = Analysis(
    ['app.py'],
    pathex=[ROOT],
    binaries=[],
    datas=[
        ('static', 'static'),      # entire UI: html, css, js
        ('content', 'content'),    # syllabus, targets, lexicons, question bank
    ],
    hiddenimports=['demo_data'],   # only reached via --demo, so the analyser misses it
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        # Nothing in the app needs these; excluding them keeps the binary small.
        'tkinter', 'unittest', 'pydoc_data', 'test',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GitGrind',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,        # keep the console: it prints the URL and any bank warnings
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon=ICON,
)
