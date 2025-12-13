"""Verify consumption history extraction for 4_510_9019722204129.pdf"""
import json
from pathlib import Path

def log(msg):
    """Print (ASCII-safe) and write to file"""
    # Print ASCII-safe version
    try:
        print(msg.encode('ascii', 'ignore').decode('ascii'))
    except:
        print("[Persian text - see output file]")
    with open("output/verify_consumption_history_4_510.txt", "a", encoding="utf-8") as f:
        f.write(msg + "\n")

# Expected values from the image
expected = [
    {
        "تاریخ قرائت": "1404/06/01",
        "میان باری": 85380,
        "اوج باری": 46480,
        "کم باری": 51100,
        "اوج بار جمع": None,  # Dot (•) in image
        "راکتیو": 43440,
        "دیماند": 436.4,
        "مبلغ": 2443693124  # Large integer, no decimal
    },
    {
        "تاریخ قرائت": "1404/05/01",
        "میان باری": 88580,
        "اوج باری": 46740,
        "کم باری": 56020,
        "اوج بار جمع": None,  # Dot (•)
        "راکتیو": 43640,
        "دیماند": 415.8,
        "مبلغ": 2540544441
    },
    {
        "تاریخ قرائت": "1404/03/27",
        "میان باری": 64980,
        "اوج باری": 34320,
        "کم باری": 39660,
        "اوج بار جمع": None,  # Dot (•)
        "راکتیو": 30440,
        "دیماند": 413.8,
        "مبلغ": 1702739903
    },
    {
        "تاریخ قرائت": "1404/03/01",
        "میان باری": 80560,
        "اوج باری": 44200,
        "کم باری": 47580,
        "اوج بار جمع": None,  # Dot (•)
        "راکتیو": 39240,
        "دیماند": 398.8,
        "مبلغ": 1919655879
    },
    {
        "تاریخ قرائت": "1404/02/01",
        "میان باری": 65280,
        "اوج باری": 16880,
        "کم باری": 31860,
        "اوج بار جمع": None,  # Dot (•)
        "راکتیو": 23500,
        "دیماند": 376.8,
        "مبلغ": 1003264451
    },
    {
        "تاریخ قرائت": "1404/01/01",
        "میان باری": 68360,
        "اوج باری": 21020,
        "کم باری": 35240,
        "اوج بار جمع": None,  # Dot (•)
        "راکتیو": 26200,
        "دیماند": 384,  # Integer (no decimal)
        "مبلغ": 993066019
    }
]

# Read extracted data
json_path = Path("output/4_510_9019722204129_consumption_history_section_restructured.json")
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

extracted = data.get("سوابق مصرف و مبلغ", [])

# Clear output file
with open("output/verify_consumption_history_4_510.txt", "w", encoding="utf-8") as f:
    f.write("")

log("="*70)
log("Verification of Consumption History Extraction for 4_510_9019722204129.pdf")
log("="*70)

all_correct = True
fields_to_check = ["تاریخ قرائت", "میان باری", "اوج باری", "کم باری", "اوج بار جمع", "راکتیو", "دیماند", "مبلغ"]

for i, (exp_row, ext_row) in enumerate(zip(expected, extracted), 1):
    log(f"\n--- Row {i} ({exp_row['تاریخ قرائت']}) ---")
    row_correct = True
    
    for field in fields_to_check:
        exp_val = exp_row[field]
        ext_val = ext_row.get(field)
        
        if field == "اوج بار جمع":
            # Should be None/null (dot in image)
            if ext_val is None:
                log(f"  {field}: OK (null/empty as expected)")
            else:
                log(f"  {field}: WARNING - extracted: {ext_val}, expected: null")
                # Don't mark as error, just warning
        
        elif field == "دیماند":
            # Can be integer or float
            if ext_val is not None:
                # Check if values match (allow for float/int conversion)
                if abs(float(ext_val) - float(exp_val)) < 0.1:
                    log(f"  {field}: OK (extracted: {ext_val}, expected: {exp_val})")
                else:
                    log(f"  {field}: MISMATCH - extracted: {ext_val}, expected: {exp_val}")
                    row_correct = False
                    all_correct = False
            else:
                log(f"  {field}: MISSING")
                row_correct = False
                all_correct = False
        
        elif field == "مبلغ":
            # Large integer values (no decimal division needed)
            if ext_val is not None:
                if abs(float(ext_val) - float(exp_val)) < 1:
                    log(f"  {field}: OK (extracted: {ext_val}, expected: {exp_val})")
                else:
                    log(f"  {field}: MISMATCH - extracted: {ext_val}, expected: {exp_val}")
                    row_correct = False
                    all_correct = False
            else:
                log(f"  {field}: MISSING")
                row_correct = False
                all_correct = False
        
        else:
            # Integer fields
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
log("="*70)
