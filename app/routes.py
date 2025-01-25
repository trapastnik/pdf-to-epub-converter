# app/routes.py

import os
import tempfile
import fitz
import gradio as gr
from app.core.pdf_parser import parse_pdf
from app.core.epub_generator import create_epub
from app.core.structure_analyzer import analyze_structure
from app.core.utils import cleanup_temp_files
from config import UPLOAD_FOLDER, OUTPUT_FOLDER

def convert_pdf_to_epub(pdf_file):
    """
    Handles the PDF to EPUB conversion process.
    """
    print("Function called")
    temp_output_dir = None

    try:
        # Check if the uploaded file is a PDF
        if not pdf_file.name.lower().endswith(".pdf"):
            gr.Error("Invalid file type. Please upload a PDF file.")
            return None

        # Create a temporary directory for the output
        temp_output_dir = tempfile.mkdtemp()
        print("Created temporary output directory:", temp_output_dir)

        # Use the path directly
        file_path = pdf_file.name
        print("File path:", file_path)

        # Open the PDF file using the path from pdf_file.name
        doc = fitz.open(file_path)
        print("Open the PDF file")

        # Pass the doc object to parse_pdf
        parsed_pdf = parse_pdf(doc)  # Pass the fitz.Document object directly
        print("# Pass the doc object to parse_pdf")

        # Analyze the structure
        parsed_pdf = analyze_structure(parsed_pdf, doc)
        print("Analyze the structure")

        # Inspect the return value of analyze_structure
        print("Return value from analyze_structure:", parsed_pdf)
        print("Type of return value:", type(parsed_pdf))

        # Generate the EPUB
        epub_filename = os.path.splitext(os.path.basename(pdf_file.name))[0] + ".epub"
        epub_path = os.path.join(temp_output_dir, epub_filename)

        # Inspect arguments to create_epub
        print("epub_filename:", epub_filename)
        print("epub_path:", epub_path)

        create_epub(parsed_pdf, epub_path)
        print("Epub created")

        # Get the absolute path:
        absolute_epub_path = os.path.abspath(epub_path)
        print("Absolute EPUB path:", absolute_epub_path)

        return absolute_epub_path

    except Exception as e:
        # Handle errors and provide feedback to the user
        print(f"An error occurred during conversion: {e}")
        gr.Error(f"An error occurred during conversion: {e}")
        return None

    finally:
        # Clean up the temporary output directory if it exists
        if temp_output_dir:
            cleanup_temp_files(temp_output_dir)
            print("Cleaned up temporary output directory")