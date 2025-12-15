"""
Restructure bill summary section for Template 2.
This handles the "خلاصه صورتحساب" (Bill Summary) section.

The main challenge is that pdfplumber produces fragmented text like:
  "6 به ا ی ا ن ر ژ ی 2 2 6 , 8 4 8 , 0 3 2"
  
instead of:
  "بهای انرژی 230,848,622"

This script reconstructs the fragmented text by:
1. Collapsing spaces in numbers: "2 2 6 , 8 4 8 , 0 3 2" → "226,848,032"
2. Collapsing spaces in field names: "به ا ی ا ن ر ژ ی" → "بهای انرژی"
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
        "5 7 9 , 0 6 9 , 7 5 3" → "579,069,753"
        "4 2 1 , 19 0 , 7 5 0" → "421,190,750"
    """
    result = text
    
    # Normalize comma spacing first: " , " → ","
    result = re.sub(r'\s*,\s*', ',', result)
    
    # Use limited iterations to prevent infinite loops
    for _ in range(10):
        prev = result
        
        # Handle spaced digits around commas: "2 2 6,8 4 8,0 3 2" → "226,848,032"
        # Only match if there's at least one space
        result = re.sub(r'(\d)\s+(\d)', r'\1\2', result)
        
        # Stop if no changes were made
        if result == prev:
            break
    
    return result


def collapse_spaced_persian(text: str) -> str:
    """
    Collapse space-separated Persian characters into words.
    
    Example:
        "به ا ی ا ن ر ژ ی" → "بهایانرژی" (close enough to match "بهای انرژی")
    """
    # This is tricky because we don't want to collapse ALL spaces
    # We'll use a targeted approach for known fragmented patterns
    
    result = text
    
    # Known fragmented patterns and their collapsed forms
    fragments = [
        (r'به\s+ا\s+ی\s+ا\s+ن\s+ر\s+ژ\s+ی', 'بهای انرژی'),
        (r'ض\s*رر\s+و\s+ز\s*یا\s*ن', 'ضررو زیان'),
        (r'ض\s+رر\s+و\s+ز\s+یا\s+ن', 'ضررو زیان'),
    ]
    
    for pattern, replacement in fragments:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    
    return result


def parse_decimal_number(text: str) -> Optional[float]:
    """Parse a number from text, handling commas and various separators."""
    if not text:
        return None
    # Remove all common separators (comma, Persian comma, space, Arabic comma)
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
    # Matches: 123,456,789 or 123,456,789-
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


def preprocess_text(text: str) -> str:
    """
    Preprocess extracted text to collapse fragmented numbers and field names.
    """
    # Convert Persian digits
    result = convert_persian_digits(text)
    
    # Collapse spaced numbers
    result = collapse_spaced_number(result)
    
    # Collapse known fragmented Persian patterns
    result = collapse_spaced_persian(result)
    
    return result


def find_field_in_line(line: str, field_patterns: Dict[str, List[str]]) -> Optional[Tuple[str, int, str]]:
    """
    Find which field (if any) is present in the line.
    Returns (field_name, position, matched_pattern) or None.
    """
    for field_name, patterns in field_patterns.items():
        for pattern in patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                return (field_name, match.start(), match.group(0))
    return None


