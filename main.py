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
