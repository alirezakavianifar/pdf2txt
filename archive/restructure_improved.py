"""Improved dynamic restructure script."""
import json
import re
from pathlib import Path


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
    
    # Parse text line by line
    lines = text.split('\n')
    
    # Extract consumption data from text
    # Pattern examples:
    # "12 3304.7 3347.33 2000 85260 0 0 0 0 0 85260 4661.618 397,449,551 میان باری"
    # "6 1089.96 1114.49 2000 49060 0 0 0 0 0 49060 5070.923 248,779,482 اوج باری"
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check for consumption rows
        if "میان باری" in line and not "مابه التفاوت" in line:
            parts = line.split()
            nums = [parse_number(p) for p in parts]
            nums = [n for n in nums if isinstance(n, (int, float))]
            
            if len(nums) >= 13:
                results["شرح مصارف"].append({
                    "شرح مصارف": "میان باری",
                    "TOU": int(nums[0]) if nums[0] < 100 else 0,
                    "شماره کنتور قبلی": int(nums[1]) if nums[1] < 100000 else nums[1],
                    "شماره کنتور کنونی": int(nums[2]) if nums[2] < 100000 else nums[2],
                    "ضریب": int(nums[3]) if nums[3] < 10000 else 1,
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
                    "TOU": int(nums[0]) if nums[0] < 100 else 0,
                    "شماره کنتور قبلی": int(nums[1]) if nums[1] < 100000 else nums[1],
                    "شماره کنتور کنونی": int(nums[2]) if nums[2] < 100000 else nums[2],
                    "ضریب": int(nums[3]) if nums[3] < 10000 else 1,
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
                    "TOU": int(nums[0]) if nums[0] < 100 else 0,
                    "شماره کنتور قبلی": int(nums[1]) if nums[1] < 100000 else nums[1],
                    "شماره کنتور کنونی": int(nums[2]) if nums[2] < 100000 else nums[2],
                    "ضریب": int(nums[3]) if nums[3] < 10000 else 1,
                    "مصرف کل": int(nums[4]),
                    "گواهی صرفه جویی": {"تولید": 0, "خرید": 0, "دوجانبه": 0, "بورس": 0},
                    "بهای انرژی پشتیبانی شده": {
                        "انرژی مشمول": int(nums[9]) if len(nums) > 9 else int(nums[4]),
                        "نرخ": float(nums[10]) if len(nums) > 10 else 0.0,
                        "مبلغ (ریال)": int(nums[11]) if len(nums) > 11 else 0
                    }
                })
        
        elif "اوج بار جمعه" in line and not "مابه التفاوت" in line:
            parts = line.split()
            nums = [parse_number(p) for p in parts]
            nums = [n for n in nums if isinstance(n, (int, float))]
            
            # Friday might have different structure
            if len(nums) >= 11:
                # Try to find the values
                consumption = None
                rate = None
                amount = None
                prev_meter = None
                curr_meter = None
                
                for num in nums:
                    if 1000 <= num <= 100000:
                        consumption = int(num) if consumption is None else consumption
                    elif isinstance(num, float) and 1000 <= num <= 10000:
                        rate = float(num) if rate is None else rate
                    elif num > 1000000:
                        amount = int(num) if amount is None else amount
                    elif 100 <= num <= 10000:
                        if prev_meter is None:
                            prev_meter = float(num)
                        elif curr_meter is None:
                            curr_meter = float(num)
                
                if consumption:
                    results["شرح مصارف"].append({
                        "شرح مصارف": "اوج بار جمعه",
                        "TOU": 0,
                        "شماره کنتور قبلی": int(prev_meter) if prev_meter else 0,
                        "شماره کنتور کنونی": int(curr_meter) if curr_meter else 0,
                        "ضریب": 1,
                        "مصرف کل": consumption,
                        "گواهی صرفه جویی": {"تولید": 0, "خرید": 0, "دوجانبه": 0, "بورس": 0},
                        "بهای انرژی پشتیبانی شده": {
                            "انرژی مشمول": consumption,
                            "نرخ": rate if rate else 0.0,
                            "مبلغ (ریال)": amount if amount else 0
                        }
                    })
        
        # Extract total
        elif "جمع" in line and "182980" in line:
            parts = line.split()
            nums = [parse_number(p) for p in parts]
            nums = [n for n in nums if isinstance(n, (int, float)) and n > 0]
            
            consumption = None
            amount = None
            
            for num in nums:
                if 100000 <= num <= 200000:
                    consumption = int(num)
                elif num > 100000000:
                    amount = int(num)
            
            if consumption or amount:
                results["جمع"] = {
                    "مصرف کل": consumption if consumption else 0,
                    "مبلغ (ریال)": amount if amount else 0
                }
        
        # Extract regulation differences
        elif "میان باری" in line and "2617.65" in line or ("2945.77" in line and "میان باری" in line):
            parts = line.split()
            nums = [parse_number(p) for p in parts]
            nums = [n for n in nums if isinstance(n, (int, float)) and n > 0]
            
            if len(nums) >= 5:
                energy = nums[0] if 1000 <= nums[0] <= 100000 else None
                base_rate = None
                avg_market = None
                rate_diff = None
                amount = None
                
                for num in nums:
                    if 5000 <= num <= 6000:  # base_rate
                        base_rate = float(num)
                    elif 2500 <= num <= 3000:  # avg_market
                        avg_market = float(num)
                    elif 2000 <= num <= 3000:  # rate_diff
                        rate_diff = float(num)
                    elif num > 100000000:  # amount
                        amount = int(num)
                
                if energy and base_rate and avg_market:
                    results["مابه التفاوت اجرای مقررات"].append({
                        "شرح مصارف": "میان باری",
                        "انرژی مشمول": int(energy),
                        "نرخ پایه": base_rate,
                        "متوسط نرخ بازار": avg_market,
                        "تفاوت نرخ": rate_diff if rate_diff else 0,
                        "مبلغ (ریال)": amount if amount else 0
                    })
        
        elif "اوج باری" in line and "2945.77" in line:
            parts = line.split()
            nums = [parse_number(p) for p in parts]
            nums = [n for n in nums if isinstance(n, (int, float)) and n > 0]
            
            if len(nums) >= 5:
                energy = nums[0] if 1000 <= nums[0] <= 100000 else None
                base_rate = None
                avg_market = None
                rate_diff = None
                amount = None
                
                for num in nums:
                    if 10000 <= num <= 11000:  # base_rate for peak
                        base_rate = float(num)
                    elif 2500 <= num <= 3000:  # avg_market
                        avg_market = float(num)
                    elif 8000 <= num <= 8100:  # rate_diff for peak
                        rate_diff = float(num)
                    elif num > 100000000:  # amount
                        amount = int(num)
                
                if energy and base_rate and avg_market:
                    results["مابه التفاوت اجرای مقررات"].append({
                        "شرح مصارف": "اوج باری",
                        "انرژی مشمول": int(energy),
                        "نرخ پایه": base_rate,
                        "متوسط نرخ بازار": avg_market,
                        "تفاوت نرخ": rate_diff if rate_diff else 0,
                        "مبلغ (ریال)": amount if amount else 0
                    })
        
        elif "کم باری" in line and "2945.77" in line:
            parts = line.split()
            nums = [parse_number(p) for p in parts]
            nums = [n for n in nums if isinstance(n, (int, float)) and n > 0]
            
            if len(nums) >= 3:
                energy = nums[0] if 1000 <= nums[0] <= 100000 else None
                base_rate = None
                avg_market = None
                
                for num in nums:
                    if 2000 <= num <= 3000:  # base_rate
                        base_rate = float(num)
                    elif 2500 <= num <= 3000:  # avg_market
                        avg_market = float(num)
                
                if energy and base_rate and avg_market:
                    results["مابه التفاوت اجرای مقررات"].append({
                        "شرح مصارف": "کم باری",
                        "انرژی مشمول": int(energy),
                        "نرخ پایه": base_rate,
                        "متوسط نرخ بازار": avg_market,
                        "تفاوت نرخ": 0,
                        "مبلغ (ریال)": 0
                    })
        
        elif "اوج بار جمعه" in line and "2945.77" in line:
            parts = line.split()
            nums = [parse_number(p) for p in parts]
            nums = [n for n in nums if isinstance(n, (int, float)) and n > 0]
            
            if len(nums) >= 5:
                energy = 0
                base_rate = None
                avg_market = None
                rate_diff = None
                amount = 0
                
                for num in nums:
                    if 10000 <= num <= 11000:  # base_rate
                        base_rate = float(num)
                    elif 2500 <= num <= 3000:  # avg_market
                        avg_market = float(num)
                    elif 8000 <= num <= 8100:  # rate_diff
                        rate_diff = float(num)
                
                if base_rate and avg_market:
                    results["مابه التفاوت اجرای مقررات"].append({
                        "شرح مصارف": "اوج بار جمعه",
                        "انرژی مشمول": energy,
                        "نرخ پایه": base_rate,
                        "متوسط نرخ بازار": avg_market,
                        "تفاوت نرخ": rate_diff if rate_diff else 0,
                        "مبلغ (ریال)": amount
                    })
    
    # Save output
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"Restructured data saved to: {output_path}")
    print(f"Extracted {len(results['شرح مصارف'])} consumption descriptions")
    print(f"Extracted {len(results['مابه التفاوت اجرای مقررات'])} regulation differences")
    
    return results


if __name__ == "__main__":
    input_file = Path("output/4_510_9019722204129_energy_supported_section.json")
    output_file = Path("output/4_510_9019722204129_energy_supported_section_restructured.json")
    
    result = restructure_json(input_file, output_file)
