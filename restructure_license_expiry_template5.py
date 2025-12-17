"""Restructure license expiry section for Template 5."""
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


def extract_license_expiry(text):
    """Extract license expiry date from text.
    
    Expected format: YYYYMMDD (e.g., ۱۴۰۳۱۲۳۹)
    """
    normalized_text = convert_persian_digits(text)
    
    # Look for "تاریخ انقضای پروانه" followed by date
    patterns = [
        r'تاریخ انقضای پروانه\s*:?\s*(\d{8})',  # YYYYMMDD format
        r'تاریخ انقضای پروانه\s*:?\s*(\d{4}/\d{2}/\d{2})',  # YYYY/MM/DD format
        r'انقضای پروانه\s*:?\s*(\d{8})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, normalized_text)
        if match:
            date_str = match.group(1)
            # If it's YYYYMMDD format, convert to YYYY/MM/DD
            if len(date_str) == 8 and '/' not in date_str:
                return f"{date_str[:4]}/{date_str[4:6]}/{date_str[6:8]}"
            return date_str
    
    # Fallback: look for 8-digit number
    numbers = re.findall(r'\d{8}', normalized_text)
    if numbers:
        date_str = numbers[0]
        return f"{date_str[:4]}/{date_str[4:6]}/{date_str[6:8]}"
    
    return None


def restructure_license_expiry_template5_json(json_path: Path, output_path: Path):
    """Restructure extracted JSON to include license expiry data for Template 5."""
    print(f"Restructuring License Expiry (Template 5) from {json_path}...")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        text = data.get('text', '')
        
        # Extract license expiry
        expiry_date = extract_license_expiry(text)
        
        # Build restructured data
        result = {
            "تاریخ انقضای پروانه": expiry_date
        }
        
        # Save restructured JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"  - Saved to {output_path}")
        if expiry_date:
            print(f"  - Extracted expiry date: {expiry_date}")
        else:
            print("  - WARNING: Could not extract license expiry date")
        
        return result
        
    except Exception as e:
        print(f"Error restructuring License Expiry T5: {e}")
        import traceback
        traceback.print_exc()
        return None

