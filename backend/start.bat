@echo off
REM start.bat - Complete setup and launch script for OpenResearch
REM Creates venv, installs dependencies, starts backend, and opens browser

setlocal enabledelayedexpansion

echo ========================================
echo   OpenResearch - Complete Setup
echo ========================================

:: Check if venv exists, create if not
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment. Make sure Python is installed.
        pause
        exit /b 1
    )
) else (
    echo Virtual environment already exists.
)

:: Activate venv
echo Activating virtual environment...
call ".venv\Scripts\activate.bat"
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment.
    pause
    exit /b 1
)

:: Install requirements
echo Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies. Check your internet connection and requirements.txt.
    pause
    exit /b 1
)

:: Start backend in background
echo Starting backend server...
start "OpenResearch Backend" cmd /c "start_backend.bat --bg --reload"

:: Wait a moment for server to start
timeout /t 3 /nobreak >nul

:: Open browser to frontend
echo Opening browser to frontend...
start http://localhost:8081

echo ========================================
echo   Setup Complete!
echo ========================================
echo Backend server is starting in the background.
echo Frontend opened in your default browser.
echo.
echo If the page doesn't load, the server might still be starting.
echo Try refreshing the page in a few seconds.
echo.
echo To stop the server later, close the "OpenResearch Backend" command window.
echo ========================================

pause