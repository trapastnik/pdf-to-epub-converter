# app/core/structure_analyzer.py
import re
import numpy as np
import fitz
from sklearn.cluster import KMeans
from typing import List, Tuple, Optional
from app.models import ParsedPDF, Chapter, Heading
from app.core.utils import apply_russian_hyphenation

# Hierarchical heading patterns (Russian + international)
HEADING_PATTERNS = [
    (r"^Глава\s+\d+", 1),           # Chapter (Level 1)
    (r"^Раздел\s+\d+", 1),          # Section (Level 1)
    (r"^Часть\s+[IVXLCDM]+", 1),    # Part with Roman numerals (Level 1)
    (r"^\d+\.\s", 2),               # Numbered heading (Level 2)
    (r"^\d+\.\d+", 2),              # Subsection (Level 2)
    (r"^[IVXLCDM]+\.", 2),          # Roman numerals (Level 2)
    (r"^\d+\.\d+\.\d+", 3),         # Sub-subsection (Level 3)
    (r"^Приложение\s+[А-ЯA-Z]", 4), # Appendix (Level 4)
]
TOC_PATTERN = re.compile(
    r'^(\d+\.\d+(?:\.\d+)*)\s+(.+?)\s+(\d+)$',  # Matches "5.2.3 Method... 30"
    re.IGNORECASE
)

def detect_toc_entries(lines: List[str]) -> List[Tuple[str, int]]:
    """Identify TOC entries with page numbers"""
    toc = []
    for line in lines:
        match = TOC_PATTERN.search(line)
        if match:
            section_num = match.group(1)
            title = match.group(2).strip()
            page_num = int(match.group(3))
            toc.append((f"{section_num} {title}", page_num))
    return toc

def analyze_structure(pdf: ParsedPDF, doc: fitz.Document) -> ParsedPDF:
    """Structure analysis with content safeguards"""
    # Existing analysis logic
    
    # Content fallback mechanism
    if not pdf.chapters:
        print("WARNING: No chapters detected, creating fallback structure")
        pdf.chapters = [
            Chapter(
                title="Main Content",
                content=pdf.content.split("\n"),
                headings=[],
                page_number=1
            )
        ]
    
    # Ensure minimum content
    for chapter in pdf.chapters:
        if not chapter.content:
            chapter.content = ["Content placeholder text"]
    
    return pdf


def get_font_stats(doc: fitz.Document) -> dict:
    """Extracts font statistics with layout preservation"""
    font_counts = {}
    for page in doc:
        blocks = page.get_text("dict", flags=11)["blocks"]
        for block in blocks:
            if block['type'] == 0:
                for line in block["lines"]:
                    for span in line["spans"]:
                        key = (span["font"], span["size"])
                        font_counts[key] = font_counts.get(key, 0) + 1
    return font_counts

def enhanced_font_clustering(font_counts: dict) -> list:
    """Cluster fonts using K-means for heading detection"""
    if not font_counts:
        return []

    font_data = [[size] for (_, size), count in font_counts.items()]
    X = np.array(font_data)
    
    n_clusters = min(3, len(font_data))
    if n_clusters < 1:
        return []

    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(X)
    clusters = kmeans.labels_

    # Get cluster with largest average font size
    cluster_stats = {}
    for i, ((_, size), _) in enumerate(font_counts.items()):
        cluster = clusters[i]
        cluster_stats.setdefault(cluster, []).append(size)
    
    sorted_clusters = sorted(
        cluster_stats.items(),
        key=lambda x: np.mean(x[1]),
        reverse=True
    )
    
    return [
        font for i, (font, _) in enumerate(font_counts.keys())
        if clusters[i] == sorted_clusters[0][0]
    ]

def detect_heading_level(text: str) -> int:
    """Detects heading level using text patterns"""
    for pattern, level in HEADING_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return level
    return 0

def determine_heading_level(text: str, font_size: float, heading_fonts: list) -> int:
    """Combines pattern and font analysis for accurate level detection"""
    if pattern_level := detect_heading_level(text):
        return pattern_level
    
    sorted_sizes = sorted({size for _, size in heading_fonts}, reverse=True)
    for idx, size in enumerate(sorted_sizes, 1):
        if font_size >= size:
            return idx
    return len(sorted_sizes) + 1

def identify_chapters_and_headings_multipass(doc: fitz.Document, heading_fonts: list) -> List[Chapter]:
    """Multi-pass structure analysis with hierarchy support"""
    chapters = []
    current_chapter = None
    current_heading_stack = []

    for page_num, page in enumerate(doc, 1):
        blocks = page.get_text("dict", flags=11)["blocks"]
        
        for block in blocks:
            if block['type'] != 0:
                continue
                
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    if not text:
                        continue

                    font_ident = (span["font"], span["size"])
                    is_heading_font = font_ident in heading_fonts
                    pattern_level = detect_heading_level(text)
                    
                    # Chapter detection
                    if pattern_level == 1:
                        current_chapter = Chapter(
                            title=text,
                            content=[],
                            headings=[],
                            page_number=page_num
                        )
                        chapters.append(current_chapter)
                        current_heading_stack = []
                        continue

                    # Heading processing
                    if is_heading_font or pattern_level > 0:
                        level = determine_heading_level(
                            text=text,
                            font_size=font_ident[1],
                            heading_fonts=heading_fonts
                        )
                        
                        # Maintain hierarchy
                        while current_heading_stack and current_heading_stack[-1].level >= level:
                            current_heading_stack.pop()
                            
                        new_heading = Heading(text=text, level=level)
                        if current_heading_stack:
                            current_heading_stack[-1].subheadings.append(new_heading)
                        else:
                            if current_chapter:
                                current_chapter.headings.append(new_heading)
                                
                        current_heading_stack.append(new_heading)
                        
                    # Regular content
                    elif current_chapter:
                        current_chapter.content.append(text)

    return chapters

def remove_page_numbers(text: str) -> str:
    """Advanced page number removal with Russian patterns"""
    patterns = [
        r"^[\s\u00a0]*[-–—]?\s*\d+\s*[-–—]?[\s\u00a0]*$",  # Standalone
        r"\bстр?\.?\s*\d+",                                # Russian "стр. X"
        r"\d+/\d+"                                         # Fractional
    ]
    for pattern in patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    return text.strip()

def merge_misaligned_lines(lines: List[str]) -> List[str]:
    """Smart paragraph reconstruction"""
    merged = []
    current_para = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Start new paragraph if:
        # - Previous line ends with sentence terminator
        # - Current line starts with uppercase
        if current_para and (
            re.search(r"[.!?]\s*$", current_para[-1]) or
            (line and line[0].isupper())
        ):
            merged.append(" ".join(current_para))
            current_para = []
            
        current_para.append(line)
    
    if current_para:
        merged.append(" ".join(current_para))
        
    return merged

def create_fallback_structure(content: str) -> List[Chapter]:
    return [Chapter(
        title="Основное содержание",
        content=merge_misaligned_lines(content.split('\n')),
        headings=[],
        page_number=1  # Add page number
    )]
def validate_content(pdf: ParsedPDF) -> bool:
    """Ensure no orphaned text or broken paragraphs"""
    for chapter in pdf.chapters:
        if any(len(line) > 500 for line in chapter.content):
            logging.warning(f"Long line detected in chapter {chapter.title}")
        if re.search(r'\w{20,}', ' '.join(chapter.content)):
            logging.error("Possible OCR artifacts detected")
            return False
    return True