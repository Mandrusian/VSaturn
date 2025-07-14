# setup.py 
from setuptools import setup

APP = ['youtube_downloader.py']


DATA_FILES = []

# Options for py2app
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'app_icon.icns', 
    'plist': {
        'CFBundleName': 'YouTube Downloader',
        'CFBundleDisplayName': 'YouTube Downloader',
        'CFBundleGetInfoString': 'YouTube Video Downloader',
        'CFBundleIdentifier': 'com.yourcompany.youtubedownloader',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0',
        'NSHumanReadableCopyright': '© 2025 Your Name/Company',
    },
    
    'includes': [
        'yt_dlp',
        'yt_dlp.extractor',       
        'yt_dlp.postprocessor',   
        'yt_dlp.compat',          
        'yt_dlp.downloader',      
        'yt_dlp.utils',           
        'yt_dlp.version',         
        
    ],
   
    'excludes': [], 
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
