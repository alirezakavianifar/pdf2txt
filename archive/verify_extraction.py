"""Verify extraction accuracy against image description."""
import json

# Expected values from image description
expected = {
    "consumption": {
        "میان باری": {
            "TOU": 12,
            "شماره کنتور قبلی": 1741.32,
            "شماره کنتور کنونی": 1744.56,
            "ضریب": 800,
            "مصرف کل": 2592,
            "انرژی مشمول": 2592,
            "نرخ": 2296,
            "مبلغ (ریال)": 5951232
        },
        "اوج باری": {
            "TOU": 6,
            "شماره کنتور قبلی": 583.95,
            "شماره کنتور کنونی": 585.37,
            "ضریب": 800,
            "مصرف کل": 1136,
            "انرژی مشمول": 1136,
            "نرخ": 4592,
            "مبلغ (ریال)": 5216512
        },
        "کم باری": {
            "TOU": 6,
            "شماره کنتور قبلی": 1061.42,
            "شماره کنتور کنونی": 1063.75,
            "ضریب": 800,
            "مصرف کل": 1864,
            "انرژی مشمول": 1864,
            "نرخ": 1148,
            "مبلغ (ریال)": 2139872
        }
    },
    "regulation": {
        "میان باری": {
            "نرخ پایه": 2296,
            "متوسط نرخ بازار": 2945.77,
            "تفاوت نرخ": 0  # Image shows "-" which means 0
        },
        "اوج باری": {
            "نرخ پایه": 4592,
            "متوسط نرخ بازار": 2945.77,
            "تفاوت نرخ": 1646.23
        },
        "کم باری": {
            "نرخ پایه": 1148,
            "متوسط نرخ بازار": 2945.77,
            "تفاوت نرخ": 0  # Image shows "-"
        }
    },
    "total": {
        "مصرف کل": 5592,
        "مبلغ (ریال)": 13307616
    }
}

# Load extracted JSON
with open('output/4_600_9000796904120_energy_supported_section_restructured.json', 'r', encoding='utf-8') as f:
    extracted = json.load(f)

output_file = open('output/verification_results.txt', 'w', encoding='utf-8')

def log(msg):
    output_file.write(msg + '\n')
    # Try to print ASCII-safe version
    try:
        print(msg)
    except:
        pass

log("=" * 80)
log("VERIFICATION RESULTS")
log("=" * 80)

# Check consumption
log("\n1. CONSUMPTION SECTION:")
all_correct = True
for desc in ["میان باری", "اوج باری", "کم باری"]:
    exp = expected["consumption"][desc]
    ext = next((x for x in extracted["شرح مصارف"] if x["شرح مصارف"] == desc), None)
    
    if not ext:
        log(f"  [X] {desc}: NOT FOUND")
        all_correct = False
        continue
    
    errors = []
    for key, exp_val in exp.items():
        if key == "مبلغ (ریال)":
            ext_val = ext["بهای انرژی پشتیبانی شده"]["مبلغ (ریال)"]
        elif key == "انرژی مشمول":
            ext_val = ext["بهای انرژی پشتیبانی شده"]["انرژی مشمول"]
        elif key == "نرخ":
            ext_val = ext["بهای انرژی پشتیبانی شده"]["نرخ"]
        else:
            ext_val = ext.get(key)
        
        if abs(ext_val - exp_val) > 0.01:
            errors.append(f"{key}: expected {exp_val}, got {ext_val}")
    
    if errors:
        log(f"  [X] {desc}: {', '.join(errors)}")
        all_correct = False
    else:
        log(f"  [OK] {desc}: ALL CORRECT")

# Check regulation differences
print("\n2. REGULATION DIFFERENCES:")
for desc in ["میان باری", "اوج باری", "کم باری"]:
    exp = expected["regulation"][desc]
    ext = next((x for x in extracted["مابه التفاوت اجرای مقررات"] if x["شرح مصارف"] == desc), None)
    
    if not ext:
        log(f"  [X] {desc}: NOT FOUND")
        all_correct = False
        continue
    
    errors = []
    for key, exp_val in exp.items():
        ext_val = ext.get(key, 0)
        if abs(ext_val - exp_val) > 0.01:
            errors.append(f"{key}: expected {exp_val}, got {ext_val}")
    
    if errors:
        log(f"  [X] {desc}: {', '.join(errors)}")
        all_correct = False
    else:
        log(f"  [OK] {desc}: ALL CORRECT")

# Check total
log("\n3. TOTAL SECTION:")
exp_total = expected["total"]
ext_total = extracted.get("جمع", {})
errors = []
if ext_total.get("مصرف کل") != exp_total["مصرف کل"]:
    errors.append(f"مصرف کل: expected {exp_total['مصرف کل']}, got {ext_total.get('مصرف کل', 'MISSING')}")
if ext_total.get("مبلغ (ریال)") != exp_total["مبلغ (ریال)"]:
    errors.append(f"مبلغ: expected {exp_total['مبلغ (ریال)']}, got {ext_total.get('مبلغ (ریال)', 'MISSING')}")

if errors:
    print(f"  ❌ TOTAL: {', '.join(errors)}")
    all_correct = False
else:
    print(f"  ✓ TOTAL: ALL CORRECT")

print("\n" + "=" * 80)
if all_correct:
    print("OVERALL: ✓ ALL SECTIONS CORRECT")
else:
    print("OVERALL: [WARNING] SOME ISSUES FOUND (see above)")
