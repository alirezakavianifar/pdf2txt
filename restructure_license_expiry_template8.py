"""Restructure license expiry section for Template 8."""
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


def extract_license_expiry_date(text: str, is_strict: bool = True) -> str | None:
    """Extract license expiry date (YYYY/MM/DD format) from text."""
    if not text:
        return None

    normalized_text = convert_persian_digits(text)
    # Comprehensive keywords for license expiry
    expiry_keywords = ["انقضا", "اعتبار", "پروانه", "مجوز"]
    
    matches = list(re.finditer(r"(\d{4}/\d{1,2}/\d{1,2})", normalized_text))
    
    # 1. Try keyword-based matching (Highest priority)
    for match in matches:
        date_str = match.group(1)
        start = max(0, match.start() - 30)
        end = min(len(normalized_text), match.end() + 30)
        context = normalized_text[start:end]
        if any(kw in context for kw in expiry_keywords):
            return date_str
            
    # 2. If not strict (dedicated license crop), pick a date that looks like a future expiry
    if not is_strict:
        future_dates = []
        for match in matches:
            date_str = match.group(1)
            try:
                year = int(date_str.split('/')[0])
                # Heuristic: anything 1405 or beyond is likely an expiry date
                # whereas 1404 or older might be issue/period dates.
                if year >= 1405:
                    future_dates.append(date_str)
            except (ValueError, IndexError):
                continue
        
        if future_dates:
            # If multiple future dates, pick the furthest one as expiry?
            # Usually there's only one.
            return sorted(future_dates)[-1]
            
    return None


def restructure_license_expiry_template8_json(extracted_json_path, output_json_path):
    """Restructure extracted JSON to include license expiry date data for Template 8."""
    with open(extracted_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Gather all possible text from this crop
    text_sources = []
    if data.get("text"):
        text_sources.append(data.get("text"))
    
    table = data.get("table", {})
    rows = table.get("rows", [])
    for row in rows:
        if row:
            text_sources.append(" ".join([str(cell) for cell in row if cell]))
    
    geometry = data.get("geometry", {})
    cells = geometry.get("cells", [])
    for cell in cells:
        if cell.get("text"):
            text_sources.append(cell.get("text"))
    
    combined_text = " ".join(text_sources)
    
    from text_normalization import default_normalizer
    normalized_text = default_normalizer.normalize(combined_text)
    
    # 1. Primary check: Use keywords on this dedicated crop
    # (We repeat the logic here to have fine-grained control)
    expiry_keywords = ["انقضا", "اعتبار", "پروانه", "مجوز"]
    
    matches = list(re.finditer(r"(\d{4}/\d{1,2}/\d{1,2})", normalized_text))
    expiry_date = None
    
    for match in matches:
        date_str = match.group(1)
        start = max(0, match.start() - 30)
        end = min(len(normalized_text), match.end() + 30)
        context = normalized_text[start:end]
        if any(kw in context for kw in expiry_keywords):
            expiry_date = date_str
            break
    
    # 2. Fallback 1: Use lenient date finder on this dedicated crop
    if not expiry_date:
        expiry_date = extract_license_expiry_date(combined_text, is_strict=False)

    # 3. Fallback 2: Check the bill_identifier_section sibling, but REQUIRE keywords there
    if not expiry_date:
        try:
            extracted_path = Path(extracted_json_path)
            stem = extracted_path.stem.replace("license_expiry_section", "bill_identifier_section")
            sibling_path = extracted_path.parent / f"{stem}.json"
            if sibling_path.exists():
                with open(sibling_path, "r", encoding="utf-8") as fb:
                    sibling_data = json.load(fb)
                
                sibling_text_sources = []
                if sibling_data.get("text"):
                    sibling_text_sources.append(sibling_data.get("text"))
                
                s_table = sibling_data.get("table", {})
                s_rows = s_table.get("rows", [])
                for row in s_rows:
                    if row:
                        sibling_text_sources.append(" ".join([str(cell) for cell in row if cell]))
                
                s_geometry = sibling_data.get("geometry", {})
                s_cells = s_geometry.get("cells", [])
                for cell in s_cells:
                    if cell.get("text"):
                        sibling_text_sources.append(cell.get("text"))
                
                combined_sibling_text = " ".join(sibling_text_sources)
                # Use strict mode for sibling text because it contains many dates
                expiry_date = extract_license_expiry_date(combined_sibling_text, is_strict=True)
        except Exception:
            pass
    
    # Build restructured data
    result = {
        "license_expiry_section": {
            "license_expiry_date": expiry_date
        }
    }
    
    # Save restructured JSON
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Restructured license expiry (Template 8) saved to: {output_json_path}")
    if expiry_date:
        print(f"Extracted expiry date: {expiry_date}")
    else:
        print("WARNING: Could not extract license expiry date")
    
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python restructure_license_expiry_template8.py <extracted_json_file> [output_json_file]")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file.parent / f"{input_file.stem}_restructured.json"
    
    if not input_file.exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)
    
    restructure_license_expiry_template8_json(input_file, output_file)

