"""Restructure license expiry section for Template 6."""
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


def parse_fuzzy_jalali_date(text: str) -> str | None:
    """
    Parse Jalali dates from noisy / bidi-garbled text.
    
    Handles:
    - YYYY/MM/DD
    - YYYYMMDD
    - DD <noise> / YYYY / MM (e.g. '28 روما/1408/09' => 1408/09/28)
    """
    if not text:
        return None
    
    t = convert_persian_digits(text)
    
    # 1) Direct YYYY/MM/DD
    m = re.search(r'(\d{4})/(\d{2})/(\d{2})', t)
    if m:
        return f"{m.group(1)}/{m.group(2)}/{m.group(3)}"
    
    # 2) Compact YYYYMMDD
    m = re.search(r'\b(\d{8})\b', t)
    if m:
        s = m.group(1)
        return f"{s[:4]}/{s[4:6]}/{s[6:8]}"
    
    # 3) Fuzzy split: capture three numeric groups around slashes,
    # allowing any non-digit noise between them.
    nums = re.findall(r'\d{1,4}', t)
    if len(nums) < 3:
        return None
    
    # Prefer a 4-digit year.
    year_candidates = [n for n in nums if len(n) == 4]
    if not year_candidates:
        return None
    
    year = year_candidates[0]
    # Take the first two non-year numbers as month/day candidates.
    rest = [n for n in nums if n != year]
    if len(rest) < 2:
        return None
    
    a, b = rest[0], rest[1]
    # Decide which is month (1..12) and which is day (1..31).
    a_i, b_i = int(a), int(b)
    if 1 <= a_i <= 12 and 1 <= b_i <= 31:
        month, day = a_i, b_i
    elif 1 <= b_i <= 12 and 1 <= a_i <= 31:
        month, day = b_i, a_i
    else:
        return None
    
    return f"{year}/{month:02d}/{day:02d}"


def extract_license_expiry(text):
    """Extract license expiry date from text.
    
    Expected format: YYYY/MM/DD (e.g., 1407/10/22)
    """
    normalized_text = convert_persian_digits(text)
    
    # Look for "تاریخ انقضای پروانه" followed by date
    patterns = [
        r'تاریخ انقضای پروانه\s*:?\s*(\d{4}/\d{2}/\d{2})',  # YYYY/MM/DD format
        r'تاریخ انقضای پروانه\s*:?\s*(\d{8})',  # YYYYMMDD format
        r'انقضای پروانه\s*:?\s*(\d{4}/\d{2}/\d{2})',
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
    
    # Fallback: fuzzy date parsing (handles bidi/noise cases)
    parsed = parse_fuzzy_jalali_date(normalized_text)
    if parsed:
        return parsed
    
    return None


def restructure_license_expiry_template6_json(json_path: Path, output_path: Path):
    """Restructure extracted JSON to include license expiry data for Template 6."""
    print(f"Restructuring License Expiry (Template 6) from {json_path}...")
    
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
        print(f"Error restructuring License Expiry T6: {e}")
        import traceback
        traceback.print_exc()
        return None

