# vsaturn_downloader_pyqt.py

import sys
import os
import threading
import queue
import webbrowser # For opening Discord link

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QFileDialog, QMessageBox, QStackedWidget,
    QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QEasingCurve, QPropertyAnimation, QUrl, QSize
from PyQt6.QtGui import QDesktopServices, QPixmap, QPainter, QPainterPath # Removed QBrush, QColor as not directly used in this snippet


import yt_dlp

# --- Global Qt Style Sheet (QSS) for a sleek, dark, 'liquid-like' aesthetic ---
GLOBAL_QSS = """
/* Base Widget Styling */
QWidget {
    background-color: rgba(35, 35, 45, 0.9); /* Dark background with slight transparency */
    color: #E0E0E0; /* Light text color */
    font-family: 'Inter', 'Segoe UI', 'Arial', sans-serif; /* Using Inter font */
    font-size: 14px;
    border-radius: 10px; /* Overall rounded corners for the main window */
}

/* Main Window Specifics (if needed, otherwise QWidget applies) */
QMainWindow {
    border-radius: 10px;
}

/* Labels */
QLabel {
    color: #C0C0C0;
    margin-bottom: 5px;
}

/* Line Edits (Input Fields) */
QLineEdit {
    background-color: rgba(60, 60, 70, 0.7); /* Darker input with transparency */
    border: 1px solid rgba(100, 100, 120, 0.5); /* Subtle border */
    border-radius: 8px; /* Rounded corners */
    padding: 8px 12px;
    color: #FFFFFF;
    selection-background-color: #0078D7;
}

QLineEdit:focus {
    border: 1px solid #00A0E0; /* Highlight on focus */
}

/* Push Buttons */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 rgba(0, 150, 200, 0.8), /* Top gradient color with transparency */
                                stop:1 rgba(0, 100, 150, 0.8)); /* Bottom gradient color with transparency */
    border: none;
    border-radius: 10px; /* More rounded corners for buttons */
    padding: 10px 20px;
    color: #FFFFFF;
    font-weight: bold;
    text-transform: uppercase;
    min-height: 35px;
    /* Removed: transition: all 0.2s ease-in-out; */ /* QSS does not support 'transition' directly */
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 rgba(0, 170, 220, 0.9),
                                stop:1 rgba(0, 120, 170, 0.9));
}

QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 rgba(0, 80, 130, 0.8),
                                stop:1 rgba(0, 50, 100, 0.8));
    border: 1px solid rgba(0, 40, 80, 0.5);
}

QPushButton:disabled {
    background-color: rgba(80, 80, 80, 0.5);
    color: rgba(200, 200, 200, 0.5);
}

/* Text Edit (Log Area) */
QTextEdit {
    background-color: rgba(30, 30, 40, 0.7); /* Even darker background for log area */
    border: 1px solid rgba(50, 50, 60, 0.5);
    border-radius: 8px;
    padding: 10px;
    color: #F0F0F0;
}

/* Scroll Bars (for QTextEdit) */
QScrollBar:vertical {
    border: none;
    background: rgba(50, 50, 60, 0.5);
    width: 10px;
    margin: 0px 0px 0px 0px;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background: rgba(0, 150, 200, 0.7);
    border-radius: 5px;
    min-height: 20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

/* Hamburger Menu Frame */
#HamburgerMenu {
    background-color: rgba(25, 25, 35, 0.95); /* Slightly darker, more opaque for menu */
    border-right: 1px solid rgba(100, 100, 120, 0.2);
    border-radius: 10px 0 0 10px; /* Rounded on the left side only */
    padding: 10px;
}

#HamburgerMenu QPushButton {
    background: transparent;
    border: none;
    color: #E0E0E0;
    text-align: left;
    padding: 15px 10px;
    border-radius: 8px;
    font-weight: normal;
    text-transform: none;
}

#HamburgerMenu QPushButton:hover {
    background-color: rgba(0, 150, 200, 0.2);
    color: #FFFFFF;
}

#HamburgerMenu QPushButton:checked { /* For selected page button */
    background-color: rgba(0, 150, 200, 0.4);
    color: #FFFFFF;
    font-weight: bold;
}

/* Hamburger Icon Button */
#HamburgerIconButton {
    background: transparent;
    border: none;
    color: #E0E0E0;
    font-size: 24px; /* Larger icon */
    padding: 5px;
    border-radius: 5px;
}
#HamburgerIconButton:hover {
    background-color: rgba(100, 100, 120, 0.2);
}

/* Stacked Widget (Content Area) */
QStackedWidget {
    background-color: transparent; /* Let the main window background show through */
}

/* Page Frames (inside Stacked Widget) */
QFrame#ContentPage {
    background-color: transparent; /* Pages themselves are transparent */
    padding: 10px;
}

/* Specific styling for image containers to round them */
#RoundedImageFrame {
    background-color: transparent; /* Inherit parent background or ensure transparency */
    border-radius: 20px; /* Adjust this value for desired roundness */
    /* Removed: overflow: hidden; */ /* QSS does not support 'overflow' directly for clipping */
    /* No border or padding here, image itself will be painted */
}

/* Styling for the App Name in Header */
#AppNameLabel {
    font-size: 20px;
    font-weight: bold;
    color: #FFFFFF;
    margin-left: 10px;
}
"""

