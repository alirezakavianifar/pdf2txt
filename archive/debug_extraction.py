"""Debug extraction logic."""
import json

with open('output/4_550_9000310904123_energy_supported_section.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

text = data['text']
lines = text.split('\n')

for i, line in enumerate(lines[:10]):
    line = line.strip()
    if len(line) < 20:
        continue
    
    parts = line.split()
    nums = []
    for p in parts:
        try:
            n = int(p.replace(',', ''))
            if n != 0:
                nums.append(n)
        except:
            try:
                n = float(p.replace(',', ''))
                if n != 0:
                    nums.append(n)
            except:
                pass
    
    if len(nums) >= 10:
        is_consumption = nums[0] < 100 and any(n > 1000000 for n in nums)
        print(f"Line {i}: nums[0]={nums[0]}, has_large={any(n > 1000000 for n in nums)}, is_consumption={is_consumption}")
        print(f"  First 5: {nums[:5]}, Large: {[n for n in nums if n > 1000000]}")
        if is_consumption:
            print(f"  MATCH! Line: {line[:100]}")
