@echo off
setlocal enabledelayedexpansion

REM ============================================================
REM  Server Monitor - Windows build script (PyInstaller)
REM  Run this on a Windows machine (or Wine) inside client/
REM ============================================================

echo [1/4] Creating virtual environment...
if not exist ".venv" (
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create venv. Install Python 3.9+ first.
        exit /b 1
    )
)

echo [2/4] Installing dependencies...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt pyinstaller
if errorlevel 1 (
    echo ERROR: pip install failed.
    exit /b 1
)

echo [3/4] Building exe with PyInstaller...
cd src
pyinstaller --noconfirm --clean ..\scripts\ServerMonitor.spec
if errorlevel 1 (
    echo ERROR: PyInstaller build failed.
    exit /b 1
)
cd ..

echo [4/4] Build complete.
echo.
echo Output: src\dist\ServerMonitor\ServerMonitor.exe
echo Bundle the whole folder, or zip it for distribution.
echo.

endlocal
