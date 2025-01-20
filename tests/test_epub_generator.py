# tests/test_epub_generator.py
import unittest
import os
import ebooklib
from ebooklib import epub
from app.core.epub_generator import create_epub
from app.models import ParsedPDF, Chapter, Heading

class TestEPUBGenerator(unittest.TestCase):
    def setUp(self):
        # Create a sample ParsedPDF object for testing
        self.test_epub_path = "tests/sample.epub"
        self.parsed_pdf = ParsedPDF(
            title="Sample EPUB",
            author="Test Author",
            chapters=[
                Chapter(title="Chapter 1", content=["This is the content of chapter 1."], headings=[], page_number=1),
                Chapter(title="Chapter 2", content=["This is the content of chapter 2.", "This is Heading 1", "This is under heading 1"], headings=[Heading(text="This is Heading 1", level=1)], page_number=2),
            ],
            metadata={"title": "Sample EPUB", "author": "Test Author", "id": "1234567890"},
            content = "Sample PDF Content"
        )

    def tearDown(self):
        # Clean up the generated EPUB file
        if os.path.exists(self.test_epub_path):
            os.remove(self.test_epub_path)

    def test_create_epub(self):
        create_epub(self.parsed_pdf, self.test_epub_path)
        self.assertTrue(os.path.exists(self.test_epub_path))

        # Further validation can be added here, e.g., using an EPUB validator
        # to check the structure and contents of the generated EPUB file.
        
        book = epub.read_epub(self.test_epub_path)
        self.assertEqual(book.get_metadata('DC', 'title'), ['Sample EPUB'])
        self.assertEqual(book.get_metadata('DC', 'creator'), ['Test Author'])
        
        chapters = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
        self.assertEqual(len(chapters), 2)
        self.assertEqual(chapters[0].get_name(), 'chapter_1.xhtml')
        self.assertEqual(chapters[1].get_name(), 'chapter_2.xhtml')

if __name__ == '__main__':
    unittest.main()