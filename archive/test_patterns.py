"""Test regex patterns on the actual text."""
import json
import re

with open('output/1_cropped_test.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

text = data['text']

# Test pattern for upper table
pattern1 = r'(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d.]+)\s+([\d,]+)\s+(میان باری|اوج باری|کم باری)'
matches1 = list(re.finditer(pattern1, text))
print(f"Pattern 1 matches: {len(matches1)}")
for m in matches1[:2]:
    print(f"  Found: {m.group(0)[:50]}...")

# Test Friday pattern
pattern2 = r'(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d.]+)\s+([\d,]+)\s+اوج بار جمعه'
matches2 = list(re.finditer(pattern2, text))
print(f"\nPattern 2 (Friday) matches: {len(matches2)}")
for m in matches2:
    print(f"  Found: {m.group(0)[:50]}...")

# Try simpler pattern - just numbers before Persian text
pattern3 = r'(\d+(?:[,\s]\d+)*)\s+([\d.]+)\s+([\d,]+)\s+(میان باری|اوج باری|کم باری|اوج بار جمعه)'
matches3 = list(re.finditer(pattern3, text))
print(f"\nPattern 3 (simple) matches: {len(matches3)}")
for m in matches3[:3]:
    print(f"  Groups: {m.groups()}")

# Try to find the exact line
lines = text.split('\n')
for i, line in enumerate(lines):
    if 'میان باری' in line or 'اوج باری' in line:
        print(f"\nLine {i}: {line[:100]}")
