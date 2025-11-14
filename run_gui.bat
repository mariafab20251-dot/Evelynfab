REM ========================================
REM File 2: run_gui.bat
REM Run this to configure overlay settings
REM ========================================

@echo off
echo.
echo ====================================
echo   Video Overlay Settings GUI
echo ====================================
echo.
echo Opening settings interface...
echo Configure your font, colors, sizes, etc.
echo Click "Save Settings" when done!
echo.

python overlay_settings_gui.py

if errorlevel 1 (
    echo.
    echo Error running GUI!
    echo Make sure Python and required packages are installed.
    echo Run setup.bat if you haven't already.
    echo.
    pause
)
