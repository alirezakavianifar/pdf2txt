"""Debug text structure to understand format."""
import json

with open('output/4_550_9000310904123_energy_supported_section.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

text = data['text']
lines = text.split('\n')

print("Looking for consumption rows...")
for i, line in enumerate(lines[:20]):
    if 'میان' in line or 'اوج' in line or 'کم' in line:
        print(f"Line {i}: {line[:150]}")
