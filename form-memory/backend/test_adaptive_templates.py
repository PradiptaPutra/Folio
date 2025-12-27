"""
Test script to demonstrate the adaptive template system working with different templates.
"""

from pathlib import Path
from engine.analyzer.intelligent_template_adapter import IntelligentTemplateAdapter

# Test both templates
templates = [
    (r"C:\Folio\form-memory\storage\references\Template-TA-UI.docx", "Template-TA-UI"),
    (r"C:\Folio\form-memory\storage\references\Template-skripsi-final-versi2020.docx", "Template-skripsi-final-versi2020")
]

print("=" * 80)
print("ADAPTIVE TEMPLATE SYSTEM TEST")
print("=" * 80)

for template_path, template_name in templates:
    if not Path(template_path).exists():
        print(f"\n[SKIP] Template not found: {template_path}")
        continue
    
    print(f"\n{'='*80}")
    print(f"Testing: {template_name}")
    print(f"{'='*80}")
    
    try:
        adapter = IntelligentTemplateAdapter(template_path)
        structure = adapter.analyze_template()
        
        print(f"\n[OK] Analysis Complete!")
        print(f"  - Template Type: {structure.template_type}")
        print(f"  - Chapters Found: {len(structure.chapter_patterns)}")
        print(f"  - Subsections Found: {len(structure.subsection_patterns)}")
        print(f"  - Placeholders Found: {len(structure.placeholder_patterns)}")
        print(f"  - Content Zones Found: {len(structure.content_zones)}")
        
        if structure.chapter_patterns:
            print(f"\n  Chapter Details:")
            for ch in structure.chapter_patterns[:5]:
                print(f"    - Chapter {ch.metadata.get('chapter_num')}: {ch.text[:50]} (confidence: {ch.confidence:.2f})")
        
        if structure.subsection_patterns:
            print(f"\n  Subsection Details (first 5):")
            for sub in structure.subsection_patterns[:5]:
                print(f"    - {sub.metadata.get('full_number', 'N/A')}: {sub.text[:50]} (confidence: {sub.confidence:.2f})")
        
        if structure.style_mapping:
            print(f"\n  Style Mapping:")
            for key, value in structure.style_mapping.items():
                print(f"    - {key}: {value}")
        
        if structure.font_info:
            print(f"\n  Font Info:")
            for key, value in structure.font_info.items():
                print(f"    - {key}: {value.get('name', 'N/A')} ({value.get('size', 'N/A')})")
        
        # Test insertion points
        print(f"\n  Insertion Points Test:")
        for chapter_num in [1, 2, 3]:
            points = adapter.get_content_insertion_points(chapter_num)
            print(f"    - Chapter {chapter_num}: {len(points)} insertion points found")
            if points:
                for idx, (para_idx, meta) in enumerate(points[:2]):
                    print(f"      Point {idx+1}: para {para_idx}, type: {meta.get('type')}, text: {meta.get('text', '')[:40]}")
        
    except Exception as e:
        print(f"\n[ERROR] Error analyzing {template_name}: {e}")
        import traceback
        traceback.print_exc()

print(f"\n{'='*80}")
print("TEST COMPLETE")
print(f"{'='*80}")

