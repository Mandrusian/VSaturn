# vsaturn.spec (NO bundle ffmpeg)


block_cipher = None


a = Analysis(
    ['vsaturn_downloader_pyqt.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('tsmandrusia.jpg', '.'),
        ('vsaturn.jpg', '.')
    ],
    hiddenimports=[
        'yt_dlp',
        'yt_dlp.extractor',
        'yt_dlp.postprocessor',
        'yt_dlp.compat',
        'yt_dlp.downloader',
        'yt_dlp.utils',
        'yt_dlp.version',
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
    name='VSaturn',
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
)

app = BUNDLE(
    exe,
    name='VSaturn.app',
    icon='app_icon.icns',
    bundle_identifier='com.yourcompany.vsaturn',
    info_plist={
        'NSHumanReadableCopyright': '(no copyright)',
        'CFBundleDisplayName': 'VSaturn',
        'CFBundleGetInfoString': 'VSaturn V2.0 - Made By Mandrusia',
        'CFBundleVersion': '2.0.0',
        'CFBundleShortVersionString': '2.0',
    }
)
