from pathlib import Path
import json
import re
from text_normalization import default_normalizer

def restructure_period_section_template4_json(json_path: Path, output_path: Path):
    """
    Restructures Period Section (Template 4).
    """
    print(f"Restructuring Period (Template 4) from {json_path}...")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Get original text and normalize only digits (not BIDI) to preserve text order
        original_text = data.get("text", "")
        # Normalize only Persian digits, not full BIDI processing which garbles Persian text
        from text_normalization import TextNormalizer
        digit_normalizer = TextNormalizer(
            normalize_whitespace=True,
            remove_extra_spaces=True,
            normalize_persian_numbers=True,
            handle_bidi=False  # Disable BIDI to preserve text order
        )
        text = digit_normalizer.normalize(original_text)
        
        # Initialize result with Persian field names
        result = {
            "از_تاریخ": None,  # From Date
            "تا_تاریخ": None,  # To Date
            "تعداد_روز_دوره": None  # Number of days in period
        }
        
        # First, try to match the combined pattern: "از تاریخ : تا تاریخ : [date1] [date2]"
        # This is the common format where both labels appear together
        combined_match = re.search(r'از\s*تاريخ\s*:?\s*تا\s*تاريخ\s*:?\s*(\d{4}/\d{2}/\d{2})\s+(\d{4}/\d{2}/\d{2})', text, re.IGNORECASE)
        if combined_match:
            result["از_تاریخ"] = combined_match.group(1)
            result["تا_تاریخ"] = combined_match.group(2)
        else:
            # Try individual patterns if combined pattern doesn't match
            # Extract "از تاریخ" (From Date)
            # Pattern: "از تاریخ : 1404/04/01" or "از تاریخ: 1404/04/01" or "از تاریخ1404/04/01"
            from_date_match = re.search(r'از\s*تاريخ\s*:?\s*(\d{4}/\d{2}/\d{2})', text, re.IGNORECASE)
            if from_date_match:
                result["از_تاریخ"] = from_date_match.group(1)
            
            # Extract "تا تاریخ" (To Date)
            # Pattern: "تا تاریخ : 1404/05/01" or similar
            to_date_match = re.search(r'تا\s*تاريخ\s*:?\s*(\d{4}/\d{2}/\d{2})', text, re.IGNORECASE)
            if to_date_match:
                result["تا_تاریخ"] = to_date_match.group(1)
        
        # Fallback: If labels not found, try to find dates by position
        # (first date is usually "از تاریخ", second is "تا تاریخ")
        if result["از_تاریخ"] is None or result["تا_تاریخ"] is None:
            all_dates = re.findall(r"\d{4}/\d{2}/\d{2}", text)
            if len(all_dates) >= 2:
                if result["از_تاریخ"] is None:
                    result["از_تاریخ"] = all_dates[0]
                if result["تا_تاریخ"] is None:
                    result["تا_تاریخ"] = all_dates[1]
            elif len(all_dates) == 1:
                if result["از_تاریخ"] is None:
                    result["از_تاریخ"] = all_dates[0]
        
        # Extract "تعداد روز دوره" (Number of days in period)
        # Pattern: "تعداد روز دوره : 31" or "تعداد روز دوره: 31" or "تعداد روز دوره : (روز) 31"
        days_match = re.search(r'تعداد\s*روز\s*دوره\s*:?\s*(?:\(روز\)\s*)?(\d+)', text, re.IGNORECASE)
        if days_match:
            result["تعداد_روز_دوره"] = int(days_match.group(1))
        else:
            # Fallback: Look for numbers that are likely period days (28-31)
            # But avoid matching years (1404, etc.)
            days_fallback = re.search(r'\b(2[89]|30|31)\b(?!\s*/\s*\d)', text)
            if days_fallback:
                result["تعداد_روز_دوره"] = int(days_fallback.group(1))
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        return result
    except Exception as e:
        print(f"Error restructuring Period T4: {e}")
        return None
