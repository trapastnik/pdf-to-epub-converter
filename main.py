# main.py
import os
import fitz
import gradio as gr
from gradio import networking
from datetime import datetime
from config import UPLOAD_FOLDER, OUTPUT_FOLDER
from app.core.pdf_parser import AdvancedPDFParser
from app.core.text_processor import TextProcessor
from app.core.epub_generator import InteractiveEPUBCreator

# Disable analytics and configure environment
os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def convert_pdf_to_epub(pdf_file):
    """Handle PDF to EPUB conversion with proper cleanup"""
    temp_output_dir = None
    try:
        # Validate input
        if not pdf_file.name.lower().endswith(".pdf"):
            raise ValueError("Invalid file type. Please upload a PDF file")

        # Initialize components
        parser = AdvancedPDFParser()
        processor = TextProcessor()
        creator = InteractiveEPUBCreator()

        # Generate unique filename
        base_name = os.path.splitext(os.path.basename(pdf_file.name))[0]
        output_filename = f"{base_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.epub"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)

        # Process PDF
        with fitz.open(pdf_file.name) as doc:
            full_text = []
            for page in doc:
                layout_blocks = parser.parse_page(page)
                full_text.append('\n'.join([b['text'] for b in layout_blocks]))
            
            processed_text = processor.process('\n\n'.join(full_text))

        # Create EPUB
        creator.create_epub(processed_text, output_path)
        return output_path

    except Exception as e:
        gr.Error(f"Conversion failed: {str(e)}")
        # Cleanup temporary files on error
        if temp_output_dir and os.path.exists(temp_output_dir):
            shutil.rmtree(temp_output_dir)
        return None
    finally:
        # Always clean up the original upload
        if os.path.exists(pdf_file.name):
            os.remove(pdf_file.name)

def launch_app():
    """Configure and launch Gradio interface with port handling"""
    # Create Gradio interface
    iface = gr.Interface(
        fn=convert_pdf_to_epub,
        inputs=gr.File(label="Upload PDF", file_types=[".pdf"]),
        outputs=gr.File(label="Download EPUB"),
        title="PDF to EPUB Converter",
        description=(
            "Convert PDF documents to EPUB format with "
            "preserved structure and formatting"
        ),
        allow_flagging="never"
    )

    # Find available port
    try:
        port = networking.find_available_port(7860, 7870)
        print(f"* Running on local URL: http://0.0.0.0:{port}")
        return iface.launch(
            server_name="0.0.0.0",
            server_port=port,
            share=False,
            show_error=True
        )
    except Exception as e:
        print(f"Port error: {str(e)} - Using random port")
        return iface.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            show_error=True
        )

if __name__ == "__main__":
    launch_app()