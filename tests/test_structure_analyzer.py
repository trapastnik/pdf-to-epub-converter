# tests/test_structure_analyzer.py
import unittest
import os
import fitz
from app.core.pdf_parser import parse_pdf
from app.core.structure_analyzer import (
    analyze_structure,
    identify_heading_fonts,
    identify_chapters_and_headings,
    get_font_stats
)
from app.models import ParsedPDF, Chapter, Heading

class TestStructureAnalyzer(unittest.TestCase):
    def setUp(self):
        # Create a sample PDF for testing
        self.test_pdf_path = "tests/sample_structure.pdf"
        self.create_sample_pdf(self.test_pdf_path)
        self.parsed_pdf = parse_pdf(self.test_pdf_path)
        self.doc = fitz.open(self.test_pdf_path)

    def tearDown(self):
        # Clean up the sample PDF
        os.remove(self.test_pdf_path)
        self.doc.close()

    def create_sample_pdf(self, filepath):
        doc = fitz.open()
        
        # Page 1
        page = doc.new_page()
        page.insert_text((50, 50), "Chapter 1: Introduction", fontsize=14, fontname="Helvetica-Bold")
        page.insert_text((50, 100), "This is the first paragraph.", fontsize=12)
        page.insert_text((50, 150), "This is the second paragraph.", fontsize=12)

        # Page 2
        page = doc.new_page()
        page.insert_text((50, 50), "Chapter 2: Main Content", fontsize=14, fontname="Helvetica-Bold")
        page.insert_text((50, 100), "This is a paragraph in chapter 2.", fontsize=12)
        page.insert_text((50, 150), "Heading 1", fontsize=13, fontname="Helvetica-Bold")
        page.insert_text((50, 200), "This is a paragraph under Heading 1.", fontsize=12)

        doc.set_metadata({"title": "Sample Structure PDF", "author": "Test Author"})
        doc.save(filepath)
        doc.close()

    def test_analyze_structure(self):
        analyzed_pdf = analyze_structure(self.parsed_pdf, self.doc)
        self.assertIsInstance(analyzed_pdf, ParsedPDF)
        self.assertEqual(len(analyzed_pdf.chapters), 2)
        self.assertEqual(analyzed_pdf.chapters[0].title, "Chapter 1: Introduction")
        self.assertEqual(analyzed_pdf.chapters[1].title, "Chapter 2: Main Content")

    def test_get_font_stats(self):
        font_stats = get_font_stats(self.doc)
        self.assertTrue(("Helvetica-Bold", 14.0) in font_stats)
        self.assertTrue(("Helvetica", 12.0) in font_stats)

    def test_identify_heading_fonts(self):
        font_counts = {("Helvetica", 12.0): 10, ("Helvetica-Bold", 14.0): 2, ("Times-Roman", 11.0): 5}
        heading_fonts = identify_heading_fonts(font_counts)
        self.assertIn(("Helvetica-Bold", 14.0), heading_fonts)
        self.assertNotIn(("Helvetica", 12.0), heading_fonts)

    def test_identify_chapters_and_headings(self):
        text = self.parsed_pdf.content
        heading_fonts = [("Helvetica-Bold", 14.0), ("Helvetica-Bold", 13.0)]
        chapters = identify_chapters_and_headings(text, self.doc, heading_fonts)
        self.assertEqual(len(chapters), 2)
        self.assertEqual(chapters[0].title, "Chapter 1: Introduction")
        self.assertEqual(chapters[1].title, "Chapter 2: Main Content")
        self.assertEqual(len(chapters[1].headings), 1)
        self.assertEqual(chapters[1].headings[0].text, "Heading 1")

if __name__ == '__main__':
    unittest.main()