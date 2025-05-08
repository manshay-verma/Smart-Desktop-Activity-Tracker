<<<<<<< HEAD
"""
Keyboard Logger Module
Captures keyboard input for activity tracking
"""

import os
import time
import logging
import threading
import json
from datetime import datetime
from pynput.keyboard import Key, Listener as KeyboardListener
import re

from utils import setup_logging
from config import CONFIG

# Setup logging
logger = setup_logging()

class KeyboardLogger:
    """
    Logs keyboard activity for understanding user tasks
    Uses secure buffering to avoid storing sensitive information
    """
    def __init__(self, data_dir, shared_data):
        """
        Initialize the keyboard logger
        
        Args:
            data_dir (str): Directory to save keyboard logs
            shared_data (dict): Shared data dictionary for inter-module communication
        """
        self.data_dir = data_dir
        self.shared_data = shared_data
        self.running = False
        
        # Key press buffer (only stores the most recent keystrokes in memory)
        self.key_buffer = []
        self.buffer_size = CONFIG.get('keyboard_buffer_size', 100)
        self.privacy_mode = CONFIG.get('keyboard_privacy_mode', True)
        
        # Special keys handling
        self.special_keys = {
            Key.space: " ",
            Key.enter: "\n",
            Key.tab: "\t",
            Key.backspace: "[BACKSPACE]"
        }
        
        # For privacy, exclude password and sensitive fields
        self.sensitive_contexts = [
            "password", "passwd", "pwd", "pin", "credit", "card", "ssn", "social",
            "birth", "security", "secret", "private", "login", "auth"
        ]
        
        # Keyboard listener
        self.keyboard_listener = None
        
        # Create logs directory
        self.keyboard_logs_dir = os.path.join(data_dir, "keyboard_logs")
        if not os.path.exists(self.keyboard_logs_dir):
            os.makedirs(self.keyboard_logs_dir)
        
        logger.info("Keyboard Logger initialized")
    
    def start_monitoring(self):
        """Start monitoring keyboard activities"""
        logger.info("Starting keyboard monitoring")
        self.running = True
        
        # Start keyboard listener
        self.keyboard_listener = KeyboardListener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        self.keyboard_listener.start()
        
        # Create a separate thread for periodic log saving
        self._save_thread = threading.Thread(target=self._periodic_save)
        self._save_thread.daemon = True
        self._save_thread.start()
        
        # Keep the thread running
        while self.running:
            time.sleep(0.1)
    
    def stop(self):
        """Stop monitoring"""
        logger.info("Stopping keyboard monitoring")
        self.running = False
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        
        # Save any remaining buffer content before stopping
        self._save_buffer()
    
    def on_key_press(self, key):
        """Key press event handler"""
        if not self.running:
            return
        
        try:
            # Convert the key to a string representation
            if hasattr(key, 'char') and key.char:
                key_str = key.char
            elif key in self.special_keys:
                key_str = self.special_keys[key]
            else:
                # Format other special keys nicely
                key_str = str(key).replace("Key.", "[") + "]"
            
            # Check if we're in a sensitive context and should mask input
            active_window = self.shared_data.get('active_window', '').lower()
            in_sensitive_context = any(term in active_window for term in self.sensitive_contexts)
            
            # Add to buffer
            if self.privacy_mode and in_sensitive_context:
                self.key_buffer.append("*")  # Mask sensitive input
            else:
                self.key_buffer.append(key_str)
            
            # Keep buffer at the specified size
            if len(self.key_buffer) > self.buffer_size:
                self.key_buffer = self.key_buffer[-self.buffer_size:]
            
            # Update the shared data with recent (limited) keystrokes
            # This is used by other modules like text analyzer
            buffer_text = ''.join(self.key_buffer[-30:])  # Only share last 30 chars
            self.shared_data['last_keys'] = buffer_text
            
        except Exception as e:
            logger.error(f"Error processing key press: {e}")
    
    def on_key_release(self, key):
        """Key release event handler"""
        pass  # Currently not needed, but kept for potential future use
    
    def _periodic_save(self):
        """Periodically save the key buffer to disk"""
        save_interval = CONFIG.get('keyboard_save_interval', 60)  # seconds
        
        while self.running:
            time.sleep(save_interval)
            self._save_buffer()
    
    def _save_buffer(self):
        """Save the current key buffer to a log file"""
        if not self.key_buffer:
            return  # Nothing to save
        
        try:
            # Create a timestamped log file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = os.path.join(self.keyboard_logs_dir, f"keyboard_log_{timestamp}.json")
            
            # Format the buffer content
            content = ''.join(self.key_buffer)
            
            # Create structured log entry
            log_entry = {
                'timestamp': timestamp,
                'active_window': self.shared_data.get('active_window', 'Unknown'),
                'content': content
            }
            
            # Save to file
            with open(log_file, 'w') as f:
                json.dump(log_entry, f, indent=2)
            
            logger.debug(f"Keyboard buffer saved to {log_file}")
            
            # Clear the buffer after saving
            self.key_buffer = []
            
        except Exception as e:
            logger.error(f"Error saving keyboard buffer: {e}")
    
    def get_last_text(self, chars=100):
        """
        Get the last N characters of text from the buffer
        
        Args:
            chars (int): Number of characters to retrieve
        
        Returns:
            str: Last N characters of text
        """
        buffer_text = ''.join(self.key_buffer[-chars:]) if self.key_buffer else ""
        return buffer_text
