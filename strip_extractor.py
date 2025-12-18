"""
Strip-based extraction utilities for bill_summary_section.pdf.

Strategy:
- Divide the cropped bill summary PDF into horizontal strips based on a
  configurable row height.
- Extract text from each strip independently.
- Identify which field label is present in the strip.
- Parse the numeric value for that field.
"""

from __future__ import annotations

import io
import re
from typing import Dict, List, Optional, Tuple

import fitz  # PyMuPDF
import pdfplumber

from text_normalization import default_normalizer


# Known field patterns (label regex -> output key)
# Template 2 patterns (original)
FIELD_PATTERNS: Dict[str, str] = {
    r"بهای\s*انرژی": "بهای انرژی",
    r"ضرر\s*و?\s*زیان": "ضررو زیان",
    r"مبلغ\s*آبونمان": "مبلغ آبونمان",
    r"مابه\s*التفاوت\s*اجرای\s*مقررات": "مابه التفاوت اجرای مقررات",
    r"مابه\s*التفاوت\s*ماده\s*16": "مابه التفاوت ماده 16 جهش تولید",
    r"هزینه\s*سوخت\s*نیروگاهی": "هزینه سوخت نیروگاهی",
    r"مالیات\s*بر\s*ارزش\s*افزوده": "مالیات بر ارزش افزوده",
    r"عوارض\s*برق": "عوارض برق",
    r"بستانکاری\s*خرید\s*خارج\s*بازار": "بستانکاری خرید خارج بازار",
    r"تجاوز\s*از\s*قدرت": "تجاوز از قدرت",
}

# Template 6 patterns - all 23 fields
# These patterns are more flexible to handle garbled/partial text
FIELD_PATTERNS_TEMPLATE6: Dict[str, str] = {
    # Energy price - first item
    r"بها[یي]\s*انرژ[یي]": "بهای انرژی",
    # Power price
    r"بها[یي]\s*قدرت": "بهای قدرت",
    # Implementation difference
    r"مابه\s*التفاوت\s*اجرا[یي]": "مابه التفاوت اجرای",
    # Subscription fee
    r"آبونمان": "آبونمان",
    # Branch tariff difference
    r"تفاوت\s*تعرفه\s*انشعاب": "تفاوت تعرفه انشعاب",
    # Power exceeded
    r"تجاوز\s*از\s*قدرت": "تجاوز از قدرت",
    # Peak season
    r"پ[یي]ک\s*فصل": "پیک فصل",
    # Reactive energy price
    r"بها[یي]\s*انرژ[یي]\s*راکت[یي]و": "بهای انرژی راکتیو",
    # License expiration
    r"انقضا[یي]\s*پروانه": "انقضای پروانه",
    # Note 14 amount
    r"(?:مبلغ\s*)?تبصره\s*[یي]?\s*14": "مبلغ تبصره ی 14",
    # Article 16 energy difference
    r"(?:مابه\s*التفاوت\s*)?(?:انرژ[یي]\s*)?مشمول\s*ماده\s*16": "مابه التفاوت انرژی مشمول ماده 16",
    # Cooperation bonus
    r"پاداش\s*همکار[یي]": "پاداش همکاری",
    # Off-market purchase credit (can be negative)
    r"بستانکار[یي]\s*خر[یي]د\s*خارج\s*بازار": "بستانکاری خرید خارج بازار",
    # Electricity price adjustment
    r"تعد[یي]ل\s*بها[یي]\s*برق": "تعدیل بهای برق",
    # Insurance
    r"ب[یي]مه(?!\s*عموم)": "بیمه",
    # Public insurance
    r"ب[یي]مه\s*عموم[یي]": "بیمه عمومی",
    # Electricity charges
    r"عوارض\s*برق": "عوارض برق",
    # VAT
    r"مال[یي]ات\s*(?:بر\s*)?ارزش\s*افزوده": "مالیات بر ارزش افزوده",
    # Penalty
    r"وجه\s*التزام": "وجه التزام",
    # Period electricity price
    r"بها[یي]\s*برق\s*دوره": "بهای برق دوره",
    # Debt/Credit (can be negative)
    r"بدهکار[یي]\s*/?\s*بستانکار[یي]": "بدهکاری / بستانکاری",
    # Thousand Rial deduction
    r"کسر\s*هزار\s*ر[یي]ال": "کسر هزار ریال",
    # Payable amount - last item
    r"مبلغ\s*قابل\s*پرداخت": "مبلغ قابل پرداخت",
}


