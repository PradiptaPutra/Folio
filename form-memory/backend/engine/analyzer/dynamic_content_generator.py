"""
Dynamic AI Content Generation System
Analyzes template structure and generates content based on detected patterns and user input
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import re
from .advanced_template_analyzer import TemplateStructure, ZoneType


@dataclass
class ContentRequirements:
    """Requirements for content generation based on template analysis"""
    chapter_structure: Dict[int, List[str]] = field(default_factory=dict)  # chapter_num -> [subsection_types]
    content_types: Dict[str, str] = field(default_factory=dict)  # subsection_key -> content_type
    length_requirements: Dict[str, int] = field(default_factory=dict)  # subsection_key -> word_count
    academic_patterns: Dict[str, Any] = field(default_factory=dict)
    template_characteristics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GeneratedContent:
    """Generated content with metadata"""
    content: Dict[str, Any] = field(default_factory=dict)  # Same structure as analyzed_data
    generation_metadata: Dict[str, Any] = field(default_factory=dict)
    quality_metrics: Dict[str, Any] = field(default_factory=dict)


class DynamicContentGenerator:
    """
    Dynamic content generator that adapts to template structure and user input
    """

    def __init__(self):
        self.research_type_detector = ResearchTypeDetector()
        self.content_mapper = ContentMapper()
        self.prompt_builder = DynamicPromptBuilder()

    def generate_content(self, user_text: str, template_structure: TemplateStructure,
                        user_metadata: Dict[str, str], api_key: str) -> GeneratedContent:
        """
        Main content generation method

        Args:
            user_text: User's raw research text/draft
            template_structure: Analyzed template structure
            user_metadata: User metadata (title, author, etc.)
            api_key: OpenRouter API key

        Returns:
            GeneratedContent with structured content and metadata
        """
        print("[INFO] Starting dynamic content generation...")

        # Step 1: Analyze user's research
        research_analysis = self._analyze_user_research(user_text)
        print(f"[INFO] Research analysis: {research_analysis['type']} with {len(research_analysis['topics'])} topics")

        # Step 2: Extract template requirements
        requirements = self._extract_template_requirements(template_structure)
        print(f"[INFO] Template requirements: {len(requirements.chapter_structure)} chapters, "
              f"{sum(len(subs) for subs in requirements.chapter_structure.values())} subsections")

        # Step 3: Build dynamic AI prompt
        prompt = self.prompt_builder.build_prompt(
            research_analysis, requirements, user_metadata, template_structure
        )

        # Step 4: Generate content with AI
        ai_content = self._call_ai_generation(prompt, api_key)

        # Step 5: Structure and validate content
        structured_content = self._structure_ai_response(ai_content, requirements)

        # Step 6: Quality assessment
        quality_metrics = self._assess_content_quality(structured_content, requirements)

        result = GeneratedContent(
            content=structured_content,
            generation_metadata={
                'research_analysis': research_analysis,
                'template_requirements': requirements,
                'prompt_used': prompt[:200] + "...",  # Truncate for storage
                'ai_model': 'openai/gpt-4o-mini',
                'generation_timestamp': '2024-12-26'
            },
            quality_metrics=quality_metrics
        )

        print(f"[SUCCESS] Generated content: {len(structured_content)} chapters, "
              f"quality score: {quality_metrics.get('overall_score', 0):.1f}")

        return result

    def _analyze_user_research(self, user_text: str) -> Dict[str, Any]:
        """Analyze user's research draft to understand content and structure"""
        analysis = {
            'type': 'unknown',
            'topics': [],
            'methodology': [],
            'findings': [],
            'word_count': len(user_text.split()),
            'sections_identified': []
        }

        text_lower = user_text.lower()

        # Detect research type
        if any(word in text_lower for word in ['survei', 'kuesioner', 'survey', 'questionnaire']):
            analysis['type'] = 'survey'
        elif any(word in text_lower for word in ['eksperimen', 'experiment', 'uji coba']):
            analysis['type'] = 'experimental'
        elif any(word in text_lower for word in ['sistem', 'aplikasi', 'software', 'website']):
            analysis['type'] = 'system_development'
        elif any(word in text_lower for word in ['studi kasus', 'case study', 'analisis']):
            analysis['type'] = 'case_study'
        else:
            analysis['type'] = 'general_research'

        # Extract topics (simple keyword extraction)
        topic_keywords = [
            'pendidikan', 'kesehatan', 'ekonomi', 'teknologi', 'lingkungan',
            'sistem informasi', 'manajemen', 'pemasaran', 'keuangan', 'sumber daya manusia',
            'machine learning', 'artificial intelligence', 'data mining', 'big data'
        ]

        analysis['topics'] = [kw for kw in topic_keywords if kw in text_lower]

        # Extract methodology mentions
        methodology_keywords = [
            'wawancara', 'interview', 'observasi', 'observation', 'kuisioner', 'questionnaire',
            'eksperimen', 'experiment', 'studi literatur', 'literature study', 'analisis data'
        ]
        analysis['methodology'] = [kw for kw in methodology_keywords if kw in text_lower]

        # Extract findings/results
        if any(word in text_lower for word in ['hasil', 'result', 'temuan', 'finding', 'menunjukkan']):
            analysis['findings'].append('has_results')

        # Identify sections user has written about
        section_keywords = {
            'latar_belakang': ['latar', 'background', 'masalah', 'problem'],
            'metodologi': ['metode', 'method', 'metodologi', 'methodology'],
            'hasil': ['hasil', 'result', 'temuan', 'finding'],
            'kesimpulan': ['kesimpulan', 'conclusion', 'saran', 'recommendation']
        }

        for section, keywords in section_keywords.items():
            if any(kw in text_lower for kw in keywords):
                analysis['sections_identified'].append(section)

        return analysis

    def _extract_template_requirements(self, template_structure: TemplateStructure) -> ContentRequirements:
        """Extract content requirements from analyzed template"""
        requirements = ContentRequirements()

        # Analyze chapter structure
        chapter_structure = {}
        content_types = {}
        length_requirements = {}

        # Process detected chapters
        for chapter_info in template_structure.academic_patterns.get('chapters', []):
            chapter_num = chapter_info.get('chapter_num')
            if chapter_num:
                subsections = []

                # Find subsections for this chapter
                for subsection_info in template_structure.academic_patterns.get('subsections', []):
                    parent_chapter = subsection_info.get('parent_chapter')
                    if parent_chapter == chapter_info['zone_id']:
                        subsection_type = subsection_info.get('semantic_type', 'general')
                        subsections.append(subsection_type)

                        # Set content type and length requirements
                        content_types[f'chapter{chapter_num}_{subsection_type}'] = subsection_type
                        length_requirements[f'chapter{chapter_num}_{subsection_type}'] = \
                            self._estimate_subsection_length(subsection_type)

                chapter_structure[chapter_num] = subsections

        requirements.chapter_structure = chapter_structure
        requirements.content_types = content_types
        requirements.length_requirements = length_requirements
        requirements.academic_patterns = template_structure.academic_patterns
        requirements.template_characteristics = self._analyze_template_characteristics(template_structure)

        return requirements

    def _estimate_subsection_length(self, subsection_type: str) -> int:
        """Estimate word count for subsection type"""
        length_estimates = {
            'latar_belakang': 250,
            'rumusan_masalah': 150,
            'tujuan': 120,
            'manfaat': 120,
            'batasan': 100,
            'landasan_teori': 300,
            'penelitian_terkait': 200,
            'kerangka_pikir': 180,
            'metode': 200,
            'analisis': 250,
            'hasil': 200,
            'kesimpulan': 150,
            'saran': 120,
            'general': 150
        }
        return length_estimates.get(subsection_type, 150)

    def _analyze_template_characteristics(self, template_structure: TemplateStructure) -> Dict[str, Any]:
        """Analyze template characteristics for content generation"""
        characteristics = {
            'university_style': 'unknown',
            'language': 'indonesian',
            'formality_level': 'academic',
            'chapter_count': len(template_structure.academic_patterns.get('chapters', [])),
            'subsection_density': len(template_structure.academic_patterns.get('subsections', [])),
            'has_front_matter': len(template_structure.academic_patterns.get('front_matter', [])) > 0,
            'has_back_matter': len(template_structure.academic_patterns.get('back_matter', [])) > 0
        }

        # Detect university style
        all_text = ' '.join([zone.content for zone in template_structure.zones.values()])
        all_text_lower = all_text.lower()

        if 'universitas indonesia' in all_text_lower or 'ui' in all_text_lower:
            characteristics['university_style'] = 'ui'
        elif 'ugm' in all_text_lower or 'universitas gadjah mada' in all_text_lower:
            characteristics['university_style'] = 'ugm'
        elif 'itb' in all_text_lower or 'institut teknologi bandung' in all_text_lower:
            characteristics['university_style'] = 'itb'
        elif 'uII' in all_text_lower or 'universitas islam indonesia' in all_text_lower:
            characteristics['university_style'] = 'uii'

        return characteristics

    def _call_ai_generation(self, prompt: str, api_key: str) -> Dict[str, Any]:
        """Call AI API for content generation"""
        try:
            import openai

            client = openai.OpenAI(
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1"
            )

            response = client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert academic content generator for Indonesian university theses. Generate high-quality, formal academic content in Indonesian."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )

            content = response.choices[0].message.content
            print(f"[AI] Generated {len(content)} characters of content")

            # Parse JSON response
            import json
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                print(f"[WARNING] AI response not valid JSON: {content[:200]}...")
                return self._fallback_parse_ai_response(content)

        except Exception as e:
            print(f"[ERROR] AI generation failed: {e}")
            return self._generate_fallback_content()

    def _fallback_parse_ai_response(self, content: str) -> Dict[str, Any]:
        """Fallback parsing for non-JSON AI responses"""
        # Simple parsing - look for chapter markers
        result = {}

        # Split by common chapter markers
        chapters = re.split(r'(?=chapter\s*\d+|BAB\s*[IVXLCDM\d]+)', content, flags=re.IGNORECASE)

        for i, chapter_text in enumerate(chapters[1:], 1):  # Skip first empty part
            chapter_key = f'chapter{i}'
            result[chapter_key] = {}

            # Extract subsections (simple approach)
            lines = chapter_text.split('\n')
            subsection_count = 0

            for line in lines:
                line = line.strip()
                if len(line) > 20 and not line.startswith('#') and not line.startswith('---'):
                    subsection_count += 1
                    subsection_key = f'subsection_{subsection_count}'
                    result[chapter_key][subsection_key] = line

        return result

    def _generate_fallback_content(self) -> Dict[str, Any]:
        """Generate basic fallback content when AI fails"""
        return {
            "chapter1": {
                "latar_belakang": "Latar belakang penelitian ini menjelaskan konteks dan pentingnya topik yang diteliti.",
                "rumusan_masalah": "Rumusan masalah penelitian adalah pertanyaan penelitian yang akan dijawab.",
                "tujuan_penelitian": "Tujuan penelitian adalah untuk mencapai hasil yang diharapkan.",
                "manfaat_penelitian": "Manfaat penelitian memberikan kontribusi bagi berbagai pihak.",
                "batasan_masalah": "Batasan masalah menentukan ruang lingkup penelitian."
            },
            "chapter2": {
                "landasan_teori": "Landasan teori menjelaskan teori-teori yang mendasari penelitian.",
                "penelitian_terkait": "Penelitian terkait menunjukkan kajian sebelumnya di bidang ini.",
                "kerangka_pikir": "Kerangka pikir menunjukkan hubungan antar konsep dalam penelitian."
            },
            "chapter3": {
                "metode_penelitian": "Metode penelitian menjelaskan bagaimana penelitian dilakukan.",
                "teknik_pengumpulan_data": "Teknik pengumpulan data menjelaskan cara mendapatkan data.",
                "teknik_analisis_data": "Teknik analisis data menjelaskan cara mengolah data."
            }
        }

    def _structure_ai_response(self, ai_content: Dict[str, Any], requirements: ContentRequirements) -> Dict[str, Any]:
        """Structure AI response into standard format"""
        structured = {}

        # Map AI response to standard chapter structure
        for chapter_num in range(1, 7):
            chapter_key = f'chapter{chapter_num}'
            ai_chapter_key = f'chapter_{chapter_num}'  # AI might use underscores

            ai_chapter_data = ai_content.get(chapter_key) or ai_content.get(ai_chapter_key) or ai_content.get(str(chapter_num))

            if ai_chapter_data:
                structured[chapter_key] = {}

                # Map subsections
                expected_subsections = requirements.chapter_structure.get(chapter_num, [])
                if expected_subsections:
                    # Map AI content to expected subsections
                    ai_subsections = list(ai_chapter_data.keys())
                    for i, expected_type in enumerate(expected_subsections):
                        if i < len(ai_subsections):
                            ai_key = ai_subsections[i]
                            structured[chapter_key][expected_type] = ai_chapter_data[ai_key]
                        else:
                            # Generate placeholder if AI didn't provide enough content
                            structured[chapter_key][expected_type] = self._generate_subsection_placeholder(expected_type)
                else:
                    # Use AI content as-is if no expected structure
                    structured[chapter_key] = ai_chapter_data

        return structured

    def _generate_subsection_placeholder(self, subsection_type: str) -> str:
        """Generate placeholder content for missing subsections"""
        placeholders = {
            'latar_belakang': 'Latar belakang penelitian ini perlu dijelaskan lebih detail berdasarkan konteks penelitian.',
            'rumusan_masalah': 'Rumusan masalah penelitian perlu dirumuskan dengan jelas dan spesifik.',
            'tujuan_penelitian': 'Tujuan penelitian perlu dinyatakan secara spesifik dan terukur.',
            'manfaat_penelitian': 'Manfaat penelitian perlu dijelaskan bagi berbagai pihak yang berkepentingan.',
            'batasan_masalah': 'Batasan masalah perlu ditentukan untuk membatasi ruang lingkup penelitian.',
            'landasan_teori': 'Landasan teori perlu dijelaskan sebagai dasar pemikiran penelitian.',
            'penelitian_terkait': 'Penelitian terkait perlu dikaji untuk mengetahui perkembangan penelitian sebelumnya.',
            'kerangka_pikir': 'Kerangka pikir perlu digambarkan untuk menunjukkan hubungan antar konsep.',
            'metode_penelitian': 'Metode penelitian perlu dijelaskan secara detail dan sistematis.',
            'hasil_penelitian': 'Hasil penelitian perlu disajikan secara objektif dan komprehensif.',
            'pembahasan': 'Pembahasan hasil penelitian perlu dianalisis secara mendalam.',
            'kesimpulan': 'Kesimpulan penelitian perlu merangkum temuan utama secara jelas.',
            'saran': 'Saran untuk penelitian selanjutnya perlu diberikan berdasarkan temuan penelitian.'
        }
        return placeholders.get(subsection_type, f'Konten untuk {subsection_type} perlu dikembangkan.')

    def _assess_content_quality(self, content: Dict[str, Any], requirements: ContentRequirements) -> Dict[str, Any]:
        """Assess quality of generated content"""
        metrics = {
            'overall_score': 0.0,
            'chapter_completeness': 0.0,
            'subsection_coverage': 0.0,
            'content_length_score': 0.0,
            'academic_tone_score': 0.0
        }

        # Calculate scores
        total_chapters = len(requirements.chapter_structure)
        completed_chapters = len([c for c in content.keys() if content[c]])

        if total_chapters > 0:
            metrics['chapter_completeness'] = completed_chapters / total_chapters

        # Subsection coverage
        total_expected = sum(len(subs) for subs in requirements.chapter_structure.values())
        total_provided = sum(len(chapter) for chapter in content.values() if isinstance(chapter, dict))

        if total_expected > 0:
            metrics['subsection_coverage'] = min(total_provided / total_expected, 1.0)

        # Content length score
        total_words = sum(len(str(v).split()) for chapter in content.values()
                         for v in chapter.values() if isinstance(chapter, dict))
        expected_words = sum(requirements.length_requirements.values())
        expected_words = max(expected_words, 1000)  # Minimum expectation

        metrics['content_length_score'] = min(total_words / expected_words, 1.0)

        # Academic tone (simple check for academic keywords)
        academic_keywords = ['penelitian', 'metode', 'hasil', 'analisis', 'kesimpulan', 'teori', 'metodologi']
        all_text = ' '.join([str(v) for chapter in content.values()
                           for v in chapter.values() if isinstance(chapter, dict)])
        all_text_lower = all_text.lower()

        keyword_count = sum(1 for kw in academic_keywords if kw in all_text_lower)
        metrics['academic_tone_score'] = min(keyword_count / len(academic_keywords), 1.0)

        # Overall score (weighted average)
        weights = {
            'chapter_completeness': 0.3,
            'subsection_coverage': 0.3,
            'content_length_score': 0.2,
            'academic_tone_score': 0.2
        }

        metrics['overall_score'] = sum(metrics[key] * weights[key] for key in weights.keys())

        return metrics


