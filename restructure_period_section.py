"""Restructure period section JSON data."""
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

def extract_period_section_data(text):
    """Extract period section data from text."""
    # Initialize result structure
    result = {
        "از تاریخ": None,  # From Date
        "تا تاریخ": None,  # To Date
        "تعداد روز دوره": None  # Number of days in period
    }
    
    # Normalize text - convert Persian digits
    normalized_text = convert_persian_digits(text)
    
    # Split text into lines for easier processing
    lines = normalized_text.split('\n')
    
    # Pattern for dates: YYYY/MM/DD
    date_pattern = r'(\d{4}/\d{2}/\d{2})'
    
    # Extract dates - look for YYYY/MM/DD pattern in text
    # The text may have "از تاریخ:1404/01/01" or "از تاریخ: 1404/01/01" format
    all_dates = re.findall(date_pattern, normalized_text)
    
    # Extract "از تاریخ" (From Date)
    # Pattern: "از تاریخ:1404/01/01" or "از تاریخ: 1404/01/01" or "از تاریخ1404/01/01"
    for line in lines:
        # Look for "از" followed by optional spaces, then "تاریخ", then optional colon/space, then date
        match = re.search(r'از\s*تاريخ\s*:?\s*(\d{4}/\d{2}/\d{2})', line, re.IGNORECASE)
        if match:
            result["از تاریخ"] = match.group(1)
            break
    
    # Extract "تا تاریخ" (To Date)
    # Pattern: "تا تاریخ:1404/02/01" or similar
    for line in lines:
        # Look for "تا" followed by optional spaces, then "تاریخ", then optional colon/space, then date
        match = re.search(r'تا\s*تاريخ\s*:?\s*(\d{4}/\d{2}/\d{2})', line, re.IGNORECASE)
        if match:
            result["تا تاریخ"] = match.group(1)
            break
    
    # Extract "تعداد روز دوره" (Number of days in period)
    # Pattern: "تعداد روز دوره: 31" or "تعداد روز دوره31"
    for line in lines:
        # Look for "تعداد" then optional spaces, "روز", optional spaces, "دوره", optional colon/space, then number
        match = re.search(r'تعداد\s*روز\s*دوره\s*:?\s*(\d+)', line, re.IGNORECASE)
        if match:
            result["تعداد روز دوره"] = int(match.group(1))
            break
    
    # Fallback: If we found two dates but not the labels, assign them by position
    # (first date is "از تاریخ", second is "تا تاریخ")
    all_dates = re.findall(date_pattern, normalized_text)
    if len(all_dates) >= 2 and (result["از تاریخ"] is None or result["تا تاریخ"] is None):
        # Typically "از تاریخ" comes first, then "تا تاریخ"
        if result["از تاریخ"] is None:
            result["از تاریخ"] = all_dates[0]
        if result["تا تاریخ"] is None:
            result["تا تاریخ"] = all_dates[1]
    
    # Fallback: Look for number 31 or similar (common period length)
    if result["تعداد روز دوره"] is None:
        # Look for standalone numbers that might be period days
        # Typically 28-31 for monthly periods
        match = re.search(r'\b(2[89]|30|31)\b', normalized_text)
        if match:
            result["تعداد روز دوره"] = int(match.group(1))
    
    return result

def restructure_period_section_json(extracted_json_path, output_json_path):
    """Restructure extracted JSON to include period section data."""
    with open(extracted_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    text = data.get('text', '')
    
    # Extract period data
    period_data = extract_period_section_data(text)
    
    # Build restructured data
    result = {
        "اطلاعات دوره": period_data
    }
    
    # Save restructured JSON
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Restructured data saved to: {output_json_path}")
    
    # Print extracted values
    extracted_count = sum(1 for v in period_data.values() if v is not None)
    print(f"Extracted {extracted_count}/{len(period_data)} period fields")
    
    return result

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python restructure_period_section.py <extracted_json_file> [output_json_file]")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file.parent / f"{input_file.stem}_restructured.json"
    
    if not input_file.exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)
    
    restructure_period_section_json(input_file, output_file)