def convert_persian_digits(text: str) -> str:
    """Convert Persian/Arabic-Indic digits to ASCII digits."""
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    arabic_indic_digits = "٠١٢٣٤٥٦٧٨٩"
    ascii_digits = "0123456789"

    result = text
    for i, p in enumerate(persian_digits):
        result = result.replace(p, ascii_digits[i])
    for i, a in enumerate(arabic_indic_digits):
        result = result.replace(a, ascii_digits[i])
    return result


def collapse_spaced_number(text: str) -> str:
    """Collapse spaced digits and normalize commas."""
    result = re.sub(r"\s*,\s*", ",", text)
    for _ in range(10):
        prev = result
        result = re.sub(r"(\d)\s+(\d)", r"\1\2", result)
        if result == prev:
            break
    return result


def parse_value(text: str) -> Optional[float]:
    """Extract numeric value from text, handling commas and trailing minus."""
    if not text:
        return None
    txt = convert_persian_digits(text)
    txt = collapse_spaced_number(txt)
    matches = re.findall(r"-?\d{1,3}(?:,\d{3})*(?:-\b)?|-?\d{4,}", txt)
    if not matches:
        return None
    candidates = []
    for m in matches:
        num_txt = m.replace(",", "").replace("٬", "").replace("،", "").replace(" ", "")
        is_negative = False
        if num_txt.endswith("-"):
            is_negative = True
            num_txt = num_txt[:-1]
        try:
            val = float(num_txt)
            if is_negative or num_txt.startswith("-"):
                val = -val
            candidates.append(val)
        except ValueError:
            continue
    if not candidates:
        return None
    # choose the number with the largest absolute value
    candidates.sort(key=lambda v: abs(v), reverse=True)
    return candidates[0]


def extract_text_from_bytes(pdf_bytes: bytes) -> str:
    """Extract normalized text from in-memory PDF."""
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        if not pdf.pages:
            return ""
        page = pdf.pages[0]
        text = page.extract_text() or ""
        if not text:
            text = page.extract_text(layout=True) or ""
    if text:
        return default_normalizer.normalize(text, apply_bidi=True)
    return ""


def identify_field(text: str) -> Optional[str]:
    """Match text against known field patterns (Template 2)."""
    for pattern, name in FIELD_PATTERNS.items():
        if re.search(pattern, text, flags=re.IGNORECASE):
            return name
    return None


def identify_field_template6(text: str) -> Optional[str]:
    """Match text against Template 6 field patterns."""
    for pattern, name in FIELD_PATTERNS_TEMPLATE6.items():
        if re.search(pattern, text, flags=re.IGNORECASE):
            return name
    return None


def crop_strip_to_bytes(pdf_path: str, y0: float, y1: float, x_margin: float = 5.0) -> bytes:
    """
    Crop a horizontal strip and return PDF bytes.
    Uses the page cropbox; adds horizontal margins.
    """
    src = fitz.open(pdf_path)
    try:
        page = src[0]
        bbox = page.cropbox if page.cropbox != page.mediabox else page.mediabox
        x0 = bbox.x0 + max(x_margin, 0)
        x1 = bbox.x1 - max(x_margin, 0)
        if x1 <= x0:
            x1 = x0 + 1  # minimal width safeguard
        rect = fitz.Rect(x0, y0, x1, y1)
        if rect.width <= 0 or rect.height <= 0:
            return b""

        # Create a new document with only the clipped region
        out_doc = fitz.open()
        out_page = out_doc.new_page(width=rect.width, height=rect.height)
        out_page.show_pdf_page(out_page.rect, src, 0, clip=rect)
        buf = out_doc.write()
        out_doc.close()
        return buf
    finally:
        src.close()


def extract_bill_summary_strips(
    pdf_path: str,
    row_height: float = 11.0,
    min_strip_height: float = 8.0,
    x_margin: float = 5.0,
) -> Dict[str, float]:
    """
    Extract bill summary fields using strip-based approach.

    Args:
        pdf_path: path to bill_summary_section.pdf
        row_height: target strip height in points
        min_strip_height: minimum height for last strip
        x_margin: horizontal margin to avoid clipping text
    """
    results: Dict[str, float] = {}

    doc = fitz.open(pdf_path)
    pl_doc = pdfplumber.open(pdf_path)
    try:
        page = doc[0]
        pl_page = pl_doc.pages[0]
        bbox = page.cropbox if page.cropbox != page.mediabox else page.mediabox
        height = bbox.y1 - bbox.y0
        if height <= 0:
            return results

        # number of strips based on row height
        n_strips = max(1, int(round(height / row_height)))

        for i in range(n_strips):
            y0 = bbox.y0 + i * row_height
            y1 = min(y0 + row_height, bbox.y1)
            if y1 - y0 < min_strip_height:
                continue

            rect = fitz.Rect(bbox.x0 + x_margin, y0, bbox.x1 - x_margin, y1)
            if rect.width <= 0 or rect.height <= 0:
                continue

            # Try pdfplumber crop first (better for text extraction)
            region = pl_page.crop((rect.x0, rect.y0, rect.x1, rect.y1))
            text = region.extract_text() or ""
            if not text:
                # fallback to fitz text extraction
                text = page.get_text("text", clip=rect) or ""

            if not text.strip():
                continue

            text = default_normalizer.normalize(text, apply_bidi=True)
            lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

            for line in lines:
                field = identify_field(line)
                if not field:
                    continue
                value = parse_value(line)
                if value is None:
                    continue
                if field not in results:
                    results[field] = value
    finally:
        doc.close()
        pl_doc.close()

    return results


