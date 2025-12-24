#!/usr/bin/env python
from pathlib import Path
from engine.analyzer.complete_thesis_builder import create_complete_thesis
import os

def test_simple_reliable():
    """Test with minimal, reliable operations only."""

    # File paths
    template_path = "C:\\Folio\\form-memory\\storage\\references\\Template-skripsi-final-versi2020.docx"
    content_path = "C:\\Folio\\form-memory\\storage\\uploads\\thesis_content.txt"
    output_path = "C:\\Folio\\form-memory\\storage\\outputs\\reliable_test.docx"

    # Check if files exist
    print(f"Template exists: {Path(template_path).exists()}")
    print(f"Content exists: {Path(content_path).exists()}")

    if not Path(template_path).exists():
        print(f"ERROR: Template not found at {template_path}")
        return

    if not Path(content_path).exists():
        print(f"ERROR: Content not found at {content_path}")
        return

    # Get API key (will fail but we have fallbacks)
    api_key = os.getenv('OPENROUTER_API_KEY', 'invalid-key')
    print(f"API key present: {api_key != 'invalid-key'}")

    # Test with minimal AI usage
    print("\n=== TESTING RELIABLE MODE ===")
    result = create_complete_thesis(
        template_path=template_path,
        content_path=content_path,
        output_path=output_path,
        use_ai=False,  # Disable AI to avoid API issues
        api_key=None,  # No API key
        user_data={
            "title": "Sistem Informasi Akademik Berbasis Web",
            "author": "Test Student",
            "supervisor": "Dr. Test Supervisor",
            "year": "2024"
        }
    )

    print("Result:", result)
    if result['status'] == 'success':
        output_file = Path(result['output_file'])
        print(f"Output file size: {output_file.stat().st_size} bytes")
        print(f"Output file exists: {output_file.exists()}")

if __name__ == '__main__':
    test_simple_reliable()