"""Restructure extracted JSON data into structured format with Persian field names."""
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional


def parse_number(value: str) -> Any:
    """Parse number from string, handling commas."""
    if not value or value == '':
        return 0
    try:
        return int(value.replace(',', '').strip())
    except ValueError:
        try:
            return float(value.replace(',', '').strip())
        except ValueError:
            return value


def extract_upper_table_data(text: str) -> List[Dict[str, Any]]:
    """Extract data from the upper table (بهای انرژی پشتیبانی شده)."""
    results = []
    
    # Pattern to match: TOU prev_meter curr_meter coefficient consumption zeros... energy rate amount description
    # Example: "13 1724439 1758899 1 34460 0 0 0 0 0 34460 4063.462 140,026,901 میان باری"
    # Also handle Friday which doesn't have TOU: "88753 90562 1 1809 0 0 0 0 0 1809 4506.294 8,151,886 اوج بار جمعه"
    
    # Pattern for rows with TOU
    pattern_with_tou = r'(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d.]+)\s+([\d,]+)\s+(میان باری|اوج باری|کم باری)'
    
    # Pattern for Friday row (no TOU at start)
    pattern_friday = r'(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d.]+)\s+([\d,]+)\s+اوج بار جمعه'
    
    matches = list(re.finditer(pattern_with_tou, text)) + list(re.finditer(pattern_friday, text))
    
    for match in matches:
        groups = match.groups()
        
        # Check if it's Friday row (11 groups) or regular row (13 groups)
        if len(groups) == 11:  # Friday row
            prev_meter = int(groups[0])
            curr_meter = int(groups[1])
            coefficient = int(groups[2])
            consumption = int(groups[3])
            savings_tolid = int(groups[4])
            savings_kharid = int(groups[5])
            savings_dojanebe = int(groups[6])
            savings_bors = int(groups[7])
            energy_included = int(groups[8])
            rate = float(groups[9])
            amount = parse_number(groups[10])
            description = "اوج بار جمعه"
            tou = None  # Friday doesn't have TOU in the pattern
        else:  # Regular row with TOU
            tou = int(groups[0])
            prev_meter = int(groups[1])
            curr_meter = int(groups[2])
            coefficient = int(groups[3])
            consumption = int(groups[4])
            savings_tolid = int(groups[5])
            savings_kharid = int(groups[6])
            savings_dojanebe = int(groups[7])
            savings_bors = int(groups[8])
            energy_included = int(groups[9])
            rate = float(groups[10])
            amount = parse_number(groups[11])
            description = groups[12]
        
        result = {
            "شرح مصارف": description,
            "TOU": tou if tou is not None else 0,  # Friday row might not have TOU
            "شماره کنتور قبلی": prev_meter,
            "شماره کنتور کنونی": curr_meter,
            "ضریب": coefficient,
            "مصرف کل": consumption,
            "گواهی صرفه جویی": {
                "تولید": savings_tolid,
                "خرید": savings_kharid,
                "دوجانبه": savings_dojanebe,
                "بورس": savings_bors
            },
            "بهای انرژی پشتیبانی شده": {
                "انرژی مشمول": energy_included,
                "نرخ": rate,
                "مبلغ (ریال)": amount
            }
        }
        results.append(result)
    
    return results


def extract_lower_table_data(text: str) -> List[Dict[str, Any]]:
    """Extract data from lower table (مابه التفاوت اجرای مقررات)."""
    results = []
    
    # Pattern to match regulation difference rows
    # Example: "34460 3477 2617.65 859.35 29,613,201 میان باری"
    # Some rows might have additional data, so we need flexible patterns
    
    # Simple pattern for mid-load and Friday
    simple_pattern = r'(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d,]+)\s+(میان باری|اوج بار جمعه)'
    
    # Complex pattern for peak and off-peak (may have extra numbers)
    # Example: "9242 6954 2617.65 4336.35 40,076,547 170 0 0.00000 0 48100 0 اوج باری"
    complex_pattern = r'(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d,]+)(?:\s+[\d.]+)*\s+(اوج باری|کم باری)'
    
    matches = list(re.finditer(simple_pattern, text)) + list(re.finditer(complex_pattern, text))
    
    for match in matches:
        groups = match.groups()
        energy = int(groups[0])
        base_rate = float(groups[1])
        avg_market_rate = float(groups[2])
        rate_diff = float(groups[3])
        amount = parse_number(groups[4])
        description = groups[5]
        
        # For off-peak, rate_diff might be 0
        if description == "کم باری" and rate_diff == 0:
            # Might need to handle differently - check if amount is also 0
            continue  # Skip if both are 0, or handle separately
        
        result = {
            "شرح مصارف": description,
            "انرژی مشمول": energy,
            "نرخ پایه": base_rate,
            "متوسط نرخ بازار": avg_market_rate,
            "تفاوت نرخ": rate_diff,
            "مبلغ (ریال)": amount
        }
        results.append(result)
    
    # Also try to find off-peak row separately (it might have 0 for rate_diff)
    offpeak_pattern = r'(\d+)\s+([\d.]+)\s+([\d.]+)\s+0\s+0\s+کم باری'
    offpeak_match = re.search(offpeak_pattern, text)
    if offpeak_match:
        # Add off-peak entry with 0 values
        result = {
            "شرح مصارف": "کم باری",
            "انرژی مشمول": int(offpeak_match.group(1)),
            "نرخ پایه": float(offpeak_match.group(2)),
            "متوسط نرخ بازار": float(offpeak_match.group(3)),
            "تفاوت نرخ": 0,
            "مبلغ (ریال)": 0
        }
        # Check if this entry already exists
        if not any(r["شرح مصارف"] == "کم باری" for r in results):
            results.append(result)
    
    return results


