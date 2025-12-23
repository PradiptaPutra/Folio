"""
Structural Parser
Converts semantic structure into executor-ready format.
No AI - deterministic mapping only.
"""

from typing import Dict, List, Any, Optional


class StructuralParser:
    """Convert semantic structure into executor input."""
    
    def parse_semantic_structure(
        self,
        semantic_elements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Convert semantic elements into structural document."""
        structural_doc = {
            "front_matter": [],
            "chapters": [],
            "appendices": [],
            "bibliography": None
        }
        
        current_chapter = None
        current_section = None
        
        for element in semantic_elements:
            elem_type = element.get("type", "paragraph")
            text = element.get("text", "")
            
            if elem_type == "chapter":
                current_chapter = {
                    "type": "chapter",
                    "number": element.get("metadata", {}).get("detected_number"),
                    "title": element.get("metadata", {}).get("detected_title"),
                    "content": [text] if text else []
                }
                structural_doc["chapters"].append(current_chapter)
                current_section = None
            
            elif elem_type == "subchapter":
                if current_chapter is None:
                    current_chapter = {
                        "type": "chapter",
                        "number": None,
                        "title": "Pendahuluan",
                        "content": [],
                        "sections": []
                    }
                    structural_doc["chapters"].append(current_chapter)
                
                current_section = {
                    "type": "subchapter",
                    "title": element.get("metadata", {}).get("detected_title"),
                    "content": [text] if text else []
                }
                if "sections" not in current_chapter:
                    current_chapter["sections"] = []
                current_chapter["sections"].append(current_section)
            
            elif elem_type == "subsubchapter":
                if current_section is None:
                    if current_chapter:
                        current_section = {
                            "type": "subchapter",
                            "title": "Subseksi",
                            "content": [],
                            "subsections": []
                        }
                        if "sections" not in current_chapter:
                            current_chapter["sections"] = []
                        current_chapter["sections"].append(current_section)
                
                if current_section:
                    subsection = {
                        "type": "subsubchapter",
                        "title": element.get("metadata", {}).get("detected_title"),
                        "content": [text] if text else []
                    }
                    if "subsections" not in current_section:
                        current_section["subsections"] = []
                    current_section["subsections"].append(subsection)
            
            elif elem_type == "paragraph":
                if current_section:
                    current_section["content"].append(text)
                elif current_chapter:
                    current_chapter["content"].append(text)
                else:
                    structural_doc["front_matter"].append(text)
            
            elif elem_type == "list":
                list_obj = {
                    "type": "list",
                    "items": element.get("metadata", {}).get("list_items", [])
                }
                if current_section:
                    if "lists" not in current_section:
                        current_section["lists"] = []
                    current_section["lists"].append(list_obj)
                elif current_chapter:
                    if "lists" not in current_chapter:
                        current_chapter["lists"] = []
                    current_chapter["lists"].append(list_obj)
            
            elif elem_type == "table_caption":
                caption_obj = {"type": "table_caption", "text": text}
                if current_chapter:
                    if "captions" not in current_chapter:
                        current_chapter["captions"] = []
                    current_chapter["captions"].append(caption_obj)
            
            elif elem_type == "figure_caption":
                caption_obj = {"type": "figure_caption", "text": text}
                if current_chapter:
                    if "captions" not in current_chapter:
                        current_chapter["captions"] = []
                    current_chapter["captions"].append(caption_obj)
            
            elif elem_type == "appendix":
                structural_doc["appendices"].append({
                    "type": "appendix",
                    "title": element.get("metadata", {}).get("detected_title"),
                    "content": [text] if text else []
                })
            
            elif elem_type == "bibliography_entry":
                if structural_doc["bibliography"] is None:
                    structural_doc["bibliography"] = []
                structural_doc["bibliography"].append(text)
        
        return structural_doc
    
    def extract_metadata(
        self,
        semantic_structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract metadata from semantic structure."""
        metadata = {
            "chapter_count": len(semantic_structure.get("chapters", [])),
            "has_front_matter": len(semantic_structure.get("front_matter", [])) > 0,
            "has_appendices": len(semantic_structure.get("appendices", [])) > 0,
            "has_bibliography": semantic_structure.get("bibliography") is not None,
        }
        
        # Count sections
        total_sections = 0
        for chapter in semantic_structure.get("chapters", []):
            total_sections += len(chapter.get("sections", []))
        metadata["section_count"] = total_sections
        
        return metadata
