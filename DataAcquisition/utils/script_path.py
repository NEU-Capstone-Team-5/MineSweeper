import os
from pathlib import Path

def get_script_dir(filepath):
    """Gets the directory of the current script."""
    return os.path.dirname(os.path.abspath(filepath))