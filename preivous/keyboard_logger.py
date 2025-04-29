from pynput import keyboard
from threading import Thread

# List of keys that trigger a screenshot
TRIGGER_KEYS = {keyboard.Key.enter, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r,
                keyboard.Key.tab, keyboard.Key.shift, keyboard.Key.cmd, keyboard.Key.cmd_r}

class KeyboardListener:
    def __init__(self, on_trigger_callback=None, on_text_submit=None):
        self.buffer = ''
        self.listener = None
        self.on_trigger = on_trigger_callback  # Called on trigger key
        self.on_text_submit = on_text_submit   # Called when Enter is pressed

    def _on_press(self, key):
        try:
            if hasattr(key, 'char') and key.char is not None:
                self.buffer += key.char
            elif key in TRIGGER_KEYS:
                if key == keyboard.Key.enter and self.on_text_submit:
                    self.on_text_submit(self.buffer)
                    self.buffer = ''
                if self.on_trigger:
                    self.on_trigger(key)
        except Exception as e:
            print(f"KeyboardListener error: {e}")

    def start(self):
        self.listener = keyboard.Listener(on_press=self._on_press)
        thread = Thread(target=self.listener.start)
        thread.daemon = True
        thread.start()

    def stop(self):
        if self.listener:
            self.listener.stop()

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
