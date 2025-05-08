@echo off
echo Smart Desktop Activity Tracker - Database Fix
echo ==========================================
echo.

REM Copy the fixed models file
echo Fixing database models...
copy /Y fixed_models.py models.py

REM Create .env file
echo Creating .env file with SQLite configuration...
echo # Database configuration > .env
echo DATABASE_URL=sqlite:///data/smart_desktop_tracker.db >> .env

REM Create data directory
echo Creating data directory...
if not exist data mkdir data

echo.
echo Database setup fixed successfully!
echo.
echo To start the application, run start.bat
echo.
pause