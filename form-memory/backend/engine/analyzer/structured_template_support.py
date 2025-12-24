"""
JSON/XML Template Format Support
Provides structured template definitions for Indonesian universities,
enabling precise, fast template processing without DOCX analysis overhead.
"""

import json
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional, Union
from pathlib import Path


class TemplateDefinition:
    """Structured template definition for Indonesian universities."""

    TEMPLATE_SCHEMA = {
        "metadata": {
            "university": "string",  # e.g., "UI", "ITB", "UGM"
            "faculty": "string",     # e.g., "FIB", "FTI", "FEB"
            "program": "string",     # e.g., "Ilmu Komputer", "Teknik Informatika"
            "version": "string",     # e.g., "2024.1"
            "standard": "string"     # e.g., "SK_MENDIKBUD_2020"
        },
        "document_properties": {
            "page_size": {"width": "number", "height": "number"},  # inches
            "margins": {"top": "number", "bottom": "number", "left": "number", "right": "number"},
            "orientation": "string"  # "portrait" or "landscape"
        },
        "typography": {
            "fonts": {
                "primary": "string",
                "secondary": "string",
                "monospace": "string"
            },
            "sizes": {
                "title": "number",
                "chapter": "number",
                "section": "number",
                "subsection": "number",
                "body": "number",
                "caption": "number",
                "footnote": "number"
            },
            "line_spacing": "number",
            "paragraph_spacing": {"before": "number", "after": "number"}
        },
        "structure": {
            "front_matter": [
                {
                    "type": "string",  # e.g., "title_page", "approval_page", "preface"
                    "required": "boolean",
                    "style": "string",  # style name or definition
                    "content_template": "string"  # template for AI generation
                }
            ],
            "main_content": {
                "chapter_pattern": "string",  # regex for chapter detection
                "section_pattern": "string",  # regex for section detection
                "heading_styles": {
                    "level_1": "style_definition",
                    "level_2": "style_definition",
                    "level_3": "style_definition"
                }
            },
            "back_matter": [
                {
                    "type": "string",
                    "required": "boolean",
                    "style": "string"
                }
            ]
        },
        "styles": {
            "paragraph_styles": {
                "style_name": {
                    "font": "string",
                    "size": "number",
                    "bold": "boolean",
                    "italic": "boolean",
                    "alignment": "string",  # "left", "center", "right", "justify"
                    "line_spacing": "number",
                    "indentation": {
                        "first_line": "number",
                        "left": "number",
                        "right": "number"
                    }
                }
            },
            "character_styles": {
                "style_name": "style_definition"
            }
        },
        "numbering": {
            "chapters": {
                "format": "string",  # "roman_upper", "arabic", "custom"
                "start_number": "number"
            },
            "sections": {
                "format": "string",
                "separator": "string"  # ".", "-", etc.
            },
            "lists": {
                "bullet_style": "string",
                "number_style": "string"
            }
        },
        "citations": {
            "style": "string",  # "APA", "MLA", "Chicago", "Harvard"
            "in_text_format": "string",
            "bibliography_format": "string"
        },
        "validation_rules": {
            "required_sections": ["array", "of", "section_types"],
            "font_restrictions": ["array", "of", "allowed", "fonts"],
            "size_limits": {
                "min_body_size": "number",
                "max_title_size": "number"
            },
            "margin_requirements": {
                "min_left_margin": "number",
                "max_top_margin": "number"
            }
        }
    }


