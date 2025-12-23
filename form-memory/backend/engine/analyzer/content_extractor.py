"""
Content Extractor
Extracts sections and content from DOCX/text files for intelligent mapping.
"""

from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path
import re
from docx import Document


class ContentExtractor:
    """Extracts and structures content from source files."""
    
    def __init__(self, content_path: str):
        """Initialize with content file (DOCX or TXT)."""
        self.content_path = Path(content_path)
        self.is_docx = self.content_path.suffix.lower() == '.docx'
        self.content = self._load_content()
    
    def _load_content(self) -> Dict[str, Any]:
        """Load content from file."""
        if self.is_docx:
            return self._extract_from_docx()
        else:
            return self._extract_from_text()
    
    def _extract_from_docx(self) -> Dict[str, Any]:
        """Extract content from DOCX file."""
        doc = Document(self.content_path)
        
        return {
            "sections": self._extract_sections_from_docx(doc),
            "raw_text": self._get_docx_text(doc),
            "tables": self._extract_tables_from_docx(doc),
            "metadata": {
                "title": doc.core_properties.title or "",
                "author": doc.core_properties.author or "",
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
            (r"^BAB\s+([IVX]+|[0-9]+)\s*\n(.+?)$", "chapter"),
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
        return self.content["sections"]
    
    def get_raw_text(self) -> str:
        """Return raw text content."""
        return self.content["raw_text"]
    
    def get_tables(self) -> List[Dict[str, Any]]:
        """Return extracted tables."""
        return self.content["tables"]
    
    def get_section_by_title(self, title_pattern: str) -> Optional[Dict[str, Any]]:
        """Find section by title pattern."""
        for section in self.content["sections"]:
            if re.search(title_pattern, section["title"], re.IGNORECASE):
                return section
        return None
    
    def get_summary(self) -> str:
        """Return a summary of extracted content."""
        sections = self.content["sections"]
        
        summary = f"""
CONTENT EXTRACTION SUMMARY
==========================

Total Sections: {len(sections)}

Sections Found:
"""
        for section in sections[:10]:  # First 10
            summary += f"- {section['title']} (Level {section['level']})\n"
        
        if len(sections) > 10:
            summary += f"... and {len(sections) - 10} more\n"
        
        summary += f"\nTables: {len(self.content['tables'])}\n"
        summary += f"Total Content Length: {len(self.content['raw_text'])} characters"
        
        return summary.strip()
