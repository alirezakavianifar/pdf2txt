"""
Quick script to display the power section extraction results for Template 2
"""
import json

# Load the restructured power section
with open('output/2_power_section_restructured.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=" * 60)
print("POWER SECTION EXTRACTION RESULTS (Template 2)")
print("=" * 60)

rows = data['power_section']['rows']
print(f"\nTotal rows extracted: {len(rows)}\n")

for i, row in enumerate(rows, 1):
    print(f"Row {i}: {row['category']}")
    print(f"  Category Key: {row['category_key']}")
    print(f"  Raw Values: {row['raw_values']}")
    
    # Show mapped fields if available
    if 'bilateral' in row:
        print(f"  Bilateral: {row.get('bilateral', 'N/A')}")
        print(f"  Exchange: {row.get('exchange', 'N/A')}")
        print(f"  Green Board: {row.get('green_board', 'N/A')}")
        print(f"  Renewable: {row.get('renewable', 'N/A')}")
        print(f"  Market Average: {row.get('market_average', 'N/A')}")
        print(f"  Max Green Need: {row.get('max_green_need', 'N/A')}")
        print(f"  Max Wholesale: {row.get('max_wholesale', 'N/A')}")
        print(f"  TOU Hours: {row.get('tou_hours', 'N/A')}")
    
    print()

print("=" * 60)
