# app/core/epub_generator.py
from ebooklib import epub
from app.models import ParsedPDF, Chapter, Heading
from app.core.utils import sanitize_filename
from typing import List
import json
import logging


# CSS for improved e-reader compatibility
EPUB_CSS = """
@namespace epub "http://www.idpf.org/2007/ops";

body {{
    -epub-hyphens: auto;
    hyphens: auto;
    text-align: justify;
    font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", sans-serif;
    line-height: 1.6;
    margin: 1em auto;
    max-width: 45em;
}}

h1 {{
    page-break-before: always;
    border-bottom: 2px solid #ccc;
    padding-bottom: 0.5em;
    font-size: 2em;
}}

h2 {{ font-size: 1.5em; }}
h3 {{ font-size: 1.3em; }}
h4 {{ font-size: 1.1em; }}

.toc {{
    list-style-type: none;
    padding-left: 1em;
}}

.toc a {{
    text-decoration: none;
    color: inherit;
    display: block;
    padding: 0.3em 0;
}}

.toc > li > a {{
    font-weight: bold;
    margin-top: 1em;
}}
"""
RUSSIAN_CSS = """
/* Improved Russian typography */
@namespace epub "http://www.idpf.org/2007/ops";

:root {
    -epub-hyphens: auto;
    hyphens: auto;
    hyphenate-limit-chars: 6 3 2;
    hyphenate-limit-lines: 2;
}

body {
    font-family: "Helvetica CY", "Noto Sans", sans-serif;
    line-height: 1.8;
    text-align: justify;
    margin: 1rem 2rem;
    text-indent: 1.5em;
}

h1 {
    font-family: "PT Sans Caption", sans-serif;
    font-size: 2.2rem;
    margin: 3rem 0 1.5rem;
    page-break-before: always;
    border-bottom: 2px solid #ccc;
    text-indent: 0;
}

p {
    margin: 0.8rem 0;
    text-align-last: left;
}

/* Image handling */
img {
    max-width: 90%;
    height: auto;
    display: block;
    margin: 1rem auto;
}
"""

class InteractiveEPUBCreator:
    def __init__(self):
        self.stages = {
            'raw_text': None,
            'processed_text': None,
            'structure': None,
            'toc': None
        }
        self.output_path = "output.epub"

    def clean_text(self, text: str) -> str:
        """Basic text cleaning implementation"""
        return text.replace('\xa0', ' ')  # Replace non-breaking spaces

    def save_checkpoint(self, stage: str):
        try:
            with open(f'checkpoint_{stage}.json', 'w', encoding='utf-8') as f:
                json.dump(self.stages[stage], f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"Error saving checkpoint: {str(e)}")

    def load_checkpoint(self, stage: str):
        try:
            with open(f'checkpoint_{stage}.json', encoding='utf-8') as f:
                self.stages[stage] = json.load(f)
        except Exception as e:
            logging.error(f"Error loading checkpoint: {str(e)}")

    def create_epub(self, processed_text: str) -> str:
        try:
            self.stages['raw_text'] = processed_text
            self.save_checkpoint('raw_text')
            
            self.load_checkpoint('raw_text')
            self.stages['processed_text'] = self.clean_text(self.stages['raw_text'])
            self.save_checkpoint('processed_text')

            # Create minimal valid EPUB structure
            book = epub.EpubBook()
            book.set_identifier('id1')
            book.set_title('Converted Book')
            book.set_language('en')
            
            # Add default chapter
            chapter = epub.EpubHtml(title='Chapter 1', file_name='chap_01.xhtml')
            chapter.content = f'<h1>Chapter 1</h1><p>{self.stages["processed_text"][:500]}...</p>'
            
            book.add_item(chapter)
            book.add_item(epub.EpubNcx())
            book.add_item(epub.EpubNav())
            
            epub.write_epub(self.output_path, book, {})
            return self.output_path
            
        except Exception as e:
            logging.error(f"EPUB creation failed: {str(e)}")
            raise

def generate_toc_html(chapters: List[Chapter]) -> str:
    """Generate semantic TOC with proper page numbers"""
    toc_items = []
    for chapter in chapters:
        # Extract page number from chapter metadata
        page_num = chapter.metadata.get('page_number', '')
        toc_items.append(
            f'<li class="toc-entry">'
            f'<a href="#{chapter.id}">{chapter.title}'
            f'<span class="page-number">{page_num}</span></a>'
            f'</li>'
        )
    
    return f'''
    <nav id="toc">
        <h2>Table of Contents</h2>
        <ul class="toc-list">
            {"".join(toc_items)}
        </ul>
    </nav>
    '''