=======
from pynput import keyboard
from threading import Thread
import time

# List of keys that trigger a screenshot
TRIGGER_KEYS = {
    keyboard.Key.enter, 
    keyboard.Key.ctrl_l, 
    keyboard.Key.ctrl_r,
    keyboard.Key.tab, 
    keyboard.Key.shift,
    keyboard.Key.shift_r,
    keyboard.Key.cmd, 
    keyboard.Key.cmd_r,
    keyboard.Key.esc,
    keyboard.Key.alt_l,
    keyboard.Key.alt_r
}

class KeyboardListener:
    def __init__(self, on_trigger_callback=None, on_text_submit=None):
        self.buffer = ''
        self.listener = None
        self.on_trigger = on_trigger_callback  # Called on trigger key
        self.on_text_submit = on_text_submit   # Called when Enter is pressed
        self.pressed_keys = set()              # Track currently pressed keys
        self.key_state_listener = None

    def _on_press(self, key):
        try:
            # Add the key to pressed keys set
            if key in TRIGGER_KEYS:
                self.pressed_keys.add(key)
                
            # Handle regular text input
            if hasattr(key, 'char') and key.char is not None:
                self.buffer += key.char
                
            # Handle special keys
            elif key in TRIGGER_KEYS:
                # Submit text when Enter is pressed
                if key == keyboard.Key.enter and self.on_text_submit:
                    self.on_text_submit(self.buffer)
                    self.buffer = ''
                    
                # Call trigger callback for special keys
                if self.on_trigger:
                    self.on_trigger(key)
                    
        except Exception as e:
            print(f"KeyboardListener error on press: {e}")

    def _on_release(self, key):
        try:
            # Remove key from pressed keys set
            if key in self.pressed_keys:
                self.pressed_keys.remove(key)
        except Exception as e:
            print(f"KeyboardListener error on release: {e}")

    def get_pressed_keys(self):
        """Return currently pressed keys"""
        return self.pressed_keys

    def start(self):
        """Start the keyboard listener"""
        self.listener = keyboard.Listener(on_press=self._on_press)
        self.key_state_listener = keyboard.Listener(on_release=self._on_release)
        
        thread = Thread(target=self.listener.start)
        thread.daemon = True
        thread.start()
        
        state_thread = Thread(target=self.key_state_listener.start)
        state_thread.daemon = True
        state_thread.start()

    def stop(self):
        """Stop the keyboard listener"""
        if self.listener:
            self.listener.stop()
        if self.key_state_listener:
            self.key_state_listener.stop()

# Example usage in main.py:
# def handle_trigger(key):
#     print(f"Trigger key pressed: {key}")
#     capture_screenshot()  # or send event to a queue
#
# def handle_text_submit(text):
#     print(f"Submitted text: {text}")
#
# keyboard_listener = KeyboardListener(handle_trigger, handle_text_submit)
# keyboard_listener.start()
>>>>>>> 6fe9b61b92db2138ce1f5c366e25b24ae028ead1
