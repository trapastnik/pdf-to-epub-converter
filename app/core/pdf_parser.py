# app/core/pdf_parser.py
from threading import Lock
import fitz
import pytesseract
from PIL import Image
import io
import os
from app.models import ParsedPDF, Chapter, Heading
from typing import List, Dict
from config import TEMP_DIR
import logging
from threading import Lock
import re


# In pdf_parser.py

os.environ['TESSDATA_PREFIX'] = '/opt/homebrew/share/tessdata/'
pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'

lock = Lock()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

PAGE_NUMBER_PATTERN = re.compile(r'^\s*\d+\s*$')  # Standalone numbers


class AdvancedPDFParser:
    def __init__(self):
        self.layout_config = {
            'header_threshold': 0.1,
            'footer_threshold': 0.9,
            'column_gap': 50
        }

    def parse_page(self, page: fitz.Page) -> list:
        blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_LIGATURES)["blocks"]
        processed = []
        for block in blocks:
            if self._is_header_footer(block, page):
                continue
            processed.append(self._process_block(block))
        return processed

    def _is_header_footer(self, block: dict, page: fitz.Page) -> bool:
        page_height = page.rect.height
        return (block['bbox'][1] < page_height * self.layout_config['header_threshold'] or
                block['bbox'][3] > page_height * self.layout_config['footer_threshold'])

    def _process_block(self, block: dict) -> dict:
        return {
            'text': '\n'.join([span['text'] for line in block['lines'] for span in line['spans']]),
            'bbox': block['bbox'],
            'style': self._detect_text_style(block)
        }

    def _detect_text_style(self, block: dict) -> str:
        for line in block['lines']:
            for span in line['spans']:
                if span['size'] > 14 or 'bold' in span['font'].lower():
                    return 'heading'
        return 'body'

def extract_text_from_pdf(doc: fitz.Document) -> str:
    """Enhanced text extraction with page number filtering"""
    text = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        page_text = page.get_text("text", flags=fitz.TEXT_PRESERVE_LIGATURES)
        
        # Remove standalone page numbers
        cleaned_lines = [
            line for line in page_text.split('\n')
            if not PAGE_NUMBER_PATTERN.match(line.strip())
        ]
        
        text.append('\n'.join(cleaned_lines))
    
    return "\n\n".join(text)

    
def extract_image_from_page(page: fitz.Page, page_num: int, doc: fitz.Document) -> str:
    """
    Extracts an image from a page and saves it to a temporary directory.

    Args:
        page: The fitz.Page object.
        page_num: The page number.
        doc: The fitz.Document object

    Returns:
        The path to the saved image.
    """
    image_list = page.get_images(full=True)
    if image_list:
        # Assuming the first image is the main content
        xref = image_list[0][0]
        base_image = doc.extract_image(xref)
        image_data = base_image["image"]

        # Save the image to the temporary directory
        image_filename = f"page_{page_num + 1}_image.png"
        image_path = os.path.join(TEMP_DIR, image_filename)
        os.makedirs(TEMP_DIR, exist_ok=True)  # Ensure the directory exists
        with open(image_path, "wb") as image_file:
            image_file.write(image_data)
        return image_path
    else:
        return "No image found on this page"

def apply_ocr_to_page(page: fitz.Page) -> str:
    """
    Applies OCR to a page using Tesseract.

    Args:
        page: The fitz.Page object.

    Returns:
        The extracted text.
    """
    # Get the page as a pixmap
    pix = page.get_pixmap()
    img = Image.open(io.BytesIO(pix.tobytes()))

    # Perform OCR using Tesseract
    # Ensure that the 'rus' language pack is installed and used
    text = pytesseract.image_to_string(img, lang='rus')
    return text

def parse_pdf(pdf_file_path: str) -> ParsedPDF:
    try:
        doc = fitz.open(pdf_file_path)
        metadata = extract_metadata(doc)
        content = extract_text_from_pdf(doc)
        
        if not content.strip():
            raise ValueError("No text content extracted from PDF")
            
        return ParsedPDF(
            title=metadata.get("title", "Untitled"),
            author=metadata.get("author", "Unknown"),
            chapters=[Chapter(
                title="Main Content", 
                content=content.split('\n'), 
                headings=[], 
                page_number=1  # Add page number here
            )],
            metadata=metadata,
            content=content
        )
    except Exception as e:
        print(f"Critical parsing error: {str(e)}")
        raise
def extract_metadata(doc: fitz.Document) -> dict:
    """
    Extracts metadata from a PDF document.

    Args:
        doc: The PyMuPDF Document object.

    Returns:
        A dictionary containing the extracted metadata.
    """
    metadata = doc.metadata

    extracted_metadata = {
        "title": metadata.get("title", ""),
        "author": metadata.get("author", ""),
        "subject": metadata.get("subject", ""),
        "keywords": metadata.get("keywords", ""),
        "creation_date": metadata.get("creationDate", ""),
        "modification_date": metadata.get("modDate", ""),
    }

    return extracted_metadata

def is_image_only_page(page: fitz.Page) -> bool:
    """
    Checks if a page is likely an image-only page (e.g., cover, illustration).

    Args:
        page: The fitz.Page object.

    Returns:
        True if the page is likely image-only, False otherwise.
    """
    # Get the image blocks on the page
    image_blocks = page.get_images(full=True)

    # If there are no image blocks, it's not an image-only page
    if not image_blocks:
        return False

    # Get the text blocks on the page
    text_blocks = page.get_text("dict", flags=11)["blocks"]

    # If there are no text blocks, it's likely an image-only page
    if not text_blocks:
        return True

    # Further checks can be added here, e.g., check if the image covers a 
    # significant portion of the page area.

    return False  # Default to False if unsure

def extract_structured_text(page: fitz.Page) -> List[str]:
    """Extract text with layout awareness"""
    blocks = page.get_text("blocks", flags=fitz.TEXT_PRESERVE_LIGATURES)
    filtered = []
    
    for block in blocks:
        # Filter out header/footer regions (top/bottom 15% of page)
        if block[1] < page.rect.height * 0.15 or block[3] > page.rect.height * 0.85:
            continue
            
        filtered.append(block[4].strip())
    
    return filtered