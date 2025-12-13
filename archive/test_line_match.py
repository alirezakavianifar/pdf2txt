"""Test if we can match lines by number patterns."""
import json

with open('output/4_550_9000310904123_energy_supported_section.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

text = data['text']
lines = text.split('\n')

# Look for lines with the pattern: number number number number large_number large_number
for i, line in enumerate(lines):
    parts = line.split()
    nums = []
    for p in parts:
        try:
            n = int(p.replace(',', ''))
            nums.append(n)
        except:
            try:
                n = float(p.replace(',', ''))
                nums.append(n)
            except:
                pass
    
    # Look for consumption pattern: TOU, meters, coef, consumption, ... large amount
    if len(nums) >= 10:
        # Check if has TOU-like number and large amount
        if nums[0] < 100 and any(n > 10000000 for n in nums):
            print(f"Line {i}: First 5 nums: {nums[:5]}, Large nums: {[n for n in nums if n > 10000000]}")
            if i > 10:
                break
