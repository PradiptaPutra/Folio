import subprocess
from pathlib import Path
from docx import Document
from skripsi_formatter import enforce_skripsi_format
from skripsi_enforcer import SkripsiEnforcer
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

    # Step 3: Apply formatting (skip if it causes issues)
    try:
        print("Applying formatting...")
        # Only call skripsi_format - skip TOC insertion as it can corrupt
        enforce_skripsi_format(str(out_path), style_config)
        print("✓ Formatting applied")
    except Exception as e:
        print(f"Warning: Could not apply formatting: {e}")
        # Don't fail - the document is still usable without perfect formatting

    # Step 4: Generate Front Matter if requested
    if frontmatter_data:
        try:
            print("Generating front matter...")
            enforcer = SkripsiEnforcer(str(out_path))
            enforcer.execute_phase_4(**frontmatter_data)
            enforcer.save()
            print("✓ Front matter added")
        except Exception as e:
            print(f"Warning: Could not add front matter: {e}")
            # Don't fail - the document is still usable without front matter

    # Final verification
    if not Path(output_path).exists():
        raise RuntimeError(f"Output file not found: {output_path}")
    
    print(f"✓ Document ready: {output_path}")