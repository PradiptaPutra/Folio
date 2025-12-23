"""
Semantic Parser
Converts raw thesis text into clean semantic structure using AI.
Detects chapter, section, and element boundaries by meaning.
"""

import json
from typing import Dict, List, Any, Optional
from openai import OpenAI


class SemanticParser:
    """Parse raw text into semantic structure."""
    
    ELEMENT_TYPES = [
        "chapter",
        "subchapter",
        "subsubchapter",
        "paragraph",
        "list",
        "table_caption",
        "figure_caption",
        "equation",
        "bibliography_entry",
        "appendix"
    ]
    
    SYSTEM_PROMPT = """You are a semantic text parser for Indonesian academic thesis documents (Skripsi).

Your task: Convert raw, messy thesis text into a clean semantic structure.

RULES:
1. Preserve ALL original text verbatim - never edit or shorten
2. Detect structure by meaning, not typography
3. Identify chapter/section boundaries, paragraphs, lists, captions
4. Return JSON with confidence scores
5. Never infer formatting or styling

VALID ELEMENT TYPES:
- chapter: Major chapter heading (BAB I, etc)
- subchapter: Subsection (1.1, etc)
- subsubchapter: Sub-subsection (1.1.1, etc)
- paragraph: Body paragraph
- list: Bulleted or numbered list with items
- table_caption: Caption for table
- figure_caption: Caption for figure
- equation: Mathematical equation
- bibliography_entry: Bibliography/reference entry
- appendix: Appendix section

OUTPUT FORMAT:
{
  "elements": [
    {
      "type": "chapter|subchapter|...",
      "text": "exact original text",
      "confidence": 0.0-1.0,
      "metadata": {
        "detected_number": "I" or "1" or null,
        "detected_title": "string or null",
        "is_list": true/false,
        "list_items": ["item1", "item2"] or null
      }
    }
  ],
  "warnings": ["ambiguous text", ...],
  "overall_confidence": 0.0-1.0
}

CONFIDENCE GUIDELINES:
- 0.9-1.0: Clear chapter/section heading or obvious paragraph
- 0.7-0.9: Likely correct with minor ambiguity
- 0.5-0.7: Could be interpreted multiple ways
- < 0.5: Mark as unknown, include in warnings

Be conservative: if unsure, lower confidence and add warning."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """Initialize with OpenAI."""
        self.client = OpenAI(api_key=api_key)
    
    def parse(self, text: str) -> Dict[str, Any]:
        """Parse raw text into semantic structure."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": self.SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": f"Parse this thesis text:\n\n{text}"
                    }
                ],
                temperature=0.3,
            )
            
            content = response.choices[0].message.content
            
            # Extract JSON from response
            result = self._extract_json(content)
            return result
            
        except Exception as e:
            return {
                "error": str(e),
                "elements": [],
                "warnings": ["AI parsing failed"],
                "overall_confidence": 0.0
            }
    
    @staticmethod
    def _extract_json(text: str) -> Dict[str, Any]:
        """Extract JSON from AI response."""
        try:
            # Try direct JSON parse
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON block
            import re
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    pass
        
        return {
            "error": "Could not extract JSON from response",
            "elements": [],
            "warnings": ["JSON parsing failed"],
            "overall_confidence": 0.0
        }
