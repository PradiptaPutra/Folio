"""
Intelligent Content Mapper
Maps content to template structure using AI-assisted matching and merging.
"""

from typing import Dict, List, Any, Tuple, Optional
import re
from .template_analyzer import TemplateAnalyzer
from .content_extractor import ContentExtractor


class ContentMapper:
    """Maps extracted content to template structure intelligently."""
    
    def __init__(self, template_analyzer: TemplateAnalyzer, content_extractor: ContentExtractor):
        """Initialize with template and content analysis."""
        self.template = template_analyzer
        self.content = content_extractor
        self.mapping = self._create_mapping()
    
    def _create_mapping(self) -> Dict[str, Any]:
        """Create intelligent mapping between content and template."""
        mapping = {
            "front_matter": self._map_front_matter(),
            "main_chapters": self._map_chapters(),
            "back_matter": self._map_back_matter(),
            "missing_sections": self._identify_missing_sections(),
            "placeholder_replacements": self._map_placeholders(),
        }
        return mapping
    
    def _map_front_matter(self) -> Dict[str, Any]:
        """Map front matter sections."""
        front_matter = {
            "cover": None,
            "approval": None,
            "statement": None,
            "dedication": None,
            "motto": None,
            "preface": None,
            "abstract_id": None,
            "abstract_en": None,
            "glossary": None,
            "toc": "AUTO_GENERATE",
            "list_figures": "AUTO_GENERATE",
            "list_tables": "AUTO_GENERATE",
        }
        
        # Try to find corresponding content sections
        sections = self.content.get_sections()
        
        section_patterns = {
            "preface": r"kata pengantar|preface",
            "abstract_id": r"abstrak|ringkasan|sari",
            "abstract_en": r"abstract|english summary",
            "glossary": r"glosarium|glossary|istilah",
        }
        
        for key, pattern in section_patterns.items():
            section = self.content.get_section_by_title(pattern)
            if section:
                front_matter[key] = {
                    "source": "content",
                    "section": section,
                    "action": "INSERT"
                }
            else:
                front_matter[key] = {
                    "action": "AUTO_GENERATE",
                    "type": key
                }
        
        return front_matter
    
    def _map_chapters(self) -> List[Dict[str, Any]]:
        """Map main content chapters."""
        chapters = []
        sections = self.content.get_sections()
        
        # Filter for main chapter-level sections
        chapter_pattern = r"^(BAB|CHAPTER|BAGIAN|PART)\s+([0-9]+|[IVX]+)"
        
        for section in sections:
            if isinstance(section, dict) and re.match(chapter_pattern, section["title"], re.IGNORECASE):
                chapters.append({
                    "title": section["title"],
                    "source": "content",
                    "sections": section.get("content", []),
                    "action": "INSERT_WITH_STYLE"
                })
        
        return chapters
    
    def _map_back_matter(self) -> Dict[str, Any]:
        """Map back matter sections."""
        back_matter = {
            "references": self.content.get_section_by_title(r"daftar pustaka|references|bibliography"),
            "appendices": [],
            "index": None,
        }
        
        # Find appendices
        appendix_sections = [s for s in self.content.get_sections() 
                            if re.search(r"lampiran|appendix|appendices", s["title"], re.IGNORECASE)]
        back_matter["appendices"] = appendix_sections
        
        return back_matter
    
    def _identify_missing_sections(self) -> Dict[str, List[str]]:
        """Identify sections required by template but missing from content."""
        template_front_matter = self.template.analysis["front_matter"]["sections"]
        content_sections = [s["title"].lower() for s in self.content.get_sections()]
        
        missing = {
            "critical": [],  # Must be added
            "recommended": [],  # Should be added
            "optional": [],  # Can be added
        }
        
        critical_sections = ["preface", "abstract"]
        recommended_sections = ["glossary", "list_tables", "list_figures"]
        
        for req_section in template_front_matter:
            if not any(req_section in cs for cs in content_sections):
                if any(crit in req_section for crit in critical_sections):
                    missing["critical"].append(req_section)
                elif any(rec in req_section for rec in recommended_sections):
                    missing["recommended"].append(req_section)
                else:
                    missing["optional"].append(req_section)
        
        return missing
    
    def _map_placeholders(self) -> Dict[str, str]:
        """Map template placeholders to content or metadata."""
        placeholders = {}
        template_placeholders = self.template.analysis["placeholders"]["text_placeholders"]
        
        for placeholder in template_placeholders:
            # Try to match with content metadata
            if any(word in placeholder.lower() for word in ["title", "judul"]):
                placeholders[placeholder] = "{TITLE}"
            elif any(word in placeholder.lower() for word in ["author", "nama", "penulis"]):
                placeholders[placeholder] = "{AUTHOR}"
            elif any(word in placeholder.lower() for word in ["date", "tanggal"]):
                placeholders[placeholder] = "{DATE}"
            elif any(word in placeholder.lower() for word in ["advisor", "dosen", "pembimbing"]):
                placeholders[placeholder] = "{ADVISOR}"
            else:
                placeholders[placeholder] = None  # Needs manual input
        
        return placeholders
    
    def get_mapping(self) -> Dict[str, Any]:
        """Return the complete mapping."""
        return self.mapping
    
    def get_action_plan(self) -> List[Dict[str, Any]]:
        """Generate an action plan for merging content into template."""
        plan = []
        
        # 1. Replace placeholders
        for placeholder, replacement in self.mapping["placeholder_replacements"].items():
            if replacement:
                plan.append({
                    "action": "REPLACE_PLACEHOLDER",
                    "placeholder": placeholder,
                    "replacement": replacement,
                    "priority": "HIGH"
                })
        
        # 2. Insert front matter
        for section, data in self.mapping["front_matter"].items():
            if isinstance(data, dict) and data.get("action") == "INSERT":
                plan.append({
                    "action": "INSERT_SECTION",
                    "section": section,
                    "source": "content",
                    "priority": "HIGH"
                })
            elif isinstance(data, dict) and data.get("action") == "AUTO_GENERATE":
                plan.append({
                    "action": "AUTO_GENERATE_SECTION",
                    "section": section,
                    "type": data.get("type"),
                    "priority": "MEDIUM"
                })
        
        # 3. Insert chapters
        for chapter in self.mapping["main_chapters"]:
            plan.append({
                "action": "INSERT_CHAPTER",
                "title": chapter["title"],
                "priority": "HIGH"
            })
        
        # 4. Insert back matter
        if self.mapping["back_matter"]["references"]:
            plan.append({
                "action": "INSERT_SECTION",
                "section": "references",
                "priority": "HIGH"
            })
        
        for appendix in self.mapping["back_matter"]["appendices"]:
            if isinstance(appendix, dict):
                plan.append({
                    "action": "INSERT_APPENDIX",
                    "title": appendix.get("title", "Untitled Appendix"),
                    "priority": "MEDIUM"
                })
        
        # 5. Add missing critical sections
        for section in self.mapping["missing_sections"]["critical"]:
            plan.append({
                "action": "ADD_MISSING_SECTION",
                "section": section,
                "priority": "HIGH",
                "warning": f"This section was required by template but missing in content"
            })
        
        return plan
    
    def get_summary(self) -> str:
        """Return a summary of the mapping."""
        mapping = self.mapping
        
        summary = f"""
CONTENT MAPPING SUMMARY
=======================

Main Chapters Found: {len(mapping['main_chapters'])}
- {', '.join(ch['title'][:30] + '...' if len(ch['title']) > 30 else ch['title'] for ch in mapping['main_chapters'][:5])}

Front Matter Sections:
- Preface: {'Found' if mapping['front_matter']['preface'] else 'Missing (will auto-generate)'}
- Abstract (ID): {'Found' if mapping['front_matter']['abstract_id'] else 'Missing (will auto-generate)'}
- Abstract (EN): {'Found' if mapping['front_matter']['abstract_en'] else 'Missing (will auto-generate)'}

Back Matter:
- References: {'Found' if mapping['back_matter']['references'] else 'Not found'}
- Appendices: {len(mapping['back_matter']['appendices'])}

Missing Critical Sections: {len(mapping['missing_sections']['critical'])}
- {', '.join(mapping['missing_sections']['critical']) or 'None'}

Action Plan Items: {len(self.get_action_plan())}
"""
        return summary.strip()
