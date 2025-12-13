"""Complete universal restructure script for different PDF formats."""
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
    """Restructure JSON using table-based extraction with text fallback."""
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
    
    # Extract TOU values from text
    tou_map = {}
    consumption_idx = 0
    for line in lines:
        parts = line.split()
        if len(parts) > 12:
            try:
                tou = int(parts[0].replace(',', ''))
                if tou < 100:
                    # Check if line has large amount (consumption row)
                    for p in parts:
                        try:
                            amt = int(p.replace(',', ''))
                            if amt > 1000000:
                                tou_map[consumption_idx] = tou
                                consumption_idx += 1
                                break
                        except:
                            pass
            except:
                pass
    
    # Extract consumption from table rows (rows 1-3 typically)
    for row_idx in range(1, min(4, len(table_rows))):
        row = table_rows[row_idx]
        try:
            amount = parse_number(row[0]) if len(row) > 0 and row[0] else 0
            if amount == 0:
                continue
            
            rate = float(parse_number(row[1])) if len(row) > 1 and row[1] else 0.0
            
            # Extract consumption from cell 7 (may contain "17456 0 0")
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
            
            # Find coefficient and meters (exclude the already-extracted rate)
            coef = 1
            meter_candidates = []
            for cell in row:
                if cell:
                    val = parse_number(cell)
                    if isinstance(val, (int, float)):
                        # Check for coefficient - common values: 1, 800, 1000, 1200, 2000
                        # Prefer larger coefficient values (1200 over 1) when both exist
                        if val in [1, 800, 1000, 1200, 2000]:
                            # Only update if we haven't found a better coefficient yet
                            # Prefer larger values (1200 > 1000 > 800 > 1)
                            if coef == 1 or (val > coef and val <= 2000):
                                coef = int(val)
                        # Then check for meters (exclude rate and coefficients)
                        elif 100 <= val <= 50000:
                            # Exclude coefficient values
                            if val not in [1, 800, 1000, 1200, 2000]:
                                # Exclude the rate we already extracted (with small tolerance for floating point)
                                if rate == 0 or abs(val - rate) > 10:
                                    meter_candidates.append(float(val))
            
            # Remove duplicates while preserving order
            seen = set()
            unique_meter_candidates = []
            for m in meter_candidates:
                if m not in seen:
                    seen.add(m)
                    unique_meter_candidates.append(m)
            meter_candidates = unique_meter_candidates
            
            # Assign meters (prev is smaller, curr is larger)
            if len(meter_candidates) >= 2:
                sorted_meters = sorted(meter_candidates)
                prev_meter = sorted_meters[0]
                curr_meter = sorted_meters[1]
            elif len(meter_candidates) == 1:
                curr_meter = meter_candidates[0]
                prev_meter = 0.0
            else:
                curr_meter = 0.0
                prev_meter = 0.0
            
            tou = tou_map.get(row_idx - 1, 12 if row_idx == 1 else 6)
            
            # Determine description
            if row_idx == 1:
                desc = "میان باری"
            elif row_idx == 2:
                desc = "اوج باری"
            elif row_idx == 3:
                desc = "کم باری"
            else:
                desc = "میان باری"
            
            if amount > 0 and rate > 0 and consumption > 0:
                results["شرح مصارف"].append({
                    "شرح مصارف": desc,
                    "TOU": tou,
                    "شماره کنتور قبلی": prev_meter,
                    "شماره کنتور کنونی": curr_meter,
                    "ضریب": coef,
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
    regulation_found = set()
    for line in lines:
        line_stripped = line.strip()
        if len(line_stripped) < 15:  # Reduced threshold to catch total line
            continue
        
        # Extract total FIRST (before processing regulation differences)
        # Pattern: contains "جمع" or matches pattern: TOU-like number, consumption (1000-200000), amount (>1M)
        line_parts = line_stripped.split()
        total_candidates = []
        for part in line_parts:
            clean_part = part.replace(',', '').replace('،', '').strip()
            try:
                n = int(clean_part)
                total_candidates.append(n)
            except ValueError:
                pass
        
        # Check for total line pattern
        # Total line pattern: starts with TOU sum (10-30), has consumption value, many zeros, large amount
        # Key: has many zeros (at least 4) which consumption rows don't have
        # Also check if line contains "جمع" explicitly (try both Persian and potential encoding variations)
        is_total_line = False
        
        # Check explicitly for "جمع" in line (most reliable indicator)
        # The character might be in the line even if direct string check fails
        has_collect_char = "جمع" in line_stripped
        
        if has_collect_char and len(total_candidates) >= 3:
            is_total_line = True
        elif len(total_candidates) >= 6:  # Total line has many numbers including zeros
            first = total_candidates[0]
            zero_count = sum(1 for n in total_candidates if n == 0)
            has_consumption = any(1000 <= n <= 500000 for n in total_candidates)
            has_amount = any(n > 100000000 for n in total_candidates)  # Very large amounts for totals
            
            # Total line: starts with TOU sum (10-30), has 4+ zeros, has consumption and very large amount
            if 10 <= first <= 30 and zero_count >= 4 and has_consumption and has_amount:
                is_total_line = True
        
        if is_total_line:
            # Parse line parts directly - total line pattern: "24 224136 ... 224136 515139744 جمع"
            # Extract the largest numbers: consumption (1000-500000) and amount (>1M)
            consumption_total = None
            amount_total = None
            
            for part in line_parts:
                # Remove commas and try to parse
                clean_part = part.replace(',', '').replace('،', '').strip()
                try:
                    n = int(clean_part)
                    # Consumption total - can be large (up to 500000 for total), but not too large
                    if 1000 <= n <= 500000:
                        # Take the largest valid consumption value (appears twice in pattern)
                        if consumption_total is None or n > consumption_total:
                            consumption_total = n
                    # Amount total - the very large number
                    elif n > 100000000:  # Very large (hundreds of millions)
                        if amount_total is None or n > amount_total:
                            amount_total = n
                except ValueError:
                    pass
            
            # Only update if we found valid values (don't overwrite with consumption row values)
            if consumption_total and consumption_total > 10000:  # Total consumption is large
                results["جمع"]["مصرف کل"] = consumption_total
            if amount_total and amount_total > 100000000:  # Total amount is very large
                results["جمع"]["مبلغ (ریال)"] = amount_total
            
            # Skip further processing for total line
            continue
        
        parts = line.split()
        nums = []
        for p in parts:
            try:
                n = int(p.replace(',', ''))
                nums.append(n)  # Include 0s for regulation rows
            except:
                try:
                    n = float(p.replace(',', ''))
                    nums.append(n)  # Include 0.0s
                except:
                    pass
        
        if len(nums) < 3:
            continue
        
        # Check for market rate (2945.77) - regulation rows have this
        has_market_rate = any(isinstance(n, float) and 2500 <= n <= 3000 for n in nums)
        # Skip consumption rows - they have TOU < 100 and large amounts, but NO market rate
        is_consumption = len(nums) > 0 and nums[0] < 100 and any(n > 1000000 for n in nums) and not has_market_rate
        # Skip if first number is large (likely consumption row)
        is_likely_consumption = len(nums) > 0 and nums[0] > 1000000
        
        if has_market_rate and not is_consumption and not is_likely_consumption:
            # Regulation pattern: "0 base_rate avg_market rate_diff 0" or similar
            energy = 0
            base_rate = None
            avg_market = None
            rate_diff = 0
            amount = 0
            
            # Find avg_market first (most distinctive)
            for n in nums:
                if isinstance(n, float) and 2500 <= n <= 3000:
                    avg_market = float(n)
                    break
            
            if avg_market:
                # Pattern: numbers... base_rate avg_market rate_diff ... (or 0 base_rate avg_market rate_diff 0)
                # Find position of avg_market
                avg_market_idx = -1
                for i, n in enumerate(nums):
                    if isinstance(n, float) and abs(n - avg_market) < 0.1:
                        avg_market_idx = i
                        break
                
                # Base rate is usually 1 position before avg_market
                # Pattern: "0 base_rate avg_market rate_diff 0" or "0 base_rate avg_market 0 0"
                if avg_market_idx > 0:
                    prev_n = nums[avg_market_idx - 1]
                    if isinstance(prev_n, (int, float)):
                        # Base rate can be 1000-12000, but not the same as avg_market
                        if 1000 <= prev_n <= 12000 and abs(prev_n - avg_market) > 100:
                            base_rate = float(prev_n)
                        # Also check if prev_n is exactly 0 (which would mean base_rate is further back)
                        elif (prev_n == 0 or prev_n == 0.0) and avg_market_idx > 1:
                            # Look one more position back
                            prev_prev_n = nums[avg_market_idx - 2]
                            if isinstance(prev_prev_n, (int, float)) and 1000 <= prev_prev_n <= 12000:
                                if abs(prev_prev_n - avg_market) > 100:
                                    base_rate = float(prev_prev_n)
                
                # Also try to find base_rate by searching backwards from avg_market
                # Pattern can be "0 base_rate avg_market 0 0" where base_rate is 1-2 positions before avg_market
                if not base_rate and avg_market_idx > 0:
                    # Check up to 3 positions back
                    for i in range(avg_market_idx - 1, max(-1, avg_market_idx - 4), -1):
                        if i >= 0 and i < len(nums):
                            candidate = nums[i]
                            if isinstance(candidate, (int, float)) and 1000 <= candidate <= 12000:
                                if abs(candidate - avg_market) > 100:
                                    base_rate = float(candidate)
                                    break
                
                # Rate diff is usually 1 position after avg_market
                if avg_market_idx >= 0 and avg_market_idx < len(nums) - 1:
                    next_n = nums[avg_market_idx + 1]
                    if isinstance(next_n, (int, float)) and 0 <= next_n <= 9000:
                        if next_n == 0:
                            rate_diff = 0
                        elif base_rate and abs(next_n - base_rate) > 100:
                            if abs(next_n - avg_market) > 100:
                                rate_diff = float(next_n)
                
                # Energy is usually first number (0 or value)
                # But we need to be careful - first might be 0, which we've included in nums now
                if len(nums) > 0:
                    first = nums[0]
                    if first == 0 or first == 0.0:
                        energy = 0
                    elif isinstance(first, (int, float)) and 1000 <= first <= 200000:
                        # But don't use it if it's actually a rate (base_rate or avg_market)
                        if first != base_rate and first != avg_market:
                            energy = int(first) if isinstance(first, float) else first
                
                if base_rate and avg_market:
                    # Determine description based on base_rate value
                    # Pattern from text (more precise):
                    # میان باری: base_rate around 2296 (2000-3000)
                    # اوج باری: base_rate around 4592 or 5510 (4500-6000)  
                    # کم باری: base_rate around 1148 or 1377 (1000-2000)
                    if base_rate >= 4500:
                        desc = "اوج باری"
                    elif base_rate >= 2000 and base_rate < 4500:
                        desc = "میان باری"
                    elif base_rate < 2000:
                        desc = "کم باری"
                    else:
                        desc = "میان باری"
                    
                    # Check if we already have this description with same base_rate
                    existing_idx = None
                    for idx, item in enumerate(results["مابه التفاوت اجرای مقررات"]):
                        if item["شرح مصارف"] == desc:
                            existing_idx = idx
                            break
                    
                    # Only add if we haven't found this description yet
                    if existing_idx is None:
                        results["مابه التفاوت اجرای مقررات"].append({
                            "شرح مصارف": desc,
                            "انرژی مشمول": energy,
                            "نرخ پایه": base_rate,
                            "متوسط نرخ بازار": avg_market,
                            "تفاوت نرخ": rate_diff,
                            "مبلغ (ریال)": amount
                        })
                        regulation_found.add(desc)
                    # If already found with same description, check if this is a better match
                    else:
                        existing = results["مابه التفاوت اجرای مقررات"][existing_idx]
                        # Update if base_rates match (same row) or if this has more complete data
                        if abs(existing["نرخ پایه"] - base_rate) < 0.1:
                            # Same base_rate, update with any new data
                            results["مابه التفاوت اجرای مقررات"][existing_idx] = {
                                "شرح مصارف": desc,
                                "انرژی مشمول": energy,
                                "نرخ پایه": base_rate,
                                "متوسط نرخ بازار": avg_market,
                                "تفاوت نرخ": rate_diff,
                                "مبلغ (ریال)": amount
                            }
                        # If different base_rate but same description, this shouldn't happen
                        # but if it does, keep the first one
    
    # Sort results
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
