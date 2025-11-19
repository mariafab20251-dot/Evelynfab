
REM ========================================
REM File 3: process_videos.bat
REM Run this to process videos with your settings
REM ========================================

@echo off
echo.
echo ====================================
echo   Video Processing Automation
echo ====================================
echo.

REM Check if settings file exists
if not exist overlay_settings.json (
    echo WARNING: No settings file found!
    echo.
    echo Please run run_gui.bat first to configure your settings.
    echo Press any key to continue with default settings, or close this window.
    pause
)

echo Starting video processing...
echo Using settings from overlay_settings.json
echo This may take a while depending on the number of videos.
echo.

python youtube_video_automation_enhanced.py

if errorlevel 1 (
    echo.
    echo Error processing videos!
    echo Check the error messages above.
    echo.
    pause
) else (
    echo.
    echo ====================================
    echo   Processing Complete!
    echo ====================================
    echo.
    echo Check your FinalVideos folder for processed videos.
    echo.
)

pause