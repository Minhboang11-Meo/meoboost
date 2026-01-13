@echo off
title MeoBoost - Optimized EXE Builder
chcp 65001 >nul

echo ╔══════════════════════════════════════════════════════════════╗
echo ║           MeoBoost - Optimized EXE Builder                   ║
echo ║           Compressed Files + Size Optimization               ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python detected
echo.

:: Install dependencies
echo [1/5] Installing build dependencies...
pip install pyinstaller rich --quiet

:: Compress files
echo [2/5] Compressing Files/ directory...
python compress_files.py
if not exist "FilesCompressed" (
    echo [ERROR] Compression failed!
    pause
    exit /b 1
)
echo [OK] Files compressed
echo.

:: Clean previous builds
echo [3/5] Cleaning previous builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

:: Build optimized EXE
echo [4/5] Building optimized MeoBoost.exe...
echo       (Using compressed files + UPX compression)
echo.

pyinstaller --noconfirm --onefile --console --name "MeoBoost" ^
    --add-data "FilesCompressed;FilesCompressed" ^
    --hidden-import "rich" ^
    --hidden-import "rich.console" ^
    --hidden-import "rich.table" ^
    --hidden-import "tweaks.power" ^
    --hidden-import "tweaks.nvidia" ^
    --hidden-import "tweaks.amd" ^
    --hidden-import "tweaks.intel" ^
    --hidden-import "tweaks.gpu_common" ^
    --hidden-import "tweaks.network" ^
    --hidden-import "tweaks.memory" ^
    --hidden-import "tweaks.input" ^
    --hidden-import "tweaks.system" ^
    --hidden-import "tweaks.misc" ^
    --hidden-import "tweaks.privacy" ^
    --hidden-import "tweaks.fps" ^
    --hidden-import "tweaks.winutil" ^
    --hidden-import "utils.registry" ^
    --hidden-import "utils.system" ^
    --hidden-import "utils.backup" ^
    --hidden-import "utils.files" ^
    --hidden-import "utils.settings" ^
    --hidden-import "utils.benchmark" ^
    --hidden-import "ui.terminal" ^
    --exclude-module "matplotlib" ^
    --exclude-module "numpy" ^
    --exclude-module "pandas" ^
    --exclude-module "scipy" ^
    --exclude-module "PIL" ^
    --exclude-module "tkinter" ^
    --exclude-module "unittest" ^
    --exclude-module "pydoc" ^
    --exclude-module "doctest" ^
    --exclude-module "test" ^
    --exclude-module "xmlrpc" ^
    --exclude-module "email" ^
    --exclude-module "html" ^
    --exclude-module "http" ^
    --exclude-module "xml" ^
    --exclude-module "logging" ^
    --exclude-module "multiprocessing" ^
    --exclude-module "concurrent" ^
    --exclude-module "asyncio" ^
    --strip ^
    --uac-admin ^
    main.py

:: Check result
echo.
if exist "dist\MeoBoost.exe" (
    echo [5/5] Build successful!
    echo.
    echo    ╔═══════════════════════════════════════════════════╗
    for %%A in ("dist\MeoBoost.exe") do (
        set /a SIZE_KB=%%~zA/1024
        echo    ║  Output: dist\MeoBoost.exe
        echo    ║  Size:   %%~zA bytes
    )
    echo    ╚═══════════════════════════════════════════════════╝
    echo.
    echo    Ready to release! Run: git tag v1.x.x ^&^& git push --tags
) else (
    echo [ERROR] Build failed!
    echo Check the error messages above.
)

echo.
pause
