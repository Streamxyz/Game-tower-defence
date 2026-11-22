@echo off
setlocal enabledelayedexpansion

title Modern Military Tower Defence - Launcher

echo ========================================================
echo    MODERN MILITARY TOWER DEFENCE - WINDOWS LAUNCHER
echo ========================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not detected in your PATH.
    echo Please install Python 3.10+ from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

:: Check if virtual environment exists, if not create one
if not exist ".venv" (
    echo [SETUP] Creating isolated Python virtual environment (.venv)...
    python -m venv .venv
    if %ERRORLEVEL% NEQ 0 (
        echo [WARN] Could not create virtual environment. Running with global python.
        goto install_deps_global
    )
)

:: Activate virtual environment
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo [SETUP] Virtual environment activated.
    echo [SETUP] Checking and installing dependencies (pygame)...
    pip install -r requirements.txt --quiet
    echo.
    echo [START] Launching Game...
    python main.py
    goto end
)

:install_deps_global
echo [SETUP] Checking and installing dependencies globally...
pip install -r requirements.txt --quiet
echo.
echo [START] Launching Game...
python main.py

:end
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [GAME CRASH OR ERROR DETECTED]
    pause
)
