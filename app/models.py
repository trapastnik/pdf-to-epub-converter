# app/models.py
from typing import List, Dict, Optional

class ParsedPDF:
    """
    Represents a parsed PDF document.
    """
    def __init__(self, title: str, author: str, chapters: List["Chapter"], metadata: Dict, content: str):
        self.title = title
        self.author = author
        self.chapters = chapters
        self.metadata = metadata
        self.content = content

class Chapter:
    """
    Represents a chapter in a document.
    """
    def __init__(self, title: str, content: List[str], headings: List["Heading"], page_number: int):
        self.title = title
        self.content = content
        self.headings = headings
        self.page_number = page_number

class Heading:
    """
    Represents a heading in a document.
    """
    def __init__(self, text: str, level: int):
        self.text = text
        self.level = level