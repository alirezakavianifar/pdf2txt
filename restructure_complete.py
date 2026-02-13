"""Complete universal restructure script for different PDF formats."""
import json
from pathlib import Path
from typing import List, Optional


def parse_number(value):
    """Parse number from string, handling commas and space-separated noise."""
    if not value or value == '':
        return 0
    
    value_str = str(value).strip()
    clean_str = value_str.replace(',', '')
    
    try:
        return int(clean_str)
    except ValueError:
        try:
            return float(clean_str)
        except ValueError:
            # Try splitting by space (e.g. "292363 7" -> 292363)
            parts = value_str.split()
            if len(parts) > 1:
                try:
                    p0 = parts[0].replace(',', '')
                    return int(p0)
                except ValueError:
                    try:
                        return float(p0)
                    except ValueError:
                        pass
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
        "مابه التفاوت ماده 16_درصد مصرف": 17,
        "مابه التفاوت ماده 16_مصرف مشمول": 0,
        "مابه التفاوت ماده 16_نرخ تجدید پذیر": 0,
        "مابه التفاوت ماده 16_نرخ میان باری": 0,
        "مابه التفاوت ماده 16_تفاوت نرخ": 0,
        "مابه التفاوت ماده 16_مبلغ": 0,
        "تجاوزازقدرت_دیماند مصرفی": 0,
        "تجاوزازقدرت_میزان تجاوز": 0,
        "تجاوزازقدرت_ضریب محاسبه": 0,
        "تجاوزازقدرت_انرژی مشمول": 0,
        "تجاوزازقدرت_نرخ": 0,
        "تجاوزازقدرت_مبلغ": 0,
        "راکتیو_شمارنده قبلی": 0,
        "راکتیو_شمارنده کنونی": 0,
        "راکتیو_مصرف": 0,
        "راکتیو_ضریب قدرت": 0,
        "راکتیو_ضریب زیان": 0,
        "راکتیو_مبلغ": 0,
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
    
    # Extract consumption from table rows
    # Data rows typically start at index 3 (after header rows)
    # Row structure: [amount, rate, ..., consumption, ..., coefficient, current_meter, ..., previous_meter, ..., TOU, description]
    # Based on actual data: row[0]=amount, row[1]=rate, row[4] or row[15]=consumption, row[17]=coef, row[18]=current, row[20]=previous, row[22]=TOU
    
    for row_idx in range(3, min(7, len(table_rows))):  # Process rows 3-6 (0-indexed)
        row = table_rows[row_idx]
        try:
            if not row or len(row) < 3:
                continue
            
            # Extract amount (cell 0)
            amount = parse_number(row[0]) if len(row) > 0 and row[0] else 0
            
            # Extract rate (cell 1)
            rate = float(parse_number(row[1])) if len(row) > 1 and row[1] else 0.0
            
            # Extract consumption - check indices 4, 15, and 16
            consumption = 0
            if len(row) > 4 and row[4]:
                consumption = parse_number(row[4])
            if consumption == 0 and len(row) > 15 and row[15]:
                consumption = parse_number(row[15])
            if consumption == 0 and len(row) > 16 and row[16]:
                consumption = parse_number(row[16])
            
            # Extract coefficient
            # In some templates, coef is at 17, in others at 18
            coef = 1
            if len(row) > 18 and row[18]:
                coef = parse_number(row[18])
            elif len(row) > 17 and row[17]:
                coef = parse_number(row[17])
            
            if coef == 0:
                coef = 1
            
            # Extract current meter
            # Can be at 18 or 20
            curr_meter = 0.0
            if len(row) > 20 and row[20]:
                curr_meter = float(parse_number(row[20]))
            elif len(row) > 18 and row[18]:
                curr_meter = float(parse_number(row[18]))
            
            # Extract previous meter
            # Can be at 20 or 22
            prev_meter = 0.0
            if len(row) > 22 and row[22]:
                prev_meter = float(parse_number(row[22]))
            elif len(row) > 20 and row[20]:
                prev_meter = float(parse_number(row[20]))
            
            # Extract TOU
            # Can be at 22 or 24
            tou = 0
            if len(row) > 24 and row[24]:
                tou = parse_number(row[24])
            elif len(row) > 22 and row[22]:
                tou = parse_number(row[22])
            
            # Determine description from row text or position
            # Check last cell for description text
            desc = None
            if len(row) > 23:
                last_cell = str(row[23]).strip()
                if "میان باری" in last_cell or "نایم" in last_cell:
                    desc = "میان باری"
                elif "اوج باری" in last_cell or "جوا" in last_cell:
                    desc = "اوج باری"
                elif "کم باری" in last_cell or "مک" in last_cell:
                    desc = "کم باری"
                elif "جمعه" in last_cell:
                    desc = "اوج بار جمعه"
            
            # Fallback to position-based description
            if not desc:
                if row_idx == 3:
                    desc = "میان باری"
                elif row_idx == 4:
                    desc = "اوج باری"
                elif row_idx == 5:
                    desc = "کم باری"
                elif row_idx == 6:
                    desc = "اوج بار جمعه"
                else:
                    desc = "میان باری"
            
            # Add row if it has valid data (allow zero consumption for Friday Peak)
            if rate > 0 and (consumption > 0 or desc == "اوج بار جمعه"):
                results["شرح مصارف"].append({
                    "شرح مصارف": desc,
                    "TOU": int(tou) if tou else 0,
                    "شماره کنتور قبلی": prev_meter,
                    "شماره کنتور کنونی": curr_meter,
                    "ضریب": int(coef) if coef else 1,
                    "مصرف کل": int(consumption) if consumption else 0,
                    "شرح مصارف_گواهی صرفه جویی": 0,
                    "شرح مصارف_تجدید_تولید": 0,
                    "شرح مصارف_تجدید_خرید": 0,
                    "شرح مصارف_غیر تجدید_دوجانبه": 0,
                    "شرح مصارف_غیر تجدید_بورس": 0,
                    "بهای انرژی پشتیبانی شده": {
                        "انرژی مشمول": int(consumption) if consumption else 0,
                        "نرخ": rate,
                        "مبلغ (ریال)": int(amount) if amount else 0
                    }
                })
        except Exception as e:
            import traceback
            traceback.print_exc()
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
