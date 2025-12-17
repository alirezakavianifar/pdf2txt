
from pathlib import Path
import json
import re
from text_normalization import default_normalizer

def restructure_consumption_table_template4_json(json_path: Path, output_path: Path):
    """
    Restructures Consumption Table (Template 4).
    """
    print(f"Restructuring Consumption Table (Template 4) from {json_path}...")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Don't apply bidi - it reverses already correct RTL text
        text = default_normalizer.normalize(data.get("text", ""), apply_bidi=False)
        lines = text.split('\n')
        
        rows = []
        
        for line in lines:
            row_name = None
            if "میان" in line or "Mid" in line:
                row_name = "میان باری"
            elif "اوج بار" in line and "جمعه" not in line:
                row_name = "اوج بار"
            elif "کم باری" in line:
                row_name = "کم باری"
            elif "جمعه" in line:
                row_name = "اوج بار جمعه"
            elif "راکتیو" in line or "اکتیو" in line:
                row_name = "راکتیو"
            else:
                continue
            
            nums = re.findall(r"[-+]?\d[\d,]*", line)
            nums = [float(n.replace(',', '')) for n in nums]
            
            entry = {"شرح": row_name}
            if len(nums) >= 2:
                entry["شمارنده_قبلی"] = nums[0]
                entry["شمارنده_کنونی"] = nums[1]
            if len(nums) >= 3:
                entry["مصرف_کل"] = nums[2]
            if len(nums) >= 4:
                entry["خرید_از_دوجانبه"] = nums[3]
            if len(nums) >= 5:
                entry["خرید_از_بورس"] = nums[4]
            if len(nums) >= 6:
                entry["خرید_از_بورس_سبز"] = nums[5]
            
            rows.append(entry)
            
        result = {"جدول_مصرف": rows}
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        return result

    except Exception as e:
        print(f"Error restructuring Consumption T4: {e}")
        return None
