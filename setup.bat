@echo off
echo ============================================
echo   Swing Trade Analyzer - Setup Script
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo Step 1: Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo ✓ Virtual environment created
echo.

echo Step 2: Activating virtual environment...
call venv\Scripts\activate.bat
echo ✓ Virtual environment activated
echo.

echo Step 3: Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed
echo.

echo Step 4: Creating data directory...
if not exist "data" mkdir data
echo ✓ Data directory created
echo.

echo Step 5: Setting up environment file...
if not exist ".env" (
    copy .env.example .env
    echo ✓ .env file created from template
    echo   Edit .env to add your Alpha Vantage API key (optional)
) else (
    echo ✓ .env file already exists
)
echo.

echo Step 6: Running verification tests...
python verify_setup.py
echo.

echo ============================================
echo   Setup Complete!
echo ============================================
echo.
echo Next steps:
echo   1. Run: run_dashboard.bat
echo   2. Or manually: streamlit run app.py
echo.
pause
