# config.py
import os

# Temporary directory for storing intermediate files
TEMP_DIR = "temp/"

# Upload folder for storing uploaded PDF files
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")

# Output folder for storing generated EPUB files
OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")

# Database settings (if using SQLite in the future)
DATABASE_URL = "sqlite:///./pdf_converter.db"