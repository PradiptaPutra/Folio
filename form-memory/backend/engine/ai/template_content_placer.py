"""
AI-powered template content placement assistant.
Uses AI to intelligently determine where content should be placed in different templates.
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
import json


class TemplateContentPlacer:
    """
    AI-powered assistant that helps determine optimal content placement
    for different thesis templates.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with API key for AI assistance."""
        self.api_key = api_key
        self.ai_available = api_key is not None
    
    def analyze_template_structure_for_placement(self, template_path: str, template_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use AI to analyze template structure and suggest content placement zones.
        
        Args:
            template_path: Path to template file
            template_analysis: Basic template analysis results
            
        Returns:
            Dictionary with placement recommendations
        """
        if not self.ai_available:
            return self._fallback_placement_analysis(template_analysis)
        
        print("[AI] Analyzing template structure for intelligent content placement...")
        
        try:
            # Prepare context for AI
            context = self._prepare_placement_context(template_path, template_analysis)
            
            # Call AI for placement analysis
            placement_analysis = self._ai_analyze_placement(context)
            
            return placement_analysis
            
        except Exception as e:
            print(f"[WARNING] AI placement analysis failed: {e}, using fallback")
            return self._fallback_placement_analysis(template_analysis)
    
    def _prepare_placement_context(self, template_path: str, template_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for AI analysis."""
        # Extract key information from template
        chapters = template_analysis.get('chapters', [])
        subsections = template_analysis.get('subsections', [])
        placeholders = template_analysis.get('placeholders', [])
        
        context = {
            'template_path': template_path,
            'chapters_detected': len(chapters),
            'subsections_detected': len(subsections),
            'placeholders_detected': len(placeholders),
            'chapter_structure': [
                {
                    'number': ch.get('chapter_num'),
                    'title': ch.get('title', ''),
                    'location': ch.get('location', 0)
                }
                for ch in chapters[:10]
            ],
            'subsection_patterns': [
                {
                    'text': sub.get('text', '')[:50],
                    'chapter': sub.get('chapter_num', 0),
                    'location': sub.get('location', 0)
                }
                for sub in subsections[:20]
            ],
            'placeholder_types': [
                {
                    'text': ph.get('text', '')[:50],
                    'type': ph.get('pattern_type', 'unknown'),
                    'location': ph.get('location', 0)
                }
                for ph in placeholders[:15]
            ]
        }
        
        return context
    
    def _ai_analyze_placement(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use AI to analyze and suggest content placement.
        
        Args:
            context: Prepared context for analysis
            
        Returns:
            Placement recommendations
        """
        try:
            from openai import OpenAI
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key
            )
            
            prompt = f"""You are an expert in Indonesian academic thesis template analysis. Analyze this template structure and provide intelligent content placement recommendations.

TEMPLATE STRUCTURE:
- Chapters detected: {context['chapters_detected']}
- Subsections detected: {context['subsections_detected']}
- Placeholders detected: {context['placeholders_detected']}

CHAPTER STRUCTURE:
{json.dumps(context['chapter_structure'], indent=2)}

SUBSECTION PATTERNS:
{json.dumps(context['subsection_patterns'], indent=2)}

PLACEHOLDER TYPES:
{json.dumps(context['placeholder_types'], indent=2)}

ANALYSIS REQUIRED:
1. Identify content placement zones for each chapter
2. Map standard thesis sections (Latar Belakang, Rumusan Masalah, etc.) to template locations
3. Suggest optimal insertion points for content
4. Identify any template-specific requirements or patterns
5. Provide confidence scores for each placement recommendation

OUTPUT FORMAT (JSON):
{{
    "placement_zones": [
        {{
            "chapter_num": 1,
            "section_key": "latar_belakang",
            "recommended_location": "paragraph_index",
            "confidence": 0.0-1.0,
            "strategy": "direct_replacement|insert_after|create_new"
        }}
    ],
    "template_characteristics": {{
        "chapter_numbering_style": "roman|numeric|semantic",
        "subsection_numbering_style": "numbered|explicit|mixed",
        "content_style_name": "Isi Paragraf|Normal|Body Text",
        "requires_ai_assistance": true/false
    }},
    "recommendations": [
        "specific recommendations for this template"
    ]
}}"""
            
            response = client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert in Indonesian academic thesis formatting and template analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            result_text = response.choices[0].message.content
            
            # Parse JSON response
            try:
                # Extract JSON from response (might have markdown code blocks)
                if '```json' in result_text:
                    json_start = result_text.find('```json') + 7
                    json_end = result_text.find('```', json_start)
                    result_text = result_text[json_start:json_end].strip()
                elif '```' in result_text:
                    json_start = result_text.find('```') + 3
                    json_end = result_text.find('```', json_start)
                    result_text = result_text[json_start:json_end].strip()
                
                placement_analysis = json.loads(result_text)
                print("[AI] Successfully received placement recommendations from AI")
                return placement_analysis
                
            except json.JSONDecodeError as e:
                print(f"[WARNING] Failed to parse AI response as JSON: {e}")
                print(f"[DEBUG] AI response: {result_text[:500]}")
                return self._fallback_placement_analysis({})
                
        except Exception as e:
            print(f"[ERROR] AI placement analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return self._fallback_placement_analysis({})
    
    def _fallback_placement_analysis(self, template_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback placement analysis without AI."""
        return {
            'placement_zones': [],
            'template_characteristics': {
                'chapter_numbering_style': 'unknown',
                'subsection_numbering_style': 'unknown',
                'content_style_name': 'Normal',
                'requires_ai_assistance': False
            },
            'recommendations': [
                'Using fallback placement strategy',
                'AI assistance not available'
            ]
        }
    
    def suggest_content_placement(self, chapter_num: int, section_key: str, 
                                  template_structure: Dict[str, Any]) -> Dict[str, Any]:
        """
        Suggest where to place specific content in a template.
        
        Args:
            chapter_num: Chapter number
            section_key: Section key (e.g., 'latar_belakang')
            template_structure: Template structure analysis
            
        Returns:
            Placement suggestion with location and strategy
        """
        # Standard mapping
        section_mapping = {
            'latar_belakang': {'order': 1, 'keywords': ['latar belakang', 'background']},
            'rumusan_masalah': {'order': 2, 'keywords': ['rumusan masalah', 'problem statement']},
            'tujuan_penelitian': {'order': 3, 'keywords': ['tujuan', 'objectives']},
            'manfaat_penelitian': {'order': 4, 'keywords': ['manfaat', 'benefits']},
            'batasan_masalah': {'order': 5, 'keywords': ['batasan', 'scope', 'ruang lingkup']},
        }
        
        section_info = section_mapping.get(section_key, {'order': 0, 'keywords': []})
        
        # Find matching placeholders or subsections
        suggestions = {
            'chapter_num': chapter_num,
            'section_key': section_key,
            'recommended_order': section_info['order'],
            'strategy': 'sequential',  # default
            'confidence': 0.5
        }
        
        # Try to find matching placeholder or subsection
        subsections = template_structure.get('subsections', [])
        placeholders = template_structure.get('placeholders', [])
        
        for sub in subsections:
            if sub.get('chapter_num') == chapter_num:
                sub_text = sub.get('text', '').lower()
                if any(kw in sub_text for kw in section_info['keywords']):
                    suggestions['location'] = sub.get('location')
                    suggestions['strategy'] = 'direct_replacement'
                    suggestions['confidence'] = 0.8
                    break
        
        return suggestions

