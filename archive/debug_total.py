"""Debug total extraction."""
import json

with open('output/4_600_9000796904120_energy_supported_section.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

text = data['text']
lines = text.split('\n')

print(f"Total lines: {len(lines)}")
for i, line in enumerate(lines):
    line_stripped = line.strip()
    # Check if line contains جمع or numbers that look like total
    if "جمع" in line_stripped or ("5592" in line_stripped and "13" in line_stripped and len(line_stripped) > 30):
        print(f"\nLine {i}: length={len(line_stripped)}")
        print(f"  Contains 'جمع': {'جمع' in line_stripped}")
        print(f"  First 100 chars: {line_stripped[:100]}")
        
        # Try to parse numbers
        parts = line_stripped.split()
        print(f"  Parts: {parts[:15]}")
        
        for part in parts:
            clean = part.replace(',', '').strip()
            try:
                n = int(clean)
                if 1000 <= n <= 200000:
                    print(f"    -> Consumption candidate: {n}")
                elif n > 1000000:
                    print(f"    -> Amount candidate: {n}")
            except:
                pass
