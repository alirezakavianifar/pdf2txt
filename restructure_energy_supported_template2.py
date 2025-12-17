"""
Restructure energy supported section for Template 2.
This handles the consumption table with multiple columns.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional


def clean_number(text: str) -> Optional[float]:
    """Clean and convert text to number."""
    if not text or text == '':
        return 0
    
    # Remove common separators
    cleaned = text.replace(',', '').replace('٬', '').replace(' ', '').strip()
    
    if not cleaned or cleaned == '-':
        return 0
    
    try:
        if '.' in cleaned:
            return float(cleaned)
        else:
            return int(cleaned)
    except ValueError:
        return None


def parse_energy_table_template2(text: str) -> Dict[str, Any]:
    """
    Parse the energy supported section table for Template 2.
    
    Based on the image, the table structure is:
    1. شرح مصرف (Consumption Description) - Category name
    2. مصرف کل (Total Consumption)
    3. ماده 16 جهش تولید - انرژی (Article 16 Production Leap - Energy)
    4. ماده 16 جهش تولید - خرید از تابلو سبز (Article 16 - Purchase from Green Board)
    5. تولید سبز - مشمول (Green Production - Included)
    6. تولید سبز - غیرمشمول (Green Production - Excluded)
    7. مصرف بورس دوجانبه (Bilateral Exchange Consumption)
    8. مشمول ما به التفاوت اجرا مقررات 4-د - مصرف (Regulation 4d - Consumption)
    9. مشمول ما به التفاوت اجرا مقررات 4-د - نرخ (Regulation 4d - Rate)
    10. مشمول ما به التفاوت اجرا مقررات 4-د - مبلغ (Regulation 4d - Amount)
    11. مشمول ما به التفاوت اجرا مقررات 4-الف - مصرف (Regulation 4a - Consumption)
    12. مشمول ما به التفاوت اجرا مقررات 4-الف - نرخ (Regulation 4a - Rate)
    13. مشمول ما به التفاوت اجرا مقررات 4-الف - مبلغ (Regulation 4a - Amount)
    14. تامین شده توسط مالک شبکه - مصرف (Supplied by Grid Owner - Consumption)
    15. تامین شده توسط مالک شبکه - نرخ (Supplied by Grid Owner - Rate)
    16. تامین شده توسط مالک شبکه - مبلغ (Supplied by Grid Owner - Amount)
    
    Text format: "میان باری 28826 864.78 0 0 0 0 0 0 0 0 0 0 45948644 45,948,644"
    """
    
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
    
    # Initialize result structure
    result = {
        "rows": [],
        "summary": {}
    }
    
    # Known row categories
    categories = ['میان باری', 'میان بار', 'اوج بار', 'کم باری', 'کم بار', 'راکتیو', 'پرمصرف']
    
    for line in lines:
        # Skip header lines
        if 'مصرف' in line and 'بورس' in line and 'ماده' in line:
            continue
        if 'شرح مصرف' in line and 'مصرف کل' in line:
            continue
        
        # Check if this line contains a known category
        matched_category = None
        for cat in categories:
            if cat in line:
                matched_category = cat
                break
        
        if matched_category:
            # Remove category name from line to get just numbers
            line_without_cat = line.replace(matched_category, '', 1).strip()
            
            # Split by whitespace and extract all numbers
            parts = line_without_cat.split()
            numbers = []
            
            for part in parts:
                num = clean_number(part)
                if num is not None:
                    numbers.append(num)
            
            # Create structured row data
            row_data = {
                "شرح مصرف": matched_category,
                "مصرف کل": None,
                "ماده 16 جهش تولید": {
                    "انرژی": None,
                    "خرید از تابلو سبز": None
                },
                "تولید سبز": {
                    "مشمول": None,
                    "غیرمشمول": None
                },
                "مصرف بورس دوجانبه": {
                    "مصرف": None
                },
                "مشمول ما به التفاوت اجرا مقررات 4-د": {
                    "مصرف": None,
                    "نرخ": None,
                    "مبلغ": None
                },
                "مشمول ما به التفاوت اجرا مقررات 4-الف": {
                    "مصرف": None,
                    "نرخ": None,
                    "مبلغ": None
                },
                "تامین شده توسط مالک شبکه": {
                    "مصرف": None,
                    "نرخ": None,
                    "مبلغ": None
                }
            }
            
            # Map numbers to fields based on expected order
            # Expected order: مصرف کل, ماده 16 انرژی, ماده 16 خرید, تولید سبز مشمول, تولید سبز غیرمشمول,
            # مصرف بورس, مقررات 4-د مصرف, مقررات 4-د نرخ, مقررات 4-د مبلغ,
            # مقررات 4-الف مصرف, مقررات 4-الف نرخ, مقررات 4-الف مبلغ,
            # تامین شده مصرف (always 0), تامین شده نرخ, تامین شده مبلغ
            
            if len(numbers) >= 1:
                row_data["مصرف کل"] = numbers[0]
            if len(numbers) >= 2:
                row_data["ماده 16 جهش تولید"]["انرژی"] = numbers[1]
            if len(numbers) >= 3:
                row_data["ماده 16 جهش تولید"]["خرید از تابلو سبز"] = numbers[2]
            if len(numbers) >= 4:
                row_data["تولید سبز"]["مشمول"] = numbers[3]
            if len(numbers) >= 5:
                row_data["تولید سبز"]["غیرمشمول"] = numbers[4]
            if len(numbers) >= 6:
                row_data["مصرف بورس دوجانبه"]["مصرف"] = numbers[5]
            if len(numbers) >= 7:
                row_data["مشمول ما به التفاوت اجرا مقررات 4-د"]["مصرف"] = numbers[6]
            if len(numbers) >= 8:
                row_data["مشمول ما به التفاوت اجرا مقررات 4-د"]["نرخ"] = numbers[7]
            if len(numbers) >= 9:
                row_data["مشمول ما به التفاوت اجرا مقررات 4-د"]["مبلغ"] = numbers[8]
            if len(numbers) >= 10:
                row_data["مشمول ما به التفاوت اجرا مقررات 4-الف"]["مصرف"] = numbers[9]
            if len(numbers) >= 11:
                row_data["مشمول ما به التفاوت اجرا مقررات 4-الف"]["نرخ"] = numbers[10]
            if len(numbers) >= 12:
                row_data["مشمول ما به التفاوت اجرا مقررات 4-الف"]["مبلغ"] = numbers[11]
            
            # تامین شده توسط مالک شبکه: مصرف is always 0 (not in the number list)
            # نرخ and مبلغ are the last two numbers
            row_data["تامین شده توسط مالک شبکه"]["مصرف"] = 0
            if len(numbers) >= 13:
                row_data["تامین شده توسط مالک شبکه"]["نرخ"] = numbers[12]
            if len(numbers) >= 14:
                row_data["تامین شده توسط مالک شبکه"]["مبلغ"] = numbers[13]
            
            result["rows"].append(row_data)
    
    return result


def restructure_energy_supported_template2_json(input_json_path, output_json_path=None):
    """
    Main function to restructure the energy supported section JSON for Template 2.
    
    Args:
        input_json_path: Path to input JSON file
        output_json_path: Path to output JSON file (optional)
    
    Returns:
        Restructured data dictionary
    """
    
    # Read input JSON
    with open(input_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract text content
    text = data.get('text', '')
    
    # Parse the table
    parsed_data = parse_energy_table_template2(text)
    
    # Create output structure
    output_data = {
        "energy_supported_section": parsed_data
    }
    
    # Save to output file if path provided
    if output_json_path:
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    return output_data


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) > 2 else None
        
        result = restructure_energy_supported_template2_json(input_path, output_path)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("Usage: python restructure_energy_supported_template2.py <input_json> [output_json]")
