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