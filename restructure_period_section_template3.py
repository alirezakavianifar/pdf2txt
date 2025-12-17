"""Restructure period section for Template 3."""
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


def extract_period_data(text):
    """Extract period information from text.
    
    Expected fields for Template 3:
    - از تاریخ (From Date): 1403/09/01
    - تا تاریخ (To Date): 1403/10/01
    - تعداد روز دوره (Days): 30
    - دوره/سال (Period/Year): 1403/10
    """
    normalized_text = convert_persian_digits(text)
    
    result = {
        "از تاریخ": None,
        "تا تاریخ": None,
        "تعداد روز دوره": None,
        "دوره/سال": None
    }
    
    lines = normalized_text.split('\n')
    
    # Extract از تاریخ (From Date)
    for line in lines:
        match = re.search(r'از تاریخ\s*:?\s*(\d{4}/\d{2}/\d{2})', line)
        if match:
            result["از تاریخ"] = match.group(1)
            break
    
    # Extract تا تاریخ (To Date)
    for line in lines:
        match = re.search(r'تا تاریخ\s*:?\s*(\d{4}/\d{2}/\d{2})', line)
        if match:
            result["تا تاریخ"] = match.group(1)
            break
    
    # Extract تعداد روز دوره (Number of Days)
    for line in lines:
        match = re.search(r'تعداد روز دوره\s*:?\s*(\d+)', line)
        if match:
            result["تعداد روز دوره"] = int(match.group(1))
            break
    
    # Extract دوره/سال (Period/Year)
    for line in lines:
        match = re.search(r'دوره\s*/?\s*سال\s*:?\s*(\d{4}/\d{2})', line)
        if match:
            result["دوره/سال"] = match.group(1)
            break
    
    # Fallback: try to find just دوره followed by date pattern
    if result["دوره/سال"] is None:
        for line in lines:
            match = re.search(r'دوره\s*:?\s*(\d{4}/\d{2})', line)
            if match:
                result["دوره/سال"] = match.group(1)
                break
    
    return result


def restructure_period_section_template3_json(extracted_json_path, output_json_path):
    """Restructure extracted JSON to include period section data for Template 3."""
    with open(extracted_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    text = data.get('text', '')
    
    # Extract period data
    period_data = extract_period_data(text)
    
    # Build restructured data
    result = {
        "اطلاعات دوره": period_data
    }
    
    # Save restructured JSON
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Restructured period section (Template 3) saved to: {output_json_path}")
    
    # Print extracted values
    extracted_count = sum(1 for v in period_data.values() if v is not None)
    print(f"Extracted {extracted_count}/{len(period_data)} period fields")
    
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python restructure_period_section_template3.py <extracted_json_file> [output_json_file]")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file.parent / f"{input_file.stem}_restructured.json"
    
    if not input_file.exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)
    
    restructure_period_section_template3_json(input_file, output_file)
