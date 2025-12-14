import zipfile
from lxml import etree

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def extract_docx_styles(docx_path):
    styles = {}
    margins = {}

    with zipfile.ZipFile(docx_path) as docx:
        styles_xml = docx.read("word/styles.xml")
        document_xml = docx.read("word/document.xml")

    # ---------- STYLES ----------
    root = etree.XML(styles_xml)

    for style in root.findall(".//w:style", NS):
        style_id = style.get("{%s}styleId" % NS["w"])
        if not style_id:
            continue

        based_on = None
        based = style.find("w:basedOn", NS)
        if based is not None:
            based_on = based.get("{%s}val" % NS["w"])

        font = None
        size = None

        rpr = style.find("w:rPr", NS)
        if rpr is not None:
            sz = rpr.find("w:sz", NS)
            if sz is not None:
                size = int(sz.get("{%s}val" % NS["w"])) / 2

            rfonts = rpr.find("w:rFonts", NS)
            if rfonts is not None:
                font = rfonts.get("{%s}ascii" % NS["w"])

        styles[style_id] = {
            "font": font,
            "size": size,
            "based_on": based_on
        }

    # ---------- MARGINS ----------
    doc_root = etree.XML(document_xml)
    sect = doc_root.find(".//w:sectPr", NS)

    if sect is not None:
        pg_mar = sect.find("w:pgMar", NS)
        if pg_mar is not None:
            margins = {
                "top": pg_mar.get("{%s}top" % NS["w"]),
                "bottom": pg_mar.get("{%s}bottom" % NS["w"]),
                "left": pg_mar.get("{%s}left" % NS["w"]),
                "right": pg_mar.get("{%s}right" % NS["w"]),
            }

    return {
        "styles": styles,
        "margins": margins
    }
