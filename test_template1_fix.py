"""
Test script to verify Template 1 Kambari and consumption table fix.
Randomly selects PDFs from template1, identifies template_1 PDFs, and tests extraction.
"""
import json
import random
from pathlib import Path
from pdf_classifier import detect_template
from run_complete_pipeline import run_pipeline


def find_template1_pdfs(template1_dir: Path, max_check: int = 20) -> list[Path]:
    """Find PDFs in template1 directory and identify which are template_1."""
    if not template1_dir.exists():
        print(f"ERROR: {template1_dir} does not exist")
        return []
    
    # Get all PDFs
    all_pdfs = list(template1_dir.glob("*.pdf"))
    if not all_pdfs:
        print(f"No PDFs found in {template1_dir}")
        return []
    
    print(f"Found {len(all_pdfs)} PDF(s) in {template1_dir}")
    
    # Randomly sample up to max_check PDFs
    sample_size = min(max_check, len(all_pdfs))
    sampled_pdfs = random.sample(all_pdfs, sample_size)
    
    print(f"\nChecking {sample_size} randomly selected PDF(s) for template_1...")
    
    template1_pdfs = []
    for pdf_path in sampled_pdfs:
        try:
            template_id, confidence, details = detect_template(pdf_path)
            print(f"  {pdf_path.name}: {template_id} (confidence: {confidence:.2f})")
            if template_id in ["template_1", "template1"]:
                template1_pdfs.append(pdf_path)
        except Exception as e:
            print(f"  {pdf_path.name}: ERROR - {e}")
    
    print(f"\nFound {len(template1_pdfs)} template_1 PDF(s)")
    return template1_pdfs


def check_consumption_history_extraction(output_dir: Path, pdf_name: str) -> dict:
    """Check if consumption history was extracted correctly, including کم باری."""
    results = {
        "pdf": pdf_name,
        "has_consumption_history": False,
        "has_kambari": False,
        "row_count": 0,
        "kambari_values": [],
        "table_count": None,
        "raw_json_exists": False
    }
    
    # Check raw extraction JSON
    raw_json_path = output_dir / f"{pdf_name}_consumption_history_section.json"
    if raw_json_path.exists():
        results["raw_json_exists"] = True
        try:
            with open(raw_json_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
                # Check how many tables were detected (if available in metadata)
                if 'table' in raw_data:
                    table_data = raw_data['table']
                    if 'row_count' in table_data:
                        results["table_count"] = table_data.get('row_count', 0)
        except Exception as e:
            print(f"    Warning: Could not read raw JSON: {e}")
    
    # Check restructured JSON
    restructured_json_path = output_dir / f"{pdf_name}_consumption_history_section_restructured.json"
    if not restructured_json_path.exists():
        return results
    
    try:
        with open(restructured_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        consumption_history = data.get("سوابق مصرف و مبلغ", [])
        if consumption_history:
            results["has_consumption_history"] = True
            results["row_count"] = len(consumption_history)
            
            # Check for کم باری in each row
            for row in consumption_history:
                if "کم باری" in row and row["کم باری"] is not None:
                    results["has_kambari"] = True
                    results["kambari_values"].append(row["کم باری"])
    
    except Exception as e:
        print(f"    Error reading restructured JSON: {e}")
    
    return results


def test_template1_extraction(pdf_paths: list[Path], test_count: int = 5):
    """Test extraction on template_1 PDFs."""
    if not pdf_paths:
        print("No template_1 PDFs to test")
        return
    
    # Test up to test_count PDFs
    test_pdfs = pdf_paths[:test_count]
    print(f"\n{'='*70}")
    print(f"Testing extraction on {len(test_pdfs)} template_1 PDF(s)")
    print(f"{'='*70}\n")
    
    results = []
    for i, pdf_path in enumerate(test_pdfs, 1):
        print(f"[{i}/{len(test_pdfs)}] Processing {pdf_path.name}...")
        
        try:
            # Run pipeline
            merged_data = run_pipeline(str(pdf_path), export_excel=False)
            
            # Check consumption history extraction
            output_dir = Path("output") / pdf_path.stem
            check_result = check_consumption_history_extraction(output_dir, pdf_path.stem)
            results.append(check_result)
            
            # Print summary
            print(f"  [OK] Consumption history: {check_result['row_count']} rows")
            print(f"  [OK] کم باری present: {check_result['has_kambari']}")
            if check_result['kambari_values']:
                print(f"  [OK] کم باری values: {check_result['kambari_values']}")
            else:
                print(f"  [FAIL] کم باری missing!")
            
        except Exception as e:
            print(f"  [ERROR] {e}")
            import traceback
            traceback.print_exc()
            results.append({
                "pdf": pdf_path.name,
                "error": str(e)
            })
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    
    successful = [r for r in results if r.get("has_consumption_history") and not r.get("error")]
    with_kambari = [r for r in successful if r.get("has_kambari")]
    
    print(f"Total tested: {len(results)}")
    print(f"Successfully extracted consumption history: {len(successful)}")
    print(f"With کم باری present: {len(with_kambari)}")
    
    if len(with_kambari) < len(successful):
        print(f"\n⚠ WARNING: {len(successful) - len(with_kambari)} PDF(s) missing کم باری")
        for r in successful:
            if not r.get("has_kambari"):
                print(f"  - {r['pdf']}: {r['row_count']} rows but no کم باری")
    
    if len(with_kambari) == len(successful) and len(successful) > 0:
        print(f"\n[SUCCESS] All {len(successful)} PDF(s) have کم باری extracted correctly!")


if __name__ == "__main__":
    template1_dir = Path("template1")
    
    # Find template_1 PDFs
    template1_pdfs = find_template1_pdfs(template1_dir, max_check=20)
    
    if template1_pdfs:
        # Test extraction on them
        test_template1_extraction(template1_pdfs, test_count=min(5, len(template1_pdfs)))
    else:
        print("\nNo template_1 PDFs found to test")
