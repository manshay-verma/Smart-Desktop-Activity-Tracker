#!/usr/bin/env python3
"""
Smart Desktop Activity Tracker
Main entry point that coordinates all modules
"""

import sys
import os
import time
import threading
import json
import logging
from datetime import datetime
import signal

# Import custom modules
from screen_mouse_logger import ScreenMouseLogger
from keyboard_logger import KeyboardLogger
from text_analyzer import TextAnalyzer
from automation_module import AutomationModule
from repetitive_task_suggestion import RepetitiveTaskSuggestion
from ml_integration import MLIntegration
from gui_interface import GUIInterface
from utils import create_data_dirs, setup_logging
from config import CONFIG

# Setup logging
logger = setup_logging()

class SmartDesktopTracker:
    """
    Main application class that coordinates all modules and manages the application lifecycle
    """
    def __init__(self):
        logger.info("Initializing Smart Desktop Tracker")
        
        # Create necessary directories
        self.data_dir = create_data_dirs()
        self.today_dir = os.path.join(self.data_dir, datetime.now().strftime("%Y-%m-%d"))
        if not os.path.exists(self.today_dir):
            os.makedirs(self.today_dir)
            
        # Initialize shared data structures
        self.shared_data = {
            'current_activity': "",
            'mouse_position': (0, 0),
            'active_window': "",
            'last_keys': "",
            'last_screenshot_path': "",
            'detected_apps': [],
            'automation_suggestions': [],
            'latest_ocr_text': ""
        }
        
        # Initialize modules
        logger.info("Initializing modules...")
        self.screen_mouse_logger = ScreenMouseLogger(self.today_dir, self.shared_data)
        self.keyboard_logger = KeyboardLogger(self.today_dir, self.shared_data)
        self.text_analyzer = TextAnalyzer(self.today_dir, self.shared_data)
        self.automation_module = AutomationModule(self.today_dir, self.shared_data)
        self.task_suggestion = RepetitiveTaskSuggestion(self.today_dir, self.shared_data)
        self.ml_integration = MLIntegration(self.today_dir, self.shared_data)
        
        # Initialize GUI last (so it can display data from other modules)
        self.gui = GUIInterface(self.shared_data, self)
        
        # Thread management
        self.threads = []
        self.running = False
        
        # Register termination handler
        signal.signal(signal.SIGINT, self.terminate)
        signal.signal(signal.SIGTERM, self.terminate)
        
        logger.info("Smart Desktop Tracker initialized")
    
    def start(self):
        """Start all modules and begin monitoring"""
        logger.info("Starting Smart Desktop Tracker")
        self.running = True
        
        # Start each module in a separate thread
        self.threads.append(threading.Thread(target=self.screen_mouse_logger.start_monitoring))
        self.threads.append(threading.Thread(target=self.keyboard_logger.start_monitoring))
        self.threads.append(threading.Thread(target=self.text_analyzer.start_analysis))
        self.threads.append(threading.Thread(target=self.task_suggestion.start_monitoring))
        self.threads.append(threading.Thread(target=self.ml_integration.start))
        
        # Start all threads
        for thread in self.threads:
            thread.daemon = True
            thread.start()
        
        # Start the GUI (this will run in the main thread)
        self.gui.start()
        
        # Main loop - keep application running
        try:
            while self.running:
                # Update the shared data summary periodically
                self._update_summary()
                time.sleep(1)
        except KeyboardInterrupt:
            self.terminate()
    
    def _update_summary(self):
        """Update the activity summary for display in the GUI"""
        activity_summary = {
            'timestamp': datetime.now().strftime("%H:%M:%S"),
            'active_window': self.shared_data.get('active_window', "Unknown"),
            'detected_apps': self.shared_data.get('detected_apps', []),
            'latest_ocr_text': self.shared_data.get('latest_ocr_text', ""),
            'automation_suggestions': self.shared_data.get('automation_suggestions', [])
        }
        
        self.shared_data['activity_summary'] = activity_summary
        
        # Signal the GUI to update with new data
        if hasattr(self.gui, 'update_display'):
            self.gui.update_display()
    
    def terminate(self, signum=None, frame=None):
        """Stop all threads and terminate the application gracefully"""
        logger.info("Terminating Smart Desktop Tracker")
        self.running = False
        
        # Stop all module monitoring
        if hasattr(self.screen_mouse_logger, 'stop'):
            self.screen_mouse_logger.stop()
        
        if hasattr(self.keyboard_logger, 'stop'):
            self.keyboard_logger.stop()
        
        if hasattr(self.text_analyzer, 'stop'):
            self.text_analyzer.stop()
        
        if hasattr(self.gui, 'stop'):
            self.gui.stop()
        
        # Save any pending data
        self._save_session_data()
        
        logger.info("Smart Desktop Tracker terminated")
        sys.exit(0)
    
    def _save_session_data(self):
        """Save session data for later analysis"""
        try:
            session_file = os.path.join(self.today_dir, f"session_{datetime.now().strftime('%H-%M-%S')}.json")
            with open(session_file, 'w') as f:
                # Remove any non-serializable data
                save_data = {k: v for k, v in self.shared_data.items() 
                             if isinstance(v, (dict, list, str, int, float, bool)) or v is None}
                json.dump(save_data, f, indent=2)
            logger.info(f"Session data saved to {session_file}")
        except Exception as e:
            logger.error(f"Error saving session data: {e}")
    
    def execute_automation(self, automation_id):
        """Execute an automation task based on its ID"""
        return self.automation_module.execute_automation(automation_id)
    
    def record_new_automation(self):
        """Start recording a new automation sequence"""
        return self.automation_module.start_recording()
    
    def stop_recording_automation(self, name=None):
        """Stop recording automation and save it"""
        return self.automation_module.stop_recording(name)

if __name__ == "__main__":
    tracker = SmartDesktopTracker()
    tracker.start()
