"""Restructure rate difference table section for Template 3."""
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
        try:
            return float(text)
        except ValueError:
            return None


def extract_rate_difference_data(text):
    """Extract rate difference table data from text.
    
    Header: شرح مصارف و مابه التفاوت نرخ تجدیدپذیر
    Rows: میان باری, اوج بار, کم باری, اوج بار جمعه
    Columns: مصرف مشمول, خرید از نیروگاه, خرید از تابلو سبز, تولید, مصرف قابل محاسبه, نرخ, مبلغ
    """
    normalized_text = convert_persian_digits(text)
    
    result = {
        "شرح مصارف و مابه التفاوت نرخ تجدیدپذیر": {
            "rows": []
        }
    }
    
    lines = [line.strip() for line in normalized_text.split('\n') if line.strip()]
    
    # Row descriptions to look for
    row_descriptions = [
        "میان باری",
        "اوج بار",
        "کم باری",
        "اوج بار جمعه"
    ]
    
    for desc in row_descriptions:
        for line in lines:
            if desc in line:
                # Try to extract numbers from this line
                numbers = re.findall(r'-?\d+(?:,\d+)*(?:\.\d+)?', line)
                if numbers:
                    row_data = {
                        "شرح مصارف": desc,
                        "values": [parse_number(num) for num in numbers]
                    }
                    result["شرح مصارف و مابه التفاوت نرخ تجدیدپذیر"]["rows"].append(row_data)
                break
    
    return result


def restructure_rate_difference_template3_json(extracted_json_path, output_json_path):
    """Restructure extracted JSON to include rate difference table data for Template 3."""
    with open(extracted_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    text = data.get('text', '')
    
    # Extract rate difference data
    rate_data = extract_rate_difference_data(text)
    
    # Build restructured data
    result = rate_data
    
    # Save restructured JSON
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Restructured rate difference table (Template 3) saved to: {output_json_path}")
    print(f"Extracted {len(rate_data['شرح مصارف و مابه التفاوت نرخ تجدیدپذیر']['rows'])} rows")
    
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python restructure_rate_difference_template3.py <extracted_json_file> [output_json_file]")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file.parent / f"{input_file.stem}_restructured.json"
    
    if not input_file.exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)
    
    restructure_rate_difference_template3_json(input_file, output_file)
