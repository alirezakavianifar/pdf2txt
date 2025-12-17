
from pathlib import Path
import json
import re
from text_normalization import default_normalizer

def parse_number(text):
    """Parse a number string, removing commas and handling Persian format."""
    if not text:
        return None
    # Remove commas and spaces
    clean = text.replace(',', '').replace(' ', '').strip()
    try:
        return int(clean)
    except ValueError:
        try:
            return float(clean)
        except ValueError:
            return None

def restructure_transit_section_template4_json(json_path: Path, output_path: Path):
    """
    Restructures Transit Section (Template 4).
    Extracts: ترانزیت, از تاریخ, تا تاریخ, تاریخ صدور صورتحساب, 
    مالیات برارزش افزوده, روز دوره, بدهکار/بستانکار, کسر هزار ریال
    """
    print(f"Restructuring Transit (Template 4) from {json_path}...")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Don't apply BIDI - it reverses already correct RTL text
        text = default_normalizer.normalize(data.get("text", ""), apply_bidi=False)
        
        # Initialize result with Persian field names
        result = {
            "ترانزیت": None,
            "از_تاریخ": None,
            "تا_تاریخ": None,
            "تاریخ_صدور_صورتحساب": None,
            "مالیات_برارزش_افزوده": None,
            "روز_دوره": None,
            "بدهکار_بستانکار": None,
            "کسر_هزار_ریال": None
        }
        
        # Common number pattern (supports commas)
        num_pat = r'(-?\d[\d,]*)'
        
        # Extract ترانزیت (Transit amount)
        transit_match = re.search(rf'ترانزیت\s*:?\s*{num_pat}', text)
        if transit_match:
            result["ترانزیت"] = parse_number(transit_match.group(1))
        
        # Extract از تاریخ (From date)
        from_date_match = re.search(r'از\s*تاریخ\s*:?\s*(\d{4}/\d{2}/\d{2})', text)
        if not from_date_match:
            # Fallback: first date might be "از تاریخ"
            # Pattern: "تاریخ : 1404/04/01" (first occurrence)
            first_date_match = re.search(r'تاریخ\s*:?\s*(\d{4}/\d{2}/\d{2})', text)
            if first_date_match:
                result["از_تاریخ"] = first_date_match.group(1)
        else:
            result["از_تاریخ"] = from_date_match.group(1)
        
        # Extract تا تاریخ (To date)
        to_date_match = re.search(r'تا\s*تاریخ\s*:?\s*(\d{4}/\d{2}/\d{2})', text)
        if not to_date_match:
            # Fallback: second date might be "تا تاریخ"
            all_dates = re.findall(r'\d{4}/\d{2}/\d{2}', text)
            if len(all_dates) >= 2 and result["از_تاریخ"]:
                # Find the date that comes after "از تاریخ"
                for i, date in enumerate(all_dates):
                    if date == result["از_تاریخ"] and i + 1 < len(all_dates):
                        result["تا_تاریخ"] = all_dates[i + 1]
                        break
        else:
            result["تا_تاریخ"] = to_date_match.group(1)
        
        # Extract تاریخ صدور صورتحساب (Invoice issue date)
        issue_date_match = re.search(r'صدور\s*صورتحساب\s*:?\s*(\d{4}/\d{2}/\d{2})', text)
        if not issue_date_match:
            # Fallback: date after "صدور صورتحساب"
            issue_label_match = re.search(r'صدور\s*صورتحساب\s*:?', text)
            if issue_label_match:
                # Find date after this label
                remaining_text = text[issue_label_match.end():]
                date_after_label = re.search(r'(\d{4}/\d{2}/\d{2})', remaining_text)
                if date_after_label:
                    result["تاریخ_صدور_صورتحساب"] = date_after_label.group(1)
        else:
            result["تاریخ_صدور_صورتحساب"] = issue_date_match.group(1)
        
        # Extract مالیات برارزش افزوده (VAT)
        vat_match = re.search(rf'مالیات\s*برارزش\s*افزوده\s*:?\s*{num_pat}', text)
        if vat_match:
            result["مالیات_برارزش_افزوده"] = parse_number(vat_match.group(1))
        
        # Extract روز دوره (Period days)
        days_match = re.search(r'روز\s*دوره\s*:?\s*(\d+)', text)
        if days_match:
            result["روز_دوره"] = int(days_match.group(1))
        
        # Extract بدهکار/بستانکار (Debt/Credit)
        debt_match = re.search(rf'بدهکار\s*/?\s*بستانکار\s*:?\s*{num_pat}', text)
        if debt_match:
            result["بدهکار_بستانکار"] = parse_number(debt_match.group(1))
        
        # Extract کسر هزار ریال (Thousand Rial deduction)
        deduction_match = re.search(rf'کسر\s*هزار\s*ریال\s*:?\s*{num_pat}', text)
        if deduction_match:
            result["کسر_هزار_ریال"] = parse_number(deduction_match.group(1))
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # Print extraction summary
        extracted_count = sum(1 for v in result.values() if v is not None)
        print(f"  - Extracted {extracted_count}/{len(result)} transit fields")
        print(f"  - Saved to {output_path}")
            
        return result
    except Exception as e:
        print(f"Error restructuring Transit T4: {e}")
        import traceback
        traceback.print_exc()
        return None
