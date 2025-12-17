"""Restructure rate difference table section for Template 5."""
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


def extract_rate_difference_data(text, table_data=None):
    """Extract rate difference table data from text.
    
    Header: مشمول ما بالتفاوت اجرای مقررات
    Rows: میان باری, اوج بار, کم باری, اوج بار جمعه
    Columns: شرح مصارف, مصرف, مبلغ, خرید بورس آزاد
    """
    normalized_text = convert_persian_digits(text)
    
    result = {
        "مشمول ما بالتفاوت اجرای مقررات": {
            "rows": []
        }
    }
    
    # Try to use table data if available
    if table_data and 'rows' in table_data:
        for row in table_data['rows']:
            if len(row) > 0:
                desc = row[0] if row[0] else ""
                if any(keyword in desc for keyword in ["میان باری", "اوج بار", "کم باری", "اوج بار جمعه"]):
                    row_data = {
                        "شرح مصارف": desc,
                        "values": [parse_number(cell) if cell else None for cell in row[1:]]
                    }
                    result["مشمول ما بالتفاوت اجرای مقررات"]["rows"].append(row_data)
        return result
    
    # Fallback: parse from text
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
                    result["مشمول ما بالتفاوت اجرای مقررات"]["rows"].append(row_data)
                break
    
    return result


def restructure_rate_difference_template5_json(json_path: Path, output_path: Path):
    """Restructure extracted JSON to include rate difference table data for Template 5."""
    print(f"Restructuring Rate Difference Table (Template 5) from {json_path}...")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        text = data.get('text', '')
        table_data = data.get('table', {})
        
        # Extract rate difference data
        rate_data = extract_rate_difference_data(text, table_data)
        
        # Build restructured data
        result = rate_data
        
        # Save restructured JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"  - Saved to {output_path}")
        row_count = len(rate_data['مشمول ما بالتفاوت اجرای مقررات']['rows'])
        print(f"  - Extracted {row_count} rows")
        
        return result
        
    except Exception as e:
        print(f"Error restructuring Rate Difference Table T5: {e}")
        import traceback
        traceback.print_exc()
        return None

