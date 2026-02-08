"""
Restructure bill summary section for Template 9.
This handles the "خلاصه صورتحساب" (Bill Summary) section.

The main challenge is that pdfplumber produces fragmented text.
This script reconstructs the fragmented text by:
1. Collapsing spaces in numbers
2. Collapsing spaces in field names
3. Using fuzzy matching for field name detection
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

from config import default_config
from strip_extractor import extract_bill_summary_strips


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


def collapse_spaced_number(text: str) -> str:
    """
    Collapse space-separated digits into proper numbers.
    
    Examples:
        "2 2 6 , 8 4 8 , 0 3 2" → "226,848,032"
        "1 3 8 , 8 5 3" → "138,853"
    """
    result = text
    
    # Normalize comma spacing first: " , " → ","
    result = re.sub(r'\s*,\s*', ',', result)
    
    # Use limited iterations to prevent infinite loops
    for _ in range(10):
        prev = result
        
        # Handle spaced digits around commas
        result = re.sub(r'(\d)\s+(\d)', r'\1\2', result)
        
        # Stop if no changes were made
        if result == prev:
            break
    
    return result


def parse_decimal_number(text: str) -> Optional[float]:
    """Parse a number from text, handling commas and various separators."""
    if not text:
        return None
    # Remove all common separators
    clean_text = text.replace(',', '').replace('٬', '').replace('،', '').replace(' ', '').strip()
    
    # Handle negative numbers (shown as "123,456-" in Persian)
    is_negative = False
    if clean_text.endswith('-'):
        is_negative = True
        clean_text = clean_text[:-1]
    
    try:
        value = float(clean_text)
        return -value if is_negative else value
    except ValueError:
        return None


def extract_all_numbers(text: str) -> List[Tuple[int, float, str]]:
    """
    Extract all numbers from text with their positions.
    Returns list of (start_position, value, original_text) tuples.
    """
    numbers = []
    
    # First, collapse spaced numbers
    collapsed = collapse_spaced_number(text)
    
    # Pattern for comma-separated numbers (including negative)
    for match in re.finditer(r'\d{1,3}(?:,\d{3})+-?|\d{1,3}(?:,\d{3})+-', collapsed):
        value = parse_decimal_number(match.group(0))
        if value is not None:
            numbers.append((match.start(), value, match.group(0)))
    
    # Pattern for plain large numbers (6+ digits)
    for match in re.finditer(r'\d{6,}', collapsed):
        # Check if this overlaps with already found numbers
        overlaps = any(
            match.start() >= n[0] and match.start() < n[0] + len(n[2])
            for n in numbers
        )
        if not overlaps:
            value = parse_decimal_number(match.group(0))
            if value is not None:
                numbers.append((match.start(), value, match.group(0)))
    
    return sorted(numbers, key=lambda x: x[0])


def remove_cid_codes(text: str) -> str:
    """
    Remove all CID codes from text comprehensively.
    """
    return re.sub(r'\(cid:\d+\)', '', text)


def preprocess_text(text: str) -> str:
    """
    Preprocess extracted text to collapse fragmented numbers and field names.
    """
    # Convert Persian digits
    result = convert_persian_digits(text)
    
    # Remove CID codes for better processing
    result = remove_cid_codes(result)
    
    # Collapse spaced numbers
    result = collapse_spaced_number(result)
    
    return result


def find_field_in_line(line: str, field_patterns: Dict[str, List[str]]) -> Optional[Tuple[str, int, str]]:
    """
    Find which field (if any) is present in the line.
    Returns (field_name, position, matched_pattern) or None.
    """
    # Remove CID codes before pattern matching
    line_clean = remove_cid_codes(line)
    
    for field_name, patterns in field_patterns.items():
        for pattern in patterns:
            match = re.search(pattern, line_clean, re.IGNORECASE)
            if match:
                return (field_name, match.start(), match.group(0))
    return None


def parse_bill_summary_template9(text: str, geometry_data: Optional[Dict] = None, table_data: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Parse the bill summary section for Template 9.
    
    Strategy:
    1. Preprocess text to collapse fragmented numbers
    2. Process line by line
    3. For each line, detect field name and extract the number after it
    4. Handle edge cases like numbers spanning lines
    5. If geometry data available, also try extracting from cell structure
    """
    
    # Preprocess text
    processed_text = preprocess_text(text)
    
    # Initialize result structure
    result = {
        "مبلغ مصرف": None,
        "بهای قدرت": None,
        "تجاوز از قدرت": None,
        "بهای آبونمان": None,
        "هزینه سوخت نیروگاهی": None,
        "مالیات و عوارض": None,
        "عوارض برق": None,
        "بدهکاری": None,
        "بهای انرژی ماده 16": None,
        "بهای انرژی تامین شده": None,
        "ما به التفاوت اجرای مقررات": None,
        "ما به التقاوت تأمین از تجدیدپذیر": None,
        "بستانکاری خرید خارج بازار": None,
        "تقاوت انقضای اعتبار پروانه": None,
        "بهای ترانزیت برق": None,
        "بهای برق دوره": None,
        "مبلغ قابل پرداخت": None,
        "کسر هزار ریال": None,
    }
    
    # Field patterns - ordered by specificity (most specific first)
    field_patterns = {
        "ما به التفاوت اجرای مقررات": [
            r"مابه\s*التفاوت\s*اجرای\s*مقررات",
            r"اجرای\s*مقررات",
        ],
        "ما به التقاوت تأمین از تجدیدپذیر": [
            r"مابه\s*التقاوت\s*تأمین\s*از\s*تجدیدپذیر",
            r"تأمین\s*از\s*تجدیدپذیر",
        ],
        "بستانکاری خرید خارج بازار": [
            r"بستانکاری\s*خرید\s*خارج\s*بازار",
            r"خرید\s*خارج\s*بازار",
        ],
        "تقاوت انقضای اعتبار پروانه": [
            r"تقاوت\s*انقضای\s*اعتبار\s*پروانه",
            r"انقضای\s*اعتبار\s*پروانه",
        ],
        "بهای انرژی ماده 16": [
            r"بهای\s*انرژی\s*ماده\s*16",
            r"ماده\s*16",
        ],
        "بهای انرژی تامین شده": [
            r"بهای\s*انرژی\s*تامین\s*شده",
            r"تامین\s*شده",
        ],
        "مبلغ مصرف": [
            r"مبلغ\s*مصرف",
            r"مبلغ.*مصرف",  # Match even if split
            r"بل.*مصرف",  # Match key characters even if split by CID codes
        ],
        "بهای قدرت": [
            r"بهای\s*قدرت",
            r"بهای.*قدرت",  # Match even if split
            r"های.*قدرت",  # Match without "ب" if fragmented
            r"قدرت.*بهای",  # Match reversed (RTL)
        ],
        "تجاوز از قدرت": [
            r"تجاوز\s*از\s*قدرت",
        ],
        "بهای آبونمان": [
            r"بهای\s*آبونمان",
            r"آبونمان",
            r"آب[^\d]*\d+",  # Match "آب" followed by number (for fragmented text like "آب(cid:198)138,853")
            r"بهای.*آب",  # Match "بهای" and "آب" even if split
        ],
        "هزینه سوخت نیروگاهی": [
            r"هزینه\s*سوخت\s*نیروگاهی",
            r"سوخت\s*نیروگاهی",
            r"سوخت.*نیروگاه",  # Match even if split
            r"ی.*گا.*یر.*خت",  # Match key characters even if split by CID codes
        ],
        "مالیات و عوارض": [
            r"مالیات\s*و\s*عوارض",
            r"مالیات",
            r"ارض.*ع.*یات",  # Match "عوارض" and "مالیات" even if split
            r"یات.*عوارض",  # Match key parts
        ],
        "عوارض برق": [
            r"عوارض\s*برق",
            r"ارض\s*برق",  # Match without "و" (common in fragmented text)
            r"ارض.*برق",  # Match even if split
        ],
        "بهای ترانزیت برق": [
            r"بهای\s*ترانزیت\s*برق",
            r"ترانزیت",
            r"زیت.*برق",  # Match "ترانزیت" and "برق" even if split
        ],
        "بدهکاری": [
            r"بدهکاری",
            r"کاری.*بد",  # Match "بدهکاری" even if reversed or split (RTL layout)
            r"بد.*کاری",  # Match both parts
        ],
        "بهای برق دوره": [
            r"بهای\s*برق\s*دوره",
            r"برق\s*دوره",
            r"ر.*ای.*برق.*د",  # Match "بهای برق دوره" even if heavily fragmented
            r"برق.*دوره",  # Match key parts
            r"ر\s*[^\d]*\d+.*برق",  # Match "برق" with number (for fragmented text)
        ],
        "مبلغ قابل پرداخت": [
            r"مبلغ\s*قابل\s*پرداخت",
            r"قابل\s*پرداخت",
            r"مبلغ.*قابل",  # Match "مبلغ" and "قابل" even if split
            r"قابل.*پرداخت",  # Match "قابل" and "پرداخت" even if split
            r"بل.*قابل.*رداخت",  # Match key characters even if split by CID codes
        ],
        "کسر هزار ریال": [
            r"کسر\s*هزار\s*ریال",
            r"کسر.*هزار",  # Match "کسر" and "هزار" even if split
            r"زار.*ریال",  # Match "هزار" and "ریال" even if split
            r"زار.*ریال.*کسر",  # Match reversed (RTL): "زار ریال ... کسر"
            r"کسر",  # Simple match for "کسر" (number will be nearby)
        ],
    }
    
    # Track which numbers have been used
    used_numbers = set()
    
    # If geometry data is available, try to extract from cells
    if geometry_data and 'cells' in geometry_data:
        # Group cells by row and try to extract field-value pairs
        cells = geometry_data['cells']
        rows_dict = {}
        for cell in cells:
            row_idx = cell.get('row', 0)
            col_idx = cell.get('col', 0)
            cell_text = cell.get('text', '').strip()
            if row_idx not in rows_dict:
                rows_dict[row_idx] = {}
            rows_dict[row_idx][col_idx] = cell_text
        
        # Process cells to find field-value pairs
        # Look for cells with Persian text (field names) and adjacent cells with numbers (values)
        for row_idx in sorted(rows_dict.keys()):
            row_cells = rows_dict[row_idx]
            for col_idx in sorted(row_cells.keys()):
                cell_text = row_cells[col_idx]
                if not cell_text:
                    continue
                
                # Check if this cell contains a field name
                normalized_cell = convert_persian_digits(cell_text)
                normalized_cell = re.sub(r'\(cid:\d+\)', '', normalized_cell)
                
                # Try to match field patterns
                for field_name, patterns in field_patterns.items():
                    if result[field_name] is not None:
                        continue
                    for pattern in patterns:
                        if re.search(pattern, normalized_cell, re.IGNORECASE):
                            # Found field name, look for value in adjacent cells or same cell
                            # Check same cell for numbers
                            numbers = extract_all_numbers(cell_text)
                            if numbers:
                                for _, value, _ in numbers:
                                    if abs(value) >= 1000:
                                        result[field_name] = value
                                        used_numbers.add(value)
                                        break
                            
                            # Check adjacent cells (right/left depending on layout)
                            for adj_col in [col_idx - 1, col_idx + 1]:
                                if adj_col in row_cells:
                                    adj_text = row_cells[adj_col]
                                    numbers = extract_all_numbers(adj_text)
                                    if numbers:
                                        for _, value, _ in numbers:
                                            if value not in used_numbers and abs(value) >= 1000:
                                                result[field_name] = value
                                                used_numbers.add(value)
                                                break
                            break
    
    # Track which numbers have been used
    used_numbers = set()
    
    # If geometry data is available, try to extract from cells first
    if geometry_data and 'cells' in geometry_data:
        # Group cells by row and try to extract field-value pairs
        cells = geometry_data['cells']
        rows_dict = {}
        for cell in cells:
            row_idx = cell.get('row', 0)
            col_idx = cell.get('col', 0)
            cell_text = cell.get('text', '').strip()
            if row_idx not in rows_dict:
                rows_dict[row_idx] = {}
            rows_dict[row_idx][col_idx] = cell_text
        
        # Process cells to find field-value pairs
        # Look for cells with Persian text (field names) and adjacent cells with numbers (values)
        for row_idx in sorted(rows_dict.keys()):
            row_cells = rows_dict[row_idx]
            for col_idx in sorted(row_cells.keys()):
                cell_text = row_cells[col_idx]
                if not cell_text:
                    continue
                
                # Check if this cell contains a field name
                normalized_cell = convert_persian_digits(cell_text)
                normalized_cell = re.sub(r'\(cid:\d+\)', '', normalized_cell)
                
                # Try to match field patterns
                for field_name, patterns in field_patterns.items():
                    if result[field_name] is not None:
                        continue
                    for pattern in patterns:
                        if re.search(pattern, normalized_cell, re.IGNORECASE):
                            # Found field name, look for value in adjacent cells or same cell
                            # Check same cell for numbers
                            numbers = extract_all_numbers(cell_text)
                            if numbers:
                                for _, value, _ in numbers:
                                    if abs(value) >= 1000:
                                        result[field_name] = value
                                        used_numbers.add(value)
                                        break
                            
                            # Check adjacent cells (right/left depending on layout)
                            for adj_col in [col_idx - 1, col_idx + 1]:
                                if adj_col in row_cells:
                                    adj_text = row_cells[adj_col]
                                    numbers = extract_all_numbers(adj_text)
                                    if numbers:
                                        for _, value, _ in numbers:
                                            if value not in used_numbers and abs(value) >= 1000:
                                                result[field_name] = value
                                                used_numbers.add(value)
                                                break
                            break
    
    # Also process table rows and headers which may have cleaner text
    if table_data is None:
        table_data = {}
    table_rows = table_data.get('rows', [])
    table_headers = table_data.get('headers', [])
    
    # Process table headers first (RTL layout: number appears before field name)
    for header in table_headers:
        if isinstance(header, str):
            # Remove CID codes from header before processing
            header_clean = remove_cid_codes(header)
            header_processed = preprocess_text(header_clean)
            header_lines = header_processed.split('\n')
            for line in header_lines:
                line = line.strip()
                if not line:
                    continue
                
                # Extract all numbers from the line first
                numbers = extract_all_numbers(line)
                if not numbers:
                    continue
                
                # Try to find field name in the line
                field_match = find_field_in_line(line, field_patterns)
                if field_match:
                    field_name, field_pos, matched_pattern = field_match
                    # Find the number closest to the field name
                    # In RTL, number usually appears before the field name
                    for _, value, _ in numbers:
                        if value not in used_numbers and abs(value) >= 100:
                            if result[field_name] is None:
                                result[field_name] = value
                                used_numbers.add(value)
                                break
                else:
                    # No field match, but we have numbers - try to match by number value
                    # This handles cases where field name is too fragmented
                    for _, value, _ in numbers:
                        if value not in used_numbers and abs(value) >= 100:
                            # Try to infer field from number value and context
                            # بهای آبونمان is typically 100k-500k
                            if 100000 <= abs(value) <= 500000 and result["بهای آبونمان"] is None:
                                result["بهای آبونمان"] = value
                                used_numbers.add(value)
                            # هزینه سوخت نیروگاهی is typically 1M-100M (but larger than آبونمان)
                            elif 1000000 <= abs(value) <= 100000000 and result["هزینه سوخت نیروگاهی"] is None:
                                result["هزینه سوخت نیروگاهی"] = value
                                used_numbers.add(value)
    
    # Process table rows (contains main summary values)
    for row in table_rows:
        if isinstance(row, list):
            row_text = ' '.join(str(cell) for cell in row)
        else:
            row_text = str(row)
        # Remove CID codes from row before processing
        row_clean = remove_cid_codes(row_text)
        row_processed = preprocess_text(row_clean)
        row_lines = row_processed.split('\n')
        for line in row_lines:
            line = line.strip()
            if not line:
                continue
            
            # Extract all numbers from the line first
            numbers = extract_all_numbers(line)
            if not numbers:
                continue
            
            # Try to find field name in the line
            field_match = find_field_in_line(line, field_patterns)
            if field_match:
                field_name, field_pos, matched_pattern = field_match
                # Find the number closest to the field name
                for _, value, _ in numbers:
                    if value in used_numbers:
                        continue
                    # Special handling for بدهکاری: validate and fix OCR errors
                    if field_name == "بدهکاری":
                        value_str = str(int(abs(value)))
                        if 1000000 <= abs(value) <= 1000000000:
                            if result[field_name] is None:
                                result[field_name] = value
                                used_numbers.add(value)
                                break
                        elif abs(value) > 1000000000 and len(value_str) >= 11:
                            # Fix OCR error: remove last 3 digits
                            fixed_value = int(value_str[:-3])
                            if 1000000 <= fixed_value <= 1000000000:
                                if result[field_name] is None:
                                    result[field_name] = float(fixed_value)
                                    used_numbers.add(value)
                                    used_numbers.add(fixed_value)
                                    break
                    elif field_name == "کسر هزار ریال":
                        # کسر هزار ریال should be very small (100-1000)
                        if 100 <= abs(value) <= 1000:
                            if result[field_name] is None:
                                result[field_name] = value
                                used_numbers.add(value)
                                break
                    elif abs(value) >= 100:
                        if result[field_name] is None:
                            result[field_name] = value
                            used_numbers.add(value)
                            break
            else:
                # No field match - try to match by number value ranges and context
                # This is a fallback for heavily fragmented text
                # Sort numbers by value to process largest first
                sorted_numbers = sorted(numbers, key=lambda x: abs(x[1]), reverse=True)
                for _, value, _ in sorted_numbers:
                    if value in used_numbers:
                        continue
                    if abs(value) < 1000:
                        continue
                    
                    # بدهکاری is typically 1M-100M (8-9 digits), but OCR might add extra digits
                    # Check if value has too many digits (likely OCR error)
                    value_str = str(int(abs(value)))
                    if 1000000 <= abs(value) <= 1000000000 and result["بدهکاری"] is None:
                        # Normal case: 7-9 digits
                        result["بدهکاری"] = value
                        used_numbers.add(value)
                    elif abs(value) > 1000000000 and result["بدهکاری"] is None:
                        # Likely OCR error with extra digits (e.g., "13,150,551,013" should be "13,150,551")
                        # Try to fix by removing last 3-4 digits if they look like a duplicate
                        if len(value_str) >= 11:
                            # Remove last 3-4 digits and check if it's a reasonable value
                            fixed_value = int(value_str[:-3])
                            if 1000000 <= fixed_value <= 1000000000:
                                result["بدهکاری"] = float(fixed_value)
                                used_numbers.add(value)
                                used_numbers.add(fixed_value)
                    # Also check for smaller values that might be بدهکاری
                    elif 10000000 <= abs(value) <= 100000000 and result["بدهکاری"] is None:
                        result["بدهکاری"] = value
                        used_numbers.add(value)
                    # بهای برق دوره is typically 100M-1B (second largest)
                    elif 100000000 <= abs(value) < 1000000000 and result["بهای برق دوره"] is None:
                        result["بهای برق دوره"] = value
                        used_numbers.add(value)
                    # مالیات و عوارض and عوارض برق are both 10M-100M
                    # Match based on which one is missing
                    elif 10000000 <= abs(value) <= 100000000:
                        if result["مالیات و عوارض"] is None:
                            result["مالیات و عوارض"] = value
                            used_numbers.add(value)
                        elif result["عوارض برق"] is None:
                            result["عوارض برق"] = value
                            used_numbers.add(value)
    
    # Split into lines and process main text
    lines = processed_text.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # Find field in this line (CID codes already removed in find_field_in_line)
        field_match = find_field_in_line(line, field_patterns)
        
        if field_match:
            field_name, field_pos, matched_pattern = field_match
            
            # Skip if already found
            if result[field_name] is not None:
                continue
            
            # Get text after the field name
            text_after = line[field_pos + len(matched_pattern):]
            # Also get text before the field name (for RTL layout where number might be before field)
            text_before = line[:field_pos]
            
            # Extract numbers from text after field
            numbers = extract_all_numbers(text_after)
            # Also extract numbers from text before field (for RTL layout)
            numbers_before = extract_all_numbers(text_before)
            # Combine: numbers after have positive offset, numbers before have negative offset
            # Convert numbers_before to have distance from field (negative means before)
            all_numbers = []
            for offset, value, original in numbers:
                all_numbers.append((offset, value, original))  # After field: positive offset
            for offset, value, original in numbers_before:
                # Before field: calculate distance (negative)
                distance = -(len(text_before) - offset)
                all_numbers.append((distance, value, original))
            # Sort by absolute distance (closest to field name first)
            all_numbers = sorted(all_numbers, key=lambda x: abs(x[0]))
            
            if all_numbers:
                for _, value, original in all_numbers:
                    # Skip if number already used
                    if value in used_numbers:
                        continue
                    
                    # Skip very small numbers (likely noise)
                    if abs(value) < 1000:
                        continue
                    
                    # Field-specific validation
                    if field_name == "بهای آبونمان":
                        # Subscription should be relatively small
                        if 10000 <= abs(value) <= 50000000:
                            result[field_name] = value
                            used_numbers.add(value)
                            break
                    elif field_name == "کسر هزار ریال":
                        # کسر هزار ریال should be very small (100-1000)
                        if 100 <= abs(value) <= 1000:
                            result[field_name] = value
                            used_numbers.add(value)
                            break
                    elif field_name in ["ما به التفاوت اجرای مقررات", "ما به التقاوت تأمین از تجدیدپذیر"]:
                        # These should be very large (millions/billions)
                        if abs(value) >= 100000:
                            result[field_name] = value
                            used_numbers.add(value)
                            break
                    else:
                        # General case: accept any reasonable value
                        result[field_name] = value
                        used_numbers.add(value)
                        break
    
    # Second pass: Try to find fields that weren't matched in first pass
    full_text = ' '.join(lines)
    
    for field_name in result:
        if result[field_name] is not None:
            continue
        
        patterns = field_patterns.get(field_name, [])
        for pattern in patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                # Get text around the match (200 chars after)
                start = match.end()
                end = min(start + 200, len(full_text))
                context = full_text[start:end]
                
                numbers = extract_all_numbers(context)
                # Also check text before the match (for RTL layout)
                start_before = max(0, match.start() - 200)
                context_before = full_text[start_before:match.start()]
                numbers_before = extract_all_numbers(context_before)
                # Combine numbers from before and after
                all_context_numbers = numbers + numbers_before
                
                if all_context_numbers:
                    for _, value, _ in all_context_numbers:
                        if value in used_numbers:
                            continue
                        # Allow small values for "کسر هزار ریال"
                        if field_name != "کسر هزار ریال" and abs(value) < 1000:
                            continue
                        
                        # Apply same validation rules
                        if field_name == "بهای آبونمان":
                            if 10000 <= abs(value) <= 50000000:
                                result[field_name] = value
                                used_numbers.add(value)
                                break
                        elif field_name == "کسر هزار ریال":
                            # کسر هزار ریال should be very small (100-1000)
                            if 100 <= abs(value) <= 1000:
                                result[field_name] = value
                                used_numbers.add(value)
                                break
                        elif field_name in ["ما به التفاوت اجرای مقررات", "ما به التقاوت تأمین از تجدیدپذیر"]:
                            if abs(value) >= 100000:
                                result[field_name] = value
                                used_numbers.add(value)
                                break
                        else:
                            result[field_name] = value
                            used_numbers.add(value)
                            break
                break
    
    return result


