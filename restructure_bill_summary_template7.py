"""Restructure bill summary section for Template 7."""
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
    
    # Check for negative sign (can be at end with -)
    is_negative = text.endswith('-') or text.startswith('-')
    if text.endswith('-'):
        text = text[:-1]
    elif text.startswith('-'):
        text = text[1:]
    
    if not text or text == '.':
        return None
    
    try:
        value = float(text)
        return -value if is_negative else value
    except ValueError:
        return None


def extract_bill_summary(text):
    """Extract financial summary items from text.
    
    Expected fields for Template 7:
    - آبونمان (Subscription Fee): 143,481
    - هزینه سوخت نیروگاهی (Power Plant Fuel Cost): 153,960,087
    - بهای انرژی راکتیو (Reactive Energy Price): 0
    - بهای فصل (Seasonal Price): 0
    - ما به التفاوت اجرای مقررات (Regulation Implementation Difference): 1,167,116,193
    - بهای برق تامین شده به نیابت (Electricity Price Supplied by Proxy): 2,601,295.32
    - بستانکاری مازاد خرید انرژی (Credit for Excess Energy Purchase): 8,508,198- (negative)
    - مبلغ مابه التفاوت ماده 16 (سبز) (Article 16 Difference Amount - Green): 0
    - عوارض برق (Electricity Tariffs): 355,610,298
    - مالیات بر ارزش افزوده (Value Added Tax): 131,531,286
    - مبلغ بدهی ماده 3 (Article 3 Debt Amount): 1/24
    - بدهکار / بستانکار (Debtor/Creditor): 1,079,251,557
    - کسر هزار ریال (Thousand Rial Deduction): 796
    - مبلغ قابل پرداخت (Payable Amount): 2,881,706,000
    - مهلت پرداخت (Payment Deadline): (date)
    - مشمول قطع (Subject to Disconnection): (yes/no)
    """
    normalized_text = convert_persian_digits(text)
    
    result = {
        "آبونمان": None,
        "هزینه سوخت نیروگاهی": None,
        "بهای انرژی راکتیو": None,
        "بهای فصل": None,
        "ما به التفاوت اجرای مقررات": None,
        "بهای برق تامین شده به نیابت": None,
        "بستانکاری مازاد خرید انرژی": None,
        "مبلغ مابه التفاوت ماده 16 (سبز)": None,
        "عوارض برق": None,
        "مالیات بر ارزش افزوده": None,
        "مبلغ بدهی ماده 3": None,
        "بدهکار / بستانکار": None,
        "کسر هزار ریال": None,
        "مبلغ قابل پرداخت": None,
        "مهلت پرداخت": None,
        "مشمول قطع": None
    }
    
    lines = normalized_text.split('\n')
    full_text = ' '.join(lines)
    
    # Extract each field - handle both label:value and label value patterns
    patterns = {
        "آبونمان": r'آبونمان\s*:?\s*([\d,]+)',
        "هزینه سوخت نیروگاهی": r'هزینه سوخت نیروگاهی\s*:?\s*([\d,]+)',
        "بهای انرژی راکتیو": r'بهای انرژی راکتیو\s*:?\s*([\d,]+)',
        "بهای فصل": r'بهای فصل\s*:?\s*([\d,]+)',
        "ما به التفاوت اجرای مقررات": r'ما\s*به?\s*التفاوت\s*اجرای\s*مقررات\s*:?\s*([\d,]+)',
        "بهای برق تامین شده به نیابت": r'بهای برق تامین شده به نیابت\s*:?\s*([\d,]+(?:\.\d+)?)',
        "بستانکاری مازاد خرید انرژی": r'بستانکاری مازاد خرید انرژی\s*:?\s*([\d,]+-?)',
        "مبلغ مابه التفاوت ماده 16 (سبز)": r'مبلغ\s*مابه\s*التفاوت\s*ماده\s*16[^\d]*\(?\s*سبز\s*\)?\s*:?\s*([\d,]+)',
        "عوارض برق": r'عوارض برق\s*:?\s*([\d,]+)',
        "مالیات بر ارزش افزوده": r'مالیات بر ارزش افزوده\s*:?\s*([\d,]+)',
        "مبلغ بدهی ماده 3": r'مبلغ\s*بدهی\s*ماده\s*3\s*:?\s*([\d/]+)',
        "بدهکار / بستانکار": r'بدهکار\s*/?\s*بستانکار\s*:?\s*([\d,]+-?)',
        "کسر هزار ریال": r'کسر هزار ریال\s*:?\s*([\d,]+)',
        "مبلغ قابل پرداخت": r'مبلغ قابل پرداخت\s*:?\s*([\d,]+)',
        "مهلت پرداخت": r'مهلت پرداخت\s*:?\s*(\d{4}/\d{2}/\d{2})',
        "مشمول قطع": r'مشمول قطع\s*:?\s*([^\n]+)'
    }
    
    for field, pattern in patterns.items():
        match = re.search(pattern, full_text)
        if match:
            if field in ["مهلت پرداخت", "مشمول قطع"]:
                result[field] = match.group(1).strip()
            elif field == "مبلغ بدهی ماده 3":
                result[field] = match.group(1).strip()
            else:
                result[field] = parse_number(match.group(1))
    
    return result


def restructure_bill_summary_template7_json(json_path: Path, output_path: Path):
    """Restructure extracted JSON to include bill summary data for Template 7."""
    print(f"Restructuring Bill Summary (Template 7) from {json_path}...")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        text = data.get('text', '')
        
        # Extract bill summary
        summary_data = extract_bill_summary(text)
        
        # Build restructured data
        result = {
            "خلاصه صورتحساب": summary_data
        }
        
        # Save restructured JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"  - Saved to {output_path}")
        extracted_count = sum(1 for v in summary_data.values() if v is not None)
        print(f"  - Extracted {extracted_count}/{len(summary_data)} summary items")
        
        return result
        
    except Exception as e:
        print(f"Error restructuring Bill Summary T7: {e}")
        import traceback
        traceback.print_exc()
        return None

