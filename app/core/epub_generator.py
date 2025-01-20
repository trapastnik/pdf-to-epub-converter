# app/core/epub_generator.py
import os
from ebooklib import epub
from app.models import ParsedPDF, Chapter, Heading
from app.core.utils import sanitize_filename
from typing import List

def create_epub(pdf: ParsedPDF, output_path: str):
    """
    Creates an EPUB file from a ParsedPDF object.

    Args:
        pdf: The ParsedPDF object containing the parsed data.
        output_path: The path where the EPUB file should be saved.
    """
    print("Inside create_epub")
    book = epub.EpubBook()

    # Set metadata
    book.set_identifier(pdf.metadata.get("id", "unknown"))
    book.set_title(pdf.metadata.get("title", "Untitled"))
    book.set_language("en")  # Assuming English for now
    if pdf.metadata.get("author"):
        book.add_author(pdf.metadata.get("author"))

    # Create chapters and add them to the book
    chapters = []
    for i, chapter_data in enumerate(pdf.chapters):
        chapter_title = chapter_data.title
        chapter_file_name = f"chapter_{i+1}.xhtml"
        chapter = epub.EpubHtml(
            title=chapter_title,
            file_name=chapter_file_name,
            lang="en"
        )

        # Create chapter content with headings
        chapter_content = f"<h1>{chapter_title}</h1>"  # Add chapter title as h1
        for part in chapter_data.content:
            if part in [h.text for h in chapter_data.headings]:
                chapter_content += f"<h2>{part}</h2>"  # Add headings as h2
            else:
                chapter_content += f"<p>{part}</p>"  # Add paragraphs

        chapter.set_content(chapter_content)
        book.add_item(chapter)
        chapters.append(chapter)

    # Define Table of Contents
    book.toc = (chapters)

    # Add default NCX and Nav files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Define CSS style
    style = """
        body {
            font-family: sans-serif;
        }
        h1 {
            text-align: center;
            font-weight: bold;
        }
        h2 {
            font-weight: bold;
        }
        p {
            text-indent: 1.5em;
            line-height: 1.4;
        }
    """
    nav_css = epub.EpubItem(
        uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style
    )
    book.add_item(nav_css)

    # Set the basic book structure
    book.spine = ["nav"] + chapters

    # Write the EPUB file
    epub.write_epub(output_path, book, {})