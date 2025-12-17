#!/usr/bin/env python3
"""
Example usage of the PDF Template Classifier

This script demonstrates how to use the pdf_classifier module
to classify PDFs by template.
"""

from pathlib import Path
import sys
import os

# Add parent directory to path if running as script
if __name__ == "__main__":
    script_dir = Path(__file__).parent
    parent_dir = script_dir.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))

from pdf_classifier import detect_template, load_templates_db


def classify_single_pdf(pdf_path: str):
    """Classify a single PDF file."""
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        print(f"[ERROR] PDF file not found: {pdf_path}")
        return
    
    print(f"Classifying: {pdf_path.name}")
    print("-" * 60)
    
    # Detect template
    template_id, confidence, details = detect_template(
        pdf_path,
        confidence_threshold=0.5
    )
    
    # Display results
    print(f"Template ID: {template_id}")
    print(f"Confidence: {confidence:.3f}")
    print(f"Visual Score: {details.get('visual_score', 0.0):.3f}")
    print(f"Structure Score: {details.get('structure_score', 0.0):.3f}")
    
    if details.get('warnings'):
        print("\nWarnings:")
        for warning in details['warnings']:
            print(f"  - {warning}")
    
    if details.get('top_candidates'):
        print("\nTop Candidates:")
        for candidate in details['top_candidates']:
            print(f"  - {candidate['template_id']}: {candidate['score']:.3f}")
    
    print()


def classify_multiple_pdfs(pdf_directory: str):
    """Classify all PDFs in a directory."""
    pdf_dir = Path(pdf_directory)
    
    if not pdf_dir.exists():
        print(f"[ERROR] Directory not found: {pdf_dir}")
        return
    
    # Find all PDFs
    pdf_files = sorted(pdf_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"[WARN] No PDF files found in {pdf_dir}")
        return
    
    print(f"Found {len(pdf_files)} PDF(s) to classify\n")
    
    # Load templates once for efficiency
    templates_db = load_templates_db()
    
    results = []
    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"[{i}/{len(pdf_files)}] Processing {pdf_path.name}...", end=" ")
        
        try:
            template_id, confidence, details = detect_template(
                pdf_path,
                templates_db=templates_db,  # Reuse loaded templates
                confidence_threshold=0.5
            )
            
            results.append({
                "pdf": pdf_path.name,
                "template_id": template_id,
                "confidence": confidence
            })
            
            status = "[OK]" if template_id != "unknown_template" else "[UNKNOWN]"
            print(f"{status} -> {template_id} (confidence: {confidence:.3f})")
            
        except Exception as e:
            print(f"[ERROR] {e}")
            results.append({
                "pdf": pdf_path.name,
                "template_id": "error",
                "confidence": 0.0,
                "error": str(e)
            })
    
    # Summary
    print("\n" + "=" * 60)
    print("Classification Summary")
    print("=" * 60)
    
    from collections import Counter
    template_counts = Counter(r["template_id"] for r in results)
    
    for template_id, count in template_counts.most_common():
        print(f"{template_id}: {count}")
    
    print(f"\nTotal: {len(results)} PDF(s)")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python example_usage.py <pdf_file>")
        print("  python example_usage.py <pdf_directory>")
        print()
        print("Examples:")
        print("  python example_usage.py document.pdf")
        print("  python example_usage.py ./pdfs/")
        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    
    if input_path.is_file() and input_path.suffix.lower() == '.pdf':
        classify_single_pdf(input_path)
    elif input_path.is_dir():
        classify_multiple_pdfs(input_path)
    else:
        print(f"[ERROR] Invalid input: {input_path}")
        print("Please provide either a PDF file or a directory containing PDFs.")
        sys.exit(1)

