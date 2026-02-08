"""
Restructure consumption table section for Template 9.
This handles the "جدول مصارف" (Consumption Table) with 8 columns.

The table has columns:
- شرح مصارف (Description: میانباری, اوج بار, کمباری, اوج بار جمعه, راکتیو)
- رقم (Number/Digit)
- شمارنده قبلی (Previous meter reading)
- شمارنده کنونی (Current meter reading)
- ضریب (Coefficient/Factor)
- مصرف (Consumption in kWh)
- نرخ (Rate)
- مبلغ (Amount in Rial)
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional


def convert_persian_digits(text: str) -> str:
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


def clean_number(text: str) -> Optional[float]:
    """Clean and convert text to number."""
    if not text or text == '':
        return None
    
    # Convert Persian digits first
    cleaned = convert_persian_digits(text.strip())
    
    # Handle "/" format (e.g., "2728/00" means 2728.00)
    if '/' in cleaned and not cleaned.startswith('/'):
        parts = cleaned.split('/')
        if len(parts) == 2:
            try:
                # Convert "2728/00" to 2728.00
                whole = parts[0].replace(',', '').replace(' ', '')
                decimal = parts[1].replace(',', '').replace(' ', '')
                cleaned = f"{whole}.{decimal}"
            except:
                pass
    
    # Remove common separators
    cleaned = cleaned.replace(',', '').replace('٬', '').replace(' ', '').replace('،', '').strip()
    
    if not cleaned or cleaned == '-' or cleaned == '.' or cleaned == '/':
        return None
    
    try:
        if '.' in cleaned:
            return float(cleaned)
        else:
            return int(cleaned)
    except ValueError:
        return None


def parse_consumption_table_template9(text: str, geometry_data: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Parse the consumption table section for Template 9.
    
    Expected structure:
    شرح مصارف | رقم | شمارنده قبلی | شمارنده کنونی | ضریب | مصرف | نرخ | مبلغ
    میانباری | 4 | 664.22 | 668.13 | 80000 | 312720.0 | 409.00 | 127902480
    ...
    """
    
    # Initialize result structure
    result = {
        "rows": [],
        "table_type": "جدول مصارف"
    }
    
    # Known consumption categories (in various forms)
    # Include encoded variations and partial matches
    categories = {
        'میانباری': 'mid_load',
        'میان بار': 'mid_load',
        'میان': 'mid_load',  # Partial match
        'اوج بار': 'peak_load',
        'اوج باری': 'peak_load',
        'اوج': 'peak_load',  # Partial match
        'کمباری': 'low_load',
        'کم بار': 'low_load',
        'کم': 'low_load',  # Partial match
        'اوج بار جمعه': 'friday_peak',
        'جمعه': 'friday_peak',  # Partial match
        'راکتیو': 'reactive'
    }
    
    # Category name patterns that might appear in encoded text
    # These are character sequences that might match even with encoding issues
    category_patterns = {
        'mid_load': [r'میان', r'باری', r'میان\s*بار'],
        'peak_load': [r'اوج', r'بار', r'اوج\s*بار'],
        'low_load': [r'کم', r'بار', r'کم\s*بار'],
        'friday_peak': [r'جمعه', r'اوج\s*بار\s*جمعه'],
        'reactive': [r'راکتیو', r'راکت']
    }
    
    # If geometry data is available, use it (more reliable for fragmented text)
    if geometry_data and 'cells' in geometry_data:
        cells = geometry_data['cells']
        
        # Group cells by row
        rows_dict = {}
        for cell in cells:
            row_idx = cell.get('row', 0)
            col_idx = cell.get('col', 0)
            cell_text = cell.get('text', '').strip()
            
            if row_idx not in rows_dict:
                rows_dict[row_idx] = {}
            rows_dict[row_idx][col_idx] = cell_text
        
        # Process each row (skip header row, typically row 0 or 1)
        for row_idx in sorted(rows_dict.keys()):
            if row_idx < 2:  # Skip header rows
                continue
            
            row_cells = rows_dict[row_idx]
            if not row_cells:
                continue
            
            # Try to identify category from first column (col 0 or col 7 depending on RTL)
            category_text = ''
            category_key = None
            
            # Check last column (col 7) for category name (RTL layout)
            if 7 in row_cells:
                category_text = convert_persian_digits(row_cells[7])
                # Remove CID encoding artifacts
                category_text = re.sub(r'\(cid:\d+\)', '', category_text)
                # Remove other special characters that might interfere
                category_text = re.sub(r'[^\w\s]', '', category_text).strip()
                
                # Try exact match first
                for cat, key in categories.items():
                    if cat in category_text:
                        category_key = key
                        break
                
                # Try pattern-based matching if exact match failed
                if not category_key:
                    for key, patterns in category_patterns.items():
                        for pattern in patterns:
                            if re.search(pattern, category_text, re.IGNORECASE):
                                category_key = key
                                break
                        if category_key:
                            break
                
                # Try partial match if pattern matching failed
                if not category_key:
                    for cat, key in categories.items():
                        # Check if any significant part of category name appears
                        cat_parts = cat.split()
                        if any(part in category_text for part in cat_parts if len(part) > 2):
                            category_key = key
                            break
            
            # If not found, check first column
            if not category_key and 0 in row_cells:
                category_text = convert_persian_digits(row_cells[0])
                category_text = re.sub(r'\(cid:\d+\)', '', category_text)
                for cat, key in categories.items():
                    if cat in category_text:
                        category_key = key
                        break
            
            # If still not found, try to infer from row position or just use generic
            if not category_key:
                # Try to extract any meaningful text as category
                if 7 in row_cells and row_cells[7].strip():
                    category_text = convert_persian_digits(row_cells[7])
                    category_text = re.sub(r'\(cid:\d+\)', '', category_text).strip()
                    category_key = 'unknown'
                elif 0 in row_cells and row_cells[0].strip() and not re.match(r'^[\d,.\s-]+$', row_cells[0]):
                    category_text = convert_persian_digits(row_cells[0])
                    category_text = re.sub(r'\(cid:\d+\)', '', category_text).strip()
                    category_key = 'unknown'
                else:
                    continue
            
            # Extract values from cells
            # There are two possible table structures (RTL layout):
            # Structure A: col 0=مبلغ, col 1=نرخ, col 2=(rate), col 3=مصرف, col 4=شمارنده کنونی, col 5=شمارنده قبلی, col 6=ضریب, col 7=شرح
            # Structure B: col 0=مبلغ, col 1=نرخ, col 2=مصرف, col 3=ضریب کنتور, col 4=شمارنده کنونی, col 5=شمارنده قبلی, col 6=رقم, col 7=شرح
            
            row_data = {
                "شرح مصارف": category_text if category_text else None,
                "category_key": category_key,
                "رقم": None,
                "شمارنده قبلی": None,
                "شمارنده کنونی": None,
                "ضریب": None,
                "مصرف": None,
                "نرخ": None,
                "مبلغ": None
            }
            
            # Extract all numeric values first to detect structure
            col_values = {}
            for col_idx in range(8):
                if col_idx in row_cells:
                    col_values[col_idx] = clean_number(row_cells[col_idx])
            
            # Detect structure by checking value ranges
            # Structure A: col 3 has consumption (typically 2000-50000), col 6 has small coefficient (4, 2000, 2400, 80000)
            # Structure B: col 2 has consumption (typically large like 110900), col 3 has meter coefficient (2000, 2400)
            is_structure_b = False
            if 2 in col_values and 3 in col_values and 6 in col_values:
                col2_val = col_values[2]
                col3_val = col_values[3]
                col6_val = col_values[6]
                
                # Check col 6 first: if it's 4 (or small), it's likely Structure A (row coefficient)
                # Structure A has row coefficient in col 6 (typically 4)
                # Structure B has رقم in col 6 (could be 4, 5, etc.)
                
                # If col 6 is 4 and col 3 is a reasonable consumption value (2000-50000), it's Structure A
                if col6_val and col6_val == 4 and col3_val and 2000 <= col3_val <= 50000:
                    is_structure_b = False  # Structure A
                # If col 3 is a meter coefficient (2000-10000) and col 2 is large consumption (>50000), it's Structure B
                elif col2_val and col3_val and col2_val > 50000 and 2000 <= col3_val <= 10000:
                    is_structure_b = True  # Structure B
                # If col 2 is large (>10000) but col 3 is also large (>10000), col 2 might be a rate, so check col 6
                elif col2_val and col3_val and col2_val > 10000 and col3_val > 10000:
                    # Both are large, check col 6 to decide
                    if col6_val and col6_val == 4:
                        is_structure_b = False  # Structure A (col 2 is rate, col 3 is consumption)
                    else:
                        # Need more context, check if col 3 looks like consumption
                        if 2000 <= col3_val <= 50000:
                            is_structure_b = False  # Structure A
                        else:
                            is_structure_b = True  # Structure B
                # Default: if col 2 is large (>10000) and col 3 is small/medium (2000-10000), it's Structure B
                elif col2_val and col3_val and col2_val > 10000 and 2000 <= col3_val <= 10000:
                    # But only if col 6 is not 4 (which would indicate Structure A)
                    if col6_val and col6_val != 4:
                        is_structure_b = True
                    else:
                        is_structure_b = False  # Structure A (col 2 is rate, col 3 is consumption)
            
            # Map columns based on detected structure
            if 0 in row_cells:
                row_data["مبلغ"] = clean_number(row_cells[0])
            if 1 in row_cells:
                row_data["نرخ"] = clean_number(row_cells[1])
            
            if is_structure_b:
                # Structure B: consumption in col 2, meter coefficient in col 3
                if 2 in row_cells:
                    row_data["مصرف"] = clean_number(row_cells[2])
                if 3 in row_cells:
                    # This is ضریب کنتور (meter coefficient), store it for later
                    meter_coeff = clean_number(row_cells[3])
                    if meter_coeff:
                        row_data["ضریب"] = meter_coeff  # Store as row-level coefficient too
                if 4 in row_cells:
                    row_data["شمارنده کنونی"] = clean_number(row_cells[4])
                if 5 in row_cells:
                    row_data["شمارنده قبلی"] = clean_number(row_cells[5])
                if 6 in row_cells:
                    row_data["رقم"] = clean_number(row_cells[6])
            else:
                # Structure A: consumption in col 3, coefficient in col 6
                # col 2 contains additional rate/value, skip it
                if 3 in row_cells:
                    row_data["مصرف"] = clean_number(row_cells[3])
                if 4 in row_cells:
                    row_data["شمارنده کنونی"] = clean_number(row_cells[4])
                if 5 in row_cells:
                    row_data["شمارنده قبلی"] = clean_number(row_cells[5])
                if 6 in row_cells:
                    row_data["ضریب"] = clean_number(row_cells[6])
                    # رقم (Number) is typically the same as ضریب
                    if row_data["ضریب"] is not None:
                        row_data["رقم"] = int(row_data["ضریب"]) if row_data["ضریب"] == int(row_data["ضریب"]) else row_data["ضریب"]
            
            # Only add if we have at least some data
            if any(v is not None for v in [row_data["رقم"], row_data["مصرف"], row_data["مبلغ"]]):
                result["rows"].append(row_data)
        
        return result
    
    # Fallback to text-based parsing if no geometry data
    # Normalize text - convert Persian digits
    normalized_text = convert_persian_digits(text)
    
    # Split text into lines
    lines = [line.strip() for line in normalized_text.strip().split('\n') if line.strip()]
    
    for line in lines:
        # Skip header lines
        if 'شرح مصارف' in line or 'شمارنده' in line or 'ضریب' in line:
            continue
        
        # Check if this line contains a known category
        matched_category = None
        matched_key = None
        for cat, key in categories.items():
            if cat in line:
                matched_category = cat
                matched_key = key
                break
        
        if matched_category:
            # Remove category name from line to get just numbers
            line_without_cat = line.replace(matched_category, '', 1).strip()
            
            # Extract all numbers from the line
            numbers = []
            number_patterns = re.findall(r'\d+[.,]?\d*', line_without_cat)
            
            for pattern in number_patterns:
                num = clean_number(pattern)
                if num is not None:
                    numbers.append(num)
            
            # Create row data with expected column mapping
            row_data = {
                "شرح مصارف": matched_category,
                "category_key": matched_key,
                "رقم": None,
                "شمارنده قبلی": None,
                "شمارنده کنونی": None,
                "ضریب": None,
                "مصرف": None,
                "نرخ": None,
                "مبلغ": None
            }
            
            # Map numbers to fields based on expected order
            if len(numbers) >= 1:
                row_data["رقم"] = int(numbers[0]) if numbers[0] == int(numbers[0]) else numbers[0]
            if len(numbers) >= 2:
                row_data["شمارنده قبلی"] = numbers[1]
            if len(numbers) >= 3:
                row_data["شمارنده کنونی"] = numbers[2]
            if len(numbers) >= 4:
                row_data["ضریب"] = int(numbers[3]) if numbers[3] == int(numbers[3]) else numbers[3]
            if len(numbers) >= 5:
                row_data["مصرف"] = numbers[4]
            if len(numbers) >= 6:
                row_data["نرخ"] = numbers[5]
            if len(numbers) >= 7:
                row_data["مبلغ"] = int(numbers[6]) if numbers[6] == int(numbers[6]) else numbers[6]
            
            if numbers:
                result["rows"].append(row_data)
    
    return result


