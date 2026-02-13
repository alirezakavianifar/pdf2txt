import json
import re
import sys

# Labels for bill identifier and payment identifier (RTL may reverse character order)
BILL_LABEL_PATTERNS = [
    r"شناسه\s*قبض",
    r"ضبق\s*هسانش",  # RTL-reversed شناسه قبض
]
PAYMENT_LABEL_PATTERNS = [
    r"شناسه\s*پرداخت",
    r"تخادرپ\s*هسانش",  # RTL-reversed شناسه پرداخت
]


def _extract_by_label(text_normalized: str, patterns: list, digit_pattern: str = r"\d{13}") -> str | None:
    """Extract number adjacent to a label (before or after)."""
    for pat in patterns:
        # Number after label: "شناسه قبض 9002034804120"
        m = re.search(pat + r"\s*(" + digit_pattern + r")", text_normalized)
        if m:
            return m.group(1)
        # Number before label (RTL): "9002034804120 شناسه قبض"
        m = re.search(r"(" + digit_pattern + r")\s*" + pat, text_normalized)
        if m:
            return m.group(1)
    return None


def restructure_bill_identifier_json(input_json_path, output_json_path):
    """
    Restructure the bill identifier section.
    """
    try:
        with open(input_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        raw_text = data.get('text', '')
        identifier = None
        payment_id = None
        
        # Normalize Persian digits
        persian_digits = '۰۱۲۳۴۵۶۷۸۹'
        english_digits = '0123456789'
        translation_table = str.maketrans(persian_digits, english_digits)
        # Collect all text sources for fallback extraction
        all_text_sources = []
        # Add raw text first
        all_text_sources.append(raw_text)
        
        table_data = data.get('table', {})
        table_rows = table_data.get('rows', [])
        if table_rows:
            for row in table_rows:
                if isinstance(row, list) and len(row) > 0:
                    row_text = ' '.join(str(cell) for cell in row)
                    all_text_sources.append(row_text)
        
        table_headers = table_data.get('headers', [])
        if table_headers:
            for header in table_headers:
                all_text_sources.append(str(header))
        
        geometry_data = data.get('geometry', {})
        geometry_numbers = []
        if geometry_data and 'cells' in geometry_data:
            for cell in geometry_data['cells']:
                cell_text = cell.get('text', '').strip()
                if cell_text:
                    all_text_sources.append(cell_text)
                    cell_normalized = cell_text.translate(translation_table)
                    cell_numbers = re.findall(r'\d{11,13}', cell_normalized)
                    geometry_numbers.extend(cell_numbers)
        
        combined_text = ' '.join(all_text_sources)
        text_normalized = combined_text.translate(translation_table)
        
        # PRIORITY 1: Extract from COMBINED text using label association
        # This covers cases where ID and Label are in the table
        bill_from_raw = _extract_by_label(text_normalized, BILL_LABEL_PATTERNS, r"\d{13}")
        payment_from_raw = _extract_by_label(text_normalized, PAYMENT_LABEL_PATTERNS, r"\d{6,15}")
        
        if bill_from_raw:
            identifier = bill_from_raw
        if payment_from_raw:
            payment_id = payment_from_raw
        
        text_clean = text_normalized.replace(' ', '').replace('\n', '').replace(':', '').replace('(', '').replace(')', '').replace('(cid:', '').replace(')', '')
        
        # Extract bill ID (13 digits) - use label-based result if found, else fallback
        if not identifier:
            bill_id_matches = re.findall(r'\d{13}', text_clean)
            if bill_id_matches:
                identifier = bill_id_matches[0]
            else:
                # Fallback: find sequences that are 8-13 digits long
                all_matches = re.findall(r'\d{8,13}', text_clean)
                if all_matches:
                    thirteen_digit = [m for m in all_matches if len(m) == 13]
                    if thirteen_digit:
                        identifier = thirteen_digit[0]
                    else:
                        valid_matches = [m for m in all_matches if 8 <= len(m) <= 13]
                        if valid_matches:
                            identifier = max(valid_matches, key=len)
        
        # If labels didn't work well (e.g. payment_id caught the bill_id), reset and use heuristics
        if payment_id and identifier and payment_id == identifier:
            payment_id = None

        # Extract payment ID (12 digits) - prioritize numbers from geometry cells (more reliable)
        # First, check geometry_numbers which are extracted separately to avoid concatenation
        if geometry_numbers:
            for num in geometry_numbers:
                if len(num) == 12:
                    if identifier and num != identifier and identifier not in num and num not in identifier:
                        if not payment_id: # Only set if not already found by label
                            payment_id = num
                        break
                elif len(num) == 11 or len(num) == 13:
                    if identifier and num != identifier and identifier not in num and num not in identifier:
                        if not payment_id:  # Use as fallback
                            payment_id = num
        
        # If not found in geometry, check text_clean
        if not payment_id:
            payment_id_matches = re.findall(r'\d{12}', text_clean)
            if payment_id_matches:
                # Filter out any that might be part of the bill ID
                for pid in payment_id_matches:
                    if identifier:
                        # Check if this payment ID is a substring of the bill ID (shouldn't be)
                        if pid in identifier:
                            continue
                        # Check if bill ID contains this payment ID (shouldn't be)
                        if identifier in pid:
                            continue
                    # Payment ID is typically 12 digits and should be a standalone number
                    payment_id = pid
                    break
        
        # If no 12-digit found, try 11-13 digit numbers that aren't the bill ID
        if not payment_id:
            all_long_matches = re.findall(r'\d{11,13}', text_clean)
            # Remove duplicates and sort
            unique_matches = list(set(all_long_matches))
            for match in unique_matches:
                if identifier:
                    # Skip if it's the bill ID
                    if match == identifier:
                        continue
                    # Skip if bill ID is contained in this match or vice versa
                    if identifier in match or match in identifier:
                        continue
                # Prefer 12-digit for payment ID
                if len(match) == 12:
                    payment_id = match
                    break
            # If still no payment ID and we have multiple long numbers, take the first non-bill-ID one
            if not payment_id and len(unique_matches) >= 2:
                for match in unique_matches:
                    if identifier and match != identifier and identifier not in match and match not in identifier:
                        # Prefer 12-digit, but accept 11 or 13 if no 12-digit available
                        if len(match) == 12:
                            payment_id = match
                            break
                # If still no 12-digit, take first non-bill-ID match
                if not payment_id:
                    for match in unique_matches:
                        if identifier and match != identifier and identifier not in match and match not in identifier:
                            payment_id = match
                            break
        
        result = {
            "شناسه قبض": identifier,
            "شناسه پرداخت": payment_id
        }
        
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        return result

    except Exception as e:
        print(f"Error structuring bill identifier: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    if len(sys.argv) > 2:
        restructure_bill_identifier_json(sys.argv[1], sys.argv[2])
