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
    def format_paragraph(paragraph, p_config=None):
        """
        Format paragraph with skripsi standards or dynamic config:
        - Line spacing: 1.5 or dynamic
        - First-line indent: 1.25 cm or dynamic
        - Space before/after: 0 pt
        - Alignment: Justify
        """
        pPr = paragraph._element.get_or_add_pPr()
        
        # Set line spacing
        spacing = pPr.find(qn('w:spacing'))
        if spacing is None:
            spacing = OxmlElement('w:spacing')
            pPr.append(spacing)
        
        spacing.set(qn('w:before'), str(SkripsiFormatter.PARAGRAPH_SPACE_BEFORE))
        spacing.set(qn('w:after'), str(SkripsiFormatter.PARAGRAPH_SPACE_AFTER))

        if p_config and p_config.get("line_spacing"):
            # Use dynamic spacing
            spacing.set(qn('w:line'), str(p_config["line_spacing"]))
            rule = p_config.get("line_rule", "auto")
            spacing.set(qn('w:lineRule'), rule)
        else:
            # Default 1.5 spacing
            spacing.set(qn('w:line'), '360')
            spacing.set(qn('w:lineRule'), 'auto')
        
        # Set first-line indent
        ind = pPr.find(qn('w:ind'))
        if ind is None:
            ind = OxmlElement('w:ind')
            pPr.append(ind)
        
        if p_config and (p_config.get("indent_first_line") or p_config.get("indent_left")):
            # Use dynamic indent
            if p_config.get("indent_first_line"):
                ind.set(qn('w:firstLine'), str(p_config["indent_first_line"]))
            if p_config.get("indent_left"):
                ind.set(qn('w:left'), str(p_config["indent_left"]))
            if p_config.get("indent_right"):
                ind.set(qn('w:right'), str(p_config["indent_right"]))
        else:
            # Default 1.25 cm
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
        Create a multilevel numbering definition (AbstractNum):
        Level 1 (0): BAB I, BAB II (Roman) -> Heading 1
        Level 2 (1): 1.1, 1.2 (Arabic, inherits Level 1 as Arabic) -> Heading 2
        Level 3 (2): 1.1.1, 1.1.2 (Arabic) -> Heading 3
        """
        abstractNum = OxmlElement('w:abstractNum')
        abstractNum.set(qn('w:abstractNumId'), str(num_id))
        
        # Link to styles (Recommended for robustness)
        multiLevelType = OxmlElement('w:multiLevelType')
        multiLevelType.set(qn('w:val'), 'multilevel')
        abstractNum.append(multiLevelType)
        
        # --- Level 1: BAB I ---
        lvl0 = OxmlElement('w:lvl')
        lvl0.set(qn('w:ilvl'), '0')
        
        start0 = OxmlElement('w:start')
        start0.set(qn('w:val'), '1')
        lvl0.append(start0)
        
        numFmt0 = OxmlElement('w:numFmt')
        numFmt0.set(qn('w:val'), 'upperRoman')
        lvl0.append(numFmt0)
        
        lvlText0 = OxmlElement('w:lvlText')
        lvlText0.set(qn('w:val'), 'BAB %1')
        lvl0.append(lvlText0)
        
        lvlJc0 = OxmlElement('w:lvlJc')
        lvlJc0.set(qn('w:val'), 'center') # BAB usually centered
        lvl0.append(lvlJc0)
        
        pPr0 = OxmlElement('w:pPr')
        ind0 = OxmlElement('w:ind')
        ind0.set(qn('w:left'), '0')
        ind0.set(qn('w:hanging'), '0')
        pPr0.append(ind0)
        lvl0.append(pPr0)
        
        abstractNum.append(lvl0)
        
        # --- Level 2: 1.1 (Converts I to 1) ---
        lvl1 = OxmlElement('w:lvl')
        lvl1.set(qn('w:ilvl'), '1')
        
        start1 = OxmlElement('w:start')
        start1.set(qn('w:val'), '1')
        lvl1.append(start1)
        
        numFmt1 = OxmlElement('w:numFmt')
        numFmt1.set(qn('w:val'), 'decimal')
        lvl1.append(numFmt1)
        
        # IsLgl: Forces previous level references (BAB I) to be Arabic (1)
        isLgl1 = OxmlElement('w:isLgl')
        lvl1.append(isLgl1)
        
        lvlText1 = OxmlElement('w:lvlText')
        lvlText1.set(qn('w:val'), '%1.%2')
        lvl1.append(lvlText1)
        
        lvlJc1 = OxmlElement('w:lvlJc')
        lvlJc1.set(qn('w:val'), 'left')
        lvl1.append(lvlJc1)
        
        pPr1 = OxmlElement('w:pPr')
        ind1 = OxmlElement('w:ind')
        ind1.set(qn('w:left'), str(SkripsiFormatter.cm_to_twips(1.25))) # Indent text
        ind1.set(qn('w:hanging'), str(SkripsiFormatter.cm_to_twips(1.25))) # Number sticks out
        pPr1.append(ind1)
        lvl1.append(pPr1)
        
        abstractNum.append(lvl1)
        
        # --- Level 3: 1.1.1 ---
        lvl2 = OxmlElement('w:lvl')
        lvl2.set(qn('w:ilvl'), '2')
        
        start2 = OxmlElement('w:start')
        start2.set(qn('w:val'), '1')
        lvl2.append(start2)
        
        numFmt2 = OxmlElement('w:numFmt')
        numFmt2.set(qn('w:val'), 'decimal')
        lvl2.append(numFmt2)
        
        isLgl2 = OxmlElement('w:isLgl')
        lvl2.append(isLgl2)
        
        lvlText2 = OxmlElement('w:lvlText')
        lvlText2.set(qn('w:val'), '%1.%2.%3')
        lvl2.append(lvlText2)
        
        lvlJc2 = OxmlElement('w:lvlJc')
        lvlJc2.set(qn('w:val'), 'left')
        lvl2.append(lvlJc2)
        
        pPr2 = OxmlElement('w:pPr')
        ind2 = OxmlElement('w:ind')
        ind2.set(qn('w:left'), str(SkripsiFormatter.cm_to_twips(1.5))) 
        ind2.set(qn('w:hanging'), str(SkripsiFormatter.cm_to_twips(1.5)))
        pPr2.append(ind2)
        lvl2.append(pPr2)
        
        abstractNum.append(lvl2)
        
        numbering_element.append(abstractNum)
        
        # Create num instance
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
    def enforce_skripsi_format(docx_path, style_config=None):
        """
        Main function: Enforce all skripsi formatting standards.
        
        1. Set page margins (dynamic if style_config provided)
        2. Fix paragraph spacing & indent (dynamic if style_config provided)
        3. Apply heading styles with Word-native numbering
        4. Apply numbering to BAB headings
        """
        doc = Document(docx_path)
        
        # Step 1: Set page margins
        if style_config and style_config.get("margins"):
            # Use dynamic margins from template
            SkripsiFormatter.set_dynamic_margins(doc, style_config["margins"])
        else:
            # Use hardcoded defaults
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
        
        # Prepare paragraph config
        p_config = style_config.get("paragraph") if style_config else None
        
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
                
                # Apply strictly defined spacing (Dosen Mode)
                spacing = pPr.find(qn('w:spacing'))
                if spacing is None:
                    spacing = OxmlElement('w:spacing')
                    pPr.append(spacing)
                
                if level == 1:
                    spacing.set(qn('w:before'), '480') # 24pt
                    spacing.set(qn('w:after'), '240')  # 12pt
                    
                    # Page Break Before (Strict requirement: BAB starts new page)
                    pageBreakBefore = pPr.find(qn('w:pageBreakBefore'))
                    if pageBreakBefore is None:
                        pageBreakBefore = OxmlElement('w:pageBreakBefore')
                        pPr.append(pageBreakBefore)
                    pageBreakBefore.set(qn('w:val'), 'on')
                    
                elif level == 2:
                    spacing.set(qn('w:before'), '240') # 12pt
                    spacing.set(qn('w:after'), '120')  # 6pt
                elif level == 3:
                    spacing.set(qn('w:before'), '120') # 6pt
                    spacing.set(qn('w:after'), '120')  # 6pt
                
                # Apply numbering to BAB (Level 1)
                # Note: Multilevel definition handles the numbering format
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
                ind = pPr.find(qn('w:ind'))
                if ind is not None:
                    ind.set(qn('w:firstLine'), '0')
            else:
                # Format normal paragraphs
                if paragraph.text.strip():  # Skip empty paragraphs
                    SkripsiFormatter.format_paragraph(paragraph, p_config)
        
        doc.save(docx_path)
        
        return {
            "status": "success",
            "margins_set": True,
            "headings_formatted": sum(heading_count_by_level.values()),
            "heading_breakdown": heading_count_by_level,
            "numbering_applied": num_id > 0
        }

    @staticmethod
    def set_dynamic_margins(doc, margins):
        """Set page margins from template config (values in twips)."""
        from docx.shared import Twips
        sections = doc.sections
        for section in sections:
            if margins.get("top"):
                section.top_margin = Twips(int(margins["top"]))
            if margins.get("bottom"):
                section.bottom_margin = Twips(int(margins["bottom"]))
            if margins.get("left"):
                section.left_margin = Twips(int(margins["left"]))
            if margins.get("right"):
                section.right_margin = Twips(int(margins["right"]))


def enforce_skripsi_format(docx_path, style_config=None):
    """
    Public function to enforce skripsi formatting.
    
    Args:
        docx_path (str): Path to DOCX file
        style_config (dict, optional): Configuration from template
        
    Returns:
        dict: Formatting results
    """
    return SkripsiFormatter.enforce_skripsi_format(docx_path, style_config)
