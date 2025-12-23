"""
Universal Template Analyzer
Dynamically analyzes DOCX templates from any university to detect:
- Required sections and their order
- Paragraph styles (fonts, sizes, spacing, indentation)
- Heading hierarchy
- Placeholders
- Special formatting rules
"""

from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path
import re
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.style import WD_STYLE_TYPE


class TemplateAnalyzer:
    """Analyzes DOCX templates to extract formatting rules and structure."""
    
    def __init__(self, template_path: str):
        """Initialize with a DOCX template."""
        self.template_path = Path(template_path)
        self.doc = Document(self.template_path)
        self.analysis = self._analyze()
    
    def _analyze(self) -> Dict[str, Any]:
        """Perform complete template analysis."""
        return {
            "styles": self._extract_styles(),
            "structure": self._detect_structure(),
            "placeholders": self._detect_placeholders(),
            "sections": self._analyze_sections(),
            "formatting_rules": self._detect_formatting_rules(),
            "front_matter": self._detect_front_matter(),
            "document_properties": self._extract_properties(),
            "margins": self._extract_margins(),
            "heading_hierarchy": self._analyze_heading_hierarchy(),
            "special_elements": self._detect_special_elements(),
        }
    
    def _extract_styles(self) -> Dict[str, Dict[str, Any]]:
        """Extract all paragraph and character styles from template."""
        styles_info = {}
        
        for style in self.doc.styles:
            if style.type == WD_STYLE_TYPE.PARAGRAPH:
                # Get outline level safely - may not exist on all styles
                outline_level = None
                try:
                    outline_level_attr = style.element.xpath('.//w:outlineLvl/@w:val')
                    if outline_level_attr:
                        outline_level = int(outline_level_attr[0])
                except Exception:
                    outline_level = None
                
                style_data = {
                    "name": style.name,
                    "base_style": style.base_style.name if style.base_style else None,
                    "outline_level": outline_level,
                    "font": {
                        "name": style.font.name if style.font and style.font.name else "Calibri",
                        "size": style.font.size.pt if style.font and style.font.size else 12,
                        "bold": style.font.bold if style.font else False,
                        "italic": style.font.italic if style.font else False,
                    },
                    "paragraph": {
                        "alignment": str(style.paragraph_format.alignment) if style.paragraph_format else None,
                        "line_spacing": style.paragraph_format.line_spacing if style.paragraph_format else None,
                        "space_before": style.paragraph_format.space_before if style.paragraph_format else None,
                        "space_after": style.paragraph_format.space_after if style.paragraph_format else None,
                        "left_indent": style.paragraph_format.left_indent if style.paragraph_format else None,
                        "first_line_indent": style.paragraph_format.first_line_indent if style.paragraph_format else None,
                    },
                    "usage_count": self._count_style_usage(style.name),
                }
                styles_info[style.name] = style_data
        
        return styles_info
    
    def _count_style_usage(self, style_name: str) -> int:
        """Count how many paragraphs use a specific style."""
        count = 0
        for para in self.doc.paragraphs:
            if para.style.name == style_name:
                count += 1
        return count
    
    def _detect_structure(self) -> Dict[str, List[Dict[str, Any]]]:
        """Detect document structure (headings, sections, hierarchy)."""
        structure = {
            "headings": [],
            "paragraphs": [],
            "tables": [],
            "hierarchy": []
        }
        
        current_heading_level = None
        
        for para in self.doc.paragraphs:
            # Detect headings - check for outline level in style
            outline_level = None
            if para.style:
                try:
                    outline_level_attr = para.style.element.xpath('.//w:outlineLvl/@w:val')
                    if outline_level_attr:
                        outline_level = int(outline_level_attr[0])
                except Exception:
                    outline_level = None
            
            if outline_level is not None:
                heading_data = {
                    "level": outline_level,
                    "style": para.style.name,
                    "text": para.text[:100],  # First 100 chars
                    "index": len(self.doc.paragraphs),
                }
                structure["headings"].append(heading_data)
                structure["hierarchy"].append(heading_data)
            
            # Detect key section markers
            if self._is_section_marker(para.text):
                structure["paragraphs"].append({
                    "type": "section_marker",
                    "text": para.text,
                    "style": para.style.name if para.style else None,
                })
        
        # Detect tables
        for table in self.doc.tables:
            structure["tables"].append({
                "rows": len(table.rows),
                "cols": len(table.columns),
                "has_header": self._has_table_header(table),
            })
        
        return structure
    
    def _is_section_marker(self, text: str) -> bool:
        """Check if text is a section marker (cover, approval, abstract, etc.)."""
        section_keywords = [
            "halaman judul", "cover", "halaman pengesahan", "pernyataan",
            "kata pengantar", "preface", "abstrak", "abstract", "sari",
            "daftar isi", "daftar tabel", "daftar gambar", "daftar lampiran",
            "glossary", "glosarium", "bibliography", "references", "daftar pustaka",
            "appendix", "lampiran", "bab", "chapter", "kesimpulan", "conclusion"
        ]
        text_lower = text.lower().strip()
        return any(keyword in text_lower for keyword in section_keywords)
    
    def _has_table_header(self, table) -> bool:
        """Check if table has a header row."""
        if len(table.rows) == 0:
            return False
        first_row = table.rows[0]
        # Header rows typically have shading or bold text
        for cell in first_row.cells:
            for para in cell.paragraphs:
                if para.runs and any(run.bold for run in para.runs):
                    return True
        return False
    
    def _detect_placeholders(self) -> Dict[str, List[str]]:
        """Detect placeholder text that needs to be replaced."""
        placeholders = {
            "text_placeholders": [],
            "field_codes": [],
            "blank_sections": []
        }
        
        placeholder_patterns = [
            r"\[.*?\]",  # [Placeholder]
            r"\{.*?\}",  # {Placeholder}
            r"{{.*?}}",  # {{Placeholder}} Jinja2-style
            r"TULIS\s+.*?(?=\n|$)",  # TULIS... (Indonesian)
            r"BAGIAN\s+.*?(?=\n|$)",  # BAGIAN... (Indonesian)
            r"<.*?>",  # <Placeholder>
        ]
        
        for para in self.doc.paragraphs:
            text = para.text
            for pattern in placeholder_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    placeholders["text_placeholders"].extend(matches)
        
        # Also check for field codes
        for para in self.doc.paragraphs:
            if hasattr(para, '_element'):
                fldChar = para._element.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}fldChar')
                if fldChar:
                    placeholders["field_codes"].append(para.text)
        
        return placeholders
    
    def _analyze_sections(self) -> Dict[str, Any]:
        """Analyze document sections (headers, footers, page setup)."""
        sections_info = {}
        
        if self.doc.sections:
            section = self.doc.sections[0]
            
            # Safely extract gutter_margin from XML (may not exist)
            gutter_margin = None
            try:
                gutter_elem = section._sectPr.xpath('.//w:pgMar/@w:gutter')
                if gutter_elem:
                    # Convert from twips to inches (1 inch = 1440 twips)
                    gutter_margin = int(gutter_elem[0]) / 1440.0
            except Exception:
                gutter_margin = None
            
            sections_info = {
                "page_height": section.page_height.inches,
                "page_width": section.page_width.inches,
                "top_margin": section.top_margin.inches if section.top_margin else None,
                "bottom_margin": section.bottom_margin.inches if section.bottom_margin else None,
                "left_margin": section.left_margin.inches if section.left_margin else None,
                "right_margin": section.right_margin.inches if section.right_margin else None,
                "header_exists": len(section.header.paragraphs) > 0,
                "footer_exists": len(section.footer.paragraphs) > 0,
                "gutter_margin": gutter_margin,
            }
        
        return sections_info
    
    def _detect_formatting_rules(self) -> Dict[str, Any]:
        """Detect special formatting rules (spacing, indentation, alignment)."""
        rules = {
            "common_font": self._detect_common_font(),
            "common_font_size": self._detect_common_font_size(),
            "indentation_pattern": self._detect_indentation_pattern(),
            "spacing_pattern": self._detect_spacing_pattern(),
            "alignment_pattern": self._detect_alignment_pattern(),
            "line_spacing_pattern": self._detect_line_spacing_pattern(),
        }
        return rules
    
    def _detect_common_font(self) -> str:
        """Detect most common font in document."""
        fonts = {}
        for para in self.doc.paragraphs:
            for run in para.runs:
                font_name = run.font.name or "Calibri"
                fonts[font_name] = fonts.get(font_name, 0) + 1
        
        return max(fonts, key=fonts.get) if fonts else "Times New Roman"
    
    def _detect_common_font_size(self) -> float:
        """Detect most common font size in document."""
        sizes = {}
        for para in self.doc.paragraphs:
            for run in para.runs:
                if run.font.size:
                    size = run.font.size.pt
                    sizes[size] = sizes.get(size, 0) + 1
        
        return max(sizes, key=sizes.get) if sizes else 12.0
    
    def _detect_indentation_pattern(self) -> Dict[str, Any]:
        """Detect paragraph indentation patterns."""
        indents = {"first_line": [], "left": [], "right": []}
        
        for para in self.doc.paragraphs:
            if para.paragraph_format:
                pf = para.paragraph_format
                if pf.first_line_indent:
                    indents["first_line"].append(pf.first_line_indent.inches)
                if pf.left_indent:
                    indents["left"].append(pf.left_indent.inches)
                if pf.right_indent:
                    indents["right"].append(pf.right_indent.inches)
        
        return {
            "common_first_line": max(set(indents["first_line"]), key=indents["first_line"].count) if indents["first_line"] else 0,
            "common_left": max(set(indents["left"]), key=indents["left"].count) if indents["left"] else 0,
        }
    
    def _detect_spacing_pattern(self) -> Dict[str, Any]:
        """Detect paragraph spacing patterns."""
        space_before = {}
        space_after = {}
        
        for para in self.doc.paragraphs:
            if para.paragraph_format:
                pf = para.paragraph_format
                if pf.space_before:
                    sb = pf.space_before.pt
                    space_before[sb] = space_before.get(sb, 0) + 1
                if pf.space_after:
                    sa = pf.space_after.pt
                    space_after[sa] = space_after.get(sa, 0) + 1
        
        return {
            "common_space_before": max(space_before, key=space_before.get) if space_before else 0,
            "common_space_after": max(space_after, key=space_after.get) if space_after else 0,
        }
    
    def _detect_alignment_pattern(self) -> str:
        """Detect common paragraph alignment."""
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        alignments = {}
        
        for para in self.doc.paragraphs:
            if para.paragraph_format and para.paragraph_format.alignment:
                align = str(para.paragraph_format.alignment)
                alignments[align] = alignments.get(align, 0) + 1
        
        return max(alignments, key=alignments.get) if alignments else "CENTER"
    
    def _detect_line_spacing_pattern(self) -> float:
        """Detect common line spacing."""
        spacings = {}
        
        for para in self.doc.paragraphs:
            if para.paragraph_format and para.paragraph_format.line_spacing:
                spacing = para.paragraph_format.line_spacing
                spacings[spacing] = spacings.get(spacing, 0) + 1
        
        return max(spacings, key=spacings.get) if spacings else 1.5
    
    def _detect_front_matter(self) -> Dict[str, Any]:
        """Detect front matter sections (cover, approval, etc.)."""
        front_matter = {
            "sections": [],
            "page_breaks": [],
            "required_sections": []
        }
        
        section_markers = [
            ("cover", ["halaman judul", "cover", "judul"]),
            ("approval", ["pengesahan", "approval", "persetujuan"]),
            ("statement", ["pernyataan", "declaration", "keaslian"]),
            ("dedication", ["persembahan", "dedication"]),
            ("motto", ["motto"]),
            ("preface", ["kata pengantar", "preface", "pengantar"]),
            ("abstract_id", ["abstrak", "ringkasan"]),
            ("abstract_en", ["abstract"]),
            ("glossary", ["glosarium", "glossary", "istilah"]),
            ("toc", ["daftar isi", "table of contents"]),
            ("list_figures", ["daftar gambar", "list of figures"]),
            ("list_tables", ["daftar tabel", "list of tables"]),
        ]
        
        for para in self.doc.paragraphs:
            text_lower = para.text.lower().strip()
            for section_type, keywords in section_markers:
                if any(kw in text_lower for kw in keywords):
                    front_matter["sections"].append(section_type)
                    front_matter["required_sections"].append(section_type)
        
        return front_matter
    
    def _extract_properties(self) -> Dict[str, str]:
        """Extract document properties (title, author, etc.)."""
        props = self.doc.core_properties
        return {
            "title": props.title or "",
            "author": props.author or "",
            "subject": props.subject or "",
            "keywords": props.keywords or "",
            "created": str(props.created) if props.created else "",
            "modified": str(props.modified) if props.modified else "",
        }
    
    def _extract_margins(self) -> Dict[str, float]:
        """Extract document margins."""
        if not self.doc.sections:
            return {}
        
        section = self.doc.sections[0]
        return {
            "top": section.top_margin.inches if section.top_margin else 1.0,
            "bottom": section.bottom_margin.inches if section.bottom_margin else 1.0,
            "left": section.left_margin.inches if section.left_margin else 1.0,
            "right": section.right_margin.inches if section.right_margin else 1.0,
        }
    
    def _analyze_heading_hierarchy(self) -> Dict[str, Any]:
        """Analyze heading hierarchy (e.g., BAB, subbab 1.1)."""
        hierarchy = {
            "heading_styles": {},
            "numbering_pattern": None,
            "title_format": None
        }
        
        heading_styles = {}
        for para in self.doc.paragraphs:
            if para.style:
                # Safely extract outline level from XML
                outline_level = None
                try:
                    outline_level_attr = para.style.element.xpath('.//w:outlineLvl/@w:val')
                    if outline_level_attr:
                        outline_level = int(outline_level_attr[0])
                except Exception:
                    outline_level = None
                
                if outline_level is not None:
                    style_name = para.style.name
                    if style_name not in heading_styles:
                        heading_styles[style_name] = {
                            "level": outline_level,
                            "examples": []
                        }
                    if len(heading_styles[style_name]["examples"]) < 3:
                        heading_styles[style_name]["examples"].append(para.text[:50])
        
        hierarchy["heading_styles"] = heading_styles
        
        # Detect numbering pattern
        for para in self.doc.paragraphs:
            if para.text and re.match(r"^(BAB|CHAPTER)\s+[IVX]+", para.text):
                hierarchy["numbering_pattern"] = "roman_uppercase"
            elif para.text and re.match(r"^(BAB|CHAPTER)\s+\d+", para.text):
                hierarchy["numbering_pattern"] = "arabic"
        
        return hierarchy
    
    def _detect_special_elements(self) -> Dict[str, List[str]]:
        """Detect special elements (tables, figures, equations, etc.)."""
        special = {
            "tables": [],
            "figures": [],
            "equations": [],
            "code_blocks": [],
            "text_boxes": [],
            "shapes": []
        }
        
        # Count tables
        for i, table in enumerate(self.doc.tables):
            special["tables"].append(f"Table {i+1}")
        
        # Detect figure/table captions
        for para in self.doc.paragraphs:
            text_lower = para.text.lower()
            if "gambar" in text_lower or "figure" in text_lower:
                special["figures"].append(para.text[:50])
            elif "persamaan" in text_lower or "equation" in text_lower:
                special["equations"].append(para.text[:50])
        
        return special
    
    def get_analysis(self) -> Dict[str, Any]:
        """Return the complete analysis."""
        return self.analysis
    
    def get_summary(self) -> str:
        """Return a human-readable summary of template analysis."""
        summary = f"""
TEMPLATE ANALYSIS SUMMARY
=========================

Document Properties:
- Title: {self.analysis['document_properties'].get('title', 'N/A')}
- Author: {self.analysis['document_properties'].get('author', 'N/A')}

Page Setup:
- Margins: L={self.analysis['margins'].get('left', 1.0)}" T={self.analysis['margins'].get('top', 1.0)}" R={self.analysis['margins'].get('right', 1.0)}" B={self.analysis['margins'].get('bottom', 1.0)}"

Formatting Rules:
- Primary Font: {self.analysis['formatting_rules']['common_font']}
- Primary Font Size: {self.analysis['formatting_rules']['common_font_size']}pt
- Line Spacing: {self.analysis['formatting_rules']['line_spacing_pattern']}
- First Line Indent: {self.analysis['formatting_rules']['indentation_pattern']['common_first_line']}"

Front Matter Sections Detected:
- {', '.join(self.analysis['front_matter']['sections']) or 'None detected'}

Detected Styles: {len(self.analysis['styles'])}
- Heading Styles: {[s for s in self.analysis['styles'] if 'Heading' in s]}

Special Elements:
- Tables: {len(self.analysis['special_elements']['tables'])}
- Figures: {len(self.analysis['special_elements']['figures'])}
- Equations: {len(self.analysis['special_elements']['equations'])}

Placeholders Found: {len(self.analysis['placeholders']['text_placeholders'])}
- Examples: {self.analysis['placeholders']['text_placeholders'][:3]}
"""
        return summary.strip()
