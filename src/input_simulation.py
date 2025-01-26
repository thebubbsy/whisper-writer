import time
import subprocess
from PyQt5.QtCore import QTimer
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

    def __init__(self, transparent_window):
        """
        Initialize the InputSimulator with the specified configuration.
        """
        self.transparent_window = transparent_window
        self.input_method = ConfigManager.get_config_value('post_processing', 'input_method')

    def typewrite(self, text):
        """
        Simulate typing the given text with the specified interval between keystrokes.

        Args:
            text (str): The text to type.
        """
        self.transparent_window.display_text(text)

    def stop(self):
        """Stop the input simulator."""
        # Add any necessary cleanup code here
        pass
