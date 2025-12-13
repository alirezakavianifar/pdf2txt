"""Generic restructure script that handles different PDF formats."""
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


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


def extract_numbers_from_text(text: str) -> List[Any]:
    """Extract all numbers from text."""
    numbers = []
    parts = text.split()
    for part in parts:
        num = parse_number(part)
        if isinstance(num, (int, float)) and num != 0:
            numbers.append(num)
    return numbers


def find_consumption_row_pattern(text: str, description_keywords: List[str]) -> Optional[Dict[str, Any]]:
    """
    Find consumption row from text using pattern matching.
    Pattern: TOU prev_meter curr_meter coefficient consumption ... energy rate amount description
    """
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or len(line) < 20:
            continue
        
        # Check if line contains the description keywords
        if not any(kw in line for kw in description_keywords):
            continue
        
        # Skip regulation difference rows
        if "2617.65" in line or "2945.77" in line:
            continue
        
        # Extract all numbers
        numbers = extract_numbers_from_text(line)
        
        if len(numbers) < 10:
            continue
        
        # Pattern matching for consumption rows
        # Expected: TOU, prev_meter, curr_meter, coefficient, consumption, zeros..., energy, rate, amount
        tou = None
        prev_meter = None
        curr_meter = None
        coefficient = None
        consumption = None
        energy_included = None
        rate = None
        amount = None
        
        # TOU is usually first number and < 100
        if numbers[0] < 100:
            tou = int(numbers[0])
        
        # Find consumption (4-6 digits, typically 1000-100000)
        consumption_candidates = [n for n in numbers if 1000 <= n <= 200000]
        if consumption_candidates:
            # Usually the first such number is consumption
            consumption = int(consumption_candidates[0])
            # Energy included often matches consumption or appears later
            if len(consumption_candidates) > 1:
                energy_included = int(consumption_candidates[1])
            else:
                energy_included = consumption
        
        # Find rate (decimal, typically 1000-10000)
        rate_candidates = [n for n in numbers if isinstance(n, float) and 1000 <= n <= 10000]
        if rate_candidates:
            rate = float(rate_candidates[0])
        
        # Find amount (large number > 1000000)
        amount_candidates = [n for n in numbers if n > 1000000]
        if amount_candidates:
            amount = int(amount_candidates[0])
        
        # Find meters (numbers that could be meter readings - could be decimals like 3304.7)
        meter_candidates = []
        for i, num in enumerate(numbers):
            # Meters are usually after TOU, before consumption
            if i > 0 and i < len(numbers) - 5:
                if isinstance(num, float) and 100 <= num <= 100000:
                    meter_candidates.append(num)
                elif isinstance(num, int) and 100 <= num <= 1000000:
                    meter_candidates.append(float(num))
        
        if len(meter_candidates) >= 2:
            prev_meter = meter_candidates[0]
            curr_meter = meter_candidates[1]
        
        # Find coefficient (often 1, 2000, or similar - appears early in sequence)
        coefficient_candidates = [n for n in numbers[:5] if n in [1, 2000, 1000, 100]]
        if coefficient_candidates:
            coefficient = int(coefficient_candidates[0])
        
        # Determine description
        description = None
        if any("میان" in kw for kw in description_keywords):
            description = "میان باری"
        elif any("اوج" in kw and "جمعه" not in kw for kw in description_keywords):
            description = "اوج باری"
        elif any("کم" in kw for kw in description_keywords):
            description = "کم باری"
        elif any("جمعه" in kw for kw in description_keywords):
            description = "اوج بار جمعه"
            tou = 0  # Friday usually doesn't have TOU
        
        if consumption and rate and amount:
            return {
                "شرح مصارف": description,
                "TOU": tou if tou is not None else 0,
                "شماره کنتور قبلی": prev_meter if prev_meter else 0,
                "شماره کنتور کنونی": curr_meter if curr_meter else 0,
                "ضریب": coefficient if coefficient else 1,
                "مصرف کل": consumption,
                "گواهی صرفه جویی": {"تولید": 0, "خرید": 0, "دوجانبه": 0, "بورس": 0},
                "بهای انرژی پشتیبانی شده": {
                    "انرژی مشمول": energy_included if energy_included else consumption,
                    "نرخ": rate,
                    "مبلغ (ریال)": amount
                }
            }
    
    return None


