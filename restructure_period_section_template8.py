"""Restructure period section for Template 8."""
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


def extract_period_info(text: str) -> dict:
    """Extract period information from text.

    Template 8 period data (from/to dates, days, period/year) is sometimes
    present in neighbouring sections (e.g. bill identifier crop). This helper
    focuses purely on recognising the patterns, independent of labels.
    """
    normalized_text = convert_persian_digits(text or "")

    result = {
        "from_date": None,
        "to_date": None,
        "number_of_days": None,
        "period_year": None,
    }

    # Collect all date-like patterns
    dates = re.findall(r"\d{4}/\d{2}/\d{2}", normalized_text)
    # Expect: from_date, to_date, maybe invoice/server date; we take the first two
    if len(dates) >= 1:
        result["from_date"] = dates[0]
    if len(dates) >= 2:
        result["to_date"] = dates[1]

    # Number of days: look for a small integer near keywords or simply the
    # first 1–3 digit number after the dates
    # Try labelled pattern first (تعداد روز دوره / تعداد روز)
    days_match = re.search(r"تعداد\s+روز(?:\s+دوره)?\s*[:\-]?\s*(\d{1,3})", normalized_text)
    if days_match:
        try:
            result["number_of_days"] = int(days_match.group(1))
        except ValueError:
            result["number_of_days"] = None
    else:
        # Fallback: find 1–3 digit numbers and pick a reasonable candidate (e.g. 31)
        small_nums = [int(m) for m in re.findall(r"\b(\d{1,3})\b", normalized_text) if 1 <= int(m) <= 366]
        if small_nums:
            result["number_of_days"] = small_nums[0]

    # Period/year: look for YYYY/MM that matches from_date month/year
    period_candidates = re.findall(r"\d{4}/\d{2}", normalized_text)
    if period_candidates:
        if result["from_date"] and result["from_date"][:7] in period_candidates:
            result["period_year"] = result["from_date"][:7]
        else:
            result["period_year"] = period_candidates[0]

    return result


def restructure_period_section_template8_json(extracted_json_path, output_json_path):
    """Restructure extracted JSON to include period section data for Template 8."""
    with open(extracted_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    text = data.get('text', '')

    # Extract period info from this crop
    period_data = extract_period_info(text)

    # Fallback: if key fields are missing, try reading from the
    # bill_identifier_section JSON, which frequently contains the full
    # period block for Template 8.
    if not period_data.get("from_date") or not period_data.get("to_date"):
        try:
            extracted_path = Path(extracted_json_path)
            stem = extracted_path.stem.replace("period_section", "bill_identifier_section")
            sibling_path = extracted_path.parent / f"{stem}.json"
            if sibling_path.exists():
                with open(sibling_path, "r", encoding="utf-8") as fb:
                    sibling_data = json.load(fb)

                # Combine text and table cells from bill_identifier_section
                sibling_parts: list[str] = [sibling_data.get("text", "")]
                sibling_table = sibling_data.get("table") or {}
                sibling_rows = sibling_table.get("rows") or []
                for row in sibling_rows:
                    for cell in row:
                        if isinstance(cell, str):
                            sibling_parts.append(cell)
                sibling_text = "\n".join(sibling_parts)

                sibling_period = extract_period_info(sibling_text)

                # Only overwrite missing fields
                for key, value in sibling_period.items():
                    if not period_data.get(key) and value:
                        period_data[key] = value
        except Exception:
            # Non-fatal; keep whatever we already extracted
            pass
    
    # Build restructured data
    result = {
        "period_section": period_data
    }
    
    # Save restructured JSON
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Restructured period section (Template 8) saved to: {output_json_path}")
    print(f"Extracted period info: {period_data}")
    
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python restructure_period_section_template8.py <extracted_json_file> [output_json_file]")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file.parent / f"{input_file.stem}_restructured.json"
    
    if not input_file.exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)
    
    restructure_period_section_template8_json(input_file, output_file)

