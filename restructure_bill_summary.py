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
            {"key": "بهای انرژی", "patterns": ["بهای انرژی", "بهای", "انرژی"]},
            {"key": "آبونمان", "patterns": ["آبونمان"]},
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
                # Remove the unique pattern found to leave the number
                # But careful: splitting might be better if regex fails
                # Try simple replacement of the matched substring
                remaining = line.replace(used_pattern, '').strip()
                
                # regex to find big numbers (including commas)
                number_match = re.search(r'[\d,]+', remaining)
                if number_match:
                    num_str = number_match.group(0)
                    value = parse_decimal_number(num_str)
                    
                    # Store result. Note: if key already exists (rare in this section), overwrite
                    if matched_key == "قسط":
                         # Special accumulation logic if needed, otherwise overwrite
                         result["خلاصه صورتحساب"][matched_key] = value
                    else:
                        result["خلاصه صورتحساب"][matched_key] = value
            else:
                # Debug unprinted lines if needed
                pass

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
