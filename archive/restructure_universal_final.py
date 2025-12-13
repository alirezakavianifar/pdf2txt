"""Universal restructure script that handles different PDF formats."""
import json
from pathlib import Path
from typing import List, Any, Optional


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


def extract_numbers_from_line(line: str) -> List[Any]:
    """Extract all numbers from a line."""
    numbers = []
    parts = line.split()
    for part in parts:
        try:
            n = int(part.replace(',', ''))
            if n != 0:
                numbers.append(n)
        except ValueError:
            try:
                n = float(part.replace(',', ''))
                if n != 0:
                    numbers.append(n)
            except ValueError:
                pass
    return numbers


def extract_consumption_row(text: str, description_marker: str = None) -> List[Dict[str, Any]]:
    """
    Extract consumption rows from text.
    Pattern: TOU prev_meter curr_meter coefficient consumption ... energy rate amount
    """
    results = []
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if len(line) < 25:  # Reduced threshold
            continue
        
        nums = extract_numbers_from_line(line)
        if len(nums) < 10:
            continue
        
        # Consumption rows have: TOU (< 100), meters, coef, consumption, ... energy, rate, large amount
        has_tou = len(nums) > 0 and nums[0] < 100
        has_large_amount = any(n > 1000000 for n in nums)
        
        if not (has_tou and has_large_amount):
            continue
        
        # Skip regulation difference rows (they have market rates in first 10 nums typically)
        # But allow consumption rows that might have market rates later
        early_market_rate = any(isinstance(n, float) and 2500 <= n <= 3000 for n in nums[:8])
        # If market rate is very early (first 5), it's likely regulation row
        very_early_market_rate = any(isinstance(n, float) and 2500 <= n <= 3000 for n in nums[:5])
        if very_early_market_rate:
            continue
        
        # Extract values
        tou = int(nums[0])
        prev_meter = nums[1] if nums[1] < 100000 else 0
        curr_meter = nums[2] if nums[2] < 100000 else 0
        coef = int(nums[3]) if nums[3] < 10000 else 1
        
        consumption = None
        energy = None
        rate = None
        amount = None
        
        # Find consumption (appears early, 1000-200000)
        for n in nums:
            if 1000 <= n <= 200000:
                if consumption is None:
                    consumption = int(n)
                elif energy is None and abs(n - consumption) > 50:
                    energy = int(n)
        
        # Find rate (decimal, 1000-10000)
        for n in nums:
            if isinstance(n, float) and 1000 <= n <= 10000:
                rate = float(n)
                break
        
        # Find amount (large number)
        for n in nums:
            if n > 1000000:
                amount = int(n)
                break
        
        if consumption and rate and amount:
            # Determine description by checking rate patterns
            if tou == 0 or amount == 0:
                desc = "اوج بار جمعه"
            elif rate > 4500:
                desc = "اوج باری"
            elif rate < 3000:
                desc = "کم باری"
            else:
                desc = "میان باری"
            
            # Avoid duplicates
            if not any(r["شرح مصارف"] == desc for r in results):
                results.append({
                    "شرح مصارف": desc,
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
    
    # Sort by typical order: میان باری, اوج باری, کم باری, اوج بار جمعه
    order = {"میان باری": 0, "اوج باری": 1, "کم باری": 2, "اوج بار جمعه": 3}
    results.sort(key=lambda x: order.get(x["شرح مصارف"], 99))
    
    return results


def extract_regulation_differences(text: str) -> List[Dict[str, Any]]:
    """Extract regulation difference rows."""
    results = []
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if len(line) < 20:
            continue
        
        nums = extract_numbers_from_line(line)
        if len(nums) < 3:
            continue
        
        # Must have market rate indicator
        has_market_rate = any(isinstance(n, float) and 2500 <= n <= 3000 for n in nums)
        if not has_market_rate:
            continue
        
        # Skip if it looks like consumption row
        if nums[0] < 100 and any(n > 1000000 for n in nums):
            continue
        
        energy = None
        base_rate = None
        avg_market = None
        rate_diff = None
        amount = None
        
        for n in nums:
            # Energy (4-6 digits)
            if 1000 <= n <= 200000 and isinstance(n, (int, float)):
                if energy is None:
                    energy = int(n)
            # Average market rate (specific range)
            elif isinstance(n, float) and 2500 <= n <= 3000:
                avg_market = float(n)
            # Base rate (varies by load type: 2000-12000)
            elif isinstance(n, (int, float)) and 2000 <= n <= 12000:
                if avg_market is None or abs(n - avg_market) > 100:
                    if base_rate is None or (base_rate < 5000 and n > 5000):
                        base_rate = float(n)
            # Rate difference
            elif isinstance(n, (int, float)) and 0 < n <= 10000:
                if n not in [energy, base_rate, avg_market]:
                    if rate_diff is None or (n > rate_diff and rate_diff < 5000):
                        rate_diff = float(n)
            # Amount
            elif n > 1000000:
                amount = int(n) if amount is None else amount
        
        if energy and base_rate and avg_market:
            # Determine description
            if base_rate > 10000:
                desc = "اوج باری"
            elif base_rate < 3000:
                desc = "کم باری"
            else:
                desc = "میان باری"
            
            # Avoid duplicates
            if not any(r["شرح مصارف"] == desc for r in results):
                results.append({
                    "شرح مصارف": desc,
                    "انرژی مشمول": energy,
                    "نرخ پایه": base_rate,
                    "متوسط نرخ بازار": avg_market,
                    "تفاوت نرخ": rate_diff if rate_diff else 0,
                    "مبلغ (ریال)": amount if amount else 0
                })
    
    # Sort by typical order
    order = {"میان باری": 0, "اوج باری": 1, "کم باری": 2, "اوج بار جمعه": 3}
    results.sort(key=lambda x: order.get(x["شرح مصارف"], 99))
    
    return results


def extract_total(text: str) -> Dict[str, Any]:
    """Extract total values."""
    total = {"مصرف کل": 0, "مبلغ (ریال)": 0}
    lines = text.split('\n')
    
    for line in lines:
        if "جمع" in line:
            nums = extract_numbers_from_line(line)
            for n in nums:
                if 10000 <= n <= 200000:
                    total["مصرف کل"] = int(n)
                elif n > 10000000:
                    total["مبلغ (ریال)"] = int(n)
            if total["مصرف کل"] > 0 or total["مبلغ (ریال)"] > 0:
                break
    
    return total


def restructure_json(input_path: Path, output_path: Path):
    """Restructure JSON using flexible extraction methods."""
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    text = data.get('text', '')
    
    # Extract all sections
    results = {
        "شرح مصارف": extract_consumption_row(text),
        "مابه التفاوت ماده 16": {"جهش تولید": {"درصد مصرف": 17, "مبلغ (ریال)": 0}},
        "مابه التفاوت اجرای مقررات": extract_regulation_differences(text),
        "جمع": extract_total(text)
    }
    
    # Save output
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"Restructured data saved to: {output_path}")
    print(f"Extracted {len(results['شرح مصارف'])} consumption descriptions")
    print(f"Extracted {len(results['مابه التفاوت اجرای مقررات'])} regulation differences")
    total_str = f"consumption={results['جمع'].get('مصرف کل', 0)}, amount={results['جمع'].get('مبلغ (ریال)', 0)}"
    print(f"Total: {total_str}")
    
    return results


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        input_file = Path(sys.argv[1])
    else:
        input_file = Path("output/4_550_9000310904123_energy_supported_section.json")
    
    output_file = input_file.parent / f"{input_file.stem}_restructured.json"
    
    result = restructure_json(input_file, output_file)
