@echo off
echo Smart Desktop Activity Tracker - Starting
echo ========================================
echo.

REM Activate virtual environment
call venv\Scripts\activate

REM Run the application
echo Starting the application...
python main.py

REM Deactivate virtual environment on exit
deactivate

echo.
pause