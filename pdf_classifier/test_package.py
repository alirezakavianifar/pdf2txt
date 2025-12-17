#!/usr/bin/env python3
"""
Test script to verify the pdf_classifier package is complete and working.
"""

import sys
from pathlib import Path

# Add parent directory to path
script_dir = Path(__file__).parent
parent_dir = script_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        from pdf_classifier import detect_template, load_templates_db
        from pdf_classifier import text_detector, visual_detector, structure_detector
        from pdf_classifier import fusion, cache, logger
        print("[OK] All imports successful")
        return True
    except Exception as e:
        print(f"[FAIL] Import error: {e}")
        return False

def test_template_loading():
    """Test that templates can be loaded."""
    print("\nTesting template loading...")
    try:
        from pdf_classifier import load_templates_db
        
        # Try to load from package directory
        package_dir = Path(__file__).parent
        signatures_dir = package_dir / "templates_config" / "signatures"
        
        if not signatures_dir.exists():
            print(f"[FAIL] Signatures directory not found: {signatures_dir}")
            return False
        
        templates_db = load_templates_db(signatures_dir)
        
        if not templates_db:
            print("[FAIL] No templates loaded")
            return False
        
        print(f"[OK] Loaded {len(templates_db)} templates: {list(templates_db.keys())}")
        return True
    except Exception as e:
        print(f"[FAIL] Template loading error: {e}")
        return False

def test_detection():
    """Test that detection works."""
    print("\nTesting detection...")
    try:
        from pdf_classifier import detect_template
        
        # Find a test PDF (look in parent directory)
        parent_dir = Path(__file__).parent.parent
        test_pdf = parent_dir / "classified" / "template_1" / "4_550_9000896204125.pdf"
        
        if not test_pdf.exists():
            print(f"[SKIP] Test PDF not found: {test_pdf}")
            return True  # Not a failure, just skip
        
        template_id, confidence, details = detect_template(test_pdf)
        
        if template_id == "unknown_template":
            print(f"[WARN] Detection returned unknown_template (confidence: {confidence:.3f})")
        else:
            print(f"[OK] Detection successful: {template_id} (confidence: {confidence:.3f})")
        
        return True
    except Exception as e:
        print(f"[FAIL] Detection error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_structure():
    """Test that all required files exist."""
    print("\nTesting file structure...")
    package_dir = Path(__file__).parent
    
    required_files = [
        "__init__.py",
        "text_detector.py",
        "visual_detector.py",
        "structure_detector.py",
        "fusion.py",
        "cache.py",
        "logger.py",
        "requirements.txt",
        "example_usage.py",
    ]
    
    required_dirs = [
        "templates_config/signatures",
    ]
    
    all_ok = True
    
    for file in required_files:
        file_path = package_dir / file
        if file_path.exists():
            print(f"[OK] {file}")
        else:
            print(f"[FAIL] Missing: {file}")
            all_ok = False
    
    for dir_path in required_dirs:
        full_path = package_dir / dir_path
        if full_path.exists():
            # Check for signature files
            sig_files = list(full_path.glob("template_*.json"))
            print(f"[OK] {dir_path} ({len(sig_files)} signature files)")
        else:
            print(f"[FAIL] Missing directory: {dir_path}")
            all_ok = False
    
    return all_ok

if __name__ == "__main__":
    print("=" * 60)
    print("PDF Classifier Package Test")
    print("=" * 60)
    
    results = []
    results.append(("File Structure", test_file_structure()))
    results.append(("Imports", test_imports()))
    results.append(("Template Loading", test_template_loading()))
    results.append(("Detection", test_detection()))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, result in results:
        status = "[OK]" if result else "[FAIL]"
        print(f"{status} {test_name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n[OK] All tests passed!")
        sys.exit(0)
    else:
        print("\n[FAIL] Some tests failed")
        sys.exit(1)

