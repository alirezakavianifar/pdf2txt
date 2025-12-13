"""Compare outputs from original PDF vs cropped PDF."""
import json
from pathlib import Path

# Read both JSON files
original = json.load(open('output/1_original_test.json', 'r', encoding='utf-8'))
cropped = json.load(open('output/1_energy_supported_section.json', 'r', encoding='utf-8'))

print("=" * 70)
print("COMPARISON: Original PDF vs Cropped PDF")
print("=" * 70)

print(f"\nOriginal PDF (1.pdf):")
print(f"  Text length: {len(original['text'])} characters")
print(f"  Table rows: {original.get('table', {}).get('row_count', 0)}")
print(f"  Table columns: {original.get('table', {}).get('column_count', 0)}")

print(f"\nCropped PDF (1/energy_supported_section.pdf):")
print(f"  Text length: {len(cropped['text'])} characters")
print(f"  Table rows: {cropped.get('table', {}).get('row_count', 0)}")
print(f"  Table columns: {cropped.get('table', {}).get('column_count', 0)}")

print(f"\nDifference:")
print(f"  Text: {len(cropped['text']) - len(original['text'])} chars")
print(f"  Table rows: {cropped.get('table', {}).get('row_count', 0) - original.get('table', {}).get('row_count', 0)}")

print("\n" + "=" * 70)
print("ORIGINAL PDF - First 300 characters:")
print("=" * 70)
print(original['text'][:300])

print("\n" + "=" * 70)
print("CROPPED PDF - First 300 characters:")
print("=" * 70)
print(cropped['text'][:300])
