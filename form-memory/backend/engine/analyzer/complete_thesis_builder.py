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
from ..ai.thesis_rewriter import ThesisRewriter


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
        self.ai_data = {}  # Will be populated during build
        self.mapper = ContentMapper(self.analyzer, self.extractor, self.ai_data)

        # Initialize AI-powered components for perfect formatting (optional)
        self.perfect_adapter = None
        self.quality_validator = None

        # Initialize AI components dynamically in build method
        self.thesis_rewriter = ThesisRewriter(api_key=api_key) if api_key else None
        self.ai_data = {}  # Will be populated during build

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

        # CRITICAL FIX: Get analyzed_data from the first AI call
        analyzed_data = None
        if self.use_ai and hasattr(self.ai_extractor, 'analyzed_data') and self.ai_extractor.analyzed_data:
            analyzed_data = self.ai_extractor.analyzed_data
            print(f"[INFO] Retrieved analyzed_data from ai_extractor: {type(analyzed_data)}")
            user_data['analyzed_data'] = analyzed_data
            print(f"[INFO] Added analyzed_data to user_data with keys: {list(analyzed_data.keys())}")
        elif self.use_ai and hasattr(self.ai_extractor, 'analyzed_data') and self.ai_extractor.analyzed_data:
            analyzed_data = self.ai_extractor.analyzed_data
            print(f"[INFO] Retrieved analyzed_data from ai_extractor: {type(analyzed_data)}")
            user_data['analyzed_data'] = analyzed_data
            print(f"[INFO] Added analyzed_data to user_data with keys: {list(analyzed_data.keys())}")

        # AI Thesis Rewriting Processing (keep this for compatibility)
        if self.use_ai and self.api_key and self.thesis_rewriter:
            try:
                print("[AI] Starting AI thesis rewriting")
                raw_text = self.extractor.get_raw_text()
                rewritten_data = self.thesis_rewriter.rewrite_thesis(raw_text)
                self.ai_data.update(rewritten_data)
                user_data.update(rewritten_data)
                print(f"[AI] Rewritten data keys: {list(rewritten_data.keys())}")
                # Recreate mapper with updated AI data
                self.mapper = ContentMapper(self.analyzer, self.extractor, self.ai_data)
            except Exception as e:
                print(f"[WARNING] AI rewriting failed: {e}")

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
            result = self._build_ai_intelligent(user_data)
        else:
            print("[DEBUG] Using standard document building")
            result = self._build_standard(user_data)

        # Ensure result is a Path object
        if not isinstance(result, Path):
            print(f"[ERROR] Build method returned {type(result).__name__} instead of Path: {result}")
            raise TypeError(f"Build method must return Path, got {type(result).__name__}")

        return result

    def _build_ai_intelligent(self, user_data):
        """Build thesis using AI-intelligent processing with proper template adaptation."""
        print(f"[DEBUG] Starting AI-intelligent build with enhanced content")

        # CRITICAL FIX: Check if we have analyzed_data from the first AI call
        analyzed_data = user_data.get('analyzed_data')
        if analyzed_data:
            print("[INFO] Using analyzed_data from first AI call for content insertion")
            return self._build_with_analyzed_data(user_data, analyzed_data)
        else:
            print("[WARNING] No analyzed_data found, falling back to standard approach")
            return self._build_standard(user_data)

    def _build_with_analyzed_data(self, user_data, analyzed_data):
        """Build document using the comprehensive analyzed_data from first AI call."""
        print("\n" + "="*60)
        print("BUILDING DOCUMENT WITH ANALYZED CONTENT")
        print("="*60)

        # Verify analyzed_data has content
        print(f"[VERIFY] Analyzed data keys: {list(analyzed_data.keys())}")

        # Check each chapter content
        for i in range(1, 7):
            chapter_key = f'chapter{i}'
            if chapter_key in analyzed_data:
                chapter = analyzed_data[chapter_key]
                print(f"\n[VERIFY] Chapter {i}:")
                for subsection, content in chapter.items():
                    content_length = len(content) if content else 0
                    preview = content[:100] if content else "[EMPTY]"
                    print(f"  - {subsection}: {content_length} chars | Preview: {preview}...")

                    if content_length < 200:
                        print(f"  ⚠️  WARNING: {subsection} content is too short ({content_length} chars)")
            else:
                print(f"\n[VERIFY] Chapter {i}: NOT FOUND")

        # Load template
        try:
            doc = Document(str(self.template_path))
            print(f"\n[INFO] Template loaded: {len(doc.paragraphs)} paragraphs")
        except Exception as e:
            print(f"[ERROR] Failed to load template: {e}")
            return self.output_path

        # Replace metadata first
        metadata = analyzed_data.get('metadata', {})
        title = metadata.get('title', user_data.get('title', 'Untitled Thesis'))
        author = metadata.get('author', user_data.get('author', 'Unknown'))
        nim = metadata.get('nim', user_data.get('nim', '00000000'))

        metadata_replacements = 0
        for para in doc.paragraphs:
            text = para.text.strip()
            # Replace title
            if any(phrase in text.upper() for phrase in ['TULIS JUDUL', 'JUDUL SKRIPSI', 'BAGIAN JUDUL']):
                para.text = title
                metadata_replacements += 1
                print(f"[METADATA] Replaced title: {title}")

            # Replace author
            if any(phrase in text.upper() for phrase in ['NAMA MAHASISWA', 'NAMA PENULIS']):
                para.text = author
                metadata_replacements += 1
                print(f"[METADATA] Replaced author: {author}")

            # Replace NIM
            if text == 'NIM' or text == '94523999' or len(text) == 8 and text.isdigit():
                para.text = nim
                metadata_replacements += 1
                print(f"[METADATA] Replaced NIM: {nim}")

        print(f"[INFO] Made {metadata_replacements} metadata replacements")

        # Insert chapter content
        chapters_data = {
            1: analyzed_data.get('chapter1', {}),
            2: analyzed_data.get('chapter2', {}),
            3: analyzed_data.get('chapter3', {}),
            4: analyzed_data.get('chapter4', {}),
            5: analyzed_data.get('chapter5', {}),
            6: analyzed_data.get('chapter6', {})
        }

        total_insertions = 0

        for chapter_num, chapter_content in chapters_data.items():
            if not chapter_content:
                print(f"[WARNING] No content for Chapter {chapter_num}")
                continue

            # Find chapter heading
            chapter_found = False
            chapter_para_index = None

            for i, para in enumerate(doc.paragraphs):
                if f"BAB {self._to_roman(chapter_num)}" in para.text.upper():
                    chapter_found = True
                    chapter_para_index = i
                    print(f"\n[INFO] Found Chapter {chapter_num} at paragraph {i}: '{para.text.strip()}'")
                    break

            if not chapter_found:
                print(f"[WARNING] Chapter {chapter_num} heading not found in template")
                continue

            # Insert content for each subsection
            current_index = chapter_para_index + 1
            chapter_insertions = 0

            for subsection_key, subsection_content in chapter_content.items():
                if not subsection_content or len(subsection_content.strip()) < 50:
                    print(f"[DEBUG] Skipping {subsection_key}: content too short ({len(subsection_content) if subsection_content else 0} chars)")
                    continue

                # Find next content paragraph after current position
                target_para = None
                target_index = None

                for j in range(current_index, min(current_index + 15, len(doc.paragraphs))):
                    para = doc.paragraphs[j]

                    # Check if this is a content paragraph (placeholder or empty content area)
                    if (para.style.name == 'isi paragraf' or
                        'Format paragraf dengan style' in para.text or
                        'TULISKAN' in para.text.upper() or
                        len(para.text.strip()) < 100):  # Likely a placeholder

                        target_para = para
                        target_index = j
                        break

                if target_para:
                    # INSERT THE CONTENT!
                    old_text = target_para.text[:50] if target_para.text else "[empty]"

                    # Clear existing content
                    target_para.clear()

                    # Add new content
                    run = target_para.add_run(subsection_content)

                    # Try to preserve style
                    try:
                        if hasattr(target_para, 'style') and 'isi paragraf' in str(target_para.style).lower():
                            target_para.style = target_para.style  # Keep existing style
                        else:
                            target_para.style = 'Normal'  # Fallback
                    except:
                        pass

                    print(f"[SUCCESS] Inserted {len(subsection_content)} chars into Chapter {chapter_num}.{subsection_key}")
                    print(f"[SUCCESS] Replaced: '{old_text}...' with '{subsection_content[:50]}...'")

                    total_insertions += 1
                    chapter_insertions += 1
                    current_index = target_index + 1
                else:
                    print(f"[WARNING] No target paragraph found for Chapter {chapter_num}.{subsection_key} after paragraph {current_index}")

            print(f"[INFO] Chapter {chapter_num}: {chapter_insertions} sections inserted")

        print(f"\n[FINAL] Total content insertions: {total_insertions}")

        if total_insertions == 0:
            print("[ERROR] NO CONTENT WAS INSERTED!")
            print("[ERROR] Check that analyzed_data has content and template has content paragraphs")
            return self.output_path

        # Save document
        print(f"[INFO] Saving document to: {self.output_path}")
        try:
            doc.save(str(self.output_path))
            print("[INFO] Document saved successfully")
        except Exception as e:
            print(f"[ERROR] Failed to save document: {e}")
            return self.output_path

        final_size = self.output_path.stat().st_size if self.output_path.exists() else 0
        print(f"[INFO] Final document size: {final_size} bytes")

        return self.output_path

    def _to_roman(self, num):
        """Convert number to Roman numeral."""
        val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
        syms = ['M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I']
        roman_num = ''
        i = 0
        while num > 0:
            for _ in range(num // val[i]):
                roman_num += syms[i]
                num -= val[i]
            i += 1
        return roman_num

    def _populate_template_with_ai_content(self, doc, ai_sections, user_data):
        """Populate template placeholders with AI-analyzed content while preserving formatting."""
        replacements_made = 0

        print(f"[DEBUG] Starting template population with {len(ai_sections)} AI sections")

        # DEBUG: Log what AI sections contain
        for i, section in enumerate(ai_sections[:3]):  # First 3 sections
            content = section.get('content', [])
            print(f"[DEBUG] AI Section {i}: title='{section.get('title', 'no title')}', content_lines={len(content)}")
            if content:
                print(f"[DEBUG] Content preview: {content[0][:100]}..." if content[0] else "Empty content")

        # Replace user data placeholders first (title, author, etc.)
        replacements_made += self._replace_user_data_placeholders(doc, user_data)

        # Replace chapter content placeholders with AI sections
        replacements_made += self._replace_chapter_placeholders(doc, ai_sections)

        # Clean up any remaining generic placeholders
        replacements_made += self._clean_generic_placeholders(doc)

        print(f"[DEBUG] Made {replacements_made} intelligent template replacements")
        return replacements_made

    def _replace_user_data_placeholders(self, doc, user_data):
        """Replace user data placeholders like title, author, etc."""
        replacements = 0

        # Title placeholders
        title_placeholders = [
            r'TULIS JUDUL', r'JUDUL SKRIPSI', r'JUDUL TUGAS AKHIR',
            r'BAGIAN JUDUL', r'HALAMAN JUDUL'
        ]

        title = user_data.get('title', '')
        if title:
            for para in doc.paragraphs:
                text = para.text.upper()
                for placeholder in title_placeholders:
                    if placeholder.upper() in text:
                        para.text = title
                        replacements += 1
                        print(f"[DEBUG] Replaced title placeholder with: '{title}'")
                        break

        # Author placeholders
        author_placeholders = [r'NAMA PENULIS', r'NAMA MAHASISWA', r'AUTHOR']
        author = user_data.get('author', '')
        if author:
            for para in doc.paragraphs:
                text = para.text.upper()
                for placeholder in author_placeholders:
                    if placeholder in text:
                        para.text = author
                        replacements += 1
                        print(f"[DEBUG] Replaced author placeholder with: '{author}'")
                        break

        # NIM placeholders
        nim_placeholders = [r'NIM', r'NOMOR INDUK MAHASISWA']
        nim = user_data.get('nim', '')
        if nim:
            for para in doc.paragraphs:
                text = para.text.upper()
                for placeholder in nim_placeholders:
                    if placeholder in text:
                        para.text = nim
                        replacements += 1
                        print(f"[DEBUG] Replaced NIM placeholder with: '{nim}'")
                        break

        return replacements

    def _replace_chapter_placeholders(self, doc, ai_sections):
        """Replace chapter content placeholders with AI-analyzed sections."""
        replacements = 0

        # Map AI sections to chapter numbers - more flexible mapping
        chapter_mapping = {}
        for i, section in enumerate(ai_sections):
            title = section.get('title', '').upper()
            content = section.get('content', [])

            # Map based on position and keywords
            if i == 0 or 'BAB I' in title or 'PENDAHULUAN' in title or 'INTRODUCTION' in title:
                chapter_mapping['I'] = section
            elif i == 1 or 'BAB II' in title or 'TINJAUAN PUSTAKA' in title or 'LITERATURE' in title:
                chapter_mapping['II'] = section
            elif i == 2 or 'BAB III' in title or 'METODOLOGI' in title or 'METHODOLOGY' in title:
                chapter_mapping['III'] = section
            elif i == 3 or 'BAB IV' in title or 'HASIL' in title or 'ANALYSIS' in title or 'RESULTS' in title:
                chapter_mapping['IV'] = section
            elif i == 4 or 'BAB V' in title or 'PENUTUP' in title or 'CONCLUSION' in title:
                chapter_mapping['V'] = section
            elif i == 5 or 'BAB VI' in title:
                chapter_mapping['VI'] = section

        print(f"[DEBUG] Chapter mapping: {list(chapter_mapping.keys())}")

        # Replace content in ALL paragraphs that look like placeholders
        # This is the key fix - insert content instead of clearing
        content_inserted = 0
        placeholders_cleared = 0

        for para_idx, para in enumerate(doc.paragraphs):
            text = para.text.strip()
            upper_text = text.upper()

            # Skip if paragraph already has substantial content (likely already processed)
            if len(text) > 200:  # Increased threshold
                continue

            # Check for placeholder patterns that should be replaced with content
            is_placeholder = (
                'SUBBAB' in upper_text or
                'ANAK SUBBAB' in upper_text or
                'CUCU SUBBAB' in upper_text or
                'TULISKAN' in upper_text or
                'ISI BAB' in upper_text or
                'CONTENT' in upper_text or
                'KONTEN' in upper_text or
                (len(text) < 50 and len(text) > 0)  # Short placeholder text
            )

            if is_placeholder:
                print(f"[DEBUG] Processing paragraph {para_idx}: '{text[:50]}...' (placeholder: {is_placeholder})")

                # Find which chapter this belongs to
                chapter_num = self._find_parent_chapter(doc, para)
                print(f"[DEBUG] Chapter context: {chapter_num}")

                if chapter_num and chapter_num in chapter_mapping:
                    ai_section = chapter_mapping[chapter_num]
                    content_lines = ai_section.get('content', [])
                    print(f"[DEBUG] AI section has {len(content_lines)} content lines")

                    # CRITICAL FIX: Insert actual content instead of clearing
                    if content_lines and len(content_lines) > 0:
                        # Join all content lines into coherent paragraphs
                        # But split into multiple paragraphs if very long
                        full_content = ' '.join([line.strip() for line in content_lines if line.strip()])

                        if len(full_content) > 1000:  # Split long content
                            # Split into paragraphs at sentence boundaries
                            sentences = full_content.replace('?', '.').replace('!', '.').split('.')
                            paragraphs = []
                            current_para = ""
                            for sentence in sentences:
                                sentence = sentence.strip()
                                if not sentence:
                                    continue
                                if len(current_para + sentence) > 500:
                                    if current_para:
                                        paragraphs.append(current_para + '.')
                                    current_para = sentence
                                else:
                                    current_para += ('. ' if current_para else '') + sentence

                            if current_para:
                                paragraphs.append(current_para + '.')

                            # Insert first paragraph into current paragraph
                            para.text = paragraphs[0]
                            content_inserted += 1

                            # Add additional paragraphs
                            current_para_obj = para
                            for additional_para in paragraphs[1:]:
                                if additional_para.strip():
                                    new_para = doc.add_paragraph(additional_para)
                                    # Copy style from original
                                    new_para.style = para.style
                                    if hasattr(para, 'paragraph_format'):
                                        new_para.paragraph_format.left_indent = para.paragraph_format.left_indent
                                        new_para.paragraph_format.first_line_indent = para.paragraph_format.first_line_indent
                                        new_para.paragraph_format.line_spacing = para.paragraph_format.line_spacing
                                    current_para_obj = new_para
                                    content_inserted += 1

                            print(f"[DEBUG] INSERTED MULTI-PARAGRAPH content for chapter {chapter_num}: {len(full_content)} chars total")
                        elif full_content:
                            para.text = full_content
                            content_inserted += 1
                            print(f"[DEBUG] INSERTED content for chapter {chapter_num}: {len(full_content)} chars")
                            print(f"[DEBUG] Content preview: {full_content[:100]}...")
                        else:
                            para.text = ""  # Clear if no content
                            placeholders_cleared += 1
                    else:
                        para.text = ""  # Clear if no content available
                        placeholders_cleared += 1
                        print(f"[DEBUG] No content available for chapter {chapter_num}")
                else:
                    # If we can't map to a chapter, clear the placeholder
                    para.text = ""
                    placeholders_cleared += 1
                    print(f"[DEBUG] Cleared unmapped placeholder: '{text[:50]}...'")
            else:
                print(f"[DEBUG] Skipping paragraph {para_idx}: not a placeholder")

        print(f"[DEBUG] Content insertion summary: {content_inserted} paragraphs filled, {placeholders_cleared} placeholders cleared")
        replacements += content_inserted

        print(f"[DEBUG] Chapter content replacement completed: {replacements} insertions")
        return replacements

    def _find_parent_chapter(self, doc, target_para):
        """Find the chapter number for a given paragraph by looking backwards."""
        para_index = None
        for i, para in enumerate(doc.paragraphs):
            if para == target_para:
                para_index = i
                break

        if para_index is None:
            return None

        # Look backwards for chapter header
        for i in range(para_index - 1, max(-1, para_index - 10), -1):
            para = doc.paragraphs[i]
            text = para.text.strip().upper()
            if text.startswith('BAB '):
                parts = text.split()
                if len(parts) >= 2:
                    chapter_marker = parts[1].strip('.:')
                    if chapter_marker in ['I', 'II', 'III', 'IV', 'V', 'VI']:
                        return chapter_marker

        return None

    def _clean_generic_placeholders(self, doc):
        """Clean up any remaining generic placeholders."""
        replacements = 0

        placeholders_to_clear = [
            r'TULISKAN', r'ISI BAB', r'SUBBAB', r'ANAK SUBBAB', r'CUCU SUBBAB',
            r'KONTEN', r'CONTENT', r'PLACEHOLDER'
        ]

        for para in doc.paragraphs:
            text = para.text.upper()
            for placeholder in placeholders_to_clear:
                if placeholder in text and len(text) < 100:  # Only clear short placeholder text
                    para.text = ""
                    replacements += 1
                    print(f"[DEBUG] Cleared generic placeholder: '{text[:50]}...'")
                    break

        return replacements

    def _populate_template_structured(self, doc, ai_sections, user_data):
        """Fallback method: Populate template in a structured way if intelligent replacement fails."""
        print("[DEBUG] Using structured population approach")

        # Find main content area (after front matter)
        main_content_start = self._find_main_content_start(doc)

        # Insert AI content in structured sections
        insert_position = main_content_start
        for idx, section in enumerate(ai_sections, 1):
            if idx > 1:
                # Add page break between chapters
                if insert_position < len(doc.paragraphs):
                    doc.paragraphs[insert_position].insert_page_break_before()

            # Add chapter title
            title = section.get('title', f'Chapter {idx}')
            if insert_position < len(doc.paragraphs):
                doc.paragraphs[insert_position].text = title
                insert_position += 1
            else:
                new_para = doc.add_paragraph(title)
                new_para.style = "Heading 1"
                insert_position = len(doc.paragraphs)

            # Add chapter content
            content = section.get('content', [])
            for line in content:
                if isinstance(line, str) and line.strip():
                    if insert_position < len(doc.paragraphs):
                        doc.paragraphs[insert_position].text = line
                        insert_position += 1
                    else:
                        new_para = doc.add_paragraph(line)
                        new_para.style = "Normal"
                        insert_position = len(doc.paragraphs)

    def _find_main_content_start(self, doc):
        """Find where main content should start in the template."""
        # Look for the first chapter or main content area
        for i, para in enumerate(doc.paragraphs):
            text = para.text.strip().upper()
            if 'BAB I' in text or 'BAB 1' in text or 'CHAPTER 1' in text:
                return i
            # Look for table of contents end
            if 'DAFTAR ISI' in text and i < len(doc.paragraphs) - 1:
                # Skip a few paragraphs after TOC
                return min(i + 5, len(doc.paragraphs))

        # Default to middle of document
        return len(doc.paragraphs) // 2

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
        try:
            generator.create_references(doc, references)
        except Exception as e:
            print(f"[WARNING] Failed to create references: {e}")
            import traceback
            traceback.print_exc()
        
        # Appendices
        appendices = user_data.get("appendices", []) if user_data and isinstance(user_data, dict) else []
        if appendices:
            try:
                # Ensure appendices is a list
                if not isinstance(appendices, list):
                    appendices = [appendices]
                generator.create_appendices(doc, appendices)
            except Exception as e:
                print(f"[WARNING] Failed to create appendices: {e}")
                import traceback
                traceback.print_exc()
    
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
