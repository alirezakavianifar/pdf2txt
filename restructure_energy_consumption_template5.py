"""Restructure energy consumption table section for Template 5."""
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


def extract_energy_consumption_data(text, table_data=None):
    """Extract energy consumption table data from text.
    
    Expected columns (after fixing RTL/reversal):
    - شرح مصارف (Description): میان باری, اوج بار, کم باری, اوج بار جمعه
    - شمارنده قبلی (Previous Counter)
    - شمارنده کنونی (Current Counter)
    - رقم (Digit)
    - ضریب (Coefficient): ۳,۰۰۰
    - مصرف (Kwh) (Consumption)
    - مشمول تجدید پذیر (Renewable Included)
    - خرید تجدید پذیر (Renewable Purchase)
    - تولید تجدید پذیر (Renewable Production)
    - خرید بورس و دو جانبه (Exchange and Bilateral Purchase)
    - مصرف تامین شده به نیابت (Consumption Supplied by Proxy) - with sub-columns: مصرف, نرخ
    - بهای انرژی (Energy Price)
    """
    normalized_text = convert_persian_digits(text)
    
    # Initialize result structure
    result = {
        "جدول مصارف انرژی": {
            "rows": []
        }
    }
    
    # Keywords map (Standard -> Reversed/Alternative)
    keywords_map = {
        "میان باری": ["میان باری", "یراب نایم", "ن ی ا ب ن ا ی م"],
        "اوج بار": ["اوج بار", "راب جوا", "ر ا ب ج و ا"],
        "کم باری": ["کم باری", "یراب مک", "ر ا ب ک م"],
        "اوج بار جمعه": ["اوج بار جمعه", "بار جمعه", "یار جمعه", "هعمج راب", "هعمج رای", "ه ع م ج ر ا ب"],
        "جمع": ["جمع", "ع مج", "ع م ج", "عمج"]
    }
    
    # Column mapping based on Template 5 layout (RTL -> Reversed Row List)
    field_names = [
        "شمارنده قبلی",
        "شمارنده کنونی",
        "رقم",
        "ضریب",
        "مصرف",
        "مشمول تجدید پذیر",
        "خرید تجدید پذیر",
        "تولید تجدید پذیر",
        "خرید بورس و دوجانبه",
        "مصرف تامین شده به نیابت - مصرف",
        "مصرف تامین شده به نیابت - نرخ",
        "بهای انرژی"
    ]

    # Try to use table data if available
    if table_data and 'rows' in table_data:
        for row in table_data['rows']:
            if len(row) > 0:
                # Check both first and last column for description
                first_cell = row[0] if row[0] else ""
                last_cell = row[-1] if row[-1] else ""
                
                matched_desc = None
                processing_row = row
                
                # Check first cell
                for key, variants in keywords_map.items():
                    if any(v in first_cell for v in variants):
                        matched_desc = key
                        break
                
                # If not found, check last cell (reversed table case)
                if not matched_desc:
                    for key, variants in keywords_map.items():
                        if any(v in last_cell for v in variants):
                            matched_desc = key
                            # If found in last cell, reverse the row to match expected order
                            processing_row = list(reversed(row))
                            break
                            
                if matched_desc:
                    values = [parse_number(cell) if cell else None for cell in processing_row[1:]]
                    
                    row_data = {
                        "شرح مصارف": matched_desc,
                    }
                    
                    # Map values to fields
                    for i, field in enumerate(field_names):
                        if i < len(values):
                            row_data[field] = values[i]
                        else:
                            row_data[field] = None
                            
                    result["جدول مصارف انرژی"]["rows"].append(row_data)
        
        if result["جدول مصارف انرژی"]["rows"]:
            return result
    
    # Fallback: parse from text
    lines = [line.strip() for line in normalized_text.split('\n') if line.strip()]
    
    for key, variants in keywords_map.items():
        # Find lines containing this description
        for line in lines:
            if any(v in line for v in variants):
                # Try to extract numbers from this line
                numbers = re.findall(r'\d+(?:,\d+)*(?:[/\.]\d+)?', line)
                if numbers:
                    values = [parse_number(num) for num in numbers]
                    
                    row_data = {
                        "شرح مصارف": key,
                    }
                    
                    # Map values to fields (best effort)
                    # In text extraction, we might get fewer or different numbers. 
                    # We'll map as many as we have to the initial fields.
                    for i, field in enumerate(field_names):
                        if i < len(values):
                            row_data[field] = values[i]
                        else:
                            row_data[field] = None
                            
                    result["جدول مصارف انرژی"]["rows"].append(row_data)
                break
    
    return result


def restructure_energy_consumption_template5_json(json_path: Path, output_path: Path):
    """Restructure extracted JSON to include energy consumption table data for Template 5."""
    print(f"Restructuring Energy Consumption Table (Template 5) from {json_path}...")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        text = data.get('text', '')
        table_data = data.get('table', {})
        
        # Extract energy consumption data
        consumption_data = extract_energy_consumption_data(text, table_data)
        
        # Build restructured data
        result = consumption_data
        
        # Save restructured JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"  - Saved to {output_path}")
        row_count = len(consumption_data['جدول مصارف انرژی']['rows'])
        print(f"  - Extracted {row_count} rows")
        
        return result
        
    except Exception as e:
        print(f"Error restructuring Energy Consumption Table T5: {e}")
        import traceback
        traceback.print_exc()
        return None