def extract_total_data(text: str) -> Dict[str, Any]:
    """Extract total (جمع) data."""
    # Look for pattern: "24 69833 0 0 0 0 0 69833 280,255,152 جمع"
    pattern = r'(\d+)\s+(\d+)\s+(?:\d+\s+){5}(\d+)\s+([\d,]+)\s+جمع'
    match = re.search(pattern, text)
    
    if match:
        total_consumption = int(match.group(2))
        total_amount = parse_number(match.group(3))
        return {
            "مصرف کل": total_consumption,
            "مبلغ (ریال)": total_amount
        }
    
    return {}


def extract_article16_data(text: str) -> Dict[str, Any]:
    """Extract مابه التفاوت ماده 16 data."""
    # Look for "جهش تولید" section
    # The pattern might be: "0 0 39039 3477 35562 0" followed by percentage and amount
    # From the image description: "درصد مصرف: 17" and some amount
    
    # Try to find percentage consumption
    # Looking at the text: there's "170" which might be the percentage (17.0 or 170)
    # And looking for amounts related to this section
    
    # Pattern for جهش تولید: we see "39039" (renewable rate) and "35562" (rate difference)
    # Let's search for related amounts
    result = {
        "جهش تولید": {}
    }
    
    # Try to find percentage - look for pattern with "170" or similar
    percent_pattern = r'(\d+)\s+درصد مصرف|درصد مصرف[:\s]+(\d+)'
    percent_match = re.search(percent_pattern, text)
    
    # Also look for amounts in the جهش تولید section
    # From the pattern "0 0 39039 3477 35562 0" we can extract some info
    
    # For now, let's extract what we can from the complex structure
    # The exact location might need adjustment based on actual text structure
    
    return result


def restructure_json(input_path: Path, output_path: Path):
    """Restructure JSON from extraction format to desired format."""
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    text = data['text']
    
    # Extract data from different sections
    شرح_مصارف = extract_upper_table_data(text)
    مابه_التفاوت_اجرای_مقررات = extract_lower_table_data(text)
    جمع = extract_total_data(text)
    مابه_التفاوت_ماده16 = extract_article16_data(text)
    
    # Build output structure
    output = {
        "شرح مصارف": شرح_مصارف,
        "مابه التفاوت ماده 16": مابه_التفاوت_ماده16,
        "مابه التفاوت اجرای مقررات": مابه_التفاوت_اجرای_مقررات,
        "جمع": جمع
    }
    
    # Save output
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"Restructured data saved to: {output_path}")
    print(f"  - شرح مصارف: {len(شرح_مصارف)} items")
    print(f"  - مابه التفاوت اجرای مقررات: {len(مابه_التفاوت_اجرای_مقررات)} items")
    print(f"  - جمع: {len(جمع)} fields")
    print(f"  - مابه التفاوت ماده 16: {'present' if مابه_التفاوت_ماده16 else 'not found'}")
    
    return output


if __name__ == "__main__":
    input_file = Path("output/1_cropped_test.json")
    output_file = Path("output/1_cropped_restructured.json")
    
    result = restructure_json(input_file, output_file)
    
    # Print sample output
    print("\n" + "=" * 70)
    print("Sample Output:")
    print("=" * 70)
    print(json.dumps(result, ensure_ascii=False, indent=2)[:1000])
