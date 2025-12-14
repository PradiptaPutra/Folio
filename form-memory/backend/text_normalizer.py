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
        if re.match(r"^BAB\s+[IVXLC]+\s*[-—]\s*.+$", line, re.IGNORECASE):
            bab, title = re.split(r"[-—]", line, maxsplit=1)
            md.append(f"# {bab.strip().upper()}")
            md.append(title.strip())
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
