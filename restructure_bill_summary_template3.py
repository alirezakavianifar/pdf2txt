"""Restructure bill summary section for Template 3."""
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
    
    # Handle trailing negative sign (e.g. "23-")
    if text.endswith('-'):
        text = '-' + text[:-1]
        
    try:
        return int(text)
    except ValueError:
        try:
            return float(text)
        except ValueError:
            return None


def extract_bill_summary_data(text):
    """Extract bill summary financial data from text.
    
    Expected fields for Template 3:
    - بهای انرژی تامین شده: 19,549,842
    - آبونمان: 129,769
    - تفاوت تعرفه انشعاب آزاد: 0
    - تجاوز از قدرت: 5,884,226,942
    - هزینه سوخت نیروگاهی: 464,987,520
    - عوارض برق: 1,743,143,496
    - مابه التفاوت ماده16 و ماده 3: 1,288,569,600
    - مبلغ دوره: 11,670,335,410
    - مالیات بر ارزش افزوده: 992,719,192
    - بدهکاری/بستانکاری: 21,759,206,375
    - کسر هزار ریال: -23
    """
    normalized_text = convert_persian_digits(text)
    
    result = {
        "بهای انرژی تامین شده": None,
        "آبونمان": None,
        "تفاوت تعرفه انشعاب آزاد": None,
        "تجاوز از قدرت": None,
        "هزینه سوخت نیروگاهی": None,
        "عوارض برق": None,
        "مابه التفاوت ماده16 و ماده 3": None,
        "مبلغ دوره": None,
        "مالیات بر ارزش افزوده": None,
        "بدهکاری/بستانکاری": None,
        "کسر هزار ریال": None
    }
    
    lines = normalized_text.split('\n')
    
    # Pattern for each field
    # Patterns for each field (supporting both "Label: Value" and "Value Label" formats)
    # Also capturing trailing minus signs
    field_patterns = {
        "بهای انرژی تامین شده": [
            r'بهای انرژی تامین شده\s*:?\s*(-?\d+(?:,\d+)*-?)',
            r'(-?\d+(?:,\d+)*-?)\s*بهای انرژی تامین شده'
        ],
        "آبونمان": [
            r'آبونمان\s*:?\s*(-?\d+(?:,\d+)*-?)',
            r'(-?\d+(?:,\d+)*-?)\s*آبونمان'
        ],
        "تفاوت تعرفه انشعاب آزاد": [
            r'تفاوت تعرفه انشعاب آزاد\s*:?\s*(-?\d+(?:,\d+)*-?)',
            r'(-?\d+(?:,\d+)*-?)\s*تفاوت تعرفه انشعاب آزاد'
        ],
        "تجاوز از قدرت": [
            r'تجاوز از قدرت\s*:?\s*(-?\d+(?:,\d+)*-?)',
            r'(-?\d+(?:,\d+)*-?)\s*تجاوز از قدرت'
        ],
        "هزینه سوخت نیروگاهی": [
            r'هزینه سوخت نیروگاهی\s*:?\s*(-?\d+(?:,\d+)*-?)',
            r'(-?\d+(?:,\d+)*-?)\s*هزینه سوخت نیروگاهی'
        ],
        "عوارض برق": [
            r'عوارض برق\s*:?\s*(-?\d+(?:,\d+)*-?)',
            r'(-?\d+(?:,\d+)*-?)\s*عوارض برق'
        ],
        "مابه التفاوت ماده16 و ماده 3": [
            r'مابه التفاوت ماده\s*16\s*و ماده\s*3\s*:?\s*(-?\d+(?:,\d+)*-?)',
            r'(-?\d+(?:,\d+)*-?)\s*مابه التفاوت ماده\s*16\s*و ماده\s*3'
        ],
        "مبلغ دوره": [
            r'مبلغ دوره\s*:?\s*(-?\d+(?:,\d+)*-?)',
            r'(-?\d+(?:,\d+)*-?)\s*مبلغ دوره'
        ],
        "مالیات بر ارزش افزوده": [
            r'مالیات بر ارزش افزوده\s*:?\s*(-?\d+(?:,\d+)*-?)',
            r'(-?\d+(?:,\d+)*-?)\s*مالیات بر ارزش افزوده'
        ],
        "بدهکاری/بستانکاری": [
            r'بدهکاری\s*/?\s*بستانکاری\s*:?\s*(-?\d+(?:,\d+)*-?)',
            r'(-?\d+(?:,\d+)*-?)\s*بدهکاری\s*/?\s*بستانکاری',
            r'بدهکاری\s*:?\s*(-?\d+(?:,\d+)*-?)',
            r'(-?\d+(?:,\d+)*-?)\s*بدهکاری'
        ],
        "کسر هزار ریال": [
            r'کسر هزار ریال\s*:?\s*(-?\d+(?:,\d+)*-?)',
            r'(-?\d+(?:,\d+)*-?)\s*کسر هزار ریال'
        ]
    }
    
    # Extract each field
    for field_name, patterns in field_patterns.items():
        for pattern in patterns:
            found = False
            for line in lines:
                match = re.search(pattern, line)
                if match:
                    result[field_name] = parse_number(match.group(1))
                    found = True
                    break
            if found:
                break
    
    return result


def restructure_bill_summary_template3_json(extracted_json_path, output_json_path):
    """Restructure extracted JSON to include bill summary data for Template 3."""
    with open(extracted_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    text = data.get('text', '')
    
    # Extract bill summary data
    summary_data = extract_bill_summary_data(text)
    
    # Build restructured data
    result = {
        "خلاصه صورتحساب": summary_data
    }
    
    # Save restructured JSON
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Restructured bill summary (Template 3) saved to: {output_json_path}")
    
    # Print extracted values
    extracted_count = sum(1 for v in summary_data.values() if v is not None)
    print(f"Extracted {extracted_count}/{len(summary_data)} bill summary fields")
    
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python restructure_bill_summary_template3.py <extracted_json_file> [output_json_file]")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file.parent / f"{input_file.stem}_restructured.json"
    
    if not input_file.exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)
    
    restructure_bill_summary_template3_json(input_file, output_file)
