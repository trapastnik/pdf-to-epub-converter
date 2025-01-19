
# app/models.py
# This file defines the data models for the application.

class ParsedPDF:
    """
    Represents a parsed PDF document.
    """
    def __init__(self, title, author, chapters, metadata, content):
        self.title = title
        self.author = author
        self.chapters = chapters # List of Chapter objects
        self.metadata = metadata # Dictionary
        self.content = content # Raw or processed content

class Chapter:
    """
    Represents a chapter in a document.
    """
    def __init__(self, title, content, headings, page_number):
        self.title = title
        self.content = content
        self.headings = headings # List of Heading objects
        self.page_number = page_number

class Heading:
    """
    Represents a heading in a document.
    """
    def __init__(self, text, level):
        self.text = text
        self.level = level # e.g., 1, 2, 3 for h1, h2, h3
