# Module Reference Guide

This document provides a detailed reference for all modules in the Smart Desktop Activity Tracker, explaining their purpose, key functions, and relationships.

## Core Modules

### Main Application (`main.py`)

**Purpose**: Entry point and coordinator for the entire application.

**Key Functions**:
- `initialize_modules()`: Set up all application modules
- `start_application()`: Start the application
- `shutdown_application()`: Clean shutdown of all modules
- `handle_exceptions()`: Global exception handler

**Dependencies**: All other modules

### Database Manager (`db_manager.py`)

**Purpose**: Manages database operations and provides an abstraction layer for storage.

**Key Functions**:
- `save_screenshot()`: Save screenshot metadata
- `log_activity()`: Record user activities
- `save_automation_task()`: Store automation sequences
- `save_automation_suggestion()`: Store automation suggestions
- `get_recent_activities()`: Retrieve recent activity logs
- `cleanup_old_data()`: Remove old data based on retention policy

**Dependencies**: `models.py` or `fixed_models.py`

### Configuration (`config.py`)

**Purpose**: Manages application configuration settings.

**Key Functions**:
- `load_config()`: Load configuration from file
- `save_config()`: Save configuration to file
- `update_config()`: Update specific configuration values

**Dependencies**: None

## Input Tracking Modules

### Keyboard Logger (`keyboard_logger.py`)

**Purpose**: Tracks keyboard activity for understanding user behavior.

**Key Functions**:
- `start_monitoring()`: Begin keyboard monitoring
- `stop()`: Stop keyboard monitoring
- `on_key_press()`: Handle key press events
- `on_key_release()`: Handle key release events
- `get_last_text()`: Retrieve recent text input (without storing actual keystrokes)

**Dependencies**: `pynput` library

### Screen and Mouse Logger (`screen_mouse_logger.py`)

**Purpose**: Captures screenshots and tracks mouse activity.

**Key Functions**:
- `start_monitoring()`: Begin screen/mouse monitoring
- `stop()`: Stop monitoring
- `on_click()`: Handle mouse click events
- `on_scroll()`: Handle mouse scroll events
- `capture_screenshot()`: Take and process screenshots
- `get_active_window_info()`: Get information about active window

**Dependencies**: `pynput`, `PIL`, `db_manager.py`

## Analysis Modules

### Text Analyzer (`text_analyzer.py`)

**Purpose**: Extracts and analyzes text from screenshots.

**Key Functions**:
- `extract_text_from_image()`: OCR text extraction
- `analyze_text()`: Process and analyze extracted text
- `identify_applications()`: Identify applications from text
- `extract_structured_data()`: Extract data like emails, URLs, etc.

**Dependencies**: `pytesseract`, `nltk`, `db_manager.py`

### ML Integration (`ml_integration.py`)

**Purpose**: Applies machine learning to identify patterns and make predictions.

**Key Classes**:
- `PatternRecognizer`: Identifies patterns in user behavior
  - `train_models()`: Train ML models on activity data
  - `detect_patterns()`: Find patterns in activity data
  - `score_patterns()`: Calculate confidence scores for patterns

**Key Functions**:
- `preprocess_data()`: Prepare data for ML algorithms
- `extract_features()`: Convert raw data to feature vectors
- `evaluate_model()`: Assess model performance

**Dependencies**: `scikit-learn`, `numpy`, `db_manager.py`

## Automation Modules

### Automation Module (`automation_module.py`)

**Purpose**: Records, manages, and executes automation sequences.

**Key Functions**:
- `start_recording()`: Begin recording user actions
- `stop_recording()`: Stop recording and save automation
- `execute_automation()`: Run a recorded automation
- `get_automations()`: List available automations
- `delete_automation()`: Remove an automation

**Private Functions**:
- `_on_record_click()`: Record mouse clicks
- `_on_record_scroll()`: Record mouse scrolls
- `_on_record_key_press()`: Record key presses
- `_optimize_recording()`: Optimize recorded sequences

**Dependencies**: `pynput`, `db_manager.py`

### Repetitive Task Suggestion (`repetitive_task_suggestion.py`)

**Purpose**: Analyzes activity data to identify and suggest automation opportunities.

**Key Functions**:
- `analyze_activity_history()`: Find patterns in past activities
- `generate_suggestions()`: Create automation suggestions
- `evaluate_suggestion_quality()`: Assess suggestion quality
- `generate_automation_from_suggestion()`: Convert suggestion to automation

**Dependencies**: `ml_integration.py`, `db_manager.py`

## User Interface

### GUI Interface (`gui_interface.py`)

**Purpose**: Manages the user interface components.

