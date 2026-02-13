"""Restructure license expiry section JSON data."""
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

def extract_license_expiry_date(text):
    """Extract license expiry date from text."""
    # Pattern: "تاریخ انقضا پروانه : YYYY/MM/DD" or similar
    # The date format might be Persian numerals or Arabic-Indic numerals
    
    # Try to find the date pattern after "تاریخ انقضا پروانه"
    patterns = [
        r'تاریخ انقضا پروانه\s*:\s*(\d{4}/\d{2}/\d{2})',  # Regular digits
        r'تاریخ انقضا پروانه\s*:\s*([۰-۹٠-٩]{4}/[۰-۹٠-٩]{2}/[۰-۹٠-٩]{2})',  # Persian/Arabic-Indic digits
        r'انقضا\s*:\s*(\d{4}/\d{2}/\d{2})',
        r'پروانه\s*:\s*(\d{4}/\d{2}/\d{2})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            date_str = match.group(1)
            # Convert Persian/Arabic-Indic numerals to regular digits
            date_str = convert_persian_digits(date_str)
            return date_str
    
    # Fallback: try to find any date-like pattern YYYY/MM/DD in the text
    # Look for patterns that might be dates
    date_pattern = r'(\d{4}/\d{2}/\d{2})'
    matches = list(re.finditer(date_pattern, text))
    
    if matches:
        # Get the first match (likely the expiry date if it's a small section)
        date_str = matches[0].group(1)
        date_str = convert_persian_digits(date_str)
        return date_str
    
    return None

def restructure_license_expiry_json(extracted_json_path, output_json_path):
    """Restructure extracted JSON to include license expiry data."""
    with open(extracted_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Gather all possible text
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
    
    # Try keyword-based matching first
    from text_normalization import default_normalizer
    normalized_text = default_normalizer.normalize(combined_text)
    
    expiry_keywords = ["انقضا", "اعتبار"]
    matches = re.finditer(r"(\d{4}/\d{1,2}/\d{1,2})", normalized_text)
    expiry_date = None
    
    for match in matches:
        date_str = match.group(1)
        # Check context around the match
        start = max(0, match.start() - 30)
        end = min(len(normalized_text), match.end() + 30)
        context = normalized_text[start:end]
        
        if any(kw in context for kw in expiry_keywords):
            expiry_date = date_str
            break
            
    # Fallback to general date extraction
    if not expiry_date:
        expiry_date = extract_license_expiry_date(combined_text)
    
    # Build restructured data
    result = {
        "تاریخ انقضا پروانه": expiry_date if expiry_date else None
    }
    
    # Save restructured JSON with explicit UTF-8 encoding
    try:
        with open(output_json_path, 'w', encoding='utf-8', errors='replace') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    except UnicodeEncodeError as e:
        # Fallback: replace problematic characters
        import sys
        if sys.stdout.encoding and 'utf' not in sys.stdout.encoding.lower():
            # On Windows with cp1252, ensure file is written correctly
            with open(output_json_path, 'w', encoding='utf-8', errors='replace') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        else:
            raise
    
    print(f"Restructured data saved to: {output_json_path}")
    if expiry_date:
        print(f"Extracted expiry date: {expiry_date}")
    else:
        print("WARNING: Could not extract expiry date")
    
    return result

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python restructure_license_expiry.py <extracted_json_file> [output_json_file]")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file.parent / f"{input_file.stem}_restructured.json"
    
    if not input_file.exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)
    
    restructure_license_expiry_json(input_file, output_file)
