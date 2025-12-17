"""Restructure period section for Template 5."""
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


def extract_period_data(text):
    """Extract period information from text.
    
    Expected fields for Template 5:
    - دوره/سال (Period/Year): ۴/۷ (period 4, year 7 of 1404)
    - از تاریخ (From Date): ۱۴۰۴/۰۶/۰۱
    - تا تاریخ (To Date): ۱۴۰۴/۰۷/۰۱
    - به مدت (Duration): ۳۱ روز (31 days)
    """
    normalized_text = convert_persian_digits(text)
    
    result = {
        "دوره/سال": None,
        "از تاریخ": None,
        "تا تاریخ": None,
        "به مدت": None
    }
    
    lines = normalized_text.split('\n')
    
    # Extract دوره/سال (Period/Year) - format like "4/7"
    for line in lines:
        match = re.search(r'دوره\s*/?\s*سال\s*:?\s*(\d+/\d+)', line)
        if match:
            result["دوره/سال"] = match.group(1)
            break
    
    # Extract از تاریخ (From Date)
    for line in lines:
        match = re.search(r'از تاریخ\s*:?\s*(\d{4}/\d{2}/\d{2})', line)
        if match:
            result["از تاریخ"] = match.group(1)
            break
    
    # Extract تا تاریخ (To Date)
    for line in lines:
        match = re.search(r'تا تاریخ\s*:?\s*(\d{4}/\d{2}/\d{2})', line)
        if match:
            result["تا تاریخ"] = match.group(1)
            break
    
    # Extract به مدت (Duration) - format like "31 روز"
    for line in lines:
        match = re.search(r'به مدت\s*:?\s*(\d+)\s*روز', line)
        if match:
            result["به مدت"] = int(match.group(1))
            break
    
    return result


def restructure_period_section_template5_json(json_path: Path, output_path: Path):
    """Restructure extracted JSON to include period section data for Template 5."""
    print(f"Restructuring Period Section (Template 5) from {json_path}...")
    
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
        print(f"Error restructuring Period Section T5: {e}")
        import traceback
        traceback.print_exc()
        return None

