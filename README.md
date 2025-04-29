# Smart Desktop Activity Tracker

A comprehensive desktop activity monitoring and automation tool that tracks user activities, analyzes behavior patterns, and suggests automations for repetitive tasks.

## Features

- **Activity Tracking**: Captures screenshots, keyboard/mouse interactions, and window title information
- **Text Analysis**: Extracts text from screenshots using OCR for rich context analysis
- **Pattern Recognition**: Uses ML algorithms to identify repetitive tasks and behavior patterns
- **Automation Suggestions**: Suggests automations for frequently performed tasks
- **Automation Execution**: Records and executes automation macros for repetitive tasks
- **Privacy Controls**: Configurable privacy settings with content filtering for sensitive information
- **Data Storage**: Secure PostgreSQL database for activity storage and analysis
- **Interactive GUI**: Floating sidebar for real-time activity monitoring and automation control

## System Requirements

- Windows 10/11 (64-bit)
- Python 3.8 or higher
- PostgreSQL 12 or higher
- 4GB RAM minimum
- 500MB free disk space

## Installation

1. Ensure Python 3.8+ is installed on your system
2. Install PostgreSQL and create a database for the application
3. Clone the repository
4. Install required packages: `pip install -r dependencies.txt`
5. Set the DATABASE_URL environment variable to your PostgreSQL connection string
6. Run the application: `python main.py`

## Configuration

The application can be configured by editing the `config.json` file that is created in the application's data directory on first run. Key configuration options include:

- **Screenshot settings**: Frequency, quality, and storage limits
- **Privacy settings**: Blacklisted applications and keywords
- **Automation settings**: Pattern detection sensitivity and suggestion thresholds
- **UI settings**: Sidebar position, opacity, and auto-hide behavior

## Database Schema

The application uses the following database tables:

- **users**: User profiles and settings
- **screenshots**: Screenshot metadata and file paths
- **activity_logs**: User activity history
- **automation_tasks**: Recorded automation macros
- **automation_suggestions**: Suggested automations based on detected patterns

## Module Structure

- **main.py**: Main entry point and module coordinator
- **gui_interface.py**: Qt-based graphical user interface
- **screen_mouse_logger.py**: Screen capture and mouse activity tracking
- **keyboard_logger.py**: Keyboard activity monitoring
- **text_analyzer.py**: OCR and text analysis from screenshots
- **automation_module.py**: Automation recording and execution
- **repetitive_task_suggestion.py**: Pattern detection and suggestion generation
- **ml_integration.py**: Machine learning for pattern recognition
- **db_manager.py**: Database operations
- **models.py**: Database models
- **utils.py**: Utility functions
- **config.py**: Configuration management

## Dependencies

See the `dependencies.txt` file for a complete list of required Python packages.

## Privacy Considerations

The application includes several privacy features:

- Keyboard privacy mode to prevent logging of sensitive information
- Application blacklist to avoid monitoring sensitive applications
- Configurable data retention policies
- Local-only processing with no data sent to external servers

## License

MIT License