class DynamicPromptBuilder:
    """Builds dynamic AI prompts based on template analysis"""

    def build_prompt(self, research_analysis: Dict[str, Any], requirements: ContentRequirements,
                    user_metadata: Dict[str, str], template_structure: TemplateStructure) -> str:
        """Build comprehensive AI prompt"""

        prompt_parts = []

        # Header with context
        prompt_parts.append(f"""
Anda adalah ahli penulisan tesis akademik Indonesia. Buat konten tesis berkualitas tinggi dalam bahasa Indonesia formal akademik.

INFORMASI PENELITIAN:
- Topik: {user_metadata.get('title', 'Tidak ditentukan')}
- Peneliti: {user_metadata.get('author', 'Tidak ditentukan')}
- Jenis penelitian: {research_analysis.get('type', 'umum')}
- Topik utama: {', '.join(research_analysis.get('topics', []))}
- Metodologi teridentifikasi: {', '.join(research_analysis.get('methodology', []))}
- Bagian yang sudah ditulis user: {', '.join(research_analysis.get('sections_identified', []))}

Karakteristik template:
- Universitas: {requirements.template_characteristics.get('university_style', 'umum')}
- Jumlah bab: {requirements.template_characteristics.get('chapter_count', 6)}
- Jumlah subbab: {requirements.template_characteristics.get('subsection_density', 0)}
""")

        # Chapter structure requirements
        prompt_parts.append("\nSTRUKTUR YANG DIPERLUKAN:")
        for chapter_num, subsections in requirements.chapter_structure.items():
            prompt_parts.append(f"\nBAB {chapter_num}:")
            for subsection in subsections:
                word_count = requirements.length_requirements.get(f'chapter{chapter_num}_{subsection}', 150)
                prompt_parts.append(f"  - {subsection}: {word_count} kata")

        # Content generation instructions
        prompt_parts.append("""
\nINSTRUKSI PENGGENERASIAN KONTEN:

1. Gunakan bahasa Indonesia formal akademik
2. Elaborasi poin user menjadi paragraf lengkap dan koheren
3. Pertahankan ide inti dan temuan user - JANGAN buat data palsu
4. Jika user belum menulis bagian tertentu, buat berdasarkan logika penelitian
5. Gunakan istilah akademik yang tepat untuk bidang penelitian
6. Sertakan sitasi dan referensi jika relevan
7. Pastikan alur logis antar bagian

FORMAT OUTPUT:
Kembalikan sebagai JSON dengan struktur:
{
  "chapter1": {
    "latar_belakang": "konten lengkap...",
    "rumusan_masalah": "konten lengkap...",
    // etc.
  },
  "chapter2": {
    "landasan_teori": "konten lengkap...",
    // etc.
  }
  // etc. untuk semua chapter
}

PENTING: Pastikan semua bagian memiliki konten substantif dan akademik!
""")

        return '\n'.join(prompt_parts)


