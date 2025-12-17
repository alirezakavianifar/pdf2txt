"""Restructure company info section for Template 7."""
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
    """Extract company and customer information from text."""
    normalized_text = convert_persian_digits(text)
    
    result = {
        "نام شرکت": None,
        "شهر امور": None,
        "آدرس": None,
        "منطقه برق": None,
        "واحد حوادث": None,
        "نام مشترک": None,
        "نشانی محل مصرف": None,
        "نشانی محل مکاتباتی": None,
        "کد پستی": None,
        "کد اقتصادی": None,
        "شناسه ملی": None,
        "شناسه پرداخت": None,
        "شناسایی": None,
        "پرونده": None,
        "شماره اشتراک": None,
        "تاریخ نصب": None,
        "عنوان و کد تعرفه": None,
        "کد فعالیت": None,
        "نوع فعالیت": None,
        "گزینه انتخابی": None,
        "رمز رایانه": None,
        "ولتاژ تغذیه": None
    }
    
    # Extract company name
    company_match = re.search(r'شرکت توزیع[^\n]*', normalized_text)
    if company_match:
        result["نام شرکت"] = company_match.group(0).strip()
    
    # Extract City/Region (شهر امور)
    city_match = re.search(r'شهر امور\s*:?\s*([^\n]+)', normalized_text)
    if city_match:
        result["شهر امور"] = city_match.group(1).strip()
    
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
    
    # Extract Customer name (مشترک گرامی)
    customer_match = re.search(r'مشترک گرامی\s*:?\s*([^\n]+)', normalized_text)
    if customer_match:
        result["نام مشترک"] = customer_match.group(1).strip()
    
    # Extract Consumption address (نشانی محل مصرف)
    consumption_addr_match = re.search(r'نشانی محل مصرف\s*:?\s*([^\n]+)', normalized_text)
    if consumption_addr_match:
        result["نشانی محل مصرف"] = consumption_addr_match.group(1).strip()
    
    # Extract Correspondence address (نشانی محل مکاتباتی)
    correspondence_addr_match = re.search(r'نشانی محل مکاتباتی\s*:?\s*([^\n]+)', normalized_text)
    if correspondence_addr_match:
        result["نشانی محل مکاتباتی"] = correspondence_addr_match.group(1).strip()
    
    # Extract Postal code (کد پستی)
    postal_match = re.search(r'کد پستی\s*:?\s*(\d+)', normalized_text)
    if postal_match:
        result["کد پستی"] = postal_match.group(1)
    
    # Extract Economic code (کد اقتصادی)
    economic_match = re.search(r'کد اقتصادی\s*:?\s*(\d+)', normalized_text)
    if economic_match:
        result["کد اقتصادی"] = economic_match.group(1)
    
    # Extract National ID (شناسه ملی)
    national_id_match = re.search(r'شناسه ملی\s*:?\s*(\d+)', normalized_text)
    if national_id_match:
        result["شناسه ملی"] = national_id_match.group(1)
    
    # Extract Payment ID (شناسه پرداخت)
    payment_id_match = re.search(r'شناسه پرداخت\s*:?\s*(\d+)', normalized_text)
    if payment_id_match:
        result["شناسه پرداخت"] = payment_id_match.group(1)
    
    # Extract Identification (شناسایی)
    identification_match = re.search(r'شناسایی\s*:?\s*([^\n]+)', normalized_text)
    if identification_match:
        result["شناسایی"] = identification_match.group(1).strip()
    
    # Extract File number (پرونده)
    file_match = re.search(r'پرونده\s*:?\s*(\d+)', normalized_text)
    if file_match:
        result["پرونده"] = file_match.group(1)
    
    # Extract Subscription number (شماره اشتراک)
    subscription_match = re.search(r'شماره اشتراک\s*:?\s*(\d+)', normalized_text)
    if subscription_match:
        result["شماره اشتراک"] = subscription_match.group(1)
    
    # Extract Installation date (تاریخ نصب)
    install_date_match = re.search(r'تاریخ نصب\s*:?\s*(\d{4}/\d{2}/\d{2})', normalized_text)
    if install_date_match:
        result["تاریخ نصب"] = install_date_match.group(1)
    
    # Extract Tariff code (عنوان و کد تعرفه)
    tariff_match = re.search(r'عنوان و کد تعرفه\s*:?\s*([^\n]+)', normalized_text)
    if tariff_match:
        result["عنوان و کد تعرفه"] = tariff_match.group(1).strip()
    
    # Extract Activity code (کد فعالیت)
    activity_match = re.search(r'کد فعالیت\s*:?\s*([^\n]+)', normalized_text)
    if activity_match:
        result["کد فعالیت"] = activity_match.group(1).strip()
    
    # Extract Activity type (نوع فعالیت)
    activity_type_match = re.search(r'نوع فعالیت\s*:?\s*([^\n]+)', normalized_text)
    if activity_type_match:
        result["نوع فعالیت"] = activity_type_match.group(1).strip()
    
    # Extract Selected option (گزینه انتخابی)
    option_match = re.search(r'گزینه انتخابی\s*:?\s*(\d+)', normalized_text)
    if option_match:
        result["گزینه انتخابی"] = option_match.group(1)
    
    # Extract Computer code (رمز رایانه)
    computer_match = re.search(r'رمز رایانه\s*:?\s*(\d+)', normalized_text)
    if computer_match:
        result["رمز رایانه"] = computer_match.group(1)
    
    # Extract Supply voltage (ولتاژ تغذیه)
    voltage_match = re.search(r'ولتاژ تغذیه\s*:?\s*([^\n]+)', normalized_text)
    if voltage_match:
        result["ولتاژ تغذیه"] = voltage_match.group(1).strip()
    
    return result


def restructure_company_info_template7_json(json_path: Path, output_path: Path):
    """Restructure extracted JSON to include company info data for Template 7."""
    print(f"Restructuring Company Info (Template 7) from {json_path}...")
    
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
        print(f"Error restructuring Company Info T7: {e}")
        import traceback
        traceback.print_exc()
        return None

