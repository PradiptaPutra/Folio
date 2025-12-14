from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import re


def detect_heading_level(paragraph):
    """
    Detect heading level based on:
    1. Paragraph text patterns (BAB, UPPERCASE sections)
    2. Paragraph style (if already marked)
    
    Returns: 1, 2, 3 for levels, or None if not a heading
    """
    text = paragraph.text.strip()
    
    # Pattern 1: BAB (Chapter) headings
    if text.startswith("BAB "):
        return 1
    
    # Pattern 2: ALL CAPS sections (subsections)
    if text and text.isupper() and len(text) < 80 and len(text) > 3:
        return 2
    
    # Pattern 3: Check existing style names from Pandoc
    style_name = paragraph.style.name if paragraph.style else ""
    if "Heading" in style_name:
        # Extract level from style name (e.g., "Heading1", "Heading 1", "heading1")
        match = re.search(r'[Hh]eading\s*(\d)', style_name)
        if match:
            level = int(match.group(1))
            return level if level <= 3 else None
    
    return None


def fix_heading_styles(docx_path):
    """
    Fix heading styles in the DOCX:
    1. Detect headings based on text patterns and existing styles
    2. Apply Word built-in styles: Heading 1, Heading 2, Heading 3
    3. Set outline levels (w:outlineLvl)
    """
    doc = Document(docx_path)
    
    # Map outline levels to style names
    level_to_style = {
        1: "Heading 1",
        2: "Heading 2",
        3: "Heading 3"
    }
    
    for paragraph in doc.paragraphs:
        level = detect_heading_level(paragraph)
        
        if level:
            # Apply the Word built-in style
            style_name = level_to_style[level]
            paragraph.style = style_name
            
            # Set outline level via XML (w:outlineLvl)
            pPr = paragraph._element.get_or_add_pPr()
            outlineLvl = pPr.find(qn('w:outlineLvl'))
            
            if outlineLvl is None:
                outlineLvl = OxmlElement('w:outlineLvl')
                pPr.append(outlineLvl)
            
            # Outline level is 0-indexed (0 = Heading 1, 1 = Heading 2, etc.)
            outlineLvl.set(qn('w:val'), str(level - 1))
    
    doc.save(docx_path)


def insert_toc(docx_path):
    """
    Complete TOC insertion workflow:
    1. Fix heading styles and outline levels
    2. Insert Word-native TOC field
    3. Add page break after TOC
    """
    # Step 1: Fix heading styles first
    fix_heading_styles(docx_path)
    
    # Step 2: Load document again and insert TOC
    doc = Document(docx_path)

    # Get the first paragraph element
    if len(doc.paragraphs) > 0:
        first_p = doc.paragraphs[0]._element
    else:
        # If no paragraphs, create one
        first_p = doc.add_paragraph()._element

    # Create TOC paragraph with proper structure
    toc_p = OxmlElement("w:p")
    
    # Add paragraph properties for better formatting
    pPr = OxmlElement("w:pPr")
    pStyle = OxmlElement("w:pStyle")
    pStyle.set(qn("w:val"), "TOC")  # Use TOC style if available
    pPr.append(pStyle)
    toc_p.append(pPr)

    # Create the TOC field
    fld = OxmlElement("w:fldSimple")
    # Requirement: TOC must list only BAB (Heading 1)
    fld.set(qn("w:instr"), 'TOC \\o "1-1" \\h \\z \\u')
    
    # Add a run with placeholder text
    run = OxmlElement("w:r")
    t = OxmlElement("w:t")
    t.text = "[Table of Contents - Update in Word with F9]"
    run.append(t)
    
    # Insert field with run
    toc_p.append(fld)
    toc_p.append(run)
    
    # Insert at the beginning of document
    if first_p.getparent() is not None:
        first_p.addprevious(toc_p)
    else:
        doc._element.insert(0, toc_p)

    # Add page break after TOC
    pb = OxmlElement("w:p")
    pPr_pb = OxmlElement("w:pPr")
    pageBreakPr = OxmlElement("w:pageBreakBefore")
    pageBreakPr.set(qn("w:val"), "1")
    pPr_pb.append(pageBreakPr)
    pb.append(pPr_pb)
    
    run_pb = OxmlElement("w:r")
    br = OxmlElement("w:br")
    br.set(qn("w:type"), "page")
    run_pb.append(br)
    pb.append(run_pb)
    
    toc_p.addnext(pb)

    doc.save(docx_path)
