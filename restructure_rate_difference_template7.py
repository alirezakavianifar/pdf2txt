"""Restructure rate difference section for Template 7 (Optional)."""
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
        # Try integer first
        if '.' not in text and '/' not in text:
            return int(text)
        else:
            # Handle decimal (slash or dot)
            text = text.replace('/', '.')
            return float(text)
    except ValueError:
        return None


def extract_rate_difference_data(text):
    """Extract rate difference information from text.
    
    Expected fields:
    - نرخ صنعتی (Industrial Rate): میان باری (5490), اوج باری (10980), کم باری (2945.77)
    - نرخ مابه التفاوت اجرای مقررات (Regulation Implementation Difference Rate): میان باری (2544.23), اوج باری (8034.23), کم باری (0)
    - متوسط قیمت تابلو اول بورس (Average First Exchange Board Price): میان باری (1801), اوج باری (1804), کم باری (1801)
    - متوسط نرخ بازار (Average Market Rate): میان باری (2945.77), اوج باری (2945.77), کم باری (2945.77)
    - حداکثر نرخ بازار عمده فروشی برق (Maximum Wholesale Market Rate): میان باری (3585.86), اوج باری (3900.71), کم باری (3186.3)
    - حداکثر نرخ تابلو سبز (Maximum Green Board Rate): میان باری (80000), اوج باری (80000), کم باری (80000)
    - نرخ تابلو سبز (Green Board Rate): میان باری (56758), اوج باری (56758), کم باری (56758)
    """
    normalized_text = convert_persian_digits(text)
    
    result = {
        "نرخ صنعتی": {
            "میان باری": None,
            "اوج باری": None,
            "کم باری": None
        },
        "نرخ مابه التفاوت اجرای مقررات": {
            "میان باری": None,
            "اوج باری": None,
            "کم باری": None
        },
        "متوسط قیمت تابلو اول بورس": {
            "میان باری": None,
            "اوج باری": None,
            "کم باری": None
        },
        "متوسط نرخ بازار": {
            "میان باری": None,
            "اوج باری": None,
            "کم باری": None
        },
        "حداکثر نرخ بازار عمده فروشی برق": {
            "میان باری": None,
            "اوج باری": None,
            "کم باری": None
        },
        "حداکثر نرخ تابلو سبز": {
            "میان باری": None,
            "اوج باری": None,
            "کم باری": None
        },
        "نرخ تابلو سبز": {
            "میان باری": None,
            "اوج باری": None,
            "کم باری": None
        }
    }
    
    lines = normalized_text.split('\n')
    full_text = ' '.join(lines)
    
    # Extract each rate type
    rate_types = [
        ("نرخ صنعتی", r'نرخ صنعتی'),
        ("نرخ مابه التفاوت اجرای مقررات", r'نرخ مابه التفاوت اجرای مقررات'),
        ("متوسط قیمت تابلو اول بورس", r'متوسط قیمت تابلو اول بورس'),
        ("متوسط نرخ بازار", r'متوسط نرخ بازار'),
        ("حداکثر نرخ بازار عمده فروشی برق", r'حداکثر نرخ بازار عمده فروشی برق'),
        ("حداکثر نرخ تابلو سبز", r'حداکثر نرخ تابلو سبز'),
        ("نرخ تابلو سبز", r'نرخ تابلو سبز')
    ]
    
    for rate_type, pattern in rate_types:
        # Find the line containing this rate type
        for line in lines:
            if re.search(pattern, line):
                # Extract numbers from this line
                numbers = re.findall(r'\d+(?:,\d+)*(?:\.\d+)?', line)
                if len(numbers) >= 3:
                    result[rate_type]["میان باری"] = parse_number(numbers[0])
                    result[rate_type]["اوج باری"] = parse_number(numbers[1])
                    result[rate_type]["کم باری"] = parse_number(numbers[2])
                break
    
    return result


def restructure_rate_difference_template7_json(json_path: Path, output_path: Path):
    """Restructure extracted JSON to include rate difference data for Template 7."""
    print(f"Restructuring Rate Difference (Template 7) from {json_path}...")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        text = data.get('text', '')
        
        # Extract rate difference data
        rate_data = extract_rate_difference_data(text)
        
        # Build restructured data
        result = {
            "نرخ های مابه التفاوت": rate_data
        }
        
        # Save restructured JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"  - Saved to {output_path}")
        extracted_count = sum(
            1 for rate_type in rate_data.values()
            for v in rate_type.values() if v is not None
        )
        print(f"  - Extracted {extracted_count} rate values")
        
        return result
        
    except Exception as e:
        print(f"Error restructuring Rate Difference T7: {e}")
        import traceback
        traceback.print_exc()
        return None

