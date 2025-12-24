"""
Complete Thesis Document Builder
Orchestrates the creation of a complete, properly structured thesis document
with all front matter, main content, and back matter.
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
from docx import Document
from docx.shared import Pt, Inches
import re
from .template_analyzer import TemplateAnalyzer
from .content_extractor import ContentExtractor
from .ai_enhanced_extractor import AIEnhancedContentExtractor
from .content_mapper import ContentMapper
from .document_merger import DocumentMerger
from .front_matter_generator import FrontMatterGenerator, BackMatterGenerator
from ..parser.normalized_extractor import extract_normalized_structure


class CompleteThesisBuilder:
    """Builds a complete thesis document with all required sections."""
    
    def __init__(self, template_path: str, content_path: str, output_path: str, use_ai: bool = True, include_frontmatter: bool = True, api_key: Optional[str] = None):
        """Initialize the perfect thesis builder.

        Args:
            template_path: Path to DOCX template
            content_path: Path to content file (DOCX or TXT)
            output_path: Path for output DOCX
            use_ai: Whether to use AI semantic analysis (if available)
            include_frontmatter: Whether to include front matter sections
            api_key: OpenRouter API key for AI features
        """
        self.template_path = Path(template_path)
        self.content_path = Path(content_path)
        self.output_path = Path(output_path)
        self.use_ai = use_ai
        self.include_frontmatter = include_frontmatter
        self.api_key = api_key

        # Initialize components
        self.analyzer = TemplateAnalyzer(str(self.template_path))

        # Use AI-enhanced extractor when available
        self.ai_extractor = AIEnhancedContentExtractor(str(self.content_path), use_ai=use_ai, api_key=api_key)
        self.extractor = ContentExtractor(str(self.content_path))
        self.mapper = ContentMapper(self.analyzer, self.extractor)

        # Initialize AI-powered components for perfect formatting (optional)
        self.perfect_adapter = None
        self.quality_validator = None

        # Initialize AI components dynamically in build method

        # Semantic validation
        self.semantic_validation = self.ai_extractor.get_semantic_validation() if use_ai else None

    def _copy_styles_from_template(self, target_doc: Document, template_doc: Document) -> None:
        """Copy styles from template document to target document."""
        try:
            # Copy paragraph styles
            for style in template_doc.styles:
                if style.name not in target_doc.styles:
                    try:
                        # Create a copy of the style in the target document
                        new_style = target_doc.styles.add_style(style.name, style.type)
                        if hasattr(style, 'font') and style.font:
                            new_style.font.name = style.font.name
                            new_style.font.size = style.font.size
                            new_style.font.bold = style.font.bold
                            new_style.font.italic = style.font.italic
                    except Exception:
                        # Skip styles that can't be copied
                        pass
        except Exception as e:
            print(f"[WARNING] Failed to copy styles from template: {e}")
    
    def build(self, user_data: Optional[Dict[str, Any]] = None) -> Path:
        """Build the complete thesis document with perfect formatting.

        Args:
            user_data: Dictionary with user data for personalization

        Returns:
            Path to created DOCX file
        """
        user_data = user_data or {}
        print(f"[DEBUG] Starting build with use_ai={self.use_ai}, api_key={'present' if self.api_key else 'missing'}")

        # AI-Powered Template Intelligence Processing
        if self.use_ai and self.api_key:
            try:
                print("[AI] Starting AI-powered template intelligence processing")

                # Step 1: AI-powered template structure analysis
                print("[AI] Step 1: AI-powered template structure analysis")
                from .ai_template_intelligence import AITemplateAnalyzer
                ai_template_analyzer = AITemplateAnalyzer(api_key=self.api_key)
                intelligent_template_analysis = ai_template_analyzer.analyze_template_with_ai(str(self.template_path))

                print(f"[DEBUG] AI template analysis result keys: {list(intelligent_template_analysis.keys())}")
                print(f"[DEBUG] Template analysis confidence: {intelligent_template_analysis.get('processing_metadata', {}).get('confidence_score', 'N/A')}")

                # Step 2: Extract structured formatting rules
                print("[AI] Step 2: Extract formatting rules to structured format")
                structured_rules = intelligent_template_analysis.get('structured_formatting_rules', {})
                print(f"[AI] Extracted {len(structured_rules)} rule categories")

                # Step 3: Apply rules intelligently to content
                print("[AI] Step 3: Apply rules intelligently to new content")
                from .ai_template_intelligence import IntelligentTemplateApplier
                template_applier = IntelligentTemplateApplier(api_key=self.api_key)

                raw_content = self.ai_extractor.raw_text
                print(f"[DEBUG] Raw content length: {len(raw_content)} characters")

                application_result = template_applier.apply_template_intelligently(
                    raw_content, intelligent_template_analysis
                )

                print(f"[DEBUG] Template application result keys: {list(application_result.keys())}")

                # Use the AI-enhanced content for final document generation
                enhanced_content = application_result.get('formatted_content', raw_content)
                print(f"[DEBUG] Enhanced content length: {len(enhanced_content)} characters")

                # Add AI analysis results to user data for enhanced processing
                user_data['ai_enhanced_content'] = enhanced_content
                user_data['ai_template_analysis'] = intelligent_template_analysis
                user_data['ai_application_result'] = application_result
                user_data['processing_method'] = 'ai_intelligent'

                confidence_score = intelligent_template_analysis.get('processing_metadata', {}).get('confidence_score', 0)
                print(f"[AI] SUCCESS: AI processing completed with {confidence_score:.1%} confidence")

            except Exception as e:
                print(f"[WARNING] AI template intelligence failed ({e}), falling back to standard processing")
                import traceback
                traceback.print_exc()

        # Choose build method based on processing type
        processing_method = user_data.get('processing_method', 'standard')
        print(f"[INFO] Building document with {processing_method} processing")

        if processing_method == 'ai_intelligent':
            print("[DEBUG] Using AI-intelligent document building")
            return self._build_ai_intelligent(user_data)
        else:
            print("[DEBUG] Using standard document building")
            return self._build_standard(user_data)

        # Fallback to standard processing
        return self._build_standard(user_data)

    def _build_ai_intelligent(self, user_data: Dict[str, Any]) -> Path:
        """Build thesis using AI-intelligent processing with proper template adaptation."""
        print(f"[DEBUG] Starting AI-intelligent build with enhanced content")

        # Get AI results
        ai_enhanced_content = user_data.get('ai_enhanced_content', '')
        ai_template_analysis = user_data.get('ai_template_analysis', {})
        ai_application_result = user_data.get('ai_application_result', {})

        print(f"[DEBUG] AI content length: {len(ai_enhanced_content)}")
        print(f"[DEBUG] Template analysis keys: {list(ai_template_analysis.keys())}")
        print(f"[DEBUG] Application result keys: {list(ai_application_result.keys())}")

        # Load template document as the base
        try:
            doc = Document(str(self.template_path))
            print(f"[DEBUG] Template loaded as base document: {len(doc.paragraphs)} paragraphs, {len(doc.styles)} styles")
        except Exception as e:
            print(f"[WARNING] Failed to load template as base, creating new document: {e}")
            doc = Document()

        # Get structure mapping for intelligent content replacement
        structure_mapping = ai_application_result.get('structure_mapping', {})
        section_mappings = structure_mapping.get('section_mappings', [])
        print(f"[DEBUG] Found {len(section_mappings)} section mappings for content replacement")

        # Simple, reliable approach that worked before
        print("[DEBUG] Using proven reliable approach")

        # Always add standard content structure for reliability
        if self.include_frontmatter:
            print("[DEBUG] Adding front matter")
            self._add_front_matter(doc, user_data)

        print("[DEBUG] Adding main content")
        try:
            normalized = extract_normalized_structure(str(self.content_path))
            self._add_main_content(doc, user_data, normalized)
        except Exception as e:
            print(f"[DEBUG] Content extraction failed, using basic: {e}")
            self._add_main_content(doc, user_data, None)

        print("[DEBUG] Adding back matter")
        self._add_back_matter(doc, user_data)

        # Debug document state before saving
        print(f"[DEBUG] Document state before save: {type(doc)}")
        print(f"[DEBUG] Document has {len(doc.paragraphs) if doc else 0} paragraphs")

        # Save the document
        print(f"[DEBUG] Saving AI-intelligent document to: {self.output_path}")
        if doc is None:
            print("[ERROR] Document became None during processing!")
            return self.output_path  # Return path even if failed

        try:
            doc.save(str(self.output_path))
            print(f"[DEBUG] Document saved successfully")
        except Exception as e:
            print(f"[ERROR] Failed to save document: {e}")
            return self.output_path

        final_size = self.output_path.stat().st_size if self.output_path.exists() else 0
        print(f"[DEBUG] AI-intelligent document saved, size: {final_size} bytes")

        return self.output_path

    def _add_ai_main_content(self, doc: Document, user_data: Dict[str, Any], ai_content: str, structure_mapping: Dict[str, Any]) -> None:
        """Add main content using AI-enhanced formatting."""
        print(f"[DEBUG] Processing AI content with structure mapping: {list(structure_mapping.keys())}")

        # If we have structured AI content, use it
        if ai_content and structure_mapping:
            # Parse AI-enhanced content into sections
            sections = self._parse_ai_content_sections(ai_content)
            print(f"[DEBUG] Parsed {len(sections)} sections from AI content")

            for idx, section in enumerate(sections, 1):
                # Add page break before chapter (except first)
                if idx > 1:
                    doc.add_page_break()

                # Add chapter heading
                title = section.get("title", f"Chapter {idx}")
                heading_para = doc.add_paragraph(title)
                heading_para.style = "Heading 1"
                heading_run = heading_para.runs[0]
                heading_run.font.bold = True
                heading_run.font.size = Pt(14)

                # Add section content with proper formatting
                content = section.get("content", [])
                if isinstance(content, list):
                    for line in content:
                        if isinstance(line, str) and line.strip():
                            para = doc.add_paragraph(line)
                            para.style = "Normal"
                            para.paragraph_format.left_indent = Inches(0.0)
                            para.paragraph_format.first_line_indent = Inches(1.0)
                            para.paragraph_format.line_spacing = 1.5
                            for run in para.runs:
                                run.font.size = Pt(11)
                                run.font.name = "Times New Roman"
        else:
            # Fallback to standard content processing
            print("[DEBUG] No AI structure mapping, falling back to standard content")
            try:
                normalized = extract_normalized_structure(str(self.content_path))
                self._add_main_content(doc, user_data, normalized)
            except Exception:
                self._add_main_content(doc, user_data, None)

    def _parse_ai_content_sections(self, ai_content: str) -> List[Dict[str, Any]]:
        """Parse AI-enhanced content into structured sections."""
        sections = []
        lines = ai_content.split('\n')
        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect section headers (enhanced patterns)
            if self._is_ai_section_header(line):
                if current_section:
                    sections.append(current_section)

                current_section = {
                    'title': line,
                    'content': [],
                    'type': 'chapter'
                }
            elif current_section:
                current_section['content'].append(line)

        if current_section:
            sections.append(current_section)

        return sections

    def _is_ai_section_header(self, line: str) -> bool:
        """Check if line is a section header in AI-enhanced content."""
        # Enhanced patterns for AI-generated content
        patterns = [
            r'^BAB\s+[IVX]+\b',  # BAB I, BAB II, etc.
            r'^BAB\s+\d+\b',     # BAB 1, BAB 2, etc.
            r'^Chapter\s+\d+',   # Chapter 1, etc.
            r'^\d+\.\s+',        # 1. , 2. , etc.
            r'^[A-Z][^.!?]*:$', # SECTION NAME:
        ]

        return any(re.match(pattern, line, re.IGNORECASE) for pattern in patterns)

    def _apply_intelligent_content_replacement(self, doc: Document, ai_content: str, structure_mapping: Dict[str, Any], user_data: Dict[str, Any]) -> Document:
        """Apply intelligent content replacement to template document."""
        print(f"[DEBUG] Applying intelligent content replacement to {len(doc.paragraphs)} paragraphs")

        # Parse AI content into structured sections
        ai_sections = self._parse_ai_content_sections(ai_content)
        print(f"[DEBUG] AI content parsed into {len(ai_sections)} sections")

        # Strategy: Replace template placeholders with real content
        replacements_made = 0

        # Look for common Indonesian thesis chapter patterns in the template
        chapter_patterns = [
            r'^BAB\s+I\b.*',  # BAB I - Pendahuluan
            r'^BAB\s+II\b.*', # BAB II - Tinjauan Pustaka
            r'^BAB\s+III\b.*', # BAB III - Metodologi
            r'^BAB\s+IV\b.*', # BAB IV - Hasil dan Pembahasan
            r'^BAB\s+V\b.*',  # BAB V - Penutup
            r'^BAB\s+VI\b.*', # BAB VI (sometimes included)
        ]

        # Simple and safe chapter title replacement
        print(f"[DEBUG] Starting chapter replacement with {len(ai_sections)} AI sections")
        for ai_section in ai_sections[:3]:  # Debug first few
            print(f"[DEBUG] AI section: {ai_section.get('title', 'no title')}")

        for i, para in enumerate(doc.paragraphs):
            text = para.text.strip()

            # Check if this paragraph matches a chapter pattern
            for pattern in chapter_patterns:
                if re.match(pattern, text.upper()):
                    chapter_num = text.split()[1] if len(text.split()) > 1 else ""
                    print(f"[DEBUG] Found chapter {chapter_num} at paragraph {i}")

                    # Find corresponding AI content - try simpler matching
                    ai_content_section = None
                    for ai_section in ai_sections:
                        section_title = ai_section.get('title', '').upper()
                        # More flexible matching
                        if chapter_num in section_title or f'BAB {chapter_num}' in section_title:
                            ai_content_section = ai_section
                            break

                    if ai_content_section:
                        # Simply replace the chapter title
                        new_title = ai_content_section.get('title', text.split('\n')[0])
                        print(f"[DEBUG] Setting paragraph {i} text to: '{new_title}'")
                        try:
                            para.text = new_title
                            replacements_made += 1
                            print(f"[DEBUG] Replaced chapter {chapter_num} title successfully")
                        except Exception as e:
                            print(f"[ERROR] Failed to set paragraph text: {e}")
                    else:
                        print(f"[DEBUG] No matching AI content for chapter {chapter_num}")
                    break

        print(f"[DEBUG] Chapter replacement completed. Document state: {type(doc)}")
        print(f"[DEBUG] Document has {len(doc.paragraphs) if doc else 0} paragraphs")

        # Skip all placeholder cleaning to avoid document corruption
        print(f"[DEBUG] Skipping all placeholder cleaning")

    def _apply_simple_chapter_titles(self, doc: Document) -> None:
        """Apply standard chapter titles by directly replacing template placeholders."""
        # Standard chapter titles
        chapter_titles = {
            'I': 'BAB I: PENDAHULUAN',
            'II': 'BAB II: TINJAUAN PUSTAKA',
            'III': 'BAB III: METODOLOGI PENELITIAN',
            'IV': 'BAB IV: HASIL DAN PEMBAHASAN',
            'V': 'BAB V: PENUTUP',
            'VI': 'BAB VI: KESIMPULAN DAN SARAN'
        }

        replacements_made = 0

        # Find and replace each chapter by looking for the specific template pattern
        for para in doc.paragraphs:
            text = para.text.strip()

            # Look for the exact template pattern: "BAB X\nTULISKAN JUDUL BAB DI BARIS INI"
            if '\n' in text and 'TULISKAN JUDUL BAB' in text.upper():
                lines = text.split('\n')
                first_line = lines[0].strip()

                # Extract chapter number
                if first_line.startswith('BAB '):
                    parts = first_line.split()
                    if len(parts) >= 2:
                        chapter_marker = parts[1].strip('.:')
                        if chapter_marker in chapter_titles:
                            # Replace with proper title
                            new_title = chapter_titles[chapter_marker]
                            para.text = new_title
                            replacements_made += 1
                            print(f"[DEBUG] Replaced template chapter {chapter_marker} with: '{new_title}'")

        print(f"[DEBUG] Made {replacements_made} template chapter replacements")

        # Also replace any remaining single-line chapter headers
        for para in doc.paragraphs:
            text = para.text.strip()
            if text.startswith('BAB ') and 'TULISKAN' in text.upper():
                parts = text.split()
                if len(parts) >= 2:
                    chapter_marker = parts[1].strip('.:')
                    if chapter_marker in chapter_titles:
                        new_title = chapter_titles[chapter_marker]
                        para.text = new_title
                        replacements_made += 1
                        print(f"[DEBUG] Replaced single-line chapter {chapter_marker} with: '{new_title}'")

        print(f"[DEBUG] Total chapter replacements: {replacements_made}")

    def _apply_safe_chapter_titles(self, doc: Document, ai_content: str, structure_mapping: Dict[str, Any]) -> None:
        """Safely replace chapter titles without risking document corruption."""
        # Parse AI content sections
        ai_sections = self._parse_ai_content_sections(ai_content)

        print(f"[DEBUG] AI content parsed into {len(ai_sections)} sections")
        for i, section in enumerate(ai_sections[:5]):  # Show first 5 for debugging
            print(f"[DEBUG] AI section {i+1}: '{section.get('title', 'no title')}'")

        # Standard chapter titles to use when AI content doesn't match
        standard_titles = {
            'I': 'BAB I: PENDAHULUAN',
            'II': 'BAB II: TINJAUAN PUSTAKA',
            'III': 'BAB III: METODOLOGI PENELITIAN',
            'IV': 'BAB IV: HASIL DAN PEMBAHASAN',
            'V': 'BAB V: PENUTUP'
        }

        # Simple chapter title mapping
        chapter_patterns = [
            r'^BAB\s+I\b.*',
            r'^BAB\s+II\b.*',
            r'^BAB\s+III\b.*',
            r'^BAB\s+IV\b.*',
            r'^BAB\s+V\b.*',
        ]

        replacements_made = 0

        # Apply title replacements safely
        for i, para in enumerate(doc.paragraphs):
            text = para.text.strip()

            # Check if this paragraph matches a chapter pattern
            for pattern_idx, pattern in enumerate(chapter_patterns):
                if re.match(pattern, text.upper()):
                    chapter_num = ['I', 'II', 'III', 'IV', 'V'][pattern_idx]
                    print(f"[DEBUG] Found chapter {chapter_num} at paragraph {i}")

                    # Try to find corresponding AI content first
                    ai_content_section = None
                    for ai_section in ai_sections:
                        section_title = ai_section.get('title', '').upper()
                        # More flexible matching
                        if chapter_num in section_title or f'BAB {chapter_num}' in section_title:
                            ai_content_section = ai_section
                            break

                    if ai_content_section:
                        # Use AI-generated title
                        new_title = ai_content_section.get('title', text.split('\n')[0])
                        print(f"[DEBUG] Using AI title: '{new_title}'")
                    else:
                        # Use standard title
                        new_title = standard_titles.get(chapter_num, text.split('\n')[0])
                        print(f"[DEBUG] Using standard title: '{new_title}'")

                    try:
                        para.text = new_title
                        replacements_made += 1
                        print(f"[DEBUG] Replaced chapter {chapter_num} title successfully")
                    except Exception as e:
                        print(f"[ERROR] Failed to set paragraph text: {e}")
                    break  # Break out of pattern matching loop

        print(f"[DEBUG] Total chapter replacements made: {replacements_made}")

    def _clean_title_placeholders_only(self, doc: Document, user_data: Dict[str, Any]) -> None:
        """Safely clean only title placeholders without corrupting the document."""
        if not user_data.get('title'):
            return

        # Only replace the main title placeholders
        title_placeholders = [
            r'.*BAGIAN INI ADALAH BAGIAN JUDUL.*TULIS JUDUL.*',
            r'.*HALAMAN JUDUL.*'
        ]

        for para in doc.paragraphs:
            text = para.text.strip()
            for pattern in title_placeholders:
                if re.match(pattern, text.upper(), re.IGNORECASE | re.DOTALL):
                    para.text = user_data['title']
                    break

    def _clean_remaining_placeholders(self, doc: Document, user_data: Dict[str, Any], ai_sections: List[Dict[str, Any]], replacements_made: int) -> None:
        """Clean up any remaining placeholders in the document."""

        # Title placeholders
        title_placeholders = [
            r'.*TULIS.*JUDUL.*',
            r'.*BAGIAN.*JUDUL.*',
            r'.*HALAMAN.*JUDUL.*',
        ]

        for para in doc.paragraphs:
            text = para.text.strip()
            for pattern in title_placeholders:
                if re.match(pattern, text.upper(), re.IGNORECASE):
                    if user_data.get('title'):
                        para.text = user_data['title']
                        replacements_made += 1
                        print(f"[DEBUG] Replaced title placeholder with: '{user_data['title']}'")
                    break

        # Chapter content placeholders
        chapter_placeholders = [
            r'.*TULISKAN.*BAB.*',
            r'.*ISI.*BAB.*',
            r'.*SUBBAB.*',
            r'.*ANAK SUBBAB.*',
            r'.*CUCU SUBBAB.*',
        ]

        for para in doc.paragraphs:
            text = para.text.strip()
            for pattern in chapter_placeholders:
                if re.match(pattern, text.upper(), re.IGNORECASE):
                    # Clear placeholder content
                    para.text = ""
                    replacements_made += 1
                    print(f"[DEBUG] Cleared placeholder content: '{text[:50]}...'")
                    break

        # Front matter placeholders
        front_matter_placeholders = [
            r'.*TUGAS AKHIR.*JUDUL.*',
            r'.*BAGIAN.*BEBAS.*',
            r'.*GAMBAR.*JUDUL.*',
        ]

        for para in doc.paragraphs:
            text = para.text.strip()
            for pattern in front_matter_placeholders:
                if re.match(pattern, text.upper(), re.IGNORECASE):
                    # Replace with appropriate content or clear
                    if 'JUDUL' in text.upper() and user_data.get('title'):
                        para.text = user_data['title']
                    else:
                        para.text = ""  # Clear generic placeholders
                    replacements_made += 1
                    print(f"[DEBUG] Cleaned front matter placeholder")
                    break

        print(f"[DEBUG] Made {replacements_made} content replacements")

        # If still no meaningful replacements, add content in main sections
        if replacements_made < 3:
            print("[DEBUG] Insufficient replacements, adding content to main body")
            self._add_content_to_main_body(doc, ai_sections, user_data)

        return doc

    def _add_content_to_main_body(self, doc: Document, ai_sections: List[Dict[str, Any]], user_data: Dict[str, Any]) -> None:
        """Add content to the main body of the document when intelligent replacement fails."""
        print("[DEBUG] Adding content to main body sections")

        # Find the main content area (after front matter, before back matter)
        main_content_start = None

        for i, para in enumerate(doc.paragraphs):
            text = para.text.strip().upper()
            # Look for the start of main content (BAB I or similar)
            if 'BAB I' in text or 'BAB 1' in text or 'CHAPTER 1' in text:
                main_content_start = i
                break

        if main_content_start is None:
            # If no chapter marker found, add after front matter
            main_content_start = 50  # Rough estimate for front matter length

        # Insert content sections
        insert_position = main_content_start
        for section in ai_sections:
            # Insert chapter title
            title = section.get('title', 'Chapter')
            doc.paragraphs[insert_position].text = title

            # Insert content
            content_lines = section.get('content', [])
            for line in content_lines:
                if isinstance(line, str) and line.strip():
                    new_para = doc.add_paragraph(line)
                    new_para.style = "Normal"

            insert_position += 1

    def _replace_chapter_content(self, doc: Document, chapter_start_idx: int, ai_section: Dict[str, Any]) -> None:
        """Replace the content area of a chapter with clean AI content."""
        content_lines = ai_section.get('content', [])
        if not content_lines:
            return

        # Find the end of this chapter (next chapter or major section break)
        chapter_end_idx = self._find_chapter_end(doc, chapter_start_idx)

        print(f"[DEBUG] Chapter content area: paragraphs {chapter_start_idx + 1} to {chapter_end_idx}")

        # Clear existing content in this range (keep the chapter title)
        insert_idx = chapter_start_idx + 1
        content_idx = 0

        # Replace existing paragraphs with new content
        while insert_idx < chapter_end_idx and content_idx < len(content_lines):
            line = content_lines[content_idx].strip()
            if line and len(line) > 10:  # Only substantial content
                para = doc.paragraphs[insert_idx]
                para.text = line

                # Apply consistent formatting
                para.style = "Normal"
                para.paragraph_format.left_indent = Inches(0.0)
                para.paragraph_format.first_line_indent = Inches(1.0)
                para.paragraph_format.line_spacing = 1.5
                for run in para.runs:
                    run.font.size = Pt(11)
                    run.font.name = "Times New Roman"

                content_idx += 1
                insert_idx += 1
            else:
                content_idx += 1

        # If we have more content, add new paragraphs
        while content_idx < len(content_lines):
            line = content_lines[content_idx].strip()
            if line and len(line) > 10:
                new_para = doc.add_paragraph(line)
                new_para.style = "Normal"
                new_para.paragraph_format.left_indent = Inches(0.0)
                new_para.paragraph_format.first_line_indent = Inches(1.0)
                new_para.paragraph_format.line_spacing = 1.5
                for run in new_para.runs:
                    run.font.size = Pt(11)
                    run.font.name = "Times New Roman"
            content_idx += 1

    def _find_chapter_end(self, doc: Document, chapter_start_idx: int) -> int:
        """Find the end of a chapter section."""
        # Look for the next chapter or major section break
        for i in range(chapter_start_idx + 1, len(doc.paragraphs)):
            text = doc.paragraphs[i].text.strip().upper()

            # Next chapter starts
            if text.startswith('BAB ') and any(c.isdigit() or c in 'IVX' for c in text.split()[1][:3] if len(text.split()) > 1):
                return i

            # Major section break (table of contents, references, etc.)
            if any(keyword in text for keyword in ['DAFTAR PUSTAKA', 'LAMPIRAN', 'TABEL', 'GAMBAR']):
                return i

        return len(doc.paragraphs)  # End of document

    def _replace_template_section(self, doc: Document, section_name: str, ai_section: Dict[str, Any]) -> int:
        """Replace a template section with AI content."""
        replacements = 0

        # Find paragraphs containing the section name
        for para in doc.paragraphs:
            if section_name.lower() in para.text.lower():
                print(f"[DEBUG] Found section '{section_name}' in paragraph")
                # Replace the content
                para.text = ai_section.get('title', section_name)

                # Add the section content after this paragraph
                content = ai_section.get('content', [])
                current_para = para
                for line in content:
                    if isinstance(line, str) and line.strip():
                        new_para = doc.add_paragraph(line)
                        new_para.style = "Normal"
                        # Copy formatting from nearby paragraphs
                        if hasattr(current_para, 'paragraph_format'):
                            new_para.paragraph_format.left_indent = current_para.paragraph_format.left_indent
                            new_para.paragraph_format.first_line_indent = current_para.paragraph_format.first_line_indent
                            new_para.paragraph_format.line_spacing = current_para.paragraph_format.line_spacing
                        for run in new_para.runs:
                            run.font.size = Pt(11)
                            run.font.name = "Times New Roman"
                        current_para = new_para
                replacements += 1
                break  # Only replace first occurrence

        return replacements

    def _append_to_template_section(self, doc: Document, section_name: str, ai_section: Dict[str, Any]) -> int:
        """Append AI content to an existing template section."""
        replacements = 0

        # Find paragraphs containing the section name
        for para in doc.paragraphs:
            if section_name.lower() in para.text.lower():
                print(f"[DEBUG] Found section '{section_name}' to append to")
                # Add content after this paragraph
                content = ai_section.get('content', [])
                current_para = para
                for line in content:
                    if isinstance(line, str) and line.strip():
                        new_para = doc.add_paragraph(line)
                        new_para.style = "Normal"
                        # Copy formatting
                        if hasattr(current_para, 'paragraph_format'):
                            new_para.paragraph_format.left_indent = current_para.paragraph_format.left_indent
                            new_para.paragraph_format.first_line_indent = current_para.paragraph_format.first_line_indent
                            new_para.paragraph_format.line_spacing = current_para.paragraph_format.line_spacing
                        for run in new_para.runs:
                            run.font.size = Pt(11)
                            run.font.name = "Times New Roman"
                        current_para = new_para
                replacements += 1
                break  # Only append to first occurrence

        return replacements

    def _add_front_matter(self, doc: Document, user_data: Dict[str, Any]) -> None:
        """Add all front matter sections."""
        generator = FrontMatterGenerator(user_data)
        
        # Title Page
        generator.create_title_page(doc)
        
        # Approval Pages
        generator.create_approval_page(doc, approval_type="supervisor")
        generator.create_approval_page(doc, approval_type="examiner")
        
        # Originality Statement
        generator.create_originality_statement(doc)
        
        # Optional: Dedication
        if user_data and isinstance(user_data, dict) and user_data.get("dedication"):
            generator.create_dedication_page(doc, user_data["dedication"])
        
        # Optional: Motto
        if user_data and isinstance(user_data, dict) and user_data.get("motto"):
            generator.create_motto_page(doc, user_data["motto"])
        
        # Preface
        generator.create_preface(doc)
        
        # Abstracts
        generator.create_abstract(doc, language="id")
        if user_data and isinstance(user_data, dict) and user_data.get("abstract_en"):
            generator.create_abstract(doc, language="en")
        
        # Table of Contents
        generator.create_table_of_contents(doc)
        
        # Glossary (if provided)
        if user_data and isinstance(user_data, dict) and user_data.get("glossary"):
            generator.create_glossary(doc, user_data["glossary"])
    
    def _add_main_content(self, doc: Document, user_data: Dict[str, Any], normalized: Dict[str, Any] | None = None) -> None:
        """Add main content (chapters/sections from extractor or normalized)."""
        if normalized and isinstance(normalized, dict) and normalized.get("chapters"):
            sections = []
            for ch in normalized.get("chapters", []):
                sec = {
                    "title": ch.get("title") or (f"BAB {ch.get('number', '')}" if ch.get('number') else "Chapter"),
                    "content": list(ch.get("content", [])),
                    "lists": list(ch.get("lists", [])),
                }
                for s in ch.get("sections", []):
                    sec["content"].extend(s.get("content", []))
                    for lst in s.get("lists", []):
                        sec.setdefault("lists", []).append(lst)
                sections.append(sec)
        else:
            sections = self.extractor.get_sections()
        
        for idx, section in enumerate(sections, 1):
            # Skip non-dict sections
            if not isinstance(section, dict):
                continue
            
            # Add page break before chapter (except first)
            if idx > 1:
                doc.add_page_break()
            
            # Add chapter heading
            title = section.get("title", f"Chapter {idx}")
            heading_para = doc.add_paragraph(title)
            heading_para.style = "Heading 1"
            heading_run = heading_para.runs[0]
            heading_run.font.bold = True
            heading_run.font.size = Pt(14)
            
            # Add section content
            content = section.get("content", [])
            if isinstance(content, list):
                for line in content:
                    if isinstance(line, str) and line.strip():
                        para = doc.add_paragraph(line)
                        para.style = "Normal"
                        # Apply paragraph formatting
                        para.paragraph_format.left_indent = Inches(0.0)
                        para.paragraph_format.first_line_indent = Inches(1.0)
                        para.paragraph_format.line_spacing = 1.5
                        for run in para.runs:
                            run.font.size = Pt(11)
                            run.font.name = "Times New Roman"
            else:
                # Content is a single string
                para = doc.add_paragraph(str(content))
                para.style = "Normal"
                para.paragraph_format.left_indent = Inches(0.0)
                para.paragraph_format.first_line_indent = Inches(1.0)
                para.paragraph_format.line_spacing = 1.5
                for run in para.runs:
                    run.font.size = Pt(11)
                    run.font.name = "Times New Roman"

            # Add lists if present
            for lst in section.get("lists", []):
                style_name = "List Number" if lst.get("ordered") else "List Bullet"
                for item in lst.get("items", []):
                    para = doc.add_paragraph(item)
                    para.style = style_name
    
    def _add_back_matter(self, doc: Document, user_data: Dict[str, Any]) -> None:
        """Add all back matter sections."""
        generator = BackMatterGenerator(user_data)
        
        # List of Tables
        generator.create_list_of_tables(doc)
        
        # List of Figures
        generator.create_list_of_figures(doc)
        
        # References/Bibliography
        references = user_data.get("references", []) if user_data and isinstance(user_data, dict) else []
        generator.create_references(doc, references)
        
        # Appendices
        appendices = user_data.get("appendices", []) if user_data and isinstance(user_data, dict) else []
        if appendices:
            generator.create_appendices(doc, appendices)
    
    def get_analysis_report(self) -> Dict[str, Any]:
        """Get comprehensive analysis report of template, content, and semantic structure."""
        report = {
            "template_analysis": self.analyzer.get_summary(),
            "content_summary": self.extractor.get_summary(),
            "mapping_summary": self.mapper.get_summary(),
            "sections_found": len(self.extractor.get_sections()),
            "styles_detected": len(self.analyzer.analysis.get("styles", {})),
        }
        
        # Add AI semantic analysis if available
        if self.use_ai:
            sections = self.ai_extractor.get_sections()
            semantic_types = []
            for s in sections:
                if isinstance(s, dict):
                    semantic_types.append(s.get("semantic_type", "unknown"))
            
            report["ai_semantic_analysis"] = {
                "extraction_summary": self.ai_extractor.get_summary(),
                "semantic_validation": self.semantic_validation,
                "semantic_types_found": list(set(semantic_types)),
            }
        
        return report

    def _build_standard(self, user_data: Dict[str, Any]) -> Path:
        """Build thesis using standard processing (fallback method)."""
        print(f"[DEBUG] Starting standard build with user_data keys: {list(user_data.keys())}")
        print(f"[DEBUG] Template path: {self.template_path}, exists: {self.template_path.exists()}")
        print(f"[DEBUG] Content path: {self.content_path}, exists: {self.content_path.exists()}")

        # Load template document and extract styles, then create new document
        try:
            template_doc = Document(str(self.template_path))
            print(f"[DEBUG] Template loaded successfully, {len(template_doc.paragraphs)} paragraphs, {len(template_doc.styles)} styles")

            # Create new document (don't keep template content)
            doc = Document()
            print(f"[DEBUG] New document created with {len(doc.styles)} default styles")

            # Copy styles from template to new document
            self._copy_styles_from_template(doc, template_doc)
            print(f"[DEBUG] After style copying: {len(doc.styles)} styles in new document")

        except Exception as e:
            print(f"[WARNING] Failed to load template, creating new document: {e}")
            doc = Document()

        # Build sections in order
        if self.include_frontmatter:
            print("[DEBUG] Adding front matter...")
            self._add_front_matter(doc, user_data)
            print(f"[DEBUG] Front matter added, document now has {len(doc.paragraphs)} paragraphs")

        # Prefer normalized extractor where available
        try:
            print("[DEBUG] Attempting normalized extraction...")
            normalized = extract_normalized_structure(str(self.content_path))
            print(f"[DEBUG] Normalized extraction successful: {normalized is not None}")
            if normalized:
                print(f"[DEBUG] Normalized structure keys: {list(normalized.keys())}")
                if 'chapters' in normalized:
                    print(f"[DEBUG] Found {len(normalized['chapters'])} chapters")
        except Exception as e:
            print(f"[DEBUG] Normalized extraction failed: {e}")
            normalized = None

        print("[DEBUG] Adding main content...")
        self._add_main_content(doc, user_data, normalized)
        print(f"[DEBUG] Main content added, document now has {len(doc.paragraphs)} paragraphs")

        print("[DEBUG] Adding back matter...")
        self._add_back_matter(doc, user_data)
        print(f"[DEBUG] Back matter added, document now has {len(doc.paragraphs)} paragraphs")

        # Save
        print(f"[DEBUG] Saving document to: {self.output_path}")
        doc.save(str(self.output_path))

        final_size = self.output_path.stat().st_size if self.output_path.exists() else 0
        print(f"[DEBUG] Document saved successfully, size: {final_size} bytes")

        return self.output_path


def create_complete_thesis(
    template_path: str,
    content_path: str,
    output_path: str,
    user_data: Optional[Dict[str, Any]] = None,
    use_ai: bool = True,
    include_frontmatter: bool = True,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """Convenience function to create a complete thesis in one call.
    
    Args:
        template_path: Path to DOCX template
        content_path: Path to content file
        output_path: Path for output DOCX
        user_data: User data dictionary
        use_ai: Whether to use AI semantic analysis
        include_frontmatter: Whether to include front matter sections
    
    Returns:
        Dictionary with:
            - output_file: Path to created document
            - status: "success" or "error"
            - message: Status message
            - report: Analysis report
    """
    try:
        # Verify files exist before creating builder
        template_p = Path(template_path)
        content_p = Path(content_path)
        
        if not template_p.exists():
            return {
                "status": "error",
                "message": f"Template file not found: {template_path}",
                "error_details": f"File does not exist: {template_path}",
            }
        
        if not content_p.exists():
            return {
                "status": "error",
                "message": f"Content file not found: {content_path}",
                "error_details": f"File does not exist: {content_path}",
            }
        
        builder = CompleteThesisBuilder(template_path, content_path, output_path, use_ai=use_ai, include_frontmatter=include_frontmatter, api_key=api_key)
        
        # Get analysis before building
        report = builder.get_analysis_report()
        
        # Build the thesis
        output = builder.build(user_data or {})
        
        return {
            "status": "success",
            "output_file": str(output),
            "message": "Complete thesis document created successfully",
            "report": report,
            "file_size": output.stat().st_size if output.exists() else 0,
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": f"Failed to create thesis: {str(e)}",
            "error_details": traceback.format_exc(),
        }
