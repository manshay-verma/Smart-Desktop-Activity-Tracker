<<<<<<< HEAD
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
=======
import os
import time
import json
import threading
import pyautogui
import cv2
import numpy as np
from datetime import datetime
from pynput import mouse
import win32gui
from pynput import keyboard
from keyboard_logger import KeyboardListener  # Import the KeyboardListener class

# === CONFIG ===
LOG_ONLY_FOR_WINDOWS = ["Chrome", "Notepad"]  # Add any window names you want to monitor
DELETE_OLDER_THAN_DAYS = 3
IMAGE_QUALITY = 60
AUTO_SCREENSHOT_INTERVAL = 15  # seconds (changed from 5 to 15 as requested)
# ==============

class EnhancedScreenLogger:
    def __init__(self, log_dir="screen_logs"):
        self.log_dir = log_dir
        self.running = False
        self.last_mouse_pos = None
        self.mouse_coords_json = {}
        self.key_state = {
            keyboard.Key.ctrl_l: False,
            keyboard.Key.ctrl_r: False,
            keyboard.Key.shift: False,
            keyboard.Key.shift_r: False,
            keyboard.Key.cmd: False,     # Windows key left
            keyboard.Key.cmd_r: False,   # Windows key right
            keyboard.Key.tab: False,
            keyboard.Key.esc: False
        }
        self.keyboard_buffer = ""
        self.last_screenshot_time = time.time()
        self.screenshot_cooldown = 0.5  # seconds
        self._ensure_directories()
        
    def _ensure_directories(self):
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def _get_active_window_title(self):
        try:
            window = win32gui.GetForegroundWindow()
            return win32gui.GetWindowText(window)
        except Exception:
            return "UnknownWindow"

    def _capture_screen(self):
        screenshot = pyautogui.screenshot()
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        return frame

    def _save_screenshot(self, frame, tag="", x=None, y=None, key_combo=None):
        """Save screenshot with additional metadata for key combinations"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.log_dir, f"{timestamp}_{tag}.jpg")
        cv2.imwrite(filename, frame, [int(cv2.IMWRITE_JPEG_QUALITY), IMAGE_QUALITY])

        # Store coordinates and metadata with screenshot
        metadata = {
            "x": x,
            "y": y,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "window": self._get_active_window_title(),
            "keyboard_buffer": self.keyboard_buffer,
            "trigger": tag
        }
        
        # Add key combination if available
        if key_combo:
            metadata["key_combination"] = key_combo
            
        self.mouse_coords_json[os.path.basename(filename)] = metadata

        print(f"[📸] Screenshot taken: {filename} ({tag})")
        return filename

    def _delete_old_files(self):
        now = time.time()
        for file in os.listdir(self.log_dir):
            path = os.path.join(self.log_dir, file)
            if os.path.isfile(path) and file.endswith(".jpg"):
                file_time = os.path.getmtime(path)
                if (now - file_time) > DELETE_OLDER_THAN_DAYS * 86400:
                    os.remove(path)
                    print(f"[🧹] Deleted old screenshot: {file}")

    def _should_log_window(self):
        """Check if the current window should be logged based on config"""
        if not LOG_ONLY_FOR_WINDOWS:  # If empty list, log all windows
            return True
            
        window_title = self._get_active_window_title()
        return any(name.lower() in window_title.lower() for name in LOG_ONLY_FOR_WINDOWS)

    def _log_click_action(self, x, y, click_type):
        """Log mouse click action with screenshots"""
        if not self._should_log_window():
            return

        # Avoid taking screenshots too quickly
        current_time = time.time()
        if current_time - self.last_screenshot_time < self.screenshot_cooldown:
            return
            
        self.last_screenshot_time = current_time
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {click_type} at ({x}, {y}) on '{self._get_active_window_title()}'")

        # Screenshot before click
        before_frame = self._capture_screen()
        self._save_screenshot(before_frame, tag=f"{click_type}_before", x=x, y=y)

        # Wait briefly to capture UI response
        time.sleep(0.3)  # Reduced from 0.8 to be more responsive

        # Screenshot after click
        after_frame = self._capture_screen()
        self._save_screenshot(after_frame, tag=f"{click_type}_after", x=x, y=y)

    def _on_click(self, x, y, button, pressed):
        """Handle mouse click events"""
        if pressed:
            click_type = "LeftClick" if button.name == "left" else "RightClick"
            self._log_click_action(x, y, click_type)

    def _on_scroll(self, x, y, dx, dy):
        """Handle mouse scroll events"""
        if not self._should_log_window():
            return

        # Avoid taking screenshots too quickly
        current_time = time.time()
        if current_time - self.last_screenshot_time < self.screenshot_cooldown:
            return
            
        self.last_screenshot_time = current_time
        
        scroll_dir = "down" if dy < 0 else "up"
        frame = self._capture_screen()
        self._save_screenshot(frame, tag=f"Scroll_{scroll_dir}", x=x, y=y)

    def _periodic_screenshot(self):
        """Take screenshots at regular intervals"""
        while self.running:
            current_time = time.time()
            time_since_last = current_time - self.last_screenshot_time
            
            if time_since_last >= AUTO_SCREENSHOT_INTERVAL and self._should_log_window():
                frame = self._capture_screen()
                x, y = pyautogui.position()
                self._save_screenshot(frame, tag="Periodic", x=x, y=y)
                self.last_screenshot_time = current_time
                
            time.sleep(1)  # Check every second but only capture based on interval

    def _keyboard_trigger_handler(self, key):
        """Handle keyboard trigger events from KeyboardListener"""
        try:
            # Update key state for the pressed key
            if key in self.key_state:
                self.key_state[key] = True
                
            # Check if combination of keys is pressed
            pressed_keys = [k for k, v in self.key_state.items() if v]
            if len(pressed_keys) >= 2:  # Require at least 2 special keys pressed together
                if not self._should_log_window():
                    return
                
                # Create a descriptive key combination string
                key_combo = "+".join(str(k).replace("Key.", "") for k in pressed_keys)
                
                # Avoid taking screenshots too quickly
                current_time = time.time()
                if current_time - self.last_screenshot_time < self.screenshot_cooldown:
                    return
                    
                self.last_screenshot_time = current_time
                
                # Take screenshot for key combination
                frame = self._capture_screen()
                x, y = pyautogui.position()
                self._save_screenshot(frame, tag=f"KeyCombo", x=x, y=y, key_combo=key_combo)
                
                # Debug output
                print(f"[⌨️] Key combination detected: {key_combo}")
                
        except Exception as e:
            print(f"Error in keyboard trigger handler: {e}")
            
    def _key_release_handler(self, key):
        """Handle key release events to track key state"""
        try:
            if key in self.key_state:
                self.key_state[key] = False
        except Exception as e:
            print(f"Error in key release handler: {e}")

    def _text_submit_handler(self, text):
        """Handle text submission (when Enter is pressed)"""
        self.keyboard_buffer = text
        print(f"[⌨️] Text submitted: {text[:30]}..." if len(text) > 30 else f"[⌨️] Text submitted: {text}")

    def start(self):
        """Start the enhanced screen logger"""
        print("[*] Starting enhanced screen, mouse, and keyboard logger...")
        self._delete_old_files()
        self.running = True
        self.last_screenshot_time = time.time()

        # Start periodic screenshot thread
        threading.Thread(target=self._periodic_screenshot, daemon=True).start()
        
        # Set up mouse listener
        mouse_listener = mouse.Listener(
            on_click=self._on_click,
            on_scroll=self._on_scroll
        )
        mouse_listener.start()
        
        # Set up keyboard listener for release events (separate from KeyboardListener)
        key_release_listener = keyboard.Listener(on_release=self._key_release_handler)
        key_release_listener.start()
        
        # Set up KeyboardListener from the imported module
        keyboard_listener = KeyboardListener(
            on_trigger_callback=self._keyboard_trigger_handler,
            on_text_submit=self._text_submit_handler
        )
        keyboard_listener.start()

        try:
            print("[*] Logger running. Press Ctrl+C to stop.")
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()
            mouse_listener.stop()
            key_release_listener.stop()
            keyboard_listener.stop()
            self.save_json_log()

    def stop(self):
        """Stop the logger"""
        self.running = False
        print("[*] Logger stopped.")

    def save_json_log(self):
        """Save the log data to a JSON file"""
        json_path = os.path.join(self.log_dir, "activity_log.json")
        with open(json_path, "w") as f:
            json.dump(self.mouse_coords_json, f, indent=4)
        print(f"[*] Activity log saved at {json_path}")


if __name__ == "__main__":
    logger = EnhancedScreenLogger()
    logger.start()
>>>>>>> 6fe9b61b92db2138ce1f5c366e25b24ae028ead1
