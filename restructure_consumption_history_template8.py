"""Restructure consumption history section for Template 8."""
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
    if not text or text == '.':
        return None
    
    text = convert_persian_digits(text)
    # Remove commas used as thousand separators
    text = text.replace(',', '')
    
    try:
        return int(text)
    except ValueError:
        return None


def extract_consumption_history(text):
    """Extract consumption history table data from text."""
    normalized_text = convert_persian_digits(text)
    
    result = {
        "historical_periods": []
    }
    
    # Split into lines
    lines = [line.strip() for line in normalized_text.split('\n') if line.strip()]
    
    # Look for table rows - each row should have period, reading date, and consumption values
    # Pattern: period (YYYY/MM) followed by reading date (YY/MM/DD) followed by numbers
    period_pattern = r'(\d{4}/\d{2})'
    date_pattern = r'(\d{2}/\d{2}/\d{2})'
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Look for period pattern
        period_match = re.search(period_pattern, line)
        if period_match:
            period = period_match.group(1)
            
            # Look for reading date in same line or next line
            date_match = re.search(date_pattern, line)
            if not date_match and i + 1 < len(lines):
                date_match = re.search(date_pattern, lines[i + 1])
            
            reading_date = date_match.group(1) if date_match else None
            
            # Extract numbers from the line(s) - should be consumption values
            # Try to find all numbers in the line
            numbers = re.findall(r'\d+(?:,\d+)*', line)
            if not numbers and i + 1 < len(lines):
                numbers = re.findall(r'\d+(?:,\d+)*', lines[i + 1])
            
            # If we found period and some numbers, try to parse as consumption row
            if numbers:
                # Try to extract values in order: mid_load, peak_load, off_peak_load, friday_peak_load, reactive, period_amount
                # The last number is usually the period amount (largest)
                parsed_numbers = [parse_number(n) for n in numbers if parse_number(n) is not None]
                
                if len(parsed_numbers) >= 3:
                    period_data = {
                        "period": period,
                        "reading_date": reading_date,
                        "mid_load": parsed_numbers[0] if len(parsed_numbers) > 0 else None,
                        "peak_load": parsed_numbers[1] if len(parsed_numbers) > 1 else None,
                        "off_peak_load": parsed_numbers[2] if len(parsed_numbers) > 2 else None,
                        "friday_peak_load": None,  # Usually empty
                        "reactive": parsed_numbers[3] if len(parsed_numbers) > 3 else None,
                        "period_amount": parsed_numbers[-1] if len(parsed_numbers) > 4 else None
                    }
                    
                    # If we have 6+ numbers, assume proper order
                    if len(parsed_numbers) >= 6:
                        period_data = {
                            "period": period,
                            "reading_date": reading_date,
                            "mid_load": parsed_numbers[0],
                            "peak_load": parsed_numbers[1],
                            "off_peak_load": parsed_numbers[2],
                            "friday_peak_load": None,
                            "reactive": parsed_numbers[4],
                            "period_amount": parsed_numbers[5]
                        }
                    
                    result["historical_periods"].append(period_data)
        
        i += 1
    
    return result


def restructure_consumption_history_template8_json(extracted_json_path, output_json_path):
    """Restructure extracted JSON to include consumption history data for Template 8."""
    with open(extracted_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    text = data.get('text', '')
    
    # Extract consumption history
    history_data = extract_consumption_history(text)
    
    # Build restructured data
    result = {
        "consumption_history_section": history_data
    }
    
    # Save restructured JSON
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Restructured consumption history (Template 8) saved to: {output_json_path}")
    print(f"Extracted {len(history_data['historical_periods'])} historical periods")
    
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python restructure_consumption_history_template8.py <extracted_json_file> [output_json_file]")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file.parent / f"{input_file.stem}_restructured.json"
    
    if not input_file.exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)
    
    restructure_consumption_history_template8_json(input_file, output_file)

