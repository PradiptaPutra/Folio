"""
Normalized Extractor
Converts DOCX/TXT into a normalized JSON structure using mammoth/pypandoc.
If optional libraries (simplify_docx/docxbox) are available, uses them;
otherwise falls back to heuristic HTML parsing.
"""

from __future__ import annotations

from typing import Dict, Any, List, Optional
from pathlib import Path

import re

try:
    import mammoth  # type: ignore
except Exception:
    mammoth = None  # type: ignore

try:
    import pypandoc  # type: ignore
except Exception:
    pypandoc = None  # type: ignore


def _html_to_normalized(html: str) -> Dict[str, Any]:
    """Convert simple HTML into a normalized structure.

    The result contains keys: front_matter, chapters, appendices, bibliography.
    Headings (h1/h2/h3), paragraphs (p), lists (ol/ul) are mapped deterministically.
    """
    from bs4 import BeautifulSoup  # type: ignore

    soup = BeautifulSoup(html, "html.parser")
    normalized: Dict[str, Any] = {
        "front_matter": [],
        "chapters": [],
        "appendices": [],
        "bibliography": None,
    }

    current_chapter: Optional[Dict[str, Any]] = None
    current_section: Optional[Dict[str, Any]] = None

    def _ensure_sections(chapter: Dict[str, Any]) -> None:
        if "sections" not in chapter:
            chapter["sections"] = []

    # Walk through top-level nodes
    for el in soup.find_all(["h1", "h2", "h3", "p", "ul", "ol"]):
        name = el.name
        text = (el.get_text() or "").strip()
        if not text:
            continue

        if name == "h1":
            # Start new chapter
            # Try to detect BAB numbering like "BAB I" or "BAB 1"
            detected_number = None
            m = re.match(r"^BAB\s+([IVX]+|\d+)", text, re.IGNORECASE)
            if m:
                detected_number = m.group(1)

            current_chapter = {
                "type": "chapter",
                "number": detected_number,
                "title": text,
                "content": [],
                "sections": [],
            }
            normalized["chapters"].append(current_chapter)
            current_section = None

        elif name == "h2":
            if current_chapter is None:
                current_chapter = {
                    "type": "chapter",
                    "number": None,
                    "title": text,
                    "content": [],
                    "sections": [],
                }
                normalized["chapters"].append(current_chapter)
            current_section = {
                "type": "subchapter",
                "title": text,
                "content": [],
                "lists": [],
            }
            _ensure_sections(current_chapter)
            current_chapter["sections"].append(current_section)

        elif name == "h3":
            if current_section is None:
                if current_chapter is None:
                    current_chapter = {
                        "type": "chapter",
                        "number": None,
                        "title": "",
                        "content": [],
                        "sections": [],
                    }
                    normalized["chapters"].append(current_chapter)
                current_section = {
                    "type": "subchapter",
                    "title": "",
                    "content": [],
                    "lists": [],
                }
                _ensure_sections(current_chapter)
                current_chapter["sections"].append(current_section)

            # Represent h3 as subsection item
            if "subsections" not in current_section:
                current_section["subsections"] = []
            current_section["subsections"].append({
                "type": "subsubchapter",
                "title": text,
                "content": [],
            })

        elif name == "p":
            if current_section is not None:
                current_section.setdefault("content", []).append(text)
            elif current_chapter is not None:
                current_chapter.setdefault("content", []).append(text)
            else:
                normalized["front_matter"].append(text)

        elif name in ("ul", "ol"):
            items = []
            for li in el.find_all("li"):
                li_text = (li.get_text() or "").strip()
                if li_text:
                    items.append(li_text)
            list_obj = {
                "type": "list",
                "ordered": (name == "ol"),
                "items": items,
            }
            if current_section is not None:
                current_section.setdefault("lists", []).append(list_obj)
            elif current_chapter is not None:
                current_chapter.setdefault("lists", []).append(list_obj)
            else:
                normalized["front_matter"].append(list_obj)

    return normalized


def extract_normalized_structure(content_path: str) -> Dict[str, Any]:
    """Extract normalized structure from a DOCX/TXT using available tools.

    Returns a JSON-ready dict with chapters/sections/lists/etc.
    """
    path = Path(content_path)
    if path.suffix.lower() == ".docx" and mammoth is not None:
        try:
            with open(path, "rb") as f:
                result = mammoth.convert_to_html(f)
                html = result.value or ""
            return _html_to_normalized(html)
        except Exception:
            pass

    # Try pypandoc to markdown → HTML
    if pypandoc is not None:
        try:
            # Convert to HTML directly (handles docx/txt/markdown)
            html = pypandoc.convert_file(str(path), "html")
            return _html_to_normalized(html)
        except Exception:
            pass

    # Fallback: simple text parsing
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        text = ""

    # Convert text to simple HTML where headings can be detected by patterns
    lines = text.splitlines()
    html_parts: List[str] = []
    for line in lines:
        if re.match(r"^BAB\s+([IVX]+|\d+)", line, re.IGNORECASE):
            html_parts.append(f"<h1>{line}</h1>")
        elif re.match(r"^\d+\.\d+\s+", line):
            html_parts.append(f"<h2>{line}</h2>")
        elif re.match(r"^\d+\.\d+\.\d+\s+", line):
            html_parts.append(f"<h3>{line}</h3>")
        else:
            html_parts.append(f"<p>{line}</p>")
    html = "\n".join(html_parts)
    return _html_to_normalized(html)