# --- Download Worker Thread ---
class DownloadThread(QThread):
    progress_signal = pyqtSignal(str, str) # message, type (info, error, success)
    finished_signal = pyqtSignal(str, str) # message, type (info, error, success)

    def __init__(self, url, output_path, platform_name):
        super().__init__()
        self.url = url
        self.output_path = output_path
        self.platform_name = platform_name # For potential platform-specific handling

    def run(self):
        try:
            # Ensure the output directory exists
            if not os.path.exists(self.output_path):
                os.makedirs(self.output_path)
                self.progress_signal.emit(f"Created output directory: {self.output_path}", 'info')

            # yt-dlp options - it intelligently handles different platforms based on URL
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', # Default for video
                'outtmpl': os.path.join(self.output_path, '%(title)s.%(ext)s'),
                'noplaylist': True,
                'progress_hooks': [self._progress_hook],
                'quiet': True, # Keep yt-dlp quiet for GUI, use hook for messages
                'no_warnings': False,
                'ignoreerrors': True,
            }

            # Specific options for audio-only (Soundcloud)
            if self.platform_name == "Soundcloud":
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
                # Ensure ffmpeg is available if converting to mp3
                # For bundled apps, ffmpeg might need to be explicitly included or pre-installed by user.
                # This script assumes ffmpeg is accessible in the system PATH or bundled by PyInstaller.

            self.progress_signal.emit(f"Attempting to download from {self.platform_name}: {self.url}", 'info')
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(self.url, download=True)
                video_title = info_dict.get('title', 'Unknown Title')
                video_ext = info_dict.get('ext', 'mp4') # Will be 'mp3' for soundcloud if postprocessed
                self.finished_signal.emit(f"Successfully downloaded: {video_title}.{video_ext}", 'success')
                self.finished_signal.emit(f"Saved to: {self.output_path}", 'success')

        except yt_dlp.utils.DownloadError as e:
            self.error_signal.emit(f"Download Error: {e}")
        except Exception as e:
            self.error_signal.emit(f"An unexpected error occurred: {e}")

    def _progress_hook(self, d):
        """Hook for yt-dlp to update GUI with progress."""
        if d['status'] == 'downloading':
            p = d.get('_percent_str', f"{d.get('downloaded_bytes', 0) / d.get('total_bytes', 1) * 100:.1f}%")
            s = d.get('_speed_str', 'N/A')
            e = d.get('_eta_str', 'N/A')
            self.progress_signal.emit(f"Downloading: {p} at {s} ETA {e}", 'info')
        elif d['status'] == 'finished':
            filename = d.get('filename', 'Unknown File')
            self.progress_signal.emit(f"Finished processing: {filename}", 'success')
        elif d['status'] == 'error':
            self.progress_signal.emit(f"Error during processing: {d.get('error', 'Unknown Error')}", 'error')


