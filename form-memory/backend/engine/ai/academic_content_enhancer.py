"""
AI-Powered Academic Content Enhancer
Provides comprehensive academic writing assistance for Indonesian theses,
including content improvement, language enhancement, and academic standards compliance.
"""

from typing import Dict, List, Any, Optional, Tuple
import re
from pathlib import Path
from engine.ai.text_generation import AbstractGenerator, PrefaceGenerator
from engine.ai.semantic_parser import SemanticParser
from engine.ai.qa_explainer import QAExplainer

# Try to import AI semantic parser
try:
    from engine.ai.semantic_parser import SemanticParser
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


class AcademicContentEnhancer:
    """AI-powered content enhancement for academic writing."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize with OpenRouter API key."""
        self.api_key = api_key
        self.ai_available = AI_AVAILABLE and api_key is not None

        # Initialize AI components
        if self.ai_available and api_key:
            self.abstract_generator = AbstractGenerator(api_key=api_key)
            self.preface_generator = PrefaceGenerator(api_key=api_key)
            self.semantic_parser = SemanticParser(api_key=api_key)
            self.qa_explainer = QAExplainer(api_key=api_key)
        else:
            self.abstract_generator = None
            self.preface_generator = None
            self.semantic_parser = None
            self.qa_explainer = None

        # Indonesian academic writing standards
        self.academic_standards = {
            "language": {
                "formal_tone": True,
                "academic_vocabulary": True,
                "passive_voice_preference": True,
                "avoid_contractions": True,
                "avoid_colloquialisms": True
            },
            "structure": {
                "clear_topic_sentences": True,
                "logical_progression": True,
                "proper_citations": True,
                "consistent_terminology": True
            },
            "content": {
                "original_contribution": True,
                "evidence_based": True,
                "critical_analysis": True,
                "theoretical_grounding": True
            }
        }

    def enhance_content(self, content: str, content_type: str = "body",
                       field_of_study: str = "general") -> Dict[str, Any]:
        """
        Comprehensively enhance academic content with AI-powered improvements.

        Args:
            content: Raw content text
            content_type: Type of content (body, abstract, preface, etc.)
            field_of_study: Academic field for context

        Returns:
            Dictionary with enhanced content and improvement details
        """
        if not self.ai_available:
            return {
                "enhanced_content": content,
                "improvements": [],
                "quality_score": 0.0,
                "warning": "AI enhancement not available - API key required"
            }

        result = {
            "original_content": content,
            "enhanced_content": content,
            "improvements": [],
            "quality_score": 0.0,
            "issues_found": [],
            "recommendations": []
        }

        try:
            # Step 1: Content quality assessment
            quality_analysis = self._assess_content_quality(content, content_type, field_of_study)
            result["quality_score"] = quality_analysis["score"]
            result["issues_found"] = quality_analysis["issues"]

            # Step 2: AI-powered language enhancement
            language_enhanced = self._enhance_language_ai(content, content_type, field_of_study)
            result["enhanced_content"] = language_enhanced["text"]
            result["improvements"].extend(language_enhanced["improvements"])

            # Step 3: AI-powered structure optimization
            structure_optimized = self._optimize_structure_ai(result["enhanced_content"], content_type)
            result["enhanced_content"] = structure_optimized["text"]
            result["improvements"].extend(structure_optimized["improvements"])

            # Step 4: Academic standards compliance
            standards_compliant = self._ensure_academic_standards(result["enhanced_content"], field_of_study)
            result["enhanced_content"] = standards_compliant["text"]
            result["improvements"].extend(standards_compliant["improvements"])

            # Step 5: Generate recommendations
            result["recommendations"] = self._generate_improvement_recommendations(result)

        except Exception as e:
            result["warning"] = f"Content enhancement failed: {str(e)}"
            result["enhanced_content"] = content  # Fallback to original

        return result

    def _enhance_language_ai(self, content: str, content_type: str, field_of_study: str) -> Dict[str, Any]:
        """Enhance language quality using advanced AI with detailed prompts."""
        enhanced = {
            "text": content,
            "improvements": []
        }

        if not self.ai_available:
            return enhanced

        try:
            # Comprehensive AI-powered language enhancement
            enhancement_prompt = f"""You are an expert academic writing assistant specializing in Indonesian thesis content. Your task is to enhance the provided text to meet the highest academic standards for Indonesian universities.

CONTENT TYPE: {content_type.upper()}
FIELD OF STUDY: {field_of_study}
LANGUAGE: Indonesian (Formal Academic)

ORIGINAL TEXT:
{content}

ENHANCEMENT REQUIREMENTS:

1. **ACADEMIC TONE & FORMALITY**
   - Use formal Indonesian academic language (Baku)
   - Avoid colloquial expressions, slang, or informal terms
   - Maintain objective, scholarly voice
   - Use passive voice appropriately for scientific writing

2. **LANGUAGE QUALITY**
   - Correct grammatical errors and improve sentence structure
   - Enhance vocabulary with appropriate academic terms
   - Improve clarity and precision of expression
   - Ensure logical flow between sentences
   - Remove redundancy and unnecessary repetition

3. **CONTENT-TYPE SPECIFIC REQUIREMENTS**

   For ABSTRACT content:
   - Structure: Background → Purpose → Methods → Results → Conclusion
   - Length: 150-250 words
   - Use present tense for general facts, past tense for specific findings
   - Include key quantitative results

   For PREFACE content:
   - Express gratitude formally
   - Explain motivation and significance
   - Maintain humble yet confident tone
   - Length: 200-400 words

   For CHAPTER BODY content:
   - Use clear topic sentences for each paragraph
   - Ensure logical progression of ideas
   - Include proper citations where needed
   - Maintain consistent terminology

4. **INDONESIAN ACADEMIC STANDARDS**
   - Use proper Indonesian academic terminology
   - Follow Indonesian thesis formatting conventions
   - Ensure cultural appropriateness for Indonesian academic context
   - Maintain respect for academic traditions

5. **PRESERVATION RULES**
   - Keep all factual information and data intact
   - Preserve technical terms and proper nouns
   - Maintain the original meaning and intent
   - Do not add information not present in original text
   - Preserve any required formatting or structure

ENHANCED TEXT (return only the improved text, no explanations):"""

            # Call OpenRouter API using OpenAI client format for better reliability
            try:
                from openai import OpenAI

                client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=self.api_key,
                )

                response = client.chat.completions.create(
                    model="anthropic/claude-3-haiku",
                    messages=[{"role": "user", "content": enhancement_prompt}],
                    max_tokens=4000,
                    temperature=0.3,  # Lower temperature for consistent academic writing
                    extra_body={"reasoning": {"enabled": True}}  # Enable reasoning for better quality
                )

                enhanced_text = response.choices[0].message.content.strip()

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
                        "model": "anthropic/claude-3-haiku",
                        "messages": [{"role": "user", "content": enhancement_prompt}],
                        "max_tokens": 4000,
                        "temperature": 0.3
                    },
                    timeout=30
                )

                if response.status_code == 200:
                    result = response.json()
                    enhanced_text = result["choices"][0]["message"]["content"].strip()
                else:
                    raise Exception(f"API request failed with status {response.status_code}")

            # Validate enhancement quality
            if len(enhanced_text) > len(content) * 0.5:  # Ensure meaningful enhancement
                enhanced["text"] = enhanced_text
                enhanced["improvements"].extend([
                    "Academic tone enhanced with formal Indonesian",
                    "Language clarity and precision improved",
                    "Grammar and sentence structure optimized",
                    f"Content length: {len(enhanced_text)} characters"
                ])
            else:
                # Fallback if AI response is too short
                enhanced["text"] = content
                enhanced["improvements"].append("AI enhancement returned insufficient content, using original")

        except Exception as e:
            enhanced["text"] = content
            enhanced["improvements"].append(f"Language enhancement failed: {str(e)}")

        return enhanced

    def _optimize_structure_ai(self, content: str, content_type: str) -> Dict[str, Any]:
        """Optimize content structure using AI analysis with detailed prompts."""
        optimized = {
            "text": content,
            "improvements": []
        }

        if not self.ai_available:
            return optimized

        try:
            structure_prompt = f"""You are a structural analysis expert for Indonesian academic theses. Analyze and optimize the structure of the provided content to meet university standards.

CONTENT TYPE: {content_type.upper()}
CONTENT TO ANALYZE:
{content}

STRUCTURAL REQUIREMENTS BY CONTENT TYPE:

**ABSTRACT Structure:**
1. Background/Latar Belakang (1-2 paragraphs)
2. Research Purpose/Tujuan Penelitian (1 paragraph)
3. Research Methods/Metode Penelitian (1 paragraph)
4. Main Results/Hasil Utama (1-2 paragraphs)
5. Conclusions/Kesimpulan (1 paragraph)

**PREFACE Structure:**
1. Opening gratitude/Pembuka dengan ucapan syukur (1 paragraph)
2. Research motivation/Motivasi Penelitian (1-2 paragraphs)
3. Acknowledgments/Ucapan Terima Kasih (2-3 paragraphs)
4. Closing/Penutup (1 paragraph)

**CHAPTER BODY Structure:**
1. Introduction/Pendahuluan Bab (if needed)
2. Main content/Isi Utama dengan sub-bab yang jelas
3. Supporting evidence/Data Pendukung
4. Analysis/Analisis (jika diperlukan)
5. Summary/Ringkasan (jika diperlukan)

**GENERAL ACADEMIC STRUCTURE RULES:**
- Each paragraph must have a clear topic sentence
- Logical progression from general to specific concepts
- Clear transitions between paragraphs using appropriate conjunctions
- Appropriate use of headings and subheadings in Indonesian academic style
- Consistent formatting and academic style throughout

**INDONESIAN THESIS SPECIFIC REQUIREMENTS:**
- Use proper Indonesian academic section numbering
- Follow Indonesian academic writing conventions
- Ensure proper paragraph transitions in Indonesian
- Maintain formal academic tone throughout
- Include appropriate academic discourse markers

TASK: Analyze the current structure and provide an optimized version that follows Indonesian thesis formatting standards. Restructure the content to have proper academic organization, clear paragraph transitions, and appropriate section breaks. Return only the restructured content with improved organization.

OPTIMIZED CONTENT:"""

            # Call AI for structure optimization
            import requests

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "openai/gpt-oss-120b:free",
                    "messages": [{"role": "user", "content": structure_prompt}],
                    "max_tokens": 4000,
                    "temperature": 0.2  # Very low temperature for structural consistency
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                optimized_text = result["choices"][0]["message"]["content"].strip()

                if len(optimized_text) > len(content) * 0.7:  # Ensure meaningful optimization
                    optimized["text"] = optimized_text
                    optimized["improvements"].extend([
                        f"Structure optimized for {content_type} format",
                        "Logical flow improved with proper transitions",
                        "Academic organization enhanced per Indonesian standards"
                    ])
                else:
                    optimized["text"] = content
                    optimized["improvements"].append("Structure optimization returned insufficient content")
            else:
                optimized["text"] = content
                optimized["improvements"].append(f"Structure optimization API call failed (status {response.status_code})")

        except Exception as e:
            optimized["text"] = content
            optimized["improvements"].append(f"Structure optimization failed: {str(e)}")

        return optimized

    # Keep existing methods for compatibility
    def _assess_content_quality(self, content: str, content_type: str,
                               field_of_study: str) -> Dict[str, Any]:
        """Assess academic content quality."""
        assessment = {
            "score": 0.0,
            "issues": [],
            "strengths": []
        }

        # Length appropriateness
        word_count = len(content.split())
        if content_type == "abstract":
            if 150 <= word_count <= 250:
                assessment["score"] += 0.2
                assessment["strengths"].append("Appropriate length for abstract")
            else:
                assessment["issues"].append(f"Abstract length {word_count} words - should be 150-250 words")
        elif content_type == "preface":
            if 200 <= word_count <= 400:
                assessment["score"] += 0.2
                assessment["strengths"].append("Appropriate length for preface")
            else:
                assessment["issues"].append(f"Preface length {word_count} words - should be 200-400 words")

        # Academic tone detection
        formal_indicators = ["penelitian", "analisis", "metode", "hasil", "kesimpulan"]
        informal_indicators = ["gue", "lu", "banget", "keren", "gampang"]

        formal_count = sum(1 for word in formal_indicators if word.lower() in content.lower())
        informal_count = sum(1 for word in informal_indicators if word.lower() in content.lower())

        if formal_count > informal_count:
            assessment["score"] += 0.2
            assessment["strengths"].append("Appropriate academic tone")
        elif informal_count > 0:
            assessment["issues"].append("Contains informal language - needs academic tone")

        # Structure analysis
        if self._has_logical_structure(content, content_type):
            assessment["score"] += 0.2
            assessment["strengths"].append("Good logical structure")

        # Language quality
        if self._has_academic_language(content):
            assessment["score"] += 0.2
            assessment["strengths"].append("Uses academic vocabulary")
        else:
            assessment["issues"].append("Limited academic vocabulary")

        # Field-specific terms
        field_terms = self._get_field_specific_terms(field_of_study)
        field_term_count = sum(1 for term in field_terms if term.lower() in content.lower())

        if field_term_count > 0:
            assessment["score"] += 0.2
            assessment["strengths"].append(f"Includes {field_term_count} field-specific terms")

        return assessment

    def _has_logical_structure(self, content: str, content_type: str) -> bool:
        """Check if content has logical structure."""
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

        if len(paragraphs) < 2:
            return False

        # Check for topic sentences (first sentence of each paragraph)
        topic_sentences = 0
        for para in paragraphs:
            sentences = para.split('.')
            if sentences and len(sentences[0].split()) > 3:  # At least 4 words
                topic_sentences += 1

        return topic_sentences >= len(paragraphs) * 0.6  # 60% have topic sentences

    def _has_academic_language(self, content: str) -> bool:
        """Check for academic language usage."""
        academic_indicators = [
            "penelitian", "analisis", "metode", "teori", "hipotesis",
            "data", "hasil", "kesimpulan", "rekomendasi", "literatur",
            "pendekatan", "kerangka", "model", "sistem", "proses"
        ]

        words = content.lower().split()
        academic_word_count = sum(1 for word in words if word in academic_indicators)

        return academic_word_count >= len(words) * 0.02  # At least 2% academic words

    def _get_field_specific_terms(self, field: str) -> List[str]:
        """Get field-specific academic terms."""
        field_terms = {
            "computer_science": ["algoritma", "database", "sistem", "aplikasi", "pengguna", "interface"],
            "information_systems": ["sistem informasi", "database", "jejaring", "keamanan", "manajemen"],
            "engineering": ["desain", "prototipe", "uji coba", "implementasi", "optimasi"],
            "business": ["strategi", "manajemen", "organisasi", "proses bisnis", "efisiensi"],
            "general": ["penelitian", "analisis", "metode", "hasil", "kesimpulan"]
        }

        return field_terms.get(field.lower(), field_terms["general"])

    def _enhance_language(self, content: str, content_type: str,
                         field_of_study: str) -> Dict[str, Any]:
        """Legacy language enhancement method - now delegates to AI version."""
        return self._enhance_language_ai(content, content_type, field_of_study)

    def _optimize_structure(self, content: str, content_type: str) -> Dict[str, Any]:
        """Legacy structure optimization method - now delegates to AI version."""
        return self._optimize_structure_ai(content, content_type)

    def _ensure_academic_standards(self, content: str, field_of_study: str) -> Dict[str, Any]:
        """Ensure content meets academic standards."""
        compliant = {
            "text": content,
            "improvements": []
        }

        # Check for academic standards compliance
        issues = []

        # Check for passive voice usage (Indonesian style)
        passive_indicators = ["dilakukan", "diterapkan", "dikembangkan", "dianalisis"]
        passive_count = sum(1 for indicator in passive_indicators if indicator in content.lower())

        if passive_count < len(content.split()) * 0.01:  # Less than 1% passive
            issues.append("Limited use of passive voice - consider more objective writing")

        # Check for citations (placeholder for now)
        if "menurut" not in content.lower() and "berdasarkan" not in content.lower():
            issues.append("Limited references to literature or sources")

        # Apply basic improvements
        if issues:
            compliant["improvements"].append("Academic standards compliance checked")
            compliant["improvements"].append(f"Identified {len(issues)} areas for improvement")
        else:
            compliant["improvements"].append("Content meets basic academic standards")

        return compliant

    def _generate_improvement_recommendations(self, result: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations based on analysis."""
        recommendations = []

        quality_score = result.get("quality_score", 0.0)
        issues = result.get("issues_found", [])

        if quality_score < 0.6:
            recommendations.append("Overall quality needs significant improvement - consider professional editing")
        elif quality_score < 0.8:
            recommendations.append("Good foundation but needs refinement for academic standards")

        if any("length" in issue.lower() for issue in issues):
            recommendations.append("Adjust content length to meet academic requirements")

        if any("tone" in issue.lower() or "language" in issue.lower() for issue in issues):
            recommendations.append("Enhance formal academic tone and eliminate colloquial expressions")

        if any("structure" in issue.lower() for issue in issues):
            recommendations.append("Improve logical structure and paragraph organization")

        if not recommendations:
            recommendations.append("Content quality is good - focus on final polishing and proofreading")

        quality_score = result.get("quality_score", 0.0)
        issues = result.get("issues_found", [])

        if quality_score < 0.6:
            recommendations.append("Overall quality needs significant improvement - consider professional editing")
        elif quality_score < 0.8:
            recommendations.append("Good foundation but needs refinement for academic standards")

        if any("length" in issue.lower() for issue in issues):
            recommendations.append("Adjust content length to meet academic requirements")

        if any("tone" in issue.lower() or "language" in issue.lower() for issue in issues):
            recommendations.append("Enhance formal academic tone and eliminate colloquial expressions")

        if any("structure" in issue.lower() for issue in issues):
            recommendations.append("Improve logical structure and paragraph organization")

        if not recommendations:
            recommendations.append("Content quality is good - focus on final polishing and proofreading")

        return recommendations
