"""Restructure power section for Template 7."""
import json
import re
from pathlib import Path


def convert_persian_digits(text):
    """Convert Persian/Arabic-Indic digits to regular digits."""
    persian_digits = '۰۱۲۳۴۵۶۷۸۹'
    arabic_indic_digits = '٠١٢٣٤٥٦٧٨٩'
    regular_digits = '0123456789'
    
    result = text
    for i, persian in enumerate(persian_digits):
        result = result.replace(persian, regular_digits[i])
    for i, arabic in enumerate(arabic_indic_digits):
        result = result.replace(arabic, regular_digits[i])
    
    return result


def parse_decimal_number(text):
    """Parse a number string, removing commas and handling Persian format."""
    if not text:
        return None
    # Remove commas and spaces
    clean = convert_persian_digits(text)
    clean = clean.replace(',', '').replace(' ', '').strip()
    try:
        return float(clean)
    except ValueError:
        return None


def extract_power_data(text):
    """Extract power values and meter specifications from text.
    
    Expected fields:
    - قراردادی (Contractual): 1200
    - مجاز (Permitted): 1200
    - مصرفی (Consumed): 659.68
    - ماکسیمتر (Maximator): 0.412
    - محاسبه شده (Calculated): (empty or 0)
    - کاهش یافته (Reduced): (empty or 0)
    - میزان تجاوز از قدرت (Amount of power exceeding): 0
    - تاریخ اتمام کاهش موقت (Temporary Reduction End Date): 1500/01/01
    
    Meter Specifications:
    - شماره بدنه کنتور اکتیو (Active Meter Body Number): 18059877002170
    - شماره بدنه کنتور راکتیو (Reactive Meter Body Number): 18059877002170
    - ضریب کنتور (Meter Coefficient): 1600
    - ضریب قدرت (Power Coefficient): 0.99
    - میزان تجاوز از قدرت (Power Exceeded Amount): 0
    """
    normalized_text = convert_persian_digits(text)
    
    result = {
        "قراردادی": None,
        "مجاز": None,
        "مصرفی": None,
        "ماکسیمتر": None,
        "محاسبه شده": None,
        "کاهش یافته": None,
        "میزان تجاوز از قدرت": None,
        "تاریخ اتمام کاهش موقت": None,
        "شماره بدنه کنتور اکتیو": None,
        "شماره بدنه کنتور راکتیو": None,
        "ضریب کنتور": None,
        "ضریب قدرت": None,
        "میزان تجاوز از قدرت (کنتور)": None
    }
    
    lines = normalized_text.split('\n')
    full_text = ' '.join(lines)
    
    # Extract قراردادی
    match = re.search(r'قراردادی\s*:?\s*(\d+(?:,\d+)?(?:\.\d+)?)', full_text)
    if match:
        result["قراردادی"] = parse_decimal_number(match.group(1))
    
    # Extract مجاز
    match = re.search(r'مجاز\s*:?\s*(\d+(?:,\d+)?(?:\.\d+)?)', full_text)
    if match:
        result["مجاز"] = parse_decimal_number(match.group(1))
    
    # Extract مصرفی
    match = re.search(r'مصرفی\s*:?\s*(\d+(?:,\d+)?(?:\.\d+)?)', full_text)
    if match:
        result["مصرفی"] = parse_decimal_number(match.group(1))
    
    # Extract ماکسیمتر
    match = re.search(r'ماکسیمتر\s*:?\s*(\d+(?:,\d+)?(?:\.\d+)?)', full_text)
    if match:
        result["ماکسیمتر"] = parse_decimal_number(match.group(1))
    
    # Extract محاسبه شده
    match = re.search(r'محاسبه شده\s*:?\s*(\d+(?:,\d+)?(?:\.\d+)?)', full_text)
    if match:
        result["محاسبه شده"] = parse_decimal_number(match.group(1))
    else:
        result["محاسبه شده"] = 0
    
    # Extract کاهش یافته
    match = re.search(r'کاهش یافته\s*:?\s*(\d+(?:,\d+)?(?:\.\d+)?)', full_text)
    if match:
        result["کاهش یافته"] = parse_decimal_number(match.group(1))
    else:
        result["کاهش یافته"] = 0
    
    # Extract میزان تجاوز از قدرت (power section)
    match = re.search(r'میزان تجاوز از قدرت\s*:?\s*(\d+(?:,\d+)?(?:\.\d+)?)', full_text)
    if match:
        result["میزان تجاوز از قدرت"] = parse_decimal_number(match.group(1))
    else:
        result["میزان تجاوز از قدرت"] = 0
    
    # Extract تاریخ اتمام کاهش موقت
    match = re.search(r'تاریخ اتمام کاهش موقت\s*:?\s*(\d{4}/\d{2}/\d{2})', full_text)
    if match:
        result["تاریخ اتمام کاهش موقت"] = match.group(1)
    
    # Extract شماره بدنه کنتور اکتیو
    match = re.search(r'شماره بدنه کنتور اکتیو\s*:?\s*(\d+)', full_text)
    if match:
        result["شماره بدنه کنتور اکتیو"] = match.group(1)
    
    # Extract شماره بدنه کنتور راکتیو
    match = re.search(r'شماره بدنه کنتور راکتیو\s*:?\s*(\d+)', full_text)
    if match:
        result["شماره بدنه کنتور راکتیو"] = match.group(1)
    
    # Extract ضریب کنتور
    match = re.search(r'ضریب کنتور\s*:?\s*(\d+(?:,\d+)?)', full_text)
    if match:
        result["ضریب کنتور"] = parse_decimal_number(match.group(1))
    
    # Extract ضریب قدرت
    match = re.search(r'ضریب قدرت\s*:?\s*(\d+(?:,\d+)?(?:\.\d+)?)', full_text)
    if match:
        result["ضریب قدرت"] = parse_decimal_number(match.group(1))
    
    # Extract میزان تجاوز از قدرت (meter section)
    match = re.search(r'میزان تجاوز از قدرت\s*:?\s*(\d+(?:,\d+)?(?:\.\d+)?)', full_text)
    if match:
        result["میزان تجاوز از قدرت (کنتور)"] = parse_decimal_number(match.group(1))
    else:
        result["میزان تجاوز از قدرت (کنتور)"] = 0
    
    return result


def restructure_power_section_template7_json(json_path: Path, output_path: Path):
    """Restructure extracted JSON to include power section data for Template 7."""
    print(f"Restructuring Power Section (Template 7) from {json_path}...")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        text = data.get('text', '')
        table_data = data.get('table', {})
        
        # Also check table rows for power section data
        if table_data and 'rows' in table_data:
            for row in table_data['rows']:
                for cell in row:
                    if cell and isinstance(cell, str):
                        text += '\n' + cell
        
        # Extract power data
        power_data = extract_power_data(text)
        
        # Build restructured data
        result = {
            "جزئیات قدرت": power_data
        }
        
        # Save restructured JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"  - Saved to {output_path}")
        extracted_count = sum(1 for v in power_data.values() if v is not None)
        print(f"  - Extracted {extracted_count}/{len(power_data)} power values")
        
        return result
        
    except Exception as e:
        print(f"Error restructuring Power Section T7: {e}")
        import traceback
        traceback.print_exc()
        return None

