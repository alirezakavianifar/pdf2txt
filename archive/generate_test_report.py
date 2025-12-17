"""
Generate detailed test report from the 6 PDFs test results.
"""

import json
from pathlib import Path
from collections import Counter

# Read all final pipeline files
pdfs = [
    "2",
    "2_2", 
    "3_1000_7001523101422",
    "3_1200_7005274901427",
    "3_1500_7003340001421",
    "4_1200_7000895201427"
]

results = {}
all_extracted_fields = Counter()
all_missing_fields = Counter()

for pdf_name in pdfs:
    output_file = Path("output") / f"{pdf_name}_final_pipeline.json"
    
    if not output_file.exists():
        results[pdf_name] = {"status": "not_found"}
        continue
    
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Get bill_summary
        bill_summary = data.get("خلاصه صورتحساب", {})
        
        extracted = [k for k, v in bill_summary.items() if v is not None]
        missing = [k for k, v in bill_summary.items() if v is None]
        
        results[pdf_name] = {
            "status": "success",
            "extracted_count": len(extracted),
            "total_count": len(bill_summary),
            "extraction_rate": (len(extracted) / len(bill_summary) * 100) if bill_summary else 0,
            "extracted_fields": extracted,
            "missing_fields": missing,
            "values": {k: v for k, v in bill_summary.items() if v is not None}
        }
        
        # Update counters
        for field in extracted:
            all_extracted_fields[field] += 1
        for field in missing:
            all_missing_fields[field] += 1
            
    except Exception as e:
        results[pdf_name] = {"status": "error", "error": str(e)}

# Generate report
print("=" * 70)
print("Template 2 Extraction Test Report - 6 PDFs")
print("=" * 70)

successful = [r for r in results.values() if r.get("status") == "success"]
print(f"\nSuccessfully processed: {len(successful)}/{len(pdfs)} PDFs\n")

# Individual results
for pdf_name, result in results.items():
    if result.get("status") == "success":
        print(f"{pdf_name}:")
        print(f"  Extracted: {result['extracted_count']}/{result['total_count']} fields ({result['extraction_rate']:.1f}%)")
        print()

# Summary statistics
if successful:
    total_extracted = sum(r['extracted_count'] for r in successful)
    total_possible = sum(r['total_count'] for r in successful)
    avg_rate = sum(r['extraction_rate'] for r in successful) / len(successful)
    
    print("=" * 70)
    print("SUMMARY STATISTICS")
    print("=" * 70)
    print(f"Total fields extracted: {total_extracted}/{total_possible}")
    print(f"Average extraction rate: {avg_rate:.1f}%")
    
    print(f"\nField extraction statistics:")
    print(f"  {len(all_extracted_fields)} different fields were extracted")
    print(f"  {len(all_missing_fields)} different fields were missing")
    print(f"\n  Top extracted fields (see JSON for field names):")
    for i, (field, count) in enumerate(all_extracted_fields.most_common(5), 1):
        percentage = (count / len(successful)) * 100
        print(f"    {i}. Extracted in {count}/{len(successful)} PDFs ({percentage:.1f}%)")
    
    print(f"\n  Top missing fields (see JSON for field names):")
    for i, (field, count) in enumerate(all_missing_fields.most_common(5), 1):
        percentage = (count / len(successful)) * 100
        print(f"    {i}. Missing in {count}/{len(successful)} PDFs ({percentage:.1f}%)")

# Save detailed report
report_file = Path("output") / "test_6_pdfs_detailed_report.json"
with open(report_file, 'w', encoding='utf-8') as f:
    json.dump({
        "summary": {
            "total_pdfs": len(pdfs),
            "successful": len(successful),
            "total_fields_extracted": total_extracted if successful else 0,
            "total_fields_possible": total_possible if successful else 0,
            "average_extraction_rate": avg_rate if successful else 0
        },
        "field_statistics": {
            "extracted": dict(all_extracted_fields),
            "missing": dict(all_missing_fields)
        },
        "detailed_results": results
    }, f, ensure_ascii=False, indent=2)

print(f"\n[OK] Detailed report saved to: {report_file}")
