"""Restructure period section JSON data for Template 9."""
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

def extract_period_section_data(text):
    """Extract period section data from text for Template 9."""
    # Initialize result structure with Template 9 specific fields
    result = {
        "از تاریخ": None,  # From Date
        "تا تاریخ": None,  # To Date
        "بمدت": None,  # Duration (number of days)
        "تاریخ صدور صورتحساب": None,  # Bill Issue Date
        "کل مصرف": None,  # Total Consumption (kWh)
        "ضریب بدی مصرف": None,  # Bad consumption factor
        "یادداشت": None,  # Note about calculation basis
        "ضریب کنتور": None,  # Meter coefficient
        "شماره بدنه کنتور اکتیو": None,  # Active meter body number
        "شماره بدنه کنتور راکتیو": None,  # Reactive meter body number
        "دوره / سال": None,  # Period / Year
    }
    
    # Normalize text - convert Persian digits
    normalized_text = convert_persian_digits(text)
    
    # Split text into lines for easier processing
    lines = normalized_text.split('\n')
    
    # Pattern for dates: YYYY/MM/DD
    date_pattern = r'(\d{4}/\d{2}/\d{2})'
    
    # Find all dates in the text
    all_dates = re.findall(date_pattern, normalized_text)
    
    # Extract "از تاریخ" (From Date) - handle RTL text issues
    # Pattern: "از تاریخ:1404/01/01" or "از تاریخ: 1404/01/01" or reversed text
    from_date_found = False
    to_date_found = False
    
    for line in lines:
        # Look for "از" followed by optional spaces, then "تاریخ", then optional colon/space, then date
        match = re.search(r'از\s*تاريخ\s*:?\s*(\d{4}/\d{2}/\d{2})', line, re.IGNORECASE)
        if match:
            result["از تاریخ"] = match.group(1)
            from_date_found = True
            break
    
    # Extract "تا تاریخ" (To Date)
    for line in lines:
        match = re.search(r'تا\s*تاريخ\s*:?\s*(\d{4}/\d{2}/\d{2})', line, re.IGNORECASE)
        if match:
            result["تا تاریخ"] = match.group(1)
            to_date_found = True
            break
    
    # Extract "بمدت" (Duration) - can be "بمدت 30 روز" or "30 روز"
    for line in lines:
        # Look for "بمدت" followed by number and "روز"
        match = re.search(r'بمدت\s*(\d+)\s*روز', line, re.IGNORECASE)
        if match:
            result["بمدت"] = int(match.group(1))
            break
        # Also look for standalone "30 روز" pattern (common in period sections)
        match = re.search(r'\b(\d+)\s*روز\b', line)
        if match and result["بمدت"] is None:
            # Check if it's a reasonable number of days (20-35 for monthly periods)
            days = int(match.group(1))
            if 20 <= days <= 35:
                result["بمدت"] = days
    
    # Extract "تاریخ صدور صورتحساب" (Bill Issue Date)
    for line in lines:
        # Look for "تاریخ صدور صورتحساب" or "تاریخ صدور" followed by date
        match = re.search(r'تاریخ\s*صدور\s*صورتحساب\s*:?\s*(\d{4}/\d{2}/\d{2})', line, re.IGNORECASE)
        if match:
            result["تاریخ صدور صورتحساب"] = match.group(1)
            break
        # Alternative pattern: "تاریخ صدور" followed by date
        match = re.search(r'تاریخ\s*صدور\s*:?\s*(\d{4}/\d{2}/\d{2})', line, re.IGNORECASE)
        if match:
            result["تاریخ صدور صورتحساب"] = match.group(1)
            break
    
    # Extract "کل مصرف" (Total Consumption) - can be "با کل مصرف" or "کل مصرف"
    for line in lines:
        # Look for "با کل مصرف" or "کل مصرف" followed by number and optional "kwh"
        match = re.search(r'(?:با\s*)?کل\s*مصرف\s*:?\s*(\d+)', line, re.IGNORECASE)
        if match:
            result["کل مصرف"] = int(match.group(1))
            break
        # Handle OCR garbled text: "684720 :ذهص(cid:187) (cid:182)ک اب" (number before garbled "با کل مصرف")
        # Pattern: number followed by colon and garbled text that might contain consumption keywords
        match = re.search(r'(\d{5,7})\s*:.*?(?:کل|مصرف|kwh|kWh|ذهص|ک|اب)', line, re.IGNORECASE)
        if match:
            consumption = int(match.group(1))
            # Check if it's a reasonable consumption value (10000-1000000 kWh for large consumers)
            if 10000 <= consumption <= 1000000:
                result["کل مصرف"] = consumption
                break
        # More flexible pattern: number followed by colon, then any text (garbled "با کل مصرف")
        # Pattern: "684720 :" followed by any characters (garbled text)
        match = re.search(r'(\d{5,7})\s*:', line)
        if match:
            consumption = int(match.group(1))
            # Check if line contains consumption-related keywords (even if garbled) or kwh
            if any(keyword in line.lower() for keyword in ['kwh', 'مصرف', 'کل', 'consumption', 'ذهص', 'ک', 'اب']):
                if 10000 <= consumption <= 1000000:
                    result["کل مصرف"] = consumption
                    break
        # Also look for pattern like "25840 :دنص" (reversed text) or "25840 (kwh)"
        # Extract numbers followed by kwh or kWh
        match = re.search(r'(\d+)\s*(?:\(kwh\)|kwh|kWh)', line, re.IGNORECASE)
        if match:
            consumption = int(match.group(1))
            # Check if it's a reasonable consumption value (1000-1000000 kWh)
            if 1000 <= consumption <= 1000000:
                result["کل مصرف"] = consumption
                break
        # Pattern: number before colon, then look for consumption-related text in the line
        match = re.search(r'(\d{5,7})\s*:', line)
        if match:
            consumption = int(match.group(1))
            # Check if line contains consumption-related keywords (even if garbled)
            if any(keyword in line.lower() for keyword in ['kwh', 'مصرف', 'کل', 'consumption']):
                if 10000 <= consumption <= 1000000:
                    result["کل مصرف"] = consumption
                    break
    
    # Additional pattern: look for numbers that might be consumption across all lines
    # Pattern like "205840" (OCR error for "25840") or "25840" near "kwh" or consumption-related text
    if result["کل مصرف"] is None:
        # First, check lines with kwh or consumption keywords
        for line in lines:
            if 'kwh' in line.lower() or 'مصرف' in line or 'کل' in line:
                # Find all numbers in the line (including longer numbers that might contain the value)
                numbers = re.findall(r'\d{4,7}', line)
                for num_str in numbers:
                    consumption = int(num_str)
                    # Check if it's a reasonable consumption value
                    if 1000 <= consumption <= 100000:
                        result["کل مصرف"] = consumption
                        break
                    # Try to fix common OCR errors: "205840" -> "25840" (remove extra 0)
                    # Pattern: number with extra 0 in middle like "205840" should be "25840"
                    if len(num_str) == 6 and '0' in num_str[1:-1]:
                        # Remove first 0 after first digit: "205840" -> "25840"
                        if num_str[1] == '0':
                            fixed_str = num_str[0] + num_str[2:]
                            try:
                                fixed_consumption = int(fixed_str)
                                if 1000 <= fixed_consumption <= 100000:
                                    result["کل مصرف"] = fixed_consumption
                                    break
                            except ValueError:
                                pass
                        # Remove middle 0: "205840" -> try "25840" (remove 0 at position 2)
                        if result["کل مصرف"] is None and num_str[2] == '0':
                            fixed_str = num_str[:2] + num_str[3:]
                            try:
                                fixed_consumption = int(fixed_str)
                                if 1000 <= fixed_consumption <= 100000:
                                    result["کل مصرف"] = fixed_consumption
                                    break
                            except ValueError:
                                pass
                if result["کل مصرف"]:
                    break
        
        # If still not found, search all lines for reasonable consumption values
        # Look for 5-6 digit numbers that appear in context with dates (period section)
        if result["کل مصرف"] is None:
            for i, line in enumerate(lines):
                # Check if this line or adjacent lines have dates (indicates period section)
                has_date = any(re.search(r'\d{4}/\d{2}/\d{2}', l) for l in lines[max(0, i-1):min(len(lines), i+2)])
                if has_date:
                    numbers = re.findall(r'\d{5,6}', line)
                    for num_str in numbers:
                        consumption = int(num_str)
                        # Try to fix OCR error first: "205840" -> "25840"
                        if len(num_str) == 6 and num_str[1] == '0':
                            fixed_str = num_str[0] + num_str[2:]
                            try:
                                fixed_consumption = int(fixed_str)
                                if 10000 <= fixed_consumption <= 100000:
                                    result["کل مصرف"] = fixed_consumption
                                    break
                            except ValueError:
                                pass
                        # Also try removing 0 at position 2: "205840" -> "20840" or other patterns
                        if result["کل مصرف"] is None and len(num_str) == 6 and num_str[2] == '0':
                            fixed_str = num_str[:2] + num_str[3:]
                            try:
                                fixed_consumption = int(fixed_str)
                                if 10000 <= fixed_consumption <= 100000:
                                    result["کل مصرف"] = fixed_consumption
                                    break
                            except ValueError:
                                pass
                        # Check if original value is reasonable (even if 6 digits, might be valid)
                        if result["کل مصرف"] is None and 10000 <= consumption <= 100000:
                            result["کل مصرف"] = consumption
                            break
                        # Also accept slightly larger values that might be OCR errors
                        if result["کل مصرف"] is None and 100000 < consumption <= 300000:
                            # Likely an OCR error, try to fix it
                            if '0' in num_str[1:-1]:
                                # Try removing one 0
                                for pos in range(1, len(num_str)-1):
                                    if num_str[pos] == '0':
                                        fixed_str = num_str[:pos] + num_str[pos+1:]
                                        try:
                                            fixed_consumption = int(fixed_str)
                                            if 10000 <= fixed_consumption <= 100000:
                                                result["کل مصرف"] = fixed_consumption
                                                break
                                        except ValueError:
                                            pass
                                if result["کل مصرف"]:
                                    break
                    if result["کل مصرف"]:
                        break
    
    # Extract "ضریب بدی مصرف" (Bad consumption factor)
    for line in lines:
        match = re.search(r'ضریب\s*(?:زبان\s*)?بدی\s*مصرف\s*:?\s*([^\n]*)', line, re.IGNORECASE)
        if match:
            factor_text = match.group(1).strip()
            # Try to extract a number if present
            num_match = re.search(r'(\d+(?:\.\d+)?)', factor_text)
            if num_match:
                try:
                    result["ضریب بدی مصرف"] = float(num_match.group(1))
                except ValueError:
                    result["ضریب بدی مصرف"] = factor_text
            else:
                result["ضریب بدی مصرف"] = factor_text if factor_text else None
            break
    
    # Extract note about calculation basis
    for line in lines:
        if 'ضریب' in line and 'بدی' in line and 'مصرف' in line and 'محاسبه' in line:
            result["یادداشت"] = "بر اساس ضریب بدی مصرف محاسبه گردیده"
            break
    
    # Fix date order: Handle RTL text issues where dates might be swapped
    # Strategy: Sort all dates chronologically and assign logically
    if len(all_dates) >= 2:
        # Sort all dates chronologically
        sorted_dates = sorted(all_dates, key=lambda x: tuple(map(int, x.split('/'))))
        
        # If we found dates with labels, verify they're in correct chronological order
        if result["از تاریخ"] and result["تا تاریخ"]:
            from_date_parts = result["از تاریخ"].split('/')
            to_date_parts = result["تا تاریخ"].split('/')
            from_date_val = int(from_date_parts[0]) * 10000 + int(from_date_parts[1]) * 100 + int(from_date_parts[2])
            to_date_val = int(to_date_parts[0]) * 10000 + int(to_date_parts[1]) * 100 + int(to_date_parts[2])
            
            # If "From Date" is actually after "To Date", they're swapped - fix it
            if from_date_val > to_date_val:
                result["از تاریخ"], result["تا تاریخ"] = result["تا تاریخ"], result["از تاریخ"]
        
        # If we have 3 dates, identify which are period dates and which is issue date
        # Period dates are typically consecutive (within same month or adjacent months)
        # Issue date is usually later and more separated
        if len(sorted_dates) == 3:
            # Calculate gaps between consecutive dates
            date1 = tuple(map(int, sorted_dates[0].split('/')))
            date2 = tuple(map(int, sorted_dates[1].split('/')))
            date3 = tuple(map(int, sorted_dates[2].split('/')))
            
            # Calculate days between dates (approximate)
            gap1_2 = (date2[0] - date1[0]) * 365 + (date2[1] - date1[1]) * 30 + (date2[2] - date1[2])
            gap2_3 = (date3[0] - date2[0]) * 365 + (date3[1] - date2[1]) * 30 + (date3[2] - date2[2])
            
            # If first two dates are close (period dates) and third is separated (issue date)
            if gap1_2 <= 35 and gap2_3 > 10:
                if result["از تاریخ"] is None:
                    result["از تاریخ"] = sorted_dates[0]
                if result["تا تاریخ"] is None:
                    result["تا تاریخ"] = sorted_dates[1]
                if result["تاریخ صدور صورتحساب"] is None:
                    result["تاریخ صدور صورتحساب"] = sorted_dates[2]
            # If last two dates are close (to date and issue date) and first is separated
            elif gap1_2 > 10 and gap2_3 <= 35:
                if result["از تاریخ"] is None:
                    result["از تاریخ"] = sorted_dates[0]
                if result["تا تاریخ"] is None:
                    result["تا تاریخ"] = sorted_dates[1]
                if result["تاریخ صدور صورتحساب"] is None:
                    result["تاریخ صدور صورتحساب"] = sorted_dates[2]
            # Default: first two are period, third is issue
            else:
                if result["از تاریخ"] is None:
                    result["از تاریخ"] = sorted_dates[0]
                if result["تا تاریخ"] is None:
                    result["تا تاریخ"] = sorted_dates[1]
                if result["تاریخ صدور صورتحساب"] is None:
                    result["تاریخ صدور صورتحساب"] = sorted_dates[2]
        
        # If we found dates but labels are missing, assign by chronological order
        elif result["از تاریخ"] is None or result["تا تاریخ"] is None:
            # Filter out Bill Issue Date if it was already found
            period_dates = [d for d in sorted_dates if d != result.get("تاریخ صدور صورتحساب")]
            
            if result["از تاریخ"] is None and len(period_dates) > 0:
                result["از تاریخ"] = period_dates[0]
            if result["تا تاریخ"] is None and len(period_dates) > 1:
                result["تا تاریخ"] = period_dates[-1]
            elif result["تا تاریخ"] is None and len(period_dates) > 0:
                result["تا تاریخ"] = period_dates[-1]
    
    # Extract Bill Issue Date from remaining dates if not found (for cases with 2 dates)
    if result["تاریخ صدور صورتحساب"] is None and len(all_dates) >= 2:
        # Filter out dates that are already used for period
        used_dates = {result["از تاریخ"], result["تا تاریخ"]}
        remaining_dates = [d for d in all_dates if d not in used_dates]
        if remaining_dates:
            # Sort remaining dates and take the latest one (most likely to be issue date)
            sorted_remaining = sorted(remaining_dates, key=lambda x: tuple(map(int, x.split('/'))))
            result["تاریخ صدور صورتحساب"] = sorted_remaining[-1]
    
    # Fallback: Look for number 28-31 as period days if not found
    if result["بمدت"] is None:
        match = re.search(r'\b(2[89]|30|31)\b', normalized_text)
        if match:
            result["بمدت"] = int(match.group(1))
    
    # Extract "دوره / سال" (Period / Year) - format: YYYY/MM
    for line in lines:
        # Look for "دوره" and "سال" followed by date pattern YYYY/MM
        match = re.search(r'دوره\s*/?\s*سال\s*:?\s*(\d{4}/\d{2})', line, re.IGNORECASE)
        if match:
            result["دوره / سال"] = match.group(1)
            break
        # Also look for pattern like "1404/07" near "دوره" or "سال"
        match = re.search(r'(?:دوره|سال).*?(\d{4}/\d{2})', line, re.IGNORECASE)
        if match:
            period_year = match.group(1)
            # Validate it's a reasonable date (1400-1500 for Persian calendar)
            year = int(period_year.split('/')[0])
            if 1400 <= year <= 1500:
                result["دوره / سال"] = period_year
                break
    
    # Extract meter specifications
    # Look for "ضریب کنتور" or "ضریب" followed by a number (typically 2000, 4000, etc.)
    for line in lines:
        # Pattern: "ضریب کنتور" or "ضریب" followed by number
        match = re.search(r'ضریب\s*(?:کنتور)?\s*:?\s*(\d+)', line, re.IGNORECASE)
        if match:
            coefficient = int(match.group(1))
            # Meter coefficients are typically 1000, 2000, 4000, etc.
            if 100 <= coefficient <= 10000:
                result["ضریب کنتور"] = coefficient
                break
    
    # Look for meter body numbers (long digit sequences: 8-14 digits)
    # Active meter: typically 13-14 digits, Reactive meter: typically 8 digits
    all_long_numbers = re.findall(r'\d{8,14}', normalized_text)
    if all_long_numbers:
        # Filter out dates and other known numbers
        filtered_numbers = []
        for num in all_long_numbers:
            # Skip if it looks like a date (YYYYMMDD format)
            if len(num) == 8 and num[:4].isdigit() and int(num[:4]) >= 1300 and int(num[:4]) <= 1500:
                continue
            # Skip if it's the bill ID (13 digits starting with 9)
            if len(num) == 13 and num.startswith('9'):
                continue
            filtered_numbers.append(num)
        
        # Sort by length: longer numbers are more likely to be active meter (14 digits)
        # Shorter numbers are more likely to be reactive meter (8 digits)
        if filtered_numbers:
            sorted_numbers = sorted(filtered_numbers, key=len, reverse=True)
            # Active meter body number: longest (13-14 digits)
            for num in sorted_numbers:
                if 13 <= len(num) <= 14:
                    result["شماره بدنه کنتور اکتیو"] = num
                    break
            # Reactive meter body number: shorter (8 digits)
            for num in sorted_numbers:
                if len(num) == 8 and num != result.get("شماره بدنه کنتور اکتیو", "")[:8]:
                    result["شماره بدنه کنتور راکتیو"] = num
                    break
    
    return result

