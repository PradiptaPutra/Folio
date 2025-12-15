import re


def normalize_txt_to_markdown(text: str) -> str:
    lines = text.splitlines()
    md = []

    for raw in lines:
        line = raw.strip()

        if not line:
            md.append("")
            continue

        # BAB I — Pendahuluan / BAB I - Pendahuluan
        # Requirement: Only 'BAB <Roman>' becomes Heading 1; the title stays plain text
        # BAB I — Pendahuluan / BAB I - Pendahuluan
        # Requirement: Merge into one heading with line break so both get the Chapter Heading style.
        if re.match(r"^BAB\s+[IVXLC]+\s*[-—]\s*.+$", line, re.IGNORECASE):
            bab, title = re.split(r"[-—]", line, maxsplit=1)
            # Use two spaces at end of line for hard line break in Markdown
            md.append(f"# {bab.strip().upper()}  \n{title.strip()}")
            continue

        # BAB I (tanpa judul)
        if re.match(r"^BAB\s+[IVXLC]+$", line, re.IGNORECASE):
            md.append(f"# {line.upper()}")
            continue

        # Subbab utama (Latar Belakang, Metode Penelitian, dll) → Heading 2
        # Title Case words (at least two words)
        if re.match(r"^[A-Z][a-z]+(\s[A-Z][a-z]+)+$", line):
            md.append(f"## {line}")
            continue

        # A. / B.
        if re.match(r"^[A-Z]\.\s+", line):
            md.append(f"### {line}")
            continue

        # 1. / 2.
        if re.match(r"^\d+\.\s+", line):
            md.append(f"#### {line}")
            continue

        md.append(line)

    return "\n\n".join(md)
