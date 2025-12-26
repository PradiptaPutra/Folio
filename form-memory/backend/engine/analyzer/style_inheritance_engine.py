"""
Style Inheritance Engine
Manages style preservation and application for content insertion with academic formatting
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE


@dataclass
class StyleRules:
    """Comprehensive style rules for academic formatting"""
    font_family: str = "Times New Roman"
    font_size: float = 11.0  # pt
    font_color: Optional[str] = None
    bold: bool = False
    italic: bool = False

    # Paragraph formatting
    alignment: str = "justify"  # left, center, right, justify
    line_spacing: float = 1.5
    space_before: float = 0.0  # pt
    space_after: float = 0.0   # pt
    first_line_indent: float = 1.0  # cm (academic standard)
    left_indent: float = 0.0
    right_indent: float = 0.0

    # List formatting
    list_style: Optional[str] = None  # numbered, bulleted, custom
    list_level: int = 0

    # Special academic elements
    is_header: bool = False
    header_level: int = 0
    is_caption: bool = False
    is_footnote: bool = False


class StyleInheritanceEngine:
    """
    Engine for extracting, preserving, and applying academic document styles
    """

    # Indonesian academic style standards
    ACADEMIC_STANDARDS = {
        'fonts': {
            'primary': 'Times New Roman',
            'secondary': ['Arial', 'Calibri'],
            'header_sizes': {1: 16, 2: 14, 3: 12, 4: 11, 5: 11},  # pt
            'body_size': 11,  # pt
        },
        'spacing': {
            'line_spacing': 1.5,
            'paragraph_spacing': {'before': 0, 'after': 0},  # pt
            'header_spacing': {'before': 24, 'after': 12},  # pt
        },
        'indentation': {
            'first_line': 1.0,  # cm
            'hanging_indent': 0.5,  # cm for references
            'list_indent': 0.5,  # cm per level
        },
        'alignment': {
            'body': 'justify',
            'headers': 'center',
            'captions': 'center',
            'lists': 'left',
        }
    }

    def __init__(self):
        self.style_database = {}
        self.inheritance_rules = {}

    def extract_styles_from_template(self, doc) -> Dict[str, StyleRules]:
        """
        Extract comprehensive style information from DOCX template

        Args:
            doc: python-docx Document object

        Returns:
            Dictionary mapping style names to StyleRules objects
        """
        print("[INFO] Extracting styles from template...")

        extracted_styles = {}

        # Extract paragraph styles
        for style in doc.styles:
            if style.type == WD_STYLE_TYPE.PARAGRAPH:
                style_rules = self._extract_paragraph_style(style)
                extracted_styles[style.name] = style_rules

        # Extract character styles (for inline formatting)
        for style in doc.styles:
            if style.type == WD_STYLE_TYPE.CHARACTER:
                char_rules = self._extract_character_style(style)
                # Merge with existing paragraph styles if applicable
                if style.name in extracted_styles:
                    extracted_styles[style.name] = self._merge_styles(
                        extracted_styles[style.name], char_rules
                    )

        # Analyze actual document usage for style intelligence
        self._analyze_document_usage(doc, extracted_styles)

        print(f"[SUCCESS] Extracted {len(extracted_styles)} style rules")
        return extracted_styles

    def create_inheritance_rules(self, template_styles: Dict[str, StyleRules]) -> Dict[str, Dict[str, Any]]:
        """
        Create inheritance rules for different content types

        Args:
            template_styles: Extracted style rules from template

        Returns:
            Inheritance rules mapping content types to style applications
        """
        rules = {
            'chapter_title': self._get_chapter_title_rules(template_styles),
            'subsection_title': self._get_subsection_title_rules(template_styles),
            'body_text': self._get_body_text_rules(template_styles),
            'list_item': self._get_list_item_rules(template_styles),
            'table': self._get_table_rules(template_styles),
            'caption': self._get_caption_rules(template_styles),
            'reference': self._get_reference_rules(template_styles),
        }

        self.inheritance_rules = rules
        return rules

    def apply_style_to_content(self, content: str, content_type: str,
                             base_style: Optional[StyleRules] = None) -> Dict[str, Any]:
        """
        Apply appropriate styling to content based on type and context

        Args:
            content: The content text to style
            content_type: Type of content (chapter_title, body_text, etc.)
            base_style: Base style to inherit from

        Returns:
            Style application instructions
        """
        if content_type not in self.inheritance_rules:
            content_type = 'body_text'  # Default

        rules = self.inheritance_rules[content_type]

        # Start with base style if provided
        if base_style:
            applied_style = self._merge_style_rules(base_style, rules)
        else:
            applied_style = rules

        # Apply content-specific adjustments
        applied_style = self._apply_content_specific_adjustments(content, applied_style, content_type)

        return applied_style

    def get_academic_formatting_instructions(self, content_type: str) -> Dict[str, Any]:
        """
        Get comprehensive formatting instructions for academic elements

        Args:
            content_type: Type of academic content

        Returns:
            Detailed formatting instructions
        """
        instructions = {
            'chapter_title': {
                'font_size': 14,
                'bold': True,
                'alignment': 'center',
                'space_after': 12,
                'all_caps': True,
                'numbering': 'BAB I - ',
            },
            'subsection_title': {
                'font_size': 12,
                'bold': True,
                'alignment': 'left',
                'first_line_indent': 0,
                'space_after': 6,
            },
            'body_paragraph': {
                'font_size': 11,
                'alignment': 'justify',
                'first_line_indent': 1.0,
                'line_spacing': 1.5,
            },
            'numbered_list': {
                'font_size': 11,
                'alignment': 'left',
                'first_line_indent': 0.5,
                'left_indent': 0.5,
                'numbering_format': '1. 2. 3.',
            },
            'bulleted_list': {
                'font_size': 11,
                'alignment': 'left',
                'first_line_indent': 0,
                'left_indent': 0.5,
                'bullet_char': '•',
            },
            'table': {
                'font_size': 10,
                'alignment': 'center',
                'borders': True,
                'header_bold': True,
                'alternating_rows': False,
            },
            'caption': {
                'font_size': 10,
                'alignment': 'center',
                'italic': True,
                'space_before': 6,
                'label': 'Tabel 1.1: ',
            },
            'reference': {
                'font_size': 11,
                'alignment': 'left',
                'first_line_indent': 0,
                'hanging_indent': 0.5,
                'line_spacing': 1.0,
            },
        }

        return instructions.get(content_type, instructions['body_paragraph'])

    def validate_style_consistency(self, applied_styles: Dict[str, Any]) -> List[str]:
        """
        Validate that applied styles are consistent with academic standards

        Args:
            applied_styles: Dictionary of applied style rules

        Returns:
            List of validation warnings/issues
        """
        warnings = []

        # Check font consistency
        fonts_used = set()
        for style_name, rules in applied_styles.items():
            if hasattr(rules, 'font_family'):
                fonts_used.add(rules.font_family)

        if len(fonts_used) > 2:
            warnings.append(f"Multiple fonts used ({len(fonts_used)}): {', '.join(fonts_used)}")

        # Check alignment consistency
        alignments = [rules.alignment for rules in applied_styles.values() if hasattr(rules, 'alignment')]
        if len(set(alignments)) > 3:
            warnings.append("Inconsistent text alignment throughout document")

        # Check spacing consistency
        line_spacings = [rules.line_spacing for rules in applied_styles.values() if hasattr(rules, 'line_spacing')]
        if line_spacings and max(line_spacings) - min(line_spacings) > 1.0:
            warnings.append("Inconsistent line spacing detected")

        return warnings

    def _extract_paragraph_style(self, style) -> StyleRules:
        """Extract paragraph style information"""
        rules = StyleRules()

        # Font properties
        if style.font:
            rules.font_family = getattr(style.font, 'name', 'Times New Roman') or 'Times New Roman'
            rules.font_size = getattr(style.font, 'size', Pt(11)).pt if style.font.size else 11
            rules.bold = getattr(style.font, 'bold', False) or False
            rules.italic = getattr(style.font, 'italic', False) or False

        # Paragraph properties
        if style.paragraph_format:
            alignment_mapping = {
                0: 'left', 1: 'center', 2: 'right', 3: 'justify',
                None: 'left'
            }
            rules.alignment = alignment_mapping.get(style.paragraph_format.alignment, 'left')

            rules.line_spacing = getattr(style.paragraph_format, 'line_spacing', 1.5) or 1.5
            rules.space_before = getattr(style.paragraph_format, 'space_before', Pt(0)).pt if style.paragraph_format.space_before else 0
            rules.space_after = getattr(style.paragraph_format, 'space_after', Pt(0)).pt if style.paragraph_format.space_after else 0

            # Convert to cm for consistency
            if style.paragraph_format.first_line_indent:
                rules.first_line_indent = style.paragraph_format.first_line_indent.cm
            if style.paragraph_format.left_indent:
                rules.left_indent = style.paragraph_format.left_indent.cm

        # Determine if this is a header style
        style_name_lower = style.name.lower()
        if 'heading' in style_name_lower or 'header' in style_name_lower:
            rules.is_header = True
            # Extract header level
            import re
            level_match = re.search(r'heading\s*(\d+)', style_name_lower, re.IGNORECASE)
            if level_match:
                rules.header_level = int(level_match.group(1))

        return rules

    def _extract_character_style(self, style) -> StyleRules:
        """Extract character style information"""
        rules = StyleRules()

        if style.font:
            rules.font_family = getattr(style.font, 'name', 'Times New Roman') or 'Times New Roman'
            rules.font_size = getattr(style.font, 'size', Pt(11)).pt if style.font.size else 11
            rules.bold = getattr(style.font, 'bold', False) or False
            rules.italic = getattr(style.font, 'italic', False) or False

        return rules

    def _analyze_document_usage(self, doc, extracted_styles: Dict[str, StyleRules]) -> None:
        """Analyze how styles are actually used in the document"""
        style_usage = {}

        for para in doc.paragraphs:
            if para.style and para.style.name in extracted_styles:
                style_name = para.style.name
                if style_name not in style_usage:
                    style_usage[style_name] = {'count': 0, 'avg_length': 0, 'samples': []}

                style_usage[style_name]['count'] += 1
                text_length = len(para.text)
                style_usage[style_name]['avg_length'] = (
                    (style_usage[style_name]['avg_length'] * (style_usage[style_name]['count'] - 1)) + text_length
                ) / style_usage[style_name]['count']

                # Keep a few samples
                if len(style_usage[style_name]['samples']) < 3:
                    style_usage[style_name]['samples'].append(para.text[:50])

        # Update style rules with usage information
        for style_name, usage_data in style_usage.items():
            if style_name in extracted_styles:
                # Infer style purpose from usage patterns
                avg_length = usage_data['avg_length']
                if avg_length < 50 and extracted_styles[style_name].bold:
                    extracted_styles[style_name].is_header = True
                elif avg_length > 200:
                    extracted_styles[style_name].is_caption = True

    def _merge_styles(self, base_style: StyleRules, overlay_style: StyleRules) -> StyleRules:
        """Merge two style rules, with overlay taking precedence"""
        merged = StyleRules()

        # Copy all attributes from base
        for attr in vars(base_style):
            if not attr.startswith('_'):
                setattr(merged, attr, getattr(base_style, attr))

        # Override with overlay
        for attr in vars(overlay_style):
            if not attr.startswith('_') and getattr(overlay_style, attr) is not None:
                setattr(merged, attr, getattr(overlay_style, attr))

        return merged

    def _get_chapter_title_rules(self, template_styles: Dict[str, StyleRules]) -> StyleRules:
        """Get style rules for chapter titles"""
        rules = StyleRules(
            font_size=14,
            bold=True,
            alignment='center',
            space_after=12,
            is_header=True,
            header_level=1
        )

        # Try to inherit from existing header styles
        for style_name, style_rules in template_styles.items():
            if style_rules.is_header and style_rules.header_level == 1:
                return self._merge_styles(style_rules, rules)

        return rules

    def _get_subsection_title_rules(self, template_styles: Dict[str, StyleRules]) -> StyleRules:
        """Get style rules for subsection titles"""
        rules = StyleRules(
            font_size=12,
            bold=True,
            alignment='left',
            first_line_indent=0,
            space_after=6,
            is_header=True,
            header_level=2
        )

        # Try to inherit from existing header styles
        for style_name, style_rules in template_styles.items():
            if style_rules.is_header and style_rules.header_level == 2:
                return self._merge_styles(style_rules, rules)

        return rules

    def _get_body_text_rules(self, template_styles: Dict[str, StyleRules]) -> StyleRules:
        """Get style rules for body text"""
        rules = StyleRules(
            font_size=11,
            alignment='justify',
            first_line_indent=1.0,
            line_spacing=1.5
        )

        # Try to find Normal or default paragraph style
        for style_name, style_rules in template_styles.items():
            if 'normal' in style_name.lower() or not style_rules.is_header:
                return self._merge_styles(style_rules, rules)

        return rules

    def _get_list_item_rules(self, template_styles: Dict[str, StyleRules]) -> StyleRules:
        """Get style rules for list items"""
        return StyleRules(
            font_size=11,
            alignment='left',
            first_line_indent=0,
            left_indent=0.5,
            line_spacing=1.5
        )

    def _get_table_rules(self, template_styles: Dict[str, StyleRules]) -> Dict[str, Any]:
        """Get style rules for tables"""
        return {
            'font_size': 10,
            'alignment': 'center',
            'borders': True,
            'header_bold': True,
            'cell_padding': 0.1,  # cm
        }

    def _get_caption_rules(self, template_styles: Dict[str, StyleRules]) -> StyleRules:
        """Get style rules for captions"""
        return StyleRules(
            font_size=10,
            alignment='center',
            italic=True,
            space_before=6
        )

    def _get_reference_rules(self, template_styles: Dict[str, StyleRules]) -> StyleRules:
        """Get style rules for references"""
        return StyleRules(
            font_size=11,
            alignment='left',
            first_line_indent=0,
            left_indent=0.5,  # Hanging indent
            line_spacing=1.0
        )

    def _merge_style_rules(self, base: StyleRules, overlay: Dict[str, Any]) -> Dict[str, Any]:
        """Merge StyleRules object with dictionary of rules"""
        result = {}

        # Copy base style attributes
        for attr in vars(base):
            if not attr.startswith('_'):
                result[attr] = getattr(base, attr)

        # Apply overlay
        result.update(overlay)

        return result

    def _apply_content_specific_adjustments(self, content: str, style: Dict[str, Any],
                                          content_type: str) -> Dict[str, Any]:
        """Apply content-specific style adjustments"""
        adjusted_style = style.copy()

        # Special handling for different content types
        if content_type == 'chapter_title':
            # Ensure chapter titles are properly formatted
            if not content.upper().startswith('BAB '):
                adjusted_style['prefix'] = 'BAB I - '
        elif content_type == 'reference':
            # References often need hanging indents
            adjusted_style['hanging_indent'] = 0.5
        elif content_type == 'list_item':
            # Lists need special indentation
            if content.strip().startswith(('1.', '2.', '3.', 'a.', 'b.', 'c.')):
                adjusted_style['list_type'] = 'numbered'
            else:
                adjusted_style['list_type'] = 'bulleted'

        return adjusted_style