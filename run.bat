@echo off
title MeoBoost Launcher
color 0B

echo.
echo   MeoBoost - Windows Performance Optimizer
echo   =========================================
echo.

:: Kiem tra Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [LOI] Chua cai Python!
    echo Tai Python 3.8+ tai: https://www.python.org/downloads/
    echo Nho tick "Add Python to PATH" khi cai dat.
    pause
    exit /b 1
)

echo [OK] Da tim thay Python
echo.

:: Kiem tra dependencies
echo [INFO] Kiem tra thu vien...
pip show rich >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Cai dat thu vien...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [LOI] Khong the cai dat thu vien!
        pause
        exit /b 1
    )
)

echo [OK] Thu vien da san sang
echo.

:: Chay voi quyen admin
echo [INFO] Khoi dong MeoBoost...
echo.

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Yeu cau quyen Administrator...
    powershell -Command "Start-Process python -ArgumentList 'main.py' -Verb RunAs -WorkingDirectory '%~dp0'"
) else (
    python main.py
)
