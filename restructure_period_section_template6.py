"""Restructure period section for Template 6."""
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
    
    Expected fields for Template 6:
    - از تاریخ (From Date): 1404/06/01
    - تا تاریخ (To Date): 1404/07/01
    - تعداد روز (Number of Days): 31
    - دوره/سال (Period/Year): 1404/6
    - تاریخ صورتحساب (Invoice Date): 1404/07/15
    """
    normalized_text = convert_persian_digits(text)
    
    result = {
        "از تاریخ": None,
        "تا تاریخ": None,
        "تعداد روز": None,
        "دوره/سال": None,
        "تاریخ صورتحساب": None
    }
    
    lines = normalized_text.split('\n')
    
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
    
    # Extract تعداد روز (Number of Days)
    for line in lines:
        match = re.search(r'تعداد روز\s*:?\s*(\d+)', line)
        if match:
            result["تعداد روز"] = int(match.group(1))
            break
    
    # Extract دوره/سال (Period/Year) - format like "1404/6"
    for line in lines:
        match = re.search(r'دوره\s*/?\s*سال\s*:?\s*(\d{4}/\d+)', line)
        if match:
            result["دوره/سال"] = match.group(1)
            break
    
    # Extract تاریخ صورتحساب (Invoice Date)
    for line in lines:
        match = re.search(r'تاریخ صورتحساب\s*:?\s*(\d{4}/\d{2}/\d{2})', line)
        if match:
            result["تاریخ صورتحساب"] = match.group(1)
            break
    
    return result


def restructure_period_section_template6_json(json_path: Path, output_path: Path):
    """Restructure extracted JSON to include period section data for Template 6."""
    print(f"Restructuring Period Section (Template 6) from {json_path}...")
    
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
        print(f"Error restructuring Period Section T6: {e}")
        import traceback
        traceback.print_exc()
        return None

