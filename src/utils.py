import os


def create_output_directory(path='outputs'):
    """Create the output directory if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(path)


def add_homebrew_path():
    """Add Homebrew path to the environment if not included."""
    homebrew_path = '/opt/homebrew/bin'
    if homebrew_path not in os.environ['PATH']:
        os.environ['PATH'] += os.pathsep + homebrew_path
