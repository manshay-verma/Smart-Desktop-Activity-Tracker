"""
Automation Module
Records and executes automation macros
"""

import os
import time
import logging
import json
import threading
from datetime import datetime
import pyautogui
from pynput import mouse, keyboard

from utils import setup_logging
from config import CONFIG

# Setup logging
logger = setup_logging()

class AutomationModule:
    """
    Records and executes automation macros for repetitive tasks
    """
    def __init__(self, data_dir, shared_data):
        """
        Initialize the automation module
        
        Args:
            data_dir (str): Directory for automation data
            shared_data (dict): Shared data dictionary for inter-module communication
        """
        self.data_dir = data_dir
        self.shared_data = shared_data
        
        # Create automation directory
        self.automation_dir = os.path.join(data_dir, "automation")
        if not os.path.exists(self.automation_dir):
            os.makedirs(self.automation_dir)
        
        # Recording state
        self.recording = False
        self.current_recording = []
        self.recording_start_time = 0
        
        # Mouse and keyboard listeners
        self.mouse_listener = None
        self.keyboard_listener = None
        
        # Stored automations
        self.automations = {}
        self._load_existing_automations()
        
        logger.info("Automation Module initialized")
    
    def start_recording(self):
        """
        Start recording a new automation macro
        
        Returns:
            bool: Success status
        """
        if self.recording:
            logger.warning("Already recording an automation")
            return False
        
        logger.info("Starting automation recording")
        self.recording = True
        self.current_recording = []
        self.recording_start_time = time.time()
        
        # Start mouse and keyboard listeners
        self.mouse_listener = mouse.Listener(
            on_click=self._on_record_click,
            on_scroll=self._on_record_scroll
        )
        self.keyboard_listener = keyboard.Listener(
            on_press=self._on_record_key_press,
            on_release=self._on_record_key_release
        )
        
        self.mouse_listener.start()
        self.keyboard_listener.start()
        
        # Update shared data
        self.shared_data['recording_automation'] = True
        
        return True
    
    def stop_recording(self, name=None):
        """
        Stop recording and save the automation
        
        Args:
            name (str, optional): Name for the automation. If None, a timestamp will be used
        
        Returns:
            dict: Recorded automation data
        """
        if not self.recording:
            logger.warning("Not currently recording an automation")
            return None
        
        logger.info("Stopping automation recording")
        self.recording = False
        
        # Stop listeners
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
        
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None
        
        # Update shared data
        self.shared_data['recording_automation'] = False
        
        # Generate automation name if not provided
        if not name:
            name = f"Automation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create automation data
        automation = {
            'name': name,
            'created': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'duration': time.time() - self.recording_start_time,
            'steps': self.current_recording
        }
        
        # Save to file
        self._save_automation(name, automation)
        
        # Add to in-memory store
        self.automations[name] = automation
        
        # Reset current recording
        self.current_recording = []
        
        return automation
    
    def execute_automation(self, automation_id):
        """
        Execute a recorded automation
        
        Args:
            automation_id (str): Name or ID of the automation to execute
        
        Returns:
            bool: Success status
        """
        # Find the automation
        if automation_id not in self.automations:
            logger.error(f"Automation '{automation_id}' not found")
            return False
        
        automation = self.automations[automation_id]
        logger.info(f"Executing automation: {automation_id}")
        
        try:
            # Execute each step
            for step in automation['steps']:
                step_type = step.get('type')
                
                if step_type == 'mouse_click':
                    x, y = step['position']
                    button = step['button']
                    # Convert string button name to pyautogui button
                    if button == 'Button.left':
                        pyautogui.click(x, y, button='left')
                    elif button == 'Button.right':
                        pyautogui.click(x, y, button='right')
                    elif button == 'Button.middle':
                        pyautogui.click(x, y, button='middle')
                
                elif step_type == 'mouse_scroll':
                    x, y = step['position']
                    dx, dy = step['scroll']
                    # Move to position first
                    pyautogui.moveTo(x, y)
                    # Then scroll
                    pyautogui.scroll(int(dy * 100))  # Adjust scroll amount
                
                elif step_type == 'key_press':
                    key = step['key']
                    # Handle special keys
                    if key.startswith('Key.'):
                        key_name = key.replace('Key.', '')
                        # Map to pyautogui key names
                        key_mapping = {
                            'space': 'space',
                            'enter': 'enter',
                            'tab': 'tab',
                            'esc': 'escape',
                            'backspace': 'backspace',
                            'delete': 'delete',
                            'up': 'up',
                            'down': 'down',
                            'left': 'left',
                            'right': 'right'
                        }
                        if key_name in key_mapping:
                            pyautogui.press(key_mapping[key_name])
                    else:
                        # Regular character
                        pyautogui.press(key)
                
                elif step_type == 'key_text':
                    # Type a full string at once (more efficient)
                    pyautogui.typewrite(step['text'])
                
                # Wait between steps
                time.sleep(step.get('delay', 0.05))
            
            logger.info(f"Automation '{automation_id}' executed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error executing automation '{automation_id}': {e}")
            return False
    
    def get_automations(self):
        """
        Get all available automations
        
        Returns:
            dict: Dictionary of automation data
        """
        return self.automations
    
    def delete_automation(self, automation_id):
        """
        Delete an automation
        
        Args:
            automation_id (str): Name or ID of the automation to delete
        
        Returns:
            bool: Success status
        """
        if automation_id not in self.automations:
            logger.error(f"Automation '{automation_id}' not found")
            return False
        
        # Remove from memory
        del self.automations[automation_id]
        
        # Remove from disk
        file_path = os.path.join(self.automation_dir, f"{automation_id}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Automation '{automation_id}' deleted")
            return True
        else:
            logger.warning(f"Automation file for '{automation_id}' not found")
            return False
    
    def _on_record_click(self, x, y, button, pressed):
        """Record mouse clicks during automation recording"""
        if not self.recording or not pressed:
            return
        
        # Add click event to recording
        self.current_recording.append({
            'type': 'mouse_click',
            'position': (x, y),
            'button': str(button),
            'time': time.time() - self.recording_start_time
        })
    
    def _on_record_scroll(self, x, y, dx, dy):
        """Record mouse scrolls during automation recording"""
        if not self.recording:
            return
        
        # Add scroll event to recording
        self.current_recording.append({
            'type': 'mouse_scroll',
            'position': (x, y),
            'scroll': (dx, dy),
            'time': time.time() - self.recording_start_time
        })
    
    def _on_record_key_press(self, key):
        """Record key presses during automation recording"""
        if not self.recording:
            return
        
        # Add key press event to recording
        if hasattr(key, 'char') and key.char:
            # For regular character keys
            self.current_recording.append({
                'type': 'key_press',
                'key': key.char,
                'time': time.time() - self.recording_start_time
            })
        else:
            # For special keys
            self.current_recording.append({
                'type': 'key_press',
                'key': str(key),
                'time': time.time() - self.recording_start_time
            })
    
    def _on_record_key_release(self, key):
        """Record key releases during automation recording"""
        if not self.recording:
            return
        
        # Currently we don't need to record key releases
        # But the method is here for potential future use
        pass
    
    def _optimize_recording(self):
        """
        Optimize the recording by combining consecutive key presses into text
        """
        if not self.current_recording:
            return
        
        optimized = []
        current_text = ""
        last_time = None
        
        for step in self.current_recording:
            if step['type'] == 'key_press' and len(step['key']) == 1:
                # Regular character that can be part of text
                if last_time is None or step['time'] - last_time < 0.5:  # 0.5 second threshold
                    current_text += step['key']
                    last_time = step['time']
                else:
                    # Time gap too large, add as new text
                    if current_text:
                        optimized.append({
                            'type': 'key_text',
                            'text': current_text,
                            'time': step['time'] - len(current_text) * 0.05  # Approximate start time
                        })
                        current_text = step['key']
                        last_time = step['time']
            else:
                # Other event type, flush current text first
                if current_text:
                    optimized.append({
                        'type': 'key_text',
                        'text': current_text,
                        'time': step['time'] - len(current_text) * 0.05  # Approximate start time
                    })
                    current_text = ""
                    last_time = None
                
                # Add the current step
                optimized.append(step)
        
        # Add any remaining text
        if current_text:
            optimized.append({
                'type': 'key_text',
                'text': current_text,
                'time': time.time() - self.recording_start_time  # End time
            })
        
        # Calculate delays between steps
        for i in range(1, len(optimized)):
            optimized[i]['delay'] = optimized[i]['time'] - optimized[i-1]['time']
        
        # First step has no delay
        if optimized:
            optimized[0]['delay'] = 0
        
        self.current_recording = optimized
    
    def _save_automation(self, name, automation):
        """
        Save automation to file
        
        Args:
            name (str): Automation name
            automation (dict): Automation data
        """
        try:
            # Optimize the recording first
            self._optimize_recording()
            
            # Update the automation with optimized steps
            automation['steps'] = self.current_recording
            
            # Save to file
            file_path = os.path.join(self.automation_dir, f"{name}.json")
            with open(file_path, 'w') as f:
                json.dump(automation, f, indent=2)
            
            logger.info(f"Automation '{name}' saved to {file_path}")
            
        except Exception as e:
            logger.error(f"Error saving automation '{name}': {e}")
    
    def _load_existing_automations(self):
        """Load existing automations from disk"""
        try:
            if not os.path.exists(self.automation_dir):
                return
            
            # Load each automation file
            for filename in os.listdir(self.automation_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.automation_dir, filename)
                    try:
                        with open(file_path, 'r') as f:
                            automation = json.load(f)
                            name = automation.get('name', filename[:-5])  # Remove .json
                            self.automations[name] = automation
                            logger.debug(f"Loaded automation: {name}")
                    except Exception as e:
                        logger.error(f"Error loading automation file {filename}: {e}")
            
            logger.info(f"Loaded {len(self.automations)} automations")
            
        except Exception as e:
            logger.error(f"Error loading automations: {e}")
