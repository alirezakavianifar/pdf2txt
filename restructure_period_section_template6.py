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


def parse_fuzzy_jalali_date(text: str) -> str | None:
    """
    Parse Jalali dates from noisy / bidi-garbled text.
    
    Handles:
    - YYYY/MM/DD
    - DD <noise> / YYYY / MM (e.g. '28 روما/1404/07' => 1404/07/28)
    """
    if not text:
        return None
    t = convert_persian_digits(text)
    
    m = re.search(r'(\d{4})/(\d{2})/(\d{2})', t)
    if m:
        return f"{m.group(1)}/{m.group(2)}/{m.group(3)}"
    
    nums = re.findall(r'\d{1,4}', t)
    if len(nums) < 3:
        return None
    
    year_candidates = [n for n in nums if len(n) == 4]
    if not year_candidates:
        return None
    year = year_candidates[0]
    rest = [n for n in nums if n != year]
    if len(rest) < 2:
        return None
    
    a_i, b_i = int(rest[0]), int(rest[1])
    if 1 <= a_i <= 12 and 1 <= b_i <= 31:
        month, day = a_i, b_i
    elif 1 <= b_i <= 12 and 1 <= a_i <= 31:
        month, day = b_i, a_i
    else:
        return None
    
    return f"{year}/{month:02d}/{day:02d}"


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
    full_text = ' '.join(lines)
    
    # --- Primary strategy: labelled extraction (ideal case) ---
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
            try:
                result["تعداد روز"] = int(match.group(1))
            except ValueError:
                result["تعداد روز"] = None
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
    
    # --- Fallback strategy: unlabeled numeric sequence ---
    # In some Template 6 crops (like 6_period_section.json), the labels such as
    # "از تاریخ" / "تا تاریخ" are missing from the flattened `text` field and
    # only the numbers appear in order:
    #   1404/06/01 1404/07/01 31 6 / 1404 1404/07/15
    # When the labelled extraction above fails, we try to recover the values
    # purely from this ordered numeric pattern.
    if all(v is None for v in result.values()):
        # Extract from/to dates directly
        dates = re.findall(r'\d{4}/\d{2}/\d{2}', full_text)
        if len(dates) >= 2:
            result["از تاریخ"] = dates[0]
            result["تا تاریخ"] = dates[1]
        
        # Days: first 1-3 digit token after the two dates
        if result["از تاریخ"] and result["تا تاریخ"]:
            after = full_text.split(result["تا تاریخ"], 1)[-1]
            m_days = re.search(r'\b(\d{1,3})\b', after)
            if m_days:
                try:
                    result["تعداد روز"] = int(m_days.group(1))
                except ValueError:
                    result["تعداد روز"] = None
        
        # Period/year like "6 / 1404" or "6/1404" (often survives even when labels don't)
        m_py = re.search(r'\b(\d{1,2})\s*/\s*(\d{4})\b', full_text)
        if m_py:
            month = int(m_py.group(1))
            year = m_py.group(2)
            result["دوره/سال"] = f"{year}/{month}"
        
        # Invoice date: look for any other fuzzy date-like fragment
        # (e.g. '28 روما/1404/07' -> 1404/07/28)
        # We pick the first parsed fuzzy date that is not equal to from/to.
        candidates = re.split(r'\s+', full_text)
        for token in candidates:
            parsed = parse_fuzzy_jalali_date(token)
            if parsed and parsed not in (result["از تاریخ"], result["تا تاریخ"]):
                result["تاریخ صورتحساب"] = parsed
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