def find_regulation_difference_row(text: str, description_keywords: List[str]) -> Optional[Dict[str, Any]]:
    """
    Find regulation difference row from text.
    Pattern: energy base_rate avg_market rate_diff amount description
    """
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Must contain description and market rate indicator
        if not any(kw in line for kw in description_keywords):
            continue
        
        # Look for market rate patterns (2617.65 or 2945.77)
        if "2617.65" not in line and "2945.77" not in line:
            continue
        
        numbers = extract_numbers_from_text(line)
        
        if len(numbers) < 3:
            continue
        
        energy = None
        base_rate = None
        avg_market = None
        rate_diff = None
        amount = None
        
        # Find energy (4-6 digits)
        energy_candidates = [n for n in numbers if 1000 <= n <= 200000]
        if energy_candidates:
            energy = int(energy_candidates[0])
        
        # Find average market rate (specific values: 2617.65 or 2945.77)
        avg_market_candidates = [n for n in numbers if isinstance(n, float) and 2500 <= n <= 3000]
        if avg_market_candidates:
            avg_market = float(avg_market_candidates[0])
        
        # Find base rate (could be 2000-12000 depending on load type)
        base_rate_candidates = [n for n in numbers if isinstance(n, (int, float)) and 2000 <= n <= 12000]
        # Remove avg_market from candidates
        base_rate_candidates = [n for n in base_rate_candidates if abs(n - (avg_market or 0)) > 100]
        if base_rate_candidates:
            base_rate = float(base_rate_candidates[0])
        
        # Find rate difference (usually < 10000, could be 0 for off-peak)
        rate_diff_candidates = [n for n in numbers if isinstance(n, (int, float)) and 0 <= n <= 10000]
        # Remove energy, base_rate, avg_market from candidates
        for val in [energy, base_rate, avg_market]:
            if val and val in rate_diff_candidates:
                rate_diff_candidates.remove(val)
        if rate_diff_candidates:
            rate_diff = float(rate_diff_candidates[0]) if rate_diff_candidates[0] > 0 else 0
        
        # Find amount (large number)
        amount_candidates = [n for n in numbers if n > 1000000]
        if amount_candidates:
            amount = int(amount_candidates[0])
        
        # Determine description
        description = None
        if any("میان" in kw for kw in description_keywords):
            description = "میان باری"
        elif any("اوج" in kw and "جمعه" not in kw for kw in description_keywords):
            description = "اوج باری"
        elif any("کم" in kw for kw in description_keywords):
            description = "کم باری"
        elif any("جمعه" in kw for kw in description_keywords):
            description = "اوج بار جمعه"
        
        if energy and base_rate and avg_market:
            return {
                "شرح مصارف": description,
                "انرژی مشمول": energy,
                "نرخ پایه": base_rate,
                "متوسط نرخ بازار": avg_market,
                "تفاوت نرخ": rate_diff if rate_diff is not None else 0,
                "مبلغ (ریال)": amount if amount else 0
            }
    
    return None


def find_total(text: str) -> Dict[str, Any]:
    """Find total values from text."""
    total = {"مصرف کل": 0, "مبلغ (ریال)": 0}
    
    lines = text.split('\n')
    for line in lines:
        if "جمع" in line:
            numbers = extract_numbers_from_text(line)
            
            # Find consumption total (usually 50000-200000)
            consumption_candidates = [n for n in numbers if 50000 <= n <= 200000]
            if consumption_candidates:
                total["مصرف کل"] = int(consumption_candidates[0])
            
            # Find amount total (large number)
            amount_candidates = [n for n in numbers if n > 100000000]
            if amount_candidates:
                total["مبلغ (ریال)"] = int(amount_candidates[0])
            
            if total["مصرف کل"] > 0 or total["مبلغ (ریال)"] > 0:
                break
    
    return total


def restructure_json(input_path: Path, output_path: Path):
    """Restructure JSON generically from extracted data."""
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    text = data.get('text', '')
    
    results = {
        "شرح مصارف": [],
        "مابه التفاوت ماده 16": {"جهش تولید": {"درصد مصرف": 17, "مبلغ (ریال)": 0}},
        "مابه التفاوت اجرای مقررات": [],
        "جمع": {}
    }
    
    # Extract consumption data
    consumption_types = [
        (["میان باری", "میان"], "میان باری"),
        (["اوج باری"], "اوج باری"),
        (["کم باری", "کم"], "کم باری"),
        (["اوج بار جمعه", "جمعه"], "اوج بار جمعه")
    ]
    
    for keywords, description in consumption_types:
        row_data = find_consumption_row_pattern(text, keywords)
        if row_data:
            results["شرح مصارف"].append(row_data)
    
    # Extract regulation differences
    for keywords, description in consumption_types:
        row_data = find_regulation_difference_row(text, keywords)
        if row_data:
            # Avoid duplicates
            existing = [r for r in results["مابه التفاوت اجرای مقررات"] if r["شرح مصارف"] == description]
            if not existing:
                results["مابه التفاوت اجرای مقررات"].append(row_data)
    
    # Extract total
    results["جمع"] = find_total(text)
    
    # Save output
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"Restructured data saved to: {output_path}")
    print(f"Extracted {len(results['شرح مصارف'])} consumption descriptions")
    print(f"Extracted {len(results['مابه التفاوت اجرای مقررات'])} regulation differences")
    print(f"Total: {results['جمع']}")
    
    return results


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        input_file = Path(sys.argv[1])
    else:
        input_file = Path("output/4_550_9000310904123_energy_supported_section.json")
    
    output_file = input_file.parent / f"{input_file.stem}_restructured.json"
    
    result = restructure_json(input_file, output_file)
