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


def extract_license_expiry_date(text: str) -> str | None:
    """Extract license expiry date (YYYY/MM/DD format) from text.

    For Template 8 the expiry date often appears in the bill-identifier crop,
    not in the dedicated license-expiry crop, so this function is reused on
    both raw texts as a generic date finder.
    """
    if not text:
        return None

    # Normalize Persian digits
    normalized_text = convert_persian_digits(text)

    # Primary pattern: YYYY/MM/DD
    primary = re.findall(r"\d{4}/\d{2}/\d{2}", normalized_text)
    if primary:
        # Prefer dates starting with 14 (Persian calendar) if present
        starting_14 = [d for d in primary if d.startswith("14")]
        return starting_14[0] if starting_14 else primary[0]

    # Fallback: any date-like pattern
    fallback = re.findall(r"\d{4}/\d{1,2}/\d{1,2}", normalized_text)
    if fallback:
        starting_14 = [d for d in fallback if d.startswith("14")]
        return starting_14[0] if starting_14 else fallback[0]

    return None


def restructure_license_expiry_template8_json(extracted_json_path, output_json_path):
    """Restructure extracted JSON to include license expiry date data for Template 8."""
    with open(extracted_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    text = data.get('text', '')

    # Try to extract from this crop first
    expiry_date = extract_license_expiry_date(text)

    # Fallback: try to read from the bill_identifier_section JSON, which for
    # Template 8 often contains the expiry date alongside the identifiers.
    if not expiry_date:
        try:
            extracted_path = Path(extracted_json_path)
            stem = extracted_path.stem.replace("license_expiry_section", "bill_identifier_section")
            sibling_path = extracted_path.parent / f"{stem}.json"
            if sibling_path.exists():
                with open(sibling_path, "r", encoding="utf-8") as fb:
                    sibling_data = json.load(fb)
                sibling_text = sibling_data.get("text", "")
                expiry_date = extract_license_expiry_date(sibling_text)
        except Exception:
            # Fallback failures are non-fatal; keep expiry_date as None
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

