import json
import re
import sys
from pathlib import Path


def parse_decimal_number(text):
    if not text:
        return None
    # Remove commas and handle Persian decimal separator
    clean_text = text.replace(',', '')
    if '/' in clean_text:
        clean_text = clean_text.replace('/', '.')
    
    try:
        return float(clean_text)
    except ValueError:
        return None

def convert_persian_digits(text):
    persian_digits = '۰۱۲۳۴۵۶۷۸۹'
    english_digits = '0123456789'
    translation_table = str.maketrans(persian_digits, english_digits)
    return text.translate(translation_table)



def restructure_bill_summary_json(input_json_path, output_json_path):
    """
    Restructure the bill summary section JSON.
    """
    try:
        with open(input_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        raw_text = data.get('text', '')
        normalized_text = convert_persian_digits(raw_text)
        table_data = data.get('table', {})
        table_rows = table_data.get('rows', [])
        
        result = {
            "خلاصه صورتحساب": {}
        }
        
        # Define standard keys we want to extract
        # And the substrings (logical) that identify them
        targets = [
            {"key": "بهای انرژی", "patterns": ["بهای انرژی", "به ا ی ا ن ر ژ ی", "بهای", "انرژی"]},
            {"key": "ضررو زیان", "patterns": ["ضررو زیان", "ض رر و ز یا ن", "ضرر", "زیان"]},
            {"key": "آبونمان", "patterns": ["آبونمان", "مبلغ آبونمان"]},
            {"key": "عوارض برق", "patterns": ["عوارض برق", "عوارض"]},
            {"key": "مالیات بر ارزش افزوده", "patterns": ["مالیات بر ارزش افزوده", "ارزش افزوده", "مالیات"]},
            {"key": "هزینه سوخت نیروگاهی", "patterns": ["هزینه سوخت نیروگاهی", "هزینه سوخت"]},
            {"key": "مابه التفاوت اجرای مقررات", "patterns": ["مابه التفاوت اجرای مقررات", "اجرای مقررات", "مقررات"]},
            {"key": "جمع دوره", "patterns": ["جمع دوره"]},
            {"key": "بدهکاری", "patterns": ["بدهکاری", "یراکهدب"]},
            {"key": "کسر هزار ریال", "patterns": ["کسر هزار ریال", "کسر هزار", "لایر رازه رسک"]},
            {"key": "قسط", "patterns": ["قسط"]},
            {"key": "تعدیل دیرکرد بهای برق", "patterns": ["تعدیل دیرکرد", "دیرکرد"]},
            {"key": "بهای انرژی راکتیو", "patterns": ["بهای انرژی راکتیو", "انرژی راکتیو", "راکتیو"]},
            {"key": "بهای فصل", "patterns": ["بهای فصل"]},
            {"key": "وجه التزام", "patterns": ["وجه التزام"]},
            {"key": "مبلغ قابل پرداخت", "patterns": ["مبلغ قابل پرداخت", "قابل پرداخت", "تخادرپ لباق گلبم"]},
            {"key": "مبلغ ماده 3", "patterns": ["ماده 3", "ماده3", "ماده۳", "ماده ۳"]},
            {"key": "مهلت پرداخت", "patterns": ["مهلت پرداخت", "تتللههمم", "تتخخااددررپپ", "تتخخااددررپپ تتللههمم"]},
        ]
        
        # First, try to extract from table structure if available (as fallback)
        # Table format: rows contain [amount, label] - but labels may be garbled
        # Only use table if text extraction fails
        # We'll process table after text extraction to fill in missing values
        
        # Use patterns directly since text is now normalized
        visual_targets = []
        for target in targets:
            # Add patterns to check
            visual_targets.append({"key": target["key"], "v_patterns": target["patterns"]})

        # Process line by line first (most reliable for "number label" format)
        # Format is typically "number label" (number comes first)
        lines = normalized_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            matched_key = None
            used_pattern = None
            
            # Check against all targets
            for item in visual_targets:
                for pattern in item["v_patterns"]:
                    if pattern in line:
                        matched_key = item["key"]
                        used_pattern = pattern
                        break
                if matched_key:
                    break
            
            if matched_key:
                # Format is "number label" - extract number BEFORE the pattern
                pattern_pos = line.find(used_pattern)
                if pattern_pos > 0:
                    # Extract number from before the pattern
                    before_pattern = line[:pattern_pos].strip()
                    # Look for comma-separated number (e.g., "3,516,324")
                    number_match = re.search(r'\d{1,3}(?:,\d{3})+(?:,\d{3})*', before_pattern)
                    if not number_match:
                        # Try fragmented number (e.g., "3 5 1 6 , 3 2 4")
                        number_match = re.search(r'[\d\s]+(?:,\s*[\d\s]+)+', before_pattern)
                    if not number_match:
                         # Try number without commas (e.g. "401") - especially for small values
                        number_match = re.search(r'\d+', before_pattern)
                    
                    if number_match:
                        num_str = number_match.group(0).replace(' ', '').replace(',', '')
                        if num_str and len(num_str) >= 3:  # Valid number (can be small like 7, 359)
                            value = parse_decimal_number(num_str)
                            if value and value >= 0:  # Allow 0 values
                                # Only update if we haven't found it yet
                                if matched_key not in result["خلاصه صورتحساب"]:
                                    result["خلاصه صورتحساب"][matched_key] = value
                            if value and value >= 0:  # Allow 0 values
                                # Only update if we haven't found it yet
                                if matched_key not in result["خلاصه صورتحساب"]:
                                    result["خلاصه صورتحساب"][matched_key] = value
                else:
                    # Pattern is at start, try to find number after pattern (fallback)
                    remaining = line.replace(used_pattern, '').strip()
                    
                    if matched_key == "مهلت پرداخت":
                         # Look for date pattern YYYY/MM/DD
                         date_match = re.search(r'\d{4}/\d{2}/\d{2}', remaining)
                         if date_match and matched_key not in result["خلاصه صورتحساب"]:
                             result["خلاصه صورتحساب"][matched_key] = date_match.group(0)
                    else:
                        number_match = re.search(r'\d{1,3}(?:,\d{3})+', remaining)
                        if not number_match:
                             number_match = re.search(r'\d+', remaining)
                        if number_match:
                            num_str = number_match.group(0).replace(' ', '').replace(',', '')
                            if num_str and len(num_str) >= 3:
                                value = parse_decimal_number(num_str)
                                if value and value >= 0:
                                    if matched_key not in result["خلاصه صورتحساب"]:
                                        result["خلاصه صورتحساب"][matched_key] = value
        
        # Now try table extraction as fallback for any missing values
        # Table format: rows contain [amount, label] - but labels may be garbled
        for row in table_rows:
            if not row or len(row) < 2:
                continue
            
            # Extract number from first cell
            amount_cell = str(row[0]).strip() if len(row) > 0 and row[0] else ""
            
            # Check for date first (for deadline)
            date_match = re.search(r'\d{4}/\d{2}/\d{2}', amount_cell)
            is_date = bool(date_match)
            
            number_match = re.search(r'\d{1,3}(?:,\d{3})+', amount_cell)
            if not number_match and not is_date:
                continue
                
            if is_date:
                value = date_match.group(0)
            else:
                value = parse_decimal_number(number_match.group(0))
                if value is None or value < 0:
                    continue
            
            # Look for label patterns in row cells (check all cells for garbled text)
            row_text = ' '.join(str(cell) for cell in row if cell)
            matched_key = None
            
            for item in targets:
                # Skip if we already have this value from text extraction
                if item["key"] in result["خلاصه صورتحساب"]:
                    continue
                
                # If we found a date, only match keys that expect a date
                if is_date and item["key"] != "مهلت پرداخت":
                    continue
                # If we found a number, skip keys that expect a date
                if not is_date and item["key"] == "مهلت پرداخت":
                    continue
                
                for pattern in item["patterns"]:
                    if pattern in row_text:
                        matched_key = item["key"]
                        break
                if matched_key:
                    break
                
                for pattern in item["patterns"]:
                    if pattern in row_text:
                        matched_key = item["key"]
                        break
                if matched_key:
                    break
            
            # Also try reverse matching - check if value matches expected range for a field
            if not matched_key:
                # Try to match by value ranges and position
                # This is a fallback when text is too garbled
                pass
            
            if matched_key and matched_key not in result["خلاصه صورتحساب"]:
                result["خلاصه صورتحساب"][matched_key] = value

        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        return result

    except Exception as e:
        print(f"Error structuring bill summary: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    if len(sys.argv) > 2:
        restructure_bill_summary_json(sys.argv[1], sys.argv[2])
