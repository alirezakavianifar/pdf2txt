"""Debug text structure."""
import json

with open('output/1_cropped_test.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

text = data['text']

print("Full text:")
print("=" * 70)
print(text)
print("=" * 70)

# Split by lines
lines = text.split('\n')
print(f"\nTotal lines: {len(lines)}")
print("\nFirst 10 lines:")
for i, line in enumerate(lines[:10]):
    print(f"{i}: {repr(line)}")
