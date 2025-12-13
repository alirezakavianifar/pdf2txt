"""Working universal restructure script."""
import json
from pathlib import Path
from typing import List, Optional


def parse_number(value):
    """Parse number from string, handling commas."""
    if not value or value == '':
        return 0
    value_str = str(value).strip().replace(',', '')
    try:
        return int(value_str)
    except ValueError:
        try:
            return float(value_str)
        except ValueError:
            return value


def restructure_json(input_path: Path, output_path: Path):
    """Restructure JSON using table rows with known structure."""
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    text = data.get('text', '')
    table_rows = data.get('table', {}).get('rows', [])
    lines = text.split('\n')
    
    results = {
        "شرح مصارف": [],
        "مابه التفاوت ماده 16": {"جهش تولید": {"درصد مصرف": 17, "مبلغ (ریال)": 0}},
        "مابه التفاوت اجرای مقررات": [],
        "جمع": {}
    }
    
    # Extract TOU values from text for each row
    tou_values = {}
    consumption_line_index = 0
    for line in lines:
        parts = line.split()
        if len(parts) > 12:
            try:
                tou = int(parts[0].replace(',', ''))
                if tou < 100:
                    # Try to find corresponding amount in this line
                    for p in parts:
                        try:
                            amount = int(p.replace(',', ''))
                            if amount > 1000000:
                                tou_values[consumption_line_index] = tou
                                consumption_line_index += 1
                                break
                        except:
                            pass
            except:
                pass
    
    # Extract consumption from table rows
    # Row 1: میان باری - [0]=amount, [1]=rate, [7]="consumption 0 0", [17]=consumption, [104]=coef, [109]=curr_meter, [113]=prev_meter
    if len(table_rows) > 1:
        row = table_rows[1]
        try:
            amount = parse_number(row[0]) if len(row) > 0 and row[0] else 0
            rate = float(parse_number(row[1])) if len(row) > 1 and row[1] else 0.0
            # Try cell 7 first (may contain "17456 0 0")
            cell7 = str(row[7]) if len(row) > 7 and row[7] else ""
            consumption_candidates = []
            if cell7:
                for part in cell7.split():
                    try:
                        n = int(part.replace(',', ''))
                        if 1000 <= n <= 200000:
                            consumption_candidates.append(n)
                    except:
                        pass
            consumption = consumption_candidates[0] if consumption_candidates else (parse_number(row[17]) if len(row) > 17 and row[17] else 0)
            # Search for coefficient and meters in the row
            coef = 1
            curr_meter = 0.0
            prev_meter = 0.0
            for i, cell in enumerate(row):
                if cell:
                    val = parse_number(cell)
                    if isinstance(val, (int, float)):
                        if val in [1, 800, 1000, 2000] and coef == 1:
                            coef = int(val)
                        # Collect meter-like values
                        elif 100 <= val <= 100000 and isinstance(val, float):
                            meter_candidates.append(float(val))
            tou = tou_values.get(0, 12)
            
            if amount > 0 and rate > 0 and consumption > 0:
                results["شرح مصارف"].append({
                    "شرح مصارف": "میان باری",
                    "TOU": tou,
                    "شماره کنتور قبلی": prev_meter,
                    "شماره کنتور کنونی": curr_meter,
                    "ضریب": int(coef) if coef else 1,
                    "مصرف کل": consumption,
                    "گواهی صرفه جویی": {"تولید": 0, "خرید": 0, "دوجانبه": 0, "بورس": 0},
                    "بهای انرژی پشتیبانی شده": {
                        "انرژی مشمول": consumption,
                        "نرخ": rate,
                        "مبلغ (ریال)": amount
                    }
                })
        except Exception as e:
            pass
    
    # Row 2: اوج باری
    if len(table_rows) > 2:
        row = table_rows[2]
        try:
            amount = parse_number(row[0]) if len(row) > 0 and row[0] else 0
            rate = float(parse_number(row[1])) if len(row) > 1 and row[1] else 0.0
            cell7 = str(row[7]) if len(row) > 7 and row[7] else ""
            consumption_candidates = []
            if cell7:
                for part in cell7.split():
                    try:
                        n = int(part.replace(',', ''))
                        if 1000 <= n <= 200000:
                            consumption_candidates.append(n)
                    except:
                        pass
            consumption = consumption_candidates[0] if consumption_candidates else (parse_number(row[17]) if len(row) > 17 and row[17] else 0)
            coef = 1
            meter_candidates = []
            for i, cell in enumerate(row):
                if cell:
                    val = parse_number(cell)
                    if isinstance(val, (int, float)):
                        if val in [1, 800, 1000, 2000] and coef == 1:
                            coef = int(val)
                        elif isinstance(val, float) and 100 <= val <= 100000:
                            meter_candidates.append(float(val))
            
            if len(meter_candidates) >= 2:
                meter_candidates_sorted = sorted(meter_candidates)
                prev_meter = meter_candidates_sorted[0]
                curr_meter = meter_candidates_sorted[1]
            elif len(meter_candidates) == 1:
                curr_meter = meter_candidates[0]
                prev_meter = 0.0
            else:
                curr_meter = 0.0
                prev_meter = 0.0
            tou = tou_values.get(1, 6)
            
            if amount > 0 and rate > 0 and consumption > 0:
                results["شرح مصارف"].append({
                    "شرح مصارف": "اوج باری",
                    "TOU": tou,
                    "شماره کنتور قبلی": prev_meter,
                    "شماره کنتور کنونی": curr_meter,
                    "ضریب": int(coef) if coef else 1,
                    "مصرف کل": consumption,
                    "گواهی صرفه جویی": {"تولید": 0, "خرید": 0, "دوجانبه": 0, "بورس": 0},
                    "بهای انرژی پشتیبانی شده": {
                        "انرژی مشمول": consumption,
                        "نرخ": rate,
                        "مبلغ (ریال)": amount
                    }
                })
        except Exception as e:
            pass
    
    # Row 3: کم باری
    if len(table_rows) > 3:
        row = table_rows[3]
        try:
            amount = parse_number(row[0]) if len(row) > 0 and row[0] else 0
            rate = float(parse_number(row[1])) if len(row) > 1 and row[1] else 0.0
            cell7 = str(row[7]) if len(row) > 7 and row[7] else ""
            consumption_candidates = []
            if cell7:
                for part in cell7.split():
                    try:
                        n = int(part.replace(',', ''))
                        if 1000 <= n <= 200000:
                            consumption_candidates.append(n)
                    except:
                        pass
            consumption = consumption_candidates[0] if consumption_candidates else (parse_number(row[17]) if len(row) > 17 and row[17] else 0)
            coef = 1
            meter_candidates = []
            for i, cell in enumerate(row):
                if cell:
                    val = parse_number(cell)
                    if isinstance(val, (int, float)):
                        if val in [1, 800, 1000, 2000] and coef == 1:
                            coef = int(val)
                        elif 100 <= val <= 100000 and isinstance(val, float):
                            meter_candidates.append(float(val))
            
            if len(meter_candidates) >= 2:
                meter_candidates_sorted = sorted(meter_candidates)
                prev_meter = meter_candidates_sorted[0]
                curr_meter = meter_candidates_sorted[1]
            elif len(meter_candidates) == 1:
                curr_meter = meter_candidates[0]
                prev_meter = 0.0
            else:
                curr_meter = 0.0
                prev_meter = 0.0
            tou = tou_values.get(2, 6)
            
            if amount > 0 and rate > 0 and consumption > 0:
                results["شرح مصارف"].append({
                    "شرح مصارف": "کم باری",
                    "TOU": tou,
                    "شماره کنتور قبلی": prev_meter,
                    "شماره کنتور کنونی": curr_meter,
                    "ضریب": int(coef) if coef else 1,
                    "مصرف کل": consumption,
                    "گواهی صرفه جویی": {"تولید": 0, "خرید": 0, "دوجانبه": 0, "بورس": 0},
                    "بهای انرژی پشتیبانی شده": {
                        "انرژی مشمول": consumption,
                        "نرخ": rate,
                        "مبلغ (ریال)": amount
                    }
                })
        except Exception as e:
            pass
    
    # Extract regulation differences from text
    for line in lines:
        if len(line.strip()) < 20:
            continue
        
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
        
        # Regulation differences have market rate (2945.77 typically)
        has_market_rate = any(isinstance(n, float) and 2500 <= n <= 3000 for n in nums)
        # Skip consumption rows (they have TOU < 100 and large amounts but no market rate in first 5 nums)
        is_consumption_row = len(nums) > 0 and nums[0] < 100 and any(n > 1000000 for n in nums)
        # Regulation rows have market rate but might not have TOU pattern
        early_market_rate = any(isinstance(n, float) and 2500 <= n <= 3000 for n in nums[:8])
        
        if has_market_rate and early_market_rate and not is_consumption_row:
            # Regulation pattern: energy base_rate avg_market rate_diff amount
            # Or: 0 base_rate avg_market rate_diff 0
            energy = 0
            base_rate = None
            avg_market = None
            rate_diff = 0
            amount = 0
            
            # Regulation pattern from text: "0 base_rate avg_market rate_diff 0" or "energy base_rate avg_market rate_diff amount"
            # Process in sequence
            for i, n in enumerate(nums):
                # First, find avg_market (most distinctive)
                if isinstance(n, float) and 2500 <= n <= 3000:
                    avg_market = float(n)
                # Base rate (appears before or after avg_market, 2000-12000)
                elif isinstance(n, (int, float)) and 2000 <= n <= 12000:
                    if avg_market is None or abs(n - avg_market) > 100:
                        if base_rate is None:
                            base_rate = float(n)
                        elif base_rate < 5000 and n > 5000:
                            base_rate = float(n)
                # Rate difference (typically 2000-9000)
                elif isinstance(n, (int, float)) and 1000 < n <= 9000:
                    if avg_market and abs(n - avg_market) > 100:
                        if base_rate and abs(n - base_rate) > 100:
                            rate_diff = float(n)
                # Energy (1000-200000, but can be 0)
                elif 1000 <= n <= 200000:
                    energy = int(n)
                # Amount
                elif n > 1000000:
                    amount = int(n)
            
            if base_rate and avg_market:
                if base_rate > 10000:
                    desc = "اوج باری"
                elif base_rate < 3000:
                    desc = "کم باری"
                else:
                    desc = "میان باری"
                
                existing = [r for r in results["مابه التفاوت اجرای مقررات"] if r["شرح مصارف"] == desc]
                if not existing:
                    results["مابه التفاوت اجرای مقررات"].append({
                        "شرح مصارف": desc,
                        "انرژی مشمول": energy,
                        "نرخ پایه": base_rate,
                        "متوسط نرخ بازار": avg_market,
                        "تفاوت نرخ": rate_diff,
                        "مبلغ (ریال)": amount
                    })
        
        # Total
        elif "جمع" in line:
            for n in nums:
                if 10000 <= n <= 200000:
                    results["جمع"]["مصرف کل"] = int(n)
                elif n > 10000000:
                    results["جمع"]["مبلغ (ریال)"] = int(n)
    
    # Sort
    order = {"میان باری": 0, "اوج باری": 1, "کم باری": 2, "اوج بار جمعه": 3}
    results["شرح مصارف"].sort(key=lambda x: order.get(x["شرح مصارف"], 99))
    results["مابه التفاوت اجرای مقررات"].sort(key=lambda x: order.get(x["شرح مصارف"], 99))
    
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
