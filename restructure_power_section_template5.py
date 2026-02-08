"""Restructure power section for Template 5."""
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
    """Extract power values from text.
    
    Expected fields:
    - قراردادی (Contractual): ۲۰۰۰
    - محاسبه شده (Calculated): ۰
    - پروانه مجاز (Authorized License): ۰
    - کاهش یافته (Reduced): ۰
    - میزان تجاوز از قدرت (Amount of power exceeding limit): ۰
    - مصرفی (Consumed): ۵۱۳.۳۰۰۰
    - عدد ماکسیمتر (Maximeter Number): ۳.۰۰۰۰
    - تاریخ اتمام کاهش موقت (Temporary Reduction End Date): optional date string
    """
    normalized_text = convert_persian_digits(text)
    
    result = {
        "قراردادی": None,
        "محاسبه شده": None,
        "پروانه مجاز": None,
        "کاهش یافته": None,
        "میزان تجاوز از قدرت": None,
        "مصرفی": None,
        "عدد ماکسیمتر": None,
        "تاریخ اتمام کاهش موقت": None
    }
    
    lines = normalized_text.split('\n')
    full_text = ' '.join(lines)
    
    # Extract قراردادی
    match = re.search(r'قراردادی[^\d]*(\d+(?:\.\d+)?)', full_text)
    if match:
        result["قراردادی"] = parse_decimal_number(match.group(1))
    
    # Extract محاسبه شده
    match = re.search(r'محاسبه شده[^\d]*(\d+(?:\.\d+)?)', full_text)
    if match:
        result["محاسبه شده"] = parse_decimal_number(match.group(1))
    
    # Extract پروانه مجاز
    match = re.search(r'پروانه مجاز[^\d]*(\d+(?:\.\d+)?)', full_text)
    if match:
        result["پروانه مجاز"] = parse_decimal_number(match.group(1))
    
    # Extract کاهش یافته
    match = re.search(r'کاهش یافته[^\d]*(\d+(?:\.\d+)?)', full_text)
    if match:
        result["کاهش یافته"] = parse_decimal_number(match.group(1))
    
    # Extract میزان تجاوز از قدرت
    match = re.search(r'میزان تجاوز از قدرت[^\d]*(\d+(?:\.\d+)?)', full_text)
    if match:
        result["میزان تجاوز از قدرت"] = parse_decimal_number(match.group(1))
    
    # Extract مصرفی (may have decimal format like 513.3000)
    match = re.search(r'مصرفی[^\d]*(\d+(?:\.\d+)?)', full_text)
    if match:
        result["مصرفی"] = parse_decimal_number(match.group(1))
    
    # Extract عدد ماکسیمتر (Maximeter Number) - can appear as "عدد ماکسیمتر 3.0000"
    match = re.search(r'عدد\s*ماکسیمتر[^\d]*(\d+(?:\.\d+)?)', full_text)
    if match:
        result["عدد ماکسیمتر"] = parse_decimal_number(match.group(1))
    else:
        # Also try without "عدد" prefix
        match = re.search(r'ماکسیمتر[^\d]*(\d+(?:\.\d+)?)', full_text)
        if match:
            result["عدد ماکسیمتر"] = parse_decimal_number(match.group(1))
    
    # Extract تاریخ اتمام کاهش موقت (Temporary Reduction End Date)
    # Check if the label exists, and if there's a date value after it
    # Look for date patterns like YYYY/MM/DD or YYYYMMDD
    date_match = re.search(r'تاریخ اتمام کاهش موقت\s*:?\s*(\d{4}[/\-]\d{2}[/\-]\d{2}|\d{8})', full_text)
    if date_match:
        result["تاریخ اتمام کاهش موقت"] = date_match.group(1).strip()
    elif 'تاریخ اتمام کاهش موقت' in full_text:
        # Label exists but no date value found, set to empty string to indicate presence
        result["تاریخ اتمام کاهش موقت"] = ""
    
    return result


def restructure_power_section_template5_json(json_path: Path, output_path: Path):
    """Restructure extracted JSON to include power section data for Template 5."""
    print(f"Restructuring Power Section (Template 5) from {json_path}...")
    
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
        
        # Convert None values to 0.0 for numeric fields (but keep None/empty for date field)
        numeric_fields = ["قراردادی", "محاسبه شده", "پروانه مجاز", "کاهش یافته", 
                         "میزان تجاوز از قدرت", "مصرفی", "عدد ماکسیمتر"]
        for field in numeric_fields:
            if power_data.get(field) is None:
                power_data[field] = 0.0
        
        # Build restructured data
        result = {
            "جزئیات قدرت": power_data
        }
        
        # Save restructured JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"  - Saved to {output_path}")
        extracted_count = sum(1 for k, v in power_data.items() 
                            if k in numeric_fields and v is not None and v != 0.0)
        print(f"  - Extracted {extracted_count} non-zero power values")
        
        return result
        
    except Exception as e:
        print(f"Error restructuring Power Section T5: {e}")
        import traceback
        traceback.print_exc()
        return None

