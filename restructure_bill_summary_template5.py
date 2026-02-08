"""Restructure bill summary section for Template 5."""
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
    """Parse a number, removing commas and handling Persian digits.
    
    Handles both leading and trailing minus signs for negative numbers.
    Examples: "-912", "912-", "-1,234,567", "1,234,567-"
    """
    if not text:
        return None
    
    text = convert_persian_digits(text)
    # Remove commas used as thousand separators
    text = text.replace(',', '').replace(' ', '').strip()
    
    # Check for negative sign (leading or trailing)
    is_negative = text.startswith('-') or text.endswith('-')
    if text.startswith('-'):
        text = text[1:]
    elif text.endswith('-'):
        text = text[:-1]
    
    try:
        value = int(text)
        return -value if is_negative else value
    except ValueError:
        return None


def extract_bill_summary(text):
    """Extract financial summary items from text.
    
    Expected fields:
    - بهای انرژی تامین شده: 18,236,250
    - بستانکاری خرید: -25,322,420 (negative value)
    - ما بالتفاوت اجرای مقررات: 821,761,655
    - آبونمان: 143,481
    - هزینه سوخت نیروگاهی: 96,036,403
    - تعدیل بهای برق: 55,664,049
    - عوارض برق: 257,171,074
    - مالیات بر ارزش افزوده: 91,085,537
    """
    normalized_text = convert_persian_digits(text)
    
    result = {
        "بهای انرژی تامین شده": None,
        "بستانکاری خرید": None,
        "ما بالتفاوت اجرای مقررات": None,
        "آبونمان": None,
        "هزینه سوخت نیروگاهی": None,
        "تعدیل بهای برق": None,
        "عوارض برق": None,
        "مالیات بر ارزش افزوده": None
    }
    
    lines = normalized_text.split('\n')
    
    # Extract each field
    # Note: In Template 5, values appear BEFORE labels (RTL text order)
    # Pattern format: value (with optional leading/trailing minus) followed by label
    patterns = {
        "بهای انرژی تامین شده": r'(-?\d+(?:,\d+)*)\s+بهای انرژی تامین شده',
        "بستانکاری خرید": r'(-?\d+(?:,\d+)*(?:-)?)\s+بستانکاری خرید',
        "ما بالتفاوت اجرای مقررات": r'(-?\d+(?:,\d+)*)\s+ما بالتفاوت اجرای مقررات',
        "آبونمان": r'(-?\d+(?:,\d+)*)\s+آبونمان',
        "هزینه سوخت نیروگاهی": r'(-?\d+(?:,\d+)*)\s+هزینه سوخت نیروگاهی',
        "تعدیل بهای برق": r'(-?\d+(?:,\d+)*)\s+تعدیل بهای برق',
        "عوارض برق": r'(-?\d+(?:,\d+)*)\s+عوارض برق',
        "مالیات بر ارزش افزوده": r'(-?\d+(?:,\d+)*)\s+مالیات بر ارزش افزوده'
    }
    
    full_text = ' '.join(lines)
    
    for field, pattern in patterns.items():
        match = re.search(pattern, full_text)
        if match:
            result[field] = parse_number(match.group(1))
    
    return result


def restructure_bill_summary_template5_json(json_path: Path, output_path: Path):
    """Restructure extracted JSON to include bill summary data for Template 5."""
    print(f"Restructuring Bill Summary (Template 5) from {json_path}...")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        text = data.get('text', '')
        
        # Extract bill summary
        summary_data = extract_bill_summary(text)
        
        # Build restructured data
        result = {
            "خلاصه صورتحساب": summary_data
        }
        
        # Save restructured JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"  - Saved to {output_path}")
        extracted_count = sum(1 for v in summary_data.values() if v is not None)
        print(f"  - Extracted {extracted_count}/{len(summary_data)} summary items")
        
        return result
        
    except Exception as e:
        print(f"Error restructuring Bill Summary T5: {e}")
        import traceback
        traceback.print_exc()
        return None

