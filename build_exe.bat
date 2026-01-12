@echo off
title MeoBoost - Build EXE
chcp 65001 >nul

echo ╔══════════════════════════════════════════╗
echo ║       MeoBoost - EXE Builder             ║
echo ╚══════════════════════════════════════════╝
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python không được cài đặt!
    echo Vui lòng cài Python 3.8+ từ python.org
    pause
    exit /b 1
)

:: Check/Install dependencies
echo [1/4] Kiểm tra và cài đặt dependencies...
pip install pyinstaller rich --quiet

:: Clean previous builds
echo [2/4] Dọn dẹp build cũ...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

:: Build EXE
echo [3/4] Đang build MeoBoost.exe...
echo       (Có thể mất 1-2 phút)
pyinstaller MeoBoost.spec --noconfirm

:: Check result
echo.
if exist "dist\MeoBoost.exe" (
    echo [4/4] ✓ Build thành công!
    echo.
    echo    File EXE: dist\MeoBoost.exe
    echo    Size: 
    for %%A in ("dist\MeoBoost.exe") do echo       %%~zA bytes
    echo.
    echo Có thể copy file MeoBoost.exe ra chạy trực tiếp.
) else (
    echo [ERROR] Build thất bại!
    echo Kiểm tra lỗi ở trên.
)

echo.
pause
