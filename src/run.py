import os
import sys
import subprocess
from dotenv import load_dotenv

print('Starting WhisperWriter...')
load_dotenv()

try:
    subprocess.run([sys.executable, os.path.join('src', 'main.py')], shell=True, check=True)
except subprocess.CalledProcessError as e:
    print(f"Failed to start WhisperWriter: {e}")
    sys.exit(1)