"""Restructure company info section for Template 5."""
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
    - Company name: شرکت توزیع نیروی برق استان بوشهر
    - National ID (شناسه ملی): ۱۰۸۶۰۱۰۰۱۶۷
    - City/Region: شهر ناحیه (برازجان)
    - Address: آدرس
    - Region: منطقه برق (برازجان)
    - Incident unit: واحد حوادث (۷۷۳۴۲۴۹۶۰۰)
    - Bill parcel code: پارچگویچ صورتحساب
    """
    normalized_text = convert_persian_digits(text)
    
    result = {
        "نام شرکت": None,
        "شناسه ملی": None,
        "شهر ناحیه": None,
        "آدرس": None,
        "منطقه برق": None,
        "واحد حوادث": None,
        "پارچگویچ صورتحساب": None
    }
    
    lines = normalized_text.split('\n')
    full_text = ' '.join(lines)
    
    # Extract company name
    company_match = re.search(r'شرکت[^\n]*', normalized_text)
    if company_match:
        result["نام شرکت"] = company_match.group(0).strip()
    
    # Extract National ID (شناسه ملی)
    national_id_match = re.search(r'شناسه ملی\s*:?\s*(\d{11})', normalized_text)
    if national_id_match:
        result["شناسه ملی"] = national_id_match.group(1)
    else:
        # Fallback: look for 11-digit number
        numbers = re.findall(r'\d{11}', normalized_text)
        if numbers:
            result["شناسه ملی"] = numbers[0]
    
    # Extract شهر ناحیه
    city_match = re.search(r'شهر ناحیه\s*:?\s*([^\n]+)', normalized_text)
    if city_match:
        result["شهر ناحیه"] = city_match.group(1).strip()
    
    # Extract آدرس
    address_match = re.search(r'آدرس\s*:?\s*([^\n]+)', normalized_text)
    if address_match:
        result["آدرس"] = address_match.group(1).strip()
    
    # Extract منطقه برق
    region_match = re.search(r'منطقه برق\s*:?\s*([^\n]+)', normalized_text)
    if region_match:
        result["منطقه برق"] = region_match.group(1).strip()
    
    # Extract واحد حوادث
    incident_match = re.search(r'واحد حوادث\s*:?\s*(\d+)', normalized_text)
    if incident_match:
        result["واحد حوادث"] = incident_match.group(1)
    
    # Extract پارچگویچ صورتحساب
    parcel_match = re.search(r'پارچگویچ صورتحساب\s*:?\s*([^\n]+)', normalized_text)
    if parcel_match:
        result["پارچگویچ صورتحساب"] = parcel_match.group(1).strip()
    
    return result


def restructure_company_info_template5_json(json_path: Path, output_path: Path):
    """Restructure extracted JSON to include company info data for Template 5."""
    print(f"Restructuring Company Info (Template 5) from {json_path}...")
    
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
        print(f"Error restructuring Company Info T5: {e}")
        import traceback
        traceback.print_exc()
        return None

