"""
Test script for newly generated templates.

This script helps verify that new templates are working correctly.
"""

from pathlib import Path
import sys

# Add parent directory to path if running as script
if __name__ == "__main__":
    script_dir = Path(__file__).parent
    parent_dir = script_dir.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))

from pdf_classifier import detect_template


def test_template(pdf_path: Path, expected_template_id: str = None):
    """Test template detection for a PDF file."""
    if not pdf_path.exists():
        print(f"Error: PDF file not found: {pdf_path}")
        return False
    
    print(f"Testing: {pdf_path.name}")
    print("-" * 60)
    
    try:
        template_id, confidence, details = detect_template(pdf_path)
        
        print(f"Detected Template: {template_id}")
        print(f"Confidence: {confidence:.3f}")
        print(f"Visual Score: {details.get('visual_score', 0.0):.3f}")
        print(f"Structure Score: {details.get('structure_score', 0.0):.3f}")
        
        if details.get('warnings'):
            print("\nWarnings:")
            for warning in details['warnings']:
                print(f"  - {warning}")
        
        if details.get('top_candidates'):
            print("\nTop Candidates:")
            for candidate in details['top_candidates'][:3]:
                print(f"  - {candidate['template_id']}: {candidate['score']:.3f}")
        
        # Check if matches expected
        if expected_template_id:
            if template_id == expected_template_id:
                print(f"\n[OK] Correctly identified as {expected_template_id}")
                return True
            else:
                print(f"\n[WARNING] Expected {expected_template_id}, got {template_id}")
                return False
        else:
            if template_id != "unknown_template":
                print(f"\n[OK] Successfully classified as {template_id}")
                return True
            else:
                print(f"\n[WARNING] Classified as unknown_template")
                return False
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Command-line interface."""
    if len(sys.argv) < 2:
        print("Usage: python test_new_template.py <pdf_file> [expected_template_id]")
        print("\nExample:")
        print("  python test_new_template.py unkhown_template/2_1500_9795135703228.pdf template_9")
        sys.exit(1)
    
    pdf_path = Path(sys.argv[1])
    expected_template_id = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = test_template(pdf_path, expected_template_id)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
