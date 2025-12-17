"""Restructure consumption history section for Template 5."""
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
    text = text.replace(',', '').replace(' ', '')
    
    try:
        return int(text)
    except ValueError:
        try:
            return float(text)
        except ValueError:
            return None


def extract_consumption_history_data(text, table_data=None):
    """Extract consumption history table data from text.
    
    Header: سوابق مصارف مبالغ و پرداختهای ادوار گذشته
    Columns: دوره/سال, تاریخ قرائت, مصارف کیلووات ساعت (میان باری, اوج بار, کم باری, اوج بار جمعه, راکتیو), 
             مبلغ دوره ریال, مهلت پرداخت, مبلغ پرداختی, تاریخ پرداخت
    Multiple rows for different periods
    """
    normalized_text = convert_persian_digits(text)
    
    result = {
        "سوابق مصارف مبالغ و پرداختهای ادوار گذشته": {
            "rows": []
        }
    }
    
    # Try to use table data if available
    if table_data and 'rows' in table_data:
        for row in table_data['rows']:
            if len(row) > 0:
                # Skip header row
                if any(keyword in str(row[0]) for keyword in ["دوره", "تاریخ", "مصارف"]):
                    continue
                
                # Extract period data
                row_data = {
                    "دوره/سال": row[0] if len(row) > 0 else None,
                    "تاریخ قرائت": row[1] if len(row) > 1 else None,
                    "مصارف کیلووات ساعت": {
                        "میان باری": parse_number(row[2]) if len(row) > 2 else None,
                        "اوج بار": parse_number(row[3]) if len(row) > 3 else None,
                        "کم باری": parse_number(row[4]) if len(row) > 4 else None,
                        "اوج بار جمعه": parse_number(row[5]) if len(row) > 5 else None,
                        "راکتیو": parse_number(row[6]) if len(row) > 6 else None
                    },
                    "مبلغ دوره ریال": parse_number(row[7]) if len(row) > 7 else None,
                    "مهلت پرداخت": row[8] if len(row) > 8 else None,
                    "مبلغ پرداختی": parse_number(row[9]) if len(row) > 9 else None,
                    "تاریخ پرداخت": row[10] if len(row) > 10 else None
                }
                result["سوابق مصارف مبالغ و پرداختهای ادوار گذشته"]["rows"].append(row_data)
        return result
    
    # Fallback: parse from text
    lines = [line.strip() for line in normalized_text.split('\n') if line.strip()]
    
    # Look for date patterns to identify rows
    date_pattern = r'\d{4}/\d{2}/\d{2}'
    period_pattern = r'\d{4}\s+\d{2}'  # Period format like "1404 07"
    
    current_row = None
    
    for line in lines:
        # Check if line contains period pattern
        if re.search(period_pattern, line):
            if current_row:
                result["سوابق مصارف مبالغ و پرداختهای ادوار گذشته"]["rows"].append(current_row)
            
            # Extract period
            period_match = re.search(r'(\d{4})\s+(\d{2})', line)
            period = f"{period_match.group(1)} {period_match.group(2)}" if period_match else None
            
            # Extract reading date
            date_match = re.search(date_pattern, line)
            reading_date = date_match.group(0) if date_match else None
            
            # Extract consumption values
            numbers = re.findall(r'\d+(?:,\d+)*', line)
            
            current_row = {
                "دوره/سال": period,
                "تاریخ قرائت": reading_date,
                "مصارف کیلووات ساعت": {
                    "میان باری": parse_number(numbers[0]) if len(numbers) > 0 else None,
                    "اوج بار": parse_number(numbers[1]) if len(numbers) > 1 else None,
                    "کم باری": parse_number(numbers[2]) if len(numbers) > 2 else None,
                    "اوج بار جمعه": parse_number(numbers[3]) if len(numbers) > 3 else None,
                    "راکتیو": parse_number(numbers[4]) if len(numbers) > 4 else None
                },
                "مبلغ دوره ریال": None,
                "مهلت پرداخت": None,
                "مبلغ پرداختی": None,
                "تاریخ پرداخت": None
            }
        elif current_row:
            # Continue extracting data for current row
            numbers = re.findall(r'\d+(?:,\d+)*', line)
            dates = re.findall(date_pattern, line)
            
            if not current_row["مبلغ دوره ریال"] and numbers:
                current_row["مبلغ دوره ریال"] = parse_number(numbers[0])
            if not current_row["مهلت پرداخت"] and dates:
                current_row["مهلت پرداخت"] = dates[0]
            if len(numbers) > 1:
                current_row["مبلغ پرداختی"] = parse_number(numbers[-1])
            if len(dates) > 1:
                current_row["تاریخ پرداخت"] = dates[-1]
    
    # Add last row
    if current_row:
        result["سوابق مصارف مبالغ و پرداختهای ادوار گذشته"]["rows"].append(current_row)
    
    return result


def restructure_consumption_history_template5_json(json_path: Path, output_path: Path):
    """Restructure extracted JSON to include consumption history data for Template 5."""
    print(f"Restructuring Consumption History (Template 5) from {json_path}...")
    
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
        row_count = len(history_data['سوابق مصارف مبالغ و پرداختهای ادوار گذشته']['rows'])
        print(f"  - Extracted {row_count} history rows")
        
        return result
        
    except Exception as e:
        print(f"Error restructuring Consumption History T5: {e}")
        import traceback
        traceback.print_exc()
        return None