def parse_bill_summary_template2(text: str) -> Dict[str, Any]:
    """
    Parse the bill summary section for Template 2.
    
    Strategy:
    1. Preprocess text to collapse fragmented numbers
    2. Process line by line
    3. For each line, detect field name and extract the number after it
    4. Handle edge cases like numbers spanning lines
    """
    
    # Preprocess text
    processed_text = preprocess_text(text)
    
    # Initialize result structure
    result = {
        "بهای انرژی": None,
        "ضررو زیان": None,
        "مبلغ آبونمان": None,
        "هزینه سوخت نیروگاهی": None,
        "مالیات بر ارزش افزوده": None,
        "عوارض برق": None,
        "تجاوز از قدرت": None,
        "مابه التفاوت اجرای مقررات": None,
        "مابه التفاوت ماده 16 جهش تولید": None,
        "بستانکاری خرید خارج بازار": None,
    }
    
    # Field patterns - ordered by specificity (most specific first)
    # Use raw string patterns that match collapsed text
    field_patterns = {
        "مابه التفاوت اجرای مقررات": [
            r"مابه\s*التفاوت\s*اجرای\s*مقررات",
            r"اجرای\s*مقررات",
        ],
        "مابه التفاوت ماده 16 جهش تولید": [
            r"مابه\s*التفاوت\s*ماده\s*16\s*جهش\s*تولید",
            r"ماده\s*16\s*جهش\s*تولید",
        ],
        "بستانکاری خرید خارج بازار": [
            r"بستانکاری\s*خرید\s*خارج\s*بازار",
            r"خرید\s*خارج\s*بازار",
        ],
        "بهای انرژی": [
            r"بهای\s*انرژی",
            r"بهایانرژی",  # Collapsed form
        ],
        "ضررو زیان": [
            r"ضررو\s*زیان",
            r"ضرر\s*و\s*زیان",
        ],
        "مبلغ آبونمان": [
            r"مبلغ\s*آبونمان",
            r"آبونمان",
        ],
        "هزینه سوخت نیروگاهی": [
            r"هزینه\s*سوخت\s*نیروگاهی",
            r"سوخت\s*نیروگاهی",
        ],
        "مالیات بر ارزش افزوده": [
            r"مالیات\s*بر\s*ارزش\s*افزوده",
            r"ارزش\s*افزوده",
        ],
        "عوارض برق": [
            r"عوارض\s*برق",
        ],
        "تجاوز از قدرت": [
            r"تجاوز\s*از\s*قدرت",
        ],
    }
    
    # Track which numbers have been used
    used_numbers = set()
    
    # Split into lines and process
    lines = processed_text.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # Find field in this line
        field_match = find_field_in_line(line, field_patterns)
        
        if field_match:
            field_name, field_pos, matched_pattern = field_match
            
            # Skip if already found
            if result[field_name] is not None:
                continue
            
            # Get text after the field name
            text_after = line[field_pos + len(matched_pattern):]
            
            # Also prepend any leading digits from the line (before field name)
            text_before = line[:field_pos].strip()
            leading_digit = ""
            if re.match(r'^\d+$', text_before):
                leading_digit = text_before
            
            # Check previous line for stray digits
            if i > 0:
                prev_line = lines[i-1].strip()
                if re.match(r'^\d+$', prev_line) and not leading_digit:
                    leading_digit = prev_line
            
            # Extract numbers from text after field
            numbers = extract_all_numbers(text_after)
            
            if numbers:
                for _, value, original in numbers:
                    # Skip if number already used
                    if value in used_numbers:
                        continue
                    
                    # Skip very small numbers (likely noise)
                    if abs(value) < 1000:
                        continue
                    
                    # Field-specific validation
                    if field_name == "مبلغ آبونمان":
                        # Subscription should be relatively small (under 1M typically)
                        if 10000 <= abs(value) <= 50000000:
                            result[field_name] = value
                            used_numbers.add(value)
                            break
                    elif field_name in ["مابه التفاوت اجرای مقررات", "مابه التفاوت ماده 16 جهش تولید"]:
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
    # This handles severely fragmented cases
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
                if numbers:
                    for _, value, _ in numbers:
                        if value in used_numbers:
                            continue
                        if abs(value) < 1000:
                            continue
                        
                        # Apply same validation rules
                        if field_name == "مبلغ آبونمان":
                            if 10000 <= abs(value) <= 50000000:
                                result[field_name] = value
                                used_numbers.add(value)
                                break
                        elif field_name in ["مابه التفاوت اجرای مقررات", "مابه التفاوت ماده 16 جهش تولید"]:
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


def restructure_bill_summary_template2_json(input_json_path, output_json_path=None):
    """
    Main function to restructure the bill summary section JSON for Template 2.
    
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
    
    # Parse the section
    parsed_data = parse_bill_summary_template2(text)
    
    # Remove None values for cleaner output (optional)
    # parsed_data = {k: v for k, v in parsed_data.items() if v is not None}
    
    # Create output structure
    output_data = {
        "خلاصه صورتحساب": parsed_data
    }
    
    # Save to output file if path provided
    if output_json_path:
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"Restructured data saved to: {output_json_path}")
    extracted_count = sum(1 for v in parsed_data.values() if v is not None)
    print(f"Extracted {extracted_count} fields from bill summary")
    
    return output_data


def restructure_bill_summary_template2_from_pdf(pdf_path: str, output_json_path: Optional[str] = None):
    """
    Extract bill summary directly from the cropped PDF using strip-based extraction.
    """
    strip_cfg = default_config.strip_extraction
    parsed_data = extract_bill_summary_strips(
        pdf_path,
        row_height=strip_cfg.row_height,
        min_strip_height=strip_cfg.min_strip_height,
        x_margin=strip_cfg.x_margin,
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
        
        result = restructure_bill_summary_template2_json(input_path, output_path)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("Usage: python restructure_bill_summary_template2.py <input_json> [output_json]")