TOC_CSS = """
.toc-entry {
    display: flex;
    justify-content: space-between;
    page-break-inside: avoid;
}

.page-number {
    font-weight: normal;
    margin-left: 1em;
}
"""
def create_epub(pdf: ParsedPDF, output_path: str) -> None:
    """Enhanced EPUB generation with validation"""
    # Content validation
    if not pdf.chapters:
        raise ValueError("No chapters found in parsed PDF content")
    
    # Create base book structure
    book = epub.EpubBook()
    book.set_language('ru')
    
    # Add CSS
    css_item = epub.EpubItem(
        uid="rus_style",
        file_name="style/main.css",
        media_type="text/css",
        content=RUSSIAN_CSS
    )
    book.add_item(css_item)

    # Create chapters with proper structure
    chapters = []
    for idx, chapter in enumerate(pdf.chapters):
        epub_chap = epub.EpubHtml(
            title=chapter.title,
            file_name=f'chap_{idx}.xhtml',
            lang='ru'
        )
        
        content = [f'<h1>{chapter.title}</h1>']
        for line in chapter.content:
            if line.strip():
                content.append(f'<p>{line}</p>')
        
        epub_chap.content = '\n'.join(content)
        book.add_item(epub_chap)
        chapters.append(epub_chap)

    # Create navigation
    book.toc = [(chap, []) for chap in chapters]
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ['nav'] + chapters
    
    # Generate output
    epub.write_epub(output_path, book, {})


def create_chapter_content(chapter_num: int, chapter: Chapter) -> epub.EpubHtml:
    """Createns chapter content with proper heading hierarchy"""
    content = []
    
    # Chapter title
    content.append(f'<h1 id="chap_{chapter_num}">{chapter.title}</h1>')
    
    # Process headings and content
    for item in chapter.content:
        if isinstance(item, Heading):
            content.append(
                f'<h{item.level} id="heading_{chapter_num}_{item.level}">'
                f'{item.text}'
                f'</h{item.level}>'
            )
        else:
            content.append(f'<p>{item}</p>')

    # Create chapter file
    chapter_file = epub.EpubHtml(
        title=chapter.title,
        file_name=f'chapter_{chapter_num}.xhtml',
        content=''.join(content)
    )
    return chapter_file

def generate_hierarchical_toc(chapters: List[Chapter]) -> list:
    """Generates nested TOC structure"""
    toc = []
    for chap_idx, chapter in enumerate(chapters, 1):
        chapter_link = epub.Link(
            f'chapter_{chap_idx}.xhtml#chap_{chap_idx}',
            chapter.title,
            f'chap_{chap_idx}'
        )
        
        # Process headings recursively
        headings = []
        for heading in chapter.headings:
            headings.extend(
                process_heading(
                    heading, 
                    chap_idx,
                    parent_level=1
                )
            )
        
        toc.append((chapter_link, headings))
    
    return toc

def process_heading(
    heading: Heading, 
    chapter_num: int,
    parent_level: int
) -> list:
    """Recursively processes headings into nested lists"""
    item = epub.Link(
        f'chapter_{chapter_num}.xhtml#heading_{chapter_num}_{heading.level}',
        heading.text,
        f'heading_{chapter_num}_{heading.level}'
    )
    
    subitems = []
    if hasattr(heading, 'subheadings'):
        for subheading in heading.subheadings:
            if subheading.level > parent_level + 1:
                continue  # Skip levels that jump too deep
            subitems.extend(
                process_heading(
                    subheading,
                    chapter_num,
                    parent_level=heading.level
                )
            )
    
    return [(item, subitems)] if subitems else [item]
def build_russian_toc(chapters: List[Chapter]) -> list:
    toc = []
    for chap_idx, chapter in enumerate(chapters):
        chap_link = epub.Link(
            f'chapter_{chap_idx}.xhtml',
            chapter.title,
            f'chap_{chap_idx}'
        )
        
        subsections = []
        for heading in chapter.headings:
            subsections.append((
                epub.Link(
                    f'chapter_{chap_idx}.xhtml#h{heading.level}',
                    heading.text,
                    f'sub_{chap_idx}_{heading.level}'
                ),
                []
            ))
        
        toc.append((chap_link, subsections))
    return toc