# --- Page Widget Template ---
class DownloaderPage(QFrame):
    def __init__(self, platform_name, parent=None):
        super().__init__(parent)
        self.setObjectName("ContentPage") # For QSS targeting
        self.platform_name = platform_name
        self.download_thread = None # To hold the reference to the download thread

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Page Title
        title_label = QLabel(f"{self.platform_name} Downloader")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #00A0E0;")
        layout.addWidget(title_label)

        # URL Input
        url_label = QLabel("Video/Audio URL:")
        layout.addWidget(url_label)

        self.url_entry = QLineEdit()
        self.url_entry.setPlaceholderText(f"Paste {self.platform_name} URL here...")
        self.url_entry.returnPressed.connect(self.start_download)
        layout.addWidget(self.url_entry)

        # Output Directory Selection
        self.output_dir = os.path.join(os.path.expanduser("~"), "Movies", "VSaturn_Downloads", self.platform_name)
        # Ensure default directory exists on startup
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        dir_layout = QHBoxLayout()
        output_label = QLabel("Save to:")
        dir_layout.addWidget(output_label)

        self.output_entry = QLineEdit(self.output_dir)
        self.output_entry.setReadOnly(True)
        dir_layout.addWidget(self.output_entry)

        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_output_directory)
        dir_layout.addWidget(browse_button)

        layout.addLayout(dir_layout)

        # Download Button
        self.download_button = QPushButton(f"Download {self.platform_name}")
        self.download_button.clicked.connect(self.start_download)
        layout.addWidget(self.download_button)

        # Log Display
        log_label = QLabel("Download Log:")
        layout.addWidget(log_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        layout.addStretch(1) # Pushes content to the top

        self.setLayout(layout)

    def browse_output_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Choose Output Directory", self.output_dir)
        if directory:
            self.output_dir = directory
            self.output_entry.setText(self.output_dir)

    def log_message(self, message, message_type='info'):
        color_map = {
            'info': '#6BEBFF',
            'error': '#FF6B6B',
            'success': '#6BFF6B'
        }
        color = color_map.get(message_type, '#C0C0C0') # Default light gray

        self.log_text.append(f"<span style='color:{color};'>{message}</span>")
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

    def start_download(self):
        url = self.url_entry.text().strip()
        
        if not url:
            QMessageBox.warning(self, "Input Error", "Please enter a URL.")
            self.log_message("Error: No URL provided.", 'error')
            return

        self.log_text.clear() # Clear previous log
        self.log_message("Starting download...", 'info')
        self.download_button.setEnabled(False) # Disable button during download

        # Create and start the download thread
        self.download_thread = DownloadThread(url, self.output_dir, self.platform_name)
        self.download_thread.progress_signal.connect(lambda msg, type: self.log_message(msg, type))
        self.download_thread.finished_signal.connect(lambda msg, type: self.download_finished(msg, type))
        self.download_thread.error_signal.connect(lambda msg, type: self.download_finished(msg, type))
        self.download_thread.start()

    def download_finished(self, message, message_type):
        self.log_message(message, message_type)
        self.download_button.setEnabled(True) # Re-enable button

        if message_type == 'error':
            QMessageBox.critical(self, "Download Failed", message)
        elif message_type == 'success':
            QMessageBox.information(self, "Download Complete", "Video/Audio downloaded successfully!")


# --- Generic Image Display Frame with Rounding ---
class RoundedImageFrame(QFrame):
    def __init__(self, image_path, size=QSize(100, 100), radius=20, parent=None):
        super().__init__(parent)
        self.setObjectName("RoundedImageFrame") # For QSS targeting
        self.setFixedSize(size)
        self.radius = radius
        
        self.pixmap = QPixmap(image_path)
        if self.pixmap.isNull():
            # Fallback for when running directly from source or bundled incorrectly
            # Try to get path relative to script if not found directly
            script_dir = os.path.dirname(os.path.abspath(__file__))
            fallback_path = os.path.join(script_dir, image_path)
            self.pixmap = QPixmap(fallback_path)
            if self.pixmap.isNull():
                print(f"Warning: Could not load image from {image_path} or {fallback_path}")
                # Create a placeholder if image still not found
                self.pixmap = QPixmap(size)
                self.pixmap.fill(Qt.GlobalColor.darkGray)


        # QSS for border-radius on the frame. Clipping is done in paintEvent.
        self.setStyleSheet(f"#RoundedImageFrame {{ border-radius: {self.radius}px; }}")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        path = QPainterPath()
        # FIX: Use toRectF() to convert QRect to QRectF for addRoundedRect
        path.addRoundedRect(self.rect().toRectF(), self.radius, self.radius)
        painter.setClipPath(path)

        # Draw the scaled pixmap
        scaled_pixmap = self.pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
        
        # Center the scaled pixmap within the frame
        x_offset = (self.width() - scaled_pixmap.width()) / 2
        y_offset = (self.height() - scaled_pixmap.height()) / 2
        painter.drawPixmap(int(x_offset), int(y_offset), scaled_pixmap)


# --- Other Projects Page ---
class OtherProjectsPage(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ContentPage")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Image at the top (tsmandrusia.jpg)
        image_frame = RoundedImageFrame('tsmandrusia.jpg', size=QSize(200, 200), radius=20)
        layout.addWidget(image_frame, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)

        title_label = QLabel("Other Projects by Mandrusia")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #00A0E0;")
        layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(15)

        # Mandrusia GitHub Pages Link
        github_label = QLabel('<a href="https://mandrusian.github.io/Mandrusia" style="color: #6BEBFF; text-decoration: underline; font-size: 16px;">mandrusian.github.io/Mandrusia</a>')
        github_label.setOpenExternalLinks(True)
        github_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        layout.addWidget(github_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(10)

        # TikTok Links
        tiktok_label = QLabel("Connect on TikTok:")
        tiktok_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(tiktok_label, alignment=Qt.AlignmentFlag.AlignCenter)

        tiktok_tech_link = QLabel('<a href="https://www.tiktok.com/@mandrusiatech" style="color: #6BEBFF; text-decoration: underline;">@mandrusiatech</a>')
        tiktok_tech_link.setOpenExternalLinks(True)
        tiktok_tech_link.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        layout.addWidget(tiktok_tech_link, alignment=Qt.AlignmentFlag.AlignCenter)

        tiktok_canada_link = QLabel('<a href="https://www.tiktok.com/@mandrusia.canada" style="color: #6BEBFF; text-decoration: underline;">@mandrusia.canada</a>')
        tiktok_canada_link.setOpenExternalLinks(True)
        tiktok_canada_link.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        layout.addWidget(tiktok_canada_link, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch(1) # Push content to top

        self.setLayout(layout)

# --- About Page ---
class AboutPage(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ContentPage")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Image at the top (vsaturn.jpg)
        image_frame = RoundedImageFrame('vsaturn.jpg', size=QSize(150, 150), radius=25) # Slightly larger and more rounded
        layout.addWidget(image_frame, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)

        # App Name
        app_name_label = QLabel("VSaturn")
        app_name_label.setStyleSheet("font-size: 30px; font-weight: bold; color: #FFFFFF; margin-bottom: 5px;")
        layout.addWidget(app_name_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Version
        version_label = QLabel("Version 2.1 | Fix 1")
        version_label.setStyleSheet("font-size: 18px; color: #C0C0C0;")
        layout.addWidget(version_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # License
        license_label = QLabel("MIT License")
        license_label.setStyleSheet("font-size: 16px; color: #909090;")
        layout.addWidget(license_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Copyright/Made By
        made_by_label = QLabel("Made By Mandrusia on <a href='https://mandrusian.github.io' style='color: #6BEBFF; text-decoration: underline;'>mandrusian.github.io</a>")
        made_by_label.setOpenExternalLinks(True)
        made_by_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        made_by_label.setStyleSheet("font-size: 16px; color: #C0C0C0;")
        layout.addWidget(made_by_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # No Copyright
        no_copyright_label = QLabel("(no copyright)")
        no_copyright_label.setStyleSheet("font-size: 12px; color: #909090;")
        layout.addWidget(no_copyright_label, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch(1) # Push content to top

        self.setLayout(layout)


# --- Main Application Window ---
class VSaturnApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VSaturn") # Updated window title
        self.setGeometry(100, 100, 1000, 700) # Wider window to accommodate menu
        self.setMinimumSize(800, 500)

        self.apply_stylesheet()
        self.init_ui()

        # Set initial page
        self.show_page(0) # Default to YouTube page

    def apply_stylesheet(self):
        self.setStyleSheet(GLOBAL_QSS)
        # For true background transparency (requires specific OS setup and frameless window)
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        # self.setWindowFlag(Qt.WindowType.FramelessWindowHint)

    def init_ui(self):
        main_layout = QVBoxLayout(self) # Changed to QV for header row
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Header Row (for Hamburger Menu Toggle and App Icon/Name) ---
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(10, 10, 10, 10)
        header_layout.setSpacing(10)

        # Menu Toggle Button (Hamburger Icon)
        self.toggle_button = QPushButton("☰") # Only hamburger icon
        self.toggle_button.setObjectName("HamburgerIconButton")
        self.toggle_button.setFixedSize(40, 40) # Make it square
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(True) # Start open
        self.toggle_button.clicked.connect(self.toggle_menu)
        header_layout.addWidget(self.toggle_button)

        # App Icon in Header (vsaturn.jpg)
        # Use a smaller radius for the header icon to make it more circular/squircle
        header_icon_frame = RoundedImageFrame('vsaturn.jpg', size=QSize(40, 40), radius=10)
        header_layout.addWidget(header_icon_frame)

        # App Name in Header
        app_name_label = QLabel("VSaturn")
        app_name_label.setObjectName("AppNameLabel")
        header_layout.addWidget(app_name_label)

        header_layout.addStretch(1) # Pushes content to the left
        main_layout.addLayout(header_layout)

        # --- Main Content Area (Menu + Stacked Widget) ---
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # --- Hamburger Menu (Left Side) ---
        self.menu_frame = QFrame(self)
        self.menu_frame.setObjectName("HamburgerMenu")
        self.menu_layout = QVBoxLayout(self.menu_frame)
        self.menu_layout.setContentsMargins(10, 20, 10, 10)
        self.menu_layout.setSpacing(10)

        self.menu_buttons_frame = QFrame(self.menu_frame)
        self.menu_buttons_layout = QVBoxLayout(self.menu_buttons_frame)
        self.menu_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.menu_buttons_layout.setSpacing(5)

        # Navigation Buttons
        self.buttons = []
        pages = [
            ("YouTube", DownloaderPage("YouTube")),
            ("TikTok", DownloaderPage("TikTok")),
            ("Soundcloud", DownloaderPage("Soundcloud")),
            ("Instagram", DownloaderPage("Instagram")),
            ("Other Projects", OtherProjectsPage()), # New Page
            ("About", AboutPage()) # New Page
        ]
        
        self.page_widgets = []
        for i, (name, page_widget) in enumerate(pages):
            button = QPushButton(name)
            button.setCheckable(True)
            button.clicked.connect(lambda checked, idx=i: self.show_page(idx))
            self.menu_buttons_layout.addWidget(button)
            self.buttons.append(button)
            self.page_widgets.append(page_widget)


        self.menu_layout.addWidget(self.menu_buttons_frame)
        self.menu_layout.addStretch(1) # Pushes buttons to the top

        # Set initial menu width
        self.menu_width = 200 # Default open width
        self.menu_frame.setFixedWidth(self.menu_width)
        self.menu_buttons_frame.setVisible(True) # Ensure buttons are visible if menu starts open

        content_layout.addWidget(self.menu_frame)

        # --- Content Area (Right Side) ---
        self.stacked_widget = QStackedWidget(self)
        for page_widget in self.page_widgets:
            self.stacked_widget.addWidget(page_widget)
        
        content_layout.addWidget(self.stacked_widget)
        main_layout.addLayout(content_layout) # Add content layout to main layout


    def toggle_menu(self):
        is_checked = self.toggle_button.isChecked()
        target_width = 200 if is_checked else 60 # Expanded vs collapsed width

        # Animate the menu width
        self.animation = QPropertyAnimation(self.menu_frame, b"minimumWidth")
        self.animation.setStartValue(self.menu_frame.width())
        self.animation.setEndValue(target_width)
        self.animation.setDuration(200) # milliseconds
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.finished.connect(lambda: self.menu_buttons_frame.setVisible(is_checked)) # Hide/show buttons after animation
        self.animation.start()

        self.menu_frame.setMinimumWidth(target_width) # Set min width immediately for layout

    def show_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
        # Update button checked state
        for i, button in enumerate(self.buttons):
            button.setChecked(i == index)

        # If menu is collapsed, expand it when a page is selected
        if not self.toggle_button.isChecked():
            self.toggle_button.setChecked(True)
            self.toggle_menu()


def main():
    app = QApplication(sys.argv)
    window = VSaturnApp() # Updated app class name
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()