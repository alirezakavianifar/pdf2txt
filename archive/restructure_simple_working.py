"""Simple working restructure script."""
import json
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
    """Restructure JSON using direct line-by-line parsing."""
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
    
    consumption_count = 0
    
    for line in lines:
        line = line.strip()
        if not line or len(line) < 20:
            continue
        
        parts = line.split()
        nums = []
        for p in parts:
            try:
                # Try int first
                n = int(p.replace(',', ''))
                if n != 0:
                    nums.append(n)
            except ValueError:
                try:
                    # Try float
                    n = float(p.replace(',', ''))
                    if n != 0:
                        nums.append(n)
                except ValueError:
                    pass
        
        if len(nums) < 10:
            continue
        
        # Check if it's a consumption row: TOU < 100, has large amount
        is_consumption = nums[0] < 100 and any(n > 1000000 for n in nums)
        is_regulation = any(isinstance(n, float) and 2500 <= n <= 3000 for n in nums) and not is_consumption
        is_total = "جمع" in line or any(50000 <= n <= 200000 for n in nums) and any(n > 50000000 for n in nums)
        
        if is_consumption:
            tou = int(nums[0])
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
                    elif energy is None:
                        energy = int(n)
                elif isinstance(n, float) and 1000 <= n <= 10000:
                    rate = float(n) if rate is None else rate
                elif n > 1000000:
                    amount = int(n) if amount is None else amount
            
            if consumption and rate and amount:
                # Determine description by rate and position
                if consumption_count == 0:
                    desc = "میان باری"
                elif consumption_count == 1:
                    desc = "اوج باری"
                elif consumption_count == 2:
                    desc = "کم باری"
                else:
                    desc = "اوج بار جمعه"
                
                results["شرح مصارف"].append({
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
                consumption_count += 1
        
        elif is_regulation:
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
                        if base_rate is None or (base_rate < 5000 and n > 5000):
                            base_rate = float(n)
                elif isinstance(n, (int, float)) and 0 < n <= 10000:
                    if n not in [energy, base_rate, avg_market] and (rate_diff is None or n > rate_diff):
                        rate_diff = float(n)
                elif n > 1000000:
                    amount = int(n)
            
            if energy and base_rate and avg_market:
                # Determine description
                if base_rate > 10000:
                    desc = "اوج باری"
                elif base_rate < 3000:
                    desc = "کم باری"
                else:
                    desc = "میان باری"
                
                # Check if already exists
                existing = [r for r in results["مابه التفاوت اجرای مقررات"] if r["شرح مصارف"] == desc]
                if not existing:
                    results["مابه التفاوت اجرای مقررات"].append({
                        "شرح مصارف": desc,
                        "انرژی مشمول": energy,
                        "نرخ پایه": base_rate,
                        "متوسط نرخ بازار": avg_market,
                        "تفاوت نرخ": rate_diff if rate_diff else 0,
                        "مبلغ (ریال)": amount if amount else 0
                    })
        
        elif is_total:
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
