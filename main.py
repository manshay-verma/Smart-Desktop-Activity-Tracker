<<<<<<< HEAD
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
from db_manager import db_manager

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
        
        # Initialize database
        self.db = db_manager
        
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
        
        # Start periodic cleanup thread
        cleanup_thread = threading.Thread(target=self._periodic_cleanup)
        cleanup_thread.daemon = True
        self.threads.append(cleanup_thread)
        
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
        
        # Log the current activity to the database if it changed
        current_activity = self.shared_data.get('current_activity')
        if current_activity and current_activity != self.shared_data.get('last_logged_activity'):
            self.db.log_activity(
                'activity_update',
                description=current_activity,
                data={
                    'active_window': self.shared_data.get('active_window', ''),
                    'detected_apps': self.shared_data.get('detected_apps', [])
                }
            )
            self.shared_data['last_logged_activity'] = current_activity
    
    def _periodic_cleanup(self):
        """Run periodic cleanup of old data"""
        cleanup_interval = 3600  # 1 hour
        days_to_keep = CONFIG.get('keep_history_days', 7)
        
        while self.running:
            time.sleep(cleanup_interval)
            if self.running:  # Check again after sleep
                logger.info(f"Running periodic cleanup (keeping {days_to_keep} days of data)")
                self.db.cleanup_old_data(days=days_to_keep)
    
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
        
        if hasattr(self.task_suggestion, 'stop'):
            self.task_suggestion.stop()
        
        if hasattr(self.ml_integration, 'stop'):
            self.ml_integration.stop()
        
        if hasattr(self.gui, 'stop'):
            self.gui.stop()
        
        # Save any pending data
        self._save_session_data()
        
        # Close database connection
        if self.db:
            self.db.close()
        
        logger.info("Smart Desktop Tracker terminated")
        sys.exit(0)
    
    def _save_session_data(self):
        """Save session data for later analysis"""
        try:
            # Save to file
            session_file = os.path.join(self.today_dir, f"session_{datetime.now().strftime('%H-%M-%S')}.json")
            with open(session_file, 'w') as f:
                # Remove any non-serializable data
                save_data = {k: v for k, v in self.shared_data.items() 
                             if isinstance(v, (dict, list, str, int, float, bool)) or v is None}
                json.dump(save_data, f, indent=2)
            
            # Log session end to database
            self.db.log_activity(
                'session_end',
                description="Session ended",
                data={
                    'session_duration': time.time() - self.shared_data.get('session_start_time', time.time()),
                    'activity_count': len(self.shared_data.get('activity_history', [])),
                }
            )
            
            logger.info(f"Session data saved to {session_file}")
        except Exception as e:
            logger.error(f"Error saving session data: {e}")
    
    def execute_automation(self, automation_id):
        """Execute an automation task based on its ID"""
        result = self.automation_module.execute_automation(automation_id)
        
        # Update execution count in the database
        if result:
            self.db.update_automation_execution(automation_id)
            
            # Log the automation execution
            self.db.log_activity(
                'automation_execution',
                description=f"Executed automation task #{automation_id}",
                data={'automation_id': automation_id, 'success': True}
            )
        
        return result
    
    def record_new_automation(self):
        """Start recording a new automation sequence"""
        result = self.automation_module.start_recording()
        
        # Log the recording start
        if result:
            self.db.log_activity(
                'automation_recording',
                description="Started recording automation",
                data={'recording_start_time': time.time()}
            )
        
        return result
    
    def stop_recording_automation(self, name=None):
        """Stop recording automation and save it"""
        automation_data = self.automation_module.stop_recording(name)
        
        # Save to database if recording was successful
        if automation_data and isinstance(automation_data, dict):
            task_id = self.db.save_automation_task(
                name=automation_data.get('name', 'Unnamed Automation'),
                steps=automation_data.get('steps', []),
                description=automation_data.get('description', ''),
                triggers=automation_data.get('triggers', [])
            )
            
            # Log the recording completion
            self.db.log_activity(
                'automation_recording',
                description=f"Completed recording automation: {automation_data.get('name', 'Unnamed')}",
                data={
                    'automation_id': task_id,
                    'step_count': len(automation_data.get('steps', [])),
                    'recording_duration': time.time() - self.shared_data.get('recording_start_time', time.time())
                }
            )
        
        return automation_data
    
    def save_suggestion(self, title, description, confidence=0.0, pattern_data=None):
        """
        Save an automation suggestion to the database
        
        Args:
            title (str): Title of the suggestion
            description (str): Description of the suggestion
            confidence (float, optional): Confidence score (0-1)
            pattern_data (dict, optional): Data about the detected pattern
        
        Returns:
            int: ID of the created suggestion, or None on failure
        """
        suggestion_id = self.db.save_automation_suggestion(
            title=title,
            description=description,
            confidence=confidence,
            pattern_data=pattern_data
        )
        
        if suggestion_id:
            # Log the suggestion creation
            self.db.log_activity(
                'suggestion_created',
                description=f"Created automation suggestion: {title}",
                data={'suggestion_id': suggestion_id, 'confidence': confidence}
            )
        
        return suggestion_id
    
    def get_automation_tasks(self):
        """Get all automation tasks from the database"""
        return self.db.get_automation_tasks()
    
    def get_automation_suggestions(self, include_dismissed=False):
        """Get automation suggestions from the database"""
        return self.db.get_automation_suggestions(include_dismissed=include_dismissed)
    
    def get_recent_activities(self, limit=50):
        """Get recent activity logs from the database"""
        return self.db.get_recent_activities(limit=limit)

if __name__ == "__main__":
    tracker = SmartDesktopTracker()
    tracker.start()
=======
# main.py
from screen_mouse_logger import ScreenMouseLogger
#from files.keyboard_logger1 import KeyboardListener
import threading
import pyautogui

def main():
    logger = ScreenMouseLogger()

    def on_key_trigger(key):
        print(f"[🧠] Key trigger detected: {key}")
        frame = logger._capture_screen()
        x, y = pyautogui.position()
        logger._save_screenshot(frame, tag=f"Key_{key}", x=x, y=y)

    def on_text_submit(text):
        print(f"[💬] Submitted text: '{text}'")

    # Start keyboard listener with screenshot trigger
    keyboard_listener = KeyboardListener(on_trigger_callback=on_key_trigger,
                                         on_text_submit=on_text_submit)
    keyboard_listener.start()

    # Start mouse and screen logger in its own thread
    threading.Thread(target=logger.start, daemon=True).start()

    # Keep main thread alive
    try:
        while True:
            pass
    except KeyboardInterrupt:
        logger.stop()
        keyboard_listener.stop()
        logger.save_json_log()

if __name__ == "__main__":
    main()
>>>>>>> 6fe9b61b92db2138ce1f5c366e25b24ae028ead1
