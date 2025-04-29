"""
Configuration Module
Defines global configuration settings for the Smart Desktop Activity Tracker
"""

import os
import json
import logging

# Default configuration
DEFAULT_CONFIG = {
    # Screenshot settings
    "screenshot_interval": 1,  # seconds
    "click_screenshot": True,  # Take screenshot on click
    "screenshot_max_count": 3000,  # Maximum number of screenshots to keep
    
    # Keyboard logger settings
    "keyboard_buffer_size": 100,  # Number of keystrokes to buffer
    "keyboard_privacy_mode": True,  # Mask sensitive input
    "keyboard_save_interval": 60,  # seconds
    
    # Text analyzer settings
    "text_analysis_interval": 2,  # seconds
    "window_detection_enabled": True,  # Enable window detection in screenshots
    
    # GUI settings
    "sidebar_width": 350,  # pixels
    "sidebar_height": 600,  # pixels
    "sidebar_opacity": 0.85,  # 0-1
    "sidebar_auto_hide": False,  # Auto hide sidebar when inactive
    "sidebar_position": "right",  # 'left' or 'right'
    
    # Data storage settings
    "keep_history_days": 7,  # Number of days to keep data
    
    # Tesseract OCR path (Windows-specific)
    "pytesseract_path": r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    
    # Automation settings
    "suggestion_threshold": 0.6,  # Minimum confidence for suggestions
    "pattern_min_occurrences": 3,  # Minimum occurrences to detect a pattern
}

# Path to the configuration file
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'config.json')

def load_config():
    """
    Load configuration from file or use defaults
    
    Returns:
        dict: Configuration dictionary
    """
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
            
            # Update with any missing default values
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
            
            return config
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Error loading configuration file: {e}")
            return DEFAULT_CONFIG.copy()
    else:
        # Create default configuration file
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        try:
            with open(CONFIG_PATH, 'w') as f:
                json.dump(DEFAULT_CONFIG, f, indent=2)
        except IOError as e:
            logging.error(f"Error creating configuration file: {e}")
        
        return DEFAULT_CONFIG.copy()

def save_config(config):
    """
    Save configuration to file
    
    Args:
        config (dict): Configuration dictionary
    
    Returns:
        bool: Success status
    """
    try:
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except (TypeError, IOError) as e:
        logging.error(f"Error saving configuration file: {e}")
        return False

def update_config(key, value):
    """
    Update a configuration value
    
    Args:
        key (str): Configuration key
        value (any): New value
    
    Returns:
        bool: Success status
    """
    config = load_config()
    config[key] = value
    return save_config(config)

# Load configuration on module import
CONFIG = load_config()