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
    output_format: str = Form("docx")
):
    """
    Unified document generation endpoint.
    
    Supports two workflows:
    1. Template-based generation: Upload template + raw text content
    2. Direct enforcement: Upload DOCX file directly
    
    Parameters:
    - file: DOCX file to enforce (direct enforcement)
    - template_file: Template DOCX (template-based)
    - reference_name: Name of previously uploaded template
    - content_file: Raw text content (template-based)
    - include_frontmatter: Whether to add front matter
    - [frontmatter fields]: Optional front matter data
    - output_format: 'docx' or 'doc'
    """
    
    # folders
    md_dir = BASE_DIR / "storage" / "markdown"
    out_dir = BASE_DIR / "storage" / "outputs"
    md_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        include_fm = include_frontmatter.lower() in ('true', '1', 'yes')
        
        # ===== WORKFLOW 1: Template-based generation =====
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
            markdown = normalize_txt_to_markdown(raw_text)
            
            # Generate from template
            md_path = md_dir / "content.md"
            md_path.write_text(markdown, encoding="utf-8")
            
            fmt = output_format.lower().strip()
            if fmt not in {"docx", "doc"}:
                fmt = "docx"
            output_path = out_dir / ("final." + fmt)
            
            # Extract template styles
            extracted = extract_docx_styles(ref_path)
            normal_style = extracted["styles"].get("Normal", {})
            paragraph_config = normal_style.get("paragraph", {})
            style_usage = detect_style_usage(str(ref_path))
            
            style_config = {
                "margins": extracted["margins"],
                "paragraph": paragraph_config,
                "mapping": style_usage
            }
            
            # Prepare front-matter data
            frontmatter_data = None
            if include_fm:
                frontmatter_data = {
                    'judul': judul or 'JUDUL SKRIPSI',
                    'penulis': penulis or 'Nama Penulis',
                    'nim': nim or 'NIM',
                    'universitas': universitas or 'Universitas',
                    'tahun': int(tahun) if tahun else 2024,
                    'abstrak_id': abstrak_id or 'ABSTRAK',
                    'abstrak_teks': abstrak_teks or 'Isi abstrak di sini.',
                    'abstrak_en_teks': abstrak_en_teks or 'Abstract content here.',
                    'kata_kunci': kata_kunci or 'keyword1, keyword2'
                }

            # Generate document (always .docx internally)
            docx_output = out_dir / "final.docx"
            markdown_to_docx(md_path, ref_path, docx_output, style_config, frontmatter_data)
            
            # Return as file download
            from fastapi.responses import FileResponse
            return FileResponse(
                docx_output,
                filename="formatted.docx",
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
        error_msg = f"Generation failed: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


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
    Universal thesis formatter endpoint.
    
    Accepts any university template and content, intelligently merges them
    with user data while preserving all formatting rules.
    
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
        
        # Step 1: Analyze template
        template_analyzer = TemplateAnalyzer(str(template_path))
        
        # Step 2: Extract content
        content_extractor = ContentExtractor(str(content_path))
        
        # Step 3: Create mapping
        content_mapper = ContentMapper(template_analyzer, content_extractor)
        
        # Step 4: Merge documents
        output_filename = f"Skripsi_{author.replace(' ', '_')}_{date.replace('/', '-')}.docx"
        output_path = BASE_DIR / "storage" / "outputs" / output_filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        merger = DocumentMerger(template_analyzer, content_extractor, content_mapper, str(output_path))
        
        # Prepare user data
        user_data = {
            "title": title,
            "author": author,
            "nim": nim,
            "advisor": advisor,
            "institution": institution,
            "date": date,
        }
        
        # Execute merge
        final_path = merger.merge(user_data)
        
        # Generate report
        report = merger.get_merge_report()
        
        # Read file for download
        from fastapi.responses import FileResponse
        return FileResponse(
            final_path,
            filename=output_filename,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "X-Merge-Report": str(report).replace('"', "'")  # Include report in header
            }
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