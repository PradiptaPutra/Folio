from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import re





def insert_toc(docx_path):
    """
    Complete TOC insertion workflow:
    1. Insert Word-native TOC field
    2. Add page break after TOC
    """
    # Note: Heading styles are handled by skripsi_formatter.py
    
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
    # Generate TOC for levels 1-3 (BAB, Subbab, Anak Subbab)
    fld.set(qn("w:instr"), 'TOC \\o "1-3" \\h \\z \\u')
    
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
