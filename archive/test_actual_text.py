"""Test actual text content."""
import json

with open('output/4_550_9000310904123_energy_supported_section.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

text = data.get('text', '')
print(f"Text length: {len(text)}")
print(f"First 500 chars: {repr(text[:500])}")

lines = text.split('\n')
print(f"Total lines: {len(lines)}")

for i, line in enumerate(lines[:5]):
    print(f"Line {i}: length={len(line)}, first 100: {repr(line[:100])}")
    parts = line.split()
    print(f"  Parts: {len(parts)}")
    if len(parts) > 10:
        print(f"  First 5 parts: {parts[:5]}")
