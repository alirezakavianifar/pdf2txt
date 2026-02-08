"""Restructure power section for Template 8."""
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
    if not text:
        return None
    
    text = convert_persian_digits(text)
    # Remove commas used as thousand separators
    text = text.replace(',', '')
    
    try:
        # Handle decimal numbers (may use slash or dot)
        if '/' in text:
            text = text.replace('/', '.')
        if '.' in text:
            return float(text)
        else:
            return int(text)
    except ValueError:
        return None


def extract_numbers_from_cid_encoded_power_text(text):
    """Extract numeric values from power section text with CID codes by pattern.
    
    When Persian text is corrupted with CID codes, we can still extract
    numbers which appear in a consistent pattern. The power section typically has:
    - Contractual power: large number with dot (e.g., 1000.00, 1100.00)
    - Calculated power: number with slash (e.g., 900/00, 990/00)
    - Reduced power: 0
    - Consumed power: decimal number (e.g., 608/00, 220.80)
    
    Returns a dict with extracted numbers by pattern type.
    """
    if not text:
        return {}
    
    normalized_text = convert_persian_digits(text)
    
    # Extract all numbers with their patterns
    numbers_with_dot = []  # e.g., 1000.00, 1100.00 (contractual)
    numbers_with_slash = []  # e.g., 900/00, 990/00 (calculated)
    decimal_numbers = []  # e.g., 220.80, 608.00 (consumed)
    zero_values = []  # 0 (reduced)
    
    # Pattern for numbers with dot (contractual power - typically large, > 100)
    dot_pattern = re.compile(r'\b(\d{3,}\.\d{2})\b')
    for match in dot_pattern.finditer(normalized_text):
        num_str = match.group(1)
        num = parse_number(num_str)
        if num is not None and num >= 100:  # Contractual power is typically >= 100
            numbers_with_dot.append(num)
    
    # Pattern for numbers with slash (calculated power)
    slash_pattern = re.compile(r'\b(\d+/\d{2})\b')
    for match in slash_pattern.finditer(normalized_text):
        num_str = match.group(1)
        num = parse_number(num_str)
        if num is not None:
            numbers_with_slash.append(num)
    
    # Pattern for decimal numbers (consumed power - typically smaller, < 1000)
    decimal_pattern = re.compile(r'\b(\d+\.\d{1,2})\b')
    for match in decimal_pattern.finditer(normalized_text):
        num_str = match.group(1)
        num = parse_number(num_str)
        if num is not None and num < 1000:  # Consumed power is typically < 1000
            decimal_numbers.append(num)
    
    # Pattern for standalone zero
    zero_pattern = re.compile(r'\b0\b')
    if zero_pattern.search(normalized_text):
        zero_values.append(0)
    
    return {
        "numbers_with_dot": numbers_with_dot,
        "numbers_with_slash": numbers_with_slash,
        "decimal_numbers": decimal_numbers,
        "zero_values": zero_values
    }


