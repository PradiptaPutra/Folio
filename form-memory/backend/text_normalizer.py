import re



def normalize_txt_to_markdown(text: str) -> str:
    lines = text.splitlines()
    md = []
    
    # Regex patterns
    # Manual numbering to strip: "1.1 ", "1.2.3 ", "A. ", "1. "
    # We strip it so Word can handle numbering automatically via styles
    re_strip_start = re.compile(r"^(\d+(\.\d+)*\.?|[A-Z]\.|[IVX]+\.)\s+")
    
    for raw in lines:
        line = raw.strip()
        
        if not line:
            md.append("")
            continue
            
        # 1. Detect BAB (Chapter)
        # Matches: BAB I, BAB 1, BAB I PENDAHULUAN (merged)
        if re.match(r"^BAB\s+[IVX\d]+", line, re.IGNORECASE):
            # Normalize to UPPERCASE
            # If it has a dash or is merged, split it
            if re.search(r"[-—]", line):
                parts = re.split(r"[-—]", line, maxsplit=1)
                bab_part = parts[0].strip().upper()
                title_part = parts[1].strip().upper() # BAB titles usually UPPER
                md.append(f"# {bab_part}  \n{title_part}")
            else:
                # Check if it's just "BAB I" or "BAB I PENDAHULUAN"
                # If it's a long line, it might be "BAB I TITLE"
                # We want to force a break if possible, but if not, just H1
                md.append(f"# {line.upper()}")
            continue

        # 2. Strip standard manual numbering for analysis
        clean_text = re_strip_start.sub("", line).strip()
        
        # 3. Detect Heading 2 (Subbab)
        # Heuristic: Title Case, clean text length > 3, and was likely numbered or looks like a title
        # "Latar Belakang", "Rumusan Masalah"
        # If the original had "1.1", it definitely is a heading
        was_numbered = re_strip_start.match(line)
        is_title_case = clean_text.istitle() or (clean_text[0].isupper() and " " in clean_text)
        
        if was_numbered and is_title_case:
             md.append(f"## {clean_text}")
             continue
             
        # Detect common un-numbered subbabs by keyword
        if clean_text.lower() in ["latar belakang", "rumusan masalah", "tujuan penelitian", "manfaat penelitian"]:
            md.append(f"## {clean_text.title()}")
            continue

        # 4. Standard paragraphs
        # If it was numbered but didn't look like a title, maybe it's a list?
        # For skripsi, usually "1. " is a list.
        # But we want to avoid accidental H1/H2.
        
        # Output as paragraph, let styles handle indentation
        md.append(line)

    return "\n\n".join(md)
