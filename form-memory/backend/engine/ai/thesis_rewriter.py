"""
AI-Powered Thesis Rewriter
Fully rewrites raw thesis content using AI for academic quality enhancement.
"""

from typing import Dict, List, Any, Optional
import json
from openai import OpenAI


class ThesisRewriter:
    """AI-powered thesis content rewriter for academic enhancement."""

    REWRITE_PROMPT = """You are an expert AI assistant specializing in Indonesian academic writing for computer science theses. Your task is to fully rewrite and enhance raw thesis content into polished, structured academic text.

Input: Raw text from draft.txt (containing chapters like BAB I-VI, lists, and basic content).

Requirements:
- Rewrite ALL content for academic quality: Improve grammar, clarity, flow, and depth. Add missing elements (e.g., if no abstract, generate one based on content).
- Structure output as valid JSON with these keys:
  - "title": Concise, academic thesis title (e.g., "Development of Web-Based Library Management System").
  - "abstract_id": Full Indonesian abstract (200-300 words, summarizing all chapters).
  - "chapters": Array of objects, each with "title" (e.g., "BAB I: PENDAHULUAN") and "content" (array of paragraphs/lists, fully rewritten).
  - "references": Array of formatted references (use APA style, expand if needed).
  - "appendices": Array of appendix items (e.g., ["Lampiran A: Code", "Lampiran B: Surveys"]).
  - "analysis_summary": 100-word executive summary of the thesis.
- Maintain Indonesian academic style: Formal language, 1.5 line spacing cues, first-line indentation hints.
- Enhance: Add transitions, examples, and depth where content is sparse (e.g., expand BAB IV with technical details).
- If input lacks sections, infer and generate (e.g., create conclusions if missing).

Output only valid JSON. No explanations.

Raw content to rewrite:
{raw_text}
"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """Initialize with OpenRouter."""
        self.client = OpenAI(
            base_url=base_url or "https://openrouter.ai/api/v1",
            api_key=api_key,
        )

    def rewrite_thesis(self, raw_text: str) -> Dict[str, Any]:
        """Rewrite raw thesis text using AI."""
        try:
            response = self.client.chat.completions.create(
                model="anthropic/claude-3-haiku",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert academic writer for Indonesian computer science theses."
                    },
                    {
                        "role": "user",
                        "content": self.REWRITE_PROMPT.format(raw_text=raw_text)
                    }
                ],
                temperature=0.3,
                max_tokens=8000
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("AI returned empty content")

            # Parse JSON
            result = json.loads(content)
            if not isinstance(result, dict):
                result = {
                    "error": "AI returned non-dict response",
                    "title": "Judul Skripsi Default",
                    "abstract_id": "Abstrak tidak dapat dihasilkan.",
                    "chapters": [],
                    "references": [],
                    "appendices": [],
                    "analysis_summary": "Ringkasan tidak tersedia."
                }
            return result
            
        except Exception as e:
            return {
                "error": str(e),
                "title": "Judul Skripsi Default",
                "abstract_id": "Abstrak tidak dapat dihasilkan.",
                "chapters": [],
                "references": [],
                "appendices": [],
                "analysis_summary": "Ringkasan tidak tersedia."
            }