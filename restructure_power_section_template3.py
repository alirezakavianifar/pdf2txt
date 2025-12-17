"""Restructure power section for Template 3."""
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
    """Parse decimal number, handling slash as decimal separator."""
    if not text:
        return None
    
    # Replace slash with dot for decimal parsing
    text = text.replace('/', '.')
    text = convert_persian_digits(text)
    # Remove commas
    text = text.replace(',', '')
    
    try:
        return float(text)
    except ValueError:
        return None


def extract_power_section_data(text):
    """Extract power section data from text.
    
    Expected fields for Template 3:
    - قراردادی (Contractual): 3000
    - ماکسیمتر (Maximator): 804
    - مجاز (Permitted): 3000
    - محاسبه شده (Calculated): 3216
    - مصرفی (Consumed): 3216
    - کاهش یافته (Reduced)
    """
    # Initialize result structure
    result = {
        "قراردادی": None,
        "ماکسیمتر": None,
        "مجاز": None,
        "محاسبه شده": None,
        "مصرفی": None,
        "کاهش یافته": None
    }
    
    # Normalize text
    normalized_text = convert_persian_digits(text)
    lines = normalized_text.split('\n')
    
    # Extract each field
    for line in lines:
        # قراردادی
        match = re.search(r'قراردادی\s*:?\s*(\d+(?:[/\.,]\d+)?)', line)
        if match and result["قراردادی"] is None:
            result["قراردادی"] = parse_decimal_number(match.group(1))
        
        # ماکسیمتر
        match = re.search(r'ماکسیمتر\s*:?\s*(\d+(?:[/\.,]\d+)?)', line)
        if match and result["ماکسیمتر"] is None:
            result["ماکسیمتر"] = parse_decimal_number(match.group(1))
        
        # مجاز
        match = re.search(r'مجاز\s*:?\s*(\d+(?:[/\.,]\d+)?)', line)
        if match and result["مجاز"] is None:
            result["مجاز"] = parse_decimal_number(match.group(1))
        
        # محاسبه شده
        match = re.search(r'محاسبه شده\s*:?\s*(\d+(?:[/\.,]\d+)?)', line)
        if match and result["محاسبه شده"] is None:
            result["محاسبه شده"] = parse_decimal_number(match.group(1))
        
        # مصرفی
        match = re.search(r'مصرفی\s*:?\s*(\d+(?:[/\.,]\d+)?)', line)
        if match and result["مصرفی"] is None:
            result["مصرفی"] = parse_decimal_number(match.group(1))
        
        # کاهش یافته
        match = re.search(r'کاهش یافته\s*:?\s*(\d+(?:[/\.,]\d+)?)', line)
        if match and result["کاهش یافته"] is None:
            result["کاهش یافته"] = parse_decimal_number(match.group(1))
    
    return result


def restructure_power_section_template3_json(extracted_json_path, output_json_path):
    """Restructure extracted JSON to include power section data for Template 3."""
    with open(extracted_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    text = data.get('text', '')
    
    # Extract power data
    power_data = extract_power_section_data(text)
    
    # Build restructured data
    result = {
        "قدرت (کیلووات)": power_data
    }
    
    # Save restructured JSON
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Restructured power section (Template 3) saved to: {output_json_path}")
    
    # Print extracted values
    extracted_count = sum(1 for v in power_data.values() if v is not None)
    print(f"Extracted {extracted_count}/{len(power_data)} power fields")
    
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python restructure_power_section_template3.py <extracted_json_file> [output_json_file]")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file.parent / f"{input_file.stem}_restructured.json"
    
    if not input_file.exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)
    
    restructure_power_section_template3_json(input_file, output_file)
