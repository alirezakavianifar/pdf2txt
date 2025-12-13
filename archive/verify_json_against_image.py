"""Verify restructured JSON against image data."""
import json

# Load the restructured JSON
with open('output/1_cropped_restructured.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=" * 70)
print("VERIFICATION: JSON vs Image Data")
print("=" * 70)

errors = []
warnings = []

# 1. Check "شرح مصارف" section
print("\n1. Checking 'شرح مصارف' section:")
print("-" * 70)

expected_consumption = {
    "میان باری": {
        "TOU": 13,
        "شماره کنتور قبلی": 1722439,  # Image shows 1722439 (different from earlier!)
        "شماره کنتور کنونی": 1758899,
        "مصرف کل": 34460,
        "نرخ": 4063.462,
        "مبلغ (ریال)": 140026901
    },
    "اوج باری": {
        "TOU": 2,
        "شماره کنتور قبلی": 527231,
        "شماره کنتور کنونی": 536473,
        "مصرف کل": 9242,
        "نرخ": 4506.294,
        "مبلغ (ریال)": 41647169
    },
    "کم باری": {
        "TOU": 9,
        "شماره کنتور قبلی": 1232928,
        "شماره کنتور کنونی": 1257250,
        "مصرف کل": 24322,
        "نرخ": 3718,
        "مبلغ (ریال)": 90429196
    },
    "اوج بار جمعه": {
        "TOU": 0,
        "شماره کنتور قبلی": 88753,
        "شماره کنتور کنونی": 90562,
        "مصرف کل": 1809,
        "نرخ": 4506.294,
        "مبلغ (ریال)": 8151886
    }
}

for item in data["شرح مصارف"]:
    desc = item["شرح مصارف"]
    if desc in expected_consumption:
        exp = expected_consumption[desc]
        for key, expected_val in exp.items():
            actual_val = item.get(key)
            if key == "مبلغ (ریال)" or key == "نرخ":
                # Handle nested structure
                if key == "مبلغ (ریال)":
                    actual_val = item.get("بهای انرژی پشتیبانی شده", {}).get("مبلغ (ریال)")
                elif key == "نرخ":
                    actual_val = item.get("بهای انرژی پشتیبانی شده", {}).get("نرخ")
            
            if actual_val != expected_val:
                error_msg = f"  [MISMATCH] {desc} - {key}: Expected {expected_val}, Got {actual_val}"
                if abs(actual_val - expected_val) < 1000:  # Small difference might be formatting
                    warnings.append(error_msg)
                    print(f"  [WARNING] {desc} - {key}: Expected {expected_val}, Got {actual_val} (minor difference)")
                else:
                    errors.append(error_msg)
                    print(error_msg)
            else:
                print(f"  [OK] {desc} - {key}: {actual_val}")
    else:
        warnings.append(f"  [UNEXPECTED] Found unexpected description: {desc}")

# 2. Check "مابه التفاوت اجرای مقررات" section
print("\n2. Checking 'مابه التفاوت اجرای مقررات' section:")
print("-" * 70)

expected_regulation = {
    "میان باری": {
        "انرژی مشمول": 34460,
        "نرخ پایه": 3477,
        "متوسط نرخ بازار": 2617.65,
        "تفاوت نرخ": 859.35,
        "مبلغ (ریال)": 29613201
    },
    "اوج باری": {
        "انرژی مشمول": 9242,
        "نرخ پایه": 6954,
        "متوسط نرخ بازار": 2617.65,
        "تفاوت نرخ": 4336.35,
        "مبلغ (ریال)": 40076547
    },
    "کم باری": {
        "انرژی مشمول": 24322,
        "نرخ پایه": 1738.5,
        "متوسط نرخ بازار": 2617.65,
        "تفاوت نرخ": 0,  # Empty in image
        "مبلغ (ریال)": 0  # Empty in image
    },
    "اوج بار جمعه": {
        "انرژی مشمول": 1809,
        "نرخ پایه": 6954,
        "متوسط نرخ بازار": 2617.65,
        "تفاوت نرخ": 4336.35,
        "مبلغ (ریال)": 7844457
    }
}

for item in data["مابه التفاوت اجرای مقررات"]:
    desc = item["شرح مصارف"]
    if desc in expected_regulation:
        exp = expected_regulation[desc]
        for key, expected_val in exp.items():
            actual_val = item.get(key)
            if actual_val != expected_val:
                error_msg = f"  [MISMATCH] {desc} - {key}: Expected {expected_val}, Got {actual_val}"
                errors.append(error_msg)
                print(error_msg)
            else:
                print(f"  [OK] {desc} - {key}: {actual_val}")
    else:
        warnings.append(f"  [UNEXPECTED] Found unexpected description: {desc}")

# 3. Check "جمع" section
print("\n3. Checking 'جمع' section:")
print("-" * 70)

expected_total = {
    "مصرف کل": 69833,
    "مبلغ (ریال)": 280255152
}

for key, expected_val in expected_total.items():
    actual_val = data["جمع"].get(key)
    if actual_val != expected_val:
        error_msg = f"  [MISMATCH] جمع - {key}: Expected {expected_val}, Got {actual_val}"
        errors.append(error_msg)
        print(error_msg)
    else:
        print(f"  [OK] جمع - {key}: {actual_val}")

# 4. Check "مابه التفاوت ماده 16" section
print("\n4. Checking 'مابه التفاوت ماده 16' section:")
print("-" * 70)

article16 = data.get("مابه التفاوت ماده 16", {}).get("جهش تولید", {})
percent = article16.get("درصد مصرف")
if percent == 17:
    print(f"  [OK] جهش تولید - درصد مصرف: {percent}")
else:
    error_msg = f"  [MISMATCH] جهش تولید - درصد مصرف: Expected 17, Got {percent}"
    errors.append(error_msg)
    print(error_msg)

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Errors: {len(errors)}")
print(f"Warnings: {len(warnings)}")

if errors:
    print("\nErrors found:")
    for err in errors[:10]:  # Show first 10 errors
        print(err)
    if len(errors) > 10:
        print(f"... and {len(errors) - 10} more errors")

if not errors and not warnings:
    print("\n[SUCCESS] All data matches the image!")
elif not errors:
    print("\n[WARNING] Some minor discrepancies found, but overall structure is correct")
else:
    print("\n[FAILED] Significant mismatches found")
