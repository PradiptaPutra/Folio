"""
Test zone detection to verify front matter vs main content identification.
"""

from pathlib import Path
from engine.analyzer.intelligent_template_adapter import IntelligentTemplateAdapter

templates = [
    (r"C:\Folio\form-memory\storage\references\Template-TA-UI.docx", "Template-TA-UI"),
    (r"C:\Folio\form-memory\storage\references\Template-skripsi-final-versi2020.docx", "Template-skripsi-final-versi2020")
]

for template_path, name in templates:
    if not Path(template_path).exists():
        print(f"[SKIP] {name} not found")
        continue
    
    print(f"\n{'='*80}")
    print(f"Testing: {name}")
    print(f"{'='*80}")
    
    try:
        adapter = IntelligentTemplateAdapter(template_path)
        structure = adapter.analyze_template()
        
        zones = adapter._document_zones
        print(f"\n[ZONES]")
        print(f"  Front matter ends at: {zones.get('front_matter_end', 'Unknown')}")
        print(f"  Main content starts at: {zones.get('main_content_start', 'Unknown')}")
        print(f"  Back matter starts at: {zones.get('back_matter_start', 'Unknown')}")
        
        if zones.get('main_content_start'):
            main_start = zones['main_content_start']
            print(f"\n[VERIFICATION]")
            print(f"  First 3 paragraphs in main content area:")
            for i in range(main_start, min(main_start + 3, len(adapter.doc.paragraphs))):
                para = adapter.doc.paragraphs[i]
                text = para.text.strip()[:60]
                print(f"    Para {i}: {text}")
            
            print(f"\n  Last 3 paragraphs before main content (should be front matter):")
            for i in range(max(0, main_start - 3), main_start):
                para = adapter.doc.paragraphs[i]
                text = para.text.strip()[:60]
                print(f"    Para {i}: {text}")
        
        print(f"\n[FILTERED PATTERNS]")
        print(f"  Chapters (after filtering): {len(structure.chapter_patterns)}")
        print(f"  Subsections (after filtering): {len(structure.subsection_patterns)}")
        print(f"  Placeholders (after filtering): {len(structure.placeholder_patterns)}")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

