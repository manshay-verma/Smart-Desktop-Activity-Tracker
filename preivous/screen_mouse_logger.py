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

# === CONFIG ===
LOG_ONLY_FOR_WINDOWS = ["Chrome", "Notepad"]
DELETE_OLDER_THAN_DAYS = 3
IMAGE_QUALITY = 60
SCREENSHOT_INTERVAL = 5  # seconds
# ==============

class ScreenMouseLogger:
    def __init__(self, log_dir="screen_logs"):
        self.log_dir = log_dir
        self.running = False
        self.last_mouse_pos = None
        self.mouse_coords_json = {}
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

    def _save_screenshot(self, frame, tag="", x=None, y=None):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.log_dir, f"{timestamp}_{tag}.jpg")
        cv2.imwrite(filename, frame, [int(cv2.IMWRITE_JPEG_QUALITY), IMAGE_QUALITY])

        # Store mouse coordinates with screenshot
        self.mouse_coords_json[os.path.basename(filename)] = {
            "x": x,
            "y": y,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "window": self._get_active_window_title()
        }

        print(f"[📸] Screenshot taken: {filename}")
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

    def _log_click_action(self, x, y, click_type):
        window_title = self._get_active_window_title()
        if not any(name.lower() in window_title.lower() for name in LOG_ONLY_FOR_WINDOWS):
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {click_type} at ({x}, {y}) on '{window_title}'")

        # Screenshot before click
        before_frame = self._capture_screen()
        self._save_screenshot(before_frame, tag=f"{click_type}_before", x=x, y=y)

        # Wait briefly to capture UI response
        time.sleep(0.8)

        # Screenshot after click
        after_frame = self._capture_screen()
        self._save_screenshot(after_frame, tag=f"{click_type}_after", x=x, y=y)

    def _on_click(self, x, y, button, pressed):
        if pressed:
            click_type = "LeftClick" if button.name == "left" else "RightClick"
            self._log_click_action(x, y, click_type)

    def _periodic_screenshot(self):
        while self.running:
            window_title = self._get_active_window_title()
            if any(name.lower() in window_title.lower() for name in LOG_ONLY_FOR_WINDOWS):
                frame = self._capture_screen()
                x, y = pyautogui.position()
                self._save_screenshot(frame, tag="Periodic", x=x, y=y)
            time.sleep(SCREENSHOT_INTERVAL)

    def start(self):
        print("[*] Starting screen and mouse logger...")
        self._delete_old_files()
        self.running = True

        threading.Thread(target=self._periodic_screenshot, daemon=True).start()
        listener = mouse.Listener(on_click=self._on_click)
        listener.start()

        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()
            listener.stop()
            self.save_json_log()

    def stop(self):
        self.running = False
        print("[*] Logger stopped.")

    def save_json_log(self):
        json_path = os.path.join(self.log_dir, "mouse_coords.json")
        with open(json_path, "w") as f:
            json.dump(self.mouse_coords_json, f, indent=4)
        print(f"[*] Mouse coordinates JSON saved at {json_path}")


if __name__ == "__main__":
    logger = ScreenMouseLogger()
    logger.start()
