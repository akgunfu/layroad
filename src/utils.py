import os
import shutil


class Icon:
    START = '\u23F3'  # Hourglass
    DONE = '\u2705'  # Green Checkmark
    ERROR = '\u274C'  # Red Cross
    DETECT = '\U0001F50D'  # Magnifying Glass


class TextColor:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'


def create_clean_output_directory(path='outputs'):
    """Create the output directory if it doesn't exist.
    If it exists and contains files, remove the files to ensure only latest outputs are kept."""
    if os.path.exists(path):
        # Remove all files in the directory
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
    else:
        os.makedirs(path)


def add_homebrew_path():
    """Add Homebrew path to the environment if not included."""
    homebrew_path = '/opt/homebrew/bin'
    if homebrew_path not in os.environ['PATH']:
        os.environ['PATH'] += os.pathsep + homebrew_path
