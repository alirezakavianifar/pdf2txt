"""Verify extraction for 4_600_9001869604126 against expected values from image."""
import json
from pathlib import Path

# Expected values from image
expected = {
    "consumption": [
        {
            "desc": "میان باری",
            "TOU": 12,
            "prev_meter": 4158.78,
            "curr_meter": 4203.08,
            "coef": 800,
            "consumption": 35440,
            "rate": 2296,
            "amount": 81370240
        },
        {
            "desc": "اوج باری",
            "TOU": 6,
            "prev_meter": 1368.58,
            "curr_meter": 1389.68,
            "coef": 800,
            "consumption": 16880,
            "rate": 4592,
            "amount": 77512960
        },
        {
            "desc": "کم باری",
            "TOU": 6,
            "prev_meter": 2625.33,
            "curr_meter": 2660.94,
            "coef": 800,
            "consumption": 28488,
            "rate": 1148,
            "amount": 32704224
        }
    ],
    "regulation": [
        {
            "desc": "میان باری",
            "base_rate": 2296,
            "avg_market": 2945.77,
            "rate_diff": 0
        },
        {
            "desc": "اوج باری",
            "base_rate": 4592,
            "avg_market": 2945.77,
            "rate_diff": 1646.23
        },
        {
            "desc": "کم باری",
            "base_rate": 1148,
            "avg_market": 2945.77,
            "rate_diff": 0
        }
    ],
    "total": {
        "consumption": 80808,
        "amount": 191587424
    }
}

def log(msg, file_handle):
    """Write to file and try to print."""
    file_handle.write(msg + "\n")
    try:
        print(msg)
    except:
        pass

def verify():
    output_file = Path("output/4_600_9001869604126_energy_supported_section_restructured.json")
    
    with open("output/verification_9001869604126.txt", "w", encoding="utf-8") as f:
        log("=" * 60, f)
        log("VERIFICATION: 4_600_9001869604126", f)
        log("=" * 60, f)
        
        if not output_file.exists():
            log(f"ERROR: {output_file} not found", f)
            return
        
        with open(output_file, 'r', encoding='utf-8') as json_file:
            actual = json.load(json_file)
        
        # Verify consumption
        log("\n--- CONSUMPTION SECTION ---", f)
        actual_consumption = actual.get("شرح مصارف", [])
        if len(actual_consumption) != len(expected["consumption"]):
            log(f"WARNING: Expected {len(expected['consumption'])} consumption rows, found {len(actual_consumption)}", f)
        
        for exp in expected["consumption"]:
            found = False
            for act in actual_consumption:
                if act["شرح مصارف"] == exp["desc"]:
                    found = True
                    log(f"\n{exp['desc']}:", f)
                    
                    # Check each field
                    fields = [
                        ("TOU", "TOU", exp["TOU"]),
                        ("prev_meter", "شماره کنتور قبلی", exp["prev_meter"]),
                        ("curr_meter", "شماره کنتور کنونی", exp["curr_meter"]),
                        ("coef", "ضریب", exp["coef"]),
                        ("consumption", "مصرف کل", exp["consumption"]),
                        ("rate", "بهای انرژی پشتیبانی شده.نرخ", exp["rate"]),
                        ("amount", "بهای انرژی پشتیبانی شده.مبلغ (ریال)", exp["amount"])
                    ]
                    
                    for field_name, path, exp_val in fields:
                        if "." in path:
                            parts = path.split(".")
                            act_val = act.get(parts[0], {}).get(parts[1])
                        else:
                            act_val = act.get(path)
                        
                        if act_val is None:
                            log(f"  {field_name}: MISSING (expected {exp_val})", f)
                        elif abs(float(act_val) - float(exp_val)) > 0.01:
                            log(f"  {field_name}: MISMATCH - got {act_val}, expected {exp_val}", f)
                        else:
                            log(f"  {field_name}: OK ({act_val})", f)
                    break
            
            if not found:
                log(f"\n{exp['desc']}: MISSING", f)
        
        # Verify regulation
        log("\n--- REGULATION DIFFERENCES ---", f)
        actual_regulation = actual.get("مابه التفاوت اجرای مقررات", [])
        if len(actual_regulation) != len(expected["regulation"]):
            log(f"WARNING: Expected {len(expected['regulation'])} regulation rows, found {len(actual_regulation)}", f)
        
        for exp in expected["regulation"]:
            found = False
            for act in actual_regulation:
                if act["شرح مصارف"] == exp["desc"]:
                    found = True
                    log(f"\n{exp['desc']}:", f)
                    
                    fields = [
                        ("base_rate", "نرخ پایه", exp["base_rate"]),
                        ("avg_market", "متوسط نرخ بازار", exp["avg_market"]),
                        ("rate_diff", "تفاوت نرخ", exp["rate_diff"])
                    ]
                    
                    for field_name, path, exp_val in fields:
                        act_val = act.get(path)
                        if act_val is None:
                            log(f"  {field_name}: MISSING (expected {exp_val})", f)
                        elif abs(float(act_val) - float(exp_val)) > 0.01:
                            log(f"  {field_name}: MISMATCH - got {act_val}, expected {exp_val}", f)
                        else:
                            log(f"  {field_name}: OK ({act_val})", f)
                    break
            
            if not found:
                log(f"\n{exp['desc']}: MISSING", f)
        
        # Verify total
        log("\n--- TOTAL SECTION ---", f)
        actual_total = actual.get("جمع", {})
        
        if not actual_total:
            log("WARNING: Total section is empty", f)
        else:
            exp_consumption = expected["total"]["consumption"]
            exp_amount = expected["total"]["amount"]
            
            act_consumption = actual_total.get("مصرف کل", 0)
            act_amount = actual_total.get("مبلغ (ریال)", 0)
            
            if act_consumption == 0:
                log(f"مصرف کل: MISSING (expected {exp_consumption})", f)
            elif abs(float(act_consumption) - float(exp_consumption)) > 0.01:
                log(f"مصرف کل: MISMATCH - got {act_consumption}, expected {exp_consumption}", f)
            else:
                log(f"مصرف کل: OK ({act_consumption})", f)
            
            if act_amount == 0:
                log(f"مبلغ (ریال): MISSING (expected {exp_amount})", f)
            elif abs(float(act_amount) - float(exp_amount)) > 0.01:
                log(f"مبلغ (ریال): MISMATCH - got {act_amount}, expected {exp_amount}", f)
            else:
                log(f"مبلغ (ریال): OK ({act_amount})", f)
        
        log("\n" + "=" * 60, f)
        log("Verification complete. See output/verification_9001869604126.txt for details.", f)

if __name__ == "__main__":
    verify()