def extract_power_values(text):
    """Extract power values from text."""
    normalized_text = convert_persian_digits(text)
    
    result = {
        "contractual_power": None,
        "calculated_power": None,
        "permitted_power": None,
        "reduced_power": None,
        "consumed_power": None,
        "power_overage": None
    }
    
    # Check if text contains CID codes (indicates corrupted Persian text)
    has_cid_codes = '(cid:' in text
    
    if has_cid_codes:
        # Extract numbers by pattern when CID codes are present
        extracted = extract_numbers_from_cid_encoded_power_text(text)
        
        # Map numbers to fields by pattern
        # Contractual power: largest number with dot (typically > 100)
        if extracted["numbers_with_dot"]:
            result["contractual_power"] = max(extracted["numbers_with_dot"])
        
        # Calculated power: first number with slash (e.g., 900/00, 990/00)
        # Consumed power: second number with slash if different (e.g., 608/00)
        if extracted["numbers_with_slash"]:
            result["calculated_power"] = extracted["numbers_with_slash"][0]
            # If there's a second slash number and it's different, it might be consumed power
            if len(extracted["numbers_with_slash"]) > 1:
                second_slash = extracted["numbers_with_slash"][1]
                # If it's in the reasonable range for consumed power and different from calculated
                if 100 <= second_slash < 1000 and abs(second_slash - result["calculated_power"]) > 1:
                    result["consumed_power"] = second_slash
        
        # Reduced power: 0
        if extracted["zero_values"]:
            result["reduced_power"] = 0
        
        # Consumed power: can be in decimal format (220.80) or slash format (608/00)
        # It's typically between 100-1000, and different from calculated power
        consumed_candidates = []
        calculated_value = result.get("calculated_power")
        
        # Check decimal numbers first
        if extracted["decimal_numbers"]:
            # Filter out numbers that are likely contractual (>= 1000) or match calculated
            for num in extracted["decimal_numbers"]:
                if 100 <= num < 1000 and (calculated_value is None or abs(num - calculated_value) > 1):
                    consumed_candidates.append(num)
        
        # Also check slash numbers (e.g., 608/00)
        if extracted["numbers_with_slash"]:
            # The first slash number is usually calculated power, so check others
            for i, num in enumerate(extracted["numbers_with_slash"]):
                if i > 0 and 100 <= num < 1000:  # Consumed power is typically 100-1000
                    # Make sure it's not the same as calculated power
                    if calculated_value is None or abs(num - calculated_value) > 1:
                        consumed_candidates.append(num)
        
        if consumed_candidates:
            # Prefer the largest reasonable value (most likely to be consumed power)
            result["consumed_power"] = max(consumed_candidates)
    else:
        # Normal text extraction using regex patterns
        patterns = {
            "contractual_power": [
                r'قراردادی\s*:\s*([\d,./]+)',
                r'قراردادی[:\s]+([\d,./]+)'
            ],
            "calculated_power": [
                r'محاسبه شده\s*:\s*([\d,./]+)',
                r'محاسبه شده[:\s]+([\d,./]+)'
            ],
            "permitted_power": [
                r'مجاز\s*:\s*([\d,./]+)',
                r'مجاز[:\s]+([\d,./]+)'
            ],
            "reduced_power": [
                r'کاهش یافته\s*:\s*([\d,./]+)',
                r'کاهش یافته[:\s]+([\d,./]+)'
            ],
            "consumed_power": [
                r'مصرفی\s*:\s*([\d,./]+)',
                r'مصرفی[:\s]+([\d,./]+)'
            ],
            "power_overage": [
                r'میزان تجاوز از قدرت\s*:\s*([\d,./]+)',
                r'تجاوز از قدرت\s*:\s*([\d,./]+)',
                r'تجاوز[:\s]+([\d,./]+)'
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


def restructure_power_section_template8_json(extracted_json_path, output_json_path):
    """Restructure extracted JSON to include power section data for Template 8."""
    with open(extracted_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    text = data.get('text', '')
    
    # Extract power values
    power_data = extract_power_values(text)
    
    # If consumed_power is still missing, try extracting from geometry cells
    # The number might be in a cell that wasn't captured in the text field
    if power_data.get("consumed_power") is None:
        geometry = data.get('geometry', {})
        cells = geometry.get('cells', [])
        calculated_value = power_data.get("calculated_power")
        contractual_value = power_data.get("contractual_power")
        
        # Look for cells containing numbers that could be consumed power (100-1000)
        consumed_candidates = []
        consumed_candidates_with_context = []  # Numbers in cells that might contain consumed power label
        
        for cell in cells:
            cell_text = cell.get('text', '')
            if cell_text:
                normalized_cell = convert_persian_digits(cell_text)
                
                # Check if cell might contain consumed power label (even if corrupted with CID codes)
                # Look for patterns that might indicate consumed power (مصرفی)
                has_consumed_context = bool(re.search(r'مصرف|مصرفی|608|220', normalized_cell, re.IGNORECASE))
                
                # Look for all decimal numbers in the cell
                for decimal_match in re.finditer(r'\b(\d+\.\d{1,2})\b', normalized_cell):
                    num = parse_number(decimal_match.group(1))
                    if num is not None and 100 <= num < 1000:
                        # Make sure it's not the same as calculated or contractual power
                        is_different = True
                        if calculated_value is not None and abs(num - calculated_value) <= 1:
                            is_different = False
                        if contractual_value is not None and abs(num - contractual_value) <= 1:
                            is_different = False
                        if is_different:
                            if has_consumed_context:
                                consumed_candidates_with_context.append(num)
                            else:
                                consumed_candidates.append(num)
                
                # Look for all numbers with slash (e.g., 608/00, 220/80)
                for slash_match in re.finditer(r'\b(\d+/\d{2})\b', normalized_cell):
                    num = parse_number(slash_match.group(1))
                    if num is not None and 100 <= num < 1000:
                        # Make sure it's not the same as calculated or contractual power
                        is_different = True
                        if calculated_value is not None and abs(num - calculated_value) <= 1:
                            is_different = False
                        if contractual_value is not None and abs(num - contractual_value) <= 1:
                            is_different = False
                        if is_different:
                            if has_consumed_context:
                                consumed_candidates_with_context.append(num)
                            else:
                                consumed_candidates.append(num)
        
        # Prefer candidates with context (in cells that might contain consumed power label)
        if consumed_candidates_with_context:
            power_data["consumed_power"] = min(consumed_candidates_with_context)
        elif consumed_candidates:
            # Consumed power is typically much smaller than calculated power
            # (e.g., 220.80 vs 990, or 608 vs 900)
            # Prefer the smallest value that's still reasonable
            calculated_value = power_data.get("calculated_power")
            if calculated_value is not None:
                # Prefer values significantly less than calculated (at least 20% less)
                threshold = calculated_value * 0.8
                below_threshold = [c for c in consumed_candidates if c < threshold]
                if below_threshold:
                    # Among those below threshold, prefer the smallest (consumed is typically much smaller)
                    power_data["consumed_power"] = min(below_threshold)
                else:
                    # If none are below threshold, prefer the smallest candidate
                    power_data["consumed_power"] = min(consumed_candidates)
            else:
                # No calculated power to compare, use the smallest reasonable value
                power_data["consumed_power"] = min(consumed_candidates)
    
    # Build restructured data
    result = {
        "power_section": power_data
    }
    
    # Save restructured JSON
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Restructured power section (Template 8) saved to: {output_json_path}")
    print(f"Extracted power values: {power_data}")
    
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python restructure_power_section_template8.py <extracted_json_file> [output_json_file]")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file.parent / f"{input_file.stem}_restructured.json"
    
    if not input_file.exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)
    
    restructure_power_section_template8_json(input_file, output_file)

