# Smart Desktop Activity Tracker - Installation Guide

## Prerequisites

Before installing the Smart Desktop Activity Tracker, ensure you have the following prerequisites:

1. **Python 3.8 or newer** - Download from [python.org](https://www.python.org/downloads/)
2. **Git** (optional) - Download from [git-scm.com](https://git-scm.com/downloads)
3. **Windows 10/11** - This application is designed for Windows

## Installation Steps

### Step 1: Get the Code

#### Option A: Download ZIP
1. Download the ZIP file from the project repository
2. Extract it to a folder on your computer

#### Option B: Clone Repository (requires Git)
```
git clone https://github.com/yourusername/smart-desktop-tracker.git
cd smart-desktop-tracker
```

### Step 2: Run Setup Script

1. Navigate to the extracted/cloned folder
2. Right-click on `setup.bat` and select "Run as administrator"
3. The setup script will:
   - Create a Python virtual environment
   - Install all required dependencies
   - Set up the database (SQLite by default)

### Step 3: First Run

1. After setup completes, run `start.bat` to start the application
2. On first run, the application will:
   - Create necessary directories
   - Initialize the database
   - Configure default settings

## Database Configuration

By default, the application uses SQLite, which requires no additional setup. However, if you want to use PostgreSQL:

1. Install PostgreSQL from [postgresql.org](https://www.postgresql.org/download/)
2. Create a new database for the application
3. Create a `.env` file in the application directory with the following content:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/dbname
   ```
   Replace `username`, `password`, and `dbname` with your PostgreSQL credentials.

## Troubleshooting

### Database Issues
If you encounter database-related errors:
1. Run `fix_db.bat` to reset the database configuration to SQLite
2. Run `test_db.py` to verify database connectivity

### Dependency Issues
If you encounter missing dependencies:
1. Activate the virtual environment:
   ```
   venv\Scripts\activate
   ```
2. Reinstall dependencies:
   ```
   pip install -r dependencies.txt
   ```

### OCR Issues
For text recognition to work properly:
1. Install Tesseract OCR from [github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)
2. Add Tesseract to your PATH or specify its location in the application settings

## Support

If you encounter any issues not covered in this guide, please:
1. Check the project repository for known issues
2. Submit a detailed bug report including:
   - Steps to reproduce the issue
   - Error messages (if any)
   - Your system configuration