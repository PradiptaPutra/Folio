"""
Text Generation Helpers
Safe text generation for abstract and preface (plain text only).
Never called from executor - requires user consent.
"""

from typing import Optional, Dict, Any
from openai import OpenAI


class AbstractGenerator:
    """Generate abstract sections."""
    
    SYSTEM_PROMPT = """You are an academic writing assistant for Indonesian theses.

Your task: Generate abstract text in plain language (no formatting).

RULES:
1. Plain text only - no formatting marks
2. Indonesian language
3. Academic tone
4. Concise (100-150 words)
5. Summarize main contribution and findings"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """Initialize with OpenAI."""
        self.client = OpenAI(api_key=api_key)
    
    def generate_abstract_id(
        self,
        title: str,
        objectives: str,
        methods: str,
        results: str
    ) -> str:
        """Generate Indonesian abstract."""
        try:
            prompt = f"""Buat abstrak dalam Bahasa Indonesia untuk thesis:
Judul: {title}
Tujuan: {objectives}
Metode: {methods}
Hasil: {results}

Tulislah dalam 100-150 kata. Hanya teks biasa, tanpa format."""
            
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
                temperature=0.7,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"[Gagal membuat abstrak: {str(e)}]"
    
    def generate_abstract_en(
        self,
        title: str,
        objectives: str,
        methods: str,
        results: str
    ) -> str:
        """Generate English abstract."""
        try:
            prompt = f"""Create an abstract in English for a thesis:
Title: {title}
Objectives: {objectives}
Methods: {methods}
Results: {results}

Write in 100-150 words. Plain text only, no formatting."""
            
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
                temperature=0.7,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"[Failed to generate abstract: {str(e)}]"


class PrefaceGenerator:
    """Generate preface sections."""
    
    SYSTEM_PROMPT = """You are an academic writing assistant for Indonesian theses.

Your task: Generate preface (Kata Pengantar) text.

RULES:
1. Plain text only
2. Indonesian language
3. Formal academic tone
4. 200-300 words
5. Express gratitude, acknowledge contributions
6. No formatting marks"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """Initialize with OpenAI."""
        self.client = OpenAI(api_key=api_key)
    
    def generate_preface(
        self,
        title: str,
        author: str,
        institution: str,
        thesis_focus: str
    ) -> str:
        """Generate preface text."""
        try:
            prompt = f"""Buatlah Kata Pengantar untuk thesis:
Judul: {title}
Penulis: {author}
Institusi: {institution}
Fokus: {thesis_focus}

Tulislah 200-300 kata dalam Bahasa Indonesia, formal dan akademis.
Sertakan ucapan terima kasih dan pengakuan kontribusi.
Hanya teks biasa, tanpa format."""
            
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
                temperature=0.7,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"[Gagal membuat kata pengantar: {str(e)}]"
