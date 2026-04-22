@echo off
title Quranic Chatbot Setup
echo ========================================
echo   Setting up Virtual Environment...
echo ========================================
echo.

:: Check if python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH.
    pause
    exit /b
)

:: Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating venv...
    python -m venv venv
) else (
    echo venv already exists.
)

:: Activate and install requirements
echo Installing requirements...
call venv\Scripts\activate
pip install -r requirements.txt

echo.
echo ========================================
echo   Setup Complete!
echo   To start the app, run: python start.py
echo ========================================
echo.
pause
