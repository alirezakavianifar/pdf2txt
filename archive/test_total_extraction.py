"""Test total extraction logic."""
test_line = "24 5592 0 0 0 0 0 5592 13,307,616 جمع"

print(f"Testing line: {test_line}")
print(f"Contains 'جمع': {'جمع' in test_line}")

line_parts = test_line.split()
print(f"Parts: {line_parts}")

for part in line_parts:
    clean_part = part.replace(',', '').replace('،', '').strip()
    try:
        n = int(clean_part)
        print(f"  {part} -> {clean_part} -> {n}")
        if 1000 <= n <= 200000:
            print(f"    -> Consumption total candidate: {n}")
        elif n > 1000000:
            print(f"    -> Amount total candidate: {n}")
    except ValueError:
        print(f"  {part} -> {clean_part} -> NOT A NUMBER")
