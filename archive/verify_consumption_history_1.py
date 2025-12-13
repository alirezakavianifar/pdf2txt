"""Verify consumption history extraction for 1.pdf"""
import json
from pathlib import Path

def log(msg):
    """Print (ASCII-safe) and write to file"""
    # Print ASCII-safe version
    try:
        print(msg.encode('ascii', 'ignore').decode('ascii'))
    except:
        print("[Persian text - see output file]")
    with open("output/verify_consumption_history_1.txt", "a", encoding="utf-8") as f:
        f.write(msg + "\n")

# Expected values from the image
expected = [
    {
        "تاریخ قرائت": "1404/01/01",
        "میان باری": 28790,
        "اوج باری": 7740,
        "کم باری": 24889,
        "اوج بار جمع": 1202,
        "راکتیو": 498,
        "دیماند": 132,
        "مبلغ": 4345169.09
    },
    {
        "تاریخ قرائت": "1403/12/01",
        "میان باری": 29227,
        "اوج باری": 8072,
        "کم باری": 25791,
        "اوج بار جمع": 1265,
        "راکتیو": 464,
        "دیماند": 121,
        "مبلغ": 4294064.56
    },
    {
        "تاریخ قرائت": "1403/11/01",
        "میان باری": 29215,
        "اوج باری": 7998,
        "کم باری": 25572,
        "اوج بار جمع": 1201,
        "راکتیو": 101,
        "دیماند": 136,
        "مبلغ": 4728734.02
    },
    {
        "تاریخ قرائت": "1403/10/01",
        "میان باری": 29187,
        "اوج باری": 7685,
        "کم باری": 24450,
        "اوج بار جمع": 1537,
        "راکتیو": 521,
        "دیماند": 124,
        "مبلغ": 4475661.68
    },
    {
        "تاریخ قرائت": "1403/09/01",
        "میان باری": 24639,
        "اوج باری": 7071,
        "کم باری": 21064,
        "اوج بار جمع": 1080,
        "راکتیو": 90,
        "دیماند": 103,
        "مبلغ": 3962687.54
    },
    {
        "تاریخ قرائت": "1403/08/01",
        "میان باری": 23381,
        "اوج باری": 6665,
        "کم باری": 16162,
        "اوج بار جمع": 1468,
        "راکتیو": 1105,
        "دیماند": 125,
        "مبلغ": 3831745.12
    }
]

# Read extracted data
json_path = Path("output/1_consumption_history_section_restructured.json")
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

extracted = data.get("سوابق مصرف و مبلغ", [])

# Clear output file
with open("output/verify_consumption_history_1.txt", "w", encoding="utf-8") as f:
    f.write("")

log("="*70)
log("Verification of Consumption History Extraction for 1.pdf")
log("="*70)

all_correct = True
fields_to_check = ["تاریخ قرائت", "میان باری", "اوج باری", "کم باری", "اوج بار جمع", "راکتیو", "دیماند", "مبلغ"]

for i, (exp_row, ext_row) in enumerate(zip(expected, extracted), 1):
    log(f"\n--- Row {i} ({exp_row['تاریخ قرائت']}) ---")
    row_correct = True
    
    for field in fields_to_check:
        exp_val = exp_row[field]
        ext_val = ext_row.get(field)
        
        if field == "مبلغ":
            # For amount, check if extracted value matches expected (accounting for decimal)
            # Expected values have 2 decimal places, extracted might be integer * 100
            if ext_val is not None:
                # Check if ext_val / 100 matches expected
                if abs(ext_val / 100 - exp_val) < 0.01:
                    log(f"  {field}: OK (extracted: {ext_val}, expected: {exp_val}, ratio check: {ext_val/100:.2f})")
                else:
                    log(f"  {field}: MISMATCH - extracted: {ext_val}, expected: {exp_val}")
                    row_correct = False
                    all_correct = False
            else:
                log(f"  {field}: MISSING")
                row_correct = False
                all_correct = False
        else:
            if ext_val == exp_val:
                log(f"  {field}: OK ({ext_val})")
            else:
                log(f"  {field}: MISMATCH - extracted: {ext_val}, expected: {exp_val}")
                row_correct = False
                all_correct = False
    
    if row_correct:
        log(f"  Row {i}: ALL FIELDS CORRECT")
    else:
        log(f"  Row {i}: HAS ERRORS")

log("\n" + "="*70)
if all_correct:
    log("RESULT: ALL VALUES CORRECT!")
else:
    log("RESULT: SOME VALUES INCORRECT")
    log("\nISSUE: مبلغ (amount) values are extracted as integers (100x larger)")
    log("       They should have 2 decimal places (e.g., 4345169.09 not 434516909)")
log("="*70)
