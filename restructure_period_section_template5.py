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
    
    # Extract دوره/سال (Period/Year) - format like "4/7" or "4 / 7"
    for line in lines:
        # Pattern 1: "دوره / سال 4 / 7" or "دوره/سال 4/7" or "دوره سال 4/7"
        match = re.search(r'دوره\s*/?\s*سال\s*:?\s*(\d+)\s*/\s*(\d+)', line)
        if match:
            result["دوره/سال"] = f"{match.group(1)}/{match.group(2)}"
            break
        # Pattern 2: "دوره / سال : 4/7" (with colon)
        match = re.search(r'دوره\s*/\s*سال\s*:\s*(\d+/\d+)', line)
        if match:
            result["دوره/سال"] = match.group(1)
            break
        # Pattern 3: "8 0 دوره سال" (numbers before the label, like in rate_difference_table)
        match = re.search(r'(\d+)\s+\d+\s+دوره\s*سال', line)
        if match:
            # Need to find the second number - look for pattern like "8 0" or "8 / 4"
            match2 = re.search(r'(\d+)\s*[/\s]\s*(\d+)\s+دوره\s*سال', line)
            if match2:
                result["دوره/سال"] = f"{match2.group(1)}/{match2.group(2)}"
            else:
                # If only one number found, try to find another number nearby
                numbers = re.findall(r'\d+', line)
                if len(numbers) >= 2:
                    # Use first two numbers as period/year
                    result["دوره/سال"] = f"{numbers[0]}/{numbers[1]}"
            if result["دوره/سال"]:
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
    
    # Extract به مدت (Duration) - format like "31 روز" or just "30"
    # Try with "روز" first, then without
    for line in lines:
        match = re.search(r'به مدت\s*:?\s*(\d+)\s*روز', line)
        if match:
            result["به مدت"] = int(match.group(1))
            break
    # Fallback: if not found with "روز", try without it
    if result["به مدت"] is None:
        for line in lines:
            match = re.search(r'به مدت\s*:?\s*(\d+)', line)
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
        
        # If "دوره/سال" is missing, try to get it from rate_difference_table_section or period_year_section
        if period_data.get("دوره/سال") is None:
            # Try rate_difference_table_section first (most likely location based on actual PDF)
            sections_to_check = ["rate_difference_table_section", "period_year_section"]
            for section_name in sections_to_check:
                try:
                    extracted_path = Path(json_path)
                    stem = extracted_path.stem.replace("period_section", section_name)
                    sibling_path = extracted_path.parent / f"{stem}.json"
                    if sibling_path.exists():
                        with open(sibling_path, "r", encoding="utf-8") as fb:
                            sibling_data = json.load(fb)
                        
                        # Combine text and table cells from the section
                        sibling_parts = [sibling_data.get("text", "")]
                        sibling_table = sibling_data.get("table") or {}
                        sibling_rows = sibling_table.get("rows") or []
                        for row in sibling_rows:
                            for cell in row:
                                if isinstance(cell, str):
                                    sibling_parts.append(cell)
                        sibling_text = "\n".join(sibling_parts)
                        
                        # Try to extract "دوره/سال" from this section
                        sibling_period = extract_period_data(sibling_text)
                        if sibling_period.get("دوره/سال"):
                            period_data["دوره/سال"] = sibling_period["دوره/سال"]
                            print(f"  - Found دوره/سال in {section_name}: {period_data['دوره/سال']}")
                            break
                except Exception as e:
                    # Non-fatal; continue to next section
                    print(f"  - Warning: Could not check {section_name} for دوره/سال: {e}")
                    continue
        
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

