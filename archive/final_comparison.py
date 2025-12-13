"""Final comparison of outputs."""
import json
from pathlib import Path

# Read both JSON files
original = json.load(open('output/1_original_test.json', 'r', encoding='utf-8'))
cropped = json.load(open('output/1_cropped_test.json', 'r', encoding='utf-8'))

print("=" * 70)
print("FINAL COMPARISON: Original PDF vs Cropped PDF")
print("=" * 70)

print(f"\nOriginal PDF (1.pdf) - NO CROP BOX:")
print(f"  Text length: {len(original['text'])} characters")
print(f"  Table rows: {original.get('table', {}).get('row_count', 0)}")
print(f"  Table columns: {original.get('table', {}).get('column_count', 0)}")

print(f"\nCropped PDF (1/energy_supported_section.pdf) - WITH CROP BOX:")
print(f"  Text length: {len(cropped['text'])} characters")
print(f"  Table rows: {cropped.get('table', {}).get('row_count', 0)}")
print(f"  Table columns: {cropped.get('table', {}).get('column_count', 0)}")

print(f"\nDifference:")
text_diff = len(cropped['text']) - len(original['text'])
table_diff = cropped.get('table', {}).get('row_count', 0) - original.get('table', {}).get('row_count', 0)
print(f"  Text: {text_diff:+d} characters ({text_diff/len(original['text'])*100:.1f}%)")
print(f"  Table rows: {table_diff:+d}")

# Write to files for easier comparison
with open('output/comparison_original.txt', 'w', encoding='utf-8') as f:
    f.write(original['text'][:500])
with open('output/comparison_cropped.txt', 'w', encoding='utf-8') as f:
    f.write(cropped['text'][:500])

print("\n" + "=" * 70)
print("First 500 chars saved to:")
print("  output/comparison_original.txt")
print("  output/comparison_cropped.txt")

# Check if cropped text is a subset of original
if cropped['text'].strip() in original['text']:
    print("\n[YES] Cropped text appears to be a subset of original text")
else:
    print("\n[NO] Cropped text is NOT a subset of original text (may be reordered/filtered)")
