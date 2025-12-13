"""Test number extraction and write to file."""
import json

def extract_numbers_from_line(line):
    numbers = []
    parts = line.split()
    for part in parts:
        try:
            n = int(part.replace(',', ''))
            if n != 0:
                numbers.append(n)
        except ValueError:
            try:
                n = float(part.replace(',', ''))
                if n != 0:
                    numbers.append(n)
            except ValueError:
                pass
    return numbers

with open('output/4_550_9000310904123_energy_supported_section.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

text = data.get('text', '')
lines = text.split('\n')

with open('output/debug_test.txt', 'w', encoding='utf-8') as f:
    for i, line in enumerate(lines[:10]):
        if len(line.strip()) < 20:
            continue
        nums = extract_numbers_from_line(line)
        if len(nums) >= 10:
            has_tou = nums[0] < 100
            has_large = any(n > 1000000 for n in nums)
            f.write(f"Line {i}: len={len(nums)}, has_tou={has_tou}, has_large={has_large}\n")
            f.write(f"  First 5: {nums[:5]}, Large: {[n for n in nums if n > 1000000]}\n")
            if has_tou and has_large:
                f.write(f"  *** MATCHES CONSUMPTION PATTERN ***\n")

print("Debug output written to output/debug_test.txt")
