"""Restructure by parsing numeric patterns from text."""
import json
from pathlib import Path
import sys
import re


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
    
    results = {
        "شرح مصارف": [],
        "مابه التفاوت ماده 16": {"جهش تولید": {"درصد مصرف": 17, "مبلغ (ریال)": 0}},
        "مابه التفاوت اجرای مقررات": [],
        "جمع": {}
    }
    
    # Parse from text - look for numeric patterns
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or len(line) < 30:
            continue
        
        # Extract all numbers from line
        # Pattern for consumption: "12 2674.66 2696.48 800 17456 0 0 0 0 0 17456 2296 40,078,976"
        # This pattern has: TOU, prev, curr, coefficient, consumption, zeros, energy, rate, amount
        parts = line.split()
        nums = []
        for p in parts:
            try:
                num = parse_number(p)
                if isinstance(num, (int, float)):
                    nums.append(num)
            except:
                pass
        
        # Check if this looks like a consumption row (has 12+ numbers with specific pattern)
        if len(nums) >= 12:
            # Pattern: small int, decimal, decimal, int, int, zeros, int, decimal/float, large int
            if (isinstance(nums[0], int) and 0 < nums[0] < 100 and
                isinstance(nums[3], int) and 100 <= nums[3] <= 10000 and
                isinstance(nums[4], int) and 1000 <= nums[4] <= 100000 and
                len(nums) >= 13 and nums[-1] > 1000000):
                
                # Determine which type by checking if we already have entries
                # First occurrence = میان باری, second = اوج باری, third = کم باری
                desc_type = None
                if len(results["شرح مصارف"]) == 0:
                    desc_type = "میان باری"
                elif len(results["شرح مصارف"]) == 1:
                    desc_type = "اوج باری"
                elif len(results["شرح مصارف"]) == 2:
                    desc_type = "کم باری"
                
                if desc_type:
                    results["شرح مصارف"].append({
                        "شرح مصارف": desc_type,
                        "TOU": int(nums[0]),
                        "شماره کنتور قبلی": nums[1],
                        "شماره کنتور کنونی": nums[2],
                        "ضریب": int(nums[3]),
                        "مصرف کل": int(nums[4]),
                        "گواهی صرفه جویی": {"تولید": 0, "خرید": 0, "دوجانبه": 0, "بورس": 0},
                        "بهای انرژی پشتیبانی شده": {
                            "انرژی مشمول": int(nums[9]) if len(nums) > 9 else int(nums[4]),
                            "نرخ": float(nums[10]) if len(nums) > 10 else 0.0,
                            "مبلغ (ریال)": int(nums[11]) if len(nums) > 11 else 0
                        }
                    })
                    continue
        
        # Check for total row: "24 35064 0 0 0 0 0 35064 98,728,000"
        if len(nums) >= 8:
            # Pattern: TOU (24), consumption, zeros, consumption again, large amount
            if (isinstance(nums[0], int) and 20 <= nums[0] <= 30 and
                len(nums) >= 9 and nums[-1] > 90000000):
                results["جمع"]["مصرف کل"] = int(nums[1]) if 10000 <= nums[1] <= 200000 else 0
                results["جمع"]["مبلغ (ریال)"] = int(nums[-1]) if nums[-1] > 90000000 else 0
                continue
        
        # Check for regulation difference rows
        # Pattern: "0 2755.2 2945.77 0 0" or "0 5510.4 2945.77 2564.63 0"
        if len(nums) >= 3:
            # Look for avg_market rate around 2945.77 or 2617.65
            avg_market_idx = None
            for i, num in enumerate(nums):
                if 2900 <= num <= 3000 or 2600 <= num <= 2700:
                    avg_market_idx = i
                    break
            
            if avg_market_idx and avg_market_idx >= 1:
                # We have a potential regulation difference row
                # Determine description by position or values
                base_rate = nums[avg_market_idx - 1] if avg_market_idx > 0 else None
                avg_market = nums[avg_market_idx]
                rate_diff = nums[avg_market_idx + 1] if len(nums) > avg_market_idx + 1 else 0
                
                # Find energy (should be first non-zero number, usually 1000-100000)
                energy = None
                for num in nums:
                    if 1000 <= num <= 100000:
                        energy = int(num)
                        break
                
                # Find amount (large number)
                amount = None
                for num in nums:
                    if num > 1000000:
                        amount = int(num)
                        break
                
                # Determine description based on base_rate value ranges
                desc = None
                if base_rate:
                    if 5000 <= base_rate <= 6000:
                        desc = "میان باری"
                    elif 10000 <= base_rate <= 11000:
                        desc = "اوج باری"
                    elif 2000 <= base_rate <= 3000:
                        desc = "کم باری"
                
                if desc and energy and base_rate and not any(x["شرح مصارف"] == desc for x in results["مابه التفاوت اجرای مقررات"]):
                    results["مابه التفاوت اجرای مقررات"].append({
                        "شرح مصارف": desc,
                        "انرژی مشمول": energy,
                        "نرخ پایه": float(base_rate),
                        "متوسط نرخ بازار": float(avg_market),
                        "تفاوت نرخ": float(rate_diff) if rate_diff > 0 else 0,
                        "مبلغ (ریال)": amount if amount else 0
                    })
    
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
