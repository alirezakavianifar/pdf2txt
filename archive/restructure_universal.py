"""Universal restructure script that works with different PDF formats."""
import json
import re
from pathlib import Path
from typing import List, Any


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


def extract_numbers(text: str) -> List[Any]:
    """Extract all numbers from text."""
    numbers = []
    parts = text.split()
    for part in parts:
        num = parse_number(part)
        if isinstance(num, (int, float)) and num != 0:
            numbers.append(num)
    return numbers


def restructure_json(input_path: Path, output_path: Path):
    """Restructure JSON using flexible text parsing."""
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    text = data.get('text', '')
    lines = text.split('\n')
    
    results = {
        "شرح مصارف": [],
        "مابه التفاوت ماده 16": {"جهش تولید": {"درصد مصرف": 17, "مبلغ (ریال)": 0}},
        "مابه التفاوت اجرای مقررات": [],
        "جمع": {}
    }
    
    # Process each line
    for line in lines:
        line = line.strip()
        if not line or len(line) < 20:
            continue
        
        nums = extract_numbers(line)
        if len(nums) < 5:
            continue
        
        # Consumption rows - pattern: numbers... description (میان باری, etc.)
        if "میان باری" in line and "2617.65" not in line and "2945.77" not in line:
            # Pattern: TOU prev curr coef consumption ... energy rate amount
            if len(nums) >= 12:
                tou = int(nums[0]) if nums[0] < 100 else 0
                prev = nums[1] if nums[1] < 100000 else 0
                curr = nums[2] if nums[2] < 100000 else 0
                coef = int(nums[3]) if nums[3] < 10000 else 1
                consumption = None
                energy = None
                rate = None
                amount = None
                
                for n in nums:
                    if 1000 <= n <= 100000 and consumption is None:
                        consumption = int(n)
                    elif 1000 <= n <= 100000 and energy is None and n != consumption:
                        energy = int(n)
                    elif isinstance(n, float) and 1000 <= n <= 10000 and rate is None:
                        rate = float(n)
                    elif n > 1000000 and amount is None:
                        amount = int(n)
                
                if consumption and rate and amount:
                    results["شرح مصارف"].append({
                        "شرح مصارف": "میان باری",
                        "TOU": tou,
                        "شماره کنتور قبلی": prev,
                        "شماره کنتور کنونی": curr,
                        "ضریب": coef,
                        "مصرف کل": consumption,
                        "گواهی صرفه جویی": {"تولید": 0, "خرید": 0, "دوجانبه": 0, "بورس": 0},
                        "بهای انرژی پشتیبانی شده": {
                            "انرژی مشمول": energy if energy else consumption,
                            "نرخ": rate,
                            "مبلغ (ریال)": amount
                        }
                    })
        
        elif "اوج باری" in line and "2617.65" not in line and "2945.77" not in line and "جمعه" not in line:
            if len(nums) >= 12:
                tou = int(nums[0]) if nums[0] < 100 else 0
                prev = nums[1] if nums[1] < 100000 else 0
                curr = nums[2] if nums[2] < 100000 else 0
                coef = int(nums[3]) if nums[3] < 10000 else 1
                consumption = None
                energy = None
                rate = None
                amount = None
                
                for n in nums:
                    if 1000 <= n <= 100000 and consumption is None:
                        consumption = int(n)
                    elif 1000 <= n <= 100000 and energy is None and n != consumption:
                        energy = int(n)
                    elif isinstance(n, float) and 1000 <= n <= 10000 and rate is None:
                        rate = float(n)
                    elif n > 1000000 and amount is None:
                        amount = int(n)
                
                if consumption and rate and amount:
                    results["شرح مصارف"].append({
                        "شرح مصارف": "اوج باری",
                        "TOU": tou,
                        "شماره کنتور قبلی": prev,
                        "شماره کنتور کنونی": curr,
                        "ضریب": coef,
                        "مصرف کل": consumption,
                        "گواهی صرفه جویی": {"تولید": 0, "خرید": 0, "دوجانبه": 0, "بورس": 0},
                        "بهای انرژی پشتیبانی شده": {
                            "انرژی مشمول": energy if energy else consumption,
                            "نرخ": rate,
                            "مبلغ (ریال)": amount
                        }
                    })
        
        elif "کم باری" in line and "2617.65" not in line and "2945.77" not in line:
            if len(nums) >= 12:
                tou = int(nums[0]) if nums[0] < 100 else 0
                prev = nums[1] if nums[1] < 100000 else 0
                curr = nums[2] if nums[2] < 100000 else 0
                coef = int(nums[3]) if nums[3] < 10000 else 1
                consumption = None
                energy = None
                rate = None
                amount = None
                
                for n in nums:
                    if 1000 <= n <= 100000 and consumption is None:
                        consumption = int(n)
                    elif 1000 <= n <= 100000 and energy is None and n != consumption:
                        energy = int(n)
                    elif isinstance(n, float) and 1000 <= n <= 10000 and rate is None:
                        rate = float(n)
                    elif n > 1000000 and amount is None:
                        amount = int(n)
                
                if consumption and rate and amount:
                    results["شرح مصارف"].append({
                        "شرح مصارف": "کم باری",
                        "TOU": tou,
                        "شماره کنتور قبلی": prev,
                        "شماره کنتور کنونی": curr,
                        "ضریب": coef,
                        "مصرف کل": consumption,
                        "گواهی صرفه جویی": {"تولید": 0, "خرید": 0, "دوجانبه": 0, "بورس": 0},
                        "بهای انرژی پشتیبانی شده": {
                            "انرژی مشمول": energy if energy else consumption,
                            "نرخ": rate,
                            "مبلغ (ریال)": amount
                        }
                    })
        
        elif "اوج بار جمعه" in line:
            if len(nums) >= 8:
                prev = nums[0] if nums[0] < 100000 else 0
                curr = nums[1] if len(nums) > 1 and nums[1] < 100000 else 0
                coef = int(nums[2]) if len(nums) > 2 and nums[2] < 10000 else 1
                consumption = None
                energy = None
                rate = None
                amount = None
                
                for n in nums:
                    if 1000 <= n <= 100000 and consumption is None:
                        consumption = int(n)
                    elif 1000 <= n <= 100000 and energy is None and n != consumption:
                        energy = int(n)
                    elif isinstance(n, float) and 1000 <= n <= 10000 and rate is None:
                        rate = float(n)
                    elif n > 1000000 and amount is None:
                        amount = int(n)
                
                if consumption or rate:
                    results["شرح مصارف"].append({
                        "شرح مصارف": "اوج بار جمعه",
                        "TOU": 0,
                        "شماره کنتور قبلی": prev,
                        "شماره کنتور کنونی": curr,
                        "ضریب": coef,
                        "مصرف کل": consumption if consumption else 0,
                        "گواهی صرفه جویی": {"تولید": 0, "خرید": 0, "دوجانبه": 0, "بورس": 0},
                        "بهای انرژی پشتیبانی شده": {
                            "انرژی مشمول": energy if energy else (consumption if consumption else 0),
                            "نرخ": rate if rate else 0.0,
                            "مبلغ (ریال)": amount if amount else 0
                        }
                    })
        
        # Regulation differences
        elif "میان باری" in line and ("2617.65" in line or "2945.77" in line):
            if len(nums) >= 5:
                energy = None
                base_rate = None
                avg_market = None
                rate_diff = None
                amount = None
                
                for n in nums:
                    if 1000 <= n <= 100000 and energy is None:
                        energy = int(n)
                    elif isinstance(n, float) and 2500 <= n <= 3000:
                        avg_market = float(n) if avg_market is None else avg_market
                    elif isinstance(n, (int, float)) and 2000 <= n <= 12000 and abs(n - (avg_market or 0)) > 100:
                        base_rate = float(n) if base_rate is None else base_rate
                    elif isinstance(n, (int, float)) and 0 <= n <= 10000 and n not in [energy, base_rate, avg_market]:
                        if rate_diff is None or (rate_diff == 0 and n > 0):
                            rate_diff = float(n)
                    elif n > 1000000:
                        amount = int(n)
                
                if energy and base_rate and avg_market:
                    existing = [r for r in results["مابه التفاوت اجرای مقررات"] if r["شرح مصارف"] == "میان باری"]
                    if not existing:
                        results["مابه التفاوت اجرای مقررات"].append({
                            "شرح مصارف": "میان باری",
                            "انرژی مشمول": energy,
                            "نرخ پایه": base_rate,
                            "متوسط نرخ بازار": avg_market,
                            "تفاوت نرخ": rate_diff if rate_diff is not None else 0,
                            "مبلغ (ریال)": amount if amount else 0
                        })
        
        elif "اوج باری" in line and ("2617.65" in line or "2945.77" in line):
            if len(nums) >= 5:
                energy = None
                base_rate = None
                avg_market = None
                rate_diff = None
                amount = None
                
                for n in nums:
                    if 1000 <= n <= 100000 and energy is None:
                        energy = int(n)
                    elif isinstance(n, float) and 2500 <= n <= 3000:
                        avg_market = float(n) if avg_market is None else avg_market
                    elif isinstance(n, (int, float)) and 2000 <= n <= 12000 and abs(n - (avg_market or 0)) > 100:
                        base_rate = float(n) if base_rate is None else base_rate
                    elif isinstance(n, (int, float)) and 0 <= n <= 10000 and n not in [energy, base_rate, avg_market]:
                        if rate_diff is None or (rate_diff < 5000 and n > rate_diff):
                            rate_diff = float(n)
                    elif n > 1000000:
                        amount = int(n)
                
                if energy and base_rate and avg_market:
                    existing = [r for r in results["مابه التفاوت اجرای مقررات"] if r["شرح مصارف"] == "اوج باری"]
                    if not existing:
                        results["مابه التفاوت اجرای مقررات"].append({
                            "شرح مصارف": "اوج باری",
                            "انرژی مشمول": energy,
                            "نرخ پایه": base_rate,
                            "متوسط نرخ بازار": avg_market,
                            "تفاوت نرخ": rate_diff if rate_diff is not None else 0,
                            "مبلغ (ریال)": amount if amount else 0
                        })
        
        elif "کم باری" in line and ("2617.65" in line or "2945.77" in line):
            if len(nums) >= 3:
                energy = None
                base_rate = None
                avg_market = None
                
                for n in nums:
                    if 1000 <= n <= 100000 and energy is None:
                        energy = int(n)
                    elif isinstance(n, float) and 2500 <= n <= 3000:
                        avg_market = float(n)
                    elif isinstance(n, (int, float)) and 2000 <= n <= 3000 and abs(n - (avg_market or 0)) > 100:
                        base_rate = float(n)
                
                if energy and base_rate and avg_market:
                    existing = [r for r in results["مابه التفاوت اجرای مقررات"] if r["شرح مصارف"] == "کم باری"]
                    if not existing:
                        results["مابه التفاوت اجرای مقررات"].append({
                            "شرح مصارف": "کم باری",
                            "انرژی مشمول": energy,
                            "نرخ پایه": base_rate,
                            "متوسط نرخ بازار": avg_market,
                            "تفاوت نرخ": 0,
                            "مبلغ (ریال)": 0
                        })
        
        elif "اوج بار جمعه" in line and ("2617.65" in line or "2945.77" in line):
            if len(nums) >= 3:
                energy = 0
                base_rate = None
                avg_market = None
                rate_diff = None
                amount = 0
                
                for n in nums:
                    if isinstance(n, float) and 2500 <= n <= 3000:
                        avg_market = float(n)
                    elif isinstance(n, (int, float)) and 10000 <= n <= 11000:
                        base_rate = float(n)
                    elif isinstance(n, (int, float)) and 8000 <= n <= 9000:
                        rate_diff = float(n)
                
                if base_rate and avg_market:
                    existing = [r for r in results["مابه التفاوت اجرای مقررات"] if r["شرح مصارف"] == "اوج بار جمعه"]
                    if not existing:
                        results["مابه التفاوت اجرای مقررات"].append({
                            "شرح مصارف": "اوج بار جمعه",
                            "انرژی مشمول": energy,
                            "نرخ پایه": base_rate,
                            "متوسط نرخ بازار": avg_market,
                            "تفاوت نرخ": rate_diff if rate_diff else 0,
                            "مبلغ (ریال)": amount
                        })
        
        # Total
        elif "جمع" in line:
            for n in nums:
                if 50000 <= n <= 200000:
                    results["جمع"]["مصرف کل"] = int(n)
                elif n > 100000000:
                    results["جمع"]["مبلغ (ریال)"] = int(n)
    
    # Save output
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"Restructured data saved to: {output_path}")
    print(f"Extracted {len(results['شرح مصارف'])} consumption descriptions")
    print(f"Extracted {len(results['مابه التفاوت اجرای مقررات'])} regulation differences")
    
    return results


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        input_file = Path(sys.argv[1])
    else:
        input_file = Path("output/4_550_9000310904123_energy_supported_section.json")
    
    output_file = input_file.parent / f"{input_file.stem}_restructured.json"
    
    result = restructure_json(input_file, output_file)
