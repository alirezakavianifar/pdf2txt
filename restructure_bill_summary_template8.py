"""Restructure bill summary section for Template 8."""
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


def extract_bill_summary(text):
    """Extract bill summary financial items from text.
    
    Returns dict with English keys (for internal mapping).
    """
    normalized_text = convert_persian_digits(text)
    
    result = {
        "consumption_amount": None,
        "power_price": None,
        "power_excess": None,
        "license_expiry_difference": None,
        "subscription_fee": None,
        "fuel_cost": None,
        "supplied_energy_cost": None,
        "article_16_energy_cost": None,
        "regulation_difference": None,
        "off_market_credit": None,
        "renewable_supply_difference": None,
        "period_electricity_cost": None,
        "taxes_and_duties": None,
        "electricity_duties": None,
        "credit": None,
        "thousand_rial_deduction": None
    }
    
    # Patterns to match labels and values - more flexible patterns
    patterns = {
        "consumption_amount": [
            r'مبلغ مصرف[^\d]*(\d+(?:,\d+)*)',
            r'مبلغ مصرف\s*:\s*([\d,]+)',
            r'مبلغ مصرف[:\s]+([\d,]+)'
        ],
        "power_price": [
            r'بهای قدرت[^\d]*(\d+(?:,\d+)*)',
            r'بهای قدرت\s*:\s*([\d,]+)',
            r'بهای قدرت[:\s]+([\d,]+)'
        ],
        "power_excess": [
            r'تجاوز از قدرت[^\d]*(\d+(?:,\d+)*)',
            r'تجاوز از قدرت\s*:\s*([\d,]+)',
            r'تجاوز از قدرت[:\s]+([\d,]+)'
        ],
        "license_expiry_difference": [
            r'تفاوت انقضای اعتبار پروانه[^\d]*(\d+(?:,\d+)*)',
            r'تفاوت انقضای اعتبار پروانه\s*:\s*([\d,]+)',
            r'تفاوت انقضای اعتبار پروانه[:\s]+([\d,]+)'
        ],
        "subscription_fee": [
            r'بهای آبونمان[^\d]*(\d+(?:,\d+)*)',
            r'بهای آبونمان\s*:\s*([\d,]+)',
            r'بهای آبونمان[:\s]+([\d,]+)'
        ],
        "fuel_cost": [
            r'هزینه سوخت نیروگاهی[^\d]*(\d+(?:,\d+)*)',
            r'هزینه سوخت نیروگاهی\s*:\s*([\d,]+)',
            r'هزینه سوخت نیروگاهی[:\s]+([\d,]+)'
        ],
        "supplied_energy_cost": [
            r'بهای انرژی تامین شده[^\d]*(\d+(?:,\d+)*)',
            r'بهای انرژی تامین شده\s*:\s*([\d,]+)',
            r'بهای انرژی تامین شده[:\s]+([\d,]+)'
        ],
        "article_16_energy_cost": [
            r'بهای انرژی ماده\s*۱۶[^\d]*(\d+(?:,\d+)*)',
            r'بهای انرژی ماده\s*16[^\d]*(\d+(?:,\d+)*)',
            r'بهای انرژی ماده ۱۶\s*:\s*([\d,]+)',
            r'بهای انرژی ماده ۱۶[:\s]+([\d,]+)'
        ],
        "regulation_difference": [
            r'مابه التفاوت اجرای مقررات[^\d]*(\d+(?:,\d+)*)',
            r'مابه التفاوت اجرای مقررات\s*:\s*([\d,]+)',
            r'مابه التفاوت اجرای مقررات[:\s]+([\d,]+)'
        ],
        "off_market_credit": [
            r'بستانکاری[^\d-]*خرید خارج بازار[^\d-]*(-?\d+(?:,\d+)*)',
            r'بستانکاری، خرید خارج بازار[^\d-]*(-?\d+(?:,\d+)*)',
            r'بستانکاری، خرید خارج بازار\s*:\s*([-\d,]+)',
            r'بستانکاری، خرید خارج بازار[:\s]+([-\d,]+)'
        ],
        "renewable_supply_difference": [
            r'مابه التفاوت تأمین از تجدیدپذیر[^\d]*(\d+(?:,\d+)*)',
            r'مابه التفاوت تأمین از تجدیدپذیر\s*:\s*([\d,]+)',
            r'مابه التفاوت تأمین از تجدیدپذیر[:\s]+([\d,]+)'
        ],
        "period_electricity_cost": [
            r'بهای برق دوره[^\d]*(\d+(?:,\d+)*)',
            r'بهای برق دوره\s*:\s*([\d,]+)',
            r'بهای برق دوره[:\s]+([\d,]+)'
        ],
        "taxes_and_duties": [
            r'مالیات و عوارض[^\d]*(\d+(?:,\d+)*)',
            r'مالیات و عوارض\s*:\s*([\d,]+)',
            r'مالیات و عوارض[:\s]+([\d,]+)'
        ],
        "electricity_duties": [
            r'عوارض برق[^\d]*(\d+(?:,\d+)*)',
            r'عوارض برق\s*:\s*([\d,]+)',
            r'عوارض برق[:\s]+([\d,]+)'
        ],
        "credit": [
            r'بستانکاری[^\d-]*(-?\d+(?:,\d+)*)',
            r'بستانکاری\s*:\s*([-\d,]+)',
            r'بستانکاری[:\s]+([-\d,]+)'
        ],
        "thousand_rial_deduction": [
            r'کسر هزار ریال[^\d]*(\d+(?:,\d+)*)',
            r'کسر هزار ریال\s*:\s*([\d,]+)',
            r'کسر هزار ریال[:\s]+([\d,]+)'
        ]
    }
    
    for key, pattern_list in patterns.items():
        for pattern in pattern_list:
            match = re.search(pattern, normalized_text)
            if match:
                value_str = match.group(1).strip()
                # Skip if it's just a dot (empty value)
                if value_str != '.' and value_str:
                    # Handle negative values
                    is_negative = value_str.startswith('-')
                    if is_negative:
                        value_str = value_str[1:]
                    value = parse_number(value_str)
                    if value is not None and is_negative:
                        value = -value
                    result[key] = value
                break
    
    return result


