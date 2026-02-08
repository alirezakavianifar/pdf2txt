"""Restructure reactive consumption section for Template 5."""
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
        return int(text)
    except ValueError:
        return None


def extract_reactive_consumption(text):
    """Extract reactive consumption and amount from text.
    
    Expected values:
    - مصرف راکتیو: ۵۷,۲۱۰
    - مبلغ راکتیو: (amount)
    """
    normalized_text = convert_persian_digits(text)
    
    result = {
        "مصرف راکتیو": None,
        "مبلغ راکتیو": None
    }
    
    # Extract مصرف راکتیو - try both patterns: number before or after the label
    # Pattern 1: number followed by "مصرف راکتیو" (try this first as it's more common)
    consumption_match = re.search(r'(\d+(?:,\d+)*)\s+مصرف\s+راکتیو', normalized_text)
    if consumption_match:
        result["مصرف راکتیو"] = parse_number(consumption_match.group(1))
    else:
        # Pattern 2: "مصرف راکتیو" followed by number (on same line, not across newlines)
        consumption_match = re.search(r'مصرف\s+راکتیو\s*:?\s*(\d+(?:,\d+)*)', normalized_text, re.MULTILINE)
        if consumption_match:
            # Check if the match is on the same line (not across newlines)
            match_start = consumption_match.start()
            match_end = consumption_match.end()
            line_start = normalized_text.rfind('\n', 0, match_start) + 1
            line_end = normalized_text.find('\n', match_end)
            if line_end == -1:
                line_end = len(normalized_text)
            line_text = normalized_text[line_start:line_end]
            if 'مصرف' in line_text and 'راکتیو' in line_text and consumption_match.group(1) in line_text:
                result["مصرف راکتیو"] = parse_number(consumption_match.group(1))
    
    # Extract مبلغ راکتیو - try both patterns: number before or after the label
    # Pattern 1: "مبلغ راکتیو" followed by number (with space between words)
    amount_match = re.search(r'مبلغ\s+راکتیو\s*:?\s*(\d+(?:,\d+)*)', normalized_text)
    if amount_match:
        result["مبلغ راکتیو"] = parse_number(amount_match.group(1))
    else:
        # Pattern 2: number followed by "مبلغ راکتیو" (with flexible spacing)
        amount_match = re.search(r'(\d+(?:,\d+)*)\s+مبلغ\s+راکتیو', normalized_text)
        if amount_match:
            result["مبلغ راکتیو"] = parse_number(amount_match.group(1))
    
    # Fallback: find numbers in text
    if result["مصرف راکتیو"] is None:
        numbers = re.findall(r'\d+(?:,\d+)*', normalized_text)
        if numbers:
            result["مصرف راکتیو"] = parse_number(numbers[0])
    
    return result


def restructure_reactive_consumption_template5_json(json_path: Path, output_path: Path):
    """Restructure extracted JSON to include reactive consumption data for Template 5."""
    print(f"Restructuring Reactive Consumption (Template 5) from {json_path}...")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        text = data.get('text', '')
        
        # Extract reactive consumption
        reactive_data = extract_reactive_consumption(text)
        
        # Build restructured data
        result = {
            "مصرف راکتیو": reactive_data
        }
        
        # Save restructured JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"  - Saved to {output_path}")
        extracted_count = sum(1 for v in reactive_data.values() if v is not None)
        print(f"  - Extracted {extracted_count}/{len(reactive_data)} reactive consumption fields")
        
        return result
        
    except Exception as e:
        print(f"Error restructuring Reactive Consumption T5: {e}")
        import traceback
        traceback.print_exc()
        return None

