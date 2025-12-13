"""Table-based restructure with flexible position detection."""
import json
from pathlib import Path
from typing import List, Optional


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


def extract_from_table_row(row: List[str], row_index: int, text: str) -> Optional[dict]:
    """Extract consumption data from a table row."""
    if not row:
        return None
    
    # Find values by scanning the row
    amount = None
    rate = None
    consumption = None
    energy = None
    coefficient = None
    curr_meter = None
    prev_meter = None
    
    # Amount is usually at the beginning (large number)
    for cell in row[:5]:
        if cell:
            # Handle cells with commas like "40,078,976"
            cell_str = str(cell).replace(',', '').strip()
            try:
                val = int(cell_str)
                if val > 1000000:
                    amount = val
                    break
            except:
                val = parse_number(cell)
                if isinstance(val, (int, float)) and val > 1000000:
                    amount = int(val)
                    break
    
    # Rate is usually near the beginning (decimal)
    for cell in row[:10]:
        if cell:
            val = parse_number(cell)
            if isinstance(val, float) and 1000 <= val <= 10000:
                rate = float(val)
                break
    
    # Consumption/energy (4-6 digit numbers)
    # Some cells contain multiple values like "17456 0 0"
    consumption_values = []
    for cell in row:
        if cell:
            # Try parsing cell as single value first
            val = parse_number(cell)
            if isinstance(val, (int, float)) and 1000 <= val <= 200000:
                consumption_values.append(int(val))
            else:
                # Try splitting cell (may contain multiple numbers)
                parts = str(cell).split()
                for part in parts:
                    try:
                        n = int(part.replace(',', ''))
                        if 1000 <= n <= 200000:
                            consumption_values.append(n)
                    except:
                        try:
                            n = float(part.replace(',', ''))
                            if 1000 <= n <= 200000:
                                consumption_values.append(int(n))
                        except:
                            pass
    
    if consumption_values:
        consumption = consumption_values[0]
        if len(consumption_values) > 1:
            energy = consumption_values[1]
        else:
            energy = consumption
    
    # Coefficient (common values: 1, 800, 1000, 2000)
    for cell in row:
        if cell:
            val = parse_number(cell)
            if isinstance(val, (int, float)) and val in [1, 800, 1000, 2000]:
                coefficient = int(val)
                break
    
    # Meters (numbers that could be meter readings)
    meter_values = []
    for cell in row:
        if cell:
            val = parse_number(cell)
            if isinstance(val, (int, float)) and 100 <= val <= 100000:
                meter_values.append(val)
                if len(meter_values) == 2:
                    break
    
    if len(meter_values) >= 2:
        curr_meter = meter_values[0]
        prev_meter = meter_values[1]
    
    # Extract TOU from text if possible (it's usually in the text line)
    tou = 0
    lines = text.split('\n')
    for line in lines:
        parts = line.split()
        for i, part in enumerate(parts):
            try:
                n = int(part.replace(',', ''))
                if n < 100 and i == 0:  # TOU is usually first number
                    # Check if this line corresponds to our row
                    if amount and str(amount) in line:
                        tou = n
                        break
            except:
                pass
        if tou > 0:
            break
    
    if amount and rate and consumption:
        # Determine description - use row index as hint
        if row_index == 1:
            desc = "میان باری"
            if tou == 0:
                tou = 12
        elif row_index == 2:
            desc = "اوج باری"
            if tou == 0:
                tou = 6
        elif row_index == 3:
            desc = "کم باری"
            if tou == 0:
                tou = 6
        elif row_index == 4:
            desc = "اوج بار جمعه"
        else:
            # Use rate to determine
            if rate > 4500:
                desc = "اوج باری"
            elif rate < 3000:
                desc = "کم باری"
            else:
                desc = "میان باری"
        
        return {
            "شرح مصارف": desc,
            "TOU": tou,
            "شماره کنتور قبلی": prev_meter if prev_meter else 0,
            "شماره کنتور کنونی": curr_meter if curr_meter else 0,
            "ضریب": coefficient if coefficient else 1,
            "مصرف کل": consumption,
            "گواهی صرفه جویی": {"تولید": 0, "خرید": 0, "دوجانبه": 0, "بورس": 0},
            "بهای انرژی پشتیبانی شده": {
                "انرژی مشمول": energy if energy else consumption,
                "نرخ": rate,
                "مبلغ (ریال)": amount
            }
        }
    
    return None