def extract_numbers_from_cid_encoded_text(text):
    """Extract numeric values from text with CID codes by position.
    
    When Persian text is corrupted with CID codes, we can still extract
    numbers which appear at the start or end of each line. The order is consistent
    across all bills.
    
    Returns a list of extracted numbers (as strings with commas) in order.
    """
    if not text:
        return []
    
    numbers = []
    lines = text.split('\n')
    
    # Pattern to match numbers (with optional commas) at start or end of line
    # Matches: "432,592,095", "0", "143,481", etc.
    number_at_start = re.compile(r'^(\d+(?:,\d+)*)')
    number_at_end = re.compile(r'(\d+(?:,\d+)*)\s*$')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        number_str = None
        
        # First try to find a number at the start of the line
        match_start = number_at_start.match(line)
        if match_start:
            number_str = match_start.group(1)
        else:
            # If no number at start, try to find one at the end
            match_end = number_at_end.search(line)
            if match_end:
                number_str = match_end.group(1)
            # Also check if the line is just "0" or starts with "0" followed by space/non-digit
            elif line == '0' or (line.startswith('0') and len(line) > 1 and not line[1].isdigit()):
                number_str = '0'
        
        if number_str:
            numbers.append(number_str)
    
    return numbers


def extract_bill_summary_from_structured(data):
    """Extract bill summary financial items from structured JSON data.
    
    Uses Persian field names as keys.
    """
    # Initialize with Persian field names
    result = {
        "مبلغ مصرف": None,
        "بهای قدرت": None,
        "تجاوز از قدرت": None,
        "تفاوت انقضای اعتبار پروانه": None,
        "بهای آبونمان": None,
        "هزینه سوخت نیروگاهی": None,
        "بهای انرژی تامین شده": None,
        "بهای انرژی ماده ۱۶": None,
        "مابه التفاوت اجرای مقررات": None,
        "بستانکاری، خرید خارج بازار": None,
        "مابه التفاوت تأمین از تجدیدپذیر": None,
        "بهای برق دوره": None,
        "مالیات و عوارض": None,
        "عوارض برق": None,
        "بستانکاری": None,
        "کسر هزار ریال": None
    }
    
    # Try to extract from raw text first (more reliable)
    raw_text = data.get('text', '')
    if raw_text:
        # Check if text contains CID codes (indicates corrupted Persian text)
        has_cid_codes = '(cid:' in raw_text
        
        if has_cid_codes:
            # Extract numbers by position when CID codes are present
            numbers = extract_numbers_from_cid_encoded_text(raw_text)
            
            # Field order based on the bill summary structure
            # This order matches the sequence in the PDF text
            # Note: "بدهکاری" and "عوارض برق" are handled separately as they may vary in position
            field_order = [
                "مبلغ مصرف",           # First number
                "بهای قدرت",            # Second number (often 0)
                "تجاوز از قدرت",        # Third number (often 0)
                "تفاوت انقضای اعتبار پروانه",  # Fourth number (often 0)
                "بهای آبونمان",         # Fifth number
                "هزینه سوخت نیروگاهی",  # Sixth number
                "بهای انرژی تامین شده", # Seventh number (often 0)
                "بهای انرژی ماده ۱۶",   # Eighth number (often 0)
                "مابه التفاوت اجرای مقررات",  # Ninth number (often 0)
                "بستانکاری، خرید خارج بازار",  # Tenth number (often 0)
                "مابه التفاوت تأمین از تجدیدپذیر",  # Eleventh number (often 0)
                "بهای برق دوره",       # Twelfth number
                "مالیات و عوارض"       # Thirteenth number
                # Note: "عوارض برق", "بدهکاری", and "کسر هزار ریال" are handled separately below
            ]
            
            # Map numbers to fields by position
            # The standard order is: مبلغ مصرف, بهای قدرت, تجاوز از قدرت, تفاوت انقضای اعتبار پروانه,
            # بهای آبونمان, هزینه سوخت نیروگاهی, بهای انرژی تامین شده, بهای انرژی ماده ۱۶,
            # مابه التفاوت اجرای مقررات, بستانکاری، خرید خارج بازار, مابه التفاوت تأمین از تجدیدپذیر,
            # بهای برق دوره, مالیات و عوارض, [عوارض برق - optional], [بدهکاری - may be separate], کسر هزار ریال
            
            # Map first 13 fields in order (up to "مالیات و عوارض")
            num_idx = 0
            for field in field_order:
                if num_idx < len(numbers):
                    value_str = numbers[num_idx]
                    parsed = parse_number(value_str)
                    if parsed is not None:
                        result[field] = parsed
                    num_idx += 1
                else:
                    break
            
            # Handle remaining numbers which may include: عوارض برق (optional), بدهکاری, کسر هزار ریال
            remaining_numbers = numbers[num_idx:] if num_idx < len(numbers) else []
            
            if remaining_numbers:
                # The last number is always "کسر هزار ریال" (usually small, < 10000)
                if len(remaining_numbers) > 0:
                    last_num = parse_number(remaining_numbers[-1])
                    if last_num is not None and last_num < 10000:
                        result["کسر هزار ریال"] = last_num
                        remaining_numbers = remaining_numbers[:-1]
                
                # The largest remaining number (> 1 billion) is usually "بدهکاری"
                if len(remaining_numbers) > 0:
                    # Find the largest number that's > 1 billion
                    debt_candidates = []
                    for num_str in remaining_numbers:
                        num = parse_number(num_str)
                        if num is not None and num > 1000000000:
                            debt_candidates.append((num, num_str))
                    
                    if debt_candidates:
                        # Use the largest one as "بدهکاری"
                        debt_candidates.sort(reverse=True)
                        result["بدهکاری"] = debt_candidates[0][0]
                        # Remove it from remaining numbers
                        remaining_numbers = [n for n in remaining_numbers if n != debt_candidates[0][1]]
                
                # Any remaining number is likely "عوارض برق" (usually medium-sized, 1M-1B)
                for num_str in remaining_numbers:
                    num = parse_number(num_str)
                    if num is not None:
                        if result.get("عوارض برق") is None:
                            result["عوارض برق"] = num
        else:
            # Normal text extraction using regex patterns
            text_extracted = extract_bill_summary(raw_text)
            # Map English keys to Persian keys
            mapping = {
                "consumption_amount": "مبلغ مصرف",
                "power_price": "بهای قدرت",
                "power_excess": "تجاوز از قدرت",
                "license_expiry_difference": "تفاوت انقضای اعتبار پروانه",
                "subscription_fee": "بهای آبونمان",
                "fuel_cost": "هزینه سوخت نیروگاهی",
                "supplied_energy_cost": "بهای انرژی تامین شده",
                "article_16_energy_cost": "بهای انرژی ماده ۱۶",
                "regulation_difference": "مابه التفاوت اجرای مقررات",
                "off_market_credit": "بستانکاری، خرید خارج بازار",
                "renewable_supply_difference": "مابه التفاوت تأمین از تجدیدپذیر",
                "period_electricity_cost": "بهای برق دوره",
                "taxes_and_duties": "مالیات و عوارض",
                "electricity_duties": "عوارض برق",
                "credit": "بستانکاری",
                "thousand_rial_deduction": "کسر هزار ریال"
            }
            for eng_key, persian_key in mapping.items():
                if text_extracted.get(eng_key) is not None:
                    result[persian_key] = text_extracted[eng_key]
    
    # Check table data for values - this is the most reliable source
    table_data = data.get('table', {})
    rows = table_data.get('rows', [])
    
    # Check row 7 (index 6) which contains the values in the first cell
    if rows and len(rows) > 6:
        row7 = rows[6]
        if row7 and isinstance(row7, list) and len(row7) > 0:
            cell_value = row7[0]
            if cell_value and isinstance(cell_value, str):
                # The cell contains newline-separated values
                # Split by actual newline characters
                all_lines = cell_value.split('\n')
                values = []
                for line in all_lines:
                    stripped = line.strip()
                    if stripped:
                        # Check if line contains numeric characters (digits, commas, minus)
                        # Remove commas and minus, check if remainder is digits
                        cleaned = stripped.replace(',', '').replace('-', '').replace(' ', '')
                        if cleaned and cleaned.isdigit():
                            values.append(stripped)
                
                # If we found enough numeric values, map them to fields
                if len(values) >= 10:
                    field_order = [
                        "مبلغ مصرف", "بهای قدرت", "تجاوز از قدرت", "تفاوت انقضای اعتبار پروانه",
                        "بهای آبونمان", "هزینه سوخت نیروگاهی", "بهای انرژی تامین شده",
                        "بهای انرژی ماده ۱۶", "مابه التفاوت اجرای مقررات",
                        "بستانکاری، خرید خارج بازار", "مابه التفاوت تأمین از تجدیدپذیر",
                        "بهای برق دوره", "مالیات و عوارض", "عوارض برق", "بستانکاری", "کسر هزار ریال"
                    ]
                    
                    # Map values to fields (always use table data - overwrite any text extraction)
                    for i, field in enumerate(field_order):
                        if i < len(values):
                            value_str = values[i].strip()
                            # Handle negative values
                            is_negative = value_str.startswith('-')
                            clean_value = value_str.lstrip('-').strip()
                            parsed = parse_number(clean_value)
                            if parsed is not None:
                                result[field] = -parsed if is_negative else parsed
                            elif clean_value == '0':
                                result[field] = 0
    
    # If table extraction didn't work, try searching all rows for a cell with many newlines
    if not any(v is not None for v in result.values()):
        for row_idx, row in enumerate(rows):
            if row and isinstance(row, list):
                for cell_idx, cell in enumerate(row):
                    if cell and isinstance(cell, str) and '\n' in cell:
                        # Count newlines to see if this might be our data
                        if cell.count('\n') >= 10:
                            all_lines = cell.split('\n')
                            values = []
                            for line in all_lines:
                                stripped = line.strip()
                                if stripped:
                                    cleaned = stripped.replace(',', '').replace('-', '').replace(' ', '')
                                    if cleaned and cleaned.isdigit():
                                        values.append(stripped)
                            
                            if len(values) >= 10:
                                field_order = [
                                    "مبلغ مصرف", "بهای قدرت", "تجاوز از قدرت", "تفاوت انقضای اعتبار پروانه",
                                    "بهای آبونمان", "هزینه سوخت نیروگاهی", "بهای انرژی تامین شده",
                                    "بهای انرژی ماده ۱۶", "مابه التفاوت اجرای مقررات",
                                    "بستانکاری، خرید خارج بازار", "مابه التفاوت تأمین از تجدیدپذیر",
                                    "بهای برق دوره", "مالیات و عوارض", "عوارض برق", "بستانکاری", "کسر هزار ریال"
                                ]
                                
                                for i, field in enumerate(field_order):
                                    if i < len(values):
                                        value_str = values[i].strip()
                                        is_negative = value_str.startswith('-')
                                        clean_value = value_str.lstrip('-').strip()
                                        parsed = parse_number(clean_value)
                                        if parsed is not None:
                                            result[field] = -parsed if is_negative else parsed
                                        elif clean_value == '0':
                                            result[field] = 0
                                break
                if any(v is not None for v in result.values()):
                    break
    
    # Get structured data as fallback
    structured_data = data.get('structured_data', {})
    
    # Extract from energy_charges
    energy_charges = structured_data.get('energy_charges', {})
    charges = energy_charges.get('charges', {})
    if 'supplied_energy_cost' in charges and result["بهای انرژی تامین شده"] is None:
        result["بهای انرژی تامین شده"] = charges['supplied_energy_cost'].get('amount')
    
    # Extract from additional_charges
    additional_charges = structured_data.get('additional_charges', {})
    if 'subscription_fee' in additional_charges and result["بهای آبونمان"] is None:
        result["بهای آبونمان"] = additional_charges['subscription_fee'].get('amount')
    if 'fuel_cost' in additional_charges and result["هزینه سوخت نیروگاهی"] is None:
        result["هزینه سوخت نیروگاهی"] = additional_charges.get('fuel_cost')
    if 'tariff_difference' in additional_charges and result["مابه التفاوت اجرای مقررات"] is None:
        result["مابه التفاوت اجرای مقررات"] = additional_charges.get('tariff_difference')
    
    # Extract from _original_structured cost_breakdown
    original_structured = structured_data.get('_original_structured', {})
    cost_breakdown = original_structured.get('cost_breakdown', {})
    if 'power_cost' in cost_breakdown and result["بهای قدرت"] is None:
        result["بهای قدرت"] = cost_breakdown.get('power_cost')
    if 'subscription_fee' in cost_breakdown and result["بهای آبونمان"] is None:
        result["بهای آبونمان"] = cost_breakdown.get('subscription_fee')
    if 'fuel_cost' in cost_breakdown and result["هزینه سوخت نیروگاهی"] is None:
        result["هزینه سوخت نیروگاهی"] = cost_breakdown.get('fuel_cost')
    if 'tariff_difference' in cost_breakdown and result["مابه التفاوت اجرای مقررات"] is None:
        result["مابه التفاوت اجرای مقررات"] = cost_breakdown.get('tariff_difference')
    if 'supplied_energy_cost' in cost_breakdown and result["بهای انرژی تامین شده"] is None:
        result["بهای انرژی تامین شده"] = cost_breakdown.get('supplied_energy_cost')
    
    # Extract from final_charges
    final_charges = original_structured.get('final_charges', {})
    if 'vat' in final_charges and result["مالیات و عوارض"] is None:
        result["مالیات و عوارض"] = final_charges.get('vat')
    
    return result


def restructure_bill_summary_template8_json(extracted_json_path, output_json_path):
    """Restructure extracted JSON to include bill summary data for Template 8."""
    with open(extracted_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract bill summary from structured data
    summary_data = extract_bill_summary_from_structured(data)
    
    # Build restructured data with Persian section name
    result = {
        "خلاصه صورتحساب": summary_data
    }
    
    # Save restructured JSON
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Restructured bill summary (Template 8) saved to: {output_json_path}")
    extracted_count = sum(1 for v in summary_data.values() if v is not None)
    print(f"Extracted {extracted_count}/{len(summary_data)} summary fields")
    
    # Print extracted values for verification (skip Persian text to avoid encoding issues)
    if extracted_count > 0:
        print(f"\nSuccessfully extracted {extracted_count} fields with values")
    
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python restructure_bill_summary_template8.py <extracted_json_file> [output_json_file]")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file.parent / f"{input_file.stem}_restructured.json"
    
    if not input_file.exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)
    
    restructure_bill_summary_template8_json(input_file, output_file)

