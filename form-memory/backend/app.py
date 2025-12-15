from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
from pathlib import Path

from utils import WORD_DEFAULTS, txt_to_markdown
from docx_inspector import extract_docx_styles, detect_style_usage
from reference_builder import build_reference_docx

from pandoc_runner import markdown_to_docx
from pydantic import BaseModel
from text_normalizer import normalize_txt_to_markdown
from skripsi_enforcer import enforce_skripsi_template


class GenerateRequest(BaseModel):
    reference_name: str
    content: str
    
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

            # Generate document
            markdown_to_docx(md_path, ref_path, output_path, style_config, frontmatter_data)
            
            # Return as file download
            from fastapi.responses import FileResponse
            return FileResponse(
                output_path,
                filename=f"formatted.{fmt}",
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        
        # ===== WORKFLOW 2: Direct file enforcement =====
        elif file:
            file_data = await file.read()
            docx_path = UPLOAD_DIR / file.filename
            with docx_path.open("wb") as buffer:
                buffer.write(file_data)
            
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
            
            # Execute enforcement
            result = enforce_skripsi_template(
                str(docx_path),
                include_frontmatter=include_fm,
                frontmatter_data=frontmatter_data
            )
            
            # Get the output file
            output_file = result.get('file', file.filename)
            output_path = UPLOAD_DIR / output_file
            
            # Return as file download
            from fastapi.responses import FileResponse
            return FileResponse(
                output_path,
                filename=f"{Path(file.filename).stem}_enforced.docx",
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        
        else:
            raise HTTPException(
                status_code=400,
                detail="Either provide template+content or file for enforcement"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_msg = f"Generation failed: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

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

