from pynput import keyboard
import time

class KeyListener:
    """
    Simplified KeyListener using pynput to capture key combinations.
    """
    def __init__(self):
        self.listener = None
        self.callbacks = {
            "on_activate_typing_and_clipboard": []
        }
        self.last_activation_time = 0
        self.activation_delay = 1  # Minimum delay in seconds between activations

    def start(self):
        """Start the key listener."""
        try:
            self.listener = keyboard.GlobalHotKeys({
                '<ctrl>+<shift>+<alt>': self._on_hotkey_triggered
            })
            self.listener.start()
        except Exception as e:
            print(f'Error starting KeyListener: {e}')

    def stop(self):
        """Stop the key listener."""
        if self.listener:
            self.listener.stop()
            self.listener = None

    def _on_hotkey_triggered(self):
        """Callback for the key combination."""
        current_time = time.time()
        if current_time - self.last_activation_time >= self.activation_delay:
            self.last_activation_time = current_time
            self._trigger_callbacks("on_activate_typing_and_clipboard")

    def add_callback(self, event, callback):
        """Add a callback function for a specific event."""
        if event in self.callbacks:
            self.callbacks[event].append(callback)

    def _trigger_callbacks(self, event):
        for callback in self.callbacks.get(event, []):
            callback()

if __name__ == "__main__":
    key_listener = KeyListener()
    key_listener.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        key_listener.stop()
