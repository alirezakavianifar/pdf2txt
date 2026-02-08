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

    # Number of days: prioritize calculation from dates (most reliable when text has CID codes)
    # Then try labelled pattern, then fallback to text extraction
    calculated_days = None
    if result["from_date"] and result["to_date"]:
            try:
                from_parts = result["from_date"].split("/")
                to_parts = result["to_date"].split("/")
                if len(from_parts) == 3 and len(to_parts) == 3:
                    from_year, from_month, from_day = int(from_parts[0]), int(from_parts[1]), int(from_parts[2])
                    to_year, to_month, to_day = int(to_parts[0]), int(to_parts[1]), int(to_parts[2])
                    
                    # Calculate day difference
                    # Persian calendar: months have 29-31 days, years have 365-366 days
                    # For same year and consecutive months, the difference is typically 28-31 days
                    if from_year == to_year:
                        if from_month == to_month:
                            # Same month: difference is just the day difference
                            calculated_days = to_day - from_day
                        else:
                            # Different months: approximate using 30 days per month
                            # This works well for consecutive months
                            month_diff = to_month - from_month
                            if month_diff == 1:
                                # Consecutive months: typically 28-31 days
                                # Use 30 as base, adjust for day difference
                                calculated_days = 30 + (to_day - from_day)
                            else:
                                # Multiple months apart: use approximation
                                calculated_days = month_diff * 30 + (to_day - from_day)
                    else:
                        # Different years: use approximation
                        year_diff = to_year - from_year
                        month_diff = to_month - from_month
                        calculated_days = year_diff * 365 + month_diff * 30 + (to_day - from_day)
                    
                    # If calculated days is reasonable (between 1 and 366), keep it
                    # Otherwise reset to None so we try other methods
                    if not (1 <= calculated_days <= 366):
                        calculated_days = None
            except (ValueError, IndexError):
                pass
    
    # Use calculated days if available
    if calculated_days is not None:
        result["number_of_days"] = calculated_days
    else:
        # Try labelled pattern (تعداد روز دوره / تعداد روز)
        days_match = re.search(r"تعداد\s+روز(?:\s+دوره)?\s*[:\-]?\s*(\d{1,3})", normalized_text)
        if days_match:
            try:
                result["number_of_days"] = int(days_match.group(1))
            except ValueError:
                pass
        
        # If still not found, look for reasonable period day numbers (28-31)
        # These are common for monthly billing periods
        if result["number_of_days"] is None:
            period_day_match = re.search(r"\b(2[89]|30|31)\b", normalized_text)
            if period_day_match:
                try:
                    result["number_of_days"] = int(period_day_match.group(1))
                except ValueError:
                    pass
        
        # Last fallback: find 1–3 digit numbers and pick a reasonable candidate
        # But prefer numbers in the 28-31 range (typical monthly periods)
        if result["number_of_days"] is None:
            small_nums = [int(m) for m in re.findall(r"\b(\d{1,3})\b", normalized_text) if 1 <= int(m) <= 366]
            if small_nums:
                # Prefer numbers in the 28-31 range
                preferred = [n for n in small_nums if 28 <= n <= 31]
                if preferred:
                    result["number_of_days"] = preferred[0]
                else:
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
    
    # If number_of_days is still missing, try extracting from geometry cells
    # The number might be in a cell that wasn't captured in the text field
    if period_data.get("number_of_days") is None:
        geometry = data.get('geometry', {})
        cells = geometry.get('cells', [])
        
        # Look for cells containing reasonable period day numbers (28-31)
        for cell in cells:
            cell_text = cell.get('text', '')
            if cell_text:
                normalized_cell = convert_persian_digits(cell_text)
                # Look for standalone numbers 28-31 (common for monthly periods)
                period_day_match = re.search(r'\b(2[89]|30|31)\b', normalized_cell)
                if period_day_match:
                    try:
                        period_data["number_of_days"] = int(period_day_match.group(1))
                        break
                    except ValueError:
                        continue

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

