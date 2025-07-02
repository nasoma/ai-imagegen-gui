# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['gui.py'],
    pathex=[],
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
    a.binaries,
    a.datas,
    [],
    name='AI Image Generator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,  # Needed for drag-and-drop to work on macOS
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='MyIcon.icns',  # This should be a string, not a list
)

app = BUNDLE(
    exe,
    name='AI Image Generator.app',
    icon='MyIcon.icns',
    bundle_identifier='com.yourname.aiimagegenerator',
)