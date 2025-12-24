"""
Front Matter Classifier
Classifies front matter blocks by intent using AI.
"""

import json
from typing import Dict, List, Any, Optional
from openai import OpenAI


class FrontMatterClassifier:
    """Classify front matter blocks."""
    
    VALID_CATEGORIES = [
        "title_page",
        "approval_page",
        "originality_statement",
        "dedication",
        "motto",
        "preface",
        "abstract_id",
        "abstract_en",
        "glossary",
        "table_of_contents",
        "list_of_tables",
        "list_of_figures",
        "unknown"
    ]
    
    SYSTEM_PROMPT = """You are a front matter classifier for Indonesian academic thesis documents.

Your task: Classify front matter blocks by their semantic intent.

VALID CATEGORIES:
- title_page: Halaman Judul (title page)
- approval_page: Lembar Pengesahan (approval/signature page)
- originality_statement: Pernyataan Keaslian (authenticity declaration)
- dedication: Persembahan (dedication)
- motto: Motto
- preface: Kata Pengantar (preface)
- abstract_id: Abstrak (Indonesian abstract)
- abstract_en: Abstract (English abstract)
- glossary: Daftar Istilah (glossary/terms)
- table_of_contents: Daftar Isi (TOC)
- list_of_tables: Daftar Tabel (table list)
- list_of_figures: Daftar Gambar (figure list)
- unknown: Cannot determine

RULES:
1. Analyze content and context only
2. Never modify text
3. Return confidence score (0.0-1.0)
4. If multiple categories match, choose most likely
5. Mark uncertain classifications as unknown

OUTPUT FORMAT:
{
  "classifications": [
    {
      "category": "title_page|approval_page|...",
      "confidence": 0.0-1.0,
      "reason": "brief explanation"
    }
  ]
}"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """Initialize with OpenRouter."""
        self.client = OpenAI(
            base_url=base_url or "https://openrouter.ai/api/v1",
            api_key=api_key,
        )
    
    def classify(self, blocks: List[str]) -> List[Dict[str, Any]]:
        """Classify list of front matter blocks."""
        if not blocks:
            return []
        
        try:
            # Combine blocks with markers for AI to analyze
            marked_blocks = "\n---\n".join(
                f"BLOCK {i}:\n{block}" for i, block in enumerate(blocks)
            )
            
            response = self.client.chat.completions.create(
                model="openai/gpt-oss-20b:free",
                messages=[
                    {
                        "role": "system",
                        "content": self.SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": marked_blocks
                    }
                ],
                temperature=0.2,
                extra_body={"reasoning": {"enabled": True}}
            )
            
            content = response.choices[0].message.content
            result = self._extract_json(content)
            
            # Ensure we have classifications for all blocks
            if "classifications" in result:
                classifications = result["classifications"]
                if len(classifications) < len(blocks):
                    for i in range(len(blocks) - len(classifications)):
                        classifications.append({
                            "category": "unknown",
                            "confidence": 0.0,
                            "reason": "Not classified by AI"
                        })
                return classifications
            
            return [{"category": "unknown", "confidence": 0.0, "reason": "No classifications returned"}]
            
        except Exception as e:
            return [
                {
                    "category": "unknown",
                    "confidence": 0.0,
                    "reason": f"Classification failed: {str(e)}"
                }
                for _ in blocks
            ]
    
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
        
        return {"classifications": []}
