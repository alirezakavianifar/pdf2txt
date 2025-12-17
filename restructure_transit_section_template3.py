"""Restructure transit section for Template 3."""
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
    if not text:
        return None
    
    text = convert_persian_digits(text)
    # Remove commas used as thousand separators
    text = text.replace(',', '')
    
    # Handle trailing negative sign
    if text.endswith('-'):
        text = '-' + text[:-1]
    
    try:
        return int(text)
    except ValueError:
        try:
            return float(text)
        except ValueError:
            return None


def extract_transit_data(text):
    """Extract transit section data from text.
    
    Expected fields for Template 3:
    - حق العمل: 0
    - ترانزیت: 1,557,187,200
    - اصلاح تعرفه دیرکرد
    - مالیات بر ارزش افزوده ترانزیت: 155,718,720
    - بهای برق دوره: 1,712,905,920
    - بدهکاری/بستانکاری: 1,677,471,561
    - کسر هزار ریال: 481
    """
    normalized_text = convert_persian_digits(text)
    
    result = {
        "حق العمل": None,
        "ترانزیت": None,
        "اصلاح تعرفه دیرکرد": None,
        "مالیات بر ارزش افزوده ترانزیت": None,
        "بهای برق دوره": None,
        "بدهکاری/بستانکاری": None,
        "کسر هزار ریال": None
    }
    
    lines = normalized_text.split('\n')
    
    # Common number pattern (supports negative at start or end, and commas)
    # Captures the number in group 1
    num_pat = r'((?:-?\d+(?:,\d+)*)|(?:\d+(?:,\d+)*-))'
    
    # Patterns for each field (list of regexes)
    # We support "Label: Value" and "Value Label" formats
    field_patterns = {
        "حق العمل": [
            fr'حق العمل\s*:?\s*{num_pat}',
            fr'{num_pat}\s*:?\s*حق العمل'
        ],
        "ترانزیت": [
            fr'ترانزیت\s*:?\s*{num_pat}',
            fr'{num_pat}\s*:?\s*ترانزیت'
        ],
        "اصلاح تعرفه دیرکرد": [
            fr'اصلاح تعرفه دیرکرد\s*:?\s*{num_pat}',
            fr'{num_pat}\s*:?\s*اصلاح تعرفه دیرکرد'
        ],
        "مالیات بر ارزش افزوده ترانزیت": [
            fr'مالیات بر ارزش افزوده ترانزیت\s*:?\s*{num_pat}',
            fr'{num_pat}\s*:?\s*مالیات بر ارزش افزوده ترانزیت'
        ],
        "بهای برق دوره": [
            fr'بهای برق دوره\s*:?\s*{num_pat}',
            fr'{num_pat}\s*:?\s*بهای برق دوره'
        ],
        "بدهکاری/بستانکاری": [
            fr'بدهکاری\s*/?\s*بستانکاری\s*:?\s*{num_pat}',
            fr'{num_pat}\s*:?\s*بدهکاری\s*/?\s*بستانکاری',
            fr'بدهکاری\s*:?\s*{num_pat}',
            fr'{num_pat}\s*:?\s*بدهکاری',
            fr'بستانکاری\s*:?\s*{num_pat}',
            fr'{num_pat}\s*:?\s*بستانکاری'
        ],
        "کسر هزار ریال": [
            fr'کسر هزار ریال\s*:?\s*{num_pat}',
            fr'{num_pat}\s*:?\s*کسر هزار ریال'
        ]
    }
    
    # Extract each field
    for field_name, patterns in field_patterns.items():
        for pattern in patterns:
            found = False
            for line in lines:
                match = re.search(pattern, line)
                if match:
                    # The number is in the first capturing group effectively
                    # Because num_pat has outer parens (group 1)
                    # But if we use pattern like '... {num_pat}' it works.
                    # Wait, re.search(fr'... {num_pat}') -> group 1 matches the num_pat content.
                    # Let's verify groups. 
                    # num_pat = r'((?:...)|(?:...))' -> Group 1 is the whole number.
                    # so match.group(1) should be the number string.
                    val_str = match.group(1)
                    parsed_val = parse_number(val_str)
                    if parsed_val is not None:
                        result[field_name] = parsed_val
                        found = True
                        break
            if found:
                break
                
    return result


def restructure_transit_section_template3_json(extracted_json_path, output_json_path):
    """Restructure extracted JSON to include transit section data for Template 3."""
    with open(extracted_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    text = data.get('text', '')
    
    # Extract transit data
    transit_data = extract_transit_data(text)
    
    # Build restructured data
    result = {
        "ترانزیت": transit_data
    }
    
    # Save restructured JSON
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Restructured transit section (Template 3) saved to: {output_json_path}")
    
    # Print extracted values
    extracted_count = sum(1 for v in transit_data.values() if v is not None)
    print(f"Extracted {extracted_count}/{len(transit_data)} transit fields")
    
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python restructure_transit_section_template3.py <extracted_json_file> [output_json_file]")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file.parent / f"{input_file.stem}_restructured.json"
    
    if not input_file.exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)
    
    restructure_transit_section_template3_json(input_file, output_file)