def extract_regulation_from_text(text: str) -> List[dict]:
    """Extract regulation differences from text."""
    results = []
    lines = text.split('\n')
    found = set()
    
    for line in lines:
        if len(line.strip()) < 20:
            continue
        
        # Extract numbers
        parts = line.split()
        nums = []
        for p in parts:
            try:
                n = int(p.replace(',', ''))
                if n != 0:
                    nums.append(n)
            except:
                try:
                    n = float(p.replace(',', ''))
                    if n != 0:
                        nums.append(n)
                except:
                    pass
        
        if len(nums) < 3:
            continue
        
        # Must have market rate
        has_market_rate = any(isinstance(n, float) and 2500 <= n <= 3000 for n in nums)
        if not has_market_rate:
            continue
        
        # Skip consumption rows
        if nums[0] < 100 and any(n > 1000000 for n in nums):
            continue
        
        energy = None
        base_rate = None
        avg_market = None
        rate_diff = None
        amount = None
        
        for n in nums:
            if 1000 <= n <= 200000:
                energy = int(n) if energy is None else energy
            elif isinstance(n, float) and 2500 <= n <= 3000:
                avg_market = float(n)
            elif isinstance(n, (int, float)) and 2000 <= n <= 12000:
                if avg_market is None or abs(n - avg_market) > 100:
                    if base_rate is None or (base_rate < 5000 and n > 5000):
                        base_rate = float(n)
            elif isinstance(n, (int, float)) and 0 < n <= 10000:
                if n not in [energy, base_rate, avg_market]:
                    if rate_diff is None or (n > rate_diff and rate_diff < 5000):
                        rate_diff = float(n)
            elif n > 1000000:
                amount = int(n)
        
        if energy and base_rate and avg_market:
            if base_rate > 10000:
                desc = "اوج باری"
            elif base_rate < 3000:
                desc = "کم باری"
            else:
                desc = "میان باری"
            
            if desc not in found:
                results.append({
                    "شرح مصارف": desc,
                    "انرژی مشمول": energy,
                    "نرخ پایه": base_rate,
                    "متوسط نرخ بازار": avg_market,
                    "تفاوت نرخ": rate_diff if rate_diff else 0,
                    "مبلغ (ریال)": amount if amount else 0
                })
                found.add(desc)
    
    order = {"میان باری": 0, "اوج باری": 1, "کم باری": 2, "اوج بار جمعه": 3}
    results.sort(key=lambda x: order.get(x["شرح مصارف"], 99))
    return results


def restructure_json(input_path: Path, output_path: Path):
    """Restructure JSON using table-based extraction."""
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
    
    # Extract consumption from table rows (rows 1-4 typically)
    for i in range(1, min(5, len(table_rows))):
        row_data = extract_from_table_row(table_rows[i], i, text)
        if row_data:
            # Check for duplicates
            existing = [r for r in results["شرح مصارف"] if r["شرح مصارف"] == row_data["شرح مصارف"]]
            if not existing:
                results["شرح مصارف"].append(row_data)
    
    # Extract regulation differences from text
    results["مابه التفاوت اجرای مقررات"] = extract_regulation_from_text(text)
    
    # Extract total
    lines = text.split('\n')
    for line in lines:
        if "جمع" in line:
            parts = line.split()
            nums = []
            for p in parts:
                try:
                    n = int(p.replace(',', ''))
                    if n != 0:
                        nums.append(n)
                except:
                    try:
                        n = float(p.replace(',', ''))
                        if n != 0:
                            nums.append(n)
                    except:
                        pass
            
            for n in nums:
                if 10000 <= n <= 200000:
                    results["جمع"]["مصرف کل"] = int(n)
                elif n > 10000000:
                    results["جمع"]["مبلغ (ریال)"] = int(n)
    
    # Sort consumption results
    order = {"میان باری": 0, "اوج باری": 1, "کم باری": 2, "اوج بار جمعه": 3}
    results["شرح مصارف"].sort(key=lambda x: order.get(x["شرح مصارف"], 99))
    
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
