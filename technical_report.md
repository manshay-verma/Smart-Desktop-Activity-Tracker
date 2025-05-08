# Smart Desktop Activity Tracker: Technical Report

## System Architecture Overview

The Smart Desktop Activity Tracker is built with a modular architecture that separates concerns into discrete components. This document explains the technology stack, data flow, and AI/ML implementations used throughout the system.

## Core Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Backend | Python 3.8+ | Core application logic |
| GUI | PyQt5 | User interface |
| Database | PostgreSQL/SQLite | Data storage |
| Image Processing | OpenCV | Screenshot analysis |
| Text Recognition | Tesseract OCR | Text extraction from images |
| Machine Learning | scikit-learn | Pattern recognition |
| Input Monitoring | pynput | Keyboard/mouse tracking |

## Module Breakdown and Code Locations

### 1. Main Application (`main.py`)

The main application initializes all modules and coordinates their interactions. It:
- Loads configuration settings
- Creates and initializes all module instances
- Sets up event handlers between modules
- Manages the application lifecycle

```python
# Key sections in main.py
def initialize_modules():
    """Initialize all application modules"""
    # Setup shared data dictionary for inter-module communication
    shared_data = {}
    
    # Initialize modules with configuration
    db_manager = DBManager()
    keyboard_logger = KeyboardLogger(data_dir, shared_data)
    screen_mouse_logger = ScreenMouseLogger(data_dir, shared_data, db_manager)
    text_analyzer = TextAnalyzer(shared_data, db_manager)
    automation_module = AutomationModule(data_dir, shared_data)
    gui = GUIInterface(shared_data, app)
```

### 2. Database Manager (`db_manager.py`)

The database manager provides an abstraction layer for database operations, handling:
- Connection management
- Model interactions (CRUD operations)
- Transaction handling
- Error recovery
- Data cleanup

Key technology: SQLAlchemy ORM with PostgreSQL (primary) or SQLite (fallback).

```python
# Key functions in db_manager.py
def save_screenshot(self, file_path, window_title=None, application_name=None, extracted_text=None):
    """Save screenshot metadata to database"""
    # Create screenshot record using SQLAlchemy model
    
def log_activity(self, activity_type, description=None, screenshot_id=None, data=None):
    """Log user activity to database"""
    # Create activity log using SQLAlchemy model
    
def get_automation_suggestions(self, include_dismissed=False):
    """Retrieve automation suggestions from database"""
    # Query and return automation suggestions
```

### 3. Input Tracking Modules

#### 3.1 Keyboard Logger (`keyboard_logger.py`)

Tracks keyboard activity to identify usage patterns.

Technologies: pynput for keyboard hooks, threading for background operation.

```python
# Key functions in keyboard_logger.py
def on_key_press(self, key):
    """Key press event handler"""
    # Log key press without capturing actual keystrokes
    # Update key frequency statistics
    
def get_last_text(self, chars=100):
    """Return last N characters of text from buffer"""
    # Used for pattern analysis without storing sensitive information
```

#### 3.2 Screen and Mouse Logger (`screen_mouse_logger.py`)

Captures screenshots and mouse activity.

Technologies: pynput for mouse tracking, PIL/Pillow for screenshots, OpenCV for image processing.

```python
# Key functions in screen_mouse_logger.py
def on_click(self, x, y, button, pressed):
    """Mouse click event handler"""
    # Log mouse click and potentially trigger screenshot
    
def capture_screenshot(self, trigger_type="manual"):
    """Capture and process screenshot"""
    # Take screenshot
    # Create thumbnail
    # Get active window information
    # Save to disk and database
```

### 4. Data Analysis Modules

#### 4.1 Text Analyzer (`text_analyzer.py`)

Extracts and analyzes text from screenshots.

Technologies: Tesseract OCR for text extraction, NLTK for text processing, regular expressions for pattern matching.

```python
# Key functions in text_analyzer.py
def extract_text_from_image(self, image_path):
    """Extract text from image using OCR"""
    # Use Tesseract to extract text
    # Clean and normalize extracted text
    
def analyze_text(self, text, context=None):
    """Analyze extracted text for patterns and meaning"""
    # Perform NLP operations
    # Identify applications
    # Extract structured data (emails, URLs, etc.)
```

#### 4.2 ML Integration (`ml_integration.py`)

Uses machine learning to identify patterns and make predictions.

Technologies: scikit-learn for ML algorithms, numpy for numerical processing.

```python
# Key classes and functions in ml_integration.py
class PatternRecognizer:
    """Recognizes patterns in user behavior using ML"""
    
    def train_models(self, activity_data):
        """Train ML models on activity data"""
        # Preprocess activity data
        # Train clustering and classification models
        
    def detect_patterns(self, new_activities):
        """Detect patterns in new activities"""
        # Apply trained models to identify patterns
        # Calculate confidence scores
        # Return detected patterns with metadata
```

### 5. Automation Modules

#### 5.1 Automation Module (`automation_module.py`)

Records, manages, and executes automation sequences.

Technologies: pynput for input simulation, custom scripting engine for automation.

