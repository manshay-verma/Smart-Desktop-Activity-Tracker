#!/usr/bin/env python3
"""
Configuration Module
Defines global configuration settings for the Smart Desktop Activity Tracker
"""

import os
import json
from utils import load_json_file, save_json_file, create_data_dirs, setup_logging

# Setup logging
logger = setup_logging()

# Default configuration
CONFIG = {
    # General settings
    "app_name": "Smart Desktop Activity Tracker",
    "version": "1.0.0",
    
    # Data storage settings
    "data_dir": os.path.join(os.path.expanduser("~"), ".smart_desktop_tracker"),
    "screenshots_dir": "screenshots",
    "logs_dir": "logs",
    "keep_history_days": 7,  # Number of days to keep data
    
    # Screenshot settings
    "screenshot_on_window_change": True,
    "screenshot_on_idle_return": True,
    "screenshot_interval": 60,  # Seconds between periodic screenshots
    "screenshot_quality": 80,  # JPEG quality (0-100)
    "create_thumbnails": True,
    "thumbnail_size": (320, 180),  # Width, height
    "max_screenshots": 3000,  # Maximum number of screenshots to store
    
    # Privacy settings
    "keyboard_privacy_mode": True,  # Don't log keystrokes for passwords, etc.
    "privacy_blacklist": [
        "password", "login", "signin", "credit", "card", "bank", "account",
        "social security", "ssn", "secret", "private"
    ],
    "app_blacklist": [
        "keychain", "password", "vault", "bank", "wallet"
    ],
    
    # OCR settings
    "enable_ocr": True,
    "ocr_language": "eng",  # Language for Tesseract OCR
    
    # Automation settings
    "suggest_automations": True,
    "min_pattern_occurrences": 3,  # Minimum occurrences to suggest automation
    "suggestion_confidence_threshold": 0.6,  # Minimum confidence to show suggestions
    
    # Machine learning settings
    "ml_enabled": True,
    "training_interval_days": 7,  # Days between model retraining
    
    # UI settings
    "sidebar_opacity": 0.9,
    "auto_hide_sidebar": True,
    "sidebar_position": "right",  # left, right
    "theme": "system",  # light, dark, system
    
    # Internal settings (not exposed in UI)
    "_last_training": None,  # Timestamp of last ML model training
    "_db_version": 1,  # Database schema version
}

def load_config():
    """
    Load configuration from file or use defaults
    
    Returns:
        dict: Configuration dictionary
    """
    global CONFIG
    
    # Get data directory
    data_dir = CONFIG["data_dir"]
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
    
    # Config file path
    config_file = os.path.join(data_dir, "config.json")
    
    # Try to load from file
    loaded_config = load_json_file(config_file)
    
    if loaded_config:
        # Merge with defaults (to ensure new settings are included)
        for key, value in loaded_config.items():
            CONFIG[key] = value
        logger.info("Configuration loaded from file")
    else:
        # Save defaults to file
        save_config(CONFIG)
        logger.info("Default configuration created")
    
    return CONFIG

def save_config(config):
    """
    Save configuration to file
    
    Args:
        config (dict): Configuration dictionary
    
    Returns:
        bool: Success status
    """
    global CONFIG
    
    # Update global config
    CONFIG.update(config)
    
    # Get data directory
    data_dir = CONFIG["data_dir"]
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
    
    # Config file path
    config_file = os.path.join(data_dir, "config.json")
    
    # Save to file
    success = save_json_file(config_file, CONFIG)
    
    if success:
        logger.info("Configuration saved to file")
    else:
        logger.error("Failed to save configuration")
    
    return success

def update_config(key, value):
    """
    Update a configuration value
    
    Args:
        key (str): Configuration key
        value (any): New value
    
    Returns:
        bool: Success status
    """
    global CONFIG
    
    # Update the value
    CONFIG[key] = value
    
    # Save the updated configuration
    return save_config(CONFIG)

# Load configuration when module is imported
CONFIG = load_config()