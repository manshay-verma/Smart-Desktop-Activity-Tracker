# Smart Desktop Activity Tracker Installation Guide

This guide will help you install and configure the Smart Desktop Activity Tracker application on your Windows system.

## Prerequisites

Before installing the application, ensure you have:

1. **Windows 10/11** (64-bit operating system)
2. **Python 3.8 or higher** installed
   - Download from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation
3. **PostgreSQL 12 or higher**
   - Download from [postgresql.org](https://www.postgresql.org/download/windows/)
   - Remember the password you set for the 'postgres' user during installation
4. **Administrator privileges** on your system (for installing dependencies)

## Installation Steps

### 1. Download the Application

Clone the repository or download the ZIP file and extract it to a location of your choice:

```bash
git clone https://github.com/yourname/smart-desktop-tracker.git
cd smart-desktop-tracker
```

### 2. Set Up the Database

1. Open pgAdmin (installed with PostgreSQL)
2. Create a new database:
   - Right-click on "Databases" and select "Create" > "Database"
   - Name it "smart_desktop_tracker" (or your preferred name)
   - Click "Save"
3. Note your PostgreSQL connection details:
   - Host (usually localhost or 127.0.0.1)
   - Port (usually 5432)
   - Username (default is 'postgres')
   - Password (the one you set during installation)
   - Database name (the one you just created)

### 3. Install Dependencies

Open Command Prompt or PowerShell as Administrator, navigate to the application directory, and install the required packages:

```bash
pip install -r dependencies.txt
```

### 4. Configure Environment Variables

1. Create a `.env` file in the application directory with the following content:

```
DATABASE_URL=postgresql://username:password@host:port/database_name
```

Replace `username`, `password`, `host`, `port`, and `database_name` with your PostgreSQL details.

Example:
```
DATABASE_URL=postgresql://postgres:mysecretpassword@localhost:5432/smart_desktop_tracker
```

### 5. Run the Application

From the application directory, run:

```bash
python main.py
```

The application should start and display its GUI interface. The first run may take longer as it sets up the database schema.

## Additional Configuration

### Autostart with Windows

To make the application start automatically with Windows:

1. Create a shortcut to the `main.py` file or create a batch file (`.bat`) that runs the application
2. Press `Win + R`, type `shell:startup` and press Enter
3. Move the shortcut or batch file to the Startup folder that opens

### Configuring the Application

After the first run, a `config.json` file will be created in the application's data directory:
```
C:\Users\<your-username>\.smart_desktop_tracker\config.json
```

You can edit this file to customize:
- Screenshot frequency and quality
- Privacy settings and content filtering
- Automation sensitivity
- UI appearance and behavior

### Tesseract OCR Setup (for Text Extraction)

For the text extraction feature to work properly:

1. Download and install Tesseract OCR from [github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)
2. During installation, note the installation path
3. Add the Tesseract installation directory to your PATH environment variable
4. Update the config.json file with the Tesseract path if needed

## Troubleshooting

### Database Connection Issues

If you encounter database connection errors:

1. Verify your PostgreSQL service is running
2. Double-check the connection string in your .env file
3. Ensure your firewall is not blocking the PostgreSQL port

### Missing Dependencies

If the application fails to start due to missing dependencies:

```bash
pip install --upgrade -r dependencies.txt
```

### GUI Display Issues

If the GUI doesn't display properly:

1. Make sure you have a compatible graphics driver installed
2. Try updating your Python and PyQt installations
3. Run the application with the `--debug` flag: `python main.py --debug`

## Support

For additional help or to report issues, please contact support@smartdesktoptracker.com or file an issue on the GitHub repository.

## Uninstallation

To uninstall the application:

1. Delete the application directory
2. Delete the data directory at `C:\Users\<your-username>\.smart_desktop_tracker\`
3. Optionally, drop the PostgreSQL database using pgAdmin