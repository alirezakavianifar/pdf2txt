"""Test extraction functions directly."""
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

test_line = lines[3]  # Should be the میان باری line
print(f"Test line: {test_line[:150]}")

nums = extract_numbers_from_line(test_line)
print(f"Extracted numbers: {nums[:15]}")

has_tou = nums[0] < 100 if nums else False
has_large = any(n > 1000000 for n in nums) if nums else False
print(f"Has TOU: {has_tou}, Has large amount: {has_large}, is_consumption: {has_tou and has_large}")
