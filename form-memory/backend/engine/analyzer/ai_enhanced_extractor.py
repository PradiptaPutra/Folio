"""
AI-Enhanced Content Extractor
Combines rule-based extraction with AI semantic analysis for better chapter detection.
"""

from typing import Dict, List, Any, Tuple, Optional
import re
from pathlib import Path
from docx import Document
from .content_extractor import ContentExtractor
from enum import Enum

# Try to import AI semantic parser
try:
    from engine.ai.semantic_parser import SemanticParser
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


class SectionType(str, Enum):
    """Document section types identified by AI."""
    CHAPTER = "chapter"
    SECTION = "section"
    SUBSECTION = "subsection"
    PARAGRAPH = "paragraph"
    INTRODUCTION = "introduction"
    METHODOLOGY = "methodology"
    RESULTS = "results"
    DISCUSSION = "discussion"
    CONCLUSION = "conclusion"
    LITERATURE_REVIEW = "literature_review"
    BACKGROUND = "background"
    UNKNOWN = "unknown"


class AIEnhancedContentExtractor:
    """Extracts content using AI semantic analysis when available."""
    
    def __init__(self, content_path: str, use_ai: bool = True, api_key: Optional[str] = None):
        """Initialize with content file.

        Args:
            content_path: Path to DOCX or TXT file
            use_ai: Whether to use AI semantic analysis (if available)
            api_key: OpenRouter API key for AI features
        """
        self.content_path = Path(content_path)
        self.is_docx = self.content_path.suffix.lower() == '.docx'
        self.use_ai = use_ai and AI_AVAILABLE and api_key is not None
        self.semantic_parser = SemanticParser(api_key=api_key) if self.use_ai else None
        
        # Load content - keep ContentExtractor object separately
        self._content_extractor = ContentExtractor(str(self.content_path))
        loaded_content = self._content_extractor._load_content()
        self.raw_text = self._extract_raw_text()
        self.sections = self._extract_sections()
    
    def _load_content(self) -> Dict[str, Any]:
        """Load content from file."""
        if self.is_docx:
            return self._extract_from_docx()
        else:
            return self._extract_from_text()
    
    def _extract_from_docx(self) -> Dict[str, Any]:
        """Extract content from DOCX file."""
        doc = Document(self.content_path)
        
        return {
            "sections": [],  # Will be populated by _extract_sections()
            "raw_text": self._get_docx_text(doc),
            "tables": self._extract_tables_from_docx(doc),
            "metadata": {
                "title": doc.core_properties.title or "",
                "author": doc.core_properties.author or "",
            }
        }
    
    def _extract_from_text(self) -> Dict[str, Any]:
        """Extract content from TXT file."""
        with open(self.content_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        return {
            "sections": [],  # Will be populated by _extract_sections()
            "raw_text": text,
            "tables": [],
            "metadata": {}
        }
    
    def _extract_raw_text(self) -> str:
        """Get all text content."""
        if self.is_docx:
            doc = Document(self.content_path)
            return self._get_docx_text(doc)
        else:
            with open(self.content_path, 'r', encoding='utf-8') as f:
                return f.read()
    
    def _extract_sections(self) -> List[Dict[str, Any]]:
        """Extract sections using AI if available, fallback to rules."""
        if self.use_ai:
            try:
                return self._extract_with_ai()
            except Exception as e:
                print(f"[WARNING] AI extraction failed: {str(e)}. Falling back to rule-based extraction.")
                return self._extract_with_rules()
        else:
            return self._extract_with_rules()
    
    def _extract_with_ai(self) -> List[Dict[str, Any]]:
        """Extract sections using AI semantic analysis."""
        if not self.raw_text.strip():
            return []
        
        # Use semantic parser to analyze text
        result = self.semantic_parser.parse(self.raw_text)
        
        if not result or "elements" not in result:
            return self._extract_with_rules()
        
        # Convert semantic elements to sections
        sections = []
        current_section = None
        current_level = 0
        
        for element in result.get("elements", []):
            elem_type = element.get("type", "paragraph")
            text = element.get("text", "").strip()
            confidence = element.get("confidence", 0.0)
            
            # Determine section type and level
            if elem_type in ["chapter", "subchapter", "subsubchapter"]:
                # Save previous section
                if current_section:
                    sections.append(current_section)
                
                # Create new section
                level_map = {
                    "chapter": 0,
                    "subchapter": 1,
                    "subsubchapter": 2
                }
                level = level_map.get(elem_type, 0)
                
                current_section = {
                    "title": text,
                    "level": level,
                    "content": [],
                    "type": elem_type,
                    "ai_confidence": confidence,
                    "ai_analyzed": True,
                }
                current_level = level
            
            elif elem_type == "paragraph" and current_section is not None:
                # Add to current section
                if text:
                    current_section["content"].append(text)
        
        # Don't forget last section
        if current_section:
            sections.append(current_section)
        
        # Classify sections semantically
        for section in sections:
            section["semantic_type"] = self._classify_section_semantic(
                section["title"],
                section.get("ai_confidence", 0.0)
            )
        
        return sections if sections else self._extract_with_rules()
    
    def _extract_with_rules(self) -> List[Dict[str, Any]]:
        """Extract sections using rule-based patterns (fallback)."""
        sections = []
        
        # Patterns for headings
        heading_patterns = [
            (r"^BAB\s+([IVX]+|[0-9]+)\s*[\s\n:]*(.+?)$", "chapter"),
            (r"^([0-9]+\.[0-9]+)\s+(.+?)$", "section"),
            (r"^([0-9]+\.[0-9]+\.[0-9]+)\s+(.+?)$", "subsection"),
            (r"^#+ (.+?)$", "markdown"),
            (r"^(PENDAHULUAN|INTRODUCTION|LATAR BELAKANG|BACKGROUND).*?$", "introduction"),
            (r"^(METODOLOGI|METHODOLOGY|METODE|METHOD).*?$", "methodology"),
            (r"^(HASIL|RESULTS?|FINDINGS?).*?$", "results"),
            (r"^(PEMBAHASAN|DISCUSSION|ANALISIS|ANALYSIS).*?$", "discussion"),
            (r"^(KESIMPULAN|CONCLUSION|PENUTUP).*?$", "conclusion"),
        ]
        
        lines = self.raw_text.split('\n')
        current_section = None
        
        for line in lines:
            matched = False
            for pattern, heading_type in heading_patterns:
                match = re.match(pattern, line.strip(), re.IGNORECASE)
                if match:
                    # Save previous section
                    if current_section:
                        sections.append(current_section)
                    
                    # Extract title
                    if len(match.groups()) >= 2:
                        title = match.group(2).strip()
                    else:
                        title = match.group(1).strip() if match.groups() else line.strip()
                    
                    # Start new section
                    current_section = {
                        "title": title,
                        "level": 0 if heading_type in ["chapter", "introduction", "methodology", "results", "discussion", "conclusion"] else 1,
                        "content": [],
                        "type": heading_type,
                        "ai_analyzed": False,
                        "ai_confidence": 1.0,  # Rule-based has high confidence
                        "semantic_type": heading_type,
                    }
                    matched = True
                    break
            
            if not matched and current_section is not None:
                if line.strip():
                    current_section["content"].append(line)
        
        if current_section:
            sections.append(current_section)
        
        return sections
    
    def _classify_section_semantic(self, title: str, confidence: float) -> str:
        """Classify section by semantic meaning."""
        title_lower = title.lower()
        
        # Semantic classification patterns
        patterns = {
            "introduction": r"(pendahuluan|introduction|latar belakang|background|rumusan masalah)",
            "methodology": r"(metodologi|methodology|metode|method|prosedur|procedure)",
            "results": r"(hasil|results?|temuan|findings?|penemuan)",
            "discussion": r"(pembahasan|discussion|analisis|analysis|penafsiran|interpretation)",
            "conclusion": r"(kesimpulan|conclusion|penutup|closing|saran|recommendation)",
            "literature_review": r"(tinjauan pustaka|literature review|kajian|review)",
            "background": r"(latar belakang|background|konteks|context)",
        }
        
        for semantic_type, pattern in patterns.items():
            if re.search(pattern, title_lower):
                return semantic_type
        
        return "unknown"
    
    def _get_docx_text(self, doc) -> str:
        """Get all text from DOCX."""
        return '\n'.join(para.text for para in doc.paragraphs)
    
    def _extract_tables_from_docx(self, doc) -> List[Dict[str, Any]]:
        """Extract tables from DOCX."""
        tables = []
        
        for i, table in enumerate(doc.tables):
            table_data = {
                "index": i,
                "rows": len(table.rows),
                "cols": len(table.columns),
                "content": []
            }
            
            for row in table.rows:
                row_data = [cell.text for cell in row.cells]
                table_data["content"].append(row_data)
            
            tables.append(table_data)
        
        return tables
    
    def get_sections(self) -> List[Dict[str, Any]]:
        """Get extracted sections."""
        return self._content_extractor.get_sections()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get extraction summary."""
        ai_analyzed = sum(1 for s in self.sections if isinstance(s, dict) and s.get("ai_analyzed", False))
        rule_based = len(self.sections) - ai_analyzed
        
        semantic_types = []
        for s in self.sections:
            if isinstance(s, dict):
                semantic_types.append(s.get("semantic_type", "unknown"))
        
        avg_conf = 0.0
        if self.sections:
            confidences = [s.get("ai_confidence", 1.0) for s in self.sections if isinstance(s, dict)]
            avg_conf = sum(confidences) / max(len(confidences), 1) if confidences else 0.0
        
        return {
            "total_sections": len(self.sections),
            "ai_analyzed_sections": ai_analyzed,
            "rule_based_sections": rule_based,
            "ai_available": self.use_ai,
            "content_type": "docx" if self.is_docx else "text",
            "semantic_types": list(set(semantic_types)),
            "average_confidence": avg_conf,
        }
    
    def get_semantic_validation(self) -> Dict[str, Any]:
        """Get semantic validation of document structure."""
        validation = {
            "status": "valid",
            "issues": [],
            "warnings": [],
            "suggestions": []
        }
        
        # Check for typical thesis structure
        semantic_types = []
        for s in self.sections:
            if isinstance(s, dict):
                semantic_types.append(s.get("semantic_type", "unknown"))
        
        # Check for missing critical sections
        expected_sections = ["introduction", "methodology", "results", "conclusion"]
        missing = [sec for sec in expected_sections if sec not in semantic_types]
        
        if missing:
            validation["warnings"].append(f"Missing expected sections: {', '.join(missing)}")
        
        # Check for low confidence sections
        low_confidence = [s for s in self.sections if isinstance(s, dict) and s.get("ai_confidence", 1.0) < 0.6]
        if low_confidence:
            validation["warnings"].append(f"{len(low_confidence)} section(s) have low AI confidence")
        
        # Check structure hierarchy
        if self.sections:
            levels = [s.get("level", 0) for s in self.sections if isinstance(s, dict)]
            if levels and max(levels) - min(levels) > 3:
                validation["suggestions"].append("Consider organizing sections with more consistent hierarchy")
        
        return validation
