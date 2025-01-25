import time
import subprocess
from pynput.keyboard import Controller as PynputController

from utils import ConfigManager

def run_command_or_exit_on_failure(command):
    """
    Run a shell command and exit if it fails.

    Args:
        command (list): The command to run as a list of strings.
    """
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        exit(1)

class InputSimulator:
    """
    A class to simulate keyboard input using various methods.
    """

    def __init__(self):
        """
        Initialize the InputSimulator with the specified configuration.
        """
        self.input_method = ConfigManager.get_config_value('post_processing', 'input_method')

        if self.input_method == 'pynput':
            self.keyboard = PynputController()

    def typewrite(self, text):
        """
        Simulate typing the given text with the specified interval between keystrokes.

        Args:
            text (str): The text to type.
        """
        interval = ConfigManager.get_config_value('post_processing', 'writing_key_press_delay') / 2
        try:
            if self.input_method == 'pynput':
                self._typewrite_pynput(text, interval)
        except Exception as e:
            print(f'Error during typewrite: {e}')

    def _typewrite_pynput(self, text, interval):
        """
        Simulate typing using pynput.

        Args:
            text (str): The text to type.
            interval (float): The interval between keystrokes in seconds.
        """
        for char in text:
            self.keyboard.press(char)
            self.keyboard.release(char)
            time.sleep(interval)

    def stop(self):
        """Stop the input simulator."""
        # Add any necessary cleanup code here
        pass
