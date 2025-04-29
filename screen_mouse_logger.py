"""
Screen Mouse Logger Module
Captures screenshots and tracks mouse position
"""

import os
import time
import logging
import threading
import json
from datetime import datetime
import pyautogui
import cv2
import numpy as np
from PIL import Image, ImageDraw
import psutil
try:
    import win32gui
    import win32process
    WINDOWS = True
except ImportError:
    WINDOWS = False

from utils import setup_logging
from config import CONFIG

# Setup logging
logger = setup_logging()

class ScreenMouseLogger:
    """
    Captures screenshots and tracks mouse movements and clicks
    """
    def __init__(self, data_dir, shared_data):
        """
        Initialize the screen and mouse logger
        
        Args:
            data_dir (str): Directory to save screenshots and logs
            shared_data (dict): Shared data dictionary for inter-module communication
        """
        self.data_dir = data_dir
        self.shared_data = shared_data
        self.running = False
        self.screenshot_interval = CONFIG.get('screenshot_interval', 1)  # seconds
        self.click_screenshot = CONFIG.get('click_screenshot', True)  # Take screenshot on click
        
        # Create screenshot directory
        self.screenshots_dir = os.path.join(data_dir, "screenshots")
        if not os.path.exists(self.screenshots_dir):
            os.makedirs(self.screenshots_dir)
        
        # Mouse click listener thread
        self.click_listener = None
        self.mouse_movements = []
        self.last_position = (0, 0)
        self.last_click_time = 0
        
        # Active window detection
        self.last_active_window = ""
        
        logger.info("Screen Mouse Logger initialized")
    
    def start_monitoring(self):
        """Start monitoring screen and mouse activities"""
        logger.info("Starting screen and mouse monitoring")
        self.running = True
        
        # Start mouse click listener
        from pynput.mouse import Listener as MouseListener
        self.click_listener = MouseListener(on_click=self.on_click, on_move=self.on_move)
        self.click_listener.start()
        
        # Main monitoring loop
        while self.running:
            try:
                # Capture screenshot periodically
                self._capture_screenshot()
                
                # Get active window info
                self._detect_active_window()
                
                # Sleep for the interval
                time.sleep(self.screenshot_interval)
                
            except Exception as e:
                logger.error(f"Error in screen monitoring: {e}")
                time.sleep(1)  # Sleep on error to avoid tight loops
    
    def stop(self):
        """Stop monitoring"""
        logger.info("Stopping screen and mouse monitoring")
        self.running = False
        if self.click_listener:
            self.click_listener.stop()
    
    def on_click(self, x, y, button, pressed):
        """Mouse click event handler"""
        if not pressed or not self.running:
            return
        
        # Record click position
        click_time = time.time()
        click_position = (x, y)
        self.shared_data['mouse_position'] = click_position
        
        # Capture screenshot on click if enabled and not too frequent
        if self.click_screenshot and click_time - self.last_click_time > 0.5:
            self.last_click_time = click_time
            self._capture_screenshot(click_triggered=True, click_pos=click_position)
        
        # Log click event
        try:
            click_data = {
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                'position': click_position,
                'button': str(button),
                'active_window': self.shared_data.get('active_window', "")
            }
            
            click_log_file = os.path.join(self.data_dir, "mouse_clicks.json")
            
            # Append to file or create new one
            if os.path.exists(click_log_file):
                with open(click_log_file, 'r+') as f:
                    try:
                        data = json.load(f)
                        data.append(click_data)
                        f.seek(0)
                        json.dump(data, f, indent=2)
                    except json.JSONDecodeError:
                        # File is empty or corrupted
                        data = [click_data]
                        f.seek(0)
                        json.dump(data, f, indent=2)
            else:
                with open(click_log_file, 'w') as f:
                    json.dump([click_data], f, indent=2)
        
        except Exception as e:
            logger.error(f"Error logging click: {e}")
    
    def on_move(self, x, y):
        """Mouse movement event handler"""
        if not self.running:
            return
        
        # Update current position
        current_position = (x, y)
        self.shared_data['mouse_position'] = current_position
        
        # Record if significant movement (save memory by not recording tiny movements)
        prev_x, prev_y = self.last_position
        if abs(x - prev_x) > 10 or abs(y - prev_y) > 10:
            self.mouse_movements.append({
                'timestamp': time.time(),
                'position': current_position
            })
            self.last_position = current_position
            
            # Trim list if it gets too long
            if len(self.mouse_movements) > 1000:
                self.mouse_movements = self.mouse_movements[-1000:]
    
    def _capture_screenshot(self, click_triggered=False, click_pos=None):
        """
        Capture and save a screenshot
        
        Args:
            click_triggered (bool): Whether this screenshot was triggered by a click
            click_pos (tuple): Click position (x, y) if applicable
        """
        try:
            # Capture full screen
            screenshot = pyautogui.screenshot()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            
            # Save original screenshot
            screenshot_name = f"screenshot_{timestamp}{'_click' if click_triggered else ''}.png"
            screenshot_path = os.path.join(self.screenshots_dir, screenshot_name)
            screenshot.save(screenshot_path)
            
            # Update shared data with the latest screenshot path
            self.shared_data['last_screenshot_path'] = screenshot_path
            
            # If click triggered, also capture a region around the click
            if click_triggered and click_pos:
                x, y = click_pos
                # Crop area around click (300x300 pixels)
                crop_size = 150  # Radius around click
                left = max(0, x - crop_size)
                top = max(0, y - crop_size)
                right = min(screenshot.width, x + crop_size)
                bottom = min(screenshot.height, y + crop_size)
                
                # Crop and save
                crop_img = screenshot.crop((left, top, right, bottom))
                crop_name = f"click_area_{timestamp}.png"
                crop_path = os.path.join(self.screenshots_dir, crop_name)
                
                # Draw a marker at the click position (relative to crop)
                draw = ImageDraw.Draw(crop_img)
                rel_x, rel_y = x - left, y - top
                draw.ellipse((rel_x-5, rel_y-5, rel_x+5, rel_y+5), outline='red', width=2)
                
                crop_img.save(crop_path)
                self.shared_data['last_click_area_path'] = crop_path
            
            logger.debug(f"Screenshot captured: {screenshot_name}")
            
        except Exception as e:
            logger.error(f"Error capturing screenshot: {e}")
    
    def _detect_active_window(self):
        """Detect and record the currently active window"""
        try:
            if WINDOWS:
                # Get active window title and process on Windows
                hwnd = win32gui.GetForegroundWindow()
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                window_title = win32gui.GetWindowText(hwnd)
                
                try:
                    process = psutil.Process(pid)
                    process_name = process.name()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    process_name = "Unknown"
                
                active_window = f"{window_title} ({process_name})"
            else:
                # Simplified version for non-Windows platforms
                active_window = "Unknown (OS not supported)"
            
            # Update shared data if changed
            if active_window != self.last_active_window:
                self.last_active_window = active_window
                self.shared_data['active_window'] = active_window
                
                # Log window change
                window_change = {
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'window': active_window
                }
                
                window_log_file = os.path.join(self.data_dir, "window_changes.json")
                
                # Append to file or create new one
                if os.path.exists(window_log_file):
                    with open(window_log_file, 'r+') as f:
                        try:
                            data = json.load(f)
                            data.append(window_change)
                            f.seek(0)
                            json.dump(data, f, indent=2)
                        except json.JSONDecodeError:
                            data = [window_change]
                            f.seek(0)
                            json.dump(data, f, indent=2)
                else:
                    with open(window_log_file, 'w') as f:
                        json.dump([window_change], f, indent=2)
        
        except Exception as e:
            logger.error(f"Error detecting active window: {e}")