def restructure_consumption_table_template9_json(input_json_path, output_json_path=None):
    """
    Main function to restructure the consumption table section JSON for Template 9.
    
    Args:
        input_json_path: Path to input JSON file
        output_json_path: Path to output JSON file (optional)
    
    Returns:
        Restructured data dictionary
    """
    
    # Read input JSON
    with open(input_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract text content and geometry data
    text = data.get('text', '')
    geometry_data = data.get('geometry', None)
    
    # Parse the table (prefer geometry data if available)
    parsed_data = parse_consumption_table_template9(text, geometry_data)
    
    # Extract meter specifications from the table
    # ضریب کنتور is the same for all rows, so extract from first row
    # For Structure B, the meter coefficient is in col 3 (stored as ضریب in row data)
    # For Structure A, the meter coefficient might be in col 6 (also stored as ضریب)
    # But we need to distinguish between row-level coefficient and meter-level coefficient
    meter_specs = {}
    if parsed_data.get("rows") and len(parsed_data["rows"]) > 0:
        first_row = parsed_data["rows"][0]
        # Check if ضریب is a meter coefficient (typically 2000, 2400, 80000) vs row coefficient (typically 4)
        if "ضریب" in first_row and first_row["ضریب"] is not None:
            coeff_value = first_row["ضریب"]
            # If coefficient is >= 2000, it's likely the meter coefficient
            # If it's 4, it's the row-level coefficient and we need to look elsewhere
            if coeff_value >= 2000:
                meter_specs["ضریب کنتور"] = coeff_value
            # For Structure B, the meter coefficient is already in ضریب
            # For Structure A, we might need to check if there's a separate meter coefficient field
            # Check all rows to see if there's a consistent large coefficient value
            elif coeff_value == 4:
                # This is Structure A, check if we can find meter coefficient from period section or elsewhere
                # For now, we'll leave it as None and let it be extracted from period section
                pass
    
    # Create output structure
    output_data = {
        "consumption_table_section": parsed_data
    }
    
    # Add meter specifications if found
    if meter_specs:
        output_data["مشخصات کنتورها"] = meter_specs
    
    # Save to output file if path provided
    if output_json_path:
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    return output_data


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) > 2 else None
        
        result = restructure_consumption_table_template9_json(input_path, output_path)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("Usage: python restructure_consumption_table_template9.py <input_json> [output_json]")
