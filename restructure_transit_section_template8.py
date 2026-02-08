"""Restructure transit section for Template 8."""
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
        return None


def extract_numbers_from_cid_encoded_transit_text(text):
    """Extract numeric values from transit section text with CID codes by pattern.
    
    When Persian text is corrupted with CID codes, we can still extract
    numbers which appear in a consistent pattern. The transit section typically has:
    - Transit price: first number (e.g., 165,732,480)
    - Transit period adjustment: second number (e.g., 11,281,342) - not in expected output
    - VAT: third number (e.g., 17,701,382)
    - Debit/Credit: fourth number (e.g., 1,667,659,613)
    - Thousand rial deduction: fifth number, typically small (e.g., 817)
    - Amount payable: last large number (e.g., 1,862,374,000)
    
    Returns a list of parsed integer values in order of appearance.
    """
    if not text:
        return []
    
    normalized_text = convert_persian_digits(text)
    
    # Extract numbers with commas (large financial values like 165,732,480)
    # Pattern matches numbers with at least one comma
    comma_number_pattern = re.compile(r'\b(\d{1,3}(?:,\d{3}){1,})\b')
    numbers = []
    
    for match in comma_number_pattern.finditer(normalized_text):
        num_str = match.group(1)
        num = parse_number(num_str)
        if num is not None:
            numbers.append(num)
    
    # Also extract standalone numbers without commas (for small values like 817 or 0)
    # But exclude numbers that are part of CID codes like "(cid:183)"
    # First, find all CID code positions to exclude
    cid_positions = []
    for cid_match in re.finditer(r'\(cid:\d+\)', normalized_text):
        cid_positions.append((cid_match.start(), cid_match.end()))
    
    # Extract standalone numbers (3-4 digits or single 0)
    # Pattern: number at start of line or after whitespace/newline, not in CID codes
    standalone_pattern = re.compile(r'(?:^|\n|\s)(\d{3,4}|0)(?!,|\d|\))')
    for match in standalone_pattern.finditer(normalized_text):
        # Check if this match is inside a CID code
        match_start = match.start(1)
        match_end = match.end(1)
        is_in_cid = False
        for cid_start, cid_end in cid_positions:
            if cid_start <= match_start < cid_end or cid_start < match_end <= cid_end:
                is_in_cid = True
                break
        
        if is_in_cid:
            continue
        
        num_str = match.group(1)
        # Check if this number is part of a larger comma-separated number
        is_part_of_larger = False
        for existing_num in numbers:
            existing_str = str(existing_num).replace(',', '')
            if existing_str.startswith(num_str) and len(existing_str) > len(num_str):
                is_part_of_larger = True
                break
        
        if not is_part_of_larger:
            num = parse_number(num_str)
            if num is not None:
                # For small numbers (< 10000), add them (like 817, or 0)
                if num < 10000:
                    # For zeros, always add them (they're valid values)
                    # For other numbers, make sure they're not duplicates
                    if num == 0 or num not in numbers:
                        numbers.append(num)
    
    return numbers


def extract_transit_data(text):
    """Extract transit section data from text."""
    normalized_text = convert_persian_digits(text)
    
    result = {
        "transit_price": None,
        "vat": None,
        "debit_credit": None,
        "thousand_rial_deduction": None,
        "amount_payable": None
    }
    
    # Check if text contains CID codes (indicates corrupted Persian text)
    has_cid_codes = '(cid:' in text
    
    if has_cid_codes:
        # Extract numbers by pattern when CID codes are present
        numbers = extract_numbers_from_cid_encoded_transit_text(text)
        
        # The text structure: first line has a header number, then transit values
        # Structure: [header on first line], transit_price, [transit_period_adjustment - skip], VAT, debit_credit, thousand_rial_deduction
        # Amount payable appears separately (often in table row, not in main text)
        
        # Split text by newlines to identify the header
        lines = text.split('\n')
        header_number = None
        if lines and lines[0]:
            # First line might contain just a header number
            first_line_numbers = extract_numbers_from_cid_encoded_transit_text(lines[0])
            if first_line_numbers:
                header_number = first_line_numbers[0]
        
        # Filter out the header number from the main numbers list
        transit_numbers = [n for n in numbers if n != header_number]
        
        # Map numbers to fields by position
        # Structure: transit_price, [transit_period_adjustment - skip], VAT, debit_credit, thousand_rial_deduction
        if len(transit_numbers) >= 1:
            # First number is transit_price
            result["transit_price"] = transit_numbers[0]
        
        if len(transit_numbers) >= 3:
            # Third number is VAT (second is transit period adjustment which we skip)
            result["vat"] = transit_numbers[2]
        
        if len(transit_numbers) >= 4:
            # Fourth number is debit_credit
            result["debit_credit"] = transit_numbers[3]
        
        if len(transit_numbers) >= 5:
            # Fifth number is thousand_rial_deduction (typically small, < 10000)
            if transit_numbers[4] < 10000:
                result["thousand_rial_deduction"] = transit_numbers[4]
        
        # Amount payable is typically in table data, not in main text
        # Will be extracted from table below
    else:
        # Normal text extraction using regex patterns
        patterns = {
            "transit_price": [
                r'بهای ترانزیت برق\s*:\s*([\d,]+)',
                r'بهای ترانزیت برق[:\s]+([\d,]+)',
                r'بهای ترانزیت\s*:\s*([\d,]+)',
                r'بهای ترانزیت[:\s]+([\d,]+)'
            ],
            "vat": [
                r'مالیات بر ارزش افزوده\s*:\s*([\d,]+)',
                r'مالیات بر ارزش افزوده[:\s]+([\d,]+)'
            ],
            "debit_credit": [
                r'بدهکاری\s*/\s*بستانکاری\s*:\s*([\d,]+)',
                r'بدهکاری\s*/\s*بستانکاری[:\s]+([\d,]+)',
                r'بدهکاری\s*:\s*([\d,]+)',
                r'بدهکاری[:\s]+([\d,]+)'
            ],
            "thousand_rial_deduction": [
                r'کسر هزار ریال\s*:\s*([\d,]+)',
                r'کسر هزار ریال[:\s]+([\d,]+)'
            ],
            "amount_payable": [
                r'مبلغ قابل پرداخت\s*:\s*([\d,]+)',
                r'مبلغ قابل پرداخت[:\s]+([\d,]+)'
            ]
        }
        
        for key, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, normalized_text)
                if match:
                    value_str = match.group(1).strip()
                    # Skip if it's just a dot (empty value)
                    if value_str != '.' and value_str:
                        result[key] = parse_number(value_str)
                    break
    
    return result


