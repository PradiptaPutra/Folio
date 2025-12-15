from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import shutil
from pathlib import Path

from utils import WORD_DEFAULTS, txt_to_markdown
from docx_inspector import extract_docx_styles, detect_style_usage
from reference_builder import build_reference_docx

from pandoc_runner import markdown_to_docx
from pydantic import BaseModel
from text_normalizer import normalize_txt_to_markdown


class GenerateRequest(BaseModel):
    reference_name: str
    content: str
    
app = FastAPI()

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


@app.post("/upload")
async def upload_docx(file: UploadFile = File(...)):
    docx_path = UPLOAD_DIR / file.filename

    with docx_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extracted = extract_docx_styles(docx_path)
    raw_styles = extracted["styles"]
    margins = extracted["margins"]

    resolved_styles = {}
    for style_id, style_data in raw_styles.items():
        resolved_styles[style_id] = resolve_style(style_id, raw_styles)
        # Preserve paragraph props if exist
        if "paragraph" in style_data:
             resolved_styles[style_id]["paragraph"] = style_data["paragraph"]

    resolved_styles["margins"] = margins

    # Use the uploaded template directly as reference (preserves original formatting, margins, styles)
    ref_path = REF_DIR / file.filename
    shutil.copy(docx_path, ref_path)

    return {
        "message": "Template extracted",
        "reference_docx": ref_path.name,
        "styles": resolved_styles
    }


@app.post("/generate")
async def generate_docx(
    reference_name: str = Form(...),
    content_file: UploadFile = File(...),
    output_format: str = Form("docx")
):
    # folders
    md_dir = BASE_DIR / "storage" / "markdown"
    out_dir = BASE_DIR / "storage" / "outputs"
    md_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    # paths
    md_path = md_dir / "content.md"
    fmt = output_format.lower().strip()
    if fmt not in {"docx", "doc"}:
        fmt = "docx"
    output_path = out_dir / ("final." + fmt)
    ref_path = REF_DIR / reference_name

    if not ref_path.exists():
        return {"error": "Reference template not found"}

    # read txt content
    raw_text = (await content_file.read()).decode("utf-8")
    markdown = normalize_txt_to_markdown(raw_text)


    md_path.write_text(markdown, encoding="utf-8")

    # retrieve styles from uploaded reference
    # We stored resolved_styles in the upload response, but the server is stateless between calls
    # Ideally, we should re-extract or store them. For now, since we have the ref_path, we can re-extract.
    # But wait, upload endpoint returned them. The frontend might not be sending them back.
    # Better approach: Extract on the fly from the reference docx.
    
    extracted = extract_docx_styles(ref_path)
    # Get Normal style or defaults
    normal_style = extracted["styles"].get("Normal", {})
    paragraph_config = normal_style.get("paragraph", {})
    
    # Detect specific style usage (Chapter heading, body text)
    style_usage = detect_style_usage(str(ref_path))
    
    style_config = {
        "margins": extracted["margins"],
        "paragraph": paragraph_config,
        "mapping": style_usage
    }

    # run pandoc
    try:
        markdown_to_docx(md_path, ref_path, output_path, style_config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {e}")

    return {
        "message": "Document generated",
        "output": output_path.name
    }
