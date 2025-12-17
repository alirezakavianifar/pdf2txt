"""Restructure energy consumption table section for Template 6."""
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
    if not text or text == '.' or text.strip() == '':
        return None
    
    text = convert_persian_digits(text)
    # Remove commas used as thousand separators
    text = text.replace(',', '').replace(' ', '').strip()
    
    if not text or text == '.':
        return None
    
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


def extract_energy_consumption_data(text, table_data=None):
    """Extract energy consumption table data from text.
    
    Expected columns (14 columns):
    - شرح مصارف (Description): میان بار, اوج بار, کم بار, جمعه, راکتیو
    - شمارنده قبلی (Previous Counter)
    - شمارنده فعلی (Current Counter)
    - تعداد ارقام (Number of Digits): 6
    - ضریب کنتور (Meter Coefficient): 4,000
    - انرژی قرائت شده (Read Energy)
    - انرژی خریداری شده دوجانبه و بورس (Energy Purchased Bilaterally and from Exchange)
    - انرژی مازاد خرید از بازار (Excess Energy Purchased from Market)
    - انرژی خریداری شده دو جانبه سبز (Green Bilaterally Purchased Energy)
    - مصرف قانون جهش تولید (Consumption under Production Leap Law)
    - انرژی تامین شده توسط توزیع (Energy Supplied by Distribution)
    - بهای انرژی تامین شده توسط توزیع (Cost of Energy Supplied by Distribution)
    - انرژی مشمول تعرفه (۴- الف) (Energy Subject to Tariff 4-A)
    - انرژی مشمول تعرفه (۴-د) (Energy Subject to Tariff 4-D)
    """
    normalized_text = convert_persian_digits(text)
    
    # Initialize result structure
    result = {
        "جدول مصارف انرژی": {
            "rows": []
        }
    }
    
    # Try to use table data if available
    if table_data and 'rows' in table_data:
        for row in table_data['rows']:
            if len(row) > 0:
                # First cell should be description
                desc = row[0] if row[0] else ""
                if any(keyword in desc for keyword in ["میان بار", "اوج بار", "کم بار", "جمعه", "راکتیو"]):
                    row_data = {
                        "شرح مصارف": desc,
                        "شمارنده قبلی": parse_number(row[1]) if len(row) > 1 else None,
                        "شمارنده فعلی": parse_number(row[2]) if len(row) > 2 else None,
                        "تعداد ارقام": parse_number(row[3]) if len(row) > 3 else None,
                        "ضریب کنتور": parse_number(row[4]) if len(row) > 4 else None,
                        "انرژی قرائت شده": parse_number(row[5]) if len(row) > 5 else None,
                        "انرژی خریداری شده دوجانبه و بورس": parse_number(row[6]) if len(row) > 6 else None,
                        "انرژی مازاد خرید از بازار": parse_number(row[7]) if len(row) > 7 else None,
                        "انرژی خریداری شده دو جانبه سبز": parse_number(row[8]) if len(row) > 8 else None,
                        "مصرف قانون جهش تولید": parse_number(row[9]) if len(row) > 9 else None,
                        "انرژی تامین شده توسط توزیع": parse_number(row[10]) if len(row) > 10 else None,
                        "بهای انرژی تامین شده توسط توزیع": parse_number(row[11]) if len(row) > 11 else None,
                        "انرژی مشمول تعرفه (۴- الف)": parse_number(row[12]) if len(row) > 12 else None,
                        "انرژی مشمول تعرفه (۴-د)": parse_number(row[13]) if len(row) > 13 else None
                    }
                    result["جدول مصارف انرژی"]["rows"].append(row_data)
        return result
    
    # Fallback: parse from text
    lines = [line.strip() for line in normalized_text.split('\n') if line.strip()]
    
    # Common row descriptions to look for
    row_descriptions = [
        "میان بار",
        "اوج بار",
        "کم بار",
        "جمعه",
        "راکتیو"
    ]
    
    for desc in row_descriptions:
        # Find lines containing this description
        for line in lines:
            if desc in line:
                # Try to extract numbers from this line
                numbers = re.findall(r'\d+(?:,\d+)*(?:[/\.]\d+)?', line)
                if numbers:
                    row_data = {
                        "شرح مصارف": desc,
                        "values": [parse_number(num) for num in numbers]
                    }
                    result["جدول مصارف انرژی"]["rows"].append(row_data)
                break
    
    return result


def restructure_energy_consumption_template6_json(json_path: Path, output_path: Path):
    """Restructure extracted JSON to include energy consumption table data for Template 6."""
    print(f"Restructuring Energy Consumption Table (Template 6) from {json_path}...")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        text = data.get('text', '')
        table_data = data.get('table', {})
        
        # Extract energy consumption data
        energy_data = extract_energy_consumption_data(text, table_data)
        
        # Build restructured data
        result = energy_data
        
        # Save restructured JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"  - Saved to {output_path}")
        row_count = len(energy_data["جدول مصارف انرژی"]["rows"])
        print(f"  - Extracted {row_count} consumption rows")
        
        return result
        
    except Exception as e:
        print(f"Error restructuring Energy Consumption T6: {e}")
        import traceback
        traceback.print_exc()
        return None

