"""Check power section coordinates by examining extracted text."""
import json
from pathlib import Path

# Check a sample power section JSON to see what text was extracted
json_file = Path("output/1_power_section.json")

if json_file.exists():
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    text = data.get('text', '')
    
    print("=" * 70)
    print("EXTRACTED TEXT FROM POWER SECTION")
    print("=" * 70)
    print(text)
    print("\n" + "=" * 70)
    print("If the text doesn't contain the power values (قراردادی, محاسبه شده, etc.)")
    print("then the coordinates need to be adjusted.")
    print("=" * 70)
else:
    print(f"File not found: {json_file}")
