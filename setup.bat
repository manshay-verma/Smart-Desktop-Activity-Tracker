@echo off
echo Smart Desktop Activity Tracker - Setup
echo =====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python 3.8 or newer.
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate

REM Install dependencies
echo Installing dependencies...
pip install -r dependencies.txt

REM Fix database setup
echo Fixing database setup...
call fix_db.bat

echo.
echo Setup completed successfully!
echo.
echo To start the application, run start.bat
echo.
pause