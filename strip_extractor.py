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
    """Match text against known field patterns."""
    for pattern, name in FIELD_PATTERNS.items():
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
