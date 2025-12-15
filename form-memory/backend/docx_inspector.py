import re
import random
import zipfile
from lxml import etree

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

def detect_style_usage(docx_path):
    """
    Heuristic to detect which styles are used for:
    - Heading 1 (BAB)
    - Body Text
    """
    from docx import Document
    doc = Document(docx_path)
    
    mapping = {
        "chapter_style": "Heading 1", # Default
        "body_style": "Normal"        # Default
    }
    
    from collections import Counter
    body_candidates = Counter()
    
    # Analyze first 500 paragraphs
    for p in doc.paragraphs[:500]:
        text = p.text.strip()
        if not text:
            continue
            
        # Detect Chapter Style (BAB...)
        if re.match(r"^BAB\s+[IVX]+", text, re.IGNORECASE) or re.match(r"^BAB\s+\d+", text, re.IGNORECASE):
            mapping["chapter_style"] = p.style.name
        
        # Detect Body Style candidates
        # Heuristic: Paragraph > 60 chars, not a heading, not all caps (likely title)
        if len(text) > 60 and not text.isupper():
            if "Heading" not in p.style.name and "JUDUL" not in p.style.name:
                body_candidates[p.style.name] += 1
    
    # Pick the most common body style
    if body_candidates:
        # Prefer non-Normal if it's common (e.g. if Isi Paragraf is used)
        most_common = body_candidates.most_common(1)[0][0]
        
        # Check if there's a specific custom style that is significant
        # If "Normal" is top but "Isi Paragraf" is close, might be mixed. 
        # But usually stick to most common.
        mapping["body_style"] = most_common
                
    return mapping


def extract_docx_styles(docx_path):
    styles = {}
    margins = {}

    with zipfile.ZipFile(docx_path) as docx:
        styles_xml = docx.read("word/styles.xml")
        document_xml = docx.read("word/document.xml")

    # ---------- STYLES ----------
    root = etree.XML(styles_xml)

    for style in root.findall(".//w:style", NS):
        style_id = style.get("{%s}styleId" % NS["w"])
        if not style_id:
            continue

        based_on = None
        based = style.find("w:basedOn", NS)
        if based is not None:
            based_on = based.get("{%s}val" % NS["w"])

        font = None
        size = None
        
        # Paragraph properties defaults
        line_spacing = None
        line_rule = None
        indent_first_line = None
        indent_left = None
        indent_right = None

        rpr = style.find("w:rPr", NS)
        if rpr is not None:
            sz = rpr.find("w:sz", NS)
            if sz is not None:
                size = int(sz.get("{%s}val" % NS["w"])) / 2

            rfonts = rpr.find("w:rFonts", NS)
            if rfonts is not None:
                font = rfonts.get("{%s}ascii" % NS["w"])
        
        ppr = style.find("w:pPr", NS)
        if ppr is not None:
            spacing = ppr.find("w:spacing", NS)
            if spacing is not None:
                line_spacing = spacing.get("{%s}line" % NS["w"])
                line_rule = spacing.get("{%s}lineRule" % NS["w"])
            
            ind = ppr.find("w:ind", NS)
            if ind is not None:
                indent_first_line = ind.get("{%s}firstLine" % NS["w"])
                indent_left = ind.get("{%s}left" % NS["w"])
                indent_right = ind.get("{%s}right" % NS["w"])

        styles[style_id] = {
            "font": font,
            "size": size,
            "based_on": based_on,
            "paragraph": {
                "line_spacing": line_spacing,
                "line_rule": line_rule,
                "indent_first_line": indent_first_line,
                "indent_left": indent_left,
                "indent_right": indent_right
            }
        }

    # ---------- MARGINS ----------
    doc_root = etree.XML(document_xml)
    sect = doc_root.find(".//w:sectPr", NS)

    if sect is not None:
        pg_mar = sect.find("w:pgMar", NS)
        if pg_mar is not None:
            margins = {
                "top": pg_mar.get("{%s}top" % NS["w"]),
                "bottom": pg_mar.get("{%s}bottom" % NS["w"]),
                "left": pg_mar.get("{%s}left" % NS["w"]),
                "right": pg_mar.get("{%s}right" % NS["w"]),
            }

    return {
        "styles": styles,
        "margins": margins
    }
