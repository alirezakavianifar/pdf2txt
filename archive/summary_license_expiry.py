"""Generate summary of license expiry extraction results."""
import json
from pathlib import Path

output_dir = Path("output")
template_dir = Path("template1")

# Get all restructured JSON files for license expiry
json_files = list(output_dir.glob("*_license_expiry_section_restructured.json"))

print("=" * 70)
print("LICENSE EXPIRY EXTRACTION SUMMARY")
print("=" * 70)

results = []
for json_file in sorted(json_files):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    pdf_name = json_file.stem.replace("_license_expiry_section_restructured", "")
    expiry_date = data.get("تاریخ انقضا پروانه")
    
    status = "OK" if expiry_date else "MISSING"
    results.append((pdf_name, expiry_date, status))

print(f"\n{'PDF Name':<35} {'Expiry Date':<15} {'Status':<10}")
print("-" * 70)
for pdf_name, date, status in results:
    date_str = date if date else "N/A"
    print(f"{pdf_name:<35} {date_str:<15} {status:<10}")

print(f"\n{'='*70}")
print(f"Total processed: {len(results)}")
print(f"Successfully extracted: {sum(1 for _, d, _ in results if d)}")
print(f"{'='*70}")
