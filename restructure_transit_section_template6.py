"""Restructure transit section for Template 6."""
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


def parse_number(text):
    """Parse a number, removing commas and handling Persian digits."""
    if not text or text == '.' or text.strip() == '':
        return None
    
    text = convert_persian_digits(text)
    # Remove commas used as thousand separators
    text = text.replace(',', '').replace(' ', '').strip()
    
    if not text or text == '.':
        return None
    
    try:
        return int(text)
    except ValueError:
        return None


def normalize_reversed_thousands(text: str) -> str:
    """See Template 6 bidi/noise notes (e.g. '200 روما,1' -> '1,200')."""
    if not text:
        return ""
    t = convert_persian_digits(text)
    t = t.replace("روما", " ")
    pattern = re.compile(r'(\d{1,3})\s*[^0-9,]{1,10},\s*(\d{1,3})')
    prev = None
    while prev != t:
        prev = t
        t = pattern.sub(r'\2,\1', t)
    return t


def _extract_currency_amounts(value: str) -> list[int]:
    """
    Extract currency-like integer amounts from a noisy cell.

    Handles common Template-6 OCR/ordering artifacts, including cases where a single
    amount is split into two tokens like: "2,000 روما4,63" which should be "4,632,000".
    """
    if not value:
        return []
    t = convert_persian_digits(str(value))
    t = t.replace("،", ",")  # Arabic comma
    t = t.replace("روما", " ")  # bidi noise (often reversed 'امور')
    t = normalize_reversed_thousands(t)

    tokens = re.findall(r"\d[\d,]*", t)
    if not tokens:
        return []

    out: list[int] = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        # Try to merge two adjacent tokens that are actually one big number split by OCR/bidi.
        if i + 1 < len(tokens):
            tok2 = tokens[i + 1]

            def is_thousands_chunk(s: str) -> bool:
                return bool(re.search(r",0{2,3}$", s))

            def is_short_comma_tail(s: str) -> bool:
                # e.g. "4,63" (missing a digit) or "12,4"
                return bool(re.search(r",\d{1,2}$", s))

            merged_val = None
            if is_thousands_chunk(tok) and is_short_comma_tail(tok2):
                merged_digits = tok2.replace(",", "") + tok.replace(",", "")
                if merged_digits.isdigit():
                    merged_val = int(merged_digits)
            elif is_short_comma_tail(tok) and is_thousands_chunk(tok2):
                merged_digits = tok.replace(",", "") + tok2.replace(",", "")
                if merged_digits.isdigit():
                    merged_val = int(merged_digits)

            # Only accept merges that look like "money" (avoid turning two small numbers into junk)
            if merged_val is not None and merged_val >= 100_000:
                out.append(merged_val)
                i += 2
                continue

        v = parse_number(tok)
        if v is not None:
            out.append(v)
        i += 1

    return out


def extract_numbers_from_any(value: str) -> list[int]:
    """Extract integer-ish numbers from a noisy cell/text."""
    if not value:
        return []
    return _extract_currency_amounts(str(value))


