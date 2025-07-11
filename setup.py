# setup.py (Revised Attempt with more comprehensive includes)

from setuptools import setup

APP = ['youtube_downloader.py']

# Data files (if any non-code files need to be copied, not directly relevant for the current ModuleNotFoundError)
DATA_FILES = []

# Options for py2app
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'app_icon.icns', # Optional: Path to your application icon (.icns file)
    'plist': {
        'CFBundleName': 'YouTube Downloader',
        'CFBundleDisplayName': 'YouTube Downloader',
        'CFBundleGetInfoString': 'YouTube Video Downloader',
        'CFBundleIdentifier': 'com.yourcompany.youtubedownloader',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0',
        'NSHumanReadableCopyright': '© 2025 Your Name/Company',
    },
    # *** IMPORTANT: More aggressive inclusions for yt-dlp ***
    'includes': [
        'yt_dlp',
        'yt_dlp.extractor',       # Crucial for recognizing video sites
        'yt_dlp.postprocessor',   # Crucial for post-download processing (e.g., converting formats)
        'yt_dlp.compat',          # Compatibility layer
        'yt_dlp.downloader',      # Core download logic
        'yt_dlp.utils',           # Utility functions
        'yt_dlp.version',         # Version information
        # Add any other top-level modules if future errors appear
    ],
    # You can keep 'packages': ['yt_dlp'] or remove it; 'includes' is often more direct for this type of problem.
    # For now, let's rely on 'includes' for yt_dlp.
    # 'packages': ['yt_dlp'],
    'excludes': [], # Do not exclude anything unless you know it's not needed.
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)