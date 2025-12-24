"""
QA Explainer
Converts XML-level diffs into human-readable Indonesian explanations.
Severity grouping and reporting only - no formatting advice.
"""

import json
from typing import Dict, List, Any, Optional
from openai import OpenAI


class QAExplainer:
    """Generate QA explanations in Indonesian."""
    
    SEVERITY_LEVELS = ["critical", "warning", "info"]
    
    SYSTEM_PROMPT = """You are a QA expert for Indonesian academic thesis documents.

Your task: Convert technical XML differences into human-readable Indonesian explanations.

RULES:
1. Explain what changed, not how to fix it
2. Use simple Indonesian (Bahasa Indonesia)
3. Group by severity: critical, warning, info
4. Never suggest formatting changes
5. Focus on clarity for document authors

SEVERITY GUIDELINES:
- critical: Content lost, corruption, or major structure change
- warning: Minor content change, metadata difference
- info: Formatting preserved, style applied correctly

OUTPUT FORMAT:
{
  "summary": "Brief Indonesian summary of changes",
  "groups": {
    "critical": [
      {
        "location": "Paragraf ke-5 (BAB I)",
        "explanation": "Konten hilang...",
        "impact": "Isi dokumen berkurang"
      }
    ],
    "warning": [...],
    "info": [...]
  },
  "overall_assessment": "Dokumen valid / Dokumen bermasalah",
  "recommendations": ["Rekomendasi 1", ...]
}"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """Initialize with OpenRouter or custom endpoint."""
        self.client = OpenAI(
            base_url=base_url or "https://openrouter.ai/api/v1",
            api_key=api_key or "OPENROUTER_API_KEY",
        )
    
    def explain_diffs(self, diffs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Explain XML diffs in Indonesian."""
        if not diffs:
            return {
                "summary": "Tidak ada perubahan terdeteksi",
                "groups": {"critical": [], "warning": [], "info": []},
                "overall_assessment": "Dokumen valid",
                "recommendations": []
            }
        
        try:
            prompt = self._build_diff_prompt(diffs)
            
            response = self.client.chat.completions.create(
                model="openai/gpt-oss-20b:free",
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
                temperature=0.3,
                extra_body={"reasoning": {"enabled": True}}
            )
            
            content = response.choices[0].message.content
            result = self._extract_json(content)
            
            # Validate structure
            if "summary" not in result:
                result["summary"] = "Analisis selesai"
            if "groups" not in result:
                result["groups"] = {"critical": [], "warning": [], "info": []}
            if "overall_assessment" not in result:
                result["overall_assessment"] = "Dokumen valid"
            
            return result
            
        except Exception as e:
            return {
                "summary": f"Analisis QA gagal: {str(e)}",
                "groups": {"critical": [], "warning": [], "info": []},
                "overall_assessment": "Dokumen valid",
                "recommendations": ["Verifikasi manual diperlukan"]
            }
    
    def explain_content_changes(self, original: str, modified: str) -> Dict[str, Any]:
        """Explain content changes between versions."""
        try:
            prompt = f"""Jelaskan perbedaan antara dua versi teks ini dalam Bahasa Indonesia.
Fokus pada apa yang berubah, bukan cara memperbaikinya.

ORIGINAL:
{original[:500]}

MODIFIED:
{modified[:500]}

Berikan penjelasan singkat dalam format JSON."""
            
            response = self.client.chat.completions.create(
                model="openai/gpt-oss-20b:free",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                extra_body={"reasoning": {"enabled": True}}
            )
            
            content = response.choices[0].message.content
            return self._extract_json(content)
            
        except Exception as e:
            return {"explanation": f"Analisis gagal: {str(e)}"}
    
    @staticmethod
    def _build_diff_prompt(diffs: List[Dict[str, Any]]) -> str:
        """Build prompt from diffs."""
        lines = ["Analisis perubahan XML dokumen Word ini:\n"]
        
        for i, diff in enumerate(diffs, 1):
            lines.append(f"\nPerubahan {i}:")
            
            if "type" in diff:
                lines.append(f"  Tipe: {diff['type']}")
            
            if "element" in diff:
                lines.append(f"  Elemen: {diff['element']}")
            
            if "location" in diff:
                lines.append(f"  Lokasi: {diff['location']}")
            
            if "old_value" in diff:
                lines.append(f"  Sebelum: {str(diff['old_value'])[:100]}")
            
            if "new_value" in diff:
                lines.append(f"  Sesudah: {str(diff['new_value'])[:100]}")
        
        lines.append("\n\nBuat penjelasan dalam format JSON sesuai output yang diminta.")
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
            "summary": "Analisis selesai",
            "groups": {"critical": [], "warning": [], "info": []},
            "overall_assessment": "Tidak dapat dipastikan"
        }
