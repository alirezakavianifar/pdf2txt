"""Restructure company info section for Template 6."""
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


def extract_company_info(text):
    """Extract company information from text.
    
    Expected fields:
    - Company name: توزیع برق گلستان
    - National ID (شناسه ملی): 411,140,441,069
    - Economic code (کد اقتصادی)
    - Subscription code (شتراک): 605508116
    - Address (آدرس)
    - Region (منطقه برق)
    - Unit code (واحد حوادث)
    - Meter body number (شمارده بدنه کنتور): 12059755
    - Meter coefficient (ضریب کنتور): 4,000
    - Voltage code (کد ولتاژ)
    - Activity code (کد فعالیت)
    - Tariff code (کد تعرفه): 4420
    - Option code (کد گزینه): 1
    - Computer code (رمز رایانه): 60550811614022
    """
    normalized_text = convert_persian_digits(text)
    
    result = {
        "نام شرکت": None,
        "شناسه ملی": None,
        "کد اقتصادی": None,
        "شتراک": None,
        "آدرس": None,
        "منطقه برق": None,
        "واحد حوادث": None,
        "شمارده بدنه کنتور": None,
        "ضریب کنتور": None,
        "کد ولتاژ": None,
        "کد فعالیت": None,
        "کد تعرفه": None,
        "کد گزینه": None,
        "رمز رایانه": None
    }
    
    lines = normalized_text.split('\n')
    full_text = ' '.join(lines)
    
    # Extract company name
    company_match = re.search(r'شرکت[^\n]*|توزیع[^\n]*', normalized_text)
    if company_match:
        result["نام شرکت"] = company_match.group(0).strip()
    
    # Extract National ID (شناسه ملی) - can be 11 or 12 digits
    national_id_match = re.search(r'شناسه ملی\s*:?\s*(\d{11,12})', normalized_text)
    if national_id_match:
        result["شناسه ملی"] = national_id_match.group(1)
    else:
        # Fallback: look for 11-12 digit number
        numbers = re.findall(r'\d{11,12}', normalized_text)
        if numbers:
            result["شناسه ملی"] = numbers[0]
    
    # Extract Economic code (کد اقتصادی)
    economic_match = re.search(r'کد اقتصادی\s*:?\s*(\d+)', normalized_text)
    if economic_match:
        result["کد اقتصادی"] = economic_match.group(1)
    
    # Extract Subscription code (شتراک)
    subscription_match = re.search(r'شتراک\s*:?\s*(\d+)', normalized_text)
    if subscription_match:
        result["شتراک"] = subscription_match.group(1)
    
    # Extract Address (آدرس)
    address_match = re.search(r'آدرس\s*:?\s*([^\n]+)', normalized_text)
    if address_match:
        result["آدرس"] = address_match.group(1).strip()
    
    # Extract Region (منطقه برق)
    region_match = re.search(r'منطقه برق\s*:?\s*([^\n]+)', normalized_text)
    if region_match:
        result["منطقه برق"] = region_match.group(1).strip()
    
    # Extract Unit code (واحد حوادث)
    incident_match = re.search(r'واحد حوادث\s*:?\s*(\d+)', normalized_text)
    if incident_match:
        result["واحد حوادث"] = incident_match.group(1)
    
    # Extract Meter body number (شمارده بدنه کنتور)
    meter_match = re.search(r'شمارده بدنه کنتور\s*:?\s*(\d+)', normalized_text)
    if meter_match:
        result["شمارده بدنه کنتور"] = meter_match.group(1)
    
    # Extract Meter coefficient (ضریب کنتور)
    coefficient_match = re.search(r'ضریب کنتور\s*:?\s*([\d,]+)', normalized_text)
    if coefficient_match:
        result["ضریب کنتور"] = coefficient_match.group(1).replace(',', '')
    
    # Extract Voltage code (کد ولتاژ)
    voltage_match = re.search(r'کد ولتاژ\s*:?\s*(\d+)', normalized_text)
    if voltage_match:
        result["کد ولتاژ"] = voltage_match.group(1)
    
    # Extract Activity code (کد فعالیت)
    activity_match = re.search(r'کد فعالیت\s*:?\s*(\d+)', normalized_text)
    if activity_match:
        result["کد فعالیت"] = activity_match.group(1)
    
    # Extract Tariff code (کد تعرفه)
    tariff_match = re.search(r'کد تعرفه\s*:?\s*(\d+)', normalized_text)
    if tariff_match:
        result["کد تعرفه"] = tariff_match.group(1)
    
    # Extract Option code (کد گزینه)
    option_match = re.search(r'کد گزینه\s*:?\s*(\d+)', normalized_text)
    if option_match:
        result["کد گزینه"] = option_match.group(1)
    
    # Extract Computer code (رمز رایانه)
    computer_match = re.search(r'رمز رایانه\s*:?\s*(\d+)', normalized_text)
    if computer_match:
        result["رمز رایانه"] = computer_match.group(1)
    
    return result


def restructure_company_info_template6_json(json_path: Path, output_path: Path):
    """Restructure extracted JSON to include company info data for Template 6."""
    print(f"Restructuring Company Info (Template 6) from {json_path}...")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        text = data.get('text', '')
        
        # Extract company info
        company_info = extract_company_info(text)
        
        # Build restructured data
        result = {
            "اطلاعات شرکت": company_info
        }
        
        # Save restructured JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"  - Saved to {output_path}")
        extracted_count = sum(1 for v in company_info.values() if v is not None)
        print(f"  - Extracted {extracted_count}/{len(company_info)} company info fields")
        
        return result
        
    except Exception as e:
        print(f"Error restructuring Company Info T6: {e}")
        import traceback
        traceback.print_exc()
        return None

