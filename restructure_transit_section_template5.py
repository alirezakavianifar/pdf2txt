"""Restructure transit section for Template 5."""
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
    text = text.replace(',', '').replace(' ', '')
    
    try:
        return int(text)
    except ValueError:
        return None


def extract_transit_data(text):
    """Extract transit section data from text.
    
    Expected field:
    - بهای ترانزیت: ۶۳۷,۷۴۳,۹۴۸
    """
    normalized_text = convert_persian_digits(text)
    
    result = {
        "بهای ترانزیت": None
    }
    
    # Extract بهای ترانزیت
    match = re.search(r'بهای ترانزیت[^\d]*(\d+(?:,\d+)*)', normalized_text)
    if match:
        result["بهای ترانزیت"] = parse_number(match.group(1))
    else:
        # Fallback: look for large number in text
        numbers = re.findall(r'\d+(?:,\d+)*', normalized_text)
        if numbers:
            # Get the largest number
            parsed_numbers = [parse_number(num) for num in numbers if parse_number(num)]
            if parsed_numbers:
                result["بهای ترانزیت"] = max(parsed_numbers)
    
    return result


def restructure_transit_section_template5_json(json_path: Path, output_path: Path):
    """Restructure extracted JSON to include transit section data for Template 5."""
    print(f"Restructuring Transit Section (Template 5) from {json_path}...")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        text = data.get('text', '')
        
        # Extract transit data
        transit_data = extract_transit_data(text)
        
        # Build restructured data
        result = {
            "ترانزیت": transit_data
        }
        
        # Save restructured JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"  - Saved to {output_path}")
        if transit_data["بهای ترانزیت"]:
            print(f"  - Extracted transit price: {transit_data['بهای ترانزیت']}")
        else:
            print("  - WARNING: Could not extract transit price")
        
        return result
        
    except Exception as e:
        print(f"Error restructuring Transit Section T5: {e}")
        import traceback
        traceback.print_exc()
        return None

