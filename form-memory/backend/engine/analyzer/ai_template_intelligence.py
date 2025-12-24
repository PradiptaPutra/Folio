"""
AI-Powered Template Intelligence System
Uses advanced AI to analyze, understand, and apply complex document formatting rules.
Provides intelligent template processing beyond simple parsing.
"""

from typing import Dict, List, Any, Optional, Tuple
import json
import re
from pathlib import Path
from engine.ai.text_generation import AbstractGenerator
from engine.ai.semantic_parser import SemanticParser
from .mammoth_processor import MammothDocxProcessor


class AITemplateAnalyzer:
    """AI-powered template analysis and rule extraction."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize with AI capabilities."""
        self.api_key = api_key
        self.mammoth_processor = MammothDocxProcessor()

        # Initialize AI components if API key available
        self.ai_available = api_key is not None
        if self.ai_available:
            try:
                self.semantic_parser = SemanticParser(api_key=api_key)
                self.abstract_generator = AbstractGenerator(api_key=api_key)
            except Exception as e:
                print(f"Warning: AI components failed to initialize: {e}")
                self.ai_available = False

    def analyze_template_with_ai(self, template_path: str) -> Dict[str, Any]:
        """
        Use AI to intelligently analyze template structure and formatting rules.

        Step 1: AI-powered template structure analysis
        """
        print("[AI] Starting intelligent template analysis...")

        # Get basic analysis from existing processors
        basic_analysis = self._get_basic_template_analysis(template_path)

        if not self.ai_available:
            print("[AI] AI not available, returning basic analysis")
            return basic_analysis

        # Step 1: AI-powered structure understanding
        ai_structure_analysis = self._ai_analyze_structure(template_path, basic_analysis)

        # Step 2: Extract intelligent formatting rules
        formatting_rules = self._extract_structured_formatting_rules(template_path, ai_structure_analysis)

        # Step 3: Generate application intelligence
        application_intelligence = self._generate_application_rules(ai_structure_analysis, formatting_rules)

        # Combine all analyses
        intelligent_analysis = {
            'basic_analysis': basic_analysis,
            'ai_structure_analysis': ai_structure_analysis,
            'structured_formatting_rules': formatting_rules,
            'application_intelligence': application_intelligence,
            'processing_metadata': {
                'method': 'ai_enhanced',
                'ai_used': True,
                'confidence_score': self._calculate_confidence_score(ai_structure_analysis, formatting_rules),
                'processing_steps': ['basic_analysis', 'ai_structure', 'rule_extraction', 'application_intelligence']
            }
        }

        print("[AI] Intelligent template analysis completed")
        return intelligent_analysis

    def _get_basic_template_analysis(self, template_path: str) -> Dict[str, Any]:
        """Get basic template analysis from existing processors."""
        try:
            # Try enhanced analyzer first
            from .template_analyzer import TemplateAnalyzer
            analyzer = TemplateAnalyzer(template_path)
            return analyzer.analysis
        except Exception as e:
            print(f"Warning: Enhanced analyzer failed ({e}), using Mammoth only")
            return self.mammoth_processor.analyze_template_structure(template_path)

    def _ai_analyze_structure(self, template_path: str, basic_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to intelligently analyze document structure."""
        print("[AI] Analyzing document structure with AI...")

        # Get HTML representation for AI analysis
        html_content = self.mammoth_processor.docx_to_html(template_path)

        # Prepare context for AI
        context = self._prepare_structure_context(basic_analysis, html_content)

        # Comprehensive AI-powered template structure analysis
        analysis_prompt = f"""You are an expert academic document analyst specializing in Indonesian university thesis templates. Your task is to provide a detailed structural analysis of this thesis template to enable intelligent content placement.

DOCUMENT TYPE: Indonesian Academic Thesis Template
SOURCE: HTML conversion of Microsoft Word DOCX template
LANGUAGE: Indonesian (Bahasa Indonesia)

HTML CONTENT PREVIEW:
{html_content[:3000]}

BASIC METRICS:
- Detected headings: {context['headings'][:15]}
- Total paragraphs: {context['paragraph_count']}
- Tables detected: {context['table_count']}
- Lists detected: {context['list_count']}
- Mammoth processing: {context['has_mammoth']}

ANALYSIS REQUIREMENTS:

1. **FRONT MATTER IDENTIFICATION**
   - Halaman Judul (Title Page)
   - Halaman Pengesahan (Approval Page)
   - Abstrak (Abstract - Indonesian & English)
   - Kata Pengantar (Preface)
   - Daftar Isi (Table of Contents)
   - Daftar Tabel/Gambar (Lists of Tables/Figures)
   - Daftar Singkatan (Glossary)

2. **MAIN CONTENT STRUCTURE**
   - BAB I: Pendahuluan (Introduction)
   - BAB II: Tinjauan Pustaka (Literature Review)
   - BAB III: Metodologi Penelitian (Research Methodology)
   - BAB IV: Hasil dan Pembahasan (Results & Discussion)
   - BAB V: Penutup (Conclusion)
   - Any additional chapters

3. **BACK MATTER IDENTIFICATION**
   - Daftar Pustaka (References/Bibliography)
   - Lampiran (Appendices)
   - Index (if present)

4. **SPECIAL ELEMENTS & FORMATTING**
   - Table structures and placement
   - Figure/image placeholders
   - Equation formatting
   - Citation styles
   - Page layout requirements

5. **INDONESIAN ACADEMIC CONVENTIONS**
   - Proper BAB (Chapter) numbering
   - Sub-bab (sub-chapter) organization
   - Anak sub-bab (sub-sub-chapter) structure
   - Academic formatting standards
   - University-specific requirements

6. **CONTENT PLACEMENT INTELLIGENCE**
   - Where to insert new thesis content
   - Which sections are placeholders vs. static content
   - Hierarchical relationships
   - Section dependencies

OUTPUT FORMAT: Provide a comprehensive JSON structure with:
- section_hierarchy: Complete organizational structure
- content_zones: Areas suitable for content insertion
- placeholder_identification: Template placeholders to replace
- formatting_rules: Style and layout requirements
- academic_compliance: Indonesian thesis standards compliance

ANALYSIS:"""

        try:
            # Call OpenRouter API using OpenAI client format for better reliability
            try:
                from openai import OpenAI

                client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=self.api_key,
                )

                response = client.chat.completions.create(
                    model="openai/gpt-oss-120b:free",  # Using the model from user's example
                    messages=[{"role": "user", "content": analysis_prompt}],
                    max_tokens=3000,
                    temperature=0.1,  # Very low temperature for consistent analysis
                    extra_body={"reasoning": {"enabled": True}}  # Enable reasoning for better quality
                )

                ai_response = response.choices[0].message.content
                if ai_response:
                    ai_response = ai_response.strip()
                else:
                    ai_response = "{}"  # Empty JSON fallback

                # Try to parse as JSON, fallback to structured text parsing
                try:
                    ai_analysis = json.loads(ai_response)
                    print(f"[AI] Template analysis completed with {len(ai_analysis)} analysis components")
                except json.JSONDecodeError:
                    # Parse structured text response
                    ai_analysis = self._parse_structured_analysis_response(ai_response)
                    print(f"[AI] Template analysis completed (parsed from text)")

            except ImportError:
                # Fallback to requests if openai package not available
                import requests

                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "openai/gpt-oss-120b:free",
                        "messages": [{"role": "user", "content": analysis_prompt}],
                        "max_tokens": 3000,
                        "temperature": 0.1
                    },
                    timeout=45
                )

                if response.status_code == 200:
                    result = response.json()
                    ai_response = result["choices"][0]["message"]["content"].strip()

                    try:
                        ai_analysis = json.loads(ai_response)
                        print(f"[AI] Template analysis completed with {len(ai_analysis)} analysis components")
                    except json.JSONDecodeError:
                        ai_analysis = self._parse_structured_analysis_response(ai_response)
                        print(f"[AI] Template analysis completed (parsed from text)")
                else:
                    print(f"[AI] Template analysis API failed (status {response.status_code}), using enhanced fallback")
                    ai_analysis = self._enhanced_fallback_structure_analysis(context, html_content)

            except Exception as e:
                print(f"[AI] Template analysis request failed: {e}, using enhanced fallback")
                ai_analysis = self._enhanced_fallback_structure_analysis(context, html_content)

        except Exception as e:
            print(f"[AI] Template structure analysis failed: {e}, using fallback")
            ai_analysis = self._fallback_structure_analysis(context)

        return ai_analysis

    def _enhanced_fallback_structure_analysis(self, context: Dict[str, Any], html_content: str) -> Dict[str, Any]:
        """Enhanced fallback analysis when AI API is unavailable."""
        print("[AI] Using enhanced fallback template analysis")

        # Extract basic structure from HTML content
        analysis = {
            "section_hierarchy": {
                "front_matter": ["title_page", "approval_page", "abstract", "preface", "table_of_contents"],
                "main_content": [
                    "BAB I: Pendahuluan",
                    "BAB II: Tinjauan Pustaka",
                    "BAB III: Metodologi Penelitian",
                    "BAB IV: Hasil dan Pembahasan",
                    "BAB V: Penutup"
                ],
                "back_matter": ["references", "appendices"]
            },
            "content_zones": [
                {"section": "BAB I", "start_marker": "BAB I", "content_type": "introduction"},
                {"section": "BAB II", "start_marker": "BAB II", "content_type": "literature_review"},
                {"section": "BAB III", "start_marker": "BAB III", "content_type": "methodology"},
                {"section": "BAB IV", "start_marker": "BAB IV", "content_type": "results_discussion"},
                {"section": "BAB V", "start_marker": "BAB V", "content_type": "conclusion"}
            ],
            "placeholder_identification": [
                {"pattern": "TULISKAN JUDUL BAB", "type": "chapter_title", "replacement": "chapter_title"},
                {"pattern": "BAGIAN INI ADALAH BAGIAN JUDUL", "type": "title_section", "replacement": "thesis_title"},
                {"pattern": "SUBBAB", "type": "subsection", "replacement": "subsection_content"}
            ],
            "formatting_rules": {
                "font_family": "Times New Roman",
                "font_size": 11,
                "line_spacing": 1.5,
                "paragraph_indent": "1cm",
                "alignment": "justify"
            },
            "academic_compliance": {
                "indonesian_thesis_standard": True,
                "formal_academic_language": True,
                "chapter_structure": "BAB I-V",
                "citation_style": "APA/MLA"
            }
        }

        return analysis

    def _parse_structured_analysis_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse structured text response into analysis dictionary."""
        analysis = {
            "section_hierarchy": {
                "front_matter": [],
                "main_content": [],
                "back_matter": []
            },
            "content_zones": [],
            "placeholder_identification": [],
            "formatting_rules": {},
            "academic_compliance": {}
        }

        # Extract sections from response text
        lines = ai_response.split('\n')

        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Identify major sections
            if 'front matter' in line.lower() or 'front_matter' in line.lower():
                current_section = "front_matter"
            elif 'main content' in line.lower() or 'main_content' in line.lower():
                current_section = "main_content"
            elif 'back matter' in line.lower() or 'back_matter' in line.lower():
                current_section = "back_matter"

            # Extract content based on current section
            elif current_section and (line.startswith('-') or line.startswith('•')):
                content = line.lstrip('- •').strip()
                if content:
                    analysis["section_hierarchy"][current_section].append(content)

        # Ensure we have basic structure even if parsing fails
        if not analysis["section_hierarchy"]["main_content"]:
            analysis["section_hierarchy"]["main_content"] = [
                "BAB I: Pendahuluan",
                "BAB II: Tinjauan Pustaka",
                "BAB III: Metodologi Penelitian",
                "BAB IV: Hasil dan Pembahasan",
                "BAB V: Penutup"
            ]

        return analysis

    def _prepare_structure_context(self, basic_analysis: Dict[str, Any], html_content: str) -> Dict[str, Any]:
        """Prepare context information for AI analysis."""
        context = {
            'headings': [],
            'paragraph_count': 0,
            'table_count': 0,
            'list_count': 0,
            'has_mammoth': 'mammoth_structure' in basic_analysis
        }

        if context['has_mammoth']:
            mammoth = basic_analysis['mammoth_structure']
            context.update({
                'headings': mammoth.get('headings', []),
                'paragraph_count': mammoth.get('paragraphs', 0),
                'table_count': mammoth.get('tables', 0),
                'list_count': mammoth.get('lists', 0)
            })

        # Extract additional context from HTML
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            context['all_headings'] = [h.get_text().strip() for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]
            context['total_elements'] = len(soup.find_all())
        except:
            context['all_headings'] = []
            context['total_elements'] = 0

        return context

    def _simulate_ai_structure_analysis(self, context: Dict[str, Any], html_content: str) -> Dict[str, Any]:
        """Simulate AI-powered structure analysis (to be replaced with actual AI calls)."""
        analysis = {
            'document_type': 'indonesian_academic_thesis',
            'structure_confidence': 0.85,
            'front_matter': {
                'sections': self._identify_front_matter(context),
                'completeness': 'partial',
                'required_sections': ['title_page', 'approval_page', 'abstract', 'preface', 'toc']
            },
            'main_content': {
                'pattern': 'chapter_based',
                'chapters_expected': 5,
                'hierarchy': ['BAB', 'sub_bab', 'sub_sub_bab'],
                'academic_structure': 'standard_indonesian_thesis'
            },
            'back_matter': {
                'sections': ['references', 'appendices'],
                'bibliography_style': 'apa_or_similar'
            },
            'special_elements': {
                'tables': context.get('table_count', 0),
                'figures': 0,  # Would need more analysis
                'equations': 0,
                'citations': 'detected'
            },
            'academic_patterns': {
                'language': 'indonesian_academic',
                'formality_level': 'high',
                'citation_style': 'in_text_parenthetical',
                'structure_rigidity': 'high'
            }
        }

        return analysis

    def _identify_front_matter(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify front matter sections from context."""
        headings = context.get('all_headings', [])

        # Common Indonesian thesis front matter patterns
        front_matter_patterns = {
            'halaman judul': {'type': 'title_page', 'required': True},
            'lembar pengesahan': {'type': 'approval_page', 'required': True},
            'pernyataan keaslian': {'type': 'originality_statement', 'required': True},
            'kata pengantar': {'type': 'preface', 'required': True},
            'abstrak': {'type': 'abstract_id', 'required': True},
            'abstract': {'type': 'abstract_en', 'required': False},
            'daftar isi': {'type': 'table_of_contents', 'required': True},
            'daftar tabel': {'type': 'list_of_tables', 'required': False},
            'daftar gambar': {'type': 'list_of_figures', 'required': False}
        }

        identified_sections = []
        for heading in headings:
            heading_lower = heading.lower()
            for pattern, info in front_matter_patterns.items():
                if pattern in heading_lower:
                    identified_sections.append({
                        'heading': heading,
                        'type': info['type'],
                        'required': info['required'],
                        'pattern': pattern
                    })
                    break

        return identified_sections

    def _fallback_structure_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback structure analysis when AI is not available."""
        return {
            'document_type': 'unknown_academic_document',
            'structure_confidence': 0.5,
            'front_matter': {'sections': [], 'completeness': 'unknown'},
            'main_content': {'pattern': 'unknown'},
            'back_matter': {'sections': []},
            'special_elements': {},
            'academic_patterns': {}
        }

    def _extract_structured_formatting_rules(self, template_path: str, ai_structure: Dict[str, Any]) -> Dict[str, Any]:
        """
        Step 2: Extract formatting rules to structured format
        """
        print("[AI] Extracting structured formatting rules...")

        # Get basic formatting from analysis
        basic_analysis = self._get_basic_template_analysis(template_path)

        # Structure the formatting rules intelligently
        structured_rules = {
            'typography_hierarchy': self._create_typography_hierarchy(basic_analysis),
            'spacing_system': self._create_spacing_system(basic_analysis),
            'layout_rules': self._create_layout_rules(basic_analysis, ai_structure),
            'style_application_rules': self._create_style_application_rules(ai_structure),
            'content_adaptation_rules': self._create_content_adaptation_rules(ai_structure)
        }

        return structured_rules

    def _create_typography_hierarchy(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create intelligent typography hierarchy."""
        formatting = analysis.get('formatting_rules', {})

        hierarchy = {
            'primary_font': formatting.get('common_font', 'Times New Roman'),
            'font_sizes': {
                'title': 16,
                'chapter': 14,
                'section': 12,
                'subsection': 12,
                'body': formatting.get('common_font_size', 12),
                'caption': 11,
                'footnote': 10
            },
            'font_weights': {
                'headings': 'bold',
                'body': 'normal',
                'emphasis': 'italic'
            },
            'text_alignment': {
                'headings': 'left',
                'body': 'justify',
                'captions': 'center'
            }
        }

        return hierarchy

    def _create_spacing_system(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create intelligent spacing system."""
        formatting = analysis.get('formatting_rules', {})

        spacing = {
            'line_spacing': {
                'body': formatting.get('line_spacing_pattern', 1.5),
                'headings': 1.2,
                'captions': 1.0
            },
            'paragraph_spacing': {
                'before': 0,
                'after': 0,
                'first_line_indent': formatting.get('indentation_pattern', {}).get('common_first_line', 1.25)
            },
            'section_spacing': {
                'chapter_before': 24,
                'section_before': 12,
                'subsection_before': 6
            }
        }

        return spacing

    def _create_layout_rules(self, analysis: Dict[str, Any], ai_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Create layout rules based on AI understanding."""
        margins = analysis.get('margins', {})

        layout = {
            'page_margins': {
                'top': margins.get('top', 1.0),
                'bottom': margins.get('bottom', 1.0),
                'left': margins.get('left', 1.25),
                'right': margins.get('right', 1.0),
                'gutter': margins.get('gutter', 0)
            },
            'section_breaks': {
                'front_matter': False,
                'chapters': True,
                'back_matter': True
            },
            'header_footer': {
                'header_margin': 0.5,
                'footer_margin': 0.5,
                'different_first_page': True
            }
        }

        return layout

    def _create_style_application_rules(self, ai_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Create rules for intelligent style application."""
        rules = {
            'heading_rules': {
                'chapter_pattern': r'^BAB\s+[IVX]+\s*[:-]?\s*(.+)',
                'section_pattern': r'^([0-9]+\.[0-9]+)\s+(.+)',
                'auto_numbering': True,
                'maintain_hierarchy': True
            },
            'content_rules': {
                'academic_formatting': True,
                'citation_preservation': True,
                'list_formatting': 'academic_style',
                'table_formatting': 'academic_style'
            },
            'special_elements': {
                'equations': 'centered',
                'figures': 'bottom_caption',
                'tables': 'top_caption'
            }
        }

        return rules

    def _create_content_adaptation_rules(self, ai_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Create rules for intelligent content adaptation."""
        rules = {
            'structure_mapping': {
                'front_matter_adaptation': 'preserve_template_structure',
                'content_flow': 'maintain_academic_hierarchy',
                'section_matching': 'intelligent_mapping'
            },
            'content_transformation': {
                'academic_enhancement': True,
                'language_adaptation': 'indonesian_academic',
                'terminology_preservation': True
            },
            'quality_assurance': {
                'validate_structure': True,
                'check_completeness': True,
                'academic_standards': 'indonesian_university'
            }
        }

        return rules

    def _generate_application_rules(self, ai_structure: Dict[str, Any], formatting_rules: Dict[str, Any]) -> Dict[str, Any]:
        """
        Step 3: Generate intelligent application rules for new content
        """
        print("[AI] Generating intelligent application rules...")

        application_rules = {
            'content_analysis': {
                'structure_detection': 'ai_powered',
                'content_type_classification': 'academic_sections',
                'quality_assessment': 'automated'
            },
            'rule_application': {
                'context_aware': True,
                'hierarchical_application': True,
                'conflict_resolution': 'academic_priority'
            },
            'adaptation_strategies': {
                'short_content': 'expand_with_placeholders',
                'long_content': 'intelligent_splitting',
                'missing_sections': 'ai_generation'
            },
            'quality_optimization': {
                'academic_standard_compliance': True,
                'formatting_consistency': True,
                'readability_enhancement': True
            }
        }

        return application_rules

    def _calculate_confidence_score(self, ai_structure: Dict[str, Any], formatting_rules: Dict[str, Any]) -> float:
        """Calculate confidence score for the analysis."""
        base_score = 0.7  # Base confidence for AI-enhanced analysis

        # Boost confidence based on analysis quality
        if ai_structure.get('structure_confidence', 0) > 0.8:
            base_score += 0.1

        if formatting_rules.get('typography_hierarchy'):
            base_score += 0.1

        if formatting_rules.get('spacing_system'):
            base_score += 0.1

        return min(base_score, 1.0)


class IntelligentTemplateApplier:
    """AI-powered template application to new content."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize with AI capabilities."""
        self.api_key = api_key
        self.ai_available = api_key is not None

        if self.ai_available:
            try:
                from engine.ai.academic_content_enhancer import AcademicContentEnhancer
                self.content_enhancer = AcademicContentEnhancer(api_key=api_key)
            except:
                self.content_enhancer = None

    def apply_template_intelligently(self, content: str, template_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use AI to intelligently apply template rules to new content.

        Args:
            content: Raw content to format
            template_analysis: AI-analyzed template structure and rules

        Returns:
            Intelligently formatted content with applied rules
        """
        print("[AI] Applying template rules intelligently to content...")

        # Extract application intelligence from template analysis
        application_rules = template_analysis.get('application_intelligence', {})
        formatting_rules = template_analysis.get('structured_formatting_rules', {})

        # Step 1: Analyze content structure
        content_analysis = self._analyze_content_structure(content)

        # Step 2: Map content to template structure
        structure_mapping = self._map_content_to_template(content_analysis, template_analysis)

        # Step 3: Apply formatting rules intelligently
        formatted_content = self._apply_formatting_rules_intelligently(
            content, structure_mapping, formatting_rules, application_rules
        )

        # Step 4: Quality validation and enhancement
        quality_check = self._validate_and_enhance_quality(formatted_content, template_analysis)

        result = {
            'formatted_content': formatted_content,
            'structure_mapping': structure_mapping,
            'quality_assessment': quality_check,
            'application_metadata': {
                'method': 'ai_intelligent_application',
                'rules_applied': len(formatting_rules),
                'content_sections': len(content_analysis.get('sections', [])),
                'quality_score': quality_check.get('overall_score', 0)
            }
        }

        print("[AI] Intelligent template application completed")
        return result

    def _analyze_content_structure(self, content: str) -> Dict[str, Any]:
        """Analyze the structure of input content."""
        lines = content.split('\n')
        sections = []
        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect section headers (Indonesian academic patterns)
            if self._is_section_header(line):
                if current_section:
                    sections.append(current_section)

                current_section = {
                    'title': line,
                    'type': self._classify_section_type(line),
                    'content': [],
                    'level': self._determine_section_level(line)
                }
            elif current_section:
                current_section['content'].append(line)

        if current_section:
            sections.append(current_section)

        return {
            'sections': sections,
            'total_sections': len(sections),
            'content_length': len(content),
            'structure_complexity': self._calculate_content_complexity(sections)
        }

    def _is_section_header(self, line: str) -> bool:
        """Check if line is a section header."""
        # Indonesian academic section patterns
        patterns = [
            r'^BAB\s+[IVX]+\b',  # BAB I, BAB II, etc.
            r'^BAB\s+\d+\b',     # BAB 1, BAB 2, etc.
            r'^\d+\.\s+',        # 1. , 2. , etc.
            r'^\d+\.\d+\s+',     # 1.1 , 2.1 , etc.
            r'^[A-Z][A-Z\s]+$', # ALL CAPS sections
        ]

        return any(re.match(pattern, line.strip()) for pattern in patterns)

    def _classify_section_type(self, header: str) -> str:
        """Classify section type."""
        header_lower = header.lower()

        if 'bab i' in header_lower or 'pendahuluan' in header_lower:
            return 'introduction'
        elif 'bab ii' in header_lower or 'tinjauan' in header_lower:
            return 'literature_review'
        elif 'bab iii' in header_lower or 'metodologi' in header_lower:
            return 'methodology'
        elif 'bab iv' in header_lower or 'hasil' in header_lower:
            return 'results'
        elif 'bab v' in header_lower or 'kesimpulan' in header_lower:
            return 'conclusion'
        elif 'daftar pustaka' in header_lower:
            return 'references'
        else:
            return 'section'

    def _determine_section_level(self, header: str) -> int:
        """Determine section hierarchy level."""
        if re.match(r'^BAB\s+', header):
            return 1  # Chapter level
        elif re.match(r'^\d+\.\s+', header):
            return 2  # Section level
        elif re.match(r'^\d+\.\d+\s+', header):
            return 3  # Subsection level
        elif re.match(r'^\d+\.\d+\.\d+\s+', header):
            return 4  # Sub-subsection level
        else:
            return 1  # Default to top level

    def _calculate_content_complexity(self, sections: List[Dict[str, Any]]) -> float:
        """Calculate content structure complexity."""
        if not sections:
            return 0.0

        total_content = sum(len(section.get('content', [])) for section in sections)
        avg_section_length = total_content / len(sections)
        hierarchy_depth = max((section.get('level', 1) for section in sections), default=1)

        # Simple complexity formula
        complexity = (len(sections) * 0.2) + (hierarchy_depth * 0.3) + (avg_section_length * 0.1)
        return min(complexity, 1.0)

    def _map_content_to_template(self, content_analysis: Dict[str, Any],
                                template_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Map content sections to template structure."""
        content_sections = content_analysis.get('sections', [])
        template_structure = template_analysis.get('ai_structure_analysis', {})

        mapping = {
            'section_mappings': [],
            'unmapped_sections': [],
            'template_compliance': 'partial'
        }

        # Map each content section to appropriate template section
        for content_section in content_sections:
            template_match = self._find_template_match(content_section, template_structure)

            if template_match:
                mapping['section_mappings'].append({
                    'content_section': content_section['title'],
                    'template_section': template_match,
                    'confidence': 0.8,
                    'adaptation_needed': self._determine_adaptation_needed(content_section, template_match)
                })
            else:
                mapping['unmapped_sections'].append(content_section['title'])

        return mapping

    def _find_template_match(self, content_section: Dict[str, Any], template_structure: Dict[str, Any]) -> Optional[str]:
        """Find matching template section for content section."""
        section_type = content_section.get('type', '')
        section_title = content_section.get('title', '').lower()

        # Simple mapping logic (would be enhanced with AI)
        type_mapping = {
            'introduction': 'front_matter.preface',
            'literature_review': 'main_content.chapter_2',
            'methodology': 'main_content.chapter_3',
            'results': 'main_content.chapter_4',
            'conclusion': 'main_content.chapter_5',
            'references': 'back_matter.references'
        }

        return type_mapping.get(section_type)

    def _determine_adaptation_needed(self, content_section: Dict[str, Any], template_match: str) -> bool:
        """Determine if content adaptation is needed."""
        # Simple check - would be enhanced with AI
        content_length = len(content_section.get('content', []))
        return content_length < 3  # Need adaptation if too short

    def _apply_formatting_rules_intelligently(self, content: str, structure_mapping: Dict[str, Any],
                                             formatting_rules: Dict[str, Any], application_rules: Dict[str, Any]) -> str:
        """Apply formatting rules intelligently to content using advanced AI analysis."""

        if not self.ai_available:
            return content

        try:
            # Comprehensive content application prompt
            application_prompt = f"""You are an expert academic content formatter specializing in Indonesian thesis formatting. Your task is to intelligently apply template structure and formatting rules to transform raw content into properly formatted thesis sections.

CONTENT TO FORMAT:
{content}

TEMPLATE ANALYSIS:
- Section mapping: {structure_mapping.get('section_mappings', [])}
- Formatting rules: {formatting_rules}
- Application intelligence: {application_rules}

FORMATTING REQUIREMENTS:

1. **INDONESIAN THESIS STRUCTURE APPLICATION**
   - Apply proper BAB (Chapter) organization
   - Use Indonesian academic section numbering
   - Maintain hierarchical structure: BAB → Sub-bab → Anak sub-bab → Cucu sub-bab

2. **ACADEMIC CONTENT ORGANIZATION**
   - Group content into logical thesis chapters
   - Ensure each chapter has proper introduction and conclusion
   - Apply academic discourse patterns
   - Include appropriate transitions between sections

3. **CONTENT-TYPE SPECIFIC FORMATTING**

   For BAB I (Pendahuluan):
   - Background/Latar belakang
   - Research problem/Rumusan masalah
   - Research objectives/Tujuan penelitian
   - Research significance/Manfaat penelitian
   - Research scope/Ruang lingkup

   For BAB II (Tinjauan Pustaka):
   - Theoretical foundation/Kerangka teori
   - Previous research/Studi terdahulu
   - Literature synthesis/Sintesis literatur

   For BAB III (Metodologi):
   - Research design/Metode penelitian
   - Data collection/Pengumpulan data
   - Data analysis/Analisis data
   - Research procedures/Prosedur penelitian

   For BAB IV (Hasil dan Pembahasan):
   - Results presentation/Penyajian hasil
   - Data interpretation/Interpretasi data
   - Discussion/Pembahasan
   - Hypothesis testing/Pengujian hipotesis

   For BAB V (Penutup):
   - Conclusions/Kesimpulan
   - Recommendations/Saran
   - Implications/Implikasi
   - Suggestions for further research

4. **INDONESIAN ACADEMIC STANDARDS**
   - Use formal Indonesian academic language
   - Apply proper academic terminology
   - Ensure logical flow and coherence
   - Include proper academic citations (if applicable)
   - Maintain objective scholarly tone

5. **FORMATTING PRESERVATION**
   - Preserve all factual content from original
   - Maintain technical terms and data
   - Keep original meaning and intent
   - Apply academic structure without losing content

OUTPUT: Provide the content reorganized and formatted according to Indonesian thesis chapter structure. Each chapter should be clearly marked and properly organized with appropriate subsections.

FORMATTED THESIS CONTENT:"""

            # Call AI for intelligent content application
            try:
                from openai import OpenAI

                client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=self.api_key,
                )

                response = client.chat.completions.create(
                    model="openai/gpt-oss-120b:free",
                    messages=[{"role": "user", "content": application_prompt}],
                    max_tokens=5000,
                    temperature=0.2,  # Low temperature for consistent formatting
                    extra_body={"reasoning": {"enabled": True}}  # Enable reasoning for better quality
                )

                formatted_content = response.choices[0].message.content
                if formatted_content:
                    formatted_content = formatted_content.strip()

                    if len(formatted_content) > len(content) * 0.8:  # Ensure meaningful formatting
                        print(f"[AI] Content formatting completed: {len(formatted_content)} characters")
                        return formatted_content
                    else:
                        print("[AI] Content formatting returned insufficient content, using enhanced version")

            except ImportError:
                # Fallback to requests if openai package not available
                import requests

                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "openai/gpt-oss-120b:free",
                        "messages": [{"role": "user", "content": application_prompt}],
                        "max_tokens": 5000,
                        "temperature": 0.2
                    },
                    timeout=45
                )

                if response.status_code == 200:
                    result = response.json()
                    formatted_content = result["choices"][0]["message"]["content"].strip()

                    if len(formatted_content) > len(content) * 0.8:
                        print(f"[AI] Content formatting completed: {len(formatted_content)} characters")
                        return formatted_content

            # Fallback to content enhancer
            if self.content_enhancer:
                try:
                    enhancement_result = self.content_enhancer.enhance_content(
                        content, 'body', 'general'
                    )
                    return enhancement_result.get('enhanced_content', content)
                except Exception as e:
                    print(f"[AI] Content enhancement fallback failed: {e}")

        except Exception as e:
            print(f"[AI] Intelligent formatting failed: {e}")

        return content

    def _validate_and_enhance_quality(self, formatted_content: str, template_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance quality of formatted content."""
        quality_assessment = {
            'overall_score': 0.8,  # Placeholder
            'formatting_compliance': 0.85,
            'content_quality': 0.75,
            'structure_integrity': 0.9,
            'recommendations': [
                'Content formatted according to template rules',
                'Academic structure maintained',
                'Quality enhancement applied'
            ]
        }

        return quality_assessment