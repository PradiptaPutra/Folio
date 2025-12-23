from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from utils import WORD_DEFAULTS, txt_to_markdown
from docx_inspector import extract_docx_styles, detect_style_usage
from reference_builder import build_reference_docx

from pandoc_runner import markdown_to_docx
from pydantic import BaseModel
from text_normalizer import normalize_txt_to_markdown

# Import AI modules
from engine.ai.semantic_parser import SemanticParser
from engine.ai.front_matter_classifier import FrontMatterClassifier
from engine.ai.style_intent_inference import StyleIntentInference
from engine.ai.text_generation import AbstractGenerator, PrefaceGenerator

# Import analyzer modules for universal formatter
from engine.analyzer import TemplateAnalyzer, ContentExtractor, ContentMapper, DocumentMerger

# ============================================================================
# Environment Configuration
# ============================================================================
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
AI_MODEL = os.getenv('AI_MODEL', 'gpt-4-turbo')
BACKEND_PORT = int(os.getenv('BACKEND_PORT', 8000))
BACKEND_DEBUG = os.getenv('BACKEND_DEBUG', 'false').lower() == 'true'

# Verify AI configuration on startup
if not OPENAI_API_KEY:
    print('[WARNING] OPENAI_API_KEY not configured. AI features will be unavailable.')
    print('[INFO] Set OPENAI_API_KEY in .env file or environment to enable AI features.')
else:
    print(f'[INFO] AI API configured with model: {AI_MODEL}')


class GenerateRequest(BaseModel):
    reference_name: str
    content: str

# ============================================================================
# Request/Response Models for AI Endpoints
# ============================================================================

class ParseTextRequest(BaseModel):
    text: str

class ClassifyFrontmatterRequest(BaseModel):
    blocks: list[str]

class InferStyleRequest(BaseModel):
    style_data: dict

class GenerateAbstractIdRequest(BaseModel):
    title: str
    objectives: str
    methods: str
    results: str

class GenerateAbstractEnRequest(BaseModel):
    title: str
    objectives: str
    methods: str
    results: str

class GeneratePrefaceRequest(BaseModel):
    title: str
    author: str
    institution: str
    thesis_focus: str

class UniversalFormatterRequest(BaseModel):
    """Request model for universal thesis formatter."""
    title: str
    author: str
    nim: str
    advisor: str
    institution: str
    date: str
    thesis_focus: str = None
    
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "storage" / "uploads"
REF_DIR = BASE_DIR / "storage" / "references"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
REF_DIR.mkdir(parents=True, exist_ok=True)


def resolve_style(style_id, styles):
    style = styles.get(style_id, {})

    font = style.get("font")
    size = style.get("size")

    if font is None or size is None:
        parent_id = style.get("based_on")
        if parent_id and parent_id in styles:
            parent = resolve_style(parent_id, styles)
            font = font or parent["font"]
            size = size or parent["size"]

    return {
        "font": font or WORD_DEFAULTS["font"],
        "size": size or WORD_DEFAULTS["size"]
    }


# ============================================================================
# AI Endpoints
# ============================================================================

@app.post("/ai/parse-text")
async def parse_text_endpoint(request: ParseTextRequest):
    """Parse raw text into semantic structure using AI."""
    if not OPENAI_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="AI features are not configured. Please set OPENAI_API_KEY."
        )
    
    try:
        parser = SemanticParser(api_key=OPENAI_API_KEY)
        result = parser.parse(request.text)
        return result
    except Exception as e:
        import traceback
        error_msg = f"Semantic analysis failed: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=f"Semantic analysis failed: {str(e)}")


@app.post("/ai/classify-frontmatter")
async def classify_frontmatter_endpoint(request: ClassifyFrontmatterRequest):
    """Classify front matter blocks using AI."""
    if not OPENAI_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="AI features are not configured. Please set OPENAI_API_KEY."
        )
    
    try:
        classifier = FrontMatterClassifier(api_key=OPENAI_API_KEY)
        result = classifier.classify(request.blocks)
        return result
    except Exception as e:
        import traceback
        error_msg = f"Front matter classification failed: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=f"Front matter classification failed: {str(e)}")


@app.post("/ai/infer-style")
async def infer_style_endpoint(request: InferStyleRequest):
    """Infer style intent from template analysis."""
    if not OPENAI_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="AI features are not configured. Please set OPENAI_API_KEY."
        )
    
    try:
        inferrer = StyleIntentInference(api_key=OPENAI_API_KEY)
        result = inferrer.infer(request.style_data)
        return result
    except Exception as e:
        import traceback
        error_msg = f"Style inference failed: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=f"Style inference failed: {str(e)}")