def extract_transit_data(text, table_data=None):
    """Extract transit section data from text.
    
    Expected fields:
    - هزینه ترانزیت (Transit Cost): 449,844,512
    - ترانزیت فوق توزیع (Super Distribution Transit): 1,049,637,194
    - حق العمل کاری (Commission/Labor Fee)
    - تعدیل بهای برق (Electricity Price Adjustment)
    - مالیات بر ارزش افزوده (Value Added Tax): 149,948,170
    - بدهی گذشته (Past Debt)
    - وجه التزام (Penalty/Liquidated Damages)
    """
    normalized_text = convert_persian_digits(text)
    
    result = {
        "هزینه ترانزیت": None,
        "ترانزیت فوق توزیع": None,
        "حق العمل کاری": None,
        "تعدیل بهای برق": None,
        "مالیات بر ارزش افزوده": None,
        "بدهی گذشته": None,
        "وجه التزام": None,
        "مبلغ قابل پرداخت": None
    }
    
    lines = normalized_text.split('\n')
    full_text = ' '.join(lines)
    
    # --- Primary strategy: labelled extraction (ideal case) ---
    patterns = {
        "هزینه ترانزیت": r'هزینه ترانزیت[^\d]*(\d+(?:,\d+)*)',
        "ترانزیت فوق توزیع": r'ترانزیت فوق توزیع[^\d]*(\d+(?:,\d+)*)',
        "حق العمل کاری": r'حق العمل کاری[^\d]*(\d+(?:,\d+)*)',
        "تعدیل بهای برق": r'تعدیل بهای برق[^\d]*(\d+(?:,\d+)*)',
        "مالیات بر ارزش افزوده": r'مالیات بر ارزش افزوده[^\d]*(\d+(?:,\d+)*)',
        "بدهی گذشته": r'بدهی گذشته[^\d]*(\d+(?:,\d+)*)',
        "وجه التزام": r'وجه التزام[^\d]*(\d+(?:,\d+)*)',
        "مبلغ قابل پرداخت": r'مبلغ قابل پرداخت[^\d]*(\d+(?:,\d+)*)',
    }
    
    for field, pattern in patterns.items():
        match = re.search(pattern, full_text)
        if match:
            result[field] = parse_number(match.group(1))
    
    # --- Fallback strategy: numeric sequence without labels ---
    # In some Template 6 crops (like 6_transit_section.json), the visible labels
    # such as "هزینه ترانزیت" etc. are only present in the table image, and the
    # flattened `text` field contains just the numbers in order, e.g.:
    #
    #   449,844,512
    #   1,049,637,194
    #   0
    #   0
    #   149,948,170
    #   0
    #   0
    #
    # When the labelled extraction above fails and *no* fields are populated,
    # we interpret numbers positionally.
    #
    # IMPORTANT: Some Template 6 variants only show the *bottom* rows of the transit
    # table (e.g. adjustment/tax/past debt/penalty/payable). In those cases we should
    # NOT assign the first number to "هزینه ترانزیت". We'll infer which layout we have.
    if all(v is None for v in result.values()):
        # Collect all integer-like tokens (including comma-separated) from the text
        values = _extract_currency_amounts(full_text)
        # Heuristic: amounts in this table are large currency figures or zeros.
        # Filter out small non-zero numbers (e.g. distances like 150 کیلومتر).
        values = [v for v in values if v == 0 or v >= 1000]

        has_top_transit_labels = any(
            k in full_text for k in ["هزینه ترانزیت", "ترانزیت فوق توزیع", "حق العمل کاری"]
        )

        if has_top_transit_labels and len(values) >= 6:
            field_order = [
                "هزینه ترانزیت",
                "ترانزیت فوق توزیع",
                "حق العمل کاری",
                "تعدیل بهای برق",
                "مالیات بر ارزش افزوده",
                "بدهی گذشته",
                "وجه التزام",
                "مبلغ قابل پرداخت",
            ]
            for field, val in zip(field_order, values):
                result[field] = val
        else:
            # Bottom-only layout: most reliable mapping is VAT -> PastDebt -> Payable.
            if len(values) == 3:
                result["مالیات بر ارزش افزوده"] = values[0]
                result["بدهی گذشته"] = values[1]
                result["مبلغ قابل پرداخت"] = values[2]
            elif len(values) == 4:
                # Assume: [Adjustment, VAT, PastDebt, Payable] (penalty blank)
                result["تعدیل بهای برق"] = values[0]
                result["مالیات بر ارزش افزوده"] = values[1]
                result["بدهی گذشته"] = values[2]
                result["مبلغ قابل پرداخت"] = values[3]
            elif len(values) >= 5:
                tail_order = [
                    "تعدیل بهای برق",
                    "مالیات بر ارزش افزوده",
                    "بدهی گذشته",
                    "وجه التزام",
                    "مبلغ قابل پرداخت",
                ]
                for field, val in zip(tail_order, values[-len(tail_order):]):
                    result[field] = val
    
    # Final fallback: if text is too garbled/empty, use table rows (common in Template 6).
    if all(v is None for v in result.values()) and table_data and isinstance(table_data, dict) and table_data.get("rows"):
        values: list[int] = []
        for row in table_data["rows"]:
            # Prefer the first column (amount column), but extract from entire row if needed.
            if row and len(row) > 0:
                values.extend(extract_numbers_from_any(row[0]))
            else:
                continue
        # Remove tiny noise numbers; keep zeros and plausible amounts.
        values = [v for v in values if v == 0 or v >= 1000]

        # If we only got a few values, treat this as the bottom-only layout.
        if len(values) == 3:
            result["مالیات بر ارزش افزوده"] = values[0]
            result["بدهی گذشته"] = values[1]
            result["مبلغ قابل پرداخت"] = values[2]
        elif len(values) == 4:
            result["تعدیل بهای برق"] = values[0]
            result["مالیات بر ارزش افزوده"] = values[1]
            result["بدهی گذشته"] = values[2]
            result["مبلغ قابل پرداخت"] = values[3]
        else:
            field_order = [
                "هزینه ترانزیت",
                "ترانزیت فوق توزیع",
                "حق العمل کاری",
                "تعدیل بهای برق",
                "مالیات بر ارزش افزوده",
                "بدهی گذشته",
                "وجه التزام",
                "مبلغ قابل پرداخت",
            ]
            for field, val in zip(field_order, values):
                result[field] = val
    
    return result


def restructure_transit_section_template6_json(json_path: Path, output_path: Path):
    """Restructure extracted JSON to include transit section data for Template 6."""
    print(f"Restructuring Transit Section (Template 6) from {json_path}...")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        text = data.get('text', '')
        table_data = data.get('table', {})
        
        # Extract transit data
        transit_data = extract_transit_data(text, table_data=table_data)
        
        # Build restructured data
        result = {
            "صورتحساب ترانزیت": transit_data
        }
        
        # Save restructured JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"  - Saved to {output_path}")
        extracted_count = sum(1 for v in transit_data.values() if v is not None)
        print(f"  - Extracted {extracted_count}/{len(transit_data)} transit fields")
        
        return result
        
    except Exception as e:
        print(f"Error restructuring Transit Section T6: {e}")
        import traceback
        traceback.print_exc()
        return None

