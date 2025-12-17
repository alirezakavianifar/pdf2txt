"""Restructure transit section for Template 6."""
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
        return int(text)
    except ValueError:
        return None


def extract_transit_data(text):
    """Extract transit section data from text.
    
    Expected fields:
    - هزینه ترانزیت (Transit Cost): 449,844,512
    - ترانزیت فوق توزیع (Super Distribution Transit): 1,049,637,194
    - حق العمل کاری (Commission/Labor Fee)
    - تعدیل بهای برق (Electricity Price Adjustment)
    - مالیات بر ارزش افزوده (Value Added Tax): 149,948,170
    - بدهی گذشته (Past Debt)
    - وجه التزام (Penalty/Liquidated Damages)
    """
    normalized_text = convert_persian_digits(text)
    
    result = {
        "هزینه ترانزیت": None,
        "ترانزیت فوق توزیع": None,
        "حق العمل کاری": None,
        "تعدیل بهای برق": None,
        "مالیات بر ارزش افزوده": None,
        "بدهی گذشته": None,
        "وجه التزام": None
    }
    
    lines = normalized_text.split('\n')
    full_text = ' '.join(lines)
    
    # Extract each field
    patterns = {
        "هزینه ترانزیت": r'هزینه ترانزیت[^\d]*(\d+(?:,\d+)*)',
        "ترانزیت فوق توزیع": r'ترانزیت فوق توزیع[^\d]*(\d+(?:,\d+)*)',
        "حق العمل کاری": r'حق العمل کاری[^\d]*(\d+(?:,\d+)*)',
        "تعدیل بهای برق": r'تعدیل بهای برق[^\d]*(\d+(?:,\d+)*)',
        "مالیات بر ارزش افزوده": r'مالیات بر ارزش افزوده[^\d]*(\d+(?:,\d+)*)',
        "بدهی گذشته": r'بدهی گذشته[^\d]*(\d+(?:,\d+)*)',
        "وجه التزام": r'وجه التزام[^\d]*(\d+(?:,\d+)*)'
    }
    
    for field, pattern in patterns.items():
        match = re.search(pattern, full_text)
        if match:
            result[field] = parse_number(match.group(1))
    
    return result


def restructure_transit_section_template6_json(json_path: Path, output_path: Path):
    """Restructure extracted JSON to include transit section data for Template 6."""
    print(f"Restructuring Transit Section (Template 6) from {json_path}...")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        text = data.get('text', '')
        
        # Extract transit data
        transit_data = extract_transit_data(text)
        
        # Build restructured data
        result = {
            "صورتحساب ترانزیت": transit_data
        }
        
        # Save restructured JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"  - Saved to {output_path}")
        extracted_count = sum(1 for v in transit_data.values() if v is not None)
        print(f"  - Extracted {extracted_count}/{len(transit_data)} transit fields")
        
        return result
        
    except Exception as e:
        print(f"Error restructuring Transit Section T6: {e}")
        import traceback
        traceback.print_exc()
        return None