```python
# Key functions in automation_module.py
def start_recording(self):
    """Start recording a new automation sequence"""
    # Set up event hooks for recording
    
def stop_recording(self, name=None):
    """Stop recording and save automation"""
    # Process and optimize recorded actions
    # Save to database
    
def execute_automation(self, automation_id):
    """Execute a recorded automation sequence"""
    # Load automation from database
    # Execute each step in sequence
    # Handle errors and exceptions
```

#### 5.2 Repetitive Task Suggestion (`repetitive_task_suggestion.py`)

Analyzes activity data to suggest automation opportunities.

Technologies: Custom pattern detection algorithms, statistical analysis.

```python
# Key functions in repetitive_task_suggestion.py
def analyze_activity_history(self, days=7):
    """Analyze activity history to find repetitive patterns"""
    # Query activity logs from database
    # Apply pattern detection algorithms
    # Calculate frequency, consistency, and complexity scores
    
def generate_suggestions(self, min_confidence=0.7):
    """Generate automation suggestions based on detected patterns"""
    # Filter patterns by confidence score
    # Create automation suggestions
    # Save suggestions to database
```

### 6. User Interface (`gui_interface.py`)

Creates and manages the floating sidebar and other UI elements.

Technologies: PyQt5 for GUI components, Qt Style Sheets for styling.

```python
# Key classes in gui_interface.py
class FloatingSidebar(QWidget):
    """Floating sidebar UI element"""
    
    def _setup_ui(self):
        """Set up the sidebar UI components"""
        # Create and arrange UI elements
        
    def update_content(self):
        """Update the sidebar content with latest data"""
        # Update activity display
        # Update suggestions
        # Update automation status
```

## AI and Machine Learning Details

### 1. Pattern Recognition Algorithm

The system uses unsupervised learning to identify patterns in user behavior:

1. **Data Collection**: Records user activities with timestamps and context
2. **Feature Extraction**: 
   - Time-based features (time of day, day of week)
   - Sequence-based features (order of applications used)
   - Content-based features (types of documents worked on)
3. **Clustering**: Uses DBSCAN algorithm to identify clusters of similar activities
4. **Sequence Detection**: Applies modified Longest Common Subsequence (LCS) algorithm to detect repeated action sequences
5. **Confidence Scoring**: Calculates a confidence score based on:
   - Frequency of pattern occurrence
   - Consistency of the pattern
   - Recency of occurrences
   - Complexity of the pattern

Code location: `ml_integration.py` (pattern detection algorithms)

### 2. Text Analysis Pipeline

Text from screenshots is processed through a multi-stage pipeline:

1. **Text Extraction**: Tesseract OCR extracts text from screenshots
2. **Preprocessing**: Text is normalized, tokenized, and cleaned
3. **Entity Recognition**: Custom rules identify structured entities (emails, URLs, file paths)
4. **Application Identification**: Application-specific patterns detect what application is being used
5. **Content Classification**: Basic classification of content type (code, document, spreadsheet, etc.)
6. **Context Building**: Relationship between texts across time is established

Code location: `text_analyzer.py` (text processing pipeline)

### 3. Automation Suggestion Engine

The suggestion engine uses a combination of rule-based and statistical approaches:

1. **Pattern Selection**: Filters patterns based on:
   - Minimum frequency threshold
   - Minimum confidence score
   - Automation feasibility
2. **Benefit Analysis**: Estimates time savings based on:
   - Frequency of task
   - Average duration of task
   - Complexity of task
3. **Suggestion Generation**: Creates human-readable suggestions with:
   - Task description
   - Estimated time savings
   - Confidence score
   - Example occurrences

Code location: `repetitive_task_suggestion.py` (suggestion generation)

## Database Schema

The database schema is defined in `models.py` (or `fixed_models.py`):

1. **User**: Stores user information and settings
2. **Screenshot**: Stores metadata for captured screenshots
3. **ActivityLog**: Records user activities with timestamps
4. **AutomationTask**: Stores recorded automation sequences
5. **AutomationSuggestion**: Stores detected patterns and suggestions

Key relationships:
- User has many Screenshots, ActivityLogs, AutomationTasks, and AutomationSuggestions
- Screenshots have many ActivityLogs
- ActivityLogs can reference Screenshots

## Performance Considerations

The application is designed with performance in mind:

1. **Screenshot Optimization**:
   - Thumbnails are generated to reduce memory usage
   - Images are processed in a separate thread to prevent UI freezing
   
2. **Database Efficiency**:
   - Periodic cleanup removes old data
   - Indexes on frequently queried fields
   - Lazy loading of relationships
   
3. **Resource Management**:
   - Configurable capture intervals
   - Adaptive resource usage based on system load
   - Background processing of intensive tasks

## Future AI/ML Enhancements

Planned enhancements to the AI/ML capabilities:

1. **User Behavior Modeling**: Creating a comprehensive model of user work patterns to better predict needs
2. **Content Understanding**: Deeper analysis of screenshot content to understand the semantic meaning of user activities
3. **Predictive Assistance**: Proactively suggesting applications or files based on time of day and current context
4. **Anomaly Detection**: Identifying unusual patterns that may indicate security concerns or inefficient workflows
5. **Reinforcement Learning**: Improving automation suggestions based on user feedback and acceptance rates