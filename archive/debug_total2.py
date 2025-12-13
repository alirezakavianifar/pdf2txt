"""Debug total extraction."""
import json

with open('output/4_600_9000796904120_energy_supported_section.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

text = data['text']
lines = text.split('\n')

with open('output/debug_total_output.txt', 'w', encoding='utf-8') as f:
    f.write(f"Total lines: {len(lines)}\n\n")
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        # Check if line contains جمع or numbers that look like total
        if "جمع" in line_stripped or ("5592" in line_stripped and "13" in line_stripped):
            f.write(f"\nLine {i}: length={len(line_stripped)}\n")
            f.write(f"  Contains 'جمع': {'جمع' in line_stripped}\n")
            f.write(f"  Full line: {line_stripped}\n")
            
            # Try to parse numbers
            parts = line_stripped.split()
            f.write(f"  Parts: {parts}\n")
            
            for part in parts:
                clean = part.replace(',', '').strip()
                try:
                    n = int(clean)
                    if 1000 <= n <= 200000:
                        f.write(f"    -> Consumption candidate: {part} -> {n}\n")
                    elif n > 1000000:
                        f.write(f"    -> Amount candidate: {part} -> {n}\n")
                except:
                    pass

print("Debug output written to output/debug_total_output.txt")
