"""Generate summary of test results."""
import json
from pathlib import Path

output_dir = Path("output")

pdf_names = [
    "1",
    "4_510_9019722204129",
    "4_550_9000310904123",
    "4_550_9000896204125",
    "4_550_9402898804120",
    "4_567_9004439404122",
    "4_600_9000796904120",
    "4_600_9001713204128",
    "4_600_9001869604126",
    "4_600_9002420604128"
]

summary_file = output_dir / "test_summary.txt"

with open(summary_file, 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("TEST RESULTS SUMMARY\n")
    f.write("=" * 80 + "\n\n")

for pdf_name in pdf_names:
    restructured_file = output_dir / f"{pdf_name}_energy_supported_section_restructured.json"
    
    if not restructured_file.exists():
        print(f"{pdf_name}: FILE NOT FOUND")
        continue
    
    with open(restructured_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    consumption_count = len(data.get("شرح مصارف", []))
    regulation_count = len(data.get("مابه التفاوت اجرای مقررات", []))
    has_total = bool(data.get("جمع", {}).get("مصرف کل") or data.get("جمع", {}).get("مبلغ (ریال)"))
    
    # Check if total has values
    total_consumption = data.get("جمع", {}).get("مصرف کل", 0)
    total_amount = data.get("جمع", {}).get("مبلغ (ریال)", 0)
    
    status = []
    if consumption_count == 3:
        status.append("[OK] Consumption")
    else:
        status.append(f"[{consumption_count}/3] Consumption")
    
    if regulation_count >= 2:
        status.append(f"[OK] Regulation ({regulation_count})")
    else:
        status.append(f"[{regulation_count}] Regulation")
    
    if has_total:
        status.append("[OK] Total")
    else:
        status.append("[MISSING] Total")
    
    with open(summary_file, 'a', encoding='utf-8') as f:
        f.write(f"\n{pdf_name}:\n")
        f.write(f"  {' | '.join(status)}\n")
        
        # Show consumption descriptions
        for item in data.get("شرح مصارف", []):
            desc = item.get("شرح مصارف", "")
            consumption = item.get("مصرف کل", 0)
            amount = item.get("بهای انرژی پشتیبانی شده", {}).get("مبلغ (ریال)", 0)
            f.write(f"    - {desc}: مصرف={consumption:,}, مبلغ={amount:,}\n")

with open(summary_file, 'a', encoding='utf-8') as f:
    f.write("\n" + "=" * 80 + "\n")

print(f"Summary written to: {summary_file}")
