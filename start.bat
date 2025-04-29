@echo off
echo Smart Desktop Activity Tracker
echo ============================
echo.

REM Check if virtual environment exists
if not exist venv (
    echo Virtual environment not found.
    echo Please run setup.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the application
echo Starting application...
python main.py
if %errorlevel% neq 0 (
    echo Application exited with an error.
    pause
)

REM Deactivate virtual environment
call deactivate