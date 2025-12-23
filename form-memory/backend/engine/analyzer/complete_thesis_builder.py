"""
Complete Thesis Document Builder
Orchestrates the creation of a complete, properly structured thesis document
with all front matter, main content, and back matter.
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
from docx import Document
from docx.shared import Pt, Inches
from .template_analyzer import TemplateAnalyzer
from .content_extractor import ContentExtractor
from .ai_enhanced_extractor import AIEnhancedContentExtractor
from .content_mapper import ContentMapper
from .document_merger import DocumentMerger
from .front_matter_generator import FrontMatterGenerator, BackMatterGenerator


class CompleteThesisBuilder:
    """Builds a complete thesis document with all required sections."""
    
    def __init__(self, template_path: str, content_path: str, output_path: str, use_ai: bool = True, include_frontmatter: bool = True):
        """Initialize the thesis builder.
        
        Args:
            template_path: Path to DOCX template
            content_path: Path to content file (DOCX or TXT)
            output_path: Path for output DOCX
            use_ai: Whether to use AI semantic analysis (if available)
            include_frontmatter: Whether to include front matter sections
        """
        self.template_path = Path(template_path)
        self.content_path = Path(content_path)
        self.output_path = Path(output_path)
        self.use_ai = use_ai
        self.include_frontmatter = include_frontmatter
        
        # Initialize components
        self.analyzer = TemplateAnalyzer(str(self.template_path))
        # Use AI-enhanced extractor when available
        self.ai_extractor = AIEnhancedContentExtractor(str(self.content_path), use_ai=use_ai)
        self.extractor = ContentExtractor(str(self.content_path))
        self.mapper = ContentMapper(self.analyzer, self.extractor)
        
        # Semantic validation
        self.semantic_validation = self.ai_extractor.get_semantic_validation() if use_ai else None
    
    def build(self, user_data: Dict[str, Any] = None) -> Path:
        """Build the complete thesis document.
        
        Args:
            user_data: Dictionary with keys:
                - title: Thesis title
                - author: Author name
                - nim: Student ID
                - advisor: Advisor name
                - institution: University/institution name
                - date: Date/year
                - abstract_id: Abstract in Indonesian
                - abstract_en: Abstract in English
                - keywords: List of keywords
                - preface: Custom preface text
                - dedication: Custom dedication text
                - motto: Custom motto text
                - references: List of reference dicts with keys:
                    - author, year, title, publisher/journal
                - appendices: List of appendix dicts with keys:
                    - title, content
                - glossary: Dict of {term: definition}
        
        Returns:
            Path to created DOCX file
        """
        user_data = user_data or {}
        
        # Load template document
        try:
            doc = Document(str(self.template_path))
        except Exception as e:
            print(f"[WARNING] Failed to load template, creating new document: {e}")
            doc = Document()
        
        # Build sections in order
        if self.include_frontmatter:
            self._add_front_matter(doc, user_data)
        self._add_main_content(doc, user_data)
        self._add_back_matter(doc, user_data)
        
        # Save
        doc.save(str(self.output_path))
        
        return self.output_path
    
    def _add_front_matter(self, doc: Document, user_data: Dict[str, Any]) -> None:
        """Add all front matter sections."""
        generator = FrontMatterGenerator(user_data)
        
        # Title Page
        generator.create_title_page(doc)
        
        # Approval Pages
        generator.create_approval_page(doc, approval_type="supervisor")
        generator.create_approval_page(doc, approval_type="examiner")
        
        # Originality Statement
        generator.create_originality_statement(doc)
        
        # Optional: Dedication
        if user_data and isinstance(user_data, dict) and user_data.get("dedication"):
            generator.create_dedication_page(doc, user_data["dedication"])
        
        # Optional: Motto
        if user_data and isinstance(user_data, dict) and user_data.get("motto"):
            generator.create_motto_page(doc, user_data["motto"])
        
        # Preface
        generator.create_preface(doc)
        
        # Abstracts
        generator.create_abstract(doc, language="id")
        if user_data and isinstance(user_data, dict) and user_data.get("abstract_en"):
            generator.create_abstract(doc, language="en")
        
        # Table of Contents
        generator.create_table_of_contents(doc)
        
        # Glossary (if provided)
        if user_data and isinstance(user_data, dict) and user_data.get("glossary"):
            generator.create_glossary(doc, user_data["glossary"])
    
    def _add_main_content(self, doc: Document, user_data: Dict[str, Any]) -> None:
        """Add main content (chapters/sections from extractor)."""
        sections = self.extractor.get_sections()
        
        for idx, section in enumerate(sections, 1):
            # Skip non-dict sections
            if not isinstance(section, dict):
                continue
            
            # Add page break before chapter (except first)
            if idx > 1:
                doc.add_page_break()
            
            # Add chapter heading
            title = section.get("title", f"Chapter {idx}")
            heading_para = doc.add_paragraph(title)
            heading_para.style = "Heading 1"
            heading_run = heading_para.runs[0]
            heading_run.font.bold = True
            heading_run.font.size = Pt(14)
            
            # Add section content
            content = section.get("content", [])
            if isinstance(content, list):
                for line in content:
                    if isinstance(line, str) and line.strip():
                        para = doc.add_paragraph(line)
                        para.style = "Normal"
                        # Apply paragraph formatting
                        para.paragraph_format.left_indent = Inches(0.0)
                        para.paragraph_format.first_line_indent = Inches(1.0)
                        para.paragraph_format.line_spacing = 1.5
                        for run in para.runs:
                            run.font.size = Pt(11)
                            run.font.name = "Times New Roman"
            else:
                # Content is a single string
                para = doc.add_paragraph(str(content))
                para.style = "Normal"
                para.paragraph_format.left_indent = Inches(0.0)
                para.paragraph_format.first_line_indent = Inches(1.0)
                para.paragraph_format.line_spacing = 1.5
                for run in para.runs:
                    run.font.size = Pt(11)
                    run.font.name = "Times New Roman"
    
    def _add_back_matter(self, doc: Document, user_data: Dict[str, Any]) -> None:
        """Add all back matter sections."""
        generator = BackMatterGenerator(user_data)
        
        # List of Tables
        generator.create_list_of_tables(doc)
        
        # List of Figures
        generator.create_list_of_figures(doc)
        
        # References/Bibliography
        references = user_data.get("references", []) if user_data and isinstance(user_data, dict) else []
        generator.create_references(doc, references)
        
        # Appendices
        appendices = user_data.get("appendices", []) if user_data and isinstance(user_data, dict) else []
        if appendices:
            generator.create_appendices(doc, appendices)
    
    def get_analysis_report(self) -> Dict[str, Any]:
        """Get comprehensive analysis report of template, content, and semantic structure."""
        report = {
            "template_analysis": self.analyzer.get_summary(),
            "content_summary": self.extractor.get_summary(),
            "mapping_summary": self.mapper.get_summary(),
            "sections_found": len(self.extractor.get_sections()),
            "styles_detected": len(self.analyzer.analysis.get("styles", {})),
        }
        
        # Add AI semantic analysis if available
        if self.use_ai:
            sections = self.ai_extractor.get_sections()
            semantic_types = []
            for s in sections:
                if isinstance(s, dict):
                    semantic_types.append(s.get("semantic_type", "unknown"))
            
            report["ai_semantic_analysis"] = {
                "extraction_summary": self.ai_extractor.get_summary(),
                "semantic_validation": self.semantic_validation,
                "semantic_types_found": list(set(semantic_types)),
            }
        
        return report


def create_complete_thesis(
    template_path: str,
    content_path: str,
    output_path: str,
    user_data: Dict[str, Any] = None,
    use_ai: bool = True,
    include_frontmatter: bool = True
) -> Dict[str, Any]:
    """Convenience function to create a complete thesis in one call.
    
    Args:
        template_path: Path to DOCX template
        content_path: Path to content file
        output_path: Path for output DOCX
        user_data: User data dictionary
        use_ai: Whether to use AI semantic analysis
        include_frontmatter: Whether to include front matter sections
    
    Returns:
        Dictionary with:
            - output_file: Path to created document
            - status: "success" or "error"
            - message: Status message
            - report: Analysis report
    """
    try:
        # Verify files exist before creating builder
        template_p = Path(template_path)
        content_p = Path(content_path)
        
        if not template_p.exists():
            return {
                "status": "error",
                "message": f"Template file not found: {template_path}",
                "error_details": f"File does not exist: {template_path}",
            }
        
        if not content_p.exists():
            return {
                "status": "error",
                "message": f"Content file not found: {content_path}",
                "error_details": f"File does not exist: {content_path}",
            }
        
        builder = CompleteThesisBuilder(template_path, content_path, output_path, use_ai=use_ai, include_frontmatter=include_frontmatter)
        
        # Get analysis before building
        report = builder.get_analysis_report()
        
        # Build the thesis
        output = builder.build(user_data or {})
        
        return {
            "status": "success",
            "output_file": str(output),
            "message": "Complete thesis document created successfully",
            "report": report,
            "file_size": output.stat().st_size if output.exists() else 0,
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": f"Failed to create thesis: {str(e)}",
            "error_details": traceback.format_exc(),
        }
