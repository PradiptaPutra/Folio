import subprocess
from pathlib import Path
from toc_inserter import insert_toc
from skripsi_formatter import enforce_skripsi_format
import shutil
import shutil as _shutil


def markdown_to_docx(md_path, ref_path, output_path, style_config=None):
    # Ensure pandoc exists
    pandoc_exe = shutil.which("pandoc")
    if not pandoc_exe:
        raise RuntimeError("Pandoc is not installed or not in PATH.")

    out_path = Path(output_path)
    # Always generate via Pandoc to a .docx first; .doc needs conversion
    primary_docx = out_path if out_path.suffix.lower() == ".docx" else out_path.with_suffix(".docx")

    subprocess.run([
        pandoc_exe,
        str(md_path),
        "--from", "markdown+header_attributes",
        "--reference-doc", str(ref_path),
        "-o", str(primary_docx)
    ], check=True, timeout=120)

    # ✅ Fix heading styles and insert TOC on the .docx
    insert_toc(primary_docx)
    
    # ✅ Enforce skripsi formatting (spacing, indent, numbering, margins)
    enforce_skripsi_format(primary_docx, style_config)

    # ✅ If requested output is legacy .doc, convert from .docx
    if out_path.suffix.lower() == ".doc":
        tmp_docx = primary_docx

        # Try LibreOffice headless conversion to .doc
        soffice = _shutil.which("soffice") or _shutil.which("libreoffice")
        if not soffice:
            # Try common Windows install paths
            possible_paths = [
                Path("C:/Program Files/LibreOffice/program/soffice.exe"),
                Path("C:/Program Files (x86)/LibreOffice/program/soffice.exe"),
                Path("C:/Program Files/LibreOffice/program/soffice.com"),
                Path("C:/Program Files (x86)/LibreOffice/program/soffice.com"),
            ]
            for p in possible_paths:
                if p.exists():
                    soffice = str(p)
                    break
        if soffice:
            subprocess.run([
                soffice,
                "--headless",
                "--convert-to", "doc",
                "--outdir", str(out_path.parent),
                str(tmp_docx)
            ], check=True, timeout=120)
        else:
            # Fallback: convert to RTF (opens in Word) using pandoc
            tmp_rtf = out_path.with_suffix(".rtf")
            subprocess.run([
                pandoc_exe,
                str(tmp_docx),
                "-o", str(tmp_rtf)
            ], check=True, timeout=60)
            # Rename RTF to requested .doc name for compatibility
            if out_path.exists():
                out_path.unlink()
            tmp_rtf.rename(out_path)

        # Verify conversion result exists
        if not out_path.exists():
            raise RuntimeError(".doc conversion failed. Install LibreOffice for native .doc or use output_format=docx.")
    else:
        # If target is .docx, ensure final file is at requested path
        if primary_docx != out_path:
            # Move/rename formatted .docx to desired name
            if out_path.exists():
                out_path.unlink()
            primary_docx.rename(out_path)

    # Final sanity check
    if not Path(output_path).exists():
        raise RuntimeError(f"Output file not found: {output_path}")