class JSONTemplateLoader:
    """Loads and validates JSON template definitions."""

    @staticmethod
    def load_template(template_path: Union[str, Path]) -> Dict[str, Any]:
        """Load template from JSON file."""
        path = Path(template_path)

        if not path.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")

        if path.suffix.lower() != '.json':
            raise ValueError("Template file must be JSON format")

        with open(path, 'r', encoding='utf-8') as f:
            template_data = json.load(f)

        # Validate template structure
        JSONTemplateLoader._validate_template(template_data)

        return template_data

    @staticmethod
    def _validate_template(template_data: Dict[str, Any]) -> None:
        """Validate template structure against schema."""
        required_keys = ['metadata', 'typography', 'structure']

        for key in required_keys:
            if key not in template_data:
                raise ValueError(f"Missing required template section: {key}")

        # Validate metadata
        metadata = template_data.get('metadata', {})
        if 'university' not in metadata:
            raise ValueError("Template metadata must include university")

        # Validate typography
        typography = template_data.get('typography', {})
        if 'fonts' not in typography or 'sizes' not in typography:
            raise ValueError("Template must define typography fonts and sizes")

    @staticmethod
    def save_template(template_data: Dict[str, Any], output_path: Union[str, Path]) -> None:
        """Save template to JSON file."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(template_data, f, indent=2, ensure_ascii=False)


class XMLTemplateLoader:
    """Loads and converts XML template definitions."""

    @staticmethod
    def load_template(template_path: Union[str, Path]) -> Dict[str, Any]:
        """Load template from XML file and convert to dict format."""
        path = Path(template_path)

        if not path.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")

        if path.suffix.lower() not in ['.xml', '.tpl']:
            raise ValueError("Template file must be XML format")

        tree = ET.parse(str(path))
        root = tree.getroot()

        # Convert XML to dictionary format
        template_data = XMLTemplateLoader._xml_to_dict(root)

        # Ensure it's a dictionary
        if isinstance(template_data, str):
            raise ValueError("XML template must contain structured data, not plain text")

        # Validate and normalize
        JSONTemplateLoader._validate_template(template_data)

        return template_data

    @staticmethod
    def _xml_to_dict(element: ET.Element) -> Union[Dict[str, Any], str]:
        """Convert XML element to dictionary."""
        result = {}

        # Handle attributes
        if element.attrib:
            result.update(element.attrib)

        # Handle child elements
        children = list(element)

        if not children:
            # Simple text element
            text = element.text.strip() if element.text else ""
            if text:
                return text
            return {}

        # Complex element with children
        for child in children:
            child_dict = XMLTemplateLoader._xml_to_dict(child)

            # Handle multiple elements with same tag
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_dict)
            else:
                result[child.tag] = child_dict

        return result


class TemplateConverter:
    """Converts DOCX templates to JSON/XML format for faster processing."""

    def __init__(self, template_analyzer):
        self.analyzer = template_analyzer
        self.analysis = template_analyzer.analysis

    def convert_to_json(self, output_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
        """Convert analyzed DOCX template to comprehensive JSON format."""
        # Build comprehensive JSON template structure from analysis
        json_template = {
            "metadata": {
                "university": self._detect_university_from_analysis(),
                "faculty": self._detect_faculty_from_analysis(),
                "program": "auto_detected",
                "version": "1.0",
                "standard": "SK_MENDIKBUD_2020",
                "converted_from": "docx_analysis",
                "analysis_date": "dynamic",
                "source_file": str(getattr(self.analyzer, 'template_path', 'unknown'))
            },
            "document_properties": {
                "page_size": {"width": 8.27, "height": 11.69},  # A4 in inches
                "margins": self.analysis.get("margins", {
                    "top": 1.0, "bottom": 1.0, "left": 1.25, "right": 1.0
                }),
                "orientation": "portrait",
                "gutter": 0
            },
            "typography": {
                "fonts": {
                    "primary": self.analysis.get("formatting_rules", {}).get("common_font", "Times New Roman"),
                    "secondary": "Arial",
                    "monospace": "Courier New"
                },
                "sizes": {
                    "title": 16,
                    "chapter": 14,
                    "section": 12,
                    "subsection": 12,
                    "body": self.analysis.get("formatting_rules", {}).get("common_font_size", 12),
                    "caption": 11,
                    "footnote": 10
                },
                "line_spacing": self.analysis.get("formatting_rules", {}).get("line_spacing_pattern", 1.5),
                "paragraph_spacing": {
                    "before": 0,
                    "after": 0
                },
                "indentation": {
                    "first_line": self.analysis.get("formatting_rules", {}).get("indentation_pattern", {}).get("common_first_line", 1.25),
                    "hanging": 0
                }
            },
            "structure": {
                "front_matter": self._extract_front_matter_structure(),
                "main_content": {
                    "chapter_pattern": r"^BAB\s+[IVX]+\s*[:-]?\s*(.+)",
                    "section_pattern": r"^([0-9]+\.[0-9]+)\s+(.+)",
                    "subsection_pattern": r"^([0-9]+\.[0-9]+\.[0-9]+)\s+(.+)",
                    "heading_styles": self._extract_heading_styles()
                },
                "back_matter": self._extract_back_matter_structure()
            },
            "styles": {
                "paragraph_styles": self.analysis.get("styles", {}),
                "character_styles": {}
            },
            "numbering": {
                "chapters": {
                    "format": "roman_upper",
                    "prefix": "BAB ",
                    "suffix": " - ",
                    "start_number": 1
                },
                "sections": {
                    "format": "decimal",
                    "separator": ".",
                    "max_levels": 3
                },
                "figures": {
                    "format": "decimal",
                    "prefix": "Gambar ",
                    "separator": "."
                },
                "tables": {
                    "format": "decimal",
                    "prefix": "Tabel ",
                    "separator": "."
                },
                "equations": {
                    "format": "decimal",
                    "prefix": "(",
                    "suffix": ")"
                }
            },
            "citations": {
                "style": "APA",
                "in_text_format": "(Author, Year)",
                "bibliography_format": "Author. (Year). Title. Publisher.",
                "sort_order": "alphabetical",
                "hanging_indent": 1.0
            },
            "validation_rules": {
                "required_sections": self._get_required_sections(),
                "font_restrictions": ["Times New Roman", "Arial", "Calibri"],
                "size_limits": {
                    "min_body_size": 11,
                    "max_body_size": 12,
                    "min_title_size": 14,
                    "max_title_size": 18
                },
                "margin_requirements": {
                    "min_left_margin": 1.0,
                    "max_left_margin": 1.5,
                    "min_top_margin": 1.0,
                    "max_top_margin": 1.5
                },
                "spacing_requirements": {
                    "line_spacing": {
                        "min": 1.4,
                        "max": 1.6
                    },
                    "paragraph_spacing": {
                        "max_before": 6,
                        "max_after": 6
                    }
                },
                "structure_requirements": {
                    "max_heading_levels": 3,
                    "min_chapters": 3,
                    "max_chapters": 7,
                    "require_conclusion": True,
                    "require_references": True
                }
            },
            "auto_generation": {
                "table_of_contents": {
                    "enabled": True,
                    "max_levels": 3,
                    "include_page_numbers": True,
                    "format": "standard"
                },
                "list_of_tables": {
                    "enabled": True,
                    "format": "standard"
                },
                "list_of_figures": {
                    "enabled": True,
                    "format": "standard"
                }
            }
        }

        if output_path:
            JSONTemplateLoader.save_template(json_template, output_path)

        return json_template

    def _detect_university_from_analysis(self) -> str:
        """Detect university from current analysis data."""
        title = self.analysis.get("document_properties", {}).get("title", "").lower()

        university_patterns = {
            "UI": ["universitas indonesia", "ui", "fib", "fekon", "fmipa"],
            "ITB": ["institut teknologi bandung", "itb", "stei", "tf", "civil"],
            "UGM": ["ugm", "gadjah mada", "ugm", "feb", "fib", "fmipa"],
            "UNPAD": ["padjadjaran", "unpad", "feb", "fh", "fisip"],
            "IPB": ["institut pertanian bogor", "ipb", "fakultas"],
            "UNS": ["sebelas maret", "uns", "surakarta"],
            "UNDIP": ["diponegoro", "undip", "semarang"],
            "UNAIR": ["airlangga", "unair", "surabaya"],
            "UB": ["brawijaya", "ub", "malang"],
            "UNNES": ["negeri semarang", "unnes"]
        }

        for univ, patterns in university_patterns.items():
            if any(pattern in title for pattern in patterns):
                return univ

        return "GENERIC_INDONESIAN"

    def _detect_faculty_from_analysis(self) -> str:
        """Detect faculty from analysis data."""
        title = self.analysis.get("document_properties", {}).get("title", "").lower()

        faculty_patterns = {
            "FIB": ["fib", "ilmu budaya", "humanities"],
            "FTI": ["fti", "teknik informatika", "informatics"],
            "FEB": ["feb", "ekonomi bisnis", "economics"],
            "FMIPA": ["fmipa", "matematika", "science"],
            "FH": ["fh", "hukum", "law"],
            "FK": ["fk", "kedokteran", "medicine"]
        }

        for faculty, patterns in faculty_patterns.items():
            if any(pattern in title for pattern in patterns):
                return faculty

        return "GENERIC"

    def _extract_front_matter_structure(self) -> List[Dict[str, Any]]:
        """Extract front matter structure from current analysis."""
        front_sections = self.analysis.get("front_matter", {}).get("sections", [])
        structure = []

        section_mapping = {
            "halaman_judul": {"type": "title_page", "order": 1},
            "lembar_pengesahan": {"type": "approval_page", "order": 2},
            "pernyataan_keaslian": {"type": "originality_statement", "order": 3},
            "kata_pengantar": {"type": "preface", "order": 4},
            "abstrak": {"type": "abstract_id", "order": 5},
            "abstract": {"type": "abstract_en", "order": 6},
            "daftar_isi": {"type": "table_of_contents", "order": 7},
            "daftar_tabel": {"type": "list_of_tables", "order": 8},
            "daftar_gambar": {"type": "list_of_figures", "order": 9}
        }

        for section in front_sections:
            if section in section_mapping:
                info = section_mapping[section]
                structure.append({
                    "type": info["type"],
                    "required": True,
                    "style": "Normal",
                    "order": info["order"],
                    "content_template": f"Auto-generate {info['type']} content"
                })

        # Sort by order
        structure.sort(key=lambda x: x.get("order", 99))
        return structure

    def _extract_back_matter_structure(self) -> List[Dict[str, Any]]:
        """Extract back matter structure."""
        return [
            {
                "type": "references",
                "required": True,
                "style": "Normal",
                "order": 1
            },
            {
                "type": "appendices",
                "required": False,
                "style": "Normal",
                "order": 2
            }
        ]

    def _extract_heading_styles(self) -> Dict[str, Any]:
        """Extract heading styles from analysis."""
        heading_hierarchy = self.analysis.get("heading_hierarchy", {})
        heading_styles = heading_hierarchy.get("heading_styles", {})

        formatted_styles = {}
        for style_name, style_info in heading_styles.items():
            level = style_info.get("level", 1)
            level_key = f"level_{level}"

            formatted_styles[level_key] = {
                "font": self.analysis.get("formatting_rules", {}).get("common_font", "Times New Roman"),
                "size": style_info.get("font_size", 12),
                "bold": True,
                "alignment": "left",
                "spacing_before": 12 * level,
                "spacing_after": 6 * level,
                "page_break_before": level == 1,
                "numbering": self._get_heading_numbering(level)
            }

        return formatted_styles

    def _get_heading_numbering(self, level: int) -> str:
        """Get heading numbering format for level."""
        numbering_formats = {
            1: "BAB {ROMAN} - ",
            2: "{decimal} ",
            3: "{decimal}.{decimal} "
        }
        return numbering_formats.get(level, "")

    def _get_required_sections(self) -> List[str]:
        """Get list of required sections from analysis."""
        front_sections = self.analysis.get("front_matter", {}).get("sections", [])
        required = []

        # Map detected sections to required section types
        section_type_mapping = {
            "halaman_judul": "title_page",
            "lembar_pengesahan": "approval_page",
            "pernyataan_keaslian": "originality_statement",
            "kata_pengantar": "preface",
            "abstrak": "abstract_id",
            "abstract": "abstract_en",
            "daftar_isi": "table_of_contents"
        }

        for section in front_sections:
            if section in section_type_mapping:
                required.append(section_type_mapping[section])

        # Always include essential sections
        essential = ["title_page", "approval_page", "abstract_id", "table_of_contents", "bab_i", "references"]
        for essential_section in essential:
            if essential_section not in required:
                required.append(essential_section)

        return required


class StructuredTemplateAnalyzer:
    """Fast analyzer for JSON/XML templates."""

    def __init__(self, template_path: Union[str, Path]):
        """Initialize with JSON/XML template file."""
        self.template_path = Path(template_path)

        # Load template based on format
        if self.template_path.suffix.lower() == '.json':
            self.template_data = JSONTemplateLoader.load_template(template_path)
        elif self.template_path.suffix.lower() in ['.xml', '.tpl']:
            self.template_data = XMLTemplateLoader.load_template(template_path)
        else:
            raise ValueError("Template must be JSON or XML format")

        # Create analysis-compatible interface
        self.analysis = self._create_analysis_interface()

    def _create_analysis_interface(self) -> Dict[str, Any]:
        """Create analysis dictionary compatible with existing code."""
        data = self.template_data

        return {
            "styles": data.get("styles", {}).get("paragraph_styles", {}),
            "formatting_rules": {
                "common_font": data.get("typography", {}).get("fonts", {}).get("primary", "Times New Roman"),
                "common_font_size": data.get("typography", {}).get("sizes", {}).get("body", 12),
                "line_spacing_pattern": data.get("typography", {}).get("line_spacing", 1.5),
                "indentation_pattern": {
                    "common_first_line": data.get("typography", {}).get("sizes", {}).get("body", 12) * 0.1
                }
            },
            "margins": data.get("document_properties", {}).get("margins", {}),
            "structure": data.get("structure", {}),
            "front_matter": {
                "sections": [item["type"] for item in data.get("structure", {}).get("front_matter", [])]
            },
            "validation_rules": data.get("validation_rules", {}),
            "typography": data.get("typography", {}),
            "metadata": data.get("metadata", {})
        }

    def get_analysis(self) -> Dict[str, Any]:
        """Return the template analysis."""
        return self.analysis

    def get_summary(self) -> str:
        """Return a human-readable summary."""
        metadata = self.template_data.get("metadata", {})

        summary = f"""
TEMPLATE SUMMARY
================

University: {metadata.get('university', 'Unknown')}
Version: {metadata.get('version', 'N/A')}
Standard: {metadata.get('standard', 'N/A')}

Typography:
- Primary Font: {self.analysis['formatting_rules']['common_font']}
- Body Size: {self.analysis['formatting_rules']['common_font_size']}pt
- Line Spacing: {self.analysis['formatting_rules']['line_spacing_pattern']}

Structure:
- Front Matter: {len(self.analysis.get('front_matter', {}).get('sections', []))} sections
- Main Content: Chapter-based structure
- Back Matter: References and appendices

Validation Rules:
- Required Sections: {len(self.analysis.get('validation_rules', {}).get('required_sections', []))}
- Font Restrictions: {len(self.analysis.get('validation_rules', {}).get('font_restrictions', []))}
"""
        return summary.strip()