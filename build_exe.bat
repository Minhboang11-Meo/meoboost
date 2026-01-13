@echo off
title MeoBoost - Nuitka Builder
chcp 65001 >nul

echo ╔══════════════════════════════════════════════════════════════╗
echo ║              MeoBoost - Nuitka Builder                       ║
echo ║         Native C Compilation for Better AV Compatibility     ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo Please install Python 3.8-3.12 from https://www.python.org/downloads/
    echo Note: Python 3.13+ is NOT supported by Nuitka yet.
    pause
    exit /b 1
)

echo [OK] Python detected
echo.

:: Install Nuitka and dependencies
echo [1/4] Installing Nuitka and dependencies...
pip install nuitka ordered-set zstandard rich --quiet

:: Clean previous builds
echo [2/4] Cleaning previous builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "main.build" rmdir /s /q "main.build"
if exist "main.dist" rmdir /s /q "main.dist"
if exist "main.onefile-build" rmdir /s /q "main.onefile-build"
if exist "nuitka-crash-report.xml" del /f /q "nuitka-crash-report.xml"

:: Build with Nuitka
echo [3/4] Building with Nuitka (this takes 3-5 minutes)...
echo       Compiling Python to native C code...
echo.

python -m nuitka ^
    --standalone ^
    --onefile ^
    --output-dir=dist ^
    --windows-console-mode=force ^
    --include-data-dir=Files=Files ^
    --enable-plugin=anti-bloat ^
    --remove-output ^
    --assume-yes-for-downloads ^
    --company-name="MeoBoost Open Source" ^
    --product-name="MeoBoost" ^
    --file-version=1.0.0.0 ^
    --product-version=1.0.0.0 ^
    --file-description="Windows Performance Optimizer" ^
    --copyright="MIT License - github.com/Minhboang11-Meo/meoboost" ^
    --deployment ^
    --output-filename=MeoBoost.exe ^
    main.py

:: Check result
echo.
if exist "dist\MeoBoost.exe" (
    echo [4/4] Build successful!
    echo.
    echo    Output: dist\MeoBoost.exe
    for %%A in ("dist\MeoBoost.exe") do echo    Size:   %%~zA bytes
    echo.
    echo Benefits of Nuitka build:
    echo   - Native C compilation (not Python bytecode)
    echo   - Better AV compatibility (fewer false positives)
    echo   - No PyInstaller bootloader signature
    echo.
) else (
    echo [ERROR] Build failed!
    echo Check the error messages above for details.
    echo.
    echo Common issues:
    echo   - Python 3.13+ is not yet supported
    echo   - Missing C compiler (install Visual Studio Build Tools)
    echo   - Insufficient disk space
)

echo.
pause

