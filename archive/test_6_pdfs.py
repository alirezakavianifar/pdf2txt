"""
Test improved extraction on 6 Template 2 PDFs.
"""

import json
from pathlib import Path
from run_complete_pipeline import run_pipeline

# Test PDFs
test_pdfs = [
    "template_2/2.pdf",
    "template_2/2_2.pdf",
    "template_2/3_1000_7001523101422.pdf",
    "template_2/3_1200_7005274901427.pdf",
    "template_2/3_1500_7003340001421.pdf",
    "template_2/4_1200_7000895201427.pdf"
]

print("=" * 70)
print("Testing Improved Template 2 Extraction on 6 PDFs")
print("=" * 70)

results = {}

for pdf_path in test_pdfs:
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        print(f"\n[SKIP] {pdf_file.name} - File not found")
        continue
    
    print(f"\n{'='*70}")
    print(f"Processing: {pdf_file.name}")
    print(f"{'='*70}")
    
    try:
        # Run pipeline
        run_pipeline(str(pdf_file))
        
        # Check results
        output_file = Path("output") / f"{pdf_file.stem}_final_pipeline.json"
        if output_file.exists():
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Analyze bill_summary extraction
            # Try different possible structures
            bill_summary = {}
            if "bill_summary_section" in data:
                bill_summary = data["bill_summary_section"].get("خلاصه صورتحساب", {})
            elif "خلاصه صورتحساب" in data:
                bill_summary = data["خلاصه صورتحساب"]
            else:
                # Check all keys for bill summary
                for key in data.keys():
                    if "خلاصه" in key or "صورتحساب" in key:
                        if isinstance(data[key], dict):
                            bill_summary = data[key]
                            break
            
            extracted = sum(1 for v in bill_summary.values() if v is not None) if bill_summary else 0
            total = len(bill_summary) if bill_summary else 0
            
            results[pdf_file.name] = {
                "status": "success",
                "bill_summary": {
                    "extracted": extracted,
                    "total": total,
                    "percentage": (extracted / total * 100) if total > 0 else 0,
                    "fields": bill_summary
                }
            }
            
            print(f"\n[OK] {pdf_file.name}")
            percentage = (extracted / total * 100) if total > 0 else 0
            print(f"  Bill Summary: {extracted}/{total} fields ({percentage:.1f}%)")
            
            # Show extracted fields (limit to avoid encoding issues)
            extracted_fields = [k for k, v in bill_summary.items() if v is not None]
            if extracted_fields:
                print(f"  Extracted: {len(extracted_fields)} fields")
            
            # Show missing fields
            missing_fields = [k for k, v in bill_summary.items() if v is None]
            if missing_fields:
                print(f"  Missing: {len(missing_fields)} fields")
        else:
            print(f"[ERROR] Output file not found: {output_file.name}")
            results[pdf_file.name] = {"status": "error", "error": "Output not found"}
            
    except Exception as e:
        print(f"[ERROR] {pdf_file.name}: {e}")
        results[pdf_file.name] = {"status": "error", "error": str(e)}

# Summary
print(f"\n{'='*70}")
print("SUMMARY")
print(f"{'='*70}")

successful = [r for r in results.values() if r.get("status") == "success"]
if successful:
    total_extracted = sum(r["bill_summary"]["extracted"] for r in successful)
    total_possible = sum(r["bill_summary"]["total"] for r in successful)
    avg_percentage = sum(r["bill_summary"]["percentage"] for r in successful) / len(successful)
    
    print(f"\nProcessed: {len(successful)}/{len(test_pdfs)} PDFs")
    print(f"Total fields extracted: {total_extracted}/{total_possible}")
    print(f"Average extraction rate: {avg_percentage:.1f}%")
    
    # Most commonly extracted fields
    all_fields = {}
    for r in successful:
        for field, value in r["bill_summary"]["fields"].items():
            if value is not None:
                all_fields[field] = all_fields.get(field, 0) + 1
    
    print(f"\nMost commonly extracted fields:")
    for field, count in sorted(all_fields.items(), key=lambda x: -x[1])[:5]:
        percentage = (count / len(successful) * 100) if successful else 0
        print(f"  Field extracted in {count}/{len(successful)} PDFs ({percentage:.1f}%)")

# Save results
output_file = Path("output") / "test_6_pdfs_results.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n[OK] Results saved to: {output_file}")
