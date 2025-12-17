
import re

text = '19,549,842 بهای انرژی تامین شده\n129,769 آبونمان\n23- کسر هزار ریال'

field_patterns = {
    "بهای انرژی تامین شده": [
        r'بهای انرژی تامین شده\s*:?\s*(-?\d+(?:,\d+)*)',
        r'(-?\d+(?:,\d+)*)\s*بهای انرژی تامین شده'
    ],
    "آبونمان": [
        r'آبونمان\s*:?\s*(-?\d+(?:,\d+)*)',
        r'(-?\d+(?:,\d+)*)\s*آبونمان'
    ],
    "کسر هزار ریال": [
        r'کسر هزار ریال\s*:?\s*(-?\d+(?:,\d+)*)',
        r'(-?\d+(?:,\d+)*)\s*کسر هزار ریال'
    ]
}

print(f"Testing with text:\n{text}\n")

for field, patterns in field_patterns.items():
    found = None
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            # Check which group captured the number (group 1 in first regex, group 1 in second)
            # Actually simplest is to look for the one that is not None if I used alternation
            # But here I am iterating.
            found = match.group(1)
            print(f"Matched '{field}': {found} (Pattern: {pattern})")
            break
    if not found:
        print(f"Failed to match '{field}'")
