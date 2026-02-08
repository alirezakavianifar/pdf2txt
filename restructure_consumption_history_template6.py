"""Restructure consumption history section for Template 6.

This section extracts the مبالغ قابل پرداخت (Amounts Payable) table:
Columns: هزینه (Cost), مبلغ قابل پرداخت (Amount), شناسه قیض (Receipt ID), شناسه پرداخت (Payment ID).
Rows: انرژی (Energy), ترانزیت (Transit).
"""
import json
import re
from pathlib import Path


def convert_persian_digits(text):
    """Convert Persian/Arabic-Indic digits to regular digits."""
    persian_digits = '۰۱۲۳۴۵۶۷۸۹'
    arabic_indic_digits = '٠١٢٣٤٥٦٧٨٩'
    regular_digits = '0123456789'
    result = str(text or "")
    for i, persian in enumerate(persian_digits):
        result = result.replace(persian, regular_digits[i])
    for i, arabic in enumerate(arabic_indic_digits):
        result = result.replace(arabic, regular_digits[i])
    return result


def parse_number(text):
    """Parse a number, removing commas and handling Persian digits."""
    if not text or text == '.' or (isinstance(text, str) and text.strip() == ''):
        return None
    text = convert_persian_digits(text)
    text = str(text).replace(',', '').replace('،', '').replace(' ', '').replace('.', '').strip()
    if not text or text == '.':
        return None
    try:
        return int(text)
    except ValueError:
        try:
            return float(text)
        except ValueError:
            return None


def _looks_like_amounts_payable_header(cells: list) -> bool:
    """Detect header row for مبالغ قابل پرداخت table."""
    joined = " ".join(str(c or "").strip() for c in cells)
    n = convert_persian_digits(joined)
    keywords = ["هزینه", "مبلغ قابل پرداخت", "شناسه قیض", "شناسه پرداخت", "مبالغ قابل پرداخت"]
    if any(k in n for k in keywords):
        return True
    # Skip garbled header like "انرژی مشم کد اقتصادی" (not a data row)
    if "انرژی مشم" in joined and "کد اقتصادی" in joined:
        return True
    return False


def _parse_amounts_payable_row(cells: list, cost_hint: str | None = None) -> dict | None:
    """
    Parse one row of مبالغ قابل پرداخت from a list of cell values.
    Expects cost (انرژی/ترانزیت), amount, receipt_id, payment_id (order may vary by RTL).
    If cost_hint is set (انرژی/ترانزیت), use it when row has no cost label but has amount/IDs.
    """
    if not cells:
        return None
    row_text = " ".join(str(c or "").strip() for c in cells if str(c or "").strip())
    normalized = convert_persian_digits(row_text)

    # Detect cost type from text or hint
    cost = None
    if "انرژی" in row_text or "انرژي" in row_text:
        cost = "انرژی"
    elif "ترانزیت" in row_text or "ترانزيت" in row_text:
        cost = "ترانزیت"
    if not cost:
        cost = cost_hint

    # All digit sequences: long ones are IDs or amount
    digit_seqs = re.findall(r'\d[\d,\.]*', normalized)
    numbers = []
    ids = []
    for seq in digit_seqs:
        cleaned = seq.replace(',', '').replace('.', '')
        if not cleaned.isdigit():
            continue
        num = int(cleaned)
        if 10 <= len(cleaned) <= 13:
            ids.append(cleaned)
        else:
            numbers.append(num)

    # Amount is typically the large one (millions); IDs are 11-13 digits
    amount = max(numbers) if numbers else None
    receipt_id = None
    payment_id = None
    if len(ids) >= 2:
        receipt_id = ids[0]
        payment_id = ids[1]
    elif len(ids) == 1:
        receipt_id = ids[0]

    # Require at least amount or cost (for hint-based rows we need amount or IDs)
    if not cost and not amount and not (receipt_id or payment_id):
        return None
    if cost or amount or receipt_id or payment_id:
        return {
            "هزینه": cost or "",
            "مبلغ قابل پرداخت": amount,
            "شناسه قیض": receipt_id,
            "شناسه پرداخت": payment_id,
        }
    return None


def _parse_amounts_payable_from_text(text: str) -> list:
    """Parse مبالغ قابل پرداخت rows from plain text lines."""
    normalized = convert_persian_digits(text or "")
    lines = [ln.strip() for ln in normalized.split('\n') if ln.strip()]
    rows = []
    for line in lines:
        if "انرژی" not in line and "انرژي" not in line and "ترانزیت" not in line and "ترانزيت" not in line:
            continue
        tokens = re.split(r'\s+', line)
        row = _parse_amounts_payable_row(tokens)
        if row:
            rows.append(row)
    return rows


