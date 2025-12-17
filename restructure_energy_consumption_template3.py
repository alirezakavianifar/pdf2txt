"""Restructure energy consumption table section for Template 3."""
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
        # Try integer first
        if '.' not in text and '/' not in text:
            return int(text)
        else:
            # Handle decimal (slash or dot)
            text = text.replace('/', '.')
            return float(text)
    except ValueError:
        return None


def extract_energy_consumption_data(text):
    """Extract energy consumption table data from text.
    
    Expected columns:
    - شرح مصارف (Description)
    - شمارنده قبلی/کنونی (Previous/Current Counter)
    - ضریب (Coefficient)
    - مصرف کل (Total Consumption)
    - مصرف مشمول/غیرمشمول قانون جهش تولید
    - انرژی خریداری شده (Purchased Energy)
    - بهای انرژی (Energy Cost)
    """
    normalized_text = convert_persian_digits(text)
    
    # Initialize result structure
    result = {
        "جدول مصارف انرژی": {
            "rows": []
        }
    }
    
    # Split into lines
    lines = [line.strip() for line in normalized_text.split('\n') if line.strip()]
    
    # Try to extract rows
    # This is a simplified extraction - a more sophisticated approach would
    # parse the table structure more carefully
    
    # Common row descriptions to look for
    row_descriptions = [
        "اوج بار",
        "میان باری", 
        "کم باری",
        "جمعه و تعطیلات رسمی",
        "اوج بار جمعه"
    ]
    
    for desc in row_descriptions:
        # Find lines containing this description
        for line in lines:
            if desc in line:
                # Try to extract numbers from this line
                numbers = re.findall(r'\d+(?:,\d+)*(?:\.\d+)?', line)
                if numbers:
                    row_data = {
                        "شرح مصارف": desc,
                        "values": [parse_number(num) for num in numbers]
                    }
                    result["جدول مصارف انرژی"]["rows"].append(row_data)
                break
    
    return result


def restructure_energy_consumption_template3_json(extracted_json_path, output_json_path):
    """Restructure extracted JSON to include energy consumption table data for Template 3."""
    with open(extracted_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    text = data.get('text', '')
    
    # Extract energy consumption data
    consumption_data = extract_energy_consumption_data(text)
    
    # Build restructured data
    result = consumption_data
    
    # Save restructured JSON
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Restructured energy consumption table (Template 3) saved to: {output_json_path}")
    print(f"Extracted {len(consumption_data['جدول مصارف انرژی']['rows'])} rows")
    
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python restructure_energy_consumption_template3.py <extracted_json_file> [output_json_file]")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file.parent / f"{input_file.stem}_restructured.json"
    
    if not input_file.exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)
    
    restructure_energy_consumption_template3_json(input_file, output_file)