def extract_bill_summary_strips_template6(
    pdf_path: str,
    row_height: float = 17.0,
    min_strip_height: float = 8.0,
    x_margin: float = 5.0,
) -> Dict[str, Optional[float]]:
    """
    Extract bill summary fields from Template 6 using the pre-extracted JSON data.
    
    This function looks for a corresponding JSON file (bill_summary_section.json)
    that was generated during the initial extraction phase. It uses the table
    rows from that JSON to assign values to fields by position.
    
    If no JSON file is found, falls back to direct PDF extraction.

    Args:
        pdf_path: path to bill_summary_section.pdf
        
    Returns:
        Dictionary with all 23 fields (None for fields not found)
    """
    return extract_bill_summary_from_json_template6(pdf_path)


def extract_bill_summary_from_json_template6(
    pdf_path: str,
) -> Dict[str, Optional[float]]:
    """
    Extract bill summary fields from the PDF using position-based extraction.
    
    Uses fitz to extract text elements with their positions, then sorts by
    Y coordinate to get values in the correct row order.
    """
    import os
    import json
    
    # Initialize result with all 23 fields as None
    results: Dict[str, Optional[float]] = {
        "بهای انرژی": None,
        "بهای قدرت": None,
        "مابه التفاوت اجرای": None,
        "آبونمان": None,
        "تفاوت تعرفه انشعاب": None,
        "تجاوز از قدرت": None,
        "پیک فصل": None,
        "بهای انرژی راکتیو": None,
        "انقضای پروانه": None,
        "مبلغ تبصره ی 14": None,
        "مابه التفاوت انرژی مشمول ماده 16": None,
        "پاداش همکاری": None,
        "بستانکاری خرید خارج بازار": None,
        "تعدیل بهای برق": None,
        "بیمه": None,
        "بیمه عمومی": None,
        "عوارض برق": None,
        "مالیات بر ارزش افزوده": None,
        "وجه التزام": None,
        "بهای برق دوره": None,
        "بدهکاری / بستانکاری": None,
        "کسر هزار ریال": None,
        "مبلغ قابل پرداخت": None,
    }
    
    # Expected order of fields in Template 6 bill summary (top to bottom)
    FIELD_ORDER = [
        "بهای انرژی",
        "بهای قدرت",
        "مابه التفاوت اجرای",
        "آبونمان",
        "تفاوت تعرفه انشعاب",
        "تجاوز از قدرت",
        "پیک فصل",
        "بهای انرژی راکتیو",
        "انقضای پروانه",
        "مبلغ تبصره ی 14",
        "مابه التفاوت انرژی مشمول ماده 16",
        "پاداش همکاری",
        "بستانکاری خرید خارج بازار",
        "تعدیل بهای برق",
        "بیمه",
        "بیمه عمومی",
        "عوارض برق",
        "مالیات بر ارزش افزوده",
        "وجه التزام",
        "بهای برق دوره",
        "بدهکاری / بستانکاری",
        "کسر هزار ریال",
        "مبلغ قابل پرداخت",
    ]
    
    # Fields that can be negative
    NEGATIVE_FIELDS = {"بستانکاری خرید خارج بازار", "بدهکاری / بستانکاری", "کسر هزار ریال"}

    try:
        # Use fitz to extract text with positions
        doc = fitz.open(pdf_path)
        try:
            page = doc[0]
            
            # Get page dimensions and find the value column (leftmost)
            # Template 6 has values on the left (~x < 70) in the cropped PDF
            
            # Get text dictionary with positions
            text_dict = page.get_text("dict")
            
            # First pass: collect text spans - separate primary values (x < 10) and extensions (10 < x < 40)
            primary_spans = []  # List of (y_pos, x_pos, text) for leftmost values
            extension_spans = []  # List of (y_pos, x_pos, text) for split value continuations
            
            # Helper to check if text is a date
            def is_date(text):
                return bool(re.match(r'^\d{4}/\d{1,2}/\d{1,2}$', text.strip()))
            
            for block in text_dict.get("blocks", []):
                if block.get("type") != 0:  # Only text blocks
                    continue
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span.get("text", "").strip()
                        if not text:
                            continue
                        
                        bbox = span.get("bbox", [0, 0, 0, 0])
                        x0, y0, x1, y1 = bbox
                        
                        # Skip rows with y < 15 (header noise)
                        if y0 < 15:
                            continue
                        
                        # Collect primary spans (leftmost value column)
                        if x0 < 10:
                            primary_spans.append((y0, x0, text))
                        # Collect extension spans (for split values like "6,768," + "امور 544,206")
                        elif x0 < 40 and any(c.isdigit() for c in text):
                            extension_spans.append((y0, x0, text))
            
            # Group primary spans by row
            row_height = 15
            row_spans = {}  # y_key -> list of (x, text)
            
            for y, x, text in primary_spans:
                y_key = round(y / row_height) * row_height
                if y_key not in row_spans:
                    row_spans[y_key] = []
                row_spans[y_key].append((x, text))
            
            # Add extension spans to matching rows
            for y, x, text in extension_spans:
                y_key = round(y / row_height) * row_height
                # Only add if there's already a primary span in this row
                if y_key in row_spans:
                    row_spans[y_key].append((x, text))
            
            # For each row, combine spans and extract number
            row_values = []
            
            for y_key in sorted(row_spans.keys()):
                row_items = row_spans[y_key]
                # Sort by x position (left to right)
                row_items.sort(key=lambda item: item[0])
                
                # Combine text from value column spans
                combined_text = ' '.join(t for _, t in row_items)
                
                # Skip dates
                if is_date(combined_text.split()[0] if combined_text.split() else ''):
                    continue
                
                # Check for trailing dash (negative indicator)
                has_dash = combined_text.strip().endswith('-')
                
                # Clean contamination
                clean_text = combined_text
                clean_text = re.sub(r'روما', '', clean_text)
                clean_text = re.sub(r'امور', '', clean_text)
                
                # Extract just digits
                digits_only = re.sub(r'[^\d-]', '', clean_text)
                
                # Ensure minus is only at start
                if '-' in digits_only:
                    digits_only = '-' + digits_only.replace('-', '')
                
                # Skip empty
                if not digits_only or digits_only == '-':
                    continue
                
                # Convert to number
                try:
                    val = float(digits_only)
                    if has_dash and val > 0:
                        val = -val
                    row_values.append(val)
                except ValueError:
                    continue
            
            # Assign values to fields by position
            for i, val in enumerate(row_values):
                if i >= len(FIELD_ORDER):
                    break
                
                field = FIELD_ORDER[i]
                results[field] = val
                
        finally:
            doc.close()
                    
    except Exception as e:
        print(f"Error in extract_bill_summary_from_json_template6: {e}")
        import traceback
        traceback.print_exc()

    return results


