@echo off
title MeoBoost Launcher
color 0B

echo.
echo   ╔══════════════════════════════════════════════════════════╗
echo   ║           MeoBoost - Windows Performance Optimizer       ║
echo   ╚══════════════════════════════════════════════════════════╝
echo.

:: Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed!
    echo.
    echo Download Python 3.8+ at: https://www.python.org/downloads/
    echo Remember to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [OK] Python found
echo.

:: Check dependencies
echo [INFO] Checking required libraries...
pip show rich >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Installing required libraries...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install libraries!
        echo Please check your internet connection and try again.
        pause
        exit /b 1
    )
)

echo [OK] All libraries are ready
echo.

:: Run with admin privileges
echo [INFO] Starting MeoBoost...
echo.

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Requesting Administrator privileges...
    powershell -Command "Start-Process python -ArgumentList 'main.py' -Verb RunAs -WorkingDirectory '%~dp0'"
) else (
    python main.py
)
