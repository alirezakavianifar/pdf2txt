"""Restructure consumption history section for Template 6."""
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
        return int(text)
    except ValueError:
        try:
            return float(text)
        except ValueError:
            return None


def extract_consumption_history_data(text, table_data=None):
    """Extract consumption history table data from text.
    
    Header: سوابق مصارف، مبالغ و پرداخت های مشترک
    Columns: دوره, تاریخ قرائت, مصرف اکتیو, مصرف راکتیو, مبلغ دوره, مبلغ پرداختی, تاریخ پرداخت
    Multiple rows for different periods
    """
    normalized_text = convert_persian_digits(text)
    
    result = {
        "سوابق مصارف، مبالغ و پرداخت های مشترک": {
            "rows": []
        }
    }
    
    # Try to use table data if available
    if table_data and 'rows' in table_data:
        for row in table_data['rows']:
            if len(row) > 0:
                # Skip header row
                if any(keyword in str(row[0]) for keyword in ["دوره", "تاریخ", "مصرف", "مبلغ"]):
                    continue
                
                # Extract period data
                row_data = {
                    "دوره": row[0] if len(row) > 0 else None,
                    "تاریخ قرائت": row[1] if len(row) > 1 else None,
                    "مصرف اکتیو": parse_number(row[2]) if len(row) > 2 else None,
                    "مصرف راکتیو": parse_number(row[3]) if len(row) > 3 else None,
                    "مبلغ دوره": parse_number(row[4]) if len(row) > 4 else None,
                    "مبلغ پرداختی": parse_number(row[5]) if len(row) > 5 else None,
                    "تاریخ پرداخت": row[6] if len(row) > 6 else None
                }
                result["سوابق مصارف، مبالغ و پرداخت های مشترک"]["rows"].append(row_data)
        return result
    
    # Fallback: parse from text
    lines = [line.strip() for line in normalized_text.split('\n') if line.strip()]
    
    # Look for date patterns to identify rows
    date_pattern = r'\d{4}/\d{2}/\d{2}'
    period_pattern = r'\d{2}/\d{2}'  # Period format like "04/04"
    
    current_row = None
    
    for line in lines:
        # Check if line contains period pattern
        if re.search(period_pattern, line):
            if current_row:
                result["سوابق مصارف، مبالغ و پرداخت های مشترک"]["rows"].append(current_row)
            
            # Extract period
            period_match = re.search(r'(\d{2}/\d{2})', line)
            period = period_match.group(1) if period_match else None
            
            # Extract reading date
            date_match = re.search(date_pattern, line)
            reading_date = date_match.group(0) if date_match else None
            
            # Extract numbers (consumption and amounts)
            numbers = re.findall(r'\d+(?:,\d+)*', line)
            parsed_numbers = [parse_number(num) for num in numbers]
            
            current_row = {
                "دوره": period,
                "تاریخ قرائت": reading_date,
                "مصرف اکتیو": parsed_numbers[0] if len(parsed_numbers) > 0 else None,
                "مصرف راکتیو": parsed_numbers[1] if len(parsed_numbers) > 1 else None,
                "مبلغ دوره": parsed_numbers[2] if len(parsed_numbers) > 2 else None,
                "مبلغ پرداختی": parsed_numbers[3] if len(parsed_numbers) > 3 else None,
                "تاریخ پرداخت": None  # May be in next line
            }
    
    # Add last row if exists
    if current_row:
        result["سوابق مصارف، مبالغ و پرداخت های مشترک"]["rows"].append(current_row)
    
    return result


def restructure_consumption_history_template6_json(json_path: Path, output_path: Path):
    """Restructure extracted JSON to include consumption history data for Template 6."""
    print(f"Restructuring Consumption History (Template 6) from {json_path}...")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        text = data.get('text', '')
        table_data = data.get('table', {})
        
        # Extract consumption history data
        history_data = extract_consumption_history_data(text, table_data)
        
        # Build restructured data
        result = history_data
        
        # Save restructured JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"  - Saved to {output_path}")
        row_count = len(history_data["سوابق مصارف، مبالغ و پرداخت های مشترک"]["rows"])
        print(f"  - Extracted {row_count} history rows")
        
        return result
        
    except Exception as e:
        print(f"Error restructuring Consumption History T6: {e}")
        import traceback
        traceback.print_exc()
        return None

