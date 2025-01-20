# main.py
import os
import gradio as gr
from app.routes import convert_pdf_to_epub
from config import UPLOAD_FOLDER, OUTPUT_FOLDER

# Create upload and output directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Define the Gradio interface
iface = gr.Interface(
    fn=convert_pdf_to_epub,
    inputs=gr.File(label="Upload PDF"),
    outputs=gr.File(label="Download EPUB"),
    title="PDF to EPUB Converter",
    description="Convert your PDF files to EPUB format with automatic structure recognition.",
    allow_flagging="never",  # Disables the flagging feature
)

# Launch the app
iface.launch()