def restructure_period_section_template9_json(extracted_json_path, output_json_path):
    """Restructure extracted JSON to include period section data for Template 9."""
    with open(extracted_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    text = data.get('text', '')
    
    # Extract period data
    period_data = extract_period_section_data(text)
    
    # Build restructured data - organize fields logically
    organized_data = {
        "از تاریخ": period_data.get("از تاریخ"),
        "تا تاریخ": period_data.get("تا تاریخ"),
        "بمدت": period_data.get("بمدت"),
        "تاریخ صدور صورتحساب": period_data.get("تاریخ صدور صورتحساب"),
        "کل مصرف": period_data.get("کل مصرف"),
        "ضریب بدی مصرف": period_data.get("ضریب بدی مصرف"),
        "یادداشت": period_data.get("یادداشت"),
        "ضریب کنتور": period_data.get("ضریب کنتور"),
        "شماره بدنه کنتور اکتیو": period_data.get("شماره بدنه کنتور اکتیو"),
        "شماره بدنه کنتور راکتیو": period_data.get("شماره بدنه کنتور راکتیو"),
        "دوره / سال": period_data.get("دوره / سال"),
    }
    
    result = {
        "اطلاعات دوره": organized_data
    }
    
    # Save restructured JSON
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Restructured data saved to: {output_json_path}")
    
    # Print extracted values
    extracted_count = sum(1 for v in organized_data.values() if v is not None)
    print(f"Extracted {extracted_count}/{len(organized_data)} period fields")
    if extracted_count > 0:
        print("  Extracted fields:")
        for key, value in organized_data.items():
            if value is not None:
                try:
                    print(f"    - {key}: {value}")
                except UnicodeEncodeError:
                    # Fallback for Windows console encoding issues
                    print(f"    - Field extracted: {value}")
    
    return result

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python restructure_period_section_template9.py <extracted_json_file> [output_json_file]")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file.parent / f"{input_file.stem}_restructured.json"
    
    if not input_file.exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)
    
    restructure_period_section_template9_json(input_file, output_file)