def restructure_transit_section_template8_json(extracted_json_path, output_json_path):
    """Restructure extracted JSON to include transit section data for Template 8."""
    with open(extracted_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    text = data.get('text', '')
    
    # Extract transit data
    transit_data = extract_transit_data(text)
    
    # If some fields are still missing, try extracting from table data
    # Table structure: numbers in column 0, labels in column 1
    table = data.get('table', {})
    rows = table.get('rows', [])
    
    if rows and len(rows) > 0:
        # First row typically contains the main transit values
        first_row = rows[0]
        if len(first_row) >= 2:
            numbers_text = first_row[0]  # Numbers in first column
            if numbers_text:
                # Extract numbers from the table cell
                table_numbers = extract_numbers_from_cid_encoded_transit_text(numbers_text)
                
                # Map table numbers to fields (same structure as text)
                # Structure: transit_price, [transit_period_adjustment - skip], VAT, debit_credit, thousand_rial_deduction
                # Note: Some files may have fewer values (e.g., only 3 zeros)
                if transit_data.get("transit_price") is None and len(table_numbers) >= 1:
                    transit_data["transit_price"] = table_numbers[0]
                
                # If we have 3 numbers, they might be: transit_price, VAT, debit_credit (no transit period adjustment)
                if len(table_numbers) == 3:
                    if transit_data.get("vat") is None:
                        transit_data["vat"] = table_numbers[1]
                    if transit_data.get("debit_credit") is None:
                        transit_data["debit_credit"] = table_numbers[2]
                else:
                    # Standard structure with transit period adjustment
                    if transit_data.get("vat") is None and len(table_numbers) >= 3:
                        transit_data["vat"] = table_numbers[2]
                    
                    if transit_data.get("debit_credit") is None and len(table_numbers) >= 4:
                        transit_data["debit_credit"] = table_numbers[3]
                    
                    if transit_data.get("thousand_rial_deduction") is None and len(table_numbers) >= 5:
                        if table_numbers[4] < 10000:
                            transit_data["thousand_rial_deduction"] = table_numbers[4]
        
        # Amount payable is typically in a later row (often row 6 or 7)
        # Look for a number in table rows that could be amount_payable
        transit_price_value = transit_data.get("transit_price")
        debit_credit_value = transit_data.get("debit_credit")
        extracted_values = {transit_price_value, debit_credit_value}
        
        for row in rows:
            if len(row) > 0 and row[0]:
                amount_text = row[0]
                amount_numbers = extract_numbers_from_cid_encoded_transit_text(amount_text)
                for num in amount_numbers:
                    # Amount payable can be large (> 1 billion) or 0
                    if num > 1000000000 or (num == 0 and transit_data.get("amount_payable") is None):
                        # Make sure it's different from other extracted values (unless it's 0 and they're also 0)
                        is_different = True
                        if num > 0:  # Only check difference for non-zero values
                            for extracted_val in extracted_values:
                                if extracted_val is not None and extracted_val > 0 and abs(num - extracted_val) < 1000:
                                    is_different = False
                                    break
                        if is_different:
                            if transit_data.get("amount_payable") is None:
                                transit_data["amount_payable"] = num
                                break
                if transit_data.get("amount_payable") is not None:
                    break
    
    # Build restructured data
    result = {
        "transit_section": transit_data
    }
    
    # Save restructured JSON
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Restructured transit section (Template 8) saved to: {output_json_path}")
    print(f"Extracted transit data: {transit_data}")
    
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python restructure_transit_section_template8.py <extracted_json_file> [output_json_file]")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file.parent / f"{input_file.stem}_restructured.json"
    
    if not input_file.exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)
    
    restructure_transit_section_template8_json(input_file, output_file)

