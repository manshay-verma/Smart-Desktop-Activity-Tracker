#!/usr/bin/env python3
"""
Utility Functions Module
Provides common utility functions for the Smart Desktop Activity Tracker
"""

import os
import json
import logging
import re
from datetime import datetime
import tempfile

def setup_logging(log_level=logging.INFO):
    """
    Setup logging configuration
    
    Args:
        log_level (int, optional): Logging level (default: INFO)
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.expanduser("~"), ".smart_desktop_tracker", "logs")
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir, exist_ok=True)
    
    # Log file path with timestamp
    log_file = os.path.join(logs_dir, f"smart_desktop_tracker_{datetime.now().strftime('%Y%m%d')}.log")
    
    # Configure logging
    logger = logging.getLogger("smart_desktop_tracker")
    logger.setLevel(log_level)
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # Formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger

def create_data_dirs():
    """
    Create necessary data directories
    
    Returns:
        str: Path to the main data directory
    """
    # Base data directory
    base_dir = os.path.join(os.path.expanduser("~"), ".smart_desktop_tracker")
    
    # Create base directory if it doesn't exist
    if not os.path.exists(base_dir):
        os.makedirs(base_dir, exist_ok=True)
    
    # Create subdirectories
    dirs = [
        "screenshots",
        "thumbnails",
        "logs",
        "models",
        "automations",
        "temp"
    ]
    
    for dir_name in dirs:
        dir_path = os.path.join(base_dir, dir_name)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
    
    return base_dir

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
        return default
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger = logging.getLogger("smart_desktop_tracker")
        logger.error(f"Error loading JSON file {file_path}: {e}")
        return default

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
        # Use atomic write pattern (write to temp file, then rename)
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.json', dir=os.path.dirname(file_path)) as tf:
            json.dump(data, tf, indent=2)
            temp_path = tf.name
        
        # Rename temp file to target file
        os.replace(temp_path, file_path)
        return True
    except Exception as e:
        logger = logging.getLogger("smart_desktop_tracker")
        logger.error(f"Error saving JSON file {file_path}: {e}")
        
        # Clean up temp file if it exists
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
        
        return False

def get_timestamp():
    """
    Get current timestamp in a consistent format
    
    Returns:
        str: Formatted timestamp
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_filename_timestamp():
    """
    Get current timestamp suitable for filenames
    
    Returns:
        str: Formatted timestamp for filenames
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def natural_sort_key(s):
    """
    Key function for natural sorting
    
    Args:
        s (str): String to convert to key
    
    Returns:
        list: Key for natural sorting
    """
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', str(s))]

def sanitize_filename(filename):
    """
    Sanitize a string to be used as a filename
    
    Args:
        filename (str): Original filename
    
    Returns:
        str: Sanitized filename
    """
    # Replace problematic characters
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', filename)
    
    # Trim spaces and dots at the end
    sanitized = sanitized.strip().rstrip('.')
    
    # Limit length
    if len(sanitized) > 255:
        base, ext = os.path.splitext(sanitized)
        sanitized = base[:255 - len(ext)] + ext
    
    # Ensure we have a valid filename
    if not sanitized:
        sanitized = "unnamed"
    
    return sanitized

def clean_text(text):
    """
    Clean and normalize text
    
    Args:
        text (str): Text to clean
    
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Replace multiple whitespace with a single space
    text = re.sub(r'\s+', ' ', text)
    
    # Remove non-printable characters
    text = ''.join(c for c in text if c.isprintable())
    
    # Trim
    return text.strip()

def is_valid_url(url):
    """
    Check if a string is a valid URL
    
    Args:
        url (str): URL to check
    
    Returns:
        bool: True if valid URL, False otherwise
    """
    url_pattern = re.compile(
        r'^(?:http|ftp)s?://'  # http://, https://, ftp://, ftps://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(url_pattern.match(url))

def get_file_size_display(size_bytes):
    """
    Get human-readable file size
    
    Args:
        size_bytes (int): Size in bytes
    
    Returns:
        str: Human-readable size
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB']
    i = 0
    
    while size_bytes >= 1024 and i < len(suffixes) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.2f} {suffixes[i]}"

def truncate_string(text, max_length=100, suffix="..."):
    """
    Truncate a string to a maximum length
    
    Args:
        text (str): Text to truncate
        max_length (int, optional): Maximum length
        suffix (str, optional): Suffix to add if truncated
    
    Returns:
        str: Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix