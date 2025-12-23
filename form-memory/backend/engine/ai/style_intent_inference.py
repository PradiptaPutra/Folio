"""
Style Intent Inference
Assists in understanding template style intent when Word styles are messy.
ASSISTIVE ONLY - executor must not blindly trust output.
"""

import json
from typing import Dict, Any, Optional, List
from openai import OpenAI


class StyleIntentInference:
    """Infer semantic intent of Word styles."""
    
    VALID_ROLES = [
        "chapter_title",
        "subchapter_title",
        "body_paragraph",
        "caption",
        "bibliography",
        "front_matter_heading",
        "unknown"
    ]
    
    SYSTEM_PROMPT = """You are a Word style analyzer for academic thesis documents.

Your task: Infer the semantic intent of Word styles based on limited information.

VALID SEMANTIC ROLES:
- chapter_title: Main chapter heading (BAB I, etc)
- subchapter_title: Subchapter/section heading
- body_paragraph: Main body text
- caption: Figure/table caption
- bibliography: Bibliography/reference text
- front_matter_heading: Front matter section heading
- unknown: Cannot determine

INPUT DATA:
- style_name: The Word style name
- example_text: Sample text using this style
- outline_level: Outline level (0-9, or null)
- usage_frequency: How often used (high/medium/low)

ANALYSIS RULES:
1. Consider outline level first (lower = more likely chapter heading)
2. Analyze example text for content patterns
3. Use style name as weak signal only
4. Conservative confidence: if unsure < 0.7, mark unknown
5. NEVER suggest formatting changes

OUTPUT FORMAT:
{
  "semantic_role": "chapter_title|subchapter_title|...",
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation",
  "recommendations": []
}

CONFIDENCE GUIDELINES:
- 0.9-1.0: Clear from outline level or text pattern
- 0.7-0.9: Likely correct
- < 0.7: Mark as unknown - do not use"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """Initialize with OpenAI."""
        self.client = OpenAI(api_key=api_key)
    
    def infer(self, style_data: Dict[str, Any]) -> Dict[str, Any]:
        """Infer semantic role from style data."""
        try:
            prompt = self._build_prompt(style_data)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": self.SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
            )
            
            content = response.choices[0].message.content
            result = self._extract_json(content)
            
            # Validate confidence
            if result.get("confidence", 0) < 0.7:
                result["semantic_role"] = "unknown"
            
            return result
            
        except Exception as e:
            return {
                "semantic_role": "unknown",
                "confidence": 0.0,
                "reasoning": f"Inference failed: {str(e)}",
                "recommendations": []
            }
    
    def infer_batch(self, styles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Infer intent for multiple styles."""
        return [self.infer(style) for style in styles]
    
    @staticmethod
    def _build_prompt(style_data: Dict[str, Any]) -> str:
        """Build analysis prompt from style data."""
        lines = ["Analyze this Word style:"]
        
        if "style_name" in style_data:
            lines.append(f"Style Name: {style_data['style_name']}")
        
        if "example_text" in style_data:
            text = style_data["example_text"]
            text = text[:200] + "..." if len(text) > 200 else text
            lines.append(f"Example Text: {text}")
        
        if "outline_level" in style_data:
            level = style_data["outline_level"]
            lines.append(f"Outline Level: {level}")
        
        if "usage_frequency" in style_data:
            lines.append(f"Usage Frequency: {style_data['usage_frequency']}")
        
        if "font_size" in style_data:
            lines.append(f"Font Size: {style_data['font_size']}")
        
        if "is_bold" in style_data:
            lines.append(f"Bold: {style_data['is_bold']}")
        
        if "is_numbered" in style_data:
            lines.append(f"Numbered: {style_data['is_numbered']}")
        
        lines.append("\nWhat is the semantic role of this style?")
        return "\n".join(lines)
    
    @staticmethod
    def _extract_json(text: str) -> Dict[str, Any]:
        """Extract JSON from AI response."""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            import re
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    pass
        
        return {
            "semantic_role": "unknown",
            "confidence": 0.0,
            "reasoning": "Could not parse response",
            "recommendations": []
        }
