"""Restructure consumption history section JSON data."""
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
    """Parse a number, handling commas."""
    if not text or text.strip() == '':
        return None
    # Remove commas and spaces
    cleaned = text.replace(',', '').replace(' ', '').strip()
    try:
        return float(cleaned)
    except (ValueError, AttributeError):
        return None

def extract_consumption_history_data(text):
    """Extract consumption history data from text."""
    # Normalize text - convert Persian digits
    normalized_text = convert_persian_digits(text)
    
    # Initialize result structure
    result = {
        "سوابق مصرف و مبلغ": []  # Consumption and Amount History
    }
    
    # Split text into lines
    lines = normalized_text.split('\n')
    
    # Pattern for dates: YYYY/MM/DD
    date_pattern = r'(\d{4}/\d{2}/\d{2})'
    
    # Pattern to identify history rows - should have a date followed by multiple numbers
    # Looking for patterns like: "1404/01/01 28790 7740 24889 ..." or "جمع دوره 1404/01/01 ..."
    history_rows = []
    
    for line in lines:
        line = line.strip()
        if not line or len(line) < 10:
            continue
        
        # Skip header lines
        if 'تاریخ قرائت' in line or '-----' in line:
            continue
        
        # Check if line contains a date pattern (may not start with it)
        date_matches = re.findall(date_pattern, line)
        if not date_matches:
            continue
        
        # Get the first date in the line as the reading date
        # For lines with "جمع دوره", the date comes after that phrase
        reading_date = None
        if 'جمع دوره' in line:
            # Find date after "جمع دوره"
            match = re.search(r'جمع دوره\s+(\d{4}/\d{2}/\d{2})', line)
            if match:
                reading_date = match.group(1)
        else:
            # Otherwise, use the first date in the line
            reading_date = date_matches[0]
        
        if not reading_date:
            continue
        
        # Extract all numbers and dates from the line
        parts = line.split()
        
        if len(parts) >= 3:  # At least date + 2 numbers
            # Try to parse as a history row
            row_data = {
                "تاریخ قرائت": reading_date,
                "میان باری": None,  # Mid-peak
                "اوج باری": None,  # Peak
                "کم باری": None,  # Low-peak
                "اوج بار جمع": None,  # Peak weekend
                "راکتیو": None,  # Reactive
                "دیماند": None,  # Demand
                "مبلغ": None,  # Amount
                "شناسه پرداخت": None,  # Payment ID
                "مهلت پرداخت": None,  # Payment deadline
                "تاریخ پرداخت": None,  # Payment date
                "مبلغ پرداخت": None  # Payment amount
            }
            
            # Find position of reading date in the line
            date_pos = line.find(reading_date)
            if date_pos == -1:
                continue
            
            # Extract content after the reading date
            line_after_date = line[date_pos + len(reading_date):].strip()
            
            # Extract all numeric values, dates, and payment IDs in order
            numeric_values = []
            all_dates = re.findall(date_pattern, line_after_date)
            # Payment ID pattern: 2222//0011//11440044 (digits//digits//digits)
            payment_ids = re.findall(r'\d+//\d+//\d+', line_after_date)
            
            # Extract all numbers (including comma-separated)
            number_strings = re.findall(r'[\d,]+(?:\.\d+)?', line_after_date)
            numbers = [parse_number(ns) for ns in number_strings if parse_number(ns) is not None]
            
            # Pattern: mid-peak, peak, low-peak, peak-weekend, reactive, demand, amount, payment_id, payment_deadline, payment_amount
            # Based on sample: "28790 7740 24889 1202 498 132 434516909 2222//0011//11440044 1403/11/13 760962000"
            
            if len(numbers) >= 7:
                row_data["میان باری"] = numbers[0]
                row_data["اوج باری"] = numbers[1]
                row_data["کم باری"] = numbers[2]
                row_data["اوج بار جمع"] = numbers[3]
                row_data["راکتیو"] = numbers[4]
                row_data["دیماند"] = numbers[5]
                row_data["مبلغ"] = numbers[6]
                
                # Payment ID comes after amount
                if payment_ids:
                    row_data["شناسه پرداخت"] = payment_ids[0]
                
                # Payment dates
                if len(all_dates) >= 1:
                    row_data["مهلت پرداخت"] = all_dates[0]
                if len(all_dates) >= 2:
                    row_data["تاریخ پرداخت"] = all_dates[1]
                
                # Payment amount is usually the last number (after the dates)
                if len(numbers) >= 8:
                    row_data["مبلغ پرداخت"] = numbers[-1]
            
            # Only add row if we have at least the reading date
            history_rows.append(row_data)
    
    result["سوابق مصرف و مبلغ"] = history_rows
    
    return result

def restructure_consumption_history_section_json(extracted_json_path, output_json_path):
    """Restructure extracted JSON to include consumption history section data."""
    with open(extracted_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    text = data.get('text', '')
    
    # Extract consumption history data
    history_data = extract_consumption_history_data(text)
    
    # Save restructured JSON
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(history_data, f, ensure_ascii=False, indent=2)
    
    print(f"Restructured data saved to: {output_json_path}")
    
    # Print extracted values
    history_count = len(history_data.get("سوابق مصرف و مبلغ", []))
    print(f"Extracted {history_count} history records")
    
    return history_data

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python restructure_consumption_history_section.py <extracted_json_file> [output_json_file]")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file.parent / f"{input_file.stem}_restructured.json"
    
    if not input_file.exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)
    
    restructure_consumption_history_section_json(input_file, output_file)
