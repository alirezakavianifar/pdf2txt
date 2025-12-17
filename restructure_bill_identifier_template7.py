"""Restructure bill identifier section for Template 7."""
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


def extract_bill_identifier(text):
    """Extract bill identifier (13-digit number) from text."""
    # Normalize Persian digits
    normalized_text = convert_persian_digits(text)
    
    # Remove spaces and newlines for easier matching
    text_clean = normalized_text.replace(' ', '').replace('\n', '')
    
    # Look for "شناسه قبض" followed by a number
    patterns = [
        r'شناسه قبض\s*:?\s*(\d{13})',
        r'شناسه قبض\s*(\d{13})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, normalized_text)
        if match:
            return match.group(1)
    
    # Fallback: look for 13-digit number
    match = re.search(r'\d{13}', text_clean)
    if match:
        return match.group(0)
    
    # Fallback: find longest sequence of digits
    matches = re.findall(r'\d+', text_clean)
    if matches:
        return max(matches, key=len)
    
    return None


def restructure_bill_identifier_template7_json(extracted_json_path, output_json_path):
    """Restructure extracted JSON to include bill identifier data for Template 7."""
    with open(extracted_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    text = data.get('text', '')
    
    # Extract bill identifier
    identifier = extract_bill_identifier(text)
    
    # Build restructured data
    result = {
        "شناسه قبض": identifier
    }
    
    # Save restructured JSON
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Restructured bill identifier (Template 7) saved to: {output_json_path}")
    if identifier:
        print(f"Extracted identifier: {identifier}")
    else:
        print("WARNING: Could not extract bill identifier")
    
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python restructure_bill_identifier_template7.py <extracted_json_file> [output_json_file]")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file.parent / f"{input_file.stem}_restructured.json"
    
    if not input_file.exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)
    
    restructure_bill_identifier_template7_json(input_file, output_file)