def restructure_bill_summary_template9_json(input_json_path, output_json_path=None):
    """
    Main function to restructure the bill summary section JSON for Template 9.
    
    Args:
        input_json_path: Path to input JSON file
        output_json_path: Path to output JSON file (optional)
    
    Returns:
        Restructured data dictionary
    """
    
    # Read input JSON
    with open(input_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract text content, geometry data, and table data
    text = data.get('text', '')
    geometry_data = data.get('geometry', None)
    table_data = data.get('table', {})
    
    # Parse the section (prefer geometry data if available)
    parsed_data = parse_bill_summary_template9(text, geometry_data, table_data)
    
    # Create output structure
    output_data = {
        "خلاصه صورتحساب": parsed_data
    }
    
    # Save to output file if path provided
    if output_json_path:
        try:
            with open(output_json_path, 'w', encoding='utf-8', errors='replace') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            try:
                print(f"Restructured data saved to: {output_json_path}")
            except UnicodeEncodeError:
                print("Restructured data saved successfully")
        except Exception as e:
            print(f"Error saving restructured data: {e}")
    
    extracted_count = sum(1 for v in parsed_data.values() if v is not None)
    try:
        print(f"Extracted {extracted_count} fields from bill summary")
    except UnicodeEncodeError:
        print(f"Extracted {extracted_count} fields from bill summary")
    
    return output_data


def restructure_bill_summary_template9_from_pdf(pdf_path: str, output_json_path: Optional[str] = None):
    """
    Extract bill summary directly from the cropped PDF using strip-based extraction.
    """
    strip_cfg = default_config.strip_extraction
    parsed_data = extract_bill_summary_strips(
        pdf_path,
        row_height=strip_cfg.row_height,
        min_strip_height=strip_cfg.min_strip_height,
        x_margin=strip_cfg.x_margin,
        template="template_9",
    )

    output_data = {
        "خلاصه صورتحساب": parsed_data
    }

    if output_json_path:
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"Extracted {len(parsed_data)} fields from bill summary (strip-based)")
    return output_data


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) > 2 else None
        
        result = restructure_bill_summary_template9_json(input_path, output_path)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("Usage: python restructure_bill_summary_template9.py <input_json> [output_json]")
