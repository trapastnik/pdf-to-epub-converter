# app/core/pdf_parser.py
import fitz
import pytesseract
from PIL import Image
import io
from app.models import ParsedPDF, Chapter, Heading
from typing import List

def extract_text_from_pdf(filepath: str) -> str:
    """
    Extracts text from a PDF file using OCR.

    Args:
        filepath: The path to the PDF file.

    Returns:
        The extracted text as a single string.
    """
    try:
        doc = fitz.open(filepath)
        text = ""
        for page in doc:
            image_list = page.get_images(full=True)
            for img in image_list:
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_data = base_image["image"]

                # Convert to PIL Image
                pil_image = Image.open(io.BytesIO(image_data))

                # Use pytesseract to extract text
                text += pytesseract.image_to_string(pil_image)
        doc.close()
        return text
    except Exception as e:
        raise ValueError(f"Error during OCR processing: {e}")

def parse_pdf(filepath: str) -> ParsedPDF:
    """
    Parses a PDF file, extracts metadata, content, and basic structure.

    Args:
        filepath: The path to the PDF file.

    Returns:
        A ParsedPDF object containing the parsed data.
    """
    try:
        doc = fitz.open(filepath)
    except Exception as e:
        raise ValueError(f"Error opening PDF file: {e}")

    metadata = extract_metadata(doc)
    title = metadata.get("title", "Untitled")
    author = metadata.get("author", "Unknown")
    content = extract_text_from_pdf(filepath)  # Use OCR to extract text
    chapters: List[Chapter] = []

    # Basic structure analysis will be done in structure_analyzer.py
    # For now, just create a single chapter with all content
    chapters.append(Chapter(title="Chapter 1", content=[content], headings=[], page_number=1))

    doc.close()
    return ParsedPDF(title=title, author=author, chapters=chapters, metadata=metadata, content=content)

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