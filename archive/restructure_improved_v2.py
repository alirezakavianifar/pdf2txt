"""Improved restructure script that finds cell positions dynamically."""
import json
from pathlib import Path
import sys


def parse_number(value):
    """Parse number from string, handling commas."""
    if not value or value == '':
        return 0
    value_str = str(value).strip()
    try:
        return int(value_str.replace(',', ''))
    except ValueError:
        try:
            return float(value_str.replace(',', ''))
        except ValueError:
            return value


def find_cell_with_value(row, target_value, tolerance=0.01):
    """Find cell index containing a target value."""
    for i, cell in enumerate(row):
        if cell:
            val = parse_number(cell)
            if isinstance(val, (int, float)):
                if isinstance(target_value, float):
                    if abs(val - target_value) < tolerance:
                        return i
                else:
                    if val == target_value:
                        return i
    return None


def restructure_json(input_path: Path, output_path: Path):
    """Restructure JSON dynamically from extracted data."""
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    text = data.get('text', '')
    table_rows = data.get('table', {}).get('rows', [])
    
    results = {
        "شرح مصارف": [],
        "مابه التفاوت ماده 16": {"جهش تولید": {"درصد مصرف": 17, "مبلغ (ریال)": 0}},
        "مابه التفاوت اجرای مقررات": [],
        "جمع": {}
    }
    
    # Parse from text first (more reliable)
    lines = text.split('\n')
    
    # Extract consumption data from text
    for line in lines:
        line = line.strip()
        if not line or len(line) < 20:
            continue
        
        # Pattern: "TOU prev_meter curr_meter coefficient consumption ... energy rate amount description"
        if "میان باری" in line and not "مابه التفاوت" in line:
            parts = line.split()
            nums = [parse_number(p) for p in parts]
            nums = [n for n in nums if isinstance(n, (int, float))]
            
            if len(nums) >= 13:
                results["شرح مصارف"].append({
                    "شرح مصارف": "میان باری",
                    "TOU": int(nums[0]),
                    "شماره کنتور قبلی": float(nums[1]) if nums[1] < 100000 else int(nums[1]),
                    "شماره کنتور کنونی": float(nums[2]) if nums[2] < 100000 else int(nums[2]),
                    "ضریب": int(nums[3]),
                    "مصرف کل": int(nums[4]),
                    "گواهی صرفه جویی": {"تولید": 0, "خرید": 0, "دوجانبه": 0, "بورس": 0},
                    "بهای انرژی پشتیبانی شده": {
                        "انرژی مشمول": int(nums[9]) if len(nums) > 9 else int(nums[4]),
                        "نرخ": float(nums[10]) if len(nums) > 10 else 0.0,
                        "مبلغ (ریال)": int(nums[11]) if len(nums) > 11 else 0
                    }
                })
        
        elif "اوج باری" in line and not "مابه التفاوت" in line and not "جمعه" in line:
            parts = line.split()
            nums = [parse_number(p) for p in parts]
            nums = [n for n in nums if isinstance(n, (int, float))]
            
            if len(nums) >= 13:
                results["شرح مصارف"].append({
                    "شرح مصارف": "اوج باری",
                    "TOU": int(nums[0]),
                    "شماره کنتور قبلی": float(nums[1]) if nums[1] < 100000 else int(nums[1]),
                    "شماره کنتور کنونی": float(nums[2]) if nums[2] < 100000 else int(nums[2]),
                    "ضریب": int(nums[3]),
                    "مصرف کل": int(nums[4]),
                    "گواهی صرفه جویی": {"تولید": 0, "خرید": 0, "دوجانبه": 0, "بورس": 0},
                    "بهای انرژی پشتیبانی شده": {
                        "انرژی مشمول": int(nums[9]) if len(nums) > 9 else int(nums[4]),
                        "نرخ": float(nums[10]) if len(nums) > 10 else 0.0,
                        "مبلغ (ریال)": int(nums[11]) if len(nums) > 11 else 0
                    }
                })
        
        elif "کم باری" in line and not "مابه التفاوت" in line:
            parts = line.split()
            nums = [parse_number(p) for p in parts]
            nums = [n for n in nums if isinstance(n, (int, float))]
            
            if len(nums) >= 13:
                results["شرح مصارف"].append({
                    "شرح مصارف": "کم باری",
                    "TOU": int(nums[0]),
                    "شماره کنتور قبلی": float(nums[1]) if nums[1] < 100000 else int(nums[1]),
                    "شماره کنتور کنونی": float(nums[2]) if nums[2] < 100000 else int(nums[2]),
                    "ضریب": int(nums[3]),
                    "مصرف کل": int(nums[4]),
                    "گواهی صرفه جویی": {"تولید": 0, "خرید": 0, "دوجانبه": 0, "بورس": 0},
                    "بهای انرژی پشتیبانی شده": {
                        "انرژی مشمول": int(nums[9]) if len(nums) > 9 else int(nums[4]),
                        "نرخ": float(nums[10]) if len(nums) > 10 else 0.0,
                        "مبلغ (ریال)": int(nums[11]) if len(nums) > 11 else 0
                    }
                })
        
        # Extract regulation differences
        elif ("میان باری" in line or "اوج باری" in line or "کم باری" in line) and ("2617.65" in line or "2945.77" in line):
            if "مابه التفاوت" not in line or "دیماند" in line:
                continue
            
            parts = line.split()
            nums = [parse_number(p) for p in parts]
            nums = [n for n in nums if isinstance(n, (int, float)) and n > 0]
            
            if len(nums) >= 3:
                desc = None
                if "میان باری" in line:
                    desc = "میان باری"
                elif "اوج باری" in line and "جمعه" not in line:
                    desc = "اوج باری"
                elif "کم باری" in line:
                    desc = "کم باری"
                
                if desc and not any(x["شرح مصارف"] == desc for x in results["مابه التفاوت اجرای مقررات"]):
                    # Find values: energy, base_rate, avg_market, rate_diff, amount
                    energy = None
                    base_rate = None
                    avg_market = None
                    rate_diff = None
                    amount = None
                    
                    for num in nums:
                        if 1000 <= num <= 100000:
                            if energy is None:
                                energy = int(num)
                        elif 2000 <= num <= 12000:
                            if base_rate is None or (base_rate < 3000 and num > 3000):
                                base_rate = float(num)
                        elif 2500 <= num <= 3000:
                            if avg_market is None:
                                avg_market = float(num)
                        elif 100 <= num <= 3000:
                            if rate_diff is None:
                                rate_diff = float(num)
                        elif num > 1000000:
                            amount = int(num)
                    
                    if energy and base_rate and avg_market:
                        results["مابه التفاوت اجرای مقررات"].append({
                            "شرح مصارف": desc,
                            "انرژی مشمول": energy,
                            "نرخ پایه": base_rate,
                            "متوسط نرخ بازار": avg_market,
                            "تفاوت نرخ": rate_diff if rate_diff else 0,
                            "مبلغ (ریال)": amount if amount else 0
                        })
        
        # Total
        elif "جمع" in line:
            parts = line.split()
            nums = [parse_number(p) for p in parts]
            nums = [n for n in nums if isinstance(n, (int, float)) and n > 0]
            
            for num in nums:
                if 30000 <= num <= 200000:
                    results["جمع"]["مصرف کل"] = int(num)
                elif num > 90000000:
                    results["جمع"]["مبلغ (ریال)"] = int(num)
    
    # Save output
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"Restructured data saved to: {output_path}")
    print(f"Extracted {len(results['شرح مصارف'])} consumption descriptions")
    print(f"Extracted {len(results['مابه التفاوت اجرای مقررات'])} regulation differences")
    
    return results


if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_file = Path(sys.argv[1])
    else:
        input_file = Path("output/4_550_9000310904123_energy_supported_section.json")
    
    output_file = input_file.parent / f"{input_file.stem}_restructured.json"
    
    result = restructure_json(input_file, output_file)
