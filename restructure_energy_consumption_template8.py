"""Restructure energy consumption table section for Template 8."""
import json
import re
from pathlib import Path


def convert_persian_digits(text):
    """Convert Persian/Arabic-Indic digits to regular digits."""
    persian_digits = '۰۱۲۳۴۵۶۷۸۹'
    arabic_indic_digits = '٠١٢٣٤٥٦٧٨٩'
    regular_digits = '0123456789'
    
    result = str(text)
    for i, persian in enumerate(persian_digits):
        result = result.replace(persian, regular_digits[i])
    for i, arabic in enumerate(arabic_indic_digits):
        result = result.replace(arabic, regular_digits[i])
    
    return result


def parse_number(text):
    """Parse a number, removing commas and handling Persian digits."""
    if not text or text == '.' or text.strip() == '':
        return None
    
    text = convert_persian_digits(str(text))
    # Remove commas used as thousand separators
    text = text.replace(',', '').replace(' ', '').strip()
    
    if not text or text == '.':
        return None
    
    try:
        # Handle decimal numbers (may use slash or dot)
        if '/' in text:
            text = text.replace('/', '.')
        if '.' in text:
            return float(text)
        else:
            return int(text)
    except ValueError:
        return None


def extract_energy_consumption_from_table(data):
    """Extract energy consumption table data from table structure.
    
    Uses Persian field names.
    """
    # Initialize result with Persian section and field names
    result = {
        "جدول مصارف انرژی": {
            "انرژی قرائت شده": {
                "ردیف": []
            },
            "خرید سبز": {
                "بورس": {},
                "دو جانبه": {}
            },
            "خرید عادی": {
                "بورس": {},
                "دو جانبه": {}
            },
            "نرخ": {
                "ردیف": []
            },
            "ماده ۵": {
                "ردیف": []
            },
            "ماده ۱۶": {
                "ردیف": []
            },
            "سایر": {
                "ردیف": []
            }
        }
    }
    
    table_data = data.get('table', {})
    rows = table_data.get('rows', [])
    
    if not rows:
        return result
    
    # Map OCR text variations to standard Persian consumption types
    ocr_to_persian = {
        "(cid:187)یار باکی": "میان باری",
        "یار باکی": "میان باری",  # Alternative without cid
        "ثزص باکی": "اوج باری",
        "ک(cid:186) باکی": "کم باری",
        "ک باکی": "کم باری",  # Alternative
        "ثزص باک ص(cid:188)ع(cid:196)": "اوج بار جمعه",
        "(cid:196)ع(cid:188)ثزص باک ص": "اوج بار جمعه",  # Alternative order
        "کثکسی(cid:194)": "راکتیو",
        "(cid:194)کثکسی": "راکتیو"  # Alternative order
    }
    
    read_energy_rows = []
    processed_rows = set()  # Track which rows we've processed
    
    # Process rows to extract Read Energy section (typically rows 1-5)
    for row_idx, row in enumerate(rows[:15]):  # Check first 15 rows
        if not row or not isinstance(row, list) or row_idx in processed_rows:
            continue
        
        # Find consumption type and its position
        consumption_type = None
        desc_position = -1
        
        for idx, cell in enumerate(row):
            if cell and isinstance(cell, str):
                # Check OCR variations first (more specific)
                for ocr_text, persian_type in ocr_to_persian.items():
                    if ocr_text in cell:
                        consumption_type = persian_type
                        desc_position = idx
                        break
                if consumption_type:
                    break
        
        if not consumption_type or desc_position < 0:
            continue
        
        processed_rows.add(row_idx)
        
        # Extract the numeric values before the description
        # Based on observed structure, going backwards from description:
        # - Previous counter: ~4 positions before
        # - Current counter: ~8 positions before  
        # - Total consumption: ~13 positions before
        # - Amount: ~17 positions before (may be 0 for some rows)
        
        numeric_values = []
        for idx in range(desc_position - 1, max(-1, desc_position - 25), -1):
            if idx < 0 or idx >= len(row):
                continue
            cell = row[idx]
            if cell and isinstance(cell, str) and cell.strip() and cell.strip() != '':
                # Check if it contains digits (including zeros)
                if any(c.isdigit() for c in cell):
                    parsed = parse_number(cell)
                    if parsed is not None:  # Include zeros
                        numeric_values.append((idx, parsed, cell.strip()))
                        if len(numeric_values) >= 4:
                            break
        
        # If we found at least some values (including zeros), process them
        # Going backwards from description: [0] is closest, [3] is farthest
        if len(numeric_values) >= 3:  # At least 3 values (some rows may have 0 for amount)
            # Sort by value size to help identify
            sorted_by_value = sorted(numeric_values, key=lambda x: x[1])
            
            # Identify each value by size:
            # - Amount is the largest (typically > 100 million)
            # - Total consumption is medium-large (typically 10,000 to 100,000,000)
            # - Previous and current counters are smallest (typically < 10,000, but can be larger for اوج باری)
            
            amount_val = None
            total_val = None
            curr_val = None
            prev_val = None
            
            # The largest value is the amount (if > 0), otherwise amount might be 0
            if sorted_by_value[-1][1] > 100000:
                amount_val = sorted_by_value[-1][1]
            else:
                # Amount might be 0 for some rows (like اوج بار جمعه)
                amount_val = 0
            
            # Find total consumption (medium size, typically 5-8 digits)
            for idx, val, orig in sorted_by_value[:-1]:
                if val > 0 and 10000 <= val <= 100000000:
                    total_val = val
                    break
            # If no total found, it might be 0
            if total_val is None:
                # Check if any value looks like total (larger than counters)
                for idx, val, orig in sorted_by_value:
                    if val > 1000 and val < 1000000 and val != amount_val:
                        total_val = val
                        break
                if total_val is None:
                    total_val = 0
            
            # The remaining two should be counters
            # Previous counter is closer to description (appears first when going backwards)
            # Current counter is further from description
            remaining = [v for v in numeric_values if v[1] != amount_val and (total_val is None or v[1] != total_val)]
            if len(remaining) >= 2:
                # Sort by position - going backwards, first encountered = closest to description = previous counter
                # The order in numeric_values is already backwards from description (closest first)
                prev_val = remaining[0][1]  # First in list = closest to description
                curr_val = remaining[1][1]  # Second in list = further from description
            elif len(remaining) == 1:
                prev_val = remaining[0][1]
            
            # Also handle case where total wasn't identified correctly
            if total_val is None and len(sorted_by_value) >= 3:
                # Try to identify total from remaining values (should be medium-sized)
                for idx, val, orig in sorted_by_value:
                    if val != amount_val and val not in [prev_val, curr_val]:
                        if 1000 <= val <= 100000000:  # More lenient range
                            total_val = val
                            break
            
            # Special case: Handle OCR error for اوج باری where 25778 might be split as 251/78
            # If previous counter seems too small and current counter also seems small, check if they should be combined
            # But for now, we'll use what's extracted - note: image shows 25778 but OCR extracted 251/78
            
            # Create row data - include all rows even if some values are 0
            row_data = {
                "شرح مصارف": consumption_type,
                "شمارنده قبلی": prev_val if prev_val is not None else 0,
                "شمارنده کنونی": curr_val if curr_val is not None else 0,
                "مصرف کل": total_val if total_val is not None else 0,
                "مبلغ": amount_val if amount_val is not None else 0
            }
            read_energy_rows.append(row_data)
    
    result["جدول مصارف انرژی"]["انرژی قرائت شده"]["ردیف"] = read_energy_rows
    
    return result


def restructure_energy_consumption_template8_json(extracted_json_path, output_json_path):
    """Restructure extracted JSON to include energy consumption table data for Template 8."""
    with open(extracted_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract from table structure
    energy_data = extract_energy_consumption_from_table(data)
    
    # Build restructured data
    result = energy_data
    
    # Save restructured JSON
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Restructured energy consumption table (Template 8) saved to: {output_json_path}")
    
    # Print summary
    read_rows = len(energy_data["جدول مصارف انرژی"]["انرژی قرائت شده"]["ردیف"])
    print(f"Extracted {read_rows} read energy rows")
    
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python restructure_energy_consumption_template8.py <extracted_json_file> [output_json_file]")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file.parent / f"{input_file.stem}_restructured.json"
    
    if not input_file.exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)
    
    restructure_energy_consumption_template8_json(input_file, output_file)
