import json

with open('output/8_energy_consumption_table_section.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

rows = data['table']['rows']

output = []

# Check row 1
output.append("Row 1:")
r1 = rows[1]
nums1 = [(i, r1[i]) for i in range(len(r1)) if r1[i] and str(r1[i]).strip() and any(c.isdigit() for c in str(r1[i]))]
for i, v in nums1:
    output.append(f"  Pos {i}: {repr(v)}")

output.append("\nRow 2:")
r2 = rows[2]
nums2 = [(i, r2[i]) for i in range(len(r2)) if r2[i] and str(r2[i]).strip() and any(c.isdigit() for c in str(r2[i]))]
for i, v in nums2:
    output.append(f"  Pos {i}: {repr(v)}")

output.append("\nRow 3:")
r3 = rows[3]
nums3 = [(i, r3[i]) for i in range(len(r3)) if r3[i] and str(r3[i]).strip() and any(c.isdigit() for c in str(r3[i]))]
for i, v in nums3:
    output.append(f"  Pos {i}: {repr(v)}")

output.append("\nRow 4:")
r4 = rows[4]
nums4 = [(i, r4[i]) for i in range(len(r4)) if r4[i] and str(r4[i]).strip() and any(c.isdigit() for c in str(r4[i]))]
for i, v in nums4[:15]:
    output.append(f"  Pos {i}: {repr(v)}")

output.append("\nRow 5:")
r5 = rows[5]
nums5 = [(i, r5[i]) for i in range(len(r5)) if r5[i] and str(r5[i]).strip() and any(c.isdigit() for c in str(r5[i]))]
for i, v in nums5[:15]:
    output.append(f"  Pos {i}: {repr(v)}")

with open('table_values_check.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))
    
print("Saved to table_values_check.txt")
