"""
Content Extractor
Extracts sections and content from DOCX/text files for intelligent mapping.
"""

from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path
import re
from docx import Document
from docx import shared as docx_shared


class ContentExtractor:
    """Extracts and structures content from source files."""
    
    def __init__(self, content_path: str):
        """Initialize content extractor."""
        self.content_path = Path(content_path)
        self.is_docx = self.content_path.suffix.lower() == '.docx'
        # Load content data
        content_data = self._load_content()
        self._sections = content_data.get("sections", [])
        self._raw_text = content_data.get("raw_text", "")
    
    def _load_content(self) -> Dict[str, Any]:
        """Load content from file."""
        if self.is_docx:
            return self._extract_from_docx()
        else:
            return self._extract_from_text()
    
    def _extract_from_docx(self) -> Dict[str, Any]:
        """Extract content from DOCX file with enhanced handling of poorly-formatted documents."""
        doc = Document(str(self.content_path))

        # Clean up the document first
        cleaned_doc = self._clean_docx_formatting(doc)

        return {
            "sections": self._extract_sections_from_docx(cleaned_doc),
            "raw_text": self._get_docx_text(cleaned_doc),
            "tables": self._extract_tables_from_docx(cleaned_doc),
            "metadata": {
                "title": doc.core_properties.title or "",
                "author": doc.core_properties.author or "",
                "formatting_quality": self._assess_docx_quality(doc),
                "needs_cleanup": self._detect_formatting_issues(doc)
            }
        }
    
    def _extract_from_text(self) -> Dict[str, Any]:
        """Extract content from TXT file."""
        with open(self.content_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        return {
            "sections": self._extract_sections_from_text(text),
            "raw_text": text,
            "tables": [],
            "metadata": {}
        }
    
    def _extract_sections_from_docx(self, doc) -> List[Dict[str, Any]]:
        """Extract sections from DOCX by headings."""
        sections = []
        current_section = None
        
        for para in doc.paragraphs:
            # Check if paragraph is a heading - safe access to outline level
            outline_level = None
            if para.style:
                try:
                    outline_level_attr = para.style.element.xpath('.//w:outlineLvl/@w:val')
                    if outline_level_attr:
                        outline_level = int(outline_level_attr[0])
                except Exception:
                    outline_level = None
            
            if outline_level is not None:
                # Save previous section
                if current_section:
                    sections.append(current_section)
                
                # Start new section
                current_section = {
                    "title": para.text,
                    "level": outline_level,
                    "content": [],
                    "style": para.style.name,
                }
            elif current_section is not None:
                # Add to current section
                if para.text.strip():
                    current_section["content"].append(para.text)
        
        # Don't forget the last section
        if current_section:
            sections.append(current_section)
        
        return sections
    
    def _extract_sections_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract sections from plain text by detecting heading patterns."""
        sections = []
        
        # Patterns for headings
        heading_patterns = [
            (r"^BAB\s+([IVX]+|[0-9]+)[:.]?\s*(.+?)$", "chapter"),
            (r"^([0-9]+\.[0-9]+)\s+(.+?)$", "section"),
            (r"^#+ (.+?)$", "markdown"),
        ]
        
        lines = text.split('\n')
        current_section = None
        
        for line in lines:
            matched = False
            for pattern, heading_type in heading_patterns:
                match = re.match(pattern, line.strip())
                if match:
                    # Save previous section
                    if current_section:
                        sections.append(current_section)
                    
                    # Start new section
                    current_section = {
                        "title": line.strip(),
                        "level": 0,
                        "content": [],
                        "type": heading_type,
                    }
                    matched = True
                    break
            
            if not matched and current_section is not None:
                if line.strip():
                    current_section["content"].append(line)
        
        if current_section:
            sections.append(current_section)
        
        return sections
    
    def _get_docx_text(self, doc) -> str:
        """Get all text from DOCX."""
        return '\n'.join(para.text for para in doc.paragraphs)
    
    def _extract_tables_from_docx(self, doc) -> List[Dict[str, Any]]:
        """Extract tables from DOCX."""
        tables = []
        
        for i, table in enumerate(doc.tables):
            table_data = {
                "index": i,
                "rows": len(table.rows),
                "cols": len(table.columns),
                "content": []
            }
            
            # Extract table content
            for row in table.rows:
                row_data = []
                for cell in row.cells:
                    cell_text = '\n'.join(para.text for para in cell.paragraphs)
                    row_data.append(cell_text)
                table_data["content"].append(row_data)
            
            tables.append(table_data)
        
        return tables
    
    def get_sections(self) -> List[Dict[str, Any]]:
        """Return extracted sections."""
        return self._sections if self._sections else []
    
    def get_raw_text(self) -> str:
        """Return raw text content."""
        return self._raw_text
    
    def get_tables(self) -> List[Dict[str, Any]]:
        """Return extracted tables."""
        content_data = self._load_content()
        return content_data.get("tables", [])
    
    def get_section_by_title(self, title_pattern: str) -> Optional[Dict[str, Any]]:
        """Find section by title pattern."""
        for section in self._sections:
            if re.search(title_pattern, section["title"], re.IGNORECASE):
                return section
        return None
    
    def get_summary(self) -> Dict[str, Any]:
        """Get extraction summary."""
        summary = f"Total Content Length: {len(self.get_raw_text())} characters"
        
        return {
            "summary": summary.strip(),
            "sections_count": len(self.get_sections()),
            "file_type": "docx" if self.is_docx else "text"
        }

    def _clean_docx_formatting(self, doc) -> Document:
        """Clean up poorly-formatted DOCX documents."""
        # Create a new document for cleaned content
        from docx import Document as NewDocument
        cleaned_doc = NewDocument()

        # Copy styles from original to cleaned document
        self._copy_styles_to_clean_doc(doc, cleaned_doc)

        # Process paragraphs and clean formatting
        for para in doc.paragraphs:
            if para.text.strip():  # Skip empty paragraphs
                cleaned_para = cleaned_doc.add_paragraph()
                cleaned_para.text = self._clean_paragraph_text(para.text)

                # Apply basic formatting rules
                self._apply_clean_formatting(cleaned_para, para)

        return cleaned_doc

    def _copy_styles_to_clean_doc(self, source_doc, target_doc) -> None:
        """Copy essential styles to cleaned document."""
        essential_styles = ['Normal', 'Heading 1', 'Heading 2', 'Heading 3']

        for style_name in essential_styles:
            try:
                source_style = source_doc.styles[style_name]
                if style_name not in target_doc.styles:
                    new_style = target_doc.styles.add_style(style_name, source_style.type)
                    # Copy basic properties
                    if hasattr(source_style, 'font') and source_style.font:
                        if source_style.font.name:
                            new_style.font.name = source_style.font.name
                        if source_style.font.size:
                            new_style.font.size = source_style.font.size
            except KeyError:
                continue

    def _clean_paragraph_text(self, text: str) -> str:
        """Clean paragraph text from formatting artifacts."""
        if not text:
            return text

        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())

        # Remove formatting artifacts (common in poorly scanned/converted documents)
        text = re.sub(r'[^\w\s\.,;:!?\-\(\)\[\]{}"\'/]', '', text)

        # Fix common OCR errors in Indonesian text
        text = self._fix_indonesian_ocr_errors(text)

        return text

    def _fix_indonesian_ocr_errors(self, text: str) -> str:
        """Fix common OCR errors in Indonesian academic text."""
        # Common OCR errors in Indonesian text
        ocr_fixes = {
            'yang': ['yang', 'yang', 'yang'],  # Often misread
            'dengan': ['dengan', 'dengan'],
            'untuk': ['untuk', 'untuk'],
            'dari': ['dari', 'dari'],
            'dalam': ['dalam', 'dalam'],
            'pada': ['pada', 'pada'],
            'oleh': ['oleh', 'oleh'],
            'telah': ['telah', 'telah'],
            'akan': ['akan', 'akan'],
            'adalah': ['adalah', 'adalah'],
            'bahwa': ['bahwa', 'bahwa'],
            'karena': ['karena', 'karena']
        }

        # This would implement more sophisticated OCR correction
        # For now, return the text as-is
        return text

    def _apply_clean_formatting(self, cleaned_para, original_para) -> None:
        """Apply clean formatting to paragraph."""
        # Set basic academic formatting
        para_format = cleaned_para.paragraph_format
        para_format.line_spacing = 1.5
        para_format.space_before = 0
        para_format.space_after = 0

        # First line indentation for body text
        if not self._is_heading(original_para):
            para_format.first_line_indent = docx_shared.Inches(0.5)  # 1.27 cm ≈ 0.5 inches

        # Justified alignment for academic text
        para_format.alignment = 3  # Justified

    def _is_heading(self, para) -> bool:
        """Check if paragraph is a heading."""
        if not para.style:
            return False

        style_name = para.style.name.lower()
        return 'heading' in style_name or 'title' in style_name

    def _assess_docx_quality(self, doc) -> str:
        """Assess the quality of DOCX formatting."""
        issues = 0
        total_checks = 5

        # Check for inconsistent fonts
        fonts = set()
        for para in doc.paragraphs[:50]:  # Sample first 50 paragraphs
            for run in para.runs:
                if run.font.name:
                    fonts.add(run.font.name)

        if len(fonts) > 3:
            issues += 1

        # Check for inconsistent font sizes
        sizes = set()
        for para in doc.paragraphs[:50]:
            for run in para.runs:
                if run.font.size:
                    sizes.add(run.font.size.pt)

        if len(sizes) > 4:
            issues += 1

        # Check for proper paragraph structure
        empty_paras = sum(1 for para in doc.paragraphs[:100] if not para.text.strip())
        if empty_paras > 20:  # Too many empty paragraphs
            issues += 1

        # Check for proper heading hierarchy
        heading_count = sum(1 for para in doc.paragraphs[:100]
                          if para.style and 'heading' in para.style.name.lower())
        if heading_count < 3:  # Should have at least some headings
            issues += 1

        quality_score = (total_checks - issues) / total_checks

        if quality_score >= 0.8:
            return "excellent"
        elif quality_score >= 0.6:
            return "good"
        elif quality_score >= 0.4:
            return "fair"
        else:
            return "poor"

    def _detect_formatting_issues(self, doc) -> Dict[str, Any]:
        """Detect specific formatting issues in DOCX."""
        issues = {
            "needs_cleanup": False,
            "issues_found": [],
            "severity": "low"
        }

        # Check for common formatting problems
        font_inconsistencies = 0
        spacing_issues = 0
        structure_problems = 0

        fonts_seen = set()
        for para in doc.paragraphs[:100]:
            for run in para.runs:
                if run.font.name:
                    fonts_seen.add(run.font.name)

        if len(fonts_seen) > 5:
            font_inconsistencies = 1
            issues["issues_found"].append("Multiple fonts used inconsistently")

        # Check spacing
        line_spacings = []
        for para in doc.paragraphs[:50]:
            if para.paragraph_format.line_spacing:
                line_spacings.append(para.paragraph_format.line_spacing)

        if line_spacings:
            avg_spacing = sum(line_spacings) / len(line_spacings)
            if not (1.3 <= avg_spacing <= 1.8):  # Not standard 1.5 spacing
                spacing_issues = 1
                issues["issues_found"].append("Inconsistent line spacing")

        # Structure check
        heading_count = sum(1 for para in doc.paragraphs[:100]
                          if para.style and 'heading' in para.style.name.lower())
        if heading_count == 0:
            structure_problems = 1
            issues["issues_found"].append("No proper heading structure detected")

        total_issues = font_inconsistencies + spacing_issues + structure_problems
        issues["needs_cleanup"] = total_issues > 0

        if total_issues >= 2:
            issues["severity"] = "high"
        elif total_issues == 1:
            issues["severity"] = "medium"

        return issues