class ResearchTypeDetector:
    """Detects research type and characteristics"""

    def detect_research_type(self, text: str) -> str:
        """Detect research methodology type"""
        text_lower = text.lower()

        if any(word in text_lower for word in ['survei', 'kuesioner', 'angket', 'survey']):
            return 'survey'
        elif any(word in text_lower for word in ['eksperimen', 'uji coba', 'experiment']):
            return 'experimental'
        elif any(word in text_lower for word in ['sistem', 'aplikasi', 'software', 'pengembangan']):
            return 'system_development'
        elif any(word in text_lower for word in ['studi kasus', 'case study']):
            return 'case_study'
        elif any(word in text_lower for word in ['literatur', 'meta-analisis', 'review']):
            return 'literature_review'
        else:
            return 'mixed_methods'


class ContentMapper:
    """Maps user content to template sections"""

    def map_user_content_to_template(self, user_text: str, template_requirements: ContentRequirements) -> Dict[str, str]:
        """Map user's written content to appropriate template sections"""

        mappings = {}
        user_sections = self._identify_user_sections(user_text)

        # Map identified sections to template
        for section_type, content in user_sections.items():
            # Find best matching template section
            best_match = self._find_best_template_match(section_type, template_requirements)
            if best_match:
                mappings[best_match] = content

        return mappings

    def _identify_user_sections(self, text: str) -> Dict[str, str]:
        """Identify sections user has written about"""
        sections = {}

        # Simple section identification based on keywords
        section_patterns = {
            'latar_belakang': r'(?i)(latar\s+belakang|background|pendahuluan)',
            'metodologi': r'(?i)(metode|metodologi|methodology)',
            'hasil': r'(?i)(hasil|result|finding|temuan)',
            'kesimpulan': r'(?i)(kesimpulan|conclusion)'
        }

        for section_type, pattern in section_patterns.items():
            match = re.search(pattern, text, re.DOTALL)
            if match:
                # Extract content after the section header
                start_pos = match.end()
                # Find next section or end of text
                next_matches = []
                for other_type, other_pattern in section_patterns.items():
                    if other_type != section_type:
                        other_match = re.search(other_pattern, text[start_pos:], re.IGNORECASE)
                        if other_match:
                            next_matches.append(other_match.start() + start_pos)

                end_pos = min(next_matches) if next_matches else len(text)
                sections[section_type] = text[start_pos:end_pos].strip()

        return sections

    def _find_best_template_match(self, user_section: str, requirements: ContentRequirements) -> Optional[str]:
        """Find best matching template section"""
        # Simple mapping - can be enhanced with semantic similarity
        mapping = {
            'latar_belakang': 'latar_belakang',
            'metodologi': 'metode_penelitian',
            'hasil': 'hasil_penelitian',
            'kesimpulan': 'kesimpulan'
        }

        return mapping.get(user_section)