"""Robust restructure script using flexible pattern matching."""
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
    
    # Track which descriptions we've found to avoid duplicates
    found_consumption = set()
    found_regulation = set()
    
    for line in lines:
        line = line.strip()
        if not line or len(line) < 20:
            continue
        
        nums = extract_numbers(line)
        if len(nums) < 5:
            continue
        
        # Check for consumption rows - look for pattern with large amount and description
        # Pattern varies but usually: numbers... description at end
        
        # میان باری - consumption
        if "میان" in line and "باری" in line and "2617.65" not in line and "2945.77" not in line and "میان باری" not in found_consumption:
            if len(nums) >= 10:
                # Find TOU (first small number)
                tou = int(nums[0]) if nums[0] < 100 else 12
                # Find meters (could be decimals)
                prev_meter = nums[1] if nums[1] < 100000 else 0
                curr_meter = nums[2] if nums[2] < 100000 else 0
                # Find coefficient
                coef = int(nums[3]) if nums[3] < 10000 else 1
                # Find consumption
                consumption = None
                energy = None
                rate = None
                amount = None
                
                for n in nums:
                    if 1000 <= n <= 100000:
                        if consumption is None:
                            consumption = int(n)
                        elif energy is None and abs(n - consumption) > 100:
                            energy = int(n)
                    elif isinstance(n, float) and 1000 <= n <= 10000:
                        rate = float(n) if rate is None else rate
                    elif n > 10000000:
                        amount = int(n) if amount is None else amount
                
                if consumption and rate and amount:
                    results["شرح مصارف"].append({
                        "شرح مصارف": "میان باری",
                        "TOU": tou,
                        "شماره کنتور قبلی": prev_meter,
                        "شماره کنتور کنونی": curr_meter,
                        "ضریب": coef,
                        "مصرف کل": consumption,
                        "گواهی صرفه جویی": {"تولید": 0, "خرید": 0, "دوجانبه": 0, "بورس": 0},
                        "بهای انرژی پشتیبانی شده": {
                            "انرژی مشمول": energy if energy else consumption,
                            "نرخ": rate,
                            "مبلغ (ریال)": amount
                        }
                    })
                    found_consumption.add("میان باری")
        
        # اوج باری - consumption (not Friday)
        elif "اوج" in line and "باری" in line and "جمعه" not in line and "2617.65" not in line and "2945.77" not in line and "اوج باری" not in found_consumption:
            if len(nums) >= 10:
                tou = int(nums[0]) if nums[0] < 100 else 6
                prev_meter = nums[1] if nums[1] < 100000 else 0
                curr_meter = nums[2] if nums[2] < 100000 else 0
                coef = int(nums[3]) if nums[3] < 10000 else 1
                consumption = None
                energy = None
                rate = None
                amount = None
                
                for n in nums:
                    if 1000 <= n <= 100000:
                        if consumption is None:
                            consumption = int(n)
                        elif energy is None and abs(n - consumption) > 100:
                            energy = int(n)
                    elif isinstance(n, float) and 1000 <= n <= 10000:
                        rate = float(n) if rate is None else rate
                    elif n > 10000000:
                        amount = int(n) if amount is None else amount
                
                if consumption and rate and amount:
                    results["شرح مصارف"].append({
                        "شرح مصارف": "اوج باری",
                        "TOU": tou,
                        "شماره کنتور قبلی": prev_meter,
                        "شماره کنتور کنونی": curr_meter,
                        "ضریب": coef,
                        "مصرف کل": consumption,
                        "گواهی صرفه جویی": {"تولید": 0, "خرید": 0, "دوجانبه": 0, "بورس": 0},
                        "بهای انرژی پشتیبانی شده": {
                            "انرژی مشمول": energy if energy else consumption,
                            "نرخ": rate,
                            "مبلغ (ریال)": amount
                        }
                    })
                    found_consumption.add("اوج باری")
        
        # کم باری - consumption
        elif "کم" in line and "باری" in line and "2617.65" not in line and "2945.77" not in line and "کم باری" not in found_consumption:
            if len(nums) >= 10:
                tou = int(nums[0]) if nums[0] < 100 else 6
                prev_meter = nums[1] if nums[1] < 100000 else 0
                curr_meter = nums[2] if nums[2] < 100000 else 0
                coef = int(nums[3]) if nums[3] < 10000 else 1
                consumption = None
                energy = None
                rate = None
                amount = None
                
                for n in nums:
                    if 1000 <= n <= 100000:
                        if consumption is None:
                            consumption = int(n)
                        elif energy is None and abs(n - consumption) > 100:
                            energy = int(n)
                    elif isinstance(n, float) and 1000 <= n <= 10000:
                        rate = float(n) if rate is None else rate
                    elif n > 10000000:
                        amount = int(n) if amount is None else amount
                
                if consumption and rate and amount:
                    results["شرح مصارف"].append({
                        "شرح مصارف": "کم باری",
                        "TOU": tou,
                        "شماره کنتور قبلی": prev_meter,
                        "شماره کنتور کنونی": curr_meter,
                        "ضریب": coef,
                        "مصرف کل": consumption,
                        "گواهی صرفه جویی": {"تولید": 0, "خرید": 0, "دوجانبه": 0, "بورس": 0},
                        "بهای انرژی پشتیبانی شده": {
                            "انرژی مشمول": energy if energy else consumption,
                            "نرخ": rate,
                            "مبلغ (ریال)": amount
                        }
                    })
                    found_consumption.add("کم باری")
        
        # اوج بار جمعه
        elif "اوج" in line and "بار" in line and "جمعه" in line and "اوج بار جمعه" not in found_consumption:
            if len(nums) >= 5:
                prev_meter = nums[0] if nums[0] < 100000 else 0
                curr_meter = nums[1] if len(nums) > 1 and nums[1] < 100000 else 0
                coef = int(nums[2]) if len(nums) > 2 and nums[2] < 10000 else 1
                consumption = None
                rate = None
                amount = None
                
                for n in nums:
                    if 1000 <= n <= 100000:
                        consumption = int(n) if consumption is None else consumption
                    elif isinstance(n, float) and 1000 <= n <= 10000:
                        rate = float(n) if rate is None else rate
                    elif n > 10000000:
                        amount = int(n) if amount is None else amount
                
                if consumption or rate:
                    results["شرح مصارف"].append({
                        "شرح مصارف": "اوج بار جمعه",
                        "TOU": 0,
                        "شماره کنتور قبلی": prev_meter,
                        "شماره کنتور کنونی": curr_meter,
                        "ضریب": coef,
                        "مصرف کل": consumption if consumption else 0,
                        "گواهی صرفه جویی": {"تولید": 0, "خرید": 0, "دوجانبه": 0, "بورس": 0},
                        "بهای انرژی پشتیبانی شده": {
                            "انرژی مشمول": consumption if consumption else 0,
                            "نرخ": rate if rate else 0.0,
                            "مبلغ (ریال)": amount if amount else 0
                        }
                    })
                    found_consumption.add("اوج بار جمعه")
        
        # Regulation differences - میان باری
        elif "میان" in line and "باری" in line and ("2617.65" in line or "2945.77" in line) and "میان باری" not in found_regulation:
            if len(nums) >= 5:
                energy = None
                base_rate = None
                avg_market = None
                rate_diff = None
                amount = None
                
                for n in nums:
                    if 1000 <= n <= 100000:
                        energy = int(n) if energy is None else energy
                    elif isinstance(n, float) and 2500 <= n <= 3000:
                        avg_market = float(n) if avg_market is None else avg_market
                    elif isinstance(n, (int, float)) and 2000 <= n <= 12000:
                        if avg_market is None or abs(n - avg_market) > 100:
                            base_rate = float(n) if base_rate is None or (base_rate < 3000 and n > 3000) else base_rate
                    elif isinstance(n, (int, float)) and 0 <= n <= 10000:
                        if n not in [energy, base_rate, avg_market] and (rate_diff is None or n > rate_diff):
                            rate_diff = float(n) if n > 0 else 0
                    elif n > 1000000:
                        amount = int(n) if amount is None else amount
                
                if energy and base_rate and avg_market:
                    results["مابه التفاوت اجرای مقررات"].append({
                        "شرح مصارف": "میان باری",
                        "انرژی مشمول": energy,
                        "نرخ پایه": base_rate,
                        "متوسط نرخ بازار": avg_market,
                        "تفاوت نرخ": rate_diff if rate_diff else 0,
                        "مبلغ (ریال)": amount if amount else 0
                    })
                    found_regulation.add("میان باری")
        
        # Regulation - اوج باری
        elif "اوج" in line and "باری" in line and "جمعه" not in line and ("2617.65" in line or "2945.77" in line) and "اوج باری" not in found_regulation:
            if len(nums) >= 5:
                energy = None
                base_rate = None
                avg_market = None
                rate_diff = None
                amount = None
                
                for n in nums:
                    if 1000 <= n <= 100000:
                        energy = int(n) if energy is None else energy
                    elif isinstance(n, float) and 2500 <= n <= 3000:
                        avg_market = float(n) if avg_market is None else avg_market
                    elif isinstance(n, (int, float)) and 5000 <= n <= 12000:
                        base_rate = float(n) if base_rate is None else base_rate
                    elif isinstance(n, (int, float)) and 8000 <= n <= 9000:
                        rate_diff = float(n) if rate_diff is None else rate_diff
                    elif n > 1000000:
                        amount = int(n) if amount is None else amount
                
                if energy and base_rate and avg_market:
                    results["مابه التفاوت اجرای مقررات"].append({
                        "شرح مصارف": "اوج باری",
                        "انرژی مشمول": energy,
                        "نرخ پایه": base_rate,
                        "متوسط نرخ بازار": avg_market,
                        "تفاوت نرخ": rate_diff if rate_diff else 0,
                        "مبلغ (ریال)": amount if amount else 0
                    })
                    found_regulation.add("اوج باری")
        
        # Regulation - کم باری
        elif "کم" in line and "باری" in line and ("2617.65" in line or "2945.77" in line) and "کم باری" not in found_regulation:
            if len(nums) >= 3:
                energy = None
                base_rate = None
                avg_market = None
                
                for n in nums:
                    if 1000 <= n <= 100000:
                        energy = int(n) if energy is None else energy
                    elif isinstance(n, float) and 2500 <= n <= 3000:
                        avg_market = float(n)
                    elif isinstance(n, (int, float)) and 1000 <= n <= 3000:
                        if avg_market is None or abs(n - avg_market) > 100:
                            base_rate = float(n) if base_rate is None else base_rate
                
                if energy and base_rate and avg_market:
                    results["مابه التفاوت اجرای مقررات"].append({
                        "شرح مصارف": "کم باری",
                        "انرژی مشمول": energy,
                        "نرخ پایه": base_rate,
                        "متوسط نرخ بازار": avg_market,
                        "تفاوت نرخ": 0,
                        "مبلغ (ریال)": 0
                    })
                    found_regulation.add("کم باری")
        
        # Regulation - اوج بار جمعه
        elif "اوج" in line and "بار" in line and "جمعه" in line and ("2617.65" in line or "2945.77" in line) and "اوج بار جمعه" not in found_regulation:
            if len(nums) >= 3:
                energy = 0
                base_rate = None
                avg_market = None
                rate_diff = None
                
                for n in nums:
                    if isinstance(n, float) and 2500 <= n <= 3000:
                        avg_market = float(n)
                    elif isinstance(n, (int, float)) and 10000 <= n <= 11000:
                        base_rate = float(n)
                    elif isinstance(n, (int, float)) and 8000 <= n <= 9000:
                        rate_diff = float(n)
                
                if base_rate and avg_market:
                    results["مابه التفاوت اجرای مقررات"].append({
                        "شرح مصارف": "اوج بار جمعه",
                        "انرژی مشمول": energy,
                        "نرخ پایه": base_rate,
                        "متوسط نرخ بازار": avg_market,
                        "تفاوت نرخ": rate_diff if rate_diff else 0,
                        "مبلغ (ریال)": 0
                    })
                    found_regulation.add("اوج بار جمعه")
        
        # Total
        elif "جمع" in line:
            for n in nums:
                if 10000 <= n <= 200000:
                    results["جمع"]["مصرف کل"] = int(n)
                elif n > 10000000:
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
