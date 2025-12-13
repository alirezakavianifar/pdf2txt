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
    """Parse a number from text, handling commas and converting to float."""
    if not text:
        return None
    # Remove commas and convert Persian digits
    text = convert_persian_digits(text.replace(',', '').replace('،', ''))
    try:
        return float(text)
    except:
        return None

def parse_date(text):
    """Parse a date in YYYY/MM/DD format."""
    if not text:
        return None
    # Convert Persian digits
    text = convert_persian_digits(text.strip())
    # Match YYYY/MM/DD pattern
    match = re.match(r'(\d{4})/(\d{2})/(\d{2})', text)
    if match:
        return match.group(0)  # Return as string in YYYY/MM/DD format
    return None

def extract_consumption_history_data(text):
    """Extract consumption history data from text."""
    # Normalize text - convert Persian digits
    normalized_text = convert_persian_digits(text)
    
    # Split text into lines
    lines = normalized_text.split('\n')
    
    # Find the table - look for header row or date patterns
    table_rows = []
    in_table = False
    
    # Column headers (from right to left in Persian)
    expected_headers = [
        "تاریخ قرائت",  # Reading Date
        "میان باری",    # Mid-Load
        "اوج باری",     # Peak Load
        "کم باری",      # Off-Peak Load
        "اوج بار جمعه", # Friday Peak Load
        "راکتیو",       # Reactive
        "دیماند",       # Demand
        "مبلغ"          # Amount
    ]
    
    # Process lines to find table data
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Look for date patterns (YYYY/MM/DD) which indicate data rows
        date_match = re.search(r'\d{4}/\d{2}/\d{2}', line)
        if date_match:
            # This is likely a data row
            # Extract all numbers and dates from the line
            # Split by whitespace and process
            parts = re.split(r'\s+', line)
            
            row_data = {}
            dates = []
            numbers = []
            
            # Extract dates and numbers
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                
                # Check if it's a date
                date = parse_date(part)
                if date:
                    dates.append(date)
                else:
                    # Check if it's a number
                    num = parse_number(part)
                    if num is not None:
                        numbers.append(num)
            
            # If we found a date and some numbers, it's a data row
            if dates and numbers:
                # The first date is usually "تاریخ قرائت"
                # Then numbers follow in order: میان باری, اوج باری, کم باری, اوج بار جمعه, راکتیو, دیماند, مبلغ
                row_data["تاریخ قرائت"] = dates[0] if dates else None
                
                # Assign numbers based on their count and typical ranges
                # Usually there are 7 numbers per row
                if len(numbers) >= 7:
                    # Last number is usually "مبلغ" (Amount) - largest value
                    # Second to last is "دیماند" (Demand)
                    # Rest are consumption values
                    row_data["میان باری"] = numbers[0] if len(numbers) >= 1 else None
                    row_data["اوج باری"] = numbers[1] if len(numbers) >= 2 else None
                    row_data["کم باری"] = numbers[2] if len(numbers) >= 3 else None
                    row_data["اوج بار جمعه"] = numbers[3] if len(numbers) >= 4 else None
                    row_data["راکتیو"] = numbers[4] if len(numbers) >= 5 else None
                    row_data["دیماند"] = numbers[5] if len(numbers) >= 6 else None
                    row_data["مبلغ"] = numbers[6] if len(numbers) >= 7 else None
                
                table_rows.append(row_data)
    
    # Alternative approach: use table extraction if text contains table structure
    # Try to extract using pdfplumber table structure if available
    # This is a fallback - we'll rely on the JSON structure from extract_text.py
    
    return table_rows

def extract_consumption_history_from_table(data):
    """Extract consumption history from table structure if available."""
    table_rows = []
    
    # Check if we have table structure
    if 'table' in data and 'rows' in data['table']:
        headers = data['table'].get('headers', [])
        rows = data['table'].get('rows', [])
        
        # Find header indices
        header_map = {}
        for idx, header in enumerate(headers):
            header_text = convert_persian_digits(header).strip()
            # Map headers
            if "تاریخ" in header_text or "قرائت" in header_text:
                header_map["تاریخ قرائت"] = idx
            elif "میان" in header_text and "باری" in header_text:
                header_map["میان باری"] = idx
            elif "اوج" in header_text and "باری" in header_text and "جمعه" not in header_text:
                header_map["اوج باری"] = idx
            elif "کم" in header_text and "باری" in header_text:
                header_map["کم باری"] = idx
            elif "جمعه" in header_text:
                header_map["اوج بار جمعه"] = idx
            elif "راکتیو" in header_text:
                header_map["راکتیو"] = idx
            elif "دیماند" in header_text:
                header_map["دیماند"] = idx
            elif "مبلغ" in header_text:
                header_map["مبلغ"] = idx
        
        # Extract data rows
        for row in rows:
            if not row or len(row) == 0:
                continue
            
            row_data = {}
            
            # Extract date
            if "تاریخ قرائت" in header_map:
                date_val = row[header_map["تاریخ قرائت"]] if header_map["تاریخ قرائت"] < len(row) else None
                row_data["تاریخ قرائت"] = parse_date(str(date_val)) if date_val else None
            
            # Extract numbers
            for key, idx in header_map.items():
                if key != "تاریخ قرائت" and idx < len(row):
                    val = row[idx]
                    if val:
                        row_data[key] = parse_number(str(val))
            
            # Only add if we have at least a date
            if row_data.get("تاریخ قرائت"):
                table_rows.append(row_data)
    
    return table_rows

def restructure_consumption_history_json(extracted_json_path, output_json_path):
    """Restructure extracted JSON to include consumption history data."""
    with open(extracted_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Try table extraction first
    table_rows = extract_consumption_history_from_table(data)
    
    # Fallback to text extraction
    if not table_rows:
        text = data.get('text', '')
        table_rows = extract_consumption_history_data(text)
    
    # Build restructured data
    result = {
        "سوابق مصرف و مبلغ": table_rows
    }
    
    # Save restructured JSON
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Restructured data saved to: {output_json_path}")
    
    # Print extracted values
    print(f"Extracted {len(table_rows)} rows from consumption history")
    
    return result

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python restructure_consumption_history.py <extracted_json_file> [output_json_file]")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file.parent / f"{input_file.stem}_restructured.json"
    
    if not input_file.exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)
    
    restructure_consumption_history_json(input_file, output_file)

