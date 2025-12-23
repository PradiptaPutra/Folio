"""
Text Replacer
Replaces text in paragraphs while preserving run-level formatting.
No modification of styles or structure.
"""

from docx.oxml.ns import qn
from typing import Optional, List


class TextReplacer:
    """Replaces text in paragraphs preserving formatting."""
    
    @staticmethod
    def replace_paragraph_text(para, new_text: str) -> None:
        """Replace all text in a paragraph preserving runs and formatting."""
        para_elem = para._element
        
        # Clear existing runs but preserve paragraph properties
        runs = para_elem.findall('.//w:r', namespaces={'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'})
        for run_elem in runs:
            para_elem.remove(run_elem)
        
        # Create single new run with formatting from first original run
        if runs:
            first_run_elem = runs[0]
            rPr = first_run_elem.find(qn('w:rPr'))
        else:
            rPr = None
        
        # Create new run
        new_run = para.add_run(new_text)
        
        # Apply original formatting if available
        if rPr is not None:
            new_run_elem = new_run._element
            new_rPr = new_run_elem.find(qn('w:rPr'))
            
            if new_rPr is not None:
                new_run_elem.remove(new_rPr)
            
            # Clone original rPr
            from copy import deepcopy
            cloned_rPr = deepcopy(rPr)
            new_run_elem.insert(0, cloned_rPr)
    
    @staticmethod
    def replace_paragraph_text_preserving_runs(para, new_text: str) -> None:
        """Replace text while preserving individual runs (if possible)."""
        para_elem = para._element
        runs = para_elem.findall('.//w:r', namespaces={'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'})
        
        if not runs:
            para.text = new_text
            return
        
        # Simple approach: put all text in first run, clear rest
        if runs:
            first_run = runs[0]
            t_elem = first_run.find(qn('w:t'))
            
            if t_elem is not None:
                t_elem.text = new_text
            else:
                # Create new text element
                t_elem = para._new_run_element()
                t_elem.text = new_text
                first_run.append(t_elem)
            
            # Remove other runs
            for run_elem in runs[1:]:
                para_elem.remove(run_elem)
    
    @staticmethod
    def append_text_to_paragraph(para, text: str) -> None:
        """Append text to paragraph preserving existing content."""
        para.add_run(text)
    
    @staticmethod
    def get_paragraph_text(para) -> str:
        """Get full text from paragraph."""
        return para.text
    
    @staticmethod
    def replace_text_in_runs(para, old_text: str, new_text: str) -> int:
        """Find and replace text within runs. Returns count of replacements."""
        para_elem = para._element
        runs = para_elem.findall('.//w:r', namespaces={'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'})
        
        count = 0
        for run_elem in runs:
            t_elem = run_elem.find(qn('w:t'))
            if t_elem is not None and t_elem.text:
                if old_text in t_elem.text:
                    t_elem.text = t_elem.text.replace(old_text, new_text)
                    count += 1
        
        return count
    
    @staticmethod
    def clear_paragraph_text(para) -> None:
        """Clear all text from paragraph preserving structure."""
        para_elem = para._element
        runs = para_elem.findall('.//w:r', namespaces={'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'})
        
        for run_elem in runs:
            para_elem.remove(run_elem)
