# YouTube Video Automation System

A comprehensive Python-based system for automatically processing videos with text overlays and uploading them to multiple YouTube channels.

## 🎯 Features

- **Video Processing**: Add beautiful text overlays to videos with customizable styles
- **GUI Configuration**: Easy-to-use Tkinter interface for customizing overlay settings
- **Multi-Channel Upload**: Automatically upload to 5 YouTube channels with rotation
- **Advanced Effects**: Color grading, vignettes, zoom effects, audio mixing
- **Retry Logic**: Automatic retry with exponential backoff for network failures
- **Error Recovery**: Failed videos moved to dedicated folder for later retry
- **Cross-Platform**: Works on Windows, macOS, and Linux

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Usage](#usage)
5. [Project Structure](#project-structure)
6. [Troubleshooting](#troubleshooting)
7. [Security](#security)

---

## 🔧 Prerequisites

### Required Software

1. **Python 3.8+**
   - Download from: https://www.python.org/downloads/
   - Verify installation: `python --version`

2. **FFmpeg** (Required by MoviePy)
   - **Windows**: Download from https://ffmpeg.org/download.html
   - **Linux**: `sudo apt-get install ffmpeg`
   - **macOS**: `brew install ffmpeg`
   - Verify installation: `ffmpeg -version`

3. **Git** (for cloning the repository)
   - Download from: https://git-scm.com/downloads

### YouTube API Setup

1. **Google Cloud Project**:
   - Go to: https://console.cloud.google.com/
   - Create a new project or select existing one
   - Enable YouTube Data API v3
   - Create OAuth 2.0 credentials (Desktop App)
   - Download `client_secret.json` for each channel

2. **API Quota**:
   - Default quota: 10,000 units/day
   - Each upload costs ~1,600 units
   - Can upload ~6 videos/day per project

---

## 📦 Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/youtube-automation.git
cd youtube-automation
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Verify FFmpeg Installation

```bash
ffmpeg -version
```

If FFmpeg is not found, install it following the [Prerequisites](#prerequisites) section.

---

## ⚙️ Configuration

### 1. Set Up Paths

The system uses environment variables for paths. You have two options:

#### Option A: Use Default Paths (Recommended for Beginners)

The system will create folders in the project directory:
- `SourceVideosToEdit/` - Place your source videos here
- `FinalVideos/` - Processed videos will be saved here
- `Quotes.txt` - Create this file with your quotes

#### Option B: Use Custom Paths (Advanced)

Set environment variables:

**Windows (PowerShell):**
```powershell
$env:VIDEO_SOURCE_FOLDER="E:\MyVideos"
$env:QUOTES_FILE="E:\MyQuotes.txt"
$env:OUTPUT_FOLDER="D:\Output"
```

**Linux/macOS:**
```bash
export VIDEO_SOURCE_FOLDER="/home/user/videos"
export QUOTES_FILE="/home/user/quotes.txt"
export OUTPUT_FOLDER="/home/user/output"
```

### 2. Set Up YouTube Credentials

1. Create `youtube_credentials/` folder in the project root
2. Place your OAuth credentials for each channel:
   - `client_secret_channel1.json`
   - `client_secret_channel2.json`
   - `client_secret_channel3.json`
   - `client_secret_channel4.json`
   - `client_secret_channel5.json`

**⚠️ IMPORTANT**: Never commit these files to Git! They are already in `.gitignore`.

### 3. Create Quotes File

Create `Quotes.txt` in the project root (or custom location):

```text
1. Success is not final, failure is not fatal. 💪 Agree or not?

2. The only way to do great work is to love what you do. ❤️ True?

3. Believe you can and you're halfway there. ✨ Relatable?
```

**Format Options**:
- Numbered format (as shown above)
- Double newline separated
- Triple dash separated (`---`)
- One quote per line

---

## 🚀 Usage

### Step 1: Configure Overlay Settings (GUI)

Run the GUI to customize text overlay appearance:

```bash
python overlay_settings_gui.py
```

**Settings You Can Customize**:
- Font style and size
- Text and background colors
- Opacity and corner radius
- Position (top/center/bottom)
- CTA (Call-to-Action) styling
- Emoji settings

Click **"Save Settings"** when done.

### Step 2: Process Videos

Add text overlays to your videos:

```bash
python youtube_video_automation.py
```

**Or for enhanced effects**:

```bash
python youtube_video_automation_enhanced.py
```

**What It Does**:
1. Loads videos from `SourceVideosToEdit/`
2. Loads quotes from `Quotes.txt`
3. Pairs each video with a quote
4. Generates hashtags automatically
5. Renders videos with overlays
6. Saves to `FinalVideos/`

### Step 3: Upload to YouTube

Upload processed videos to your channels:

```bash
python youtube_uploader.py
```

**Interactive Menu**:
1. Upload one video now
2. Start continuous upload (every 5 minutes)
3. Show upload statistics
4. Exit

**First Time Setup**:
- Browser will open for each channel
- Sign in to authorize the application
- Credentials are saved for future use

---

## 📁 Project Structure

```
youtube-automation/
├── config.py                           # Configuration management
├── requirements.txt                    # Python dependencies
├── .gitignore                          # Git ignore rules
├── README.md                           # This file
│
├── youtube_video_automation.py         # Basic video processing
├── youtube_video_automation_enhanced.py # Advanced effects
├── youtube_uploader.py                 # Multi-channel uploader
├── overlay_settings_gui.py             # Settings GUI
│
├── overlay_settings.json               # Saved overlay settings
├── Quotes.txt                          # Your quotes (create this)
├── NotoColorEmoji.ttf                  # Bundled emoji font
│
├── youtube_credentials/                # OAuth credentials (create this)
│   ├── client_secret_channel1.json
│   ├── client_secret_channel2.json
│   ├── token_channel1.pickle           # Auto-generated
│   └── ...
│
├── SourceVideosToEdit/                 # Input videos (auto-created)
├── FinalVideos/                        # Processed videos (auto-created)
│   ├── Uploaded/                       # Successfully uploaded
│   ├── Failed/                         # Failed uploads
│   ├── upload_log.json                 # Upload history
│   └── processing_log.json             # Processing history
│
└── fonts/                              # Custom fonts (optional)
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. ModuleNotFoundError: No module named 'moviepy'

**Solution**:
```bash
pip install -r requirements.txt
```

#### 2. FFmpeg not found

**Error**: `FileNotFoundError: [WinError 2] The system cannot find the file specified`

**Solution**:
- Install FFmpeg following [Prerequisites](#prerequisites)
- Add FFmpeg to system PATH
- Restart terminal after installation

#### 3. Font loading errors

**Error**: `⚠ Could not load font`

**Solution**:
- The system will use default font (degraded quality)
- Install the font you specified in overlay settings
- Or use bundled `NotoColorEmoji.ttf` for emojis

#### 4. YouTube Upload Fails (403 - Quota Exceeded)

**Solution**:
- Wait 24 hours for quota reset
- Create additional Google Cloud projects
- Use different OAuth credentials

#### 5. Video file not found

**Solution**:
- Check `VIDEO_SOURCE_FOLDER` path is correct
- Ensure videos have supported extensions: `.mp4`, `.avi`, `.mov`, `.mkv`
- Verify folder exists and has read permissions

#### 6. Credentials Error

**Error**: `❌ Missing credentials file`

**Solution**:
- Verify OAuth credentials are in `youtube_credentials/` folder
- Check filename matches: `client_secret_channel1.json`
- Ensure JSON file is valid (not corrupt)

---

## 🔒 Security

### Best Practices

1. **Never Commit Credentials**
   - `.gitignore` protects OAuth credentials
   - Double-check before `git push`

2. **Token Storage**
   - Tokens stored as `.pickle` files (not encrypted)
   - Keep `youtube_credentials/` folder secure
   - Don't share pickle files

3. **API Quota Management**
   - Monitor daily usage in Google Cloud Console
   - Set up quota alerts
   - Use separate projects for different channels

4. **Path Traversal Protection**
   - Filename sanitization prevents `../` attacks
   - Don't use untrusted quotes files

---

## 🔄 Update Guide

### Pulling Latest Changes

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

### Configuration Changes

If new configuration options are added:
1. Check `config.py` for new settings
2. Update your environment variables if needed
3. Re-run `overlay_settings_gui.py` to update settings file

---

## 📊 Monitoring

### View Upload Statistics

```bash
python youtube_uploader.py
# Choose option 3: Show upload statistics
```

### Check Logs

- **Upload Log**: `FinalVideos/upload_log.json`
- **Processing Log**: `FinalVideos/processing_log.json`

### View Failed Videos

Check `FinalVideos/Failed/` folder for videos that failed to upload.

---

## 🎨 Customization

### Adding More Channels

Edit `youtube_uploader.py`:

```python
self.channels = {
    'channel6': {
        'name': 'Channel 6',
        'credentials_file': 'client_secret_channel6.json',
        'token_file': 'token_channel6.pickle',
        'default_category': '22',
        'default_privacy': 'public'
    }
}
```

### Changing Upload Interval

Set environment variable:

```bash
# Windows
$env:UPLOAD_INTERVAL=600  # 10 minutes

# Linux/macOS
export UPLOAD_INTERVAL=600
```

### Custom Font Paths

Place fonts in `fonts/` folder, or specify full path in GUI settings.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a Pull Request

---

## 📝 License

This project is provided as-is for educational purposes.

---

## 🆘 Support

For issues and questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review `ProjectDetails.txt` for detailed workflow
3. Open an issue on GitHub

---

## 🎉 Quick Start Summary

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up credentials
# Place OAuth JSON files in youtube_credentials/

# 3. Create Quotes.txt

# 4. Configure settings
python overlay_settings_gui.py

# 5. Process videos
python youtube_video_automation.py

# 6. Upload to YouTube
python youtube_uploader.py
```

**That's it! Your YouTube automation system is ready!** 🚀
