# app/core/utils.py
import os
import re
import shutil
import pyphen
from functools import lru_cache
from config import TEMP_DIR
from typing import Optional

# Hyphenation setup
@lru_cache(maxsize=None)
def get_hyphenator() -> Optional[pyphen.Pyphen]:
    """Cached hyphenator factory with error handling"""
    try:
        return pyphen.Pyphen(lang='ru')
    except Exception as e:
        print(f"Hyphenator initialization failed: {e}")
        return None

def apply_russian_hyphenation(text: str) -> str:
    """
    Applies soft hyphens to Russian text for proper EPUB hyphenation.
    Preserves original word boundaries for e-reader reflow.
    """
    hyphenator = get_hyphenator()
    if not hyphenator:
        return text
    
    try:
        return hyphenator.inserted(text, hyphen='\u00AD')  # SOFT HYPHEN (U+00AD)
    except Exception as e:
        print(f"Hyphenation error: {e}")
        return text

# Original file management functions
def sanitize_filename(filename: str) -> str:
    """Sanitizes filenames for safe filesystem use"""
    clean = re.sub(r'[\\/*?:"<>|]', "", filename)[:255]
    return clean.strip() if clean.strip() else "untitled"

def cleanup_temp_files(filepath: str) -> None:
    """Safely removes temporary directories"""
    try:
        temp_dir = os.path.join(filepath, TEMP_DIR)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    except Exception as e:
        print(f"Temp cleanup error: {e}")