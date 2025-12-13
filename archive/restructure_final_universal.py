"""Final universal restructure script using number-based pattern matching."""
import json
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


def extract_consumption_from_line(line: str, line_index: int, expected_order: List[str]) -> Optional[Dict[str, Any]]:
    """
    Extract consumption data from a line based on number patterns.
    expected_order is list of expected descriptions in order of appearance.
    """
    nums = extract_numbers(line)
    if len(nums) < 10:
        return None
    
    # Pattern: TOU, prev_meter, curr_meter, coefficient, consumption, zeros..., energy, rate, amount
    # Check if it looks like a consumption row (has TOU < 100 and large amount > 1M)
    has_tou = nums[0] < 100
    has_large_amount = any(n > 1000000 for n in nums)
    
    if not (has_tou and has_large_amount):
        return None
    
    tou = int(nums[0]) if nums[0] < 100 else 0
    prev_meter = nums[1] if nums[1] < 100000 else 0
    curr_meter = nums[2] if nums[2] < 100000 else 0
    coef = int(nums[3]) if nums[3] < 10000 else 1
    
    consumption = None
    energy = None
    rate = None
    amount = None
    
    # Find consumption (typically appears early, 1000-100000)
    for n in nums:
        if 1000 <= n <= 100000:
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
        if n > 10000000:
            amount = int(n)
            break
    
    if not (consumption and rate and amount):
        return None
    
    # Determine description based on position in expected order
    # We'll use line_index to estimate, but it's not perfect
    # Better to check text for keywords if possible
    description_map = {
        0: "میان باری",
        1: "اوج باری", 
        2: "کم باری",
        3: "اوج بار جمعه"
    }
    
    description = description_map.get(line_index % 4, "میان باری")
    
    # Try to detect from numbers - Friday usually has TOU=0 or no TOU
    if tou == 0 and amount == 0:
        description = "اوج بار جمعه"
    # Peak usually has higher rate
    elif rate and rate > 4500:
        description = "اوج باری"
    # Off-peak has lower rate
    elif rate and rate < 3000:
        description = "کم باری"
    
    return {
        "شرح مصارف": description,
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
    }


def extract_regulation_from_line(line: str) -> Optional[Dict[str, Any]]:
    """Extract regulation difference from line."""
    nums = extract_numbers(line)
    if len(nums) < 3:
        return None
    
    # Must have market rate indicator
    has_market_rate = any(isinstance(n, float) and 2500 <= n <= 3000 for n in nums)
    if not has_market_rate:
        return None
    
    energy = None
    base_rate = None
    avg_market = None
    rate_diff = None
    amount = None
    
    for n in nums:
        if 1000 <= n <= 100000:
            energy = int(n) if energy is None else energy
        elif isinstance(n, float) and 2500 <= n <= 3000:
            avg_market = float(n)
        elif isinstance(n, (int, float)) and 2000 <= n <= 12000:
            if avg_market is None or abs(n - avg_market) > 100:
                if base_rate is None or (base_rate < 3000 and n > 3000):
                    base_rate = float(n)
        elif isinstance(n, (int, float)) and 0 <= n <= 10000:
            if n not in [energy, base_rate, avg_market]:
                if rate_diff is None or (n > 0 and rate_diff == 0):
                    rate_diff = float(n) if n > 0 else 0
        elif n > 1000000:
            amount = int(n)
    
    if not (energy and base_rate and avg_market):
        return None
    
    # Determine description from context - this is tricky without text
    # We'll use rate patterns
    if base_rate and base_rate > 10000:
        description = "اوج باری"
    elif base_rate and base_rate < 3000:
        description = "کم باری"
    else:
        description = "میان باری"
    
    return {
        "شرح مصارف": description,
        "انرژی مشمول": energy,
        "نرخ پایه": base_rate,
        "متوسط نرخ بازار": avg_market,
        "تفاوت نرخ": rate_diff if rate_diff is not None else 0,
        "مبلغ (ریال)": amount if amount else 0
    }


def restructure_json(input_path: Path, output_path: Path):
    """Restructure JSON using flexible pattern matching."""
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
    
    consumption_found = []
    regulation_found = []
    
    # First pass: find consumption rows
    consumption_index = 0
    for i, line in enumerate(lines):
        if len(line.strip()) < 20:
            continue
        
        # Try to extract consumption
        consumption_data = extract_consumption_from_line(line, consumption_index, ["میان باری", "اوج باری", "کم باری", "اوج بار جمعه"])
        if consumption_data:
            # Avoid duplicates by checking if we already have this description
            existing = [c for c in consumption_found if c["شرح مصارف"] == consumption_data["شرح مصارف"]]
            if not existing:
                results["شرح مصارف"].append(consumption_data)
                consumption_found.append(consumption_data)
                consumption_index += 1
        
        # Try to extract regulation difference
        regulation_data = extract_regulation_from_line(line)
        if regulation_data:
            existing = [r for r in regulation_found if r["شرح مصارف"] == regulation_data["شرح مصارف"]]
            if not existing:
                results["مابه التفاوت اجرای مقررات"].append(regulation_data)
                regulation_found.append(regulation_data)
        
        # Find total
        if "جمع" in line:
            nums = extract_numbers(line)
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