def _extract_from_pdf_directly(
    pdf_path: str,
    results: Dict[str, Optional[float]],
    field_order: list,
    negative_fields: set
) -> Dict[str, Optional[float]]:
    """Fallback to direct PDF extraction if JSON is not available."""
    try:
        doc = fitz.open(pdf_path)
        try:
            page = doc[0]
            full_text = page.get_text()
            
            # Clean contamination
            for _ in range(5):
                prev = full_text
                full_text = re.sub(r'(\d+),?امور\s*(\d)', r'\1\2', full_text)
                full_text = re.sub(r'(\d+)\s*روما\s*(\d)', r'\1\2', full_text)
                full_text = re.sub(r'(\d)\s+(\d)', r'\1\2', full_text)
                if full_text == prev:
                    break
            
            # Helper to check if text is a date
            def is_date(text):
                return bool(re.match(r'^\d{4}/\d{1,2}/\d{1,2}$', text.strip()))
            
            # Extract numbers line by line
            lines = full_text.split('\n')
            row_values = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Skip dates
                if is_date(line):
                    continue
                
                # Check for trailing dash
                has_dash = line.endswith('-')
                
                # Find number in line
                number_match = re.search(r'-?\d{1,3}(?:,\d{3})+|-?\d{4,}', line)
                if number_match:
                    val = parse_value(number_match.group())
                    if val is not None:
                        if has_dash and val > 0:
                            val = -val
                        row_values.append(val)
            
            # Assign values to fields by position
            for i, val in enumerate(row_values):
                if i >= len(field_order):
                    break
                results[field_order[i]] = val
                
        finally:
            doc.close()
            
    except Exception as e:
        print(f"Error in _extract_from_pdf_directly: {e}")
    
    return results
