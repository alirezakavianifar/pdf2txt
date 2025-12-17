"""
Restructure power section for Template 2.
This handles the "قدرت خریداری شده از نرخ" (Power Purchased from Rate) table.

The table has columns:
- شرح (Description): میان باری, کم باری, اوج بار
- دوجانبه (Bilateral)
- بورس (Exchange)
- نابله سبز (Green Board)
- تجدیدپذیر (Renewable)
- متوسط بازار (Market Average)
- حداکثرنیاز سبز (Max Green Need)
- حداکثر عمده فروشی (Max Wholesale)
- ساعت TOU (TOU Hours)
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


def parse_power_table_template2(text: str) -> Dict[str, Any]:
    """
    Parse the power section table for Template 2.
    
    Expected structure based on the image:
    - Header row with column names
    - Data rows: میان باری, کم باری, اوج بار
    - Each row has multiple numeric values
    """
    
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
    
    # Initialize result structure
    result = {
        "rows": [],
        "table_type": "قدرت خریداری شده از نرخ"
    }
    
    # Known row categories
    categories = {
        'میان باری': 'mid_load',
        'میان بار': 'mid_load',
        'کم باری': 'low_load', 
        'کم بار': 'low_load',
        'اوج بار': 'peak_load',
        'اوج باری': 'peak_load'
    }
    
    for line in lines:
        # Skip header lines
        if 'قدرت' in line and 'خریداری' in line:
            continue
        if 'شرح' in line or 'دوجانبه' in line or 'بورس' in line:
            continue
        
        # Check if this line contains a known category
        matched_category = None
        matched_key = None
        for cat, key in categories.items():
            if cat in line:
                matched_category = cat
                matched_key = key
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
            
            # Create row data with expected column mapping
            # Based on the image, columns are (from right to left):
            # شرح, دوجانبه, بورس, تابلو سبز, تجدیدپذیر, متوسط بازار, حداکثر تابلو سبز, حداکثر عمده فروشی, ساعت TOU
            # Text format: "میان باری 0 0 0 39039 2617.65 37000 3125.74 13"
            # So numbers are: [دوجانبه, بورس, تابلو سبز, تجدیدپذیر, متوسط بازار, حداکثر تابلو سبز, حداکثر عمده فروشی, ساعت TOU]
            
            row_data = {
                "شرح": matched_category,
                "category_key": matched_key,
                "قدرت خریداری شده از": {
                    "دوجانبه": None,
                    "بورس": None,
                    "تابلو سبز": None
                },
                "نرخ": {
                    "تجدیدپذیر": None,
                    "متوسط بازار": None,
                    "حداکثر تابلو سبز": None,
                    "حداکثر عمده فروشی": None
                },
                "ساعت TOU": None
            }
            
            # Map to specific fields if we have enough values
            if len(numbers) >= 8:
                row_data["قدرت خریداری شده از"]["دوجانبه"] = numbers[0]
                row_data["قدرت خریداری شده از"]["بورس"] = numbers[1]
                row_data["قدرت خریداری شده از"]["تابلو سبز"] = numbers[2]
                row_data["نرخ"]["تجدیدپذیر"] = numbers[3]
                row_data["نرخ"]["متوسط بازار"] = numbers[4]
                row_data["نرخ"]["حداکثر تابلو سبز"] = numbers[5]
                row_data["نرخ"]["حداکثر عمده فروشی"] = numbers[6]
                row_data["ساعت TOU"] = numbers[7]
            elif len(numbers) >= 3:
                # Partial mapping for incomplete data
                if len(numbers) >= 7:
                    row_data["نرخ"]["حداکثر عمده فروشی"] = numbers[6]
                if len(numbers) >= 6:
                    row_data["نرخ"]["حداکثر تابلو سبز"] = numbers[5]
                if len(numbers) >= 5:
                    row_data["نرخ"]["متوسط بازار"] = numbers[4]
                if len(numbers) >= 4:
                    row_data["نرخ"]["تجدیدپذیر"] = numbers[3]
                if len(numbers) >= 3:
                    row_data["قدرت خریداری شده از"]["تابلو سبز"] = numbers[2]
                if len(numbers) >= 2:
                    row_data["قدرت خریداری شده از"]["بورس"] = numbers[1]
                if len(numbers) >= 1:
                    row_data["قدرت خریداری شده از"]["دوجانبه"] = numbers[0]
            
            if numbers:
                result["rows"].append(row_data)
    
    return result


def restructure_power_section_template2_json(input_json_path, output_json_path=None):
    """
    Main function to restructure the power section JSON for Template 2.
    
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
    parsed_data = parse_power_table_template2(text)
    
    # Create output structure
    output_data = {
        "power_section": parsed_data
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
        
        result = restructure_power_section_template2_json(input_path, output_path)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("Usage: python restructure_power_section_template2.py <input_json> [output_json]")
