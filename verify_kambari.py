"""Quick verification that کم باری is extracted from all test PDFs."""
import json
from pathlib import Path

test_files = [
    "output/1/1_consumption_history_section_restructured.json",
    "output/4_600_9002420604128/4_600_9002420604128_consumption_history_section_restructured.json",
    "output/4_550_9000896204125/4_550_9000896204125_consumption_history_section_restructured.json",
    "output/4_550_9402898804120/4_550_9402898804120_consumption_history_section_restructured.json",
    "output/4_600_9000796904120/4_600_9000796904120_consumption_history_section_restructured.json",
]

results = []
for f in test_files:
    path = Path(f)
    if path.exists():
        with open(path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            rows = data.get("سوابق مصرف و مبلغ", [])
            has_kambari = all("کم باری" in r and r["کم باری"] is not None for r in rows)
            results.append({
                "pdf": path.parent.name,
                "rows": len(rows),
                "has_kambari": has_kambari,
                "kambari_count": sum(1 for r in rows if "کم باری" in r and r["کم باری"] is not None)
            })

print(f"\n{'='*60}")
print(f"VERIFICATION RESULTS: {len(results)} PDF(s) tested")
print(f"{'='*60}\n")

for r in results:
    status = "OK" if r["has_kambari"] else "MISSING"
    print(f"  {r['pdf']}: {r['rows']} rows, Kambari: {status} ({r['kambari_count']}/{r['rows']} rows)")

all_ok = all(r["has_kambari"] for r in results)
print(f"\n{'='*60}")
if all_ok:
    print(f"SUCCESS: All {len(results)} PDF(s) have Kambari extracted correctly!")
else:
    failed = [r["pdf"] for r in results if not r["has_kambari"]]
    print(f"FAILED: {len(failed)} PDF(s) missing Kambari: {failed}")
print(f"{'='*60}\n")
