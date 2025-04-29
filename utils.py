"""
Utility Functions Module
Provides common utility functions for the Smart Desktop Activity Tracker
"""

import os
import logging
import json
from datetime import datetime

def setup_logging(log_level=logging.INFO):
    """
    Setup logging configuration
    
    Args:
        log_level (int, optional): Logging level (default: INFO)
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger('smart_desktop_tracker')
    logger.setLevel(log_level)
    
    # Check if handlers already exist to avoid duplicates
    if not logger.handlers:
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(console_handler)
        
        # Create log directory if it doesn't exist
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Create file handler
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = os.path.join(log_dir, f'tracker_{today}.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        
        # Add file handler to logger
        logger.addHandler(file_handler)
    
    return logger

def create_data_dirs():
    """
    Create necessary data directories
    
    Returns:
        str: Path to the main data directory
    """
    # Get the directory of the current script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create main data directory
    data_dir = os.path.join(base_dir, 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Create dated directories to organize data
    today_dir = os.path.join(data_dir, datetime.now().strftime('%Y-%m-%d'))
    if not os.path.exists(today_dir):
        os.makedirs(today_dir)
    
    # Create subdirectories for different data types
    subdirs = ['screenshots', 'keyboard_logs', 'mouse_logs', 'window_logs', 'analysis']
    for subdir in subdirs:
        subdir_path = os.path.join(today_dir, subdir)
        if not os.path.exists(subdir_path):
            os.makedirs(subdir_path)
    
    return today_dir

def load_json_file(file_path, default=None):
    """
    Load data from a JSON file
    
    Args:
        file_path (str): Path to the JSON file
        default (any, optional): Default value if file doesn't exist or is invalid
    
    Returns:
        any: Loaded data or default value
    """
    if not os.path.exists(file_path):
        return default if default is not None else {}
    
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger = logging.getLogger('smart_desktop_tracker')
        logger.error(f"Error loading JSON from {file_path}: {e}")
        return default if default is not None else {}

def save_json_file(file_path, data):
    """
    Save data to a JSON file
    
    Args:
        file_path (str): Path to the JSON file
        data (any): Data to save
    
    Returns:
        bool: Success status
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except (TypeError, IOError) as e:
        logger = logging.getLogger('smart_desktop_tracker')
        logger.error(f"Error saving JSON to {file_path}: {e}")
        return False

def get_timestamp():
    """
    Get current timestamp in a consistent format
    
    Returns:
        str: Formatted timestamp
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

def get_filename_timestamp():
    """
    Get current timestamp suitable for filenames
    
    Returns:
        str: Formatted timestamp for filenames
    """
    return datetime.now().strftime('%Y%m%d_%H%M%S_%f')

def natural_sort_key(s):
    """
    Key function for natural sorting
    
    Args:
        s (str): String to convert to key
    
    Returns:
        list: Key for natural sorting
    """
    import re
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]