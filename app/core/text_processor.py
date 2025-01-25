# app/core/text_processor.py
from typing import List, Dict, Callable
import re

class TextProcessor:
    def __init__(self):
        self.pipeline = []
        self.config = {
            'hyphen_handling': True,
            'paragraph_merge_threshold': 0.8,
            'toc_patterns': [
                r'(?P<section>\d+(\.\d+)*)\s+(?P<title>.+?)\s+(?P<page>\d+)$',
                r'(?P<title>.*?)\s+\.{3,}\s+(?P<page>\d+)$'
            ]
        }

    def add_processing_step(self, func: Callable):
        self.pipeline.append(func)

    def process(self, text: str) -> str:
        for step in self.pipeline:
            text = step(text)
        return text

    def default_hyphen_handler(self, text: str) -> str:
        """Merge hyphenated words across line breaks"""
        return re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)

    def paragraph_merger(self, text: str) -> str:
        """Smart paragraph merging using multiple heuristics"""
        lines = text.split('\n')
        merged = []
        current_para = []
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_para:
                    merged.append(' '.join(current_para))
                    current_para = []
                continue
                
            # Check for paragraph starters
            if len(current_para) == 0 and line[0].islower():
                if merged:
                    merged[-1] += ' ' + line
                    continue
                    
            current_para.append(line)
            
        if current_para:
            merged.append(' '.join(current_para))
            
        return '\n\n'.join(merged)

    def detect_toc_entries(self, text: str) -> List[Dict]:
        """Improved TOC detection with multiple patterns"""
        entries = []
        for pattern in self.config['toc_patterns']:
            matches = re.finditer(pattern, text, re.MULTILINE)
            for match in matches:
                entries.append({
                    'section': match.group('section') if 'section' in match.groupdict() else None,
                    'title': match.group('title').strip(),
                    'page': int(match.group('page'))
                })
        return entries

    def interactive_correction(self, text: str) -> str:
        """Placeholder for manual correction interface"""
        # This would be implemented as a GUI/web interface
        # For CLI, could output diff and accept patches
        return text