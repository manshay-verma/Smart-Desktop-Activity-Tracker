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