REM ========================================
REM File 1: setup.bat
REM Run this FIRST to install required packages
REM ========================================

@echo off
echo.
echo ====================================
echo   Installing Required Packages
echo ====================================
echo.

echo Installing MoviePy (latest version)...
pip install moviepy --upgrade

echo.
echo Installing Pillow...
pip install pillow --upgrade

echo.
echo Installing numpy...
pip install numpy --upgrade

echo.
echo ====================================
echo   Installation Complete!
echo ====================================
echo.
echo Next steps:
echo   1. Run run_gui.bat to configure your overlay settings
echo   2. Run process_videos.bat to process your videos
echo.

pause