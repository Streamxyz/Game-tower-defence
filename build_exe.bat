@echo off
setlocal

title Modern Military Tower Defence - Standalone EXE Builder

echo ========================================================
echo        STANDALONE WINDOWS .EXE BUILD SCRIPT
echo ========================================================
echo.

python -m pip install pyinstaller pygame --quiet
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install PyInstaller.
    pause
    exit /b 1
)

echo [BUILD] Packaging game into standalone executable...
pyinstaller --noconfirm --onedir --windowed ^
    --name "ModernMilitaryTowerDefence" ^
    --add-data "assets;assets" ^
    main.py

echo.
if %ERRORLEVEL% EQU 0 (
    echo ========================================================
    echo  SUCCESS! Standalone game created in: dist\ModernMilitaryTowerDefence\
    echo  You can distribute that folder to any Windows computer!
    echo ========================================================
) else (
    echo [ERROR] Build failed.
)

pause
