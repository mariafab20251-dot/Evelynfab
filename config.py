"""
Configuration Management for YouTube Video Automation
Supports environment variables and cross-platform paths
"""

import os
import sys
from pathlib import Path


class Config:
    """Centralized configuration with environment variable support"""

    def __init__(self):
        """Initialize configuration with sensible defaults"""

        # ============================================
        # PROJECT ROOT
        # ============================================
        self.PROJECT_ROOT = Path(__file__).parent.absolute()

        # ============================================
        # VIDEO PROCESSING PATHS
        # ============================================
        # Use environment variables if set, otherwise use defaults

        # Source videos folder
        self.VIDEO_FOLDER = Path(
            os.getenv('VIDEO_SOURCE_FOLDER',
                     self.PROJECT_ROOT / 'SourceVideosToEdit')
        )

        # Quotes file
        self.QUOTES_FILE = Path(
            os.getenv('QUOTES_FILE',
                     self.PROJECT_ROOT / 'Quotes.txt')
        )

        # Output folder for processed videos
        self.OUTPUT_FOLDER = Path(
            os.getenv('OUTPUT_FOLDER',
                     self.PROJECT_ROOT / 'FinalVideos')
        )

        # ============================================
        # UPLOAD PATHS
        # ============================================
        self.VIDEOS_UPLOAD_FOLDER = Path(
            os.getenv('UPLOAD_FOLDER',
                     self.OUTPUT_FOLDER)  # Default: same as output folder
        )

        self.UPLOADED_FOLDER = self.VIDEOS_UPLOAD_FOLDER / 'Uploaded'
        self.FAILED_FOLDER = self.VIDEOS_UPLOAD_FOLDER / 'Failed'

        # ============================================
        # CREDENTIALS
        # ============================================
        self.CREDENTIALS_FOLDER = Path(
            os.getenv('CREDENTIALS_FOLDER',
                     self.PROJECT_ROOT / 'youtube_credentials')
        )

        # ============================================
        # FONTS
        # ============================================
        # Platform-specific font folders
        if sys.platform == 'win32':
            self.SYSTEM_FONTS_FOLDER = Path(r'C:\Windows\Fonts')
        elif sys.platform == 'darwin':  # macOS
            self.SYSTEM_FONTS_FOLDER = Path('/Library/Fonts')
        else:  # Linux
            self.SYSTEM_FONTS_FOLDER = Path('/usr/share/fonts')

        # Custom fonts folder (project-specific)
        self.PROJECT_FONTS_FOLDER = self.PROJECT_ROOT / 'fonts'

        # Emoji font (bundled with project)
        self.EMOJI_FONT = self.PROJECT_ROOT / 'NotoColorEmoji.ttf'

        # ============================================
        # SETTINGS FILES
        # ============================================
        self.OVERLAY_SETTINGS = self.PROJECT_ROOT / 'overlay_settings.json'
        self.UPLOAD_LOG = self.VIDEOS_UPLOAD_FOLDER / 'upload_log.json'
        self.PROCESSING_LOG = self.OUTPUT_FOLDER / 'processing_log.json'

        # ============================================
        # UPLOAD SETTINGS
        # ============================================
        self.UPLOAD_INTERVAL = int(os.getenv('UPLOAD_INTERVAL', 300))  # 5 minutes default

        # ============================================
        # RETRY SETTINGS
        # ============================================
        self.MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
        self.RETRY_DELAY = int(os.getenv('RETRY_DELAY', 5))  # seconds

        # ============================================
        # CREATE REQUIRED FOLDERS
        # ============================================
        self._create_folders()

    def _create_folders(self):
        """Create all required folders if they don't exist"""
        folders = [
            self.VIDEO_FOLDER,
            self.OUTPUT_FOLDER,
            self.UPLOADED_FOLDER,
            self.FAILED_FOLDER,
            self.CREDENTIALS_FOLDER,
            self.PROJECT_FONTS_FOLDER,
        ]

        for folder in folders:
            try:
                folder.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                print(f"⚠ Warning: Could not create folder {folder}: {e}")

    def validate(self):
        """Validate configuration and show warnings for missing items"""
        issues = []

        # Check critical folders exist
        if not self.VIDEO_FOLDER.exists():
            issues.append(f"Video source folder not found: {self.VIDEO_FOLDER}")

        if not self.QUOTES_FILE.exists():
            issues.append(f"Quotes file not found: {self.QUOTES_FILE}")

        # Check system fonts folder
        if not self.SYSTEM_FONTS_FOLDER.exists():
            issues.append(f"System fonts folder not found: {self.SYSTEM_FONTS_FOLDER}")

        # Check emoji font
        if not self.EMOJI_FONT.exists():
            issues.append(f"Emoji font not found: {self.EMOJI_FONT}")

        return issues

    def print_config(self):
        """Print current configuration"""
        print("\n" + "="*70)
        print("CONFIGURATION")
        print("="*70)
        print(f"Project Root: {self.PROJECT_ROOT}")
        print(f"\nVideo Processing:")
        print(f"  Source Videos: {self.VIDEO_FOLDER}")
        print(f"  Quotes File: {self.QUOTES_FILE}")
        print(f"  Output Folder: {self.OUTPUT_FOLDER}")
        print(f"\nUpload:")
        print(f"  Upload Folder: {self.VIDEOS_UPLOAD_FOLDER}")
        print(f"  Uploaded Archive: {self.UPLOADED_FOLDER}")
        print(f"  Failed Archive: {self.FAILED_FOLDER}")
        print(f"\nCredentials:")
        print(f"  Folder: {self.CREDENTIALS_FOLDER}")
        print(f"\nFonts:")
        print(f"  System Fonts: {self.SYSTEM_FONTS_FOLDER}")
        print(f"  Project Fonts: {self.PROJECT_FONTS_FOLDER}")
        print(f"  Emoji Font: {self.EMOJI_FONT}")
        print("="*70 + "\n")

        # Show validation issues
        issues = self.validate()
        if issues:
            print("⚠ Configuration Warnings:")
            for issue in issues:
                print(f"  - {issue}")
            print()


# ============================================
# GLOBAL CONFIG INSTANCE
# ============================================
config = Config()


# ============================================
# EXAMPLE: How to use environment variables
# ============================================
"""
Set environment variables before running the script:

Windows (Command Prompt):
    set VIDEO_SOURCE_FOLDER=E:\\MyVideos
    set QUOTES_FILE=E:\\MyQuotes.txt
    set OUTPUT_FOLDER=D:\\Output
    python youtube_video_automation.py

Windows (PowerShell):
    $env:VIDEO_SOURCE_FOLDER="E:\\MyVideos"
    $env:QUOTES_FILE="E:\\MyQuotes.txt"
    $env:OUTPUT_FOLDER="D:\\Output"
    python youtube_video_automation.py

Linux/macOS:
    export VIDEO_SOURCE_FOLDER="/home/user/videos"
    export QUOTES_FILE="/home/user/quotes.txt"
    export OUTPUT_FOLDER="/home/user/output"
    python3 youtube_video_automation.py

Or create a .env file and load it with python-dotenv package.
"""


if __name__ == "__main__":
    # Test configuration
    config.print_config()
