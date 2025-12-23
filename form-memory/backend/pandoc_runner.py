import subprocess
from pathlib import Path
from docx import Document
import shutil


def markdown_to_docx(md_path, ref_path, output_path, style_config=None, frontmatter_data=None):
    # Ensure pandoc exists
    pandoc_exe = shutil.which("pandoc")
    if not pandoc_exe:
        raise RuntimeError("Pandoc is not installed or not in PATH.")

    out_path = Path(output_path)
    
    try:
        # Step 1: Generate base DOCX from markdown using pandoc
        print(f"Generating DOCX from markdown...")
        subprocess.run([
            pandoc_exe,
            str(md_path),
            "--from", "markdown+header_attributes",
            "--reference-doc", str(ref_path),
            "-o", str(out_path)
        ], check=True, timeout=120)
        
        if not out_path.exists():
            raise RuntimeError("Pandoc failed to generate output file")
        print(f"✓ Pandoc generated: {out_path}")
        
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Pandoc conversion failed: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Document generation failed: {str(e)}")

    # Step 2: Verify document is valid
    try:
        test_doc = Document(str(out_path))
        print(f"✓ Document is valid ({len(test_doc.paragraphs)} paragraphs)")
    except Exception as e:
        print(f"ERROR: Generated document is corrupted: {str(e)}")
        raise RuntimeError(f"Generated document is corrupted: {str(e)}")

    # Final verification
    if not Path(output_path).exists():
        raise RuntimeError(f"Output file not found: {output_path}")
    
    print(f"✓ Document ready: {output_path}")