"""
Analyze the output document to identify formatting errors.
"""

from docx import Document
import re

output_path = r"C:\Folio\form-memory\storage\outputs\Skripsi_Redify.docx"
doc = Document(output_path)

print("=" * 80)
print("OUTPUT DOCUMENT ERROR ANALYSIS")
print("=" * 80)

issues = []

# Check for problematic text patterns
for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()
    
    # Check for "Disusun Oleh:" in wrong place
    if "Disusun Oleh:" in text and i > 50:  # Not in front matter
        issues.append(f"Line {i}: 'Disusun Oleh:' found in main content")
    
    # Check for subsections with missing chapter numbers
    if re.match(r'^\.\d+', text):  # Starts with .1, .2, etc.
        issues.append(f"Line {i}: Subsection missing chapter number: '{text[:50]}'")
    
    # Check for empty subsections
    if re.match(r'^\d+\.\d+', text) and len(text) < 30:
        next_para_idx = i + 1
        if next_para_idx < len(doc.paragraphs):
            next_text = doc.paragraphs[next_para_idx].text.strip()
            # If next paragraph is also a subsection or BAB, this one is empty
            if re.match(r'^\d+\.\d+', next_text) or re.match(r'^BAB', next_text, re.I):
                issues.append(f"Line {i}: Empty subsection: '{text}'")
    
    # Check for misplaced BAB headings
    if re.match(r'^BAB\s+[IVX]', text, re.I):
        # Check if it's in the middle of content (not at start of chapter)
        if i > 0:
            prev_text = doc.paragraphs[i-1].text.strip()
            if not re.match(r'^\d+\.\d+', prev_text) and len(prev_text) > 10:
                issues.append(f"Line {i}: BAB heading may be misplaced: '{text}'")
    
    # Check for metadata at end
    if i > len(doc.paragraphs) - 5:
        if re.match(r'^\d{8}', text) or "Informatika" in text or "94523999" in text:
            issues.append(f"Line {i}: Metadata found in content: '{text[:50]}'")

print(f"\nFound {len(issues)} issues:\n")
for issue in issues:
    print(f"  [X] {issue}")

# Check subsection structure
print("\n" + "=" * 80)
print("SUBSECTION STRUCTURE ANALYSIS")
print("=" * 80)

subsections = []
for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()
    if re.match(r'^\d+\.\d+', text):
        subsections.append((i, text[:60]))

print(f"\nFound {len(subsections)} subsections:")
for idx, (line_num, text) in enumerate(subsections, 1):
    print(f"  {idx}. Line {line_num}: {text}")

# Check for missing chapter numbers
print("\nChecking for subsections with missing chapter numbers:")
for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()
    if re.match(r'^\.\d+', text):  # Starts with .1, .2, etc. (missing chapter)
        print(f"  [X] Line {i}: Missing chapter number: '{text[:50]}'")

print("\n" + "=" * 80)

