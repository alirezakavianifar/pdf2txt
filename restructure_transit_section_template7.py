"""Restructure transit section for Template 7."""
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
    
    # Check for negative sign (can be at end with -)
    is_negative = text.endswith('-') or text.startswith('-')
    if text.endswith('-'):
        text = text[:-1]
    elif text.startswith('-'):
        text = text[1:]
    
    if not text or text == '.':
        return None
    
    try:
        return int(text) if not is_negative else -int(text)
    except ValueError:
        return None


def extract_transit_data(text):
    """Extract transit section data from text.
    
    Expected fields for Template 7:
    - ترانزیت توزیع (Distribution Transit): 168,075,118
    - ترانزیت برق منطقه ای (Regional Electricity Transit): 392,175,274
    - مالیات بر ارزش افزوده (Value Added Tax): 56,025,039
    - بدهکار / بستانکار (Debtor/Creditor): 616,274,476- (negative)
    - کسر هزار ریال (Thousand Rial Deduction): 955
    - نرخ ترانزیت توزیع (Distribution Transit Rate): 246564
    - نرخ ترانزیت برق منطقه ای (Regional Electricity Transit Rate): 575316
    """
    normalized_text = convert_persian_digits(text)
    
    result = {
        "ترانزیت توزیع": None,
        "ترانزیت برق منطقه ای": None,
        "مالیات بر ارزش افزوده": None,
        "بدهکار / بستانکار": None,
        "کسر هزار ریال": None,
        "نرخ ترانزیت توزیع": None,
        "نرخ ترانزیت برق منطقه ای": None
    }
    
    lines = normalized_text.split('\n')
    full_text = ' '.join(lines)
    
    # Extract each field
    patterns = {
        "ترانزیت توزیع": r'ترانزیت توزیع\s*:?\s*([\d,]+)',
        "ترانزیت برق منطقه ای": r'ترانزیت برق منطقه\s*ای\s*:?\s*([\d,]+)',
        "مالیات بر ارزش افزوده": r'مالیات بر ارزش افزوده\s*:?\s*([\d,]+)',
        "بدهکار / بستانکار": r'بدهکار\s*/?\s*بستانکار\s*:?\s*([\d,]+-?)',
        "کسر هزار ریال": r'کسر هزار ریال\s*:?\s*([\d,]+)',
        "نرخ ترانزیت توزیع": r'نرخ ترانزیت توزیع\s*:?\s*([\d,]+)',
        "نرخ ترانزیت برق منطقه ای": r'نرخ ترانزیت برق منطقه\s*ای\s*:?\s*([\d,]+)'
    }
    
    for field, pattern in patterns.items():
        match = re.search(pattern, full_text)
        if match:
            result[field] = parse_number(match.group(1))
    
    return result


def restructure_transit_section_template7_json(json_path: Path, output_path: Path):
    """Restructure extracted JSON to include transit section data for Template 7."""
    print(f"Restructuring Transit Section (Template 7) from {json_path}...")
    
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
        print(f"Error restructuring Transit Section T7: {e}")
        import traceback
        traceback.print_exc()
        return None

