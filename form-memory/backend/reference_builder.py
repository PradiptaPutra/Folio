import subprocess
import zipfile
from lxml import etree
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def build_reference_docx(styles, output_path):
    scaffold = BASE_DIR / "templates" / "scaffold.md"

    temp_docx = output_path.with_suffix(".tmp.docx")

    result = subprocess.run(
        [
            "pandoc",
            str(scaffold),
            "-o",
            str(temp_docx)
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Pandoc failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )


    with zipfile.ZipFile(temp_docx) as zin:
        with zipfile.ZipFile(output_path, "w") as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)

                if item.filename == "word/styles.xml":
                    data = _inject_styles(data, styles)

                if item.filename == "word/document.xml":
                    data = _inject_margins(data, styles["margins"])

                zout.writestr(item, data)

    temp_docx.unlink()


def _inject_styles(styles_xml, styles):
    root = etree.XML(styles_xml)
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

    for style in root.findall(".//w:style", ns):
        style_id = style.get("{%s}styleId" % ns["w"])
        if style_id in styles:
            rpr = style.find(".//w:rPr", ns)
            if rpr is None:
                continue

            sz = rpr.find(".//w:sz", ns)
            if sz is not None and styles[style_id]["size"]:
                sz.set("{%s}val" % ns["w"], str(int(styles[style_id]["size"] * 2)))

    return etree.tostring(root, xml_declaration=True, encoding="UTF-8")


def _inject_margins(document_xml, margins):
    root = etree.XML(document_xml)
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

    pgMar = root.find(".//w:pgMar", ns)
    if pgMar is not None:
        for side in ["top", "bottom", "left", "right"]:
            pgMar.set("{%s}%s" % (ns["w"], side), margins[side])

    return etree.tostring(root, xml_declaration=True, encoding="UTF-8")
