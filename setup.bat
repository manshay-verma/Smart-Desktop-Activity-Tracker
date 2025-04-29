@echo off
echo Smart Desktop Activity Tracker - Setup
echo =====================================
echo.

REM Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed or not in your PATH.
    echo Please install Python 3.8 or higher from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo Failed to create virtual environment.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo Installing dependencies...
pip install -r dependencies.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies.
    pause
    exit /b 1
)

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating default .env file...
    echo # Database configuration > .env
    echo # Uncomment and modify the line below to use a PostgreSQL database >> .env
    echo # DATABASE_URL=postgresql://username:password@localhost:5432/database_name >> .env
    echo # By default, a local SQLite database will be used >> .env
    echo. >> .env
)

echo.
echo Setup completed successfully!
echo.
echo To start the application:
echo 1. Run "start.bat"
echo.
echo To set up a PostgreSQL database:
echo 1. Install PostgreSQL from https://www.postgresql.org/download/
echo 2. Create a database for the application
echo 3. Edit the .env file and uncomment the DATABASE_URL line
echo 4. Update the connection details in the DATABASE_URL
echo.
pause