**Key Classes**:
- `FloatingSidebar`: Main UI component
  - `_setup_ui()`: Create UI elements
  - `update_content()`: Update displayed information
  - `toggle_expand()`: Expand/collapse sidebar
  - `check_auto_hide()`: Handle auto-hide functionality
  - `toggle_recording()`: Control automation recording

- `GUIInterface`: Controller for UI components
  - `start()`: Initialize and show UI
  - `stop()`: Hide and clean up UI
  - `update_display()`: Update UI with current data

**Dependencies**: `PyQt5`, shared data dictionary

## Utility Modules

### Utilities (`utils.py`)

**Purpose**: Provides common utility functions used across the application.

**Key Functions**:
- `get_timestamp()`: Generate formatted timestamps
- `create_thumbnail()`: Create thumbnail of image
- `sanitize_filename()`: Clean filenames for storage
- `calculate_hash()`: Generate hash for data
- `load_json()`: Safely load JSON data
- `save_json()`: Safely save JSON data

**Dependencies**: Various standard libraries

## Database Models

### Models (`models.py` or `fixed_models.py`)

**Purpose**: Defines database schema and ORM models.

**Key Models**:
- `User`: User information and settings
- `Screenshot`: Screenshot metadata
- `ActivityLog`: Activity records
- `AutomationTask`: Recorded automations
- `AutomationSuggestion`: Suggested automations

**Key Functions**:
- `init_db()`: Initialize database connection

**Dependencies**: `sqlalchemy`

## Module Relationships Diagram

```
main.py
  │
  ├─── config.py
  │
  ├─── db_manager.py ──── models.py/fixed_models.py
  │
  ├─── utils.py
  │
  ├─── Input Tracking
  │     │
  │     ├─── keyboard_logger.py
  │     │
  │     └─── screen_mouse_logger.py
  │
  ├─── Analysis
  │     │
  │     ├─── text_analyzer.py
  │     │
  │     └─── ml_integration.py
  │
  ├─── Automation
  │     │
  │     ├─── automation_module.py
  │     │
  │     └─── repetitive_task_suggestion.py
  │
  └─── GUI
        │
        └─── gui_interface.py
```

## File Locations

All module files are in the project root directory:

```
/
├── main.py
├── config.py
├── db_manager.py
├── models.py
├── fixed_models.py
├── utils.py
├── keyboard_logger.py
├── screen_mouse_logger.py
├── text_analyzer.py
├── ml_integration.py
├── automation_module.py
├── repetitive_task_suggestion.py
├── gui_interface.py
├── setup.bat
├── start.bat
├── fix_db.bat
└── test_db.py
```

## Data Directories

The application uses these data directories:

1. `/data/`: Main data directory (SQLite database)
2. `/logs/`: Log files
3. `~/.smart_desktop_tracker/`: User data directory (created if using default settings)

## Configuration Files

1. `.env`: Environment variables including database configuration
2. `config.json`: User preferences and settings (created at first run)

## How Modules Communicate

Modules communicate through:

1. **Shared Data Dictionary**: A central dictionary passed to all modules
2. **Database**: Persistent storage of data shared between modules
3. **Direct Function Calls**: Some modules call functions in other modules
4. **Event System**: For asynchronous communication between components

## Adding New Modules

To add a new module:

1. Create a new Python file in the project root
2. Import necessary dependencies
3. Define a class with an `__init__` method accepting at least:
   - `data_dir`: Directory for module-specific data
   - `shared_data`: Shared data dictionary
4. Implement `start()` and `stop()` methods
5. Add the module initialization to `main.py`

Example skeleton for a new module:

```python
class NewModule:
    """
    Description of the new module
    """
    def __init__(self, data_dir, shared_data):
        """
        Initialize the module
        
        Args:
            data_dir (str): Directory for module data
            shared_data (dict): Shared data dictionary
        """
        self.data_dir = data_dir
        self.shared_data = shared_data
        self.running = False
        
    def start(self):
        """Start the module"""
        if self.running:
            return
            
        # Module initialization code
        self.running = True
        
    def stop(self):
        """Stop the module"""
        if not self.running:
            return
            
        # Module cleanup code
        self.running = False
```

## Troubleshooting Module Issues

Common module issues and solutions:

1. **Module Import Errors**:
   - Check that all required packages are installed
   - Verify file paths and names

2. **Module Initialization Failures**:
   - Check that required directories exist
   - Verify database connection
   - Check permissions on files and directories

3. **Module Communication Issues**:
   - Verify shared_data dictionary is being passed correctly
   - Check for typos in dictionary keys

4. **Database-Related Errors**:
   - Run `fix_db.bat` to reset database configuration
   - Check database connection string in `.env`
   - Verify SQLAlchemy models match database schema