# app/core/structure_analyzer.py
import re
from typing import List, Tuple
from app.models import ParsedPDF, Chapter, Heading
import fitz

def analyze_structure(pdf: ParsedPDF, doc: fitz.Document) -> ParsedPDF:
    """
    Analyzes the structure of a parsed PDF document to identify chapters and headings.

    Args:
        pdf: The ParsedPDF object containing the parsed content.
        doc: The fitz document.

    Returns:
        The ParsedPDF object with the identified structure.
    """
    # Analyze font sizes and styles for headings
    print("Inside analyze_structure")
    font_counts = get_font_stats(doc)
    heading_fonts = identify_heading_fonts(font_counts)

    # Analyze the text content to identify chapters and headings
    chapters = identify_chapters_and_headings(pdf.content, doc, heading_fonts)

    pdf.chapters = chapters
    print("Exiting analyze_structure")

    return pdf

def get_font_stats(doc: fitz.Document):
    """
    Analyzes font sizes and styles used on each page of the PDF.
    Returns a dictionary of font statistics.
    """
    font_counts = {}
    for page in doc:
        for block in page.get_text("dict", flags=11)["blocks"]:
            if block['type'] == 0:  # Text block
                for line in block["lines"]:
                    for span in line["spans"]:
                        font_identifier = (span["font"], span["size"])
                        font_counts[font_identifier] = font_counts.get(font_identifier, 0) + 1
    return font_counts

def identify_heading_fonts(font_counts: dict):
    """
    Identifies potential heading fonts based on frequency.
    Assumes that headings are used less frequently than body text.
    """
    if not font_counts:
        return []

    # Sort fonts by frequency (ascending)
    sorted_fonts = sorted(font_counts.items(), key=lambda item: item[1])

    # Assume the least frequent fonts are potential headings
    heading_threshold = 0.2 * len(sorted_fonts)
    heading_fonts = [font for font, count in sorted_fonts[:int(heading_threshold)]]

    return heading_fonts

def identify_chapters_and_headings(text: str, doc: fitz.Document, heading_fonts: List[Tuple[str, float]]) -> List[Chapter]:
    """
    Identifies chapters and headings in the text content using font information.

    Args:
        text: The raw text content of the PDF.
        doc: The fitz document.
        heading_fonts: A list of font identifiers potentially used for headings.

    Returns:
        A list of Chapter objects with identified headings.
    """
    chapters: List[Chapter] = []
    current_chapter = None
    current_heading = None

    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if b["type"] == 0:
                for line in b["lines"]:
                    for span in line["spans"]:
                        font_identifier = (span["font"], span["size"])
                        text = span["text"].strip()
                        if not text:
                            continue
                        if any(font_identifier == h_font for h_font in heading_fonts):
                            # Likely a heading
                            if current_chapter is None:
                                # Start of a new chapter (e.g., first page)
                                current_chapter = Chapter(title=text, content=[], headings=[], page_number=page_num + 1)
                                chapters.append(current_chapter)
                            elif current_heading is None or current_heading.text != text:
                                current_heading = Heading(text=text, level=1)
                                current_chapter.headings.append(current_heading)
                                current_chapter.content.append(text)
                        elif current_chapter is not None:
                            current_chapter.content.append(text)
                        else:
                            current_chapter = Chapter(title="Chapter", content=[], headings=[], page_number=page_num + 1)
                            current_chapter.content.append(text)
                            chapters.append(current_chapter)

    # If no chapters were identified, treat the whole document as one chapter
    if not chapters:
        chapters.append(Chapter(title="Document", content=[text], headings=[], page_number=1))

    return chapters