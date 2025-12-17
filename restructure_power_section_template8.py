"""Restructure power section for Template 8."""
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
        # Handle decimal numbers (may use slash or dot)
        if '/' in text:
            text = text.replace('/', '.')
        if '.' in text:
            return float(text)
        else:
            return int(text)
    except ValueError:
        return None


def extract_power_values(text):
    """Extract power values from text."""
    normalized_text = convert_persian_digits(text)
    
    result = {
        "contractual_power": None,
        "calculated_power": None,
        "permitted_power": None,
        "reduced_power": None,
        "consumed_power": None,
        "power_overage": None
    }
    
    # Patterns to match labels and values
    patterns = {
        "contractual_power": [
            r'قراردادی\s*:\s*([\d,./]+)',
            r'قراردادی[:\s]+([\d,./]+)'
        ],
        "calculated_power": [
            r'محاسبه شده\s*:\s*([\d,./]+)',
            r'محاسبه شده[:\s]+([\d,./]+)'
        ],
        "permitted_power": [
            r'مجاز\s*:\s*([\d,./]+)',
            r'مجاز[:\s]+([\d,./]+)'
        ],
        "reduced_power": [
            r'کاهش یافته\s*:\s*([\d,./]+)',
            r'کاهش یافته[:\s]+([\d,./]+)'
        ],
        "consumed_power": [
            r'مصرفی\s*:\s*([\d,./]+)',
            r'مصرفی[:\s]+([\d,./]+)'
        ],
        "power_overage": [
            r'میزان تجاوز از قدرت\s*:\s*([\d,./]+)',
            r'تجاوز از قدرت\s*:\s*([\d,./]+)',
            r'تجاوز[:\s]+([\d,./]+)'
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


def restructure_power_section_template8_json(extracted_json_path, output_json_path):
    """Restructure extracted JSON to include power section data for Template 8."""
    with open(extracted_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    text = data.get('text', '')
    
    # Extract power values
    power_data = extract_power_values(text)
    
    # Build restructured data
    result = {
        "power_section": power_data
    }
    
    # Save restructured JSON
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Restructured power section (Template 8) saved to: {output_json_path}")
    print(f"Extracted power values: {power_data}")
    
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python restructure_power_section_template8.py <extracted_json_file> [output_json_file]")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file.parent / f"{input_file.stem}_restructured.json"
    
    if not input_file.exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)
    
    restructure_power_section_template8_json(input_file, output_file)

