"""
Mammoth-based DOCX Processor
Uses pure Python Mammoth library to convert DOCX to HTML/Markdown for easier processing.
Provides cleaner text extraction and template analysis capabilities.
"""

import mammoth
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from bs4 import BeautifulSoup
import re


class MammothDocxProcessor:
    """Processes DOCX files using Mammoth for cleaner HTML/Markdown output."""

    def __init__(self):
        self.options = mammoth.options

    def docx_to_html(self, docx_path: str) -> str:
        """Convert DOCX to clean HTML."""
        with open(docx_path, 'rb') as docx_file:
            result = mammoth.convert_to_html(docx_file)
            return result.value

    def docx_to_markdown(self, docx_path: str) -> str:
        """Convert DOCX to Markdown."""
        with open(docx_path, 'rb') as docx_file:
            result = mammoth.convert_to_markdown(docx_file)
            return result.value

    def extract_text_with_styles(self, docx_path: str) -> Dict[str, Any]:
        """Extract text with style information."""
        with open(docx_path, 'rb') as docx_file:
            result = mammoth.convert_to_html(docx_file, style_map=self._get_style_map())
            html_content = result.value
            messages = result.messages

            return {
                'html': html_content,
                'text': self._html_to_text(html_content),
                'styles': self._extract_styles_from_html(html_content),
                'messages': messages
            }

    def _get_style_map(self) -> str:
        """Get style map for better HTML conversion."""
        return """
        p[style-name='Title'] => h1.title
        p[style-name='Heading 1'] => h1
        p[style-name='Heading 2'] => h2
        p[style-name='Heading 3'] => h3
        p[style-name='Heading 4'] => h4
        p[style-name='Heading 5'] => h5
        p[style-name='Heading 6'] => h6
        p[style-name='Subtitle'] => h2.subtitle
        p[style-name='Quote'] => blockquote
        p[style-name='Intense Quote'] => blockquote.intense
        p[style-name='Bibliography'] => div.bibliography
        r[style-name='Strong'] => strong
        r[style-name='Emphasis'] => em
        r[style-name='Code'] => code
        table => table.table
        """

    def _html_to_text(self, html: str) -> str:
        """Convert HTML back to clean text."""
        soup = BeautifulSoup(html, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()

        # Get text
        text = soup.get_text()

        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)

        return text

    def _extract_styles_from_html(self, html: str) -> Dict[str, Any]:
        """Extract style information from HTML."""
        soup = BeautifulSoup(html, 'html.parser')

        styles = {
            'headings': [],
            'paragraphs': [],
            'lists': [],
            'tables': len(soup.find_all('table')),
            'images': len(soup.find_all('img')),
            'links': len(soup.find_all('a'))
        }

        # Extract headings
        for i in range(1, 7):
            headings = soup.find_all(f'h{i}')
            styles['headings'].extend([h.get_text().strip() for h in headings])

        # Count paragraphs
        styles['paragraphs'] = len(soup.find_all('p'))

        # Extract lists
        lists = soup.find_all(['ul', 'ol'])
        for list_elem in lists:
            items = list_elem.find_all('li')
            styles['lists'].append({
                'type': list_elem.name,
                'items': len(items),
                'content': [item.get_text().strip() for item in items]
            })

        return styles

    def analyze_template_structure(self, docx_path: str) -> Dict[str, Any]:
        """Analyze template structure using HTML representation."""
        html = self.docx_to_html(docx_path)
        soup = BeautifulSoup(html, 'html.parser')

        analysis = {
            'structure': {
                'headings': self._analyze_headings(soup),
                'sections': self._analyze_sections(soup),
                'formatting': self._analyze_formatting(soup),
                'layout': self._analyze_layout(soup)
            },
            'content': {
                'total_words': len(self._html_to_text(html).split()),
                'total_paragraphs': len(soup.find_all('p')),
                'total_headings': sum(len(soup.find_all(f'h{i}')) for i in range(1, 7)),
                'total_tables': len(soup.find_all('table')),
                'total_lists': len(soup.find_all(['ul', 'ol']))
            },
            'html_representation': html
        }

        return analysis

    def _analyze_headings(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze heading structure."""
        headings = {}
        for i in range(1, 7):
            h_tags = soup.find_all(f'h{i}')
            headings[f'h{i}'] = {
                'count': len(h_tags),
                'content': [h.get_text().strip() for h in h_tags],
                'patterns': self._detect_heading_patterns([h.get_text().strip() for h in h_tags])
            }

        return headings

    def _analyze_sections(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze document sections."""
        # Look for common academic section patterns
        sections = {
            'front_matter': [],
            'main_content': [],
            'back_matter': []
        }

        text_content = self._html_to_text(soup.get_text())

        # Front matter patterns
        front_patterns = [
            r'^(halaman judul|title page)', r'^(pengesahan|approval)',
            r'^(abstrak|abstract)', r'^(kata pengantar|preface)',
            r'^(daftar isi|table of contents)'
        ]

        # Main content patterns
        main_patterns = [
            r'^bab\s+\d+', r'^chapter\s+\d+', r'^\d+\.\s+', r'^[A-Z]\.\s+'
        ]

        # Back matter patterns
        back_patterns = [
            r'^(daftar pustaka|bibliography|references)',
            r'^(lampiran|appendix)', r'^(indeks|index)'
        ]

        lines = text_content.split('\n')
        current_section = 'unknown'

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if any(re.search(pattern, line, re.IGNORECASE) for pattern in front_patterns):
                current_section = 'front_matter'
            elif any(re.search(pattern, line, re.IGNORECASE) for pattern in main_patterns):
                current_section = 'main_content'
            elif any(re.search(pattern, line, re.IGNORECASE) for pattern in back_patterns):
                current_section = 'back_matter'

            if current_section in sections:
                sections[current_section].append(line)

        return sections

    def _analyze_formatting(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze formatting patterns."""
        formatting = {
            'bold_elements': len(soup.find_all(['strong', 'b'])),
            'italic_elements': len(soup.find_all(['em', 'i'])),
            'underline_elements': len(soup.find_all(style=lambda s: s and 'text-decoration' in s)),
            'font_sizes': self._extract_font_sizes(soup),
            'alignment_patterns': self._analyze_alignment(soup)
        }

        return formatting

    def _analyze_layout(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze document layout."""
        layout = {
            'has_tables': len(soup.find_all('table')) > 0,
            'has_lists': len(soup.find_all(['ul', 'ol'])) > 0,
            'has_images': len(soup.find_all('img')) > 0,
            'structure_complexity': self._calculate_structure_complexity(soup)
        }

        return layout

    def _detect_heading_patterns(self, headings: List[str]) -> List[str]:
        """Detect patterns in headings."""
        patterns = []

        # Check for numbered sections
        numbered = [h for h in headings if re.match(r'^\d+', h)]
        if numbered:
            patterns.append(f"numbered_sections: {len(numbered)} found")

        # Check for BAB pattern (Indonesian)
        bab_pattern = [h for h in headings if re.match(r'^BAB\s+\d+', h, re.IGNORECASE)]
        if bab_pattern:
            patterns.append(f"bab_chapters: {len(bab_pattern)} found")

        # Check for Chapter pattern (English)
        chapter_pattern = [h for h in headings if re.match(r'^Chapter\s+\d+', h, re.IGNORECASE)]
        if chapter_pattern:
            patterns.append(f"english_chapters: {len(chapter_pattern)} found")

        return patterns

    def _extract_font_sizes(self, soup: BeautifulSoup) -> List[int]:
        """Extract font sizes from HTML (simplified)."""
        # This is a simplified version - in practice, you'd parse CSS styles
        return [12]  # Default assumption

    def _analyze_alignment(self, soup: BeautifulSoup) -> Dict[str, int]:
        """Analyze text alignment patterns."""
        alignments = {
            'left': 0,
            'center': 0,
            'right': 0,
            'justify': 0
        }

        # Count alignment styles (simplified)
        alignments['left'] = len(soup.find_all('p'))
        alignments['center'] = len(soup.find_all(style=lambda s: s and 'text-align: center' in s))

        return alignments

    def _calculate_structure_complexity(self, soup: BeautifulSoup) -> float:
        """Calculate document structure complexity score."""
        elements = len(soup.find_all())
        depth = self._calculate_html_depth(soup)
        headings = sum(len(soup.find_all(f'h{i}')) for i in range(1, 7))

        # Simple complexity formula
        complexity = (elements * 0.1) + (depth * 2) + (headings * 1.5)
        return min(complexity, 10.0)  # Cap at 10

    def _calculate_html_depth(self, soup: BeautifulSoup, max_depth: int = 0) -> int:
        """Calculate maximum HTML nesting depth."""
        def get_depth(element, current_depth=0):
            if not element.find_all():
                return current_depth
            return max(get_depth(child, current_depth + 1) for child in element.find_all())

        return get_depth(soup)

    def compare_documents(self, docx1_path: str, docx2_path: str) -> Dict[str, Any]:
        """Compare two DOCX documents using HTML representation."""
        html1 = self.docx_to_html(docx1_path)
        html2 = self.docx_to_html(docx2_path)

        soup1 = BeautifulSoup(html1, 'html.parser')
        soup2 = BeautifulSoup(html2, 'html.parser')

        comparison = {
            'structure_similarity': self._compare_structure(soup1, soup2),
            'content_similarity': self._compare_content(html1, html2),
            'formatting_differences': self._compare_formatting(soup1, soup2),
            'recommendations': []
        }

        return comparison

    def _compare_structure(self, soup1: BeautifulSoup, soup2: BeautifulSoup) -> float:
        """Compare document structures."""
        headings1 = sum(len(soup1.find_all(f'h{i}')) for i in range(1, 7))
        headings2 = sum(len(soup2.find_all(f'h{i}')) for i in range(1, 7))

        paragraphs1 = len(soup1.find_all('p'))
        paragraphs2 = len(soup2.find_all('p'))

        # Simple similarity score
        heading_diff = abs(headings1 - headings2) / max(headings1, headings2, 1)
        paragraph_diff = abs(paragraphs1 - paragraphs2) / max(paragraphs1, paragraphs2, 1)

        similarity = 1.0 - (heading_diff + paragraph_diff) / 2
        return max(0.0, similarity)

    def _compare_content(self, html1: str, html2: str) -> float:
        """Compare document content."""
        text1 = self._html_to_text(html1)
        text2 = self._html_to_text(html2)

        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        if not union:
            return 1.0

        return len(intersection) / len(union)

    def _compare_formatting(self, soup1: BeautifulSoup, soup2: BeautifulSoup) -> List[str]:
        """Compare document formatting."""
        differences = []

        # Compare basic structure
        tables1 = len(soup1.find_all('table'))
        tables2 = len(soup2.find_all('table'))
        if tables1 != tables2:
            differences.append(f"Table count differs: {tables1} vs {tables2}")

        lists1 = len(soup1.find_all(['ul', 'ol']))
        lists2 = len(soup2.find_all(['ul', 'ol']))
        if lists1 != lists2:
            differences.append(f"List count differs: {lists1} vs {lists2}")

        return differences


class EnhancedTemplateAnalyzer:
    """Enhanced template analyzer using both python-docx and Mammoth."""

    def __init__(self, template_path: str):
        """Initialize with both analysis methods."""
        self.template_path = template_path
        self.docx_analyzer = None  # Will be set if available
        self.mammoth_processor = MammothDocxProcessor()

        # Try to initialize python-docx analyzer as fallback
        try:
            from .template_analyzer import TemplateAnalyzer
            self.docx_analyzer = TemplateAnalyzer(template_path)
        except Exception as e:
            print(f"Warning: python-docx analyzer failed: {e}")

    def analyze_template(self) -> Dict[str, Any]:
        """Analyze template using the best available method."""
        # Prefer Mammoth for cleaner analysis
        try:
            mammoth_analysis = self.mammoth_processor.analyze_template_structure(self.template_path)

            # Enhance with python-docx data if available
            if self.docx_analyzer:
                docx_data = self.docx_analyzer.analysis
                mammoth_analysis['docx_fallback'] = docx_data

            return {
                'method': 'mammoth',
                'analysis': mammoth_analysis,
                'success': True
            }

        except Exception as e:
            print(f"Mammoth analysis failed, falling back to python-docx: {e}")

            if self.docx_analyzer:
                return {
                    'method': 'python-docx',
                    'analysis': self.docx_analyzer.analysis,
                    'success': True
                }
            else:
                return {
                    'method': 'failed',
                    'error': str(e),
                    'success': False
                }

    def convert_to_structured_format(self) -> Optional[Dict[str, Any]]:
        """Convert template to structured format using available method."""
        if self.docx_analyzer:
            return self.docx_analyzer.convert_to_structured_format()

        return None