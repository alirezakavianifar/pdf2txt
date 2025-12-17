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
            {"key": "بدهکاری", "patterns": ["بدهکاری"]},
            {"key": "کسر هزار ریال", "patterns": ["کسر هزار ریال", "کسر هزار"]},
            {"key": "قسط", "patterns": ["قسط"]},
            {"key": "تعدیل دیرکرد بهای برق", "patterns": ["تعدیل دیرکرد", "دیرکرد"]},
        ]
        
        # Use patterns directly since text is now normalized
        visual_targets = []
        for target in targets:
            # Add patterns to check
            visual_targets.append({"key": target["key"], "v_patterns": target["patterns"]})

        # Handle fragmented text - join all lines first to reconstruct broken words
        # The text might have words split across lines like "8 به ا ی ا ن ر ژ ی" which should be "بهای انرژی"
        full_text = normalized_text.replace('\n', ' ').replace('  ', ' ')
        
        # Also process line by line for non-fragmented cases
        lines = normalized_text.split('\n')
        
        # First, try to extract from full text (handles fragmented cases)
        # Look for patterns that might be split across lines
        for item in visual_targets:
            for pattern in item["v_patterns"]:
                # Check if pattern exists in full text (might be fragmented)
                if pattern in full_text:
                    # Find the pattern and extract number around it (before and after)
                    pattern_pos = full_text.find(pattern)
                    if pattern_pos >= 0:
                        # Look for number before the pattern (might be split, e.g., "8" before "به ا ی ا ن ر ژ ی")
                        before_text = full_text[max(0, pattern_pos - 20):pattern_pos]
                        # Look for number after the pattern (within next 150 chars)
                        after_text = full_text[pattern_pos + len(pattern):pattern_pos + len(pattern) + 150]
                        
                        number_candidates = []
                        
                        # Strategy 1: Look for properly formatted comma-separated numbers after pattern
                        simple_match = re.search(r'\d{1,3}(?:,\d{3})+', after_text)
                        if simple_match:
                            value = parse_decimal_number(simple_match.group(0))
                            if value and value > 0:
                                number_candidates.append((value, 1))  # Priority 1 (best format)
                        
                        # Strategy 2: Look for fragmented comma-separated numbers after pattern
                        # Pattern: digits/spaces, comma, digits/spaces, comma, digits/spaces
                        fragmented_comma = re.findall(r'[\d\s]+,\s*[\d\s]+,\s*[\d\s]+', after_text)
                        for match in fragmented_comma[:2]:
                            cleaned = match.replace(' ', '')
                            if len(cleaned.replace(',', '')) >= 6:
                                value = parse_decimal_number(cleaned)
                                if value and value > 0 and 10000 <= value <= 999999999:
                                    number_candidates.append((value, 2))
                        
                        # Strategy 3: Check if there's a digit before pattern that might be part of number
                        # Look for pattern like "8 به ا ی ا ن ر ژ ی 2 0 2 , 0 9 3 , 0 8"
                        # The "8" might be the start: "8" + "2 0 2 , 0 9 3 , 0 8" = "80,202,093,08" (wrong)
                        # Or maybe it's: "8 0 , 3 9 0 , 2 0 2" but OCR split it
                        # Try to find if there's a digit right before pattern
                        before_digit = re.search(r'(\d)\s*$', before_text)
                        if before_digit and fragmented_comma:
                            # Try combining: digit + fragmented number
                            first_digit = before_digit.group(1)
                            frag_match = fragmented_comma[0]
                            # Try: first_digit + first part of fragmented
                            # This is complex, skip for now and use after-text only
                            pass
                        
                        # Strategy 4: Look for long digit sequences
                        long_digit_seq = re.findall(r'[\d\s]{12,}', after_text)
                        for match in long_digit_seq[:2]:
                            cleaned = match.replace(' ', '')
                            if len(cleaned) >= 6 and len(cleaned) <= 12:
                                value = parse_decimal_number(cleaned)
                                if value and value > 0 and 10000 <= value <= 999999999:
                                    number_candidates.append((value, 3))
                        
                        # Use the best candidate
                        if number_candidates:
                            number_candidates.sort(key=lambda x: (x[1], -x[0]))
                            value = number_candidates[0][0]
                            if item["key"] not in result["خلاصه صورتحساب"]:
                                result["خلاصه صورتحساب"][item["key"]] = value
                            break
        
        # Also process line by line for cleaner extractions
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
                # Remove the unique pattern found to leave the number
                remaining = line.replace(used_pattern, '').strip()
                
                # regex to find big numbers (including commas and spaces)
                # Handle fragmented numbers like "2 0 2 , 0 9 3 , 0 8"
                number_match = re.search(r'[\d,\s]+', remaining)
                if number_match:
                    num_str = number_match.group(0).replace(' ', '').replace(',', '')
                    if num_str and len(num_str) >= 6:  # Valid large number
                        value = parse_decimal_number(num_str)
                        if value and value > 0:
                            # Only update if we haven't found it yet, or if this value is larger (more complete)
                            if matched_key not in result["خلاصه صورتحساب"] or result["خلاصه صورتحساب"][matched_key] < value:
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
