"""Restructure bill identifier section for Template 8."""
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


def extract_bill_identifier(text: str) -> str | None:
    """Extract bill identifier (may contain dots as separators) from text.

    Template 8 text is noisy and often includes multiple numbers (dates, account numbers, etc.).
    Strategy:
    - Prefer 13+ digit sequences (bill IDs and similar)
    - If multiple candidates, pick the one that looks most like a bill ID:
      - length >= 13
      - starts with '22' when available (matches samples like 2207525403220)
    - As a last resort, fall back to the longest digit sequence.
    """
    if not text:
        return None

    # Normalize Persian digits
    normalized_text = convert_persian_digits(text)

    # Remove whitespace for easier matching
    text_clean = normalized_text.replace(" ", "").replace("\n", "")

    # 1) Look for pattern with dots (e.g., "220.752540.3220")
    dotted = re.findall(r"\d+\.\d+\.\d+", text_clean)
    if dotted:
        dotted = [v for v in dotted if len(v.replace(".", "")) >= 12]
        if dotted:
            starting_22 = [v for v in dotted if v.replace(".", "").startswith("22")]
            if starting_22:
                return max(starting_22, key=lambda v: len(v.replace(".", "")))
            return max(dotted, key=lambda v: len(v.replace(".", "")))

    # 2) Collect all long digit sequences (13+ digits)
    long_digits = [m for m in re.findall(r"\d{13,}", text_clean)]
    if long_digits:
        # Prefer ones starting with 22 (matches bill id examples)
        starting_22 = [v for v in long_digits if v.startswith("22")]
        if starting_22:
            return max(starting_22, key=len)
        return max(long_digits, key=len)

    # 3) Fallback: find longest sequence of digits of any length
    matches = re.findall(r"\d+", text_clean)
    if matches:
        return max(matches, key=len)

    return None


def restructure_bill_identifier_template8_json(extracted_json_path, output_json_path):
    """Restructure extracted JSON to include bill identifier data for Template 8."""
    with open(extracted_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Combine plain text and any table cell text to maximise our chances of
    # seeing the full identifier (which is often only present inside the table
    # content for Template 8).
    parts: list[str] = [data.get("text", "")]
    table = data.get("table") or {}
    rows = table.get("rows") or []
    for row in rows:
        for cell in row:
            if isinstance(cell, str):
                parts.append(cell)
    full_text = "\n".join(parts)

    # Extract bill identifier
    identifier = extract_bill_identifier(full_text)
    
    # Build restructured data
    result = {
        "bill_identifier_section": {
            "bill_id": identifier
        }
    }
    
    # Save restructured JSON
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Restructured bill identifier (Template 8) saved to: {output_json_path}")
    if identifier:
        print(f"Extracted identifier: {identifier}")
    else:
        print("WARNING: Could not extract bill identifier")
    
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python restructure_bill_identifier_template8.py <extracted_json_file> [output_json_file]")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file.parent / f"{input_file.stem}_restructured.json"
    
    if not input_file.exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)
    
    restructure_bill_identifier_template8_json(input_file, output_file)

