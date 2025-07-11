# vsaturn.spec (for PyQt6 GUI app)

# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(
    ['vsaturn_downloader_pyqt.py'], # IMPORTANT: Changed to the new PyQt GUI script name
    pathex=[],
    binaries=[],
    datas=[
        ('tsmandrusia.jpg', '.'), # Copy to Contents/MacOS/
        ('vsaturn.jpg', '.')      # Copy to Contents/MacOS/
    ],
    hiddenimports=[
        'yt_dlp',
        'yt_dlp.extractor',
        'yt_dlp.postprocessor',
        'yt_dlp.compat',
        'yt_dlp.downloader',
        'yt_dlp.utils',
        'yt_dlp.version',
        # PyInstaller usually finds PyQt6 dependencies, but if you hit errors,
        # you might need to add specific Qt modules here, e.g.:
        # 'PyQt6.QtCore',
        # 'PyQt6.QtWidgets',
        # 'PyQt6.QtGui',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VSaturn', # Updated app name for the executable
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False, # Set to False for a GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# This part is crucial for a proper macOS .app bundle with an icon.
# You need an .icns file for your icon (e.g., 'app_icon.icns' in your project folder)
# The user specified they already have the .icns file.
app = BUNDLE(
    exe,
    name='VSaturn.app', # The final .app bundle name
    icon='app_icon.icns', # Path to your .icns file (e.g., in the same directory as spec)
    bundle_identifier='com.yourcompany.vsaturn', # IMPORTANT: Updated unique identifier
    info_plist={
        'NSHumanReadableCopyright': '(no copyright)', # Updated to "no copyright"
        'CFBundleDisplayName': 'VSaturn', # Updated display name
        'CFBundleGetInfoString': 'VSaturn V2.0 - Made By Mandrusia', # Updated info string
        'CFBundleVersion': '2.0.0', # Updated version
        'CFBundleShortVersionString': '2.0', # Updated short version
        # You can add more plist entries here, like LSMinimumSystemVersion for macOS version
        # 'LSMinimumSystemVersion': '10.15.0', # Example for macOS Catalina or later
    }
)