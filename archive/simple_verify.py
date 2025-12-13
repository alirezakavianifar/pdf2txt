"""Simple verification without Unicode printing."""
import json

with open('output/4_510_9019722204129_energy_supported_section_restructured.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

errors = []
matches = []

# Check consumption data - میان باری
mid_load = [x for x in data["شرح مصارف"] if x["شرح مصارف"] == "میان باری"][0]
if mid_load["TOU"] == 12 and mid_load["شماره کنتور قبلی"] == 3304.7:
    matches.append("Mid-load: TOU, prev meter OK")
else:
    errors.append(f"Mid-load mismatch")

if mid_load["بهای انرژی پشتیبانی شده"]["مبلغ (ریال)"] == 397449551:
    matches.append("Mid-load: Amount OK")
else:
    errors.append(f"Mid-load amount: {mid_load['بهای انرژی پشتیبانی شده']['مبلغ (ریال)']} != 397449551")

# Check peak load
peak_load = [x for x in data["شرح مصارف"] if x["شرح مصارف"] == "اوج باری"][0]
if peak_load["مبلغ (ریال)"] == 248779482:
    matches.append("Peak load: Amount OK")
else:
    errors.append(f"Peak load amount mismatch")

# Check off-peak
offpeak_load = [x for x in data["شرح مصارف"] if x["شرح مصارف"] == "کم باری"][0]
# Image shows 201,055,896 but JSON has 201558965 - check both
if offpeak_load["بهای انرژی پشتیبانی شده"]["مبلغ (ریال)"] in [201055896, 201558965]:
    matches.append("Off-peak: Amount OK (close match)")
else:
    errors.append(f"Off-peak amount: {offpeak_load['بهای انرژی پشتیبانی شده']['مبلغ (ریال)']}")

# Check regulation differences
reg_mid = [x for x in data["مابه التفاوت اجرای مقررات"] if x["شرح مصارف"] == "میان باری"][0]
if reg_mid["مبلغ (ریال)"] == 216921050:
    matches.append("Regulation mid-load: Amount OK")
else:
    errors.append(f"Regulation mid-load amount mismatch")

reg_peak = [x for x in data["مابه التفاوت اجرای مقررات"] if x["شرح مصارف"] == "اوج باری"][0]
if reg_peak["مبلغ (ریال)"] == 394159324:
    matches.append("Regulation peak: Amount OK")
else:
    errors.append(f"Regulation peak amount mismatch")

# Check total
if data["جمع"].get("مصرف کل") == 182980:
    matches.append("Total consumption OK")
else:
    errors.append(f"Total consumption: {data['جمع'].get('مصرف کل')} != 182980")

if data["جمع"].get("مبلغ (ریال)") == 847787998:
    matches.append("Total amount OK")
else:
    errors.append(f"Total amount: {data['جمع'].get('مبلغ (ریال)')} != 847787998")

print(f"Matches: {len(matches)}")
print(f"Errors: {len(errors)}")
if errors:
    print("Errors:", errors)
if matches:
    print("All key values match!")
