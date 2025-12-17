"""Restructure license expiry section for Template 3."""
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


def extract_license_expiry_date(text):
    """Extract license expiry date from text."""
    # Normalize Persian digits first
    normalized_text = convert_persian_digits(text)
    
    # Pattern: "تاریخ انقضا پروانه : YYYY/MM/DD" or similar
    patterns = [
        r'تاریخ انقضا پروانه\s*:\s*(\d{4}/\d{2}/\d{2})',
        r'انقضا پروانه\s*:\s*(\d{4}/\d{2}/\d{2})',
        r'انقضا\s*:\s*(\d{4}/\d{2}/\d{2})',
        r'پروانه\s*:\s*(\d{4}/\d{2}/\d{2})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, normalized_text)
        if match:
            return match.group(1)
    
    # Fallback: find any date-like pattern YYYY/MM/DD
    date_pattern = r'(\d{4}/\d{2}/\d{2})'
    match = re.search(date_pattern, normalized_text)
    if match:
        return match.group(1)
    
    return None


def restructure_license_expiry_template3_json(extracted_json_path, output_json_path):
    """Restructure extracted JSON to include license expiry data for Template 3."""
    with open(extracted_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    text = data.get('text', '')
    
    # Extract date
    expiry_date = extract_license_expiry_date(text)
    
    # Build restructured data
    result = {
        "تاریخ انقضا پروانه": expiry_date
    }
    
    # Save restructured JSON
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Restructured license expiry (Template 3) saved to: {output_json_path}")
    if expiry_date:
        print(f"Extracted expiry date: {expiry_date}")
    else:
        print("WARNING: Could not extract expiry date")
    
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python restructure_license_expiry_template3.py <extracted_json_file> [output_json_file]")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file.parent / f"{input_file.stem}_restructured.json"
    
    if not input_file.exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)
    
    restructure_license_expiry_template3_json(input_file, output_file)
