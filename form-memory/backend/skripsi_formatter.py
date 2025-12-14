"""
Skripsi Formatter - Enforce Indonesian University Thesis Formatting Standards

Implements:
1. Paragraph spacing & indent (1.5 line spacing, 1.25 cm first-line indent)
2. Word-native auto numbering for BAB & Subbab
3. Margin enforcement via reference.docx
"""

from docx import Document
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import re


class SkripsiFormatter:
    """Enforces Indonesian thesis formatting standards."""
    
    # Constants (in cm)
    MARGIN_TOP = 4.0
    MARGIN_BOTTOM = 3.0
    MARGIN_LEFT = 4.0
    MARGIN_RIGHT = 3.0
    
    # Paragraph formatting (in cm and line spacing)
    LINE_SPACING = 1.5
    FIRST_LINE_INDENT = 1.25  # cm
    PARAGRAPH_SPACE_BEFORE = 0  # pt
    PARAGRAPH_SPACE_AFTER = 0  # pt
    
    @staticmethod
    def cm_to_twips(cm):
        """Convert cm to twips (1 cm = 566.93 twips)."""
        return int(cm * 566.93)
    
    @staticmethod
    def detect_heading_level(paragraph):
        """
        Detect heading level:
        - BAB pattern → Level 1
        - ALL CAPS section → Level 2
        - Existing heading styles → Preserve level
        """
        text = paragraph.text.strip()
        
        if text.startswith("BAB "):
            return 1
        
        if text and text.isupper() and 3 < len(text) < 80:
            return 2
        
        style_name = paragraph.style.name if paragraph.style else ""
        match = re.search(r'[Hh]eading\s*(\d)', style_name)
        if match:
            level = int(match.group(1))
            return level if 1 <= level <= 3 else None
        
        return None
    
    @staticmethod
    def extract_bab_number(text):
        """Extract BAB number from text like 'BAB 1 PENDAHULUAN'."""
        match = re.match(r'BAB\s+(\d+)\s*(.*)', text.strip(), re.IGNORECASE)
        if match:
            return int(match.group(1)), match.group(2).strip()
        return None, None
    
    @staticmethod
    def format_paragraph(paragraph):
        """
        Format paragraph with skripsi standards:
        - Line spacing: 1.5
        - First-line indent: 1.25 cm
        - Space before/after: 0 pt
        - Alignment: Justify
        """
        pPr = paragraph._element.get_or_add_pPr()
        
        # Set line spacing (1.5)
        spacing = pPr.find(qn('w:spacing'))
        if spacing is None:
            spacing = OxmlElement('w:spacing')
            pPr.append(spacing)
        
        # Line spacing 1.5 = 360 (in twentieths of a point)
        spacing.set(qn('w:line'), '360')
        spacing.set(qn('w:lineRule'), 'auto')
        spacing.set(qn('w:before'), str(SkripsiFormatter.PARAGRAPH_SPACE_BEFORE))
        spacing.set(qn('w:after'), str(SkripsiFormatter.PARAGRAPH_SPACE_AFTER))
        
        # Set first-line indent (1.25 cm = 708 twips)
        ind = pPr.find(qn('w:ind'))
        if ind is None:
            ind = OxmlElement('w:ind')
            pPr.append(ind)
        
        indent_twips = SkripsiFormatter.cm_to_twips(SkripsiFormatter.FIRST_LINE_INDENT)
        ind.set(qn('w:firstLine'), str(indent_twips))
        
        # Set alignment to justify
        jc = pPr.find(qn('w:jc'))
        if jc is None:
            jc = OxmlElement('w:jc')
            pPr.append(jc)
        jc.set(qn('w:val'), 'both')
    
    @staticmethod
    def get_or_create_numbering(doc):
        """Get or create numbering part for multilevel numbering."""
        try:
            numbering_part = doc.part.numbering_part
        except:
            # Create numbering part if it doesn't exist
            from docx.opc.constants import RELATIONSHIP_TARGET_MODE
            numbering_part = doc.part.relate_to(
                'numbering.xml',
                'http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering'
            )
            numbering_part._element = parse_xml(r'<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>')
        
        return numbering_part
    
    @staticmethod
    def create_multilevel_numbering_definition(numbering_element, num_id):
        """
        Create a multilevel numbering definition:
        Level 1: I, II, III, ... (Roman uppercase)
        Level 2: A, B, C, ... (Letters)
        Level 3: 1, 2, 3, ... (Numbers)
        """
        # Create abstractNum
        abstractNum = OxmlElement('w:abstractNum')
        abstractNum.set(qn('w:abstractNumId'), str(num_id))
        
        # Level 1: Roman numerals (I, II, III)
        for level in range(3):
            lvl = OxmlElement('w:lvl')
            lvl.set(qn('w:ilvl'), str(level))
            
            start = OxmlElement('w:start')
            start.set(qn('w:val'), '1')
            lvl.append(start)
            
            numFmt = OxmlElement('w:numFmt')
            if level == 0:
                numFmt.set(qn('w:val'), 'upperRoman')
            elif level == 1:
                numFmt.set(qn('w:val'), 'upperLetter')
            else:
                numFmt.set(qn('w:val'), 'decimal')
            lvl.append(numFmt)
            
            lvlText = OxmlElement('w:lvlText')
            if level == 0:
                lvlText.set(qn('w:val'), 'BAB %1')
            elif level == 1:
                lvlText.set(qn('w:val'), '%2.')
            else:
                lvlText.set(qn('w:val'), '%3.')
            lvl.append(lvlText)
            
            lvlJc = OxmlElement('w:lvlJc')
            lvlJc.set(qn('w:val'), 'left')
            lvl.append(lvlJc)
            
            pPr = OxmlElement('w:pPr')
            ind = OxmlElement('w:ind')
            if level == 0:
                ind.set(qn('w:left'), '0')
                ind.set(qn('w:hanging'), '0')
            elif level == 1:
                ind.set(qn('w:left'), str(SkripsiFormatter.cm_to_twips(0.75)))
                ind.set(qn('w:hanging'), str(SkripsiFormatter.cm_to_twips(0.75)))
            else:
                ind.set(qn('w:left'), str(SkripsiFormatter.cm_to_twips(1.5)))
                ind.set(qn('w:hanging'), str(SkripsiFormatter.cm_to_twips(1.5)))
            pPr.append(ind)
            lvl.append(pPr)
            
            abstractNum.append(lvl)
        
        numbering_element.append(abstractNum)
        
        # Create num reference
        num = OxmlElement('w:num')
        num.set(qn('w:numId'), str(num_id + 1))
        absNumId = OxmlElement('w:abstractNumId')
        absNumId.set(qn('w:val'), str(num_id))
        num.append(absNumId)
        numbering_element.append(num)
        
        return num_id + 1
    
    @staticmethod
    def apply_heading_numbering(paragraph, level, num_id, ilvl):
        """Apply numbering to a heading paragraph."""
        pPr = paragraph._element.get_or_add_pPr()
        
        # Remove existing numbering
        numPr = pPr.find(qn('w:numPr'))
        if numPr is not None:
            pPr.remove(numPr)
        
        # Add new numbering
        numPr = OxmlElement('w:numPr')
        
        ilvlElem = OxmlElement('w:ilvl')
        ilvlElem.set(qn('w:val'), str(ilvl))
        numPr.append(ilvlElem)
        
        numIdElem = OxmlElement('w:numId')
        numIdElem.set(qn('w:val'), str(num_id))
        numPr.append(numIdElem)
        
        pPr.insert(0, numPr)
    
    @staticmethod
    def set_page_margins(doc):
        """Enforce page margins via section properties."""
        sections = doc.sections
        for section in sections:
            section.top_margin = Cm(SkripsiFormatter.MARGIN_TOP)
            section.bottom_margin = Cm(SkripsiFormatter.MARGIN_BOTTOM)
            section.left_margin = Cm(SkripsiFormatter.MARGIN_LEFT)
            section.right_margin = Cm(SkripsiFormatter.MARGIN_RIGHT)
    
    @staticmethod
    def enforce_skripsi_format(docx_path):
        """
        Main function: Enforce all skripsi formatting standards.
        
        1. Set page margins
        2. Fix paragraph spacing & indent
        3. Apply heading styles with Word-native numbering
        4. Apply numbering to BAB headings
        """
        doc = Document(docx_path)
        
        # Step 1: Set page margins
        SkripsiFormatter.set_page_margins(doc)
        
        # Step 2: Create numbering structure
        numbering_element = doc.element.find(qn('w:numbering'))
        if numbering_element is None:
            # Create numbering part
            numbering_xml = f'''<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" 
                                              xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml">
                             </w:numbering>'''
            numbering_element = parse_xml(numbering_xml)
        
        num_id = SkripsiFormatter.create_multilevel_numbering_definition(numbering_element, 0)
        
        # Ensure numbering is in document
        if doc.element.find(qn('w:numbering')) is None:
            doc.element.insert(0, numbering_element)
        
        # Step 3: Process paragraphs
        heading_count_by_level = {1: 0, 2: 0, 3: 0}
        
        for paragraph in doc.paragraphs:
            level = SkripsiFormatter.detect_heading_level(paragraph)
            
            if level:
                # Apply heading style
                style_name = {1: "Heading 1", 2: "Heading 2", 3: "Heading 3"}[level]
                paragraph.style = style_name
                
                # Set outline level for TOC
                pPr = paragraph._element.get_or_add_pPr()
                outlineLvl = pPr.find(qn('w:outlineLvl'))
                if outlineLvl is None:
                    outlineLvl = OxmlElement('w:outlineLvl')
                    pPr.append(outlineLvl)
                outlineLvl.set(qn('w:val'), str(level - 1))
                
                # Apply numbering to BAB (Level 1)
                if level == 1:
                    SkripsiFormatter.apply_heading_numbering(paragraph, level, num_id, 0)
                    heading_count_by_level[1] += 1
                elif level == 2:
                    SkripsiFormatter.apply_heading_numbering(paragraph, level, num_id, 1)
                    heading_count_by_level[2] += 1
                elif level == 3:
                    SkripsiFormatter.apply_heading_numbering(paragraph, level, num_id, 2)
                    heading_count_by_level[3] += 1
                
                # No indent for headings
                pPr = paragraph._element.get_or_add_pPr()
                ind = pPr.find(qn('w:ind'))
                if ind is not None:
                    ind.set(qn('w:firstLine'), '0')
            else:
                # Format normal paragraphs
                if paragraph.text.strip():  # Skip empty paragraphs
                    SkripsiFormatter.format_paragraph(paragraph)
        
        doc.save(docx_path)
        
        return {
            "status": "success",
            "margins_set": True,
            "headings_formatted": sum(heading_count_by_level.values()),
            "heading_breakdown": heading_count_by_level,
            "numbering_applied": num_id > 0
        }


def enforce_skripsi_format(docx_path):
    """
    Public function to enforce skripsi formatting.
    
    Args:
        docx_path (str): Path to DOCX file
        
    Returns:
        dict: Formatting results
    """
    return SkripsiFormatter.enforce_skripsi_format(docx_path)
