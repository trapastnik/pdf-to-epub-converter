# tests/test_pdf_parser.py
import unittest
import os
import fitz
from app.core.pdf_parser import parse_pdf, extract_metadata
from app.models import ParsedPDF

class TestPDFParser(unittest.TestCase):
    def setUp(self):
        # Create a sample PDF for testing
        self.test_pdf_path = "tests/sample.pdf"
        self.create_sample_pdf(self.test_pdf_path)

    def tearDown(self):
        # Clean up the sample PDF
        os.remove(self.test_pdf_path)

    def create_sample_pdf(self, filepath):
        doc = fitz.open()
        page = doc.new_page()
        text = "Sample PDF Content"
        page.insert_text((50, 100), text, fontsize=12)
        doc.set_metadata({"title": "Sample PDF", "author": "Test Author"})
        doc.save(filepath)
        doc.close()

    def test_parse_pdf(self):
        parsed_pdf = parse_pdf(self.test_pdf_path)
        self.assertIsInstance(parsed_pdf, ParsedPDF)
        self.assertEqual(parsed_pdf.title, "Sample PDF")
        self.assertEqual(parsed_pdf.author, "Test Author")

    def test_extract_metadata(self):
        doc = fitz.open(self.test_pdf_path)
        metadata = extract_metadata(doc)
        self.assertEqual(metadata["title"], "Sample PDF")
        self.assertEqual(metadata["author"], "Test Author")
        doc.close()

if __name__ == '__main__':
    unittest.main()