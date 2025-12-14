WORD_DEFAULTS = {
    "font": "Times New Roman",
    "size": 12.0
}

def txt_to_markdown(text: str) -> str:
    lines = text.splitlines()
    md_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            md_lines.append("")
            continue

        # detect BAB
        if line.startswith("BAB "):
            md_lines.append(f"# {line}")
        # detect sub section
        elif line.isupper() and len(line) < 80:
            md_lines.append(f"## {line}")
        else:
            md_lines.append(line)

    return "\n\n".join(md_lines)
