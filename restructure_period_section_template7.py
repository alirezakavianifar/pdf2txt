"""Restructure period section for Template 7."""
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
    """Parse number from text, removing commas."""
    if not text:
        return None
    try:
        return float(text.replace(',', ''))
    except:
        return None


def extract_period_data(text):
    """Extract period information from text.
    
    Expected fields for Template 7:
    - از تاریخ (From Date): 1404/06/01
    - تا تاریخ (To Date): 1404/07/01
    - به مدت (Duration): 31 (days)
    - تاریخ صدور صورتحساب (Invoice Issue Date): 1404/07/30
    - کل مصرف (Total Consumption): 361872
    """
    normalized_text = convert_persian_digits(text)
    
    result = {
        "از تاریخ": None,
        "تا تاریخ": None,
        "به مدت": None,
        "تاریخ صدور صورتحساب": None,
        "کل مصرف": None
    }
    
    lines = normalized_text.split('\n')
    full_text = ' '.join(lines)
    
    # Extract از تاریخ (From Date)
    match = re.search(r'از تاریخ\s*:?\s*(\d{4}/\d{2}/\d{2})', normalized_text)
    if match:
        result["از تاریخ"] = match.group(1)
    
    # Extract تا تاریخ (To Date)
    match = re.search(r'تا تاریخ\s*:?\s*(\d{4}/\d{2}/\d{2})', normalized_text)
    if match:
        result["تا تاریخ"] = match.group(1)
    
    # Extract به مدت (Duration) - look for number followed by "روز" or just number
    match = re.search(r'به مدت\s*:?\s*(\d+)', normalized_text)
    if match:
        result["به مدت"] = int(match.group(1))
    
    # Extract تاریخ صدور صورتحساب (Invoice Issue Date)
    match = re.search(r'تاریخ صدور صورتحساب\s*:?\s*(\d{4}/\d{2}/\d{2})', normalized_text)
    if match:
        result["تاریخ صدور صورتحساب"] = match.group(1)
    
    # Extract کل مصرف (Total Consumption)
    match = re.search(r'کل مصرف\s*:?\s*([\d,]+)', normalized_text)
    if match:
        result["کل مصرف"] = parse_number(match.group(1))
    
    return result


def restructure_period_section_template7_json(json_path: Path, output_path: Path):
    """Restructure extracted JSON to include period section data for Template 7."""
    print(f"Restructuring Period Section (Template 7) from {json_path}...")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        text = data.get('text', '')
        
        # Extract period data
        period_data = extract_period_data(text)
        
        # Build restructured data
        result = {
            "اطلاعات دوره": period_data
        }
        
        # Save restructured JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"  - Saved to {output_path}")
        extracted_count = sum(1 for v in period_data.values() if v is not None)
        print(f"  - Extracted {extracted_count}/{len(period_data)} period fields")
        
        return result
        
    except Exception as e:
        print(f"Error restructuring Period Section T7: {e}")
        import traceback
        traceback.print_exc()
        return None