def _parse_amounts_payable_from_geometry(cells: list) -> list:
    """Parse مبالغ قابل پرداخت from geometry.cells: find rows with انرژی/ترانزیت and extract amount/IDs."""
    if not cells:
        return []
    # Group by row
    by_row = {}
    for c in cells:
        r, col = c.get("row", 0), c.get("col", 0)
        text = (c.get("text") or "").strip()
        if r not in by_row:
            by_row[r] = {}
        by_row[r][col] = text
    rows_out = []
    for r in sorted(by_row.keys()):
        row_cells = by_row[r]
        # Build a single line for this row (RTL: high col first)
        parts = [row_cells[col] for col in sorted(row_cells.keys(), reverse=True) if row_cells[col]]
        line = " ".join(parts)
        if not line:
            continue
        # Cost label: look for انرژی or ترانزیت (allow "انرژی مشم" -> treat as انرژی)
        cost = None
        if "انرژی" in line:
            cost = "انرژی"
        elif "ترانزیت" in line or "ترانزيت" in line:
            cost = "ترانزیت"
        if not cost:
            continue
        parsed = _parse_amounts_payable_row(parts)
        if parsed:
            rows_out.append(parsed)
    return rows_out


def _parse_amounts_payable_table(text: str, table_data: dict | None, geometry: dict | None = None) -> dict:
    """
    Extract مبالغ قابل پرداخت table (Amounts Payable).
    Returns {"مبالغ قابل پرداخت": {"rows": [{"هزینه", "مبلغ قابل پرداخت", "شناسه قیض", "شناسه پرداخت"}, ...]}}.
    """
    result = {"مبالغ قابل پرداخت": {"rows": []}}

    if table_data and table_data.get("rows"):
        candidate_rows = list(table_data.get("rows", []))
        headers = table_data.get("headers") or []
        if headers and not _looks_like_amounts_payable_header(headers):
            candidate_rows.insert(0, headers)
        cost_order = ["انرژی", "ترانزیت"]
        data_row_index = 0
        for row in candidate_rows:
            if not row or not any(str(c or "").strip() for c in row):
                continue
            if _looks_like_amounts_payable_header(row):
                continue
            cells = [str(c or "").strip() for c in row]
            parsed = _parse_amounts_payable_row(cells)
            if not parsed and data_row_index < len(cost_order):
                parsed = _parse_amounts_payable_row(cells, cost_hint=cost_order[data_row_index])
            if not parsed:
                continue
            # Only count rows with meaningful amount (>= 100k) or IDs as انرژی/ترانزیت
            amount = parsed.get("مبلغ قابل پرداخت") or 0
            has_ids = parsed.get("شناسه قیض") or parsed.get("شناسه پرداخت")
            if amount < 100_000 and not has_ids:
                continue
            if not parsed.get("هزینه") and data_row_index < len(cost_order):
                parsed["هزینه"] = cost_order[data_row_index]
            result["مبالغ قابل پرداخت"]["rows"].append(parsed)
            data_row_index += 1

    if not result["مبالغ قابل پرداخت"]["rows"]:
        result["مبالغ قابل پرداخت"]["rows"] = _parse_amounts_payable_from_text(text)

    if not result["مبالغ قابل پرداخت"]["rows"] and geometry and geometry.get("cells"):
        from_geom = _parse_amounts_payable_from_geometry(geometry["cells"])
        # Keep only rows that look like real amounts payable (large amount or has IDs)
        result["مبالغ قابل پرداخت"]["rows"] = [
            r for r in from_geom
            if (r.get("مبلغ قابل پرداخت") or 0) >= 100_000 or r.get("شناسه قیض") or r.get("شناسه پرداخت")
        ]

    return result


def restructure_consumption_history_template6_json(json_path: Path, output_path: Path):
    """Restructure extracted JSON to مبالغ قابل پرداخت (Amounts Payable) for Template 6."""
    print(f"Restructuring Consumption History (Template 6) from {json_path}...")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        text = data.get('text', '')
        table_data = data.get('table', {})
        geometry = data.get('geometry', {})

        result = _parse_amounts_payable_table(text, table_data, geometry)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        row_count = len(result["مبالغ قابل پرداخت"]["rows"])
        print(f"  - Saved to {output_path}")
        print(f"  - Extracted {row_count} amounts payable rows")
        return result
    except Exception as e:
        print(f"Error restructuring Consumption History T6: {e}")
        import traceback
        traceback.print_exc()
        return None