@app.post("/ai/generate-abstract-id")
async def generate_abstract_id_endpoint(request: GenerateAbstractIdRequest):
    """Generate abstract in Indonesian."""
    if not OPENAI_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="AI features are not configured. Please set OPENAI_API_KEY."
        )
    
    try:
        generator = AbstractGenerator(api_key=OPENAI_API_KEY)
        abstract = generator.generate_abstract_id(
            title=request.title,
            objectives=request.objectives,
            methods=request.methods,
            results=request.results
        )
        return {"abstract": abstract}
    except Exception as e:
        import traceback
        error_msg = f"Abstract generation failed: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=f"Abstract generation failed: {str(e)}")


@app.post("/ai/generate-abstract-en")
async def generate_abstract_en_endpoint(request: GenerateAbstractEnRequest):
    """Generate abstract in English."""
    if not OPENAI_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="AI features are not configured. Please set OPENAI_API_KEY."
        )
    
    try:
        generator = AbstractGenerator(api_key=OPENAI_API_KEY)
        abstract = generator.generate_abstract_en(
            title=request.title,
            objectives=request.objectives,
            methods=request.methods,
            results=request.results
        )
        return {"abstract": abstract}
    except Exception as e:
        import traceback
        error_msg = f"Abstract generation failed: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=f"Abstract generation failed: {str(e)}")


@app.post("/ai/generate-preface")
async def generate_preface_endpoint(request: GeneratePrefaceRequest):
    """Generate preface."""
    if not OPENAI_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="AI features are not configured. Please set OPENAI_API_KEY."
        )
    
    try:
        generator = PrefaceGenerator(api_key=OPENAI_API_KEY)
        preface = generator.generate_preface(
            title=request.title,
            author=request.author,
            institution=request.institution,
            thesis_focus=request.thesis_focus
        )
        return {"preface": preface}
    except Exception as e:
        import traceback
        error_msg = f"Preface generation failed: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=f"Preface generation failed: {str(e)}")


@app.post("/validate-template")
async def validate_template(file: UploadFile = File(...)):
    """Validate a template DOCX file."""
    try:
        template_data = await file.read()
        template_path = UPLOAD_DIR / file.filename
        
        with template_path.open("wb") as buffer:
            buffer.write(template_data)
        
        # Extract and validate styles
        extracted = extract_docx_styles(template_path)
        
        return {
            "status": "valid",
            "message": "Template validated successfully",
            "filename": file.filename,
            "styles": extracted.get("styles", {}),
            "margins": extracted.get("margins", {})
        }
    except Exception as e:
        import traceback
        error_msg = f"Template validation failed: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        raise HTTPException(status_code=400, detail=f"Template validation failed: {str(e)}")


