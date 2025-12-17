"""
Restructure consumption history section for Template 2.
This handles the "سوابق مصرف و مبلغ" (Consumption and Amount History) table.

The table has 12 columns:
1. دوره - سال (Period - Year): e.g., "1-1404"
2. تاریخ قرائت (Reading Date): e.g., "1404/02/01"
3. میان باری (Mid-load): e.g., "28826"
4. اوج باری (Peak-load): e.g., "7184"
5. کم باری (Off-peak): e.g., "14478"
6. اوج بار جمعه (Friday Peak): Always "+"
7. راکتیو (Reactive): e.g., "37204"
8. صورتحساب (Bill Type): Always "انرژی"
9. مبلغ دوره - ریال (Period Amount): e.g., "186,936,811"
10. مهلت پرداخت (Payment Deadline): e.g., "1404/02/12"
11. مبلغ پرداختی - ریال (Paid Amount): e.g., "276,981,000" (only in first row)
12. تاریخ پرداخت (Payment Date): e.g., "1404/02/18" (only in first row)
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


def parse_number(text: str) -> Optional[float]:
    """Parse a number from text, handling commas and converting to float."""
    if not text:
        return None
    # Remove commas and convert Persian digits
    text = convert_persian_digits(text.replace(',', '').replace('،', '').replace(' ', '').strip())
    if not text or text == '-' or text == '.':
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_date(text: str) -> Optional[str]:
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


def parse_period_year(text: str) -> Optional[str]:
    """Parse period-year format like '1-1404' or '1404-1'."""
    if not text:
        return None
    text = convert_persian_digits(text.strip())
    # Match patterns like "1-1404" or "1404-1"
    match = re.match(r'(\d{4})-(\d+)', text)
    if match:
        return f"{match.group(2)}-{match.group(1)}"  # Return as "period-year"
    match = re.match(r'(\d+)-(\d{4})', text)
    if match:
        return f"{match.group(1)}-{match.group(2)}"  # Return as "period-year"
    return None


def parse_consumption_history_template2(text: str) -> List[Dict[str, Any]]:
    """
    Parse the consumption history table for Template 2.
    
    Expected text format:
    دوره - سال تاریخ قرائت میان باری اوج باری کم باری اوج بار جمعه راکتیو صورتحساب مبلغ دوره - ریال مهلت پرداخت مبلغ پرداختی - ریال تاریخ پرداخت
    1404/02/01 28826 7184 14478 0 37204 انرژی 186,936,811 1404/02/12 1-1404
    276,981,000 1404/02/01 28826 7184 14478 0 37204 انرژی 186,936,811 1404/02/12 1404/02/18 1-1404
    ...
    """
    
    # Normalize text - convert Persian digits
    normalized_text = convert_persian_digits(text)
    
    # Split text into lines
    lines = [line.strip() for line in normalized_text.strip().split('\n') if line.strip()]
    
    rows = []
    
    # Process each line
    for line in lines:
        # Skip header line
        if 'دوره' in line and 'سال' in line and 'تاریخ قرائت' in line:
            continue
        
        # Split line into parts
        parts = line.split()
        
        if not parts:
            continue
        
        # Initialize row data
        row_data = {}
        
        # Find all dates, numbers, and special values in the line
        dates = []
        numbers = []
        period_year = None
        bill_type = None
        friday_peak = None
        
        # Process each part
        for i, part in enumerate(parts):
            part = part.strip()
            if not part:
                continue
            
            # Check for period-year format (e.g., "1-1404" or "1404-1")
            period = parse_period_year(part)
            if period:
                period_year = period
                continue
            
            # Check for date
            date = parse_date(part)
            if date:
                dates.append((i, date))  # Store index and date
                continue
            
            # Check for "انرژی" (bill type)
            if part == 'انرژی' or 'انرژی' in part:
                bill_type = 'انرژی'
                continue
            
            # Check for "+" (Friday peak)
            if part == '+' or part == '\\+':
                friday_peak = '+'
                continue
            
            # Check for number
            num = parse_number(part)
            if num is not None:
                numbers.append((i, num, part))  # Store index, number, and original part
        
        # If we have dates and numbers, it's a data row
        if dates and numbers:
            # Sort by position
            dates.sort(key=lambda x: x[0])
            numbers.sort(key=lambda x: x[0])
            
            # Extract dates in order
            date_values = [d[1] for d in dates]
            reading_date = date_values[0] if date_values else None
            payment_deadline = date_values[1] if len(date_values) >= 2 else None
            payment_date = date_values[2] if len(date_values) >= 3 else None
            
            # Find reading date position
            reading_date_pos = dates[0][0] if dates else -1
            
            # Separate numbers by size and position
            paid_amount = None
            period_amount = None
            consumption_nums = []
            
            for pos, num, orig_part in numbers:
                # Paid amount: very large (> 100M) and appears before reading date
                if num > 100000000 and pos < reading_date_pos:
                    paid_amount = num
                # Period amount: large (> 10M) and appears after reading date
                elif num > 10000000 and pos > reading_date_pos:
                    period_amount = num
                # Consumption values: smaller numbers (< 1M) after reading date
                elif num < 1000000 and pos > reading_date_pos:
                    consumption_nums.append(num)
            
            # Consumption values order: میان باری, اوج باری, کم باری, اوج بار جمعه (0), راکتیو
            if len(consumption_nums) >= 5:
                row_data["میان باری"] = consumption_nums[0]
                row_data["اوج باری"] = consumption_nums[1]
                row_data["کم باری"] = consumption_nums[2]
                # consumption_nums[3] is 0 for friday peak, but we display "+"
                row_data["اوج بار جمعه"] = "+"
                row_data["راکتیو"] = consumption_nums[4]
            elif len(consumption_nums) >= 4:
                row_data["میان باری"] = consumption_nums[0]
                row_data["اوج باری"] = consumption_nums[1]
                row_data["کم باری"] = consumption_nums[2]
                row_data["اوج بار جمعه"] = "+"
                row_data["راکتیو"] = consumption_nums[3]
            
            # Set other fields
            row_data["تاریخ قرائت"] = reading_date
            row_data["صورتحساب"] = bill_type if bill_type else "انرژی"
            row_data["مبلغ دوره - ریال"] = period_amount
            row_data["مهلت پرداخت"] = payment_deadline
            row_data["مبلغ پرداختی - ریال"] = paid_amount
            row_data["تاریخ پرداخت"] = payment_date
            row_data["دوره - سال"] = period_year
            
            # Only add row if we have at least a reading date
            if row_data.get("تاریخ قرائت"):
                rows.append(row_data)
    
    return rows


def restructure_consumption_history_template2_json(input_json_path, output_json_path=None):
    """
    Main function to restructure the consumption history section JSON for Template 2.
    
    Args:
        input_json_path: Path to input JSON file
        output_json_path: Path to output JSON file (optional)
    
    Returns:
        Restructured data dictionary
    """
    
    # Read input JSON
    with open(input_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract text content
    text = data.get('text', '')
    
    # Parse the table
    parsed_rows = parse_consumption_history_template2(text)
    
    # Create output structure
    output_data = {
        "سوابق مصرف و مبلغ": parsed_rows
    }
    
    # Save to output file if path provided
    if output_json_path:
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"Restructured data saved to: {output_json_path}")
    print(f"Extracted {len(parsed_rows)} rows from consumption history")
    
    return output_data


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) > 2 else None
        
        result = restructure_consumption_history_template2_json(input_path, output_path)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("Usage: python restructure_consumption_history_template2.py <input_json> [output_json]")
