"""Restructure transit section for Template 8."""
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


def parse_number(text):
    """Parse a number, removing commas and handling Persian digits."""
    if not text or text == '.' or text.strip() == '':
        return None
    
    text = convert_persian_digits(text)
    # Remove commas used as thousand separators
    text = text.replace(',', '').replace(' ', '').strip()
    
    if not text or text == '.':
        return None
    
    try:
        return int(text)
    except ValueError:
        return None


def extract_transit_data(text):
    """Extract transit section data from text."""
    normalized_text = convert_persian_digits(text)
    
    result = {
        "transit_price": None,
        "vat": None,
        "debit_credit": None,
        "thousand_rial_deduction": None,
        "amount_payable": None
    }
    
    # Patterns to match labels and values
    patterns = {
        "transit_price": [
            r'بهای ترانزیت برق\s*:\s*([\d,]+)',
            r'بهای ترانزیت برق[:\s]+([\d,]+)',
            r'بهای ترانزیت\s*:\s*([\d,]+)',
            r'بهای ترانزیت[:\s]+([\d,]+)'
        ],
        "vat": [
            r'مالیات بر ارزش افزوده\s*:\s*([\d,]+)',
            r'مالیات بر ارزش افزوده[:\s]+([\d,]+)'
        ],
        "debit_credit": [
            r'بدهکاری\s*/\s*بستانکاری\s*:\s*([\d,]+)',
            r'بدهکاری\s*/\s*بستانکاری[:\s]+([\d,]+)',
            r'بدهکاری\s*:\s*([\d,]+)',
            r'بدهکاری[:\s]+([\d,]+)'
        ],
        "thousand_rial_deduction": [
            r'کسر هزار ریال\s*:\s*([\d,]+)',
            r'کسر هزار ریال[:\s]+([\d,]+)'
        ],
        "amount_payable": [
            r'مبلغ قابل پرداخت\s*:\s*([\d,]+)',
            r'مبلغ قابل پرداخت[:\s]+([\d,]+)'
        ]
    }
    
    for key, pattern_list in patterns.items():
        for pattern in pattern_list:
            match = re.search(pattern, normalized_text)
            if match:
                value_str = match.group(1).strip()
                # Skip if it's just a dot (empty value)
                if value_str != '.' and value_str:
                    result[key] = parse_number(value_str)
                break
    
    return result


def restructure_transit_section_template8_json(extracted_json_path, output_json_path):
    """Restructure extracted JSON to include transit section data for Template 8."""
    with open(extracted_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    text = data.get('text', '')
    
    # Extract transit data
    transit_data = extract_transit_data(text)
    
    # Build restructured data
    result = {
        "transit_section": transit_data
    }
    
    # Save restructured JSON
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Restructured transit section (Template 8) saved to: {output_json_path}")
    print(f"Extracted transit data: {transit_data}")
    
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python restructure_transit_section_template8.py <extracted_json_file> [output_json_file]")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file.parent / f"{input_file.stem}_restructured.json"
    
    if not input_file.exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)
    
    restructure_transit_section_template8_json(input_file, output_file)

