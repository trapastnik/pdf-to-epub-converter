# app/core/utils.py
import os
import re
import shutil
from config import TEMP_DIR

def sanitize_filename(filename):
    """
    Sanitizes a filename by removing invalid characters and ensuring it's suitable for use in a file system.
    """
    # Remove invalid characters
    filename = re.sub(r'[\\/*?:"<>|]', "", filename)

    # Truncate to a reasonable length (e.g., 255 characters)
    filename = filename[:255]

    # Ensure the filename is not empty or just whitespace
    if not filename or filename.isspace():
        filename = "untitled"

    return filename

def cleanup_temp_files(filepath):
    """
    Deletes the temporary directory and its contents.
    """
    try:
        temp_dir = os.path.join(filepath, TEMP_DIR)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    except Exception as e:
        print(f"Error cleaning up temporary files: {e}")