@app.post("/generate")
async def generate_document(
    file: UploadFile = File(None),
    template_file: UploadFile = File(None),
    reference_name: str = Form(None),
    content_file: UploadFile = File(None),
    include_frontmatter: str = Form("false"),
    judul: str = Form(None),
    penulis: str = Form(None),
    nim: str = Form(None),
    universitas: str = Form(None),
    tahun: str = Form(None),
    abstrak_id: str = Form(None),
    abstrak_teks: str = Form(None),
    abstrak_en_teks: str = Form(None),
    kata_kunci: str = Form(None),
    output_format: str = Form("docx"),
    dosen_pembimbing: str = Form(None),
    use_ai_analysis: str = Form("true")
):
    """
    Unified document generation endpoint - NOW CREATES COMPLETE THESIS with AI!
    
    Generates a fully-structured thesis document with:
    - Front Matter: Title page, approvals, originality, preface, abstracts
    - Main Content: Chapters from provided content (AI-analyzed structure)
    - Back Matter: References, appendices, lists
    
    Uses AI semantic analysis to intelligently detect document structure
    when available, falls back to rule-based extraction if needed.
    
    Parameters:
    - file: DOCX file to enforce (direct enforcement)
    - template_file: Template DOCX (template-based)
    - reference_name: Name of previously uploaded template
    - content_file: Raw text content (template-based)
    - include_frontmatter: Whether to add front matter
    - use_ai_analysis: Whether to use AI semantic analysis (true/false)
    - [frontmatter fields]: Front matter data
    - output_format: 'docx' or 'doc'
    """
    
    # folders
    md_dir = BASE_DIR / "storage" / "markdown"
    out_dir = BASE_DIR / "storage" / "outputs"
    md_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize content_path to None for cleanup
    content_path = None
    
    try:
        from engine.analyzer.complete_thesis_builder import create_complete_thesis
        
        include_fm = include_frontmatter.lower() in ('true', '1', 'yes')
        use_ai = use_ai_analysis.lower() in ('true', '1', 'yes')
        
        # ===== WORKFLOW 1: Template-based generation with COMPLETE THESIS (AI-enhanced) =====
        if (template_file or reference_name) and content_file:
            # Handle template upload
            if template_file:
                template_data = await template_file.read()
                template_path = UPLOAD_DIR / template_file.filename
                with template_path.open("wb") as buffer:
                    buffer.write(template_data)
                ref_path = REF_DIR / template_file.filename
                shutil.copy(template_path, ref_path)
                ref_name = template_file.filename
            else:
                ref_name = reference_name
                ref_path = REF_DIR / ref_name
            
            if not ref_path.exists():
                raise HTTPException(status_code=404, detail="Template not found")
            
            # Read text content
            raw_text = (await content_file.read()).decode("utf-8")
            print(f"[DEBUG] Raw text length: {len(raw_text)}")
            print(f"[DEBUG] Raw text preview: {raw_text[:200]}...")

            # Prepare output path
            student_name = penulis or "Student"
            output_filename = f"Skripsi_{student_name.replace(' ', '_')}.docx"
            output_path = out_dir / output_filename
            
            # Prepare user data for complete thesis builder
            user_data = {
                "title": judul or "JUDUL SKRIPSI",
                "author": penulis or "Nama Penulis",
                "nim": nim or "NIM",
                "advisor": dosen_pembimbing or "Nama Dosen Pembimbing",
                "institution": universitas or "Universitas",
                "date": tahun or "2025",
                "abstract_id": abstrak_teks or abstrak_id or "",
                "abstract_en": abstrak_en_teks or "",
                "keywords": kata_kunci.split(',') if kata_kunci else [],
            }
            
            # Create unique content file for thesis builder
            import time
            timestamp = int(time.time())
            content_path = UPLOAD_DIR / f"thesis_content_{timestamp}.txt"
            content_path.write_text(raw_text, encoding="utf-8")
            
            # Build COMPLETE thesis document
            result = create_complete_thesis(
                str(ref_path),
                str(content_path),
                str(output_path),
                user_data,
                use_ai=use_ai,
                include_frontmatter=include_fm
            )
            
            if not isinstance(result, dict):
                raise Exception(f"Expected dict result, got {type(result).__name__}: {result}")
            
            if result.get("status") != "success":
                raise Exception(result.get("message", "Failed to create thesis"))
            
            # Clean up temporary content file
            if content_path is not None and content_path.exists():
                content_path.unlink()
            
            # Return as file download
            from fastapi.responses import FileResponse
            return FileResponse(
                output_path,
                filename=output_filename,
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        
        else:
            raise HTTPException(
                status_code=400,
                detail="Provide template and content for document generation"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        # Clean up temporary content file on error
        if content_path is not None and content_path.exists():
            try:
                content_path.unlink()
            except:
                pass
        error_msg = f"Generation failed: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@app.post("/validate-semantic-structure")
async def validate_semantic_structure(
    content_file: UploadFile = File(...),
    use_ai: str = Form("true")
):
    """
    Validate the semantic structure of a document using AI analysis.
    
    Returns:
    - semantic_types: List of detected section types (introduction, methodology, etc.)
    - validation_status: Overall structure validation status
    - issues: Any structural problems found
    - warnings: Warnings about missing sections
    - suggestions: Improvement recommendations
    - ai_used: Whether AI analysis was used
    - summary: Extraction summary with confidence scores
    """
    try:
        from engine.analyzer.ai_enhanced_extractor import AIEnhancedContentExtractor
        
        # Save content file temporarily
        content_data = await content_file.read()
        content_path = UPLOAD_DIR / content_file.filename
        with content_path.open("wb") as buffer:
            buffer.write(content_data)
        
        # Extract and validate
        use_ai_flag = use_ai.lower() in ('true', '1', 'yes')
        extractor = AIEnhancedContentExtractor(str(content_path), use_ai=use_ai_flag)
        
        validation = extractor.get_semantic_validation()
        summary = extractor.get_summary()
        
        return {
            "status": "success",
            "validation": validation,
            "summary": summary,
            "sections": [
                {
                    "title": s.get("title", "Untitled"),
                    "type": s.get("semantic_type", "unknown"),
                    "level": s.get("level", 0),
                    "ai_analyzed": s.get("ai_analyzed", False),
                    "confidence": s.get("ai_confidence", 0.0),
                    "length": len(s.get("content", []))
                }
                for s in extractor.get_sections()
            ]
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Semantic validation failed: {str(e)}"
        )


@app.get("/ai-analysis-status")
async def ai_analysis_status():
    """Check if AI semantic analysis is available."""
    try:
        from engine.analyzer.ai_enhanced_extractor import AI_AVAILABLE
        from engine.ai.semantic_parser import SemanticParser
        
        return {
            "ai_available": AI_AVAILABLE,
            "semantic_parser_available": True,
            "capabilities": [
                "Chapter detection",
                "Section classification",
                "Semantic type inference",
                "Document structure validation",
                "Confidence scoring"
            ] if AI_AVAILABLE else []
        }
    except Exception as e:
        return {
            "ai_available": False,
            "semantic_parser_available": False,
            "error": str(e)
        }


# ============================================================================
# Universal Thesis Formatter Endpoints
# ============================================================================

@app.post("/universal-formatter/analyze-template")
async def analyze_template_endpoint(file: UploadFile = File(...)):
    """Analyze a DOCX template to detect structure and formatting rules."""
    try:
        # Save uploaded file
        template_data = await file.read()
        template_path = UPLOAD_DIR / file.filename
        
        with template_path.open("wb") as buffer:
            buffer.write(template_data)
        
        # Analyze template
        analyzer = TemplateAnalyzer(str(template_path))
        analysis = analyzer.get_analysis()
        
        return {
            "status": "success",
            "message": "Template analyzed successfully",
            "analysis": {
                "document_properties": analysis.get("document_properties"),
                "margins": analysis.get("margins"),
                "front_matter_sections": analysis.get("front_matter", {}).get("sections", []),
                "detected_styles": list(analysis.get("styles", {}).keys()),
                "heading_hierarchy": analysis.get("heading_hierarchy", {}),
                "special_elements": analysis.get("special_elements", {}),
                "formatting_rules": analysis.get("formatting_rules", {}),
            },
            "summary": analyzer.get_summary()
        }
    except Exception as e:
        import traceback
        error_msg = f"Template analysis failed: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        raise HTTPException(status_code=400, detail=f"Template analysis failed: {str(e)}")


@app.post("/universal-formatter/extract-content")
async def extract_content_endpoint(file: UploadFile = File(...)):
    """Extract sections and content from a DOCX or TXT file."""
    try:
        # Save uploaded file
        content_data = await file.read()
        content_path = UPLOAD_DIR / file.filename
        
        with content_path.open("wb" if file.filename.endswith('.docx') else "w") as buffer:
            if file.filename.endswith('.docx'):
                buffer.write(content_data)
            else:
                buffer.write(content_data.decode('utf-8'))
        
        # Extract content
        extractor = ContentExtractor(str(content_path))
        sections = extractor.get_sections()
        
        return {
            "status": "success",
            "message": "Content extracted successfully",
            "sections": sections,
            "section_count": len(sections),
            "summary": extractor.get_summary()
        }
    except Exception as e:
        import traceback
        error_msg = f"Content extraction failed: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        raise HTTPException(status_code=400, detail=f"Content extraction failed: {str(e)}")


@app.post("/universal-formatter/format-thesis")
async def format_thesis_endpoint(
    template_file: UploadFile = File(...),
    content_file: UploadFile = File(...),
    title: str = Form(...),
    author: str = Form(...),
    nim: str = Form(...),
    advisor: str = Form(...),
    institution: str = Form(...),
    date: str = Form(...)
):
    """
    Universal thesis formatter endpoint - creates COMPLETE thesis documents.
    
    Creates a fully structured thesis with:
    - Front Matter: Title page, approval pages, originality statement, preface, abstracts
    - Main Content: Chapters from user content
    - Back Matter: References, appendices, lists of tables/figures
    
    Parameters:
    - template_file: DOCX template from university
    - content_file: DOCX or TXT content file
    - title: Thesis title
    - author: Author/Student name
    - nim: Student ID
    - advisor: Advisor name
    - institution: University name
    - date: Current date
    """
    try:
        from engine.analyzer.complete_thesis_builder import create_complete_thesis
        
        # Save files
        template_data = await template_file.read()
        content_data = await content_file.read()
        
        template_path = UPLOAD_DIR / template_file.filename
        content_path = UPLOAD_DIR / content_file.filename
        
        with template_path.open("wb") as f:
            f.write(template_data)
        
        is_content_docx = content_file.filename.endswith('.docx')
        with content_path.open("wb" if is_content_docx else "w") as f:
            if is_content_docx:
                f.write(content_data)
            else:
                f.write(content_data.decode('utf-8'))
        
        # Prepare output path
        output_filename = f"Skripsi_{author.replace(' ', '_')}_{date.replace('/', '-')}.docx"
        output_path = BASE_DIR / "storage" / "outputs" / output_filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Build complete thesis
        user_data = {
            "title": title,
            "author": author,
            "nim": nim,
            "advisor": advisor,
            "institution": institution,
            "date": date,
        }
        
        result = create_complete_thesis(
            str(template_path),
            str(content_path),
            str(output_path),
            user_data
        )
        
        if result["status"] != "success":
            raise Exception(result.get("message", "Failed to create thesis"))
        
        # Return file for download
        from fastapi.responses import FileResponse
        return FileResponse(
            output_path,
            filename=output_filename,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
    except Exception as e:
        import traceback
        error_msg = f"Thesis formatting failed: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=f"Thesis formatting failed: {str(e)}")


@app.get("/universal-formatter/info")
async def universal_formatter_info():
    """Get information about the universal formatter."""
    return {
        "status": "available",
        "version": "2.0.0",
        "name": "Universal Thesis/Skripsi Formatter",
        "description": "Intelligently formats theses/skripsi for any university template",
        "capabilities": [
            "Automatic template detection and analysis",
            "Dynamic content extraction",
            "Intelligent section mapping",
            "Style preservation and consistency",
            "Auto-generation of missing sections",
            "Placeholder replacement with user data",
            "Support for any university template",
            "Works with DOCX and TXT content files",
        ],
        "supported_universities": "Any university (universal support)",
        "endpoints": {
            "/universal-formatter/analyze-template": "Analyze a DOCX template",
            "/universal-formatter/extract-content": "Extract sections from content file",
            "/universal-formatter/format-thesis": "Format thesis using template and content",
            "/universal-formatter/info": "Get formatter information",
        }
    }


@app.post("/preview-document")
async def preview_document(file: UploadFile = File(...)):
    """
    Convert DOCX file to HTML for preview in browser.
    """
    try:
        # Save uploaded file temporarily
        temp_dir = BASE_DIR / "storage" / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)

        temp_file = temp_dir / f"preview_{file.filename}"
        with open(temp_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Convert DOCX to HTML using pandoc
        import subprocess
        html_output = temp_file.with_suffix('.html')

        # Run pandoc to convert DOCX to HTML
        result = subprocess.run(
            ['pandoc', str(temp_file), '-o', str(html_output), '--self-contained'],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Pandoc conversion failed: {result.stderr}")

        # Read the HTML content
        with open(html_output, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Clean up temp files
        temp_file.unlink(missing_ok=True)
        html_output.unlink(missing_ok=True)

        return {
            "status": "success",
            "html_content": html_content
        }

    except Exception as e:
        import traceback
        error_msg = f"Document preview failed: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=f"Preview generation failed: {str(e)}")


@app.get("/enforcement-status")
async def enforcement_status():
    """
    Get information about available enforcement phases.
    
    Returns:
        - phases: Dict mapping phase -> description
        - version: Implementation version
    """
    return {
        "status": "available",
        "version": "1.0.0",
        "phases": {
            "phase_3_1": "BAB + Judul merging (soft line break)",
            "phase_3_2": "IsiParagraf paragraph style enforcement",
            "phase_3_3": "Native Word TOC field generation",
            "phase_3_4": "Strict heading style discipline",
            "phase_3_5": "Page breaks & numbering",
            "phase_4": "Front-matter auto-generation"
        },
        "implementation": {
            "bab_judul_merge": "Detects BAB I + PENDAHULUAN, merges with soft break",
            "paragraph_formatting": "1.5 line spacing, 1cm indent, justified, 0pt spacing",
            "toc_field": "TOC \\o \"1-2\" \\h \\z \\u (Heading 1-2 only)",
            "page_breaks": "Before each BAB except BAB I",
            "front_matter": "Title page, approval, declaration, preface, abstracts"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=BACKEND_PORT, reload=BACKEND_DEBUG)