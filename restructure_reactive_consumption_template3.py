"""Restructure reactive consumption section for Template 3."""
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
    
    try:
        return int(text)
    except ValueError:
        return None


def extract_reactive_consumption(text):
    """Extract reactive consumption value from text.
    
    Expected value for Template 3: 568000
    """
    normalized_text = convert_persian_digits(text)
    
    # Look for "مصرف راکتیو" followed by a number
    patterns = [
        r'مصرف راکتیو\s*:?\s*(\d+(?:,\d+)*)',
        r'راکتیو\s*:?\s*(\d+(?:,\d+)*)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, normalized_text)
        if match:
            return parse_number(match.group(1))
    
    # Fallback: find any large number in the text
    # Remove spaces first
    text_clean = normalized_text.replace(' ', '').replace('\n', '')
    numbers = re.findall(r'\d+(?:,\d+)*', text_clean)
    
    if numbers:
        # Parse and return the largest number (likely the consumption value)
        parsed_numbers = [parse_number(num) for num in numbers if parse_number(num)]
        if parsed_numbers:
            return max(parsed_numbers)
    
    return None


def restructure_reactive_consumption_template3_json(extracted_json_path, output_json_path):
    """Restructure extracted JSON to include reactive consumption data for Template 3."""
    with open(extracted_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    text = data.get('text', '')
    
    # Extract reactive consumption
    reactive_value = extract_reactive_consumption(text)
    
    # Build restructured data
    result = {
        "مصرف راکتیو": reactive_value
    }
    
    # Save restructured JSON
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Restructured reactive consumption (Template 3) saved to: {output_json_path}")
    if reactive_value is not None:
        print(f"Extracted reactive consumption: {reactive_value}")
    else:
        print("WARNING: Could not extract reactive consumption value")
    
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python restructure_reactive_consumption_template3.py <extracted_json_file> [output_json_file]")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file.parent / f"{input_file.stem}_restructured.json"
    
    if not input_file.exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)
    
    restructure_reactive_consumption_template3_json(input_file, output_file)
